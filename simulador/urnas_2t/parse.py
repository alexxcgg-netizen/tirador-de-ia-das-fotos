import asn1tools, zipfile, re, collections, datetime
SPEC='/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts/bu2026.asn1'
C=asn1tools.compile_files(SPEC, codec='ber')
def bu(path):
    env=C.decode('EntidadeEnvelopeGenerico', open(path,'rb').read())
    b=C.decode('EntidadeBoletimUrna', env['conteudo'])
    r={'tipoUrna':b['urna']['tipoUrna'],'tipoArquivo':b['urna']['tipoArquivo'],
       'versao':b['urna']['versaoVotacao'],
       'motivoSA': str(b['urna'].get('motivoUtilizacaoSA')) if b['urna'].get('motivoUtilizacaoSA') else '',
       'urna_id':b['urna']['correspondenciaResultado']['carga']['numeroInternoUrna'],
       'compareceram':b['qtdEleitoresCompareceram'],'emissao':b['dataHoraEmissao'],
       'id_mun':b['identificacaoSecao']['municipioZona']['municipio'],
       'id_zona':b['identificacaoSecao']['municipioZona']['zona'],
       'id_secao':b['identificacaoSecao']['secao'],'local':b['identificacaoSecao']['local']}
    ds=b['dadosSecaoSA']
    if ds[0]=='dadosSecao':
        r['abertura']=ds[1]['dataHoraAbertura']; r['encerramento']=ds[1]['dataHoraEncerramento']
    else:
        r['abertura']=''; r['encerramento']=''; r['dadosSA']=str(ds[1])
    det=b.get('detalhamentoComparecimento') or {}
    r['bio']=det.get('qtdEleitoresHabilitadosPorBiometria'); r['biografia']=det.get('qtdEleitoresHabilitadosPorBiografia'); r['semBio']=det.get('qtdEleitoresCompareceramSemBiometria')
    r['lula']=r['flavio']=r['brancos']=r['nulos']=0; r['outros_nominais']=0; r['n_cargos']=0
    for e in b['resultadosVotacaoPorEleicao']:
        r['aptos']=e['qtdEleitoresAptos']; r['aptosTTE']=e['qtdEleitoresAptosTTE']; r['idEleicao']=e['idEleicao']
        for rv in e['resultadosVotacao']:
            for t in rv['totaisVotosCargo']:
                r['n_cargos']+=1; r.setdefault('cargos',[]).append(str(t['codigoCargo'][1]))
                if t['codigoCargo']!=('cargoConstitucional','presidente'): continue
                r['qtdComparecimento_cargo']=rv['qtdComparecimento']
                for v in t['votosVotaveis']:
                    tv=v['tipoVoto']; q=v['quantidadeVotos']
                    if tv=='nominal':
                        cod=v['identificacaoVotavel']['codigo']
                        if cod==13: r['lula']+=q
                        elif cod==22: r['flavio']+=q
                        else: r['outros_nominais']+=q
                    elif tv=='branco': r['brancos']+=q
                    elif tv=='nulo': r['nulos']+=q
                    else: r['outros_tipo_'+tv]=r.get('outros_tipo_'+tv,0)+q
    r['cargos']='/'.join(r.get('cargos',[]))
    r['soma_votos']=r['lula']+r['flavio']+r['brancos']+r['nulos']+r['outros_nominais']
    return r

def ts(l):
    return datetime.datetime.strptime(l[:19],'%d/%m/%Y %H:%M:%S')
INTEREST=re.compile(r'ligada|Iniciando aplica|contingên|Contingên|substitu|Substitu|reinicia|Reinicia|ERRO|Erro|erro|falha|Falha|FALHA|Encerra|encerra|pronta para receber|Desligamento|desligad|Bateria|bateria|Ajuste|ajust|hora|Hora|Cancelad|cancelad|anulad|Anulad|suspens|Suspens|Prorroga|prorroga|horário|Horário')
def msg_mask(m):
    return re.sub(r'\d','#',m)
