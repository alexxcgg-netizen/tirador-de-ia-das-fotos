"""L03, tarefa 1: memorias de banda como diferencas de E_b(f) e de J(f), ordem por ordem PN, contra o substituto.

Partes (saida resultados/exp20_pn.txt e .json; figura figuras/e20_bandas_pn.png):
 (a) conferencias: formula de Gaunt contra quadratura; alpha_L(x) = taxa de memoria / fluxo de energia pelas
     amplitudes ABFO contra a razao dU_20/dt / F de Cunningham et al. (1PN e 1.5PN SO); integral de dU20/dt / xdot
     contra H_20 (Cunningham); primeira lei J(x) contra Blanchet LRR eq. (Jcirc) (sem spin, 3PN); cancelamento da cauda.
 (b) series das razoes: alpha_2, alpha_4 (deslocamento), beta_3 (spin), giroscopica l=1, 3, CM l=2 (parte nula), com
     todos os modos ABFO (l <= 4) e so com os modos do substituto (sem (3,1), (4,2), (4,1)).
 (c) primeira lei modo a modo no substituto: (dE_lm/dt)/(dJ_lm/dt) = (omega_lm/m)(1 + (Adot/(A omega))^2) e a razao
     total dE/dJ contra Omega = omega_22/2 ao longo da onda (sistema A).
 (d) memorias de banda do substituto (nivel A, deslocamento de janela, multipolos m = 0) contra a previsao PN ordem
     por ordem, para 5 sistemas e bandas em M f de 0.002 a 0.014.
"""
import json
import os
import time

import numpy as np
import sympy as sp
from scipy.integrate import quad

import binarias as B
import exp20_comum as C
import exp20_pn_comum as P
import observaveis as O
from deteccao import MSUN_S
from harmonicos import sYlm, Dfrak

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
linhas = []
OUT = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


MODOS_SUR = tuple(k for k in P.MODOS_ABFO if k not in ((3, 1), (4, 2), (4, 1)))
SISTEMAS = [("q1", 1.0, 0.0, 0.0), ("A", 1.2, 0.3, -0.2), ("q3s", 3.0, 0.6, 0.0), ("q4a", 4.0, -0.5, -0.5),
            ("q2s", 2.0, 0.5, 0.5)]
BORDAS = [0.002, 0.003, 0.004, 0.006, 0.008, 0.010, 0.012, 0.014]       # M f (frequencia de onda)
ORDENS = [0, 2, 3, 4, 5, 6, 7]                                          # potencia de v nas chaves
NOME_ORD = {0: "N", 2: "1PN", 3: "1.5PN", 4: "2PN", 5: "2.5PN", 6: "3PN", 7: "3.5PN"}


def coef_float(e, k):
    return sp.expand(e).coeff(P.v, k)


def so_coefs(c3):
    """Coeficientes (a_s, a_dsig) de c3 = a_s s + a_dsig delta sigma, avaliados em dois deltas (confere a forma)."""
    out = []
    for d in (0.37, 0.81):
        a = float(sp.re(sp.N(c3.subs({P.s: 1, P.sigma: 0, P.delta: d}))))
        b = float(sp.re(sp.N(c3.subs({P.s: 0, P.sigma: 1, P.delta: d})))) / d
        out.append((a, b))
    if abs(out[0][0] - out[1][0]) > 1e-9 or abs(out[0][1] - out[1][1]) > 1e-9:
        return out[0][0], out[0][1], "(AVISO: nao e da forma a s + b delta sigma)"
    return out[0][0], out[0][1], ""


def racional(c, tol=1e-9):
    try:
        return sp.nsimplify(sp.N(c, 20), tolerance=tol, rational=True)
    except Exception:
        return c


