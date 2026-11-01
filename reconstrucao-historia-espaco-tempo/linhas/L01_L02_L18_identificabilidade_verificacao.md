# Verificação adversarial da linha D1 (L01, L02, L18): identificabilidade e fibras

Relatório verificado: `linhas/L01_L02_L18_identificabilidade.md`. Não editei esse relatório nem os scripts dele.

Os scripts desta verificação ficam em `codigo/revisao/ver_D1_*.py` e as saídas em `resultados/ver_D1_*.txt`. Tudo foi
rodado de `codigo/` com `OMP_NUM_THREADS=1` e no máximo 2 processos.

Sempre que possível usei um **caminho de cálculo independente** do `exp17_comum.memorias_varias` do autor:
- `observaveis.memorias_observaveis`, que gera uma onda por avaliação;
- passos de diferença finita diferentes dos do autor;
- `dt` reduzido à metade;
- pontos fora da grade do exp17.

Rótulos: [E] estabelecido, [D] derivado ou conferido aqui, [H] hipótese.

## Veredito geral

O núcleo numérico se reproduz por caminho independente, quase sempre a 4 ou 5 algarismos:
- os valores singulares em A;
- os loci de queda de posto;
- os pares do exp07;
- a dobra em $\iota$;
- as duas soluções da dobra global;
- as constantes do limite (2,2).

Há quatro problemas.

1. **O argumento de sinal contra a degenerescência $q$–$\chi_{\rm ef}$ (H1.7) não se sustenta.** O autovetor fraco
   da Fisher 4×4 da onda é dominado por $\chi_a$. Nas comparações corretas o sinal muda conforme o teste. A conclusão
   "a onda resolve a direção fraca da memória" continua válida por outro critério, que é robusto.
2. **O 4º valor singular intrínseco (~1e-3) depende do modelo.** Trocar NRHybSur3dq8_CCE por NRHybSur3dq8 muda
   $\sigma_4$ por um fator de até 5, e muda o jacobiano 15 a 70 vezes mais que $\sigma_4$. O "posto intrínseco 4" de T0
   não está certificado entre modelos. A *estrutura* que produz o valor pequeno (spin ≈ giroscópica) se mantém nos dois
   modelos.
3. **O "quase invariante" $M_f(1+\nu)$ é uma tautologia.** Ele é a razão observada CM/deslocamento (fixa por
   construção na fibra) dividida por uma forma angular que depende de $\iota$. A alegação de originalidade nº 5 deve
   ser retirada.
4. **O posto 4 no polo com todos os $m$ (H1.3 refutada) vale no modelo, mas é fraco na prática.** Ele se mantém
   mesmo sem a coluna $\phi'$, mas vem de valores singulares de 3e-5 a 3e-2, abaixo do erro do modelo.

## 1. Afirmações verificadas

### V1. Posto genérico e valores singulares em A (H1.1) — **confirmado**

Script: `ver_D1_jacobiano.py`, saída `resultados/ver_D1_jacobiano.txt`. Usa `observaveis` com passos $(\ln M,q,\chi)$
= (1e-3, 1e-2) e (2e-4, 2e-3); o exp17 usou 1e-4 e 4e-3.

| Caso em A ($\iota=50^\circ$, escala abs) | Relatório | Esta verificação |
|---|---|---|
| T0 livre | 4,353; 1,672; 0,6293; 0,1108 | 4,35339; 1,67197; 0,62931; 0,11084, iguais com os dois passos e com dt = 0,125 |
| T0 intrínseco | 3,094; 0,317; 0,0453; 9,50e-4 | 3,09359; 0,31661; 0,04530; 9,500e-4 (dt 0,25 e 0,125) |
| T0 com $\iota$ conhecido | 3,990; 0,806; 0,315; 0,0346 | 3,9903; 0,8057; 0,3154; 0,0346 (`ver_D1_polo.txt`) |
| T intrínseco | 3,110; 0,314; 0,0348; 0,0165 | 3,1103; 0,314; 0,0348; 0,0165 (`ver_D1_polo.txt`) |

Fora da grade do exp17, T0 livre tem posto 4 com folga, e $\|J(h_1)-J(h_2)\|_F\le8\times10^{-4}$:

