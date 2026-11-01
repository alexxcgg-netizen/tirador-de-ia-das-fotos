# L12–L15 — Limites memória–energia, canais não gravitacionais, momentos × janelas e outros campos (agente D4)

Rótulos: **[E]** estabelecido (com referência), **[D]** derivado ou verificado aqui, **[H]** hipótese, **[S]** especulação.
Todo número citado vem de um arquivo em `resultados/` produzido pelos scripts `codigo/exp28_*`, `exp29_*`, `exp36_*`
e `exp37_*` (indicado em cada caso). Convenções do projeto: $G=c=1$, $h=r(h_+-ih_\times)$, modos em ${}_{-2}Y_{\ell m}$.
Modelo de binária: NRHybSur3dq8_CCE pela infraestrutura `codigo/observaveis.py` (L00), nível A (memória nula), janela
física desde 10 Hz, $M=65\,M_\odot$.

## Resumo

1. **L12, constante ótima [D].** A fórmula de Thorne coincide com a fórmula em modos do projeto até 9e-15 (mesmo sinal e
   normalização). Daí $|D\,\Delta h|\le 4E_\text{rad}$ (supremo: feixe apontado para o observador). Para radiação
   gravitacional com multipolos $\ell\le L$, a constante ótima $c_L$ é um autovalor de uma matriz de Gram:
   - $c_2=\sqrt{30}/6=0{,}9129$ (exato, sympy);
   - $c_3=1{,}852$, $c_4=2{,}239$, $c_6=2{,}715$, $c_8=3{,}006$ e $c_{128}=3{,}931$;
   - $4-c_L\approx8{,}9/L$, com expoente local −0,991 entre $L=96$ e $128$.

   Uma binária quadrupolar de ordem dominante fica em $\sin^2\iota(17+\cos^2\iota)/24\le17/24$.
2. **L12, versão para binárias [D].** O limite cresce depressa com a pequena energia fora de $\ell=2$, por causa dos
   termos cruzados: $c(e_2)$ = 1,20 com $e_2=0{,}99$ e 1,55 com $e_2=0{,}95$. Em binárias reais:
   - a memória nula fica em 31–65% de $c(e_2)E_\text{janela}$ (de lado) e em 16–21% de $4E_\text{janela}$;
   - a lei da área deixa mais um fator de 3 a 13 de folga;
   - no total, a memória fica em 3–22% (com $c(e_2)$ e o spin final) ou em 1,3–4,7% (com 4 e só a lei da área) do limite.

   Um teste da lei da área pela memória é possível em princípio, mas só detectaria memórias 4,5–77 vezes maiores que a
   da RG. Com SNR 8,6 (ET) ou 34 (CE), o teste de consistência com o fluxo das ondas é muito mais forte.
3. **L13 [E + D].** Núcleo [E, MW2019 eq. 100]: as partes $\ell=0,1$ da fluência não geram memória. Verifiquei que isso
   vale para qualquer velocidade $\beta$ (≤ 2e-15).
   - Construí duas histórias com memória nula igual no céu inteiro (1,3e-14): uma só gravitacional; outra com 30% da
     energia num jato bipolar de neutrinos com recuo.
   - A degenerescência se quebra:
     - pelo perfil temporal: uma memória que sobe em 1 s retém 0,4% (aLIGO) a 0,7% (CE) da SNR de um degrau rápido;
     - pela velocidade: $\lambda_\ell(\beta)/\lambda_\ell(1)\to c_\ell\beta^\ell$ com $\beta\to0$, com $c_2=4/5$;
     - pela orientação da polarização da memória: 10,6° com um jato desalinhado de 15°;
     - pela razão memória/oscilação.
   - Cota inferior da energia não gravitacional: $E_x\ge D\,|\delta h|/4$, válida para qualquer $\beta\le1$.
4. **L14 [D, numérico].**
   - **Condicionamento.** O número de condição de $K$ momentos cresce exponencialmente: fator ~5,0 por momento com a
     origem na fusão ou no início, ~2,3 com a origem no meio. O de $K$ janelas cresce só como $K^{1{,}1}$–$K^{1{,}2}$
     (H14.1 confirmada).
   - **Informação.** Com ruído comum na série, $K$ momentos retêm a mesma informação que $K$ coeficientes de Legendre:
     ≤ 0,6% com $K\le32$ e ≤ 5,5% com $K=64$. $K$ janelas de energia igual retêm 18–43% com $K=6$ e 93–99% com $K=64$.
     Janelas uniformes no tempo retêm < 0,5%.
   - **Moral.** A base estável e informativa são janelas adaptadas ao fluxo, isto é, amostras da curva de memória
     concentradas na fusão. Condicionamento bom não basta.
   - **Sensibilidade ao início.** Os momentos superiores dependem do início da janela: mudar o início de −4 s para −3 s
     muda $\mu_1$ em 21% e $\mu_9$ em 92%.
5. **L15 [D].** Todo observável integral, sesquilinear, local e invariante por translação em $u$ depende só de
   $(B,A,\ldots)$ e é invariante por um filtro de fase comum. Isso vale para qualquer campo livre sem massa.
   Verificado (≤ 7e-16):
   - na memória EM nula de um escalar carregado sem massa (só $\Omega=A-A^\dagger$);
   - na memória gravitacional de radiação EM.

   Onde falha:
   - **memória linear** (é o valor em $\omega=0$): só é invariante se $e^{i\varphi(0)}=1$; uma rotação de dualidade a
     muda em 59%;
   - **campos massivos:** a invariância sobrevive, mas a redução a dois momentos não. Dois espectros com os mesmos
     momentos de ordem 0, 1 e 2 dão memórias que diferem 1,6%.

---

## 1. Pergunta e hipóteses

- **L12.** Existe uma desigualdade rigorosa entre memória e energia irradiada? Qual a constante ótima, em geral e para
  radiação com $\ell\le L$? Combinada com a lei da área, ela limita a memória de uma binária? Faz sentido testar a lei
  da área ou a energia não gravitacional pela memória?
  - **H12.1** $|D\Delta h|\le4E$, com 4 ótimo.
  - **H12.2** Para $\ell\le L$, $c_L<4$ é um autovalor generalizado e $c_L\to4$.
  - **H12.3** Com a lei da área, $|D\Delta h_\text{nula}|\le c\,(M_B-M_{\rm irr,0})$, com folga moderada nas binárias.
  - **H12.4** Isso permite um teste útil da lei da área.
