# L10 e L11 — Precessão: multipolos $m\neq0$, spins no plano e zeros da memória no céu (agente D6)

Modelo: NRSur7dq4 (Varma et al. 2019), substituto precessante de RN com modos $\ell\le4$ no referencial inercial. O
domínio de treino é $q\le4$ e $|\chi|\le0{,}8$; a onda começa em $t=-4300\,M$.

Janela: de $f_{22}=f_0=0{,}007/M$ até o fim da onda ($t=+100\,M$). $t_i$ é o instante em que a frequência orbital
coprecessante vale $\pi f_0$. Os spins e o referencial são os da época de referência $f_\text{ref}=f_0$:
$z=\hat L(t_i)$ e $x=\hat n(t_i)$. Para $M=65\,M_\odot$, $f_0$ corresponde a 21,9 Hz.

Nível A: memórias nulas pelos fluxos de todos os modos $\ell\le4$ (21 modos), multipolos de saída até $\ell=8$; CM
como no L00 (nula + ordinária com o deslocamento de janela).

Código: `codigo/exp33_*.py`, `exp34_*.py` e `exp35_observador.py`. Resultados em `resultados/exp33_*`, `exp34_*` e
`exp35_*`; figuras `figuras/e33_*.png`, `e34_*.png` e `e35_*.png`. Rótulos: [E] estabelecido, [D] derivado aqui,
[H] hipótese, [S] especulação.

---

## 1. Pergunta e hipóteses

**L10.** Com spins precessantes, as memórias globais ganham multipolos $m\neq0$. Eles carregam informação dos spins
no plano? Que informação? Qual a relação com o recuo e com a direção do momento angular irradiado? Quantos números
de memória vê um observador?

**L11.** O padrão de memória de deslocamento no céu é um campo de linhas: polarização, direções sem sentido, peso de
spin $-2$. Onde ficam os seus zeros e quais são os seus índices? Vale Poincaré–Hopf, isto é, a soma dos índices é 2?
Com precessão, os zeros seguem $J_\text{rad}$ ou o spin final?

Hipóteses (status na seção 9):

- **H10.1** Com spins alinhados, NRSur7dq4 e NRHybSur3dq8_CCE concordam em ~1% no nível A, na mesma janela.
- **H10.2** Os modos $m=0$ coorbitais do NRSur7dq4 não contêm memória.
- **H10.3** (do 09) Os multipolos $m=\pm1,\pm2$ codificam a inclinação do momento angular irradiado.
- **H10.4** (do 09) O posto do jacobiano em relação aos 7 parâmetros sobe. Com spins alinhados, 3 parâmetros dão
  posto 3.
- **H10.5** A direção mais fraca é o azimute comum dos spins no plano.
- **H10.6** A parte secular dos $m\neq0$ é a rotação do padrão axissimétrico pelo eixo coprecessante.
- **H10.7** Um observador vê 4 números de memória mensuráveis (mais a giroscópica), contra 10 parâmetros.
- **H11.1** Soma dos índices = 2 (normalização de campo de linhas).
- **H11.2** Sem precessão e só com $m=0$, há dois zeros de índice +1 nos polos.
- **H11.3** Os zeros de índice +1 são instáveis: qualquer $m\neq0$ os divide em pares de +1/2.
- **H11.4** [D] Para o campo $\ell=2$ puro, os zeros são os "eixos ópticos" do tensor de memória.
- **H11.5** (do 09) Com precessão, os zeros seguem $J_\text{rad}$; alternativa: seguem $\chi_f$.

## 2. Fundamentação e equações

**Tensor de polarização.** Para o campo $h(\hat n)=\sum a_{\ell m}\,{}_{-2}Y_{\ell m}(\hat n)$, com $h=h_+-ih_\times$:
$$P=h_+\,e_++h_\times\,e_\times,\qquad e_+=\hat\theta\hat\theta-\hat\phi\hat\phi,\qquad e_\times=\hat\theta\hat\phi+\hat\phi\hat\theta.$$
É um tensor tangente global, sem a singularidade da base nos polos. Numa base tangente fixa $(u,w)$ com
$u\times w=\hat n_0$:
$$z=P_{uu}-P_{ww}+2iP_{uw}=|h|\,e^{2i\psi}.$$
O índice de um zero isolado é (enrolamento de $\arg z$)/2 num laço anti-horário visto de fora. Para campos de linhas
em $S^2$, a soma dos índices é $\chi(S^2)=2$ [E] (Poincaré–Hopf para campos de linhas; Hopf). Os índices genéricos
são $\pm1/2$.

Se a convenção de $h_\times$ estivesse trocada, a soma daria −2. Isso serve de teste da orientação: deu +2 em todos
os casos.

