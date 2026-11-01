# L01, L02 e L18 — Identificabilidade das memórias num observador, geometria da fibra degenerada e espectro de multipolos (agente D1)

Modelo: NRHybSur3dq8_CCE, nível A (memórias nulas pelo fluxo dos modos oscilatórios), deslocamento **de janela**,
janela desde $f_{22}=10$ Hz, infraestrutura `codigo/observaveis.py` (L00). Sistema de referência A (exp07):
$M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, $D=400$ Mpc, $\iota=50^\circ$.

Rótulos: **[E]** estabelecido (com referência), **[D]** derivado ou verificado aqui, **[H]** hipótese, **[S]** especulação.
Todo número vem de um arquivo em `resultados/` citado no texto.

## Resumo

1. **Posto** [D, numérico + analítico]. Nos três conjuntos de observáveis o posto do jacobiano é o máximo possível em
   toda a grade (135 pontos intrínsecos × 6 inclinações × 6 azimutes): 4 para as quatro memórias com só $m=0$ (T0) e com
   todos os $m$ (T), 2 para o que um interferômetro mede (O: deslocamento e spin). O limiar é o de Weyl,
   $\tau=\|E\|_F$, com $E$ medido por passos $h,h/2,h/4$; $\sigma_4/\tau\ge71$ em T0 fora dos loci exatos.
2. **Loci exatos** [D, analítico, conferido]. Em $\iota=\pi/2$ o posto cai para 3 (T0 e T), pela simetria de reflexão.
   Em $\iota=0$ cai para 1 em T0 e para 0 em O0 (fator $\sin^2\iota$), **mas não com todos os $m$**: os multipolos
   $m=2$ (borda da fusão) mantêm o posto 4 em T e 2 em O no eixo. Em $q=1$, $\chi_1=\chi_2$ o posto intrínseco cai
   para 2 (troca de rótulos); o substituto viola essa simetria em ~1e-3. Para o problema quadrado
   ($\iota$ e $D$ conhecidos) há também **dobras** genéricas: em A o determinante muda de sinal entre
   $\iota=37{,}0^\circ$ e $37{,}5^\circ$.
3. **Fibras** [D]. Nos pontos regulares a fibra tem dimensão $n-k$: 2 (T0), 3 (T, com $\phi'$), 5 (O). Perto do
   setor circular e alinhado, isso vale também com excentricidade (+2) e precessão (+4). **Com contraparte
   eletromagnética** ($\iota$ e $D$ conhecidos), T0 dá solução isolada, mas mal condicionada ($\sigma_4/\sigma_1$
   mediano 1e-3). T continua com uma curva de soluções, porque o azimute $\phi'$ segue desconhecido: em A,
   $q$ vai de 1,02 a 1,21 ao longo dela, enquanto $M$ e $\chi_{\rm ef}$ ficam fixos a 0,5% e ±0,005.
4. **A direção quase nula intrínseca não é a degenerescência $q$–$\chi_{\rm ef}$ da onda** [D]. Ela vem de uma
   relação exata do limite (2,2): com só $(2,\pm2)$, spin e giroscópica são proporcionais à mesma integral
   $H=\int{\rm Im}(\bar h_{22}\dot h_{22})du$, com constantes universais ($S_{30}/H=-0{,}029200=-C_J$,
   $G_{10}/H=0{,}16287$, $G_{30}/H=-0{,}053311$). A parte nula da CM se anula. O jacobiano intrínseco do modelo (2,2)
   tem posto exatamente 3 ($\sigma_4\sim10^{-13}$); os modos superiores quebram isso em ~1e-3. A direção fraca da onda
   (Fisher, IMRPhenomXAS/XHM) é outra: $d\chi_{\rm ef}/d\ln\eta$ tem sinal oposto em A, e a onda mede a direção fraca
   da memória 15 a 2,5e5 vezes melhor (em Fisher) que a sua própria direção fraca.
5. **Pares do exp07** [D, numérico]. Com o deslocamento de janela, os pares antigos diferem 2,6e-3 a 4,9e-2. Resolvidos
   de novo, **persistem como exatos** (resíduo 1e-11 a 1e-10, no piso da infraestrutura) para
   $(q_B,\chi_{2B})=(1,0),(2,0),(3,0),(2,+0{,}5)$, em T0 e em T para os 8 azimutes testados. Com todos os $m$ a solução
   anda bastante com $\phi'_B$: $\chi_{1B}$ varia até 0,47. As formas de onda continuam distinguíveis: *match* aLIGO
   0,44–0,99, $\rho_{\rm crit}$ 0,9–7,7 contra SNR 66.
6. **Fibra global** [D, numérico]. Em T0, 75 dos 117 pontos $(q_B,\chi_{2B})$ têm solução exata, com M de 64,7 a 90,1
   $M_\odot$. A região é **conexa** (uma componente). A borda tem dois tipos: a parede $|\chi_1|=0{,}8$ e uma **dobra**
   interior, onde duas soluções se fundem e desaparecem. A dobra foi confirmada por continuação exata: $\sigma_{\min}$
   do jacobiano 3×3 vai a zero e há duas soluções exatas logo antes. A hipótese "superfície parametrizável por
   $(q_B,\chi_{2B})$, uma solução por ponto" está **refutada** perto da dobra. O que a fibra preserva melhor (além das
   quatro memórias) é $M_f(1+\nu)$: varia 3% contra 42% de $M_f$, com $\nu$ a fração nula da CM.
7. **L18** [D, numérico]. O conteúdo de multipolos é de ~1 número por memória e 2 na giroscópica.
   - Número de multipolos ≥ 1e-2 do maior: deslocamento 1–2, spin 1, CM 1–2, giroscópica 2 ($\ell=3/\ell=1\approx0{,}32$–0,38).
   - Número efetivo $N_{\rm ef}$: 1,000–1,003, e 1,21–1,28 na giroscópica.
   - $\ell\ge6$ fica em ≤ 4e-4 do maior e não está convergido nos modos de entrada: o substituto não tem (4,2) nem (6,6).

---

## 1. Pergunta e hipóteses

**L01.** Qual é o posto do mapa $F$: parâmetros → memórias num observador? Onde ele cai? Que direções formam o espaço nulo?
O que muda com contraparte eletromagnética? **L02.** Qual é a forma global da fibra $F^{-1}(F(A))$? **L18.** Quantos
multipolos de memória uma binária excita de forma significativa?

