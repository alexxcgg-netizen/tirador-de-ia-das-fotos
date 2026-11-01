"""exp34 (L11) - zeros do padrao de memoria no ceu (campo de spin -2) e seus indices; Poincare-Hopf.

Campo: h(n) = sum_lm a_lm (-2)Y_lm(n) (h = h_+ - i h_x). Como tensor tangente global, sem singularidade de base,
P = h_+ e_+ + h_x e_x, e_+ = th th - ph ph, e_x = th ph + ph th (convencao h = h_ij mbar^i mbar^j, m = (th + i ph)/sqrt2).
Num ponto n0 com base tangente fixa (u, w), u x w = n0, z = P(u,u) - P(w,w) + 2i P(u,w) = |h| e^{2 i psi} (psi =
angulo de polarizacao). Indice de linha de um zero = (enrolamento de arg z num laco anti-horario visto de fora)/2;
para campos de linhas em S^2 a soma dos indices e chi(S^2) = 2 (Poincare-Hopf; em termos de arg z, soma 4).

Ferramentas:
  tensor_P(mem_tipo, n)        tensor 3x3 em pontos n (N, 3)
  zeros(mem_tipo)              zeros por minimos locais de |h| numa rede + refinamento (least squares numa carta),
                               indices por laco; devolve lista de (n, indice, |h|/max|h|)
  indices_triangulos(mem_tipo) caminho independente: icosfera girada, enrolamento de arg z em cada triangulo
  eixos_opticos(A)             previsao [D] para um campo l = 2 puro: zeros nos "eixos opticos" do tensor A
                               (n = cos a e1 +- sin a e3, sin^2 a = (l2 - l3)/(l1 - l3), e antipodas), indice +1/2 cada
Teste executavel: python exp34_zeros.py -> resultados/exp34_zeros_testes.txt
"""
import os
import sys

import numpy as np
from scipy.optimize import least_squares

from harmonicos import sYlm

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")


def _base_esferica(n):
    th = np.arccos(np.clip(n[:, 2], -1, 1))
    ph = np.arctan2(n[:, 1], n[:, 0])
    eth = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], axis=1)
    eph = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)], axis=1)
    return th, ph, eth, eph


def campo_h(mem_tipo, n, s=-2):
    n = np.atleast_2d(n)
    th = np.arccos(np.clip(n[:, 2], -1, 1))
    ph = np.arctan2(n[:, 1], n[:, 0])
    z = np.zeros(len(n), dtype=complex)
    for (l, m), c in mem_tipo.items():
        if l >= abs(s) and c != 0:
            z += c * sYlm(s, l, m, th, ph)
    return z


def tensor_P(mem_tipo, n):
    """Tensor de polarizacao P (N, 3, 3) = h_+ e_+ + h_x e_x nos pontos n (N, 3) (fora dos polos exatos)."""
    n = np.atleast_2d(n)
    h = campo_h(mem_tipo, n)
    hp, hx = h.real, -h.imag
    _, _, et, ep = _base_esferica(n)
    ep_ = np.einsum("ni,nj->nij", et, et) - np.einsum("ni,nj->nij", ep, ep)
    ex_ = np.einsum("ni,nj->nij", et, ep) + np.einsum("ni,nj->nij", ep, et)
    return hp[:, None, None] * ep_ + hx[:, None, None] * ex_


def base_tangente(n0):
    n0 = n0 / np.linalg.norm(n0)
    a = np.array([1.0, 0, 0]) if abs(n0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, n0)
    u /= np.linalg.norm(u)
    w = np.cross(n0, u)
    return u, w                      # u x w = n0


def z_local(mem_tipo, n, u, w):
    P = tensor_P(mem_tipo, n)
    puu = np.einsum("i,nij,j->n", u, P, u)
    pww = np.einsum("i,nij,j->n", w, P, w)
    puw = np.einsum("i,nij,j->n", u, P, w)
    return puu - pww + 2j * puw


def _girar_fora_do_polo(n):
    """Evita os polos exatos da base esferica (singular): pequena perturbacao."""
    n = np.array(n, float)
    k = np.abs(n[:, 2]) > 1 - 1e-14
    n[k, 0] += 1e-7
    return n / np.linalg.norm(n, axis=1)[:, None]


