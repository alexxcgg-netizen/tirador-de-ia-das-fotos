"""Noite da apuração: resultado oficial do 1º turno (TSE), avaliação das previsões e
previsão do 2º turno condicionada ao 1º turno real.

Etapas (``--rodar-tudo`` faz todas, de forma idempotente, e pode ser repetido
enquanto a apuração avança):

a) **Resultado oficial (TSE).** Descobre o código da eleição no arquivo de
   configuração público (``/oficial/comum/config/ele-c.json``: ciclo ``ele2026``,
   eleição federal do 1º turno = 6257, 2º turno = 6258), baixa o JSON de
   presidente do Brasil, de cada UF e do exterior
   (``/oficial/ele2026/6257/dados/{uf}/{uf}-c0001-e006257-u.json``) e interpreta
   seções totalizadas (``pst``), eleitorado, comparecimento, abstenção, brancos,
   nulos, válidos e votos por candidato. Também lê o formato antigo
   "dados-simplificados" (``...-r.json``, usado em 2022). Fallbacks, nesta ordem:
   cópia local da última leitura bem-sucedida (``data/tse_1t_2026/``) e um CSV
   manual (``data/resultado_1t_manual.csv``), preenchido a partir de qualquer fonte
   que publique a apuração (G1, UOL etc.). UFs com apuração parcial são projetadas **por município**
   (``{uf}-e006257-ab.json`` + ``{uf}{cdmun}-c0001-e006257-u.json``; votos restantes = eleitorado não
   totalizado x taxa de válidos de 2022; fatias = apuradas no município ou 2022 deslocado pelo swing observado;
   ver ``projetar_uf_municipios`` e ``--replay-2022``); se os arquivos por município falharem, a UF volta ao
   método antigo (fatias apuradas, válidos / pst).
b) **Avaliação** das previsões da véspera (3 visões do modelo, modelo alternativo,
   última pesquisa de cada instituto, média das pesquisas, mercados) contra o
   resultado: erros nacional e por UF, cobertura dos intervalos, Brier e log score
   dos eventos (1º lugar, ida ao 2º turno, decisão no 1º turno).
   Saídas: ``data/avaliacao_1t.json`` e ``AVALIACAO_1T.md``.
c) **2º turno condicionado ao 1º turno real** (500 mil simulações): fatias reais por
   UF (projetadas se a apuração for parcial), transferência dos votos dos
   eliminados (matriz Quaest + incerteza Dirichlet), variação do comparecimento
   entre turnos por UF (média 2014/2018/2022), pesquisas de 2º turno (as de antes do
   1º turno com peso reduzido; as feitas depois do 1º turno, quando houver, com peso
   maior) e erro nacional/regional/estadual calibrado no histórico (1º turno real
   -> 2º turno real em 2014, 2018 e 2022). Saída: ``web/resultados_2t.json``.
d) Regera a cópia de publicação (``publicar.py``).

Uso:
    python simulador/resultado_1t.py --rodar-tudo           # noite da eleição (2026)
    python simulador/resultado_1t.py --rodar-tudo --n 50000 # mais rápido
    python simulador/resultado_1t.py --ensaio-2022          # ensaio completo com 2022
    python simulador/resultado_1t.py --gerar-fixture-2022   # (re)gera os JSON de teste de 2022
    python simulador/resultado_1t.py --replay-2022          # valida a projeção da apuração parcial (2022)
    python simulador/resultado_1t.py --rodar-tudo --sem-municipios  # só o método antigo de projeção
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import modelo as M  # noqa: E402

DADOS = AQUI / "data"
WEB = AQUI / "web"
FIXTURES = AQUI / "tests" / "fixtures" / "tse"
CACHE_2026 = DADOS / "tse_1t_2026"
MANUAL_CSV = DADOS / "resultado_1t_manual.csv"
BASE_TSE = "https://resultados.tse.jus.br"
CONFIG_TSE = BASE_TSE + "/oficial/comum/config/ele-c.json"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
       "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]
REGIAO = {"AC": "N", "AM": "N", "AP": "N", "PA": "N", "RO": "N", "RR": "N", "TO": "N", "AL": "NE", "BA": "NE",
          "CE": "NE", "MA": "NE", "PB": "NE", "PE": "NE", "PI": "NE", "RN": "NE", "SE": "NE", "DF": "CO", "GO": "CO",
          "MS": "CO", "MT": "CO", "ES": "SE", "MG": "SE", "RJ": "SE", "SP": "SE", "PR": "S", "RS": "S", "SC": "S",
          "ZZ": "EXT"}
# número na urna -> nome usado no modelo (demais candidatos -> "Outros")
NUMEROS = {
    2026: {"13": "Lula", "22": "Flavio", "55": "Caiado", "70": "Cury", "30": "Zema", "14": "Renan"},
    2022: {"13": "Lula", "22": "Bolsonaro", "12": "Ciro", "15": "Tebet"},
    2018: {"13": "Haddad", "17": "Bolsonaro", "12": "Ciro", "45": "Alckmin", "18": "Marina", "30": "Amoedo"},
    2014: {"13": "Dilma", "45": "Aecio", "40": "Marina"},
}
CANDS_ANO = {2026: M.CANDS, 2022: ["Lula", "Bolsonaro", "Ciro", "Tebet", "Outros"],
             2018: ["Haddad", "Bolsonaro", "Ciro", "Alckmin", "Marina", "Amoedo", "Outros"],
             2014: ["Dilma", "Aecio", "Marina", "Outros"]}
DATAS = {2014: ("2014-10-05", "2014-10-26"), 2018: ("2018-10-07", "2018-10-28"), 2022: ("2022-10-02", "2022-10-30"),
         2026: ("2026-10-04", "2026-10-25")}
CODIGOS_CONHECIDOS = {2026: ("ele2026", "6257", "6258"), 2022: ("ele2022", "544", "545")}

# Transferência no 2º turno Lula x Flávio, linhas [Lula, Flávio, branco/nulo/abstenção] por candidato eliminado.
# Caiado e Renan: Quaest 2-3/10/2026 (BR-02197/2026; eleitores de Caiado 43% Flávio, 19% Lula; de Renan 60%
# Flávio, 11% Lula); Cury e Zema: Quaest 24-27/09/2026 (premissas.json); Outros: inferência neutra.
TRANSF_LF_2026 = {"Caiado": [0.19, 0.43, 0.38], "Cury": [0.28, 0.35, 0.37], "Zema": [0.10, 0.80, 0.10],
                  "Renan": [0.11, 0.60, 0.29], "Outros": [0.30, 0.30, 0.40]}
FONTE_TRANSF_2026 = ("Quaest 2-3/10/2026 (Caiado, Renan; https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/"
                     "noticia/2026/10/03/quaest-presidente-3-outubro.ghtml) e 24-27/09/2026 (Cury, Zema; premissas.json); "
                     "Outros = inferência neutra")
LINHA_GENERICA = [0.35, 0.35, 0.30]

PARAM_2T = {
    "peso_pesquisas_pre_1t": {"valor": 0.25, "origem": "inferencia",
                              "nota": "Pesquisas de 2º turno feitas antes do 1º turno: peso reduzido (em 2018 e 2022 "
                                      "superestimaram o PT em 3,5 e 4,7 p.p.; a deriva entre turnos é grande)."},
    "dp_pesquisas_pos_1t_base_pp": {"valor": 1.5, "origem": "backtest",
                                    "nota": "Erro das pesquisas de 2º turno na véspera do 2º turno (BACKTEST.md, bloco nac3)."},
    "deriva_pos_1t_pp_por_21_dias": {"valor": 3.0, "origem": "inferencia",
                                     "nota": "Deriva adicional das pesquisas feitas depois do 1º turno, proporcional aos dias até o 2º turno."},
    "dp_nacional_piso_pp": {"valor": 2.0, "origem": "inferencia",
                            "nota": "Piso do erro nacional da projeção 1º turno real -> 2º turno (3 eleições só)."},
    "dp_nacional_prior_pp": {"valor": 3.0, "origem": "inferencia",
                             "nota": "Prior do dp nacional (qui-quadrado inverso escalado, 2 graus de liberdade): com 2-3 "
                                     "erros históricos, o RMS puro subestima o dp. dp = sqrt((2 x 3² + soma e²)/(2 + n))."},
    "gl_prior_dp": {"valor": 2, "origem": "inferencia"},
    "tau0_vies_pp": {"valor": 2.0, "origem": "inferencia",
                     "nota": "Viés da projeção (média dos erros históricos) encolhido para zero com prior N(0, 2²), "
                             "como no modelo principal (vies.tau0_q_pp)."},
    "gl_t": {"valor": 5, "origem": "inferencia", "nota": "Caudas t de Student para erros nacional e estaduais."},
    "alfa_dirichlet": {"valor": 30, "origem": "inferencia", "nota": "Incerteza da matriz de transferência (premissas.json)."},
    "dp_projecao_uf_logito": {"valor": 0.12, "origem": "inferencia",
                              "nota": "UF com apuração parcial: ruído nas fatias x sqrt(1 - pst); ~3 p.p. com 0% apurado."},
    "dp_uf_sem_apuracao_logito": {"valor": 0.25, "origem": "inferencia",
                                  "nota": "UF sem nenhuma seção totalizada: fatias da previsão de véspera com dp ~6 p.p."},
    "dp_abst_nacional_pp": {"valor": 1.0, "origem": "inferencia"},
    "dp_abst_uf_pp": {"valor": 1.0, "origem": "inferencia"},
    "dp_bn_pp": {"valor": 0.5, "origem": "inferencia"},
    "fator_par_imprevisto": {"valor": 1.5, "origem": "inferencia",
                             "nota": "Par de 2º turno diferente do previsto: sem matriz de transferência medida; erro x1,5."},
}


def _num(x) -> float:
    """'48,43' / '57259504' / '' -> float."""
    if x is None:
        return float("nan")
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(".", "").replace(",", ".") if "," in str(x) else str(x).strip()
    try:
        return float(s)
    except ValueError:
        return float("nan")


# ================================================================ a) TSE: descoberta, download e leitura
def descobrir_eleicao(cfg: dict, ano: int = 2026, turno: int = 1) -> dict | None:
    """Acha no ele-c.json a eleição federal (cargo Presidente) do ano/turno: {'ciclo','cd','cdt2','nm'}."""
    for pl in cfg.get("pl", []):
        if pl.get("c") != f"ele{ano}":
            continue
        for e in pl.get("e", []):
            if str(e.get("t")) != str(turno):
                continue
            cargos = [c.get("ds", "") for a in e.get("abr", []) for c in a.get("cp", [])]
            if any(c.strip().lower() == "presidente" for c in cargos):
                return {"ciclo": pl["c"], "cd": str(e["cd"]), "cdt2": str(e.get("cdt2") or ""), "nm": e.get("nm", "")}
    return None


def urls_presidente(ciclo: str, cd: str, uf: str) -> list:
    uf = uf.lower()
    cd6 = f"{int(cd):06d}"
    return [f"{BASE_TSE}/oficial/{ciclo}/{cd}/dados/{uf}/{uf}-c0001-e{cd6}-u.json",                 # 2024+
            f"{BASE_TSE}/oficial/{ciclo}/{cd}/dados-simplificados/{uf}/{uf}-c0001-e{cd6}-r.json"]   # 2022


def _baixar(url: str, timeout=20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "simulador-eleicao-2026 (pesquisa academica)",
                                               "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_tse(js: dict, numeros: dict | None = None) -> dict:
    """Lê um JSON de resultado de presidente do TSE (formato 'u' de 2024+ ou 'r' simplificado de 2022).

    Devolve {'abr','pst','psi','eleitorado','comparecimento','abstencao','validos','brancos','nulos',
    'total','votos': {nome_modelo: votos}, 'candidatos': [{n, nome, votos}], 'atualizado'}."""
    numeros = numeros or {}
    if "carg" in js:                                     # formato 2024/2026
        s, e, v = js.get("s", {}), js.get("e", {}), js.get("v", {})
        cands = []
        for car in js["carg"]:
            if str(car.get("cd")) != "1":
                continue
            for agr in car.get("agr", []):
                for par in agr.get("par", []):
                    for c in par.get("cand", []):
                        cands.append({"n": str(c.get("n")), "nome": c.get("nmu") or c.get("nm"), "votos": _num(c.get("vap")),
                                      "situacao": c.get("dvt", "")})
        out = {"abr": str(js.get("cdabr", "")).upper(), "pst": _num(s.get("pst")), "psi": _num(s.get("psi")),
               "eleitorado": _num(e.get("te")), "eleitorado_totalizado": _num(e.get("est")),
               "comparecimento": _num(e.get("c")), "abstencao": _num(e.get("a")),
               "validos": _num(v.get("vv")), "brancos": _num(v.get("vb")), "nulos": _num(v.get("tvn")),
               "total": _num(v.get("tv")), "atualizado": f"{js.get('dg', '')} {js.get('hg', '')}".strip(),
               "formato": "u"}
    elif "cand" in js:                                   # formato 2022 (dados-simplificados)
        cands = [{"n": str(c.get("n")), "nome": c.get("nm"), "votos": _num(c.get("vap")), "situacao": c.get("dvt", "")}
                 for c in js["cand"]]
        out = {"abr": str(js.get("cdabr", "")).upper(), "pst": _num(js.get("pst")), "psi": _num(js.get("psi")),
               "eleitorado": _num(js.get("e")), "comparecimento": _num(js.get("c")), "abstencao": _num(js.get("a")),
               "validos": _num(js.get("vv")), "brancos": _num(js.get("vb")), "nulos": _num(js.get("tvn")),
               "total": _num(js.get("tv")), "atualizado": f"{js.get('dg', '')} {js.get('hg', '')}".strip(),
               "formato": "r"}
    else:
        raise ValueError("JSON do TSE em formato desconhecido (sem 'carg' nem 'cand')")
    # votos anulados/sub judice não são válidos: só os candidatos 'Válido' (ou sem situação) entram
    votos = {}
    for c in cands:
        if c["situacao"] and not str(c["situacao"]).lower().startswith("v"):
            continue
        nome = numeros.get(c["n"], "Outros")
        votos[nome] = votos.get(nome, 0.0) + (0.0 if math.isnan(c["votos"]) else c["votos"])
    out["votos"] = votos
    out["candidatos"] = cands
    if not np.isfinite(out["validos"]) or out["validos"] <= 0:
        out["validos"] = float(sum(votos.values()))
    return out


def ler_manual(caminho: Path, cands: list) -> dict:
    """CSV manual: uf,pst,eleitorado,comparecimento,abstencao,validos,brancos,nulos,<um campo por candidato (votos)>."""
    df = pd.read_csv(caminho)
    out = {}
    for r in df.itertuples(index=False):
        d = r._asdict()
        uf = str(d["uf"]).upper()
        votos = {c: float(d.get(c.lower(), d.get(c, 0)) or 0) for c in cands}
        out[uf] = {"abr": uf, "pst": float(d["pst"]), "psi": float(d.get("psi", d["pst"])),
                   "eleitorado": float(d["eleitorado"]), "comparecimento": float(d["comparecimento"]),
                   "abstencao": float(d["abstencao"]), "validos": float(d.get("validos") or sum(votos.values())),
                   "brancos": float(d["brancos"]), "nulos": float(d["nulos"]), "total": float("nan"),
                   "votos": votos, "candidatos": [], "atualizado": "manual", "formato": "manual"}
    return out


def buscar_resultados(ano: int = 2026, fonte: str = "auto", diretorio: Path | None = None, log=print) -> dict:
    """Baixa/lê o resultado de presidente: {'BR': parse, 'SP': parse, ..., '_meta': {...}}.

    fonte: 'tse' (só TSE), 'diretorio' (JSONs locais em `diretorio`), 'manual' (CSV), 'auto' (TSE -> cache -> manual)."""
    numeros = NUMEROS[ano]
    cands = CANDS_ANO[ano]
    meta = {"fonte": None, "erros": []}
    res = {}
    if fonte == "diretorio":
        for uf in ["BR"] + UFS:
            for p in sorted(Path(diretorio).glob(f"{uf.lower()}-c0001-e*.json")):
                res[uf] = parse_tse(json.loads(p.read_text(encoding="utf-8")), numeros)
        meta["fonte"] = f"arquivos locais ({diretorio})"
    if fonte in ("auto", "tse"):
        ciclo, cd, cdt2 = CODIGOS_CONHECIDOS.get(ano, (f"ele{ano}", None, None))
        try:
            cfg = _baixar(CONFIG_TSE)
            el = descobrir_eleicao(cfg, ano, 1)
            if el:
                ciclo, cd, cdt2 = el["ciclo"], el["cd"], el["cdt2"]
                meta["eleicao"] = el
        except Exception as ex:                                  # noqa: BLE001
            meta["erros"].append(f"config TSE: {ex}")
        meta["codigo"] = {"ciclo": ciclo, "cd": cd, "cdt2": cdt2}
        brutos = {}
        for uf in ["BR"] + UFS:
            for url in urls_presidente(ciclo, cd, uf):
                try:
                    js = _baixar(url)
                    res[uf] = parse_tse(js, numeros)
                    brutos[uf] = js
                    break
                except Exception as ex:                          # noqa: BLE001
                    meta["erros"].append(f"{uf}: {url.rsplit('/', 1)[-1]}: {ex}")
        if "BR" in res:
            meta["fonte"] = f"TSE ({BASE_TSE}/oficial/{ciclo}/{cd}/dados/...)"
            if ano == 2026:
                CACHE_2026.mkdir(parents=True, exist_ok=True)
                for uf, js in brutos.items():
                    (CACHE_2026 / f"{uf.lower()}-c0001-e{int(cd):06d}-u.json").write_text(
                        json.dumps(js, ensure_ascii=False), encoding="utf-8")
        elif fonte == "auto" and ano == 2026 and CACHE_2026.exists() and any(CACHE_2026.glob("br-*.json")):
            log("TSE indisponível: usando a última leitura gravada em data/tse_1t_2026/")
            return buscar_resultados(ano, "diretorio", CACHE_2026, log) | {"_meta": {"fonte": "cache local (TSE indisponível)",
                                                                                   "erros": meta["erros"]}}
        elif fonte == "auto" and MANUAL_CSV.exists():
            log("TSE indisponível: usando data/resultado_1t_manual.csv")
            res = ler_manual(MANUAL_CSV, cands)
            meta["fonte"] = "CSV manual (data/resultado_1t_manual.csv)"
    if fonte == "manual":
        res = ler_manual(MANUAL_CSV, cands)
        meta["fonte"] = "CSV manual"
    res["_meta"] = meta
    return res


# ================================================================ consolidação (com projeção da apuração parcial)
def consolidar(res: dict, ano: int, ufs_ref: pd.DataFrame, previsao_uf: dict | None = None,
               proj_mun: dict | None = None) -> dict:
    """Fatias de votos válidos por UF e nacionais; UFs parciais projetadas.

    ufs_ref: DataFrame com uf, eleitores, abst1, bn1 (referência para UFs sem apuração).
    previsao_uf: {uf: {cand: fatia}} da previsão de véspera (UFs sem nenhuma seção totalizada).
    proj_mun: saída de projetar_municipios / projecao_municipal_2026; UFs parciais presentes nela usam a projeção
    por município (fatias e válidos); as demais, o método antigo (fatias apuradas, válidos / pst)."""
    pm = (proj_mun or {}).get("ufs", {})
    metodo = []
    sd_mun = np.full(len(UFS), np.nan)
    cands = CANDS_ANO[ano]
    K = len(cands)
    U = len(UFS)
    S = np.zeros((U, K)); V1 = np.zeros(U); pst = np.zeros(U); ele = np.zeros(U)
    abst = np.zeros(U); bn = np.zeros(U); fonte_uf = []
    ref = ufs_ref.set_index("uf")
    for i, uf in enumerate(UFS):
        r = res.get(uf)
        e_ref = float(ref.loc[uf, "eleitores"]) if uf in ref.index else 0.0
        if r is not None and r["validos"] > 0 and r["pst"] > 0:
            v = np.array([r["votos"].get(c, 0.0) for c in cands])
            S[i] = v / max(v.sum(), 1)
            pst[i] = min(r["pst"], 100.0)
            ele[i] = r["eleitorado"] if np.isfinite(r["eleitorado"]) and r["eleitorado"] > 0 else e_ref
            comp = r["comparecimento"]
            # abstenção/brancos/nulos medidos sobre o eleitorado das seções totalizadas
            ele_tot = r.get("eleitorado_totalizado", float("nan"))
            if not (np.isfinite(ele_tot) and ele_tot > 0):
                ele_tot = (comp + r["abstencao"]) if np.isfinite(r["abstencao"]) else ele[i] * pst[i] / 100
            abst[i] = 100 * (1 - comp / ele_tot) if ele_tot > 0 and np.isfinite(comp) and comp > 0 else ref.loc[uf, "abst1"]
            bn[i] = 100 * (r["brancos"] + r["nulos"]) / comp if np.isfinite(comp) and comp > 0 else ref.loc[uf, "bn1"]
            V1[i] = r["validos"] / (pst[i] / 100)
            fonte_uf.append("apurado" if pst[i] >= 99.995 else "parcial")
            if pst[i] < 99.995 and uf in pm and np.all(np.isfinite(pm[uf]["S"])) and pm[uf]["V"] > 0:
                S[i] = np.asarray(pm[uf]["S"], float) / np.sum(pm[uf]["S"])
                V1[i] = float(pm[uf]["V"])
                sd_mun[i] = float(pm[uf]["sd_logito"])
                metodo.append("municipios")
            else:
                metodo.append("apurado" if pst[i] >= 99.995 else "validos/pst")
        else:
            prev = (previsao_uf or {}).get(uf)
            if prev is None:
                raise ValueError(f"UF {uf} sem apuração e sem previsão de véspera")
            S[i] = np.array([prev.get(c, 0.0) for c in cands]); S[i] /= S[i].sum()
            ele[i] = e_ref
            abst[i] = float(ref.loc[uf, "abst1"]); bn[i] = float(ref.loc[uf, "bn1"])
            V1[i] = ele[i] * (1 - abst[i] / 100) * (1 - bn[i] / 100)
            fonte_uf.append("previsão")
            metodo.append("previsão")
    nat = (V1[:, None] * S).sum(0) / V1.sum()
    br = res.get("BR")
    return {"cands": cands, "S": S, "V1": V1, "pst": pst, "eleitores": ele, "abst1": abst, "bn1": bn,
            "fonte_uf": fonte_uf, "nacional": nat, "pst_nacional": float(br["pst"]) if br else float("nan"),
            "nacional_tse": ({c: br["votos"].get(c, 0.0) / max(br["validos"], 1) for c in cands} if br else None),
            "atualizado": br["atualizado"] if br else "", "br": br, "metodo_uf": metodo, "sd_mun": sd_mun}


def status_apuracao(c: dict) -> str:
    p = c["pst_nacional"]
    if not np.isfinite(p) or p <= 0:
        return "aguardando"
    return "final" if p >= 99.995 else "parcial"


# ================================================================ projeção por município (apuração parcial)
# Em vez de supor que as seções restantes de uma UF votam como as já apuradas (válidos / pst), projeta cada
# município: votos válidos restantes = eleitorado ainda não totalizado x taxa de válidos esperada (2022, ajustada
# pela variação de comparecimento observada na UF) e fatias = as apuradas no município (se parcial) ou as de 2022
# no município deslocadas pelo swing da UF medido nos municípios já apurados. Fonte ao vivo: arquivo de
# abrangência por UF ({uf}-e006257-ab.json: seções/eleitorado totalizados por município) + arquivo de cada
# município ({uf}{cdmun}-c0001-e006257-u.json, mesmo formato "u" da UF). Qualquer falha -> método antigo na UF.
MUN_2022 = DADOS / "municipios_2022.csv"
PARAM_MUN = {
    "k_shrink_uf": {"valor": 3.0, "origem": "replay_2022",
                    "nota": "Swing da UF encolhido para o swing nacional com peso de k municípios efetivos."},
    "peso_municipio": {"valor": "sqrt_validos", "origem": "replay_2022",
                       "nota": "Swing médio da UF ponderado por sqrt(válidos apurados): a capital não domina a média."},
    "ridge_inclinacoes": {"valor": 0.5, "origem": "replay_2022",
                          "nota": "Swing depende do porte e da inclinação política do município (estimado dentro das "
                                  "UFs, com todo o país); ridge puxa para swing uniforme quando há poucos apurados."},
    "min_validos_swing": {"valor": 30, "origem": "inferencia", "nota": "Municípios com menos válidos apurados ficam fora do swing."},
    "dp_swing_piso_logito": {"valor": 0.15, "origem": "replay_2022",
                             "nota": "Erro sistemático do swing (municípios apurados não são comparáveis aos restantes)."},
    "dp_mun_piso_logito": {"valor": 0.20, "origem": "replay_2022", "nota": "Piso do ruído municipal em torno do swing."},
    "dp_extrapolacao_logito": {"valor": 0.20, "origem": "replay_2022",
                               "nota": "Erro comum extra por unidade de distância (logito da fatia do PT, log do "
                                       "eleitorado) entre um município não apurado e a faixa dos já apurados: "
                                       "quando só as capitais foram apuradas, o interior é extrapolação."},
    "tolerancia_soma_uf": {"valor": 0.25, "origem": "inferencia",
                           "nota": "Soma dos municípios x votos do arquivo da UF: diferença relativa acima disso -> "
                                   "método antigo na UF (arquivos de horários diferentes divergem um pouco no início)."},
    "workers": {"valor": 24, "origem": "inferencia", "nota": "Downloads simultâneos dos arquivos por município."},
    "prazo_download_s": {"valor": 150, "origem": "inferencia",
                         "nota": "Tempo máximo baixando municípios; UF incompleta -> método antigo."},
}


def _lg(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def _ex(x):
    return 1 / (1 + np.exp(-np.asarray(x, float)))


def url_ab(ciclo: str, cd: str, uf: str) -> str:
    uf = uf.lower()
    return f"{BASE_TSE}/oficial/{ciclo}/{cd}/dados/{uf}/{uf}-e{int(cd):06d}-ab.json"


def url_municipio(ciclo: str, cd: str, uf: str, cdmun) -> str:
    uf = uf.lower()
    return f"{BASE_TSE}/oficial/{ciclo}/{cd}/dados/{uf}/{uf}{int(cdmun):05d}-c0001-e{int(cd):06d}-u.json"


def parse_ab(js: dict) -> pd.DataFrame:
    """Arquivo de abrangência da UF: uma linha por município (cd, te, est, pst, chave de versão)."""
    rows = []
    for a in js.get("abr", []):
        if str(a.get("tpabr", "")).lower() not in ("mun", "mu"):
            continue
        s, e = a.get("s", {}), a.get("e", {})
        rows.append({"cd": int(a["cdabr"]), "te": _num(e.get("te")), "est": _num(e.get("est")), "pst": _num(s.get("pst")),
                     "versao": f"{a.get('dt', '')} {a.get('ht', '')} {s.get('st', '')} {e.get('est', '')}"})
    return pd.DataFrame(rows, columns=["cd", "te", "est", "pst", "versao"])


def base_municipal(caminho: Path = MUN_2022) -> pd.DataFrame:
    b = pd.read_csv(caminho)
    return b.rename(columns={"cd_municipio_tse": "cd", "aptos": "b_aptos", "validos": "b_validos",
                             "pt_votos": "b_pt", "bolsonaro_votos": "b_opp"})[["uf", "cd", "b_aptos", "b_validos", "b_pt", "b_opp"]]


def _estatisticas_swing(m: pd.DataFrame, K: int, ia: int, ib: int) -> dict:
    """Swing (logito) observado nos municípios com votos apurados, para A (PT) e para B dentro dos não-A,
    e razão de válidos/eleitorado observada x esperada. m: colunas te, est, v0..v{K-1}, b_*."""
    V = m[[f"v{k}" for k in range(K)]].to_numpy(float)
    tot = V.sum(1)
    ok = (tot >= PARAM_MUN["min_validos_swing"]["valor"]) & m.b_validos.notna().to_numpy() & (m.b_validos.fillna(0).to_numpy() > 0) \
        & (m.est.to_numpy() > 0)
    if not ok.any():
        return {"n": 0}
    V, tot, mm = V[ok], tot[ok], m[ok]
    pa_b = (mm.b_pt / mm.b_validos).to_numpy()
    pb_b = (mm.b_opp / (mm.b_validos - mm.b_pt).clip(lower=1)).to_numpy()
    yA = _lg(V[:, ia] / tot) - _lg(pa_b)
    yB = _lg(V[:, ib] / np.maximum(tot - V[:, ia], 1)) - _lg(pb_b)
    taxa_obs = tot / mm.est.to_numpy()
    taxa_esp = (mm.b_validos / mm.b_aptos).to_numpy()
    w = np.sqrt(tot)
    X = np.column_stack([_lg(pa_b), np.log(mm.b_aptos.clip(lower=1).to_numpy(float))])
    return {"n": int(ok.sum()), "w": w, "yA": yA, "yB": yB, "ylr": np.log(taxa_obs / taxa_esp), "votos": tot, "X": X}


def _x_municipios(m: pd.DataFrame) -> np.ndarray:
    """Covariáveis do swing: logito da fatia do PT na referência e log do eleitorado na referência."""
    b = m.b_validos.fillna(0).to_numpy(float)
    pa = np.where(b > 0, m.b_pt.fillna(0).to_numpy(float) / np.maximum(b, 1), 0.5)
    return np.column_stack([_lg(pa), np.log(np.maximum(m.b_aptos.fillna(1).to_numpy(float), 1))])


def _quantil_w(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return float(x[o][min(np.searchsorted(c, q), len(x) - 1)])


def _inclinacoes(sts: list, lam: float) -> dict:
    """Inclinações do swing nas covariáveis, estimadas DENTRO das UFs (cada UF centrada na sua média ponderada)
    com todos os municípios apurados do país; ridge (lam x soma dos pesos) puxa para swing uniforme."""
    Xs, ys, ws = {"A": [], "B": []}, {"A": [], "B": []}, []
    for st in sts:
        w = st["w"]
        xc = st["X"] - (w[:, None] * st["X"]).sum(0) / w.sum()
        for k in ("A", "B"):
            y = st["y" + k]
            ys[k].append(y - _media_w(y, w))
            Xs[k].append(xc)
        ws.append(w)
    out = {}
    if not ws:
        return {"bA": np.zeros(2), "bB": np.zeros(2)}
    w = np.concatenate(ws)
    Xall = np.concatenate([st["X"] for st in sts])
    # faixa das covariáveis nos municípios apurados: a projeção não extrapola a inclinação para fora dela
    out["x_lo"] = np.array([_quantil_w(Xall[:, j], w, 0.05) for j in range(Xall.shape[1])])
    out["x_hi"] = np.array([_quantil_w(Xall[:, j], w, 0.95) for j in range(Xall.shape[1])])
    for k in ("A", "B"):
        X, y = np.concatenate(Xs[k]), np.concatenate(ys[k])
        Xw = X * w[:, None]
        sx = X.std(0) + 1e-9
        A_ = Xw.T @ X + lam * w.sum() * np.diag(sx ** 2)
        out["b" + k] = np.linalg.solve(A_, Xw.T @ y) if len(y) > 5 else np.zeros(2)
    return out


def _media_w(y, w):
    return float(np.sum(w * y) / np.sum(w))


def _resumo_swing(st: dict, incl: dict | None = None) -> dict:
    """Intercepto do swing (swing médio depois de descontar as covariáveis), dispersão e variação de válidos."""
    if not st or st.get("n", 0) == 0:
        return {"n_eff": 0.0, "dA": 0.0, "dB": 0.0, "lr": 0.0, "sA": 0.15, "sB": 0.15}
    incl = incl or {"bA": np.zeros(2), "bB": np.zeros(2)}
    w = st["w"]
    n_eff = float(w.sum() ** 2 / np.sum(w ** 2))
    X = st["X"] if incl.get("x_lo") is None else np.clip(st["X"], incl["x_lo"], incl["x_hi"])
    yA = st["yA"] - X @ incl["bA"]
    yB = st["yB"] - X @ incl["bB"]
    out = {"n_eff": n_eff, "dA": _media_w(yA, w), "dB": _media_w(yB, w), "lr": _media_w(st["ylr"], w)}
    for k, y in (("sA", yA), ("sB", yB)):
        out[k] = float(np.sqrt(_media_w((y - out["d" + k[1]]) ** 2, w))) if n_eff > 1.5 else 0.15
    return out


def projetar_uf_municipios(m: pd.DataFrame, K: int, ia: int = 0, ib: int = 1, prior: dict | None = None) -> dict:
    """Projeção de uma UF a partir dos municípios.

    m: uma linha por município: te (eleitorado atual), est (eleitorado das seções totalizadas), v0..v{K-1} (votos
    apurados por candidato), b_aptos, b_validos, b_pt, b_opp (eleição de referência; NaN se município novo).
    prior: swing nacional {'dA','dB','lr'} para o encolhimento. Devolve {'S','V','sd_logito','apurado','swing'}."""
    prior = prior or {"dA": 0.0, "dB": 0.0, "lr": 0.0}
    incl = {"bA": np.asarray(prior.get("bA", np.zeros(2))), "bB": np.asarray(prior.get("bB", np.zeros(2))),
            "x_lo": prior.get("x_lo"), "x_hi": prior.get("x_hi")}
    m = m.reset_index(drop=True)
    V = m[[f"v{k}" for k in range(K)]].to_numpy(float)
    tot = V.sum(1)
    te = m.te.to_numpy(float)
    est = np.minimum(m.est.fillna(0).to_numpy(float), te)
    f = np.where(te > 0, est / np.maximum(te, 1), 1.0)
    st = _estatisticas_swing(m, K, ia, ib)
    r = _resumo_swing(st, incl)
    kk = PARAM_MUN["k_shrink_uf"]["valor"]
    n = r["n_eff"]
    dA = (n * r["dA"] + kk * prior["dA"]) / (n + kk)
    dB = (n * r["dB"] + kk * prior["dB"]) / (n + kk)
    lr = (n * r["lr"] + kk * prior.get("lr", 0.0)) / (n + kk)
    # fatias dos candidatos menores (fora A e B): composição apurada na UF
    menores = [k for k in range(K) if k not in (ia, ib)]
    vm = V[:, menores].sum(0)
    comp_men = vm / vm.sum() if vm.sum() > 0 else np.full(len(menores), 1 / max(len(menores), 1))
    S_uf_ap = V.sum(0) / max(V.sum(), 1)
    tem_b = m.b_validos.notna().to_numpy() & (m.b_validos.fillna(0).to_numpy() > 0)
    bval = m.b_validos.fillna(1).to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        pa_b = np.where(tem_b, m.b_pt.fillna(0).to_numpy(float) / bval, np.nan)
    pb_b = np.where(tem_b, m.b_opp.fillna(0).to_numpy(float) / np.maximum(bval - m.b_pt.fillna(0).to_numpy(float), 1), np.nan)
    Xm = _x_municipios(m)
    fora = np.zeros(len(m))                 # distância (covariáveis) até a faixa dos municípios já apurados
    if incl.get("x_lo") is not None:
        Xc = np.clip(Xm, incl["x_lo"], incl["x_hi"])
        fora = np.abs(Xm - Xc).sum(1)
        Xm = Xc
    sA = _ex(_lg(pa_b) + dA + Xm @ incl["bA"])
    sB = (1 - sA) * _ex(_lg(pb_b) + dB + Xm @ incl["bB"])
    Sp = np.zeros((len(m), K))
    Sp[:, ia], Sp[:, ib] = sA, sB
    Sp[:, menores] = (1 - sA - sB)[:, None] * comp_men[None]
    Sp[~tem_b] = S_uf_ap if V.sum() > 0 else np.full(K, 1 / K)
    # taxa de válidos por eleitor para o eleitorado restante
    taxa_esp = np.where(tem_b, bval / np.maximum(m.b_aptos.fillna(1).to_numpy(float), 1), np.nan) * math.exp(lr)
    taxa_uf_obs = tot.sum() / est.sum() if est.sum() > 0 else np.nan
    taxa_esp = np.where(np.isfinite(taxa_esp), taxa_esp, taxa_uf_obs if np.isfinite(taxa_uf_obs) else 0.8)
    taxa_obs = np.where(est > 0, tot / np.maximum(est, 1), taxa_esp)
    taxa = f * taxa_obs + (1 - f) * taxa_esp
    # fatias do eleitorado restante: apuradas no município (se houver votos) ou a projeção por swing
    sh_obs = np.where(tot[:, None] > 0, V / np.maximum(tot, 1)[:, None], 0)
    S_rest = np.where((tot > 0)[:, None], sh_obs, Sp)
    R = np.maximum(te - est, 0) * taxa
    votos = V.sum(0) + (R[:, None] * S_rest).sum(0)
    Vtot = float(votos.sum())
    S = votos / max(Vtot, 1)
    # incerteza na fatia de A (p.p. de fatia): ruído municipal independente + erro comum do swing
    sig_mun = max(r["sA"], PARAM_MUN["dp_mun_piso_logito"]["valor"])
    se_sw = math.sqrt(sig_mun ** 2 / max(n + kk, 1) + PARAM_MUN["dp_swing_piso_logito"]["valor"] ** 2)
    sa = S_rest[:, ia]
    deriv = sa * (1 - sa) * R
    nao_ap = tot <= 0
    fat = np.where(nao_ap, 1.0, np.sqrt(np.clip(1 - f, 0, 1)) * 0.5)      # parcial: só o resto do município varia
    var = np.sum((deriv * sig_mun * fat) ** 2) + (np.sum(deriv[nao_ap]) * se_sw) ** 2 \
        + (np.sum(deriv[~nao_ap]) * se_sw * 0.5) ** 2 \
        + (np.sum(deriv[nao_ap] * fora[nao_ap]) * PARAM_MUN["dp_extrapolacao_logito"]["valor"]) ** 2
    sd_fatia = math.sqrt(var) / max(Vtot, 1)
    sA_uf = float(np.clip(S[ia], 0.01, 0.99))
    return {"S": S, "V": Vtot, "sd_fatia_a": sd_fatia, "sd_logito": sd_fatia / (sA_uf * (1 - sA_uf)),
            "apurado_frac": float(est.sum() / max(te.sum(), 1)), "n_municipios": int(len(m)),
            "n_municipios_com_votos": int((tot > 0).sum()),
            "swing": {"dA": dA, "dB": dB, "lr": lr, "n_eff": n, "dA_bruto": r["dA"], "sig_mun": sig_mun, "se_swing": se_sw},
            "_st": st}


def projetar_municipios(dados: dict, K: int, ia: int = 0, ib: int = 1) -> dict:
    """dados: {uf: DataFrame (ver projetar_uf_municipios)}. Duas passadas: swing nacional (média dos municípios
    apurados de todas as UFs, ponderada) como prior, depois cada UF encolhida para ele."""
    sts = [_estatisticas_swing(m, K, ia, ib) for m in dados.values()]
    sts = [s for s in sts if s.get("n", 0) > 0]
    incl = _inclinacoes(sts, PARAM_MUN["ridge_inclinacoes"]["valor"]) if sts else {"bA": np.zeros(2), "bB": np.zeros(2)}
    if sts:
        junto = {k: np.concatenate([s[k] for s in sts]) for k in ("w", "yA", "yB", "ylr", "X")}
        junto["n"] = sum(s["n"] for s in sts)
        rn = _resumo_swing(junto, incl)
        prior = {"dA": rn["dA"], "dB": rn["dB"], "lr": rn["lr"]} | incl
    else:
        prior = {"dA": 0.0, "dB": 0.0, "lr": 0.0} | incl
    out = {uf: projetar_uf_municipios(m, K, ia, ib, prior) for uf, m in dados.items()}
    return {"ufs": out, "prior_nacional": prior}


def baixar_municipios(ciclo: str, cd: str, ufs: list, numeros: dict, cands: list, log=print,
                      cache_dir: Path | None = None, baixar=None) -> tuple[dict, dict]:
    """Baixa abrangência + arquivos por município (só os que têm seções totalizadas e mudaram desde a última
    leitura). Devolve ({uf: DataFrame pronto para projetar}, meta). UFs com falha ficam de fora."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    baixar = baixar or _baixar
    cache_dir = cache_dir or (CACHE_2026 / "municipios")
    cache_p = cache_dir / "cache.json"
    try:
        cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    except Exception:                                            # noqa: BLE001
        cache = {}
    base = base_municipal()
    meta = {"erros": [], "baixados": 0, "do_cache": 0, "ufs_ok": [], "ufs_falha": []}
    abr = {}
    for uf in ufs:
        try:
            abr[uf] = parse_ab(baixar(url_ab(ciclo, cd, uf)))
        except Exception as ex:                                  # noqa: BLE001
            meta["erros"].append(f"ab {uf}: {ex}")
            meta["ufs_falha"].append(uf)
    tarefas = []
    for uf, a in abr.items():
        for r in a.itertuples():
            if not (r.est > 0):
                continue
            ch = f"{uf}-{r.cd}"
            if ch in cache and cache[ch].get("versao") == r.versao:
                meta["do_cache"] += 1
                continue
            tarefas.append((uf, r.cd, r.versao))
    t0 = time.perf_counter()
    prazo = PARAM_MUN["prazo_download_s"]["valor"]
    falhas = set()

    def um(t):
        uf, cdm, ver = t
        p = parse_tse(baixar(url_municipio(ciclo, cd, uf, cdm)), numeros)
        return t, {"versao": ver, "est": p.get("eleitorado_totalizado"), "te": p.get("eleitorado"),
                   "votos": [float(p["votos"].get(c, 0.0)) for c in cands]}
    if tarefas:
        with ThreadPoolExecutor(max_workers=PARAM_MUN["workers"]["valor"]) as ex:
            futs = [ex.submit(um, t) for t in tarefas]
            for fu in as_completed(futs):
                try:
                    t, d = fu.result()
                    cache[f"{t[0]}-{t[1]}"] = d
                    meta["baixados"] += 1
                except Exception as e:                           # noqa: BLE001
                    meta["erros"].append(f"municipio: {e}")
                if time.perf_counter() - t0 > prazo:
                    meta["erros"].append("prazo de download esgotado")
                    for g in futs:
                        g.cancel()
                    break
    for t in tarefas:
        ch = f"{t[0]}-{t[1]}"
        if ch not in cache or cache[ch].get("versao") != t[2]:
            falhas.add(t[0])
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_p.write_text(json.dumps(cache), encoding="utf-8")
    except Exception as e:                                       # noqa: BLE001
        meta["erros"].append(f"cache: {e}")
    dados = {}
    K = len(cands)
    for uf, a in abr.items():
        if uf in falhas or a.empty:
            meta["ufs_falha"].append(uf)
            continue
        m = a.copy()
        for k in range(K):
            m[f"v{k}"] = 0.0
        for i, r in enumerate(m.itertuples()):
            ch = f"{uf}-{r.cd}"
            if r.est > 0 and ch in cache:
                m.loc[i, [f"v{k}" for k in range(K)]] = cache[ch]["votos"]
        m = m.merge(base[base.uf == uf].drop(columns="uf"), on="cd", how="left")
        dados[uf] = m
        meta["ufs_ok"].append(uf)
    meta["tempo_s"] = round(time.perf_counter() - t0, 1)
    return dados, meta


