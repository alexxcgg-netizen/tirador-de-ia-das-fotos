"""Verificacao L00 (5): observaveis.comparar2 / snr2 com controles.

  (a) A contra A deslocado fora da grade: a mesma onda fisica (sistema A, todos os modos, iota 50, phi 0)
      amostrada em duas redes do substituto (t_desloc 0 e 0.37), desde 0.9 f0 (o taper de 0.5 s cai abaixo de
      10 Hz); B comeca 0.2 s depois e tem os tempos somados de 1.2345678e-3 s. Esperado: 1 - match ~ 0 e
      atraso = t_pico(B) - t_pico(A) (diferenca dos instantes de amostra do pico, que preparar usa no alinhamento).
  (b) dois sinais conhecidos com transformada analitica (seno-gaussianas com f, sigma, fase e t0 diferentes):
      match exato por integracao densa em frequencia (df = 1/64 Hz) e maximizacao continua no atraso.
  (c) degraus suaves (tipo memoria) a(t) = (D/2)(1 + tanh((t - t0)/tau)): transformada analitica
      -i pi tau (D/2) / sinh(pi^2 tau f); SNR e match exatos contra snr2 / comparar2 com fim='rampa'.
  (d) A contra q = 1.19 (o teste do D0) com sinais desde 0.9 f0 (taper fora da banda) contra desde t_i.
  (d') o mesmo com as duas ondas desde 0.7 f0 (referencia limpa);
  (e) atraso_rotulos (chave acrescentada na verificacao) com atrasos conhecidos e rotulos de inicio diferentes.
Saida: resultados/revisao/verif_L00_match.txt
"""
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize_scalar

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
import deteccao as Dt                                    # noqa: E402
import observaveis as O                                  # noqa: E402

SAIDA = os.path.join(AQUI, "..", "..", "resultados", "revisao", "verif_L00_match.txt")
L = []
T0 = time.time()
SA = dict(q=1.2, c1=0.3, c2=-0.2, M=65.0, D=400.0, iota=np.radians(50.0), F=10.0)


def log(s=""):
    print(s, flush=True)
    L.append(s)


def strain(q, desloc=0.0, inicio="aux"):
    t, h, ti = O.gerar_janela(q, SA["c1"], SA["c2"], SA["M"], SA["F"], t_desloc=desloc)
    ts, s = Dt.strain_observador(t, h, sorted(h.keys()), SA["M"], SA["D"], SA["iota"], 0.0)
    del h
    if inicio == "ti":                                    # comeca em t_i (primeiro ponto por spline)
        from scipy.interpolate import CubicSpline
        k = int(np.searchsorted(t, ti))
        j = np.arange(k - 4, k + 4)
        v0 = CubicSpline(t[j], s[j].real)(ti) + 1j * CubicSpline(t[j], s[j].imag)(ti)
        Ms = SA["M"] * Dt.MSUN_S
        return np.concatenate([[ti * Ms], ts[k:]]), np.concatenate([[v0], s[k:]])
    return ts, s


# ------------------------------------------------------------------ (a)
log("(a) A contra A em outra rede (t_desloc 0.37), B comecando 0.2 s depois e tempos + 1.2345678e-3 s; aLIGO, 10 Hz")
tA, sA = strain(SA["q"])
tB, sB = strain(SA["q"], desloc=0.37)
j = int(np.searchsorted(tB, tB[0] + 0.2))
tB, sB = tB[j:] + 1.2345678e-3, sB[j:]
log("  inicio A %.4f s, B %.4f s (antes do pico); f_22 no inicio ~ 0.9 x 10 Hz" % (tA[0], tB[0] - 1.2345678e-3))
esp = (tB[0] - tA[0]) - 1.2345678e-3        # B(t) = A(t - 1.2345678e-3): tau esperado entre as primeiras amostras
for kw in (dict(), dict(fim="nada"), dict(taper=0.0, fim="nada")):
    c = O.comparar2(tA, sA, tB, sB, "aLIGO", 10.0, **kw)
    log("  comparar2 %-30s 1 - match %.2e ; atraso %+.9e s (esperado %+.9e) ; atraso_rotulos %+.9e s (esperado"
        " +1.234567800e-03) ; SNR %.4f %.4f" % (str(kw), 1 - c["match"], c["atraso"], esp, c.get("atraso_rotulos", np.nan),
                                              c["snr_A"], c["snr_B"]))
