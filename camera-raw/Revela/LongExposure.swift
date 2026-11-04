import CoreImage
import CoreVideo
import Vision

/// Exposição longa: soma (seda) ou guarda o mais claro (rastros) de cada quadro do vídeo durante alguns segundos.
/// Usa dois buffers que se alternam na memória de vídeo, sem guardar os quadros. Roda na fila de vídeo.
final class LongExposure {
    enum Style: String, CaseIterable, Identifiable {
        case silk = "Seda"
        case trails = "Rastros"
        var id: String { rawValue }
    }

    private var buffers: [CVPixelBuffer] = []
    private var current = 0
    private var accumulated: CIImage?
    private var extent: CGRect = .zero
    private(set) var count = 0
    private(set) var isRunning = false
    private var style: Style = .silk
    private var endTime: CFAbsoluteTime = 0
    private var finished: ((CIImage?, Int) -> Void)?
    /// Na mão: cada quadro é alinhado com o primeiro antes de somar.
    private var handheld = false
    private var referenceSmall: CIImage?
    private var maxShift = CGSize.zero
    private let alignScale: CGFloat = 0.2

    func start(seconds: Double, style: Style, handheld: Bool, completion: @escaping (CIImage?, Int) -> Void) {
        self.style = style
        self.handheld = handheld
        referenceSmall = nil
        maxShift = .zero
        accumulated = nil
        count = 0
        buffers = []
        endTime = CFAbsoluteTimeGetCurrent() + seconds
        finished = completion
        isRunning = true
    }

    func add(_ frame: CIImage) {
        guard isRunning else { return }
        // O tempo acabou: termina mesmo que este quadro não sirva (antes a LONGA podia nunca acabar)
        if accumulated != nil, CFAbsoluteTimeGetCurrent() >= endTime { return stop() }
        // Logo depois de ligar ainda podem chegar quadros no tamanho do visor: recomeça no tamanho novo
        if accumulated != nil, frame.extent.size != extent.size {
            guard count < 20 else { return }
            accumulated = nil
            buffers = []
            count = 0
            referenceSmall = nil
            maxShift = .zero
        }
        if accumulated == nil {
            extent = frame.extent
            guard makeBuffers() else {
                stop()
                return
            }
        }
        var shifted = frame.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        if handheld { shifted = align(shifted) }
        let next: CIImage
        if let accumulated {
            let kernel = style == .silk ? Developer.sumKernel : Developer.maxKernel
            next = kernel?.apply(extent: shifted.extent, arguments: [accumulated, shifted]) ?? accumulated
        } else {
            next = shifted
        }
        // Calcula agora num dos dois buffers, alternando, para não acumular uma cadeia de filtros
        let target = buffers[current]
        current = 1 - current
        Developer.context.render(next, to: target, bounds: CGRect(origin: .zero, size: extent.size), colorSpace: Developer.linearP3)
        accumulated = CIImage(cvPixelBuffer: target, options: [.colorSpace: Developer.linearP3])
        count += 1
        if CFAbsoluteTimeGetCurrent() >= endTime { stop() }
    }

    /// Desloca o quadro para cair em cima do primeiro (Vision numa versão pequena: rápido o bastante a 30 por segundo).
    private func align(_ image: CIImage) -> CIImage {
        let small = image.transformed(by: CGAffineTransform(scaleX: alignScale, y: alignScale))
        guard let referenceSmall else {
            // Guarda o primeiro quadro (cópia: o buffer da câmera volta para ela)
            if let cg = Developer.context.createCGImage(small, from: small.extent) { referenceSmall = CIImage(cgImage: cg) }
            return image
        }
        let request = VNTranslationalImageRegistrationRequest(targetedCIImage: small, options: [:])
        guard (try? VNImageRequestHandler(ciImage: referenceSmall, options: [:]).perform([request])) != nil,
              let observation = request.results?.first as? VNImageTranslationAlignmentObservation else { return image }
        let tx = observation.alignmentTransform.tx / alignScale, ty = observation.alignmentTransform.ty / alignScale
        // Pulo grande demais é erro do alinhamento: usa o quadro como veio
        guard abs(tx) < extent.width * 0.12, abs(ty) < extent.height * 0.12 else { return image }
        maxShift = CGSize(width: max(maxShift.width, abs(tx)), height: max(maxShift.height, abs(ty)))
        return image.transformed(by: CGAffineTransform(translationX: tx, y: ty)).cropped(to: CGRect(origin: .zero, size: extent.size))
    }

    func stop() {
        guard isRunning else { return }
        isRunning = false
        var result = accumulated
        if style == .silk, let sum = accumulated, count > 0 {
            let k = CGFloat(1) / CGFloat(count)
            result = sum.applyingFilter("CIColorMatrix", parameters: [
                "inputRVector": CIVector(x: k, y: 0, z: 0, w: 0),
                "inputGVector": CIVector(x: 0, y: k, z: 0, w: 0),
                "inputBVector": CIVector(x: 0, y: 0, z: k, w: 0),
                "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
            ])
        }
        // Na mão: corta a borda que nem todos os quadros cobriram
        if handheld, let image = result, maxShift != .zero {
            let inset = CGRect(origin: .zero, size: extent.size)
                .insetBy(dx: ceil(maxShift.width) + 2, dy: ceil(maxShift.height) + 2)
            if inset.width > extent.width * 0.6, inset.height > extent.height * 0.6 {
                result = image.cropped(to: inset).transformed(by: CGAffineTransform(translationX: -inset.minX, y: -inset.minY))
            }
        }
        // Copia o resultado para fora dos buffers de trabalho antes de soltá-los
        if let image = result {
            let size = image.extent.size
            var out: CVPixelBuffer?
            CVPixelBufferCreate(nil, Int(size.width), Int(size.height), kCVPixelFormatType_64RGBAHalf,
                                [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any]] as CFDictionary, &out)
            if let out {
                Developer.context.render(image, to: out, bounds: CGRect(origin: .zero, size: size), colorSpace: Developer.linearP3)
                result = CIImage(cvPixelBuffer: out, options: [.colorSpace: Developer.linearP3])
            }
        }
        buffers = []
        accumulated = nil
        let done = finished
        finished = nil
        done?(result, count)
    }

    private func makeBuffers() -> Bool {
        let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any],
                                           kCVPixelBufferMetalCompatibilityKey: true]
        for _ in 0..<2 {
            var buffer: CVPixelBuffer?
            guard CVPixelBufferCreate(nil, Int(extent.width), Int(extent.height), kCVPixelFormatType_64RGBAHalf,
                                      attributes as CFDictionary, &buffer) == kCVReturnSuccess, let buffer else { return false }
            buffers.append(buffer)
        }
        current = 0
        return true
    }
}
