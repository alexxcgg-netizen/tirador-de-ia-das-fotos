import CoreImage
import CoreImage.CIFilterBuiltins
import Photos
import SwiftUI
import VisionKit

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Scanner de documentos: usa a câmera de documentos do iOS (acha a folha sozinho, endireita,
/// aceita várias páginas) e o Revela limpa as páginas e junta tudo num PDF, sem marca d'água.
struct DocumentScanView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var pages: [UIImage] = []
    @State private var scanning = true
    @State private var style: DocStyle = .clean
    @State private var processed: [UIImage] = []
    @State private var working = false
    @State private var pdfURL: URL?
    @State private var message: String?
    /// Só a montagem mais recente vale (trocar o estilo várias vezes rápido não embaralha as páginas).
    @State private var generation = 0

    var body: some View {
        Group {
            if scanning {
                DocumentCamera { result in
                    scanning = false
                    switch result {
                    case .success(let scanned):
                        if scanned.isEmpty { dismiss() } else { pages += scanned; rebuild() }
                    case .cancelled:
                        if pages.isEmpty { dismiss() }
                    case .failed(let error):
                        dlog("Documento: falhou \(error.localizedDescription)")
                        message = "O scanner falhou: \(error.localizedDescription)"
                    }
                }
                .ignoresSafeArea()
            } else {
                result
            }
        }
        .preferredColorScheme(.dark)
        .tint(accent)
    }

    private var result: some View {
        NavigationStack {
            VStack(spacing: 12) {
                Picker("Estilo", selection: $style) {
                    ForEach(DocStyle.allCases) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 16)
                .onChange(of: style) { _, _ in rebuild() }

                ScrollView {
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(Array(processed.enumerated()), id: \.offset) { index, page in
                            VStack(spacing: 4) {
                                Image(uiImage: page)
                                    .resizable().scaledToFit()
                                    .clipShape(RoundedRectangle(cornerRadius: 6))
                                    .shadow(radius: 3)
                                HStack {
                                    Text("Página \(index + 1)").font(.caption).opacity(0.7)
                                    Spacer()
                                    Button(role: .destructive) { remove(index) } label: { Image(systemName: "trash") }
                                        .font(.caption)
                                }
                            }
                        }
                    }
                    .padding(16)
                }

                if let message {
                    Text(message).font(.footnote).foregroundStyle(.secondary).padding(.horizontal)
                }

                HStack(spacing: 10) {
                    Button {
                        scanning = true
                    } label: {
                        Label("Mais páginas", systemImage: "plus.viewfinder").frame(maxWidth: .infinity, minHeight: 48)
                    }
                    .buttonStyle(.bordered)
                    Button { savePhotos() } label: {
                        Label("Galeria", systemImage: "photo").frame(maxWidth: .infinity, minHeight: 48)
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.horizontal, 16)

                if let pdfURL, !working {
                    ShareLink(item: pdfURL) {
                        Label("Salvar ou enviar PDF (\(processed.count) pág.)", systemImage: "doc.richtext")
                            .font(.body.weight(.bold))
                            .frame(maxWidth: .infinity, minHeight: 50)
                            .background(Capsule().fill(accent))
                            .foregroundStyle(.black)
                    }
                    .padding(.horizontal, 16)
                } else if working {
                    ProgressView("Montando o PDF…").frame(minHeight: 50)
                }
            }
            .padding(.bottom, 8)
            .navigationTitle("Documento")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Fechar") { dismiss() } } }
        }
    }

    private func remove(_ index: Int) {
        guard pages.indices.contains(index) else { return }
        pages.remove(at: index)
        if pages.isEmpty { scanning = true } else { rebuild() }
    }

    /// Aplica o estilo em todas as páginas e monta o PDF de novo.
    private func rebuild() {
        working = true
        pdfURL = nil
        generation += 1
        let gen = generation
        let pages = self.pages, style = self.style
        DispatchQueue.global(qos: .userInitiated).async {
            let t0 = CFAbsoluteTimeGetCurrent()
            let cleaned = pages.map { DocumentCleaner.apply(style, to: $0) }
            let url = DocumentCleaner.makePDF(cleaned)
            let bytes: Int? = url.flatMap { (try? $0.resourceValues(forKeys: [.fileSizeKey]))?.fileSize }
            let size = bytes.map { "\($0 / 1024) KB" } ?? "falhou"
            dlog("Documento: \(pages.count) página(s) · \(style.rawValue) · PDF \(size) · \(Diagnostics.ms(since: t0))")
            DispatchQueue.main.async {
                guard gen == generation else { return }
                processed = cleaned
                pdfURL = url
                working = false
                if url == nil { message = "Não consegui montar o PDF." }
            }
        }
    }

    private func savePhotos() {
        let images = processed
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else {
                DispatchQueue.main.async { message = RevelaError.photosDenied.localizedDescription }
                return
            }
            PHPhotoLibrary.shared().performChanges({
                for image in images {
                    if let data = image.jpegData(compressionQuality: 0.85) {
                        PHAssetCreationRequest.forAsset().addResource(with: .photo, data: data, options: nil)
                    }
                }
            }, completionHandler: { _, error in
                DispatchQueue.main.async {
                    // O erro do iOS sozinho não dizia o que fazer: vai com a explicação em português na frente
                    message = error.map { RevelaError.explained($0).localizedDescription } ?? "\(images.count) página(s) salvas na galeria."
                }
            })
        }
    }
}