| Ponto | $\sigma_4$ T0 livre | $\sigma_4$ intrínseco |
|---|---|---|
| $q$ = 2,5, $\chi$ = (−0,3; +0,5), M = 45, $\iota$ = 35° | 0,150 | 6,2e-3 |
| $q$ = 7,5, $\chi$ = (+0,75; −0,75), M = 100, $\iota$ = 65° | 0,198 | 2,3e-3 |

Ressalvas:
- O limiar $\tau=\|E\|_F$ é uma estimativa do erro de truncamento (diferença entre passos), não uma cota rigorosa. Não
  inclui o erro do modelo.
- O resultado para T0, T e O **livres** ($\sigma_{\min}\ge1{,}4\times10^{-3}$, mediana ~0,1) é robusto.
- A grade começa em $\iota=10^\circ$. Em $\iota=1^\circ$, T0 intrínseco já tem $\sigma_4=1{,}2\times10^{-6}<\tau=1{,}4\times10^{-6}$
  (`ver_D1_polo.txt`), ou seja, posto numérico 3. O enunciado "posto máximo para $\iota\le85^\circ$" vale para a
  grade, não para todo $\iota>0$ nos casos com $\iota$ e $D$ fixos.

### V2. Loci exatos em $\iota=\pi/2$ e $\iota=0$ (H1.2) — **confirmado** (analítico e numérico)

- Refiz os lemas. A reflexão no plano orbital troca o sinal das pseudoescalares (spin e giroscópica) para todo $\phi'$.
  Em $\iota=\pi/2$ as duas linhas só têm a coluna $\iota$, e o posto fica ≤ 3. No polo, com só $m=0$, as linhas $s=-2$
  são $O(\iota^2)$, e o posto fica ≤ 1.
- Numérico independente (`ver_D1_pontos.txt` (4)): $F(\pi-\iota)/F(\iota)=(1,-1,1,-1)$ a ≤ 4,8e-15, com todos os $m$,
  3 inclinações × 3 azimutes. O relatório citava 1e-10; o valor real é melhor.
- Em $\iota=0$, T0: $\sigma=(1{,}3788;0;0;0)$ (`ver_D1_polo.txt`).

### V3. Polo com todos os $m$: H1.3 "refutada" — **confirmado no modelo, com ressalva física**

Scripts: `ver_D1_polo.py` e `ver_D1_pontos.py` (3).

**Objeção testada.** No polo, girar $\phi'$ não move o observador; só gira a base de polarização
(${}_{-2}Y_{\ell2}(0,\phi)\propto e^{2i\phi}$). Um posto que dependesse da coluna $\phi'$ seria um artefato de base.

**Resultado.** Sem a coluna $\phi'$, T no polo continua com posto 4:

| Caso, $\iota=0$ | $\sigma$ |
|---|---|
| sem $\phi'$ | 1,379; 0,029; 0,0079; 0,0015 |
| sem $\phi'$ e sem $\iota$ | 1,379; 8,3e-3; 1,6e-3; 4,5e-5 |
| intrínseco | 0,80; 6,8e-3; 1,0e-3; 3,5e-5 ($\tau=4{,}6\times10^{-6}$) |

A objeção cai: os multipolos $m=2$ carregam informação intrínseca de fato.

**Robustez à definição dos $m\neq0$.** Os valores no polo relativos a T0 em 50° são deslocamento 2,6e-4, spin 2,2e-4 e
CM −5,2e-3 (com $\phi'=0$; dependem de $\phi'$). Eles mudam ≤ 1e-3 relativo com dt = 0,125 ou com 6 órbitas na média,
e 1–12% com janela abrupta.

**Ressalva.** Os valores singulares que dão o posto 4 no polo (3e-5 a 3e-2) ficam abaixo do erro do modelo:
- violação da simetria de troca: 1e-3 a 1e-2;
- diferença entre substitutos no jacobiano: ~2e-2 (V5).

Na prática o polo continua sendo um locus de quase-degenerescência. O relatório diz isso de passagem ("sinais ~1e-3").
O status deveria ser "refutada no modelo; fisicamente não certificada".

### V4. A direção quase nula intrínseca não é a degenerescência $q$–$\chi_{\rm ef}$ (H1.7) — **conclusão parcialmente confirmada; argumento de sinal refutado**

