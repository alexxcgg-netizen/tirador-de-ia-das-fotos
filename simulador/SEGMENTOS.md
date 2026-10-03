# Módulo de segmentos (`segmentos.py`)

Leva a segmentação do eleitorado (renda/classe, idade, escolaridade, religião,
gênero, região, Bolsa Família) para dentro do modelo, e não só para o
briefing. O módulo é independente: **não altera `modelo.py`, `rodar.py` nem
`web/`**. A integração está descrita no fim deste documento.

Dados até 3/10/2026. Todos os números têm fonte (TSE, IBGE, MDS, Datafolha,
Quaest, AtlasIntel) ou estão marcados como cálculo ou inferência.

```bash
python simulador/segmentos.py                 # regenera os arquivos em data/ (~40 s)
python simulador/segmentos.py caminho/perfil_comparecimento_abstencao_2022.zip   # reagrega o TSE antes
python -m pytest simulador/tests/test_segmentos.py -q
```

## Arquivos

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `data/covariaveis_uf.csv` (entrada) | Covariáveis por UF: famílias no Bolsa Família por 100 eleitores (MDS, set/2026), % evangélicos, católicos e sem religião, % brancos, pardos e pretos, % urbana (Censo 2022), renda per capita e Gini (PNAD 2025), e o perfil do eleitorado TSE 2026 (% mulheres, 16–17, 60+, 70+, analfabeto ou "lê e escreve", até fundamental incompleto, superior completo) | cópia de `research_notes/.../demografia_uf.csv` e da tabela por UF de `segmentacao_eleitorado.md` |
| `data/prior_demografico_uf.csv` | Prior por UF e turno: simples, demográfico, misto, dp, discrepância e as covariáveis | `prior_demografico_uf()` |
| `data/abstencao_segmentos_uf.csv` | 2022, UF (27 + ZZ) × turno × 8 faixas etárias × 5 escolaridades × gênero: aptos, comparecimento, abstenção | TSE `perfil_comparecimento_abstencao_2022.zip`, agregado por `agregar_perfil_comparecimento()`. O zip bruto (201 MB) foi apagado |
| `data/ajuste_comparecimento_uf.csv` | 2026, UF + BR × turno: ajuste de comparecimento (p.p. e logito), dp, p5–p95 e valor central | `ajuste_comparecimento_2026()` |
| `data/segmentos_voto.json` | Voto por segmento (2022 2º turno × 2026 1º turno), tamanhos dos segmentos, abstenção de 2022 por segmento e ajuste nacional | `decomposicao_segmentos()` |

---

## (a) Prior demográfico por UF

### Método
- **Alvo:** lean do PT na UF, em logito: `logito(fatia na UF) − logito(fatia nacional)`.
  - No 2º turno, a fatia é a % de válidos do PT.
  - No 1º turno, é PT/(PT + 2º colocado), a mesma definição de `modelo.carregar_ufs`.
  - Anos usados: 2014, 2018 e 2022 (TSE).
- **Covariáveis** (7, padronizadas):
  - famílias no Bolsa Família por 100 eleitores;
  - % evangélicos;
  - % brancos;
  - log da renda per capita;
  - % urbana;
  - % de eleitores com 60 anos ou mais (TSE 2026);
  - % de eleitores com superior completo (TSE 2026).
- **Modelo:** ridge com intercepto sem penalização. O λ é escolhido por leave-one-out (LOO) na grade 0,3–30 e ficou em λ = 1. O RMSE do LOO foi calculado com λ escolhido de forma aninhada.
- **Validação fora do tempo:** é o teste que importa para 2026, porque o prior de 2026 usa o lean de 2022.
  - Prever o lean de 2022 com o que se sabia depois de 2018.
  - Prever o lean de 2018 com o que se sabia depois de 2014.
  - Os erros são RMSE entre as 27 UFs, em p.p. da fatia do PT.
