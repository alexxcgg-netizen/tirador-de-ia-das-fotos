import SwiftUI

/// Tela do relatório: a pessoa escreve o que notou, e compartilha o texto com o Claude.
struct ReportView: View {
    /// nil no modo seguro (a câmera não foi ligada).
    var camera: CameraModel?
    @Environment(\.dismiss) private var dismiss
    @State private var note = ""
    @State private var report = ""
    @State private var fileURL: URL?
    @State private var copied = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Text("Escreva o que você notou (o que funcionou, o que ficou estranho, o que quer diferente). Depois compartilhe e mande para o Claude.")
                        .font(.subheadline).foregroundStyle(.secondary)

                    TextField("Ex.: o macro não focou no cabelo, a foto da lua saiu clara…", text: $note, axis: .vertical)
                        .lineLimit(3...8)
                        .padding(12)
                        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.08)))

                    HStack(spacing: 10) {
                        if let fileURL {
                            ShareLink(item: fileURL) {
                                Label("Compartilhar", systemImage: "square.and.arrow.up")
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        Button {
                            UIPasteboard.general.string = report
                            copied = true
                        } label: {
                            Label(copied ? "Copiado" : "Copiar", systemImage: copied ? "checkmark" : "doc.on.doc")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                    }

                    Text(report.isEmpty ? "Montando o relatório…" : report)
                        .font(.system(size: 11, design: .monospaced))
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.05)))

                    Button("Limpar registro", role: .destructive) {
                        Diagnostics.shared.clear()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { build() }
                    }
                    .font(.footnote)
                }
                .padding()
            }
            .navigationTitle("Relatório")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("OK") { dismiss() } }
            }
        }
        .tint(Color(red: 0.96, green: 0.64, blue: 0.24))
        .onAppear(perform: build)
        .onChange(of: note) { _, _ in build() }
    }

    private func build() {
        copied = false
        let describe: (@escaping (String) -> Void) -> Void = { done in
            if let camera { camera.describeCapabilities(completion: done) } else { done("(modo seguro: câmera não ligada)\n") }
        }
        describe { cameraText in
            Diagnostics.shared.report(note: note, camera: cameraText) { text in
                report = text
                let url = FileManager.default.temporaryDirectory.appendingPathComponent("relatorio-revela.md")
                try? text.write(to: url, atomically: true, encoding: .utf8)
                fileURL = url
            }
        }
    }
}
