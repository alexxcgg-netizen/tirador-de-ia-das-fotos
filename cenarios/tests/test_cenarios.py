import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import importlib.util  # noqa: E402

import cenarios as C  # noqa: E402
import premissas as PR  # noqa: E402

# carrega cenarios/rodar.py com nome próprio (simulador/ também tem um rodar.py)
_spec = importlib.util.spec_from_file_location("cenarios_rodar", Path(__file__).resolve().parents[1] / "rodar.py")
RD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RD)

N = 4000
TIPOS = list(PR.TIPOS)


@pytest.fixture(scope="module")
def par():
    return C.rodar_par(N, 7, PR.CANDIDATOS)


def _d(R, h):
    return R["L"]["familias"][h]["idx"] - R["F"]["familias"][h]["idx"]


# ---------------------------------------------------------------------------
# Básicos
# ---------------------------------------------------------------------------
def test_triangular_limites_e_media():
    u = np.random.default_rng(0).random(200_000)
    v = C.tri_ppf(u, 1.0, 2.0, 6.0)
    assert v.min() >= 1.0 and v.max() <= 6.0
    assert abs(v.mean() - 3.0) < 0.02


def test_ir_lei_15270_e_correcao():
    assert C.ir_mensal(3777.0, C.inss(3777.0)) == pytest.approx(0.0)
    sem = C.ir_mensal(6500.0, C.inss(6500.0), reducao=False)
    com = C.ir_mensal(6500.0, C.inss(6500.0), reducao=True)
    assert sem - com == pytest.approx(978.62 - 0.133145 * 6500, abs=0.01)
    # arrasto de faixa: renda nominal 5.200 paga IR com tabela congelada, não com tabela corrigida 10%
    assert C.ir_mensal(5200.0, C.inss(5200.0), True, 1.0) > 0
    assert C.ir_mensal(5200.0, C.inss(5200.0), True, 1.1) == pytest.approx(0.0)


def test_calibracao_divida_2027():
    assert C.DIVIDA_CONS[0] == pytest.approx(86.4, abs=1e-6)


def test_rotulo_media_nao_mediana():
    """R8: R$ 3.777 é a renda MÉDIA da PNADC; nenhuma família-tipo se diz 'mediana'."""
    assert "renda_mediana" not in PR.BASE and PR.BASE["renda_media_trabalho"] == 3777.0
    assert all("median" not in t["nome"].lower() for t in PR.TIPOS.values())


def test_familias_pedidas():
    assert len(PR.TIPOS) == 10
    for k in ("formal_sm", "informal_sm", "autonomo", "bf_ne", "bf_resto", "aposentado_piso", "aposentado_acima",
              "classe_media", "endividado", "topo"):
        assert k in PR.TIPOS


# ---------------------------------------------------------------------------
# Mesma régua (neutralidade)
# ---------------------------------------------------------------------------
def _chaves(d):
    if isinstance(d, dict):
        return {k: _chaves(v) for k, v in d.items() if k != "nome"}
    return None


def test_programas_tem_mesmas_chaves():
    assert _chaves(PR.CANDIDATOS["L"]) == _chaves(PR.CANDIDATOS["F"])
    for cj in PR.CONJUNTOS:
        _, sp = PR.aplicar_conjunto(cj)
        assert _chaves(sp["L"]) == _chaves(sp["F"])


def test_codigo_sem_nome_de_candidato():
    """Nenhum sinal fixo: a simulação não conhece rótulos de candidato."""
    for f in (C.simular, C._familia):
        src = inspect.getsource(f)
        corpo = src.split('"""', 2)[-1]
        for proibido in ('"L"', '"F"', "'L'", "'F'", "Lula", "Flávio", "Flavio", "Bolsonaro"):
            assert proibido not in corpo, (f.__name__, proibido)


