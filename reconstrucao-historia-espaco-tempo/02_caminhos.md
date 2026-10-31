# Etapa 2 — Caminhos independentes e conexões entre áreas

Rótulos: **[E]** estabelecido, **[D]** derivado ou verificado aqui, **[H]** hipótese, **[S]** especulação.

## 1. Relatividade geral: o que chega ao infinito nulo

- No formalismo de Bondi–Sachs [BBM1962; Sachs1962], o dado livre em $\mathscr I^+$ é a *news*
  $N_{AB}=\partial_uC_{AB}$, isto é, duas funções reais de $(u,\theta,\phi)$. A massa de Bondi $m$ e o
  aspecto de momento angular $N_A$ evoluem por equações diferenciais em $u$ alimentadas pela *news*.
  Os coeficientes de ordem mais alta em $1/r$ ficam determinados a menos de "funções de integração"
  independentes do tempo [SO2022, citando Barnich–Troessaert e GN2022] **[E]**.
- **Consequência:** tudo o que se observa em $\mathscr I^+$ (memórias, cargas, fluxos, observáveis
  persistentes de ordem dominante) é funcional de (*news*, valores iniciais das cargas e das funções
  de integração) **[E]**.
- Multipolos (formalismo pós-Minkowskiano multipolar [Blanchet2014]): os momentos radiativos são
  $U_L=M_L^{(\ell)}+\dots$. Em regiões não radiativas, $M_L(u)=\sum_{k=0}^{\ell}M_{L,k}u^k$. O termo
  $k=\ell$ dá a memória de deslocamento, os termos $1\le k\le\ell-1$ não afetam o cisalhamento linear
  (suas variações codificam as memórias subdominantes), e $k=0$ (multipolo estático) é invisível na
  radiação [COS2022] **[E]**.

## 2. Formalismo BMS e cargas assintóticas

| Memória | Carga / simetria | Referência |
|---|---|---|
| deslocamento | supermomento / supertranslações | SZ2016, FN2017 |
| spin | superspin / superrotações (teorema subdominante do gráviton mole) | PSZ2016, CS2014, FN2017 |
| centro de massa | super-CM / superboosts | Nichols2018, CFR2018 |
| giroscópica | corrente das supertranslações duais + gerador da dualidade | SO2022, SO2023, GGP2019, GGPerry2020 |
| memórias superiores | momentos $\int u^nN\,du$; torre de cargas $w_{1+\infty}$ | SGN2024, Strominger2021, FPR2022 |

Todas obedecem ao mesmo esquema **[E]**: memória = (variação de uma carga entre os estados inicial e
final) + (integral no tempo de um fluxo quadrático na radiação).

## 3. As quatro memórias como "mapas de fluência"

Lendo as fórmulas da §1 de `03_problema_concreto.md` **[D, leitura das fórmulas de E]**:

- deslocamento: padrão angular ($\ell\ge2$) da energia irradiada por ângulo sólido, $\int|\dot h|^2du$;
- spin: parte rotacional do fluxo de momento angular por ângulo sólido;
- CM: parte de divergência do mesmo fluxo, mais a variação das cargas de super-CM; o termo de
  centroide temporal da energia é removido de propósito [Nichols2018];
- giroscópica: spin + fluência de helicidade $\int\mathrm{Im}(\bar h\dot h)\,du$ (diferença entre
  potências circular-esquerda e circular-direita), inclusive a parte $\ell=0$, a helicidade total
  irradiada [SO2023].

O Teorema 1 (`03_problema_concreto.md`) mostra que as quatro são lineares em duas matrizes
$(B,\,A-A^\dagger)$ **[D]**.

## 4. Harmônicos esféricos

- Regras de seleção por símbolos 3j: o produto dos modos $(\ell',m')$ e $(\ell'',m'')$ alimenta
  $\ell\in[|\ell'-\ell''|,\ell'+\ell'']$ e $m=m'+m''$.
