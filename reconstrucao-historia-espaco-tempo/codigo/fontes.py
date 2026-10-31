"""Fontes hipoteticas para a etapa 3 (gravidade linearizada + memoria em ordem quadratica).

Fonte de referencia: um corpo girante isolado (sem recuo) que parte do repouso,
gira acelerando (chirp) e volta ao repouso. Os modos de radiacao sao

    h_lm(u) = c_lm * d^2/du^2 [ a(u) exp(-i m phi(u)) ],

com m par (simetria de rotacao de 180 graus: nenhum fluxo de momento linear no
plano) e h_{l,-m} = (-1)^l conj(h_lm) (simetria equatorial: nenhum fluxo em z).
Como h_lm e a segunda derivada de uma funcao que se anula nas pontas, int h du = 0
e int u h du = 0: a fonte comeca e termina parada, sem memoria linear.

As outras historias sao obtidas da referencia por operacoes que, pelo teorema da
etapa 3, preservam as quatro memorias (partes nulas) ou as preservam aproximadamente:
  filtro de fase comum (passa-tudo) -> anti-chirp e "dispersao" aleatoria (exato)
  rotacao de dualidade constante (exato)
  divisao em duas explosoes de meia potencia (aproximado; exato no limite sem sobreposicao)
"""
import numpy as np

LISTA = [(2, 2), (2, -2), (3, 2), (3, -2), (4, 4), (4, -4), (4, 2), (4, -2)]
# amplitudes relativas e fases dos modos m > 0 (os de m < 0 saem da simetria)
# h_lm ~ -c_lm m^2 phidot^2 a e^{-i m phi}: c_lm = razao * 4/m^2 da |h_lm|/|h_22| no pico
# razoes tipicas de uma binaria de massas desiguais: 0.05 (3,2), 0.08 (4,4), 0.02 (4,2)
COEF = {(2, 2): 1.0, (3, 2): 0.05 * np.exp(0.6j), (4, 4): 0.02 * np.exp(-0.4j), (4, 2): 0.02 * np.exp(1.1j)}


def grade_tempo(L=16384.0, n=2 ** 15):
    du = L / n
    u = (np.arange(n) - n // 2) * du
    return u, du


def omegas(n, du):
    return 2 * np.pi * np.fft.fftfreq(n, d=du)


def derivar(f, du, ordem=1):
    w = omegas(f.shape[0], du)
    fator = (1j * w) ** ordem
    F = np.fft.fft(f, axis=0)
    if F.ndim == 2:
        fator = fator[:, None]
    return np.fft.ifft(fator * F, axis=0)


def envelope(u, u0, largura, p=8):
    """Super-gaussiana: na pratica de suporte compacto (cai a ~1e-300 em 2 larguras)."""
    return np.exp(-np.abs((u - u0) / largura) ** p)


def fonte_girante(u, du, Om0=0.03, Om1=0.15, u0=0.0, dur=1600.0, amp22=0.3):
    """Corpo girante com velocidade angular subindo linearmente de Om0 a Om1 (chirp)."""
    s = (u - u0) / dur                                # -1/2 .. 1/2 no miolo
    Om = Om0 + (Om1 - Om0) * (s + 0.5)
    phi = (Om0 + 0.5 * (Om1 - Om0)) * (u - u0) + 0.5 * (Om1 - Om0) / dur * (u - u0) ** 2
    a = envelope(u, u0, 0.62 * dur)
    modos = {}
    for (l, m), c in COEF.items():
        Q = a * np.exp(-1j * m * phi)
        h = derivar(Q, du, 2)
        modos[(l, m)] = c * h
        modos[(l, -m)] = (-1) ** l * np.conj(c * h)
    H = np.stack([modos[k] for k in LISTA], axis=1)
    escala = amp22 / np.max(np.abs(H[:, 0]))
    return H * escala, Om


def aplicar_fase(H, fase):
    """Filtro de fase comum a todos os modos: h~_lm(w) -> exp(i fase(w)) h~_lm(w)."""
    F = np.fft.fft(H, axis=0)
    return np.fft.ifft(np.exp(1j * fase)[:, None] * F, axis=0)


def fase_antichirp(n, du, Om0=0.03, Om1=0.15, dur=1600.0, u0=0.0):
    """Fase impar e suave que inverte a varredura de frequencia dos modos com m = 2.

    Convencao fisica h~(w) = int h e^{+iwu} du (o modo 22 ~ e^{-2i phi} tem w > 0).
    No modo 22 a frequencia e w = 2 phidot(u), logo o atraso de grupo e
    u(w) = u0 + (w/2 - Om_med)/phiddot. O filtro soma -2 (u(w) - u0), o que reflete a
    varredura em torno de u0:  fase(w) = -(w^2/2 - 2 Om_med w)/phiddot  para w > 0,
    estendida como funcao impar (nucleo real: o mesmo filtro em h_+ e h_x).
    Devolve o multiplicador na convencao do numpy (fft ~ int f e^{-iwt}): exp(-i fase(w)).
    """
    w = omegas(n, du)
    Om_med = 0.5 * (Om0 + Om1)
    phidd = (Om1 - Om0) / dur
    a = np.abs(w)
    fase_fis = -np.sign(w) * (a ** 2 / 2 - 2 * Om_med * a) / phidd
    return -fase_fis


def fase_aleatoria(n, du, rng, tau=150.0, termos=6, forca=5.0):
    """Fase impar e suave: fase(w) = sum_j c_j sin(j w tau)."""
    w = omegas(n, du)
    c = rng.normal(size=termos) * forca / np.arange(1, termos + 1)
    return sum(cj * np.sin((j + 1) * w * tau) for j, cj in enumerate(c))


def deslocar(H, du, T):
    """H(u - T) por translacao espectral (tambem um filtro de fase, fase = -w T... em numpy +)."""
    w = omegas(H.shape[0], du)
    return aplicar_fase(H, -w * T)


def dividir(H, du, T):
    """Duas explosoes de meia potencia em u = -T e u = +T."""
    return (deslocar(H, du, T) + deslocar(H, du, -T)) / np.sqrt(2)


def dualidade(H, alfa):
    """Rotacao de dualidade constante: mistura momentos de massa e de corrente."""
    return np.exp(1j * alfa) * H
