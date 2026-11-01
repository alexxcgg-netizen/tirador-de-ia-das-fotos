"""Experimento 17 (L01/L02, tarefa 3): os pares 'exatos' do exp07 com os observaveis corrigidos.

A: M = 65, q = 1.2, chi = (0.3, -0.2), D = 400 Mpc, iota = 50 graus, janela desde 10 Hz.
(T0) quatro memorias so m = 0, deslocamento de janela: (a) o par do exp07 sem resolver de novo; (b) resolvido de novo
     (exp17_resolver, partindo do par do exp07). (T) todos os m: alvo de A com phi'_A = 0 (azimute medido da fase
     orbital no pico); para phi'_B em 8 valores resolve (iota, chi1, M) por continuacao a partir da solucao T0.
Formas de onda: comparar2 (observaveis, FRAC_INICIO = 0.7, todos os modos, h_+, aLIGO e ET, fmin = 10 Hz).
Saidas: resultados/exp17_pares.txt, resultados/exp17_pares.json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
import exp17_resolver as R                               # noqa: E402
import observaveis as O                                  # noqa: E402
import deteccao as Dt                                    # noqa: E402

A = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0))
CASOS = [(1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (6.0, 0.0), (2.0, 0.5), (3.0, -0.5)]
PHIS_B = tuple(np.arange(8) * np.pi / 4)
SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_pares")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def strain(q, c1, c2, M, D, iota, phi_ti):
    O.FRAC_INICIO = 0.7
    t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)
    O.FRAC_INICIO = 0.9
    lista = sorted(h)
    ts, s = Dt.strain_observador(t, h, lista, M, D, iota, phi_ti)
    del t, h
    return ts, s


def comparar(pA, pB):
    tA, sA = strain(pA["q"], pA["c1"], pA["c2"], pA["M"], pA["D"], pA["iota"], pA["phi"])
    tB, sB = strain(pB["q"], pB["c1"], pB["c2"], pB["M"], pB["D"], pB["iota"], pB["phi"])
    out = {}
    for psd in ("aLIGO", "ET"):
        c = O.comparar2(tA, sA, tB, sB, psd, 10.0)
        out[psd] = dict(match=c["match"], snr_A=c["snr_A"], snr_B=c["snr_B"], rho_crit=c["rho_crit"])
    return out


if __name__ == "__main__":
    t0 = time.time()
    e7 = json.load(open(os.path.join(AQUI, "..", "resultados", "exp07_pares.json")))
    pares7 = {(p["qB"], p["c2B"]): p for p in e7["pares"]}
    alvo0, auxA = R.alvo_de(A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"], 0.0, "T0")
    alvoT, _ = R.alvo_de(A["q"], A["c1"], A["c2"], A["M"], A["D"], A["iota"], 0.0, "T")
    log("A: M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus; janela desde 10 Hz (nivel A, observaveis)")
    log("  T0 (m = 0, desl. de janela): " + ", ".join("%s %.6e" % kv for kv in alvo0.items()))
    log("  T  (todos os m, phi'_A = 0): " + ", ".join("%s %.6e" % kv for kv in alvoT.items()))
    log("  T/T0 - 1: " + ", ".join("%s %+.3e" % (k, alvoT[k] / alvo0[k] - 1) for k in alvo0))
    log("  M_f = %.6f M, E_janela = %.6f, Phi_pico = %.3f rad" % (auxA["M_f"], auxA["E_janela"], auxA["Phi_pico"]))
    log("  [exp07, desl. total, so m = 0: desl 1.829e-22, spin -2.498e-25 s, CM -3.069e-26 s, giro -3.157e-41 rad]")
    resultados = []
    for (qB, c2B) in CASOS:
        p7 = pares7[(qB, c2B)]
        log("")
        log("Caso q_B = %.1f, chi2_B = %+.1f; par do exp07: M %.4f, chi1 %+.5f, D %.3f Mpc, iota %.4f graus"
            % (qB, c2B, p7["M"], p7["c1"], p7["D"], np.degrees(p7["iota"])))
        # (a) par do exp07 com os observaveis novos (D_B e M_B do exp07, sem resolver)
        r = C.memorias_varias(qB, p7["c1"], c2B, [p7["M"]])[0]
        v0 = C.fisicos(C.so_m0(r["mem_pico"]), p7["iota"], 0.0, p7["M"], p7["D"])
        d_a = {k: v0[k] / alvo0[k] - 1 for k in alvo0}
        log("  (a) par do exp07 em T0 (desl. de janela), sem resolver: " + ", ".join("%s %+.2e" % kv for kv in d_a.items()))
        # (b) T0 resolvido de novo
        rs = R.Resolvedor(alvo0, qB, c2B, "T0")
        s0 = rs.resolver((p7["iota"], p7["c1"], p7["M"]))
        log("  (b) T0 resolvido: M %.4f, chi1 %+.5f, D %.3f Mpc, iota %.4f graus | residuo max %.1e (%d avaliacoes, %d ondas)%s"
            % (s0["M"], s0["chi1"], s0["D"], np.degrees(s0["iota"]), s0["res"], s0["nfev"], s0["ondas"],
               " NO LIMITE do dominio" if s0["no_limite"] else ""))
        log("      desloca: M %+.4f, chi1 %+.5f, D %+.3f Mpc, iota %+.4f graus ; M_f B = %.6f M (M_f B M_B / M_f A M_A - 1 = %+.4f)"
            % (s0["M"] - p7["M"], s0["chi1"] - p7["c1"], s0["D"] - p7["D"], np.degrees(s0["iota"] - p7["iota"]), s0["M_f"],
               s0["M_f"] * s0["M"] / (auxA["M_f"] * A["M"]) - 1))
        reg = dict(qB=qB, c2B=c2B, exp07=dict(M=p7["M"], c1=p7["c1"], D=p7["D"], iota=p7["iota"]), dif_a=d_a, T0=s0)
        # (T) todos os m, continuacao em phi'_B
        curva = []
        x = (s0["iota"], s0["chi1"], s0["M"])
        for phB in PHIS_B:
            rt = R.Resolvedor(alvoT, qB, c2B, "T", phiB=phB)
            sT = rt.resolver(x)
            curva.append(sT)
            x = (sT["iota"], sT["chi1"], sT["M"])
        reg["T"] = curva
        res = np.array([c["res"] for c in curva])
        for nm in ("M", "chi1", "D", "iota"):
            vals = np.array([c[nm] for c in curva])
            if nm == "iota":
                vals = np.degrees(vals)
            log("  (T) phi'_B em 8 valores: %-5s de %.4f a %.4f" % (nm, vals.min(), vals.max()))
        log("  (T) residuo max ao longo da curva: %.1e ; no limite em %d de 8" % (res.max(), sum(c["no_limite"] for c in curva)))
        # formas de onda (so para solucoes dentro do dominio com residuo pequeno)
        if s0["res"] < 1e-6 and not s0["no_limite"]:
            pA = dict(A, phi=0.0)
            pB = dict(q=qB, c1=s0["chi1"], c2=c2B, M=s0["M"], D=s0["D"], iota=s0["iota"], phi=0.0)
            cmp0 = comparar(pA, pB)
            reg["onda_T0"] = cmp0
            log("  onda T0 (phi = 0 nos dois): match aLIGO %.4f (SNR_A %.1f, rho_crit %.2f) ; ET %.4f (SNR_A %.0f, rho_crit %.2f)"
                % (cmp0["aLIGO"]["match"], cmp0["aLIGO"]["snr_A"], cmp0["aLIGO"]["rho_crit"],
                   cmp0["ET"]["match"], cmp0["ET"]["snr_A"], cmp0["ET"]["rho_crit"]))
            ondas = []
            for c in curva[::2]:
                if c["res"] > 1e-6 or c["no_limite"]:
                    continue
                pA = dict(A, phi=0.0 + auxA["Phi_pico"])
                pB = dict(q=qB, c1=c["chi1"], c2=c2B, M=c["M"], D=c["D"], iota=c["iota"], phi=c["phiB"] + c["Phi_pico"])
                ondas.append((c["phiB"], comparar(pA, pB)))
            reg["onda_T"] = ondas
            if ondas:
                mts = np.array([o[1]["aLIGO"]["match"] for o in ondas])
                rcs = np.array([o[1]["aLIGO"]["rho_crit"] for o in ondas])
                log("  onda T (phi'_B = 0, pi/2, pi, 3pi/2): match aLIGO de %.4f a %.4f ; rho_crit de %.2f a %.2f"
                    % (mts.min(), mts.max(), rcs.min(), rcs.max()))
        resultados.append(reg)
        log("  (%.0f s)" % (time.time() - t0))
    with open(SAIDA + ".txt", "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(SAIDA + ".json", "w") as fh:
        json.dump(dict(A=A, alvo_T0=alvo0, alvo_T=alvoT, auxA={k: (v if not isinstance(v, dict) else v) for k, v in auxA.items()},
                       pares=resultados), fh, indent=1, default=float)