- Fontes com simetria equatorial: memória elétrica em $\ell$ par com $m=0$, magnética em $\ell$ ímpar com
  $m=0$ (a de spin está no (3,0); conferido no exp01).
- O fator $\sqrt{(\ell-2)!/(\ell+2)!}\sim\ell^{-2}$ apaga as estruturas angulares finas (problema inverso
  mal posto de forma polinomial; `01_revisao_critica.md` §2.8).

## 5. Problemas inversos e unicidade

- Critérios de Hadamard: existência, unicidade, estabilidade. Os três falham aqui, cada um por um motivo.
- **Unicidade, teoria linear.** No gauge TT, $h^{TT}_{ij}(u,\mathbf n)=\frac{4}{r}\Lambda_{ij,kl}(\mathbf n)\int
  d^3x\,T_{kl}(u+\mathbf n\cdot\mathbf x,\mathbf x)$. Em Fourier, só se observa $\Lambda\tilde T(\omega,\omega\mathbf n)$,
  isto é, o tensor de energia-momento **sobre o cone de luz** $|\mathbf k|=\omega$, projetado em duas
  polarizações (resultado de livro-texto). Tudo fora do cone é invisível: são as fontes não radiantes,
  análogas às do eletromagnetismo [DW1973; BC1977]. Não achei tratamento sistemático para a gravidade
  (busca em §9).
- **Unicidade, teoria não linear, exemplos exatos:** Birkhoff (dinâmica esférica invisível) **[E]**;
  núcleo do horizonte, rigoroso na teoria linear [DRSR2018; Masaood2022] e ilustrado no exp04 **[D]**;
  binária × sistema de Lagrange com o mesmo quadrupolo [THA2009] **[E]**.
- **Estabilidade:** reconstruir a forma de onda a partir da torre de memórias é uma continuação
  analítica. Medi a amplificação do ruído: $\sim e^{a^2/4}$ com $a=\omega_0\sigma$ (exp05) **[D]**.

## 6. Teoria da informação

- Cramér–Rao e Fisher: a precisão das grandezas reconstruídas é limitada pela razão sinal-ruído.
- Contagem de formas distinguíveis: o volume do espaço de parâmetros na métrica de Fisher dá o número
  de modelos de onda [Owen1996]. O número máximo de formas distinguíveis é
  $\ln N\approx\tfrac12N_{\rm bins}\ln(1+\rho^2/N_{\rm bins})$, com forma de capacidade de Shannon [FH1998] **[E]**.
- Desigualdade de processamento de dados: nenhum processamento aumenta a informação mútua com a história.
- Estimativas aplicadas à memória: §5 de `04_brechas.md` **[D]**.

## 7. Reconstrução de sinais e análise de fase

- O Teorema 1 diz que as memórias são **medidas de intensidade**: dependem de $\tilde h\tilde h^\dagger$,
  não de $\tilde h$. É a mesma situação da óptica, em que um detector de intensidade perde a fase. A
  recuperação de fase em uma dimensão não é única [Hofstetter1964; Fienup1982] **[E]**. Aqui é pior,
  porque as memórias guardam só dois momentos espectrais, não o espectro de potência inteiro **[D]**.
- A forma de onda é a **medida de campo** (coerente): guarda a fase espectral, que contém a ordem
  temporal (*chirp* × anti-*chirp*, uma explosão × duas).

## 8. Simulações numéricas e aprendizado de máquina

- **Relatividade numérica:** a memória é extraída por evolução característica de Cauchy (CCE) e conferida
  pelas leis de balanço [Mitman2020]; é adicionada a catálogos [Mitman2021]; exige fixar o referencial
  BMS [Mitman2024]; já entra em substitutos de forma de onda [Yoo2023]; foi calculada em fusões de
  buracos negros [PR2011]. As simulações resolvem o problema direto (história → onda), não o inverso.
- **Aprendizado de máquina:** estimação de posterior amortizada [Dax2021; Gabbard2022] reproduz a
  inferência bayesiana muito mais rápido. Não remove degenerescências, que vêm do problema direto. Em
  inferência por simulação, o modelo a priori (as simulações de treino) decide o que é "reconstruído"
  nas direções que os dados não veem.