def test_espelho_trocar_programas_inverte_resultado():
    a = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["L"], "F": PR.CANDIDATOS["F"]})
    b = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["F"], "F": PR.CANDIDATOS["L"]}, slots=("2", "1"))
    for h in TIPOS:
        np.testing.assert_allclose(_d(a, h), -_d(b, h), atol=1e-9)
    np.testing.assert_allclose(a["L"]["macro"]["divida"], b["F"]["macro"]["divida"])


def test_mesmo_programa_diferenca_nula():
    R = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["F"], "F": PR.CANDIDATOS["F"]}, slots=("1", "1"))
    for h in TIPOS:
        assert np.all(_d(R, h) == 0)


@pytest.mark.parametrize("canal", PR.CANAIS)
def test_cada_canal_pode_favorecer_qualquer_um(canal):
    """Com só um canal ligado, trocar os programas troca o sinal da contribuição: o canal não tem
    sinal embutido; o que decide é o parâmetro."""
    on = {c: (c == canal) for c in PR.CANAIS}
    a = C.rodar_par(1000, 5, {"L": PR.CANDIDATOS["L"], "F": PR.CANDIDATOS["F"]}, canais=on)
    b = C.rodar_par(1000, 5, {"L": PR.CANDIDATOS["F"], "F": PR.CANDIDATOS["L"]}, canais=on, slots=("2", "1"))
    for h in TIPOS:
        np.testing.assert_allclose(_d(a, h).mean(0), -_d(b, h).mean(0), atol=1e-9)


def test_regressao_bolsa_familia_mesma_regra():
    """Revisão R1: na v1 o hiato do Bolsa Família (+7 pontos, P = 0,98) vinha de reajustes reais
    assimétricos. Com prior assimétrico o hiato reaparece; com a mesma regra para os dois, trocar só o
    bloco do Bolsa Família não move a diferença."""
    lp, fp = deepcopy(PR.CANDIDATOS["L"]), deepcopy(PR.CANDIDATOS["F"])
    assert lp["bolsa"] == fp["bolsa"]
    lp_v1 = deepcopy(lp); fp_v1 = deepcopy(lp)
    lp_v1["bolsa"] = {"p_reajuste": 1.0, "real_extra": 1.0}
    fp_v1["bolsa"] = {"p_reajuste": 0.3, "real_extra": 0.0}
    v1 = C.rodar_par(2000, 9, {"L": lp_v1, "F": fp_v1}, tipos=["bf_ne"], slots=("1", "1"))
    assert _d(v1, "bf_ne")[:, PR.ANOS.index(2030)].mean() > 3.0
    igual = C.rodar_par(2000, 9, {"L": lp, "F": fp}, tipos=["bf_ne"])
    troca = deepcopy(fp); troca["bolsa"] = deepcopy(lp["bolsa"])
    igual2 = C.rodar_par(2000, 9, {"L": lp, "F": troca}, tipos=["bf_ne"])
    np.testing.assert_allclose(_d(igual, "bf_ne"), _d(igual2, "bf_ne"))


# ---------------------------------------------------------------------------
# Mecanismos
# ---------------------------------------------------------------------------
def test_regra_do_minimo_usa_pib_de_t_menos_2():
    """Revisão R2 (bug da v1): o ganho real de 2029 usa o PIB de 2027, não o de 2028."""
    r = C.simular(PR.CANDIDATOS["L"], 2000, 11, "1", fixos={"regra": True})
    m = r["macro"]
    niv_inpc = np.cumprod(1 + m["inpc"] / 100, axis=1)
    sm = m["sm_real"] / 100 * PR.BASE["salario_minimo"] * niv_inpc
    i28, i29 = PR.ANOS.index(2028), PR.ANOS.index(2029)
    esperado = sm[:, i28] * (1 + m["inpc"][:, i28] / 100) * (1 + np.clip(m["pib"][:, PR.ANOS.index(2027)], 0.6, 2.5) / 100)
    np.testing.assert_allclose(sm[:, i29], esperado, rtol=1e-9)
    errado = sm[:, i28] * (1 + m["inpc"][:, i28] / 100) * (1 + np.clip(m["pib"][:, i28], 0.6, 2.5) / 100)
    assert np.abs(sm[:, i29] - errado).max() > 1.0


