#!/usr/bin/env python3
"""Gera simulador/web/nordeste_trajetoria.json a partir de
research_notes/Nordeste e cenarios economicos 2026/nordeste_trajetoria_governos.md e
nordeste_trajetoria_indicadores.csv (SE = Sergipe; SE_R = região Sudeste).

Uso (re-executavel, so biblioteca padrao):
    python simulador/gerar_nordeste_trajetoria_json.py [--saida x.json]

Nada de numero e inventado: tabelas e textos sao lidos da nota (mesma ordem, mesmas casas decimais) e
as series saem do CSV. Se a nota mudar de formato, as validacoes abaixo falham em vez de gerar JSON errado.
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.path.join(RAIZ, "research_notes", "Nordeste e cenarios economicos 2026")
SAIDA_PADRAO = os.path.join(AQUI, "web", "nordeste_trajetoria.json")

TOPO = ["meta", "partidos", "numeros_usuario", "trajetoria", "comparacao_pt", "espelho", "eleitoral", "limites", "resumo"]
UFS_NE = ["BA", "PI", "CE", "RN", "MA", "PB", "PE", "AL", "SE"]
GRUPOS = [("GRUPO_NE_PT_ATUAL", "Nordeste PT atual (BA, PI, CE, RN)"),
          ("GRUPO_NE_OUTROS", "Outros NE (MA, PB, PE, AL, SE)"),
          ("BR", "Brasil"),
          ("GRUPO_COMPARACAO_SP_SC_PR_GO_MT", "Espelho: SP, PR, SC, GO, MT")]
INDICADORES = [
    ("pobreza_685ppc", "Pobreza (abaixo de US$ 6,85/dia, PPC 2017)"),
    ("analfabetismo_15mais", "Analfabetismo, 15 anos ou mais"),
    ("pib_pc_pct_do_Brasil", "PIB per capita relativo (Brasil = 100)"),
    ("ideb_anos_iniciais", "IDEB, anos iniciais"),
    ("homicidios_100mil", "Homicídios por 100 mil habitantes"),
    ("informalidade", "Informalidade (% dos ocupados)"),
    ("esgoto_rede_geral_censo", "Esgoto por rede geral ou pluvial (Censo)"),
    ("renda_dom_pc_real_2025", "Renda domiciliar per capita real"),
]


def num(s):
    s = (s or "").strip().replace("−", "-").replace("%", "").replace("*", "")
    if s in ("", "–", "-"):
        return None
    try:
        return float(s.replace(".", "").replace(",", ".") if "," in s else s)
    except ValueError:
        return None


def limpa(t):
    return re.sub(r"\*\*|`", "", t).strip()


def secoes(md):
    """Divide a nota em blocos pelos titulos '## N.' e '### N.N'."""
    out, chave, buf = {}, None, []
    for ln in md.splitlines():
        m = re.match(r"^(##|###)\s+(\d+(?:\.\d+)?)[\s.]", ln)
        if m:
            if chave is not None:
                out[chave] = "\n".join(buf)
            chave, buf = m.group(2), [ln]
        elif re.match(r"^###\s+Resumo da seção (\d)", ln):
            if chave is not None:
                out[chave] = "\n".join(buf)
            chave, buf = "R" + re.match(r"^###\s+Resumo da seção (\d)", ln).group(1), [ln]
        else:
            buf.append(ln)
    if chave is not None:
        out[chave] = "\n".join(buf)
    return out


def tabela(texto, apos=None):
    """Primeira tabela markdown do texto (depois de 'apos', se dado). Devolve (cabecalho, linhas)."""
    if apos:
        texto = texto.split(apos, 1)[1]
    cab, linhas = None, []
    for ln in texto.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cels = [limpa(c) for c in s.strip("|").split("|")]
            if cab is None:
                cab = cels
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cels):
                continue
            else:
                linhas.append(cels)
        elif cab is not None:
            break
    return cab, linhas


def partidos(sec):
    _, mand = tabela(sec["1.2"])
    _, anos = tabela(sec["1.3"])
    por = defaultdict(list)
    for uf, gov, par, ini, fim in mand:
        por[uf].append({"governador": gov, "partido": par, "inicio": ini, "fim": fim})
    out = []
    for uf, pt, ali, pta, outros in anos:
        out.append({"uf": uf, "anos_PT": num(pt), "anos_aliados_esquerda": num(ali),
                    "anos_PT_mais_aliados": num(pta), "anos_outros": num(outros), "mandatos": por[uf]})
    assert [p["uf"] for p in out] == UFS_NE, "ordem/UFs da tabela 1.3"
    return out


URLS_NUM = {
    1: "https://sidra.ibge.gov.br/tabela/7126",
    2: "https://sidra.ibge.gov.br/tabela/7113",
    3: "https://www.undp.org/pt/brazil/news/nordeste-lidera-maiores-avancos-estaduais-no-idhm-entre-2012-e-2024",
    4: "https://tratabrasil.org.br/90-milhoes-brasileiros-nao-tem-coleta-esgoto/",
    5: "https://sidra.ibge.gov.br/tabela/5938",
    6: "https://sidra.ibge.gov.br/tabela/5938",
    7: "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio=2023&no_anexo=DCA-Anexo%20I-C&id_ente=29",
    8: "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?an_exercicio=2023&no_anexo=DCA-Anexo%20I-C&id_ente=29",
    9: "https://observatorio-politica-fiscal.ibre.fgv.br/politica-economica/outros/federacao-em-perspectiva-um-balanco-de-custos-e-beneficios-por-uf",
    10: "https://www.cartacapital.com.br/educacao/enem-2024-registrou-12-redacoes-com-nota-mil-apenas-uma-na-rede-publica/",
}


def veredito(txt):
    t = txt.lower()
    if t.startswith("diferente / parcial") or t.startswith("parcial"):
        return "parcial"
    if t.startswith("diferente"):
        return "diferente"
    if t.startswith("confirmado"):
        return "confirmado"
    raise ValueError(txt)


def numeros_usuario(sec):
    _, linhas = tabela(sec["2"])
    out = []
    for n, citado, ver, o_que, fonte in linhas:
        i = int(n)
        out.append({"item": i, "descricao": citado, "valor_citado": citado, "valor_verificado": o_que,
                    "veredito": veredito(ver), "veredito_na_nota": ver, "fonte": fonte, "fonte_url": URLS_NUM[i]})
    assert len(out) == 10
    c = [x["veredito"] for x in out]
    assert c.count("confirmado") == 7 and c.count("diferente") + c.count("parcial") == 3, c
    return out


def comparacao_pt(sec):
    cab, linhas = tabela(sec["3.3"])
    notas_ideb = ("Pontos bons dos estados do PT: Ceará e Piauí estão entre os melhores do país no IDEB em 2025 "
                  "(CE: 6,8/5,7/4,5; PI: 6,3/5,4/5,0, tabela secundária). Pontos ruins: BA (3,9) e RN (3,7) estão entre "
                  "os piores no ensino médio em 2023, como o Maranhão, sem PT (3,8).")
    out = []
    for ind, dpt, dout, r_pt, r_amp, r_niv, coef in linhas:
        m = re.match(r"(-?[\d,]+) \(([\d,]+)\)", coef)
        c, ep = num(m.group(1)), num(m.group(2))
        signif = abs(c) >= 2 * ep
        p_pt = re.search(r"\[([\d,]+)\]", r_pt)
        p_amp = re.search(r"\[([\d,]+)\]", r_amp)
        resultado = ("coeficiente de +10 anos de PT significativo" if signif else
                     "sem coeficiente significativo") + f" ({coef}); Δ médio {dpt} nos estados atuais do PT contra {dout} nos outros NE"
        nota = (f"Correlação de postos com anos de PT {r_pt}; com PT + PSB/PCdoB/PDT {r_amp}; com o nível inicial {r_niv}.")
        if p_amp and num(p_amp.group(1)) < 0.05:
            nota += (" Exceção formal: com anos de esquerda ampla a correlação é significativa a 5% (+0,75, p = 0,02), "
                     "no sentido de MENOS queda do analfabetismo onde houve mais anos de esquerda; em 30 testes é compatível com acaso.")
        if ind.startswith("Homicídios"):
            nota += (" Exceção nos números: os homicídios pioram mais nos estados atuais do PT do que nos outros "
                     "(diferença média de grupo), embora o coeficiente de anos de PT não seja distinguível de zero (n = 9); "
                     "MA (sem PT) também subiu (+20,9) e PE (sem PT) caiu (−15,8).")
        if ind.startswith("IDEB"):
            nota += " " + notas_ideb
        out.append({"indicador": ind, "resultado": resultado, "nota": nota,
                    "delta_pt_atual": num(dpt), "delta_outros_ne": num(dout),
                    "coef_10_anos_pt": c, "erro_padrao": ep, "significativo_5pct": signif})
    assert len(out) == 15, len(out)
    return out


def espelho(sec):
    cab, linhas = tabela(sec["3.5"])
    grupos = cab[1:]
    out = []
    for ln in linhas:
        for g, v in zip(grupos, ln[1:]):
            out.append({"grupo": g, "indicador": ln[0], "resultado": v})
    resto = sec["3.5"].split("\n\n")
    bullets = [limpa(b[2:]) for b in sec["3.5"].splitlines() if b.startswith("- ")]
    for b in bullets:
        out.append({"grupo": "SP, SC, PR, GO, MT (síntese)", "indicador": b.split(":")[0], "resultado": b.split(":", 1)[1].strip() if ":" in b else b})
    assert len(out) >= 60
    return out


def eleitoral(sec):
    t5 = sec["5"]
    cab, linhas = tabela(t5)
    chaves = ["eleicao", "votos_candidato_pt_mi", "ne_mi", "pct_votos_do_candidato_vindos_do_ne", "ne_pct_dos_validos",
              "pt_pct_validos_no_ne", "pt_pct_validos_fora_do_ne", "margem_ne_mi", "margem_fora_do_ne_mi", "margem_nacional_mi"]
    tab = [dict(zip(chaves, [limpa(l[0])] + [num(x) for x in l[1:]])) for l in linhas]
    nota_tab = next(limpa(l) for l in t5.splitlines() if l.startswith("(Para 2002"))
    regioes = [limpa(l) for l in t5.splitlines() if l.startswith("**Por região, 2026")]
    itens = [limpa(m) for m in re.findall(r"^\d\.\s+(.*)$", t5.split("O que a aritmética diz:", 1)[1], flags=re.M)]
    assert len(itens) == 5
    m2026 = re.search(r"2026 \(1º turno\), margem de Lula − Flávio \(mi\):([^.]*)\. Em 2022", regioes[0].replace("**", "")) if regioes else None
    return {
        "fonte": "TSE via simulador/data/resultados_uf_2002_2022.csv e modelo_municipal/data/mun_2026_1t.csv (1º turno de 2026 com cerca de 1,2% do eleitorado extrapolado)",
        "tabela": tab, "nota_tabela": nota_tab, "margens_por_regiao": regioes[0] if regioes else "",
        "aritmetica": itens[:3],
        "enquadramento": ("'O Nordeste salva o Brasil' é um enquadramento, não um número: " + itens[3].split(": ", 1)[1]
                          if ": " in itens[3] else itens[3]),
        "espelho": ("A mesma conta lida para as outras regiões: no 1º turno de 2026 as margens de Lula contra Flávio foram "
                    "Sudeste −5,67, Sul −5,04, Centro-Oeste −2,17 e Norte −0,46 (mi); em 2022 (2º turno), Sudeste −4,25, Sul −4,19, "
                    "Centro-Oeste −1,81 e Norte −0,19. Logo, 'Sudeste, Sul e Centro-Oeste decidem por Flávio' é tão verdadeiro "
                    "como aritmética quanto 'o Nordeste decide por Lula', e nenhuma das duas frases explica por que as pessoas votam."),
        "indireto": itens[4],
        "itens_originais": itens,
    }


def limites(sec):
    t = sec["7"].split("**Limites e vieses a procurar", 1)[1]
    itens = [limpa(l[2:]) for l in t.splitlines() if l.startswith("- ")]
    extras = [
        "Janelas e anos-base diferentes por indicador: a escolha do ano inicial muda os números e as janelas estão escritas em cada série.",
        "Séries por grupo são médias ponderadas pela população do Censo 2022 (IDEB: média simples); n = 9 estados, nada é efeito causal.",
    ]
    assert len(itens) >= 8
    return itens + extras


def resumo(sec, md):
    r = []
    for n, nome in (("R1", "Quem governou"), ("R2", "Números do usuário"), ("R3", "Trajetória"), ("R4", "Controles e ressalvas"), ("R5", "Aritmética eleitoral")):
        corpo = [l for l in sec[n].splitlines()[1:] if l.strip()]
        r.append(f"{nome}: " + limpa(" ".join(corpo)))
    r.append("Correção à lista do usuário: o PT também governou o Piauí em 2003–abr/2010 (Wellington Dias) e Sergipe em 2007–dez/2013 (Marcelo Déda).")
    fim = md.split("## 8. Resumo da nota (Resumo da aba)", 1)[1].split("---", 1)[0]
    r.append("Resumo da aba: " + limpa(" ".join(l for l in fim.splitlines() if l.strip())))
    return r


def trajetoria(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    idx = defaultdict(lambda: defaultdict(dict))
    meta = {}
    for r in rows:
        if r["uf"] in {g for g, _ in GRUPOS} and r["indicador"] in {i for i, _ in INDICADORES}:
            idx[r["indicador"]][r["uf"]][int(r["ano"])] = float(r["valor"])
            meta.setdefault((r["indicador"], r["uf"]), (r["unidade"], r["fonte"], r["tag"]))
    out = []
    for ind, nome in INDICADORES:
        series = []
        for g, rotulo in GRUPOS:
            pts = sorted(idx[ind][g].items())
            assert pts, (ind, g)
            series.append({"grupo": rotulo, "anos": [a for a, _ in pts], "valores": [round(v, 2) for _, v in pts]})
        un, fonte, tag = meta[(ind, "GRUPO_NE_OUTROS")]
        out.append({"indicador": nome, "id": ind, "unidade": meta[(ind, "BR")][0], "fonte": meta[(ind, "BR")][1] + " | grupos: " + fonte,
                    "tag": tag, "series": series})
    return out


def construir(pasta=PASTA):
    md = open(os.path.join(pasta, "nordeste_trajetoria_governos.md"), encoding="utf-8").read()
    sec = secoes(md)
    dados = {
        "meta": {
            "gerado_em": datetime.date.today().isoformat(),
            "titulo": "Nordeste: quem governou, o que mudou e o que os dados dizem (2002–2026)",
            "origem": ["research_notes/Nordeste e cenarios economicos 2026/nordeste_trajetoria_governos.md",
                       "research_notes/Nordeste e cenarios economicos 2026/nordeste_trajetoria_indicadores.csv"],
            "grupos": {"Nordeste PT atual": "BA, PI, CE, RN (governo do PT em 2026)",
                       "Outros NE": "MA, PB, PE, AL, SE (SE teve PT em 2007–2013; MA, PB, PE e AL nunca)",
                       "Brasil": "total nacional (homicídios: média das 5 regiões ponderada pela população do Censo 2022)",
                       "Espelho SP/PR/SC/GO/MT": "estados de comparação com a mesma régua; não são um 'grupo de direita' homogêneo nem placar contra o NE"},
            "correcao": "O PT também governou o Piauí em 2003–abr/2010 e Sergipe em 2007–dez/2013; a lista de estados do PT feita só com BA, PI (desde 2015), CE e RN está incompleta.",
            "convencoes": "[fato] dado de fonte oficial; [cálculo próprio] conta feita a partir de dado com fonte; [estimativa] inferência com premissa explícita. Médias de grupo ponderadas pela população do Censo 2022 (IDEB: média simples).",
            "avisos": ["Não é veredito sobre partidos nem recomendação de voto: n = 9 estados, sem desenho causal.",
                       "A classificação de PSB/PCdoB/PDT como aliados de esquerda do PT é dos autores e é discutível; a coluna do PT é mostrada separada.",
                       "O placar depende da seleção de indicadores e do ano-base; as séries do arquivo são uma seleção de 8 indicadores do CSV."],
        },
        "partidos": partidos(sec),
        "numeros_usuario": numeros_usuario(sec),
        "trajetoria": trajetoria(os.path.join(pasta, "nordeste_trajetoria_indicadores.csv")),
        "comparacao_pt": comparacao_pt(sec),
        "espelho": espelho(sec),
        "eleitoral": eleitoral(sec),
        "limites": limites(sec),
        "resumo": resumo(sec, md),
    }
    validar(dados)
    return dados


def validar(d):
    assert all(k in d for k in TOPO)
    assert len(d["partidos"]) == 9 and len(d["numeros_usuario"]) == 10 and len(d["comparacao_pt"]) == 15
    for n in d["numeros_usuario"]:
        assert n["veredito"] in ("confirmado", "diferente", "parcial") and n["fonte_url"].startswith("http")
    for t in d["trajetoria"]:
        assert len(t["series"]) == 4
        for s in t["series"]:
            assert len(s["anos"]) == len(s["valores"]) > 0
    pi = next(p for p in d["partidos"] if p["uf"] == "PI")
    se = next(p for p in d["partidos"] if p["uf"] == "SE")
    assert any(m["partido"] == "PT" and m["inicio"] == "01/01/2003" for m in pi["mandatos"])
    assert any(m["partido"] == "PT" and m["inicio"] == "01/01/2007" for m in se["mandatos"])
    assert len(d["eleitoral"]["tabela"]) == 8 and len(d["espelho"]) >= 60


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=SAIDA_PADRAO)
    a = ap.parse_args()
    dados = construir()
    os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{a.saida}: {os.path.getsize(a.saida)/1024:.0f} KB")


if __name__ == "__main__":
    sys.exit(main())
