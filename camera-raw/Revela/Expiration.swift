import Foundation
import UserNotifications

/// A instalação com conta grátis da Apple vale 7 dias. Lê a data no perfil de instalação
/// (embedded.mobileprovision) para avisar antes do app parar de abrir.
enum Expiration {
    static let date: Date? = {
        guard let url = Bundle.main.url(forResource: "embedded", withExtension: "mobileprovision"),
              let data = try? Data(contentsOf: url),
              let text = String(data: data, encoding: .isoLatin1),
              let start = text.range(of: "<?xml"), let end = text.range(of: "</plist>") else { return nil }
        let plist = Data(text[start.lowerBound..<end.upperBound].utf8)
        let dict = (try? PropertyListSerialization.propertyList(from: plist, format: nil)) as? [String: Any]
        return dict?["ExpirationDate"] as? Date
    }()

    /// Dias inteiros que faltam (0 = vence hoje).
    static var daysLeft: Int? {
        guard let date else { return nil }
        return max(0, Int(floor(date.timeIntervalSinceNow / 86_400)))
    }

    static var text: String {
        guard let date else { return "sem data (instalação sem perfil)" }
        return date.formatted(date: .abbreviated, time: .shortened)
    }

    /// Avisos: 1 dia antes e 3 horas antes de vencer.
    static func scheduleReminders() {
        guard let date, date.timeIntervalSinceNow > 0 else { return }
        dlog("Instalação vale até \(text)")
        let center = UNUserNotificationCenter.current()
        center.requestAuthorization(options: [.alert, .sound]) { granted, _ in
            guard granted else { return }
            center.removePendingNotificationRequests(withIdentifiers: ["expira-1d", "expira-3h"])
            for (id, before, body) in [("expira-1d", 86_400.0, "O Revela para de abrir amanhã. Reinstale pelo Sideloadly no PC."),
                                       ("expira-3h", 10_800.0, "O Revela para de abrir em 3 horas. Reinstale pelo Sideloadly.")] {
                let fire = date.addingTimeInterval(-before)
                guard fire.timeIntervalSinceNow > 60 else { continue }
                let content = UNMutableNotificationContent()
                content.title = "Revela"
                content.body = body
                let trigger = UNTimeIntervalNotificationTrigger(timeInterval: fire.timeIntervalSinceNow, repeats: false)
                center.add(UNNotificationRequest(identifier: id, content: content, trigger: trigger))
            }
        }
    }
}
