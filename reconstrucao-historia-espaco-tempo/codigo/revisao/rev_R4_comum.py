"""Revisor R4: funcoes comuns (SEOBNRv5EHM com anomalia relativistica livre, nivel A).

Reproduz exatamente a cadeia do exp12 (exp12_excentricas_imr.gerar / memorias_janela / fisicos), com uma
unica diferenca: a anomalia relativistica inicial l0 (rel_anomaly do pyseobnr) e um argumento, em vez
de fixa em 0. Para l0 = 0 o resultado deve ser identico bit a bit ao do exp12.
Nao guarda formas de onda: o cache (opcional) guarda so as memorias (dicionarios pequenos).
"""
import logging
import os
import sys
import warnings

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
COD = os.path.dirname(AQUI)
RAIZ = os.path.dirname(COD)
RES = os.path.join(RAIZ, "resultados", "revisao")
sys.path.insert(0, COD)
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402
import exp12_excentricas_imr as E                       # noqa: E402

F_FIS = E.F_FIS
LISTA = E.LISTA
_cache = {}


class _Coletor(logging.Handler):
    """Guarda as mensagens de log do pyseobnr (WARNING ou mais grave)."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.msgs = []

    def emit(self, rec):
        self.msgs.append("%s: %s" % (rec.levelname, rec.getMessage()))


COLETOR = _Coletor()
logging.getLogger("pyseobnr").addHandler(COLETOR)
logging.getLogger().addHandler(COLETOR)


def gerar(q, c1, c2, f0, e0, l0=0.0, debug=False):
    """Como E.gerar, mas com rel_anomaly = l0. Com debug=True devolve tambem o objeto do modelo."""
    from pyseobnr.generate_waveform import generate_modes_opt
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        saida = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=l0,
                                   approximant="SEOBNRv5EHM", debug=debug)
    for a in avisos:
        COLETOR.msgs.append("warnings.%s: %s" % (a.category.__name__, a.message))
    t, modos = saida[0], saida[1]
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    if debug:
        return np.asarray(t), h, saida[2]
    return np.asarray(t), h


def mem_ehm(q, c1, c2, M, e0, l0=0.0, usar_cache=True):
    """Memorias m = 0 de janela (desde 10 Hz) e auxiliares, nivel A; chave do cache sem arredondamento."""
    k = (float(q), float(c1), float(c2), float(M), float(e0), float(l0))
    if usar_cache and k in _cache:
        return _cache[k]
    f0 = M * Dt.MSUN_S * F_FIS
    t, h = gerar(q, c1, c2, f0, e0, l0)
    eta = q / (1 + q) ** 2
    out = E.memorias_janela(t, h, LISTA, E.calc(), eta, (np.pi * f0) ** (2 / 3))
    del t, h
    if usar_cache:
        _cache[k] = out
    return out


def fisicos(par, usar_cache=True):
    """As quatro memorias no observador (unidades fisicas) para par = dict(M, q, c1, c2, D, iota, e, l0)."""
    mem, aux = mem_ehm(par["q"], par["c1"], par["c2"], par["M"], par["e"], par.get("l0", 0.0), usar_cache)
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"]), aux


def dif_rel(v, alvo):
    return {k: (v[k] - alvo[k]) / abs(alvo[k]) for k in B.TIPOS}


def maxabs(d):
    return max(abs(x) for x in d.values())