**Campo elétrico $\ell=2$ puro: eixos ópticos [D].** A memória de deslocamento é elétrica:
$h=\tfrac12\bar\eth^2\Phi$, com $\Phi$ real. Para $\Phi=\hat n\cdot A\,\hat n$ ($A$ simétrico sem traço), a hessiana
covariante na esfera é
$$\nabla\nabla\Phi=2\,P_\perp A P_\perp-2\Phi\,P_\perp ,$$
e sua parte sem traço se anula se, e só se, $A$ restrito ao plano tangente for isotrópico. São as seções circulares do
"elipsoide" de $A$. Com autovalores $\lambda_1\ge\lambda_2\ge\lambda_3$ e autovetores $e_i$, os zeros são
$$\hat n=\cos\alpha\,e_1\pm\sin\alpha\,e_3\ \text{e antípodas},\qquad \sin^2\alpha=\frac{\lambda_2-\lambda_3}{\lambda_1-\lambda_3}.$$
São quatro zeros de índice +1/2: a soma é 2, e são iguais pela simetria $\hat n\to-\hat n$ e pela reflexão no
plano $(e_1,e_3)$.

- **Caso uniaxial** ($\lambda_2=\lambda_3$): os quatro zeros se fundem dois a dois em $\pm e_1$, com índice +1. É o
  caso alinhado, $\Phi\propto Y_{20}$.
- **Perturbação $\epsilon$:** $\alpha\approx\sqrt{(\lambda_2-\lambda_3)/(\lambda_1-\lambda_3)}\sim\sqrt\epsilon$. A
  separação dos zeros amplifica pela raiz quadrada qualquer quebra da simetria axial.

É o mesmo mecanismo pelo qual o Sol, ponto de índice +1 no padrão de polarização do céu, se divide nos pontos de
Babinet e Brewster, de +1/2 cada (Berry, Dennis & Lee 2004). Aqui ele aparece nos zeros da memória.

**Modelo do eixo precessante [D, aproximação].** Suponha que a emissão instantânea é axissimétrica em torno do eixo
coprecessante $\hat z_c(t)$. Então a taxa de memória $\ell=2$ é
$$\dot a_{2m}(t)\approx\rho(t)\sqrt{4\pi/5}\;\overline{Y_{2m}(\hat z_c(t))},$$
e o tensor de memória é $A\propto\int dE\,(3\hat z_c\hat z_c^T-1)$. Logo $e_1$ é o autovetor principal de
$$Q=\int dE\,\hat z_c\hat z_c^T,$$
que chamo de eixo de luminosidade $e_Q$, e a previsão é $\sin^2\alpha=(q_2-q_3)/(q_1-q_3)$.

**Momento angular irradiado.** Fórmulas de Ruiz et al. 2008 para $dJ/dt$ em termos de $h_{\ell m}$
(`exp33_comum.taxa_J`). O recuo vem dos modos $\ell=1$ de $\int|\dot h|^2$, como em `binarias.momento_irradiado`.

**Jacobiano módulo rotações.** O observador não conhece a orientação da fonte. Os geradores de rotação agem nos
multipolos como $\delta a_{\ell m}=-i(L_k a)_{\ell m}$, para qualquer peso de spin. Projeto $J_\text{int}$ (88×7)
fora do espaço gerado por $J_\text{rot}$ (88×3). O vetor de observáveis é o vetor real ortonormal dos multipolos
$\ell\le4$ de todos os $m$:

- deslocamento, spin e CM: $\ell=2..4$, 21 componentes cada;
- giroscópica: $\ell=0..4$, 25 componentes.

São 88 no total, com $\sum v^2=\int|\text{campo}|^2$.

## 3. Experimentos

| Script | O que faz | Saída |
|---|---|---|
| `exp33_comum.py` | `gerar7` (rede fixa, dinâmica; opção de zerar os $m=0$ coorbitais), `instante_orbital`, `memorias7` (memórias, $J_\text{rad}$, $P_\text{rad}$, $M_f$, spins em $t_i$), `vetor_real`, `girar_gerador` | — |
| `exp33_validacao.py` | (a) gerador; (b) alinhados contra CCE; (c) $J_\text{rad}$ e recuo contra surfinBH; (d) dt; (e) $m=0$ coorbitais; (f) suavidade; (g) memória nos $m=0$; (h) bico em spin nulo | `resultados/exp33_validacao.txt` |
| `exp33_jacobiano.py` | jacobianos em 6 pontos J0–J5 (passos $10^{-5}$ e $5\cdot10^{-6}$), rotações (conferidas por `init_quat`), invariantes de rotação, coordenadas físicas dos spins no plano, $\ell\le8$ | `resultados/exp33_jacobiano.txt`, `exp33_jacobianos.npz`; `figuras/e33_jacobiano.png` |
| `exp33_secular.py` | séries acumuladas dos $m\neq0$, média orbital, varredura do início da janela, modelo do eixo precessante | `resultados/exp33_secular.txt`, `figuras/e33_secular.png` |
| `exp34_zeros.py` | localizador de zeros (mínimos locais + refinamento + busca local), índice por laço, contagem independente pela icosfera, eixos ópticos; testes sintéticos | `resultados/exp34_zeros_testes.txt` |
| `exp34_populacao.py` | 8 sistemas nomeados + 60 aleatórios ($q\in[1,4]$, $|\chi|\in[0{,}1;0{,}8]$, direções isótropas, semente 11) | `resultados/exp34_populacao.txt`, `.npz`; `figuras/e34_ceu.png`, `e34_angulos.png` (`exp34_figura.py`) |
| `exp35_observador.py` | números de memória num observador e jacobianos 4×10 e 5×10; varredura do céu | `resultados/exp35_observador.txt`, `figuras/e35_observador.png` |

