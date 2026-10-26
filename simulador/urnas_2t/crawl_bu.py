"""Rastreador so de BU do 2o turno 2026 (pleito 3221), todas as secoes.
Um pedido por vez (aux.json + bu.dat por secao), espera crescente no 429, retoma de onde parou.
Rodar com: python3 -I crawl_bu.py   (de fora da pasta de dados)
Saida: urnas/todas_secoes.csv (append), urnas/crawl/progress.json, urnas/crawl/crawl.log
"""
import sys, os, json, csv, time, re, ssl, http.client, datetime, urllib.parse
SCR = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts'
sys.path.insert(0, SCR)
import parse  # compila bu2026.asn1

U = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas'
CR = U + '/crawl'; RAW = CR + '/raw'; CFG = CR + '/config'
for d in (CR, RAW, CFG): os.makedirs(d, exist_ok=True)
OUT = U + '/todas_secoes.csv'
PEND = CR + '/pendentes.csv'
HOST = 'resultados.tse.jus.br'
BASE = '/oficial/ele2026/arquivo-urna/3221'
UFS = ['sp', 'mg', 'rj', 'ba', 'rs', 'pr', 'pe', 'ce', 'pa', 'sc', 'go', 'ma', 'am', 'es', 'pb', 'rn', 'mt',
       'al', 'pi', 'df', 'ms', 'se', 'ro', 'to', 'ac', 'ap', 'rr', 'zz']
FIELDS = ['uf', 'cd_mun', 'municipio', 'zona', 'secao', 'secoes_agregadas', 'aux_st', 'n_hashes', 'tipo_urna',
          'aptos', 'comparecimento', 'lula_13', 'flavio_22', 'brancos', 'nulos', 'outros_nominais',
          'hab_biometria', 'hab_biografia_sem_digital', 'compareceram_sem_biometria',
          'abertura_bu_local', 'encerramento_bu_local', 'comparecimento_cargo_pres', 'soma_votos_pres',
          'soma_igual_comparecimento', 'flags']
SAFE = re.compile(r'^[A-Za-z0-9._-]+$')
LOG = open(CR + '/crawl.log', 'a')
def log(*a):
    LOG.write(time.strftime('%Y-%m-%d %H:%M:%S ') + ' '.join(map(str, a)) + '\n'); LOG.flush()

MIN_INT = float(os.environ.get('CRAWL_MIN_INTERVAL', '0.5'))  # ~2 pedidos/s no maximo
st = {'interval': MIN_INT, 'last': 0.0, 'ok': 0, 'n429': 0, 'streak': 0, 'req': 0}
_conn = [None]
def _connect():
    p = urllib.parse.urlparse(os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or '')
    ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
    if p.hostname:
        c = http.client.HTTPSConnection(p.hostname, p.port, context=ctx, timeout=60); c.set_tunnel(HOST, 443)
    else:
        c = http.client.HTTPSConnection(HOST, 443, context=ctx, timeout=60)
    return c
def get(path, tries=10):
    """devolve (status, bytes). status 200/404/... ; 'fail' depois de muitas tentativas"""
    wait = 5
    for i in range(tries):
        dt = time.time() - st['last']
        if dt < st['interval']: time.sleep(st['interval'] - dt)
        st['last'] = time.time(); st['req'] += 1
        try:
            if _conn[0] is None: _conn[0] = _connect()
            _conn[0].request('GET', BASE + path, headers={'Connection': 'keep-alive', 'User-Agent': 'pesquisa-urnas/1.0'})
            r = _conn[0].getresponse(); data = r.read()
            if r.getheader('Connection', '').lower() == 'close': _conn[0].close(); _conn[0] = None
        except Exception as e:
            log('ERR', type(e).__name__, e, path)
            try: _conn[0].close()
            except Exception: pass
            _conn[0] = None; time.sleep(wait); wait = min(wait * 2, 300); continue
        if r.status == 200:
            st['streak'] += 1
            if st['streak'] >= 300 and st['interval'] > MIN_INT:
                st['interval'] = max(MIN_INT, st['interval'] * 0.9); st['streak'] = 0
            return 200, data
        if r.status == 429 or r.status >= 500:
            st['n429'] += r.status == 429; st['streak'] = 0
            st['interval'] = min(5.0, st['interval'] * 1.3)
            ra = r.getheader('Retry-After')
            s = max(wait, int(ra)) if ra and ra.isdigit() else wait
            log(r.status, 'sleep', s, 'interval', round(st['interval'], 2), path)
            time.sleep(s); wait = min(wait * 2, 300); continue
        return r.status, data
    return 'fail', b''

def config(uf):
    f = f'{CFG}/{uf}.json'
    if not (os.path.exists(f) and os.path.getsize(f) > 0):
        s, d = get(f'/config/{uf}/{uf}-p003221-cs.json')
        if s != 200: raise RuntimeError(f'config {uf} {s}')
        open(f, 'wb').write(d)
    return json.load(open(f))

def done_keys():
    k = set()
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, newline='')): k.add((r['uf'], r['cd_mun'], r['zona'], r['secao']))
    return k

