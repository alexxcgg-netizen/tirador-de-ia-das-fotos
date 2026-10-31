# Etapa 1 — Revisão crítica do que foi apresentado

Rótulos: **[E]** estabelecido (com referência), **[D]** derivado ou verificado aqui, **[H]** hipótese,
**[S]** especulação. Referências em `referencias.md`.

## 1. A equação central está certa?

$$h^{\rm mem}_{\ell m}(u)=K_\ell\int_{-\infty}^{u}F_{\ell m}(u')\,du',\qquad \frac{dh^{\rm mem}_{\ell m}}{du}=K_\ell F_{\ell m}(u).$$

**Sim, como definição da memória nula gerada pelo fluxo de energia das próprias ondas, desde que
as convenções sejam fixadas** [E: BD1992; Favata2009a, eq. 3; Favata2009b]:

- $h=h_+-i h_\times=\sum_{\ell m}h_{\ell m}\,{}_{-2}Y_{\ell m}$ (harmônicos com peso de spin −2);
- $F_{\ell m}(u)=\oint d\Omega\;Y^*_{\ell m}(\Omega)\,\dfrac{dE}{du\,d\Omega}$ (harmônicos **escalares**);
- $K_\ell=\dfrac{16\pi G}{c^4R}\sqrt{\dfrac{(\ell-2)!}{(\ell+2)!}}$ ($R$ = distância), válido só para $\ell\ge2$.

O fator $\sqrt{(\ell-2)!/(\ell+2)!}$ vem de inverter $\mathfrak D=\tfrac18D^2(D^2+2)$ e aplicar
$\bar\eth^2$ [Mitman2020]. Conferi numericamente (exp01): para uma binária quase circular, o código dá
$h^{\rm mem}_{20}=(4/7)\sqrt{5\pi/6}\,\eta Mx/R$ com razão 1,0003 [Favata2009a] e o padrão
$\sin^2\theta(17+\cos^2\theta)$ com erro 6e-4 [Nichols2017]. Os resíduos vêm da inconsistência
pós-newtoniana do termo $\dot A^2$ no fluxo, não do código. A derivada é trivial (teorema fundamental do cálculo).

## 2. Simplificações perigosas e conclusões que não se sustentam

**2.1 A fonte da memória está incompleta.** A lei de balanço exata é [E: FN2017; Mitman2020; BG2014]

$$\Delta h^{E}=\tfrac12\bar\eth^2\mathfrak D^{-1}\Big[\Delta m+\tfrac14\!\int\!|\dot h|^2du+4\pi\!\int\! r^2T_{uu}\,du\Big].$$

Faltam na equação discutida: (a) a **memória ordinária** $\Delta m$ (massas que escapam, recuo do
remanescente, ejeção de matéria) e (b) o fluxo de **toda** radiação sem massa: neutrinos [Epstein1978;
MCL2021], radiação eletromagnética e matéria ejetada. Isso não é detalhe: em fusões de estrelas de
nêutrons, EM, neutrinos e ejeção somam ~15% da memória total (campo magnético moderado) e até ~50%
(campo extremo) [Bamber2026].

**2.2 $\ell=0$ e $\ell=1$ não são memória.** Estão no núcleo de $\mathfrak D$: são a energia e o
momento irradiados (perda de massa e recuo). As componentes de baixa ordem da energia irradiada não
aparecem na deformação.

**2.3 O perfil $h^{\rm mem}(u)$ em tempos intermediários é uma convenção.** O detector mede só o $h$
total. A separação "oscilatório + memória" em cada instante não é observável. Só a variação
assintótica tem significado invariante. A lei exata vale em cada $u$ mas envolve a massa de Bondi
$m(u)$, que um detector distante não mede.

**2.4 Paridade.** A memória nula de deslocamento é puramente elétrica, porque vem de um fluxo escalar.
Mas "não existe memória magnética" é **teorema só para o eletromagnetismo** [Winicour2014]. Para a
gravidade, nenhuma fonte realista é conhecida e o resultado é "plausível" [Winicour2014]. A memória
do vácuo é de paridade elétrica [Bieri2018]. Há um exemplo em gravidade linearizada com memória
ordinária de paridade magnética em ordem $1/r$ [SW2019]. A afirmação correta é: "nenhuma fonte
astrofísica realista conhecida produz memória magnética".

**2.5 Dependência do referencial BMS.** A memória de deslocamento $\Delta C_{AB}$ é invariante por
supertranslações. As de spin e de CM não são, quando há memória de deslocamento: sob supertranslação
$\alpha$, $\int C_{AB}du$ muda por $-\alpha\,\Delta C_{AB}$. A memória de CM definida por Nichols é
invariante sob supertranslações infinitesimais em transições estacionário→estacionário [Nichols2018].
Em relatividade numérica é preciso fixar o referencial BMS [Mitman2024].

**2.6 "Deformação permanente do espaço-tempo" é uma imagem enganosa.** Depois que a onda passa, a
curvatura volta a zero: o espaço-tempo local é de novo plano. O que fica é o **deslocamento relativo**
de massas em queda livre (e outros observáveis persistentes [FGHN2019]), isto é, a transição entre
dois vácuos que diferem por uma supertranslação [SZ2016]. **Não existe arquivo gravado no espaço perto
da fonte para ser lido depois.** A informação viaja para fora sobre cones de luz e passa por cada
observador uma única vez. Isso muda o enquadramento do projeto: "ler a história deixada no
espaço-tempo" significa "ler a radiação que passa por nós".

**2.7 Um observador vê uma direção.** O padrão angular da memória no céu (os harmônicos da energia
irradiada) não é observável num único evento. Medimos o valor numa direção: duas polarizações, das
quais a magnética é nula para fontes realistas. Os padrões no céu só aparecem estatisticamente, em
populações (empilhamento [Lasky2016; Hubner2020]), ou em geometrias especiais (ver `04_brechas.md` §6).

**2.8 $K_\ell\propto\ell^{-2}$ suaviza o padrão angular.** A memória é uma versão passa-baixa do
padrão de energia. Recuperar os multipolos de energia a partir dos de memória multiplica o ruído
por $\sqrt{(\ell+2)!/(\ell-2)!}\sim\ell^2$: problema inverso mal posto de forma branda (polinomial).

**2.9 Detectores terrestres não medem o degrau.** Medem a subida da memória (na banda), e o valor
final é inferido com um modelo. Redes de pulsares medem o degrau, mas nenhuma memória foi detectada
[NANOGrav2024; NANOGrav2025]. Nenhuma memória foi detectada até hoje em dados de LIGO/Virgo
[Hubner2020]. Previsões: com A+ ou O5 a memória de deslocamento aparece numa população [GN2023];
o Cosmic Explorer vê eventos individuais altos e a memória de spin numa população em ~2 anos [GN2023];
o Einstein Telescope mede, no melhor caso, a amplitude da memória de deslocamento a 2% e a de spin a 22% [Goncharov2024].

**2.10 Memória de spin ≠ memória giroscópica.** A giroscópica é a de spin **mais** um termo de
helicidade, o gerador da dualidade elétrico-magnética [SO2022; SO2023]. Ordem de grandeza:
$\Phi\sim2\times10^{-39}\,[(M/M_\odot)/(r/{\rm Mpc})]^2$ rad [SO2022], fora do alcance de qualquer
detector atual.

**2.11 "A memória contém informação que a forma de onda não tem."** **No vácuo, falso**: a memória é
um funcional da *news* e das cargas inicial e final (leis de balanço). Pode ser inferida da parte
oscilatória [Khera2021; ADK2020]. **Com matéria, verdadeiro**: contém o fluxo dos canais que não são
gravitacionais (§2.1). Esse é o seu valor informacional próprio.

**2.12 IA não cria informação.** Pela desigualdade de processamento de dados, $I(H;f(D))\le I(H;D)$
para qualquer algoritmo $f$. Componentes da história que não chegam aos dados (§5 de
`06_conclusoes_e_limites.md`) só são "reconstruídas" pela distribuição a priori. Redes de inferência
amortizada (DINGO [Dax2021], VItamin [Gabbard2022]) aceleram a estimativa do posterior, mas não
reduzem a degenerescência.

## 3. Os nove tópicos discutidos antes

| # | Tópico | Situação | Correção ou nuance |
|---|---|---|---|
| 1 | Memória de deslocamento | [E] ZP1974, BT1987, Thorne1992 | É deslocamento relativo de massas livres (§2.6); a parte ordinária existe (§2.1) |
| 2 | Memória não linear | [E] Christodoulou1991, WW1991, Thorne1992, BD1992 | Formalmente de ordem 2,5PN, mas entra no $h$ na ordem dominante por causa da integral hereditária [Favata2010]; a estimativa "desprezível" de WW1991 foi superada |
| 3 | Memória de spin | [E] PSZ2016, Nichols2017 | Parte magnética de $\int h\,du$; não é a giroscópica (§2.10); depende do referencial BMS (§2.5) |
| 4 | Memória de CM | [E] Nichols2018 | Remove a parte de $\int h\,du$ ligada à memória nula; detecção improvável com detectores atuais e próximos [Nichols2018] |
| 5 | Memória giroscópica | [E] SO2022, SO2023 | Spin + helicidade; ~1e-39 rad para fontes estelares |
| 6 | Harmônicos esféricos | [E] | Só $\ell\ge2$; $K_\ell\sim\ell^{-2}$ suaviza (§2.8); um observador vê uma direção (§2.7) |
| 7 | Limites de problemas inversos | [E] em parte | Desenvolvido em `06_conclusoes_e_limites.md`; núcleos concretos: Birkhoff, horizonte, fontes não radiantes, órbitas do Teorema 1 |
| 8 | Memória × forma de onda completa | [E] Khera2021 | Memória = funcional da forma de onda + cargas; o que ela retém está no Teorema 1 (`03_problema_concreto.md`) |
| 9 | IA para reconstruir histórias | [E] para estimação de parâmetros | Limitada pela desigualdade de processamento de dados (§2.12) |

## 4. O que é conhecido e o que é novo nesta pesquisa

| Afirmação | Situação |
|---|---|
| Memória como integral do fluxo; fórmula em modos | [E] BD1992, Favata2009a |
| Memória independe da fase do modo (2,2) | [E] Favata2010 ("depende só da amplitude do modo h22, não da fase") |
| As **quatro** memórias dependem só de $\int\omega\,\tilde h\tilde h^\dagger$ e $\int\omega^2\,\tilde h\tilde h^\dagger$; invariância por filtros de fase comuns | [D] não encontrado na literatura nessa forma (busca em `02_caminhos.md` §9) |
| Construções explícitas de histórias distintas com as mesmas quatro memórias (anti-chirp, divisão, dualidade, dispersão) | [D] não encontrado |
| Quebra na ordem cúbica (1e-7 a 1e-4) e restauração a 1e-8 por ajuste de fase | [D]; coerente com [DS2005] |
| Reconstrução da forma de onda a partir da torre de memórias: amplificação do ruído $\sim e^{a^2/4}$ | [D] quantificação; a reconstrução por analiticidade é [E] FPR2024, sem análise de estabilidade |
| Núcleo do horizonte (radiação que nunca chega a $\mathscr I^+$) | [E] DRSR2018, Masaood2022; ilustração numérica [D] |
| Memória como referência de polarização para testar birrefringência | [H] não encontrado |
| Memória como calorímetro de canais não gravitacionais | [E] em partes (BG2014, HYZ2023, Bamber2026); o teste de "excesso" para radiação escura é [H] |
