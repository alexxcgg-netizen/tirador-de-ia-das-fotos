"""exp33 (L10) - validacao do caminho NRSur7dq4 de exp33_comum.

(a) gerar7 com zerar_m0=False reproduz a chamada publica do gwsurrogate; com spins alinhados e zerar_m0=True os
    modos inerciais (l, 0) ficam nulos e o quaternio coprecessante e a identidade.
(b) spins alinhados: NRSur7dq4 contra NRHybSur3dq8_CCE (observaveis.py), nivel A, mesma janela f_22 >= f0 = 0.007,
    multipolos m = 0 principais, E_janela, M_f, modulos dos m != 0; com o mesmo conjunto de modos e com todos.
(c) momento linear e angular irradiados contra surfinBH NRSur7dq4Remnant (v_f e J_i - J_f) em sistemas alinhados e
    precessantes (spins e referencial em f_ref = f0).
(d) convergencia em dt (0.25 contra 0.125) num sistema precessante.
(e) efeito de zerar os modos coorbitais m = 0 (variante "como o CCE"; o padrao usa todos os modos).
(g) os modos coorbitais m = 0 do NRSur7dq4 nao contem memoria (valor final e maximo de Re/Im).
(h) bico do NRSur7dq4 em spin nulo (nao diferenciavel em chiB = 0).
(f) suavidade nos 7 parametros: derivadas com passos 1e-3 e 1e-4.
Saida: resultados/exp33_validacao.txt
"""
import os
import sys
import time

import numpy as np

import exp33_comum as C
import observaveis as O
import binarias as B
from deteccao import MSUN_S

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
F0 = C.F0_PADRAO
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


ALINHADOS = [(1.0, 0.0, 0.0), (1.2, 0.3, -0.2), (2.0, -0.5, 0.5), (3.0, 0.5, 0.3), (4.0, 0.0, 0.0)]
PREC = {"P1": (2.0, (0.5, 0.0, 0.2), (0.0, -0.3, 0.1)),
        "P2": (1.2, (0.6, 0.2, 0.0), (-0.3, 0.4, 0.2)),
        "P3": (3.0, (0.7, 0.0, 0.0), (0.0, 0.0, 0.0)),
        "P4": (1.0, (0.5, 0.0, 0.0), (-0.5, 0.0, 0.0))}
CHAVES = [("deslocamento", (2, 0)), ("deslocamento", (4, 0)), ("spin", (3, 0)), ("cm", (2, 0)), ("cm", (4, 0)),
          ("giroscopica", (1, 0)), ("giroscopica", (3, 0))]


def calc7(q, cA, cB, dt=0.25, zerar_m0=False, modos=C.MODOS, f_ref=F0):
    t, h, dyn = C.gerar7(q, cA, cB, dt=dt, f_ref=f_ref, zerar_m0=zerar_m0)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, aux = C.memorias7(q, t, h, dyn, ti, modos=modos)
    del t, h, dyn
    return mem, aux


def valor(mem, tipo, k):
    z = mem[tipo].get(k, 0j)
    return z.imag if tipo == "spin" else z.real


# ---------------------------------------------------------------- (a)
def teste_a():
    log("(a) gerador")
    s = C.sur7()
    q, cA, cB = PREC["P1"]
    t, h, dyn = C.gerar7(q, cA, cB, zerar_m0=False, f_ref=F0)
    t2, h2, _ = s(q, list(cA), list(cB), times=t, f_low=0, f_ref=F0)
    d = max(np.max(np.abs(h[k] - h2[k])) for k in h)
    log("  P1, zerar_m0=False contra chamada publica: max |dh| = %.1e" % d)
    t, h, dyn = C.gerar7(1.2, (0, 0, 0.3), (0, 0, -0.2), zerar_m0=True, f_ref=F0)
    d0 = max(np.max(np.abs(h[(l, 0)])) for l in (2, 3, 4))
    dq = np.max(np.abs(dyn["q_copr"] - np.array([1, 0, 0, 0])[:, None]))
    log("  alinhado (1.2; 0.3, -0.2), zerar_m0=True: max |h_l0| = %.1e ; max |q_copr - 1| = %.1e ; modos l <= %d, "
        "N = %d, t de %.2f a %.2f M" % (d0, dq, max(k[0] for k in h), len(t), t[0], t[-1]))
    t, h, dyn = C.gerar7(*PREC["P1"], zerar_m0=True, f_ref=F0)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    log("  P1: t_i = %.3f M ; chiA(t_i) = %s ; chiB(t_i) = %s ; eixo coprecessante em t_i = %s" % (
        ti, np.round([O._interp_em(t, dyn["chiA"][:, k], ti) for k in range(3)], 5),
        np.round([O._interp_em(t, dyn["chiB"][:, k], ti) for k in range(3)], 5),
        np.round(C.eixo_copr([O._interp_em(t, dyn["q_copr"][k], ti) for k in range(4)]), 5)))
    del t, h, dyn


