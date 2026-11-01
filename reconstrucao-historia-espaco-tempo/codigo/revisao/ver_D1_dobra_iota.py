"""Verificacao adversarial D1 (H1.6b): dobra do problema quadrado (iota e D conhecidos, T0) em iota ~ 37 graus no ponto A.

Caminho independente (observaveis.memorias_observaveis, m = 0): multipolos em p e p +- h (q, chi: 1e-2 e 2e-3;
ln M: 1e-3 e 2e-4) e projecao numa grade fina de iota (20 a 85 graus, passo 0.25). Para cada iota: det e sigma_min
do jacobiano intrinseco 4x4 (escala abs: linhas / |F(iota = 50)|) com os dois passos; troca de sinal do det.
Tambem em dois outros pontos (fora da grade do exp17), para ver se as dobras sao genericas.
Saida: resultados/ver_D1_dobra_iota.txt
"""
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
SAIDA = os.path.join(AQUI, "..", "..", "resultados", "ver_D1_dobra_iota.txt")
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")
IOTAS = np.radians(np.arange(20.0, 85.01, 0.25))


def mult(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    import observaveis as O
    lnM, q, c1, c2 = arg
    M = float(np.exp(lnM))
    m, a = O.memorias_observaveis(q, c1, c2, M, 10.0)
    out = np.zeros((len(IOTAS) + 1, 4))
    for i, io in enumerate(list(IOTAS) + [np.radians(50.0)]):
        v = O.valores_fisicos_completo(m, io, 0.0, M, 400.0)
        out[i] = [v[k] for k in TIPOS]
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    PASSOS = [np.array([1e-3, 1e-2, 1e-2, 1e-2]), np.array([2e-4, 2e-3, 2e-3, 2e-3])]
    pontos = {"A": np.array([np.log(65.0), 1.2, 0.3, -0.2]),
              "q2.5 (-0.3,+0.5) M45": np.array([np.log(45.0), 2.5, -0.3, 0.5]),
              "q4 (+0.5,+0.5) M80": np.array([np.log(80.0), 4.0, 0.5, 0.5])}
    args, chave = [], []
    for nome, p0 in pontos.items():
        args.append(tuple(p0))
        chave.append((nome, None, 0, 0))
        for ih, h in enumerate(PASSOS):
            for k in range(4):
                for sg in (1, -1):
                    p = p0.copy()
                    p[k] += sg * h[k]
                    args.append(tuple(p))
                    chave.append((nome, ih, k, sg))
    with mp.get_context("spawn").Pool(2) as pool:
        res = pool.map(mult, args, chunksize=1)
    R = dict(zip(chave, res))
    L = []
    for nome in pontos:
        base = R[(nome, None, 0, 0)]
        s = 1 / np.abs(base[-1])
        dets, smins = [], []
        for ih, h in enumerate(PASSOS):
            Jt = np.zeros((len(IOTAS), 4, 4))
            for k in range(4):
                Jt[:, :, k] = (R[(nome, ih, k, 1)][:-1] - R[(nome, ih, k, -1)][:-1]) / (2 * h[k])
            Js = Jt * s[None, :, None]
            dets.append(np.linalg.det(Js))
            smins.append(np.linalg.svd(Js, compute_uv=False)[:, -1])
        L.append("== %s: troca de sinal de det(J intrinseco 4x4), escala abs, iota de 20 a 85 graus (passo 0.25)" % nome)
        for ih in range(2):
            d = dets[ih]
            tr = np.nonzero(np.sign(d[1:]) != np.sign(d[:-1]))[0]
            L.append("  passos %s: trocas entre %s graus" % (PASSOS[ih].tolist(),
                                                            ["%.2f-%.2f" % (np.degrees(IOTAS[i]), np.degrees(IOTAS[i + 1])) for i in tr]))
            for i in tr:
                L.append("     sigma_min em %.2f e %.2f: %.2e, %.2e ; |J(h1)-J(h2)| relativo nesses pontos: dif. de sigma_min %.1e"
                         % (np.degrees(IOTAS[i]), np.degrees(IOTAS[i + 1]), smins[ih][i], smins[ih][i + 1],
                            abs(smins[0][i] - smins[1][i])))
        j = int(np.argmin(np.abs(np.degrees(IOTAS) - 50.0)))
        L.append("  sigma_min em 50 graus: %.3e (passo 1), %.3e (passo 2); min sobre iota: %.2e em %.2f graus"
                 % (smins[0][j], smins[1][j], smins[1].min(), np.degrees(IOTAS[np.argmin(smins[1])])))
        L.append("")
    print("\n".join(L))
    with open(SAIDA, "w") as fh:
        fh.write("\n".join(L) + "\n")