cd = Dt.comparar(tA, sA, tB, sB, "aLIGO", 10.0)
log("  deteccao.comparar: 1 - match %.2e" % (1 - cd["+"]["match"]))
for psd in ("CE",):
    c = O.comparar2(tA, sA, tB, sB, psd, 10.0)
    log("  %s: comparar2 1 - match %.2e ; atraso %+.6e s" % (psd, 1 - c["match"], c["atraso"]))
del tA, sA, tB, sB
O.FRAC_INICIO = 0.7
tA, sA = strain(SA["q"])
tB, sB = strain(SA["q"], desloc=0.37)
O.FRAC_INICIO = 0.9
j = int(np.searchsorted(tB, tB[0] + 0.2))
tB, sB = tB[j:] + 1.2345678e-3, sB[j:]
for psd in ("aLIGO", "CE"):
    c = O.comparar2(tA, sA, tB, sB, psd, 10.0)
    log("  o mesmo com as ondas desde 0.7 f0 (taper em ~7 Hz), %-5s: 1 - match %.2e ; atraso_rotulos %+.9e s"
        % (psd, 1 - c["match"], c["atraso_rotulos"]))
del tA, sA, tB, sB
log("  (%.0f s)" % (time.time() - T0))


# ------------------------------------------------------------------ utilitarios exatos
def psd_densa(nome, fmax=2048.0, df=1 / 64.0, fmin=10.0):
    n = int(round(fmax / df)) + 1
    f = np.arange(n) * df
    S = Dt.psd_serie(nome, n, df, fmin)
    ok = np.isfinite(S) & (f >= fmin)
    return f[ok], S[ok], df


def match_exato(Af, Bf, f, S, df, tau0=0.0, largura=5e-3):
    aa = 4 * np.sum(np.abs(Af) ** 2 / S) * df
    bb = 4 * np.sum(np.abs(Bf) ** 2 / S) * df
    c = 4 * Af * np.conj(Bf) / S * df
    # varredura global do atraso: transformada inversa com zero padding (passo 1/(N df)), depois refino continuo
    N = 1 << 22
    z = np.abs(np.fft.ifft(np.concatenate([c, np.zeros(N - len(c))])) * N)
    taus = np.arange(N) / (N * df)
    taus[taus > 0.5 / df] -= 1 / df
    j = int(np.argmax(z))
    dtau = 1 / (N * df)
    r = minimize_scalar(lambda tt: -np.abs(np.sum(c * np.exp(2j * np.pi * f * tt))),
                        bounds=(taus[j] - dtau, taus[j] + dtau), method="bounded", options=dict(xatol=1e-13))
    return np.sqrt(aa), np.sqrt(bb), -r.fun / np.sqrt(aa * bb), float(r.x)


# ------------------------------------------------------------------ (b)
log("")
log("(b) seno-gaussianas a(t) = exp(-(t-t0)^2/2s^2) cos(2 pi f1 (t-t0) + p): match exato contra comparar2")
f, S, df = psd_densa("aLIGO")


def sg_t(tt, t0, s, f1, p, amp=1e-21):
    return amp * np.exp(-0.5 * ((tt - t0) / s) ** 2) * np.cos(2 * np.pi * f1 * (tt - t0) + p)


