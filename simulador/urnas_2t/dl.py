import os, sys, time, json, re, urllib.request, urllib.error, random
BASE='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
RAW='/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad/urnas/raw'
LOG=open(RAW+'/dl_log.txt','a')
_last=[0.0]
def fetch(url, dest, tries=8):
    if os.path.exists(dest) and os.path.getsize(dest)>0: return 'cached'
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    wait=5
    for i in range(tries):
        dt=time.time()-_last[0]
        if dt<0.3: time.sleep(0.3-dt)
        _last[0]=time.time()
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data=r.read()
            with open(dest+'.part','wb') as f: f.write(data)
            os.replace(dest+'.part', dest)
            return 'ok'
        except urllib.error.HTTPError as e:
            LOG.write(f'{e.code} {url}\n'); LOG.flush()
            if e.code==429 or e.code>=500:
                time.sleep(wait); wait=min(wait*2,120); continue
            return f'http{e.code}'
        except Exception as e:
            LOG.write(f'ERR {e} {url}\n'); LOG.flush()
            time.sleep(wait); wait=min(wait*2,120)
    return 'fail'
SAFE=re.compile(r'^[A-Za-z0-9._-]+$')
def config(uf):
    d=f'{RAW}/config/{uf}.json'
    fetch(f'{BASE}/config/{uf}/{uf}-p003221-cs.json', d)
    return json.load(open(d))
def section(uf, mun, zona, sec, types=('bu','log')):
    """downloads aux + requested file types for every hash; returns list of (hash, st, {tp:path})"""
    rel=f'{uf}/{mun}/{zona}/{sec}'
    d=f'{RAW}/{rel}'
    auxn=f'p003221-{uf}-m{mun}-z{zona}-s{sec}-aux.json'
    st=fetch(f'{BASE}/dados/{rel}/{auxn}', f'{d}/aux.json')
    if st not in ('ok','cached'): return None, st
    aux=json.load(open(f'{d}/aux.json'))
    out=[]
    for h in aux.get('hashes',[]):
        hs=h['hash']; 
        if not SAFE.match(hs): continue
        files={}
        for a in h.get('arq',[]):
            if a.get('tp') in types and SAFE.match(a['nm']):
                p=f'{d}/{hs[:16]}/{a["nm"]}'
                r=fetch(f'{BASE}/dados/{rel}/{hs}/{a["nm"]}', p)
                if r in ('ok','cached'): files[a['tp']]=p
                else: files[a['tp']+'_err']=r
        out.append({'hash':hs,'st':h.get('st'),'dr':h.get('dr'),'hr':h.get('hr'),'files':files})
    return aux, out
