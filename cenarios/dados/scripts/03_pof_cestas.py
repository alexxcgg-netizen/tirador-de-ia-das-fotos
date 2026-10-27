import json, pandas as pd
OUT='/home/user/tirador-de-ia-das-fotos/cenarios/dados/'
v={}
for f in ['pof6715.json','pof6972.json']:
    for r in json.load(open(f))[1:]:
        if r['V'] in ('-','...','X',''): val=0.0
        else: val=float(r['V'])
        # find class/type codes
        keys=[k for k in r if k.endswith('C') and k.startswith('D')]
        cl=[r[k] for k in keys if r[k] in ('7999','47558','47559','47560','47561','47562','47563','47564')][0]
        tp=r[keys[-1]]
        v[(cl,tp)]=val
w={}
for t in ['7060','7063']:
    for r in json.load(open(f'w{t}.json'))[1:]:
        w[(t,r['D4C'])]=float(r['V'])
classes=[('7999','Total',None,None),('47558','Ate R$1.908 (ate 2 SM de 2018)',0,2),('47559','R$1.908-2.862 (2-3 SM)',2,3),('47560','R$2.862-5.724 (3-6 SM)',3,6),('47561','R$5.724-9.540 (6-10 SM)',6,10),('47562','R$9.540-14.310 (10-15 SM)',10,15),('47563','R$14.310-23.850 (15-25 SM)',15,25),('47564','>R$23.850 (>25 SM)',25,None)]
fam={'7999':69017704,'47558':16737438,'47559':13079821,'47560':21099497,'47561':9509008,'47562':4256727,'47563':2629450,'47564':1705764}
# categoria, [pof codes], grupo IPCA, codigo IPCA (c315)
cats=[
('alimentacao_domicilio',['103626'],'1.Alimentação e bebidas > 11.Alimentação no domicílio','7171'),
('alimentacao_fora_domicilio',['103692'],'1.Alimentação e bebidas > 12.Alimentação fora do domicílio','7432'),
('habitacao_aluguel_monetario',['8007'],'2.Habitação > 2101001.Aluguel residencial','7448'),
('habitacao_aluguel_nao_monetario_imputado',['8008'],'(fora do IPCA: aluguel imputado de imóvel próprio/cedido)',None),
('habitacao_condominio',['8009'],'2.Habitação > 2101002.Condomínio','7449'),
('habitacao_energia_eletrica',['8018'],'2.Habitação > 2202.Energia elétrica residencial','7484'),
('habitacao_gas_domestico',['8022'],'2.Habitação > 2201004.Gás de botijão','7482'),
('habitacao_agua_esgoto',['8010'],'2.Habitação > 2103.Água e esgoto (taxa)',None),
('habitacao_manutencao_limpeza_outros',['8024','8025','8023'],'2.Habitação (reparos, artigos de limpeza, outros)',None),
('artigos_residencia',['8026','111442','8027'],'3.Artigos de residência','7486'),
('comunicacao_telefonia_internet',['8019','8020','8021','103606','103594'],'9.Comunicação','7786'),
('vestuario',['103554'],'4.Vestuário','7558'),
('transporte_publico_urbano',['103562'],'5.Transportes > 5101.Transporte público','7627'),
('transporte_combustivel',['103563','103564'],'5.Transportes > 5104.Combustíveis (veículos)','7656'),
('transporte_veiculo_manutencao',['8011'],'5.Transportes > 5102.Veículo próprio (manutenção/acessórios)',None),
('transporte_aquisicao_veiculos',['103566'],'5.Transportes > 5102.Veículo próprio (automóvel novo/usado, moto)',None),
('transporte_viagens_outros',['8012','103568'],'5.Transportes (passagem aérea, ônibus interestadual, outros)',None),
('saude_remedios',['103575'],'6.Saúde e cuidados pessoais > 6101.Produtos farmacêuticos','7662'),
('saude_plano',['103576'],'6.Saúde e cuidados pessoais > 6203.Plano de saúde','7696'),
('saude_outros',['103577','103578','8013','103580','103581','103582','103583','103584'],'6.Saúde e cuidados pessoais > 62.Serviços de saúde (exceto plano)',None),
('higiene_cuidados_pessoais',['103569'],'6.Saúde e cuidados pessoais > 6301.Higiene pessoal','7698'),
('educacao',['103585'],'8.Educação','7766'),
('recreacao_cultura',['103593','8015','8016','103597'],'7.Despesas pessoais > 72.Recreação, jogos e fumo',None),
('fumo',['103598'],'7.Despesas pessoais > Fumo',None),
('servicos_pessoais',['103599'],'7.Despesas pessoais > 71.Serviços pessoais','7713'),
('despesas_diversas',['103605','103607','103608','103609','103610'],'7.Despesas pessoais (jogos de azar, cerimônias, serviços profissionais, outros)',None),
('fin_servicos_bancarios',['103614'],'(outras despesas correntes; IPCA 7.Despesas pessoais > Serviços bancários)',None),
('fin_emprestimos_carne',['103623'],'(fora do IPCA) Diminuição do passivo: empréstimo e carnê (principal+juros)',None),
('fin_prestacao_imovel',['103624'],'(fora do IPCA) Diminuição do passivo: prestação de imóvel',None),
('impostos_contribuicoes',['103612','103613'],'(fora do IPCA) Impostos e contribuições trabalhistas',None),
('transferencias_previdencia_outras',['103615','103616','103617'],'(fora do IPCA) Pensões/doações, previdência privada, outras',None),
('aumento_ativo',['103618'],'(fora do IPCA) Aquisição/reforma de imóvel, investimentos',None),
]
rows=[]
for cl,nome,lo,hi in classes:
    tot=v[(cl,'103536')]; cons=v[(cl,'103538')]
    soma=0
    for cat,codes,ipca,ic in cats:
        val=sum(v[(cl,c)] for c in codes)
        rows.append(dict(classe_codigo=cl,classe_rendimento=nome,limite_inf_sm2018=lo,limite_sup_sm2018=hi,num_familias=fam[cl],
            categoria=cat,codigos_pof_tab=('6972:' if cat.startswith('alimentacao') else '6715:')+'+'.join(codes),
            despesa_media_mensal_rs_jan2018=round(val,2),pct_despesa_total=round(100*val/tot,2),pct_despesa_consumo=round(100*val/cons,2) if not cat.startswith(('fin_','impostos','transfer','aumento')) else None,
            grupo_ipca=ipca,codigo_ipca_c315=ic,peso_ipca_ago2026=w.get(('7060',ic)) if ic else None,peso_inpc_ago2026=w.get(('7063',ic)) if ic else None))
    rows.append(dict(classe_codigo=cl,classe_rendimento=nome,limite_inf_sm2018=lo,limite_sup_sm2018=hi,num_familias=fam[cl],categoria='TOTAL_despesa_consumo',codigos_pof_tab='6715:103538',despesa_media_mensal_rs_jan2018=cons,pct_despesa_total=round(100*cons/tot,2),pct_despesa_consumo=100.0))
    rows.append(dict(classe_codigo=cl,classe_rendimento=nome,limite_inf_sm2018=lo,limite_sup_sm2018=hi,num_familias=fam[cl],categoria='TOTAL_despesa_total',codigos_pof_tab='6715:103536',despesa_media_mensal_rs_jan2018=tot,pct_despesa_total=100.0))
df=pd.DataFrame(rows)
df.to_csv(OUT+'cestas_consumo_pof.csv',index=False)
# check sum of consumption cats vs consumo total
cc=df[~df.categoria.str.startswith(('fin_','impostos','transfer','aumento','TOTAL'))].groupby('classe_codigo').pct_despesa_consumo.sum()
print(cc)
print(df[df.classe_codigo.isin(['47558','47564'])][['classe_codigo','categoria','pct_despesa_consumo','pct_despesa_total']].to_string())
