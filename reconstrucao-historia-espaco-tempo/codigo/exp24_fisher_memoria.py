"""Experimento 24 (L05): Fisher e Cramer-Rao do sinal SO de memoria nula num detector.

Sinal: memoria nula (fluxo dos modos oscilatorios, nivel A, l = 2..8, m = 0; eletrica acumulada + magnetica
instantanea) projetada num detector, s = cos 2psi h+ + sin 2psi hx (|F| = 1), espectro exato do degrau mantido
(exp24_comum). Banda 10 Hz ate F = M f = 0.5. Parametros: (ln M, q, chi1, chi2, ln D, cos iota, t0, psi).

Testes:
  T1 serie modal esparsa contra observaveis.serie_memoria (magnetica=True);
  T2 SNR (+ e x) contra o L00 e convergencia em N (resolucao em frequencia);
  T3 dependencia do inicio da janela (f_ini) e do comprimento da janela de Tukey (dentro da banda);
  T4 derivada em ln M pela lei de escala contra diferenca finita fisica (inicio fixo em 10 Hz, interpolacao em F);
  T5 convergencia das diferencas finitas em q, chi1, chi2 (passos 4e-3, 2e-3, 1e-3).
Fisher: aLIGO, A+, ET, CE; detector unico (psi = 0) e rede de dois detectores a 45 graus (mede h+ e hx).
Autovalores branqueados pelo prior, d_ef, informacao mutua gaussiana, Cramer-Rao; Fisher reduzido aos intrinsecos.
Teste de validade (Vallisneri 2008): aproximacao de sinal linearizado nos eixos 1-sigma do posterior.
Sistema de massa baixa (M = 6, mesma q e spins; fusao acima da banda) com o mesmo tratamento.
Saidas: resultados/exp24_fisher_memoria.txt e .json; figuras/e24_fisher_memoria.png
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
NOMES = ["lnM", "q", "c1", "c2", "lnD", "cosi", "t0", "psi"]
INTR = ["lnM", "q", "c1", "c2"]


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def derivadas(E0, Efd, M, D, iota, psi, passo, f_cache=None):
    """Espectros fisicos do sinal e das derivadas (dict nome -> array) na grade nativa de E0."""
    Ms, Ds = M * MSUN_S, D * MPC_S
    k = Ms * Ms / Ds
    f = E0.F / Ms
    Y = C._Ylist(iota)
    dY = C.dY_dcos(iota)
    c2, s2 = np.cos(2 * psi), np.sin(2 * psi)

    def proj(E, Yv):
        return k * (c2 * (E.Sp_ @ Yv) + s2 * (E.Sx_ @ Yv))

    s = proj(E0, Y)
    out = {}
    Sp_iota = c2 * (E0.Sp_ @ Y) + s2 * (E0.Sx_ @ Y)
    Dp_iota = c2 * (E0.Dp_ @ Y) + s2 * (E0.Dx_ @ Y)
    out["lnM"] = k * (2 * Sp_iota + E0.F * Dp_iota)
    for nome in ("q", "c1", "c2"):
        Em, Ep = Efd[nome]
        out[nome] = (proj(Ep, Y) - proj(Em, Y)) / (2 * passo[nome])
    out["lnD"] = -s
    out["cosi"] = proj(E0, dY)
    out["t0"] = -2j * np.pi * f * s
    out["psi"] = k * (-2 * s2 * (E0.Sp_ @ Y) + 2 * c2 * (E0.Sx_ @ Y))
    return s, out, f


def fisher_de(der, w, df, nomes=NOMES):
    return C.matriz_produtos([der[n] for n in nomes], w, df)


def reduzido(G, nomes, livres):
    """Fisher dos demais parametros maximizando (perfil) sobre `livres`: complemento de Schur."""
    i = [nomes.index(n) for n in nomes if n not in livres]
    j = [nomes.index(n) for n in livres]
    A = G[np.ix_(i, i)]
    Bm = G[np.ix_(i, j)]
    Cm = G[np.ix_(j, j)]
    return A - Bm @ np.linalg.solve(Cm, Bm.T), [nomes[x] for x in i]


def resumo_fisher(G, rotulo, nomes=NOMES, intr=INTR):
    an = C.analise_fisher(G, nomes, C.SIG_PRIOR, intrinsecos=intr)
    log("  %s: autovalores branqueados = %s" % (rotulo, " ".join("%.3g" % x for x in an["lam"])))
    log("     d_ef = %.2f ; I(theta; dados) = %.1f bits ; I(intrinsecos) = %.2f bits ; cond = %.2g"
        % (an["d_ef"], an["mi"], an["mi_intr"], an["cond"]))
    log("     Cramer-Rao sem prior: " + " ".join("%s %.3g" % (n, v) for n, v in zip(nomes, an["cr"])))
    log("     posterior (com prior): " + " ".join("%s %.3g" % (n, v) for n, v in zip(nomes, an["post"])))
    log("     bits por parametro: " + " ".join("%s %.2f" % (n, v) for n, v in zip(nomes, an["mi_par"])))
    for k in range(min(4, len(nomes))):
        v = an["V"][:, k]
        ordem = np.argsort(-np.abs(v))[:4]
        log("     autovetor %d (lambda %.3g): " % (k + 1, an["lam"][k]) + " ".join("%+.2f %s" % (v[i], nomes[i]) for i in ordem))
    return an


def espectros_fd(q, c1, c2, M, f_ini, passos, N, T_tap, extra=None):
    """Espectros centrais e pares +-h para q, chi1, chi2 (mesma grade adimensional, M fixo)."""
    E0 = C.EspectroMemoria(q, c1, c2, M, f_ini, N=N, T_tap=T_tap)
    Efd = {}
    for nome in ("q", "c1", "c2"):
        par = []
        for sgn in (-1, 1):
            p = dict(q=q, c1=c1, c2=c2)
            p[nome] += sgn * passos[nome]
            par.append(C.EspectroMemoria(p["q"], p["c1"], p["c2"], M, f_ini, N=N, T_tap=T_tap))
        Efd[nome] = par
    return E0, Efd


def sinal_em(par, f, iota_ref=None, N=2 ** 19, T_tap=1500.0, f_ini=10.0):
    """Sinal fisico (detector, psi) em parametros arbitrarios, avaliado na grade f por interpolacao em F."""
    E = C.EspectroMemoria(par["q"], par["c1"], par["c2"], par["M"], f_ini, N=N, T_tap=T_tap, Fmax=0.6)
    sp = C.splines(E, par["iota"])
    return C.sinal_memoria(sp, par["M"], par["D"], par["psi"], f, t0=par.get("t0", 0.0))


def main():
    A = dict(C.SIST_A)
    M, D, iota, psi = A["M"], A["D"], A["iota"], A["psi"]
    res = {}
    log("Experimento 24: Fisher do sinal so de memoria nula. Sistema A: M=65, q=1.2, chi=(0.3,-0.2), D=400 Mpc, "
        "iota=50 graus, psi=0 (detector otimo para +), banda desde 10 Hz.")

    # ---------------- T1
    t, h, ti = O.gerar_janela(A["q"], A["c1"], A["c2"], M, 10.0)
    k, G = C.serie_modal(t, h, ti)
    ts, s = O.serie_memoria(t, h, ti, iota, 0.0, M, D, tipo="nula", magnetica=True)
    Ms, Ds = M * MSUN_S, D * MPC_S
    s2 = (G @ C._Ylist(iota)) * Ms / Ds
    log("T1 serie modal esparsa contra observaveis.serie_memoria(magnetica=True): max|dif|/max|s| = %.1e"
        % (np.max(np.abs(s2 - s[1:])) / np.max(np.abs(s))))
    del ts, s, s2, G

    # ---------------- T2
    log("T2 SNR do sinal de memoria (h+ e hx separados) e convergencia em N:")
    snr = {}
    for N in (2 ** 18, 2 ** 19, 2 ** 20):
        E = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, 10.0, N=N, t=t, h=h, t_i=ti)
        hp, hx, _, _ = E.canais(iota)
        f, sp = C.fisico(E.F, hp, M, D)
        _, sx = C.fisico(E.F, hx, M, D)
        df = f[1] - f[0]
        partes = []
        for nome in C.PSDS:
            w = C.psd_grade(nome, len(f), df)
            rp, rx = np.sqrt(C.produto(sp, sp, w, df)), np.sqrt(C.produto(sx, sx, w, df))
            partes.append("%s %.5f / %.5f" % (nome, rp, rx))
            snr[(N, nome)] = (rp, rx)
        log("  N = 2^%d (df = %.4f Hz): rho_+ / rho_x: %s" % (int(np.log2(N)), df, " ; ".join(partes)))
    log("  (L00: rho_+ nula = 0.4702 / 0.8920 / 8.6405 / 34.0901)")
    res["snr"] = {nome: snr[(2 ** 19, nome)] for nome in C.PSDS}

    # ---------------- T3
    log("T3 inicio da janela e janela de Tukey (grade fixa de A, N = 2^19): 1 - match (amplitude e tempo livres) "
        "contra (10 Hz, T_tap = 1500 M) e razao de SNR:")
    E_ref = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, 10.0, N=2 ** 19, t=t, h=h, t_i=ti)
    del t, h
    hp, hx, _, _ = E_ref.canais(iota)
    f, sref = C.fisico(E_ref.F, hp, M, D)
    df = f[1] - f[0]
    for (fi, Tt) in ((8.0, 1500.0), (12.4, 1500.0), (16.0, 1500.0), (10.0, 750.0), (10.0, 3000.0)):
        Ex = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, fi, N=2 ** 19, T_tap=Tt)
        _, sx_ = C.fisico(Ex.F, Ex.canais(iota)[0], M, D)
        partes = []
        for nome in ("aLIGO", "CE"):
            w = C.psd_grade(nome, len(f), df)
            mt, tau, aa, bb = C.match_memoria(sref, sx_, w, df, f)
            partes.append("%s 1-match %.1e, rho/rho_ref - 1 = %+.1e" % (nome, 1 - mt, np.sqrt(bb / aa) - 1))
        log("  f_ini = %5.1f Hz, T_tap = %5.0f M (%.2f s): %s" % (fi, Tt, Tt * Ms, " ; ".join(partes)))
        del Ex

    # ---------------- T4
    log("T4 derivada em ln M: lei de escala (forma adimensional fixa) contra diferenca finita fisica "
        "(inicio da janela fixo em 10 Hz; espectro de M(1+-h) interpolado em F):")
    s0, der, f = derivadas(E_ref, {"q": (E_ref, E_ref), "c1": (E_ref, E_ref), "c2": (E_ref, E_ref)}, M, D, iota, psi,
                           dict(q=1, c1=1, c2=1))
    dM_esc = der["lnM"]
    for hM in (2e-3, 1e-3):
        sm = sinal_em(dict(A, M=M * np.exp(-hM)), f)
        spl = sinal_em(dict(A, M=M * np.exp(hM)), f)
        dM_fd = (spl - sm) / (2 * hM)
        partes = []
        for nome in ("aLIGO", "ET", "CE"):
            w = C.psd_grade(nome, len(f), df)
            nn = C.produto(dM_esc, dM_esc, w, df)
            dd = C.produto(dM_fd - dM_esc, dM_fd - dM_esc, w, df)
            partes.append("%s |dif|/|d| = %.1e" % (nome, np.sqrt(dd / nn)))
        log("  h = %.0e: %s" % (hM, " ; ".join(partes)))
    # parte do inicio da janela (f_ini) na derivada fisica
    hF = 2e-3
    Eip = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, 10.0 * np.exp(hF), N=2 ** 19)
    Eim = C.EspectroMemoria(A["q"], A["c1"], A["c2"], M, 10.0 * np.exp(-hF), N=2 ** 19)
    k_ = Ms * Ms / Ds
    dfi = k_ * (Eip.canais(iota)[0] - Eim.canais(iota)[0]) / (2 * hF)
    for nome in ("aLIGO", "CE"):
        w = C.psd_grade(nome, len(f), df)
        log("  parte d s/d ln f_ini (M fixo): |.|/|d s/d ln M| = %.1e (%s)"
            % (np.sqrt(C.produto(dfi, dfi, w, df) / C.produto(dM_esc, dM_esc, w, df)), nome))
    del Eip, Eim

    # ---------------- T5 e Fisher
    log("T5 convergencia das diferencas finitas em q, chi1, chi2 (Fisher de CE, detector unico):")
    Gs = {}
    ders = {}
    for hh in (4e-3, 2e-3, 1e-3):
        passos = dict(q=hh, c1=hh, c2=hh)
        _, Efd = espectros_fd(A["q"], A["c1"], A["c2"], M, 10.0, passos, 2 ** 19, 1500.0)
        s0, der, f = derivadas(E_ref, Efd, M, D, iota, psi, passos)
        ders[hh] = der
        w = C.psd_grade("CE", len(f), df)
        Gs[hh] = fisher_de(der, w, df)
        del Efd
    for (a, b) in ((4e-3, 2e-3), (2e-3, 1e-3)):
        na = np.sqrt(np.outer(np.diag(Gs[b]), np.diag(Gs[b])))
        log("  max |G(%.0e) - G(%.0e)| / sqrt(G_ii G_jj) = %.1e" % (a, b, np.max(np.abs(Gs[a] - Gs[b]) / na)))
    # Richardson (ordem 2): D = (4 D(h/2) - D(h))/3
    der = {n: (4 * ders[1e-3][n] - ders[2e-3][n]) / 3 if n in ("q", "c1", "c2") else ders[1e-3][n] for n in NOMES}
    w = C.psd_grade("CE", len(f), df)
    GR = fisher_de(der, w, df)
    na = np.sqrt(np.outer(np.diag(GR), np.diag(GR)))
    log("  Richardson contra h = 1e-3: max relativo %.1e" % np.max(np.abs(GR - Gs[1e-3]) / na))
    lamR = np.linalg.eigvalsh(GR * np.outer([C.SIG_PRIOR[n] for n in NOMES], [C.SIG_PRIOR[n] for n in NOMES]))
    lam1 = np.linalg.eigvalsh(Gs[1e-3] * np.outer([C.SIG_PRIOR[n] for n in NOMES], [C.SIG_PRIOR[n] for n in NOMES]))
    log("  autovalores branqueados (CE): Richardson / h=1e-3 - 1: " + " ".join("%+.1e" % x for x in (lam1 / lamR - 1)))

    # ---------------- Fisher em cada detector
    log("")
    log("FISHER do sinal so de memoria nula, sistema A (D = 400 Mpc). Priors (desvio de uniforme): "
        + " ".join("%s %.3g" % (n, C.SIG_PRIOR[n]) for n in NOMES))
    res["A"] = {}
    # rede de dois detectores: o segundo mede psi + pi/4 (no psi = 0: hx)
    passos = dict(q=1e-3, c1=1e-3, c2=1e-3)
    _, Efd1 = espectros_fd(A["q"], A["c1"], A["c2"], M, 10.0, passos, 2 ** 19, 1500.0)
    passos2 = dict(q=2e-3, c1=2e-3, c2=2e-3)
    _, Efd2 = espectros_fd(A["q"], A["c1"], A["c2"], M, 10.0, passos2, 2 ** 19, 1500.0)

    def der_rich(psi_):
        _, d1, _ = derivadas(E_ref, Efd1, M, D, iota, psi_, passos)
        s_, d2, _ = derivadas(E_ref, Efd2, M, D, iota, psi_, passos2)
        return s_, {n: (4 * d1[n] - d2[n]) / 3 if n in ("q", "c1", "c2") else d1[n] for n in NOMES}

    s1, D1 = der_rich(psi)
    s2_, D2 = der_rich(psi + np.pi / 4)
    # no segundo detector, d/d psi do sinal do segundo detector e o mesmo psi (psi + pi/4 e so a orientacao)
    for nome in C.PSDS:
        w = C.psd_grade(nome, len(f), df)
        G1 = fisher_de(D1, w, df)
        G2 = fisher_de(D2, w, df)
        rho1 = np.sqrt(C.produto(s1, s1, w, df))
        rho2 = np.sqrt(C.produto(s2_, s2_, w, df))
        log("%s: detector unico rho = %.3f ; segundo detector (45 graus) rho = %.3f" % (nome, rho1, rho2))
        an1 = resumo_fisher(G1, "detector unico")
        an2 = resumo_fisher(G1 + G2, "rede (2 detectores, + e x)")
        Gr, nr = reduzido(G1, NOMES, ["lnD", "t0"])
        anr = C.analise_fisher(Gr, nr, C.SIG_PRIOR)
        Gr2, nr2 = reduzido(G1, NOMES, ["lnD", "t0", "cosi", "psi"])
        anr2 = C.analise_fisher(Gr2, nr2, C.SIG_PRIOR)
        log("     Fisher reduzido aos intrinsecos (perfil em amplitude e tempo): autovalores branqueados %s ; d_ef %.2f"
            % (" ".join("%.3g" % x for x in anr["lam"]), anr["d_ef"]))
        log("     reduzido (perfil em ln D, t0, cos iota, psi): %s ; d_ef %.2f"
            % (" ".join("%.3g" % x for x in anr2["lam"]), anr2["d_ef"]))
        for kk in range(2):
            v = anr2["V"][:, kk]
            log("        autovetor %d: " % (kk + 1) + " ".join("%+.2f %s" % (v[i], nr2[i]) for i in range(len(nr2))))
        res["A"][nome] = dict(rho=rho1, rho2=rho2, G1=G1.tolist(), G2=G2.tolist(), lam1=an1["lam"].tolist(),
                              d_ef1=an1["d_ef"], mi1=an1["mi"], mi_intr1=an1["mi_intr"], cr1=an1["cr"].tolist(),
                              post1=an1["post"].tolist(), lam_rede=an2["lam"].tolist(), d_ef_rede=an2["d_ef"],
                              mi_rede=an2["mi"], mi_intr_rede=an2["mi_intr"], post_rede=an2["post"].tolist(),
                              lam_red=anr2["lam"].tolist(), V_red=anr2["V"].tolist(), nomes_red=nr2,
                              lam_red_At=anr["lam"].tolist(), V_red_At=anr["V"].tolist(), nomes_red_At=nr)
    res["nomes"] = NOMES
    res["sig_prior"] = {n: C.SIG_PRIOR[n] for n in NOMES}

    # ---------------- Vallisneri: aproximacao de sinal linearizado
    log("")
    log("Validade (Vallisneri 2008, aproximacao de sinal linearizado): deslocamentos de 1 sigma ao longo dos eixos do "
        "posterior (Fisher + prior), detector unico. dchi2_lin = (J d|J d); dchi2 = (s(th+d)-s(th)|.); "
        "eps = (s(th+d)-s(th)-J d|.).")
    centro = dict(A)
    for nome in ("ET", "CE"):
        w = C.psd_grade(nome, len(f), df)
        G1 = np.array(res["A"][nome]["G1"])
        sp = np.array([C.SIG_PRIOR[n] for n in NOMES])
        Cw = np.linalg.inv(G1 * np.outer(sp, sp) + np.eye(len(NOMES)))
        mu, U = np.linalg.eigh(Cw)
        for kk in range(len(NOMES)):
            d = np.sqrt(mu[kk]) * U[:, kk] * sp
            # escala para ficar no dominio do modelo
            fator = 1.0
            for _ in range(30):
                p = dict(centro)
                p["M"] = M * np.exp(fator * d[0])
                p["q"] = A["q"] + fator * d[1]
                p["c1"] = A["c1"] + fator * d[2]
                p["c2"] = A["c2"] + fator * d[3]
                if 1.0 <= p["q"] <= 8 and abs(p["c1"]) <= 0.8 and abs(p["c2"]) <= 0.8:
                    break
                fator *= 0.8
            dd = fator * d
            p["D"] = D * np.exp(dd[4])
            ci = np.clip(np.cos(iota) + dd[5], -1, 1)
            p["iota"] = float(np.arccos(ci))
            p["t0"] = dd[6]
            p["psi"] = psi + dd[7]
            Jd = sum(dd[i] * D1[n] for i, n in enumerate(NOMES))
            if any(abs(dd[i]) > 0 for i in range(4)):
                sdes = sinal_em(p, f)
            else:
                sp_ = C.splines(E_ref, p["iota"])
                sdes = C.sinal_memoria(sp_, p["M"], p["D"], p["psi"], f, t0=p["t0"])
            ds = sdes - s1
            lin = C.produto(Jd, Jd, w, df)
            tru = C.produto(ds, ds, w, df)
            eps = C.produto(ds - Jd, ds - Jd, w, df)
            log("  %s eixo %d (sigma_post^2 = %.2g em unidades de prior; fator %.2f): dchi2_lin %.3f ; dchi2 %.3f ; eps %.3f"
                % (nome, kk + 1, mu[kk], fator, lin, tru, eps))
            log("      d = " + " ".join("%s %+.3g" % (n, v) for n, v in zip(NOMES, dd)))

    # ---------------- massa baixa
    log("")
    log("SISTEMA DE MASSA BAIXA: M = 6, q = 1.2, chi = (0.3, -0.2), iota = 50 graus; fusao em ~3 kHz (acima da banda). "
        "Janela desde M f0 = 0.0016 (55 Hz, ~3 s antes do pico), T_tap = 10000 M.")
    Mb = 6.0
    fib = 0.0016 / (Mb * MSUN_S)
    Nb = 2 ** 20
    Eb, Efdb = espectros_fd(A["q"], A["c1"], A["c2"], Mb, fib, passos, Nb, 10000.0)
    _, Efdb2 = espectros_fd(A["q"], A["c1"], A["c2"], Mb, fib, passos2, Nb, 10000.0)
    _, d1, fb = derivadas(Eb, Efdb, Mb, D, iota, psi, passos)
    sb, d2, _ = derivadas(Eb, Efdb2, Mb, D, iota, psi, passos2)
    Db = {n: (4 * d1[n] - d2[n]) / 3 if n in ("q", "c1", "c2") else d1[n] for n in NOMES}
    _, d1r, _ = derivadas(Eb, Efdb, Mb, D, iota, psi + np.pi / 4, passos)
    sb2, d2r, _ = derivadas(Eb, Efdb2, Mb, D, iota, psi + np.pi / 4, passos2)
    Db2 = {n: (4 * d1r[n] - d2r[n]) / 3 if n in ("q", "c1", "c2") else d1r[n] for n in NOMES}
    dfb = fb[1] - fb[0]
    # inicio da janela: comparar com inicio 1.5 vezes mais cedo
    Eb_cedo = C.EspectroMemoria(A["q"], A["c1"], A["c2"], Mb, fib * 0.86, N=Nb, T_tap=10000.0)
    _, sb_cedo = C.fisico(Eb_cedo.F, Eb_cedo.canais(iota)[0], Mb, D)
    del Eb_cedo
    res["baixa"] = {}
    for nome in C.PSDS:
        w = C.psd_grade(nome, len(fb), dfb)
        mt, _, aa, bb = C.match_memoria(sb, sb_cedo, w, dfb, fb)
        G1 = fisher_de(Db, w, dfb)
        G2 = fisher_de(Db2, w, dfb)
        rho = np.sqrt(C.produto(sb, sb, w, dfb))
        Dsc = D * rho / 34.09
        log("%s: rho(D=400) = %.3f ; inicio 1.2 x mais cedo: 1-match %.1e ; D com rho = 34.09: %.1f Mpc" % (nome, rho, 1 - mt, Dsc))
        # mesmo rho de A em CE (34.09): Fisher escalado
        an1 = resumo_fisher(G1 * (34.09 / rho) ** 2, "detector unico, escalado para rho = 34.09")
        Gr2, nr2 = reduzido(G1 * (34.09 / rho) ** 2, NOMES, ["lnD", "t0", "cosi", "psi"])
        anr2 = C.analise_fisher(Gr2, nr2, C.SIG_PRIOR)
        log("     reduzido (perfil em ln D, t0, cos iota, psi), rho = 34.09: %s ; d_ef %.2f"
            % (" ".join("%.3g" % x for x in anr2["lam"]), anr2["d_ef"]))
        for kk in range(2):
            v = anr2["V"][:, kk]
            log("        autovetor %d: " % (kk + 1) + " ".join("%+.2f %s" % (v[i], nr2[i]) for i in range(len(nr2))))
        res["baixa"][nome] = dict(rho=rho, G1=G1.tolist(), G2=G2.tolist(), lam_esc=an1["lam"].tolist(),
                                  d_ef_esc=an1["d_ef"], lam_red_esc=anr2["lam"].tolist(), V_red=anr2["V"].tolist(),
                                  nomes_red=nr2, mi_esc=an1["mi"], mi_intr_esc=an1["mi_intr"], D_rho34=Dsc)

    # ---------------- figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    C.estilo(plt)
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    for nome, cor in (("aLIGO", C.COR["laranja"]), ("ET", C.COR["verde"]), ("CE", C.COR["azul"])):
        ax[0].semilogy(np.arange(1, 9), res["A"][nome]["lam1"], "o-", color=cor, label=nome)
        ax[1].semilogy(np.arange(1, 5), res["A"][nome]["lam_red"], "o-", color=cor, label=nome)
        ax[1].semilogy(np.arange(1, 5), res["baixa"][nome]["lam_red_esc"], "s--", color=cor, alpha=0.6)
    for a in ax[:2]:
        a.axhline(1.0, color=C.COR["texto"], lw=0.8, ls=":")
    ax[0].set_xlabel("autovalor (ordem)")
    ax[0].set_ylabel("autovalor do Fisher branqueado pelo prior")
    ax[0].set_title("memória nula, 8 parâmetros (sistema A)")
    ax[0].legend(frameon=False)
    ax[1].set_xlabel("autovalor (ordem)")
    ax[1].set_title("intrínsecos, perfil em D, t0, ι, ψ\n(tracejado: M = 6, mesmo ρ = 34)")
    # espectro do sinal e derivadas whitened (CE)
    w = C.psd_grade("CE", len(f), df)
    sel = (f > 10) & (f < 1500)
    Sn = np.where(w > 0, 1 / np.where(w > 0, w, 1), np.inf)
    for n_, cor in (("lnD", C.COR["azul"]), ("lnM", C.COR["laranja"]), ("q", C.COR["verde"]), ("t0", C.COR["texto"])):
        y = 2 * np.sqrt(f[sel]) * np.abs(D1[n_][sel]) / np.sqrt(Sn[sel])
        ax[2].loglog(f[sel], y * (C.SIG_PRIOR[n_] if n_ != "t0" else 1e-3), color=cor,
                     label={"lnD": "s (= −∂/∂ln D)", "lnM": "σ_p ∂s/∂ln M", "q": "σ_p ∂s/∂q", "t0": "1 ms · ∂s/∂t0"}[n_])
    ax[2].set_xlabel("frequência (Hz)")
    ax[2].set_ylabel("2√f |s̃| / √S_n (CE)")
    ax[2].set_title("sinal e derivadas branqueados (CE)")
    ax[2].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(C.FIG, "e24_fisher_memoria.png"), dpi=150)
    log("")
    log("figura: figuras/e24_fisher_memoria.png ; tempo total %.0f s" % (time.time() - T0))
    with open(os.path.join(C.RES, "exp24_fisher_memoria.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    with open(os.path.join(C.RES, "exp24_fisher_memoria.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
