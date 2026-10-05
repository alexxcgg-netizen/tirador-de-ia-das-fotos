"""Gera simulador/web/nordeste.json (aba "Nordeste" do painel) a partir dos CSVs de
research_notes/Nordeste e cenarios economicos 2026/ (produzidos por nordeste_dados_1t.py).

Números vêm dos CSVs (cálculo próprio sobre dados do TSE/IBGE/MDS, marcados [calc]); os blocos de texto
(o que dizem as pesquisas, explicações concorrentes, estratégias, o que monitorar) são uma curadoria de
nordeste_opiniao.md, cada item com o rótulo da nota ([FATO], [ALEGAÇÃO], [OPINIÃO]) e a fonte.

Uso: python simulador/gerar_nordeste_json.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOTAS = AQUI.parent / "research_notes" / "Nordeste e cenarios economicos 2026"
SAIDA = AQUI / "web" / "nordeste.json"

UF_NE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
CAPITAL = {"MA": "São Luís", "PI": "Teresina", "CE": "Fortaleza", "RN": "Natal", "PB": "João Pessoa",
           "PE": "Recife", "AL": "Maceió", "SE": "Aracaju", "BA": "Salvador"}


def ler(nome: str) -> list[dict]:
    with open(NOTAS / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def r(x, d=1):
    return None if x in (None, "") else round(float(x), d)


def cortes(rows: list[dict]) -> dict:
    out = defaultdict(list)
    for x in rows:
        out[x["corte"]].append({
            "grupo": x["grupo"], "faixa": x.get("faixa") or None, "munic": int(float(x["munic"])),
            "validos26_mil": r(x["validos26_mil"], 0), "lula22": r(x["lula22_%"]), "lula26": r(x["lula26_%"]),
            "flavio26": r(x["flav26_%"]), "bols22": r(x["bols22_%"]), "terc26": r(x["terc26_%"]),
            "swing": r(x["swing_pp"]), "swing2p": r(x["swing2p_pp"]), "dvotos_lula_mil": r(x["dvotos_lula_mil"], 0),
            "dmargem_mil": r(x["dmargem_mil"], 0), "comp22": r(x["comp22_%"]), "comp26": r(x["comp26_%"]),
            "dcomp": r(x["dcomp_pp"]),
        })
    return dict(out)


def capital_interior(rows: list[dict]) -> list[dict]:
    """Por UF: swing da capital (município único, exato) e do interior (média de lula22/lula26 ponderada
    pelos válidos de 2026: aproximação), e Δmargem somada (exata)."""
    acc = {uf: {"cap": None, "int_v": 0.0, "int_l22": 0.0, "int_l26": 0.0, "int_dm": 0.0} for uf in UF_NE}
    for m in rows:
        a = acc[m["uf"]]
        if m["tipo"] == "Capital":
            a["cap"] = m
        else:
            v = float(m["validos"])
            a["int_v"] += v
            a["int_l22"] += v * float(m["lula22"])
            a["int_l26"] += v * float(m["lula26"])
            a["int_dm"] += float(m["dmarg"])
    out = []
    for uf in UF_NE:
        a, c = acc[uf], acc[uf]["cap"]
        out.append({"uf": uf, "capital": CAPITAL[uf], "swing_cap": r(c["swing"]),
                    "swing_int": r((a["int_l26"] - a["int_l22"]) / a["int_v"]),
                    "dmargem_cap_mil": r(float(c["dmarg"]) / 1000, 0), "dmargem_int_mil": r(a["int_dm"] / 1000, 0)})
    return out


def comparecimento_hist(rows: list[dict]) -> list[dict]:
    """Δ comparecimento 1T→2T no NE por ano. Os aptos de cada UF saem de Δvotantes / Δp.p.; a taxa regional é a
    soma dos Δvotantes sobre a soma dos aptos."""
    por_ano = defaultdict(lambda: {"dcomp_mil": 0.0, "aptos_mil": 0.0, "dmargem_pt_mil": 0.0, "ufs": {}})
    for x in rows:
        a = por_ano[int(x["ano"])]
        dm, dpp = float(x["dcomp_mil"]), float(x["dcomp_pp"])
        a["dcomp_mil"] += dm
        a["aptos_mil"] += dm * 100 / dpp
        a["dmargem_pt_mil"] += float(x["dmargem_pt_mil"])
        a["ufs"][x["uf"]] = r(dpp)
    return [{"ano": ano, "dcomp_pp": r(a["dcomp_mil"] / a["aptos_mil"] * 100), "dvotantes_mil": r(a["dcomp_mil"], 0),
             "dmargem_pt_mil": r(a["dmargem_pt_mil"], 0), "ufs": {uf: a["ufs"].get(uf) for uf in UF_NE}}
            for ano, a in sorted(por_ano.items())]


def cenarios(rows: list[dict]) -> list[dict]:
    out = []
    for x in rows:
        nome = x["cenario"]
        cod, _, desc = nome.partition(". ")
        out.append({"cod": cod, "descricao": desc, "transferencia_mil": r(x["transferencia_mil"], 0),
                    "comparecimento_mil": r(x["comparecimento_mil"], 0), "brancos_nulos_mil": r(x["brancos_nulos_mil"], 0),
                    "total_mil": r(x["total_NE_mil"], 0), "pct_gap": r(x["%_do_gap"], 0)})
    return out


def terceiros(rows: list[dict]) -> list[dict]:
    return [{"uf": x["uf"], "caiado_mil": r(x["caiado_mil"], 0), "cury_mil": r(x["cury_mil"], 0),
             "renan_mil": r(x["renan_mil"], 0), "zema_mil": r(x["zema_mil"], 0), "total_mil": r(x["4_terc_mil"], 0),
             "pct_validos": r(x["4_terc_%val"])} for x in rows]


# ---------- curadoria de nordeste_opiniao.md (texto; rótulos da nota)
Q = "https://jornaldaparaiba.com.br/politica/preocupacao-com-corrupcao-dobra-no-nordeste-e-chega-a-18-aponta-genialquaest"
OPINIAO = {
    "preocupacoes": {
        "titulo": "Maior problema, segundo eleitores do NE (Quaest)",
        "colunas": ["abr./2026", "fev./2026"],
        "linhas": [["Violência", 34, 35], ["Corrupção", 18, 9], ["Questões sociais", 15, None], ["Saúde", 14, None],
                   ["Economia", 8, 12], ["Educação", 5, None]],
        "fonte": "Quaest, 10–13/04/2026, recorte NE (Jornal da Paraíba, 24/04/2026)", "url": Q,
    },
    "itens": [
        {"rot": "FATO", "txt": "Custo de vida: 60% dos nordestinos disseram que o poder de compra diminuiu em 12 meses (fev./2026; 21% igual, 18% aumentou). A percepção de alta dos alimentos passou de 58% para 72% entre março e abril.",
         "fonte": "Quaest, 05–09/02/2026 (Jornal da Paraíba)", "url": "https://jornaldaparaiba.com.br/politica/60-dos-nordestinos-dizem-que-poder-de-compra-diminuiu-em-1-ano-diz-genialquaest"},
        {"rot": "FATO", "txt": "Aprovação de Lula no NE: 61% aprovam e 36% desaprovam (24–27/09/2026), a única região com saldo positivo (nacional 46 x 49). A desaprovação no NE subiu de 29% para 35% entre julho e setembro.",
         "fonte": "Quaest (InfoMoney, 28/09/2026)", "url": "https://www.infomoney.com.br/politica/quaest-lula-registra-46-de-aprovacao-e-49-de-desaprovacao/"},
        {"rot": "FATO", "txt": "Bolsa Família: entre beneficiários, Lula foi de 51% para 64% na semana anterior ao reajuste de 15% e ficou em 64% depois dele. Não aparece efeito adicional do anúncio. O pagamento reajustado começa em 19/10, seis dias antes do 2º turno.",
         "fonte": "BTG/Nexus, 18–20/09/2026 (Correio); Decreto 13.120/2026 (Metrópoles)", "url": "https://www.correio24horas.com.br/eleicoes/lula-nao-tem-ganho-mas-mantem-64-da-preferencia-de-beneficiarios-do-bolsa-familia-apos-anuncio-de-reajuste-aponta-pesquisa-0926"},
        {"rot": "FATO", "txt": "Religião: entre católicos do NE, Lula tem vantagem de 29 a 53 p.p. em todos os estados. Entre evangélicos, a disputa empata na PB (35 x 35) e se inverte em AL (Flávio 48 x Lula 25).",
         "fonte": "Quaest, 24–29/08/2026 (CartaCapital, 05/09/2026)", "url": "https://www.cartacapital.com.br/artigo/lula-lidera-com-folga-no-nordeste-mas-enfrenta-resistencia-entre-evangelicos/"},
        {"rot": "FATO", "txt": "Pesquisas x urna: na Bahia, a AtlasIntel deu 60,5% a Lula nos válidos; o resultado foi 66,1%. No Piauí, 68,5% previstos contra 71,0%. Base limitada: não generalizar sem as estaduais de outros institutos.",
         "fonte": "AtlasIntel, 27/09–02/10 (Exame, 03/10/2026)", "url": "https://exame.com/brasil/pesquisa-atlasintel-lula-lidera-com-vantagem-de-307-pontos-no-maior-colegio-do-nordeste/"},
    ],
}

EXPLICACOES = [
    {"exp": "Custo de vida e alimentos", "quem": "Rogério Marinho (PL), Revista Oeste, Felipe Nunes (Quaest), B. Tadeu César (UFRGS)",
     "a_favor": "60% perderam poder de compra (Quaest, fev.); cesta básica com maior alta no NE (DIEESE, 1º tri)",
     "contra": "Aprovação no NE em 61% em setembro; reajuste do Bolsa Família e salário mínimo atenuam"},
    {"exp": "Segurança e violência", "quem": "Gazeta do Povo; oposições estaduais (ACM Neto, Ciro); CartaCapital",
     "a_favor": "Violência é o problema nº 1 (34–40%); BA, AL, PE e CE com altas taxas de homicídio (Atlas da Violência 2026)",
     "contra": "Governadores do PT na BA e no CE reeleitos no 1º turno; punição ao governante \"não é automática\" (Piquet Carneiro)"},
    {"exp": "Crescimento evangélico e voto por valores", "quem": "Nexo; CartaCapital (Menezes, UFBA); BBC (V. Araújo)",
     "a_favor": "Empate ou inversão entre evangélicos na PB e em AL; desaprovação de 53–63% entre evangélicos em BA, PB e AL",
     "contra": "Nos municípios, Lula perdeu menos onde há mais evangélicos [calc]; AD Madureira apoiou Caiado; 83% rejeitam voto indicado pelo pastor"},
    {"exp": "Ascensão social e nova classe média", "quem": "Edinho Silva (PT) [ALEGAÇÃO]; Priscila Lapa (UFPE); Simone Viscarra (Univasf)",
     "a_favor": "Erosão urbana de longo prazo nas capitais (−13,5 p.p. de 2006 a 2022); fronteira agrícola virou à direita",
     "contra": "Em 2026 a queda foi maior no interior pequeno (−3,8 p.p.) que nas capitais (−0,6) [calc]"},
    {"exp": "Escândalos (INSS, Banco Master)", "quem": "Gazeta do Povo, Revista Oeste, PL (vice Alfredo Gaspar)",
     "a_favor": "NE é a região mais afetada pela fraude do INSS; corrupção como problema dobrou no NE (9% → 18%)",
     "contra": "Master atinge os dois lados; no NE o governo foi mais bem avaliado na resposta ao INSS"},
    {"exp": "Fragmentação: migração para Cury e Caiado", "quem": "Diagnóstico interno da campanha de Lula (CNN, 21/09)",
     "a_favor": "BTG/Nexus: 5% dos eleitores de Lula em 2022 foram para Cury e 5% para Caiado",
     "contra": "Os terceiros somaram só 5,2% dos válidos no NE [calc]; parte pode voltar no 2º turno"},
    {"exp": "Política local e governadores", "quem": "Imprensa regional",
     "a_favor": "Aliados do governo perderam em PE, AL e MA",
     "contra": "Voto \"Luquel\" em PE (Lula teve 63,5% no estado); derrota de aliado não é perda de voto presidencial"},
    {"exp": "Desgaste de 16+ anos e novos canais de comunicação", "quem": "Movimento Econômico (Márcio Didier)",
     "a_favor": "Desaprovação em paridade técnica em alguns estados no início de 2026", "contra": "Difícil de medir"},
]

ESTRATEGIAS = {
    "Lula": [
        {"rot": "FATO", "txt": "Reta final do 1º turno no NE (Recife, Feira de Santana, AL, CE). Temas: Bolsa Família, bets, salário mínimo, fim da escala 6x1."},
        {"rot": "ALEGAÇÃO", "txt": "Para o 2º turno: caminhadas em vez de comícios, coordenação com Camilo Santana e foco na abstenção de idosos e mais pobres (CNN, 03/10)."},
        {"rot": "FATO", "txt": "Governadores aliados reeleitos na BA, no CE e no PI; senadores do PT eleitos na BA e em PE."},
    ],
    "Flávio": [
        {"rot": "FATO", "txt": "Giro pelo NE no 1º turno (Maceió, Arapiraca, Fortaleza, Juazeiro do Norte, Recife, Vitória da Conquista, Natal, São Luís) e guinada ao Sudeste a 11 dias do pleito."},
        {"rot": "ALEGAÇÃO", "txt": "Slogan \"Nordeste é solução\"; foco em segurança, emprego, custo de vida. Vice nordestino Alfredo Gaspar (PL-AL), relator da CPMI do INSS, com a missão de rodar os 9 estados."},
        {"rot": "ALEGAÇÃO", "txt": "Para o 2º turno: ofensiva no NE para reduzir rejeição, coordenação de Rogério Marinho (PL-RN), mais agendas em igrejas evangélicas (CNN, 03/10)."},
    ],
    "fonte": "nordeste_opiniao.md, seções 4–6 (CNN Brasil, InfoMoney, Exame, Metrópoles, Voz da Bahia)",
    "url": "https://www.cnnbrasil.com.br/blogs/taina-falcao/eleicoes/lula-e-flavio-ajustam-rota-e-desenham-estrategias-para-eventual-2o-turno/",
}

MONITORAR = [
    {"tit": "Governadores do PSD", "txt": "O PSD declarou neutralidade e liberou os diretórios. Três governadores do NE são do partido: Raquel Lyra (PE), Eduardo Braide (MA) e Fábio Mitidieri (SE). Até 05/10 não havia declaração deles para o 2º turno.",
     "url": "https://www.cnnbrasil.com.br/eleicoes/psd-de-caiado-adota-neutralidade-e-libera-diretorios-em-2o-turno/"},
    {"tit": "Assembleia de Deus Madureira", "txt": "A CONAMAD apoiou Caiado no 1º turno e não definiu posição para o 2º. Com Caiado fora, a direção dessa rede (sobretudo em AL, PB e RN) é o principal ponto a observar no voto evangélico.",
     "url": "https://veronoticias.com/politica/assembleia-de-deus-madureira-se-afasta-de-flavio-bolsonaro-e-apoia-caiado/"},
    {"tit": "Ciro Gomes", "txt": "Derrotado por Elmano (PT) no CE, mas vencedor em Fortaleza por cerca de 98 mil votos. O PL negociava um apoio de Ciro a Flávio no 2º turno (O Povo, 05/09).",
     "url": "https://mais.opovo.com.br/colunistas/joao-paulo-biage-politica-brasilia/2026/09/05/pl-articula-apoio-de-ciro-a-flavio-no-2-turno.html"},
    {"tit": "Comparecimento e Bolsa Família", "txt": "Pagamento reajustado a partir de 19/10. O NE já tem a menor abstenção do país; em 2014, 2018 e 2022 o comparecimento regional não subiu mais de 0,2 p.p. entre os turnos [calc].", "url": None},
    {"tit": "RN e capitais apertadas", "txt": "2º turno estadual no RN (Allyson Bezerra x Cadu de Lula) casado com o presidencial; Natal e João Pessoa foram as capitais mais disputadas.", "url": None},
]


def main():
    uf_rows = ler("nordeste_swing_cortes.csv")
    c = cortes(uf_rows)
    ne = next(x for x in c["uf"] if x["grupo"] == "NE")
    terc = terceiros(ler("nordeste_terceiros_uf.csv"))
    terc_ne = next(x for x in terc if x["uf"] == "NE")
    hist = comparecimento_hist(ler("nordeste_comparecimento_1t2t_hist.csv"))
    cen = cenarios(ler("nordeste_cenarios_2t.csv"))
    ci = capital_interior(ler("nordeste_swing_municipios.csv"))
    ufs = [x for x in c["uf"] if x["grupo"] != "NE"]
    top3 = sorted(ufs, key=lambda x: x["dmargem_mil"])[:3]
    out = {
        "meta": {
            "titulo": "Nordeste no 1º turno de 2026 x 2022",
            "referencia": "2026-10-05",
            "gerado_por": "simulador/gerar_nordeste_json.py",
            "fontes": [
                "TSE: 1º turno 2026 por município (modelo_municipal/data/mun_2026_1t.csv), 2022 e 2018 (munzona)",
                "IBGE Censo 2022 (evangélicos, renda), MDS (Bolsa Família set./2026)",
                "research_notes/Nordeste e cenarios economicos 2026: nordeste_dados_1t.py, nordeste_dados_1t.md, nordeste_opiniao.md",
            ],
            "nota_calc": "[calc] = cálculo próprio a partir dos arquivos do TSE/IBGE/MDS no repositório. Swing = % de Lula nos válidos no 1T 2026 menos no 1T 2022. Δmargem = (Lula − Flávio) 2026 menos (Lula − Bolsonaro) 2022, em votos.",
        },
        "resumo": {
            "lula26": ne["lula26"], "flavio26": ne["flavio26"], "lula22": ne["lula22"], "bols22": ne["bols22"],
            "margem22_pp": r(ne["lula22"] - ne["bols22"]), "margem26_pp": r(ne["lula26"] - ne["flavio26"]),
            "swing": ne["swing"], "dmargem_mil": ne["dmargem_mil"], "dmargem_nacional_mil": -8450,
            "comp22": ne["comp22"], "comp26": ne["comp26"], "dcomp": ne["dcomp"], "comp_br22": 79.05, "comp_br26": 78.88,
            "terceiros_mil": terc_ne["total_mil"], "terceiros_pct": terc_ne["pct_validos"],
            "gap_nacional_mil": 2259, "eleitorado_ne_pct": 27.4,
            "maiores_perdas": [{"uf": x["grupo"], "dmargem_mil": x["dmargem_mil"]} for x in top3],
        },
        "uf": ufs,
        "tipo": c["tipo"], "porte": c["porte"], "pbf": c["pbf"], "evang": c["evang"], "renda": c["renda"],
        "capital_interior": ci,
        "terceiros_uf": terc,
        "comparecimento_1t2t": hist,
        "cenarios": cen,
        "cenarios_nota": ("Contribuição líquida do NE (Lula − Flávio, mil votos) por três canais: transferência dos votos "
                          "dos 4 terceiros do NE, variação do comparecimento entre turnos e brancos/nulos que passam a votar "
                          "válido. São exercícios aritméticos condicionais, não previsões. Matrizes: Quaest nacional "
                          "(2–3/10 e 24–27/9), \"pró-Lula\" (+10 p.p. para Lula em cada terceiro) e \"pró-Flávio\" "
                          "(inspirada na inferência ecológica de 2022 no NE)."),
        "opiniao": OPINIAO,
        "explicacoes": EXPLICACOES,
        "estrategias": ESTRATEGIAS,
        "monitorar": MONITORAR,
    }
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("gravado:", SAIDA)
    return out


if __name__ == "__main__":
    main()
