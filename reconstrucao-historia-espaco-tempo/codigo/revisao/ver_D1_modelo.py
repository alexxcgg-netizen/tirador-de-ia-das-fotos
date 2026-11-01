"""Verificacao adversarial D1: o 4o valor singular intrinseco de T0 (~1e-3) e robusto a troca de modelo?

O relatorio admite que sigma4 intrinseco (9.5e-4 em A) esta na ordem do erro do substituto (violacao da simetria de
troca ~1e-3). Teste direto: mesmo calculo (T0, m = 0, nivel A, deslocamento de janela, escala abs) com
NRHybSur3dq8_CCE e com NRHybSur3dq8 (outro substituto, mesmos modos oscilatorios de entrada: binarias.lista_osc()),
via exp17_comum.memorias_varias(modelo=...). Passos: ln M 2e-4, q e chi 2e-3 (diferencas centrais).
Saida: resultados/ver_D1_modelo.txt
"""
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_modelo.txt")
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")
IO = np.radians(50.0)
HM, HI = 2e-4, 2e-3


def avalia(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    import exp17_comum as C
    modelo, q, c1, c2, Ms = arg
    rs = C.memorias_varias(q, c1, c2, list(Ms), media=False, modelo=modelo)
    return [C.vetor_fisico(C.so_m0(r["mem_ti"]), IO, 0.0, M, 400.0) for r, M in zip(rs, Ms)]


if __name__ == "__main__":
    import multiprocessing as mp
    pts = [(1.2, 0.3, -0.2, 65.0), (2.0, 0.0, 0.0, 65.0), (3.0, 0.6, 0.0, 65.0)]
    args, keys = [], []
    for modelo in ("NRHybSur3dq8_CCE", "NRHybSur3dq8"):
        for (q, c1, c2, M) in pts:
            args.append((modelo, q, c1, c2, (M, M * np.exp(HM), M * np.exp(-HM))))
            keys.append((modelo, (q, c1, c2, M), "base"))
            for k in range(3):
                for sg in (1, -1):
                    p = [q, c1, c2]
                    p[k] += sg * HI
                    args.append((modelo, p[0], p[1], p[2], (M,)))
                    keys.append((modelo, (q, c1, c2, M), (k, sg)))
    with mp.get_context("spawn").Pool(2) as pool:
        res = pool.map(avalia, args, chunksize=1)
    R = dict(zip(keys, res))
    L = ["T0 intrinseco (ln M, q, chi1, chi2), iota = 50 graus, D = 400 Mpc, escala abs; dois substitutos"]
    for (q, c1, c2, M) in pts:
        out = {}
        for modelo in ("NRHybSur3dq8_CCE", "NRHybSur3dq8"):
            b = R[(modelo, (q, c1, c2, M), "base")]
            F0 = b[0]
            J = np.zeros((4, 4))
            J[:, 0] = (b[1] - b[2]) / (2 * HM)
            for k in range(3):
                J[:, k + 1] = (R[(modelo, (q, c1, c2, M), (k, 1))][0] - R[(modelo, (q, c1, c2, M), (k, -1))][0]) / (2 * HI)
            Js = J / np.abs(F0)[:, None]
            U, sv, Vt = np.linalg.svd(Js)
            out[modelo] = (F0, Js, sv, Vt[-1] * np.sign(Vt[-1][1]), U[:, -1] * np.sign(U[1, -1]))
            L.append("  (%.1f, %+.1f, %+.1f) %-17s sigma = %s ; v = %s ; u = %s" % (q, c1, c2, modelo,
                                                                              np.array2string(sv, precision=4),
                                                                              np.array2string(out[modelo][3], precision=3),
                                                                              np.array2string(out[modelo][4], precision=3)))
        a, b = out["NRHybSur3dq8_CCE"], out["NRHybSur3dq8"]
        L.append("     F(sem CCE)/F(CCE) - 1 = %s ; ||J_semCCE - J_CCE||_F (abs) = %.2e ; angulo entre v: %.1f graus"
                 % (np.array2string(b[0] / a[0] - 1, precision=2), np.linalg.norm(b[1] - a[1]),
                    np.degrees(np.arccos(min(1, abs(a[3] @ b[3]))))))
    print("\n".join(L))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