def sg_f(ff, t0, s, f1, p, amp=1e-21):
    g = s * np.sqrt(2 * np.pi) / 2
    return amp * g * (np.exp(1j * p) * np.exp(-2 * np.pi ** 2 * s ** 2 * (ff - f1) ** 2)
                      + np.exp(-1j * p) * np.exp(-2 * np.pi ** 2 * s ** 2 * (ff + f1) ** 2)) * np.exp(-2j * np.pi * ff * t0)


casos = [((2.0, 0.040, 80.0, 0.3), (2.0012345, 0.045, 83.0, 1.1)),
         ((2.0, 0.020, 150.0, 0.0), (2.0003141, 0.020, 150.0, 2.0)),
         ((2.0, 0.100, 40.0, 0.7), (1.9937, 0.080, 36.0, -0.4))]
for pa, pb in casos:
    ta = 0.0 + np.arange(int(4.0 * 16384)) / 16384.0                  # grade fina e nao alinhada com 1/4096
    tb = 0.37 / 16384 + np.arange(int(4.0 * 13000)) / 13000.0
    a, b = sg_t(ta, *pa) + 0j, sg_t(tb, *pb) + 0j
    rA, rB, mt, tau = match_exato(sg_f(f, *pa), sg_f(f, *pb), f, S, df, tau0=pb[0] - pa[0])
    c = O.comparar2(ta, a, tb, b, "aLIGO", 10.0, taper=0.0, fim="nada")
    # tau exato e na convencao a(t) ~ b(t - tau) com o mesmo t; comparar2 conta das primeiras amostras
    log("  a %s b %s: exato match %.8f SNR %.5f %.5f tau %+.7e ; comparar2 match %.8f SNR %.5f %.5f tau %+.7e"
        " (esperado %+.7e)" % (pa, pb, mt, rA, rB, tau, c["match"], c["snr_A"], c["snr_B"], c["atraso"],
                               tau + (tb[0] - ta[0])))
    cd = Dt.comparar(ta, a, tb, b, "aLIGO", 10.0)
    log("      dif. de match: comparar2 %+.1e ; deteccao.comparar %+.1e ; dif. relativa de SNR comparar2 %+.1e"
        % (c["match"] - mt, cd["+"]["match"] - mt, c["snr_A"] / rA - 1))
log("  (%.0f s)" % (time.time() - T0))

# ------------------------------------------------------------------ (c)
log("")
log("(c) degraus suaves (memoria) a(t) = (D/2)(1 + tanh((t - t0)/tau)), D = 1.6e-22: SNR e match exatos")


def st_t(tt, t0, tau, D=1.6e-22):
    return 0.5 * D * (1 + np.tanh((tt - t0) / tau))


def st_f(ff, t0, tau, D=1.6e-22):
    return 0.5 * D * (-1j * np.pi * tau / np.sinh(np.pi ** 2 * tau * ff)) * np.exp(-2j * np.pi * ff * t0)


for nome in ("aLIGO", "CE"):
    fN, SN, dfN = psd_densa(nome)
    for (pa, pb) in (((3.0, 0.003), (3.0004321, 0.0045)), ((3.0, 0.010), (3.0, 0.012))):
        ta = np.arange(int(3.3 * 16384)) / 16384.0
        tb = 0.37 / 16384 + np.arange(int(3.3 * 13000)) / 13000.0
        a, b = st_t(ta, *pa) + 0j, st_t(tb, *pb) + 0j
        rA, rB, mt, tau = match_exato(st_f(fN, *pa), st_f(fN, *pb), fN, SN, dfN, tau0=pb[0] - pa[0])
        c = O.comparar2(ta, a, tb, b, nome, 10.0)
        s2 = O.snr2(ta, a, nome, 10.0)
        s2n = O.snr2(ta, a, nome, 10.0, fim="nada")
        # mesma soma discreta de snr2 (grade df = fs/n com f >= fmin), com a transformada analitica
        nn = 1
        while nn < 2 * (int(round((ta[-1] - ta[0]) * 4096)) + int(12 * 4096)):
            nn *= 2
        fd = np.fft.rfftfreq(nn, 1 / 4096.0)
        Sd = Dt.psd_serie(nome, len(fd), fd[1], 10.0)
        okd = fd >= 10.0
        rdisc = np.sqrt(4 * np.sum(np.abs(st_f(fd[okd], *pa)) ** 2 / Sd[okd]) * fd[1])
        log("  %-5s a %s b %s: exato SNR_A %.6e match %.8f ; snr2 %.6e (dif. %+.1e ; sem rampa %+.1e ; contra a mesma"
            " soma discreta %+.1e) ; comparar2 match %.8f (dif. %+.1e) SNR_B %+.1e"
            % (nome, pa, pb, rA, mt, s2, s2 / rA - 1, s2n / rA - 1, s2 / rdisc - 1, c["match"], c["match"] - mt,
               c["snr_B"] / rB - 1))
