import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Faixa de filmes em cima do visor: cada filme aparece com o que a câmera está vendo agora.
/// Um toque troca o filme e o visor já mostra; não precisa abrir lista nem voltar.
struct LookStrip: View {
    @ObservedObject var camera: CameraModel
    /// Revelar de novo aberto por cima: as miniaturas param (a GPU fica para a revelação).
    var paused = false
    var onMore: () -> Void

    /// "todos", "meus" ou o nome de um tipo (Cor, Fuji…).
    @AppStorage("lookStripFilter") private var filter = "todos"
    @State private var thumbs: [String: UIImage] = [:]
    /// Miniaturas na tela agora (só elas, mais 2 de cada lado, são refeitas).
    @State private var visible: Set<String> = []
    /// Quadro do visor da última rodada: sem quadro novo não refaz nada.
    @State private var lastFrame = -1
    @State private var rendering = false

    private var items: [CameraModel.LookChoice] {
        let mine = camera.customLooks.map { CameraModel.LookChoice(id: "c:" + $0.id.uuidString, name: $0.name) }
        func base(_ looks: [Look]) -> [CameraModel.LookChoice] {
            looks.map { CameraModel.LookChoice(id: "b:" + $0.rawValue, name: $0.rawValue) }
        }
        switch filter {
        case "meus": return mine
        case "todos": return mine + base(Look.allCases)
        default:
            guard let family = LookFamily(rawValue: filter) else { return mine + base(Look.allCases) }
            return base([.neutro] + family.looks.filter { $0 != .neutro })
        }
    }

    private var filters: [(id: String, name: String)] {
        var list: [(String, String)] = [("todos", "Todos")]
        if !camera.customLooks.isEmpty { list.append(("meus", "Meus")) }
        list += LookFamily.allCases.filter { $0 != .neutro }.map { ($0.rawValue, $0.rawValue) }
        return list
    }

    var body: some View {
        VStack(spacing: 8) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(filters, id: \.id) { f in
                        Button(f.name) {
                            filter = f.id
                            UISelectionFeedbackGenerator().selectionChanged()
                        }
                        .font(.caption.weight(.bold))
                        .padding(.horizontal, 10).frame(height: 28)
                        .foregroundStyle(filter == f.id ? Color.black : Color.white)
                        .background(Capsule().fill(filter == f.id ? accent : Color.white.opacity(0.12)))
                        .buttonStyle(.plain)
                        .selectedTrait(filter == f.id)
                    }
                }
                .padding(.horizontal, 10)
            }

            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    // Preguiçosa: só as miniaturas perto da tela existem (e avisam quando aparecem)
                    LazyHStack(spacing: 8) {
                        ForEach(items) { item in
                            thumbnail(item)
                                .id(item.id)
                                .onAppear { visible.insert(item.id) }
                                .onDisappear { visible.remove(item.id) }
                        }
                    }
                    .padding(.horizontal, 10)
                }
                .onAppear { proxy.scrollTo(camera.currentLookID, anchor: .center) }
                .onChange(of: filter) { _, _ in
                    DispatchQueue.main.async { proxy.scrollTo(camera.currentLookID, anchor: .center) }
                }
            }

            HStack(spacing: 10) {
                Text("Intensidade").font(.caption.weight(.semibold)).opacity(0.8)
                Slider(value: $camera.lookAmount, in: 0...1, step: 0.05)
                Text("\(Int((camera.lookAmount * 100).rounded()))%")
                    .font(.system(.caption, design: .monospaced)).frame(width: 38, alignment: .trailing)
                Button(action: onMore) {
                    Image(systemName: "ellipsis.circle").font(.system(size: 20, weight: .semibold))
                        .frame(width: 36, height: 36)
                }
                .buttonStyle(.plain)
                .foregroundStyle(accent)
                .accessibilityLabel("Mais opções de filme")
            }
            .padding(.horizontal, 12)
        }
        .padding(.vertical, 10)
        .background(.black.opacity(0.62), in: RoundedRectangle(cornerRadius: 18))
        // Miniaturas ao vivo: as da tela refeitas a cada ~2 s com o que a câmera vê; as que acabaram de
        // aparecer sem imagem saem em meio segundo. Antes eram todas (31+) a cada 1,1 s, mesmo fora da tela
        .task(id: filter) {
            var tick = 0
            while !Task.isCancelled {
                refresh(full: tick % 4 == 0)
                tick += 1
                try? await Task.sleep(nanoseconds: 500_000_000)
            }
        }
    }

    /// As miniaturas na tela e 2 de cada lado (antes de ver nada, as primeiras).
    private func wantedIDs() -> [String] {
        let all = items.map(\.id)
        let shown = all.indices.filter { visible.contains(all[$0]) }
        guard let first = shown.first, let last = shown.last else { return Array(all.prefix(6)) }
        return Array(all[max(0, first - 2)...min(all.count - 1, last + 2)])
    }

    private func refresh(full: Bool) {
        // Revelar de novo aberto, sequência saindo ou iPhone quente: a revelação e o visor vêm primeiro
        guard !paused, !rendering, camera.stackProgress == nil,
              ProcessInfo.processInfo.thermalState.rawValue < ProcessInfo.ThermalState.serious.rawValue else { return }
        let wanted = wantedIDs()
        let frame = camera.renderer.enqueuedCount
        // Sem quadro novo (câmera parada) só faz as que ainda não têm imagem
        let ids = full && frame != lastFrame ? wanted : wanted.filter { thumbs[$0] == nil }
        guard !ids.isEmpty else { return }
        if full { lastFrame = frame }
        rendering = true
        camera.lookThumbnails(ids: ids) { images in
            thumbs.merge(images) { _, new in new }
            rendering = false
        }
    }

    private func thumbnail(_ item: CameraModel.LookChoice) -> some View {
        let selected = camera.currentLookID == item.id
        return Button {
            withAnimation(.snappy(duration: 0.15)) { camera.chooseLook(id: item.id) }
            UISelectionFeedbackGenerator().selectionChanged()
        } label: {
            VStack(spacing: 4) {
                ZStack {
                    RoundedRectangle(cornerRadius: 10).fill(Color.white.opacity(0.08))
                    if let image = thumbs[item.id] {
                        Image(uiImage: image).resizable().scaledToFill()
                    }
                }
                .frame(width: 62, height: 78)
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .overlay(RoundedRectangle(cornerRadius: 10).strokeBorder(selected ? accent : .clear, lineWidth: 2.5))
                Text(item.name)
                    .font(.system(size: 10, weight: selected ? .bold : .semibold))
                    .foregroundStyle(selected ? accent : Color.white.opacity(0.85))
                    .lineLimit(1).minimumScaleFactor(0.7)
                    .frame(width: 66)
            }
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Filme \(item.name)")
        .selectedTrait(selected)
    }
}