enum DocStyle: String, CaseIterable, Identifiable {
    case clean = "Limpo"
    case color = "Cor original"
    case blackWhite = "Preto e branco"
    case gray = "Cinza"

    var id: String { rawValue }
}

enum DocumentCleaner {
    private static let context = CIContext()

    static func apply(_ style: DocStyle, to page: UIImage) -> UIImage {
        guard style != .color, let input = CIImage(image: page)?.oriented(.up) else { return downscaled(page) }
        let image = scaled(input)
        let output: CIImage
        switch style {
        case .color:
            output = image
        case .clean:
            // Papel branco por igual (tira a sombra da mão e o amarelado), cor dos carimbos e canetas mantida
            output = whitened(image, keepColor: true)
        case .blackWhite:
            output = whitened(image, keepColor: false)
                .applyingFilter("CIColorControls", parameters: [kCIInputContrastKey: 1.9, kCIInputBrightnessKey: 0.06])
        case .gray:
            output = whitened(image, keepColor: false)
        }
        guard let cg = context.createCGImage(output, from: output.extent) else { return downscaled(page) }
        return UIImage(cgImage: cg)
    }

    /// Divide a página pelo "fundo" (a página com o texto apagado): o papel vira branco puro e o texto fica.
    private static func whitened(_ image: CIImage, keepColor: Bool) -> CIImage {
        let e = image.extent
        let source = keepColor ? image : image.applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 0])
        let radius = max(e.width, e.height) * 0.006
        let background = source
            .applyingFilter("CIMorphologyMaximum", parameters: [kCIInputRadiusKey: radius])
            .clampedToExtent()
            .applyingGaussianBlur(sigma: Double(radius * 2))
            .cropped(to: e)
        let divided = Developer.paperKernel?.apply(extent: e, arguments: [source, background]) ?? source
        // Texto mais escuro e papel branco
        return divided.applyingFilter("CIToneCurve", parameters: [
            "inputPoint0": CIVector(x: 0, y: 0),
            "inputPoint1": CIVector(x: 0.35, y: 0.12),
            "inputPoint2": CIVector(x: 0.7, y: 0.6),
            "inputPoint3": CIVector(x: 0.9, y: 0.97),
            "inputPoint4": CIVector(x: 1, y: 1),
        ])
    }

    /// Páginas com no máximo 2400 px no lado maior (texto nítido, PDF leve).
    private static func scaled(_ image: CIImage) -> CIImage {
        let long = max(image.extent.width, image.extent.height)
        guard long > 2400 else { return image }
        let s = 2400 / long
        return image.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
    }

    private static func downscaled(_ page: UIImage) -> UIImage {
        guard let ci = CIImage(image: page)?.oriented(.up) else { return page }
        let image = scaled(ci)
        guard let cg = context.createCGImage(image, from: image.extent) else { return page }
        return UIImage(cgImage: cg)
    }

    /// PDF com uma página por imagem, largura de folha A4 e a altura que a página pedir.
    static func makePDF(_ pages: [UIImage]) -> URL? {
        guard !pages.isEmpty else { return nil }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH.mm"
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("Documento \(formatter.string(from: Date())).pdf")
        let width: CGFloat = 595
        let renderer = UIGraphicsPDFRenderer(bounds: CGRect(x: 0, y: 0, width: width, height: 842))
        do {
            try renderer.writePDF(to: url) { ctx in
                for page in pages {
                    let height = width * page.size.height / max(page.size.width, 1)
                    let bounds = CGRect(x: 0, y: 0, width: width, height: height)
                    ctx.beginPage(withBounds: bounds, pageInfo: [:])
                    // JPEG dentro do PDF: o arquivo fica pequeno o bastante para mandar no WhatsApp
                    if let jpeg = page.jpegData(compressionQuality: 0.72),
                       let provider = CGDataProvider(data: jpeg as CFData),
                       let cg = CGImage(jpegDataProviderSource: provider, decode: nil, shouldInterpolate: true, intent: .defaultIntent) {
                        ctx.cgContext.saveGState()
                        ctx.cgContext.translateBy(x: 0, y: height)
                        ctx.cgContext.scaleBy(x: 1, y: -1)
                        ctx.cgContext.draw(cg, in: bounds)
                        ctx.cgContext.restoreGState()
                    } else {
                        page.draw(in: bounds)
                    }
                }
            }
            return url
        } catch {
            dlog("Documento: PDF falhou \(error.localizedDescription)")
            return nil
        }
    }
}

/// A câmera de documentos do iOS.
private struct DocumentCamera: UIViewControllerRepresentable {
    enum Outcome {
        case success([UIImage])
        case cancelled
        case failed(Error)
    }

    let completion: (Outcome) -> Void

    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let controller = VNDocumentCameraViewController()
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(_ controller: VNDocumentCameraViewController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(completion: completion) }

    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let completion: (Outcome) -> Void
        init(completion: @escaping (Outcome) -> Void) { self.completion = completion }

        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            completion(.success((0..<scan.pageCount).map { scan.imageOfPage(at: $0) }))
        }

        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
            completion(.cancelled)
        }

        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFailWithError error: Error) {
            completion(.failed(error))
        }
    }
}
