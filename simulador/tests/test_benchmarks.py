"""Testes de benchmarks.py (limiares de sinal, cobertura das UFs, bellwethers)."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import benchmarks as B  # noqa: E402


@pytest.fixture(scope="module")
def out():
    return B.gerar(escrever=False)


def test_limiar_dp_igual_e_ponto_medio():
    assert B.limiar(44.0, 3.0, 46.0, 3.0) == pytest.approx(45.0)
    # razão de verossimilhança no limiar 3x é exatamente 3
    x = B.limiar(44.0, 3.0, 46.0, 3.0, math.log(3))
    assert x < 45.0
    assert B.log_razao(x, 44.0, 3.0, 46.0, 3.0) == pytest.approx(math.log(3))


def test_limiar_dp_diferente_fica_entre_medias():
    x = B.limiar(10.0, 2.0, 14.0, 3.0)
    assert 10.0 <= x <= 14.0
    assert B.log_razao(x, 10.0, 2.0, 14.0, 3.0) == pytest.approx(0.0, abs=1e-9)


def test_sinais_simetricos():
    s = B.sinais(44.0, 3.0, 46.0, 3.0)
    assert s["indiferenca"] == pytest.approx(45.0)
    assert s["calibrado_3x"] < s["indiferenca"] < s["neutro_3x"]
    assert s["indiferenca"] - s["calibrado_3x"] == pytest.approx(s["neutro_3x"] - s["indiferenca"])
    assert s["separacao"] == pytest.approx(2 / 3)


def test_sd_de_quantis_normal_padrao():
    assert B.sd_de_quantis(-B.Z90, B.Z90) == pytest.approx(1.0)


def test_cobertura_e_coerencia(out):
    ufs = {r["uf"] for r in out["ufs"]}
    assert set(B.UFS_27) <= ufs and "ZZ" in ufs
    for r in [out["nacional"]] + out["ufs"]:
        for v in B.VISOES:
            for c in ("lula", "flavio"):
                b = r[f"{c}_{v}"]
                assert b["p10"] <= b["p50"] <= b["p90"]
                assert 0 < b["media"] < 100
        lo, hi = sorted([r["lula_calibrado"]["media"], r["lula_neutro"]["media"]])
        assert lo <= r["sinal_lula"]["indiferenca"] <= hi
        assert "lula_2022_1t" in r


def test_nacional_2022_e_previsao(out):
    n = out["nacional"]
    assert n["lula_2022_1t"] == pytest.approx(48.43, abs=0.01)
    assert n["bolsonaro_2022_1t"] == pytest.approx(43.20, abs=0.01)
    # o calibrado é menos favorável a Lula que o neutro
    assert n["lula_calibrado"]["media"] < n["lula_neutro"]["media"]
    assert n["sinal_lula"]["calibrado_3x"] < n["sinal_lula"]["indiferenca"] < n["sinal_lula"]["neutro_3x"]
    assert n["sinal_margem"]["calibrado_3x"] < n["sinal_margem"]["neutro_3x"]


def test_pct_eleitorado_soma_100(out):
    assert sum(r["pct_eleitorado"] for r in out["ufs"]) == pytest.approx(100.0, abs=0.05)


def test_bellwether_ufs(out):
    bw = out["bellwether_ufs"]
    assert len(bw) == 27
    assert [b["desvio_medio_abs_2p_pp"] for b in bw] == sorted(b["desvio_medio_abs_2p_pp"] for b in bw)
    assert bw[0]["uf"] == "MG"  # acertou o vencedor de todas as eleições 2006–2022
    assert bw[0]["acertou_vencedor_2t"] == "5/5"


def test_bellwether_municipios(out):
    bm = out["bellwether_municipios"]
    assert 0 < len(bm) <= 15
    assert all(m["validos_2022"] >= 100_000 for m in bm)


def test_csv_achatado(out):
    f = B.achatar(out["ufs"][0])
    for k in ("lula_calibrado_p10", "flavio_neutro_p90", "sinal_lula_indiferenca", "lula_2022_1t"):
        assert k in f


def test_trajetoria_apuracao(out):
    t = out["trajetoria_apuracao"]
    pts = t["pontos"]
    assert pts[-1]["deriva_2022"] == pytest.approx(0.0)
    assert [p["pct_apurado"] for p in pts] == sorted(p["pct_apurado"] for p in pts)
    # em 2022 Bolsonaro liderou até ~2/3 apurados e Lula virou por volta de 70%
    assert all(p["margem_2022"] < 0 for p in pts if p["pct_apurado"] <= 66.66)
    assert all(p["margem_2022"] > 0 for p in pts if p["pct_apurado"] >= 70)
    for v in B.VISOES:
        assert 0.5 < t["k_escala"][v] < 1.5
        assert pts[-1][f"margem_esperada_{v}"] == pytest.approx(out["nacional"][f"margem_{v}"]["media"])
        # parcial cedo é mais pró-Flávio que o final esperado
        assert pts[3][f"margem_esperada_{v}"] < pts[-1][f"margem_esperada_{v}"]
