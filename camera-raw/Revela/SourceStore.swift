import CoreGraphics
import Foundation

/// Guarda o arquivo original (DNG, ou HEIC com profundidade no Retrato) das últimas fotos,
/// para dar para revelar de novo com outro filme ou mudar o foco do retrato depois.
enum SourceStore {
    struct Entry: Codable {
        var assetID: String
        var file: String
        var isRaw: Bool
        var hasDepth: Bool
        var zoom: Double
        var aspect: String
        var mirror: Bool
        var aperture: Float
        var focusX: Double?
        var focusY: Double?
        var date: Date
        var mode: String
        /// ETTR: quanto a revelação descontou (a foto foi exposta mais clara). Opcional: originais antigos não têm.
        var exposureOffset: Float?
        /// Versão neutra já revelada (não aplica os tons locais de novo). Opcional: originais antigos não têm.
        var toned: Bool?

        var focusPoint: CGPoint? { focusX.flatMap { x in focusY.map { CGPoint(x: x, y: $0) } } }
    }

    /// Quantas fotos ficam guardadas (as mais antigas saem).
    static let limit = 12
    static let maxBytes = 700 * 1_048_576

    private static let queue = DispatchQueue(label: "revela.sources")
    private static let directory: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dir = docs.appendingPathComponent("originais", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir
    }()
    private static var indexURL: URL { directory.appendingPathComponent("indice.json") }

    private static func readIndex() -> [Entry] {
        guard let data = try? Data(contentsOf: indexURL) else { return [] }
        return (try? JSONDecoder().decode([Entry].self, from: data)) ?? []
    }

    private static func writeIndex(_ entries: [Entry]) {
        if let data = try? JSONEncoder().encode(entries) { try? data.write(to: indexURL, options: .atomic) }
    }

    static func keep(_ frame: CapturedFrame, options: DevelopOptions, assetID: String, mode: String,
                     aperture: Float, focusPoint: CGPoint?) {
        queue.async {
            let file = UUID().uuidString + (frame.isRaw ? ".dng" : ".heic")
            do {
                try frame.data.write(to: directory.appendingPathComponent(file))
            } catch {
                dlog("Original não guardado: \(error.localizedDescription)")
                return
            }
            var entries = readIndex()
            entries.insert(Entry(assetID: assetID, file: file, isRaw: frame.isRaw, hasDepth: frame.hasDepth,
                                 zoom: Double(options.zoom), aspect: options.originalAspect ? "" : options.aspect.rawValue,
                                 mirror: options.mirror,
                                 aperture: aperture, focusX: focusPoint.map { Double($0.x) }, focusY: focusPoint.map { Double($0.y) },
                                 date: Date(), mode: mode,
                                 exposureOffset: options.exposureOffset == 0 ? nil : options.exposureOffset,
                                 toned: frame.toned ? true : nil), at: 0)
            // No máximo `limit` fotos e uns 700 MB (um ProRAW de 48 MP passa de 70 MB)
            func size(_ e: Entry) -> Int {
                (try? directory.appendingPathComponent(e.file).resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
            }
            var total = entries.reduce(0) { $0 + size($1) }
            while entries.count > 1, entries.count > limit || total > maxBytes {
                let old = entries.removeLast()
                total -= size(old)
                try? FileManager.default.removeItem(at: directory.appendingPathComponent(old.file))
            }
            writeIndex(entries)
        }
    }

    /// Original de uma foto da galeria (pelo identificador), se ainda estiver guardado.
    static func find(assetID: String) -> (Entry, Data)? {
        queue.sync {
            guard let entry = readIndex().first(where: { $0.assetID == assetID }),
                  let data = try? Data(contentsOf: directory.appendingPathComponent(entry.file)) else { return nil }
            return (entry, data)
        }
    }

    /// Só o índice (sem ler o arquivo, que pode ter 100 MB): para conferir se a foto nova já chegou.
    static func latestEntry() -> Entry? {
        queue.sync { readIndex().first }
    }

    /// Arquivo do original mais novo, sem ler (pode ter 100 MB): a miniatura ao abrir o app sai dele.
    static func latestFileURL() -> URL? {
        queue.sync { readIndex().first.map { directory.appendingPathComponent($0.file) } }
    }

    /// As últimas fotos guardadas (só o índice), da mais nova para a mais velha.
    static func recentEntries(limit: Int) -> [Entry] {
        queue.sync { Array(readIndex().prefix(limit)) }
    }

    static func latest() -> (Entry, Data)? {
        queue.sync {
            guard let entry = readIndex().first,
                  let data = try? Data(contentsOf: directory.appendingPathComponent(entry.file)) else { return nil }
            return (entry, data)
        }
    }

    /// Espaço ocupado, para mostrar nos Ajustes.
    static func totalBytes() -> Int {
        queue.sync {
            let files = (try? FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: [.fileSizeKey])) ?? []
            return files.reduce(0) { $0 + ((try? $1.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0) }
        }
    }

    static func clear() {
        queue.async {
            let files = (try? FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)) ?? []
            files.forEach { try? FileManager.default.removeItem(at: $0) }
        }
    }
}
