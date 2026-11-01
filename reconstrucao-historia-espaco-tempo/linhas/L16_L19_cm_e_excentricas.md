# L19 e L16 — Memória de CM como atraso; excentricidade, anomalia e duas janelas (agente D8)

Rótulos: [E] estabelecido na literatura, [D] derivado aqui, [H] hipótese, [S] especulação.
Todos os números vêm dos arquivos de `resultados/` citados; os scripts estão em `codigo/` com os prefixos
`exp38_`, `exp39_` (L19) e `exp40_` (L16). Figuras: `figuras/e38_cm_atraso.png` e `figuras/e40_excentricas.png`.
Infraestrutura: `codigo/observaveis.py` (L00) para o NRHybSur3dq8_CCE; para o SEOBNRv5EHM escrevi o tratamento
análogo em `codigo/exp40_comum.py` (pesos de janela com início exato, derivada de 8ª ordem, energia de ligação
pela Hamiltoniana EOB, segunda janela por frequência orbital média).

---

# Parte I — L19: a memória de CM como atraso do degrau de memória

## I.1 Pergunta e hipóteses

**Pergunta.** A parte ordinária da memória de CM vale $\mathcal K_{20}/J_{20}=-M_f/2$ ([Nichols2018] eq. 4.23, com
$M_f$). Isso quer dizer que o degrau de memória da deformação chega $M_f/2$ depois do degrau previsto pelo fluxo?
Para cada $\ell$, qual é o atraso? O transiente do exp09 (até ~18% do degrau, 4–9 M depois do pico) é esse atraso?
A memória observada comparada com a prevista pela onda oscilatória mede $M_f$? Com que precisão?

Hipóteses (status na tabela I.9):

- **H19.1** [D] A memória de CM de Nichols, no nível da deformação, é menos o deslocamento vezes o atraso do
  *centroide* da taxa de memória (deformação real contra fluxo), para cada $\ell$.
- **H19.2** [D] A parte ordinária dá $\delta_\ell=\tfrac32M_f/\mathfrak D_\ell=12M_f/[(\ell-1)\ell(\ell+1)(\ell+2)]$:
  $M_f/2$, $M_f/30$, $M_f/140$, $M_f/420$ para $\ell=2,4,6,8$.
- **H19.3** [H] (da linha L19) O transiente do exp09 é o atraso: $h_\text{RN}(u)-h_\text{fluxo}(u)\approx-\delta\,\dot h_\text{fluxo}(u)$.
- **H19.4** [H] O deslocamento temporal que melhor alinha o (2,0) de RN com a memória nula acumulada é $M_f/2$.
- **H19.5** [H] O substituto NRHybSur3dq8_CCE confirma numericamente o atraso de centroide previsto,
  $\delta_\text{tot}=-\text{cm}_{\ell0}/\text{desl}_{\ell0}$.
- **H19.6** [H] O transiente é o toque quase normal (2,0,0) do remanescente (alternativa a H19.3).
- **H19.7** [D/H] Controle: a memória de spin não tem parte ordinária em sistemas sem precessão, logo
  $\int(h_{30}^\text{RN}-h_{30}^\text{fluxo})\,du=0$; o substituto deve satisfazer isso.
- **H19.8** [H] O atraso, comparando a memória observada com a prevista pela onda, mede $M_f$ com precisão útil em ET/CE.

## I.2 Fundamentação e equações

Normalização do código (`memorias.py`, [Mitman2020]): $h=\sum h_{\ell m}\,{}_{-2}Y_{\ell m}$,
$h^E_{\ell m}=\tfrac12\bar\eth^2_\ell\Phi_{\ell m}$ com $\bar\eth^2_\ell=\sqrt{(\ell+2)!/(\ell-2)!}$ e
$\mathfrak D_\ell=\tfrac18(\ell-1)\ell(\ell+1)(\ell+2)$.

**Balanço do aspecto de massa** [E] ([Mitman2020], eq. ememoryfinal, válido entre dois instantes quaisquer):
$$h^E_{\ell0}(u)-h^E_{\ell0}(u_s)=\tfrac12\bar\eth^2_\ell\,\mathfrak D_\ell^{-1}\big[m_\ell(u)-m_\ell(u_s)\big]+S_\ell(u)-S_\ell(u_s),$$
onde $S_\ell$ é a memória nula acumulada pelo fluxo ($\tfrac14\int|\dot h|^2$ projetado). Defino
$D_\ell(u)\equiv[h_{\ell0}(u)-h_{\ell0}(u_s)]-[S_\ell(u)-S_\ell(u_s)]=\tfrac12\bar\eth^2_\ell\mathfrak D_\ell^{-1}[m_\ell(u)-m_\ell(u_s)]$:
é o transiente do aspecto de massa, visto na deformação.

**Memória de CM** [E] ([Nichols2018] eq. 3.11):
$\Delta\mathcal K=\int_{u_1}^{u_2}(\Phi-\Phi^{(n)})\,du-[u(\Phi-\Phi^{(n)})]_{u_1}^{u_2}$. No nível da deformação
(o `cm` do código, $\tfrac12\bar\eth^2\Delta\mathcal K$):
$$K_\ell=\int D_\ell\,du-[u\,D_\ell]=-\int u\,\dot D_\ell\,du=-\Big(\int u\,\dot h_{\ell0}\,du-\int u\,\dot S_\ell\,du\Big).$$

**[D] Proposição (H19.1).** Se os degraus são iguais ($D_\ell(u_2)=0$, isto é, sem memória ordinária de
deslocamento entre os estados inicial e final; a do recuo é $O(v^2)\sim10^{-7}$), então
$$K_\ell=-\Delta J_\ell\,\big(\langle u\rangle_{\dot h_{\ell0}}-\langle u\rangle_{\dot S_\ell}\big),\qquad \langle u\rangle_f\equiv\frac{\int u\,\dot f\,du}{\int\dot f\,du}.$$
A memória de CM é exatamente menos o deslocamento vezes o atraso do centroide do degrau real em relação ao do
degrau previsto pelo fluxo: $\delta_\ell\equiv-K_\ell/\Delta J_\ell$. Equivalentemente
$\delta_\ell\Delta J_\ell=-\tfrac12\bar\eth^2_\ell\mathfrak D_\ell^{-1}\int[m_\ell(u)-m_\ell(u_s)]\,du$: o atraso é a
integral no tempo do transiente do aspecto de massa. Demonstração: integração por partes. Não diz nada sobre a
**forma** de $D_\ell$; só sobre seu primeiro momento.

**[D] Atraso ordinário (H19.2).** A parte ordinária vem da mudança da carga de super-CM, linear na memória
([FN2017]; [Nichols2018] eq. 4.23): o remanescente, supertransladado por $\alpha\propto\Delta\Phi$, carrega
super-CM $3M_f\alpha$. No código, $K^\text{ord}_\ell=-\tfrac32M_f\Delta J_\ell/\mathfrak D_\ell$ (conferido contra as
eqs. 4.25a,b de Nichols em `revisao/rev_R1_analitico.py`, A8). Logo
$$\delta^\text{ord}_\ell=\frac{3M_f}{2\mathfrak D_\ell}=\frac{12\,M_f}{(\ell-1)\ell(\ell+1)(\ell+2)}:\qquad \ell=2:\ \tfrac{M_f}{2};\quad \ell=4:\ \tfrac{M_f}{30};\quad \ell=6:\ \tfrac{M_f}{140};\quad \ell=8:\ \tfrac{M_f}{420}.$$
O atraso ordinário só depende de $M_f$; o total inclui a parte nula da CM e depende do sistema.
Mecanismo: o balanço do aspecto de momento angular, $\partial_u\mathcal N=m+F_E$ na parte elétrica (os termos
lineares em $C_{AB}$ se cancelam na parte elétrica, [D], conta direta com
$C_{AB}=(2D_AD_B-\gamma_{AB}D^2)\Phi$), força a integral no tempo do transiente do aspecto de massa a fornecer o
super-CM final. No observador, $\delta(\theta)=\sum_\ell\delta_\ell\Delta J_\ell Y_\ell/\sum_\ell\Delta J_\ell Y_\ell$.

