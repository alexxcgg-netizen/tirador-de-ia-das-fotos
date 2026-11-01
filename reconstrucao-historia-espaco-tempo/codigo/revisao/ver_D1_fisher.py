"""Verificacao adversarial D1 (H1.7): a direcao quase nula da memoria e a degenerescencia q-chi_eff da onda?

O exp18_qchi compara a direcao quase nula da memoria com o autovetor de MENOR autovalor da Fisher 4x4 da onda em
(ln M, q, chi1, chi2) e conclui 'sinal oposto de dchi_eff/dln eta'. Objecao: esse autovetor e dominado pela
diferenca de spins chi_a (dchi_a/dln eta ~ -44 a -55 no proprio exp18_qchi.txt), e a degenerescencia q-chi_eff
da literatura e uma afirmacao no plano (eta, chi_eff) com chi_a e M marginalizados (ou fixos). Aqui:
  (a) Fisher propria (lalsimulation, passos 1e-4 e 1e-5, df = 1/32 e 1/64) em (ln M, q, chi1, chi2, t_c, phi_c);
  (b) mudanca para y = (ln M, ln eta, chi_eff, chi_a);
  (c) covariancia marginal 2x2 em (ln eta, chi_eff) [M, chi_a, t_c, phi_c marginalizados]: eixo maior,
      inclinacao dchi_eff/dln eta e coeficiente de correlacao;
  (d) Fisher condicional com chi_a fixo (3x3 em ln M, ln eta, chi_eff): direcao mais fraca;
  (e) a direcao quase nula da memoria em A (exp18_qchi.txt: v_mem = (-0.0256, -0.9832, -0.1428, 0.1108)) nas
      mesmas coordenadas, e o 1-sigma da onda ao longo dela.
Saida: resultados/ver_D1_fisher.txt
"""
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
from deteccao import psd_serie                    # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_fisher.txt")


def hf(p, aprox, df, fmin, fmax, phi=0.0, D=400.0, iota=np.radians(50.0)):
    import lal
    import lalsimulation as ls
    lnM, q, c1, c2 = p
    M = np.exp(lnM)
    m1, m2 = M * q / (1 + q), M / (1 + q)
    hp, hc = ls.SimInspiralChooseFDWaveform(m1 * lal.MSUN_SI, m2 * lal.MSUN_SI, 0.0, 0.0, c1, 0.0, 0.0, c2,
                                            D * 1e6 * lal.PC_SI, iota, phi, 0.0, 0.0, 0.0, df, fmin, fmax, fmin,
                                            None, getattr(ls, aprox))
    return hp.data.data.copy()


def fisher6(p0, aprox, psd, passo, df, fmin=10.0, fmax=1024.0):
    h0 = hf(p0, aprox, df, fmin, fmax)
    n = len(h0)
    f = np.arange(n) * df
    Sn = psd_serie(psd, n, df, fmin)
    der = []
    for k in range(4):
        pp, pm = np.array(p0, float), np.array(p0, float)
        pp[k] += passo
        pm[k] -= passo
        der.append((hf(pp, aprox, df, fmin, fmax)[:n] - hf(pm, aprox, df, fmin, fmax)[:n]) / (2 * passo))
    der.append(2j * np.pi * f * h0)
    e = 1e-4
    der.append((hf(p0, aprox, df, fmin, fmax, phi=e)[:n] - hf(p0, aprox, df, fmin, fmax, phi=-e)[:n]) / (2 * e))
    der = np.array(der)
    ok = np.isfinite(Sn) & (f >= fmin) & (Sn > 0)
    G = 4 * np.real(np.einsum("if,jf,f->ij", der[:, ok], der[:, ok].conj(), 1.0 / Sn[ok])) * df
    snr = np.sqrt(4 * np.sum(np.abs(h0[ok]) ** 2 / Sn[ok]) * df)
    return G, snr


