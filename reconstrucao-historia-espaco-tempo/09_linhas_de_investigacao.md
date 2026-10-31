# Etapa 7 — Linhas de investigação

Pergunta-mãe: **que representação dos observáveis gravitacionais recupera o máximo da história física de
um sistema, e o que nunca pode ser recuperado?** A etapa 6 (`07_binarias_reais.md`) mostrou que as
quatro memórias integradas, num observador, deixam famílias contínuas de binárias indistinguíveis.
Esta etapa ataca o problema por 18 linhas independentes. Cada uma tem uma pergunta concreta, uma
hipótese, a matemática necessária, um teste e a contribuição que poderia render.

Classificação: **potencial científico** (A = pode render teorema ou observável novo; B = resultado útil,
provavelmente parcial; C = exploratório) e **viabilidade** aqui (alta = dá para testar com os modelos
instalados; média = exige aproximações; baixa = depende de dados ou código indisponíveis). A coluna
"Agente" indica quem desenvolveu a linha na etapa 7 (`linhas/`). Resultados e status estão no
`banco_de_hipoteses.md` e em `10_identificabilidade_e_informacao.md`.

| Linha | Área principal | Potencial | Viabilidade | Agente |
|---|---|---|---|---|
| L01 Teorema de identificabilidade no observador | geometria diferencial, RG | A | alta | D1 |
| L02 Geometria e topologia das fibras degeneradas | topologia, sistemas dinâmicos | A | alta | D1 |
| L03 Janelas múltiplas e a curva de energia de ligação | RG, PN, análise | A | alta | D2 |
| L04 Desenho ótimo de janelas | matemática aplicada, estatística | A | alta | D2 |
| L05 Informação de Fisher e Cramér-Rao da memória sozinha | estatística, teoria da informação | A | alta | D3 |
| L06 Informação mútua e aprendizado de máquina | teoria da informação, IA | B | alta | D3 |
| L07 O que um detector mede de fato | óptica, interferometria | B | alta | D3 |
| L08 Recuperação exata de fase pelos fluxos | análise harmônica, sistemas dinâmicos | A | alta | D5 |
| L09 Memória no *ringdown* | RG, teoria de perturbações | B | alta | D5 |
| L10 Precessão: multipolos $m\neq0$ e spins no plano | RG, BMS | A | média | D6 |
| L11 Zeros da memória no céu (Poincaré–Hopf) | topologia | B | média | D6 |
| L12 Limites para a memória pelo teorema da área | termodinâmica de buracos negros | B | alta | D4 |
| L13 Canais não gravitacionais: núcleo e degenerescência | teoria de campos, astrofísica | B | alta | D4 |
| L14 Janelas × momentos (memórias superiores) | matemática aplicada | B | alta | D7 |
| L15 Generalização do Teorema 1 a outros campos | teoria de campos | C | alta | D7 |
| L16 Excentricidade: dimensão da família e anomalia | RG, PN, EOB | B | alta | D8 |
| L17 Estrelas de nêutrons: marés na memória | astrofísica nuclear | B | média | D8 |
| L18 Cargas suaves como informação (BMS e quântica) | BMS, mecânica quântica | C | média | D1 (parte) |

---

## L01 — Teorema de identificabilidade no observador

- **Pergunta.** Qual é o posto do jacobiano do mapa $F:(M,q,\chi_1,\chi_2,D,\iota)\mapsto$ (quatro
  memórias num observador)? Onde ele cai? Quais direções formam o espaço nulo?
- **Hipótese.** O posto é 4 para ângulos genéricos. Cai em $\iota=\pi/2$ (spin e giroscópica são ímpares
  sob $\iota\to\pi-\iota$) e em $\iota=0$ (os harmônicos ${}_{-2}Y_{\ell0}$ se anulam nos polos; só a
  giroscópica sobrevive). O espaço nulo mistura parâmetros intrínsecos com $(D,\iota)$.
- **Problema que resolve.** A etapa 6 supôs posto 4 sem calculá-lo.
- **Fundamentação.** Teorema da função implícita e teorema do posto constante. A paridade dos
  harmônicos com peso de spin dá ${}_{s}Y_{\ell0}(\pi-\iota)=(-1)^{\ell+s}{}_{s}Y_{\ell0}(\iota)$.
- **Matemática.** Jacobiano por diferenças finitas sobre uma grade do espaço de parâmetros, SVD,
  menores e análise de paridade.
