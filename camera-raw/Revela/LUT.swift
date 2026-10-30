import CoreImage
import Foundation

/// LUT 3D (.cube) pronta para o CIColorCube.
final class LUTCube {
    let dimension: Int
    let data: Data

    init(dimension: Int, data: Data) {
        self.dimension = dimension
        self.data = data
    }

    /// Lê o formato .cube (Resolve, Adobe, a maioria dos LUTs da internet).
    static func parse(_ text: String) -> LUTCube? {
        var size = 0
        var minDomain = SIMD3<Float>(0, 0, 0), maxDomain = SIMD3<Float>(1, 1, 1)
        var values: [Float] = []
        for raw in text.split(whereSeparator: \.isNewline) {
            let line = raw.trimmingCharacters(in: .whitespaces)
            if line.isEmpty || line.hasPrefix("#") { continue }
            let parts = line.split(whereSeparator: { $0 == " " || $0 == "\t" })
            guard let key = parts.first else { continue }
            switch key.uppercased() {
            case "LUT_3D_SIZE":
                size = parts.count > 1 ? Int(parts[1]) ?? 0 : 0
                values.reserveCapacity(size * size * size * 4)
            case "LUT_1D_SIZE":
                return nil
            case "DOMAIN_MIN":
                let v = parts.dropFirst().compactMap { Float($0) }
                if v.count == 3 { minDomain = SIMD3(v[0], v[1], v[2]) }
            case "DOMAIN_MAX":
                let v = parts.dropFirst().compactMap { Float($0) }
                if v.count == 3 { maxDomain = SIMD3(v[0], v[1], v[2]) }
            case "TITLE", "LUT_3D_INPUT_RANGE", "LUT_1D_INPUT_RANGE":
                continue
            default:
                let v = parts.compactMap { Float($0) }
                guard v.count == 3 else { continue }
                // Fora do domínio 0…1: traz para 0…1
                let range = maxDomain - minDomain
                values.append((v[0] - minDomain.x) / max(range.x, 1e-6))
                values.append((v[1] - minDomain.y) / max(range.y, 1e-6))
                values.append((v[2] - minDomain.z) / max(range.z, 1e-6))
                values.append(1)
            }
        }
        guard size >= 2, size <= 128, values.count == size * size * size * 4 else { return nil }
        return LUTCube(dimension: size, data: values.withUnsafeBufferPointer { Data(buffer: $0) })
    }
}

/// Guarda as LUTs importadas no aparelho e mantém as já lidas na memória.
enum LUTStore {
    private static let lock = NSLock()
    private static var cache: [String: LUTCube] = [:]
    private static let directory: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dir = docs.appendingPathComponent("luts", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir
    }()

    /// Copia o .cube para o app. Devolve o nome do arquivo guardado e um nome para o filme.
    static func importFile(at url: URL) -> (file: String, name: String)? {
        let scoped = url.startAccessingSecurityScopedResource()
        defer { if scoped { url.stopAccessingSecurityScopedResource() } }
        guard let text = (try? String(contentsOf: url, encoding: .utf8)) ?? (try? String(contentsOf: url, encoding: .isoLatin1)),
              let cube = LUTCube.parse(text) else { return nil }
        let file = UUID().uuidString + ".cube"
        do {
            try text.write(to: directory.appendingPathComponent(file), atomically: true, encoding: .utf8)
        } catch {
            return nil
        }
        lock.lock()
        cache[file] = cube
        lock.unlock()
        let name = url.deletingPathExtension().lastPathComponent
        dlog("LUT importada: \(name) (\(cube.dimension)³)")
        return (file, name)
    }

    static func cube(_ file: String) -> LUTCube? {
        lock.lock()
        defer { lock.unlock() }
        if let cached = cache[file] { return cached }
        guard let text = try? String(contentsOf: directory.appendingPathComponent(file), encoding: .utf8),
              let cube = LUTCube.parse(text) else { return nil }
        cache[file] = cube
        return cube
    }

    static func delete(_ file: String) {
        lock.lock()
        cache[file] = nil
        lock.unlock()
        try? FileManager.default.removeItem(at: directory.appendingPathComponent(file))
    }
}
