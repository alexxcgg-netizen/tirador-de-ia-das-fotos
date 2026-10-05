import pandas as pd, json, urllib.request
OUT='/home/user/tirador-de-ia-das-fotos/cenarios/dados/'
rows=[]
def R(fonte,ref,faixa,ind,val,un,obs=''): rows.append(dict(fonte=fonte,referencia=ref,faixa_renda=faixa,indicador=ind,valor=val,unidade=un,observacao=obs))
# BCB SGS agregados
sgs={29034:'comprometimento_renda_servico_divida_dessaz',29035:'comprometimento_renda_servico_divida_exceto_habitacional_dessaz',29036:'comprometimento_renda_amortizacao_dessaz',29264:'comprometimento_renda_juros_sem_ajuste',29265:'comprometimento_renda_servico_divida_sem_ajuste',29037:'endividamento_familias_sfn_renda_12m',29038:'endividamento_familias_exceto_habitacional_renda_12m',21084:'inadimplencia_carteira_pf_total_90d',21112:'inadimplencia_carteira_pf_recursos_livres_90d'}
for s,n in sgs.items():
    r=json.load(urllib.request.urlopen(f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{s}/dados/ultimos/1?formato=json',timeout=60))[0]
    d=r['data'].split('/'); R(f'BCB SGS {s}',f'{d[2]}-{d[1]}','Todas (agregado nacional)',n,float(r['valor']),'%','RNDBF = renda nacional disponivel bruta das familias' if s<29300 and s>29000 else '')
# SCR.data por faixa de renda
t=pd.read_pickle('scr_porte.pkl')
ordem=['Sem rendimento','Até 1 salário mínimo','Mais de 1 a 2 salários mínimos','Mais de 2 a 3 salários mínimos','Mais de 3 a 5 salários mínimos','Mais de 5 a 10 salários mínimos','Mais de 10 a 20 salários mínimos','Acima de 20 salários mínimos','Indisponível','TOTAL PF']
for f in ordem:
    x=t[t.porte==f].iloc[0]
    for c,u in [('carteira_ativa_rs_bi','R$ bilhoes'),('pct_carteira_pf','%'),('pct_inadimplencia_90d','%'),('pct_vencido_15d','%'),('pct_ativo_problematico','%')]:
        R('BCB SCR.data (planilha_202607.csv), cliente=PF, por porte (renda do tomador)','2026-07',f,'scr_'+c,round(float(x[c]),2),u,'inadimplencia_90d = carteira_inadimplida_arrastada/carteira_ativa')
m=pd.read_pickle('scr_mod.pkl')
for _,x in m.iterrows():
    R('BCB SCR.data (planilha_202607.csv), PF por porte x modalidade','2026-07',x.porte,f'scr_inadimplencia_90d__{x.modalidade}',round(float(x.pct_inadimplencia_90d),2),'%',f'carteira R$ {x.carteira_ativa_rs_bi:.1f} bi')
    R('BCB SCR.data (planilha_202607.csv), PF por porte x modalidade','2026-07',x.porte,f'scr_carteira_rs_bi__{x.modalidade}',round(float(x.carteira_ativa_rs_bi),2),'R$ bilhoes','')
# Peic CNC agosto/2026
pf='CNC Peic ago/2026 (divulgada 10/09/2026, portaldocomercio.org.br)'
peic={'Ate 3 SM':(85.1,38.8,18.3),'3 a 5 SM':(83.7,28.0,None),'5 a 10 SM':(77.2,20.3,7.8),'Mais de 10 SM':(72.3,14.9,None),'Total':(82.0,29.9,12.5)}
for f,(e,a,s) in peic.items():
    R(pf,'2026-08',f,'peic_pct_familias_endividadas',e,'% familias')
    R(pf,'2026-08',f,'peic_pct_familias_contas_em_atraso',a,'% familias')
    if s is not None: R(pf,'2026-08',f,'peic_pct_sem_condicoes_de_pagar',s,'% familias')
R(pf,'2026-08','Total','peic_pct_renda_comprometida_media',29.5,'% renda','media entre endividados')
R(pf,'2026-08','Total','peic_pct_familias_mais_50pct_renda_comprometida',19.2,'% familias')
R('CNC Peic jul/2026 (Agencia Brasil 07/08/2026)','2026-07','Total','peic_tempo_medio_atraso',64.6,'dias')
R('CNC Peic jul/2026 (Agencia Brasil 07/08/2026)','2026-07','Ate 3 SM','peic_pct_familias_contas_em_atraso',38.5,'% familias')
R('CNC Peic jul/2026 (Agencia Brasil 07/08/2026)','2026-07','Mais de 10 SM','peic_pct_familias_contas_em_atraso',15.1,'% familias')
R('Serasa Mapa da Inadimplencia (via imprensa; fonte privada)','2026-08','Total','serasa_pessoas_negativadas',83.9,'milhoes de pessoas','recorde da serie; sem recorte por renda; fonte secundaria')
pd.DataFrame(rows).to_csv(OUT+'endividamento_por_renda.csv',index=False)
print(len(rows))
