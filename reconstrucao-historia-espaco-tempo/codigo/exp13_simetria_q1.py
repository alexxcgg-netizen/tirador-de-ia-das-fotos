"""Experimento 13: a direcao quase plana das memorias globais em massas iguais (exp06, A3).

Afirmacao analitica (simetria de troca): para q = 1, trocar os rotulos dos buracos (chi1 <-> chi2) e
o mesmo sistema girado de pi em torno do eixo z; os multipolos m = 0 nao mudam com essa rotacao, e os
modos de m impar trocam de sinal. Logo, com chi_s = (chi1 + chi2)/2 e chi_a = (chi1 - chi2)/2:
  memorias m = 0 (todas)  = funcoes PARES de chi_a      -> diferenca ~ chi_a^2,
  modos de m impar        = funcoes IMPARES de chi_a    -> amplitude ~ chi_a (nulos em chi_a = 0),
  modos de m par          = funcoes pares de chi_a.
Entao, perto de chi_a = 0, a memoria (mesmo global, todos os multipolos) so ve chi_a em 2a ordem,
enquanto a onda oscilatoria o ve em 1a ordem na amplitude (modos (2,1), (3,3), ...).
Teste numerico com NRHybSur3dq8_CCE: sistemas (q = 1, chi_s + d, chi_s - d) contra (1, chi_s, chi_s),
niveis A e C, e a onda num observador (M = 65, D = 400 Mpc, iota = 50 graus, aLIGO desde 10 Hz).
Saida: resultados/exp13_simetria_q1.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import binarias as B                                    # noqa: E402
import deteccao as Dt                                   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


M, D, IOTA, F = 65.0, 400.0, np.radians(50.0), 10.0
lista = B.lista_osc() + B.MODOS_M0
deltas = [0.025, 0.05, 0.1, 0.2]
for chi_s in (-0.5, 0.3):
    log("chi_s = %+.1f (q = 1): sistema B = (chi_s + d, chi_s - d) contra A = (chi_s, chi_s)" % chi_s)
    vA = {n: B.vetor(B.memorias(1.0, chi_s, chi_s, nivel=n)[0])[0] for n in ("A", "C")}
    tA, hA = B.gerar(1.0, chi_s, chi_s, f0=M * Dt.MSUN_S * F)
    tsA, sA = Dt.strain_observador(tA, hA, lista, M, D, IOTA)
    difs, mism, h21 = [], [], []
    for d in deltas:
        vB = {n: B.vetor(B.memorias(1.0, chi_s + d, chi_s - d, nivel=n)[0])[0] for n in ("A", "C")}
        rel = {n: np.max(np.abs((vB[n] - vA[n]) / vA[n])) for n in ("A", "C")}
        tB, hB = B.gerar(1.0, chi_s + d, chi_s - d, f0=M * Dt.MSUN_S * F)
        tsB, sB = Dt.strain_observador(tB, hB, lista, M, D, IOTA)
        cl = Dt.comparar(tsA, sA, tsB, sB, "aLIGO", fmin=F)["+"]
        k = np.argmax(np.abs(hB[(2, 2)]))
        r21 = np.abs(hB[(2, 1)][k]) / np.abs(hB[(2, 2)][k])
        difs.append(rel["C"])
        mism.append(1 - cl["match"])
        h21.append(r21)
        log("  d = %.3f: max dif. relativa das 7 memorias globais: nivel A %.2e, nivel C %.2e | onda: 1 - match aLIGO = %.2e (rho_crit %.1f, SNR_A %.0f) | |h21|/|h22| no pico = %.2e"
            % (d, rel["A"], rel["C"], 1 - cl["match"], cl["rho_crit"], cl["snr_A"], r21))
    ld = np.log(deltas)
    log("  expoentes (ajuste log-log): memorias (nivel C) ~ d^%.2f ; 1 - match ~ d^%.2f ; |h21|/|h22| ~ d^%.2f"
        % (np.polyfit(ld, np.log(difs), 1)[0], np.polyfit(ld, np.log(mism), 1)[0], np.polyfit(ld, np.log(h21), 1)[0]))
    log()
with open(os.path.join(AQUI, "..", "resultados", "exp13_simetria_q1.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
