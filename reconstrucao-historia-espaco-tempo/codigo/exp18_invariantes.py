"""Experimento 18 (L02, tarefa 5): o que e preservado ao longo da fibra T0 de A?

Le resultados/exp17_fibra.json (solucoes T0 polidas, campo 'exato') e recalcula as memorias exatas em cada solucao
(exp17_comum). Para cada candidato a invariante, dispersao relativa (max - min)/|media| ao longo da fibra:
  parametros: M, q, eta, Mc, chi_eff, chi_a, D, iota;
  cargas e remanescente: M_f (fisico), E irradiada na janela e total (fisicas), multipolos globais desl20, spin30,
  cm20, giro10 (adimensionais e fisicos);
  combinacoes sugeridas pela ordem dominante e pela reducao (2,2):
    desl  ~ (eta M / D) sin^2 i (17 + cos^2 i)          (Favata 2009; simetria eta, D -> lambda eta, lambda D do 07)
    spin  ~ (eta M^2 / D) sin^2 i cos i
    CM/desl = M (cm/desl)_adim ~ -M_f,fis (1 + nu) / 2, nu = parte nula / parte ordinaria no observador
    E_janela,fis * sin^2 i (17 + cos^2 i) / D            (deslocamento ~ energia irradiada x forma angular)
Saidas: resultados/exp18_invariantes.txt, figuras/e18_invariantes.png
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import exp17_comum as C                                  # noqa: E402
from harmonicos import sYlm, Dfrak                      # noqa: E402

SAIDA = os.path.join(AQUI, "..", "resultados", "exp18_invariantes")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def quantidades(q, c1, c2, M, D, iota):
    r = C.memorias_varias(q, c1, c2, [M], media=False)[0]
    mem, aux = C.so_m0(r["mem_ti"]), r["aux"]
    v = C.fisicos(mem, iota, 0.0, M, D)
    a = C.adim(mem, iota, 0.0)
    Mf = aux["M_f"]
    ordn = sum(-1.5 * Mf * mem["deslocamento"][(l, 0)].real / Dfrak(l) * sYlm(-2, l, 0, iota, 0.0).real
               for l in range(2, 9) if (l, 0) in mem["deslocamento"])
    nu = (a["cm"] - ordn) / ordn
    eta = q / (1 + q) ** 2
    s2 = np.sin(iota) ** 2
    out = dict(M=M, q=q, eta=eta, Mc=M * eta ** 0.6, chi_eff=(q * c1 + c2) / (1 + q), chi_a=0.5 * (c1 - c2), D=D,
               iota=np.degrees(iota), M_f_fis=Mf * M, M_f_adim=Mf, E_jan_fis=aux["E_janela"] * M,
               E_tot_fis=(aux["E_janela"] + aux["E_lig"]) * M,
               desl20=mem["deslocamento"][(2, 0)].real, spin30=mem["spin"][(3, 0)].imag, cm20=mem["cm"][(2, 0)].real,
               giro10=mem["giroscopica"][(1, 0)].real,
               nu=nu, Mf_1nu=Mf * M * (1 + nu), r_cm=a["cm"] / a["deslocamento"],
               lo_desl=eta * M / D * s2 * (17 + np.cos(iota) ** 2),
               lo_spin=eta * M ** 2 / D * s2 * np.cos(iota),
               E_ang=aux["E_janela"] * M * s2 * (17 + np.cos(iota) ** 2) / D,
               desl_obs=v["deslocamento"], spin_obs=v["spin"], cm_obs=v["cm"], giro_obs=v["giroscopica"])
    return out


if __name__ == "__main__":
    d = json.load(open(os.path.join(AQUI, "..", "resultados", "exp17_fibra.json")))
    sols = []
    for chave, reg in d["pontos"].items():
        for s in reg["T0"]:
            e = s.get("exato")
            if e is None or e["res"] > 1e-6 or e["no_limite"]:
                continue
            sols.append((reg["qB"], e["chi1"], reg["c2B"], e["M"], e["D"], e["iota"]))
    log("Fibra T0 de A: %d solucoes polidas (residuo < 1e-6, dentro do dominio)" % len(sols))
    A = quantidades(1.2, 0.3, -0.2, 65.0, 400.0, np.radians(50.0))
    Q = [quantidades(*s) for s in sols]
    nomes = list(A.keys())
    log("%-10s %12s %12s %12s %10s" % ("grandeza", "A", "min", "max", "(max-min)/|A|"))
    disp = {}
    for k in nomes:
        v = np.array([x[k] for x in Q])
        disp[k] = (v.max() - v.min()) / abs(A[k]) if A[k] != 0 else np.nan
        log("%-10s %12.5e %12.5e %12.5e %10.2e" % (k, A[k], v.min(), v.max(), disp[k]))
    # correlacoes dos intrinsecos ao longo da fibra
    X = np.array([[x["q"], x["chi_eff"], x["chi_a"], x["M"], x["D"], x["iota"]] for x in Q])
    log("")
    log("Correlacoes ao longo da fibra (q, chi_eff, chi_a, M, D, iota):")
    log(np.array2string(np.corrcoef(X.T), precision=3))
    # ajuste linear de chi_eff em ln eta
    eta = np.array([x["eta"] for x in Q])
    ce = np.array([x["chi_eff"] for x in Q])
    p = np.polyfit(np.log(eta), ce, 1)
    log("chi_eff ~ %.4f ln(eta) + %.4f (residuo rms %.3f)" % (p[0], p[1], np.std(ce - np.polyval(p, np.log(eta)))))
    with open(SAIDA + ".txt", "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(SAIDA + ".json", "w") as fh:
        json.dump(dict(A=A, sols=Q), fh, indent=0, default=float)
    # figura
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                         "text.color": "#52514e", "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0",
                         "axes.spines.top": False, "axes.spines.right": False})
    sel = ["M", "Mc", "eta", "chi_eff", "D", "iota", "M_f_fis", "E_tot_fis", "desl20", "spin30", "giro10", "Mf_1nu",
           "lo_desl", "lo_spin", "E_ang"]
    rot = {"M": "M", "Mc": "massa de chirp", "eta": "η", "chi_eff": "χ_ef", "D": "D", "iota": "ι", "M_f_fis": "M_f",
           "E_tot_fis": "E irradiada", "desl20": "J₂₀ (adim.)", "spin30": "S₃₀ (adim.)", "giro10": "Φ₁₀ (adim.)",
           "Mf_1nu": "M_f (1 + ν)", "lo_desl": "ηM sin²ι(17+cos²ι)/D", "lo_spin": "ηM² sin²ι cosι/D",
           "E_ang": "E_jan sin²ι(17+cos²ι)/D"}
    vals = [disp[k] for k in sel]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    cores = ["#eb6834" if k in ("Mf_1nu", "lo_desl", "lo_spin", "E_ang") else "#2a78d6" for k in sel]
    ax.bar(range(len(sel)), vals, color=cores)
    ax.set_yscale("log")
    ax.set_xticks(range(len(sel)))
    ax.set_xticklabels([rot[k] for k in sel], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("(máx − mín)/|valor de A| na fibra")
    ax.set_title("Variação ao longo da fibra T0 de A (%d soluções exatas); laranja: combinações candidatas a invariante" % len(Q),
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(AQUI, "..", "figuras", "e18_invariantes.png"), dpi=140)
