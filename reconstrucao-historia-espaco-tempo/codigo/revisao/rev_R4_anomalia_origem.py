"""Revisor R4, tarefa 2 (diagnostico): de onde vem a dependencia das memorias em l0?

Para B (e0 = 0.2, q_B = 2) do exp12 com l0 = 0, pi/2, pi, 3pi/2 (e, para comparar, e0 = 0 e e0 = 0.05):
  - duracao do sinal (inicio da janela ate o pico), energia na janela E_jan, |h22| no pico;
  - energia irradiada antes de t = -T (T = 2000, 500, 100 M antes do pico) e depois: onde a diferenca
    entre l0 = 0 e l0 = pi se acumula (inicio da janela, inspiral ou fusao);
  - o mesmo para a integral da helicidade/momento angular (proxy da memoria de spin): int Im(conj(h) hdot) por modo.
  - teste de deslocamento temporal: B(l0 = pi) comparado com B(l0 = 0) truncado/estendido para a mesma duracao.
Saida: resultados/revisao/rev_R4_anomalia_origem.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402
import binarias as Bn                                   # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


q, c1, c2, M = 2.0, 0.05960457850002948, 0.0, 72.5875185658003
f0 = M * C.Dt.MSUN_S * C.F_FIS


def fluxos(e0, l0):
    t, h = C.gerar(q, c1, c2, f0, e0, l0)
    dt = t[1] - t[0]
    H = np.stack([h[k] for k in C.LISTA], axis=1)
    Hd = Bn.derivada4(H, dt)
    dE = np.sum(np.abs(Hd) ** 2, axis=1) / (16 * np.pi)                     # dE/du
    mm = np.array([k[1] for k in C.LISTA])
    dJ = np.sum(mm * np.imag(np.conj(H) * Hd), axis=1) / (16 * np.pi) * -1   # dJz/du (sinal irrelevante)
    i_pico = np.argmax(np.abs(h[(2, 2)]))
    return t - t[i_pico], dE, dJ, np.abs(h[(2, 2)][i_pico]), dt


if __name__ == "__main__":
    log("Diagnostico da dependencia em l0: B (e0 = 0.2, q = 2, chi1 = 0.0596, M = 72.59), SEOBNRv5EHM, janela desde f_onda media 10 Hz")
    res = {}
    for e0, l0 in [(0.0, 0.0), (0.05, 0.0), (0.05, np.pi), (0.2, 0.0), (0.2, 0.5 * np.pi), (0.2, np.pi), (0.2, 1.5 * np.pi)]:
        t, dE, dJ, a22, dt = fluxos(e0, l0)
        Ej, Jj = np.sum(dE) * dt, np.sum(dJ) * dt
        cortes = {}
        for T in (4000.0, 2000.0, 500.0, 100.0):
            sel = t < -T
            cortes[T] = (np.sum(dE[sel]) * dt, np.sum(dJ[sel]) * dt)
        res[(e0, l0)] = dict(t0=t[0], Ej=Ej, Jj=Jj, a22=a22, cortes=cortes, t=t, dE=dE, dJ=dJ, dt=dt)
        log("  e0 = %.2f l0 = %.2f pi: duracao %.1f M ; E_jan %.6e ; J_jan %.6e ; |h22| pico %.6f ; E depois de -100 M %.6e ; J antes de -2000 M %.6e"
            % (e0, l0 / np.pi, -t[0], Ej, Jj, a22, Ej - cortes[100.0][0], cortes[2000.0][1]))
    log()
    log("Diferenca relativa (l0 - [l0 = 0]) / [l0 = 0], e0 = 0.2, por trecho (tempo antes do pico):")
    r0 = res[(0.2, 0.0)]
    for l0 in (0.5 * np.pi, np.pi, 1.5 * np.pi):
        r = res[(0.2, l0)]
        dEtot = r["Ej"] / r0["Ej"] - 1
        dJtot = r["Jj"] / r0["Jj"] - 1
        dEfus = (r["Ej"] - r["cortes"][100.0][0]) / (r0["Ej"] - r0["cortes"][100.0][0]) - 1
        dEins = r["cortes"][500.0][0] / r0["cortes"][500.0][0] - 1
        dJins = r["cortes"][2000.0][1] / r0["cortes"][2000.0][1] - 1
        # energia e J acumulados nos mesmos ultimos 9000 M (janela comum alinhada no pico)
        Tc = min(-r["t0"], -r0["t0"]) - 1.0
        Ec = np.sum(r["dE"][r["t"] > -Tc]) * r["dt"] / (np.sum(r0["dE"][r0["t"] > -Tc]) * r0["dt"]) - 1
        Jc = np.sum(r["dJ"][r["t"] > -Tc]) * r["dt"] / (np.sum(r0["dJ"][r0["t"] > -Tc]) * r0["dt"]) - 1
        log("  l0 = %.2f pi: duracao %+.1f M ; E_jan %+.2e (fusao t > -100 M: %+.2e ; inspiral t < -500 M: %+.2e) ; J_jan %+.2e (t < -2000 M: %+.2e) ; |h22| pico %+.1e"
            % (l0 / np.pi, r["t0"] - r0["t0"], dEtot, dEfus, dEins, dJtot, dJins, r["a22"] / r0["a22"] - 1))
        log("       mesma janela alinhada no pico (ultimos %.0f M): E %+.2e ; J %+.2e" % (Tc, Ec, Jc))
    log()
    r0, r1 = res[(0.05, 0.0)], res[(0.05, np.pi)]
    log("Referencia e0 = 0.05: l0 = pi x 0: duracao %+.1f M ; E_jan %+.2e ; J_jan %+.2e ; |h22| pico %+.1e"
        % (r1["t0"] - r0["t0"], r1["Ej"] / r0["Ej"] - 1, r1["Jj"] / r0["Jj"] - 1, r1["a22"] / r0["a22"] - 1))
    r0, r1 = res[(0.0, 0.0)], res[(0.2, 0.0)]
    log("Referencia e0 = 0.2 x 0 (l0 = 0): duracao %+.1f M ; E_jan %+.2e ; J_jan %+.2e ; |h22| pico %+.1e"
        % (r1["t0"] - r0["t0"], r1["Ej"] / r0["Ej"] - 1, r1["Jj"] / r0["Jj"] - 1, r1["a22"] / r0["a22"] - 1))
    with open(os.path.join(C.RES, "rev_R4_anomalia_origem.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