Pontos do jacobiano, como $(q;\ \vec\chi_A;\ \vec\chi_B)$:

| Ponto | $q$ | $\vec\chi_A$ | $\vec\chi_B$ |
|---|---|---|---|
| J0 (alinhado) | 1,2 | (0, 0, 0,3) | (0, 0, −0,2) |
| J1 | 2 | (0,5, 0, 0,2) | (0, −0,3, 0,1) |
| J2 | 1,2 | (0,6, 0,2, 0) | (−0,3, 0,4, 0,2) |
| J3 | 3 | (0,7, 0, 0) | (0, 0, 0,1) |
| J4 | 1,05 | (0,5, 0, 0) | (−0,5, 0, 0) |
| J5 | 1,5 | (0,3, 0,3, −0,3) | (0,2, −0,4, 0,4) |

Custo: uma onda mais as memórias leva ~0,1 s. Cada jacobiano completo leva 10–50 s. A população inteira levou
~8,5 min, num processo, com `OMP_NUM_THREADS=1`.

## 4. Resultados

### 4.1 Validação (`resultados/exp33_validacao.txt`)

**(a) Gerador.**
- Com `zerar_m0=False`, `gerar7` reproduz a chamada pública exatamente (diferença 0).
- Com spins alinhados, o quatérnio coprecessante desvia da identidade só ~1e-4 até o pico, mas chega a 2,5e-2 em
  $t>50\,M$.
- Isso cria um piso de $m$ ímpar espúrio. Em $q=1$ sem spin (onde deveria ser nulo), $|{\rm spin}_{21}|$ vale 1,3e-4
  no NRSur7dq4 contra 2,8e-6 no CCE, e o recuo vale 6,7e-6 contra 1,8e-7.

**(g) Memória nos $m=0$ coorbitais [H10.2].**
- O (2,0) coorbital termina em 4,7e-5 a 7,3e-5, contra uma memória de deslocamento (2,0) de 0,028 a 0,086 nesses
  sistemas. Não há memória neles.
- Os $m=0$ coorbitais são radiação ordinária: Re até 1,5e-2 perto do pico e, em precessão, Im até 1,7e-2.
- Por isso o padrão usa todos os modos.
- Zerá-los (variante "como o CCE") muda o vetor de memórias em 7e-4 (P1) e 1,6e-3 (P4). Mas no P4, configuração de
  supercoice, a parte $m\neq0$ muda em 10% a 73%: ela é pequena (~0,5% do total) e dominada por esses modos.

**(b) Alinhados contra CCE [H10.1].** Mesmos modos de entrada ($\ell\le4$ do CCE), mesma janela, cinco sistemas
($q$ de 1 a 4):

| Multipolo | Diferença |
|---|---|
| desl20 | ≤ 1,4% |
| spin30 | ≤ 0,8% |
| giro10, giro30 | ≤ 0,8% |
| cm20 | ≤ 4,8% (cancelamento entre as partes nula e ordinária) |
| desl40, cm40 | 1,1% a 21% e 5% a 43% |

- Com os modos extras do NRSur7dq4 — (3,1), (4,1) e (4,2) —, desl40 muda de 2% a 46%.
- **Achado lateral:** o nível A do CCE (e de `binarias`) subestima o deslocamento $\ell=4$ em ~10% ou mais por
  faltarem esses modos. Os termos cruzados são lineares na amplitude do modo ausente, embora a sua energia seja só
  ~1e-6 (L00).
- Os termos de borda $m\neq0$ (spin21, giro21, desl31) concordam a 0,9–1,1 quando não nulos por simetria.
- As energias de janela diferem até 2% (q = 3; demais ≤ 0,8%); $t_i$ difere até 6,7 M.

**(c) Recuo e momento angular.**
- $-P/M_f$ das memórias concorda com $v_f$ do surfinBH NRSur7dq4Remnant em direção e módulo. Exemplos: P1
  (0,00066, −0,00074, 0,00347) contra (0,00066, −0,00073, 0,00333); P2 −0,00681 contra −0,00643 em $z$.
- $J_\text{rad}$ concorda com $J_i^{PN}-M_f^2\vec\chi_f$ a 0,8e-3 a 2e-2 (de |J| ~ 0,2–0,4). O resto é compatível
  com $|L|$ só 2PN não spinorial e com $\hat L_N\neq\hat z_c$.
