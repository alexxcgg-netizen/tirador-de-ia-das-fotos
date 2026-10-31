"""Revisor R3: de onde vem a diferenca entre os niveis A e C (spin (3,0), giro (3,0), desl (2,0)).

Para cada sistema (NRHybSur3dq8_CCE, janela M f0 = 0.004, dt = 0.25):
  1. taxa instantanea do nivel A, hB_30(u) (fluxo dos modos oscilatorios), contra h_30(u) do substituto;
     acumulados S_A(u) = int hB_30, S_C(u) = int h_30 e onde a diferenca se acumula
     (antes da hibridizacao, na janela de hibridizacao [-3500, -2500] M do pico, na RN, depois do pico);
  2. as duas taxas divididas pela ordem PN dominante |h30| = (16/5) sqrt(6 pi/35) nu^2 x^(7/2), em funcao de x;
  3. o mesmo para o deslocamento (2,0): d h_20/du contra a taxa nula, e h_20(u0) contra Favata 3PN em x0;
  4. a giroscopica (3,0) separada em termo de spin e termo de helicidade (amplificacao da diferenca de spin);
  5. decomposicao da memoria de spin (3,0) do nivel A por pares de modos (q = 8 e q = 1).
Saida: resultados/revisao/rev_R3_origem_AC.txt e .json
"""
import json
import os
import time

import numpy as np

from rev_R3_comum import B, gram, Dfrak, ethb2_de_escalar, taxas_instantaneas, x_de_h22, h30_pn_lo, \
    spin_por_pares, SAIDA

