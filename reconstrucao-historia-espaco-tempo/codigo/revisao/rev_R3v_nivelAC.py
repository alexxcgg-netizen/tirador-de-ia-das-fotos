"""Verificador R3v: checa os itens 1, 2, 4 e 7 do revisor R3 (NRHybSur3dq8_CCE, niveis A e C).

Caminho independente do usado por R3 (que usa partes_instantaneas): aqui as memorias de cada trecho de tempo saem
das matrizes de Gram do trecho (memorias_gram), com a derivada calculada na onda inteira e depois recortada.
  (1) helicidade (3,0) e giro (1,0) nos niveis A (so osc.) e C (osc. + m = 0): sao iguais?
  (2) spin (3,0): A e C por trechos de tempo [inicio, -3500], [-3500, -2500], [-2500, -100], [-100, fim];
      razao C/A da taxa em blocos de 1000 M (onde muda a razao: hibridizacao?)
  (4) lista de modos do _CCE; nivel A com o NRHybSur3dq8 (extrapolado) com e sem (3,1), (4,2)
  (7) janela de 50 M: memoria de CM (2,0) do codigo
Saida: resultados/revisao/rev_R3v_nivelAC.txt
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import binarias as B                                    # noqa: E402
from memorias import CalculadoraMemoria, gram           # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def spin_trecho(calc, H, Hd, sel, dt):
    """Im S_30 (nivel A) so com as amostras do trecho sel (Gram do trecho)."""
    m = calc.memorias_gram(*gram(H[sel], Hd[sel], dt))
    return m["spin"][(3, 0)].imag, m


if __name__ == "__main__":
    t00 = time.time()
    dt = 0.25
    c_osc, c_full = B.calculadoras()
    Losc = B.lista_osc()
    for q in (1.0, 8.0):
        t, h = B.gerar(q, 0.0, 0.0, f0=0.004, dt=dt)
        if q == 1.0:
            log("modos do NRHybSur3dq8_CCE: " + str(sorted(k for k in h if k[1] >= 0)))
        H = np.stack([h[k] for k in Losc], axis=1)
        Hd = B.derivada4(H, dt)
        Hf = np.concatenate([H, np.stack([h[k] for k in B.MODOS_M0], axis=1)], axis=1)
        Hfd = B.derivada4(Hf, dt)
        mA = c_osc.memorias_gram(*gram(H, Hd, dt))
        mF = c_full.memorias_gram(*gram(Hf, Hfd, dt))
        log("=== q = %.0f" % q)
        # (1) helicidade nos dois niveis
        for k in ((1, 0), (3, 0)):
            a, c = mA["helicidade_modos"][k], mF["helicidade_modos"][k]
            log("  (1) helicidade %s: so osc. = %.8f ; osc.+m=0 = %.8f ; dif. rel. = %.1e" % (k, a.real, c.real, abs(c - a) / abs(a)))
        memA, _ = B.memorias(q, 0.0, 0.0, f0=0.004, dt=dt, nivel="A", t=t, h=h)
        memC, _ = B.memorias(q, 0.0, 0.0, f0=0.004, dt=dt, nivel="C", t=t, h=h)
        gA, gC = memA["giroscopica"][(3, 0)].real, memC["giroscopica"][(3, 0)].real
        sA, sC = memA["spin"][(3, 0)].imag, memC["spin"][(3, 0)].imag
        hel = 0.25 * mA["helicidade_modos"][(3, 0)].real
        log("  (1) giro30 A = %.6f C = %.6f (dif %+.4f) ; termo de spin A = %.6f C = %.6f ; helicidade/4 = %.6f"
            % (gA, gC, (gA - gC) / gC, gA - hel, gC - 0.25 * mF["helicidade_modos"][(3, 0)].real, hel))
        log("      giro10 A = %.8f C = %.8f" % (memA["giroscopica"][(1, 0)].real, memC["giroscopica"][(1, 0)].real))
        log("      (dS/S_C) * termo_spin_C / giro_C = %+.5f ; observado %+.5f"
            % ((sA - sC) / sC * (gC - 0.25 * mF["helicidade_modos"][(3, 0)].real) / gC, (gA - gC) / gC))
        # (2) trechos
        norma = np.sum(np.abs(H) ** 2, axis=1)
        tp = t[np.argmax(norma)]
        log("  (2) spin30: A = %.6f C = %.6f (A-C)/C = %+.4f ; inicio em %.0f M do pico" % (sA, sC, (sA - sC) / sC, t[0] - tp))
        cortes = [-1e9, -3500, -2500, -100, 1e9]
        soma = 0.0
        for a, b in zip(cortes[:-1], cortes[1:]):
            sel = (t - tp > a) & (t - tp <= b)
            Sa, _ = spin_trecho(c_osc, H, Hd, sel, dt)
            Sc = np.sum(h[(3, 0)][sel]).imag * dt
            soma += Sa - Sc
            log("      trecho (%6.0f, %6.0f]: A = %.6f C = %.6f ; (A-C) = %+.6f = %+.2f%% de C total ; C/A - 1 = %+.4f"
                % (max(a, t[0] - tp), min(b, t[-1] - tp), Sa, Sc, Sa - Sc, 100 * (Sa - Sc) / sC, Sc / Sa - 1))
        log("      soma dos trechos (A-C)/C = %+.4f" % (soma / sC))
        # razao C/A em blocos de 1000 M (so inspiral)
        blocos = []
        b0 = t[0] - tp
        while b0 + 1000 < -100:
            sel = (t - tp > b0) & (t - tp <= b0 + 1000)
            Sa, _ = spin_trecho(c_osc, H, Hd, sel, dt)
            Sc = np.sum(h[(3, 0)][sel]).imag * dt
            blocos.append("%.0f:%.4f" % (b0 + 500, Sc / Sa))
            b0 += 1000
        log("      C/A por bloco de 1000 M (centro do bloco em M do pico: razao): " + " ".join(blocos))
        # (7) janela de 50 M
        if q == 1.0:
            n = 200
            m50, a50 = B.memorias(q, 0.0, 0.0, t=t[:n], h={k: v[:n] for k, v in h.items()}, nivel="A")
            eta = 0.25
            x0 = (np.pi * 0.004) ** (2 / 3)
            log("  (7) janela de %.0f M: desl20 = %.6f cm20 = %+.6f ; -(1/2) M_f favata(x0) = %+.6f ; desl20 so janela = %.2e"
                % (t[n - 1] - t[0], m50["deslocamento"][(2, 0)].real, m50["cm"][(2, 0)].real,
                   -0.5 * a50["M_f"] * B.favata_h20(x0, eta), m50["deslocamento"][(2, 0)].real - B.favata_h20(x0, eta)))
        del t, h, H, Hd, Hf, Hfd
        log("  (%.0f s)" % (time.time() - t00))

    # (4) NRHybSur3dq8 extrapolado com (3,1), (4,2)
    import gwsurrogate
    sur = gwsurrogate.LoadSurrogate("NRHybSur3dq8")
    L2 = Losc + [(3, 1), (3, -1), (4, 2), (4, -2)]
    c2 = CalculadoraMemoria(L2)
    for q in (1.0, 8.0):
        t, hh, _ = sur(q, [0, 0, 0], [0, 0, 0], dt=dt, f_low=0.004)
        hh = {(int(l), int(m)): np.asarray(v) for (l, m), v in hh.items()}
        if q == 1.0:
            log("modos do NRHybSur3dq8: " + str(sorted(k for k in hh if k[1] >= 0)))
        vals = []
        for L, c in ((Losc, c_osc), (L2, c2)):
            H = np.stack([hh[k] for k in L], axis=1)
            Hd = B.derivada4(H, dt)
            m = c.memorias_gram(*gram(H, Hd, dt))
            vals.append((m["spin"][(3, 0)].imag, m["deslocamento"][(2, 0)].real, m["giroscopica"][(3, 0)].real))
        v0, v1 = np.array(vals[0]), np.array(vals[1])
        log("  (4) q = %.0f NRHybSur3dq8 nivel A: spin30 %.6f -> %.6f (%+.2e) ; desl20 janela %+.2e ; giro30 %+.2e"
            % (q, v0[0], v1[0], v1[0] / v0[0] - 1, v1[1] / v0[1] - 1, v1[2] / v0[2] - 1))
        del t, hh
    log("  (%.0f s)" % (time.time() - t00))
    with open(os.path.join(SAIDA, "rev_R3v_nivelAC.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
