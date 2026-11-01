"""Experimento 17 (L01): analise dos jacobianos (SVD, posto numerico, loci, espaco nulo).

Le resultados/exp17_jacobianos_dados.npz (exp17_jacobianos.py) e o ponto A (resultados/exp17_jac_A.npz). Conjuntos de observaveis no observador (D = 400 Mpc):
  T0: (desl, spin, CM, giro) so com multipolos m = 0; parametros (ln M, q, chi1, chi2, ln D, iota)       n = 6
  T : as quatro com todos os (l, m), l <= 8; parametros + phi' (azimute medido da fase orbital no pico)  n = 7
  O : (desl, spin) com todos os m (o que um interferometro mede de memoria integrada)                     n = 7
  O0: (desl, spin) so m = 0                                                                              n = 6
Casos: 'livre' (todos), 'iota' (iota conhecido), 'iotaD' (iota e D conhecidos), 'intr' (so ln M, q, chi1, chi2).
Escalas: 'abs' = linhas / |F(iota = 50 graus, phi' = 0, so m = 0)| do mesmo ponto (independe de iota);
         'rel' = linhas / |F| no proprio ponto (omitida se |F| ~ 0).
Em q = 1 (borda do dominio) a coluna q e a derivada unilateral (q >= 1); ver jacobiano().
Posto numerico: numero de valores singulares acima de tau = ||E||_F, onde E e a cota do erro de cada elemento
(|D_h - D_h/2| + |D_h/2 - D_h/4|, mesma escala); pela desigualdade de Weyl |sigma_k(J + dJ) - sigma_k(J)| <= ||dJ||_2
<= ||dJ||_F, entao sigma_k > tau garante sigma_k(J exato) > 0 (jacobiano do MODELO; o erro do modelo e outra coisa).
Saidas: resultados/exp17_jacobianos.txt, resultados/exp17_jacobianos_resumo.json, figuras/e17_jacobiano.png
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from harmonicos import sYlm                               # noqa: E402
from deteccao import MSUN_S, MPC_S                        # noqa: E402

TIPOS = ("deslocamento", "spin", "cm", "giroscopica")
S_T = {"deslocamento": -2, "spin": -2, "cm": -2, "giroscopica": 0}
KD = np.array([1.0, 1.0, 1.0, 2.0])
D_MPC = 400.0
IOTAS = (10.0, 30.0, 50.0, 70.0, 85.0, 90.0)
PHIS = tuple(np.arange(6) * np.pi / 3)
COLS = ("lnM", "q", "chi1", "chi2", "lnD", "iota", "phi")
DADOS = os.path.join(AQUI, "..", "resultados", "exp17_jacobianos_dados.npz")
PA = os.path.join(AQUI, "..", "resultados", "exp17_jac_A.npz")
SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_jacobianos.txt")
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


_z = np.load(DADOS)
z = {k: _z[k] for k in _z.files}             # carrega tudo uma vez (o npz comprimido e lido sob demanda)
K = {t: [tuple(int(a) for a in x) for x in z["chaves_" + t]] for t in TIPOS}
OFF = {}
o = 0
for t in TIPOS:
    OFF[t] = o
    o += len(K[t])
NK = o
MS = tuple(z["MS"])
FR = tuple(z["FRACS"])
H_INT, H_LNM = float(z["H_INT"]), float(z["H_LNM"])
PONTOS = [tuple(p) for p in z["pontos"]]
MMAT = np.zeros(NK)
for t in TIPOS:
    for j, (l, m) in enumerate(K[t]):
        MMAT[OFF[t] + j] = m


def ymat(iota, phi, m0):
    Y = np.zeros((4, NK), dtype=complex)
    for i, t in enumerate(TIPOS):
        for j, (l, m) in enumerate(K[t]):
            if m0 and m != 0:
                continue
            Y[i, OFF[t] + j] = complex(sYlm(S_T[t], l, m, iota, phi))
    return Y


def val(Y, v):
    zz = v @ Y.T
    out = zz.real.copy()
    out[..., 1] = -zz[..., 1].imag
    return out


def esc(M):
    Ms, Ds = M * MSUN_S, D_MPC * MPC_S
    return np.array([Ms / Ds, Ms ** 2 / Ds, Ms ** 2 / Ds, (Ms / Ds) ** 2])


_ycache = {}


def Ys(iota, phi, m0):
    k = (round(iota, 12), round(phi, 12), m0)
    if k not in _ycache:
        e = 1e-6
        Y = ymat(iota, phi, m0)
        _ycache[k] = (Y, ymat(iota + e, phi, m0), ymat(iota - e, phi, m0), Y * (1j * MMAT)[None, :], e)
    return _ycache[k]


def jacobiano(dp, j, iota, phi, m0):
    """J (4 x 7) e E (4 x 7) em unidades fisicas; dp = dict com base, V, lista. Colunas COLS."""
    Y, Yp, Ym, Yf, e = Ys(iota, phi, m0)
    base, V, lst = dp["base"], dp["V"], dp["lista"]
    i0 = 7 * j
    M0 = lst[i0]
    F0 = esc(M0) * val(Y, base[i0])
    Dk = []
    for k, fr in enumerate(FR):
        a, b = i0 + 1 + 2 * k, i0 + 2 + 2 * k
        Dk.append((esc(lst[a]) * val(Y, base[a]) - esc(lst[b]) * val(Y, base[b])) / (2 * fr * H_LNM))
    cols, errs = [Dk[1]], [np.abs(Dk[0] - Dk[1]) + np.abs(Dk[1] - Dk[2])]
    for d in range(3):
        if d == 0 and abs(dp["p"][0] - 1.0) < 1e-12:
            # q = 1 e borda do dominio (q >= 1); o modelo nao e exatamente simetrico pela troca em q = 1 (salto de
            # ~1e-3 entre F(1, chi1, chi2) e F(1, chi2, chi1)), entao a diferenca central atraves de q = 1 nao converge.
            # Derivada unilateral de 2a ordem: (-3 F(1) + 4 F(1 + h') - F(1 + 2 h')) / (2 h'), h' = h/2 e h/4.
            Fb = esc(M0) * val(Y, base[i0])
            Fp = {k: esc(M0) * val(Y, V[0, k, 0, j]) for k in range(len(FR))}       # q = 1 + FR[k] h
            D1 = (-3 * Fb + 4 * Fp[1] - Fp[0]) / (2 * FR[1] * H_INT)
            D2 = (-3 * Fb + 4 * Fp[2] - Fp[1]) / (2 * FR[2] * H_INT)
            cols.append(D2)
            errs.append(2 * np.abs(D1 - D2))
            continue
        Dk = [esc(M0) * (val(Y, V[d, k, 0, j]) - val(Y, V[d, k, 1, j])) / (2 * fr * H_INT) for k, fr in enumerate(FR)]
        cols.append(Dk[1])
        errs.append(np.abs(Dk[0] - Dk[1]) + np.abs(Dk[1] - Dk[2]))
    cols.append(-KD * F0)
    errs.append(np.zeros(4))
    ci = esc(M0) * (val(Yp, base[i0]) - val(Ym, base[i0])) / (2 * e)
    cols.append(ci)
    errs.append(1e-8 * np.abs(ci))
    cols.append(esc(M0) * val(Yf, base[i0]))
    errs.append(np.zeros(4))
    return F0, np.array(cols).T, np.array(errs).T


CONJ = {"T0": (True, [0, 1, 2, 3], [0, 1, 2, 3, 4, 5]),
        "T": (False, [0, 1, 2, 3], [0, 1, 2, 3, 4, 5, 6]),
        "O": (False, [0, 1], [0, 1, 2, 3, 4, 5, 6]),
        "O0": (True, [0, 1], [0, 1, 2, 3, 4, 5])}
CASOS = {"livre": [], "iota": ["iota"], "iotaD": ["iota", "lnD"], "intr": ["iota", "lnD", "phi"]}


def analisar(dp, j, iota, phi, conj, caso, escala, Fref):
    m0, rows, cols = CONJ[conj]
    F0, J, E = jacobiano(dp, j, iota, phi, m0)
    cols = [c for c in cols if COLS[c] not in CASOS[caso]]
    J, E, F = J[np.ix_(rows, cols)], E[np.ix_(rows, cols)], F0[rows]
    if escala == "abs":
        s = 1 / np.abs(Fref[rows])
    else:
        if np.any(np.abs(F) < 1e-9 * np.abs(Fref[rows])):
            return None
        s = 1 / np.abs(F)
    Js, Es = J * s[:, None], E * s[:, None]
    U, sv, Vt = np.linalg.svd(Js)
    tau = np.linalg.norm(Es)
    return dict(sv=sv, tau=tau, posto=int(np.sum(sv > tau)), n=len(cols), cols=[COLS[c] for c in cols], Vt=Vt,
                J=Js, E=Es, F=F)


def carregar_ponto(i):
    return dict(base=z["base_pico"][i], V=z["V"][i], lista=z["lista"][i], aux=z["aux"][i], p=PONTOS[i])


def carregar_A():
    w = np.load(PA)
    return dict(base=w["base_pico"], V=w["V"], lista=w["lista"], aux=w["aux"], p=(1.2, 0.3, -0.2))


def fref(dp, j):
    Y = Ys(np.radians(50.0), 0.0, True)[0]
    return esc(dp["lista"][7 * j]) * val(Y, dp["base"][7 * j])


# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    np.set_printoptions(linewidth=150)
    log("Experimento 17 (L01): jacobianos das memorias no observador; NRHybSur3dq8_CCE, nivel A, janela desde 10 Hz,")
    log("deslocamento de janela, D = 400 Mpc; m != 0 no referencial do pico com o termo de borda inicial suprimido.")
    log("Passos: q, chi: h = %.0e (h, h/2, h/4); ln M: %.0e. Posto numerico: sigma > tau = ||E||_F (Weyl)." % (H_INT, H_LNM))
    log("Grade: q %s, chi1, chi2 em (-0.6, 0, 0.6), M %s, iota %s graus, phi' = k pi/3 (k = 0..5)."
        % (sorted(set(p[0] for p in PONTOS)), MS, IOTAS))
    log("")
    resumo = {}
    piores = {}
    for conj in ("T0", "T", "O", "O0"):
        for caso in ("livre", "iota", "iotaD", "intr"):
            for escala in ("abs", "rel"):
                for io in IOTAS:
                    regs = []
                    for i, p in enumerate(PONTOS):
                        dp = carregar_ponto(i)
                        for j in range(len(MS)):
                            Fr = fref(dp, j)
                            for phi in (PHIS if conj in ("T", "O") else (0.0,)):
                                r = analisar(dp, j, np.radians(io), phi, conj, caso, escala, Fr)
                                if r is None:
                                    continue
                                regs.append((p, MS[j], phi, r))
                    if not regs:
                        continue
                    nmax = min(len(regs[0][3]["sv"]), 4)
                    svl = np.array([r[3]["sv"][-1] if len(r[3]["sv"]) else 0 for r in regs])
                    taus = np.array([r[3]["tau"] for r in regs])
                    postos = np.array([r[3]["posto"] for r in regs])
                    n = regs[0][3]["n"]
                    chave = "%s|%s|%s|%d" % (conj, caso, escala, io)
                    cont = {int(k): int(np.sum(postos == k)) for k in np.unique(postos)}
                    resumo[chave] = dict(n=n, postos=cont, sv_ultimo_min=float(svl.min()),
                                         sv_ultimo_med=float(np.median(svl)), sv_ultimo_max=float(svl.max()),
                                         tau_max=float(taus.max()), razao_min=float(np.min(svl / taus)),
                                         sv_todos_med=[float(x) for x in np.median(np.array([r[3]["sv"] for r in regs]), axis=0)])
                    k = int(np.argmin(svl / taus))
                    piores[chave] = (regs[k][0], regs[k][1], regs[k][2], regs[k][3]["sv"].tolist(), regs[k][3]["tau"])
    # ------------------------------------------------ tabela
    for escala in ("abs", "rel"):
        log("=" * 118)
        log("Escala '%s': por conjunto/caso e iota: n parametros, contagem de postos numericos, ultimo sigma (min/mediana/max),"
            % escala)
        log("max tau, min sigma_ultimo/tau, medianas de todos os sigma.")
        for conj in ("T0", "T", "O", "O0"):
            for caso in ("livre", "iota", "iotaD", "intr"):
                for io in IOTAS:
                    c = "%s|%s|%s|%d" % (conj, caso, escala, io)
                    if c not in resumo:
                        continue
                    r = resumo[c]
                    log("  %-3s %-6s iota %4.0f  n=%d  postos %-16s  sig_ult %.2e / %.2e / %.2e  tau_max %.1e  min(sig/tau) %.1e  med %s"
                        % (conj, caso, io, r["n"], str(r["postos"]), r["sv_ultimo_min"], r["sv_ultimo_med"], r["sv_ultimo_max"],
                           r["tau_max"], r["razao_min"], " ".join("%.2e" % x for x in r["sv_todos_med"])))
    log("")
    log("Pior caso (min sigma_ultimo/tau) de cada combinacao com escala abs: (q, chi1, chi2), M, phi', sigmas, tau")
    for c, v in piores.items():
        if "|abs|" in c:
            log("  %-22s %s M=%.0f phi'=%.2f sv=%s tau=%.1e" % (c, v[0], v[1], v[2], np.array2string(np.array(v[3]), precision=3), v[4]))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    with open(SAIDA.replace(".txt", "_resumo.json"), "w") as fh:
        json.dump(resumo, fh, indent=0)
