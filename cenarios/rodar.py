"""Roda os cenários v2 e grava simulador/web/cenarios.json.

Saídas (todas com os dois vencedores na mesma régua):
  * por conjunto de hipóteses (central, neutro, pró-Lula, pró-Flávio) e família-tipo: resultados ANO A
    ANO (2027–2034) de Lula, Flávio e da diferença pareada, com faixas, equivalente-certeza (CRRA),
    P(pobreza) e a camada "medido × vivido";
  * células por regime inicial de cada vencedor, para a página repesar os priors de credibilidade;
  * sustentabilidade: ganho acumulado nos anos 1–2, 3–4 e 5–8, vantagem inicial revertida,
    P(crise / quebra da regra / ajuste forçado);
  * decomposição de Shapley por canal (exata, 2^11 coalizões) e experimento "+1 p.p. no mínimo";
  * tornado e índices de Sobol de 1ª ordem (estimador "given-data" por partição);
  * veredito de robustez por família (inconclusivo quando o sinal muda entre conjuntos).

Uso:
    python cenarios/rodar.py                      # 200.000 simulações por vencedor e conjunto
    python cenarios/rodar.py --n 20000 --n-shap 1500 --saida /tmp/x.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cenarios as C  # noqa: E402
import dados as DD  # noqa: E402
import premissas as PR  # noqa: E402

RAIZ = AQUI.parent
SAIDA = RAIZ / "simulador" / "web" / "cenarios.json"
CONJ = ["central", "neutro", "pro_lula", "pro_flavio"]
TIPOS = list(PR.TIPOS)
ANOS = PR.ANOS
I2030 = ANOS.index(2030)
QS = [0.1, 0.25, 0.5, 0.75, 0.9]
HIST_IDX = (40.0, 180.0, 1.0)
HIST_D = (-40.0, 40.0, 0.5)
LIMIAR_PONTOS = 1.0     # diferença média abaixo disso (pontos do índice) é "pequena"
LIMIAR_P = 0.70         # P(vencedor > outro) mínima para "robusto"
PERIODOS = {"anos_1_2": [0, 1], "anos_3_4": [2, 3], "anos_5_8": [4, 5, 6, 7]}


def _q(a, axis=0):
    return np.quantile(a, QS, axis=axis)


def hist(v, spec):
    lo, hi, st = spec
    nb = int(round((hi - lo) / st))
    idx = np.clip(np.floor((v - lo) / st + 1e-9).astype(int), 0, nb - 1)
    h = np.bincount(idx, minlength=nb)
    nz = np.nonzero(h)[0]
    if len(nz) == 0:
        return [0, []]
    return [int(nz[0]), h[nz[0]:nz[-1] + 1].tolist()]


def ce(v, rho):
    v = np.maximum(v, 1.0)
    return float(np.mean(v ** (1 - rho)) ** (1 / (1 - rho))) if rho != 1 else float(np.exp(np.mean(np.log(v))))


def r(x, nd=3):
    if isinstance(x, (list, tuple)):
        x = np.asarray(x, float)
    if isinstance(x, np.ndarray):
        return np.round(x, nd).tolist()
    return round(float(x), nd)


# ---------------------------------------------------------------------------
# Estatísticas
# ---------------------------------------------------------------------------
def stats_familia(RL, RF, h, rho):
    l, f = RL["familias"][h], RF["familias"][h]
    out = {}
    for nome, a in (("L", l["idx"]), ("F", f["idx"]), ("D", l["idx"] - f["idx"])):
        q = _q(a)
        out[nome] = {"media": r(a.mean(0), 2), **{f"p{int(qq * 100)}": r(q[i], 2) for i, qq in enumerate(QS)}}
    d = l["idx"] - f["idx"]
    out["D"]["p_L_maior"] = r((d > 0).mean(0))
    out["D"]["p_F_maior"] = r((d < 0).mean(0))
    viv = {}
    for nome, a in (("L", l["idx_vivido"]), ("F", f["idx_vivido"]), ("D", l["idx_vivido"] - f["idx_vivido"])):
        q = np.quantile(a, [0.1, 0.5, 0.9], axis=0)
        viv[nome] = {"media": r(a.mean(0), 2), "p10": r(q[0], 2), "p50": r(q[1], 2), "p90": r(q[2], 2)}
    out["vivido"] = viv
    lin, ext = PR.BASE["linha_pobreza_pc"], PR.BASE["linha_extrema_pc"]
    out["ce"] = {c: r([ce(x["idx"][:, t], rho) for t in range(len(ANOS))], 2) for c, x in (("L", l), ("F", f))}
    out["pobreza"] = {c: r((x["pc_real"] < lin).mean(0)) for c, x in (("L", l), ("F", f))}
    out["extrema"] = {c: r((x["pc_real"] < ext).mean(0)) for c, x in (("L", l), ("F", f))}
    out["renda0"] = r(float(l["renda0"]), 1)
    hl, hf = l["idx_hora"], f["idx_hora"]
    out["hora"] = {"L": r(hl.mean(0), 2), "F": r(hf.mean(0), 2), "D": r((hl - hf).mean(0), 2)}
    out["pobreza_2026"] = r(float(l["renda0"]) / PR.TIPOS[h]["tam"] < lin)
    out["in_natura"] = {c: r(np.asarray(x["inkind"]).mean(0), 2) for c, x in (("L", l), ("F", f))}
    if l["comida2019"] is not None:
        out["comida2019"] = {c: r(np.median(x["comida2019"], 0), 1) for c, x in (("L", l), ("F", f))}
    # sustentabilidade
    sus = {}
    for c, x in (("L", l["idx"]), ("F", f["idx"]), ("D", d)):
        sus[c] = {p: r((x[:, ix] - (0 if c == "D" else 100)).mean(), 2) for p, ix in PERIODOS.items()}
    d12, d58 = d[:, [0, 1]].mean(1), d[:, 4:].mean(1)
    # M6 da revisão v2: rótulo neutro — só a mudança da diferença entre os anos 1–2 e 5–8
    sus["mudanca_D"] = r(float(d58.mean() - d12.mean()), 2)
    sus["p_sinal_muda"] = r((np.sign(d12) != np.sign(d58)).mean())
    out["sustentabilidade"] = sus
    return out


def celulas(RL, RF, h):
    """Médias por ano e histogramas (2030 e 2034) condicionais ao regime inicial de cada vencedor."""
    l, f = RL["familias"][h]["idx"], RF["familias"][h]["idx"]
    sl, sf = RL["regime_ini"], RF["regime_ini"]
    d = l - f
    out = {"L": {}, "F": {}, "D": {}}
    for c, a, s in (("L", l, sl), ("F", f, sf)):
        for k in range(3):
            m = s == k
            if m.sum() == 0:
                continue
            out[c][str(k)] = {"n": int(m.sum()), "media": r(a[m].mean(0), 2),
                              "h2030": hist(a[m, I2030], HIST_IDX), "h2034": hist(a[m, -1], HIST_IDX)}
    for a_ in range(3):
        for b_ in range(3):
            m = (sl == a_) & (sf == b_)
            if m.sum() == 0:
                continue
            out["D"][f"{a_}{b_}"] = {"n": int(m.sum()), "media": r(d[m].mean(0), 3), "pos": r((d[m] > 0).mean(0), 4),
                                     "neg": r((d[m] < 0).mean(0), 4),
                                     "h2030": hist(d[m, I2030], HIST_D), "h2034": hist(d[m, -1], HIST_D)}
    return out


def macro(RL, RF):
    out = {}
    for v in RL["macro"]:
        out[v] = {}
        for c, R in (("L", RL), ("F", RF)):
            a = R["macro"][v]
            q = np.quantile(a, [0.1, 0.5, 0.9], axis=0)
            out[v][c] = {"p10": r(q[0], 2), "p50": r(q[1], 2), "p90": r(q[2], 2), "media": r(a.mean(0), 2)}
    out["regimes"] = {"L": r(RL["regimes_p"]), "F": r(RF["regimes_p"])}
    ev = {}
    for e in ("regra_sm_2030", "regra_sm_2034", "quebra_forcada", "crise_ate_2030", "arcabouco_rompido_2030",
              "ajuste_forcado_pos", "iva", "x6", "pec12", "reverte_topo"):
        ev[e] = {"L": r(RL["eventos"][e].mean()), "F": r(RF["eventos"][e].mean())}
    ev["bf_reajustes"] = {"L": r(RL["eventos"]["bf_reajustes"].mean(), 2), "F": r(RF["eventos"]["bf_reajustes"].mean(), 2)}
    out["eventos"] = ev
    return out


def faixas(RL, RF):
    pesos = DD.faixas_salariais()
    out = []
    for reg in ("NE", "resto"):
        for vin in ("formal", "informal"):
            pw = {m: p for m, p, _ in pesos[(reg, vin)]}
            for m in C.FAIXAS_M:
                k = f"{reg}|{vin}|{m:g}"
                out.append({"regiao": reg, "vinculo": vin, "m": m, "peso": r(pw[m], 4),
                            "L": [r(RL["faixas"][k][:, t].mean(), 2) for t in (1, I2030, len(ANOS) - 1)],
                            "F": [r(RF["faixas"][k][:, t].mean(), 2) for t in (1, I2030, len(ANOS) - 1)]})
    return out


MEIO, PONTAS = ["2a5", "5a10", "10a20"], ["ate2", "50mais"]


def sanduiche(RL, RF):
    """Matriz faixa × tipo de renda: variação média do índice por período (L, F, L − F) e o teste do
    'sanduíche': o meio (2–20 SM) vai pior que as DUAS pontas (até 2 e 50+ SM)?"""
    cel = {}
    for h, tp in PR.SANDUICHE.items():
        l, f = RL["familias"][h]["idx"], RF["familias"][h]["idx"]
        cel[h] = {"faixa": tp["faixa"], "tipo": tp["tipo_renda"],
                  "ano": {"L": r(l.mean(0) - 100, 2), "F": r(f.mean(0) - 100, 2), "D": r((l - f).mean(0), 2)},
                  "periodo": {c: {pp: r((x[:, ix].mean() - (0 if c == "D" else 100)), 2) for pp, ix in PERIODOS.items()}
                              for c, x in (("L", l), ("F", f), ("D", l - f))},
                  "p_L_maior_2030": r(((l - f)[:, I2030] > 0).mean())}
    teste = {}
    for tr in ("clt", "pj"):   # capital fora do teste (C2: renda + reavaliação, sinal sensível à Selic)
        teste[tr] = {}
        for c in ("L", "F"):
            teste[tr][c] = {}
            for pp in PERIODOS:
                v = {fx: cel[f"s_{fx}_{tr}"]["periodo"][c][pp] for fx, *_ in PR.FAIXAS_SANDUICHE}
                meio = float(np.mean([v[x] for x in MEIO]))
                pontas = [v[x] for x in PONTAS]
                folga = meio - min(pontas)
                veredito_s = "sim" if folga < -LIMIAR_PONTOS else ("não" if meio - max(pontas) > -LIMIAR_PONTOS and folga >= 0 else "indistinguível")
                if veredito_s == "não" and folga < LIMIAR_PONTOS:
                    veredito_s = "indistinguível"
                teste[tr][c][pp] = {"meio": round(meio, 2), "ate2": v["ate2"], "50mais": v["50mais"],
                                    "aperto": round(meio - float(np.mean(pontas)), 2), "veredito": veredito_s}
    return {"celulas": cel, "teste": teste}


def _estacionaria(P):
    w, v = np.linalg.eig(P.T)
    x = np.real(v[:, np.argmin(np.abs(w - 1))])
    return x / x.sum()


def veredito(por_conj, h, t):
    """Mesmo sinal da diferença média em todos os conjuntos? Magnitude e probabilidade no central."""
    ds = {c: por_conj[c]["familias"][h]["D"]["media"][t] for c in CONJ}
    sinais = {c: (1 if v > 0 else (-1 if v < 0 else 0)) for c, v in ds.items()}
    cen = por_conj["central"]["familias"][h]["D"]
    lado = "L" if ds["central"] > 0 else "F"
    p_lado = cen["p_L_maior"][t] if lado == "L" else cen["p_F_maior"][t]
    if len(set(sinais.values())) > 1:
        rot, cod = "inconclusivo", "inconclusivo"
    elif min(abs(v) for v in ds.values()) >= LIMIAR_PONTOS and p_lado >= LIMIAR_P:
        rot, cod = f"robusto: favorece {'Lula' if lado == 'L' else 'Flávio'}", "robusto_" + lado
    elif abs(ds["central"]) > LIMIAR_PONTOS and not (0.35 <= p_lado <= 0.65):
        rot, cod = f"frágil: inclina para {'Lula' if lado == 'L' else 'Flávio'}", "fragil_" + lado
    else:
        # M6: sem rótulo narrativo quando a diferença é menor que 1 ponto ou P está entre 0,35 e 0,65
        rot, cod = "sem diferença detectável", "nula"
    return {"rotulo": rot, "codigo": cod, "dif_por_conjunto": {c: round(v, 2) for c, v in ds.items()},
            "vira_em": [c for c in CONJ if sinais[c] != sinais["central"]]}


# ---------------------------------------------------------------------------
# Sobol (1ª ordem, "given-data": razão de correlação por partição em quantis)
# ---------------------------------------------------------------------------
def sobol(RL, RF, h, t, nbins=20, top=10):
    y = RL["familias"][h]["idx"][:, t] - RF["familias"][h]["idx"][:, t]
    vy = y.var()
    if vy <= 0:
        return []
    out = []
    cand = {**{k: v for k, v in RL["amostras"].items()}}
    for k in ("regime_ini", "iva", "x6", "pec12", "reverte_topo", "corte_comb", "intencao_regra", "comp_obrigatoria",
              "ajuste_total"):
        if k in RL["amostras"]:
            cand[k + "|L"] = RL["amostras"][k]
        if k in RF["amostras"]:
            cand[k + "|F"] = RF["amostras"][k]
        cand.pop(k, None)
    for k, xv in cand.items():
        xv = np.asarray(xv, float)
        if np.ptp(xv) == 0:
            continue
        uniq = np.unique(xv)
        if len(uniq) <= 5:
            lab = np.searchsorted(uniq, xv)
        else:
            edges = np.quantile(xv, np.linspace(0, 1, nbins + 1)[1:-1])
            lab = np.searchsorted(edges, xv)
        cnt = np.bincount(lab)
        sm = np.bincount(lab, weights=y)
        ok = cnt > 0
        mu = sm[ok] / cnt[ok]
        s1 = float((cnt[ok] * (mu - y.mean()) ** 2).sum() / len(y) / vy)
        # correção do viés de partição (≈ (nbins−1)/N)
        s1 = max(0.0, s1 - (ok.sum() - 1) / len(y))
        out.append((k, s1))
    out.sort(key=lambda z: -z[1])
    return [{"param": k, "s1": round(v, 4)} for k, v in out[:top]]


# ---------------------------------------------------------------------------
# Shapley por canal (coalizões avaliadas em paralelo)
# ---------------------------------------------------------------------------
_SH = {}


def _avaliar(args):
    mask, canais, n, seed, specs, comum, slots, tipo_saida = args
    on = {c: bool(mask >> i & 1) for i, c in enumerate(canais)}
    for c in PR.CANAIS:
        on.setdefault(c, True)
    R = C.rodar_par(n, seed, specs, {**(comum or {}), "desemprego_binario": False}, on, slots=slots)
    if tipo_saida == "dif":
        return mask, np.stack([(R["L"]["familias"][h]["idx"] - R["F"]["familias"][h]["idx"]).mean(0) for h in TIPOS])
    return mask, np.stack([(R["L"]["familias"][h]["idx"] - R["F"]["familias"][h]["idx"]).mean(0) for h in TIPOS])


def shapley(canais, n, seed, specs, comum=None, slots=("1", "2"), procs=None):
    k = len(canais)
    jobs = [(m, canais, n, seed, specs, comum, slots, "dif") for m in range(1 << k)]
    procs = procs or min(4, os.cpu_count() or 1)
    if procs == 1:
        val = dict(map(_avaliar, jobs))
    else:
        with Pool(procs) as pool:
            val = dict(pool.map(_avaliar, jobs, chunksize=8))
    phi = np.zeros((k,) + val[0].shape)
    fat = [math.factorial(s) * math.factorial(k - s - 1) / math.factorial(k) for s in range(k)]
    for i in range(k):
        bit = 1 << i
        for m in range(1 << k):
            if m & bit:
                continue
            s = bin(m).count("1")
            phi[i] += fat[s] * (val[m | bit] - val[m])
    return phi, val[(1 << k) - 1], val[0]


# ---------------------------------------------------------------------------
# Tornado (central): cada premissa nos extremos, demais no padrão
# ---------------------------------------------------------------------------
def _sp(c, path, v):
    return ("spec", c, path, v)


def _tornado_itens():
    itens = []
    nomes = {"regime.pi0": ("R5", "Prior de credibilidade", ("crise mais provável", "crível mais provável")),
             "minimo.p_intencao": ("C1", "Intenção de manter a regra do mínimo", ("0,6–0,8", "0,9–1,0")),
             "bolsa.p_reajuste": ("R1", "Reajuste do Bolsa Família", ("0,2–0,6", "0,6–0,95")),
             "ir.p_correcao": ("M2", "Correção da tabela do IR", ("0–0,3/ano", "0,4–0,8/ano")),
             "fiscal.composicao": ("R4", "Composição do ajuste", ("50% obrigatórias", "5% obrigatórias")),
             "fiscal.receita_unica": ("CC45", "Parte do ajuste em receita única", ("70%", "10%")),
             "credito.direcionado_dfatia": ("C7", "Expansão do crédito direcionado", ("+2 p.p./ano", "−0,5 p.p./ano"))}
    for path, fav, desf in PR.EXECUCAO_DISPUTADA:
        cod, nome, ext = nomes[path]
        for cand, nm in (("L", "Lula"), ("F", "Flávio")):
            itens.append((cod, f"{nome} — {nm}", [_sp(cand, path, desf)], [_sp(cand, path, fav)], ext))
    itens += [
        ("L1/F1", "Choque de impacto do câmbio (os dois)", [_sp("L", "regime.impacto_cambio", 0.03), _sp("F", "regime.impacto_cambio", -0.04)],
         [_sp("L", "regime.impacto_cambio", 0.15), _sp("F", "regime.impacto_cambio", -0.14)], ("fraco", "forte")),
        ("F9", "P(IVA de 20%) — Flávio", [_sp("F", "iva.p", 0.05)], [_sp("F", "iva.p", 0.4)], ("0,05", "0,4")),
        ("F8", "P(reverter impostos sobre o topo) — Flávio", [_sp("F", "ir.p_reverte_topo", 0.1)], [_sp("F", "ir.p_reverte_topo", 0.5)], ("0,1", "0,5")),
        ("CC17", "Subsídio a combustíveis em 2027 — Lula", [_sp("L", "combustivel.subsidio_2027", 0.15)], [_sp("L", "combustivel.subsidio_2027", 0.6)], ("0,15% PIB", "0,6% PIB")),
        ("F14", "P(PEC 12) — Flávio", [_sp("F", "trabalho.p_pec12", 0.1)], [_sp("F", "trabalho.p_pec12", 0.5)], ("0,1", "0,5")),
    ]
    for k, rot in [("premio_divida", "Prêmio por p.p. de dívida"), ("sm_repasse_escala", "Repasse do mínimo a preços"),
                   ("farol_informal", "Efeito farol (informais)"), ("emprego_sm_ne", "Emprego formal ao mínimo no NE"),
                   ("mult_transferencia", "Multiplicador de transferências"), ("mult_discricionaria", "Multiplicador da discricionária"),
                   ("obrig_abono", "Abono no corte de obrigatórias"), ("incidencia_lucro_salario", "Tributo sobre lucro → salários"),
                   ("taylor_pi", "Reação da Selic à inflação"), ("fx_crise", "Câmbio no regime de crise"),
                   ("financiado_divida", "Promessa sem fonte que vira dívida"), ("topo_decil_parcela", "Parte da receita do topo paga pelo décimo"),
                   ("cambio_renda", "Câmbio → renda (comerciáveis)"), ("achatamento_psi", "Achatamento (custo não repassado)"),
                   ("fechamento_k", "Fechamento fiscal: P de estouro"), ("fechamento_sm", "Fechamento: sai pela regra do mínimo"),
                   ("beta_acoes_premio", "Ações x prêmio de risco"), ("crise_aperto_p", "Pacote de emergência na crise")]:
        sp = PR.COMUM[k]
        lo, hi = PR._ponta(sp, "lo"), PR._ponta(sp, "hi")
        itens.append(("comum", rot, [("comum", k, lo)], [("comum", k, hi)], (f"{lo:g}".replace(".", ","), f"{hi:g}".replace(".", ","))))
    return itens


TORNADO = None


def _aplicar(ajustes, base_specs):
    from copy import deepcopy
    specs = deepcopy(base_specs)
    com = {}
    for a in ajustes:
        if a[0] == "comum":
            com[a[1]] = a[2]
        else:
            _, cand, path, v = a
            d = specs[cand]
            ks = path.split(".")
            for kk in ks[:-1]:
                d = d[kk]
            d[ks[-1]] = v
    return com, specs


def _tornado_job(args):
    i, lado, ajustes, n, seed = args
    com, specs = _aplicar(ajustes, PR.CANDIDATOS)
    com["desemprego_binario"] = False
    R = C.rodar_par(n, seed, specs, com)
    return i, lado, {h: [r((R["L"]["familias"][h]["idx"][:, t] - R["F"]["familias"][h]["idx"][:, t]).mean(), 3)
                         for t in (I2030, len(ANOS) - 1)] for h in TIPOS}


def tornado(n, seed, procs=None):
    global TORNADO
    TORNADO = _tornado_itens()
    jobs = []
    for i, (_, _, lo, hi, _) in enumerate(TORNADO):
        jobs += [(i, "baixo", lo, n, seed), (i, "alto", hi, n, seed)]
    with Pool(procs or min(4, os.cpu_count() or 1)) as pool:
        res = pool.map(_tornado_job, jobs)
    base = _tornado_job((-1, "base", [], n, seed))[2]
    out = [{"id": t[0], "nome": t[1], "extremos": list(t[4])} for t in TORNADO]
    for i, lado, v in res:
        out[i][lado] = v
    return {"base": base, "itens": out}


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    ap.add_argument("--n-shap", type=int, default=4_000)
    ap.add_argument("--n-sens", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--saida", type=Path, default=SAIDA)
    ap.add_argument("--procs", type=int, default=None)
    a = ap.parse_args(argv)
    t0 = time.time()
    rho = float(PR.COMUM["crra"])

    por_conj = {}
    for cj in CONJ:
        com, specs = PR.aplicar_conjunto(cj)
        R = C.rodar_par(a.n, a.seed, specs, com, tipos=TIPOS + list(PR.SANDUICHE))
        RL, RF = R["L"], R["F"]
        por_conj[cj] = {
            "familias": {h: stats_familia(RL, RF, h, rho) for h in TIPOS},
            "celulas": {h: celulas(RL, RF, h) for h in TIPOS},
            "macro": macro(RL, RF),
            "pi0": {"L": specs["L"]["regime"]["pi0"], "F": specs["F"]["regime"]["pi0"]},
            "sanduiche": sanduiche(RL, RF),
        }
        if cj == "central":
            por_conj[cj]["faixas"] = faixas(RL, RF)
            # m1: Sobol sobre E[D | sorteios de política e macro] (sem a loteria do emprego da família)
            RE = C.rodar_par(min(a.n, 60_000), a.seed + 5, specs, {**com, "desemprego_binario": False})
            por_conj[cj]["sobol"] = {h: {"2030": sobol(RE["L"], RE["F"], h, I2030), "2034": sobol(RE["L"], RE["F"], h, len(ANOS) - 1)} for h in TIPOS}
            por_conj[cj]["d_esperado"] = {h: r((RE["L"]["familias"][h]["idx"] - RE["F"]["familias"][h]["idx"]).mean(0), 3) for h in TIPOS}
            del RE
        del R, RL, RF
        print(f"{cj}: {time.time() - t0:.1f}s", flush=True)

    rob = {h: {"2030": veredito(por_conj, h, I2030), "2034": veredito(por_conj, h, len(ANOS) - 1),
               "2028": veredito(por_conj, h, ANOS.index(2028))} for h in TIPOS}

    phi, cheio, vazio = shapley(PR.CANAIS, a.n_shap, a.seed + 1, PR.CANDIDATOS, procs=a.procs)
    print(f"shapley: {time.time() - t0:.1f}s", flush=True)
    shap = {h: {"canais": {c: r(phi[i, j], 3) for i, c in enumerate(PR.CANAIS)}, "total": r(cheio[j], 3),
                "sem_canais": r(vazio[j], 3)} for j, h in enumerate(TIPOS)}

    # Experimento: +1 p.p. de ganho real do mínimo a partir de 2028 (mesmo programa e mesmos sorteios)
    from copy import deepcopy
    base = deepcopy(PR.CANDIDATOS["L"])
    base["minimo"]["p_intencao"] = 1.0
    extra = deepcopy(base)
    extra["minimo"]["ganho_extra"] = 1.0
    can_sm = ["sm_direto", "repasse", "farol", "achatamento", "emprego", "juros", "cambio", "fiscal"]
    phi_sm, cheio_sm, _ = shapley(can_sm, a.n_shap, a.seed + 2, {"L": extra, "F": base}, slots=("1", "1"), procs=a.procs)
    print(f"experimento SM: {time.time() - t0:.1f}s", flush=True)
    exp_sm = {h: {"canais": {c: r(phi_sm[i, j], 3) for i, c in enumerate(can_sm)}, "total": r(cheio_sm[j], 3)}
              for j, h in enumerate(TIPOS)}

    torn = tornado(a.n_sens, a.seed + 3, a.procs)
    print(f"tornado: {time.time() - t0:.1f}s", flush=True)

    out = {
        "versao": 2,
        "meta": {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_por_vencedor": a.n,
                 "n_shapley": a.n_shap, "n_sensibilidade": a.n_sens, "semente": a.seed, "anos": ANOS,
                 "anos_mandato": ANOS[:PR.ANOS_MANDATO], "segundos": round(time.time() - t0, 1),
                 "crra": rho, "limiar_pontos": LIMIAR_PONTOS, "limiar_p": LIMIAR_P,
                 "notas": ["revisao_cetica_cenarios_v1.md", "salario_minimo_equilibrio_geral.md", "macro_fiscal_dinamica.md",
                           "checagem_promessas_discursos.md", "cenarios_economicos_insumos.md", "medido_vs_vivido.md"]},
        "base": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in PR.BASE.items()},
        "consenso": {k: v.tolist() for k, v in PR.CONS.items()},
        "divida_consenso": r(C.DIVIDA_CONS, 2),
        "tipos": {h: {"nome": t["nome"], "curto": t["curto"], "tam": t["tam"]} for h, t in PR.TIPOS.items()},
        "sanduiche_def": {"faixas": [[f[0], f[1], f[2]] for f in PR.FAIXAS_SANDUICHE], "tipos_renda": PR.TIPOS_RENDA,
                          "adapt": PR.ADAPT, "l15270": PR.L15270, "in_kind": [f[4] for f in PR.FAIXAS_SANDUICHE],
                          "trib_pj": PR.TRIB_PJ, "meio": MEIO, "pontas": PONTAS},
        "conjuntos": {k: v for k, v in PR.CONJUNTOS.items()},
        "ordem_conjuntos": CONJ,
        "canais": PR.CANAIS, "canal_nome": PR.CANAL_NOME, "regimes": PR.REGIMES,
        "transicao": PR.TRANSICAO.tolist(),
        "hist": {"idx": list(HIST_IDX), "d": list(HIST_D)},
        "resultados": por_conj,
        "robustez": rob,
        "shapley": shap,
        "experimento_sm": exp_sm, "canais_sm": can_sm,
        "tornado": torn,
        "canais_premissa": ["fiscal", "sm_direto", "trabalho", "impostos", "credito"],
        "canais_longo": ["longo_prazo"],
        "regime_estacionario": r(_estacionaria(PR.TRANSICAO)),
        "parametros": [dict(zip(["id", "nome", "lula", "flavio", "fonte", "tipo"], p)) for p in PR.PARAMETROS],
    }
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False, default=float)
    a.saida.write_text(txt, encoding="utf-8")
    print(f"gravado {a.saida} ({len(txt) / 1e6:.2f} MB) em {time.time() - t0:.1f}s")
    cen = por_conj["central"]["familias"]
    for h in TIPOS:
        d = cen[h]["D"]
        print(f"{h:17s} D2028 {d['media'][1]:+6.2f}  D2030 {d['media'][I2030]:+6.2f} [{d['p10'][I2030]:+.1f},{d['p90'][I2030]:+.1f}] "
              f"P(L>F) {d['p_L_maior'][I2030]:.2f}  D2034 {d['media'][-1]:+6.2f}  | {rob[h]['2030']['rotulo']} {rob[h]['2030']['dif_por_conjunto']}")
    return out


if __name__ == "__main__":
    main()
