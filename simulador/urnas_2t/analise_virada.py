"""Virada do 2T por município: 1º turno (dados abertos, todos os candidatos) x 2º turno (arquivos do TSE baixados).
Saída: tabela por município (CSV) e regressão ecológica do ganho de votos de Lula e Flávio."""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/user/tirador-de-ia-das-fotos/simulador")
import resultado_1t as R
PASTA = Path(sys.argv[1]); SAIDA = Path(sys.argv[2])
t1 = {(r["uf"], int(r["cd_municipio"])): r for r in csv.DictReader(open("/home/user/tirador-de-ia-das-fotos/simulador/data/municipios_1t_2026_candidatos.csv", encoding="utf-8"))}
REG = R.REGIAO
rows = []
for f in PASTA.glob("*.json"):
    uf, cd = f.stem[:2].upper(), int(f.stem[2:])
    a = t1.get((uf, cd))
    if not a:
        continue
    r = R.parse_tse(json.loads(f.read_text(encoding="utf-8")), R.NUMEROS[2026])
    if r["pst"] < 99.99:
        continue
    g = {k: float(a[k]) for k in ("lula", "flavio", "caiado", "cury", "zema", "renan", "outros", "validos")}
    l2, f2 = r["votos"].get("Lula", 0.0), r["votos"].get("Flavio", 0.0)
    rows.append({"uf": uf, "regiao": REG[uf], "cd": cd, "municipio": a["municipio"], **{k + "_1t": v for k, v in g.items()},
                 "lula_2t": l2, "flavio_2t": f2, "validos_2t": l2 + f2, "comparecimento_2t": r["comparecimento"], "eleitorado": r["eleitorado"]})
with open(SAIDA, "w", encoding="utf-8", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
A = lambda k: np.array([x[k] for x in rows])
dl, df = A("lula_2t") - A("lula_1t"), A("flavio_2t") - A("flavio_1t")
terc = A("caiado_1t") + A("cury_1t") + A("zema_1t") + A("renan_1t") + A("outros_1t")
dv = A("validos_2t") - A("validos_1t")
novos = dv  # válidos a mais no 2º turno (comparecimento e menos brancos/nulos), saldo
print("municipios", len(rows), "validos 1t cobertos %.1f mi" % (A("validos_1t").sum() / 1e6))
print("Lula +%.2f mi, Flavio +%.2f mi; terceiros 1T %.2f mi; validos a mais %.2f mi" % (dl.sum() / 1e6, df.sum() / 1e6, terc.sum() / 1e6, dv.sum() / 1e6))
# regressão ecológica: ganho de Lula = soma de coeficientes x votos de cada fonte no 1º turno (+ válidos a mais)
X = np.column_stack([A("caiado_1t"), A("cury_1t"), A("zema_1t"), A("renan_1t"), A("outros_1t"), dv, A("flavio_1t"), A("lula_1t")])
nomes = ["Caiado", "Cury", "Zema", "Renan", "outros", "validos a mais", "Flavio 1T", "Lula 1T"]
wts = 1 / np.sqrt(A("validos_1t"))   # municípios grandes têm variância maior em votos absolutos
coef, *_ = np.linalg.lstsq(X * wts[:, None], dl * wts, rcond=None)
coefF, *_ = np.linalg.lstsq(X * wts[:, None], df * wts, rcond=None)
for n, c, cf in zip(nomes, coef, coefF):
    print(f"{n:15s} -> Lula {c:+.3f}  Flavio {cf:+.3f}")
for reg in ("S", "SE", "CO", "NE", "N"):
    m = A("regiao") == reg
    s1 = A("lula_1t")[m].sum() / (A("lula_1t")[m].sum() + A("flavio_1t")[m].sum()); s2 = A("lula_2t")[m].sum() / A("validos_2t")[m].sum()
    print(reg, "swing %.2f" % (100 * (s2 - s1)), "terceiros %.1f%%" % (100 * terc[m].sum() / A("validos_1t")[m].sum()), "Lula pega do saldo %.1f%%" % (100 * dl[m].sum() / (dl[m].sum() + df[m].sum())))
# versão restrita: cada fonte dividida entre os dois (coeficiente de Lula entre 0 e 1), sem troca direta entre Lula e Flávio
from scipy.optimize import lsq_linear
Xr = np.column_stack([A("caiado_1t"), A("cury_1t"), A("zema_1t"), A("renan_1t"), A("outros_1t"), dv])
nr = ["Caiado", "Cury", "Zema", "Renan", "outros", "validos a mais"]
alvo = dl - (dv * 0)  # ganho de Lula
fit = lambda m: lsq_linear(Xr[m] * wts[m, None], alvo[m] * wts[m], bounds=(0, 1)).x
base = fit(np.ones(len(rows), bool))
ufs = sorted(set(A("uf")))
rng = np.random.default_rng(1)
boots = []
for _ in range(200):                                   # bootstrap por UF (municípios de um estado se parecem)
    pick = rng.choice(ufs, len(ufs))
    m = np.concatenate([np.where(A("uf") == u)[0] for u in pick])
    boots.append(fit(m))
boots = np.array(boots)
print("restrito (fração que foi para Lula; IC 80% por bootstrap de UFs):")
for i, n in enumerate(nr):
    print(f"  {n:15s} {base[i]:.2f}  [{np.quantile(boots[:, i], .1):.2f}, {np.quantile(boots[:, i], .9):.2f}]")
pred = Xr @ base
print("explica %.1f%% do ganho de Lula; resíduo %.2f mi" % (100 * pred.sum() / dl.sum(), (dl.sum() - pred.sum()) / 1e6))
contrib = {n: float((Xr[:, i] * base[i]).sum() / 1e6) for i, n in enumerate(nr)}
print("contribuição ao ganho de Lula (mi):", {k: round(v, 2) for k, v in contrib.items()})
