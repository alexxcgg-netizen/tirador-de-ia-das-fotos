# L05, L06 e L07 — Quanta informação a memória sozinha carrega, e o que um detector mede (agente D3)

Sistema de referência: o "sistema A" do exp07 ($M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, $D=400$ Mpc,
$\iota=50°$), NRHybSur3dq8_CCE, janela desde 10 Hz, banda desde 10 Hz. Sinal de memória: a memória **nula** de
nível A (`observaveis.serie_memoria`, tipo `'nula'`, com a parte magnética), $\ell=2..8$, $m=0$; os modos $m=0$ do
substituto (`'rn'`, com o toque quase normal) entram só para comparar. Toda a maquinaria de janela, quadratura e
série vem de `codigo/observaveis.py` (L00).

**Resumo.**
- **L05.** Num detector, a memória nula de A fixa **3 direções** em CE ($\rho=34$): o instante ($\sigma_{t_0}=1{,}1$ ms),
  uma amplitude ($\cos\iota$ com $\ln D$) e uma escala de massa ($\sigma_{\ln M}=0{,}12$ contra 0,32 do prior);
  ~2,5 em ET ($\rho=8{,}6$); ~1 em aLIGO/A+, onde o Fisher nem vale ($\rho<1$). Dos 15,6 bits (CE) só 1,7 são
  sobre os parâmetros intrínsecos. A onda oscilatória fixa os 9 parâmetros (96 bits em CE, 42 intrínsecos).
- **Memória órfã (item 7 da revisão).** Minimizando sobre $M$, $D$, $\psi$, $t_0$, 72% do cubo
  $(q\in[1,6],\chi_{1,2}\in[-0{,}8,0{,}8])$ é indistinguível de A em CE com $\rho=34$ (79% com $\iota$ livre, 63%
  com $M$ fixo), e 100% em ET. Todos os pares
  do exp07 ficam dentro (1−match ≤ 2,6e-4 < 4,3e-4), mas com massas $M^*$ diferentes das do exp07: a família da
  série de memória não é a família das memórias integradas. A região tem 3 dimensões intrínsecas livres e uma
  quarta ($M$) com meia largura ~0,2 em $\ln M$; o que mais a limita é $q$ ($q\gtrsim4$ sai com $\rho\approx25$–40).
- **[D] A memória na banda não é um degrau.** A cauda da inspiral dá
  $1-|T(f)|\simeq c\,(2\pi fM)^{1/4}$, $c\propto\eta^{-1/4}/x_*$; numericamente a lei acerta a ordem de grandeza
  (razão 0,75–1,0 em $Mf=10^{-4}$, 0,5–1,7 até $10^{-2}$) com expoente efetivo 0,14–0,28. Isso vale também para a "memória órfã" de
  massa baixa ($M=6$): em $\rho=34$ ela exclui 41–47% do cubo, mais que A.
- **L07.** Um detector mede no máximo: instante, amplitude do degrau na banda e uma escala; uma rede acrescenta
  $\psi$. O spin entra com $\rho_\times=\rho_+/7$ a $\rho_+/10{,}6$; o valor integrado (DC) do spin nunca é medido
  (29% dele em 10 Hz). O CM é degenerado com $t_0$ sem a onda oscilatória; com ela, o atraso $M_f/2$ fica a 1σ
  em CE. A giroscópica não tem sinal. As quatro memórias integradas, **se** medidas a $1/\rho_+$ cada (idealização
  da etapa 6), dariam 2,5 vezes a informação intrínseca que a série de fato tem; o degrau final retém 35% dos bits e
  2–7% da parte intrínseca; MOPED retém 100% no fiducial e ≥ 99,2% em binárias bem diferentes.
- **L06.** (seção 4.7) Sem ruído, as quatro integradas preveem bem $\cos\iota$, $D$, $\mathcal M$, $M$, $M_f$ e mal $q$ e os spins; com ruído realista (CE), os valores integrados mensuráveis só guardam $|\cos\iota|$ e uma amplitude, e a **série** comprimida guarda a escala de massa ($R^2\approx0{,}5$ para $\ln M$, $\ln\mathcal M$, $\ln M_f$); em ET quase nada.

---

## 1. Pergunta e hipóteses

**L05.** Com ruído realista (aLIGO, A+, ET, CE), quantas combinações de parâmetros a memória sozinha determina,
com que precisão e quantos bits? Quanto vale a degenerescência da memória órfã quando se minimiza sobre a família?

**L06.** Sem supor modelo linear, quais parâmetros (e combinações) são previsíveis a partir de observáveis de
memória (integrados, mensuráveis, resumos da série), com e sem ruído?

**L07.** Quantos números de memória um detector e uma rede obtêm de fato, e quanto do Fisher da série é retido por
compressões (quatro memórias integradas, degrau final, MOPED)?

Hipóteses (status na seção 9):
- **H05.1** A memória na banda determina 2–3 combinações (amplitude, escala de tempo, instante); o resto é degenerado (09).
- **H05.2** A escala de tempo medida é $\sim M_f$.
- **H05.3** O Fisher vale (Vallisneri 2008) nas direções medidas em ET/CE e falha nas dominadas pelo prior.
- **H05.4** Junto da onda oscilatória a memória acrescenta pouca informação (só melhora $D$–$\iota$).
- **H05.5** [D] A memória na banda não é um degrau: $1-|T|\propto(Mf)^{1/4}$ com coeficiente $\propto\eta^{-1/4}/x_*$.
- **H05.6** A memória de um sistema de massa baixa (fusão acima da banda) carrega menos informação intrínseca que a de A com o mesmo $\rho$.
- **H05.7** (item 7) Minimizando sobre a família, a memória resolvida no tempo **não** separa os pares do exp07 de A.
- **H05.8** A região degenerada da memória órfã ocupa a maior parte do cubo intrínseco em CE com $\rho=34$.
- **H05.9** O vale $M^*(q,\chi)$ é uma curva de $M_f$ constante (ou de outra escala física simples).
- **H06.1** (09) Informação mútua e $R^2$ altos para $D/M$ e combinações de $M_f$ e $\iota$; baixos para $q$ e spins.
- **H06.2** Com ruído realista, a previsibilidade dos intrínsecos cai a quase zero; sobram combinações de amplitude.
- **H07.1** Um detector mede ≤ 2 números de memória além de $t_0$; uma rede acrescenta $\psi$.
- **H07.2** As 4 memórias integradas idealizadas superestimam a informação disponível.
- **H07.3** O degrau final (um número) retém a maior parte da informação **intrínseca** da série.
- **H07.4** MOPED retém todo o Fisher no fiducial e degrada longe dele.
- **H07.5** A memória de CM é mensurável como atraso do degrau quando a onda oscilatória fixa o resto.

## 2. Fundamentação e equações

**Sinal.** A memória nula de nível A (fluxo dos modos oscilatórios do NRHybSur3dq8_CCE, $\ell=2..8$, $m=0$) é
$h^{\rm mem}=h_+-ih_\times=\sum_L G_L(t)\,{}_{-2}Y_{L0}(\iota)$, com $G_L$ elétrico acumulado desde $t_i$ ($L$ par,
$h_+$) mais a parte magnética instantânea $h^B_L$ ($L$ ímpar, $h_\times$; sua integral é a memória de spin). Num
detector com $|F|=1$: $s=F_+h_++F_\times h_\times=\mathrm{Re}[e^{2i\psi}h]$ ($\psi=0$: detector ótimo para $+$, a
convenção de `snr2` do L00). Uma rede ideal de dois detectores co-localizados a 45° mede $h_+$ e $h_\times$.

**Espectro exato de um degrau mantido [D].** Com $s_k$ na rede $t_k$ (passo $\Delta t$), começando em zero (janela
de Tukey ancorada em $t_i$) e terminando constante, e $\Delta s_k=s_k-s_{k-1}$ de suporte compacto,
$$\tilde s(f)=\Delta t\,\frac{A(f)}{1-e^{-2\pi i f\Delta t}},\qquad A(f)=\sum_k\Delta s_k\,e^{-2\pi i f t_k}.$$
É a transformada exata da série discreta mantida para sempre (não há rampa nem patamar artificiais); é a versão
discreta da regularização de [VTRH2024] (transformar a derivada e dividir por $2\pi if$).

