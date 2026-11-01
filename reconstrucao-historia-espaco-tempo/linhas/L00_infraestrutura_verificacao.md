# L00 — Verificação da infraestrutura `codigo/observaveis.py` (verificador de D0)

Objeto: `codigo/observaveis.py`, `codigo/testes_observaveis.py` e o relatório `linhas/L00_infraestrutura.md` do
agente D0. Sistema de referência: o "sistema A" do exp07 ($M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$,
$D=400$ Mpc, $\iota=50^\circ$, janela desde 10 Hz, NRHybSur3dq8_CCE).

**Veredito curto.** O módulo pode ser usado pelas linhas. Os seis pontos pedidos conferem com verificações
independentes: pesos de quadratura, suavidade, parte ordinária da CM, `todos_m`, `comparar2` e série nula com a
SNR de A. Achei um erro claro, só de semântica: o `atraso` de `comparar2` não é "relativo ao alinhamento pelos
picos". Corrigi a docstring e acrescentei `atraso_rotulos`; nenhum número mudou. Achei também quatro limitações
que o L00 não registra e que importam para as linhas (seção 6):

1. o ruído do substituto nas direções $q$ e $\chi$ (~3e-10);
2. a oscilação em $M$ das memórias com todos os $m$ num $\phi$ fixo;
3. o piso de `comparar2` quando a onda começa logo abaixo de $f_\text{min}$;
4. o erro O(dt²) da série nula em instantes intermediários.

Scripts novos (prefixo único `verif_L00_`, na pasta de revisão): `codigo/revisao/verif_L00_quadratura.py`,
`verif_L00_suavidade.py`, `verif_L00_ruido.py`, `verif_L00_cm_mnao0.py`, `verif_L00_match.py`,
`verif_L00_serie_nula.py` e `verif_L00_extra.py`. As saídas estão em `resultados/revisao/verif_L00_*.txt`. Todos
os números abaixo foram copiados dessas saídas ou de `resultados/testes_observaveis.txt`.

---

## 1. Pergunta e hipóteses

**Pergunta.** As afirmações do D0 sobre `observaveis.py` resistem a testes independentes do código dele? E o
módulo tem erros que comprometam as sete linhas que vão usá-lo?

Hipóteses verificadas (status na seção 10):

- **V1** `pesos_janela` integra de $t_i$ (fora da grade) ao fim com erro de trapézio, exato para funções lineares
  e contínuo em $t_i$.
- **V2** As memórias de janela são suaves em $M$: a escada de ~3e-6 sumiu.
- **V3** Também são suaves em $q$ e $\chi$. Pergunta minha, que o D0 não testou.
- **V4** O resultado não depende do início auxiliar `FRAC_INICIO`.
- **V5** A correção de fase em $t_i$ não sofre da ambiguidade de $\pi$.
- **V6** A CM usa o mesmo deslocamento nas partes nula e ordinária, e vai a zero numa janela curta.
- **V7** `todos_m=True` reproduz `codigo/revisao/rev_R1_m_nao_nulo.py`.
- **V8** `comparar2` dá o *match* certo.
- **V9** O `atraso` de `comparar2` é "relativo ao alinhamento pelos picos".
- **V10** A série nula termina no deslocamento de janela e reproduz a SNR de A (0,47 / 0,89 / 8,6 / 34).
- **V11** A diferença contra `binarias` vem inteiramente do início da janela (teste (c) do D0).
- **V12** "Os passos podem agora ser tão pequenos quanto ~1e-6" (seção 9 do L00).

## 2. Fundamentação e equações

**Pesos.** Para $t_{k-1}<t_i\le t_k$, com $a=(t_i-t_{k-1})/dt$ e $L=t_k-t_i$, os pesos do D0 equivalem a
somar o trapézio de $t_k$ ao fim com o subintervalo $[t_i,t_k]$, este com $f(t_i)$ interpolado linearmente.

Para $f=(t-c)^2$ o erro tem forma fechada [D]:
$$E=\tfrac{dt^2}{6}(T-t_k)+\tfrac{L^3}{6}+\tfrac{L}{2}\,a(1-a)\,dt^2 .$$
Os três termos são o trapézio composto, o trapézio parcial e a interpolação linear de um termo quadrático.
Derivando em $t_i$: $dI/dt_i=-f_\text{lin}(t_i)$, contínua; $I$ é $C^1$, com saltos de $I''$ nos nós [D].

