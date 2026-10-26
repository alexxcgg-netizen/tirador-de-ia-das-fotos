"""Confere todas_secoes.csv contra o total oficial do TSE por municipio (mun2t/{uf}{mun}.json, eleicao 6258).
Uso: python3 -I validar_secoes.py   -> imprime resumo e grava urnas/crawl/validacao_municipios.csv"""
import csv, json, os, collections
S = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad'
U = S + '/urnas'
K = ['aptos', 'comparecimento', 'lula_13', 'flavio_22', 'brancos', 'nulos']
agg = collections.defaultdict(collections.Counter); nsec = collections.Counter()
bad = []; flags = collections.Counter()
for r in csv.DictReader(open(U + '/todas_secoes.csv', newline='')):
    key = (r['uf'], r['cd_mun']); nsec[key] += 1
    for k in K: agg[key][k] += int(r[k] or 0)
    for k in ('hab_biometria', 'hab_biografia_sem_digital', 'compareceram_sem_biometria'): agg[key][k] += int(r[k] or 0)
    if r['soma_igual_comparecimento'] != '1': bad.append(r)
    for f in r['flags'].split(';'):
        if f: flags[f] += 1
out = []; st = collections.Counter()
for key, t in sorted(agg.items()):
    f = f'{S}/mun2t/{key[0]}{key[1]}.json'
    if not os.path.exists(f): st['sem_oficial_baixado'] += 1; continue
    d = json.load(open(f))
    of = {'aptos': int(d['e']['te']), 'comparecimento': int(d['e']['c']), 'brancos': int(d['v']['vb']), 'nulos': int(d['v']['tvn'])}
    for a in d['carg'][0]['agr']:
        for p in a['par']:
            for c in p['cand']:
                if c['n'] == '13': of['lula_13'] = int(c['vap'])
                if c['n'] == '22': of['flavio_22'] = int(c['vap'])
    completo = nsec[key] == int(d['s']['ts'])
    dif = {k: t[k] - of.get(k, 0) for k in K}
    ok = all(v == 0 for v in dif.values())
    st[('completo' if completo else 'parcial', 'bate' if ok else 'difere')] += 1
    out.append({'uf': key[0], 'cd_mun': key[1], 'secoes_lidas': nsec[key], 'secoes_oficiais': d['s']['ts'],
                'secoes_totalizadas_oficial': d['s']['st'], 'completo': int(completo), 'bate': int(ok),
                **{'dif_' + k: v for k, v in dif.items()}})
w = csv.DictWriter(open(U + '/crawl/validacao_municipios.csv', 'w', newline=''), fieldnames=list(out[0].keys()) if out else ['uf'])
w.writeheader(); w.writerows(out)
tot = collections.Counter()
for t in agg.values(): tot.update(t)
print('secoes lidas:', sum(nsec.values()), '| municipios:', len(agg))
print('totais:', dict(tot))
print('municipios (completude, conferencia):', dict(st))
print('municipios completos que NAO batem:', [(o['uf'], o['cd_mun'], {k: v for k, v in o.items() if k.startswith('dif_') and v}) for o in out if o['completo'] and not o['bate']][:20])
print('secoes em que soma dos votos de presidente != comparecimento:', len(bad))
for r in bad[:20]: print('  ', r['uf'], r['cd_mun'], r['municipio'], r['zona'], r['secao'], 'comp', r['comparecimento'], 'soma', r['soma_votos_pres'], r['flags'])
print('flags:', flags.most_common(15))