- **L13.** Que emissões não gravitacionais são invisíveis à memória? O que quebra a degenerescência?
  - **H13.1** As partes $\ell=0,1$ são invisíveis para qualquer velocidade.
  - **H13.2** Histórias com a mesma parte $\ell\ge2$ da fluência total têm memória idêntica.
  - **H13.3** Perfil temporal, velocidade e polarização quebram a degenerescência.
- **L14.** Momentos (memórias superiores) ou janelas: qual base é estável e retém informação?
  - **H14.1** O número de condição dos momentos cresce exponencialmente em $K$ e o das janelas polinomialmente.
  - **H14.2** As janelas retêm mais informação de Fisher.
  - **H14.3** Os momentos dependem da origem do tempo e do início da janela.
- **L15.**
  - **H15.1** A redução de Gram e a invariância por filtros valem para todo campo cujo fluxo é quadrático na radiação.
  - **H15.2** Elas falham para partículas massivas.

## 2. Fundamentação e equações

### 2.1 Desigualdade memória–energia (L12)

Fórmula de Thorne 1992 [E]: $\Delta h^{TT}_{jk}=\frac4D\int\frac{dE}{d\Omega'}\big[\frac{n'_jn'_k}{1-n'\cdot N}\big]^{TT}d\Omega'$.
Contraindo com $\bar m^j\bar m^k$, $\bar m=(e_\theta-ie_\phi)/\sqrt2$, obtém-se $h_+-ih_\times$:

$$D\,\Delta h(N)=4\!\int\!F(n')\,K(n',N)\,d\Omega',\qquad K=\frac{(n'\cdot\bar m)^2}{1-n'\cdot N},\qquad |K|=\frac{1+n'\cdot N}{2}\le1 .$$

Com $N=\hat z$, $K=\tfrac12(1+\cos\theta')e^{-2i\phi'}$, que é suave nas coordenadas da grade. A conferência numérica
contra `memorias.CalculadoraMemoria` (Mitman et al. 2020) está em `resultados/exp28_constantes.txt` (a): 12 matrizes
$B$ aleatórias com $L=2..5$, mais um $N$ genérico, diferença ≤ 9,2e-15. **[D] Mesma normalização e mesmo sinal.**

**Desigualdade geral [D, imediata].** Como $F\ge0$, $|D\Delta h|\le4\int F\sup|K|=4E$. O supremo 4 é atingido no limite
de toda a energia num feixe estreito apontado para $N$, com azimute fixo. Isso equivale ao "da ordem de $4GE/r$" de
jatos ultrarrelativísticos [LP2021].

**Radiação com $2\le\ell\le L$ [D].** Escrevendo $F=\frac1{16\pi}\sum_{jk}B_{jk}Y_j\bar Y_k$ e $E=\mathrm{tr}B/16\pi$:

$$D\Delta h=\sum_{jk}B_{jk}\Gamma_{jk},\quad \Gamma_{jk}=\frac1{4\pi}\!\int\!Y_j\bar Y_kK\,d\Omega,\qquad
c_L=\sup_{B\succeq0}\frac{|D\Delta h|}{E}=16\pi\,\lambda_{\max}\!\Big(\tfrac12(X+X^\dagger)\Big),\ X=\Gamma^T .$$

- Qualquer $B\succeq0$ é realizável: surtos disjuntos somam matrizes de posto 1.
- A fase de $\Delta h$ é livre por rotação em torno de $N$. Conferido: a variação com $\alpha$ é ≤ 6e-15.
- $\Gamma$ só acopla $m_j=m_k+2$. Isso permite um método 1D (integral só em $\theta$, autovalor esparso) até $L=128$.

Para $L=2$ (sympy, `exp28_c2_exato.py`), os autovalores de $16\pi\,\mathrm{Herm}(X)$ são
$\pm\sqrt{30}/6,\pm2/3,0$, logo **$c_2=\sqrt{30}/6=\sqrt{5/6}$**.

**Energia dividida [D].** Na janela de uma binária, a fração $e_2$ da energia está em $\ell=2$ e o resto em $\ell=3..5$.
O máximo com essa restrição é um problema quadrático com duas restrições. Pelo S-lema complexo, a relaxação SDP é exata:

$$c(e_2)=\min_\mu 16\pi\big[\lambda_{\max}(H-\mu P_2)+\mu e_2\big].$$

Conferido pelo primal: a fração e o valor do autovetor ótimo coincidem com o dual (sem aviso, `exp28_folga.py`).

**Lei da área [E: Hawking 1971].**
- Área: $M_f\ge M_{\rm irr,f}\ge M_{\rm irr,0}=\sqrt{\sum_i m_i^2(1+\sqrt{1-\chi_i^2})/2}$.
- Energia na janela: $E_\text{janela}\le 1-E_\text{lig}(x_i)-M_{\rm irr,0}$, com $E_\text{lig}$ 3PN+SO do L00.
- Com o spin final $\chi_f$ medido (aqui, o ajuste NRSur3dq8Remnant): $M_f\ge M_{\rm irr,0}\sqrt{2/(1+\sqrt{1-\chi_f^2})}$.

  Essa é a forma em que a conservação de momento angular entra. Sem $\chi_f$, $J$ não ajuda: o mínimo sobre $J_f$ dá
  $J_f=0$.
- Limite: $|D\Delta h_\text{nula}|\le c\,E_\text{max}$.
- Recíproca: $E_\text{rad}\ge D|\Delta h|/c$.

### 2.2 Canais e velocidade (L13)

Para partículas com velocidade $\beta$ e energia (com a de repouso) $dE/d\Omega'$ [E: Thorne 1992; Segalis & Ori 2001]:
$K_\beta=\beta^2(n'\cdot\bar m)^2/(1-\beta n'\cdot N)$.

Por equivariância sob rotações, uma fluência no multipolo $\ell$ gera memória só no multipolo $\ell$, com coeficiente
$\lambda_\ell(\beta)$. Como não há harmônicos de peso −2 com $\ell<2$, **o núcleo $\ell=0,1$ vale para todo $\beta$** [D;
o caso $\beta=1$ é MW2019 eq. 100].

