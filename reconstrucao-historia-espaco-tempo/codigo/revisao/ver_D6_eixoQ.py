"""Verificacao adversarial D6 (L11): os zeros da memoria de deslocamento seguem e_Q e nao J_rad / chi_f?

Populacao nova (semente 99, 10 sistemas, q em [1, 4], |chi| em [0.3, 0.8], direcoes isotropas) mais dois casos
extremos (q = 4, chi_perp = 0.8 nos dois; q = 1, spins antiparalelos no plano grandes).
Caminho independente do exp34 para:
  - tensor A do l = 2 (ajuste de n.A.n a Re sum Phi_2m Y_2m com scipy.special.sph_harm_y);
  - zeros do campo completo (l <= 8) por minimos de |h| numa rede de Fibonacci + Nelder-Mead e indices por laco;
  - e_Q com tres pesos: |hdot|^2 (como no exp34), so os modos (2, +-2) e peso uniforme no tempo;
  - J_rad (do exp33_comum.memorias7), chi_f (surfinBH), L_i.
Saida: impressa (redirecionada para resultados/ver_D6_eixoQ.txt).
"""
import os
import sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import lal
from scipy.optimize import minimize
from scipy.special import sph_harm_y

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import exp33_comum as C
import observaveis as O
from harmonicos import sYlm, ethb2_de_escalar

F0 = C.F0_PADRAO


def ang_eixo(a, b):
    c = abs(np.dot(a, b)) / np.linalg.norm(a) / np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def tensor_lal(pot2):
    rng = np.random.default_rng(5)
    n = rng.normal(size=(60, 3))
    n /= np.linalg.norm(n, axis=1)[:, None]
    f = []
    for v in n:
        th, ph = np.arccos(v[2]), np.arctan2(v[1], v[0])
        f.append(np.real(sum(pot2.get(m, 0j) * sph_harm_y(2, m, th, ph) for m in range(-2, 3))))
    # A simetrico sem traco: 5 parametros
    Xm = np.stack([n[:, 0] ** 2 - n[:, 2] ** 2, n[:, 1] ** 2 - n[:, 2] ** 2, 2 * n[:, 0] * n[:, 1],
                   2 * n[:, 0] * n[:, 2], 2 * n[:, 1] * n[:, 2]], axis=1)
    c, res, *_ = np.linalg.lstsq(Xm, np.array(f), rcond=None)
    A = np.array([[c[0], c[2], c[3]], [c[2], c[1], c[4]], [c[3], c[4], -c[0] - c[1]]])
    return A


def campo_z(mem_tipo, n, u, w):
    """z = P(u,u) - P(w,w) + 2i P(u,w) com P = h+ e+ + hx ex, h = sum a sY(-2)."""
    n = np.atleast_2d(n)
    th = np.arccos(np.clip(n[:, 2], -1, 1))
    ph = np.arctan2(n[:, 1], n[:, 0])
    h = sum(c * sYlm(-2, l, m, th, ph) for (l, m), c in mem_tipo.items() if l >= 2 and c != 0)
    hp, hx = h.real, -h.imag
    et = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], 1)
    ep = np.stack([-np.sin(ph), np.cos(ph), 0 * ph], 1)
    cu_t, cu_p = et @ u, ep @ u
    cw_t, cw_p = et @ w, ep @ w
    # P(a,b) = hp (a_t b_t - a_p b_p) + hx (a_t b_p + a_p b_t)
    Puu = hp * (cu_t ** 2 - cu_p ** 2) + hx * 2 * cu_t * cu_p
    Pww = hp * (cw_t ** 2 - cw_p ** 2) + hx * 2 * cw_t * cw_p
    Puw = hp * (cu_t * cw_t - cu_p * cw_p) + hx * (cu_t * cw_p + cu_p * cw_t)
    return Puu - Pww + 2j * Puw, np.abs(h)


def base(n0):
    a = np.array([1.0, 0, 0]) if abs(n0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, n0)
    u /= np.linalg.norm(u)
    return u, np.cross(n0, u)


def zeros_campo(mem_tipo, N=30000):
    i = np.arange(N) + 0.5
    ph = np.pi * (1 + 5 ** 0.5) * i + 0.37
    ct = 1 - 2 * i / N
    n = np.stack([np.sqrt(1 - ct ** 2) * np.cos(ph), np.sqrt(1 - ct ** 2) * np.sin(ph), ct], 1)
    th, phi = np.arccos(ct), np.arctan2(n[:, 1], n[:, 0])
    a = np.abs(sum(c * sYlm(-2, l, m, th, phi) for (l, m), c in mem_tipo.items() if l >= 2 and c != 0))
    from scipy.spatial import cKDTree
    _, nb = cKDTree(n).query(n, k=13)
    cand = [n[j] for j in range(N) if a[j] <= a[nb[j, 1:]].min()]
    amax = a.max()
    achados = []
    for p0 in cand:
        u, w = base(p0)

        def f(c):
            m = p0 + c[0] * u + c[1] * w
            m = m / np.linalg.norm(m)
            return campo_z(mem_tipo, m[None], u, w)[1][0] / amax
        r = minimize(f, [0, 0], method="Nelder-Mead", options=dict(xatol=1e-12, fatol=1e-16, maxiter=3000))
        if r.fun > 1e-6:
            continue
        m = p0 + r.x[0] * u + r.x[1] * w
        m /= np.linalg.norm(m)
        if any(np.arccos(np.clip(m @ y, -1, 1)) < 1e-4 for y in achados):
            continue
        achados.append(m)
    out = []
    for m in achados:
        dmin = min([np.arccos(np.clip(m @ y, -1, 1)) for y in achados if y is not m] + [0.1])
        u, w = base(m)
        rr = 0.25 * dmin
        tt = np.linspace(0, 2 * np.pi, 300, endpoint=False)
        pts = np.cos(rr) * m + np.sin(rr) * (np.cos(tt)[:, None] * u + np.sin(tt)[:, None] * w)
        z, _ = campo_z(mem_tipo, pts, u, w)
        out.append((m, float(np.sum(np.angle(np.roll(z, -1) / z)) / (4 * np.pi))))
    return out


