import SwiftUI

@main
struct RevelaApp: App {
    @State private var safeMode = LaunchGuard.begin()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            if safeMode {
                SafeModeView { safeMode = false }
            } else {
                ContentView()
            }
        }
        .onChange(of: scenePhase) { _, phase in
            // Fechar o app de propósito não conta como travamento
            if phase == .background { LaunchGuard.markStable() }
        }
    }
}

/// Aparece quando o app fechou sozinho ao abrir: deixa mandar o relatório sem ligar a câmera.
struct SafeModeView: View {
    let openCamera: () -> Void
    @State private var showReport = false

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 44))
                .foregroundStyle(Color(red: 0.96, green: 0.64, blue: 0.24))
            Text("O Revela fechou da última vez")
                .font(.title3.weight(.bold))
            Text("Abri sem ligar a câmera. Mande o relatório para o Claude: ele mostra onde o app parou.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            Button {
                showReport = true
            } label: {
                Label("Ver e mandar o relatório", systemImage: "doc.text.magnifyingglass")
                    .frame(maxWidth: .infinity, minHeight: 48)
            }
            .buttonStyle(.borderedProminent)
            Button {
                LaunchGuard.markStable()
                openCamera()
            } label: {
                Text("Tentar abrir a câmera").frame(maxWidth: .infinity, minHeight: 48)
            }
            .buttonStyle(.bordered)
        }
        .padding(24)
        .tint(Color(red: 0.96, green: 0.64, blue: 0.24))
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showReport) { ReportView(camera: nil) }
    }
}
