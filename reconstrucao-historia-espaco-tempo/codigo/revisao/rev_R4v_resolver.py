"""Verificador R4v, item 3: os pares q_B = 1.2 e q_B = 1 do exp12 sao aproximados ou so mal convergidos?

Mesmo problema do exp12 (nivel A, SEOBNRv5EHM, l0 = 0): q_B, chi2_B, e0 fixos; D_B sai do deslocamento;
(iota_B, chi1_B, M_B) nas tres equacoes de spin, CM e giroscopica. Em vez do least_squares do exp12, Newton
com jacobiano por diferencas centrais com passos grandes diante do tremor (~1e-5): dchi1 = h_c, dM = h_M; iota
nao exige reavaliar o modelo (so entra nos harmonicos). Busca linear (alfa = 1, 1/2, ..., 1/32). Cada passo
registra os valores singulares do jacobiano escalado (iota 0.01 rad, chi1 0.01, M 0.1 Msol) e a reducao
prevista pela linearizacao. Se o jacobiano for regular e Newton cair ao piso (~1e-5), o par era so mal
convergido; se o jacobiano for quase singular e o residuo travar, o minimo e de fato nao nulo (aproximado).
Uso: python revisao/rev_R4v_resolver.py <e0> <qB> [h_c h_M]
Saida: resultados/revisao/rev_R4v_resolver_e<e0>_q<qB>.txt
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
COD = os.path.dirname(AQUI)
RAIZ = os.path.dirname(COD)
sys.path.insert(0, COD)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E                       # noqa: E402

RES = os.path.join(RAIZ, "resultados", "revisao")
linhas = []
_mem = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def mem(q, c1, c2, M, e0):
    """Memorias (dicionario pequeno) com chave exata; nao guarda a onda."""
    k = (float(q), float(c1), float(c2), float(M), float(e0))
    if k not in _mem:
        f0 = M * Dt.MSUN_S * E.F_FIS
        t, h = E.gerar(q, c1, c2, f0, e0)
        eta = q / (1 + q) ** 2
        _mem[k] = E.memorias_janela(t, h, E.LISTA, E.calc(), eta, (np.pi * f0) ** (2 / 3))[0]
        del t, h
    return _mem[k]


if __name__ == "__main__":
    t0 = time.time()
    eB, qB = float(sys.argv[1]), float(sys.argv[2])
    hc = float(sys.argv[3]) if len(sys.argv) > 3 else 2e-3
    hM = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp12_pares.json")))
    pj = [x for x in DADOS["pares"] if x["e0"] == eB and x["qB"] == qB][0]
    c2B = pj["c2B"]
    alvo = DADOS["alvo"]
    TRES = ("spin", "cm", "giroscopica")

    def obs(x):
        iota, c1, M = x
        m = mem(qB, c1, c2B, M, eB)
        v1 = B.valores_fisicos(m, iota, M, 1.0)
        D = v1["deslocamento"] / alvo["deslocamento"]
        v = B.valores_fisicos(m, iota, M, D)
        return np.array([(v[k] - alvo[k]) / abs(alvo[k]) for k in TRES]), D

    def jac(x):
        J = np.zeros((3, 3))
        passos = (1e-5, hc, hM)
        for j in range(3):
            xp, xm = np.array(x, float), np.array(x, float)
            xp[j] += passos[j]
            xm[j] -= passos[j]
            J[:, j] = (obs(xp)[0] - obs(xm)[0]) / (2 * passos[j])
        return J

    esc = np.array([0.01, 0.01, 0.1])
    x = np.array([pj["iota"], pj["c1"], pj["M"]])
    r, D = obs(x)
    log("caso e0 = %.1f, q_B = %.1f, chi2_B = %+.1f ; passos h_chi1 = %.0e, h_M = %.2f Msol ; partida = solucao do json (residuo json %.2e)"
        % (eB, qB, c2B, hc, hM, pj["residuo"]))
    log("  it 0: max|r| %.3e r [%s] iota %.4f graus chi1 %+.5f M %.4f D %.2f"
        % (np.max(np.abs(r)), " ".join("%+.2e" % z for z in r), np.degrees(x[0]), x[1], x[2], D))
    for it in range(1, 13):
        J = jac(x)
        sv = np.linalg.svd(J * esc, compute_uv=False)
        dx = np.linalg.solve(J, -r)
        ok = False
        for alfa in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
            xn = x + alfa * dx
            if not (-0.8 <= xn[1] <= 0.8):
                continue
            rn, Dn = obs(xn)
            if np.max(np.abs(rn)) < np.max(np.abs(r)):
                ok = True
                break
        log("  it %d: valores singulares (escalados) %s ; passo Newton dx = (%+.2e rad, %+.2e, %+.3e Msol)"
            % (it, " ".join("%.2e" % s for s in sv), dx[0], dx[1], dx[2]))
        if not ok:
            log("        nenhum alfa reduz max|r| (ultimo tentado: max|r| %.3e) -> para" % np.max(np.abs(rn)))
            break
        x, r, D = xn, rn, Dn
        log("        alfa %.3f: max|r| %.3e r [%s] iota %.4f graus chi1 %+.5f M %.4f D %.2f"
            % (alfa, np.max(np.abs(r)), " ".join("%+.2e" % z for z in r), np.degrees(x[0]), x[1], x[2], D))
        if np.max(np.abs(r)) < 1.5e-5:
            log("        chegou ao piso do modelo (< 1.5e-5)")
            break
    log("(%d avaliacoes do modelo, %.0f s)" % (len(_mem), time.time() - t0))
    with open(os.path.join(RES, "rev_R4v_resolver_e%.1f_q%.1f.txt" % (eB, qB)), "w") as f:
        f.write("\n".join(linhas) + "\n")
