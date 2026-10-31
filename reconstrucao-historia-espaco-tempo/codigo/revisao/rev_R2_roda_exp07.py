"""Revisao R2: roda o exp07 sem alterar o script, trocando o Pool(4) por um mapa serial.

Motivo: a maquina e compartilhada (no maximo 2 processos Python). O exp07 cria um Pool(4) de
processos 'spawn'; aqui o Pool e substituido por um objeto que executa o map no proprio processo.
O resultado numerico e o mesmo (o otimizador e deterministico); so o tempo muda.
Uso: cd codigo && python3 revisao/rev_R2_roda_exp07.py
"""
import multiprocessing.context as mpc
import os
import runpy
import time


class PoolSerial:
    """Imita a interface usada pelo exp07: with ... as pool: pool.map(f, lista)."""

    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def map(self, f, lista):
        out = []
        for i, x in enumerate(lista):
            t0 = time.time()
            out.append(f(x))
            print("  [R2] caso %d/%d resolvido em %.0f s" % (i + 1, len(lista), time.time() - t0), flush=True)
        return out


mpc.BaseContext.Pool = lambda self, *a, **k: PoolSerial()
AQUI = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(AQUI, "..", "exp07_binarias_observador.py"), run_name="__main__")