def indice_laco(mem_tipo, n0, raio=1e-3, npts=256):
    """Indice de linha (enrolamento de psi / 2pi) num laco de raio angular `raio` em torno de n0."""
    u, w = base_tangente(n0)
    a = np.linspace(0, 2 * np.pi, npts, endpoint=False)
    n = (np.cos(raio) * n0[None, :] + np.sin(raio) * (np.cos(a)[:, None] * u[None, :] + np.sin(a)[:, None] * w[None, :]))
    n = _girar_fora_do_polo(n)
    z = z_local(mem_tipo, n, u, w)
    d = np.angle(np.roll(z, -1) / z)
    return float(np.sum(d) / (2 * np.pi) / 2), float(np.min(np.abs(z)))


def fibonacci(N, rot=None):
    i = np.arange(N) + 0.5
    phi = np.arccos(1 - 2 * i / N)
    th = np.pi * (1 + 5 ** 0.5) * i
    n = np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], axis=1)
    return n if rot is None else n @ rot.T


def rotacao_aleatoria(seed=1):
    rng = np.random.default_rng(seed)
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    a, b, c, d = q
    return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                     [2 * (b * c + a * d), a * a - b * b + c * c - d * d, 2 * (c * d - a * b)],
                     [2 * (b * d - a * c), 2 * (c * d + a * b), a * a - b * b - c * c + d * d]])


def _minimos_locais_carta(mem_tipo, n0, raio, npts):
    """Minimos locais de |h| numa rede quadrada (npts x npts) da carta tangente em n0, ate o raio angular dado."""
    u, w = base_tangente(n0)
    x = np.linspace(-raio, raio, npts)
    X, Y = np.meshgrid(x, x, indexing="ij")
    n = n0[None, :] + X.ravel()[:, None] * u[None, :] + Y.ravel()[:, None] * w[None, :]
    n /= np.linalg.norm(n, axis=1)[:, None]
    a = np.abs(campo_h(mem_tipo, _girar_fora_do_polo(n))).reshape(npts, npts)
    out = []
    for i in range(1, npts - 1):
        for j in range(1, npts - 1):
            if a[i, j] <= a[i - 1:i + 2, j - 1:j + 2].min():
                out.append(n.reshape(npts, npts, 3)[i, j])
    return out


def zeros(mem_tipo, N=40000, viz=12, tol_rel=1e-7, raio_idx=None, extras=(), busca_local=True):
    """Zeros de h no ceu: minimos locais de |h| (rede de Fibonacci girada, N pontos, viz vizinhos), mais candidatos
    extras (por exemplo centros de triangulos com indice != 0), refinados por least_squares em (Re z, Im z) numa carta
    tangente. Se a soma dos indices nao der 2, faz busca local fina (raio 8 graus) em torno de cada zero achado.
    Devolve lista de dicts (n, indice, hmin_rel, raio_laco, dmin)."""
    from scipy.spatial import cKDTree
    pts = fibonacci(N, rotacao_aleatoria(7))
    a = np.abs(campo_h(mem_tipo, pts))
    amax = a.max()
    arv = cKDTree(pts)
    _, nb = arv.query(pts, k=viz + 1)
    cand = [pts[i] for i in range(N) if a[i] <= a[nb[i, 1:]].min()] + [np.asarray(e, float) for e in extras]
    achados = _refinar(mem_tipo, cand, amax, tol_rel, [])
    _indices(mem_tipo, achados, raio_idx)
    if busca_local and abs(sum(z["indice"] for z in achados) - 2) > 1e-6:
        novos = []
        for z in list(achados):
            novos += _minimos_locais_carta(mem_tipo, z["n"], np.radians(8.0), 161)
        achados = _refinar(mem_tipo, novos, amax, tol_rel, achados)
        _indices(mem_tipo, achados, raio_idx)
    return achados


