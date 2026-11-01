# L03 e L04 — Janelas múltiplas, a curva de energia de ligação e o desenho ótimo de janelas (agente D2)

Modelo: NRHybSur3dq8_CCE, nível A (memórias nulas pelo fluxo dos modos oscilatórios), deslocamento **de janela**,
infraestrutura `codigo/observaveis.py` (L00). Janelas $[t_i(f),\text{fim}]$ com $t_i(f)$ o instante exato em que a
frequência do modo (2,2) vale $f$; bandas $[f_a,f_b]$ = diferença de duas janelas. Sistema de referência A (exp07):
$M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, $D=400$ Mpc, $\iota=50^\circ$.

Rótulos: **[E]** estabelecido (com referência), **[D]** derivado ou verificado aqui, **[H]** hipótese, **[S]** especulação.
Todo número citado vem de um arquivo em `resultados/` (indicado) produzido pelos scripts `codigo/exp20_*`–`exp23_*`.

## Resumo

1. **Fatoração exata da memória de banda** [D, analítico; conferido]. Com janelas definidas pela frequência,
   $dm/dx=-\alpha(x)E_b'(x)$ (deslocamento) e $-\beta(x)x^{-3/2}E_b'(x)$ (spin, pela primeira lei $dJ=dE/\Omega$).
   - $\alpha$ e $\beta$ são razões taxa/fluxo que só dependem das amplitudes relativas dos modos.
   - **O fluxo $F(x)$ e suas caudas cancelam**; só a absorção no horizonte sobra.
   - A memória de banda é a integral de $E_b$ pesada pela distribuição angular dos fluxos, e não "$\Delta E_b$" puro: a
     correção vem em 1PN.
   - Conferências independentes:
     - $\alpha_2$ e $\alpha_4$ (amplitudes ABFO + Gaunt) reproduzem exatamente os coeficientes 1PN e 1,5PN SO de
       Cunningham et al. 2025 ($-1051/2016+71\nu/24$; $5s/3+99\delta\sigma/64$);
     - $\int\alpha E_b'$ reproduz o $H_{20}$ deles;
     - $\beta_3$ reproduz Nichols 2017 na ordem dominante e o modo (3,0) de Blanchet 2024 em 1PN;
     - $J(x)$ pela primeira lei coincide exatamente com o de Blanchet até 3PN.
   - Deduzido aqui: a série de spin de banda
     $S_{30}\propto\nu x^{-1/2}\{1+(7529/4536-68\nu/27)x-(415s/54+3575\delta\sigma/864)x^{3/2}\}$. O SO não tem
     conferência independente.
2. **Contra o substituto** [numérico]. Sem spin, o erro PN da banda cai ordem a ordem até 1,2e-5 (3,5PN, $Mf$ 0,002–0,003),
   e 1PN = 1,5PN exatamente (a cauda cancela). Com spins satura em ~1e-3. A decomposição mostra que o patamar é da
   **energia** irradiada do substituto contra a $E_b$ PN; $\alpha$ concorda a ~1e-4.
3. **O que cada ordem acrescenta** [D + numérico]. Posto do jacobiano das bandas da inspiral (deslocamento + spin):
   **2 (N) → 4 (1PN) → 6 (1,5PN)**, conferido no modelo PN (zeros numéricos de 1e-12 a 1e-19).
   - N: $\mathcal M^{5/3}/D$ e $\iota$;
   - 1PN: $M$ e $\nu$ (dois números, não um; H03.4 refutada na forma ingênua);
   - 1,5PN: duas combinações SO distintas ($16s/3+419\delta\sigma/160$ e $415s/54+3575\delta\sigma/864$);
   - 2PN: nenhum parâmetro novo.
4. **Janelas** [numérico]. Cada janela nova acrescenta **dois** números até saturar:
   - T0 (quatro memórias): 4 → 6;
   - O0 (deslocamento + spin): 2 → 4 → 6, com $\sigma_6$ = 1,1e-6 em $K=3$.

   A função de janela contínua (49 janelas) não acrescenta direções: o espectro só cresce como $\sqrt K$ (T0:
   $\sigma_6/\sqrt K$ = 3,7e-4 com $K=2$ e 2,4e-4 com $K=49$).
5. **Família** [numérico].
   - Com as quatro memórias, a família aproximada **não encolhe** de $K=2$ para $K=4$: o resíduo mínimo cresce ~linearmente
     com $|q_B-q_A|$, com inclinação 5,4e-3 → 6,3e-3, e a faixa com $\max|r|<10^{-3}$ é $q_B\in[1;1{,}3]$ nos três casos.
   - No conjunto mensurável, o resíduo com três janelas é 2e-6 a 1e-5 em $q_B\in[1;1{,}6]$, e com quatro, 5e-6 a 3e-5:
     encolhe, mas fica muito abaixo de qualquer precisão realista.
6. **Desenho ótimo** [numérico]. Com o ruído de CE (erro 1/SNR por banda, ou bandas correlacionadas):
   - **duas ou três bandas bastam**: em A, $D$ = 8,2 → 11,2–11,5 → 11,6–12,1 (1, 2, 3 bandas); com 4 a 6, ≤ +0,04;
   - o corte ótimo de $K=2$ cai no pico ($0{,}9\,f_{\rm pico}$, a borda permitida) em todas as fontes;
   - o ganho é quase todo na escala de massa ($\sigma_{\ln M}$: 0,80 → 0,28 do prior); $q$ e os spins ficam no prior;
   - o critério E é degenerado ($\lambda_{\min}\le9\times10^{-4}$).

   **Universalidade em $Mf$:** exata sem detector (A, $M=30$, $M=150$: cortes idênticos e $D$ igual a 5e-4), quebrada pelo ruído
   (o 2º corte vai de $Mf$ = 0,023 a 0,036 entre $M$ = 30 e 150, isto é, $f_{\rm corte}\propto M^{-0{,}72}$).
7. **Parte nula da CM de banda** [numérico]. Não é zero no substituto (1–6% na inspiral), mas também não é termo de
   borda (hipótese refutada). Ela é $\propto\Delta(Mf)$, com um salto em $Mf\approx0{,}006$ [H: artefato de
   referencial ou de hibridização do substituto].

---

## 1. Pergunta e hipóteses

**L03.** O que exatamente uma segunda (terceira, …) janela acrescenta? A memória acumulada numa banda de frequência é a
energia e o momento angular irradiados nela, isto é, diferenças de $E_b(f)$ e $L(f)$?

**L04.** Que fronteiras de janelas maximizam a identificabilidade? Quantas bastam? O ótimo é universal em $Mf$?

Hipóteses (status na seção 9):
- **H03.1** [09] Com janelas definidas por frequência, a memória de uma banda é uma diferença de funções da energia de
  ligação $E_b(x)$ e do momento angular orbital $J(x)$, ligadas pela primeira lei $dE=\Omega\,dJ$.
- **H03.2** Primeira lei modo a modo: $dE_{\ell m}/dJ_{\ell m}=\omega_{\ell m}/m$.
- **H03.3** [09] Na ordem dominante as bandas só veem $\mathcal M^{5/3}/D$ (e $\iota$ pelos fatores angulares).
- **H03.4** [09] $\eta$ entra em 1PN e a combinação spin-órbita em 1,5PN (um número por ordem).
- **H03.5** [09] Cada janela extra acrescenta cerca de dois números, não quatro.
- **H03.6** A família aproximada de binárias com as mesmas memórias em $K$ janelas encolhe com $K$.
- **H03.7** A memória de banda do substituto concorda com a previsão PN, e o erro cai ordem a ordem.
- **H03.8** A parte nula da memória de CM numa banda da inspiral é um termo de borda (e não zero).
- **H03.9** A razão $\pi f\,dS/dh$ entre as memórias de banda de spin e de deslocamento mede $\iota$ sem depender de
  $M$ e $D$ (teste da primeira lei com a memória).
- **H04.1** [09] Duas janelas bastam para tornar o mapa localmente injetivo (posto 6).
- **H04.2** [09] As fronteiras ótimas são universais em $Mf$ (escalam como $1/M$ em Hz).
- **H04.3** Com o ruído realista (CE/ET), mais bandas não acrescentam informação além da janela única.

## 2. Fundamentação e equações

### 2.1 Função de janela e sua derivada [D]

Seja $m_k(f)$ a memória de tipo $k$ acumulada de $t(f)$ ao fim (fusão e toque incluídos), $x=(\pi Mf)^{2/3}$
($f$ = frequência de onda do (2,2), $\Omega=\pi f$). Por definição $dm_k/df=-\dot m_k(t(f))\,dt/df$, e a memória da
banda é $m_k(f_a)-m_k(f_b)$. Todas as memórias nulas são formas bilineares em $(h,\dot h)$ (em `memorias.py`: lineares
nas matrizes de Gram $B=\int\dot h\dot h^\dagger$ e $A=\int h\dot h^\dagger$), e por isso **aditivas** em bandas.

