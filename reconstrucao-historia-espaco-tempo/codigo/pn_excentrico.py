"""Inspiral excentrica em ordem newtoniana (quadrupolo) com evolucao orbital de Peters (1964).

Unidades: G = c = M = 1 (massa total), mu = eta.
  da/dt = -(64/5) eta a^-3 (1 + 73 e^2/24 + 37 e^4/96) / (1-e^2)^(7/2)
  de/dt = -(304/15) eta e a^-4 (1 + 121 e^2/304) / (1-e^2)^(5/2)
  dl/dt = n = a^(-3/2)                      (anomalia media; periastro fixo nesta ordem)
Orbita kepleriana: l = E - e sin E, r = a(1 - e cos E), anomalia verdadeira v.
Deformacao: h_ij = 2 d^2(eta x_i x_j)/dt^2 (r vezes h, quadrupolo), h = h_+ - i h_x na base (theta, phi),
projetada nos modos (-2)Y_2m por quadratura (so l = 2: (2,+-2), (2,+-1) = 0 em orbita plana, (2,0)).
Parada: semi-latus rectum p = a(1-e^2) = 6 + 2e (separatriz de Schwarzschild para particula teste).
Inicio: frequencia media de onda f = n/pi = M f_fis.
"""
import numpy as np
from scipy.integrate import solve_ivp

from harmonicos import Grade


def _rhs(t, y, eta):
    a, e, l = y
    e = max(e, 0.0)
    fa = (1 + 73 / 24 * e ** 2 + 37 / 96 * e ** 4) / (1 - e ** 2) ** 3.5
    fe = (1 + 121 / 304 * e ** 2) / (1 - e ** 2) ** 2.5
    return [-64 / 5 * eta / a ** 3 * fa, -304 / 15 * eta * e / a ** 4 * fe, a ** -1.5]


def _parada(t, y, eta):
    a, e, _ = y
    return a * (1 - e ** 2) - (6 + 2 * e)


_parada.terminal = True


def orbita(eta, e0, f0, dt=0.5):
    n0 = np.pi * f0
    a0 = n0 ** (-2 / 3)
    sol = solve_ivp(_rhs, [0, 1e9], [a0, e0, 0.0], args=(eta,), events=_parada, rtol=1e-11, atol=1e-12,
                    dense_output=True, max_step=200.0)
    # grade que termina exatamente na separatriz: com np.arange o ultimo passo (onde o fluxo e maximo)
    # entrava ou saia conforme os parametros, e as memorias pulavam ~1e-3 (objetivo nao suave)
    n = int(np.ceil(sol.t[-1] / dt)) + 1
    t = np.linspace(0, sol.t[-1], n)
    a, e, l = sol.sol(t)
    e = np.maximum(e, 0)
    E = l.copy()
    for _ in range(60):
        E = E - (E - e * np.sin(E) - l) / (1 - e * np.cos(E))
    r = a * (1 - e * np.cos(E))
    v = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    return t, r, np.unwrap(v), a, e


_proj = {}


def _projetores():
    if "P" in _proj:
        return _proj["P"]
    from harmonicos import sYlm
    g = Grade(16, 32)
    th, ph = g.theta, g.phi
    et = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    ep = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)])
    P = {}
    for m in (-2, -1, 0, 1, 2):
        Y = np.conj(sYlm(-2, 2, m, th, ph)) * g.peso
        M = np.zeros((3, 3), dtype=complex)
        for i in range(3):
            for j in range(3):
                hp = 0.5 * (et[i] * et[j] - ep[i] * ep[j])
                hx = 0.5 * (et[i] * ep[j] + ep[i] * et[j])
                M[i, j] = np.sum((hp - 1j * hx) * Y)
        P[(2, m)] = M
    _proj["P"] = P
    return P


def modos(eta, e0, f0, dt=0.5):
    """t, dict de modos l = 2 (todos os m), r, a, e."""
    t, r, phi, a, e = orbita(eta, e0, f0, dt)
    dt = t[1] - t[0]
    x = np.stack([r * np.cos(phi), r * np.sin(phi), np.zeros_like(r)], axis=1)
    I = eta * x[:, :, None] * x[:, None, :]
    Idd = np.empty_like(I)
    for i in range(3):
        for j in range(3):
            f = I[:, i, j]
            d2 = np.gradient(np.gradient(f, dt, edge_order=2), dt, edge_order=2)
            d2[2:-2] = (-f[4:] + 16 * f[3:-1] - 30 * f[2:-2] + 16 * f[1:-3] - f[:-4]) / (12 * dt ** 2)
            Idd[:, i, j] = d2
    P = _projetores()
    h = {k: 2 * np.einsum("tij,ij->t", Idd, M) for k, M in P.items()}
    return t, h, r, a, e