## 9. Verificação de originalidade (busca bibliográfica de 31/10/2026)

Resultado da busca (arXiv, INSPIRE, ADS; resumos e, em vários casos, texto completo):

| Hipótese | Veredito | Mais próximo na literatura |
|---|---|---|
| Memórias dependem só dos momentos espectrais; invariância por filtros de fase | **não encontrado** nessa forma | Favata2010: depende da amplitude do h22, não da fase; Thorne1992; Garfinkle2016 |
| Construções explícitas de fontes degeneradas | **não encontrado** | THA2009 (degenerescência da forma de onda, não da memória) |
| Torre de memórias → forma de onda por analiticidade | **conhecido** | FPR2024 (com obstrução por caudas; sem análise de estabilidade) |
| Mal condicionamento dessa reconstrução | **não encontrado** | — |
| CM e centroide temporal; giroscópica e helicidade | **parcial** | Nichols2018 remove o centroide; SGN2024 eq. 3.12 o contém; SO2023 (helicidade); LY2024 |
| Memória quebra degenerescências de parâmetros | **conhecido** | Xu2024 (distância–inclinação, SNR>90), RS2025, Gasparotto2023, Lasky2016 |
| Lentes perto da fonte dão vistas de vários ângulos | **conhecido**; para mapear a memória: **não encontrado** | GK2022, Martens2026, DL2020 |
| Teoria da informação de ondas gravitacionais | **parcial** | FH1998, Owen1996; nada específico para a memória |
| Fontes não radiantes em gravidade | **parcial** | COS2022 (polinômios), THA2009 |
| Memória como referência de polarização para birrefringência | **não encontrado** | HZZ2022, CJS2025, ZZQW2020 |
| Excesso de memória como calorímetro de canais não gravitacionais | **parcial** | HYZ2023, Bamber2026, YM2018, MCL2021 |

"Não encontrado" quer dizer "não encontrado após busca razoável", não "inédito garantido".

## 10. Conexões entre áreas

1. **Memória ↔ detecção de intensidade ↔ recuperação de fase (óptica).** É a conexão central desta pesquisa
   (Teorema 1). Explica de uma vez por que histórias com ordens temporais opostas têm a mesma memória.
2. **Torre de memórias ↔ coeficientes de Taylor ↔ continuação analítica (Paley–Wiener).** Em princípio a
   torre determina a onda, se não houver caudas [FPR2024]. Na prática é instável de forma explosiva
   (exp05), e as caudas $1/u$ [LS2019] tornam os momentos divergentes.
3. **Horizonte ↔ teoria de espalhamento.** O que cai no buraco é informação perdida para $\mathscr I^+$
   já na teoria clássica linear, sem nenhum paradoxo quântico (exp04).
4. **Dualidade ↔ helicidade ↔ memória giroscópica ↔ polarização.** A rotação de dualidade é simetria da
   gravidade linearizada [HT2005] e falha na ordem cúbica [DS2005]. A memória giroscópica mede o seu
   gerador [SO2023]. A memória elétrica funciona como referência de polarização (`04_brechas.md` §8).
5. **Degenerescências ↔ simetrias.** Cada simetria exata do problema direto é uma degenerescência que
   nenhum dado remove: translação no tempo, escala do vácuo (massa ↔ desvio para o vermelho, quebrada
   por efeitos de maré [MR2012]), dualidade, filtros de fase (para as memórias), referencial BMS.
   Quebrar a simetria (matéria com escala própria, ordem cúbica) é o que cria informação.
6. **Cabelo mole ↔ memória clássica.** No debate quântico, as cargas moles não carregam informação além
   da fixada pelas leis de conservação [MP2016; BP2017]. Na versão clássica, a memória é funcional da
   *news* e das cargas: a mesma conclusão.
7. **Populações ↔ tomografia angular.** Eventos vistos em inclinações diferentes amostram o padrão
   angular médio da memória [Lasky2016; YM2018].