**Série nula independente.** Usei a normalização de Favata 2009 (eq. 3.3, de memória; conferida abaixo pela
coincidência numérica com a fórmula de Mitman et al. 2020 em `memorias.py`):
$$\frac{d h^\text{mem}_{L0}}{du}=\sqrt{\tfrac{(L-2)!}{(L+2)!}}\;E_{L0}(u),\qquad
E_{L0}=\sum_{a,b}\dot h_a\,\overline{\dot h_b}\int{}_{-2}Y_a\,\overline{{}_{-2}Y_b}\,Y_{L0}\,d\Omega .$$
A integral angular vem de coeficientes de Gaunt (símbolos 3j do sympy):
$$(-1)^m\sqrt{\tfrac{(2l_a+1)(2l_b+1)(2L+1)}{4\pi}}\begin{pmatrix}l_a&l_b&L\\m&-m&0\end{pmatrix}\begin{pmatrix}l_a&l_b&L\\2&-2&0\end{pmatrix}.$$
O integral no tempo usa a antiderivada de uma spline cúbica, não os pesos. Esse caminho não passa pela grade de
`CalculadoraMemoria` nem por `pesos_janela`.

**Atraso em `produto2`.** O espectro cruzado $\sum_f A\bar B\,e^{2\pi i f\tau}/S$ maximiza
$(a\,|\,b(\cdot-\tau))$, isto é, $a(t)\approx b(t-\tau)$. O tempo é contado da primeira amostra de cada série
[D]. Em `preparar`, subtrair o instante do pico não muda as amostras: elas ficam em $t[0]+j/f_s$. Logo
$\tau$ não depende do pico. Se $B(t)=A(t-\delta)$ nos rótulos dados, então
$\delta=(t^B_\text{início}-t^A_\text{início})-\tau$.

**Oscilação em $M$ dos $m\neq0$.** Com $\phi$ medido a partir da fase orbital em $t_i$, o termo de borda final
(fusão) de um multipolo de ordem $m$ gira como $e^{-im(\Phi_\text{fusão}-\Phi_i)}$. Mudar $M$ desloca $t_i$ em
$dt_i/de$ (com $e=\Delta M/M$). Isso gira a borda final de $m\,\omega_\text{orb}(t_i)\,dt_i/de$ por unidade de
$e$ [D].

## 3. Experimentos

| Script | O que faz | Custo |
|---|---|---|
| `testes_observaveis.py` (do D0) | rodado três vezes: original, depois da correção, versão final | ~2,2 min cada |
| `verif_L00_quadratura.py` | funções conhecidas com $t_i$ fora da grade; fórmula fechada do erro; continuidade em $t_i$; `gram_pesos`; rede deslocada | 4 s |
| `verif_L00_suavidade.py` | ver abaixo | 3,5 min |
| `verif_L00_ruido.py` | ruído em $q$ por modo; `FRAC_INICIO` com $f_0$ de 0,003 a 0,015; oscilação em $M$ ($e$ de 0 a 0,03) | ~3 min |
| `verif_L00_cm_mnao0.py` | identidade da CM multipolo a multipolo; janelas curtas (10–400 M); cópia exata de `memorias_todas`/`observador` do rev_R1; rotação azimutal; grades de 12, 24 e 720 valores de $\phi$ | 36 s |
| `verif_L00_match.py` | ver abaixo | ~2 min |
| `verif_L00_serie_nula.py` | série por Gaunt e spline em dt = 0,25 e 0,125; SNR por outro tratamento (8192 Hz, interpolação linear, 2 s mantidos e janela de Planck de 16 s, sem taper) | 72 s |
| `verif_L00_extra.py` | teste (c) do D0 com $t_i:=t_{0b}-dt/2$; amostra final do nível C | 20 s |

`verif_L00_suavidade.py`:
- $M$: 81 valores em $\Delta M/M\in[0,4\text{e-}5]$; $t_i$ atravessa 7 intervalos da rede;
- $q$ e $\chi_1$: 41 valores, passo 2e-6;
- `FRAC_INICIO` de 0,80 a 0,97 em $M$ = 30, 65 e 120;
- $|\delta\phi|$ em 105 combinações: $M$ de 20 a 150, $q$ de 1 a 8, três pares de spins;
- jacobianos com passos $h$, $h/2$ e $h/4$.

`verif_L00_match.py`:
- (a) A contra A noutra rede, começando 0,2 s depois e com rótulos deslocados de 1,2345678e-3 s; ondas desde
  0,9 $f_0$ e desde 0,7 $f_0$;
- (b) senos-gaussianos com transformada analítica: *match* exato por integração densa ($df$ = 1/64 Hz) e varredura
  global do atraso;
- (c) degraus $\tanh$ (tipo memória), com transformada $-i\pi\tau(D/2)/\sinh(\pi^2\tau f)$;
- (d) A contra $q=1{,}19$ desde $t_i$, desde 0,9 $f_0$ e desde 0,7 $f_0$.

