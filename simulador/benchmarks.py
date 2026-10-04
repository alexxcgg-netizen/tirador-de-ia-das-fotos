"""Benchmarks para a noite da apuração do 1º turno de 2026 ("o que observar hoje").

Lê a previsão pré-eleitoral (web/resultados.json, visões calibrada e neutra) e os resultados
TSE históricos (data/resultados_uf_2002_2022.csv, data/municipios_2018.csv, data/municipios_2022.csv)
e grava:

  data/benchmarks_uf.csv   uma linha por UF (+ ZZ exterior) e uma linha BR
  web/benchmarks.json      o mesmo, mais UFs e municípios "bellwether"

Para cada unidade:
  * Lula e Flávio no 1º turno (% dos válidos) esperados em cada visão: média, p10, p50, p90;
  * Lula e Bolsonaro no 1º turno de 2022 (TSE);
  * limiares de sinal: o valor final na UF em que as duas visões são igualmente prováveis
    (acima/abaixo dele, a visão correspondente fica mais provável) e os valores em que a razão
    de verossimilhança chega a 3:1 para cada lado. A distribuição de cada visão é aproximada por
    uma normal com média = média do modelo e dp = (p90 − p10) / 2,563.

Atenção: as duas visões diferem sobretudo por um deslocamento nacional (viés das pesquisas). Uma
UF isolada traz pouca evidência (erro estadual ~3 p.p. ≫ diferença entre as visões); o sinal útil
vem do nacional e da média de muitas UFs. A coluna `separacao` (|Δmédia| / dp) mede isso.

Uso: python simulador/benchmarks.py
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
DATA = RAIZ / "data"
WEB = RAIZ / "web"

Z90 = 1.2815515655446004  # quantil 0,9 da normal padrão
QS = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]  # níveis de rodar.py (quantis nacionais)
I10, I50, I90 = QS.index(0.1), QS.index(0.5), QS.index(0.9)
VISOES = ("calibrado", "neutro")
LR_FORTE = 3.0
ANOS_BELLWETHER = (2006, 2010, 2014, 2018, 2022)
UFS_27 = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI",
          "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]


# ------------------------------------------------------------------ estatística
def sd_de_quantis(p10: float, p90: float) -> float:
    return (p90 - p10) / (2 * Z90)


def log_razao(x, m1, s1, m2, s2):
    """log f1(x) − log f2(x) para normais N(m1, s1) e N(m2, s2)."""
    return (-((x - m1) ** 2) / (2 * s1 ** 2) - math.log(s1)) - (-((x - m2) ** 2) / (2 * s2 ** 2) - math.log(s2))


def limiar(m1: float, s1: float, m2: float, s2: float, log_k: float = 0.0) -> float:
    """Valor x em que log f1(x) − log f2(x) = log_k, do lado em que a visão 1 ganha força.

    Com log_k = 0: ponto de indiferença (entre as médias). Com log_k > 0: valor a partir do qual
    a visão 1 é k vezes mais provável (do lado de m1). Retorna nan se não houver raiz.
    """
    # a x² + b x + c = 0
    a = -1 / (2 * s1 ** 2) + 1 / (2 * s2 ** 2)
    b = m1 / s1 ** 2 - m2 / s2 ** 2
    c = -(m1 ** 2) / (2 * s1 ** 2) + (m2 ** 2) / (2 * s2 ** 2) - math.log(s1) + math.log(s2) - log_k
    if abs(a) < 1e-12:
        if abs(b) < 1e-12:
            return float("nan")
        raizes = [-c / b]
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return float("nan")
        r = math.sqrt(disc)
        raizes = [(-b + r) / (2 * a), (-b - r) / (2 * a)]
    mid = (m1 + m2) / 2
    if log_k == 0:
        cand = [x for x in raizes if min(m1, m2) - 1e-9 <= x <= max(m1, m2) + 1e-9]
        if cand:
            return float(cand[0])
        return float(min(raizes, key=lambda x: abs(x - mid)))
    # do lado de m1 (a partir do ponto médio, na direção de m1); escolhe a raiz mais próxima
    lado = 1 if m1 >= m2 else -1
    cand = [x for x in raizes if (x - mid) * lado >= -1e-9]
    if not cand:
        return float("nan")
    return float(min(cand, key=lambda x: abs(x - mid)))


def sinais(m_cal, s_cal, m_neu, s_neu) -> dict:
    """Limiares com dp comum (média das duas): evita cruzamentos espúrios da aproximação normal
    quando os dp diferem um pouco. Com dp comum o ponto de indiferença é o ponto médio e a razão
    de verossimilhança é monotônica no valor observado."""
    s = (s_cal + s_neu) / 2
    lk = math.log(LR_FORTE)
    return {
        "indiferenca": limiar(m_cal, s, m_neu, s),
        "calibrado_3x": limiar(m_cal, s, m_neu, s, lk),
        "neutro_3x": limiar(m_neu, s, m_cal, s, lk),
        "separacao": abs(m_cal - m_neu) / s,
    }


# ------------------------------------------------------------------ dados
def carregar_previsao(caminho: Path = WEB / "resultados.json") -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_historico(caminho: Path = DATA / "resultados_uf_2002_2022.csv") -> pd.DataFrame:
    return pd.read_csv(caminho)


def _bloco_cand(media, p10, p50, p90):
    return {"media": round(media, 2), "p10": round(p10, 2), "p50": round(p50, 2), "p90": round(p90, 2),
            "sd": round(sd_de_quantis(p10, p90), 3)}


def benchmarks_unidades(prev: dict, hist: pd.DataFrame) -> list[dict]:
    h22 = hist[(hist.ano == 2022) & (hist.turno == 1)].set_index("uf")
    linhas = []

    # ---- nacional
    nac = {"uf": "BR", "nome": "Brasil", "regiao": "BR",
           "eleitores": int(sum(u["eleitores"] for u in prev["visoes"]["calibrado"]["ufs"]))}
    for v in VISOES:
        pt = prev["visoes"][v]["primeiro_turno"]
        for cand, chave in (("lula", "Lula"), ("flavio", "Flavio")):
            q = pt[chave]["quantis"]
            nac[f"{cand}_{v}"] = _bloco_cand(pt[chave]["media"], q[I10], q[I50], q[I90])
        qm = pt["margem_lula_flavio"]["quantis"]
        nac[f"margem_{v}"] = _bloco_cand(pt["margem_lula_flavio"]["media"], qm[I10], qm[I50], qm[I90])
    linhas.append(nac)

    # ---- UFs
    neu = {u["uf"]: u for u in prev["visoes"]["neutro"]["ufs"]}
    for u in prev["visoes"]["calibrado"]["ufs"]:
        r = {"uf": u["uf"], "nome": u["nome"], "regiao": u["regiao"], "eleitores": int(u["eleitores"])}
        for v, src in (("calibrado", u), ("neutro", neu[u["uf"]])):
            for cand in ("lula", "flavio"):
                q = src[f"{cand}_1t_q"]
                r[f"{cand}_{v}"] = _bloco_cand(src[f"{cand}_1t_media"], q[0], q[1], q[2])
            r[f"margem_{v}"] = {"media": round(src["lula_1t_media"] - src["flavio_1t_media"], 2)}
        linhas.append(r)

    tot = nac["eleitores"]
    for r in linhas:
        r["pct_eleitorado"] = round(100 * r["eleitores"] / tot, 3) if r["uf"] != "BR" else 100.0
        if r["uf"] in h22.index:
            x = h22.loc[r["uf"]]
            r["lula_2022_1t"] = round(float(x.pt_pct_validos), 2)
            r["bolsonaro_2022_1t"] = round(float(x.oponente_pct_validos), 2)
            r["margem_2022_1t"] = round(r["lula_2022_1t"] - r["bolsonaro_2022_1t"], 2)
        for cand in ("lula", "flavio"):
            c, n = r[f"{cand}_calibrado"], r[f"{cand}_neutro"]
            r[f"sinal_{cand}"] = {k: round(val, 2) for k, val in sinais(c["media"], c["sd"], n["media"], n["sd"]).items()}
        if "sd" in r["margem_calibrado"]:
            c, n = r["margem_calibrado"], r["margem_neutro"]
            r["sinal_margem"] = {k: round(val, 2) for k, val in sinais(c["media"], c["sd"], n["media"], n["sd"]).items()}
        if "lula_2022_1t" in r:
            r["swing_lula_esperado_calibrado"] = round(r["lula_calibrado"]["media"] - r["lula_2022_1t"], 2)
            r["swing_lula_esperado_neutro"] = round(r["lula_neutro"]["media"] - r["lula_2022_1t"], 2)
    return linhas


# ------------------------------------------------------------------ bellwethers
def bellwether_ufs(hist: pd.DataFrame, anos=ANOS_BELLWETHER) -> list[dict]:
    """UFs mais próximas do resultado nacional (fatia PT nos dois primeiros e % válidos), 1º e 2º turnos."""
    h = hist[hist.ano.isin(anos)].copy()
    br = h[h.uf == "BR"].set_index(["ano", "turno"])
    out = []
    for uf, g in h[h.uf.isin(UFS_27)].groupby("uf"):
        g = g.drop_duplicates(["ano", "turno"]).set_index(["ano", "turno"])
        d2p = g.pt_2p_pct - br.loc[g.index, "pt_2p_pct"]
        dval = g.pt_pct_validos - br.loc[g.index, "pt_pct_validos"]
        g1 = g.xs(1, level="turno")
        b1 = br.xs(1, level="turno")
        # PT em 1º na UF no 1º turno == PT em 1º no Brasil
        acerto_1t = int(((g1.pt_pct_validos > g1.oponente_pct_validos) ==
                         (b1.loc[g1.index, "pt_pct_validos"] > b1.loc[g1.index, "oponente_pct_validos"])).sum())
        g2 = g.xs(2, level="turno")
        b2 = br.xs(2, level="turno")
        acerto_2t = int(((g2.pt_pct_validos > 50) == (b2.loc[g2.index, "pt_pct_validos"] > 50)).sum())
        d1 = d2p.xs(1, level="turno")
        out.append({
            "uf": uf,
            "desvio_medio_abs_2p_pp": round(float(d2p.abs().mean()), 2),
            "desvio_medio_abs_2p_1t_pp": round(float(d1.abs().mean()), 2),
            "desvio_medio_abs_validos_1t_pp": round(float(dval.xs(1, level="turno").abs().mean()), 2),
            "lean_medio_2p_pp": round(float(d2p.mean()), 2),
            "lean_2p_1t_2022_pp": round(float(d1.loc[2022]), 2) if 2022 in d1.index else None,
            "lean_2p_1t_por_ano": {int(a): round(float(v), 2) for a, v in d1.items()},
            "acertou_1o_lugar_1t": f"{acerto_1t}/{len(g1)}",
            "acertou_vencedor_2t": f"{acerto_2t}/{len(g2)}",
        })
    out.sort(key=lambda r: r["desvio_medio_abs_2p_pp"])
    return out


def _mun(caminho: Path) -> pd.DataFrame:
    m = pd.read_csv(caminho)
    m["pt_2p"] = 100 * m.pt_votos / (m.pt_votos + m.bolsonaro_votos)
    return m


def bellwether_municipios(arquivos: dict | None = None, min_validos: int = 100_000, top: int = 15) -> list[dict]:
    """Municípios grandes mais próximos do nacional (PT x Bolsonaro, 1º turno de 2018 e 2022).

    O repositório só tem dados municipais de 2018 e 2022 (TSE munzona); 2006–2014 não entram aqui.
    """
    arquivos = arquivos or {2018: DATA / "municipios_2018.csv", 2022: DATA / "municipios_2022.csv"}
    devs = []
    for ano, p in arquivos.items():
        if not Path(p).exists():
            continue
        m = _mun(p)
        nac = 100 * m.pt_votos.sum() / (m.pt_votos.sum() + m.bolsonaro_votos.sum())
        m = m.assign(**{f"lean_{ano}": m.pt_2p - nac})
        devs.append(m.set_index("cd_municipio_tse")[["uf", "municipio", "validos", "pt_2p", f"lean_{ano}"]]
                    .rename(columns={"validos": f"validos_{ano}", "pt_2p": f"pt_2p_{ano}"}))
    if not devs:
        return []
    df = devs[0]
    for d in devs[1:]:
        df = df.join(d.drop(columns=["uf", "municipio"]), how="inner")
    ult = max(arquivos)
    df = df[df[f"validos_{ult}"] >= min_validos]
    leans = [c for c in df.columns if c.startswith("lean_")]
    df = df.assign(desvio=df[leans].abs().mean(axis=1)).sort_values("desvio").head(top)
    out = []
    for cd, r in df.iterrows():
        out.append({"cd_municipio_tse": int(cd), "uf": r.uf, "municipio": r.municipio,
                    "validos_2022": int(r.get("validos_2022", 0)),
                    "desvio_medio_abs_2p_pp": round(float(r.desvio), 2),
                    **{c: round(float(r[c]), 2) for c in leans}})
    return out


# ------------------------------------------------------------------ ordem da apuração (2022 → 2026)
# 1º turno de 2022, % das seções totalizadas pelo TSE x % válidos (horário de Brasília).
# Fontes: blog ao vivo da Suno (https://www.suno.com.br/noticias/votacao-eleicoes-2022/), CGTN (70%),
# France 24 (97,3%), TSE (final). Detalhes e ressalvas em APURACAO_2022_ORDEM.md.
APURACAO_2022_1T = [
    # (horário, % apurado, Lula, Bolsonaro)
    ("17:36", 0.62, 41.04, 48.23),
    ("17:49", 1.03, 41.32, 48.37),
    ("18:14", 4.23, 42.03, 48.84),
    ("18:38", 10.0, 42.87, 48.35),
    ("19:00", 20.0, 43.32, 47.93),
    ("19:21", 35.51, 43.86, 47.34),
    ("19:38", 52.21, 44.86, 46.31),
    ("20:06", 66.66, 45.55, 45.69),
    ("20:15", 70.0, 45.74, 45.51),
    ("~21:30", 97.3, 47.9, 43.7),
    ("22:57", 99.54, 48.31, 43.30),
    ("final", 100.0, 48.43, 43.20),
]


def _margem_regional(ufs: list, chave: str) -> float:
    """Margem Lula − adversário média (ponderada por eleitores) em N+NE menos a de S+SE+CO."""
    acc = {True: [0.0, 0.0], False: [0.0, 0.0]}
    for r in ufs:
        if r["uf"] == "ZZ" or chave not in r:
            continue
        m = r[chave]["media"] if isinstance(r[chave], dict) else r[chave]
        g = r["regiao"] in ("N", "NE")
        acc[g][0] += m * r["eleitores"]
        acc[g][1] += r["eleitores"]
    return acc[True][0] / acc[True][1] - acc[False][0] / acc[False][1]


def trajetoria_esperada(nacional: dict, ufs: list) -> dict:
    """Margem parcial (Lula − Flávio) esperada por % apurado, se a ordem da apuração repetir 2022.

    deriva_2022(p) = margem parcial − margem final em 2022. Para 2026 ela é escalada por
    k = (gap regional N+NE x S+SE+CO esperado em 2026) / (gap de 2022), porque a deriva vem de
    o Sul/Sudeste/Centro-Oeste serem totalizados antes do Norte/Nordeste.
    """
    final22 = APURACAO_2022_1T[-1][2] - APURACAO_2022_1T[-1][3]
    k = {v: _margem_regional(ufs, f"margem_{v}") / _margem_regional(ufs, "margem_2022_1t") for v in VISOES}
    linhas = []
    for hora, pct, lula, bol in APURACAO_2022_1T:
        der = (lula - bol) - final22
        lin = {"hora_brasilia_2022": hora, "pct_apurado": pct, "lula_2022": lula, "bolsonaro_2022": bol,
               "margem_2022": round(lula - bol, 2), "deriva_2022": round(der, 2)}
        for v in VISOES:
            lin[f"margem_esperada_{v}"] = round(nacional[f"margem_{v}"]["media"] + k[v] * der, 2)
        kk = (k["calibrado"] + k["neutro"]) / 2
        lin["margem_indiferenca"] = round(nacional["sinal_margem"]["indiferenca"] + kk * der, 2)
        linhas.append(lin)
    return {"k_escala": {v: round(x, 3) for v, x in k.items()}, "pontos": linhas,
            "nota": ("Ilustrativo: supõe a mesma ordem de totalização de 2022, escalada pelo gap regional esperado. "
                     "Margem em p.p. dos válidos, Lula − Flávio (2022: Lula − Bolsonaro).")}


# ------------------------------------------------------------------ saída
def achatar(r: dict) -> dict:
    f = {"uf": r["uf"], "nome": r["nome"], "regiao": r["regiao"], "eleitores_2026": r["eleitores"],
         "pct_eleitorado": r["pct_eleitorado"]}
    for v in VISOES:
        for cand in ("lula", "flavio"):
            for k in ("media", "p10", "p50", "p90"):
                f[f"{cand}_{v}_{k}"] = r[f"{cand}_{v}"][k]
        f[f"margem_{v}_media"] = r[f"margem_{v}"]["media"]
    for k in ("lula_2022_1t", "bolsonaro_2022_1t", "margem_2022_1t",
              "swing_lula_esperado_calibrado", "swing_lula_esperado_neutro"):
        f[k] = r.get(k, "")
    for cand in ("lula", "flavio"):
        for k in ("indiferenca", "calibrado_3x", "neutro_3x", "separacao"):
            f[f"sinal_{cand}_{k}"] = r[f"sinal_{cand}"][k]
    for k in ("indiferenca", "calibrado_3x", "neutro_3x", "separacao"):
        f[f"sinal_margem_{k}"] = r["sinal_margem"][k] if "sinal_margem" in r else ""
    return f


def gerar(prev: dict | None = None, hist: pd.DataFrame | None = None, escrever: bool = True) -> dict:
    prev = prev if prev is not None else carregar_previsao()
    hist = hist if hist is not None else carregar_historico()
    unid = benchmarks_unidades(prev, hist)
    out = {
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "previsao_gerada_em": prev["meta"].get("gerado_em"),
            "data_referencia": prev["meta"].get("data_referencia"),
            "unidade": "% dos votos válidos no 1º turno",
            "metodo": ("Cada visão aproximada por normal (média do modelo; dp = (p90 − p10)/2,563; limiares com o dp médio das duas). "
                       "sinal.indiferenca = valor final em que calibrado e neutro são igualmente prováveis; "
                       "calibrado_3x / neutro_3x = valor a partir do qual a visão é 3x mais provável que a outra. "
                       "separacao = |Δmédia|/dp: abaixo de ~0,5 a UF sozinha quase não distingue as visões."),
            "fontes": ["web/resultados.json (rodada de 3–4/10/2026)",
                       "data/resultados_uf_2002_2022.csv (TSE)",
                       "data/municipios_2018.csv, data/municipios_2022.csv (TSE votacao_candidato_munzona, 1º turno)"],
        },
        "nacional": unid[0],
        "ufs": unid[1:],
        "trajetoria_apuracao": trajetoria_esperada(unid[0], unid[1:]),
        "bellwether_ufs": bellwether_ufs(hist),
        "bellwether_municipios": bellwether_municipios(),
    }
    if escrever:
        linhas = [achatar(r) for r in unid]
        with open(DATA / "benchmarks_uf.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
            w.writeheader()
            w.writerows(linhas)
        (WEB / "benchmarks.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main():
    out = gerar()
    n = out["nacional"]
    print(f"BR  Lula cal {n['lula_calibrado']['media']} / neu {n['lula_neutro']['media']} "
          f"| indiferença {n['sinal_lula']['indiferenca']} | 2022 {n.get('lula_2022_1t')}")
    print(f"BR  margem cal {n['margem_calibrado']['media']} / neu {n['margem_neutro']['media']} "
          f"| indiferença {n['sinal_margem']['indiferenca']}")
    for r in out["ufs"]:
        print(f"{r['uf']:3} Lula cal {r['lula_calibrado']['media']:5.1f} neu {r['lula_neutro']['media']:5.1f} "
              f"ind {r['sinal_lula']['indiferenca']:5.1f} sep {r['sinal_lula']['separacao']:.2f} 2022 {r.get('lula_2022_1t', '')}")
    for p in out["trajetoria_apuracao"]["pontos"]:
        print(f"{p['pct_apurado']:6.2f}% 2022 {p['margem_2022']:+6.2f} | 2026 cal {p['margem_esperada_calibrado']:+6.2f} "
              f"neu {p['margem_esperada_neutro']:+6.2f} ind {p['margem_indiferenca']:+6.2f}")
    print("k:", out["trajetoria_apuracao"]["k_escala"])
    print("Bellwether UFs:", [(b["uf"], b["desvio_medio_abs_2p_pp"]) for b in out["bellwether_ufs"][:6]])
    print("Bellwether municípios:", [(b["municipio"], b["uf"], b["desvio_medio_abs_2p_pp"]) for b in out["bellwether_municipios"][:8]])


if __name__ == "__main__":
    main()
