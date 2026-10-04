"""Projeção da apuração parcial por município (resultado_1t.py) e replay com 2022.

Fixtures novas em tests/fixtures/tse/2026/ (baixadas em 4/10/2026, antes da apuração, com zeros):
  * ac-e006257-ab.json             abrangência do AC: seções/eleitorado totalizados por município
  * ac01120-c0001-e006257-u.json   presidente em Acrelândia (AC), formato "u" por município
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resultado_1t as R  # noqa: E402

FX = Path(__file__).resolve().parent / "fixtures" / "tse"


def _js(p):
    return json.loads((FX / p).read_text(encoding="utf-8"))


def test_urls_e_abrangencia():
    assert R.url_ab("ele2026", "6257", "AC").endswith("/oficial/ele2026/6257/dados/ac/ac-e006257-ab.json")
    assert R.url_municipio("ele2026", "6257", "AC", 1120).endswith("/dados/ac/ac01120-c0001-e006257-u.json")
    ab = R.parse_ab(_js("2026/ac-e006257-ab.json"))
    assert len(ab) == 22 and (ab.est == 0).all() and (ab.te > 0).all()           # só municípios, sem a linha da UF
    assert 1120 in set(ab.cd)
    base = R.base_municipal()
    assert set(ab.cd) <= set(base[base.uf == "AC"].cd)                            # códigos TSE 2026 = 2022
    m = R.parse_tse(_js("2026/ac01120-c0001-e006257-u.json"), R.NUMEROS[2026])
    assert m["abr"] == "01120" and set(m["votos"]) == set(R.CANDS_ANO[2026]) and m["eleitorado"] > 0


def test_municipios_2022_bate_com_tse():
    b = pd.read_csv(R.MUN_2022)
    assert len(b) > 5500 and not b.duplicated(["uf", "cd_municipio_tse"]).any()
    assert b.pt_votos.sum() == 57259504 and b.bolsonaro_votos.sum() == 51072345 and b.validos.sum() == 118229719
    assert b.aptos.sum() == 156454011
    assert (b.comparecimento <= b.aptos).all() and (b.validos <= b.comparecimento).all()
    b18 = pd.read_csv(R.MUN_2018)
    assert b18.pt_votos.sum() == 31342051 and b18.bolsonaro_votos.sum() == 49277010
    z = pd.read_csv(R.REPLAY_ZONAS)
    assert z.lula.sum() == 57259504 and z.validos.sum() == 118229719


def _uf_sintetica(swing=0.2, n=10, apurados=4, parcial_f=None):
    """UF com n municípios; base com PT de 30% a 70%; 'apurados' primeiros totalmente apurados com swing uniforme."""
    rng = np.random.default_rng(0)
    pa = np.linspace(0.3, 0.7, n)
    pb = np.full(n, 0.8)                          # B com 80% dos não-PT
    apt = rng.integers(5000, 50000, n).astype(float)
    val = apt * 0.75
    m = pd.DataFrame({"cd": np.arange(n), "te": apt * 1.05, "b_aptos": apt, "b_validos": val, "b_pt": val * pa,
                      "b_opp": val * (1 - pa) * pb})
    sa = R._ex(R._lg(pa) + swing)
    sb = (1 - sa) * pb
    est = np.zeros(n)
    est[:apurados] = m.te[:apurados]
    if parcial_f is not None:
        est[apurados] = parcial_f * m.te[apurados]
    v = (est * 0.75)[:, None] * np.column_stack([sa, sb, 1 - sa - sb])
    m["est"] = est
    for k in range(3):
        m[f"v{k}"] = v[:, k]
    return m, sa, sb


def test_projecao_swing_uniforme_recupera_resultado():
    m, sa, sb = _uf_sintetica(swing=0.2)
    r = R.projetar_uf_municipios(m, 3, 0, 1, {"dA": 0.2, "dB": 0.0, "lr": 0.0})
    final_v = (m.te * 0.75).to_numpy()
    real = np.sum(final_v * sa) / final_v.sum()
    assert r["S"][0] == pytest.approx(real, abs=2e-3)
    assert r["V"] == pytest.approx(final_v.sum(), rel=1e-6)
    assert r["swing"]["dA_bruto"] == pytest.approx(0.2, abs=1e-6)
    # método antigo erraria: só municípios de base PT baixa foram apurados
    antigo = m[["v0", "v1", "v2"]].to_numpy().sum(0)
    assert abs(antigo[0] / antigo.sum() - real) > 0.05
    assert r["sd_fatia_a"] > 0


def test_incerteza_encolhe_com_a_apuracao():
    sds = [R.projetar_uf_municipios(_uf_sintetica(apurados=k)[0], 3)["sd_fatia_a"] for k in (2, 5, 8, 10)]
    assert sds[0] > sds[1] > sds[2] > sds[3] and sds[3] == pytest.approx(0, abs=1e-9)


def test_municipio_parcial_usa_fatia_apurada_e_novo_municipio():
    m, sa, sb = _uf_sintetica(apurados=3, parcial_f=0.5)
    r = R.projetar_uf_municipios(m, 3)
    assert 0 < r["S"][0] < 1 and r["S"].sum() == pytest.approx(1)
    # município sem referência (criado depois da eleição de referência): fatias apuradas da UF, sem NaN
    m2 = m.copy()
    m2.loc[9, ["b_aptos", "b_validos", "b_pt", "b_opp"]] = np.nan
    r2 = R.projetar_uf_municipios(m2, 3)
    assert np.all(np.isfinite(r2["S"])) and np.isfinite(r2["V"]) and np.isfinite(r2["sd_logito"])
    # UF sem nenhum voto apurado ainda: usa o prior nacional
    m3 = m.copy()
    m3[["est", "v0", "v1", "v2"]] = 0.0
    r3 = R.projetar_uf_municipios(m3, 3, prior={"dA": 0.2, "dB": 0.0, "lr": 0.0})
    final_v = (m.te * 0.75).to_numpy()
    assert r3["S"][0] == pytest.approx(np.sum(final_v * sa) / final_v.sum(), abs=5e-3)


@pytest.fixture(scope="module")
def replay():
    return {c: R.replay_2022(c, (0.10, 0.25, 0.50, 0.75), seed=1) for c in R.CENARIOS_REPLAY}


def test_replay_2022_novo_melhor_que_antigo(replay):
    """Ordem não aleatória (zonas por porte / pela fatia de Bolsonaro): a projeção por município erra menos."""
    for c in ("direita_primeiro", "pequenos_primeiro"):
        for r in replay[c]:
            assert abs(r["novo_erro_lula_pp"]) < abs(r["antigo_erro_lula_pp"]), (c, r)
            assert r["novo_mae_uf_lula_pp"] < r["antigo_mae_uf_lula_pp"], (c, r)
    for c in R.CENARIOS_REPLAY:
        for r in replay[c]:
            if c == "grandes_primeiro" and r["apurado_pct"] < 20:
                continue      # só capitais apuradas: o interior é extrapolação (ver README); intervalo largo
            assert r["novo_mae_uf_lula_pp"] < r["antigo_mae_uf_lula_pp"] + 0.3, (c, r)
    # cobertura do intervalo de 90% por UF razoável a partir de 25% apurado
    cob = [r["novo_cobertura_90_uf"] for c in R.CENARIOS_REPLAY for r in replay[c] if r["apurado_pct"] >= 24]
    assert np.mean(cob) > 0.75
    # 'Bolsonaro primeiro' (como em 2022): método antigo erra a margem em mais de 10 p.p. com 10% apurado
    r10 = replay["direita_primeiro"][0]
    assert abs(r10["antigo_erro_margem_pp"]) > 10 and abs(r10["novo_erro_margem_pp"]) < 5
    # erro cai com a apuração
    for c in R.CENARIOS_REPLAY:
        assert replay[c][-1]["novo_mae_uf_lula_pp"] < replay[c][0]["novo_mae_uf_lula_pp"]
    assert [r["apurado_pct"] for r in replay["aleatorio"]] == pytest.approx([10, 25, 50, 75], abs=0.5)


def _fake_tse(frac_apurada=0.5, lula=0.40, flavio=0.45):
    """Servidor falso: abrangência do AC (fixture) com metade dos municípios apurados (todos com a mesma
    fatia) e arquivos por município derivados da fixture de Acrelândia."""
    ab = _js("2026/ac-e006257-ab.json")
    tmpl = _js("2026/ac01120-c0001-e006257-u.json")
    muns = [a for a in ab["abr"] if a["tpabr"] == "mun"]
    estado = {}
    for i, a in enumerate(muns):
        te = int(a["e"]["te"])
        est = te if i % 2 == 0 else int(te * frac_apurada) if i % 4 == 1 else 0
        a["e"]["est"] = str(est)
        a["s"]["st"] = "1" if est else "0"
        vv = int(est * 0.75)
        estado[a["cdabr"]] = (te, est, vv)
    calls = {"n": 0}

    def baixar(url, timeout=20):
        calls["n"] += 1
        if url.endswith("-ab.json"):
            return copy.deepcopy(ab)
        cd = url.rsplit("/", 1)[-1][2:7]
        te, est, vv = estado[cd]
        js = copy.deepcopy(tmpl)
        js["cdabr"] = cd
        js["e"]["te"], js["e"]["est"], js["v"]["vv"] = str(te), str(est), str(vv)
        for car in js["carg"]:
            for ag in car["agr"]:
                for par in ag["par"]:
                    for c in par["cand"]:
                        c["vap"] = str(int(vv * {"13": lula, "22": flavio}.get(c["n"], (1 - lula - flavio) / 10)))
        return js
    return baixar, estado, calls


def test_projecao_municipal_2026_ponta_a_ponta(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CACHE_2026", tmp_path)
    baixar, estado, calls = _fake_tse()
    vv = sum(e[2] for e in estado.values())
    votos = {"Lula": vv * 0.40, "Flavio": vv * 0.45}
    votos.update({c: vv * 0.15 / 5 for c in R.CANDS_ANO[2026][2:]})
    res = {"AC": {"pst": 60.0, "votos": votos}, "SP": {"pst": 100.0, "votos": {}}}
    pj = R.projecao_municipal_2026(res, {"ciclo": "ele2026", "cd": "6257"}, log=lambda *a: None, baixar=baixar)
    assert pj is not None and set(pj["ufs"]) == {"AC"}
    r = pj["ufs"]["AC"]
    assert r["S"].sum() == pytest.approx(1) and 0.3 < r["S"][0] < 0.5
    te = sum(e[0] for e in estado.values())
    assert 0.5 * te < r["V"] < 0.9 * te
    n1 = calls["n"]
    # 2ª rodada sem mudanças: só a abrangência é baixada (municípios vêm do cache)
    pj2 = R.projecao_municipal_2026(res, {"ciclo": "ele2026", "cd": "6257"}, log=lambda *a: None, baixar=baixar)
    assert calls["n"] - n1 == 1 and pj2["ufs"]["AC"]["S"] == pytest.approx(r["S"])
    # soma dos municípios incoerente com o arquivo da UF: método antigo na UF
    res_ruim = {"AC": {"pst": 60.0, "votos": {k: v * 1.5 for k, v in votos.items()}}}
    pj3 = R.projecao_municipal_2026(res_ruim, None, log=lambda *a: None, baixar=baixar)
    assert pj3 is None or "AC" not in pj3["ufs"]


def test_falha_no_download_volta_ao_metodo_antigo(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CACHE_2026", tmp_path)

    def quebra(url, timeout=20):
        raise OSError("404")
    res = {"AC": {"pst": 60.0, "votos": {"Lula": 1.0}}}
    assert R.projecao_municipal_2026(res, None, log=lambda *a: None, baixar=quebra) is None


def test_consolidar_com_projecao_municipal():
    res = R.buscar_resultados(2022, "diretorio", FX / "2022", log=lambda *a: None)
    res.pop("_meta")
    h = R._hist()
    r1 = h[(h.ano == 2022) & (h.turno == 1)].set_index("uf")
    ref = pd.DataFrame({"uf": R.UFS, "eleitores": r1.loc[R.UFS, "eleitorado"].values,
                        "abst1": r1.loc[R.UFS, "abstencao_pct"].values,
                        "bn1": (r1.loc[R.UFS, "branco_pct_comp"] + r1.loc[R.UFS, "nulo_pct_comp"]).values})
    res = copy.deepcopy(res)
    res["SP"]["pst"] = 40.0
    S_proj = np.array([0.45, 0.45, 0.04, 0.04, 0.02])
    pj = {"ufs": {"SP": {"S": S_proj, "V": 2.6e7, "sd_logito": 0.05},
                  "RJ": {"S": S_proj, "V": 1.0, "sd_logito": 0.05}}}           # RJ totalizado: projeção ignorada
    c = R.consolidar(res, 2022, ref, None, pj)
    i, j = R.UFS.index("SP"), R.UFS.index("RJ")
    assert c["S"][i] == pytest.approx(S_proj) and c["V1"][i] == 2.6e7 and c["metodo_uf"][i] == "municipios"
    assert c["metodo_uf"][j] == "apurado" and c["V1"][j] > 1e6
    sd = R._sd_proj(c)
    assert sd[i] == pytest.approx(0.05) and sd[j] == 0
    c0 = R.consolidar(res, 2022, ref)
    assert c0["metodo_uf"][i] == "validos/pst" and np.all(np.isnan(c0["sd_mun"]))


def test_rodar_2026_parcial_com_municipios(monkeypatch, tmp_path):
    """Noite da apuração com 30% apurado: AC projetado por município (servidor falso), demais UFs pelo método
    antigo (download dos municípios falha); o pipeline completo roda e registra o método de cada UF."""
    baixar_ac, _, _ = _fake_tse()

    def baixar(url, timeout=20):
        if "/ac/" in url:
            return baixar_ac(url)
        raise OSError("404 (teste)")
    cands = R.CANDS_ANO[2026]
    fat = dict(zip(cands, [0.44, 0.40, 0.06, 0.04, 0.03, 0.02, 0.01]))
    el = pd.read_csv(R.DADOS / "eleitorado_uf_2026.csv").set_index("uf")

    def falso(ano, fonte="auto", diretorio=None, log=print):
        res = {}
        for uf in ["BR"] + R.UFS:
            e = float(el.eleitores_2026.sum() if uf == "BR" else el.loc[uf, "eleitores_2026"])
            est = 0.3 * e
            comp = 0.8 * est
            vv = 0.95 * comp
            res[uf] = {"abr": uf, "pst": 30.0, "psi": 30.0, "eleitorado": e, "eleitorado_totalizado": est,
                       "comparecimento": comp, "abstencao": est - comp, "validos": vv, "brancos": 0.02 * comp,
                       "nulos": 0.03 * comp, "total": comp, "votos": {c: vv * f for c, f in fat.items()},
                       "candidatos": [], "atualizado": "04/10/2026 21:00:00", "formato": "u"}
        res["_meta"] = {"fonte": "TSE (teste)", "codigo": {"ciclo": "ele2026", "cd": "6257", "cdt2": "6258"}, "erros": []}
        return res
    gravados = {}
    monkeypatch.setattr(R, "buscar_resultados", falso)
    monkeypatch.setattr(R, "_baixar", baixar)
    monkeypatch.setattr(R, "CACHE_2026", tmp_path / "cache")
    monkeypatch.setattr(R, "AQUI", tmp_path)
    monkeypatch.setattr(R, "_gravar_json", lambda p, obj: gravados.__setitem__(Path(p).name, json.loads(
        json.dumps(R._limpo(obj), allow_nan=False))))
    # o AC falso tem fatias próprias (40/45): a soma dos municípios não bate com o AC do arquivo da UF -> ajusta
    vv_ac = sum(e[2] for e in _fake_tse()[1].values())
    orig = falso

    def falso_ac(*a, **k):
        res = orig(*a, **k)
        votos = {"Lula": vv_ac * 0.40, "Flavio": vv_ac * 0.45}
        votos.update({c: vv_ac * 0.15 / 5 for c in cands[2:]})
        res["AC"]["votos"] = votos
        res["AC"]["validos"] = vv_ac
        return res
    monkeypatch.setattr(R, "buscar_resultados", falso_ac)
    out = R.rodar_2026(2000, 1, fonte="auto", log=lambda *a: None)
    pp = out["meta"]["projecao_parcial"]
    assert pp["metodo_uf"]["AC"] == "municipios"
    assert pp["metodo_uf"]["SP"] == "validos/pst"
    assert pp["nacional_metodo_antigo"] is not None
    assert "resultados_2t.json" in gravados and gravados["resultados_2t.json"]["meta"]["status"] == "parcial"
    assert 0 <= out["segundo_turno"]["p_a_vence"] <= 1
    # sem municípios (flag): todas as UFs no método antigo
    out2 = R.rodar_2026(2000, 1, fonte="auto", log=lambda *a: None, municipios=False)
    assert out2["meta"]["projecao_parcial"]["metodo_uf"]["AC"] == "validos/pst"
