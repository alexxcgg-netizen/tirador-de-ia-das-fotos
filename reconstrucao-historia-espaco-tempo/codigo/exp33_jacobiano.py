"""exp33 (L10) - jacobiano das memorias globais em relacao aos 7 parametros (q, chiA vetor, chiB vetor) no NRSur7dq4.

Observaveis: vetor real ortonormal (exp33_comum.vetor_real) dos multipolos l <= 4 de todos os m das quatro
memorias de janela (f_22 >= f0 = 0.007 ate o fim; nivel A, todos os modos l <= 4): deslocamento, spin, CM
(l = 2..4, 21 componentes cada) e giroscopica (l = 0..4, 25): 88 componentes.
Parametros: q, chiA = (x, y, z), chiB = (x, y, z) em f_ref = f0, no referencial coorbital (z = L, x = n).

Para cada ponto:
  J_int (88 x 7) por diferencas centrais (passos 1e-5 e 5e-6; o erro numerico e estimado pela diferenca);
  J_rot (88 x 3): geradores de rotacao aplicados aos multipolos (o observador nao conhece a orientacao da fonte);
  conferencia de J_rot por rotacao finita (init_quat do gwsurrogate);
  valores singulares de J_int, de [J_int | J_rot] e de P_perp J_int (projetado fora das rotacoes); idem so com
  as linhas m = 0 e so com as m != 0; idem para o vetor com l <= 8;
  jacobiano de invariantes de rotacao (potencias por l, potencias cruzadas entre tipos, invariantes dos tensores
  l = 2) como caminho independente para o posto modulo rotacoes;
  jacobianos de grandezas do remanescente e da radiacao (M_f, chi_f, v_f do surfinBH; J_rad e P_rad das memorias)
  e o angulo entre os subespacos.
Saidas: resultados/exp33_jacobiano.txt, resultados/exp33_jacobianos.npz
"""
import os
import sys
import time

import numpy as np

import exp33_comum as C

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
F0 = C.F0_PADRAO
NOMES = ["q", "chiAx", "chiAy", "chiAz", "chiBx", "chiBy", "chiBz"]
PONTOS = {
    "J0": (1.2, (0.0, 0.0, 0.3), (0.0, 0.0, -0.2)),
    "J1": (2.0, (0.5, 0.0, 0.2), (0.0, -0.3, 0.1)),
    "J2": (1.2, (0.6, 0.2, 0.0), (-0.3, 0.4, 0.2)),
    "J3": (3.0, (0.7, 0.0, 0.0), (0.0, 0.0, 0.1)),      # chiB != 0: com chiB = 0 o NRSur7dq4 tem um bico ~|chiB| (exp33_validacao h)
    "J4": (1.05, (0.5, 0.0, 0.0), (-0.5, 0.0, 0.0)),    # q > 1 para as diferencas centrais em q
    "J5": (1.5, (0.3, 0.3, -0.3), (0.2, -0.4, 0.4)),
}
linhas = []
T0 = time.time()


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def avaliar(p, init_quat=None, lmax=4):
    q, cA, cB = p[0], p[1:4], p[4:7]
    if init_quat is None:
        t, h, dyn = C.gerar7(q, cA, cB, f_ref=F0)
    else:
        s = C.sur7()
        tc = s._sur_dimless.t_coorb
        tt = np.arange(int(np.ceil(tc[0] / 0.25)), int(np.floor(tc[-1] / 0.25)) + 1) * 0.25
        t, h, dyn = s(float(q), list(cA), list(cB), times=tt, f_low=0, f_ref=F0,
                      precessing_opts={"return_dynamics": True, "init_quat": list(init_quat)})
        h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, aux = C.memorias7(q, t, h, dyn, ti)
    del t, h, dyn
    v, rot = C.vetor_real(mem, lmax=lmax)
    return v, rot, mem, aux


def jac_central(f, p0, hh):
    cols = []
    for i in range(len(p0)):
        e = np.zeros(len(p0))
        e[i] = hh
        cols.append((f(p0 + e) - f(p0 - e)) / (2 * hh))
    return np.array(cols).T


def proj_fora(Jint, Jrot):
    Q, _ = np.linalg.qr(Jrot)
    return Jint - Q @ (Q.T @ Jint)


def sv(M):
    return np.linalg.svd(M, compute_uv=False)


def fmt(s):
    return " ".join("%.2e" % x for x in s)


def posto(s, erro, rel=1e-9):
    return int(np.sum(s > max(10 * erro, rel * s[0])))


