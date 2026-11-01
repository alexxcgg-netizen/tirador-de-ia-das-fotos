"""Experimento 30 (linha L08, agente D5): recuperacao exata da fase de um modo pelos fluxos P e H.

Partes:
 1. Algebra (sympy): udot^2 = 4(uP - H^2), psidot = H/u, P/H = psidot / (1 - adot^2/P).
    Contraexemplo de unicidade: circulo e reta tangente (mesmos P e H).
 2. Estrutura da EDO no substituto (sistema A, modo (2,2)):
    - ponto de retorno t_p = argmax(H^2/P) = argmax|h22| e max(H^2/P) = max|h22|^2;
    - expoente kappa = a psidot^2 / |addot| em t_p (Briot-Bouquet: unicidade pelo ponto de retorno);
    - amplificacao da integracao para frente exp(int 2P/udot) e uma integracao RK de verdade a partir do
      valor exato (diverge); familia de solucoes perturbadas (fogem ou morrem antes do pico);
    - contracao para tras a partir do ponto de retorno com valor inicial errado;
    - sensibilidade a perturbacoes de P e H (suaves e brancas).
 3. Testes (a) P, H do proprio (2,2); (b) P, H dos modos de memoria pelas leis de balanco (nivel A, todos os modos
    oscilatorios); (c) modos m = 0 de RN. Seis sistemas (A e os cinco do exp09). Reconstrucoes adiabatica (o
    Omega_mem do exp09), iteracao e EDO a partir do ponto de retorno. Rede deslocada (t_desloc = 0.37) para A.
Saidas: resultados/exp30_fase_exata.txt, resultados/exp30_fase_exata.json, figuras/e30_fase_exata.png
"""
import json
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np                                        # noqa: E402
import sympy as sp                                        # noqa: E402
from scipy.integrate import solve_ivp                     # noqa: E402
from scipy.interpolate import CubicSpline                 # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp30_comum as C                                   # noqa: E402

linhas = []
res = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


T0 = time.time()
# ====================================================================== 1. algebra
log("== 1. Algebra (sympy)")
a, ad, w_ = sp.symbols("a adot psidot", positive=True)
fase = sp.exp(-sp.I * sp.Symbol("psi", real=True))
hs = a * fase
hds = (ad - sp.I * a * w_) * fase                        # d/dt [a e^{-i psi}]
P = sp.simplify(sp.expand(hds * sp.conjugate(hds)))
Hs = sp.simplify(-sp.im(sp.expand(sp.conjugate(hs) * hds)))
u, udot = a ** 2, 2 * a * ad
r1 = sp.simplify(udot ** 2 - 4 * (u * P - Hs ** 2))
r2 = sp.simplify(Hs / u - w_)
r3 = sp.simplify(P / Hs - w_ / (1 - ad ** 2 / P))
log("  P = %s ; H = %s" % (P, Hs))
log("  udot^2 - 4(uP - H^2) = %s ; H/u - psidot = %s ; P/H - psidot/(1 - adot^2/P) = %s" % (r1, r2, r3))
res["algebra"] = dict(r1=str(r1), r2=str(r2), r3=str(r3))

# contraexemplo: circulo e reta tangente (h2 = h1 ate t = 0, depois a tangente)
tc = np.linspace(-10, 10, 20001)
dtc = tc[1] - tc[0]
w, R0 = 0.7, 1.3
h1 = R0 * np.exp(-1j * w * tc)
h2 = np.where(tc < 0, h1, R0 - 1j * w * R0 * tc)
hd1 = -1j * w * h1
hd2 = np.where(tc < 0, hd1, -1j * w * R0 + 0 * tc)
P1, P2 = np.abs(hd1) ** 2, np.abs(hd2) ** 2
H1, H2 = -np.imag(np.conj(h1) * hd1), -np.imag(np.conj(h2) * hd2)
log("  contraexemplo circulo x tangente: max|P1-P2|/P = %.1e ; max|H1-H2|/H = %.1e ; max|h1-h2| = %.2f (|h| = %.2f)"
    % (np.max(np.abs(P1 - P2)) / P1[0], np.max(np.abs(H1 - H2)) / H1[0], np.max(np.abs(h1 - h2)), R0))
