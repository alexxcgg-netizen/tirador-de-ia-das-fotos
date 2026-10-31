import Foundation
import Security
import UIKit

/// Chave do GitHub guardada no Keychain do iPhone (nunca vai dentro do .ipa).
enum Keychain {
    private static let service = "com.alexxcgg.revela"

    static func get(_ key: String) -> String? {
        let query: [CFString: Any] = [kSecClass: kSecClassGenericPassword, kSecAttrService: service,
                                      kSecAttrAccount: key, kSecReturnData: true, kSecMatchLimit: kSecMatchLimitOne]
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func set(_ key: String, _ value: String) {
        delete(key)
        let item: [CFString: Any] = [kSecClass: kSecClassGenericPassword, kSecAttrService: service, kSecAttrAccount: key,
                                     kSecValueData: Data(value.utf8), kSecAttrAccessible: kSecAttrAccessibleAfterFirstUnlock]
        SecItemAdd(item as CFDictionary, nil)
    }

    static func delete(_ key: String) {
        let query: [CFString: Any] = [kSecClass: kSecClassGenericPassword, kSecAttrService: service, kSecAttrAccount: key]
        SecItemDelete(query as CFDictionary)
    }
}

/// Ponte com o Claude pelo GitHub (ramo `revela-sync` do repositório do app):
/// o Claude manda filmes, ajustes e recados; o app manda relatórios e o estado. Confere ao abrir e a cada 15 s aberto.
@MainActor
final class ClaudeSync: ObservableObject {
    static let shared = ClaudeSync()

    private static let repo = "alexxcgg-netizen/tirador-de-ia-das-fotos"
    private static let branch = "revela-sync"
    private static let tokenKey = "githubToken"

    @Published private(set) var connected = Keychain.get(ClaudeSync.tokenKey) != nil
    @Published private(set) var status = ""
    @Published private(set) var sending = false

    weak var camera: CameraModel?
    private var etags: [String: String] = [:]
    private var shas: [String: String] = [:]
    private var timer: Timer?
    private var pulling = false
    private var lastStatePush = Date.distantPast
    private let defaults = UserDefaults.standard

    private var token: String? { Keychain.get(Self.tokenKey) }

    // MARK: - Conectar

    /// Testa a chave lendo o ramo; se der certo, guarda no Keychain e começa a conferir.
    func connect(token raw: String) async -> Bool {
        let token = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !token.isEmpty else { return false }
        status = "Testando a chave…"
        let (code, _, _) = await request("GET", path: "LEIA-ME.md", token: token)
        switch code {
        case 200:
            Keychain.set(Self.tokenKey, token)
            connected = true
            status = "Conectado"
            dlog("Claude: conectado pelo GitHub")
            start()
            return true
        case 401: status = "Chave inválida ou vencida."
        case 403, 404: status = "A chave não enxerga o repositório do Revela (confira o repositório escolhido e a permissão Contents)."
        case 0: status = "Sem internet agora."
        default: status = "O GitHub respondeu \(code)."
        }
        return false
    }

    func disconnect() {
        Keychain.delete(Self.tokenKey)
        connected = false
        stop()
        etags = [:]
        shas = [:]
        status = "Desconectado"
    }

    /// App em primeiro plano: confere agora e a cada 15 s.
    func start() {
        guard connected else { return }
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 15, repeats: true) { [weak self] _ in
            Task { @MainActor in await self?.pull() }
        }
        Task { await pull() }
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    // MARK: - Receber do Claude

