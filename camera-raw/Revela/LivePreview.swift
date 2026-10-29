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
    private var histogramBusy = false

    weak var view: MTKView?

    // Lidos e escritos só na main thread
    var look: Look = .filme
    var zebra = false
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

        // Preenche a área do visor (aspect fill), centralizado
        let size = view.drawableSize
        let scale = max(size.width / frame.extent.width, size.height / frame.extent.height)
        var image = frame
            .transformed(by: CGAffineTransform(translationX: -frame.extent.minX, y: -frame.extent.minY))
            .transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        image = image.transformed(by: CGAffineTransform(
            translationX: (size.width - image.extent.width) / 2,
            y: (size.height - image.extent.height) / 2))
        image = Developer.preview(image, look: look, zebra: zebra)
            .cropped(to: CGRect(origin: .zero, size: size))

        let destination = CIRenderDestination(
            width: Int(size.width), height: Int(size.height),
            pixelFormat: view.colorPixelFormat, commandBuffer: buffer,
            mtlTextureProvider: { drawable.texture })
        _ = try? context.startTask(toRender: image, to: destination)
        buffer.present(drawable)
        buffer.commit()

        frameCount += 1
        if frameCount % 6 == 0 { computeHistogram(of: image) }
    }

    private func computeHistogram(of image: CIImage) {
        guard !histogramBusy else { return }
        histogramBusy = true
        let callback = onHistogram
        histogramQueue.async {
            defer { DispatchQueue.main.async { self.histogramBusy = false } }
            let filter = CIFilter.areaHistogram()
            filter.inputImage = image.applyingFilter("CILinearToSRGBToneCurve")
            filter.extent = image.extent
            filter.count = 64
            filter.scale = 1
            guard let output = filter.outputImage else { return }

            var bins = [Float](repeating: 0, count: 64 * 4)
            self.context.render(output, toBitmap: &bins, rowBytes: 64 * 4 * MemoryLayout<Float>.size,
                                bounds: CGRect(x: 0, y: 0, width: 64, height: 1), format: .RGBAf, colorSpace: nil)
            var luma = (0..<64).map { 0.2126 * bins[$0 * 4] + 0.7152 * bins[$0 * 4 + 1] + 0.0722 * bins[$0 * 4 + 2] }
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
        view.backgroundColor = .black
        view.delegate = renderer
        renderer.view = view
        return view
    }

    func updateUIView(_ uiView: MTKView, context: Context) {}
}