def test_regime_markov():
    assert np.allclose(PR.TRANSICAO.sum(1), 1)
    for c in PR.CANDIDATOS.values():
        assert sum(c["regime"]["pi0"]) == pytest.approx(1.0)
    r = C.simular(PR.CANDIDATOS["L"], 20000, 2, "1")
    freq = np.bincount(r["regime_ini"], minlength=3) / 20000
    np.testing.assert_allclose(freq, PR.CANDIDATOS["L"]["regime"]["pi0"], atol=0.015)
    cr = C.simular(PR.CANDIDATOS["L"], 3000, 2, "1", fixos={"s0": 2})
    ok = C.simular(PR.CANDIDATOS["L"], 3000, 2, "1", fixos={"s0": 0})
    assert np.median(cr["macro"]["cambio"][:, 0]) > np.median(ok["macro"]["cambio"][:, 0])
    assert cr["macro"]["selic"][:, 0].mean() > ok["macro"]["selic"][:, 0].mean()


def test_realimentacao_fiscal_ligada():
    """Revisão R3: dívida acima do consenso encarece juros (o canal estava desligado na v1)."""
    a = deepcopy(PR.CANDIDATOS["F"]); b = deepcopy(PR.CANDIDATOS["F"])
    a["fiscal"]["ajuste_total"] = 0.0
    b["fiscal"]["ajuste_total"] = 2.5
    ra = C.simular(a, 4000, 4, "1", fixos={"s0": 1})
    rb = C.simular(b, 4000, 4, "1", fixos={"s0": 1})
    assert ra["macro"]["divida"][:, 3].mean() > rb["macro"]["divida"][:, 3].mean() + 1
    assert ra["macro"]["premio"][:, 3].mean() > rb["macro"]["premio"][:, 3].mean()
    assert ra["macro"]["selic"][:, 3].mean() > rb["macro"]["selic"][:, 3].mean()


def test_incidencia_dos_cortes():
    """Revisão R4: o mesmo ajuste feito em obrigatórias (abono) pesa mais no formal de 1 SM do que
    feito em receita sobre o topo; e o topo paga a receita sobre o topo."""
    base = deepcopy(PR.CANDIDATOS["F"])
    base["fiscal"]["ajuste_total"] = 1.5
    base["fiscal"]["receita_unica"] = 0.0
    base["minimo"]["p_intencao"] = 1.0
    ob, tp = deepcopy(base), deepcopy(base)
    ob["fiscal"]["composicao"] = [0.0, 0.0, 0.0, 1.0]
    tp["fiscal"]["composicao"] = [1.0, 0.0, 0.0, 0.0]
    ob["fiscal"]["concentracao"] = tp["fiscal"]["concentracao"] = 1e6
    R = C.rodar_par(3000, 6, {"L": ob, "F": tp}, fixos={"s0": 0, "regra": True}, slots=("1", "1"))
    i = PR.ANOS.index(2030)
    assert _d(R, "formal_sm")[:, i].mean() < -0.5
    assert _d(R, "topo")[:, i].mean() > 0.3


def test_promessa_sem_fonte_tem_custo():
    a = deepcopy(PR.CANDIDATOS["F"]); b = deepcopy(PR.CANDIDATOS["F"])
    a["iva"]["p"], b["iva"]["p"] = 0.0, 1.0
    ra, rb = C.simular(a, 3000, 8, "1"), C.simular(b, 3000, 8, "1")
    assert rb["macro"]["divida"][:, -1].mean() > ra["macro"]["divida"][:, -1].mean()