- **Prior misto:** `w × (0,85 × lean anterior) + (1 − w) × demográfico`.
  - O peso w minimiza a média do RMSE nas duas transições, numa grade de 0,50 a 1,00.
  - O dp do prior é o RMSE fora do tempo do misto, somado em quadratura à incerteza de previsão do ridge para a UF.

### Resultados (RMSE em p.p. da fatia do PT, 27 UFs)

| Teste | 2º turno | 1º turno (fatia bipartidária) |
|---|---|---|
| LOO transversal: demografia → lean 2022 | **7,8** (R² LOO 0,70) | 8,1 (R² 0,69) |
| LOO transversal: demografia → lean 2018 | 7,8 (R² 0,77) | 8,1 (R² 0,79) |
| **Simples 0,85 × lean 2018 → 2022** (regra atual do `modelo.py`) | **4,1** | 6,0 |
| Persistência 1,0 × lean 2018 → 2022 | 4,9 | 7,2 |
| Demográfico (treinado em 2018) → 2022 | 7,1 | 8,9 |
| Simples 0,85 × lean 2014 → 2018 | 6,7 | 7,7 |
| Demográfico (treinado em 2014) → 2018 | 7,5 | 8,0 |
| **Peso ótimo do simples, w** | **1,00** | **0,80** |
| Misto 2018 → 2022 | 4,1 | 6,2 |
| Misto 2014 → 2018 | 6,7 | 7,3 |
| Correlação entre os erros do simples e do demográfico (2022) | 0,71 | 0,75 |

**Leitura**
- **A demografia explica cerca de 70% da variância do mapa entre UFs.**
  - Efeitos por 1 dp da covariável, em logito, 2º turno:
    - evangélicos −0,37;
    - log da renda −0,27;
    - brancos −0,27;
    - 60+ +0,26;
    - Bolsa Família +0,23;
    - superior +0,11;
    - urbana +0,10.
  - Esses efeitos são correlações ecológicas entre UFs, não efeitos causais.
- **Ainda assim, a demografia prevê o lean da eleição seguinte pior que o lean anterior encolhido** (2º turno: 7,1 contra 4,1 p.p.).
  - Os erros dos dois são muito correlacionados (0,7).
  - No 2º turno, a combinação ótima é **w = 1**: o prior misto é igual ao prior simples.
  - No 1º turno, a demografia recebe peso de 20%, e o ganho é pequeno e instável:
    - de 7,7 para 7,3 p.p. em 2014→2018;
    - de 6,0 para 6,2 p.p. em 2018→2022, ou seja, piora.
  - O teste tem só duas transições, e 2018 foi um realinhamento. Por isso o valor de w é frágil.
- **Conclusão:** o prior atual do `modelo.py` (0,85 × lean de 2022) já é o melhor prior disponível. A regressão demográfica serve principalmente como **checagem**. A coluna `discrepancia_pp` (demográfico − simples) mostra onde o voto de 2022 destoa do perfil da UF:
  - **RR** +15: a demografia "esperaria" a UF bem menos antipetista;
  - **AL** +8;
  - **PA, AM, TO** −5 a −7;
  - **DF** −7;
  - **AP** −5.
- **UFs com pesquisas fracas:**
  - **AP:** no 2º turno, o prior simples dá −1,9 p.p. e o demográfico −6,8. A Quaest-AP de 1º turno (32 × 36, fatia de 47%, cerca de −4,6 p.p. em relação à média nacional de 51,6%) fica entre os dois, mais perto do demográfico. Há indício de que o lean de 2022 superestima o PT no AP.
  - **GO:** no 2º turno, o prior simples dá −8,2 e o demográfico −10,5. A diferença é pequena.
- **dp do prior** (em p.p. no nível nacional de 2022):

  | Turno | Conservador (inclui o realinhamento de 2018) | Recente (só 2018→2022) |
  |---|---|---|
  | 2º | 6,2 | 4,5 |
  | 1º | 8,0 | 7,0 |

  O `modelo.py` usa 4,0 nos dois turnos. **Isso é otimista para o 1º turno**, cujo lean é mais volátil (RMSE do simples de 6,0 em 2018→2022).

---

