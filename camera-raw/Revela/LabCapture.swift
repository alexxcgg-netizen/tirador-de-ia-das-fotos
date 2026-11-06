import Foundation

/// "Guardar para o laboratório": cada disparo vira uma pasta em Arquivos → No meu iPhone → Revela → laboratorio,
/// com todas as fotos cruas da sequência (DNG) e um info.json. Você manda a pasta para o Google Drive e o Claude
/// testa a revelação em cima das suas fotos de verdade, quantas vezes precisar, sem você fotografar de novo.
enum LabCapture {
    private static let queue = DispatchQueue(label: "revela.lab", qos: .utility)

    static var directory: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("laboratorio", isDirectory: true)
    }

    static func save(_ frames: [CapturedFrame], mode: String, options: DevelopOptions) {
        guard !frames.isEmpty else { return }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd_HH-mm-ss"
        let stamp = formatter.string(from: Date())
        let safeMode = mode.folding(options: .diacriticInsensitive, locale: nil).replacingOccurrences(of: " ", with: "-")
        let folder = directory.appendingPathComponent("\(stamp)_\(safeMode)", isDirectory: true)
        let info: [String: Any] = [
            "modo": mode,
            "fotos": frames.count,
            "exposicoes": frames.map { Double($0.exposureBias) },
            "raw": frames.map(\.isRaw),
            "profundidade": frames.map(\.hasDepth),
            "zoom": Double(options.zoom),
            "proporcao": options.aspect.rawValue,
            "filme": options.lookName,
            "versao": Diagnostics.appVersion,
            "data": ISO8601DateFormatter().string(from: Date()),
        ]
        queue.async {
            do {
                try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
                for (i, frame) in frames.enumerated() {
                    let ext = frame.isRaw ? "dng" : "heic"
                    let bias = frame.exposureBias == 0 ? "" : String(format: "_%+.0fEV", frame.exposureBias)
                    try frame.data.write(to: folder.appendingPathComponent(String(format: "quadro_%02d%@.%@", i + 1, bias, ext)))
                }
                let json = try JSONSerialization.data(withJSONObject: info, options: [.prettyPrinted, .sortedKeys])
                try json.write(to: folder.appendingPathComponent("info.json"))
                dlog("Laboratório: \(frames.count) foto(s) de \(mode) guardadas em laboratorio/\(folder.lastPathComponent)")
            } catch {
                dlog("❌ Laboratório: não guardou (\(error.localizedDescription))")
            }
        }
    }

    /// Espaço ocupado (para os Ajustes).
    static func totalBytes() -> Int {
        guard let items = FileManager.default.enumerator(at: directory, includingPropertiesForKeys: [.fileSizeKey]) else { return 0 }
        var total = 0
        for case let url as URL in items {
            total += (try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
        }
        return total
    }

    static func clear() {
        queue.async { try? FileManager.default.removeItem(at: directory) }
    }
}
