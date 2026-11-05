import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Faixa de filmes em cima do visor: cada filme aparece com o que a câmera está vendo agora.
/// Um toque troca o filme e o visor já mostra; não precisa abrir lista nem voltar.
struct LookStrip: View {
    @ObservedObject var camera: CameraModel
    var onMore: () -> Void

    /// "todos", "meus" ou o nome de um tipo (Cor, Fuji…).
    @AppStorage("lookStripFilter") private var filter = "todos"
    @State private var thumbs: [String: UIImage] = [:]

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
                    }
                }
                .padding(.horizontal, 10)
            }

            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(items) { item in
                            thumbnail(item)
                                .id(item.id)
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
        // Miniaturas ao vivo: refeitas a cada segundo com o que a câmera vê
        .task(id: filter) {
            while !Task.isCancelled {
                refresh()
                try? await Task.sleep(nanoseconds: 1_100_000_000)
            }
        }
    }

    private func refresh() {
        camera.lookThumbnails(ids: items.map(\.id)) { images in
            thumbs.merge(images) { _, new in new }
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
    }
}

/// Telinha com todos os modos: um toque escolhe e fecha.
struct ModeGrid: View {
    @ObservedObject var camera: CameraModel
    var onOrganize: () -> Void
    @Environment(\.dismiss) private var dismiss

    private let columns = [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)]

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: columns, spacing: 10) {
                    ForEach(camera.visibleModes) { mode in
                        let on = camera.captureMode == mode
                        Button {
                            camera.select(captureMode: mode)
                            UISelectionFeedbackGenerator().selectionChanged()
                            dismiss()
                        } label: {
                            VStack(spacing: 8) {
                                Image(systemName: mode.symbol).font(.system(size: 22, weight: .semibold))
                                Text(mode.rawValue)
                                    .font(.system(size: 12, weight: .bold)).tracking(0.4)
                                    .lineLimit(1).minimumScaleFactor(0.7)
                            }
                            .frame(maxWidth: .infinity, minHeight: 76)
                            .foregroundStyle(on ? Color.black : Color.white)
                            .background(RoundedRectangle(cornerRadius: 14).fill(on ? accent : Color.white.opacity(0.08)))
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel("Modo \(mode.rawValue)")
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
