"""Revisor R3: testes complementares da origem A x C e da precisao numerica.

 (a) passo de tempo: memorias nos niveis A e C com dt = 0.25 e dt = 0.1 (derivada de 4a ordem e soma de Riemann);
 (b) inicio da janela: (A - C)/C em funcao de M f0 (0.004 ... 0.012). Se a diferenca vem do trecho PN do
     substituto, ela cai quando a janela comeca dentro da parte de RN (t0 > -3500 M do pico);
 (c) na parte PN: a taxa do nivel A dividida pela ordem dominante contra |h22/h22_LO|^2 (correcoes PN de amplitude),
     e a previsao analitica |H22|^2 com a amplitude PN ate 2.5PN (Blanchet LRR 2014, eq. do H22);
 (d) modos que faltam: NRHybSur3dq8 (extrapolado, tem (3,1) e (4,2)) com e sem esses modos, e contra o _CCE.
Saida: resultados/revisao/rev_R3_modos_janela_dt.txt
"""
import functools
import os
import time

import numpy as np

from rev_R3_comum import B, gram, CalculadoraMemoria, taxas_instantaneas, x_de_h22, h30_pn_lo, SAIDA

NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def vetores(q, c1, c2, f0=0.004, dt=0.25):
    t, h = B.gerar(q, c1, c2, f0=f0, dt=dt)
    vA = B.vetor(B.memorias(q, c1, c2, f0=f0, dt=dt, nivel="A", t=t, h=h)[0])[0]
    vC = B.vetor(B.memorias(q, c1, c2, f0=f0, dt=dt, nivel="C", t=t, h=h)[0])[0]
    tp =t[np.argmax(sum(np.abs(v) ** 2 for v in h.values()))]
    return vA, vC, t[0] - tp


def amp22_pn(x, nu):
    """|H22| com a amplitude PN ate 2.5PN (parte real e imaginaria), Blanchet LRR 2014."""
    H = (1 + x * (-107 / 42 + 55 / 42 * nu) + 2 * np.pi * x ** 1.5
         + x ** 2 * (-2173 / 1512 - 1069 / 216 * nu + 2047 / 1512 * nu ** 2)
         + x ** 2.5 * (-107 * np.pi / 21 + (34 * np.pi / 21 - 24j) * nu))
    return np.abs(H)


@functools.lru_cache(maxsize=1)
def _sur_ext():
    import gwsurrogate
    return gwsurrogate.LoadSurrogate("NRHybSur3dq8")


def spin_nivelA(t, h, lista, dt):
    calc = CalculadoraMemoria(lista)
    H = np.stack([h[k] for k in lista], axis=1)
    Hd = B.derivada4(H, dt)
    m = calc.memorias_gram(*gram(H, Hd, dt))
    return m["spin"][(3, 0)].imag, m["deslocamento"][(2, 0)].real, m["giroscopica"][(3, 0)].real