SISTEMAS = [(1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (8.0, 0.0, 0.0), (1.0, 0.6, 0.6), (3.0, 0.6, 0.0)]
linhas = []
res = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def analisar(q, c1, c2, f0=0.004, dt=0.25):
    t, h = B.gerar(q, c1, c2, f0=f0, dt=dt)
    eta = q / (1 + q) ** 2
    x0 = (np.pi * f0) ** (2 / 3)
    c_osc, _ = B.calculadoras()
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = B.derivada4(H, dt)
    hB, hEJ, dmem = taxas_instantaneas(c_osc, H, Hd, [(2, 0), (3, 0), (4, 0)])
    norma = np.sum(np.abs(np.stack(list(h.values()), axis=1)) ** 2, axis=1)
    tp = t[np.argmax(norma)]
    h30 = h[(3, 0)]
    h20 = h[(2, 0)]
    SA = np.cumsum(hB[:, 1]) * dt
    SC = np.cumsum(h30) * dt
    # conferencia com binarias.memorias (nivel A e C)
    mA, _ = B.memorias(q, c1, c2, f0=f0, dt=dt, nivel="A", t=t, h=h)
    mC, _ = B.memorias(q, c1, c2, f0=f0, dt=dt, nivel="C", t=t, h=h)
    out = dict(q=q, c1=c1, c2=c2, t0=float(t[0] - tp))
    out["spin_A_bin"] = complex(mA["spin"][(3, 0)])
    out["spin_C_bin"] = complex(mC["spin"][(3, 0)])
    out["SA_fim"] = complex(SA[-1])
    out["SC_fim"] = complex(SC[-1])
    # onde a diferenca se acumula
    cortes = [t[0] - 1, tp - 3500, tp - 2500, tp - 100, tp + 1e9]
    nomes = ["antes de -3500 (PN/EOB)", "[-3500,-2500] (hibridizacao)", "[-2500,-100] (RN)", "depois de -100"]
    dS = hB[:, 1] - h30
    trechos = []
    for a, b, nm in zip(cortes[:-1], cortes[1:], nomes):
        sel = (t > a) & (t <= b)
        trechos.append((nm, float(np.imag(np.sum(dS[sel]) * dt)), float(np.imag(np.sum(h30[sel]) * dt)),
                        float(np.imag(np.sum(hB[sel, 1]) * dt))))
    out["trechos_spin"] = trechos
    # taxas / ordem dominante em funcao de x
    x = x_de_h22(t, h[(2, 2)])
    lo = h30_pn_lo(x, eta)
    tab = []
    for xa in (0.055, 0.06, 0.07, 0.08, 0.10, 0.12, 0.15):
        k = np.argmin(np.abs(x[t < tp - 200] - xa))
        tab.append((xa, float(t[k] - tp), float(np.abs(hB[k, 1]) / lo[k]), float(np.abs(h30[k]) / lo[k]),
                    float(np.angle(hB[k, 1]) / np.pi), float(np.angle(h30[k]) / np.pi)))
    out["razao_LO"] = tab
    # deslocamento: taxa nula contra dh20/du e valor inicial contra Favata
    dh20 = np.gradient(h20, dt)
    D_A = np.sum(dmem[:, 0]) * dt
    D_C = h20[-1] - h20[0]
    out["desl20"] = dict(janela_A=float(D_A.real), janela_C=float(D_C.real), h20_inicio=float(h20[0].real),
                         favata_x0=float(B.favata_h20(x0, eta)), total_A=float(mA["deslocamento"][(2, 0)].real),
                         total_C=float(mC["deslocamento"][(2, 0)].real),
                         h40_inicio=float(h[(4, 0)][0].real), lrr_x0=float(B.lrr_h40(x0, eta)),
                         x_inicio=float(x[5]), x0=float(x0))
    tabd = []
    for xa in (0.055, 0.07, 0.10, 0.15):
        k = np.argmin(np.abs(x[t < tp - 200] - xa))
        # media movel de uma orbita para tirar oscilacoes residuais de dh20/du
        P = 2 * np.pi / x[k] ** 1.5
        sel = np.abs(t - t[k]) < P / 2
        tabd.append((xa, float(np.mean(dmem[sel, 0]).real), float(np.mean(dh20[sel]).real)))
    out["taxa_desl"] = tabd
    trd = []
    for a, b, nm in zip(cortes[:-1], cortes[1:], nomes):
        sel = (t > a) & (t <= b)
        trd.append((nm, float(np.sum(dmem[sel, 0]).real * dt), float(np.sum(dh20[sel]).real * dt)))
    out["trechos_desl"] = trd
    # giroscopica (3,0): termo de spin e de helicidade, nos niveis A e C
    B_, A_ = gram(H, Hd, dt)
    m = c_osc.memorias_gram(B_, A_)
    termo_spin_A = -Dfrak(3) * m["spin_potencial"][(3, 0)]
    termo_spin_A2 = -Dfrak(3) * 2j * m["spin"][(3, 0)] / ethb2_de_escalar(3)     # pela formula do nivel C
    hel = 0.25 * m["helicidade_modos"][(3, 0)]
    out["giro30"] = dict(termo_spin_A=complex(termo_spin_A), termo_spin_A_via_formulaC=complex(termo_spin_A2),
                         helicidade=complex(hel), total_A=complex(mA["giroscopica"][(3, 0)]),
                         total_C=complex(mC["giroscopica"][(3, 0)]))
    if (q, c1, c2) in [(8.0, 0.0, 0.0), (1.0, 0.0, 0.0)]:
        pares = spin_por_pares(c_osc, B_, A_, Losc)
        out["pares"] = sorted(((str(k), float(v.imag)) for k, v in pares.items() if abs(v) > 1e-9 * abs(SA[-1])),
                              key=lambda z: -abs(z[1]))
    return out


if __name__ == "__main__":
    t00 = time.time()
    for (q, c1, c2) in SISTEMAS:
        o = analisar(q, c1, c2)
        res[str((q, c1, c2))] = o
        sA, sC = o["SA_fim"].imag, o["SC_fim"].imag
        log("=== q = %.0f, chi = (%+.1f, %+.1f); inicio da janela em t - t_pico = %.0f M" % (q, c1, c2, o["t0"]))
        log("  spin30 (Im): A = %.6f (binarias: %.6f)  C = %.6f (binarias: %.6f)  (A-C)/C = %+.4f"
            % (sA, o["spin_A_bin"].imag, sC, o["spin_C_bin"].imag, (sA - sC) / sC))
        log("  onde (A - C) se acumula [trecho: Im int(hB - h30), Im int h30 (C), Im int hB (A)]:")
        for nm, d, c, a in o["trechos_spin"]:
            log("     %-30s  dif = %+.5f (%5.1f%% da dif. total)   C = %.5f   A = %.5f" % (nm, d, 100 * d / (sA - sC), c, a))
        log("  taxas / ordem PN dominante: x, t-t_pico, |hB_A|/LO, |h30_C|/LO, fase hB/pi, fase h30/pi")
        for r in o["razao_LO"]:
            log("     x = %.3f  t = %8.0f  A/LO = %.4f  C/LO = %.4f  fases %+.3f %+.3f" % r)
        d = o["desl20"]
        log("  desl20: total A = %.5f, total C = %.5f, (A-C)/C = %+.4f" % (d["total_A"], d["total_C"],
                                                                         (d["total_A"] - d["total_C"]) / d["total_C"]))
        log("     antes da janela: Favata 3PN(x0) = %.6f ; h20(u0) do substituto = %.6f ; dif./C total = %+.4f"
            % (d["favata_x0"], d["h20_inicio"], (d["favata_x0"] - d["h20_inicio"]) / d["total_C"]))
        log("     na janela: fluxo (A) = %.6f ; h20(fim)-h20(u0) (C) = %.6f ; dif./C total = %+.4f"
            % (d["janela_A"], d["janela_C"], (d["janela_A"] - d["janela_C"]) / d["total_C"]))
        log("     x medido no inicio = %.5f (x0 nominal %.5f); h40(u0) = %.3e, LRR 1PN(x0) = %.3e"
            % (d["x_inicio"], d["x0"], d["h40_inicio"], d["lrr_x0"]))
        for nm, a, c in o["trechos_desl"]:
            log("     %-30s  fluxo A = %.6f   dh20 C = %.6f   (A-C) = %+.2e" % (nm, a, c, a - c))
        log("     taxa media numa orbita (x, A, C): " + "; ".join("%.3f: %.3e / %.3e (%.4f)" % (xa, a, c, a / c)
                                                                 for xa, a, c in o["taxa_desl"]))
        g = o["giro30"]
        log("  giro30: termo de spin (A) = %.5f [pela formula do nivel C: %.5f], helicidade = %.5f, total A = %.5f, C = %.5f"
            % (g["termo_spin_A"].real, g["termo_spin_A_via_formulaC"].real, g["helicidade"].real,
               g["total_A"].real, g["total_C"].real))
        rs = (sA - sC) / sC
        prev = rs * g["termo_spin_A"].real / g["total_A"].real
        log("     (giroA-giroC)/giroC = %+.4f ; previsto so pela dif. de spin: (dS/S)*(termo spin/total) ~ %+.4f"
            % ((g["total_A"].real - g["total_C"].real) / g["total_C"].real, prev))
        if "pares" in o:
            log("  spin30 (nivel A) por pares de modos (Im), fracao do total:")
            for k, v in o["pares"][:14]:
                log("     %-22s %+.6f  (%+.4f)" % (k, v, v / sA))
        log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3_origem_AC.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(SAIDA, "rev_R3_origem_AC.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda z: [z.real, z.imag] if isinstance(z, complex) else float(z))