Numa órbita circular adiabática $h_{\ell m}=a_{\ell m}(x)\,e^{-im\psi}$ e $\dot h_{\ell m}=-im\Omega h_{\ell m}+O(\dot x)$, com
$\dot a/a\sim\dot x/x=O(x^{5/2})\,\Omega$. As taxas de memória e os fluxos são então quadráticos nas **amplitudes
relativas** $a_{\ell m}$ e o quociente só depende delas:

$$\alpha_L(x)\equiv\frac{dh^{\rm mem}_{L0}/du}{dE/du},\qquad \beta_L(x)\equiv\frac{dS_{L0}/du}{dJ/du},\qquad
\frac{dE}{du}=\frac{1}{16\pi}\sum_{\ell m}m^2\Omega^2|h_{\ell m}|^2=\Omega\,\frac{dJ}{du}.$$

Para o deslocamento, $dh_{L0}/du=\sqrt{(L-2)!/(L+2)!}\,\sum_{ab}\dot h_a\dot{\bar h}_b\,G^L_{ab}$ com
$G^L_{ab}=\oint{}_{-2}Y_a\,{}_{-2}\bar Y_b\,Y_{L0}$ (fórmula de 3j), e

$$\alpha_L=16\pi\sqrt{\tfrac{(L-2)!}{(L+2)!}}\;\frac{\sum_{ab}m_am_b\,a_a\bar a_b\,G^L_{ab}}{\sum_a m_a^2|a_a|^2}.$$

Com $\dot x=F(x)/E_b'(x)$ (balanço de energia), $E_b>0$ a energia de ligação:

$$\boxed{\frac{dm^{\rm desl}_L}{dx}=-\alpha_L(x)\,E_b'(x),\qquad \frac{dm^{\rm spin}_L}{dx}=-\beta_L(x)\,x^{-3/2}E_b'(x)\quad(M=1)}$$

usando a primeira lei $dJ=dE/\Omega$, $\Omega=x^{3/2}/M$. **O fluxo $F(x)$ cancela**: a memória como função da
frequência depende só da dinâmica conservativa ($E_b$) e da distribuição angular dos fluxos ($\alpha,\beta$). Em
particular as caudas ($4\pi x^{3/2}$ em $F$ e em $dU_{20}/dt$) não aparecem. Sobra só a absorção no horizonte, que
entra como $F_\infty/(F_\infty+F_H)$ (relativa $O(x^{5/2})$ com spins). Isso explica por que $H_{20}(x)$ não tem termo
$x^{3/2}$ sem spin, embora $dU_{20}/dt$ tenha [Favata 2009, Cunningham et al. 2025].

A memória de banda é a integral

$$\Delta h_{L0}[f_a,f_b]=\int_{x_a}^{x_b}\alpha_L(x)\,E_b'(x)\,dx,\qquad
\Delta S_{L0}[f_a,f_b]=\int_{x_a}^{x_b}\beta_L(x)\,x^{-3/2}E_b'(x)\,dx .$$

Na ordem dominante isso é a nota 4 de Favata (PRD 80, 024002, 2009): $\delta h\sim\Delta E^{\rm gw}/R$.

### 2.2 Primeira lei modo a modo [D, identidade]

Para qualquer modo $h=A\,e^{-i\varphi}$, $\dot E_{\ell m}=|\dot h|^2/16\pi=(\dot A^2+\omega^2A^2)/16\pi$ e
$\dot J_{\ell m}=-m\,{\rm Im}(\bar h\dot h)/16\pi=m\omega A^2/16\pi$, logo

$$\frac{dE_{\ell m}}{dJ_{\ell m}}=\frac{\omega_{\ell m}}{m}\Big[1+\varepsilon_{\ell m}^2\Big],\qquad
\varepsilon_{\ell m}=\frac{\dot A_{\ell m}}{A_{\ell m}\,\omega_{\ell m}} .$$

Na inspiral $\varepsilon\simeq(32/5)\nu x^{5/2}$ (reação de radiação), e o desvio é $O(x^5)$; no toque
$\varepsilon=1/(\omega_{\rm QNM}\tau)$. Com todos os modos em $\omega_{\ell m}=m\Omega$ (órbita circular), somar dá
$dE=\Omega\,dJ$ a menos de $\varepsilon^2$: é a forma radiativa da primeira lei conservativa
$dE_b=\Omega\,dJ$ [E: Le Tiec, Blanchet & Whiting 2012], que aqui gera $J(x)$ a partir de $E_b(x)$.

### 2.3 O que cada ordem acrescenta [D]

Escrevendo $E_b=\tfrac{\nu x}{2}\{1+e_2x+e_3x^{3/2}+\dots\}$ e $\alpha=\alpha_0\{1+a_2x+a_3x^{3/2}+\dots\}$:

$$h_{20}(x)=\alpha_0\,\tfrac{\nu x}{2}\Big\{1+\tfrac{a_2+2e_2}{2}\,x+\big(\tfrac25a_3+e_3\big)x^{3/2}+\dots\Big\},\qquad
S_{30}(x)=\beta_0\,\nu x^{-1/2}\Big\{1-(b_2+2e_2)\,x-\tfrac12\big(b_3+\tfrac52e_3\big)x^{3/2}+\dots\Big\},$$

e a banda é $h_{20}(x_b)-h_{20}(x_a)$, $S_{30}(x_a)-S_{30}(x_b)$. Em unidades físicas
$\nu M x=\nu M^{5/3}(\pi f)^{2/3}=\mathcal M^{5/3}(\pi f)^{2/3}$ e $\nu M^2x^{-1/2}=\mathcal M^{5/3}(\pi f)^{-1/3}$:

- **Newtoniana:** deslocamento $\propto(\mathcal M^{5/3}/D)\,A_d(\iota)\,\Delta f^{2/3}$ e spin
  $\propto(\mathcal M^{5/3}/D)\,A_s(\iota)\,\Delta f^{-1/3}$. As formas em $f$ são universais. Quaisquer $K$ bandas dão
  **dois** números: $\mathcal M^{5/3}/D$ e $\iota$ (pela razão $A_s/A_d$).
- **1PN:** os termos $c_d(\nu)(\pi Mf)^{2/3}$ e $c_s(\nu)(\pi Mf)^{2/3}$ trazem $M$ separado de $\mathcal M$. Como
  $c_d/c_s$ depende de $\nu$, são **dois** números novos ($M$ e $\nu$), e com eles $D$ sai de $\mathcal M^{5/3}/D$.
- **1,5PN:** duas combinações spin-órbita diferentes, $16/3\,s+419/160\,\delta\sigma$ (deslocamento) e
  $415/54\,s+3575/864\,\delta\sigma$ (spin), fixam $\chi_1$ e $\chi_2$: mais **dois**.
- **2PN e acima:** as mesmas variáveis (termos $\nu^2$, $s^2$, $s\sigma$, $\sigma^2$). Não há parâmetros novos, só
  redundância.

Previsão: posto 2 (N), 4 (1PN), 6 (1,5PN). Os valores singulares das bandas da inspiral caem como as potências de $x$
das ordens que os criam.

**Razão spin/deslocamento [D].** No observador, $\pi f\,dS/dh=(\beta/\alpha)(x)\,A_s(\iota)/A_d(\iota)$, com
$\beta/\alpha=(\beta_0/\alpha_0)[1+(b_2-a_2)x+\dots]$. Isso independe de $M$, $D$ e, na ordem dominante, de $q$ e dos
spins: mede $\iota$. É também um teste da primeira lei com a memória. A correção 1PN é
$b_2-a_2=0{,}3615-0{,}2731\,\nu$ (seção 5.1).

## 3. Fontes PN usadas e como foram obtidas

- $E(x)$ (3,5PN, SO+SS+SSS), $F_\infty$, $F_H$, $\dot x$, $dU_{20}/dt$, $H_{20}$, $H_{40}$, $H_{60}$, $H_{80}$ com spins
  alinhados: material suplementar de Cunningham, Kavanagh, Pound, Trestini, Warburton & Neef, CQG 42, 135009 (2025),
  arXiv:2410.23950v2 (`anc/Supplementary_Material.dat.wl`). Variáveis $s=(m_1^2\chi_1+m_2^2\chi_2)/M^2$,
  $\sigma=(m_2\chi_2-m_1\chi_1)/M$, $\delta=(m_1-m_2)/M$.
