"""Revisao R2, itens 2 e 3: distinguibilidade dos pares do exp07 com normas diferentes, e sensibilidade
do match e da SNR ao tratamento do sinal (janela no inicio, degrau da memoria no fim, resolucao no tempo).

Item 2. O 07 usa rho_crit = 1/sqrt(2(1 - match)), que supoe (a|a) = (b|b). Os pares B tem M, D e iota
diferentes, logo SNR diferente. Aqui: SNR de B (aLIGO e ET), (dh|dh) exato na SNR real e a SNR de A em que
(dh|dh) = 1 com a razao rho_B/rho_A fixa (rev_R2_comum.criterios).
Item 3. Para os pares (1, 0), (2, 0) e (2, +0.5): match e SNR com (i) busca no tempo 16 vezes mais fina,
(ii) janela de cosseno de 0.25/0.5/1 s no inicio, (iii) memoria com rampa no fim (exp15), (iv) so modos
oscilatorios, (v) fs = 8192 Hz, (vi) tudo junto.
Le resultados/exp07_pares.json. Saida: resultados/revisao/rev_R2_distinguibilidade.txt e .json
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import rev_R2_comum as C                                # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


F = 10.0
dados = json.load(open(os.path.join(RES, "exp07_pares.json")))
A = dados["A"]
LISTA = B.lista_osc() + B.MODOS_M0


def strain(par, lista=LISTA):
    t, h = B.gerar(par["q"], par["c1"], par["c2"], f0=par["M"] * Dt.MSUN_S * F, dt=0.25)
    return Dt.strain_observador(t, h, lista, par["M"], par["D"], par["iota"])


tsA, sA = strain(A)
tsAo, sAo = strain(A, B.lista_osc())
saida = dict(item2=[], item3=[])

log("ITEM 2: normas diferentes. rc_igual = 1/sqrt(2(1-m)) [07]; rc_exato = 1/sqrt(1+r^2-2rm), r = rho_B/rho_A;")
log("        rc_ampl = 1/sqrt(1-m^2) (amplitude de B livre); dd_real = (dh|dh) na SNR real (A a 400 Mpc).")
log("        Mesmo produto do exp07 (deteccao.comparar, h_+, fs 4096, sem janela).")
for p in dados["pares"]:
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    tsB, sB = strain(par)
    reg = dict(qB=p["qB"], c2B=p["c2B"], delta=max(abs(x) for x in p["dif"].values()))
    for psd in ("aLIGO", "ET"):
        c = Dt.comparar(tsA, sA, tsB, sB, psd, fmin=F)["+"]
        k = C.criterios(c)
        reg[psd] = dict(match=c["match"], snr_A=c["snr_A"], snr_B=c["snr_B"], **k)
        log("  par (%.0f, %+.1f) %-5s: match %.4f | SNR_A %.1f SNR_B %.1f (r = %.3f) | dd_real %.3e (sqrt %.1f) | "
            "rho_crit: igual %.3f, exato %.3f, ampl. livre %.3f"
            % (p["qB"], p["c2B"], psd, c["match"], c["snr_A"], c["snr_B"], k["r"], k["dd_real"], np.sqrt(k["dd_real"]),
               k["rc_igual"], k["rc_exato"], k["rc_ampl"]))
    saida["item2"].append(reg)
    del tsB, sB

log("")
log("ITEM 3: sensibilidade do match e da SNR ao tratamento do sinal (h_+).")
variantes = [
    ("exp07 (base)", dict()),
    ("busca no tempo x16", dict(up=16)),
    ("cosseno 0.25 s no inicio", dict(taper=0.25)),
    ("cosseno 0.5 s no inicio", dict(taper=0.5)),
    ("cosseno 1 s no inicio", dict(taper=1.0)),
    ("memoria com rampa no fim", dict(fim="rampa")),
    ("fs 8192 Hz", dict(fs=8192.0)),
    ("cos 0.5 s + rampa + x16", dict(taper=0.5, fim="rampa", up=16)),
]
for p in dados["pares"]:
    if (p["qB"], p["c2B"]) not in ((1.0, 0.0), (2.0, 0.0), (2.0, 0.5)):
        continue
    par = dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"])
    tsB, sB = strain(par)
    tsBo, sBo = strain(par, B.lista_osc())
    for psd in ("aLIGO", "ET"):
        base = None
        for nome, kw in variantes + [("so modos oscilatorios", dict(osc=True)),
                                     ("so osc. + cos 0.5 s + x16", dict(osc=True, taper=0.5, up=16))]:
            kw = dict(kw)
            if kw.pop("osc", False):
                c = C.comparar(tsAo, sAo, tsBo, sBo, psd, F, **kw)
            else:
                c = C.comparar(tsA, sA, tsB, sB, psd, F, **kw)
            k = C.criterios(c)
            if base is None:
                base = c
            log("  par (%.0f, %+.1f) %-5s %-28s: 1-match %.4e (var. %+.1e) | SNR_A %.2f (%+.1e) SNR_B %.2f (%+.1e) | rc_igual %.2f rc_exato %.2f"
                % (p["qB"], p["c2B"], psd, nome, 1 - c["match"], (1 - c["match"]) / (1 - base["match"]) - 1,
                   c["snr_A"], c["snr_A"] / base["snr_A"] - 1, c["snr_B"], c["snr_B"] / base["snr_B"] - 1,
                   k["rc_igual"], k["rc_exato"]))
            saida["item3"].append(dict(par=(p["qB"], p["c2B"]), psd=psd, variante=nome, **c, **k))
    del tsB, sB, tsBo, sBo

with open(os.path.join(RES, "revisao", "rev_R2_distinguibilidade.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(RES, "revisao", "rev_R2_distinguibilidade.json"), "w") as f:
    json.dump(saida, f, indent=1, default=float)