/// Telinha com todos os modos: um toque escolhe e fecha.
struct ModeGrid: View {
    @ObservedObject var camera: CameraModel
    var onOrganize: () -> Void
    @Environment(\.dismiss) private var dismiss

    private let columns = [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)]

    /// Um modo na grade, com a primeira frase da dica embaixo. Gravando ou numa sequência a troca não vale
    /// (o select avisa "Espere terminar…" e a grade fica aberta).
    private func modeCell(_ mode: CaptureMode) -> some View {
        let on = camera.captureMode == mode
        let busy = camera.isBusy
        return Button {
            camera.select(captureMode: mode)
            guard !busy || on else { return }
            UISelectionFeedbackGenerator().selectionChanged()
            dismiss()
        } label: {
            VStack(spacing: 6) {
                Image(systemName: mode.symbol).font(.system(size: 22, weight: .semibold))
                Text(mode.rawValue)
                    .font(.system(size: 12, weight: .bold)).tracking(0.4)
                    .lineLimit(1).minimumScaleFactor(0.7)
                Text(mode.shortHint)
                    .font(.system(size: 9, weight: .medium))
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .opacity(0.7)
            }
            .padding(.horizontal, 6)
            .frame(maxWidth: .infinity, minHeight: 100)
            .foregroundStyle(on ? Color.black : Color.white)
            .background(RoundedRectangle(cornerRadius: 14).fill(on ? accent : Color.white.opacity(0.08)))
        }
        .buttonStyle(.plain)
        .opacity(busy && !on ? 0.4 : 1)
        .accessibilityLabel("Modo \(mode.rawValue)")
        .accessibilityHint(mode.shortHint)
        .selectedTrait(on)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: columns, spacing: 10) {
                    ForEach(camera.visibleModes) { mode in
                        modeCell(mode)
                    }
                }
                .padding(16)
                Button {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { onOrganize() }
                } label: {
                    Label("Organizar e esconder modos", systemImage: "list.bullet")
                        .font(.footnote.weight(.semibold))
                        .frame(maxWidth: .infinity, minHeight: 44)
                }
                .buttonStyle(.plain)
                .foregroundStyle(accent)
                .padding(.bottom, 12)
            }
            .navigationTitle("Modos")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("OK") { dismiss() } } }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
}