Além disso, $\beta^2/(1-\beta x)$ cresce com $\beta$, logo $|K_\beta|\le|K_1|\le1$. **A cota $E_x\ge D|\delta h|/4$ vale
para qualquer mistura de canais** [D].

### 2.3 Momentos e janelas (L14)

- Fluxo $F(t)=dm_{20}/dt$: taxa da memória nula no multipolo (2,0), em unidades de deformação/s, com $D=400$ Mpc.
- Coeficientes de Gaunt calculados na grade.
- Momentos: $\mu_n=\int\tau^nF\,dt$, com $\tau=(t-t_\text{ref})/T$ e $T=4{,}04$ s.
- Janelas: $W_k=\int_{s_k}^{T_b}F\,dt$, com cortes $s_k$ uniformes no tempo ou de energia igual (pelo fluxo nominal).
- Operador em $L^2$: linhas $\ell_i(t_j)\sqrt{w_j}$.
- Fisher, modelo 1: ruído independente $\sigma=\varepsilon|\Delta m|$ por medida.
- Fisher, modelo 2: ruído branco comum nas amostras de $F$. A informação retida é a projeção das derivadas no espaço das
  linhas, calculada por QR.

  Esse espaço é o dos polinômios de grau $<K$ para os momentos, qualquer que seja a origem, e o das funções constantes
  por partes para as janelas.

### 2.4 Generalização (L15)

**Proposição [D].** Sejam $\psi_j(u)$ os multipolos em $\mathscr I^+$ de campos livres sem massa, de qualquer spin. Seja

$$O=\int du\sum_{jk}\sum_{a,b\le1}c^{ab}_{jk}(\Omega)\,\partial_u^a\psi_j\,\overline{\partial_u^b\psi_k}.$$

Então $O$ é linear em $C=\int\psi\psi^\dagger$, $A=\int\psi\dot\psi^\dagger$ e $B=\int\dot\psi\dot\psi^\dagger$. Em Fourier,
os termos com $a+b=n$ são momentos de ordem $n$ da matriz espectral $\tilde\psi\tilde\psi^\dagger$. Logo $O$ é invariante por
$\tilde\psi_j\to e^{i\varphi(\omega)}\tilde\psi_j$ (comum a todos os $j$).

- Com $a+b$ arbitrário a invariância continua, mas com mais momentos.
- Campos que não interferem no fluxo (por exemplo, gravitacional + EM: $T_{uu}$ é soma) admitem **um filtro independente
  por campo**.
- Para campos reais o filtro deve ser ímpar, $\varphi(-\omega)=-\varphi(\omega)$. Isso também preserva os termos
  bilineares sem conjugação.

Casos:
- **Escalar carregado sem massa.** A fluência de carga é $Q=-2\,\mathrm{Im}\int\bar\Phi\dot\Phi\,du=i\sum_{jk}\overline{\Omega_{jk}}\,\bar Y_jY_k$:
  depende só de $\Omega$. A memória EM nula (o "kick") é $D^A\!\int E_Adu=4\pi Q+\text{ordinária}$ [E: BG2013], com
  núcleo $\ell=0$ (conservação de carga).
- **Memória de cor (Yang–Mills).** É quadrática no fluxo de cor dos glúons [E: Pate, Raclariu & Strominger 2017], logo é
  do mesmo tipo. Não testei numericamente [H].

## 3. Experimentos (scripts, parâmetros, saídas)

| Script | O que faz | Saída | Tempo |
|---|---|---|---|
| `codigo/exp28_constantes.py` | (a) Thorne × modos; (b) $c_L$, $L$ = 2–32 (2D) e 8–128 (1D, `spherical`); (c) multipolo único; quadrupolo de binária | `resultados/exp28_constantes.{txt,json}` | 28 s |
| `codigo/exp28_c2_exato.py` | $c_2$ exato (sympy) | `resultados/exp28_c2_exato.txt` | 3 s |
| `codigo/exp28_folga.py` | 9 binárias × 5 inclinações × 48 azimutes; nível A janela e total, nível C; energia por $\ell$; $c(e_2)$; lei da área; NRSur3dq8Remnant | `resultados/exp28_folga.{txt,json}` | 20 s |
| `codigo/exp28_figura.py` | figura | `figuras/e28_limite_memoria.png` | — |
| `codigo/exp29_canais.py` | núcleo para $\beta$ = 1, 0,9, 0,5 e 0,1; tabela $\lambda_\ell(\beta)$; exemplo G×N; SNR de memórias lentas (`observaveis.snr2`); $\beta<1$; polarização; razão memória/oscilação | `resultados/exp29_canais.{txt,json}` | 1 s |
| `codigo/exp29_figura.py` | figura | `figuras/e29_canais.png` | — |
| `codigo/exp36_janelas_momentos.py` | sistema A, $[-4;\,0{,}04]$ s, 4096 Hz ($N$ = 16549); condição $K$ = 1–24; reconstrução; Fisher (modelos 1 e 2, passos $h$ e $h/2$); origem e início | `resultados/exp36_janelas_momentos.{txt,json}`, `figuras/e36_janelas_momentos.png` | 21 s |
| `codigo/exp37_outros_campos.py` | escalar carregado (16 modos, $\ell\le3$); EM (15 modos, $\ell\le3$); filtros aleatório, translação e dualidade; espectros massivos | `resultados/exp37_outros_campos.txt` | 3 s |

Todos rodaram com `OMP_NUM_THREADS=1`, um processo, a partir de `codigo/`.

## 4. Resultados

### 4.1 L12 — constantes (`exp28_constantes.txt`, `exp28_c2_exato.txt`)

| $L$ | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 | 64 | 128 | ∞ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $c_L$ | 0,91287 | 1,85166 | 2,23872 | 2,51080 | 2,71462 | 3,00568 | 3,31300 | 3,47542 | 3,73047 | 3,86328 | 3,93112 | 4 |

- **Assintótica.** $L(4-c_L)$ = 7,95, 8,39, 8,62, 8,75 e 8,82 para $L$ = 8, 16, 32, 64 e 128, com expoente local −0,92 →
  −0,991. Logo $4-c_L\simeq a/L$, com $a\approx8{,}9$ (extrapolação linear em $1/L$ dos dois últimos pontos: 8,88).
- **Concordância entre métodos.** O método 1D coincide com o 2D em 10 algarismos para $L$ = 8, 16 e 32.
- **Autovetor ótimo.** Mistura $m$ e $m+2$ no referencial do observador e espalha energia por muitos $\ell$; para $L$
  grande, o peso de $\ell=2$ é pequeno (0,005 em $L=32$).
