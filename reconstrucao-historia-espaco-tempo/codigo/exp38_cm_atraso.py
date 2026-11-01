"""Experimento 38 (linha L19): a memoria de CM como atraso do degrau de memoria.

Pergunta: o degrau de memoria da deformacao (modos m = 0 de RN do NRHybSur3dq8_CCE) chega M_f/2 depois do
degrau previsto pelo fluxo dos modos oscilatorios (memoria nula, nivel A)? O transiente do exp09 e esse atraso?

Identidade [D] (Nichols 2018, eq. 3.11 e nota 8): com D_l(u) = [h_l0(u) - h_l0(u_s)] - [S_l(u) - S_l(u_s)]
(S = memoria nula acumulada pelo fluxo desde u_s) e D(u_f) = 0,
    DeltaK_l = int D_l du - [u D_l] = -(int u dh_l0 - int u dS_l) = -DeltaJ_l * (centroide(dh) - centroide(dS)),
logo a memoria de CM (no nivel da deformacao) e menos o deslocamento vezes o ATRASO DO CENTROIDE da taxa de
memoria. A parte ordinaria do codigo, -(3/2) M_f DeltaJ_l / Dfrak(l), da delta_l = (3/2) M_f / Dfrak(l) =
12 M_f / ((l-1) l (l+1) (l+2)): M_f/2 (l = 2), M_f/30 (l = 4), M_f/140 (l = 6), M_f/420 (l = 8).

Para cada sistema (q de 1 a 8, varios spins; M = 65, janela desde 10 Hz) mede:
  a) previsao: delta_ord_l, delta_tot_l = -cm_l/desl_l (codigo, nivel A, deslocamento de janela);
  b) D_l(u) desde t_i: valor final (deslocamento C - A), deriva na inspiral (antes da fusao), area total;
  c) atraso de centroide com os degraus normalizados (lambda = R_fim/S_fim), para varios inicios u_s;
  d) teste pontual: D(u) ~ c - delta dS/du em [-60, 60] M (fracao explicada) e melhor deslocamento temporal
     R(u) ~ lambda S(u - delta) + c em [-100, 100] M;
  e) toque quase normal: ajuste de D para u >= 16 M com o QNM (2,0,0) do remanescente (qnm + NRSur3dq8Remnant);
  f) controle magnetico: int (h30_RN - h30_fluxo) du = 0 se nao ha parte ordinaria de spin (cargas
     magneticas l = 3 nulas no inicio e no fim);
  g) (q <= 4) modos ausentes do substituto CCE ((3,1), (4,2), (4,1), l = 5 menos (5,5)): fracao do fluxo
     acumulado que eles carregam, pelo NRSur7dq4.
Saida: resultados/exp38_cm_atraso.txt e .json; series de q = 1, 4 e A em resultados/exp38_series.npz (so
u, S, R, D por l; poucos MB).
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
RES = os.path.join(AQUI, "..", "resultados")

SISTEMAS = [(1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (6.0, 0.0, 0.0), (8.0, 0.0, 0.0),
            (1.0, 0.6, 0.6), (1.0, -0.6, -0.6), (3.0, 0.6, 0.0), (1.2, 0.3, -0.2), (8.0, 0.6, 0.0)]
M_SOL, F_INI = 65.0, 10.0
US = (-2000.0, -1000.0, -500.0, -300.0, -200.0, -100.0)


def series_modos(t, h, ti, lista):
    """Memoria nula acumulada S_l0(u) desde t_i (mesma quadratura de observaveis.serie_memoria), taxa e h^B."""
    import binarias as B
    import observaveis as O
    c_osc = B.calculadoras()[0]
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    Hd = O.derivada(H, t[1] - t[0], 8)
    k = int(np.searchsorted(t, ti, side="left"))
    H, Hd = H[k - 1:], Hd[k - 1:]
    n = H.shape[0]
    R = np.zeros((n, len(lista)), complex)
    HB = np.zeros_like(R)
    for i in range(0, n, 2048):
        hB, _, dm = c_osc.partes_instantaneas(H[i:i + 2048], Hd[i:i + 2048], lista)
        R[i:i + 2048] = dm
        HB[i:i + 2048] = hB
    del H, Hd
    dtt = t[1] - t[0]
    a = (ti - t[k - 1]) / dtt
    L = t[k] - ti
    acum = np.zeros((n, len(lista)), complex)
    acum[1] = 0.5 * L * ((1 - a) * R[0] + (1 + a) * R[1])
    acum[2:] = acum[1] + np.cumsum(0.5 * dtt * (R[1:-1] + R[2:]), axis=0)
    S = acum.copy()
    S[0] = 0
    taxa = R.copy()
    taxa[0] = (1 - a) * R[0] + a * R[1]
    hb = HB.copy()
    hb[0] = (1 - a) * HB[0] + a * HB[1]
    ts = np.concatenate([[ti], t[k:]])
    return ts, S, taxa, hb


def _trap(y, x):
    r = np.trapezoid(y, x)
    return complex(r) if np.iscomplexobj(r) else float(r)


def centroide(ts, R, S, us, normalizar=True):
    """Atraso do centroide de dR em relacao ao de dS a partir de u_s (degraus normalizados se pedido)."""
    s = ts >= us
    t = ts[s]
    r = R[s] - np.interp(us, ts, R)
    x = S[s] - np.interp(us, ts, S)
    lam = r[-1] / x[-1] if normalizar else 1.0
    Dp = r - lam * x
    area = _trap(Dp, t)
    # delta_c = -[int Dp du - u_f Dp(u_f)] / degrau ; com normalizacao Dp(u_f) = 0
    return float(-(area - t[-1] * Dp[-1]) / r[-1]), float(lam - 1)


def qnm_200(q, c1, c2):
    import qnm
    import surfinBH
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    mf = float(fit.mf(q, [0, 0, c1], [0, 0, c2])[0])
    chif = float(fit.chif(q, [0, 0, c1], [0, 0, c2])[0][2])
    om = qnm.modes_cache(s=-2, l=2, m=0, n=0)(a=abs(chif))[0] / mf
    return mf, chif, complex(om)


def faltantes(q, c1, c2):
    """Fracao de S_20, S_40 (acumulados desde o inicio do NRSur7dq4, ~-4300 M) que vem dos modos fora do CCE."""
    import gwsurrogate
    import binarias as B
    import observaveis as O
    from memorias import CalculadoraMemoria
    sur = gwsurrogate.LoadSurrogate("NRSur7dq4")
    t, h, _ = sur(q, [0, 0, c1], [0, 0, c2], dt=0.25, f_low=0)
    h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
    t = np.asarray(t)
    out = {}
    for nome, L in (("todos", [k for k in h if k[1] != 0]), ("cce", [k for k in B.lista_osc() if k in h])):
        c = CalculadoraMemoria(L, lmax_saida=8)
        H = np.stack([h[k] for k in L], axis=1)
        _, _, dm = c.partes_instantaneas(H, O.derivada(H, 0.25, 8), [(2, 0), (4, 0)])
        out[nome] = np.cumsum(dm.real, axis=0) * 0.25
    del h
    fr = out["todos"][-1] / out["cce"][-1] - 1
    j = np.searchsorted(t, -100.0)
    fr100 = (out["todos"][-1] - out["todos"][j]) / (out["cce"][-1] - out["cce"][j]) - 1
    return dict(frac20=float(fr[0]), frac40=float(fr[1]), frac20_ult100=float(fr100[0]),
                frac40_ult100=float(fr100[1]), t0=float(t[0]))


def analisar(sis):
    import observaveis as O
    from harmonicos import Dfrak
    from scipy.optimize import least_squares, minimize_scalar
    q, c1, c2 = sis
    t0 = time.time()
    t, h, ti = O.gerar_janela(q, c1, c2, M_SOL, F_INI)
    memA, aux = O.memorias_observaveis(q, c1, c2, M_SOL, F_INI, t=t, h=h, t_i=ti)
    memC, _ = O.memorias_observaveis(q, c1, c2, M_SOL, F_INI, t=t, h=h, t_i=ti, nivel="C")
    v = O.no_observador_completo(memA, np.radians(50.0), 0.0)
    lista = [(2, 0), (3, 0), (4, 0)]
    ts, S, taxa, hb = series_modos(t, h, ti, lista)
    k = int(np.searchsorted(t, ti, side="left"))
    RN = {}
    for (l, m) in lista:
        v0 = O._interp_em(t, h[(l, m)], ti)
        RN[l] = np.concatenate([[0], h[(l, m)][k:] - v0])
    h30abs = np.concatenate([[O._interp_em(t, h[(3, 0)], ti)], h[(3, 0)][k:]])
    del t, h
    Mf = aux["M_f"]
    out = dict(q=q, c1=c1, c2=c2, M_f=Mf, t_i=ti)
    series = dict(u=ts)
    for l, j in ((2, 0), (4, 2)):
        R = RN[l].real
        Sx = S[:, j].real
        rx = taxa[:, j].real
        D = R - Sx
        dJ = memA["deslocamento"][(l, 0)].real
        cm = memA["cm"][(l, 0)].real
        ordn = -1.5 * Mf * dJ / Dfrak(l)
        o = dict(desl_A=dJ, desl_C=memC["deslocamento"][(l, 0)].real, cm_tot=cm, cm_ord=ordn,
                 delta_ord=1.5 * Mf / Dfrak(l), delta_tot=-cm / dJ)
        o["D_fim_rel"] = float(D[-1] / Sx[-1])
        o["area_total"] = _trap(D, ts)
        o["delta_area_total"] = float(-(o["area_total"] - ts[-1] * D[-1]) / Sx[-1])
        # deriva antes da fusao: D (desde t_i) em instantes fixos e razao dD/dS entre dois instantes
        for uu in (-3000.0, -1000.0, -300.0, -100.0, -30.0):
            o["D_rel_%d" % uu] = float(np.interp(uu, ts, D) / Sx[-1])
        for (a_, b_) in ((-2500.0, -300.0), (-1000.0, -100.0), (-300.0, -50.0)):
            o["dD_dS_%d_%d" % (a_, b_)] = float((np.interp(b_, ts, D) - np.interp(a_, ts, D))
                                                / (np.interp(b_, ts, Sx) - np.interp(a_, ts, Sx)))
        o["delta_c"] = {}
        o["lambda_m1"] = {}
        for us in US:
            dc, lm = centroide(ts, R, Sx, us)
            o["delta_c"][str(int(us))] = dc
            o["lambda_m1"][str(int(us))] = lm
        o["delta_c_sem_norm_m100"] = centroide(ts, R, Sx, -100.0, normalizar=False)[0]
        # teste pontual em [-60, 60]
        s = (ts >= -60) & (ts <= 60)
        Dl = D[s] - D[s][0]
        A_ = np.stack([np.ones(s.sum()), -rx[s]], axis=1)
        cf, *_ = np.linalg.lstsq(A_, Dl, rcond=None)
        res = Dl - A_ @ cf
        o["pontual_delta"] = float(cf[1])
        o["pontual_R2"] = float(1 - np.sum(res ** 2) / np.sum((Dl - Dl.mean()) ** 2))
        o["pontual_maxD"] = float(np.max(np.abs(Dl)) / Sx[-1])
        o["pontual_max_delta_ord_Sdot"] = float(o["delta_ord"] * np.max(np.abs(rx[s])) / Sx[-1])
        # melhor deslocamento temporal R(u) ~ lam S(u - d) + c em [-100, 100]
        s2 = (ts >= -100) & (ts <= 100)

        def custo(d):
            Ssh = np.interp(ts[s2] - d, ts, Sx)
            A2 = np.stack([Ssh, np.ones(s2.sum())], axis=1)
            c2_, *_ = np.linalg.lstsq(A2, R[s2], rcond=None)
            return float(np.sum((R[s2] - A2 @ c2_) ** 2))
        r_ = minimize_scalar(custo, bounds=(-10, 20), method="bounded", options=dict(xatol=1e-4))
        o["melhor_desloc"] = float(r_.x)
        o["melhor_desloc_rms_rel"] = float(np.sqrt(r_.fun / s2.sum()) / Sx[-1])
        o["desloc0_rms_rel"] = float(np.sqrt(custo(0.0) / s2.sum()) / Sx[-1])
        o["desloc_ord_rms_rel"] = float(np.sqrt(custo(o["delta_ord"]) / s2.sum()) / Sx[-1])
        # pico das taxas
        dR = np.gradient(R, ts)
        sp = (ts > -50) & (ts < 60)
        o["t_pico_taxa_fluxo"] = float(ts[sp][np.argmax(rx[sp])])
        o["t_pico_taxa_RN"] = float(ts[sp][np.argmax(dR[sp])])
        out["l%d" % l] = o
        series["S%d" % l] = Sx.astype(np.float32)
        series["R%d" % l] = R.astype(np.float32)
        series["taxa%d" % l] = rx.astype(np.float32)
    # toque quase normal (2,0,0)
    mf_fit, chif, om = qnm_200(q, c1, c2)
    R = RN[2].real
    D = R - S[:, 0].real
    s = ts >= 16.0
    tt = ts[s] - 16.0
    y = D[s]

    def res_q(p):
        c, a, ph = p
        return y - (c + a * np.exp(om.imag * tt) * np.cos(om.real * tt + ph))

    def res_l(p):
        c, a, ph, wr, wi = p
        return y - (c + a * np.exp(-wi * tt) * np.cos(wr * tt + ph))
    rq = least_squares(res_q, [y[-1], np.max(np.abs(y)), 0.0])
    rl = least_squares(res_l, [rq.x[0], rq.x[1], rq.x[2], om.real, -om.imag])
    out["qnm"] = dict(M_f_fit=mf_fit, chi_f=chif, omega_200=[om.real, om.imag],
                      A_rel=float(abs(rq.x[1]) / S[-1, 0].real), rms_res_rel=float(np.std(rq.fun) / np.std(y)),
                      livre_omega=[float(rl.x[3]), float(-rl.x[4])], livre_rms_rel=float(np.std(rl.fun) / np.std(y)))
    # controle magnetico: h30 absoluto (o modo de spin e instantaneo, nao acumulado)
    hB30 = hb[:, 1]
    mag = {}
    for us in (None, -2500.0, -1000.0, -300.0):
        s = ts >= (ts[0] if us is None else us)
        mag["inicio" if us is None else str(int(us))] = float((_trap(h30abs[s], ts[s]) / _trap(hB30[s], ts[s])).real - 1)
    out["magnetico"] = mag
    out["tempo_s"] = time.time() - t0
    out["obs_iota50"] = dict(desl=v["deslocamento"], cm=v["cm"], delta_obs=-v["cm"] / v["deslocamento"])
    return out, series


def analisar_completo(sis):
    """analisar + modos ausentes (q <= 4) + escolha das series guardadas."""
    q, c1, c2 = sis
    out, series = analisar(sis)
    if q <= 4.0:
        out["faltantes"] = faltantes(q, c1, c2)
    guardar = sis in ((1.0, 0.0, 0.0), (4.0, 0.0, 0.0), (1.2, 0.3, -0.2))
    if not guardar:
        series = None
    else:                                               # guarda so u >= -3000 M (a figura e o exp38_deriva usam u_s >= -1000 M)
        sel = series["u"] >= -3000.0
        series = {k: v[sel] for k, v in series.items()}
    return out, series


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    with mp.get_context("spawn").Pool(2) as pool:
        resultados = pool.map(analisar_completo, SISTEMAS)
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    log("exp38: memoria de CM como atraso (NRHybSur3dq8_CCE, M = 65, janela desde 10 Hz, nivel A x modos m = 0 de RN)")
    log("delta_ord_l = (3/2) M_f / Dfrak(l): l = 2 -> M_f/2 ; l = 4 -> M_f/30 ; delta_tot = -cm_l/desl_l (codigo)")
    js = []
    npz = {}
    for (q, c1, c2), (o, ser) in zip(SISTEMAS, resultados):
        js.append(o)
        log()
        log("q = %.1f chi = (%+.1f, %+.1f): M_f = %.5f ; QNM (2,0,0) M omega = %.4f - %.4f i (livre: %.4f - %.4f i) ; "
            "toque A/desl = %.3f, ajuste explica %.0f%% da variancia de D para u >= 16 M"
            % (q, c1, c2, o["M_f"], o["qnm"]["omega_200"][0], -o["qnm"]["omega_200"][1], o["qnm"]["livre_omega"][0],
               o["qnm"]["livre_omega"][1], o["qnm"]["A_rel"], 100 * (1 - o["qnm"]["rms_res_rel"] ** 2)))
        for l in (2, 4):
            a = o["l%d" % l]
            log("  l = %d: desl A %.5e C %.5e (C/A-1 = %+.2e) ; cm tot %.4e (ord %.4e) ; delta_ord %.4f M, delta_tot %.4f M"
                % (l, a["desl_A"], a["desl_C"], a["desl_C"] / a["desl_A"] - 1, a["cm_tot"], a["cm_ord"], a["delta_ord"],
                   a["delta_tot"]))
            log("        area total int D = %+.4f (prevista = cm_tot = %+.4f) -> delta_area_total = %+.3f M ; D/desl em "
                "-3000/-1000/-300/-100/-30 M: %s" % (a["area_total"], a["cm_tot"], a["delta_area_total"],
                                                     " ".join("%+.1e" % a["D_rel_%d" % u] for u in (-3000, -1000, -300, -100, -30))))
            log("        deriva dD/dS: [-2500,-300] %+.3f ; [-1000,-100] %+.3f ; [-300,-50] %+.3f"
                % (a["dD_dS_-2500_-300"], a["dD_dS_-1000_-100"], a["dD_dS_-300_-50"]))
            log("        atraso de centroide normalizado delta_c(u_s) [M] (lambda-1): "
                + " ".join("%d: %+.3f (%+.1e)" % (int(u), a["delta_c"][str(int(u))], a["lambda_m1"][str(int(u))]) for u in US))
            log("        pontual em [-60,60]: max|D|/desl = %.3f contra delta_ord max(dS/du)/desl = %.4f ; ajuste D ~ c - delta dS: "
                "delta = %+.2f M, R^2 = %.3f" % (a["pontual_maxD"], a["pontual_max_delta_ord_Sdot"], a["pontual_delta"],
                                                 a["pontual_R2"]))
            log("        melhor deslocamento R(u) ~ lam S(u-d)+c em [-100,100]: d = %+.2f M (rms/desl %.2e ; d = 0: %.2e ; d = delta_ord: %.2e)"
                " ; pico da taxa: fluxo %+.2f M, RN %+.2f M"
                % (a["melhor_desloc"], a["melhor_desloc_rms_rel"], a["desloc0_rms_rel"], a["desloc_ord_rms_rel"],
                   a["t_pico_taxa_fluxo"], a["t_pico_taxa_RN"]))
        log("  controle magnetico int h30_RN / int hB30_fluxo - 1: " + " ".join("%s: %+.2e" % kv for kv in o["magnetico"].items()))
        if "faltantes" in o:
            f = o["faltantes"]
            log("  modos fora do CCE (NRSur7dq4): +%.2e em S20, %+.2e em S40 (acumulado desde %.0f M) ; ultimos 100 M: %+.2e, %+.2e"
                % (f["frac20"], f["frac40"], f["t0"], f["frac20_ult100"], f["frac40_ult100"]))
        log("  observador iota = 50 graus: CM/desl = %.4f M  -> atraso efetivo %.4f M = %.1f us (M = 65)"
            % (o["obs_iota50"]["cm"] / o["obs_iota50"]["desl"], o["obs_iota50"]["delta_obs"],
               o["obs_iota50"]["delta_obs"] * M_SOL * 4.925490947641267e-06 * 1e6))
        if ser is not None:
            nome = "q%.1f_%+.1f_%+.1f" % (q, c1, c2)
            for kk, vv in ser.items():
                npz[nome + "_" + kk] = vv
    log()
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "exp38_cm_atraso.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(RES, "exp38_cm_atraso.json"), "w") as f:
        json.dump(js, f, indent=1, default=float)
    np.savez_compressed(os.path.join(RES, "exp38_series.npz"), **npz)
