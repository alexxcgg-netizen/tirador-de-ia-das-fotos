import pandas as pd, numpy as np
U='/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas'
df=pd.read_csv(U+'/todas_secoes.csv',dtype={'cd_mun':str,'zona':str,'secao':str}).drop_duplicates(['uf','cd_mun','zona','secao'])
df['v2']=df.lula_13+df.flavio_22
k=['uf','cd_mun','zona','secao']
fl=df[((df.v2>=100)&((df.lula_13/df.v2>=.95)|(df.flavio_22/df.v2>=.95)))|((df.aptos>=50)&(df.comparecimento>=df.aptos))][k].assign(grupo='sinalizada')
rest=df.merge(fl[k],on=k,how='left',indicator=True); rest=rest[rest._merge=='left_only']
am=rest.sample(14000,random_state=7)[k].assign(grupo='amostra')
al=pd.concat([fl,am]); al.to_csv(U+'/alvos_1t.csv',index=False)
print(len(fl),len(am),len(al))