def projecao_municipal_2026(res: dict, cd_info: dict | None, log=print, baixar=None) -> dict | None:
    """Projeção por município das UFs com apuração parcial (2026). None se não der (método antigo)."""
    try:
        ciclo, cd = (cd_info or {}).get("ciclo") or "ele2026", (cd_info or {}).get("cd") or "6257"
        cands = CANDS_ANO[2026]
        parciais = [u for u in UFS if u in res and isinstance(res[u], dict) and 0 < res[u].get("pst", 0) < 99.995]
        if not parciais:
            return None
        dados, meta = baixar_municipios(ciclo, cd, parciais, NUMEROS[2026], cands, log=log, baixar=baixar)
        if not dados:
            log("projeção por município indisponível: método antigo (válidos / pst) em todas as UFs")
            return None
        pj = projetar_municipios(dados, len(cands), cands.index("Lula"), cands.index("Flavio"))
        # coerência com o arquivo da UF: se a soma dos municípios não bate com o apurado na UF, método antigo na UF
        for uf in list(pj["ufs"]):
            v_mun = float(dados[uf][[f"v{k}" for k in range(len(cands))]].to_numpy().sum())
            v_uf = float(sum(res[uf]["votos"].values()))
            if v_uf > 0 and abs(v_mun - v_uf) / v_uf > PARAM_MUN["tolerancia_soma_uf"]["valor"]:
                meta["erros"].append(f"{uf}: municípios somam {v_mun:.0f} válidos, UF {v_uf:.0f}: método antigo")
                pj["ufs"].pop(uf)
        pj["meta"] = meta
        log(f"projeção por município: {len(pj['ufs'])} UFs; {meta['baixados']} arquivos baixados, "
            f"{meta['do_cache']} do cache, {meta['tempo_s']} s")
        return pj
    except Exception as ex:                                       # noqa: BLE001
        log(f"projeção por município falhou ({ex}): método antigo")
        return None