- Ângulos medidos:

  | Sistema | $\angle(\chi_f,\ \text{eixo no pico})$ | $\angle(J_\text{rad},\chi_f)$ |
  |---|---|---|
  | P1 | 12,4° | 3,3° |
  | P3 | 27,1° | 8,2° |

**(d) e (f) Numérica.**
- dt 0,25 contra 0,125: 3e-8 a 4e-8.
- Suavidade: derivadas com passos 1e-3 e 1e-4 diferem 6e-7 a 4,5e-5.

**(h) Bico em spin nulo.**
- Em $\vec\chi_B=0$, as memórias têm um bico: $|v(\pm h)-v_0|/h\approx0{,}06$ dos dois lados, e a segunda diferença
  cresce como $1/h$ (1,2e5 em $h=10^{-6}$).
- Com $\vec\chi_B=(0,0,0{,}1)$ tudo é suave (segunda diferença 0,097, constante).
- É artefato da parametrização do substituto, não física.
- Consequência: no primeiro cálculo de J3 (com $\chi_B=0$), o posto aparente era 3. Era artefato, refutado aqui.

### 4.2 Jacobiano dos spins no plano [H10.4, H10.5] (`resultados/exp33_jacobiano.txt`)

**Precisão.** Erro numérico $\|J(10^{-5})-J(5\cdot10^{-6})\|$ de 6,6e-10 a 3,3e-6 (J5; os demais ≤ 7,7e-8). O gerador de rotação concorda com
rotações finitas (`init_quat`) a ≤ 4e-9.

**Valores singulares de $P_\perp J_\text{int}$ (intrínsecos módulo rotação), divididos por $|v|$:**

| Ponto | 7 valores singulares | > 1e-2 | > 1e-3 |
|---|---|---|---|
| J0 (alinhado) | 4,0e-1 2,9e-1 4,7e-2 1,5e-2 1,1e-2 5,5e-3 4,4e-3 | 5 | 7 |
| J1 | 2,5 4,5e-1 1,2e-1 2,4e-2 1,0e-2 7,2e-3 1,0e-3 | 5 | 6 |
| J2 | 1,1 1,8e-1 9,4e-2 2,5e-2 1,5e-2 1,1e-2 1,4e-3 | 6 | 7 |
| J3 | 7,5 7,2e-1 2,7e-1 3,6e-2 2,7e-2 1,4e-2 1,2e-3 | 6 | 7 |
| J4 | 4,8e-1 1,4e-1 7,2e-2 3,5e-2 1,7e-2 1,3e-2 3,5e-3 | 6 | 7 |
| J5 | 2,3 3,7e-1 8,5e-2 4,7e-2 1,3e-2 1,1e-2 1,2e-3 | 6 | 7 |

- **Posto 7 de 7 em todos os pontos** (critério: > 10× o erro numérico). Inclui o ponto alinhado J0: as derivadas
  em relação aos spins no plano entram em primeira ordem pelos $m\neq0$, pela inclinação.
- O posto 7 se mantém só com as linhas $m=0$ do referencial da fonte, só com $m\neq0$, com cada tipo de memória
  sozinho e com $\ell\le8$ (312 componentes).
- Caminho independente: o jacobiano de 60 invariantes de rotação (potências por $\ell$, potências cruzadas, traços
  de produtos dos tensores $\ell=2$, contrações com o vetor $\ell=1$ da giroscópica) também tem posto 7 em todos os
  pontos. O erro relativo vai de 3e-8 a 1,5e-5.
- **Efetivamente:** acima de 1% de $|v|$, que é a ordem da discordância entre modelos na seção 4.1, sobram 5 ou 6
  direções. A sétima, ~1e-3, está abaixo do erro de modelo.

**Coordenadas físicas** $(|\chi_{A\perp}|,|\chi_{B\perp}|,\bar\varphi,\Delta\varphi)$, onde $\bar\varphi$ é o
azimute médio dos spins no plano em relação a $\hat n(t_i)$ e $\Delta\varphi=\varphi_A-\varphi_B$. Projetando fora
as rotações e $(q,\chi_{Az},\chi_{Bz})$:

| Ponto | Valores singulares (vetores dominantes) |
|---|---|
| J1 | 9,6e-2 ($|\chi_{A\perp}|$) · 5,8e-3 ($|\chi_{B\perp}|$) · 2,2e-3 ($\Delta\varphi$) · 4,8e-4 ($\bar\varphi$, 0,97) |
| J2 | 4,5e-2 · 1,1e-2 · 8,5e-3 · 1,1e-3 ($\bar\varphi$ 0,96) |
| J5 | 6,6e-2 · 1,1e-2 · 3,5e-3 · 6,2e-4 ($\bar\varphi$ 1,00) |
| J4 (supercoice, spins antiparalelos) | 6,7e-2 · 1,8e-2 · 9,0e-3 · 1,7e-3 ($\Delta\varphi$ −0,87, $\bar\varphi$ −0,45) |