if __name__ == "__main__":
    t00 = time.time()
    # (a) passo de tempo
    log("(a) passo de tempo: (v(dt=0.1) - v(dt=0.25)) / |v(dt=0.25)| nos niveis A e C")
    for (q, c1, c2) in [(1.0, 0.0, 0.0), (8.0, 0.0, 0.0), (2.0, 0.8, -0.8)]:
        a25, c25, _ = vetores(q, c1, c2, dt=0.25)
        a10, c10, _ = vetores(q, c1, c2, dt=0.1)
        log("  q=%.0f chi=(%+.1f,%+.1f) A: " % (q, c1, c2) + " ".join("%s %+.1e" % (n, x) for n, x in
                                                                   zip(NOMES, (a10 - a25) / np.abs(a25))))
        log("  %-19s C: " % "" + " ".join("%s %+.1e" % (n, x) for n, x in zip(NOMES, (c10 - c25) / np.abs(c25))))
        log("  %-19s (A-C)/C com dt=0.1: " % "" + " ".join("%s %+.4f" % (n, x) for n, x in
                                                          zip(NOMES, (a10 - c10) / np.abs(c10))))
    log("  (%.0f s)" % (time.time() - t00))

    # (b) inicio da janela
    log()
    log("(b) (A - C)/C em funcao do inicio da janela M f0 (t0 = inicio relativo ao pico)")
    for (q, c1, c2) in [(1.0, 0.0, 0.0), (4.0, 0.0, 0.0), (8.0, 0.0, 0.0), (1.0, 0.6, 0.6)]:
        for f0 in (0.004, 0.006, 0.008, 0.010, 0.012):
            vA, vC, t0 = vetores(q, c1, c2, f0=f0)
            d = (vA - vC) / np.abs(vC)
            log("  q=%.0f chi=(%+.1f,%+.1f) M f0=%.3f t0=%7.0f M: spin30 %+.4f giro30 %+.4f desl20 %+.4f cm20 %+.4f (C: spin30 %.5f)"
                % (q, c1, c2, f0, t0, d[2], d[6], d[0], d[3], vC[2]))
    log("  (%.0f s)" % (time.time() - t00))

    # (c) taxa do nivel A na parte PN e amplitude PN do (2,2)
    log()
    log("(c) parte PN: |hB_30|/LO (nivel A) contra |h22|^2/|h22_LO|^2 do substituto e contra |H22_PN(2.5PN)|^2")
    c_osc, _ = B.calculadoras()
    for q in (1.0, 8.0):
        t, h = B.gerar(q, 0.0, 0.0)
        eta = q / (1 + q) ** 2
        Losc = B.lista_osc()
        sel = slice(0, 4096)                               # so o comeco da janela
        H = np.stack([h[k] for k in Losc], axis=1)
        Hd = B.derivada4(H, 0.25)
        hB, _, _ = taxas_instantaneas(c_osc, H[sel], Hd[sel], [(3, 0)])
        x = x_de_h22(t, h[(2, 2)])[sel]
        lo = h30_pn_lo(x, eta)
        a22 = np.abs(h[(2, 2)][sel]) / (8 * np.sqrt(np.pi / 5) * eta * x)
        for k in (200, 2000, 3800):
            log("  q=%.0f x=%.4f: A/LO = %.4f ; (|h22|/|h22_LO|)^2 = %.4f ; |H22_PN|^2 = %.4f ; C/LO = %.4f"
                % (q, x[k], abs(hB[k, 0]) / lo[k], a22[k] ** 2, amp22_pn(x[k], eta) ** 2,
                   abs(h[(3, 0)][k]) / lo[k]))
        del t, h, H, Hd
    log("  (%.0f s)" % (time.time() - t00))

    # (d) modos que faltam
    log()
    log("(d) modos (3,1) e (4,2): NRHybSur3dq8 (extrapolado) nivel A, com e sem esses modos; e o _CCE com a mesma lista")
    base = B.lista_osc()
    extra = [(3, 1), (3, -1), (4, 2), (4, -2)]
    for q in (1.0, 2.0, 4.0, 8.0):
        t, h, _ = _sur_ext()(q, [0, 0, 0], [0, 0, 0], dt=0.25, f_low=0.004)
        h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
        s0, d0, g0 = spin_nivelA(t, h, base, 0.25)
        s1, d1, g1 = spin_nivelA(t, h, base + extra, 0.25)
        del t, h
        t, h = B.gerar(q, 0.0, 0.0)
        sc, dc, gc = spin_nivelA(t, h, base, 0.25)
        sC = (np.sum(h[(3, 0)]) * 0.25).imag
        del t, h
        log("  q=%.0f: spin30 ext %.6f -> com (3,1),(4,2) %.6f (%+.2e rel.) ; desl20(janela) %+.2e rel. ; giro30 %+.2e rel."
            % (q, s0, s1, (s1 - s0) / s0, (d1 - d0) / d0, (g1 - g0) / g0))
        log("        spin30 _CCE nivel A %.6f (ext/CCE - 1 = %+.4f) ; nivel C (int h30) %.6f"
            % (sc, s0 / sc - 1, sC))
    log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3_modos_janela_dt.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
