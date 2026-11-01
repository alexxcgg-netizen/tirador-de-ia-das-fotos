# L00 — Infraestrutura: observáveis de memória numa janela física (agente D0)

Módulo novo: `codigo/observaveis.py`. Testes: `codigo/testes_observaveis.py` → `resultados/testes_observaveis.txt`
e `figuras/e00_escada_suavidade.png`. Não alterei `binarias.py`, `deteccao.py` nem `memorias.py`.

Sistema de referência dos testes (o "sistema A" do exp07): $M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$,
$D=400$ Mpc, $\iota=50^\circ$, janela desde 10 Hz, modelo NRHybSur3dq8_CCE.

---

## 1. Pergunta e hipóteses

**Pergunta.** Como calcular as quatro memórias numa janela $[t_i,\text{fim}]$ fixada por uma frequência física, e
a série temporal da memória que um detector veria, sem os defeitos achados na revisão adversarial da etapa 6?
Os defeitos são os itens 1 a 4, 6 e 13 do contexto: a escada numérica, o descarte dos $m\neq0$, o deslocamento
total no lugar do de janela, a inconsistência da memória de CM, o toque quase normal contado como memória e o
piso artificial do *match*.

Hipóteses (status na tabela da seção 10):

- **H00.1** A escada de ~3e-6 vem só do início discreto da janela. Com a onda numa rede fixa ancorada no pico,
  $t_i$ exato e peso parcial no primeiro subintervalo, as memórias ficam suaves em $M$: segundas diferenças
  ≪ 1e-8 em passos de 1e-7.
- **H00.2** A onda adimensional do substituto, avaliada numa rede fixa (opção `times`), não depende de
  `f_low`, isto é, do ponto onde começa o trecho auxiliar.
- **H00.3** Em dt = 0,25 M, o erro de discretização vem sobretudo da derivada de 4ª ordem na fusão. Uma
  derivada de 8ª ordem o reduz em ordens de grandeza.
- **H00.4** $M_f$ com $E_\text{lig}$ 1PN erra ~5e-5. Com 3PN mais spin-órbita 1,5/2,5/3,5PN, o erro da energia de
  ligação cai para ~1e-6 a 1e-5.
- **H00.5** Os $m\neq0$ mudam a memória de spin no observador em ±1,3e-2 ao longo de $\phi$ (a revisão achou
  isso com outra convenção de fase).
- **H00.6** A série "nula" termina exatamente no deslocamento de janela.
- **H00.7** `comparar2` tem 1−match < 1e-8 contra a própria onda atrasada fora da grade e reproduz a SNR da
  memória nula de A: 0,47 / 0,89 / 8,6 / 34.
- **H00.8** Com o deslocamento de janela, a memória de CM de uma janela curta tende a zero (consistência do item 4).
- **H00.9** A diferença sistemática $M_f$(observáveis) − NRSur3dq8Remnant ≈ +5,5e-5 vem dos modos ausentes
  do substituto CCE.

## 2. Fundamentação e equações

**Rede fixa e instante inicial.** A onda é pedida ao gwsurrogate nos instantes $t_k=(k+\delta)\,dt$. A rede
fica ancorada em $t=0$ (pico do (2,2)), com $\delta=$ `t_desloc`, e cobre o trecho desde $0{,}9f_0$
($f_0=M\,\mathrm{MSUN\_S}\,f_\text{ini}$). Em `binarias.gerar` (opção `dt`) a grade começa num nó da grade
esparsa do substituto e é truncada no primeiro ponto depois de `f_low`. Por isso o início salta de dt quando $M$
muda. A frequência é

$$\omega_{22}(t)=-\frac{d}{dt}\,\mathrm{unwrap}[\arg h_{22}(t)],$$

com diferenças centrais de 8ª ordem. $t_i$ é obtido por interpolação linear de $\omega_{22}$ entre os dois
pontos da rede que cercam $2\pi f_0$, antes do pico.

**Fase orbital.** O gwsurrogate zera a fase no ponto da grade mais próximo de `f_ref`, o que cria outra
escada, que afeta só os $m\neq0$. Uso `f_ref` $=f_0$ e corrijo exatamente com
$h_{\ell m}\to h_{\ell m}\,e^{-im\,\Phi_{22}(t_i)/2}$. Aqui $\Phi_{22}(t_i)$ vem de interpolação cúbica local
e é pequeno, $|\Phi_{22}(t_i)|\lesssim\omega_{22}\,dt$. A ambiguidade de $\pi$ fica a do gwsurrogate: o buraco
mais pesado está em $+x$ quando $f_{22}=f_0$. O azimute $\phi$ do observador é medido a partir dessa fase.