Ambiente: um ou dois processos Python, `OMP_NUM_THREADS=1`, saídas filtradas com `grep -v -i "msun\|warn\|Loaded"`.

## 4. Resultados

### 4.0 Testes do D0

A saída é idêntica a `resultados/testes_observaveis.txt` nas três execuções; só as linhas de tempo mudam. A
figura `figuras/e00_escada_suavidade.png` foi regravada e é idêntica byte a byte.

### 4.1 Pesos de quadratura — `verif_L00_quadratura.txt` [V1: confirmada matematicamente e numericamente]

- **Funções lineares.** $f=1$ e $f=t$ com 200 valores aleatórios de $t_i$: erro relativo máximo 0 e 2,2e-16.
- **Fórmula fechada.** Para $f=(t-c)^2$, |erro medido − fórmula fechada| / integral = 2,0e-16 (erro típico
  1,2e-10). Os pesos são exatamente o esquema descrito.
- **Ordem.** $\cos(0{,}02t+0{,}3)$: erros −8,33e-6, −2,08e-6 e −5,21e-7 para dt = 0,5, 0,25 e 0,125 (razões
  4,00 e 4,00). Ordem 2 também para $\cos(0{,}5t)$ e para uma gaussiana.
- **Continuidade no nó.** $I(\text{nó}\mp10^{-9})-I(\text{nó})=\mp8{,}451\text{e-}10$, contra $f(\text{nó})\cdot10^{-9}=8{,}447\text{e-}10$.
- **Derivada.** $dI/dt_i=+0{,}8232626$ contra $-f_\text{lin}(t_i)=+0{,}8232623$ (resto de arredondamento da
  diferença finita).
- **Gram e rede deslocada.** `gram_pesos` coincide com a soma explícita (2,0e-15). Na rede deslocada
  (`t_desloc` 0,37), $\sum w=T-t_i$ exatamente, também com $t_i$ a ±1e-12 de um nó.

### 4.2 Suavidade — `verif_L00_suavidade.txt`, `verif_L00_ruido.txt`

**[V2] Em $M$: confirmada numericamente.** Varredura de $e$ de 0 a 4e-5 (81 valores; $t_i$ anda 1,804 M):

| Caso | Resíduo do ajuste cúbico |
|---|---|
| nível A, $m=0$ | ≤ 6,9e-12 |
| nível C, $m=0$ | ≤ 7,0e-12 |
| todos os $m$, $\phi=0{,}8$ | ≤ 8,6e-11 |
| `binarias`, mesma varredura | 1,3e-6 (spin), 1,4e-6 (giroscópica) |

**[V3] Em $q$ e $\chi$: o resíduo é ~1000 vezes maior que em $M$.**
- Em $q$ (passo 2e-6) o resíduo chega a 2,9e-10 (deslocamento). Em $\chi_1$, a 3,5e-10. As segundas diferenças
  vão até 9,1e-10.
- A origem é o próprio substituto, não `observaveis`:
  - a energia de janela de cada modo isolado tem resíduo de 2,2e-10 a 1,4e-9, tanto antes quanto depois do pico;
  - $|h_{22}|$ num instante fixo é suave (6e-13);
  - $t_i$ tem resíduo de 1,5e-6 M.
- Não há escada. É um piso de ruído na evolução de fase do substituto em função de $q$ e $\chi$.

**[V4] `FRAC_INICIO`: confirmada para FRAC ≤ 0,9.**
- Contra FRAC = 0,6, os multipolos (todos os $m$) diferem ≤ 6e-11 com FRAC = 0,8 ou 0,9, para $f_0$ de 0,0032 a
  0,0148 ($M$ de 65 a 300; $f_\text{ini}$ de 10 a 45 Hz).
- Com FRAC = 0,95 a diferença chega a 3e-9 ($f_0$ = 0,0064). Com 0,97 e $M=120$, chega a 7e-8 nas memórias e a
  2e-4 M em $t_i$.
- Causa: o gwsurrogate trunca a grade esparsa cinco nós antes de `f_low` (`_search_omega(...) - 5` em
  `gwsurrogate/new/surrogate.py`) e depois interpola. O padrão 0,9 é seguro; valores acima de ~0,93 não são.

**[V5] Fase: confirmada.**
- No código do gwsurrogate, com `times` a fase é zerada no ponto da rede dada cuja $\omega_{22}$ (diferença para
  frente) está mais perto de $2\pi f_\text{ref}$.
- Em 105 combinações, o máximo de $|\delta\phi|$ antes da correção é 1,114e-2 rad, contra $\omega_{22}dt$ =
  1,161e-2 em $M=150$. Nunca fica perto de $\pi$, então não há troca de sinal dos $m$ ímpares.
