import AVKit
import CoreMotion
import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

struct ContentView: View {
    @StateObject private var camera = CameraModel()
    @StateObject private var level = LevelMeter()
    @State private var panel: Panel?
    @State private var showReport = false
    @State private var showGuide = false
    @State private var pressingShutter = false
    @AppStorage("guideSeen") private var guideSeen = false

    enum Panel { case exposure, whiteBalance, focus, look }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            // Invisível: só para o iPhone informar o ângulo certo do visor de cada câmera
            AngleLayerView(layer: camera.angleLayer)
                .frame(width: 2, height: 2)
                .opacity(0.02)
                .allowsHitTesting(false)
            if camera.authorized {
                VStack(spacing: 10) {
                    topBar
                    viewfinder
                    readoutChips
                    controlPanel
                    lookStrip
                    Spacer(minLength: 0)
                    modePicker
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
        .onAppear {
            camera.start()
            level.start()
            if !guideSeen {
                guideSeen = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { showGuide = true }
            }
        }
        .physicalShutter(began: { camera.beginHold() }, ended: { camera.endHold() }, cancelled: { camera.cancelHold() })
        .sheet(isPresented: $showReport) { ReportView(camera: camera) }
        .sheet(isPresented: $showGuide) { GuideView() }
        .alert("Revela", isPresented: Binding(
            get: { camera.message != nil },
            set: { if !$0 { camera.message = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(camera.message ?? "")
        }
    }

    // MARK: - Topo

    private var topBar: some View {
        HStack(spacing: 8) {
            Picker("Modo", selection: Binding(get: { camera.rawMode }, set: {
                camera.select(mode: $0)
                camera.show($0 == .proRAW ? "ProRAW: 48 MP, detalhe e pouco ruído. O melhor no dia a dia."
                                          : "RAW puro: o sinal cru do sensor, 12 MP, sem nada da Apple. Mais ruído, mais controle.")
            })) {
                ForEach(RawMode.allCases) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .frame(maxWidth: 168)

            Spacer(minLength: 0)

            iconToggle(camera.timerSeconds == 0 ? "timer" : "\(camera.timerSeconds)s",
                       isSymbol: camera.timerSeconds == 0, isOn: camera.timerSeconds > 0) {
                camera.cycleTimer()
                camera.show(camera.timerSeconds == 0 ? "Timer desligado" : "Timer: a foto sai \(camera.timerSeconds) s depois de apertar")
            }
            iconToggle("circle.lefthalf.striped.horizontal", isOn: camera.zebra) {
                camera.zebra.toggle()
                camera.show(camera.zebra ? "Zebra: listras onde a luz estourou (branco sem detalhe)" : "Zebra desligada")
            }
            iconToggle("scope", isOn: camera.peaking) {
                camera.peaking.toggle()
                camera.show(camera.peaking ? "Peaking: o que está em foco fica com borda laranja" : "Peaking desligado")
            }
            iconToggle(camera.aspect.rawValue, isSymbol: false, isOn: camera.aspect != .r43) {
                camera.cycleAspect()
                camera.show("Proporção da foto: \(camera.aspect.rawValue)")
            }
            Menu {
                Button { showGuide = true } label: { Label("Guia rápido", systemImage: "questionmark.circle") }
                Toggle(isOn: $camera.showGrid) { Label("Grade de terços", systemImage: "grid") }
                Toggle(isOn: $camera.mirror) { Label("Espelhar foto (como no espelho)", systemImage: "arrow.left.and.right.righttriangle.left.righttriangle.right") }
                Toggle(isOn: $camera.saveDNG) { Label("Guardar DNG original", systemImage: "doc.badge.plus") }
                Button { showReport = true } label: { Label("Relatório para o Claude", systemImage: "doc.text.magnifyingglass") }
            } label: {
                Image(systemName: "ellipsis")
                    .frame(width: 34, height: 34)
                    .foregroundStyle(.white)
                    .background(Circle().fill(.white.opacity(0.08)))
            }
        }
        .padding(.top, 6)
    }

    private var modePicker: some View {
        VStack(spacing: 4) {
            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 18) {
                        ForEach(CaptureMode.allCases) { mode in
                            Button(mode.rawValue) {
                                withAnimation(.snappy(duration: 0.2)) {
                                    camera.select(captureMode: mode)
                                    proxy.scrollTo(mode, anchor: .center)
                                }
                                UISelectionFeedbackGenerator().selectionChanged()
                            }
                            .font(.caption.weight(.bold)).tracking(0.8)
                            .foregroundStyle(camera.captureMode == mode ? accent : Color.white.opacity(0.75))
                            .buttonStyle(.plain)
                            .id(mode)
                        }
                    }
                    .padding(.horizontal, 16)
                }
            }
            if camera.captureMode == .freeze { freezeControls }
            if !camera.captureMode.hint.isEmpty {
                Text(camera.captureMode.hint)
                    .font(.caption2).opacity(0.6)
                    .multilineTextAlignment(.center)
                    .transition(.opacity)
            }
        }
    }

    /// Velocidade do CONGELAR e o modo de máximo congelamento.
    private var freezeControls: some View {
        HStack(spacing: 6) {
            ForEach(CameraModel.freezeSpeeds, id: \.self) { speed in
                Button("1/\(Int((1 / speed).rounded()))") {
                    camera.freezeShutter = speed
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .padding(.horizontal, 7).padding(.vertical, 5)
                .foregroundStyle(camera.freezeShutter == speed ? Color.black : Color.white)
                .background(Capsule().fill(camera.freezeShutter == speed ? accent : Color.white.opacity(0.1)))
                .buttonStyle(.plain)
            }
            Button("MÁX") {
                camera.freezeMax.toggle()
                camera.show(camera.freezeMax
                            ? "Máximo congelamento: sensor no modo de 240 fps, raios menos tortos, foto de ~2 MP"
                            : "Congelamento normal: foto de 12 MP")
            }
            .font(.system(size: 11, weight: .heavy))
            .padding(.horizontal, 8).padding(.vertical, 5)
            .foregroundStyle(camera.freezeMax ? Color.black : accent)
            .background(Capsule().fill(camera.freezeMax ? accent : Color.white.opacity(0.1)))
            .buttonStyle(.plain)
        }
    }

    private func iconToggle(_ name: String, isSymbol: Bool = true, isOn: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Group {
                if isSymbol { Image(systemName: name) } else { Text(name).font(.system(size: 11, weight: .bold)).minimumScaleFactor(0.7) }
            }
            .frame(width: 34, height: 34)
            .foregroundStyle(isOn ? accent : .white)
            .background(Circle().fill(.white.opacity(isOn ? 0.16 : 0.08)))
        }
        .buttonStyle(.plain)
    }

    // MARK: - Visor

    private var viewfinder: some View {
        GeometryReader { geo in
            ZStack {
                LivePreview(renderer: camera.renderer)
                if camera.showGrid {
                    ThirdsGrid().stroke(.white.opacity(0.22), lineWidth: 0.5)
                }
                AspectMask(aspect: camera.aspect)
                LevelLine(roll: level.roll)
                if let p = camera.focusPoint {
                    FocusSquare()
                        .position(x: p.x * geo.size.width, y: p.y * geo.size.height)
                        .id(p)
                }
                if let toast = camera.toast {
                    Text(toast)
                        .font(.footnote.weight(.semibold))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(.black.opacity(0.7), in: RoundedRectangle(cornerRadius: 12))
                        .padding(.horizontal, 24)
                        .frame(maxHeight: .infinity, alignment: .top)
                        .padding(.top, 56)
                        .transition(.opacity)
                        .allowsHitTesting(false)
                        .id(toast)
                }
                VStack {
                    HStack {
                        Histogram(bins: camera.histogram)
                            .frame(width: 96, height: 40)
                        Spacer()
                        Text(camera.look.rawValue.uppercased() + " · " + statusText.replacingOccurrences(of: "\n", with: " ")
                             + (camera.mirror ? " · ESPELHO" : ""))
                            .font(.caption2.weight(.bold)).tracking(1.2)
                            .padding(.horizontal, 8).padding(.vertical, 4)
                            .background(.black.opacity(0.45), in: Capsule())
                    }
                    Spacer()
                }
                .padding(8)
                if camera.loupe {
                    Text("LUPA 4×")
                        .font(.caption2.weight(.bold)).tracking(1.2)
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(accent, in: Capsule())
                        .foregroundStyle(.black)
                        .frame(maxHeight: .infinity, alignment: .bottom)
                        .padding(.bottom, 10)
                }
                if let face = camera.faceRect, camera.stackProgress == nil {
                    let zoom = camera.lens.zoom
                    let advice = camera.distanceAdvice
                    let color: Color = advice == nil ? .white.opacity(0.6) : (advice!.good ? .green : accent)
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(color, lineWidth: 1.5)
                        .frame(width: face.width * zoom * geo.size.width, height: face.height * zoom * geo.size.height)
                        .position(x: (0.5 + (face.midX - 0.5) * zoom) * geo.size.width,
                                  y: (0.5 + (face.midY - 0.5) * zoom) * geo.size.height)
                        .animation(.easeOut(duration: 0.15), value: face)
                        .allowsHitTesting(false)
                    if let advice {
                        Label(advice.text, systemImage: advice.good ? "checkmark.circle.fill" : "figure.walk")
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .foregroundStyle(advice.good ? Color.black : Color.white)
                            .background(advice.good ? Color.green : Color.black.opacity(0.6), in: Capsule())
                            .frame(maxHeight: .infinity, alignment: .bottom)
                            .padding(.bottom, 10)
                            .allowsHitTesting(false)
                    }
                }
                if camera.lens == .macro && camera.stackProgress == nil {
                    Text("Macro: aproxime até 2 cm")
                        .font(.caption.weight(.semibold))
                        .padding(.horizontal, 10).padding(.vertical, 5)
                        .background(.black.opacity(0.5), in: Capsule())
                        .frame(maxHeight: .infinity, alignment: .bottom)
                        .padding(.bottom, camera.loupe ? 40 : 10)
                }
                if let progress = camera.stackProgress {
                    VStack(spacing: 6) {
                        ProgressView().tint(.white)
                        Text("Fotografando \(progress)").font(.subheadline.weight(.semibold))
                        Text("Não mexa o iPhone").font(.caption).opacity(0.7)
                    }
                    .padding(16)
                    .background(.black.opacity(0.55), in: RoundedRectangle(cornerRadius: 14))
                }
                if camera.actionRecording || camera.bursting || camera.lowLight {
                    HStack(spacing: 6) {
                        if camera.actionRecording {
                            Circle().fill(Color.red).frame(width: 9, height: 9)
                            Text("GRAVANDO 120 fps")
                        } else if camera.bursting {
                            Image(systemName: "square.stack.3d.down.right.fill")
                            Text("RAJADA \(camera.burstCount)")
                        } else {
                            Image(systemName: "exclamationmark.triangle.fill")
                            Text("Luz fraca: a foto vai ter ruído")
                        }
                    }
                    .font(.caption.weight(.bold))
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(.black.opacity(0.6), in: Capsule())
                    .frame(maxHeight: .infinity, alignment: .bottom)
                    .padding(.bottom, 44)
                    .allowsHitTesting(false)
                }
                if camera.countdown > 0 {
                    Text("\(camera.countdown)")
                        .font(.system(size: 96, weight: .thin, design: .rounded))
                        .contentTransition(.numericText(countsDown: true))
                        .shadow(radius: 8)
                }
                Color.white.opacity(camera.flash ? 0.85 : 0)
                    .animation(.easeOut(duration: 0.2), value: camera.flash)
                    .allowsHitTesting(false)
            }
            .contentShape(Rectangle())
            .onTapGesture(coordinateSpace: .local) { location in
                camera.focus(at: CGPoint(x: location.x / geo.size.width, y: location.y / geo.size.height))
            }
        }
        .aspectRatio(3 / 4, contentMode: .fit)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .animation(.snappy(duration: 0.25), value: camera.countdown)
        .animation(.easeOut(duration: 0.2), value: camera.toast)
    }

    // MARK: - Controles

    private var readoutChips: some View {
        HStack(spacing: 8) {
            chip(.exposure, title: "ISO \(Int(camera.manualExposure ? camera.selectedISO : camera.readoutISO))",
                 subtitle: shutterText(camera.manualExposure ? camera.selectedShutter : camera.readoutShutter),
                 isAuto: !camera.manualExposure)
            chip(.whiteBalance, title: camera.manualWB ? "\(Int(camera.kelvin))K" : "AWB",
                 subtitle: "Balanço", isAuto: !camera.manualWB)
            chip(.focus, title: camera.manualFocus ? String(format: "%.2f", camera.lensPosition) : "AF",
                 subtitle: "Foco", isAuto: !camera.manualFocus)
            chip(.look, title: "\(Int((camera.lookAmount * 100).rounded()))%",
                 subtitle: "Look", isAuto: camera.lookAmount == 1 && camera.grainAmount == 1)
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
            .foregroundStyle(isAuto ? Color.white : accent)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(panel == which ? Color.white.opacity(0.2) : Color.white.opacity(0.08))
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
                        Slider(value: $camera.lensPosition, in: 0...1) { editing in
                            withAnimation(.snappy(duration: 0.2)) { camera.loupe = editing }
                        }
                        Text("Longe").font(.caption)
                    }
                    Text("Ao arrastar, o visor amplia 4× e o peaking marca o que está em foco.")
                        .font(.caption2).opacity(0.6)
                }
            }
            .panelStyle()
        case .look:
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("Intensidade").frame(width: 80, alignment: .leading)
                    Slider(value: $camera.lookAmount, in: 0...1, step: 0.05)
                    Text("\(Int((camera.lookAmount * 100).rounded()))%")
                        .font(.system(.footnote, design: .monospaced))
                        .frame(width: 56, alignment: .trailing)
                }
                HStack {
                    Text("Grão").frame(width: 80, alignment: .leading)
                    Slider(value: $camera.grainAmount, in: 0...2, step: 0.1)
                    Text(String(format: "%.1f×", camera.grainAmount))
                        .font(.system(.footnote, design: .monospaced))
                        .frame(width: 56, alignment: .trailing)
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

    private var lookStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(Look.allCases) { look in
                    Button {
                        withAnimation(.snappy(duration: 0.2)) { camera.look = look }
                        UISelectionFeedbackGenerator().selectionChanged()
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(look.rawValue).font(.subheadline.weight(.semibold))
                            Text(look.subtitle).font(.caption2).opacity(0.65).lineLimit(1)
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .foregroundStyle(camera.look == look ? Color.black : Color.white)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(camera.look == look ? accent : Color.white.opacity(0.08))
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    // MARK: - Base

    private var lensPicker: some View {
        HStack(spacing: 8) {
            ForEach(camera.lens == .front ? [Lens.front] : camera.availableLenses) { lens in
                Button {
                    withAnimation(.snappy(duration: 0.2)) { camera.select(lens: lens) }
                    if lens == .macro { camera.show("Macro: chegue até 2 cm. O peaking liga sozinho para mostrar o que está em foco.") }
                } label: {
                    if lens == .macro {
                        Image(systemName: "camera.macro")
                    } else {
                        Text(lens.rawValue).minimumScaleFactor(0.6).lineLimit(1)
                    }
                }
                    .font(.footnote.weight(.bold))
                    .frame(width: 44, height: 44)
                    .foregroundStyle(camera.lens == lens ? accent : Color.white)
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

            // Toque = foto; segurar = rajada (RÁPIDO, CONGELAR) ou gravação (AÇÃO)
            ZStack {
                Circle().stroke(.white, lineWidth: 4).frame(width: 78, height: 78)
                Circle()
                    .fill(camera.actionRecording ? Color.red : (camera.countdown > 0 || camera.bursting ? accent : .white))
                    .frame(width: camera.actionRecording ? 34 : 64, height: camera.actionRecording ? 34 : 64)
                    .clipShape(RoundedRectangle(cornerRadius: camera.actionRecording ? 8 : 32))
            }
            .scaleEffect(pressingShutter ? 0.9 : 1)
            .animation(.spring(response: 0.2, dampingFraction: 0.6), value: pressingShutter)
            .animation(.snappy(duration: 0.2), value: camera.actionRecording)
            .contentShape(Circle())
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { _ in
                        guard !pressingShutter else { return }
                        pressingShutter = true
                        camera.beginHold()
                    }
                    .onEnded { _ in
                        pressingShutter = false
                        camera.endHold()
                    }
            )
            .accessibilityAddTraits(.isButton)
            .accessibilityLabel("Fotografar")

            Spacer()

            ZStack {
                if camera.processing > 0 {
                    VStack(spacing: 4) {
                        ProgressView().tint(.white)
                        Text("Revelando").font(.caption2).opacity(0.7)
                    }
                } else if camera.hasFront {
                    Button {
                        withAnimation(.snappy(duration: 0.25)) { camera.flipCamera() }
                        UIImpactFeedbackGenerator(style: .light).impactOccurred()
                    } label: {
                        Image(systemName: "arrow.triangle.2.circlepath")
                            .font(.title3.weight(.semibold))
                            .frame(width: 52, height: 52)
                            .foregroundStyle(camera.lens == .front ? accent : .white)
                            .background(Circle().fill(.white.opacity(0.1)))
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("Virar câmera")
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

    private var statusText: String {
        switch camera.captureMode {
        case .focusStack: return "7×\nFOCO"
        case .average: return "8×\nMÉDIA"
        case .night: return "8×\nNOITE"
        case .stars: return "16×\nCÉU"
        case .moon: return "8×\nLUA"
        case .flash: return "DNG\nFLASH"
        case .fast: return camera.rawMode == .bayer ? "RAW\n12MP" : "HEIC\n12MP"
        case .action: return "4K\n120"
        case .freeze: return camera.freezeMax ? "1/\(Int((1 / camera.freezeShutter).rounded()))\nMÁX" : "1/\(Int((1 / camera.freezeShutter).rounded()))\n12MP"
        case .photo, .portrait:
            if camera.rawMode == .bayer { return "DNG\nRAW" }
            return camera.lens.zoom > 1 ? "DNG\n12MP" : "DNG\n48MP"
        }
    }

    private func shutterText(_ seconds: Double) -> String {
        guard seconds > 0 else { return "—" }
        if seconds >= 0.5 { return String(format: "%.1fs", seconds) }
        return "1/\(Int((1 / seconds).rounded()))"
    }
}

// MARK: - Peças do visor

/// Inclinação lateral do iPhone, para a linha de nível.
final class LevelMeter: ObservableObject {
    @Published var roll: Double = 0
    private let motion = CMMotionManager()

    func start() {
        guard motion.isDeviceMotionAvailable, !motion.isDeviceMotionActive else { return }
        motion.deviceMotionUpdateInterval = 1 / 30
        motion.startDeviceMotionUpdates(to: .main) { [weak self] data, _ in
            guard let g = data?.gravity else { return }
            self?.roll = atan2(g.x, -g.y)
        }
    }
}

private struct LevelLine: View {
    let roll: Double
    @State private var wasLevel = false

    private var isLevel: Bool { abs(roll) < 1 * .pi / 180 }

    var body: some View {
        HStack(spacing: 0) {
            Rectangle().frame(width: 40, height: 1.5)
            Spacer().frame(width: 36)
            Rectangle().frame(width: 40, height: 1.5)
        }
        .foregroundStyle(isLevel ? accent : Color.white.opacity(0.7))
        .rotationEffect(.radians(-roll))
        .opacity(abs(roll) < 20 * .pi / 180 ? 1 : 0)
        .onChange(of: isLevel) { _, level in
            if level { UISelectionFeedbackGenerator().selectionChanged() }
        }
        .allowsHitTesting(false)
    }
}

/// Escurece o que fica fora da proporção escolhida.
private struct AspectMask: View {
    let aspect: AspectRatio

    var body: some View {
        GeometryReader { geo in
            let rect = aspect.crop(CGRect(origin: .zero, size: geo.size), zoom: 1)
            Path { p in
                p.addRect(CGRect(origin: .zero, size: geo.size))
                p.addRect(rect)
            }
            .fill(Color.black.opacity(0.6), style: FillStyle(eoFill: true))
            .animation(.snappy(duration: 0.25), value: aspect)
        }
        .allowsHitTesting(false)
    }
}

private struct FocusSquare: View {
    @State private var settled = false

    var body: some View {
        RoundedRectangle(cornerRadius: 3)
            .stroke(accent, lineWidth: 1.5)
            .frame(width: 72, height: 72)
            .scaleEffect(settled ? 1 : 1.35)
            .opacity(settled ? 1 : 0.3)
            .onAppear { withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) { settled = true } }
            .allowsHitTesting(false)
    }
}

private struct Histogram: View {
    let bins: [Float]

    var body: some View {
        Canvas { ctx, size in
            guard bins.count > 1 else { return }
            var path = Path()
            path.move(to: CGPoint(x: 0, y: size.height))
            for (i, v) in bins.enumerated() {
                let x = size.width * CGFloat(i) / CGFloat(bins.count - 1)
                path.addLine(to: CGPoint(x: x, y: size.height * (1 - CGFloat(min(v, 1)))))
            }
            path.addLine(to: CGPoint(x: size.width, y: size.height))
            path.closeSubpath()
            ctx.fill(path, with: .color(.white.opacity(0.75)))
        }
        .padding(4)
        .background(.black.opacity(0.45), in: RoundedRectangle(cornerRadius: 6))
        .allowsHitTesting(false)
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
            .tint(accent)
            .padding(12)
            .background(RoundedRectangle(cornerRadius: 12).fill(.white.opacity(0.08)))
            .transition(.opacity.combined(with: .move(edge: .top)))
    }

    /// Volume e Controle da Câmera: apertar e soltar como o botão da tela (iOS 18+).
    @ViewBuilder
    func physicalShutter(began: @escaping () -> Void, ended: @escaping () -> Void,
                         cancelled: @escaping () -> Void) -> some View {
        if #available(iOS 18.0, *) {
            onCameraCaptureEvent { event in
                switch event.phase {
                case .began: began()
                case .ended: ended()
                default: cancelled()
                }
            }
        } else {
            self
        }
    }
}

/// Hospeda a camada invisível do visor, usada só pelo RotationCoordinator.
private struct AngleLayerView: UIViewRepresentable {
    let layer: AVCaptureVideoPreviewLayer

    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        view.layer.addSublayer(layer)
        layer.frame = CGRect(x: 0, y: 0, width: 2, height: 2)
        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {}
}