## (b) Comparecimento por segmento e ajuste de comparecimento

### Dados de abstenção (TSE 2022, agregação própria)
- **Arquivo:** `perfil_comparecimento_abstencao_2022.zip`, de 201 MB.
  - O zip não tem arquivo próprio para o DF. Por isso a agregação usa o `*_BRASIL.csv`, que traz as 27 UFs e o exterior.
- **Conferência com o TSE:**
  - Aptos: 156.384.048, contra 156.454.011 oficiais.
  - A abstenção por UF bate com `resultados_uf_2002_2022.csv` até 0,03 p.p.
  - No exterior (ZZ) a diferença é de 4,5 p.p. Por isso o ZZ fica fora do modelo de segmentos.
- **Abstenção no 1º turno de 2022:**
  - Por idade: 16–17 17%; 18–24 21%; 25–34 21%; 35–44 16%; 45–59 13%; 60–69 14%; **70–79 47%**; **80+ 82%**. O grupo 60+ soma 34,4%, igual aos 34,5% citados pela Gazeta do Povo.
  - Por escolaridade: analfabeto ou "lê e escreve" 39%; fundamental incompleto 24%; fundamental completo ou médio incompleto 21%; médio completo 15%; superior 13%.
  - Por gênero: mulheres 19,8%; homens 21,9%.

### Método do ajuste
1. **Células.** Cada célula é UF × faixa etária × escolaridade × gênero (cerca de 2.000 por turno). Cada uma tem aptos e taxa de comparecimento de 2022.
   - Para 2026, os aptos são reponderados (raking) ao eleitorado TSE 2026 de cada UF: total, 16–17/18–59/60–69/70+, escolaridade e % de mulheres.
   - A taxa de comparecimento de cada célula continua a de 2022.
2. **Voto por célula.** `logito p = região + desvio da UF na região + idade + escolaridade + gênero`.
   - O desvio da UF é o seu lean de 2022 menos o da sua região.
   - Os efeitos são calibrados no logito para que a média ponderada pelos **aptos** reproduza as margens publicadas: as pesquisas representam o eleitorado apto, sem filtro de eleitor provável.
   - Cada dimensão é deslocada por uma constante em logito, para que todas impliquem o mesmo total. A composição do cadastro difere da amostra (o cadastro tem 37% com "fundamental", contra 28% na amostra Datafolha). Esse deslocamento preserva os contrastes.
   - Mapeamento das categorias:
     - escolaridade: analfabeto até fundamental completo → "fundamental"; médio incompleto e completo → "médio"; superior incompleto e completo → "superior";
     - idade: 16–17 e 18–24 → "16–24"; 60–69, 70–79 e 80+ → "60+".
3. **Ajuste.** `ajuste = p(votantes) − p(aptos)` na UF, em que os votantes são os aptos × a taxa de comparecimento.
4. **Incerteza** (400 sorteios). Em cada sorteio:
   - escolhe-se a fonte de voto por segmento;
   - as margens recebem erro amostral (n do segmento, deff 1,5) mais 1 p.p. de erro não amostral;
   - aplica-se um fator κ ~ U(0,7; 1,0), que encolhe o desvio de abstenção de cada célula. É uma inferência: parte da abstenção de 80+ e de analfabetos vem de eleitores falecidos ou que mudaram e continuam no cadastro, e as pesquisas não entrevistam essas pessoas;
   - soma-se ruído de dp 0,10 no logito do comparecimento por faixa × escolaridade, para cobrir mudanças entre 2022 e 2026.
5. **Fontes de voto por segmento:**
   - 1º turno de 2026: Datafolha 15–17/09/2026, com a fatia Lula/(Lula + Flávio) calculada dos votos totais;
   - 2º turno de 2026: mistura 50/50 desse Datafolha com o Datafolha 28–29/10/2022 do 2º turno. Não há cruzamentos de 2º turno de 2026 nas notas.

### Resultado para 2026 (p.p. na fatia de Lula entre os dois; negativo = favorece Flávio)

