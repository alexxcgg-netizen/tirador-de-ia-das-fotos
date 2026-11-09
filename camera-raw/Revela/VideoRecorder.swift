import AVFoundation
import CoreImage
import UIKit

/// Grava vídeo com o look já aplicado: cada quadro passa pela revelação e vai para um arquivo HEVC, com o som do microfone.
/// Todas as chamadas podem vir de qualquer fila; o trabalho roda numa fila própria.
final class VideoRecorder {
    /// Depois do toque de parar, quanto ainda se espera pelos quadros atrasados: a estabilização cinematográfica
    /// entrega o vídeo até ~1 s depois do som, e o fim do vídeo sumia com o som continuando
    static let drainSeconds = 1.5
    /// Depois do toque de parar, sem quadro nenhum por este tempo a câmera parou (interrupção, troca de modo): fecha já,
    /// em vez de esperar o resto do `drainSeconds` (o fim pelo relógio caía com o app no fundo, sem codificador)
    static let idleSeconds = 0.2
    /// Quadros seguidos de outro tamanho até desistir: a câmera mudou de formato de vez e o arquivo ficava parado sem aviso
    static let maxMismatchRun = 15
    /// Som guardado enquanto o arquivo não nasce (~21 ms cada: ~6 s), para o começo do vídeo não sair mudo
    private static let maxPendingAudio = 300

    private let queue = DispatchQueue(label: "revela.recorder", qos: .userInitiated)
    // Na fila do gravador
    private var writer: AVAssetWriter?
    private var videoInput: AVAssetWriterInput?
    private var audioInput: AVAssetWriterInput?
    private var adaptor: AVAssetWriterInputPixelBufferAdaptor?
    private var started = false
    private var frames = 0
    private var url: URL?
    private var failureReported = false
    /// Gravação armada (o arquivo só nasce no primeiro quadro, do tamanho dele).
    private var activeID: Int?
    private var fps = 30
    private var transform = CGAffineTransform.identity
    private var writerSize: CGSize?
    /// Tamanho do quadro anterior enquanto o arquivo não existe: ele nasce quando dois quadros seguidos concordam
    private var candidateSize: CGSize?
    private var mismatched = 0
    /// Quadros de outro tamanho seguidos (zera a cada quadro bom)
    private var mismatchRun = 0
    private var lastVideoTime: CMTime?
    /// Instante em que a gravação foi armada (relógio dos quadros): quadro e som de antes ficam de fora
    private var armedAt = CMTime.invalid
    /// Som que chegou antes do arquivo nascer (ou com o codificador sem fôlego), em ordem
    private var pendingAudio: [CMSampleBuffer] = []
    /// Quem pediu o fim, esperando os últimos quadros.
    private var stopCompletion: ((URL?, Int, Bool) -> Void)?
    // Com trava: lidos na fila da câmera a cada quadro
    private let lock = NSLock()
    private var recording = false
    /// Instante do toque de parar (relógio da câmera): quadros de antes ainda entram, som e quadros de depois não.
    private var stopTime = CMTime.invalid
    /// Maior gravação já parada: o começo atrasado dela (vem por outra fila) é ignorado em vez de gravar escondido
    private var stoppedID = 0
    /// Quadros esperando a revelação. Acima de 2 o quadro novo é descartado: antes cada um entrava numa fila sem fim
    /// segurando um buffer da câmera, e quando a revelação não acompanhava a câmera ficava sem buffers
    private var pending = 0
    private var dropped = 0
    /// Quadros que chegaram da câmera (só conta): depois do toque de parar, diz se ainda vem algum
    private var arrivals = 0
    private let colorSpace = CGColorSpace(name: CGColorSpace.itur_709) ?? CGColorSpaceCreateDeviceRGB()

    /// O arquivo falhou no meio (disco cheio, codificador): chamado uma vez por gravação, na fila principal, com o motivo.
    /// Definido uma vez antes da primeira gravação.
    var onFailure: ((String) -> Void)?

    /// Aceitando quadros (gravando, ou esperando os atrasados depois do toque de parar).
    var isRecording: Bool {
        lock.lock()
        defer { lock.unlock() }
        return recording
    }

