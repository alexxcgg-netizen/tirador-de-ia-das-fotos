# L08 e L09 — Recuperação exata da fase pelos fluxos; memória no *ringdown* (agente D5)

**Modelo.** NRHybSur3dq8_CCE.

**Infraestrutura.** `codigo/observaveis.py` (L00):
- rede fixa;
- $t_i$ exato;
- derivada de 8ª ordem.

**Sistemas.**
- Sistema A: $M=65$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, janela desde 10 Hz.
- Os cinco sistemas do exp09, com $Mf_0=0{,}006$:
  - $q=1$, 2 e 4 sem spin;
  - $q=1$ com $\chi=(0{,}6;0{,}6)$;
  - $q=3$ com $\chi=(0{,}6;0)$.

**Scripts e saídas.**
- Scripts: `codigo/exp30_comum.py`, `exp30_fase_exata.py`, `exp31_varios_modos.py`, `exp32_fase_ruido.py`,
  `exp32_ringdown.py`.
- Saídas: `resultados/exp30_*`, `exp31_*`, `exp32_*`.
- Figuras: `figuras/e30_fase_exata.png`, `figuras/e31_varios_modos.png`.

Rótulos: [E] estabelecido, [D] derivado aqui, [H] hipótese, [S] especulação.

**Resumo.**

1. **Identidade [D, demonstrada].** Para $h=a\,e^{-i\psi}$ valem $u\equiv a^2$, $\dot u^2=4(uP-H^2)$,
   $\dot\psi=H/u$ e $P/H=\dot\psi/(1-\dot a^2/P)$ (sympy, resíduo 0). Geometricamente, $h(t)$ é uma curva plana:
   - $P$ é o quadrado da velocidade;
   - $H$ é o momento angular em torno da origem;
   - a equação é o problema radial $\dot r^2=P-H^2/r^2$.
2. **Unicidade [D].** A hipótese do 09 ("$a\to0$ no passado fixa a solução") é **falsa**. Antes do pico, todas as
   soluções vizinhas convergem para a verdadeira quando $t\to-\infty$. A solução é fixada pelo **ponto de retorno**:
   - $t_p=\arg\max(H^2/P)=\arg\max|h|$ e $\max(H^2/P)=\max|h|^2$, porque $H^2/P\le|h|^2$ com igualdade só onde
     $\dot a=0$;
   - em $t_p$ as perturbações se comportam como $|t-t_p|^{-\kappa}$, com $\kappa=a\dot\psi^2/|\ddot a|=54{,}6$ no
     sistema A;
   - só a solução verdadeira atravessa o pico. As outras fogem ($u$ chega a $10^3$–$10^4$ vezes o verdadeiro) ou
     deixam de ter solução real antes dele.

   Nos mínimos de amplitude a unicidade falha localmente. Dois contraexemplos de unicidade:
   - um círculo e a sua tangente têm $P$ e $H$ iguais a $8\times10^{-16}$;
   - dois surtos disjuntos (revisão, A7).
3. **Estabilidade [D + numérico].**
   - Integrar para frente desde o passado é impossível: amplificação $10^{1{,}59\times10^5}$ entre $t_i$ e
     $t_p-1$ M. Partindo do valor exato em $t=-1000$ M, a integração (RK45) perde a solução real em 1 M.
   - Integrar a partir do ponto de retorno (para trás antes do pico, para frente depois) é **bem condicionado**:
     um ruído relativo em $P/H$ passa a $\dot\psi$ com fator 1,00, e um erro de 10% em $u(t_p)$ cai para
     $4\times10^{-5}$ em 1 M.
4. **Teste (a), $P$ e $H$ do próprio (2,2) [numérico].**
   - A EDO a partir do ponto de retorno reconstrói $\dot\psi$ com erro $\le1{,}5\times10^{-9}$ na inspiral,
     $\le1{,}2\times10^{-5}$ até $t_p+30$ e $\le2{,}6\times10^{-5}$ até $t_p+60$ (seis sistemas mais a rede deslocada).
   - O estimador adiabático $P/H$ (o $\Omega_{\rm mem}$ do exp09) erra no máximo $1{,}9\times10^{-3}$ antes do pico
     e 1–3,5% depois.
   - Erro de fase do adiabático: 0,015–0,025 rad acumulados até o pico e 0,13–0,29 rad até $t_p+30$.
5. **Testes (b) e (c), $P$ e $H$ dos modos de memória.**
   - Leis de balanço: erro mediano em $\Omega$ de 1,5–3,3% na inspiral e 4–8% no fim. **A EDO não melhora nada.**
   - A hipótese de que a sobre-estimativa adiabática explicaria o erro de fusão do exp09 está **refutada**: ela
     vale $\le0{,}2\%$ antes do pico.
   - O erro vem da **estrutura angular**: é o termo cruzado $(2,2)\times(3,2)$, linear em $h_{32}/h_{22}$, com
     viés $-3{,}6\,{\rm Re}(h_{22}\bar h_{32})/|h_{22}|^2$. A soma linear dos pares prevê o viés medido:
     −1,52% contra −1,47% em A, −2,18% contra −2,06% em $q=4$.
   - Os modos $m=0$ do substituto (RN) são inconsistentes com um único modo: o ponto de retorno cai em 7–48 M
     depois do pico, e milhares de passos caem na fronteira.
6. **Vários modos [D + numérico].**
   - Os pesos angulares por par estão tabelados. Os modos com $\ell=3$ **não** contribuem para a projeção $L=2$ do
     fluxo de energia (zero exato do 3j).
   - Com as 7 projeções $m=0$ ($E_{2,4,6,8}$, $J_{3,5,7}$), a separação em cada instante funciona em massas quase
     iguais: $\Omega$ a ~$10^{-3}$ e sobreposição do (2,2) reconstruído de 0,975 em A e 0,999 em $q=1$,
     $\chi=0{,}6$.
   - Falha em $q=4$ (sobreposição ≤ 0,25) e depende da escolha de pares e de pesos.
   - São 7 equações para ≥ 10 amplitudes de pares mais $\Omega$: a separação **não** é independente de modelo.
7. **Equivalência sem ruído (pergunta do usuário).**
   - Os multipolos $m=0$ de memória, resolvidos no tempo e **separados no céu**, determinam o modo dominante a
     menos de uma fase constante (único modo, suporte conexo, amplitude unimodal) [D].
   - Na prática, a contaminação pelos outros modos limita a fase a vários radianos.
   - Os multipolos $m\ne0$ do fluxo resolvido no tempo carregam a **própria fase orbital**:
     $\arg E_{44}+4\phi_{\rm orb}$ varia só 0,13 rad em 65 rad (A).
   - Um **único observador** com $\iota$ desconhecido mede $\Omega(t)$ só a menos de um fator constante $K(\iota)$:
     ±10° em $\iota$ dá +18% e −21,5%. É uma ambiguidade exata da EDO (teste de escala: $\dot\psi'/\dot\psi=\lambda/\mu$
     a $10^{-5}$ na inspiral).