# ---------------------------------------------------------------- (b)
def mem_cce(q, c1, c2, modos):
    Mfic = F0 / (MSUN_S * 10.0)
    t, h, ti = O.gerar_janela(q, c1, c2, Mfic, 10.0)
    n = len(t)
    dyn = {"chiA": np.tile([0, 0, c1], (n, 1)), "chiB": np.tile([0, 0, c2], (n, 1)),
           "q_copr": np.tile(np.array([1.0, 0, 0, 0])[:, None], (1, n)),
           "orbphase": -0.5 * np.unwrap(np.angle(h[(2, 2)]))}
    mem, aux = C.memorias7(q, t, h, dyn, ti, modos=modos)
    del t, h
    return mem, aux


def teste_b():
    log("")
    log("(b) spins alinhados: NRSur7dq4 contra NRHybSur3dq8_CCE, nivel A, janela f_22 >= %.4f, ate o fim de cada onda" % F0)
    cce_l5 = tuple(B.lista_osc())
    cce_l4 = tuple(k for k in cce_l5 if k[0] <= 4)
    log("  conjuntos: S7 = NRSur7dq4 m != 0 (l <= 4, 18 modos) ; S7c = NRSur7dq4 so com os modos do CCE l <= 4 ; "
        "Cc4 = CCE l <= 4 ; C5 = CCE com (5,5)")
    log("  diferencas relativas (X - CCE_mesmos_modos)/CCE")
    for (q, c1, c2) in ALINHADOS:
        m7, a7 = calc7(q, (0, 0, c1), (0, 0, c2), modos=C.MODOS_SEM_M0, zerar_m0=True)
        m7c, a7c = calc7(q, (0, 0, c1), (0, 0, c2), modos=cce_l4, zerar_m0=True)
        mc4, ac4 = mem_cce(q, c1, c2, cce_l4)
        mc5, ac5 = mem_cce(q, c1, c2, cce_l5)
        log("  q %.1f chi (%+.1f, %+.1f): t_i S7 %.2f, CCE %.2f M ; E_janela S7 %.6f S7c %.6f Cc4 %.6f C5 %.6f ;"
            " M_f S7 %.6f C5 %.6f" % (q, c1, c2, a7["t_i"], ac5["t_i"], a7["E_janela"], a7c["E_janela"],
                                       ac4["E_janela"], ac5["E_janela"], a7["M_f"], ac5["M_f"]))
        partes = []
        for tipo, k in CHAVES:
            v7, v7c, v4, v5 = (valor(m, tipo, k) for m in (m7, m7c, mc4, mc5))
            partes.append("%s%d%d: S7c-Cc4 %+.2e, S7-C5 %+.2e (modos S7-S7c %+.1e, C5-Cc4 %+.1e)" % (
                tipo[:4], k[0], k[1], v7c / v4 - 1, v7 / v5 - 1, v7 / v7c - 1, v5 / v4 - 1))
        for p in partes:
            log("      " + p)
        for tipo, k in (("spin", (2, 1)), ("giroscopica", (2, 1)), ("deslocamento", (3, 1)), ("cm", (2, 2)),
                        ("deslocamento", (2, 2))):
            a, b = abs(m7[tipo].get(k, 0)), abs(mc5[tipo].get(k, 0))
            log("      |%s%d%d| (borda m != 0): S7 %.3e, C5 %.3e (razao %.3f)" % (tipo[:4], k[0], k[1], a, b, a / b))
        log("      recuo |P|/M_f: S7 %.3e, C5 %.3e" % (np.linalg.norm(a7["P_rad"]) / a7["M_f"],
                                                       np.linalg.norm(ac5["P_rad"]) / ac5["M_f"]))
    log("  (%.0f s)" % (time.time() - T0))


# ---------------------------------------------------------------- (c)
def L_pn(x, eta):
    """|L| orbital (M = 1) ate 2PN sem spin: (eta/sqrt(x)) [1 + (3/2 + eta/6) x + (27/8 - 19/8 eta + eta^2/24) x^2]."""
    return eta / np.sqrt(x) * (1 + (1.5 + eta / 6) * x + (27 / 8 - 19 / 8 * eta + eta ** 2 / 24) * x ** 2)


