import sys, json, random
sys.path.insert(0,'/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/scripts')
import dl, unicodedata
norm=lambda x: unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().upper().strip()
UFS='ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to'.split()
allsec=[]; muni={}
for uf in UFS:
    cfg=dl.config(uf)
    for a in cfg['abr']:
        for m in a['mu']:
            muni[(uf,m['cd'])]=m['nm']
            for z in m['zon']:
                for s in z['sec']:
                    allsec.append((uf,m['cd'],z['cd'],s['ns']))
print('total secoes', len(allsec), flush=True)
json.dump({'n_total':len(allsec)}, open(dl.RAW+'/universe.json','w'))
rng=random.Random(20261025)
nat=rng.sample(allsec,150)
def pick(uf,names,k):
    cds=[c for (u,c),n in muni.items() if u==uf and norm(n) in [norm(x) for x in names]]
    assert cds, names
    pool=[s for s in allsec if s[0]==uf and s[1] in cds]
    print(uf,names,cds,len(pool),flush=True)
    return rng.sample(pool,k)
ba=pick('ba',['SALVADOR'],50)+pick('ba',['FEIRA DE SANTANA'],15)+pick('ba',['LAURO DE FREITAS'],15)
sp=pick('sp',['SÃO PAULO'],80)
plan=[('nacional',s) for s in nat]+[('ba_cidades',s) for s in ba]+[('sp_capital',s) for s in sp]
res=[]
for i,(grp,(uf,m,z,s)) in enumerate(plan):
    aux,out=dl.section(uf,m,z,s)
    res.append({'grupo':grp,'uf':uf,'mun':m,'nm':muni[(uf,m)],'zona':z,'secao':s,'hashes':out,'aux_st':aux.get('st') if aux else out})
    if i%20==0: print(i, flush=True); json.dump(res, open(dl.RAW+'/sample_index.json','w'))
json.dump(res, open(dl.RAW+'/sample_index.json','w'))
print('done',len(res))
