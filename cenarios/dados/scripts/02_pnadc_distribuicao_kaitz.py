import pandas as pd, numpy as np
SM=1621.0
OUT='/home/user/tirador-de-ia-das-fotos/cenarios/dados/'
df=pd.read_pickle('poder/ocup_2026q2.pkl')
reg={'1':'Norte','2':'Nordeste','3':'Sudeste','4':'Sul','5':'Centro-Oeste'}
df['regiao']=df.UF.str[0].map(reg)
p=df.VD4009; cnpj=df.V4019=='1'
formal=p.isin(['01','03','05','06','07'])|(p.isin(['08','09'])&cnpj)
df['vinculo']=np.where(formal,'formal','informal')
df['emp_cart_priv']=p=='01'
df['com_rend']=df.VD4019>0
w='V1028'
bins=[0,0.98,1.02,1.5,2,3,5,10,np.inf]
labels=['<1 SM (abaixo de 0,98)','~1 SM (0,98-1,02)','1-1,5 SM','1,5-2 SM','2-3 SM','3-5 SM','5-10 SM','>10 SM']
def wq(x,wt,q):
    o=np.argsort(x); x=x[o]; wt=wt[o]; c=np.cumsum(wt)/wt.sum()
    return np.interp(q,c,x)
rows=[]
def add(nivel,geo,vinc,d):
    tot=d[w].sum(); dr=d[d.com_rend]; totr=dr[w].sum()
    r=dr.VD4019/SM
    cat=pd.cut(r,bins,labels=labels,right=False)
    sh=dr.groupby(cat,observed=False)[w].sum()/totr
    base=dict(nivel=nivel,local=geo,vinculo=vinc,ocupados_mil=round(tot/1e3,1),ocupados_com_rendimento_mil=round(totr/1e3,1))
    for k,v in sh.items(): rows.append({**base,'faixa_sm':k,'pct_ocupados_com_rend':round(100*v,2)})
    ex=dr[dr.VD4019==SM][w].sum()/totr
    b5=dr[(r>=0.95)&(r<=1.05)][w].sum()/totr
    le1=dr[r<=1.02][w].sum()/totr
    med=wq(dr.VD4019.values,dr[w].values,0.5)
    rows.append({**base,'faixa_sm':'exatamente R$ 1.621 (=1 SM)','pct_ocupados_com_rend':round(100*ex,2)})
    rows.append({**base,'faixa_sm':'entre 0,95 e 1,05 SM','pct_ocupados_com_rend':round(100*b5,2)})
    rows.append({**base,'faixa_sm':'ate 1 SM (<=1,02)','pct_ocupados_com_rend':round(100*le1,2)})
    rows.append({**base,'faixa_sm':'mediana em multiplos de SM','pct_ocupados_com_rend':round(med/SM,3)})
for vinc,sub in [('todos',df),('formal',df[df.vinculo=='formal']),('informal',df[df.vinculo=='informal']),('empregado_privado_com_carteira',df[df.emp_cart_priv])]:
    add('Brasil','Brasil',vinc,sub)
    for g,s in sub.groupby('regiao'): add('Regiao',g,vinc,s)
out=pd.DataFrame(rows)
out.insert(0,'periodo','2026T2'); out.insert(1,'salario_minimo_rs',SM)
out.insert(2,'renda','habitual de todos os trabalhos (VD4019)')
out.to_csv(OUT+'distribuicao_salarios.csv',index=False)
# Kaitz
uf={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
kr=[]
def kz(nivel,cod,nome,d):
    dr=d[d.com_rend]
    r={'periodo':'2026T2','nivel':nivel,'codigo':cod,'local':nome,'salario_minimo_rs':SM,'ocupados_com_rend_mil':round(dr[w].sum()/1e3,1)}
    for var,lab in [('VD4019','todos_trab'),('VD4016','trab_principal')]:
        x=dr[dr[var]>0]
        med=wq(x[var].values,x[w].values,0.5); mean=np.average(x[var],weights=x[w])
        r[f'mediana_{lab}_rs']=round(med,0); r[f'media_{lab}_rs']=round(mean,0)
        r[f'kaitz_mediana_{lab}']=round(SM/med,3); r[f'kaitz_media_{lab}']=round(SM/mean,3)
    f=dr[dr.vinculo=='formal']; med=wq(f.VD4019.values,f[w].values,0.5)
    r['mediana_formal_rs']=round(med,0); r['kaitz_mediana_formal']=round(SM/med,3)
    c=dr[dr.emp_cart_priv]; med=wq(c.VD4019.values,c[w].values,0.5)
    r['mediana_empregado_carteira_privado_rs']=round(med,0); r['kaitz_mediana_empregado_carteira_privado']=round(SM/med,3)
    i=dr[dr.vinculo=='informal']; med=wq(i.VD4019.values,i[w].values,0.5)
    r['mediana_informal_rs']=round(med,0); r['kaitz_mediana_informal']=round(SM/med,3)
    r['pct_informal']=round(100*d[d.vinculo=='informal'][w].sum()/d[w].sum(),1)
    r['n_amostra']=len(dr)
    kr.append(r)
kz('Brasil','1','Brasil',df)
for c,n in {'1':'Norte','2':'Nordeste','3':'Sudeste','4':'Sul','5':'Centro-Oeste'}.items(): kz('Regiao',c,n,df[df.UF.str[0]==c])
for c,n in uf.items(): kz('UF',c,n,df[df.UF==c])
pd.DataFrame(kr).to_csv(OUT+'kaitz_uf.csv',index=False)
print(pd.DataFrame(kr)[['local','mediana_todos_trab_rs','media_todos_trab_rs','kaitz_mediana_todos_trab','kaitz_media_todos_trab','pct_informal']].to_string())
print(out[out.local=='Brasil'].to_string())
