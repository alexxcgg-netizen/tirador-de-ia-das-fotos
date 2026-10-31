# Etapa 4 — Procurando brechas

A Etapa 3 mostrou que as quatro memórias não determinam a história. Aqui mudo de perspectiva e
pergunto o que *poderia* determiná-la. Rótulos: **[E]** estabelecido, **[D]** derivado aqui,
**[H]** hipótese, **[S]** especulação.

## 1. Estamos medindo a variável errada?

Sim. As memórias são **variáveis de fluência**: integrais no tempo de produtos da radiação,
como um bolômetro. A variável que guarda a história é o **campo**: a *news* $N(u,\Omega)$.
Entre os dois extremos há uma escada:

| Observável | O que fixa da história | Situação |
|---|---|---|
| 4 memórias | projeção linear de $\int\omega\,\tilde h\tilde h^\dagger$ e $\int\omega^2\tilde h\tilde h^\dagger$ | [D] Teorema 1 |
| matrizes de Gram completas $(B,\Omega)$ | os mesmos dois momentos espectrais para todos os pares de modos | [D] |
| fluxos com peso $u^n$ (cargas de super-CM, primeiro momento da *news*) | atrasos de grupo, isto é, a ordem temporal | [E] SGN2024, eq. 3.12 |
| fluxo instantâneo $\dot h(u)\dot h(u)^\dagger$ em todo $u$ | $\dot h(u)$ a menos de uma fase comum $e^{i\theta(u)}$ (matriz de posto 1) | [D] elementar |
| *news* completa | tudo o que chega a $\mathscr I^+$ | [E] |

A penúltima linha é instrutiva: mesmo conhecendo *todas* as grandezas quadráticas em *todos* os
instantes, sobra uma rotação de dualidade local no tempo. Só observáveis lineares no campo
(a forma de onda, ou a torre de memórias lineares) a fixam.

## 2. Existe informação escondida na fase?

Sim, e é a maior parte. Pelo Teorema 1, a **fase espectral comum** a todos os modos é invisível
para as quatro memórias. Ela contém a ordem temporal: *chirp* × anti-*chirp*, uma explosão ×
duas, sinal limpo × disperso (exp02). As **fases relativas entre modos** aparecem em parte, nas
componentes fora da diagonal das matrizes espectrais cruzadas **[D]**. Em [Favata2010] já está
que a memória depende da amplitude do modo (2,2) e não da sua fase **[E]**. A generalização às
quatro memórias e ao grupo de filtros de fase é **[D]**.

## 3. Observáveis gravitacionais ainda não considerados

- **Memórias superiores** [SGN2024]: momentos $\int u^nN\,du$, ligados à torre de cargas
  $w_{1+\infty}$ [Strominger2021; FPR2022]. São lineares na *news* e sensíveis à ordem temporal.
  Em princípio a torre inteira reconstrói a onda [FPR2024]. Na prática a reconstrução é instável
  de forma explosiva (exp05): ruído amplificado por $\sim e^{a^2/4}$ **[D]**.
- **Caudas tardias** $h\simeq h_\infty+A/u$ [LS2019]: o coeficiente fixa os momentos dos objetos
  finais. É informação sobre o *estado final*, não sobre o caminho. Também faz os momentos
  $\int u^nN\,du$ com $n\ge1$ divergirem (exp05).
- **Observáveis persistentes** [FGHN2019; GN2022]: desvio de curvas, rotação de giroscópios e
  similares. Reorganizam as mesmas memórias e acrescentam termos de ordem superior.
- **Constantes de Newman–Penrose** [NP1968]: conservadas em $\mathscr I^+$, codificam o estado inicial
  (multipolos estáticos). Aparecem em ordens altas de $1/r$, então são irrelevantes na prática.
- **Densidade de fluxo de helicidade** [LY2024] e a memória giroscópica [SO2023]: a helicidade total
  de órbitas de dois corpos é nula, mas sua distribuição angular não é.
- **Dados no horizonte**: completam a teoria de espalhamento, mas são inacessíveis a qualquer
  observador externo (exp04).