| | 1º turno (fatia p2) | 2º turno (fatia q) |
|---|---|---|
| **Brasil** | **−0,37** (dp 0,17; p5–p95 −0,64 a −0,10; central −0,42) | **−0,25** (dp 0,16; −0,55 a −0,03; central −0,30) |
| Faixa entre UFs | −0,55 (RJ, SP, MG, RS) a −0,15 (RR, PI) | −0,41 a −0,13 |

**Mecanismo.** Quem se abstém mais (70+, analfabetos, fundamental incompleto, 18–34) pende para Lula nas pesquisas. Em 2026 o grupo 60+ também está mais pró-Lula (Datafolha: 43 × 33). O efeito é maior nas UFs mais velhas do Sudeste e do Sul. Ele é **pequeno e quase uniforme**: funciona sobretudo como um deslocamento nacional de 0,25 a 0,4 p.p.

### Validação em 2022

O teste aplica às pesquisas finais de 2022 o ajuste estimado com o comparecimento real de 2022 e os gradientes do Datafolha de 2022.

| Turno | Ajuste nacional | Média de 14 (2T) / 12 (1T) pesquisas: erro antes → depois | Média de 6 grandes institutos* | Datafolha | Institutos que melhoram |
|---|---|---|---|---|---|
| 2º | −0,19 p.p. (dp 0,09) | +0,11 → −0,08 | +1,92 → +1,72 | +1,20 → +1,01 | 8 de 14 |
| 1º | −0,18 p.p. (dp 0,09) | +1,22 → +1,05 | +4,39 → +4,21 | +5,66 → +5,48 | 9 de 12 |

\* Datafolha, Ipec, Quaest, AtlasIntel, PoderData e Ipespe.

- **O ajuste vai na direção certa.** Em 2022 as pesquisas tradicionais superestimaram Lula, e o ajuste corrige no mesmo sentido.
- **Mas o efeito é pequeno:** explica cerca de 10% do erro dos grandes institutos no 2º turno e 4% no 1º.
- **Datafolha 2T por recorte:** o erro melhora em 5 de 8 recortes (SE, S, NE, SP, MG) e piora nos 3 em que o Datafolha tinha subestimado Lula (CO, N, RJ). Isso é esperado de um deslocamento quase uniforme.
- **Conclusão:** o comparecimento diferencial por idade, escolaridade e gênero **não explica** o erro de 2022 no 1º turno (≈5–8 p.p. em Bolsonaro). O maior candidato a explicação continua sendo a mudança tardia de voto ou a não resposta diferencial (README, cenário "viés histórico").
- **Ressalva:** o Datafolha 2022 fornece os gradientes por segmento e também é uma das pesquisas corrigidas. O ajuste, porém, depende só dos contrastes entre segmentos, não do nível da pesquisa.

---

## (c) Decomposição por segmento (`segmentos_voto.json`)

Estrutura:
```json
{
  "titulo": "...",
  "data_referencia": "2026-10-03",
  "totais": {"voto_2022_2t": {...}, "voto_2026_1t": {...}, "abstencao_2022_1t_pct": 20.91},
  "fontes": {...}, "avisos": [...],
  "ajuste_comparecimento_nacional_2026": {"turno_1": {...}, "turno_2": {...}},
  "dimensoes": [
    {"dimensao": "genero", "rotulo": "Gênero", "categorias": [
      {"categoria": "Mulheres", "tamanho_pct": 52.84, "fonte_tamanho": "TSE 2026",
       "voto_2022_2t": {"lula": 55, "bolsonaro": 45, "margem_lula": 10},
       "voto_2026_1t": {"lula": 41, "flavio": 32, "margem_lula": 9, "fatia_lula_2p": 56.2},
       "outras_2026": [{"pesquisa": "AtlasIntel ...", "lula": 57.4, "adversario": 32.9, "fonte_url": "..."}],
       "abstencao_2022_1t_pct": 19.8, "abstencao_2022_2t_pct": 19.7}]}
  ]
}
```

**Dimensões e fonte do tamanho de cada segmento**

