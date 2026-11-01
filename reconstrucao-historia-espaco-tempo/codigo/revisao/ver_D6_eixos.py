"""Verificacao adversarial D6 (L11): zeros de campos eletricos/magneticos de peso -2 na esfera, por caminho
independente do exp34 (sem sYlm nem eth: tensor sem traco da hessiana covariante de um potencial polinomial).

Para Phi = F(n) restrito a S^2 com F homogeneo de grau k (harmonico => multipolo l = k puro):
   Hess_S Phi = P (d d F) P - k F P,   P = 1 - n n^T
   E = parte sem traco de Hess_S Phi  (campo eletrico, ~ ethb^2 Phi)
   B = rotacao de 45 graus de E (n x E) (campo magnetico)
Zeros: minimos de |E| (norma de Frobenius) a partir de uma rede, refinados; indice de linha pelo enrolamento de
arg z / 2 com z = E_uu - E_ww + 2 i E_uw num laco anti-horario (u x w = n).

Testes:
 T1 l = 2 triaxial aleatorio: zeros contra a formula sin^2 a = (l2 - l3)/(l1 - l3)
 T2 Y20 + eps * (perturbacao) para perturbacoes l = 2 m = 2, l = 2 m = 1, l = 3 m = 1, l = 3 m = 2, l = 4 m = 1,
    l = 4 m = 2, l = 3 m = 3, magnetico l = 3 m = 1: numero de zeros perto do polo norte, indices, maior distancia ao
    polo, expoente de escala com eps.
Saida: resultados/ver_D6_eixos.txt (somente impressa; o arquivo e escrito pelo chamador com tee)
"""
import numpy as np
import sympy as sp
from scipy.optimize import minimize

x, y, z = sp.symbols("x y z", real=True)
r2 = x * x + y * y + z * z
X = sp.Matrix([x, y, z])


def preparar(F):
    F = sp.expand(F)
    k = sp.Poly(F, x, y, z).total_degree()
    lap = sp.Poly(sp.expand(sum(sp.diff(F, v, 2) for v in (x, y, z))), x, y, z) if k > 1 else None
    assert lap is None or max([abs(float(c)) for c in lap.coeffs()] + [0.0]) < 1e-9, "nao harmonico"
    Hm = sp.hessian(F, (x, y, z))
    fF = sp.lambdify((x, y, z), F, "numpy")
    fH = sp.lambdify((x, y, z), Hm, "numpy")
    return fF, fH, k


def soma_campos(lista):
    """lista de (coef, F, tipo) com tipo 'E' ou 'B'."""
    prep = [(c, preparar(F), t) for c, F, t in lista]

    def campo(n):
        n = np.asarray(n, float)
        n = n / np.linalg.norm(n)
        P = np.eye(3) - np.outer(n, n)
        T = np.zeros((3, 3))
        for c, (fF, fH, k), t in prep:
            H = np.array(fH(*n), float)
            S = P @ H @ P - k * float(fF(*n)) * P
            E = S - 0.5 * np.trace(S) * P
            if t == "B":
                Jn = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])   # n x .
                E = Jn @ E
                E = 0.5 * (E + E.T)
                E = E - 0.5 * np.trace(E) * P
            T += c * E
        return T
    return campo


