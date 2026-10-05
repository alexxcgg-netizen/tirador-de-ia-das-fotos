import pandas as pd
num=['vencido_acima_de_15_dias','carteira_ativa','carteira_inadimplida_arrastada','ativo_problematico','a_vencer_ate_90_dias']
d=pd.read_csv('planilha_202607.csv',sep=';',encoding='utf-8-sig',usecols=['data_base','cliente','porte','modalidade']+num,decimal=',',dtype={c:str for c in ['cliente','porte','modalidade']})
d=d[d.cliente=='PF']
d['porte']=d.porte.str.strip().str.replace('PF - ','')
d['modalidade']=d.modalidade.str.strip().str.replace('PF - ','')
for c in num: d[c]=pd.to_numeric(d[c],errors='coerce')
def agg(g):
    a=g[num].sum()
    return pd.Series({'carteira_ativa_rs_bi':a.carteira_ativa/1e9,'vencido_15d_rs_bi':a.vencido_acima_de_15_dias/1e9,'inadimplida_90d_rs_bi':a.carteira_inadimplida_arrastada/1e9,'ativo_problematico_rs_bi':a.ativo_problematico/1e9,
      'pct_inadimplencia_90d':100*a.carteira_inadimplida_arrastada/a.carteira_ativa,'pct_vencido_15d':100*a.vencido_acima_de_15_dias/a.carteira_ativa,'pct_ativo_problematico':100*a.ativo_problematico/a.carteira_ativa})
t=d.groupby('porte').apply(agg); t.loc['TOTAL PF']=agg(d)
t['pct_carteira_pf']=100*t.carteira_ativa_rs_bi/t.loc['TOTAL PF','carteira_ativa_rs_bi']
print(t.round(2).to_string())
m=d.groupby(['porte','modalidade']).apply(agg).reset_index()
m=pd.concat([m,d.groupby('modalidade').apply(agg).reset_index().assign(porte='TOTAL PF')])
t.reset_index().to_pickle('scr_porte.pkl'); m.to_pickle('scr_mod.pkl')
print(m[m.porte=='TOTAL PF'].round(2).to_string())
