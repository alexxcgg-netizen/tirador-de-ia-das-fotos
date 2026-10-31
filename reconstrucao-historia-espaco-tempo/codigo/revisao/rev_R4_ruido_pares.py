"""Revisor R4, tarefa 1: reavaliacao dos pares do exp12 (SEOBNRv5EHM, nivel A) num processo novo.

Uso: python revisao/rev_R4_ruido_pares.py <rotulo> <ordem>     (ordem = "direta" ou "inversa")
     python revisao/rev_R4_ruido_pares.py resumo                (compara as execucoes gravadas)

Cada execucao (um processo novo):
  a) avalia A (e0 = 0) e os 6 B de resultados/exp12_pares.json, sem cache, na ordem pedida;
  b) compara com o alvo gravado no json (calculado no processo principal do exp12) e com o A recalculado;
  c) reavalia A e o par (e0 = 0.2, q_B = 2) uma segunda vez no fim, no mesmo processo (determinismo interno);
  d) "tremor": o par (0.2, 2) com M_B * (1 + k * 1e-12) e (1 + k * 1e-9), k = 1, 2, 3 (abaixo do arredondamento
     do cache do exp12, que guarda chaves com 9 casas decimais).
Saida: resultados/revisao/rev_R4_ruido_<rotulo>.json ; resumo em resultados/revisao/rev_R4_ruido_pares.txt
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rev_R4_comum as C                                # noqa: E402

DADOS = json.load(open(os.path.join(C.RAIZ, "resultados", "exp12_pares.json")))


def par_B(p):
    return dict(M=p["M"], q=p["qB"], c1=p["c1"], c2=p["c2B"], D=p["D"], iota=p["iota"], e=p["e0"], l0=0.0)


def rodar(rotulo, ordem):
    t0 = time.time()
    A = dict(DADOS["A"])
    alvo_json = DADOS["alvo"]
    nomes = ["A"] + ["B e0=%.1f qB=%.1f" % (p["e0"], p["qB"]) for p in DADOS["pares"]]
    pares = [A] + [par_B(p) for p in DADOS["pares"]]
    idx = list(range(len(pares)))
    if ordem == "inversa":
        idx = idx[::-1]
    vals = {}
    for i in idx:
        v, _ = C.fisicos(pares[i], usar_cache=False)
        vals[nomes[i]] = v
    # segunda avaliacao no mesmo processo
    v2A, _ = C.fisicos(A, usar_cache=False)
    j = [k for k, p in enumerate(DADOS["pares"]) if p["e0"] == 0.2 and p["qB"] == 2.0][0]
    pB = par_B(DADOS["pares"][j])
    v2B, _ = C.fisicos(pB, usar_cache=False)
    # tremor em M
    tremor = {}
    for eps in (1e-12, 1e-9):
        for k in (1, 2, 3):
            pp = dict(pB, M=pB["M"] * (1 + k * eps))
            v, _ = C.fisicos(pp, usar_cache=False)
            tremor["%g*%d" % (eps, k)] = v
    out = dict(rotulo=rotulo, ordem=ordem, vals=vals, A_de_novo=v2A, B02q2_de_novo=v2B, tremor=tremor,
               alvo_json=alvo_json, avisos=C.COLETOR.msgs[:20], n_avisos=len(C.COLETOR.msgs),
               segundos=time.time() - t0, omp=os.environ.get("OMP_NUM_THREADS"))
    with open(os.path.join(C.RES, "rev_R4_ruido_%s.json" % rotulo), "w") as f:
        json.dump(out, f, indent=1)
    print("ok %s %.0f s" % (rotulo, time.time() - t0))


def resumo():
    import glob
    arqs = sorted(glob.glob(os.path.join(C.RES, "rev_R4_ruido_exec*.json")))
    runs = [json.load(open(a)) for a in arqs]
    linhas = []

    def log(s=""):
        print(s)
        linhas.append(s)

    tipos = ("deslocamento", "spin", "cm", "giroscopica")
    alvo = DADOS["alvo"]
    log("Tarefa 1: pares do exp12 reavaliados em %d processos novos (OMP_NUM_THREADS=%s)" % (len(runs), runs[0]["omp"]))
    log("execucoes: " + ", ".join("%s (ordem %s, %.0f s, avisos do pyseobnr: %d)" % (r["rotulo"], r["ordem"], r["segundos"], r["n_avisos"]) for r in runs))
    log()
    log("(a) diferenca relativa de cada B ao alvo GRAVADO no json (A do exp12), por execucao; max sobre as 4 memorias e detalhe:")
    for nome in runs[0]["vals"]:
        partes = []
        for r in runs:
            d = C.dif_rel(r["vals"][nome], alvo)
            partes.append("%s: max %.2e [%s]" % (r["rotulo"], C.maxabs(d), " ".join("%s %+.1e" % (k[:4], d[k]) for k in tipos)))
        log("  %-18s " % nome + " | ".join(partes))
    log()
    log("(b) diferenca relativa entre execucoes (mesmo ponto, processos diferentes), max sobre as 4 memorias:")
    for nome in runs[0]["vals"]:
        ds = []
        for i in range(len(runs)):
            for j in range(i + 1, len(runs)):
                ds.append(C.maxabs(C.dif_rel(runs[i]["vals"][nome], runs[j]["vals"][nome])))
        log("  %-18s " % nome + " ".join("%.1e" % x for x in ds))
    log()
    log("(c) segunda avaliacao no mesmo processo (A e B e0=0.2 qB=2): diferenca relativa max")
    for r in runs:
        dA = C.maxabs(C.dif_rel(r["A_de_novo"], r["vals"]["A"]))
        dB = C.maxabs(C.dif_rel(r["B02q2_de_novo"], r["vals"]["B e0=0.2 qB=2.0"]))
        log("  %s: A %.1e ; B %.1e" % (r["rotulo"], dA, dB))
    log()
    log("(d) tremor: B (e0=0.2, qB=2) com M_B (1 + k eps); diferenca relativa ao ponto exato (max sobre as 4 memorias e por memoria)")
    for r in runs[:1]:
        base = r["vals"]["B e0=0.2 qB=2.0"]
        for k, v in r["tremor"].items():
            d = C.dif_rel(v, base)
            log("  eps*k = %-8s max %.2e [%s]" % (k, C.maxabs(d), " ".join("%s %+.1e" % (t[:4], d[t]) for t in tipos)))
    log()
    log("(e) residuo gravado no json (processo filho do exp12, so spin/cm/giro) x reavaliacao aqui (4 memorias):")
    for p in DADOS["pares"]:
        nome = "B e0=%.1f qB=%.1f" % (p["e0"], p["qB"])
        d = [C.maxabs(C.dif_rel(r["vals"][nome], alvo)) for r in runs]
        log("  %-18s json %.2e ; aqui %s" % (nome, p["residuo"], " ".join("%.2e" % x for x in d)))
    if runs[0]["avisos"]:
        log()
        log("avisos registrados (primeiros): " + " || ".join(runs[0]["avisos"][:5]))
    with open(os.path.join(C.RES, "rev_R4_ruido_pares.txt"), "w") as f:
        f.write("\n".join(linhas) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "resumo":
        resumo()
    else:
        rodar(sys.argv[1], sys.argv[2])
