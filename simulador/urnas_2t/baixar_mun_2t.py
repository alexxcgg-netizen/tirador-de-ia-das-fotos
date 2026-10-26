"""Baixa o resultado do 2º turno (TSE, 6258) de cada município do CSV do 1º turno, um por vez, com pausa e
novas tentativas no 429. Retoma de onde parou. Grava um JSON por município em PASTA."""
import csv, json, sys, time
from pathlib import Path
sys.path.insert(0, "/home/user/tirador-de-ia-das-fotos/simulador")
import resultado_1t as R
PASTA = Path(sys.argv[1])
mun = [r for r in csv.DictReader(open("/home/user/tirador-de-ia-das-fotos/simulador/data/municipios_1t_2026.csv", encoding="utf-8")) if r["uf"] != "ZZ"]
mun.sort(key=lambda r: -int(r["validos"]))
ok = falha = 0
for r in mun:
    f = PASTA / f"{r['uf'].lower()}{int(r['cd_municipio']):05d}.json"
    if f.exists():
        continue
    for t in range(6):
        try:
            js = R._baixar(R.url_municipio("ele2026", "6258", r["uf"], int(r["cd_municipio"])), timeout=20, tentativas=1)
            f.write_text(json.dumps(js, ensure_ascii=False), encoding="utf-8"); ok += 1
            break
        except Exception as ex:
            time.sleep(3 + 4 * t if "429" in str(ex) else 1)
    else:
        falha += 1
    time.sleep(0.25)
    if (ok + falha) % 250 == 0:
        print(time.strftime("%H:%M:%S"), ok, falha, flush=True)
print("FIM", ok, falha, flush=True)