- Amplitudes $h_{\ell m}$, $\ell\le4$, até 1,5PN com spin-órbita: Arun, Buonanno, Faye & Ochsner, PRD 79, 104023 (2009),
  arXiv:0810.5336 (`anc/ABFO09.m`), no limite não precessante $\iota=0$, $\alpha=\pi$ (seção II do artigo). Na
  convenção ABFO, $H_{\ell m}=i^mH^{\rm Blanchet}_{\ell m}$: é uma fase comum por $m$, que não afeta os produtos de mesmo $m$.
- $J(x)$ sem spin (Blanchet, Living Rev. Relativ. 27, 4 (2024), eq. Jcirc) e $H_{30}$ (mesma referência, eq. H30), só
  para conferir.

Os arquivos foram baixados do arXiv (fonte LaTeX, `export`/`e-print`) para o diretório de rascunho e lidos como dados
por `codigo/exp20_pn_extrair.py`, com `python -I` e `sympy.parsing.mathematica.parse_mathematica`, que não executa código.
As expressões convertidas estão em `resultados/exp20_pn_expressoes.json`.

## 4. Experimentos

| Script | O que faz | Saída |
|---|---|---|
| `codigo/exp20_comum.py` | memórias de $K$ janelas a partir de **uma** onda (pós-processamento copiado de `memorias_observaveis`); jacobianos de $\ln|y|$ (5 pontos; $\iota$, $D$, $\phi$ sem regerar a onda) | — |
| `codigo/exp20_teste_comum.py` | confere `janelas` contra `memorias_observaveis` (uma onda por janela) e o jacobiano com $h$ e $h/2$ | `resultados/exp20_teste_comum.txt` |
| `codigo/exp20_pn_extrair.py` | extrai as expressões PN publicadas (seção 3) | `resultados/exp20_pn_expressoes.json` |
| `codigo/exp20_pn_comum.py` | $\alpha_L,\beta_L$ exatos (Gaunt) e por núcleos numéricos da `CalculadoraMemoria`; $E_b$, $J$ pela primeira lei | — |
| `codigo/exp20_pn.py` | tarefa 1: conferências, séries das razões, primeira lei modo a modo, bandas do substituto contra PN | `resultados/exp20_pn.txt`, `.json`, `figuras/e20_bandas_pn.png` |
| `codigo/exp20_cm_borda.py` | parte nula da CM de banda como termo de borda (H03.8) | `resultados/exp20_cm_borda.txt` |
| `codigo/exp20_cm_dt.py` | a mesma parte nula com dt = 0,25 e 0,125 (teste numérico de H03.8) | `resultados/exp20_cm_dt.txt` |
| `codigo/exp21_jacobianos_K.py` | tarefa 2: jacobianos com 49 janelas de 10 a 37,5 Hz ($Mf$ 0,0032–0,012), subconjuntos $K=1..49$; T0, O0, T, O; bandas da inspiral contra o modelo PN ordem a ordem | `resultados/exp21_jacobianos_K.txt`, `.json`, `.npz`, `figuras/e21_valores_singulares.png` |
| `codigo/exp22_familia_K.py`, `exp22_resumo.py` | tarefa 3: perfil em $q_B$ do resíduo mínimo para $K$ janelas (T0: $K=1,2,3,4$; O0: $K=2,3,4,6$), LM próprio, várias partidas | `resultados/exp22_familia_*.json/.txt`, `exp22_resumo.txt`, `figuras/e22_familia.png` |
| `codigo/exp23_preparar.py` | tarefa 4: bandas elementares numa grade comum em $Mf$, jacobianos, matrizes de Gram do ruído (CE, ET) | `resultados/exp23_prep_*.npz/.txt` |
| `codigo/exp23_desenho.py` | tarefa 4: otimização exaustiva ($K\le5$) e por descida coordenada ($K=6$) dos cortes; critérios D e E; ruídos `diag`, `corr`, `unif` | `resultados/exp23_desenho.txt`, `.json`, `figuras/e23_desenho.png` |

Parâmetros: `dt = 0,25 M`, derivada de 8ª ordem, $E_{\rm lig}$ 3PN+SO para $M_f$ (padrões do L00). Passos dos jacobianos:
2e-3 em $q$ e $\chi$ (acima do piso de ruído de 3e-10 do substituto, verificação L00), 5e-4 relativo em $M$ (abaixo do
período de 0,73% das oscilações com todos os $m$), 1e-4 rad em $\iota$ e $\phi$, 1e-3 relativo em $D$. Máquina
compartilhada: no máximo dois processos, `OMP_NUM_THREADS=1`.

## 5. Resultados

### 5.0 Infraestrutura de janelas múltiplas (`exp20_teste_comum.txt`)

- Com só $m=0$, as memórias de quatro janelas (10, 14, 20, 31 Hz) tiradas de uma onda gerada desde 10 Hz coincidem
  com `memorias_observaveis` (uma onda por janela) a ≤ 1,4e-12 por multipolo, nos níveis A e C. $t_i$ e $M_f$ são
  idênticos.
- Com todos os $m$, a diferença ingênua chega a 4,7e-2. É só convenção: a fase orbital é zerada em $t_i$ da janela mais
  baixa. Depois da rotação azimutal $\phi\to\phi-\Delta$, com $\Delta$ a fase orbital em $t_i(f)$, a diferença cai para
  ≤ 3,8e-10.
- Jacobiano 8×6 (10 e 14 Hz): $|J(h)-J(h/2)|/|J|$ ≤ 2,0e-6 por coluna, e os valores singulares coincidem nos cinco
  algarismos impressos.

### 5.1 Razões taxa/fluxo e primeira lei (`exp20_pn.txt`, partes a e b) [D, analítico + conferência]

Com as amplitudes ABFO ($\ell\le4$, 1,5PN SO) e a fórmula de Gaunt (conferida por quadratura com `harmonicos.sYlm`
a 1,1e-7):

| Razão | Valor dominante | 1PN | 1,5PN (SO) |
|---|---|---|---|
| $\alpha_2$ (desl. (2,0) / $\dot E$) | $4\sqrt{30\pi}/21=1{,}8491675$ | $-1051/2016+71\nu/24$ | $5s/3+99\,\delta\sigma/64$ |
| $\alpha_4$ (desl. (4,0) / $\dot E$) | $\sqrt{10\pi}/315=0{,}0177936$ | $-157925/14784+9105\nu/176$ | $40s/3+205\,\delta\sigma/16$ |
| $\beta_3$ (spin (3,0) / $\dot J$) | $\sqrt{210\pi}/70=0{,}3669328$ | $-725/4536+145\nu/54$ | $100s/27+1415\,\delta\sigma/432$ |
| giroscópica (1,0) / $\dot J$ | $-2{,}0466534$ | $-293/672+111\nu/56$ | $10s/21+27\,\delta\sigma/56$ |
| giroscópica (3,0) / $\dot J$ | $+0{,}6699246$ | $449/1512+11\nu/18$ | $10s/3+93\,\delta\sigma/32$ |
| CM (2,0), parte nula | 0 | 0 | 0 (≤ 1,6e-17) |

Não há termo de 0,5PN em nenhuma razão, nem a cauda $4\pi$. Conferências:

- **$\alpha_2$ e $\alpha_4$.** Os coeficientes de 1PN e 1,5PN coincidem exatamente com a razão
  $(dU_{L0}/dt)/F$ de Cunningham et al. 2025 (eqs. 39 e 41 e o suplemento). Os valores em ponto flutuante batem em 12
  algarismos: $-0{,}521329365079$, $2{,}958333333333$, $1{,}666666666667$, $1{,}546875000000$. O valor dominante
  coincide com o de Favata, $(8/7)\sqrt{5\pi/6}$. São dois caminhos independentes: amplitudes ABFO com Gaunt de um
  lado, cálculo de memória de Cunningham et al. do outro.
- **$\beta_3$.** O valor dominante é o coeficiente $\sqrt{3\pi/70}$ de Nichols, PRD 95, 084048 (2017), eq.
  SpinMemLeadingPN. O 1PN coincide com a razão entre o modo (3,0) não oscilatório de Blanchet LRR 2024 (eq. H30,
  $-\tfrac25 i\sqrt{6/7}\,\nu[x^{5/2}+x^{7/2}(-5017/1296-25\nu/108)]$) e $F/\Omega$:
  $-5017/1296+1247/336=-725/4536$, $-25/108+35/12=145/54$. Essa linha é impressa por `exp20_pn.py`.
- **CM.** Taxa nula até 1,5PN: na inspiral quase circular a memória de CM só começa em 3PN e 4PN [E: Nichols PRD 98,
  064032 (2018)].