**Pesos de janela.** Para $t_{k-1}<t_i\le t_k$, com $a=(t_i-t_{k-1})/dt$ e $L=t_k-t_i$:

$$w_{k-1}=\tfrac12L(1-a),\quad w_k=\tfrac12L(1+a)+\tfrac12dt,\quad w_j=dt\ (k<j<N-1),\quad w_{N-1}=\tfrac12dt.$$

Isso é o trapézio de $t_k$ ao fim mais o subintervalo $[t_i,t_k]$ com $f(t_i)$ interpolado linearmente. A
integral é contínua em $t_i$ e tem derivada contínua $-f(t_i)$. As matrizes de Gram ponderadas são
$B=\sum_k w_k\dot h_k\dot h_k^\dagger$ e $A=\sum_k w_k h_k\dot h_k^\dagger$. Elas entram em
`CalculadoraMemoria.memorias_gram` sem mudança, com as fórmulas de Mitman et al. 2020, Nichols 2018 e
Seraj & Oblak 2022 já usadas em `memorias.py`.

**Memória de CM** ($\Delta K$ de Nichols 2018, eq. 3.11), no mesmo esquema de `binarias`:

$$\Delta K_{\ell m}^{(h)}=\text{(nula da janela)}+\tfrac12\,\bar\eth^2_\ell\left[-\tfrac32M_f\,\frac{\Delta\Phi_{\ell m}}{\mathfrak D_\ell}\right],\qquad \Delta\Phi_{\ell m}=\frac{2\,\Delta J_{\ell m}}{\bar\eth^2_\ell}.$$

$\Delta J$ é o deslocamento da opção `desl`. Com `desl='janela'`, as partes nula e ordinária usam a mesma
janela: é a correção do item 4. Com `desl='total'`, a parte nula continua sendo só a da janela (a nula total
diverge com o início da inspiral). Essa opção existe só para reproduzir `binarias`.

**Massa final.** $M_f=1-E_\text{janela}-E_\text{lig}(x_i)$, com $x_i=(\pi f_0)^{2/3}$. A energia de ligação vem de
Blanchet, Living Rev. Relativ. 17, 2 (2014), eqs. 233 e 415:

$$E_\text{lig}=\tfrac{\eta x}{2}\Big\{1-\big(\tfrac34+\tfrac{\eta}{12}\big)x-\big(\tfrac{27}{8}-\tfrac{19}{8}\eta+\tfrac{\eta^2}{24}\big)x^2-\big(\tfrac{675}{64}-(\tfrac{34445}{576}-\tfrac{205}{96}\pi^2)\eta+\tfrac{155}{96}\eta^2+\tfrac{35}{5184}\eta^3\big)x^3$$
$$\qquad+x^{3/2}\big[\tfrac{14}{3}S+2\delta\Sigma\big]+x^{5/2}\big[(11-\tfrac{61}{9}\eta)S+\delta(3-\tfrac{10}{3}\eta)\Sigma\big]+x^{7/2}\big[(\tfrac{135}{4}-\tfrac{367}{4}\eta+\tfrac{29}{12}\eta^2)S+\delta(\tfrac{27}{4}-39\eta+\tfrac54\eta^2)\Sigma\big]\Big\}$$

Aqui $S=\chi_1m_1^2+\chi_2m_2^2$, $\Sigma=\chi_2m_2-\chi_1m_1$ e $\delta=m_1-m_2$ ($M=1$). Os termos spin-spin
ficaram de fora.

**Série temporal nula.** Para cada $(\ell,m)$, $S_{\ell m}(t)=\int_{t_i}^{t}\dot J^\text{nula}_{\ell m}\,du$,
integrado com a mesma quadratura dos pesos, a partir da taxa de `partes_instantaneas`. A série é
$s(t)=\sum S_{\ell m}(t)\,{}_{-2}Y_{\ell m}(\iota,\phi)\,M/D$. Opcionalmente soma-se a parte magnética
instantânea $h^B(u)$, cuja integral é a memória de spin.

**Match.** O critério de distinguibilidade sem supor normas iguais (Lindblom et al. 2008) é
$(\delta h|\delta h)=\rho_A^2+\rho_B^2-2\rho_A\rho_B\,\text{match}=1$. Isso dá
$\rho_\text{crit}=1/\sqrt{1+r^2-2r\,\text{match}}$ com $r=\rho_B/\rho_A$; é o `rc_exato` de
`revisao/rev_R2_comum.py`.