    func pull() async {
        guard connected, !pulling else { return }
        pulling = true
        defer { pulling = false }
        if let data = await fetchIfChanged("looks.json"),
           let looks = try? JSONDecoder().decode([CustomLook].self, from: data) {
            camera?.applyRemoteLooks(looks)
        }
        if let data = await fetchIfChanged("ajustes.json"),
           let settings = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any], !settings.isEmpty {
            // Só aplica quando o arquivo mudou desde a última vez (não briga com o que você mexe no app)
            let fingerprint = shas["ajustes.json"] ?? ""
            if !fingerprint.isEmpty, fingerprint != defaults.string(forKey: "ajustesAplicados") {
                defaults.set(fingerprint, forKey: "ajustesAplicados")
                camera?.applyRemoteSettings(settings)
            }
        }
        if let data = await fetchIfChanged("recado.json"),
           let recado = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any],
           let id = recado["id"] as? String, !id.isEmpty, id != defaults.string(forKey: "ultimoRecado"),
           let texto = recado["texto"] as? String, !texto.isEmpty {
            defaults.set(id, forKey: "ultimoRecado")
            camera?.message = "Recado do Claude: \(texto)"
            dlog("Claude: recado \(id)")
        }
        if Date().timeIntervalSince(lastStatePush) > 600 {
            lastStatePush = Date()
            await pushState()
        }
        status = "Conectado · conferido às \(Date().formatted(date: .omitted, time: .shortened))"
    }

    /// Baixa o arquivo só se mudou (ETag); devolve nil se não mudou ou deu erro.
    private func fetchIfChanged(_ path: String) async -> Data? {
        let (code, body, headers) = await request("GET", path: path, etag: etags[path])
        if code == 401 {
            status = "A chave venceu ou foi apagada. Conecte de novo."
            return nil
        }
        guard code == 200, let body,
              let json = (try? JSONSerialization.jsonObject(with: body)) as? [String: Any],
              let content = json["content"] as? String,
              let data = Data(base64Encoded: content, options: .ignoreUnknownCharacters) else { return nil }
        if let etag = headers["etag"] { etags[path] = etag }
        if let sha = json["sha"] as? String { shas[path] = sha }
        return data
    }

    // MARK: - Mandar para o Claude

    /// Filmes próprios mudaram no app: manda a lista inteira.
    func pushLooks(_ looks: [CustomLook]) async -> Bool {
        guard connected else { return false }
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        guard let data = try? encoder.encode(looks) else { return false }
        let ok = await put("looks.json", data: data, message: "Revela: filmes próprios (\(looks.count))")
        // O ETag mudou: a próxima conferida baixa a versão nova (que é igual à nossa)
        if ok { etags["looks.json"] = nil }
        return ok
    }

    /// Relatório para o Claude. Devolve se foi.
    func sendReport(_ text: String) async -> Bool {
        guard connected else { return false }
        sending = true
        defer { sending = false }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd_HH-mm-ss"
        let path = "relatorios/\(formatter.string(from: Date())).md"
        let ok = await put(path, data: Data(text.utf8), message: "Revela: relatório \(Diagnostics.appVersion)")
        dlog(ok ? "Claude: relatório enviado (\(path))" : "❌ Claude: relatório não foi")
        status = ok ? "Relatório enviado às \(Date().formatted(date: .omitted, time: .shortened))" : status
        return ok
    }

    /// Estado do app (versão, validade, ajustes) para o Claude saber como está o iPhone.
    func pushState() async {
        guard connected, let camera else { return }
        let state: [String: Any] = [
            "versao": Diagnostics.appVersion,
            "aparelho": Diagnostics.deviceModel,
            "ios": UIDevice.current.systemVersion,
            "instalacaoValeAte": Expiration.text,
            "atualizadoEm": ISO8601DateFormatter().string(from: Date()),
            "ajustes": camera.settingsSnapshot,
        ]
        guard let data = try? JSONSerialization.data(withJSONObject: state, options: [.prettyPrinted, .sortedKeys]) else { return }
        _ = await put("estado.json", data: data, message: "Revela: estado")
    }

    /// Grava um arquivo no ramo (cria ou substitui). Se o arquivo mudou no meio do caminho, busca o sha e tenta de novo.
    private func put(_ path: String, data: Data, message: String) async -> Bool {
        for attempt in 0..<2 {
            if shas[path] == nil || attempt > 0 {
                let (code, body, _) = await request("GET", path: path)
                if code == 200, let body, let json = (try? JSONSerialization.jsonObject(with: body)) as? [String: Any] {
                    shas[path] = json["sha"] as? String
                }
            }
            var payload: [String: Any] = ["message": message, "content": data.base64EncodedString(), "branch": Self.branch]
            if let sha = shas[path] { payload["sha"] = sha }
            let (code, body, _) = await request("PUT", path: path, body: try? JSONSerialization.data(withJSONObject: payload))
            if code == 200 || code == 201 {
                if let body, let json = (try? JSONSerialization.jsonObject(with: body)) as? [String: Any],
                   let content = json["content"] as? [String: Any] {
                    shas[path] = content["sha"] as? String
                }
                return true
            }
            if code == 403 { status = "A chave não pode gravar (precisa de Contents: Read and write)." }
            if code != 409 && code != 422 { return false }
        }
        return false
    }

    // MARK: - GitHub

    private func request(_ method: String, path: String, token: String? = nil, etag: String? = nil,
                         body: Data? = nil) async -> (Int, Data?, [String: String]) {
        guard let token = token ?? self.token else { return (401, nil, [:]) }
        let encoded = path.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? path
        var components = URLComponents(string: "https://api.github.com/repos/\(Self.repo)/contents/\(encoded)")
        if method == "GET" { components?.queryItems = [URLQueryItem(name: "ref", value: Self.branch)] }
        guard let url = components?.url else { return (0, nil, [:]) }
        var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 20)
        request.httpMethod = method
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        if let etag { request.setValue(etag, forHTTPHeaderField: "If-None-Match") }
        if let body {
            request.httpBody = body
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            let http = response as? HTTPURLResponse
            var headers: [String: String] = [:]
            if let etag = http?.value(forHTTPHeaderField: "ETag") { headers["etag"] = etag }
            return (http?.statusCode ?? 0, data, headers)
        } catch {
            return (0, nil, [:])
        }
    }
}