- **$H_{20}(x)$.** $\int\alpha_2E_b'\,dx$ reproduz o $H_{20}$ de Cunningham. Com os coeficientes acima e
  $e_2=-(3/4+\nu/12)$, $e_3=14s/3+2\delta\sigma$:
  $(a_2+2e_2)/2=-4075/4032+67\nu/48$ e $\tfrac25a_3+e_3=16s/3+419\,\delta\sigma/160$, exatamente os termos de
  $H_{20}$. Numericamente, $(dh_{20}/dx)\,\dot x$ difere de $dU_{20}/dt/\sqrt2$ em −2,0e-6 em $x=0{,}01$ e −1,3e-3 em
  $x=0{,}05$, pelo truncamento em $O(x^4)$. Em $x=0{,}05$, $h_{20}$(Cunningham, 3,5PN) $=1{,}10888\times10^{-2}$
  contra $1{,}10890\times10^{-2}$ de `binarias.favata_h20` (3PN).
- **Primeira lei.** $J(x)$ obtido por $\int-x^{-3/2}E_b'\,dx$ coincide **exatamente** com o $J$ de Blanchet até 3PN
  sem spin (diferença simbólica 0). Os termos SO saem $-\tfrac56(7s+3\delta\sigma)x^{3/2}$ e
  $\tfrac{7}{72}(61\nu s-99s+30\nu\delta\sigma-27\delta\sigma)x^{5/2}$.

**Memória de spin de banda até 1,5PN** [D; o 1PN conferido como acima, o SO só pela integração]:

$$S_{30}(x)=\frac{\sqrt{210\pi}}{70}\,\nu\,x^{-1/2}\Big\{1+\Big(\frac{7529}{4536}-\frac{68}{27}\nu\Big)x
-\Big(\frac{415}{54}s+\frac{3575}{864}\delta\sigma\Big)x^{3/2}+O(x^2)\Big\},\qquad \Delta S_{30}=S_{30}(x_a)-S_{30}(x_b).$$

**Modos ausentes do substituto.** O substituto não tem (3,1), (4,2) e (4,1). Sem eles,
$\alpha_2\to1+(-1517/2688+2077\nu/672)x+(5s/3+37\delta\sigma/24)x^{3/2}$ e
$\beta_3\to1+(-8375/24192+725\nu/224)x+(100s/27+355\delta\sigma/108)x^{3/2}$. Isso muda o 1PN de $\alpha_2$ em
$-0{,}043+0{,}13\nu$ (cerca de −5e-4 relativo em $x=0{,}05$, $\nu\approx0{,}25$) e o de $\beta_3$ em $-0{,}19+0{,}55\nu$
(cerca de −2e-3). A comparação com o substituto usa a versão "modos do substituto".

**Parte nula da CM de banda (H03.8).** No substituto ela **não** é zero na inspiral (`exp20_pn.txt` (d),
`exp20_cm_borda.txt`, `exp20_cm_dt.txt`). Fração nula da banda de cm20: 1,0e-2 a 6,5e-2 ($q=1$), −1,1e-2 a −2,6e-2
($q=3$), −3,1e-2 a −1,1e-1 ($q=4$, $\chi=-0{,}5$).

A hipótese do termo de borda foi **refutada**. O núcleo da CM só vê a parte anti-hermitiana $A^\dagger-A$, que mata as
derivadas totais $\tfrac12\Delta(a_a\bar a_b)$; a previsão sai ~1e-23, contra 1e-5 medidos.

Outras quatro explicações testadas:
1. **Numérica.** Refutada: com dt = 0,125 os valores são idênticos em todos os algarismos impressos.
2. **Convenção da massa na parte ordinária** ($M_f$ em vez da massa de Bondi $M(u)\approx1-E_b$). Daria 4,5%, não 1%.
   Também não explica a forma.
3. **Termos cruzados não adiabáticos** entre modos de ordens PN diferentes. Estimados em ~1e-4 relativos, e suaves.
4. **Artefato de referencial ou de hibridização do substituto.** Compatível com os dados [H].

A parte nula por banda é **proporcional a $\Delta(Mf)$**: −1,13e-5 por 0,001 em $Mf$ abaixo de 0,006 e −3,1e-5 por 0,001
acima. O salto acontece em $Mf\approx0{,}006$, perto do início da parte de RN do substituto. Uma origem física
adiabática seria suave em $x$ e começaria em 3PN [Nichols 2018].

### 5.2 Memórias de banda do substituto contra PN (`exp20_pn.txt`, parte d; `figuras/e20_bandas_pn.png`)

Bandas em $Mf$: [0,002; 0,003], …, [0,012; 0,014]; multipolos $m=0$. A tabela dá o erro relativo PN/substituto − 1
nas três primeiras bandas e na última.

**$q=1$, sem spin.**

| Memória | N | 1PN | 1,5PN | 2PN | 3PN | 3,5PN |
|---|---|---|---|---|---|---|
| desl. (2,0), [0,002; 0,003] | +7,1e-2 | +1,5e-2 | +1,5e-2 | +2,7e-4 | +2,4e-5 | **−1,2e-5** |
| desl. (2,0), [0,004; 0,006] | +1,3e-1 | +3,9e-2 | +3,9e-2 | +1,3e-4 | −9,3e-4 | −1,1e-3 |
| desl. (2,0), [0,012; 0,014] | +4,0e-1 | +1,8e-1 | +1,8e-1 | +3,8e-3 | −5,0e-3 | −7,2e-3 |
| spin (3,0), [0,002; 0,003] | +6,0e-2 | +1,4e-2 | +1,4e-2 | +1,0e-4 | −1,5e-4 | −1,5e-4 |
| desl. (4,0), [0,002; 0,003] | +1,3e-2 | +2,0e-2 | +2,0e-2 | −4,7e-4 | −9,1e-4 | −1,1e-3 |

- Sem spin, 1PN e 1,5PN dão exatamente o mesmo número: a cauda cancela (seção 2.1).
- No começo da banda o erro cai até 1,2e-5. Na fusão ($Mf\ge0{,}006$) a série PN satura em 3e-3 a 7e-3.

**Com spins.** Banda [0,002; 0,003], 3,5PN no deslocamento (2,0) e 1,5PN (+$E_b$ até 3,5PN) no spin:

| Sistema | desl. (2,0) | spin (3,0) |
|---|---|---|
| A ($q=1{,}2$; $+0{,}3$, $-0{,}2$) | −8,4e-4 | −9,5e-4 |
| $q=3$ ($+0{,}6$, 0) | −1,4e-3 | −2,3e-3 |
| $q=2$ ($+0{,}5$, $+0{,}5$) | −1,6e-3 | −1,9e-3 |
| $q=4$ ($-0{,}5$, $-0{,}5$) | +6,5e-4 | −1,2e-3 |

- O SO de 1,5PN é necessário: em $q=2$ com $\chi=+0{,}5$ ele leva o erro de −1,6e-2 (1PN) para +1,1e-2. Mas a série
  satura num patamar de ~1e-3 a 2e-3, que não cai com a ordem.
- Para $q=4$, $\chi=-0{,}5$, a convergência é lenta: 1,6e-2 a 3,5PN em [0,010; 0,012].

**De onde vem o patamar com spins** (`exp20_pn.txt` (d), linhas "energia da banda" e "alpha efetivo"). Separei o
erro da banda em erro da energia irradiada e erro da razão $\alpha_{\rm ef}=\Delta h_{20}/\Delta E$. Banda
[0,002; 0,003]:

| Sistema | energia: Cunningham 3,5PN | energia: 3PN+SO sem SS | $\alpha_{\rm ef}$ (ABFO 1,5PN) |
|---|---|---|---|
| $q=1$ | −1,9e-5 | −1,9e-5 | +6,5e-5 |
| A | −8,5e-4 | −8,3e-4 | +7,4e-5 |
| $q=3$ ($+0{,}6$, 0) | −1,3e-3 | −2,0e-4 | −4,6e-4 |
| $q=2$ ($+0{,}5$, $+0{,}5$) | −1,7e-3 | −3,7e-4 | −4,3e-5 |
| $q=4$ ($-0{,}5$, $-0{,}5$) | +1,1e-3 | +2,5e-3 | −1,1e-3 |

- **A fatoração em $\alpha\times E_b'$ vale** a ~1e-4 em $\alpha$ para $q\le2$. O patamar de ~1e-3 é quase todo da
  **energia**: a energia irradiada do substituto difere da $E_b$ PN de 1e-3 a 2e-3 com spins.
- Os termos spin-spin de Cunningham **pioram** a concordância com o substituto em $q=3$ e $q=2$ (−1,3e-3 contra −2,0e-4
  sem SS). **[H]** O trecho híbrido PN/EOB do substituto não tem a mesma energia SS que o PN de 3,5PN. Cabe na incerteza
  entre modelos de ~1e-4 absoluto do L00.