| Dimensão | Fonte do tamanho |
|---|---|
| Gênero | TSE 2026 |
| Idade | TSE 2026 |
| Escolaridade | TSE 2026 (do cadastro) |
| Renda familiar | amostra Datafolha 2022 |
| Religião | Censo 2022 |
| Região | TSE 2026 |
| Bolsa Família | amostra Datafolha 2022 e MDS |

- **Abstenção de 2022 por segmento:** incluída para gênero, idade e escolaridade.
- **Aviso, que o painel deve exibir:** o 2022 é o 2º turno em votos válidos e o 2026 é o 1º turno em votos totais. Compare a ordem e o sinal das margens, não o tamanho.

---

## Interface para integração em `modelo.py`

### Funções

| Função | Entrada | Saída |
|---|---|---|
| `carregar_covariaveis()` | `data/covariaveis_uf.csv` | DataFrame com índice nas 27 UFs e as 7 covariáveis |
| `carregar_leans()` | `data/resultados_uf_2002_2022.csv` | `({(ano, turno): Series lean_logito}, {(ano, turno): fatia nacional})` |
| `validar_prior_demografico(turno)` | — | dict com os RMSEs, w, λ e o dp do misto |
| `prior_demografico_uf(turno)` | — | DataFrame de 27 linhas (colunas abaixo) |
| `coeficientes_prior(turno)` | — | dict com os coeficientes (logito por dp) |
| `agregar_perfil_comparecimento(zip)` | zip do TSE | grava `abstencao_segmentos_uf.csv` |
| `carregar_abstencao_segmentos()` / `abstencao_por_segmento(cel, por, turno)` | CSV | tabelas de abstenção |
| `montar_celulas(cel, turno)` / `projetar_celulas_2026(c)` | — | células com `aptos`, `comp_taxa` e `regiao` |
| `ajustar_modelo_voto(celulas, fonte, lean_uf)` | `FONTES_VOTO[...]` | efeitos e p por célula |
| `ajuste_comparecimento(celulas, fontes, lean_uf, n_sorteios)` | — | DataFrame por UF + BR |
| `ajuste_comparecimento_2026()` | — | o conteúdo de `ajuste_comparecimento_uf.csv` |
| `validar_comparecimento_2022()` | — | dict com as validações acima |
| `decomposicao_segmentos()` | — | dict pronto para JSON |
| `gerar_arquivos()` | — | grava os arquivos de saída e devolve as validações |

### Colunas principais

**`prior_demografico_uf.csv`**: chave `(turno, uf)`, com turno 1 = fatia p2 e turno 2 = fatia q.
- `prior_misto_logito` e `dp_prior_logito`, ou `dp_prior_recente_logito`;
- `prior_simples_logito` (= 0,85 × lean 2022, idêntico ao atual);
- `prior_demografico_logito` e `discrepancia_pp`.

**`ajuste_comparecimento_uf.csv`**: chave `(turno, uf)`, com 27 UFs + `BR`.
- `ajuste_logito` e `dp_ajuste_logito`;
- `ajuste_pp`, `dp_ajuste_pp`, `ajuste_central_pp`.

### Como encaixar (sugestão; quem decide é quem integra)

1. **Prior da UF** (`construir_base`, onde hoje está `pr1 = expit(logit(p2_nat) + f * r.lean1_logit)`):
   ```python
   pri = pd.read_csv(DADOS / "prior_demografico_uf.csv").set_index(["turno", "uf"])
   pr1 = float(expit(logit(p2_nat) + pri.loc[(1, r.uf), "prior_misto_logito"]))
   pr2 = float(expit(logit(q_nat)  + pri.loc[(2, r.uf), "prior_misto_logito"]))   # = simples (w = 1)
   sdp1 = pri.loc[(1, r.uf), "dp_prior_recente_pp"] / 100    # 7,0 p.p. (hoje 4,0)
   sdp2 = pri.loc[(2, r.uf), "dp_prior_recente_pp"] / 100    # 4,5 p.p.
   ```
   - No 2º turno, o centro não muda. O que muda é só o dp, se for adotado.
   - No 1º turno, o centro muda pouco (diferença média absoluta de 0,7 p.p.; máximo de 2,8 p.p., em RR) e o dp sobe.
   - O efeito é maior nas UFs sem pesquisa ou com pesquisa fraca: AP e o 2º turno de GO.
   - Para apenas checar, mostre `discrepancia_pp` no painel e não altere nada.
