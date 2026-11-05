"""Placar do laboratório: mede as metas do BRIEFING.md nas imagens do ramo revela-lab.

Uso: python3 placar.py <pasta do ramo revela-lab>
Precisa de numpy e Pillow. Imprime cada meta com o número, a meta e OK / FALTA.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

LUMA = np.array([0.2126, 0.7152, 0.0722])


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64) / 255


def luma(a):
    return a @ LUMA


def sat(a):
    return float((a.max(-1) - a.min(-1)).mean())


def edges(path):
    g = np.asarray(Image.open(path).convert("L").filter(ImageFilter.FIND_EDGES)).astype(np.float64)
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


def psnr(a, b, reach=16):
    """PSNR depois de achar o melhor encaixe (os recortes podem sair alguns pixels deslocados)."""
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    a, b = a[:h, :w], b[:h, :w]
    m = reach
    core = a[m:h - m, m:w - m]
    best = min(((core - b[m + dy:h - m + dy, m + dx:w - m + dx]) ** 2).mean()
               for dy in range(-m, m + 1) for dx in range(-m, m + 1))
    return 10 * np.log10(1 / max(best, 1e-12))


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
        check(f"FOTO {n}", "saturação ÷ Apple", f"{r:.2f}", 0.9 <= r <= 1.15, "0,9–1,15")
        if os.path.exists(f("apple_100pct")):
            (ea, pka), (en, pkn) = edges(f("apple_100pct")), edges(f("Neutro_100pct"))
            check(f"FOTO {n}", "detalhe 100% vs Apple", f"{en:.1f} / {ea:.1f}", en >= ea, "≥ Apple")
            check(f"FOTO {n}", "pico de borda ÷ Apple (halo)", f"{pkn / max(pka, 1e-6):.2f}", pkn <= 1.3 * pka, "≤ 1,3")

    looks = os.path.join(root, "looks")
    if os.path.isdir(looks):
        bad = []
        for n in sorted(os.listdir(looks)):
            for fl in sorted(os.listdir(os.path.join(looks, n))):
                l = luma(load(os.path.join(looks, n, fl)))
                p5, p99 = np.percentile(l, [5, 99])
                if p5 < 0.02 or p99 < 0.7:
                    bad.append(f"{n}/{fl[3:-4]} (p5 {p5:.2f}, p99 {p99:.2f})")
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
            r = local_noise(b) / max(local_noise(a), 1e-6)
            check(f"NOITE {n}", "ruído 8 fotos ÷ 1 foto", f"{r:.2f}", r <= 0.5, "≤ 0,50")
            lb = luma(b)
            check(f"NOITE {n}", "preto (p1)", f"{np.percentile(lb, 1):.3f}", np.percentile(lb, 1) <= 0.06, "≤ 0,06")
            check(f"NOITE {n}", "luz média", f"{lb.mean():.2f}", 0.18 <= lb.mean() <= 0.32, "0,18–0,32")

    sr = os.path.join(root, "superres")
    if os.path.isdir(sr):
        for n in sorted({f.split("_")[0] for f in os.listdir(sr)}):
            p = lambda s: os.path.join(sr, f"{n}_{s}.jpg")
            if not all(os.path.exists(p(s)) for s in ("0_original", "1_uma_ampliada", "2_super")):
                continue
            t = load(p("0_original"))
            gain = psnr(load(p("2_super")), t) - psnr(load(p("1_uma_ampliada")), t)
            check(f"SUPER ZOOM {n}", "ganho de PSNR sobre uma ampliada", f"{gain:+.2f} dB", gain >= 1.5, "≥ +1,5 dB")

    width = max(len(r[1]) for r in rows) if rows else 10
    ok = sum(1 for r in rows if r[4] == "OK")
    total = sum(1 for r in rows if r[4])
    for area, name, value, goal, status in rows:
        print(f"{area:22s} {name:{width}s} {value:>14s}  meta {goal:14s} {status}")
    print(f"\nPlacar: {ok}/{total} metas cumpridas")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