def teste_c():
    import surfinBH
    log("")
    log("(c) momento linear e angular irradiados contra NRSur7dq4Remnant (omega0 = pi f0, evolucao pelo substituto)")
    fit = surfinBH.LoadFits("NRSur7dq4Remnant")
    casos = [("alinhado", (1.2, (0, 0, 0.3), (0, 0, -0.2))), ("alinhado", (3.0, (0, 0, 0.5), (0, 0, 0.3)))]
    casos += list(PREC.items())
    for nome, (q, cA, cB) in casos:
        m, a = calc7(q, cA, cB)
        mf, chif, vf, mfe, chife, vfe = fit.all(q, list(cA), list(cB), omega0=np.pi * F0, omega_switch_IG=0.5 * np.pi * F0)
        eta = q / (1 + q) ** 2
        m1, m2 = q / (1 + q), 1 / (1 + q)
        Ji = L_pn(a["x_i"], eta) * a["Lhat_i"] + m1 ** 2 * a["chiA_i"] + m2 ** 2 * a["chiB_i"]
        Jf = mf ** 2 * np.asarray(chif)
        Jesp = Ji - Jf
        log("  %s q %.1f chiA %s chiB %s" % (nome, q, cA, cB))
        log("      M_f: memorias %.5f ; ajuste %.5f +- %.1e" % (a["M_f"], mf, mfe))
        log("      recuo -P/M_f = %s ; ajuste v_f = %s (+- %s)" % (np.array2string(-a["P_rad"] / a["M_f"], precision=5),
                                                                   np.array2string(np.asarray(vf), precision=5),
                                                                   np.array2string(np.asarray(vfe), precision=1)))
        log("      J_rad (janela) = %s ; J_i(PN) - M_f^2 chi_f = %s ; |dif| = %.2e" % (
            np.array2string(a["J_rad"], precision=5), np.array2string(Jesp, precision=5), np.linalg.norm(a["J_rad"] - Jesp)))
        log("      chi_f (ajuste) = %s ; eixo coprecessante no pico = %s ; angulo(chi_f, eixo pico) = %.2f graus ;"
            " angulo(J_rad, chi_f) = %.2f graus" % (np.array2string(np.asarray(chif), precision=4),
                                                     np.array2string(a["Lhat_pico"], precision=4),
                                                     np.degrees(ang(chif, a["Lhat_pico"])),
                                                     np.degrees(ang(chif, a["J_rad"]))))
    log("  (%.0f s)" % (time.time() - T0))


def ang(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1)))


# ---------------------------------------------------------------- (d), (e)
def teste_de():
    log("")
    log("(d) convergencia em dt e (e) efeito de zerar os modos coorbitais m = 0")
    for nome in ("P1", "P4"):
        q, cA, cB = PREC[nome]
        m1, _ = calc7(q, cA, cB, dt=0.25)
        m2, _ = calc7(q, cA, cB, dt=0.125)
        m3, _ = calc7(q, cA, cB, zerar_m0=True)
        v1, rot = C.vetor_real(m1)
        v2, _ = C.vetor_real(m2)
        v3, _ = C.vetor_real(m3)
        log("  %s: |v(dt .25) - v(dt .125)|/|v| = %.2e ; |v(m0 coorbitais zerados) - v(padrao)|/|v| = %.2e" % (
            nome, np.linalg.norm(v1 - v2) / np.linalg.norm(v1), np.linalg.norm(v3 - v1) / np.linalg.norm(v1)))
        for tipo in C.TIPOS:
            idx = [i for i, r in enumerate(rot) if r[0] == tipo]
            idx_m = [i for i in idx if rot[i][2] != 0]
            log("      %-12s |dv|/|v_tipo| dt: %.1e ; m0: %.1e ; so m != 0: dt %.1e, m0 %.1e (|v_m!=0|/|v_tipo| = %.3f)" % (
                tipo, np.linalg.norm((v1 - v2)[idx]) / np.linalg.norm(v1[idx]),
                np.linalg.norm((v3 - v1)[idx]) / np.linalg.norm(v1[idx]),
                np.linalg.norm((v1 - v2)[idx_m]) / max(np.linalg.norm(v1[idx_m]), 1e-30),
                np.linalg.norm((v3 - v1)[idx_m]) / max(np.linalg.norm(v1[idx_m]), 1e-30),
                np.linalg.norm(v1[idx_m]) / np.linalg.norm(v1[idx])))
    log("  (%.0f s)" % (time.time() - T0))


