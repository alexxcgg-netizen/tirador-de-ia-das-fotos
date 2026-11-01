"""Experimento 28 (L12): folga da desigualdade memoria-energia e do limite pela lei da area em binarias reais.

Desigualdades (D = distancia, unidades G = c = M = 1, h = r(h_+ - i h_x)/M):
  (I)   |D Delta h_nula(N)| <= c_L E_rad                          (exp28_constantes: c_2 = sqrt(30)/6, c_inf = 4)
  (Ia)  versao com a divisao de energia: E_2 = energia em l = 2, E_r = resto (l = 3..5):
        |D Delta h| <= E_rad * c(e2),  c(e2) = min_mu [16 pi lambda_max(H - mu P_2) + mu e2 16 pi]  (S-lema, exato)
  (II)  lei da area (Hawking 1971): M_f >= M_irr,f >= sqrt(M_irr1^2 + M_irr2^2) = M_irr0,
        M_irr,i^2 = m_i^2 (1 + sqrt(1 - chi_i^2))/2. Na janela [t_i, fim]: E_janela <= 1 - E_lig(x_i) - M_irr0.
  (IIb) com o spin final chi_f (medido no ringdown, ou ajuste NRSur3dq8Remnant): M_f = M_irr,f sqrt(2/(1+sqrt(1-chi_f^2)))
        >= M_irr0 sqrt(2/(1+sqrt(1-chi_f^2))).
  Limite da memoria nula: |D Delta h| <= c E_max.
Memorias: observaveis.memorias_observaveis, nivel A (nula, fluxo dos modos oscilatorios), desl='janela' e 'total',
todos_m=True; nivel C (RN: modos m = 0 do substituto) para comparacao. Sistemas com M = 65 Msun, janela desde 10 Hz.
Saida: resultados/exp28_folga.txt, resultados/exp28_folga.json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import observaveis as O                               # noqa: E402
import binarias as B                                  # noqa: E402
from harmonicos import Grade, sYlm, modos              # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


# ------------------------------------------------------------------ c(e2) para modos l <= 5
def matriz_H(lista):
    g = Grade(2 * 5 + 12, 4 * 5 + 16)
    K = (1 + np.cos(g.theta)) / 2 * np.exp(-2j * g.phi)
    Y = np.array([g.Y(-2, l, m).ravel() for (l, m) in lista])
    Gam = (Y * (g.peso * K).ravel()) @ Y.conj().T / (4 * np.pi)
    X = Gam.T
    return 0.5 * (X + X.conj().T)


LISTA5 = modos(5, 2)
H5 = matriz_H(LISTA5)
P2 = np.diag([1.0 if l == 2 else 0.0 for (l, m) in LISTA5])


def c_e2(e2):
    """sup |D Dh|/E sobre radiacao l <= 5 com fracao e2 da energia em l = 2 (dual exato de Lagrange, S-lema)."""
    from scipy.optimize import minimize_scalar
    f = lambda mu: 16 * np.pi * (np.linalg.eigvalsh(H5 - mu * P2)[-1] + mu * e2)    # noqa: E731
    r = minimize_scalar(f, bounds=(-20.0, 20.0), method="bounded", options=dict(xatol=1e-12))
    # conferencia primal: autovetor do mu otimo deve ter fracao e2 em l = 2 (gap de dualidade zero)
    ev, V = np.linalg.eigh(H5 - r.x * P2)
    v = V[:, -1]
    frac = float(np.real(v.conj() @ P2 @ v))
    primal = 16 * np.pi * float(np.real(v.conj() @ H5 @ v))
    if e2 < 0.9999 and (abs(frac - e2) > 1e-5 or abs(primal - r.fun) > 1e-6):
        print("aviso dual: frac %.6f e2 %.6f primal %.8f dual %.8f" % (frac, e2, primal, r.fun))
    return float(r.fun)


C2 = np.sqrt(30) / 6
C5 = 16 * np.pi * np.linalg.eigvalsh(H5)[-1]
log("c_2 = %.10f, c_5 = %.10f, c_inf = 4; c(e2): e2=1 -> %.6f, 0.99 -> %.6f, 0.95 -> %.6f, 0.9 -> %.6f" % (
    C2, C5, c_e2(1.0), c_e2(0.99), c_e2(0.95), c_e2(0.9)))


def m_irr(m, chi):
    return m * np.sqrt((1 + np.sqrt(1 - chi * chi)) / 2)


def complexo_obs(mem, iota, phi):
    return sum(c * complex(sYlm(-2, l, mm, iota, phi)) for (l, mm), c in mem["deslocamento"].items())


SISTEMAS = [(1.0, 0.0, 0.0), (1.2, 0.3, -0.2), (2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (8.0, 0.0, 0.0),
            (1.0, 0.8, 0.8), (1.0, -0.8, -0.8), (3.0, 0.6, -0.4), (6.0, 0.8, 0.0)]
IOTAS = (0, 30, 50, 70, 90)
PHIS = np.linspace(0, 2 * np.pi, 48, endpoint=False)
M_MSUN, F_INI = 65.0, 10.0

import surfinBH                                      # noqa: E402
fit = surfinBH.LoadFits("NRSur3dq8Remnant")
saida = []
log()
log("Sistemas: M = %.0f Msun, janela desde %.0f Hz (NRHybSur3dq8_CCE). Razoes r = |D Dh_nula|/E (max em phi)." % (M_MSUN, F_INI))
for (q, c1, c2) in SISTEMAS:
    t, h, ti = O.gerar_janela(q, c1, c2, M_MSUN, F_INI)
    memA, aux = O.memorias_observaveis(q, c1, c2, M_MSUN, F_INI, t=t, h=h, t_i=ti, todos_m=True, desl="janela")
    memT, auxT = O.memorias_observaveis(q, c1, c2, M_MSUN, F_INI, t=t, h=h, t_i=ti, todos_m=True, desl="total")
    memC, _ = O.memorias_observaveis(q, c1, c2, M_MSUN, F_INI, t=t, h=h, t_i=ti, todos_m=True, nivel="C")
    # energia por l, a partir da matriz de Gram da janela
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = O.derivada(H, t[1] - t[0])
    w = O.pesos_janela(t, ti)
    Bm, _ = O.gram_pesos(H, Hd, w)
    del H, Hd, t, h
    El = {}
    for k, (l, m) in enumerate(Losc):
        El[l] = El.get(l, 0.0) + float(np.real(Bm[k, k])) / (16 * np.pi)
    E_win = aux["E_janela"]
    e2 = El[2] / sum(El.values())
    ce2 = c_e2(e2)
    m1, m2 = q / (1 + q), 1 / (1 + q)
    Mirr0 = np.sqrt(m_irr(m1, c1) ** 2 + m_irr(m2, c2) ** 2)
    mf_fit, chif, _, dmf, dchif, _ = fit.all(q, [0, 0, c1], [0, 0, c2])
    chif = float(chif[2])
    fac_chi = np.sqrt(2 / (1 + np.sqrt(1 - chif ** 2)))
    E_area = 1 - aux["E_lig"] - Mirr0
    E_area_chi = 1 - aux["E_lig"] - Mirr0 * fac_chi
    E_tot = 1 - aux["M_f"]
    reg = dict(q=q, chi1=c1, chi2=c2, E_janela=E_win, E_lig=aux["E_lig"], M_f=aux["M_f"], M_f_fit=float(mf_fit),
               chi_f=chif, M_irr0=float(Mirr0), E_area=float(E_area), E_area_chi=float(E_area_chi),
               E_tot=E_tot, E_tot_area=float(1 - Mirr0), E_tot_area_chi=float(1 - Mirr0 * fac_chi),
               E_por_l={int(k): v for k, v in El.items()}, e2=e2, c_e2=ce2, iotas={})
    log()
    log("q=%.1f chi=(%+.1f,%+.1f): E_janela=%.6f (l=2: %.4f; l=3: %.2e; l=4: %.2e; l=5: %.2e) E_lig(10Hz)=%.6f" % (
        q, c1, c2, E_win, e2, El[3] / E_win, El[4] / E_win, El[5] / E_win, aux["E_lig"]))
    log("   M_f=%.6f (ajuste %.6f), chi_f=%.4f, M_irr0=%.6f; E_area(janela)=%.5f, com chi_f %.5f; E_win/E_area=%.4f (%.4f com chi_f)" % (
        aux["M_f"], mf_fit, chif, Mirr0, E_area, E_area_chi, E_win / E_area, E_win / E_area_chi))
    log("   c(e2)=%.5f (c_2=%.5f, c_5=%.5f)" % (ce2, C2, C5))
    log("   iota | r_nula=|DDh|/E_win | r/c(e2) | r/4 | |DDh|/(c(e2) E_area_chi) | |DDh|/(4 E_area) | Im/Re | r_RN(C)/r_A | total: |DDh_tot|/E_tot, /(c E_tot_area_chi)")
    for ideg in IOTAS:
        io = np.radians(ideg)
        zA = np.array([complexo_obs(memA, io, p) for p in PHIS])
        zC = np.array([complexo_obs(memC, io, p) for p in PHIS])
        zT = np.array([complexo_obs(memT, io, p) for p in PHIS])
        k = int(np.argmax(np.abs(zA)))
        r = abs(zA[k]) / E_win
        rT = np.max(np.abs(zT)) / E_tot
        d = dict(r=r, r_sobre_ce2=r / ce2, r_sobre_4=r / 4, limite_area_chi=abs(zA[k]) / (ce2 * E_area_chi),
                 limite_area_4=abs(zA[k]) / (4 * E_area), im_re=float(abs(zA[k].imag) / max(abs(zA[k].real), 1e-300)),
                 rC_rA=float(np.max(np.abs(zC)) / np.max(np.abs(zA))), r_tot=rT,
                 tot_area_chi=float(np.max(np.abs(zT)) / (ce2 * reg["E_tot_area_chi"])),
                 lo_17_24=(np.sin(io) ** 2 * (17 + np.cos(io) ** 2) / 24))
        reg["iotas"][ideg] = d
        log("   %4d | %.5f (LO quadrupolo %.5f) | %.4f | %.4f | %.4f | %.4f | %.1e | %.4f | %.5f, %.4f" % (
            ideg, r, d["lo_17_24"], d["r_sobre_ce2"], d["r_sobre_4"], d["limite_area_chi"], d["limite_area_4"],
            d["im_re"], d["rC_rA"], rT, d["tot_area_chi"]))
    saida.append(reg)

with open(os.path.join(RES, "exp28_folga.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "exp28_folga.json"), "w") as f:
    json.dump(dict(c2=C2, c5=C5, sistemas=saida), f, indent=1)