**Lei de escala em $M$ [D, elementar].** $s(t)=(M/D)\,S(t/M)\Rightarrow\tilde s(f)=(M^2/D)\,\hat S(Mf)$ e
$$\partial_{\ln M}\tilde s=(M^2/D)\,[\,2\hat S(F)+F\hat S'(F)\,]_{F=Mf},\qquad \hat S'(F)=\Delta t\Big[\frac{A'}{1-e}-\frac{A\,2\pi i\Delta t\,e}{(1-e)^2}\Big],\ A'=-2\pi i\sum t_k\Delta s_k e^{-2\pi iFt_k}.$$

**Fisher, prior e informação.** $\Gamma_{ij}=(\partial_is|\partial_js)$, $(a|b)=4\,\mathrm{Re}\int a\bar b/S_n\,df$
(ponto médio, bin da borda de 10 Hz com peso fracionário). Com prior gaussiano de desvios $\sigma_p$
(uniformes convertidos: largura$/\sqrt{12}$), o Fisher branqueado $\Gamma'=\Sigma_p^{1/2}\Gamma\Sigma_p^{1/2}$ tem
autovalores $\lambda'_i$; então
$$d_{\rm ef}=\sum_i\frac{\lambda'_i}{\lambda'_i+1},\qquad I(\theta;\text{dados})=\tfrac12\sum_i\log_2(1+\lambda'_i)\ \text{bits},$$
que é a forma invariante da fórmula do 09 (coincide com ela quando o prior é isotrópico). Cramér-Rao sem prior:
$\sqrt{(\Gamma^{-1})_{ii}}$; posterior gaussiano: $\sqrt{[(\Gamma+\Sigma_p^{-1})^{-1}]_{ii}}$. Informação sobre os
intrínsecos: $\tfrac12\log_2[\det\Sigma_{p,\rm int}/\det\Sigma_{\rm post,int}]$. Fisher reduzido (perfil em
parâmetros livres $E$): complemento de Schur $\Gamma_{II}-\Gamma_{IE}\Gamma_{EE}^{-1}\Gamma_{EI}$.

**Memória órfã num detector [D].** Com céu, $D$ e $\psi$ livres, o conjunto dos sinais de B num detector é o plano
gerado por $h_+^B$ e $h_\times^B$; o match máximo é $\sqrt{c^{\rm T}G^{-1}c}/\rho_A$ com
$c(\tau)=((s_A|h_+^B(\cdot-\tau)),(s_A|h_\times^B(\cdot-\tau)))$ e $G$ a matriz de Gram de $(h_+^B,h_\times^B)$,
maximizado em $\tau$ (sem maximizar fase: o sinal não é oscilatório). Critério: $1-\text{match}<1/(2\rho_A^2)$.

**Lei $(Mf)^{1/4}$ [D].** Na inspiral, em ordem dominante (Favata 2009),
$h_+^{\rm obs}(\tau)=Q\,\eta\,x(\tau)$, $x=\tfrac14(\eta\tau/5M)^{-1/4}$, $\tau=t_c-t$,
$Q=8\sqrt{\pi/5}\,[\tfrac{5}{14\sqrt6}Y_{20}(\iota)+\tfrac{1}{504\sqrt2}Y_{40}(\iota)]$. A taxa é
$\tfrac{A'}{4}\tau^{-5/4}$ com $A'=Q\eta\,\tfrac14(5M/\eta)^{1/4}$, e
$\int_0^\infty\tau^{s-1}(e^{i\omega\tau}-1)d\tau=\Gamma(s)(-i\omega)^{-s}$ ($s=-\tfrac14$) dá
$$\tilde h_+(f)=\frac{1}{2\pi if}\Big[\Delta H_{\rm tot}+\tfrac{A'}{4}\Gamma(-\tfrac14)(-2\pi if)^{1/4}+O(f)\Big],$$
$$T(f)\equiv\frac{2\pi if\,\tilde h_+}{\Delta H_{\rm tot}}=1-c\,(2\pi fM)^{1/4}e^{-i\pi/8}+\dots,\qquad c=\frac{|\Gamma(-\tfrac14)|}{16\,x_*}\Big(\frac{5}{\eta}\Big)^{1/4},\ x_*=\frac{\Delta H_{\rm tot}}{Q\eta}.$$
$\Delta H_{\rm tot}$ é a memória **total** (desde $x=0$): a dependência do início da janela cancela entre o degrau e a
cauda. Consequência: para $fM\ll1$ a forma da memória na banda depende dos intrínsecos só por $c\,M^{1/4}$, isto é,
por $M/(\eta x_*^4)$; com amplitude e instante, são 3 números (mais $\psi$ numa rede). A transformada exata do
"modelo mínimo" de Favata 2009 (eq. 14, função de Kummer $U(1,7/4,2\pi if\tau_{rr})$) contém essa correção
implicitamente; a expansão e sua consequência para a identificabilidade não foram encontradas enunciadas (seção 7).

**Compressões (L07).** Uma estatística linear $y=(u|x)$ tem média $(u|s(\theta))$ e covariância $(u_i|u_j)$; seu
Fisher é $J=D^{\rm T}(u|u)^{-1}D$, $D_{ij}=(u_i|\partial_js)$, e $J\le\Gamma$ (processamento de dados). MOPED
[HJL2000]: $u_i=\partial_is_{\rm fid}$, que dá $J=\Gamma$ no fiducial. As "quatro memórias integradas" não são
estatísticas lineares dos dados na banda; para elas uso $J=\nabla y^{\rm T}C_y^{-1}\nabla y$ com um erro suposto
(idealização) — esse $J$ pode exceder $\Gamma$, e o excesso mede o quanto a idealização promete além dos dados.

**L06.** Informação mútua por KSG (algoritmo 1, $k=5$, norma do máximo) depois de gaussianizar cada variável por
postos: $I=\psi(k)+\psi(N)-\langle\psi(n_x+1)+\psi(n_y+1)\rangle$. Previsibilidade: $R^2$ de validação cruzada
agrupada por binária intrínseca (os 4 sorteios extrínsecos de uma binária ficam na mesma dobra).


## 3. Experimentos

Todos com `OMP_NUM_THREADS=1`, no máximo dois processos Python, saídas filtradas como pedido. Sistema A: $M=65$,
$q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, $D=400$ Mpc, $\iota=50°$, $\psi=0$, janela desde 10 Hz, banda a partir de 10 Hz.
Priors (desvio do uniforme): $\ln M$ 0,317 ($M$ em fator 3), $q$ 0,866 ($[1,4]$), $\chi_{1,2}$ 0,462,
$\ln D$ 0,465 ($D$ em fator 5), $\cos\iota$ 0,577, $t_0$ 0,05 s, $\psi$ 0,907, $\phi$ 1,81.

| Script | O que faz | Saída |
|---|---|---|
| `codigo/exp24_comum.py` | módulo: taxas $m=0$ esparsas, espectro exato do degrau, lei de escala em $M$, Fisher, match no plano $(h_+,h_\times)$, derivadas numa grade qualquer | — |
| `codigo/exp24_fisher_memoria.py` | testes T1–T5; Fisher da memória nula (8 parâmetros) em aLIGO, A+, ET, CE, detector único e rede; Fisher reduzido; teste de Vallisneri; sistema de massa baixa ($M=6$) | `resultados/exp24_fisher_memoria.{txt,json}` (123 s) |
| `codigo/exp24_lei_quarto.py` | lei $(Mf)^{1/4}$: $1-|T|$ numérico contra a previsão, 6 binárias | `resultados/exp24_lei_quarto.{txt,json}` |
| `codigo/exp25_fisher_onda.py` | Fisher da onda oscilatória, da completa (osc + nula), de osc + modos $m=0$ do substituto e da memória (9 parâmetros com $\phi$), $\psi=0$ e $\pi/8$, rede | `resultados/exp25_fisher_onda.{txt,json}` (43 s) |
| `codigo/exp25_compressao.py` | L07: SNR por polarização, fração em banda, atraso de CM; compressões (a)–(d) e MOPED fora do fiducial | `resultados/exp25_compressao.{txt,json}` |
| `codigo/exp25_figuras.py` | figura `figuras/e24_fisher_memoria.png` (autovalores, desvios a posteriori, lei 1/4) | |
| `codigo/exp26_orfa.py` | memória órfã: 1−match mínimo sobre $(\ln M,\cos\iota)$, com $D,\psi,t_0$ livres, em 174 pontos $(q,\chi_1,\chi_2)$ (A) e 71 (massa baixa) | `resultados/exp26_orfa_{A,baixa}.json` |
| `codigo/exp26_analise.py` | frações degeneradas, largura do vale, Fisher contra perfil, o que fixa o vale; figura `figuras/e26_orfa.png` | `resultados/exp26_analise.{txt,json}` |
| `codigo/exp26_vale.py` | regressões do vale, índice espectral local | `resultados/exp26_vale.{txt,json}` |
| `codigo/exp27_conjunto.py` | L06: conjunto de binárias e observáveis (5 partes de 300 binárias, ~4,5 min cada) | `resultados/exp27_conjunto_{0..4}.npz` |
| `codigo/exp27_analise.py` | informação mútua (KSG) e $R^2$ (validação cruzada agrupada); figura `figuras/e27_informacao.png` | `resultados/exp27_analise.{txt,json}` |


## 4. Resultados

### 4.1 Testes da maquinaria (`exp24_fisher_memoria.txt`, T1–T5)

| Teste | Resultado |
|---|---|
| T1 série modal esparsa contra `observaveis.serie_memoria(magnetica=True)` | máx \|dif\|/máx\|s\| = 4,0e-15 (cerca de 20 vezes mais rápida: 0,6 s contra 12,4 s num teste à parte, máquina compartilhada) |
| T2 SNR $\rho_+$ (memória nula, $\psi=0$) | 0,47025 / 0,89203 / 8,63616 / 34,0874 (aLIGO / A+ / ET / CE), estável em $N=2^{18},2^{19},2^{20}$ a 4e-6. L00: 0,4702 / 0,8920 / 8,6405 / 34,0901; a diferença (5e-4 em ET) é o bin de 10 Hz com peso inteiro em `snr2`, que a verificação do L00 já apontou |
| T2 SNR $\rho_\times$ | 0,0670 / 0,1274 / 0,8135 / 3,2111; $\rho_+/\rho_\times$ = 7,0 / 7,0 / 10,6 / 10,6 (item 5 da revisão: 8–11) |
| T3 início da janela (8 a 16 Hz) e janela de Tukey (0,24 a 0,96 s) | 1−match ≤ 9,9e-10; SNR muda ≤ 1,6e-7 |
| T4 derivada em ln M (lei de escala) contra diferença finita física com início fixo em 10 Hz | diferença relativa 3,1e-3 (aLIGO) a 5,0e-3 (CE) com $h=10^{-2}$; cresce para $h$ pequeno (ruído da interpolação em F); a parte $\partial s/\partial\ln f_{\rm ini}$ (início da janela) vale 1,4e-3 a 3,3e-3 da derivada |
| T5 diferenças finitas em $q,\chi_1,\chi_2$ (passos 4e-3, 2e-3, 1e-3) | $\max|\Delta\Gamma|/\sqrt{\Gamma_{ii}\Gamma_{jj}}$ = 1,3e-4 e 3,4e-5; Richardson contra 1e-3: 1,1e-5; autovalores branqueados mudam ≤ 7,2e-4 |
| Onda oscilatória (`exp25_fisher_onda.txt`): janela (0,65 $f_0$, 6250 M) contra (0,62 $f_0$, 12500 M) | \|ds\|/\|s\| = 2,7e-4 (aLIGO) a 1,2e-3 (ET); diferenças finitas: 2,9e-3, Richardson 9,6e-4; autovalores ≤ 3,6e-3 |
| Massa baixa: início 0,86 $f_0$ (janela 1,5 vez mais longa) | 1−match 5e-12 a 7e-11 |

### 4.2 Fisher da memória sozinha, sistema A (`exp24_fisher_memoria.txt`, `.json`)

Detector único ($\psi=0$). $\lambda'$: autovalores do Fisher branqueado pelo prior (> 1: direção fixada pelos dados).
Desvios a posteriori com prior; entre parênteses, o do prior.

| | aLIGO | A+ | ET | CE |
|---|---|---|---|---|
| $\rho_+$ | 0,470 | 0,892 | 8,64 | 34,09 |
| $\lambda'$ (4 maiores) | 42,5; 0,37; 6,3e-3; 4,7e-5 | 154; 1,31; 0,022; 1,7e-4 | 5,8e3; 127; 1,25; 0,012 | 8,7e4; 1,97e3; 11,8; 0,11 |
| $d_{\rm ef}$ | 1,25 | 1,58 | 2,56 | 3,03 |
| $I(\theta;\text{dados})$ | 3,0 bits | 4,3 | 10,3 | 15,6 |
| $I$(intrínsecos) | 0,01 bits | 0,03 | 0,61 | 1,70 |
| $\sigma_{\ln M}$ (0,317) | 0,316 | 0,314 | 0,219 | 0,121 |
| $\sigma_{\cos\iota}$ (0,577) | 0,509 | 0,419 | 0,244 | 0,235 |
| $\sigma_{\ln D}$ (0,465) | 0,456 | 0,447 | 0,434 | 0,433 |
| $\sigma_{t_0}$ (50 ms) | 7,7 ms | 4,3 ms | 1,37 ms | 1,09 ms |
| $\sigma_q,\sigma_{\chi_1},\sigma_{\chi_2}$ | = prior | = prior | 0,86; 0,45; 0,46 | 0,85; 0,45; 0,46 |
| rede (+ e ×): $d_{\rm ef}$; $I$; $\sigma_\psi$ (0,907) | 1,66; 3,4; 0,70 | 2,30; 5,2; 0,49 | 3,62; 14,4; 0,059 | 4,46; 22,0; 0,015 |

**Autovetores (CE, detector único).** 1: $t_0$ (1,00). 2: $-0{,}90\cos\iota-0{,}36\ln D+0{,}15\chi_1+0{,}13\ln M$
— a amplitude, quase toda em $\cos\iota$ porque $h_+^{\rm mem}\propto\sin^2\iota$ e o prior de $\ln D$ é mais
estreito. 3: $+0{,}95\ln M-0{,}17\psi+0{,}13\cos\iota+0{,}13\chi_1$ — a escala de tempo. 4 ($\lambda'=0{,}11$, abaixo
de 1): $\psi$ com $q$. ET e A+ têm os mesmos três primeiros vetores. Com $\psi=\pi/8$ (ponto genérico, sem o
máximo de $\cos2\psi$): CE $\rho=24{,}7$, $d_{\rm ef}=2{,}92$, $I_{\rm intr}=1{,}21$ bits (`exp25_fisher_onda.txt`).

**Fisher reduzido aos intrínsecos** (complemento de Schur, perfil nos extrínsecos), autovalores branqueados:

| Perfil em | aLIGO | ET | CE |
|---|---|---|---|
| $\ln D,t_0$ | 6,3e-3; 4,8e-5 | 1,29; 0,012 | 12,2; 0,11; 7,4e-3 ($d_{\rm ef}$ 1,03) |
| $\ln D,t_0,\cos\iota,\psi$ | 7,3e-4 | 0,133 | 1,04; 1,0e-3; 4,7e-4 ($d_{\rm ef}$ 0,51) |

O primeiro autovetor é $-0{,}99\ln M-0{,}10\chi_1-0{,}06\chi_2$: a única direção intrínseca que a memória "vê"
localmente é uma escala de massa, e ela se mistura com $\iota$ e $\psi$ (o perfil nesses dois reduz 12,2 para 1,04).

**Sistema de massa baixa** ($M=6$, mesmos $q,\chi,\iota$; fusão ~3 kHz). $\rho$ em 400 Mpc: 0,121 / 0,232 / 1,54 /
5,42; $\rho_{\rm CE}=34$ em $D=63{,}6$ Mpc. Com o Fisher escalado para $\rho=34{,}09$:

| | aLIGO | A+ | ET | CE |
|---|---|---|---|---|
| $\lambda'$ de $\ln M$ (3º) | 3,32 | 3,69 | 2,56 | 0,88 |
| $d_{\rm ef}$; $I_{\rm intr}$ | 2,81; 1,01 | 2,83; 1,06 | 2,76; 0,89 | 2,49; 0,49 |
| reduzido ($\ln D,t_0,\cos\iota,\psi$) | 0,40 | 0,46 | 0,25 | 0,066 |
| $\sigma_{t_0}$ | — | — | 0,12 ms | 0,14 ms |

Com o mesmo $\rho$, a escala de massa de $M=6$ é 13 vezes menos informativa que a de A em CE (0,88 contra 11,8) e o
instante 8 vezes mais preciso. A escala aparece mais em aLIGO/A+ (relativamente mais sensíveis em kHz).

### 4.2b Comparação com a onda oscilatória e a completa (`exp25_fisher_onda.txt`)

Nove parâmetros (com $\phi$), detector único $\psi=0$. "Completa" = oscilatória + memória nula; "osc+RN" =
oscilatória + modos $m=0$ do substituto (com o toque quase normal).

| | aLIGO | A+ | ET | CE |
|---|---|---|---|---|
| $\rho$ oscilatória | 65,9 | 125,9 | 901 | 3201 |
| $d_{\rm ef}$ (de 9) | 8,28 | 8,74 | 8,99 | 9,00 |
| $I$ / $I_{\rm intr}$ (bits) | 48,3 / 19,7 | 56,1 / 22,8 | 82,4 / 35,7 | 95,7 / 41,6 |
| $\sigma_{\ln M}$; $\sigma_q$; $\sigma_{\chi_1}$; $\sigma_{\chi_2}$ | 2,9e-3; 0,060; 0,12; 0,16 | 1,8e-3; 0,037; 0,069; 0,093 | 3,1e-4; 6,9e-3; 0,013; 0,017 | 1,1e-4; 2,5e-3; 4,9e-3; 6,5e-3 |
| $\sigma_{\ln D}$; $\sigma_{\cos\iota}$; $\sigma_{t_0}$ | 0,097; 0,095; 64 μs | 0,052; 0,051; 34 μs | 9,0e-3; 9,1e-3; 5,6 μs | 3,9e-3; 4,0e-3; 2,3 μs |
| Cramér-Rao de $\ln D$: osc → completa → osc+RN | 0,1045 → 0,1034 → 0,1014 | 0,0533 → 0,0528 → 0,0519 | 9,00e-3 → 8,78e-3 → 8,61e-3 | 3,86e-3 → 3,57e-3 → 3,47e-3 |
| $I$ osc → completa | 48,32 → 48,33 | 56,14 → 56,15 | 82,45 → 82,49 | 95,71 → 95,82 |

Com a onda oscilatória presente, a memória só melhora a quebra distância–inclinação: 1% em aLIGO, 8% em CE
(10% contando o toque quase normal dos modos $m=0$), e acrescenta 0,01–0,1 bit. A diferença entre a memória
sozinha e a onda é de ~80 bits em CE: a memória contém $15{,}6/95{,}7\approx16\%$ dos bits e $1{,}7/41{,}6\approx4\%$
da informação intrínseca, mas quase tudo isso é redundante com a onda.

### 4.3 Validade do Fisher (Vallisneri) e perfil de verossimilhança

**Aproximação de sinal linearizado** (`exp24_fisher_memoria.txt`): deslocamentos de 1σ ao longo dos eixos do
posterior (Fisher + prior), com o sinal verdadeiro recalculado. Nos três eixos medidos:
CE $\Delta\chi^2_{\rm lin}$ = 1,000 / 0,999 / 0,922 contra $\Delta\chi^2$ verdadeiro 1,000 / 0,991 / 1,025, resto
$\varepsilon$ = 0,001 / 0,000 / 0,078; ET $\varepsilon$ = 0,014 / 0,000 / 0,135. Nos eixos dominados pelo prior o
Fisher falha completamente: $\varepsilon$ = 1091 (CE, eixo com $\delta\psi=-0{,}77$: em $\psi=0$ o sinal é
$\propto\cos2\psi$, estacionário, e a degenerescência $\psi$–$D$ é curva), 32 e 20 (CE, eixos com
$\delta q=+0{,}61$ e $\delta\chi_1=+0{,}36$), 83 (ET). Em aLIGO e A+ ($\rho<1$) não há detecção: os "bits" desses
detectores (3,0 e 4,3, quase todos em $t_0$) não têm significado operacional.

**Perfil contra Fisher** (`exp26_analise.txt`; ponto A, $q,\chi$ fixos, $\iota$ fixo, $D,\psi,t_0$ livres):

| $\Delta\ln M$ | −0,288 | −0,133 | −0,055 | +0,099 | +0,177 | +0,332 |
|---|---|---|---|---|---|---|
| 1−match (perfil, CE) | 3,08e-3 | 6,30e-4 | 8,74e-5 | 6,88e-5 | 2,58e-4 | 1,34e-3 |
| Fisher | 9,25e-4 | 1,97e-4 | 3,44e-5 | 1,11e-4 | 3,50e-4 | 1,23e-3 |
| razão | 3,33 | 3,19 | 2,54 | 0,62 | 0,74 | 1,09 |

A verossimilhança é assimétrica: massas menores são excluídas ~3 vezes mais depressa que o Fisher prevê, massas
maiores ~1,5 vez mais devagar. O intervalo de 1σ em CE (1−match = 4,3e-4) vai de $\Delta\ln M\approx-0{,}11$ a $+0{,}21$
(Fisher: ±0,20). Mesmo padrão em ET. Para $M=6$ a assimetria é maior (razões 2,7–5,6 de um lado, 0,64–1,09 do
outro).

**Globalmente o Fisher subestima a separação em $q$:** em $q=1{,}2$ o sinal depende de $q$ quase só por
$\eta$, estacionário em $q=1$; a varredura global (4.4) mostra que $q\gtrsim4$ é separável em CE.

### 4.4 Memória órfã: a região degenerada (`exp26_orfa_{A,baixa}.json`, `exp26_analise.txt`, `figuras/e26_orfa.png`)

1−match mínimo sobre $\ln M$ (varredura de 17 pontos + Brent) e $\cos\iota$ (Nelder-Mead), com $D,\psi,t_0$ livres,
em 160 pontos de Sobol de $(q,\chi_1,\chi_2)\in[1,6]\times[-0{,}8,0{,}8]^2$, mais A, os 7 pares do exp07 e 6
cantos. Limiar $1/(2\rho^2)$: 4,30e-4 (CE, $\rho=34{,}09$), 6,70e-3 (ET, $\rho=8{,}64$).

| Fração do cubo indistinguível de A | $M$ e $\iota$ livres | só $M$ livre ($\iota=50°$) | $M=65$ fixo |
|---|---|---|---|
| CE, $\rho=34$ | 0,79 | 0,72 | 0,63 |
| ET, $\rho=8{,}6$ | 1,00 | 1,00 | 1,00 |
| massa baixa, CE, $\rho=34$ ($D=63{,}6$ Mpc) | 0,59 | 0,55 | 0,53 |
| massa baixa, ET, $\rho=9{,}7$ / CE e ET em 400 Mpc | 1,00 | 1,00 | 1,00 |

- **$\rho$ necessário para excluir cada ponto** ($1/\sqrt{2\,\text{mm}_{\min}}$), percentis 10/50/90: A em CE
  29 / 61 / 471; em ET 21 / 43 / 344. Fração excluída com $\rho$ = 100, 300, 1000: 0,66, 0,83, 0,95 (CE).
  Massa baixa: CE 23 / 40 / 534; ET 19 / 34 / 425.
- **O que separa é sobretudo $q$** (figura e26, painel 1): 1−match mínimo de 1e-8 a 2e-5 perto de $q=1$, ~1e-4 em
  $q=3$, 3e-4 a 1e-3 em $q=5$–6, quase independente de $\chi_{\rm eff}$.
- **Forma:** um vale $M^*(q,\chi_1,\chi_2)$ (painel 2) com $M^*$ de 51,8 a 69,8 (desvio de $\ln M^*$ 0,066),
  curvatura mediana $1-\text{match}\approx0{,}0111\,(\ln M-\ln M^*)^2$ e meia largura 0,196 em $\ln M$ no limiar de
  CE. Para $M=6$ o vale é 15 vezes mais plano (0,00075; meia largura 0,76 em $\ln M$ com $\rho=34$). Ou seja: em CE com $\rho=34$, a região tem as três
  dimensões $(q,\chi_1,\chi_2)$ praticamente livres até $q\approx4$ e uma quarta ($\ln M$) de largura total ~0,4.
- **Artefato a registrar:** com $\iota$ livre, 82% dos ótimos vão a $\cos\iota\to0$. No plano $(h_+,h_\times)$ com
  amplitude livre, o limite $\iota\to90°$ mantém a direção de $h_\times$ com $D\to0$ e $\psi\to45°$, o que não é
  físico com um prior em $D$. Por isso uso como número principal a coluna "só $M$ livre".
- **Pares do exp07 (H05.7):** 1−match mínimo (CE) 1,1e-8 ($q_B=1$), 1,3e-5 ($q_B=2$), 6,5e-5 ($q_B=3$), 7,0e-5
  ($q_B=4$), 2,6e-4 ($q_B=6$), 2,9e-5 ($q_B=2,\chi_2=0{,}5$), 1,1e-5 ($q_B=3,\chi_2=-0{,}5$): todos abaixo de 4,3e-4.
  As massas que os igualam a A são $M^*$ = 65,3; 63,5; 59,7; 53,9; 53,3; 64,0; 56,6, e não as do exp07 (65,0;
  69,5; 73,7; 75,4; 83,6; 72,3; 70,2). Com $M$ fixo em 65, $q_B=4$ (7,0e-4) e $q_B=6$ (1,3e-3) saem.
  **Resposta ao item 7:** a revisão (rev_R1_detector, com $M$ e $\iota$ do exp07 e modos de RN) separava os pares
  com $\rho_{\rm crit}\approx3$–14; minimizando sobre a família, nenhum se separa de A com $\rho=34$ em CE. Os pares
  continuam ambíguos para a memória órfã, mas por outra família: a que iguala a **série** tem outro $M$, e a
  interseção com a família das quatro memórias integradas não é a mesma curva.

### 4.5 Lei $(Mf)^{1/4}$ e o vale (`exp24_lei_quarto.txt`, `exp26_analise.txt`, `exp26_vale.txt`)

$1-|T|$ numérico (espectro exato da série nula, normalizado pela memória total) contra a previsão de ordem dominante
$c\cos(\pi/8)(2\pi Mf)^{1/4}$:

| $(q;\chi_1,\chi_2)$ | $x_*$ | $c$ | razão em $Mf=10^{-4}$ | $10^{-3}$ | $10^{-2}$ | expoente em $[10^{-4},10^{-3}]$ |
|---|---|---|---|---|---|---|
| (1,2; 0,3, −0,2) | 0,446 | 1,457 | 0,876 | 0,780 | 0,866 | 0,198 |
| (1; 0, 0) | 0,425 | 1,526 | 0,864 | 0,759 | 0,825 | 0,191 |
| (4; 0, 0) | 0,254 | 2,851 | 0,804 | 0,646 | 0,550 | 0,152 |
| (1; 0,8, 0,8) | 0,845 | 0,767 | 1,005 | 1,062 | 1,660 | 0,277 |
| (1; −0,8, −0,8) | 0,279 | 2,323 | 0,752 | 0,583 | 0,541 | 0,136 |
| (3; 0,5, −0,5) | 0,398 | 1,748 | 0,881 | 0,781 | 0,811 | 0,197 |

A lei dá a ordem de grandeza e o sinal da dependência em $x_*$ (memória total maior → menos desvio do degrau), mas
as correções de ordem superior (relativas $\sim(Mf)^{1/4}$, PN e spin-órbita) são grandes: razões de 0,54 a 1,66
e expoentes efetivos de 0,14 a 0,28. Em 10 Hz o desvio do degrau é grande: 0,24 para $M=6$ ($Mf=3\times10^{-4}$)
e ~0,40 para A ($Mf=3{,}2\times10^{-3}$), normalizando pela memória total.

**O que fixa o vale (H05.9).** Desvio padrão, nos 174 pontos de A, de cada candidato a "escala medida":
$\ln M^*$ 0,066; $\ln(M^*m_f)$ 0,071; $\ln(M^*m_f/\omega_{220})$ 0,208; largura a meia altura da taxa 0,100;
desvio padrão da taxa 0,092; massa de chirp 0,167; lei de ordem dominante $\ln[M^*/(\eta x_*^4)]$ 1,68. Nenhuma é
mais constante que o próprio $M^*$. Para $M=6$: 0,343; 0,354; 0,492; 0,249; 0,393; 0,310; 2,01 (a largura da taxa
é a menos ruim). Descrição empírica (`exp26_vale.txt`): $\ln M^*$ depende sobretudo de $\chi_{\rm eff}$, $\ln M^*\approx4{,}12-0{,}12\,\chi_{\rm eff}$ ($R^2=0{,}54$); linear em $(\eta,\chi_{\rm eff},\chi_a)$, $R^2=0{,}65$; quadrático em $(q,\chi_1,\chi_2)$, $R^2=0{,}72$ com resto 0,035. Esse resto é da ordem da largura do fundo do vale: as posições ótimas em CE e ET diferem com desvio 0,029 (média −0,001). Hipótese do índice espectral (com amplitude livre a banda vê a forma de $|T|$ a menos de escala): o índice local $n=d\ln|F\hat h_+|/d\ln F$ em $f_c=22$ Hz tem desvio 0,036 ao longo do vale contra 0,061 com $M$ fixo — o vale tende a igualar a inclinação espectral na banda (fator 1,7), mas não só ela. Para $M=6$ o vale nem é bem definido (desvio de $\ln M^*$ 0,34; CE e ET diferem 0,20; índice 0,033 contra 0,023).

### 4.6 L07: o que um detector mede (`exp25_compressao.txt`)

**Valores integrados de A** (janela desde 10 Hz, $m=0$, nível A): deslocamento 1,6450e-22; spin −2,4979e-25 s;
CM −2,7929e-26 s; giroscópica −3,1565e-41 rad; $M_f=0{,}9498\,M$. O degrau final da série nula coincide com o
deslocamento de janela (2e-15).

**Fração em banda.** Normalizando pelo degrau de janela, $|2\pi f\tilde h_+(f)|/\Delta h_+$ vale 0,851 (1 Hz),
0,679 (10 Hz), 0,570 (20 Hz), 0,317 (50 Hz), 0,097 (100 Hz), 0,004 (200 Hz). Para a memória de spin,
$|\tilde h_\times(f)|/|\int h_\times du|$ vale 0,486 (1 Hz), 0,292 (10 Hz), 0,225 (20 Hz), 0,111 (50 Hz), 0,031
(100 Hz): o valor integrado (DC) do spin nunca é medido; o que entra na banda é o pulso $h_\times$.
(Com o espectro em $f\to0$, $\int h_\times du=2{,}435\times10^{-25}$ s contra o valor de janela 2,498e-25 s; a
diferença de 2,5% é o primeiro bin, 0,024 Hz, e a janela de Tukey.)

| Detector | $\rho_+$ | $\rho_\times$ | $\rho_+/\rho_\times$ | $f_{\rm rms}$ (Hz) | $\sigma$(atraso só da memória) | $|{\rm CM}/\Delta h_+|$ | razão |
|---|---|---|---|---|---|---|---|
| aLIGO | 0,470 | 0,067 | 7,0 | 44,1 | 7,67 ms | 0,170 ms | 0,02 |
| A+ | 0,892 | 0,127 | 7,0 | 44,2 | 4,04 ms | 0,170 ms | 0,04 |
| ET | 8,64 | 0,813 | 10,6 | 28,1 | 0,656 ms | 0,170 ms | 0,26 |
| CE | 34,09 | 3,21 | 10,6 | 27,5 | 0,170 ms | 0,170 ms | 1,00 |

O $\sigma$ do atraso é o de um deslocamento no tempo **só da memória** com os demais parâmetros fixados pela onda
oscilatória ($\sigma_{t_0}$ da onda em CE: 2,25 μs) e a amplitude da memória livre (a mesma coisa a 3 algarismos).
A memória de CM, lida como atraso $|{\rm CM}/\Delta h_+|\approx M_f/2$ do degrau (item 4), fica a 1σ em CE para o
sistema A e a 0,26σ em ET; sem a onda oscilatória o CM é degenerado com $t_0$ (o $\sigma_{t_0}$ da memória
sozinha em CE é 1,1 ms com prior, 27 ms sem prior).

**Compressões** (informação mútua gaussiana com os priors; "retida" = $I_y/I_{\rm série}$ do mesmo arranjo):

| Compressão | ET: $I$ (bits) | retida | $I_{\rm intr}$ | CE: $I$ (bits) | retida | $I_{\rm intr}$ |
|---|---|---|---|---|---|---|
| série, detector único | 10,34 | 100% | 0,61 | 15,59 | 100% | 1,70 |
| série, rede (+ e ×) | 14,37 | 100% | 0,64 | 22,03 | 100% | 1,97 |
| (a-ideal) 4 memórias integradas, erro 1/ρ+ cada | 8,64 | 84% | **1,56 (256%)** | 15,32 | 98% | **4,28 (251%)** |
| (a-real) amplitudes dos moldes + e × (rede) | 5,12 | 36% | 0,04 (7%) | 9,10 | 41% | 0,04 (2%) |
| (b1) degrau: amplitude do molde + | 3,50 | 34% | 0,04 (7%) | 5,47 | 35% | 0,04 (2%) |
| (b2) degrau: $\Delta h_+$ com erro $\Delta h/\rho_+$ | 3,53 | 34% | 0,06 (10%) | 5,51 | 35% | 0,06 (4%) |
| (d) amplitude + instante | 9,75 | 94% | 0,04 (7%) | 13,68 | 88% | 0,04 (2%) |
| (c) MOPED, 8 números (no fiducial) | 10,34 | 100% | 0,61 | 15,59 | 100% | 1,70 |

- As quatro memórias integradas, **se** cada uma fosse medida com erro relativo $1/\rho_+$ (a idealização implícita
  da etapa 6), dariam 2,5 vezes mais informação sobre os intrínsecos do que a série inteira de fato contém. A
  idealização superestima: o spin entra com $\rho_\times\approx\rho_+/10$, o CM é degenerado com $t_0$ e a
  giroscópica não tem sinal na banda.
- O degrau final (um número) retém ~35% dos bits e quase nada dos intrínsecos (2–7%). Amplitude e instante
  juntos retêm 88–94% dos bits: quase toda a informação da memória sozinha é extrínseca (instante e amplitude).
- **MOPED fora do fiducial** (vetores de A aplicados a outra binária B, mesmo $t_0$): retém 100% para
  $M=70$, para $q=2,\chi=0$ e para $\iota=80°$; 99,8% para $M=45,q=1,\chi=-0{,}5$; 99,2–99,3% para
  $M=100,q=3,\chi=+0{,}5$ (ET, CE). Oito números fixos comprimem sem perda a memória de binárias muito diferentes:
  o conjunto dos sinais de memória é quase plano (baixa dimensão) na métrica do ruído, o que é a própria
  degenerescência vista por outro ângulo.

### 4.7 L06: informação mútua e aprendizado (`exp27_conjunto_{0..4}.npz`, `exp27_analise.txt`, `figuras/e27_informacao.png`)

**Conjunto.** 1500 binárias intrínsecas (Sobol: $M\in[40,120]$, $q\in[1,4]$, $\chi_{1,2}\in[-0{,}8,0{,}8]$) × 4
sorteios extrínsecos ($\cos\iota$ uniforme, $D\propto D^2$ em [200, 1000] Mpc, $\phi$ uniforme) = 6000 amostras,
sem falhas (5 partes de ~4,5 min com 2 processos). Rede ideal (+ e ×, $\psi=0$ conhecido). SNR da memória nula
($h_+$): CE mediana 11,2 (10%–90%: 2,8–29,1); ET 2,9 (0,7–7,5). Controle: degrau da série = deslocamento integrado
$m=0$ a 1e-14. Ruído "real" de (b): $\sigma_{\Delta h}=\Delta h_A/\rho_{+,A}$ e $\sigma_{\rm spin}=|{\rm spin}_A|/\rho_{\times,A}$
(nível absoluto do detector, calibrado em A); "ideal" de (a): as quatro com erro $|y_A|/\rho_{+,A}$.

**Controle do estimador KSG** (gaussianas com $I$ exata 0,068 e 1,198 bits): dim 1: 0,072 e 1,221; dim 4: 0,078 e
1,109; dim 9: 0,047 e 0,702. Em 8–9 dimensões o KSG subestima (até 40%): os $I$ dos resumos (c) são cotas
inferiores; para comparar conjuntos de dimensões diferentes uso o $R^2$.

$R^2$ (HistGradientBoosting, validação cruzada de 5 dobras agrupada por binária), extrato:

| Observáveis | $\ln M$ | $q$ | $\chi_1$ | $\chi_2$ | $\ln D$ | $\cos\iota$ | $|\cos\iota|$ | $\ln M_f$ | $\ln\mathcal M$ | $\chi_{\rm eff}$ | $\ln(\eta M/D)$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| (a) 4 integradas, sem ruído | 0,83 | 0,26 | 0,28 | 0,08 | 0,91 | 0,99 | 0,94 | 0,82 | 0,91 | 0,38 | 0,93 |
| (a) 4 integradas, erro ideal (CE) | 0,69 | 0,18 | 0,18 | 0,01 | 0,78 | 0,97 | 0,90 | 0,68 | 0,78 | 0,26 | 0,86 |
| (b) desl.+spin, sem ruído | 0,38 | 0,10 | 0,08 | −0,06 | 0,20 | 0,96 | 0,89 | 0,37 | 0,45 | 0,11 | 0,64 |
| (b) desl.+spin, ruído real (CE) | 0,08 | 0,06 | 0,06 | −0,08 | 0,16 | 0,37 | 0,52 | 0,06 | 0,15 | 0,07 | 0,39 |
| (c1) MOPED, sem ruído (CE) | 0,85 | 0,40 | 0,24 | −0,04 | 0,50 | 0,84 | 0,80 | 0,84 | 0,84 | 0,21 | 0,69 |
| (c1) MOPED, com ruído (CE) | 0,50 | 0,21 | 0,11 | −0,09 | 0,23 | −0,01 (lin. 0,27) | 0,42 | 0,48 | 0,50 | 0,09 | 0,38 |
| (c2) banco de 9 moldes, com ruído (CE) | 0,35 | 0,17 | 0,04 | −0,08 | 0,14 | −0,14 | 0,35 | 0,35 | 0,32 | 0,06 | 0,32 |
| (c3) potência em 9 bandas, com ruído (CE) | 0,04 | 0,14 | 0,04 | −0,09 | 0,15 | −0,10 | 0,21 | 0,03 | 0,08 | 0,04 | 0,25 |
| (c) c1+c2+c3, com ruído (CE) | 0,49 | 0,21 | 0,11 | −0,06 | 0,24 | −0,03 | 0,43 | 0,47 | 0,50 | 0,10 | 0,38 |
| (c) c1+c2+c3, com ruído (ET) | 0,13 | 0,13 | 0,04 | −0,07 | 0,15 | −0,08 | 0,24 | 0,13 | 0,16 | 0,04 | 0,25 |

Informação mútua KSG (bits), mesmos conjuntos: (a) sem ruído $\cos\iota$ 2,95, $|\cos\iota|$ 2,14,
$\ln(\eta M/D)$ 1,70, $\ln\mathcal M$ 1,39, $\ln M$ 1,00, $\ln D$ 0,97, $q$ 0,20, $\chi_1$ 0,24, $\chi_2$ 0,08;
(b) com ruído real (CE): $\cos\iota$ 1,25, $|\cos\iota|$ 0,78, $\ln(\eta M/D)$ 0,48, $\ln M$ 0,14; (c1) MOPED com
ruído (CE): $\ln M$ 0,59, $\ln\mathcal M$ 0,65, $\ln M_f$ 0,56, $\cos\iota$ 0,60, $q$ 0,24, $\chi_{1,2}$ ≤ 0,14.

- **Sem ruído** (H06.1): as quatro integradas determinam $\cos\iota$ ($R^2$ 0,99), $\ln(\eta M/D)$ (0,93), $\ln D$
  (0,91), $\ln\mathcal M$ (0,91), $\ln M$ (0,83), $\ln M_f$ (0,82); mal $q$ (0,26), $\chi_1$ (0,28), $\chi_2$ (0,08),
  $\chi_{\rm eff}$ (0,38). Confirma o 09, com $\cos\iota$ (pelo sinal do spin e pela giroscópica) acima de $D/M$.
- **Com ruído realista** (H06.2): os valores integrados mensuráveis (b) perdem quase tudo de intrínseco
  ($\ln M$ 0,08); sobram $|\cos\iota|$ (0,52) e a amplitude $\ln(\eta M/D)$ (0,39). A **série** comprimida
  (MOPED) guarda a escala de massa: $\ln M$ 0,50, $\ln\mathcal M$ 0,50, $\ln M_f$ 0,48 em CE (SNR mediana 11); em
  ET cai para 0,12–0,16. Os resumos invariantes no tempo (banco, bandas) ficam abaixo do MOPED (que usa o $t_0$
  verdadeiro, uma vantagem). $q$ chega a 0,21 e os spins individuais a ~0 em todos os casos com ruído.
- O HGB perde para a regressão linear em alguns casos ruidosos ($\cos\iota$ com MOPED: −0,01 contra 0,27):
  pouco sinal e muito ruído favorecem o modelo mais simples.

## 5. Tentativas de refutação e alternativas

1. **"3 direções em CE" seria artefato do ponto $\psi=0$?** Em $\psi=0$ o termo $\cos2\psi$ é estacionário. Refeito
   em $\psi=\pi/8$: $d_{\rm ef}$ 2,92 contra 3,03, $I_{\rm intr}$ 1,21 contra 1,70 bits; os três autovetores são
   os mesmos. Robusto.
2. **A escala de massa viria do início da janela ou do toque quase normal?** Início entre 8 e 16 Hz e janela de
   Tukey entre 0,24 e 0,96 s mudam o sinal na banda em ≤ 1e-9 (1−match); $\partial s/\partial\ln f_{\rm ini}$ é
   ≤ 3,3e-3 da derivada em $\ln M$. O sinal é a memória nula (sem toque quase normal); com os modos $m=0$ de RN o
   Cramér-Rao de $\ln D$ muda só 3%.
3. **O Fisher vale?** Teste de Vallisneri (4.3): sim nas três direções medidas em CE ($\varepsilon\le0{,}08$) e ET
   ($\le0{,}14$), não nas demais. Perfil em $\ln M$: assimetria de fator 3. Varredura global: o Fisher local
   subestima a separação em $q$ (ponto quase simétrico $q\approx1$).
4. **"Quase todo o cubo é degenerado" seria artefato da liberdade em $\iota$ ou do plano $(h_+,h_\times)$?** Com
   $\iota$ fixo a fração cai de 0,79 para 0,72; com $M$ também fixo, 0,63. A conclusão não depende dessas
   liberdades. O limite $\cos\iota\to0$ foi identificado como artefato ($D\to0$) e excluído do número principal.
5. **H05.9 (o vale é $M_f$ constante) falhou.** Abordagens tentadas, nenhuma mais constante que $M^*$ (seção 4.5):
   (i) $M_f$ (surfinBH), (ii) $M_f/\omega_{220}$ (frequência do QNM, pacote `qnm`), (iii) largura a meia altura da
   taxa de memória, (iv) desvio padrão da taxa, (v) massa de chirp, (vi) lei de ordem dominante $M/(\eta x_*^4)$,
   (vii) regressões em $(q,\chi_1,\chi_2)$ e $(\eta,\chi_{\rm eff},\chi_a)$, (viii) $M^*+k\chi_{\rm eff}$ e
   $M^*E_{\rm rad}$, (ix) índice espectral local no centro da banda (`exp26_vale.txt`). Nenhuma explica o vale melhor que $\ln M^*$ mais uma correção linear em $\chi_{\rm eff}$; a descrição que resta é empírica ($R^2$ 0,54–0,72) e o índice espectral explica só parte. Conclusão: a versão "$M_f$ constante" está refutada; o vale é uma propriedade da forma completa do espectro na banda.
6. **H05.5 (lei 1/4).** Tentei refutá-la com seis binárias de $q$ e spins extremos: a ordem de grandeza resiste, o
   coeficiente não (razões 0,54–1,66). Classifico como lei assintótica qualitativa.
7. **H05.6 (massa baixa carrega menos informação).** O Fisher local confirma (escala de massa 13 vezes menos
   informativa), mas a varredura global refuta a versão forte: com o mesmo $\rho=34$, a memória de $M=6$ exclui
   41–47% do cubo, contra 21–37% para A. Explicação proposta [H], não testada separadamente: a forma na banda
   depende de $x_*$ (memória total) pela lei 1/4, e $M$ não compensa ($c\,M^{1/4}$: um fator 3 em $c$ exigiria um
   fator 81 em $M$), ao passo que para A a fusão está na banda e $M$ compensa melhor.
   McNeill et al. e Ebersold & Tiwari tratam a memória órfã como degrau; aqui o degrau tem uma cauda $f^{1/4}$
   mensurável em $\rho\gtrsim30$.
8. **Compressões.** A retenção de 100% do MOPED no fiducial é um teorema (HJL 2000) e serve de teste do código; a
   retenção ≥ 99,2% fora dele poderia ser artefato do mesmo $t_0$ — é, em parte (o instante é dado). Não testei com
   $t_0$ buscado.
9. **L06.** O KSG foi testado com gaussianas de $I$ conhecida (subestima até 40% em 9 dimensões: os $I$ dos resumos são cotas inferiores). A validação cruzada é agrupada por binária (sem vazamento entre sorteios extrínsecos). O modelo linear serve de referência; quando o HGB fica abaixo dele, o $R^2$ do HGB é sinal de pouco sinal, não de ausência de informação.

## 6. Contraexemplos e limitações

- **Modelo.** Tudo é NRHybSur3dq8_CCE (spins alinhados, $q\le8$, $|\chi|\le0{,}8$), memória nula de nível A (ordem
  quadrática nos modos oscilatórios, $\ell\le8$, $m=0$). Precessão, excentricidade e matéria ficam de fora; a memória
  $m\neq0$ (borda final, item 2) não entra na série; ela é oscilatória na banda e entra junto da onda. A incerteza
  entre modelos de $E_{\rm janela}$ (~1e-4, L00) é desprezível diante dos erros estatísticos aqui.
- **Detector idealizado.** $|F|=1$ e um único $\psi$; a rede "+ e ×" é um par co-localizado a 45° com a mesma PSD,
  um limite superior para redes reais (ET tem três braços a 60°; CE terá sítios separados). Ruído gaussiano
  estacionário, curvas de projeto do lalsimulation, banda desde 10 Hz (com 5 Hz, ET e CE ganhariam SNR de memória;
  rev_R2 mediu ~20% de 10 para 20 Hz).
- **Prior.** $d_{\rm ef}$ e bits dependem dos priors (gaussianos com o desvio dos uniformes). O prior de $t_0$
  (50 ms) é convencional: a informação em $t_0$ é $\log_2(\sigma_p/\sigma)$ e domina os bits totais; por isso dou
  sempre também $I_{\rm intr}$.
- **Fisher.** Vale só nas 2–3 direções medidas em ET/CE (seção 4.3); a verossimilhança em $\ln M$ é assimétrica
  (fator 3) já em $\rho=34$; em aLIGO/A+ nada vale. Não rodei MCMC: a verificação não linear é o perfil (4.3) e a
  varredura global (4.4), ambas com ruído zero (sem viés de realização).
- **Varredura órfã.** 160 pontos de Sobol (A) e 64 (massa baixa) dão frações com erro binomial ~0,035–0,06.
  $M$ restrito a $[0{,}55;1{,}9]\times M_A$ (A) e $[0{,}5;2]\times M_A$ (baixa): para $q$ alto o ótimo pode estar
  fora (subestimaria a região). O limite $\iota\to90°$ é artefato (4.4). O critério $1/(2\rho^2)$ é o de um
  parâmetro; para uma região 4D a 68% o limiar seria ~4,7 vezes maior, e a região, maior ainda.
- **Lei $(Mf)^{1/4}$.** É assintótica, de ordem dominante e sem spins; os desvios numéricos (0,54–1,66) mostram que
  correções PN e de spin pesam em toda a faixa útil. A conclusão qualitativa (não é um degrau; a forma depende de
  $x_*$) é robusta; a fórmula do coeficiente não serve como modelo quantitativo.
- **MOPED fora do fiducial** foi testado com o mesmo $t_0$; na prática o instante tem de ser buscado.
- **L06.** Rede ideal com $\psi=0$ conhecido; MOPED com o $t_0$ verdadeiro (vantagem irreal: o banco de moldes, invariante no tempo, fica abaixo); uma realização de ruído por amostra; os erros de (a) e (b) são níveis absolutos calibrados em A (aproximação de forma fixa). Prior de $q$ só até 4 e massas 40–120. O $R^2$ depende das larguras do prior; compará-lo entre alvos é qualitativo.

## 7. Literatura e originalidade

**Como conferi.** API do arXiv (`export.arxiv.org/api/query`), cerca de 25 consultas por título e resumo:
"gravitational wave memory" com Fisher, Cramér-Rao, "parameter estimation", "identifiability", "orphan memory",
"subsolar", "Cosmic Explorer", "Einstein Telescope", "distance-inclination"; MOPED, "optimal data compression" e
"score compression" com "gravitational wave"; "mutual information" com "gravitational-wave". Duas buscas na web
(WebSearch) e leitura (WebFetch) do texto de Favata 2009 (ar5iv 0902.3660) para a transformada do modelo mínimo.
Resumos lidos pela API: McNeill et al. 2017, Ebersold & Tiwari 2020, Gasparotto et al. 2023, Xu et al. 2024,
Rosselló-Sastre et al. 2025, Grant & Nichols 2023, Wang 2026.

**O que já se sabe [E]:**
- Memória órfã e a forma de degrau: [McNeill2017] (PRL 118, 181103), "high-frequency bursts produce orphan
  memory in the LIGO/Virgo band"; [ET2020] (PRD 101, 104041), "the morphology of the memory signal depends
  minimally upon the source parameters ... only the overall amplitude of the signal changes".
- Fisher com memória junto da onda oscilatória: [Gasparotto2023] (arXiv:2301.13228, LISA): a memória reduz a
  degenerescência distância–inclinação só para sinais curtos; [Xu2024] (PRD 109, 123034, inferência bayesiana com
  injeções): a memória quebra a degenerescência distância–inclinação para SNR > 90 nos detectores atuais;
  [RS2025] (PRD 112, 084021): o modo (2,0) completo em A#, CE e ET reduz vieses de spin.
- Detectabilidade e populações: [Lasky2016], [Hubner2020], [GN2023] (PRD 107, 064056), [Goncharov2024]
  (arXiv:2310.10718: ET restringe a amplitude da memória a ~2% em um ano), [SGN2026].
- Resposta lenta (reação de radiação) e rápida (fusão) da memória: [Johnson2019] (arXiv:1810.09563).
  Transformada do modelo mínimo de memória com função de Kummer $U(1,7/4,2\pi if\tau_{rr})$: [Favata2009a] eq. 14.
- MOPED: [HJL2000] (MNRAS 317, 965). Estimador de informação mútua: [KSG2004] (PRE 69, 066138). Validade do
  Fisher em SNR baixa: [Vallisneri2008] (PRD 77, 042001). Informação mútua em testes de RG com ondas:
  [Wang2026] (arXiv:2609.10220), outro uso.

**O que não encontrei e parece novo aqui [D]/[H]** (a busca é limitada a títulos e resumos):
1. Fisher, Cramér-Rao, $d_{\rm ef}$ e informação mútua da memória **sozinha** resolvida no tempo, com prior, em
   aLIGO/A+/ET/CE, e a contagem de direções medidas (3 em CE, ~2,5 em ET, ~1 em aLIGO) com teste de Vallisneri.
2. A região degenerada da memória órfã calculada explicitamente, minimizando sobre $M$, $\iota$, $\psi$, $D$, $t_0$:
   frações do cubo $(q,\chi_1,\chi_2)$ indistinguíveis em função de $\rho$ (Ebersold & Tiwari afirmam a
   degenerescência qualitativamente).
3. A lei assintótica $1-|T|\simeq c\,(2\pi fM)^{1/4}$ com $c\propto\eta^{-1/4}/x_*$ e a consequência "a forma da
   memória na banda só depende de $M/(\eta x_*^4)$ para $fM\ll1$". Está implícita na transformada exata do modelo
   mínimo de Favata 2009 (eq. 14); não achei a expansão nem a leitura em termos de identificabilidade. Não alego
   prioridade sobre a matemática, que é uma expansão elementar.
4. MOPED aplicado à memória e a retenção ≥ 99% fora do fiducial; a comparação quantitativa "4 memórias integradas
   idealizadas contra a série" (250% de informação intrínseca a mais na idealização).
5. O atraso de CM ($\approx M_f/2$) a 1σ em CE para um sistema tipo GW150914 a 400 Mpc com a onda oscilatória
   fixando o resto (relação conhecida [Nichols2018]; o número para CE não encontrei; ver também L19, agente D8).

**Referências novas (não estão em `referencias.md`):**
- [KSG2004] A. Kraskov, H. Stögbauer, P. Grassberger, "Estimating mutual information", PRE 69, 066138 (2004).
- [Wang2026] Y.-F. Wang, "Testing source dependence in gravitational-wave tests of general relativity with mutual
  information", arXiv:2609.10220 (conferido pela API do arXiv; outro uso da informação mútua).
- Já em `referencias.md` e relevantes aqui: [DTLW2020] (rajadas de memória modeladas como lei de potência em
  frequência; a lei $(Mf)^{1/4}$ diz que, para binárias, o índice efetivo na banda depende de $Mf$ e de $x_*$),
  [VTRH2024] (transformada de sinais com degrau), [Johnson2019], [HJL2000], [Vallisneri2008].

## 8. Próximos experimentos

1. **Posterior bayesiano completo da memória órfã.** O MOPED mostra que os sinais de memória vivem num subespaço
   linear de dimensão ≤ 8 (retenção ≥ 99,2%); um emulador de base reduzida dos espectros adimensionais em
   $(q,\chi_1,\chi_2)$ (com $M$ pela lei de escala) tornaria um MCMC barato (ms por avaliação) e daria o posterior
   não gaussiano (assimetria em $\ln M$, curvatura $\psi$–$D$) em CE e ET, com ruído.
2. **Rede real.** ET (três detectores a 60°) e CE+CE+ET com padrões de antena, posição no céu e banda desde 5 Hz;
   recontar as direções medidas (a rede ideal "+ e ×" daqui é um limite superior para $\psi$).
3. **Moldes de busca órfã.** Ebersold & Tiwari interpolam um molde de memória de forma fixa em massa. A lei
   $(Mf)^{1/4}$ e a varredura mostram que a forma depende de $x_*$ (spins) com 1−match até 1e-3: medir a perda de
   SNR de um banco de forma fixa e propor um banco de 1 parâmetro ($c\,M^{1/4}$).
4. **Atraso de CM com a onda completa (L19).** Aqui o atraso $M_f/2$ fica a 1σ em CE para A; repetir com o
   modelo completo (parte ordinária nos modos $m=0$) e uma população, para ver quantos eventos dão $M_f$ pela memória.
5. **Correções PN da lei 1/4.** Expandir a transformada com a memória 1PN e spin-órbita (Favata 2009, Blanchet
   2014) para obter o coeficiente com erro < 10% e um "índice espectral" analítico da memória na banda.
6. **Precessão e memória $m\neq0$ (L10).** Repetir o Fisher com NRSur7dq4: os modos de memória $m\neq0$ oscilam na
   banda e poderiam carregar os spins no plano.

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H05.1 | A memória na banda fixa 2–3 combinações (instante, amplitude, escala); o resto é degenerado | confirmada numericamente | CE: $d_{\rm ef}=3{,}03$ ($t_0$; $\cos\iota$ com $\ln D$; $\ln M$), ET 2,56; aLIGO/A+ 1,25/1,58 sem valor ($\rho<1$) |
| H05.2 | A escala medida é $\sim M_f$ | refutada | ao longo do vale, $\ln(M^*m_f)$ varia mais (0,071) que $\ln M^*$ (0,066); melhor descrição: $\ln M^*\approx4{,}12-0{,}12\chi_{\rm eff}$ |
| H05.3 | O Fisher vale nas direções medidas (ET/CE) e falha nas dominadas pelo prior | confirmada numericamente, com ressalva | $\varepsilon\le0{,}08$ (CE), $\le0{,}14$ (ET); 20–1091 fora delas; perfil em $\ln M$ assimétrico por fator 3 |
| H05.4 | Junto da onda, a memória acrescenta pouco (só $D$–$\iota$) | confirmada numericamente | CR($\ln D$): −1% (aLIGO) a −8% (CE), −10% com RN; +0,01 a +0,1 bit |
| H05.5 | $1-|T|\simeq c(2\pi Mf)^{1/4}$, $c\propto\eta^{-1/4}/x_*$ | confirmada matematicamente (ordem dominante); numericamente só em ordem de grandeza | razões 0,54–1,66; expoentes 0,14–0,28 (6 binárias) |
| H05.6 | Massa baixa (fusão fora da banda) carrega menos informação intrínseca com o mesmo $\rho$ | inconclusiva | local (Fisher): sim, escala 13 vezes menos informativa; global: não, exclui 41–47% do cubo contra 21–37% de A |
| H05.7 | Minimizando sobre a família, a memória resolvida no tempo não separa os pares do exp07 | confirmada numericamente | CE, $\rho=34$: 1−match 1,1e-8 a 2,6e-4 < 4,3e-4, com $M^*\neq M_B$ |
| H05.8 | A região degenerada ocupa a maior parte do cubo em CE ($\rho=34$) | confirmada numericamente | 72% (só $M$ livre), 63% ($M$ fixo), 100% em ET; cai a 34% com $\rho=100$ |
| H05.9 | O vale $M^*(q,\chi)$ é uma escala física simples | refutada | 9 abordagens (seção 5, item 5); índice espectral local só parcialmente constante (desvio 0,036 contra 0,061) |
| H06.1 | $R^2$/informação altos para $D/M$, $M_f$, $\iota$; baixos para $q$ e spins | confirmada numericamente (sem ruído) | $R^2$: $\cos\iota$ 0,99, $\ln(\eta M/D)$ 0,93, $\ln M_f$ 0,82; $q$ 0,26, $\chi_2$ 0,08 |
| H06.2 | Com ruído realista a previsibilidade dos intrínsecos vai a ~0 | refutada em parte | CE: série (MOPED) $\ln M$ 0,50, $\ln\mathcal M$ 0,50; valores integrados mensuráveis 0,08; ET 0,13; $q$ ≤ 0,21, spins ~0 |
| H07.1 | Um detector mede ≤ 2 números de memória além de $t_0$; uma rede acrescenta $\psi$ | confirmada numericamente | detector: $t_0$ + amplitude + escala ($d_{\rm ef}$ 3,03); rede: + $\psi$ ($\sigma_\psi=0{,}015$, $d_{\rm ef}$ 4,46) |
| H07.2 | As 4 memórias integradas idealizadas superestimam a informação | confirmada numericamente | $I_{\rm intr}$ = 251% (CE) e 256% (ET) da série |
| H07.3 | O degrau final retém a maior parte da informação intrínseca | refutada | 2–7% da intrínseca (35% dos bits totais) |
| H07.4 | MOPED retém tudo no fiducial e degrada longe dele | confirmada matematicamente no fiducial (teorema, conferido: 100%); refutada a degradação | ≥ 99,2% em 5 binárias diferentes de A |
| H07.5 | O CM é mensurável como atraso do degrau quando a onda fixa o resto | inconclusiva | atraso $M_f/2=0{,}170$ ms contra $\sigma=0{,}170$ ms (CE: 1σ para A), 0,656 ms (ET); 3σ exigiria $\rho_{\rm mem}\approx100$ |

