"""Experimento 17 (L01, tarefa 2 iv): fibra de A com contraparte eletromagnetica (iota e D conhecidos), conjunto T.

Com todos os m, o azimute phi'_B (fase orbital no pico, vista do observador) continua desconhecido mesmo com iota e D
fixados pela contraparte: 4 equacoes (desl, spin, CM, giro) e 5 incognitas (ln M, q, chi1, chi2, phi'_B) -> fibra de
dimensao 1. Aqui a curva e seguida por continuacao em phi'_B (passos de pi/16, nos dois sentidos a partir de A,
phi'_A = 0), resolvendo (ln M, q, chi1, chi2) exatamente (Newton com jacobiano por diferencas centrais: ln M 1e-4 com tres
janelas da mesma onda; q, chi 1e-4). Para quando q < 1, |chi| > 0.8 ou o residuo nao cai abaixo de 1e-8.
Contraste: T0 com iota e D conhecidos (4 x 4) tem solucao isolada; a mesma continuacao nao se aplica.
Saidas: resultados/exp17_fibra_iD.txt, resultados/exp17_fibra_iD.json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402

A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_fibra_iD")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def F(q, c1, c2, M, phi):
    r = C.memorias_varias(q, c1, c2, [M])[0]
    return C.vetor_fisico(r["mem_pico"], A["iota"], phi, M, A["D"])


def residuo(x, phi, alvo):
    lnM, q, c1, c2 = x
    return F(q, c1, c2, np.exp(lnM), phi) / alvo - 1


def jac(x, phi, alvo):
    lnM, q, c1, c2 = x
    h = 1e-4
    rr = C.memorias_varias(q, c1, c2, [np.exp(lnM - h), np.exp(lnM), np.exp(lnM + h)])
    v = [C.vetor_fisico(r["mem_pico"], A["iota"], phi, np.exp(lnM + s * h), A["D"]) / alvo - 1 for r, s in zip(rr, (-1, 0, 1))]
    cols = [(v[2] - v[0]) / (2 * h)]
    for k in (1, 2, 3):
        xp, xm = np.array(x, float), np.array(x, float)
        xp[k] += h
        xm[k] -= h
        cols.append((residuo(xp, phi, alvo) - residuo(xm, phi, alvo)) / (2 * h))
    return np.array(cols).T, v[1]


def newton(x0, phi, alvo, it=8):
    x = np.array(x0, float)
    for _ in range(it):
        Jm, r = jac(x, phi, alvo)
        if np.max(np.abs(r)) < 1e-10:
            break
        dx = np.linalg.solve(Jm, -r)
        lam = 1.0
        while lam > 1e-3:
            xn = x + lam * dx
            if xn[1] >= 1.0 and abs(xn[2]) <= 0.8 and abs(xn[3]) <= 0.8:
                rn = residuo(xn, phi, alvo)
                if np.max(np.abs(rn)) < np.max(np.abs(r)):
                    break
            lam /= 2
        x = xn
    r = residuo(x, phi, alvo)
    Jm, _ = jac(x, phi, alvo)
    return x, float(np.max(np.abs(r))), np.linalg.svd(Jm / 1.0, compute_uv=False)


if __name__ == "__main__":
    t0 = time.time()
    alvo = F(A["q"], A["c1"], A["c2"], A["M"], 0.0)
    log("A (T, phi'_A = 0, iota = 50 graus e D = 400 Mpc conhecidos): alvo %s" % alvo)
    log("Continuacao da fibra 1D em phi'_B: colunas phi'_B, M, q, chi1, chi2, chi_eff, residuo max, sigma(J 4x4)")
    curva = []
    x0 = np.array([np.log(A["M"]), A["q"], A["c1"], A["c2"]])
    for sentido in (+1, -1):
        x = x0.copy()
        xant = None
        for k in range(1, 33):
            phi = sentido * k * np.pi / 16
            xg = x if xant is None else x + (x - xant)            # predicao linear
            if xg[1] < 1.0 or abs(xg[2]) > 0.8 or abs(xg[3]) > 0.8:
                xg = x
            xs, res, sv = newton(xg, phi, alvo)
            if res > 1e-8 or xs[1] < 1.0 or abs(xs[2]) > 0.8 or abs(xs[3]) > 0.8:
                log("  phi'_B = %+.4f: parou (residuo %.1e, q %.4f, chi1 %+.4f, chi2 %+.4f)" % (phi, res, xs[1], xs[2], xs[3]))
                break
            xant, x = x, xs
            M, q, c1, c2 = np.exp(xs[0]), xs[1], xs[2], xs[3]
            ce = (q * c1 + c2) / (1 + q)
            curva.append(dict(phi=phi, M=M, q=q, c1=c1, c2=c2, chi_eff=ce, res=res, sv=sv.tolist()))
            log("  %+.4f  M %.3f  q %.4f  chi1 %+.4f  chi2 %+.4f  chi_eff %+.4f  res %.1e  sv %s"
                % (phi, M, q, c1, c2, ce, res, np.array2string(sv, precision=3)))
            if abs(phi) >= 2 * np.pi - 1e-9:
                break
    qs = np.array([c["q"] for c in curva])
    if len(qs):
        log("Faixa ao longo da curva: q de %.4f a %.4f ; M de %.3f a %.3f ; chi_eff de %+.4f a %+.4f"
            % (qs.min(), qs.max(), min(c["M"] for c in curva), max(c["M"] for c in curva),
               min(c["chi_eff"] for c in curva), max(c["chi_eff"] for c in curva)))
    log("(%.0f s)" % (time.time() - t0))
    with open(SAIDA + ".txt", "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(SAIDA + ".json", "w") as fh:
        json.dump(dict(alvo=alvo.tolist(), curva=curva), fh, indent=0)
