import QuickLook
import RealityKit
import SceneKit
import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Tela do scanner 3D: CENA (LiDAR + fotos, pacote para Gaussian splatting) e OBJETO (Object Capture da Apple).
struct ScannerView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var scanner = SceneScanner()
    @State private var mode = 0
    @State private var showCloud = false
    @State private var quickLook: URL?

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            if mode == 0 {
                ARContainer(arView: scanner.arView).ignoresSafeArea()
                sceneHUD
            } else if #available(iOS 17.0, *) {
                ObjectCaptureFlow(quickLook: $quickLook)
            } else {
                Text("O modo OBJETO precisa do iOS 17.").foregroundStyle(.white)
            }
            VStack {
                HStack {
                    Picker("Modo", selection: $mode) {
                        Text("CENA").tag(0)
                        Text("OBJETO").tag(1)
                    }
                    .pickerStyle(.segmented)
                    .frame(maxWidth: 220)
                    .disabled(scanner.recording || scanner.busy != nil)
                    Spacer()
                    Button { dismiss() } label: {
                        Image(systemName: "xmark")
                            .font(.system(size: 17, weight: .bold))
                            .frame(width: 44, height: 44)
                            .foregroundStyle(.white)
                            .background(Circle().fill(Color.black.opacity(0.55)))
                    }
                    .accessibilityLabel("Fechar scanner")
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
                Spacer()
            }
        }
        .preferredColorScheme(.dark)
        .tint(accent)
        .onAppear { scanner.startPreview() }
        .onDisappear { scanner.stop() }
        .onChange(of: mode) { _, newMode in
            // O OBJETO usa a câmera do jeito dele: a sessão da CENA precisa parar
            if newMode == 0 { scanner.startPreview() } else { scanner.stop() }
        }
        .sheet(isPresented: $showCloud) {
            if let ply = scanner.result?.ply { PointCloudView(plyURL: ply).ignoresSafeArea() }
        }
        .quickLookPreview($quickLook)
    }

    // MARK: - CENA

    private var sceneHUD: some View {
        VStack(spacing: 12) {
            Spacer()
            Text(scanner.busy ?? scanner.status)
                .font(.subheadline.weight(.semibold))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 14).padding(.vertical, 8)
                .background(.black.opacity(0.6), in: RoundedRectangle(cornerRadius: 12))

            if scanner.recording || scanner.keyframes > 0 {
                HStack(spacing: 18) {
                    Label("\(scanner.keyframes) fotos", systemImage: "camera.fill")
                    Label(pointsText(scanner.pointCount), systemImage: "circle.grid.3x3.fill")
                }
                .font(.footnote.weight(.bold))
                .padding(.horizontal, 14).padding(.vertical, 8)
                .background(.black.opacity(0.6), in: Capsule())
            }

            if let result = scanner.result {
                resultPanel(result)
            } else if scanner.busy == nil {
                Button {
                    if scanner.recording { scanner.finish() } else { scanner.startRecording() }
                    UIImpactFeedbackGenerator(style: .medium).impactOccurred()
                } label: {
                    ZStack {
                        Circle().stroke(.white, lineWidth: 5).frame(width: 84, height: 84)
                        RoundedRectangle(cornerRadius: scanner.recording ? 8 : 34)
                            .fill(Color.red)
                            .frame(width: scanner.recording ? 36 : 68, height: scanner.recording ? 36 : 68)
                    }
                }
                .accessibilityLabel(scanner.recording ? "Terminar escaneamento" : "Começar escaneamento")
                Text(scanner.recording
                     ? "Ande devagar em volta. Passe por cima e por baixo também. Toque para terminar."
                     : "A malha colorida mostra o que o LiDAR já viu. Comece pertinho e vá cobrindo tudo.")
                    .font(.caption).foregroundStyle(.white.opacity(0.8))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 24)
            } else {
                ProgressView().tint(.white)
            }
        }
        .padding(.bottom, 24)
    }

    private func resultPanel(_ result: SceneScanner.ScanResult) -> some View {
        VStack(spacing: 10) {
            Text("\(result.frames) fotos · \(pointsText(result.points))")
                .font(.headline)
            HStack(spacing: 10) {
                Button { showCloud = true } label: {
                    Label("Ver em 3D", systemImage: "cube.transparent").frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.borderedProminent)
                if let usdz = result.usdz {
                    Button { quickLook = usdz } label: {
                        Label("Malha em AR", systemImage: "arkit").frame(maxWidth: .infinity, minHeight: 44)
                    }
                    .buttonStyle(.bordered)
                }
            }
            if let zip = result.zip {
                ShareLink(item: zip) {
                    Label("Mandar o pacote para o PC (.zip)", systemImage: "square.and.arrow.up")
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.bordered)
            }
            Text("No PC: abra o Brush (github.com/ArthurBrussee/brush) e arraste o .zip para gerar o Gaussian splat.")
                .font(.caption).foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("Novo escaneamento") { scanner.startRecording() }
                .font(.subheadline.weight(.semibold))
        }
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 18).fill(Color.black.opacity(0.75)))
        .padding(.horizontal, 16)
    }

    private func pointsText(_ n: Int) -> String {
        n >= 1_000_000 ? String(format: "%.1f mi de pontos", Double(n) / 1_000_000).replacingOccurrences(of: ".", with: ",")
            : "\(n / 1000) mil pontos"
    }
}