| Id | Hipótese (antes dos testes) |
|---|---|
| H1.1 | Posto genérico 4 para T0 e T e 2 para O, certificado acima do piso numérico |
| H1.2 | Queda exata em $\iota=\pi/2$ (T0, T: 3) e $\iota=0$ (T0: 1; O0: 0) |
| H1.3 | Com todos os $m$, $\iota=0$ também é locus de queda |
| H1.4 | Em $q=1$, $\chi_1=\chi_2$ o posto intrínseco de T0 cai para 2 |
| H1.5 | Fibras regulares de dimensão $n-k$ (T0: 2; T: 3; O: 5), +2 com $(e_0,\ell_0)$, +4 com precessão |
| H1.6 | Com $\iota$ e $D$ conhecidos, T0 é localmente identificável e T não é ($\phi'$ desconhecido) |
| H1.7 | A direção quase nula intrínseca (σ ~ 7e-4 em R1) é a versão memória da degenerescência $q$–$\chi_{\rm ef}$ |
| H1.8 | Os pares exatos do exp07 persistem com deslocamento de janela (T0) e com todos os $m$ (T) |
| H2.1 | A fibra T0 é uma superfície conexa, parametrizável por $(q_B,\chi_{2B})$, com uma solução por ponto e borda só em $\lvert\chi_1\rvert=0{,}8$ |
| H2.2 | A fibra preserva o "orçamento de cargas" ($M_f$, $E$) — já refutada no exp16; testar $M_f(1+\nu)$ |
| H2.3 | A redução (2,2) explica a estrutura do jacobiano |
| H18.1 | O espectro $\lvert X_{\ell0}\rvert$ decai rápido; conteúdo efetivo de poucos números, dominado por $\ell=2$ |

## 2. Fundamentação e equações

### 2.1 Os três conjuntos de observáveis

Os multipolos de janela $X^{\rm tipo}_{\ell m}(\lambda)$, com $\lambda=(M,q,\chi_1,\chi_2)$, são adimensionais. No
observador (convenções de `observaveis.no_observador_completo`):

$$\Delta h_+=\tfrac MD\,{\rm Re}\sum J_{\ell m}\,{}_{-2}Y_{\ell m},\quad \int h_\times du=-\tfrac{M^2}{D}\,{\rm Im}\sum S_{\ell m}\,{}_{-2}Y_{\ell m},\quad
\Delta\mathcal K=\tfrac{M^2}{D}\,{\rm Re}\sum K_{\ell m}\,{}_{-2}Y_{\ell m},\quad \Phi=\tfrac{M^2}{D^2}\,{\rm Re}\sum\Phi_{\ell m}\,{}_0Y_{\ell m},$$

com harmônicos em $(\iota,\phi')$.

| Conjunto | Observáveis | Parâmetros | $n$ | $k$ |
|---|---|---|---|---|
| **T0** | as quatro, só $m=0$ (como no 07, mas com deslocamento de janela) | $(\ln M,q,\chi_1,\chi_2,\ln D,\iota)$ | 6 | 4 |
| **T** | as quatro, todos os $(\ell,m)$, $\ell\le8$ | os de T0 e $\phi'$ | 7 | 4 |
| **O** | $\Delta h_+$ e $\int h_\times du$, todos os $m$ (sem giroscópica; CM absorvido por $t_0$, item 5 da revisão) | os de T | 7 | 2 |
| **O0** | O com só $m=0$ | os de T0 | 6 | 2 |

**Azimute.** $\phi'=\phi-\Phi_{\rm orb}(0)$ é o azimute medido a partir da fase orbital no pico. A troca
$(\lambda,\phi)\to(\lambda,\phi')$ é um difeomorfismo: não muda posto nem dimensão de fibra. Ela tira dos
multipolos $m\neq0$ a rotação de ~450 rad por unidade de $\ln M$ que a fase em $t_i$ impõe (verif_L00, item V12).

**Borda inicial.** Os multipolos $m\neq0$ de uma janela abrupta carregam um termo de borda em $t_i$: a primitiva
oscilatória de um integrando $\sim e^{-im\psi}$. Isso é artefato do corte, parte da onda oscilatória, não memória. Ele
vale 1,7e-6 a 1,7e-3 do maior multipolo $m=0$ (spin e CM são os maiores; `exp17_validacao.txt` (a)). Por isso os
$m\neq0$ de T são a média (janela de Hann) sobre inícios em $[t_i,t_i+3T_{\rm orb}]$. Ela suprime esse termo e
converge a ≤ 4,4e-6 ao trocar o comprimento da média (`exp17_validacao.txt` (b)). Os $m=0$, $E_{\rm janela}$ e $M_f$
são sempre os da janela que começa em $t_i$.

### 2.2 Lemas de simetria [D, analíticos]

- **L-escala.** $F_i=D^{-k_i}G_i(\lambda,\iota,\phi')$, com $k=(1,1,1,2)$. Logo a coluna de $\ln D$ é $-k\odot F$.
- **L-reflexão.** Para spins alinhados o sistema é invariante pela reflexão no plano orbital, e
  $h_{\ell,-m}=(-1)^\ell\bar h_{\ell m}$ [E]. Para qualquer janela e todos os $m$:
  $\Delta h_+(\pi-\iota)=\Delta h_+(\iota)$, $\Delta\mathcal K(\pi-\iota)=\Delta\mathcal K(\iota)$,
  $\int h_\times(\pi-\iota)=-\int h_\times(\iota)$ e $\Phi(\pi-\iota)=-\Phi(\iota)$, porque spin e giroscópica
  são pseudoescalares.
  - Conferido com todos os $m$: $F(\pi-\iota)/F(\iota)=(1,-1,1,-1)$ a 1e-10 (`exp17_interpretacao.txt` (5)).
- **L-polo.** ${}_sY_{\ell m}(0,\phi)=0$ salvo $m=-s$ [E].
  - Com só $m=0$: deslocamento, spin e CM ($s=-2$) são $O(\iota^2)$ (${}_{-2}Y_{\ell0}\propto\sin^2\iota$); a
    giroscópica ($s=0$) é $O(1)$.
  - Com todos os $m$, os multipolos $m=2$ sobrevivem no eixo: $\Delta h_+-i\int\!\cdots\propto X_{\ell2}\,{}_{-2}Y_{\ell2}(0)\,e^{2i\phi'}$.
- **L-troca.** $F(q,\chi_1,\chi_2,\iota,\phi')=F(1/q,\chi_2,\chi_1,\iota,\phi'+\pi)$, na convenção "corpo 1 em $+x$".
  - Em $q=1$, $\chi_1=\chi_2$, separando $F=F_{\rm par}+F_{\rm ímpar}$ (paridade de $m$): $\partial_{\ln q}F_{\rm par}=0$
    e $\partial_{\chi_1}F_{\rm par}=\partial_{\chi_2}F_{\rm par}$.
  - Já $\partial_{\ln q}F_{\rm ímpar}\neq0$ e $\partial_{\chi_1}F_{\rm ímpar}=-\partial_{\chi_2}F_{\rm ímpar}$.

### 2.3 Teorema (identificabilidade local no observador) [D]

Seja $F:\mathcal P\subset\mathbb R^n\to\mathbb R^k$ de classe $C^1$, um dos conjuntos acima. Supõem-se spins alinhados,
órbita circular e a janela fixada pela frequência física.

**(i) Cota.** ${\rm posto}\,dF\le\min(k,n)$: 4 em T0 e T, 2 em O.

**(ii) Loci exatos de queda, para todo $\lambda$:**
- (a) **$\iota=\pi/2$.** Por L-reflexão, as linhas de spin e de giroscópica se anulam fora da coluna $\iota$. Logo são
  paralelas, e ${\rm posto}\le3$ em T0 e T. Em O, a linha de deslocamento tem $\partial_\iota=0$ e a de spin só tem
  $\partial_\iota$, então o posto continua 2. Com $\iota$ conhecido, as linhas de spin e giroscópica se anulam: T0 e T
  ficam com posto ≤ 2, O com ≤ 1.
- (b) **$\iota=0$ ou $\pi$, só $m=0$.** Por L-polo, as linhas de deslocamento, spin e CM se anulam, junto com a derivada
  em $\iota$, porque $\sin^2\iota$ tem derivada nula. Fica ${\rm posto}\le1$ em T0 (só a giroscópica) e ${\rm posto}=0$ em O0.
  - Com todos os $m$ não há queda forçada: o lema prevê linhas não nulas vindas de $X_{\ell2}$.
- (c) **$q=1$, $\chi_1=\chi_2$, só $m=0$.** Por L-troca, a coluna $q$ se anula e as colunas $\chi_1$ e $\chi_2$ coincidem.
  O bloco intrínseco tem posto ≤ 2. T0 tem posto ≤ 3 com $\iota$ conhecido e ≤ 2 com $\iota$ e $D$ conhecidos; com
  tudo livre a cota continua 4.
  - Esse é o conjunto fixo da involução de troca. Na carta $(q\ge1,\chi_1,\chi_2)$ é uma singularidade de orbifold:
    as memórias veem $\ln q$ e $\chi_a$ só em segunda ordem, o que estende o §2.5 do 07 à direção $q$.
- (d) **Dobras genéricas.** Para mapas quadrados ($n=k$, por exemplo T0 com $\iota$ e $D$ conhecidos), o conjunto
  $\det dF=0$ tem genericamente codimensão 1. Para $k<n$, o conjunto de posto ≤ $k-1$ tem codimensão $n-k+1$ (Thom). Não
  são simetrias: são dobras do mapa, e a grade só as encontra por amostragem (§4.1).

**(iii) Fibras.** Num ponto com ${\rm posto}\,dF=k$, pelo teorema do posto constante, $F^{-1}(F(p))$ é localmente uma
subvariedade de dimensão $n-k$:

| Caso | T0 | T | O | O0 |
|---|---|---|---|---|
| Circular, spins alinhados | 2 | 3 | 5 | 4 |
| Com $(e_0,\ell_0)$, em coordenadas cartesianas $(e_0\cos\ell_0,e_0\sin\ell_0)$ | 4 | 5 | 7 | — |

- **Precessão.** Os 4 componentes de spin no plano somam 4 dimensões; T vai para 7.
- **Por que vale perto do setor circular e alinhado.** Num ponto circular e alinhado de posto $k$, o jacobiano do mapa
  estendido contém as colunas do mapa restrito, então tem posto ≥ $k$, logo $=k$. O conjunto de posto máximo é aberto,
  e por isso a dimensão $n_{\rm ext}-k$ vale numa vizinhança. Exige-se só que as memórias sejam $C^1$ em
  $(e_0\cos\ell_0,e_0\sin\ell_0)$ e nos spins cartesianos.
- **Longe do setor circular** ($e_0$ grande, precessão forte), o posto não foi testado aqui. L16 e L10 tratam disso.

**(iv) Unicidade local.** Seja $F_r$ o mapa restrito às incógnitas, com $n_r$ colunas.
- (a) Se ${\rm posto}\,dF_r(p)=n_r$, $p$ é localmente identificável (imersão).
- (b) Se o posto é constante e igual a $r<n_r$ numa vizinhança, $p$ não é localmente identificável: a fibra tem dimensão
  $n_r-r>0$.
- (c) Nos loci de (ii), a primeira ordem não decide.

Como $k=4$, a unicidade local exige $n_r\le4$:

| Incógnitas | T0 | T | O |
|---|---|---|---|
| todas | fibra 2D | fibra 3D | fibra 5D |
| $\iota$ conhecido | curva | fibra 2D | 4D |
| $\iota$ e $D$ conhecidos | localmente identificável | curva ($\phi'$ desconhecido) | 3D |

No caso "$\iota$ e $D$ conhecidos", T0 é localmente identificável onde $\det\neq0$, isto é, fora das dobras.

*Demonstração:* (i) é trivial. (ii) sai dos lemas da §2.2. (iii) e (iv) são o teorema do posto constante e o da
função inversa aplicados a $F_r$. ∎

### 2.4 Redução (2,2) [D]

Com só $(2,\pm2)$ e $h_{2,-2}=\bar h_{22}$, a projeção $m=0$ de qualquer bilinear em $(h,\dot h)$ envolve só quatro
funções do tempo: $|\dot h_{22}|^2$, $|h_{22}|^2$, ${\rm Re}(\bar h_{22}\dot h_{22})=\tfrac12\,d|h_{22}|^2/du$ e
${\rm Im}(\bar h_{22}\dot h_{22})$. Os termos cruzados $(2,2)\times\overline{(2,-2)}$ têm $m=4$. Daí:

$$J_{\ell0}=c^J_\ell\,E,\qquad S_{30}=c^S\,H,\qquad \Phi_{\ell0}=c^\Phi_\ell\,H\ (\ell=1,3),\qquad K_{\ell0}=-\tfrac32M_f\,J_{\ell0}/\mathfrak D_\ell,$$

com $E=\int|\dot h_{22}|^2du$, $H=\int{\rm Im}(\bar h_{22}\dot h_{22})du$ e constantes $c$ universais (Gaunt). As formas
angulares ficam fixas:
- deslocamento $\propto\sin^2\iota\,(17+\cos^2\iota)$ (Favata 2009, eq. 4.5a [E]);
- spin $\propto\sin^2\iota\cos\iota$;
- CM ∝ deslocamento (a parte nula some);
- giroscópica $\propto Y_{10}+(c^\Phi_3/c^\Phi_1)\,Y_{30}$.

**Consequência.** Spin e giroscópica carregam a mesma informação intrínseca, porque ambas são proporcionais a $H$, e a
razão giroscópica/spin mede só $D$ (vezes uma forma angular). A informação intrínseca de T0 fica em três funções:
$E$, $H$ e $M_f=1-E_{\rm janela}-E_{\rm lig}(x_i;\lambda)$. Logo o posto intrínseco é ≤ 3 no limite (2,2), e o
quarto valor singular intrínseco mede a contribuição dos modos superiores.

## 3. Experimentos

Todos foram rodados de `codigo/` com `OMP_NUM_THREADS=1`, no máximo dois processos e saída filtrada.

| Script | O que faz | Tempo | Saídas |
|---|---|---|---|
| `exp17_comum.py` | `memorias_varias`: memórias de muitas janelas (vários $M$) a partir de uma onda; somas de cauda das matrizes de Gram; referenciais 'ti' e 'pico'; média da borda inicial; troca para $q<1$; opção de modelo e de lista de modos | — | — |
| `exp17_validacao.py` | (a) contra `observaveis`; (b) borda inicial; (c) erro do interpolante da tabela | 2 min | `exp17_validacao.txt` |
| `exp17_jacobianos.py` | grade $q\in\{1;1{,}2;2;3;5\}$, $\chi_{1,2}\in\{-0{,}6;0;0{,}6\}$, $M\in\{30,65,120\}$; diferenças centrais com $h,h/2,h/4$ ($h=4\times10^{-3}$ em $q,\chi$; $10^{-4}$ em $\ln M$); argumento `A` para o ponto A | 13 min (2 proc.) | `exp17_jacobianos_dados.npz`, `exp17_jac_A.npz` |
| `exp17_analise_jac.py` | SVD de T0, T, O, O0 nos casos livre / $\iota$ conhecido / $\iota$ e $D$ conhecidos / intrínseco, escalas 'abs' (linhas / $\lvert F(\iota=50^\circ)\rvert$) e 'rel', $\iota\in\{10,30,50,70,85,90\}^\circ$, $\phi'=k\pi/3$; posto pelo limiar de Weyl. Em $q=1$ a coluna $q$ usa derivada unilateral (§5) | 25 s | `exp17_jacobianos.txt`, `_resumo.json` |
| `exp17_interpreta.py` | ponto A, espaço nulo na carta do exp07, direção quase nula, fibra 1D de T com $(\iota,D)$, loci, dobra em $\iota$, razão CM/desl | 25 s | `exp17_interpretacao.txt` |
| `exp17_figura_jac.py` | figura dos valores singulares | 1 min | `figuras/e17_jacobiano.png` |
| `exp17_resolver.py` + `exp17_pares.py` | pares do exp07 re-resolvidos (T0 e T, 8 valores de $\phi'_B$); *match* com `comparar2` (FRAC_INICIO = 0,7, todos os modos, aLIGO e ET) | 13 min | `exp17_pares.txt/.json` |
| `exp17_fibra_tabela.py` | tabela de multipolos por $(q_B,\chi_{2B})$: 13 nós de Chebyshev em $\chi_1$ × 40 valores de $M\in[45,130]$, em diretório de rascunho | 23 min (2 proc.) | — |
| `exp17_fibra.py` | busca exaustiva no interpolante (81 × 121 × 179 em $\chi_1$, $M$, $\iota$), refino, agrupamento e polimento exato; T com 8 valores de $\phi'_B$ | 27 min (2 proc.) | `exp17_fibra_0_60/_60_117.json/.txt` |
| `exp17_fibra_resumo.py` | junta as partes, polimento extra, classificação, conexidade | 3 min | `exp17_fibra.json`, `exp17_fibra_resumo.txt` |
| `exp17_figura_fibra.py` | figura da fibra | — | `figuras/e17_fibra.png` |
| `exp17_dobra.py` | continuação exata em $\chi_{2B}$ ($q_B$ = 1,5; 2; 3) até a borda interior; segunda solução | 8 min | `exp17_dobra.txt` |
| `exp17_fibra_iD.py` | T com $\iota$ e $D$ conhecidos: continuação em $\phi'_B$ (Newton exato 4×4) | 2,3 min | `exp17_fibra_iD.txt/.json` |
| `exp18_reducao.py` | jacobiano completo contra só (2,2) | 3 min | `exp18_reducao.txt` |
| `exp18_proporcionalidade.py` | razões universais do limite (2,2) | 1 min | `exp18_proporcionalidade.txt` |
| `exp18_qchi.py` | Fisher da onda (IMRPhenomXAS e XHM, aLIGO e ET, $t_c$ e $\phi_c$ projetados) contra a direção quase nula da memória | 3 min | `exp18_qchi.txt` |
| `exp18_invariantes.py` | grandezas ao longo das 76 soluções exatas da fibra | 2 min | `exp18_invariantes.txt/.json`, `figuras/e18_invariantes.png` |
| `exp19_espectro.py` | L18: $\lvert X_{\ell0}\rvert$ até $\ell=10$, $q\in\{1,2,4,8\}$, 4 pares de spins, $Mf_0=0{,}004$; conteúdo de modos; PN | 12 s | `exp19_espectro.txt/.json`, `figuras/e19_espectro.png` |

## 4. Resultados

### 4.0 Infraestrutura (`exp17_validacao.txt`)

- **(a)** `memorias_varias`, gerando a onda desde o menor $f_0$, reproduz `observaveis.memorias_observaveis(todos_m=True)`
  com diferença máxima de 2e-15 a 1,2e-14 ($M$ = 65 e 80) e 1,7e-12 a 9e-12 ($M=120$). Isso está no nível do V4 do
  verificador (início auxiliar). $M_f$ e $t_i$ são idênticos.
- **Correção de convenção.** A fase orbital precisa ser ancorada no valor *enrolado* da fase de (2,2) no $f_{\rm ref}$ do
  gwsurrogate. Sem isso os $m$ ímpares trocavam de sinal: diferença de 3e-2, achada e corrigida durante o
  desenvolvimento.
- **(b)** Borda inicial dos $m\neq0$, relativa ao maior $m=0$: deslocamento 1,7e-6 a 2,6e-5; spin 1,5e-4 a 1,7e-3;
  CM 2,7e-4 a 1,3e-3; giroscópica 1,7e-5 a 1,8e-4 (cresce com $M$). A média a remove; trocar o comprimento da média muda
  o resultado em ≤ 4,4e-6.
- **(c)** Erro do interpolante da tabela no observador: mediana 3,2e-5 e máximo 1,8e-4 em T0; mediana 4,4e-5 e máximo
  2,0e-4 em T. Ele só localiza soluções; todas as soluções relatadas foram polidas com avaliações exatas.

### 4.1 Posto, valores singulares e loci (L01) — `exp17_jacobianos.txt`, `exp17_interpretacao.txt`, `figuras/e17_jacobiano.png`

**Ponto A**, escala 'abs' (`exp17_interpretacao.txt` (1)):

| Conjunto / caso | Valores singulares | $\tau$ |
|---|---|---|
| T0 livre | 4,353; 1,672; 0,6293; 0,1108 | 1,1e-5 |
| T0 com $\iota$ conhecido | 3,990; 0,806; 0,315; 0,0346 | |
| T0 intrínseco ($D$, $\iota$ fixos) | 3,094; 0,317; 0,0453; 9,50e-4 | |
| T livre ($\phi'=0$) | 4,369; 1,684; 0,631; 0,116 | |
| T com $\iota$ e $D$ conhecidos | 3,110; 0,314; 0,0348; 0,0170 | |
| T intrínseco ($\phi'$ fixo) | 3,110; 0,314; 0,0348; 0,0165 | |
| O livre | 2,748; 0,883 | |

- O limiar $\tau$ fica ≤ 1e-4 em T0 e ≤ 7,5e-4 em T, em toda a grade.
- A revisão R1, com deslocamento total, tinha 4,395; 1,665; 0,608; 0,115 para T0 livre e 3,147; 0,264; 0,0407; 6,59e-4
  para o intrínseco.
- **Os $m\neq0$ aumentam o 4º valor singular intrínseco de 9,5e-4 para 0,0165.** A direção fraca de T0 é quebrada pelos
  termos de borda da fusão (se $\phi'$ for conhecido).

**Grade.** Contagem de postos e menor $\sigma_{\rm último}/\tau$; $\iota$ em graus:

| Conjunto, caso | $\iota\le85$ | $\iota=90$ |
|---|---|---|
| T0 livre | 4 em todos (135/135); menor $\sigma_4$: 1,4e-3 (10°), 4,4e-3 (30°), 5,9e-2 (50°), 5,4e-2 (70°), 2,5e-2 (85°); $\min\sigma_4/\tau=71$ | 3 (135/135); $\sigma_4\le6{,}7\times10^{-12}$ |
| T0, $\iota$ conhecido | 4 (135/135) | 2 (135/135) |
| T0 intrínseco | 4 em 125–135 de 135; 3 em até 10 pontos ($q=1,\chi_1=\chi_2$, ou dobras) | 2 |
| T livre | 4 (810/810), $\min\sigma_4/\tau=14$ | 3 (810/810) |
| T, $\iota$ e $D$ conhecidos | 4 em 807–810 de 810 | 2 |
| O e O0, livre | 2 em todos | 2 em todos |
| O0, $\iota$ conhecido | 2 | 1 |

Medianas de $\sigma_4$ em T0 livre: 1,7e-2 ($\iota=10$), 0,10 (30), 0,11 (50), 0,22 (70), 0,084 (85).

**Loci** (`exp17_interpretacao.txt` (5)):

- **$\iota=90^\circ$, T.** As linhas de spin e giroscópica valem $|F|/|F_{\rm ref}|=1{,}5\times10^{-15}$. Fora da
  coluna $\iota$, seus elementos são ≤ 1,4e-11, contra $J_\iota=2{,}66$ e 2,25. Para deslocamento e CM,
  $J_\iota\le1{,}6\times10^{-10}$. Confirma H1.2.
- **$\iota=0$:**

  | Conjunto | Valores singulares | Posto |
  |---|---|---|
  | T0 | 1,379; 0; 0; 0 | 1 |
  | O0 | 0; 0 | 0 |
  | T | 1,379; 0,029; 0,019; 0,002 ($\tau=2{,}1\times10^{-6}$) | 4 |
  | O | 0,029; 0,004 | 2 |

  - No eixo, T tem deslocamento, spin e CM de 1,6e-3, 3,4e-4 e 4,6e-3 do valor a 50°. São as contribuições $m=2$.
  - **H1.3 refutada:** com todos os $m$ o polo não é locus de queda. Na prática o posto é dado por sinais ~1e-3
    (bordas da fusão).
- **$q=1$, $\chi_1=\chi_2$, T0, coluna $q$ unilateral:**

  | Grandeza | Valor | O que diz |
  |---|---|---|
  | $\lvert$col $q\rvert$ | 7,7e-3 a 1,3e-2 | deveria ser 0 |
  | $\lvert$col $\chi_1$ − col $\chi_2\rvert$ | 1,1e-3 a 7,4e-3 | deveria ser 0 |
  | $\lvert$col $\chi_1\rvert$ | 0,43 a 0,79 | escala de comparação |
  | $(F(1+h)-F(1))/(hF)$, $h$ = 4e-3, 2e-3, 1e-3 | ≈ −0,011, −0,009, −0,009 | não vai a zero |

  - **Violação da simetria pelo substituto, ~1% na derivada.** Pela L-troca, $(F(1+h)-F(1))/(hF)$ deveria ser $O(h)$.
  - Direto: $F(1,\chi_1,\chi_2)/F(1,\chi_2,\chi_1)-1$ = 1,3e-4 a 8,9e-4.
  - $\partial_qF(1,\chi_1,\chi_2)+\partial_qF(1,\chi_2,\chi_1)$ = 5e-4 a 1,4e-2 (relativo); deveria ser 0.
  - Consequência: com $\iota$ e $D$ conhecidos, $\sigma_{3,4}$ = (4,1e-3; 7,1e-4) em $\chi=-0{,}6$, onde o teorema
    prevê (0; 0). **H1.4 confirmada analiticamente; o modelo a respeita só até ~1e-3–1e-2.**
  - Em T a coluna $q$ vale 0,018–0,056: é a parte $m$ ímpar, física, como previsto pela L-troca.
- **Dobra genérica.** No ponto A com $\iota$ e $D$ conhecidos, $\det dF_r$ muda de sinal entre $\iota=37{,}0^\circ$ e
  $37{,}5^\circ$ ($\sigma_4=1{,}5\times10^{-5}$ e $1{,}4\times10^{-5}$, $\tau=7{,}8\times10^{-6}$; (5e); mergulho
  visível em `e17_jacobiano.png`). Ali o problema quadrado perde a unicidade local: dobra de Whitney, sem simetria.

**Espaço nulo de T0 na carta do exp07** (tangente da fibra 2D em A, (2)):
- $d(\ln M,\chi_1,\ln D,\iota)/dq=(+0{,}028;\,+0{,}013;\,-0{,}004;\,+0{,}61^\circ)$;
- $d/d\chi_2=(+0{,}014;\,-1{,}249;\,-0{,}054;\,+6{,}3^\circ)$.

Leitura física: a fibra troca sobretudo $\chi_2$ por $\chi_1$ (spin efetivo quase fixo) e $\iota$; $q$ entra com
coeficientes pequenos em A. Em $q=3$, $\chi=(-0{,}6,0)$ os coeficientes passam de 5 em $\chi_1$: a tangente gira muito
ao longo da grade (tabela em (2)).

**Direção quase nula intrínseca** ((3), `exp18_qchi.txt`, `exp18_reducao.txt`, `exp18_proporcionalidade.txt`):

- **Em A.** $v=(-0{,}026;-0{,}983;-0{,}143;+0{,}111)$ em $(\ln M,q,\chi_1,\chi_2)$, com $\sigma_4/\sigma_1=3{,}1\times10^{-4}$.
  Por unidade de $d\ln\eta$: $d\ln\mathcal M_c=+0{,}26$, $d\chi_{\rm ef}=-1{,}73$, $d\chi_a=-1{,}70$.
- **Na grade** (324 casos): mediana $d\chi_{\rm ef}/d\ln\eta=-1{,}70$ (percentis 10/90: −2,25/−0,79);
  $d\ln\mathcal M_c/d\ln\eta=+0{,}23$; $\sigma_4/\sigma_1$ mediano 1,06e-3 (percentis 10/90: 2,0e-4/3,7e-3).
- **A onda** (Fisher, IMRPhenomXAS/XHM, aLIGO e ET, $t_c$ e $\phi_c$ projetados):
  - em A a direção fraca tem $d\chi_{\rm ef}/d\ln\eta=+1{,}74$ (XAS) e +3,03 (XHM): **sinal oposto**;
  - $\cos(v_{\rm mem},v_{\rm onda})$ = 0,33–0,37;
  - $R=v_{\rm mem}^TGv_{\rm mem}/\lambda_{\min}(G)$ = 272 (XHM aLIGO) a 5,5e4 (XAS ET);
  - nos 6 pontos e 4 variantes, $R$ vai de 15 a 2,5e5;
  - em $q=2$, $\chi=(-0{,}6,0{,}6)$ as direções quase coincidem ($\cos$ = 0,97–0,995), mas mesmo assim $R$ = 99–3,7e3;
  - a onda mede a direção fraca da memória com 1σ = 1,2e-2 (aLIGO) e 3,8e-4 (ET), em unidades de $|v|=1$.
  - **H1.7 refutada** como identificação. As duas direções não coincidem em geral, e a onda resolve a da memória.
- **Origem verdadeira (redução (2,2)):**
  - Com só $(2,\pm2)$, as razões são universais a 7 algarismos em 7 sistemas: $J_{20}/E=0{,}0735760$ (= $C_E$ do 07),
    $S_{30}/H=-0{,}0291996$ ($=-C_J$, revisão item 12), $G_{10}/H=0{,}162868$, $G_{30}/H=-0{,}0533109$. A parte nula
    da CM é ≤ 1e-14 de $|h_{22}|^2$, ou seja, nula.
  - O jacobiano intrínseco (2,2) tem $\sigma_4$ = 2e-14 a 7e-13: posto exatamente 3 em 5 sistemas.
  - O completo tem $\sigma_4$ = 8,8e-4 a 6,8e-3. A direção quase nula é a quebra, pelos modos superiores, da identidade
    "spin ∝ giroscópica ∝ $H$".
  - **A redução (2,2) explica o jacobiano** em $\|J_{22}-J\|_F/\|J\|_F$ = 3–9%: os três primeiros valores singulares
    concordam a ~1–5% e um ângulo principal entre os espaços nulos 2D de T0 é 0,9°–6,5°.
  - **Não explica** o 4º valor singular (0,032–0,047 contra 0,079–0,116), o outro ângulo principal (35°–85°) nem a
    direção quase nula intrínseca (55°–86°).
  - Valores absolutos do modelo (2,2) contra o completo: de −22% a +13%.

**T com $\iota$ e $D$ conhecidos** (`exp17_fibra_iD.txt`). A curva de soluções exatas (resíduo ≤ 9,3e-11) foi seguida
por continuação a partir de A:

| Grandeza | De | A |
|---|---|---|
| $\phi'_B$ | −0,98 rad | +0,59 rad |
| $q$ | 1,018 | 1,208 |
| $M$ | 64,67 | 65,00 |
| $\chi_1$ | 0,22 | 0,40 |
| $\chi_2$ | −0,10 | −0,28 |
| $\chi_{\rm ef}$ | 0,064 | 0,073 |

- A curva sai do domínio fundamental pelos dois lados, em $q\to1$ (resíduo mínimo 7,5e-4 e 1,9e-3 com $q\ge1$ imposto).
  Pela troca, continua com rótulos trocados e $\phi'+\pi$.
- **H1.6 confirmada.** Mesmo com contraparte, as memórias com todos os $m$ não fixam $q$ (1,02 a 1,21) nem a divisão de
  spin; fixam $M$ e $\chi_{\rm ef}$.

### 4.2 Pares do exp07 com observáveis corrigidos (tarefa 3) — `exp17_pares.txt`

Alvo A:
- T0: $\Delta h_+=1{,}644983\times10^{-22}$ (janela; total no 07: 1,829e-22), spin −2,497911e-25 s, CM −2,792950e-26 s,
  giroscópica −3,156457e-41 rad.
- T ($\phi'_A=0$) / T0 − 1: +7,8e-4, +1,31e-2, −4,0e-3, +5,0e-3.

| $(q_B,\chi_{2B})$ | (a) par do 07 em T0, sem resolver (desl; CM) | (b) T0 resolvido: $M$, $\chi_1$, $D$, $\iota$; resíduo | T, 8 valores de $\phi'_B$: faixa de $\chi_1$; resíduo máx. | *match* aLIGO T0 ($\rho_{\rm crit}$) | *match* aLIGO T ($\rho_{\rm crit}$) | *match* ET T0 |
|---|---|---|---|---|---|---|
| (1, 0) | −2,6e-3; −2,4e-3 | 64,93; +0,074; 398,1; 50,56°; **9,7e-12** | 0,131 a 0,348; 2,3e-10 | 0,944 (3,0) | 0,962–0,992 (3,6–7,7) | 0,727 |
| (2, 0) | −1,6e-2; −2,3e-2 | 69,94; +0,166; 385,6; 55,59°; **4,7e-11** | 0,088 a 0,356; 7,4e-11 | 0,885 (2,1) | 0,776–0,973 (1,6–4,3) | 0,513 |
| (3, 0) | −9,5e-3; −2,5e-2 | 75,72; +0,456; 381,3; 57,64°; **1,1e-10** | 0,451 a 0,650; 1,0e-10 | 0,654 (1,2) | 0,437–0,669 (0,9–1,3) | 0,330 |
| (2, +0,5) | −3,6e-2; −4,9e-2 | 73,19; −0,190; 379,4; 58,99°; **1,7e-11** | −0,396 a +0,072; 7,4e-11 | 0,620 (1,2) | 0,529–0,818 (1,1–1,7) | 0,312 |
| (4, 0) | | sem solução: resíduo 8,7e-3, $\chi_1$ → 0,79 | | | | |
| (3, −0,5) | | sem solução: 1,7e-2 | | | | |
| (6, 0) | | sem solução: $\chi_1=0{,}8$, 6,6e-2 | | | | |

- SNR de A: 65,9 (aLIGO) e 901 (ET).
- As diferenças sem resolver vêm do deslocamento de janela; spin e giroscópica ficam em ~1e-6.
- **H1.8 confirmada.** Os quatro pares do 07 que eram exatos continuam exatos no piso da nova infraestrutura, em T0 e em
  T. Os três "aproximados" do 07 continuam sem solução no domínio. As formas de onda continuam distinguíveis com folga
  (SNR 66 ≫ $\rho_{\rm crit}$ ≤ 7,7).
- $M_f$ físico varia ao longo dos pares: $M_fM$ de B relativo a A = −0,01%, +8,5%, +18%, +14%. É a refutação do
  orçamento de cargas do exp16, refeita com observáveis corretos.

### 4.3 Fibra global (L02, tarefa 4) — `exp17_fibra_resumo.txt`, `exp17_dobra.txt`, `figuras/e17_fibra.png`

**Existência e números:**
- Grade $q_B$ = 1,0–4,0 (passo 0,25) × $\chi_{2B}$ = −0,8–0,8 (passo 0,2): **75 de 117 pontos** têm solução exata em
  T0 (resíduo < 1e-8 e $|\chi_1|\le0{,}8$), com 76 soluções ao todo.
- Faixas nas soluções: $\chi_1$ de −0,561 a +0,741; $M_B$ de 64,7 a 90,1; $D_B$ de 370,0 a 412,4 Mpc; $\iota_B$ de
  46,7° a 64,8°; $M_f$ físico de 61,3 a 87,4 $M_\odot$ (A: 61,7).
- Nenhum mínimo caiu na borda $M$ = 45 ou 130.
  - A faixa $M\in[45,130]$ se justifica pela razão $r$ = CM/(M desl): fica em [−0,62, −0,18] na grade de jacobianos
    ([−0,62, −0,35] para $q\le3$) e varia ≤ 4% com $\iota$ (`exp17_interpretacao.txt` (6)).
  - Pela equação da CM, $M_B=M_Ar_A/r_B\ge56$.

**Conexidade:** uma única componente (vizinhança de 4 na grade), com 75 pontos.

**Borda.** Há dois tipos:
- (i) a parede $|\chi_1|=0{,}8$, em $\chi_{2B}\le-0{,}6$ para $q_B\le1{,}5$, e no canto $q_B\ge3{,}5$. Ali há mínimos na
  parede com resíduo 4e-3 a 4e-2;
- (ii) **uma dobra interior**, entre $\chi_{2B}=-0{,}4$ e 0, para $q_B$ de 1,5 a 4. Ali há mínimos interiores não nulos,
  com resíduo exato 4e-4 a 8e-3.

**Continuação exata** (`exp17_dobra.txt`), descendo em $\chi_{2B}$ a $q_B$ fixo:

| $q_B$ | $\sigma_{\min}$ (3×3) | Última solução | Segunda solução | Depois |
|---|---|---|---|---|
| 1,5 | 0,010 → 0,002 | $\chi_{2B}=-0{,}40$, $\chi_1$ = 0,674 | em $\chi_1>0{,}8$: na parede, resíduo 3,7e-4 | resíduo mínimo 6,0e-4 |
| 2 | 0,011 → 0,002 | $\chi_{2B}=-0{,}36$, $\chi_1$ = 0,618 | $\chi_1$ = 0,722, $\iota$ 46,7°, resíduo 4,6e-12 | resíduo mínimo 8,3e-4 |
| 3 | 0,011 → 0,002 | $\chi_{2B}=-0{,}20$, $\chi_1$ = 0,675 | $\chi_1$ = 0,741, $\iota$ 50,4°, resíduo 2e-11 | resíduo mínimo 8,2e-4 |

A segunda solução de $q_B=3$, $\chi_{2B}=-0{,}2$ é o único ponto da grade com duas soluções exatas. É uma dobra:
- duas folhas da fibra se encontram;
- $d\chi_1/d\chi_2$ diverge;
- além dela não há solução real.

**H2.1 refutada em duas partes:**
- a projeção da fibra em $(q_B,\chi_{2B})$ não é injetiva perto da dobra: há uma segunda folha, quase toda fora do
  domínio ($\chi_1>0{,}8$, $\iota\approx40^\circ$–48°, $D\approx400$–490 Mpc), que é vista como mínimo na parede em
  quase todos os pontos;
- a borda inclui uma dobra, não só a parede.

**Confirmado:** conexidade e ausência de componentes isoladas na grade e no domínio.

**T** (todos os $m$, $\phi'_A=0$):
- 76 pontos com solução para algum dos 8 $\phi'_B$; 56 com solução para os 8.
- A região T difere da T0 só junto à borda:
  - só T: (1,0, −0,8), (1,0, −0,6), (1,25, −0,8), (1,25, −0,6), (1,75, −0,4);
  - só T0: (2,75, −0,2), (3,0, −0,2), (3,5, 0,0), (4,0, 0,2), perto da dobra.
- Em cada ponto as soluções formam uma curva em $\phi'_B$. Por exemplo, em (2,0, 0,0): $\chi_1$ de 0,088 a 0,356,
  $\iota$ de 52,0° a 57,2°, $D$ de 378,5 a 400,4 Mpc.
- Em 9 pontos há duas soluções T para o mesmo $\phi'_B$ (dobra).

### 4.4 Invariantes ao longo da fibra (tarefa 5) — `exp18_invariantes.txt`, `figuras/e18_invariantes.png`

Sobre as 76 soluções exatas:
- **As quatro memórias no observador ficam fixas a ≤ 3,5e-10**, conferência independente do polimento.
- **Variação relativa** $({\max}-{\min})/|A|$:

| Grandeza | Variação |
|---|---|
| $M$ | 0,39 |
| $q$ | 2,5 |
| $\eta$ | 0,36 |
| $\mathcal M_c$ | 0,21 |
| $\chi_{\rm ef}$ | 8,3 (0,007 a 0,61) |
| $D$ | 0,11 |
| $\iota$ | 0,36 |
| $M_f$ físico | 0,42 |
| $E_{\rm janela}$ física | 0,37 |
| $J_{20}$, $S_{30}$, $K_{20}$, $\Phi_{10}$ globais | 0,63; 0,53; 0,77; 0,50 |
| $\nu$ (fração nula da CM no observador) | de −0,21 a +0,16 |
| **$M_f(1+\nu)$** | **0,030** |
| $E_{\rm janela}\sin^2\iota(17+\cos^2\iota)/D$ | 0,16 |
| $\eta M\sin^2\iota(17+\cos^2\iota)/D$ (escala PN dominante) | 0,65 |

- **O que a fibra preserva.**
  - Exatamente, as quatro memórias: equivalem, com $D$ eliminado, às razões spin/desl ($\propto M\,S/J$, um
    "período orbital médio ponderado pela energia" vezes forma angular), CM/desl e giroscópica/desl².
  - Aproximadamente, a combinação física $M_f(1+\nu)$, porque CM/desl $\approx-\tfrac12M_f(1+\nu)\cdot$[forma quase
    independente de $\iota$]. A redução (2,2) mostra que $\nu$ vem inteira dos modos superiores.
  - **Nenhuma carga isolada** ($M_f$, $E$, multipolos globais) é preservada. A simetria PN dominante
    $(\eta,D)\to(\lambda\eta,\lambda D)$ não descreve a fibra (variação 65%).
- **Correlações ao longo da fibra:** $q$–$\chi_{\rm ef}$ +0,875; $M$–$\iota$ +0,92; $D$–$\iota$ −0,99. Ajuste
  $\chi_{\rm ef}\approx-1{,}02\ln\eta-1{,}41$ (rms 0,074): na fibra global, a memória troca razão de massas por spin
  efetivo no mesmo sentido da direção quase nula local.

### 4.5 L18: espectro de multipolos — `exp19_espectro.txt`, `figuras/e19_espectro.png`

Janela $Mf_0=0{,}004$, nível A, 16 sistemas. Valores relativos ao maior multipolo de cada tipo.

**Deslocamento** ($\ell$ = 2, 4, 6, 8, 10):

| Caso | $\ell=4$ | $\ell=6$ | $\ell=8$ | $\ell=10$ |
|---|---|---|---|---|
| $q=1$, $\chi=0$ | 1,7e-2 | 2,0e-4 | 4,0e-6 | 5e-13 (os modos ímpares se anulam por simetria) |
| $q=8$, $\chi=0$ | 8,8e-3 | 3,4e-4 | 2,9e-5 | 1,3e-6 |
| todos | 1,4e-3 a 2,0e-2 | 5,7e-7 a 4,1e-4 | | |

**Outras memórias:**
- Spin: $\ell=5$ entre 1,7e-4 e 8,8e-3; $\ell=7$ ≤ 1,8e-4.
- CM: $\ell=4$ entre 9,9e-4 e 3,7e-2.
- Giroscópica: $\ell=3/\ell=1$ entre 0,32 e 0,38 (0,327 no limite (2,2)); $\ell=5$ ≤ 7,6e-3.

**Contagem:** n(≥1e-2) é 1–2 no deslocamento, 1 no spin, 1–2 na CM e 2 na giroscópica; n(≥1e-3) é 1–3.
$N_{\rm ef}$ = 1,000–1,003 (1,206–1,277 na giroscópica). **H18.1 confirmada.**

**Dependência em $q$:**
- $\ell=4$ do deslocamento cai de ~1,7e-2 ($q=1$) para 2,6e-3 ($q=4$) e volta a 8,8e-3 ($q=8$);
- $\ell=6$ e 8 crescem com $q$ ($\ell=8$: 4e-6 → 3e-5).

**Conteúdo de modos ($\chi=0$).** $\ell\ge6$ não converge:
- em $q=4$, $\ell=6$ muda de 5,7e-7 (CCE) para 3,6e-5 com (3,1) e (4,2) (NRHybSur3dq8);
- (6,6) falta nos dois modelos, e pela contagem PN entra em $\ell=8$ e 10 na ordem dominante;
- $\ell=4$ muda 5–20% entre os modelos.

**PN** (Favata 2009, eq. 4.3, só inspiral até $x$ = 1/6 a 1/4): $\ell=6/\ell=2$ = 1,6e-5 a 2,3e-5 em $q=1$, contra 2,0e-4
no IMR. A fusão domina os $\ell$ altos. Em $q=8$: 1,2e-4 a 1,8e-4, contra 3,4e-4.

**No limite (2,2):** $J_{40}/J_{20}=\sqrt3/180=0{,}009623$ exatamente, $\ell\ge6$ em ~1e-17, o spin só tem $\ell=3$
(`exp18_reducao.txt`).

## 5. Tentativas de refutação e alternativas

1. **Limiar do posto.** O primeiro cálculo deu postos 1–3 espalhados e $\tau$ até 0,8. Rastreei a causa: em $q=1$ a
   diferença central atravessa $q=1$ pela extensão de troca, e o substituto viola a simetria. Há um salto
   $F(1,\chi_1,\chi_2)\neq F(1,\chi_2,\chi_1)$ de até 8,9e-4 e antissimetria de $\partial_q$ violada em ~1e-2.
   - Corrigi com derivada unilateral em $q=1$. Os postos ficaram limpos ($\tau\le10^{-4}$).
   - O defeito do modelo virou resultado (§4.1).
2. **Escala.** O posto foi decidido em duas escalas, 'abs' e 'rel', com o mesmo resultado fora de $\iota=90^\circ$, onde
   'rel' não se aplica.
   - Alternativas consideradas: limiar relativo a $\sigma_1$ (arbitrário) e menores 4×4 (equivalente).
   - Limitação: o limiar de Weyl só certifica o mapa do **modelo**.
3. **Borda inicial dos $m\neq0$.** Cinco abordagens:
   - janela abrupta (artefato de 1e-3);
   - início mais cedo (reduz pouco: $\propto x^{3,5}$);
   - subtração analítica da primitiva oscilatória (exigiria as taxas de todos os tipos);
   - referencial 'ti' (a borda final gira 450 rad por unidade de $\ln M$ e as derivadas não convergem);
   - média de Hann sobre o início: adotada; converge a 4,4e-6.
4. **Direção quase nula.** Testei três explicações:
   - $q$–$\chi_{\rm ef}$ da onda: refutada (§4.1);
   - leis de escala PN dominantes: a simetria $(\eta,D)$ do 07 mexe em $D$, e $D$ está fixo aqui;
   - redução (2,2): confirmada, posto intrínseco exatamente 3.

   O ângulo de 55°–86° entre as direções nulas dos dois modelos mostra que a *direção* é escolhida pela quebra (modos
   superiores), não pelo limite (2,2).
5. **Fibra.** Para não perder soluções:
   - busca exaustiva em grade densa 3D;
   - até 8 candidatos por ponto;
   - polimento exato, inclusive dos mínimos interiores com resíduo até 1e-2;
   - continuação exata independente em $\chi_{2B}$ (`exp17_dobra.py`), que confirmou a dobra por outro caminho;
   - candidatos na borda de $M$: nenhum.

   A primeira justificativa da faixa de $M$ (razão CM/desl entre −0,55 e −0,44) estava **errada**. O cálculo deu
   [−0,62, −0,18] e corrigi a docstring. A faixa continua suficiente por outro critério: nenhum mínimo na borda.
6. **Invariantes.** Candidatos testados: $M_f$, $E$, $J_{20}$, $\mathcal M_c$, $\eta M/D$ com forma angular, $E/D$ com
   forma angular, $M_f(1+\nu)$. Só o último fica em 3%; não é exato.
7. **Erro meu de processo.** Usei `pkill -f` com um padrão que casava com o meu próprio comando; morreu só o processo de
   análise, que refiz. Um laço de espera com `pgrep -f` travou pelo mesmo motivo; também refeito.

## 6. Contraexemplos e limitações

- **Erro do modelo.**
  - Simetria de troca violada em ~1e-3 (valores) e ~1e-2 (derivadas em $q$).
  - Níveis A e C diferem 0,3–9% nos multipolos dominantes (07).
  - $M_f$ conhecido a ~1e-4 (L00).
  - Valores singulares abaixo de ~1e-3 relativos (o 4º intrínseco de T0, as dobras) são do modelo e **não estão
    certificados fisicamente**.
- **Domínio.** $|\chi|\le0{,}8$, $q\le8$, spins alinhados, órbita circular. As dimensões com $(e_0,\ell_0)$ e com
  precessão valem só perto do setor circular e alinhado (lema de semicontinuidade). Longe dele não foram testadas.
- **Observáveis.**
  - Os $m\neq0$ de T dependem da definição (média sobre o início). Com janela abrupta mudam em até 1,7e-3 do $m=0$.
  - T supõe a base de polarização da fonte. Com o ângulo de polarização $\psi$ desconhecido, um detector mistura $h_+$
    e $h_\times$ (L07).
  - O não inclui padrões de antena.
- **Fibra.**
  - Interpolante com erro até 2e-4; todas as soluções relatadas foram polidas.
  - Para T a curva em $\phi'_B$ foi amostrada em 8 valores; a existência "para algum $\phi'$" pode deixar escapar
    intervalos estreitos.
  - A segunda folha foi vista só pela parede $\chi_1=0{,}8$. Sua extensão fora do domínio do modelo não é acessível.
- **L18.**
  - $\ell\ge6$ não converge nos modos de entrada (faltam (4,2), (3,1), (6,6) no CCE).
  - Os números de $\ell$ alto são ordens de grandeza.
  - Janela $Mf_0=0{,}004$: as razões de spin e giroscópica dependem da janela.
- **Fisher da onda.** Modelos fenomenológicos (IMRPhenomXAS/XHM); detector ótimo para $h_+$; sem marginalizar $D$,
  $\iota$, $\psi$.

## 7. Literatura e originalidade

Busca feita em:
- **API do arXiv:** "gravitational wave memory" AND degeneracy; memory AND identifiability; displacement memory AND spin
  memory AND parameter estimation; nonlinear memory AND inclination AND Fisher; orphan memory.
- **Crossref:** identifiability gravitational memory; memory parameter degeneracy spin center of mass; rank Jacobian
  gravitational wave observables degeneracy.
- **WebSearch:** memória e D–$\iota$; memória sozinha e degenerescência q–spin; multipolos de memória de $\ell$ alto;
  degenerescência $q$–$\chi$.
- **Fonte LaTeX de Favata 2009** (arXiv e-print), lida para os coeficientes PN.

| Referência | O que tem | Como conferi |
|---|---|---|
| Gasparotto et al., arXiv:2301.13228 (LISA) | a memória ajuda a quebrar a degenerescência $D$–$\iota$ da onda | resumo |
| Xu et al., PRD 109, 123034 (2024), arXiv:2403.00441 | idem, com a memória como acréscimo à onda | resumo |
| McNeill et al. 2017 e Ebersold & Tiwari 2020 | memória órfã: degenerescência qualitativa | já no projeto |
| Baird et al., PRD 87, 024035 (2013); Pürrer, Hannam & Ohme, arXiv:1512.04955 | degenerescência $q$–$\chi$ da onda | resumo; comparação quantitativa aqui |
| Favata 2009, PRD 80, 024002, eq. 4.3 [E] | espectro PN de inspiral da memória de deslocamento até $\ell=10$, com $\hat H_{60}\propto x(1-3612\eta/839)$ | texto da fonte |
| Talbot et al. 2018, arXiv:1807.00990 | os modos superiores mudam a memória em ~10% | resumo |
| Siddhant, Grant & Nichols, arXiv:2608.23739 | sinais e detecção de memórias superiores; o resumo não traz análise de identificabilidade | resumo |
| Nichols 2017; Faye & Seraj 2025; Seraj & Oblak 2023 | spin e giroscópica, ambas ligadas ao fluxo de momento angular | já no projeto |

**O que parece novo** (dentro do que achei; nenhum trabalho com análise de posto ou fibras do mapa parâmetros →
memórias integradas):
1. o teorema de identificabilidade com os loci exatos, inclusive o fato de que com todos os $m$ o polo deixa de ser
   locus de queda;
2. a curva residual em $(q,\chi_a)$ com contraparte EM no conjunto T;
3. a identidade exata do limite (2,2): spin ∝ giroscópica ∝ $H$, CM sem parte nula. É provavelmente implícita nas
   fórmulas PN (ambas ligadas ao momento angular irradiado), mas não a achei enunciada como degenerescência de
   parâmetros;
4. o mapa global da fibra com a dobra;
5. $M_f(1+\nu)$ como quase invariante.

**O que não é novo:** o espectro PN de inspiral (Favata 2009) e a constante $C_J$ (revisão, item 12).

## 8. Próximos experimentos

1. Repetir o posto e a fibra no nível C e com outro substituto (NRSur7dq4 na parte comum) para certificar
   fisicamente $\sigma_4^{\rm intr}$ e a dobra.
2. T com $\iota$ e $D$ conhecidos: seguir a curva através de $q=1$, aplicando a troca, para ver se fecha em laço.
3. Excentricidade e precessão: posto e dimensão da fibra longe do setor circular (com L16 e L10).
4. Padrões de antena e $\psi$ no conjunto O (com L07).
5. Mapa da dobra em 3D $(q_B,\chi_{2B},\chi_{1B})$, incluindo a segunda folha com um modelo válido em $|\chi|>0{,}8$.
6. L18: espectro com modelos de mais modos, (4,2) e (6,6), para fixar $\ell=6$–10.

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H1.1 | Posto genérico 4 (T0, T) e 2 (O), certificado | confirmada numericamente | `exp17_jacobianos.txt`: 135/135 e 810/810 com posto máximo para $\iota\le85^\circ$; $\min\sigma/\tau$ = 71 (T0) e 14 (T) |
| H1.2 | Queda exata em $\iota=\pi/2$ (T0, T → 3) e $\iota=0$ (T0 → 1, O0 → 0) | confirmada matematicamente e numericamente | lemas L-reflexão e L-polo; $\sigma_4\le7\times10^{-12}$; $(1,-1,1,-1)$ a 1e-10 |
| H1.3 | Com todos os $m$, $\iota=0$ também é locus de queda | refutada | T: σ = 1,379; 0,029; 0,019; 0,002 em $\iota=0$ (posto 4); O posto 2 |
| H1.4 | $q=1$, $\chi_1=\chi_2$: posto intrínseco 2 (T0) | confirmada matematicamente; no modelo só até ~1e-3–1e-2 | L-troca; coluna $q$ = 0,8–1,3e-2 e $\chi_1-\chi_2$ = 1–7e-3 no substituto (deveriam ser 0) |
| H1.5 | Fibras de dimensão $n-k$ (2/3/5; +2 excêntrica; +4 precessante) | confirmada matematicamente (circular: também numericamente) | teorema do posto constante e semicontinuidade; posto máximo na grade |
| H1.6 | Com $\iota$ e $D$ conhecidos: T0 identificável localmente, T não | confirmada (T0 fora das dobras) | T0 σ4 > τ em 125–135/135; T: curva com $q$ 1,02–1,21 (`exp17_fibra_iD.txt`) |
| H1.6b | O problema quadrado tem dobras genéricas sem simetria | confirmada numericamente | det muda de sinal em $\iota$ entre 37,0° e 37,5° em A |
| H1.7 | A direção quase nula intrínseca é a degenerescência $q$–$\chi_{\rm ef}$ da onda | refutada | sinal oposto de $d\chi_{\rm ef}/d\ln\eta$ em A; $R$ = 15–2,5e5 (`exp18_qchi.txt`) |
| H1.7b | Ela é a quebra, pelos modos superiores, da proporcionalidade exata spin ∝ giroscópica ∝ $H$ do limite (2,2) | confirmada matematicamente (limite (2,2)) e numericamente | razões universais a 7 algarismos; σ4 (2,2) ~ 1e-13 contra ~1e-3 completo |
| H1.8 | Pares exatos do exp07 persistem (T0, T) | confirmada numericamente (4 pares); os 3 aproximados seguem sem solução | resíduos 1e-11–1e-10; T em 8 azimutes ≤ 2,3e-10 |
| H2.1 | Fibra conexa, parametrizável por $(q_B,\chi_{2B})$, uma solução por ponto, borda só em $\lvert\chi_1\rvert=0{,}8$ | refutada em parte: conexa e sem componentes isoladas, mas com dobra (duas folhas) e borda interior | `exp17_fibra_resumo.txt`, `exp17_dobra.txt` |
| H2.2 | A fibra preserva $M_f$ e $E$ | refutada (de novo) | $M_f$ 42%, $E$ 37%; $M_f(1+\nu)$ preservado a 3% (não exato) |
| H2.3 | A redução (2,2) explica o jacobiano | confirmada em parte (σ1–σ3, um ângulo do espaço nulo); refutada para σ4 e a direção quase nula | `exp18_reducao.txt` |
| H18.1 | Espectro dominado por $\ell=2$ (1 número por memória; 2 na giroscópica) | confirmada numericamente | $N_{\rm ef}$ 1,000–1,003 (giroscópica 1,21–1,28); $\ell\ge6$ ≤ 4e-4 (não convergido nos modos) |
