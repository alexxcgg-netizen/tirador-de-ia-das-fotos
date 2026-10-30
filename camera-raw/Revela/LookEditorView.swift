import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Cria ou edita um filme próprio. O visor mostra cada mudança na hora (a tela abre pela metade).
struct LookEditorView: View {
    @ObservedObject var camera: CameraModel
    @State var draft: CustomLook
    @Environment(\.dismiss) private var dismiss
    @State private var previousCustom: CustomLook?
    @State private var previousLook: Look = .portra
    @State private var saved = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    TextField("Nome do filme", text: $draft.name)
                        .font(.title3.weight(.semibold))
                        .padding(12)
                        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.08)))

                    Text("Começa do").font(.footnote.weight(.semibold)).opacity(0.7)
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(Look.allCases) { look in
                                let on = draft.base == look.rawValue
                                Button {
                                    let keepName = draft.name
                                    let id = draft.id
                                    draft = .starting(from: look)
                                    draft.id = id
                                    if !keepName.hasPrefix("Meu ") { draft.name = keepName }
                                } label: {
                                    Text(look.rawValue)
                                        .font(.footnote.weight(.semibold))
                                        .padding(.horizontal, 12).frame(height: 34)
                                        .foregroundStyle(on ? Color.black : Color.white)
                                        .background(Capsule().fill(on ? accent : Color.white.opacity(0.08)))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }

                    group("Luz e cor") {
                        slider("Exposição", $draft.exposure, -1...1, format: { String(format: "%+.1f", $0) })
                        slider("Contraste", $draft.contrast, 0.6...1.6, format: percent)
                        slider("Saturação", $draft.saturation, 0...1.8, format: percent)
                        slider("Temperatura", $draft.warmth, -1...1, format: { $0 > 0.02 ? "quente" : ($0 < -0.02 ? "frio" : "—") })
                        slider("Tom", $draft.tint, -1...1, format: { $0 > 0.02 ? "magenta" : ($0 < -0.02 ? "verde" : "—") })
                        slider("Cor das sombras", $draft.shadowColor, -1...1, format: { $0 > 0.02 ? "quente" : ($0 < -0.02 ? "azulada" : "—") })
                        slider("Preto lavado", $draft.fade, 0...1, format: percent)
                        Toggle("Preto e branco", isOn: $draft.blackAndWhite)
                    }

                    group("Textura do filme") {
                        slider("Grão", $draft.grain, 0...0.2, format: { String(format: "%.0f", $0 * 500) })
                        slider("Tamanho do grão", $draft.grainSize, 0.8...3, format: { String(format: "%.1f", $0) })
                        slider("Vinheta", $draft.vignette, 0...0.6, format: { String(format: "%.0f", $0 * 100 / 0.6) })
                        slider("Halo nas luzes", $draft.halation, 0...0.6, format: { String(format: "%.0f", $0 * 100 / 0.6) })
                        slider("Brilho suave", $draft.bloom, 0...0.5, format: { String(format: "%.0f", $0 * 200) })
                    }

                    Text("O visor já mostra o filme. Puxe a tela para cima para ver todos os ajustes.")
                        .font(.caption).opacity(0.5)
                }
                .padding(16)
            }
            .navigationTitle("Meu filme")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Cancelar") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Salvar") {
                        saved = true
                        if draft.name.trimmingCharacters(in: .whitespaces).isEmpty { draft.name = "Meu filme" }
                        camera.saveCustomLook(draft)
                        dismiss()
                    }
                    .bold()
                }
            }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
        .presentationDetents([.medium, .large])
        .presentationBackgroundInteraction(.enabled(upThrough: .medium))
        .onAppear {
            previousCustom = camera.customLook
            previousLook = camera.look
            camera.customLook = draft
        }
        .onChange(of: draft) { _, new in camera.customLook = new }
        .onDisappear {
            // Cancelou: volta ao que estava escolhido antes
            if !saved {
                camera.customLook = previousCustom
                camera.look = previousLook
            }
        }
    }

    private func percent(_ v: Float) -> String { "\(Int((v * 100).rounded()))%" }

    private func group<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title).font(.footnote.weight(.semibold)).opacity(0.7)
            content()
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.white.opacity(0.06)))
    }

    private func slider(_ label: String, _ value: Binding<Float>, _ range: ClosedRange<Float>,
                        format: @escaping (Float) -> String) -> some View {
        VStack(spacing: 2) {
            HStack {
                Text(label).font(.subheadline)
                Spacer()
                Text(format(value.wrappedValue)).font(.system(.footnote, design: .monospaced)).opacity(0.7)
            }
            Slider(value: value, in: range)
        }
    }
}
