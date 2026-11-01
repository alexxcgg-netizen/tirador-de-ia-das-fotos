"""Resumo da tarefa 3 (L03): residuo minimo da familia em funcao de K e de q_B; previsao linear pelo jacobiano em A.

Le resultados/exp22_familia_<CONFIG>.json. Previsao linear: com q_B - q_A = dq e as outras 5 livres, o residuo minimo
linearizado e dq * |P_perp J_q|, P_perp = projetor ortogonal ao espaco das colunas (chi1, chi2, M, iota, D) do jacobiano
de r = (y_B - y_A)/|y_A| (exp20_comum.jacobiano, que da d ln|y|; r ~ d ln|y| para residuos pequenos).
Saida: resultados/exp22_resumo.txt; figuras/e22_familia.png
"""
import json
import os

import numpy as np

import exp20_comum as C
from exp22_familia_K import CONFIGS, QB, A

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    dados = {}
    for nome in CONFIGS:
        arq = os.path.join(RAIZ, "resultados", "exp22_familia_%s.json" % nome)
        if os.path.exists(arq):
            dados[nome] = json.load(open(arq))
    log("Residuo minimo (norma e max|r|) sobre (chi1, chi2, M, iota, D) com q_B fixo; melhor de todas as partidas")
    tab = {}
    for nome, d in dados.items():
        conj, freqs = CONFIGS[nome]
        tipos = C.TIPOS if conj == "T0" else ("deslocamento", "spin")
        J, _ = C.jacobiano(A, freqs, tipos=tipos)
        Jq, Jr = J[:, 0], J[:, 1:]
        Q, _ = np.linalg.qr(Jr)
        perp = np.linalg.norm(Jq - Q @ (Q.T @ Jq))
        linha = []
        for qB in QB:
            sols = [s for s in d["solucoes"] if abs(s["qB"] - qB) < 1e-12]
            b = min(sols, key=lambda s: s["norma"])
            linha.append((qB, b["norma"], b["maxres"], abs(qB - A["q"]) * perp, b["par"]))
        tab[nome] = linha
        log("  %-7s (%s, %d eq.): |P_perp J_q| = %.3e" % (nome, conj, J.shape[0], perp))
        for qB, nr, mx, lin, p in linha:
            log("     q_B=%.2f: norma %.2e max %.2e (linear %.2e) -> chi1 %+.3f chi2 %+.3f M %.2f iota %.1f D %.0f"
                % (qB, nr, mx, lin, p["c1"], p["c2"], p["M"], np.degrees(p["iota"]), p["D"]))
    # intervalo de q_B com residuo < limiar (interpolacao log-linear entre os pontos do perfil)
    log()
    log("Faixa de q_B (perfil) com max|r| abaixo do limiar:")
    for nome, linha in tab.items():
        txt = []
        for lim in (1e-4, 1e-3, 1e-2):
            ok = [qB for qB, nr, mx, lin, p in linha if mx < lim]
            txt.append("%.0e: %s" % (lim, ("[%.2f, %.2f]" % (min(ok), max(ok))) if ok else "nenhum"))
        log("  %-7s %s" % (nome, " ; ".join(txt)))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"axes.facecolor": "#fcfcfb", "figure.facecolor": "#fcfcfb", "axes.edgecolor": "#52514e",
                         "text.color": "#52514e", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "grid.color": "#e6e5e0", "font.size": 9})
    cores = ["#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#9b59b6", "#c0392b"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for i, conj in enumerate(("T0", "O0")):
        k = 0
        for nome, linha in tab.items():
            if CONFIGS[nome][0] != conj:
                continue
            q = [z[0] for z in linha]
            ax[i].semilogy(q, [max(z[2], 1e-13) for z in linha], "o-", color=cores[k % 6], ms=3,
                           label="%s (K=%d)" % (nome, len(CONFIGS[nome][1])))
            ax[i].semilogy(q, [max(z[3], 1e-13) for z in linha], ":", color=cores[k % 6], lw=0.8)
            k += 1
        ax[i].axvline(A["q"], color="#52514e", lw=0.6)
        ax[i].set_xlabel("$q_B$ (fixo)")
        ax[i].set_ylabel("resíduo mínimo max|r|")
        ax[i].set_title({"T0": "quatro memórias (m=0)", "O0": "deslocamento + spin (m=0)"}[conj]
                        + "; pontilhado: previsão linear", fontsize=9)
        ax[i].grid(True, which="both")
        ax[i].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e22_familia.png"), dpi=150)
    with open(os.path.join(RAIZ, "resultados", "exp22_resumo.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
