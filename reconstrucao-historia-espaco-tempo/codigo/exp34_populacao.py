"""exp34 (L11) - zeros da memoria de deslocamento no ceu para binarias alinhadas e precessantes (NRSur7dq4).

Para cada sistema (janela f_22 >= f0 = 0.007 ate o fim, nivel A, todos os modos l <= 4, memorias l <= 8):
  - zeros do campo de deslocamento (todos os l, m), indices (laco) e soma (Poincare-Hopf); conferencia pela icosfera;
  - zeros so da parte l = 2 e a previsao dos eixos opticos do tensor A (Phi_2 = n.A.n);
  - direcoes: e1 (autovetor do maior autovalor de A), pontos medios dos pares de zeros, L_i (= z), eixo
    coprecessante no pico, J_rad (janela), chi_f (surfinBH NRSur7dq4Remnant, omega0 = pi f0), J_i (PN + spins),
    eixo de luminosidade e_Q (autovetor principal de Q = int dE zc zc^T, zc = eixo coprecessante);
  - meia abertura dos pares de zeros: medida, prevista pelos autovalores de A e prevista por Q (emissao
    instantanea uniaxial em torno de zc: A ~ int dE (3 zc zc^T - 1)).
  - zeros e soma de indices tambem para a memoria de spin (campo magnetico) e de CM.
Populacao: sistemas nomeados + N aleatorios (q em [1, 4], |chi| em [0.1, 0.8], direcoes isotropas; semente fixa).
Saidas: resultados/exp34_populacao.txt, resultados/exp34_populacao.npz
"""
import os
import sys
import time

import numpy as np

import exp33_comum as C
import exp34_zeros as Z
from harmonicos import ethb2_de_escalar

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
F0 = C.F0_PADRAO
NOMEADOS = {
    "AL1": (1.2, (0, 0, 0.3), (0, 0, -0.2)),
    "AL2": (3.0, (0, 0, 0.5), (0, 0, 0.3)),
    "P1": (2.0, (0.5, 0.0, 0.2), (0.0, -0.3, 0.1)),
    "P2": (1.2, (0.6, 0.2, 0.0), (-0.3, 0.4, 0.2)),
    "P3": (3.0, (0.7, 0.0, 0.0), (0.0, 0.0, 0.1)),
    "P4": (1.05, (0.5, 0.0, 0.0), (-0.5, 0.0, 0.0)),
    "P5": (1.5, (0.3, 0.3, -0.3), (0.2, -0.4, 0.4)),
    "P6": (4.0, (0.8, 0.0, -0.1), (0.0, 0.0, 0.1)),
}
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def ang(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))))


def ang_eixo(a, b):
    """Angulo entre eixos (sem sentido), em graus."""
    x = ang(a, b)
    return min(x, 180 - x)


def tensor_desl(mem):
    pot = {(l, m): 2 * c / ethb2_de_escalar(l) for (l, m), c in mem["deslocamento"].items() if l == 2}
    import exp33_jacobiano as EJ
    return EJ.tensor_l2(pot)


def l_pn(x, eta):
    return eta / np.sqrt(x) * (1 + (1.5 + eta / 6) * x + (27 / 8 - 19 / 8 * eta + eta ** 2 / 24) * x ** 2)


def eixo_luminosidade(t, h, dyn, t_i):
    import observaveis as O
    w = O.pesos_janela(t, t_i)
    dt = t[1] - t[0]
    H = np.stack([h[k] for k in C.MODOS], axis=1)
    Hd = O.derivada(H, dt, 8)
    L = np.sum(np.abs(Hd) ** 2, axis=1) / (16 * np.pi)
    del H, Hd
    zc = np.array([C.eixo_copr(dyn["q_copr"][:, k]) for k in range(len(t))])
    Q = np.einsum("k,ki,kj->ij", w * L, zc, zc)
    lam, E = np.linalg.eigh(Q)
    eQ = E[:, 2] * np.sign(E[2, 2] if abs(E[2, 2]) > 1e-12 else 1.0)
    s2 = (lam[1] - lam[0]) / (lam[2] - lam[0])
    return eQ, float(np.degrees(np.arcsin(np.sqrt(max(s2, 0))))), lam


