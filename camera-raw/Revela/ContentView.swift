import AVKit
import CoreMotion
import SwiftUI

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)
private let panelFill = Color(white: 0.11)
private let panelOn = Color(white: 0.23)

struct ContentView: View {
    @StateObject private var camera = CameraModel()
    @StateObject private var level = LevelMeter()
    @State private var showSettings = false
    @State private var showLooks = false
    @State private var showReport = false
    @State private var showGuide = false
    @State private var pressingShutter = false
    @State private var pinchStart: CGFloat?
    @AppStorage("guideSeen") private var guideSeen = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            if camera.authorized {
                VStack(spacing: 14) {
                    topBar
                    viewfinder
                    lensPicker
                    modePicker
                    Spacer(minLength: 0)
                    bottomBar
                }
                .padding(.horizontal, 16)
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
        .sheet(isPresented: $showSettings) { settingsSheet }
        .sheet(isPresented: $showLooks) { looksSheet }
        .sheet(isPresented: $showReport) { ReportView(camera: camera) }
        .fullScreenCover(isPresented: $camera.showScanner, onDismiss: { camera.scannerClosed() }) { ScannerView() }
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

    // MARK: - Topo: look, proporção e Ajustes

    private var anyManual: Bool {
        camera.manualExposure || camera.manualFocus || camera.manualWB
    }

    private var topBar: some View {
        HStack(spacing: 10) {
            Button { showLooks = true } label: {
                HStack(spacing: 8) {
                    Image(systemName: "camera.filters").foregroundStyle(accent)
                    Text(camera.look.rawValue).font(.body.weight(.semibold)).lineLimit(1)
                }
                .padding(.horizontal, 18)
                .frame(height: 48)
                .background(Capsule().fill(panelFill))
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Look: \(camera.look.rawValue)")

            Spacer(minLength: 0)

            Button {
                camera.cycleAspect()
                camera.show("Proporção da foto: \(camera.aspect.rawValue)")
            } label: {
                Text(camera.aspect.rawValue)
                    .font(.system(size: 14, weight: .bold))
                    .minimumScaleFactor(0.7)
                    .frame(width: 48, height: 48)
                    .foregroundStyle(camera.aspect == .r43 ? Color.white : accent)
                    .background(Circle().fill(panelFill))
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Proporção \(camera.aspect.rawValue)")

            Button { showSettings = true } label: {
                Image(systemName: "slider.horizontal.3")
                    .font(.system(size: 19, weight: .semibold))
                    .frame(width: 48, height: 48)
                    .foregroundStyle(anyManual ? accent : Color.white)
                    .background(Circle().fill(panelFill))
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Ajustes")
        }
        .padding(.top, 6)
    }

    // MARK: - Lentes e modos

    /// Zooms do dia a dia ficam à vista; 8× e Macro ficam no "···". Pinça no visor faz qualquer zoom entre eles.
    private var zoomPresets: [CGFloat] {
        var presets: [CGFloat] = []
        if camera.availableLenses.contains(.ultraWide) { presets.append(0.5) }
        presets += [1, 2]
        if camera.availableLenses.contains(.tele) { presets.append(4) }
        return presets
    }

    private func zoomLabel(_ z: CGFloat) -> String {
        z == 0.5 ? "0,5×" : "\(Int(z))×"
    }

    private func isCurrent(_ z: CGFloat) -> Bool {
        camera.lens != .macro && abs(camera.zoom - z) < 0.05
    }

    private var lensPicker: some View {
        HStack(spacing: 12) {
            if camera.lens == .front {
                ForEach([CGFloat(1), 2], id: \.self) { z in zoomButton(z) }
            } else {
                ForEach(zoomPresets, id: \.self) { z in zoomButton(z) }
                let extraOn = camera.lens == .macro || isCurrent(8)
                Menu {
                    if camera.availableLenses.contains(.tele) {
                        Button { withAnimation(.snappy(duration: 0.2)) { camera.setZoom(8) } } label: {
                            Label("8× (tele recortada)", systemImage: "plus.magnifyingglass")
                        }
                    }
                    if camera.availableLenses.contains(.macro) {
                        Button {
                            withAnimation(.snappy(duration: 0.2)) { camera.select(lens: .macro) }
                            camera.show("Macro: chegue até 2 cm. O peaking liga sozinho para mostrar o que está em foco.")
                        } label: {
                            Label("Macro (até 2 cm)", systemImage: "camera.macro")
                        }
                    }
                } label: {
                    Group {
                        if camera.lens == .macro { Image(systemName: "camera.macro") }
                        else if isCurrent(8) { Text("8×") }
                        else { Text("···") }
                    }
                    .font(.system(size: 15, weight: .bold))
                    .frame(width: 52, height: 52)
                    .foregroundStyle(extraOn ? accent : Color.white)
                    .background(Circle().fill(extraOn ? panelOn : panelFill))
                }
                .accessibilityLabel("Mais lentes")
            }
        }
    }

    /// Este botão mostra o zoom atual? (o exato, ou o mais perto quando a pinça parou entre dois)
    private func showsCurrentZoom(_ z: CGFloat) -> Bool {
        if camera.lens == .macro { return false }
        if isCurrent(z) { return true }
        let anyExact = zoomPresets.contains { isCurrent($0) }
        return !anyExact && nearestPreset == z
    }

    private func zoomButton(_ z: CGFloat) -> some View {
        let current: Bool = showsCurrentZoom(z)
        let title: String = current ? camera.zoomText : zoomLabel(z)
        let fill: Color = isCurrent(z) ? panelOn : panelFill
        return Button {
            withAnimation(.snappy(duration: 0.2)) {
                if camera.lens == .macro { camera.select(lens: .wide) }
                camera.setZoom(z)
            }
        } label: {
            Text(title)
                .font(.system(size: 15, weight: .bold))
                .minimumScaleFactor(0.6).lineLimit(1)
                .frame(width: 52, height: 52)
                .foregroundStyle(current ? accent : Color.white)
                .background(Circle().fill(fill))
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Zoom \(zoomLabel(z))")
    }

    /// O botão mais perto do zoom atual mostra o valor exato (ex.: 2,7×) quando você usa a pinça.
    private var nearestPreset: CGFloat {
        let presets = camera.lens == .front ? [CGFloat(1), 2] : zoomPresets
        return presets.last(where: { $0 <= camera.zoom + 0.01 }) ?? presets.first ?? 1
    }

    private var modePicker: some View {
        VStack(spacing: 6) {
            ScrollViewReader { proxy in
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 22) {
                        ForEach(CaptureMode.allCases) { mode in
                            Button(mode.rawValue) {
                                withAnimation(.snappy(duration: 0.2)) {
                                    camera.select(captureMode: mode)
                                    proxy.scrollTo(mode, anchor: .center)
                                }
                                UISelectionFeedbackGenerator().selectionChanged()
                            }
                            .font(.system(size: 15, weight: .bold)).tracking(0.6)
                            .foregroundStyle(camera.captureMode == mode ? accent : Color.white.opacity(0.7))
                            .frame(minHeight: 36)
                            .buttonStyle(.plain)
                            .id(mode)
                        }
                    }
                    .padding(.horizontal, 20)
                }
                .onAppear { proxy.scrollTo(camera.captureMode, anchor: .center) }
            }
            if camera.captureMode == .freeze { freezeControls }
            if camera.captureMode == .portrait { apertureControls }
            if camera.captureMode == .night { nightControls }
            if camera.captureMode == .longExposure { longControls }
            if camera.captureMode == .video { videoControls }
            if camera.captureMode == .cinematic { cinematicControls }
            if !camera.captureMode.hint.isEmpty {
                Text(camera.captureMode.hint)
                    .font(.caption).opacity(0.6)
                    .multilineTextAlignment(.center)
                    .transition(.opacity)
            }
        }
    }

    /// Retrato: quanto borrar o fundo, como a abertura de uma lente.
    private var apertureControls: some View {
        HStack(spacing: 6) {
            ForEach(CameraModel.apertures, id: \.self) { f in
                Button(apertureLabel(f)) {
                    camera.portraitAperture = f
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .padding(.horizontal, 8).frame(height: 36)
                .foregroundStyle(camera.portraitAperture == f ? Color.black : Color.white)
                .background(Capsule().fill(camera.portraitAperture == f ? accent : panelFill))
                .buttonStyle(.plain)
            }
        }
    }

    private func apertureLabel(_ f: Float) -> String {
        if f == f.rounded() { return "f/\(Int(f))" }
        return "f/" + String(format: "%.1f", f).replacingOccurrences(of: ".", with: ",")
    }

    /// Vídeo: quadros por segundo.
    private var videoControls: some View {
        HStack(spacing: 6) {
            ForEach(CameraModel.videoRates, id: \.self) { fps in
                Button("\(fps) fps") {
                    camera.setVideoFPS(fps)
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 12, weight: .bold))
                .padding(.horizontal, 10).frame(height: 36)
                .foregroundStyle(camera.videoFPS == fps ? Color.black : Color.white)
                .background(Capsule().fill(camera.videoFPS == fps ? accent : panelFill))
                .buttonStyle(.plain)
                .disabled(camera.isRecordingVideo)
            }
            Text("1080p").font(.caption.weight(.bold)).foregroundStyle(.secondary)
        }
    }

    /// Cinema: quanto desfocar o fundo (dentro do que a câmera aceita).
    private var cinematicControls: some View {
        HStack(spacing: 6) {
            ForEach([Float(2), 2.8, 4, 5.6, 8, 16].filter { camera.cinematicRange.contains($0) }, id: \.self) { f in
                Button(apertureLabel(f)) {
                    camera.setCinematicAperture(f)
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .padding(.horizontal, 8).frame(height: 36)
                .foregroundStyle(camera.cinematicAperture == f ? Color.black : Color.white)
                .background(Capsule().fill(camera.cinematicAperture == f ? accent : panelFill))
                .buttonStyle(.plain)
                .disabled(camera.isRecordingVideo)
            }
        }
    }

    /// Exposição longa: duração e estilo.
    private var longControls: some View {
        HStack(spacing: 6) {
            ForEach(CameraModel.longSeconds, id: \.self) { sec in
                Button("\(Int(sec)) s") {
                    camera.longSecondsChoice = sec
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 12, weight: .bold))
                .padding(.horizontal, 9).frame(height: 36)
                .foregroundStyle(camera.longSecondsChoice == sec ? Color.black : Color.white)
                .background(Capsule().fill(camera.longSecondsChoice == sec ? accent : panelFill))
                .buttonStyle(.plain)
            }
            ForEach(LongExposure.Style.allCases) { style in
                Button(style.rawValue) {
                    camera.longStyle = style
                    UISelectionFeedbackGenerator().selectionChanged()
                }
                .font(.system(size: 12, weight: .bold))
                .padding(.horizontal, 10).frame(height: 36)
                .foregroundStyle(camera.longStyle == style ? Color.black : Color.white)
                .background(Capsule().fill(camera.longStyle == style ? accent : panelFill))
                .buttonStyle(.plain)
            }
        }
    }

    /// Noite: tempo de cada foto e quantas fotos somar.
    private var nightControls: some View {
        VStack(spacing: 6) {
            HStack(spacing: 6) {
                ForEach(NightTime.allCases) { t in
                    Button(t.rawValue) {
                        camera.nightTime = t
                        UISelectionFeedbackGenerator().selectionChanged()
                    }
                    .font(.system(size: 12, weight: .bold))
                    .padding(.horizontal, 9).frame(height: 36)
                    .foregroundStyle(camera.nightTime == t ? Color.black : Color.white)
                    .background(Capsule().fill(camera.nightTime == t ? accent : panelFill))
                    .buttonStyle(.plain)
                }
            }
            HStack(spacing: 6) {
                ForEach([4, 8, 16], id: \.self) { n in
                    Button("\(n) fotos") {
                        camera.nightFrames = n
                        UISelectionFeedbackGenerator().selectionChanged()
                    }
                    .font(.system(size: 12, weight: .bold))
                    .padding(.horizontal, 9).frame(height: 36)
                    .foregroundStyle(camera.nightFrames == n ? Color.black : Color.white)
                    .background(Capsule().fill(camera.nightFrames == n ? accent : panelFill))
                    .buttonStyle(.plain)
                }
                Label(camera.isSteady ? "Apoiado" : "Na mão", systemImage: camera.isSteady ? "checkmark.circle.fill" : "hand.raised.fill")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(camera.isSteady ? Color.green : Color.white.opacity(0.7))
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
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .padding(.horizontal, 8).frame(height: 36)
                .foregroundStyle(camera.freezeShutter == speed ? Color.black : Color.white)
                .background(Capsule().fill(camera.freezeShutter == speed ? accent : panelFill))
                .buttonStyle(.plain)
            }
            Button("MÁX") {
                camera.freezeMax.toggle()
                camera.show(camera.freezeMax
                            ? "Máximo congelamento: sensor no modo de 240 fps, raios menos tortos, foto de ~2 MP"
                            : "Congelamento normal: foto de 12 MP")
            }
            .font(.system(size: 12, weight: .heavy))
            .padding(.horizontal, 10).frame(height: 36)
            .foregroundStyle(camera.freezeMax ? Color.black : accent)
            .background(Capsule().fill(camera.freezeMax ? accent : panelFill))
            .buttonStyle(.plain)
        }
    }

    // MARK: - Visor

    private var viewfinder: some View {
        GeometryReader { geo in
            ZStack {
                // Visor do sistema: escondido (serve para o iPhone informar o ângulo de cada câmera);
                // no modo CINEMÁTICO é ele que aparece, porque só ele mostra o desfoque ao vivo
                AngleLayerView(layer: camera.angleLayer)
                    .opacity(camera.captureMode == .cinematic ? 1 : 0.02)
                    .allowsHitTesting(false)
                LivePreview(renderer: camera.renderer)
                    .opacity(camera.captureMode == .cinematic ? 0 : 1)
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
                        Histogram(bins: camera.histogram, rgb: camera.rgbHistogram ? camera.histogramRGB : [])
                            .frame(width: 96, height: 40)
                        Spacer()
                        VStack(alignment: .trailing, spacing: 4) {
                            Text(statusText.replacingOccurrences(of: "\n", with: " ") + (camera.mirror ? " · ESPELHO" : ""))
                                .font(.caption2.weight(.bold)).tracking(1.2)
                                .padding(.horizontal, 8).padding(.vertical, 4)
                                .background(.black.opacity(0.45), in: Capsule())
                            if anyManual {
                                Text(manualSummary)
                                    .font(.caption2.weight(.bold))
                                    .foregroundStyle(accent)
                                    .padding(.horizontal, 8).padding(.vertical, 4)
                                    .background(.black.opacity(0.45), in: Capsule())
                            }
                        }
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
                    let zoom = camera.crop
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
                        Text(camera.captureMode == .longExposure ? "Expondo · faltam \(progress)" : "Fotografando \(progress)")
                            .font(.subheadline.weight(.semibold))
                        Text("Não mexa o iPhone").font(.caption).opacity(0.7)
                    }
                    .padding(16)
                    .background(.black.opacity(0.55), in: RoundedRectangle(cornerRadius: 14))
                }
                if let started = camera.recordingStarted {
                    TimelineView(.periodic(from: started, by: 1)) { context in
                        let seconds = Int(context.date.timeIntervalSince(started))
                        HStack(spacing: 6) {
                            Circle().fill(Color.red).frame(width: 9, height: 9)
                            Text(String(format: "REC %02d:%02d", seconds / 60, seconds % 60))
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                        }
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(.black.opacity(0.6), in: Capsule())
                    }
                    .frame(maxHeight: .infinity, alignment: .top)
                    .padding(.top, 52)
                    .allowsHitTesting(false)
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
            .overlay {
                if pinchStart != nil {
                    Text(camera.zoomText)
                        .font(.system(size: 22, weight: .bold, design: .rounded))
                        .padding(.horizontal, 14).padding(.vertical, 8)
                        .background(.black.opacity(0.6), in: Capsule())
                        .allowsHitTesting(false)
                }
            }
            .contentShape(Rectangle())
            .simultaneousGesture(
                MagnificationGesture()
                    .onChanged { scale in
                        if pinchStart == nil { pinchStart = camera.zoom }
                        camera.setZoom((pinchStart ?? 1) * scale, settle: false)
                    }
                    .onEnded { _ in
                        pinchStart = nil
                        camera.setZoom(camera.zoom, settle: true)
                    }
            )
            .onTapGesture(coordinateSpace: .local) { location in
                camera.focus(at: CGPoint(x: location.x / geo.size.width, y: location.y / geo.size.height))
            }
        }
        .aspectRatio(3 / 4, contentMode: .fit)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .animation(.snappy(duration: 0.25), value: camera.countdown)
        .animation(.easeOut(duration: 0.2), value: camera.toast)
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

    private var bottomBar: some View {
        HStack {
            Button {
                if let url = URL(string: "photos-redirect://") { UIApplication.shared.open(url) }
            } label: {
                ZStack {
                    if let thumb = camera.thumbnail {
                        Image(uiImage: thumb).resizable().scaledToFill()
                    } else {
                        panelFill
                    }
                    if camera.processing > 0 {
                        Color.black.opacity(0.45)
                        ProgressView().tint(.white)
                    }
                }
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .buttonStyle(.plain)
            .accessibilityLabel(camera.processing > 0 ? "Revelando, abrir fotos" : "Abrir fotos")

            Spacer()

            // Toque = foto; segurar = rajada (RÁPIDO, CONGELAR) ou gravação (AÇÃO)
            ZStack {
                Circle().stroke(.white, lineWidth: 5).frame(width: 84, height: 84)
                Circle()
                    .fill(shutterColor)
                    .frame(width: shutterIsStop ? 36 : 68, height: shutterIsStop ? 36 : 68)
                    .clipShape(RoundedRectangle(cornerRadius: shutterIsStop ? 8 : 34))
            }
            .scaleEffect(pressingShutter ? 0.9 : 1)
            .animation(.spring(response: 0.2, dampingFraction: 0.6), value: pressingShutter)
            .animation(.snappy(duration: 0.2), value: shutterIsStop)
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

            Button {
                withAnimation(.snappy(duration: 0.25)) { camera.flipCamera() }
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
            } label: {
                Image(systemName: "arrow.triangle.2.circlepath")
                    .font(.system(size: 21, weight: .semibold))
                    .frame(width: 56, height: 56)
                    .foregroundStyle(camera.lens == .front ? accent : .white)
                    .background(Circle().fill(panelFill))
            }
            .buttonStyle(.plain)
            .opacity(camera.hasFront ? 1 : 0)
            .disabled(!camera.hasFront)
            .accessibilityLabel("Virar câmera")
        }
        .padding(.horizontal, 12)
    }

    // MARK: - Ajustes (abre pela metade, com o visor visível em cima)

    private var settingsSheet: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 14) {
                    settingsSection("Formato da foto") {
                        Picker("Formato", selection: Binding(get: { camera.rawMode }, set: { camera.select(mode: $0) })) {
                            ForEach(RawMode.allCases) { mode in Text(mode.rawValue).tag(mode) }
                        }
                        .pickerStyle(.segmented)
                        Text(camera.rawMode == .proRAW
                             ? "ProRAW: 48 MP, muito detalhe e pouco ruído. O melhor no dia a dia."
                             : "RAW puro: o sinal cru do sensor, 12 MP, sem nada da Apple. Mais ruído, mais controle.")
                            .font(.footnote).foregroundStyle(.secondary)
                    }

                    settingsSection("Luz") {
                        Toggle("ISO e tempo na mão", isOn: $camera.manualExposure)
                        if camera.manualExposure {
                            sliderRow("ISO", value: $camera.isoIndex,
                                      range: 0...Double(max(camera.isoStops.count - 1, 1)),
                                      text: "\(Int(camera.selectedISO))")
                            sliderRow("Tempo", value: $camera.shutterIndex,
                                      range: 0...Double(max(camera.shutterStops.count - 1, 1)),
                                      text: shutterText(camera.selectedShutter))
                        } else {
                            HStack {
                                Text("Mais clara / escura").frame(width: 120, alignment: .leading)
                                Slider(value: $camera.evBias, in: -3...3, step: 1 / 3)
                                Text(String(format: "%+.1f", camera.evBias))
                                    .font(.system(.footnote, design: .monospaced))
                                    .frame(width: 44, alignment: .trailing)
                            }
                            Text("Agora: ISO \(Int(camera.readoutISO)) · \(shutterText(camera.readoutShutter))")
                                .font(.footnote).foregroundStyle(.secondary)
                        }
                    }

                    settingsSection("Foco") {
                        Toggle("Foco na mão", isOn: $camera.manualFocus)
                        if camera.manualFocus {
                            HStack {
                                Text("Perto").font(.footnote)
                                Slider(value: $camera.lensPosition, in: 0...1) { editing in
                                    withAnimation(.snappy(duration: 0.2)) { camera.loupe = editing }
                                }
                                Text("Longe").font(.footnote)
                            }
                            Text("Enquanto arrasta, o visor amplia 4×.").font(.footnote).foregroundStyle(.secondary)
                        }
                    }

                    settingsSection("Cor da luz") {
                        Toggle("Cor na mão", isOn: $camera.manualWB)
                        if camera.manualWB {
                            HStack {
                                Text("Kelvin").frame(width: 60, alignment: .leading)
                                Slider(value: $camera.kelvin, in: 2500...10000, step: 100)
                                Text("\(Int(camera.kelvin))K")
                                    .font(.system(.footnote, design: .monospaced))
                                    .frame(width: 56, alignment: .trailing)
                            }
                            Text("Baixo deixa a foto azulada, alto deixa alaranjada.").font(.footnote).foregroundStyle(.secondary)
                        }
                    }

                    settingsSection("Ajudas") {
                        Toggle("Peaking (bordas em foco em laranja)", isOn: $camera.peaking)
                        Toggle("Zebra (listras onde estourou)", isOn: $camera.zebra)
                        Toggle("Grade de terços", isOn: $camera.showGrid)
                        Toggle("Histograma colorido (R, G, B)", isOn: $camera.rgbHistogram)
                        Toggle("Cor falsa (exposição por cores)", isOn: $camera.falseColor)
                        if camera.falseColor {
                            Text("Roxo: preto sem detalhe · azul: sombra · verde: cinza médio · rosa: pele bem exposta · amarelo: quase estourando · vermelho: estourado")
                                .font(.footnote).foregroundStyle(.secondary)
                        }
                        Picker("Timer", selection: $camera.timerSeconds) {
                            Text("Sem timer").tag(0)
                            Text("3 s").tag(3)
                            Text("10 s").tag(10)
                        }
                        .pickerStyle(.segmented)
                    }

                    settingsSection("Ao salvar") {
                        Toggle("Espelhar (como no espelho)", isOn: $camera.mirror)
                        Toggle("Guardar também o DNG (RAW)", isOn: $camera.saveDNG)
                    }

                    VStack(spacing: 10) {
                        Button {
                            showSettings = false
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { showGuide = true }
                        } label: {
                            Label("Guia rápido", systemImage: "questionmark.circle").frame(maxWidth: .infinity, minHeight: 44)
                        }
                        .buttonStyle(.bordered)
                        Button {
                            showSettings = false
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { showReport = true }
                        } label: {
                            Label("Relatório para o Claude", systemImage: "doc.text.magnifyingglass").frame(maxWidth: .infinity, minHeight: 44)
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding(16)
            }
            .navigationTitle("Ajustes")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("OK") { showSettings = false } } }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
        .presentationDetents([.medium, .large])
        .presentationBackgroundInteraction(.enabled(upThrough: .medium))
        .presentationDragIndicator(.visible)
    }

    private func settingsSection<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title.uppercased()).font(.caption.weight(.bold)).tracking(0.8).foregroundStyle(.secondary)
            content()
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color.white.opacity(0.07)))
    }

    // MARK: - Looks (abre pela metade: o visor mostra o look na hora)

    private var looksSheet: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 10) {
                    VStack(spacing: 8) {
                        HStack {
                            Text("Intensidade").frame(width: 90, alignment: .leading)
                            Slider(value: $camera.lookAmount, in: 0...1, step: 0.05)
                            Text("\(Int((camera.lookAmount * 100).rounded()))%")
                                .font(.system(.footnote, design: .monospaced)).frame(width: 44, alignment: .trailing)
                        }
                        HStack {
                            Text("Grão").frame(width: 90, alignment: .leading)
                            Slider(value: $camera.grainAmount, in: 0...2, step: 0.1)
                            Text(String(format: "%.1f×", camera.grainAmount))
                                .font(.system(.footnote, design: .monospaced)).frame(width: 44, alignment: .trailing)
                        }
                    }
                    .padding(14)
                    .background(RoundedRectangle(cornerRadius: 14).fill(Color.white.opacity(0.07)))

                    ForEach(Look.allCases) { look in
                        Button {
                            withAnimation(.snappy(duration: 0.2)) { camera.look = look }
                            UISelectionFeedbackGenerator().selectionChanged()
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(look.rawValue).font(.body.weight(.semibold))
                                    Text(look.subtitle).font(.footnote).opacity(0.7)
                                }
                                Spacer()
                                if camera.look == look { Image(systemName: "checkmark").font(.body.weight(.bold)) }
                            }
                            .padding(.horizontal, 16)
                            .frame(minHeight: 56)
                            .foregroundStyle(camera.look == look ? Color.black : Color.white)
                            .background(RoundedRectangle(cornerRadius: 14).fill(camera.look == look ? accent : Color.white.opacity(0.07)))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(16)
            }
            .navigationTitle("Looks")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("OK") { showLooks = false } } }
        }
        .tint(accent)
        .preferredColorScheme(.dark)
        .presentationDetents([.medium, .large])
        .presentationBackgroundInteraction(.enabled(upThrough: .medium))
        .presentationDragIndicator(.visible)
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
        case .night: return "\(camera.nightFrames)×\nNOITE"
        case .stars: return "16×\nCÉU"
        case .moon: return "8×\nLUA"
        case .flash: return "DNG\nFLASH"
        case .fast: return camera.rawMode == .bayer ? "RAW\n12MP" : "HEIC\n12MP"
        case .action: return "4K\n120"
        case .freeze: return camera.freezeMax ? "1/\(Int((1 / camera.freezeShutter).rounded()))\nMÁX" : "1/\(Int((1 / camera.freezeShutter).rounded()))\n12MP"
        case .hdr: return "HDR\n3× RAW"
        case .video: return "1080p\n\(camera.videoFPS) fps"
        case .cinematic: return apertureLabel(camera.cinematicAperture) + "\nCINEMA"
        case .dual: return "DUPLA\nFOTO · VÍDEO"
        case .scan: return "3D\nLIDAR"
        case .longExposure: return "\(Int(camera.longSecondsChoice)) s\n\(camera.longStyle.rawValue.uppercased())"
        case .superRes: return "4× 48MP\nSUPER"
        case .portrait: return apertureLabel(camera.portraitAperture) + "\nRETRATO"
        case .photo:
            if camera.rawMode == .bayer { return "DNG\nRAW" }
            return camera.crop > 1.4 ? "DNG\n\(camera.zoomText)" : "DNG\n48MP"
        }
    }

    /// Botão vira um quadrado vermelho enquanto grava.
    private var shutterIsStop: Bool { camera.actionRecording || camera.isRecordingVideo }

    private var shutterColor: Color {
        if shutterIsStop { return .red }
        if camera.captureMode == .video || camera.captureMode == .cinematic { return .red }
        if camera.countdown > 0 || camera.bursting { return accent }
        return .white
    }

    /// O que está na mão, para lembrar no visor (ex.: "ISO 200 · 1/250 · MF").
    private var manualSummary: String {
        var parts: [String] = []
        if camera.manualExposure { parts.append("ISO \(Int(camera.selectedISO)) · \(shutterText(camera.selectedShutter))") }
        if camera.manualFocus { parts.append("MF") }
        if camera.manualWB { parts.append("\(Int(camera.kelvin))K") }
        return parts.joined(separator: " · ")
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
    /// Vermelho, verde e azul; vazio mostra só a luminância.
    var rgb: [[Float]] = []

    private func path(_ values: [Float], in size: CGSize) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: 0, y: size.height))
        for (i, v) in values.enumerated() {
            let x = size.width * CGFloat(i) / CGFloat(max(values.count - 1, 1))
            path.addLine(to: CGPoint(x: x, y: size.height * (1 - CGFloat(min(v, 1)))))
        }
        path.addLine(to: CGPoint(x: size.width, y: size.height))
        path.closeSubpath()
        return path
    }

    var body: some View {
        Canvas { ctx, size in
            if rgb.count == 3 {
                ctx.blendMode = .plusLighter
                let colors: [Color] = [.red, .green, .blue]
                for (channel, color) in zip(rgb, colors) where channel.count > 1 {
                    ctx.fill(path(channel, in: size), with: .color(color.opacity(0.7)))
                }
            } else if bins.count > 1 {
                ctx.fill(path(bins, in: size), with: .color(.white.opacity(0.75)))
            }
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

/// Hospeda o visor do sistema. Fica quase invisível (serve para o RotationCoordinator)
/// e aparece de verdade no modo CINEMÁTICO.
private struct AngleLayerView: UIViewRepresentable {
    let layer: AVCaptureVideoPreviewLayer

    final class Host: UIView {
        var previewLayer: AVCaptureVideoPreviewLayer?
        override func layoutSubviews() {
            super.layoutSubviews()
            previewLayer?.frame = bounds
        }
    }

    func makeUIView(context: Context) -> Host {
        let view = Host()
        layer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(layer)
        view.previewLayer = layer
        return view
    }

    func updateUIView(_ uiView: Host, context: Context) {}
}
