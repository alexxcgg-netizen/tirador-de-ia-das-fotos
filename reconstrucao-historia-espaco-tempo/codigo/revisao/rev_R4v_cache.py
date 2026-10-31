"""Verificador R4v, item 2: o 'residuo' do exp12_pares.json vem de colisoes da chave arredondada do cache?

Refaz, num processo so, exatamente o que o processo filho do exp12 fez para um caso (E._caso: as 3 partidas
de E.PARTIDAS em sequencia, com o mesmo cache compartilhado), usando as proprias funcoes do exp12. A unica
mudanca e um involucro em E.mem_ehm que registra as colisoes: chamadas cuja chave arredondada (9 casas) ja
estava no cache, mas com floats exatos diferentes (o cache devolve entao as memorias de outro ponto).
No fim de cada partida: o residuo do otimizador, se o ponto final foi uma colisao, e o residuo reavaliado
sem cache (4 memorias, com o D gravado). Compara com o json bit a bit.
Uso: python revisao/rev_R4v_cache.py <e0> <qB>
Saida: resultados/revisao/rev_R4v_cache_e<e0>_q<qB>.txt
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
_orig = E.mem_ehm
_primeiro = {}
_colisoes = []
_n = [0]


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def chave(q, c1, c2, M, e0):
    return (round(q, 9), round(c1, 9), round(c2, 9), round(M, 9), round(e0, 9))


def mem_instr(q, c1, c2, M, e0):
    k = chave(q, c1, c2, M, e0)
    ex = (q, c1, c2, M, e0)
    if k in E._cache:
        if _primeiro[k] != ex:
            _colisoes.append((ex, _primeiro[k]))
    else:
        _primeiro[k] = ex
        _n[0] += 1
    return _orig(q, c1, c2, M, e0)


E.mem_ehm = mem_instr


def sem_cache(par):
    f0 = par["M"] * Dt.MSUN_S * E.F_FIS
    t, h = E.gerar(par["q"], par["c1"], par["c2"], f0, par["e"])
    eta = par["q"] / (1 + par["q"]) ** 2
    mem, _ = E.memorias_janela(t, h, E.LISTA, E.calc(), eta, (np.pi * f0) ** (2 / 3))
    del t, h
    return B.valores_fisicos(mem, par["iota"], par["M"], par["D"])


if __name__ == "__main__":
    t0 = time.time()
    eB, qB = float(sys.argv[1]), float(sys.argv[2])
    DADOS = json.load(open(os.path.join(RAIZ, "resultados", "exp12_pares.json")))
    pj = [x for x in DADOS["pares"] if x["e0"] == eB and x["qB"] == qB][0]
    c2B = pj["c2B"]
    alvo = DADOS["alvo"]
    log("caso e0 = %.1f, q_B = %.1f, chi2_B = %+.1f ; json: residuo %.16e, M %.16g, c1 %.16g, D %.16g, iota %.16g"
        % (eB, qB, c2B, pj["residuo"], pj["M"], pj["c1"], pj["D"], pj["iota"]))
    melhor = None
    for i, x0 in enumerate(E.PARTIDAS):
        nc0 = len(_colisoes)
        try:
            par, r = E.resolver(alvo, qB, c2B, eB, x0)
        except Exception as ex:                       # fora do dominio do modelo
            log("  partida %d: excecao %s" % (i, ex))
            continue
        k = chave(qB, par["c1"], c2B, par["M"], eB)
        col_final = _primeiro[k] != (qB, par["c1"], c2B, par["M"], eB)
        vB = sem_cache(par)
        d = [(vB[kk] - alvo[kk]) / abs(alvo[kk]) for kk in TIP]
        log("  partida %d: residuo do otimizador %.4e ; M %.13f c1 %+.10f iota %.10f D %.8f ; colisoes nesta partida %d ; ponto final colidido: %s"
            % (i, r, par["M"], par["c1"], par["iota"], par["D"], len(_colisoes) - nc0, col_final))
        if col_final:
            ex = _primeiro[k]
            log("      ponto que o cache devolveu no fim: dM %+.3e Msol, dc1 %+.3e" % (ex[3] - par["M"], ex[1] - par["c1"]))
        log("      reavaliado sem cache (4 memorias): max %.4e [%s]" % (max(abs(x) for x in d), " ".join("%s %+.2e" % (kk[:4], x) for kk, x in zip(TIP, d))))
        if melhor is None or r < melhor[1]:
            melhor = (par, r)
        if melhor[1] < 1e-9:
            break
    par, r = melhor
    log("melhor: residuo %.16e (json %.16e) ; M %.16g (json %.16g) ; bit a bit igual ao json: residuo %s, M %s, D %s"
        % (r, pj["residuo"], par["M"], pj["M"], r == pj["residuo"], par["M"] == pj["M"], par["D"] == pj["D"]))
    log("avaliacoes novas do modelo %d ; colisoes no total %d ; (%.0f s)" % (_n[0], len(_colisoes), time.time() - t0))
    if _colisoes:
        dm = [abs(a[3] - b[3]) for a, b in _colisoes]
        dc = [abs(a[1] - b[1]) for a, b in _colisoes]
        log("  colisoes: |dM| ate %.1e Msol, |dc1| ate %.1e" % (max(dm), max(dc)))
    with open(os.path.join(RES, "rev_R4v_cache_e%.1f_q%.1f.txt" % (eB, qB)), "w") as f:
        f.write("\n".join(linhas) + "\n")
