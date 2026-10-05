"""Roda os cenários 2027–2030 e grava simulador/web/cenarios.json.

Saídas:
  * resumo exato (premissas padrão) por arquétipo e vencedor, e da diferença L − F;
  * "células": histogramas condicionais a cada combinação de eventos binários sem
    fonte (persistência do câmbio, regra do mínimo, IVA, 6x1, PEC 12). A página
    repondera as células quando o leitor move os controles (mistura exata, sem
    rodar o modelo no navegador). Uma grade extra fixa a sensibilidade do prêmio
    de risco à dívida (E8) em 0,03 / 0,112 / 0,33;
  * trajetórias macro e por arquétipo, com faixas;
  * sensibilidade (dados do gráfico de tornado) e decomposição por canal.

Uso:
    python cenarios/rodar.py                # 200.000 simulações por vencedor
    python cenarios/rodar.py --n 20000 --n-sens 10000 --saida /tmp/x.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cenarios as C  # noqa: E402

RAIZ = AQUI.parent
SAIDA = RAIZ / "simulador" / "web" / "cenarios.json"

METRICAS = list(C.ARQUETIPOS) + ["horas", "cestas"]
HIST = {  # (mín, máx, passo) — bordas exatas em 100 (índice), 0 (diferença)
    "pp": (40.0, 180.0, 0.5), "horas": (40.0, 220.0, 0.5), "cestas": (0.8, 3.6, 0.01),
    "d_pp": (-60.0, 60.0, 0.5), "d_horas": (-80.0, 80.0, 0.5), "d_cestas": (-1.5, 1.5, 0.01),
}
QS = [0.1, 0.25, 0.5, 0.75, 0.9]


def hist_tipo(m, diff=False):
    base = "pp" if m in C.ARQUETIPOS else m
    return ("d_" + base) if diff else base


def valores(r, m):
    if m in C.ARQUETIPOS:
        return r["pp"][m][:, -1]
    if m == "horas":
        return r["horas_cesta"][:, -1]
    return r["cestas_sm"][:, -1]


def histograma(v, tipo):
    lo, hi, st = HIST[tipo]
    nb = int(round((hi - lo) / st))
    idx = np.clip(np.floor((v - lo) / st + 1e-9).astype(int), 0, nb - 1)
    h = np.bincount(idx, minlength=nb)
    nz = np.nonzero(h)[0]
    if len(nz) == 0:
        return [0, []]
    return [int(nz[0]), h[nz[0]:nz[-1] + 1].tolist()]


def chaves_celulas(r, cand):
    ev = C.EVENTOS[cand]
    bits = np.stack([r["eventos"][e].astype(int) for e in ev], 1)
    return bits @ (1 << np.arange(len(ev))[::-1]), len(ev)


def celulas(R):
    """Histogramas condicionais por célula de eventos (marginais e da diferença)."""
    out = {"L": {}, "F": {}, "D": {}}
    cod = {}
    for cand in ("L", "F"):
        k, ne = chaves_celulas(R[cand], cand)
        cod[cand] = (k, ne)
        for c in range(1 << ne):
            sel = k == c
            nc = int(sel.sum())
            if nc == 0:
                continue
            key = format(c, f"0{ne}b")
            out[cand][key] = {"n": nc, "m": {m: [round(float(valores(R[cand], m)[sel].sum()), 3)]
                                             + histograma(valores(R[cand], m)[sel], hist_tipo(m))
                                             for m in METRICAS}}
    kL, nL = cod["L"]; kF, nF = cod["F"]
    dif = {m: valores(R["L"], m) - valores(R["F"], m) for m in METRICAS}
    for cl, cf in product(range(1 << nL), range(1 << nF)):
        sel = (kL == cl) & (kF == cf)
        nc = int(sel.sum())
        if nc == 0:
            continue
        key = format(cl, f"0{nL}b") + "|" + format(cf, f"0{nF}b")
        out["D"][key] = {"n": nc, "m": {m: [round(float(dif[m][sel].sum()), 3)]
                                        + histograma(dif[m][sel], hist_tipo(m, True)) for m in METRICAS}}
    return out


def peso_celula(chave, eventos, probs):
    """Probabilidade de uma célula (eventos independentes) — mesma conta da página."""
    p = 1.0
    for bit, e in zip(chave, eventos):
        p *= probs[e] if bit == "1" else 1 - probs[e]
    return p


def mistura_media(cel_cand, eventos, probs, metrica):
    """Média reponderada de uma métrica a partir das células (espelha a página)."""
    num = den = 0.0
    for k, c in cel_cand.items():
        w = peso_celula(k, eventos, probs)
        num += w * c["m"][metrica][0] / c["n"]
        den += w
    return num / den


def resumo(v):
    q = np.quantile(v, QS)
    return {"media": float(v.mean()), "p10": float(q[0]), "p25": float(q[1]), "p50": float(q[2]),
            "p75": float(q[3]), "p90": float(q[4])}


def resumo_exato(R):
    out = {}
    for m in METRICAS:
        vl, vf = valores(R["L"], m), valores(R["F"], m)
        lim = 100.0 if m in C.ARQUETIPOS else (C.BASE["horas_cesta"] if m == "horas" else C.BASE["cestas_por_sm"])
        melhor = (lambda v: (v < lim).mean()) if m == "horas" else (lambda v: (v > lim).mean())
        d = vl - vf
        out[m] = {"L": {**resumo(vl), "p_melhor": float(melhor(vl))},
                  "F": {**resumo(vf), "p_melhor": float(melhor(vf))},
                  "D": {**resumo(d), "p_L_maior": float((d > 0).mean())}}
    return out


def faixas_anuais(R):
    macro, arq = {}, {}
    for var in R["L"]["macro"]:
        if var == "premio":
            continue
        macro[var] = {}
        for cand in ("L", "F"):
            a = R[cand]["macro"][var]
            q = np.quantile(a, [0.1, 0.5, 0.9], axis=0)
            macro[var][cand] = {"p10": q[0].round(3).tolist(), "p50": q[1].round(3).tolist(),
                                "p90": q[2].round(3).tolist(), "media": a.mean(0).round(3).tolist()}
    for m in C.ARQUETIPOS:
        arq[m] = {}
        for cand in ("L", "F"):
            q = np.quantile(R[cand]["pp"][m], QS, axis=0)
            arq[m][cand] = {f"p{int(qq * 100)}": q[i].round(2).tolist() for i, qq in enumerate(QS)}
    for nome, chave in (("horas", "horas_cesta"), ("cestas", "cestas_sm")):
        arq[nome] = {}
        for cand in ("L", "F"):
            q = np.quantile(R[cand][chave], QS, axis=0)
            arq[nome][cand] = {f"p{int(qq * 100)}": q[i].round(3).tolist() for i, qq in enumerate(QS)}
    return macro, arq


def medias(R):
    out = {}
    for m in METRICAS:
        l, f = float(valores(R["L"], m).mean()), float(valores(R["F"], m).mean())
        out[m] = {"L": l, "F": f, "D": l - f}
    return out


# ---------------------------------------------------------------------------
# Sensibilidade (tornado): cada premissa sem fonte (e E8, de faixa larga) nos extremos
# ---------------------------------------------------------------------------
def _spec(cand, grupo, chave, valor):
    return ("spec", cand, grupo, chave, valor)


TORNADO = [
    # id, rótulo, tipo, [ajustes baixo], [ajustes alto], rótulos dos extremos
    ("L2", "P(depreciação persiste) — cenário Lula", "suposição",
     [_spec("L", "credibilidade", "p_persiste", 0.3)], [_spec("L", "credibilidade", "p_persiste", 0.7)], ("0,3", "0,7")),
    ("F2", "P(apreciação persiste) — cenário Flávio", "suposição",
     [_spec("F", "credibilidade", "p_persiste", 0.3)], [_spec("F", "credibilidade", "p_persiste", 0.7)], ("0,3", "0,7")),
    ("L3/F3", "Convergência quando o choque não persiste", "suposição",
     [("comum", "conv_pior", 0.0)], [("comum", "conv_pior", 0.068)], ("consenso", "+6,8%")),
    ("L4", "Selic fim de 2027 — cenário Lula", "suposição",
     [_spec("L", "credibilidade", "selic_2027", 11.0)], [_spec("L", "credibilidade", "selic_2027", 14.0)], ("11%", "14%")),
    ("F4", "Selic fim de 2027 — cenário Flávio", "suposição",
     [_spec("F", "credibilidade", "selic_2027", 9.75)], [_spec("F", "credibilidade", "selic_2027", 12.5)], ("9,75%", "12,5%")),
    ("F6", "P(Flávio mantém a regra do mínimo)", "suposição",
     [_spec("F", "minimo", "p_regra", 0.4)], [_spec("F", "minimo", "p_regra", 0.9)], ("0,4", "0,9")),
    ("L7", "Reajuste real do Bolsa Família — Lula", "suposição",
     [_spec("L", "bolsa", "real", 0.0)], [_spec("L", "bolsa", "real", 3.0)], ("0%", "+3%")),
    ("F7", "Reajuste real do Bolsa Família — Flávio", "suposição",
     [_spec("F", "bolsa", "real", -2.0)], [_spec("F", "bolsa", "real", 1.0)], ("−2%", "+1%")),
    ("F8", "P(Flávio mantém a isenção do IR)", "suposição",
     [_spec("F", "ir", "p_mantida", 0.7)], [_spec("F", "ir", "p_mantida", 1.0)], ("0,7", "1,0")),
    ("F9", "P(IVA de 20% aprovado)", "suposição",
     [_spec("F", "iva", "p", 0.05)], [_spec("F", "iva", "p", 0.4)], ("0,05", "0,4")),
    ("L12/F12", "P(fim da 6x1), nos dois cenários", "suposição",
     [_spec("L", "trabalho", "p_6x1", 0.3), _spec("F", "trabalho", "p_6x1", 0.3)],
     [_spec("L", "trabalho", "p_6x1", 0.8), _spec("F", "trabalho", "p_6x1", 0.8)], ("0,3", "0,8")),
    ("C13'", "6x1: alta de preços de serviços", "suposição",
     [("comum", "x6_precos_servicos", 0.0)], [("comum", "x6_precos_servicos", 3.0)], ("0%", "+3%")),
    ("F14", "P(PEC 12, contrato por hora)", "suposição",
     [_spec("F", "trabalho", "p_pec12", 0.1)], [_spec("F", "trabalho", "p_pec12", 0.5)], ("0,1", "0,5")),
    ("L16", "Ajuste fiscal até 2030 — Lula (p.p. PIB)", "projeção",
     [_spec("L", "credibilidade", "ajuste", 0.5)], [_spec("L", "credibilidade", "ajuste", 2.5)], ("0,5", "2,5")),
    ("F16", "Ajuste fiscal em 18 meses — Flávio (p.p. PIB)", "projeção",
     [_spec("F", "credibilidade", "ajuste", 0.5)], [_spec("F", "credibilidade", "ajuste", 3.0)], ("0,5", "3,0")),
    ("C15", "Defasagem que chega à bomba", "suposição",
     [("comum", "fracao_bomba", 0.0)], [("comum", "fracao_bomba", 0.47)], ("0", "0,47")),
    ("E5", "Assimetria do repasse cambial", "suposição",
     [("comum", "assimetria", 0.5)], [("comum", "assimetria", 1.0)], ("0,5", "1,0")),
    ("E8", "Prêmio por p.p. de dívida", "fonte (faixa larga)",
     [("comum", "premio_divida", 0.03)], [("comum", "premio_divida", 0.33)], ("0,03", "0,33")),
    ("M1", "Realimentação prêmio → câmbio e Selic", "suposição",
     [("comum", "premio_cambio", 0.05), ("comum", "premio_selic", 0.25)],
     [("comum", "premio_cambio", 0.15), ("comum", "premio_selic", 0.75)], ("fraca", "forte")),
    ("M2", "Acoplamento credibilidade ↔ Selic e ajuste", "suposição",
     [("comum", "acoplamento", 0.1)], [("comum", "acoplamento", 0.9)], ("0,1", "0,9")),
    ("M3", "Persistência do desvio da Selic", "suposição",
     [("comum", "selic_persistencia", 0.4)], [("comum", "selic_persistencia", 0.8)], ("0,4", "0,8")),
    ("M4a", "Efeito da Selic no PIB", "suposição",
     [("comum", "pib_selic", 0.15)], [("comum", "pib_selic", 0.45)], ("0,15", "0,45")),
    ("M4b", "Multiplicador fiscal", "suposição",
     [("comum", "multiplicador", 0.3)], [("comum", "multiplicador", 0.8)], ("0,3", "0,8")),
    ("M5", "Repasse da inflação aos salários", "suposição",
     [("comum", "indexacao_1", 0.3), ("comum", "indexacao_2", 0.2)],
     [("comum", "indexacao_1", 0.7), ("comum", "indexacao_2", 0.5)], ("baixo", "alto")),
    ("M6", "Comprometimento de renda × Selic", "suposição",
     [("comum", "credito_comprometimento", 0.1)], [("comum", "credito_comprometimento", 0.3)], ("0,1", "0,3")),
    ("C12", "Renda real 2028–30 (comum)", "suposição",
     [("comum", "renda_real_2028_30", -0.5)], [("comum", "renda_real_2028_30", 3.0)], ("−0,5%", "+3%")),
]


def aplicar(ajustes):
    comum, specs = {}, {"L": C.montar_spec("L"), "F": C.montar_spec("F")}
    for a in ajustes:
        if a[0] == "comum":
            comum[a[1]] = a[2]
        else:
            _, cand, grupo, chave, valor = a
            specs[cand][grupo][chave] = valor
    return comum, specs


def tornado(n, seed, base):
    out = []
    for pid, rot, tipo, baixo, alto, ext in TORNADO:
        res = {}
        for lado, aj in (("baixo", baixo), ("alto", alto)):
            comum, specs = aplicar(aj)
            res[lado] = medias(C.rodar_par(n, seed, comum, specs))
        out.append({"id": pid, "nome": rot, "tipo": tipo, "extremos": list(ext), **res})
    return out


def decomposicao(n, seed, base):
    """Contribuição de cada grupo de canais para a diferença média L − F
    (média das trocas nos dois sentidos; o resto é interação)."""
    out = {}
    for g in C.GRUPOS:
        f_com_l = C.rodar_cenario(C.montar_spec("F", {g: "L"}), n, seed, "F")
        l_com_f = C.rodar_cenario(C.montar_spec("L", {g: "F"}), n, seed, "L")
        contrib = {}
        for m in METRICAS:
            a = float(valores(f_com_l, m).mean()) - base[m]["F"]
            b = base[m]["L"] - float(valores(l_com_f, m).mean())
            contrib[m] = 0.5 * (a + b)
        out[g] = contrib
    return out


def arred(o, nd=4):
    if isinstance(o, float):
        return round(o, nd)
    if isinstance(o, dict):
        return {k: arred(v, nd) for k, v in o.items()}
    if isinstance(o, list):
        return [arred(v, nd) for v in o]
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    ap.add_argument("--n-sens", type=int, default=50_000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--saida", type=Path, default=SAIDA)
    a = ap.parse_args(argv)
    t0 = time.time()

    R = C.rodar_par(a.n, a.seed)
    exato = resumo_exato(R)
    macro, arq = faixas_anuais(R)
    grades = {"dist": celulas(R)}
    print(f"principal: {time.time() - t0:.1f}s", flush=True)
    for v in (0.03, 0.112, 0.33):
        Rg = C.rodar_par(a.n, a.seed, {"premio_divida": v})
        grades[f"{v:g}"] = celulas(Rg)
        print(f"grade E8={v}: {time.time() - t0:.1f}s", flush=True)

    base_s = medias(C.rodar_par(a.n_sens, a.seed))
    torn = tornado(a.n_sens, a.seed, base_s)
    print(f"tornado: {time.time() - t0:.1f}s", flush=True)
    dec = decomposicao(a.n_sens, a.seed, base_s)
    print(f"decomposição: {time.time() - t0:.1f}s", flush=True)

    pesos = {k: {c: round(v, 4) for c, v in d.items()} for k, d in C.PESOS.items()}
    out = {
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "n_por_vencedor": a.n, "n_sensibilidade": a.n_sens, "semente": a.seed,
            "anos": C.ANOS, "segundos": round(time.time() - t0, 1),
            "insumos": "research_notes/Nordeste e cenarios economicos 2026/cenarios_economicos_insumos.md",
        },
        "base": {k: round(float(v), 4) for k, v in C.BASE.items()},
        "consenso": {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in C.CONS.items()},
        "pesos": pesos,
        "arquetipos": C.ARQUETIPOS,
        "candidatos": {"L": "Lula", "F": "Flávio Bolsonaro"},
        "eventos": C.EVENTOS,
        "probs_padrao": {
            "L": {"persiste": C.CANDIDATOS["L"]["credibilidade"]["p_persiste"],
                  "x6": C.CANDIDATOS["L"]["trabalho"]["p_6x1"]},
            "F": {"persiste": C.CANDIDATOS["F"]["credibilidade"]["p_persiste"],
                  "regra_sm": C.CANDIDATOS["F"]["minimo"]["p_regra"],
                  "iva": C.CANDIDATOS["F"]["iva"]["p"],
                  "x6": C.CANDIDATOS["F"]["trabalho"]["p_6x1"],
                  "pec12": C.CANDIDATOS["F"]["trabalho"]["p_pec12"]},
        },
        "hist": {k: list(v) for k, v in HIST.items()},
        "metricas": METRICAS,
        "resumo_exato": exato,
        "grades": grades,
        "macro": macro,
        "trajetorias": arq,
        "tornado": {"base": base_s, "itens": torn},
        "decomposicao": {"grupos": C.GRUPO_NOME, "contrib": dec, "total": {m: base_s[m]["D"] for m in METRICAS}},
        "parametros": [dict(zip(["id", "nome", "lula", "flavio", "fonte", "tipo"], p)) for p in C.PARAMETROS],
    }
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(arred(out), ensure_ascii=False, separators=(",", ":"))
    a.saida.write_text(txt, encoding="utf-8")
    print(f"gravado {a.saida} ({len(txt) / 1e6:.2f} MB) em {time.time() - t0:.1f}s")
    for m in METRICAS:
        e = exato[m]
        print(f"{m:11s} L {e['L']['media']:7.2f} [{e['L']['p10']:.1f}–{e['L']['p90']:.1f}] "
              f"F {e['F']['media']:7.2f} [{e['F']['p10']:.1f}–{e['F']['p90']:.1f}] "
              f"D {e['D']['media']:+.2f} [{e['D']['p10']:+.1f}, {e['D']['p90']:+.1f}] P(L>F) {e['D']['p_L_maior']:.2f}")
    return out


if __name__ == "__main__":
    main()