# ------------------------------------------------------------------ (a)
def parte_a():
    log("(a) CONFERENCIAS")
    # Gaunt contra quadratura
    th = np.linspace(0, np.pi, 4001)
    pior = 0.0
    for (la, lb, m, L) in [(2, 2, 2, 2), (2, 3, 2, 2), (2, 4, 2, 2), (3, 3, 3, 4), (2, 3, 1, 2), (3, 4, 3, 4), (2, 2, 1, 4)]:
        f = np.array([complex(sYlm(-2, la, m, t, 0.0)) * np.conj(complex(sYlm(-2, lb, m, t, 0.0)))
                      * complex(sYlm(0, L, 0, t, 0.0)) for t in th])
        num = 2 * np.pi * np.trapezoid(f * np.sin(th), th)
        g = complex(sp.N(P.gaunt(la, lb, m, L)))
        pior = max(pior, abs(num - g))
    log("  Gaunt (3j) contra quadratura com harmonicos.sYlm, 7 casos: max |dif| = %.1e" % pior)
    # alpha_2 exato (Gaunt) com todos os modos ABFO
    a2 = P.alpha_desl(2, P.MODOS_ABFO, 3)
    a0 = sp.nsimplify(coef_float(a2, 0))
    log("  alpha_2 (todos os modos ABFO, l<=4): alpha_0 = %s = %.10f ; Favata (8/7)sqrt(5 pi/6) = %.10f"
        % (a0, float(a0), float(sp.Rational(8, 7) * sp.sqrt(5 * sp.pi / 6))))
    c2 = sp.expand(sp.simplify(coef_float(a2, 2) / a0).subs(P.delta ** 2, 1 - 4 * P.nu))
    c3 = sp.expand(sp.cancel(P.em_s_sigma(sp.simplify(coef_float(a2, 3) / a0))))
    a_s, a_ds, av = so_coefs(c3)
    log("    a_1PN = %.12f + %.12f nu ; a_1.5PN = %.12f s + %.12f delta sigma %s; a_0.5PN = %s"
        % (float(c2.subs(P.nu, 0)), float(sp.diff(c2, P.nu)), a_s, a_ds, av, coef_float(a2, 1)))
    log("    (Cunningham: -1051/2016 = %.12f, 71/24 = %.12f ; 5/3 = %.12f, 99/64 = %.12f)"
        % (-1051 / 2016, 71 / 24, 5 / 3, 99 / 64))
    # Cunningham: dU20/dt / F
    U = P.expr("U20dot")
    F = P.expr("F")
    r = sp.series(sp.expand((U / F).subs(P.x, P.v ** 2) / (U / F).subs(P.x, P.v ** 2).subs(P.v, 0)
                            if False else (U / F).subs(P.x, P.v ** 2)), P.v, 0, 4).removeO()
    r0 = coef_float(r, 0)
    log("    Cunningham et al. (dU20/dt)/F: 1PN %s ; 1.5PN %s (o 4 pi da cauda aparece em dU20/dt e em F e cancela)"
        % (sp.nsimplify(sp.expand(coef_float(r, 2) / r0)), sp.nsimplify(sp.expand(coef_float(r, 3) / r0))))
    OUT["alpha2"] = dict(a0=str(a0), a1PN=str(c2), a15PN=str(c3))
    # alpha_4
    a4 = P.alpha_desl(4, P.MODOS_ABFO, 3)
    a40 = sp.nsimplify(coef_float(a4, 0))
    c42 = sp.expand(sp.simplify(coef_float(a4, 2) / a40).subs(P.delta ** 2, 1 - 4 * P.nu))
    c43 = sp.expand(sp.cancel(P.em_s_sigma(sp.simplify(coef_float(a4, 3) / a40))))
    U4 = P.expr("U40dot")
    r4 = sp.series((U4 / F).subs(P.x, P.v ** 2), P.v, 0, 4).removeO()
    a_s, a_ds, av = so_coefs(c43)
    log("  alpha_4: alpha_0 = %s ; a_1PN = %.10f + %.10f nu ; a_1.5PN = %.10f s + %.10f delta sigma %s"
        % (a40, float(c42.subs(P.nu, 0)), float(sp.diff(c42, P.nu)), a_s, a_ds, av))
    log("    (Cunningham: -157925/14784 = %.10f, 9105/176 = %.10f ; 40/3, 205/16 = %.10f, %.10f)"
        % (-157925 / 14784, 9105 / 176, 40 / 3, 205 / 16))
    log("    Cunningham (dU40/dt)/F: 1PN %s ; 1.5PN %s"
        % (sp.nsimplify(sp.expand(coef_float(r4, 2) / coef_float(r4, 0))),
           sp.nsimplify(sp.expand(coef_float(r4, 3) / coef_float(r4, 0)))))
    # beta_3 pela taxa conhecida: dS30/du = |h30| (modo magnetico nao oscilatorio), Blanchet LRR 2024 eq. (H30, sem spin):
    # H30 = -(2/5) i sqrt(6/7) nu [x^{5/2} + x^{7/2}(-5017/1296 - 25/108 nu)], h = 2 nu x sqrt(16 pi/5) H; J flux = F/Omega
    H30 = sp.Rational(2, 5) * sp.sqrt(sp.Rational(6, 7)) * P.nu * (P.x ** sp.Rational(5, 2) + P.x ** sp.Rational(7, 2)
                                                                   * (-sp.Rational(5017, 1296) - sp.Rational(25, 108) * P.nu))
    taxa = 2 * P.nu * P.x * sp.sqrt(16 * sp.pi / 5) * H30
    Jdot = (F.subs({P.s: 0, P.sigma: 0}) / P.x ** sp.Rational(3, 2))
    rb = sp.series((taxa / Jdot).subs(P.x, P.v ** 2), P.v, 0, 3).removeO()
    rb0 = sp.simplify(coef_float(rb, 0))
    log("  beta_3 pela taxa conhecida do modo (3,0) (Blanchet LRR 2024, H30) e F: beta_0 = %s = %.10f ; 1PN %s"
        % (rb0, float(rb0), sp.nsimplify(sp.expand(coef_float(rb, 2) / rb0))))
    # H20 = integral de alpha E_b' dx (com o fluxo no horizonte): conferir numericamente
    lead, ser = P.chaves("H20")
    norm = P.expr("norm").subs(P.M, 1)
    h20 = sp.expand(-norm * lead * ser)                       # sinal do codigo (positivo)
    xd = P.expr("xdot").subs(P.M, 1)
    dh = sp.diff(h20, P.x) * xd
    alvo = U.subs(P.M, 1) / sp.sqrt(2)
    for (q, c1, c2_) in [(1.0, 0.0, 0.0), (3.0, 0.6, -0.4)]:
        sub = P.subs_num(q, c1, c2_)
        for xx in (0.01, 0.05):
            a = float(dh.subs(sub).subs(P.x, xx))
            b = float(alvo.subs(sub).subs(P.x, xx))
            log("    d h20/dx * xdot contra +dU20/dt/sqrt2 (q=%g, chi=(%g,%g), x=%.2f): razao - 1 = %+.3e"
                % (q, c1, c2_, xx, a / b - 1))
    log("    (h20 do codigo = -norm H20 > 0 e h20_mem = +U20/sqrt2 nessa convencao; a razao difere de 1 em O(x^4) por truncamento)")
    fav = B.favata_h20(0.05, 0.25)
    log("    h20(x=0.05, q=1, sem spin): Cunningham %.10e ; binarias.favata_h20 (3PN) %.10e"
        % (float(h20.subs(P.subs_num(1, 0, 0)).subs(P.x, 0.05)), fav))
    # primeira lei: J(x) pela integral de E_b
    J = P.J_primeira_lei(7)
    J0 = sp.expand(J.subs({P.s: 0, P.sigma: 0}) / (P.nu * P.x ** sp.Rational(-1, 2)))
    J_bl = (1 + (sp.Rational(3, 2) + P.nu / 6) * P.x + (sp.Rational(27, 8) - sp.Rational(19, 8) * P.nu + P.nu ** 2 / 24) * P.x ** 2
            + (sp.Rational(135, 16) + (-sp.Rational(6889, 144) + sp.Rational(41, 24) * sp.pi ** 2) * P.nu
               + sp.Rational(31, 24) * P.nu ** 2 + sp.Rational(7, 1296) * P.nu ** 3) * P.x ** 3)
    dif = sp.simplify(sp.expand(J0 - J_bl))
    log("  primeira lei: J(x)/(nu x^-1/2) pela integral de -x^-3/2 dE_b/dx, sem spins, menos Blanchet (Jcirc) ate 3PN: %s" % dif)
    Jso = sp.expand(J / (P.nu * P.x ** sp.Rational(-1, 2)))
    log("    termos SO de J: x^{3/2}: %s ; x^{5/2}: %s"
        % (sp.factor(sp.expand(Jso).coeff(P.x ** sp.Rational(3, 2))), sp.factor(sp.expand(Jso).coeff(P.x ** sp.Rational(5, 2)))))
    OUT["J_SO_15"] = str(sp.expand(Jso).coeff(P.x ** sp.Rational(3, 2)))
    return a2


