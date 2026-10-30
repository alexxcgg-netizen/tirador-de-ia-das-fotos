import CoreLocation

/// Onde a foto foi tirada, para ela aparecer no mapa da galeria. Só liga com o app aberto.
final class Locator: NSObject, CLLocationManagerDelegate {
    static let shared = Locator()

    private let manager = CLLocationManager()
    private let lock = NSLock()
    private var latest: CLLocation?

    /// Ligado por padrão; dá para desligar nos Ajustes do app.
    var enabled: Bool {
        get { UserDefaults.standard.object(forKey: "saveLocation") as? Bool ?? true }
        set {
            UserDefaults.standard.set(newValue, forKey: "saveLocation")
            if newValue { start() } else { stop() }
        }
    }

    /// Posição de no máximo 10 minutos atrás (nil se desligado ou sem sinal).
    var current: CLLocation? {
        lock.lock()
        defer { lock.unlock() }
        guard enabled, let latest, -latest.timestamp.timeIntervalSinceNow < 600 else { return nil }
        return latest
    }

    private override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters
        manager.distanceFilter = 15
    }

    func start() {
        guard enabled else { return }
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways: manager.startUpdatingLocation()
        default: break
        }
    }

    func stop() {
        manager.stopUpdatingLocation()
    }

    var statusText: String {
        switch manager.authorizationStatus {
        case .notDetermined: return "ainda não pediu"
        case .authorizedWhenInUse, .authorizedAlways: return current == nil ? "permitida, sem sinal ainda" : "ok"
        default: return "negada nos Ajustes do iPhone"
        }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        if enabled, manager.authorizationStatus == .authorizedWhenInUse || manager.authorizationStatus == .authorizedAlways {
            manager.startUpdatingLocation()
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let last = locations.last, last.horizontalAccuracy >= 0 else { return }
        lock.lock()
        latest = last
        lock.unlock()
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {}
}