8. **Com ruído (Fisher da memória nula do D3, linearizado), resposta à pergunta.** A fase prevista do (2,2) até o
   pico tem os seguintes desvios em CE ($\rho=34$):

   | Desde | Desvio | Informação |
   |---|---|---|
   | 10 Hz | 56 rad | 0 bit |
   | 20 Hz | 19 rad | 0 bit |
   | 100 Hz | 1,2 rad | 0,4 bit |
   | 5 ms antes do pico | 0,76 rad | 1,0 bit |
   | 2 ms antes do pico | 0,34 rad | 2,1 bits |

   Em ET ($\rho=8{,}6$) os números são piores. A memória sozinha recupera a fase (≥ 1 bit) só nos últimos ~5 ms
   antes da fusão (≈ 0,7 ciclo), de 81,6 ciclos na banda. Mesmo isso vem do modelo de binária (massa e instante), não de uma recuperação de
   fase.
9. **L09 [confere com Elhashash & Nichols 2025].**
   - A taxa da memória decai como $2\Gamma_{220}$ a 0,3–0,7% (janela $[30,55]$ M depois do pico, só o (2,2)).
   - O batimento 220–221 é **superamortecido**: $\Delta\omega/(\Gamma_0+\Gamma_1)=0{,}034$–$0{,}050$, sem oscilação
     visível.
   - A oscilação visível na taxa completa (~0,21–0,22/M) é compatível com o par $(2,2)\times(3,2)$ (0,238/M).
   - O resíduo RN − nula do modo (2,0) toca na frequência do QNM linear (2,0,0) (≤ 1% em A e $q=1$), já apontado na
     literatura de CCE.
   - Nada de novo além dessas observações.

---

## 1. Pergunta e hipóteses

**Pergunta (L08).** As séries temporais de $P=|\dot h|^2$ e $H=-{\rm Im}(\bar h\dot h)$ determinam o modo dominante sem
aproximação adiabática? Com que condição de unicidade, com que estabilidade, e o que sobra quando $P$ e $H$ vêm dos
modos de memória, de vários modos ou de um detector com ruído?

**Pergunta (L09, curta).** A taxa da memória depois do pico é a soma sobre pares de QNMs (Elhashash & Nichols)?
Isso acrescenta algo?

Hipóteses (status na seção 9):
- **H08.1** $\dot u^2=4(uP-H^2)$, $\dot\psi=H/u$, $P/H=\dot\psi/(1-\dot a^2/P)$.
- **H08.2** (do 09) A condição inicial "$a\to0$ no passado" fixa a solução.
- **H08.3** O ponto de retorno é $t_p=\arg\max(H^2/P)$, com $u(t_p)=\max(H^2/P)$.
- **H08.4** Unicidade pelo ponto de retorno: com amplitude unimodal de máximo não degenerado, $H>0$ e $u\to0$ em
  $\pm\infty$, a solução é única.
- **H08.5** No regime adiabático, a integração da EDO para frente é mal condicionada. A integração a partir do ponto
  de retorno é bem condicionada.
- **H08.6** Com $P$ e $H$ do próprio (2,2), a reconstrução é exata até a fusão.
- **H08.7** (do 09) A sobre-estimativa $1/(1-\dot a^2/P)$ explica parte do erro de fusão do exp09 (4–8%).
- **H08.8** O erro de $\Omega_{\rm mem}$ vem da contaminação angular por pares de modos, sobretudo $(2,2)\times(3,2)$.
- **H08.9** As projeções $L=2..8$ permitem separar os modos.
- **H08.10** Sem ruído, os multipolos de memória resolvidos no tempo equivalem à onda oscilatória a menos da fase
  orbital.
- **H08.11** Para um único observador, $\Omega(t)$ fica determinada a menos de um fator $K(\iota)$.
- **H08.12** Com ruído realista, a memória quase não recupera fase.
- **H09.1** A taxa da memória decai como $e^{-2t/\tau_{220}}$.
- **H09.2** Há batimentos visíveis em $\omega_{220}-\omega_{221}$.
- **H09.3** O resíduo RN − nula do (2,0) é o toque linear do QNM (2,0,0).

## 2. Fundamentação e equações

### 2.1 Identidade e geometria [D]

Com $h=a e^{-i\psi}$ e $\dot h=(\dot a-ia\dot\psi)e^{-i\psi}$:

$$P=\dot a^2+a^2\dot\psi^2,\qquad H=a^2\dot\psi,\qquad \bar h\dot h=\tfrac12\dot u-iH .$$

Como $|\bar h\dot h|^2=|h|^2|\dot h|^2$, vale $\tfrac14\dot u^2+H^2=uP$, isto é, $\dot u^2=4(uP-H^2)$, e
$\dot\psi=H/u$. Além disso,

$$\frac PH=\dot\psi\Big(1+\frac{\dot a^2}{a^2\dot\psi^2}\Big)=\frac{\dot\psi}{1-\dot a^2/P},$$

de modo que o estimador adiabático sempre superestima. O sympy confirma as três identidades com resíduo 0
(`exp30_fase_exata.txt`, seção 1).

**Geometria.** $h(t)$ é uma curva no plano complexo, $P$ é o quadrado da velocidade e $H$ é o momento angular em torno
da origem. Com $r=a$:

$$\dot r^2=P-H^2/r^2 .$$

É o problema radial de uma partícula de velocidade e momento angular dados. Os pontos de retorno ($\dot r=0$) são
os extremos da amplitude.

**Ligação com a etapa 6.**
- O estimador $\Omega=P/(2H)$ é a relação de órbita circular $\dot E=\Omega\dot J_z$ [E].
- A proposição 2.6 do 07 usa $Q=h\dot h^\dagger$ inteiro. A parte ${\rm Re}\,Q=\dot u/2$ já dá $u$ por integração,
  e o problema fica trivial.
- O L08 é a versão sem ${\rm Re}\,Q$, que é o que os modos de memória fornecem.

### 2.2 Fronteira e ponto de retorno [D]

Seja $v\equiv uP-H^2=u\dot a^2\ge0$. Então

$$u\ge u_b\equiv H^2/P,\qquad\text{com igualdade se e só se }\dot a=0 .$$

Como $u_b\le u\le\max u=u(t_p)=u_b(t_p)$, o máximo global de $u_b$ é o máximo global de $u$, no mesmo instante
**(H08.3)**. Em $t_p$, $v$ tem zero duplo e $\dot u_b(t_p)=0$.

### 2.3 Linearização, estabilidade e unicidade [D]

Diferenciando $\dot u^2=4(uP-H^2)$:

$$\delta\dot u=\frac{2P}{\dot u}\,\delta u+\frac{2(u\,\delta P-2H\,\delta H)}{\dot u}.$$

**Antes do pico** ($\dot u>0$). A taxa $2P/\dot u\approx\dot\psi/\sqrt\varepsilon$, com
$\varepsilon=\dot a^2/(a^2\dot\psi^2)$, é enorme:
- integrar para frente amplifica por $\exp\int2P/\dot u$;
- integrar para trás contrai. O forçamento, dividido pela taxa, dá $\delta u\approx-(u\,\delta P-2H\,\delta H)/P$:
  condicionamento de ordem 1.

**Depois do pico** ($\dot u<0$), as duas direções se invertem.

**Perto do ponto de retorno.** Com $\dot u\approx2a\ddot a(t-t_p)$ vem $\delta u\propto|t-t_p|^{-\kappa}$, com

$$\kappa=\frac{P}{a|\ddot a|}\Big|_{t_p}=\frac{a\dot\psi^2}{|\ddot a|}\Big|_{t_p}>0 .$$

