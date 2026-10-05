#!/usr/bin/env python3
"""Auditoria de simetria entre os dois mapas do indireto (Lula/PT x Flavio/Bolsonaro).

Uso:
    python auditoria_simetria.py                 # imprime o relatorio em markdown
    python auditoria_simetria.py --saida x.md    # grava em arquivo
    python auditoria_simetria.py --lula a.csv --flavio b.csv

Le os dois CSVs (mesmo esquema; delimitador ';' ou ',') e imprime:
  1. casos por categoria e por lado
  2. casos por periodo
  3. vocabulario de tags (e violacoes: so [fato] / [leitura] / [narrativa de X])
  4. distribuicao de confianca_fato e forca_leitura_indireta
  5. casos com 1 fonte x 2+ (e quantos passam a "barra de evidencia")
  6. mistura de veiculos (esquerda/centro/direita/oficial/checador) pela tabela
     SOURCE_CLASS abaixo (editavel; dominios sem classe sao listados)
  7. estatisticas de redacao (hedges e adjetivos por 1000 palavras)
  8. os 10 mais fortes e os 5 mais fracos de cada mapa pela MESMA regra (RULE_*)

O modulo tambem exporta funcoes usadas para gerar os mapas (ranking_fortes, ranking_fracos).
So usa a biblioteca padrao.
"""
import argparse
import csv
import hashlib
import io
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Tabela de classificacao dos veiculos (por dominio). Classificacao aproximada,
# usada pelas revisoes adversariais; editar aqui muda o relatorio.
# Classes: esquerda, centro, direita, oficial, checador
# ---------------------------------------------------------------------------
SOURCE_CLASS = {
    # esquerda / campo governista / independente de esquerda
    "brasil247.com": "esquerda", "revistaforum.com.br": "esquerda",
    "brasildefato.com.br": "esquerda", "vermelho.org.br": "esquerda",
    "fpabramo.org.br": "esquerda", "cut.org.br": "esquerda",
    "diariodocentrodomundo.com.br": "esquerda", "iclnoticias.com.br": "esquerda",
    "plantaobrasil.net": "esquerda", "intercept.com.br": "esquerda",
    "apublica.org": "esquerda", "cartacapital.com.br": "esquerda",
    "terrabrasilnoticias.com": "esquerda",
    # direita / campo oposicionista
    "gazetadopovo.com.br": "direita", "jovempan.com.br": "direita",
    "revistaoeste.com": "direita", "oantagonista.com.br": "direita",
    "contrafatos.com.br": "direita", "brasilemfolhas.com.br": "direita",
    "revistaexilio.substack.com": "direita", "gospelmais.com": "direita",
    "diariodopoder.com.br": "direita", "gazetabrasil.com.br": "direita",
    # oficial / primaria
    "gov.br": "oficial", "agenciabrasil.ebc.com.br": "oficial",
    "agenciagov.ebc.com.br": "oficial", "senado.leg.br": "oficial",
    "camara.leg.br": "oficial", "stf.jus.br": "oficial", "tse.jus.br": "oficial",
    "planalto.gov.br": "oficial", "ustr.gov": "oficial", "noticias.stf.jus.br": "oficial",
    "portal.stf.jus.br": "oficial",
    # checadores
    "aosfatos.org": "checador", "agencialupa.org": "checador", "ranking.org.br": "checador",
    # imprensa geral / centro / especializada
    "cnnbrasil.com.br": "centro", "metropoles.com": "centro", "otempo.com.br": "centro",
    "em.com.br": "centro", "infomoney.com.br": "centro", "poder360.com.br": "centro",
    "jornaldebrasilia.com.br": "centro", "correiobraziliense.com.br": "centro",
    "terra.com.br": "centro", "jb.com.br": "centro", "bloomberg.com": "centro",
    "aljazeera.com": "centro", "cnbc.com": "centro", "sbtnews.sbt.com.br": "centro",
    "ndmais.com.br": "centro", "migalhas.com.br": "centro", "conjur.com.br": "centro",
    "exame.com": "centro", "spacemoney.com.br": "centro", "tribunadosertao.com.br": "centro",
    "congressoemfoco.com.br": "centro", "itatiaia.com.br": "centro",
    "mixvale.com.br": "centro", "dnoticias.pt": "centro", "tmc.com.br": "centro",
    "maisretorno.com": "centro", "agazeta.com.br": "centro", "ofolhademinas.com.br": "centro",
    "tvtnews.com.br": "centro", "movimentoeconomico.com.br": "centro",
    "diariodocomercio.com.br": "centro", "campograndenews.com.br": "centro",
    "jornalopcao.com.br": "centro", "riotimesonline.com": "centro",
    "ncnews.com.br": "centro", "publico.pt": "centro", "jusbrasil.com.br": "centro",
    "jornaldanova.com.br": "centro", "moneytimes.com.br": "centro",
    "1news.correiobraziliense.com.br": "centro", "painelpolitico.com": "centro",
    "tagteam.harvard.edu": "centro", "timesbrasil.com.br": "centro",
    "obrasilianista.com.br": "centro", "istoedinheiro.com.br": "centro",
    "comunidadecontabilbrasil.com": "centro", "dn.pt": "centro",
    "ranking.org.br ": "checador",
}
PRIMARIAS = {"oficial"}          # fonte primaria/oficial passa a barra sozinha
CHECADOR_PASSA = True            # um checador com metodo publicado passa a barra