# ------------------------------------------------------------------ (b)
def parte_b():
    log()
    log("(b) RAZOES taxa/fluxo (series em x; coeficientes racionalizados conferidos contra os floats)")
    res = {}
    for nome_m, modos in (("todos (ABFO l<=4)", P.MODOS_ABFO), ("substituto (sem 31, 42, 41)", MODOS_SUR)):
        log("  modos: " + nome_m)
        for saida, por in [(("deslocamento", (2, 0)), "E"), (("deslocamento", (4, 0)), "E"), (("spin", (3, 0)), "J"),
                           (("giroscopica", (1, 0)), "J"), (("giroscopica", (3, 0)), "J"), (("cm", (2, 0)), "E")]:
            r = P.razao_serie(saida, modos, 3, por=por, racionalizar=False)
            Om = sp.Symbol("Om", positive=True)
            r = r.subs(Om, sp.Rational(1, 10))          # so a CM (parte nula) tem termos em 1/Omega; ~0 de qualquer forma
            r0 = complex(sp.N(coef_float(r, 0)))
            if abs(r0) < 1e-12:
                mx = max(abs(complex(sp.N(coef_float(r, k).subs({P.delta: 0.3, P.chis: 0.2, P.chia: 0.1})))) for k in range(4))
                log("    %-12s %s: taxa nula (|coef| <= %.1e ate 1.5PN)" % (saida[0], saida[1], mx))
                res[str(saida) + nome_m] = "zero"
                continue
            c2 = sp.expand(sp.simplify(coef_float(r, 2) / r0).subs(P.delta ** 2, 1 - 4 * P.nu))
            c3 = sp.cancel(P.em_s_sigma(sp.simplify(coef_float(r, 3) / r0)))
            k0 = float(sp.re(sp.N(c2.subs(P.nu, 0))))
            k1 = float(sp.re(sp.N(sp.diff(c2, P.nu))))
            a_s, a_ds, av = so_coefs(c3)
            rac = [sp.nsimplify(z, tolerance=1e-7, rational=True) for z in (k0, k1, a_s, a_ds)]
            log("    %-12s %s: r0 = %+.10f ; 1PN: %+.9f %+.9f nu [%s, %s] ; 1.5PN: %+.9f s %+.9f delta sigma [%s, %s] %s; 0.5PN: %.1e"
                % (saida[0], saida[1], r0.real, k0, k1, rac[0], rac[1], a_s, a_ds, rac[2], rac[3], av,
                   abs(complex(sp.N(coef_float(r, 1).subs({P.delta: 0.3, P.chis: 0.2, P.chia: 0.1}))))))
            res[str(saida) + nome_m] = dict(r0=r0.real, c2=[k0, k1], c3=[a_s, a_ds], racionais=[str(z) for z in rac])
    OUT["razoes"] = res
    return res