**Limite do enunciado.** A proposição vale para o primeiro momento. Um atraso pontual
$D(u)\approx-\delta\dot S(u)$ é uma hipótese a mais (H19.3). A parte linear do (2,0),
$\propto\ddot I_{20}$, tem área $\Delta\dot I_{20}$, nula entre estados estacionários. O toque quase normal pode
ser grande sem mudar muito o atraso de centroide [S]; não testei isso separadamente.

**Controle magnético (H19.7)** [D]. No setor magnético, $h^B$ é instantâneo, e
$\int(h^B_\text{RN}-h^B_\text{fluxo})\,du$ é a variação da carga magnética $\ell=3$ do aspecto de momento angular.
Ela é nula entre estados estacionários sem precessão: binária no início (sem $m=0$ em $\ell=3$ na ordem dominante)
e Kerr no fim (só $\ell=1$).

## I.3 Experimentos

| Script | O que faz | Saída |
|---|---|---|
| `exp38_cm_atraso.py` | 10 sistemas ($q=1,2,4,6,8$ sem spin; $(1;\pm0{,}6,\pm0{,}6)$; $(3;0{,}6,0)$; A $=(1{,}2;0{,}3,-0{,}2)$; $(8;0{,}6,0)$), $M=65$, janela desde 10 Hz. $S_\ell(u)$ (nível A, mesma quadratura de `serie_memoria`) contra $h_{\ell0}^\text{RN}$. Previsões; deriva; área; atraso de centroide para vários inícios $u_s$; teste pontual; melhor deslocamento; ajuste do QNM (2,0,0) (qnm + NRSur3dq8Remnant); controle magnético; modos ausentes (NRSur7dq4, $q\le4$). 2 processos, 165 s | `resultados/exp38_cm_atraso.txt`, `.json`, `exp38_series.npz` |
| `exp38_deriva.py` | atraso de centroide com a deriva da inspiral ajustada e removida (constante, ou constante + fração de $S$), 3 sistemas | `resultados/exp38_deriva.txt` |
| `exp39_cm_mensuravel.py` | precisão de Fisher do atraso, $\sigma_\delta=1/\|\dot s_n\|$, com a série nula no observador ($\iota=50°$, $D=400$ Mpc, $h_+$), $M=30,65,120,200$; aLIGO, A+, ET, CE ($f_\text{min}$ 10 Hz; ET e CE também 5 Hz); SNR da diferença $s_\text{RN}-s_n$ | `resultados/exp39_cm_mensuravel.txt`, `.json` |
| `exp38_figura.py` | figura | `figuras/e38_cm_atraso.png` |

## I.4 Resultados

**Previsões** (`exp38_cm_atraso.txt`, nível A, deslocamento de janela; $\delta$ em unidades de $M$):

| Sistema $(q;\chi_1,\chi_2)$ | $M_f$ | $\delta^\text{ord}_2$ | $\delta^\text{tot}_2$ | $\delta^\text{tot}_4$ | $\delta$ no observador ($\iota=50°$) |
|---|---|---|---|---|---|
| (1; 0, 0) | 0,9516 | 0,476 | 0,545 | 0,127 | 0,534 |
| (2; 0, 0) | 0,9613 | 0,481 | 0,496 | 0,066 | 0,490 |
| (4; 0, 0) | 0,9780 | 0,489 | 0,373 | 0,895 | 0,371 |
| (6; 0, 0) | 0,9855 | 0,493 | 0,301 | 0,479 | 0,299 |
| (8; 0, 0) | 0,9895 | 0,495 | 0,264 | 0,435 | 0,262 |
| (1; +0,6, +0,6) | 0,9269 | 0,463 | 0,496 | 0,068 | 0,483 |
| (1; −0,6, −0,6) | 0,9638 | 0,482 | 0,602 | 0,228 | 0,594 |
| (3; +0,6, 0) | 0,9570 | 0,478 | 0,466 | −0,058 | 0,463 |
| A (1,2; +0,3, −0,2) | 0,9498 | 0,475 | 0,541 | 0,121 | 0,530 |
| (8; +0,6, 0) | 0,9826 | 0,491 | 0,365 | 0,208 | 0,368 |

- A parte nula da CM aumenta o atraso em $\ell=2$ para $q\approx1$ (até +25%) e o reduz para $q$ grande (até −47%
  em $q=8$).
- Em $\ell=4$ a parte nula domina (por exemplo, 0,127 contra o ordinário 0,032 em $q=1$) e o atraso total muda de
  sinal entre sistemas. Os modos ausentes do substituto CCE mudam $S_{40}$ em 10–14% (em módulo; 59% em (3; +0,6, 0); NRSur7dq4,
  abaixo), então os números de $\ell=4$ são só indicativos.
- No observador o atraso é dominado por $\ell=2$: 0,26–0,59 M; no sistema A, 0,530 M = 170 µs para $M=65$.

**O transiente não é o atraso (H19.3, H19.4)** (`exp38_cm_atraso.txt`; figura e38, painéis a e b):

| Sistema | max\|D\|/desl em [−60, 60] M | $(M_f/2)\max\dot S$/desl | $\delta$ do ajuste $D\approx c-\delta\dot S$ ($R^2$) | melhor deslocamento $R(u)\approx\lambda S(u-d)+c$ | pico da taxa: fluxo / RN |
|---|---|---|---|---|---|
| (1; 0, 0) | 0,177 | 0,0119 | 3,7 M (0,27) | 2,5 M | +7,5 / +10,75 M |
| (2; 0, 0) | 0,234 | 0,0111 | 5,9 M (0,33) | 3,7 M | +6,75 / +11,75 M |
| (4; 0, 0) | 0,488 | 0,0093 | 15,4 M (0,35) | 8,2 M | +5,0 / +13,5 M |
| (6; 0, 0) | 0,781 | 0,0080 | 24,1 M (0,25) | 11,2 M | +4,0 / +14,25 M |
| (8; 0, 0) | 1,063 | 0,0070 | 31,6 M (0,18) | 13,3 M | +3,25 / +14,75 M |
| (1; +0,6, +0,6) | 0,045 | 0,0105 | 1,1 M (0,28) | 1,0 M | +9,0 / +10,5 M |
| (1; −0,6, −0,6) | 0,482 | 0,0129 | 9,0 M (0,26) | 4,4 M | +7,25 / +10,75 M |
| (3; +0,6, 0) | 0,075 | 0,0095 | 2,5 M (0,37) | 1,9 M | +8,25 / +12,25 M |
| A | 0,150 | 0,0118 | 3,3 M (0,28) | 2,3 M | +7,75 / +10,75 M |
| (8; +0,6, 0) | 0,122 | 0,0064 | 6,0 M (0,42) | 4,5 M | +6,25 / +15,25 M |

