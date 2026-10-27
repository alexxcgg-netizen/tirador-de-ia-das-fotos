"""gerar_nordeste_json.py: o JSON da aba Nordeste bate com os CSVs da nota de pesquisa."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gerar_nordeste_json as g  # noqa: E402


def test_gera_json_coerente(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "SAIDA", tmp_path / "nordeste.json")
    out = g.main()
    assert json.loads((tmp_path / "nordeste.json").read_text(encoding="utf-8")) == out
    s = out["resumo"]
    assert round(s["lula26"]) == 64 and abs(s["margem22_pp"] - 39.8) < 0.2 and abs(s["margem26_pp"] - 32.9) < 0.2
    assert len(out["uf"]) == 9 and {u["grupo"] for u in out["uf"]} == set(g.UF_NE)
    # soma das UFs = total do NE (Δmargem, mil votos)
    assert abs(sum(u["dmargem_mil"] for u in out["uf"]) - s["dmargem_mil"]) < 5
    assert [x["uf"] for x in s["maiores_perdas"]] == ["BA", "CE", "MA"]
    tot = [c["total_mil"] for c in out["cenarios"]]
    assert min(tot) == -1130 and max(tot) == 807
    for c in out["cenarios"]:
        assert abs(c["transferencia_mil"] + c["comparecimento_mil"] + c["brancos_nulos_mil"] - c["total_mil"]) <= 2
    hist = {h["ano"]: h["dcomp_pp"] for h in out["comparecimento_1t2t"]}
    assert hist == {2014: -1.6, 2018: -1.1, 2022: 0.2}
    porte = [p["swing"] for p in out["porte"]]
    assert porte[0] < porte[-1]   # municípios pequenos caíram mais que os grandes