- **A informação dos spins no plano vem nesta ordem:** módulo do maior spin no plano (≈ $\chi_p$) ≫ módulo do
  menor > diferença de azimutes > azimute comum.
- O azimute comum $\bar\varphi$, que no recuo é a direção mais forte (o recuo oscila com ele), é a direção mais
  fraca das memórias.
- Os valores das colunas mostram que $\bar\varphi$ não é invisível: $|P_\perp J\,\partial_{\bar\varphi}|/|v|$ vale
  0,02–0,12. O que acontece é que o seu efeito imita uma combinação de $q$, $\chi_z$ e dos módulos. É
  quase-degenerescência, não insensibilidade.

**Relação com o recuo e com $J_\text{rad}$.**
- $J_\text{rad}$ é o $\ell=1$ do mesmo campo de fluxo de momento angular cujo $\ell\ge2$ dá as memórias de spin e
  de CM. O recuo é o $\ell=1$ do fluxo de energia cujo $\ell\ge2$ é a memória de deslocamento [E]. Os multipolos
  $\ell\ge2$ são independentes do $\ell=1$: não existe relação local exata.
- Os jacobianos de $(M_f,\vec\chi_f,\vec v_f)$ (surfinBH) têm posto 7, mas valores singulares mais espalhados: o
  menor vai de 5,1e-5 (J2) a 5,1e-4 (J4). Portanto o remanescente sozinho também tem uma direção quase nula.
- A comparação de subespaços entre memórias e remanescente é trivial com posto 7 em dimensão 7, e foi descartada. O
  teste da "direção" está na L11 (4.5).

### 4.3 Parte secular e termos de borda [H10.6] (`resultados/exp33_secular.txt`, `figuras/e33_secular.png`)

- **Precessantes (P1, P3, P6):**
  - desl (2,1) final de 1,1e-2 a 1,5e-2, isto é, 18% a 125% de desl (2,0);
  - a média orbital em $t=-200\,M$ já é 16% a 25% do valor final de (2,1) e 36% a 49% do de (2,2);
  - o resto vem da fusão.
- **Alinhado AL1:** desl (2,1) final é 1,3e-5 (1,6e-4 de (2,0)). A deriva secular de ~1e-5 vem do ruído do
  quatérnio, ver 4.1(a).
- **Modelo do eixo precessante** (taxa axissimétrica girada por $\hat z_c(t)$):
  - final modelo/real: (2,1) entre 0,93 e 0,96; (2,2) entre 0,83 e 1,05;
  - médias orbitais em −200 M: 0,96 a 1,03;
  - fases dentro de 13°.
  - A parte secular é a rotação do padrão $m=0$ pelo eixo de precessão. O resto (5–17%) é da fusão.
- **Borda inicial.** Varrendo o início da janela num período orbital (285,7 M) e tirando a deriva linear:
  - deslocamento $\ell=2$: ≤ 1,7e-3 nos precessantes (1,7e-2 no (2,2) do alinhado, que é pequeno);
  - $\ell=3,4$: ≤ 1,1e-2;
  - spin: até 6%, e 23% num multipolo quase cancelado (P6 (3,1)).

### 4.4 Zeros: testes sintéticos [H11.1–H11.4] (`resultados/exp34_zeros_testes.txt`)

| Campo | Zeros | Soma dos índices |
|---|---|---|
| $\Phi=Y_{20}$, elétrico e magnético | 2 nos polos, índice +1 | 2,000 |
| $\ell=2$ triaxial, 3 casos | 4 de índice +1/2, coincidem com os eixos ópticos a ≤ 1,5e-6° | 2,000 |
| elétrico $\ell=2..4$ aleatório | 10 a 12, índices ±1/2 | 2,000 |
| E+B | 8 a 12 | 2,000 |

Os dois métodos (laço e icosfera) dão a mesma soma em todos os casos.

### 4.5 Zeros da memória de binárias [H11.1–H11.5] (`resultados/exp34_populacao.txt`, `figuras/e34_*.png`)

**Contagem.**
- Todos os 68 sistemas (8 nomeados + 60 aleatórios) têm exatamente 4 zeros, todos +1/2, soma 2,000. A icosfera dá
  2,00 em todos.
- Memória de spin: 6 zeros (cinco +1/2 e um −1/2, uma "estrela") em 7 de 8 nomeados; 4 em P6.
- CM: 4 zeros de +1/2.

