"""Revisor R3: estimativa da parte ORDINARIA da memoria de spin (3,0) e do peso dos modos que faltam.

Parte ordinaria = Delta Im[eth qbar N] / (Dfrak D^2), mudanca do aspecto de momento angular magnetico l = 3 entre
as pontas da janela. Analise dimensional: N_A tem dimensao M^2 (como J); o octupolo de corrente S_3 tem M^4. Na teoria
linear N^B_l ~ S_l^(l-1), isto e, N^B_3 ~ d^2 S_30/du^2 (o octupolo estatico do Kerr final, S_3 = -M a^3, nao entra).
  inicio (orbita quase circular, ordem dominante): S_30 ~ nu (1-3 nu) x^(-5/2) [M^4] (parte m = 0 de
     sum m_A x x (x cross v)), dx/dt = (64/5) nu x^5  ->  d^2S_30/dt^2 = -614.4 nu^3 (1-3 nu) x^(11/2) [M^2]
  fim (Kerr com recuo v, S_ijk ~ STF(x^i x^j J^k), x = v t): d^2 S/dt^2 ~ 2 v^2 J
  termos quadraticos em C no aspecto 'chapeu' (inicio da janela): ~ |h22(u0)|^2; no fim C e eletrico e axissimetrico
     (so m = 0), e o produto de dois campos eletricos axissimetricos nao tem parte magnetica.
Compara-se com a parte nula Dfrak D^2 int Psi (escala do fluxo) e com a diferenca A - C. Fatores O(1) de normalizacao
nao entram (a conclusao vale se a razao for << 1e-2).
Tambem: fracao da energia irradiada em cada modo (q = 8) perto de x = 0.1 e no total, para estimar modos l >= 6.
Saida: resultados/revisao/rev_R3_ordinaria.txt
"""
import os

import numpy as np

from rev_R3_comum import B, gram, Dfrak, SAIDA, x_de_h22
from harmonicos import D2

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    import surfinBH
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    for q in (1.0, 8.0):
        eta = q / (1 + q) ** 2
        t, h = B.gerar(q, 0.0, 0.0)
        mA, aux = B.memorias(q, 0.0, 0.0, t=t, h=h, nivel="A")
        mC, _ = B.memorias(q, 0.0, 0.0, t=t, h=h, nivel="C")
        c_osc, _ = B.calculadoras()
        Losc = B.lista_osc()
        H = np.stack([h[k] for k in Losc], axis=1)
        Hd = B.derivada4(H, 0.25)
        Bm, Am = gram(H, Hd, 0.25)
        m = c_osc.memorias_gram(Bm, Am)
        fluxo = abs(m["spin_potencial"][(3, 0)] * Dfrak(3) * D2(3))       # |Dfrak D^2 int Psi| (parte nula)
        dif = abs(mA["spin"][(3, 0)] - mC["spin"][(3, 0)]) / abs(mC["spin"][(3, 0)])
        x0 = aux["x0"]
        n_ini = 614.4 * eta ** 3 * (1 - 3 * eta) * x0 ** 5.5
        chif, _ = fit.chif(q, [0, 0, 0], [0, 0, 0])
        vf, _ = fit.vf(q, [0, 0, 0], [0, 0, 0])
        mf, _ = fit.mf(q, [0, 0, 0], [0, 0, 0])
        J = np.linalg.norm(chif) * mf ** 2
        n_fim = 2 * np.linalg.norm(vf) ** 2 * J
        quad = abs(h[(2, 2)][0]) ** 2
        log("q = %.0f: escala da parte nula |Dfrak D^2 int Psi|_30 = %.3e ; |A - C|/C (spin30) = %.4f" % (q, fluxo, dif))
        log("   ordinaria linear, inicio: |d2 S30/dt2| ~ %.2e (razao %.1e) ; fim (recuo %.2e c, J_f = %.3f): 2 v^2 J ~ %.2e (razao %.1e)"
            % (n_ini, n_ini / fluxo, np.linalg.norm(vf), J, n_fim, n_fim / fluxo))
        log("   ordinaria quadratica em C no inicio: |h22(u0)|^2 = %.2e (razao %.1e)" % (quad, quad / fluxo))
        # energia por modo
        E_modo = {}
        for j, k in enumerate(Losc):
            lm = (k[0], abs(k[1]))
            E_modo[lm] = E_modo.get(lm, 0) + Bm[j, j].real / (16 * np.pi)
        Etot = sum(E_modo.values())
        log("   energia irradiada por modo (fracao do total, janela inteira): "
            + ", ".join("%s %.2e" % (k, v / Etot) for k, v in sorted(E_modo.items(), key=lambda z: -z[1])))
        x = x_de_h22(t, h[(2, 2)])
        tp = t[np.argmax(np.abs(h[(2, 2)]))]
        k = np.argmin(np.abs(x[t < tp - 300] - 0.1))
        fl = {}
        for j, kk in enumerate(Losc):
            lm = (kk[0], abs(kk[1]))
            fl[lm] = fl.get(lm, 0) + abs(Hd[k, j]) ** 2
        ft = sum(fl.values())
        log("   fluxo de energia por modo em x = 0.1 (t - t_pico = %.0f M): " % (t[k] - tp)
            + ", ".join("%s %.2e" % (kk, v / ft) for kk, v in sorted(fl.items(), key=lambda z: -z[1])))
        del t, h, H, Hd
    with open(os.path.join(SAIDA, "rev_R3_ordinaria.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
