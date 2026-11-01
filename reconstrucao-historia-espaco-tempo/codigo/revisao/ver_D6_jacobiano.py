"""Verificacao adversarial D6 (L10): robustez do posto 7 (modulo rotacoes) e da hierarquia dos spins no plano.

Usa exp33_jacobiano.avaliar (mesmas memorias), mas testa o que o exp33 nao testou:
 (1) passos de diferenca finita grandes (1e-3, 1e-4) contra 1e-5 em J0 e J1;
 (2) bico em spin no plano nulo no ponto alinhado J0: diferencas laterais v(+h) - v0 e v0 - v(-h) nas 4 direcoes
     no plano, e a segunda diferenca (v(+h) + v(-h) - 2 v0)/h^2 para h = 1e-3, 1e-4, 1e-5 (cresce como 1/h se houver
     bico ~|chi_perp|);
 (3) variante de modelagem: o mesmo jacobiano com zerar_m0=True (memorias sem os m = 0 coorbitais) - quanto mudam os
     menores valores singulares (a direcao fraca e estavel sob uma mudanca de modelagem do tamanho do erro do nivel A?);
 (4) pontos novos: perto do alinhado (chi_perp = 0.02), perto da borda do dominio (q = 3.8, |chi| ~ 0.7) e
     spins grandes no plano em q ~ 1.1; hierarquia em coordenadas fisicas (|chiA_p|, |chiB_p|, phi_med, dphi).
Saida: impressa (redirecionada para resultados/ver_D6_jacobiano.txt).
"""
import os
import sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import exp33_comum as C
import exp33_jacobiano as EJ

F0 = C.F0_PADRAO


def avaliar(p, zerar=False):
    q, cA, cB = p[0], p[1:4], p[4:7]
    t, h, dyn = C.gerar7(q, cA, cB, f_ref=F0, zerar_m0=zerar)
    ti = C.instante_orbital(t, dyn["orbphase"], F0)
    mem, aux = C.memorias7(q, t, h, dyn, ti)
    del t, h, dyn
    v, rot = C.vetor_real(mem)
    return v, mem


def jac(p0, hh, zerar=False):
    cols = []
    for i in range(7):
        e = np.zeros(7)
        e[i] = hh
        cols.append((avaliar(p0 + e, zerar)[0] - avaliar(p0 - e, zerar)[0]) / (2 * hh))
    return np.array(cols).T


def proj(J, R):
    Q, _ = np.linalg.qr(R)
    return J - Q @ (Q.T @ J)


def sv_mod_rot(p0, hh, zerar=False):
    v0, mem0 = avaliar(p0, zerar)
    J = jac(p0, hh, zerar)
    R = np.array([C.vetor_real(C.girar_gerador(mem0, e))[0] for e in "xyz"]).T
    return np.linalg.svd(proj(J, R), compute_uv=False) / np.linalg.norm(v0), J, R, v0


def fisicas(p0, J, R, v0):
    aA, aB = np.hypot(p0[1], p0[2]), np.hypot(p0[4], p0[5])
    fA, fB = np.arctan2(p0[2], p0[1]), np.arctan2(p0[5], p0[4])
    T = np.zeros((7, 7))
    T[0, 0] = 1
    T[3, 1] = 1
    T[6, 2] = 1
    T[1, 3], T[2, 3] = np.cos(fA), np.sin(fA)
    T[4, 4], T[5, 4] = np.cos(fB), np.sin(fB)
    for col, (dA, dB) in ((5, (1.0, 1.0)), (6, (0.5, -0.5))):
        T[1, col], T[2, col] = -aA * np.sin(fA) * dA, aA * np.cos(fA) * dA
        T[4, col], T[5, col] = -aB * np.sin(fB) * dB, aB * np.cos(fB) * dB
    Jal = np.concatenate([R, J @ T[:, :3]], axis=1)
    Jp = proj(J @ T[:, 3:], Jal)
    _, s, Vt = np.linalg.svd(Jp)
    return s / np.linalg.norm(v0), Vt


def fmt(s):
    return " ".join("%.2e" % x for x in s)


