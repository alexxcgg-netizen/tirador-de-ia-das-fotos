"""Experimento 18 (L01, tarefa 2): a direcao quase nula intrinseca das memorias e a degenerescencia q-chi_eff da onda?

Memoria: jacobiano T0 com D e iota fixos (4 x 4 em ln M, q, chi1, chi2), escala relativa, de exp17 (ponto A e grade).
Onda: matriz de Fisher da onda oscilatoria h_+ (IMRPhenomXAS, so (2,2), e IMRPhenomXHM, com modos superiores;
lalsimulation), aLIGO e ET, fmin = 10 Hz, D = 400 Mpc, iota = 50 graus, nos mesmos parametros (ln M, q, chi1, chi2),
com t_c e phi_c projetados (complemento de Schur). Compara:
  - a direcao mais fraca da onda (autovetor de menor autovalor) com a direcao quase nula da memoria;
  - R = v_mem^T G v_mem / lambda_min(G) (= 1 se coincidem; a escala das coordenadas e a mesma nos dois);
  - d chi_eff / d ln eta e d ln Mc / d ln eta ao longo de cada direcao (invariantes de escala).
Saida: resultados/exp18_qchi.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from deteccao import psd_serie                            # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp18_qchi.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def hf(p, aprox, df, fmin, fmax, D=400.0, iota=np.radians(50.0), phi=0.0):
    import lal
    import lalsimulation as ls
    lnM, q, c1, c2 = p
    M = np.exp(lnM)
    m1, m2 = M * q / (1 + q), M / (1 + q)
    hp, hc = ls.SimInspiralChooseFDWaveform(m1 * lal.MSUN_SI, m2 * lal.MSUN_SI, 0.0, 0.0, c1, 0.0, 0.0, c2,
                                            D * 1e6 * lal.PC_SI, iota, phi, 0.0, 0.0, 0.0, df, fmin, fmax, fmin,
                                            None, getattr(ls, aprox))
    return hp.data.data.copy()


def fisher(p0, aprox, psd, fmin=10.0, df=1.0 / 64, fmax=1024.0):
    h0 = hf(p0, aprox, df, fmin, fmax)
    n = len(h0)
    f = np.arange(n) * df
    Sn = psd_serie(psd, n, df, fmin)
    passos = np.array([1e-5, 1e-5, 1e-5, 1e-5])
    der = []
    for k in range(4):
        pp, pm = np.array(p0, float), np.array(p0, float)
        pp[k] += passos[k]
        pm[k] -= passos[k]
        der.append((hf(pp, aprox, df, fmin, fmax)[:n] - hf(pm, aprox, df, fmin, fmax)[:n]) / (2 * passos[k]))
    der.append(-2j * np.pi * f * h0)        # t_c
    e = 1e-5                                # phi_c: fase orbital de referencia (exato tambem com modos superiores)
    der.append((hf(p0, aprox, df, fmin, fmax, phi=e)[:n] - hf(p0, aprox, df, fmin, fmax, phi=-e)[:n]) / (2 * e))
    der = np.array(der)
    ok = np.isfinite(Sn) & (f >= fmin)
    G = 4 * np.real(np.einsum("if,jf,f->ij", der[:, ok], der[:, ok].conj(), 1.0 / Sn[ok])) * df
    snr = np.sqrt(4 * np.sum(np.abs(h0[ok]) ** 2 / Sn[ok]) * df)
    Gaa, Gab, Gbb = G[:4, :4], G[:4, 4:], G[4:, 4:]
    Gp = Gaa - Gab @ np.linalg.solve(Gbb, Gab.T)
    return Gp, snr


def fis(v, q, c1, c2):
    dlnM, dq, dc1, dc2 = v
    eta = q / (1 + q) ** 2
    dln_eta = (1 - q) / (1 + q) ** 3 * dq / eta
    dce = (q * dc1 + dc2) / (1 + q) + (c1 - c2) / (1 + q) ** 2 * dq
    dlnMc = dlnM + 0.6 * dln_eta
    return dlnMc / dln_eta, dce / dln_eta, 0.5 * (dc1 - dc2) / dln_eta


if __name__ == "__main__":
    np.set_printoptions(linewidth=150, precision=4)
    import exp17_analise_jac as J
    casos = [("A", None, 1.2, 0.3, -0.2)]
    for i, p in enumerate(J.PONTOS):
        if p in [(2.0, 0.0, 0.0), (3.0, 0.6, 0.0), (1.2, 0.6, -0.6), (2.0, -0.6, 0.6), (5.0, 0.0, 0.0)]:
            casos.append(("grade", i) + tuple(p))
    log("Direcao quase nula da memoria (T0, D e iota = 50 graus fixos) contra a direcao fraca da onda (Fisher, t_c e phi_c")
    log("projetados), M = 65 M_sol. Vetores em (ln M, q, chi1, chi2) unitarios; razoes d ln Mc, d chi_eff, d chi_a por d ln eta.")
    for nome, i, q, c1, c2 in casos:
        dp = J.carregar_A() if nome == "A" else J.carregar_ponto(i)
        Fr = J.fref(dp, 1)
        r = J.analisar(dp, 1, np.radians(50.0), 0.0, "T0", "intr", "rel", Fr)
        vm = r["Vt"][-1]
        log("")
        log("%s q = %.1f chi = (%+.1f, %+.1f): memoria sigma = %s ; v_mem = %s ; (dlnMc, dchi_eff, dchi_a)/dln eta = %s"
            % (nome, q, c1, c2, np.array2string(r["sv"], precision=3), np.array2string(vm, precision=4),
               np.array2string(np.array(fis(vm, q, c1, c2)), precision=4)))
        p0 = (np.log(65.0), q, c1, c2)
        for aprox in ("IMRPhenomXAS", "IMRPhenomXHM"):
            for psd in ("aLIGO", "ET"):
                Gp, snr = fisher(p0, aprox, psd)
                w, U = np.linalg.eigh(Gp)
                vw = U[:, 0]
                Rr = vm @ Gp @ vm / w[0]
                cosang = abs(vm @ vw)
                sig_w = 1 / np.sqrt(w[0])
                sig_mem_dir = 1 / np.sqrt(vm @ Gp @ vm)
                log("  %-12s %-5s SNR %.1f: v_fraca = %s ; cos(v_mem, v_fraca) = %.3f ; R = %.2e ; (dlnMc, dchi_eff, dchi_a)/dln eta = %s"
                    % (aprox, psd, snr, np.array2string(vw, precision=4), cosang, Rr,
                       np.array2string(np.array(fis(vw, q, c1, c2)), precision=4)))
                log("               1-sigma da onda: ao longo de v_fraca %.2e ; ao longo de v_mem %.2e (unidades de |v| = 1)"
                    % (sig_w, sig_mem_dir))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