# ---------------------------------------------------------------- replay com 2022 (validação da projeção)
REPLAY_ZONAS = DADOS / "replay_munzona_2022.csv"
MUN_2018 = DADOS / "municipios_2018.csv"
CENARIOS_REPLAY = ("grandes_primeiro", "pequenos_primeiro", "direita_primeiro", "aleatorio")


def _ordem_replay(z: pd.DataFrame, cenario: str, rng) -> np.ndarray:
    tam = z.groupby(["uf", "cd_municipio_tse"]).aptos.transform("sum").to_numpy(float)
    ruido = rng.standard_normal(len(z))
    if cenario == "grandes_primeiro":          # capitais/grandes municípios primeiro (ordem por porte + ruído)
        chave = -np.log(tam) + 0.7 * ruido
    elif cenario == "pequenos_primeiro":
        chave = np.log(tam) + 0.7 * ruido
    elif cenario == "direita_primeiro":       # como em 2022: Bolsonaro na frente no início da apuração
        chave = -(z.bolsonaro / z.validos.clip(lower=1)).to_numpy() * 6 + 0.7 * ruido
    else:
        chave = ruido
    return chave


def replay_2022(cenario: str, pontos=(0.10, 0.25, 0.50, 0.75), seed: int = 1, z: pd.DataFrame | None = None,
                base: pd.DataFrame | None = None) -> list:
    """Reapura o 1º turno de 2022 em ordem não aleatória (zona eleitoral como unidade de totalização; cada UF
    num ritmo próprio) e compara, em cada ponto da apuração, a projeção antiga (válidos / pst por UF) e a nova
    (por município, referência 2018) com o resultado final. Erros em p.p. de votos válidos."""
    cands = ["Lula", "Bolsonaro", "Ciro", "Tebet", "Outros"]
    cols = ["lula", "bolsonaro", "ciro", "tebet", "outros"]
    z = (pd.read_csv(REPLAY_ZONAS) if z is None else z).copy()
    base = base_municipal(MUN_2018) if base is None else base
    rng = np.random.default_rng(seed)
    z["chave"] = _ordem_replay(z, cenario, rng)
    z = z.sort_values(["uf", "chave"]).reset_index(drop=True)
    final_uf = z.groupby("uf")[cols].sum()
    final_br = final_uf.sum() / final_uf.to_numpy().sum()
    final_s_uf = final_uf.div(final_uf.sum(axis=1), axis=0)
    ritmo = {u: float(np.clip(rng.lognormal(0, 0.3), 0.4, 2.5)) for u in final_uf.index}
    mun_tot = z.groupby(["uf", "cd_municipio_tse"], as_index=False).aptos.sum().rename(columns={"cd_municipio_tse": "cd",
                                                                                               "aptos": "te"})
    out = []
    for p in pontos:
        # fração apurada de cada UF; ajusta o ritmo para que o Brasil esteja em p
        def frac_uf(esc):
            return {u: float(np.clip(p * ritmo[u] * esc, 0.01, 1.0)) for u in ritmo}
        lo, hi = 0.05, 20.0
        apt_uf = z.groupby("uf").aptos.sum()
        for _ in range(40):
            mid = (lo + hi) / 2
            fu = frac_uf(mid)
            tot = sum(fu[u] * apt_uf[u] for u in fu) / apt_uf.sum()
            lo, hi = (mid, hi) if tot < p else (lo, mid)
        fu = frac_uf((lo + hi) / 2)
        cum = z.groupby("uf").aptos.cumsum() - z.aptos
        alvo = z.uf.map(fu) * z.uf.map(apt_uf)
        fr = np.clip((alvo - cum) / z.aptos.clip(lower=1), 0, 1)        # fração apurada de cada zona
        ap = z[["uf", "cd_municipio_tse"]].copy()
        ap["est"] = z.aptos * fr
        for k, c in enumerate(cols):
            ap[f"v{k}"] = z[c] * fr
        ap = ap.groupby(["uf", "cd_municipio_tse"], as_index=False).sum().rename(columns={"cd_municipio_tse": "cd"})
        ap = ap.merge(mun_tot, on=["uf", "cd"])
        # método antigo
        ant_S, ant_V, nov_S, nov_V, sd_a = {}, {}, {}, {}, {}
        dados = {}
        for uf, g in ap.groupby("uf"):
            v = g[[f"v{k}" for k in range(5)]].to_numpy().sum(0)
            pst = g.est.sum() / g.te.sum()
            ant_S[uf] = v / v.sum()
            ant_V[uf] = v.sum() / pst
            dados[uf] = g.merge(base[base.uf == uf].drop(columns="uf"), on="cd", how="left")
        pj = projetar_municipios(dados, 5, 0, 1)
        for uf, r in pj["ufs"].items():
            nov_S[uf], nov_V[uf], sd_a[uf] = r["S"], r["V"], r["sd_fatia_a"]
        ufs = sorted(ant_S)
        res = {"cenario": cenario, "seed": seed, "apurado_pct": round(100 * float(ap.est.sum() / ap.te.sum()), 1)}
        for nome, SS, VV in (("antigo", ant_S, ant_V), ("novo", nov_S, nov_V)):
            nat = sum(VV[u] * SS[u] for u in ufs) / sum(VV[u] for u in ufs)
            res[f"{nome}_erro_lula_pp"] = round(100 * float(nat[0] - final_br["lula"]), 3)
            res[f"{nome}_erro_margem_pp"] = round(100 * float((nat[0] - nat[1]) - (final_br["lula"] - final_br["bolsonaro"])), 3)
            erros_uf = [100 * (SS[u][0] - final_s_uf.loc[u, "lula"]) for u in ufs if u != "ZZ"]
            res[f"{nome}_mae_uf_lula_pp"] = round(float(np.mean(np.abs(erros_uf))), 3)
            res[f"{nome}_max_uf_lula_pp"] = round(float(np.max(np.abs(erros_uf))), 3)
            res[f"{nome}_erro_validos_pct"] = round(100 * float(sum(VV.values()) / final_uf.to_numpy().sum() - 1), 3)
        zsc = [abs(nov_S[u][0] - final_s_uf.loc[u, "lula"]) / max(sd_a[u], 1e-6) for u in ufs if u != "ZZ"]
        res["novo_cobertura_90_uf"] = round(float(np.mean(np.array(zsc) <= 1.645)), 3)
        res["novo_sd_medio_uf_pp"] = round(100 * float(np.mean([sd_a[u] for u in ufs if u != "ZZ"])), 3)
        out.append(res)
    return out