- **Um só multipolo.** $\ell=2$: 0,913; $\ell=3$: 0,667; $\ell=4$: 0,800; $\ell=6$: 1,058; $\ell=8$: 1,207.
- **Quadrupolo de binária.** Só (2,±2) no referencial da fonte e $B$ diagonal:
  $D\Delta h/E=\sin^2\iota(17+\cos^2\iota)/24$, conferido em 4 inclinações a 1e-10; máximo $17/24=0{,}7083$ em $\iota=90°$.

  É a forma conhecida da memória de ordem dominante [E, Favata 2009], escrita aqui com a energia. Fica em 0,776 de $c_2$.

### 4.2 L12 — folga em binárias (`exp28_folga.txt`)

Razões no observador, máximo em $\phi$ (48 valores). $r=|D\Delta h_\text{nula}|/E_\text{janela}$; $E^\chi_\text{área}$ usa o
$\chi_f$ do ajuste.

| Sistema $(q;\chi_1,\chi_2)$ | $e_2$ | $c(e_2)$ | $E_\text{jan}/E_\text{área}$ ($E^\chi_\text{área}$) | $r$ (90°) | $r/c(e_2)$ (50°/90°) | $r/4$ (90°) | $|D\Delta h|/(c(e_2)E^\chi_\text{área})$ (50°/90°) | $|D\Delta h|/(4E_\text{área})$ (90°) |
|---|---|---|---|---|---|---|---|---|
| (1; 0, 0) | 0,9888 | 1,222 | 0,149 (0,183) | 0,773 | 0,387 / 0,633 | 0,193 | 0,071 / 0,116 | 0,029 |
| A: (1,2; 0,3, −0,2) | 0,9839 | 1,282 | 0,154 (0,193) | 0,777 | 0,370 / 0,606 | 0,194 | 0,072 / 0,117 | 0,030 |
| (2; 0, 0) | 0,9501 | 1,552 | 0,135 (0,165) | 0,742 | 0,285 / 0,478 | 0,186 | 0,047 / 0,079 | 0,025 |
| (4; 0, 0) | 0,8816 | 1,865 | 0,107 (0,126) | 0,674 | 0,209 / 0,361 | 0,169 | 0,026 / 0,046 | 0,018 |
| (8; 0, 0) | 0,8386 | 2,002 | 0,082 (0,092) | 0,628 | 0,180 / 0,314 | 0,157 | 0,017 / 0,029 | 0,013 |
| (1; 0,8, 0,8) | 0,9840 | 1,281 | 0,230 (0,341) | 0,827 | 0,400 / 0,645 | 0,207 | 0,136 / 0,220 | 0,047 |
| (1; −0,8, −0,8) | 0,9881 | 1,231 | 0,077 (0,081) | 0,737 | 0,365 / 0,599 | 0,184 | 0,030 / 0,049 | 0,014 |
| (3; 0,6, −0,4) | 0,8856 | 1,851 | 0,152 (0,232) | 0,725 | 0,231 / 0,392 | 0,181 | 0,054 / 0,091 | 0,028 |
| (6; 0,8, 0) | 0,7953 | 2,113 | 0,128 (0,292) | 0,669 | 0,182 / 0,317 | 0,167 | 0,053 / 0,092 | 0,021 |

- **Saturação de cada desigualdade.**
  - De lado, $r$ = 0,63–0,83, isto é, 0,89–1,17 vezes a constante do quadrupolo (17/24); em $q=1$ ela a excede
    (0,77–0,83 > 0,708), por causa das ordens PN e da fusão.
  - Usa 31–65% de $c(e_2)$ e 16–21% de 4.
  - A lei da área usa 8–23% (8–34% com $\chi_f$).
- **Face a face** ($\iota=0$): $r\le0{,}005$, porque a memória vai com $\sin^2\iota$.
- **RN contra quadrático.** A memória de RN (nível C) é 1–4% maior que a nula quadrática ($r_C/r_A$ de 1,008 a 1,043 para $\iota\ge30°$),
  ainda muito abaixo do limite. A cota se aplica à parte nula; a correção cúbica não a ameaça.
- **Memória total** (desde $x=0$; $E_\text{tot}=1-M_f$): $|D\Delta h_\text{tot}|/E_\text{tot}$ ≈ 0,64–0,82 (90°). Contra
  $c(e_2)(1-M_{\rm irr,0}\cdot\text{fator}(\chi_f))$ ela usa 3,6–22,7%.

### 4.3 L12 — o teste da lei da área faz sentido?

**[D, quantitativo] Só como teste grosseiro.**

No sistema A ($\iota=50°$), a memória da RG está em **7,2%** do limite afiado (com $c(e_2)$ e $\chi_f$) e em **1,8%** do
limite simples (4, só a área).
- Uma violação só seria detectável se a memória observada passasse do limite, isto é, se fosse 14 ou 55 vezes a da RG.
- Com SNR da memória nula de 8,6 (ET) ou 34 (CE) (L00), a memória é medida a ~12% ou ~3%.

O teste da lei da área pela memória exclui, portanto, só "memórias 14–55 vezes maiores que a da RG". O teste de
consistência (memória medida contra a prevista pelo fluxo das ondas oscilatórias) é sensível a desvios de ~3%. Ele já
contém a lei da área implicitamente, porque o fluxo das ondas mede $E_\text{rad}$.

O que a desigualdade dá de novo e sem modelo:
1. **Cota inferior da energia irradiada.** $E_\text{rad}\ge D|\Delta h|/c(e_2)$ dá 37% do $E_\text{janela}$ verdadeiro
   em A ($\iota=50°$) e 61% de lado. Com 4 no lugar de $c(e_2)$: 12% e 19%. Exige $D$, que é degenerado com $\iota$.
2. **Cota inferior de energia não gravitacional.** $E_x\ge D|\delta h|/4$ para qualquer excesso de memória $\delta h$ sobre
   a previsão pelo fluxo das ondas. Vale para qualquer canal nulo ou massivo (§2.2). No exemplo do exp29: cota 0,0027
   contra 0,015 verdadeiro (fator 0,18).

### 4.4 L13 (`exp29_canais.txt`)