## 3. API (nomes exatos; docstrings em português sem acentos)

| Função | O que faz |
|---|---|
| `gerar_janela(q, chi1, chi2, M_msun, f_ini_hz, dt=0.25, t_desloc=0.0) -> (t, h, t_i)` | onda na rede fixa desde ~0,9 $f_0$; $t_i$ em que $f_{22}=f_0$; fase orbital zerada em $t_i$; `t` em M, `h` dict de modos (inclusive $m=0$ e $m<0$) |
| `pesos_janela(t, t_i) -> w` | pesos de trapézio de $t_i$ ao fim, com subintervalo parcial linear |
| `gram_pesos(H, Hd, w) -> (B, A)` | como `memorias.gram`, com pesos |
| `memorias_observaveis(q, chi1, chi2, M_msun, f_ini_hz, nivel='A', desl='janela', todos_m=False, dt=0.25, t=None, h=None, t_i=None, ordem_deriv=8, ordem_elig=3) -> (mem, aux)` | memórias (dict por tipo e $(\ell,m)$, $\ell\le8$); `aux`: `E_janela`, `E_lig`, `M_f`, `P_rad`, `recuo` ($=-P/M_f$), `t_i`, `x_i`, `eta`, `f0` |
| `no_observador_completo(mem, iota, phi)` | as quatro memórias adimensionais no observador, somando todos os $(\ell,m)$; com só $m=0$ reproduz `binarias.no_observador` |
| `valores_fisicos_completo(mem, iota, phi, M_msun, D_mpc)` | mesmo formato de `binarias.valores_fisicos` |
| `serie_memoria(t, h, t_i, iota, phi, M_msun, D_mpc, tipo='nula', todos_m=False, magnetica=False) -> (t_s, s)` | série $h_+-ih_\times$ (segundos, deformação) desde $t_i$; `'nula'`: fluxo dos modos oscilatórios; `'rn'`: modos $m=0$ do substituto menos o valor em $t_i$ (inclui o toque quase normal) |
| `comparar2(tA, hA, tB, hB, nome_psd, fmin, fs=4096.0, up=16, taper=0.5, fim='rampa')` | dict com `match`, `snr_A`, `snr_B`, `r`, `rho_crit` exato, `dd`, `atraso` |
| `snr2(t, h, nome_psd, fmin, fs=4096.0, taper=0.5, fim='rampa')` | SNR ótima de $h_+$ |
| auxiliares: `derivada(H, dt, ordem=8)`, `instante_frequencia(t, h22, f0)`, `e_lig(x, q, chi1, chi2, ordem=3)`, `preparar(...)`, `produto2(...)` | |

**Nível A:** fluxos dos modos oscilatórios.

**Nível C:**
- deslocamento $h_{\ell0}(\text{fim})-h_{\ell0}(t_i)$ para $\ell=2,4$, interpolado linearmente; com
  `desl='total'`, $h_{\ell0}(\text{fim})$;
- spin $\sum_k w_k\,h_{30}(t_k)$;
- giroscópica $-\mathfrak D_3\Psi_{30}$ + helicidade, como no nível C de `binarias`;
- demais multipolos (inclusive os $m\neq0$) pelos fluxos com todos os modos.

**Uso típico numa linha:**

```python
import observaveis as O
t, h, ti = O.gerar_janela(q, c1, c2, M, 10.0)             # gerar uma vez
mem, aux = O.memorias_observaveis(q, c1, c2, M, 10.0, t=t, h=h, t_i=ti, todos_m=True)
v = O.valores_fisicos_completo(mem, iota, phi, M, D)      # quatro numeros fisicos
ts, s = O.serie_memoria(t, h, ti, iota, phi, M, D, tipo="nula")
rho = O.snr2(ts, s, "CE", 10.0)
del t, h                                                   # nao guardar formas de onda em lacos
```

Custo medido no sistema A, na máquina compartilhada, depois de carregar o substituto:

| Chamada | Tempo |
|---|---|
| `gerar_janela` | 0,1 s |
| `memorias_observaveis` com `todos_m` | 0,55 s |
| `serie_memoria('nula')` | 14 s |
| `snr2` | 0,03 s |

O pico de memória do processo é 0,95 GB, dos quais 0,54 GB vêm só de carregar o substituto.

