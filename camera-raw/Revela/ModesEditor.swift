import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Escolhe quais modos aparecem na fileira e em que ordem (arraste pelas três listras).
struct ModesEditor: View {
    @ObservedObject var camera: CameraModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section {
                    ForEach(camera.modeOrder) { mode in
                        Toggle(isOn: Binding(
                            get: { !camera.hiddenModes.contains(mode) },
                            set: { on in
                                if on { camera.hiddenModes.remove(mode) } else { camera.hiddenModes.insert(mode) }
                                camera.saveModes()
                            })) {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(mode.rawValue).font(.body.weight(.semibold))
                                if !mode.hint.isEmpty {
                                    Text(mode.hint).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                                }
                            }
                        }
                        .disabled(mode == .photo)
                    }
                    .onMove { from, to in
                        camera.modeOrder.move(fromOffsets: from, toOffset: to)
                        camera.saveModes()
                    }
                } footer: {
                    Text("Desligue os modos que você não usa. Arraste pelas listras para mudar a ordem. FOTO fica sempre.")
                }
                Section {
                    Button("Voltar ao padrão") {
                        camera.modeOrder = CaptureMode.allCases
                        camera.hiddenModes = []
                        camera.saveModes()
                    }
                }
            }
            .environment(\.editMode, .constant(.active))
            .navigationTitle("Modos")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("OK") { dismiss() } } }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
    }
}
