"""Verificacao independente (R2v) do item 6 da revisao R2: simetria de troca em q = 1 (exp13).

Analitico: em q = 1, trocar (chi1, chi2) -> (chi2, chi1) e o mesmo sistema girado de pi em torno de z, logo
h_lm -> (-1)^m h_lm e todas as memorias m = 0 (bilineares com m = m') sao PARES em chi_a, em qualquer nivel.
Uma parte impar mede a violacao da simetria pelo substituto (modelo), nao pela fisica.

1) Expoentes do 07 §3.1/§3.2 recalculados a partir dos numeros impressos em resultados/exp13_simetria_q1.txt.
2) Decomposicao par/impar por multipolo (janela global M f0 = 0.004, como no exp13), niveis A e C, d = 0.0125,
   0.05, 0.1, 0.2; e no nivel A tambem com o inicio suave de rev_R2v_escada (sem a escada da grade), para
   excluir que a parte impar do nivel A seja o salto de uma amostra no inicio da janela.
3) A violacao diretamente nos modos: amplitudes |h_lm| de (chi_s + d, chi_s - d) e (chi_s - d, chi_s + d) numa
   grade comum (t de -3000 M a 80 M), e diferenca de fase orbital acumulada.
Saida: resultados/revisao/rev_R2v_simetria.txt
"""
import os
import re
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import binarias as B                                    # noqa: E402
import rev_R2v_escada as E                              # noqa: E402

RES = os.path.join(AQUI, "..", "..", "resultados")
NOMES = ["desl20", "desl40", "spin30", "cm20", "cm40", "giro10", "giro30"]
F0 = 0.004
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def ajuste(d, y):
    return np.polyfit(np.log(d), np.log(y), 1)[0]


# ------------------------------------------------------------------ 1) numeros do exp13
txt = open(os.path.join(RES, "exp13_simetria_q1.txt")).read()
log("1) Expoentes a partir dos numeros impressos no exp13 (d = 0.025, 0.05, 0.1, 0.2):")
for bloco in txt.split("chi_s = ")[1:]:
    chi = bloco.split(" ")[0]
    reg = re.findall(r"d = ([\d.]+): .*?nivel A ([\d.e+-]+), nivel C ([\d.e+-]+) \| onda: 1 - match aLIGO = ([\d.e+-]+)", bloco)
    d = np.array([float(r[0]) for r in reg])
    a, c, m = (np.array([float(r[k]) for r in reg]) for k in (1, 2, 3))
    loc = lambda y: " ".join("%.2f" % (np.log(y[i + 1] / y[i]) / np.log(d[i + 1] / d[i])) for i in range(len(d) - 1))
    log("   chi_s %s: nivel A d^%.2f (locais %s ; A/d^2 = %s) | nivel C d^%.2f | 1-match d^%.2f (locais %s)"
        % (chi, ajuste(d, a), loc(a), " ".join("%.3f" % x for x in a / d ** 2), ajuste(d, c), ajuste(d, m), loc(m)))

# ------------------------------------------------------------------ 2) par e impar por multipolo
log("")
log("2) Parte par [v(+d)+v(-d)]/2 - v(0) e impar [v(+d)-v(-d)]/2, relativas a |v(0)|, por multipolo (janela M f0 = 0.004).")


def vets(c1, c2):
    t, h = B.gerar(1.0, c1, c2, f0=F0)
    out = {n: B.vetor(B.memorias(1.0, c1, c2, f0=F0, nivel=n, t=t, h=h)[0])[0] for n in ("A", "C")}
    del t, h
    out["A suave"] = B.vetor(E.memorias_suave(1.0, c1, c2, F0, 0.25, "A")[0])[0]
    return out


for chi_s in (0.3, -0.5):
    v0 = vets(chi_s, chi_s)
    imp_max = {n: [] for n in v0}
    par_max = {n: [] for n in v0}
    ds = (0.0125, 0.05, 0.1, 0.2)
    for d in ds:
        vp, vm = vets(chi_s + d, chi_s - d), vets(chi_s - d, chi_s + d)
        for n in ("A", "A suave", "C"):
            imp = np.abs((vp[n] - vm[n]) / 2 / v0[n])
            par = np.abs(((vp[n] + vm[n]) / 2 - v0[n]) / v0[n])
            rel = np.abs((vp[n] - v0[n]) / v0[n])
            imp_max[n].append(imp.max())
            par_max[n].append(par.max())
            if d in (0.0125, 0.1):
                log("   chi_s %+.1f d %.4f nivel %-7s impar: %s" % (chi_s, d, n, " ".join("%s %.1e" % kv for kv in zip(NOMES, imp))))
                log("   %s par:   %s | max dif. B-A %.2e (%s)" % (" " * 33, " ".join("%s %.1e" % kv for kv in zip(NOMES, par)),
                                                              rel.max(), NOMES[int(np.argmax(rel))]))
    for n in ("A", "A suave", "C"):
        log("   chi_s %+.1f nivel %-7s: max impar/d = %s ; max par/d^2 = %s ; expoentes impar %.2f par %.2f"
            % (chi_s, n, " ".join("%.2e" % (y / d) for y, d in zip(imp_max[n], ds)),
               " ".join("%.3f" % (y / d ** 2) for y, d in zip(par_max[n], ds)), ajuste(ds, imp_max[n]), ajuste(ds, par_max[n])))

# ------------------------------------------------------------------ 3) violacao nos modos
log("")
log("3) Violacao nos modos oscilatorios: (chi_s + d, chi_s - d) contra (chi_s - d, chi_s + d), d = 0.1, t de -3000 a 80 M.")
tc = np.arange(-3000.0, 80.0, 0.25)
for chi_s in (0.3, -0.5):
    hs = []
    for c1, c2 in ((chi_s + 0.1, chi_s - 0.1), (chi_s - 0.1, chi_s + 0.1)):
        t, h = B.gerar(1.0, c1, c2, f0=F0)
        hs.append({k: np.interp(tc, t, np.abs(h[k])) for k in ((2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (2, 0), (3, 0))}
                  | {"fase": np.interp(tc, t, np.unwrap(np.angle(h[(2, 2)])))})
        del t, h
    txt = []
    for k in ((2, 2), (2, 1), (3, 3), (3, 2), (4, 4), (2, 0), (3, 0)):
        a, b = hs[0][k], hs[1][k]
        txt.append("%s %.1e" % ("".join(map(str, k)), np.max(np.abs(a - b)) / np.max(a)))
    df = hs[0]["fase"] - hs[1]["fase"]
    df -= df[0]
    log("   chi_s %+.1f: max ||h_lm(+)|-|h_lm(-)|| / max|h_lm(+)|: %s ; fase do (2,2) acumulada de -3000 a 0 M: %.1e rad"
        % (chi_s, " ".join(txt), np.abs(df[np.argmin(np.abs(tc))])))
with open(os.path.join(RES, "revisao", "rev_R2v_simetria.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
