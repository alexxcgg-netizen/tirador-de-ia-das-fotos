"""Placar do laboratório: mede as metas do BRIEFING.md nas imagens do ramo revela-lab.

Uso: python3 placar.py <pasta do ramo revela-lab>
Precisa de numpy e Pillow. Imprime cada meta com o número, a meta e OK / FALTA.
"""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageFilter

LUMA = np.array([0.2126, 0.7152, 0.0722])


def real(path):
    """As pastas medidas em PSNR vêm em PNG (sem perda); as outras em JPEG."""
    if path.endswith(".jpg") and not os.path.exists(path) and os.path.exists(path[:-4] + ".png"):
        return path[:-4] + ".png"
    return path


def load(path):
    return np.asarray(Image.open(real(path)).convert("RGB")).astype(np.float64) / 255


def luma(a):
    return a @ LUMA


def sat(a):
    return float((a.max(-1) - a.min(-1)).mean())


def edges(path):
    g = np.asarray(Image.open(real(path)).convert("L").filter(ImageFilter.FIND_EDGES)).astype(np.float64)
    return float(g.mean()), float(np.percentile(g, 99.5))


def local_noise(a):
    """Desvio local em áreas lisas: diferença para uma versão borrada, nos 30% menos texturizados."""
    l = luma(a)
    img = Image.fromarray((np.clip(l, 0, 1) * 255).astype(np.uint8))
    blur = np.asarray(img.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
    big = np.asarray(img.filter(ImageFilter.GaussianBlur(8))).astype(np.float64) / 255
    texture = np.abs(blur - big)
    flat = texture <= np.percentile(texture, 30)
    return float(np.abs(l - blur)[flat].mean())


def _fourier_shift(img, dx, dy):
    """Desloca por fração de pixel (fase na FFT), canal por canal."""
    h, w = img.shape[:2]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    phase = np.exp(-2j * np.pi * (fx * dx + fy * dy))
    return np.stack([np.real(np.fft.ifft2(np.fft.fft2(img[..., c]) * phase)) for c in range(img.shape[2])], -1)


def psnr(a, b, reach=16):
    """PSNR depois do melhor encaixe, inteiro e depois em fração de pixel (a super resolução sai na posição da
    foto de referência que ela escolheu, que pode estar meio pixel deslocada da original)."""
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    a, b = a[:h, :w], b[:h, :w]
    m = reach
    core = a[m:h - m, m:w - m]
    best = min((((core - b[m + dy:h - m + dy, m + dx:w - m + dx]) ** 2).mean(), dx, dy)
               for dy in range(-m, m + 1) for dx in range(-m, m + 1))
    _, bx, by = best
    window = b[m + by:h - m + by, m + bx:w - m + bx]
    fine = min(((core - _fourier_shift(window, fx, fy))[4:-4, 4:-4] ** 2).mean()
               for fy in np.arange(-0.75, 0.76, 0.25) for fx in np.arange(-0.75, 0.76, 0.25))
    return 10 * np.log10(1 / max(min(best[0], fine), 1e-12))


rows = []


def check(area, name, value, ok, goal):
    rows.append((area, name, value, goal, "OK" if ok else "FALTA"))


# ---------------------------------------------------------------------------------------------------------------
# Prevenção (RevelaLab/PrevencaoTests.swift): defeitos achados na revisão de código que não podem voltar sem ninguém
# ver. Cada meta mede a saída de um teste; se o teste não gerou nada (não rodou, quebrou, ou o laboratório é de antes
# dele), a meta fica FALTA com "sem saída" — nunca derruba o placar.

SEM = "sem saída"


def _png(root, rel):
    p = os.path.join(root, rel + ".png")
    return p if os.path.exists(p) else None


def _log_text(root):
    p = os.path.join(root, "log.txt")
    return open(p, encoding="utf-8", errors="ignore").read() if os.path.exists(p) else ""


def _same(*arrays):
    """Recorta todas no menor tamanho comum (as saídas podem diferir de 1 px)."""
    h = min(a.shape[0] for a in arrays)
    w = min(a.shape[1] for a in arrays)
    return [a[:h, :w] for a in arrays]


def _gauss(l, sigma):
    """Borrão gaussiano separável em ponto flutuante (sem arredondar para 8 bits)."""
    r = max(1, int(round(3 * sigma)))
    x = np.arange(-r, r + 1, dtype=np.float64)
    k = np.exp(-x * x / (2 * sigma * sigma))
    k /= k.sum()
    p = np.pad(l, ((r, r), (0, 0)), mode="edge")
    t = sum(k[i] * p[i:i + l.shape[0]] for i in range(2 * r + 1))
    p = np.pad(t, ((0, 0), (r, r)), mode="edge")
    return sum(k[i] * p[:, i:i + l.shape[1]] for i in range(2 * r + 1))


def _edge_mean(l):
    img = Image.fromarray((np.clip(l, 0, 1) * 255).astype(np.uint8))
    return float(np.asarray(img.filter(ImageFilter.FIND_EDGES)).astype(np.float64)[1:-1, 1:-1].mean())


def _maxfilt(l, r):
    p = np.pad(l, r, mode="edge")
    h, w = l.shape
    out = np.full(l.shape, -np.inf)
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            out = np.maximum(out, p[dy:dy + h, dx:dx + w])
    return out


def _sem(area, metas):
    for name, goal in metas:
        check(area, name, SEM, False, goal)


def _geometria(root, log):
    meta = ("recorte por lente, ponto do Retrato, proporção", "todos")
    m = re.search(r"GEOMETRIA: (\d+)/(\d+) casos certos", log)
    if not m:
        return _sem("GEOMETRIA", [meta])
    ok, total = int(m.group(1)), int(m.group(2))
    check("GEOMETRIA", meta[0], f"{ok}/{total}", ok == total and total > 0, meta[1])


def _longa(root, log):
    area = "LONGA"
    metas = [("seda 240 quadros: erro na rampa clara (degraus)", "≤ 1 código"),
             ("seda: níveis da rampa ÷ códigos de 8 bits", "≥ 2"),
             ("rastros: erro na rampa clara", "≤ 0,5 código"),
             ("rastros no escuro: quanto o preto sobe", "≤ 1 σ"),
             ("seda no escuro: quanto o preto sobe", "≤ 0,25 σ")]
    ctrl = re.search(r"LONGA controle \(1 quadro\): erro máximo ([\d.]+) códigos", log)
    if not ctrl:
        return _sem(area, metas)
    c = float(ctrl.group(1))
    rows.append((area, "controle da medida: 1 quadro (só informação)", f"{c:.2f} cód.", "", ""))
    if c > 0.6:
        # A medida em si está errada (não o app): nenhuma meta da LONGA vale nesta rodada
        for name, goal in metas:
            check(area, name, "medida inválida", False, goal)
        return
    seda = re.search(r"LONGA seda rampa \((\d+) de (\d+) quadros\): erro máximo ([\d.]+) códigos · níveis (\d+) em ([\d.]+) códigos", log)
    if seda:
        used, asked, err = int(seda.group(1)), int(seda.group(2)), float(seda.group(3))
        value = f"{err:.2f} cód." + ("" if used == asked else f" ({used}/{asked} q.)")
        check(area, metas[0][0], value, err <= 1.0 and used == asked, metas[0][1])
        r = int(seda.group(4)) / max(float(seda.group(5)), 1e-6)
        check(area, metas[1][0], f"{r:.1f}", r >= 2, metas[1][1])
    else:
        _sem(area, metas[0:2])
    tr = re.search(r"LONGA rastros rampa \((\d+) de (\d+) quadros\): erro máximo ([\d.]+) códigos", log)
    if tr:
        err = float(tr.group(3))
        check(area, metas[2][0], f"{err:.2f} cód.", err <= 0.5 and tr.group(1) == tr.group(2), metas[2][1])
    else:
        _sem(area, metas[2:3])
    for style, meta, limit in (("rastros", metas[3], 1.0), ("seda", metas[4], 0.25)):
        m = re.search(rf"LONGA {style} escuro \((\d+) de (\d+) quadros\): preto sobe ([-\d.]+) σ", log)
        if not m:
            _sem(area, [meta])
            continue
        lift = float(m.group(3))
        check(area, meta[0], f"{lift:+.2f} σ", abs(lift) <= limit and m.group(1) == m.group(2), meta[1])


def _panorama(root, log):
    area = "PANORAMA"
    metas = [("emendas vs miolo dos quadros (PSNR)", "≥ miolo − 1,5 dB"), ("salto de exposição nas emendas", "≤ 0,015")]
    m = re.search(r"PANORAMA: emendas ([\d\- ]+) · miolos ([\d\- ]+)", log)
    po, pt = _png(root, "panorama/emendado"), _png(root, "panorama/verdade")
    if not (m and po and pt):
        return _sem(area, metas)
    seams = [(int(a), int(b)) for a, b in re.findall(r"(\d+)-(\d+)", m.group(1))]
    cores = [(int(a), int(b)) for a, b in re.findall(r"(\d+)-(\d+)", m.group(2))]
    out, truth = _same(luma(load(po)), luma(load(pt)))
    h, w = out.shape
    mg = 18
    # Melhor encaixe inteiro (±8 px) da saída na cena revelada pelo mesmo caminho
    best = None
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            e = float(((out[mg:h - mg, mg:w - mg] - truth[mg + dy:h - mg + dy, mg + dx:w - mg + dx]) ** 2).mean())
            if best is None or e < best[0]:
                best = (e, dx, dy)
    _, dx, dy = best
    aligned = np.roll(np.roll(truth, -dy, axis=0), -dx, axis=1)
    band = slice(mg, h - mg)

    def mse(zones):
        vals = []
        for a, b in zones:
            a, b = max(a, mg), min(b, w - mg)
            if b - a >= 4:
                vals.append(float(((out[band, a:b] - aligned[band, a:b]) ** 2).mean()))
        return float(np.mean(vals)) if vals else None

    ms, mc = mse(seams), mse(cores)
    if ms is None or mc is None:
        return _sem(area, metas)
    ps, pc = 10 * np.log10(1 / max(ms, 1e-12)), 10 * np.log10(1 / max(mc, 1e-12))
    check(area, metas[0][0], f"{ps:.1f} / {pc:.1f} dB", ps >= pc - 1.5, metas[0][1])
    jumps = []
    for a, b in seams:
        l0, l1, r0, r1 = max(a - 30, mg), a - 4, b + 4, min(b + 30, w - mg)
        if l1 - l0 >= 4 and r1 - r0 >= 4:
            dl = float((out[band, l0:l1] - aligned[band, l0:l1]).mean())
            dr = float((out[band, r0:r1] - aligned[band, r0:r1]).mean())
            jumps.append(abs(dr - dl))
    if jumps:
        check(area, metas[1][0], f"{max(jumps):.3f}", max(jumps) <= 0.015, metas[1][1])
    else:
        _sem(area, metas[1:])


def _estrelas(root, log):
    area = "ESTRELAS"
    metas = [("pico das estrelas da borda ÷ céu parado", "≥ 0,80"), ("largura (FWHM) das estrelas ÷ céu parado", "≤ 1,5"),
             ("pixels quentes que sobram ÷ 1 foto", "≤ 0,10")]
    ps, pm, p1 = _png(root, "estrelas/parado"), _png(root, "estrelas/girando"), _png(root, "estrelas/uma_foto")
    m = re.search(r"ESTRELAS: pixels quentes ((?:\d+,\d+ ?)+)", log)
    if not (ps and pm):
        return _sem(area, metas)
    still, moving = _same(luma(load(ps)), luma(load(pm)))
    h, w = still.shape
    hot = [tuple(int(v) for v in t.split(",")) for t in m.group(1).split()] if m else []
    # Estrelas: picos isolados no céu parado (fora do chão, das bordas, dos pixels quentes e do estourado)
    bg = float(np.median(still[: int(h * 0.7)]))
    cand = (still == _maxfilt(still, 3)) & (still - bg > 0.08) & (still < 0.92)
    cand[:16] = False
    cand[int(h * 0.72):] = False
    cand[:, :16] = False
    cand[:, w - 16:] = False
    for c, r in hot:
        cand[max(0, r - 10):r + 11, max(0, c - 10):c + 11] = False
    ys, xs = np.nonzero(cand)
    picked = []
    for i in np.argsort(-still[ys, xs]):
        y, x = int(ys[i]), int(xs[i])
        if all((y - a) ** 2 + (x - b) ** 2 >= 144 for a, b in picked):
            picked.append((y, x))
        if len(picked) >= 80:
            break

    def measure(lum, y, x, search):
        win = lum[y - search:y + search + 1, x - search:x + search + 1]
        iy, ix = np.unravel_index(int(np.argmax(win)), win.shape)
        py, px = y - search + int(iy), x - search + int(ix)
        b = float(np.median(lum[max(0, py - 10):py + 11, max(0, px - 10):px + 11]))
        peak = float(lum[py, px]) - b
        core = lum[max(0, py - 5):py + 6, max(0, px - 5):px + 6]
        spread = float(((core - b) > 0.5 * peak).sum()) if peak > 0 else 0.0
        return peak, 2 * (spread / np.pi) ** 0.5

    radius = (h * h + w * w) ** 0.5 / 2
    outer = [(y, x) for y, x in picked if ((y - h / 2) ** 2 + (x - w / 2) ** 2) ** 0.5 > 0.5 * radius]
    use = outer if len(outer) >= 5 else picked
    peaks, widths = [], []
    for y, x in use:
        p0, f0 = measure(still, y, x, 1)
        pm_, fm = measure(moving, y, x, 4)
        if p0 > 0.05 and f0 > 0:
            peaks.append(pm_ / p0)
            widths.append(fm / f0)
    if len(peaks) < 3:
        check(area, metas[0][0], f"{len(peaks)} estrelas", False, metas[0][1])
        check(area, metas[1][0], f"{len(peaks)} estrelas", False, metas[1][1])
    else:
        rp, rf = float(np.median(peaks)), float(np.median(widths))
        check(area, metas[0][0], f"{rp:.2f} ({len(peaks)} estrelas)", rp >= 0.8, metas[0][1])
        check(area, metas[1][0], f"{rf:.2f}", rf <= 1.5, metas[1][1])
    if not (p1 and hot):
        return _sem(area, metas[2:])
    single, moving2 = _same(luma(load(p1)), moving)

    def excess(lum, c, r):
        core = float(lum[max(0, r - 1):r + 2, max(0, c - 1):c + 2].max())
        return core - float(np.median(lum[max(0, r - 6):r + 7, max(0, c - 6):c + 7]))

    worst = max(excess(moving2, c, r) / max(excess(single, c, r), 1e-6) for c, r in hot)
    check(area, metas[2][0], f"{worst:.2f}", worst <= 0.10, metas[2][1])


def _estrelas_polo(root, log):
    """P04b: polo dentro da foto, estrelas finas, luz parada 2×2 no chão, quentes onde o céu anda ≥ 5 px e trilhas de avião.
    As posições vêm do registro, no PNG (x, linha a partir de cima), já onde caem na foto de referência."""
    area = "ESTRELAS polo"
    metas = [("estrelas perto do polo (≤ 1,3 px de giro): pico ÷ céu parado", "≥ 0,80"),
             ("luz parada 2×2 no chão: pico ÷ parado", "≥ 0,80"),
             ("pixels quentes que sobram ÷ 1 foto", "≤ 0,10"),
             ("trilha de avião em 1 foto: sobra ÷ σ do céu de 1 foto", "≤ 1,5"),
             ("trilha em 2 fotos: sobra ÷ σ do céu de 1 foto", "≤ 1,5")]
    m = re.search(r"ESTRELAS POLO: quentes ((?:\d+,\d+ ?)+) · luz (\d+),(\d+) · trilha1 ([-\d.,]+) · trilha2 ([-\d.,]+) · "
                  r"perto do polo ([-\d.,;]+)", log)
    ps, pm, p1 = (_png(root, f"estrelas/polo_{k}") for k in ("parado", "girando", "uma_foto"))
    if not (m and ps and pm and p1):
        return _sem(area, metas)
    still, moving, single = _same(luma(load(ps)), luma(load(pm)), luma(load(p1)))
    h, w = still.shape

    def peak(lum, x, y, search):
        c, r = int(np.floor(x)), int(np.floor(y))
        if not (search <= r < h - search and search <= c < w - search):
            return None
        top = float(lum[r - search:r + search + 1, c - search:c + search + 1].max())
        return top - float(np.median(lum[max(0, r - 10):r + 11, max(0, c - 10):c + 11]))

    ratios = []
    for t in m.group(6).split(";"):
        x, y = (float(v) for v in t.split(","))
        p0, pm_ = peak(still, x, y, 2), peak(moving, x, y, 3)
        if p0 is not None and pm_ is not None and p0 > 0.05:
            ratios.append(pm_ / p0)
    if len(ratios) >= 3:
        rp = float(np.median(ratios))
        check(area, metas[0][0], f"{rp:.2f} ({len(ratios)} estrelas)", rp >= 0.8, metas[0][1])
    else:
        check(area, metas[0][0], f"{len(ratios)} estrelas", False, metas[0][1])
    lx, ly = int(m.group(2)) + 1.0, int(m.group(3)) + 1.0
    l0, l1 = peak(still, lx, ly, 2), peak(moving, lx, ly, 2)
    if l0 is not None and l1 is not None and l0 > 0.05:
        check(area, metas[1][0], f"{l1 / l0:.2f}", l1 / l0 >= 0.8, metas[1][1])
    else:
        check(area, metas[1][0], "luz sumiu" if l0 else SEM, False, metas[1][1])
    hot = [tuple(int(v) for v in t.split(",")) for t in m.group(1).split()]

    def excess(lum, c, r):
        core = float(lum[max(0, r - 1):r + 2, max(0, c - 1):c + 2].max())
        return core - float(np.median(lum[max(0, r - 6):r + 7, max(0, c - 6):c + 7]))

    worst = max(excess(moving, c, r) / max(excess(single, c, r), 1e-6) for c, r in hot)
    check(area, metas[2][0], f"{worst:.2f}", worst <= 0.10, metas[2][1])
    # σ do céu numa foto só: desvio robusto (mediana) do detalhe fino no céu de cima, sem as estrelas
    sky = single[int(h * 0.1):int(h * 0.45), 16:w - 16]
    hp = sky - _gauss(sky, 3)
    sigma = 1.4826 * float(np.median(np.abs(hp - np.median(hp))))

    def residual(seg):
        x0, y0, x1, y1 = seg
        length = float(np.hypot(x1 - x0, y1 - y0))
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        nx, ny = -uy, ux
        vals = []
        for s in np.arange(12, length - 12, 3):
            cx, cy = x0 + ux * s, y0 + uy * s

            def at(t):
                c, r = int(np.floor(cx + nx * t)), int(np.floor(cy + ny * t))
                return float(moving[r, c]) if 0 <= r < h and 0 <= c < w else None

            prof = [at(t) for t in range(-5, 6)]
            bgv = [at(t) for t in list(range(-14, -7)) + list(range(8, 15))]
            if any(v is None for v in prof + bgv):
                continue
            bg = float(np.median(bgv))
            # Integral do excesso no perfil ÷ a do traço desenhado (σ 0,7 px: 1,75 px) = altura de uma trilha igual
            vals.append(sum(v - bg for v in prof) / 1.75)
        return float(np.median(vals)) if vals else None

    for k, meta in ((4, metas[3]), (5, metas[4])):
        seg = [float(v) for v in m.group(k).split(",")]
        rv = residual(seg) if len(seg) == 4 else None
        if rv is None or sigma <= 0:
            _sem(area, [meta])
            continue
        check(area, meta[0], f"{rv / sigma:.2f}", rv / sigma <= 1.5, meta[1])


def _media(root, log):
    area = "MÉDIA"
    metas = [("nitidez com fração de pixel ÷ foto ideal", "≥ 0,90"), ("ruído 8 fotos ÷ 1 foto (≈ 1/√8)", "≤ 0,42")]
    paths = [_png(root, f"media/{k}") for k in ("ideal", "uma", "nitidez", "ruido")]
    if not all(paths):
        return _sem(area, metas)
    ideal, one, sharp, noisy = _same(*[luma(load(p)) for p in paths])
    mg = 24

    def inner(a):
        return a[mg:-mg, mg:-mg]

    r = _edge_mean(inner(sharp)) / max(_edge_mean(inner(ideal)), 1e-6)
    check(area, metas[0][0], f"{r:.2f}", r >= 0.9, metas[0][1])
    tex = inner(np.abs(_gauss(ideal, 2) - _gauss(ideal, 8)))
    flat = tex <= np.percentile(tex, 30)
    nz = lambda x: float(np.std(inner(x - ideal)[flat]))
    q = nz(noisy) / max(nz(one), 1e-6)
    check(area, metas[1][0], f"{q:.2f}", q <= 0.42, metas[1][1])


def _foco(root, log):
    area = "FOCO EMPILHADO"
    metas = [("nitidez nas duas metades ÷ cena nítida (a pior)", "≥ 0,85"), ("halo na divisa ÷ erro da metade borrada", "≤ 0,5"),
             ("degrau na divisa com a 2ª foto +0,3 EV", "≤ 0,02")]
    p = {k: _png(root, f"foco/{k}") for k in ("nitida", "borrada", "junta", "junta_exposicao")}
    if p["nitida"] and p["borrada"] and p["junta"]:
        sharp, soft, merged = _same(luma(load(p["nitida"])), luma(load(p["borrada"])), luma(load(p["junta"])))
        h, w = sharp.shape
        mid, mg = w // 2, 24
        left, right = (slice(mg, h - mg), slice(mg, mid - 48)), (slice(mg, h - mg), slice(mid + 48, w - mg))
        r = min(_edge_mean(merged[left]) / max(_edge_mean(sharp[left]), 1e-6),
                _edge_mean(merged[right]) / max(_edge_mean(sharp[right]), 1e-6))
        check(area, metas[0][0], f"{r:.2f}", r >= 0.85, metas[0][1])
        band = (slice(mg, h - mg), slice(mid - 16, mid + 16))
        halo = float(np.abs(merged[band] - sharp[band]).mean()) / max(float(np.abs(soft[band] - sharp[band]).mean()), 1e-6)
        check(area, metas[1][0], f"{halo:.2f}", halo <= 0.5, metas[1][1])
    else:
        _sem(area, metas[0:2])
    if p["nitida"] and p["junta_exposicao"]:
        sharp, bright = _same(luma(load(p["nitida"])), luma(load(p["junta_exposicao"])))
        h, w = sharp.shape
        mid, mg = w // 2, 24
        d = bright - sharp
        step = abs(float(d[mg:h - mg, mid + 20:mid + 80].mean()) - float(d[mg:h - mg, mid - 80:mid - 20].mean()))
        check(area, metas[2][0], f"{step:.3f}", step <= 0.02, metas[2][1])
    else:
        _sem(area, metas[2:])
    # 4 fotos, a 1ª toda fora de foco e cada terço nítido numa delas (vizinhas com σ 1 e 2): a pior das três faixas
    quatro = ("4 fotos (1ª fora de foco): nitidez ÷ cena nítida no pior terço", "≥ 0,85")
    pq = _png(root, "foco/quatro")
    if p["nitida"] and pq:
        sharp, q = _same(luma(load(p["nitida"])), luma(load(pq)))
        h, w = sharp.shape
        mg = 24
        cuts = [0, w // 3, 2 * w // 3, w]
        zones = [(slice(mg, h - mg), slice(max(cuts[k] + 40, mg), min(cuts[k + 1] - 40, w - mg))) for k in range(3)]
        r = min(_edge_mean(q[z]) / max(_edge_mean(sharp[z]), 1e-6) for z in zones)
        check(area, quatro[0], f"{r:.2f}", r >= 0.85, quatro[1])
    else:
        _sem(area, [quatro])


def _foto_consistencia(root, log):
    metas = [("luz média FOTO 3× − FOTO", "±0,03"), ("meio (p50) FOTO 3× − FOTO", "±0,03"),
             ("saturação FOTO 3× ÷ FOTO", "0,92–1,08"), ("contraste local FOTO 3× ÷ FOTO", "0,90–1,10")]
    d = os.path.join(root, "foto_consistencia")
    names = sorted({f[:-4].rsplit("_", 1)[0] for f in os.listdir(d) if f.endswith(".png")}) if os.path.isdir(d) else []
    if not names:
        return _sem("FOTO 3× = FOTO", metas)
    for n in names:
        area = f"FOTO 3×=FOTO {n}"
        pu, pj = _png(root, f"foto_consistencia/{n}_uma"), _png(root, f"foto_consistencia/{n}_juntada")
        if not (pu and pj):
            _sem(area, metas)
            continue
        one, fused = _same(load(pu), load(pj))
        lo, lf = luma(one), luma(fused)
        dm = float(lf.mean() - lo.mean())
        check(area, metas[0][0], f"{dm:+.3f}", abs(dm) <= 0.03, metas[0][1])
        dp = float(np.percentile(lf, 50) - np.percentile(lo, 50))
        check(area, metas[1][0], f"{dp:+.3f}", abs(dp) <= 0.03, metas[1][1])
        rs = sat(fused) / max(sat(one), 1e-6)
        check(area, metas[2][0], f"{rs:.2f}", 0.92 <= rs <= 1.08, metas[2][1])
        local = lambda l: float(np.abs(l - _gauss(l, 8))[16:-16, 16:-16].mean())
        rc = local(lf) / max(local(lo), 1e-6)
        check(area, metas[3][0], f"{rc:.2f}", 0.9 <= rc <= 1.1, metas[3][1])
        rows.append((area, "bordas finas FOTO 3× ÷ FOTO (só informação)",
                     f"{_edge_mean(lf[16:-16, 16:-16]) / max(_edge_mean(lo[16:-16, 16:-16]), 1e-6):.2f}", "", ""))


def _noite_ruim(root, log):
    area = "NOITE foto ruim"
    base = _png(root, "noite_ruim/sem")
    for label, name in (("ruido", "foto de puro ruído fica de fora (PSNR vs sem ela)"),
                        ("outra_cena", "foto de outra cena fica de fora (PSNR vs sem ela)")):
        other = _png(root, f"noite_ruim/{label}")
        if not (base and other):
            _sem(area, [(name, "≥ 35 dB")])
            continue
        v = psnr(load(other), load(base), reach=2)
        check(area, name, f"{v:.1f} dB", v >= 35, "≥ 35 dB")


def _ghost(obj, clean, spots):
    """Fantasma: |com vulto − sem vulto| em cada lugar do vulto (com folga), menos o fundo. O lugar mais forte é o da
    foto de referência (vulto inteiro); o maior dos outros, dividido por ele, é o fantasma."""
    o, c = _same(obj, clean)
    d = np.abs(o - c)
    h, w = d.shape
    mask = np.zeros(d.shape, bool)
    vals = []
    for x, y, sw, sh in spots:
        x0, x1 = max(0, int((x - 0.02) * w)), min(w, int(round((x + sw + 0.02) * w)))
        y0, y1 = max(0, int((y - 0.03) * h)), min(h, int(round((y + sh + 0.03) * h)))
        mask[y0:y1, x0:x1] = True
        vals.append(float(d[y0:y1, x0:x1].mean()) if y1 > y0 and x1 > x0 else 0.0)
    base = float(np.median(d[~mask])) if (~mask).any() else 0.0
    vals = [max(v - base, 0.0) for v in vals]
    ref = int(np.argmax(vals))
    ghost = max([v for i, v in enumerate(vals) if i != ref] or [0.0])
    return ghost / max(vals[ref], 1e-9), vals[ref]


def _fantasmas(root, log):
    spots = {}
    for m in re.finditer(r"FANTASMA (\w+) (\w+): vulto em ([\d.,;]+)", log):
        spots[(m.group(1), m.group(2))] = [tuple(float(v) for v in s.split(",")) for s in m.group(3).split(";") if s]
    for mode, label in (("noite", "NOITE"), ("foto3x", "FOTO 3×"), ("superzoom", "SUPER ZOOM")):
        area = f"FANTASMA {label}"
        for variant, clean, desc in (("claro", "limpo", "vulto claro andando"), ("escuro", "limpo", "vulto escuro andando"),
                                     ("ceu", "limpo_ceu", "vulto escuro no céu claro (> 0,85)")):
            name = f"{desc}: fantasma ÷ contraste"
            po, pc = _png(root, f"fantasma/{mode}_{variant}"), _png(root, f"fantasma/{mode}_{clean}")
            sp = spots.get((mode, variant))
            if not (po and pc and sp):
                _sem(area, [(name, "≤ 5%")])
                continue
            ratio, contrast = _ghost(luma(load(po)), luma(load(pc)), sp)
            if contrast < 0.01:
                check(area, name, "vulto sumiu", False, "≤ 5%")
                continue
            check(area, name, f"{ratio * 100:.1f}%", ratio <= 0.05, "≤ 5%")


def _lua(root, log):
    area = "LUA 48 MP"
    metas = [("terminou, saída ≥ 40 MP", "sim"), ("usa as 5 fotos (sem corte por memória)", "5/5"),
             ("memória: acréscimo no pico", "≤ 2500 MB")]
    a = log.find("LUA 48 MP: início")
    b = log.find("LUA 48 MP: fim", a + 1) if a >= 0 else -1
    if a < 0 or b < 0:
        return _sem(area, metas)
    inner = log[a:b]
    end = re.search(r"LUA 48 MP: fim · saída (.*?) · .*? · memória pico ([\d.]+) MB \(acréscimo ([\d.]+) MB\)", log[b:])
    mp = re.search(r"\(([\d.]+) MP\)", end.group(1)) if end else None
    out_mp = float(mp.group(1)) if mp else 0.0
    check(area, metas[0][0], f"{out_mp:.1f} MP" if mp else SEM, out_mp >= 40, metas[0][1])
    used = [int(x) for x in re.findall(r"Super resolução revelada: (\d+) fotos", inner)]
    kept = [int(x) for x in re.findall(r"ficam (\d+) fotos", inner)]
    chosen = [int(x) for x in re.findall(r"usando as (\d+) mais nítidas", inner)]
    n = used[-1] if used else 0
    ok = n == 5 and all(k >= 5 for k in kept) and all(c >= 5 for c in chosen)
    value = f"{n}/5" + (f" (cortou p/ {min(kept)})" if kept and min(kept) < 5 else "")
    check(area, metas[1][0], value, ok, metas[1][1])
    if end:
        extra = float(end.group(3))
        check(area, metas[2][0], f"{extra:.0f} MB", extra <= 2500, metas[2][1])
        rows.append((area, "memória pico do processo (só informação)", f"{float(end.group(2)):.0f} MB", "", ""))
    else:
        _sem(area, metas[2:])


def _between(log, start, end):
    a = log.find(start)
    b = log.find(end, a + 1) if a >= 0 else -1
    return log[a:b] if a >= 0 and b >= 0 else None


def _estourado(root, log):
    """P11: janela estourada de 14% (min(cena + ruído, 1) em cada foto). O ajuste do ruído da rajada desabava com ≥ ~6%
    estourado e as junções viravam uma foto só."""
    area = "ESTOURADO"
    metas = [("FOTO 3×: ruído no liso juntada ÷ foto única", "≤ 0,60"),
             ("NOITE: erro juntada vs foto única (vs cena sem ruído)", "≥ +3 dB"),
             ("SUPER ZOOM: ganho com corte − ganho sem corte", "≥ −0,5 dB"),
             ("SUPER ZOOM: σ ajustado com corte ÷ sem corte", "0,5–2")]
    pu, pj = _png(root, "estourado/foto3x_uma"), _png(root, "estourado/foto3x_juntada")
    if pu and pj:
        one, fused = _same(luma(load(pu)), luma(load(pj)))
        # Fora a janela estourada e a beirada dela (no liso dela as duas têm ruído zero e dominariam o "liso"): o que é claro
        # demais ou chapado de verdade (variação < 2 códigos em 9×9 na foto única), alargado 6 px
        chapado = (_maxfilt(one, 4) + _maxfilt(-one, 4)) < 2 / 255
        valid = (_maxfilt(one, 6) < 0.95) & (_maxfilt(fused, 6) < 0.95) & (_maxfilt(chapado.astype(np.float64), 6) < 0.5)
        valid[:16], valid[-16:], valid[:, :16], valid[:, -16:] = False, False, False, False
        if valid.sum() < 1000:
            check(area, metas[0][0], "sem liso", False, metas[0][1])
        else:
            # O liso pela textura da foto única (os 30% menos texturizados fora da janela), o mesmo lugar nas duas
            tex = np.abs(_gauss(one, 2) - _gauss(one, 8))
            sel = valid & (tex <= np.percentile(tex[valid], 30))
            flat_noise = lambda l: float(np.abs(l - _gauss(l, 2))[sel].mean())
            r = flat_noise(fused) / max(flat_noise(one), 1e-6)
            check(area, metas[0][0], f"{r:.2f}", r <= 0.6, metas[0][1])
    else:
        _sem(area, metas[0:1])

    def center(a, side=600):
        h, w = a.shape[:2]
        s = min(side, h, w)
        y0, x0 = (h - s) // 2, (w - s) // 2
        return a[y0:y0 + s, x0:x0 + s]

    pi, p1, pm = (_png(root, f"estourado/noite_{k}") for k in ("ideal", "uma", "juntada"))
    if pi and p1 and pm:
        ideal, one, merged = _same(load(pi), load(p1), load(pm))
        gain = psnr(center(merged), center(ideal), reach=4) - psnr(center(one), center(ideal), reach=4)
        check(area, metas[1][0], f"{gain:+.2f} dB", gain >= 3, metas[1][1])
    else:
        _sem(area, metas[1:2])
    for mode in ("foto3x", "noite"):
        inner = _between(log, f"ESTOURADO {mode}: início", f"ESTOURADO {mode}: fim")
        fit = re.search(r"σ em 0,18 ([\d.]+) · diferença no centro ([\d.]+)", inner or "")
        if fit:
            rows.append((area, f"{mode}: σ ajustado (detalhe) / diferença no centro (só informação)",
                         f"{float(fit.group(1)):.5f} / {float(fit.group(2)):.5f}", "", ""))
    gains, sigmas = {}, {}
    for label in ("corte", "livre"):
        pv, pu1, ps = (_png(root, f"estourado/superzoom_{label}_{k}") for k in ("verdade", "uma", "super"))
        if pv and pu1 and ps:
            t, one, sr = _same(load(pv), load(pu1), load(ps))
            gains[label] = psnr(center(sr), center(t), reach=4) - psnr(center(one), center(t), reach=4)
        inner = _between(log, f"ESTOURADO superzoom_{label}: início", f"ESTOURADO superzoom_{label}: fim")
        fit = re.search(r"ruído a ([-\d.e+]+) b ([-\d.e+]+)", inner or "")
        if fit:
            sigmas[label] = max(float(fit.group(1)) * 0.18 + float(fit.group(2)), 0.0) ** 0.5
    if len(gains) == 2:
        d = gains["corte"] - gains["livre"]
        check(area, metas[2][0], f"{d:+.2f} dB ({gains['corte']:+.2f} / {gains['livre']:+.2f})", d >= -0.5, metas[2][1])
    else:
        _sem(area, metas[2:3])
    if len(sigmas) == 2 and sigmas["livre"] > 0:
        q = sigmas["corte"] / sigmas["livre"]
        check(area, metas[3][0], f"{q:.2f}", 0.5 <= q <= 2, metas[3][1])
    else:
        _sem(area, metas[3:4])


def prevencao(root):
    log = _log_text(root)
    for fn in (_geometria, _longa, _panorama, _estrelas, _estrelas_polo, _media, _foco, _foto_consistencia, _noite_ruim,
               _fantasmas, _lua, _estourado):
        try:
            fn(root, log)
        except Exception as e:  # um teste com saída estranha não derruba o placar: vira FALTA com o erro
            check(f"Prevenção {fn.__name__.strip('_')}", "erro ao medir", type(e).__name__, False, "medir")


def main(root):
    foto_dir = os.path.join(root, "foto")
    names = sorted({f.split("_")[0] for f in (os.listdir(foto_dir) if os.path.isdir(foto_dir) else []) if f.endswith(".jpg")})
    for n in names:
        f = lambda s: os.path.join(root, "foto", f"{n}_{s}.jpg")
        if not os.path.exists(f("apple")):
            continue
        ap, ne = load(f("apple")), load(f("Neutro"))
        la, ln = luma(ap), luma(ne)
        pa, pn = np.percentile(la, [1, 50, 99]), np.percentile(ln, [1, 50, 99])
        check(f"FOTO {n}", "luz média vs Apple", f"{ln.mean():.2f} / {la.mean():.2f}", abs(ln.mean() - la.mean()) <= 0.04, "±0,04")
        check(f"FOTO {n}", "meio (p50) vs Apple", f"{pn[1]:.2f} / {pa[1]:.2f}", abs(pn[1] - pa[1]) <= 0.04, "±0,04")
        check(f"FOTO {n}", "branco (p99) vs Apple", f"{pn[2]:.2f} / {pa[2]:.2f}", pn[2] >= pa[2] - 0.03, "≥ Apple − 0,03")
        check(f"FOTO {n}", "preto (p1) vs Apple", f"{pn[0]:.2f} / {pa[0]:.2f}", pn[0] <= pa[0] + 0.03, "≤ Apple + 0,03")
        r = sat(ne) / max(sat(ap), 1e-6)
        if n.startswith("iphone"):
            check(f"FOTO {n}", "saturação ÷ Apple", f"{r:.2f}", 0.9 <= r <= 1.15, "0,9–1,15")
        else:
            # A Apple revelando RAW de outra marca não é a câmera nativa de ninguém: só informação
            rows.append((f"FOTO {n}", "saturação ÷ Apple (só informação)", f"{r:.2f}", "", ""))
        if os.path.exists(f("apple_100pct")):
            (ea, pka), (en, pkn) = edges(f("apple_100pct")), edges(f("Neutro_100pct"))
            check(f"FOTO {n}", "detalhe 100% vs Apple", f"{en:.1f} / {ea:.1f}", en >= ea, "≥ Apple")
            check(f"FOTO {n}", "pico de borda ÷ Apple (halo)", f"{pkn / max(pka, 1e-6):.2f}", pkn <= 1.3 * pka, "≤ 1,3")

    looks = os.path.join(root, "looks")
    if os.path.isdir(looks):
        bad = []
        # Comparado com o Neutro da mesma foto (cena escura de verdade não é defeito); Noir e Bleach esmagam de propósito
        for n in sorted(os.listdir(looks)):
            files = sorted(os.listdir(os.path.join(looks, n)))
            neutral = [fl for fl in files if fl[3:-4] == "Neutro"]
            if not neutral:
                continue
            ln = luma(load(os.path.join(looks, n, neutral[0])))
            n5, n99 = np.percentile(ln, [5, 99])
            for fl in files:
                name = fl[3:-4]
                if name in ("Neutro", "Noir", "Bleach Bypass"):
                    continue
                l = luma(load(os.path.join(looks, n, fl)))
                p5, p99 = np.percentile(l, [5, 99])
                if p5 < min(0.02, n5 * 0.6) or p99 < min(0.7, n99 - 0.12):
                    bad.append(f"{n}/{name} (p5 {p5:.2f} vs {n5:.2f}, p99 {p99:.2f} vs {n99:.2f})")
        check("Filmes", "filmes com sombra esmagada ou branco apagado", f"{len(bad)}", not bad, "0")
        for b in bad[:12]:
            rows.append(("", "  " + b, "", "", ""))

    pilha = os.path.join(root, "noite_pilha")
    if os.path.isdir(pilha):
        for n in sorted({f.split("_")[0] for f in os.listdir(pilha)}):
            one, eight = os.path.join(pilha, f"{n}_0_uma_foto.jpg"), os.path.join(pilha, f"{n}_1_oito_fotos.jpg")
            if not (os.path.exists(one) and os.path.exists(eight)):
                continue
            a, b = load(one), load(eight)
            ideal_path = os.path.join(pilha, f"{n}_9_ideal.jpg")
            if os.path.exists(real(ideal_path)):
                # Ruído onde a cena sem ruído é lisa, relativo ao brilho de cada uma (a pilha sai mais escura que a foto única)
                ideal = luma(load(ideal_path))
                img_i = Image.fromarray((np.clip(ideal, 0, 1) * 255).astype(np.uint8))
                tex = np.abs(np.asarray(img_i.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
                             - np.asarray(img_i.filter(ImageFilter.GaussianBlur(8))).astype(np.float64) / 255)
                flat = tex <= np.percentile(tex, 30)
                def noise_on(x):
                    l = luma(x)
                    im = Image.fromarray((np.clip(l, 0, 1) * 255).astype(np.uint8))
                    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
                    return float(np.abs(l - bl)[flat].mean())
                # Absoluto (dividir pelo brilho punia a pilha: na foto única o próprio ruído clareia o escuro), menos a
                # textura que a cena sem ruído já tem ali
                base = noise_on(ideal[..., None].repeat(3, -1))
                excess = lambda v: max(v * v - base * base, 0) ** 0.5
                r = excess(noise_on(b)) / max(excess(noise_on(a)), 1e-6)
            else:
                r = local_noise(b) / max(local_noise(a), 1e-6)
            if os.path.exists(real(ideal_path)):
                # 3× como na FOTO: um terço do erro (potência) da foto única, contra a cena sem ruído. Pega ruído e perda de
                # detalhe juntos (só o ruído premiava limpar demais a foto única de comparação)
                ideal_img = load(ideal_path)
                gain = psnr(b, ideal_img, reach=4) - psnr(a, ideal_img, reach=4)
                check(f"NOITE {n}", "erro 8 fotos vs 1 foto (vs cena sem ruído, 3×)", f"{gain:+.2f} dB", gain >= 4.77, "≥ +4,8 dB")
                rows.append((f"NOITE {n}", "ruído 8 fotos ÷ 1 foto (só informação)", f"{r:.2f}", "", ""))
            else:
                check(f"NOITE {n}", "ruído 8 fotos ÷ 1 foto (3×)", f"{r:.2f}", r <= 0.33, "≤ 0,33")
            lb = luma(b)
            check(f"NOITE {n}", "preto (p1)", f"{np.percentile(lb, 1):.3f}", np.percentile(lb, 1) <= 0.06, "≤ 0,06")
            check(f"NOITE {n}", "luz média", f"{lb.mean():.2f}", 0.18 <= lb.mean() <= 0.32, "0,18–0,32")

    # FOTO 3×: 8 fotos juntadas contra a foto única, as duas medidas contra a mesma cena sem ruído
    ff = os.path.join(root, "foto_fusao")
    if os.path.isdir(ff):
        for n in sorted({f.split("_")[0] for f in os.listdir(ff)}):
            p = lambda s: os.path.join(ff, f"{n}_{s}.jpg")
            if not all(os.path.exists(real(p(s))) for s in ("0_ideal", "1_uma", "2_juntada")):
                continue
            ideal, one, fused = load(p("0_ideal")), load(p("1_uma")), load(p("2_juntada"))
            gain = psnr(fused, ideal, reach=4) - psnr(one, ideal, reach=4)
            check(f"FOTO 3× {n}", "erro da juntada vs foto única (vs cena sem ruído)", f"{gain:+.2f} dB", gain >= 4.77, "≥ +4,8 dB")
            r = local_noise(fused) / max(local_noise(one), 1e-6)
            check(f"FOTO 3× {n}", "ruído juntada ÷ foto única", f"{r:.2f}", r <= 0.33, "≤ 0,33")

    # Grão do filme na NOITE em 100%: pontinhos claros soltos em área lisa, além dos que o Neutro já tem
    nf = os.path.join(root, "noite_filme")
    if os.path.isdir(nf):
        from scipy import ndimage
        def specks(path):
            l = np.asarray(Image.open(real(path)).convert("L")).astype(np.float64) / 255
            med = ndimage.median_filter(l, 5)
            tex = ndimage.uniform_filter(np.abs(l - ndimage.gaussian_filter(l, 2)), 9)
            flat = tex < np.percentile(tex, 40)
            return float((((l - med) > 0.08) & flat).sum() / l.size * 1e6)
        for n in sorted({f.split("_")[0] for f in os.listdir(nf)}):
            a, b = os.path.join(nf, f"{n}_ektar_100pct.jpg"), os.path.join(nf, f"{n}_neutro_100pct.jpg")
            a, b = real(a), real(b)
            if os.path.exists(a) and os.path.exists(b):
                extra = specks(a) - specks(b)
                check(f"NOITE filme {n}", "pontinhos do grão por MP (Ektar − Neutro)", f"{extra:.0f}", extra <= 50, "≤ 50")
                # Absoluto (a foto da sala do Alex tinha 5.150): bordas pontilhadas também contam
                rows.append((f"NOITE filme {n}", "pontinhos por MP no Neutro (só informação)", f"{specks(b):.0f}", "", ""))

    # NOITE na mão (caminho da mão do Alex + borrão + 2 fotos tremidas) contra a mesma cena no tripé
    mao = os.path.join(root, "noite_mao")
    if os.path.exists(real(os.path.join(mao, "mao_100pct.jpg"))) and os.path.exists(real(os.path.join(mao, "tripe_100pct.jpg"))):
        em, _ = edges(os.path.join(mao, "mao_100pct.jpg"))
        et, _ = edges(os.path.join(mao, "tripe_100pct.jpg"))
        ideal_path = os.path.join(mao, "ideal_100pct.jpg")
        if os.path.exists(real(ideal_path)):
            # Erro contra a cena sem ruído e sem mexer: na mão no máximo 1 dB pior que no tripé (a soma das bordas
            # subia com o repique de qualquer filtro e não servia de régua). A referência da mão pode estar ~25 px deslocada
            ideal = load(ideal_path)
            pm, pt = psnr(load(os.path.join(mao, "mao_100pct.jpg")), ideal, reach=26), psnr(load(os.path.join(mao, "tripe_100pct.jpg")), ideal, reach=4)
            rows.append(("NOITE na mão", "na mão / tripé contra a cena sem ruído (só informação)", f"{pm:.1f} / {pt:.1f} dB", "", ""))
            one_path = os.path.join(mao, "uma_100pct.jpg")
            if os.path.exists(real(one_path)):
                # 3× como as outras: ⅓ do erro de uma foto só tirada na mão (o tripé do teste não tem borrão nenhum e fica
                # perfeito, 50 dB; "≤ 1 dB pior que ele" era impossível com qualquer movimento de mão)
                po = psnr(load(one_path), ideal, reach=26)
                rows.append(("NOITE na mão", "fim de tarde: erro na mão vs 1 foto na mão (só informação)", f"{pm - po:+.2f} dB", "", ""))
            rows.append(("NOITE na mão", "detalhe (bordas) mão ÷ tripé (só informação)", f"{em / max(et, 1e-6):.2f}", "", ""))
            # O 3× de verdade é no escuro da NOITE: lá a foto única tem o ruído que a junção tira (com ruído leve o erro
            # da foto única é só o borrão da mão, o mesmo da junção, e nenhuma junção chega a ⅓ dele)
            dk = {k: os.path.join(mao, f"{k}_escuro_100pct.jpg") for k in ("mao", "uma", "ideal")}
            if all(os.path.exists(real(v)) for v in dk.values()):
                di = load(dk["ideal"])
                gm, go = psnr(load(dk["mao"]), di, reach=26), psnr(load(dk["uma"]), di, reach=26)
                check("NOITE na mão", "escuro: erro na mão vs 1 foto na mão (contra a cena sem ruído, 3×)", f"{gm - go:+.2f} dB",
                      gm - go >= 4.77, "≥ +4,8 dB")
        else:
            r = em / max(et, 1e-6)
            check("NOITE na mão", "detalhe na mão ÷ tripé (centro 100%)", f"{r:.2f}", r >= 0.9, "≥ 0,90")

    # HDR 3×: 3× a faixa de luz da foto normal = ⅓ do estourado e ⅓ do ruído (relativo) nas sombras
    hd = os.path.join(root, "hdr")
    if os.path.isdir(hd):
        for n in sorted({f.split("_")[0] for f in os.listdir(hd)}):
            pa, pb = os.path.join(hd, f"{n}_0_foto_normal.jpg"), os.path.join(hd, f"{n}_1_hdr.jpg")
            if not (os.path.exists(real(pa)) and os.path.exists(real(pb))):
                continue
            a, b = load(pa), load(pb)
            if a.shape != b.shape:
                continue
            ca, cb = (a.max(-1) >= 0.98).mean(), (b.max(-1) >= 0.98).mean()
            check(f"HDR {n}", "estourado HDR ÷ foto normal (3×)", f"{cb / max(ca, 1e-6):.2f} ({cb * 100:.1f}%)",
                  cb <= ca / 3 or cb <= 0.001, "≤ 0,33")
            la = luma(a)
            im = Image.fromarray((la * 255).astype(np.uint8))
            tex = np.abs(np.asarray(im.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
                         - np.asarray(im.filter(ImageFilter.GaussianBlur(8))).astype(np.float64) / 255)
            sh = (la > 0.03) & (la < 0.25) & (tex < np.percentile(tex, 50))
            if sh.mean() < 0.005:
                continue
            ia, ib = os.path.join(hd, f"{n}_0_foto_normal_ideal.jpg"), os.path.join(hd, f"{n}_1_hdr_ideal.jpg")
            if os.path.exists(real(ia)) and os.path.exists(real(ib)):
                # Ruído = diferença para a mesma foto sem ruído, relativa ao brilho dela (a textura não conta)
                ai, bi = load(ia), load(ib)
                nz = lambda x, xi: float(np.abs(luma(x) - luma(xi))[sh].mean() / max(luma(xi)[sh].mean(), 1e-3))
                r = nz(b, bi) / max(nz(a, ai), 1e-6)
            else:
                def nz(x):
                    l = luma(x)
                    i2 = Image.fromarray((np.clip(l, 0, 1) * 255).astype(np.uint8))
                    bl = np.asarray(i2.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
                    return float(np.abs(l - bl)[sh].mean() / max(l[sh].mean(), 1e-3))
                r = nz(b) / max(nz(a), 1e-6)
            check(f"HDR {n}", "ruído relativo nas sombras HDR ÷ normal (3×)", f"{r:.2f}", r <= 0.33, "≤ 0,33")

    # RETRATO 3×: vazamento do sujeito no fundo logo acima da borda (o laboratório troca o sujeito por magenta e mede o
    # que muda no fundo), ≤ ⅓ do de um desfoque comum
    lp = os.path.join(root, "log.txt")
    if os.path.exists(lp):
        import re
        for m in re.finditer(r"RETRATO (\w+): vazamento nosso ([\d.]+) · desfoque comum ([\d.]+)",
                             open(lp, encoding="utf-8", errors="ignore").read()):
            ours, naive = float(m.group(2)), float(m.group(3))
            ratio = ours / max(naive, 1e-9)
            check(f"RETRATO {m.group(1)}", "vazamento na borda ÷ desfoque comum (3×)", f"{ratio:.2f}", ratio <= 0.33, "≤ 0,33")

    sr = os.path.join(root, "superres")
    if os.path.isdir(sr):
        for n in sorted({f.split("_")[0] for f in os.listdir(sr)}):
            p = lambda s: os.path.join(sr, f"{n}_{s}.jpg")
            if not all(os.path.exists(real(p(s))) for s in ("0_original", "1_uma_ampliada", "2_super")):
                continue
            t = load(p("0_original"))
            gain = psnr(load(p("2_super")), t, reach=4) - psnr(load(p("1_uma_ampliada")), t, reach=4)
            # 3×: um terço do erro (potência) de uma foto ampliada = +4,8 dB
            check(f"SUPER ZOOM {n}", "ganho de PSNR sobre uma ampliada (3×)", f"{gain:+.2f} dB", gain >= 4.77, "≥ +4,8 dB")
            if os.path.exists(real(p("3_original_heic"))):
                rows.append((f"SUPER ZOOM {n}", "PSNR do HEIC 0,9 sozinho / do SUPER ZOOM (só informação)",
                             f"{psnr(load(p('3_original_heic')), t, reach=4):.1f} / {psnr(load(p('2_super')), t, reach=4):.1f} dB", "", ""))

    var = os.path.join(root, "superres_var")
    if os.path.isdir(var):
        for fl in sorted(os.listdir(var)):
            n, label = fl[:-4].split("_", 1)
            p = lambda s: os.path.join(sr, f"{n}_{s}.jpg")
            if not os.path.exists(real(p("0_original"))):
                continue
            t = load(p("0_original"))
            gain = psnr(load(os.path.join(var, fl)), t, reach=4) - psnr(load(p("1_uma_ampliada")), t, reach=4)
            rows.append((f"SUPER ZOOM {n}", f"variação {label} (só informação)", f"{gain:+.2f} dB", "", ""))

    # Alinhamento com deslocamentos de mão de verdade: o "desloca" do registro contra o esperado
    log_path = os.path.join(root, "log.txt")
    if os.path.exists(log_path):
        import re
        lines = open(log_path, encoding="utf-8", errors="ignore").read().splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"ALINHAMENTO (\w+): esperado (.*)", line)
            if not m:
                continue
            kind = m.group(1)
            expected = [tuple(map(float, p.split(","))) for p in re.findall(r"\(([-\d.]+, [-\d.]+)\)", m.group(2))]
            got = []
            for nxt in lines[i + 1:]:
                if nxt.startswith(f"ALINHAMENTO {kind}: fim"):
                    break
                g = re.search(r"desloca ([-\d.]+), ([-\d.]+) px", nxt)
                if g:
                    got.append((float(g.group(1)), float(g.group(2))))
            if len(got) != len(expected):
                check(f"ALINHAMENTO {kind}", "fotos alinhadas", f"{len(got)}/{len(expected)}", False, "todas")
                continue
            err = max(((a - x) ** 2 + (b - y) ** 2) ** 0.5 for (a, b), (x, y) in zip(got, expected))
            check(f"ALINHAMENTO {kind}", "erro máximo (deslocamento de mão real)", f"{err:.2f} px", err <= 0.5, "≤ 0,5 px")

    prevencao(root)

    width = max(len(r[1]) for r in rows) if rows else 10
    ok = sum(1 for r in rows if r[4] == "OK")
    total = sum(1 for r in rows if r[4])
    for area, name, value, goal, status in rows:
        print(f"{area:22s} {name:{width}s} {value:>14s}  meta {goal:14s} {status}")
    print(f"\nPlacar: {ok}/{total} metas cumpridas")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
