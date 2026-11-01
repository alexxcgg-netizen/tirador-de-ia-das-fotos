"""Experimento 32b (linha L09, agente D5, checagem curta): taxa da memoria depois do pico e pares de QNMs.

Elhashash & Nichols (arXiv:2504.18635, modelo de ringdown da memoria, eq. (44) na versao HTML v2) escrevem a memoria
(2,0) no ringdown como soma sobre pares de QNMs do mesmo m, com fatores exp[-i(omega_n - conj(omega_n'))(t - t0)]:
a taxa decai como exp(-2 t/tau_220) no fim e os pares (n, n') dao frequencias-diferenca Re(omega_n - omega_n') com
amortecimento 1/tau_n + 1/tau_n'. Aqui:
 1. remanescente (NRSur3dq8Remnant) e QNMs (pacote qnm), em unidades da massa total M;
 2. taxa da memoria nula R_2(t) = d h20^mem/du (nivel A) depois do pico: (i) so (2,+-2), (ii) todos os modos;
    (iii) RN: d Re h20/du do substituto;
 3. inclinacao de log R_2 em janelas [t1, t1 + 25] contra 2/tau_220;
 4. matrix pencil (Hua & Sarkar 1990) de R_2 em [t1, 60] M: polos contra os pares previstos;
 5. residuo h20(RN) - h20(nula) depois do pico (o "toque" dos modos m = 0): polos contra omega_200, omega_201.
Sistemas: A, q = 1 sem spin, q = 4 sem spin. Saida: resultados/exp32_ringdown.txt, .json
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np                                        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp30_comum as C                                   # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def pencil(y, dt, ordem):
    """Matrix pencil: polos s_k (y ~ sum c_k exp(s_k t)) e amplitudes."""
    N = len(y)
    L = N // 3
    Y = np.array([y[i:i + L + 1] for i in range(N - L)])
    _, sv, Vh = np.linalg.svd(Y, full_matrices=False)
    V = Vh.conj().T[:, :ordem]
    z = np.linalg.eigvals(np.linalg.pinv(V[:-1]) @ V[1:])
    s = np.log(z) / dt
    tt = np.arange(N) * dt
    Z = np.exp(np.outer(tt, s))
    c = np.linalg.lstsq(Z, y, rcond=None)[0]
    rel = np.linalg.norm(Z @ c - y) / np.linalg.norm(y)
    return s, c, sv[:ordem + 3] / sv[0], rel


import qnm                                                # noqa: E402
import surfinBH                                           # noqa: E402
fit = surfinBH.LoadFits("NRSur3dq8Remnant")
res = {}
SIST = [("A", (1.2, 0.3, -0.2)), ("q=1", (1.0, 0.0, 0.0)), ("q=4", (4.0, 0.0, 0.0))]
for nome, (q, c1, c2) in SIST:
    mf, chif, _, _, _, _ = fit.all(q, [0, 0, c1], [0, 0, c2])
    af = float(chif[2])
    W = {}
    for (l, m, n) in ((2, 2, 0), (2, 2, 1), (2, 2, 2), (3, 2, 0), (2, 0, 0), (2, 0, 1), (2, -2, 0)):
        w, _, _ = qnm.modes_cache(s=-2, l=l, m=m, n=n)(a=af)
        W[(l, m, n)] = complex(w) / float(mf)           # em 1/M (M total inicial)
    g0, g1 = -W[(2, 2, 0)].imag, -W[(2, 2, 1)].imag
    log("== %s: M_f = %.5f, chi_f = %.5f ; omega (1/M): 220 %.4f%+.4fi, 221 %.4f%+.4fi, 320 %.4f%+.4fi, 200 %.4f%+.4fi,"
        " 201 %.4f%+.4fi, 2-20 %.4f%+.4fi" % (nome, mf, af, *sum(([W[k].real, W[k].imag] for k in
                                                                   ((2, 2, 0), (2, 2, 1), (3, 2, 0), (2, 0, 0), (2, 0, 1), (2, -2, 0))), [])))
    pares = {"220x220": complex(0, -2 * g0), "220x221": W[(2, 2, 0)] - np.conj(W[(2, 2, 1)]),
             "221x221": complex(0, -2 * g1), "220x320": W[(3, 2, 0)] - np.conj(W[(2, 2, 0)]),
             "220x(2-20 espelho)": W[(2, 2, 0)] + W[(2, -2, 0)]}
    log("   pares previstos (Re = frequencia-diferenca, -Im = amortecimento): " + " ; ".join(
        "%s %.4f/%.4f" % (k, v.real, -v.imag) for k, v in pares.items()))
    Qb = abs(pares["220x221"].real) / (g0 + g1)
    log("   batimento 220-221: Delta omega/(Gamma_0+Gamma_1) = %.3f (fase do batimento por e-dobra do termo cruzado)" % Qb)
    t, hh, ti = C.gerar(q, c1, c2, f0=0.006)
    sel = (t >= -200) & (t <= 130)
    t = t[sel]
    h = {k: v[sel] for k, v in hh.items()}
    del hh
    dt = t[1] - t[0]
    tpk = t[np.argmax(np.abs(h[(2, 2)]))]
    _, _, R22, _ = C.fluxos_memoria(t, h, so22=True)
    _, _, Rall, _ = C.fluxos_memoria(t, h)
    Rrn = C.D(h[(2, 0)].real, dt)
    out = dict(M_f=float(mf), chi_f=af, omega={str(k): [v.real, v.imag] for k, v in W.items()},
               pares={k: [v.real, v.imag] for k, v in pares.items()}, Q_batimento=Qb)
    # 3. inclinacao local
    for rot, R in (("so (2,2)", R22[:, 0].real), ("todos os modos", Rall[:, 0].real), ("RN d h20/du", Rrn)):
        partes = []
        for t1 in (5.0, 10.0, 15.0, 20.0, 30.0, 40.0):
            m = (t - tpk >= t1) & (t - tpk <= t1 + 25) & (R > 0)
            if np.sum(m) < 20 or np.any(R[(t - tpk >= t1) & (t - tpk <= t1 + 25)] <= 0):
                partes.append("[%g,%g] R<=0" % (t1, t1 + 25))
                continue
            sl = np.polyfit(t[m] - tpk, np.log(R[m]), 1)[0]
            partes.append("[%g,%g]: %.4f (%+.1f%%)" % (t1, t1 + 25, -sl, 100 * (-sl / (2 * g0) - 1)))
            out["incl %s %g" % (rot, t1)] = float(-sl)
        log("   decaimento de %-15s -dlnR/dt contra 2 Gamma_220 = %.4f: " % (rot, 2 * g0) + " ; ".join(partes))
    # 4. matrix pencil da taxa
    for rot, R in (("so (2,2)", R22[:, 0].real), ("todos os modos", Rall[:, 0].real)):
        for t1, ordem in ((10.0, 3), (10.0, 5), (20.0, 3)):
            m = (t - tpk >= t1) & (t - tpk <= 60.0)
            s, c, sv, rel = pencil(R[m], dt, ordem)
            om = 1j * s                                      # y ~ exp(-i omega t)
            ordem_idx = np.argsort(-np.abs(c))
            log("   pencil %-15s [%g,60] ordem %d (residuo %.1e; sv/sv0 %s): " % (rot, t1, ordem, rel,
                                                                            " ".join("%.0e" % x for x in sv[:ordem + 1]))
                + " ; ".join("%.4f/%.4f (|c| %.1e)" % (om[k].real, -om[k].imag, abs(c[k])) for k in ordem_idx))
            out["pencil %s %g %d" % (rot, t1, ordem)] = [[float(om[k].real), float(-om[k].imag), float(abs(c[k]))]
                                                         for k in ordem_idx]
    # 5. toque dos modos m = 0: residuo RN - nula
    k0 = int(np.argmin(np.abs(t - (tpk - 150))))
    nula = np.concatenate([[0.0], np.cumsum(0.5 * dt * (Rall[k0:-1, 0].real + Rall[k0 + 1:, 0].real))])
    resid = h[(2, 0)].real[k0:] - h[(2, 0)].real[k0] - nula
    tr = t[k0:] - tpk
    degrau = float(nula[-1])
    log("   h20(RN) - h20(nula) desde t_p-150: no pico %.2e, maximo %.2e em t-t_p = %.1f, no fim %.2e (degrau nulo nesse trecho %.2e)"
        % (resid[np.argmin(np.abs(tr))], np.max(np.abs(resid)), tr[np.argmax(np.abs(resid))], resid[-1], degrau))
    for t1 in (5.0, 10.0):
        m = (tr >= t1) & (tr <= 70)
        y = resid[m] - resid[m][-1]
        s, c, sv, rel = pencil(C.D(resid, dt)[m], dt, 4)
        om = 1j * s
        oi = np.argsort(-np.abs(c))
        log("   pencil d(RN - nula)/dt [%g,70] ordem 4 (residuo %.1e): " % (t1, rel)
            + " ; ".join("%.4f/%.4f (|c| %.1e)" % (om[k].real, -om[k].imag, abs(c[k])) for k in oi)
            + "  [previsto 200: %.4f/%.4f ; 201: %.4f/%.4f]" % (W[(2, 0, 0)].real, -W[(2, 0, 0)].imag, W[(2, 0, 1)].real,
                                                                -W[(2, 0, 1)].imag))
        out["pencil_rn %g" % t1] = [[float(om[k].real), float(-om[k].imag), float(abs(c[k]))] for k in oi]
    res[nome] = out
    del h
    log("")
with open(os.path.join(C.RES, "exp32_ringdown.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(C.RES, "exp32_ringdown.json"), "w") as f:
    json.dump(res, f, indent=1)
