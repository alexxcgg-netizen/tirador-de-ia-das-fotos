"""Verificacao adversarial D5 (L08/L09): pesos angulares, zero do 3j, K(iota), frequencias de pares de QNM.

Independente de exp24_comum.taxas_m0 / exp31: usa a implementacao de memoria do pacote sxs (Mitman et al.,
sxs.waveforms.memory.J_E e J_J, eqs. 17b e 17d de 'Adding gravitational memory to waveform catalogs using BMS
balance laws') sobre sinais circulares sinteticos com Omega constante.
  - g^E_{2,p}/g^E_{2,22} e g^J_{3,p}/g^J_{3,22} para p = 21, 32, 33, 22x32  -> b_p
  - zero do 3j (3 3 2; 2 -2 0) por sympy
  - K(iota) do observador (formula do relatorio, harmonicos.sYlm) e K(40)/K(50), K(60)/K(50)
  - frequencias Re(omega_a - omega_b) de pares de QNM de mesmo m (pacote qnm) contra o polo 0.2175/M do exp32
"""
import os
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

out = []


def log(s=""):
    print(s, flush=True)
    out.append(s)


# ------------------------------------------------------------------ 1. 3j
import sympy as sp  # noqa: E402
from sympy.physics.wigner import wigner_3j  # noqa: E402

log("== 1. 3j")
for l in (2, 3, 4, 5):
    log("  (l l 2; 2 -2 0) l=%d: %s ; (l l 2; m -m 0) m=3: %s" % (
        l, sp.nsimplify(wigner_3j(l, l, 2, 2, -2, 0)), sp.nsimplify(wigner_3j(l, l, 2, 3, -3, 0)) if l >= 3 else "-"))

# ------------------------------------------------------------------ 2. pesos por sxs
import sxs  # noqa: E402
from sxs.waveforms.memory import J_E, J_J  # noqa: E402

log("")
log("== 2. Pesos angulares com sxs.waveforms.memory (J_E, J_J), sinais circulares, Omega = 0.05")
Om = 0.05
t = np.arange(0, 400.0, 0.1)
ellmax = 4
modos = [(l, m) for l in range(2, ellmax + 1) for m in range(-l, l + 1)]
idx = {lm: k for k, lm in enumerate(modos)}