**Núcleo.** Fluências $\ell=0+\ell=1$ aleatórias dão $|D\Delta h|/|\text{coef}|$ ≤ 1,9e-15 ($\beta=1$), 6,5e-16 (0,9),
3,1e-16 (0,5) e 1,2e-17 (0,1).

**Transferência $\lambda_\ell(\beta)/\lambda_\ell(1)$** (excertos):

| $\ell$ | β=0,99 | 0,9 | 0,5 | 0,1 |
|---|---|---|---|---|
| 2 | 0,971 | 0,758 | 0,208 | 8,0e-3 |
| 4 | 0,913 | 0,472 | 0,0276 | 3,8e-5 |
| 8 | 0,748 | 0,138 | 3,1e-4 | 5,3e-10 |

- Conferida pela integração 2D direta do núcleo massivo: 0,2078164743 nos dois métodos ($\ell=2$, $\beta=0{,}5$).
- **Limite $\beta\to0$:** $\lambda_\ell/\lambda_\ell(1)\to c_\ell\beta^\ell$, com $c_\ell$ = 0,8000, 0,5714, 0,3810, 0,2424 para
  $\ell$ = 2–5 (numericamente 4/5, 4/7, 8/21, 8/33).
- **Leitura:** matéria lenta só "vê" o quadrupolo do fluxo de momento.

**Exemplo explícito.** São duas histórias:
- **G**: só ondas (2,±2), energia $E=0{,}05$.
- **N**: ondas com $0{,}7E$ mais neutrinos com $0{,}3E$, numa distribuição angular igual à das ondas — um jato bipolar
  largo, com razão polo/equador 7,96 — mais um termo dipolar de um lado só ($d=0{,}084$; positividade conferida, mínimo
  3,6e-4).

Resultados:
- A memória nula difere ≤ **1,3e-14** no céu inteiro ($\ell\le8$).
- Os neutrinos levam momento 1,26e-3, o que dá recuo $v=1{,}26\times10^{-3}$. A memória ordinária do recuo é ~$2v^2=3$e-6,
  contra 3,5e-2 da nula: a degenerescência só cai em $O(v^2)$, como em MW2019 eq. 101.
- As massas finais e as memórias de deslocamento são iguais; as histórias diferem.

**Quebras.**
1. **Tempo.** SNR de uma memória com subida exponencial de tempo $\tau$, relativa ao degrau rápido:

   | Detector | $\tau$ = 10 ms | 0,1 s | 1 s |
   |---|---|---|---|
   | aLIGO | 0,31 | 0,036 | 0,004 |
   | CE | 0,52 | 0,069 | 0,007 |

   Neutrinos emitidos em ~1 s (supernova) praticamente não aparecem na banda. Se tiverem o mesmo perfil temporal das ondas,
   a série temporal da memória é idêntica (a memória nula é a fluência acumulada). O tempo só quebra a degenerescência
   quando os perfis diferem.
2. **Velocidade.** Com a mesma fluência emitida com $\beta<1$, a memória de lado cai de fatores 0,9915, 0,928 e 0,763
   ($\beta$ = 0,99, 0,9, 0,5). Em $\iota=30°$ as razões são diferentes (0,9908, 0,924, 0,761): o padrão angular muda.
   - A memória de partículas massivas chega com a frente de luz do evento de emissão, não com as partículas [D, linearizada].
   - A velocidade entra pelo núcleo angular, não pelo atraso.
3. **Polarização.** A memória nula de qualquer canal é de paridade elétrica. O que separa os canais é a orientação.
   - Jato estreito (meia abertura 15°) com eixo inclinado $\alpha$, fora do plano $(z,N)$, $\iota=60°$: o ângulo de
     polarização da memória total é 0°, 10,6°, 20,9° e 43,4° para $\alpha$ = 0, 15, 30 e 60°. As ondas sozinhas
     preveem 0°.
   - Isso é o identificador de canal de [CBV2024], aqui na forma "ângulo de polarização da memória contra o previsto
     pelo fluxo das ondas".
   - Exige uma rede de detectores: um só detector mede $F_+h_++F_\times h_\times$.
4. **Razão memória/oscilação.** O fluxo das ondas de N prevê 0,0248; a memória observada é 0,0354, um excesso de 43%.
   É o teste de "excesso de memória".

**O que um teste de excesso de memória pode e não pode detectar [D].**
- **Pode:** a parte $\ell\ge2$ da fluência não gravitacional, pesada por $\lambda_\ell(\beta)$, na banda do detector (escalas
  de ms).
- **Não pode:**
  - emissão isotrópica ou dipolar (só via $O(v^2)$ do recuo);
  - emissão lenta (≳0,1 s em CE);
  - emissão não relativística de alto $\ell$.

### 4.5 L14 (`exp36_janelas_momentos.txt`, `figuras/e36_janelas_momentos.png`)

- **Conferência.** $\int F$ coincide com o deslocamento (2,0) de janela de `observaveis` a 5,8e-7 (interpolação spline
  numa grade de 4096 Hz). 50% da memória da janela acumula no último 0,7 ms antes do pico; 90% até 5,4 ms depois.
- **Número de condição** (linhas normalizadas):

  | $K$ | mom. (fusão) | mom. (início) | mom. (meio) | jan. uniformes | jan. de energia igual |
  |---|---|---|---|---|---|
  | 4 | 82 | 86 | 4,8 | 5,4 | 7,8 |
  | 8 | 7,0e4 | 7,7e4 | 126 | 11,6 | 20,5 |
  | 12 | 6,7e7 | 7,8e7 | 3,7e3 | 17,9 | 32,6 |
  | 24 | 3,1e15 | 5,3e15 | 1,2e8 | 37 | 70 |

  - Ajustes: $\ln\text{cond}\approx1{,}62K$ (fator 5,04 por momento), $1{,}64K$ (início) e $0{,}85K$ (meio: fator 2,35).
  - Janelas: $\propto K^{1{,}08}$ (uniformes) e $K^{1{,}21}$ (energia igual).
  - **H14.1 confirmada.**
- **Reconstrução de $m(t)$.** Erro máximo / $\Delta m$, mediana de 20 realizações:
  - sem ruído: momentos 0,25 em $K=20$, porque polinômios não resolvem a fusão; janelas uniformes 0,50; janelas de
    energia igual 0,037;
  - com $\varepsilon=10^{-3}$: momentos 2,3e3 ($K=12$) e 2,1e9 ($K=20$); janelas de energia igual 0,063 ($K=12$) e 0,038
    ($K=20$).
