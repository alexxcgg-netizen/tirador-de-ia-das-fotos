import sys, json, csv, collections, datetime
sys.path.insert(0,'/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts')
import parse
U='/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas'
idx=json.load(open(U+'/raw/brusque_index.json'))
cfg=json.load(open(U+'/raw/config/sc.json'))
m=[m for m in cfg['abr'][0]['mu'] if m['cd']=='80551'][0]
agreg={}
for z in m['zon']:
    for s in z['sec']:
        if 'nsa' in s: agreg[(z['cd'],s['ns'])]=s['nsa']
rows=[]; notable=collections.Counter(); hrs=[]
for x in idx:
    if not isinstance(x['hashes'],list): continue
    h=x['hashes'][0]; b=parse.bu(h['files']['bu']); l=parse.log(h['files']['log'])
    v=l['votos']; t17=datetime.datetime(2026,10,25,17,0,0); t1730=datetime.datetime(2026,10,25,17,30,0)
    flags=[]
    if (b['id_mun'],b['id_zona'],b['id_secao'])!=(80551,int(x['zona']),int(x['secao'])): flags.append('id_bu_difere')
    if b['soma_votos']!=b['compareceram']: flags.append('soma_votos!=comparecimento')
    if len(v)!=b['compareceram']: flags.append(f'votos_log({len(v)})!=bu({b["compareceram"]})')
    if b['tipoUrna']!='secao': flags.append('tipoUrna='+b['tipoUrna'])
    if b['tipoArquivo']!='votacaoUE': flags.append('tipoArquivo='+b['tipoArquivo'])
    bv=[t for t in l['boot_times'] if l['pronta'] and t>l['pronta'] and (not l['enc_conf'] or t<l['enc_conf'])]
    if bv: flags.append(f'religada_durante_votacao_{len(bv)}x')
    if len(l['urnas_ids'])>1: flags.append('varias_urnas_no_log:'+'/'.join(l['urnas_ids']))
    if l['urnas_ids'] and b['urna_id'] not in [int(u) for u in l['urnas_ids']]: flags.append('urna_log!=urna_bu')
    if v and (v[0]<datetime.datetime(2026,10,25,8,0) ): flags.append('voto_antes_8h')
    for k,c in l['notable'].items(): notable[k]+=c
    rows.append({'zona':x['zona'],'secao':x['secao'],'secoes_agregadas':';'.join(agreg.get((x['zona'],x['secao']),[])),
        'local':b['local'],'urna':b['urna_id'],'tipo_urna':b['tipoUrna'],'aptos':b['aptos'],'comparecimento':b['compareceram'],
        'lula_13':b['lula'],'flavio_22':b['flavio'],'brancos':b['brancos'],'nulos':b['nulos'],
        'abertura_bu':b['abertura'],'encerramento_bu':b['encerramento'],'emissao_bu':b['emissao'],
        'log_pronta':l['pronta'],'log_operador_encerrar':l['enc_sel'],'log_encerramento_confirmado':l['enc_conf'],
        'votos_log':len(v),'primeiro_voto':v[0] if v else '','ultimo_voto':v[-1] if v else '',
        'votos_apos_17h00':sum(t>=t17 for t in v),'votos_apos_17h30':sum(t>=t1730 for t in v),
        'urna_ligada_no_dia':l['boots_dia'],'religada_durante_votacao':len(bv),'alertas_log':l['levels'].get('ALERTA',0),'erros_log':l['levels'].get('ERRO',0),
        'flags':';'.join(flags)})
    for t in v: hrs.append(('sc','80551','BRUSQUE',x['zona'],x['secao'],'brusque',t))
with open(U+'/brusque_secoes.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
tot=collections.Counter()
for r in rows:
    for k in ('aptos','comparecimento','lula_13','flavio_22','brancos','nulos','votos_log','votos_apos_17h00','votos_apos_17h30'): tot[k]+=r[k]
print(len(rows), dict(tot))
print('flags', collections.Counter(f for r in rows for f in r['flags'].split(';') if f))
print('encerramento hist', collections.Counter(str(r['encerramento_bu'])[9:13] for r in rows).most_common(30))
json.dump([[a,b,c,d,e,f,t.isoformat()] for a,b,c,d,e,f,t in hrs], open(U+'/raw/brusque_votos.json','w'))
for k,c in sorted(notable.items(), key=lambda z:-z[1]): print(c,k)