Script: `ver_D1_fisher.py`, saída `resultados/ver_D1_fisher.txt`. É uma Fisher própria (lalsimulation) com dois passos
(1e-4 e 1e-5) e dois df (1/32 e 1/64), passada para as coordenadas $y=(\ln M,\ln\eta,\chi_{\rm ef},\chi_a)$.

**O argumento de sinal não se sustenta.**
- O autovetor de menor autovalor da Fisher 4×4, usado no exp18, é quase todo $\chi_a$: em $y$, (−0,007; 0,016;
  0,027; −0,683) para XAS e aLIGO.
- O "$d\chi_{\rm ef}/d\ln\eta=+1{,}74$" é a razão de duas componentes pequenas de um vetor de $\chi_a$
  ($d\chi_a/d\ln\eta=-44$).
- A degenerescência $q$–$\chi_{\rm ef}$ da literatura é uma afirmação no plano $(\eta,\chi_{\rm ef})$. Nesse plano, o
  sinal muda conforme o teste:

| Teste (XAS) | aLIGO | ET | Sinal relativo à memória (−1,73) |
|---|---|---|---|
| Covariância marginal ($M$, $\chi_a$, $t_c$, $\phi_c$ marginalizados): eixo maior $d\chi_{\rm ef}/d\ln\eta$ | +1,44 | +1,46 | oposto |
| Covariância marginal: correlação | +0,54 | +0,32 | — |
| Fisher condicional com $\chi_a$ fixo: direção fraca | −0,18 | −0,26 | **mesmo**, mas 7–10 vezes menor |

**XHM é numericamente instável.** Trocar o passo de 1e-5 para 1e-4 muda:
- a razão do autovetor 4×4 de +3,04 para +5,77 (aLIGO);
- a inclinação marginal de +9,0 para +78,5;
- a correlação de +0,25 para +0,02.

Os números de XHM do exp18 (+3,03; $R$ = 272) dependem do passo.

**O que é robusto.** O 1σ da onda ao longo de $v_{\rm mem}$ vale 1,20e-2 (aLIGO) e 3,82e-4 (ET) nos dois modelos e
nos dois passos. Ao longo do autovetor fraco da onda vale 1,1 (XAS) e 0,2 (XHM). A onda mede bem a direção fraca da
memória. Isso basta para refutar H1.7 como identificação.

Duas observações sobre as métricas do relatório:
- $R=v^TGv/\lambda_{\min}\ge1$ vale por definição.
- O $\cos$ entre vetores depende das coordenadas.

**Correção sugerida:** retirar o argumento "sinal oposto" e manter o argumento do 1σ ao longo de $v_{\rm mem}$.

### V5. Identidade do limite (2,2) e origem da direção quase nula (H1.7b) — **identidade confirmada analiticamente; atribuição confirmada qualitativamente; tamanho de $\sigma_4$ dependente do modelo**

Script: `ver_D1_reducao22.py`, saída `resultados/ver_D1_reducao22.txt`.

**Derivação independente.**
- Com só $(2,\pm2)$, as matrizes de Gram têm, em $m=0$, só $B_{22,22}=E$ e ${\rm Im}A_{22,22}=-H$. Os termos cruzados
  têm $m=\pm4$.
- O código usa só $A-A^\dagger$ (a etapa 3 mostrou que tudo depende só de $B$ e $A-A^\dagger$), e por isso
  ${\rm Re}(\bar h\dot h)=\tfrac12d|h|^2/du$ sai. Isso explica a CM nula = 0 mesmo com $|h_{22}|^2\neq0$ nas pontas.
- Constantes calculadas à mão:
  - $C_E=\sqrt{30}/(42\sqrt\pi)=0{,}0735760$;
  - $G_{10}/H=\tfrac14\cdot\tfrac54\sqrt{3/4\pi}\cdot\tfrac{16}{15}=0{,}162868$;
  - $\tfrac14{\rm Hel}_{30}/H=0{,}0266555$. Com o termo de spin $-\mathfrak D_3\,{\rm pot}_{30}=-0{,}0799664\,H$ (de
    $S_{30}/H=-C_J$), dá $G_{30}/H=-0{,}0533109$;
  - $J_{40}/J_{20}=\sqrt3/180$, refeito com integrais de Legendre: 0,009623.
- Todas coincidem com o relatório.