def replay_resumo(cenarios=CENARIOS_REPLAY, seeds=range(1, 6), pontos=(0.10, 0.25, 0.50, 0.75)) -> pd.DataFrame:
    z = pd.read_csv(REPLAY_ZONAS)
    base = base_municipal(MUN_2018)
    linhas = [r | {"ponto": p} for c in cenarios for s in seeds
              for p, r in zip(pontos, replay_2022(c, pontos, s, z, base))]
    t = pd.DataFrame(linhas)
    num = [c for c in t.columns if c.startswith(("antigo", "novo"))]
    a = t.copy()
    for c in num:
        if "erro" in c and "mae" not in c and "max" not in c:
            a[c] = a[c].abs()
    return a.groupby(["cenario", "ponto"])[["apurado_pct"] + num].mean().round(2)


# ================================================================ histórico (2014/2018/2022)
def _hist():
    return pd.read_csv(DADOS / "resultados_uf_2002_2022.csv")


def historico_ano(ano: int) -> dict:
    """1º e 2º turno reais por UF de um ano (fatias em válidos; PT, adversário, T)."""
    h = _hist()
    r1 = h[(h.ano == ano) & (h.turno == 1)].set_index("uf")
    r2 = h[(h.ano == ano) & (h.turno == 2)].set_index("uf")
    ufs = [u for u in UFS if u in r1.index]
    L = r1.loc[ufs, "pt_pct_validos"].values / 100
    F = r1.loc[ufs, "oponente_pct_validos"].values / 100
    return {"ufs": ufs, "L": L, "F": F, "T": 1 - L - F, "V1": r1.loc[ufs, "votos_validos"].values.astype(float),
            "V2": r2.loc[ufs, "votos_validos"].values.astype(float), "q": r2.loc[ufs, "pt_pct_validos"].values / 100,
            "q_br": float(r2.loc["BR", "pt_pct_validos"]) / 100, "abst1": r1.loc[ufs, "abstencao_pct"].values,
            "abst2": r2.loc[ufs, "abstencao_pct"].values,
            "bn1": (r1.loc[ufs, "branco_pct_comp"] + r1.loc[ufs, "nulo_pct_comp"]).values,
            "bn2": (r2.loc[ufs, "branco_pct_comp"] + r2.loc[ufs, "nulo_pct_comp"]).values,
            "eleitores": r1.loc[ufs, "eleitorado"].values.astype(float)}


def delta_comparecimento(anos=(2014, 2018, 2022)) -> pd.DataFrame:
    """Variação média (2º − 1º turno) da abstenção e de brancos+nulos por UF, em p.p."""
    rows = []
    for a in anos:
        d = historico_ano(a)
        for i, u in enumerate(d["ufs"]):
            rows.append({"ano": a, "uf": u, "d_abst": d["abst2"][i] - d["abst1"][i], "d_bn": d["bn2"][i] - d["bn1"][i]})
    t = pd.DataFrame(rows)
    return t.groupby("uf")[["d_abst", "d_bn"]].mean().reindex(UFS).fillna(t[["d_abst", "d_bn"]].mean())


def _q_transf(L, F, T, row):
    """2º turno PT pela via de transferência (linha genérica [PT, adversário, fora] para todos os menores)."""
    return (L + T * row[0]) / (L + F + T * (row[0] + row[1]))


def _desloc(q, w, alvo):
    return M._resolver_desloc(np.clip(q, 1e-4, 1 - 1e-4), w, alvo)


_PRE1T = {}


def preditores_hist(ano: int, P: dict | None = None) -> dict:
    """O que se sabia na véspera do 1º turno de `ano`: linha de transferência implícita (pesquisas pareadas de
    1º e 2º turno) e média das pesquisas de 2º turno PT x adversário (house effects, recência)."""
    if ano in _PRE1T:
        return _PRE1T[ano]
    import backtest as BT
    P = P or M.carregar_premissas()
    b = BT.construir_base_hist(ano, "v1", P)
    out = {"linha": [float(x) for x in b.e.transf[0]], "q_pesquisas": float(b.q_nat) if b.tem_2t else None}
    _PRE1T[ano] = out
    return out


def ecologico(ano: int) -> dict:
    """Estimativa ecológica (TSE) do destino dos votos entre turnos: dos votos ganhos por PT e adversário,
    fração do PT; e regressão por UF do ganho do PT (p.p. dos válidos) na fatia dos menores no 1º turno."""
    h = _hist()
    r1 = h[(h.ano == ano) & (h.turno == 1)].set_index("uf")
    r2 = h[(h.ano == ano) & (h.turno == 2)].set_index("uf")
    dpt = r2.loc["BR", "pt_votos"] - r1.loc["BR", "pt_votos"]
    dop = r2.loc["BR", "oponente_votos"] - r1.loc["BR", "oponente_votos"]
    menores = r1.loc["BR", "votos_validos"] - r1.loc["BR", "pt_votos"] - r1.loc["BR", "oponente_votos"]
    ufs = [u for u in UFS if u in r1.index and u != "ZZ"]
    T = 1 - (r1.loc[ufs, "pt_pct_validos"] + r1.loc[ufs, "oponente_pct_validos"]) / 100
    g = (r2.loc[ufs, "pt_pct_validos"] - r1.loc[ufs, "pt_pct_validos"]) / 100
    X = np.column_stack([np.ones(len(ufs)), T.values])
    coef = np.linalg.lstsq(X, g.values, rcond=None)[0]
    return {"ano": ano, "fracao_pt_dos_ganhos": float(dpt / (dpt + dop)),
            "ganho_total_sobre_menores": float((dpt + dop) / menores),
            "inclinacao_ganho_pt_por_menores_uf": float(coef[1]), "intercepto_uf": float(coef[0])}


