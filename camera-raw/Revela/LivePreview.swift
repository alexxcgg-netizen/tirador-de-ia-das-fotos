import CoreImage
import CoreImage.CIFilterBuiltins
import MetalKit
import SwiftUI

/// Desenha o vídeo da câmera já com o look aplicado, e calcula o histograma.
final class PreviewRenderer: NSObject, MTKViewDelegate {
    let device: MTLDevice = MTLCreateSystemDefaultDevice()!
    private lazy var queue = device.makeCommandQueue()!
    private lazy var context = CIContext(mtlDevice: device, options: [
        .workingColorSpace: Developer.linearP3,
        .cacheIntermediates: false,
    ])
    private let histogramQueue = DispatchQueue(label: "revela.histogram")
    private let lock = NSLock()
    private var frame: CIImage?
    private var frameCount = 0
    private var fpsWindowStart = CFAbsoluteTimeGetCurrent()
    private var fpsFrames = 0
    private var histogramBusy = false

    weak var view: MTKView?

    // Lidos e escritos só na main thread
    var options = Developer.PreviewOptions()
    /// Lupa de foco: amplia o centro 4× enquanto você ajusta o foco.
    var loupe = false
    var onHistogram: (([Float]) -> Void)?

    /// Chamado na fila de vídeo a cada quadro.
    func enqueue(_ image: CIImage) {
        lock.lock()
        frame = image
        lock.unlock()
        DispatchQueue.main.async { self.view?.draw() }
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}

    func draw(in view: MTKView) {
        lock.lock()
        let frame = self.frame
        lock.unlock()
        guard let frame, let drawable = view.currentDrawable, let buffer = queue.makeCommandBuffer() else { return }

        // Preenche a área do visor (aspect fill), centralizado, com zoom digital e lupa
        let size = view.drawableSize
        let zoom = options.develop.zoom * (loupe ? 4 : 1)
        let scale = max(size.width / frame.extent.width, size.height / frame.extent.height) * zoom
        var image = frame
            .transformed(by: CGAffineTransform(translationX: -frame.extent.minX, y: -frame.extent.minY))
            .transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        image = image.transformed(by: CGAffineTransform(
            translationX: (size.width - image.extent.width) / 2,
            y: (size.height - image.extent.height) / 2))
        image = Developer.preview(image, options: options)
            .cropped(to: CGRect(origin: .zero, size: size))

        let destination = CIRenderDestination(
            width: Int(size.width), height: Int(size.height),
            pixelFormat: view.colorPixelFormat, commandBuffer: buffer,
            mtlTextureProvider: { drawable.texture })
        _ = try? context.startTask(toRender: image, to: destination)
        buffer.present(drawable)
        buffer.commit()

        frameCount += 1
        if frameCount % 10 == 0 { computeHistogram(of: image) }

        // Quadros por segundo do visor, para o relatório
        fpsFrames += 1
        let now = CFAbsoluteTimeGetCurrent()
        if now - fpsWindowStart > 3 {
            let fps: Double = Double(fpsFrames) / (now - fpsWindowStart)
            let fpsText = String(format: "%.0f", fps)
            let lookName = options.develop.look.rawValue
            Diagnostics.shared.set("Visor", "\(fpsText) quadros/s · \(Int(size.width))×\(Int(size.height)) · look \(lookName)")
            fpsFrames = 0
            fpsWindowStart = now
        }
    }

    private func computeHistogram(of image: CIImage) {
        guard !histogramBusy else { return }
        histogramBusy = true
        let callback = onHistogram
        histogramQueue.async {
            defer { DispatchQueue.main.async { self.histogramBusy = false } }
            // Uma versão pequena basta para o histograma
            let scale = min(1, 256 / max(image.extent.width, image.extent.height))
            let small = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
            let filter = CIFilter.areaHistogram()
            filter.inputImage = small.applyingFilter("CILinearToSRGBToneCurve")
            filter.extent = small.extent
            filter.count = 64
            filter.scale = 1
            guard let output = filter.outputImage else { return }

            var bins = [Float](repeating: 0, count: 64 * 4)
            self.context.render(output, toBitmap: &bins, rowBytes: 64 * 4 * MemoryLayout<Float>.size,
                                bounds: CGRect(x: 0, y: 0, width: 64, height: 1), format: .RGBAf, colorSpace: nil)
            var luma = [Float](repeating: 0, count: 64)
            for i in 0..<64 {
                let r: Float = bins[i * 4], g: Float = bins[i * 4 + 1], b: Float = bins[i * 4 + 2]
                luma[i] = 0.2126 * r + 0.7152 * g + 0.0722 * b
            }
            if let peak = luma.max(), peak > 0 { luma = luma.map { $0 / peak } }
            DispatchQueue.main.async { callback?(luma) }
        }
    }
}

struct LivePreview: UIViewRepresentable {
    let renderer: PreviewRenderer

    func makeUIView(context: Context) -> MTKView {
        let view = MTKView(frame: .zero, device: renderer.device)
        view.framebufferOnly = false
        view.isPaused = true
        view.enableSetNeedsDisplay = false
        view.colorPixelFormat = .bgra8Unorm
        // 2× em vez de 3×: na tela do visor não dá para ver a diferença, e são metade dos pixels para revelar
        view.contentScaleFactor = min(UIScreen.main.scale, 2)
        view.backgroundColor = .black
        view.delegate = renderer
        renderer.view = view
        return view
    }

    func updateUIView(_ uiView: MTKView, context: Context) {}
}
