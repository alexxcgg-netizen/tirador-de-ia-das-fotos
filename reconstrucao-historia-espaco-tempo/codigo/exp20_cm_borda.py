"""L03: a parte nula da memoria de CM numa banda da inspiral e um termo de borda (hipotese H03.8).

Na orbita circular adiabatica a taxa da parte nula da CM e zero ate 1.5PN (exp20_pn (b)). Mas numa banda finita
[t_a, t_b] o integrando W tem a parte nao adiabatica a_a adot_b^* (a = amplitude lenta), cuja integral e ~ (1/2) Delta(a_a a_b^*):
um termo de borda proporcional a |h|^2 nas pontas, nao suprimido por eps = Adot/(A omega).
Previsao: cm_nula(banda) ~ (1/2) sum_ab [Re Delta(h_a hbar_b) KA_re + Im Delta(h_a hbar_b) KA_im] (nucleos de exp20_pn_comum,
modos do substituto), com h nas pontas da banda; contra o valor do substituto (nivel A).
Saida: resultados/exp20_cm_borda.txt
"""
import os

import numpy as np

import exp20_comum as C
import exp20_pn_comum as P
import observaveis as O
from deteccao import MSUN_S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODOS_SUR = tuple(k for k in P.MODOS_ABFO if k not in ((3, 1), (4, 2), (4, 1))) + ((5, 5),)
BORDAS = [0.002, 0.003, 0.004, 0.006, 0.008, 0.010, 0.012, 0.014]
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    lista, K = P.nucleos(MODOS_SUR)
    KB_re, KB_im, KA_re, KA_im = K[("cm", (2, 0))]
    Mref = 50.0
    for nome, q, c1, c2 in [("q1", 1.0, 0.0, 0.0), ("A", 1.2, 0.3, -0.2), ("q4a", 4.0, -0.5, -0.5)]:
        freqs = [b / (Mref * MSUN_S) for b in BORDAS]
        rr, (t, h) = C.janelas(q, c1, c2, Mref, freqs, devolver_onda=True)
        # parte nula da CM por janela: cm total menos a ordinaria (-1.5 M_f desl / Dfrak)
        from harmonicos import Dfrak
        nula = [m["cm"][(2, 0)].real + 1.5 * aux["M_f"] * m["deslocamento"][(2, 0)].real / Dfrak(2) for m, aux in rr]
        tis = [aux["t_i"] for m, aux in rr]
        hv = {}
        for ti in tis:
            hv[ti] = np.array([O._interp_em(t, h[k], ti) for k in lista])
        fim = np.array([h[k][-1] for k in lista])
        log("sistema %s (q=%g, chi=(%+.1f, %+.1f)): parte nula da CM (2,0) por banda, substituto contra termo de borda" % (nome, q, c1, c2))
        for j in range(len(BORDAS) - 1):
            sur = nula[j] - nula[j + 1]
            ha, hb = hv[tis[j]], hv[tis[j + 1]]
            D = np.outer(hb, hb.conj()) - np.outer(ha, ha.conj())
            mm = np.array([k[1] for k in lista])
            mask = mm[:, None] == mm[None, :]
            prev = 0.5 * np.sum((D.real * KA_re + D.imag * KA_im) * mask)
            log("  [%.3f, %.3f]: substituto %+.4e ; borda (1/2) Delta(h hbar) K_A %+.4e ; razao %.4f"
                % (BORDAS[j], BORDAS[j + 1], sur, prev, prev / sur))
        # janela inteira: borda final ~ 0 (A -> 0 no fim do toque), so a borda inicial e a fusao
        D = np.outer(fim, fim.conj()) - np.outer(hv[tis[0]], hv[tis[0]].conj())
        prev = 0.5 * np.sum((D.real * KA_re + D.imag * KA_im) * (mm[:, None] == mm[None, :]))
        log("  janela inteira desde M f = 0.002: parte nula %+.4e ; termo de borda das pontas %+.4e (a fusao nao e adiabatica)"
            % (nula[0], prev))
        del t, h
    with open(os.path.join(RAIZ, "resultados", "exp20_cm_borda.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