**Alinhado.**
- Só com $m=0$ (AL1): zeros em (2e-6, −2e-6, 1) e no antípoda, índice +1 [H11.2].
- Com todos os $m$ (termos de borda da fusão), cada polo se divide em dois +1/2 [H11.3]:

  | Sistema | Meia abertura medida | Eixos ópticos | Outra referência |
  |---|---|---|---|
  | AL1 | 2,55° | 2,60° | $\sqrt\epsilon$ = 2,43°, com $\epsilon=|a_{2,m\neq0}|/|a_{20}|=1{,}79\text{e-}3$ |
  | AL2 | 1,33° | 1,25° | — |

- A divisão por raiz quadrada amplifica um efeito de 1,8e-3 para 2,5°.

**Direção dos zeros [H11.5]** (60 aleatórios). Ângulo entre $e_1$ (eixo dos pares de zeros) e cada direção, em
graus:

| Direção | Mediana | Percentil 90 | Máximo |
|---|---|---|---|
| $e_Q$ (eixo de luminosidade) | 0,89 | 2,35 | 4,13 |
| $J_\text{rad}$ | 3,25 | 7,06 | 19,1 |
| $\vec J_i$ | 5,08 | 10,0 | 25,1 |
| $\vec\chi_f$ | 6,01 | 12,5 | 30,1 |
| eixo no pico | 5,55 | 11,2 | 21,4 |
| $\hat L_i$ | 10,2 | 20,6 | 56,3 |

- O ponto médio de cada par dá números parecidos (mediana 1,33° para $e_Q$, 2,93° para $J_\text{rad}$).
- **Os zeros não seguem nem $J_\text{rad}$ nem o spin final.** Seguem o eixo coprecessante ponderado pela
  luminosidade: a orientação média do plano orbital durante a emissão, dominada pela fusão. Entre as grandezas de
  conservação, $J_\text{rad}$ fica mais perto que $\chi_f$.
- Casos extremos:

  | Sistema | $\angle(e_1,\hat L_i)$ | $J_\text{rad}$ | $\chi_f$ | $e_Q$ |
  |---|---|---|---|---|
  | P6 ($q=4$, $\chi_{A\perp}=0{,}8$) | 37° | 20° | 25° | 5,0° |
  | P3 | 21° | 11° | 16° | 2,7° |

**Abertura dos pares.**
- Mediana 3,2°, de 0,8° a 12,8°.
- Eixos ópticos do tensor $\ell=2$: erro mediano 0,38° (máximo 1,73°). O resto vem de $\ell\ge3$.
- Previsão por $Q$: erro mediano 1,1° (máximo 3,6°), correlação 0,85.
- A abertura mede a triaxialidade do tensor de memória: o espalhamento das orientações do plano orbital, mais os
  termos de borda da fusão.

### 4.6 Um observador [H10.7] (`resultados/exp35_observador.txt`)

**Números mensuráveis.** São 4:
- $\Delta h_+,\Delta h_\times$;
- $\int h_+,\int h_\times$ da memória (CM + spin; num ponto, as partes E e B não se separam).

A giroscópica é o 5º número, não mensurável (item 5).

**Invariantes por $\psi$.** Sob o ângulo de polarização $\psi$, os dois pares giram juntos de $2\psi$. Sobram 3
invariantes: $|\Delta h|$, $|\int h|$ e o ângulo relativo entre os dois.

**Parâmetros.** São 10: 7 intrínsecos mais $\iota$, $\phi$, $\psi$. Com $M$, $D$ e $t_0$, são 13.

**Jacobianos em $\iota=50°$, $\phi=0{,}3$** (linhas divididas pelo módulo de cada tipo):

| Ponto | 4×10 | 4×7 (ângulos fixos) |
|---|---|---|
| J0 | 3,06 1,82 0,58 0,38 | — |
| J1 | 5,87 3,30 2,25 0,40 | 5,72 1,62 0,89 0,36 |
| J2 | 3,11 2,62 1,43 0,048 | — |

Posto 4 em todos os pontos e em toda a grade do céu (menor valor singular entre 1,6e-2 e 6,2e-2, normalizado). O
núcleo tem dimensão ≥ 6, ou 9 com $M$, $D$, $t_0$.

**Assinatura de precessão.** $|\Delta h_\times|/|\Delta h_+|$ tem mediana no céu de 0,005 no alinhado J0 (só borda
$m\neq0$), contra 0,15–0,30 nos precessantes.

**Um interferômetro.** Mede $F_+h_++F_\times h_\times$: um número por tipo, 2 no total.

## 5. Tentativas de refutação e alternativas

**1. Posto 7 (H10.4).**
- (i) Dois passos, com erro estimado.
- (ii) Gerador de rotação conferido por rotação finita.
- (iii) Invariantes de rotação, caminho independente.
- (iv) Subconjuntos: $m=0$, $m\neq0$, cada tipo, $\ell\le8$.
- (v) Corte pelo erro de modelo, 1%: sobram 5–6 direções.
- (vi) Um posto 3 apareceu em J3: era o bico do substituto em $\chi_B=0$, refutado em (h).
- (vii) O ponto alinhado J0 também tem posto 7. É o ponto mais exigente, porque nele os spins no plano só entram
  pelos $m\neq0$.