## 4. Experimentos

`codigo/testes_observaveis.py`, um único processo com `OMP_NUM_THREADS=1`, ~2,5 min. Saída em
`resultados/testes_observaveis.txt`; os números abaixo foram copiados de lá.

| Teste | O que faz |
|---|---|
| (a) | suavidade em $M$: passos 1e-7 (k=0..6) e 1e-6 (k=0..12), níveis A e C; todos os $m$; contraste com `binarias`; início auxiliar 0,8 $f_0$ contra 0,9 $f_0$ |
| figura | memória de spin de A para $\Delta M/M$ de 0 a 1,2e-5, `binarias` contra `observaveis` |
| (b) | dt = 0,25, 0,125, 0,0625 com derivadas de 8ª e 4ª ordem; rede deslocada de meio passo |
| (c) | `desl='total'`, `todos_m=False` contra `binarias.memorias_fisicas`, níveis A e C |
| (d) | efeito dos $m\neq0$ ao longo de 24 valores de $\phi$ |
| (e) | valor final da série nula contra o deslocamento de janela; parte magnética; série `'rn'` |
| (f) | `comparar2` com atrasos fora da grade; contraste com `deteccao.comparar`; SNR das séries nula e `'rn'` |
| (g) | limite de massa teste de $E_\text{lig}$ (Kerr, sympy); energia irradiada de 10 a 20 Hz no substituto contra $\Delta E_\text{lig}$; $M_f$ contra o ajuste NRSur3dq8Remnant |
| (h) | CM (2,0) numa janela de 50 M |
| (i) | origem da diferença de $M_f$: modos ausentes e outro substituto (NRSur7dq4) |

## 5. Resultados

### (a) Suavidade [H00.1, H00.2]

Segundas diferenças relativas das memórias de janela de A no observador:

| Caso | Segunda diferença |
|---|---|
| passo 1e-7 | ≤ 1,5e-14 (níveis A e C); a primeira diferença é ~5e-8 no spin |
| passo 1e-6, nível A | ≤ 9,9e-12 |
| passo 1e-6, nível C | ≤ 1,0e-11 |
| contraste: `binarias`, passo 1e-6 | 2,8e-6 (spin), 3,0e-6 (giroscópica), 3,6e-7 (deslocamento) |
| todos os $m$, $\phi=0{,}8$ rad, passo 1e-6 | ≤ 6,2e-10 |

- No caso com todos os $m$, a segunda diferença de 6,2e-10 é curvatura genuína, não escada. Quando $t_i$ anda
  ~0,044 M por passo, a parte $m\neq0$ (~1,3e-2) gira ~4,4e-4 rad, e $(4{,}4\text{e-}4)^2\times1{,}3\text{e-}2\approx2\text{e-}9$.
- Início auxiliar em 0,8 $f_0$ contra 0,9 $f_0$: os multipolos diferem ≤ 1,2e-15 e $t_i$ é idêntico. A
  independência de `f_low` na rede fixa também foi verificada diretamente: diferença 0,0 nos modos.
- A figura `figuras/e00_escada_suavidade.png` mostra a escada de `binarias` (degraus de 2,8e-6, espaçados de
  ~5,6e-6 em $\Delta M/M$) contra a reta suave de `observaveis` (variação de 6,07e-6 em 1,2e-5).

### (b) Convergência em dt [H00.3]

Diferenças relativas contra dt = 0,0625:

| Caso | Deslocamento | Spin | CM | Giroscópica |
|---|---|---|---|---|
| ordem 8, dt 0,25 | −8,2e-8 | −3,3e-10 | −5,9e-8 | −2,0e-10 |
| ordem 8, dt 0,125 | −1,5e-8 | — | −1,2e-8 | — |
| ordem 4, dt 0,25 | −7,5e-6 | −1,4e-6 | −6,9e-6 | −1,2e-6 |
| ordem 4, dt 0,125 | −4,7e-7 | — | −4,3e-7 | — |

- Na 8ª ordem, o resto escala como $dt^2$: a razão de 15 para 3 é ~5,6 entre dt 0,25 e 0,125. É o erro do
  trapézio, ~1e-7 em dt = 0,25.
- Ordem 8 contra ordem 4 em dt = 0,0625: 3,3e-8.
- Rede deslocada de meio passo: ≤ 5,5e-8 no observador e ≤ 3,4e-8 nos multipolos.

### (c) Contra `binarias` [consistência]

Com as mesmas fórmulas (derivada de 4ª ordem, $E_\text{lig}$ 1PN):

