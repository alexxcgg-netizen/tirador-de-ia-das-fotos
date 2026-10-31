# Conclusões, limites e próximos passos

Rótulos: **[E]** estabelecido, **[D]** derivado ou verificado aqui, **[H]** hipótese, **[S]** especulação.

## 1. Resposta à pergunta central

> *Qual é a quantidade máxima de informação sobre a história de um sistema físico que pode ser
> reconstruída a partir das observações gravitacionais?*

A resposta vem em camadas, da mais geral para a mais prática.

1. **Causalidade.** Só a parte do espaço-tempo que pode mandar sinais ao infinito, $J^-(\mathscr I^+)$,
   é acessível. O interior de buracos negros está excluído por definição **[E]**.
2. **Completude dos dados radiativos.** Tudo o que chega ao infinito é a *news* (duas funções de
   tempo e direção) mais os valores iniciais das cargas e das funções de integração. Memórias, cargas
   e fluxos são funcionais disso **[E]**. **No vácuo, a memória não acrescenta informação à forma de
   onda completa** **[E]**. Com matéria, acrescenta o fluxo dos canais não gravitacionais **[E]**.
3. **O que se perde mesmo para um observador ideal que cobrisse o céu inteiro:** radiação absorvida
   pelo horizonte (exp04), dinâmica esférica (Birkhoff), multipolos estáticos e partes polinomiais no
   tempo dos multipolos [COS2022], e, na teoria linear, todas as componentes de Fourier da fonte fora
   do cone de luz **[E]**.
4. **O que as memórias retêm:** só os momentos espectrais de primeira e segunda ordem da matriz
   espectral cruzada dos modos. A fase espectral comum, que contém a ordem temporal dos eventos, é
   invisível. Existem infinitas histórias distintas com as mesmas quatro memórias (Teoremas 1 e 2)
   **[D]**.
5. **Um observador real** (uma direção, banda e ruído finitos) obtém no máximo ~150 bits de uma fusão
   como GW150914. A memória contribui com ~0,2 bit no LIGO de projeto e até ~6 bits no Einstein
   Telescope **[D, estimativa]**.
6. **Reconstruir a onda só pela torre de memórias** é instável de forma explosiva: o ruído é
   amplificado por $\sim e^{a^2/4}$ **[D]**.
7. **Com modelos físicos** (RG + matéria), a história vira um conjunto finito de parâmetros e a
   precisão é limitada pela informação de Fisher. As degenerescências que restam vêm de simetrias **[E]**.
8. **Inteligência artificial** não passa o limite da desigualdade de processamento de dados. Nas
   direções que os dados não veem, quem decide é a distribuição a priori **[E]**.

**Resposta negativa, com demonstração:** não existe reconstrução completa da história a partir de
observações gravitacionais. Os limites L1–L7 abaixo são rigorosos (ou ilustrados com precisão de
máquina). **Resposta positiva:** existe uma forma "mais completa" do que a memória sozinha. É a
combinação da §3, e ela tem previsões testáveis (§4).

## 2. Limites (enunciados)

| # | Limite | Situação |
|---|---|---|
| L1 | Nada fora de $J^-(\mathscr I^+)$ afeta os dados em $\mathscr I^+$ | [E] definição de horizonte de eventos |
| L2 | Observáveis em $\mathscr I^+$ = funcionais da *news* e dos dados iniciais das cargas | [E] BBM1962, Sachs1962, FN2017, Mitman2020 |
| L3 | Dados em $\mathscr I^+$ não determinam o dado inicial: falta o que cai no horizonte | [E] DRSR2018, Masaood2022; exp04 [D] |
| L4 | Dinâmica esférica é invisível | [E] Birkhoff |
| L5 | As quatro memórias dependem só de $(B,\,A-A^\dagger)$; fibras de dimensão infinita | [D] Teoremas 1 e 2; exp02 |
| L6 | Reconstrução pela torre de memórias: amplificação $\gtrsim e^{a^2/4}$; caudas $1/u$ tornam a torre divergente | [D] exp05; [E] FPR2024, LS2019 |
| L7 | $I(\text{história};f(\text{dados}))\le I(\text{história};\text{dados})$ para qualquer algoritmo | [E] |

## 3. O que é mais completo do que a memória

1. **Forma de onda multimodo completa.** Contém a fase espectral (a ordem temporal) e mais de 99% da informação.
2. **Teste de consistência de quatro memórias [D/H].** Pelo Teorema 1, as partes nulas das quatro
   memórias são previstas por duas matrizes ($B$ e $A-A^\dagger$) calculadas da forma de onda
   oscilatória medida. Comparar com as memórias medidas testa a RG não linear com quatro observáveis.
   Generaliza o que [Khera2021] faz para a memória de deslocamento.
3. **Calorimetria multimensageira [E em partes, H no teste de excesso].** O resíduo entre a memória
   medida e a prevista pela onda mede a anisotropia da fluência de neutrinos, luz e matéria ejetada,
   e de qualquer radiação sem massa desconhecida.
4. **Polarização relativa memória/oscilação [H].** Mede o ângulo de dualidade da fonte e serve de
   referência para birrefringência de velocidade.
5. **Vários ângulos de visão [E parcial, S].** Populações (estatística) e lentes perto da fonte.

## 4. Previsões verificáveis