    /// Arma a gravação `id`. O arquivo nasce no primeiro quadro, com o tamanho dele: no toque a câmera ainda podia estar
    /// trocando de formato (FOTO → VÍDEO 4K, 4K ↔ 1080p, lente) e o arquivo saía do tamanho errado, cortado ou com lixo.
    /// `transform` gira o vídeo na reprodução (iPhone deitado durante a gravação).
    func start(id: Int, fps: Int, transform: CGAffineTransform) {
        // No relógio dos quadros e do som da câmera (o do sistema, como no stop). Com a estabilização forte os quadros
        // chegam ~1 s atrasados: sem este corte o arquivo começava ~1 s antes do toque, e esse segundo saía mudo
        let armedAt = CMClockGetTime(CMClockGetHostTimeClock())
        queue.async {
            self.lock.lock()
            let stale = id <= self.stoppedID
            self.lock.unlock()
            guard !stale else {
                dlog("Vídeo: o começo da gravação \(id) chegou depois do fim dela, ignorado")
                return
            }
            // A anterior ainda esperando os quadros atrasados (ou largada aberta): fecha agora
            if self.activeID != nil { self.finish() }
            self.activeID = id
            self.fps = min(max(fps, 1), 240)
            self.transform = transform
            self.failureReported = false
            self.started = false
            self.frames = 0
            self.writerSize = nil
            self.candidateSize = nil
            self.mismatched = 0
            self.mismatchRun = 0
            self.lastVideoTime = nil
            self.armedAt = armedAt
            self.pendingAudio = []
            self.lock.lock()
            self.recording = true
            self.stopTime = .invalid
            self.dropped = 0
            self.lock.unlock()
            dlog("Vídeo: gravação \(id) armada a \(self.fps) fps (o arquivo nasce no primeiro quadro)")
        }
    }