## 4. Luz, neutrinos e ondas gravitacionais juntos

Esta é a brecha mais sólida. A memória nula é alimentada por **todo** fluxo sem massa, não só
pelas ondas gravitacionais [BG2014; Epstein1978]:

$$\Delta h_{\rm medida}-\Delta h\big[\text{fluxo de OG medido}\big]=\tfrac12\bar\eth^2\mathfrak D^{-1}\Big[\Delta m+4\pi\!\int\! r^2T_{uu}\,du\Big].$$

- Fusões de estrelas de nêutrons: EM, neutrinos e ejeção somam ~15–50% da memória total [Bamber2026] **[E]**.
- Supernovas galácticas: memória de neutrinos de $10^{-22}$–$10^{-21}$, acumulada em 0,1–10 s, máximo em
  0,1–1 Hz, ao alcance de DECIGO/BBO [MCL2021] **[E]**.
- Fora da RG, a memória nula só muda se houver fontes extras de energia nula radiativa [HYZ2023] **[E]**.

**Proposta [H].** Um "teste de excesso de memória": a forma de onda oscilatória fixa a memória
gravitacional pelo Teorema 1, os detectores de neutrinos e de luz medem o fluxo na nossa direção,
e o **resíduo** mede a anisotropia ($\ell\ge2$) da fluência em canais não gravitacionais. Se, depois
de contabilizados os canais conhecidos, sobrar excesso, isso seria indício de radiação sem massa
desconhecida ("radiação escura") **[S]**. As peças estão em [YM2018; HYZ2023; Bamber2026]; o teste
de excesso para canais escuros não foi encontrado.

## 5. Formulando com entropia e teoria da informação

Para um parâmetro real de amplitude conhecida medido com razão sinal-ruído $\rho$ num canal
gaussiano, a informação é no máximo $\tfrac12\log_2(1+\rho^2)$ bits. Com números verificados:

| Caso | $\rho$ da memória | Informação máxima |
|---|---|---|
| Evento tipo GW150914, LIGO de projeto (SNR 3 com ~35 eventos [Lasky2016] → $\rho\approx3/\sqrt{35}$) | ~0,5 | ~0,2 bit |
| Einstein Telescope, amplitude do deslocamento medida a 2% (melhor caso em [Goncharov2024]) | ~50 | ~5,6 bits |
| Einstein Telescope, amplitude do spin medida a 22% (melhor caso em [Goncharov2024]) | ~4,5 | ~2,3 bits |

Para comparar, a forma de onda completa de GW150914 ($\rho\approx24$, ~0,2 s de sinal e ~300 Hz de
banda, $N_{\rm bins}\approx120$) comporta até $\tfrac12N_{\rm bins}\ln(1+\rho^2/N_{\rm bins})\approx106$
nats $\approx150$ bits de formas distinguíveis [FH1998] **[D, estimativa de ordem de grandeza]**.

**Leitura:** a memória carrega menos de ~1% da informação do sinal. O valor dela não é a
quantidade, é a **natureza**: é um teste independente de modelo da RG não linear e um calorímetro
dos canais que não são ondas gravitacionais (§4).

## 6. Propriedades invariantes que identifiquem a história

As invariantes disponíveis (massa e spin finais, recuo, cargas BMS do estado final, sem cabelo
para o buraco remanescente) identificam o **estado final**, não o caminho. Todas as histórias da
Etapa 3 terminam no mesmo estado (Corolário 2). Princípio organizador **[D, formulação]**:

> **dados de frequência zero (memórias, caudas, cargas) ↔ estados assintóticos;
> dados de frequência finita (a forma de onda) ↔ a dinâmica entre eles.**

## 7. Simetrias e estruturas esquecidas

Toda simetria exata do problema direto vira uma degenerescência do inverso:

