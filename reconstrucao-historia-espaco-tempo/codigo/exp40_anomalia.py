"""Experimento 40, parte 3 (linha L16, tarefa 4): a memoria carrega a fase radial na fusao?

[H] A dependencia das memorias na anomalia inicial l0 (a e0 fixo na frequencia media de 10 Hz) vem dos ultimos
~100-500 M: e a fase radial com que a binaria chega ao mergulho.
Mede, no SEOBNRv5EHM com as correcoes da L16 (janela desde 10 Hz, multipolos globais m = 0):
  a) para dois sistemas (o A do exp12 e o B (e0 = 0,2, q = 2) do exp12), e0 = 0,02 ... 0,3 e 12 valores de l0:
     desl20, spin30, cm20, giro10, E_janela, M_f (balanco), recuo; amplitude do 1o e 2o harmonicos em l0
     (relativa a media) e lei de potencia em e0; excentricidade residual da dinamica EOB em t = -500 M e -100 M;
     fracao da variacao acumulada depois de t_pico - 100 M (janela desde -100 M);
  b) consistencia interna: o ringdown do modelo usa M_f e chi_f de ajustes quase circulares (independentes de l0),
     mas a energia irradiada varia com l0: a variacao de M_f pelo balanco e a inconsistencia;
  c) controle PN (Peters + quadrupolo newtoniano, so inspiral ate a separatriz p = 6 + 2e): o mesmo com l0 livre.
     Aqui o fim da janela nao depende de l0 (separatriz secular) e o efeito so pode vir das bordas.
Saida: resultados/exp40_anomalia.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp40_comum as C                                 # noqa: E402

SISTEMAS = {"A": (1.2, 0.3, -0.2, 65.0), "B": (2.0, 0.0596, 0.0, 72.5875)}
E0S = (0.02, 0.05, 0.1, 0.2, 0.3)
L0S = tuple(2 * np.pi * k / 12 for k in range(12))
QUANT = ("desl20", "spin30", "cm20", "giro10", "E_janela", "M_f", "recuo")


def um_ponto(arg):
    nome, e0, l0 = arg
    q, c1, c2, M = SISTEMAS[nome]
    t, h, dyn, nu, ts_ = C.gerar(q, c1, c2, M, e0, l0)
    h20 = C.h20_newton(t, dyn, nu, ts_)
    out = {}
    for rot, tw in (("jan10", t[0]), ("ult100", -100.0), ("ult500", -500.0)):
        mem, aux = C.memorias(t, h, tw, dyn, nu, ts_, True, h20)
        out[rot] = dict(desl20=mem["deslocamento"][(2, 0)].real, spin30=-mem["spin"][(3, 0)].imag,
                        cm20=mem["cm"][(2, 0)].real, giro10=mem["giroscopica"][(1, 0)].real,
                        E_janela=aux["E_janela"], M_f=aux["M_f"], recuo=float(np.linalg.norm(aux["recuo"])))
    td = dyn[:, 0] - ts_
    out["e_m500"] = float(np.interp(-500.0, td, dyn[:, 5]))
    out["e_m100"] = float(np.interp(-100.0, td, dyn[:, 5]))
    out["fase_radial_m100"] = float(np.interp(-100.0, td, dyn[:, 6]))
    out["nuH_fim"] = float(nu * dyn[-1, 8])          # energia EOB no fim da dinamica (~t_match), unidades de M
    out["t_fim_dyn"] = float(td[-1])
    del t, h, dyn, h20
    return (nome, e0, l0), out


def harmonicos(y):
    """Amplitudes do 1o e 2o harmonicos de y(l0) (12 pontos uniformes), relativas a media, e resto rms."""
    Y = np.fft.rfft(y) / len(y)
    m = Y[0].real
    a1, a2 = 2 * abs(Y[1]) / abs(m), 2 * abs(Y[2]) / abs(m)
    resto = np.sqrt(np.sum(np.abs(Y[3:]) ** 2) * 2) / abs(m)
    return float(a1), float(a2), float(resto), float(np.angle(Y[1]))


# ------------------------------------------------------------------ controle PN
def pn_memorias(eta, e0, f0, l0, dt=0.5, r_corte=None):
    """Memorias m = 0 (deslocamento l = 2, spin l = 3) do modelo PN newtoniano com anomalia media inicial l0.

    r_corte=None: janela ate a separatriz secular p = 6 + 2e (como pn_excentrico; nao depende de l0).
    r_corte=r_c: janela ate o primeiro instante em que a separacao INSTANTANEA r(t) cai abaixo de r_c (modelo de
    brinquedo de um mergulho disparado pela fase radial); o ultimo subintervalo entra com peso parcial."""
    from scipy.integrate import solve_ivp
    import pn_excentrico as PN
    from memorias import CalculadoraMemoria, gram
    import binarias as B
    n0 = np.pi * f0
    a0 = n0 ** (-2 / 3)
    sol = solve_ivp(PN._rhs, [0, 1e9], [a0, e0, l0], args=(eta,), events=PN._parada, rtol=1e-11, atol=1e-12,
                    dense_output=True, max_step=200.0)
    n = int(np.ceil(sol.t[-1] / dt)) + 1
    t = np.linspace(0, sol.t[-1], n)
    a, e, l = sol.sol(t)
    e = np.maximum(e, 0)
    E = l.copy()
    for _ in range(60):
        E = E - (E - e * np.sin(E) - l) / (1 - e * np.cos(E))
    r = a * (1 - e * np.cos(E))
    v = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    phi = np.unwrap(v)
    dtt = t[1] - t[0]
    w_fim = None
    if r_corte is not None:
        k = int(np.nonzero(r <= r_corte)[0][0])
        tc = t[k - 1] + (r[k - 1] - r_corte) / (r[k - 1] - r[k]) * dtt
        nmax = k + 6
        t, r, phi = t[:nmax], r[:nmax], phi[:nmax]
        # pesos de trapezio de t[0] a tc (subintervalo final parcial por interpolacao linear)
        w_fim = np.zeros(nmax)
        w_fim[:k] = dtt
        w_fim[0] = 0.5 * dtt
        w_fim[k - 1] = 0.5 * dtt
        L = tc - t[k - 1]
        b = L / dtt
        w_fim[k - 1] += 0.5 * L * (2 - b)
        w_fim[k] += 0.5 * L * b
    x = np.stack([r * np.cos(phi), r * np.sin(phi), np.zeros_like(r)], axis=1)
    I = eta * x[:, :, None] * x[:, None, :]
    P = PN._projetores()
    h = {}
    for k, Mk in P.items():
        f = np.einsum("tij,ij->t", I, Mk)
        d2 = np.gradient(np.gradient(f, dtt, edge_order=2), dtt, edge_order=2)
        d2[2:-2] = (-f[4:] + 16 * f[3:-1] - 30 * f[2:-2] + 16 * f[1:-3] - f[:-4]) / (12 * dtt ** 2)
        h[k] = 2 * d2
    L = [(2, 2), (2, -2), (2, 1), (2, -1), (2, 0)]
    H = np.stack([h[k] for k in L], axis=1)
    Hd = B.derivada4(H, dtt)
    if w_fim is None:
        Bm, Am = gram(H, Hd, dtt)
        dur = float(t[-1])
    else:
        import observaveis as O
        Bm, Am = O.gram_pesos(H, Hd, w_fim)
        dur = float(np.sum(w_fim))
    m = CalculadoraMemoria(L, lmax_saida=5).memorias_gram(Bm, Am)
    return dict(desl20=m["deslocamento"][(2, 0)].real, spin30=-m["spin"][(3, 0)].imag,
                E=float(m["energia_total"]), duracao=dur)


def pn_ponto(arg):
    e0, l0 = arg
    from deteccao import MSUN_S
    q, c1, c2, M = SISTEMAS["B"]
    eta = q / (1 + q) ** 2
    f0 = M * MSUN_S * 10.0
    return (e0, l0), dict(secular=pn_memorias(eta, e0, f0, l0), r8=pn_memorias(eta, e0, f0, l0, r_corte=8.0))


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    tarefas = [(n, e0, l0) for n in SISTEMAS for e0 in E0S for l0 in L0S]
    with mp.get_context("spawn").Pool(2) as pool:
        res = dict(pool.map(um_ponto, tarefas, chunksize=4))
        pn = dict(pool.map(pn_ponto, [(e0, l0) for e0 in (0.1, 0.2, 0.3) for l0 in L0S], chunksize=3))
        circ = dict(pool.map(um_ponto, [(n, 0.0, 0.0) for n in SISTEMAS]))
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    log("exp40_anomalia: dependencia das memorias globais (m = 0, janela desde 10 Hz) na anomalia relativistica inicial l0")
    log("amplitude do 1o harmonico em l0 (relativa a media) | 2o harmonico | resto rms ; 12 valores de l0")
    js = dict(SEOB={}, PN={}, circ={})
    for nome in SISTEMAS:
        c0 = circ[(nome, 0.0, 0.0)]
        log()
        log("Sistema %s %s ; circular: desl20 %.5e spin30 %.5e E_jan %.6e M_f %.6f"
            % (nome, SISTEMAS[nome], c0["jan10"]["desl20"], c0["jan10"]["spin30"], c0["jan10"]["E_janela"],
               c0["jan10"]["M_f"]))
        js["circ"][nome] = c0
        for e0 in E0S:
            pts = [res[(nome, e0, l0)] for l0 in L0S]
            linha = []
            ent = {}
            for qn in QUANT:
                y = np.array([p["jan10"][qn] for p in pts])
                a1, a2, rr, fase = harmonicos(y)
                ent[qn] = dict(a1=a1, a2=a2, resto=rr, fase1=fase, media=float(y.mean()), min=float(y.min()),
                               max=float(y.max()), valores=list(map(float, y)))
                if qn in ("desl20", "spin30", "cm20", "giro10", "E_janela", "M_f"):
                    linha.append("%s %.2e|%.1e|%.0e" % (qn, a1, a2, rr))
            # fracao da variacao (pico a pico de desl20) acumulada nos ultimos 100 e 500 M
            y10 = np.array([p["jan10"]["desl20"] for p in pts])
            y100 = np.array([p["ult100"]["desl20"] for p in pts])
            y500 = np.array([p["ult500"]["desl20"] for p in pts])
            fr100 = float(np.std(y100 - y100.mean()) / np.std(y10 - y10.mean()))
            fr500 = float(np.std(y500 - y500.mean()) / np.std(y10 - y10.mean()))
            cor100 = float(np.corrcoef(y100, y10)[0, 1])
            dM = (np.max([p["jan10"]["M_f"] for p in pts]) - np.min([p["jan10"]["M_f"] for p in pts]))
            em5 = np.mean([p["e_m500"] for p in pts])
            em1 = np.mean([p["e_m100"] for p in pts])
            ent.update(frac_ult100=fr100, frac_ult500=fr500, cor_ult100=cor100, dMf_pp=float(dM), e_m500=float(em5),
                       e_m100=float(em1),
                       desl20_rel_circ=float(y10.mean() / c0["jan10"]["desl20"] - 1))
            # de onde vem a variacao de E_janela: energia EOB no fim da dinamica (Nee et al. 2025, eq. 22) e resto
            Ej = np.array([p["jan10"]["E_janela"] for p in pts])
            Hf = np.array([p["nuH_fim"] for p in pts])
            ent["E_jan_pp"] = float(Ej.max() - Ej.min())
            ent["menos_nuHfim_pp"] = float((-Hf).max() - (-Hf).min())
            ent["cor_Ejan_menosHfim"] = float(np.corrcoef(Ej, -Hf)[0, 1])
            ent["resto_ringdown_pp"] = float(np.ptp(Ej + Hf))
            js["SEOB"]["%s_%.2f" % (nome, e0)] = ent
            log("  e0 = %.2f (e_EOB em -500 M %.4f, em -100 M %.4f): %s" % (e0, em5, em1, " ; ".join(linha)))
            log("            E_janela pico a pico %.2e ; -nu H(fim da dinamica) pico a pico %.2e (correlacao %.3f) ;"
                " resto (energia depois do fim da dinamica) pico a pico %.2e"
                % (ent["E_jan_pp"], ent["menos_nuHfim_pp"], ent["cor_Ejan_menosHfim"], ent["resto_ringdown_pp"]))
            log("            variacao de desl20 com l0 vinda dos ultimos 100 M: %.2f (correlacao %.3f), 500 M: %.2f ;"
                " M_f pico a pico %.2e (relativo %.1e) ; media de desl20 - circular %+.2e"
                % (fr100, cor100, fr500, dM, dM / c0["jan10"]["M_f"], ent["desl20_rel_circ"]))
        # lei de potencia em e0 para o 1o harmonico de desl20 e de M_f
        for qn in ("desl20", "spin30", "M_f"):
            a = np.array([js["SEOB"]["%s_%.2f" % (nome, e0)][qn]["a1"] for e0 in E0S])
            p = np.polyfit(np.log(E0S), np.log(a), 1)
            log("  %s: 1o harmonico ~ e0^%.2f (ajuste em e0 = %s) ; a1/e0 = %s"
                % (qn, p[0], E0S, " ".join("%.2e" % (x / e) for x, e in zip(a, E0S))))
    log()
    log("Controle PN (Peters + quadrupolo, so inspiral ate p = 6 + 2e), sistema B (eta de q = 2), desde 10 Hz:")
    for var, rot in (("secular", "fim na separatriz secular p = 6 + 2e"), ("r8", "fim quando r(t) instantaneo < 8 M")):
        log(" %s:" % rot)
        for e0 in (0.1, 0.2, 0.3):
            pts = [pn[(e0, l0)][var] for l0 in L0S]
            ent = {}
            for qn in ("desl20", "spin30", "E", "duracao"):
                y = np.array([p[qn] for p in pts])
                a1, a2, rr, fase = harmonicos(y)
                ent[qn] = dict(a1=a1, a2=a2, resto=rr, media=float(y.mean()), pp=float(y.max() - y.min()))
            js["PN"]["%s_%.2f" % (var, e0)] = ent
            log("  e0 = %.1f: desl20 1o harm. %.2e (2o %.1e) ; spin30 %.2e ; E irradiada %.2e ; duracao media %.0f M"
                " (pico a pico %.1f M)" % (e0, ent["desl20"]["a1"], ent["desl20"]["a2"], ent["spin30"]["a1"],
                                           ent["E"]["a1"], ent["duracao"]["media"], ent["duracao"]["pp"]))
    log()
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "exp40_anomalia.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(C.RES, "exp40_anomalia.json"), "w") as f:
        json.dump(js, f, indent=1, default=float)