### 5.3 Primeira lei modo a modo no substituto (`exp20_pn.txt`, parte c)

- **Identidade.** $(dE_{\ell m}/dJ_{\ell m})/[(\omega/m)(1+\varepsilon^2)]-1$ fica entre 1,1e-8 [(2,2)] e 3,2e-4 [(4,3),
  o modo mais fraco, limitado pela derivada numérica da fase], em $t_i+50<u<60$.
- **$\varepsilon^2$ no (2,2):** 2,25e-6 em $u=-5000$; 4,3e-5 em −500; 9,5e-4 em −50; 3e-7 no pico (onde $\dot A=0$);
  1,9e-2 a 2,1e-2 no toque. A previsão da reação de radiação em $u=-5000$ é $(32\nu x^{5/2}/5)^2\approx2{,}5\times10^{-6}$, com $x\approx0{,}063$
  pela relação tempo-frequência de ordem dominante.
- **Total:** $\dot E/(\Omega\dot J)-1$ = +2,3e-6 ($u=-5000$), +4,3e-5 (−500), +9,8e-4 (−50), −2,2e-5 (pico), +2,1e-2 (toque).
- **Integrais desde 10 Hz:** até $u=-200$, $E=8{,}43802\times10^{-3}$ contra $\int\Omega\,dJ=8{,}43775\times10^{-3}$
  (razão − 1 = 3,2e-5). Até o fim, 4,46896e-2 contra 4,44922e-2 (4,4e-3).
- A primeira lei integrada vale a 3e-5 na inspiral. Na janela inteira falha em 0,44%, por causa da fusão e do toque
  ($\varepsilon\sim0{,}14$ e $\omega_{\ell m}\ne m\Omega$).

### 5.4 Quantos números cada janela acrescenta (`exp21_jacobianos_K.txt`, `figuras/e21_valores_singulares.png`)

Valores singulares do jacobiano de $\ln|y|$, colunas escaladas como na R4 (0,1 em $q$, $\chi_1$, $\chi_2$; 1 $M_\odot$;
0,01 rad em $\iota$ e $\phi$; 1% em $D$). Janelas até o fim (fusão incluída), $K$ janelas geométricas de 10 a 37,5 Hz:

| Conjunto | $K$ | valores singulares |
|---|---|---|
| T0 (4 memórias, $m=0$) | 1 | 9,8e-2, 2,0e-2, 1,2e-2, 4,1e-3 |
| | 2 | 1,5e-1, 2,7e-2, 2,0e-2, 7,7e-3, **3,1e-3, 5,2e-4** |
| | 3 | 1,9e-1, 3,2e-2, 2,4e-2, 9,2e-3, 3,2e-3, 5,7e-4 |
| | 49 | 7,5e-1, 1,3e-1, 9,6e-2, 3,6e-2, 1,0e-2, 1,7e-3 |
| O0 (desl. + spin, $m=0$) | 1 | 7,2e-2, 1,3e-2 |
| | 2 | 1,1e-1, 1,7e-2, **5,4e-3, 3,5e-4** |
| | 3 | 1,4e-1, 2,0e-2, 5,4e-3, 3,6e-4, **1,8e-4, 1,1e-6** |
| | 49 | 5,5e-1, 8,0e-2, 1,7e-2, 1,1e-3, 8,7e-4, 5,9e-5 |
| T (4 memórias, todos os $m$, 7 parâmetros) | 2 | 2,6e-1, 1,1e-1, 2,1e-2, 5,3e-3, 2,6e-3, 1,0e-3, 2,5e-6 |
| O (desl. + spin, todos os $m$) | 3 | 2,8e-1, 7,7e-2, 3,9e-3, 7,6e-4, 3,4e-4, 4,8e-6 |
| | 4 | …, 8,1e-5, **3,2e-7** (o 7º) |

**Contagem.** Cada janela nova acrescenta **dois** números até o posto saturar:
- T0: 4 (uma janela) → 6 (duas);
- O0: 2 → 4 → 6, e o sexto valor com três janelas é só 1,1e-6;
- O: precisa de 4 janelas para o posto 7.

**Saturação.** Com mais janelas o espectro só cresce como $\sqrt K$, pela repetição das medidas:
- T0: $\sigma_6/\sqrt K$ vale 3,7e-4 com $K=2$ e 2,4e-4 com $K=49$;
- O0: $\sigma_6/\sqrt K$ vale 6,6e-7 com $K=3$ e 8,4e-6 com $K=49$. Só aqui a função de janela contínua melhora a
  6ª direção, de 13 vezes.

**Direção mais fraca.**
- T0 (K=49): quase só $q$ (−0,96 nas escalas R4).
- O0: $q$, $\chi_1$, $\chi_2$ juntos.
- T e O: o azimute $\phi$ (−1,000), porque $\phi$ só entra pelas bordas $m\neq0$ (±1,3% no spin) e a escala de
  0,01 rad o torna pequeno.

**Limiar físico.** A janela inteira de A em CE tem SNR 34,7 no deslocamento e 3,2 no spin (`exp23_prep_A.txt`). A
precisão relativa é, então, $\varepsilon_d\approx0{,}029$ e $\varepsilon_s\approx0{,}31$. Contagem de valores
singulares acima dos limiares:

| Conjunto | 1e-2 | 1e-3 | 1e-4 | 1e-5 |
|---|---|---|---|---|
| T0, $K=1$ | 3 | 4 | 4 | 4 |
| T0, $K=2$ | 3 | 5 | 6 | 6 |
| O0, $K=2$ | 2 | 3 | 4 | 4 |
| O0, $K=5$ | 2 | 3 | 5 | 6 |

- O $K$ mínimo para posto 6 com $\sigma_6>10^{-4}$ é 2 em T0. Em O0 nenhum $K\le49$ chega lá; com $\sigma_6>10^{-5}$,
  $K=5$. Com $\sigma_6>10^{-3}$, T0 precisa de $K=25$, e isso só pela contagem repetida $\sqrt K$.
- Com $\varepsilon\sim0{,}03$ (CE), nenhum $K$ dá mais que 1 a 2 números mensuráveis.

**Bandas da inspiral contra PN (H03.3–H03.5).** Só as bandas $[f_j,f_{j+1}]$, sem a janela da fusão; deslocamento e
spin, $m=0$. Valores singulares com $K=9$ (8 bandas):

| Modelo | $\sigma_1$…$\sigma_6$ |
|---|---|
| substituto | 1,28e-1, 3,9e-2, 2,3e-2, 5,0e-3, 7,5e-4, 1,7e-4 |
| PN N | 1,22e-1, 2,1e-2, 9e-13, 5e-13, 3e-13, 9e-20 |
| PN 1PN | 1,19e-1, 2,1e-2, 9,3e-4, 5,0e-5, 4e-13, 4e-20 |
| PN 1,5PN | 1,27e-1, 2,3e-2, 1,7e-2, 1,1e-4, 2,0e-5, 4,8e-6 |
| PN 3,5PN | 1,28e-1, 2,8e-2, 2,1e-2, 1,5e-4, 6,0e-5, 8,2e-6 |

- **O posto previsto ordem a ordem se confirma exatamente: 2 (N), 4 (1PN), 6 (1,5PN).** Na ordem dominante,
  $\sigma_3\dots\sigma_6$ ficam no zero numérico (1e-12).
- $\sigma_1$ a $\sigma_3$ do substituto concordam com o PN de ordem alta a 0–40%. $\sigma_4$ a $\sigma_6$ do substituto
  são 20 a 30 vezes maiores que os PN.
- Com bandas finas ($K=25$, 49) o substituto tem $\sigma_2$ de 0,17 a 0,30, contra 0,05–0,07 no PN. Isso é estável entre
  $h$ e $h/2$ e vem das bandas tardias ($Mf\gtrsim0{,}008$): as normas das linhas oscilam de banda para banda (0,03, 0,06,
  0,04, 0,07, 0,13). **[H]** A causa provável são as pequenas oscilações de $\omega_{22}$ do substituto (excentricidade
  residual ou hibridização), que deslocam as bordas definidas por frequência.
- Erro das próprias bandas PN contra o substituto ($K=9$): N, 9–29%; 1PN, 2–11%; 2PN, ≤ 0,8%; 3,5PN, ≤ 8e-3 (deslocamento)
  e ≤ 4,7e-3 (spin).

### 5.5 A família sob $K$ janelas (`exp22_familia_*.txt`, `exp22_resumo.txt`, `figuras/e22_familia.png`)