def log(path, day='25/10/2026'):
    z=zipfile.ZipFile(path)
    names=z.namelist()
    import io
    chunks=[]; nested_ok=[]; nested_fail=[]
    for n in names:
        d=z.read(n)
        if n.endswith('.dat'): chunks.append(d)
        elif n.endswith('.jez'):
            try:
                if d[:2]==b'PK':
                    zz=zipfile.ZipFile(io.BytesIO(d))
                    for nn in zz.namelist():
                        if nn.endswith('.dat'): chunks.append(zz.read(nn))
                else:
                    import py7zr
                    with py7zr.SevenZipFile(io.BytesIO(d)) as sz:
                        for nn,bio in sz.readall().items():
                            if nn.endswith('.dat'): chunks.append(bio.read())
                nested_ok.append(n)
            except Exception as e:
                nested_fail.append(n+':'+type(e).__name__)
    seen=set(); lines=[]
    for d in chunks:
        for l in d.decode('latin-1', errors='replace').splitlines():
            if l in seen: continue
            seen.add(l); lines.append(l)
    lines.sort(key=lambda l: (l[6:10],l[3:5],l[0:2],l[11:19]) if len(l)>19 and l[2]=='/' else ('',))
    r_n={'nested_ok':nested_ok,'nested_fail':nested_fail}
    r={'log_files':';'.join(names)}; r.update(r_n)
    votos=[]; ev=[]; urnas=set(); levels=collections.Counter(); notable=collections.Counter()
    pronta=None; hab=collections.Counter(); nhab=0; cont=[]; reinic=0; erros=collections.Counter(); boot_t=[]; susp=[]; enc_sel=None; enc_conf=None; ini_enc=None; boots=0; apps=0; lastvote=None
    for l in lines:
        if not l.startswith(day): continue
        p=l.split('\t')
        if len(p)<5: continue
        levels[p[1]]+=1; urnas.add(p[2]); msg=p[4]
        t=ts(l)
        if msg.startswith('Tipo de habilitação do eleitor'):
            hab[msg.split('[',1)[-1].rstrip(']') if '[' in msg else msg]+=1
        if msg.startswith('Eleitor foi habilitado'): nhab+=1
        if 'ontingência' in msg or 'ubstitu' in msg: cont.append(msg_mask(msg))
        if msg.startswith('Reiniciando a urna') or msg.startswith('Urna reiniciada'): reinic+=1
        if p[1]=='ERRO': erros[msg_mask(msg)[:90]]+=1
        if msg.startswith('O voto do eleitor foi computado'): votos.append(t)
        elif msg.startswith('Urna pronta para receber votos'): pronta = pronta or t
        elif msg.startswith('Operador selecionou: Encerrar vota'): enc_sel=t
        elif msg.startswith('Procedimento de encerramento confirmado'): enc_conf=t
        elif msg.startswith('Inicio do Encerramento') or msg.startswith('Início do Encerramento'): ini_enc=t
        if msg.startswith('Urna ligada em'): boots+=1; boot_t.append(t)
        if msg.startswith('Votação suspensa'): susp.append(t)
        if p[3]=='VOTA' and msg.startswith('Iniciando aplica'): apps+=1
        if p[1] not in ('INFO',) or INTEREST.search(msg):
            notable[(p[1],p[3],re.sub(r'\d','#',msg)[:140])]+=1
    r.update(votos=votos, pronta=pronta, enc_sel=enc_sel, enc_conf=enc_conf, ini_enc=ini_enc,
             boots_dia=boots, hab=hab, nhab=nhab, cont=cont, reinic=reinic, erros=erros, boot_times=boot_t, suspensoes=susp, vota_apps_dia=apps, urnas_ids=sorted(urnas), levels=dict(levels), notable=notable,
             all_days=sorted(set(l[:10] for l in lines if len(l)>10 and l[2]=='/')))
    return r
