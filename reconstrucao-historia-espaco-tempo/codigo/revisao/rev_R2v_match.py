"""Verificacao independente (R2v) dos itens 3, 4 e 5 da revisao R2: o match de deteccao.comparar.

Referencia independente ('ouro'), sem reaproveitar rev_R2_comum:
  - a onda e gerada desde f_22 = 5 Hz (e nao 10 Hz) direto na grade de 1/4096 s (dt do substituto em M
    escolhido para isso, sem reamostragem linear); o inicio e levado a zero por cosseno ate f_22 = 7 Hz,
    de modo que a banda f >= 10 Hz (inclusive os modos (3,3) e (4,4)) nao ve o corte;
  - modos m = 0: menos o valor inicial; o valor final e mantido 4 s e levado a zero por cosseno de 8 s;
  - maximizacao no tempo continua: pico da correlacao com zero padding x4 e refinamento por
    minimize_scalar de |sum W(f) e^{2 pi i f tau}| (a fase sai do modulo).
Tambem a decomposicao do artefato do exp07 (ondas desde 10 Hz em dt = 0.25 M, como no exp07):
  base (deteccao.comparar) ; so busca fina no tempo ; so cosseno de 0.5 s no inicio ; so rampa no fim dos
  m = 0 ; os tres juntos (como R2). A busca fina aqui e a continua (nao a x16 do R2).
Casos: membros da familia de A com chi2_B = -0.2 (q_B = 1.15, 1.19, 1.25, resolvidos de novo como no R2);
exp13 (q = 1, chi_s = +0.3, d = 0.1, 0.2, 0.3; chi_s = -0.5, d = 0.2); pares (1, 0) e (2, 0) do exp07.
AVISO (achado depois, em rev_R2v_match2/3): a coluna OURO deste script NAO e autoconsistente. O gwsurrogate
zera a fase orbital em f_ref = f_low; com inicio em 5 Hz, A e B ficam com fases orbitais zeradas em 5 Hz e, num
observador fixo, a mistura dos modos m != 2 muda (A contra A com inicio 5.0 e 5.3 Hz: 1 - match 2.5e-3). O ouro
correto, com f_ref = 10 Hz como no exp07, esta em rev_R2v_match3.py. A decomposicao base / busca fina / cosseno /
rampa / os tres (ondas desde 10 Hz) continua valida.
Saida: resultados/revisao/rev_R2v_match.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
FS = 4096.0
DTS = 1.0 / FS
FMIN = 10.0
LISTA = B.lista_osc() + B.MODOS_M0
linhas = []
_psd = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def psd(n, df):
    k = (n, round(df, 15))
    if k not in _psd:
        _psd.clear()
        _psd[k] = Dt.psd_serie("aLIGO", n, df, FMIN)
    return _psd[k]


def produto_fino(a, b, dt=DTS, up=4):
    """(a|a), (b|b) e match (h_+), maximizado na fase e no tempo continuo."""
    n = 1
    while n < 2 * max(len(a), len(b)):
        n *= 2
    Af = np.fft.rfft(a.real, n) * dt
    Bf = np.fft.rfft(b.real, n) * dt
    f = np.fft.rfftfreq(n, dt)
    df = f[1] - f[0]
    Sn = psd(len(f), df)
    ok = f >= FMIN
    aa = 4 * np.sum(np.abs(Af[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(Bf[ok]) ** 2 / Sn[ok]) * df
    W = np.where(ok, Af * np.conj(Bf) / Sn, 0)
    N = n * up
    integ = np.zeros(N, dtype=complex)
    integ[:len(f)] = W
    serie = np.abs(np.fft.ifft(integ)) * N
    m = int(np.argmax(serie))
    tau0 = (m if m < N // 2 else m - N) * dt / up
    fk, Wk = f[ok], W[ok]

    def g(tau):
        return -np.abs(np.sum(Wk * np.exp(2j * np.pi * fk * tau)))

    r = minimize_scalar(g, bounds=(tau0 - dt / up, tau0 + dt / up), method="bounded",
                        options=dict(xatol=1e-6 * dt))
    gm = max(-r.fun, serie[m])
    return aa, bb, float(4 * df * gm / np.sqrt(aa * bb))


def ouro(par):
    """Serie h_+ - i h_x (1/4096 s) desde 5 Hz, cosseno ate 7 Hz, m = 0 com rampa. Sem reamostragem."""
    dtM = DTS / (par["M"] * Dt.MSUN_S)
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * 5.0, dt=dtM)
    _, osc = Dt.strain_observador(t, h, B.lista_osc(), par["M"], par["D"], par["iota"])
    _, m0 = Dt.strain_observador(t, h, B.MODOS_M0, par["M"], par["D"], par["iota"])
    fase = np.unwrap(np.angle(h[(2, 2)]))
    f22 = np.abs(np.gradient(fase, t)) / (2 * np.pi) / (par["M"] * Dt.MSUN_S)
    del t, h
    k7 = int(np.argmax(f22 > 7.0))
    w = np.ones(len(osc))
    w[:k7] = 0.5 * (1 - np.cos(np.pi * np.arange(k7) / k7))
    m0 = (m0 - m0[0]) * w
    n_hold, n_rampa = int(4 * FS), int(8 * FS)
    rampa = m0[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
    m0 = np.concatenate([m0, np.full(n_hold, m0[-1]), rampa])
    osc = np.concatenate([osc * w, np.zeros(n_hold + n_rampa)])
    return osc + m0, osc


def exp07_serie(par):
    """Strain no observador desde 10 Hz em dt = 0.25 M (como no exp07)."""
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * 10.0, dt=0.25)
    ts, s = Dt.strain_observador(t, h, LISTA, par["M"], par["D"], par["iota"])
    del t, h
    return ts, s


def tratar(ts, s, taper=0.0, rampa=False):
    """Reamostra como deteccao.comparar (alinhado pelo pico) e aplica as variantes."""
    _, x = Dt._reamostrar(ts - ts[np.argmax(np.abs(s))], s, DTS)
    if rampa:
        # so a parte m = 0 tem valor final nao nulo: subtrai a constante inicial e leva o valor final a zero
        x = x - x[0]
        n_hold, n_rampa = int(4 * FS), int(8 * FS)
        r = x[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
        x = np.concatenate([x, np.full(n_hold, x[-1]), r])
    if taper > 0:
        n = int(taper * FS)
        w = np.ones(len(x))
        w[:n] = 0.5 * (1 - np.cos(np.pi * np.arange(n) / n))
        x = x * w
    return x


def caso(nome, pA, pB, sA07, oA):
    tsB, sB = exp07_serie(pB)
    base = Dt.comparar(sA07[0], sA07[1], tsB, sB, "aLIGO", fmin=FMIN)["+"]["match"]
    xa0, xb0 = tratar(*sA07), tratar(tsB, sB)
    fino = produto_fino(xa0, xb0)[2]
    tap = produto_fino(tratar(*sA07, taper=0.5), tratar(tsB, sB, taper=0.5))[2]
    ram = produto_fino(tratar(*sA07, rampa=True), tratar(tsB, sB, rampa=True))[2]
    tud = produto_fino(tratar(*sA07, taper=0.5, rampa=True), tratar(tsB, sB, taper=0.5, rampa=True))[2]
    del tsB, sB, xa0, xb0
    oB = ouro(pB)
    aa, bb, mo = produto_fino(oA[0], oB[0])
    mo_osc = produto_fino(oA[1], oB[1])[2]
    del oB
    rc = 1 / np.sqrt(2 * (1 - mo))
    log("  %-28s 1-match: base %.3e | so busca fina %.3e | so cosseno 0.5 s %.3e | so rampa m=0 %.3e | os tres %.3e"
        " || OURO %.3e (rho_crit %.1f ; SNR_A %.1f SNR_B %.1f) ; ouro so osc. %.3e"
        % (nome, 1 - base, 1 - fino, 1 - tap, 1 - ram, 1 - tud, 1 - mo, rc, np.sqrt(aa), np.sqrt(bb), 1 - mo_osc))
    return 1 - base, 1 - tud, 1 - mo


if __name__ == "__main__":
    t_ini = time.time()
    dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
    A, alvo = dados["A"], dados["alvo"]

    log("AVISO: a coluna OURO abaixo tem a fase orbital zerada em 5 Hz (f_ref = f_low) e nao e autoconsistente; "
        "ver rev_R2v_match3.txt (ouro com f_ref = 10 Hz). As outras colunas valem.")
    log("Item 4: degraus dos modos m = 0 de A (h_20 adimensional no inicio da janela de 10 Hz e no fim):")
    t, h = B.gerar(A["q"], A["c1"], A["c2"], f0=A["M"] * Dt.MSUN_S * 10.0)
    log("  h20: %.4f -> %.4f ; h40: %.5f -> %.5f" % (h[(2, 0)][0].real, h[(2, 0)][-1].real, h[(4, 0)][0].real,
                                                    h[(4, 0)][-1].real))
    ts, s = Dt.strain_observador(t, h, B.MODOS_M0, A["M"], A["D"], A["iota"])
    del t, h
    x = tratar(ts, s)
    xr = tratar(ts, s, rampa=True)
    log("  SNR (aLIGO) da parte m = 0 de h_+: sem tratamento (como no comparar) %.3f ; com valor inicial subtraido e "
        "rampa %.3f ; razao %.2f" % (np.sqrt(produto_fino(x, x)[0]), np.sqrt(produto_fino(xr, xr)[0]),
                                     np.sqrt(produto_fino(x, x)[0] / produto_fino(xr, xr)[0])))
    xs = x - x[0]
    log("  so com o valor inicial subtraido (sem rampa): %.3f" % np.sqrt(produto_fino(xs, xs)[0]))
    del ts, s, x, xr, xs

    sA07 = exp07_serie(A)
    oA = ouro(A)
    log("")
    log("Itens 3 e 4: membros da familia de A (chi2_B = -0.2, mesmas 4 memorias no nivel A), aLIGO, h_+.")
    dqs, mb, mt, mo = [], [], [], []
    for qB in (1.15, 1.19, 1.25):
        pB, r = E7.resolver(alvo, qB, -0.2, (A["iota"], 0.3, 65.0))
        log("  q_B %.2f: M %.4f chi1 %+.5f D %.3f iota %.3f graus | residuo %.1e (%.0f s)"
            % (qB, pB["M"], pB["c1"], pB["D"], np.degrees(pB["iota"]), r, time.time() - t_ini))
        b, tt, o = caso("familia q_B %.2f" % qB, A, pB, sA07, oA)
        dqs.append(abs(qB - 1.2))
        mb.append(b)
        mt.append(tt)
        mo.append(o)
    dq = np.array(dqs)
    for nome, y in (("base", mb), ("os tres (R2)", mt), ("ouro", mo)):
        p = np.polyfit(np.log(dq[[0, 1]]), np.log(np.array(y)[[0, 1]]), 1)
        log("  expoente em dq (q_B 1.15 e 1.19) %-12s: %.2f ; coef. %.3g ; |dq| nao separado na SNR 66: %.4f"
            % (nome, p[0], np.exp(p[1]), (1 / (2 * 66.0 ** 2) / np.exp(p[1])) ** (1 / p[0])))
    log("  (%.0f s)" % (time.time() - t_ini))
    del sA07, oA

    log("")
    log("Item 5: exp13 (q = 1, M = 65, D = 400 Mpc, iota = 50 graus), B = (chi_s + d, chi_s - d) contra A = (chi_s, chi_s).")
    for chi_s, ds in ((0.3, (0.1, 0.2, 0.3)), (-0.5, (0.2,))):
        pA = dict(M=65.0, q=1.0, c1=chi_s, c2=chi_s, D=400.0, iota=np.radians(50.0))
        sA = exp07_serie(pA)
        oAq = ouro(pA)
        ys = []
        for d in ds:
            pB = dict(pA, c1=chi_s + d, c2=chi_s - d)
            _, _, o = caso("chi_s %+.1f d %.1f" % (chi_s, d), pA, pB, sA, oAq)
            ys.append(o)
        if len(ds) > 1:
            log("  chi_s %+.1f: expoente local do ouro em d: %s ; rho_crit * d (ouro): %s"
                % (chi_s, " ".join("%.2f" % (np.log(ys[i + 1] / ys[i]) / np.log(ds[i + 1] / ds[i])) for i in range(len(ds) - 1)),
                   " ".join("%.1f" % (d / np.sqrt(2 * y)) for d, y in zip(ds, ys))))
        del sA, oAq
    log("  (%.0f s)" % (time.time() - t_ini))

    log("")
    log("Item 4: pares do exp07 (o artefato pesa nos numeros da tabela do 07 §3.3?).")
    sA07 = exp07_serie(A)
    oA = ouro(A)
    for p in dados["pares"]:
        if (p["qB"], p["c2B"]) in ((1.0, 0.0), (2.0, 0.0)):
            pB = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
            b, tt, o = caso("par (%.0f, %+.1f)" % (p["qB"], p["c2B"]), A, pB, sA07, oA)
            log("     rho_crit: base %.2f ; ouro %.2f" % (1 / np.sqrt(2 * b), 1 / np.sqrt(2 * o)))
    log("  (%.0f s)" % (time.time() - t_ini))
    with open(os.path.join(RES, "revisao", "rev_R2v_match.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