Só $\delta u\equiv0$ chega a $t_p$ regularmente, dos dois lados. É uma singularidade do tipo Briot–Bouquet com
expoente negativo, logo com solução única pelo ponto. Num **mínimo** de $a$, $\ddot a>0$ dá
$\delta u\propto|t-t_m|^{+\kappa_m}$: todas as soluções vizinhas passam pelo ponto (não unicidade local). Elas são
fixadas pelos máximos adjacentes.

**Proposição (um modo) [D; demonstração no nível linearizado].** Suponha:
- $h\in C^2$ com $a>0$ e $H>0$;
- $a$ unimodal, com máximo não degenerado ($\ddot a(t_p)<0$);
- $a\to0$ em $\pm\infty$;
- $u_b$ com um único ponto crítico.

Então a única solução $C^1$ positiva de $\dot u^2=4(uP-H^2)$ com $u\to0$ em $\pm\infty$ é $u=|h|^2$, e
$h=\sqrt u\,e^{-i\int H/u}$ a menos de uma fase constante.

*Esboço.*
1. Uma solução que vai a zero nos dois lados tem um máximo, onde $\dot u=0$, isto é, $v=0$.
2. Fora de um ponto crítico de $u_b$, $v=0$ implica $\dot v=-P\dot u_b\ne0$, e a solução sai da região real.
3. Logo a troca de ramo só ocorre em $t_p$, com $u=u_b(t_p)$.
4. Pela linearização, a solução que chega a $(t_p,u_b(t_p))$ é única de cada lado.
5. As que não trocam de ramo crescem para sempre ($u\to$ constante positiva) ou morrem.

O passo não linear (teorema de Briot–Bouquet) não foi escrito em detalhe.

**Contraexemplos.**
- Amplitude constante ($\ddot a=0$, sem retorno não degenerado): o círculo e a reta tangente colada nele têm $P$ e $H$
  idênticos (seção 4.1).
- Suporte desconexo: fases relativas livres (revisão, A7).
- A condição "$a\to0$ no passado" sozinha (H08.2): falha, porque as soluções vizinhas convergem para a verdadeira
  quando $t\to-\infty$.

### 2.4 Algoritmos

- **Iteração:** $\dot\psi_{n+1}=(P-\dot a_n^2)/H$, com $a_n^2=H/\dot\psi_n$. O fator de contração é
  $\sim\sqrt\varepsilon/(T\dot\psi)$, onde $T$ é a escala de tempo da perturbação.
- **EDO:** trapézio implícito a partir de $k_p=\arg\max u_b$, com $u(k_p)=u_b(k_p)$:
  - ramo $+$ para trás e ramo $-$ para frente;
  - em cada passo, raiz única (Brent) da equação escalar monótona;
  - se não há raiz real, o passo é posto na fronteira ($u=u_b$, o valor adiabático). A contagem desses passos
    ("clip") mede a inconsistência dos dados com um único modo.

### 2.5 Fluxos projetados nos modos de memória [E + D]

Para o par $(2,\pm2)$ puro:

$$\dot h_{20}^{\rm mem}=C_EP,\qquad {\rm Im}\,h_{30}^B=C_JH,$$

com $C_E=\sqrt{30}/(42\sqrt\pi)=0{,}073576$, $C_J=\sqrt{210}/(280\sqrt\pi)=0{,}029200$ e $C=2C_E/C_J=40\sqrt7/21$
(item 12 da revisão). Com vários modos, na aproximação circular ($\dot h_{\ell m}\approx-im\Omega h_{\ell m}$):

$$E_L=\Omega^2\sum_pm_p^2\,g^E_{L,p}X_p,\qquad J_L={\rm Im}\,h^B_L=\Omega\sum_pm_p\,g^J_{L,p}X_p,$$