Alvo: A. Para cada $q_B\in\{1;\,1{,}1;\,1{,}3;\,1{,}6;\,2;\,3\}$, minimiza-se o resíduo relativo
$r=(y_B-y_A)/|y_A|$ sobre $(\chi_1,\chi_2,M,\iota,D)$ com LM, partindo de três pontos:
- de A com $q$ trocado e por continuação (varredura de A para cima e para baixo);
- do par do exp07 com $\chi_{2B}=0$, quando existe;
- de uma partida aleatória em $q_B=1{,}6$ e $3$.

As partidas aleatórias e de continuação convergiram ao mesmo mínimo em todos os casos sobredeterminados conferidos
(por exemplo, $q_B=1{,}6$ em T0_K2r: $\chi_1=+0{,}3635$, $\chi_2=-0{,}2422$ nas duas). Previsão linear: resíduo
$\approx|q_B-q_A|\,\|P_\perp J_q\|$.

Máximo de $|r|$ (melhor partida):

| Configuração | eq. | $\|P_\perp J_q\|$ (norma, por unidade de $q$) | $q_B=1{,}0$ | 1,1 | 1,3 | 1,6 | 2,0 | 3,0 |
|---|---|---|---|---|---|---|---|---|
| T0, $K=1$ (10 Hz) | 4 | 0 | 8e-12 | 9e-12 | 2e-12 | 7e-12 | 2e-12 | 1e-11 |
| T0, $K=2$ (10, 20 Hz) | 8 | 2,6e-3 | 2,1e-4 | 1,1e-4 | 1,8e-4 | 9,5e-4 | 2,2e-3 | 5,9e-3 |
| T0, $K=2$ (10, 37,5 Hz) | 8 | 5,4e-3 | 5,4e-4 | 2,5e-4 | 3,6e-4 | 1,9e-3 | 4,5e-3 | 1,1e-2 |
| T0, $K=3$ | 12 | 5,9e-3 | 5,1e-4 | 2,6e-4 | 3,7e-4 | 1,9e-3 | 4,4e-3 | 1,1e-2 |
| T0, $K=4$ | 16 | 6,3e-3 | 5,0e-4 | 2,8e-4 | 3,9e-4 | 2,0e-3 | 4,7e-3 | 1,2e-2 |
| O0, $K=2$ | 4 | 0 | 3e-11 | 3e-11 | 8e-12 | 2e-11 | 3e-12 | 1e-11 |
| O0, $K=3$ | 6 | 2,3e-5 | 2,4e-6 | 1,6e-6 | 2,0e-6 | 1,0e-5 | 7,2e-4* | 3,4e-3* |
| O0, $K=4$ | 8 | 9,7e-5 | 4,6e-6 | 8,1e-6 | 7,5e-6 | 3,2e-5 | 1,2e-3* | 3,9e-3* |

O0 com $K=6$ foi iniciado e interrompido por tempo (≈25 min estimados); não há resultado.

\* Em $q_B=2$ e $3$ a solução de O0, $K=3$, encosta no limite do modelo, $\chi_2=-0{,}8$: o resíduo é limitado pela
fronteira do domínio, não pela física.

1. **Família exata.** Com $K=1$ (T0) e com $K\le2$ (O0) há menos equações que incógnitas e a família é exata (resíduo
   ~1e-11, o piso da infraestrutura) em toda a faixa $q_B\in[1,3]$. As soluções andam bastante: em T0, $K=1$, $\chi_1$
   vai de −0,06 a +0,27 e $M$ de 64,9 a 79,8 $M_\odot$; em O0, $K=2$, $D$ vai de 305 a 402 Mpc.
2. **Família aproximada.** Com a primeira janela a mais, o resíduo mínimo passa a crescer com $|q_B-q_A|$. Na
   norma (a previsão linear é para a norma; a tabela dá o máximo), a razão medido/linear em T0, $K=2$, é:
   - 0,74 ($q_B=1{,}1$), 1,2 (1,3) e 1,7 (1,6);
   - 2,2 em $q_B=3$: acima de $|\Delta q|\approx0{,}4$ o crescimento é mais rápido que linear.
   - **De $K=2$ para $K=4$ ela quase não encolhe:** $\|P_\perp J_q\|$ vai de 5,4e-3 a 6,3e-3 (+17%), e os máximos dos
     resíduos mínimos mudam de −8% a +12%. Em tolerância, a faixa de $q_B$ com $\max|r|<10^{-3}$ é [1,0; 1,3] para $K=2,3,4$, e com
     $<10^{-2}$, [1,0; 2,0].
   - As janelas mais separadas importam mais que o número: 10+37,5 Hz dá um resíduo 2,4 vezes o de 10+20 Hz.
3. **Conjunto mensurável.** Com O0, $K=3$ (6 equações), a família aproximada tem resíduo de só **2e-6 a 1e-5** em
   $q_B\in[1;1{,}6]$. Com $K=4$, $\|P_\perp J_q\|$ cresce 4,3 vezes (2,3e-5 → 9,7e-5) e o resíduo fica em 5e-6 a 3e-5.
   Aqui uma janela a mais ainda encolhe a família, como no espectro de O0 (5.4), mas o resíduo continua
   10^3–10^4 vezes abaixo das precisões de CE (3% no deslocamento, 30% no spin).
4. **Comparação com a revisão R4.** Lá, com o deslocamento total e `binarias`, T0 de 10+20 Hz dava 4,4e-5 ($q_B=1{,}1$) a
   2,3e-3 ($q_B=3$). Aqui, com o deslocamento de janela, 1,1e-4 a 5,9e-3: mesma ordem e mesma forma.

### 5.6 Desenho ótimo de bandas (`exp23_desenho.txt`, `exp23_prep_*.txt`, `figuras/e23_desenho.png`)

**Fontes:**
- A;
- $q=3$, $\chi=(0{,}6;0)$;
- A com $M=30$;
- A com $M=150$.

Todas com $D=400$ Mpc, $\iota=50^\circ$. Grade comum em $Mf$ (razão 1,066), de 10 Hz até $0{,}9\,f_{\rm pico}$
($Mf\approx0{,}050$; $Mf_{\rm pico}$ = 0,0583 em A, 0,0620 em $q=3$). Medidas: deslocamento (+) e spin (×) por banda.
Parâmetros $(q,\chi_1,\chi_2,\ln M,\iota,\ln D)$, priors gaussianos de larguras (2; 0,5; 0,5; 0,3; 0,5; 0,5).

**SNR da memória nula** (série desde 10 Hz, $f_{\rm min}=5$ Hz):

| Fonte | CE desl. | CE spin | ET desl. | ET spin |
|---|---|---|---|---|
| A | 34,7 | 3,2 | 11,7 | 0,85 |
| $q=3$ | 23,3 | 1,9 | 8,1 | 0,49 |
| $M=30$ | 21,0 | 1,3 | 6,7 | 0,40 |
| $M=150$ | 46,6 | 6,8 | 19,5 | 1,9 |

- Com $f_{\rm min}=10$ Hz, A dá 34,09 e 3,21 em CE, que é a SNR do L00.
- Quase toda a SNR está na última banda (fusão e toque). Em A/CE, a soma das bandas da inspiral até $Mf=0{,}03$ tem SNR
  ≲ 1,5 por banda; as bandas abaixo de 20 Hz, $<10^{-2}$.
- A soma de todos os elementos de $G$ reproduz a SNR da série inteira em todos os casos (34,6789 contra 34,6789).

**Resultados (CE).** $D$ = Σ ln(1+λ) do Fisher branqueado; $\sigma_{\rm post}/\sigma_{\rm prior}$ na ordem
$(q,\chi_1,\chi_2,\ln M,\iota,\ln D)$.

| Fonte | $K$ | cortes D-ótimos, `corr` (Hz) | $Mf$ | $D$ `corr` | $D$ `diag` | $\sigma_{\rm post}/\sigma_{\rm prior}$ (`corr`) |
|---|---|---|---|---|---|---|
| A | 1 | — | — | 8,175 | 8,175 | 0,99 0,98 0,99 0,80 0,44 0,78 |
| A | 2 | 156,2 | 0,050 | 11,200 | 11,466 | 0,99 0,85 0,94 0,36 0,40 0,75 |
| A | 3 | 93,7; 156,2 | 0,030; 0,050 | 11,647 | 12,145 | 0,98 0,87 0,95 0,28 0,41 0,74 |
| A | 4–6 | — | — | 11,66 | 12,17–12,18 | igual a $K=3$ |
| $q=3$ | 2 / 3 | 156,2 / 113,5; 156,2 | 0,050 / 0,036; 0,050 | 10,669 / 10,898 | 10,910 / 11,370 | 0,79 0,72 1,00 0,49 0,55 0,89 ($K=3$) |
| $M=30$ | 2 / 3 | 338,4 / 157,3; 338,4 | 0,050 / 0,023; 0,050 | 8,171 / 8,460 | 8,401 / 8,835 | 0,99 0,91 0,97 0,41 0,57 0,83 ($K=3$) |
| $M=150$ | 2 / 3 | 67,7 / 49,2; 67,7 | 0,050 / 0,036; 0,050 | 13,821 / 14,479 | 14,827 / 15,857 | 0,95 0,84 0,94 0,24 0,24 0,65 ($K=3$) |

