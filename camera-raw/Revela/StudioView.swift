import CoreImage
import ImageIO
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

private let accent = Color(red: 0.96, green: 0.64, blue: 0.24)

/// Arquivo RAW vindo da galeria (o seletor de fotos entrega o DNG quando a foto tem um).
private struct RawFile: Transferable {
    let data: Data
    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(importedContentType: .rawImage) { RawFile(data: $0) }
    }
}

/// Revelar de novo: abre uma foto (a última do Revela ou qualquer uma da galeria), troca o filme,
/// a intensidade, o grão, a proporção e, no retrato, o foco e o desfoque. Salva como foto nova.
final class StudioModel: ObservableObject {
    @Published var preview: UIImage?
    @Published var before: UIImage?
    @Published var frame: CapturedFrame?
    @Published var title = ""
    @Published var loading = false
    @Published var saving = false
    @Published var message: String?

    @Published var look: Look = .portra { didSet { refresh() } }
    @Published var custom: CustomLook? { didSet { refresh() } }
    @Published var amount: Float = 1 { didSet { refresh() } }
    @Published var grain: Float = 1 { didSet { refresh() } }
    /// nil = proporção original da foto.
    @Published var aspect: AspectRatio? { didSet { refresh() } }
    @Published var aperture: Float = 2.8 { didSet { refresh(scene: true) } }
    /// Ponto em foco no retrato (0…1, origem em cima à esquerda, na foto inteira).
    @Published var focus: CGPoint? { didSet { refresh(scene: true) } }
    /// Ajustes de luz, cor, horizonte e recorte (antes do filme).
    @Published var adjust = Developer.Adjust() { didSet { refresh() } }
    var skinProtection = true

    private var zoom: CGFloat = 1
    private var mirror = false
    /// Cena pequena já aberta (só reabre quando muda o foco ou o desfoque do retrato).
    private var previewScene: CIImage?
    private var previewScale: Float = 1
    private let queue = DispatchQueue(label: "revela.studio", qos: .userInitiated)
    private var generation = 0
    private var suspendRefresh = false

    var hasDepth: Bool { frame?.hasDepth ?? false }
    var lookName: String { custom?.name ?? look.rawValue }

    var options: DevelopOptions {
        var o = DevelopOptions(look: look, custom: custom, amount: amount, grain: grain, zoom: zoom,
                               aspect: aspect ?? .r43, mirror: mirror)
        o.originalAspect = aspect == nil
        o.skinProtection = skinProtection
        return o
    }

    /// Começa com as escolhas atuais da câmera.
    func start(from camera: CameraModel) {
        suspendRefresh = true
        look = camera.look
        custom = camera.customLook
        amount = camera.lookAmount
        grain = camera.grainAmount
        skinProtection = camera.skinProtection
        suspendRefresh = false
    }

    func loadLatest() {
        loading = true
        queue.async {
            let latest = SourceStore.latest()
            DispatchQueue.main.async {
                if let latest { self.use(entry: latest.0, data: latest.1) } else { self.loading = false }
            }
        }
    }

    private func use(entry: SourceStore.Entry, data: Data) {
        suspendRefresh = true
        zoom = CGFloat(entry.zoom)
        mirror = entry.mirror
        aspect = AspectRatio(rawValue: entry.aspect)
        aperture = entry.aperture
        focus = entry.focusPoint
        suspendRefresh = false
        title = "\(entry.mode) · \(entry.date.formatted(date: .omitted, time: .shortened))"
        open(CapturedFrame(data: data, isRaw: entry.isRaw, hasDepth: entry.hasDepth))
    }

    func load(_ item: PhotosPickerItem) {
        loading = true
        message = nil
        Task {
            // Foto do próprio Revela: o original guardado tem tudo (RAW, profundidade, foco escolhido)
            if let id = item.itemIdentifier, let found = SourceStore.find(assetID: id) {
                await MainActor.run { self.use(entry: found.0, data: found.1) }
                return
            }
            var data: Data?
            if item.supportedContentTypes.contains(where: { $0.conforms(to: .rawImage) }) {
                data = (try? await item.loadTransferable(type: RawFile.self))?.data
            }
            if data == nil { data = try? await item.loadTransferable(type: Data.self) }
            await MainActor.run {
                guard let data else {
                    self.loading = false
                    self.message = "Não consegui abrir essa foto."
                    return
                }
                self.suspendRefresh = true
                self.zoom = 1
                self.mirror = false
                self.aspect = nil
                self.focus = nil
                self.aperture = 2.8
                self.suspendRefresh = false
                self.title = "Da galeria"
                self.open(CapturedFrame(data: data, isRaw: Self.isRaw(data), hasDepth: Developer.hasDepth(data)))
            }
        }
    }