# ------------------------------------------------------------------ (c)
def parte_c():
    log()
    log("(c) PRIMEIRA LEI MODO A MODO NO SUBSTITUTO (sistema A, desde 10 Hz)")
    A = C.PAR_A
    t, h, ti = O.gerar_janela(A["q"], A["c1"], A["c2"], A["M"], 10.0)
    dt = t[1] - t[0]
    Edot_t = 0
    Jdot_t = 0
    marcas = [-5000.0, -500.0, -50.0, 0.0, 20.0, 50.0]
    for (l, m) in B.MODOS_OSC:
        hh = h[(l, m)]
        hd = O.derivada(hh[:, None], dt, 8)[:, 0]
        Ed = np.abs(hd) ** 2 / (16 * np.pi)
        Jd = -m * np.imag(np.conj(hh) * hd) / (16 * np.pi)
        Ed_t = 2 * Ed                                         # +m e -m contribuem igual (spins alinhados)
        Edot_t = Edot_t + Ed_t
        Jdot_t = Jdot_t + 2 * Jd
        A_ = np.abs(hh)
        fase = np.unwrap(np.angle(hh))
        w = -O.derivada(fase[:, None], dt, 8)[:, 0]
        Ad = O.derivada(A_[:, None], dt, 8)[:, 0]
        prev = (w / m) * (1 + (Ad / (A_ * w)) ** 2)
        ok = (t > ti + 50) & (t < 60) & (A_ > 1e-2 * A_.max())       # fora das pontas e do fim do toque
        err = np.max(np.abs((Ed / Jd)[ok] / prev[ok] - 1))
        txt = " ".join("u=%+.0f: %.2e" % (u, ((Ad / (A_ * w)) ** 2)[np.argmin(np.abs(t - u))]) for u in marcas)
        log("  (%d,%d): max |(dE/dJ)/((w/m)(1+eps^2)) - 1| = %.1e (identidade; t_i+50 < u < 60, A > 1e-2 max) ; eps^2 = (Adot/(A w))^2 em %s"
            % (l, m, err, txt))
    Om = -O.derivada(np.unwrap(np.angle(h[(2, 2)]))[:, None], dt, 8)[:, 0] / 2
    rr = Edot_t / (Jdot_t * Om) - 1
    log("  total: (dE/dt)/(Omega dJ/dt) - 1, Omega = omega_22/2: " + " ".join(
        "u=%+.0f: %+.2e" % (u, rr[np.argmin(np.abs(t - u))]) for u in marcas))
    # integral: E da janela contra integral de Omega dJ (primeira lei integrada)
    w8 = O.pesos_janela(t, ti)
    k = t < -200
    EJ = np.sum((w8 * Edot_t)[k]), np.sum((w8 * Om * Jdot_t)[k])
    EJf = np.sum(w8 * Edot_t), np.sum(w8 * Om * Jdot_t)
    log("  integrais desde 10 Hz: ate u = -200: E = %.8e, int Omega dJ = %.8e (razao - 1 = %+.2e) ; ate o fim: %.6e contra %.6e (%+.2e)"
        % (EJ[0], EJ[1], EJ[0] / EJ[1] - 1, EJf[0], EJf[1], EJf[0] / EJf[1] - 1))
    OUT["primeira_lei"] = dict(razao_ate_m200=EJ[0] / EJ[1] - 1, razao_total=EJf[0] / EJf[1] - 1)
    del t, h