log("  (%.0f s)" % (time.time() - T0))

# ------------------------------------------------------------------ (d)
log("")
log("(d) A contra q = 1.19, aLIGO e CE: sinais desde 0.9 f0 (taper fora da banda) contra desde t_i (teste do D0)")
for inicio in ("aux", "ti"):
    tA, sA = strain(SA["q"], inicio=inicio)
    tC, sC = strain(1.19, inicio=inicio)
    for nome in ("aLIGO", "CE"):
        c = O.comparar2(tA, sA, tC, sC, nome, 10.0)
        c2 = O.comparar2(tA, sA, tC, sC, nome, 10.0, taper=2.0)
        log("  inicio %-3s %-5s: comparar2 1 - match %.4e (taper 2 s: %.4e) ; SNR_A %.3f" % (
            inicio, nome, 1 - c["match"], 1 - c2["match"], c["snr_A"]))
    del tA, sA, tC, sC
log("  (%.0f s)" % (time.time() - T0))
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")

# ------------------------------------------------------------------ (d') referencia limpa desde 0.7 f0
L.append("")
L.append("(d') A contra q = 1.19 com as duas ondas desde 0.7 f0 (piso A-contra-A ~3e-8 aLIGO, ~3e-7 CE, ver (a))")
print(L[-1])
O.FRAC_INICIO = 0.7
tA, sA = strain(SA["q"])
tC, sC = strain(1.19)
O.FRAC_INICIO = 0.9
for nome in ("aLIGO", "CE"):
    c = O.comparar2(tA, sA, tC, sC, nome, 10.0)
    log("  desde 0.7 f0, %-5s: comparar2 1 - match %.4e ; SNR_A %.3f" % (nome, 1 - c["match"], c["snr_A"]))
del tA, sA, tC, sC
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")

# ------------------------------------------------------------------ (e) teste direto de atraso_rotulos
log("")
log("(e) atraso_rotulos com atrasos conhecidos: seno-gaussiana em grades de 16384 Hz (desde 0.1 s) e 13000 Hz (desde 0.4321 s)")


def gsg(tt):
    return 1e-21 * np.exp(-0.5 * ((tt - 2.0) / 0.04) ** 2) * np.cos(2 * np.pi * 80 * (tt - 2.0))


tA = 0.1 + np.arange(int(3.5 * 16384)) / 16384.0
tB = 0.4321 + np.arange(int(3.0 * 13000)) / 13000.0
for d in (0.0, 2.3456e-4, -1.111e-3):
    c = O.comparar2(tA, gsg(tA) + 0j, tB, gsg(tB - d) + 0j, "aLIGO", 10.0, taper=0.0, fim="nada")
    log("  delta verdadeiro %+.7e s: atraso_rotulos %+.7e s ; atraso (entre primeiras amostras) %+.7e s ; 1 - match %.1e"
        % (d, c["atraso_rotulos"], c["atraso"], 1 - c["match"]))
with open(SAIDA, "w") as fh:
    fh.write("\n".join(L) + "\n")