**2. H10.5 (direção fraca = $\bar\varphi$).** Vale em J1, J2 e J5. No supercoice J4 a direção fraca é $\Delta\varphi$
com mistura de $\bar\varphi$. Não é universal: depende da configuração.

**3. H11.5 ($J_\text{rad}$) falhou.** Testei cinco direções alternativas: $\chi_f$, $\vec J_i$, $\hat L_i$, o eixo
no pico e $e_Q$. Testei também duas definições do eixo dos zeros: $e_1$ e o ponto médio dos pares. Só $e_Q$ fica
abaixo de 5° em toda a população.

$e_Q$ não é independente da onda: usa o quatérnio coprecessante. A afirmação física é: "os zeros marcam a
orientação do plano orbital ponderada por $dE$". É a previsão do modelo uniaxial. O modelo é aproximado: o erro na
abertura chega a 3,6°.

**4. Zeros perdidos.** A primeira versão do localizador achou 3 zeros em P2 e 2 em AL2, com soma 1,5 e 1,0, enquanto
a icosfera dava 2. Corrigi com centros de triângulos como candidatos e uma busca local quando a soma ≠ 2. Depois
disso: 68/68 com soma 2. Poincaré–Hopf serviu de detector de erro.

**5. Variante sem os $m=0$ coorbitais.** Muda as memórias globais em 7e-4 a 1,6e-3. Não afeta os zeros: o
tensor $\ell=2$ é dominado por $\ell=2$, $m=0$.

**6. H10.1 em $\ell=4$.** A discordância grande em desl40 e cm40 tem causa achada: modos ausentes no nível A do CCE
e cancelamento na CM. Não é erro do caminho NRSur7dq4.

## 6. Contraexemplos e limitações

- **Modelo.** NRSur7dq4 tem erro do substituto e começa em ~4300 M. A janela de 0,007/M é curta ($f\approx22$ Hz
  para $M=65$). As memórias são de nível A (quadráticas, $\ell\le4$ na entrada) e sem a memória dos próprios modos
  $m=0$.
- **Ruído do substituto.**
  - O quatérnio coprecessante tem ruído de ~1e-4 rad, e de 2,5e-2 depois de $t=50\,M$. Isso cria $m$ ímpar
    espúrio em ~1e-4 da memória.
  - Há um bico em spin nulo.
  - $q\ge1$ é obrigatório no surfinBH (usei `allow_extrap` só nos passos de $q=1{,}05$).
- **Posto local.** É posto em pontos, não injetividade global. Fibras e pares distantes não foram procurados (ver
  L01). O jacobiano é sem ruído de detector: posto 7 global não implica mensurável.
- **Observador.** 4 números contra 10 a 13 parâmetros: a memória sozinha não determina os spins no plano num
  observador. Os pares de zeros e as aberturas da L11 são propriedades do padrão global no céu, inacessíveis a um
  detector.
- **Escala.** Coordenadas $(q,\chi)$ adimensionais; os valores singulares dependem dessa escolha.

## 7. Literatura e originalidade

**Como conferi.** WebSearch com as consultas:
- "gravitational wave memory precessing binary m≠0 in-plane spins";
- "polarization singularities gravitational wave sky zeros Poincaré-Hopf memory";
- "memory and recoil kick relation multipoles";
- "memory sky pattern zeros tendex/umbilic precessing";
- "memory precessing Fisher in-plane spin identifiability".

Mais WebFetch dos resumos de arXiv:1107.2959, 1605.01273 e 2602.23425. A API do arXiv não respondeu (tempo
esgotado).

**Encontrado:**
- Memória $m\neq0$ em precessão: Talbot et al. PRD 98 064031 (2018) (os modos $|m|=1$ quase do tamanho do $m=0$);
  Rosselló-Sastre & Husa arXiv:2506.08888 (PRD 2025).
- Assimetria $\pm m$ dos modos oscilatórios mede a direção do spin no plano: Kalaghatgi & Hannam arXiv:2008.09957.
  Nas memórias, mostro que esse azimute é a direção mais fraca.
- Zeros da radiação no céu com Poincaré–Hopf para campos de linhas: Zimmerman, Nichols & Zhang PRD 84 044037 (2011).
  É a radiação instantânea (linhas de tendex e vórtice), não a memória.
- Padrão E/B da memória linearizada: Mädler & Winicour CQG 33 175006 (2016), sem zeros.
- Polarização do céu e divisão do ponto de índice +1 em +1/2: Berry, Dennis & Lee, New J. Phys. 6, 162 (2004).
- Singularidades de polarização de ondas gravitacionais em interferência de ondas planas: Rigouzzo et al.
  arXiv:2602.23425.
- Fisher singular da memória dominante: Gasparotto et al. PRD 107 124033 (2023).
- Kick memory: Favata 2009.
- Fórmulas de fluxo: Ruiz et al. 2008.