def base(n0):
    n0 = n0 / np.linalg.norm(n0)
    a = np.array([1.0, 0, 0]) if abs(n0[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, n0)
    u /= np.linalg.norm(u)
    return u, np.cross(n0, u)


def zloc(campo, n, u, w):
    T = campo(n)
    return u @ T @ u - w @ T @ w + 2j * (u @ T @ w)


def indice(campo, n0, raio, npts=400):
    u, w = base(n0)
    a = np.linspace(0, 2 * np.pi, npts, endpoint=False)
    zs = np.array([zloc(campo, np.cos(raio) * n0 + np.sin(raio) * (np.cos(t) * u + np.sin(t) * w), u, w) for t in a])
    return np.sum(np.angle(np.roll(zs, -1) / zs)) / (2 * np.pi) / 2


def achar_zeros(campo, n0=None, raio_busca=None, N=4000, tol=1e-9):
    """Zeros na esfera inteira (n0 None) ou numa calota em torno de n0."""
    rng = np.random.default_rng(1)
    if n0 is None:
        P = rng.normal(size=(N, 3))
    else:
        u, w = base(n0)
        rr = raio_busca * np.sqrt(rng.uniform(size=N))
        tt = rng.uniform(0, 2 * np.pi, N)
        P = np.cos(rr)[:, None] * n0 + np.sin(rr)[:, None] * (np.cos(tt)[:, None] * u + np.sin(tt)[:, None] * w)
    P /= np.linalg.norm(P, axis=1)[:, None]
    escala = max(np.linalg.norm(campo(p)) for p in P[:200])
    val = np.array([np.linalg.norm(campo(p)) for p in P])
    ordem = np.argsort(val)[:250]
    achados = []
    for i in ordem:
        p0 = P[i]
        u, w = base(p0)

        def f(c):
            n = p0 + c[0] * u + c[1] * w
            return np.linalg.norm(campo(n)) ** 2 / escala ** 2
        r = minimize(f, [0, 0], method="Nelder-Mead", options=dict(xatol=1e-13, fatol=1e-30, maxiter=4000))
        n = p0 + r.x[0] * u + r.x[1] * w
        n /= np.linalg.norm(n)
        if np.sqrt(f(r.x)) > tol:
            continue
        if n0 is not None and np.arccos(np.clip(n @ n0, -1, 1)) > raio_busca:
            continue
        if any(np.arccos(np.clip(n @ m, -1, 1)) < 1e-6 for m in achados):
            continue
        achados.append(n)
    out = []
    for n in achados:
        dmin = min([np.arccos(np.clip(n @ m, -1, 1)) for m in achados if m is not n] + [0.2])
        out.append((n, indice(campo, n, 0.25 * dmin)))
    return out


def T1():
    print("T1: l = 2 triaxial aleatorio (potencial n.A.n), zeros contra eixos opticos")
    rng = np.random.default_rng(42)
    for k in range(4):
        M = rng.normal(size=(3, 3))
        A = M + M.T
        A -= np.trace(A) / 3 * np.eye(3)
        F = sum(A[i, j] * X[i] * X[j] for i in range(3) for j in range(3))
        campo = soma_campos([(1.0, F, "E")])
        zz = achar_zeros(campo)
        lam, E = np.linalg.eigh(A)
        s2 = (lam[1] - lam[0]) / (lam[2] - lam[0])
        a = np.arcsin(np.sqrt(s2))
        prev = [np.cos(a) * E[:, 2] + sg * np.sin(a) * E[:, 0] for sg in (1, -1)]
        prev += [-p for p in prev]
        d = max(min(np.degrees(np.arccos(np.clip(abs(p @ n), -1, 1))) for n, _ in zz) for p in prev)
        # caso magnetico com o mesmo A
        zb = achar_zeros(soma_campos([(1.0, F, "B")]))
        db = max(min(np.degrees(np.arccos(np.clip(abs(p @ n), -1, 1))) for n, _ in zb) for p in prev)
        print("  caso %d: autovalores %s ; %d zeros, indices %s, soma %.3f ; meia abertura prevista %.3f graus ;"
              " desvio max %.1e graus ; magnetico: %d zeros, indices %s, desvio %.1e" % (
                  k, np.round(lam, 3), len(zz), [round(float(i), 3) for _, i in zz], sum(i for _, i in zz), np.degrees(a), d,
                  len(zb), [round(float(i), 3) for _, i in zb], db))


PERT = {
    "l2m2 (E)": (sp.re(sp.expand((x + sp.I * y) ** 2)), "E"),
    "l2m1 (E)": (sp.re(sp.expand((x + sp.I * y) * z)), "E"),
    "l3m1 (E)": (sp.re(sp.expand((x + sp.I * y) * (5 * z * z - r2))), "E"),
    "l3m2 (E)": (sp.re(sp.expand((x + sp.I * y) ** 2 * z)), "E"),
    "l3m3 (E)": (sp.re(sp.expand((x + sp.I * y) ** 3)), "E"),
    "l4m1 (E)": (sp.re(sp.expand((x + sp.I * y) * z * (7 * z * z - 3 * r2))), "E"),
    "l4m2 (E)": (sp.re(sp.expand((x + sp.I * y) ** 2 * (7 * z * z - r2))), "E"),
    "l3m1 (B)": (sp.re(sp.expand((x + sp.I * y) * (5 * z * z - r2))), "B"),
    "l2m1 (B)": (sp.re(sp.expand((x + sp.I * y) * z)), "B"),
}


def T2():
    print("T2: Y20 (potencial 3z^2 - r^2) + eps * perturbacao normalizada; zeros a ate 30 graus do polo norte")
    F0 = 3 * z * z - r2
    c0 = soma_campos([(1.0, F0, "E")])
    nz = np.array([0, 0, 1.0])
    # normalizacao: razao das normas rms dos campos no ceu
    rng = np.random.default_rng(3)
    S = rng.normal(size=(3000, 3))
    S /= np.linalg.norm(S, axis=1)[:, None]
    rms0 = np.sqrt(np.mean([np.linalg.norm(c0(s)) ** 2 for s in S]))
    for nome, (Fp, t) in PERT.items():
        cp = soma_campos([(1.0, Fp, t)])
        rmsp = np.sqrt(np.mean([np.linalg.norm(cp(s)) ** 2 for s in S]))
        linhas = []
        dists = []
        for eps in (1e-2, 1e-3, 1e-4):
            campo = soma_campos([(1.0, F0, "E"), (eps * rms0 / rmsp, Fp, t)])
            zz = achar_zeros(campo, n0=nz, raio_busca=np.radians(30), N=1500, tol=1e-8)
            if zz:
                dmax = max(np.degrees(np.arccos(np.clip(n @ nz, -1, 1))) for n, _ in zz)
                # separacao maxima entre zeros do grupo
                sep = max([np.degrees(np.arccos(np.clip(a @ b, -1, 1))) for a, _ in zz for b, _ in zz] + [0])
            else:
                dmax = sep = np.nan
            dists.append(sep)
            linhas.append("eps %.0e: %d zeros, indices %s, soma %.2f, separacao max %.3e graus" % (
                eps, len(zz), sorted([round(float(i), 2) for _, i in zz]), sum(i for _, i in zz), sep))
        d = np.array(dists)
        expo = np.polyfit(np.log10([1e-2, 1e-3, 1e-4]), np.log10(d), 1)[0] if np.all(d > 0) else np.nan
        print("  %-9s: %s ; expoente d ~ eps^%.2f" % (nome, " | ".join(linhas), expo))


if __name__ == "__main__":
    T1()
    T2()
