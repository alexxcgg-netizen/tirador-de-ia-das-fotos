import CoreImage
import CoreVideo

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

    func start(seconds: Double, style: Style, completion: @escaping (CIImage?, Int) -> Void) {
        self.style = style
        accumulated = nil
        count = 0
        buffers = []
        endTime = CFAbsoluteTimeGetCurrent() + seconds
        finished = completion
        isRunning = true
    }

    func add(_ frame: CIImage) {
        guard isRunning else { return }
        if accumulated == nil {
            extent = frame.extent
            guard makeBuffers() else {
                stop()
                return
            }
        }
        let shifted = frame.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
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
        // Copia o resultado para fora dos buffers de trabalho antes de soltá-los
        if let image = result {
            var out: CVPixelBuffer?
            CVPixelBufferCreate(nil, Int(extent.width), Int(extent.height), kCVPixelFormatType_64RGBAHalf,
                                [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any]] as CFDictionary, &out)
            if let out {
                Developer.context.render(image, to: out, bounds: CGRect(origin: .zero, size: extent.size), colorSpace: Developer.linearP3)
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