- A fase residual em $t_i$ depois da correção é ≤ 4,6e-12 rad.

**[V12] Jacobianos: parcial.** Com passo $h=10^{-3}$, a razão entre diferenças sucessivas é ~4 (de 3,3 a 4,3)
para as quatro memórias em $q$, $\chi_1$, $\chi_2$ e $M$, como deve ser para diferenças centrais. Erro relativo
$|D(h/2)-D(h/4)|/|D|$:

| Direção | Erro |
|---|---|
| $\chi_1$, $\chi_2$ | 8e-6 a 6e-5 |
| $q$ | 2,5e-5 (spin) a 9,5e-4 (deslocamento) |
| $M$, todos os $m$, $\phi$ fixo, $h=10^{-3}$ relativo | 5,1e-3 a 2,5e-2 |

O caso de $M$ é físico: as memórias com todos os $m$ num $\phi$ fixo oscilam em $M$.
- $dt_i/de=4{,}49\text{e}4$ M, então $\omega_\text{orb}\,dt_i/de=452$ rad e o período previsto para $|m|=1$ é
  $\Delta e=0{,}0139$.
- Medido para spin e giroscópica: 0,0146.
- Medido para deslocamento e CM: 0,0073, com $|m|=2$ dominante.
- Amplitude: spin [−1,36e-2, +1,38e-2]; CM [−5,9e-3, +5,6e-3].

A frase do L00 ("passos ~1e-6 sem o piso") vale em $M$ para os $m=0$. Em $q$ e $\chi$ o piso é ~3e-10, e com
passo 1e-6 o erro da derivada fica em ~3e-4.

### 4.3 Parte ordinária da CM — `verif_L00_cm_mnao0.txt` [V6: confirmada]

- **Identidade.** Recalculei a parte nula com `memorias_gram` e os pesos, sem passar por
  `memorias_observaveis`. Multipolo a multipolo ($\ell\le8$, todos os $m$):
  $\text{cm}=\text{nula}-\tfrac32M_f\,\Delta J/\mathfrak D_\ell$, com resto relativo de 8,4e-24 (A, `'janela'`),
  2,6e-16 (A, `'total'`) e 2,7e-22 / 2,4e-22 (C). Em todos os casos o $\Delta J$ usado é o deslocamento devolvido
  pela mesma chamada.
- **Composição de cm20 em A.** −0,049191 com `'janela'`: nula 12,3%, ordinária 87,7%. Com `'total'`, −0,054074.
- **No observador.** CM = −0,011218, dos quais 87,4% vêm da parte ordinária. Para comparação,
  $-(M_f/2)\Delta h_+=-0{,}010046$ (item 4 da revisão).
- **Janelas curtas** ($q=1$, $\chi=0$). Com `'janela'`, cm20 é linear na duração: cm20/duração ≈ −7,47e-8 a
  −7,58e-8 por M, de 10 a 400 M. Com `'total'`, cm20 tende a $-(M_f/2)h_{20}^\text{Favata}=-5{,}1555\text{e-}3$.
- **Convenção alternativa** $M_f\Phi_f-M_i\Phi_i$, que exige o deslocamento total em $t_i$ (inobservável): muda
  cm20 de A em −0,47%. É escolha de convenção, não erro; o L00 já a menciona.

### 4.4 `todos_m` contra rev_R1 — `verif_L00_cm_mnao0.txt` [V7: confirmada]

- **Cópia do rev_R1.** A cópia exata de `memorias_todas` e `observador` reproduz `rev_R1_m_nao_nulo.txt` na
  grade de 12 valores de $\phi$: desl [−1,14e-3, +1,79e-3], spin ±1,34e-2, cm [−4,86e-3, +4,58e-3],
  giro [−5,29e-3, +5,12e-3].
- **Comparação multipolo a multipolo.** Mesmas fórmulas (derivada de 4ª ordem, E_lig 1PN, `desl='total'`).
  As duas convenções de fase diferem por uma rotação azimutal única, estimada em $\alpha=-5{,}74\text{e-}4$ rad:
  - $m=0$: diferem 2,6e-7 a 2,2e-6 (a escada de `binarias`);
  - $m\neq0$, depois da rotação: diferem 1,2e-5 (deslocamento), 9,3e-6 (spin), 7,0e-6 (giroscópica) e 3,9e-4
    (CM) do maior $|m\neq0|$; sem a rotação, 5,6e-4 a 1,5e-3.
