import CoreImage
import ImageIO
import CoreMotion
import UIKit
import Vision

/// Panorama: enquanto o iPhone gira, guarda um quadro de vídeo em resolução cheia a cada pedaço do giro.
/// O giroscópio diz quanto girou; no fim, o Revela projeta tudo num cilindro, alinha e emenda.
final class PanoramaCapture {
    struct Frame {
        let data: Data
        /// Giro desde o primeiro quadro, em radianos (positivo = para a direita).
        let yaw: Double
    }

    /// Até onde vai antes de terminar sozinho (~240°).
    static let maxSweep = 4.2
    /// O que a barra de progresso considera "completo" (180°).
    static let fullSweep = Double.pi

    private(set) var isRunning = false
    private let motion = CMMotionManager()
    private let lock = NSLock()
    private let context = CIContext()
    private let encodeQueue = DispatchQueue(label: "revela.panorama", qos: .userInitiated)
    private let encodeGroup = DispatchGroup()

    private var yaw = 0.0
    private var startElevation: Double?
    private var elevation = 0.0
    private var speed = 0.0
    private var lastTimestamp: TimeInterval?
    private var nextYaw = 0.0
    private var step = 0.4
    private var frames: [Frame] = []
    private var lastReport = 0.0
    private var finishing = false

    /// Progresso (0…1 de 180°) e um aviso ("Mais devagar", "Mantenha na linha"), no main.
    var onProgress: ((Double, String?) -> Void)?
    /// Chegou no limite do giro.
    var onLimit: (() -> Void)?

    /// Cada panorama tem um número: um fim atrasado de um panorama antigo não mexe no novo.
    private var run = 0
    /// Os primeiros quadros depois de ligar ainda podem vir no tamanho do visor: são pulados.
    private var warmup = 0
    private var frameSize: CGSize?
    /// Limite de quadros (na tele, cada um cobre pouco do giro e a memória acabaria).
    static let maxFrames = 22

    func start(step: Double) {
        lock.lock()
        run += 1
        warmup = 8
        frameSize = nil
        frames = []
        takenCount = 0
        yaw = 0
        nextYaw = 0
        startElevation = nil
        lastTimestamp = nil
        finishing = false
        self.step = step
        isRunning = true
        lock.unlock()
        motion.deviceMotionUpdateInterval = 1 / 60
        motion.startDeviceMotionUpdates(to: OperationQueue()) { [weak self] data, _ in
            guard let self, let data else { return }
            self.update(with: data)
        }
        dlog(String(format: "Panorama: começou (um quadro a cada %.0f°)", step * 180 / .pi))
    }

    private func update(with data: CMDeviceMotion) {
        let g = data.gravity
        let w = data.rotationRate
        // Giro em volta do eixo vertical (a gravidade): para a direita dá positivo
        let rate = w.x * g.x + w.y * g.y + w.z * g.z
        lock.lock()
        if let last = lastTimestamp { yaw += rate * (data.timestamp - last) }
        lastTimestamp = data.timestamp
        // Para onde a câmera aponta, para cima ou para baixo (a de trás olha para −z)
        elevation = asin(max(-1, min(1, g.z)))
        if startElevation == nil { startElevation = elevation }
        speed = abs(rate)
        let progress = min(1, abs(yaw) / Self.fullSweep)
        let drift = abs(elevation - (startElevation ?? elevation))
        let reached = abs(yaw) >= Self.maxSweep
        let now = data.timestamp
        let report = now - lastReport > 1.0 / 15
        if report { lastReport = now }
        lock.unlock()
        if report {
            // O quadro só é guardado abaixo de ~0,4 rad/s (logo abaixo): o aviso acompanha
            let warning: String? = speed > 0.4 ? "Mais devagar" : (drift > 0.08 ? "Mantenha na linha" : nil)
            DispatchQueue.main.async { self.onProgress?(progress, warning) }
        }
        if reached { DispatchQueue.main.async { self.onLimit?() } }
    }

