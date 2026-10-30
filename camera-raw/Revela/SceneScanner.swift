import ARKit
import CoreImage
import ImageIO
import ModelIO
import RealityKit
import UniformTypeIdentifiers

/// Scanner 3D, modo CENA: ARKit (posição de cada foto pelo LiDAR + giroscópio) e profundidade do LiDAR.
/// Guarda um pacote pronto para Gaussian splatting no PC (formato nerfstudio, abre no Brush),
/// uma nuvem de pontos colorida (PLY) e a malha do LiDAR (OBJ e USDZ para ver em realidade aumentada).
final class SceneScanner: NSObject, ObservableObject, ARSessionDelegate {
    static var isSupported: Bool { ARWorldTrackingConfiguration.supportsFrameSemantics(.sceneDepth) }

    let arView = ARView(frame: .zero, cameraMode: .ar, automaticallyConfigureSession: false)

    @Published var recording = false
    @Published var keyframes = 0
    @Published var pointCount = 0
    @Published var status = "Aponte para a cena"
    @Published var busy: String?
    @Published var result: ScanResult?

    struct ScanResult {
        let folder: URL
        let zip: URL?
        let ply: URL
        let usdz: URL?
        let frames: Int
        let points: Int
    }

    private let writeQueue = DispatchQueue(label: "revela.scan.write", qos: .userInitiated)
    private let context = CIContext()
    private var folder: URL?
    private var frameEntries: [[String: Any]] = []
    private var lastTransform: simd_float4x4?
    private var lastTime: TimeInterval = 0
    private var pending = 0
    private var usingFourK = false

    // Nuvem de pontos: 1 ponto por voxel de 1 cm (sem duplicar o que já foi visto)
    private var voxels = Set<Int64>()
    private var cloudPoints: [SIMD3<Float>] = []
    private var cloudColors: [SIMD3<UInt8>] = []
    private let maxPoints = 4_000_000

    // MARK: - Sessão

    func startPreview() {
        arView.session.delegate = self
        arView.debugOptions = [.showSceneUnderstanding]
        arView.environment.sceneUnderstanding.options = []
        run(fourK: true)
    }