- **Faixas em $\phi$.** Na mesma grade, rev_R1 e `observaveis` coincidem em 3–4 algarismos. O mínimo do
  deslocamento difere entre os dois relatórios (−1,14e-3 no rev_R1, −1,23e-3 no D0) só porque as grades têm 12 e
  24 valores de $\phi$. Na grade de 720 valores:
  - `'total'`: spin [−1,351e-2, +1,355e-2], desl [−1,234e-3, +1,798e-3];
  - padrão `'janela'`: desl [−1,373e-3, +1,999e-3], cm [−5,405e-3, +5,036e-3], giro [−5,323e-3, +5,136e-3].

  A grade de 24 valores subestima os extremos em ~1%.
- `no_observador_completo` coincide com `observador` do rev_R1 (diferença 0,0).

### 4.5 `comparar2` — `verif_L00_match.txt` [V8: confirmada, com piso; V9: refutada e corrigida]

**(a) A contra A**, outra rede, começando 0,2 s depois, rótulos + 1,2345678e-3 s:

| Variante | aLIGO | CE |
|---|---|---|
| ondas desde 0,9 $f_0$ (taper de 0,5 s em ~9 Hz) | 4,61e-6 | 9,33e-5 |
| ondas desde 0,7 $f_0$ | 2,77e-8 | 3,48e-7 |
| sem taper e sem rampa | 6,87e-4 | — |
| `deteccao.comparar` | 7,14e-4 | — |

Valores de 1 − match. O `atraso` devolvido é +1,999676072e-1 s, contra +1,999676058e-1 previsto pela convenção
das primeiras amostras. Não é o atraso entre picos, como dizia a docstring. Depois da correção,
`atraso_rotulos` dá +1,234566440e-3 s, contra 1,2345678e-3 verdadeiro.

**(b) Senos-gaussianos com transformada analítica.**
- O *match* coincide com o exato em +2,1e-9, −5,6e-16 e +1,6e-7. A SNR, em ≤ 2,4e-7. O $\tau$, em 4e-10 s ou
  menos.
- Para comparação, `deteccao.comparar` erra 3,5e-6, −1,4e-6 e −8,8e-7.
- O terceiro caso (match 0,2984) exigiu varredura global do atraso no valor exato. Minha primeira varredura,
  de ±5 ms, não achava o máximo; o erro era meu, não de `comparar2`.

**(c) Degraus tipo memória.**
- `snr2` coincide com a mesma soma discreta da transformada analítica em 1e-10 a 2,7e-8.
- Contra a integral contínua, difere +9,7e-7 a +1,5e-4. É o efeito de borda da soma de Riemann em $f_\text{min}$
  (o bin de 10 Hz entra com peso $df$ inteiro), maior em CE.
- Sem a rampa a SNR sai errada por fatores de 1,6 a 6,9. Com ela, o *match* coincide com o exato em ≤ 8,6e-7.

**(d) A contra $q=1{,}19$.** Referência limpa, com as duas ondas desde 0,7 $f_0$: 1 − match = 4,6712e-4 (aLIGO)
e 6,8660e-4 (CE).

| Variante | aLIGO | CE |
|---|---|---|
| começando em $t_i$ (teste do D0) | 4,6608e-4 (−0,2%) | 6,5838e-4 (−4,1%) |
| em $t_i$ com taper de 2 s | 4,5672e-4 (−2,2%) | 5,8735e-4 (−14,5%) |

Uma onda que começa exatamente em $f_\text{min}$ tem o *match* enviesado para baixo pelo taper dentro da banda.

### 4.6 Série nula e SNR de A — `verif_L00_serie_nula.txt` [V10: confirmada]

- **Gaunt.** A fórmula, conferida por quadratura com `harmonicos.sYlm` em 7 casos, erra no máximo 8,5e-15.
  São 110 coeficientes não nulos.
- **Valor final.** A série independente (Gaunt, derivada de 8ª ordem, antiderivada de spline) termina em
  1,6449830393e-22, igual a `serie_memoria` e ao deslocamento de janela. A diferença é 3,5e-12 em dt = 0,25 e
  5,7e-13 em dt = 0,125. Com a derivada por spline difere −1,2e-6 e −7,8e-8 (convergência ~dt⁴), o que confirma
  que a 8ª ordem já convergiu.
- **Instantes intermediários.** `serie_memoria` integra por trapézio e carrega erro O(dt²): −1,2e-5 no pico
  ($u=0$), +8,0e-6 em $u=20$ M e −2,0e-7 em $u=-100$ M, com dt = 0,25. Em dt = 0,125 os mesmos valores são
  −2,9e-6, +2,0e-6 e −5,0e-8 (razão ≈ 4,1). No fim o erro some porque a taxa é estacionária
  (Euler–Maclaurin: o termo $-(dt^2/12)[R'(u)-R'(t_i)]$ vai a zero). O L00 não menciona isso; não afeta a SNR.
