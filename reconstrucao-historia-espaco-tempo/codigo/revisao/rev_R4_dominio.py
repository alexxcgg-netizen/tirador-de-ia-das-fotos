"""Revisor R4, tarefa 3: e0 = 0.3 em "10 Hz" esta no dominio do SEOBNRv5EHM? O modelo emite avisos?

O exp12 chama generate_modes_opt(q, chi1, chi2, omega_start = pi M f, ...), com f = 10 Hz e o ajuste padrao
EccIC = 1: omega_start e a frequencia orbital MEDIA (orbit-averaged); a frequencia de onda (2,2) media e 10 Hz
(frequencia orbital media 5 Hz).
Para cada configuracao, com debug = True, registra:
  - separacao inicial r_start (o modelo integra para tras equacoes seculares se r_start < r_start_min = 10 M);
  - e(t) e a anomalia z(t) da dinamica (colunas 5 e 6 de model.dynamics), e quando a frequencia media
    chega a 20 Hz de onda (x = x0 * 2^(2/3), coluna 7), e no fim da inspiral (o modelo aborta se e_fim > 0.25);
  - avisos (logging do pyseobnr e warnings do Python) e excecoes.
Tambem procura o limite em e0 para a configuracao A (e0 = 0.4 ... 0.8).
Saida: resultados/revisao/rev_R4_dominio.txt
"""
import logging
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

logging.getLogger("pyseobnr").setLevel(logging.DEBUG)
linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def examinar(nome, q, c1, c2, M, e0, l0=0.0):
    f0 = M * C.Dt.MSUN_S * C.F_FIS
    n0 = len(C.COLETOR.msgs)
    try:
        t, h, mod = C.gerar(q, c1, c2, f0, e0, l0, debug=True)
    except Exception as exc:                            # fora do dominio
        novos = C.COLETOR.msgs[n0:]
        log("  %-34s FALHOU: %s" % (nome, str(exc)[:220]))
        for s in novos[:2]:
            log("      log: " + s[:260])
        return
    dyn = mod.dynamics
    x = dyn[:, 7]
    x0 = (np.pi * f0) ** (2 / 3)
    x20 = x0 * 2 ** (2 / 3)
    i20 = np.searchsorted(x, x20) if x[-1] > x20 else None
    e20 = dyn[i20, 5] if i20 is not None else np.nan
    novos = C.COLETOR.msgs[n0:]
    log("  %-34s r_start = %.2f M ; e no inicio %.4f (pedido %.2f) ; e em 20 Hz %.4f ; e no fim da inspiral %.4f (r = %.2f M) ; duracao %.0f M ; avisos %d"
        % (nome, mod.r_start, dyn[0, 5], e0, e20, dyn[-1, 5], dyn[-1, 1], t[-1] - t[0], len(novos)))
    for s in novos[:3]:
        log("      log: " + s[:300])
    del t, h, mod, dyn


if __name__ == "__main__":
    t0 = time.time()
    log("Tarefa 3: dominio do SEOBNRv5EHM nas configuracoes do exp12 (EccIC = 1: omega_start = frequencia orbital media; f_onda media = 10 Hz)")
    log("  limites no codigo do pyseobnr 0.3.7: 0 <= e0 < 1; r_start < 10 M => integracao secular para tras (aviso);")
    log("  e_fim > 0.25 no fim da inspiral => erro; r0 PN < 6 M => erro; ICs com desvio > 1% em r ou > 1.5% em pphi => erro.")
    log()
    log("Configuracoes do exp12:")
    examinar("A (q=1.2, chi=(.3,-.2), M=65) e0=0", 1.2, 0.3, -0.2, 65.0, 0.0)
    for e0 in (0.1, 0.2, 0.3):
        examinar("A-exc. e0=%.1f" % e0, 1.2, 0.3, -0.2, 65.0, e0)
    examinar("B e0=0.3 qB=2 (M 73.23, chi1 .183)", 2.0, 0.18331746249982117, 0.0, 73.2318162082271, 0.3)
    examinar("B e0=0.3 qB=1.2 (M 67.39, chi1 .671)", 1.2, 0.6706318745992426, -0.2, 67.39032577550046, 0.3)
    examinar("B e0=0.2 qB=2, l0 = pi", 2.0, 0.05960457850002948, 0.0, 72.5875185658003, 0.2, np.pi)
    examinar("B e0=0.3 qB=2, l0 = pi", 2.0, 0.18331746249982117, 0.0, 73.2318162082271, 0.3, np.pi)
    log()
    log("Procura do limite em e0 (configuracao A, l0 = 0 e pi):")
    for e0 in (0.4, 0.5, 0.6, 0.7, 0.8):
        for l0 in (0.0, np.pi):
            examinar("A e0=%.1f l0=%.0f pi" % (e0, l0 / np.pi), 1.2, 0.3, -0.2, 65.0, e0, l0)
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(C.RES, "rev_R4_dominio.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