    private static func isRaw(_ data: Data) -> Bool {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let type = CGImageSourceGetType(source).flatMap({ UTType($0 as String) }) else { return false }
        return type.conforms(to: .rawImage)
    }

    private func open(_ newFrame: CapturedFrame) {
        suspendRefresh = true
        adjust = Developer.Adjust()
        suspendRefresh = false
        frame = newFrame
        previewScene = nil
        before = nil
        dlog("Revelar de novo: \(newFrame.isRaw ? "RAW" : "foto") \(newFrame.data.count / 1024) KB\(newFrame.hasDepth ? " · com profundidade" : "")")
        refresh(scene: true)
    }

    /// Tamanho da prévia: o lado maior com ~1600 px.
    private static func scale(for frame: CapturedFrame) -> Float {
        var long: CGFloat = 4000
        if frame.isRaw, let raw = CIRAWFilter(imageData: frame.data, identifierHint: "com.adobe.raw-image") {
            long = max(raw.nativeSize.width, raw.nativeSize.height)
        } else if let source = CGImageSourceCreateWithData(frame.data as CFData, nil),
                  let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
                  let w = props[kCGImagePropertyPixelWidth] as? CGFloat, let h = props[kCGImagePropertyPixelHeight] as? CGFloat {
            long = max(w, h)
        }
        return Float(min(1, 1600 / max(long, 1)))
    }

    func refresh(scene reopen: Bool = false) {
        guard !suspendRefresh, let frame else { return }
        if reopen { previewScene = nil }
        generation += 1
        let gen = generation
        let options = self.options
        let adjust = self.adjust
        let aperture = self.aperture, focus = self.focus
        let cached = previewScene
        let needsBefore = before == nil
        queue.async {
            guard gen == self.generation else { return }
            var scene = cached
            if scene == nil {
                let scale = Self.scale(for: frame)
                guard let opened = Developer.scene(for: frame, scale: scale, aperture: frame.hasDepth ? aperture : nil,
                                                   focusPoint: focus) else {
                    DispatchQueue.main.async {
                        self.loading = false
                        self.message = "Não consegui revelar essa foto."
                    }
                    return
                }
                scene = Developer.materialize(opened, extent: opened.extent)
                DispatchQueue.main.async { if gen == self.generation { self.previewScene = scene } }
            }
            guard let scene, gen == self.generation else { return }
            let image = Developer.render(Developer.adjusted(scene, adjust), options: options)
            var neutral = options
            neutral.custom = nil
            neutral.look = .neutro
            neutral.amount = 0
            // "Antes": a foto como veio, sem ajustes nem filme
            let beforeImage = needsBefore ? Developer.render(scene, options: neutral) : nil
            DispatchQueue.main.async {
                guard gen == self.generation else { return }
                self.preview = image
                if let beforeImage { self.before = beforeImage }
                self.loading = false
            }
        }
    }

    /// Toque na prévia (0…1 na imagem mostrada) -> ponto na foto inteira.
    func setFocus(atDisplayed p: CGPoint) {
        // Com o horizonte girado ou recortado o toque não cai no mesmo lugar: foco só com a foto inteira
        guard hasDepth, adjust.straighten == 0, adjust.crop <= 1.001, let scene = previewScene else { return }
        let rect = options.cropRect(in: scene.extent)
        let e = scene.extent
        let u = mirror ? 1 - p.x : p.x
        let x = (rect.minX + u * rect.width - e.minX) / e.width
        let ciY = rect.maxY - p.y * rect.height
        focus = CGPoint(x: x, y: 1 - (ciY - e.minY) / e.height)
    }

    /// Foco atual em coordenadas da prévia (para desenhar o círculo).
    var focusOnDisplay: CGPoint? {
        guard let focus, adjust.straighten == 0, adjust.crop <= 1.001, let scene = previewScene else { return nil }
        let rect = options.cropRect(in: scene.extent)
        let e = scene.extent
        var u = (focus.x * e.width + e.minX - rect.minX) / rect.width
        if mirror { u = 1 - u }
        let ciY = (1 - focus.y) * e.height + e.minY
        let v = (rect.maxY - ciY) / rect.height
        guard (0...1).contains(u), (0...1).contains(v) else { return nil }
        return CGPoint(x: u, y: v)
    }