2. **Comparecimento** (em `construir_base`, depois da calibração; `ufs` está na ordem de `eleitorado_uf_2026.csv`):
   ```python
   aj = pd.read_csv(DADOS / "ajuste_comparecimento_uf.csv").set_index(["turno", "uf"])
   a1 = ufs.uf.map(lambda u: aj["ajuste_logito"].get((1, u), aj.loc[(1, "BR"), "ajuste_logito"])).values
   a2 = ufs.uf.map(lambda u: aj["ajuste_logito"].get((2, u), aj.loc[(2, "BR"), "ajuste_logito"])).values
   p2_cal = expit(logit(p2_cal) + a1)
   q_cal  = expit(logit(q_cal) + a2)
   ```
   - A linha do exterior (ZZ) recebe o valor de BR.
   - **Incerteza:** dp nacional de cerca de 0,17 p.p. Pode ser somada em quadratura ao `erro_nacional_1t.dp_p2_pp`, mas é desprezível diante de 3,5.
   - **Interruptor:** sugerimos `premissas.json → comparecimento.ajuste_segmentos` (true/false), com origem "cálculo (TSE 2022 + Datafolha)".
3. **Cenário "viés histórico":** o erro histórico de 2014/18/22 já inclui qualquer efeito de comparecimento que tenha existido. Aplicar o ajuste nos dois cenários conta duas vezes cerca de 0,2 p.p. Há duas opções:
   - aplicar só no cenário neutro;
   - aplicar nos dois e reduzir `vies_2t_lula_media_pp` em 0,2.
4. **Painel:** ler `segmentos_voto.json` e exibir uma tabela ou gráfico de margens por segmento, 2022 × 2026, com o tamanho de cada segmento e os avisos.

---

## Limitações
- **Prior:**
  - São só 27 UFs e duas transições fora do tempo. O peso w e o dp são estimativas grosseiras.
  - As covariáveis são de 2022–2026 e foram usadas também para "prever" 2018, o que gera anacronismo.
  - As correlações são ecológicas.
  - O Bolsa Família por eleitor e a renda são quase colineares; o ridge reparte o efeito entre os dois.
- **Comparecimento:**
  - A escolaridade do cadastro TSE é declarada no alistamento e fica desatualizada. O mapeamento para as categorias das pesquisas é aproximado.
  - Não há comparecimento por renda, religião ou Bolsa Família (o TSE não coleta). Esses segmentos entram no prior (via UF) e na exibição, mas não no ajuste.
  - Brancos e nulos diferenciais por segmento não são modelados.
  - O modelo de voto é aditivo, sem interações (ex.: idade × escolaridade).
  - As margens de 2026 vêm de uma única pesquisa (Datafolha, n = 2.002), e os pesos dos segmentos de 2026 foram aproximados pelo TSE.
  - O fator κ (cadastro "inflado") é inferência.
  - O comparecimento por célula de 2026 é suposto igual ao de 2022. O transporte gratuito em 2026 e a polarização podem mudá-lo.
  - O ZZ fica fora do ajuste.
- **Decomposição:**
  - 1º turno de 2026 contra 2º turno de 2022, em bases diferentes.
  - Segmentos com n pequeno.
  - Em evangélicos e gênero, os institutos divergem muito (presencial × online).
- **Neutralidade:** o módulo só reorganiza dados publicados e não escolhe lado.
  - O ajuste de comparecimento favorece Flávio em cerca de 0,3 p.p. porque é isso que os dados do TSE e os cruzamentos das pesquisas indicam.
  - A validação mostra que esse efeito é pequeno e que, sozinho, não reproduz o erro histórico das pesquisas.
