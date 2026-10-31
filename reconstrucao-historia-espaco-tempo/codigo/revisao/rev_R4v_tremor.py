"""Verificador R4v, itens 1 e 6: determinismo, tremor do SEOBNRv5EHM e frequencia instantanea no inicio.

Cadeia identica a do exp12 (E.gerar + E.memorias_janela + B.valores_fisicos), sem cache nenhum.
 a) determinismo: B (e0 = 0.2, q_B = 2) do exp12_pares.json avaliado duas vezes neste processo e comparado,
    bit a bit, com o valor gravado pelo revisor R4 num processo diferente (rev_R4_ruido_exec1.json);
 b) tremor em M (= tremor em omega_start, pois M so entra por f0 = M f): passos relativos de 1e-15 a 1e-6;
 c) tremor em c1, q e e0 (passo absoluto 1e-12) e no circular A (e0 = 0);
 d) onde a onda muda: h22 de M e M (1 + 1e-12) alinhados no pico; diferenca relativa por trecho e
    diferenca de fase; comprimento da serie e instante do pico;
 e) item 6: frequencia instantanea do (2,2) (Hz) na primeira orbita, para B (0.2, 2) e B (0.3, 2), l0 = 0.
Saida: resultados/revisao/rev_R4v_tremor.txt
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
TIP = ("deslocamento", "spin", "cm", "giroscopica")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def onda(q, c1, c2, M, e0):
    f0 = M * Dt.MSUN_S * E.F_FIS
    return E.gerar(q, c1, c2, f0, e0)


def quatro(par):
    """As quatro memorias no observador, sem cache (mesma cadeia do exp12)."""
    f0 = par["M"] * Dt.MSUN_S * E.F_FIS
    t, h = E.gerar(par["q"], par["c1"], par["c2"], f0, par["e"])
    eta = par["q"] / (1 + par["q"]) ** 2
    mem, aux = E.memorias_janela(t, h, E.LISTA, E.calc(), eta, (np.pi * f0) ** (2 / 3))
    del t, h
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"])


def drel(v, w):
    return np.array([(v[k] - w[k]) / abs(w[k]) for k in TIP])


def fmt(d):
    return "max %.2e [%s]" % (np.max(np.abs(d)), " ".join("%s %+.1e" % (k[:4], x) for k, x in zip(TIP, d)))


if __name__ == "__main__":
    t0 = time.time()
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp12_pares.json")))
    p = [x for x in DADOS["pares"] if x["e0"] == 0.2 and x["qB"] == 2.0][0]
    PB = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"], e=p["e0"])
    PA = dict(DADOS["A"])
    # ---------- a) ----------
    v0 = quatro(PB)
    v0b = quatro(PB)
    r4 = json.load(open(os.path.join(RES, "rev_R4_ruido_exec1.json")))["vals"]["B e0=0.2 qB=2.0"]
    log("a) determinismo, B (e0 = 0.2, q_B = 2): 2a avaliacao neste processo: %s" % fmt(drel(v0b, v0)))
    log("   contra o valor gravado pelo R4 em outro processo: %s ; bit a bit igual: %s"
        % (fmt(drel(v0, r4)), all(v0[k] == r4[k] for k in TIP)))
    vA = quatro(PA)
    log("   A recalculado contra o alvo do exp12_pares.json: %s ; bit a bit igual: %s"
        % (fmt(drel(vA, DADOS["alvo"])), all(vA[k] == DADOS["alvo"][k] for k in TIP)))
    log("   B (0.2, 2) contra o alvo (delta do par, reavaliado): %s" % fmt(drel(v0, DADOS["alvo"])))
    # ---------- b) ----------
    log()
    log("b) tremor em M (B 0.2, 2): diferenca relativa a M exato, M -> M (1 + eps)")
    for eps in (1e-15, 1e-14, -1e-14, 1e-13, 1e-12, -1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6):
        v = quatro(dict(PB, M=PB["M"] * (1 + eps)))
        # a parte esperada de uma variacao suave e ~ eps (escala M/D, M^2/D): desprezivel ate 1e-7
        log("   eps %+.0e (M muda %+.2e Msol): %s" % (eps, PB["M"] * eps, fmt(drel(v, v0))))
    # ---------- c) ----------
    log()
    log("c) tremor em outros parametros (passo absoluto 1e-12) e no circular A")
    for nome in ("c1", "q", "e"):
        v = quatro(dict(PB, **{nome: PB[nome] + 1e-12}))
        log("   B (0.2, 2), %s + 1e-12: %s" % (nome, fmt(drel(v, v0))))
    for eps in (1e-12, 1e-9, 1e-6):
        v = quatro(dict(PA, M=PA["M"] * (1 + eps)))
        log("   A (e0 = 0), M (1 + %.0e): %s" % (eps, fmt(drel(v, vA))))
    v = quatro(dict(PA, c1=PA["c1"] + 1e-12))
    log("   A (e0 = 0), c1 + 1e-12: %s" % fmt(drel(v, vA)))
    # ---------- d) ----------
    log()
    log("d) onde a onda muda: B (0.2, 2) com M e M (1 + 1e-12); h22 em funcao de t - t_pico (unidades de M)")
    ta, ha = onda(PB["q"], PB["c1"], PB["c2"], PB["M"], PB["e"])
    tb, hb = onda(PB["q"], PB["c1"], PB["c2"], PB["M"] * (1 + 1e-12), PB["e"])
    ia, ib = np.argmax(np.abs(ha[(2, 2)])), np.argmax(np.abs(hb[(2, 2)]))
    log("   comprimento %d x %d amostras ; dt %.6f x %.6f ; t0 %.6f x %.6f ; t_pico - t0 %.6f x %.6f ; t_fim - t_pico %.4f x %.4f"
        % (len(ta), len(tb), ta[1] - ta[0], tb[1] - tb[0], ta[0], tb[0], ta[ia] - ta[0], tb[ib] - tb[0],
           ta[-1] - ta[ia], tb[-1] - tb[ib]))
    # pico com interpolacao quadratica em |h22|
    def pico(t, h):
        a = np.abs(h)
        i = np.argmax(a)
        y0, y1, y2 = a[i - 1], a[i], a[i + 1]
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        return t[i] + d * (t[1] - t[0])
    tpa, tpb = pico(ta, ha[(2, 2)]), pico(tb, hb[(2, 2)])
    log("   t_pico interpolado - t0: %.9f x %.9f (diferenca %+.3e M)" % (tpa - ta[0], tpb - tb[0], (tpb - tb[0]) - (tpa - ta[0])))
    sa, sb = ta - tpa, tb - tpb
    lo, hi = max(sa[0], sb[0]), min(sa[-1], sb[-1])
    grade = np.arange(lo, hi, 0.1)
    def interp(s, z):
        return np.interp(grade, s, z.real) + 1j * np.interp(grade, s, z.imag)
    za, zb = interp(sa, ha[(2, 2)]), interp(sb, hb[(2, 2)])
    fa, fb = np.unwrap(np.angle(za)), np.unwrap(np.angle(zb))
    dfase = (fb - fb[np.argmin(np.abs(grade))]) - (fa - fa[np.argmin(np.abs(grade))])
    for (u1, u2) in [(lo, lo + 200), (lo + 200, -5000), (-5000, -1000), (-1000, -300), (-300, -100), (-100, -20), (-20, 0), (0, hi)]:
        sel = (grade >= u1) & (grade < u2)
        if not np.any(sel):
            continue
        da = np.abs(np.abs(zb[sel]) - np.abs(za[sel])) / np.abs(za[sel])
        log("   t - t_pico em [%7.0f, %7.0f): max |d|h22||/|h22| %.1e ; max |d fase| (alinhada no pico) %.1e rad"
            % (u1, u2, np.max(da), np.max(np.abs(dfase[sel]))))
    del ta, ha, tb, hb, za, zb
    # ---------- e) ----------
    log()
    log("e) item 6: frequencia instantanea do (2,2) no inicio (l0 = 0), em Hz no detector")
    for pp in DADOS["pares"]:
        if pp["qB"] != 2.0:
            continue
        t, h = onda(pp["qB"], pp["c1"], pp["c2B"], pp["M"], pp["e0"])
        fase = np.unwrap(np.angle(h[(2, 2)]))
        w = np.gradient(fase, t[1] - t[0])
        Ms = pp["M"] * Dt.MSUN_S
        f0 = Ms * E.F_FIS                                  # M f na frequencia media pedida
        T_orb = 2.0 / f0                                   # periodo orbital medio (em M): 2 pi / (pi f0)
        for n_orb in (1, 2):
            sel = t - t[0] <= n_orb * T_orb
            fhz = np.abs(w[sel]) / (2 * np.pi) / Ms
            log("   e0 = %.1f, q_B = 2, M = %.2f: %d orbita(s) medias: f22 de %.2f a %.2f Hz ; f22 no 1o ponto %.2f Hz ; media no intervalo %.2f Hz"
                % (pp["e0"], pp["M"], n_orb, fhz.min(), fhz.max(), fhz[1], np.mean(fhz)))
        # fracao do tempo da 1a orbita com f22 < 10 Hz
        sel = t - t[0] <= T_orb
        fhz = np.abs(w[sel]) / (2 * np.pi) / Ms
        log("       fracao do 1o periodo com f22 < 10 Hz: %.2f" % np.mean(fhz < 10.0))
        del t, h
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "rev_R4v_tremor.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