- **Teste.** Grade em $(q,\chi_1,\chi_2,\iota)$; posto numérico com limiar relativo ao piso numérico.
  Repetir com $\iota$ conhecido (contraparte eletromagnética) e com $(\iota,D)$ conhecidos.
- **Contribuição possível.** Um teorema de identificabilidade local, com os loci de degenerescência
  explícitos, e a resposta quantitativa para observações multimensageiras.
- **Hipótese já testada (fora do agente).** "As memórias de um observador medem o orçamento de cargas
  ($M_f$, $E$ e $J$ irradiados)": **refutada**. Ao longo da família do exp07, $M_f$ muda até 14% e $E$
  irradiada até 14%; a inclinação e a distância compensam.

## L02 — Geometria e topologia das fibras degeneradas

- **Pergunta.** Qual é a forma global de $F^{-1}(F(A))$: dimensão, extensão, bordas, componentes conexas?
- **Hipótese.** A fibra é uma superfície conexa, parametrizável por $(q_B,\chi_{2B})$, com borda onde
  $|\chi_1|$ atinge o limite do domínio. Não há componentes isoladas (soluções "distantes").
- **Problema que resolve.** Identificabilidade **global**, não só local.
- **Fundamentação.** Continuação numérica de variedades implícitas; teorema de Sard.
- **Matemática.** Resolver em grade de $(q_B,\chi_{2B})$; continuação por pseudo-comprimento de arco;
  busca com muitas partidas aleatórias por soluções fora da componente principal.
- **Teste.** Mapa da região de existência; contagem de soluções por ponto.
- **Contribuição possível.** Primeiro mapa explícito de uma fibra degenerada de memórias para binárias
  reais.

## L03 — Janelas múltiplas e a curva de energia de ligação

- **Pergunta.** O que exatamente uma segunda janela acrescenta?
- **Hipótese.** A memória acumulada entre duas frequências é a energia (e o momento angular) irradiada
  na banda, isto é, diferenças da energia de ligação $E_b(f)$ e do momento angular orbital $L(f)$,
  ligadas pela primeira lei $dE=\Omega\,dL$. Consequências:
  - na ordem PN dominante, as diferenças de janela só veem $\mathcal M^{5/3}/D$, como a amplitude
    oscilatória;
  - $\eta$ aparece em 1PN e a combinação spin-órbita em 1,5PN;
  - cada janela extra acrescenta cerca de dois números, não quatro.
- **Problema que resolve.** Explica por que as janelas quebram a degenerescência e quanto.
- **Fundamentação.** Balanço de energia e de momento angular; expansão PN de $E_b(x)$ [Blanchet2024].
- **Matemática.** Derivar $m_k(f)$ (memória de tipo $k$ acumulada desde $f$) e $dm_k/df$; posto dos
  jacobianos com $K$ janelas.
- **Teste.** Jacobianos $4K\times6$ para $K=1,\dots,4$; comparar com a previsão PN.
- **Contribuição possível.** Uma "espectroscopia de energia de ligação" pela memória.

## L04 — Desenho ótimo de janelas

- **Pergunta.** Quais frequências de início e fim maximizam a identificabilidade? Quantas janelas
  bastam? O ótimo é universal ou depende da fonte?
- **Hipótese.** Duas janelas bastam para tornar o mapa localmente injetivo (posto 6). As fronteiras
  ótimas são universais em $Mf$ e, portanto, escalam como $1/M$ em Hz.
- **Fundamentação.** Desenho ótimo de experimentos: critérios D (determinante) e E (menor valor
  singular) da informação de Fisher.
- **Teste.** Otimização das fronteiras para 4 fontes diferentes; comparar os ótimos em $Mf$.
- **Contribuição possível.** Uma prescrição prática de análise de memória por bandas.

## L05 — Informação de Fisher e Cramér-Rao da memória sozinha

- **Pergunta.** Com ruído realista (aLIGO, ET, CE), quantas combinações de parâmetros a memória
  sozinha determina? Com que precisão? Quantos bits?
- **Hipótese.** A memória observável em banda é um degrau suave com tempo de subida $\sim M_f$. Ela
  determina cerca de 2–3 combinações (amplitude, escala de tempo e instante). O resto é degenerado.
- **Problema que resolve.** A memória órfã: o que se reconstrói quando só a memória está na banda.
- **Fundamentação.** Matriz de Fisher, limite de Cramér-Rao, dimensão efetiva bayesiana
  $d_{\rm ef}=\sum\lambda_i/(\lambda_i+\sigma_{\rm prior}^{-2})$ e informação mútua gaussiana
  $\tfrac12\log\det(I+\Sigma_{\rm prior}\Gamma)$.
