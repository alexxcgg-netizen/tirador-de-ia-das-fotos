# Modelo municipal do 2º turno (estrutura do 1º turno)

Terceira projeção do 2º turno de 2026 (Lula x Flávio Bolsonaro, 25/10), independente do `simulador/` e do
`modelo_alternativo/`. **Não usa pesquisas nem Polymarket/mercados.** A única entrada de 2026 é o resultado do 1º
turno em cada um dos 5.757 municípios (5.570 no Brasil e 187 cidades no exterior). O modelo aprende como, em 2018 e
2022, os votos do 1º turno de cada município se converteram em votos do 2º turno, e aplica isso a 2026.

```
python modelo_municipal/baixar_historico.py   # 2018/2022 (TSE dados abertos) -> data/hist_{ano}.csv
python modelo_municipal/baixar_2026.py        # 1º turno 2026 (TSE resultados) -> data/mun_2026_1t.csv
python modelo_municipal/rodar_mun.py          # validação + projeção + 500 mil simulações (~3 s)
python -m pytest modelo_municipal/tests       # 7 testes
```

## Resultado (1º turno 2026 totalizado, leitura de 5/10)

| | Modelo municipal | Simulador principal |
|---|---|---|
| Lula, % dos válidos (central) | **46,0%** | 47,14% |
| Intervalo de 95% | 40,5% a 51,6% | — |
| Desvio-padrão | 2,8 p.p. | — |
| **P(Lula vence)** | **8%** | 13% |
| Válidos no 2º turno | 119,0 mi | — |
| Comparecimento no 2º turno | 124,7 mi (78,5% dos aptos) | — |
| Votos projetados | Lula 54,8 mi, Flávio 64,2 mi | — |

Ponto de partida: no 1º turno Lula teve 45,16% dos válidos, Flávio 47,03%, e os terceiros 7,8%. Desses
terceiros, 7,6 p.p. são do bloco **não-esquerda** (Cury 2,9; Renan Santos 2,2; Caiado 2,2; Zema 0,3; outros) e só
0,17 p.p. de esquerda (PSTU, PCB, PCO, UP). Para virar, Lula precisaria de cerca de 62% dos votos dos terceiros. Em
2018 e 2022, o bloco equivalente de não-esquerda foi majoritariamente para o candidato da direita.

Por UF (fatia de Lula e P(Lula vence na UF)): BA 67,3% (100%), PI 71,8%, MA 65,2%, PE 64,5%, SE 64,1%,
CE 62,9%, PB 62,5%, RN 59,8%, AL 55,9% (97%), **PA 50,6% (58%)**, **AM 48,3% (28%)**, ZZ/exterior 47,6% (21%),
AP 46,6% (13%), MG 44,1% (2%), TO 43,9% (2%), RJ 40,1%, SP 39,7%, DF 39,1%, ES 38,3%, RS 36,1%, MS 35,3%,
GO 33,0%, PR 31,9%, MT 29,7%, AC 29,3%, SC 25,5%, RO 26,1%, RR 23,7%. Os números completos estão em
`resultados_municipal_2t.json` (`uf`).

## Método

### Dados
* **2018 e 2022**: `votacao_candidato_munzona_{ano}.zip` (votos por candidato) e `detalhe_votacao_munzona_{ano}.zip`
  (aptos, comparecimento, brancos, nulos), ambos do CDN de dados abertos do TSE. As linhas de Presidente ficam no
  membro `*_BR.csv`. O zip de 2022 tem 640 MB, então o script **não baixa os zips**: lê o diretório central do
  zip com requisições HTTP Range e extrai só o membro `_BR.csv`, de 2 a 3 MB comprimidos. Os totais conferem com
  os oficiais (2022: Lula 57,26 mi no 1º turno e 60,35 mi no 2º; 2018: Haddad 29,28% e 44,87%). Ficam só os CSVs
  compactos `data/hist_{ano}.csv`.
* **2026**: arquivos `{uf}{cdmun}-c0001-e006257-u.json` e a abrangência `{uf}-e006257-ab.json`, com no máximo 8
  conexões e retentativas com backoff em respostas 429. O cache bruto (`data/_raw_2026/`) não é versionado. O CSV
  `data/mun_2026_1t.csv` traz todos os candidatos (`c{número}`), brancos, nulos, comparecimento e `pst`. Cerca de 57
  municípios (1,2% do eleitorado) ainda não estavam 100% totalizados. Neles, as contagens são extrapoladas por
  `100/pst`.