| Nível | Deslocamento | Spin | CM | Giroscópica | $M_f$ |
|---|---|---|---|---|---|
| A | −2,6e-7 | −2,0e-6 | −2,2e-7 | −2,2e-6 | +1,4e-8 |
| C | −4,2e-7 | −2,1e-6 | −3,4e-7 | −2,2e-6 | — |

Toda a diferença é a do início da janela. `binarias` começa em $t_0=-16430{,}2602$ M e usa a regra do
retângulo, o que equivale a começar em ~$t_0-dt/2=-16430{,}385$; aqui $t_i=-16430{,}2044$. São 0,18 M a menos,
e a taxa de spin é ~1,1e-5/M, o que dá 2e-6: é a escada, abaixo de 1e-5 como pedido.

Com o padrão do módulo (8ª ordem, 3PN+SO), no nível A: deslocamento +6,3e-6, CM +2,8e-5, $M_f$ +2,4e-5. Essas
diferenças são as correções da derivada e de $E_\text{lig}$; ver (b) e (g).

### (d) Multipolos $m\neq0$ [H00.5]

Razão (todos os $m$)/(só $m=0$) − 1 ao longo de $\phi$, $\iota=50^\circ$:

| Caso | Deslocamento | Spin | CM | Giroscópica |
|---|---|---|---|---|
| nível A, `desl='janela'` | [−1,37e-3, +1,99e-3] | ±1,34e-2 | [−5,3e-3, +5,0e-3] | [−5,3e-3, +5,1e-3] |
| nível A, `desl='total'` | [−1,23e-3, +1,79e-3] | ±1,34e-2 | [−4,9e-3, +4,6e-3] | [−5,3e-3, +5,1e-3] |
| nível C, `desl='janela'` | [−2,8e-3, +3,0e-3] | [−1,32e-2, +1,34e-2] | [−3,6e-3, +3,0e-3] | [−5,7e-3, +4,8e-3] |

- Com `desl='total'`, os valores coincidem com a revisão (`rev_R1_m_nao_nulo.txt`: spin ±1,34e-2).
- Maior multipolo $m\neq0$ de cada tipo: spin (2,−1) |.| = 4,4e-3 contra (3,0) 0,26; giroscópica (2,−1) 3,6e-3;
  deslocamento (3,−1) 1,7e-4; CM (2,−2) 1,2e-4.

### (e) Série nula [H00.6]

- O valor final de $\mathrm{Re}\,s$ é igual ao deslocamento de janela em unidades físicas: diferença relativa
  1,6e-15 com só $m=0$ e 1,3e-15 e 2,2e-15 com todos os $m$ ($\phi=0{,}7$ e 2,9).
- Com `magnetica=True`, $\int h_\times dt$ da série é igual à memória de spin da janela: −2,497911e-25 s nos
  dois, diferença 2e-16.
- Série `'rn'`: o valor final é igual ao deslocamento de janela do nível C restrito a $\ell=2,4$ (diferença
  0,0). Com $\ell=6,8$ do fluxo a diferença é 1,2e-4.

### (f) `comparar2` e SNR [H00.7]

Atraso verdadeiramente sub-amostra. O sinal com janela de Tukey já aplicada, $g(t)$, é comparado com
$g(t-\varepsilon)$ nos mesmos instantes, com `taper=0`. Valores de 1−match:

| $\varepsilon$ (s) | up=1, sem refino | up=16, sem refino | up=16 com refino contínuo | `deteccao.comparar` |
|---|---|---|---|---|
| 9,03e-5 (=0,37/fs) | 8,1e-4 | 1,5e-7 | **5,8e-10** | 8,1e-4 |
| 1,2346e-3 | 1,9e-5 | 2,0e-7 | **2,6e-9** | 6,3e-4 |
| 5,3e-5 | 2,8e-4 | 5,2e-6 | **1,6e-9** | 2,8e-4 |

O atraso recuperado é exato (−9,0332e-5, −1,2346e-3 e −5,2882e-5 s).

A amostrado noutra rede do substituto (`t_desloc=0.37`) e com os tempos somados de 1,2345678e-3 s dá
1−match = 1,0e-12. Esse caso testa só a reamostragem por spline: as duas séries começam no mesmo instante físico.

Contraste entre dois sistemas: A contra $q=1{,}19$ (demais parâmetros iguais), aLIGO.

