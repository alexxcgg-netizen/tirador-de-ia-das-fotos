"""Experimento 17 (L01): dados dos jacobianos das memorias no observador numa grade de parametros.

Grade: q em {1, 1.2, 2, 3, 5}, chi1, chi2 em {-0.6, 0, 0.6}, M em {30, 65, 120} M_sol; janela desde 10 Hz;
NRHybSur3dq8_CCE, nivel A, deslocamento de janela, todos os (l, m) com l <= 8 (exp17_comum.memorias_varias).
Para cada (q, chi1, chi2): onda base e diferencas centrais em q, chi1, chi2 com passos h, h/2, h/4
(h = 4e-3; o ruido do substituto em q e chi e ~3e-10, verif_L00), e em ln M com h = 1e-4, 1e-4/2, 1e-4/4 (as
janelas de varios M saem da mesma onda). q - h < 1 usa a simetria de troca (exp17_comum.gerar_base).
Guarda so os multipolos (referenciais 'pico', com o termo de borda inicial dos m != 0 suprimido, e 'ti' na onda
base) e os auxiliares. A analise (SVD, posto, loci) esta em exp17_analise_jac.py.
Saida: resultados/exp17_jacobianos_dados.npz (grade) e resultados/exp17_jac_A.npz (argumento 'A': ponto A do exp07).
Os arquivos por ponto ficam em resultados/exp17_jac_tmp (apagado depois de consolidado).
"""
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

QS = (1.0, 1.2, 2.0, 3.0, 5.0)
CHIS = (-0.6, 0.0, 0.6)
MS = (30.0, 65.0, 120.0)
H_INT = 4e-3
H_LNM = 1e-4
FRACS = (1.0, 0.5, 0.25)
SAIDA = os.path.join(AQUI, "..", "resultados", "exp17_jacobianos_dados.npz")
TMP = os.path.join(AQUI, "..", "resultados", "exp17_jac_tmp")


def chaves():
    import exp17_comum as C
    r = C.memorias_varias(1.2, 0.3, -0.2, [120.0])[0]
    return {t: sorted(r["mem_pico"][t]) for t in C.TIPOS}


def vetor(mem, K):
    import exp17_comum as C
    return np.concatenate([np.array([mem[t][k] for k in K[t]]) for t in C.TIPOS])


def ponto(arg):
    os.environ["OMP_NUM_THREADS"] = "1"
    q, c1, c2, K = arg
    nome = os.path.join(TMP, "p_%.2f_%+.2f_%+.2f.npz" % (q, c1, c2))
    if os.path.exists(nome):
        return nome
    import exp17_comum as C
    t0 = time.time()
    # base: todos os M e os passos em ln M
    lista = []
    for M0 in MS:
        lista.append(M0)
        for fr in FRACS:
            lista += [M0 * np.exp(fr * H_LNM), M0 * np.exp(-fr * H_LNM)]
    res = C.memorias_varias(q, c1, c2, lista)
    base_pico = np.array([vetor(r["mem_pico"], K) for r in res])
    base_ti = np.array([vetor(r["mem_ti"], K) for r in res])
    aux = np.array([[r["aux"][k] for k in ("M_f", "E_janela", "E_lig", "t_i", "x_i", "Phi_pico")] for r in res])
    borda = np.array([[r["aux"]["borda"][t] for t in C.TIPOS] for r in res])
    # variacoes intrinsecas
    var = {}
    for j, nomep in enumerate(("q", "c1", "c2")):
        for fr in FRACS:
            for sg in (+1, -1):
                p = [q, c1, c2]
                p[j] += sg * fr * H_INT
                rr = C.memorias_varias(p[0], p[1], p[2], list(MS))
                var[(j, fr, sg)] = (np.array([vetor(r["mem_pico"], K) for r in rr]),
                                    np.array([r["aux"]["M_f"] for r in rr]))
    V = np.zeros((3, len(FRACS), 2, len(MS), base_pico.shape[1]), dtype=complex)
    VMf = np.zeros((3, len(FRACS), 2, len(MS)))
    for (j, fr, sg), (v, mf) in var.items():
        V[j, FRACS.index(fr), 0 if sg > 0 else 1] = v
        VMf[j, FRACS.index(fr), 0 if sg > 0 else 1] = mf
    np.savez(nome, base_pico=base_pico, base_ti=base_ti, aux=aux, borda=borda, V=V, VMf=VMf,
             lista=np.array(lista), tempo=time.time() - t0)
    print("ponto q=%.2f chi=(%+.1f,%+.1f): %.0f s" % (q, c1, c2, time.time() - t0), flush=True)
    return nome


if __name__ == "__main__":
    import multiprocessing as mp
    os.makedirs(TMP, exist_ok=True)
    K = chaves()
    pontos = [(q, c1, c2, K) for q in QS for c1 in CHIS for c2 in CHIS]
    if len(sys.argv) > 1 and sys.argv[1] == "A":            # ponto A do exp07 (fora da grade)
        import shutil
        shutil.copy(ponto((1.2, 0.3, -0.2, K)), os.path.join(AQUI, "..", "resultados", "exp17_jac_A.npz"))
        sys.exit(0)
    if len(sys.argv) > 1:                                  # subconjunto: indices i0:i1
        i0, i1 = map(int, sys.argv[1].split(":"))
        pontos = pontos[i0:i1]
    t0 = time.time()
    with mp.get_context("spawn").Pool(2) as pool:
        nomes = pool.map(ponto, pontos, chunksize=1)
    print("total %.0f s" % (time.time() - t0))
    todos = [(q, c1, c2) for q in QS for c1 in CHIS for c2 in CHIS]
    if all(os.path.exists(os.path.join(TMP, "p_%.2f_%+.2f_%+.2f.npz" % p)) for p in todos):
        dados = {}
        for i, p in enumerate(todos):
            z = np.load(os.path.join(TMP, "p_%.2f_%+.2f_%+.2f.npz" % p))
            for k in z.files:
                dados.setdefault(k, []).append(z[k])
        out = {k: np.array(v) for k, v in dados.items()}
        out["pontos"] = np.array(todos)
        out["MS"] = np.array(MS)
        out["FRACS"] = np.array(FRACS)
        out["H_INT"] = H_INT
        out["H_LNM"] = H_LNM
        for t in K:
            out["chaves_" + t] = np.array(K[t])
        np.savez_compressed(SAIDA, **out)
        print("gravado", SAIDA)
