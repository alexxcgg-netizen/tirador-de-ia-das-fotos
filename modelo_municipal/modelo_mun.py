"""Modelo municipal do 2º turno: estrutura do 1º turno -> 2º turno, município a município.

Nada de pesquisas nem de mercados: a única entrada de 2026 é o resultado do 1º turno por município.

Notação (por município i, tudo como fração do eleitorado apto do 1º turno):
  x = (PT1, OPP1, TERC1, BN1, ABS1)  -- PT, principal adversário, terceiros, brancos+nulos, abstenção; soma 1
  y_pt = PT2 / aptos,   y_opp = OPP2 / aptos

Dois modelos:

* ``EI`` (inferência ecológica de Goodman com restrições): y_k = x · beta_k, beta_k em [0, 1]^5
  (beta_k[j] = fração dos eleitores da categoria j que vota em k no 2º turno). Estimado por mínimos quadrados
  ponderados pelo eleitorado, em hierarquia nacional -> grupo (UF, ou porte, ...) com encolhimento (ridge)
  do grupo para o nível de cima. Dá a fatia do PT e o comparecimento/válidos do 2º turno.

* ``LOGIT`` (regressão de swing): logito da fatia do PT nos válidos do 2º turno sobre o logito da fatia
  bipartidária do 1º turno, peso dos terceiros, brancos/nulos, abstenção, porte e (opcional) efeitos de UF.
  Os válidos do 2º turno vêm de uma regressão linear de válidos2/aptos sobre o mesmo conjunto.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
CATS = ["x_pt", "x_opp", "x_terc", "x_bn", "x_abs"]
# variante com os terceiros separados em esquerda/centro-esquerda e não-esquerda (centro, centro-direita, direita)
CATS6 = ["x_pt", "x_opp", "x_terc_esq", "x_terc_nesq", "x_bn", "x_abs"]
# 2026: números dos candidatos de esquerda no 1º turno (PSTU, PCB, PCO, UP). Os demais terceiros (Caiado/PSD,
# Augusto Cury/Avante, Renan Santos/Missão, Zema/Novo, DC, PMB) formam o bloco não-esquerda.
ESQUERDA_2026 = {16, 21, 29, 80}
REGIAO = {
    "AC": "N", "AM": "N", "AP": "N", "PA": "N", "RO": "N", "RR": "N", "TO": "N",
    "AL": "NE", "BA": "NE", "CE": "NE", "MA": "NE", "PB": "NE", "PE": "NE", "PI": "NE", "RN": "NE", "SE": "NE",
    "DF": "CO", "GO": "CO", "MS": "CO", "MT": "CO",
    "ES": "SE", "MG": "SE", "RJ": "SE", "SP": "SE",
    "PR": "S", "RS": "S", "SC": "S",
    "ZZ": "EX",
}


# ------------------------------------------------------------------ dados
def _completar(d: pd.DataFrame) -> pd.DataFrame:
    """Recebe aptos, comparecimento, brancos, nulos, pt1, opp1, terc1 (e opcionalmente pt2, opp2, validos2, comp2)
    e acrescenta as frações x_*, y_*, covariáveis e chaves de grupo."""
    d = d[d.aptos > 0].copy()
    a = d.aptos.astype(float)
    d["x_pt"] = d.pt1 / a
    d["x_opp"] = d.opp1 / a
    d["x_terc"] = d.terc1 / a
    d["x_bn"] = (d.brancos + d.nulos) / a
    d["x_abs"] = (a - d.comparecimento).clip(lower=0) / a
    s = d[CATS].sum(axis=1)
    d[CATS] = d[CATS].div(s, axis=0)  # pequenas inconsistências (votos anulados sub judice etc.)
    if "terc_esq" in d:
        d["x_terc_esq"] = (d.terc_esq / a) / s
        d["x_terc_nesq"] = (d.x_terc - d.x_terc_esq).clip(lower=0)
    d["regiao"] = d.uf.map(REGIAO).fillna("EX")
    d["log_aptos"] = np.log(a.clip(lower=1))
    d["porte"] = pd.cut(a, [-1, 10_000, 50_000, 200_000, np.inf], labels=["p1", "p2", "p3", "p4"]).astype(str)
    d["uf_porte"] = d.uf + "_" + d.porte
    if "pt2" in d:
        d["y_pt"] = d.pt2 / a
        d["y_opp"] = d.opp2 / a
    return d.reset_index(drop=True)


def carregar_historico(ano: int, pasta: Path = DADOS) -> pd.DataFrame:
    h = pd.read_csv(pasta / f"hist_{ano}.csv")
    d = pd.DataFrame({
        "cd_municipio_tse": h.cd_municipio_tse, "uf": h.uf, "municipio": h.municipio,
        "aptos": h.t1_aptos, "comparecimento": h.t1_comparecimento, "brancos": h.t1_brancos, "nulos": h.t1_nulos,
        "pt1": h.t1_pt, "opp1": h.t1_opp, "terc1": h.t1_terceiros, "terc_esq": h.t1_terc_esq,
        "pt2": h.t2_pt, "opp2": h.t2_opp, "comp2": h.t2_comparecimento,
    })
    d = d[(h.t2_aptos > 0) & (h.t2_pt + h.t2_opp > 0)]
    out = _completar(d)
    out["ano"] = ano
    return out


def carregar_2026(pasta: Path = DADOS) -> pd.DataFrame:
    m = pd.read_csv(pasta / "mun_2026_1t.csv")
    # municípios ainda não 100% totalizados (pst < 100: ~60 municípios, ~1% do eleitorado): extrapola as contagens
    # das seções totalizadas para o município inteiro, senão a abstenção sairia inflada
    fator = 100 / m.pst.clip(lower=1).where(m.pst > 0, 100) if "pst" in m else 1.0
    cand = [c for c in m.columns if c.startswith("c") and c[1:].isdigit()]
    for c in ["comparecimento", "brancos", "nulos", "lula", "flavio", "terceiros", *cand]:
        if c in m:
            m[c] = m[c] * fator
    m["comparecimento"] = np.minimum(m.comparecimento, m.aptos)
    d = pd.DataFrame({
        "cd_municipio_tse": m.cd_municipio_tse, "uf": m.uf, "aptos": m.aptos, "comparecimento": m.comparecimento,
        "brancos": m.brancos, "nulos": m.nulos, "pt1": m.lula, "opp1": m.flavio, "terc1": m.terceiros,
        "terc_esq": m[[f"c{n}" for n in ESQUERDA_2026 if f"c{n}" in m]].sum(axis=1),
    })
    out = _completar(d)
    out["ano"] = 2026
    return out


# ------------------------------------------------------------------ modelo EI (Goodman restrito, hierárquico)
def _lsq(X, y, w, prior=None, lam=0.0):
    """min sum w (y - X b)^2 + lam * |b - prior|^2,  0 <= b <= 1."""
    sw = np.sqrt(w)
    A, b = X * sw[:, None], y * sw
    if prior is not None and lam > 0:
        A = np.vstack([A, np.sqrt(lam) * np.eye(X.shape[1])])
        b = np.concatenate([b, np.sqrt(lam) * prior])
    return lsq_linear(A, b, bounds=(0.0, 1.0), method="bvls").x


@dataclass
class ModeloEI:
    """niveis: chaves de grupo, do mais grosso ao mais fino (ex.: ["regiao", "uf"]); lam: pseudo-número de
    municípios médios que puxa cada grupo para o seu nível de cima."""
    niveis: list = field(default_factory=lambda: ["uf"])
    lam: float = 30.0
    cats: list = field(default_factory=lambda: list(CATS))
    coefs: dict = field(default_factory=dict)  # (nivel, grupo) -> {"pt": beta, "opp": beta}

    def ajustar(self, d: pd.DataFrame) -> "ModeloEI":
        d = d.reset_index(drop=True)
        X = d[self.cats].to_numpy(float)
        w = d.aptos.to_numpy(float)
        w = w / w.mean()
        self.coefs = {("nac", "nac"): {k: _lsq(X, d[f"y_{k}"].to_numpy(float), w) for k in ("pt", "opp")}}
        pai = pd.Series([("nac", "nac")] * len(d))
        for nv in self.niveis:
            g = d[nv].to_numpy()
            novo = []
            for grp in pd.unique(g):
                idx = np.where(g == grp)[0]
                p = self.coefs[pai.iloc[idx[0]]]
                self.coefs[(nv, grp)] = {k: _lsq(X[idx], d[f"y_{k}"].to_numpy(float)[idx], w[idx], p[k], self.lam)
                                         for k in ("pt", "opp")}
            pai = pd.Series([(nv, gg) for gg in g])
        return self

    def _beta(self, linha) -> dict:
        for nv in reversed(self.niveis):
            c = self.coefs.get((nv, linha[nv]))
            if c is not None:
                return c
        return self.coefs[("nac", "nac")]

    def prever(self, d: pd.DataFrame) -> pd.DataFrame:
        X = d[self.cats].to_numpy(float)
        Bpt = np.zeros_like(X)
        Bop = np.zeros_like(X)
        chaves = d[self.niveis].to_numpy() if self.niveis else np.empty((len(d), 0))
        cache = {}
        for i in range(len(d)):
            key = tuple(chaves[i])
            if key not in cache:
                cache[key] = self._beta(dict(zip(self.niveis, key)))
            Bpt[i], Bop[i] = cache[key]["pt"], cache[key]["opp"]
        return _saida(d, (X * Bpt).sum(1), (X * Bop).sum(1))


def _saida(d, ypt, yopp) -> pd.DataFrame:
    a = d.aptos.to_numpy(float)
    out = pd.DataFrame({"cd_municipio_tse": d.cd_municipio_tse.to_numpy(), "uf": d.uf.to_numpy(),
                        "regiao": d.regiao.to_numpy(), "aptos": a})
    out["pt2_prev"] = ypt * a
    out["opp2_prev"] = yopp * a
    out["validos2_prev"] = out.pt2_prev + out.opp2_prev
    out["fatia_pt_prev"] = out.pt2_prev / out.validos2_prev.clip(lower=1e-9)
    return out


# ------------------------------------------------------------------ modelo LOGIT (swing)
def _lg(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def _matriz_logit(d: pd.DataFrame, ufs: list | None, efeito: str | None):
    z1 = _lg((d.x_pt / (d.x_pt + d.x_opp)).fillna(0.5))
    comp = (1 - d.x_abs).clip(lower=1e-6)
    terc = d.x_terc / comp
    cols = [np.ones(len(d)), z1, terc, terc * z1, d.x_bn / comp, d.x_abs, d.log_aptos - 9.5]
    if efeito:
        for u in ufs[1:]:
            cols.append((d[efeito] == u).to_numpy(float))
    return np.column_stack(cols)


@dataclass
class ModeloLogit:
    efeito: str | None = "uf"  # None, "regiao" ou "uf"
    ridge: float = 1e-3
    b_share: np.ndarray | None = None
    b_val: np.ndarray | None = None
    grupos: list | None = None

    def ajustar(self, d: pd.DataFrame) -> "ModeloLogit":
        self.grupos = sorted(d[self.efeito].unique()) if self.efeito else None
        X = _matriz_logit(d, self.grupos, self.efeito)
        v2 = d.y_pt + d.y_opp
        w = (v2 * d.aptos).to_numpy(float)
        w = w / w.mean()
        y = _lg((d.y_pt / v2).fillna(0.5))
        R = self.ridge * np.eye(X.shape[1])
        R[0, 0] = 0
        Xw = X * w[:, None]
        self.b_share = np.linalg.solve(Xw.T @ X + R * w.sum(), Xw.T @ y)
        wa = d.aptos.to_numpy(float) / d.aptos.mean()
        Xa = X * wa[:, None]
        self.b_val = np.linalg.solve(Xa.T @ X + R * wa.sum(), Xa.T @ v2.to_numpy(float))
        return self

    def prever(self, d: pd.DataFrame) -> pd.DataFrame:
        X = _matriz_logit(d, self.grupos, self.efeito)
        if self.efeito:  # grupos ausentes no treino -> efeito zero (já é o caso: coluna inexistente)
            pass
        s = 1 / (1 + np.exp(-(X @ self.b_share)))
        v2 = np.clip(X @ self.b_val, 0.05, 1.0)
        return _saida(d, s * v2, (1 - s) * v2)


# ------------------------------------------------------------------ agregação e avaliação
def agregar(prev: pd.DataFrame, por: str | None = None) -> pd.DataFrame:
    g = prev.groupby(por) if por else prev.assign(_n="BR").groupby("_n")
    s = g[["pt2_prev", "opp2_prev", "validos2_prev", "aptos"]].sum()
    s["fatia_pt_prev"] = s.pt2_prev / s.validos2_prev
    return s


def avaliar(prev: pd.DataFrame, real: pd.DataFrame) -> dict:
    """Erros (previsto - real) da fatia do PT nos válidos (p.p.) e dos válidos (%) no país, por UF e por município."""
    r = real[["cd_municipio_tse", "uf", "y_pt", "y_opp", "aptos"]].copy()
    r["pt2"] = r.y_pt * r.aptos
    r["v2"] = (r.y_pt + r.y_opp) * r.aptos
    m = prev.merge(r[["cd_municipio_tse", "uf", "pt2", "v2"]], on=["cd_municipio_tse", "uf"])
    m["e_mun"] = 100 * (m.fatia_pt_prev - m.pt2 / m.v2)
    nat_p = m.pt2_prev.sum() / m.validos2_prev.sum()
    nat_r = m.pt2.sum() / m.v2.sum()
    e_nat = 100 * (nat_p - nat_r)
    uf = m.groupby("uf")[["pt2_prev", "validos2_prev", "pt2", "v2"]].sum()
    uf["e"] = 100 * (uf.pt2_prev / uf.validos2_prev - uf.pt2 / uf.v2)
    uf["reg"] = uf.index.map(REGIAO)
    reg = m.groupby("regiao")[["pt2_prev", "validos2_prev", "pt2", "v2"]].sum()
    reg["e"] = 100 * (reg.pt2_prev / reg.validos2_prev - reg.pt2 / reg.v2)
    ufb = uf.drop(index="ZZ", errors="ignore")
    wv = ufb.v2 / ufb.v2.sum()
    # componentes: regional = erro da região menos o nacional; UF = erro da UF menos o da sua região;
    # municipal = erro do município menos o da sua UF (ponderado pelos válidos)
    regb = reg.drop(index="EX", errors="ignore")
    wr = regb.v2 / regb.v2.sum()
    e_reg_dev = regb.e - e_nat
    e_uf_dev = ufb.e - ufb.reg.map(reg.e)
    m["e_mun_dev"] = m.e_mun - m.uf.map(uf.e)
    wm = m.v2 / m.v2.sum()
    return {
        "erro_nacional_pp": float(e_nat),
        "fatia_prev_pct": float(100 * nat_p), "fatia_real_pct": float(100 * nat_r),
        "erro_validos_pct": float(100 * (m.validos2_prev.sum() / m.v2.sum() - 1)),
        "validos_prev_mi": float(m.validos2_prev.sum() / 1e6), "validos_real_mi": float(m.v2.sum() / 1e6),
        "rmse_uf_pp": float(np.sqrt(np.sum(wv * ufb.e ** 2))),
        "mae_uf_pp": float(np.mean(np.abs(ufb.e))),
        "rmse_uf_sem_nacional_pp": float(np.sqrt(np.sum(wv * (ufb.e - e_nat) ** 2))),
        "dp_regiao_pp": float(np.sqrt(np.sum(wr * e_reg_dev ** 2))),
        "dp_uf_na_regiao_pp": float(np.sqrt(np.sum(wv * e_uf_dev ** 2))),
        "rmse_mun_pp": float(np.sqrt(np.sum(wm * m.e_mun ** 2))),
        "mae_mun_pp": float(np.mean(np.abs(m.e_mun))),
        "dp_mun_na_uf_pp": float(np.sqrt(np.sum(wm * m.e_mun_dev ** 2))),
        "dp_mun_na_uf_pp_sem_peso": float(np.sqrt(np.mean(m.e_mun_dev ** 2))),
        "n_municipios": int(len(m)),
        "erros_uf_pp": {k: round(float(v), 2) for k, v in uf.e.items()},
    }


# ------------------------------------------------------------------ simulação
def simular(prev: pd.DataFrame, dp_nac: float, dp_reg: float, dp_uf: float, dp_mun: float,
            n: int = 500_000, semente: int = 2026, lote: int = 100_000) -> dict:
    """Simula a fatia de Lula nos válidos (em p.p.) somando erros nacional, regional (região), de UF e municipal.

    O erro municipal (independente entre municípios, dp_mun p.p.) é agregado analiticamente: no nível de uma área
    com válidos V_i, entra como N(0, dp_mun^2 * sum V_i^2 / (sum V_i)^2). Isso evita sortear 5.570 x 500 mil números.
    """
    rng = np.random.default_rng(semente)
    p = prev.copy()
    p["reg_sim"] = p.regiao
    ufs = sorted(p.uf.unique())
    regs = sorted(p.reg_sim.unique())
    uf = p.groupby("uf").agg(V=("validos2_prev", "sum"), PT=("pt2_prev", "sum"),
                             V2=("validos2_prev", lambda v: float(np.sum(v.to_numpy() ** 2))))
    uf = uf.loc[ufs]
    uf["base"] = 100 * uf.PT / uf.V
    uf["sd_mun"] = dp_mun * np.sqrt(uf.V2) / uf.V
    uf["ireg"] = [regs.index(REGIAO.get(u, "EX")) for u in ufs]
    W = (uf.V / uf.V.sum()).to_numpy()
    base_nac = float(100 * uf.PT.sum() / uf.V.sum())
    sd_mun_nac = float(dp_mun * np.sqrt(uf.V2.sum()) / uf.V.sum())
    nac = np.empty(n)
    soma_uf = np.zeros(len(ufs))
    soma_uf_p = np.zeros(len(ufs))
    feitos = 0
    while feitos < n:
        k = min(lote, n - feitos)
        e_n = rng.normal(0, dp_nac, (k, 1))
        e_r = rng.normal(0, dp_reg, (k, len(regs)))[:, uf.ireg.to_numpy()]
        e_u = rng.normal(0, dp_uf, (k, len(ufs)))
        e_m = rng.normal(0, 1, (k, len(ufs))) * uf.sd_mun.to_numpy()
        s_uf = uf.base.to_numpy() + e_n + e_r + e_u + e_m
        nac[feitos:feitos + k] = s_uf @ W
        soma_uf += s_uf.sum(0)
        soma_uf_p += (s_uf > 50).sum(0)
        feitos += k
    q = np.percentile(nac, [2.5, 5, 10, 25, 50, 75, 90, 95, 97.5])
    return {
        "n_sim": n, "base_pct": base_nac,
        "p_lula": float(np.mean(nac > 50)),
        "media_pct": float(nac.mean()), "dp_pct": float(nac.std()),
        "quantis_pct": {k: float(v) for k, v in zip(["2.5", "5", "10", "25", "50", "75", "90", "95", "97.5"], q)},
        "dp_componentes_pp": {"nacional": dp_nac, "regional": dp_reg, "uf": dp_uf, "municipal": dp_mun,
                              "municipal_agregado_no_pais": sd_mun_nac},
        "uf": {u: {"fatia_lula_pct": round(float(uf.base.iloc[j]), 2), "media_sim_pct": round(float(soma_uf[j] / n), 2),
                   "p_lula": round(float(soma_uf_p[j] / n), 4), "validos_mi": round(float(uf.V.iloc[j] / 1e6), 3)}
               for j, u in enumerate(ufs)},
    }
