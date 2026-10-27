"""Vigia a publicacao do Boletim de Urna na Web do 2o turno 2026 (bweb_2t_{UF}_*.zip) no Portal de Dados Abertos do TSE.
Quando aparecer, baixa UF por UF (um ZIP por vez, apagado depois), le so o cargo Presidente e grava
urnas/todas_secoes_bweb.csv (uma linha por secao). Sem biometria detalhada (o bweb so traz QT_ELEI_BIOM_SEM_HABILITACAO);
a biometria vem do rastreador de BU (crawl_bu.py).
Uso: python3 -I bweb_watch.py            (vigia a cada 15 min)
     python3 -I bweb_watch.py --teste ZIP (processa um zip local, ex. do 1o turno, para teste)"""
import sys, os, io, csv, json, time, zipfile, urllib.request, collections, re
U = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas'
W = U + '/bweb'; os.makedirs(W, exist_ok=True)
OUT = U + '/todas_secoes_bweb.csv'
API = 'https://dadosabertos.tse.jus.br/api/3/action/package_show?id=resultados-2026-boletim-de-urna'
LOG = open(W + '/watch.log', 'a')
def log(*a): LOG.write(time.strftime('%Y-%m-%d %H:%M:%S ') + ' '.join(map(str, a)) + '\n'); LOG.flush()
F = ['uf', 'cd_mun', 'municipio', 'zona', 'secao', 'secoes_agregadas', 'tipo_urna', 'aptos', 'comparecimento', 'lula_13',
     'flavio_22', 'brancos', 'nulos', 'outros', 'abertura', 'encerramento', 'biom_sem_habilitacao', 'bu_recebido',
     'soma_votos_pres', 'soma_igual_comparecimento']

def ingest(zpath, uf_hint, w, cargo='1'):
    sec = {}
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if not n.lower().endswith('.csv'): continue
            with z.open(n) as fh:
                for r in csv.DictReader(io.TextIOWrapper(fh, encoding='latin-1', newline=''), delimiter=';'):
                    if r['CD_CARGO_PERGUNTA'] != cargo: continue
                    k = (r['SG_UF'], r['CD_MUNICIPIO'], r['NR_ZONA'], r['NR_SECAO'])
                    s = sec.get(k)
                    if s is None:
                        s = sec[k] = {'uf': r['SG_UF'].lower(), 'cd_mun': r['CD_MUNICIPIO'].zfill(5), 'municipio': r['NM_MUNICIPIO'],
                                      'zona': r['NR_ZONA'].zfill(4), 'secao': r['NR_SECAO'].zfill(4),
                                      'secoes_agregadas': '' if r['DS_SECOES_AGREGADAS'] == '#NULO#' else r['DS_SECOES_AGREGADAS'],
                                      'tipo_urna': r['DS_TIPO_URNA'], 'aptos': int(r['QT_APTOS']), 'comparecimento': int(r['QT_COMPARECIMENTO']),
                                      'lula_13': 0, 'flavio_22': 0, 'brancos': 0, 'nulos': 0, 'outros': 0,
                                      'abertura': r['DT_ABERTURA'], 'encerramento': r['DT_ENCERRAMENTO'],
                                      'biom_sem_habilitacao': r['QT_ELEI_BIOM_SEM_HABILITACAO'], 'bu_recebido': r['DT_BU_RECEBIDO']}
                    q = int(r['QT_VOTOS']); tv = r['DS_TIPO_VOTAVEL'].lower(); nr = r['NR_VOTAVEL']
                    if nr == '13' and tv.startswith('nominal'): s['lula_13'] += q
                    elif nr == '22' and tv.startswith('nominal'): s['flavio_22'] += q
                    elif tv.startswith('branco'): s['brancos'] += q
                    elif tv.startswith('nulo'): s['nulos'] += q
                    else: s['outros'] += q
    for s in sec.values():
        s['soma_votos_pres'] = s['lula_13'] + s['flavio_22'] + s['brancos'] + s['nulos'] + s['outros']
        s['soma_igual_comparecimento'] = int(s['soma_votos_pres'] == s['comparecimento'])
        w.writerow(s)
    return len(sec)

def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--teste':
        w = csv.DictWriter(open(W + '/teste.csv', 'w', newline=''), fieldnames=F); w.writeheader(); n = ingest(sys.argv[2], '', w); print('secoes', n); return
    stf = W + '/estado.json'
    estado = json.load(open(stf)) if os.path.exists(stf) else {'feitos': []}
    while True:
        try:
            d = json.load(urllib.request.urlopen(API, timeout=60))['result']
            urls = [r['url'] for r in d['resources'] if re.search(r'/bweb_2t_[A-Z]{2}_\d{12}\.zip$', r['url'])]
        except Exception as e:
            log('ERR api', e); urls = []
        log('verificado: urls 2t =', len(urls))
        pend = [u for u in urls if u not in estado['feitos']]
        if pend:
            new = not os.path.exists(OUT)
            fo = open(OUT, 'a', newline=''); w = csv.DictWriter(fo, fieldnames=F)
            if new: w.writeheader()
            for u in sorted(pend):
                zp = W + '/atual.zip'
                try:
                    urllib.request.urlretrieve(u, zp)
                    n = ingest(zp, '', w); fo.flush()
                    estado['feitos'].append(u); json.dump(estado, open(stf, 'w'))
                    log('OK', u, 'secoes', n)
                except Exception as e:
                    log('ERR', u, e)
                finally:
                    if os.path.exists(zp): os.remove(zp)
            fo.close()
        if urls and all(u in estado['feitos'] for u in urls) and len(urls) >= 28:
            log('FIM: todas as UFs do bweb 2t processadas'); return
        time.sleep(900)

if __name__ == '__main__':
    main()
