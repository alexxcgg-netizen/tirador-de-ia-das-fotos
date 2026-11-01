"""exp33 (L10) - figura dos valores singulares do jacobiano das memorias globais (e33_jacobiano.png).
Usa resultados/exp33_jacobianos.npz (exp33_jacobiano.py)."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TX = "#52514e"
CORES = ["#52514e", "#2a78d6", "#eb6834", "#1baf7a", "#9a9893", "#7a4fb5"]


def proj_fora(J, R):
    Q, _ = np.linalg.qr(R)
    return J - Q @ (Q.T @ J)


def main():
    d = np.load(os.path.join(RAIZ, "resultados", "exp33_jacobianos.npz"))
    nomes = sorted({k.split("_")[0] for k in d.files})
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for a in ax:
        a.set_facecolor("#fcfcfb")
        a.grid(color="#e6e5e0")
        a.tick_params(colors=TX)
    for i, n in enumerate(nomes):
        J1, Jrot, v0, mrow = d[n + "_J1"], d[n + "_Jrot"], d[n + "_v0"], d[n + "_mrow"]
        s = np.linalg.svd(proj_fora(J1, Jrot), compute_uv=False) / np.linalg.norm(v0)
        s0 = np.linalg.svd(proj_fora(J1[mrow], Jrot[mrow]), compute_uv=False) / np.linalg.norm(v0)
        ax[0].semilogy(np.arange(1, 8), s, "o-", color=CORES[i % 6], label=n)
        ax[1].semilogy(np.arange(1, 8), s0, "s--", color=CORES[i % 6], label=n)
    ax[0].axhline(1e-2, color="#eb6834", lw=0.8, ls=":")
    ax[0].text(1.1, 1.2e-2, "~ incerteza entre modelos (1%)", color="#eb6834", fontsize=8)
    ax[0].set_title("todos os multipolos l <= 4 (88), fora das rotacoes", color=TX, fontsize=10)
    ax[1].set_title("so as linhas m = 0 do referencial da fonte", color=TX, fontsize=10)
    for a in ax:
        a.set_xlabel("indice do valor singular", color=TX)
        a.set_ylabel("valor singular / |v|", color=TX)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e33_jacobiano.png"), dpi=130, facecolor="#fcfcfb")


if __name__ == "__main__":
    main()