- **SNR** ($h_+$, $\phi=0$):

  | Detector | `snr2` | outro tratamento | série independente, L ≤ 8 | série independente, L ≤ 4 | rev_R5 |
  |---|---|---|---|---|---|
  | aLIGO | 0,4702 | 0,4702 | 0,4702 | 0,4703 | 0,470 |
  | A+ | 0,8920 | 0,8920 | 0,8920 | 0,8922 | 0,892 |
  | ET | 8,6405 | 8,6403 | 8,6405 | 8,6420 | 8,642 |
  | CE | 34,0901 | 34,0896 | 34,0901 | 34,0962 | 34,096 |

  A diferença de 2e-4 entre o D0 e o rev_R5 (que o L00 deixou sem explicação) vem toda dos multipolos
  $\ell=6,8$: o rev_R5 usa só $\ell\le4$.

### 4.7 Teste (c) do D0 — `verif_L00_extra.txt` [V11: parcial]

- **Nível A.** Com $t_i:=t_{0b}-dt/2$ (a regra do retângulo de `binarias` equivale ao trapézio desde aí), a
  diferença contra `binarias` cai de 2,0e-6 para ≤ 4,7e-10. A atribuição do D0 está certa.
- **Nível C.** O deslocamento difere −4,2e-7 qualquer que seja o início. A causa é a última amostra:
  - `binarias` termina em 134,99 M e `observaveis` em 134,75 M;
  - o $h_{20}$ do substituto ainda varia +1,7e-7 por M no fim dos dados;
  - razão dos valores finais − 1 = −3,89e-7.

  O deslocamento de nível C tem, portanto, uma ambiguidade de ~4e-7 ligada ao fim dos dados.

### 4.8 Correção feita em `codigo/observaveis.py` (única)

1. **Defeito.** A docstring de `comparar2` dizia que `atraso` é "relativo ao alinhamento pelos picos". Na
   verdade é o $\tau$ entre as primeiras amostras ($a(t)\approx b(t-\tau)$). A subtração do pico em `preparar` não
   muda as amostras. O L00 (seção 7) repete o erro.
2. **Correção.**
   - docstrings de `preparar`, `produto2` e `comparar2` corrigidas, mais uma nota no cabeçalho do módulo;
   - função `_inicio_serie(t)`;
   - nova chave `atraso_rotulos` $=(t^B_\text{início}-t^A_\text{início})-\tau$, o atraso de B em relação a A nos
     rótulos dados ($B(t)\approx A(t-\delta)$).

   A chave `atraso` continua igual.
3. **Teste direto** (`verif_L00_match.txt` (e); seno-gaussiano em grades de 16384 e 13000 Hz com inícios
   diferentes): $\delta$ verdadeiro 0, +2,3456e-4 e −1,111e-3 s; `atraso_rotulos` devolve esses valores (ver o
   arquivo). Em (a), dá
   1,234566440e-3 contra 1,2345678e-3.
4. **Efeito.** Nenhum número de memória, SNR ou *match* mudou: os testes do D0 saem idênticos.

## 5. Tentativas de refutação e alternativas

1. **Escada.**
   - Varredura em $M$ quatro vezes mais longa que a do D0 (7 nós atravessados).
   - Varreduras em $q$ e $\chi$.
   - Mudança de `FRAC_INICIO` com $f_0$ alto. Na inspiral a grade esparsa do substituto é rala (dezenas a centenas de M entre nós em $t_i$, visto
     num script exploratório não guardado), e a truncagem em `initIdx` poderia criar outra escada. Com 0,9, não
     cria (`verif_L00_ruido.txt` (b)).
   - Possível troca de sinal dos $m$ ímpares pela ambiguidade de $\pi$.
   - Nada disso reabriu a escada. O ruído em $q$ e $\chi$ foi rastreado até a energia de cada modo do substituto.