def analisar(nome, q, cA, cB, fit):
    t, h, dyn = C.gerar7(q, cA, cB, f_ref=F0)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, aux = C.memorias7(q, t, h, dyn, ti)
    w = O.pesos_janela(t, ti)
    dt = t[1] - t[0]
    zc = np.array([C.eixo_copr(dyn["q_copr"][:, k]) for k in range(len(t))])
    L_all = sum(np.abs(np.gradient(h[k], dt)) ** 2 for k in C.MODOS)
    L_22 = sum(np.abs(np.gradient(h[k], dt)) ** 2 for k in [(2, 2), (2, -2)])
    eixos = {}
    for rot, peso in (("e_Q", L_all), ("e_Q22", L_22), ("e_unif", np.ones_like(L_all))):
        Q = np.einsum("k,ki,kj->ij", w * peso, zc, zc)
        eixos[rot] = np.linalg.eigh(Q)[1][:, 2]
    del t, h, dyn, zc
    mf, chif, vf, *_ = fit.all(q, list(cA), list(cB), omega0=np.pi * F0, omega_switch_IG=0.5 * np.pi * F0,
                               allow_extrap=True)
    D = mem["deslocamento"]
    pot2 = {m: 2 * D[(2, m)] / ethb2_de_escalar(2) for m in range(-2, 3)}
    A = tensor_lal(pot2)
    lam, E = np.linalg.eigh(A)
    # eixo distinto: autovalor mais afastado da media dos outros dois
    k = 2 if (lam[2] - lam[1]) > (lam[1] - lam[0]) else 0
    e1 = E[:, k]
    eixos.update(J_rad=aux["J_rad"], chi_f=np.asarray(chif), L_i=aux["Lhat_i"], L_pico=aux["Lhat_pico"])
    angs = {kk: ang_eixo(e1, v) for kk, v in eixos.items()}
    zz = zeros_campo(D)
    perto = [(m, i) for m, i in zz if abs(m @ e1) > np.cos(np.radians(25))]
    meia = (0.5 * np.degrees(np.arccos(np.clip(perto[0][0] @ perto[1][0], -1, 1)))
            if len([1 for m, i in perto if m @ e1 > 0]) == 2 else np.nan)
    zs = zeros_campo(mem["spin"])
    print("%s q %.2f chiA %s chiB %s" % (nome, q, np.round(cA, 2).tolist(), np.round(cB, 2).tolist()))
    print("   autovalores de A %s ; eixo distinto = autovetor %d" % (np.round(lam, 5), k))
    print("   angulo e1 com: " + " ; ".join("%s %.2f" % (kk, v) for kk, v in angs.items()))
    print("   desl: %d zeros, indices %s, soma %.2f ; meia abertura do par (+e1) %.2f graus ; spin: %d zeros, indices %s, soma %.2f"
          % (len(zz), sorted(round(i, 2) for _, i in zz), sum(i for _, i in zz), meia, len(zs),
             sorted(round(i, 2) for _, i in zs), sum(i for _, i in zs)), flush=True)
    return angs


def main():
    import surfinBH
    fit = surfinBH.LoadFits("NRSur7dq4Remnant")
    rng = np.random.default_rng(99)
    sis = []
    for k in range(10):
        q = rng.uniform(1.0, 4.0)
        vs = []
        for _ in range(2):
            u = rng.normal(size=3)
            u /= np.linalg.norm(u)
            vs.append(tuple(rng.uniform(0.3, 0.8) * u))
        sis.append(("S%02d" % k, q, vs[0], vs[1]))
    sis.append(("X1 q4 dois spins no plano 0.8", 4.0, (0.8, 0.0, 0.0), (0.0, 0.8, 0.0)))
    sis.append(("X2 q1 antiparalelos no plano", 1.0, (0.0, 0.8, 0.0), (0.0, -0.8, 0.0)))
    sis.append(("X3 q2 spin A quase antialinhado", 2.0, (0.4, 0.0, -0.69), (0.0, 0.0, 0.0001)))
    todos = []
    for nome, q, a, b in sis:
        try:
            todos.append(analisar(nome, q, a, b, fit))
        except Exception as e:
            print(nome, "falhou:", e)
    print("Resumo (%d sistemas): mediana / maximo do angulo de e1 com cada eixo" % len(todos))
    for kk in todos[0]:
        v = np.array([d[kk] for d in todos])
        print("   %-7s mediana %.2f max %.2f" % (kk, np.median(v), v.max()))


if __name__ == "__main__":
    main()