def calibrar_2t(anos: tuple, w_pre: float, P: dict | None = None) -> dict:
    """Erros históricos da projeção '1º turno real -> 2º turno' em cada ano de `anos`, com o que se sabia na
    véspera do 1º turno (linha de transferência implícita, pesquisas de 2º turno com peso w_pre).
    Devolve dp nacional (RMS dos erros), dp regional e estadual (resíduos depois do deslocamento nacional)."""
    erros, res_uf, detalhe = [], [], []
    for a in anos:
        d = historico_ano(a)
        pre = preditores_hist(a, P)
        m = np.array([u != "ZZ" for u in d["ufs"]])
        qtr = _q_transf(d["L"], d["F"], d["T"], pre["linha"])
        w2 = d["V1"]
        qtr_br = float(np.sum(w2 * qtr) / w2.sum())
        if pre["q_pesquisas"] is not None:
            qc = float(M.expit(w_pre * M.logit(pre["q_pesquisas"]) + (1 - w_pre) * M.logit(qtr_br)))
        else:
            qc = qtr_br
        e = 100 * (qc - d["q_br"])
        erros.append(e)
        # resíduos por UF depois de ajustar o nível nacional ao real
        dd = _desloc(qtr, w2, d["q_br"])
        r = (M.logit(d["q"]) - M.logit(qtr) - dd)[m]
        pp = r * 100 * d["q"][m] * (1 - d["q"][m])
        reg = np.array([REGIAO[u] for u in np.array(d["ufs"])[m]])
        for u, x, g in zip(np.array(d["ufs"])[m], pp, reg):
            res_uf.append({"ano": a, "uf": u, "regiao": g, "res_pp": float(x)})
        detalhe.append({"ano": a, "q_real": 100 * d["q_br"], "q_transferencia": 100 * qtr_br,
                        "q_pesquisas_pre_1t": None if pre["q_pesquisas"] is None else 100 * pre["q_pesquisas"],
                        "q_projecao": 100 * qc, "erro_pp": e, "linha_transferencia": pre["linha"],
                        "erro_so_transferencia_pp": 100 * (qtr_br - d["q_br"]),
                        "erro_so_pesquisas_pp": None if pre["q_pesquisas"] is None else 100 * (pre["q_pesquisas"] - d["q_br"])})
    t = pd.DataFrame(res_uf)
    # componente regional: média dos resíduos por região e ano; estadual: resto
    t["reg_media"] = t.groupby(["ano", "regiao"]).res_pp.transform("mean")
    sd_reg = float(np.sqrt(np.mean(t.groupby(["ano", "regiao"]).res_pp.mean() ** 2)))
    sd_uf = float(np.sqrt(np.mean((t.res_pp - t.reg_media) ** 2)))
    piso = PARAM_2T["dp_nacional_piso_pp"]["valor"]
    s0, nu0 = PARAM_2T["dp_nacional_prior_pp"]["valor"], PARAM_2T["gl_prior_dp"]["valor"]
    rms = float(np.sqrt(np.mean(np.square(erros))))
    sd_nat = max(math.sqrt((nu0 * s0 ** 2 + float(np.sum(np.square(erros)))) / (nu0 + len(erros))), piso)
    vies, vies_dp = M.eb_vies(erros, sd_nat, PARAM_2T["tau0_vies_pp"]["valor"])
    return {"anos": list(anos), "dp_nacional_pp": sd_nat, "rms_erros_pp": rms, "vies_pp": vies, "vies_dp_pp": vies_dp,
            "dp_regional_pp": sd_reg, "dp_uf_pp": sd_uf, "erros_pp": erros, "detalhe": detalhe}


# ================================================================ c) simulação do 2º turno
def simular_2t(c: dict, par: tuple, transf: dict, q_pesq: dict | None, cal: dict, d_comp: pd.DataFrame,
               n: int = 500_000, seed: int = 20261025, lote: int = 100_000, par_previsto: bool = True,
               sd_proj: np.ndarray | None = None) -> dict:
    """2º turno par[0] x par[1] condicionado ao 1º turno real (consolidado em `c`).

    transf: {candidato eliminado: [p_A, p_B, p_fora]}; q_pesq: {'q': fatia de A, 'peso': w} ou None."""
    cands = c["cands"]
    A, B = cands.index(par[0]), cands.index(par[1])
    elim = [k for k in range(len(cands)) if k not in (A, B)]
    rows = np.array([transf.get(cands[k], LINHA_GENERICA) for k in elim], float)
    U = len(UFS)
    S0 = c["S"]
    alfa = PARAM_2T["alfa_dirichlet"]["valor"]
    gl = PARAM_2T["gl_t"]["valor"]
    fator = 1.0 if par_previsto else PARAM_2T["fator_par_imprevisto"]["valor"]
    reg_idx = np.array([["N", "NE", "CO", "SE", "S", "EXT"].index(REGIAO[u]) for u in UFS])
    sd_proj = np.zeros(U) if sd_proj is None else sd_proj

    def q_transf(S, R):
        num = S[..., A] + (S[..., elim] * R[..., 0]).sum(-1)
        den = S[..., A] + S[..., B] + (S[..., elim] * (R[..., 0] + R[..., 1])).sum(-1)
        return num / den

    abst2_c = np.clip(c["abst1"] + d_comp["d_abst"].values, 3, 80)
    bn2_c = np.clip(c["bn1"] + d_comp["d_bn"].values, 0.3, 30)
    W2c = c["eleitores"] * (1 - abst2_c / 100) * (1 - bn2_c / 100)
    qtr_c = q_transf(S0[None], rows[None, None])[0]
    qtr_br = float(np.sum(W2c * qtr_c) / W2c.sum())
    if q_pesq is not None and q_pesq.get("q") is not None:
        w = q_pesq["peso"]
        q_centro = float(M.expit(w * M.logit(q_pesq["q"]) + (1 - w) * M.logit(qtr_br)))
    else:
        w = 0.0
        q_centro = qtr_br
    q_centro_sem_vies = q_centro
    vies = cal.get("vies_pp", 0.0) if par_previsto else 0.0          # erros históricos medidos na fatia do PT (= A)
    q_centro = float(np.clip(q_centro - vies / 100, 0.01, 0.99))     # viés histórico encolhido
    d0 = _desloc(qtr_c, W2c, q_centro)
    sd_nat = math.sqrt(cal["dp_nacional_pp"] ** 2 + (cal.get("vies_dp_pp", 0.0) if par_previsto else 0.0) ** 2) * fator
    if q_pesq is not None and q_pesq.get("dp_pos_pp"):
        # pesquisas feitas depois do 1º turno: combinação por precisão com a projeção histórica
        sp = q_pesq["dp_pos_pp"]
        sd_nat = 1 / math.sqrt(1 / sd_nat ** 2 + 1 / sp ** 2)
    rng = np.random.default_rng(seed)
    # parte da variância nacional já vem da incerteza da matriz (Dirichlet): não contar duas vezes
    Rp = np.stack([rng.dirichlet(alfa * rows[j] + 1e-3, 20000) for j in range(len(elim))], axis=1)
    qp = q_transf(S0[None], Rp[:, None, :, :])
    var_dir = float(np.var((W2c * qp).sum(1) / W2c.sum()) * 1e4)
    sd_e = math.sqrt(max(sd_nat ** 2 - var_dir, (0.5 * sd_nat) ** 2))
    acc = {"Q": [], "decide": [], "nat1": []}
    hq = np.zeros((U, 1001), np.int64); sq = np.zeros(U); win = np.zeros(U)
    feito = 0
    while feito < n:
        Bn = min(lote, n - feito)
        if np.any(sd_proj > 0):
            z = rng.standard_normal((Bn, U, len(cands))) * sd_proj[None, :, None]
            S = S0[None] * np.exp(z)
            S = S / S.sum(2, keepdims=True)
        else:
            S = np.broadcast_to(S0[None], (Bn, U, len(cands)))
        nat1 = (c["V1"][None, :, None] * S).sum(1) / c["V1"].sum()
        decide = nat1.max(1) > 0.5
        R = np.stack([rng.dirichlet(alfa * rows[j] + 1e-3, Bn) for j in range(len(elim))], axis=1)   # (B, E, 3)
        qtr = q_transf(S, R[:, None, :, :])
        e_nat = M.t_unit(rng, Bn, gl).astype(float) * sd_e
        e_reg = rng.standard_normal((Bn, 6)) * cal["dp_regional_pp"]
        e_uf = M.t_unit(rng, (Bn, U), gl).astype(float) * cal["dp_uf_pp"]
        e_uf[:, UFS.index("ZZ")] *= 3.0                         # exterior: muito mais volátil
        pp = e_nat[:, None] + e_reg[:, reg_idx] + e_uf
        conv = 1 / (100 * np.clip(qtr, 0.05, 0.95) * (1 - np.clip(qtr, 0.05, 0.95)))
        q = M.expit(M.logit(qtr) + d0 + pp * conv)
        ab = np.clip(abst2_c[None] + rng.standard_normal((Bn, 1)) * PARAM_2T["dp_abst_nacional_pp"]["valor"]
                     + rng.standard_normal((Bn, U)) * PARAM_2T["dp_abst_uf_pp"]["valor"], 3, 80)
        bb = np.clip(bn2_c[None] + rng.standard_normal((Bn, U)) * PARAM_2T["dp_bn_pp"]["valor"], 0.3, 30)
        W2 = c["eleitores"][None] * (1 - ab / 100) * (1 - bb / 100)
        Q = (W2 * q).sum(1) / W2.sum(1)
        acc["Q"].append(Q); acc["decide"].append(decide); acc["nat1"].append(nat1[:, [A, B]])
        idx = np.clip(np.rint(q * 1000).astype(int), 0, 1000)
        for u in range(U):
            hq[u] += np.bincount(idx[:, u], minlength=1001)
        sq += q.sum(0); win += (q > 0.5).sum(0)
        feito += Bn
    Q = np.concatenate(acc["Q"]); dec = np.concatenate(acc["decide"])
    QS = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]

    def qh(h, qs):
        cc = np.cumsum(h) / h.sum()
        return [round(float(np.searchsorted(cc, x) / 10), 2) for x in qs]
    marg = (2 * Q - 1) * 100
    bordas = np.arange(-25, 25.25, 0.5)
    hm, _ = np.histogram(np.clip(marg, -25, 25 - 1e-6), bordas)
    ufs_out = []
    for i, u in enumerate(UFS):
        ufs_out.append({"uf": u, "regiao": REGIAO[u], "a_media": round(sq[i] / n * 100, 2), "a_q": qh(hq[i], [0.1, 0.5, 0.9]),
                        "a_q95": qh(hq[i], [0.025, 0.975]), "p_a": round(win[i] / n, 4),
                        "a_1t": round(float(S0[i, A]) * 100, 2), "b_1t": round(float(S0[i, B]) * 100, 2),
                        "transferencia_central": round(float(qtr_c[i]) * 100, 2),
                        "pst": round(float(c["pst"][i]), 2), "fonte": c["fonte_uf"][i]})
    return {
        "par": list(par), "n": n, "semente": seed,
        "p_a_vence": round(float((Q > 0.5).mean()), 5), "p_b_vence": round(float((Q <= 0.5).mean()), 5),
        "ep_mc": round(math.sqrt(max((Q > 0.5).mean() * (1 - (Q > 0.5).mean()), 1e-12) / n), 5),
        "a_media": round(float(Q.mean() * 100), 3), "a_quantis": [round(float(x) * 100, 2) for x in np.quantile(Q, QS)],
        "margem_quantis": [round(float(x), 2) for x in np.quantile(marg, QS)],
        "hist_margem": {"inicio": -25, "passo": 0.5, "contagens": hm.astype(int).tolist()},
        "p_decidido_1t_projecao": round(float(dec.mean()), 5),
        "centro": {"via_transferencia_a_pct": round(qtr_br * 100, 3),
                   "pesquisas_a_pct": None if not q_pesq or q_pesq.get("q") is None else round(q_pesq["q"] * 100, 3),
                   "peso_pesquisas": w, "centro_sem_vies_a_pct": round(q_centro_sem_vies * 100, 3),
                   "vies_historico_pp": round(vies, 3), "centro_a_pct": round(q_centro * 100, 3)},
        "erros": {"dp_nacional_pp": round(sd_nat, 3), "dp_nacional_extra_pp": round(sd_e, 3),
                  "dp_nacional_da_matriz_pp": round(math.sqrt(var_dir), 3), "dp_regional_pp": round(cal["dp_regional_pp"], 3),
                  "dp_uf_pp": round(cal["dp_uf_pp"], 3), "gl_t": gl, "par_previsto": par_previsto},
        "transferencia": {cands[k]: [round(x, 3) for x in transf.get(cands[k], LINHA_GENERICA)] for k in elim},
        "ufs": ufs_out,
        "_Q": Q,
    }


def definir_par(c: dict) -> tuple[tuple, bool, bool]:
    """Os dois mais votados nacionalmente; (par, decidido_no_1t, par_previsto)."""
    nat = c["nacional"]
    o = np.argsort(-nat)
    par = (c["cands"][o[0]], c["cands"][o[1]])
    previsto = set(par) == set(c["cands"][:2])
    if previsto and par[0] != c["cands"][0]:
        par = (c["cands"][0], c["cands"][1])        # A = PT sempre que o par for o previsto
    return par, bool(nat.max() > 0.5), previsto


def transf_para_par(par: tuple, ano: int, linha_hist: list | None = None) -> dict:
    if ano == 2026 and set(par) == {"Lula", "Flavio"}:
        t = dict(TRANSF_LF_2026)
        if par[0] == "Flavio":
            t = {k: [v[1], v[0], v[2]] for k, v in t.items()}
        return t
    if linha_hist is not None:
        return {c: list(linha_hist) for c in CANDS_ANO[ano] if c not in par}
    return {c: list(LINHA_GENERICA) for c in CANDS_ANO[ano] if c not in par}


