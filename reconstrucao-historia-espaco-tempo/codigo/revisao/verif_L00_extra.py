"""Verificacao L00, conferencia extra do teste (c) do D0: a diferenca observaveis(desl='total') - binarias vem so
do inicio da janela?

binarias.memorias_fisicas integra pela regra do retangulo desde o primeiro ponto t0b da sua grade, o que equivale
(regra do ponto medio) ao trapezio desde t0b - dt/2. Se a atribuicao do D0 esta certa, observaveis com
t_i := t0b - dt/2, mesmas formulas (derivada de 4a ordem, E_lig 1PN, desl='total') reproduz binarias ate o erro
de quadratura O(dt^2) (as duas redes sao diferentes: a de binarias nao esta ancorada no pico).
Saida: resultados/revisao/verif_L00_extra.txt
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                     # noqa: E402
import observaveis as O                                  # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_extra.txt")
L = []
SA = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, F=10.0, iota=np.radians(50.0))


def log(s=""):
    print(s, flush=True)
    L.append(s)


for nivel in ("A", "C"):
    mb, ab, tb, hb = B.memorias_fisicas(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel=nivel)
    t0b = tb[0]
    del tb, hb
    t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
    vb = B.no_observador(mb, SA["iota"])
    for rot, tini in (("t_i (padrao)", ti), ("t0b - dt/2", t0b - 0.125), ("t0b", t0b)):
        mo, ao = O.memorias_observaveis(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel=nivel, desl="total",
                                        t=t, h=h, t_i=tini, ordem_deriv=4, ordem_elig=1)
        vo = B.no_observador(mo, SA["iota"])
        log("  nivel %s, inicio %-12s (%.4f M): observaveis/binarias - 1: %s ; M_f %+.1e" % (
            nivel, rot, tini, " ".join("%s %+.1e" % (k[:4], vo[k] / vb[k] - 1) for k in O.TIPOS), ao["M_f"] - ab["M_f"]))
    del t, h
# nivel C: o deslocamento 'total' e h_l0 na ULTIMA amostra; as duas grades terminam em instantes diferentes
mb, ab, tb, hb = B.memorias_fisicas(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"], nivel="C")
t, h, ti = O.gerar_janela(SA["q"], SA["c1"], SA["c2"], SA["M"], SA["F"])
d = np.gradient(h[(2, 0)].real, t[1] - t[0])
log("  nivel C: fim de binarias t = %.4f M, h20 = %.12e ; fim de observaveis t = %.4f M, h20 = %.12e ; razao - 1 = %+.2e"
    % (tb[-1], hb[(2, 0)][-1].real, t[-1], h[(2, 0)][-1].real, h[(2, 0)][-1].real / hb[(2, 0)][-1].real - 1))
log("  dh20/dt no fim dos dados (t = %.2f M): %+.2e por M (|h20| = %.4f): o modo (2,0) do substituto ainda varia"
    % (t[-3], d[-3], abs(h[(2, 0)][-1])))
del t, h, tb, hb
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