def process(uf, mun, nm, z, s, agreg):
    rel = f'{uf}/{mun}/{z}/{s}'
    row = {'uf': uf, 'cd_mun': mun, 'municipio': nm, 'zona': z, 'secao': s, 'secoes_agregadas': agreg}
    code, d = get(f'/dados/{rel}/p003221-{uf}-m{mun}-z{z}-s{s}-aux.json')
    if code != 200: return None, f'aux_{code}'
    aux = json.loads(d)
    hs = [h for h in aux.get('hashes', []) if SAFE.match(h.get('hash', ''))]
    row['aux_st'] = aux.get('st'); row['n_hashes'] = len(hs)
    cand = [(h, a['nm']) for h in hs for a in h.get('arq', []) if a.get('tp') == 'bu' and SAFE.match(a.get('nm', ''))]
    if not cand: return None, f'sem_bu_no_aux_{aux.get("st")}'
    h, nmf = cand[-1]  # ultimo hash publicado
    code, d = get(f'/dados/{rel}/{h["hash"]}/{nmf}')
    if code != 200: return None, f'bu_{code}'
    tmp = f'{RAW}/{uf}{mun}{z}{s}-bu.dat'
    open(tmp, 'wb').write(d)
    try:
        b = parse.bu(tmp)
    except Exception as e:
        return None, f'bu_decode_{type(e).__name__}'
    finally:
        os.remove(tmp)
    flags = []
    if (b['id_mun'], b['id_zona'], b['id_secao']) != (int(mun), int(z), int(s)): flags.append('id_bu_difere')
    if b.get('qtdComparecimento_cargo') != b['compareceram']: flags.append('comparecimento_cargo_difere')
    if b['tipoUrna'] != 'secao': flags.append('tipoUrna=' + b['tipoUrna'])
    if b['tipoArquivo'] != 'votacaoUE': flags.append('tipoArquivo=' + b['tipoArquivo'])
    if b.get('dadosSA'): flags.append('BU_de_SA')
    if 'presidente' not in b['cargos']: flags.append('sem_cargo_presidente')
    if len(hs) != 1: flags.append(f'{len(hs)}_hashes')
    row.update(tipo_urna=b['tipoUrna'], aptos=b.get('aptos'), comparecimento=b['compareceram'], lula_13=b['lula'],
               flavio_22=b['flavio'], brancos=b['brancos'], nulos=b['nulos'], outros_nominais=b['outros_nominais'],
               hab_biometria=b['bio'], hab_biografia_sem_digital=b['biografia'], compareceram_sem_biometria=b['semBio'],
               abertura_bu_local=b['abertura'], encerramento_bu_local=b['encerramento'],
               comparecimento_cargo_pres=b.get('qtdComparecimento_cargo'), soma_votos_pres=b['soma_votos'],
               soma_igual_comparecimento=int(b['soma_votos'] == b['compareceram']), flags=';'.join(flags))
    return row, None

def main():
    only = sys.argv[1:]  # opcional: lista de UFs
    ufs = [u for u in UFS if not only or u in only]
    done = done_keys(); log('START done=', len(done), 'ufs', ufs)
    new = not os.path.exists(OUT)
    fo = open(OUT, 'a', newline=''); w = csv.DictWriter(fo, fieldnames=FIELDS)
    if new: w.writeheader()
    newp = not os.path.exists(PEND)
    fp = open(PEND, 'a', newline=''); wp = csv.writer(fp)
    if newp: wp.writerow(['uf', 'cd_mun', 'zona', 'secao', 'motivo', 'quando'])
    t0 = time.time(); n0 = len(done); prog = {}
    for uf in ufs:
        cfg = config(uf)
        plan = []
        for a in cfg['abr']:
            for m in a['mu']:
                if os.environ.get('CRAWL_MUN') and m['cd'] != os.environ['CRAWL_MUN']: continue
                for z in m['zon']:
                    for s in z['sec']:
                        if 'nsp' in s: continue  # secao agregada a outra: sem urna propria
                        plan.append((m['cd'], m.get('nm', ''), z['cd'], s['ns'], ';'.join(s.get('nsa', []))))
        todo = [p for p in plan if (uf, p[0], p[2], p[3]) not in done]
        prog[uf] = {'total': len(plan), 'feitas': len(plan) - len(todo)}
        log('UF', uf, 'total', len(plan), 'faltam', len(todo))
        for i, (mun, nm, z, s, ag) in enumerate(todo):
            if not SAFE.match(mun + z + s): continue
            row, err = process(uf, mun, nm, z, s, ag)
            if row:
                w.writerow(row); fo.flush(); done.add((uf, mun, z, s)); prog[uf]['feitas'] += 1
            else:
                wp.writerow([uf, mun, z, s, err, time.strftime('%Y-%m-%d %H:%M:%S')]); fp.flush()
            if i % 50 == 0:
                el = time.time() - t0; nd = len(done) - n0
                json.dump({'atualizado': time.strftime('%Y-%m-%d %H:%M:%S'), 'secoes_feitas_total': len(done),
                           'nesta_execucao': nd, 'secoes_por_hora': round(nd / el * 3600) if el > 0 else 0,
                           'uf_atual': uf, 'por_uf': prog, 'pedidos': st['req'], 'n429': st['n429'],
                           'intervalo_s': round(st['interval'], 3)}, open(CR + '/progress.json', 'w'), indent=1)
    log('FIM', len(done))
    json.dump({'atualizado': time.strftime('%Y-%m-%d %H:%M:%S'), 'FIM': True, 'secoes_feitas_total': len(done), 'por_uf': prog,
               'pedidos': st['req'], 'n429': st['n429']}, open(CR + '/progress.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