    /// Fila de vídeo: guarda o quadro se o giro passou do próximo ponto.
    func offer(_ image: CIImage) {
        lock.lock()
        guard isRunning, !finishing else { lock.unlock(); return }
        if warmup > 0 {
            warmup -= 1
            lock.unlock()
            return
        }
        // Todos os quadros do mesmo tamanho (se um veio diferente, a câmera ainda estava trocando)
        if let frameSize, frameSize != image.extent.size {
            lock.unlock()
            return
        }
        frameSize = image.extent.size
        if takenCount >= Self.maxFrames {
            lock.unlock()
            DispatchQueue.main.async { self.onLimit?() }
            return
        }
        let current = yaw
        let first = takenCount == 0
        // Rápido demais o quadro sai tremido: espera a mão desacelerar. Com o obturador até 1/250 s, 0,4 rad/s borra ~3 px
        // (antes aceitava até 1,4 rad/s com 1/30–1/60 s: 20–60 px). Se a mão não desacelera e a parte repetida já está
        // acabando (passou meio passo do ponto), aceita até 0,8 rad/s para não abrir buraco no panorama
        let late = abs(current) >= nextYaw + step * 0.5
        // Acima de 0,8 rad/s nenhum quadro era guardado e o panorama saía com um buraco (transparente/preto). O passo é 0,42
        // do campo de visão: 0,9 passo depois do ponto só ~20% do quadro ainda repete o anterior (o encaixe pede 15%). Aí
        // guarda de qualquer jeito: tremido é melhor que buraco
        let lastChance = abs(current) >= nextYaw + step * 0.9
        let take = first || (abs(current) >= nextYaw && (speed < 0.4 || (late && speed < 0.8) || lastChance))
        if take {
            nextYaw = (first ? 0 : abs(current)) + step
            takenCount += 1
        }
        lock.unlock()
        guard take else { return }
        // Copia já (o buffer da câmera volta para ela), comprime em segundo plano
        let scale = min(1, 3000 / max(image.extent.width, image.extent.height))
        let small = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        guard let cg = context.createCGImage(small, from: small.extent) else { return }
        encodeGroup.enter()
        encodeQueue.async {
            defer { self.encodeGroup.leave() }
            let data = self.context.heifRepresentation(of: CIImage(cgImage: cg), format: .RGBA8,
                                                        colorSpace: CGColorSpace(name: CGColorSpace.displayP3)!, options: [:])
            guard let data else { return }
            self.lock.lock()
            self.frames.append(Frame(data: data, yaw: current))
            self.lock.unlock()
        }
    }

    private var takenCount = 0

    func finish(completion: @escaping ([Frame]) -> Void) {
        lock.lock()
        finishing = true
        let token = run
        lock.unlock()
        motion.stopDeviceMotionUpdates()
        encodeGroup.notify(queue: encodeQueue) {
            self.lock.lock()
            guard token == self.run else {
                self.lock.unlock()
                return completion([])
            }
            let result = self.frames.sorted { $0.yaw < $1.yaw }
            self.frames = []
            self.takenCount = 0
            self.isRunning = false
            self.lock.unlock()
            dlog(String(format: "Panorama: %d quadros, giro de %.0f°", result.count,
                        ((result.last?.yaw ?? 0) - (result.first?.yaw ?? 0)) * 180 / .pi))
            completion(result)
        }
    }
}