- O transiente é 4 a 150 vezes maior do que um atraso de $M_f/2$ produziria.
- O ajuste de um atraso pontual explica só 18–42% da variância, com $\delta$ de 1,1 a 32 M.
- O melhor deslocamento é de 1,0 a 13 M, não 0,5 M.
- O degrau de RN é mais íngreme e mais tardio que o do fluxo: o pico da taxa vem 1,5–11,5 M depois. Depois ele
  passa do valor final e oscila.

**É o toque quase normal (H19.6)** (`exp38_cm_atraso.txt`, campo `qnm`):
- Para $u\ge16$ M, um único QNM (2,0,0) com frequência fixa (pacote qnm, remanescente do NRSur3dq8Remnant)
  explica 97–99% da variância de $D$ nos sistemas sem spin, 96–99% em A, (1; −0,6, −0,6) e (3; +0,6, 0), 90% em
  (1; +0,6, +0,6) e 84% em (8; +0,6, 0).
- Ajuste livre: $M\omega=0{,}411$ contra 0,413 (q = 1), 0,394 contra 0,405 (q = 2), 0,373 contra 0,391 (q = 4),
  0,357 contra 0,381 (q = 8). Amortecimento livre 0,095–0,145 contra 0,085–0,090.
- Amplitude do toque relativa ao deslocamento: 0,02 em (1; +0,6, +0,6), 0,11 em (1; 0, 0), 0,46 em (4; 0, 0) e
  1,09 em (8; 0, 0). Para $q$ grande o toque é maior que o próprio degrau de memória.
- Isso concorda com a leitura de [Mitman2024] (no (2,0), a contribuição do aspecto de massa é o toque do
  remanescente) e com os modelos de [RSHB2024], que separam memória e toque no (2,0).

**O substituto não testa o atraso de centroide (H19.5).** Três obstáculos (`exp38_cm_atraso.txt`, `exp38_deriva.txt`):

1. **Deriva na inspiral.** $D$ cresce antes da fusão: $dD/dS=+0{,}028$ a $+0{,}095$ em $[-2500,-300]$ M e
   $+0{,}014$ a $+0{,}26$ em $[-300,-50]$ M. O (2,0) de RN acumula 3–10% mais depressa que o fluxo na parte de RN.
   - Não tem a dependência em $x$ de um efeito PN: a razão quase não cresce de −2500 para −300 M, onde $x^4$
     cresce ~9 vezes.
   - $D$ salta da ordem de 1e−6 para 1e−4 relativos através da janela de hibridização (−3500 a −2500 M,
     [Yoo2023]).
   - Atribuo a deriva ao modelo (hibridização ou o (2,0) da CCE) [H, não isolado].
2. **Desvio final.** $D(\text{fim})/\text{desl}=+0{,}7\%$ a $+1{,}9\%$. Os modos ausentes do substituto CCE explicam
   0,12–0,46% (NRSur7dq4, $q\le4$): somam 0,35% a $S_{20}$ e 11% a $S_{40}$ em $q=1$.
3. **Consequência.**
   - A área total dá $\delta$ entre −35 e +29 M, contra 0,26–0,60 M previstos.
   - O atraso de centroide normalizado depende do início $u_s$ da comparação: em $q=1$ vale 0,03 / 0,61 / 0,88 /
     1,03 / 1,48 M para $u_s$ = −1000 / −500 / −300 / −200 / −100 M; entre sistemas, de −3,8 a +3,8 M.
   - Com a deriva ajustada e removida (`exp38_deriva.txt`), o atraso fica em 0,9–1,6 M (q = 1), 0,96–1,5 M (A) e
     1,8–3,4 M (q = 4) com o modelo de deriva constante. As variantes normalizadas espalham de −0,16 a 2,7 M.
   - O sinal (atraso positivo) concorda com a previsão. O valor fica 2 a 6 vezes acima, e cresce com $q$ quando a
     previsão diminui. A dispersão entre variantes é maior que o efeito.
   - Testar $\delta\approx0{,}5$ M exigiria o (2,0) com erro $\ll0{,}5\,\dot S$ na fusão (~1e−3 do degrau) e erros
     de taxa $\ll10^{-4}$ na inspiral. O substituto erra 1e−2 e 5e−2.

**Controle magnético (H19.7).** $\int h_{30}^\text{RN}du/\int h^B_{30}du-1$, desde −1000 M:
- de −3,4e−3 a +7e−3 nos sistemas sem spin;
- +1,4e−2 e +1,5e−2 nos casos com $\chi_1=0{,}6$.

Desde o início da janela (parte PN do híbrido) vai a +1,1e−2 até +7,8e−2: o erro de 5–12% na taxa do (3,0) PN do
item 10 da revisão. O setor magnético obedece ao balanço a ≲1,5% na parte de RN; o elétrico, não, a 3–10%. Isso
reforça que a deriva elétrica é do modelo, ou de um aspecto de massa físico que eu não soube prever. Como o
magnético passa, a causa não é a extração dos modos $m=0$ em geral.

**Mensurabilidade (H19.8)** (`exp39_cm_mensuravel.txt`; $D=400$ Mpc, $\iota=50°$, $h_+$, $f_\text{min}=10$ Hz):

| $M$ ($M_\odot$) | $\delta_\text{tot}$ | Detector | $\rho_\text{nula}$ | $f_\text{rms}$ | $\sigma_\delta$ | $\delta/\sigma_\delta$ | $\rho(s_\text{RN}-s_n)$ |
|---|---|---|---|---|---|---|---|
| 30 | 78 µs | CE | 20,7 | 37,5 Hz | 205 µs | 0,38 | 3,8 |
| 65 (A) | 170 µs | aLIGO | 0,47 | 44 Hz | 7,7 ms | 0,022 | 0,45 |
| 65 (A) | 170 µs | A+ | 0,89 | 44 Hz | 4,0 ms | 0,042 | 0,86 |
| 65 (A) | 170 µs | ET | 8,6 | 28 Hz | 656 µs | 0,26 | 4,7 |
| 65 (A) | 170 µs | CE | 34,1 | 27,5 Hz | 170 µs | 1,00 | 12,4 |
| 120 | 315 µs | ET | 11,5 | 19 Hz | 716 µs | 0,44 | 8,8 |
| 120 | 315 µs | CE | 43,5 | 22 Hz | 168 µs | 1,88 | 29 |
| 200 | 528 µs | ET (5 Hz) | 22,3 | 11 Hz | 658 µs | 0,80 | 13,9 |
| 200 | 528 µs | CE | 44,5 | 18 Hz | 197 µs | 2,68 | 55 |

- A precisão do instante fica em ~170–205 µs em CE para qualquer $M$, porque $\rho$ e $f_\text{rms}$ se compensam.
  Como $\delta\propto M_f$, $\sigma(M_f)/M_f=\sigma_\delta/\delta$ vale 1,0 (A), 0,53 ($M=120$) e 0,37 ($M=200$) a
  400 Mpc em CE, e no mínimo 1,2 em ET (com 5 Hz; 1,5 com 10 Hz).
- A 100 Mpc a razão sobe 4 vezes: CE daria $\sigma(M_f)/M_f\approx0{,}1$–0,25.
- Para 3σ com eventos iguais ao A: 9 em CE e 134 em ET.
- O atraso direto, $\|s(t)-s(t-\delta)\|$, coincide com $\delta\|\dot s\|$ em todos os casos (coluna "direto" do
  arquivo): a aproximação de Fisher vale.
- A revisão citava 86 µs em CE (`rev_R1_detector.txt`). Ela usava a série de RN com o toque, $f_\text{rms}=47$ Hz.
  Só com a memória nula, $f_\text{rms}=27{,}5$ Hz e $\sigma=170$ µs.
