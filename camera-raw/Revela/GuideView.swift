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
            Item(symbol: "camera.filters", title: "Botão do look",
                 text: "Mostra o look atual (ex.: Portra 400). Toque para escolher outro e ajustar intensidade e grão; o visor muda na hora."),
            Item(symbol: "slider.horizontal.3", title: "Ajustes",
                 text: "Tudo o que é técnico mora aqui: formato RAW, luz, foco, cor, timer, peaking, zebra, espelhar e o relatório. Abre pela metade, com o visor visível."),
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
            Item(symbol: "lock", title: "Segurar no visor", text: "Trava foco e exposição (TRAVA AE/AF). Um toque solta."),
            Item(symbol: "photo.on.rectangle", title: "Miniatura", text: "Abre o Revelar de novo: troque o filme da última foto (ou de qualquer foto da galeria) e, no retrato, o foco e o desfoque. Na aba Ajustes: exposição, temperatura, tom, sombras, altas luzes, endireitar e recorte."),
            Item(symbol: "person.crop.circle", title: "Proteger a pele", text: "Nos filmes fortes (Matrix, Blockbuster, Cross-process…) a pele fica natural e o resto pega o look, como os coloristas fazem no cinema. Liga e desliga na lista de looks."),
            Item(symbol: "chart.bar.fill", title: "Histograma",
                 text: "O gráfico no canto: à esquerda as sombras, à direita as luzes. Encostado na direita = estourado."),
            Item(symbol: "minus", title: "Nível", text: "Fica laranja quando o iPhone está reto. Apontando para baixo vira duas cruzes que se encontram."),
            Item(symbol: "paintpalette", title: "Cor falsa (em Ajustes)",
                 text: "Pinta a imagem por brilho: verde é o cinza médio, rosa é pele bem exposta, vermelho é estourado."),
        ]),
        ("Controles", [
            Item(symbol: "dial.low", title: "ISO e obturador",
                 text: "ISO é a sensibilidade (mais alto = mais claro e mais ruído). Obturador é o tempo da foto (mais longo = mais claro e mais tremido)."),
            Item(symbol: "thermometer.sun", title: "Balanço (AWB)", text: "Cor da luz. Kelvin baixo deixa a foto azulada, alto deixa alaranjada."),
            Item(symbol: "scope", title: "Foco manual", text: "Arraste de perto a longe. Enquanto arrasta, o visor amplia 4× (lupa)."),
            Item(symbol: "camera.filters", title: "Look", text: "O estilo de filme. O chip Look ajusta a intensidade e o tamanho do grão."),
            Item(symbol: "paintbrush", title: "Meus filmes", text: "Na lista de looks, \"Criar filme\" parte do look atual: mexa em cor, contraste, grão e luz e salve com um nome."),
        ]),
        ("Modos rápidos", [
            Item(symbol: "bolt.fill", title: "Rápido",
                 text: "Disparo sem atraso em 12 MP. Toque várias vezes ou segure o botão para rajada (até 60 fotos)."),
            Item(symbol: "figure.run", title: "Ação",
                 text: "Grava em 4K a 120 quadros por segundo enquanto você segura (um toque grava 1 s). O app salva as 8 fotos mais nítidas e o vídeo em câmera lenta."),
            Item(symbol: "snowflake", title: "Congelar",
                 text: "Obturador de 1/1000 a 1/16000 s para parar movimento (roda, água, esporte). Precisa de muita luz. MÁX usa o modo mais rápido do sensor: raios menos tortos, foto de ~2 MP."),
        ]),
        ("Zoom", [
            Item(symbol: "arrow.up.left.and.arrow.down.right", title: "Pinça no visor",
                 text: "Afaste dois dedos para aproximar (até 25×). Ao soltar, o app escolhe sozinho a melhor câmera: ultra-angular, principal ou tele."),
            Item(symbol: "plus.magnifyingglass", title: "Botões de zoom",
                 text: "0,5×, 1×, 2× e 4× são câmeras ou recortes de 48 MP com qualidade óptica. A flor liga o Macro (foca a 2 cm) e o 8× é a tele recortada."),
        ]),
        ("Vídeo", [
            Item(symbol: "video.fill", title: "Vídeo", text: "1080p a 24, 30 ou 60 fps com o look gravado junto. Toque para começar e parar."),
            Item(symbol: "camera.aperture", title: "Cinemático",
                 text: "Vídeo com o fundo desfocado (Modo Cinema da Apple). O foco segue as pessoas, e no app Fotos dá para mudar o foco e o desfoque depois."),
            Item(symbol: "rectangle.inset.topright.filled", title: "Dupla",
                 text: "Câmera de trás e da frente ao mesmo tempo, com você num quadrinho. Toque: foto. Segure: vídeo."),
        ]),
        ("Scanner 3D", [
            Item(symbol: "cube.transparent", title: "CENA (LiDAR + fotos)",
                 text: "Ande devagar em volta: o app guarda fotos 4K com a posição exata de cada uma e a profundidade do LiDAR. No fim: nuvem de pontos colorida, malha para ver em AR e um .zip para gerar um Gaussian splat realista no PC com o Brush."),
            Item(symbol: "cube", title: "OBJETO",
                 text: "Object Capture da Apple: modelo 3D de um objeto, montado no iPhone. No iPhone 17 Pro ele tem um defeito conhecido do iOS; se falhar, use CENA."),
        ]),
        ("Modos", [
            Item(symbol: "person.crop.rectangle", title: "Retrato",
                 text: "Fundo desfocado pela profundidade medida com o LiDAR, com bokeh de lente: as luzes do fundo viram bolinhas e o cabelo fica recortado. f/1,4 borra muito, f/16 quase nada. Também avisa a distância para o rosto não deformar."),
            Item(symbol: "sun.max", title: "HDR",
                 text: "3 fotos RAW (escura, normal, clara) juntadas: céu com cor e sombra com detalhe, sem o exagero do HDR comum."),
            Item(symbol: "moon.stars", title: "Noite, Estrelas, Lua",
                 text: "Várias fotos alinhadas e somadas: muito menos ruído no escuro. Na Noite você escolhe o tempo de cada foto e quantas; no Auto, se o iPhone estiver apoiado, cada foto fica mais longa."),
            Item(symbol: "camera.macro", title: "Macro e Foco empilhado",
                 text: "A flor liga o macro (foca a 2 cm); chegando perto com a 1× ele liga sozinho. No macro: 2× e 3× (super resolução), Empilhar (6 fotos, tudo nítido) e Luz (lanterna fraca, média ou forte)."),
            Item(symbol: "square.and.arrow.down", title: "LUT e cor copiada",
                 text: "Na lista de looks: importe uma LUT .cube (do app Arquivos) ou escolha uma foto para copiar a cor dela."),
            Item(symbol: "square.stack", title: "Três looks por foto",
                 text: "Em Ajustes: cada foto sai também em mais dois looks que você escolhe."),
            Item(symbol: "timer", title: "Longa",
                 text: "Junta 1 a 8 segundos de vídeo numa foto. Seda deixa água e nuvens lisas; Rastros desenha as luzes dos carros e estrelas. Apoie o iPhone."),
            Item(symbol: "square.resize.up", title: "Super res",
                 text: "6 fotos de 48 MP alinhadas em fração de pixel e juntadas: foto de até 100 MP com mais detalhe real (e menos ruído) para ampliar depois. Segure firme; leva uns segundos para revelar."),
            Item(symbol: "square.stack.3d.up", title: "Média", text: "8 fotos somadas: menos ruído, ou água lisa com obturador lento."),
            Item(symbol: "pano", title: "Panorama", text: "Toque e gire o iPhone devagar para um lado, sem subir nem descer. Toque de novo para terminar (ou ele para sozinho em 240°)."),
            Item(symbol: "doc.viewfinder", title: "DOC", text: "Documentos de várias páginas: acha a folha sozinho, deixa o papel branco e junta tudo num PDF, sem marca d'água."),
        ]),
        ("Dentro de Ajustes", [
            Item(symbol: "arrow.left.and.right", title: "Espelhar", text: "Salva a foto invertida, como você se vê no espelho."),
            Item(symbol: "location", title: "Localização", text: "Guarda onde cada foto foi tirada, para ela aparecer no mapa da galeria."),
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
