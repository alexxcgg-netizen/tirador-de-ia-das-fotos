"""Roda a validação (deixa-uma-eleição-de-fora), ajusta o modelo em 2018+2022, projeta o 2º turno de 2026 por
município e simula a incerteza (500 mil simulações nacionais).

    python modelo_municipal/baixar_historico.py   # 2018/2022 -> data/hist_{ano}.csv (uma vez)
    python modelo_municipal/baixar_2026.py        # 1º turno 2026 -> data/mun_2026_1t.csv (uma vez)
    python modelo_municipal/rodar_mun.py          # -> resultados_municipal_2t.json, projecao_municipios_2t.csv
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from modelo_mun import (AQUI, CATS, CATS6, ModeloEI, ModeloLogit, agregar, avaliar, carregar_2026,
                        carregar_historico, simular)

VARIANTES = {
    # principal: Goodman restrito, terceiros divididos em esquerda / não-esquerda, encolhimento nacional -> UF
    "EI6_uf": lambda: ModeloEI(niveis=["uf"], lam=10, cats=CATS6),
    "EI6_regiao_uf": lambda: ModeloEI(niveis=["regiao", "uf"], lam=30, cats=CATS6),
    "EI6_uf_porte": lambda: ModeloEI(niveis=["uf", "uf_porte"], lam=30, cats=CATS6),
    "EI6_nacional": lambda: ModeloEI(niveis=[], lam=0, cats=CATS6),
    # terceiros num bloco só (a pergunta original: terceiros/brancos/abstenção -> 2º turno)
    "EI5_uf": lambda: ModeloEI(niveis=["uf"], lam=10, cats=CATS),
    "EI5_nacional": lambda: ModeloEI(niveis=[], lam=0, cats=CATS),
    # regressão de swing no logito com efeitos de UF
    "LOGIT_uf": lambda: ModeloLogit(efeito="uf"),
    "LOGIT_sem_efeito": lambda: ModeloLogit(efeito=None),
}
PRINCIPAL = "EI6_uf"


def _r(x, n=2):
    return round(float(x), n)


def main(n_sim: int = 500_000) -> dict:
    H = {a: carregar_historico(a) for a in (2018, 2022)}
    d26 = carregar_2026()
    pool = pd.concat([H[2018], H[2022]], ignore_index=True)

    # ---------------- validação deixa-uma-eleição-de-fora
    validacao, proj_var = {}, {}
    for nome, f in VARIANTES.items():
        validacao[nome] = {}
        for tr, te in ((2018, 2022), (2022, 2018)):
            m = f().ajustar(H[tr])
            r = avaliar(m.prever(H[te]), H[te])
            if nome != PRINCIPAL:
                r.pop("erros_uf_pp")
            validacao[nome][f"{tr}->{te}"] = r
        # projeção 2026 de cada variante (treino 2018, 2022 e conjunto)
        proj_var[nome] = {}
        for rot, dados in (("treino_2018", H[2018]), ("treino_2022", H[2022]), ("treino_2018_2022", pool)):
            p = f().ajustar(dados).prever(d26)
            a = agregar(p).iloc[0]
            proj_var[nome][rot] = {"lula_pct": _r(100 * a.fatia_pt_prev), "validos_mi": _r(a.validos2_prev / 1e6, 3)}

    def rms(chave, nome=PRINCIPAL):
        return float(np.sqrt(np.mean([validacao[nome][k][chave] ** 2 for k in validacao[nome]])))

    resumo_val = {
        nome: {"rmse_nacional_pp": _r(rms("erro_nacional_pp", nome)), "rmse_uf_pp": _r(rms("rmse_uf_pp", nome)),
               "rmse_municipal_pp": _r(rms("rmse_mun_pp", nome)), "erro_validos_rms_pct": _r(rms("erro_validos_pct", nome))}
        for nome in VARIANTES
    }

    # ---------------- modelo principal treinado em 2018+2022
    modelo = VARIANTES[PRINCIPAL]().ajustar(pool)
    prev = modelo.prever(d26)
    nac = agregar(prev).iloc[0]

    # componentes de erro a partir da validação (média quadrática dos dois sentidos)
    dp = {"nac": rms("erro_nacional_pp"), "reg": rms("dp_regiao_pp"), "uf": rms("dp_uf_na_regiao_pp"),
          "mun": rms("dp_mun_na_uf_pp")}
    sim = simular(prev, dp["nac"], dp["reg"], dp["uf"], dp["mun"], n=n_sim)

    # comparecimento do 2º turno: válidos projetados + brancos/nulos (taxa do 2º turno de 2022 por UF)
    h22 = pd.read_csv(AQUI / "data" / "hist_2022.csv")
    g = h22.groupby("uf")[["t2_brancos", "t2_nulos", "t2_comparecimento"]].sum()
    taxa_bn = ((g.t2_brancos + g.t2_nulos) / g.t2_comparecimento)
    vuf = prev.groupby("uf").validos2_prev.sum()
    comp_uf = vuf / (1 - taxa_bn.reindex(vuf.index).fillna(taxa_bn.mean()))
    aptos = float(d26.aptos.sum())
    comp1 = float(d26.comparecimento.sum())

    # sensibilidade: fração do bloco "não-esquerda" (Caiado, Cury, Renan Santos, Zema...) que vai para Lula
    beta = {k: modelo.coefs[("nac", "nac")][k] for k in ("pt", "opp")}
    sens = []
    X = d26[CATS6].to_numpy(float)
    a26 = d26.aptos.to_numpy(float)
    base_pt = prev.pt2_prev.to_numpy()
    base_op = prev.opp2_prev.to_numpy()
    tn = X[:, CATS6.index("x_terc_nesq")] * a26
    for frac_lula in (0.2, 0.3, 0.4, 0.5, 0.6):
        # mantém o total do bloco que vota no 2º turno igual ao do modelo; troca só a divisão Lula/Flávio
        Bp = np.array([modelo._beta({"uf": u})["pt"][3] for u in d26.uf])
        Bo = np.array([modelo._beta({"uf": u})["opp"][3] for u in d26.uf])
        vot = (Bp + Bo) * tn
        pt = base_pt - Bp * tn + frac_lula * vot
        op = base_op - Bo * tn + (1 - frac_lula) * vot
        sens.append({"fracao_nao_esquerda_para_lula": frac_lula, "lula_pct": _r(100 * pt.sum() / (pt + op).sum())})

    uf_saida = {}
    for u, s in sim["uf"].items():
        s = dict(s)
        s["comparecimento_mi"] = _r(comp_uf.get(u, np.nan) / 1e6, 3)
        uf_saida[u] = s

    res = {
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "descricao": "Projeção do 2º turno 2026 (Lula x Flávio Bolsonaro, 25/10) só com a estrutura municipal do "
                         "1º turno: sem pesquisas e sem Polymarket/mercados.",
            "modelo_principal": PRINCIPAL,
            "treino": "2018 + 2022 (1º -> 2º turno, por município)",
            "n_municipios_2026": int(len(d26)),
            "fontes": ["resultados.tse.jus.br ele2026/6257 (arquivos por município)",
                       "cdn.tse.jus.br votacao_candidato_munzona / detalhe_votacao_munzona 2018 e 2022"],
        },
        "primeiro_turno_2026": {
            "lula_pct_validos": _r(100 * d26.pt1.sum() / (d26.pt1 + d26.opp1 + d26.terc1).sum()),
            "flavio_pct_validos": _r(100 * d26.opp1.sum() / (d26.pt1 + d26.opp1 + d26.terc1).sum()),
            "terceiros_esquerda_pct_validos": _r(100 * d26.terc_esq.sum() / (d26.pt1 + d26.opp1 + d26.terc1).sum()),
            "terceiros_nao_esquerda_pct_validos": _r(100 * (d26.terc1 - d26.terc_esq).sum() / (d26.pt1 + d26.opp1 + d26.terc1).sum()),
            "aptos_mi": _r(aptos / 1e6, 3), "comparecimento_mi": _r(comp1 / 1e6, 3),
            "validos_mi": _r((d26.pt1 + d26.opp1 + d26.terc1).sum() / 1e6, 3),
        },
        "nacional": {
            "p_lula": _r(sim["p_lula"], 4),
            "lula_pct_projetado": _r(100 * nac.fatia_pt_prev),
            "lula_pct_media_sim": _r(sim["media_pct"]),
            "lula_pct_dp": _r(sim["dp_pct"]),
            "lula_pct_quantis": {k: _r(v) for k, v in sim["quantis_pct"].items()},
            "validos_mi": _r(nac.validos2_prev / 1e6, 3),
            "comparecimento_mi": _r(comp_uf.sum() / 1e6, 3),
            "comparecimento_pct_aptos": _r(100 * comp_uf.sum() / aptos),
            "lula_votos_mi": _r(nac.pt2_prev / 1e6, 3),
            "flavio_votos_mi": _r(nac.opp2_prev / 1e6, 3),
            "n_sim": sim["n_sim"],
            "dp_componentes_pp": {k: _r(v, 3) for k, v in sim["dp_componentes_pp"].items()},
        },
        "coeficientes_nacionais_2018_2022": {
            "categorias_1t": CATS6,
            "fracao_para_lula": [_r(x, 3) for x in beta["pt"]],
            "fracao_para_opositor": [_r(x, 3) for x in beta["opp"]],
        },
        "uf": uf_saida,
        "validacao": validacao,
        "validacao_resumo": resumo_val,
        "variantes_2026": proj_var,
        "sensibilidade_nao_esquerda": sens,
        "comparacao_modelo_principal": {"simulador_lula_pct": 47.14, "simulador_p_lula": 0.13},
    }
    (AQUI / "resultados_municipal_2t.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    out = d26[["cd_municipio_tse", "uf", "aptos"]].copy()
    out["lula_1t_pct"] = (100 * d26.pt1 / (d26.pt1 + d26.opp1 + d26.terc1).clip(lower=1)).round(2)
    out["flavio_1t_pct"] = (100 * d26.opp1 / (d26.pt1 + d26.opp1 + d26.terc1).clip(lower=1)).round(2)
    out["lula_2t_votos"] = prev.pt2_prev.round(0).astype(int)
    out["flavio_2t_votos"] = prev.opp2_prev.round(0).astype(int)
    out["validos_2t"] = prev.validos2_prev.round(0).astype(int)
    out["lula_2t_pct"] = (100 * prev.fatia_pt_prev).round(2)
    out.to_csv(AQUI / "projecao_municipios_2t.csv", index=False)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sim", type=int, default=500_000)
    r = main(ap.parse_args().n_sim)
    n = r["nacional"]
    print(json.dumps({k: n[k] for k in ("p_lula", "lula_pct_projetado", "lula_pct_quantis", "validos_mi", "comparecimento_mi")},
                     ensure_ascii=False, indent=1))
    print(json.dumps(r["validacao_resumo"], indent=1))
    print(json.dumps(r["variantes_2026"], indent=1))
    print(json.dumps(r["sensibilidade_nao_esquerda"]))