- A diferença completa $s_\text{RN}-s_n$ é muito mais forte que a parte de atraso (12,4 contra 1,0 em CE, para A).
  O que um detector separaria do previsto pelo fluxo é sobretudo o toque $m=0$, mais a deriva do modelo, não o
  atraso.

## I.5 Tentativas de refutação e alternativas

Para H19.3, H19.4 e H19.5 tentei oito abordagens:
1. ajuste pontual de $D$ por $\dot S$;
2. melhor deslocamento temporal com escala livre;
3. atraso de centroide com seis inícios, com e sem normalização dos degraus;
4. área na janela inteira;
5. remoção da deriva por dois modelos e dois intervalos de ajuste (`exp38_deriva.py`);
6. identificação do toque por QNM fixo e livre;
7. correção dos modos ausentes (NRSur7dq4);
8. controle magnético, que separa erro de extração de efeito elétrico.

Também olhei $\ell=4$, em que o atraso ordinário previsto é 15 vezes menor e a parte nula domina. Nenhuma
abordagem achou $\delta\approx M_f/2$ de forma estável.
- O transiente pontual é refutado com folga.
- O atraso de centroide fica inconclusivo: sinal certo, magnitude 2–6 vezes maior e dependente de escolhas.

A minha própria hipótese inicial de que a deriva da inspiral seria um efeito físico de "cauda da memória" (estimativa
de ordem de grandeza ~$64x^4\ln$, que dava alguns % em $x\sim0{,}15$) não se sustenta: a deriva não cresce com $x$
como deveria, e aparece já logo depois da janela de hibridização.

## I.6 Contraexemplos e limitações

- A proposição I.2 é sobre o primeiro momento. Um transiente de área zero (o toque, se sua área for pequena) pode
  ter qualquer amplitude: o exp38 mostra amplitudes de até 1,09 vez o degrau.
- A parte ordinária usada ([Nichols2018] 4.23) é linear na memória e supõe o estado inicial com super-CM
  $3M\alpha_i$. A variante $M_f\Phi_f-M_i\Phi_i$ muda cm20 em 0,47% (L00). Correções de recuo são $O(v^2)$.
- O fluxo do substituto CCE perde 0,1–0,5% de $S_{20}$ e muda $S_{40}$ em 10–59% (modos ausentes).
- O (2,0) do substituto tem deriva de 3–10% da taxa na parte de RN e erro final de ~1%: insuficiente para testar
  $\delta\sim0{,}5$ M.
- A mensurabilidade usa só $h_+$ (detector ótimo), sem padrões de antena nem marginalização sobre os parâmetros
  da onda. Ignora o desvio para o vermelho ($M$ do detector = $M$ da fonte) e trata o toque $m=0$ como conhecido
  (previsto pela onda completa). É um limite otimista.
- Mesmo com precisão perfeita, $M_f$ já é medido muito melhor pelo próprio *ringdown* oscilatório. O atraso serve
  como teste de consistência do balanço BMS (super-CM do remanescente), não como medida competitiva de $M_f$.

## I.7 Literatura e originalidade

Como conferi:
- texto completo de [Nichols2018] (arXiv:1807.08767; eqs. 3.5–3.13, 4.23–4.25, nota 8);
- [GM2024] (arXiv:2312.02295), [SGN2024] (2403.13907) e [SGN2026] (2608.23739), por busca no PDF de "time shift",
  "delay", "centroid" e "M/2": nada;
- a revisão [Mitman2024] (arXiv:2405.08868, §IV e fig. 3);
- [RSHB2024] (arXiv:2405.17302) e [VTRH2024] (arXiv:2406.16636);
- API do arXiv com "center-of-mass memory" (todos os campos), "ordinary memory" AND "mass aspect",
  memory AND "time delay" AND gravitational, "drift memory";
- WebSearch geral.

O que está estabelecido:
- A definição de $\Delta\mathcal K$ e a forma "$u$ vezes a derivada do aspecto de massa" (nota 8 de Nichols) são
  [E].
- A CM já é descrita como um "atraso de tempo" entre observadores em queda livre em trajetórias antiparalelas
  ([Nichols2018]; resumido em [RSHB2024] §I). É outro atraso: entre observadores, não entre o degrau e o fluxo num
  observador.
- [GM2024] calcula a memória de CM numa simulação SXS e nota que $\text{Re}\,\hat{\mathcal F}_1$ não tem a forma
  esperada (contaminação de QNM), sem ligar isso a um atraso.

O que não encontrei:
- a leitura "memória de CM = −deslocamento × atraso do centroide do degrau real em relação ao previsto pelo
  fluxo", com $\delta_\ell=12M_f/[(\ell-1)\ell(\ell+1)(\ell+2)]$;
- o uso disso para medir $M_f$ por memória + onda.

A identidade é uma integração por partes de 3.11 e provavelmente é conhecida implicitamente. Não alego descoberta;
no máximo uma reformulação útil, com a ressalva de que a forma pontual é falsa e o efeito observável é pequeno.

## I.8 Próximos experimentos

1. Testar a proposição com dados de CCE que tragam o aspecto de massa ($\Psi_2$) e a deformação. Exemplo: o
   catálogo SXS CCE, com `scri`. Precisa de download grande e não foi feito.
2. Isolar a área do toque (2,0,0): ajustar o toque com início livre e calcular a área do resto.
3. Fisher conjunto: atraso, amplitude do toque $m=0$ e parâmetros da onda, com padrões de antena e rede de
   detectores.
4. Somar populações em CE: o atraso médio normalizado por $M_f$ medido pela onda.

## I.9 Tabela de hipóteses (L19)

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H19.1 | $K_\ell=-\Delta J_\ell\,\delta_\ell$ (atraso de centroide) | confirmada matematicamente | integração por partes de [Nichols2018] 3.11 (§I.2) |
| H19.2 | $\delta^\text{ord}_\ell=12M_f/[(\ell-1)\ell(\ell+1)(\ell+2)]$ ($M_f/2$, $M_f/30$, ...) | confirmada matematicamente (dada a eq. 4.23) | §I.2; valores na tabela de previsões |
| H19.3 | transiente do exp09 = atraso pontual $-\delta\dot S$ | refutada | max\|D\| 4–150× maior; $R^2$ 0,18–0,42; $\delta$ ajustado 1,1–32 M |
| H19.4 | o melhor deslocamento é $M_f/2$ | refutada | 1,0–13 M |
| H19.5 | o substituto confirma $\delta_\text{tot}$ (centroide) | inconclusiva | sinal certo; 0,9–3,4 M contra 0,37–0,54 M; depende de $u_s$ e do modelo de deriva; deriva do (2,0) de 3–10% |
| H19.6 | o transiente é o toque (2,0,0) | confirmada numericamente | 84–99% da variância para $u\ge16$ M; $\omega$ livre a 0,5–16% do QNM |
| H19.7 | sem parte ordinária de spin: $\int h_{30}^\text{RN}=\int h^B_{30}$ | confirmada numericamente na parte de RN | ≤1,5e−2 desde −1000 M; 1–8% na parte PN do híbrido |
| H19.8 | o atraso mede $M_f$ com precisão útil em ET/CE | refutada para medidas competitivas | $\delta/\sigma$ = 0,26 (ET) e 1,0 (CE) no A a 400 Mpc; ≤2,7 em $M=200$; $\sigma(M_f)/M_f\ge0{,}37$ |

---

# Parte II — L16: excentricidade, anomalia e duas janelas

## II.1 Pergunta e hipóteses