res["contraexemplo_tangente"] = dict(dP=float(np.max(np.abs(P1 - P2)) / P1[0]), dH=float(np.max(np.abs(H1 - H2)) / H1[0]),
                                     dh=float(np.max(np.abs(h1 - h2))))

# ====================================================================== 2. estrutura no substituto
log("")
log("== 2. Estrutura da EDO no modo (2,2) do substituto (sistema A: M=65, q=1.2, chi=(0.3,-0.2), janela 10 Hz)")
t, hh, ti = C.gerar(1.2, 0.3, -0.2)
dt = t[1] - t[0]
sel = (t >= ti - 60) & (t <= C.T_FIM + 30)
t = t[sel]
h = {k: v[sel] for k, v in hh.items()}
del hh
P, H, aa, psid, psi = C.fluxos_modo(h[(2, 2)], dt)
uu = aa ** 2
kp, ub, frac = C.ponto_retorno(P, H)
kpa = int(np.argmax(aa))
y0, y1, y2 = uu[kpa - 1], uu[kpa], uu[kpa + 1]
frac_a = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
log("  argmax(H^2/P) = %.4f M (refinado) ; argmax|h22| = %.4f M ; max(H^2/P)/max|h22|^2 - 1 = %.1e"
    % (t[kp] + frac * dt, t[kpa] + frac_a * dt, ub[kp] / uu[kpa] - 1))
# H^2/P <= |h|^2 em todo instante
dentro = (t > ti) & (t < C.T_FIM)
log("  max (H^2/P - |h|^2)/|h|^2 na janela = %.1e (deve ser <= 0: u_b <= u)" % np.max((ub - uu)[dentro] / uu[dentro]))
add = C.D(C.D(aa, dt), dt)
kappa = aa[kpa] * psid[kpa] ** 2 / abs(add[kpa])
log("  expoente no ponto de retorno kappa = a psidot^2/|addot| = %.1f (a = %.4f, psidot = %.4f, addot/a = %.3e)"
    % (kappa, aa[kpa], psid[kpa], add[kpa] / aa[kpa]))
res["retorno"] = dict(t_ub=float(t[kp] + frac * dt), t_a=float(t[kpa] + frac_a * dt), razao=float(ub[kp] / uu[kpa] - 1),
                      kappa=float(kappa))
# unimodalidade de u_b
dub = np.diff(ub[dentro])
log("  mudancas de sinal de d(H^2/P)/dt na janela (unimodalidade): %d" % int(np.sum(np.diff(np.sign(dub)) != 0)))

# amplificacao da integracao para frente: exp(int 2P/udot)
ud = C.D(uu, dt)
taxa = 2 * P / ud
amp = {}
for t1 in (ti, -3000.0, -300.0, -30.0):
    for t2 in (-100.0, -10.0, -1.0):
        if t2 <= t1:
            continue
        m = (t >= t1) & (t <= t2)
        amp[(t1, t2)] = float(np.sum(taxa[m]) * dt / np.log(10))
log("  log10 da amplificacao exp(int_{t1}^{t2} 2P/udot dt) da integracao para frente:")
for (t1, t2), v in amp.items():
    log("     t1 = %9.1f, t2 = %6.1f: %.3e" % (t1, t2, v))
res["log10_amplificacao"] = {"%g,%g" % k: v for k, v in amp.items()}
k1000 = np.argmin(np.abs(t + 1000))
log("  taxa 2P/udot (1/M): t=-10000 fora; t=-1000: %.2f ; t=-100: %.2f ; t=-10: %.2f ; t=+10: %.2f"
    % (taxa[k1000], taxa[np.argmin(np.abs(t + 100))], taxa[np.argmin(np.abs(t + 10))], taxa[np.argmin(np.abs(t - 10))]))

