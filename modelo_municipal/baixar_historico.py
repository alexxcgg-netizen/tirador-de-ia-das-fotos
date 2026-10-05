"""Agrega 2018 e 2022 (Presidente, 1º e 2º turnos) por município a partir dos dados abertos do TSE.

Fontes (cdn.tse.jus.br/estatistica/sead/odsele/):
  votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip  -> votos por candidato (membro *_BR.csv)
  detalhe_votacao_munzona/detalhe_votacao_munzona_{ano}.zip      -> aptos, comparecimento, brancos, nulos
Os zips grandes (~640 MB) não são baixados inteiros: o leitor abaixo faz requisições HTTP Range e extrai só o
membro *_BR.csv (onde estão as linhas de Presidente). Zips eventualmente baixados por inteiro são apagados ao final.

Saída: modelo_municipal/data/hist_{ano}.csv, uma linha por município (inclui exterior, UF=ZZ) com colunas
  {t}_aptos, {t}_comparecimento, {t}_brancos, {t}_nulos, {t}_validos, {t}_pt, {t}_opp  para t in (t1, t2)
  e t1_terceiros = t1_validos - t1_pt - t1_opp.
"""
from __future__ import annotations

import io
import os
import random
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "data"
CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
NUM_PT = 13
NUM_OPP = {2018: 17, 2022: 22}
# terceiros de esquerda/centro-esquerda (os demais terceiros formam o bloco "não-esquerda": centro, centro-direita, direita)
ESQUERDA = {2018: {12, 18, 50, 16, 54}, 2022: {12, 16, 21, 80}}


def _req(url: str, rng: tuple[int, int] | None = None, metodo: str = "GET"):
    espera = 2.0
    for _ in range(12):
        try:
            h = {"User-Agent": "modelo-municipal/1.0 (pesquisa)"}
            if rng:
                h["Range"] = f"bytes={rng[0]}-{rng[1]}"
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h, method=metodo), timeout=120)
            if metodo == "HEAD":
                return r
            return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except Exception:
            pass
        time.sleep(espera + random.random())
        espera = min(espera * 2, 90)
    raise RuntimeError(f"falhou: {url}")


class HttpRangeFile(io.RawIOBase):
    """Arquivo somente-leitura e 'seekable' sobre HTTP Range, suficiente para zipfile.ZipFile."""

    def __init__(self, url: str):
        self.url = url
        self.size = int(_req(url, metodo="HEAD").headers["Content-Length"])
        self.pos = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        # blocos grandes: zipfile lê o membro em pedaços pequenos
        bloco = max(n, 0)
        data = _req(self.url, (self.pos, self.pos + bloco - 1))
        self.pos += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)


CACHE_BRUTO = Path(os.environ.get("CACHE_BRUTO_TSE", DADOS / "_bruto"))  # não versionado


def ler_membro_br(tipo: str, ano: int) -> pd.DataFrame:
    cache = CACHE_BRUTO / f"{tipo}_{ano}_BR.csv"
    if cache.exists():
        return pd.read_csv(cache, sep=";", encoding="latin-1", low_memory=False)
    url = f"{CDN}/{tipo}/{tipo}_{ano}.zip"
    f = io.BufferedReader(HttpRangeFile(url), buffer_size=8 * 1024 * 1024)
    z = zipfile.ZipFile(f)
    nome = [n for n in z.namelist() if n.upper().endswith("_BR.CSV")][0]
    print(f"{url} -> {nome} ({z.getinfo(nome).compress_size/1e6:.1f} MB comprimido)", file=sys.stderr)
    with z.open(nome) as m:
        bruto = m.read()
    CACHE_BRUTO.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(bruto)
    return pd.read_csv(io.BytesIO(bruto), sep=";", encoding="latin-1", low_memory=False)


def agregar(ano: int) -> pd.DataFrame:
    det = ler_membro_br("detalhe_votacao_munzona", ano)
    det = det[det.CD_CARGO == 1]
    cand = ler_membro_br("votacao_candidato_munzona", ano)
    cand = cand[cand.CD_CARGO == 1]
    chave = ["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"]
    out = None
    for t in (1, 2):
        d = det[det.NR_TURNO == t].groupby(chave)[
            ["QT_APTOS", "QT_COMPARECIMENTO", "QT_VOTOS_BRANCOS", "QT_TOTAL_VOTOS_NULOS", "QT_TOTAL_VOTOS_VALIDOS"]].sum()
        d.columns = [f"t{t}_aptos", f"t{t}_comparecimento", f"t{t}_brancos", f"t{t}_nulos", f"t{t}_validos"]
        c = cand[cand.NR_TURNO == t]
        piv = c.pivot_table(index=chave, columns="NR_CANDIDATO", values="QT_VOTOS_NOMINAIS", aggfunc="sum").fillna(0)
        d[f"t{t}_pt"] = piv[NUM_PT].reindex(d.index).fillna(0)
        d[f"t{t}_opp"] = piv[NUM_OPP[ano]].reindex(d.index).fillna(0)
        if t == 1:
            esq = [c for c in piv.columns if c in ESQUERDA[ano]]
            d["t1_terc_esq"] = piv[esq].sum(axis=1).reindex(d.index).fillna(0)
        d[f"t{t}_soma_cand"] = piv.sum(axis=1).reindex(d.index).fillna(0)
        out = d if out is None else out.join(d, how="outer")
    out = out.reset_index().rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "cd_municipio_tse", "NM_MUNICIPIO": "municipio"})
    out["uf"] = out.uf.replace({"VT": "ZZ"})
    out["t1_terceiros"] = out.t1_soma_cand - out.t1_pt - out.t1_opp
    out["t1_terc_nesq"] = out.t1_terceiros - out.t1_terc_esq
    out = out.drop(columns=["t1_soma_cand", "t2_soma_cand"])
    return out


def main(anos=(2018, 2022)):
    DADOS.mkdir(exist_ok=True)
    for ano in anos:
        df = agregar(int(ano))
        df.to_csv(DADOS / f"hist_{ano}.csv", index=False)
        print(ano, len(df), df[[c for c in df.columns if c.startswith("t")]].sum().round(0).to_dict(), file=sys.stderr)
    for z in DADOS.glob("*.zip"):
        z.unlink()


if __name__ == "__main__":
    main(sys.argv[1:] or (2018, 2022))
