"""Teste do 'efeito-sanduíche' eleitoral (renda × swing 2022→2026).

Duas partes, só leitura dos dados do repositório:
  A) Pesquisas por faixa de renda (simulador/data/renda_voto_aprovacao.csv): swing 2022→2026 por faixa,
     erro-padrão com efeito de desenho, e o contraste-sanduíche S = swing(meio) − média(swing base, swing topo).
     S < 0  => o meio andou mais para o adversário de Lula do que as duas pontas (assinatura sanduíche).
  B) Resultado real (TSE), ecológico: swing municipal 1T 2022 → 1T 2026 contra a renda domiciliar per capita
     do Censo 2022 (SIDRA 10295 v13431), com e sem controles (UF, % evangélicos, porte, capital).

Rodar:  python "research_notes/Nordeste e cenarios economicos 2026/sanduiche_eleitoral.py"
"""
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
DEFF = 1.5          # efeito de desenho suposto (amostras por cotas/pontos de fluxo)


# ---------------------------------------------------------------- A) pesquisas
def fatia(l, a):
    return 100 * l / (l + a)


def ep_fatia(p, n, base_validos=1.0):
    """erro-padrão (p.p.) da fatia bipartidária p (%) com n entrevistas na faixa."""
    n_ef = max(n * base_validos, 1) / DEFF
    return 100 * np.sqrt((p / 100) * (1 - p / 100) / n_ef)


def parte_a():
    df = pd.read_csv(RAIZ / "simulador/data/renda_voto_aprovacao.csv")
    v = df[df.medida.isin(["voto_2t", "voto_1t"])].copy()
    v["fatia"] = fatia(v.lula_pct, v.adversario_pct)
    v["ep"] = [ep_fatia(p, n, (l + a) / 100) for p, n, l, a in zip(v.fatia, v.n_faixa, v.lula_pct, v.adversario_pct)]
    print("\n== Fatia bipartidária de Lula por faixa (pesquisas) ==")
    print(v[["instituto", "campo_fim", "medida", "faixa", "lula_pct", "adversario_pct", "n_faixa", "fatia", "ep"]]
          .round(1).to_string(index=False))

    def pega(inst, campo, medida, faixa):
        s = v[(v.instituto == inst) & (v.campo_fim == campo) & (v.medida == medida) & (v.faixa == faixa)]
        return (float(s.fatia.iloc[0]), float(s.ep.iloc[0])) if len(s) else (np.nan, np.nan)

    pares = [
        # (rótulo, 2022, 2026)
        ("Datafolha 2T 28-29/10/22 -> 2T 15-17/09/26", ("Datafolha", "2022-10-29", "voto_2t"), ("Datafolha", "2026-09-17", "voto_2t")),
        ("Datafolha 2T 05-07/10/22 -> 2T 15-17/09/26", ("Datafolha", "2022-10-07", "voto_2t"), ("Datafolha", "2026-09-17", "voto_2t")),
        ("Datafolha 2T 28-29/10/22 -> 1T final 03/10/26 (bipartidário, corrigido 1T->2T)", ("Datafolha", "2022-10-29", "voto_2t"), ("Datafolha", "2026-10-03", "voto_1t")),
        ("Quaest 2T 23-25/10/22 -> 1T 24-27/09/26 (bipartidário, corrigido 1T->2T)", ("Quaest", "2022-10-25", "voto_2t"), ("Quaest", "2026-09-27", "voto_1t")),
    ]
    # correção 1T bipartidário -> 2T válidos por faixa, estimada no Datafolha 15-17/09/2026 (mesma amostra mede os dois)
    corr = {}
    for f in ["ate2", "2a5", "mais5"]:
        corr[f] = pega("Datafolha", "2026-09-17", "voto_2t", f)[0] - pega("Datafolha", "2026-09-17", "voto_1t", f)[0]
    print("\nCorreção 1T bipartidário -> 2T (Datafolha 15-17/09/26, p.p.):", {k: round(c, 1) for k, c in corr.items()})

    nac = {  # fatia nacional da mesma pesquisa (2T válidos, ou 1T bipartidário) para tirar o deslocamento comum
        ("Datafolha", "2022-10-29", "voto_2t"): 52.0, ("Datafolha", "2022-10-07", "voto_2t"): 53.0,
        ("Datafolha", "2026-09-17", "voto_2t"): fatia(46, 44), ("Datafolha", "2026-10-03", "voto_1t"): fatia(42, 40),
        ("Quaest", "2022-10-25", "voto_2t"): fatia(48, 42), ("Quaest", "2026-09-27", "voto_1t"): fatia(39, 34),
    }
    linhas = []
    for rot, a, b in pares:
        sw, ep = {}, {}
        for f in ["ate2", "2a5", "mais5"]:
            p0, e0 = pega(*a, f)
            p1, e1 = pega(*b, f)
            if b[2] == "voto_1t":
                p1 += corr[f]
                e1 = np.hypot(e1, 2.0)        # incerteza extra da correção (suposta)
            sw[f], ep[f] = p1 - p0, np.hypot(e0, e1)
        n0, n1 = nac[a], nac[b] + (np.nan if b[2] == "voto_1t" else 0)
        S = sw["2a5"] - 0.5 * (sw["ate2"] + sw["mais5"])
        eS = np.sqrt(ep["2a5"] ** 2 + 0.25 * (ep["ate2"] ** 2 + ep["mais5"] ** 2))
        G = sw["mais5"] - sw["ate2"]
        eG = np.hypot(ep["mais5"], ep["ate2"])
        linhas.append(dict(par=rot, sw_ate2=sw["ate2"], ep_ate2=ep["ate2"], sw_2a5=sw["2a5"], ep_2a5=ep["2a5"],
                           sw_mais5=sw["mais5"], ep_mais5=ep["mais5"], S=S, ep_S=eS, gradiente_topo_base=G, ep_G=eG,
                           sw_nacional=(nac[b] - nac[a]) if b[2] == "voto_2t" else np.nan))
    t = pd.DataFrame(linhas)
    print("\n== Swing 2022->2026 por faixa (p.p. da fatia de Lula) e contraste-sanduíche S ==")
    print(t.round(1).to_string(index=False))
    # combinação por variância inversa (as linhas não são independentes: partilham a amostra de 2026)
    w = 1 / t.ep_S ** 2
    print(f"\nS combinado (variância inversa, ignora dependência): {np.sum(w * t.S) / w.sum():+.1f}"
          f" ± {1 / np.sqrt(w.sum()):.1f} p.p.  (S<0 = sanduíche)")
    return t