    func save() {
        guard let frame, !saving else { return }
        saving = true
        let options = self.options
        let adjust = self.adjust
        let aperture = self.aperture, focus = self.focus
        queue.async {
            let t0 = CFAbsoluteTimeGetCurrent()
            let output = Developer.scene(for: frame, aperture: frame.hasDepth ? aperture : nil, focusPoint: focus)
                .flatMap { Developer.finish(Developer.adjusted($0, adjust), options: options) }
            guard let output else {
                DispatchQueue.main.async {
                    self.saving = false
                    self.message = "Não consegui revelar essa foto."
                }
                return
            }
            Library.save(dng: nil, developed: output.heic, tryPair: false) { error in
                dlog("Revelar de novo: \(options.lookName) salvo em \(Diagnostics.ms(since: t0))\(error.map { " · erro \($0.localizedDescription)" } ?? "")")
                DispatchQueue.main.async {
                    self.saving = false
                    self.message = error?.localizedDescription ?? "Salvo como foto nova na galeria."
                }
            }
        }
    }
}

struct StudioView: View {
    @ObservedObject var camera: CameraModel
    @StateObject private var model = StudioModel()
    @Environment(\.dismiss) private var dismiss
    @State private var pickerItem: PhotosPickerItem?
    @State private var showBefore = false
    @State private var tab = 0

    var body: some View {
        VStack(spacing: 0) {
            header
            photo
            controls
        }
        .background(Color.black.ignoresSafeArea())
        .preferredColorScheme(.dark)
        .tint(accent)
        .onAppear {
            model.start(from: camera)
            model.loadLatest()
        }
        .onChange(of: pickerItem) { _, item in
            if let item { model.load(item) }
        }
    }

    private var header: some View {
        HStack {
            Button { dismiss() } label: {
                Image(systemName: "xmark").font(.body.weight(.bold)).frame(width: 44, height: 44)
            }
            VStack(alignment: .leading, spacing: 0) {
                Text("Revelar de novo").font(.headline)
                if !model.title.isEmpty { Text(model.title).font(.caption).opacity(0.6) }
            }
            Spacer()
            Button {
                if let url = URL(string: "photos-redirect://") { UIApplication.shared.open(url) }
            } label: {
                Image(systemName: "photo.on.rectangle").frame(width: 44, height: 44)
            }
            .accessibilityLabel("Abrir o app Fotos")
            PhotosPicker(selection: $pickerItem, matching: .images, preferredItemEncoding: .current, photoLibrary: .shared()) {
                Text("Escolher").font(.body.weight(.semibold))
                    .padding(.horizontal, 14).frame(height: 36)
                    .background(Capsule().fill(Color.white.opacity(0.12)))
            }
        }
        .padding(.horizontal, 8)
        .foregroundStyle(.white)
    }

    private var photo: some View {
        GeometryReader { geo in
            ZStack {
                if let image = showBefore ? (model.before ?? model.preview) : model.preview {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .overlay {
                            GeometryReader { box in
                                if model.hasDepth, !showBefore, let p = model.focusOnDisplay {
                                    Circle().stroke(accent, lineWidth: 2)
                                        .frame(width: 56, height: 56)
                                        .position(x: p.x * box.size.width, y: p.y * box.size.height)
                                }
                                Color.clear
                                    .contentShape(Rectangle())
                                    .onTapGesture(coordinateSpace: .local) { location in
                                        model.setFocus(atDisplayed: CGPoint(x: location.x / box.size.width,
                                                                            y: location.y / box.size.height))
                                    }
                            }
                        }
                } else if !model.loading {
                    VStack(spacing: 14) {
                        Image(systemName: "photo.badge.plus").font(.system(size: 44)).opacity(0.6)
                        Text("Escolha uma foto da galeria para revelar com os filmes do Revela.")
                            .multilineTextAlignment(.center).opacity(0.7)
                        PhotosPicker(selection: $pickerItem, matching: .images, preferredItemEncoding: .current, photoLibrary: .shared()) {
                            Text("Escolher foto").bold().padding(.horizontal, 20).frame(height: 46)
                                .background(Capsule().fill(accent)).foregroundStyle(.black)
                        }
                    }
                    .padding(30)
                }
                if model.loading || model.saving {
                    ProgressView(model.saving ? "Revelando em resolução cheia…" : "Abrindo…")
                        .padding(16)
                        .background(RoundedRectangle(cornerRadius: 12).fill(.black.opacity(0.7)))
                }
                if let message = model.message {
                    VStack {
                        Spacer()
                        Text(message).font(.footnote.weight(.semibold))
                            .padding(.horizontal, 14).padding(.vertical, 8)
                            .background(Capsule().fill(.black.opacity(0.75)))
                            .padding(.bottom, 10)
                    }
                    .onTapGesture { model.message = nil }
                }
            }
            .frame(width: geo.size.width, height: geo.size.height)
        }
    }

    private var controls: some View {
        VStack(spacing: 10) {
            Picker("", selection: $tab) {
                Text("Filme").tag(0)
                Text("Ajustes").tag(1)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 16)
            if tab == 0 { filmControls } else { adjustControls }
            bottomButtons
        }
        .padding(.top, 8)
        .foregroundStyle(.white)
    }