- **Teste.** Fisher dos modos $m=0$ do NRHybSur3dq8_CCE contra o Fisher da onda oscilatória.
- **Contribuição possível.** Os limites de identificabilidade estatística da memória órfã.

## L06 — Informação mútua e aprendizado de máquina

- **Pergunta.** Quais parâmetros são previsíveis a partir das memórias, sem supor modelo linear?
- **Hipótese.** A informação mútua e a previsibilidade ($R^2$) são altas para $D/M$ e para combinações
  de $M_f$ e $\iota$, e baixas para $q$ e os spins individuais.
- **Fundamentação.** Estimador kNN de informação mútua (Kraskov–Stögbauer–Grassberger) e regressores
  não lineares.
- **Teste.** Conjunto de alguns milhares de binárias amostradas de uma distribuição a priori,
  observáveis com ruído realista e $R^2$ por parâmetro.
- **Contribuição possível.** Uma medida de identificabilidade independente do modelo.

## L07 — O que um detector mede de fato

- **Pergunta.** As "quatro memórias" são mensuráveis?
- **Hipótese.** Não diretamente:
  - um detector mede $F_+h_++F_\times h_\times$, com o ângulo de polarização $\psi$ desconhecido;
  - as memórias de spin e de CM são integrais no tempo, isto é, componentes de frequência quase zero
    que detectores em solo não veem.

  O conjunto mensurável é menor que quatro números.
- **Teste.** Resposta de detectores e rede; espectro das memórias integradas contra as curvas de ruído.
- **Contribuição possível.** Uma contagem honesta dos números de memória mensuráveis.

## L08 — Recuperação exata de fase pelos fluxos

- **Pergunta.** As séries temporais dos fluxos de energia $P=|\dot h|^2$ e de momento angular
  $H=-{\rm Im}(\bar h\dot h)$ determinam o modo dominante sem aproximação adiabática?
- **Hipótese.** Sim. Com $h=a\,e^{-i\psi}$: $P=\dot a^2+a^2\dot\psi^2$ e $H=a^2\dot\psi$, então
  $u=a^2$ obedece a $\dot u^2=4(uP-H^2)$. Uma condição inicial ($a\to0$ no passado) fixa a solução, e
  $\dot\psi=H/u$. O estimador da etapa 6, $\Omega=P/(2H)$, é a aproximação adiabática ($\dot a=0$) e
  superestima $\dot\psi$ por $1/(1-\dot a^2/P)$, o que explicaria parte do erro na fusão.
- **Teste.** Com $P$ e $H$ do próprio (2,2) a reconstrução deve ser exata; com $P$ e $H$ vindos dos
  modos de memória, medir o erro.
- **Contribuição possível.** Um algoritmo de recuperação de fase a partir de observáveis de memória.

## L09 — Memória no *ringdown*

- **Pergunta.** Que informação de modos quase normais (QNMs) a memória carrega?
- **Hipótese.** Depois do pico, a taxa da memória decai como $e^{-2t/\tau_{220}}$, e aparecem batimentos
  nas frequências-diferença $\omega_n-\omega_{n'}$ com amortecimento $1/\tau_n+1/\tau_{n'}$.
- **Teste.** Ajuste das derivadas dos modos $m=0$ do substituto depois do pico; comparar com o pacote
  `qnm`.
- **Contribuição possível.** Espectroscopia de diferenças de frequência no setor de memória.

## L10 — Precessão: multipolos $m\neq0$ e spins no plano

- **Pergunta.** Com spins precessantes, as memórias globais ganham multipolos $m\neq0$. Eles carregam
  informação dos spins no plano?
- **Hipótese.** Os multipolos $m=\pm1,\pm2$ codificam a inclinação do momento angular irradiado em
  relação a $\hat L$ inicial. O posto do jacobiano em relação aos 7 parâmetros intrínsecos sobe.
- **Teste.** NRSur7dq4 (modos oscilatórios, nível A) e jacobianos em relação a $(q,\vec\chi_1,\vec\chi_2)$.
- **Contribuição possível.** A primeira análise de identificabilidade das memórias de binárias
  precessantes.

## L11 — Zeros da memória no céu (Poincaré–Hopf)

- **Pergunta.** O padrão de memória no céu é um campo de spin 2, um "campo de direções sem sentido".
  Pelo teorema de Poincaré–Hopf, a soma dos índices dos seus zeros é fixa. Onde ficam os zeros?
