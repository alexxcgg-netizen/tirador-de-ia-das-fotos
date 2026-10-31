"""Harmonicos esfericos com peso de spin, operadores eth e quadratura na esfera.

Convencoes (as mesmas de Mitman et al. 2020, PRD 102, 104007, e do catalogo SXS):

    eth  sY_lm = +sqrt((l-s)(l+s+1)) (s+1)Y_lm
    ethb sY_lm = -sqrt((l+s)(l-s+1)) (s-1)Y_lm
    conj(sY_lm) = (-1)^(s+m) (-s)Y_l(-m)

A deformacao e h = (1/2) qbar^A qbar^B C_AB = sum h_lm (-2)Y_lm, com h = h_+ - i h_x
(h aqui e r vezes a deformacao, unidades G = c = 1).

Formula explicita de Goldberg et al. (1967), escrita sem cotangentes para nao
dividir por zero nos polos.
"""
from functools import lru_cache
from math import comb, factorial, sqrt, pi

import numpy as np


def sYlm(s, l, m, theta, phi):
    """Harmonico esferico com peso de spin s, avaliado em arrays theta, phi."""
    if l < abs(s) or abs(m) > l:
        return np.zeros(np.broadcast(theta, phi).shape, dtype=complex)
    pref = (-1) ** m * sqrt(factorial(l + m) * factorial(l - m) * (2 * l + 1)
                            / (4 * pi * factorial(l + s) * factorial(l - s)))
    st = np.sin(np.asarray(theta) / 2.0)
    ct = np.cos(np.asarray(theta) / 2.0)
    tot = np.zeros(np.broadcast(theta, phi).shape, dtype=float)
    for r in range(0, l - s + 1):
        k = r + s - m
        if k < 0 or k > l + s:
            continue
        c = comb(l - s, r) * comb(l + s, k) * (-1) ** (l - r - s)
        p = 2 * r + s - m          # potencia de cot(theta/2)
        tot = tot + c * st ** (2 * l - p) * ct ** p
    return pref * tot * np.exp(1j * m * np.asarray(phi))


def eth_fator(s, l):
    """Autovalor de eth: sY_lm -> fator * (s+1)Y_lm."""
    v = (l - s) * (l + s + 1)
    return sqrt(v) if v > 0 else 0.0


def ethb_fator(s, l):
    """Autovalor de ethbar: sY_lm -> fator * (s-1)Y_lm."""
    v = (l + s) * (l - s + 1)
    return -sqrt(v) if v > 0 else 0.0


def modos(lmax, lmin=0):
    """Lista ordenada de (l, m)."""
    return [(l, m) for l in range(lmin, lmax + 1) for m in range(-l, l + 1)]


class Grade:
    """Grade de Gauss-Legendre em cos(theta) x pontos uniformes em phi.

    Integra exatamente produtos de harmonicos cujo grau total em l seja < 2*ntheta
    e cuja soma de |m| seja < nphi.
    """

    def __init__(self, ntheta=40, nphi=80):
        x, w = np.polynomial.legendre.leggauss(ntheta)
        self.theta1 = np.arccos(x)
        self.phi1 = 2 * pi * np.arange(nphi) / nphi
        self.theta, self.phi = np.meshgrid(self.theta1, self.phi1, indexing="ij")
        self.peso = (w[:, None] * np.full(nphi, 2 * pi / nphi)[None, :])
        self.shape = self.theta.shape
        self._cache = {}

    def Y(self, s, l, m):
        chave = (s, l, m)
        if chave not in self._cache:
            self._cache[chave] = sYlm(s, l, m, self.theta, self.phi)
        return self._cache[chave]

    def matriz_Y(self, s, lista):
        """Matriz (nmodos, npontos) com sY_lm na grade."""
        return np.array([self.Y(s, l, m).ravel() for (l, m) in lista])

    def projetar(self, f, s, lmax, lmin=None):
        """Coeficientes f_lm = int f conj(sY_lm) dOmega. f pode ter eixo extra no inicio."""
        if lmin is None:
            lmin = abs(s)
        lista = modos(lmax, lmin)
        Ym = self.matriz_Y(s, lista)
        fw = (np.asarray(f) * self.peso).reshape(np.asarray(f).shape[:-2] + (-1,))
        return lista, fw @ Ym.conj().T

    def sintetizar(self, coef, s, lista):
        """Campo na grade a partir de coeficientes coef[..., k] nos modos lista."""
        Ym = self.matriz_Y(s, lista)
        out = np.asarray(coef) @ Ym
        return out.reshape(np.asarray(coef).shape[:-1] + self.shape)

    def integrar(self, f):
        return np.sum(np.asarray(f) * self.peso, axis=(-2, -1))


@lru_cache(maxsize=None)
def _fatorial_razao(l):
    """(l+2)!/(l-2)! = (l-1) l (l+1) (l+2)."""
    return (l - 1) * l * (l + 1) * (l + 2)


def D2(l):
    """Laplaciano na esfera unitaria em spin 0: -l(l+1)."""
    return -l * (l + 1)


def Dfrak(l):
    """Operador de Mitman et al.: (1/8) D^2 (D^2 + 2) = (1/8)(l-1)l(l+1)(l+2)."""
    return _fatorial_razao(l) / 8.0


def ethb2_de_escalar(l):
    """ethbar^2 aplicado a 0Y_lm = sqrt((l+2)!/(l-2)!) (-2)Y_lm."""
    return sqrt(_fatorial_razao(l)) if l >= 2 else 0.0