# integracao RK de verdade, para frente, desde o valor exato (ramo +)
Ps, Hsp = CubicSpline(t, P), CubicSpline(t, H)


def rhs(tq, y, s=1.0):
    v = y[0] * Ps(tq) - Hsp(tq) ** 2
    return [s * 2 * np.sqrt(max(v, 0.0))]


def ev_fronteira(tq, y):
    return y[0] * Ps(tq) - Hsp(tq) ** 2


ev_fronteira.terminal = True
ev_fronteira.direction = -1
log("  integracao para frente (RK45, rtol=atol rel. 1e-13) desde u exato em t1:")
fam = {}
for t1 in (-1000.0, -100.0, -30.0):
    k1 = np.argmin(np.abs(t - t1))
    for nome, fator in (("exato", 1.0), ("+1e-9", 1 + 1e-9), ("-1e-9", 1 - 1e-9)):
        sol = solve_ivp(rhs, (t[k1], 20.0), [uu[k1] * fator], method="RK45", rtol=1e-13, atol=1e-16 * uu[k1],
                        events=ev_fronteira, dense_output=True, max_step=0.05)
        tf = sol.t[-1]
        ug = np.interp(sol.t, t, uu)
        dev = np.abs(sol.y[0] / ug - 1)
        jj = np.nonzero(dev > 1e-2)[0]
        t_dev = sol.t[jj[0]] if len(jj) else np.nan
        morreu = len(sol.t_events[0]) > 0
        fam[(t1, nome)] = dict(t_desvio_1pct=float(t_dev), t_fim=float(tf), morreu=bool(morreu),
                               u_fim_rel=float(sol.y[0][-1] / np.interp(tf, t, uu)))
        log("     t1 = %7.1f, inicio %-6s: desvio > 1%% em t = %8.2f M ; fim em t = %7.2f (%s) ; u/u_verdadeiro no fim = %.3g"
            % (t1, nome, t_dev, tf, "atinge u = H^2/P: sem continuacao real" if morreu else "chega a t = 20",
               fam[(t1, nome)]["u_fim_rel"]))
        if t1 == -30.0:
            fam[(t1, nome)]["serie"] = (sol.t, sol.y[0])
res["familia"] = {"%g %s" % k: {kk: vv for kk, vv in v.items() if kk != "serie"} for k, v in fam.items()}

# contracao para tras a partir do ponto de retorno com valor inicial errado
log("  integracao para tras (trapezio implicito) desde o ponto de retorno com u(t_p) errado:")
ref, _, _ = C.edo_retorno(t, P, H)
contr = {}
for delta in (+1e-3, -1e-3, +1e-1):
    u2, _, ncl = C.edo_retorno(t, P, H, u_inicial=ub[kp] * (1 + delta))
    partes = []
    for tq in (-0.25, -0.5, -1.0, -2.0, -5.0, 0.25, 1.0, 5.0):
        k = np.argmin(np.abs(t - tq))
        partes.append("t=%+.2f: %.1e" % (tq, u2[k] / ref[k] - 1))
        contr["%g,%g" % (delta, tq)] = float(u2[k] / ref[k] - 1)
    log("     delta = %+.0e: desvio relativo de u: " % delta + " ; ".join(partes) + " (clip %d)" % ncl)
res["contracao"] = contr

