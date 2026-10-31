"""Verificacao (R2v), continuacao de rev_R2v_match.py: por que o 'ouro' e o match tratado do R2 discordam
nos membros da familia de A (q_B = 1.19: ouro 7.7e-4 contra 1.7e-4)?

1) Autoconsistencia do ouro: A contra A com outra frequencia de inicio (5.0 contra 5.3 Hz; cosseno ate 7 Hz):
   o 1 - match deve ser ~0.
2) Convergencia do ouro na frequencia de inicio: q_B = 1.19 com inicio/fim do cosseno em (5, 7), (7, 8.5),
   (8, 9.3) e (9.5, 9.9) Hz, e com a onda desde 10 Hz e cosseno de 0.5 s (R2).
3) Banda: ouro e o tratamento do R2 com f_min = 10, 15 e 25 Hz (se a diferenca vem da banda perto de 10 Hz,
   que a onda truncada em 10 Hz nao contem por inteiro, as duas devem concordar com f_min alto).
4) Lei de escala do ouro na familia: q_B = 1.15, 1.18, 1.19, 1.195, 1.205, 1.21, 1.22, 1.25 (chi2_B = -0.2).
RESULTADO do item 1: o ouro com f_ref = f_low = 5 Hz NAO e autoconsistente (2.5e-3): a fase orbital zerada no
inicio muda a mistura dos modos m != 2 no observador. Por isso a coluna 'ouro' dos itens 2 a 4 deste script nao
serve de referencia; o ouro correto (f_ref = 10 Hz, como no exp07) esta em rev_R2v_match3.py.
Saida: resultados/revisao/rev_R2v_match2.txt
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp07_binarias_observador as E7                  # noqa: E402
import rev_R2v_match as RM                              # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
FS, DTS = RM.FS, RM.DTS
linhas = []
_psd = {}


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def psd(n, df, fmin):
    k = (n, round(df, 15), fmin)
    if k not in _psd:
        if len(_psd) > 3:
            _psd.clear()
        _psd[k] = Dt.psd_serie("aLIGO", n, df, fmin)
    return _psd[k]


def match(a, b, fmin=10.0, up=4, n_min=0):
    """Como RM.produto_fino, com f_min livre. Devolve 1 - match."""
    n = 1
    while n < max(2 * max(len(a), len(b)), n_min):
        n *= 2
    Af = np.fft.rfft(a.real, n) * DTS
    Bf = np.fft.rfft(b.real, n) * DTS
    f = np.fft.rfftfreq(n, DTS)
    df = f[1] - f[0]
    Sn = psd(len(f), df, fmin)
    ok = f >= fmin
    aa = 4 * np.sum(np.abs(Af[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(Bf[ok]) ** 2 / Sn[ok]) * df
    W = np.where(ok, Af * np.conj(Bf) / Sn, 0)
    N = n * up
    integ = np.zeros(N, dtype=complex)
    integ[:len(f)] = W
    serie = np.abs(np.fft.ifft(integ)) * N
    m = int(np.argmax(serie))
    tau0 = (m if m < N // 2 else m - N) * DTS / up
    fk, Wk = f[ok], W[ok]
    r = minimize_scalar(lambda tau: -np.abs(np.sum(Wk * np.exp(2j * np.pi * fk * tau))),
                        bounds=(tau0 - DTS / up, tau0 + DTS / up), method="bounded", options=dict(xatol=1e-6 * DTS))
    return 1 - float(4 * df * max(-r.fun, serie[m]) / np.sqrt(aa * bb))


def ouro2(par, f_ini=5.0, f_tap=7.0):
    """Como RM.ouro, com frequencia de inicio e fim do cosseno livres."""
    dtM = DTS / (par["M"] * Dt.MSUN_S)
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * f_ini, dt=dtM)
    _, osc = Dt.strain_observador(t, h, B.lista_osc(), par["M"], par["D"], par["iota"])
    _, m0 = Dt.strain_observador(t, h, B.MODOS_M0, par["M"], par["D"], par["iota"])
    fase = np.unwrap(np.angle(h[(2, 2)]))
    f22 = np.abs(np.gradient(fase, t)) / (2 * np.pi) / (par["M"] * Dt.MSUN_S)
    del t, h
    k = int(np.argmax(f22 > f_tap))
    w = np.ones(len(osc))
    if k > 0:
        w[:k] = 0.5 * (1 - np.cos(np.pi * np.arange(k) / k))
    m0 = (m0 - m0[0]) * w
    n_hold, n_rampa = int(4 * FS), int(8 * FS)
    rampa = m0[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
    m0 = np.concatenate([m0, np.full(n_hold, m0[-1]), rampa])
    osc = np.concatenate([osc * w, np.zeros(n_hold + n_rampa)])
    return osc + m0


def r2(par):
    """Tratamento do R2: onda desde 10 Hz (dt 0.25 M), cosseno de 0.5 s, rampa nos m = 0."""
    ts, s = RM.exp07_serie(par)
    return RM.tratar(ts, s, taper=0.5, rampa=True)


if __name__ == "__main__":
    t0 = time.time()
    dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
    A, alvo = dados["A"], dados["alvo"]
    NMIN = 2 ** 19                                      # mesma grade de frequencia para todos os casos
    oA = ouro2(A)
    log("AVISO: aqui a fase orbital e zerada no inicio (f_ref = f_low); o item 1 mostra que isso nao e autoconsistente. "
        "A coluna 'ouro' dos itens 2 a 4 nao serve de referencia: ver rev_R2v_match3.txt.")
    log("1) Autoconsistencia: A (inicio 5.0 Hz) contra A (inicio 5.3 Hz), cosseno ate 7 Hz: 1-match %.2e"
        % match(oA, ouro2(A, 5.3, 7.0), n_min=NMIN))
    pB, r = E7.resolver(alvo, 1.19, -0.2, (A["iota"], 0.3, 65.0))
    log("2) q_B = 1.19 (residuo %.1e): convergencia na frequencia de inicio (f_min = 10 Hz)" % r)
    for fi, ft in ((5.0, 7.0), (7.0, 8.5), (8.0, 9.3), (9.5, 9.9)):
        log("   inicio %.1f Hz, cosseno ate %.1f Hz: 1-match %.3e" % (fi, ft, match(ouro2(A, fi, ft), ouro2(pB, fi, ft), n_min=NMIN)))
    xA, xB = r2(A), r2(pB)
    log("   desde 10 Hz, cosseno de 0.5 s e rampa (R2): 1-match %.3e" % match(xA, xB, n_min=NMIN))
    oB = ouro2(pB)
    log("3) Banda (q_B = 1.19):")
    for fmin in (10.0, 15.0, 25.0):
        log("   f_min %4.1f Hz: ouro %.3e ; R2 %.3e" % (fmin, match(oA, oB, fmin, n_min=NMIN), match(xA, xB, fmin, n_min=NMIN)))
    del xA, xB, oB
    log("   (%.0f s)" % (time.time() - t0))
    log("4) Lei de escala do ouro e do R2 ao longo da familia (chi2_B = -0.2), f_min = 10 Hz:")
    xA = r2(A)
    dq, yo, yr = [], [], []
    for qB in (1.15, 1.18, 1.19, 1.195, 1.205, 1.21, 1.22, 1.25):
        pB, r = E7.resolver(alvo, qB, -0.2, (A["iota"], 0.3, 65.0))
        o = match(oA, ouro2(pB), n_min=NMIN)
        x = match(xA, r2(pB), n_min=NMIN)
        dq.append(abs(qB - 1.2))
        yo.append(o)
        yr.append(x)
        log("   q_B %.3f (residuo %.1e): ouro %.3e (rho_crit %.1f) ; R2 %.3e (rho_crit %.1f)"
            % (qB, r, o, 1 / np.sqrt(2 * o), x, 1 / np.sqrt(2 * x)))
    dq, yo, yr = np.array(dq), np.array(yo), np.array(yr)
    for lado, sel in (("q_B < 1.2", dq * 0 + np.array([1, 1, 1, 1, 0, 0, 0, 0]) > 0),
                      ("q_B > 1.2", np.array([0, 0, 0, 0, 1, 1, 1, 1]) > 0)):
        po = np.polyfit(np.log(dq[sel]), np.log(yo[sel]), 1)
        pr = np.polyfit(np.log(dq[sel]), np.log(yr[sel]), 1)
        log("   %s: ouro 1-match = %.3g dq^%.2f ; R2 1-match = %.3g dq^%.2f" % (lado, np.exp(po[1]), po[0], np.exp(pr[1]), pr[0]))
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "revisao", "rev_R2v_match2.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
