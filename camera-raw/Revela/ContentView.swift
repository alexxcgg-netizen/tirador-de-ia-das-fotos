import SwiftUI

struct ContentView: View {
    @StateObject private var camera = CameraModel()
    @State private var panel: Panel?

    enum Panel { case exposure, whiteBalance, focus }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            if camera.authorized {
                VStack(spacing: 12) {
                    topBar
                    CameraPreview(session: camera.session)
                        .aspectRatio(3 / 4, contentMode: .fit)
                        .clipShape(RoundedRectangle(cornerRadius: 6))
                        .overlay { ThirdsGrid().stroke(.white.opacity(0.18), lineWidth: 0.5) }
                    readoutChips
                    controlPanel
                    Spacer(minLength: 0)
                    lensPicker
                    bottomBar
                }
                .padding(.horizontal, 12)
                .padding(.bottom, 8)
            } else {
                noAccess
            }
        }
        .preferredColorScheme(.dark)
        .statusBarHidden()
        .onAppear { camera.start() }
        .alert("Revela", isPresented: Binding(
            get: { camera.message != nil },
            set: { if !$0 { camera.message = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(camera.message ?? "")
        }
    }

    // MARK: - Partes da tela

    private var topBar: some View {
        HStack {
            Picker("Modo", selection: Binding(get: { camera.rawMode }, set: { camera.select(mode: $0) })) {
                ForEach(RawMode.allCases) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .frame(maxWidth: 200)

            Spacer()

            Menu {
                Picker("Look", selection: $camera.look) {
                    ForEach(Look.allCases) { look in
                        Text(look.rawValue).tag(look)
                    }
                }
            } label: {
                Label(camera.look.rawValue, systemImage: "camera.filters")
                    .font(.subheadline.weight(.semibold))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(.white.opacity(0.12), in: Capsule())
            }
        }
        .padding(.top, 8)
    }

    private var readoutChips: some View {
        HStack(spacing: 8) {
            chip(.exposure, title: "ISO \(Int(camera.manualExposure ? camera.selectedISO : camera.readoutISO))",
                 subtitle: shutterText(camera.manualExposure ? camera.selectedShutter : camera.readoutShutter),
                 isAuto: !camera.manualExposure)
            chip(.whiteBalance, title: camera.manualWB ? "\(Int(camera.kelvin))K" : "AWB",
                 subtitle: "Balanço", isAuto: !camera.manualWB)
            chip(.focus, title: camera.manualFocus ? String(format: "%.2f", camera.lensPosition) : "AF",
                 subtitle: "Foco", isAuto: !camera.manualFocus)
        }
    }

    private func chip(_ which: Panel, title: String, subtitle: String, isAuto: Bool) -> some View {
        Button {
            withAnimation(.snappy(duration: 0.25)) { panel = panel == which ? nil : which }
        } label: {
            VStack(spacing: 2) {
                Text(title).font(.system(.subheadline, design: .monospaced).weight(.semibold))
                Text(subtitle).font(.caption2).opacity(0.7)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
            .foregroundStyle(isAuto ? Color.white : Color.yellow)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(panel == which ? Color.white.opacity(0.22) : Color.white.opacity(0.08))
            )
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private var controlPanel: some View {
        switch panel {
        case .exposure:
            VStack(alignment: .leading, spacing: 8) {
                Toggle("Exposição manual", isOn: $camera.manualExposure)
                if camera.manualExposure {
                    sliderRow("ISO", value: $camera.isoIndex,
                              range: 0...Double(max(camera.isoStops.count - 1, 1)),
                              text: "\(Int(camera.selectedISO))")
                    sliderRow("Obturador", value: $camera.shutterIndex,
                              range: 0...Double(max(camera.shutterStops.count - 1, 1)),
                              text: shutterText(camera.selectedShutter))
                } else {
                    HStack {
                        Text("EV").frame(width: 80, alignment: .leading)
                        Slider(value: $camera.evBias, in: -3...3, step: 1 / 3)
                        Text(String(format: "%+.1f", camera.evBias))
                            .font(.system(.footnote, design: .monospaced))
                            .frame(width: 56, alignment: .trailing)
                    }
                }
            }
            .panelStyle()
        case .whiteBalance:
            VStack(alignment: .leading, spacing: 8) {
                Toggle("Balanço manual", isOn: $camera.manualWB)
                if camera.manualWB {
                    HStack {
                        Text("Kelvin").frame(width: 80, alignment: .leading)
                        Slider(value: $camera.kelvin, in: 2500...10000, step: 100)
                        Text("\(Int(camera.kelvin))K")
                            .font(.system(.footnote, design: .monospaced))
                            .frame(width: 56, alignment: .trailing)
                    }
                }
            }
            .panelStyle()
        case .focus:
            VStack(alignment: .leading, spacing: 8) {
                Toggle("Foco manual", isOn: $camera.manualFocus)
                if camera.manualFocus {
                    HStack {
                        Text("Perto").font(.caption)
                        Slider(value: $camera.lensPosition, in: 0...1)
                        Text("Longe").font(.caption)
                    }
                }
            }
            .panelStyle()
        case nil:
            EmptyView()
        }
    }

    private func sliderRow(_ label: String, value: Binding<Double>, range: ClosedRange<Double>, text: String) -> some View {
        HStack {
            Text(label).frame(width: 80, alignment: .leading)
            Slider(value: value, in: range, step: 1)
            Text(text)
                .font(.system(.footnote, design: .monospaced))
                .frame(width: 56, alignment: .trailing)
        }
    }

    private var lensPicker: some View {
        HStack(spacing: 10) {
            ForEach(camera.availableLenses) { lens in
                Button(lens.rawValue) { camera.select(lens: lens) }
                    .font(.footnote.weight(.bold))
                    .frame(width: 44, height: 44)
                    .foregroundStyle(camera.lens == lens ? Color.yellow : Color.white)
                    .background(Circle().fill(.white.opacity(camera.lens == lens ? 0.2 : 0.08)))
                    .buttonStyle(.plain)
            }
        }
    }

    private var bottomBar: some View {
        HStack {
            Button {
                if let url = URL(string: "photos-redirect://") { UIApplication.shared.open(url) }
            } label: {
                Group {
                    if let thumb = camera.thumbnail {
                        Image(uiImage: thumb).resizable().scaledToFill()
                    } else {
                        Color.white.opacity(0.1)
                    }
                }
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }
            .buttonStyle(.plain)

            Spacer()

            Button(action: camera.capture) {
                ZStack {
                    Circle().stroke(.white, lineWidth: 4).frame(width: 78, height: 78)
                    Circle().fill(.white).frame(width: 64, height: 64)
                }
            }
            .buttonStyle(ShutterButtonStyle())

            Spacer()

            ZStack {
                if camera.processing > 0 {
                    VStack(spacing: 4) {
                        ProgressView().tint(.white)
                        Text("Revelando").font(.caption2).opacity(0.7)
                    }
                }
            }
            .frame(width: 56, height: 56)
        }
        .padding(.horizontal, 8)
    }

    private var noAccess: some View {
        VStack(spacing: 12) {
            Image(systemName: "camera.fill").font(.largeTitle)
            Text("O Revela precisa da câmera.").font(.headline)
            Text("Libere em Ajustes → Revela → Câmera.").font(.subheadline).opacity(0.7)
            Button("Abrir Ajustes") {
                if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
            }
            .buttonStyle(.borderedProminent)
        }
        .foregroundStyle(.white)
        .padding()
    }

    private func shutterText(_ seconds: Double) -> String {
        guard seconds > 0 else { return "—" }
        if seconds >= 0.5 { return String(format: "%.1fs", seconds) }
        return "1/\(Int((1 / seconds).rounded()))"
    }
}

private struct ShutterButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.9 : 1)
            .animation(.spring(response: 0.2, dampingFraction: 0.6), value: configuration.isPressed)
    }
}

private struct ThirdsGrid: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        for i in 1...2 {
            let x = rect.minX + rect.width * CGFloat(i) / 3
            let y = rect.minY + rect.height * CGFloat(i) / 3
            path.move(to: CGPoint(x: x, y: rect.minY))
            path.addLine(to: CGPoint(x: x, y: rect.maxY))
            path.move(to: CGPoint(x: rect.minX, y: y))
            path.addLine(to: CGPoint(x: rect.maxX, y: y))
        }
        return path
    }
}

private extension View {
    func panelStyle() -> some View {
        self
            .font(.subheadline)
            .tint(.yellow)
            .padding(12)
            .background(RoundedRectangle(cornerRadius: 12).fill(.white.opacity(0.08)))
            .transition(.opacity.combined(with: .move(edge: .top)))
    }
}
