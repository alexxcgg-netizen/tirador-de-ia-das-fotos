import CoreGraphics

/// Geometria da captura em funções puras (sem câmera, sem estado), para o laboratório testar sem iPhone.
/// `cropFactor` é a conta do recorte de cada foto (CameraModel.shotOptions, com a lente que abriu e o zoom do sensor).
/// `photoPoint` ainda não está ligada: o Retrato usa framePoint + photoPoint(fromFrame:) do CameraModel. Testes: `PrevencaoTests.testP01Geometria` (RevelaLab).
enum CaptureGeometry {
    /// Recorte central (≥ 1) que a revelação aplica para chegar no zoom pedido, calculado com a lente que TIROU a foto.
    /// - Parameters:
    ///   - wantedZoom: zoom pedido, em relação à 1× (0,5; 1; 2,7; 8…).
    ///   - captureBaseZoom: zoom sem recorte da câmera que entregou a foto (0,5 ultra-angular/macro, 1 grande-angular,
    ///     4 tele). Não é a lente escolhida nem a do visor no toque: durante a troca de lente as três podem diferir, e a
    ///     foto tem que sair com o enquadramento pedido qualquer que seja a câmera que respondeu.
    ///   - front: foto da câmera da frente (zoom digital de 1× a 3×; o recorte é o próprio zoom).
    /// - Returns: 1 quando não há o que recortar (zoom menor que o da lente, ou valores inválidos).
    static func cropFactor(wantedZoom: CGFloat, captureBaseZoom: CGFloat, front: Bool = false) -> CGFloat {
        guard wantedZoom.isFinite, wantedZoom > 0 else { return 1 }
        if front { return min(max(wantedZoom, 1), 3) }
        guard captureBaseZoom.isFinite, captureBaseZoom > 0 else { return 1 }
        return max(1, wantedZoom / captureBaseZoom)
    }

    /// Ponto tocado no visor → ponto na foto inteira (antes do recorte), os dois em 0…1 com origem em cima à esquerda.
    /// Como o visor mostra a foto: gira `quarterTurns` quartos de volta no sentido horário, recorta o miolo 1/`crop` e
    /// espelha na horizontal se `mirrored`. Aqui é o caminho de volta: desespelha, desfaz o recorte, desgira.
    /// - Parameters:
    ///   - viewPoint: onde a pessoa tocou, em 0…1 do visor (como ela vê).
    ///   - crop: recorte central (zoom digital) da revelação, ≥ 1 (valor inválido conta como 1).
    ///   - mirrored: o visor está espelhado em relação à foto salva antes do espelho da revelação (câmera da frente:
    ///     o visor espelha e a foto não).
    ///   - quarterTurns: quartos de volta, no sentido horário, que levam a foto salva (já em pé pela orientação do
    ///     arquivo) para o jeito que o visor mostra. iPhone deitado com a tela travada em pé = ±1. Negativo = anti-horário.
    /// - Returns: o ponto na foto, limitado a 0…1.
    static func photoPoint(fromView viewPoint: CGPoint, crop: CGFloat, mirrored: Bool, quarterTurns: Int) -> CGPoint {
        let c = crop.isFinite && crop >= 1 ? crop : 1
        var x = viewPoint.x, y = viewPoint.y
        if mirrored { x = 1 - x }
        x = 0.5 + (x - 0.5) / c
        y = 0.5 + (y - 0.5) / c
        // Cada quarto horário levou (x, y) da foto para (1 − y, x) no visor; a volta é (x, y) → (y, 1 − x)
        let turns = ((quarterTurns % 4) + 4) % 4
        for _ in 0..<turns {
            (x, y) = (y, 1 - x)
        }
        return CGPoint(x: min(max(x, 0), 1), y: min(max(y, 0), 1))
    }
}
