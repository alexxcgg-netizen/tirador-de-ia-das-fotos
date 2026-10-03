import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelo as M  # noqa: E402
import rodar as R  # noqa: E402


@pytest.fixture(scope="module")
def base():
    return M.construir_base()


@pytest.fixture(scope="module")
def lote(base):
    return {c: M.simular_lote(base, c, 20000, np.random.default_rng(7)) for c in ("neutro", "historico")}


def test_shares_somam_um(lote, base):
    for r in lote.values():
        assert np.allclose(r["nat1"].sum(1), 1, atol=1e-4)
        uf = np.stack([r["uf_L"], r["uf_F"]], 2)
        assert (uf > 0).all() and (uf < 1).all()
        assert ((r["uf_q"] > 0) & (r["uf_q"] < 1)).all()


def test_shares_uf_somam_um(base):
    rng = np.random.default_rng(3)
    r = M.simular_lote(base, "neutro", 2000, rng)
    # 1 - Lula - Flávio = soma dos menores, sempre não negativa
    assert (1 - r["uf_L"] - r["uf_F"] >= -1e-5).all()


def test_media_uf_calibrada_reproduz_nacional(base):
    ufs = base.ufs
    w = (ufs.eleitores_2026 * (1 - ufs.abst_1t_2022 / 100) * (1 - ufs.bn_1t_2022_pct_comp / 100)).values
    T = 1 - base.m_uf.sum(1)
    p2 = np.sum(w * T * base.p2_uf) / np.sum(w * T)
    assert abs(p2 - base.p2_nat) < 1e-6
    w2 = (ufs.eleitores_2026 * (1 - ufs.abst_2t_2022 / 100) * (1 - ufs.bn_2t_2022_pct_comp / 100)).values
    assert abs(np.sum(w2 * base.q_uf) / np.sum(w2) - base.q_nat) < 1e-6


def test_probabilidades_em_0_1():
    res, _, _ = R.executar(20000, 11, 10000)
    for cen in res.values():
        for k, v in cen["prob"].items():
            assert 0 <= v["p"] <= 1, k
        assert abs(cen["prob"]["lula_vence"]["p"] + cen["prob"]["flavio_vence"]["p"]
                   + cen["prob"]["outro_vence"]["p"] - 1) < 1e-9
        for u in cen["ufs"]:
            assert 0 <= u["p_lula_2t"] <= 1 and 0 <= u["p_lula_1o_1t"] <= 1


def test_reprodutivel_com_semente():
    a, _, _ = R.executar(5000, 123, 2500)
    b, _, _ = R.executar(5000, 123, 2500)
    c, _, _ = R.executar(5000, 124, 2500)
    assert a["neutro"]["prob"] == b["neutro"]["prob"]
    assert a["historico"]["ufs"] == b["historico"]["ufs"]
    assert a["neutro"]["prob"] != c["neutro"]["prob"]


def test_agregado_das_ufs_segue_sorteio_nacional(lote, base):
    r = lote["neutro"]
    impl = M.expit(M.logit(base.p2_nat) + r["e_p2"])        # sorteio nacional implícito
    agg = r["nat_p2_agregado"]                              # soma das UFs ponderada
    assert np.corrcoef(impl, agg)[0, 1] > 0.98
    # diferença média pequena (contração da 3ª via desloca levemente p2 a favor de quem recebe mais transferências)
    assert abs(np.mean(agg - impl)) < 0.01
    assert np.std(agg - impl) < 0.01


def test_sanidade_geografia(lote):
    q = lote["neutro"]["uf_q"].mean(0)
    import pandas as pd
    ufs = M.carregar_ufs()
    s = pd.Series(q, index=ufs.uf)
    for uf in ("BA", "PE", "CE", "PI", "MA"):
        assert s[uf] > 0.6
    for uf in ("SC", "PR", "MT", "RO", "RR", "AC"):
        assert s[uf] < 0.42


def test_cenario_historico_desloca_para_flavio(lote):
    n = lote["neutro"]; h = lote["historico"]
    assert h["nat1"][:, 1].mean() > n["nat1"][:, 1].mean() + 0.02
    assert h["Q"].mean() < n["Q"].mean()