**Pergunta.** Com $(e_0,\ell_0)$ livres, a família excêntrica de binárias com as quatro memórias de uma circular
tem dimensão 4 (rev_R4). Três perguntas:
- Os pares circular × excêntrica do exp12 sobrevivem quando se corrigem duas faltas do modelo: o (2,0) oscilatório
  das órbitas excêntricas e a energia de ligação excêntrica em $M_f$?
- Com DUAS janelas (10 e 20 Hz de frequência média; oito equações e oito incógnitas $M,q,\chi_1,\chi_2,D,\iota,e_0,\ell_0$),
  uma excêntrica ainda imita a circular A?
- A dependência em $\ell_0$ (que vem dos últimos ~100–500 M) é física ou artefato do modelo?

Hipóteses (status na tabela II.9):

- **H16.1** [H] O (2,0) oscilatório e a energia de ligação excêntrica mudam as memórias de B mais que o tremor
  (~1e−5), mas os pares continuam existindo: resolvidos de novo, voltam ao piso.
- **H16.2** [H] Com duas janelas e $e_0,\ell_0$ livres existe uma excêntrica ($e_0\ge0{,}1$) com as oito memórias de A
  no piso.
- **H16.3** [H] Perto de A, as direções excêntricas $(e_0\cos\ell_0,e_0\sin\ell_0)$ entram no núcleo aproximado do
  jacobiano de duas janelas.
- **H16.4** [H] A dependência em $\ell_0$ a $e_0$ fixo é linear em $e_0$, vem da fase radial com que a binária chega
  ao mergulho (últimos ~100 M) e é física (não artefato do modelo).

## II.2 Fundamentação e equações

- **Modelo.** SEOBNRv5EHM ([GBE2025]; pyseobnr 0.3.7), nível A (fluxos dos modos oscilatórios
  (2,2), (2,1), (3,3), (3,2), (4,4), (4,3) e $m<0$), multipolos $m=0$ como no exp12.
- **Primeira janela.** Começa no início da onda (EccIC = 1: frequência orbital média do modelo $=\pi Mf$, com
  $f=10$ Hz).
- **Segunda janela.** Começa quando a frequência orbital **média** vale $\pi Mf_2$ ($f_2=20$ Hz). A média é
  $\langle\omega\rangle_k=[\phi(t_{k+1})-\phi(t_k)]/(t_{k+1}-t_k)$ entre passagens sucessivas pelo periastro (máximos
  de $\Omega$ na dinâmica, refinados por parábola), atribuída ao instante médio e interpolada por spline. A
  coluna $x$ da dinâmica oscila com a fase radial (desvio rms 1,7e−4 em $e_0=0{,}2$), o que daria um instante
  instável em ±150 M; por isso não a usei.
- **Pesos de janela.** Iguais aos do L00 (`observaveis.pesos_janela`): início exato, derivada de 8ª ordem.
- **(2,0) oscilatório newtoniano.** Pela fórmula do quadrupolo na dinâmica EOB:
  $h_{20}=2\,\ddot I_{ij}P^{(20)}_{ij}$, $I_{ij}=\nu x_ix_j$, com $x=r(\cos\phi,\sin\phi,0)$ e os projetores de
  `pn_excentrico`. É desligado por um cosseno entre −200 e −100 M, onde a órbita já circularizou e a fórmula
  newtoniana deixa de valer.
  - Como $h_{20}$ é real, entra só em $|\dot h|^2$ (deslocamento, CM).
  - Não muda spin nem giroscópica, porque $\mathrm{Im}(\bar h_{20}\dot h_{20})=0$.
- **Energia de ligação.** $E_\text{lig}=1-\nu H_\text{EOB}(t_w)$ no início de cada janela (coluna 8 da dinâmica,
  $H/\mu$).
  - No circular coincide com a $E_\text{lig}$ 3PN+SO do L00 a 5e−7 (0,0055442 contra 0,0055447).
  - Com $e_0=0{,}2$ cai 2,5e−5, contra −2,2e−5 da correção 1PN excêntrica [D]:
    $E_\text{lig}=\tfrac{\nu x}{2}\{1+x[-\tfrac34-\tfrac{\nu}{12}-\tfrac{2e_t^2}{1-e_t^2}]\}$, com $x$ da frequência
    azimutal média (derivada da parametrização quase kepleriana 1PN; confere com a forma
    $[-\tfrac34-\tfrac\nu{12}+(-\tfrac54+\tfrac\nu{12})e_t^2]/(1-e_t^2)$).
  - $M_f=1-E_\text{janela}-E_\text{lig}$; as duas janelas dão o mesmo $M_f$ a 2,9e−6 (A) e 2,6e−7 (B).
- **Tremor.** ~1e−5 (rev_R4). Por isso os jacobianos usam passos grandes (diff_step 3e−3 e 1e−2) e o otimizador
  recomeça de várias partidas.
- **Anomalia [D].** Perto de $e_0=0$, a variação das memórias é $e_0(a\cos\ell+b\sin\ell)+O(e_0^2)$. Mas $\ell$ deve
  ser a fase radial **perto da fusão**: a fase acumulada de 10 Hz até a fusão depende de $e_0$ (a duração muda com
  $e_0^2$), de modo que, com $\ell_0$ medido em 10 Hz, o harmônico gira com $e_0$ (visto no jacobiano, §II.4).

## II.3 Experimentos

| Script | O que faz | Saída |
|---|---|---|
| `exp40_comum.py` | geração com dinâmica, (2,0) newtoniano, janelas, $E_\text{lig}$ EOB, memórias | — |
| `exp40_pares.py` | os seis pares do exp12: diferenças com a cadeia do exp12, só (2,0), só $E_\text{lig}$, as duas; re-solução de $(\iota,\chi_1,M)$ ($D$ pelo deslocamento) com seis tentativas; conferência do (2,0) contra o modelo PN. 2 processos, 418 s | `resultados/exp40_pares.txt`, `.json` |
| `exp40_duas_janelas.py` | 7 equações × 7 incógnitas ($D$ eliminado): 9 partidas excêntricas (pares do exp12 com $\ell_0=0$; um com $\ell_0=\pi$; família circular de duas janelas do rev_R4 com $e_0=0{,}05$); controle circular ($e_0=0$, 5 incógnitas); orçamento de ~34 iterações por partida. 535 s | `resultados/exp40_duas_janelas.txt`, `.json` |
| `exp40_jacobiano.py` | jacobiano 7 × 7 em A, com colunas circulares (diferenças centrais, passos $h$ e $h/2$) e colunas $(X,Y)=(e_0\cos\ell_0,e_0\sin\ell_0)$ pelo 1º harmônico com $e_0=0{,}03$ e 0,06; quatro buscas locais a partir dos controles circulares com $e_0=0{,}03$. 212 s | `resultados/exp40_jacobiano.txt`, `.json` |
| `exp40_anomalia.py` | sistemas A e B do exp12, $e_0=0{,}02$–0,3, 12 valores de $\ell_0$: harmônicos em $\ell_0$ de desl20, spin30, cm20, giro10, $E_\text{janela}$, $M_f$; parte vinda dos últimos 100 e 500 M; excentricidade residual; energia EOB no fim da dinâmica; controle PN (Peters + quadrupolo) com fim na separatriz secular e com fim em $r(t)<8$ M. 70 s | `resultados/exp40_anomalia.txt`, `.json` |
| `exp40_teob.py` | tentativa de segundo modelo excêntrico (TEOBResumS) | `resultados/exp40_teob.txt` |
| `exp40_figura.py` | figura | `figuras/e40_excentricas.png` |