# ------------------------------------------------------------------ invariantes de rotacao
def tensor_l2(pot):
    """Tensor simetrico sem traco A com f(n) = n.A.n para o campo real f = Re sum_m pot_2m Y_2m."""
    from harmonicos import sYlm
    rng = np.random.default_rng(0)
    n = rng.normal(size=(40, 3))
    n /= np.linalg.norm(n, axis=1)[:, None]
    th, ph = np.arccos(n[:, 2]), np.arctan2(n[:, 1], n[:, 0])
    f = np.real(sum(pot.get((2, m), 0j) * sYlm(0, 2, m, th, ph) for m in range(-2, 3)))
    X = np.stack([n[:, 0] ** 2 - n[:, 2] ** 2, n[:, 1] ** 2 - n[:, 2] ** 2, 2 * n[:, 0] * n[:, 1],
                  2 * n[:, 0] * n[:, 2], 2 * n[:, 1] * n[:, 2]], axis=1)
    c = np.linalg.lstsq(X, f, rcond=None)[0]
    return np.array([[c[0], c[2], c[3]], [c[2], c[1], c[4]], [c[3], c[4], -c[0] - c[1]]])


def potenciais(mem):
    """Potenciais escalares reais (coeficientes em Y_lm) de cada tipo."""
    from harmonicos import ethb2_de_escalar
    out = {}
    for tipo in C.TIPOS:
        d = {}
        for (l, m), a in mem[tipo].items():
            if tipo == "giroscopica":
                d[(l, m)] = a
            elif l >= 2:
                c = ethb2_de_escalar(l)
                d[(l, m)] = (2j * a / c) if tipo == "spin" else (2 * a / c)
        out[tipo] = d
    return out


def invariantes(mem, lmax=4):
    P = potenciais(mem)
    inv = []
    tipos = list(C.TIPOS)
    for l in range(0, lmax + 1):
        for i, a in enumerate(tipos):
            for b in tipos[i:]:
                if l < 2 and (a != "giroscopica" or b != "giroscopica"):
                    continue
                s = sum(P[a].get((l, m), 0j) * np.conj(P[b].get((l, m), 0j)) for m in range(-l, l + 1))
                inv.append(s.real)
    T = [tensor_l2(P[t]) for t in tipos]
    for i in range(4):
        for j in range(i, 4):
            for k in range(j, 4):
                inv.append(np.trace(T[i] @ T[j] @ T[k]))
    # invariantes que ligam l = 2 a l = 1 da giroscopica (vetor) e a l = 3 (contracao n.A.n com o campo l = 3 nao e
    # trivial; usamos so o vetor l = 1)
    g1 = P["giroscopica"]
    vz = g1.get((1, 0), 0j).real
    vxy = -np.sqrt(2) * np.conj(g1.get((1, 1), 0j))
    v = np.array([vxy.real, vxy.imag, vz])
    for Tm in T:
        inv += [v @ Tm @ v, v @ Tm @ Tm @ v]
    return np.array(inv)


# ------------------------------------------------------------------ remanescente
def remanescente(p, fit):
    q, cA, cB = p[0], list(p[1:4]), list(p[4:7])
    mf, chif, vf, _, _, _ = fit.all(q, cA, cB, omega0=np.pi * F0, omega_switch_IG=0.5 * np.pi * F0, allow_extrap=True)
    return np.concatenate([[mf], chif, vf])


def angulos_principais(A, B):
    """Angulos principais (graus) entre os espacos-coluna de A e B."""
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    s = np.clip(np.linalg.svd(Qa.T @ Qb, compute_uv=False), -1, 1)
    return np.degrees(np.arccos(s))