# ---------------------------------------------------------------------------
# Regras de ranking (identicas para os dois mapas)
# ---------------------------------------------------------------------------
FORCA_ORD = {"forte": 3, "média": 2, "fraca": 1, "não conclusivo": 0}
CONF_ORD = {"alta": 3, "média": 2, "baixa": 1}
RULE_FORTES = (
    "10 mais fortes = casos com status 'indireto' (a leitura indireta e o que esta em teste), que "
    "passam a barra de evidencia (fonte primaria/oficial, OU checador com metodo publicado, OU 2+ "
    "veiculos distintos), que NAO estao marcados 'disputado' e cuja forca_leitura_indireta e "
    "'forte' ou 'media'. Ordem: forca_leitura_indireta, depois confianca_fato, depois numero de "
    "veiculos distintos, depois numero de classes de veiculo diferentes; empate final pelo "
    "SHA-1 do id (arbitrario, sem relacao com lado, data ou tema). Casos favoraveis ao ator, "
    "'nao indireto' e retirados nao entram."
)
RULE_FRACOS = (
    "5 mais fracos = casos com status 'indireto' (a acusacao de indireto que menos se sustenta). "
    "Ordem crescente: forca_leitura_indireta (nao conclusivo < fraca), depois confianca_fato "
    "(baixa < media < alta), depois numero de veiculos distintos (menos primeiro), depois SHA-1 do "
    "id. Casos 'nao indireto' (controles explicitos) e retirados ficam em listas proprias."
)

HEDGES = ["pode", "podem", "possível", "possivelmente", "talvez", "supostamente", "alegadamente",
          "teria", "poderia", "aparentemente", "sugere", "indica", "segundo", "não verificado",
          "não conclusivo", "sem prova", "não está provad", "não foi achad", "a confirmar",
          "ao que parece", "em tese", "se confirmado"]
ADJETIVOS = ["enganoso", "enganosa", "tenebroso", "tenebrosa", "grave", "gravíssimo", "absurdo",
             "histórico", "inaceitável", "escandaloso", "vergonhoso", "forte", "duro", "dura",
             "pesado", "pesada", "ótimo", "péssimo", "claro", "claramente", "evidente",
             "óbvio", "flagrante", "robusto", "frágil", "fraco", "fraca", "infeliz", "raro",
             "rara", "perigoso", "extremamente", "muito", "enorme", "brutal"]

TAG_OK = re.compile(r"^\[(fato|leitura|narrativa de [^\[\]]+)\]( \+ \[(fato|leitura|narrativa de [^\[\]]+)\])*$")


def ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        texto = f.read()
    delim = ";" if texto.split("\n", 1)[0].count(";") > texto.split("\n", 1)[0].count(",") else ","
    return list(csv.DictReader(io.StringIO(texto), delimiter=delim))


