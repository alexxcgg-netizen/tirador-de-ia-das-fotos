"""Verificacao adversarial D6: nos sistemas em que o localizador simples do ver_D6_eixoQ achou soma 1.5 (S01, S03,
S05 spin), conferir com o localizador do exp34 (com candidatos da icosfera) e a soma pela icosfera; e conferir os
8 zeros da memoria de spin no caso X2 (q = 1, spins antiparalelos no plano 0.8)."""
import os
import sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import exp33_comum as C
import exp34_zeros as Z

rng = np.random.default_rng(99)
sis = {}
for k in range(10):
    q = rng.uniform(1.0, 4.0)
    vs = []
    for _ in range(2):
        u = rng.normal(size=3)
        u /= np.linalg.norm(u)
        vs.append(tuple(rng.uniform(0.3, 0.8) * u))
    sis["S%02d" % k] = (q, vs[0], vs[1])
sis["X2"] = (1.0, (0.0, 0.8, 0.0), (0.0, -0.8, 0.0))
for nome in ("S01", "S03", "S05", "X2"):
    q, a, b = sis[nome]
    t, h, dyn = C.gerar7(q, a, b, f_ref=C.F0_PADRAO)
    ti = C.instante_orbital(t, dyn["orbphase"], C.F0_PADRAO)
    mem, _ = C.memorias7(q, t, h, dyn, ti)
    del t, h, dyn
    for tipo in ("deslocamento", "spin"):
        tri, lista = Z.indices_triangulos(mem[tipo], nivel=6)
        zz = Z.zeros(mem[tipo], extras=[c for c, _ in lista])
        d = min([np.degrees(z["dmin"]) for z in zz]) if zz else np.nan
        print("%s %-12s: icosfera soma %.2f (%d triangulos) ; exp34: %d zeros, indices %s, soma %.2f ; menor distancia"
              " entre zeros %.3f graus" % (nome, tipo, tri, len(lista), len(zz), sorted(round(z["indice"], 2) for z in zz),
                                           sum(z["indice"] for z in zz), d), flush=True)