# sensibilidade a perturbacoes de P e H
log("  sensibilidade: P -> P(1+dP), H -> H(1+dH); erro relativo de psidot (rms na janela ate t_p+60):")
rng = np.random.default_rng(30)
jan = (t > ti + 20) & (t < C.T_FIM)
sens = {}
for tipo in ("suave", "branca"):
    if tipo == "suave":
        def pert():
            x = np.zeros(len(t))
            for _ in range(20):
                per = np.exp(rng.uniform(np.log(50), np.log(2000)))
                x += np.sin(2 * np.pi * t / per + rng.uniform(0, 2 * np.pi))
            return 1e-3 * x / np.sqrt(np.mean(x ** 2))
    else:
        def pert():
            return 1e-6 * rng.standard_normal(len(t))
    dP, dH = pert(), pert()
    Pn, Hn = P * (1 + dP), H * (1 + dH)
    e_in = np.sqrt(np.mean((dP - dH)[jan] ** 2))
    ead = C.adiabatica(Pn, Hn) / psid - 1
    un, _, ncl = C.edo_retorno(t, Pn, Hn)
    eod = (Hn / un) / psid - 1
    eod0 = (H / ref) / psid - 1
    sens[tipo] = dict(rms_entrada=float(e_in), rms_adiab=float(np.sqrt(np.mean((ead - (P / H / psid - 1))[jan] ** 2))),
                      rms_edo=float(np.sqrt(np.mean((eod - eod0)[jan] ** 2))), clip=ncl)
    log("     %-6s: rms(dP - dH) = %.2e ; variacao rms do adiabatico %.2e ; da EDO %.2e (clip %d)"
        % (tipo, e_in, sens[tipo]["rms_adiab"], sens[tipo]["rms_edo"], ncl))
res["sensibilidade"] = sens
# escala: dados (lambda P, mu H) tambem admitem solucao pelo ponto de retorno (ambiguidade de um observador com iota
# desconhecido: h+ e hx medidos a menos de fatores angulares diferentes)
log("  escala: P -> lambda P, H -> mu H (fatores angulares desconhecidos); a EDO reconstroi psidot' / psidot:")
esc = {}
for lam, mu in ((1.1, 1.0), (1.0, 1.1), (1.21, 1.1), (0.8, 1.0)):
    u3, _, ncl = C.edo_retorno(t, lam * P, mu * H)
    r = (mu * H / u3) / psid
    partes = []
    for rn, m in C.regioes(t, ti, 0.0).items():
        partes.append("%s: mediana %.5f [%.5f, %.5f]" % (rn.split(" (")[0], np.median(r[m]), np.min(r[m]), np.max(r[m])))
    esc["%g,%g" % (lam, mu)] = dict(clip=ncl, med_insp=float(np.median(r[C.regioes(t, ti, 0.0)["inspiral (t_i+20, t_p-200)"]])))
    log("     lambda = %.2f, mu = %.2f (lambda/mu = %.4f; clip %d): " % (lam, mu, lam / mu, ncl) + " | ".join(partes))
res["escala"] = esc
fig_A = dict(t=t, ub=ub, uu=uu, fam={k: v["serie"] for k, v in fam.items() if "serie" in v}, psid=psid,
             e_ad=P / H / psid - 1, e_edo=(H / ref) / psid - 1)
del h

# ====================================================================== 3. testes (a), (b), (c)
log("")
log("== 3. Testes (a) P, H do (2,2) ; (b) dos modos de memoria (nivel A, leis de balanco) ; (c) modos m = 0 de RN")
log("   erros relativos de psidot = 2 Omega contra a frequencia verdadeira do (2,2): mediana / maximo por regiao")
SIST = [("A (10 Hz)", dict(q=1.2, c1=0.3, c2=-0.2)), ("A rede deslocada 0.37", dict(q=1.2, c1=0.3, c2=-0.2, t_desloc=0.37)),
        ("q=1", dict(q=1.0, c1=0.0, c2=0.0, f0=0.006)), ("q=2", dict(q=2.0, c1=0.0, c2=0.0, f0=0.006)),
        ("q=4", dict(q=4.0, c1=0.0, c2=0.0, f0=0.006)), ("q=1 chi=(0.6,0.6)", dict(q=1.0, c1=0.6, c2=0.6, f0=0.006)),
        ("q=3 chi=(0.6,0)", dict(q=3.0, c1=0.6, c2=0.0, f0=0.006))]
