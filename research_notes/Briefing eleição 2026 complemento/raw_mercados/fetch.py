import json,subprocess,sys,datetime
slugs="""brazil-presidential-election
brazil-presidential-election-first-round-winner
will-any-presidential-candidate-win-outright-in-the-first-round-of-the-brazil-election
which-candidates-will-advance-to-brazils-presidential-runoff
brazil-presidential-election-first-round-2nd-place
brazil-presidential-election-first-round-3rd-place
brazil-presidential-election-first-round-4th-place
brazil-presidential-election-first-round-margin-of-victory
brazil-presidential-election-first-round-lula-da-silva-vote-share
brazil-presidential-election-first-round-lula-da-silva-vote-share-higher-strikes-20261002141337150
brazil-presidential-election-first-round-flavio-bolsonaro-vote-share
brazil-presidential-election-first-round-flavio-bolsonaro-vote-share-higher-strikes
brazil-presidential-election-first-round-renan-santos-vote-share
brazil-presidential-election-first-round-augusto-cury-vote-share
brazil-presidential-election-first-round-turnout
lula-or-bolsonaro-favored-on
lula-flips-bolsonaro-for-brazil-president-by
brazil-presidential-election-first-round-1st-place-in-sao-paulo
brazil-presidential-election-first-round-1st-place-in-minas-gerais
brazil-presidential-election-first-round-1st-place-in-rio-de-janeiro
brazil-presidential-election-first-round-1st-place-in-bahia
brazil-presidential-election-first-round-1st-place-in-parana
brazil-presidential-election-first-round-1st-place-in-rio-grande-do-sul
brazil-presidential-election-first-round-1st-place-in-goias
brazil-presidential-election-first-round-1st-place-in-federal-district
brazil-presidential-election-first-round-1st-place-in-pernambuco
brazil-presidential-election-first-round-1st-place-in-ceara
brazil-presidential-election-first-round-1st-place-in-para
brazil-presidential-election-first-round-1st-place-in-amazonas
brazil-presidential-election-first-round-1st-place-in-santa-catarina
brazil-presidential-election-first-round-1st-place-in-espirito-santo
flavio-bolsonaro-participates-in-debate-before-first-round
lula-participates-in-debate-before-first-round
who-will-trump-endorse-for-president-of-brazil-20260803210809
next-brazil-senate-election-most-seats-won
brazil-chamber-of-deputies-election-winner
so-paulo-governor-election-winner
rio-de-janeiro-governor-election-winner-20260608202949176""".split()
out={}
print("FETCH UTC", datetime.datetime.utcnow().isoformat())
for s in slugs:
    r=subprocess.run(["curl","-sS","-m","30","https://gamma-api.polymarket.com/events?slug="+s],capture_output=True,text=True).stdout
    try: e=json.loads(r)[0]
    except Exception as ex: print("FAIL",s,ex); continue
    out[s]=e
    print(f"\n## {e['title']} | vol={e.get('volume',0):,.0f} liq={e.get('liquidity',0) or 0:,.0f} vol24h={e.get('volume24hr',0) or 0:,.0f} start={e.get('startDate','')[:10]}")
    rows=[]
    for m in e['markets']:
        if m.get('closed') and not m.get('active',True): pass
        try: p=json.loads(m.get('outcomePrices','[]'))
        except: p=[]
        name=m.get('groupItemTitle') or m['question']
        rows.append((float(p[0]) if p else -1,name,m.get('bestBid'),m.get('bestAsk'),m.get('lastTradePrice'),float(m.get('volume') or 0),m.get('closed')))
    rows.sort(reverse=True)
    tot=sum(r[0] for r in rows if r[0]>0)
    for r in rows:
        if r[0]>=0.005 or r[5]>500000: print(f"  {r[1][:45]:45s} yes={r[0]:.4f} bid={r[2]} ask={r[3]} last={r[4]} vol={r[5]:,.0f} closed={r[6]}")
    print(f"  soma YES={tot:.4f}")
json.dump(out,open("polymarket_events_snapshot.json","w"))