# ---------------------------------------------------------------- B) resultado real, ecológico
def wls(y, X, w):
    W = np.sqrt(w)
    b, *_ = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)
    e = y - X @ b
    # erro-padrão robusto (HC1) ponderado
    XtWX_inv = np.linalg.pinv((X * w[:, None]).T @ X)
    meat = (X * (w * e)[:, None]).T @ (X * (w * e)[:, None])
    n, k = X.shape
    V = XtWX_inv @ meat @ XtWX_inv * n / (n - k)
    return b, np.sqrt(np.diag(V))


def parte_b():
    m26 = pd.read_csv(RAIZ / "modelo_municipal/data/mun_2026_1t.csv")
    m22 = pd.read_csv(RAIZ / "modelo_municipal/data/hist_2022.csv")
    cov = pd.read_csv(AQUI / "covariaveis_mun_br.csv")
    d = (m26.merge(m22, on=["cd_municipio_tse", "uf"], how="inner")
            .merge(cov[["codigo_tse", "capital", "renda_pc", "pct_evang"]], left_on="cd_municipio_tse",
                   right_on="codigo_tse", how="inner"))
    d = d[d.uf != "ZZ"].copy()
    d["p22"] = fatia(d.t1_pt, d.t1_opp)                 # 1T 2022, Lula/(Lula+Bolsonaro)
    d["p26"] = fatia(d.lula, d.flavio)                  # 1T 2026, Lula/(Lula+Flávio)
    d["q22"] = 100 * d.t2_pt / d.t2_validos             # 2T 2022
    d["v22"] = 100 * d.t1_pt / d.t1_validos
    d["v26"] = 100 * d.lula / d.validos
    d["swing2p"] = d.p26 - d.p22
    d["swing_v"] = d.v26 - d.v22
    d["nordeste"] = d.uf.isin(["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"])
    d["w"] = d.validos
    # renda familiar equivalente em SM: renda pc × 2,79 moradores (Censo 2022) / SM 2022 (R$ 1.212). Aproximação.
    d["sm_fam_equiv"] = d.renda_pc * 2.79 / 1212
    print(f"\nMunicípios casados: {len(d)}; válidos 2026: {d.validos.sum()/1e6:.1f} mi")

    def tab(g):
        w = g.w
        return pd.Series({"munic": len(g), "validos_mi": w.sum() / 1e6,
                          "renda_pc_media": np.average(g.renda_pc, weights=w),
                          "p22": np.average(g.p22, weights=w), "p26": np.average(g.p26, weights=w),
                          "swing2p": np.average(g.swing2p, weights=w), "swing_v": np.average(g.swing_v, weights=w)})

    def quantil_ponderado(g, k):
        g = g.sort_values("renda_pc")
        cw = g.w.cumsum() / g.w.sum()
        return g.assign(q=np.minimum((cw * k).astype(int) + 1, k))

    # decis (Brasil) e quintis (recortes) de renda, ponderados por eleitores (válidos 2026)
    d = quantil_ponderado(d, 10).rename(columns={"q": "decil"})
    out = {"BR": d.groupby("decil").apply(tab)}
    hi = d.pct_evang >= np.average(d.pct_evang, weights=d.w)
    for nome, sub in [("NE", d[d.nordeste]), ("fora_NE", d[~d.nordeste]),
                      ("evang_alto", d[hi]), ("evang_baixo", d[~hi]),
                      ("fora_NE_evang_baixo", d[~d.nordeste & ~hi])]:
        out[nome] = quantil_ponderado(sub, 5).groupby("q").apply(tab)
    for k, t in out.items():
        print(f"\n== Swing municipal por faixa de renda pc ({k}) ==")
        print(t.round(2).to_string())

    # regressões: swing2p ~ UF FE + controles + log renda + log renda^2
    d["lr"] = np.log(d.renda_pc) - np.log(np.average(d.renda_pc, weights=d.w))
    ufs = sorted(d.uf.unique())
    FE = np.column_stack([(d.uf == u).astype(float) for u in ufs])
    ctrl = np.column_stack([d.pct_evang / 10, np.log(d.aptos), d.capital, d.p22 / 10])
    res = []
    for nome, X, cols in [
        ("só renda (linear+quadr.)", np.column_stack([np.ones(len(d)), d.lr, d.lr ** 2]), ["const", "lr", "lr2"]),
        ("UF FE + renda", np.column_stack([FE, d.lr, d.lr ** 2]), ufs + ["lr", "lr2"]),
        ("UF FE + evang + porte + capital + p22 + renda",
         np.column_stack([FE, ctrl, d.lr, d.lr ** 2]), ufs + ["evang10", "log_aptos", "capital", "p22_10", "lr", "lr2"]),
    ]:
        b, se = wls(d.swing2p.values, X, d.w.values)
        i, j = cols.index("lr"), cols.index("lr2")
        vert = -b[i] / (2 * b[j]) if b[j] != 0 else np.nan
        res.append(dict(modelo=nome, b_lr=b[i], ep_lr=se[i], b_lr2=b[j], ep_lr2=se[j],
                        vertice_renda_pc=float(np.exp(vert) * np.average(d.renda_pc, weights=d.w))))
        if "evang10" in cols:
            k = cols.index("evang10")
            res[-1]["b_evang10"] = b[k]; res[-1]["ep_evang10"] = se[k]
    # decis como dummies (decil 1 = referência), com UF FE e controles: forma livre da relação
    D = np.column_stack([(d.decil == k).astype(float) for k in range(2, 11)])
    for nome, X in [("decis + UF FE", np.column_stack([FE, D])),
                    ("decis + UF FE + evang + porte + capital + p22", np.column_stack([FE, ctrl, D]))]:
        b, se = wls(d.swing2p.values, X, d.w.values)
        print(f"\n== {nome}: efeito do decil de renda pc no swing bipartidário (p.p., vs decil 1) ==")
        print("  " + "  ".join(f"D{k}:{b[-10 + k]:+.2f}({se[-10 + k]:.2f})" for k in range(1, 10)).replace("D1:", "D2:", 1)
              if False else "  " + "  ".join(f"D{k + 2}:{b[X.shape[1] - 9 + k]:+.2f}({se[X.shape[1] - 9 + k]:.2f})"
                                             for k in range(9)))
    r = pd.DataFrame(res)
    print("\n== WLS: swing bipartidário (p.p.) ~ log renda pc + (log renda pc)^2; EP robusto HC1 ==")
    print("   b_lr2 > 0 e vértice no meio da distribuição = forma em U no swing de Lula = sanduíche ecológico")
    print(r.round(3).to_string(index=False))
    out["BR"].round(3).to_csv(AQUI / "sanduiche_swing_decis_renda.csv")
    return out, r


if __name__ == "__main__":
    parte_a()
    parte_b()