**Sinais sintéticos.** Usei $h_{22}(t)$ aleatórios e suaves, sem substituto e com $|h|^2$ diferente nas pontas. As
razões saem universais a ~1e-5 (diferença de derivada numérica), e a CM nula fica ≤ 1,3e-15.
- Achado extra: $S_{30}/G_{10}=-0{,}179284$ continua igual mesmo com $h_{2,-2}\neq\bar h_{22}$. A proporcionalidade
  spin–giroscópica vem só de $\ell=2$; não precisa da simetria de reflexão.

**Atribuição.** O vetor singular **esquerdo** da direção quase nula intrínseca é
$u\approx(0{,}09;\,0{,}68;\,0{,}06;\,-0{,}72)$ em (desl, spin, CM, giro), ou seja, spin − giroscópica.
- Vale em A e nos pontos fora da grade.
- Vale também com NRHybSur3dq8.
- O ângulo entre as linhas spin e giro do jacobiano intrínseco é só 0,027–0,046 rad.
- Isso confirma, por um caminho que o relatório não usou, que o valor singular pequeno vem da quase proporcionalidade
  spin ∝ giroscópica.

**Dependência do modelo** (`ver_D1_modelo.py`, saída `resultados/ver_D1_modelo.txt`):

| Ponto | $\sigma_4$ intrínseco, CCE | $\sigma_4$ intrínseco, NRHybSur3dq8 | $\|J_{\rm semCCE}-J_{\rm CCE}\|_F$ |
|---|---|---|---|
| A | 9,5e-4 | 1,9e-4 | 1,4e-2 |
| $q=2$, $\chi=0$ | 1,27e-3 | 1,77e-3 | 2,2e-2 |
| $q=3$, $\chi=(0{,}6;0)$ | 8,8e-4 | 1,54e-3 | 2,6e-2 |

- Pela desigualdade de Weyl aplicada entre modelos, a diferença entre os jacobianos excede $\sigma_4$ em 15 a 70 vezes.
- O "posto intrínseco 4" de T0 não está certificado como propriedade física.
- A direção $v$ concorda entre modelos a 0,5°–7°.
- O relatório admite isso em geral (§6). O status "confirmada matematicamente e numericamente" de H1.7b deve se
  restringir à identidade (2,2) e à estrutura spin ≈ giro, sem o valor de $\sigma_4$.

**Originalidade.** Faye & Seraj, CQG 42, 035005 (2025) (arXiv:2409.02624; resumo lido pela API do arXiv) decompõem a
memória giroscópica em memória de spin mais fluxo de helicidade. No limite (2,2) os dois termos são ∝ $H$, então a
proporcionalidade é quase imediata a partir da literatura. "Implícita", como diz o relatório, é justo. O que é daqui é
o uso como degenerescência de parâmetros.

### V6. Pares do exp07 persistem (H1.8) e dobra global (H2.1) — **confirmados; o piso numérico é ~1e-7, não 1e-11**

Script: `ver_D1_pontos.py` (1). As soluções foram tiradas de `exp17_pares.json` e `exp17_fibra.json` e reavaliadas com
`observaveis` independente. Diferença $F_B/F_A-1$:

| Solução | dt = 0,25 | dt = 0,125 |
|---|---|---|
| par (2, 0) | ≤ 4,8e-11 | ≤ 2,0e-8 |
| par (2, +0,5) | ≤ 1,7e-11 | ≤ 2,6e-8 |
| dobra (3, −0,2), $\chi_1$ = 0,675 | ≤ 2,9e-11 | ≤ 1,6e-7 |
| dobra (3, −0,2), $\chi_1$ = 0,741 | ≤ 2,0e-11 | ≤ 7,1e-8 |
| extremo (3, +0,8), $M$ = 87 | ≤ 2,6e-11 | ≤ 6,5e-8 |

- As duas soluções da dobra são reais. Em (3, +0,8), $M_fM=84{,}3\,M_\odot$ contra 61,7 em A.
- Os resíduos de 1e-11 do relatório são a tolerância do Newton com o dt fixo. O piso de discretização (troca de dt) é
  ~1e-7. O relatório chama 1e-11 a 1e-10 de "piso da infraestrutura", o que não é exato; a conclusão não muda.