def test_salario_minimo_equilibrio_geral():
    """+1 p.p. de ganho real: aposentado do piso ganha quase tudo; informal ganha pelo farol; preços de
    serviços intensivos em SM sobem; ganho do formal de 1 SM é menor que o do aposentado (emprego)."""
    base = deepcopy(PR.CANDIDATOS["L"]); base["minimo"]["p_intencao"] = 1.0
    ext = deepcopy(base); ext["minimo"]["ganho_extra"] = 1.0
    R = C.rodar_par(3000, 12, {"L": ext, "F": base}, slots=("1", "1"), fixos={"regra": True})
    i = PR.ANOS.index(2030)
    ap, fo, inf_, top = (_d(R, h)[:, i].mean() for h in ("aposentado_piso", "formal_sm", "informal_sm", "topo"))
    assert 2.0 < ap < 3.5
    assert 0.3 < inf_ < ap
    assert fo < ap
    assert abs(top) < 0.5
    assert (R["L"]["macro"]["servicos_sm"][:, 1:4].mean() > R["F"]["macro"]["servicos_sm"][:, 1:4].mean())


def test_camada_vivido_simetrica_e_alavancada(par):
    R = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["L"], "F": PR.CANDIDATOS["L"]}, slots=("1", "1"))
    for h in TIPOS:
        np.testing.assert_array_equal(R["L"]["familias"][h]["idx_vivido"], R["F"]["familias"][h]["idx_vivido"])
    # renda livre depois da dívida é alavancada: mais volátil e mais sensível à Selic que a oficial
    e = par["L"]["familias"]["endividado"]
    i = PR.ANOS.index(2030)
    assert e["idx_vivido"][:, i].std() > e["idx"][:, i].std()
    sel = par["L"]["macro"]["selic"][:, i]
    gap = e["idx_vivido"][:, i] - e["idx"][:, i]
    assert np.corrcoef(sel, gap)[0, 1] < 0


def test_receita_unica_some_e_volta_como_conta():
    """conta_completa_politicas.md: receita única melhora o primário em 2027–28 e falta depois."""
    a = deepcopy(PR.CANDIDATOS["F"]); b = deepcopy(PR.CANDIDATOS["F"])
    a["fiscal"]["receita_unica"], b["fiscal"]["receita_unica"] = 0.0, 0.7
    ra = C.simular(a, 3000, 4, "1", fixos={"s0": 0})
    rb = C.simular(b, 3000, 4, "1", fixos={"s0": 0})
    pa, pb = ra["macro"]["primario"].mean(0), rb["macro"]["primario"].mean(0)
    assert abs(pb[0] - pa[0]) < 0.15            # 2027: mesmo resultado primário (receita no lugar do corte)
    assert pb[3] < pa[3] - 0.2                   # 2030: o buraco aparece
    assert pb[5] < pa[5] - 0.2                   # 2032: antecipação falta
    assert rb["macro"]["corte_obrigatoria"][:, 0].mean() < ra["macro"]["corte_obrigatoria"][:, 0].mean()


def test_credito_direcionado_e_ressaca():
    """custos_ocultos_credito_subsidios.md: mais direcionado → Selic mais alta (C7); crédito novo às
    famílias → impulso no início e PIB menor depois (C22); mesma regra para qualquer programa."""
    a = deepcopy(PR.CANDIDATOS["L"]); b = deepcopy(PR.CANDIDATOS["L"])
    for s in (a, b):
        s["credito"]["expansao_credito"] = 0.0
    a["credito"]["direcionado_dfatia"], b["credito"]["direcionado_dfatia"] = 0.0, 2.0
    ra, rb = C.simular(a, 3000, 5, "1", fixos={"s0": 1}), C.simular(b, 3000, 5, "1", fixos={"s0": 1})
    assert rb["macro"]["selic"][:, 3].mean() > ra["macro"]["selic"][:, 3].mean() + 0.1
    c_, d_ = deepcopy(a), deepcopy(a)
    d_["credito"]["expansao_credito"] = 1.0
    rc, rd = C.simular(c_, 3000, 5, "1", fixos={"s0": 1}), C.simular(d_, 3000, 5, "1", fixos={"s0": 1})
    assert rd["macro"]["pib"][:, 0].mean() > rc["macro"]["pib"][:, 0].mean()
    assert rd["macro"]["pib"][:, 5].mean() < rc["macro"]["pib"][:, 5].mean()


