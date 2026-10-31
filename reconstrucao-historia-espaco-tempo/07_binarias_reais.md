# Etapa 6 — A degenerescência sobrevive em binárias reais de buracos negros?

**Pergunta.** As etapas 3 a 5 mostraram que histórias diferentes podem deixar as mesmas quatro
memórias (deslocamento, spin, centro de massa e giroscópica) com formas de onda diferentes. Mas as
fontes eram artificiais, com dinâmica prescrita. Aqui a fonte é uma binária de buracos negros da
relatividade geral (RG): massas, spins, excentricidade, inclinação, distância e recuo do remanescente
deixam de ser livres e ficam amarrados pelas equações de Einstein. A degenerescência sobrevive? É só
uma propriedade matemática de fontes artificiais ou uma limitação real da reconstrução de fusões?

**Resposta curta.**

1. **A família infinita das etapas 3–5 não sobrevive** (analítico, §2.1). Aquela família vinha de
   filtros de fase (passa-tudo) aplicados à onda. Numa binária da RG a amplitude e a fase são
   amarradas, $|\tilde h(f)|^2=a(f)^2\Psi''(f)/2\pi$. Por isso, filtrar a fase de uma binária não dá
   outra binária.
2. **Para um observador real (uma direção), sobra uma degenerescência de dimensão finita, e ela é
   exata** (analítico §2.2 + numérico §3.3). Um observador mede 4 números, e a binária tem pelo
   menos 6 parâmetros. Construí binárias com massa, razão de massas, spins, distância, inclinação e
   recuo diferentes cujas quatro memórias coincidem em $10^{-10}$ (substituto de relatividade
   numérica, RN). Também construí pares circular × excêntrica ($e_0=0{,}2$ e $0{,}3$ em 10 Hz) que
   coincidem em $\sim10^{-5}$ (modelo SEOBNRv5EHM, com inspiral, fusão e *ringdown*).
3. **A degenerescência resiste às três camadas de correção** (§3.4):
   - nível A (ordem quadrática, a das etapas 3–5);
   - nível B (ordem seguinte, nos dois sentidos: pós-newtoniano e não linear);
   - nível C (memória completa de RN).

   O par concreto do nível A se desloca só $6\times10^{-6}$–$7\times10^{-5}$ no nível B não linear e
   0,4%–1,7% no nível C. Resolvendo de novo no nível C, a coincidência volta a $10^{-12}$–$10^{-7}$.
   A família é exata onde foi resolvida de novo (A e C); o par de um nível é aproximado no outro. Já
   a simetria pós-newtoniana que existia na ordem dominante é destruída na ordem seguinte.
4. **As formas de onda completas desses pares são diferentes.** O *match* em aLIGO fica entre 0,50
   e 0,985, e os pares são distinguíveis a partir de SNR de 1 a 6. O sistema de referência tem
   SNR 66.
5. **No céu inteiro (todos os multipolos), as memórias de binárias genéricas são quase injetivas**
   (numérico, §3.2). Não há par exato, e o mais próximo difere em 0,5%, menos que o erro do próprio
   modelo. Há uma exceção estrutural: com massas iguais, as memórias só veem a assimetria dos spins
   em segunda ordem (simetria de troca, analítico §2.5).
6. **Um observável com fase existe** (§2.6, §3.6). As memórias perdem a fase porque são integrais no
   tempo; as taxas não perdem. Para binárias quase circulares,
   $\Omega_{\rm mem}(u)=\dot h_{20}/(C\,|h_{30}|)$ recupera a frequência orbital usando só os modos de
   memória:
   - exato para o modo (2,2) puro;
   - 2–3% de erro com as leis de balanço;
   - até 13% com os modos $m=0$ do substituto.

   A forma mais simples e robusta do mesmo princípio é medir as memórias em duas janelas. Pares
   idênticos com a janela começando em 10 Hz diferem de $2\times10^{-3}$ a $5\times10^{-2}$ com
   início em 5 ou 20 Hz.
7. **Conclusão** (§6). A família infinita é propriedade do mapa "radiação → memória" para fontes
   arbitrárias, não das binárias da RG. A família finita de um observador é uma limitação real das
   quatro memórias integradas. Ela importa na prática quando só a memória é observada (memória
   "órfã" de fontes fora da banda [McNeill2017]). Quando a onda oscilatória é observada, ela resolve
   a ambiguidade com folga. A precisão necessária para separar os pares só pela memória exige SNR
   de memória de 20 a 300. O sistema de referência dá 0,8 (aLIGO), 1,4 (A+), 11 (ET) e 39 (CE).

Rótulos: **[E]** estabelecido (com referência), **[D]** derivado ou verificado aqui, **[H]** hipótese,
**[S]** especulação. Além disso, cada resultado diz se é **analítico** (vale para qualquer sistema da
classe, com as hipóteses enunciadas) ou **numérico** (calculado com um modelo de onda específico; vale
para os casos calculados e carrega o erro do modelo).

---

## 1. Modelos, definições e tolerância

### 1.1 Parâmetros e convenções

Unidades $G=c=1$. Parâmetros intrínsecos $\lambda=(M,q,\chi_1,\chi_2,e_0,\ell_0)$:
- $M$ é a massa total no referencial do detector, $q=m_1/m_2\ge1$ e $\eta=q/(1+q)^2$;
- $\chi_{1,2}$ são spins alinhados ao momento angular orbital;
- $e_0$ e $\ell_0$ são a excentricidade e a anomalia numa frequência de referência.

Os parâmetros extrínsecos são a distância $D$, a inclinação $\iota$, a fase e a posição no céu. O
remanescente ($M_f$, $\chi_f$ e recuo $v$) é função de $\lambda$ pela RG. A deformação é

$$h\equiv r(h_+-ih_\times)=M\sum_{\ell m}H_{\ell m}(u/M;\lambda)\,{}_{-2}Y_{\ell m},\qquad
h_+-ih_\times\big|_{\rm obs}=\frac MD\sum_{\ell m}H_{\ell m}\,{}_{-2}Y_{\ell m}(\iota,\phi_0),$$

com $H_{\ell,-m}=(-1)^\ell\bar H_{\ell m}$ para spins alinhados (simetria de reflexão no plano orbital).
As memórias são as da `03_problema_concreto.md` §1 (leis de balanço BMS de [Mitman2020], [Nichols2018],
[SO2022]), com $\mathfrak D=\tfrac18D^2(D^2+2)$:

$$\Delta J^E=\tfrac12\bar\eth^2\mathfrak D^{-1}\Big[\Delta m+\tfrac14\!\int\!|\dot h|^2du\Big],\qquad
\mathfrak DD^2\!\!\int\!\Psi\,du=\Delta{\rm Im}[\eth\bar q^A\hat N_A]+\tfrac18{\rm Im}\,\eth\!\!\int\!W du,$$
$$\mathfrak DD^2\Delta\mathcal K=\Delta{\rm Re}[\eth\bar q^A\hat N_A]+\tfrac18{\rm Re}\,\eth\!\!\int\!W du,\qquad
r^2\Phi=-\mathfrak D\!\!\int\!\Psi\,du+\tfrac14\!\int\!{\rm Im}(\bar h\dot h)\,du,$$

$W=3\dot h\,\bar\eth\bar h-3h\,\bar\eth\dot{\bar h}-\dot{\bar h}\,\bar\eth h+\bar h\,\bar\eth\dot h$. A fórmula
giroscópica foi conferida contra o resultado pós-newtoniano de [FS2025] (exp01, teste T10: erro $4\times10^{-5}$).

### 1.2 O que se compara: multipolos $m=0$, globais e num observador

