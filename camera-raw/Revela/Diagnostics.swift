import Foundation
import MetricKit
import UIKit
import os

/// Registro do que acontece no app, para montar o relatório que vai para o Claude.
/// Fica salvo em arquivo, então sobrevive a um travamento.
final class Diagnostics: NSObject, MXMetricManagerSubscriber {
    static let shared = Diagnostics()

    private let queue = DispatchQueue(label: "revela.diagnostics")
    private let logURL: URL
    private let crashDir: URL
    private let maxLogBytes = 400_000
    private let start = Date()

    /// Estatísticas que mudam o tempo todo (ex.: quadros por segundo do visor); entram no relatório sem poluir o log.
    private var stats: [String: String] = [:]

    private override init() {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        logURL = docs.appendingPathComponent("revela-log.txt")
        crashDir = docs.appendingPathComponent("diagnostics", isDirectory: true)
        try? FileManager.default.createDirectory(at: crashDir, withIntermediateDirectories: true)
        super.init()
    }

    private var monitoring = false

    func startMonitoring() {
        guard !monitoring else { return }
        monitoring = true
        // Erro do Objective-C que escapou: anota o motivo antes do app fechar
        NSSetUncaughtExceptionHandler { exception in
            let stack = exception.callStackSymbols.prefix(25).joined(separator: "\n")
            Diagnostics.shared.log("💥 App fechou: \(exception.name.rawValue): \(exception.reason ?? "")\n\(stack)")
        }
        MXMetricManager.shared.add(self)
        log("App aberto · \(Self.deviceModel) · iOS \(UIDevice.current.systemVersion) · Revela \(Self.appVersion)")
        let center = NotificationCenter.default
        center.addObserver(forName: UIApplication.didReceiveMemoryWarningNotification, object: nil, queue: nil) { _ in
            self.log("⚠️ Aviso de memória · livre: \(Self.freeMemory)")
        }
        center.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification, object: nil, queue: nil) { _ in
            self.log("🌡️ Temperatura: \(Self.thermalState)")
        }
    }

    private let writeLock = NSLock()

    /// Grava na hora (não em fila): se o app fechar logo depois, a linha já está no arquivo.
    func log(_ message: String) {
        let elapsed = String(format: "%7.1fs", Date().timeIntervalSince(start))
        let line = "\(elapsed)  \(message)\n"
        guard let data = line.data(using: .utf8) else { return }
        writeLock.lock()
        defer { writeLock.unlock() }
        if let handle = try? FileHandle(forWritingTo: logURL) {
            handle.seekToEndOfFile()
            handle.write(data)
            try? handle.close()
        } else {
            try? data.write(to: logURL)
        }
        trimIfNeeded()
    }

    func set(_ key: String, _ value: String) {
        queue.async { self.stats[key] = value }
    }

    /// Mede quanto tempo um trecho leva e registra.
    @discardableResult
    func time<T>(_ label: String, _ work: () -> T) -> T {
        let t0 = CFAbsoluteTimeGetCurrent()
        let result = work()
        log("\(label): \(Self.ms(since: t0))")
        return result
    }

    static func ms(since t0: CFAbsoluteTime) -> String {
        String(format: "%.0f ms", (CFAbsoluteTimeGetCurrent() - t0) * 1000)
    }

    func clear() {
        queue.async {
            try? FileManager.default.removeItem(at: self.logURL)
            if let files = try? FileManager.default.contentsOfDirectory(at: self.crashDir, includingPropertiesForKeys: nil) {
                files.forEach { try? FileManager.default.removeItem(at: $0) }
            }
        }
        log("Relatório limpo")
    }

    private func trimIfNeeded() {
        guard let size = (try? FileManager.default.attributesOfItem(atPath: logURL.path))?[.size] as? Int,
              size > maxLogBytes, let data = try? Data(contentsOf: logURL) else { return }
        try? data.suffix(maxLogBytes / 2).write(to: logURL)
    }

    // MARK: - Relatório

    func report(note: String, camera: String, completion: @escaping (String) -> Void) {
        queue.async {
            var out = "# Relatório do Revela\n\n"
            if !note.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                out += "## O que aconteceu (escrito por quem usa)\n\(note)\n\n"
            }
            out += "## Aparelho\n"
            out += "- Modelo: \(Self.deviceModel)\n"
            out += "- iOS: \(UIDevice.current.systemVersion)\n"
            out += "- Revela: \(Self.appVersion)\n"
            out += "- Memória livre: \(Self.freeMemory)\n"
            out += "- Temperatura: \(Self.thermalState)\n"
            out += "- Gerado em: \(ISO8601DateFormatter().string(from: Date()))\n\n"
            out += "## Agora\n"
            for (key, value) in self.stats.sorted(by: { $0.key < $1.key }) { out += "- \(key): \(value)\n" }
            out += "\n## Câmera\n\(camera)\n"
            // O que o Claude (Opus 5.5) viu nas últimas fotos, se a análise foi feita
            if let analysis = PhotoCritic.lastAnalysis {
                out += "## Análise das fotos pelo Claude (Opus 5.5)\n\(analysis)\n\n"
            }

            let crashes = (try? FileManager.default.contentsOfDirectory(at: self.crashDir, includingPropertiesForKeys: nil)) ?? []
            if !crashes.isEmpty {
                out += "## Travamentos e problemas registrados pelo iOS (\(crashes.count))\n"
                for file in crashes.sorted(by: { $0.lastPathComponent > $1.lastPathComponent }).prefix(3) {
                    let text = (try? String(contentsOf: file, encoding: .utf8)) ?? ""
                    out += "### \(file.lastPathComponent)\n```json\n\(text.prefix(12_000))\n```\n"
                }
                out += "\n"
            }

            let log = (try? String(contentsOf: self.logURL, encoding: .utf8)) ?? "(vazio)"
            out += "## Registro\n```\n\(log.suffix(60_000))\n```\n"
            DispatchQueue.main.async { completion(out) }
        }
    }

    // MARK: - MetricKit (travamentos chegam na próxima abertura do app)

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            let name = "ios-\(Int(payload.timeStampEnd.timeIntervalSince1970)).json"
            try? payload.jsonRepresentation().write(to: crashDir.appendingPathComponent(name))
            let crashes = payload.crashDiagnostics?.count ?? 0
            let hangs = payload.hangDiagnostics?.count ?? 0
            log("📋 iOS entregou diagnóstico: \(crashes) travamento(s), \(hangs) congelamento(s)")
        }
    }

    func didReceive(_ payloads: [MXMetricPayload]) {}

    // MARK: - Informações do aparelho

    static var deviceModel: String {
        var info = utsname()
        uname(&info)
        return withUnsafePointer(to: &info.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: 1) { String(cString: $0) }
        }
    }

    static var appVersion: String {
        let info = Bundle.main.infoDictionary
        return "\(info?["CFBundleShortVersionString"] ?? "?") (\(info?["CFBundleVersion"] ?? "?"))"
    }

    static var freeMemory: String {
        String(format: "%.0f MB", Double(os_proc_available_memory()) / 1_048_576)
    }

    static var thermalState: String {
        switch ProcessInfo.processInfo.thermalState {
        case .nominal: return "normal"
        case .fair: return "morno"
        case .serious: return "quente"
        case .critical: return "crítico"
        @unknown default: return "?"
        }
    }
}

/// Atalho curto.
func dlog(_ message: String) { Diagnostics.shared.log(message) }

/// Tenta um comando que a câmera pode recusar. Se recusar, anota o motivo e segue em vez de fechar o app.
@discardableResult
func attempt(_ label: String, _ block: () -> Void) -> Bool {
    if let exception = RevelaCatch(block) {
        dlog("💥 \(label) recusado: \(exception.name.rawValue): \(exception.reason ?? "")")
        return false
    }
    return true
}

/// Abertura do app: se a anterior não chegou a ficar de pé, abre no modo seguro.
enum LaunchGuard {
    private static let key = "launchInProgress"

    /// true = a última abertura fechou antes de terminar.
    static func begin() -> Bool {
        let defaults = UserDefaults.standard
        let crashed = defaults.bool(forKey: key)
        defaults.set(true, forKey: key)
        Diagnostics.shared.startMonitoring()
        if crashed { dlog("⚠️ A abertura anterior fechou antes de terminar: modo seguro") }
        return crashed
    }

    static func markStable() {
        UserDefaults.standard.set(false, forKey: key)
    }
}