    private func run(fourK: Bool) {
        let config = ARWorldTrackingConfiguration()
        if ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) { config.sceneReconstruction = .mesh }
        config.frameSemantics = [.sceneDepth]
        // Fotos em 4K deixam o splat bem mais nítido
        if fourK, let format = ARWorldTrackingConfiguration.recommendedVideoFormatFor4KResolution {
            config.videoFormat = format
            usingFourK = true
        } else {
            usingFourK = false
        }
        arView.session.run(config, options: [.resetTracking, .removeExistingAnchors])
        dlog("Scanner: ARKit \(usingFourK ? "4K" : "padrão") · \(config.videoFormat.imageResolution.width)×\(config.videoFormat.imageResolution.height)")
    }

    func stop() {
        arView.session.pause()
    }

    func session(_ session: ARSession, didFailWithError error: Error) {
        dlog("Scanner: ARKit falhou (\(error.localizedDescription))")
        if usingFourK {
            run(fourK: false)
        } else {
            status = "O ARKit parou: \(error.localizedDescription)"
        }
    }

    // MARK: - Gravação

    func startRecording() {
        let stamp = ISO8601DateFormatter().string(from: Date()).replacingOccurrences(of: ":", with: "-")
        let base = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Scans/cena-\(stamp)", isDirectory: true)
        for sub in ["images", "depth", "confidence"] {
            try? FileManager.default.createDirectory(at: base.appendingPathComponent(sub), withIntermediateDirectories: true)
        }
        folder = base
        frameEntries = []
        voxels = []
        cloudPoints = []
        cloudColors = []
        lastTransform = nil
        keyframes = 0
        pointCount = 0
        result = nil
        recording = true
        dlog("Scanner: gravando em \(base.lastPathComponent)")
    }

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        switch frame.camera.trackingState {
        case .normal:
            if !recording { status = "Pronto. Toque em gravar e ande devagar em volta" }
        case .limited(let reason):
            switch reason {
            case .excessiveMotion: status = "Mais devagar"
            case .insufficientFeatures: status = "Pouca textura: aponte para algo com detalhes"
            case .initializing, .relocalizing: status = "Reconhecendo o ambiente…"
            @unknown default: status = "Rastreamento limitado"
            }
            return
        case .notAvailable:
            status = "Rastreamento indisponível"
            return
        }
        guard recording, let folder, pending < 3, let depth = frame.sceneDepth else { return }

        // Foto nova só quando andou 5 cm ou girou 5°, e no máximo 4 por segundo
        let t = frame.camera.transform
        if let last = lastTransform {
            let moved = simd_distance(SIMD3(t.columns.3.x, t.columns.3.y, t.columns.3.z),
                                      SIMD3(last.columns.3.x, last.columns.3.y, last.columns.3.z))
            let forwardNow = -SIMD3(t.columns.2.x, t.columns.2.y, t.columns.2.z)
            let forwardThen = -SIMD3(last.columns.2.x, last.columns.2.y, last.columns.2.z)
            let turned = acos(min(max(simd_dot(forwardNow, forwardThen), -1), 1)) * 180 / .pi
            guard frame.timestamp - lastTime > 0.25, moved > 0.05 || turned > 5 else { return }
        }
        lastTransform = t
        lastTime = frame.timestamp
        let index = frameEntries.count + 1
        let name = String(format: "frame_%05d", index)

        // Copia o que precisa agora (o ARKit reaproveita os buffers)
        let image = CIImage(cvPixelBuffer: frame.capturedImage)
        let depthValues = Self.copyFloats(depth.depthMap)
        let confidenceValues = depth.confidenceMap.map(Self.copyBytes)
        let depthSize = (CVPixelBufferGetWidth(depth.depthMap), CVPixelBufferGetHeight(depth.depthMap))
        let k = frame.camera.intrinsics
        let resolution = frame.camera.imageResolution

        frameEntries.append([
            "file_path": "images/\(name).jpg",
            "depth_file_path": "depth/\(name).png",
            "fl_x": k[0][0], "fl_y": k[1][1], "cx": k[2][0], "cy": k[2][1],
            "w": Int(resolution.width), "h": Int(resolution.height),
            // Mesma convenção do nerfstudio (OpenGL): x direita, y cima, olhando para -z
            "transform_matrix": (0..<4).map { row in (0..<4).map { col in t[col][row] } },
        ])
        pending += 1

        writeQueue.async {
            try? self.context.writeJPEGRepresentation(
                of: image, to: folder.appendingPathComponent("images/\(name).jpg"),
                colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!,
                options: [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.92])
            Self.writeDepthPNG(depthValues, width: depthSize.0, height: depthSize.1,
                               to: folder.appendingPathComponent("depth/\(name).png"))
            if let confidenceValues {
                Self.writeGrayPNG(confidenceValues.map { $0 * 127 }, width: depthSize.0, height: depthSize.1,
                                  to: folder.appendingPathComponent("confidence/\(name).png"))
            }
            self.addPoints(image: image, depth: depthValues, confidence: confidenceValues, size: depthSize,
                           intrinsics: k, resolution: resolution, transform: t)
            let points = self.cloudPoints.count
            DispatchQueue.main.async {
                self.pending -= 1
                self.keyframes = index
                self.pointCount = points
            }
        }
    }

    /// Cada pixel de profundidade confiável vira um ponto colorido no espaço.
    private func addPoints(image: CIImage, depth: [Float], confidence: [UInt8]?, size: (Int, Int),
                           intrinsics k: simd_float3x3, resolution: CGSize, transform t: simd_float4x4) {
        let (w, h) = size
        guard cloudPoints.count < maxPoints, depth.count == w * h else { return }
        // Cor: a foto reduzida para o tamanho do mapa de profundidade
        let small = image.transformed(by: CGAffineTransform(scaleX: CGFloat(w) / image.extent.width,
                                                            y: CGFloat(h) / image.extent.height))
        var rgba = [UInt8](repeating: 0, count: w * h * 4)
        context.render(small, toBitmap: &rgba, rowBytes: w * 4, bounds: CGRect(x: 0, y: 0, width: w, height: h),
                       format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB))
        let s = Float(w) / Float(resolution.width)
        let fx = k[0][0] * s, fy = k[1][1] * s, cx = k[2][0] * s, cy = k[2][1] * s
        for v in stride(from: 0, to: h, by: 2) {
            for u in stride(from: 0, to: w, by: 2) {
                let i = v * w + u
                if let confidence, confidence[i] < 2 { continue }
                let d = depth[i]
                guard d > 0.1, d < 5 else { continue }
                let x = (Float(u) + 0.5 - cx) * d / fx
                let y = (Float(v) + 0.5 - cy) * d / fy
                let world = t * SIMD4<Float>(x, -y, -d, 1)
                let key = Self.voxelKey(world)
                guard voxels.insert(key).inserted else { continue }
                cloudPoints.append(SIMD3(world.x, world.y, world.z))
                // O bitmap renderizado vem de baixo para cima
                let row = h - 1 - v
                let p = (row * w + u) * 4
                cloudColors.append(SIMD3(rgba[p], rgba[p + 1], rgba[p + 2]))
            }
        }
    }

    private static func voxelKey(_ p: SIMD4<Float>) -> Int64 {
        let ix = Int64((p.x * 100).rounded(.down)) & 0x1FFFFF
        let iy = Int64((p.y * 100).rounded(.down)) & 0x1FFFFF
        let iz = Int64((p.z * 100).rounded(.down)) & 0x1FFFFF
        return ix | (iy << 21) | (iz << 42)
    }

    // MARK: - Fim

    func finish() {
        guard recording, let folder else { return }
        recording = false
        busy = "Salvando \(keyframes) fotos…"
        let meshAnchors = arView.session.currentFrame?.anchors.compactMap { $0 as? ARMeshAnchor } ?? []
        let entries = frameEntries
        writeQueue.async {
            // 1. transforms.json (nerfstudio): abre direto no Brush
            var json: [String: Any] = ["camera_model": "OPENCV", "k1": 0, "k2": 0, "p1": 0, "p2": 0,
                                       "ply_file_path": "points.ply", "frames": entries]
            if let first = entries.first {
                for key in ["fl_x", "fl_y", "cx", "cy", "w", "h"] { json[key] = first[key] }
            }
            if let data = try? JSONSerialization.data(withJSONObject: json, options: [.prettyPrinted, .sortedKeys]) {
                try? data.write(to: folder.appendingPathComponent("transforms.json"))
            }
            // 2. Nuvem de pontos colorida
            DispatchQueue.main.async { self.busy = "Montando a nuvem de pontos…" }
            let ply = folder.appendingPathComponent("points.ply")
            Self.writePLY(points: self.cloudPoints, colors: self.cloudColors, to: ply)
            // 3. Malha do LiDAR
            DispatchQueue.main.async { self.busy = "Exportando a malha…" }
            let obj = folder.appendingPathComponent("mesh.obj")
            let faces = Self.writeOBJ(anchors: meshAnchors, to: obj)
            var usdz: URL?
            if faces > 0 {
                let target = folder.appendingPathComponent("mesh.usdz")
                let asset = MDLAsset(url: obj)
                if MDLAsset.canExportFileExtension("usdz"), (try? asset.export(to: target)) != nil { usdz = target }
            }
            try? Self.readme.write(to: folder.appendingPathComponent("LEIA-ME.txt"), atomically: true, encoding: .utf8)
            // 4. Um .zip com tudo, para mandar ao PC
            DispatchQueue.main.async { self.busy = "Compactando…" }
            let zip = Self.zip(folder)
            let points = self.cloudPoints.count
            dlog("Scanner: \(entries.count) fotos · \(points) pontos · \(faces) triângulos · zip \(zip.map { "\(((try? $0.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0) / 1_048_576) MB" } ?? "falhou")")
            DispatchQueue.main.async {
                self.busy = nil
                self.result = ScanResult(folder: folder, zip: zip, ply: ply, usdz: usdz, frames: entries.count, points: points)
            }
        }
    }

    static let readme = """
    Escaneamento do Revela (modo CENA)

    images/        fotos (com a posição exata de cada uma em transforms.json)
    depth/         profundidade do LiDAR por foto (PNG 16 bits, em milímetros)
    confidence/    confiança do LiDAR (0 baixa, 127 média, 254 alta)
    transforms.json  câmeras no formato do nerfstudio (OpenGL)
    points.ply     nuvem de pontos colorida (abre no Blender, MeshLab, CloudCompare)
    mesh.obj/usdz  malha do LiDAR

    Para um Gaussian splat realista no PC (Windows):
    1. Baixe o Brush: https://github.com/ArthurBrussee/brush (Releases)
    2. Abra o Brush e arraste o .zip deste escaneamento
    3. Deixe treinar; depois exporte o .ply do splat
    As posições vêm do LiDAR + giroscópio do iPhone, então o Brush não precisa adivinhar onde cada foto foi tirada.
    """

    // MARK: - Arquivos

    private static func copyFloats(_ buffer: CVPixelBuffer) -> [Float] {
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
        let w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer)
        let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
        guard let base = CVPixelBufferGetBaseAddress(buffer) else { return [] }
        var out = [Float](repeating: 0, count: w * h)
        for y in 0..<h {
            let row = base.advanced(by: y * rowBytes).assumingMemoryBound(to: Float.self)
            for x in 0..<w { out[y * w + x] = row[x] }
        }
        return out
    }

    private static func copyBytes(_ buffer: CVPixelBuffer) -> [UInt8] {
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
        let w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer)
        let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
        guard let base = CVPixelBufferGetBaseAddress(buffer) else { return [] }
        var out = [UInt8](repeating: 0, count: w * h)
        for y in 0..<h {
            let row = base.advanced(by: y * rowBytes).assumingMemoryBound(to: UInt8.self)
            for x in 0..<w { out[y * w + x] = row[x] }
        }
        return out
    }

    /// Profundidade em milímetros, PNG de 16 bits (o formato que os programas de splat e nerf leem).
    private static func writeDepthPNG(_ depth: [Float], width: Int, height: Int, to url: URL) {
        var mm = [UInt16](repeating: 0, count: width * height)
        for i in 0..<min(depth.count, mm.count) {
            let v = depth[i] * 1000
            mm[i] = v.isFinite ? UInt16(min(max(v, 0), 65535)) : 0
        }
        let data = mm.withUnsafeBufferPointer { Data(buffer: $0) }
        guard let provider = CGDataProvider(data: data as CFData),
              let image = CGImage(width: width, height: height, bitsPerComponent: 16, bitsPerPixel: 16, bytesPerRow: width * 2,
                                  space: CGColorSpaceCreateDeviceGray(),
                                  bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.none.rawValue | CGBitmapInfo.byteOrder16Little.rawValue),
                                  provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent)
        else { return }
        writePNG(image, to: url)
    }

    private static func writeGrayPNG(_ bytes: [UInt8], width: Int, height: Int, to url: URL) {
        let data = Data(bytes)
        guard let provider = CGDataProvider(data: data as CFData),
              let image = CGImage(width: width, height: height, bitsPerComponent: 8, bitsPerPixel: 8, bytesPerRow: width,
                                  space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.none.rawValue),
                                  provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent)
        else { return }
        writePNG(image, to: url)
    }

    private static func writePNG(_ image: CGImage, to url: URL) {
        guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else { return }
        CGImageDestinationAddImage(destination, image, nil)
        CGImageDestinationFinalize(destination)
    }

    /// PLY binário: x, y, z (float) e r, g, b (byte) por ponto.
    private static func writePLY(points: [SIMD3<Float>], colors: [SIMD3<UInt8>], to url: URL) {
        let header = """
        ply
        format binary_little_endian 1.0
        element vertex \(points.count)
        property float x
        property float y
        property float z
        property uchar red
        property uchar green
        property uchar blue
        end_header

        """
        var data = Data(header.utf8)
        data.reserveCapacity(data.count + points.count * 15)
        for (p, c) in Swift.zip(points, colors) {
            var xyz = (p.x, p.y, p.z)
            withUnsafeBytes(of: &xyz) { data.append(contentsOf: $0) }
            data.append(contentsOf: [c.x, c.y, c.z])
        }
        try? data.write(to: url)
    }

    /// Malha do LiDAR em OBJ (coordenadas do mundo). Devolve quantos triângulos escreveu.
    private static func writeOBJ(anchors: [ARMeshAnchor], to url: URL) -> Int {
        FileManager.default.createFile(atPath: url.path, contents: nil)
        guard let handle = try? FileHandle(forWritingTo: url) else { return 0 }
        defer { try? handle.close() }
        var vertexOffset = 1
        var faces = 0
        for anchor in anchors {
            let geometry = anchor.geometry
            let vertices = geometry.vertices
            var text = ""
            text.reserveCapacity(vertices.count * 40)
            let vertexBase = vertices.buffer.contents().advanced(by: vertices.offset)
            for i in 0..<vertices.count {
                let v = vertexBase.advanced(by: i * vertices.stride).assumingMemoryBound(to: Float.self)
                let world = anchor.transform * SIMD4<Float>(v[0], v[1], v[2], 1)
                text += "v \(world.x) \(world.y) \(world.z)\n"
            }
            let faceElement = geometry.faces
            let indexBase = faceElement.buffer.contents()
            for f in 0..<faceElement.count {
                var ids: [Int] = []
                for j in 0..<faceElement.indexCountPerPrimitive {
                    let at = (f * faceElement.indexCountPerPrimitive + j) * faceElement.bytesPerIndex
                    let index = faceElement.bytesPerIndex == 4
                        ? Int(indexBase.advanced(by: at).assumingMemoryBound(to: UInt32.self).pointee)
                        : Int(indexBase.advanced(by: at).assumingMemoryBound(to: UInt16.self).pointee)
                    ids.append(index + vertexOffset)
                }
                text += "f " + ids.map(String.init).joined(separator: " ") + "\n"
                faces += 1
            }
            vertexOffset += vertices.count
            handle.write(Data(text.utf8))
        }
        return faces
    }

    /// Compacta a pasta num .zip (o iOS faz isso sozinho ao "preparar para envio").
    private static func zip(_ folder: URL) -> URL? {
        var output: URL?
        var error: NSError?
        NSFileCoordinator().coordinate(readingItemAt: folder, options: .forUploading, error: &error) { zipped in
            let target = folder.deletingLastPathComponent().appendingPathComponent(folder.lastPathComponent + ".zip")
            try? FileManager.default.removeItem(at: target)
            if (try? FileManager.default.copyItem(at: zipped, to: target)) != nil { output = target }
        }
        return output
    }
}
