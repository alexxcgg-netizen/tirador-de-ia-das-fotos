"""Experimento 27 (L06): conjunto de binarias e observaveis de memoria (com e sem ruido) para informacao mutua e
aprendizado de maquina.

Binarias intrinsecas (Sobol embaralhado): M em [40, 120], q em [1, 4], chi1, chi2 em [-0.8, 0.8]; para cada uma,
K = 4 sorteios extrinsecos: cos iota uniforme em [-1, 1], D com densidade ~ D^2 em [200, 1000] Mpc, phi uniforme.
Detector: rede ideal de dois detectores co-localizados a 45 graus (mede h+ e hx; psi = 0 conhecido), mesma PSD.
Observaveis guardados por amostra (so numeros):
  (a) as quatro memorias integradas no observador, janela desde 10 Hz, todos os (l, m) (com phi);
  (b) as mensuraveis: deslocamento de janela e spin (das mesmas);
  (c) resumos da serie de memoria nula (CE e ET):
      c1 MOPED com os 8 vetores do fiducial A (rede): y_i = (u1_i|h+) + (u2_i|hx), no tempo de chegada verdadeiro;
      c2 banco de 6 moldes h+ (q = 1, chi = 0, iota = 90 graus, M = 40..120) e 3 moldes hx (iota = 60 graus,
         M = 50, 80, 110): max_tau |(T|x(.-tau))|/|T| (invariante no tempo);
      c3 potencia branqueada em bandas: h+ em [10,20,40,80,160,320,1000] Hz e hx em [10,40,160,1000] Hz;
  cada um sem ruido e com uma realizacao de ruido gaussiano da PSD (CE e ET).
Uso: python exp27_conjunto.py <parte> <n_partes> <n_intrinsecas>
Saida: resultados/exp27_conjunto_<parte>.npz
"""
import multiprocessing as mp
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DF = 1.0 / 32
FMAXC = 1000.0
K_EXT = 4
PSDS = ("CE", "ET")
BANDAS_P = [10, 20, 40, 80, 160, 320, 1000]
BANDAS_X = [10, 40, 160, 1000]
MASSAS_P = [40, 55, 70, 85, 100, 120]
MASSAS_X = [50, 80, 110]
TIPOS = ("deslocamento", "spin", "cm", "giroscopica")


def _init():
    global C, O, G
    import exp24_comum as C_
    import observaveis as O_
    from deteccao import MSUN_S, MPC_S, psd_serie
    from scipy.interpolate import CubicSpline
    C, O = C_, O_
    f = np.arange(0, FMAXC + DF / 2, DF)
    A = dict(C.SIST_A)
    G = dict(f=f, MSUN_S=MSUN_S, MPC_S=MPC_S, W={}, S={}, u1={}, u2={})
    for p in PSDS:
        G["W"][p] = C.psd_grade(p, len(f), DF)
        Sraw = psd_serie(p, len(f), DF, 9.0)
        G["S"][p] = np.where(G["W"][p] > 0, Sraw, 0.0)
    # fiducial A: vetores MOPED (rede: psi = 0 e psi = pi/4)
    s1, d1 = C.derivadas_grade(dict(A, psi=0.0), f)
    s2, d2 = C.derivadas_grade(dict(A, psi=np.pi / 4), f)
    G["u1"] = [d1[n] for n in C.NOMES8]
    G["u2"] = [d2[n] for n in C.NOMES8]
    G["rhoA"] = {p: (np.sqrt(C.produto(s1, s1, G["W"][p], DF)), np.sqrt(C.produto(s2, s2, G["W"][p], DF))) for p in PSDS}
    # banco de moldes
    G["bank_p"], G["bank_x"] = [], []
    for Mk in MASSAS_P:
        E = C.EspectroMemoria(1.0, 0.0, 0.0, Mk, 10.0, N=2 ** 19, Fmax=0.8)
        Ms = Mk * MSUN_S
        G["bank_p"].append(Ms * Ms * CubicSpline(E.F, E.canais(np.pi / 2)[0])(Ms * f))
    for Mk in MASSAS_X:
        E = C.EspectroMemoria(1.0, 0.0, 0.0, Mk, 10.0, N=2 ** 19, Fmax=0.8)
        Ms = Mk * MSUN_S
        G["bank_x"].append(Ms * Ms * CubicSpline(E.F, E.canais(np.radians(60.0))[1])(Ms * f))
    del E
    # memorias integradas de A (para os erros de (a) e (b))
    mem, aux = O.memorias_observaveis(A["q"], A["c1"], A["c2"], A["M"], 10.0, todos_m=True)
    v = O.valores_fisicos_completo(mem, A["iota"], 0.0, A["M"], A["D"])
    G["yA"] = np.array([v[t] for t in TIPOS])