| Variante | 1−match |
|---|---|
| `comparar2` | 4,66e-4 ($\rho_\text{crit}=32{,}7$) |
| sem taper e sem rampa | 2,74e-3 |
| `deteccao.comparar` | 3,76e-3 (8× maior, o piso artificial do item 13) |

SNR de $h_+$ das memórias de A:

| Série | aLIGO | A+ | ET | CE | Referência |
|---|---|---|---|---|---|
| nula | 0,470 | 0,892 | 8,640 | 34,090 | 0,470 / 0,892 / 8,642 / 34,096 (`rev_R5_snr_memoria_qnm.txt`) |
| `'rn'` | 0,759 | 1,444 | 10,686 | 39,104 | exp15 / rev_R5: 0,759 / 1,444 / 10,686 / 39,103 |

O taper de 0,5 s não muda a SNR nula na 3ª casa.

### (g) $E_\text{lig}$ e $M_f$ [H00.4]

- **Limite de massa teste.** Expandi a energia de órbitas equatoriais de Kerr em $v=(M\Omega)^{1/3}$ (sympy).
  Os coeficientes em $a^0$ e $a^1$ até $v^9$ coincidem com o limite $\eta\to0$ da fórmula (diferenças
  todas 0).
- **Energia irradiada entre 10 e 20 Hz no substituto ($M=65$) contra $\Delta E_\text{lig}$.** Erro PN − substituto:

  | $(q;\chi_1,\chi_2)$ | 1PN | 3PN+SO | 3PN sem SO |
  |---|---|---|---|
  | (1,2; 0, 0) | +1,06e-4 | −2,3e-6 | −2,3e-6 |
  | (4; 0, 0) | +7,9e-5 | −2,4e-6 | −2,4e-6 |
  | (1,2; +0,5, +0,5) | −7,0e-5 | −2,0e-6 | −1,78e-4 |
  | (4; +0,5, +0,5) | −5,0e-5 | −7,6e-6 | −1,32e-4 |
  | (1,2; −0,5, −0,5) | +3,0e-4 | +1,8e-5 | +1,94e-4 |
  | (4; −0,5, −0,5) | +2,2e-4 | +1,4e-5 | +1,38e-4 |
  | (1,2; +0,3, −0,2) | +7,6e-5 | −5,2e-6 | −3,2e-5 |
  | (4; +0,3, −0,2) | +2,3e-5 | −4,3e-6 | −5,9e-5 |

  Os termos SO são indispensáveis com spins. O resto, ≤ 1,8e-5 a 20 Hz, é ímpar em $\chi$ e portanto não é
  spin-spin; provavelmente vem de ordens SO mais altas.
- **$M_f$ contra NRSur3dq8Remnant.** Diferenças +5,2e-5 (A), +5,6e-5, +6,7e-5 e +5,4e-5, todas dentro do erro
  do ajuste (±1,2e-4) mas sistemáticas. Ver (i).

### (h) CM numa janela curta [H00.8]

Janela de 50 M desde $t_i$, $q=1$, $\chi=0$:

| Opção | desl20 | cm20 |
|---|---|---|
| `desl='janela'` | 7,4e-6 | −3,7e-6 (vai a ~0, como deve) |
| `desl='total'` | 1,04e-2 | −5,159e-3 |

Com `'total'`, cm20 é igual a $-(M_f/2)\,h_{20}^\text{Favata}(x_i)=-5{,}155\text{e-}3$: um termo de borda que
vem de antes da janela. Na janela completa, cm20 vale −0,04729 (`'janela'`) contra −0,05223 (`'total'`); 9,4%
do valor "total" vinha de antes de 10 Hz.

### (i) Origem da diferença de $M_f$ [H00.9 — refutada]

Os modos com $\ell\le4$ ausentes do substituto CCE ((3,1), (4,1), (4,2)) carregam só 6,6e-7 a 1,2e-6 de energia
no NRSur7dq4. A explicação "modos ausentes" está refutada.

Na mesma janela ($f_{22}\ge0{,}0055/M$), a energia irradiada difere entre os dois substitutos (CCE − NRSur7dq4):

| $(q;\chi_1,\chi_2)$ | Diferença |
|---|---|
| (1; 0, 0) | −2,2e-5 |
| (1,2; +0,3, −0,2) | −1,1e-4 |
| (2; −0,5, +0,5) | +2,3e-4 |

Os dois ajustes de remanescente dão erros de 6e-5 e 1,2e-4.

