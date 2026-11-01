"""Experimento 25b (L07): quantos numeros de memoria um detector obtem, e quanto do Fisher da serie de memoria e
retido por compressoes.

Sinal: memoria nula do sistema A num detector (psi = 0) e numa rede de dois detectores a 45 graus (h+ e hx).
Parametros e priors do exp24. Compressoes (estatisticas lineares dos dados quando possivel):
  (a-ideal)  as quatro memorias integradas (desl., spin, CM, giro; janela desde 10 Hz, m = 0) como se medidas com
             erro relativo 1/rho_+ cada (idealizacao da etapa 6): J = grad y^T diag(sigma^-2) grad y;
  (a-real)   o que tem assinatura na banda: amplitude do molde h+ (detector 1) e do molde hx (detector 2, rede);
             J = sum_det (u|ds)(u|ds)^T/(u|u), u = molde de A (estatistica linear exata);
  (b)        o degrau final: (b1) amplitude do molde h+ de A (filtro casado, uma estatistica linear);
             (b2) Delta h_+ de janela medido com erro Delta h/rho_+ (gradiente do valor integrado);
  (c)        MOPED (Heavens, Jimenez & Lahav 2000): y_i = (d s_A/d theta_i | x), i = 1..8; no ponto fiducial retem
             todo o Fisher; fora dele, J(B) = D^T Gamma_A^-1 D, D_ij = (u_i | d_j s_B).
  (d)        amplitude e instante: y = ((s_A|x), (ds_A/dt|x)).
Retencao: informacao mutua gaussiana (bits, com os priors) e desvio a posteriori por parametro.
Tambem: SNR por polarizacao, fracao em banda do degrau e da memoria de spin, atraso de CM contra sigma_t.
Saidas: resultados/exp25_compressao.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402
import observaveis as O                                   # noqa: E402
from deteccao import MSUN_S, MPC_S                        # noqa: E402

T0 = time.time()
LINHAS = []
NOMES = C.NOMES8
INTR = ["lnM", "q", "c1", "c2"]
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def memorias_obs(par, iota=None):
    mem, aux = O.memorias_observaveis(par["q"], par["c1"], par["c2"], par["M"], 10.0, nivel="A", desl="janela",
                                      todos_m=False)
    v = O.valores_fisicos_completo(mem, par["iota"] if iota is None else iota, 0.0, par["M"], par["D"])
    return np.array([v[t] for t in TIPOS]), mem, aux


def gradiente_memorias(par, h=1e-3):
    """d y / d theta (4 x 8) para as quatro memorias integradas no observador."""
    y0, mem0, aux0 = memorias_obs(par)
    g = np.zeros((4, 8))
    for j, nome in enumerate(NOMES):
        if nome == "lnM":
            yp = memorias_obs(dict(par, M=par["M"] * np.exp(h)))[0]
            ym = memorias_obs(dict(par, M=par["M"] * np.exp(-h)))[0]
            g[:, j] = (yp - ym) / (2 * h)
        elif nome in ("q", "c1", "c2"):
            yp = memorias_obs(dict(par, **{nome: par[nome] + h}))[0]
            ym = memorias_obs(dict(par, **{nome: par[nome] - h}))[0]
            g[:, j] = (yp - ym) / (2 * h)
        elif nome == "lnD":
            g[:, j] = -y0 * np.array([1, 1, 1, 2])
        elif nome == "cosi":
            ci = np.cos(par["iota"])
            eps = 1e-5
            vp = O.valores_fisicos_completo(mem0, np.arccos(ci + eps), 0.0, par["M"], par["D"])
            vm = O.valores_fisicos_completo(mem0, np.arccos(ci - eps), 0.0, par["M"], par["D"])
            g[:, j] = (np.array([vp[t] for t in TIPOS]) - np.array([vm[t] for t in TIPOS])) / (2 * eps)
    return y0, g, aux0


def info(J, rot):
    an = C.analise_fisher(J + 0.0, NOMES, C.SIG_PRIOR, intrinsecos=INTR)
    return an


def main():
    A = dict(C.SIST_A)
    M, D, iota = A["M"], A["D"], A["iota"]
    Ms = M * MSUN_S
    # grade fisica: grade nativa de A (N = 2^19), ate 1500 Hz
    E0 = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, 10.0, N=2 ** 19, Fmax=0.6)
    f = E0.F / Ms
    f = f[f <= 1500.0]
    df = f[1] - f[0]
    log("Experimento 25b (L07): o que um detector mede da memoria e compressoes. Sistema A, psi = 0.")
    s1, d1 = C.derivadas_grade(dict(A, psi=0.0), f, E0=E0)
    s2, d2 = C.derivadas_grade(dict(A, psi=np.pi / 4), f, E0=E0)
    res = {}

    # ---------------- L07: SNR por polarizacao, fracoes em banda
    hp, hx, _, _ = E0.canais(iota)
    F = Ms * f
    from scipy.interpolate import CubicSpline
    k = Ms * Ms / (D * MPC_S)
    sp_ = k * CubicSpline(E0.F, hp)(F)
    sx_ = k * CubicSpline(E0.F, hx)(F)
    y0, g, aux = gradiente_memorias(A)
    log("Memorias integradas de A no observador (janela desde 10 Hz, m = 0, nivel A): desl %.4e ; spin %.4e s ; "
        "CM %.4e s ; giro %.4e rad ; M_f = %.4f M" % (y0[0], y0[1], y0[2], y0[3], aux["M_f"]))
    dh = float(np.real(E0.final @ C._Ylist(iota))) * Ms / (D * MPC_S)
    log("Degrau de janela da serie nula (h+ final): %.4e (= desl., dif. rel. %.1e)" % (dh, dh / y0[0] - 1))
    log("Fracao em banda: |2 pi f h~+(f)| / Delta h+ e |h~x(f)| / |int hx du| (memoria de spin):")
    Sxdc = abs(k * hx[1])          # h~x(F -> 0) = int hx du (primeiro bin; F_1 = 7.6e-6/M)
    log("  int hx du (espectro em f -> 0): %.4e s (memoria de spin no observador: %.4e s)" % (Sxdc, abs(y0[1])))
    for f0 in (1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 400.0):
        j = int(np.argmin(np.abs(f - f0)))
        log("  f = %5.0f Hz: degrau %.3f ; spin %.3f" % (f[j], 2 * np.pi * f[j] * abs(sp_[j]) / abs(dh),
                                                      abs(sx_[j]) / Sxdc))
    res["L07"] = {}
    for nome in C.PSDS:
        w = C.psd_grade(nome, len(f), df)
        rp = np.sqrt(C.produto(sp_, sp_, w, df))
        rx = np.sqrt(C.produto(sx_, sx_, w, df))
        frms = np.sqrt(C.produto(2j * np.pi * f * sp_, 2j * np.pi * f * sp_, w, df)) / (2 * np.pi * rp)
        # atraso de CM: sigma de um deslocamento no tempo SO da memoria (demais parametros fixados pela onda)
        dts = 1 / (2 * np.pi * rp * frms)
        # com a amplitude da memoria livre tambem
        u1 = -2j * np.pi * f * sp_
        Gm = np.array([[C.produto(u1, u1, w, df), C.produto(u1, sp_, w, df)],
                       [C.produto(sp_, u1, w, df), C.produto(sp_, sp_, w, df)]])
        dts2 = np.sqrt(np.linalg.inv(Gm)[0, 0])
        cm_atraso = abs(y0[2] / y0[0])
        log("  %-5s: rho_+ = %.3f ; rho_x = %.3f (razao %.1f) ; f_rms = %.1f Hz ; sigma(atraso da memoria) = %.2e s "
            "(%.2e s com amplitude livre) ; |CM/desl| = %.2e s ; razao %.2f"
            % (nome, rp, rx, rp / rx, frms, dts, dts2, cm_atraso, cm_atraso / dts2))
        res["L07"][nome] = dict(rho_p=rp, rho_x=rx, frms=frms, sig_atraso=dts, sig_atraso_amp=dts2, cm_atraso=cm_atraso)

    # ---------------- compressoes
    log("")
    log("Compressoes: informacao mutua gaussiana com os priors (bits) e desvio a posteriori. 'retida' = I_y / I_serie.")
    res["comp"] = {}
    for nome in C.PSDS:
        w = C.psd_grade(nome, len(f), df)
        D1 = [d1[n] for n in NOMES]
        D2 = [d2[n] for n in NOMES]
        G1 = C.matriz_produtos(D1, w, df)
        G2 = C.matriz_produtos(D2, w, df)
        rp = np.sqrt(C.produto(s1, s1, w, df))
        rx = np.sqrt(C.produto(s2, s2, w, df))
        casos = {}
        casos["serie (det. unico)"] = G1
        casos["serie (rede)"] = G1 + G2
        # (a-ideal): 4 memorias com erro relativo 1/rho_+
        sig = np.abs(y0) / rp
        casos["(a-ideal) 4 memorias, erro 1/rho+"] = g.T @ np.diag(sig ** -2) @ g
        # (a-real): amplitude dos moldes h+ (det 1) e hx (det 2)
        v1 = np.array([C.produto(s1, dd, w, df) for dd in D1])
        v2 = np.array([C.produto(s2, dd, w, df) for dd in D2])
        Jb1 = np.outer(v1, v1) / C.produto(s1, s1, w, df)
        Jx = np.outer(v2, v2) / C.produto(s2, s2, w, df)
        casos["(a-real) amplitudes + e x (rede)"] = Jb1 + Jx
        casos["(b1) degrau: amplitude do molde + (det. unico)"] = Jb1
        gd = g[0]
        casos["(b2) degrau: Delta h+ com erro Delta h/rho+"] = np.outer(gd, gd) * (rp / y0[0]) ** 2
        # (d) amplitude e instante
        ut = -2j * np.pi * f * s1
        U = [s1, ut]
        Gu = C.matriz_produtos(U, w, df)
        Vm = np.array([[C.produto(u, dd, w, df) for dd in D1] for u in U])
        casos["(d) amplitude + instante (det. unico)"] = Vm.T @ np.linalg.solve(Gu, Vm)
        # (c) MOPED no fiducial: igual a G1 (verificacao numerica)
        Vm = np.array([[C.produto(u, dd, w, df) for dd in D1] for u in D1])
        sp = np.array([C.SIG_PRIOR[n] for n in NOMES])
        Gw = G1 * np.outer(sp, sp)
        Vw = Vm * np.outer(sp, sp)
        Jm = Vw.T @ np.linalg.pinv(Gw, rcond=1e-13) @ Vw / np.outer(sp, sp)
        casos["(c) MOPED 8 numeros (det. unico)"] = Jm
        ref1 = info(G1, "")
        ref2 = info(G1 + G2, "")
        log("%s:" % nome)
        res["comp"][nome] = {}
        for rot, J in casos.items():
            an = info(J, rot)
            ref = ref2 if "rede" in rot else ref1
            log("  %-48s I = %6.2f bits (retida %5.1f%%) ; I_intr = %5.2f bits (%5.1f%%) ; d_ef = %.2f ; post: %s"
                % (rot, an["mi"], 100 * an["mi"] / ref["mi"], an["mi_intr"],
                   100 * an["mi_intr"] / max(ref["mi_intr"], 1e-12), an["d_ef"],
                   " ".join("%s %.3g" % (n, v) for n, v in zip(NOMES, an["post"]))))
            res["comp"][nome][rot] = dict(mi=an["mi"], mi_intr=an["mi_intr"], d_ef=an["d_ef"], post=an["post"].tolist())

    # ---------------- MOPED fora do fiducial
    log("")
    log("MOPED com vetores do fiducial A aplicado a outras binarias B (detector unico, psi = 0; mesmo t0):")
    Bs = [dict(A, M=70.0), dict(A, q=2.0, c1=0.0, c2=0.0), dict(A, M=100.0, q=3.0, c1=0.5, c2=0.5),
          dict(A, M=45.0, q=1.0, c1=-0.5, c2=-0.5), dict(A, iota=np.radians(80.0))]
    res["moped"] = []
    for Bp in Bs:
        sB, dB = C.derivadas_grade(dict(Bp, psi=0.0), f)
        linha = "  B: M %.0f q %.1f chi (%.1f, %.1f) iota %.0f:" % (Bp["M"], Bp["q"], Bp["c1"], Bp["c2"],
                                                                     np.degrees(Bp["iota"]))
        reg = dict(B={k_: float(v) for k_, v in Bp.items()})
        for nome in ("ET", "CE"):
            w = C.psd_grade(nome, len(f), df)
            D1 = [d1[n] for n in NOMES]
            DB = [dB[n] for n in NOMES]
            GA = C.matriz_produtos(D1, w, df)
            GB = C.matriz_produtos(DB, w, df)
            Vm = np.array([[C.produto(u, dd, w, df) for dd in DB] for u in D1])
            sp = np.array([C.SIG_PRIOR[n] for n in NOMES])
            Jm = (Vm * np.outer(sp, sp)).T @ np.linalg.pinv(GA * np.outer(sp, sp), rcond=1e-13) @ (Vm * np.outer(sp, sp))
            Jm = Jm / np.outer(sp, sp)
            aB, aJ = info(GB, ""), info(Jm, "")
            linha += " %s I_B %.2f, MOPED %.2f (%.1f%%), I_intr %.2f -> %.2f ;" % (
                nome, aB["mi"], aJ["mi"], 100 * aJ["mi"] / aB["mi"], aB["mi_intr"], aJ["mi_intr"])
            reg[nome] = dict(mi_B=aB["mi"], mi_moped=aJ["mi"], mi_intr_B=aB["mi_intr"], mi_intr_moped=aJ["mi_intr"])
        log(linha)
        res["moped"].append(reg)
    log("tempo total %.0f s" % (time.time() - T0))
    with open(os.path.join(C.RES, "exp25_compressao.json"), "w") as fh:
        json.dump(res, fh, default=float)
    with open(os.path.join(C.RES, "exp25_compressao.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
