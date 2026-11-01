"""Figuras das linhas L05/L07 a partir das saidas json de exp24_fisher_memoria, exp25_fisher_onda, exp24_lei_quarto.

figuras/e24_fisher_memoria.png : (1) autovalores do Fisher branqueado pelo prior (memoria nula; onda oscilatoria em
                                 CE para contraste); (2) desvio a posteriori / desvio do prior por parametro;
                                 (3) lei (M f)^(1/4): 1 - |T| numerico contra a previsao de ordem dominante.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    C.estilo(plt)
    with open(os.path.join(C.RES, "exp24_fisher_memoria.json")) as fh:
        J24 = json.load(fh)
    with open(os.path.join(C.RES, "exp25_fisher_onda.json")) as fh:
        J25 = json.load(fh)
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.9))
    cores = {"aLIGO": C.COR["laranja"], "ET": C.COR["verde"], "CE": C.COR["azul"]}
    for p in ("aLIGO", "ET", "CE"):
        lam = J24["A"][p]["lam1"]
        ax[0].semilogy(np.arange(1, len(lam) + 1), lam, "o-", color=cores[p], label="memória nula, %s (ρ = %.2g)"
                       % (p, J24["A"][p]["rho"]))
    lam_b = J24["baixa"]["CE"]["lam_esc"]
    ax[0].semilogy(np.arange(1, 9), lam_b, "s--", color=cores["CE"], alpha=0.6, label="memória, M = 6, CE (ρ = 34)")
    lo = J25["osc"]["unico_psi0.000_CE"]["lam"]
    ax[0].semilogy(np.arange(1, len(lo) + 1), lo, "^:", color=C.COR["texto"], label="onda oscilatória, CE (ρ = 3201)")
    ax[0].axhline(1.0, color=C.COR["texto"], lw=0.8, ls=":")
    ax[0].set_xlabel("autovalor (ordem decrescente)")
    ax[0].set_ylabel("autovalor do Fisher branqueado pelo prior")
    ax[0].set_title("quantas direções os dados fixam (> 1)")
    ax[0].legend(frameon=False, fontsize=6.5, loc="lower left")
    nomes = J24["nomes"]
    x = np.arange(len(nomes))
    sp = np.array([J24["sig_prior"][n] for n in nomes])
    series = [("memória ET", np.array(J24["A"]["ET"]["post1"]) / sp, cores["ET"], "o"),
              ("memória CE", np.array(J24["A"]["CE"]["post1"]) / sp, cores["CE"], "o"),
              ("memória CE, rede (+ e ×)", np.array(J24["A"]["CE"]["post_rede"]) / sp, cores["CE"], "s"),
              ("oscilatória aLIGO", np.array(J25["osc"]["unico_psi0.000_aLIGO"]["post"][:8]) / sp, cores["aLIGO"], "^"),
              ("oscilatória CE", np.array(J25["osc"]["unico_psi0.000_CE"]["post"][:8]) / sp, C.COR["texto"], "^")]
    for k, (rot, v, cor, mk) in enumerate(series):
        ax[1].semilogy(x + (k - 2) * 0.08, v, mk, color=cor, label=rot, ms=4, alpha=0.9 if mk != "s" else 0.6)
    ax[1].set_xticks(x)
    rot_n = {"lnM": "ln M", "q": "q", "c1": "χ1", "c2": "χ2", "lnD": "ln D", "cosi": "cos ι", "t0": "t0", "psi": "ψ"}
    ax[1].set_xticklabels([rot_n[n] for n in nomes])
    ax[1].axhline(1.0, color=C.COR["texto"], lw=0.8, ls=":")
    ax[1].set_ylabel("σ a posteriori / σ do prior")
    ax[1].set_title("o que a memória sozinha mede (sistema A)")
    ax[1].legend(frameon=False, fontsize=6.5, loc="lower left")
    try:
        with open(os.path.join(C.RES, "exp24_lei_quarto.json")) as fh:
            JL = json.load(fh)
        cc = [C.COR["azul"], C.COR["laranja"], C.COR["verde"], C.COR["texto"], "#9a6fd0", "#c9a227"]
        for k, (rot, d) in enumerate(JL.items()):
            F = np.array(d["F"])
            pq = rot.replace("q", "").split("_c")
            ch = pq[1].split("_")
            lab = "q = %s, χ = (%s, %s)" % (pq[0].replace(".", ","), ch[0].replace(".", ","), ch[1].replace(".", ","))
            ax[2].loglog(F, d["um_menos_T"], "-", color=cc[k % len(cc)], label=lab)
            ax[2].loglog(F, d["c"] * np.cos(np.pi / 8) * (2 * np.pi * F) ** 0.25, ":", color=cc[k % len(cc)])
        Ma, Mb = 65 * C.MSUN_S, 6 * C.MSUN_S
        ax[2].axvspan(Ma * 10, Ma * 300, color=C.COR["azul"], alpha=0.06)
        ax[2].axvspan(Mb * 10, Mb * 300, color=C.COR["laranja"], alpha=0.06)
        ax[2].text(Ma * 12, 0.075, "10–300 Hz\nM = 65", fontsize=6.5, color=C.COR["azul"])
        ax[2].text(Mb * 12, 0.075, "10–300 Hz\nM = 6", fontsize=6.5, color=C.COR["laranja"])
        ax[2].set_ylim(0.06, 4)
        ax[2].set_xlabel("M f")
        ax[2].set_ylabel("1 − |T(f)|,  T = 2πif h̃+(f) / ΔH_total")
        ax[2].set_title("a memória na banda não é um degrau:\nlei (M f)^1/4 (pontilhado: ordem dominante)")
        ax[2].legend(frameon=False, fontsize=6, loc="upper left")
    except FileNotFoundError:
        pass
    fig.tight_layout()
    fig.savefig(os.path.join(C.FIG, "e24_fisher_memoria.png"), dpi=150)


if __name__ == "__main__":
    main()
