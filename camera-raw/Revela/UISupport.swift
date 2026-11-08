import ImageIO
import Photos
import SwiftUI
import UIKit

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Número com vírgula, como se escreve no Brasil ("0,5", "+0,3", "1,0").
func ptNumber<T: BinaryFloatingPoint>(_ value: T, digits: Int = 1, sign: Bool = false) -> String {
    let format = "%" + (sign ? "+" : "") + ".\(digits)f"
    return String(format: format, Double(value)).replacingOccurrences(of: ".", with: ",")
}

extension View {
    /// Leitor de tela: diz "selecionado" no botão escolhido de uma fileira de opções.
    func selectedTrait(_ on: Bool) -> some View {
        accessibilityAddTraits(on ? AccessibilityTraits.isSelected : AccessibilityTraits())
    }
}

/// Pede ao iOS um tempo a mais quando o app vai para o fundo no meio de um trabalho (revelação, análise do Claude).
/// Sem isso o iOS congelava o app na hora e a foto só saía quando ele voltasse. Chamar só na fila principal.
final class BackgroundWork {
    static let shared = BackgroundWork()
    private var tasks: [String: UIBackgroundTaskIdentifier] = [:]

    func begin(_ name: String) {
        guard tasks[name] == nil else { return }
        let id = UIApplication.shared.beginBackgroundTask(withName: name) { [weak self] in
            // O tempo extra acabou: solta antes que o iOS feche o app
            self?.end(name)
        }
        if id != .invalid { tasks[name] = id }
    }

    func end(_ name: String) {
        guard let id = tasks.removeValue(forKey: name) else { return }
        UIApplication.shared.endBackgroundTask(id)
    }
}

/// Miniatura da última foto do Revela ao abrir o app (antes o quadradinho ficava vazio até a primeira foto).
enum LastPhoto {
    /// Com acesso às fotos já dado, a foto revelada da galeria; senão, a prévia do original guardado.
    /// Tudo fora da fila principal; `completion` volta na principal. Nunca pede permissão nova.
    static func loadThumbnail(completion: @escaping (UIImage) -> Void) {
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
        let canRead = status == .authorized || status == .limited
        DispatchQueue.global(qos: .utility).async {
            let developed: UIImage? = canRead ? LastPhoto.fromLibrary() : nil
            guard let image = developed ?? LastPhoto.fromOriginal() else { return }
            DispatchQueue.main.async { completion(image) }
        }
    }

    private static func fromLibrary() -> UIImage? {
        guard let id = SourceStore.latestEntry()?.assetID,
              let asset = PHAsset.fetchAssets(withLocalIdentifiers: [id], options: nil).firstObject else { return nil }
        let options = PHImageRequestOptions()
        options.isSynchronous = true
        options.deliveryMode = .highQualityFormat
        options.resizeMode = .fast
        options.isNetworkAccessAllowed = false
        var result: UIImage?
        PHImageManager.default().requestImage(for: asset, targetSize: CGSize(width: 168, height: 168),
                                              contentMode: .aspectFill, options: options) { image, _ in result = image }
        return result
    }

    private static func fromOriginal() -> UIImage? {
        guard let url = SourceStore.latestFileURL(),
              let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
        // DNG: só a prévia embutida (abrir o RAW inteiro na abertura do app pesaria); HEIC sai rápido de qualquer jeito
        let isRaw = url.pathExtension.lowercased() == "dng"
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageIfAbsent: !isRaw,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceThumbnailMaxPixelSize: 240,
        ]
        guard let cg = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else { return nil }
        return UIImage(cgImage: cg)
    }
}

/// Mira da NOITE: muda 10 vezes por segundo, então fica num objeto só dela (só a mira se redesenha, não a tela toda).
final class AimState: ObservableObject {
    @Published var offset: CGSize = .zero
}

extension CameraModel {
    /// Algo saindo agora que uma troca de modo estragaria: gravação, rajada, sequência, contagem ou panorama.
    var isBusy: Bool {
        isRecordingVideo || actionRecording || bursting || stackProgress != nil || longRemaining != nil
            || countdown > 0 || panoramaProgress != nil
    }

    /// ISO a partir do qual a FOTO junta várias fotos (FOTO 3×). O mesmo número do capture().
    static let fusionMinISO: Float = 320

    /// A FOTO 3× vale neste modo e nesta lente (só falta a luz): FOTO, junção ligada, nem macro nem frontal.
    var fusionEligible: Bool {
        captureMode == .photo && photoFusion && lens != .macro && lens != .front
    }

    /// O próximo toque na FOTO vai sair FOTO 3× (mesma condição do capture()).
    var fusionWillTrigger: Bool {
        fusionEligible && (manualExposure ? selectedISO : readoutISO) >= CameraModel.fusionMinISO
    }
}

extension CaptureMode {
    /// Primeira frase da dica, para a telinha de modos.
    var shortHint: String {
        hint.split(separator: ".", maxSplits: 1).first.map { String($0) } ?? hint
    }
}

/// Novidades de cada versão: aparecem uma vez quando o app atualiza (só nas versões que têm texto aqui).
enum WhatsNew {
    static let notes: [String: [String]] = [
        "0.30": [
            "FOTO 3× com mais acabamento: com pouca luz, cada toque junta várias fotos do mesmo instante. O selo 3× no visor avisa quando vai acontecer.",
            "SUPER ZOOM novo: 24 fotos na mão, todas as nítidas resolvidas juntas, com mais detalhe de verdade.",
            "NOITE na mão mais nítida: fotos mais curtas (1/15 a 1/8 s) e o borrão que sobra desfeito.",
            "Vídeo mais robusto, e o app não troca de modo no meio de uma gravação ou de uma sequência.",
            "Revelações longas mostram no visor o que está revelando; dá para continuar fotografando.",
            "Timer no topo (toque no botão de foto para cancelar a contagem), ajustes guardados entre aberturas e menus do sistema em português.",
        ],
    ]

    static var currentVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? ""
    }

    /// As notas para mostrar agora (uma vez por versão). Na primeira instalação não mostra: o Guia rápido já abre.
    static func pending(firstLaunch: Bool) -> [String]? {
        let defaults = UserDefaults.standard
        let version = currentVersion
        guard !version.isEmpty, defaults.string(forKey: "lastSeenVersion") != version else { return nil }
        defaults.set(version, forKey: "lastSeenVersion")
        guard !firstLaunch else { return nil }
        return notes[version]
    }
}

/// Cartão "Novidades da versão", uma vez depois de atualizar.
struct WhatsNewView: View {
    let items: [String]
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    ForEach(items, id: \.self) { item in
                        HStack(alignment: .top, spacing: 10) {
                            Image(systemName: "sparkle").foregroundStyle(accent)
                            Text(item).font(.subheadline)
                        }
                    }
                }
                .padding(20)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .navigationTitle("Novidades da versão \(WhatsNew.currentVersion)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Entendi") { dismiss() } } }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
        .presentationDetents([.medium, .large])
    }
}