- **Fisher, modelo 1.** Ruído igual por medida, 6 parâmetros livres; $\sigma/\varepsilon$ com $K=12$:

  | Funcional | $\ln M$ | $q$ | $t_0$ (s) |
  |---|---|---|---|
  | momentos (fusão) | 6,8e6 | 5,7e7 | 2,8e3 |
  | momentos (início) | 9,7e5 | — | — |
  | janelas uniformes | 1,9e4 | — | — |
  | janelas de energia igual | 15,1 | 423 | 0,085 |

  - Estabilidade: os valores mudam ≤ 2,7e-3 com o passo $h/2$.
  - **H14.2 confirmada:** ganho de 4 a 6 ordens de grandeza.
  - Com só $(\ln A,\ln M,t_0)$ e $K=8$: momentos 233, janelas de energia igual 4,4.
- **Fisher, modelo 2** (fração retida $\sigma_\text{série}/\sigma_K$):
  - momentos: 1e-5 a 1e-4 com $K=6$, 4e-4 a 6e-3 com $K=12$–$32$, 7e-3 a 5,5e-2 com $K=64$. São idênticos a $K$
    coeficientes de Legendre.
  - **Ortogonalizar os momentos resolve o condicionamento, não a falta de informação.**
  - janelas de energia igual: 0,18–0,43 com $K=6$, 0,54–0,82 com $K=12$, 0,93–0,99 com $K=64$;
  - janelas uniformes: ≤ 4,1e-3 até $K=64$.
- **Origem e início.**
  - Com origem na fusão, $\mu_n/\Delta m$ = 1, −0,033, 0,015, −0,0097, …: os momentos superiores são pequenos e dominados
    pela inspiral.
  - Com origem no início, ≈ 0,96, 0,93, …: quase só $\Delta m$.
  - Mudar o início de −4 s para −3 s muda os momentos $n$ = 1–9 em 21%, 41%, 56%, …, 92%. As janelas de energia igual
    não mudam: o primeiro corte está em −0,254 s; só $W_0$ muda, 0,8%.
  - $t_0$ livre contra fixo, $K=12$: momentos (fusão) $\sigma_{\ln M}$ 6,8e6 → 3,3e5 (fator 21); janelas 15,1 → 15,0.
  - **H14.3 confirmada.**

### 4.6 L15 (`exp37_outros_campos.txt`)

- **Escalar carregado.**
  - A fórmula $Q(\Omega)$ coincide com o cálculo no tempo a 1,2e-15.
  - Sob um filtro de fase comum aleatório com dispersão forte (sobreposição das histórias 0,026), a memória EM nula muda
    7,2e-16 e a gravitacional 1,9e-16.
- **Radiação EM.** Memória gravitacional invariante (≤ 6e-16) sob filtro aleatório, translação e dualidade. A memória EM
  linear $\int a\,du$:
  - não muda sob translação (2e-15);
  - muda 1,7 (relativo) sob o filtro aleatório e 0,59 sob a dualidade constante 0,6.
- **Massivo.** Duas distribuições de quanta, uma linha larga em $\omega=1{,}6$ e duas linhas em 1,15 e 1,787, têm os
  mesmos $\int S$, $\langle\omega\rangle=1{,}6166$ e $\langle\omega^2\rangle=2{,}6931$, mas memória/E de 0,5178 e 0,5096
  (1,6%). A redução a momentos finitos falha. Como o filtro de fase não muda $S(\omega)$, a invariância continua.

## 5. Tentativas de refutação e alternativas

1. **Convenção da fórmula de Thorne.** Comparada com a de modos, que tem outra origem (leis de balanço de Mitman et al.).
   Testei 12 matrizes $B$ aleatórias e um $N$ genérico numa grade girada. Se o sinal estivesse trocado, $c_L$ não mudaria,
   mas a interpretação "memória positiva de lado" sim. Coincidem.
2. **$c_L$ por dois métodos independentes** (2D com `harmonicos`, 1D com `spherical`) e forma fechada para $L=2$.
   - Precisão de `harmonicos.sYlm` em $\ell$ alto: erro de normalização de 2e-8 em $\ell=32$ e 1,3e-3 em $\ell=48$.
     Por isso usei `spherical` acima de 32.
   - A fase $\alpha$ não muda $c_L$ (≤ 6e-15).
3. **Caso restrito inicial errado.** Minha primeira versão de "só (2,±2)" estava no referencial do observador e deu 0,
   porque $\Gamma$ só acopla $m\to m+2$. O caso certo é no referencial da fonte. Corrigido: dá 17/24.
4. **H12.4 (teste útil da lei da área): refutada na forma ingênua.** Cinco formulações:
   - (i) 4 e só a área: memória em 1,3–4,7% do limite;
   - (ii) $c_5$;
   - (iii) $c(e_2)$ com a divisão de energia medida;
   - (iv) área com $\chi_f$ (conservação de $J$ via o remanescente);
   - (v) memória total contra $E_\text{tot}$ desde $x=0$;
   - (vi) constante do quadrupolo 17/24. É afiada, mas depende de modelo e é violada pela própria RG em $q=1$ (0,77 > 0,708).
     Não serve como cota.

   Nenhuma leva a folga abaixo de ~4,5 vezes. O melhor caso é 0,22 ($q=1$, $\chi=0{,}8$, de lado).
5. **O dual do S-lema** foi conferido pelo autovetor primal. Para $e_2=1$ o mínimo fica no infinito; com a caixa $|\mu|\le20$
   ele dá 0,9150 contra o exato 0,9129. Isso não afeta as binárias ($e_2\le0{,}989$).
6. **L14, Fisher mal condicionado.**
   - A primeira versão invertia $J^TJ$ com cond ~1e16 e dava zeros. Refeito por QR, com o menor valor singular relativo
     reportado e variação com passo $h/2$ ≤ 3e-3.
   - A direção $q$–$\chi_1$–$\chi_2$ é quase degenerada (sv relativo 7e-4 nas janelas), como no L01.
   - Também troquei a métrica de reconstrução: o erro $L^2$ relativo é dominado pela parte em que $m\approx0$. Uso o erro
     máximo em unidades de $\Delta m$.