- **Hipótese.** Sem precessão, os zeros estão nos polos (índice +1 cada). Com precessão, eles se
  deslocam e seguem a direção do momento angular irradiado: um observável topológico.
- **Teste.** Localizar os zeros do padrão de deslocamento para sistemas precessantes.

## L12 — Limites para a memória pelo teorema da área

- **Pergunta.** Existe uma desigualdade rigorosa entre a amplitude da memória e a energia irradiada, e
  entre esta e o teorema da área de Hawking?
- **Hipótese.** Pela fórmula de Thorne,
  $\Delta h^{TT}_{ij}=\frac4D\int\frac{dE}{d\Omega'}\big[\frac{n'_in'_j}{1-n'\cdot N}\big]^{TT}d\Omega'$ com
  $dE/d\Omega'\ge0$. Daí $|\Delta h|\le4E_{\rm rad}/D$, e com o teorema da área
  $|\Delta h|\le4(M-M_{f,\min})/D$. A recíproca, $E_{\rm rad}\ge D|\Delta h|/4$, seria um limite
  inferior da energia irradiada que independe de modelo.
- **Teste.** Verificar a desigualdade e sua folga com relatividade numérica; versão mais justa para
  radiação dominada por $\ell\le L$.
- **Contribuição possível.** Um teste do teorema da área ou de energia não gravitacional pela memória.

## L13 — Canais não gravitacionais: núcleo e degenerescência

- **Pergunta.** Que histórias de emissão de neutrinos, luz e matéria são invisíveis à memória?
- **Hipótese.** O mapa (fluência total de energia nula no céu) → (memória de deslocamento) tem núcleo
  formado pelas partes $\ell=0$ e $\ell=1$. Toda emissão isotrópica ou dipolar é invisível, e histórias
  com a mesma parte $\ell\ge2$ da fluência são indistinguíveis pela memória final.
- **Teste.** Exemplos explícitos (jato de neutrinos × emissão gravitacional equivalente).
  Partículas massivas chegam depois e mudam a estrutura temporal da memória.
- **Contribuição possível.** Um enunciado preciso do que um teste de "excesso de memória" pode e não
  pode detectar.

## L14 — Janelas × momentos (memórias superiores)

- **Pergunta.** As "memórias superiores" (momentos temporais da *news*, [SGN2024; GM2024]) e as janelas
  carregam a mesma informação. Qual base é estável?
- **Hipótese.** Reconstruir o fluxo a partir de $K$ momentos tem número de condição exponencial em $K$
  (como a torre da etapa 5). A partir de $K$ janelas cumulativas, ele cresce só polinomialmente.
- **Teste.** Números de condição das matrizes de amostragem para fluxos de binárias reais.
- **Contribuição possível.** Uma base estável para a informação das memórias superiores.

## L15 — Generalização do Teorema 1 a outros campos

- **Pergunta.** A redução de Gram (as memórias só veem dois momentos espectrais) vale para a memória
  eletromagnética e a de campos escalares?
- **Hipótese.** Sim, para todo campo cujo fluxo é quadrático na radiação.

## L16 — Excentricidade: dimensão da família e anomalia

- **Pergunta.** Com $(e_0,\ell_0)$ livres a família tem dimensão 4. A anomalia inicial $\ell_0$ muda as
  memórias? Duas janelas ainda isolam a solução quando a excentricidade é livre?
- **Teste.** SEOBNRv5EHM: variar $\ell_0$ e resolver com duas janelas.

## L17 — Estrelas de nêutrons: marés na memória

- **Pergunta.** A memória de uma binária de estrelas de nêutrons depende da deformabilidade $\Lambda$?
  Há degenerescência entre $\Lambda$ e a massa?
- **Hipótese.** A memória acumulada até o contato mede a energia de ligação no contato, que depende de
  $\Lambda$ (ver [TEH2021] para a distinção de sistemas mistos).
- **Teste.** NRHybSur3dq8Tidal (nível A até o contato).

## L18 — Cargas suaves como informação

- **Pergunta.** Quantos multipolos de memória uma binária excita de forma significativa (o "conteúdo
  de cabelo macio")?
- **Hipótese.** O espectro $|J^E_{\ell0}|$ decai rapidamente com $\ell$, e o conteúdo efetivo é de
  poucos números, dominado por $\ell=2$.
- **Teste.** Multipolos até $\ell=10$ no nível A.
