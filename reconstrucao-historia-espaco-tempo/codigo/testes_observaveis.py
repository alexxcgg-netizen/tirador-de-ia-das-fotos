"""Testes do modulo observaveis.py (agente D0, infraestrutura das linhas da etapa 7).

Sistema A do exp07: M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus, janela desde 10 Hz.
  (a) suavidade em M: M (1 + k 1e-7), k = 0..6, e M (1 + k 1e-6), k = 0..12 (atravessa degraus da escada de
      binarias, mostrada para contraste); independencia do inicio auxiliar (0.9 f0 contra 0.8 f0);
  (b) convergencia em dt (0.25, 0.125, 0.0625; derivada de 8a e de 4a ordem) e deslocamento da rede de meio passo;
  (c) desl='total', todos_m=False contra binarias.memorias_fisicas (niveis A e C);
  (d) todos_m: efeito dos m != 0 no observador (iota = 50 graus) em funcao de phi;
  (e) serie 'nula': valor final contra o deslocamento de janela (m = 0 e todos os m);
  (f) comparar2: A contra A amostrado noutra rede e deslocado por um tempo fora da grade; contraste com
      deteccao.comparar; SNR das memorias nula e 'rn' de A (aLIGO, A+, ET, CE);
  (g) refutacao de E_lig: limite de massa teste (Kerr, sympy) e energia irradiada entre 10 e 20 Hz no substituto;
      M_f contra o ajuste NRSur3dq8Remnant (surfinBH);
  (h) CM numa janela curta (50 M): com desl='janela' deve ir a ~0 (com 'total' fica -(M_f/2) h20_Favata);
  (i) origem da diferenca de M_f contra o ajuste de remanescente (modos ausentes; outro substituto, NRSur7dq4).
Saida: resultados/testes_observaveis.txt e figuras/e00_escada_suavidade.png
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import binarias as B                                   # noqa: E402
import deteccao as Dt                                  # noqa: E402
import observaveis as O                                # noqa: E402

RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
SA = dict(M=65.0, q=1.2, c1=0.3, c2=-0.2, D=400.0, iota=np.radians(50.0), F=10.0)
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def obs(mem, phi=0.0, iota=SA["iota"]):
    return O.no_observador_completo(mem, iota, phi)


def fmt(d, f="%+.2e"):
    return " ".join(("%s " + f) % (k[:4], v) for k, v in d.items())


def rel(a, b):
    return {k: a[k] / b[k] - 1 for k in O.TIPOS}


def multipolos_rel(ma, mb):
    """max |a - b| / max |b| por tipo (multipolos)."""
    out = {}
    for tipo in O.TIPOS:
        esc = max(abs(v) for v in mb[tipo].values())
        out[tipo] = max(abs(ma[tipo][k] - mb[tipo][k]) for k in mb[tipo]) / esc
    return out


def mem_A(M=SA["M"], nivel="A", **kw):
    return O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], M, SA["F"], nivel=nivel, **kw)


# ======================================================================== (a) suavidade
def teste_a():
    log("(a) Suavidade em M (memorias de janela de A no observador, iota = 50 graus, phi = 0; niveis A e C)")
    for passo, kmax in ((1e-7, 6), (1e-6, 12)):
        for nivel in ("A", "C"):
            vals = []
            for k in range(kmax + 1):
                t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"] * (1 + k * passo), SA["F"])
                m, _ = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"] * (1 + k * passo), SA["F"],
                                              nivel=nivel, t=t, h=h, t_i=ti)
                del t, h
                vals.append([obs(m)[x] for x in O.TIPOS])
            v = np.array(vals)
            r = v / v[0] - 1
            d1 = np.abs(np.diff(r, axis=0)).max(axis=0)
            d2 = np.abs(np.diff(r, 2, axis=0)).max(axis=0)
            log("  passo %.0e, k = 0..%d, nivel %s: max |1a dif.| %s" % (passo, kmax, nivel, fmt(dict(zip(O.TIPOS, d1)), "%.2e")))
            log("  %s max |2a dif.| %s" % (" " * 33, fmt(dict(zip(O.TIPOS, d2)), "%.1e")))
        if passo == 1e-6:
            vals = []
            for k in range(kmax + 1):
                m, _, t, h = B.memorias_fisicas(SA["q"], SA["c1"], SA["c2"], SA["M"] * (1 + k * passo), SA["F"])
                del t, h
                vals.append([B.no_observador(m, SA["iota"])[x] for x in O.TIPOS])
            v = np.array(vals)
            r = v / v[0] - 1
            d2 = np.abs(np.diff(r, 2, axis=0)).max(axis=0)
            log("  contraste binarias.memorias_fisicas (nivel A), passo 1e-6: max |2a dif.| %s"
                % fmt(dict(zip(O.TIPOS, d2)), "%.1e"))
    # todos os m (dependem da fase orbital zerada em t_i): observador phi = 0.8 rad
    vals = []
    for k in range(13):
        m, _ = mem_A(M=SA["M"] * (1 + k * 1e-6), todos_m=True)
        vals.append([obs(m, 0.8)[x] for x in O.TIPOS])
    v = np.array(vals)
    r = v / v[0] - 1
    d2 = np.abs(np.diff(r, 2, axis=0)).max(axis=0)
    log("  todos os m (phi = 0.8 rad), nivel A, passo 1e-6, k = 0..12: max |2a dif.| %s" % fmt(dict(zip(O.TIPOS, d2)), "%.1e"))
    # independencia do inicio auxiliar
    m1, a1 = mem_A(todos_m=True)
    O.FRAC_INICIO = 0.8
    m2, a2 = mem_A(todos_m=True)
    O.FRAC_INICIO = 0.9
    log("  inicio auxiliar 0.8 f0 contra 0.9 f0 (todos os m): max dif. relativa dos multipolos %s ; t_i %.3e M"
        % (fmt(multipolos_rel(m2, m1), "%.1e"), a2["t_i"] - a1["t_i"]))
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== figura da escada
def figura_escada():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    es = np.linspace(0, 1.2e-5, 25)
    sb, so = [], []
    for e in es:
        m, _, t, h = B.memorias_fisicas(SA["q"], SA["c1"], SA["c2"], SA["M"] * (1 + e), SA["F"])
        del t, h
        sb.append(B.no_observador(m, SA["iota"])["spin"])
        m, _ = mem_A(M=SA["M"] * (1 + e))
        so.append(obs(m)["spin"])
    sb, so = np.array(sb), np.array(so)
    fig, ax = plt.subplots(figsize=(7.0, 4.2), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.grid(color="#e6e5e0", lw=0.8)
    ax.plot(es * 1e6, (sb / so[0] - 1) * 1e6, "o-", color="#eb6834", ms=4, label="binarias (inicio no 1o ponto da grade)")
    ax.plot(es * 1e6, (so / so[0] - 1) * 1e6, "s-", color="#2a78d6", ms=4, label="observaveis (t_i exato, peso parcial)")
    ax.set_xlabel(r"$\Delta M / M$ ($10^{-6}$)", color="#52514e")
    ax.set_ylabel(r"memoria de spin no observador: variacao relativa ($10^{-6}$)", color="#52514e")
    ax.set_title("Sistema A, janela desde 10 Hz, nivel A", color="#52514e")
    ax.tick_params(colors="#52514e")
    ax.legend(frameon=False, labelcolor="#52514e")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "e00_escada_suavidade.png"), dpi=130, facecolor="#fcfcfb")
    plt.close(fig)
    log("  figura e00_escada_suavidade.png: binarias salta %.2e (max-min %.2e) ; observaveis varia linearmente %.2e"
        % (np.max(np.abs(np.diff(sb / so[0]))), np.ptp(sb / so[0]), np.ptp(so / so[0])))


# ======================================================================== (b) convergencia em dt
def teste_b():
    log("")
    log("(b) Convergencia em dt (memorias de janela de A, nivel A, todos os m guardados; observador phi = 0 e multipolos)")
    ref = {}
    for ordem in (8, 4):
        res = {}
        for dt in (0.25, 0.125, 0.0625):
            t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], dt=dt)
            res[dt] = mem_A(t=t, h=h, t_i=ti, dt=dt, todos_m=True, ordem_deriv=ordem)[0]
            del t, h
        ref[ordem] = res
        for dt in (0.25, 0.125):
            log("  derivada ordem %d: dt %.4f contra 0.0625: observador %s" % (ordem, dt, fmt(rel(obs(res[dt]), obs(res[0.0625])))))
            log("  %s multipolos %s" % (" " * 36, fmt(multipolos_rel(res[dt], res[0.0625]), "%.1e")))
    log("  ordem 8 contra ordem 4 em dt 0.0625: %s" % fmt(rel(obs(ref[8][0.0625]), obs(ref[4][0.0625]))))
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], dt=0.25, t_desloc=0.5)
    m, _ = mem_A(t=t, h=h, t_i=ti, todos_m=True)
    del t, h
    log("  rede deslocada de meio passo (dt 0.25, t_desloc 0.5) contra a rede padrao: observador %s"
        % fmt(rel(obs(m), obs(ref[8][0.25]))))
    log("  %s multipolos %s" % (" " * 59, fmt(multipolos_rel(m, ref[8][0.25]), "%.1e")))
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (c) contra binarias
def teste_c():
    log("")
    log("(c) desl='total', todos_m=False contra binarias.memorias_fisicas (A desde 10 Hz)")
    for nivel in ("A", "C"):
        mb, ab, tb, hb = B.memorias_fisicas(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel=nivel)
        t0b = tb[0]
        del tb, hb
        t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
        for rot, kw in (("deriv. 4a ordem, E_lig 1PN (mesmas formulas)", dict(ordem_deriv=4, ordem_elig=1)),
                        ("padrao (deriv. 8a ordem, E_lig 3PN+SO)", {})):
            mo, ao = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel=nivel, desl="total",
                                            t=t, h=h, t_i=ti, **kw)
            log("  nivel %s, %s: observador %s" % (nivel, rot, fmt(rel(B.no_observador(mo, SA["iota"]),
                                                                    B.no_observador(mb, SA["iota"])))))
            log("  %s multipolos %s ; M_f %+.2e" % (" " * (10 + len(rot)), fmt(multipolos_rel(mo, mb), "%.1e"),
                                                    ao["M_f"] - ab["M_f"]))
        log("  (inicio da janela: binarias t0 = %.4f M com regra do retangulo, ~ t0 - dt/2 = %.4f ; observaveis t_i = %.4f M)"
            % (t0b, t0b - 0.125, ti))
        del t, h
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (d) m != 0
def teste_d():
    log("")
    log("(d) Multipolos m != 0 no observador (iota = 50 graus): (todos os m)/(so m = 0) - 1 ao longo de phi (24 valores)")
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    phis = np.linspace(0, 2 * np.pi, 25)[:-1]
    for desl in ("janela", "total"):
        m, _ = mem_A(t=t, h=h, t_i=ti, todos_m=True, desl=desl)
        m0 = {tp: {k: v for k, v in m[tp].items() if k[1] == 0} for tp in O.TIPOS}
        base = obs(m0)
        R = np.array([[obs(m, ph)[tp] / base[tp] - 1 for tp in O.TIPOS] for ph in phis])
        log("  desl='%s': %s" % (desl, " ".join("%s [%+.2e, %+.2e]" % (tp[:4], R[:, i].min(), R[:, i].max())
                                                 for i, tp in enumerate(O.TIPOS))))
        if desl == "janela":
            for tp in O.TIPOS:
                maior = max(((k, abs(v)) for k, v in m[tp].items() if k[1] != 0), key=lambda kv: kv[1])
                mm0 = max(abs(v) for k, v in m[tp].items() if k[1] == 0)
                log("    %-13s maior multipolo m != 0: %s |.| = %.2e ; maior m = 0: %.2e" % (tp, maior[0], maior[1], mm0))
            iA = int(np.argmax(np.abs(R[:, 1])))
            log("    phi do maior efeito no spin: %.0f graus" % np.degrees(phis[iA]))
    mC, _ = mem_A(nivel="C", t=t, h=h, t_i=ti, todos_m=True)
    m0 = {tp: {k: v for k, v in mC[tp].items() if k[1] == 0} for tp in O.TIPOS}
    base = obs(m0)
    R = np.array([[obs(mC, ph)[tp] / base[tp] - 1 for tp in O.TIPOS] for ph in phis])
    log("  nivel C, desl='janela': %s" % " ".join("%s [%+.2e, %+.2e]" % (tp[:4], R[:, i].min(), R[:, i].max())
                                                for i, tp in enumerate(O.TIPOS)))
    del t, h
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (e) serie nula
def teste_e():
    log("")
    log("(e) Serie 'nula': valor final (Re = Delta h_+) contra o deslocamento de janela de memorias_observaveis")
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    for todos, phi in ((False, 0.0), (True, 0.7), (True, 2.9)):
        m, _ = mem_A(t=t, h=h, t_i=ti, todos_m=todos)
        alvo = O.valores_fisicos_completo(m, SA["iota"], phi, SA["M"], SA["D"])["deslocamento"]
        ts, s = O.serie_memoria(t, h, ti, SA["iota"], phi, SA["M"], SA["D"], tipo="nula", todos_m=todos)
        log("  todos_m=%s, phi = %.1f: Re s(fim) = %.10e ; deslocamento = %.10e ; dif. relativa %.1e ; s(t_i) = %.1e ; "
            "max|Im s|/|Re s(fim)| = %.1e" % (todos, phi, s[-1].real, alvo, s[-1].real / alvo - 1, abs(s[0]),
                                              np.max(np.abs(s.imag)) / abs(s[-1].real)))
    ts, s = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="nula", magnetica=True)
    m, _ = mem_A(t=t, h=h, t_i=ti)
    sp = O.valores_fisicos_completo(m, SA["iota"], 0.0, SA["M"], SA["D"])["spin"]
    integ = -np.trapezoid(s.imag, ts)          # int h_x du = -int Im(h_+ - i h_x) du
    log("  magnetica=True: int h_x dt (trapezio da serie) = %.6e s ; memoria de spin (janela) = %.6e s ; dif. %.1e"
        % (integ, sp, integ / sp - 1))
    tr, sr = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="rn")
    mC, _ = mem_A(nivel="C", t=t, h=h, t_i=ti)
    alvoC = O.valores_fisicos_completo(mC, SA["iota"], 0.0, SA["M"], SA["D"])["deslocamento"]
    mC24 = {tp: ({k: mC[tp][k] for k in ((2, 0), (4, 0))} if tp == "deslocamento" else mC[tp]) for tp in O.TIPOS}
    alvo24 = O.valores_fisicos_completo(mC24, SA["iota"], 0.0, SA["M"], SA["D"])["deslocamento"]
    log("  tipo 'rn': Re s(fim) = %.10e ; deslocamento de janela nivel C so l = 2, 4 = %.10e (dif. %.1e) ; com l = 6, 8"
        " do fluxo = %.6e (dif. %.1e)" % (sr[-1].real, alvo24, sr[-1].real / alvo24 - 1, alvoC, sr[-1].real / alvoC - 1))
    del t, h
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (f) comparar2 e SNR
def _strain(t, h, ti):
    """h_+ - i h_x no observador (todos os modos), em unidades fisicas, desde t_i (primeiro ponto em t_i, spline)."""
    from scipy.interpolate import CubicSpline
    lista = sorted(h.keys())
    ts, s = Dt.strain_observador(t, h, lista, SA["M"], SA["D"], SA["iota"], 0.0)
    k = int(np.searchsorted(t, ti))
    j = np.arange(k - 4, k + 4)
    v0 = CubicSpline(t[j], s[j].real)(ti) + 1j * CubicSpline(t[j], s[j].imag)(ti)
    Ms = SA["M"] * Dt.MSUN_S
    return np.concatenate([[ti * Ms], ts[k:]]), np.concatenate([[v0], s[k:]])


def teste_f():
    log("")
    log("(f) comparar2: A (rede padrao) contra A amostrado na rede deslocada de 0.37 dt e com os tempos somados de"
        " tau = 1.2345678e-3 s (todos os modos, observador iota = 50 graus, phi = 0, aLIGO, f_min 10 Hz)")
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    tA, sA = _strain(t, h, ti)
    del t, h
    t, h, ti2 = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], t_desloc=0.37)
    tB, sB = _strain(t, h, ti2)
    del t, h
    tB = tB + 1.2345678e-3
    log("  t_i das duas redes: %.6f e %.6f M (dif. %.1e M)" % (ti, ti2, ti2 - ti))
    c = O.comparar2(tA, sA, tB, sB, "aLIGO", 10.0)
    log("  comparar2: 1 - match = %.2e ; SNR_A %.4f SNR_B %.4f ; rho_crit %.3g ; atraso %.3e s" % (
        1 - c["match"], c["snr_A"], c["snr_B"], c["rho_crit"], c["atraso"]))
    dt = 1 / 4096.0
    a = O.preparar(tA, sA)
    b = O.preparar(tB, sB)
    for up, ref in ((1, False), (16, False), (16, True)):
        _, _, mt, _ = O.produto2(a, b, dt, "aLIGO", 10.0, up=up, refinar=ref)
        log("    variante: up = %2d, refino continuo %-5s: 1 - match = %.2e" % (up, ref, 1 - mt))
    log("  (as duas series comecam no mesmo instante fisico t_i, entao a reamostragem em 1/fs cai nos mesmos instantes:"
        " este caso testa a reamostragem por spline, nao a busca no tempo)")
    c0 = O.comparar2(tA, sA, tA + 1.2345678e-3, sA, "aLIGO", 10.0)
    log("  mesma amostragem, so os tempos somados de tau: 1 - match = %.2e" % (1 - c0["match"]))
    cd = Dt.comparar(tA, sA, tB, sB, "aLIGO", 10.0)
    log("  deteccao.comparar no mesmo par: 1 - match = %.2e (h_+)" % (1 - cd["+"]["match"]))
    # atraso sub-amostra de verdade: g(t) = w(t - t_i) s(t) (janela de Tukey de 0.5 s ja aplicada), A = g nos
    # instantes t_i + j/fs, B = g(t - eps) nos mesmos instantes (eps fora da grade 1/fs e da rede do substituto)
    from scipy.interpolate import CubicSpline
    fs = 4096.0
    tg = tA[0] + np.arange(int((tA[-1] - tA[0]) * fs)) / fs        # ate o fim do substituto (135 M apos o pico)
    csr, csi = CubicSpline(tA, sA.real), CubicSpline(tA, sA.imag)

    def g(tt):
        u = np.clip((tt - tA[0]) / 0.5, 0, 1)
        w = 0.5 * (1 - np.cos(np.pi * u))
        tt = np.clip(tt, tA[0], tA[-1])
        return w * (csr(tt) + 1j * csi(tt))

    for eps in (0.37 / fs, 1.2345678e-3, 5.3e-5):
        ga, gb = g(tg), g(tg - eps)
        a = O.preparar(tg, ga, taper=0.0)
        b = O.preparar(tg, gb, taper=0.0)
        txt = []
        for up, ref in ((1, False), (16, False), (16, True)):
            _, _, mt, tau = O.produto2(a, b, 1 / fs, "aLIGO", 10.0, up=up, refinar=ref)
            txt.append("up %2d refino %-5s 1-match %.2e (atraso %.4e s)" % (up, ref, 1 - mt, tau))
        cdd = Dt.comparar(tg, ga, tg, gb, "aLIGO", 10.0)
        log("  atraso eps = %.4e s: %s ; deteccao.comparar %.2e" % (eps, " | ".join(txt), 1 - cdd["+"]["match"]))
    del tA, sA, tB, sB
    # contraste com dois sistemas diferentes: o piso artificial de deteccao.comparar (item 13 da revisao)
    t, h, ti = O.gerar_janela(1.19, SA["c1"], SA["c2"], SA["M"], SA["F"])
    tC, sC = _strain(t, h, ti)
    del t, h
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    tA, sA = _strain(t, h, ti)
    del t, h
    c2 = O.comparar2(tA, sA, tC, sC, "aLIGO", 10.0)
    cd = Dt.comparar(tA, sA, tC, sC, "aLIGO", 10.0)
    cn = O.comparar2(tA, sA, tC, sC, "aLIGO", 10.0, fim="nada", taper=0.0)
    log("  A contra q = 1.19 (demais parametros iguais), aLIGO: comparar2 1-match %.3e (rho_crit %.1f) ; sem taper e sem"
        " rampa %.3e ; deteccao.comparar %.3e" % (1 - c2["match"], c2["rho_crit"], 1 - cn["match"], 1 - cd["+"]["match"]))
    del tA, sA, tC, sC
    log("  SNR das memorias de A (h_+, D = 400 Mpc, iota = 50 graus, f_min 10 Hz):")
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    tn, sn = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="nula")
    tr, sr = O.serie_memoria(t, h, ti, SA["iota"], 0.0, SA["M"], SA["D"], tipo="rn")
    del t, h
    ref_n = {"aLIGO": 0.470, "A+": 0.892, "ET": 8.642, "CE": 34.096}         # rev_R5_snr_memoria_qnm.txt, 'A'
    ref_r = {"aLIGO": 0.759, "A+": 1.444, "ET": 10.686, "CE": 39.103}       # rev_R5 / exp15, 'C'
    for psd in ("aLIGO", "A+", "ET", "CE"):
        r_n = O.snr2(tn, sn, psd, 10.0)
        r_r = O.snr2(tr, sr, psd, 10.0)
        r_n0 = O.snr2(tn, sn, psd, 10.0, taper=0.0)
        log("    %-5s: nula %.3f (rev_R5 %.3f ; sem taper %.3f) ; rn %.3f (exp15 %.3f)" % (
            psd, r_n, ref_n[psd], r_n0, r_r, ref_r[psd]))
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (g) E_lig
def teste_g():
    log("")
    log("(g) Refutacao de E_lig e M_f")
    import sympy as sp
    w_, a = sp.symbols("w a", positive=True)
    # Kerr: E/mu = (1 - 2u^2 + a u^3)/sqrt(1 - 3u^2 + 2a u^3) com u = sqrt(M/r_BL); M Omega = u^3/(1 + a u^3), entao
    # u = v (1 - a v^3)^(-1/3) com v = (M Omega)^(1/3) = sqrt(x)
    u = w_ * (1 - a * w_ ** 3) ** sp.Rational(-1, 3)
    Ek = (1 - 2 * u ** 2 + a * u ** 3) / sp.sqrt(1 - 3 * u ** 2 + 2 * a * u ** 3) - 1
    ser = sp.series(Ek, w_, 0, 10).removeO()
    v = w_
    # limite de massa teste da formula: q -> infinito, eta -> 0, m1 -> 1, S = chi1, Sig = -chi1, d = 1
    pn = -(v ** 2 / 2) * (1 - sp.Rational(3, 4) * v ** 2 - sp.Rational(27, 8) * v ** 4 - sp.Rational(675, 64) * v ** 6
                          + (sp.Rational(14, 3) - 2) * a * v ** 3 + (11 - 3) * a * v ** 5
                          + (sp.Rational(135, 4) - sp.Rational(27, 4)) * a * v ** 7)
    dif = sp.expand(ser - pn)
    lin = [sp.nsimplify(sp.expand(dif).coeff(a, 0).coeff(v, n)) for n in range(2, 10)]
    um = [sp.nsimplify(sp.expand(dif).coeff(a, 1).coeff(v, n)) for n in range(2, 10)]
    log("  limite de massa teste (Kerr equatorial, E/mu): Kerr - formula, coeficientes de v^2..v^9 em a^0: %s ; em a^1: %s"
        % (lin, um))
    # energia irradiada entre 10 e 20 Hz (substituto) contra E_lig(x20) - E_lig(x10)
    for (c1, c2) in ((0.0, 0.0), (0.5, 0.5), (-0.5, -0.5), (0.3, -0.2)):
        for q in (1.2, 4.0):
            t, h, ti = O.gerar_janela(q, c1, c2, SA["M"], 10.0)
            _, a10 = O.memorias_observaveis(q, c1, c2, SA["M"], 10.0, t=t, h=h, t_i=ti)
            ti20 = O.instante_frequencia(t, h[(2, 2)], SA["M"] * Dt.MSUN_S * 20.0)[0]
            _, a20 = O.memorias_observaveis(q, c1, c2, SA["M"], 20.0, t=t, h=h, t_i=ti20)
            del t, h
            dE = a10["E_janela"] - a20["E_janela"]
            x10, x20 = a10["x_i"], a20["x_i"]
            e1 = O.e_lig(x20, q, c1, c2, 1) - O.e_lig(x10, q, c1, c2, 1)
            e3 = O.e_lig(x20, q, c1, c2, 3) - O.e_lig(x10, q, c1, c2, 3)
            e3s = O.e_lig(x20, q, 0.0, 0.0, 3) - O.e_lig(x10, q, 0.0, 0.0, 3)
            log("  q %.1f chi (%+.1f, %+.1f): E_rad(10->20 Hz) substituto %.6e ; PN-substituto: 1PN %+.2e ; 3PN+SO %+.2e ;"
                " 3PN sem SO %+.2e" % (q, c1, c2, dE, e1 - dE, e3 - dE, e3s - dE))
    # M_f contra o ajuste de remanescente
    import surfinBH
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    for (q, c1, c2) in ((1.2, 0.3, -0.2), (1.0, 0.0, 0.0), (4.0, 0.5, 0.0), (2.0, -0.5, 0.5)):
        mf, mf_err = fit.mf(q, [0, 0, c1], [0, 0, c2])
        _, aux = O.memorias_observaveis(q, c1, c2, SA["M"], 10.0)
        _, aux1 = O.memorias_observaveis(q, c1, c2, SA["M"], 10.0, ordem_elig=1)
        log("  q %.1f chi (%+.1f, %+.1f): M_f observaveis %.6f (com E_lig 1PN %.6f) ; NRSur3dq8Remnant %.6f +- %.1e ;"
            " dif. %+.1e" % (q, c1, c2, aux["M_f"], aux1["M_f"], mf, mf_err, aux["M_f"] - mf))
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (h) CM em janela curta
def teste_h():
    log("")
    log("(h) Memoria de CM (2,0) numa janela curta (50 M desde t_i), A, q = 1, chi = 0, f_ini 10 Hz, M = 65")
    t, h, ti = O.gerar_janela(1.0, 0.0, 0.0, SA["M"], 10.0)
    n = int(np.searchsorted(t, ti + 50.0))
    tc, hc = t[:n], {k: v[:n] for k, v in h.items()}
    del t, h
    for desl in ("janela", "total"):
        m, aux = O.memorias_observaveis(1.0, 0.0, 0.0, SA["M"], 10.0, desl=desl, t=tc, h=hc, t_i=ti)
        log("  desl='%s': desl20 = %+.3e ; cm20 = %+.3e" % (desl, m["deslocamento"][(2, 0)].real, m["cm"][(2, 0)].real))
    log("  -(M_f/2) h20_Favata(x_i) = %+.3e" % (-0.5 * aux["M_f"] * B.favata_h20(aux["x_i"], 0.25)))
    mJ, _ = O.memorias_observaveis(1.0, 0.0, 0.0, SA["M"], 10.0, desl="janela")
    mT, _ = O.memorias_observaveis(1.0, 0.0, 0.0, SA["M"], 10.0, desl="total")
    log("  janela completa: cm20 'janela' = %+.5f ; 'total' = %+.5f ; fracao de cm20 'total' vinda de antes da janela %.1f%%"
        % (mJ["cm"][(2, 0)].real, mT["cm"][(2, 0)].real, 100 * (1 - mJ["cm"][(2, 0)].real / mT["cm"][(2, 0)].real)))
    log("  (%.0f s)" % (time.time() - T0))


# ======================================================================== (i) origem da diferenca de M_f
def teste_i():
    log("")
    log("(i) Origem da diferenca M_f(observaveis) - NRSur3dq8Remnant ~ +5.5e-5: modos ausentes do substituto CCE e"
        " energia irradiada de outro substituto (NRSur7dq4, todos os modos l <= 4) na mesma janela f_22 >= 0.0055/M")
    import gwsurrogate
    import surfinBH
    s7 = gwsurrogate.LoadSurrogate("NRSur7dq4")
    fit3 = surfinBH.LoadFits("NRSur3dq8Remnant")
    fit7 = surfinBH.LoadFits("NRSur7dq4Remnant")
    cce = set(B.lista_osc()) | set(B.MODOS_M0)
    f0 = 0.0055
    for (q, c1, c2) in ((1.2, 0.3, -0.2), (1.0, 0.0, 0.0), (2.0, -0.5, 0.5)):
        t7, h7, _ = s7(q, [0, 0, c1], [0, 0, c2], dt=0.25, f_low=0)
        ti7 = O.instante_frequencia(t7, h7[(2, 2)], f0)[0]
        w = O.pesos_janela(t7, ti7)
        Em = {k: float(np.sum(w * np.abs(O.derivada(v[:, None], 0.25)[:, 0]) ** 2) / (16 * np.pi)) for k, v in h7.items()}
        del t7, h7
        E7 = sum(Em.values())
        falta = sum(v for k, v in Em.items() if k not in cce)
        Mfic = f0 / (Dt.MSUN_S * 10.0)                     # massa ficticia: f_ini = 10 Hz corresponde a M f = f0
        _, aux = O.memorias_observaveis(q, c1, c2, Mfic, 10.0)
        El = O.e_lig(aux["x_i"], q, c1, c2, 3)
        mf3, e3 = fit3.mf(q, [0, 0, c1], [0, 0, c2])
        mf7, e7 = fit7.mf(q, [0, 0, c1], [0, 0, c2])
        log("  q %.1f chi (%+.1f, %+.1f): E_janela CCE %.6f ; NRSur7dq4 %.6f (dif. %+.1e) ; energia nos modos l <= 4 ausentes do"
            " CCE (NRSur7dq4) %.1e" % (q, c1, c2, aux["E_janela"], E7, aux["E_janela"] - E7, falta))
        log("      1 - E_lig - E_janela: CCE %.6f ; NRSur7dq4 %.6f ; ajustes: NRSur3dq8Remnant %.6f +- %.1e ; NRSur7dq4Remnant"
            " %.6f +- %.1e" % (1 - El - aux["E_janela"], 1 - El - E7, mf3, e3, mf7, e7))
    log("  (%.0f s)" % (time.time() - T0))


if __name__ == "__main__":
    so = sys.argv[1:] or ["a", "fig", "b", "c", "d", "e", "f", "g", "h", "i"]
    log("Testes de observaveis.py ; sistema A: M = 65, q = 1.2, chi = (+0.3, -0.2), D = 400 Mpc, iota = 50 graus, 10 Hz")
    for nome in so:
        {"a": teste_a, "fig": figura_escada, "b": teste_b, "c": teste_c, "d": teste_d, "e": teste_e,
         "f": teste_f, "g": teste_g, "h": teste_h, "i": teste_i}[nome]()
    if not sys.argv[1:]:                     # so a execucao completa grava o arquivo de resultados
        with open(os.path.join(RES, "testes_observaveis.txt"), "w") as fh:
            fh.write("\n".join(linhas) + "\n")
