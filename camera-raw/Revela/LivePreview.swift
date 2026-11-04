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
    /// Retrato: quanto borrar o fundo no visor (0 = nada). A foto final usa a profundidade de verdade.
    var portraitBlur: Float = 0
    private var personMask: CIImage?
    /// Retrato: profundidade ao vivo (disparidade, já em pé) e a disparidade do ponto em foco.
    private var depth: CIImage?
    private var depthFocus: Float = 0

    /// Máscara de pessoa vinda da fila de vídeo (branco = pessoa).
    func setPersonMask(_ mask: CIImage?) {
        lock.lock()
        personMask = mask
        lock.unlock()
    }

    /// Profundidade vinda do LiDAR/TrueDepth (nil = sem profundidade, usa só a máscara de pessoa).
    func setDepth(_ map: CIImage?, focus: Float) {
        lock.lock()
        depth = map
        depthFocus = focus
        lock.unlock()
    }
    /// Luminância e, separados, vermelho, verde e azul (64 faixas cada, de 0 a 1).
    var onHistogram: (([Float], [[Float]]) -> Void)?

    /// Miniatura na hora do disparo: o último quadro do visor, já com o look (a foto de verdade chega depois).
    func snapshot(maxSide: CGFloat = 400) -> UIImage? {
        lock.lock()
        let frame = self.frame
        lock.unlock()
        guard let frame else { return nil }
        let scale = maxSide / max(frame.extent.width, frame.extent.height)
        let small = frame.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        var options = self.options
        options.zebra = false
        options.peaking = false
        options.falseColor = false
        let image = Developer.preview(small, options: options)
        guard let cg = context.createCGImage(image, from: image.extent, format: .RGBA8, colorSpace: Developer.displayP3) else { return nil }
        return UIImage(cgImage: cg)
    }

    /// Chamado na fila de vídeo a cada quadro.
    /// Quantos quadros chegaram ao visor (o teste de modos confere se a imagem está vindo).
    private(set) var enqueuedCount = 0

    func enqueue(_ image: CIImage) {
        lock.lock()
        frame = image
        enqueuedCount &+= 1
        lock.unlock()
        DispatchQueue.main.async { self.view?.draw() }
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}

    func draw(in view: MTKView) {
        lock.lock()
        let frame = self.frame
        let mask = personMask
        let depth = self.depth
        let depthFocus = self.depthFocus
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
        // Retrato com profundidade: bokeh de verdade no visor, mais borrado quanto mais longe do foco
        if portraitBlur > 0, let depth {
            func fit(_ m: CIImage) -> CIImage {
                m.transformed(by: CGAffineTransform(translationX: -m.extent.minX, y: -m.extent.minY))
                    .transformed(by: CGAffineTransform(scaleX: image.extent.width / m.extent.width, y: image.extent.height / m.extent.height))
                    .transformed(by: CGAffineTransform(translationX: image.extent.minX, y: image.extent.minY))
            }
            let disparity = fit(depth).clampedToExtent().applyingGaussianBlur(sigma: 3).cropped(to: image.extent)
            let matte = mask.map(fit) ?? CIImage(color: .black).cropped(to: image.extent)
            let strength = portraitBlur * 3
            if let map = Developer.blurMap(disparity: disparity, matte: matte, focus: depthFocus, strength: strength) {
                image = Developer.liveBokeh(image, map: map, radius: image.extent.width * 0.014 * CGFloat(portraitBlur))
            }
        } else if portraitBlur > 0, let mask {
            let fitted = mask.transformed(by: CGAffineTransform(scaleX: image.extent.width / mask.extent.width,
                                                                y: image.extent.height / mask.extent.height))
                .transformed(by: CGAffineTransform(translationX: image.extent.minX, y: image.extent.minY))
            let blurred = image.clampedToExtent()
                .applyingGaussianBlur(sigma: Double(CGFloat(portraitBlur) * size.width * 0.01))
                .cropped(to: image.extent)
            image = image.applyingFilter("CIBlendWithMask", parameters: [
                kCIInputBackgroundImageKey: blurred,
                kCIInputMaskImageKey: fitted,
            ])
        }
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
            let lookName = options.develop.lookName
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
            var red = [Float](repeating: 0, count: 64)
            var green = [Float](repeating: 0, count: 64)
            var blue = [Float](repeating: 0, count: 64)
            for i in 0..<64 {
                let r: Float = bins[i * 4], g: Float = bins[i * 4 + 1], b: Float = bins[i * 4 + 2]
                red[i] = r
                green[i] = g
                blue[i] = b
                luma[i] = 0.2126 * r + 0.7152 * g + 0.0722 * b
            }
            if let peak = luma.max(), peak > 0 { luma = luma.map { $0 / peak } }
            let peakRGB = max(red.max() ?? 0, green.max() ?? 0, blue.max() ?? 0)
            let rgb: [[Float]] = peakRGB > 0 ? [red, green, blue].map { channel in channel.map { $0 / peakRGB } } : []
            DispatchQueue.main.async { callback?(luma, rgb) }
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