def dominio(url):
    h = urlparse(url.strip()).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def classe_dominio(d):
    if d in SOURCE_CLASS:
        return SOURCE_CLASS[d]
    for chave, cl in SOURCE_CLASS.items():
        if d.endswith("." + chave) or d.endswith(chave) and "." in chave:
            return cl
    return None


def urls_do_caso(r):
    return [u.strip() for u in re.split(r"\s*(?:\||;\s+(?=http))\s*", r.get("fonte_url", "")) if u.strip().startswith("http")]


def info_fontes(r):
    doms = []
    for u in urls_do_caso(r):
        d = dominio(u)
        if d not in doms:
            doms.append(d)
    classes = [classe_dominio(d) for d in doms]
    return doms, classes


def passa_barra(r):
    doms, classes = info_fontes(r)
    if any(c in PRIMARIAS for c in classes):
        return True
    if CHECADOR_PASSA and any(c == "checador" for c in classes):
        return True
    return len(doms) >= 2


def sha(r):
    return hashlib.sha1(r["id"].encode()).hexdigest()


def ano(r):
    m = re.search(r"(19|20)\d\d", r.get("data", ""))
    return int(m.group(0)) if m else 0


def _chave_forte(r):
    doms, classes = info_fontes(r)
    return (-FORCA_ORD.get(r["forca_leitura_indireta"], 0), -CONF_ORD.get(r["confianca_fato"], 0),
            -len(doms), -len({c for c in classes if c}), sha(r))


def ranking_fortes(rows, n=10):
    el = [r for r in rows if r["status"] == "indireto" and passa_barra(r)
          and r.get("disputado", "não") != "sim"
          and r["forca_leitura_indireta"] in ("forte", "média")]
    return sorted(el, key=_chave_forte)[:n]


def ranking_fracos(rows, n=5):
    el = [r for r in rows if r["status"] == "indireto"]
    def k(r):
        doms, _ = info_fontes(r)
        return (FORCA_ORD.get(r["forca_leitura_indireta"], 0), CONF_ORD.get(r["confianca_fato"], 0), len(doms), sha(r))
    return sorted(el, key=k)[:n]


def tabela(cab, linhas):
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] * len(cab)) + "|"]
    for l in linhas:
        out.append("| " + " | ".join(str(x) for x in l) + " |")
    return "\n".join(out)


def palavras(txt):
    return re.findall(r"[\wÀ-ÿ'-]+", txt.lower())


def contar_termos(txt, termos):
    t = txt.lower()
    return sum(len(re.findall(r"\b" + re.escape(x.lower()), t)) for x in termos)


