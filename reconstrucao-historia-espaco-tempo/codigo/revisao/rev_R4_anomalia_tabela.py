"""Revisor R4, tarefa 2 (diagnostico 3): a tabela "memorias x e0" do 07 §3.5 (exp12 parte 2) com l0 livre.

Configuracao A do exp12 (M = 65, q = 1.2, chi = (+0.3, -0.2)), janela desde 10 Hz, multipolos globais
(B.vetor: desl20, desl40, spin30, cm20, cm40, giro10, giro30) relativos ao circular, para e0 = 0.05 ... 0.3 e
l0 = 0, pi/2, pi, 3pi/2: faixa (min, max) sobre l0. Mostra se o efeito de e0 e maior que o de l0.
Tambem: frequencia do (2,2) em tempos fixos antes do pico para B (e0 = 0.2, q = 2) com l0 = 0 e pi.
Saida: resultados/revisao/rev_R4_anomalia_tabela.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
if __name__ == "__main__":
    v0 = C.B.vetor(C.mem_ehm(1.2, 0.3, -0.2, 65.0, 0.0, 0.0, usar_cache=False)[0])[0]
    log("Memorias globais (A do exp12, M = 65, q = 1.2) relativas ao circular: valor com l0 = 0 (o do exp12) e faixa [min, max] sobre l0 = 0, pi/2, pi, 3pi/2")
    for e0 in (0.05, 0.1, 0.2, 0.3):
        rel = []
        for l0 in (0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi):
            v = C.B.vetor(C.mem_ehm(1.2, 0.3, -0.2, 65.0, e0, l0, usar_cache=False)[0])[0]
            rel.append((v - v0) / np.abs(v0))
        rel = np.array(rel)
        log("  e0 = %.2f: " % e0 + " ; ".join("%s %+.4f [%+.4f, %+.4f]" % (n, rel[0, i], rel[:, i].min(), rel[:, i].max())
                                             for i, n in enumerate(NOMES) if n in ("desl20", "spin30", "cm20", "giro10")))
    log()
    log("Frequencia de onda do (2,2), M omega_22, em tempos fixos antes do pico, B (e0 = 0.2, q = 2, M = 72.59): l0 = 0 x pi")
    q, c1, c2, M = 2.0, 0.05960457850002948, 0.0, 72.5875185658003
    f0 = M * C.Dt.MSUN_S * C.F_FIS
    om = {}
    for l0 in (0.0, np.pi):
        t, h = C.gerar(q, c1, c2, f0, 0.2, l0)
        tp = t[np.argmax(np.abs(h[(2, 2)]))]
        w = -np.gradient(np.unwrap(np.angle(h[(2, 2)])), t)
        om[l0] = (t - tp, w, np.abs(h[(2, 2)]))
        del t, h
    tc, wc, ac = om[0.0]
    tp_, wp, ap = om[np.pi]
    for ti in (-2000.0, -1000.0, -500.0, -300.0, -100.0, -50.0, -20.0, -5.0):
        a, b = np.interp(ti, tc, wc), np.interp(ti, tp_, wp)
        aa, ab = np.interp(ti, tc, ac), np.interp(ti, tp_, ap)
        log("  t = %+7.0f M: M omega22 l0=0 %.5f, l0=pi %.5f (razao - 1 = %+.2e) ; |h22| razao - 1 = %+.2e" % (ti, a, b, b / a - 1, ab / aa - 1))
    # tempo antes do pico em que omega22 atinge valores fixos (media movel para tirar a oscilacao excentrica)
    for wv in (0.06, 0.08, 0.1, 0.15):
        ts = []
        for (tt, ww, _) in (om[0.0], om[np.pi]):
            k = 400
            wm = np.convolve(ww, np.ones(k) / k, mode="same")
            sel = tt < -30
            i = np.where(sel & (wm >= wv))[0][0]
            ts.append(tt[i])
        log("  M omega22 (media movel de 40 M) = %.2f atingida em t = %.1f M (l0 = 0) e %.1f M (l0 = pi): diferenca %+.1f M" % (wv, ts[0], ts[1], ts[1] - ts[0]))
    with open(os.path.join(C.RES, "rev_R4_anomalia_tabela.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
