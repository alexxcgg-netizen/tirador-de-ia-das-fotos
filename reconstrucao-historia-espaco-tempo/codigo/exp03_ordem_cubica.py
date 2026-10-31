"""Experimento 3: a degenerescencia sobrevive alem da ordem quadratica?

Na ordem quadratica as memorias dependem so das matrizes de Gram (exp02). Na ordem
seguinte a propria memoria entra nos fluxos: h_total = h_osc + h_nl, com h_nl =
memoria nula acumulada (modos (2,0),(4,0)) + modo de memoria de spin (3,0). Os termos
h_nl x hdot_osc ja nao sao invariantes por filtro de fase.

Parte 1: mede a quebra da igualdade A (chirp) x B (anti-chirp) nessa ordem.
Parte 2: continuacao. Historia B(s) = A atravessando o filtro de fase s*phi_E + sum_k eps_k b_k,
  com phi_E uma dispersao forte e aleatoria (a da fonte E do exp02) e b_k bossas impares.
  Para s = 0, 0.1, ..., 1, corrijo eps (Levenberg-Marquardt, jacobiano por diferencas
  finitas) para manter as memorias de ordem cubica iguais as de A. Como so a fase muda,
  as memorias de ordem quadratica continuam exatamente iguais o tempo todo.

Modelo de brinquedo: os termos eletricos instantaneos de ordem G^2 que dependem da
dinamica da fonte (e as caudas) nao estao incluidos; o ponto e estrutural.
Saida: resultados/exp03_ordem_cubica.txt, figuras/e3_ordem_cubica.png
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import fontes as F                                                  # noqa: E402
from memorias import CalculadoraMemoria, gram, diferenca_relativa   # noqa: E402
from harmonicos import Grade, eth_fator, ethb_fator, Dfrak, D2, ethb2_de_escalar  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


u, du = F.grade_tempo(L=16384.0, n=2 ** 14)
n = len(u)
HA, _ = F.fonte_girante(u, du)
NL = [(2, 0), (3, 0), (4, 0)]
calc_nl = CalculadoraMemoria(F.LISTA, lmax_saida=4)
calc_full = CalculadoraMemoria(F.LISTA + NL)
calc_osc = CalculadoraMemoria(F.LISTA)
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


class NaoLinearRapido:
    """h_nl(u) por acoplamentos angulares pre-computados (mesmas formulas de partes_instantaneas).

    E_k(u) = sum_ab cE[k,a,b] hdot_a conj(hdot_b);  W_k(u) = sum_ab cW[k,a,b] (hdot_a conj(h_b) - h_a conj(hdot_b)),
    com cW = 3 cP + cQ, P_ab = Y_a conj(eth Y_b), Q_ab = conj(Y_b) ethb Y_a (ver memorias.py).
    """

    def __init__(self, lista, saida, ntheta=30, nphi=64):
        g = Grade(ntheta, nphi)
        w = g.peso
        Y = np.array([g.Y(-2, l, m) for (l, m) in lista])
        eY = np.array([eth_fator(-2, l) * g.Y(-1, l, m) for (l, m) in lista])
        ebY = np.array([ethb_fator(-2, l) * g.Y(-3, l, m) for (l, m) in lista])
        Y0 = np.array([g.Y(0, l, m) for (l, m) in saida])
        Ym1 = np.array([g.Y(-1, l, m) for (l, m) in saida])
        self.cE = np.einsum('aij,bij,kij,ij->kab', Y, Y.conj(), Y0.conj(), w)
        cP = np.einsum('aij,bij,kij,ij->kab', Y, eY.conj(), Ym1.conj(), w)
        cQ = np.einsum('bij,aij,kij,ij->kab', Y.conj(), ebY, Ym1.conj(), w)
        self.cW = 3 * cP + cQ
        self.saida = saida
        self.fat_eth = np.array([eth_fator(-1, l) for (l, m) in saida])
        self.fat_B = np.array([-0.5j * ethb2_de_escalar(l) * 0.125 / (Dfrak(l) * D2(l)) for (l, m) in saida])
        self.fat_E = np.array([0.5 * ethb2_de_escalar(l) * 0.25 / Dfrak(l) for (l, m) in saida])
        assert all(m == 0 for (l, m) in saida)     # Re/Im de modo m = 0 sao Re/Im do coeficiente

    def __call__(self, H, Hd):
        E = np.einsum('kab,ua,ub->uk', self.cE, Hd, Hd.conj())
        X = Hd[:, :, None] * H.conj()[:, None, :] - H[:, :, None] * Hd.conj()[:, None, :]
        W = np.einsum('kab,uab->uk', self.cW, X)
        ethW = self.fat_eth * W
        hB = self.fat_B * ethW.imag
        dmem = self.fat_E * E.real
        return hB, dmem


rapido = NaoLinearRapido(F.LISTA, NL)


def completo(H, lento=False):
    Hd = F.derivar(H, du, 1)
    if lento:
        hB, _, dmem = calc_nl.partes_instantaneas(H, Hd, NL)
    else:
        hB, dmem = rapido(H, Hd)
    return np.concatenate([H, np.cumsum(dmem, axis=0) * du + hB], axis=1)


def memorias_completas(H):
    Hf = completo(H)
    return calc_full.memorias_gram(*gram(Hf, np.gradient(Hf, du, axis=0), du))


def quad(H):
    return calc_osc.memorias_gram(*gram(H, F.derivar(H, du, 1), du))


def fmt(d):
    return ", ".join("%s %.1e" % (k, v) for k, v in d.items())


# ---------------- parte 1 ----------------
t0 = time.time()
HB = F.aplicar_fase(HA, F.fase_antichirp(n, du))
mA = memorias_completas(HA)
mB = memorias_completas(HB)
_a, _b = completo(HA), completo(HA, lento=True)
log("Conferencia: termos nao lineares, rapido x grade: max|dif|/max = %.1e" % (np.abs(_a - _b).max() / np.abs(_b).max()))
log("Parte 1 (A chirp x B anti-chirp)")
log("  ordem quadratica, diferenca relativa: " + fmt(diferenca_relativa(quad(HA), quad(HB))))
log("  efeito da ordem cubica nas memorias de A: " + fmt(diferenca_relativa(quad(HA), mA)))
log("  ordem cubica, diferenca relativa (quebra): " + fmt(diferenca_relativa(mA, mB)))

# ---------------- parte 2 ----------------
rng = np.random.default_rng(7)
phiE = F.fase_aleatoria(n, du, rng)                       # a mesma dispersao da fonte E (exp02)
w = F.omegas(n, du)
centros = np.linspace(0.03, 0.8, 50)
larg = (centros[1] - centros[0]) * 1.2
base = np.array([np.sign(w) * np.exp(-0.5 * ((np.abs(w) - c) / larg) ** 2) for c in centros]
                + [np.sin(j * w * 40.0) for j in range(1, 51)])

# componentes independentes: m >= 0, partes que nao sao identicamente nulas
mE = memorias_completas(F.aplicar_fase(HA, phiE))
escalas = {t: max(abs(c) for c in mA[t].values()) for t in TIPOS}
comp = []
for t in TIPOS:
    for k in sorted(mA[t]):
        if k[1] < 0:
            continue
        for parte in ("re", "im"):
            f = (lambda z: z.real) if parte == "re" else (lambda z: z.imag)
            if max(abs(f(mA[t][k])), abs(f(mE[t][k]))) > 1e-12 * escalas[t]:
                comp.append((t, k, parte))


def vetor(m):
    return np.array([(m[t][k].real if p == "re" else m[t][k].imag) / escalas[t] for t, k, p in comp])


alvo = vetor(mA)
log("Parte 2: %d componentes reais independentes a igualar; %d parametros de fase" % (len(comp), base.shape[0]))


def historia(s, eps):
    return F.aplicar_fase(HA, s * phiE + eps @ base)


def residuo(s, eps):
    return vetor(memorias_completas(historia(s, eps))) - alvo


eps = np.zeros(base.shape[0])
caminho = []
for s in np.linspace(0.05, 1.0, 20):
    r = residuo(s, eps)
    r0 = np.max(np.abs(r))
    J = None
    lam = 1e-6
    for it in range(8):
        if np.max(np.abs(r)) < 1e-11:
            break
        if J is None:
            J = np.zeros((len(r), len(eps)))
            h = 1e-4
            for k in range(len(eps)):
                e2 = eps.copy()
                e2[k] += h
                J[:, k] = (residuo(s, e2) - r) / h
        while True:
            passo = np.linalg.solve(J.T @ J + lam * np.eye(len(eps)), -J.T @ r)
            r2 = residuo(s, eps + passo)
            if np.max(np.abs(r2)) < np.max(np.abs(r)):
                eps, r = eps + passo, r2
                lam = max(lam / 10, 1e-12)
                break
            lam *= 10
            if lam > 1e6:
                break
        if lam > 1e6:
            break
    r_puro = np.max(np.abs(residuo(s, 0 * eps)))
    caminho.append((s, r_puro, np.max(np.abs(r)), np.max(np.abs(eps))))
    if J is not None:
        log("    posto do jacobiano = %d de %d componentes" % (np.linalg.matrix_rank(J, 1e-9 * np.abs(J).max()), len(r)))
    log("  s = %.2f: sem correcao %.1e | partindo da correcao anterior %.1e -> corrigido %.1e   |eps|max = %.3f rad   (%.0f s)"
        % (s, np.max(np.abs(residuo(s, 0 * eps))), r0, np.max(np.abs(r)), np.max(np.abs(eps)), time.time() - t0))

# polimento no ponto final: Levenberg-Marquardt com jacobiano novo (diferencas centrais) a cada iteracao
r = residuo(1.0, eps)
lam = None
for it in range(12):
    if np.max(np.abs(r)) < 1e-12:
        break
    J = np.zeros((len(r), len(eps)))
    h = 1e-5
    for k in range(len(eps)):
        ep, em = eps.copy(), eps.copy()
        ep[k] += h
        em[k] -= h
        J[:, k] = (residuo(1.0, ep) - residuo(1.0, em)) / (2 * h)
    JTJ, JTr = J.T @ J, J.T @ r
    if lam is None:
        lam = 1e-3 * np.max(np.diag(JTJ))
    aceito = False
    for _ in range(30):
        passo = np.linalg.solve(JTJ + lam * np.eye(len(eps)), -JTr)
        r2 = residuo(1.0, eps + passo)
        if np.linalg.norm(r2) < np.linalg.norm(r):
            eps, r, lam, aceito = eps + passo, r2, lam / 5, True
            break
        lam *= 5
    sv = np.linalg.svd(J, compute_uv=False)
    log("  polimento %d: max residuo %.1e  (aceito=%s, lambda=%.1e, sigma_min/sigma_max=%.1e)"
        % (it + 1, np.max(np.abs(r)), aceito, lam, sv[-1] / sv[0]))
    if not aceito:
        break
polido = np.max(np.abs(r))

Hfim = historia(1.0, eps)
log("Historia final B' (s = 1):")
log("  ordem cubica, A x B': " + fmt(diferenca_relativa(mA, memorias_completas(Hfim))))
log("  ordem quadratica, A x B' (exata por construcao): " + fmt(diferenca_relativa(quad(HA), quad(Hfim))))
log("  sem a correcao (so a dispersao, s = 1, eps = 0), ordem cubica: "
    + fmt(diferenca_relativa(mA, memorias_completas(historia(1.0, 0 * eps)))))


def overlap(a, b):
    xc = np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b)))
    return np.max(np.abs(xc)) / np.sqrt(np.sum(np.abs(a) ** 2) * np.sum(np.abs(b) ** 2))


log("  sobreposicao do modo 22 entre A e B' = %.3f" % overlap(HA[:, 0], Hfim[:, 0]))
with open(os.path.join(AQUI, "..", "resultados", "exp03_ordem_cubica.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")

import matplotlib                                                   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ss = [c[0] for c in caminho]
ax.semilogy(ss, [c[1] for c in caminho], color="#eb6834", lw=2, marker="o", ms=4, label="só a dispersão (sem correção de fase)")
ax.semilogy(ss, [max(c[2], 1e-16) for c in caminho], color="#2a78d6", lw=2, marker="o", ms=4, label="com a fase corrigida")
ax.semilogy([1.0], [polido], color="#2a78d6", marker="*", ms=11, ls="none")
ax.annotate("após polimento", (1.0, polido), textcoords="offset points", xytext=(-70, -4), fontsize=7, color="#52514e")
ax.set_xlabel("intensidade s da dispersão aplicada a A")
ax.set_ylabel("maior diferença relativa (ordem cúbica)")
ax.set_title("Memórias de ordem cúbica mantidas iguais às de A ao longo do caminho", loc="left", fontsize=9)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(AQUI, "..", "figuras", "e3_ordem_cubica.png"), dpi=140)
