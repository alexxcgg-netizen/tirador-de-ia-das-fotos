"""Leitura dos dados de entrada (cenarios/dados/*.csv) para o modelo v2.

Tudo aqui é *dado* ou *mapeamento* documentado; nenhuma escolha depende do candidato.

* `faixas_salariais()`: distribuição da renda do trabalho em múltiplos do SM (PNADC 2T2026),
  Nordeste x resto do Brasil, formal x informal (o "resto" é Brasil − Nordeste em contagens).
* `cestas()`: pesos de consumo por setor de preço para cada classe de renda da POF 2017–18
  (sem aluguel imputado, que não é preço pago), com o ajuste do Nordeste para alimentos.
* `pesos_indice("ipca"|"inpc")`: pesos oficiais (ago/2026) agregados nos mesmos setores.
* `custo_sm()`: custo fiscal de +R$ 1 no SM (PLDO 2027, Anexo V).
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

DADOS = Path(__file__).resolve().parent / "dados"

# Setores de preço do modelo (ver cenarios.SETORES para as equações)
SETORES = ["A", "I", "SSM", "SO", "ALU", "ENE", "GLP", "COMB", "ONI", "REM", "PLA"]
SETOR_NOME = {
    "A": "Alimentação no domicílio",
    "I": "Bens industriais",
    "SSM": "Serviços intensivos em salário mínimo (comer fora, serviços pessoais, reparos)",
    "SO": "Outros serviços (educação, comunicação, saúde não regulada, condomínio)",
    "ALU": "Aluguel",
    "ENE": "Energia elétrica e água",
    "GLP": "Gás de botijão",
    "COMB": "Gasolina e etanol",
    "ONI": "Ônibus urbano",
    "REM": "Remédios",
    "PLA": "Plano de saúde",
}

# categoria POF -> {setor: fração}
MAPA_POF = {
    "alimentacao_domicilio": {"A": 1},
    "alimentacao_fora_domicilio": {"SSM": 1},
    "habitacao_aluguel_monetario": {"ALU": 1},
    "habitacao_condominio": {"SO": 1},
    "habitacao_energia_eletrica": {"ENE": 1},
    "habitacao_gas_domestico": {"GLP": 1},
    "habitacao_agua_esgoto": {"ENE": 1},
    "habitacao_manutencao_limpeza_outros": {"SSM": 0.5, "I": 0.5},
    "artigos_residencia": {"I": 1},
    "comunicacao_telefonia_internet": {"SO": 1},
    "vestuario": {"I": 1},
    "transporte_publico_urbano": {"ONI": 1},
    "transporte_combustivel": {"COMB": 1},
    "transporte_veiculo_manutencao": {"I": 0.5, "SSM": 0.5},
    "transporte_aquisicao_veiculos": {"I": 1},
    "transporte_viagens_outros": {"SO": 1},
    "saude_remedios": {"REM": 1},
    "saude_plano": {"PLA": 1},
    "saude_outros": {"SO": 1},
    "higiene_cuidados_pessoais": {"I": 1},
    "educacao": {"SO": 1},
    "recreacao_cultura": {"SO": 0.5, "I": 0.5},
    "fumo": {"I": 1},
    "servicos_pessoais": {"SSM": 1},
    "despesas_diversas": {"SO": 1},
}

CLASSES_POF = {
    "47558": "até 2 SM (2018)", "47559": "2–3 SM", "47560": "3–6 SM", "47561": "6–10 SM",
    "47562": "10–15 SM", "47563": "15–25 SM", "47564": "> 25 SM", "7999": "Total",
}
# Nordeste (POF, sem aluguel imputado, salario_minimo_equilibrio_geral.md §6.1): participação de
# alimentação no domicílio. Usada para reescalar o setor A nas cestas de famílias do Nordeste.
ALIM_NE_SOBRE_BR = {"47558": 25.7 / 22.9, "47559": 22.7 / 19.2, "47560": 17.4 / 16.6}


def _ler(nome):
    with open(DADOS / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=None)
def cestas() -> dict:
    """{classe: {setor: peso}} (soma 1), sem aluguel imputado."""
    out = {}
    for r in _ler("cestas_consumo_pof.csv"):
        cat = r["categoria"]
        if cat not in MAPA_POF or not r["pct_despesa_consumo"]:
            continue
        c = out.setdefault(r["classe_codigo"], {s: 0.0 for s in SETORES})
        for s, fr in MAPA_POF[cat].items():
            c[s] += fr * float(r["pct_despesa_consumo"])
    for c in out.values():
        tot = sum(c.values())
        for s in c:
            c[s] /= tot
    return out


def cesta(classe: str, nordeste: bool = False) -> dict:
    c = dict(cestas()[classe])
    if nordeste:
        f = ALIM_NE_SOBRE_BR.get(classe, 1.0)
        a_novo = c["A"] * f
        resto = 1 - c["A"]
        for s in c:
            c[s] = a_novo if s == "A" else c[s] * (1 - a_novo) / resto
    return c


@lru_cache(maxsize=None)
def pesos_indice(indice: str = "ipca") -> dict:
    """Pesos oficiais (ago/2026) por setor; categorias POF sem peso oficial no CSV recebem a
    participação da POF (classe Total) reescalada para fechar 100%."""
    col = "peso_ipca_ago2026" if indice == "ipca" else "peso_inpc_ago2026"
    of, sem = {s: 0.0 for s in SETORES}, {s: 0.0 for s in SETORES}
    for r in _ler("cestas_consumo_pof.csv"):
        if r["classe_codigo"] != "7999" or r["categoria"] not in MAPA_POF:
            continue
        for s, fr in MAPA_POF[r["categoria"]].items():
            if r[col]:
                of[s] += fr * float(r[col])
            elif r["pct_despesa_consumo"]:
                sem[s] += fr * float(r["pct_despesa_consumo"])
    tot_of = sum(of.values())
    falta = 100.0 - tot_of
    tot_sem = sum(sem.values())
    w = {s: (of[s] + falta * sem[s] / tot_sem) / 100.0 for s in SETORES}
    return w


@lru_cache(maxsize=None)
def faixas_salariais() -> dict:
    """{(regiao, vinculo): [(m_central, participação)]} com regiao em {"NE", "resto", "BR"}."""
    faixas = [("<1 SM (abaixo de 0,98)", 0.6), ("~1 SM (0,98-1,02)", 1.0), ("1-1,5 SM", 1.25),
              ("1,5-2 SM", 1.75), ("2-3 SM", 2.5), ("3-5 SM", 4.0), ("5-10 SM", 7.0), (">10 SM", 15.0)]
    cont = {}
    for r in _ler("distribuicao_salarios.csv"):
        if r["vinculo"] not in ("formal", "informal") or r["local"] not in ("Brasil", "Nordeste"):
            continue
        n = float(r["ocupados_com_rendimento_mil"])
        cont.setdefault((r["local"], r["vinculo"]), {})[r["faixa_sm"]] = n * float(r["pct_ocupados_com_rend"]) / 100
    out = {}
    for v in ("formal", "informal"):
        br, ne = cont[("Brasil", v)], cont[("Nordeste", v)]
        for reg, src in (("BR", br), ("NE", ne), ("resto", {k: br[k] - ne[k] for k in br})):
            tot = sum(src[f] for f, _ in faixas)
            out[(reg, v)] = [(m, src[f] / tot, src[f]) for f, m in faixas]
    return out


def fracao_ne_no_piso_formal() -> float:
    """Fração dos formais com ~1 SM que estão no Nordeste (pondera a elasticidade de emprego)."""
    f = faixas_salariais()
    ne = dict((m, n) for m, _, n in f[("NE", "formal")])[1.0]
    br = dict((m, n) for m, _, n in f[("BR", "formal")])[1.0]
    return ne / br


@lru_cache(maxsize=None)
def kaitz() -> dict:
    out = {}
    for r in _ler("kaitz_uf.csv"):
        out[r["local"]] = float(r["kaitz_mediana_todos_trab"])
    return out


@lru_cache(maxsize=None)
def custo_sm() -> dict:
    v = {r["indicador"]: float(r["valor"]) for r in _ler("beneficios_piso_inss.csv")}
    return {"despesa_mi": v["custo_R1_SM_total_despesas"], "receita_mi": v["custo_R1_SM_arrecadacao_previdenciaria"],
            "abono_mi": v["custo_R1_SM_abono_salarial"]}


def massa_salarial_perto_do_piso() -> float:
    """Participação, na massa de salários formal, de quem ganha até 1,5 SM [calc PNADC]."""
    f = faixas_salariais()[("BR", "formal")]
    tot = sum(m * p for m, p, _ in f)
    return sum(m * p for m, p, _ in f if m <= 1.25) / tot