def taxas(amps):
    """amps: dict (l,m>0) -> amplitude complexa c, h_lm = c e^{-i m Om t}, h_{l,-m} = (-1)^l conj(h_lm)."""
    data = np.zeros((len(t), len(modos)), dtype=complex)
    for (l, m), c in amps.items():
        hlm = c * np.exp(-1j * m * Om * t)
        data[:, idx[(l, m)]] = hlm
        data[:, idx[(l, -m)]] = (-1) ** l * np.conj(hlm)
    w = sxs.WaveformModes(data, time=t, time_axis=0, modes_axis=1, ell_min=2, ell_max=ellmax, spin_weight=-2)
    je = J_E(w)
    jj = J_J(w)
    k20 = je.index(2, 0)
    k30 = jj.index(3, 0)
    sl = slice(len(t) // 4, 3 * len(t) // 4)
    e2 = np.polyfit(t[sl], np.real(np.asarray(je)[sl, k20]), 1)[0]          # taxa de h20^mem
    e4 = np.polyfit(t[sl], np.real(np.asarray(je)[sl, je.index(4, 0)]), 1)[0]
    j3 = np.median(np.imag(np.asarray(jj)[sl, k30]))
    return e2, e4, j3


e2_22, e4_22, j3_22 = taxas({(2, 2): 1.0})
P22, H22 = (2 * Om) ** 2, 2 * Om
C_E = np.sqrt(30) / (42 * np.sqrt(np.pi))
C_J = np.sqrt(210) / (280 * np.sqrt(np.pi))
log("  so (2,2): taxa h20 / P = %.6f (C_E = %.6f) ; Im h30 / H = %.6f (C_J = %.6f) ; taxa h40/P = %.6f"
    % (e2_22 / P22, C_E, j3_22 / H22, C_J, e4_22 / P22))
gE22, gJ22 = e2_22 / (4 * Om ** 2), j3_22 / (2 * Om)
res = {}
for nome, amps, m, X in (("21", {(2, 1): 1.0}, 1, 1.0), ("33", {(3, 3): 1.0}, 3, 1.0), ("32", {(3, 2): 1.0}, 2, 1.0),
                         ("44", {(4, 4): 1.0}, 4, 1.0), ("43", {(4, 3): 1.0}, 3, 1.0)):
    e2, e4, j3 = taxas(amps)
    gE = e2 / (m ** 2 * Om ** 2 * X)
    gJ = j3 / (m * Om * X)
    res[nome] = (gE, gJ, m)
# par cruzado 22 x 32: X = Re(h22 conj h32); separa do quadratico por diferenca
for dl in (0.0, 0.7):
    c32 = 0.3 * np.exp(1j * dl)
    e2a, _, j3a = taxas({(2, 2): 1.0, (3, 2): c32})
    e2b, _, j3b = taxas({(3, 2): c32})
    X = np.real(1.0 * np.conj(c32))
    gE = (e2a - e2_22 - e2b) / (4 * Om ** 2 * X)
    gJ = (j3a - j3_22 - j3b) / (2 * Om * X)
    res["22x32 (fase %.1f)" % dl] = (gE, gJ, 2)
log("  pesos normalizados pelo (2,2) do proprio sxs e b_p = m^2 gE/(4 gE22) - m gJ/(2 gJ22):")
for nome, (gE, gJ, m) in res.items():
    b = m ** 2 * gE / (4 * gE22) - m * gJ / (2 * gJ22)
    log("   %-16s gE2/gE22 = %+.6f  gJ3/gJ22 = %+.6f  -> gE2 = %+.6f gJ3 = %+.6f (escala do relatorio)  b = %+.4f"
        % (nome, gE / gE22, gJ / gJ22, gE / gE22 * C_E, gJ / gJ22 * C_J, b))

# ------------------------------------------------------------------ 3. K(iota)
from harmonicos import sYlm  # noqa: E402

log("")
log("== 3. K(iota) = -C_J Y30 / (C_E Y20 + g4 Y40), (-2)Y_L0(iota)")
g4 = e4_22 / P22
log("  g4 (sxs) = %.6f (relatorio 0.000708)" % g4)


def Y(l, th):
    return np.real(complex(np.asarray(sYlm(-2, l, 0, th, 0.0)).ravel()[0]))


def K(io):
    th = np.radians(io)
    return -C_J * Y(3, th) / (C_E * Y(2, th) + g4 * Y(4, th))


for io in (40, 45, 55, 60):
    log("  K(%d)/K(50) - 1 = %+.4f" % (io, K(io) / K(50) - 1))
log("  K(50) = %.5f ; K(90) = %.3e ; K(10) = %.4f" % (K(50), K(90), K(10)))

# ------------------------------------------------------------------ 4. QNM: frequencias de pares
import qnm  # noqa: E402

log("")
log("== 4. Frequencias de pares de QNM (m' iguais), sistema A: M_f = 0.94971, chi_f = 0.71404 (exp32)")
Mf, chif = 0.94971, 0.71404
om = {}
for (l, m, n) in [(2, 2, 0), (2, 2, 1), (3, 2, 0), (3, 2, 1), (3, 3, 0), (4, 3, 0), (4, 4, 0), (5, 4, 0), (2, 1, 0),
                  (3, 1, 0), (4, 2, 0), (2, 0, 0)]:
    seq = qnm.modes_cache(s=-2, l=l, m=m, n=n)
    w, _, _ = seq(a=chif)
    om[(l, m, n)] = w / Mf
for k, v in om.items():
    log("  omega%d%d%d = %.4f %+.4fi" % (*k, v.real, v.imag))
pares = [((2, 2, 0), (3, 2, 0)), ((2, 2, 1), (3, 2, 0)), ((2, 2, 0), (3, 2, 1)), ((3, 3, 0), (4, 3, 0)),
         ((4, 4, 0), (5, 4, 0)), ((2, 1, 0), (3, 1, 0)), ((2, 2, 0), (4, 2, 0)), ((2, 2, 0), (2, 2, 1))]
for a, b in pares:
    d = om[b] - om[a]
    log("  par %s x %s: Re(dw) = %.4f ; Gamma_a + Gamma_b = %.4f" % (a, b, abs(d.real), -(om[a].imag + om[b].imag)))
log("  polo medido no exp32 (todos os modos, A): 0.2175 (oscilacao) / 0.2227 (amortecimento)")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ver_D5_pesos.txt"), "w") as f:
    f.write("\n".join(out) + "\n")
