"""Experimento 17 (L01): interpretacao dos jacobianos — ponto A, espacos nulos, loci exatos e restricao de M.

Usa exp17_analise_jac (mesmas funcoes) e os dados de exp17_jacobianos.py (grade + ponto A).
Itens:
  (1) ponto A: sigmas de T0, T, O (abs e rel), comparacao com rev_R1_jacobiano (deslocamento total);
  (2) espaco nulo de T0 (dimensao 2) na carta do exp07: d(ln M, chi1, ln D, iota)/d(q, chi2) ao longo da fibra;
  (3) direcao quase nula intrinseca (D, iota fixos) em (ln Mc, eta, chi_eff, chi_a) ao longo da grade;
  (4) T com iota e D conhecidos: tangente da fibra 1D (d lambda / d phi');
  (5) loci: iota = 90 (paridade), iota = 0 (fator sin^2 e m = 2), q = 1 com chi1 = chi2 (troca), paridade direta do teste;
  (6) razao CM/(M desl) no observador (restricao de M_B usada em exp17_fibra).
Saida: resultados/exp17_interpretacao.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_analise_jac as J                            # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_interpretacao.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def conv_fis(v, q, c1, c2):
    """(d lnM, dq, dchi1, dchi2) -> (d ln Mc, d eta, d chi_eff, d chi_a, d ln eta)."""
    dlnM, dq, dc1, dc2 = v[:4]
    eta = q / (1 + q) ** 2
    deta = (1 - q) / (1 + q) ** 3 * dq
    dlnMc = dlnM + 0.6 * deta / eta
    dce = (q * dc1 + dc2) / (1 + q) + (c1 - c2) / (1 + q) ** 2 * dq
    dca = 0.5 * (dc1 - dc2)
    return np.array([dlnMc, deta, dce, dca, deta / eta])


if __name__ == "__main__":
    np.set_printoptions(linewidth=150, precision=4, suppress=False)
    io50 = np.radians(50.0)
    # ---------------------------------------------------------------- (1) ponto A
    dA = J.carregar_A()
    jA = 1                                   # M = 65
    FrA = J.fref(dA, jA)
    log("(1) Ponto A (q 1.2, chi (0.3, -0.2), M 65, D 400, iota 50, phi' = 0); colunas %s" % (J.COLS,))
    log("    F_ref (fisico, T0, iota 50): %s" % FrA)
    for conj in ("T0", "T", "O", "O0"):
        for caso in ("livre", "iota", "iotaD", "intr"):
            for esc in ("abs", "rel"):
                r = J.analisar(dA, jA, io50, 0.0, conj, caso, esc, FrA)
                log("    %-3s %-6s %-4s n=%d sigma = %s  tau = %.1e  posto %d"
                    % (conj, caso, esc, r["n"], np.array2string(r["sv"], precision=4), r["tau"], r["posto"]))
    log("    [rev_R1 (desl. total, linhas / |F(50)|): sv 4.395 1.665 0.608 0.115; intrinsecos 3.147 0.264 0.0407 6.59e-4]")
    r = J.analisar(dA, jA, io50, 0.0, "T0", "livre", "rel", FrA)
    log("    T0 livre rel: jacobiano relativo (linhas desl, spin, CM, giro):")
    for i, nm in enumerate(J.TIPOS):
        log("      %-12s %s   (erro max %.1e)" % (nm, np.array2string(r["J"][i], precision=4), r["E"][i].max()))
    # ---------------------------------------------------------------- (2) espaco nulo T0 na carta do exp07
    log("")
    log("(2) Espaco nulo de T0 (livre): tangente da fibra na carta do exp07 (q_B, chi2_B livres)")
    log("    d(ln M, chi1, ln D, iota[graus]) / dq  e  / dchi2, em A e em pontos da grade (iota = 50, M = 65)")

    def tangente(dp, j, iota, phi=0.0, conj="T0"):
        F0, Jm, E = J.jacobiano(dp, j, iota, phi, conj == "T0")
        Jm = Jm / np.abs(F0)[:, None]                    # escala relativa (o numero de condicao fica sem unidades)
        A = Jm[:, [0, 2, 4, 5]]
        Bm = Jm[:, [1, 3]]
        X = -np.linalg.solve(A, Bm)
        X[3] = np.degrees(X[3])
        return X, np.linalg.cond(A)
    X, cnd = tangente(dA, jA, io50)
    log("    A: d/dq   = lnM %+.4f  chi1 %+.4f  lnD %+.4f  iota %+.3f graus" % tuple(X[:, 0]))
    log("       d/dchi2 = lnM %+.4f  chi1 %+.4f  lnD %+.4f  iota %+.3f graus   (cond %.1e)" % (tuple(X[:, 1]) + (cnd,)))
    for i, p in enumerate(J.PONTOS):
        if p[2] != 0.0:
            continue
        dp = J.carregar_ponto(i)
        X, cnd = tangente(dp, 1, io50)
        log("    q %.1f chi (%+.1f, %+.1f): d/dq: lnM %+.4f chi1 %+.4f lnD %+.4f iota %+.3f | d/dchi2: lnM %+.4f chi1 %+.4f lnD %+.4f iota %+.3f"
            % ((p[0], p[1], p[2]) + tuple(X[:, 0]) + tuple(X[:, 1])))
    # ---------------------------------------------------------------- (3) direcao quase nula intrinseca
    log("")
    log("(3) Direcao quase nula intrinseca (T0, D e iota fixos, escala rel): v_min em (ln M, q, chi1, chi2) e em")
    log("    (d ln Mc, d eta, d chi_eff, d chi_a), normalizada por |d ln eta| = 1; sigma_4/sigma_1")
    r = J.analisar(dA, jA, io50, 0.0, "T0", "intr", "rel", FrA)
    v = r["Vt"][-1]
    w = conv_fis(v, 1.2, 0.3, -0.2)
    log("    A: v = %s ; (dlnMc, deta, dchi_eff, dchi_a)/|dln eta| = %s ; sigma4/sigma1 = %.2e"
        % (np.array2string(v, precision=4), np.array2string(w[:4] / abs(w[4]), precision=4), r["sv"][-1] / r["sv"][0]))
    tab = []
    for i, p in enumerate(J.PONTOS):
        dp = J.carregar_ponto(i)
        for j, M in enumerate(J.MS):
            Fr = J.fref(dp, j)
            for io in (30.0, 50.0, 70.0):
                rr = J.analisar(dp, j, np.radians(io), 0.0, "T0", "intr", "rel", Fr)
                if rr is None:
                    continue
                v = rr["Vt"][-1]
                w = conv_fis(v, *p)
                if abs(w[4]) < 1e-12:
                    continue
                tab.append((p, M, io, rr["sv"][-1] / rr["sv"][0], w[0] / w[4], w[2] / w[4], w[3] / w[4],
                            abs(v[1]), rr["sv"][-1] / rr["tau"]))
    arr = np.array([t[3:] for t in tab])
    log("    grade (q != 1 ou chi1 != chi2; iota 30, 50, 70): N = %d" % len(tab))
    for k, nm in enumerate(("sigma4/sigma1", "dlnMc/dln eta", "dchi_eff/dln eta", "dchi_a/dln eta", "|v_q|", "sigma4/tau")):
        log("      %-17s mediana %+.3e  percentis 10/90: %+.3e / %+.3e" % (nm, np.median(arr[:, k]), np.percentile(arr[:, k], 10),
                                                                     np.percentile(arr[:, k], 90)))
    for q in (1.2, 2.0, 3.0, 5.0):
        sel = np.array([abs(t[0][0] - q) < 1e-9 for t in tab])
        if sel.any():
            log("      q = %.1f: dchi_eff/dln eta mediana %+.3f ; dlnMc/dln eta %+.3f ; sigma4/sigma1 %.2e"
                % (q, np.median(arr[sel, 2]), np.median(arr[sel, 1]), np.median(arr[sel, 0])))
    # ---------------------------------------------------------------- (4) T com iota e D conhecidos
    log("")
    log("(4) T com iota e D conhecidos (n = 5: ln M, q, chi1, chi2, phi'): tangente da fibra 1D, normalizada por d phi' = 1 rad")
    for phi in J.PHIS[:3]:
        r = J.analisar(dA, jA, io50, phi, "T", "iotaD", "abs", FrA)
        v = r["Vt"][-1] / r["Vt"][-1][-1]
        log("    A, phi' = %.2f: sigma %s ; d(lnM, q, chi1, chi2)/dphi' = %s" % (phi, np.array2string(r["sv"], precision=3),
                                                                             np.array2string(v[:4], precision=4)))
    # ---------------------------------------------------------------- (5) loci
    log("")
    log("(5) Loci exatos")
    # (5a) iota = 90: linhas spin e giro so na coluna iota
    F0, Jm, E = J.jacobiano(dA, jA, np.pi / 2, 0.7, False)
    Fr = FrA
    Js = Jm / np.abs(Fr)[:, None]
    for i in (1, 3):
        outras = np.max(np.abs(np.delete(Js[i], 5)))
        log("    iota = 90, T (phi' = 0.7): linha %-12s |F|/|F_ref| = %.1e ; max |J| fora da coluna iota = %.1e ; J_iota = %.3e"
            % (J.TIPOS[i], abs(F0[i] / Fr[i]), outras, Js[i, 5]))
    log("    desl e CM: J_iota em 90 graus = %.1e, %.1e (pares em iota - pi/2)" % (Js[0, 5], Js[2, 5]))
    # (5b) iota = 0 e perto: T0 e T
    for io in (0.0, 1e-3, 1e-2, np.radians(2.0)):
        for conj in ("T0", "T", "O", "O0"):
            r = J.analisar(dA, jA, io, 0.7, conj, "livre", "abs", FrA)
            log("    iota = %.4f rad, %-3s: |F|/|F_ref| = %s ; sigma = %s ; tau = %.1e ; posto %d"
                % (io, conj, np.array2string(np.abs(r["F"] / FrA[[0, 1, 2, 3][:len(r["F"])]]), precision=2),
                   np.array2string(r["sv"], precision=3), r["tau"], r["posto"]))
    # (5c) q = 1, chi1 = chi2
    log("    q = 1, chi1 = chi2 (simetria de troca): colunas (escala abs, iota 50, M 65)")
    for i, p in enumerate(J.PONTOS):
        if p[0] != 1.0 or p[1] != p[2]:
            continue
        dp = J.carregar_ponto(i)
        Fr = J.fref(dp, 1)
        for conj in ("T0", "T"):
            F0, Jm, E = J.jacobiano(dp, 1, io50, 0.7, conj == "T0")
            Js = Jm / np.abs(Fr)[:, None]
            Es = E / np.abs(Fr)[:, None]
            nq = np.linalg.norm(Js[:, 1])
            ndif = np.linalg.norm(Js[:, 2] - Js[:, 3])
            nref = np.linalg.norm(Js[:, 2])
            log("      chi = %+.1f %-2s: |col q| = %.2e (erro %.1e) ; |col chi1 - col chi2| = %.2e (erro %.1e) ; |col chi1| = %.2e"
                % (p[1], conj, nq, np.linalg.norm(Es[:, 1]), ndif, np.linalg.norm(Es[:, 2] + Es[:, 3]), nref))
            for caso in ("livre", "iota", "iotaD"):
                r = J.analisar(dp, 1, io50, 0.7, conj, caso, "abs", Fr)
                log("         %-6s sigma = %s tau = %.1e posto %d" % (caso, np.array2string(r["sv"], precision=3), r["tau"], r["posto"]))
        # teste de paridade em ln q: (F(1+h) - F(1))/h deve ser O(h) se F e par em ln q
        Y = J.Ys(io50, 0.0, True)[0]
        base = J.val(Y, dp["base"][7])
        g = []
        for k, fr in enumerate(J.FR):
            g.append((J.val(Y, dp["V"][0, k, 0, 1]) - base) / (fr * J.H_INT) / np.abs(base))
        g = np.array(g)
        log("      chi = %+.1f: (F(1+h)-F(1))/(h F) [m=0] para h = 4e-3, 2e-3, 1e-3: %s ; razoes %s"
            % (p[1], np.array2string(g[:, 0], precision=3), np.array2string(g[1:, 0] / g[:-1, 0], precision=3)))
    # (5d) paridade numerica F(pi - iota) = (+, -, +, -) F(iota) com todos os m
    rr = []
    for io in (20.0, 50.0, 75.0):
        Y1 = J.Ys(np.radians(io), 0.7, False)[0]
        Y2 = J.Ys(np.pi - np.radians(io), 0.7, False)[0]
        rr.append(J.val(Y2, dA["base"][7]) / J.val(Y1, dA["base"][7]))
    log("    paridade com todos os m (A, phi' = 0.7): F(pi - iota)/F(iota) = %s" % np.array2string(np.array(rr), precision=10))
    # ---------------------------------------------------------------- (5e) dobra em iota do problema quadrado
    log("")
    log("(5e) T0 com iota e D conhecidos (4 x 4) no ponto A, varrendo iota: det(J) e sigma_4 (escala abs)")
    ant = None
    for io in np.arange(5.0, 89.6, 0.5):
        r = J.analisar(dA, jA, np.radians(io), 0.0, "T0", "iotaD", "abs", FrA)
        dt = np.linalg.det(r["J"])
        if ant is not None and np.sign(dt) != np.sign(ant[1]):
            log("    det muda de sinal entre iota = %.1f e %.1f graus (sigma_4 = %.2e e %.2e; tau = %.1e)"
                % (ant[0], io, ant[2], r["sv"][-1], r["tau"]))
        ant = (io, dt, r["sv"][-1])
    # ---------------------------------------------------------------- (6) razao CM/(M desl)
    log("")
    log("(6) Razao r = CM_adim / desl_adim (= CM / (M desl) fisico) na grade, T0 e T (phi' = k pi/3)")
    rs = {"T0": [], "T": []}
    for i, p in enumerate(J.PONTOS):
        dp = J.carregar_ponto(i)
        for j, M in enumerate(J.MS):
            for io in J.IOTAS + (5.0, 1.0):
                for conj, phis in (("T0", (0.0,)), ("T", J.PHIS)):
                    for phi in phis:
                        Y = J.Ys(np.radians(io), phi, conj == "T0")[0]
                        v = J.val(Y, dp["base"][7 * j])
                        rs[conj].append((v[2] / v[0], p, M, io))
    for conj in rs:
        a = np.array([x[0] for x in rs[conj]])
        k1, k2 = int(np.argmin(a)), int(np.argmax(a))
        log("    %-2s: r de %.4f (%s, M %.0f, iota %.0f) a %.4f (%s, M %.0f, iota %.0f)"
            % (conj, a[k1], rs[conj][k1][1], rs[conj][k1][2], rs[conj][k1][3], a[k2], rs[conj][k2][1], rs[conj][k2][2],
               rs[conj][k2][3]))
    Y = J.Ys(io50, 0.0, True)[0]
    vA = J.val(Y, dA["base"][7])
    log("    A: r = %.4f ; logo M_B = 65 r_A / r_B fica em [%.1f, %.1f] para r_B na faixa acima (T0)"
        % (vA[2] / vA[0], 65 * (vA[2] / vA[0]) / min(x[0] for x in rs["T0"]), 65 * (vA[2] / vA[0]) / max(x[0] for x in rs["T0"])))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