## II.4 Resultados

**Tarefas 1 e 2: pares do exp12 com as correções** (`exp40_pares.txt`; figura e40c). Máximo de |diferença relativa|
das quatro memórias no observador, B − A (janela de 10 Hz, $\ell_0=0$):

| Par ($e_0$; $q_B$; $\chi_{2B}$) | Cadeia do exp12 | Só (2,0) | Só $E_\text{lig}$ EOB | As duas | Resolvido de novo | Mudança dos parâmetros |
|---|---|---|---|---|---|---|
| 0,1; 1,2; −0,2 | 5,2e−4 | 5,2e−4 | 5,2e−4 | 5,2e−4 | **9,5e−7** | $M$ −1,6e−4 rel.; $\chi_1$ 0,349 → 0,383 |
| 0,2; 1,2; −0,2 | 2,6e−4 | 2,6e−4 | 2,6e−4 | 2,6e−4 | **5,0e−6** | $M$ +3,8e−4; $\chi_1$ +0,005 |
| 0,3; 1,2; −0,2 | 1,15e−2 | 1,15e−2 | 1,15e−2 | 1,15e−2 | 1,07e−2 (sem solução) | — |
| 0,2; 2; 0 | 6,8e−6 | 2,3e−6 | 4,7e−5 | 4,1e−5 | **1,5e−6** | $M$ −3,4e−5; $\chi_1$ +6e−5 |
| 0,3; 2; 0 | 8,6e−6 | 1,9e−5 | 5,7e−5 | 4,6e−5 | **2,7e−6** | $M$ −4,3e−5; $\chi_1$ +1,4e−4 |
| 0,2; 1; 0 | 5,7e−5 | 6,1e−5 | 5,9e−5 | 6,4e−5 | **2,4e−5** | $M$ −1,0e−4; $\chi_1$ −1,2e−3 |

- **Conferência da cadeia.** Reproduz o alvo do exp12 a ≤5,6e−7 (com a derivada de 8ª ordem).
- **(2,0) oscilatório.** Muda o deslocamento e a CM de B em até 1,1e−5; spin e giroscópica em 0 (até 1e−15), como
  previsto. É do tamanho do tremor.
- **$E_\text{lig}$ excêntrica (EOB).** Muda $E_\text{lig}$ de B em −1,1e−5 a −8,4e−5 em relação à fórmula 1PN
  circular do exp12. A CM, proporcional a $M_f$, muda até 5,7e−5. Os dois pares que estavam no piso ($q_B=2$)
  saem dele (4,1e−5 e 4,6e−5).
- **Re-solução.** Voltam ao piso (1,5e−6 e 2,7e−6) com mudanças de parâmetros ≤ 4e−5 em $M$ e ≤ 1,4e−4 em
  $\chi_1$. Os pares sobrevivem às correções.
- **Pares mal convergidos.** Os do exp12 com $q_B=1{,}2$ convergem agora a 9,5e−7 e 5,0e−6, como a correção C22 da
  revisão. O caso $e_0=0{,}3$, $q_B=1{,}2$ continua sem solução, como no exp12.
- **Conferência do (2,0) newtoniano.** $\max|h_{20}|/\max|h_{22}|$ nas duas primeiras órbitas, EOB com fórmula
  newtoniana contra o modelo PN newtoniano: razão 0,71–0,77 nos três casos. As definições de excentricidade e as
  coordenadas diferem. Como o efeito total é ≤ 1,1e−5, um erro de 30% nele é ≤ 4e−6.

**Tarefa 3: duas janelas** (`exp40_duas_janelas.txt`, `exp40_jacobiano.txt`; figura e40d).

A (SEOBNRv5EHM com as correções):

| Janela | Deslocamento | Spin | CM | Giroscópica |
|---|---|---|---|---|
| 10 Hz | 1,64372e−22 | −2,48904e−25 s | −2,91704e−26 s | −3,15601e−41 rad |
| 20 Hz | 1,54308e−22 | −1,72765e−25 s | −2,76262e−26 s | −2,14050e−41 rad |

- **Controle circular** ($e_0=0$, 5 incógnitas, 7 equações): partindo da família aproximada do rev_R4, o
  otimizador chega a 2,4e−5 em $(q,\chi_1,\chi_2)=(1{,}196;\,0{,}274;\,-0{,}165)$ e 1,0e−4 em
  $(1{,}233;\,0{,}423;\,-0{,}374)$, os dois com $M\approx65$ e $\iota\approx50°$. A família circular aproximada de
  duas janelas existe também neste modelo, a ~2e−5–1e−4, ao longo da direção fraca ($\chi_1$ e $\chi_2$ em sentidos
  opostos).
- **Nove partidas excêntricas** ($e_0$ 0,05–0,3): o melhor foi 3,6e−3 ($e_0=0{,}098$, $q=1{,}199$). As outras deram
  4,4e−3 a 5,2e−2, com resíduos dominados pela segunda janela (por exemplo, o par $(0{,}2;\,q_B=2)$ do exp12 fica
  com 1,9–2,4e−2 em 20 Hz).
  - O otimizador quase não se moveu.
  - Com o orçamento usado (≤ 34 iterações de 8 avaliações), isso não prova ausência de solução.
- **Jacobiano em A** (colunas escaladas por 0,01 rad, 0,1, 1 $M_\odot$, 0,1, 0,1, 0,1, 0,1):

  | Caso | Valores singulares |
  |---|---|
  | circular, 7 × 5 | 1,22e−1, 3,15e−2, 1,07e−2, 3,44e−3, 5,39e−5 |
  | com $(X,Y)$ de $e_0=0{,}03$, 7 × 7 | 1,22e−1, 3,15e−2, 1,08e−2, 3,52e−3, 1,60e−4, 8,32e−5, **1,55e−5** |
  | com $(X,Y)$ de $e_0=0{,}06$ | menor valor singular 1,73e−5 |

  - **Direção mais fraca:** $\chi_1$ −0,52, $\chi_2$ +0,65, $X$ −0,33, $Y$ −0,43 (unidades da escala).
  - **Alcance.** Uma mudança de 0,64 unidades de escala nela ($\Delta\chi_1\approx-0{,}033$, $\Delta\chi_2\approx+0{,}042$,
    $\Delta e_0\approx0{,}035$) muda os resíduos só 1e−5, o tremor.
  - **Conclusão.** As direções excêntricas entram no núcleo aproximado: perto de A, uma excentricidade de alguns
    centésimos compensada pelos spins fica a ~1e−5–1e−4.
- **Linearidade.** As colunas $(X,Y)$ medidas com $e_0=0{,}03$ e 0,06 diferem 195% e 146%. O harmônico em $\ell_0$
  gira com $e_0$, porque a fase radial acumulada de 10 Hz até a fusão depende de $e_0$. A média em $\ell_0$ cresce
  como $e_0^2$ (razão 3,84 para o fator 4 esperado).
  - A variável natural é a fase radial perto da fusão, como em [Nee2025].
  - O jacobiano em $(X,Y)$ é, por isso, só local (em $e_0\approx0{,}03$).
- **Buscas locais com $e_0=0{,}03$** a partir dos dois controles circulares, $\ell_0=0$ ou $\pi$: 6,6e−4, 1,8e−4,
  4,0e−4 e **1,5e−4** ($e_0=0{,}029$, $q=1{,}240$, $\chi=(0{,}421,\,-0{,}377)$, $\ell_0\approx\pi$).
  - Não caem abaixo do piso circular (2,4e−5).
  - Ficam na mesma ordem que o segundo controle (1,0e−4).

