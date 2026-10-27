#!/usr/bin/env python3
"""Gera simulador/web/segundo_turno_conteudo.json a partir das notas de pesquisa do 2º turno.

Uso (re-executável, só biblioteca padrão):
    python simulador/gerar_segundo_turno_json.py
    python simulador/gerar_segundo_turno_json.py --saida x.json

Entradas:
  research_notes/Segundo turno 2026/pesquisas_pos_1t.md   (pesquisas depois do 1º turno)
  research_notes/Segundo turno 2026/campanha_2t_eventos.md (campanha do 2º turno e o indireto)
  research_notes/Democracia 2026/risco_democratico.md      (risco democrático)
  simulador/data/pesquisas_nacionais.csv                   (números usados pelo modelo)

Regra: o script só EXTRAI texto e tabelas das notas (markdown leve preservado: **negrito**, [link](url),
`código`); não escreve conteúdo próprio. Marcas como [não verificado], [disputado] e [reportado] passam
intactas. A única transformação editorial é a ordem das colunas por candidato: Flávio Bolsonaro antes de
Lula (ordem alfabética pelo primeiro nome, regra do painel), sem mudar o conteúdo das células.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
NOTA_P = RAIZ / "research_notes" / "Segundo turno 2026" / "pesquisas_pos_1t.md"
NOTA_C = RAIZ / "research_notes" / "Segundo turno 2026" / "campanha_2t_eventos.md"
NOTA_D = RAIZ / "research_notes" / "Democracia 2026" / "risco_democratico.md"
CSV_NAC = AQUI / "data" / "pesquisas_nacionais.csv"
SAIDA_PADRAO = AQUI / "web" / "segundo_turno_conteudo.json"
DATA_1T = "2026-10-04"


# ---------------------------------------------------------------- markdown (subconjunto usado nas notas)
def secao(md: str, prefixo: str, ocorrencia: int = 0) -> str:
    """Corpo da seção cujo título começa com `prefixo` (até o próximo título de nível igual ou maior)."""
    linhas = md.split("\n")
    achados = [i for i, l in enumerate(linhas) if re.match(r"^#{1,6} ", l) and l.lstrip("#").strip().startswith(prefixo)]
    if len(achados) <= ocorrencia:
        raise KeyError(f"seção não encontrada: {prefixo!r}")
    i = achados[ocorrencia]
    nivel = len(linhas[i]) - len(linhas[i].lstrip("#"))
    fim = len(linhas)
    for j in range(i + 1, len(linhas)):
        m = re.match(r"^(#{1,6}) ", linhas[j])
        if m and len(m.group(1)) <= nivel:
            fim = j
            break
    return "\n".join(linhas[i + 1:fim]).strip("\n")


def titulo_secao(md: str, prefixo: str) -> str:
    for l in md.split("\n"):
        if re.match(r"^#{1,6} ", l) and l.lstrip("#").strip().startswith(prefixo):
            return l.lstrip("#").strip()
    raise KeyError(prefixo)


def _celulas(linha: str) -> list[str]:
    s = linha.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def blocos(corpo: str) -> list[dict]:
    """Converte um trecho de markdown em blocos: parágrafo (p), lista (ul/ol, com subitens), tabela (tab), subtítulo (h)."""
    out: list[dict] = []
    linhas = corpo.split("\n")
    i = 0
    while i < len(linhas):
        l = linhas[i]
        s = l.strip()
        if not s or s == "---":
            i += 1
            continue
        m = re.match(r"^(#{1,6}) (.*)$", l)
        if m:
            out.append({"t": "h", "md": m.group(2).strip()})
            i += 1
            continue
        if s.startswith("|"):
            tab = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                tab.append(linhas[i])
                i += 1
            cab = _celulas(tab[0])
            lin = [_celulas(x) for x in tab[1:] if not re.match(r"^\s*\|?\s*:?-{2,}", x)]
            out.append({"t": "tab", "cab": cab, "lin": lin})
            continue
        if s.startswith(">"):
            txt = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                t = linhas[i].strip()[1:].strip()
                if t:
                    txt.append(t)
                i += 1
            for t in txt:
                out.append({"t": "p", "md": t})
            continue
        mi = re.match(r"^(- |\d+\. )(.*)$", l)
        if mi:
            tipo = "ul" if mi.group(1) == "- " else "ol"
            itens: list[dict] = []
            while i < len(linhas):
                l2 = linhas[i]
                if not l2.strip():
                    # lista continua se a próxima linha não vazia for item do mesmo tipo
                    k = i + 1
                    while k < len(linhas) and not linhas[k].strip():
                        k += 1
                    if k < len(linhas) and re.match(r"^(- |\d+\. )", linhas[k]) and (("- " == linhas[k][:2]) == (tipo == "ul")):
                        i = k
                        continue
                    break
                mt = re.match(r"^(- |\d+\. )(.*)$", l2)
                ms = re.match(r"^\s{2,}(- |\d+\. )(.*)$", l2)
                if mt and ((mt.group(1) == "- ") == (tipo == "ul")):
                    itens.append({"md": mt.group(2).strip(), "sub": []})
                elif ms and itens:
                    itens[-1]["sub"].append(ms.group(2).strip())
                elif l2.startswith(" ") and itens:
                    if itens[-1]["sub"]:
                        itens[-1]["sub"][-1] += " " + l2.strip()
                    else:
                        itens[-1]["md"] += " " + l2.strip()
                else:
                    break
                i += 1
            out.append({"t": tipo, "itens": [it if it["sub"] else it["md"] for it in itens]})
            continue
        par = [s]
        i += 1
        while i < len(linhas) and linhas[i].strip() and not re.match(r"^(#{1,6} |\||- |\d+\. |>)", linhas[i].strip()):
            par.append(linhas[i].strip())
            i += 1
        out.append({"t": "p", "md": " ".join(par)})
    return out


def tabela(corpo: str, n: int = 0) -> dict:
    tabs = [b for b in blocos(corpo) if b["t"] == "tab"]
    return tabs[n]


def itens(corpo: str, n: int = 0) -> list:
    ls = [b for b in blocos(corpo) if b["t"] in ("ul", "ol")]
    return ls[n]["itens"]


def paragrafo(corpo: str, inicio: str) -> str:
    for b in blocos(corpo):
        if b["t"] == "p" and b["md"].startswith(inicio):
            return b["md"]
    raise KeyError(inicio)


def plano(md: str) -> str:
    """Texto sem marcação (para os quadros Resumo, que são texto puro)."""
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1", md)
    s = s.replace("**", "")
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def sem_rotulo(md: str) -> str:
    """Tira o rótulo inicial em negrito ("**Resumo.** ", "**Resumo da seção 3.** ")."""
    return re.sub(r"^\*\*[^*]+\*\*:?\s*", "", md).strip()


def item_com(lista: list, inicio: str) -> str:
    for it in lista:
        txt = it if isinstance(it, str) else it["md"]
        if txt.startswith(inicio):
            return txt
    raise KeyError(inicio)


def flavio_antes(tab: dict) -> dict:
    """Reordena colunas para que as colunas de Flávio venham antes das de Lula (conteúdo das células intacto)."""
    cab = tab["cab"]
    idx = list(range(len(cab)))
    lula = [k for k in idx if re.search(r"\bLula\b", cab[k]) and not re.search(r"Fl[áa]vio", cab[k])]
    flav = [k for k in idx if re.search(r"Fl[áa]vio", cab[k])]
    if not lula or not flav or min(flav) < min(lula):
        return tab
    resto = [k for k in idx if k not in lula and k not in flav]
    fixos = [k for k in resto if k < min(lula)]
    ordem = fixos + flav + lula + [k for k in resto if k not in fixos]
    return {"t": "tab", "cab": [cab[k] for k in ordem], "lin": [[r[k] if k < len(r) else "" for k in ordem] for r in tab["lin"]]}


# ---------------------------------------------------------------- pesquisas pós-1º turno
def _inst(nome: str) -> str:
    return nome.split("/")[0].strip()


def pesquisas(md: str) -> dict:
    b = secao(md, "B. Tabela consolidada")
    tb = tabela(b)
    cab = tb["cab"]
    linhas = []
    for r in tb["lin"]:
        d = dict(zip(cab, r))
        linhas.append({"instituto": _inst(d["Instituto"]), "instituto_nota": d["Instituto"], "campo": d["Campo"],
                       "divulgacao": d["Divulg."], "n": d["n"], "modo": d["Modo"], "registro": d["Registro TSE"],
                       "lula_total": d["Lula (total)"], "flavio_total": d["Flávio (total)"], "branco_nulo": d["Branco/nulo"],
                       "ns": d["NS"], "lula_validos": d["Lula válidos"], "flavio_validos": d["Flávio válidos"], "margem": d["Margem"]})
    e = secao(md, "E. Comparação com a rodada anterior")
    te = tabela(e)
    anteriores = {}
    for r in te["lin"]:
        d = dict(zip(te["cab"], r))
        anteriores[_inst(d["Instituto"])] = {"antes": d["Antes (2T)"], "agora": d["Agora (2T)"],
                                              "mudanca": d[[k for k in te["cab"] if k.startswith("Mudança")][0]],
                                              "erro_1t": d[[k for k in te["cab"] if k.startswith("Erro")][0]]}
    verif = {}
    try:
        tv = tabela(secao(md, "Verificação em fonte primária"))
        for r in tv["lin"]:
            d = dict(zip(tv["cab"], r))
            for nome in d["Instituto"].split(","):
                verif[_inst(nome)] = {"fonte": d["Fonte aberta"], "confirma": d["O que confirma"], "status": d["Status"]}
        resumo_verif = sem_rotulo(paragrafo(secao(md, "Verificação em fonte primária"), "**Resumo.**"))
    except KeyError:
        resumo_verif = None
    csvp = []
    with open(CSV_NAC, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["campo_fim"] > DATA_1T and r["t2_lula"] and not r["lula"]:
                csvp.append({"instituto": r["instituto"], "campo_inicio": r["campo_inicio"], "campo_fim": r["campo_fim"],
                             "n": int(r["n"]) if r["n"] else None, "modo": r["modo"], "t2_lula": float(r["t2_lula"]),
                             "t2_flavio": float(r["t2_flavio"]),
                             "validos": "VOTOS VALIDOS" in r["obs"].upper()})   # mesma regra do modelo (resultado_1t.py)
    medias = paragrafo(b, "**Médias (válidos, Flávio)**")
    sel = blocos(secao(md, "Seleção (brecha 9), de novo"))
    return {
        "fonte": "research_notes/Segundo turno 2026/pesquisas_pos_1t.md (seções B, E e verificação) e simulador/data/pesquisas_nacionais.csv",
        "criterio": paragrafo(md, "Mesmo critério de verificação"),
        "tabela": linhas,
        "anteriores": anteriores,
        "verificacao": verif,
        "verificacao_resumo": resumo_verif,
        "csv": csvp,
        "medias": medias,
        "selecao": [x["md"] for x in sel if x["t"] == "p"],
        "resumo_aba": itens(secao(md, "Resumo da aba (atualização de 12/10)")),
    }


# ---------------------------------------------------------------- campanha do 2º turno
CASO_RE = re.compile(r"^\*\*(Novo, )?([LF]\d+)(?: (revisto|atualizado))?\. (.+?)\*\*(.*)$")


def casos(md: str) -> dict:
    """Casos L/F do indireto: título e corpo (seção 5) e atualizações (U7)."""
    out: dict[str, dict] = {}

    def varrer(corpo: str, rotulo: str):
        cur = None
        buf: list[str] = []

        def fecha():
            if cur:
                cod, tipo, tit, extra = cur
                linhas = ([extra] if extra else []) + buf
                c = out.setdefault(cod, {"codigo": cod, "lado": "lula" if cod.startswith("L") else "flavio", "titulo": tit, "versoes": []})
                if tipo == "revisto":
                    c["titulo"] = tit
                c["versoes"].append({"rotulo": rotulo if tipo else "Seção 5 (09/10, revista em 12/10)", "titulo": tit,
                                     "blocos": blocos("\n".join(linhas))})
        for l in corpo.split("\n"):
            m = CASO_RE.match(l.strip())
            if m or l.startswith("### ") or l.startswith("**O caso Vorcaro") or l.startswith("**Placar"):
                fecha()
                cur, buf = None, []
                if m:
                    cur = (m.group(2), m.group(3) or ("novo" if m.group(1) else None), m.group(4).strip(), m.group(5).strip())
                    if cur[1] == "novo":
                        cur = (cur[0], None, cur[2], cur[3])
                continue
            if cur:
                buf.append(l)
        fecha()

    varrer(secao(md, "5. O indireto"), "Seção 5")
    varrer(secao(md, "U7. O indireto"), "Atualização de 12/10 (U7)")
    # L3 foi dividido em L3a e L3b pela revisão de 12/10
    if "L3" in out:
        base = out["L3"]
        corpo = secao(md, "5. O indireto")
        for cod in ("L3a", "L3b"):
            m = re.search(r"^- \*\*" + cod + r"\. ([^:]+): (\w+)\.\*\* (.*)$", corpo, re.M)
            if m:
                out[cod] = {"codigo": cod, "lado": "lula", "titulo": base["titulo"].split(" Dividido")[0] + " " + m.group(1) + ".",
                            "versoes": base["versoes"]}
    return out


def placar(md: str) -> dict:
    tb = tabela(secao(md, "R3. Placar final"))
    linhas = []
    for r in tb["lin"]:
        d = dict(zip(tb["cab"], r))
        linhas.append({"forca": d[""] if "" in d else r[0],
                       "flavio": [x.strip() for x in d["Flávio"].split(",") if x.strip()],
                       "lula": [x.strip() for x in d["Lula"].split(",") if x.strip()]})
    return {"colunas": ["Flávio", "Lula"], "linhas": linhas}


def campanha(md: str) -> dict:
    cab = blocos(md.split("\n---\n")[0])
    resumo_geral = itens(secao(md, "Resumo", 0))
    resumo_u = itens(secao(md, "Resumo (atualização de 12/10)"))
    s1 = secao(md, "1. Linha do tempo")
    s2 = secao(md, "2. Apoios e neutralidades")
    s4 = secao(md, "4. Mercados de previsão")
    u6 = secao(md, "U6. Mercados")
    r = secao(md, "R. Revisão adversarial")
    u7 = secao(md, "U7. O indireto")
    vorc_i = u7.index("**O caso Vorcaro")
    vorc = blocos(u7[vorc_i:])
    cs = casos(md)
    pl = placar(md)
    for ln in pl["linhas"]:
        for cod in ln["flavio"] + ln["lula"]:
            if cod in cs:
                cs[cod]["forca"] = ln["forca"]
    u5 = itens(secao(md, "U5. Debates, PEC 6x1 e TSE"))
    return {
        "fonte": "research_notes/Segundo turno 2026/campanha_2t_eventos.md",
        "titulo": md.split("\n")[0].lstrip("# ").strip(),
        "cabecalho": [b["md"] for b in cab if b["t"] == "p"],
        "linha_tempo": {
            "ate_09": tabela(s1),
            "de_09_a_11": tabela(secao(md, "U2. Linha do tempo")),
            "correcoes": itens(secao(md, "U1. Correções explícitas")),
            "resumo": ["Atualização de 12/10: " + sem_rotulo(item_com(resumo_u, "**Fatos novos**")),
                       "Levantamento de 09/10 (o que mudou depois está no quadro de correções): " + sem_rotulo(paragrafo(s1, "**Resumo.**"))],
        },
        "apoios": {
            "eliminados": tabela(secao(md, "2.1 Candidatos eliminados")),
            "partidos": tabela(secao(md, "2.2 Partidos")),
            "governadores": tabela(secao(md, "2.3 Governadores")),
            "governadores_base": paragrafo(secao(md, "2.3 Governadores"), "Base:"),
            "novos": tabela(secao(md, "U4. Apoios")),
            "matriz": blocos(secao(md, "2.4 O que os apoios mudam")),
            "resumo": [sem_rotulo(paragrafo(s2, "**Resumo.**")), sem_rotulo(item_com(resumo_geral, "**Apoios:**"))],
        },
        "justica": {
            "decisoes": tabela(secao(md, "3.2 Decisões judiciais")),
            "atualizacao": item_com(u5, "**TSE**"),
            "resumo": [sem_rotulo(item_com(resumo_geral, "**Justiça:**")), sem_rotulo(item_com(resumo_u, "**TSE**"))],
        },
        "mercados": {
            "previsao": tabela(secao(md, "4.1 Mercados de previsão")),
            "previsao_12_10": tabela(u6, 0),
            "previsao_notas": [b["md"] for b in blocos(secao(md, "4.1 Mercados de previsão")) if b["t"] == "p"]
                              + [b["md"] for b in blocos(u6) if b["t"] == "p" and b["md"].startswith("Volume")],
            "ativos": tabela(secao(md, "4.2 Ativos")),
            "ativos_12_10": tabela(u6, 1),
            "ativos_notas": [b["md"] for b in blocos(secao(md, "4.2 Ativos")) if b["t"] == "p"]
                            + [b["md"] for b in blocos(u6) if b["t"] == "p" and b["md"].startswith("Alta na semana")],
            "bancos": tabela(secao(md, "4.3 Notas de bancos")),
            "bancos_notas": [b["md"] for b in blocos(secao(md, "4.3 Notas de bancos")) if b["t"] == "p"],
            "resumo": [sem_rotulo(paragrafo(s4, "**Resumo.**")), sem_rotulo(item_com(resumo_u, "**Mercados**"))],
        },
        "indireto": {
            "checklist": paragrafo(secao(md, "5. O indireto"), "Mesmas perguntas"),
            "regra": itens(secao(md, "R1. Regra única de força")),
            "placar": pl,
            "placar_notas": [b["md"] for b in blocos(secao(md, "R3. Placar final")) if b["t"] == "p"],
            "espelho": itens(secao(md, "5.3 Teste do espelho")),
            "casos": cs,
            "conflitos": tabela(secao(md, "R2. Conflitos")),
            "vorcaro": {"titulo": plano(vorc[0]["md"]), "tabela": flavio_antes([b for b in vorc if b["t"] == "tab"][0]),
                        "notas": [b["md"] for b in vorc[1:] if b["t"] == "p"]},
            "resumo": [sem_rotulo(paragrafo(r, "**Resumo da seção R.**")), sem_rotulo(paragrafo(secao(md, "5.3 Teste do espelho"), "**Resumo.**"))],
        },
        "disputados": {
            "lista": itens(secao(md, "R4. Itens marcados")),
            "nao_verificado_09_10": item_com(resumo_geral, "**Não verificado:**"),
            "nao_verificado_12_10": item_com(resumo_u, "**Não verificado**"),
            "resumo": [sem_rotulo(item_com(resumo_u, "**Não verificado**"))],
        },
        "resumo_aba": [plano(x) for x in itens(secao(md, "Resumo da aba"))],
    }


# ---------------------------------------------------------------- risco democrático
def _serie(tab: dict, col: str) -> list:
    k = tab["cab"].index(col)
    return [float(r[k].replace(",", ".")) if re.match(r"^[0-9]+([.,][0-9]+)?$", r[k]) else None for r in tab["lin"]]


def risco(md: str) -> dict:
    cab = md.split("\n## 0.")[0]
    s0 = secao(md, "0. Resposta curta")
    s3 = secao(md, "3. Restrições institucionais")
    s4 = secao(md, "4. Medidas com evidência")
    s5 = secao(md, "5. A literatura")
    s8 = secao(md, "8. Vereditos")
    v41 = tabela(secao(md, "4.1 V-Dem"))
    fh = tabela(secao(md, "4.2 Freedom House"))
    fh_lin = [r for r in fh["lin"] if r[0].startswith("Freedom House, Liberdade no Mundo")][0]
    resumo_final = itens(secao(md, "Resumo", 0))
    item2 = [it for it in resumo_final if isinstance(it, dict) and it["md"].startswith("**Forma fraca")][0]
    nv = itens(secao(md, "11. O que não foi verificado"))
    conv = itens(cab.split("**Convenções.**")[1])
    return {
        "fonte": "research_notes/Democracia 2026/risco_democratico.md",
        "titulo": md.split("\n")[0].lstrip("# ").strip(),
        "data": paragrafo(cab, "Data da pesquisa"),
        "convencoes": conv,
        "selecao": paragrafo(cab, "**Aviso de seleção"),
        "vereditos": {
            "tabela": tabela(s0),
            "notas": [b["md"] for b in blocos(s0) if b["t"] == "p"],
            "resumo": [sem_rotulo(paragrafo(s8, "**Resumo da seção 8.**")), plano(sem_rotulo(resumo_final[0] if isinstance(resumo_final[0], str) else resumo_final[0]["md"]))],
        },
        "evidencia": {
            "flavio": {"titulo": titulo_secao(md, "8.1"), "blocos": blocos(secao(md, "8.1"))},
            "lula": {"titulo": titulo_secao(md, "8.2"), "blocos": blocos(secao(md, "8.2"))},
            "sinais_tabela": tabela(secao(md, "5.1 Os quatro sinais")),
            "regua": paragrafo(s5, "**Régua de graduação"),
            "resumo": [sem_rotulo(paragrafo(s5, "**Resumo da seção 5.**"))] + [plano(x) for x in item2["sub"][:2]],
        },
        "freios": {
            "quoruns": tabela(secao(md, "3.1 Congresso eleito"), 1),
            "quoruns_leitura": paragrafo(secao(md, "3.1 Congresso eleito"), "[leitura] Para os dois"),
            "camara_fonte": paragrafo(secao(md, "3.1 Congresso eleito"), "**Câmara (513)**"),
            "senado": paragrafo(secao(md, "3.1 Congresso eleito"), "**Senado (81)"),
            "stf": tabela(secao(md, "3.2 STF")),
            "stf_projecao": tabela(secao(md, "3.2 STF"), 1),
            "stf_notas": [b["md"] for b in blocos(secao(md, "3.2 STF")) if b["t"] == "p"],
            "outros": tabela(secao(md, "3.3 Outros freios")),
            "sozinho": paragrafo(secao(md, "3.3 Outros freios"), "**O que um presidente muda sozinho**"),
            "resumo": [sem_rotulo(paragrafo(s3, "**Resumo da seção 3.**"))],
        },
        "indices": {
            "vdem": {"anos": [int(r[0]) for r in v41["lin"]],
                     "series": {c: _serie(v41, c) for c in v41["cab"][1:]},
                     "fonte": titulo_secao(md, "4.1 V-Dem")},
            "vdem_nota": [b["md"] for b in blocos(secao(md, "4.1 V-Dem")) if b["t"] == "p"],
            "freedom_house": {"anos": [int(x) for x in fh["cab"][1:]],
                              "valores": [float(x) if re.match(r"^\d+$", x) else None for x in fh_lin[1:]],
                              "rotulo": fh_lin[0]},
            "outros_indices": tabela(secao(md, "4.2 Freedom House")),
            "fontes_42": paragrafo(secao(md, "4.2 Freedom House"), "Fontes:"),
            "leitura": itens(secao(md, "4.3 O que se moveu")),
            "resumo": [sem_rotulo(paragrafo(s4, "**Resumo da seção 4.**"))],
        },
        "sinais": {
            "tabela": tabela(secao(md, "8.4 Sinais a observar")),
            "resumo": [plano(sem_rotulo(item_com(resumo_final, "**O que observar")))],
        },
        "peso": {
            "titulo": titulo_secao(md, "8.3"),
            "blocos": blocos(secao(md, "8.3")),
            "resumo": [plano(x) for x in item2["sub"][2:3]],
        },
        "nao_verificado": {"lista": nv, "resumo": [plano(conv[-1])] if conv else []},
        "resumo_aba": [plano(x) for x in itens(secao(md, "Resumo da aba"))],
    }


def _frases(no):
    """Quadros Resumo: texto puro e com inicial maiúscula (o rótulo em negrito das notas foi retirado)."""
    if isinstance(no, dict):
        for k, v in no.items():
            if k in ("resumo", "resumo_aba") and isinstance(v, list):
                no[k] = [plano(x)[:1].upper() + plano(x)[1:] for x in v if isinstance(x, str) and x.strip()]
            else:
                _frases(v)
    elif isinstance(no, list):
        for v in no:
            _frases(v)


def gerar() -> dict:
    p = NOTA_P.read_text(encoding="utf-8")
    c = NOTA_C.read_text(encoding="utf-8")
    d = NOTA_D.read_text(encoding="utf-8")
    out = {
        "meta": {"gerado_em": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "gerador": "simulador/gerar_segundo_turno_json.py",
                 "regra": "Texto extraído das notas sem reescrita; colunas por candidato na ordem Flávio Bolsonaro, Lula."},
        "pesquisas_pos_1t": pesquisas(p),
        "campanha_2t": campanha(c),
        "risco_democratico": risco(d),
    }
    _frases(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saida", default=str(SAIDA_PADRAO))
    a = ap.parse_args()
    js = gerar()
    Path(a.saida).write_text(json.dumps(js, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("gravado:", a.saida, f"({Path(a.saida).stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
