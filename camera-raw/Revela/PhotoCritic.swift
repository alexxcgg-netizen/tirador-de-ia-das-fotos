import CoreImage
import Foundation
import ImageIO
import Photos
import UIKit

/// O Claude (Opus 5.5) olha as últimas fotos nos mínimos detalhes e escreve o que a revelação precisa melhorar.
/// A análise entra no relatório. A chave da API fica no Keychain do iPhone (nunca dentro do .ipa).
@MainActor
final class PhotoCritic: ObservableObject {
    static let shared = PhotoCritic()

    private static let keyName = "anthropicKey"
    private static let model = "claude-opus-5-5"

    @Published private(set) var hasKey = Keychain.get(PhotoCritic.keyName) != nil
    @Published private(set) var status = ""
    @Published private(set) var running = false

    private var key: String? { Keychain.get(Self.keyName) }

    nonisolated static var analysisURL: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("analise-claude.md")
    }

    /// A última análise salva (vai no relatório).
    nonisolated static var lastAnalysis: String? { try? String(contentsOf: analysisURL, encoding: .utf8) }

    // MARK: - Chave

    /// Testa a chave com um pedido minúsculo; se der certo, guarda no Keychain.
    func connect(key raw: String) async -> Bool {
        let key = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !key.isEmpty else { return false }
        status = "Testando a chave…"
        let body: [String: Any] = [
            "model": Self.model, "max_tokens": 16,
            "output_config": ["effort": "low"],
            "messages": [["role": "user", "content": "Responda só: OK"]],
        ]
        let (code, json) = await send(body, key: key, timeout: 60)
        switch code {
        case 200:
            guard Keychain.set(Self.keyName, key) else {
                status = "A chave funciona, mas o iPhone não deixou guardar no Keychain. Tente de novo."
                return false
            }
            hasKey = true
            status = "Chave do Claude conectada"
            dlog("Claude API: chave conectada")
            return true
        case 401: status = "Chave inválida."
        case 403: status = "A chave não tem permissão."
        case 0: status = "Sem internet agora."
        default: status = "A API respondeu \(code): \(Self.errorMessage(json))"
        }
        return false
    }

    func disconnect() {
        Keychain.delete(Self.keyName)
        hasKey = false
        status = "Chave removida"
    }

    // MARK: - Análise

    /// Manda as últimas `count` fotos (inteira em alta resolução + recorte 100% do centro) e guarda a análise.
    @discardableResult
    func analyzeRecent(count: Int = 6) async -> String? {
        guard let key, !running else { return nil }
        running = true
        // Se for para o fundo no meio, o iOS dá um tempinho (o pedido leva minutos: o certo é deixar o app aberto)
        BackgroundWork.shared.begin("analise")
        defer {
            running = false
            BackgroundWork.shared.end("analise")
        }
        status = "Pedindo acesso às fotos…"
        let auth = await withCheckedContinuation { cont in
            PHPhotoLibrary.requestAuthorization(for: .readWrite) { cont.resume(returning: $0) }
        }
        guard auth == .authorized || auth == .limited else {
            status = "Sem acesso às fotos. Libere em Ajustes → Revela → Fotos."
            return nil
        }
        let entries = SourceStore.recentEntries(limit: count)
        guard !entries.isEmpty else {
            status = "Ainda não há fotos do Revela guardadas para analisar."
            return nil
        }
        var content: [[String: Any]] = []
        var used = 0
        for (i, entry) in entries.enumerated() {
            status = "Preparando foto \(i + 1) de \(entries.count)…"
            guard let prepared = await Self.prepare(entry: entry) else { continue }
            used += 1
            content.append(["type": "text", "text": "Foto \(used) — \(prepared.description)"])
            content.append(Self.imageBlock(prepared.full))
            content.append(["type": "text", "text": "Foto \(used) — recorte 100% (pixel por pixel) do centro"])
            content.append(Self.imageBlock(prepared.crop))
        }
        guard used > 0 else {
            status = "Não consegui abrir as fotos na galeria (foram apagadas?)."
            return nil
        }
        content.append(["type": "text", "text": Self.request(count: used)])
        var body: [String: Any] = [
            "model": Self.model,
            "max_tokens": 16000,
            "output_config": ["effort": "high"],
            "fallbacks": "default",
            "system": Self.systemPrompt,
            "messages": [["role": "user", "content": content]],
        ]
        status = "O Claude está olhando \(used) foto(s) nos mínimos detalhes… (leva 1 a 3 min; deixe o app aberto)"
        let t0 = CFAbsoluteTimeGetCurrent()
        var (code, json) = await send(body, key: key, timeout: 600, beta: "server-side-fallback-2026-07-01")
        // O pedido cortado também é cobrado: entra na conta junto com o segundo
        var firstInput = 0, firstOutput = 0
        // Passou do limite de tamanho e veio cortada: pede de novo uma vez, com o dobro de espaço
        if code == 200, (json?["stop_reason"] as? String) == "max_tokens" {
            let firstUsage = json?["usage"] as? [String: Any]
            firstInput = firstUsage?["input_tokens"] as? Int ?? 0
            firstOutput = firstUsage?["output_tokens"] as? Int ?? 0
            dlog("Claude API: análise cortada no limite (16000 tokens); pedindo de novo com 32000")
            status = "A análise ficou longa e veio cortada; pedindo de novo com mais espaço… (deixe o app aberto)"
            body["max_tokens"] = 32000
            (code, json) = await send(body, key: key, timeout: 900, beta: "server-side-fallback-2026-07-01")
        }
        guard code == 200, let json else {
            status = code == 0 ? "Sem internet (ou demorou demais)." : "A API respondeu \(code): \(Self.errorMessage(json))"
            dlog("❌ Claude API: análise falhou (\(code))")
            return nil
        }
        if (json["stop_reason"] as? String) == "refusal" {
            status = "O Claude recusou analisar essas fotos."
            return nil
        }
        let blocks = json["content"] as? [[String: Any]] ?? []
        let text = blocks.filter { ($0["type"] as? String) == "text" }.compactMap { $0["text"] as? String }.joined(separator: "\n")
        guard !text.isEmpty else {
            status = "A resposta veio vazia."
            return nil
        }
        // Mesmo com o dobro de espaço veio cortada: guarda o que veio, avisando
        let truncated = (json["stop_reason"] as? String) == "max_tokens"
        let usage = json["usage"] as? [String: Any]
        let input = (usage?["input_tokens"] as? Int ?? 0) + firstInput
        let output = (usage?["output_tokens"] as? Int ?? 0) + firstOutput
        let dollars = Double(input) * 4 / 1_000_000 + Double(output) * 20 / 1_000_000
        let seconds = CFAbsoluteTimeGetCurrent() - t0
        let requests = firstInput + firstOutput > 0 ? " (2 pedidos)" : ""
        let header = "_\(used) foto(s) · \(Self.model) · \(Date().formatted(date: .abbreviated, time: .shortened)) · " +
            String(format: "%d tokens de entrada, %d de saída%@ · ~US$ %.2f · %.0f s_\n\n", input, output, requests, dollars, seconds)
        let full = header + text + (truncated ? "\n\n_(a análise veio cortada no fim: passou do limite de tamanho da resposta)_" : "")
        try? full.write(to: Self.analysisURL, atomically: true, encoding: .utf8)
        dlog(String(format: "Claude API: análise de %d fotos pronta (%.0f s, ~US$ %.2f)%@", used, seconds, dollars,
                    truncated ? " · cortada no limite" : ""))
        status = "Análise pronta (~US$ \(ptNumber(dollars, digits: 2))). Ela vai junto no relatório."
            + (truncated ? " Veio cortada no fim (longa demais)." : "")
        return full
    }

    // MARK: - Fotos

    private struct Prepared {
        let full: Data
        let crop: Data
        let description: String
    }

    /// A foto revelada da galeria: inteira (até 2048 px) e o centro em 100%, em JPEG, mais o que se sabe dela.
    private static func prepare(entry: SourceStore.Entry) async -> Prepared? {
        guard let asset = PHAsset.fetchAssets(withLocalIdentifiers: [entry.assetID], options: nil).firstObject else { return nil }
        let options = PHImageRequestOptions()
        options.isNetworkAccessAllowed = true
        options.deliveryMode = .highQualityFormat
        options.version = .current
        let data: Data? = await withCheckedContinuation { cont in
            PHImageManager.default().requestImageDataAndOrientation(for: asset, options: options) { data, _, _, _ in
                cont.resume(returning: data)
            }
        }
        guard let data else { return nil }
        return await Task.detached(priority: .userInitiated) { () -> Prepared? in
            guard let image = CIImage(data: data, options: [.applyOrientationProperty: true]) else { return nil }
            let e = image.extent
            let s = min(1, 2048 / max(e.width, e.height))
            let small = image.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: s, kCIInputAspectRatioKey: 1])
            let side = min(1024, min(e.width, e.height))
            let crop = image.cropped(to: CGRect(x: e.midX - side / 2, y: e.midY - side / 2, width: side, height: side).integral)
            let sRGB = CGColorSpace(name: CGColorSpace.sRGB)!
            let quality = [kCGImageDestinationLossyCompressionQuality as CIImageRepresentationOption: 0.88]
            guard let fullJPEG = Developer.context.jpegRepresentation(of: small, colorSpace: sRGB, options: quality),
                  let cropJPEG = Developer.context.jpegRepresentation(of: crop, colorSpace: sRGB, options: quality) else { return nil }
            let exif = image.properties[kCGImagePropertyExifDictionary as String] as? [String: Any]
            let iso = (exif?[kCGImagePropertyExifISOSpeedRatings as String] as? [NSNumber])?.first.map { "ISO \($0.intValue)" } ?? "ISO ?"
            let time = (exif?[kCGImagePropertyExifExposureTime as String] as? Double).map { $0 >= 0.5 ? String(format: "%.1f s", $0) : "1/\(Int((1 / $0).rounded())) s" } ?? "tempo ?"
            let lens = exif?[kCGImagePropertyExifLensModel as String] as? String ?? ""
            let desc = "modo \(entry.mode), \(Int(e.width))×\(Int(e.height)) px, \(iso), \(time), " +
                (entry.isRaw ? "revelada do RAW" : "versão já revelada (pilha/HDR)") +
                (entry.zoom > 1.01 ? String(format: ", zoom %.1f×", entry.zoom) : "") +
                (lens.isEmpty ? "" : ", lente \(lens)") +
                ", tirada em \(entry.date.formatted(date: .abbreviated, time: .shortened))"
            return Prepared(full: fullJPEG, crop: cropJPEG, description: desc)
        }.value
    }

    private static func imageBlock(_ jpeg: Data) -> [String: Any] {
        ["type": "image", "source": ["type": "base64", "media_type": "image/jpeg", "data": jpeg.base64EncodedString()]]
    }

    // MARK: - Pedido

    private static let systemPrompt = """
    Você é um engenheiro de qualidade de imagem e diretor de fotografia avaliando fotos de um app de câmera RAW para \
    iPhone (o Revela, num iPhone 17 Pro Max). O app tem a própria revelação: RAW linear (CIRAWFilter sem o processamento \
    da Apple), tons locais (luz de fundo borrada puxada para a média; sombras sobem mais que as luzes descem), curva \
    fílmica ACES com saturação e filmes (matriz de cor, CDL, tons de sombra e luz, grão em três tamanhos, halo, vinheta), \
    nitidez fina leve, redução de ruído (cor borrada + ondaletas no brilho). Modos com várias fotos: NOITE (alinhamento \
    em fração de pixel, junção em duas faixas como o HDR+, foto curta −3 EV para as luzes, clareamento automático até \
    3 paradas, ponto de preto medido, na mão fotos de 1/15 a 1/8 s e o borrão que sobra desfeito com Huber-TV, estrela \
    nas luzes imitando o iPhone 18 Pro), FOTO 3× (com pouca luz, várias fotos do mesmo instante alinhadas e juntadas), \
    HDR (−2/0/+2), SUPER ZOOM (24 fotos na mão) e SUPER RES (alinhamento por região e todas as fotos nítidas resolvidas \
    juntas num MAP: cada foto é a cena ampliada 2× borrada e deslocada, com regularização Huber-TV conjunta de brilho e \
    cor e anti-fantasma; o MAP já desfaz o borrão do sensor e da lente, sem desconvolução depois), RETRATO (profundidade \
    do LiDAR + máscaras, desfoque em camadas). O objetivo é ficar melhor que a câmera nativa do iPhone.

    Para cada foto você recebe a foto inteira e um recorte 100% do centro. Olhe nos mínimos detalhes. Para cada foto, \
    diga o que está bom e liste cada problema com: o quê, onde na foto, quão grave (leve/médio/forte) e qual parte da \
    revelação provavelmente causa e como ajustar (seja técnico e específico). Procure especialmente: exposição e \
    branco/preto, balanço de branco e cor de pele, saturação, halos dos tons locais, ruído (cor e brilho) e se a redução \
    de ruído virou pintura, nitidez/excesso de nitidez, artefatos de junção (fantasma, duplicação, bordas, faixas), \
    luzes estouradas ou cor errada em postes, estrela nas luzes (realismo), grão do filme, desfoque do retrato (bordas, \
    cabelo). No fim, uma lista "Prioridades" com as 5 mudanças que mais melhorariam as fotos. Escreva em português do \
    Brasil, em Markdown, direto ao ponto. Se a foto estiver ótima, diga.
    """

    private static func request(count: Int) -> String {
        "Analise as \(count) foto(s) acima, uma por uma, nos mínimos detalhes, e termine com as Prioridades."
    }

    private func send(_ body: [String: Any], key: String, timeout: TimeInterval, beta: String? = nil) async -> (Int, [String: Any]?) {
        guard let url = URL(string: "https://api.anthropic.com/v1/messages"),
              let data = try? JSONSerialization.data(withJSONObject: body) else { return (0, nil) }
        var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: timeout)
        request.httpMethod = "POST"
        request.httpBody = data
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(key, forHTTPHeaderField: "x-api-key")
        request.setValue("2026-10-21", forHTTPHeaderField: "anthropic-version")
        if let beta { request.setValue(beta, forHTTPHeaderField: "anthropic-beta") }
        do {
            let (responseData, response) = try await URLSession.shared.data(for: request)
            let code = (response as? HTTPURLResponse)?.statusCode ?? 0
            return (code, (try? JSONSerialization.jsonObject(with: responseData)) as? [String: Any])
        } catch {
            return (0, nil)
        }
    }

    private static func errorMessage(_ json: [String: Any]?) -> String {
        ((json?["error"] as? [String: Any])?["message"] as? String) ?? "erro"
    }
}