private struct ARContainer: UIViewRepresentable {
    let arView: ARView
    func makeUIView(context: Context) -> ARView { arView }
    func updateUIView(_ uiView: ARView, context: Context) {}
}

// MARK: - OBJETO (Object Capture da Apple)

@available(iOS 17.0, *)
struct ObjectCaptureFlow: View {
    @Binding var quickLook: URL?
    @State private var session: ObjectCaptureSession?
    @State private var stateText = "Preparando…"
    @State private var isReady = false
    @State private var isDetecting = false
    @State private var isCapturing = false
    @State private var progress: Double?
    @State private var errorText: String?
    @State private var modelURL: URL?
    @State private var imagesFolder: URL?

    var body: some View {
        ZStack {
            if let session {
                ObjectCaptureView(session: session).ignoresSafeArea()
            }
            VStack(spacing: 12) {
                Spacer()
                Text(errorText ?? stateText)
                    .font(.subheadline.weight(.semibold))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 14).padding(.vertical, 8)
                    .background(.black.opacity(0.6), in: RoundedRectangle(cornerRadius: 12))
                    .padding(.horizontal, 16)
                if let progress {
                    ProgressView(value: progress).tint(accent).padding(.horizontal, 40)
                }
                if let modelURL {
                    HStack(spacing: 10) {
                        Button { quickLook = modelURL } label: {
                            Label("Ver em AR", systemImage: "arkit").frame(maxWidth: .infinity, minHeight: 44)
                        }
                        .buttonStyle(.borderedProminent)
                        ShareLink(item: modelURL) {
                            Label("Compartilhar", systemImage: "square.and.arrow.up").frame(maxWidth: .infinity, minHeight: 44)
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding(.horizontal, 16)
                } else if let session {
                    actionButton(session)
                }
            }
            .padding(.bottom, 24)
        }
        .task { await start() }
        .onDisappear { session?.cancel() }
    }

    @ViewBuilder
    private func actionButton(_ session: ObjectCaptureSession) -> some View {
        if isReady {
            Button("Achar o objeto") { _ = session.startDetecting() }.buttonStyle(.borderedProminent)
        } else if isDetecting {
            Button("Começar a fotografar") { session.startCapturing() }.buttonStyle(.borderedProminent)
        } else if isCapturing {
            Button("Terminar") { session.finish() }.buttonStyle(.borderedProminent)
        }
    }

    private func start() async {
        guard ObjectCaptureSession.isSupported else {
            errorText = "Este iPhone não faz Object Capture. Use o modo CENA."
            return
        }
        let base = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Scans/objeto-\(Int(Date().timeIntervalSince1970))", isDirectory: true)
        let images = base.appendingPathComponent("images", isDirectory: true)
        let checkpoint = base.appendingPathComponent("checkpoint", isDirectory: true)
        try? FileManager.default.createDirectory(at: images, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: checkpoint, withIntermediateDirectories: true)
        imagesFolder = images
        var configuration = ObjectCaptureSession.Configuration()
        configuration.checkpointDirectory = checkpoint
        let newSession = ObjectCaptureSession()
        newSession.start(imagesDirectory: images, configuration: configuration)
        session = newSession
        dlog("Objeto: Object Capture iniciado")
        for await state in newSession.stateUpdates {
            isReady = false
            isDetecting = false
            isCapturing = false
            switch state {
            case .ready:
                isReady = true
                stateText = "Coloque o objeto no centro e toque em Achar o objeto"
            case .detecting:
                isDetecting = true
                stateText = "Ajuste a caixa em volta do objeto"
            case .capturing:
                isCapturing = true
                stateText = "Ande devagar em volta do objeto; o anel mostra o que falta"
            case .finishing:
                stateText = "Finalizando a captura…"
            case .completed:
                stateText = "Montando o modelo 3D no iPhone…"
                await reconstruct(images: images, base: base)
            case .failed(let error):
                dlog("Objeto: Object Capture falhou: \(error.localizedDescription)")
                errorText = "O Object Capture falhou (\(error.localizedDescription)). No iPhone 17 Pro isso é um defeito conhecido do iOS; use o modo CENA."
            default:
                stateText = "Preparando…"
            }
        }
    }

    private func reconstruct(images: URL, base: URL) async {
        guard PhotogrammetrySession.isSupported else {
            errorText = "Este iPhone não monta modelos 3D. As fotos ficaram salvas em Arquivos."
            return
        }
        let output = base.appendingPathComponent("modelo.usdz")
        do {
            var configuration = PhotogrammetrySession.Configuration()
            configuration.checkpointDirectory = base.appendingPathComponent("checkpoint", isDirectory: true)
            let photogrammetry = try PhotogrammetrySession(input: images, configuration: configuration)
            try photogrammetry.process(requests: [.modelFile(url: output, detail: .reduced)])
            for try await message in photogrammetry.outputs {
                switch message {
                case .requestProgress(_, let fraction):
                    progress = fraction
                case .requestError(_, let error):
                    throw error
                case .processingComplete:
                    progress = nil
                    modelURL = output
                    stateText = "Modelo pronto"
                    dlog("Objeto: modelo 3D pronto")
                default:
                    break
                }
            }
        } catch {
            progress = nil
            dlog("Objeto: reconstrução falhou: \(error.localizedDescription)")
            errorText = "Não deu para montar o modelo (\(error.localizedDescription)). Use o modo CENA."
        }
    }
}

// MARK: - Visualizador da nuvem de pontos

struct PointCloudView: UIViewRepresentable {
    let plyURL: URL

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView()
        view.backgroundColor = .black
        view.allowsCameraControl = true
        view.autoenablesDefaultLighting = false
        view.scene = Self.scene(from: plyURL)
        return view
    }