def analisar(nome, p0, fit, guardar):
    log("")
    log("=== %s: q %.2f chiA %s chiB %s" % (nome, p0[0], tuple(p0[1:4]), tuple(p0[4:7])))
    v0, rot, mem0, aux0 = avaliar(p0)
    f = lambda p: avaliar(p)[0]
    J1 = jac_central(f, p0, 1e-5)
    J2 = jac_central(f, p0, 5e-6)
    erro = np.linalg.norm(J1 - J2, 2)
    Jrot = np.array([C.vetor_real(C.girar_gerador(mem0, e))[0] for e in "xyz"]).T
    # conferencia por rotacao finita (init_quat), eps = 1e-5
    eps = 1e-5
    conf = []
    for k, e in enumerate("xyz"):
        u = np.zeros(3)
        u[k] = 1
        qp = np.concatenate([[np.cos(eps / 2)], np.sin(eps / 2) * u])
        qm = np.concatenate([[np.cos(eps / 2)], -np.sin(eps / 2) * u])
        d = (avaliar(p0, qp)[0] - avaliar(p0, qm)[0]) / (2 * eps)
        conf.append(min(np.linalg.norm(d - Jrot[:, k]), np.linalg.norm(d + Jrot[:, k])) / np.linalg.norm(d))
    m_idx = np.array([r[2] == 0 for r in rot])
    log("  |v| = %.4f ; |v_m!=0|/|v| = %.3f ; erro numerico ||J(1e-5) - J(5e-6)|| = %.1e ; gerador de rotacao contra"
        " init_quat (dif. relativa, x y z): %s" % (np.linalg.norm(v0), np.linalg.norm(v0[~m_idx]) / np.linalg.norm(v0),
                                                    erro, fmt(conf)))
    log("  M_f %.5f ; |J_rad| %.4f ; angulo(J_rad, z) %.2f graus ; |v_recuo| %.2e" % (
        aux0["M_f"], np.linalg.norm(aux0["J_rad"]), np.degrees(np.arccos(aux0["J_rad"][2] / np.linalg.norm(aux0["J_rad"]))),
        np.linalg.norm(aux0["P_rad"]) / aux0["M_f"]))
    sJ = sv(J1)
    sA = sv(np.concatenate([J1, Jrot], axis=1))
    sP = sv(proj_fora(J1, Jrot))
    sR = sv(Jrot)
    log("  valores singulares J_int (7):            %s  -> posto %d" % (fmt(sJ), posto(sJ, erro)))
    log("  valores singulares J_rot (3):            %s" % fmt(sR))
    log("  valores singulares [J_int | J_rot] (10): %s  -> posto %d" % (fmt(sA), posto(sA, erro)))
    log("  valores singulares P_perp J_int (7):     %s  -> posto %d (intrinsecos modulo rotacao)" % (fmt(sP), posto(sP, erro)))
    for rotulo, idx in (("m = 0", m_idx), ("m != 0", ~m_idx)):
        s1 = sv(J1[idx])
        s2 = sv(proj_fora(J1[idx], Jrot[idx])) if np.linalg.norm(Jrot[idx]) > 0 else s1
        log("    so linhas %-6s: J_int %s (posto %d) ; P_perp J_int %s (posto %d)" % (
            rotulo, fmt(s1), posto(s1, erro), fmt(s2), posto(s2, erro)))
    for tipo in C.TIPOS:
        idx = np.array([r[0] == tipo for r in rot])
        s1 = sv(proj_fora(J1[idx], Jrot[idx]))
        log("    so %-12s: P_perp J_int %s (posto %d)" % (tipo, fmt(s1), posto(s1, erro)))
    # direcoes de parametros
    _, _, Vt = np.linalg.svd(proj_fora(J1, Jrot))
    log("  direcoes de parametros (P_perp J_int), vetores singulares a direita (componentes q, chiA xyz, chiB xyz):")
    for k in range(7):
        log("    sigma %.2e : %s" % (sP[k], " ".join("%+.3f" % x for x in Vt[k])))
    # coordenadas fisicas dos spins no plano: (q, chiAz, chiBz, |chiA_perp|, |chiB_perp|, phi_medio, delta_phi)
    aA, aB = np.hypot(p0[1], p0[2]), np.hypot(p0[4], p0[5])
    if aA > 0 and aB > 0:
        fA, fB = np.arctan2(p0[2], p0[1]), np.arctan2(p0[5], p0[4])
        T = np.zeros((7, 7))           # d(chi)/d(xi)
        T[0, 0] = 1
        T[3, 1] = 1
        T[6, 2] = 1
        T[1, 3], T[2, 3] = np.cos(fA), np.sin(fA)
        T[4, 4], T[5, 4] = np.cos(fB), np.sin(fB)
        for col, (dA, dB) in ((5, (1.0, 1.0)), (6, (0.5, -0.5))):
            T[1, col], T[2, col] = -aA * np.sin(fA) * dA, aA * np.cos(fA) * dA
            T[4, col], T[5, col] = -aB * np.sin(fB) * dB, aB * np.cos(fB) * dB
        Jxi = proj_fora(J1 @ T, Jrot)
        nomes_xi = ["q", "chiAz", "chiBz", "|chiA_p|", "|chiB_p|", "phi_med", "dphi"]
        log("  coordenadas fisicas (phi_med = azimute medio dos spins no plano em relacao a n, dphi = phiA - phiB):")
        log("    |coluna de P_perp J| / |v|: " + " ".join("%s %.2e" % (nm, np.linalg.norm(Jxi[:, k]) / np.linalg.norm(v0))
                                                       for k, nm in enumerate(nomes_xi)))
        sx = sv(Jxi)
        _, _, Vx = np.linalg.svd(Jxi)
        log("    valores singulares %s ; direcao mais fraca: %s" % (fmt(sx), " ".join(
            "%s %+.3f" % (nm, x) for nm, x in zip(nomes_xi, Vx[-1]))))
        # so os 4 graus no plano, depois de projetar fora rotacoes e os 3 parametros alinhados
        Jal = np.concatenate([Jrot, J1 @ T[:, :3]], axis=1)
        Jp = proj_fora(J1 @ T[:, 3:], Jal)
        sp = sv(Jp)
        _, _, Vp = np.linalg.svd(Jp)
        log("    so os 4 graus no plano, fora de rotacoes e de (q, chiAz, chiBz): valores singulares %s" % fmt(sp))
        for k in range(4):
            log("      sigma %.2e : %s" % (sp[k], " ".join("%s %+.3f" % (nm, x) for nm, x in zip(nomes_xi[3:], Vp[k]))))
    # l <= 8
    v8f = lambda p: avaliar(p, lmax=8)[0]
    J8 = jac_central(v8f, p0, 1e-5)
    J8b = jac_central(v8f, p0, 5e-6)
    mem8 = mem0
    Jrot8 = np.array([C.vetor_real(C.girar_gerador(mem8, e), lmax=8)[0] for e in "xyz"]).T
    s8 = sv(proj_fora(J8, Jrot8))
    log("  l <= 8 (%d componentes): P_perp J_int %s (posto %d)" % (J8.shape[0], fmt(s8), posto(s8, np.linalg.norm(J8 - J8b, 2))))
    # invariantes
    fi = lambda p: invariantes(avaliar(p)[2])
    Ji = jac_central(fi, p0, 1e-5)
    Ji2 = jac_central(fi, p0, 5e-6)
    nr = np.linalg.norm(Ji, axis=1)
    ok = nr > 1e-10 * nr.max()
    Jin = Ji[ok] / nr[ok, None]
    ei = np.linalg.norm((Ji - Ji2)[ok] / nr[ok, None], 2)
    si = sv(Jin)
    log("  invariantes de rotacao (%d de %d nao nulos, linhas normalizadas): valores singulares %s ; erro %.1e ; posto %d" % (
        int(ok.sum()), Ji.shape[0], fmt(si), ei, posto(si, ei)))
    # remanescente e radiacao
    fr = lambda p: remanescente(p, fit)
    Jr = jac_central(fr, p0, 1e-4)
    fq = lambda p: np.concatenate([avaliar(p)[3]["J_rad"], avaliar(p)[3]["P_rad"]])
    Jq = jac_central(fq, p0, 1e-5)
    log("  jacobiano do remanescente (M_f, chi_f, v_f; surfinBH): valores singulares %s" % fmt(sv(Jr)))
    log("  jacobiano de (J_rad, P_rad) da janela: valores singulares %s" % fmt(sv(Jq)))
    guardar[nome] = dict(p0=p0, v0=v0, J1=J1, J2=J2, Jrot=Jrot, J8=J8, Ji=Ji, Jr=Jr, Jq=Jq, mrow=m_idx)
    log("  (%.0f s)" % (time.time() - T0))


if __name__ == "__main__":
    import surfinBH
    fit = surfinBH.LoadFits("NRSur7dq4Remnant")
    so = sys.argv[1:] or list(PONTOS)
    log("exp33_jacobiano: NRSur7dq4, nivel A (todos os modos l <= 4), janela f_22 >= %.4f, observaveis l <= 4 (88)" % F0)
    log("posto: numero de valores singulares > max(10 x erro numerico, 1e-9 x maior)")
    guardar = {}
    for n in so:
        q, cA, cB = PONTOS[n]
        analisar(n, np.array([q, *cA, *cB], float), fit, guardar)
    if not sys.argv[1:]:
        with open(os.path.join(RES, "exp33_jacobiano.txt"), "w") as fh:
            fh.write("\n".join(linhas) + "\n")
        np.savez(os.path.join(RES, "exp33_jacobianos.npz"),
                 **{"%s_%s" % (n, k): v for n, d in guardar.items() for k, v in d.items()})