- A persistência dos pares não é um teste forte. Com fibra regular de dimensão 2 em T0, qualquer $(q_B,\chi_{2B})$
  dentro da projeção da fibra tem solução. "Os pares persistem" é consequência do teorema do posto, não confirmação
  independente.

### V7. Dobra do problema quadrado em $\iota\approx37^\circ$ (H1.6b) — **confirmado**

Script: `ver_D1_dobra_iota.py`, saída `resultados/ver_D1_dobra_iota.txt`. Usa uma grade fina de $\iota$ (passo 0,25°)
e os dois passos.

| Ponto | Troca de sinal de det | $\sigma_{\min}$ na troca |
|---|---|---|
| A | entre 37,25° e 37,50° (relatório: 37,0–37,5°) | 5,8e-7 |
| $q=4$, $\chi$ = (0,5; 0,5), M = 80 | entre 67,75° e 68,00° | 1,2e-6 |
| $q=2{,}5$, $\chi$ = (−0,3; +0,5), M = 45 | nenhuma em 20–85° | — |

As dobras são genéricas no sentido de codimensão 1, mas o local exato está ~1e-6 abaixo de qualquer erro de modelo.

### V8. Curva de T com $\iota$ e $D$ conhecidos (H1.6) — **confirmada, com robustez quantificada**

