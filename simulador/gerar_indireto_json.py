#!/usr/bin/env python3
"""Gera simulador/web/indireto.json a partir de research_notes/Indireto 2026.

Uso (re-executavel, so biblioteca padrao):
    python simulador/gerar_indireto_json.py
    python simulador/gerar_indireto_json.py --saida x.json

Entradas: indireto_lula.csv, indireto_flavio.csv (';'), simetria_depois.md e
auditoria_simetria.py (regra dos 10 mais fortes / 5 mais fracos, importada sem copiar).
Nao inventa nem altera fatos: campo vazio no CSV fica vazio no JSON.
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.path.join(RAIZ, "research_notes", "Indireto 2026")
SAIDA_PADRAO = os.path.join(AQUI, "web", "indireto.json")

LADOS = {"lula": "indireto_lula.csv", "flavio": "indireto_flavio.csv"}
NOMES_LADO = {"lula": "Lula/PT", "flavio": "Flávio/Bolsonaro"}
STATUS_OK = ("indireto", "não indireto", "retirado")
CAMPOS_CASO = ["id", "lado", "categoria", "periodo", "ator", "data", "fala_ou_ato",
               "comportamento_revelado", "leituras_por_publico", "negacao_plausivel",
               "quem_perderia_se_dito_direto", "contra_evidencia", "fonte_url",
               "confianca_fato", "forca_leitura", "status", "a_favor_do_ator", "disputado", "tag"]
TOPO = ["meta", "como_ler", "categorias", "casos", "contagens", "top_fortes", "top_fracos",
        "simetria", "resumos"]
TAG_OK = re.compile(r"^\[(fato|leitura|narrativa de [^\[\]]+)\]( \+ \[(fato|leitura|narrativa de [^\[\]]+)\])*$")

CATEGORIAS = [
    (1, "Porta-vozes", "O ator não diz, mas ministros, partido, aliados, influenciadores, 'fontes em off' ou anúncios pagos dizem. Avalia-se o ecossistema, não só a boca do candidato."),
    (2, "Atos sem palavras", "Nomeações, decretos, vetos, emendas e verbas: quem recebe dinheiro ou cargo e quando. O ato como evidência de comportamento, para comparar com o discurso."),
    (3, "Timing", "Quando a informação ou a medida aparece: dado ruim em dia de baixa atenção, benefício antes da eleição e conta depois, medidas que vencem entre os turnos."),
    (4, "Escolha do número", "Ano-base, média ou mediana, nominal ou real, métrica trocada quando a antiga piora. O dado pode ser verdadeiro e o enquadramento mudar a conclusão."),
    (5, "Palavras com dono", "Termos-senha ('democracia', 'instituições', 'liberdade', 'família', 'fome') que sinalizam lado sem afirmar nada verificável."),
    (6, "Mensagens diferentes por público", "O que se diz a cada plateia (comício, mercado, imprensa estrangeira, igreja) quando as versões não coincidem."),
    (7, "Imagens, símbolos e memes", "Imagem, símbolo, gesto, cor, música ou a data de uma postagem usados como recado, sem frase que possa ser citada."),
    (8, "Reescrita posterior", "Fala original guardada com data comparada com a explicação dada depois ('não foi isso que eu quis dizer')."),
    (9, "Silêncios", "Assuntos de que o ator não fala ou de que nunca fala mal, quando o contexto indica que falar teria custo ou benefício."),
    (10, "Aliados e proteção", "Com quem o ator se alia e quem defende ou deixa de criticar; o comportamento diante de aliados investigados, condenados ou beneficiados."),
    (11, "Linguagem de ameaça e combate", "Frases de confronto, ameaça ou guerra, e se foram eleitorais (contra um grupo político) ou dirigidas a pessoas."),
    (12, "Narrativa de vítima ou inimigo", "Enquadramentos em que o ator ou o grupo aparece perseguido, ou um adversário aparece como inimigo, e o que a narrativa explica ou deixa de explicar."),
]

REGRA_TEXTO = ("Mesma régua para os dois lados: o ator é avaliado pelo que faz, defende, protege, financia, cala e "
               "com quem se alia, não só pelo que declara. O rótulo 'indireto' é uma hipótese em teste, não um veredito: "
               "cada caso traz a leitura inocente mais forte (coluna contra_evidencia).")

AVISOS = [
    "Este é um mapa de comportamento e de leituras possíveis, não um veredito sobre pessoas e não é recomendação de voto.",
    "As contagens dependem da seleção: os casos foram escolhidos por quem pesquisou, e a escolha, a ordem e a omissão de temas são, elas próprias, enquadramento. O número de casos de um lado não mede quem 'fala mais indireto'.",
    "A classificação dos veículos (esquerda, centro, direita, oficial, checador) e a rubrica de força da leitura são juízos dos autores, aplicados por um modelo de IA que não consegue auditar o próprio treinamento; podem ser contestados caso a caso pelas colunas do CSV.",
    "Itens não verificados ou com fonte única estão marcados: confianca_fato 'média' ou 'baixa', força da leitura limitada a 'fraca' quando a fonte não passa a barra de evidência, 'disputado' quando as fontes não resolvem o fato.",
    "Casos com status 'retirado' ficam no arquivo para transparência (evidência insuficiente ou fundidos em outro caso) e não entram nas contagens por categoria e período nem nos rankings.",
]


def carregar_auditoria():
    caminho = os.path.join(PASTA, "auditoria_simetria.py")
    spec = importlib.util.spec_from_file_location("auditoria_simetria", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sim_nao(v):
    return (v or "").strip().lower() == "sim"


def primeira_url(txt):
    for u in re.split(r"\s*\|\s*|\s+(?=https?://)", (txt or "").strip()):
        if u.strip().startswith("http"):
            return u.strip()
    return (txt or "").strip()


def cat_id(txt):
    m = re.match(r"\s*(\d+)", txt or "")
    return int(m.group(1)) if m else 0


def caso_de_linha(lado, r):
    af = (r.get("a_favor_do_ator") or "").strip()
    return {
        "id": r["id"], "lado": lado, "categoria": cat_id(r["categoria"]), "periodo": r["periodo"],
        "ator": r["ator"], "data": r["data"], "fala_ou_ato": r["fala_ou_ato_literal"],
        "comportamento_revelado": r["comportamento_revelado"],
        "leituras_por_publico": r["leituras_por_publico"], "negacao_plausivel": r["negacao_plausivel"],
        "quem_perderia_se_dito_direto": r["quem_perderia_se_dito_direto"],
        "contra_evidencia": r["contra_evidencia_ou_leitura_alternativa"],
        "fonte_url": primeira_url(r["fonte_url"]), "confianca_fato": r["confianca_fato"],
        "forca_leitura": r["forca_leitura_indireta"], "status": r["status"],
        # 'sim' e 'misto' (fato nos dois sentidos) contam como favoráveis, como na auditoria de simetria
        "a_favor_do_ator": af in ("sim", "misto"),
        "disputado": sim_nao(r.get("disputado")), "tag": r["tag"],
    }


def tabelas_md(texto):
    """Extrai tabelas markdown com o ultimo titulo/paragrafo antes de cada uma."""
    out, titulo, atual = [], "", None
    for ln in texto.splitlines():
        s = ln.strip()
        if s.startswith("|"):
            cels = [c.strip() for c in s.strip("|").split("|")]
            if atual is None:
                atual = {"titulo": re.sub(r"[*#`]", "", titulo).strip(": "), "colunas": cels, "linhas": []}
            elif all(re.fullmatch(r":?-{2,}:?", c) or c == "---" for c in cels):
                continue
            else:
                atual["linhas"].append(cels)
        else:
            if atual is not None:
                out.append(atual)
                atual = None
            if s:
                titulo = s
    if atual is not None:
        out.append(atual)
    return out


def limpa(t):
    return re.sub(r"\*\*|`", "", t).strip()


def simetria_de_md():
    texto = open(os.path.join(PASTA, "simetria_depois.md"), encoding="utf-8").read()
    corpo = texto.split("## Interpretação", 1)[1].split("## Saída do script", 1)[0]
    itens = [limpa(m) for m in re.findall(r"^\d+\.\s+(.*)$", corpo, flags=re.M)]
    restantes = [i for i in itens if i.lower().startswith("assimetria que resta")]
    reconhecidas = [i for i in itens if i.lower().startswith(("o que ficou simétrico", "viés da própria revisão"))]
    tabs = tabelas_md(texto)
    return {
        "texto": "Resultado de auditoria_simetria.py (lê os dois CSVs) e interpretação, com as assimetrias que restam. " + " ".join(itens),
        "o_que_ficou_simetrico": [i for i in itens if i.lower().startswith("o que ficou simétrico")],
        "assimetrias_restantes": restantes,
        "vies_da_revisao": [i for i in itens if i.lower().startswith("viés da própria revisão")],
        "tabela": tabs,
    }, tabs, bool(restantes), bool(reconhecidas)


def contagens_de(casos):
    ativos = [c for c in casos if c["status"] != "retirado"]
    por_lado = {}
    for l in LADOS:
        cl = [c for c in casos if c["lado"] == l]
        por_lado[l] = {"total": len(cl), "ativos": sum(1 for c in cl if c["status"] != "retirado"),
                       "indireto": sum(1 for c in cl if c["status"] == "indireto"),
                       "nao_indireto": sum(1 for c in cl if c["status"] == "não indireto"),
                       "retirado": sum(1 for c in cl if c["status"] == "retirado")}
    por_cat = {str(i): {l: sum(1 for c in ativos if c["lado"] == l and c["categoria"] == i) for l in LADOS}
               for i, _, _ in CATEGORIAS}
    periodos = sorted({c["periodo"] for c in casos})
    por_per = {p: {l: sum(1 for c in ativos if c["lado"] == l and c["periodo"] == p) for l in LADOS} for p in periodos}
    por_status = {s: {l: sum(1 for c in casos if c["lado"] == l and c["status"] == s) for l in LADOS} for s in STATUS_OK}
    return {"por_lado": por_lado, "por_categoria_lado": por_cat, "por_periodo": por_per, "por_status": por_status,
            "nota": "Contagens por categoria e por período usam só casos ativos (status 'indireto' ou 'não indireto'); "
                    "por_status e por_lado contam todas as linhas, inclusive as retiradas."}


def resumos_de(casos, cont, topf, topfr, assim):
    pl, pf = cont["por_lado"]["lula"], cont["por_lado"]["flavio"]
    ativos = [c for c in casos if c["status"] != "retirado"]

    def dist(l, campo):
        c = Counter(x[campo] for x in ativos if x["lado"] == l)
        return c
    fl, ff = dist("lula", "forca_leitura"), dist("flavio", "forca_leitura")
    cl, cf = dist("lula", "confianca_fato"), dist("flavio", "confianca_fato")
    fav = {l: sum(1 for c in ativos if c["lado"] == l and c["a_favor_do_ator"]) for l in LADOS}
    cats = cont["por_categoria_lado"]
    maiores = sorted(cats.items(), key=lambda kv: -(kv[1]["lula"] + kv[1]["flavio"]))[:3]
    nomes_cat = {str(i): n for i, n, _ in CATEGORIAS}
    per = cont["por_periodo"]
    R = []
    R.append({"secao": "Visão geral", "pontos": [
        f"{pl['total'] + pf['total']} linhas nos dois mapas: {pl['total']} de Lula/PT e {pf['total']} de Flávio/Bolsonaro.",
        f"Casos ativos: {pl['ativos']} de Lula/PT ({pl['indireto']} indireto, {pl['nao_indireto']} não indireto) e {pf['ativos']} de Flávio/Bolsonaro ({pf['indireto']} indireto, {pf['nao_indireto']} não indireto).",
        f"Retirados e mantidos no arquivo: {pl['retirado']} de Lula/PT e {pf['retirado']} de Flávio/Bolsonaro.",
        "As contagens dependem da seleção dos casos; não medem quem fala mais indireto."]})
    R.append({"secao": "Lula, PT e governo", "pontos": [
        f"{pl['ativos']} casos ativos; confiança no fato: {cl['alta']} alta, {cl['média']} média, {cl['baixa']} baixa.",
        f"Força da leitura indireta: {fl['forte']} forte, {fl['média']} média, {fl['fraca']} fraca, {fl['não conclusivo']} não conclusivo.",
        f"Casos favoráveis ao ator (agiu direto e pagando custo, ou fato nos dois sentidos): {fav['lula']} de {pl['ativos']}.",
        f"Disputados: {sum(1 for c in ativos if c['lado'] == 'lula' and c['disputado'])}."]})
    R.append({"secao": "Flávio, Bolsonaro e aliados", "pontos": [
        f"{pf['ativos']} casos ativos; confiança no fato: {cf['alta']} alta, {cf['média']} média, {cf['baixa']} baixa.",
        f"Força da leitura indireta: {ff['forte']} forte, {ff['média']} média, {ff['fraca']} fraca, {ff['não conclusivo']} não conclusivo.",
        f"Casos favoráveis ao ator: {fav['flavio']} de {pf['ativos']}.",
        f"Disputados: {sum(1 for c in ativos if c['lado'] == 'flavio' and c['disputado'])}."]})
    R.append({"secao": "Por categoria", "pontos": [
        "Mais casos ativos: " + "; ".join(f"{nomes_cat[k]} ({v['lula']} Lula/PT, {v['flavio']} Flávio/Bolsonaro)" for k, v in maiores) + ".",
        f"Imagens, símbolos e memes: {cats['7']['lula']} de Lula/PT e {cats['7']['flavio']} de Flávio/Bolsonaro.",
        f"Mensagens diferentes por público: {cats['6']['lula']} de Lula/PT e {cats['6']['flavio']} de Flávio/Bolsonaro.",
        "A escolha das 12 categorias e a omissão de temas são, elas próprias, seleção."]})
    pl_per = "; ".join(f"{p} ({v['lula']})" for p, v in per.items() if v["lula"])
    pf_per = "; ".join(f"{p} ({v['flavio']})" for p, v in per.items() if v["flavio"])
    R.append({"secao": "Por período", "pontos": [
        f"Casos ativos de Lula/PT por período: {pl_per}.",
        f"Casos ativos de Flávio/Bolsonaro por período: {pf_per}.",
        "O recorte comparável é 2023-26 (governo Lula contra oposição); o histórico tem tamanhos diferentes nos dois lados."]})
    R.append({"secao": "Mais fortes e mais fracos", "pontos": [
        f"Mais fortes pela mesma regra: {len(topf['lula'])} de Lula/PT e {len(topf['flavio'])} de Flávio/Bolsonaro (Lula/PT tem menos casos elegíveis, não um corte diferente).",
        f"Mais fracos pela mesma regra: {len(topfr['lula'])} de cada lado.",
        "Regra: status 'indireto', fonte que passa a barra de evidência, não disputado e força forte ou média; ordem por força, confiança, número de veículos e classes, desempate por SHA-1 do id."]})
    R.append({"secao": "Simetria e limites", "pontos": [
        f"Assimetrias que restam declaradas: {len(assim)} (força da leitura, escopo histórico, fontes, redação).",
        f"Mesmo vocabulário de tags, mesmas colunas, mesma barra de evidência e {pl['retirado']} e {pf['retirado']} linhas retiradas.",
        "A revisão foi feita por um modelo de IA, sem auditoria independente da rubrica de força e da classificação dos veículos."]})
    R.append({"secao": "Resumo da aba", "pontos": [
        f"{pl['ativos']} casos ativos de Lula/PT e {pf['ativos']} de Flávio/Bolsonaro, com a mesma régua, as mesmas colunas e a mesma barra de evidência.",
        f"Leitura 'forte': {fl['forte']} caso de Lula/PT e {ff['forte']} de Flávio/Bolsonaro; 'não conclusivo': {fl['não conclusivo']} e {ff['não conclusivo']}.",
        "É um mapa de comportamento e de leituras, não um veredito nem recomendação de voto; a seleção e a rubrica são juízos dos autores.",
        "Assimetrias restantes (força, escopo histórico, fontes, redação) estão declaradas na seção de simetria."]})
    return R


def construir(pasta=PASTA):
    aud = carregar_auditoria()
    linhas = {l: aud.ler_csv(os.path.join(pasta, f)) for l, f in LADOS.items()}
    casos = [caso_de_linha(l, r) for l in LADOS for r in linhas[l]]
    cont = contagens_de(casos)
    topf = {l: [r["id"] for r in aud.ranking_fortes(linhas[l])] for l in LADOS}
    topfr = {l: [r["id"] for r in aud.ranking_fracos(linhas[l])] for l in LADOS}
    sim, _tabs, tem_assim, _ = simetria_de_md()
    elegiveis = {l: sum(1 for r in linhas[l] if r["status"] == "indireto" and aud.passa_barra(r)
                        and r.get("disputado", "não") != "sim" and r["forca_leitura_indireta"] in ("forte", "média"))
                 for l in LADOS}
    sim["atualizacao"] = (
        "As tabelas e o texto vêm de simetria_depois.md (gerado em 2026-10-05). O recálculo do script sobre os CSVs "
        f"atuais dá {elegiveis['lula']} casos elegíveis para os mais fortes de Lula/PT e {elegiveis['flavio']} de "
        "Flávio/Bolsonaro; o md registra 9 e 17. Onde o texto do md disser que o top de Lula tem 9 casos, vale o "
        "recálculo (top_fortes e top_fracos deste arquivo usam o script atual).")
    sim["elegiveis_top_fortes_recalculo"] = elegiveis
    escopo = {l: [{"periodo": p, "ativos": sum(1 for c in casos if c["lado"] == l and c["periodo"] == p and c["status"] != "retirado"),
                   "total": sum(1 for c in casos if c["lado"] == l and c["periodo"] == p)}
                  for p in sorted({c["periodo"] for c in casos if c["lado"] == l})] for l in LADOS}
    como_ler = [
        {"titulo": "O que é", "texto": "Um mapa de comportamento revelado: o que cada ator faz, defende, protege, cala e com quem se alia, ao lado do que diz. Método, não conclusão: o rótulo 'indireto' é hipótese em teste."},
        {"titulo": "Duas colunas separadas", "texto": "confianca_fato mede o quanto se tem certeza de que o fato ocorreu (alta = fonte primária ou duas independentes; média = uma fonte confiável; baixa = resumo de busca, blog ou página não aberta). forca_leitura mede o quanto a leitura 'o comportamento revela o que a fala não diz' se sustenta depois da contra-evidência: forte, média, fraca ou não conclusivo."},
        {"titulo": "Rubrica da força (igual nos dois lados)", "texto": "forte = ato ou documento verificado que contradiz a fala ou protege o ator, sem contra-evidência com número e fonte que o explique; média = ato verificado com contra-evidência parcial; fraca = a contra-evidência explica o ato sem a leitura indireta, ou a fala é explícita, ou a fonte única limita a leitura; não conclusivo = falta dado ou as duas leituras têm apoio parecido. É um juízo dos autores."},
        {"titulo": "Status", "texto": "indireto = a acusação de indireto está em teste; não indireto = fala ou ato explícito, mantido como controle; retirado = evidência insuficiente, fonte única de campo, fora do escopo ou duplicata (fica no arquivo e a interface o oculta por padrão)."},
        {"titulo": "Barra de evidência", "texto": "Fonte primária ou oficial, OU checador com método publicado, OU dois ou mais veículos distintos. Quem não passa tem a força limitada a 'fraca' e não entra nos mais fortes."},
        {"titulo": "Negação plausível e tag", "texto": "negacao_plausivel indica se havia saída do tipo 'não foi isso que eu quis dizer'. A tag é só [fato], [leitura] ou [narrativa de X]; nenhum rótulo de conclusão."},
        {"titulo": "Favorável ao ator e disputado", "texto": "a_favor_do_ator marca casos em que o ator agiu direto e pagando custo, ou há fato nos dois sentidos (no CSV 'misto' também vira verdadeiro aqui). disputado marca fato que as fontes não resolveram, com as duas leituras na contra-evidência."},
        {"titulo": "fonte_url", "texto": "Quando o caso tem várias fontes, o arquivo traz a primeira; as demais estão nos CSVs de origem."},
    ]
    dados = {
        "meta": {
            "gerado_em": datetime.date.today().isoformat(),
            "origem": ["research_notes/Indireto 2026/indireto_lula.csv", "research_notes/Indireto 2026/indireto_flavio.csv",
                       "research_notes/Indireto 2026/simetria_depois.md", "research_notes/Indireto 2026/auditoria_simetria.py"],
            "escopo": escopo,
            "regra": REGRA_TEXTO,
            "regra_top_fortes": aud.RULE_FORTES,
            "regra_top_fracos": aud.RULE_FRACOS,
            "avisos": AVISOS,
        },
        "como_ler": como_ler,
        "categorias": [{"id": i, "nome": n, "descricao": d} for i, n, d in CATEGORIAS],
        "casos": casos,
        "contagens": cont,
        "top_fortes": topf,
        "top_fracos": topfr,
        "simetria": sim,
        "resumos": resumos_de(casos, cont, topf, topfr, sim["assimetrias_restantes"]),
    }
    validar(dados)
    return dados


def validar(d):
    """Levanta AssertionError se o JSON for inconsistente."""
    assert all(k in d for k in TOPO), "chave de topo ausente"
    ids = [c["id"] for c in d["casos"]]
    assert len(ids) == len(set(ids)), "ids duplicados"
    for c in d["casos"]:
        assert list(c.keys()) == CAMPOS_CASO or set(c) == set(CAMPOS_CASO), f"campos de {c['id']}"
        assert c["lado"] in LADOS and c["status"] in STATUS_OK
        assert isinstance(c["a_favor_do_ator"], bool) and isinstance(c["disputado"], bool)
        assert isinstance(c["categoria"], int) and 1 <= c["categoria"] <= 12
        assert TAG_OK.match(c["tag"].strip()), f"tag fora do vocabulario em {c['id']}"
    por_id = {c["id"]: c for c in d["casos"]}
    for chave in ("top_fortes", "top_fracos"):
        for l, lst in d[chave].items():
            for i in lst:
                assert i in por_id and por_id[i]["lado"] == l, f"{chave}: {i}"
                assert por_id[i]["status"] == "indireto"
    ct = d["contagens"]
    for l in LADOS:
        cl = [c for c in d["casos"] if c["lado"] == l]
        assert ct["por_lado"][l]["total"] == len(cl)
        assert ct["por_lado"][l]["ativos"] == sum(1 for c in cl if c["status"] != "retirado")
        for s in STATUS_OK:
            assert ct["por_status"][s][l] == sum(1 for c in cl if c["status"] == s)
        for k, v in ct["por_categoria_lado"].items():
            assert v[l] == sum(1 for c in cl if c["status"] != "retirado" and c["categoria"] == int(k))
        for p, v in ct["por_periodo"].items():
            assert v[l] == sum(1 for c in cl if c["status"] != "retirado" and c["periodo"] == p)
    assert len(d["categorias"]) == 12
    assert d["resumos"][-1]["secao"] == "Resumo da aba"
    assert all(3 <= len(r["pontos"]) <= 5 for r in d["resumos"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=SAIDA_PADRAO)
    a = ap.parse_args()
    dados = construir()
    os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
        f.write("\n")
    n = {l: dados["contagens"]["por_lado"][l] for l in LADOS}
    print(f"{a.saida}: {os.path.getsize(a.saida)/1024:.0f} KB; " + "; ".join(f"{NOMES_LADO[l]} {v}" for l, v in n.items()))


if __name__ == "__main__":
    sys.exit(main())