**Tarefa 4: anomalia** (`exp40_anomalia.txt`; figura e40a,b). Amplitude do 1º harmônico em $\ell_0$ (12 valores),
relativa à média, para as memórias globais $m=0$ desde 10 Hz:

| Sistema, $e_0$ | $e_\text{EOB}$ em −500 M / −100 M | desl20 | spin30 | cm20 | giro10 | $E_\text{janela}$ | $M_f$ |
|---|---|---|---|---|---|---|---|
| A, 0,02 | 0,0055 / 0,0029 | 8,4e−4 | 6,6e−4 | 7,6e−4 | 6,5e−4 | 8,7e−4 | 4,0e−5 |
| A, 0,05 | 0,0137 / 0,0074 | 2,0e−3 | 1,4e−3 | 1,8e−3 | 1,3e−3 | 2,1e−3 | 9,8e−5 |
| A, 0,1 | 0,028 / 0,015 | 4,1e−3 | 3,4e−3 | 3,7e−3 | 3,4e−3 | 4,3e−3 | 2,0e−4 |
| A, 0,2 | 0,058 / 0,031 | 8,1e−3 | 6,0e−3 | 7,3e−3 | 6,0e−3 | 8,4e−3 | 4,0e−4 |
| A, 0,3 | 0,095 / 0,051 | 1,35e−2 | 1,18e−2 | 1,21e−2 | 1,18e−2 | 1,40e−2 | 6,5e−4 |
| B, 0,02 | 0,0060 / 0,0033 | 9,2e−4 | 7,2e−4 | 9,0e−4 | 7,1e−4 | 9,4e−4 | 3,3e−5 |
| B, 0,1 | 0,031 / 0,017 | 4,5e−3 | 3,4e−3 | 4,4e−3 | 3,4e−3 | 4,6e−3 | 1,6e−4 |
| B, 0,2 | 0,064 / 0,035 | 9,3e−3 | 6,1e−3 | 9,0e−3 | 5,9e−3 | 9,4e−3 | 3,4e−4 |
| B, 0,3 | 0,104 / 0,057 | 1,56e−2 | 1,30e−2 | 1,52e−2 | 1,29e−2 | 1,58e−2 | 5,5e−4 |

- **Escala em $e_0$.** Linear de 0,02 a 0,3: expoente ajustado 1,02 (A) e 1,03 (B) para desl20 e $M_f$.
  $a_1/e_0=0{,}040$–0,045 (A) e 0,045–0,052 (B) no deslocamento.
- **Harmônicos superiores.** O 2º harmônico é 1–26% do 1º (cresce com $e_0$); o resto, ≤ 6%.
- **Onde nasce.** A variação com $\ell_0$ vem da fusão: a memória acumulada só nos últimos 100 M varia 1,32–1,44
  vezes o total (correlação 0,90–0,94). Desde −500 M, 0,83–0,86: há uma compensação parcial entre −500 e −100 M.
- **$M_f$ pelo balanço.** Varia com amplitude relativa 4,0e−4 (A) e 3,4e−4 (B) em $e_0=0{,}2$.
- **Inconsistência interna do modelo.** O *ringdown* do SEOBNRv5EHM usa $M_f$ e $\chi_f$ de ajustes quase circulares,
  que não dependem de $\ell_0$. A energia irradiada varia; as frequências quase normais, não. A inconsistência é
  desse tamanho.
- **De onde vem a variação de $E_\text{janela}$.** A energia EOB no fim da dinâmica ($\nu H$) varia 1,9e−4–6,6e−4
  pico a pico, com correlação fraca com $E_\text{janela}$ (−0,50 a +0,22). A energia irradiada depois do fim da
  dinâmica varia mais (2,6e−4–1,5e−3). Neste modelo a dependência sai do mergulho mais o acoplamento
  fusão-*ringdown*, não só de $H$ em $t_\text{match}$.
- **Controle PN** (newtoniano + Peters, só inspiral, sistema B):
  - **Fim na separatriz secular** $p=6+2e$ (duração idêntica para todo $\ell_0$): 1º harmônico do deslocamento 4,5e−3,
    9,3e−3 e 1,50e−2 para $e_0=0{,}1$, 0,2 e 0,3. Quase os mesmos números do SEOBNRv5EHM no B (4,5e−3, 9,3e−3,
    1,56e−2). No spin: 2,1e−3, 4,0e−3 e 6,6e−3, contra 3,4e−3, 6,1e−3 e 1,3e−2.
  - **Mecanismo PN.** É o último ciclo radial incompleto antes de um corte fixo no tempo secular. A coincidência
    numérica sugere que o tamanho do efeito é fixado pela fase radial com que a emissão termina, e não por
    detalhes da fusão do modelo [H].
  - **Corte em $r(t)<8$ M instantâneo.** Descontínuo: o instante de corte salta até 65–118 M, um período radial. Dá
    2,9e−2–3,8e−2, com 2º harmônico de metade do 1º. É só uma cota grosseira.
- **Segundo modelo.** O TEOBResumS 4.4.1 instalado ignora `ecc`, `ecc_freq` e `anomaly`: saídas idênticas bit a bit
  ao circular (`exp40_teob.txt`). Não houve checagem independente com outro EOB excêntrico.

## II.5 Tentativas de refutação e alternativas

- **H16.1.** Separei as duas correções (quatro variantes). Resolvi de novo com seis tentativas: três partidas e dois
  passos. Conferi o (2,0) newtoniano contra o modelo PN.
- **H16.2, cinco abordagens:**
  1. partidas nos pares do exp12;
  2. partida com $\ell_0=\pi$;
  3. partidas na família circular de duas janelas com $e_0=0{,}05$;
  4. jacobiano em A com direções excêntricas;
  5. buscas locais com $e_0=0{,}03$ a partir da família circular deste mesmo modelo.

  Também fiz o controle circular. Nada chegou ao piso (≤ 3e−5) com $e_0>0$. O melhor foi 1,5e−4 com
  $e_0\approx0{,}03$.
- **H16.4.** Separação em janelas (últimos 100 e 500 M). Escala em $e_0$ com cinco valores. Dois sistemas. Energia
  EOB no fim da dinâmica. Dois controles PN (corte secular e corte instantâneo). Tentativa de segundo modelo
  (TEOBResumS, indisponível no ramo excêntrico). Literatura de RN.

## II.6 Contraexemplos e limitações

- **Só $m=0$**, como no exp12. Com todos os $m$ entra a fase de referência (L00). A anomalia mexe também nos
  multipolos $m\neq0$; não medi.
- **Tremor ~1e−5 do SEOBNRv5EHM.** Resíduos abaixo disso (9,5e−7 etc.) são sorte de amostragem, não precisão.
- **Orçamento do otimizador** nas duas janelas: ~34 iterações por partida. A ausência de solução com $e_0\ge0{,}1$
  não está provada.
- **Definições.** A primeira janela usa a definição do modelo (EccIC = 1) e a segunda a média entre periastros. As
  duas são definições físicas razoáveis, mas não a mesma.
- **(2,0) newtoniano** desligado entre −200 e −100 M por escolha; o efeito total é ≤ 1,1e−5.
- **Validação.** Nenhuma simulação de RN excêntrica pública foi baixada; o tamanho absoluto da dependência em $\ell_0$
  na memória não está validado. Só há a comparação qualitativa com [Nee2025] (abaixo).