def analisar(nome, q, cA, cB, fit, tri_nivel=5, todos=True):
    t, h, dyn = C.gerar7(q, cA, cB, f_ref=F0)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, aux = C.memorias7(q, t, h, dyn, ti)
    eQ, aQ, lamQ = eixo_luminosidade(t, h, dyn, ti)
    del t, h, dyn
    mf, chif, vf, _, _, _ = fit.all(q, list(cA), list(cB), omega0=np.pi * F0, omega_switch_IG=0.5 * np.pi * F0,
                                    allow_extrap=True)
    eta = q / (1 + q) ** 2
    m1, m2 = q / (1 + q), 1 / (1 + q)
    Ji = l_pn(aux["x_i"], eta) * aux["Lhat_i"] + m1 ** 2 * aux["chiA_i"] + m2 ** 2 * aux["chiB_i"]
    D = mem["deslocamento"]
    tri, lista_tri = Z.indices_triangulos(D, nivel=tri_nivel)
    zz = Z.zeros(D, extras=[c for c, _ in lista_tri])
    soma = sum(z["indice"] for z in zz)
    A = tensor_desl(mem)
    prev, a_prev, e1 = Z.eixos_opticos(A)
    if e1[2] < 0:
        e1 = -e1
    z2 = Z.zeros({k: v for k, v in D.items() if k[0] == 2}, extras=prev)
    d_opt = max(min(ang(p, z["n"]) for z in z2) for p in prev) if len(z2) == 4 else np.nan
    # pares em torno de +e1 e -e1
    gp = [z["n"] for z in zz if z["n"] @ e1 > 0]
    gm = [z["n"] for z in zz if z["n"] @ e1 < 0]
    mid_p = np.sum(gp, axis=0) if gp else np.full(3, np.nan)
    mid_m = -np.sum(gm, axis=0) if gm else np.full(3, np.nan)
    abert = 0.5 * ang(gp[0], gp[1]) if len(gp) == 2 else np.nan
    dirs = {"L_i": aux["Lhat_i"], "L_pico": aux["Lhat_pico"], "J_rad": aux["J_rad"], "chi_f": np.asarray(chif),
            "J_i": Ji, "e_Q": eQ}
    res = dict(nome=nome, q=q, cA=np.array(cA, float), cB=np.array(cB, float), nzeros=len(zz),
               indices=[z["indice"] for z in zz], soma=soma, soma_tri=tri, e1=e1, mid_p=mid_p, mid_m=mid_m,
               abert=abert, a_prev=np.degrees(a_prev), a_Q=aQ, d_opt=d_opt, nz2=len(z2),
               ang_e1={k: ang_eixo(e1, v) for k, v in dirs.items()},
               ang_mid={k: ang_eixo(mid_p, v) if gp else np.nan for k, v in dirs.items()},
               ang_e1_eQ=ang_eixo(e1, eQ), ang_Jrad_chif=ang(aux["J_rad"], chif), ang_Li_chif=ang(aux["Lhat_i"], chif),
               tilt_chif=ang([0, 0, 1], chif), zeros=[z["n"] for z in zz], hmin=[z["hmin_rel"] for z in zz],
               dmin=min([z["dmin"] for z in zz]) if zz else np.nan)
    if todos:
        for tipo in ("spin", "cm"):
            _, lt = Z.indices_triangulos(mem[tipo], nivel=tri_nivel)
            zt = Z.zeros(mem[tipo], extras=[c for c, _ in lt])
            res["soma_" + tipo] = sum(z["indice"] for z in zt)
            res["nz_" + tipo] = len(zt)
            res["idx_" + tipo] = [z["indice"] for z in zt]
            ezt = [z["n"] for z in zt]
            res["ang_" + tipo + "_e1"] = [ang_eixo(n, e1) for n in ezt]
    return res


def resumo(r):
    log("  %s q %.2f chiA %s chiB %s: %d zeros, indices %s, soma %.3f (icosfera %.2f) ; menor distancia entre zeros %.3f graus"
        % (r["nome"], r["q"], np.round(r["cA"], 2).tolist(), np.round(r["cB"], 2).tolist(), r["nzeros"],
           [round(x, 2) for x in r["indices"]], r["soma"], r["soma_tri"], np.degrees(r["dmin"])))
    log("      meia abertura dos pares: medida %.3f graus ; eixos opticos de A (l = 2) %.3f ; prevista por Q %.3f ;"
        " zeros so de l = 2 contra eixos opticos: %d zeros, desvio max %.1e graus" % (
            r["abert"], r["a_prev"], r["a_Q"], r["nz2"], r["d_opt"]))
    log("      angulo de e1 com: " + " ; ".join("%s %.2f" % (k, v) for k, v in r["ang_e1"].items()))
    log("      angulo do ponto medio do par (+) com: " + " ; ".join("%s %.2f" % (k, v) for k, v in r["ang_mid"].items()))
    if "soma_spin" in r:
        log("      spin: %d zeros, indices %s, soma %.2f ; CM: %d zeros, indices %s, soma %.2f" % (
            r["nz_spin"], [round(x, 2) for x in r["idx_spin"]], r["soma_spin"], r["nz_cm"],
            [round(x, 2) for x in r["idx_cm"]], r["soma_cm"]))


def aleatorios(N, seed=11):
    rng = np.random.default_rng(seed)
    out = []
    for k in range(N):
        q = rng.uniform(1.0, 4.0)
        vs = []
        for _ in range(2):
            u = rng.normal(size=3)
            u /= np.linalg.norm(u)
            vs.append(tuple(rng.uniform(0.1, 0.8) * u))
        out.append(("R%02d" % k, q, vs[0], vs[1]))
    return out


