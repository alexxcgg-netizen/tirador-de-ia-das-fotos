"""Cruza 1T x 2T por secao (alvos_1t.csv: sinalizadas + amostra aleatoria). Uso: python3 -P analise_1t2t.py"""
import json
import numpy as np
import pandas as pd

S = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad'
U = S + '/urnas'
K = ['uf', 'cd_mun', 'zona', 'secao']
rd = lambda f: pd.read_csv(f, dtype={'cd_mun': str, 'zona': str, 'secao': str}).drop_duplicates(K)
a1 = rd(U + '/todas_secoes_1t.csv'); a2 = rd(U + '/todas_secoes.csv'); al = rd(U + '/alvos_1t.csv')
m = a1.merge(a2, on=K, suffixes=('_1', '_2')).merge(al[K + ['grupo']], on=K)
m['v1'] = m.lula_13_1 + m.flavio_22_1; m['v2'] = m.lula_13_2 + m.flavio_22_2
m = m[(m.v1 >= 30) & (m.v2 >= 30)].copy()
m['s1'] = m.lula_13_1 / m.v1; m['s2'] = m.lula_13_2 / m.v2
m['d'] = m.s2 - m.s1
m['tx1'] = m.comparecimento_1 / m.aptos_1; m['tx2'] = m.comparecimento_2 / m.aptos_2
# desvio do deslocamento da secao em relacao ao deslocamento do municipio (so da amostra, municipios com >=15 secoes na amostra)
g = m.groupby(['uf', 'cd_mun'])
m['d_mun'] = g.d.transform('median'); m['n_amostra_mun'] = g.d.transform('size')
m['res'] = m.d - m.d_mun
R = {'secoes_pareadas': int(len(m))}
for gr, x in m.groupby('grupo'):
    R[gr] = {'n': int(len(x)), 'share1_med': round(float(x.s1.median()), 4), 'share2_med': round(float(x.s2.median()), 4),
             'desloc_medio_pp': round(100 * float(x.d.mean()), 2), 'desloc_desvio_pp': round(100 * float(x.d.std()), 2),
             'tx1_med': round(float(x.tx1.median()), 4), 'tx2_med': round(float(x.tx2.median()), 4)}
am = m[m.grupo == 'amostra']
# ruido binomial esperado do deslocamento: sd ~ sqrt(p(1-p)(1/v1+1/v2))
p = (am.s1 + am.s2) / 2
am = am.assign(sd_bin=np.sqrt(p.clip(.02, .98) * (1 - p.clip(.02, .98)) * (1 / am.v1 + 1 / am.v2)))
am['zd'] = (am.d - am.d.median()) / am.sd_bin
R['amostra_zd'] = {'mediana': float(am.zd.median()), 'desvio': float(am.zd.std()),
                   'gt5': int((am.zd > 5).sum()), 'lt_m5': int((am.zd < -5).sum()),
                   'gt8': int((am.zd > 8).sum()), 'lt_m8': int((am.zd < -8).sum())}
# deslocamento por faixa de share no 1T (a regressao a media e esperada nos extremos)
am['faixa'] = pd.cut(am.s1, [0, .2, .4, .5, .6, .8, 1.0])
R['por_faixa_s1'] = am.groupby('faixa', observed=True).agg(n=('d', 'size'), desloc_pp=('d', lambda s: round(100 * s.mean(), 2)),
                                                           sd_pp=('d', lambda s: round(100 * s.std(), 2))).reset_index().astype({'faixa': str}).to_dict('records')
# sinalizadas: ja eram extremas no 1T?
sg = m[m.grupo == 'sinalizada']
R['sinalizadas'] = {
    'lula_ge95_2T': {'n': int((sg.s2 >= .95).sum()), 's1_med': round(float(sg[sg.s2 >= .95].s1.median()), 4),
                     'desloc_med_pp': round(100 * float(sg[sg.s2 >= .95].d.median()), 2)},
    'flavio_ge95_2T': {'n': int((sg.s2 <= .05).sum()), 's1_med': round(float(sg[sg.s2 <= .05].s1.median()), 4) if (sg.s2 <= .05).any() else None,
                       'desloc_med_pp': round(100 * float(sg[sg.s2 <= .05].d.median()), 2) if (sg.s2 <= .05).any() else None},
    'comp_ge_aptos': {'n': int((sg.comparecimento_2 >= sg.aptos_2).sum()), 'tx1_med': round(float(sg[sg.comparecimento_2 >= sg.aptos_2].tx1.median()), 4)}}
# maiores deslocamentos nao explicados (amostra)
top = am.reindex(am.zd.abs().sort_values(ascending=False).index).head(12)
R['top_desloc'] = top[['uf', 'cd_mun', 'zona', 'secao', 'lula_13_1', 'flavio_22_1', 'lula_13_2', 'flavio_22_2', 'zd']].round(2).to_dict('records')
json.dump(R, open(U + '/analise_1t2t.json', 'w'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R, ensure_ascii=False, indent=1, default=str))