**Não encontrei** (o que parece novo, com a ressalva de busca limitada):
- (a) posto do jacobiano das memórias globais em relação aos 7 parâmetros, módulo rotações, e a hierarquia
  $|\chi_{A\perp}|\gg|\chi_{B\perp}|>\Delta\varphi>\bar\varphi$;
- (b) zeros da memória no céu, com o resultado dos eixos ópticos [D] (matemática elementar; a novidade é só a
  aplicação), a divisão $\sqrt\epsilon$ e a constatação de que os zeros seguem $e_Q$, não $J_\text{rad}$ nem $\chi_f$;
- (c) o modelo do eixo precessante para a parte secular. Ideia próxima de trabalhos de *twisting-up* de
  modos coprecessantes; não alego novidade.

## 8. Próximos experimentos

1. Fibras globais: há pares precessantes distintos com as mesmas 88 memórias, dentro de 1%? Minimizar como no L01.
2. Fisher de uma rede (2–3 detectores) para os 4 números do observador, com ruído; quanto de $\chi_p$ sobra.
3. Zeros com nível C ou com um modelo que tenha memória nos $m=0$ coprecessantes (NRSur7dq4 não tem).
4. Teste do modelo do eixo precessante em PN (precessão simples) para a parte inspiral, em forma fechada.
5. Ver se a abertura dos pares de zeros, como medida de triaxialidade, se relaciona com $\chi_p$ e $q$ por uma lei
   simples.

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H10.1 | NRSur7dq4 e CCE alinhados concordam ~1% no nível A, mesma janela | confirmada numericamente (desl20 ≤ 1,4%, spin30 e giro ≤ 0,8%); refutada para cm20 (≤ 4,8%) e $\ell=4$ (até 21% com os mesmos modos; os modos ausentes no CCE mudam desl40 em até 46%) | `exp33_validacao.txt` (b) |
| H10.2 | Os $m=0$ coorbitais do NRSur7dq4 não têm memória | confirmada numericamente | (g): (2,0) final ≤ 7,3e-5 contra 0,03–0,09 |
| H10.3 | $m=\pm1,\pm2$ codificam a inclinação de $J_\text{rad}$ | refutada como enunciada: codificam a orientação média do plano orbital ponderada por $dE$ ($e_Q$) | 4.5: $e_Q$ 0,89° contra $J_\text{rad}$ 3,25° (mediana) |
| H10.4 | O posto sobe com os spins no plano | confirmada numericamente: 7/7 módulo rotações, em 6 pontos; 5–6 acima de 1% de $\lvert v\rvert$ | `exp33_jacobiano.txt` |
| H10.5 | Direção mais fraca = azimute comum dos spins no plano | confirmada numericamente em J1, J2, J5; refutada como universal (J4: $\Delta\varphi$) | 4.2 |
| H10.6 | Parte secular dos $m\neq0$ = rotação do padrão $m=0$ pelo eixo coprecessante | confirmada numericamente (modelo/real 0,83–1,05 no final; 0,96–1,03 nas médias orbitais) | `exp33_secular.txt` (c) |
| H10.7 | Um observador: 4 números mensuráveis (+ giro), 3 invariantes por $\psi$, contra 10 parâmetros | confirmada numericamente (posto 4 em todo o céu) e por contagem | `exp35_observador.txt` |
| H10.8 | O NRSur7dq4 é suave em spin nulo | refutada (bico ~$\lvert\chi_B\rvert$) | (h) |
| H11.1 | Soma dos índices = 2 | confirmada matematicamente (Poincaré–Hopf) e numericamente (68/68 sistemas e testes, dois métodos) | 4.4, 4.5 |
| H11.2 | Só $m=0$: dois zeros +1 nos polos | confirmada matematicamente (axissimetria) e numericamente | 4.5 |
| H11.3 | Os zeros +1 se dividem em pares de +1/2, com meia abertura ~$\sqrt\epsilon$ | confirmada numericamente (AL1: 2,55° contra 2,43°) | 4.5 |
| H11.4 | $\ell=2$ puro: zeros = eixos ópticos, $\sin^2\alpha=(\lambda_2-\lambda_3)/(\lambda_1-\lambda_3)$, índice +1/2 | confirmada matematicamente [D] e numericamente (1,5e-6°) | 2, 4.4 |
| H11.5 | Com precessão os zeros seguem $J_\text{rad}$ (ou $\chi_f$) | refutada: seguem $e_Q$ (mediana 0,89°, máximo 4,1°); $J_\text{rad}$ 3,3° (máximo 19°), $\chi_f$ 6,0° (máximo 30°) | 4.5, `e34_angulos.png` |
| H11.6 | Abertura dos pares prevista pelo modelo uniaxial ($Q$) | inconclusiva (erro mediano 1,1°, correlação 0,85); pelos eixos ópticos de $A$: 0,38° | 4.5 |
