"""Revisor R3: convencoes e fatores (memoria de CM ordinaria na janela, momento irradiado, M_f, Favata com spins).

 (1) memoria de CM (2,0) do nivel A: a parte ordinaria usa o deslocamento TOTAL (Favata antes da janela + janela).
     Compara com a versao de janela (so o deslocamento da janela) e com M_f Phi_f - M_i Phi_i; mede a fracao de cm20
     que vem do deslocamento anterior a janela; testa uma janela de comprimento quase nulo (50 M).
 (2) momento_irradiado: compara com a integral direta (1/16 pi) int n |hdot|^2 numa grade fina, modos sinteticos.
 (3) M_f: tamanho do termo 2PN da energia de ligacao que falta em E_rad.
Saida: resultados/revisao/rev_R3_cm_convencoes.txt
"""
import os

import numpy as np

from rev_R3_comum import B, gram, CalculadoraMemoria, SAIDA
from harmonicos import Grade, sYlm

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def e_lig(x, eta, ordem=1):
    """Energia de ligacao (positiva) de orbita circular: (eta x/2)[1 - (3/4 + eta/12) x - (27/8 - 19/8 eta + eta^2/24) x^2]."""
    s = 1 - (0.75 + eta / 12) * x
    if ordem >= 2:
        s = s - (27 / 8 - 19 / 8 * eta + eta ** 2 / 24) * x ** 2
    return 0.5 * eta * x * s


if __name__ == "__main__":
    log("(1) memoria de CM (2,0), nivel A, janela M f0 = 0.004")
    log("    cm20 = nula(janela) - (1/2) M_f J^E_20 [Dfrak(2) = 3]; 'pre' = parte ordinaria que vem do deslocamento antes da janela")
    for q in (1.0, 2.0, 4.0, 8.0):
        t, h = B.gerar(q, 0.0, 0.0)
        mem, aux = B.memorias(q, 0.0, 0.0, t=t, h=h, nivel="A")
        eta, x0, Mf = aux["eta"], aux["x0"], aux["M_f"]
        pre = B.favata_h20(x0, eta)
        J = mem["deslocamento"][(2, 0)].real
        cm = mem["cm"][(2, 0)].real
        nula = cm + 0.5 * Mf * J
        cm_jan = nula - 0.5 * Mf * (J - pre)                   # so o deslocamento da janela
        Mi = 1 - e_lig(x0, eta)
        cm_dif = nula - 0.5 * (Mf * J - Mi * pre)               # M_f Phi_f - M_i Phi_i
        log("  q=%.0f: cm20 (codigo) = %+.5f ; parte nula = %+.5f ; ordinaria pre-janela = %+.5f (%.1f%% de cm20)"
            % (q, cm, nula, -0.5 * Mf * pre, 100 * (-0.5 * Mf * pre) / cm))
        log("        cm20 so com o deslocamento da janela = %+.5f ; com M_f Phi_f - M_i Phi_i = %+.5f" % (cm_jan, cm_dif))
        if q == 1.0:
            n = 200                                             # janela de 50 M
            tt = t[:n]
            hh = {k: v[:n] for k, v in h.items()}
            m2, a2 = B.memorias(q, 0.0, 0.0, t=tt, h=hh, nivel="A")
            log("        janela de %.0f M: desl20 = %.5f, cm20 = %+.5f (esperado ~0 para uma janela curta; -M_f/2 x Favata(x0) = %+.5f)"
                % (tt[-1] - tt[0], m2["deslocamento"][(2, 0)].real, m2["cm"][(2, 0)].real, -0.5 * a2["M_f"] * pre))
        del t, h

    log()
    log("(2) momento_irradiado contra integral direta numa grade (modos sinteticos)")
    rng = np.random.default_rng(3)
    lista = [(2, 2), (2, -2), (3, 2), (3, -2), (2, 1), (2, -1), (3, 3), (3, -3), (2, 0), (3, 0)]
    calc = CalculadoraMemoria(lista)
    nt = 400
    u = np.linspace(0, 40, nt)
    du = u[1] - u[0]
    H = np.stack([(rng.normal() + 1j * rng.normal()) * np.exp(-1j * (0.3 + 0.1 * k) * u) * np.exp(-((u - 20) / 8) ** 2)
                  for k in range(len(lista))], axis=1)
    Hd = B.derivada4(H, du)
    m = calc.memorias_gram(*gram(H, Hd, du))
    P = B.momento_irradiado(m["energia_modos"])
    g = Grade(40, 80)
    Ym = np.array([g.Y(-2, l, mm) for (l, mm) in lista])
    E = np.zeros(g.shape)
    for i in range(nt):
        E += np.abs(np.tensordot(Hd[i], Ym, axes=1)) ** 2 * du
    n_vec = [np.sin(g.theta) * np.cos(g.phi), np.sin(g.theta) * np.sin(g.phi), np.cos(g.theta)]
    Pdir = np.array([g.integrar(nv * E) for nv in n_vec]) / (16 * np.pi)
    log("  P (codigo)  = %s" % np.array2string(P, precision=8))
    log("  P (direto)  = %s ; max|dif|/|P| = %.1e" % (np.array2string(Pdir, precision=8),
                                                       np.max(np.abs(P - Pdir)) / np.linalg.norm(Pdir)))

    log()
    log("(3) M_f: termo 2PN da energia de ligacao em x0 = (pi 0.004)^(2/3) (ausente em binarias.memorias)")
    x0 = (np.pi * 0.004) ** (2 / 3)
    for q in (1.0, 8.0):
        eta = q / (1 + q) ** 2
        log("  q=%.0f: E_lig 1PN = %.6e ; 2PN - 1PN = %+.2e (em M_f)" % (q, e_lig(x0, eta), e_lig(x0, eta, 2) - e_lig(x0, eta)))
    with open(os.path.join(SAIDA, "rev_R3_cm_convencoes.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
