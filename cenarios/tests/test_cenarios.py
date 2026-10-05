import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cenarios as C  # noqa: E402
import rodar as R  # noqa: E402

N = 20_000


@pytest.fixture(scope="module")
def par():
    return C.rodar_par(N, 7)


def test_triangular_limites_e_media():
    u = np.random.default_rng(0).random(200_000)
    v = C.tri_ppf(u, 1.0, 2.0, 6.0)
    assert v.min() >= 1.0 and v.max() <= 6.0
    assert abs(v.mean() - 3.0) < 0.02


def test_ir_lei_15270():
    assert C.ir_mensal(3777.0, C.inss(3777.0)) == pytest.approx(0.0)
    # redução parcial: R$ 978,62 − 0,133145 × renda
    sem = C.ir_mensal(6500.0, C.inss(6500.0), reducao=False)
    com = C.ir_mensal(6500.0, C.inss(6500.0), reducao=True)
    assert sem - com == pytest.approx(978.62 - 0.133145 * 6500, abs=0.01)
    assert C.ir_mensal(9000.0, C.inss(9000.0), True) == C.ir_mensal(9000.0, C.inss(9000.0), False)


def test_calibracao_divida_2027():
    s = (C.BASE["selic_fim_2026"] + C.CONS["selic_fim"][0]) / 2 / 100
    pi, g = C.CONS["ipca"][0] / 100, C.CONS["pib"][0] / 100
    i = C.PARCELA_SELIC * s + (1 - C.PARCELA_SELIC) * (pi + C.K_JURO_REAL)
    d = C.BASE["divida"] * (1 + i) / ((1 + g) * (1 + pi)) - C.CONS["primario_sem_ajuste"][0]
    assert d == pytest.approx(86.4, abs=1e-6)


def test_mesmas_regras_para_os_dois():
    """Trocar todos os grupos de parâmetros reproduz exatamente o outro cenário:
    não há código específico de candidato fora de CANDIDATOS."""
    todos = {g: "F" for g in C.GRUPOS}
    a = C.rodar_cenario(C.montar_spec("L", todos), 5000, 3, "F")
    b = C.rodar_cenario(C.CANDIDATOS["F"], 5000, 3, "F")
    for k in C.ARQUETIPOS:
        np.testing.assert_allclose(a["pp"][k], b["pp"][k])


def test_mesma_especificacao_diferenca_nula():
    a = C.rodar_cenario(C.CANDIDATOS["L"], 5000, 3, "L")
    b = C.rodar_cenario(C.CANDIDATOS["L"], 5000, 3, "L")
    for k in C.ARQUETIPOS:
        assert np.all(a["pp"][k] == b["pp"][k])


def test_numeros_aleatorios_comuns(par):
    """Choques exógenos idênticos: o prêmio de alimentos é o mesmo nos dois cenários,
    então a diferença de inflação de alimentos vem só dos canais do vencedor."""
    dl = par["L"]["macro"]["alimentos"] - par["L"]["macro"]["ipca"]
    df = par["F"]["macro"]["alimentos"] - par["F"]["macro"]["ipca"]
    assert np.corrcoef(dl[:, 0], df[:, 0])[0, 1] > 0.95


def test_ancora_no_consenso(par):
    media = 0.5 * (par["L"]["macro"]["ipca"][:, 0].mean() + par["F"]["macro"]["ipca"][:, 0].mean())
    assert abs(media - C.CONS["ipca"][0]) < 0.6
    fx = 0.5 * (np.median(par["L"]["macro"]["cambio"][:, 0]) + np.median(par["F"]["macro"]["cambio"][:, 0]))
    assert abs(fx - C.CONS["cambio"][0]) < 0.3


def test_direcao_do_choque_cambial(par):
    assert np.median(par["L"]["macro"]["cambio"][:, 0]) > C.BASE["cambio"]
    assert np.median(par["F"]["macro"]["cambio"][:, 0]) < C.BASE["cambio"]


def test_regra_do_minimo():
    com = C.simular(C.CANDIDATOS["F"], 3000, 1, "F", fixos={"regra_sm": 1})
    sem = C.simular(C.CANDIDATOS["F"], 3000, 1, "F", fixos={"regra_sm": 0})
    s1, s0 = com["pp"]["aposentado"], sem["pp"]["aposentado"]
    np.testing.assert_allclose(s1[:, 0], s0[:, 0])
    assert np.all(s1[:, -1] >= s0[:, -1] - 1e-9)


def test_horas_cesta_base():
    assert C.BASE["horas_cesta"] == pytest.approx(105.85, abs=0.01)


def test_reponderacao_reproduz_resultado(par):
    cel = R.celulas(par)
    for cand in ("L", "F"):
        tot = sum(c["n"] for c in cel[cand].values())
        assert tot == N
        probs = {"persiste": C.CANDIDATOS[cand]["credibilidade"]["p_persiste"],
                 "x6": C.CANDIDATOS[cand]["trabalho"]["p_6x1"],
                 "regra_sm": C.CANDIDATOS[cand]["minimo"]["p_regra"],
                 "iva": C.CANDIDATOS[cand]["iva"]["p"],
                 "pec12": C.CANDIDATOS[cand]["trabalho"]["p_pec12"]}
        for m in ("sm", "mediano", "bf"):
            exato = par[cand]["pp"][m][:, -1].mean()
            mix = R.mistura_media(cel[cand], C.EVENTOS[cand], probs, m)
            assert mix == pytest.approx(exato, abs=0.15)
        for c in cel[cand].values():
            assert sum(c["m"]["sm"][2]) == c["n"]
