import SwiftUI

/// Explica cada botão e cada termo do app, em português simples.
struct GuideView: View {
    @Environment(\.dismiss) private var dismiss

    private struct Item: Identifiable {
        let symbol: String
        let title: String
        let text: String
        var id: String { title }
    }

    private let sections: [(String, [Item])] = [
        ("Topo", [
            Item(symbol: "camera.aperture", title: "ProRAW",
                 text: "Foto RAW de 48 MP em que a Apple já juntou alguns quadros e limpou o ruído. Muito detalhe; a melhor escolha no dia a dia."),
            Item(symbol: "camera.aperture", title: "RAW puro",
                 text: "O sinal cru do sensor, um quadro só, 12 MP, sem nada da Apple. Tem mais ruído, mas é o \u{201C}filme virgem\u{201D} de verdade."),
            Item(symbol: "timer", title: "Timer", text: "A foto sai 3 ou 10 segundos depois de apertar. Bom com tripé ou para entrar na foto."),
            Item(symbol: "circle.lefthalf.striped.horizontal", title: "Zebra",
                 text: "Listras onde a luz estourou, ou seja, ficou branco sem detalhe. Se aparecer, baixe a exposição."),
            Item(symbol: "scope", title: "Peaking (a mira)",
                 text: "Pinta de laranja as bordas que estão em foco. Essencial no macro e no foco manual."),
            Item(symbol: "rectangle", title: "4:3, 1:1, 16:9, 65:24", text: "Proporção da foto. 65:24 é a panorâmica de cinema."),
        ]),
        ("Visor", [
            Item(symbol: "hand.tap", title: "Tocar no visor", text: "Foca e mede a luz no ponto tocado."),
            Item(symbol: "chart.bar.fill", title: "Histograma",
                 text: "O gráfico no canto: à esquerda as sombras, à direita as luzes. Encostado na direita = estourado."),
            Item(symbol: "minus", title: "Linha de nível", text: "Fica laranja quando o iPhone está reto."),
        ]),
        ("Controles", [
            Item(symbol: "dial.low", title: "ISO e obturador",
                 text: "ISO é a sensibilidade (mais alto = mais claro e mais ruído). Obturador é o tempo da foto (mais longo = mais claro e mais tremido)."),
            Item(symbol: "thermometer.sun", title: "Balanço (AWB)", text: "Cor da luz. Kelvin baixo deixa a foto azulada, alto deixa alaranjada."),
            Item(symbol: "scope", title: "Foco manual", text: "Arraste de perto a longe. Enquanto arrasta, o visor amplia 4× (lupa)."),
            Item(symbol: "camera.filters", title: "Look", text: "O estilo de filme. O chip Look ajusta a intensidade e o tamanho do grão."),
        ]),
        ("Modos", [
            Item(symbol: "person.crop.rectangle", title: "Retrato", text: "Lente 2× e aviso de distância para o rosto não deformar."),
            Item(symbol: "moon.stars", title: "Noite, Estrelas, Lua", text: "Várias fotos alinhadas e somadas: muito menos ruído no escuro."),
            Item(symbol: "camera.macro", title: "Macro e Foco empilhado",
                 text: "Macro foca a 2 cm. Foco empilhado faz 7 fotos com foco diferente e junta tudo nítido."),
            Item(symbol: "square.stack.3d.up", title: "Média", text: "8 fotos somadas: menos ruído, ou água lisa com obturador lento."),
        ]),
        ("Menu …", [
            Item(symbol: "arrow.left.and.right", title: "Espelhar", text: "Salva a foto invertida, como você se vê no espelho."),
            Item(symbol: "doc.badge.plus", title: "Guardar DNG",
                 text: "Guarda também o arquivo RAW original (uns 50 MB) para revelar depois no Lightroom."),
            Item(symbol: "doc.text.magnifyingglass", title: "Relatório", text: "Junta o que aconteceu no app para você mandar ao Claude."),
        ]),
    ]

    var body: some View {
        NavigationStack {
            List {
                ForEach(sections, id: \.0) { section in
                    Section(section.0) {
                        ForEach(section.1) { item in
                            HStack(alignment: .top, spacing: 12) {
                                Image(systemName: item.symbol)
                                    .frame(width: 26)
                                    .foregroundStyle(Color(red: 0.96, green: 0.64, blue: 0.24))
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(item.title).font(.subheadline.weight(.semibold))
                                    Text(item.text).font(.footnote).foregroundStyle(.secondary)
                                }
                            }
                            .padding(.vertical, 2)
                        }
                    }
                }
            }
            .navigationTitle("Guia rápido")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("OK") { dismiss() } }
            }
        }
        .preferredColorScheme(.dark)
    }
}