2. **Pesos.**
   - Comparação com a fórmula fechada do erro, não só com a integral (o que separa "erro de trapézio" de "pesos
     errados").
   - Nós exatos e $t_i$ a ±1e-12 de um nó.
3. **CM.**
   - Recálculo da parte nula fora de `memorias_observaveis`.
   - Escala com a duração da janela.
   - Convenção alternativa $M_f\Phi_f-M_i\Phi_i$.
4. **`todos_m`.** Cópia literal do código do revisor, não reimplementação. A rotação azimutal foi estimada por
   um único multipolo e testada em todos.
5. **`comparar2`.**
   - Cinco controles: mesma onda com início e rede diferentes; senos-gaussianos analíticos (três casos, um com
     *match* 0,30); degraus analíticos (quatro casos, dois detectores); par físico com três inícios; atrasos
     conhecidos com rótulos diferentes.
   - O primeiro controle revelou o erro de semântica do `atraso` (V9).
   - Uma falha minha: a varredura de atraso de ±5 ms no valor exato achou um máximo local no caso de *match*
     0,30. Corrigida com uma varredura global por FFT densa.
6. **Série nula.** Caminho com projeção (Gaunt), normalização (Favata), quadratura (spline), derivada (8ª ordem
   ou spline) e tratamento de SNR independentes. Dois dt para separar o erro de trapézio.

## 6. Contraexemplos e limitações

- **Ruído do substituto em $q$ e $\chi$ (~3e-10 relativo).** Use passos ≥ ~1e-4 em $q$ e $\chi$ nos jacobianos.
  - Com $h=10^{-3}$ o erro de truncagem é ~1e-5 a 1e-3.
  - Com $h=10^{-6}$ o ruído dá ~3e-4.
- **Memórias com todos os $m$ num $\phi$ fixo oscilam em $M$.** O período é $\Delta M/M\approx1{,}46\%$ para
  $|m|=1$ e 0,73% para $|m|=2$; a amplitude é ±1,4% no spin. Para Fisher ou jacobianos com os $m\neq0$:
  - a fase de referência (ou $\phi$) tem de ser um parâmetro;
  - os passos em $M$ devem ser ≲ 1e-4 relativos (erro de truncagem ~(452·|m|·h)²/6).
- **Piso de `comparar2` depende do início da onda.** Ondas desde 0,9 $f_\text{min}$ (o padrão de `gerar_janela`)
  dão piso A-contra-A de 4,6e-6 (aLIGO) e 9,3e-5 (CE). Para comparar deformações completas, faça
  `O.FRAC_INICIO = 0.7` antes de gerar; o piso cai para 2,8e-8 e 3,5e-7. As memórias não mudam com isso
  (≤ 6e-11, V4).
- **Ondas começando em $f_\text{min}$.** Enviesam o *match* para baixo em 0,2% (aLIGO) e 4% (CE); com taper de
  2 s, em 14%.
- **Série nula fora do fim.** Erro de trapézio de até ~1e-5 relativo perto da fusão (dt = 0,25), ~3e-6 com
  dt = 0,125. Irrelevante para SNR e para *match* com $\rho\lesssim100$.
- **SNR.** Soma de Riemann com o bin de $f_\text{min}$ inteiro: viés ≤ 1,5e-4 em CE.
- **Nível C.** O deslocamento depende da última amostra em ~4e-7.
- **Não verifiquei de forma independente:**
  - a parte magnética da série e a memória de spin, que só conferi pela consistência interna de 2e-16 do D0;
  - a memória giroscópica;
  - a série `'rn'`;
  - os coeficientes de massas comparáveis de $E_\text{lig}$ contra o texto de Blanchet 2014. Conferi de memória
    as eqs. 233 e 415, e à mão o termo SO dominante no limite de massa teste: $-\tfrac43\,a\,v^5$ em $E/\mu$,
    igual a $-\tfrac{v^2}{2}(\tfrac{14}{3}-2)a v^3$. Os testes (g) do D0 foram só reexecutados;
  - a incerteza de modelo de $M_f$ (~1e-4), só reexecutada.
- **A PSD é a mesma** (`deteccao.psd_serie`) em todos os controles. Erros nas curvas do lalsimulation não seriam
  detectados.
- **Detector.** `comparar2` e `snr2` usam só $h_+$. Para a resposta de um detector, passe
  $(F_++iF_\times)\,h$ no lugar de $h$: a parte real é $F_+h_++F_\times h_\times$ [D, álgebra direta]. Não foi
  testado numericamente.

## 7. Literatura e originalidade

Não há alegação de originalidade: é verificação numérica de infraestrutura, e por isso não fiz busca
bibliográfica.

Fontes usadas:
- Favata 2009 (eq. 3.3, normalização da memória nula; conferida pela coincidência com Mitman et al. 2020 em
  `memorias.py` a 3,5e-12);
- integrais de três harmônicos com peso de spin por símbolos 3j (fórmula padrão), conferidas por quadratura;
- Blanchet, Living Rev. Relativ. 17, 2 (2014), eqs. 233 e 415, de memória;
- Bardeen, Press & Teukolsky 1972 (energia de órbitas equatoriais de Kerr), para o limite de massa teste;
- Euler–Maclaurin, para o erro de trapézio.

O comportamento de `f_ref`/`times` do gwsurrogate foi lido no código instalado (`gwsurrogate/new/surrogate.py`,
`_coorbital_to_inertial_frame`, `_search_omega`).

## 8. Próximos experimentos (recomendações às linhas)

1. Para Fisher e jacobianos (L01, L05): incluir a fase de referência e $\phi$; passos ≥ 1e-4 em $q$ e $\chi$ e
   ≲ 1e-4 em $M$ quando houver $m\neq0$. Validar cada jacobiano com $h$, $h/2$ e $h/4$, como em
   `verif_L00_suavidade.py` (e).
2. Para *match* entre deformações completas (L05–L07): gerar com `O.FRAC_INICIO = 0.7` e usar `atraso_rotulos`
   para ler atrasos. Entre séries de memória (que começam em zero em $t_i$), o padrão serve.
3. Testar de forma independente a parte magnética da série (memória de spin resolvida no tempo) com coeficientes
   de Gaunt do fluxo de momento angular.
4. Opcional: correção de Euler–Maclaurin nos instantes intermediários de `serie_memoria`, se uma linha precisar da
   forma da memória com precisão melhor que 1e-5.

## 9. Arquivos

- **Alterado:** `codigo/observaveis.py` (só docstrings, `_inicio_serie` e a chave `atraso_rotulos` de
  `comparar2`).
- **Regravados pela execução final dos testes do D0:** `resultados/testes_observaveis.txt` e
  `figuras/e00_escada_suavidade.png` (conteúdo idêntico).
- **Novos:**
  - `codigo/revisao/verif_L00_quadratura.py`, `verif_L00_suavidade.py`, `verif_L00_ruido.py`,
    `verif_L00_cm_mnao0.py`, `verif_L00_match.py`, `verif_L00_serie_nula.py`, `verif_L00_extra.py`;
  - `resultados/revisao/verif_L00_*.txt` (as sete saídas);
  - este relatório.

## 10. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| V1 | `pesos_janela`: trapézio com $t_i$ fora da grade, exato para lineares, contínuo em $t_i$ | confirmada matematicamente e numericamente | erro = fórmula fechada (2e-16); ordem 2; $dI/dt_i=-f_\text{lin}$ |
| V2 | Sem escada em $M$ | confirmada numericamente | resíduo ≤ 7e-12 ($m=0$), 8,6e-11 (todos os $m$); `binarias` 1,3e-6 |
| V3 | Suave em $q$ e $\chi$ | confirmada com piso | resíduo ~3e-10, vindo do substituto (energia por modo 2e-10 a 1,4e-9) |
| V4 | Independência de `FRAC_INICIO` | confirmada para ≤ 0,9 | ≤ 6e-11 com $f_0$ de 0,003 a 0,015; 0,95–0,97 até 7e-8 |
| V5 | Correção de fase sem ambiguidade de $\pi$ | confirmada numericamente | $|\delta\phi|\le1{,}1\text{e-}2$; resíduo 4,6e-12 rad |
| V6 | CM com o mesmo deslocamento nas duas partes; janela curta → 0 | confirmada numericamente | identidade 8e-24; cm20 ∝ duração (−7,5e-8/M) |
| V7 | `todos_m` = rev_R1 | confirmada numericamente | cópia do rev_R1 reproduzida; multipolos ≤ 1,2e-5 (CM 3,9e-4) depois da rotação; mesmas faixas |
| V8 | `comparar2` dá o *match* certo | confirmada numericamente, com piso dependente do início | analíticos ≤ 1,6e-7; piso 4,6e-6 / 9,3e-5 (0,9 $f_0$) e 2,8e-8 / 3,5e-7 (0,7 $f_0$) |
| V9 | `atraso` relativo ao alinhamento pelos picos | refutada; corrigida (docstring e `atraso_rotulos`) | `atraso` = 0,19997 s = diferença dos inícios; `atraso_rotulos` exato a 1e-9 s |
| V10 | Série nula termina no deslocamento de janela; SNR 0,47 / 0,89 / 8,6 / 34 | confirmada numericamente (caminho independente) | 3,5e-12; SNR 0,4702 / 0,8920 / 8,6405 / 34,0901; erro intermediário O(dt²) ≤ 1,2e-5 |
| V11 | Diferença contra `binarias` = só o início da janela | confirmada (nível A); refutada para o deslocamento do nível C | A: ≤ 4,7e-10 com $t_{0b}-dt/2$; C: −4,2e-7 da última amostra |
| V12 | Passos de ~1e-6 servem nos jacobianos | parcialmente refutada | em $M$ ($m=0$) sim; em $q$ e $\chi$, piso 3e-10; com todos os $m$, oscilação em $M$ de período 1,46% |