### Modelo principal: inferência ecológica de Goodman com restrições (`EI6_uf`)
Em cada município, o eleitorado apto do 1º turno é dividido em 6 categorias, com frações `x` que somam 1:
PT, principal adversário, **terceiros de esquerda**, **terceiros de não-esquerda**, brancos+nulos e abstenção.
Os votos do 2º turno, como fração dos aptos, são modelados assim:

```
PT2/aptos  = Σ_j x_j · β_PT,j        OPP2/aptos = Σ_j x_j · β_OPP,j        0 ≤ β ≤ 1
```

`β_k,j` é a fração dos eleitores da categoria j que votou em k no 2º turno. O resto se absteve ou anulou, então o
mesmo modelo dá a fatia e os válidos. A estimação usa mínimos quadrados limitados (BVLS) ponderados pelo
eleitorado, em hierarquia: primeiro os coeficientes nacionais, depois cada UF com encolhimento (ridge, `lam` = 10
municípios médios) em direção aos nacionais. O exterior é tratado como uma "UF" (ZZ). O modelo final é treinado em
2018 e 2022 juntos. Coeficientes nacionais resultantes:

| categoria do 1º turno | → Lula/PT | → adversário |
|---|---|---|
| PT | 0,97 | 0,01 |
| adversário | 0,00 | 1,00 |
| terceiros de esquerda | 0,83 | 0,03 |
| terceiros de não-esquerda | 0,00 | 0,64 |
| brancos+nulos | 0,39 | 0,00 |
| abstenção | 0,00 | 0,04 |

A classificação dos terceiros é a seguinte:
* 2018, esquerda: Ciro, Marina, Boulos, Vera, Goulart.
* 2022, esquerda: Ciro, Vera, Sofia Manzano, Léo Péricles.
* 2026, esquerda: PSTU, PCB, PCO e UP.
* Todos os demais candidatos (Alckmin, Amoêdo, Meirelles, Álvaro Dias, Daciolo, Tebet, Soraya, D'Ávila, Kelmon,
  Caiado, Cury, Renan Santos, Zema etc.) formam o bloco de não-esquerda.

Separar os terceiros nesses dois blocos foi a escolha que mais melhorou a validação: com um bloco único, o erro
nacional ia de 5,3 para 2,8 p.p. de RMS. Ela também importa para 2026, porque quase todos os terceiros de agora são
de não-esquerda.

### Variantes comparadas (todas na validação e na projeção)
* `EI6_regiao_uf` (nacional → região → UF), `EI6_uf_porte` (UF → UF × porte do município, 4 faixas de eleitorado)
  e `EI6_nacional` (sem hierarquia).
* `EI5_*`: os terceiros num bloco só.
* `LOGIT_*`: regressão do logito da fatia de Lula no 2º turno sobre o logito da fatia bipartidária do 1º turno,
  peso dos terceiros (com interação), brancos/nulos, abstenção e log do eleitorado, com e sem efeitos de UF. Os
  válidos vêm de uma regressão linear.

### Validação deixando uma eleição de fora
Treino numa eleição e previsão da outra. Erro = previsto − real, em p.p. da fatia do PT nos válidos.

| variante | 2018→2022 nacional | 2022→2018 nacional | RMS nacional | RMS UF | RMS município | erro nos válidos (RMS) |
|---|---|---|---|---|---|---|
| **EI6_uf (principal)** | **+1,82** | **−3,50** | **2,79** | **2,87** | **3,10** | 2,7% |
| EI6_regiao_uf | +1,72 | −3,51 | 2,76 | 2,83 | 3,07 | 2,7% |
| EI6_uf_porte | +1,84 | −3,47 | 2,78 | 2,86 | 3,10 | 2,7% |
| EI6_nacional | +1,95 | −3,56 | 2,87 | 2,96 | 3,17 | 2,6% |
| EI5_uf | +2,40 | −7,15 | 5,33 | 5,84 | 6,20 | 1,4% |
| EI5_nacional | +2,71 | −7,22 | 5,45 | 6,10 | 6,44 | 1,3% |
| LOGIT_uf | +3,96 | −7,86 | 6,22 | 6,35 | 6,89 | 7,1% |
| LOGIT_sem_efeito | +4,06 | −8,08 | 6,39 | 6,57 | 7,12 | 5,3% |

Em ambos os sentidos, o modelo principal **acerta bem a geografia** e erra principalmente o **nível nacional**:
* 2018→2022: UF após remover o erro nacional, RMS 0,65 p.p.; dispersão regional 0,50; UF dentro da região 0,46;
  município dentro da UF 0,76 p.p. (ponderado por válidos).
* 2022→2018: os mesmos itens dão 1,47, 1,20, 0,88 e 1,50 p.p.