1. **Duas ou três bandas bastam.** O ganho de $K=1$ para $K=2$ é +3,0 (`corr`) e +3,3 (`diag`) em $D$, isto é,
   ~1,5 nat ≈ 2,2 bits. De 2 para 3, +0,45 a +0,68. De 3 para 6, ≤ +0,04 (A). Os cortes geométricos ingênuos em $Mf$
   dão $D$ = 8,20 ($K=2$) a 9,49 ($K=6$) em A (`diag`): mesmo com seis bandas, menos que o ótimo de duas.
2. **O corte de $K=2$ cai sempre na borda superior permitida,** $0{,}9\,f_{\rm pico}$. Isso vale nas quatro fontes, nos
   dois detectores e nos três modelos de ruído. A primeira grade, até $Mf=0{,}030$, também o punha na borda
   (`exp23_desenho_grade030.txt`). Leitura: a melhor divisão separa o pico e o toque de todo o resto. Com bandas
   definidas pela frequência instantânea do (2,2), o pico é o limite; bandas por tempo poderiam ir além (seção 10).
3. **O que as bandas medem.** O ganho é quase todo na escala de massa: $\sigma_{\ln M}$ cai de 0,80 para 0,28 do prior
   (A), e para 0,24 com $M=150$. $\iota$ melhora pouco (0,44 → 0,41). $q$, $\chi_1$ e $\chi_2$ ficam no prior
   (0,85–1,00). **O critério E é degenerado:** $\lambda_{\min}\le8{,}7\times10^{-4}$ em todos os desenhos com CE e ET (zero exato com
   $2K<6$). Os desenhos E-ótimos são erráticos (cortes de 11 a 156 Hz) e dão $D$ pior; não servem de prescrição.
4. **Universalidade em $Mf$ (H04.2).**
   - (a) Com erro relativo uniforme e início comum ($Mf=0{,}0074$), A e $M=30$ (mesmos $q$ e $\chi$) dão **exatamente**
     os mesmos cortes em $Mf$ e o mesmo $D$:
     - $K=2$: 0,050, $D$ = 27,7033;
     - $K=3$: (0,0095; 0,0101), $D$ = 34,6012;
     - $K=4$: (0,0095; 0,0101; 0,050), $D$ = 38,4416.

     $M=150$ dá os mesmos cortes, com $D$ = 34,6200. A diferença de 5e-4 vem só da primeira borda: 10 Hz não cai na grade.
     Isso confirma numericamente o argumento de escala [D]: sem detector, o Fisher só depende de $Mf$, $q$ e $\chi$.
   - (b) Com outro $(q,\chi)$ o ótimo muda: $q=3$ dá (0,0108; 0,0115).
   - (c) Com o ruído de CE, mesmo com início comum, o segundo corte de $K=3$ deriva com $M$: $Mf$ = 0,023 ($M=30$),
     0,028 (A, 65) e 0,036 ($M=150$); em Hz, 157, 88 e 49. Em Hz o corte escala como $M^{-0{,}72}$, e não $M^{-1}$: a
     curva de ruído puxa o ótimo para a banda sensível.

     **H04.2 vale como identidade de escala sem ruído e só aproximadamente com ruído.**
   - (d) O primeiro corte (o pico) é universal por construção: está preso a $f_{\rm pico}\propto1/M$.
5. **Artefato do modelo uniforme.** Com erro relativo fixo por banda, o ótimo de $K=3$ escolhe duas bordas **adjacentes**
   (0,0095; 0,0101): uma banda estreitíssima vale tanto quanto uma larga. É irrealista, e é o que o modelo pedido
   (1/SNR por banda, `diag`) e o correlacionado corrigem: neles as bandas estreitas têm SNR pequena.
6. **ET.** Mesma estrutura, com ganhos menores (A: $D$ = 5,08 → 6,29 → 6,64, `diag`).


## 6. Tentativas de refutação e alternativas

1. **"Memória de banda = diferença de $E_b$" (H03.1).** Cinco maneiras de tentar derrubá-la:
   - (i) recalcular $\alpha_L$ com amplitudes independentes (ABFO) e comparar com a razão de Cunningham et al.: os
     coeficientes coincidem até 1,5PN;
   - (ii) verificar a integral $\int\alpha E_b'$ contra o $H_{20}$ publicado: coincide termo a termo;
   - (iii) comparar com o substituto, que não usa nenhuma das hipóteses PN;
   - (iv) separar o erro em erro de energia e erro de $\alpha$ (seção 5.2);
   - (v) procurar um termo que a fatoração não captura: a absorção no horizonte, que entra em $H_{20}(x)$ pelo
     $\dot x$ total e não pelo fluxo no infinito.

   A hipótese resiste na inspiral até ~1e-3 com spins e ~1e-5 sem spins. Na fusão ($Mf\gtrsim0{,}01$) a expansão PN
   satura, e a frase "diferença de $E_b(f)$" vale só onde $E_b(f)$ existe.
2. **"Um número por ordem PN" (H03.4) — refutada na forma ingênua.** O deslocamento e o spin têm coeficientes de 1PN
   diferentes, $c_d(\nu)\ne c_s(\nu)$, e por isso 1PN dá dois números ($M$ e $\nu$), não só $\eta$. Isso se confirma no
   jacobiano das bandas PN (posto 2 → 4 → 6). Alternativas testadas:
   - só deslocamento: o posto cresce de 1 em 1 por ordem;
   - incluir a giroscópica: não muda nada;
   - incluir a ordem 2PN: não acrescenta posto;
   - trocar a grade de bandas ($K=3$ a 49): os mesmos postos.
3. **Pares e família.** O LM próprio substituiu o `least_squares` (trf com limites), que estagnava em 1,7e-4 nos
   problemas subdeterminados. A culpa era do algoritmo, não do modelo: um Gauss-Newton de norma mínima chegou a 7e-11
   em 5 iterações a partir do mesmo ponto (rascunho conferido). A segunda versão do perfil passou a partir de A em cada
   $q_B$, com varredura para cima e para baixo, para não ficar presa num ramo distante.
4. **Desenho ótimo.** A primeira grade terminava em $Mf=0{,}030$, e o ótimo de $K=2$ caía na **borda** da grade em todas
   as fontes (`resultados/exp23_desenho_grade030.txt`). Estendi a grade até $0{,}9\,f_{\rm pico}$ ($Mf\approx0{,}050$) e
   refiz tudo; a seção 5.6 usa a grade estendida. Usei três modelos de ruído (diagonal, correlacionado, relativo
   uniforme), dois detectores (CE, ET), dois critérios (D, E) e uma referência ingênua (cortes geométricos).
5. **Universalidade em $Mf$.** Testada em duas condições: só o ruído relativo uniforme com início comum, e o CE com
   início comum. Esta separa o efeito da curva de ruído do efeito da faixa disponível acima de 10 Hz.
6. **Erro meu corrigido.** Em `exp20_comum.jacobiano` o segundo valor devolvido é o valor **bruto** $y$, não $\ln|y|$.
   Duas versões preliminares (bandas do exp21 e Y do exp23) o exponenciavam; corrigi as duas antes de qualquer número
   relatado. A docstring agora diz isso.
7. **Primeira lei modo a modo.** A "identidade" falhou na primeira versão (razões de até 1e2) porque eu incluía as
   pontas da série e o fim do toque, onde a amplitude é ruído. Restrito a $t_i+50<u<60$ e $A>10^{-2}A_{\max}$, o desvio
   fica no arredondamento (seção 5.3).

## 7. Contraexemplos e limitações

- **Modelo.** Tudo é NRHybSur3dq8_CCE, nível A: spins alinhados, $q\le8$, modos de entrada $\ell\le5$ sem (3,1),
  (4,2), (4,1). A diferença entre modelos de $E_{\rm janela}$ é ~1e-4 (L00), do tamanho do patamar de 1e-3 relativo
  das bandas com spin na inspiral.
- **PN.** Amplitudes SO só até 1,5PN (ABFO), e por isso $\beta$ só até 1,5PN. As ordens superiores do spin melhoram
  só pela $E_b$. O 1,5PN SO de $\beta_3$ não tem conferência independente: os modos com spin até 3,5PN existem (Henry, Marsat & Khalil 2022, ref. HMK22 de
  Blanchet LRR 2024), mas não os extraí.