# ------------------------------------------------------------------ (d)
def previsoes(q, c1, c2, a_sur, a_all, raz):
    """Funcoes x -> memoria acumulada (convencao do codigo) por ordem PN: desl20, desl40, spin30, giro10, giro30.

    desl: h_l0(x) de Cunningham (todos os modos) + correcao dos modos ausentes do substituto (ABFO, 1PN e 1.5PN);
    spin/giro: integral de beta(x) x^{-3/2} E_b'(x) (beta ABFO ate 1.5PN com os modos do substituto; E_b ate 3.5PN).
    """
    sub = P.subs_num(q, c1, c2)
    nuv = sub[P.nu]
    out = {}
    for nome, L in (("desl20", "H20"), ("desl40", "H40")):
        lead, ser = P.chaves(L)
        norm = P.expr("norm").subs(P.M, 1)
        sgn = -1
        fs = {}
        for n in ORDENS:
            e = sgn * norm * lead * P.serie_em_v(ser, n).subs(P.v, sp.sqrt(P.x))
            fs[n] = sp.lambdify(P.x, e.subs(sub), "numpy")
        out[nome] = fs
    # correcao dos modos ausentes (deslocamento l = 2, 4): integral de (alpha_sur - alpha_all) E_b' dx
    Eb = P.E_lig_pos(7)
    dEb = {n: sp.lambdify(P.x, sp.diff(P.nu * P.x / 2 * P.serie_em_v(sp.expand(Eb / (P.nu * P.x / 2)), n)
                                        .subs(P.v, sp.sqrt(P.x)), P.x).subs(sub), "numpy") for n in ORDENS}
    corr = {}
    for nome, L in (("desl20", 2), ("desl40", 4)):
        dal = sp.expand(a_sur[L] - a_all[L])
        f = sp.lambdify(P.v, dal.subs(sub), "numpy")
        corr[nome] = lambda xa, xb, f=f: quad(lambda xx: float(np.real(f(np.sqrt(xx)))) * dEb[7](xx), xa, xb,
                                              epsabs=0, epsrel=1e-12)[0]
    out["corr"] = corr
    # spin e giroscopica
    for nome, saida in (("spin30", ("spin", (3, 0))), ("giro10", ("giroscopica", (1, 0))), ("giro30", ("giroscopica", (3, 0)))):
        r = raz[saida]
        fs = {}
        for n in ORDENS:
            nb = min(n, 3)
            rb = sum(coef_float(r, k) * P.v ** k for k in range(nb + 1))
            fr = sp.lambdify(P.v, rb.subs(sub), "numpy")
            de = dEb[n]
            fs[n] = (lambda xa, xb, fr=fr, de=de: quad(lambda xx: float(np.real(fr(np.sqrt(xx)))) * xx ** -1.5 * de(xx),
                                                       xa, xb, epsabs=0, epsrel=1e-12)[0])
        out[nome] = fs
    return out, nuv