com $X_p=|h_{\ell m}|^2$ (par próprio) ou ${\rm Re}(h_{\ell m}\bar h_{\ell'm})$ (par cruzado de mesmo $m$; a parte
imaginária não contribui, $<10^{-16}$).

O estimador de um modo tem viés linear

$$\frac{\Omega_{\rm est}}{\Omega}-1\simeq\sum_pb_p\frac{X_p}{|h_{22}|^2},\qquad b_p=\frac{m_p^2g^E_{2,p}}{4g^E_{2,22}}-\frac{m_pg^J_{3,p}}{2g^J_{3,22}} .$$

**Zero do 3j.** O peso $g^E_{2,p}$ dos modos com $\ell=3$ é zero. O fator angular contém
$\begin{pmatrix}3&3&2\\2&-2&0\end{pmatrix}\propto3s^2-\ell(\ell+1)=12-12=0$ [D]. Esse zero não foi verificado na
literatura.

### 2.6 Um observador [D]

No observador, para o (2,2), vale $h_+^{\rm mem}=(C_EY_{20}+g^E_{4,22}Y_{40})\!\int P$ e
$h_\times^{\rm mem}=-C_JY_{30}H$ (com ${}_{-2}Y_{L0}(\iota)$ reais). Logo

$$\Omega_{\rm obs}=K(\iota)\,\frac{\dot h_+}{2h_\times},\qquad K(\iota)=-\frac{C_JY_{30}(\iota)}{C_EY_{20}(\iota)+g^E_{4,22}Y_{40}(\iota)} .$$

Com $\iota$ desconhecido, os dados $(\lambda P,\mu H)$ admitem solução da mesma EDO:
$w=(\lambda/\mu^2)u'$ satisfaz $\dot w^2=4(\lambda/\mu)^2(wP-H^2)$. Assim $\dot\psi'\approx(\lambda/\mu)\dot\psi$,
com correções $O(\varepsilon)$, e a escala de $\Omega$ e o número de ciclos ficam livres **(H08.11)**.

### 2.7 Multipolos $m\ne0$ [D]

$E_{L,4}$ recebe o par $(2,2)\times\overline{(2,-2)}$, e assim $E_{44}\propto\dot h_{22}^2\propto e^{-4i\phi_{\rm orb}}$.
Os pares com $m-m'=1$ dão $E_{L,1}\propto e^{-i\phi_{\rm orb}}$; só $L+M$ par sobrevive, pela reflexão.

O padrão do fluxo no céu gira com a binária. Com só o (2,2), a simetria de ordem 4 deixa a ambiguidade
$\phi\to\phi+\pi/2$, que é $h_{22}\to-h_{22}$: o "a menos de um sinal" da revisão.

### 2.8 Ruído

A fase prevista entre dois instantes observados, $t_a$ e o pico $t_b$, é
$\Delta\psi=\Psi_\theta((t_b-t_0)/M)-\Psi_\theta((t_a-t_0)/M)$. Os gradientes são:
- $\partial_{\ln M}=-(t_b\dot\psi_b-t_a\dot\psi_a)$;
- $\partial_{t_0}=-(\dot\psi_b-\dot\psi_a)/M_s$;
- $\partial_{q,\chi}$ por diferenças centrais, com passos de $10^{-3}$ e $2\times10^{-3}$, que concordam a
  $3{,}7\times10^{-5}$.

O desvio é $\sigma^2=g^{\rm T}\Sigma g$, com $\Sigma=(G+\Sigma_p^{-1})^{-1}$, $G$ do D3 e o prior do D3. A
informação sobre a fase módulo $2\pi$ é $I=\log_2 2\pi-h(\text{normal enrolada})$ bits.

### 2.9 L09 [E]

Elhashash & Nichols (arXiv:2504.18635v2, eq. 44 da versão HTML, a "3.29" do contexto) escrevem
$h_{20}^{\rm rd}$ como soma sobre pares de QNMs de mesmo $m'$. Cada par contribui com o fator
$\exp[-i(\omega_{\bar\ell m'\bar n}-\bar\omega_{\bar{\bar\ell}m'\bar{\bar n}})(t-t_0)]$, com os modos (2,2), (3,2) e
(2,1), oito sobretons cada e só prógrados, conferido por WebFetch. A taxa tem, portanto:
- frequências ${\rm Re}(\omega_n-\omega_{n'})$;
- amortecimentos $\Gamma_n+\Gamma_{n'}$.

O fator de batimento [D, elementar] é $Q_b=|\Delta\omega|/(\Gamma_n+\Gamma_{n'})$.

## 3. Experimentos

| Script | O que faz | Saída | Tempo |
|---|---|---|---|
| `exp30_comum.py` | constantes, fluxos dos modos e da memória (via `exp24_comum.taxas_m0`), reconstruções adiabática, iterativa e EDO, métricas | — | — |
| `exp30_fase_exata.py` | álgebra (sympy); contraexemplo da tangente; ponto de retorno, $\kappa$, amplificação, RK45 para frente, família perturbada, contração desde $t_p$, sensibilidade a ruído suave e branco, ambiguidade de escala; testes (a), (b), (c) em 6 sistemas mais rede deslocada (`t_desloc`=0,37) | `resultados/exp30_fase_exata.{txt,json}`, `figuras/e30_fase_exata.png` | 43 s |
| `exp31_varios_modos.py` | pesos $g^E$, $g^J$ por par (sinais circulares sintéticos); decomposição de $E_2$, $J_3$; viés linear; separação por instante (conjuntos S1–S5, pesos relativos "rel" ou escalados "esc"); observador ($K(\iota)$); multipolos $m\ne0$ | `resultados/exp31_varios_modos.{txt,json}`, `figuras/e31_varios_modos.png` | 69 s |
| `exp32_fase_ruido.py` | Fisher do D3 (`resultados/exp24_fisher_memoria.json`) → desvio da fase prevista do (2,2) | `resultados/exp32_fase_ruido.{txt,json}` | ~1 min |
| `exp32_ringdown.py` | remanescente (NRSur3dq8Remnant) e QNMs (`qnm`); decaimento local de $\log R_2$; *matrix pencil* da taxa e do resíduo RN − nula | `resultados/exp32_ringdown.{txt,json}` | ~1 min |

Condições: `OMP_NUM_THREADS=1`, no máximo 2 processos, dt = 0,25 M. Só números são guardados; nenhuma forma de onda
fica em cache.

## 4. Resultados

### 4.1 Álgebra e contraexemplo (`exp30_fase_exata.txt` §1)

- O sympy dá $P=a^2\dot\psi^2+\dot a^2$, $H=a^2\dot\psi$ e resíduo 0 nas três identidades.
- Círculo ($R=1{,}3$, $\omega=0{,}7$) contra círculo seguido da tangente a partir de $t=0$:
  $\max|P_1-P_2|/P=8{,}0\times10^{-16}$ e $\max|H_1-H_2|/H=5{,}6\times10^{-16}$, enquanto $\max|h_1-h_2|=8{,}25$
  (para $|h|=1{,}3$).

### 4.2 Estrutura da EDO no (2,2) do sistema A (`exp30_fase_exata.txt` §2)

**Ponto de retorno.**
- $\arg\max(H^2/P)=-0{,}0849$ M $=\arg\max|h_{22}|$, após refinamento parabólico.
- $\max(H^2/P)/\max|h_{22}|^2-1=-3{,}1\times10^{-7}$ (discretização).
- $u_b\le u$ em toda a janela.
- $d(H^2/P)/dt$ troca de sinal uma única vez: $u_b$ é unimodal.
- $\kappa=54{,}6$, com $a=0{,}3898$, $\dot\psi=0{,}3664$ e $\ddot a/a=-2{,}46\times10^{-3}$.

**Integração para frente.**
- Taxa $2P/\dot u$: 13,3/M em $t=-1000$ e 6,0/M em $t=-100$.
- $\log_{10}$ da amplificação: $1{,}59\times10^5$ (de $t_i$ a $-1$ M), $1{,}83\times10^4$ (de −3000 a −1),
  937 (de −300 a −1), 118 (de −30 a −1).
- RK45 (rtol $10^{-13}$, $P$ e $H$ por spline):

  | Partida | Resultado |
  |---|---|
  | valor **exato** em $t=-1000$ | morre ($u=H^2/P$, sem continuação real) em $-998{,}97$ |
  | valor exato em $t=-100$ | passa de 1% de desvio em $-95{,}87$; chega a $t=20$ com $u/u_{\rm ver}=2250$ |
  | $(1-10^{-9})$ do exato | morre em 0,7–2,7 M |
  | $(1+10^{-9})$ do exato | foge (desvio de 1% em 2,8–3,4 M; $u$ chega a 970 a $1{,}2\times10^4$ vezes o verdadeiro em $t=20$) |

  A figura e30 (painel 1) mostra a família.

**Para trás desde o ponto de retorno**, com $u(t_p)$ errado:

| Erro inicial | Desvio em $t_p-1$ | $t_p-5$ | $t_p+1$ | $t_p+5$ |
|---|---|---|---|---|
| ±$10^{-3}$ | $4{,}5\times10^{-6}$ | $3{,}9\times10^{-11}$ | $2{,}4\times10^{-5}$ | $4{,}7\times10^{-12}$ |
| $10^{-1}$ | $-3{,}8\times10^{-5}$ | $-6{,}9\times10^{-10}$ | $-5{,}4\times10^{-5}$ | $-2{,}4\times10^{-11}$ |

**Sensibilidade.** $P(1+\delta_P)$ e $H(1+\delta_H)$:
- perturbação suave (20 senos, períodos de 50 a 2000 M), rms($\delta_P-\delta_H$) = $1{,}42\times10^{-3}$: a variação
  rms de $\dot\psi$ é $1{,}42\times10^{-3}$, tanto no adiabático quanto na EDO;
- ruído branco de $1{,}42\times10^{-6}$: $1{,}42\times10^{-6}$ (adiabático) e $1{,}35\times10^{-6}$ (EDO).

Condicionamento 1.

**Escala** (ambiguidade de $\iota$). Com $(\lambda,\mu)=(1{,}1;1)$, a EDO dá $\dot\psi'/\dot\psi=1{,}10000$ na
inspiral, 1,10007 no fim da inspiral e 1,0026 a 1,0042 vezes $\lambda/\mu$ depois do pico. O mesmo vale para
(1; 1,1), (1,21; 1,1) e (0,8; 1): depende só de $\lambda/\mu$. Os passos na fronteira são 11, como sem escala.

### 4.3 Teste (a): $P$ e $H$ do próprio (2,2) (`exp30_fase_exata.txt` §3)

Erro relativo de $\dot\psi$ (máximo nos 6 sistemas mais a rede deslocada):

| Região | Adiabático | Iteração | EDO |
|---|---|---|---|
| inspiral ($t_i+20$, $t_p-200$) | $\le1{,}6\times10^{-4}$ | $\le2\times10^{-9}$ | $\le1{,}5\times10^{-9}$ |
| fim da inspiral ($t_p-200$, $t_p$) | $\le1{,}9\times10^{-3}$ | $\le2{,}7\times10^{-4}$ (às vezes indefinida) | $\le6{,}2\times10^{-6}$ |
| pós-pico ($t_p$, $t_p+30$) | 1,2–3,5% | — | $\le1{,}2\times10^{-5}$ |
| toque ($t_p+30$, $t_p+60$) | 1,5–4,5% | — | $\le2{,}6\times10^{-5}$ |

- **Amplitude** $|h_{22}|$ pela EDO: $\le3{,}1\times10^{-6}$ no fim da inspiral e $\le6\times10^{-6}$ depois do pico.
  Pelo adiabático: até 0,093% e 1,7%.
- **Fase acumulada desde $t_i$:** a EDO erra $<5\times10^{-4}$ rad (impresso "−0,000") até $t_p+30$. O adiabático
  erra +0,015 a +0,025 rad até o pico e +0,13 a +0,29 rad até $t_p+30$.
- **Sobreposição** (só a fase livre) até $t_p+30$: 1,00000 (EDO) e 0,99992–0,99997 (adiabático).
- **Iteração.** Converge antes do pico ($2\times10^{-3}\to10^{-9}$ em 5 passos) e também depois dele, com dados
  exatos ($2\times10^{-2}\to10^{-6}$).
  - Por usar derivadas globais, propaga NaN a partir de onde $H<0$ (t ≳ 75 M, onde o (2,2) do substituto deixa de
    ser um modo limpo) e diverge com dados inconsistentes (RN).
  - Corrijo aqui uma conclusão minha da fase exploratória: eu atribuí a divergência a uma instabilidade de alta
    frequência depois do pico; era só o NaN do fim dos dados.
- **Rede deslocada:** $t_p$ a $-0{,}16$ M, e os mesmos erros nos dois primeiros algarismos.

### 4.4 Testes (b) e (c): fluxos dos modos de memória (`exp30_fase_exata.txt` §3)

Consistência: com só $(2,\pm2)$ no fluxo, $\max|P_{\rm mem}/P-1|=1{,}2\times10^{-14}$ e
$\max|H_{\rm mem}/H-1|=2{,}9\times10^{-15}$ em todos os sistemas.

Erro de $\Omega$ (mediana/máximo) com **todos** os modos (b):

| Sistema | Inspiral adiab. | Inspiral EDO | Fim da insp. adiab. | Fim da insp. EDO | Pós-pico EDO | Fase no pico, EDO (rad) | Sobreposição até $t_p+30$ |
|---|---|---|---|---|---|---|---|
| A (10 Hz) | 1,5e-2/3,7e-2 | 1,5e-2/3,7e-2 | 4,5e-2/1,1e-1 | 4,5e-2/1,1e-1 | 1,8e-1 | −10,2 (de 512,8) | 0,165 |
| $q=1$ | 2,1e-2/3,5e-2 | igual | 4,1e-2/1,0e-1 | 4,2e-2 | 1,7e-1 | −4,5 (de 158,1) | 0,346 |
| $q=2$ | 2,1e-2/3,5e-2 | igual | 4,2e-2/8,4e-2 | igual | 1,2e-1 | −4,8 (de 172,7) | 0,293 |
| $q=4$ | 2,1e-2/3,6e-2 | igual | 4,2e-2/5,9e-2 | 4,2e-2 | 8,2e-2 | −5,8 (de 224,0) | 0,121 |
| $q=1$, $\chi=0{,}6$ | 3,3e-2/6,2e-2 | igual | 7,6e-2/1,6e-1 | 7,7e-2 | 2,2e-1 | −9,5 (de 198,4) | 0,164 |
| $q=3$, $\chi=(0{,}6;0)$ | 2,8e-2/5,2e-2 | igual | 6,3e-2/1,2e-1 | igual | 1,4e-1 | −9,2 (de 244,6) | 0,179 |

- Nas regiões do exp09, (b) dá 1,5–3,3% na inspiral e 4,3–8,0% na "fusão". O exp09 relatava 2,1–3,3% e 4–8%;
  o 1,5% de A vem da janela de 10 Hz.
- O ponto de retorno efetivo fica em $t_p=-2{,}25$ a $+3{,}6$ M.
- **A EDO e o adiabático coincidem antes do pico até a 3ª casa** (H08.7 refutada). Depois do pico a EDO é
  ligeiramente pior (0,18 contra 0,16 em A): a equação exata aplicada a dados que não são de um modo só.
- (c), RN: inspiral 5–9% e fim 2–7% (medianas). O ponto de retorno efetivo cai entre −4,3 e +47,8 M do pico (≥ 7,5 M
  depois dele em 6 dos 7 casos), e 3000 a 4100 passos ficam na fronteira (dados inconsistentes com um modo). Os erros de fase no pico vão de 2 a 17 rad.

### 4.5 Vários modos (`exp31_varios_modos.txt`)

**Pesos** ($g^E$: $L=2,4,6,8$; $g^J$: $L=3,5,7$):

| Par | $g^E_2$ | $g^E_4$ | $g^E_6$ | $g^E_8$ | $g^J_3$ | $g^J_5$ | $g^J_7$ |
|---|---|---|---|---|---|---|---|
| 22 | +0,073576 | +0,000708 | 0 | 0 | +0,029200 | 0 | 0 |
| 21 | −0,036788 | −0,002832 | 0 | 0 | −0,058399 | 0 | 0 |
| 33 | **0** | −0,009461 | −0,000174 | 0 | −0,022711 | −0,004891 | 0 |
| 32 | **0** | +0,022076 | +0,001041 | 0 | +0,022711 | +0,019564 | 0 |
| 44 | −0,037457 | −0,006862 | +0,001527 | +0,000038 | −0,061939 | −0,000903 | +0,000889 |
| 43 | −0,009364 | +0,010293 | −0,006490 | −0,000302 | +0,030969 | +0,002483 | −0,005335 |
| 55 | −0,059427 | −0,002287 | +0,002021 | −0,000265 | −0,097332 | +0,004966 | +0,000719 |
| 22×32 | +0,217641 | +0,016754 | 0 | 0 | +0,191941 | +0,004630 | 0 |
| 33×43 | +0,178412 | −0,023411 | −0,004208 | 0 | +0,178801 | −0,031019 | −0,001155 |

**Viés linear** $b_p$:

| Par | 21 | 33 | 32 | 44 | 43 | 55 | 22×32 | 33×43 |
|---|---|---|---|---|---|---|---|---|
| $b_p$ | +0,875 | +1,167 | −0,778 | +2,206 | −1,877 | +3,285 | **−3,615** | −3,729 |

**Decomposição.** Em A, $t=-1000$ M, o par 22×32 dá 2,2% de $E_2$ e 4,7% de $J_3$. Em $t=-10$ M dá 7,9% e 16%.
O modelo circular reproduz $E_2$ e $J_3$ a $\le2{,}7\times10^{-4}$ até $t=-200$ M, a $\le1{,}9\times10^{-3}$ em
$t=-50$, a $\le1\%$ em $t=-10$ e a até 8% em $t=+10$ (quatro sistemas).

**Viés medido contra o previsto** (inspiral, medianas):

| Sistema | Medido | Previsto, todos os pares | Previsto, só 22×32 |
|---|---|---|---|
| A | −1,47% | −1,52% | −1,57% |
| $q=4$ | −2,06% | −2,18% | −4,46% (cancelado por 33, 21, 44, 33×43) |
| $q=1$, $\chi=0{,}6$ | −3,33% | −3,54% | — |
| $q=2$ | −2,11% | −2,21% | — |

H08.8 confirmada.

**Separação por instante** (7 projeções; melhor caso de cada sistema; mediana inspiral; fim da inspiral):

| Sistema | Melhor conjunto | $\Omega$ insp. | $\Omega$ fim | Fase no pico | Sobreposição | Um modo (referência) |
|---|---|---|---|---|---|---|
| A | S2 (22, 22×32), esc | 1,2e-3 | 3,1e-3 | −0,81 rad | 0,975 | −10,15 rad; 0,167 |
| $q=1$, $\chi=0{,}6$ | S5, rel | 7,3e-4 | 4,4e-3 | −0,19 rad | 0,999 | −9,4 rad; 0,165 |
| $q=2$ | S4 (22, 22×32, 21, 33, 44), esc | 2,5e-3 | 4,7e-3 | +0,46 rad | 0,988 | −4,74 rad; 0,296 |
| $q=4$ | S4, esc | 1,9e-2 | 8,3e-2 | +7,4 rad | **0,246** | −5,75 rad; 0,121 |

- O melhor conjunto muda de sistema para sistema. Os conjuntos mais ricos podem ser muito piores: S5 em $q=4$ dá
  sobreposição 0,019.
- Pesos relativos ("rel") e escalados ("esc") trocam de vencedor.
- Só com $(E_2,E_4,J_3)$, o subsistema $3\times3$ para $(\Omega,X_{22},X_{22\times32})$ tem número de condição 15,4.

**Observador** ($\iota=50°$, $h_+$ e $h_\times$ separados, sem ruído):
- com $\iota$ conhecido, $\Omega_{\rm obs}$ erra 1,4% (A), 2,4% ($q=4$), 3,1% ($q=1$, $\chi=0{,}6$) e 2,1% ($q=2$)
  na inspiral;
- com $\iota$ errado, $K'/K-1$ vale +0,180, +0,095, −0,103 e −0,215 para −10°, −5°, +5° e +10°.

**$m\ne0$:**

| Sistema | $\arg E_{44}+4\phi_{\rm orb}$ | $\arg E_{31}+\phi_{\rm orb}$ | $\lvert E_{44}\rvert/\lvert E_{20}\rvert$ | $\lvert E_{31}\rvert/\lvert E_{20}\rvert$ |
|---|---|---|---|---|
| A (65 rad de fase orbital, $t_p-2000$ a $t_p$) | varia 0,13 rad | 0,14 rad | 0,038 | 0,012 |
| $q=4$ (69 rad) | 0,39 rad | 0,35 rad | 0,035 | 0,071 |

$|E_{21}|/|E_{20}|\le2\times10^{-16}$: nulo por reflexão.

### 4.6 Ruído (`exp32_fase_ruido.txt`)

**Fase verdadeira do (2,2) até o pico** em A:

| Desde | $\Delta\psi$ | Instante |
|---|---|---|
| 10 Hz | 512,8 rad (81,6 ciclos) | 5,26 s antes do pico |
| 20 Hz | 145,6 rad | — |
| 100 Hz | 7,2 rad | 8,8 ms antes |
| — | 4,6 rad | 5 ms antes |
| — | 2,1 rad | 2 ms antes |

**Desvio da fase prevista** (rad; bits sobre a fase módulo $2\pi$ entre parênteses):

| Cenário | 10 Hz | 20 Hz | 50 Hz | 100 Hz | 10 ms | 5 ms | 2 ms |
|---|---|---|---|---|---|---|---|
| só prior | 120 | 60 | 42 | 26 | 27 | 19 | 9,6 |
| ET, detector único, tudo livre | 80 | 25 | 4,7 | 1,4 (0,23) | 1,5 (0,15) | 0,92 (0,73) | 0,43 (1,8) |
| CE, detector único, tudo livre | 56 | 19 | 4,0 | 1,2 (0,41) | 1,3 (0,30) | 0,76 (1,0) | 0,34 (2,1) |
| CE, rede, $q$ e $\chi$ conhecidos | 29 | 8,1 | 1,3 (0,29) | 0,36 (2,1) | 0,40 (1,9) | 0,25 (2,6) | 0,12 (3,6) |
| CE, rede, só $\ln M$ e $t_0$ livres | 15 | 4,3 | 0,70 (1,1) | 0,21 (2,9) | 0,22 (2,8) | 0,14 (3,4) | 0,07 (4,4) |

- Em CE, a SNR da polarização × é $\rho_\times=3{,}21$, e em ET é 0,81 (D3). A taxa $H(t)$, que fixaria $\Omega$
  pela razão $P/H$, não é resolvida nem em CE.
- Mesmo no cenário mais otimista (CE, rede, só $\ln M$ e $t_0$ livres), a fase só passa de ~1 bit de informação
  nos últimos ~50 Hz–fusão, isto é, ~25 rad (~4 ciclos).

### 4.7 L09 (`exp32_ringdown.txt`)

Remanescente e QNMs, em 1/M da massa inicial (A: $M_f=0{,}94971$, $\chi_f=0{,}71404$):

| QNM | $\omega$ (A) |
|---|---|
| 220 | 0,5675 − 0,0845i |
| 221 | 0,5559 − 0,2553i |
| 320 | 0,8056 − 0,0881i |
| 200 | 0,4160 − 0,0886i |

Decaimento local $-d\ln R_2/dt$ contra $2\Gamma_{220}$:

| Taxa | Sistema | [5,30] | [10,35] | [20,45] | [30,55] | [40,65] |
|---|---|---|---|---|---|---|
| só (2,2) | A | −34,7% | −17,2% | −3,3% | **−0,5%** | +1,3% |
| só (2,2) | $q=1$ | — | — | — | −0,7% | — |
| só (2,2) | $q=4$ | — | — | — | +0,3% | — |
| todos os modos | A, $q=1$, $q=4$ | — | — | — | −1,9%, −1,8%, +2,3% | — |
| RN | todos | $d h_{20}/du$ troca de sinal (toque linear): não é um fluxo positivo | | | | |

- O decaimento **mais lento** logo após o pico (−35% em [5,30]) é o que se espera da fase de fusão e do primeiro
  sobretom interferindo, não de pares de QNM puros.
- **Batimento 220–221:** $\Delta\omega=0{,}0116$/M contra $\Gamma_0+\Gamma_1=0{,}340$/M (A), $Q_b=0{,}034$ (A),
  0,036 ($q=1$) e 0,050 ($q=4$). Superamortecido.
- **Matrix pencil, só (2,2)** ([10,60], ordem 3): polos não oscilantes com amortecimentos 0,175 ($2\Gamma_0=0{,}169$),
  0,273 (entre 0,169 e $\Gamma_0+\Gamma_1=0{,}340$) e 0,514 ($2\Gamma_1=0{,}511$).
- **Todos os modos:** polo oscilante ±0,2175/0,2227 (A) e ±0,2203/0,2262 ($q=1$). O par 220×320 previsto é
  0,238/0,173; o 221×320, 0,250/0,343. O resultado é compatível com uma mistura dos dois.
- Os polos mudam com a ordem e a janela: em $q=4$ eles não se estabilizam.
- **Resíduo $h_{20}$(RN) − $h_{20}$(nula):**
  - máximo $1{,}33\times10^{-2}$ em $t-t_p=4{,}8$ M (A), contra o degrau nulo de $7{,}35\times10^{-2}$ no trecho;
  - o *pencil* da derivada dá ±0,4206/0,0638 ([5,70]) e ±0,4150/0,0749 ([10,70]), contra $\omega_{200}$ =
    0,4160/0,0886;
  - $q=1$: 0,4170 e 0,4126 contra 0,4132;
  - $q=4$: 0,4161 e 0,4011 contra 0,3909;
  - amortecimento 10–30% menor que o previsto;
  - o segundo par (~0,25–0,30/~0,13–0,21) não foi identificado.

## 5. Tentativas de refutação e alternativas

1. **Identidade e reconstrução (H08.1, H08.6).** Atacadas por sete caminhos:
   - sympy simbólico;
   - dados exatos em 6 sistemas;
   - rede deslocada, com o ponto de retorno entre nós;
   - EDO contra iteração (métodos diferentes, mesma resposta a $10^{-9}$ antes do pico);
   - perturbação do valor inicial em $t_p$;
   - ruído suave e branco;
   - escala $(\lambda,\mu)$.

   Nada refutou.
2. **H08.2 refutada.** Verificações:
   - argumento (contração para trás);
   - RK45 desde o valor exato, que morre em 1 M;
   - família perturbada de $\pm10^{-9}$.

   **Alternativas de condição de unicidade** examinadas: (i) $a\to0$ no passado (falha); (ii) $a\to0$ no futuro
   (insuficiente sozinha: depois do pico as soluções também convergem para a verdadeira); (iii) $a\to0$ nos dois
   lados mais passagem por $v=0$ (funciona, seção 2.3); (iv) ponto de retorno $\arg\max u_b$ (funciona e é
   construtivo); (v) suporte conexo e unimodalidade (necessárias: contraexemplos da tangente e dos surtos); (vi) para
   amplitude multimodal (excêntricas), os mínimos não fixam nada e os máximos sim [D, não testado numericamente].
3. **H08.7 refutada.** Seis abordagens para explicar o erro de fusão do exp09:
   - (i) correção adiabática exata (EDO): não muda nada antes do pico;
   - (ii) iteração: idem;
   - (iii) rede deslocada: idem;
   - (iv) separação por regiões (o erro está antes do pico e cresce com $x$);
   - (v) decomposição em pares de modos: **explica** (viés previsto a 3–6%);
   - (vi) RN contra leis de balanço: o RN acrescenta erro próprio, sem melhorar.
4. **H08.9 (separação de modos), parcialmente refutada.** Abordagens:
   - (i) cinco conjuntos de pares;
   - (ii) dois esquemas de peso;
   - (iii) subsistema exato $3\times3$ (condição 15,4);
   - (iv) quatro sistemas, inclusive $q=4$, onde falha;
   - (v) observador único, onde as 7 projeções colapsam em 2 séries ($h_+$, $h_\times$) e a separação é impossível;
   - (vi) multipolos $m\ne0$, que contornam o problema para a fase orbital.

   Não encontrei critério interno (sem a verdade) que escolha o conjunto certo. O resíduo do ajuste diminui com o
   número de pares (S5 é exatamente determinado e às vezes é o pior).
5. **H08.10** foi enfraquecida para o enunciado da seção 2.3 (um modo, céu resolvido) e completada pela observação
   dos $m\ne0$. A equivalência "módulo a fase orbital" não vale para um observador ($K(\iota)$) nem com mais de um
   modo relevante (as fases constantes de cada $m$ ficam livres nos $m=0$).
6. **Ruído (H08.12).** Para tentar refutar, considerei cinco cenários, do só prior ao mais otimista (só $\ln M$ e $t_0$
   livres, rede, CE). A conclusão (≤ ~4 ciclos com mais de 1 bit, no melhor caso) não muda.
7. **L09.** Duas variáveis (só (2,2) e todos os modos), cinco janelas de inclinação, *pencil* com 3 ordens e 2
   janelas, resíduo RN − nula com 2 janelas.

## 6. Contraexemplos e limitações

- **Unicidade.** Exige amplitude unimodal com máximo não degenerado, $H>0$ e suporte conexo. A demonstração está no
  nível linearizado em $t_p$.
- **Amplitude multimodal (excêntricas, L16).** Os máximos fixam a solução e os mínimos não. Não foi testado.
- **O substituto.** O (2,2) deixa de ser um modo de frequência positiva depois de ~65 M ($H<0$ em $t\approx78$ M).
  Os números "até $t_p+60$" param ali.
- **Fluxos de memória de nível A.** São quadráticos, com os 7 pares de modos do substituto (sem (3,1), (4,2), (4,1)).
  Os pesos são da aproximação circular, que vale a $\le2{,}7\times10^{-4}$ até $t=-200$ M, a $\le1{,}9\times10^{-3}$
  em $-50$ M e a até 8% depois do pico.
- **A separação de modos depende de modelo.** Funciona onde há hierarquia limpa (massas quase iguais).
- **O $K(\iota)$ supõe o (2,2) dominante.** Com outros modos a contaminação muda com $\iota$.
- **Ruído.**
  - Fisher linearizado, herdado do D3. O D3 mostrou que, em $\ln M$, a verossimilhança é assimétrica por fator ~3,
    e que o Fisher falha nos eixos dominados pelo prior.
  - As derivadas da fase são do modelo (NRHybSur3dq8_CCE). A "fase prevista" vem do modelo de binária ajustado à
    memória, não de uma recuperação de fase.
  - Só o sistema A.
- **L09.**
  - O *matrix pencil* é instável com a ordem: os números servem como compatibilidade, não como medida.
  - Não ajustei o modelo de Elhashash & Nichols, que tem amplitudes ajustadas a NR.
  - Não tratei modos espelho nem QNMs quadráticos.
- **Erro de modelo.** Diferenças de ~1e-4 na energia entre substitutos (L00) não afetam as conclusões, que são de
  ordem 1e-2 ou mais.

## 7. Literatura e originalidade

**Como conferi.**
- API do arXiv, com dez consultas combinando: *memory*, *orbital frequency*, *orbital phase*, *phase retrieval*,
  *spin memory*, *angular momentum flux*, *ringdown*, *quasinormal*, *instantaneous frequency*.
- Cinco buscas na web:
  - fluxo de energia e momento angular → fase;
  - $dE/dJ$ e $\Omega$;
  - modos de memória → fase;
  - razão das taxas de deslocamento e de spin;
  - *phase retrieval* em ondas gravitacionais.
- Crossref ("gravitational wave memory orbital phase reconstruction").
- Leitura (WebFetch) do modelo de *ringdown* de arXiv:2504.18635v2.

**Estabelecido [E].**
- $\dot E=\Omega\dot J_z$ em órbitas circulares (primeira lei da mecânica de binárias; usada em EOB). Damour, Nagar,
  Pollney & Reisswig, PRL 108, 131101 (2012), mostram a relação $E(j)$ invariante.
- Memória de spin no modo $h_{30}$: Nichols, PRD 95, 084048 (2017), arXiv:1702.03300.
- Memória no *ringdown* como soma de pares de QNMs: Elhashash & Nichols, arXiv:2504.18635. A L09 foi conferida
  contra esse trabalho.
- Ponte entre QNMs quadráticos e memória: Shi et al., arXiv:2603.07469 (2026).
- Fenomenologia não linear da fusão no limite de razão de massa pequena: Bourg et al., arXiv:2609.06861 (2026).
- Modos $m=0$ de CCE com toque quase normal: Rosselló-Sastre, Husa & Bera, arXiv:2405.17302; Valencia et al.,
  arXiv:2406.16636.
- Detecção das memórias de deslocamento e de spin: Grant & Nichols, PRD 107, 064056 (2023).
- O problema radial $\dot r^2=v^2-L^2/r^2$ e as soluções singulares e envelopes de EDOs são clássicos (mecânica
  analítica; equações de Clairaut e de Briot–Bouquet).

**Não encontrado (o que não prova novidade).**
1. Reconstrução do modo oscilatório a partir de $P$ e $H$ resolvidos no tempo (ou dos modos de memória), com o
   ponto de retorno como condição de unicidade e a análise de estabilidade.
2. A tabela de pesos por par e o viés linear do estimador $\Omega_{\rm mem}$, dominado por $(2,2)\times(3,2)$.
3. O zero exato do peso $L=2$ para $\ell=3$.
4. A ambiguidade de escala $K(\iota)$ de um único observador.
5. A estimativa, via Fisher, de quanta fase a memória sozinha prevê.

Esses itens parecem lacunas abertas, mas 1 e 4 são consequências diretas de álgebra elementar. O valor deles está
na aplicação à memória, não na matemática. Não alego descoberta.

**L09.** Confere; nada de novo além das observações elementares do superamortecimento e do toque do (2,0,0) no
resíduo (já apontado qualitativamente na literatura de CCE).

## 8. Próximos experimentos

1. Escrever a demonstração não linear em $t_p$ (Briot–Bouquet) e estender a amplitude multimodal. Testar com as
   excêntricas (SEOBNRv5EHM, tratamento de janela do L16) para verificar a seleção pelos máximos.
2. Separação de modos com prior PN nas razões de amplitude $|h_{\ell m}|/|h_{22}|(x,\eta,\chi)$: transforma H08.9
   em estimação de parâmetros. Medir quanto se ganha sobre o estimador de um modo em $q=4$.
3. Recuperação de fase pelos multipolos $m\ne0$ com o céu resolvido: reconstruir $\phi_{\rm orb}(t)$ a partir de
   $\arg E_{44}$ e $\arg E_{31}$ (resolve a ambiguidade de $\pi/2$ quando $q\ne1$). Verificar se a parte $m\ne0$ da
   memória num observador (oscilatória, ~4% da taxa) é separável dos modos lineares em algum regime [S].
4. Problema de recuperação de fase no céu inteiro: o padrão $|\dot h(\theta,\phi)|^2$ num instante determina
   $\dot h$ a menos de fase global? [H; em 2D, a recuperação de fase é genericamente única].
5. Verossimilhança completa (não Fisher) da fase prevista, com o perfil assimétrico em $\ln M$ do D3.
6. L09: ajustar diretamente o modelo de pares com os QNMs fixados e amplitudes livres, incluindo modos espelho e
   QQNMs, para isolar o par (0,1) superamortecido.

## 9. Tabela de hipóteses

| Id | Enunciado | Status | Evidência |
|---|---|---|---|
| H08.1 | $\dot u^2=4(uP-H^2)$, $\dot\psi=H/u$, $P/H=\dot\psi/(1-\dot a^2/P)$ | confirmada matematicamente | sympy, resíduo 0; §2.1 |
| H08.2 | "$a\to0$ no passado" fixa a solução | refutada | contração para trás; RK45 desde o exato morre em 1 M; família $\pm10^{-9}$ (§4.2) |
| H08.3 | $t_p=\arg\max H^2/P$ e $\max H^2/P=\max\lvert h\rvert^2$ | confirmada matematicamente e numericamente | §2.2; $-0{,}0849$ M nos dois; razão $-3{,}1\times10^{-7}$ |
| H08.4 | Unicidade pelo ponto de retorno (amplitude unimodal, máximo não degenerado, suporte conexo) | confirmada matematicamente (nível linearizado) e numericamente | $\kappa=54{,}6$; erro de 10% em $u(t_p)$ cai a $4\times10^{-5}$ em 1 M; contraexemplos da tangente e dos surtos |
| H08.5 | Para frente: mal condicionado; desde $t_p$: bem condicionado | confirmada numericamente | amplificação $10^{1{,}59\times10^5}$; condicionamento 1,00 (§4.2) |
| H08.6 | $P$ e $H$ do (2,2) → reconstrução exata até a fusão | confirmada numericamente | EDO $\le1{,}5\times10^{-9}$ (inspiral), $\le2{,}6\times10^{-5}$ até $t_p+60$, sobreposição 1,00000 |
| H08.7 | A correção adiabática explica parte do erro de fusão do exp09 | refutada | $\le0{,}19\%$ antes do pico; EDO = adiabático a 3 casas com os fluxos de memória |
| H08.8 | O erro de $\Omega_{\rm mem}$ vem dos pares de modos, sobretudo $(2,2)\times(3,2)$ | confirmada numericamente | viés previsto −1,52% contra −1,47% medido (A); $b_{22\times32}=-3{,}6$ |
| H08.8b | O peso $L=2$ do fluxo de energia é zero para $\ell=3$ | confirmada matematicamente | 3j $\propto3s^2-\ell(\ell+1)=0$; pesos numéricos 0 |
| H08.9 | As projeções $L=2..8$ ($m=0$) separam os modos | inconclusiva (funciona com hierarquia limpa, falha em $q=4$, depende de modelo) | sobreposição 0,975–0,999 (massas quase iguais) contra 0,25 ($q=4$) |
| H08.10 | Sem ruído, os multipolos de memória resolvidos no tempo equivalem à onda módulo a fase orbital | confirmada matematicamente para um modo com céu resolvido; refutada para um observador e para vários modos com só $m=0$ | §2.3, §2.6; multipolos $m\ne0$ seguem $\phi_{\rm orb}$ a 0,13–0,39 rad |
| H08.11 | Para um observador, $\Omega$ fica a menos de $K(\iota)$ | confirmada numericamente (e pela álgebra da EDO) | $\dot\psi'/\dot\psi=\lambda/\mu$ a $10^{-5}$; ±10° → +18% / −21,5% |
| H08.12 | Com ruído realista, a memória quase não recupera fase | confirmada numericamente (Fisher linearizado) | CE: 56 rad desde 10 Hz; > 1 bit só nos últimos ~5 ms |
| H09.1 | A taxa da memória decai como $e^{-2t/\tau_{220}}$ | confirmada numericamente (no fim) | −0,5%, −0,7%, +0,3% em [30,55] M; −35% em [5,30] |
| H09.2 | Batimentos visíveis em $\omega_{220}-\omega_{221}$ | refutada | $Q_b=0{,}034$–$0{,}050$ (superamortecido); a oscilação visível é $(2,2)\times(3,2)$ |
| H09.3 | O resíduo RN − nula do (2,0) é o toque do QNM (2,0,0) | confirmada numericamente na frequência (≤ 1% em A e $q=1$; 2,6–6% em $q=4$); inconclusiva no amortecimento | *pencil* §4.7 |