# ---------------------------------------------------------------- (f)
def teste_f():
    log("")
    log("(f) suavidade: derivadas centrais do vetor real (l <= 4) com passos 1e-3 e 1e-4 em cada parametro, P1")
    q, cA, cB = PREC["P1"]
    p0 = np.array([q, *cA, *cB])

    def V(p):
        m, _ = calc7(p[0], p[1:4], p[4:7])
        return C.vetor_real(m)[0]
    nomes = ["q", "chiAx", "chiAy", "chiAz", "chiBx", "chiBy", "chiBz"]
    for i in range(7):
        ds = []
        for hh in (1e-3, 1e-4):
            e = np.zeros(7)
            e[i] = hh
            ds.append((V(p0 + e) - V(p0 - e)) / (2 * hh))
        log("  %-6s |dv| = %.4e ; dif. relativa entre passos = %.1e" % (nomes[i], np.linalg.norm(ds[0]),
                                                                       np.linalg.norm(ds[0] - ds[1]) / np.linalg.norm(ds[0])))
    log("  (%.0f s)" % (time.time() - T0))


# ---------------------------------------------------------------- (g)
class _Grava:
    def __init__(self, orig, dest):
        self.orig, self.dest = orig, dest

    def __call__(self, q, a, b, ellMax=4):
        m = self.orig(q, a, b, ellMax=ellMax)
        self.dest["h"] = m.copy()
        return m

    def __getattr__(self, n):
        return getattr(self.orig, n)


def teste_g():
    log("")
    log("(g) modos coorbitais m = 0 do NRSur7dq4 (rede esparsa do substituto): ha memoria neles?")
    s = C.sur7()
    ps = s._sur_dimless
    casos = [("alinhado", (1.2, (0, 0, 0.3), (0, 0, -0.2)))] + list(PREC.items())
    for nome, (q, cA, cB) in casos:
        dest = {}
        o = ps.coorb_sur
        ps.coorb_sur = _Grava(o, dest)
        try:
            t, h, dyn = s(q, list(cA), list(cB), dt=1.0, f_low=0, f_ref=F0, precessing_opts={"return_dynamics": True})
        finally:
            ps.coorb_sur = o
        H = dest["h"]
        partes = []
        for l in (2, 3, 4):
            r = H[l * l - 4 + l]
            partes.append("(%d,0): max|Re| %.1e, max|Im| %.1e, valor final %.1e" % (l, np.abs(r.real).max(),
                                                                                   np.abs(r.imag).max(), abs(r[-1])))
        log("  %s: max|h22 coorb| %.3f ; %s" % (nome, np.abs(H[4]).max(), " ; ".join(partes)))
        mem, aux = calc7(q, cA, cB)
        log("      deslocamento (2,0) de memoria nula (nivel A) na janela: %.4f  (o (2,0) coorbital termina em %.1e: sem memoria)"
            % (mem["deslocamento"][(2, 0)].real, abs(H[2 * 2 - 4 + 2][-1])))
        del t, h, dyn
    log("  (%.0f s)" % (time.time() - T0))


# ---------------------------------------------------------------- (h)
def teste_h():
    log("")
    log("(h) diferenciabilidade em spin nulo: q = 3, chiA = (0.7, 0, 0), chiB = (0,0,0) contra chiB = (0,0,0.1);"
        " variacao de chiBx em +-h")
    for cB0 in ((0.0, 0.0, 0.0), (0.0, 0.0, 0.1)):
        v0 = C.vetor_real(calc7(3.0, (0.7, 0, 0), cB0)[0])[0]
        for hh in (1e-6, 1e-5, 1e-4, 1e-3):
            vp = C.vetor_real(calc7(3.0, (0.7, 0, 0), (cB0[0] + hh, cB0[1], cB0[2]))[0])[0]
            vm = C.vetor_real(calc7(3.0, (0.7, 0, 0), (cB0[0] - hh, cB0[1], cB0[2]))[0])[0]
            log("  chiB0 %s h %.0e: |v(+h)-v0|/h %.3e ; |v(-h)-v0|/h %.3e ; |v(+h)-v(-h)|/2h %.3e ; |v(+h)+v(-h)-2v0|/h^2 %.2e"
                % (cB0, hh, np.linalg.norm(vp - v0) / hh, np.linalg.norm(vm - v0) / hh, np.linalg.norm(vp - vm) / 2 / hh,
                   np.linalg.norm(vp + vm - 2 * v0) / hh ** 2))
    log("  (%.0f s)" % (time.time() - T0))


if __name__ == "__main__":
    so = sys.argv[1:] or ["a", "b", "c", "de", "f", "g", "h"]
    log("exp33_validacao: NRSur7dq4 (nivel A, modos coorbitais m = 0 zerados), f0 = %.4f" % F0)
    for n in so:
        {"a": teste_a, "b": teste_b, "c": teste_c, "de": teste_de, "f": teste_f, "g": teste_g, "h": teste_h}[n]()
    if not sys.argv[1:]:
        with open(os.path.join(RES, "exp33_validacao.txt"), "w") as fh:
            fh.write("\n".join(linhas) + "\n")