def main():
    P = {k: np.array([q, *a, *b], float) for k, (q, a, b) in EJ.PONTOS.items()}
    P["N1 quase alinhado"] = np.array([1.5, 0.02, 0.0, 0.4, 0.0, 0.02, -0.3])
    P["N2 borda q=3.8"] = np.array([3.8, 0.6, 0.3, 0.3, -0.4, 0.5, -0.2])
    P["N3 q=1.1 spins grandes"] = np.array([1.1, 0.75, 0.0, 0.1, 0.0, 0.7, 0.1])
    print("(1) passos de diferenca finita: valores singulares de P_perp J / |v|")
    for k in ("J0", "J1"):
        for hh in (1e-3, 1e-4, 1e-5):
            s, *_ = sv_mod_rot(P[k], hh)
            print("  %s h %.0e: %s" % (k, hh, fmt(s)))
    print("(2) bico em chi_perp = 0 no alinhado J0 (direcoes chiAx, chiAy, chiBx, chiBy)")
    p0 = P["J0"]
    v0 = avaliar(p0)[0]
    for i, nm in ((1, "chiAx"), (2, "chiAy"), (4, "chiBx"), (5, "chiBy")):
        lin = []
        for hh in (1e-3, 1e-4, 1e-5):
            e = np.zeros(7)
            e[i] = hh
            vp, vm = avaliar(p0 + e)[0], avaliar(p0 - e)[0]
            dp, dm = (vp - v0) / hh, (v0 - vm) / hh
            d2 = (vp + vm - 2 * v0) / hh ** 2
            lin.append("h %.0e: |D+ - D-|/|D+| %.2e, |segunda dif| %.2e" % (
                hh, np.linalg.norm(dp - dm) / np.linalg.norm(dp), np.linalg.norm(d2)))
        print("  %s: %s" % (nm, " ; ".join(lin)))
    # mesmo teste numa direcao aligned de controle (chiAz) para comparar a segunda diferenca
    lin = []
    for hh in (1e-3, 1e-4, 1e-5):
        e = np.zeros(7)
        e[3] = hh
        vp, vm = avaliar(p0 + e)[0], avaliar(p0 - e)[0]
        lin.append("h %.0e: |segunda dif| %.2e" % (hh, np.linalg.norm((vp + vm - 2 * v0) / hh ** 2)))
    print("  controle chiAz: %s" % " ; ".join(lin))
    print("(3) variante sem os m = 0 coorbitais (zerar_m0=True), passo 1e-4")
    for k in ("J0", "J1", "J2", "J4"):
        s1, J1, R1, va = sv_mod_rot(P[k], 1e-4)
        s2, J2, R2, vb = sv_mod_rot(P[k], 1e-4, zerar=True)
        print("  %s: normal %s" % (k, fmt(s1)))
        print("  %s: sem m0  %s ; ||J_sem - J||/||J|| = %.2e ; razao dos menores sv %.2f" % (
            k, fmt(s2), np.linalg.norm(J2 - J1, 2) / np.linalg.norm(J1, 2), s2[-1] / s1[-1]))
        if k in ("J1", "J2"):
            f1, V1 = fisicas(P[k], J1, R1, va)
            f2, V2 = fisicas(P[k], J2, R2, vb)
            print("      fisicas normal %s ; mais fraca %s" % (fmt(f1), " ".join("%+.2f" % x for x in V1[-1])))
            print("      fisicas sem m0 %s ; mais fraca %s" % (fmt(f2), " ".join("%+.2f" % x for x in V2[-1])))
    print("(4) pontos novos (passos 1e-4 e 1e-5)")
    for k in ("N1 quase alinhado", "N2 borda q=3.8", "N3 q=1.1 spins grandes"):
        sa, Ja, Ra, va = sv_mod_rot(P[k], 1e-4)
        sb, Jb, Rb, vb = sv_mod_rot(P[k], 1e-5)
        err = np.linalg.norm(Ja - Jb, 2) / np.linalg.norm(va)
        print("  %s %s: P_perp J/|v| (1e-4) %s ; (1e-5) %s ; ||dJ||/|v| %.1e" % (k, P[k].tolist(), fmt(sa), fmt(sb), err))
        f, V = fisicas(P[k], Jb, Rb, vb)
        print("      4 graus no plano (|chiA_p|, |chiB_p|, phi_med, dphi): %s" % fmt(f))
        for j in range(4):
            print("        sigma %.2e : %s" % (f[j], " ".join("%+.3f" % x for x in V[j])))


if __name__ == "__main__":
    main()