res["testes"] = {}
fig_b = None
for nome, par in SIST:
    t0 = time.time()
    t, hh, ti = C.gerar(par["q"], par["c1"], par["c2"], t_desloc=par.get("t_desloc", 0.0), f0=par.get("f0"))
    sel = (t >= ti - 60) & (t <= C.T_FIM + 30)
    t = t[sel]
    h = {k: v[sel] for k, v in hh.items()}
    del hh
    dt = t[1] - t[0]
    P, H, aa, psid, psi = C.fluxos_modo(h[(2, 2)], dt)
    tpk = t[np.argmax(aa)]
    Pb, Hb, _, _ = C.fluxos_memoria(t, h)
    Pc, Hc = C.fluxos_rn(t, h)
    Pb2, Hb2, _, _ = C.fluxos_memoria(t, h, so22=True)
    out = dict(t_i=float(ti), consist_so22=dict(P=float(np.max(np.abs(Pb2 / P - 1)[(t > ti) & (t < C.T_FIM)])),
                                                 H=float(np.max(np.abs(Hb2 / H - 1)[(t > ti) & (t < C.T_FIM)]))))
    log("")
    log("  %s: t_i = %.1f M ; consistencia (fluxos so de (2,+-2)): max|P_mem/P - 1| = %.1e, max|H_mem/H - 1| = %.1e"
        % (nome, ti, out["consist_so22"]["P"], out["consist_so22"]["H"]))
    reg = C.regioes(t, ti, tpk)
    reg.update(C.regioes_exp09(t, tpk))
    for fonte, (PP, HH) in (("a", (P, H)), ("b", (Pb, Hb)), ("c", (Pc, Hc))):
        o = {}
        psid_ad = C.adiabatica(PP, HH)
        dom = t <= tpk + C.T_FIM                      # a iteracao e global: fora daqui H < 0 contamina (nan)
        m_it = ((t > ti) & (t < tpk - 5))[dom]
        psid_it = np.full(len(t), np.nan)
        psid_it[dom], hist = C.iteracao(PP[dom], HH[dom], dt, n=40, mascara=m_it)
        m_dep = ((t > tpk + 2) & (t < tpk + 30))[dom]
        psid_it2, hist_dep = C.iteracao(PP[dom], HH[dom], dt, n=40, mascara=m_dep)
        psid_itd = np.full(len(t), np.nan)
        psid_itd[dom] = psid_it2
        uo, kpo, ncl = C.edo_retorno(t, PP, HH)
        psid_edo = HH / uo
        o["t_p"] = float(t[kpo])
        o["clip"] = int(ncl)
        o["iter_conv"] = hist[:8]
        o["iter_pos_pico"] = hist_dep[:8] + hist_dep[-1:]
        for rn, m in reg.items():
            o[rn] = dict(adiab=C.erro_rel(psid_ad, psid, m), edo=C.erro_rel(psid_edo, psid, m),
                         iter=C.erro_rel(psid_itd, psid, m) if np.all(np.isfinite(psid_itd[m])) else None,
                         ampl_adiab=C.erro_rel(np.sqrt(HH ** 2 / PP), aa, m), ampl_edo=C.erro_rel(np.sqrt(uo), aa, m))
        # fase acumulada desde t_i e sobreposicao do (2,2) reconstruido (so fase constante livre)
        fv = C.fase_acumulada(psid, t, ti, dt)
        kpk = np.argmin(np.abs(t - tpk))
        k30 = np.argmin(np.abs(t - tpk - 30))
        jan = (t >= ti) & (t <= tpk + 30)
        janI = (t >= ti) & (t <= tpk - 200)
        for rec, ps_r, a_r in (("adiab", psid_ad, np.sqrt(np.abs(HH ** 2 / PP))), ("edo", psid_edo, np.sqrt(uo))):
            fr = C.fase_acumulada(ps_r, t, ti, dt)
            o["fase_" + rec] = dict(no_pico=float(fr[kpk] - fv[kpk]), em_30=float(fr[k30] - fv[k30]),
                                    total_pico=float(fv[kpk]))
            hrec = a_r * np.exp(-1j * fr)
            hver = aa * np.exp(-1j * fv)
            o["overlap_" + rec] = dict(ate_30=C.overlap_fase(hrec[jan], hver[jan]),
                                       inspiral=C.overlap_fase(hrec[janI], hver[janI]))
        res_l = []
        for rn in reg:
            r = o[rn]
            res_l.append("%s: adiab %.1e/%.1e edo %.1e/%.1e%s" % (
                rn.split(" (")[0], r["adiab"][0], r["adiab"][1], r["edo"][0], r["edo"][1],
                (" iter %.1e/%.1e" % tuple(r["iter"])) if r["iter"] else ""))
        log("   (%s) t_p = %.2f, clip %d | " % (fonte, o["t_p"], o["clip"]) + " | ".join(res_l))
        log("        fase acumulada desde t_i (verdadeira %.1f rad ate o pico): erro no pico adiab %+.3f, edo %+.3f rad ;"
            " em t_p+30: adiab %+.3f, edo %+.3f | sobreposicao (fase livre) ate t_p+30: adiab %.5f, edo %.5f ;"
            " so inspiral: adiab %.5f, edo %.5f"
            % (o["fase_adiab"]["total_pico"], o["fase_adiab"]["no_pico"], o["fase_edo"]["no_pico"],
               o["fase_adiab"]["em_30"], o["fase_edo"]["em_30"], o["overlap_adiab"]["ate_30"],
               o["overlap_edo"]["ate_30"], o["overlap_adiab"]["inspiral"], o["overlap_edo"]["inspiral"]))
        log("        amplitude |h22|: erro rel. mediano/max fim da inspiral: adiab %.1e/%.1e edo %.1e/%.1e ; pos-pico: adiab %.1e/%.1e edo %.1e/%.1e"
            % (*o["fim da inspiral (t_p-200, t_p)"]["ampl_adiab"], *o["fim da inspiral (t_p-200, t_p)"]["ampl_edo"],
               *o["pos-pico (t_p, t_p+30)"]["ampl_adiab"], *o["pos-pico (t_p, t_p+30)"]["ampl_edo"]))
        log("        iteracao: maior variacao relativa por passo antes do pico %s ; depois do pico (t_p+2, t_p+30) %s"
            % (" ".join("%.0e" % x for x in hist[:6]), " ".join("%.0e" % x for x in hist_dep[:6]) + " ... %.0e (passo 40)" % hist_dep[-1]))
        out[fonte] = o
        if nome == "A (10 Hz)":
            if fig_b is None:
                fig_b = dict(t=t - tpk, psid=psid)
            fig_b[fonte] = dict(ad=psid_ad, edo=psid_edo, fase_ad=C.fase_acumulada(psid_ad, t, ti, dt) - fv,
                                fase_edo=C.fase_acumulada(psid_edo, t, ti, dt) - fv)
    del h
    res["testes"][nome] = out
    log("   (%.0f s)" % (time.time() - t0))