def relatorio(lados):
    """lados: {'Lula/PT': rows, 'Flávio/Bolsonaro': rows}"""
    nomes = list(lados)
    out = []
    P = out.append
    P("# Auditoria de simetria (gerada por auditoria_simetria.py)\n")
    P(f"Lados: {', '.join(nomes)}. Contagens sobre TODAS as linhas do CSV (inclui status retirado) onde indicado; "
      "a maioria das tabelas usa so os casos ativos (status 'indireto' ou 'não indireto').\n")

    # 0 status
    P("## 0. Linhas por status\n")
    sts = ["indireto", "não indireto", "retirado"]
    P(tabela(["status"] + nomes + ["total"], [[s] + [sum(1 for r in lados[n] if r["status"] == s) for n in nomes] +
                                              [sum(1 for n in nomes for r in lados[n] if r["status"] == s)] for s in sts] +
                                             [["TOTAL de linhas"] + [len(lados[n]) for n in nomes] + [sum(len(lados[n]) for n in nomes)]]))
    ativos = {n: [r for r in lados[n] if r["status"] != "retirado"] for n in nomes}
    P("")
    P("Casos favoraveis ao ator (a_favor_do_ator sim/misto), entre os ativos: " +
      "; ".join(f"{n}: {sum(1 for r in ativos[n] if r['a_favor_do_ator'] == 'sim')} sim + {sum(1 for r in ativos[n] if r['a_favor_do_ator'] == 'misto')} misto" for n in nomes))
    P("Casos marcados 'disputado': " + "; ".join(f"{n}: {sum(1 for r in ativos[n] if r['disputado'] == 'sim')}" for n in nomes) + "\n")

    # 1 categoria
    P("## 1. Casos ativos por categoria\n")
    cats = sorted({r["categoria"] for n in nomes for r in ativos[n]}, key=lambda c: int(c.split()[0]))
    P(tabela(["categoria"] + nomes, [[c] + [sum(1 for r in ativos[n] if r["categoria"] == c) for n in nomes] for c in cats] +
             [["TOTAL"] + [len(ativos[n]) for n in nomes]]))
    P("")

    # 2 periodo
    P("## 2. Casos ativos por periodo\n")
    pers = sorted({r["periodo"] for n in nomes for r in ativos[n]})
    P(tabela(["periodo"] + nomes, [[p] + [sum(1 for r in ativos[n] if r["periodo"] == p) for n in nomes] for p in pers]))
    P("")

    # 3 tags
    P("## 3. Vocabulario de tags (casos ativos)\n")
    for n in nomes:
        c = Counter()
        bad = []
        for r in ativos[n]:
            for t in re.findall(r"\[[^\]]+\]", r["tag"]):
                c["[narrativa de X]" if t.startswith("[narrativa de") else t] += 1
            if not TAG_OK.match(r["tag"].strip()):
                bad.append(r["id"])
        P(f"- {n}: {dict(c)}; violacoes do vocabulario: {bad if bad else 'nenhuma'}")
    P("")

    # 4 confianca e forca
    P("## 4. confianca_fato e forca_leitura_indireta (casos ativos)\n")
    for campo, ordem in (("confianca_fato", ["alta", "média", "baixa"]),
                         ("forca_leitura_indireta", ["forte", "média", "fraca", "não conclusivo"])):
        P(f"**{campo}**\n")
        P(tabela([campo] + [f"{n} (n)" for n in nomes] + [f"{n} (%)" for n in nomes],
                 [[v] + [sum(1 for r in ativos[n] if r[campo] == v) for n in nomes] +
                  [f"{100*sum(1 for r in ativos[n] if r[campo] == v)/max(1,len(ativos[n])):.0f}%" for n in nomes] for v in ordem]))
        P("")
    P("Cruzamento (alta confianca no fato x forca da leitura), so 'indireto':\n")
    P(tabela(["lado", "alta+forte", "alta+média", "alta+fraca", "alta+nc"],
             [[n] + [sum(1 for r in lados[n] if r["status"] == "indireto" and r["confianca_fato"] == "alta" and r["forca_leitura_indireta"] == f)
                     for f in ["forte", "média", "fraca", "não conclusivo"]] for n in nomes]))
    P("")

    # 5 fontes
    P("## 5. Numero de fontes (veiculos distintos) por caso ativo\n")
    linhas = []
    for n in nomes:
        c1 = sum(1 for r in ativos[n] if len(info_fontes(r)[0]) <= 1)
        c2 = len(ativos[n]) - c1
        pb = sum(1 for r in ativos[n] if passa_barra(r))
        prim = sum(1 for r in ativos[n] if any(c in PRIMARIAS for c in info_fontes(r)[1]))
        chk = sum(1 for r in ativos[n] if any(c == "checador" for c in info_fontes(r)[1]))
        linhas.append([n, c1, c2, prim, chk, pb, len(ativos[n]) - pb])
    P(tabela(["lado", "1 fonte", "2+ fontes", "com fonte oficial", "com checador", "passa a barra", "nao passa"], linhas))
    P("\nBarra de evidencia: fonte oficial/primaria, OU checador, OU 2+ veiculos distintos. "
      "Casos que nao passam tem forca limitada a 'fraca' e nao entram nos 10 mais fortes.\n")

    # 6 mix
    P("## 6. Mistura de veiculos (URLs distintas por dominio, casos ativos)\n")
    cls_ord = ["esquerda", "centro", "direita", "oficial", "checador", "(sem classe)"]
    cont = {n: Counter() for n in nomes}
    sem = Counter()
    tot = {n: 0 for n in nomes}
    for n in nomes:
        for r in ativos[n]:
            doms, classes = info_fontes(r)
            for d, c in zip(doms, classes):
                tot[n] += 1
                if c is None:
                    sem[d] += 1
                cont[n][c or "(sem classe)"] += 1
    P(tabela(["classe"] + [f"{n} (n)" for n in nomes] + [f"{n} (%)" for n in nomes],
             [[c] + [cont[n][c] for n in nomes] + [f"{100*cont[n][c]/max(1,tot[n]):.0f}%" for n in nomes] for c in cls_ord] +
             [["TOTAL de citacoes"] + [tot[n] for n in nomes] + [""] * len(nomes)]))
    if sem:
        P("\nDominios sem classe na tabela SOURCE_CLASS: " + ", ".join(sorted(sem)))
    P("")
    P("Principais dominios por lado:\n")
    for n in nomes:
        dd = Counter(d for r in ativos[n] for d in info_fontes(r)[0])
        P(f"- {n}: " + ", ".join(f"{d} ({k})" for d, k in dd.most_common(8)))
    P("")

    # 7 redacao
    P("## 7. Redacao (campos comportamento_revelado + contra_evidencia, casos ativos)\n")
    linhas = []
    for n in nomes:
        txt = " ".join(r["comportamento_revelado"] + " " + r["contra_evidencia_ou_leitura_alternativa"] for r in ativos[n])
        nw = max(1, len(palavras(txt)))
        h = contar_termos(txt, HEDGES)
        a = contar_termos(txt, ADJETIVOS)
        cm = sum(len(r["contra_evidencia_ou_leitura_alternativa"]) for r in ativos[n]) / max(1, len(ativos[n]))
        com_num = sum(1 for r in ativos[n] if re.search(r"\d", r["contra_evidencia_ou_leitura_alternativa"]))
        linhas.append([n, nw, h, f"{1000*h/nw:.1f}", a, f"{1000*a/nw:.1f}", f"{cm:.0f}", f"{100*com_num/max(1,len(ativos[n])):.0f}%"])
    P(tabela(["lado", "palavras", "hedges", "hedges/1000", "adjetivos", "adjetivos/1000", "tam. medio contra-evid. (car.)", "contra-evid. com numero"], linhas))
    P("\nListas usadas: HEDGES e ADJETIVOS no topo do script (aproximacao por prefixo de palavra; serve para comparar os lados, nao para medir tom).\n")

    # 8 rankings
    P("## 8. Rankings pela mesma regra\n")
    P("**Regra dos 10 mais fortes.** " + RULE_FORTES + "\n")
    P("**Regra dos 5 mais fracos.** " + RULE_FRACOS + "\n")
    for n in nomes:
        P(f"### {n}\n")
        f = ranking_fortes(lados[n])
        P("Mais fortes: " + ", ".join(f"{r['id']} ({r['forca_leitura_indireta']}/{r['confianca_fato']})" for r in f))
        el = [r for r in lados[n] if r["status"] == "indireto" and passa_barra(r) and r["disputado"] != "sim"
              and r["forca_leitura_indireta"] in ("forte", "média")]
        P(f"(elegiveis: {len(el)})")
        w = ranking_fracos(lados[n])
        P("Mais fracos: " + ", ".join(f"{r['id']} ({r['forca_leitura_indireta']}/{r['confianca_fato']})" for r in w) + "\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lula", default=os.path.join(AQUI, "indireto_lula.csv"))
    ap.add_argument("--flavio", default=os.path.join(AQUI, "indireto_flavio.csv"))
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    lados = {"Lula/PT": ler_csv(a.lula), "Flávio/Bolsonaro": ler_csv(a.flavio)}
    rel = relatorio(lados)
    if a.saida:
        with open(a.saida, "w", encoding="utf-8") as f:
            f.write(rel + "\n")
    else:
        sys.stdout.write(rel + "\n")


if __name__ == "__main__":
    main()