7. **Justiça da comparação momentos × janelas.**
   - Três origens para os momentos e normalização das linhas.
   - Base de Legendre: mesmo espaço de linhas. No modelo 2 a informação é a mesma, então o problema dos momentos é
     informação, não só condicionamento.
   - As janelas de energia igual usam o fluxo nominal para escolher os cortes; é um desenho adaptativo. As janelas
     uniformes, não adaptadas, são tão ruins quanto os momentos.
8. **L13, positividade e realizabilidade.** A fluência dos neutrinos é ≥ 3,6e-4 em toda parte. A fluência das ondas vem de
   modos reais. O excesso de energia inferido pela cota (0,18 do verdadeiro) é coerente com $r/4$.
9. **L15, sinal da derivada.** A primeira versão de `dd` tinha o sinal trocado e a fórmula $Q(\Omega)$ com índices trocados
   (erro de 0,41). Corrigido: 1,2e-15. A invariância já valia antes, porque o erro era comum.

## 6. Contraexemplos e limitações

- **Ordem.** $c_L$ e as cotas valem na ordem quadrática (memória nula de Thorne/Christodoulou). A memória de RN excede a
  quadrática em 1–4%. Uma cota rigorosa da memória total precisaria da ordem cúbica (sem prova aqui).
- **$E_\text{lig}$.** Vem do PN 3PN+SO (erro ≤ 1,8e-5, L00). $M_f$ e $E_\text{janela}$ têm incerteza de modelo ~1e-4 (L00).
- **Áreas iniciais.** A lei da área usa as áreas de Kerr isolado. Em $t_i$ os buracos já interagem (marés, absorção no
  horizonte); esse erro não foi estimado.
- **Escopo das binárias.** Só NRHybSur3dq8_CCE: spins alinhados, $\ell\le5$ nos modos de entrada e $q\le8$. Precessão e
  excentricidade não foram testadas.
- **Degenerescência $D$–$\iota$.** O teste da área e a cota de energia exigem $D$, fortemente correlacionado com $\iota$.
  Não propaguei essa incerteza.
- **L13.**
  - As fluências são "de brinquedo" (formas fixadas), não simulações de supernova.
  - A SNR é de $h_+$ ótimo (sem padrões de antena).
  - O exemplo G×N tem memória de spin nula nas duas histórias, porque $A=0$. Com ondas que levam momento angular, a
    memória de spin escala com $(1-\varepsilon)$ e quebraria a degenerescência (não calculado).
- **L14.**
  - Os modelos de ruído são de brinquedo: ruído branco no fluxo, ou independente por medida. Um detector real mede
    $F_+h_++F_\times h_\times$ com ruído colorido (L05–L07).
  - Só um sistema e só o multipolo (2,0).
  - Os cortes de energia igual dependem do fluxo nominal.
  - Não testei os "momentos de Cauchy" de [GM2024] (limite superior variável), que são intermediários entre momentos e
    janelas.
- **L15.** A afirmação sobre Yang–Mills não foi testada. Para campos massivos, a afirmação "a memória depende só da
  distribuição assintótica de momento" é [E] para partículas livres (Thorne 1992), mas não verifiquei para campos massivos
  autointeragentes.

## 7. Literatura e originalidade

**Como conferi.** WebSearch, nas consultas:
- "gravitational wave memory upper bound radiated energy";
- "memory Hawking area theorem bound";
- "memory relativistic ejecta antenna pattern";
- "maximum memory for given radiated energy";
- "color memory / charged massless scalar memory";
- "higher memory effects moments window".

Também usei WebFetch de arXiv:1607.03122 e de arXiv:2312.02295v3. A API do arXiv com frases entre aspas devolveu vazio
ou travou; a consulta foi interrompida e não é base de nenhuma afirmação.

**Encontrado.**
- **Desigualdade simples.**
  - O "da ordem de $4GE/r$" para jatos ultrarrelativísticos aparece em Leiderschneider & Piran, PRD 104, 104002 (2021),
    arXiv:2107.12418 [LP2021].
  - O padrão angular de Segalis & Ori, PRD 64, 064018 (2001), gr-qc/0101117, já contém o núcleo massivo.
  - $|D\Delta h|\le4E$ é imediato da fórmula de Thorne 1992; trato como [E/elementar].
- **Cotas por entropia.** Bousso, Halpern & Koeller, PRD 94, 064047 (2016) dão cotas por entropia, quadráticas na *news*,
  que não são a desigualdade memória–energia.
- **Lei da área.** Mädler & Winicour 2019 [MW2019] limitam a memória **ordinária** de boost pela lei da área.
- **Excesso de memória e canais.**
  - O teste de geração de memória com binárias é de Yang & Martynov, PRL 121, 071102 (2018).
  - Neutrinos: Epstein 1978; Bieri & Garfinkle 2015 [BG2014nu]; [CBV2024], com a polarização como identificador de canal.
- **Memórias superiores.** [SGN2024] e Grant & Mitman, CQG 41, 175003 (2024) [GM2024]. Usam momentos de Cauchy com
  referência $\tilde u$ arbitrária ("all results hold regardless of the chosen value of $\tilde u$") e notam que da
  memória só se recupera a deformação a menos de constante.
- **Outros campos.** Memória de cor: Pate, Raclariu & Strominger, PRL 119, 261602 (2017). Memória EM: [BG2013].

**Não encontrei.** As afirmações abaixo são "não encontradas na busca acima", não "novas":
- a constante ótima para radiação com $\ell\le L$ ($c_2=\sqrt{30}/6$, $c_L\to4$ como $\sim8{,}9/L$);
- a versão com divisão de energia $c(e_2)$;
- a cota da memória **nula** de uma binária pela lei da área, com a folga medida em RN;
- a cota $E_x\ge D|\delta h|/4$ para qualquer $\beta$;
- os coeficientes $\lambda_\ell(\beta)$ por multipolo e o limite $c_\ell\beta^\ell$;
- a comparação quantitativa momentos × janelas: condição, Fisher e sensibilidade ao início;
- a proposição geral de L15 com filtros por campo e a falha só da redução (não da invariância) no caso massivo.

São todas derivações elementares. O valor está em fechar as lacunas listadas na revisão R5, não em técnica nova.

## 8. Próximos experimentos