| Simetria | Degenerescência | Quem quebra |
|---|---|---|
| translação no tempo | instante de emissão | relógio externo (contraparte EM) |
| escala do vácuo ($M\to\lambda M$, $t\to\lambda t$) | massa ↔ desvio para o vermelho | efeitos de maré, que têm escala própria [MR2012] |
| dualidade constante | massa ↔ corrente | ordem cúbica da RG [DS2005]; polarização da memória (§8) |
| filtros de fase comuns | ordem temporal (só para memórias) | a forma de onda; ordem cúbica (exp03: 1e-7 a 1e-4) |
| referencial BMS (supertranslações) | spin e CM dependem do referencial | fixação de referencial [Mitman2024] |
| simetria esférica (Birkhoff) | toda dinâmica radial | neutrinos e luz |

## 8. A memória como referência de polarização [H]

Numa direção, a polarização da memória nula fica presa à geometria do padrão de fluxo (paridade
elétrica). A da oscilação reflete a mistura massa/corrente e a orientação da fonte. Daí duas ideias:

1. **Ângulo de dualidade.** A fonte D (exp02) é idêntica a A girada em torno da linha de visada,
   com sobreposição 1,00 maximizando a fase. Só o ângulo relativo entre a polarização da memória e
   a da oscilação as separa (sem girar a polarização, a sobreposição no equador cai para 0,50).
2. **Teste de birrefringência.** Em teorias com birrefringência de velocidade, o plano de
   polarização gira de um ângulo que cresce com a frequência e a distância (ex.: escalar-tensor
   sem fantasmas, teleparalelo simétrico, Hořava–Lifshitz [ZZQW2020]). O conteúdo de baixa
   frequência da memória gira menos que a oscilação, e o ângulo relativo vira medida da
   birrefringência acumulada.

Ressalvas importantes: no Chern–Simons dinâmico domina a birrefringência de *amplitude*, e as
memórias não mudam se o escalar não se acopla à matéria [HZZ2022]. Uma rotação independente da
frequência é degenerada com o ângulo de polarização. A memória que se mede é a subida na banda,
então o efeito é uma rotação diferencial que depende da frequência. É preciso memória com $\rho$
alto (ET, CE, LISA). Não achei essa proposta na literatura (`02_caminhos.md` §9).

## 9. Mais de um ângulo de visão [S]

- **Populações:** eventos vistos em inclinações diferentes amostram o padrão angular médio da
  memória [Lasky2016; YM2018]; o terceiro geração pode descartar padrões isotrópicos [YM2018].
- **Lentes perto da fonte:** um buraco negro supermassivo perto de uma binária produz ecos que vêm de
  radiação emitida em outras direções, com outra amplitude e outra polarização [GK2022]; duas vistas
  quebram degenerescências de modos superiores [Martens2026]. Isso permitiria amostrar o padrão da
  memória em dois ou mais pontos do céu da fonte. Ressalva física: frequências
  $f\lesssim c^3/(2\pi GM_{\rm lente})$ ficam no regime de óptica ondulatória e não sofrem lente
  geométrica (para $10^8M_\odot$, $GM/c^3\approx490$ s, logo $f\lesssim3\times10^{-4}$ Hz). A subida da
  memória na banda do LIGO é lenteada normalmente, mas o "degrau" de baixíssima frequência não.

## 10. Balanço das brechas

| Brecha | Ganha o quê | Situação |
|---|---|---|
| usar a forma de onda inteira | toda a ordem temporal | [E] (é o que se faz em estimação de parâmetros) |
| fluxos com peso $u$, memórias superiores | atrasos de grupo | [E] teoria; medida muito difícil |
| torre completa | a onda, em princípio | [E] teoria; instável na prática (exp05) [D] |
| luz + neutrinos + OG | canais não gravitacionais, ejeção | [E] em partes; teste de excesso [H] |
| polarização relativa memória/oscilação | dualidade, birrefringência | [H] |
| populações e lentes | padrão angular no céu | [E] parcial / [S] |
| nada disso alcança | interior de horizontes, radiação absorvida, dinâmica esférica, multipolos estáticos | limites rigorosos (`06_conclusoes_e_limites.md`) |