def limpa(x):
    if isinstance(x, dict):
        return {str(k): limpa(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [limpa(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    return x


with open(os.path.join(C.RES, "exp30_fase_exata.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(C.RES, "exp30_fase_exata.json"), "w") as f:
    json.dump(limpa(res), f, indent=1)

# ====================================================================== figura
import matplotlib                                         # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                           # noqa: E402
C.estilo(plt)
fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.2))
# (1) ponto de retorno e familia
x = ax[0, 0]
t = fig_A["t"]
m = (t > -40) & (t < 12)
x.plot(t[m], fig_A["uu"][m], color=C.COR["texto"], lw=2.4, label="u = |h22|² verdadeiro")
x.plot(t[m], fig_A["ub"][m], color=C.COR["verde"], lw=1.2, ls="--", label="fronteira H²/P (u ≥ H²/P)")
for (t1, nome), (ts, us) in fig_A["fam"].items():
    if nome == "exato":
        continue
    mm = ts < 12
    x.plot(ts[mm], us[mm], color=C.COR["laranja"] if nome.startswith("+") else C.COR["azul"], lw=1.0,
           label="para frente desde t = -30 M com u x (1 %s 1e-9)" % nome[0])
x.axvline(0, color=C.COR["cinza"], lw=0.6)
x.set_ylim(0, 0.2)
x.set_xlabel("t - t_pico (M)")
x.set_ylabel("u = a²")
x.set_title("Ponto de retorno: só a solução verdadeira chega ao pico", loc="left", fontsize=9)
x.legend(frameon=False, fontsize=6.5, loc="lower left")
# (2) erro do adiabatico e da EDO, P e H exatos
x = ax[0, 1]
m = (t > -3000) & (t < 60)
x.semilogy(t[m], np.abs(fig_A["e_ad"][m]), color=C.COR["laranja"], lw=1.0, label="adiabático P/H (Ω = P/2H)")
x.semilogy(t[m], np.abs(fig_A["e_edo"][m]) + 1e-16, color=C.COR["azul"], lw=1.0, label="EDO a partir do ponto de retorno")
x.set_xlabel("t - t_pico (M)")
x.set_ylabel("|ψ̇ reconstruída / ψ̇ verdadeira − 1|")
x.set_title("(a) P e H do próprio (2,2): a EDO é exata até o toque", loc="left", fontsize=9)
x.set_ylim(1e-12, 1)
x.legend(frameon=False, fontsize=7)
# (3) Omega de memoria perto da fusao
x = ax[1, 0]
tb = fig_b["t"]
m = (tb > -300) & (tb < 40)
x.plot(tb[m], 0.5 * fig_b["psid"][m], color=C.COR["texto"], lw=2.4, label="Ω verdadeira (fase do 2,2)")
x.plot(tb[m], 0.5 * fig_b["b"]["edo"][m], color=C.COR["azul"], lw=1.1, label="(b) leis de balanço, EDO")
x.plot(tb[m], 0.5 * fig_b["b"]["ad"][m], color=C.COR["azul"], lw=0.8, ls=":", label="(b) adiabático (exp09)")
x.plot(tb[m], 0.5 * fig_b["c"]["edo"][m], color=C.COR["laranja"], lw=1.1, label="(c) modos m = 0 de RN, EDO")
x.set_ylim(0, 0.4)
x.set_xlabel("t - t_pico (M)")
x.set_ylabel("Ω (1/M)")
x.set_title("Sistema A: Ω pelos modos de memória", loc="left", fontsize=9)
x.legend(frameon=False, fontsize=7)
# (4) erro de fase acumulado
x = ax[1, 1]
m = (tb > tb[0] + 60) & (tb < 30)
for fonte, cor, rot in (("a", C.COR["verde"], "(a) P, H do (2,2)"), ("b", C.COR["azul"], "(b) leis de balanço"),
                        ("c", C.COR["laranja"], "(c) RN")):
    x.plot(tb[m], fig_b[fonte]["fase_edo"][m], color=cor, lw=1.2, label=rot + ", EDO")
    x.plot(tb[m], fig_b[fonte]["fase_ad"][m], color=cor, lw=0.8, ls=":", label=rot + ", adiabático")
x.set_xlabel("t - t_pico (M)")
x.set_ylabel("erro da fase do (2,2) desde 10 Hz (rad)")
x.set_title("Fase acumulada: o erro vem dos fluxos, não da aproximação adiabática", loc="left", fontsize=9)
x.legend(frameon=False, fontsize=6.5)
fig.tight_layout()
fig.savefig(os.path.join(C.FIG, "e30_fase_exata.png"), dpi=140)
log("tempo total %.0f s" % (time.time() - T0))
with open(os.path.join(C.RES, "exp30_fase_exata.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