def jac_y(q, c1, c2):
    """dy/dx, x = (ln M, q, chi1, chi2), y = (ln M, ln eta, chi_eff, chi_a)."""
    J = np.zeros((4, 4))
    J[0, 0] = 1
    J[1, 1] = 1 / q - 2 / (1 + q)
    J[2, 1] = (c1 - c2) / (1 + q) ** 2
    J[2, 2] = q / (1 + q)
    J[2, 3] = 1 / (1 + q)
    J[3, 2], J[3, 3] = 0.5, -0.5
    return J


if __name__ == "__main__":
    L = []

    def log(s=""):
        print(s, flush=True)
        L.append(s)

    q, c1, c2 = 1.2, 0.3, -0.2
    p0 = (np.log(65.0), q, c1, c2)
    Jy = jac_y(q, c1, c2)
    vmem = np.array([-0.0256, -0.9832, -0.1428, 0.1108])
    ym = Jy @ vmem
    log("Ponto A (M = 65, q = 1.2, chi = (0.3, -0.2), D = 400 Mpc, iota = 50 graus), fmin = 10 Hz.")
    log("Direcao quase nula da memoria (exp18_qchi.txt) em y = (lnM, ln eta, chi_eff, chi_a): %s ; dchi_eff/dln eta = %.3f ;"
        " dchi_a/dln eta = %.3f" % (np.array2string(ym, precision=4), ym[2] / ym[1], ym[3] / ym[1]))
    for aprox in ("IMRPhenomXAS", "IMRPhenomXHM"):
        for psd in ("aLIGO", "ET"):
            for passo, df in ((1e-4, 1 / 32), (1e-5, 1 / 64)):
                G6, snr = fisher6(p0, aprox, psd, passo, df)
                Gaa, Gab, Gbb = G6[:4, :4], G6[:4, 4:], G6[4:, 4:]
                Gx = Gaa - Gab @ np.linalg.solve(Gbb, Gab.T)          # t_c, phi_c projetados
                Jinv = np.linalg.inv(Jy)
                Gy = Jinv.T @ Gx @ Jinv
                Cy = np.linalg.inv(Gy)
                C2 = Cy[np.ix_([1, 2], [1, 2])]
                w, U = np.linalg.eigh(C2)
                eixo = U[:, -1]
                rho = C2[0, 1] / np.sqrt(C2[0, 0] * C2[1, 1])
                # condicional chi_a fixo
                G3 = Gy[:3, :3]
                w3, U3 = np.linalg.eigh(G3)
                v3 = U3[:, 0]
                # 4x4: menor autovalor em x (como exp18) e sua leitura em y
                w4, U4 = np.linalg.eigh(Gx)
                y4 = Jy @ U4[:, 0]
                sig_vmem = 1 / np.sqrt(vmem @ Gx @ vmem)
                log("")
                log("%s %s passo %.0e df 1/%d: SNR %.1f" % (aprox, psd, passo, int(round(1 / df)), snr))
                log("  (exp18) autovetor fraco 4x4 em y: %s ; dchi_eff/dln eta = %+.3f ; dchi_a/dln eta = %+.2f"
                    % (np.array2string(y4, precision=4), y4[2] / y4[1], y4[3] / y4[1]))
                log("  marginal (ln eta, chi_eff): sigma = (%.3e, %.3e), correlacao %+.4f, eixo maior dchi_eff/dln eta = %+.3f"
                    % (np.sqrt(C2[0, 0]), np.sqrt(C2[1, 1]), rho, eixo[1] / eixo[0]))
                log("  condicional chi_a fixo (lnM, ln eta, chi_eff): direcao fraca %s ; dchi_eff/dln eta = %+.3f ;"
                    " dlnM/dln eta = %+.3f" % (np.array2string(v3, precision=4), v3[2] / v3[1], v3[0] / v3[1]))
                log("  1-sigma da onda ao longo de v_mem: %.2e (|v| = 1 em x) ; ao longo do autovetor fraco 4x4: %.2e"
                    % (sig_vmem, 1 / np.sqrt(w4[0])))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