def _indices(mem_tipo, achados, raio_idx):
    for z in achados:
        dmin = min([np.arccos(np.clip(z["n"] @ y["n"], -1, 1)) for y in achados if y is not z] + [1.0])
        rr = raio_idx or min(1e-2, 0.25 * dmin)
        z["indice"], _ = indice_laco(mem_tipo, z["n"], raio=rr)
        z["raio_laco"] = rr
        z["dmin"] = dmin


def _refinar(mem_tipo, cand, amax, tol_rel, achados):
    achados = list(achados)
    for n0 in cand:
        n0 = n0 / np.linalg.norm(n0)
        u, w = base_tangente(n0)

        def res(x):
            n = n0 + x[0] * u + x[1] * w
            n = n / np.linalg.norm(n)
            z = z_local(mem_tipo, _girar_fora_do_polo(n[None, :]), u, w)[0] / amax
            return [z.real, z.imag]
        r = least_squares(res, [0.0, 0.0], xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=200)
        n = n0 + r.x[0] * u + r.x[1] * w
        n /= np.linalg.norm(n)
        hm = abs(campo_h(mem_tipo, _girar_fora_do_polo(n[None, :]))[0]) / amax
        if hm > tol_rel:
            continue
        if any(np.arccos(np.clip(n @ z["n"], -1, 1)) < 1e-5 for z in achados):
            continue
        achados.append(dict(n=n, hmin_rel=hm))
    return achados


def icosfera(nivel):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7),
         (9, 8, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    for _ in range(nivel):
        meio = {}
        F2 = []

        def mid(i, j):
            k = (min(i, j), max(i, j))
            if k not in meio:
                v = V[i] + V[j]
                V.append(v / np.linalg.norm(v))
                meio[k] = len(V) - 1
            return meio[k]
        for (a, b, c) in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    return np.array(V), np.array(F)


def indices_triangulos(mem_tipo, nivel=6, seed=3):
    """Caminho independente: enrolamento de arg z (dobro do indice de linha) em cada triangulo de uma icosfera girada.
    Devolve (soma dos indices de linha, lista de (centro do triangulo, indice))."""
    V, F = icosfera(nivel)
    V = V @ rotacao_aleatoria(seed).T
    V = _girar_fora_do_polo(V)
    P = tensor_P(mem_tipo, V)
    tot = 0.0
    lista = []
    for f in F:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]
        N = a + b + c
        N /= np.linalg.norm(N)
        if np.cross(b - a, c - a) @ N < 0:
            f = (f[0], f[2], f[1])
        u, w = base_tangente(N)
        z = []
        for k in f:
            Pk = P[k]
            z.append(u @ Pk @ u - w @ Pk @ w + 2j * (u @ Pk @ w))
        z = np.array(z)
        enr = np.sum(np.angle(np.roll(z, -1) / z)) / (2 * np.pi)
        k = int(np.round(enr))
        if k != 0:
            lista.append((N, k / 2))
            tot += k / 2
    return tot, lista


def eixos_opticos(A):
    """Zeros previstos [D] do campo eletrico l = 2 puro com potencial Phi = n.A.n: eixos opticos do tensor A."""
    lam, E = np.linalg.eigh(A)
    l3, l2, l1 = lam
    e3, e2, e1 = E[:, 0], E[:, 1], E[:, 2]
    s2 = (l2 - l3) / (l1 - l3) if l1 > l3 else 0.0
    a = np.arcsin(np.sqrt(np.clip(s2, 0, 1)))
    n1 = np.cos(a) * e1 + np.sin(a) * e3
    n2 = np.cos(a) * e1 - np.sin(a) * e3
    return [n1, n2, -n1, -n2], a, e1


# ------------------------------------------------------------------ testes
def _pot_para_h(pot):
    """Coeficientes de h para um campo eletrico h = (1/2) ethb^2 Phi a partir de Phi_lm."""
    from harmonicos import ethb2_de_escalar
    return {(l, m): 0.5 * ethb2_de_escalar(l) * c for (l, m), c in pot.items() if l >= 2}