O erro nacional muda de sinal entre os dois sentidos: a taxa de transferência de cada bloco não é estável de uma
eleição para a outra. Os erros por UF do modelo principal estão em `validacao.EI6_uf.*.erros_uf_pp`.

Projeção de 2026 conforme o treino (EI6_uf): 2018 → 47,4%; 2022 → 46,0%; 2018 e 2022 juntos → 46,0%. As variantes
com bloco único de terceiros dão 47,5% a 50,0%, porque emprestam a 2026 a transferência de Ciro e Tebet, que é mais
favorável ao PT. Elas foram as que pior validaram.

### Incerteza
Os componentes vêm da validação, como a média quadrática dos dois sentidos:
* nacional: 2,79 p.p.;
* regional (5 regiões): 0,92 p.p.;
* UF dentro da região: 0,70 p.p.;
* município dentro da UF: 1,19 p.p.

Foram 500 mil simulações normais. O erro municipal, independente entre municípios, é agregado analiticamente por
UF, com variância `dp² · ΣV_i² / (ΣV_i)²`, sem sortear 5.757 × 500 mil números. No país ele vale só 0,09 p.p.
A P(Lula) por UF vem das mesmas simulações. O desvio nacional é estimado com **apenas dois pontos** (as duas
eleições de validação). Ele é grosseiro, mas é coerente com o tamanho dos erros observados.

### Sensibilidade: quanto do bloco não-esquerda vai para Lula
A inferência ecológica atribui **0%** do bloco não-esquerda a Lula, e 64% ao adversário. Esse número é suspeito. O
método confunde a transferência dos terceiros com a mobilização diferencial dos abstencionistas (por exemplo, a de
Bolsonaro em 2022) e com o efeito de composição dos municípios. Mantido o total desse bloco que vota no 2º turno,
mudando só a divisão:

| fração do bloco não-esquerda para Lula | 20% | 30% | 40% | 50% | 60% |
|---|---|---|---|---|---|
| Lula, % dos válidos | 47,0 | 47,5 | 48,0 | 48,5 | 49,0 |

Mesmo dando a Lula 60% desses votos, a projeção fica abaixo de 50%. Para Lula vencer, seria preciso também mudar
a mobilização (abstenção e brancos/nulos) a seu favor, como em 2018.

## Comparação com o modelo principal
O simulador principal dá 47,14% e P(Lula) = 13%. O modelo municipal, sem pesquisas nem mercados, dá **46,0% e
P = 8%**. Os dois estão do mesmo lado e a cerca de 1 p.p. de distância, bem dentro da incerteza deste modelo
(DP de 2,8 p.p.). A cena da sensibilidade com cerca de 20% do bloco não-esquerda indo para Lula reproduz quase
exatamente o simulador (47,0%).

## Limitações
* **Falácia ecológica.** Os β são associações agregadas entre municípios, não transferências individuais. Valores
  nos limites (0 ou 1) indicam que a restrição está ativa e que a causa é colinearidade, não um fato sobre os
  eleitores.
* **Só duas eleições de treino**, ambas com Bolsonaro como adversário e com composições de terceiros muito
  diferentes da de 2026. Em 2026 o bloco não-esquerda é mais à direita do que Tebet ou Alckmin. Não há como validar
  a transferência específica de Caiado, Cury, Renan Santos e Zema.
* A classificação esquerda × não-esquerda é uma escolha do autor. Ela foi feita antes de olhar a projeção de 2026,
  mas foi escolhida porque melhorou a validação.
* Não inclui nada que aconteça entre os turnos (campanha, apoios, debates, eventos), nem diferença de
  comparecimento por motivo novo. Os brancos+nulos do 2º turno usados no comparecimento seguem a taxa por UF de 2022.
* O DP nacional vem de dois erros de validação. As caudas reais podem ser maiores.
* Cerca de 1% do eleitorado estava em municípios com totalização parcial (extrapolada).

## Arquivos
* `resultados_municipal_2t.json`: P(Lula), média e quantis, válidos e comparecimento em milhões, UFs, validação
  completa, variantes, coeficientes e sensibilidade.
* `projecao_municipios_2t.csv`: por município, aptos, % do 1º turno, votos projetados de Lula e Flávio, válidos e
  % de Lula no 2º turno.
* `modelo_mun.py` (modelos, avaliação, simulação), `rodar_mun.py`, `baixar_historico.py`, `baixar_2026.py`, `tests/`.
* `data/hist_2018.csv`, `data/hist_2022.csv`, `data/mun_2026_1t.csv`: agregados municipais compactos.