Script: `ver_D1_pontos.py` (2). As pontas da curva ($\phi'_B$ = −0,982 e +0,589) foram avaliadas em quatro definições
dos $m\neq0$:

| Definição dos $m\neq0$ | Resíduo |
|---|---|
| a do relatório | ≤ 3,5e-11 |
| dt = 0,125 | ≤ 8,3e-8 |
| média de 6 órbitas | ≤ 1,7e-7 |
| janela abrupta | ≤ 1,8e-4 |

- A curva existe por contagem de dimensão (4 equações, 5 incógnitas). Ela só se desloca ~1e-4 com a definição.
- Detalhe de apresentação (`exp17_fibra_iD.json`): $q$ não é monótono ao longo da curva. O máximo 1,208 fica em
  $\phi'=-0{,}196$ e o mínimo 1,018 em +0,589. A tabela "De −0,98 a +0,59 / $q$ de 1,018 a 1,208" sugere pontas
  pareadas que não existem.

### V9. Quase invariante $M_f(1+\nu)$ (H2.2 e originalidade nº 5) — **refutado como resultado: é tautológico**

Teste com os dados do autor (`resultados/exp18_invariantes.json`, cálculo inline):
- $M\cdot({\rm CM}/{\rm desl})_{\rm adim}$, que é uma razão de observáveis, varia **6,3e-11** ao longo das 76
  soluções. Fica fixa por construção.
- Pela definição do código, $1+\nu={\rm CM}/{\rm ordinária}$, com ordinária $=-\tfrac32M_f\sum_\ell J_\ell Y_\ell/\mathfrak D_\ell$.
  Daí $M_f(1+\nu)M=M\,({\rm CM}/{\rm desl})\cdot c(\iota)$, onde $c$ só depende da mistura $\ell=2/\ell=4$ (≈ −2,0).
- A razão $M_f(1+\nu)/(M\,r_{\rm cm})$ varia **3,04%** e tem correlação **0,88** com $\iota$. Isso é exatamente a
  "variação de 3%" do relatório.
- $M_f(1+\nu)$ não é uma grandeza conservada pela fibra. É o observável CM/deslocamento reescrito, corrigido por uma
  forma angular.
- A alegação "o que a fibra preserva melhor é $M_f(1+\nu)$", e a nº 5 da §7, devem sair ou ser reescritas como
  "a razão CM/desl fixa $M_f(1+\nu)$ a menos da forma angular, ~3% nesta fibra".

## 2. Afirmações não verificadas aqui

- Mapa completo da fibra global (75 de 117 pontos, conexidade). Só conferi as soluções de (3, −0,2) e (3, +0,8).
- *Matches* aLIGO e ET dos pares.
- Números de L18 além de $J_{40}/J_{20}$ no limite (2,2) e $G_{30}/G_{10}=-0{,}327$: $N_{\rm ef}$, $\ell\ge6$. O próprio
  relatório diz que $\ell\ge6$ não converge.
- Extensões com excentricidade e precessão (+2 e +4). Dependem da hipótese de que o mapa seja $C^1$ em
  $(e_0\cos\ell_0,e_0\sin\ell_0)$. A revisão anterior (item 14) mostrou que a saída do SEOBNRv5EHM não é suave em
  ~1e-5, o que deixa essa hipótese sem teste.

## 3. Literatura e originalidade (busca curta)

Busca pela API do arXiv:
- "gravitational wave memory" AND identifiability;
- "spin memory" AND degeneracy;
- "gyroscopic memory";
- memory AND Fisher AND center-of-mass;
- "nonlinear memory" AND "parameter estimation" AND "mass ratio";
- memory AND Jacobian AND gravitational;
- "orphan memory".

Não achei análise de posto ou de fibras do mapa parâmetros → memórias integradas. Achei:
- arXiv:2409.02624 (Faye & Seraj): decomposição da giroscópica (V5);
- arXiv:2607.04909 (Rosselló-Sastre, Husa et al.): busca do modo (2,0) em GWTC-4/5, sem identificabilidade;
- arXiv:1702.01759 (McNeill et al.), já citado.

A busca foi curta (títulos e resumos). Sobre as alegações de originalidade da §7:
- **1** (teorema de posto e loci), **2** (curva com contraparte) e **4** (mapa da fibra com dobra): plausíveis como
  novas.
- **3** (identidade (2,2)): implícita em Faye & Seraj 2025 e nas fórmulas PN; o enunciado como degenerescência é daqui.
- **5** ($M_f(1+\nu)$): retirar (V9).

## 4. Tabela de hipóteses revista

| Id | Status no relatório | Status após verificação | Motivo |
|---|---|---|---|
| H1.1 | confirmada numericamente | **confirmada** (caminho independente; fora da grade) | V1 |
| H1.2 | confirmada mat. e num. | **confirmada** (reflexão a 5e-15) | V2 |
| H1.3 | refutada | **refutada no modelo; fisicamente não certificada** (σ 3e-5 a 3e-2 abaixo do erro do modelo) | V3 |
| H1.4 | confirmada mat. | confirmada mat. (lema refeito); não testada de novo numericamente | — |
| H1.6 | confirmada | **confirmada**; T0 com $\iota$, $D$ é localmente identificável só no modelo ($\sigma_4/\sigma_1\sim3\times10^{-4}$, abaixo da diferença entre modelos) | V5, V8 |
| H1.6b | confirmada numericamente | **confirmada** (37,25–37,50°; outra dobra em 67,9° num 2º ponto) | V7 |
| H1.7 | refutada | **refutada por outro argumento** (1σ ao longo de $v_{\rm mem}$); o argumento de sinal é inválido e o XHM é instável no passo | V4 |
| H1.7b | confirmada mat. e num. | **identidade (2,2): confirmada analiticamente; estrutura spin ≈ giro: confirmada em 2 modelos; valor de $\sigma_4$: dependente do modelo (fator 5)** | V5 |
| H1.8 | confirmada numericamente | **confirmada**, com piso ~1e-7 (dt); consequência do teorema do posto, não teste independente | V6 |
| H2.1 | refutada em parte | **dobra confirmada** (duas soluções em (3, −0,2) reproduzidas) | V6 |
| H2.2 / $M_f(1+\nu)$ | refutada; quase invariante a 3% | **o quase invariante é tautológico** (razão CM/desl reescrita) | V9 |

## 5. Arquivos desta verificação

| Script | Saída |
|---|---|
| `codigo/revisao/ver_D1_jacobiano.py` | `resultados/ver_D1_jacobiano.txt` |
| `codigo/revisao/ver_D1_fisher.py` | `resultados/ver_D1_fisher.txt` |
| `codigo/revisao/ver_D1_pontos.py` | `resultados/ver_D1_pontos.txt` |
| `codigo/revisao/ver_D1_polo.py` | `resultados/ver_D1_polo.txt` |
| `codigo/revisao/ver_D1_dobra_iota.py` | `resultados/ver_D1_dobra_iota.txt` |
| `codigo/revisao/ver_D1_reducao22.py` | `resultados/ver_D1_reducao22.txt` |
| `codigo/revisao/ver_D1_modelo.py` | `resultados/ver_D1_modelo.txt` |