    func updateUIView(_ uiView: SCNView, context: Context) {}

    /// Lê o PLY que o scanner gravou (15 bytes por ponto) e mostra até 1,5 milhão de pontos.
    static func scene(from url: URL) -> SCNScene {
        let scene = SCNScene()
        guard let data = try? Data(contentsOf: url, options: .mappedIfSafe),
              let end = data.range(of: Data("end_header\n".utf8)) else { return scene }
        let body = data[end.upperBound...]
        let total = body.count / 15
        guard total > 0 else { return scene }
        let step = max(1, total / 1_500_000)
        var vertices: [SCNVector3] = []
        var colors: [Float] = []
        vertices.reserveCapacity(total / step)
        colors.reserveCapacity(total / step * 3)
        var center = SIMD3<Float>(0, 0, 0)
        body.withUnsafeBytes { raw in
            for i in stride(from: 0, to: total, by: step) {
                let o = i * 15
                let x = raw.loadUnaligned(fromByteOffset: o, as: Float.self)
                let y = raw.loadUnaligned(fromByteOffset: o + 4, as: Float.self)
                let z = raw.loadUnaligned(fromByteOffset: o + 8, as: Float.self)
                vertices.append(SCNVector3(x, y, z))
                center += SIMD3(x, y, z)
                colors.append(Float(raw[o + 12]) / 255)
                colors.append(Float(raw[o + 13]) / 255)
                colors.append(Float(raw[o + 14]) / 255)
            }
        }
        center /= Float(vertices.count)
        let vertexSource = SCNGeometrySource(vertices: vertices)
        let colorData = colors.withUnsafeBufferPointer { Data(buffer: $0) }
        let colorSource = SCNGeometrySource(data: colorData, semantic: .color, vectorCount: vertices.count,
                                            usesFloatComponents: true, componentsPerVector: 3, bytesPerComponent: 4,
                                            dataOffset: 0, dataStride: 12)
        let indices = (0..<UInt32(vertices.count)).map { $0 }
        let element = SCNGeometryElement(indices: indices, primitiveType: .point)
        element.pointSize = 3
        element.minimumPointScreenSpaceRadius = 1
        element.maximumPointScreenSpaceRadius = 6
        let geometry = SCNGeometry(sources: [vertexSource, colorSource], elements: [element])
        let material = SCNMaterial()
        material.lightingModel = .constant
        geometry.materials = [material]
        let node = SCNNode(geometry: geometry)
        node.position = SCNVector3(-center.x, -center.y, -center.z)
        scene.rootNode.addChildNode(node)
        let camera = SCNNode()
        camera.camera = SCNCamera()
        camera.camera?.zNear = 0.01
        camera.position = SCNVector3(0, 0, 2.5)
        scene.rootNode.addChildNode(camera)
        return scene
    }
}