def parte_d(raz_sur, a_sur, a_all):
    log()
    log("(d) MEMORIAS DE BANDA: substituto (nivel A, janela) contra PN, ordem por ordem")
    log("    erro relativo (PN - substituto)/substituto por banda [Mf_a, Mf_b]; deslocamento: H_l0 de Cunningham et al. "
        "(todos os modos) + correcao dos modos ausentes do substituto; spin/giro: beta ABFO (modos do substituto) ate 1.5PN "
        "e E_b(x) de Cunningham ate a ordem indicada (acima de 1.5PN so E_b melhora)")
    Mref = 50.0
    res = {}
    for nome, q, c1, c2 in SISTEMAS:
        t0 = time.time()
        freqs = [b / (Mref * MSUN_S) for b in BORDAS]
        rr = C.janelas(q, c1, c2, Mref, freqs)
        mem = {k: [] for k in ("desl20", "desl40", "spin30", "giro10", "giro30", "cm20")}
        xs = []
        Mfs = []
        for m, aux in rr:
            mem["desl20"].append(m["deslocamento"][(2, 0)].real)
            mem["desl40"].append(m["deslocamento"][(4, 0)].real)
            mem["spin30"].append(m["spin"][(3, 0)].imag)
            mem["giro10"].append(m["giroscopica"][(1, 0)].real)
            mem["giro30"].append(m["giroscopica"][(3, 0)].real)
            mem["cm20"].append(m["cm"][(2, 0)].real)
            xs.append(aux["x_i"])
            Mfs.append(aux["M_f"])
        Ej = [aux["E_janela"] for m, aux in rr]
        prev, nuv = previsoes(q, c1, c2, a_sur, a_all, raz_sur)
        log("  sistema %s (q=%g, chi=(%+.1f,%+.1f)), %.0f s" % (nome, q, c1, c2, time.time() - t0))
        resS = {}
        # energia da banda: substituto contra Delta E_b (Cunningham et al., 3.5PN com SO, SS, SSS) e contra e_lig (3PN+SO, sem SS)
        Ebf = sp.lambdify(P.x, P.E_lig_pos(7).subs(P.subs_num(q, c1, c2)), "numpy")
        eE, eE2, eal = [], [], []
        for j in range(len(BORDAS) - 1):
            Es = Ej[j] - Ej[j + 1]
            xa, xb = xs[j], xs[j + 1]
            eE.append((Ebf(xb) - Ebf(xa)) / Es - 1)
            eE2.append((O.e_lig(xb, q, c1, c2) - O.e_lig(xa, q, c1, c2)) / Es - 1)
            # alpha efetivo da banda: (desl20 da banda)/(energia da banda), contra a media PN de alpha (modos do substituto)
            fa = sp.lambdify(P.v, a_sur[2].subs(P.subs_num(q, c1, c2)), "numpy")
            dEb = sp.lambdify(P.x, sp.diff(P.E_lig_pos(7), P.x).subs(P.subs_num(q, c1, c2)), "numpy")
            num = quad(lambda xx: float(np.real(fa(np.sqrt(xx)))) * dEb(xx), xa, xb, epsrel=1e-12)[0]
            alpha_pn = num / (Ebf(xb) - Ebf(xa))
            alpha_sur = (mem["desl20"][j] - mem["desl20"][j + 1]) / Es
            eal.append(alpha_pn / alpha_sur - 1)
        log("    energia da banda, PN/substituto - 1: Cunningham 3.5PN %s ; e_lig 3PN+SO %s"
            % (" ".join("%+.1e" % z for z in eE), " ".join("%+.1e" % z for z in eE2)))
        log("    alpha efetivo (desl20/energia) da banda, PN (ABFO 1.5PN)/substituto - 1: %s" % " ".join("%+.1e" % z for z in eal))
        resS["erro_energia"] = eE
        resS["erro_alpha"] = eal
        for tipo in ("desl20", "desl40", "spin30", "giro30"):
            log("    %s" % tipo)
            linha_tipo = []
            for j in range(len(BORDAS) - 1):
                sur = mem[tipo][j] - mem[tipo][j + 1]
                xa, xb = xs[j], xs[j + 1]
                errs = []
                for n in ORDENS:
                    if tipo.startswith("desl"):
                        pn = prev[tipo][n](xb) - prev[tipo][n](xa) + (prev["corr"][tipo](xa, xb) if n >= 2 else 0.0)
                    else:
                        pn = prev[tipo][n](xa, xb)
                        if j == 0 and n == 0:
                            sgn_ok = np.sign(pn) == np.sign(sur)
                    errs.append(pn / sur - 1)
                linha_tipo.append(dict(banda=[BORDAS[j], BORDAS[j + 1]], sur=sur, erros=errs))
                log("      [%.3f, %.3f] sub %+.6e | " % (BORDAS[j], BORDAS[j + 1], sur)
                    + " ".join("%s %+.1e" % (NOME_ORD[n], e) for n, e in zip(ORDENS, errs)))
            resS[tipo] = linha_tipo
        # CM: parte ordinaria -1.5 M_f desl / Dfrak(2), parte nula ~ 0 na inspiral
        log("    cm20: banda (substituto) contra -1.5 M_f desl20_banda / Dfrak(2) (parte nula prevista ~0 na inspiral)")
        cmrel = []
        for j in range(len(BORDAS) - 1):
            sur = mem["cm20"][j] - mem["cm20"][j + 1]
            ordn = -1.5 * Mfs[j] * (mem["desl20"][j] - mem["desl20"][j + 1]) / Dfrak(2)
            cmrel.append((sur - ordn) / sur)
        log("      fracao nula da CM por banda: " + " ".join("%+.1e" % c for c in cmrel))
        resS["cm_nula"] = cmrel
        res[nome] = resS
    OUT["bandas"] = res
    return res