def _A_para_pot(A):
    """Coeficientes Phi_2m (base Y_2m) de Phi = n.A.n (A simetrico sem traco)."""
    from harmonicos import Grade
    g = Grade(12, 24)
    n = np.stack([np.sin(g.theta) * np.cos(g.phi), np.sin(g.theta) * np.sin(g.phi), np.cos(g.theta)], axis=-1)
    f = np.einsum("...i,ij,...j->...", n, A, n)
    lista, c = g.projetar(f, 0, 2, 0)
    return {lm: v for lm, v in zip(lista, c) if lm[0] == 2}


def testes():
    out = []

    def log(s):
        print(s, flush=True)
        out.append(s)
    log("exp34_zeros: testes do localizador de zeros e dos indices")
    # 1. eletrico axissimetrico l = 2: zeros duplos nos polos, indice +1
    pot = {(2, 0): 1.0 + 0j}
    hm = _pot_para_h(pot)
    zz = zeros(hm)
    tot, tri = indices_triangulos(hm)
    log("1. Phi = Y20 (eletrico, axissimetrico): zeros %s ; soma dos indices (laco) %.3f ; triangulos: soma %.2f, %d"
        " triangulos com indice != 0" % ([(np.round(z["n"], 4).tolist(), round(z["indice"], 3)) for z in zz],
                                          sum(z["indice"] for z in zz), tot, len(tri)))
    # 2. magnetico axissimetrico: h = -(i/2) ethb^2 Psi
    hb = {k: -1j * v for k, v in hm.items()}
    zz = zeros(hb)
    log("2. magnetico Psi = Y20: zeros %s ; soma %.3f" % ([(np.round(z["n"], 4).tolist(), round(z["indice"], 3)) for z in zz],
                                                         sum(z["indice"] for z in zz)))
    # 3. l = 2 triaxial: eixos opticos
    rng = np.random.default_rng(5)
    for k in range(3):
        M = rng.normal(size=(3, 3))
        A = M + M.T
        A -= np.trace(A) / 3 * np.eye(3)
        hm = _pot_para_h(_A_para_pot(A))
        zz = zeros(hm)
        prev, a, e1 = eixos_opticos(A)
        dif = max(min(np.degrees(np.arccos(np.clip(p @ z["n"], -1, 1))) for z in zz) for p in prev) if zz else np.nan
        tot, tri = indices_triangulos(hm)
        log("3.%d l = 2 triaxial (autovalores %s): %d zeros, indices %s, soma %.3f ; triangulos soma %.2f ; maior distancia"
            " zero previsto (eixos opticos, meia abertura %.2f graus) - achado: %.2e graus" % (
                k, np.round(np.linalg.eigvalsh(A), 3), len(zz), [round(z["indice"], 3) for z in zz],
                sum(z["indice"] for z in zz), tot, np.degrees(a), dif))
    # 4. l = 2 + l = 3 + l = 4 aleatorio (eletrico): zeros genericos
    for k in range(3):
        pot = {}
        for l in (2, 3, 4):
            for m in range(0, l + 1):
                c = rng.normal() + (1j * rng.normal() if m > 0 else 0)
                pot[(l, m)] = c / (l * l)
                if m > 0:
                    pot[(l, -m)] = (-1) ** m * np.conj(c) / (l * l)
        hm = _pot_para_h(pot)
        zz = zeros(hm)
        tot, tri = indices_triangulos(hm)
        log("4.%d eletrico l = 2..4 aleatorio: %d zeros, indices %s, soma %.3f ; triangulos: soma %.2f (%d)" % (
            k, len(zz), [round(z["indice"], 3) for z in zz], sum(z["indice"] for z in zz), tot, len(tri)))
        # mesmo campo com parte magnetica acrescentada (E + B)
        hb = dict(hm)
        for kk, v in _pot_para_h(pot).items():
            hb[kk] = hb[kk] + (-1j) * 0.7 * v * (1 if kk[1] % 2 == 0 else -1)
        zz = zeros(hb)
        tot, tri = indices_triangulos(hb)
        log("    E + B: %d zeros, indices %s, soma %.3f ; triangulos: soma %.2f" % (
            len(zz), [round(z["indice"], 3) for z in zz], sum(z["indice"] for z in zz), tot))
    with open(os.path.join(RES, "exp34_zeros_testes.txt"), "w") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    testes()
