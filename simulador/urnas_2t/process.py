import sys, json, csv, os, shutil, collections, datetime
sys.path.insert(0,'/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts')
import dl, parse
U='/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas'
OFF={'ac':-2,'am':-1,'ro':-1,'rr':-1,'mt':-1,'ms':-1}  # horas do relogio local em relacao a Brasilia
plan=json.load(open(U+'/amostra_plano.json'))
OUT=U+'/amostra_secoes.csv'; VH=U+'/raw_votos_min_amostra.csv'; NOT=U+'/raw_notable_amostra.json'
done=set()
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT)): done.add((r['grupo'],r['uf'],r['mun'],r['zona'],r['secao']))
notable=json.load(open(NOT)) if os.path.exists(NOT) else {}
FIELDS=['grupo','uf','mun','municipio','zona','secao','aux_st','n_arquivos_hash','tipo_urna','urna','aptos','comparecimento','lula_13','flavio_22','brancos','nulos',
 'offset_h','abertura_bu_local','encerramento_bu_local','encerramento_bu_brasilia','log_pronta_local','log_encerramento_local','votos_log','primeiro_voto_local','ultimo_voto_local',
 'votos_apos_17h00_bsb','votos_apos_17h30_bsb','votos_apos_17h00_local','religada_durante_votacao','suspensoes','erros_log','flags']
newf=not os.path.exists(OUT)
fo=open(OUT,'a',newline=''); w=csv.DictWriter(fo,fieldnames=FIELDS)
if newf: w.writeheader()
fv=open(VH,'a',newline=''); wv=csv.writer(fv)
def fmt(t): return t.strftime('%Y-%m-%d %H:%M:%S') if t else ''
for i,(g,uf,mun,z,s,nm) in enumerate(plan):
    if (g,uf,mun,z,s) in done: continue
    aux,out=dl.section(uf,mun,z,s)
    row={'grupo':g,'uf':uf,'mun':mun,'municipio':nm,'zona':z,'secao':s,'offset_h':OFF.get(uf,0)}
    flags=[]
    if aux is None:
        row['aux_st']=out; row['flags']='sem_aux'
    else:
        row['aux_st']=aux.get('st'); row['n_arquivos_hash']=len(out)
        if len(out)!=1: flags.append(f'{len(out)}_hashes')
        h=out[-1] if out else None
        if h and 'bu' in h['files']:
            b=parse.bu(h['files']['bu'])
            row.update(tipo_urna=b['tipoUrna'],urna=b['urna_id'],aptos=b['aptos'],comparecimento=b['compareceram'],lula_13=b['lula'],flavio_22=b['flavio'],brancos=b['brancos'],nulos=b['nulos'],
                       abertura_bu_local=b['abertura'],encerramento_bu_local=b['encerramento'])
            if b['encerramento']:
                e=datetime.datetime.strptime(b['encerramento'],'%Y%m%dT%H%M%S')-datetime.timedelta(hours=OFF.get(uf,0))
                row['encerramento_bu_brasilia']=fmt(e)
            if (b['id_mun'],b['id_zona'],b['id_secao'])!=(int(mun),int(z),int(s)): flags.append('id_bu_difere')
            if b['soma_votos']!=b['compareceram']: flags.append('soma_votos!=comparecimento')
            if b['tipoUrna']!='secao': flags.append('tipoUrna='+b['tipoUrna'])
            if b['tipoArquivo']!='votacaoUE': flags.append('tipoArquivo='+b['tipoArquivo'])
            if b.get('dadosSA'): flags.append('BU_de_SA')
        else: flags.append('sem_bu')
        if h and 'log' in h['files']:
            l=parse.log(h['files']['log'])
            v=l['votos']; off=datetime.timedelta(hours=OFF.get(uf,0))
            vb=[t-off for t in v]
            t17=datetime.datetime(2026,10,25,17); t1730=datetime.datetime(2026,10,25,17,30)
            bv=[t for t in l['boot_times'] if l['pronta'] and t>l['pronta'] and (not l['enc_conf'] or t<l['enc_conf'])]
            row.update(log_pronta_local=fmt(l['pronta']),log_encerramento_local=fmt(l['enc_conf']),votos_log=len(v),
                       primeiro_voto_local=fmt(v[0]) if v else '',ultimo_voto_local=fmt(v[-1]) if v else '',
                       votos_apos_17h00_bsb=sum(t>=t17 for t in vb),votos_apos_17h30_bsb=sum(t>=t1730 for t in vb),
                       votos_apos_17h00_local=sum(t>=t17 for t in v),religada_durante_votacao=len(bv),suspensoes=len(l['suspensoes']),
                       erros_log=l['levels'].get('ERRO',0))
            if 'comparecimento' in row and len(v)!=row['comparecimento']: flags.append(f'votos_log({len(v)})!=bu({row["comparecimento"]})')
            if bv: flags.append(f'religada_durante_votacao_{len(bv)}x')
            if len(l['urnas_ids'])>1: flags.append('varias_urnas_no_log:'+'/'.join(l['urnas_ids']))
            if l['nested_fail']: flags.append('log_aninhado_ilegivel:'+'/'.join(l['nested_fail']))
            if v and min(vb)<datetime.datetime(2026,10,25,8): flags.append('voto_antes_8h_bsb')
            if not l['enc_conf']: flags.append('sem_encerramento_no_log')
            cnt=collections.Counter(t.strftime('%H:%M') for t in vb)
            for m,c in sorted(cnt.items()): wv.writerow([g,uf,mun,nm,z,s,m,c])
            for k,c in l['notable'].items():
                key='|'.join(k); d=notable.setdefault(key,[0,0]); d[0]+=c; d[1]+=1
        else: flags.append('sem_log')
        row['flags']=';'.join(flags)
    w.writerow(row); fo.flush(); fv.flush()
    shutil.rmtree(f'{dl.RAW}/{uf}/{mun}/{z}/{s}', ignore_errors=True)
    json.dump(notable, open(NOT,'w'))
    if i%20==0: print(i, flush=True)
print('done')