# ================================================================ pesquisas de 2º turno 2026
def pesquisas_2t_2026(par: tuple, prem: dict, hoje: pd.Timestamp) -> dict | None:
    """Média das pesquisas de 2º turno Lula x Flávio: as feitas depois do 1º turno, se houver; senão as da véspera."""
    if set(par) != {"Lula", "Flavio"}:
        return None
    df = M.carregar_pesquisas_nacionais_2026()[0]
    t1 = pd.Timestamp(DATAS[2026][0])
    pos = df[(df.campo_inicio > t1) & df.t2_lula.notna() & df.t2_flavio.notna() & (df.campo_fim <= hoje)]
    if len(pos):
        x = pos.sort_values("campo_fim").groupby("instituto").tail(1)
        dias = (hoje - x.campo_fim).dt.days.clip(lower=0)
        w = np.sqrt(x.n.fillna(2000).clip(upper=3000)) * np.exp(-dias / 7)
        q = float(np.sum(w * M.logit(x.t2_lula / (x.t2_lula + x.t2_flavio))) / w.sum())
        q = float(M.expit(q))
        dias_2t = max((pd.Timestamp(DATAS[2026][1]) - hoje).days, 0)
        sp = math.sqrt(PARAM_2T["dp_pesquisas_pos_1t_base_pp"]["valor"] ** 2
                       + (PARAM_2T["deriva_pos_1t_pp_por_21_dias"]["valor"] * dias_2t / 21) ** 2)
        return {"q": q if par[0] == "Lula" else 1 - q, "peso": 0.5, "dp_pos_pp": sp, "tipo": "pos_1t",
                "n_pesquisas": int(len(x)), "institutos": sorted(x.instituto.tolist())}
    b = M.construir_base_2026(prem)
    q = b.q_nat
    return {"q": q if par[0] == "Lula" else 1 - q, "peso": PARAM_2T["peso_pesquisas_pre_1t"]["valor"], "tipo": "pre_1t",
            "n_pesquisas": len(b.agg2["tabela"]) if b.agg2 else 0}


# ================================================================ b) avaliação das previsões
QS7 = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]


def _pit_quantis(qs: dict, y: float) -> float:
    """PIT aproximado por interpolação linear nos quantis {nivel: valor}."""
    ks = sorted(qs)
    xs = [qs[k] for k in ks]
    if y <= xs[0]:
        return ks[0] * (y / xs[0]) if xs[0] > 0 else 0.0
    if y >= xs[-1]:
        return ks[-1] + (1 - ks[-1]) * min((y - xs[-1]) / max(xs[-1] - xs[0], 1e-6), 1.0)
    return float(np.interp(y, xs, ks))


def _pinball(qs: dict, y: float) -> float:
    """Média do pinball loss x2 nos quantis disponíveis (aproxima o CRPS)."""
    return float(np.mean([2 * ((y < v) - k) * (v - y) for k, v in qs.items()]))


def _evento(p, y):
    pc = min(max(p, 1e-3), 1 - 1e-3)
    return {"p": round(float(p), 4), "ocorreu": int(bool(y)), "brier": round((p - y) ** 2, 4),
            "log_score": round(math.log(pc if y else 1 - pc), 4)}


def previsoes_modelo(js: dict, cands: list, rotulos: dict | None = None) -> list:
    """Converte web/resultados.json (ou a saída de rodar.executar) em previsões comparáveis."""
    out = []
    visoes = js.get("visoes", js)
    for v, r in visoes.items():
        if not isinstance(r, dict) or "primeiro_turno" not in r:
            continue
        nac = {}
        for c in cands:
            pt = r["primeiro_turno"].get(c)
            if pt:
                nac[c] = {"media": pt["media"], "quantis": dict(zip(QS7, pt["quantis"]))}
        ev = {"primeiro_lugar": {c: r["prob_1o_lugar"][c]["p"] for c in cands if c in r.get("prob_1o_lugar", {})},
              "vai_ao_2t": {c: r["prob_top2"][c]["p"] for c in cands if c in r.get("prob_top2", {})},
              "decidida_1t": r["prob"]["decide_1t"]["p"]}
        ufs = {}
        for u in r.get("ufs", []):
            ufs[u["uf"]] = {cands[0]: {"media": u["lula_1t_media"], "q": dict(zip([0.1, 0.5, 0.9], u["lula_1t_q"]))},
                            cands[1]: {"media": u["flavio_1t_media"], "q": dict(zip([0.1, 0.5, 0.9], u["flavio_1t_q"]))},
                            "p_a_1o": u["p_lula_1o_1t"]}
        out.append({"fonte": (rotulos or {}).get(v, f"Modelo principal: {v}"), "tipo": "modelo", "visao": v,
                    "nacional": nac, "eventos": ev, "ufs": ufs})
    return out


def previsoes_alternativo(js: dict, cands: list) -> list:
    out = []
    for v, r in js.get("cenarios_2026", {}).items():
        q = r["quantis_pct_validos"]
        nac = {}
        for c, chave in ((cands[0], "lula_1t"), (cands[1], "flavio_1t")):
            x = q[chave]
            nac[c] = {"media": x["media"], "quantis": {0.05: x["p5"], 0.1: x["p10"], 0.25: x["p25"], 0.5: x["p50"],
                                                       0.75: x["p75"], 0.9: x["p90"], 0.95: x["p95"]}}
        p = r["prob"]
        ev = {"primeiro_lugar": {cands[0]: p["lula_1o_no_1t"], cands[1]: 1 - p["lula_1o_no_1t"]},
              "vai_ao_2t": {cands[0]: p.get("top2_lula_flavio", 1.0), cands[1]: p.get("top2_lula_flavio", 1.0)},
              "decidida_1t": p["decide_1t"]}
        ufs = {u: {"p_a_1o": d["p_lula_a_frente_1t"]} for u, d in r.get("ufs", {}).items()}
        out.append({"fonte": f"Modelo alternativo: {v}", "tipo": "modelo_alternativo", "visao": v, "nacional": nac,
                    "eventos": ev, "ufs": ufs})
    return out


def previsoes_pesquisas_2026(dias=7) -> list:
    """Última pesquisa nacional de cada instituto com campo encerrado até 7 dias antes da eleição, em válidos."""
    df = M.carregar_pesquisas_nacionais_2026()[0]
    t1 = pd.Timestamp(DATAS[2026][0])
    d = df[(df.campo_fim < t1) & (df.campo_fim >= t1 - pd.Timedelta(days=dias)) & df.lula.notna() & df.flavio.notna()]
    d = d.sort_values("campo_fim").groupby("instituto").tail(1)
    out = []
    for r in d.itertuples():
        named = {c: getattr(r, M.COL[c]) for c in M.CANDS if not pd.isna(getattr(r, M.COL[c]))}
        validos = "VOTOS VALIDOS" in str(r.obs).upper() or (not pd.isna(r.bni) and r.bni == 0)
        if all(c in named for c in M.CANDS[:6]) and not pd.isna(r.bni):
            tot = sum(named.values()) if "Outros" in named else 100 - r.bni
        elif not pd.isna(r.bni):
            tot = 100 - r.bni
        elif validos:
            tot = 100.0
        else:
            tot = sum(named.values())
        nac = {c: {"media": round(100 * v / tot, 2)} for c, v in named.items()}
        out.append({"fonte": f"{r.instituto} ({r.campo_inicio:%d/%m}–{r.campo_fim:%d/%m})", "tipo": "pesquisa",
                    "instituto": r.instituto, "nacional": nac, "eventos": {}, "ufs": {},
                    "obs": "convertida para válidos (exclui brancos/nulos/indecisos)" if not validos else "publicada em válidos"})
    return out


def previsao_media_pesquisas(base: M.Base, cands: list) -> dict:
    """Média do agregador (house effects, recência) antes da contração da terceira via e do viés."""
    T = float(base.m_nat.sum())
    nac = {cands[0]: {"media": round(100 * (1 - T) * base.p2_nat, 2)},
           cands[1]: {"media": round(100 * (1 - T) * (1 - base.p2_nat), 2)}}
    for c, v in zip(cands[2:], base.m_nat):
        nac[c] = {"media": round(100 * float(v), 2)}
    return {"fonte": "Média das pesquisas (agregador, sem ajustes)", "tipo": "media", "nacional": nac, "eventos": {}, "ufs": {}}


def previsoes_mercados() -> list:
    m = pd.read_csv(DADOS / "mercados_snapshot.csv")
    out = []
    for plat, g in m.groupby("plataforma"):
        ev = {"primeiro_lugar": {}, "vai_ao_2t": {}}
        for r in g.itertuples():
            p = r.normalizado if not pd.isna(r.normalizado) and str(r.normalizado) != "" else r.probabilidade
            p = float(p)
            nome = {"Lula": "Lula", "Flavio Bolsonaro": "Flavio"}.get(r.resultado, r.resultado)
            if r.mercado == "Alguem vence no 1o turno" and r.resultado == "Sim":
                ev["decidida_1t"] = p
            elif r.mercado == "1o colocado no 1o turno":
                ev["primeiro_lugar"][nome] = p
                if nome == "Lula":
                    ev["primeiro_lugar"].setdefault("Flavio", 1 - p)
            elif r.mercado == "Vai ao 2o turno":
                ev["vai_ao_2t"][nome] = float(r.probabilidade)
        ev = {k: v for k, v in ev.items() if v not in ({}, None)}
        if ev:
            out.append({"fonte": f"Mercado: {plat}", "tipo": "mercado", "nacional": {}, "eventos": ev, "ufs": {}})
    return out


def avaliar(c: dict, previsoes: list) -> dict:
    """Compara previsões e resultado (c = consolidar(...)). Fatias em %."""
    cands = c["cands"]
    real = {k: 100 * float(v) for k, v in zip(cands, c["nacional"])}
    ordem = sorted(cands, key=lambda k: -real[k])
    top2 = set(ordem[:2])
    decidida = max(real.values()) > 50
    real_uf = {u: {k: 100 * float(c["S"][i, j]) for j, k in enumerate(cands)} for i, u in enumerate(UFS)}
    A, B = cands[0], cands[1]
    linhas = []
    for f in previsoes:
        nac = {}
        for k, d in f["nacional"].items():
            if k not in real:
                continue
            e = {"previsto": d["media"], "real": round(real[k], 3), "erro": round(d["media"] - real[k], 3)}
            if "quantis" in d:
                qs = {float(a): float(b) for a, b in d["quantis"].items()}
                e["pit"] = round(_pit_quantis(qs, real[k]), 3)
                e["mediana"] = qs.get(0.5)
                e["erro_mediana"] = round(qs[0.5] - real[k], 3) if 0.5 in qs else None
                if 0.1 in qs and 0.9 in qs:
                    e["em_80"] = bool(qs[0.1] <= real[k] <= qs[0.9])
                lo, hi = (qs.get(0.025), qs.get(0.975)) if 0.025 in qs else (qs.get(0.05), qs.get(0.95))
                if lo is not None:
                    e["em_95" if 0.025 in qs else "em_90"] = bool(lo <= real[k] <= hi)
                e["crps_aprox"] = round(_pinball(qs, real[k]), 3)
            nac[k] = e
        resumo = {}
        if A in nac and B in nac:
            resumo["erro_margem"] = round((nac[A]["previsto"] - nac[B]["previsto"]) - (real[A] - real[B]), 3)
        ks = [k for k in nac]
        resumo["mae_candidatos"] = round(float(np.mean([abs(nac[k]["erro"]) for k in ks])), 3) if ks else None
        resumo["mae_dois_primeiros"] = round(float(np.mean([abs(nac[k]["erro"]) for k in (A, B) if k in nac])), 3) \
            if any(k in nac for k in (A, B)) else None
        ev = {}
        e_ = f.get("eventos", {})
        for k, p in e_.get("primeiro_lugar", {}).items():
            if k in real:
                ev[f"{k} em 1º"] = _evento(p, ordem[0] == k)
        for k, p in e_.get("vai_ao_2t", {}).items():
            if k in real:
                ev[f"{k} no 2º turno"] = _evento(p, (k in top2) and not decidida)
        if "decidida_1t" in e_:
            ev["Decidida no 1º turno"] = _evento(e_["decidida_1t"], decidida)
        uf = {}
        if f.get("ufs"):
            erros_a, erros_b, cob_a, cob_b, br = [], [], [], [], []
            for u, d in f["ufs"].items():
                if u not in real_uf or u == "ZZ":
                    continue
                ra, rb = real_uf[u][A], real_uf[u][B]
                if A in d:
                    erros_a.append(d[A]["media"] - ra)
                    q = d[A].get("q", {})
                    if q:
                        cob_a.append(q[0.1] <= ra <= q[0.9])
                if B in d:
                    erros_b.append(d[B]["media"] - rb)
                    q = d[B].get("q", {})
                    if q:
                        cob_b.append(q[0.1] <= rb <= q[0.9])
                if "p_a_1o" in d:
                    y = max(real_uf[u], key=real_uf[u].get) == A
                    br.append(((d["p_a_1o"] - y) ** 2, (d["p_a_1o"] > 0.5) == y))
            if erros_a:
                uf = {"n_ufs": len(erros_a), f"mae_{A}": round(float(np.mean(np.abs(erros_a))), 3),
                      f"vies_{A}": round(float(np.mean(erros_a)), 3), f"mae_{B}": round(float(np.mean(np.abs(erros_b))), 3),
                      f"vies_{B}": round(float(np.mean(erros_b)), 3),
                      "cobertura_80": round(float(np.mean(cob_a + cob_b)), 3) if cob_a else None}
            if br:
                uf["brier_a_1o"] = round(float(np.mean([x[0] for x in br])), 4)
                uf["acerto_a_1o"] = round(float(np.mean([x[1] for x in br])), 3)
        linhas.append({"fonte": f["fonte"], "tipo": f["tipo"], "nacional": nac, "resumo": resumo, "eventos": ev, "uf": uf,
                       "obs": f.get("obs", "")})
    pesq = [x for x in linhas if x["tipo"] == "pesquisa" and x["resumo"].get("erro_margem") is not None]
    mais_perto = sorted(pesq, key=lambda x: (abs(x["resumo"]["erro_margem"]), x["resumo"]["mae_dois_primeiros"]))
    return {"real": {"nacional": {k: round(v, 3) for k, v in real.items()}, "ordem": ordem, "decidida_1t": decidida,
                     "pst_nacional": c["pst_nacional"], "atualizado": c["atualizado"],
                     "ufs": {u: {k: round(v, 2) for k, v in d.items()} for u, d in real_uf.items()},
                     "fonte_uf": dict(zip(UFS, c["fonte_uf"]))},
            "previsoes": linhas,
            "ranking_pesquisas_margem": [{"fonte": x["fonte"], "erro_margem": x["resumo"]["erro_margem"],
                                          "mae_dois_primeiros": x["resumo"]["mae_dois_primeiros"]} for x in mais_perto]}


def _f(x, d=1):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "–"
    return f"{x:.{d}f}".replace(".", ",")