    private var adjustControls: some View {
        VStack(spacing: 4) {
            row("Exposição", value: String(format: "%+.1f", model.adjust.exposure)) {
                Slider(value: $model.adjust.exposure, in: -2...2, step: 0.1)
            }
            row("Temperatura", value: String(format: "%+.0f", model.adjust.temperature * 100)) {
                Slider(value: $model.adjust.temperature, in: -1...1, step: 0.02)
            }
            row("Tom", value: String(format: "%+.0f", model.adjust.tint * 100)) {
                Slider(value: $model.adjust.tint, in: -1...1, step: 0.02)
            }
            row("Sombras", value: String(format: "%+.0f", model.adjust.shadows * 100)) {
                Slider(value: $model.adjust.shadows, in: -1...1, step: 0.02)
            }
            row("Altas luzes", value: String(format: "%+.0f", model.adjust.highlights * 100)) {
                Slider(value: $model.adjust.highlights, in: -1...1, step: 0.02)
            }
            row("Endireitar", value: String(format: "%+.1f°", model.adjust.straighten)) {
                Slider(value: $model.adjust.straighten, in: -10...10, step: 0.1)
            }
            row("Recorte", value: String(format: "%.1f×", model.adjust.crop)) {
                Slider(value: $model.adjust.crop, in: 1...3, step: 0.05)
            }
            HStack {
                Text("Temperatura +: mais quente · Tom +: magenta · Altas luzes −: recupera o céu")
                    .font(.caption2).opacity(0.55)
                Spacer()
                Button("Zerar") { model.adjust = Developer.Adjust() }
                    .font(.footnote.weight(.semibold))
                    .disabled(model.adjust.isNeutral)
            }
        }
        .padding(.horizontal, 16)
    }

    private var filmControls: some View {
        VStack(spacing: 10) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(camera.customLooks) { custom in
                        chip(custom.name, on: model.custom?.id == custom.id) { model.custom = custom }
                    }
                    ForEach(Look.allCases) { look in
                        chip(look.rawValue, on: model.custom == nil && model.look == look) {
                            model.custom = nil
                            model.look = look
                        }
                    }
                }
                .padding(.horizontal, 14)
            }
            VStack(spacing: 6) {
                row("Intensidade", value: "\(Int((model.amount * 100).rounded()))%") {
                    Slider(value: $model.amount, in: 0...1, step: 0.05)
                }
                row("Grão", value: String(format: "%.1f×", model.grain)) {
                    Slider(value: $model.grain, in: 0...2, step: 0.1)
                }
                if model.hasDepth {
                    row("Desfoque", value: String(format: "f/%.1f", model.aperture)) {
                        Slider(value: Binding(get: { -model.aperture }, set: { model.aperture = -$0 }), in: -16.0 ... -1.4)
                    }
                    Text("Toque na foto para escolher o que fica em foco.").font(.caption).opacity(0.55)
                }
                HStack(spacing: 8) {
                    chip("Original", on: model.aspect == nil) { model.aspect = nil }
                    ForEach(AspectRatio.allCases) { a in
                        chip(a.rawValue, on: model.aspect == a) { model.aspect = a }
                    }
                }
            }
            .padding(.horizontal, 16)
        }
    }

    private var bottomButtons: some View {
            HStack(spacing: 10) {
                Text("Antes")
                    .font(.body.weight(.semibold))
                    .frame(width: 96, height: 50)
                    .background(Capsule().fill(Color.white.opacity(showBefore ? 0.3 : 0.12)))
                    .onLongPressGesture(minimumDuration: 0, maximumDistance: 60, pressing: { showBefore = $0 }, perform: {})
                    .accessibilityLabel("Segure para ver a foto sem o filme")
                Button { model.save() } label: {
                    Label("Salvar como foto nova", systemImage: "square.and.arrow.down")
                        .font(.body.weight(.bold))
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Capsule().fill(accent))
                        .foregroundStyle(.black)
                }
                .disabled(model.frame == nil || model.saving)
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 8)
    }

    private func chip(_ title: String, on: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.footnote.weight(.semibold))
                .lineLimit(1)
                .padding(.horizontal, 12).frame(height: 34)
                .foregroundStyle(on ? Color.black : Color.white)
                .background(Capsule().fill(on ? accent : Color.white.opacity(0.1)))
        }
        .buttonStyle(.plain)
    }

    private func row<C: View>(_ label: String, value: String, @ViewBuilder control: () -> C) -> some View {
        HStack {
            Text(label).font(.subheadline).frame(width: 86, alignment: .leading)
            control()
            Text(value).font(.system(.footnote, design: .monospaced)).frame(width: 52, alignment: .trailing)
        }
    }
}
