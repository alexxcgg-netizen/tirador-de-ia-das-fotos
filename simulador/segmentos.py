"""Módulo de segmentos do eleitorado para o simulador presidencial de 2026.

Funções puras (NumPy/pandas), independentes de ``modelo.py``. Três blocos:

(a) **Prior demográfico por UF** — regressão ridge do lean partidário da UF
    (fatia do PT na UF menos a nacional, em logito, TSE 2018/2022) em
    covariáveis da UF (Bolsa Família, evangélicos, brancos, renda, urbanização,
    60+, superior completo). Validação por leave-one-out (LOO) e fora do tempo
    (treina na eleição t−1, prevê a eleição t), comparada com o prior simples
    ``0,85 × lean anterior`` usado em ``modelo.py``. Produz um prior misto por
    UF e o seu desvio-padrão.

(b) **Comparecimento por segmento** — abstenção por UF × faixa etária ×
    escolaridade × gênero (TSE, perfil_comparecimento_abstencao 2022),
    combinada com o voto por segmento (Datafolha 2022 e 2026) num modelo
    logístico aditivo por célula. O resultado é o "ajuste de comparecimento"
    por UF: quanto muda a fatia de Lula nos votos válidos quando se passa da
    população das pesquisas (todo o eleitorado apto) para quem de fato vota.

(c) **Decomposição por segmento para exibição** — voto por segmento
    (Datafolha 2022 2º turno x 2026 1º turno, mais Quaest/Atlas), com tamanho
    de cada segmento (TSE 2026, Censo 2022, MDS), em estrutura pronta para JSON.

Unidades: "lean" e ajustes em logito são relativos à fatia bipartidária de
Lula/PT (Lula/(Lula+oponente)); "p.p." = pontos percentuais dessa fatia.
Interface para integração em SEGMENTOS.md.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]


# ============================================================== utilidades
def logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=float)))


def lean_para_pp(lean_logito, nacional):
    """Converte lean em logito para p.p. da fatia, dado o nível nacional (0-1)."""
    return (expit(logit(nacional) + np.asarray(lean_logito)) - nacional) * 100


# ============================================================== (a) prior demográfico
#: Covariáveis do prior demográfico: nome curto -> (coluna em covariaveis_uf.csv, transformação)
COVARIAVEIS_PRIOR = {
    "pbf_por_100_eleitores": ("pbf_familias_por_100_eleitores", None),
    "pct_evangelicos": ("pct_evangelicos_10mais_c2022", None),
    "pct_brancos": ("pct_branca_c2022", None),
    "log_renda_pc": ("renda_pc_pnadc2025_rs", "log"),
    "pct_urbana": ("pct_urbana_c2022", None),
    "pct_60mais": ("pct_60mais_tse2026", None),
    "pct_superior": ("pct_sup_compl_tse2026", None),
}

#: Fator do prior simples de modelo.py (premissas.json, estados.fator_lean).
FATOR_LEAN_SIMPLES = 0.85


def carregar_covariaveis(caminho: Path | str = DADOS / "covariaveis_uf.csv") -> pd.DataFrame:
    """Lê as covariáveis por UF e devolve DataFrame (índice = UF) com as colunas
    de ``COVARIAVEIS_PRIOR`` já transformadas (log da renda)."""
    cov = pd.read_csv(caminho).set_index("uf")
    X = pd.DataFrame(index=cov.index)
    for nome, (col, transf) in COVARIAVEIS_PRIOR.items():
        X[nome] = np.log(cov[col]) if transf == "log" else cov[col].astype(float)
    return X.loc[UFS]


def carregar_leans(caminho: Path | str = DADOS / "resultados_uf_2002_2022.csv") -> tuple[dict, dict]:
    """Lean do PT por UF em logito, por (ano, turno), e fatia nacional.

    1º turno: fatia bipartidária PT/(PT+2º colocado nacional) (``pt_2p_pct``);
    2º turno: % de válidos do PT. Lean = logito(UF) − logito(Brasil, com exterior),
    a mesma definição de ``modelo.carregar_ufs``.
    Devolve ({(ano, turno): Series por UF}, {(ano, turno): fatia nacional 0-1}).
    """
    res = pd.read_csv(caminho)
    leans, nac = {}, {}
    for (ano, turno), g in res.groupby(["ano", "turno"]):
        g = g.set_index("uf")
        col = "pt_2p_pct" if turno == 1 else "pt_pct_validos"
        br = g.loc["BR", col] / 100
        leans[(int(ano), int(turno))] = pd.Series(logit(g.loc[UFS, col] / 100) - logit(br), index=UFS)
        nac[(int(ano), int(turno))] = float(br)
    return leans, nac


def _padronizar(X: np.ndarray, ref: np.ndarray | None = None):
    ref = X if ref is None else ref
    mu, sd = ref.mean(0), ref.std(0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    return (X - mu) / sd


def ridge_ajustar(X: np.ndarray, y: np.ndarray, lam: float, w: np.ndarray | None = None) -> np.ndarray:
    """Ridge com intercepto não penalizado. X já padronizado. Devolve [b0, b...]."""
    n, p = X.shape
    A = np.c_[np.ones(n), X]
    W = np.ones(n) if w is None else np.asarray(w, float)
    P = lam * np.eye(p + 1)
    P[0, 0] = 0.0
    return np.linalg.solve(A.T @ (A * W[:, None]) + P, A.T @ (W * y))


def ridge_prever(beta: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.c_[np.ones(len(X)), X] @ beta


def ridge_loo(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """Previsões leave-one-out (reajusta sem a observação i, inclusive a padronização)."""
    n = len(y)
    out = np.empty(n)
    for i in range(n):
        m = np.arange(n) != i
        Zm = _padronizar(X[m])
        Zi = _padronizar(X[i:i + 1], X[m])
        out[i] = ridge_prever(ridge_ajustar(Zm, y[m], lam), Zi)[0]
    return out


def rmse_pp(prev_logito, obs_logito, nacional) -> float:
    """RMSE em p.p. da fatia do PT (converte os leans em fatias no nível nacional observado)."""
    a = expit(logit(nacional) + np.asarray(prev_logito))
    b = expit(logit(nacional) + np.asarray(obs_logito))
    return float(np.sqrt(np.mean((a - b) ** 2)) * 100)


GRADE_LAMBDA = (0.3, 1.0, 3.0, 10.0, 30.0)
GRADE_PESO = tuple(np.round(np.arange(0.5, 1.0001, 0.05), 2))


def escolher_lambda(X: np.ndarray, y: np.ndarray, nacional: float, grade=GRADE_LAMBDA) -> tuple[float, dict]:
    """Escolhe o λ do ridge pelo menor RMSE LOO (em p.p.)."""
    tab = {lam: rmse_pp(ridge_loo(X, y, lam), y, nacional) for lam in grade}
    return min(tab, key=tab.get), tab


def validar_prior_demografico(turno: int = 2, X: pd.DataFrame | None = None,
                              leans: dict | None = None, nac: dict | None = None) -> dict:
    """Validação do prior demográfico (RMSEs em p.p. da fatia do PT, 27 UFs).

    * ``loo_demografico_{ano}``: ridge covariáveis -> lean do mesmo ano, LOO
      (λ escolhido por LOO aninhado: para cada UF retirada, λ é escolhido só
      com as outras 26). Mede o quanto a demografia "explica" o mapa.
    * ``simples_{t-1}->{t}``: prior de modelo.py, 0,85 × lean da eleição anterior.
    * ``demografico_{t-1}->{t}``: ridge treinado no lean da eleição anterior
      (todas as UFs, como no uso para 2026) usado como previsão do lean
      seguinte; ``demografico_loo_*`` é o mesmo sem a própria UF no treino.
    * ``misto_{t-1}->{t}``: w × simples + (1−w) × demográfico. O peso w é
      escolhido minimizando a média dos RMSEs das duas transições (2014→2018,
      2018→2022); por isso o misto é levemente otimista (só 1 parâmetro).
    """
    X = carregar_covariaveis() if X is None else X
    if leans is None or nac is None:
        leans, nac = carregar_leans()
    Xv = X.loc[UFS].values
    out = {"turno": turno, "n_ufs": len(UFS)}

    # λ por LOO em cada ano (e LOO aninhado para o RMSE reportado)
    lambdas = {}
    for ano in (2018, 2022):
        y = leans[(ano, turno)].values
        lam, tab = escolher_lambda(Xv, y, nac[(ano, turno)])
        lambdas[ano] = lam
        aninh = np.empty(len(y))
        for i in range(len(y)):
            m = np.arange(len(y)) != i
            lam_i, _ = escolher_lambda(Xv[m], y[m], nac[(ano, turno)])
            Zm = _padronizar(Xv[m])
            aninh[i] = ridge_prever(ridge_ajustar(Zm, y[m], lam_i), _padronizar(Xv[i:i + 1], Xv[m]))[0]
        out[f"loo_demografico_{ano}"] = rmse_pp(aninh, y, nac[(ano, turno)])
        out[f"loo_por_lambda_{ano}"] = {str(k): round(v, 3) for k, v in tab.items()}
        out[f"r2_loo_{ano}"] = float(1 - np.mean((aninh - y) ** 2) / np.var(y))
    out["lambda"] = lambdas

    trans = [(2014, 2018), (2018, 2022)]
    S, D, Y = {}, {}, {}
    for a0, a1 in trans:
        y0, y1 = leans[(a0, turno)].values, leans[(a1, turno)].values
        S[a1] = FATOR_LEAN_SIMPLES * y0
        # análogo exato do uso em 2026: ridge treinado com TODAS as UFs no lean da
        # eleição anterior (a própria UF entra no ajuste, como entrará o lean 2022)
        lam0 = lambdas.get(a0, lambdas[2018])
        D[a1] = ridge_prever(ridge_ajustar(_padronizar(Xv), y0, lam0), _padronizar(Xv))
        out[f"demografico_loo_{a0}->{a1}"] = rmse_pp(ridge_loo(Xv, y0, lam0), y1, nac[(a1, turno)])
        Y[a1] = y1
        out[f"simples_{a0}->{a1}"] = rmse_pp(S[a1], y1, nac[(a1, turno)])
        out[f"demografico_{a0}->{a1}"] = rmse_pp(D[a1], y1, nac[(a1, turno)])
        out[f"persistencia_1.0_{a0}->{a1}"] = rmse_pp(y0, y1, nac[(a1, turno)])
    curva = {}
    for w in GRADE_PESO:
        curva[w] = [rmse_pp(w * S[a1] + (1 - w) * D[a1], Y[a1], nac[(a1, turno)]) for _, a1 in trans]
    w_opt = min(curva, key=lambda w: np.mean(curva[w]))
    out["peso_simples"] = float(w_opt)
    out["curva_peso"] = {str(w): [round(v, 3) for v in r] for w, r in curva.items()}
    for (a0, a1), v in zip(trans, curva[w_opt]):
        out[f"misto_{a0}->{a1}"] = v
    # erro do prior misto em logito (para o dp por UF): RMSE na transição mais recente
    e = (w_opt * S[2022] + (1 - w_opt) * D[2022]) - Y[2022]
    out["dp_misto_logito_2018->2022"] = float(np.sqrt(np.mean(e ** 2)))
    e_all = np.concatenate([(w_opt * S[a1] + (1 - w_opt) * D[a1]) - Y[a1] for _, a1 in trans])
    out["dp_misto_logito_media"] = float(np.sqrt(np.mean(e_all ** 2)))
    e_s = S[2022] - Y[2022]
    e_d = D[2022] - Y[2022]
    out["correlacao_erros_simples_demografico_2022"] = float(np.corrcoef(e_s, e_d)[0, 1])
    return out


def prior_demografico_uf(turno: int = 2, validacao: dict | None = None,
                         X: pd.DataFrame | None = None, leans: dict | None = None,
                         nac: dict | None = None) -> pd.DataFrame:
    """Prior por UF para 2026, em logito (lean relativo ao nacional).

    Colunas:
      * ``lean_2022_logito``: lean observado em 2022;
      * ``prior_simples_logito`` = 0,85 × lean 2022 (o prior atual de modelo.py);
      * ``prior_demografico_logito``: ridge (covariáveis -> lean 2022, todas as UFs);
      * ``prior_demografico_loo_logito``: idem sem a própria UF (checagem);
      * ``prior_misto_logito`` = w × simples + (1−w) × demográfico (w da validação);
      * ``dp_prior_logito``: dp do prior misto = RMSE fora do tempo do misto
        (média das transições 2014→18 e 2018→22, em logito) somado em quadratura
        à incerteza de previsão do ridge para a UF (alavancagem). Conservador:
        inclui o realinhamento de 2018;
      * ``dp_prior_recente_logito``: idem só com a transição 2018→2022;
      * ``*_pp``: os mesmos valores em p.p. da fatia, no nível nacional de 2022;
      * ``discrepancia_pp`` = demográfico − simples (sinal de alerta: UF cujo
        voto de 2022 destoa do que a demografia sugere).
    """
    X = carregar_covariaveis() if X is None else X
    if leans is None or nac is None:
        leans, nac = carregar_leans()
    val = validacao or validar_prior_demografico(turno, X, leans, nac)
    Xv = X.loc[UFS].values
    y = leans[(2022, turno)].values
    lam = val["lambda"][2022]
    Z = _padronizar(Xv)
    beta = ridge_ajustar(Z, y, lam)
    dem = ridge_prever(beta, Z)
    dem_loo = ridge_loo(Xv, y, lam)
    w = val["peso_simples"]
    simples = FATOR_LEAN_SIMPLES * y
    misto = w * simples + (1 - w) * dem
    # incerteza de previsão do ridge (alavancagem) com resíduo LOO
    A = np.c_[np.ones(len(Z)), Z]
    P = lam * np.eye(A.shape[1]); P[0, 0] = 0
    H = A @ np.linalg.solve(A.T @ A + P, A.T)
    s2 = np.mean((dem_loo - y) ** 2)
    se_dem = np.sqrt(np.clip(np.diag(H), 0, None) * s2)
    dp = np.sqrt(val["dp_misto_logito_media"] ** 2 + ((1 - w) * se_dem) ** 2)
    dp_rec = np.sqrt(val["dp_misto_logito_2018->2022"] ** 2 + ((1 - w) * se_dem) ** 2)
    n22 = nac[(2022, turno)]
    df = pd.DataFrame({
        "uf": UFS, "turno": turno,
        "lean_2022_logito": y,
        "prior_simples_logito": simples,
        "prior_demografico_logito": dem,
        "prior_demografico_loo_logito": dem_loo,
        "prior_misto_logito": misto,
        "dp_prior_logito": dp,
        "dp_prior_recente_logito": dp_rec,
    })
    for c in ["lean_2022", "prior_simples", "prior_demografico", "prior_demografico_loo", "prior_misto"]:
        df[c + "_pp"] = lean_para_pp(df[c + "_logito"], n22)
    df["dp_prior_pp"] = df["dp_prior_logito"] * n22 * (1 - n22) * 100
    df["dp_prior_recente_pp"] = df["dp_prior_recente_logito"] * n22 * (1 - n22) * 100
    df["discrepancia_pp"] = df["prior_demografico_pp"] - df["prior_simples_pp"]
    df["peso_simples"] = w
    df["lambda_ridge"] = lam
    df.attrs["coeficientes_logito_por_dp"] = dict(zip(X.columns, beta[1:].round(4)))
    df.attrs["validacao"] = val
    return df


def coeficientes_prior(turno: int = 2) -> dict:
    """Coeficientes do ridge (logito por 1 dp da covariável) ajustado no lean 2022."""
    X = carregar_covariaveis()
    leans, nac = carregar_leans()
    y = leans[(2022, turno)].values
    lam, _ = escolher_lambda(X.values, y, nac[(2022, turno)])
    beta = ridge_ajustar(_padronizar(X.values), y, lam)
    return {"intercepto": float(beta[0]), **{k: float(v) for k, v in zip(X.columns, beta[1:])},
            "lambda": lam}


# ============================================================== (b) comparecimento por segmento
URL_PERFIL_COMPARECIMENTO_2022 = ("https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/"
                                  "perfil_comparecimento_abstencao_2022.zip")

#: Faixas etárias agregadas (código TSE CD_FAIXA_ETARIA = idade × 100 para 16-20; faixas quinquenais acima)
FAIXAS = ["16-17", "18-24", "25-34", "35-44", "45-59", "60-69", "70-79", "80+"]
#: Escolaridade agregada (cadastro eleitoral do TSE)
ESCOLARIDADES = ["analf_le", "fund_inc", "fund_comp_medio_inc", "medio_comp", "superior"]
GENEROS = ["F", "M"]

_MAPA_ESCOL = {
    "ANALFABETO": "analf_le", "LÊ E ESCREVE": "analf_le",
    "ENSINO FUNDAMENTAL INCOMPLETO": "fund_inc",
    "ENSINO FUNDAMENTAL COMPLETO": "fund_comp_medio_inc", "ENSINO MÉDIO INCOMPLETO": "fund_comp_medio_inc",
    "ENSINO MÉDIO COMPLETO": "medio_comp",
    "SUPERIOR INCOMPLETO": "superior", "SUPERIOR COMPLETO": "superior",
}
_MAPA_GENERO = {"FEMININO": "F", "MASCULINO": "M"}


def _faixa_de_descricao(ds: str) -> str | None:
    """'21 a 24 anos' -> '18-24'; '16 anos' -> '16-17'; 'Inválido' -> None."""
    if not isinstance(ds, str) or not ds[:2].isdigit():
        return None
    idade = int(ds.split()[0])
    for lim, nome in ((18, "16-17"), (25, "18-24"), (35, "25-34"), (45, "35-44"), (60, "45-59"),
                      (70, "60-69"), (80, "70-79")):
        if idade < lim:
            return nome
    return "80+"


def agregar_perfil_comparecimento(caminho_zip: Path | str, saida: Path | str | None = DADOS / "abstencao_segmentos_uf.csv",
                                  ano: int = 2022) -> pd.DataFrame:
    """Agrega o arquivo do TSE ``perfil_comparecimento_abstencao_{ano}.zip`` para
    UF × turno × faixa etária × escolaridade × gênero.

    Lê o ``*_BRASIL.csv`` do zip, que traz todas as UFs **e** o exterior (ZZ):
    o zip de 2022 não tem arquivo próprio para o DF, então os arquivos por UF
    não bastam. Linhas com idade "Inválido", escolaridade ou gênero "NÃO
    INFORMADO" (≈0,05% dos aptos) são descartadas. O comparecimento é o mesmo
    para todos os cargos.
    Os totais por UF conferem com ``resultados_uf_2002_2022.csv`` (diferença
    < 0,2% no eleitorado; abstenção igual até 0,05 p.p.).
    """
    import zipfile
    cols = ["NR_TURNO", "SG_UF", "DS_GENERO", "DS_FAIXA_ETARIA", "DS_GRAU_ESCOLARIDADE",
            "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]
    partes = []
    with zipfile.ZipFile(caminho_zip) as z:
        for nome in z.namelist():
            if not nome.endswith("_BRASIL.csv"):
                continue
            with z.open(nome) as f:
                for ch in pd.read_csv(f, sep=";", encoding="latin1", usecols=cols, chunksize=2_000_000):
                    partes.append(ch.groupby(cols[:5], as_index=False)[cols[5:]].sum())
    bruto = pd.concat(partes).groupby(cols[:5], as_index=False)[cols[5:]].sum()
    return _bandas_de_bruto(bruto, ano, saida)


def _bandas_de_bruto(bruto: pd.DataFrame, ano: int, saida) -> pd.DataFrame:
    d = bruto.copy()
    d["faixa_etaria"] = d["DS_FAIXA_ETARIA"].map(_faixa_de_descricao)
    d["escolaridade"] = d["DS_GRAU_ESCOLARIDADE"].map(_MAPA_ESCOL)
    d["genero"] = d["DS_GENERO"].map(_MAPA_GENERO)
    d = d.dropna(subset=["faixa_etaria", "escolaridade", "genero"])
    g = (d.groupby(["NR_TURNO", "SG_UF", "faixa_etaria", "escolaridade", "genero"], as_index=False)
         [["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]].sum())
    g.columns = ["turno", "uf", "faixa_etaria", "escolaridade", "genero", "aptos", "comparecimento", "abstencao"]
    g.insert(0, "ano", ano)
    g["abstencao_pct"] = (100 * g["abstencao"] / g["aptos"]).round(3)
    g["fonte"] = f"TSE perfil_comparecimento_abstencao_{ano}.zip (agregação própria)"
    g = g.sort_values(["turno", "uf", "faixa_etaria", "escolaridade", "genero"]).reset_index(drop=True)
    if saida is not None:
        g.to_csv(saida, index=False)
    return g


def carregar_abstencao_segmentos(caminho: Path | str = DADOS / "abstencao_segmentos_uf.csv") -> pd.DataFrame:
    """Lê a tabela UF × turno × faixa × escolaridade × gênero (aptos, comparecimento)."""
    return pd.read_csv(caminho)


def abstencao_por_segmento(cel: pd.DataFrame, por: list[str], turno: int = 1) -> pd.DataFrame:
    """Abstenção (%) agregada por qualquer combinação de colunas (ex.: ['faixa_etaria'])."""
    d = cel[cel.turno == turno].groupby(por)[["aptos", "abstencao"]].sum()
    d["abstencao_pct"] = 100 * d["abstencao"] / d["aptos"]
    d["pct_aptos"] = 100 * d["aptos"] / d["aptos"].sum()
    return d.reset_index()


# --------------------------------------------------------------- voto por segmento (fontes)
#: Voto por segmento, fatia de Lula entre os dois primeiros (0-100). Para 2026 (1º turno,
#: votos totais) a fatia é Lula/(Lula+Flávio); para 2022 (2º turno) são os válidos publicados.
#: n = entrevistas da pesquisa (para o erro amostral do segmento: n × peso do segmento).
FONTES_VOTO = {
    "datafolha_2022_2t": {
        "descricao": "Datafolha 28-29/10/2022, véspera do 2º turno, votos válidos Lula x Bolsonaro (BR-08297/2022)",
        "fonte_url": "https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf",
        "n": 8308, "total": 52.0, "fracao_dois_primeiros": 0.94,
        "margens": {
            "genero": {"M": (50, 48), "F": (55, 52)},
            "idade": {"16-24": (57, 14), "25-34": (51, 20), "35-44": (50, 21), "45-59": (53, 25), "60+": (52, 20)},
            "escolaridade": {"fundamental": (61, 28), "medio": (49, 46), "superior": (49, 26)},
            "regiao": {"SE": (48, 43), "S": (40, 14), "NE": (71, 27), "CO": (39, 7), "N": (48, 8)},
        },
    },
    "datafolha_2026_1t": {
        "descricao": "Datafolha 15-17/09/2026, 1º turno, Lula/(Lula+Flávio) a partir dos votos totais (BR-04029/2026)",
        "fonte_url": "https://ncnews.com.br/2026/09/18/datafolha-revela-onde-lula-e-flavio-bolsonaro-concentram-forca-veja-os-recortes-por-idade-renda-religiao-e-regiao/",
        "n": 2002, "total": 100 * 39 / 75, "fracao_dois_primeiros": 0.75,
        "margens": {
            "genero": {"M": (100 * 37 / 76, 47), "F": (100 * 41 / 73, 53)},
            "idade": {"16-24": (100 * 39 / 68, 13), "25-34": (100 * 37 / 76, 19), "35-44": (100 * 41 / 76, 20),
                      "45-59": (100 * 35 / 74, 25), "60+": (100 * 43 / 76, 23)},
            "escolaridade": {"fundamental": (100 * 47 / 77, 30), "medio": (100 * 36 / 74, 46), "superior": (100 * 36 / 73, 24)},
            "regiao": {"NE": (100 * 56 / 82, 27), "SE": (100 * 34 / 71, 42), "S": (100 * 27 / 72, 14), "CO+N": (100 * 35 / 76, 17)},
        },
    },
}
# Pesos dos segmentos em 2026 (2º elemento das tuplas) não foram publicados na nota;
# usam-se os tamanhos do eleitorado TSE 2026 / amostra 2022 como aproximação (só
# afetam o erro amostral simulado, não o ajuste central).

_ESCOL_PARA_PESQUISA = {"analf_le": "fundamental", "fund_inc": "fundamental",
                        "fund_comp_medio_inc": "medio", "medio_comp": "medio", "superior": "superior"}
_FAIXA_PARA_PESQUISA = {"16-17": "16-24", "18-24": "16-24", "25-34": "25-34", "35-44": "35-44",
                        "45-59": "45-59", "60-69": "60+", "70-79": "60+", "80+": "60+"}


def _regiao_cat(regiao: pd.Series, margens_regiao: dict) -> pd.Series:
    if "CO+N" in margens_regiao:
        return regiao.replace({"CO": "CO+N", "N": "CO+N"})
    return regiao


def montar_celulas(cel: pd.DataFrame, turno: int, regioes: pd.Series | None = None) -> pd.DataFrame:
    """Células UF × faixa × escolaridade × gênero de um turno, com região e taxa de comparecimento."""
    regioes = regioes if regioes is not None else pd.read_csv(DADOS / "eleitorado_uf_2026.csv").set_index("uf")["regiao"]
    c = cel[(cel.turno == turno) & cel.uf.isin(UFS)].copy()   # exterior (ZZ) fica fora
    c["regiao"] = c["uf"].map(regioes)
    c["comp_taxa"] = c["comparecimento"] / c["aptos"]
    return c.reset_index(drop=True)


def ajustar_modelo_voto(celulas: pd.DataFrame, fonte: dict, lean_uf: pd.Series | None = None,
                        alvos: dict | None = None, iter_max: int = 200, tol: float = 1e-7) -> dict:
    """Ajusta um modelo logístico aditivo por célula às margens publicadas.

    logito p(célula) = região + desvio da UF na região + idade + escolaridade + gênero.

    * Os efeitos de idade, escolaridade, gênero e região são calibrados (como
      um "raking" no logito) para que a média ponderada pelos **aptos** em cada
      categoria reproduza a margem publicada pela pesquisa (a pesquisa
      representa o eleitorado apto, não só quem vota).
    * O desvio da UF dentro da região é fixo: lean de 2022 da UF menos o lean
      médio da região (``lean_uf`` em logito; se None, zero).
    * Mapeamentos: escolaridade do cadastro TSE -> fundamental (analfabeto a
      fundamental completo) / médio (médio incompleto e completo) / superior;
      16-17 e 18-24 -> 16-24; 60-69, 70-79, 80+ -> 60+.

    Devolve dict com os efeitos e o vetor p por célula.
    """
    alvos = alvos or {k: {c: v[0] / 100 for c, v in m.items()} for k, m in fonte["margens"].items()}
    c = celulas
    w = c["aptos"].values.astype(float)
    cat = {
        "genero": c["genero"].values,
        "idade": c["faixa_etaria"].map(_FAIXA_PARA_PESQUISA).values,
        "escolaridade": c["escolaridade"].map(_ESCOL_PARA_PESQUISA).values,
        "regiao": _regiao_cat(c["regiao"], alvos["regiao"]).values,
    }
    if lean_uf is not None:
        lu = c["uf"].map(lean_uf).values
        df_l = pd.DataFrame({"r": cat["regiao"], "l": lu, "w": w})
        med = df_l.groupby("r").apply(lambda g: np.average(g.l, weights=g.w), include_groups=False)
        desvio = lu - pd.Series(cat["regiao"]).map(med).values
    else:
        desvio = np.zeros(len(c))
    idx = {k: np.array([list(alvos[k]).index(x) for x in cat[k]]) for k in alvos}
    # Coerência das margens: a composição do cadastro TSE difere da amostra (ex.: o
    # cadastro tem mais "fundamental"), então cada dimensão implicaria um total
    # diferente. Desloca-se cada dimensão por uma constante em logito para que a
    # média ponderada pelos aptos seja o total implícito pelas regiões. Preserva
    # os contrastes (em logito) dentro da dimensão, que é o que importa aqui.
    comp = {k: np.bincount(idx[k], weights=w, minlength=len(alvos[k])) / w.sum() for k in alvos}
    total = float(np.sum(comp["regiao"] * np.array(list(alvos["regiao"].values()))))
    alvos = dict(alvos)
    for k in alvos:
        if k == "regiao":
            continue
        lt = logit(np.array(list(alvos[k].values())))
        lo, hi = -3.0, 3.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if np.sum(comp[k] * expit(lt + mid)) < total:
                lo = mid
            else:
                hi = mid
        alvos[k] = dict(zip(alvos[k], expit(lt + (lo + hi) / 2)))
    efeitos = {k: {cc: 0.0 for cc in alvos[k]} for k in alvos}
    efeitos["regiao"] = {cc: float(logit(v)) for cc, v in alvos["regiao"].items()}

    def eta():
        e = desvio.copy()
        for k in alvos:
            e += np.array([efeitos[k][cc] for cc in alvos[k]])[idx[k]]
        return e

    for it in range(iter_max):
        maior = 0.0
        for k in alvos:
            p = expit(eta())
            for j, cc in enumerate(alvos[k]):
                m = idx[k] == j
                atual = np.average(p[m], weights=w[m])
                passo = float(logit(alvos[k][cc]) - logit(atual))
                efeitos[k][cc] += passo
                maior = max(maior, abs(passo))
        if maior < tol:
            break
    p = expit(eta())
    # identificação: centra idade/escolaridade/gênero (média ponderada pelos aptos = 0)
    # e passa a constante para a região (não muda p)
    for k in ("genero", "idade", "escolaridade"):
        if k in efeitos:
            v = np.array([efeitos[k][cc] for cc in alvos[k]])
            m = float(np.sum(comp[k] * v))
            efeitos[k] = {cc: float(x - m) for cc, x in zip(alvos[k], v)}
            efeitos["regiao"] = {cc: float(x + m) for cc, x in efeitos["regiao"].items()}
    return {"efeitos": efeitos, "p": p, "iteracoes": it + 1, "convergiu": maior < tol,
            "desvio_uf": desvio, "alvos_coerentes": alvos, "total_implicito": total}


def _agregar_por_uf(celulas: pd.DataFrame, p: np.ndarray, pesos_comp: np.ndarray | None = None) -> pd.DataFrame:
    c = celulas
    wa = c["aptos"].values.astype(float)
    wc = wa * (c["comp_taxa"].values if pesos_comp is None else pesos_comp)
    g = pd.DataFrame({"uf": c["uf"].values, "wa": wa, "wc": wc, "pa": wa * p, "pc": wc * p})
    s = g.groupby("uf")[["wa", "wc", "pa", "pc"]].sum()
    out = pd.DataFrame({"p_aptos": s.pa / s.wa, "p_votantes": s.pc / s.wc, "comparecimento": s.wc / s.wa})
    tot = s.sum()
    out.loc["BR"] = [tot.pa / tot.wa, tot.pc / tot.wc, tot.wc / tot.wa]
    return out


def _perturbar_alvos(fonte: dict, rng: np.random.Generator, deff: float = 1.5, nao_amostral_pp: float = 1.0) -> dict:
    """Sorteia margens com erro amostral (n do segmento, efeito de desenho) + erro não amostral."""
    n = fonte["n"] * fonte.get("fracao_dois_primeiros", 1.0)
    out = {}
    for k, m in fonte["margens"].items():
        out[k] = {}
        for cc, (v, peso) in m.items():
            p = v / 100
            nk = max(n * peso / 100, 30)
            sd = math.sqrt(deff * p * (1 - p) / nk + (nao_amostral_pp / 100) ** 2)
            out[k][cc] = float(np.clip(p + rng.normal(0, sd), 0.02, 0.98))
    return out


def ajuste_comparecimento(celulas: pd.DataFrame, fontes: list[dict], lean_uf: pd.Series | None = None,
                          n_sorteios: int = 200, semente: int = 2026,
                          kappa_intervalo: tuple[float, float] = (0.7, 1.0),
                          dp_logito_comparecimento: float = 0.10) -> pd.DataFrame:
    """Ajuste de comparecimento por UF (p.p. da fatia de Lula e logito), com incerteza.

    Para cada sorteio:
      1. escolhe uma fonte de voto por segmento (uniforme entre ``fontes``) e
         perturba as margens publicadas (erro amostral + 1 p.p. não amostral);
      2. ajusta o modelo por célula (``ajustar_modelo_voto``);
      3. perturba o comparecimento por célula: (i) fator κ ~ U(kappa_intervalo)
         que encolhe o desvio da abstenção da célula em relação à média da UF
         (inferência: parte da abstenção altíssima de 80+ e analfabetos é de
         eleitores falecidos/mudados ainda no cadastro, que as pesquisas nunca
         entrevistam); (ii) ruído no logito do comparecimento por
         faixa × escolaridade (dp ``dp_logito_comparecimento``, mudança 2022->2026);
      4. ajuste = p(votantes) − p(aptos) na UF.

    Devolve DataFrame por UF (+ 'BR'): ajuste médio e dp, em p.p. e em logito,
    e o ajuste central (fonte(s) sem perturbação, κ = 1).
    """
    rng = np.random.default_rng(semente)
    c = celulas
    comp = c["comp_taxa"].values
    uf_comp = c.groupby("uf").apply(lambda g: np.average(g.comp_taxa, weights=g.aptos), include_groups=False)
    base_uf = c["uf"].map(uf_comp).values
    grupo = (c["faixa_etaria"] + "|" + c["escolaridade"]).values
    grupos = np.unique(grupo)
    gi = np.searchsorted(grupos, grupo)

    # central
    centrais = []
    for f in fontes:
        mv = ajustar_modelo_voto(c, f, lean_uf)
        centrais.append(_agregar_por_uf(c, mv["p"]))
    central = sum(centrais) / len(centrais)

    res = []
    for s in range(n_sorteios):
        f = fontes[rng.integers(len(fontes))]
        mv = ajustar_modelo_voto(c, f, lean_uf, alvos=_perturbar_alvos(f, rng), iter_max=60, tol=1e-5)
        kappa = rng.uniform(*kappa_intervalo)
        lc = logit(base_uf) + kappa * (logit(comp) - logit(base_uf)) + rng.normal(0, dp_logito_comparecimento, len(grupos))[gi]
        a = _agregar_por_uf(c, mv["p"], expit(lc))
        res.append(a)
    aj_pp = np.stack([(r.p_votantes - r.p_aptos).values for r in res]) * 100
    aj_lg = np.stack([(logit(r.p_votantes.values) - logit(r.p_aptos.values)) for r in res])
    idx = res[0].index
    out = pd.DataFrame({
        "uf": idx,
        "p_aptos_central": central.p_aptos.values,
        "p_votantes_central": central.p_votantes.values,
        "ajuste_central_pp": (central.p_votantes - central.p_aptos).values * 100,
        "ajuste_pp": aj_pp.mean(0), "dp_ajuste_pp": aj_pp.std(0),
        "ajuste_logito": aj_lg.mean(0), "dp_ajuste_logito": aj_lg.std(0),
        "ajuste_p05_pp": np.percentile(aj_pp, 5, axis=0), "ajuste_p95_pp": np.percentile(aj_pp, 95, axis=0),
        "comparecimento_celulas": central.comparecimento.values,
    })
    return out


def projetar_celulas_2026(celulas: pd.DataFrame, cov: pd.DataFrame | None = None, iter_max: int = 100) -> pd.DataFrame:
    """Reajusta (raking) os aptos das células de 2022 às margens do eleitorado de 2026 por UF.

    Margens por UF (perfil_eleitorado_2026, ``covariaveis_uf.csv``): total de
    eleitores; faixas 16-17 / 18-59 / 60-69 / 70+; escolaridade analfabeto+lê e
    escreve / fundamental incompleto / demais; % mulheres. A taxa de
    comparecimento de cada célula continua a de 2022 (hipótese: o
    comparecimento por perfil se repete; a incerteza entra no sorteio).
    """
    cov = cov if cov is not None else pd.read_csv(DADOS / "covariaveis_uf.csv").set_index("uf")
    out = []
    idade_g = celulas["faixa_etaria"].map({"16-17": "16-17", "60-69": "60-69", "70-79": "70+", "80+": "70+"}).fillna("18-59")
    escol_g = celulas["escolaridade"].map({"analf_le": "analf_le", "fund_inc": "fund_inc"}).fillna("demais")
    for uf, g in celulas.groupby("uf"):
        r = cov.loc[uf]
        alvo_idade = {"16-17": r.pct_16_17_tse2026, "60-69": r.pct_60mais_tse2026 - r.pct_70mais_tse2026,
                      "70+": r.pct_70mais_tse2026}
        alvo_idade["18-59"] = 100 - sum(alvo_idade.values())
        alvo_escol = {"analf_le": r.pct_analf_le_tse2026, "fund_inc": r.pct_ate_fund_inc_tse2026 - r.pct_analf_le_tse2026}
        alvo_escol["demais"] = 100 - sum(alvo_escol.values())
        alvo_gen = {"F": r.pct_fem_tse2026, "M": 100 - r.pct_fem_tse2026}
        w = g["aptos"].values.astype(float).copy()
        dims = [(idade_g.loc[g.index].values, alvo_idade), (escol_g.loc[g.index].values, alvo_escol),
                (g["genero"].values, alvo_gen)]
        for _ in range(iter_max):
            for lab, alvo in dims:
                tot = w.sum()
                for k, v in alvo.items():
                    m = lab == k
                    s = w[m].sum()
                    if s > 0:
                        w[m] *= (v / 100 * tot) / s
        w *= r.eleitores_2026_tse / w.sum()
        gg = g.copy()
        gg["aptos"] = w
        gg["comparecimento"] = w * gg["comp_taxa"]
        out.append(gg)
    return pd.concat(out).reset_index(drop=True)


#: Pesquisas finais de 2022 (fatia de Lula nos válidos, ou Lula/(Lula+Bolsonaro) no 1º turno)
#: Fonte: research_notes/Briefing eleição presidencial 2026/2022_pesquisas_vs_resultado.md
#: (Wikipedia PT/EN com registros TSE; conversão a válidos [calc] nas notas).
PESQUISAS_FINAIS_2022 = {
    2: {"resultado": 50.90, "pesquisas": {
        "Datafolha": 52.1, "Ipec": 53.8, "Quaest": 51.7, "AtlasIntel": 53.4, "IFP": 50.2, "MDA": 51.1,
        "Paraná Pesquisas": 50.4, "Veritá": 49.0, "Brasmarket": 47.0, "Futura": 49.7, "Gerp": 47.8,
        "PoderData": 52.7, "Ipespe": 53.2, "Ideia": 52.1}},
    1: {"resultado": 52.86, "pesquisas": {  # Lula/(Lula+Bolsonaro) a partir dos VV [calc]
        "Datafolha": 100 * 50.5 / 86.3, "Ipec": 100 * 50.5 / 87.1, "Ipespe": 100 * 49.5 / 85.0,
        "AtlasIntel": 100 * 50.4 / 91.6, "MDA": 100 * 48.3 / 88.0, "Paraná Pesquisas": 100 * 47.2 / 87.3,
        "Veritá": 100 * 42.6 / 88.3, "Brasmarket": 100 * 34.8 / 85.9, "Futura": 100 * 43.6 / 84.1,
        "Ideia": 100 * 48.9 / 87.4, "PoderData": 100 * 48.4 / 87.1, "Quaest": 100 * 50.5 / 86.8}},
}
#: Institutos "tradicionais"/de maior amostra usados no indicador agregado
GRANDES_INSTITUTOS_2022 = ["Datafolha", "Ipec", "Quaest", "AtlasIntel", "PoderData", "Ipespe"]
#: Datafolha véspera do 2º turno de 2022 por região/UF (válidos de Lula) e resultado TSE
DATAFOLHA_2022_2T_REGIOES = {
    "SE": (48, 45.7), "S": (40, 38.2), "NE": (71, 69.3), "CO": (39, 39.8), "N": (48, 49.0),
    "SP": (49, 44.76), "RJ": (43, 43.47), "MG": (53, 50.20),
}


def validar_comparecimento_2022(cel: pd.DataFrame | None = None, n_sorteios: int = 200, semente: int = 22) -> dict:
    """Aplica o ajuste de comparecimento às pesquisas finais de 2022 e compara com o TSE.

    2º turno: gradientes do Datafolha 28-29/10/2022 + comparecimento real do 2º
    turno por célula. 1º turno: mesmos gradientes (não há cruzamentos de 1º turno
    nas notas) + comparecimento do 1º turno. Atenção: o Datafolha 2022 é usado
    para estimar os gradientes por segmento e também é uma das pesquisas
    corrigidas — mas o ajuste depende só dos contrastes entre segmentos e do
    comparecimento, não do nível da pesquisa.
    """
    cel = carregar_abstencao_segmentos() if cel is None else cel
    leans, _ = carregar_leans()
    regioes = pd.read_csv(DADOS / "eleitorado_uf_2026.csv").set_index("uf")["regiao"]
    out = {}
    for turno in (2, 1):
        c = montar_celulas(cel, turno, regioes)
        aj = ajuste_comparecimento(c, [FONTES_VOTO["datafolha_2022_2t"]], leans[(2022, turno)],
                                   n_sorteios=n_sorteios, semente=semente).set_index("uf")
        a_br, sd_br = float(aj.loc["BR", "ajuste_pp"]), float(aj.loc["BR", "dp_ajuste_pp"])
        a_c = float(aj.loc["BR", "ajuste_central_pp"])
        info = PESQUISAS_FINAIS_2022[turno]
        res = info["resultado"]
        linhas = []
        for nome, v in info["pesquisas"].items():
            linhas.append({"instituto": nome, "pesquisa": round(v, 2), "ajustada": round(v + a_c, 2),
                           "erro_antes": round(v - res, 2), "erro_depois": round(v + a_c - res, 2)})
        media = float(np.mean(list(info["pesquisas"].values())))
        grandes = [info["pesquisas"][k] for k in GRANDES_INSTITUTOS_2022 if k in info["pesquisas"]]
        mg = float(np.mean(grandes))
        ea = [abs(l["erro_antes"]) for l in linhas]
        ed = [abs(l["erro_depois"]) for l in linhas]
        out[f"turno_{turno}"] = {
            "ajuste_nacional_central_pp": a_c, "ajuste_nacional_pp": a_br, "dp_ajuste_nacional_pp": sd_br,
            "resultado_tse": res, "media_pesquisas": media, "media_ajustada": media + a_c,
            "erro_medio_antes": media - res, "erro_medio_depois": media + a_c - res,
            "mae_antes": float(np.mean(ea)), "mae_depois": float(np.mean(ed)),
            "erro_medio_grandes_antes": mg - res, "erro_medio_grandes_depois": mg + a_c - res,
            "erro_datafolha_antes": info["pesquisas"]["Datafolha"] - res,
            "erro_datafolha_depois": info["pesquisas"]["Datafolha"] + a_c - res,
            "institutos_que_melhoram": int(sum(d < b for d, b in zip(ed, ea))), "n_institutos": len(linhas),
            "fracao_do_erro_grandes_explicada": float(-a_c / (mg - res)),
            "por_instituto": linhas,
        }
        if turno == 2:
            # por região / UF (Datafolha 2T)
            reg = []
            c2 = c.copy()
            mv = ajustar_modelo_voto(c2, FONTES_VOTO["datafolha_2022_2t"], leans[(2022, 2)])
            c2["p"] = mv["p"]
            for chave, (pesq, real) in DATAFOLHA_2022_2T_REGIOES.items():
                m = (c2.regiao == chave) if chave in ("SE", "S", "NE", "CO", "N") else (c2.uf == chave)
                g = c2[m]
                pa = np.average(g.p, weights=g.aptos)
                pv = np.average(g.p, weights=g.comparecimento)
                aj_r = (pv - pa) * 100
                reg.append({"recorte": chave, "datafolha": pesq, "ajustado": round(pesq + aj_r, 2), "tse": real,
                            "ajuste_pp": round(aj_r, 2), "erro_antes": round(pesq - real, 2),
                            "erro_depois": round(pesq + aj_r - real, 2)})
            out["turno_2"]["datafolha_por_regiao_uf"] = reg
            out["turno_2"]["regioes_uf_que_melhoram"] = int(sum(abs(r["erro_depois"]) < abs(r["erro_antes"]) for r in reg))
    return out


def ajuste_comparecimento_2026(cel: pd.DataFrame | None = None, n_sorteios: int = 400, semente: int = 2026) -> pd.DataFrame:
    """Ajuste de comparecimento por UF para 2026, 1º e 2º turnos.

    Células: 2022 reponderadas ao eleitorado 2026 (``projetar_celulas_2026``),
    comparecimento por célula de 2022 do mesmo turno. Voto por segmento:
    1º turno -> Datafolha 15-17/09/2026 (Lula/(Lula+Flávio));
    2º turno -> mistura (sorteio 50/50) do Datafolha 2026 1º turno e do
    Datafolha 2022 2º turno (não há cruzamentos de 2º turno de 2026 nas notas).
    Desvio da UF dentro da região: lean de 2022 do mesmo turno.
    """
    cel = carregar_abstencao_segmentos() if cel is None else cel
    leans, _ = carregar_leans()
    regioes = pd.read_csv(DADOS / "eleitorado_uf_2026.csv").set_index("uf")["regiao"]
    partes = []
    for turno, fontes in ((1, ["datafolha_2026_1t"]), (2, ["datafolha_2026_1t", "datafolha_2022_2t"])):
        c = projetar_celulas_2026(montar_celulas(cel, turno, regioes))
        aj = ajuste_comparecimento(c, [FONTES_VOTO[f] for f in fontes], leans[(2022, turno)],
                                   n_sorteios=n_sorteios, semente=semente + turno)
        aj.insert(1, "turno", turno)
        aj.insert(2, "fontes_voto", "+".join(fontes))
        partes.append(aj)
    df = pd.concat(partes, ignore_index=True)
    df["nota"] = ("ajuste = fatia de Lula entre votantes - fatia entre aptos (populacao das pesquisas); "
                  "somar em logito a media por UF (ajuste_logito) antes da calibracao nacional")
    return df


# ============================================================== (c) decomposição por segmento (exibição)
_F22 = "https://static.poder360.com.br/2022/12/datafolha-BR-082972022-1.pdf"
_F26 = ("https://ncnews.com.br/2026/09/18/datafolha-revela-onde-lula-e-flavio-bolsonaro-concentram-forca-"
        "veja-os-recortes-por-idade-renda-religiao-e-regiao/")
_FQ26 = "https://www.em.com.br/politica/2026/09/7509823-quaest-lula-avanca-entre-catolicos-e-evangelicos-apos-polemica.html"
_FA26 = "https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/atlasintel-presidente-setembro-2026-4/"
_FTSE26 = "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip"
_FCENSO_REL = "https://apisidra.ibge.gov.br/values/t/9537/n1/all/v/1000140/p/2022/c133/95263,95277,2836/c2/6794/c58/95253"
_FMDS = ("https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&wt=json&fq=anomes_s:202609&rows=6000"
         "&fl=sigla_uf,qtd_familias_beneficiarias_bolsa_familia,valor_repassado_bolsa_familia_f")
_FAUX22 = ("https://www.terra.com.br/noticias/brasil/politica/datafolha-lula-tem-57-contra-26-de-bolsonaro-entre-quem-"
           "recebe-auxilio,637a7ccd640613cb7f3f190b32ab687fsuh932g0.html")

#: Tabela-base da decomposição. Cada categoria: tamanho (% e fonte), voto 2022
#: (Datafolha 28-29/10/2022, válidos do 2º turno, Lula x Bolsonaro), voto 2026
#: (Datafolha 15-17/09/2026, 1º turno, % de votos totais, Lula x Flávio) e outras leituras.
SEGMENTOS_BASE = [
    ("genero", "Gênero", [
        ("Mulheres", 52.84, "TSE 2026", (55, 45), (41, 32), [("AtlasIntel 23-28/09/2026, 1º turno", 57.4, 32.9, _FA26)]),
        ("Homens", 47.15, "TSE 2026", (50, 50), (37, 39), [("AtlasIntel 23-28/09/2026, 1º turno (só Flávio publicado)", None, 52.4, _FA26)]),
    ]),
    ("idade", "Idade", [
        ("16-24", 12.11, "TSE 2026", (57, 43), (39, 29), []),
        ("25-34", 19.00, "TSE 2026", (51, 49), (37, 39), []),
        ("35-44", 19.69, "TSE 2026", (50, 50), (41, 35), []),
        ("45-59", 25.60, "TSE 2026", (53, 47), (35, 39), []),
        ("60+", 23.60, "TSE 2026", (52, 48), (43, 33), []),
    ]),
    ("escolaridade", "Escolaridade", [
        ("Fundamental", 36.84, "TSE 2026 (cadastro: analfabeto a fundamental completo; amostra Datafolha 2022: 28%)", (61, 39), (47, 30), []),
        ("Médio", 46.10, "TSE 2026 (cadastro: médio incompleto e completo; amostra Datafolha 2022: 46%)", (49, 51), (36, 38), []),
        ("Superior", 17.05, "TSE 2026 (cadastro: superior incompleto e completo; amostra Datafolha 2022: 26%)", (49, 51), (36, 37), []),
    ]),
    ("renda", "Renda familiar mensal", [
        ("Até 2 SM", 46.0, "amostra Datafolha 2022 (renda familiar)", (61, 39), (46, 29), []),
        ("2 a 5 SM", 36.0, "amostra Datafolha 2022", (45, 55), (33, 41), []),
        ("Mais de 5 SM", 15.0, "amostra Datafolha 2022 (5-10 SM 11% + 10+ SM 4%)", (41, 59), (28, 44), []),
    ]),
    ("religiao", "Religião", [
        ("Católicos", 56.75, "Censo 2022 (10 anos ou mais)", (59, 41), (43, 32),
         [("Quaest 24-27/09/2026, 1º turno", 48, 29, _FQ26), ("Quaest 24-27/09/2026, 2º turno", 50, 37, _FQ26)]),
        ("Evangélicos", 26.85, "Censo 2022 (10 anos ou mais)", (31, 69), (26, 48),
         [("Quaest 24-27/09/2026, 1º turno", 27, 46, _FQ26), ("Quaest 24-27/09/2026, 2º turno", 30, 54, _FQ26),
          ("AtlasIntel 23-28/09/2026, 1º turno", 20.8, 62.7, _FA26)]),
        ("Sem religião", 9.28, "Censo 2022 (10 anos ou mais)", None, None, []),
    ]),
    ("regiao", "Região", [
        ("Sudeste", 41.78, "TSE 2026", (48, 52), (34, 37), []),
        ("Nordeste", 27.42, "TSE 2026", (71, 29), (56, 26), []),
        ("Sul", 14.40, "TSE 2026", (40, 60), (27, 45), []),
        ("Norte", 8.26, "TSE 2026", (48, 52), None, []),
        ("Centro-Oeste", 7.56, "TSE 2026", (39, 61), None, []),
        ("Centro-Oeste + Norte", 15.82, "TSE 2026", None, (35, 41), []),
    ]),
    ("bolsa_familia", "Bolsa Família", [
        ("Beneficiários", 23.0, "amostra Datafolha 2022 (recebia Auxílio Brasil); MDS set/2026: 19,3 mi de famílias = 12,2 por 100 eleitores", None, (53, 28),
         [("Datafolha 2022, quem recebia Auxílio Brasil (votos totais, 2º turno)", 57, 26, _FAUX22)]),
        ("Não beneficiários", 77.0, "complemento", None, (36, 37), []),
    ]),
]
_ABST_MAP = {
    "genero": ("genero", {"Mulheres": ["F"], "Homens": ["M"]}),
    "idade": ("faixa_etaria", {"16-24": ["16-17", "18-24"], "25-34": ["25-34"], "35-44": ["35-44"],
                               "45-59": ["45-59"], "60+": ["60-69", "70-79", "80+"]}),
    "escolaridade": ("escolaridade", {"Fundamental": ["analf_le", "fund_inc", "fund_comp_medio_inc"],
                                      "Médio": ["medio_comp"], "Superior": ["superior"]}),
}


def decomposicao_segmentos(cel: pd.DataFrame | None = None) -> dict:
    """Estrutura pronta para JSON com o voto por segmento (2022 x 2026) e o tamanho de cada segmento.

    Para cada categoria: ``tamanho_pct`` e fonte; ``voto_2022_2t`` (válidos,
    Lula x Bolsonaro, margem); ``voto_2026_1t`` (votos totais, Lula x Flávio,
    margem e fatia Lula/(Lula+Flávio)); ``outras_2026``; e, para gênero,
    idade e escolaridade, ``abstencao_2022_1t_pct``/``2t`` (TSE).
    Nota: na escolaridade, "Médio" da abstenção usa só médio completo e
    "Fundamental" inclui médio incompleto (agrupamentos do cadastro TSE).
    """
    cel = carregar_abstencao_segmentos() if cel is None else cel
    dims = []
    for chave, rotulo, cats in SEGMENTOS_BASE:
        lista = []
        for nome, tam, ftam, v22, v26, outras in cats:
            item = {"categoria": nome, "tamanho_pct": tam, "fonte_tamanho": ftam}
            if v22:
                item["voto_2022_2t"] = {"lula": v22[0], "bolsonaro": v22[1], "margem_lula": v22[0] - v22[1]}
            if v26:
                item["voto_2026_1t"] = {"lula": v26[0], "flavio": v26[1], "margem_lula": v26[0] - v26[1],
                                        "fatia_lula_2p": round(100 * v26[0] / (v26[0] + v26[1]), 1)}
            if outras:
                item["outras_2026"] = [{"pesquisa": o[0], "lula": o[1], "adversario": o[2], "fonte_url": o[3]}
                                       for o in outras]
            if chave in _ABST_MAP:
                col, mapa = _ABST_MAP[chave]
                for t in (1, 2):
                    d = cel[(cel.turno == t) & cel[col].isin(mapa[nome])]
                    item[f"abstencao_2022_{t}t_pct"] = round(100 * d.abstencao.sum() / d.aptos.sum(), 1)
            lista.append(item)
        dims.append({"dimensao": chave, "rotulo": rotulo, "categorias": lista})
    tot = cel[cel.turno == 1]
    return {
        "titulo": "Voto por segmento: 2022 (2º turno) x 2026 (1º turno)",
        "data_referencia": "2026-10-03",
        "totais": {
            "voto_2022_2t": {"lula": 52, "bolsonaro": 48, "resultado_tse_lula": 50.90},
            "voto_2026_1t": {"lula": 39, "flavio": 36, "fatia_lula_2p": round(100 * 39 / 75, 1)},
            "abstencao_2022_1t_pct": round(100 * tot.abstencao.sum() / tot.aptos.sum(), 2),
        },
        "fontes": {
            "datafolha_2022_2t": {"descricao": FONTES_VOTO["datafolha_2022_2t"]["descricao"], "url": _F22},
            "datafolha_2026_1t": {"descricao": FONTES_VOTO["datafolha_2026_1t"]["descricao"], "url": _F26},
            "tse_eleitorado_2026": _FTSE26, "censo_2022_religiao": _FCENSO_REL, "mds_bolsa_familia_set2026": _FMDS,
            "tse_comparecimento_2022": URL_PERFIL_COMPARECIMENTO_2022,
        },
        "avisos": [
            "2022 é 2º turno em votos válidos; 2026 é 1º turno em votos totais (com ~25% em outros e brancos/nulos/indecisos): compare ordem e sinal das margens, não o tamanho.",
            "Margem de erro dos segmentos é maior que a do total (Datafolha 2026: n = 2.002; subgrupos de 250-1.000 entrevistas).",
            "Evangélicos e gênero variam muito entre institutos (presencial x online).",
            "Tamanhos: TSE 2026 para gênero/idade/escolaridade/região (escolaridade do cadastro é desatualizada e mais baixa que a das pesquisas); Censo 2022 para religião; renda e Bolsa Família = amostra Datafolha 2022.",
        ],
        "dimensoes": dims,
    }


# ============================================================== geração dos arquivos
def gerar_arquivos(destino: Path | str = DADOS, n_sorteios: int = 400) -> dict:
    """Gera os arquivos de saída em ``data/`` e devolve um resumo da validação.

    prior_demografico_uf.csv, ajuste_comparecimento_uf.csv, segmentos_voto.json.
    (abstencao_segmentos_uf.csv vem de ``agregar_perfil_comparecimento``.)
    """
    destino = Path(destino)
    X = carregar_covariaveis()
    leans, nac = carregar_leans()
    vals, priores = {}, []
    for turno in (1, 2):
        v = validar_prior_demografico(turno, X, leans, nac)
        vals[turno] = v
        priores.append(prior_demografico_uf(turno, v, X, leans, nac))
    pri = pd.concat(priores, ignore_index=True)
    pri = pri.merge(X.reset_index().rename(columns={"index": "uf"}), on="uf")
    pri["fonte"] = ("TSE resultados 2014-2022 (data/resultados_uf_2002_2022.csv); covariaveis: data/covariaveis_uf.csv; "
                    "metodo: segmentos.prior_demografico_uf")
    num = pri.select_dtypes("number").columns
    pri[num] = pri[num].round(5)
    pri.to_csv(destino / "prior_demografico_uf.csv", index=False)

    aj = ajuste_comparecimento_2026(n_sorteios=n_sorteios)
    num = aj.select_dtypes("number").columns
    aj[num] = aj[num].round(5)
    aj.to_csv(destino / "ajuste_comparecimento_uf.csv", index=False)

    seg = decomposicao_segmentos()
    val22 = validar_comparecimento_2022(n_sorteios=max(100, n_sorteios // 2))
    seg["ajuste_comparecimento_nacional_2026"] = {
        f"turno_{t}": {k: round(float(aj[(aj.uf == "BR") & (aj.turno == t)][k].iloc[0]), 3)
                       for k in ("ajuste_central_pp", "ajuste_pp", "dp_ajuste_pp")} for t in (1, 2)}
    (destino / "segmentos_voto.json").write_text(json.dumps(seg, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"validacao_prior": vals, "validacao_comparecimento_2022": val22}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].endswith(".zip"):
        agregar_perfil_comparecimento(sys.argv[1])
    r = gerar_arquivos()
    for t, v in r["validacao_prior"].items():
        print(f"turno {t}: " + ", ".join(f"{k}={v[k]:.2f}" for k in v if isinstance(v[k], float)))
    for t, v in r["validacao_comparecimento_2022"].items():
        print(t, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()
                  if k not in ("por_instituto", "datafolha_por_regiao_uf")})