def escrever_avaliacao_md(av: dict, titulo: str, nota: str = "") -> str:
    r = av["real"]
    cands = list(r["nacional"].keys())
    A, B = cands[0], cands[1]
    L = [f"# {titulo}\n"]
    L.append(f"Gerado por `resultado_1t.py` em {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. "
             f"Seções totalizadas no Brasil: {_f(r['pst_nacional'], 2)}% (TSE, {r['atualizado'] or '–'}). "
             + ("**Apuração parcial: números provisórios; UFs não totalizadas projetadas.** " if r["pst_nacional"] < 99.995 else "")
             + nota + "\n")
    L.append("## Resultado (votos válidos, %)\n")
    L.append("| " + " | ".join(cands) + " |")
    L.append("|" + "---|" * len(cands))
    L.append("| " + " | ".join(_f(r["nacional"][k], 2) for k in cands) + " |")
    L.append(f"\nDecidida no 1º turno: {'sim' if r['decidida_1t'] else 'não'}. Ordem: {', '.join(r['ordem'][:3])}.\n")
    L.append("## Previsões nacionais x resultado\n")
    L.append("Erro = previsto − real (p.p. de votos válidos; positivo = previsão acima do resultado). Para os modelos, "
             "'previsto' é a média das simulações; PIT = posição do resultado na distribuição prevista (0,5 = no centro); "
             "CRPS aproximado pelos quantis publicados (menor = melhor).\n")
    L.append(f"| Fonte | {A} prev. | erro | {B} prev. | erro | Erro na margem | MAE 2 primeiros | PIT {A} | PIT {B} | "
             f"Em 80% ({A}/{B}) | CRPS {A}/{B} |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in av["previsoes"]:
        n = x["nacional"]
        if A not in n:
            continue
        a, b = n[A], n.get(B, {})
        em80 = "–" if "em_80" not in a else f"{'sim' if a['em_80'] else 'não'}/{'sim' if b.get('em_80') else 'não'}"
        L.append(f"| {x['fonte']} | {_f(a['previsto'])} | {_f(a['erro'])} | {_f(b.get('previsto'))} | {_f(b.get('erro'))} | "
                 f"{_f(x['resumo'].get('erro_margem'))} | {_f(x['resumo'].get('mae_dois_primeiros'))} | "
                 f"{_f(a.get('pit'), 2)} | {_f(b.get('pit'), 2)} | {em80} | "
                 f"{_f(a.get('crps_aprox'), 2)}/{_f(b.get('crps_aprox'), 2)} |")
    if av["ranking_pesquisas_margem"]:
        L.append("\n**Pesquisas ordenadas pelo erro absoluto na margem entre os dois primeiros:** "
                 + "; ".join(f"{p['fonte']} {_f(p['erro_margem'])}" for p in av["ranking_pesquisas_margem"]) + ".\n")
    L.append("## Eventos (Brier e log score)\n")
    L.append("Brier = (p − ocorreu)²; log score = log da probabilidade dada ao que aconteceu (mais perto de 0 = melhor).\n")
    L.append("| Fonte | Evento | P prevista | Ocorreu | Brier | Log score |")
    L.append("|---|---|---|---|---|---|")
    for x in av["previsoes"]:
        for nome, e in x["eventos"].items():
            if e["p"] < 0.002 and not e["ocorreu"]:
                continue                      # eventos que ninguém considerou possíveis (candidatos menores)
            L.append(f"| {x['fonte']} | {nome} | {_f(e['p'], 3)} | {'sim' if e['ocorreu'] else 'não'} | {_f(e['brier'], 3)} | "
                     f"{_f(e['log_score'], 3)} |")
    L.append("\n## UFs\n")
    L.append(f"| Fonte | UFs | MAE {A} | Viés {A} | MAE {B} | Viés {B} | Cobertura 80% | Brier '{A} 1º na UF' | Acerto do favorito |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for x in av["previsoes"]:
        u = x["uf"]
        if not u:
            continue
        L.append(f"| {x['fonte']} | {u.get('n_ufs', '–')} | {_f(u.get(f'mae_{A}'))} | {_f(u.get(f'vies_{A}'))} | "
                 f"{_f(u.get(f'mae_{B}'))} | {_f(u.get(f'vies_{B}'))} | "
                 f"{_f(100 * u['cobertura_80'] if u.get('cobertura_80') is not None else None, 0)}% | "
                 f"{_f(u.get('brier_a_1o'), 3)} | {_f(100 * u['acerto_a_1o'] if u.get('acerto_a_1o') is not None else None, 0)}% |")
    L.append("\nExterior fora das métricas por UF. Viés positivo = previsão acima do resultado.\n")
    L.append("## Resultado por UF (votos válidos, %)\n")
    L.append(f"| UF | {A} | {B} | Situação |")
    L.append("|---|---|---|---|")
    for u, d in r["ufs"].items():
        L.append(f"| {u} | {_f(d[A], 1)} | {_f(d[B], 1)} | {r['fonte_uf'][u]} |")
    L.append("\nLeitura: uma eleição é uma única realização; um modelo bem calibrado erra fora do intervalo de 80% em "
             "1 a cada 5 eleições. Comparações entre institutos em uma só eleição dizem pouco sobre a qualidade "
             "metodológica de cada um.\n")
    return "\n".join(L)


# ================================================================ orquestração 2026
def _previsao_uf_2026(js: dict) -> dict:
    """Fatias por UF da véspera (calibrado) para UFs sem apuração: Lula/Flávio do modelo e menores na composição nacional."""
    v = js["visoes"]["calibrado"]
    nat = {c: v["primeiro_turno"][c]["media"] for c in M.CANDS}
    menores_tot = sum(nat[c] for c in M.MENORES)
    out = {}
    for u in v["ufs"]:
        a, b = u["lula_1t_media"], u["flavio_1t_media"]
        resto = max(100 - a - b, 0.5)
        d = {"Lula": a / 100, "Flavio": b / 100}
        for c in M.MENORES:
            d[c] = resto / 100 * nat[c] / menores_tot
        out[u["uf"]] = d
    return out


def _ufs_ref_2026() -> pd.DataFrame:
    el = pd.read_csv(DADOS / "eleitorado_uf_2026.csv")
    return pd.DataFrame({"uf": el.uf, "eleitores": el.eleitores_2026, "abst1": el.abst_1t_2022, "bn1": el.bn_1t_2022_pct_comp})


def _sd_proj(c: dict) -> np.ndarray:
    pst = c["pst"]
    sd = PARAM_2T["dp_projecao_uf_logito"]["valor"] * np.sqrt(np.clip(1 - pst / 100, 0, 1))
    sd[np.array(c["fonte_uf"]) == "previsão"] = PARAM_2T["dp_uf_sem_apuracao_logito"]["valor"]
    sm = c.get("sd_mun")
    if sm is not None:
        ok = np.isfinite(sm)
        sd[ok] = sm[ok]                      # projeção por município: incerteza própria (encolhe com a apuração)
    return sd


def _limpo(x):
    if isinstance(x, dict):
        return {str(k): _limpo(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, (list, tuple)):
        return [_limpo(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.ndarray):
        return _limpo(x.tolist())
    return x


def rodar_2026(n: int, seed: int, fonte: str = "auto", log=print, municipios: bool = True) -> dict:
    prem = M.carregar_premissas()
    res = buscar_resultados(2026, fonte, log=log)
    meta_f = res.pop("_meta", {})
    js = json.loads((WEB / "resultados.json").read_text(encoding="utf-8"))
    agora = datetime.now(timezone.utc)
    saida = {"meta": {"gerado_em": agora.isoformat(timespec="seconds"), "fonte": meta_f.get("fonte"),
                      "codigo_tse": meta_f.get("codigo"), "erros_download": meta_f.get("erros", [])[:40],
                      "n": n, "semente": seed, "ensaio": False, "parametros": PARAM_2T,
                      "transferencia_fonte": FONTE_TRANSF_2026}}
    ensaio = DADOS / "ensaio_2022" / "resumo.json"
    if ensaio.exists():
        saida["ensaio_2022"] = json.loads(ensaio.read_text(encoding="utf-8"))
    if "BR" not in res or not np.isfinite(res["BR"]["pst"]) or res["BR"]["pst"] <= 0:
        saida["meta"]["status"] = "aguardando"
        saida["meta"]["mensagem"] = ("Apuração ainda não começou (ou TSE indisponível): 0% das seções totalizadas. "
                                     "A previsão do 2º turno aparece aqui depois das primeiras parciais.")
        log(saida["meta"]["mensagem"])
        _gravar_json(WEB / "resultados_2t.json", saida)
        return saida
    pj = None
    if municipios and fonte in ("auto", "tse") and str(meta_f.get("fonte") or "").startswith("TSE"):
        pj = projecao_municipal_2026(res, meta_f.get("codigo"), log=log)
    try:
        c = consolidar(res, 2026, _ufs_ref_2026(), _previsao_uf_2026(js), pj)
    except Exception as ex:                                       # noqa: BLE001
        if pj is None:
            raise
        log(f"consolidação com projeção por município falhou ({ex}): método antigo")
        pj = None
        c = consolidar(res, 2026, _ufs_ref_2026(), _previsao_uf_2026(js))
    saida["meta"]["projecao_parcial"] = {
        "metodo_uf": dict(zip(UFS, c["metodo_uf"])), "parametros": PARAM_MUN,
        "download": None if pj is None else {k: v for k, v in pj.get("meta", {}).items() if k != "erros"} | {
            "erros": pj.get("meta", {}).get("erros", [])[:20]},
        "swing_uf": None if pj is None else {u: {k: round(float(v), 4) for k, v in r["swing"].items()}
                                             | {"apurado_frac": round(r["apurado_frac"], 4),
                                                "sd_fatia_lula_pp": round(100 * r["sd_fatia_a"], 3)}
                                             for u, r in pj["ufs"].items()},
        "nacional_metodo_antigo": None}
    if pj is not None:
        c_ant = consolidar(res, 2026, _ufs_ref_2026(), _previsao_uf_2026(js))
        saida["meta"]["projecao_parcial"]["nacional_metodo_antigo"] = {
            k: round(100 * float(v), 3) for k, v in zip(c_ant["cands"], c_ant["nacional"])}
    status = status_apuracao(c)
    saida["meta"]["status"] = status
    saida["meta"]["pst_nacional"] = c["pst_nacional"]
    saida["meta"]["atualizado_tse"] = c["atualizado"]
    # b) avaliação
    base = M.construir_base_2026(prem)
    prev = previsoes_modelo(js, M.CANDS, {"calibrado": "Modelo principal: calibrado", "neutro": "Modelo principal: neutro",
                                          "pleno": "Modelo principal: viés pleno"})
    alt = AQUI.parent / "modelo_alternativo" / "resultados_alt.json"
    if alt.exists():
        prev += previsoes_alternativo(json.loads(alt.read_text(encoding="utf-8")), M.CANDS)
    prev += [previsao_media_pesquisas(base, M.CANDS)] + previsoes_pesquisas_2026() + previsoes_mercados()
    av = avaliar(c, prev)
    _gravar_json(DADOS / "avaliacao_1t.json", av)
    (AQUI / "AVALIACAO_1T.md").write_text(escrever_avaliacao_md(
        av, "Avaliação das previsões do 1º turno de 2026",
        "Fonte do resultado: " + str(meta_f.get("fonte")) + "."), encoding="utf-8")
    # c) 2º turno
    par, decidido, previsto = definir_par(c)
    saida["primeiro_turno_real"] = {"nacional": {k: round(100 * float(v), 3) for k, v in zip(c["cands"], c["nacional"])},
                                    "nacional_tse_parcial": c["nacional_tse"],
                                    "comparecimento_pct": _comp_br(c), "pst_nacional": c["pst_nacional"]}
    saida["par"] = list(par)
    saida["decidido_1t"] = decidido and status == "final"
    if saida["decidido_1t"]:
        saida["mensagem"] = f"{par[0]} teve mais de 50% dos votos válidos: eleição decidida no 1º turno."
        _gravar_json(WEB / "resultados_2t.json", saida)
        return saida
    cal = calibrar_2t((2014, 2018, 2022), PARAM_2T["peso_pesquisas_pre_1t"]["valor"])
    qp = pesquisas_2t_2026(par, prem, pd.Timestamp(agora.date()))
    d_comp = delta_comparecimento()
    sim = simular_2t(c, par, transf_para_par(par, 2026), qp, cal, d_comp, n=n, seed=seed, par_previsto=previsto,
                     sd_proj=_sd_proj(c))
    sim["pesquisas_2t"] = qp
    sim["calibracao"] = {k: v for k, v in cal.items()}
    sim["ecologico"] = [ecologico(a) for a in (2014, 2018, 2022)]
    nomes = dict(zip(UFS, pd.read_csv(DADOS / "eleitorado_uf_2026.csv").set_index("uf").reindex(UFS)["nome"].fillna("Exterior")))
    for u in sim["ufs"]:
        u["nome"] = nomes.get(u["uf"], u["uf"])
    saida["segundo_turno"] = sim
    _gravar_json(WEB / "resultados_2t.json", saida)
    log(f"[2T] {par[0]} x {par[1]}: P({par[0]}) = {sim['p_a_vence']:.3f}; {par[0]} {sim['a_media']:.1f}% "
        f"(p10–p90 {sim['a_quantis'][1]}–{sim['a_quantis'][5]}); apuração {c['pst_nacional']:.2f}%")
    return saida


def _comp_br(c):
    br = c.get("br")
    if not br or not br.get("eleitorado"):
        return None
    tot = br["eleitorado"] * br["pst"] / 100
    return round(100 * br["comparecimento"] / tot, 2) if tot > 0 else None


def _gravar_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(_limpo(obj), ensure_ascii=False, allow_nan=False), encoding="utf-8")


# ================================================================ ensaio com 2014/2018/2022 (1º turno de cada ano como "hoje")
def gerar_fixture_2022(destino: Path = FIXTURES / "2022") -> list:
    """Reconstrói, no formato 'dados-simplificados' do TSE de 2022 (...-c0001-e000544-r.json), os resultados
    oficiais do 1º turno de 2022 por UF, a partir da agregação TSE em data/resultados_uf_2002_2022.csv.
    (Os JSON originais do TSE de 2022 não estão mais publicados: /oficial/ele2022/544/... devolve 404 em 4/10/2026.)
    Candidatos fora dos 4 primeiros somados num registro 'DEMAIS CANDIDATOS' (número 0)."""
    destino.mkdir(parents=True, exist_ok=True)
    h = _hist()
    r1 = h[(h.ano == 2022) & (h.turno == 1)].set_index("uf")
    feitos = []
    for uf in ["BR"] + UFS:
        r = r1.loc[uf]
        vv = int(r.votos_validos)
        pct = {"13": r.pt_pct_validos, "22": r.oponente_pct_validos, "15": r.terceiro1_pct_validos,
               "12": r.terceiro2_pct_validos}
        votos = {k: int(round(vv * v / 100)) for k, v in pct.items()}
        votos["0"] = vv - sum(votos.values())
        nomes = {"13": "LULA", "22": "JAIR BOLSONARO", "15": "SIMONE TEBET", "12": "CIRO GOMES", "0": "DEMAIS CANDIDATOS"}
        js = {"ele": "544", "tpabr": "BR" if uf == "BR" else "UF", "cdabr": uf, "carper": "1", "md": "N", "t": "1", "f": "O",
              "dg": "02/10/2022", "hg": "23:59:59", "dt": "02/10/2022", "ht": "23:59:59", "dv": "S", "tf": "S",
              "s": "", "st": "", "pst": "100,00", "si": "", "psi": "100,00",
              "e": str(int(r.eleitorado)), "c": str(int(r.comparecimento)), "a": str(int(r.abstencoes)),
              "vb": str(int(r.brancos)), "tvn": str(int(r.nulos)), "vv": str(vv), "tv": str(int(r.comparecimento)),
              "_nota": "Reconstruído de data/resultados_uf_2002_2022.csv (TSE dados abertos), formato dados-simplificados 2022",
              "cand": [{"seq": str(i + 1), "n": k, "nm": nomes[k], "e": "N", "st": "", "dvt": "Válido", "vap": str(v),
                        "pvap": f"{100 * v / vv:.2f}".replace(".", ",")}
                       for i, (k, v) in enumerate(sorted(votos.items(), key=lambda kv: -kv[1]))]}
        p = destino / f"{uf.lower()}-c0001-e000544-r.json"
        p.write_text(json.dumps(js, ensure_ascii=False, indent=0), encoding="utf-8")
        feitos.append(p)
    return feitos


def _previsao_hist(ano: int, P: dict, n: int, seed: int):
    """Previsão da véspera do 1º turno de `ano` com o motor do modelo (3 visões, prior de viés sem o ano)."""
    import backtest as BT
    import rodar as R
    err = BT.erros_brutos(P)
    b = BT.construir_base_hist(ano, "v1", P)
    vieses = {}
    for v in M.VISOES:
        pri = BT.priors_vies(err, [a for a in BT.ANOS if a != ano], P, v)
        d = BT.vies_para_rodada(pri, "v1", v)
        d["ajuste_comp"] = False
        vieses[v] = d
    res, _, _ = R.executar(n, seed, 100_000, base=b, vieses=vieses, prem=P)
    return res, b


def previsoes_pesquisas_hist(ano: int, cands: list, dias=7) -> list:
    nac = pd.read_csv(DADOS / "backtest_pesquisas_nacionais.csv", parse_dates=["campo_inicio", "campo_fim"])
    t1 = pd.Timestamp(DATAS[ano][0])
    d = nac[(nac.ano == ano) & (nac.turno_alvo == 1) & (nac.campo_fim < t1) & (nac.campo_fim >= t1 - pd.Timedelta(days=dias))]
    d = d.sort_values("campo_fim").groupby("instituto").tail(1)
    out = []
    for r in d.itertuples():
        named = {cands[0]: r.pt, cands[1]: r.opp}
        for s in ("c3", "c4", "c5", "c6"):
            nm = getattr(r, f"{s}_nome")
            if isinstance(nm, str) and nm in cands and not pd.isna(getattr(r, s)):
                named[nm] = getattr(r, s)
        tot = 100 - r.bni if not pd.isna(r.bni) else sum(named.values()) + (0 if pd.isna(r.outros) else r.outros)
        out.append({"fonte": f"{r.instituto} ({r.campo_inicio:%d/%m}–{r.campo_fim:%d/%m})", "tipo": "pesquisa",
                    "instituto": r.instituto, "nacional": {k: {"media": round(100 * v / tot, 2)} for k, v in named.items()},
                    "eventos": {}, "ufs": {}})
    return out


def ensaio(ano: int, n: int = 500_000, seed: int = 20221002, P: dict | None = None, escrever=True, log=print) -> dict:
    """Pipeline completo como se fosse a noite do 1º turno de `ano` (2014, 2018 ou 2022):
    a) lê o resultado (2022: JSONs reconstruídos no formato do TSE; 2014/2018: CSV TSE); b) avalia a previsão de
    véspera do modelo e as pesquisas; c) prevê o 2º turno com o que se sabia na véspera do 1º turno + 1º turno real,
    com erros calibrados SEM o próprio ano; compara com o 2º turno real."""
    P = P or M.carregar_premissas()
    cands = CANDS_ANO[ano]
    h = _hist()
    r1 = h[(h.ano == ano) & (h.turno == 1)].set_index("uf")
    ufs_ref = pd.DataFrame({"uf": UFS, "eleitores": r1.loc[UFS, "eleitorado"].values,
                            "abst1": r1.loc[UFS, "abstencao_pct"].values,
                            "bn1": (r1.loc[UFS, "branco_pct_comp"] + r1.loc[UFS, "nulo_pct_comp"]).values})
    if ano == 2022:
        if not (FIXTURES / "2022" / "br-c0001-e000544-r.json").exists():
            gerar_fixture_2022()
        res = buscar_resultados(2022, "diretorio", FIXTURES / "2022", log)
    else:
        res = {}
        for uf in ["BR"] + UFS:
            r = r1.loc[uf]
            votos = {cands[0]: r.pt_votos, cands[1]: r.oponente_votos}
            resto = r.votos_validos - r.pt_votos - r.oponente_votos
            votos["Outros"] = resto
            res[uf] = {"abr": uf, "pst": 100.0, "psi": 100.0, "eleitorado": float(r.eleitorado),
                       "comparecimento": float(r.comparecimento), "abstencao": float(r.abstencoes),
                       "validos": float(r.votos_validos), "brancos": float(r.brancos), "nulos": float(r.nulos),
                       "total": float(r.comparecimento), "votos": votos, "atualizado": "TSE (CSV)"}
        res["_meta"] = {"fonte": "CSV TSE"}
    res.pop("_meta", None)
    c = consolidar(res, ano, ufs_ref)
    prev_js, base = _previsao_hist(ano, P, min(n, 200_000), seed)
    prev = previsoes_modelo(prev_js, cands, {"calibrado": "Modelo principal: calibrado", "neutro": "Modelo principal: neutro",
                                             "pleno": "Modelo principal: viés pleno"})
    prev += [previsao_media_pesquisas(base, cands)] + previsoes_pesquisas_hist(ano, cands)
    av = avaliar(c, prev)
    # 2º turno
    par, decidido, previsto = definir_par(c)
    outros = tuple(a for a in (2014, 2018, 2022) if a != ano)
    w = PARAM_2T["peso_pesquisas_pre_1t"]["valor"]
    cal = calibrar_2t(outros, w, P)
    pre = preditores_hist(ano, P)
    qp = {"q": pre["q_pesquisas"], "peso": w, "tipo": "pre_1t"} if pre["q_pesquisas"] is not None else None
    d_comp = delta_comparecimento(outros)
    sim = simular_2t(c, par, transf_para_par(par, ano, pre["linha"]), qp, cal, d_comp, n=n, seed=seed,
                     par_previsto=previsto)
    d = historico_ano(ano)
    real_q = d["q_br"] * 100
    Q = sim.pop("_Q")
    pit = float(np.mean(Q * 100 < real_q))
    real_uf = dict(zip(d["ufs"], d["q"] * 100))
    cob80 = [u["a_q"][0] <= real_uf[u["uf"]] <= u["a_q"][2] for u in sim["ufs"] if u["uf"] != "ZZ"]
    cob95 = [u["a_q95"][0] <= real_uf[u["uf"]] <= u["a_q95"][1] for u in sim["ufs"] if u["uf"] != "ZZ"]
    brier_uf = [(u["p_a"] - (real_uf[u["uf"]] > 50)) ** 2 for u in sim["ufs"] if u["uf"] != "ZZ"]
    acerto_uf = [(u["p_a"] > 0.5) == (real_uf[u["uf"]] > 50) for u in sim["ufs"] if u["uf"] != "ZZ"]
    mae_uf = [abs(u["a_media"] - real_uf[u["uf"]]) for u in sim["ufs"] if u["uf"] != "ZZ"]
    comp = {"ano": ano, "par": list(par), "real_a_pct": round(real_q, 3),
            "previsto_a_media": sim["a_media"], "previsto_a_quantis": sim["a_quantis"], "erro_pp": round(sim["a_media"] - real_q, 3),
            "pit": round(pit, 3), "em_80": bool(sim["a_quantis"][1] <= real_q <= sim["a_quantis"][5]),
            "em_95": bool(sim["a_quantis"][0] <= real_q <= sim["a_quantis"][6]),
            "p_a_vence": sim["p_a_vence"], "a_venceu": bool(real_q > 50),
            "brier_nacional": round((sim["p_a_vence"] - (real_q > 50)) ** 2, 4),
            "uf_mae_pp": round(float(np.mean(mae_uf)), 3), "uf_cobertura_80": round(float(np.mean(cob80)), 3),
            "uf_cobertura_95": round(float(np.mean(cob95)), 3), "uf_brier": round(float(np.mean(brier_uf)), 4),
            "uf_acerto": round(float(np.mean(acerto_uf)), 3), "centro": sim["centro"], "erros": sim["erros"],
            "calibracao_anos": list(outros),
            "modelo_vespera_1t_a_media": prev_js["calibrado"]["segundo_turno"]["lula_media"] if "calibrado" in prev_js else None}
    for u in sim["ufs"]:
        u["real_2t"] = round(real_uf.get(u["uf"], float("nan")), 2)
    out = {"ano": ano, "avaliacao_1t": av, "segundo_turno": sim, "comparacao_2t": comp, "calibracao": cal,
           "pesquisas_2t": qp, "ecologico": ecologico(ano)}
    if escrever:
        dest = DADOS / f"ensaio_{ano}"
        _gravar_json(dest / "avaliacao_1t.json", av)
        _gravar_json(dest / "resultados_2t.json", {"meta": {"ensaio": True, "ano": ano, "n": n, "semente": seed,
                                                            "status": "final", "parametros": PARAM_2T},
                                                   "primeiro_turno_real": {"nacional": av["real"]["nacional"]},
                                                   "par": list(par), "decidido_1t": False, "segundo_turno": sim,
                                                   "comparacao_2t": comp})
        (dest / "AVALIACAO_1T.md").write_text(escrever_avaliacao_md(
            av, f"Ensaio: avaliação das previsões do 1º turno de {ano}",
            "Ensaio do pipeline com dados históricos (resultado oficial do TSE)."), encoding="utf-8")
    log(f"[ensaio {ano}] 2T {par[0]}: previsto {sim['a_media']:.1f} (p10–p90 {sim['a_quantis'][1]}–{sim['a_quantis'][5]}), "
        f"real {real_q:.1f}; P({par[0]} vence) {sim['p_a_vence']:.3f}; PIT {pit:.2f}; UFs MAE {comp['uf_mae_pp']:.1f} "
        f"cob80 {comp['uf_cobertura_80']:.2f} acerto {comp['uf_acerto']:.2f}")
    return out


def ensaios_historicos(n: int, log=print) -> dict:
    P = M.carregar_premissas()
    resumo = {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "anos": {}}
    for ano in (2014, 2018, 2022):
        o = ensaio(ano, n=n, P=P, escrever=(ano == 2022), log=log)
        resumo["anos"][ano] = o["comparacao_2t"]
        if ano == 2022:
            av = o["avaliacao_1t"]
            resumo["avaliacao_1t_2022"] = {
                "real": av["real"]["nacional"],
                "previsoes": [{"fonte": x["fonte"], "erro_margem": x["resumo"].get("erro_margem"),
                               "mae_dois_primeiros": x["resumo"].get("mae_dois_primeiros"),
                               "pit_pt": x["nacional"].get("Lula", {}).get("pit"),
                               "pit_adv": x["nacional"].get("Bolsonaro", {}).get("pit")} for x in av["previsoes"]]}
    c = pd.DataFrame(resumo["anos"].values())
    resumo["agregado"] = {"mae_nacional_pp": round(float(c.erro_pp.abs().mean()), 3),
                          "cobertura_80_nacional": round(float(c.em_80.mean()), 3),
                          "cobertura_95_nacional": round(float(c.em_95.mean()), 3),
                          "brier_nacional": round(float(c.brier_nacional.mean()), 4),
                          "uf_cobertura_80": round(float(c.uf_cobertura_80.mean()), 3),
                          "uf_cobertura_95": round(float(c.uf_cobertura_95.mean()), 3),
                          "uf_mae_pp": round(float(c.uf_mae_pp.mean()), 3)}
    _gravar_json(DADOS / "ensaio_2022" / "resumo.json", resumo)
    return resumo


# ================================================================ CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rodar-tudo", action="store_true", help="a) resultado TSE, b) avaliação, c) 2º turno, d) publicar")
    ap.add_argument("--ensaio-2022", action="store_true", help="ensaio completo com 2022 (+ validação 2014/2018)")
    ap.add_argument("--gerar-fixture-2022", action="store_true")
    ap.add_argument("--fonte", default="auto", choices=["auto", "tse", "manual"])
    ap.add_argument("--sem-municipios", action="store_true",
                    help="não usar a projeção por município (método antigo: válidos / pst por UF)")
    ap.add_argument("--replay-2022", action="store_true",
                    help="valida a projeção da apuração parcial reapurando 2022 em ordem não aleatória")
    ap.add_argument("--n", type=int, default=500_000)
    ap.add_argument("--seed", type=int, default=20261025)
    a = ap.parse_args()
    t0 = time.perf_counter()
    if a.gerar_fixture_2022:
        print("gravados:", len(gerar_fixture_2022()), "arquivos em", FIXTURES / "2022")
    if a.ensaio_2022:
        r = ensaios_historicos(a.n)
        print(json.dumps(r["agregado"], ensure_ascii=False))
    if a.rodar_tudo:
        rodar_2026(a.n, a.seed, a.fonte, municipios=not a.sem_municipios)
        import publicar
        publicar.main()
    if a.replay_2022:
        t = replay_resumo()
        _gravar_json(DADOS / "replay_projecao_2022.json", {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                                            "parametros": PARAM_MUN,
                                                            "tabela": t.reset_index().to_dict(orient="records")})
        with pd.option_context("display.width", 250, "display.max_columns", 30):
            print(t)
    if not (a.rodar_tudo or a.ensaio_2022 or a.gerar_fixture_2022 or a.replay_2022):
        ap.print_help()
    print(f"tempo {time.perf_counter() - t0:.1f} s")


if __name__ == "__main__":
    main()
