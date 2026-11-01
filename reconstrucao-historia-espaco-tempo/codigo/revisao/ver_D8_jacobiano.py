"""Verificacao D8: o menor valor singular 5.4e-5 -> 1.55e-5 (exp40_jacobiano) e evidencia especifica das
direcoes excentricas, ou acontece com quaisquer duas colunas acrescentadas?

Entrelacamento [E]: para A = [B C] (7 x 7) com B (7 x 5), sigma_7(A) <= sigma_5(B). Base de comparacao:
trocar as colunas (X, Y) por vetores aleatorios com as mesmas normas (e outras escalas) e ver a distribuicao
de sigma_min. Tambem: sensibilidade a escala das colunas (X, Y) e ao erro de passo das colunas circulares
(M tem erro h x h/2 de 16%). So le resultados/exp40_jacobiano.json (nao roda o modelo).
"""
import json
import os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "..", "resultados")
J7 = np.array(json.load(open(os.path.join(RES, "exp40_jacobiano.json")))["J7"])
B, C = J7[:, :5], J7[:, 5:]
s5 = np.linalg.svd(B, compute_uv=False)
s7 = np.linalg.svd(J7, compute_uv=False)
print("sigma(B 7x5) =", " ".join("%.3e" % x for x in s5))
print("sigma(J7)    =", " ".join("%.3e" % x for x in s7))
print("normas das colunas X, Y (escaladas):", np.linalg.norm(C, axis=0))
rng = np.random.default_rng(1)
for nome, gen in (("gaussianas, mesmas normas", lambda: rng.standard_normal((7, 2))),):
    v = []
    for _ in range(20000):
        R = gen()
        R = R / np.linalg.norm(R, axis=0) * np.linalg.norm(C, axis=0)
        v.append(np.linalg.svd(np.concatenate([B, R], axis=1), compute_uv=False)[-1])
    v = np.array(v)
    print("%s: sigma_min mediana %.3e, quantis 10%% %.3e 90%% %.3e ; fracao <= 1.55e-5: %.3f"
          % (nome, np.median(v), np.quantile(v, 0.1), np.quantile(v, 0.9), np.mean(v <= s7[-1])))
# so uma coluna aleatoria acrescentada (7 x 6)
v6 = []
for _ in range(20000):
    r = rng.standard_normal((7, 1)); r *= np.linalg.norm(C[:, 0]) / np.linalg.norm(r)
    v6.append(np.linalg.svd(np.concatenate([B, r], axis=1), compute_uv=False)[-1])
print("uma coluna aleatoria (7x6): sigma_min mediana %.3e" % np.median(v6))
for k in (0, 1):
    print("so a coluna %s real (7x6): sigma_min %.3e" % ("XY"[k], np.linalg.svd(np.concatenate([B, C[:, k:k + 1]], axis=1), compute_uv=False)[-1]))
# escala das colunas excentricas
for f in (0.1, 0.3, 1.0, 3.0, 10.0):
    print("escala (X,Y) x %.1f: sigma_min %.3e" % (f, np.linalg.svd(np.concatenate([B, f * C], axis=1), compute_uv=False)[-1]))
# erro de passo: perturbar as colunas circulares com ruido relativo do tamanho do erro h x h/2 medido
err = np.array([2.9e-4, 1.7e-2, 1.6e-1, 5.6e-2, 1.1e-2])
for nome, M in (("B", B), ("J7", J7)):
    v = []
    for _ in range(5000):
        P = M.copy()
        for k in range(5):
            d = rng.standard_normal(7); d *= err[k] * np.linalg.norm(B[:, k]) / np.linalg.norm(d)
            P[:, k] = P[:, k] + d
        v.append(np.linalg.svd(P, compute_uv=False)[-1])
    v = np.array(v)
    print("%s com erro de passo nas colunas circulares: sigma_min mediana %.2e, 10%%-90%% %.2e-%.2e" %
          (nome, np.median(v), np.quantile(v, .1), np.quantile(v, .9)))
# componente do vetor singular fraco nas direcoes excentricas comparada com o caso aleatorio
U, s, Vt = np.linalg.svd(J7)
print("vetor fraco real: peso em (X,Y) = %.3f" % np.linalg.norm(Vt[-1, 5:]))
w = []
for _ in range(5000):
    R = rng.standard_normal((7, 2)); R = R / np.linalg.norm(R, axis=0) * np.linalg.norm(C, axis=0)
    w.append(np.linalg.norm(np.linalg.svd(np.concatenate([B, R], axis=1))[2][-1, 5:]))
print("colunas aleatorias: peso mediano em (X,Y) do vetor fraco = %.3f (10%%-90%% %.3f-%.3f)"
      % (np.median(w), np.quantile(w, .1), np.quantile(w, .9)))