**Conclusão:** a diferença de ~5e-5 está no nível da incerteza entre modelos (~1e-4). Não é um defeito
numérico do módulo. Tratar $M_f$ como conhecido a ~1e-4.

## 6. Tentativas de refutação e alternativas

1. **Escada (H00.1).** Cinco abordagens:
   - (i) a da revisão (`rev_R2v_escada.py`): $t_i$ por diferença para frente e peso fracionário no primeiro
     ponto. Remove o salto, mas mantém a grade do gwsurrogate ancorada num nó esparso, que muda com `f_low`;
   - (ii) quantizar `f_low`. Desnecessário: na rede fixa os valores não dependem de `f_low` (teste (a), 1e-15);
   - (iii) suavizar o início com uma rampa, como em `rev_R1`. Rejeitado: muda o observável;
   - (iv) rede fixa, $t_i$ exato e peso parcial: adotada;
   - (v) interpolação de ordem mais alta do integrando em $t_i$. Desnecessária: a dobra da interpolação linear
     dá segunda diferença ~1e-12, estimada e medida.
2. **Kerr.** Minha primeira verificação acusou diferenças em $a^1$ (+1/3, −1/2, −27/8). A causa estava no
   teste: a fórmula de Kerr usa $u=\sqrt{M/r_{BL}}$, não $(M\Omega)^{1/3}$. Corrigida a variável, tudo coincide.
3. **Teste (f).** A primeira versão era trivial (mesmo instante físico inicial: as amostras caíam nos mesmos
   instantes). Refeito com atraso verdadeiro. Depois, um resíduo de 5e-8 em $\varepsilon$ = 1,2 ms foi rastreado
   até um corte meu de 64 amostras no fim: a série acabava ~84 M após o pico, com o *ringdown* ainda em ~1e-3.
   Sem o corte, 2,6e-9.
4. **Parte magnética da série.** Na primeira versão eu subtraía $h^B(t_i)$, e $\int h_\times$ errava 19%.
   $h^B$ é instantâneo, não acumulado, e não deve ser subtraído. Corrigido; a diferença caiu para 2e-16.
5. **$M_f$.** Testadas cinco alternativas: 1PN, 3PN sem SO, 3PN+SO, o ajuste NRSur3dq8Remnant e a energia do
   NRSur7dq4. A hipótese "modos ausentes" (H00.9) foi refutada.
6. **Derivada.** Testadas a 4ª e a 8ª ordem. A derivada espectral (FFT) não foi tentada: o sinal não é
   periódico e o fim tem um degrau nos $m=0$.

## 7. Contraexemplos e limitações

- **Erro do modelo.** NRHybSur3dq8_CCE só tem spins alinhados, $q\le8$ (treino), $|\chi|\le0{,}8$, e os modos
  $\ell\le5$ listados em `binarias.MODOS_OSC`.
  - A energia irradiada difere de NRSur7dq4 por até 2,3e-4 (teste (i)). Esse é o nível de incerteza de
    $E_\text{janela}$ e $M_f$, e é muito maior que o erro numérico (~1e-7).
  - O nível C tem 5–12% de erro na taxa de spin na parte híbrida PN (item 10 da revisão). O nível A é mais
    confiável na inspiral.
- **$E_\text{lig}$.** Sem termos spin-spin. O resto é ≤ 1,8e-5 a 20 Hz com $|\chi|=0{,}5$ e menor a 10 Hz.
- **Opção `desl='total'`.** A parte nula da CM continua sendo só a da janela; use `'janela'` para observáveis.
  A parte ordinária usa $M_f$. A variante $M_f\Phi_f-M_i\Phi_i$ difere ~0,5% (`rev_R3_cm_convencoes.txt`).
- **Nível C com `todos_m`.** Os $m\neq0$ vêm do fluxo (o substituto não tem modos de memória $m\neq0$).
- **Convenção de $\phi$.** Depende da resolução de $\pi$ do gwsurrogate (buraco mais pesado em $+x$ quando
  $f_{22}=f_0$). Comparações de $\phi$ entre sistemas diferentes são convenção, não física.
- **`comparar2`.**
  - Usa só $h_+$ (detector ótimo para +), sem padrões de antena: o que um detector mede é $F_+h_++F_\times h_\times$
    (item 5).
  - O fim dos dados é 135 M após o pico. O tratamento `'rampa'` mantém o último valor, inclusive um resto de
    *ringdown* de ~1e-5 do pico.
  - O alinhamento inicial é pelo pico de $|h|$ (só define o atraso relativo; a busca é contínua).
