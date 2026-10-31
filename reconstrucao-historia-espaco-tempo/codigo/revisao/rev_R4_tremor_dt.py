"""Revisor R4, tarefa 1 (diagnostico): o "piso numerico" ~1e-5 do SEOBNRv5EHM depende do passo de tempo?

O pyseobnr e deterministico (rev_R4_ruido_pares), mas M_B -> M_B (1 + 1e-12) muda as memorias em ~5e-6.
Aqui: B (e0 = 0.2, q_B = 2) do exp12 com M_B (1 + k 1e-12), k = 0..4, para tres passos da grade de saida
(settings["dt"]: 0.1 M = padrao do exp12, 0.05 M e 0.025 M). Mede a dispersao (max - min)/|media| de cada memoria.
Saida: resultados/revisao/rev_R4_tremor_dt.txt
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


def gerar_dt(q, c1, c2, f0, e0, dtM, extra=None):
    import lal
    from pyseobnr.generate_waveform import generate_modes_opt
    ajustes = dict(M=50.0, dt=dtM * 50.0 * lal.MTSUN_SI)
    if extra:
        ajustes.update(extra)
    t, modos = generate_modes_opt(q, c1, c2, np.pi * f0, eccentricity=e0, rel_anomaly=0.0, approximant="SEOBNRv5EHM",
                                  settings=ajustes)
    h = {}
    for chave, v in modos.items():
        l, m = (int(x) for x in chave.split(","))
        h[(l, m)] = np.asarray(v)
        h[(l, -m)] = (-1) ** l * np.conj(h[(l, m)])
    return np.asarray(t), h


if __name__ == "__main__":
    DADOS = json.load(open(os.path.join(C.RAIZ, "resultados", "exp12_pares.json")))
    p = [x for x in DADOS["pares"] if x["e0"] == 0.2 and x["qB"] == 2.0][0]
    log("Tremor das memorias de B (e0 = 0.2, q_B = 2) sob M_B (1 + k 1e-12), k = 0..4, para tres passos de tempo")
    log("(depois: dt = 0.1 M com tolerancias do integrador mais finas, rtol/atol = 1e-13/1e-14 em vez de 1e-11/1e-12)")
    casos = [(0.1, None), (0.05, None), (0.025, None), (0.1, dict(rtol=1e-13, atol=1e-14))]
    for dtM, extra in casos:
        vals = []
        for k in range(5):
            M = p["M"] * (1 + k * 1e-12)
            f0 = M * C.Dt.MSUN_S * C.F_FIS
            t, h = gerar_dt(p["qB"], p["c1"], p["c2B"], f0, p["e0"], dtM, extra)
            dt_real = t[1] - t[0]
            eta = p["qB"] / (1 + p["qB"]) ** 2
            mem, _ = C.E.memorias_janela(t, h, C.LISTA, C.E.calc(), eta, (np.pi * f0) ** (2 / 3))
            del t, h
            v = C.B.valores_fisicos(mem, p["iota"], M, p["D"])
            vals.append([v[kk] for kk in ("deslocamento", "spin", "cm", "giroscopica")])
        vals = np.array(vals)
        disp = (vals.max(0) - vals.min(0)) / np.abs(vals.mean(0))
        log("  dt = %.3f M (grade real %.4f M)%s: dispersao relativa desl %.1e spin %.1e cm %.1e giro %.1e"
            % (dtM, dt_real, " rtol 1e-13" if extra else "", *disp))
        if dtM == 0.1 and extra is None:
            ref = vals[0]
        else:
            d = (vals[0] - ref) / np.abs(ref)
            log("       mudanca em relacao a dt = 0.1 M (k = 0): desl %+.1e spin %+.1e cm %+.1e giro %+.1e" % tuple(d))
    with open(os.path.join(C.RES, "rev_R4_tremor_dt.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