if __name__ == "__main__":
    import surfinBH
    fit = surfinBH.LoadFits("NRSur7dq4Remnant")
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    log("exp34_populacao: zeros da memoria de deslocamento no ceu (NRSur7dq4, nivel A, janela f_22 >= %.4f, l <= 8)" % F0)
    log("angulos em graus; e1 = eixo principal do tensor l = 2 do deslocamento; e_Q = eixo de luminosidade")
    todos = []
    log("")
    log("Sistemas nomeados (icosfera nivel 6):")
    for nome, (q, cA, cB) in NOMEADOS.items():
        r = analisar(nome, q, cA, cB, fit, tri_nivel=6)
        resumo(r)
        todos.append(r)
    # alinhado so com m = 0 (controle axissimetrico)
    t, h, dyn = C.gerar7(*NOMEADOS["AL1"], f_ref=F0)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, _ = C.memorias7(NOMEADOS["AL1"][0], t, h, dyn, ti)
    del t, h, dyn
    D0 = {k: v for k, v in mem["deslocamento"].items() if k[1] == 0}
    zz = Z.zeros(D0)
    Dm = mem["deslocamento"]
    eps = np.sqrt(sum(abs(v) ** 2 for k, v in Dm.items() if k[0] == 2 and k[1] != 0)) / abs(Dm[(2, 0)])
    log("  AL1 so m = 0: zeros %s, indices %s ; com todos os m: razao |l=2, m!=0|/|a20| = %.2e, sqrt = %.2e rad = %.3f graus"
        % ([np.round(z["n"], 6).tolist() for z in zz], [round(z["indice"], 3) for z in zz], eps, np.sqrt(eps),
           np.degrees(np.sqrt(eps))))
    log("")
    log("Populacao aleatoria (%d sistemas, icosfera nivel 5):" % N)
    for (nome, q, cA, cB) in aleatorios(N):
        try:
            r = analisar(nome, q, cA, cB, fit, tri_nivel=5, todos=False)
        except Exception as e:                       # fora do dominio do substituto
            log("  %s falhou: %s" % (nome, e))
            continue
        resumo(r)
        todos.append(r)
        log("      (%.0f s)" % (time.time() - T0))
    pop = [r for r in todos if r["nome"].startswith("R")]
    log("")
    log("Resumo da populacao (%d):" % len(pop))
    if not pop:
        sys.exit(0)
    log("  numero de zeros: %s" % {n: sum(1 for r in pop if r["nzeros"] == n) for n in sorted(set(r["nzeros"] for r in pop))})
    log("  somas de indices (laco): %s ; (icosfera): %s" % (sorted(set(round(r["soma"], 3) for r in pop)),
                                                           sorted(set(round(r["soma_tri"], 3) for r in pop))))
    for chave in ("L_i", "L_pico", "J_rad", "chi_f", "J_i", "e_Q"):
        a = np.array([r["ang_e1"][chave] for r in pop])
        b = np.array([r["ang_mid"][chave] for r in pop])
        log("  angulo e1 - %-6s: mediana %.2f, percentil 90 %.2f, max %.2f ; ponto medio do par - %-6s: mediana %.2f,"
            " p90 %.2f, max %.2f" % (chave, np.median(a), np.percentile(a, 90), a.max(), chave, np.nanmedian(b),
                                     np.nanpercentile(b, 90), np.nanmax(b)))
    a = np.array([r["abert"] for r in pop])
    ap = np.array([r["a_prev"] for r in pop])
    aq = np.array([r["a_Q"] for r in pop])
    ok = np.isfinite(a)
    log("  meia abertura medida: mediana %.2f graus (min %.2f, max %.2f) ; |medida - eixos opticos de A|: mediana %.2f,"
        " max %.2f ; |medida - prevista por Q|: mediana %.2f, max %.2f ; correlacao (medida, Q) %.3f" % (
            np.median(a[ok]), a[ok].min(), a[ok].max(), np.median(np.abs(a - ap)[ok]), np.max(np.abs(a - ap)[ok]),
            np.median(np.abs(a - aq)[ok]), np.max(np.abs(a - aq)[ok]), np.corrcoef(a[ok], aq[ok])[0, 1]))
    tilt = np.array([r["tilt_chif"] for r in pop])
    log("  inclinacao de chi_f em relacao a L_i: mediana %.2f graus, max %.2f" % (np.median(tilt), tilt.max()))
    with open(os.path.join(RES, "exp34_populacao.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    chaves_num = ["q", "soma", "soma_tri", "abert", "a_prev", "a_Q", "nzeros", "ang_e1_eQ", "ang_Jrad_chif",
                  "ang_Li_chif", "tilt_chif"]
    np.savez(os.path.join(RES, "exp34_populacao.npz"),
             nomes=np.array([r["nome"] for r in todos]),
             **{k: np.array([r[k] for r in todos], float) for k in chaves_num},
             cA=np.array([r["cA"] for r in todos]), cB=np.array([r["cB"] for r in todos]),
             e1=np.array([r["e1"] for r in todos]), mid_p=np.array([r["mid_p"] for r in todos]),
             **{"ang_e1_" + k: np.array([r["ang_e1"][k] for r in todos]) for k in todos[0]["ang_e1"]},
             **{"ang_mid_" + k: np.array([r["ang_mid"][k] for r in todos]) for k in todos[0]["ang_mid"]})