1. Cota na ordem cúbica (memória de RN contra $c_L$) e prova ou contraexemplo de que a correção é sempre ≤ 5%.
2. Propagar a degenerescência $D$–$\iota$ (posterior da parte oscilatória) na cota $E_\text{rad}\ge D|\Delta h|/c(e_2)$.
3. Repetir a folga com NRSur7dq4 (precessão) e SEOBNRv5EHM (excentricidade); o $e_2$ menor eleva $c(e_2)$.
4. L13 com fluências de simulações de supernova (por exemplo, as séries públicas de CBV2024) e padrões de antena de uma
   rede. Ângulo de polarização mínimo detectável contra a SNR.
5. L14 com momentos de Cauchy [GM2024], ruído colorido no detector e memória medida como série $F_+h_++F_\times h_\times$.
   Desenho ótimo de cortes sem conhecer o fluxo, por exemplo cortes em frequência (ligação com L03/L04).
6. L15: verificação numérica para a memória de cor (Yang–Mills linearizado + termo quadrático).

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H12.1 | $|D\Delta h|\le4E_\text{rad}$, com 4 ótimo (supremo, não atingido) | confirmada matematicamente | §2.1; $|K|\le1$; $c_L\to4$ (exp28_constantes) |
| H12.2 | Para $\ell\le L$, $c_L$ é autovalor de Gram; $c_2=\sqrt{30}/6$; $4-c_L\sim8{,}9/L$ | $c_2$ e a caracterização: confirmadas matematicamente; assintótica: confirmada numericamente | exp28_c2_exato; exp28_constantes (b), (b2) |
| H12.2b | Com fração $e_2$ em $\ell=2$, o limite exato é o dual do S-lema e cresce rápido ($c$ = 1,20 em $e_2$ = 0,99) | confirmada numericamente (dual = primal) | exp28_folga |
| H12.3 | Lei da área + $c(e_2)$ limitam a memória nula de binárias, com folga | confirmada numericamente | memória em 3–22% do limite (exp28_folga) |
| H12.4 | O limite permite um teste útil da lei da área | refutada (só exclui memórias ≥ 4,5–77 vezes a da RG; o teste de consistência é mais forte) | §4.3 |
| H12.5 | Cota sem modelo da energia não gravitacional: $E_x\ge D|\delta h|/4$ para todo $\beta$ | confirmada matematicamente | §2.2 (monotonia em $\beta$); exp29 (c-iv) |
| H13.1 | O núcleo $\ell=0,1$ vale para qualquer velocidade | confirmada matematicamente (equivariância) e numericamente (≤ 2e-15) | exp29 (a) |
| H13.2 | Mesma parte $\ell\ge2$ da fluência total ⇒ mesma memória nula, inclusive com jato de neutrinos e recuo | confirmada numericamente (1,3e-14), quebrada só em $O(v^2)$ | exp29 (b) |
| H13.3 | Tempo, velocidade, polarização e razão memória/oscilação quebram a degenerescência | confirmada numericamente (com as ressalvas: o tempo só se os perfis diferem; a polarização só se as orientações diferem) | exp29 (c) |
| H13.4 | $\lambda_\ell(\beta)/\lambda_\ell(1)\to c_\ell\beta^\ell$ ($c_2=4/5$, $c_3=4/7$, $c_4=8/21$, $c_5=8/33$) | confirmada numericamente (forma fechada não demonstrada) | exp29 (a) |
| H14.1 | Condição dos momentos exponencial em $K$; das janelas polinomial | confirmada numericamente | exp36 (b): ×5,0 (×2,35 com origem no meio) contra $K^{1,1}$–$K^{1,2}$ |
| H14.2 | Janelas retêm mais informação de Fisher que momentos | confirmada numericamente para janelas adaptadas; refutada para janelas uniformes no tempo | exp36 (d) |
| H14.3 | Os momentos dependem da origem do tempo e do início da janela; as janelas não | confirmada numericamente | exp36 (e): 21–92%; $t_0$ fator 21 |
| H14.4 | Ortogonalizar os momentos (Legendre) resolve o problema | refutada: resolve o condicionamento, não a informação (modelo 2: mesma informação) | exp36 (d) modelo 2 |
| H15.1 | Redução e invariância valem para qualquer fluxo sesquilinear local de campos sem massa; um filtro por campo que não interfere | confirmada matematicamente (proposição §2.4) e numericamente (escalar carregado, EM: ≤ 7e-16) | exp37 (a), (b) |
| H15.2 | Para memória linear, só filtros com $e^{i\varphi(0)}=1$ | confirmada matematicamente e numericamente | exp37 (b): dualidade muda 59% |
| H15.3 | Partículas massivas: a redução a $(B,A)$ falha, a invariância por filtros sobrevive | confirmada numericamente (1,6%) | exp37 (c) |
| H15.4 | A memória de cor de Yang–Mills é do mesmo tipo | não testada | — |

## Referências usadas aqui (além de `referencias.md`)

- **[LP2021]** O. Leiderschneider, T. Piran, "Gravitational radiation from accelerating jets", PRD 104, 104002 (2021);
  arXiv:2107.12418. Conferência: WebSearch (resumo: sinal de memória "of order 4GE/r").
- **[SO2001]** A. Segalis, A. Ori, "Emission of gravitational radiation from ultrarelativistic sources", PRD 64, 064018
  (2001); gr-qc/0101117. Conferência: WebSearch.
- **[BHK2016]** R. Bousso, I. Halpern, J. Koeller, "Information content of gravitational radiation and the vacuum",
  PRD 94, 064047 (2016); arXiv:1607.03122. Conferência: WebFetch do resumo.
- **[PRS2017]** M. Pate, A.-M. Raclariu, A. Strominger, "Color memory", PRL 119, 261602 (2017); arXiv:1707.08016.
  Conferência: WebSearch.
- **[YM2018]** H. Yang, D. Martynov, "Testing gravitational memory generation with compact binary mergers", PRL 121,
  071102 (2018); arXiv:1803.02429. Conferência: WebSearch.
- **[GM2024]** Grant & Mitman (já em `referencias.md`). Conferência adicional: WebFetch de arXiv:2312.02295v3 (momentos
  de Cauchy, referência $\tilde u$ arbitrária).
- Hawking, "Gravitational radiation from colliding black holes", PRL 26, 1344 (1971): lei da área e eficiência máxima.
  Citado de conhecimento prévio, não reconferido nesta busca.
