import CoreImage
import CoreVideo
import Vision

/// Exposição longa: soma (seda) ou guarda o mais claro (rastros) de cada quadro do vídeo durante alguns segundos.
/// Usa buffers que se alternam na memória de vídeo, sem guardar os quadros. Roda na fila de vídeo.
final class LongExposure {
    enum Style: String, CaseIterable, Identifiable {
        case silk = "Seda"
        case trails = "Rastros"
        var id: String { rawValue }
    }

    /// Soma em 32 bits: em meia precisão a soma passava de 128 em ~300 quadros e cada quadro novo era arredondado
    /// (o que somava menos de 0,06 sumia). Dois que se alternam, para não ler e escrever no mesmo
    private var sumBuffers: [CVPixelBuffer] = []
    /// Rastros: o máximo de cada ponto (máximo não acumula erro: meia precisão basta)
    private var trailBuffers: [CVPixelBuffer] = []
    private var current = 0
    private var sum: CIImage?
    private var trail: CIImage?
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
    /// Rastros: quanto o máximo de N quadros de puro ruído sobe acima da média (medido no 1º quadro): sai do máximo no fim
    private var trailThreshold: Float = 0.002

    /// Conta em 32 bits: o contexto de sempre trabalha em meia precisão e arredondaria a soma de novo no caminho
    private static let floatContext = CIContext(options: [
        .workingColorSpace: Developer.linearP3,
        .workingFormat: CIFormat.RGBAf,
        .cacheIntermediates: false,
    ])
    private var renderContext: CIContext = LongExposure.floatContext

    func start(seconds: Double, style: Style, handheld: Bool, completion: @escaping (CIImage?, Int) -> Void) {
        self.style = style
        self.handheld = handheld
        referenceSmall = nil
        maxShift = .zero
        sum = nil
        trail = nil
        count = 0
        sumBuffers = []
        trailBuffers = []
        endTime = CFAbsoluteTimeGetCurrent() + seconds
        finished = completion
        isRunning = true
    }

