"""Teste do exp20_comum: janelas multiplas de uma so onda contra observaveis.memorias_observaveis (uma onda por janela).

Saida: resultados/exp20_teste_comum.txt
"""
import os
import time

import numpy as np

import exp20_comum as C
import observaveis as O

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


if __name__ == "__main__":
    A = C.PAR_A
    freqs = [10.0, 14.0, 20.0, 31.0]
    for todos_m in (False, True):
        for nivel in ("A", "C"):
            t0 = time.time()
            res = C.janelas(A["q"], A["c1"], A["c2"], A["M"], freqs, nivel=nivel, todos_m=todos_m)
            t1 = time.time() - t0
            pior = 0.0
            for f, (m, aux) in zip(freqs, res):
                mo, auxo = O.memorias_observaveis(A["q"], A["c1"], A["c2"], A["M"], f, nivel=nivel, todos_m=todos_m)
                for tipo in C.TIPOS:
                    for k, v in mo[tipo].items():
                        esc = max(abs(z) for z in mo[tipo].values())
                        pior = max(pior, abs(m[tipo][k] - v) / esc)
                vo = C.no_obs(mo, A["iota"], 0.7, A["M"], A["D"])
                v = C.no_obs(m, A["iota"], 0.7, A["M"], A["D"])
                log("  todos_m=%s nivel %s f=%5.1f Hz: t_i %.6f vs %.6f ; M_f %.10f vs %.10f ; obs rel %s"
                    % (todos_m, nivel, f, aux["t_i"], auxo["t_i"], aux["M_f"], auxo["M_f"],
                       " ".join("%.1e" % x for x in np.abs(v / vo - 1))))
            log("  -> pior diferenca relativa por multipolo: %.2e ; tempo das %d janelas numa chamada %.2f s"
                % (pior, len(freqs), t1))
    # todos os m: a fase orbital e zerada em t_i(min f) aqui e em t_i(f) em memorias_observaveis; a diferenca deve
    # ser uma rotacao azimutal phi -> phi - Delta, Delta = fase orbital em t_i(f) (modulo pi, ambiguidade do (2,2))
    log()
    log("todos_m: comparacao depois da rotacao azimutal (Delta = -fase22(t_i)/2 + k pi, k que minimiza)")
    res, (t, h) = C.janelas(A["q"], A["c1"], A["c2"], A["M"], freqs, todos_m=True, devolver_onda=True)
    fase = np.unwrap(np.angle(h[(2, 2)]))
    for f, (m, aux) in zip(freqs, res):
        mo, auxo = O.memorias_observaveis(A["q"], A["c1"], A["c2"], A["M"], f, todos_m=True)
        dl = -0.5 * float(np.interp(aux["t_i"], t, fase))
        melhor = None
        for kk in (0, 1):
            Dl = dl + kk * np.pi
            pior = 0.0
            for tipo in C.TIPOS:
                esc = max(abs(z) for z in mo[tipo].values())
                for (l, mm), v in mo[tipo].items():
                    pior = max(pior, abs(m[tipo][(l, mm)] * np.exp(1j * mm * Dl) - v) / esc)
            if melhor is None or pior < melhor[0]:
                melhor = (pior, kk, Dl)
        log("  f=%5.1f Hz: Delta = %+.6f rad (k=%d) ; pior diferenca relativa por multipolo depois da rotacao %.2e"
            % (f, melhor[2], melhor[1], melhor[0]))
    del t, h
    # jacobiano: custo e conferencia h contra h/2
    t0 = time.time()
    J1, y0 = C.jacobiano(A, freqs[:2])
    t1 = time.time() - t0
    passos2 = dict(q=1e-3, c1=1e-3, c2=1e-3, M=2.5e-4 * A["M"], iota=5e-5, D=5e-4 * A["D"], phi=5e-5)
    J2, _ = C.jacobiano(A, freqs[:2], passos=passos2)
    log()
    log("jacobiano 8x6 (10, 14 Hz): %.1f s ; |J(h) - J(h/2)| / |J| por coluna: %s"
        % (t1, " ".join("%.1e" % x for x in np.linalg.norm(J1 - J2, axis=0) / np.linalg.norm(J1, axis=0))))
    s1, _ = C.svd_escalado(J1, A, ("q", "c1", "c2", "M", "iota", "D"))
    s2, _ = C.svd_escalado(J2, A, ("q", "c1", "c2", "M", "iota", "D"))
    log("  valores singulares (escalas R4) h  : " + " ".join("%.4e" % x for x in s1))
    log("  valores singulares (escalas R4) h/2: " + " ".join("%.4e" % x for x in s2))
    with open(os.path.join(RAIZ, "resultados", "exp20_teste_comum.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