- **V1.** Para qualquer fonte no vácuo, as partes nulas das quatro memórias medidas devem coincidir
  com as previstas pelas matrizes de Gram da forma de onda medida (ET, CE, LISA). Desvio indica
  canal extra ou RG modificada [HYZ2023].
- **V2.** Em fusões de estrelas de nêutrons, a memória excede a prevista pela onda gravitacional em
  ~15–50% [Bamber2026]. O excesso deve ter o padrão angular da fluência anisotrópica de EM,
  neutrinos e ejeção.
- **V3.** Numa supernova galáctica, a memória de neutrinos ($10^{-22}$–$10^{-21}$, 0,1–10 s [MCL2021])
  combinada com o perfil temporal medido em detectores de neutrinos separa a anisotropia ($\ell\ge2$)
  do fluxo total.
- **V4 [H].** Com birrefringência de velocidade, o ângulo entre a polarização da memória e a da
  oscilação deve depender da frequência e da distância. Na RG é fixo pela geometria da fonte.
- **V5 (negativa).** Nenhuma análise só de memória (por exemplo, buscas de *bursts with memory* em
  redes de pulsares [NANOGrav2024; NANOGrav2025]) pode separar fontes que diferem só na ordem
  temporal da emissão. Nenhuma análise de ondas gravitacionais pode reconstruir o perfil radial de
  um colapso esférico.
- **V6.** Empilhando populações de binárias sem precessão, a dependência com a inclinação deve seguir
  $\sin^2\iota\,(17+\cos^2\iota)$ (deslocamento) e $\sin^2\iota\cos\iota$ (spin) [Nichols2017; GN2023].

## 5. Comparação com o conhecimento existente

| Resultado desta pesquisa | Relação com a literatura |
|---|---|
| Teorema 1 (quatro memórias ↔ dois momentos espectrais) | Generaliza "a memória independe da fase do h22" [Favata2010]; não encontrado nessa forma |
| Construções A–E | Não encontradas; no mesmo espírito de [THA2009] (degenerescência da onda, não da memória) |
| Quebra cúbica e restauração | Coerente com a falha da dualidade na ordem cúbica [DS2005] |
| Núcleo do horizonte | Ilustração de [DRSR2018; Masaood2022] |
| Instabilidade da torre | Complementa [FPR2024], que mostra a reconstrução por analiticidade sem análise de estabilidade |
| Bits de informação da memória | Usa [FH1998; Lasky2016; Goncharov2024]; estimativa nova, simples |
| Teste de birrefringência pela memória | Não encontrado; [HZZ2022; CJS2025; ZZQW2020] tratam memória e paridade de outra forma |

## 6. Problemas em aberto (em ordem de promessa)

1. **Degenerescência em todas as ordens.** Provar com o teorema da função implícita em espaços de
   Sobolev, usando as leis de balanço exatas. O exp03 dá posto completo e resíduo de 1e-8.
2. **Caso autogravitante — respondido em parte na etapa 6** (`07_binarias_reais.md`). Para spins
   alinhados, o mapa é quase injetivo no céu inteiro, com uma direção cega de 2ª ordem em massas
   iguais. Num observador há famílias exatas de binárias com as mesmas quatro memórias. Ficam em
   aberto: precessão (12 parâmetros), excentricidade no nível de RN e o caso da memória órfã.
3. **Informação nas grandezas com peso $u$ e nas memórias superiores** com ruído realista.
4. **Teste de birrefringência:** previsão quantitativa para ET, CE e LISA.
5. **Teste de excesso de memória** para estrelas de nêutrons e supernovas, com simulações tipo [Bamber2026].
6. **Lentes perto da fonte** com óptica ondulatória para a parte de baixa frequência da memória.

## 7. Onde paramos (31/10/2026, depois da etapa 6)

- Revisão crítica concluída; nove tópicos anteriores reavaliados (`01_revisao_critica.md`).
- Teorema 1 (redução de Gram) enunciado, demonstrado e verificado; cinco fontes degeneradas construídas.
- Código validado contra Favata 2009, Nichols 2017 e Nichols 2018; cinco experimentos reproduzíveis.
- Bibliografia verificada (≈80 referências) e checagem de originalidade feita (`02_caminhos.md` §9).
- **Etapa 6 concluída** (`07_binarias_reais.md`, exp06–exp15). A família infinita das etapas 3–5 não
  contém binárias da RG (analítico). Num observador, a degenerescência sobrevive como família exata de
  dimensão ≥ 2, testada nos níveis A, B e C, também entre binárias circulares e excêntricas
  (SEOBNRv5EHM). As ondas completas separam os pares a partir de SNR 1–6. O observável
  $\Omega_{\rm mem}=\dot h_{20}/(C|h_{30}|)$ recupera a fase só com modos de memória, com erro de 2–13%.
- **Correção registrada:** a primeira versão da análise excêntrica PN tinha um objetivo não suave (grade
  de tempo truncada antes da separatriz). A conclusão "nenhuma excêntrica imita a circular" foi retirada
  e substituída pela correta: sem spins, só com $\eta>1/4$ (`07_binarias_reais.md` §4, item 4).
- **Próximo passo sugerido:** a memória órfã. Quando só a memória de uma fonte está na banda (fontes
  subsolares, [McNeill2017; ET2020]), a família degenerada da etapa 6 é a ambiguidade real da
  reconstrução. Medir o tamanho dessa família com ruído realista, e estender para spins precessantes.