extension Developer {
    /// Emenda os quadros do panorama: cilindro, alinhamento fino pelo Vision, mistura suave nas emendas, look.
    /// `fov`: ângulo de visão horizontal do quadro em pé (radianos).
    static func panorama(_ frames: [PanoramaCapture.Frame], fov: Double, options: DevelopOptions) -> Output? {
        let t0 = CFAbsoluteTimeGetCurrent()
        // Abre cada quadro uma vez só, na memória (8 bits): a emenda lê cada um várias vezes
        let images: [CIImage] = frames.compactMap { frame in
            guard let source = CGImageSourceCreateWithData(frame.data as CFData, nil),
                  let cg = CGImageSourceCreateImageAtIndex(source, 0, [kCGImageSourceShouldCacheImmediately: true] as CFDictionary)
            else { return nil }
            return CIImage(cgImage: cg)
        }
        guard images.count == frames.count, images.count >= 2, let first = images.first,
              let cylinderKernel else { return nil }
        let W = first.extent.width, H = first.extent.height
        let f = (W / 2) / CGFloat(tan(fov / 2))
        // Sem parte repetida entre dois quadros seguidos (giro rápido demais, quadro perdido) ficava um buraco transparente
        // no meio: o panorama vai até o último quadro emendado sem falha
        var continuous = 1
        while continuous < frames.count, abs(f * CGFloat(frames[continuous].yaw - frames[continuous - 1].yaw)) < W {
            continuous += 1
        }
        if continuous < frames.count {
            dlog("⚠️ Panorama: quadros \(continuous) e \(continuous + 1) sem parte repetida: fica até o quadro \(continuous) de \(frames.count)")
        }
        let center = CIVector(x: W / 2, y: H / 2)
        // Daqui em diante tudo conta por `warped` (só os quadros contínuos)
        let warped: [CIImage] = images.prefix(continuous).map { image in
            let img = image.transformed(by: CGAffineTransform(translationX: -image.extent.minX, y: -image.extent.minY))
            return cylinderKernel.apply(extent: CGRect(x: 0, y: 0, width: W, height: H),
                                        roiCallback: { _, _ in img.extent },
                                        image: img, arguments: [Float(f), center]) ?? img
        }

        // Posição de cada quadro: o giroscópio dá o grosso, o Vision acerta o resto na parte que se repete
        var positions = [CGPoint.zero]
        for i in 1..<warped.count {
            let d = f * CGFloat(frames[i].yaw - frames[i - 1].yaw)
            var p = CGPoint(x: positions[i - 1].x + d, y: positions[i - 1].y)
            let overlap = W - abs(d)
            if overlap > W * 0.15 {
                let prevRect = d >= 0 ? CGRect(x: d, y: 0, width: overlap, height: H) : CGRect(x: 0, y: 0, width: overlap, height: H)
                let curRect = d >= 0 ? CGRect(x: 0, y: 0, width: overlap, height: H) : CGRect(x: -d, y: 0, width: overlap, height: H)
                let s: CGFloat = 0.25
                func piece(_ image: CIImage, _ rect: CGRect) -> CIImage {
                    image.cropped(to: rect)
                        .transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))
                        .transformed(by: CGAffineTransform(scaleX: s, y: s))
                }
                let request = VNTranslationalImageRegistrationRequest(targetedCIImage: piece(warped[i], curRect), options: [:])
                let handler = VNImageRequestHandler(ciImage: piece(warped[i - 1], prevRect), options: [:])
                if (try? handler.perform([request])) != nil,
                   let observation = request.results?.first as? VNImageTranslationAlignmentObservation {
                    let tx = observation.alignmentTransform.tx / s, ty = observation.alignmentTransform.ty / s
                    if abs(tx) < overlap * 0.25, abs(ty) < H * 0.08 {
                        p.x += tx
                        p.y += ty
                    } else {
                        dlog(String(format: "Panorama: emenda %d com ajuste exagerado (%.0f, %.0f); só giroscópio", i, tx, ty))
                    }
                }
            }
            positions.append(p)
        }

        // Emenda: cada quadro entra por cima do anterior com uma transição suave no meio da parte repetida
        var canvas = warped[0]
        for i in 1..<warped.count {
            let image = warped[i].transformed(by: CGAffineTransform(translationX: positions[i].x, y: positions[i].y))
            let a = positions[i - 1].x, b = positions[i].x
            let rightward = b >= a
            let overlapStart = rightward ? b : a
            let overlapEnd = rightward ? a + W : b + W
            let width = max(overlapEnd - overlapStart, 1)
            // Emenda na coluna em que os dois quadros mais concordam (gente andando, paralaxe de perto: a emenda fixa no meio
            // cortava no meio deles e aparecia duplicado), com transição curta em volta dela (antes 30–70% fixo)
            let previous = warped[i - 1].transformed(by: CGAffineTransform(translationX: positions[i - 1].x, y: positions[i - 1].y))
            let yLow = max(positions[i - 1].y, positions[i].y), yHigh = min(positions[i - 1].y, positions[i].y) + H
            let seam = seamColumn(previous, image, overlap: CGRect(x: overlapStart, y: yLow, width: width, height: yHigh - yLow))
                ?? overlapStart + width * 0.5
            let p0 = seam - width * 0.1, p1 = seam + width * 0.1
            let ramp = CIFilter(name: "CILinearGradient", parameters: [
                "inputPoint0": CIVector(x: p0, y: 0),
                "inputPoint1": CIVector(x: p1, y: 0),
                "inputColor0": CIColor(red: rightward ? 0 : 1, green: rightward ? 0 : 1, blue: rightward ? 0 : 1),
                "inputColor1": CIColor(red: rightward ? 1 : 0, green: rightward ? 1 : 0, blue: rightward ? 1 : 0),
            ])?.outputImage?.cropped(to: image.extent) ?? CIImage(color: .white).cropped(to: image.extent)
            let faded = image.applyingFilter("CIBlendWithMask", parameters: [
                kCIInputBackgroundImageKey: CIImage.empty(),
                kCIInputMaskImageKey: ramp,
            ])
            canvas = faded.composited(over: canvas)
        }

        // Corta as bordas tortas do cilindro e o sobe-e-desce da mão
        let ys = positions.map(\.y)
        let curve = H / 2 * (1 - CGFloat(cos(fov / 2)))
        let top = (ys.min() ?? 0) + H - curve
        let bottom = (ys.max() ?? 0) + curve
        // O cilindro não preenche a largura toda do quadro: tira a faixa vazia dos dois lados
        let empty = max(0, W / 2 - f * CGFloat(fov) / 2) + 2
        let left = (positions.map(\.x).min() ?? 0) + empty
        let right = (positions.map(\.x).max() ?? 0) + W - empty
        let rect = CGRect(x: left, y: bottom, width: right - left, height: max(top - bottom, H * 0.5)).integral
        let stitched = canvas.cropped(to: rect).transformed(by: CGAffineTransform(translationX: -rect.minX, y: -rect.minY))

        var opts = options
        opts.zoom = 1
        opts.originalAspect = true
        let output = developVideoImage(stitched, options: opts)
        dlog(String(format: "Panorama emendado: %d quadros → %.0f×%.0f em %@", warped.count, rect.width, rect.height,
                    Diagnostics.ms(since: t0)))
        return output
    }

    /// Coluna da emenda dentro da parte repetida (coordenadas do panorama): a de menor diferença de brilho entre os dois
    /// quadros, numa versão de ~96 px de largura, entre 20% e 80% da parte repetida. nil se a parte repetida é pequena
    private static func seamColumn(_ a: CIImage, _ b: CIImage, overlap: CGRect) -> CGFloat? {
        guard overlap.width >= 16, overlap.height >= 16 else { return nil }
        let k = min(1, 96 / overlap.width)
        let w = Int((overlap.width * k).rounded(.down)), h = Int((overlap.height * k).rounded(.down))
        guard w >= 8, h >= 8 else { return nil }
        func small(_ image: CIImage) -> [Float] {
            let reduced = image.cropped(to: overlap)
                .transformed(by: CGAffineTransform(translationX: -overlap.minX, y: -overlap.minY))
                .applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: k, kCIInputAspectRatioKey: 1])
            var pixels = [Float](repeating: 0, count: w * h * 4)
            context.render(reduced, toBitmap: &pixels, rowBytes: w * 16, bounds: CGRect(x: 0, y: 0, width: w, height: h),
                           format: .RGBAf, colorSpace: nil)
            return pixels
        }
        let pa = small(a), pb = small(b)
        var cost = [Float](repeating: 0, count: w)
        for y in 0..<h {
            for x in 0..<w {
                let o = (y * w + x) * 4
                let la: Float = 0.2126 * pa[o] + 0.7152 * pa[o + 1] + 0.0722 * pa[o + 2]
                let lb: Float = 0.2126 * pb[o] + 0.7152 * pb[o + 1] + 0.0722 * pb[o + 2]
                let d = abs(la - lb)
                if d.isFinite { cost[x] += d }
            }
        }
        let lo = max(1, w / 5), hi = min(w - 2, w * 4 / 5)
        guard hi > lo else { return nil }
        var best = lo
        var bestCost = Float.greatestFiniteMagnitude
        for x in lo...hi {
            let c = cost[x - 1] + cost[x] + cost[x + 1]
            if c < bestCost {
                bestCost = c
                best = x
            }
        }
        return overlap.minX + (CGFloat(best) + 0.5) / k
    }
}