def _resumos(hp, hx, p, rng):
    """Resumos c1, c2, c3 sem e com ruido para a PSD p."""
    f, w = G["f"], G["W"][p]
    out = {}
    nf = len(f)
    sig = np.sqrt(G["S"][p] / (4 * DF))
    n1 = sig * (rng.standard_normal(nf) + 1j * rng.standard_normal(nf))
    n2 = sig * (rng.standard_normal(nf) + 1j * rng.standard_normal(nf))
    for rot, xp, xx in (("0", hp, hx), ("n", hp + n1, hx + n2)):
        out["moped_" + rot] = np.array([C.produto(u, xp, w, DF) + C.produto(v, xx, w, DF)
                                        for u, v in zip(G["u1"], G["u2"])])
        bk = []
        for T in G["bank_p"]:
            Ov, _ = C.overlap_tempo(xp, T, w, DF, up=1)
            bk.append(np.max(np.abs(Ov)) / np.sqrt(C.produto(T, T, w, DF)))
        for T in G["bank_x"]:
            Ov, _ = C.overlap_tempo(xx, T, w, DF, up=1)
            bk.append(np.max(np.abs(Ov)) / np.sqrt(C.produto(T, T, w, DF)))
        out["banco_" + rot] = np.array(bk)
        bd = []
        for x, bandas in ((xp, BANDAS_P), (xx, BANDAS_X)):
            for a, b in zip(bandas[:-1], bandas[1:]):
                sel = (f >= a) & (f < b)
                bd.append(4 * DF * np.sum(np.abs(x[sel]) ** 2 * w[sel]))
        out["bandas_" + rot] = np.array(bd)
    out["rho"] = np.array([np.sqrt(C.produto(hp, hp, w, DF)), np.sqrt(C.produto(hx, hx, w, DF))])
    return out


def _binaria(args):
    from scipy.interpolate import CubicSpline
    i, M, q, c1, c2, ext, seed = args
    rng = np.random.default_rng(seed)
    t1 = time.time()
    try:
        t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)
        mem, aux = O.memorias_observaveis(q, c1, c2, M, 10.0, t=t, h=h, t_i=ti, todos_m=True)
        mem0 = {tp: {k: v for k, v in mem[tp].items() if k[1] == 0} for tp in mem}
        E = C.EspectroMemoria(q, c1, c2, M, 10.0, N=2 ** 19, Fmax=0.8, t=t, h=h, t_i=ti)
    except Exception as ex:
        return [dict(i=i, erro=str(ex))]
    del t, h
    Ms = M * G["MSUN_S"]
    F = Ms * G["f"]
    P = CubicSpline(E.F, E.Sp_)(F)
    X = CubicSpline(E.F, E.Sx_)(F)
    final = E.final.copy()
    del E
    eta = q / (1 + q) ** 2
    res = []
    for (cosi, D, phi) in ext:
        iota = float(np.arccos(cosi))
        v = O.valores_fisicos_completo(mem, iota, phi, M, D)
        v0 = O.valores_fisicos_completo(mem0, iota, phi, M, D)
        Y = C._Ylist(iota)
        k = Ms * Ms / (D * G["MPC_S"])
        hp, hx = k * (P @ Y), k * (X @ Y)
        r = dict(i=i, M=M, q=q, c1=c1, c2=c2, cosi=cosi, D=D, phi=phi, eta=eta, Mf=aux["M_f"] * M,
                 integ=np.array([v[tp] for tp in TIPOS]), integ_m0=np.array([v0[tp] for tp in TIPOS]),
                 degrau_serie=float(np.real(final @ Y)) * Ms / (D * G["MPC_S"]), tempo=time.time() - t1)
        for p in PSDS:
            for kk, vv in _resumos(hp, hx, p, rng).items():
                r[p + "_" + kk] = vv
        res.append(r)
    return res


def main():
    parte, n_partes, n_int = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    from scipy.stats import qmc
    u = qmc.Sobol(d=4, scramble=True, seed=27).random(n_int)
    rng = np.random.default_rng(1000 + 0)
    ext_all = []
    for j in range(n_int):
        e = []
        for _ in range(K_EXT):
            cosi = rng.uniform(-1, 1)
            D = (200.0 ** 3 + rng.uniform() * (1000.0 ** 3 - 200.0 ** 3)) ** (1 / 3)
            phi = rng.uniform(0, 2 * np.pi)
            e.append((cosi, D, phi))
        ext_all.append(e)
    tarefas = []
    for j in range(n_int):
        if j % n_partes != parte:
            continue
        M = 40 + 80 * u[j, 0]
        q = 1 + 3 * u[j, 1]
        c1 = -0.8 + 1.6 * u[j, 2]
        c2 = -0.8 + 1.6 * u[j, 3]
        tarefas.append((j, M, q, c1, c2, ext_all[j], 10_000 + j))
    t0 = time.time()
    ctx = mp.get_context("spawn")
    linhas = []
    with ctx.Pool(2, initializer=_init) as pool:
        for k, r in enumerate(pool.imap_unordered(_binaria, tarefas, chunksize=2)):
            linhas += r
            if k % 25 == 0:
                print("%d/%d %.0f s" % (k + 1, len(tarefas), time.time() - t0), flush=True)
    ok = [r for r in linhas if "erro" not in r]
    erros = [r for r in linhas if "erro" in r]
    chaves = [kk for kk in ok[0].keys()]
    dados = {kk: np.array([r[kk] for r in ok]) for kk in chaves}
    _init()
    dados["yA"] = G["yA"]
    dados["rhoA_CE"] = np.array(G["rhoA"]["CE"])
    dados["rhoA_ET"] = np.array(G["rhoA"]["ET"])
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "exp27_conjunto_%d.npz" % parte)
    np.savez_compressed(saida, **dados)
    print("parte %d: %d amostras, %d erros, %.0f s" % (parte, len(ok), len(erros), time.time() - t0))
    for r in erros[:5]:
        print("erro", r)


if __name__ == "__main__":
    main()