- **CM e giroscópica.** Entram só no conjunto teórico (T0, T). Interferômetros não medem a giroscópica, e a CM é
  degenerada com o tempo de chegada (item 5 da revisão).
- **Bandas finas.** As bordas definidas pela frequência instantânea herdam as oscilações de $\omega_{22}$ do
  substituto. Com bandas de largura ≲ 3% em $f$, os jacobianos das bandas tardias deixam de ser suaves (seção 5.4).
- **Modelo de ruído.** O deslocamento é medido em + e o spin em ×, cada um com detector ótimo. É uma idealização: um
  detector mede $F_+h_++F_\times h_\times$, e as duas polarizações competem. A forma dentro de cada banda é tratada
  como conhecida (só a amplitude é estimada); isso **superestima** a informação de muitas bandas finas. As bandas
  suaves (partição da unidade com transição de ±2% em $f$) diferem das nítidas em ≤ 7e-3, exceto a primeira banda
  estreita (até 80%, sem efeito: SNR ~1e-5).
- **Prior.** O critério D com prior gaussiano depende das larguras escolhidas. O critério E é degenerado sempre que
  $2K<6$, e na prática sempre (direções sem informação).
- **Multipolos $m\ne0$ e $\phi$.** Nos conjuntos T e O a direção mais fraca é $\phi$ na escala de 0,01 rad. Com
  escala de 1 rad o ordenamento muda; não refiz o desenho com $m\ne0$.

## 8. Literatura e originalidade

Como conferi:
- API do arXiv (`export.arxiv.org/api/query`), com buscas por título, resumo e autor:
  - "memory" + spin-orbit / post-Newtonian / "spin memory" / bands / "binding energy" / "first law" / Fisher /
    identifiability / "optimal design";
  - autores Cunningham, Nichols, Favata;
- WebSearch;
- leitura das fontes LaTeX de arXiv:2410.23950, 0810.5336, 1310.1528v6, 1702.03300, 1807.08767, 2403.13907,
  2409.02624, 0812.0069 e 0902.3660 (notas de rodapé de Favata).

O que já existe [E]:
- memória ∝ energia irradiada na ordem dominante (Favata, PRD 80, 024002, 2009, nota 4: $\delta h\sim\Delta E^{\rm gw}/R$,
  $\Delta E\approx(\eta M/2)(M/r)$);
- $H_{20}$, $H_{40}$ (e $\ell=6,8$) até 3,5PN com spins alinhados (Cunningham et al., CQG 42, 135009, 2025, suplemento);
  sem spin até 3PN (Favata 2009). Com isso, a memória de deslocamento de banda até 3,5PN é uma aplicação direta;
- memória de spin dominante, $\propto\eta M^2x^{-1/2}$ (Nichols 2017); a taxa é o modo (3,0) não oscilatório,
  conhecido até 1PN sem spin (Blanchet LRR 2024, eq. H30);
- CM só em 3PN/4PN (Nichols 2018);
- primeira lei $dE=\Omega\,dJ$ para órbitas circulares (Le Tiec, Blanchet & Whiting, PRD 85, 064039, 2012);
- amplitudes SO 1,5PN (Arun, Buonanno, Faye & Ochsner, PRD 79, 104023, 2009);
- degenerescência qualitativa da memória sozinha (McNeill et al. 2017; Ebersold & Tiwari 2020);

O que não achei (lacunas que parecem abertas; [D] aqui):
- a fatoração explícita $dm/dx=\alpha(x)E_b'(x)$, com o cancelamento do fluxo (e das caudas) e a ressalva do horizonte.
  Está implícita nos cálculos de Favata e Cunningham, mas não a encontrei enunciada como propriedade dos observáveis de
  banda;
- as razões $\alpha_4$, $\beta_3$ e as giroscópicas com SO, e a série $S_{30}(x)$ com o termo 1,5PN SO. O 1PN de
  $\beta_3$ é consequência de resultados conhecidos (conferido); o SO não achei;
- a contagem de posto ordem a ordem (2, 4, 6) e o espectro de valores singulares de $K$ janelas;
- desenho ótimo (critérios D e E) de bandas de memória, e o teste de universalidade em $Mf$;
- a explicação da parte nula da CM de banda como termo de borda (seção 5.1).

Não reivindico originalidade das expressões PN de deslocamento, nem da primeira lei.

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H03.1 | Memória de banda = função de $E_b(x)$ e $J(x)$ (primeira lei), sem o fluxo | confirmada matematicamente (fatoração; caudas cancelam) e numericamente (Cunningham termo a termo; substituto 1,2e-5 sem spin, ~1e-3 com spin, patamar na energia) | 2.1, 5.1, 5.2 |
| H03.1' | ... e é "$\Delta E_b$" puro | refutada | $\alpha(x)$ tem correções de 1PN, $-1051/2016+71\nu/24$ |
| H03.2 | $dE_{\ell m}/dJ_{\ell m}=\omega_{\ell m}/m$ | refutada na forma exata; confirmada matematicamente com o fator $1+\varepsilon^2$ | identidade; substituto: ≤ 3e-4; $\varepsilon^2$ 2e-6 (inspiral) a 2e-2 (toque) |
| H03.3 | Na ordem N as bandas só veem $\mathcal M^{5/3}/D$ (e $\iota$) | confirmada matematicamente e numericamente | posto 2 no modelo PN N ($\sigma_3$ ~ 1e-12) |
| H03.4 | 1PN acrescenta só $\eta$; 1,5PN uma combinação SO | refutada (forma ingênua): cada ordem acrescenta **dois** | posto 2 → 4 → 6 (5.4) |
| H03.5 | Cada janela extra acrescenta ~2 números | confirmada numericamente | T0 4 → 6; O0 2 → 4 → 6 |
| H03.5' | Muitas janelas (função contínua) acrescentam direções | refutada | $\sigma_i/\sqrt K$ estável de $K=2$ a 49 (T0) |
| H03.6 | A família aproximada encolhe com $K$ | refutada para T0 além de $K=2$; confirmada fracamente para O0 ($K=3\to4$: inclinação ×4,3), mas sempre ≪ precisão de medida | T0: ≤ 17% de $K=2$ a 4; O0: resíduos 2e-6 → 8e-6 |
| H03.7 | Bandas do substituto = PN, com erro caindo ordem a ordem | confirmada numericamente na inspiral sem spin; com spin satura em ~1e-3 (energia do modelo) | 5.2 |
| H03.8 | Parte nula da CM de banda = termo de borda | refutada (borda prevista ~1e-23, medida 1e-5); origem [H] modelo | 5.1, `exp20_cm_borda.txt`, `exp20_cm_dt.txt` |
| H04.1 | Duas janelas tornam o mapa localmente injetivo (posto 6) | confirmada numericamente para T0 ($\sigma_6$ = 5,2e-4); refutada para O0 (precisa de 3, $\sigma_6$ = 1,1e-6). Com ruído realista nenhum $K$ basta | 5.4, 5.6 |
| H04.2 | Fronteiras ótimas universais em $Mf$ | confirmada matematicamente e numericamente sem detector; refutada com o ruído de CE/ET ($\propto M^{-0{,}72}$ em Hz); o corte principal (pico) é universal | 5.6 |
| H04.3 | Com ruído realista mais bandas não acrescentam informação | confirmada numericamente acima de $K=3$; de 1 para 2 bandas o ganho é real (~2,2 bits, na escala de massa) | 5.6 |
| H03.9 | $\pi f\,dS/dh$ mede $\iota$ independentemente da massa e da distância (teste da primeira lei) | confirmada matematicamente na ordem dominante; não testada com ruído | 2.3 |

## 10. Próximos experimentos

1. Extrair os modos com spin de HMK22 (citado em Blanchet LRR 2024) para conferir o 1,5PN SO de $\beta_3$ e levar $\beta$ a
   2PN; com isso, a previsão da memória de spin de banda chega a 2PN completo.
2. Desenho ótimo com a resposta real de um detector ($F_+h_++F_\times h_\times$), as duas polarizações juntas e
   marginalização sobre $t_0$ e $\psi$ (como em L05), em vez de + e × ótimos e separados.
3. Repetir a tarefa 3 (família) com o conjunto mensurável e ruído: resíduo mínimo em unidades de $\sigma$ do modelo
   correlacionado, em vez de resíduo relativo.
4. Bandas definidas por **tempo** em vez de frequência, e bandas definidas pela frequência suavizada (média orbital),
   para separar a estrutura fina de $\omega_{22}$ (seção 5.4) da física.
5. Testar a razão $\pi f\,dS/dh$ como medida de $\iota$ e teste da primeira lei em populações (CE + ET), onde o spin
   tem SNR acumulada maior.


