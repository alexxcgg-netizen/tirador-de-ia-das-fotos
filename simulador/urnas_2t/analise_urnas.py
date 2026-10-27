"""Analise estatistica de todas as urnas do 2T (todas_secoes.csv). Uso: python3 -I analise_urnas.py
Grava urnas/relatorio_completo.md e urnas/analise_resumo.json. Descritivo: anomalia estatistica NAO e prova de fraude."""
import json
import numpy as np
import pandas as pd
from scipy import stats

S = '/tmp/claude-0/-home-user-tirador-de-ia-das-fotos/3c9b5811-fca5-51b3-ac00-75dbd87eaeac/scratchpad'
U = S + '/urnas'
df = pd.read_csv(U + '/todas_secoes.csv', dtype={'cd_mun': str, 'zona': str, 'secao': str})
df = df.drop_duplicates(['uf', 'cd_mun', 'zona', 'secao'])
for c in ['aptos', 'comparecimento', 'lula_13', 'flavio_22', 'brancos', 'nulos', 'hab_biometria',
          'compareceram_sem_biometria', 'soma_igual_comparecimento']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
R = {}
n = len(df)
R['secoes'] = n
R['lula'] = int(df.lula_13.sum()); R['flavio'] = int(df.flavio_22.sum())
R['validos'] = R['lula'] + R['flavio']
R['lula_pct'] = round(100 * R['lula'] / R['validos'], 2)
R['soma_diferente_comparecimento'] = int((df.soma_igual_comparecimento != 1).sum())
R['comparecimento_maior_que_aptos'] = int((df.comparecimento > df.aptos).sum())

# 1) ultimo digito dos votos de cada candidato (secoes com >=100 votos): deve ser ~uniforme
dig = {}
for col in ['lula_13', 'flavio_22']:
    x = df.loc[df[col] >= 100, col].astype(int) % 10
    obs = np.bincount(x, minlength=10)
    chi = stats.chisquare(obs)
    dig[col] = {'n': int(x.size), 'p_chi2': float(chi.pvalue), 'freq_pct': [round(100 * v / x.size, 2) for v in obs]}
R['ultimo_digito'] = dig

# 2) residuo da secao contra o municipio (binomial): assimetria dos extremos
df['v2'] = df.lula_13 + df.flavio_22
g = df.groupby(['uf', 'cd_mun'])
df['p_mun'] = g.lula_13.transform('sum') / g.v2.transform('sum')
df['nsec_mun'] = g.lula_13.transform('size')
m = (df.nsec_mun >= 10) & (df.v2 >= 50) & (df.p_mun.between(0.02, 0.98))
d = df[m].copy()
d['z'] = (d.lula_13 - d.v2 * d.p_mun) / np.sqrt(d.v2 * d.p_mun * (1 - d.p_mun))
R['residuo'] = {'secoes': int(len(d)), 'z_mediana': float(d.z.median()), 'z_desvio': float(d.z.std()),
                'z_gt_5_lula': int((d.z > 5).sum()), 'z_lt_m5_flavio': int((d.z < -5).sum()),
                'z_gt_8_lula': int((d.z > 8).sum()), 'z_lt_m8_flavio': int((d.z < -8).sum())}

# 3) secoes quase unanimes
big = df[df.v2 >= 100]
R['unanimes'] = {'lula_ge_99': int((big.lula_13 / big.v2 >= .99).sum()), 'flavio_ge_99': int((big.flavio_22 / big.v2 >= .99).sum()),
                 'lula_ge_95': int((big.lula_13 / big.v2 >= .95).sum()), 'flavio_ge_95': int((big.flavio_22 / big.v2 >= .95).sum())}

# 4) comparecimento
df['tx'] = df.comparecimento / df.aptos
ok = df[df.aptos >= 50]
R['comparecimento'] = {'media': round(float(ok.tx.mean()), 4), 'ge_98': int((ok.tx >= .98).sum()), 'eq_100': int((ok.tx >= 1).sum()),
                       'le_50': int((ok.tx <= .5).sum())}
mm = df.groupby(['uf', 'cd_mun']).agg(l=('lula_13', 'sum'), f=('flavio_22', 'sum'), c=('comparecimento', 'sum'), a=('aptos', 'sum'))
mm = mm[(mm.l + mm.f) >= 2000]
mm['pl'] = mm.l / (mm.l + mm.f); mm['tx'] = mm.c / mm.a
R['corr_comparecimento_pctlula_municipios'] = {'n': int(len(mm)), 'pearson': float(mm.tx.corr(mm.pl)), 'spearman': float(mm.tx.corr(mm.pl, method='spearman'))}

# 5) biometria
df['sem_bio'] = df.compareceram_sem_biometria / df.comparecimento.replace(0, np.nan)
R['sem_biometria'] = {'media_pct': round(100 * float(df.compareceram_sem_biometria.sum() / df.comparecimento.sum()), 2),
                      'secoes_ge_30pct': int((df.sem_bio >= .3).sum())}
mb = df.groupby(['uf', 'cd_mun']).agg(sb=('compareceram_sem_biometria', 'sum'), c=('comparecimento', 'sum'), l=('lula_13', 'sum'), f=('flavio_22', 'sum'))
mb = mb[mb.l + mb.f >= 2000]
R['corr_sembio_pctlula_municipios'] = float((mb.sb / mb.c).corr(mb.l / (mb.l + mb.f)))

# 6) horario de encerramento (hora local do BU)
enc = pd.to_datetime(df.encerramento_bu_local, format='%Y%m%dT%H%M%S', errors='coerce')
R['encerramento'] = {'apos_18h_local': int((enc.dt.hour >= 18).sum()), 'sem_horario': int(enc.isna().sum())}
R['flags'] = df['flags'].fillna('').str.split(';').explode().value_counts().head(10).to_dict()
R['flags'].pop('', None)

# por UF
pu = df.groupby('uf').agg(secoes=('secao', 'size'), l=('lula_13', 'sum'), f=('flavio_22', 'sum'))
pu['lula_pct'] = (100 * pu.l / (pu.l + pu.f)).round(2)
R['por_uf'] = pu[['secoes', 'lula_pct']].to_dict('index')

# extremos do residuo para inspecao
ext = d.reindex(d.z.abs().sort_values(ascending=False).index).head(15)
R['top_residuos'] = ext[['uf', 'municipio', 'zona', 'secao', 'lula_13', 'flavio_22', 'p_mun', 'z']].round(3).to_dict('records')
json.dump(R, open(U + '/analise_resumo.json', 'w'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in R.items() if k not in ('por_uf', 'top_residuos')}, ensure_ascii=False, indent=1, default=str))
