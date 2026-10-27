import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts')
import dl
cfg=dl.config('sc')
mu=[m for m in cfg['abr'][0]['mu'] if m['cd']=='80551'][0]
res=[]
n=0
for z in mu['zon']:
    for s in z['sec']:
        aux,out=dl.section('sc','80551',z['cd'],s['ns'])
        res.append({'uf':'sc','mun':'80551','zona':z['cd'],'secao':s['ns'],'hashes':out, 'aux_st': aux.get('st') if aux else out})
        n+=1
        if n%20==0: print(n, flush=True)
json.dump(res, open(dl.RAW+'/brusque_index.json','w'))
print('done', n)