def test_horizonte_ate_2034_e_ajuste_forcado(par):
    assert PR.ANOS[0] == 2027 and PR.ANOS[-1] == 2034 and len(PR.ANOS) == PR.T == 8
    assert par["L"]["macro"]["ajuste_forcado"][:, :PR.ANOS_MANDATO].max() == 0
    assert par["L"]["macro"]["ajuste_forcado"][:, -1].max() > 0


def test_shapley_eficiencia_pequeno():
    phi, cheio, vazio = RD.shapley(["sm_direto", "fiscal", "cambio"], 800, 1, PR.CANDIDATOS, procs=1)
    np.testing.assert_allclose(phi.sum(0), cheio - vazio, atol=1e-9)


def test_reponderacao_por_regime_reproduz_media(par):
    i = PR.ANOS.index(2030)
    for h in ("formal_sm", "topo"):
        cel = RD.celulas(par["L"], par["F"], h)
        piL, piF = PR.CANDIDATOS["L"]["regime"]["pi0"], PR.CANDIDATOS["F"]["regime"]["pi0"]
        mix = sum(piL[a] * piF[b] * cel["D"][f"{a}{b}"]["media"][i] for a in range(3) for b in range(3))
        assert mix == pytest.approx(_d(par, h)[:, i].mean(), abs=0.35)
        n = sum(c["n"] for c in cel["D"].values())
        assert n == N


def test_veredito_inconclusivo_quando_sinal_muda():
    fam = lambda v: {"familias": {"x": {"D": {"media": [v], "p_L_maior": [0.9], "p_F_maior": [0.1]}}}}
    pc = {"central": fam(2.0), "neutro": fam(1.5), "pro_lula": fam(3.0), "pro_flavio": fam(-0.5)}
    assert RD.veredito(pc, "x", 0)["codigo"] == "inconclusivo"
    pc["pro_flavio"] = fam(1.2)
    assert RD.veredito(pc, "x", 0)["codigo"] == "robusto_L"
    pc["pro_flavio"] = fam(0.2)
    assert RD.veredito(pc, "x", 0)["codigo"] == "fragil_L"


def test_sanduiche_matriz_e_mesma_regua():
    assert len(PR.SANDUICHE) == 18
    R = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["L"], "F": PR.CANDIDATOS["F"]}, tipos=list(PR.SANDUICHE))
    S = RD.sanduiche(R["L"], R["F"])
    assert set(S["teste"]) == {"clt", "pj", "capital"}
    b = C.rodar_par(1500, 3, {"L": PR.CANDIDATOS["F"], "F": PR.CANDIDATOS["L"]}, tipos=list(PR.SANDUICHE), slots=("2", "1"))
    for h in PR.SANDUICHE:
        np.testing.assert_allclose(_d(R, h), -_d(b, h), atol=1e-9)
    # reverter o imposto mínimo ajuda a PJ de 50+ SM e não mexe na CLT de até 2 SM
    a = deepcopy(PR.CANDIDATOS["F"]); z = deepcopy(PR.CANDIDATOS["F"])
    a["ir"]["p_reverte_topo"], z["ir"]["p_reverte_topo"] = 1.0, 0.0
    a["ir"]["p_reverte_bancos"] = z["ir"]["p_reverte_bancos"] = 0.0
    Q = C.rodar_par(1500, 3, {"L": a, "F": z}, tipos=["s_50mais_pj", "s_ate2_clt"], slots=("1", "1"))
    assert _d(Q, "s_50mais_pj")[:, -1].mean() > 1.0


def test_json_publicado():
    p = RD.SAIDA
    if not p.exists():
        pytest.skip("cenarios.json ainda não gerado")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["versao"] == 2 and d["meta"]["anos"][-1] == 2034
    for k in ("resultados", "robustez", "shapley", "experimento_sm", "tornado", "parametros"):
        assert k in d
    assert set(d["resultados"]) == {"central", "neutro", "pro_lula", "pro_flavio"}
    assert set(d["robustez"]) == set(PR.TIPOS)
