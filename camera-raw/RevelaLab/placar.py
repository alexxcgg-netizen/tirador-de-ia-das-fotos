"""Placar do laboratório: mede as metas do BRIEFING.md nas imagens do ramo revela-lab.

Uso: python3 placar.py <pasta do ramo revela-lab>
Precisa de numpy e Pillow. Imprime cada meta com o número, a meta e OK / FALTA.
"""
import os
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


def main(root):
    names = sorted({f.split("_")[0] for f in os.listdir(os.path.join(root, "foto")) if f.endswith(".jpg")})
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
            gain = psnr(fused, ideal) - psnr(one, ideal)
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
            def nz(x):
                l = luma(x)
                i2 = Image.fromarray((np.clip(l, 0, 1) * 255).astype(np.uint8))
                bl = np.asarray(i2.filter(ImageFilter.GaussianBlur(2))).astype(np.float64) / 255
                return float(np.abs(l - bl)[sh].mean() / max(l[sh].mean(), 1e-3))
            r = nz(b) / max(nz(a), 1e-6)
            check(f"HDR {n}", "ruído relativo nas sombras HDR ÷ normal (3×)", f"{r:.2f}", r <= 0.33, "≤ 0,33")

    # RETRATO 3×: vazamento da cor do sujeito no fundo, logo acima da borda, ≤ ⅓ do de um desfoque comum
    rt = os.path.join(root, "retrato")
    if os.path.isdir(rt):
        import re
        radii = {}
        lp = os.path.join(root, "log.txt")
        if os.path.exists(lp):
            for m in re.finditer(r"RETRATO (\w+): raio ([\d.]+) px em (\d+) px", open(lp, encoding="utf-8", errors="ignore").read()):
                radii[m.group(1)] = (float(m.group(2)), float(m.group(3)))
        from scipy import ndimage
        for n in sorted({f.split("_")[0].split(".")[0] for f in os.listdir(rt)}):
            po, pc, pm = os.path.join(rt, f"{n}.jpg"), os.path.join(rt, f"{n}_0_cena.jpg"), os.path.join(rt, f"{n}_0_mapa.jpg")
            if not all(os.path.exists(real(x)) for x in (po, pc, pm)) or n not in radii:
                continue
            out, cena = load(po), load(pc)
            w = load(pm)[..., 0]
            if out.shape != cena.shape or w.shape != out.shape[:2]:
                continue
            r = radii[n][0] * out.shape[1] / radii[n][1]
            lin = cena ** 2.2
            disk = lambda x: ndimage.uniform_filter(x, size=max(3, int(2 * r) | 1))
            ideal = (np.stack([disk(lin[..., c] * w) for c in range(3)], -1) / np.maximum(disk(w), 1e-4)[..., None]) ** (1 / 2.2)
            naive = np.stack([disk(lin[..., c]) for c in range(3)], -1) ** (1 / 2.2)
            band = (w > 0.98) & (ndimage.uniform_filter((w < 0.5).astype(float), size=int(2 * r) | 1) > 0)
            if band.sum() < 100:
                continue
            e_ours = float(np.abs(out - ideal)[band].mean())
            e_naive = float(np.abs(naive - ideal)[band].mean())
            ratio = e_ours / max(e_naive, 1e-6)
            check(f"RETRATO {n}", "vazamento na borda ÷ desfoque comum (3×)", f"{ratio:.2f}", ratio <= 0.33, "≤ 0,33")

    sr = os.path.join(root, "superres")
    if os.path.isdir(sr):
        for n in sorted({f.split("_")[0] for f in os.listdir(sr)}):
            p = lambda s: os.path.join(sr, f"{n}_{s}.jpg")
            if not all(os.path.exists(real(p(s))) for s in ("0_original", "1_uma_ampliada", "2_super")):
                continue
            t = load(p("0_original"))
            gain = psnr(load(p("2_super")), t) - psnr(load(p("1_uma_ampliada")), t)
            # 3×: um terço do erro (potência) de uma foto ampliada = +4,8 dB
            check(f"SUPER ZOOM {n}", "ganho de PSNR sobre uma ampliada (3×)", f"{gain:+.2f} dB", gain >= 4.77, "≥ +4,8 dB")
            if os.path.exists(real(p("3_original_heic"))):
                rows.append((f"SUPER ZOOM {n}", "PSNR do HEIC 0,9 sozinho / do SUPER ZOOM (só informação)",
                             f"{psnr(load(p('3_original_heic')), t):.1f} / {psnr(load(p('2_super')), t):.1f} dB", "", ""))

    var = os.path.join(root, "superres_var")
    if os.path.isdir(var):
        for fl in sorted(os.listdir(var)):
            n, label = fl[:-4].split("_", 1)
            p = lambda s: os.path.join(sr, f"{n}_{s}.jpg")
            if not os.path.exists(p("0_original")):
                continue
            t = load(p("0_original"))
            gain = psnr(load(os.path.join(var, fl)), t) - psnr(load(p("1_uma_ampliada")), t)
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

    width = max(len(r[1]) for r in rows) if rows else 10
    ok = sum(1 for r in rows if r[4] == "OK")
    total = sum(1 for r in rows if r[4])
    for area, name, value, goal, status in rows:
        print(f"{area:22s} {name:{width}s} {value:>14s}  meta {goal:14s} {status}")
    print(f"\nPlacar: {ok}/{total} metas cumpridas")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