- **Escopo.** O módulo cobre só NRHybSur3dq8_CCE. O caminho SEOBNRv5EHM (`exp12`) continua com início na grade e
  saída não suave (item 14). A linha L16 precisaria de um tratamento análogo de janela e fase.
- **Série nula.** É de ordem quadrática (nível A), com $\ell\le8$ e só os modos do substituto.

## 8. Literatura e originalidade

Não alego originalidade: é infraestrutura numérica. As fórmulas vêm de:
- Mitman et al. 2020 (memórias nulas);
- Nichols 2018, eqs. 3.11 e 4.23 ($\Delta K$);
- Seraj & Oblak 2022 (giroscópica);
- Favata 2009 e Blanchet LRR 2024 (memória antes da janela, como em `binarias`);
- Blanchet LRR 2014, eqs. 233 e 415 ($E_\text{lig}$);
- Yoo et al. 2023 (NRHybSur3dq8_CCE);
- Varma et al. 2019 (NRSur7dq4 e os ajustes NRSur3dq8Remnant / NRSur7dq4Remnant via surfinBH);
- Lindblom, Owen & Brown 2008 (critério de distinguibilidade).

Os coeficientes de $E_\text{lig}$ foram conferidos de duas formas independentes da fonte: no limite de massa
teste (Kerr, exato até 3,5PN em $a^0$ e $a^1$) e contra o fluxo do substituto (seção 5(g)). Os coeficientes
de massas comparáveis só foram testados indiretamente, por essa comparação. Não fiz busca bibliográfica porque
não há alegação de novidade.

## 9. Próximos experimentos

1. Tratamento análogo de janela e fase para SEOBNRv5EHM (excêntricas, L16): rede fixa, $t_i$ exato, anomalia
   explícita.
2. Termos spin-spin em $E_\text{lig}$ e comparação com o fluxo em $|\chi|=0{,}8$.
3. `comparar2` com padrões de antena e as duas polarizações ($F_+h_++F_\times h_\times$), para as linhas
   L05–L07.
4. Matrizes de Fisher e jacobianos (L01, L05) com as memórias suaves: os passos podem agora ser tão pequenos
   quanto ~1e-6 sem o piso de 3e-6.
5. Quantificar a incerteza entre modelos de $E_\text{janela}$ e das memórias (CCE contra NRSur7dq4 na
   parte comum) como barra de erro sistemática de cada linha.

## 10. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H00.1 | Rede fixa + $t_i$ exato + peso parcial eliminam a escada (segunda diferença ≪ 1e-8) | confirmada numericamente | (a): ≤ 1,5e-14 (passo 1e-7), ≤ 1e-11 (passo 1e-6); `binarias` 2,8e-6; figura e00 |
| H00.2 | A onda na rede fixa não depende de `f_low` | confirmada numericamente | diferença 0,0 nos modos; memórias ≤ 1,2e-15 (0,8 contra 0,9 $f_0$) |
| H00.3 | O erro em dt = 0,25 vem da derivada de 4ª ordem; a 8ª reduz | confirmada numericamente | (b): 7,5e-6 → 8,2e-8 (deslocamento), 1,4e-6 → 3,3e-10 (spin) |
| H00.4 | $E_\text{lig}$ 3PN+SO reduz o erro da energia de ligação para ~1e-6–1e-5 | confirmada numericamente (e analiticamente no limite de massa teste) | (g): 1PN até 3,0e-4, 3PN+SO ≤ 1,8e-5 (10→20 Hz); Kerr exato até 3,5PN |
| H00.5 | $m\neq0$ mudam o spin no observador em ±1,3e-2 | confirmada numericamente | (d): ±1,34e-2 |
| H00.6 | Série nula termina no deslocamento de janela | confirmada numericamente | (e): 1,6e-15 |
| H00.7 | `comparar2`: 1−match < 1e-8 com atraso fora da grade; SNR nula 0,47/0,89/8,6/34 | confirmada numericamente | (f): 5,8e-10 a 2,6e-9; SNR 0,470/0,892/8,640/34,090 |
| H00.8 | CM de janela curta → 0 com `desl='janela'` | confirmada numericamente | (h): −3,7e-6 contra −5,16e-3 com `'total'` |
| H00.9 | A diferença $M_f$ − NRSur3dq8Remnant (+5,5e-5) vem dos modos ausentes do CCE | refutada | (i): modos ausentes ~1e-6; a diferença entre modelos é ~1e-4 |