    func add(_ frame: CIImage) {
        guard isRunning else { return }
        // O tempo acabou: termina mesmo que este quadro não sirva (antes a LONGA podia nunca acabar)
        if sum != nil, CFAbsoluteTimeGetCurrent() >= endTime { return stop() }
        // Logo depois de ligar ainda podem chegar quadros no tamanho do visor: recomeça no tamanho novo
        if sum != nil, frame.extent.size != extent.size {
            guard count < 20 else { return }
            sum = nil
            trail = nil
            sumBuffers = []
            trailBuffers = []
            count = 0
            referenceSmall = nil
            maxShift = .zero
        }
        if sum == nil {
            extent = frame.extent
            guard makeBuffers() else {
                stop()
                return
            }
        }
        let bounds = CGRect(origin: .zero, size: extent.size)
        var shifted = frame.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        if handheld { shifted = align(shifted) }
        if count == 0 {
            // Ruído do quadro (detalhe de 1 px, mediana; ~0,87σ no ruído branco): o máximo de 60 quadros de ruído sobe ~2,3σ.
            // 2,3× o medido (= 2σ) tira quase tudo disso. Antes: o maior excesso sobre a média corrente, menos max(0,004;
            // 3× o ruído) + 5% da média — na rampa clara do laboratório isso passava de 1 código (o pontilhado de 1 código
            // nunca chegava ao limite: erro 1,03 códigos, meta 0,5). Estudo em Python nos quadros do teste: rampa 0,35
            // código, escuro sobe 0,64σ (máximo puro: 2,33σ). Piso 0,0005: quadro de vídeo quase sem ruído medido
            trailThreshold = max(0.0005, 2.3 * Developer.measuredNoise(shifted.cropped(to: bounds)))
        }
        // Rastros: o máximo de cada ponto (no fim: o maior entre a média e máximo − limite). A luz que passou fica inteira
        // (menos o limite, que é do tamanho do ruído); onde nada passou fica a média, sem o preto subir
        if style == .trails {
            let nextTrail = trail.map { shifted.applyingFilter("CIMaximumCompositing", parameters: [kCIInputBackgroundImageKey: $0]) }
                ?? shifted
            let trailTarget = trailBuffers[current]
            renderContext.render(nextTrail.cropped(to: bounds), to: trailTarget, bounds: bounds, colorSpace: Developer.linearP3)
            trail = CIImage(cvPixelBuffer: trailTarget, options: [.colorSpace: Developer.linearP3])
        }
        let next: CIImage
        if let sum {
            next = Developer.sumKernel?.apply(extent: bounds, arguments: [sum, shifted]) ?? sum
        } else {
            next = shifted
        }
        // Calcula agora num dos dois buffers, alternando, para não acumular uma cadeia de filtros
        var target = sumBuffers[current]
        renderContext.render(next, to: target, bounds: bounds, colorSpace: Developer.linearP3)
        // 1º quadro: conferido no buffer de 32 bits (se o formato não fosse aceito, a soma sairia preta): senão, meia precisão
        if count == 0, renderContext === LongExposure.floatContext, !matches(next, buffer: target) {
            dlog("Exposição longa: soma em 32 bits não conferiu; meia precisão")
            let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any],
                                               kCVPixelBufferMetalCompatibilityKey: true]
            var half: [CVPixelBuffer] = []
            for _ in 0..<2 {
                var buffer: CVPixelBuffer?
                if CVPixelBufferCreate(nil, Int(extent.width), Int(extent.height), kCVPixelFormatType_64RGBAHalf,
                                       attributes as CFDictionary, &buffer) == kCVReturnSuccess, let buffer { half.append(buffer) }
            }
            guard half.count == 2 else {
                stop()
                return
            }
            sumBuffers = half
            renderContext = Developer.context
            target = sumBuffers[current]
            renderContext.render(next, to: target, bounds: bounds, colorSpace: Developer.linearP3)
        }
        current = 1 - current
        sum = CIImage(cvPixelBuffer: target, options: [.colorSpace: Developer.linearP3])
        count += 1
        if CFAbsoluteTimeGetCurrent() >= endTime { stop() }
    }

    /// O quadro saiu mesmo no buffer de 32 bits? Média do verde num quadrado de 16 px no meio, lida do buffer, contra a do
    /// quadro calculada à parte
    private func matches(_ frame: CIImage, buffer: CVPixelBuffer) -> Bool {
        let w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer)
        guard w >= 32, h >= 32 else { return true }
        let block = CGRect(x: w / 2 - 8, y: h / 2 - 8, width: 16, height: 16)
        let average = frame.cropped(to: block).applyingFilter("CIAreaAverage", parameters: [kCIInputExtentKey: CIVector(cgRect: block)])
        let one = average.transformed(by: CGAffineTransform(translationX: -average.extent.minX, y: -average.extent.minY))
        var expected = [Float](repeating: 0, count: 4)
        Developer.context.render(one, toBitmap: &expected, rowBytes: 16, bounds: CGRect(x: 0, y: 0, width: 1, height: 1),
                                 format: .RGBAf, colorSpace: Developer.linearP3)
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
        guard let base = CVPixelBufferGetBaseAddress(buffer) else { return false }
        let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
        var total: Float = 0
        for row in (h / 2 - 8)..<(h / 2 + 8) {
            let line = (base + row * rowBytes).assumingMemoryBound(to: Float.self)
            for col in (w / 2 - 8)..<(w / 2 + 8) { total += line[col * 4 + 1] }
        }
        let got = total / 256, want = expected[1]
        guard got.isFinite, want.isFinite else { return false }
        return abs(got - want) <= max(0.02, 0.1 * abs(want))
    }

    /// Desloca o quadro para cair em cima do primeiro, pela mesma busca da NOITE (pedaço do centro em dois níveis, com
    /// fração de pixel). O Vision errava com a mão de verdade (andou 5 px, disse 28)
    private func align(_ image: CIImage) -> CIImage {
        let small = image.transformed(by: CGAffineTransform(scaleX: alignScale, y: alignScale))
        guard let referenceSmall else {
            // Guarda o primeiro quadro (cópia: o buffer da câmera volta para ela)
            if let cg = Developer.context.createCGImage(small, from: small.extent) { referenceSmall = CIImage(cgImage: cg) }
            return image
        }
        guard let shift = Developer.coarseShift(ref: referenceSmall, img: small, scale: alignScale) else { return image }
        let tx = shift.x, ty = shift.y
        // Pulo grande demais é erro do alinhamento: usa o quadro como veio
        guard abs(tx) < extent.width * 0.12, abs(ty) < extent.height * 0.12 else { return image }
        maxShift = CGSize(width: max(maxShift.width, abs(tx)), height: max(maxShift.height, abs(ty)))
        return image.clampedToExtent().transformed(by: CGAffineTransform(translationX: tx, y: ty))
            .cropped(to: CGRect(origin: .zero, size: extent.size))
    }

    func stop() {
        guard isRunning else { return }
        isRunning = false
        var result: CIImage?
        if let sum, count > 0 {
            let k = CGFloat(1) / CGFloat(count)
            let mean = sum.applyingFilter("CIColorMatrix", parameters: [
                "inputRVector": CIVector(x: k, y: 0, z: 0, w: 0),
                "inputGVector": CIVector(x: 0, y: k, z: 0, w: 0),
                "inputBVector": CIVector(x: 0, y: 0, z: k, w: 0),
                "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1),
            ])
            // Rastros: o maior entre a média (preto no lugar onde nada passou) e o máximo menos o quanto o ruído sozinho subiria
            if style == .trails, let trail {
                let t = CGFloat(trailThreshold)
                let lowered = trail.applyingFilter("CIColorMatrix", parameters: [
                    "inputBiasVector": CIVector(x: -t, y: -t, z: -t, w: 0),
                ])
                result = lowered.applyingFilter("CIMaximumCompositing", parameters: [kCIInputBackgroundImageKey: mean])
                    .cropped(to: mean.extent)
            } else {
                result = mean
            }
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
                renderContext.render(image, to: out, bounds: CGRect(origin: .zero, size: size), colorSpace: Developer.linearP3)
                result = CIImage(cvPixelBuffer: out, options: [.colorSpace: Developer.linearP3])
            }
        }
        sumBuffers = []
        trailBuffers = []
        sum = nil
        trail = nil
        let done = finished
        finished = nil
        done?(result, count)
    }

    private func makeBuffers() -> Bool {
        let attributes: [CFString: Any] = [kCVPixelBufferIOSurfacePropertiesKey: [:] as [CFString: Any],
                                           kCVPixelBufferMetalCompatibilityKey: true]
        func make(_ format: OSType, _ n: Int) -> [CVPixelBuffer]? {
            var list: [CVPixelBuffer] = []
            for _ in 0..<n {
                var buffer: CVPixelBuffer?
                guard CVPixelBufferCreate(nil, Int(extent.width), Int(extent.height), format,
                                          attributes as CFDictionary, &buffer) == kCVReturnSuccess, let buffer else { return nil }
                list.append(buffer)
            }
            return list
        }
        // Soma em 32 bits; sem memória para isso, meia precisão como antes (e o contexto de sempre)
        if let float = make(kCVPixelFormatType_128RGBAFloat, 2) {
            sumBuffers = float
            renderContext = LongExposure.floatContext
        } else if let half = make(kCVPixelFormatType_64RGBAHalf, 2) {
            sumBuffers = half
            renderContext = Developer.context
            dlog("Exposição longa: soma em meia precisão (sem memória para 32 bits)")
        } else {
            return false
        }
        if style == .trails {
            guard let half = make(kCVPixelFormatType_64RGBAHalf, 2) else { return false }
            trailBuffers = half
        } else {
            trailBuffers = []
        }
        current = 0
        return true
    }
}