    /// Na fila do gravador: cria o arquivo do tamanho do quadro.
    private func makeWriter(width: Int, height: Int) -> Bool {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("video-\(UUID().uuidString).mov")
        guard let writer = try? AVAssetWriter(outputURL: url, fileType: .mov) else {
            dlog("❌ Vídeo: não criou o arquivo")
            reportFailure("Não foi possível criar o arquivo do vídeo.")
            return false
        }
        // Fragmentos de 2 s: se a gravação falhar ou o app fechar no meio, o arquivo ainda abre até o último pedaço salvo
        writer.movieFragmentInterval = CMTime(seconds: 2, preferredTimescale: 600)
        // ~0,2 bit por pixel: o grão do filme é ruído de propósito e pede mais bits que um vídeo limpo
        // (4K30 ≈ 50 Mb/s, 1080p60 ≈ 25 Mb/s, 1080p30 ≈ 12 Mb/s)
        let bitRate = Int(Double(width * height * fps) * 0.2)
        let video = AVAssetWriterInput(mediaType: .video, outputSettings: [
            AVVideoCodecKey: AVVideoCodecType.hevc,
            AVVideoWidthKey: width,
            AVVideoHeightKey: height,
            AVVideoColorPropertiesKey: [
                AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
            ],
            AVVideoCompressionPropertiesKey: [
                AVVideoAverageBitRateKey: bitRate,
                AVVideoExpectedSourceFrameRateKey: fps,
            ],
        ])
        video.expectsMediaDataInRealTime = true
        video.transform = transform
        let audio = AVAssetWriterInput(mediaType: .audio, outputSettings: [
            AVFormatIDKey: kAudioFormatMPEG4AAC,
            AVNumberOfChannelsKey: 1,
            AVSampleRateKey: 48_000,
            AVEncoderBitRateKey: 128_000,
        ])
        audio.expectsMediaDataInRealTime = true
        guard writer.canAdd(video) else {
            dlog("❌ Vídeo: o codificador recusou \(width)×\(height)")
            reportFailure("O codificador recusou o vídeo \(width)×\(height).")
            return false
        }
        writer.add(video)
        if writer.canAdd(audio) { writer.add(audio) }
        // A revelação desenha direto nos buffers do próprio codificador (sem cópia no meio)
        adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: video, sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
            kCVPixelBufferWidthKey as String: width,
            kCVPixelBufferHeightKey as String: height,
            kCVPixelBufferIOSurfacePropertiesKey as String: [:] as [String: Any],
        ])
        self.writer = writer
        videoInput = video
        audioInput = writer.inputs.contains(audio) ? audio : nil
        self.url = url
        writerSize = CGSize(width: width, height: height)
        dlog("Vídeo: gravando \(width)×\(height) a \(fps) fps · \(bitRate / 1_000_000) Mb/s")
        return true
    }

    /// Um quadro já revelado (luz linear de tela, como sai do Developer.preview).
    func append(_ image: CIImage, at time: CMTime) {
        lock.lock()
        guard recording else {
            lock.unlock()
            return
        }
        arrivals &+= 1
        guard pending < 2 else {
            dropped += 1
            lock.unlock()
            return
        }
        pending += 1
        lock.unlock()
        queue.async {
            self.write(image, at: time)
            self.lock.lock()
            self.pending -= 1
            self.lock.unlock()
        }
    }

    /// Na fila do gravador.
    private func write(_ image: CIImage, at time: CMTime) {
        guard activeID != nil, isRecording else { return }
        lock.lock()
        let stopAt = stopTime
        lock.unlock()
        if stopAt.isValid, CMTimeCompare(time, stopAt) > 0 {
            // Primeiro quadro de depois do toque de parar: os atrasados da estabilização já entraram
            if stopCompletion != nil { finish() }
            return
        }
        if armedAt.isValid, CMTimeCompare(time, armedAt) < 0 {
            // Quadro de antes do toque. Passados 3 s e ainda só quadros "de antes", eles vêm em outro relógio: para de
            // cortar (melhor um começo adiantado que vídeo nenhum)
            guard (CMClockGetTime(CMClockGetHostTimeClock()) - armedAt).seconds > 3 else { return }
            dlog("⚠️ Vídeo: os quadros vêm em outro relógio; o começo não é cortado")
            armedAt = .invalid
        }
        // App no fundo: o iOS não deixa usar a GPU e o quadro desenhado saía preto ou com lixo. Fica de fora
        if ForegroundGate.shared.isBackground {
            lock.lock()
            dropped += 1
            lock.unlock()
            return
        }
        let extent = image.extent
        guard !extent.isInfinite, !extent.isEmpty else { return }
        let size = CGSize(width: extent.width.rounded(), height: extent.height.rounded())
        if writer == nil {
            // Dois quadros seguidos do mesmo tamanho: um quadro velho (de antes da troca de formato) não decide o arquivo
            guard candidateSize == size else {
                candidateSize = size
                return
            }
            guard makeWriter(width: Int(size.width), height: Int(size.height)), let writer else { return }
            guard writer.startWriting() else {
                dlog("❌ Vídeo: \(writer.error?.localizedDescription ?? "não começou")")
                reportFailure(Self.failureText(writer.error))
                return
            }
            writer.startSession(atSourceTime: time)
            started = true
            // O som que chegou enquanto o primeiro quadro não vinha entra agora (antes era descartado: começo mudo)
            pendingAudio.removeAll { CMTimeCompare(CMSampleBufferGetPresentationTimeStamp($0), time) < 0 }
            flushAudio()
        }
        guard let writer, let input = videoInput, let adaptor else { return }
        guard size == writerSize else {
            // A câmera trocou de formato no meio: desenhar no arquivo do tamanho antigo cortava o quadro ou deixava lixo
            if mismatched == 0 {
                let w = Int(writerSize?.width ?? 0), h = Int(writerSize?.height ?? 0)
                dlog("⚠️ Vídeo: quadro \(Int(size.width))×\(Int(size.height)) num arquivo \(w)×\(h): descartado")
            }
            mismatched += 1
            mismatchRun += 1
            // A câmera mudou de formato de vez: antes o arquivo ficava parado, sem aviso, até o toque de parar. Fecha com o
            // que já foi gravado (já parando: só fecha, sem aviso)
            if mismatchRun >= Self.maxMismatchRun {
                dlog("❌ Vídeo: \(mismatchRun) quadros seguidos de outro tamanho")
                if stopCompletion != nil { finish() } else { reportFailure("A câmera mudou o formato do vídeo no meio e a gravação parou.") }
            }
            return
        }
        mismatchRun = 0
        guard writer.status == .writing else {
            dlog("❌ Vídeo: o arquivo parou (\(writer.error?.localizedDescription ?? "?"))")
            reportFailure(Self.failureText(writer.error))
            return
        }
        guard input.isReadyForMoreMediaData, let pool = adaptor.pixelBufferPool else {
            lock.lock()
            dropped += 1
            lock.unlock()
            return
        }
        var buffer: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, pool, &buffer)
        guard let buffer else { return }
        let bounds = CGRect(x: 0, y: 0, width: CVPixelBufferGetWidth(buffer), height: CVPixelBufferGetHeight(buffer))
        let placed = image.transformed(by: CGAffineTransform(translationX: -extent.minX, y: -extent.minY))
        Developer.context.render(placed, to: buffer, bounds: bounds, colorSpace: colorSpace)
        if adaptor.append(buffer, withPresentationTime: time) {
            frames += 1
            lastVideoTime = time
        } else if writer.status == .failed {
            dlog("❌ Vídeo: o codificador falhou (\(writer.error?.localizedDescription ?? "?"))")
            reportFailure(Self.failureText(writer.error))
        }
    }

    func appendAudio(_ sampleBuffer: CMSampleBuffer) {
        guard isRecording else { return }
        queue.async {
            guard self.isRecording, self.activeID != nil else { return }
            let time = CMSampleBufferGetPresentationTimeStamp(sampleBuffer)
            self.lock.lock()
            let stopAt = self.stopTime
            self.lock.unlock()
            // Som de depois do toque de parar fica de fora (o vídeo atrasado ainda está chegando); o de antes de armar também
            if stopAt.isValid, CMTimeCompare(time, stopAt) > 0 { return }
            if self.armedAt.isValid, CMTimeCompare(time, self.armedAt) < 0 { return }
            if self.started, self.writer?.status != .writing || self.audioInput == nil { return }
            // Em ordem: o arquivo ainda não nasceu (o vídeo estabilizado chega ~1 s depois do som) ou o codificador está
            // sem fôlego. Passando do limite sai o mais velho (antes o som desse tempo era todo descartado)
            self.pendingAudio.append(sampleBuffer)
            if self.pendingAudio.count > Self.maxPendingAudio {
                self.pendingAudio.removeFirst(self.pendingAudio.count - Self.maxPendingAudio)
            }
            self.flushAudio()
        }
    }

    /// Na fila do gravador: o som guardado entra em ordem enquanto o codificador aceitar (o resto espera a próxima vez).
    private func flushAudio() {
        guard started, let writer, writer.status == .writing, let input = audioInput else { return }
        while let first = pendingAudio.first, input.isReadyForMoreMediaData {
            pendingAudio.removeFirst()
            guard input.append(first) else { break }
        }
    }

    /// Fecha o arquivo da gravação `id`. Os quadros de antes do toque que ainda estão chegando entram (por até
    /// `drainSeconds`); o som de depois do toque não. `partial`: a gravação falhou no meio e o arquivo vai até o
    /// último fragmento salvo. Pode chegar antes do `start` da mesma gravação: o começo é ignorado quando chegar.
    /// `drain` false (interrupção, falha): fecha já, sem esperar os atrasados. Sem quadro nenhum por `idleSeconds` também.
    func stop(id: Int, drain: Bool = true, completion: @escaping (_ url: URL?, _ frames: Int, _ partial: Bool) -> Void) {
        // Os quadros e o som da câmera vêm no relógio do sistema (o da sessão de captura)
        let now = CMClockGetTime(CMClockGetHostTimeClock())
        lock.lock()
        stoppedID = max(stoppedID, id)
        if recording, !stopTime.isValid { stopTime = now }
        lock.unlock()
        queue.async {
            guard self.activeID == id, self.stopCompletion == nil else {
                // Não chegou a começar (o fim veio antes do começo): nada a fechar
                dlog("Vídeo: fim da gravação \(id) sem gravação armada")
                completion(nil, 0, false)
                return
            }
            self.stopCompletion = completion
            // Interrupção, falha, app no fundo ou arquivo já parado por erro: fecha já. Senão espera os quadros
            // atrasados (também sem arquivo ainda: num toque curto os quadros do começo ainda estão chegando)
            let writing = self.writer.map { $0.status == .writing } ?? true
            guard drain, self.isRecording, writing, !ForegroundGate.shared.isBackground else { return self.finish() }
            self.waitForLateFrames(id: id, seen: self.arrivalCount, until: .now() + Self.drainSeconds)
        }
    }

    private var arrivalCount: Int {
        lock.lock()
        defer { lock.unlock() }
        return arrivals
    }

    /// Na fila do gravador: espera os quadros atrasados enquanto eles continuam chegando, até `deadline`.
    private func waitForLateFrames(id: Int, seen: Int, until deadline: DispatchTime) {
        queue.asyncAfter(deadline: .now() + Self.idleSeconds) {
            guard self.activeID == id, self.stopCompletion != nil else { return }
            let count = self.arrivalCount
            if count == seen {
                dlog("Vídeo: nenhum quadro em \(Self.idleSeconds) s depois do fim (a câmera parou): fechando já")
                self.finish()
            } else if DispatchTime.now() >= deadline || ForegroundGate.shared.isBackground {
                self.finish()
            } else {
                self.waitForLateFrames(id: id, seen: count, until: deadline)
            }
        }
    }

    /// Na fila do gravador: fecha o arquivo da gravação armada e avisa quem pediu o fim.
    private func finish() {
        let writer = self.writer, url = self.url, frames = self.frames, started = self.started
        let videoInput = self.videoInput, audioInput = self.audioInput, last = lastVideoTime, fps = self.fps
        let mismatched = self.mismatched
        // O som que ainda esperava o codificador entra antes de fechar
        flushAudio()
        pendingAudio = []
        let completion = stopCompletion
        stopCompletion = nil
        activeID = nil
        self.writer = nil
        self.videoInput = nil
        self.audioInput = nil
        adaptor = nil
        self.url = nil
        self.started = false
        lastVideoTime = nil
        writerSize = nil
        candidateSize = nil
        lock.lock()
        recording = false
        stopTime = .invalid
        let dropped = self.dropped
        lock.unlock()
        dlog("Vídeo: \(frames) quadros gravados\(dropped > 0 ? ", \(dropped) descartados (a revelação não acompanhou)" : "")"
             + (mismatched > 0 ? ", \(mismatched) de outro tamanho fora" : ""))
        guard let writer, started else {
            if let url { try? FileManager.default.removeItem(at: url) }
            completion?(nil, 0, false)
            return
        }
        guard writer.status == .writing else {
            // Falhou no meio: com os fragmentos de 2 s o arquivo costuma abrir até o último pedaço
            completion?(Self.hasData(url) ? url : nil, frames, true)
            return
        }
        videoInput?.markAsFinished()
        audioInput?.markAsFinished()
        // O arquivo acaba junto com o último quadro de vídeo: o som não passa do fim da imagem
        if let last { writer.endSession(atSourceTime: CMTimeAdd(last, CMTime(value: 1, timescale: CMTimeScale(fps)))) }
        writer.finishWriting {
            if writer.status == .completed {
                completion?(url, frames, false)
            } else {
                dlog("❌ Vídeo: não fechou o arquivo (\(writer.error?.localizedDescription ?? "?"))")
                completion?(Self.hasData(url) ? url : nil, frames, true)
            }
        }
    }

    /// Na fila do gravador: para de aceitar quadros e avisa o app (uma vez).
    private func reportFailure(_ text: String) {
        lock.lock()
        recording = false
        lock.unlock()
        // Já tinham pedido o fim (esperando os quadros atrasados): fecha agora com o que deu
        if stopCompletion != nil { finish() }
        guard !failureReported else { return }
        failureReported = true
        let callback = onFailure
        DispatchQueue.main.async { callback?(text) }
    }

    private static func failureText(_ error: Error?) -> String {
        let code = (error as NSError?)?.code
        if code == AVError.Code.diskFull.rawValue {
            return "Acabou o espaço do iPhone e a gravação parou."
        }
        return "A gravação parou por um erro (\(error?.localizedDescription ?? "desconhecido"))."
    }

    /// O arquivo existe e tem alguma coisa dentro (um pedaço de vídeo de verdade, não só o cabeçalho).
    static func hasData(_ url: URL?) -> Bool {
        guard let url, let size = (try? url.resourceValues(forKeys: [.fileSizeKey]))?.fileSize else { return false }
        return size > 100_000
    }
}

/// Tempo extra para terminar de salvar quando o app vai para o fundo no meio (ligação, botão de início).
/// Termine com `end()`, na fila principal.
final class BackgroundTask {
    private var id = UIBackgroundTaskIdentifier.invalid

    init(_ name: String) {
        id = UIApplication.shared.beginBackgroundTask(withName: name) { [weak self] in self?.end() }
    }

    func end() {
        guard id != .invalid else { return }
        UIApplication.shared.endBackgroundTask(id)
        id = .invalid
    }
}