def figura(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"axes.facecolor": "#fcfcfb", "figure.facecolor": "#fcfcfb", "axes.edgecolor": "#52514e",
                         "text.color": "#52514e", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "grid.color": "#e6e5e0", "font.size": 9})
    cores = ["#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#9b59b6"]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
    for i, (tipo, tit) in enumerate((("desl20", "deslocamento (2,0)"), ("desl40", "deslocamento (4,0)"),
                                     ("spin30", "spin (3,0)"))):
        for c, (nome, q, c1, c2) in zip(cores, SISTEMAS):
            # banda [0.004, 0.006]
            L = [d for d in res[nome][tipo] if abs(d["banda"][0] - 0.004) < 1e-9][0]
            ax[i].semilogy(range(len(ORDENS)), np.abs(L["erros"]) + 1e-12, "o-", color=c, ms=3,
                           label="q=%g, $\\chi$=(%+.1f,%+.1f)" % (q, c1, c2))
        ax[i].set_xticks(range(len(ORDENS)))
        ax[i].set_xticklabels([NOME_ORD[n] for n in ORDENS])
        ax[i].set_title(tit + ", banda $Mf\\in[0{,}004;\\,0{,}006]$", fontsize=9)
        ax[i].set_ylabel("|PN/substituto - 1|")
        ax[i].grid(True)
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e20_bandas_pn.png"), dpi=150)


if __name__ == "__main__":
    t0 = time.time()
    parte_a()
    raz = parte_b()
    # razoes para as previsoes (series simbolicas)
    raz_sur = {s_: P.razao_serie(s_, MODOS_SUR, 3, por="J", racionalizar=False)
               for s_ in (("spin", (3, 0)), ("giroscopica", (1, 0)), ("giroscopica", (3, 0)))}
    a_sur = {L: P.alpha_desl(L, MODOS_SUR, 3) for L in (2, 4)}
    a_all = {L: P.alpha_desl(L, P.MODOS_ABFO, 3) for L in (2, 4)}
    for L in (2, 4):
        d = sp.expand(a_sur[L] - a_all[L])
        log("  alpha_%d(substituto) - alpha_%d(todos) = %s" % (L, L, sp.nsimplify(sp.simplify(
            sp.expand(d / coef_float(a_all[L], 0)).subs(P.delta ** 2, 1 - 4 * P.nu)))))
    parte_c()
    res = parte_d(raz_sur, a_sur, a_all)
    figura(res)
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RAIZ, "resultados", "exp20_pn.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(os.path.join(RAIZ, "resultados", "exp20_pn.json"), "w") as fh:
        json.dump(OUT, fh, indent=1, default=str)
