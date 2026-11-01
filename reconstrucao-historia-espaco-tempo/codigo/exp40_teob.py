"""Experimento 40, parte 4 (linha L16, tarefa 4): tentativa de checar a dependencia na anomalia com um segundo
modelo EOB excentrico (TEOBResumS-Dali), independente do SEOBNRv5EHM.

Resultado: o TEOBResumS 4.4.1 instalado (EOBRun_module) IGNORA os parametros excentricos (ecc, ecc_freq, anomaly):
as saidas sao identicas bit a bit as do caso circular (mesma duracao, mesma amplitude, dinamica sem variaveis
excentricas). E o ramo quase circular; o ramo Dali nao esta disponivel aqui. Este script so documenta a conferencia.
Saida: resultados/exp40_teob.txt
"""
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")


def rodar(extra):
    import EOBRun_module as EOB
    p = dict(M=65., q=1.2, chi1=0.3, chi2=-0.2, LambdaAl2=0., LambdaBl2=0., distance=1., inclination=0.,
             coalescence_angle=0., domain=0, arg_out="yes", use_mode_lm=[1], output_hpc="no", output_multipoles="no",
             srate_interp=4096., use_geometric_units="yes", initial_frequency=65.0 * 4.925490947641267e-06 * 10.0,
             interp_uniform_grid="yes")
    p.update(extra)
    t, _, _, hlm, dyn = EOB.EOBRunPy(p)
    return np.asarray(t), np.asarray(hlm["1"][0]), np.asarray(hlm["1"][1]), sorted(dyn.keys())


if __name__ == "__main__":

    from importlib.metadata import version
    linhas = ["exp40_teob: TEOBResumS %s honra a excentricidade?" % version("teobresums")]
    t0, A0, f0, k0 = rodar(dict(ecc=0.0))
    for extra in (dict(ecc=0.2), dict(ecc=0.2, ecc_freq=2, anomaly=1.0), dict(ecc=0.3, ecc_freq=1, anomaly=2.0)):
        t, A, f, k = rodar(extra)
        igual = len(t) == len(t0) and np.array_equal(A, A0) and np.array_equal(f, f0)
        linhas.append("  %s: duracao %.1f M (circular %.1f M) ; amplitude e fase do (2,2) identicas bit a bit ao circular: %s"
                      % (extra, t[-1] - t[0], t0[-1] - t0[0], igual))
    linhas.append("  colunas da dinamica: %s (sem variaveis excentricas)" % k0)
    linhas.append("  conclusao: este build e o ramo quase circular; a checagem com um 2o modelo excentrico nao foi possivel.")
    with open(os.path.join(RES, "exp40_teob.txt"), "w") as fh:
        fh.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))
