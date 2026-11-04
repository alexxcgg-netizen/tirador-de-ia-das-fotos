import CoreGraphics
import Foundation

/// O que muda várias vezes por segundo no visor (histograma, ISO de agora, rosto). Fica separado do
/// CameraModel: só as pecinhas que mostram isso se redesenham, não a tela inteira (era o que engasgava).
final class LiveStats: ObservableObject {
    struct FaceAdvice: Equatable {
        let text: String
        let good: Bool
    }

    @Published var histogram: [Float] = []
    @Published var histogramRGB: [[Float]] = []
    @Published var iso: Float = 0
    @Published var shutter: Double = 0
    @Published var face: CGRect?
    @Published var advice: FaceAdvice?
}