- **Modelo.** O SEOBNRv5EHM supõe *ringdown* quase circular (QNMs independentes de $\ell_0$), enquanto a energia
  irradiada depende de $\ell_0$.

## II.7 Literatura e originalidade

Como conferi:
- API do arXiv: "mean anomaly" AND remnant; "mean anomaly" AND memory (nenhum resultado); memory AND eccentric AND
  "black hole"; SEOBNRv5EHM;
- WebSearch;
- texto de [Nee2025] (arXiv:2503.05422, §3.2–3.3, fig. 6 e 11);
- resumo de [WLZW2025] (arXiv:2510.08105).

O que já se sabe:
- **[Nee2025]** (RN SpEC, massas iguais, sem spin): $M_f$, o pico de $|h_{22}|$ e a luminosidade de pico oscilam com a
  anomalia média a $e$ fixo, com amplitude quase linear em $e$ (luminosidade até ~5%). A estimativa de $M_f$ do
  SEOBNRv5EHM pela Hamiltoniana em $t_\text{match}$ reproduz "razoavelmente" amplitude e fase. No eixo da fig. 6,
  $\delta M_f/M$ cabe em ±8e−4 com $e\approx0{,}17$ em $\langle\omega_{22}\rangle=0{,}069/M$ (leitura grosseira da
  figura).
  - Comparação com o meu número: no B, $e_\text{EOB}\approx0{,}064$ em −500 M, onde $M\omega_{22}\approx0{,}066$;
    obtenho amplitude $3{,}4$e−4. Por unidade de $e$, ~5e−3 aqui contra ~3–5e−3 da RN.
  - Mesma ordem de grandeza. Definições de $e$ diferentes; não é uma comparação quantitativa.
- **[WLZW2025]** (RIT): oscilações com a anomalia em massa, spin e recuo do remanescente.
- **[Favata2011] e [EBF2019]:** memória de órbitas excêntricas (PN).

O que não encontrei: um trabalho que diga que a **memória** depende da anomalia.

Conclusões:
- A dependência em $\ell_0$ da memória é física no sentido qualitativo: ela segue da dependência de $E_\text{rad}$ e
  $M_f$ na anomalia, publicada em RN, porque a memória de deslocamento é dominada pela fusão.
- A família excêntrica de dimensão 4 e o estudo de duas janelas com $(e_0,\ell_0)$ livres são deste projeto. Não
  alego novidade além de resultados de modelo.

## II.8 Próximos experimentos

1. Repetir a tarefa 4 com simulações excêntricas de RN que tenham CCE (memória), ou ao menos com o modelo de
   remanescente excêntrico de [Nee2025] e de arXiv:2605.00124. Assim a parte "física × artefato" fica quantitativa.
2. Duas janelas com $e_0\ge0{,}1$, com mais orçamento e partidas aleatórias, usando como variável a fase radial perto
   da fusão em vez de $\ell_0$ em 10 Hz (a dependência fica mais simples, [Nee2025]).
3. Incluir os multipolos $m\neq0$ e a fase de referência; ver se a anomalia é separável da fase orbital.
4. Instalar o TEOBResumS-Dalí (ramo excêntrico) para um segundo modelo.

## II.9 Tabela de hipóteses (L16)

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H16.1 | as correções mudam B acima do tremor, mas os pares sobrevivem | confirmada numericamente | (2,0) ≤ 1,1e−5; $E_\text{lig}$ até 5,7e−5 na CM; re-solvidos a 9,5e−7–2,4e−5; nos pares que já estavam no piso ($q_B=2$) os parâmetros mudam ≤ 4e−5 em $M$ e ≤ 1,4e−4 em $\chi_1$ |
| H16.2 | com duas janelas existe excêntrica ($e_0\ge0{,}1$) que imita A no piso | inconclusiva (não encontrada) | melhor 3,6e−3 em 9 partidas com orçamento limitado |
| H16.3 | as direções excêntricas entram no núcleo aproximado em A | confirmada numericamente (localmente, $e_0\approx0{,}03$) | menor valor singular 5,4e−5 → 1,55e−5; busca local 1,5e−4 com $e_0=0{,}029$ |
| H16.4a | dependência em $\ell_0$ linear em $e_0$ | confirmada numericamente | expoentes 1,02–1,03; $a_1/e_0\approx0{,}04$–0,05 |
| H16.4b | ela nasce no mergulho (últimos ~100 M) | confirmada numericamente | razão 1,32–1,44 e correlação 0,90–0,94 nos últimos 100 M |
| H16.4c | ela é física, não artefato do modelo | confirmada qualitativamente pela literatura; magnitude não validada | [Nee2025]: $M_f$ oscila com a anomalia, ∝ $e$, e a estimativa EOB acompanha; controle PN dá o mesmo tamanho; ringdown do modelo inconsistente |

---

## Referências citadas

- [Nichols2018] D. A. Nichols, PRD 98, 064032 (2018); arXiv:1807.08767 (lido: eqs. 3.5–3.13, 4.23–4.25, nota 8).
- [FN2017] É. É. Flanagan, D. A. Nichols, PRD 95, 044002 (2017); arXiv:1510.03386.
- [Mitman2020] K. Mitman et al., PRD 102, 104007 (2020); arXiv:2007.11562.
- [Mitman2024] K. Mitman et al., CQG 41, 223001 (2024); arXiv:2405.08868 (lido: §IV, fig. 3 e nota 24: no (2,0), a contribuição do aspecto de massa é o toque do *ringdown*).
- [GM2024] A. M. Grant, K. Mitman, CQG 41, 175003 (2024); arXiv:2312.02295.
- [SGN2024] S. Siddhant, A. M. Grant, D. A. Nichols, CQG 41, 205014 (2024); arXiv:2403.13907. [SGN2026] arXiv:2608.23739.
- [RSHB2024] M. Rosselló-Sastre, S. Husa, S. Bera, "A waveform model for the missing quadrupole mode from black hole coalescence: memory effect and ringdown of the (ℓ=2, m=0) spherical harmonic", arXiv:2405.17302 (revista não conferida). Conferência: PDF (§I; modelam memória e toque do (2,0) separadamente).
- [VTRH2024] J. Valencia et al., PRD 110, 124026 (2024); arXiv:2406.16636.
- [Yoo2023] J. Yoo et al., PRD 108, 064027 (2023); arXiv:2306.03148 (lido: quadro BMS PN; janela de hibridização 2500–3500 M antes do pico).
- [GBE2025] A. Gamboa et al. (SEOBNRv5EHM), PRD 112, 044038 (2025); arXiv:2412.12823.
- [Nee2025] P. J. Nee, A. Gamboa, H. P. Pfeiffer, L. Pompili, A. Ramos-Buades, V. Varma, M. Boyle, A. Buonanno, R. Enficiaud, L. E. Kidder, M. A. Scheel, "Impact of eccentricity and mean anomaly in numerical relativity mergers", CQG 42, 135011 (2025); arXiv:2503.05422 (lido: §3.2–3.3).
- [WLZW2025] H. Wang, B. Liu, Y.-C. Zou, Q.-W. Wu, "The influence of the mean anomaly on the dynamical quantities of binary black hole mergers in eccentric orbits", arXiv:2510.08105 (revista não conferida).
- [Favata2011] M. Favata, PRD 84, 124013 (2011). [EBF2019] M. Ebersold et al., PRD 100, 084043 (2019).
- [DaRe2025] Da Re et al., NRSur3dq8BMSRemnant (surfinBH), arXiv:2503.09569 (docstring lida: o NRHybSur3dq8_CCE está no quadro BMS PN).