Para spins alinhados, depois da integração no tempo só sobrevivem os multipolos $m=0$ das memórias.
Os de $m\neq0$ vêm de produtos de modos com $m$ diferentes, que oscilam como $e^{-i(m-m')\psi}$; a
integral deles é só um termo de borda da janela **[D]**. O vetor global (céu inteiro, referencial da fonte) é

$$\mu(\lambda)=\big(J^E_{20},\,J^E_{40},\,S_{30},\,\mathcal K_{20},\,\mathcal K_{40},\,\Phi_{10},\,\Phi_{30}\big),$$

e no observador as quatro memórias valem, com escala exata por análise dimensional **[D, analítico]**:

$$\Delta h_+=\frac MD\,d(\iota),\qquad \int\! h_\times du=\frac{M^2}{D}\,s(\iota),\qquad
\int\! h_+du\Big|_{\rm CM}=\frac{M^2}{D}\,c(\iota),\qquad \Phi=\Big(\frac MD\Big)^2 g(\iota),$$

onde $d=\sum_\ell{\rm Re}\,J^E_{\ell0}\,{}_{-2}Y_{\ell0}(\iota)$ e analogamente para $s$, $c$ e $g$ (este com
${}_0Y_{\ell0}$). Os coeficientes dependem de $\lambda$ e da janela.

### 1.3 Janela

As memórias de spin e giroscópica acumulam o momento angular irradiado. Ele cresce sem limite para
trás no tempo: $\Delta J\propto\eta M^2(x_i^{-1/2}-x_f^{-1/2})$, com $x=(\pi Mf)^{2/3}$ (newtoniano)
**[D]**. Por isso essas memórias só têm sentido numa janela, e adoto a que um detector impõe: o
acúmulo começa na frequência de onda $f_i$ (10 Hz no observador; $Mf_i=0{,}004$ no estudo global). A
memória de deslocamento converge ($\propto x_i\to0$). Nos exp06, exp07 e exp11 uso o deslocamento
total, com a parte anterior à janela dada pela fórmula 3PN de [Favata2009b] para $(2,0)$ e pela de
1PN de [Blanchet2024] para $(4,0)$. Nos exp10, exp12 e exp15 uso o deslocamento de janela, que é o que
um detector com corte em baixa frequência mede. Como A e B são sempre tratados da mesma forma, a
escolha não altera a lógica.

### 1.4 Os três níveis de robustez

O pedido foi: (A) a ordem em que a degenerescência foi achada, (B) a ordem seguinte e (C) a RN. Cada
nível é implementado assim:

- **Nível A (ordem quadrática, a das etapas 3–5).** As partes nulas vêm das leis de balanço com os
  modos oscilatórios ($m\neq0$) de uma binária real:

  $$J^E=\tfrac18\bar\eth^2\mathfrak D^{-1}\!\!\int_{u_i}^{u_f}\!|\dot h_{\rm osc}|^2du+J^E_{\rm antes},\qquad
  \mathcal K=\mathcal K_{\rm nula}[h_{\rm osc}]-\tfrac32M_f\,\mathfrak D^{-1}\Delta\Phi_E,$$

  com a memória de CM ordinária de [Nichols2018] (eq. KlmChargePhilm). Aqui $\Delta\Phi_E$ é o
  potencial elétrico do deslocamento, $\Delta J^E=\tfrac12\bar\eth^2\Delta\Phi_E$, e
  $M_f=1-E_{\rm janela}-E_{\rm lig}(x_i)$.
- **Nível B, em dois sentidos.**
  - (B-PN) A dinâmica da fonte na ordem pós-newtoniana seguinte: ordem dominante × 1PN nos modos e na
    evolução orbital, com os modos de [Blanchet2024] (exp08).
  - (B-NL) A memória na ordem não linear seguinte: os próprios modos de memória ($m=0$) entram nos
    fluxos, o que dá os termos cúbicos.
- **Nível C (RN completa).** As memórias são lidas direto dos modos $m=0$ do substituto NRHybSur3dq8_CCE
  [Yoo2023], extraídos por CCE, que contêm a memória completa da RG:

  $$J^E_{\ell0}=H_{\ell0}(u_f),\qquad S_{30}=\!\int\!H_{30}\,du,\qquad
  \Phi_{30}=-\mathfrak D_3\Psi_{30}+\tfrac14[\text{helicidade de todos os modos}]_{30},$$

  e a de CM é a ordinária com o deslocamento de RN mais a parte nula com todos os modos.

Modelos usados:

| Modelo | O que é | Onde |
|---|---|---|
| NRHybSur3dq8_CCE [Yoo2023] | substituto de RN com memória por CCE; spins alinhados, $q\le8$, $\lvert\chi\rvert\le0{,}8$ | exp06, exp07, exp09, exp11, exp13–15 |
| NRSur3dq8Remnant [VGSHZ2019] | ajuste de RN para massa, spin e recuo do remanescente | conferência (exp06) |
| SEOBNRv5EHM [GBE2025] (pyseobnr 0.3.7) | EOB excêntrico, spins alinhados, calibrado a RN, sem modos $m=0$ | exp12 |
| TEOBResumS 4.4.1 [Nagar2018] | EOB quase circular (a versão do PyPI ignora a excentricidade) | conferência (exp10) |
| PN newtoniano + Peters [Peters1964] | inspiral excêntrica de 10 Hz até a separatriz $p=6+2e$ | exp10, exp10b |
| PN dominante e 1PN [Blanchet2024] | modos até 1,5PN no (2,2) e evolução até 2PN | exp08 |

O modelo excêntrico TEOBResumS-Dalí não pôde ser compilado: o sistema de permissões bloqueou a
compilação de código externo a partir de um clone git. Usei o SEOBNRv5EHM, instalado do PyPI. A
dependência `pygsl_lite` precisou ser compilada com `setuptools` 75, porque as versões novas quebram
o `spawn` do seu `setup.py`.

### 1.5 Tolerância

Para duas binárias A e B, a diferença é a maior diferença relativa entre as memórias:

$$\delta(A,B)=\max_k\frac{|m_k^B-m_k^A|}{|m_k^A|},\qquad k\in\{\text{desl.},\ \text{spin},\ \text{CM},\ \text{giro}\}\ \text{(observador) ou os 7 multipolos de }\mu\ \text{(global)}.$$

Três escalas de comparação, todas medidas aqui:

| Escala | Valor | O que é |
|---|---|---|
| $\varepsilon_{\rm num}$ | $10^{-10}$ (nível A), $\sim10^{-7}$ (nível C), $\sim10^{-5}$ (SEOBNRv5EHM) | piso numérico: variação das memórias sob passos minúsculos dos parâmetros e repetição do cálculo |
| $\varepsilon_{\rm mod}$ | $10^{-2}$ | erro do modelo: diferença entre os níveis A e C nos multipolos dominantes (0,3% a 9%, §3.1) |
| $\varepsilon_{\rm obs}$ | $1/\rho_{\rm mem}$ | precisão de medida de uma memória com SNR de memória $\rho_{\rm mem}$ (§3.3) |

**Classificação.** Na versão corrigida do modelo, resolvo de novo as equações procurando a
binária B:
- **exata:** $\delta\le\varepsilon_{\rm num}$;
- **aproximada:** $\varepsilon_{\rm num}<\delta\le\varepsilon_{\rm mod}$;
- **destruída:** $\delta>\varepsilon_{\rm mod}$.

### 1.6 Quando duas ondas são distinguíveis

Produto interno $(a|b)=4\,{\rm Re}\int_{f_{\min}}^\infty\tilde a\bar{\tilde b}/S_n\,df$. O *match* é o
produto normalizado maximizado sobre o instante e a fase de chegada. Pelo critério de [LOB2008], as ondas
são distinguíveis quando $(\delta h|\delta h)>1$. Para normas iguais, isso equivale a

$$\rho>\rho_{\rm crit}=\frac1{\sqrt{2(1-\text{match})}} .$$

Uso um detector orientado de forma ótima para $h_+$, com $f_{\min}=10$ Hz e as curvas do
lalsimulation: aLIGO de projeto (LIGO-T1800044), A+ (LIGO-T1800042), ET-D e CE ([ET-CE2017]).

---

## 2. Resultados analíticos

### 2.1 Por que a família infinita não sobrevive [D, analítico]

O Teorema 1 (`03_problema_concreto.md` §2) diz que as memórias só veem $B=\int\dot h\dot h^\dagger$ e
$A-A^\dagger$. Logo, qualquer filtro de fase comum $\tilde h_j\to e^{i\varphi(\omega)}\tilde h_j$ as
preserva. Duas observações mostram que isso não gera binárias degeneradas:

(i) **A memória observada depende da distância além da forma da onda.** As leis de balanço valem para
$rh$. Com $rh=D\,h_{\rm obs}$:

$$\Delta h_{\rm obs}\propto D\!\int\!|\dot h_{\rm obs}|^2du .$$

Dois sinais com o mesmo espectro observado só têm as mesmas memórias se estiverem à mesma distância.

(ii) **Na RG, fase e amplitude são amarradas.** Na fase estacionária do modo dominante,
$h_{22}=a(t)e^{-i\phi(t)}$ com $\dot\phi=2\pi f$:

$$\tilde h_{22}(f)\simeq a(t_f)\sqrt{2\pi/\ddot\phi(t_f)}\;e^{i\Psi(f)},\qquad \Psi''(f)=\frac{4\pi^2}{\ddot\phi(t_f)}
\quad\Longrightarrow\quad |\tilde h_{22}(f)|^2=\frac{a(t_f)^2\,\Psi''(f)}{2\pi}.$$

Para uma órbita quase circular, $a(t_f)=a_\lambda(f)$ e $\Psi''_\lambda(f)$ são fixados por $\lambda$ (órbita e
balanço de energia). Um filtro muda $\Psi$ sem mudar $|\tilde h|$. Para que o resultado seja outra
binária $\lambda'$ à mesma distância, é preciso que $a_{\lambda'}^2\Psi''_{\lambda'}=a_\lambda^2\Psi''_\lambda$
para todo $f$ na banda. Na ordem dominante, $a^2\Psi''\propto\mathcal M^{5/3}f^{-7/3}$, o que impõe a mesma
massa de *chirp* $\mathcal M$. Mas então $\Psi_{\lambda'}=\Psi_\lambda$ nessa ordem, e o filtro é trivial
(só desloca o tempo e a fase). Nas ordens seguintes, $a$ e $\Psi$ dependem de $\eta$ e dos spins de
formas diferentes; a fusão e o *ringdown* dependem de $(M,\eta,\chi)$. Igualar $|\tilde h|$ na banda
inteira força, genericamente, $\lambda'=\lambda$.

**Conclusão:** a família infinita de histórias da etapa 3 não contém pares de binárias da RG.
Ressalva: o argumento usa fase estacionária e vale para a inspiral; a fusão é tratada numericamente
(§3.2).

### 2.2 Contagem: a família de um observador [D, analítico]

Seja $F:\mathcal P\to\mathbb R^4$ o mapa dos parâmetros nas quatro memórias de um observador. A
dimensão de $\mathcal P$ é $n\ge6$:
- 6 para spins alinhados em órbita circular, $(M,q,\chi_1,\chi_2,D,\iota)$;
- 8 com $(e_0,\ell_0)$;
- 12 com spins precessantes.

Se $F$ é $C^1$ e ${\rm posto}\,dF=4$ em A, o teorema da função implícita diz que $F^{-1}(F(A))$ é,
perto de A, uma variedade de dimensão $n-4\ge2$. Concretamente, as leis de escala da §1.2 eliminam $D$:

$$D_B=D_A\,\frac{M_B\,d_B(\iota_B)}{M_A\,d_A(\iota_A)},$$

e sobram três equações, que só envolvem razões: $M\,s/d$, $M\,c/d$ e $g/d^2$. Elas determinam três
das incógnitas $(M_B,\iota_B,q_B,\chi_{1B},\chi_{2B})$. Por isso fixo $q_B$ e $\chi_{2B}$ e resolvo para
$(\iota_B,\chi_{1B},M_B)$.

### 2.3 A simetria pós-newtoniana da ordem dominante e sua quebra [D, analítico]

Na ordem dominante, para órbita circular [Blanchet2024]:

$$H_{22}=8\sqrt{\pi/5}\,\eta x\,e^{-2i\psi},\qquad \dot x=\tfrac{64}{5}\eta x^5 .$$

Cada memória é a integral de uma forma bilinear em $H_{22}$ e $\dot H_{22}$:
$\int F\,du=\int F\,dx/\dot x$, com $F\propto\eta^2f(x)$ e $du\propto dx/(\eta x^5)$. Então toda memória é
$\eta\times I(x_i,x_f)$, e $x_i=(\pi Mf_i)^{2/3}$ e $x_f=1/6$ só dependem de $M$. No observador:

$$\Delta h_+\propto\frac{\eta M}{D},\qquad \int h_\times du,\ \int h_+du\propto\frac{\eta M^2}{D},\qquad \Phi\propto\frac{\eta M^2}{D^2}.$$

**Simetria:** com $M$ e $\iota$ fixos, $(\eta,D)\to(\lambda\eta,\lambda D)$ preserva deslocamento,
spin e CM, e multiplica a giroscópica por $1/\lambda$. Na ordem dominante, a razão de massas é
exatamente degenerada com essas três memórias; só a giroscópica a separa.

Na ordem 1PN, os coeficientes dependem de $\eta$ fora do prefator:
- $H_{22}\to H_{22}[1+x(-\tfrac{107}{42}+\tfrac{55}{42}\eta)]$;
- $\dot x\to\dot x[1+x(-\tfrac{743}{336}-\tfrac{11}{4}\eta)]$.

A simetria quebra em $O(x\,\Delta\eta)\sim1\%$. Números no exp08 (§3.4).

### 2.4 O recuo não é medido pelas quatro memórias [D, analítico]

Com spins alinhados, o recuo $\vec v$ fica no plano orbital. Uma rotação de $\pi$ em torno do eixo
orbital leva $\vec v\to-\vec v$ e não muda os multipolos $m=0$. Então estes só dependem de $\vec v$ em
ordem par: $O(v^2)\sim10^{-7}$, como a parte $\ell=2$ do aspecto de massa de um buraco negro em
movimento. A parte linear em $v$ fica nos multipolos $m=\pm1$. Logo, as quatro memórias $m=0$ de um
observador não fixam o recuo. Os pares exatos da §3.3 têm recuos de 18 a 227 km/s, contra 77 km/s de A.

### 2.5 Massas iguais: as memórias só veem a assimetria dos spins em 2ª ordem [D, analítico]

Para $q=1$, trocar os rótulos dos buracos ($\chi_1\leftrightarrow\chi_2$) dá o mesmo sistema girado
de $\pi$ em torno do eixo orbital: $H_{\ell m}\to(-1)^mH_{\ell m}$ **[E]**. Com
$\chi_s=(\chi_1+\chi_2)/2$ e $\chi_a=(\chi_1-\chi_2)/2$:
- todo multipolo $m=0$ (todas as memórias, no céu inteiro) é função **par** de $\chi_a$;
- os modos com $m$ ímpar são funções **ímpares** de $\chi_a$; por exemplo, $H_{21}\propto\chi_a$.

Perto de $\chi_a=0$, as memórias diferem por $O(\chi_a^2)$, enquanto a onda difere por $O(\chi_a)$ em
amplitude, nos modos ímpares. É uma direção cega de segunda ordem das memórias globais: a única
degenerescência estrutural do céu inteiro que achei.

### 2.6 Observável que preserva a fase [D, analítico]

**Proposição.** Seja $h=\sum_jh_jY_j$ com modos $C^1$ que vão a zero no passado. As bilineares
**resolvidas no tempo** $P(u)=\dot h\dot h^\dagger$ e $Q(u)=h\dot h^\dagger$ determinam $h(u)$ a menos de
uma fase global constante.

*Demonstração.* Escreva $h_j=|h_j|e^{-i\psi_j}$.
1. ${\rm Re}\,Q_{jj}=\tfrac12\tfrac{d}{du}|h_j|^2$ dá $|h_j|$.
2. ${\rm Im}\,Q_{jj}=|h_j|^2\dot\psi_j$ dá $\psi_j$ a menos de uma constante (onde $h_j\neq0$).
3. Os termos fora da diagonal, $Q_{jk}=h_j\dot{\bar h}_k$, fixam as diferenças $\psi_j-\psi_k$.

Sobra só uma fase comum $e^{i\alpha}$, que não altera $P$ nem $Q$. ∎

As memórias são $\int P\,du$ e $\int(Q-Q^\dagger)du$ (Teorema 1). **A informação de fase se perde na
integração no tempo, não na estrutura quadrática.** Os modos de memória da própria deformação, como
funções de $u$, guardam projeções angulares de $P$ e $Q$ em cada instante:
- $\dot h_{20}$ é a projeção $\ell=2$ do fluxo de energia (a taxa da memória de deslocamento);
- $h_{30}$ é a projeção $\ell=3$ do fluxo de momento angular (o modo da memória de spin [Nichols2017]).

Para órbitas quase circulares, cada modo $h_{\ell m}\propto e^{-im\psi}$ satisfaz
$|\dot h_{\ell m}|^2=m^2\Omega^2|h_{\ell m}|^2$, o que dá a relação de órbita circular $\dot E=\Omega\,\dot J_z$
**[E]**. Com o (2,2) dominante:

$$\dot h_{20}=C_E\,|\dot h_{22}|^2,\qquad C_E=\frac1{\sqrt{24}}\Big\langle|{}_{-2}Y_{22}|^2+|{}_{-2}Y_{2,-2}|^2,\,Y_{20}\Big\rangle=0{,}073576,$$

$$\boxed{\ \Omega_{\rm mem}(u)=\frac{\dot h_{20}(u)}{C\,|h_{30}(u)|}\ },\qquad C=5{,}0397 .$$

Integrando, $\psi_{\rm mem}=\int\Omega_{\rm mem}du$. A amplitude sai de
$|h_{22}|=\sqrt{\dot h_{20}/C_E}\,/(2\Omega_{\rm mem})$. **Os dois modos de memória, resolvidos no tempo,
reconstroem o modo (2,2) a menos de uma fase constante**, uma recuperação de fase a partir de
intensidades (análoga ao FROG [BEE2020] e à STFT [AW2020]).

**Versão discreta: memórias em duas janelas.** As memórias acumuladas a partir de duas frequências
iniciais diferentes, $f_i$ e $f_i'$, dão 8 equações para 6 parâmetros. Genericamente, isso elimina a
família da §2.2. É a forma mais grosseira, e mais robusta, de "resolver a memória no tempo".

---

## 3. Resultados numéricos (simulações)

### 3.1 Conferência dos modelos

**Níveis A, B e C (exp06, parte 1).** Valem para 8 sistemas com $q$ de 1 a 8 e spins de −0,8 a 0,8,
na janela $Mf_i=0{,}004$. Maior $|A-C|/|C|$ por multipolo:

| desl. (2,0) | desl. (4,0) | spin (3,0) | CM (2,0) | CM (4,0) | giro (1,0) | giro (3,0) |
|---|---|---|---|---|---|---|
| 0,017 | 0,66 | 0,067 | 0,021 | 0,13 | 0,000 | 0,094 |

- Os multipolos dominantes concordam entre 0,3% e 9%. Os maiores desvios são em $q=8$ e nos
  multipolos $\ell=4$, que são pequenos.
- O nível B difere do A em $\lesssim10^{-3}$ nos multipolos dominantes (até $10^{-2}$ nos $\ell=4$, que
  são pequenos): os termos cúbicos são desprezíveis.
- A massa final calculada pelo fluxo bate com o ajuste NRSur3dq8Remnant [VGSHZ2019] em $\le3\times10^{-4}$.
- O recuo bate dentro de 1–2 desvios do ajuste (por exemplo, 153 contra 133 ± 11 km/s para $q=2$, e
  82 contra 83 ± 8 km/s para $q=8$).

**Outros modelos contra o substituto** (mesmos modos, nível A):

| Comparação | desl. (2,0), spin e giro | CM (2,0) |
|---|---|---|
| SEOBNRv5EHM com $e_0=0$ (exp12, parte 1) | 0,0–0,8% | 4–8% |
| TEOBResumS (exp10, parte 1) | 0,3–5% | — |

As convenções conferem: os sinais das memórias de spin e giroscópica coincidem. Os multipolos
$\ell=4$, pequenos, diferem bastante entre modelos.

**O nível C quebra uma simetria exata (exp13), e isso mede o erro do substituto.** Pela §2.5, as
memórias em $q=1$ são pares em $\chi_a$. No nível A, a diferença escala como $d^{2,0}$, como deve. No
nível C ela escala como $d^{1,0}$, com $1{,}4\times10^{-3}$ já em $d=0{,}025$. Os modos $m=0$ do
substituto violam a simetria em primeira ordem, no nível de $10^{-3}$–$10^{-2}$. Os números do
nível C valem, portanto, só até cerca de $10^{-3}$.

### 3.2 Céu inteiro: as memórias globais quase determinam a binária (exp06 parte 2, exp11, exp13)

Fiz a decomposição em valores singulares do jacobiano relativo $\partial\mu/\partial(\ln M,q,\chi_1,\chi_2)$
(7 multipolos × 4 parâmetros) e busquei, para cada $q_B$, a binária B mais próxima, minimizando
$\delta$ sobre $(M_B/M_A,\chi_{1B},\chi_{2B})$.

| Referência | Valores singulares | Melhor B | $\delta$ mínimo |
|---|---|---|---|
| A1 ($q=1{,}2$, χ = 0,3 / −0,2) | 4,79; 0,66; 0,43; 0,056 | $q_B=1{,}25$, χ = 0,372 / −0,274, $M\times0{,}9982$ | $4{,}6\times10^{-3}$ (nível C: $4{,}8\times10^{-3}$) |
| A2 ($q=3$, χ = 0,6 / 0) | 8,33; 4,67; 1,03; 0,41 | nenhum | $>1{,}1$ para todo $q_B\ne3$ |
| A3 ($q=1$, χ = −0,5 / −0,5) | 4,73; 0,56; 0,019; $1{,}2\times10^{-4}$ | ao longo de $\chi_1-\chi_2$ | ver abaixo |

**Leitura:**
- Para binárias genéricas não há par exato no céu inteiro. O mais próximo (A1) difere em 0,5%, abaixo
  de $\varepsilon_{\rm mod}$: com estes modelos não dá para decidir se é uma quase degenerescência
  real da RG. A classificação é **aproximada**, nos níveis A e C.
- O valor singular de $1{,}2\times10^{-4}$ de A3 tem direção $(0;\,-0{,}009;\,-0{,}707;\,+0{,}707)$, que
  é exatamente $\chi_a$. É a simetria da §2.5.

**O caso de massas iguais em números (exp13).** Comparo B = $(1,\ \chi_s+d,\ \chi_s-d)$ com A =
$(1,\ \chi_s,\ \chi_s)$, para $M=65$, $D=400$ Mpc e $\iota=50°$:

| $\chi_s$ | $d$ | memórias globais, nível A | 1 − match (aLIGO) | $\rho_{\rm crit}$ | $\lvert h_{21}\rvert/\lvert h_{22}\rvert$ no pico |
|---|---|---|---|---|---|
| −0,5 | 0,025 | $7{,}4\times10^{-5}$ | $3{,}8\times10^{-6}$ | 362 | 0,0040 |
| −0,5 | 0,05 | $3{,}0\times10^{-4}$ | $1{,}5\times10^{-5}$ | 181 | 0,0080 |
| −0,5 | 0,1 | $1{,}2\times10^{-3}$ | $6{,}2\times10^{-5}$ | 90 | 0,016 |
| −0,5 | 0,2 | $4{,}8\times10^{-3}$ | $2{,}5\times10^{-4}$ | 45 | 0,032 |
| +0,3 | 0,1 | $1{,}8\times10^{-3}$ | $5{,}5\times10^{-5}$ | 96 | 0,016 |
| +0,3 | 0,2 | $8{,}0\times10^{-3}$ | $1{,}2\times10^{-3}$ | 20 | 0,032 |

- Expoentes medidos: memórias $\propto d^{2,0}$, 1 − match $\propto d^{2,0}$ e $|h_{21}|/|h_{22}|\propto d^{1,0}$.
- A onda separa os dois sistemas a partir de $\rho\approx9/d$. As memórias só os separariam com SNR de
  memória $\sim8/d^2$ ($\approx800$ para $d=0{,}1$).
- Os dois observáveis enxergam mal a assimetria de spins em massas iguais; a memória, uma ordem pior.

### 3.3 Um observador: pares com as mesmas quatro memórias (exp07, exp15)

**Sistema A** (tipo GW150914): $M=65\,M_\odot$, $q=1{,}2$, $\chi=(+0{,}3,-0{,}2)$, $D=400$ Mpc,
$\iota=50°$. Memórias a partir de 10 Hz:

| Memória | Valor | |
|---|---|---|
| Deslocamento | $\Delta h_+=1{,}829\times10^{-22}$ | |
| Spin | $\int h_\times du=-2{,}498\times10^{-25}$ s | |
| CM | $\int h_+du=-3{,}069\times10^{-26}$ s | |
| Giroscópica | $\Phi=-3{,}157\times10^{-41}$ rad | |
| Remanescente | recuo 77 km/s, $M_f/M=0{,}950$ | |

Resolvi $(\iota_B,\chi_{1B},M_B)$ com $D_B$ eliminado (§2.2), no nível A, com 4 pontos de partida
por caso.

| $q_B$ | $\chi_{2B}$ | $M_B$ | $\chi_{1B}$ | $D_B$ (Mpc) | $\iota_B$ | $\delta$ | match aLIGO ($\rho_{\rm crit}$) | match ET ($\rho_{\rm crit}$) | recuo (km/s) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 64,99 | +0,079 | 398,6 | 50,4° | $4{,}1\times10^{-11}$ | 0,938 (2,9) | 0,717 (1,3) | 18 |
| 2 | 0 | 69,45 | +0,217 | 389,2 | 54,2° | $8{,}9\times10^{-11}$ | 0,980 (5,1) | 0,986 (5,9) | 104 |
| 3 | 0 | 73,69 | +0,549 | 387,0 | 55,0° | $3{,}0\times10^{-6}$ | 0,498 (1,0) | 0,330 (0,9) | 65 |
| 2 | +0,5 | 72,30 | −0,143 | 384,0 | 57,0° | $1{,}0\times10^{-10}$ | 0,670 (1,2) | 0,328 (0,9) | 227 |
| 4 | 0 | 75,40 | +0,800* | 384,3 | 53,1° | $1{,}5\times10^{-2}$ | 0,317 | 0,198 | 23 |
| 3 | −0,5 | 70,23 | +0,800* | 391,4 | 50,1° | $1{,}8\times10^{-2}$ | 0,411 | 0,252 | 55 |
| 6 | 0 | 83,57 | +0,800* | 336,5 | 60,6° | $7{,}8\times10^{-2}$ | 0,307 | 0,183 | 13 |

\* no limite de validade do substituto ($|\chi|\le0{,}8$).

- **Existem binárias diferentes com as mesmas quatro memórias**, coincidindo em $10^{-10}$ a
  $10^{-11}$. Elas diferem de A em todas as grandezas: $M$ (de 65 a 74), $q$ (de 1 a 3), spins,
  distância, inclinação e recuo (de 18 a 227 km/s).
- Para $q_B\ge4$ (com $\chi_{2B}=0$), não há solução dentro do domínio do modelo: $\chi_1$ teria de
  passar de 0,8. A família existe, mas tem fronteira.
- **As formas de onda são diferentes:** a SNR de A é 66 em aLIGO e 899 em ET, muito acima de
  $\rho_{\rm crit}$. O par mais parecido ($q_B=2$, match 0,98) se separa a partir de SNR 5.

Figura: `figuras/e7_pares_observador.png`. A, B ($q=2$) e B ($q=3$) terminam no mesmo degrau de
memória, mas oscilam de forma diferente.

**Quanto da SNR está na memória (exp15).** Comparei a parte $m=0$ de $h_+$ (os modos de memória) de A
com a onda oscilatória:

| Detector | aLIGO | A+ | ET | CE |
|---|---|---|---|---|
| SNR da memória | 0,76 | 1,44 | 10,7 | 39,1 |
| SNR da onda oscilatória | 66 | 126 | 899 | 3203 |

A razão é $1{,}2\times10^{-2}$ em todos. Isso é da mesma ordem das estimativas da literatura, segundo
as quais a memória de um evento isolado fica perto ou abaixo de SNR 1 no aLIGO e passa de 1 nos
detectores da próxima geração [Lasky2016; Hubner2020; GN2023]. A precisão relativa de cada memória é no máximo $1/\rho_{\rm mem}$, que fica entre 2,6% (CE)
e 130% (aLIGO).

### 3.4 Robustez nos níveis A, B e C (exp11, exp08)

**B-NL e C, para os pares do exp07 (exp11).** Para cada par: a diferença $\delta$ do par do nível A
recalculada em cada nível, e o resultado de resolver de novo no nível C partindo da solução do nível A.

| Par ($q_B$, $\chi_{2B}$) | $\delta$ A | $\delta$ B-NL | $\delta$ C | $\delta$ após resolver em C | Deslocamento da solução |
|---|---|---|---|---|---|
| (1, 0) | $4{,}1\times10^{-11}$ | $5{,}7\times10^{-6}$ | $4{,}4\times10^{-3}$ | $3{,}8\times10^{-12}$: **exata** | $M$ +0,04; $\chi_1$ +0,014; $D$ +0,5 Mpc; $\iota$ +0,03° |
| (2, 0) | $8{,}9\times10^{-11}$ | $1{,}7\times10^{-5}$ | $5{,}6\times10^{-3}$ | $1{,}1\times10^{-10}$: **exata** | $M$ −0,04; $\chi_1$ −0,021; $D$ −1,2; $\iota$ +0,5° |
| (3, 0) | $3{,}0\times10^{-6}$ | $4{,}3\times10^{-5}$ | $1{,}7\times10^{-2}$ | $6{,}4\times10^{-12}$: **exata** | $M$ +0,34; $\chi_1$ −0,061; $D$ −4,8; $\iota$ +1,5° |
| (2, +0,5) | $1{,}0\times10^{-10}$ | $7{,}2\times10^{-5}$ | $6{,}4\times10^{-3}$ | $2\times10^{-7}$: **exata**, no piso numérico do nível C | $M$ −0,11; $\chi_1$ −0,002; $D$ −0,4; $\iota$ +0,4° |
| (4, 0) | $1{,}5\times10^{-2}$ | $1{,}5\times10^{-2}$ | $1{,}9\times10^{-2}$ | $6{,}3\times10^{-3}$: aproximada | $\chi_1$ no limite 0,8 |
| (3, −0,5) | $1{,}8\times10^{-2}$ | $1{,}8\times10^{-2}$ | $1{,}7\times10^{-2}$ | $8{,}0\times10^{-3}$: aproximada | $\chi_1$ no limite 0,8 |
| (6, 0) | $7{,}8\times10^{-2}$ | $7{,}8\times10^{-2}$ | $6{,}4\times10^{-2}$ | $7{,}4\times10^{-2}$: destruída | $\chi_1$ no limite 0,8 |

O par (2, +0,5) foi resolvido de novo a partir do último ponto e voltou a $2{,}2\times10^{-7}$; esse é
o piso numérico do nível C nessa região.

**B-PN: ordem dominante × 1PN (exp08).** Par $q=1{,}2$ × $q=3$, com $\lambda=\eta_B/\eta_A=0{,}756$,
$D_B=\lambda D_A$ e mesmos $M=65$ e $\iota=50°$.

| Ordem | deslocamento | spin | CM | giroscópica |
|---|---|---|---|---|
| dominante | $-1{,}3\times10^{-4}$ | $+5{,}9\times10^{-5}$ | $-5{,}0\times10^{-3}$ | fator $1/\lambda=1{,}32$ |
| 1PN | $-1{,}4\times10^{-2}$ | $+1{,}2\times10^{-2}$ | $+5{,}5\times10^{-3}$ | fator 1,32 |

- O CM já difere $5\times10^{-3}$ na ordem dominante porque $M_f$ depende de $\eta$.
- Em 1PN, refazer o ajuste de $(M,D,\iota)$ com $q_B=3$ fixo não recupera a simetria: sobra
  $1{,}3\times10^{-2}$ nas três memórias, e $1{,}1\times10^{-1}$ com as quatro.
- A simetria é **destruída** na ordem seguinte. A família da §2.2 continua existindo porque os spins
  entram como incógnitas.

**Classificação (pedido 3):**

| Degenerescência | Nível A (ordem quadrática) | Nível B (ordem seguinte) | Nível C (RN) |
|---|---|---|---|
| Família infinita de filtros (etapas 3–5) | destruída pela dinâmica da RG (analítico, §2.1) | — | — |
| Simetria $(\eta,D)\to(\lambda\eta,\lambda D)$ de 3 memórias | exata na ordem PN dominante (giro quebra) | **destruída** em 1PN ($\sim1\%$, não restaurável) | — |
| Família de um observador, spins alinhados, circular, $q_B\le3$ | **exata** ($10^{-10}$) | B-NL: o par do nível A fica em $6\times10^{-6}$–$7\times10^{-5}$ (aproximado, 100 vezes menos que em C); a família não foi re-resolvida em B | **exata** como família ($10^{-12}$–$10^{-7}$); o par do nível A fica **aproximado** (0,4–1,7%) |
| Idem, $q_B\ge4$ com $\chi_{2B}=0$ | aproximada/destruída por falta de domínio ($\chi\le0{,}8$) | idem | idem |
| Circular × excêntrica com spins (SEOBNRv5EHM) | **exata** no piso do modelo ($7\times10^{-6}$–$5\times10^{-4}$), §3.5 | não testável (o modelo não tem modos $m=0$) | impossível aqui (não há RN excêntrica com memória) |
| Circular × excêntrica sem spins (PN, só inspiral) | aproximada para $e_0=0{,}1$ ($3\times10^{-3}$); **destruída** para $e_0\ge0{,}2$ (exigiria $\eta>1/4$), §3.5 | — | — |
| Céu inteiro, binárias genéricas | aproximada (0,5%) ou inexistente | não calculado | aproximada (0,48%) |
| Céu inteiro, $q=1$, direção $\chi_a$ | aproximada de 2ª ordem ($0{,}12\,d^2$) | — | o substituto viola a simetria (erro do modelo) |

### 3.5 Excentricidade (exp10, exp10b, exp12)

**Quanto a excentricidade muda as memórias com os outros parâmetros fixos.** Valores em relação ao
caso circular, para $M=65$, $q=1{,}2$, a partir de 10 Hz:

| $e_0$ em 10 Hz | 0,05 | 0,1 | 0,2 | 0,3 |
|---|---|---|---|---|
| Deslocamento, SEOBNRv5EHM com fusão (exp12) | +0,2% | −0,1% | −0,7% | −1,05% |
| Spin, SEOBNRv5EHM com fusão (exp12) | 0,0% | −0,6% | −3,1% | −6,3% |
| Deslocamento, PN só inspiral (exp10) | −0,5% | −1,0% | −0,6% | −3,7% |
| Spin, PN só inspiral (exp10) | −0,5% | −1,4% | −4,6% | −11% |

- A giroscópica acompanha o spin; o CM acompanha o deslocamento.
- Com fusão, o efeito é menor do que só na inspiral, porque a memória acumula mais na fusão, quando a
  órbita já circularizou [Favata2011].
- O SEOBNRv5EHM não tem a parte oscilatória do modo (2,0) das órbitas excêntricas. No modelo PN, ela
  muda o deslocamento em no máximo $3\times10^{-4}$ (com $e_0=0{,}4$) e o spin e a giroscópica em
  $10^{-15}$: a falta é desprezível.

**Pares circular × excêntrica com fusão (exp12, SEOBNRv5EHM, nível A).** A é o sistema da §3.3 com
$e_0=0$, calculado pelo mesmo modelo, com deslocamento de janela. B é excêntrico em 10 Hz.

| $e_0$ de B | $q_B$, $\chi_{2B}$ | $M_B$ | $\chi_{1B}$ | $D_B$ | $\iota_B$ | $\delta$ | match aLIGO ($\rho_{\rm crit}$) | match ET | recuo B |
|---|---|---|---|---|---|---|---|---|---|
| 0,1 | 1,2; −0,2 | 65,16 | +0,349 | 401,7 | 49,4° | $5{,}2\times10^{-4}$ | 0,985 (5,7) | 0,890 | 79 |
| 0,2 | 1,2; −0,2 | 65,91 | +0,556 | 413,0 | 46,2° | $2{,}6\times10^{-4}$ | 0,892 (2,2) | 0,700 | 114 |
| 0,2 | 2; 0 | 72,59 | +0,060 | 383,2 | 56,3° | $7{,}1\times10^{-6}$ | 0,682 (1,3) | 0,379 | 134 |
| 0,3 | 2; 0 | 73,23 | +0,183 | 387,7 | 54,0° | $7{,}8\times10^{-6}$ | 0,672 (1,2) | 0,369 | 109 |
| 0,2 | 1; 0 | 65,61 | +0,668 | 421,6 | 44,0° | $5{,}6\times10^{-5}$ | 0,635 (1,2) | 0,466 | 119 |
| 0,3 | 1,2; −0,2 | 67,39 | +0,671 | 416,6 | 44,4° | $1{,}2\times10^{-2}$ | 0,841 | 0,607 | 127 |

Recuo de A: 72 km/s.
- O piso numérico do SEOBNRv5EHM é $\sim10^{-5}$: variação de $10^{-5}$–$10^{-4}$ sob passos de
  $10^{-6}$ em $M$, e diferenças da mesma ordem entre execuções repetidas.
- **Binárias excêntricas podem ter exatamente as memórias de uma circular** (no piso numérico do
  modelo), para $e_0$ até 0,3. Com $q_B=1{,}2$ ou 1, a excentricidade é compensada sobretudo pelo spin
  ($\chi_1$ sobe de 0,3 para 0,35–0,67); com $q_B=2$, pela massa e pela razão de massas.
- No caso $e_0=0{,}3$ com $q_B=1{,}2$ não achei solução: o melhor de 3 + 8 partidas foi
  $1{,}2\times10^{-2}$ (refutação, exp12 parte 4: $1{,}8\times10^{-2}$ a $1{,}1\times10^{-1}$).

A excentricidade aparece de imediato na onda, como modulação da frequência: figura
`figuras/e12_excentrica.png`.

**Sem spins não há compensação (exp10 corrigido, exp10b).** No modelo PN (inspiral newtoniana, sem
spins) o otimizador leva $\eta$ ao limite físico $1/4$ ($q_B=1$) e para:

| $e_0$ | 0,1 | 0,2 | 0,3 |
|---|---|---|---|
| Resíduo (melhor de 3 + 12 partidas) | $3{,}0\times10^{-3}$ | $1{,}5\times10^{-2}$ | $3{,}9\times10^{-2}$ |
| Match aLIGO (no ponto do exp10) | 0,93 | 0,79 | 0,69 |

A excentricidade reduz a memória de spin em relação à de deslocamento. Sem spins, a única forma de
compensar seria aumentar $\eta$, e A ($\eta=0{,}248$) já está perto do máximo. Na busca com 12 partidas
aleatórias por valor de $e_0$ (exp10b), todas convergem ao mesmo mínimo, com $\eta=1/4$ no limite. Sem
spins, a degenerescência é aproximada para $e_0=0{,}1$ ($3\times10^{-3}$) e destruída para $e_0\ge0{,}2$.

### 3.6 O observável de fase na prática (exp09, exp14)

**Calibração.** Com um sinal (2,2) puro e o código conferido: $C_E=0{,}073576$ e $C=5{,}039682$,
igual ao valor analítico 5,0396, com dispersão de $1{,}6\times10^{-5}$ ao longo do sinal.

**Com RN (exp09, 5 sistemas, $q$ de 1 a 4, spins de 0 a 0,6):**

| Fonte das taxas | Erro mediano em $\Omega$, inspiral | Erro mediano em $\Omega$, fusão |
|---|---|---|
| Leis de balanço (modos oscilatórios) | 2,1–3,3% | 4–8% |
| Modos $m=0$ do substituto | 5–9% | 4–7% |

- O erro com as leis de balanço vem da calibração: $C$ vale para o (2,2) puro e os modos superiores
  mudam a distribuição angular dos fluxos.
- O erro extra com o substituto vem do modo $h_{20}$ de RN, que não é só a memória acumulada pelo
  fluxo. A diferença é de 0,8–1,8% no fim, mas chega a $\sim18\%$ do total 4–9 M depois do pico (parte
  ordinária, transiente do aspecto de massa).
- Na inspiral, a origem do excesso não foi isolada **[H: hibridização PN dos modos $m=0$ do substituto]**.
- A fase acumulada em 20–33 ciclos erra de 0,1 a 9,8 rad. A onda (2,2) reconstruída só com memória tem
  sobreposição de 0,34 a 0,94.
- Nas fontes artificiais da etapa 3, chirp × anti-chirp têm memórias integradas iguais, mas
  $\Omega_{\rm mem}$ cresce (0,067 → 0,148) numa e decresce (0,146 → 0,066) na outra.

**Nos pares degenerados (exp14).** Para os pares $(1,0)$ e $(2,0)$, as frequências verdadeiras de A e B
no mesmo tempo antes do pico diferem só 0,1–1,3%, porque os pares têm quase a mesma massa de *chirp*.
O estimador com os modos do substituto erra entre −13% e +9%, variando no tempo. **Com os modos do
substituto, $\Omega_{\rm mem}$ não separa os pares mais próximos.** Para o par (2, +0,5), as frequências
diferem 4–7% e o estimador acompanha a diferença só em parte.

**A versão discreta funciona com folga (exp14).** O mesmo par exato com a janela começando em outra
frequência:

| Par | Início da janela | Spin | Giroscópica | Deslocamento | CM |
|---|---|---|---|---|---|
| (1, 0) | 5 Hz | $-3{,}6\times10^{-3}$ | $-3{,}4\times10^{-3}$ | $\lesssim3\times10^{-4}$ | $\lesssim3\times10^{-4}$ |
| (1, 0) | 20 Hz | $+4{,}5\times10^{-3}$ | $+4{,}4\times10^{-3}$ | $\lesssim3\times10^{-4}$ | $\lesssim3\times10^{-4}$ |
| (2, 0) | 5 Hz | $-1{,}3\times10^{-2}$ | $-9{,}0\times10^{-3}$ | $\lesssim7\times10^{-4}$ | $\lesssim2\times10^{-4}$ |
| (2, 0) | 20 Hz | $+2{,}0\times10^{-2}$ | $+1{,}4\times10^{-2}$ | $\lesssim7\times10^{-4}$ | $\lesssim2\times10^{-4}$ |
| (2, +0,5) | 5 Hz | $-3{,}5\times10^{-2}$ | $-2{,}8\times10^{-2}$ | $\lesssim2\times10^{-4}$ | $\lesssim8\times10^{-4}$ |
| (2, +0,5) | 20 Hz | $+5{,}0\times10^{-2}$ | $+4{,}0\times10^{-2}$ | $\lesssim2\times10^{-4}$ | $\lesssim8\times10^{-4}$ |

A coincidência de $10^{-10}$ vale só para a janela em que foi construída. Mas separar os pares assim
exige SNR de memória de 20 a 300 (§3.3), fora do alcance de qualquer detector previsto para este
sistema; CE chega perto só do par (2, +0,5).

---

## 4. Tentativas de refutação

| # | Tentativa | Resultado |
|---|---|---|
| 1 | Os pares exatos são artefato do otimizador? | Não. Recalculei as memórias de B no processo principal, usei 4 partidas por caso e resolvi de novo no nível C partindo da solução do nível A (exp11); a coincidência se repete em $10^{-10}$–$10^{-12}$. |
| 2 | É artefato da janela? | **Em parte, sim** (exp14). A coincidência é das quatro memórias integradas numa janela dada; com outra janela os pares diferem em $10^{-3}$–$5\times10^{-2}$. O enunciado correto é "mesmas quatro memórias na mesma janela". |
| 3 | O nível C é confiável? | Só até $\sim10^{-3}$. O substituto viola em primeira ordem uma simetria exata (exp13), e A e C diferem de 0,3% a 9% nos multipolos dominantes. Por isso a família é testada resolvendo de novo em C, e não comparando números de níveis diferentes. |
| 4 | O resultado excêntrico PN era robusto? | **Não era, e foi corrigido.** A primeira versão (exp10 e exp10b) dizia que nenhuma excêntrica imitava a circular (resíduo ≥ 4%). Testando a suavidade do objetivo, achei um defeito: a grade de tempo terminava no último múltiplo de $dt$ antes da separatriz, onde o fluxo é máximo. As memórias pulavam $4\times10^{-4}$–$1{,}2\times10^{-3}$ sob passos de $10^{-5}$ em $M$, e as derivadas numéricas ficavam ~100 vezes erradas; o otimizador ficava parado no ponto de partida. Com a grade terminando exatamente na separatriz, a variação ficou suave ($3\times10^{-6}$ por passo) e o resultado mudou de natureza: sem spins, a excêntrica precisa de $\eta>1/4$ (§3.5). A conclusão antiga foi retirada. |
| 5 | As convenções do SEOBNRv5EHM batem? | Sim. Com $e_0=0$ ele reproduz o substituto em 0,0–0,8% (desl., spin, giro), com os mesmos sinais. As fases relativas dos modos ímpares diferem por $\pi$, o que é só uma escolha da origem da fase orbital; os multipolos $m=0$ não mudam. |
| 6 | A falta do modo (2,0) excêntrico no SEOBNRv5EHM pesa? | Não: $\le3\times10^{-4}$ (modelo PN). |
| 7 | O par global de 0,5% é real? | Indecidível com estes modelos: é menor que a diferença entre níveis. Em C continua 0,48%. |
| 8 | "Distinguível" depende de detalhes do match? | O match maximiza só sobre tempo e fase, não sobre os outros parâmetros, mas os pares B estão longe de A ($\rho_{\rm crit}$ de 0,9 a 5,9, contra SNR 66). Uma estimativa bayesiana completa não foi feita. |
| 9 | Um único sistema de referência basta? | Não para generalizar números: os pares de observador usam só o sistema A. A conclusão qualitativa (família de dimensão ≥ 2) vem da contagem e vale para qualquer A em que o posto seja 4. O estudo global usou 3 referências. |

---

## 5. O que já se sabia e o que é novo

**Estabelecido [E]:**
- memória de binárias em substitutos de RN [Yoo2023], em EOB [GPA2024] e em PN até 3PN [Favata2009b];
- memória de binárias excêntricas [Favata2011; EBF2019] e memória giroscópica PN [FS2025];
- modelos para o modo (2,0) e o efeito da memória na estimativa de parâmetros [RS2025; RH2025];
- a memória quebra a degenerescência distância–inclinação a partir de SNR ~90 [Xu2024]. No LISA, por
  análise de Fisher, ela ajuda pouco a estimar parâmetros de binárias massivas [GVB2023]. Aqui aparece
  um mecanismo parecido: a giroscópica ($\propto D^{-2}$) quebra a simetria PN que deixa as outras três
  ($\propto D^{-1}$) invariantes. Esses trabalhos usam a memória **junto com** a onda oscilatória;
  aqui a pergunta é o que as memórias determinam **sozinhas**;
- perspectivas de detecção [Lasky2016; Johnson2019; Hubner2020; GN2023] e cautelas sobre como afirmar
  uma detecção [ZMG2026];
- memória "órfã" de fontes cuja onda oscilatória está fora da banda [McNeill2017] e buscas de
  memória de fontes subsolares [ET2020]. É nesse cenário que a degenerescência deste estudo pesaria;
- modelos de forma de onda da memória [EN2025]; memórias superiores em RN [GM2024];
- recuperação de fase por STFT e FROG [AW2020; BEE2020];
- a simetria de troca em massas iguais (modos ímpares $\propto\chi_a$).

**Não encontrado na literatura** (busca de 31/10/2026 na web e na API do arXiv: memória ×
degenerescência × binárias; "mesmas memórias, ondas diferentes"; memória de spin × frequência orbital;
memória × massas iguais × spin antissimétrico). É elementar, mas não o vi enunciado:
- **[D]** pares explícitos de binárias da RG com as mesmas quatro memórias num observador, e sua
  classificação nos níveis A, B e C;
- **[D]** o argumento de que a família de filtros de fase não contém pares de binárias (§2.1);
- **[D]** a proposição de que as bilineares resolvidas no tempo determinam $h$ a menos de fase
  constante, e o estimador $\Omega_{\rm mem}=\dot h_{20}/(C|h_{30}|)$;
- **[D]** a cegueira de segunda ordem das memórias a $\chi_a$ em massas iguais (consequência imediata
  da simetria conhecida);
- **[D]** a violação dessa simetria pelos modos $m=0$ do NRHybSur3dq8_CCE, como medida do erro do modelo.

---

## 6. Resposta ao objetivo

**A degenerescência é só uma propriedade matemática de fontes artificiais, ou uma limitação real da
reconstrução histórica de fusões de buracos negros?**

1. **A parte infinita é matemática.** A família de histórias com as mesmas memórias, gerada por filtros
   de fase, existe para fontes arbitrárias e não contém pares de binárias da RG, porque a RG amarra a
   fase à amplitude.
2. **A parte finita é real.** Num observador, as quatro memórias integradas não determinam a
   binária: há famílias contínuas, de dimensão ≥ 2 (≥ 4 com excentricidade), de binárias com massas,
   razões de massa, spins, excentricidades, distâncias, inclinações e recuos diferentes e as mesmas
   quatro memórias. A família é exata nos níveis A e C (resolvida de novo), e no nível B não linear o
   par se desloca só $\sim10^{-5}$; só a simetria PN particular da ordem dominante é destruída.
3. **A limitação é das memórias integradas, não da informação disponível.** A onda oscilatória separa
   esses pares a partir de SNR 1–6. As memórias resolvidas no tempo, ou medidas em duas janelas,
   também os separam em princípio, mas exigem SNR de memória de 20 a 300. Um sistema tipo GW150914 a
   400 Mpc dá 0,8 em aLIGO e 39 em CE.
4. **Consequência prática.** Para uma fusão observada com a onda completa, a ambiguidade das
   memórias não limita a reconstrução. Para uma fonte vista só pela memória (onda oscilatória fora da
   banda), a reconstrução da história é ambígua por construção, e mais ainda com excentricidade.
   Nenhum algoritmo resolve isso sem informação adicional (`06_conclusoes_e_limites.md` §2).

---

## 7. Limitações e próximos passos

- **Só spins alinhados.** Com precessão há 12 parâmetros e a contagem sugere famílias maiores. O
  NRSur7dq4 não tem modos de memória, então só o nível A seria possível.
- **Excentricidade sem nível C.** Não há substituto de RN excêntrico com memória disponível aqui, e o
  SEOBNRv5EHM não tem modos $m=0$, então o nível B-NL não foi testado. O TEOBResumS-Dalí, que tem
  memória [GPA2024], não pôde ser compilado (bloqueio de permissão).
- **Um sistema de referência** para os pares de observador. Varrer o espaço de A mostraria onde a
  família tem fronteira, como em $q_B\ge4$.
- **Sem estimativa bayesiana completa.** "Distinguível" está no sentido de [LOB2008], par a par.
- **$\Omega_{\rm mem}$ precisa de calibração** dependente do conteúdo de modos. Com os modos do
  substituto ele é ruidoso; testar com modos de memória extraídos direto de simulações (SXS/CCE).
- **Memória órfã:** quantificar a família degenerada quando só a memória está na banda (fontes
  subsolares, [ET2020]). É onde este resultado tem consequência observacional direta.

## Como reproduzir

```bash
pip install numpy scipy matplotlib gwsurrogate surfinBH lalsuite teobresums
# pyseobnr 0.3.7 (SEOBNRv5EHM) precisa de pygsl_lite; no Python 3.13 compilei assim:
#   apt-get install libgsl-dev swig
#   echo "setuptools==75.8.0" > c.txt; PIP_CONSTRAINT=c.txt pip install pygsl_lite==0.1.8
#   pip install pyseobnr==0.3.7
cd codigo
python3 exp06_binarias_global.py        # niveis A/B/C, remanescente, ceu inteiro (~3 min)
python3 exp07_binarias_observador.py    # pares de um observador + formas de onda (~2 min)
python3 exp08_pn.py                     # simetria PN dominante x 1PN
python3 exp09_fase.py                   # observavel Omega_mem
python3 exp10_excentricas.py            # excentricas PN (inspiral) + TEOB circular
python3 exp10b_refutacao_excentrica.py  # partidas aleatorias (excentricas PN)
python3 exp11_robustez.py               # pares do exp07 nos niveis A, B, C (usa exp07_pares.json)
python3 exp12_excentricas_imr.py        # excentricas com fusao (SEOBNRv5EHM) (~10 min)
python3 exp12b_figura.py
python3 exp13_simetria_q1.py            # massas iguais: chi_a em 2a ordem
python3 exp14_janela_e_fase_pares.py    # dependencia da janela; Omega_mem nos pares
python3 exp15_snr_memoria.py            # SNR da memoria do sistema A
```

As saídas de texto estão em `resultados/` (`exp06`–`exp15`, mais `exp07_pares.json` e
`exp12_pares.json`). As figuras (`e6`, `e7`, `e9`, `e12`) estão em `figuras/`. O código de base está em
`codigo/binarias.py` (memórias nos três níveis), `codigo/deteccao.py` (unidades, curvas de ruído e
match) e `codigo/pn_excentrico.py` (inspiral excêntrica).
