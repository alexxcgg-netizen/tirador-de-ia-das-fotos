"""Experimento 39 (linha L19, tarefa 3): mensurabilidade do atraso da memoria (memoria + onda oscilatoria).

Observavel combinado: a onda oscilatoria (SNR alta) preve a memoria nula s_n(t) (balanco de fluxo); a memoria
observada difere por um transiente de area -DeltaK (memoria de CM), isto e, por um atraso de centroide
delta = -CM_obs / Delta h_obs (exp38; ~M_f/2 vezes ~1,1 pela parte nula da CM, em l = 2).
Precisao de Fisher para um deslocamento temporal da memoria com a fase/tempo fixados pela onda:
    sigma_delta = 1 / || ds_n/dt ||   (a amplitude da memoria nao se correlaciona com delta: (s|ds/dt) = 0).
Tambem: SNR de s_n(t) - s_n(t - delta) (direto), SNR da diferenca completa s_RN - s_n (parte ordinaria +
toque quase normal dos m = 0) e a fracao dela que um atraso puro explica.
Sistemas: o A do exp07 (q = 1,2, chi = (0,3, -0,2), D = 400 Mpc, iota = 50 graus) com M = 30, 65, 120, 200;
deteccao com h_+ (detector otimo para +), f_min = 10 Hz (5 Hz para ET e CE como variante).
Saida: resultados/exp39_cm_mensuravel.txt e .json
"""
import json
import os
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
RES = os.path.join(AQUI, "..", "resultados")
import observaveis as O                                  # noqa: E402
from deteccao import MSUN_S                              # noqa: E402

Q, C1, C2, DMPC, IOTA, PHI = 1.2, 0.3, -0.2, 400.0, np.radians(50.0), 0.0
MASSAS = (30.0, 65.0, 120.0, 200.0)
DETS = (("aLIGO", 10.0), ("A+", 10.0), ("ET", 10.0), ("CE", 10.0), ("ET", 5.0), ("CE", 5.0))


def derivada_serie(ts, s):
    """ds/dt na parte uniforme da serie (o primeiro ponto, t_i, fica fora da rede)."""
    ds = np.gradient(s[1:], ts[2] - ts[1])
    return ts[1:], ds


def caso(M):
    t0 = time.time()
    t, h, ti = O.gerar_janela(Q, C1, C2, M, 10.0)
    mem, aux = O.memorias_observaveis(Q, C1, C2, M, 10.0, t=t, h=h, t_i=ti)
    v = O.no_observador_completo(mem, IOTA, PHI)
    from harmonicos import Dfrak
    # atraso efetivo no observador: total (nula + ordinaria da CM) e so a parte ordinaria
    d_tot = -v["cm"] / v["deslocamento"]
    mem_ord = {tipo: dict(vals) for tipo, vals in mem.items()}
    mem_ord["cm"] = {k: -1.5 * aux["M_f"] * mem["deslocamento"][k] / Dfrak(k[0]) for k in mem["deslocamento"]}
    d_ord = -O.no_observador_completo(mem_ord, IOTA, PHI)["cm"] / v["deslocamento"]
    ts, sn = O.serie_memoria(t, h, ti, IOTA, PHI, M, DMPC, tipo="nula")
    tr, sr = O.serie_memoria(t, h, ti, IOTA, PHI, M, DMPC, tipo="rn")
    del t, h
    Ms = M * MSUN_S
    out = dict(M=M, M_f=aux["M_f"], delta_tot_M=d_tot, delta_ord_M=d_ord, delta_tot_s=d_tot * Ms,
               delta_ord_s=d_ord * Ms, det={})
    tsd, dsn = derivada_serie(ts, sn.real)
    # difercas no mesmo rotulo de tempo
    s_sh = np.interp(ts - d_tot * Ms, ts, sn.real, left=0.0)
    dif_atraso = sn.real - s_sh
    rn_menos_n = sr.real - sn.real                      # mesma grade (ambas desde t_i)
    # parte de rn - n explicada por um atraso puro: projecao de minimos quadrados no tempo, so para referencia
    for nome, fmin in DETS:
        rho = O.snr2(ts, sn, nome, fmin)
        rho_d = O.snr2(tsd, dsn + 0j, nome, fmin, fim="nada")
        rho_atraso = O.snr2(ts, dif_atraso + 0j, nome, fmin, fim="nada")
        rho_rn_n = O.snr2(ts, rn_menos_n + 0j, nome, fmin, fim="nada")
        rho_rn = O.snr2(tr, sr, nome, fmin)
        sig = 1.0 / rho_d
        out["det"]["%s_%g" % (nome, fmin)] = dict(rho_nula=rho, rho_rn=rho_rn, sigma_delta_s=sig,
                                                  razao_tot=d_tot * Ms / sig, razao_ord=d_ord * Ms / sig,
                                                  rho_atraso_direto=rho_atraso, rho_rn_menos_nula=rho_rn_n,
                                                  f_rms=rho_d / (2 * np.pi * rho))
    out["tempo_s"] = time.time() - t0
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    t0 = time.time()
    with mp.get_context("spawn").Pool(2) as pool:
        res = pool.map(caso, MASSAS)
    linhas = []

    def log(s=""):
        print(s, flush=True)
        linhas.append(s)
    log("exp39: atraso da memoria (CM) como observavel combinado memoria + onda; q = 1.2, chi = (+0.3, -0.2), "
        "D = 400 Mpc, iota = 50 graus, h_+, janela desde 10 Hz")
    log("sigma_delta = 1/||d s_nula/dt|| ; delta_tot = -CM/desl no observador (nula + ordinaria da CM) ; "
        "f_rms = ||ds/dt||/(2 pi rho)")
    for o in res:
        log()
        log("M = %.0f (M_f = %.4f M): delta_tot = %.4f M = %.1f us ; delta_ord = %.4f M = %.1f us"
            % (o["M"], o["M_f"], o["delta_tot_M"], 1e6 * o["delta_tot_s"], o["delta_ord_M"], 1e6 * o["delta_ord_s"]))
        for k, d in o["det"].items():
            n3 = 9.0 / d["razao_tot"] ** 2
            log("  %-9s rho_nula %7.3f  rho_rn %7.3f  f_rms %6.1f Hz  sigma_delta %8.1f us  delta/sigma %.3f (ord %.3f)"
                "  [direto %.3f]  rho(rn - nula) %.3f  eventos iguais p/ 3 sigma %.0f ; sigma(M_f)/M_f = %.2f"
                % (k, d["rho_nula"], d["rho_rn"], d["f_rms"], 1e6 * d["sigma_delta_s"], d["razao_tot"], d["razao_ord"],
                   d["rho_atraso_direto"], d["rho_rn_menos_nula"], n3, 1.0 / d["razao_tot"]))
    log()
    log("Escala: delta/sigma ~ rho_nula * 2 pi f_rms * delta ; rho ~ 1/D ; para D = 100 Mpc multiplicar por 4.")
    log("(%.0f s)" % (time.time() - t0))
    with open(os.path.join(RES, "exp39_cm_mensuravel.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(RES, "exp39_cm_mensuravel.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
