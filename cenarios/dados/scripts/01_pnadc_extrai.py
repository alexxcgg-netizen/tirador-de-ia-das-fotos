import pandas as pd
cols={'Ano':(1,4),'Trimestre':(5,1),'UF':(6,2),'V1028':(50,15),'V2009':(104,3),'V4019':(186,1),'V4029':(195,1),
'VD4002':(410,1),'VD4009':(417,2),'VD4012':(423,1),'VD4016':(427,8),'VD4019':(444,8),'VD4031':(462,3)}
specs=[(s-1,s-1+w) for s,w in cols.values()]
df=pd.read_fwf('PNADC_022026.txt',colspecs=specs,names=list(cols),header=None,dtype=str)
df=df[df.VD4002=='1']
for c in ['V1028','V2009','VD4016','VD4019','VD4031']: df[c]=pd.to_numeric(df[c],errors='coerce')
df.to_pickle('poder/ocup_2026q2.pkl')
print(len(df), df.V1028.sum())
