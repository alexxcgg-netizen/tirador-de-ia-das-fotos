# Etapa 7 — Identificabilidade e conteúdo de informação da memória gravitacional

**Pergunta.** Que representação dos observáveis gravitacionais recupera o máximo da história física de
uma fonte? O que é recuperável, o que é irrecuperável, que observáveis acrescentam informação?

**Fontes.** Esta síntese junta as linhas desenvolvidas na etapa 7 (`linhas/`, um relatório por linha
mais uma verificação adversarial independente de cada um) e a revisão da etapa 6
(`08_revisao_e_correcoes.md`). Sempre que o verificador corrigiu o desenvolvedor, vale a versão do
verificador, e a correção é indicada. Os scripts estão em `codigo/exp17_*`–`exp40_*` e
`codigo/observaveis.py` (infraestrutura corrigida, `linhas/L00_*`). As saídas estão em `resultados/`.

**Rótulos.**
- [E] estabelecido;
- [D] derivado aqui;
- [H] hipótese.

Analítico = demonstração. Numérico = modelo específico, com o erro do modelo.

"Não encontrado" quer dizer que não apareceu em buscas no arXiv, Crossref e na web (em parte só em
resumos; a API do arXiv recusou consultas em três verificações). Não é garantia de ineditismo.

---

## 0. Resposta curta

1. **As quatro memórias integradas não são o observável.**
   - Um interferômetro não mede a memória giroscópica.
   - O CM se confunde com o instante de chegada.
   - A parte DC da memória de spin fica fora da banda.

   O que se mede é a **forma de onda da memória na banda**. Tratar as quatro memórias idealizadas como
   medidas superestima em ~2,5 vezes a informação intrínseca disponível (§3).
2. **A forma de onda da memória sozinha, mesmo em CE, determina ~3 combinações:**
   - o instante;
   - uma amplitude ($\cos\iota$ e $\ln D$);
   - uma escala de massa.

   Isso dá $d_{\rm ef}\approx3$ e só ~1–3 bits sobre os parâmetros intrínsecos (§3). Razão de massas e
   spins individuais ficam no prior. A degenerescência da "memória órfã", antes qualitativa
   ([McNeill2017; ET2020]), agora tem números. Ressalva importante: com **detector único**; numa rede
   que separa as duas polarizações ela encolhe (§3.3).
3. **No plano teórico há um teorema de identificabilidade (§1).** O mapa (parâmetros) → (memórias num
   observador):
   - tem posto genérico 4 (2 para o subconjunto deslocamento + spin);
   - tem loci exatos de queda de posto;
   - tem fibras de dimensão $n-4$;
   - tem uma fibra global conexa com uma dobra interior.

   No limite em que só o modo (2,2) irradia, spin e giroscópica são proporcionais a uma única
   quantidade. O posto intrínseco é então **exatamente 3**, e a direção quase nula do mapa real vem da
   quebra dessa identidade pelos modos superiores.
4. **Várias janelas no tempo não acrescentam informação além da forma de onda (§2).** A memória de
   banda é uma mudança de variável da energia de ligação ([Favata2009b] eqs. 3.15–3.16). Na ordem
   dominante ela só vê $\mathcal M^{5/3}/D$, e cada ordem PN acrescenta dois números. A segunda janela
   recupera informação que a forma de onda de uma janela já contém.
5. **Observável que preserva a fase (§4).** Sem ruído, os modos de memória resolvidos no tempo
   determinam o modo dominante a menos de uma fase constante, por uma EDO exata, se a solução for $C^1$.
   Três obstáculos:
   - num só observador, a frequência fica determinada só a menos de um fator $K(\iota)$;
   - com vários modos há um viés angular dominado pelo par (2,2)×(3,2);
   - com ruído realista a fase não se recupera (desvio de 56 rad em CE).
6. **Limites rigorosos novos (§6).**
   - $|D\,\Delta h|\le4E_{\rm rad}$, com 4 ótimo.
   - Constante ótima $c_L$ para radiação com $\ell\le L$: $c_2=\sqrt{30}/6$ e $4-c_L\approx8{,}886/L$.
   - Cota inferior da energia irradiada, sem modelo, $E_{\rm rad}\ge D|\Delta h|/c(e_2)$.
   - Cota de energia não gravitacional $E_{\rm ng}\ge D|\text{excesso}|/4$, para qualquer velocidade das
     partículas.
   - A lei da área de Hawking não é testável pela memória: só excluiria memórias de 4,5 a 78 vezes as
     da RG.
7. **Precessão e topologia (§5).**
   - As memórias globais de binárias precessantes têm posto 7 (módulo rotações) nos 7 parâmetros
     intrínsecos.
   - Os zeros do padrão de memória no céu são os "eixos ópticos" do tensor de memória, com índice +1/2
     cada (Poincaré–Hopf: soma 2).
   - Com precessão, os zeros seguem o eixo coprecessante ponderado pela luminosidade, e não o momento
     angular irradiado.
8. **Memória de CM como atraso (§7).** A memória de CM é exatamente (menos) o salto de deslocamento
   vezes o atraso entre o degrau real e o previsto pelo fluxo. A parte ordinária dá atraso de $M_f/2$
   em $\ell=2$. Medir $M_f$ assim não é competitivo: $\sigma(M_f)/M_f\ge0{,}43$ mesmo para $M=200$ em CE.

---

## 1. Identificabilidade (L01, L02, L18; `linhas/L01_L02_L18_*`)

### 1.1 Teorema de posto [D, analítico e numérico]

**Conjuntos de observáveis.**
- **T0:** as quatro memórias só com $m=0$, com deslocamento de janela.
- **T:** as quatro memórias com todos os $m$ e o azimute $\phi$ do observador.
- **O:** só deslocamento e spin, $m=0$. É o subconjunto que poderia vir de um interferômetro, mas
  ainda como números integrados (ver §3.4).

**Parâmetros:** $(M,q,\chi_1,\chi_2,D,\iota)$, mais $\phi$ em T.

1. **Posto genérico máximo.** Vale 4 (T0 e T) e 2 (O). Foi certificado em 135 pontos intrínsecos × 6
   inclinações (× 6 azimutes em T e O), com limiar de Weyl $\tau=\|E\|_F$ estimado por passos
   $h,h/2,h/4$. A razão mínima $\sigma_4/\tau$ é 71 em T0 e 14 em T. Em A (T0, escala absoluta) os
   valores singulares são 4,353; 1,672; 0,629; 0,111.
2. **Loci exatos de queda.** Em $\iota=\pi/2$ o posto cai para 3: spin e giroscópica são ímpares sob
   $\iota\to\pi-\iota$, para todos os $m$ (conferido a $5\times10^{-15}$). Em $\iota=0$ ele cai para 1
   em T0 e para 0 em O0, porque ${}_sY_{\ell m}(0)=0$, salvo $m=-s$. Com todos os $m$, o polo **não**
   é um locus de queda no modelo (valores singulares 1,379; 0,029; 0,019; 0,002). Mas esses números
   ficam abaixo do erro do modelo, de modo que isso não está certificado fisicamente (verificador).
3. **Simetria de troca.** Em $q=1$ com $\chi_1=\chi_2$, o posto intrínseco de T0 cai para 2: a coluna
   $q$ se anula e as colunas $\chi_1$ e $\chi_2$ ficam iguais. O substituto viola a simetria em
   $1{,}3\times10^{-4}$–$8{,}9\times10^{-4}$.
4. **Dimensão das fibras regulares.** É $n-k$: 2 (T0), 3 (T) e 5 (O). Excentricidade acrescenta 2
   ($e_0,\ell_0$) e precessão acrescenta 4, perto do setor circular alinhado (teorema do posto
   constante). Com excentricidade, a hipótese $C^1$ não foi testada contra o tremor do SEOBNRv5EHM.

### 1.2 O limite (2,2) e a origem da direção quase nula [D, analítico + numérico]

Se só o modo (2,2) irradia, valem razões universais, conferidas a 7 algarismos em 7 sistemas:

$$\frac{J^E_{20}}{E}=C_E=0{,}0735760,\qquad \frac{S_{30}}{H}=-C_J=-0{,}0291996,\qquad \frac{\Phi_{10}}{H}=0{,}162868,\qquad \frac{\Phi_{30}}{H}=-0{,}0533109,$$

com $H=\int{\rm Im}(\bar h_{22}\dot h_{22})\,du$ e a parte nula do CM identicamente nula.

**Consequência.** Spin e giroscópica são proporcionais a $H$, e **o posto intrínseco do modelo (2,2) é
exatamente 3** ($\sigma_4\sim10^{-13}$). A direção quase nula do mapa completo (vetor singular à
esquerda ≈ spin − giroscópica, igual em dois modelos a 0,5–7°) é a quebra dessa identidade pelos modos
superiores. A proporcionalidade é quase imediata a partir de [FS2025].

**Ressalvas do verificador.**
- O valor de $\sigma_4$ intrínseco depende do modelo: $9{,}5\times10^{-4}$ (CCE) contra
  $1{,}9\times10^{-4}$ (NRHybSur3dq8). Os jacobianos dos dois modelos diferem 15 a 70 vezes $\sigma_4$.
  O posto intrínseco 4 de T0 **não está certificado entre modelos**; a estrutura spin − giroscópica,
  sim.
- A direção quase nula da memória **não** é a degenerescência $q$–$\chi_{\rm eff}$ da onda
  [Baird2013]. O critério robusto: o desvio de 1σ da onda ao longo dessa direção é $1{,}2\times10^{-2}$
  (aLIGO) e $3{,}8\times10^{-4}$ (ET). O argumento de sinal do relatório foi retirado.

### 1.3 Observações multimensageiras [D, numérico]

- **$\iota$ e $D$ conhecidos (por exemplo, contraparte eletromagnética):** T0 é localmente
  identificável, mas mal condicionado. O problema quadrado tem **dobras genéricas**: em A,
  $\det J$ muda de sinal entre $\iota=37{,}0°$ e $37{,}5°$.
- **Com todos os $m$ (T):** sobra uma curva exata (resíduo $\le9{,}3\times10^{-11}$) com $q$ de 1,018
  a 1,208, $\chi_{\rm eff}$ de 0,064 a 0,073 e $M$ de 64,67 a 65,00.

Estruturas tão finas ficam abaixo do erro entre modelos (§8).

### 1.4 Fibra global [D, numérico]

**A fibra de T0 de A em $(q_B,\chi_{2B})$:**
- 75 de 117 pontos têm solução exata, formando **uma componente conexa**;
- a borda é em parte a parede $|\chi_1|=0{,}8$ e em parte uma **dobra interior**, onde duas soluções
  se fundem. Exemplo: em $q=3$, $\chi_2=-0{,}2$ há $\chi_1=0{,}675$ e $0{,}741$;
- ao longo da fibra, $M_B$ vai de 64,7 a 90,1, $D_B$ de 370 a 412 Mpc, $\iota_B$ de 46,7° a 64,8° e
  $M_f$ de 61,3 a 87,4 $M_\odot$.

**Os pares do exp07 continuam exatos com deslocamento de janela e com todos os $m$:**
- resíduos de $10^{-11}$–$10^{-10}$ (piso real ~$10^{-7}$ sob mudança de $dt$);
- com todos os $m$, $\chi_{1B}$ varia até 0,47 conforme o azimute;
- isso decorre do teorema de posto;
- as ondas continuam distinguíveis (match aLIGO 0,44–0,99).

**Invariantes.** O "orçamento de cargas" ($M_f$, $E$) não se conserva: varia 42% e 37% (H17). O
candidato $M_f(1+\nu)$, que varia 3%, é uma **tautologia** (verificador): é a razão observada
CM/deslocamento, fixa ao longo da fibra, reescrita com um fator angular.

### 1.5 Espectro de multipolos (L18) [D, numérico]

Cerca de um multipolo de memória por tipo é significativo ($>10^{-2}$ do maior); a giroscópica tem dois.
O número efetivo é $N_{\rm ef}=1{,}000$–$1{,}003$ (giroscópica 1,21–1,28). Multipolos com $\ell\ge6$
ficam abaixo de $4\times10^{-4}$ e não convergem nos modos de entrada.

O nível A do substituto CCE não tem os modos (3,1), (4,1), (4,2) (D6). Isso muda o deslocamento
$\ell=4$ de −13% a +46%, e todas as razões $\ell=4/\ell=2$ carregam esse erro (§8). A parte "BMS e
quântica" de L18 não foi desenvolvida.

---

## 2. Janelas e energia de ligação (L03, L04; `linhas/L03_L04_*`)

1. **Fatoração [E na forma; D na leitura].** Com janelas definidas por frequência:
   - deslocamento: $dm/dx=-\alpha(x)\,E_b'(x)$;
   - spin: $dm/dx=-\beta(x)\,x^{-3/2}E_b'(x)$, pela primeira lei $dE_b=\Omega\,dJ$ [LTBW2012].

   É a mudança de variável das eqs. 3.15–3.16 de [Favata2009b] (verificador). Na fatoração cancelam o
   fluxo e só a cauda dominante de 1,5PN. A partir de 2,5PN, $\alpha$ tem caudas: o termo
   $253\pi(4\nu-1)/96\,x^{5/2}$ é zero em $q=1$ e vale $-6{,}6\times10^{-4}$ em $q=3$, $x=0{,}04$. As
   razões $\alpha_2$ e $\alpha_4$ reproduzem [Cunningham2025] em 1PN e no termo spin-órbita de 1,5PN.
   O termo spin-órbita de $\beta_3$ não foi conferido de forma independente.
2. **O que cada ordem PN acrescenta [D, analítico].** O posto do jacobiano das memórias de banda é 2
   (newtoniano: só $\mathcal M^{5/3}/D$ e $\iota$), 4 (1PN) e 6 (1,5PN). **Cada ordem acrescenta dois
   números, não um**: deslocamento e spin têm coeficientes 1PN e SO diferentes.
3. **Concordância com o substituto.** O erro PN de banda cai até $1{,}2\times10^{-5}$, mas o teste é
   **circular** (verificador): as bandas usadas ficam na parte híbrida PN/EOB do NRHybSur3dq8_CCE
   (hibridização em $Mf\approx0{,}0055$–$0{,}0063$). Na parte de RN o erro não cai além de 2PN.
4. **Janelas como observável [D, numérico].**
   - Cada janela acrescenta até dois números até saturar, o que é contagem de equações: T0 vai de 4
     para 6; O0 de 2 para 4 e para 6.
   - Em O0 o sexto valor singular depende do ponto e das janelas por mais de uma ordem de grandeza
     (mediana $2\times10^{-7}$).
   - A família aproximada de duas janelas não encolhe com mais janelas em T0.
   - Em O0 o resíduo da família é $2\times10^{-6}$–$3\times10^{-5}$, muito abaixo de qualquer precisão
     realista.
5. **Desenho ótimo [D, numérico].**
   - Com ruído de CE/ET, 2–3 bandas bastam, e o ganho (~2 bits, em $\ln M$) depende do prior.
   - O ótimo de $K=2$ fica na borda imposta, $0{,}9f_{\rm pico}$.
   - A universalidade em $Mf$ é exata sem detector e é quebrada pela PSD ($f_{\rm corte}\propto M^{-0{,}72}$).
   - **O ganho em $\ln M$ já está na forma de onda de memória de uma só janela**: $\sigma_{\ln M}$/prior
     vale 0,38 com a série (exp24) contra 0,36 com duas bandas.

   Conclusão: dividir em janelas é só uma compressão da série temporal.

## 3. Conteúdo de informação da memória sozinha (L05–L07; `linhas/L05_L06_L07_*`)

### 3.1 Fisher da memória nula [D, numérico]

Sistema A (M = 65, q = 1,2, χ = (0,3; −0,2), D = 400 Mpc, ι = 50°), memória **nula** (pelo fluxo),
**detector único**:

| Detector | $\rho_{\rm mem}$ | $d_{\rm ef}$ | bits (total) | bits intrínsecos |
|---|---|---|---|---|
| aLIGO | 0,47 | 1,25 | 3,0 | 0,01 |
| A+ | 0,89 | 1,58 | 4,3 | 0,03 |
| ET | 8,6 | 2,56 | 10,3 | 0,61 |
| CE | 34 | 3,03 | 15,6 | 1,70 |

- **As três direções medidas em CE:**
  - $t_0$, a 1,09 ms;
  - a amplitude, $-0{,}90\cos\iota-0{,}36\ln D$;
  - a escala, $+0{,}95\ln M$, com $\sigma_{\ln M}=0{,}121$ contra prior 0,317.
- **Fisher reduzido aos intrínsecos:** um único autovalor perto de 1, quase só em $\ln M$.
- **Dependência do prior:** bits totais de 13,3 a 19,9 e bits intrínsecos de 1,2 a 2,7 (verificador).
- **Validade do Fisher** (critério de Vallisneri): vale nas 3 direções medidas
  ($\varepsilon\le0{,}08$ em CE) e falha nas dominadas pelo prior ($\varepsilon$ até 1091). O perfil em
  $\ln M$ é assimétrico (fator ~3).
- **A escala de tempo medida não é $M_f$** (refutado). Ao longo do vale
  $\ln M^*\approx4{,}12-0{,}12\,\chi_{\rm eff}$ nenhuma escala física simples é mais constante que $M^*$
  (nove abordagens).

### 3.2 A memória junto com a onda [D, numérico]

Somar a memória à onda oscilatória melhora o Cramér-Rao de $\ln D$ em 1% (aLIGO) e 8% (CE). O ganho de
informação é de 95,71 para 95,82 bits em CE. Isso é coerente com [Gasparotto2023; Xu2024].

### 3.3 Memória órfã [D, numérico]

Minimizando o mismatch sobre $(M,D,\psi,t_0)$, com um **detector único** em CE ($\rho=34$, limiar
$1/(2\rho^2)=4{,}3\times10^{-4}$):
- 72% do cubo $q\in[1,6]$, $\chi\in[-0{,}8,0{,}8]^2$ é indistinguível de A (63% com $M$ fixo);
- em ET, 100%;
- todos os pares do exp07 ficam dentro, com massas $M^*$ diferentes das do exp07;
- o parâmetro que mais separa é $q$ ($q\gtrsim4$).

**Ressalva do verificador:** a degenerescência usa a liberdade em $\psi$, que mistura o canal $h_\times$.
Numa rede ideal que mede $+$ e $\times$, o par $q_B=4$ já se separa ($8{,}3\times10^{-4}$, acima do
limiar). As frações acima valem **só para detector único**; o ET (triângulo) e redes reais não foram
calculados (§9).

### 3.4 O que um detector mede e as compressões [D, numérico]

- **O que se mede.** Um detector mede $t_0$, uma amplitude e uma escala. Uma rede que separa as
  polarizações acrescenta $\psi$ ($\sigma_\psi=0{,}015$, $d_{\rm ef}=4{,}46$).
  - Razão de SNR $\rho_+/\rho_\times=7$–10,6.
  - Do valor DC da memória de spin, só 29% está em 10 Hz e 11% em 50 Hz.
  - A giroscópica não tem sinal.
- **Compressões** (CE):
  - as quatro memórias integradas idealizadas dariam **251%** da informação intrínseca da série;
  - o degrau final retém 35% dos bits, mas só 2% (CE) a 7% (ET) da informação intrínseca;
  - amplitude + instante retêm 88–94% dos bits;
  - MOPED [HJL2000] retém 100% no ponto fiducial e 91–97% da informação intrínseca longe dele, com
    $t_0$ dado (verificador).
- **Aprendizado (L06, 6000 amostras).**
  - Sem ruído, $R^2$ = 0,99 em $\cos\iota$, 0,83 em $\ln M$, 0,26 em $q$ e 0,08 em $\chi_2$.
  - Com ruído real em CE, a série comprimida por MOPED mantém $R^2\approx0{,}5$ em $\ln M$, $\ln\mathcal M$
    e $\ln M_f$, confirmado com três aprendizes.
  - Deslocamento + spin integrados dão 0,08. Em ET, ≤ 0,16.
  - O estimador KSG de informação mútua subestima em até 40% em 9 dimensões.
- **A memória na banda não é um degrau.** $1-|T(f)|\approx c\,(2\pi Mf)^{1/4}$ na cauda da inspiral.
  A matemática assintótica confere, mas a transformada analítica, com função de Kummer, já está em
  [EN2025b] eqs. 56–57. A consequência "a forma só depende de $M/(\eta x_*^4)$" foi refutada na banda.

## 4. Fase recuperada dos fluxos (L08, L09; `linhas/L08_L09_*`)

1. **Identidades [D, analítico].** Para $h=a\,e^{-i\psi}$, $P=|\dot h|^2$ e $H=-{\rm Im}(\bar h\dot h)$:

   $$\dot u^2=4(uP-H^2),\quad u=a^2,\qquad \dot\psi=\frac Hu,\qquad \frac PH=\frac{\dot\psi}{1-\dot a^2/P},$$

   e o pico da amplitude é $t_p=\arg\max(H^2/P)=\arg\max|h|$, com $\max(H^2/P)=\max|h|^2$.
   Geometricamente, $h(t)$ é uma curva plana: $P$ é o quadrado da velocidade e $H$ o momento angular em
   torno da origem.
2. **Unicidade [D].**
   - A condição "$a\to0$ no passado" não fixa a solução (refutada).
   - Quem fixa é o **ponto de retorno**. O verificador completou o passo não linear de Briot–Bouquet
     ($F'(y^*)=-2-\sqrt{P/y^*}<0$), o que prova a unicidade **entre soluções $C^1$**.
   - Sem $C^1$ ela falha: há soluções $C^0$ com quina que têm os mesmos $P$ e $H$ e fase até 9,2 rad
     diferente.
   - Outros contraexemplos: uma circunferência e sua tangente; surtos disjuntos.
3. **Estabilidade.** Integrar para a frente amplifica erros por $10^{1{,}59\times10^5}$. A partir do
   ponto de retorno o condicionamento é ~1. A EDO só supera o estimador adiabático com erros relativos
   de $P$ e $H$ abaixo de ~$10^{-4}$.
4. **Testes.**
   - Com $P$ e $H$ do próprio (2,2), a reconstrução é exata: $\le1{,}6\times10^{-8}$ até $t_p+60M$ com
     um integrador de Radau (verificador).
   - Com $P$ e $H$ dos modos de memória, a EDO **não** melhora o $\Omega_{\rm mem}$ adiabático: o erro
     de 1,5–3,3% na inspiral e 4–8% no fim não é não adiabaticidade.
   - O erro é **contaminação angular**, sobretudo do par (2,2)×(3,2), com coeficiente
     $b=-3{,}6154$ (conferido com `sxs.waveforms.memory` a 6 algarismos). Modos com $\ell=3$ têm peso
     zero na projeção $L=2$ (zero exato de um símbolo 3j).
5. **Observador único.** Com $\iota$ desconhecido, $\Omega(t)$ só se determina a menos de um fator
   $K(\iota)$, que é uma ambiguidade exata da EDO: ±10° em $\iota$ dão +18% / −21,5%.
6. **Multipolos $m\neq0$.** Os multipolos $m\neq0$ do fluxo resolvido no tempo carregam a própria fase
   orbital: $\arg E_{44}+4\phi_{\rm orb}$ varia só 0,13 rad em 65 rad.
7. **Com ruído.** Pelo Fisher linearizado de §3, em CE o desvio da fase prevista desde 10 Hz é 56 rad.
   Ela só carrega mais de 1 bit nos últimos ~5 ms (0,7 ciclo de 81,6). **Na prática a memória não
   recupera a fase.**
8. **L09 (ringdown).**
   - Confere com [EN2025b]: a taxa da memória decai como $2\Gamma_{220}$, a 0,3–0,7%, entre 30 e 55 M
     depois do pico.
   - O batimento 220–221 é superamortecido ($Q=0{,}034$–$0{,}05$).
   - A oscilação visível de ~0,21/M fica 8–14% abaixo de todos os pares de QNM com $m=2$: **não
     identificada** (verificador).

## 5. Precessão e topologia do céu (L10, L11; `linhas/L10_L11_*`)

**Validação.**
- NRSur7dq4 e CCE concordam a 1–1,4% em desl20, spin30 e giroscópica, mas não em cm20 (até 4,8%) nem
  em $\ell=4$.
- Os modos $m=0$ coorbitais do NRSur7dq4 não contêm memória.

**L10 [D, numérico].**
- **Posto.** O jacobiano das 88 memórias globais ($\ell\le4$, todos os $m$), descontadas as rotações, tem
  **posto 7 de 7** nos 6 pontos testados. Acima de 1% de $|v|$, que é o erro entre modelos, sobram 5–6
  direções.
- **Hierarquia.** A direção mais fraca é o azimute comum dos spins no plano em 6 de 7 pontos (exceção:
  configuração de "supercoice"). A hierarquia $|\chi_{A\perp}|\gg|\chi_{B\perp}|$ falha com $q\approx1$.
- **Parte secular dos $m\neq0$.** É a rotação do padrão $m=0$ pelo eixo coprecessante: razão
  modelo/real de 0,83 a 1,05.
- **Um observador** vê 4 combinações de multipolos, das quais no máximo 2 são mensuráveis (§3.4). A
  razão $|\Delta h_\times|/|\Delta h_+|$ só é observável se $\psi$ vier da onda oscilatória.

**L11 [D, analítico + numérico].**
- **Eixos ópticos.** O padrão de deslocamento no céu é um campo de linhas (spin 2). Para o campo
  $\ell=2$ puro, os zeros são os **eixos ópticos** do tensor de memória, com
  $\sin^2\alpha=(\lambda_2-\lambda_3)/(\lambda_1-\lambda_3)$ e índice +1/2 cada. A matemática é a da
  óptica cristalina; a aplicação não foi encontrada.
- **Poincaré–Hopf** (soma dos índices = 2) vale em 68/68 sistemas.
- **Divisão dos zeros.** Só com $m=0$ há dois zeros +1 nos polos. A parte $|m|=2$ divide cada um em
  dois de +1/2, com meia abertura $\sim\sqrt{2\epsilon_2/\sqrt3}$. Partes de $m$ ímpar dividem em
  $O(\epsilon)$ e podem criar zeros de −1/2 (verificador).
- **Com precessão**, os zeros seguem o eixo coprecessante ponderado pela luminosidade, $e_Q$ (mediana
  0,89°, máximo 4,1°), e **não** $J_{\rm rad}$ (3,3°, máximo 19°) nem $\chi_f$ (6,0°). Confirmado numa
  população nova.

## 6. Limites memória–energia e canais não gravitacionais (L12–L15; `linhas/L12_a_L15_*`)

1. **Cota universal [D, analítico].** $|D\,\Delta h|\le4E_{\rm rad}$, porque a fórmula de Thorne (cuja
   normalização confere com a de modos a $9\times10^{-15}$) tem núcleo de módulo
   $(1+\hat n\cdot\hat N)/2\le1$. O 4 é o supremo, atingido no limite de um feixe dirigido ao observador.
2. **Radiação com $\ell\le L$ [D].** A constante ótima é $c_L=16\pi\lambda_{\max}$ de uma matriz de
   Gram:
   - $c_2=\sqrt{30}/6$, exato (sympy);
   - $c_3=1{,}852$, $c_4=2{,}239$, $c_8=3{,}006$;
   - $4-c_L\approx8{,}886/L$ (recalculado até $L=256$).

   Para o quadrupolo de uma binária na ordem dominante,
   $D\Delta h/E=\sin^2\iota\,(17+\cos^2\iota)/24$. Fixando a fração $e_2$ da energia em $\ell=2$, a cota
   $c(e_2)$ é um problema semidefinido: $c(0{,}99)=1{,}20$, com $c(1-\varepsilon)\approx c_2+2{,}94\sqrt\varepsilon$.
3. **Lei da área [D].** Em 9 binárias vistas de lado:
   - a memória fica em 1,3–4,7% da cota "$4E$ com $E$ máxima pela lei da área";
   - fica em 2,9–22% da cota "$c(e_2)$ com o spin final".

   Um teste da lei da área pela memória só excluiria memórias 4,5 a 78 vezes as da RG: **não é útil**.
   O teste de consistência com o fluxo das ondas é muito mais forte.
4. **Cotas inferiores sem modelo [D].**
   - $E_{\rm rad}\ge D|\Delta h|/c(e_2)$, que recupera 37–61% da energia verdadeira;
   - $E_{\rm ng}\ge D|\text{excesso de memória}|/4$ para qualquer velocidade $\beta\le1$ das partículas.

   As duas exigem conhecer $D$.
5. **Canais (L13).**
   - **Núcleo [E, MW2019].** O núcleo $\ell=0,1$ vale para qualquer $\beta$.
   - **Limite de velocidade [D, demonstrado pelo verificador].** O limite de baixa velocidade
     $\lambda_\ell(\beta)\to c_\ell\beta^\ell$ tem a forma fechada
     $c_\ell=2^{\ell-1}\ell!(\ell+2)!/(2\ell+1)!$. A entrada $\ell=8$ da tabela do exp29 estava errada
     por precisão numérica.
   - **Exemplo construído.** Duas histórias, uma só gravitacional e outra com 30% da energia num jato
     de neutrinos, têm a mesma memória nula no céu inteiro.
   - **O que quebra essa degenerescência:**
     - o perfil temporal;
     - a velocidade;
     - a polarização (um jato inclinado 15° gira a memória 10,6°; ver [CBV2024]);
     - a razão memória/oscilação.
6. **Momentos × janelas (L14).** Vale a versão do verificador.
   - **O que conta é a variável.** Funcionais numa variável adaptada ao fluxo (fração acumulada da
     memória $c(t)$: momentos de Legendre em $c$ ou janelas de energia igual) retêm a informação de
     Fisher: 94–97% com $K=12$ e $\ge99{,}7\%$ com $K\ge32$. Funcionais em $t$ uniforme não retêm.
   - **Dependência da janela.** Os momentos em $t$ mudam 21–92% quando o início da janela muda; os
     momentos em $c(t)$, $\le7\times10^{-5}$.
   - O condicionamento exponencial dos monômios é clássico (Hilbert, Vandermonde).
7. **L15 [D].** Todo fluxo sesquilinear local de campos sem massa depende só de $(B,A)$ e é invariante
   por um filtro de fase comum. Isso inclui a memória eletromagnética e a memória gravitacional de
   radiação eletromagnética. A memória linear só é invariante se $e^{i\varphi(0)}=1$. Com partículas
   massivas a redução a dois momentos falha: casando $\int S$ e $\int S/\omega$, as memórias diferem
   0,6–9,4%.

## 7. Memória de CM como atraso, e excentricidade (L16, L19; `linhas/L16_L19_*`)

1. **Identidade [D, analítico; conferida no LaTeX de Nichols 2018].** Integrando por partes a eq. 3.11
   de [Nichols2018], a memória de CM no nível da deformação é

   $$\mathcal K_\ell=-\Delta J_\ell\,\delta_\ell,$$

   onde $\delta_\ell$ é o atraso entre o centroide do degrau de RN e o do degrau previsto pelo fluxo
   (igual à integral no tempo do transiente do aspecto de massa). A parte ordinária dá
   $\delta_\ell^{\rm ord}=12M_f/((\ell-1)\ell(\ell+1)(\ell+2))$: $M_f/2$, $M_f/30$, $M_f/140$ para
   $\ell=2,4,6$. Com a parte nula, $\delta_2=0{,}26$–$0{,}60\,M$. É uma reformulação elementar; o uso
   como atraso não foi encontrado.
2. **Versão pontual refutada.** O transiente do exp09 não é $-\delta\,\dot S$: é 4 a 150 vezes maior.
   Depois de $u\ge16M$ ele é o toque do QNM (2,0,0), que explica 84–99% da variância. Perto do pico,
   precisa de sobretons ou de uma parte não QNM (verificador).
3. **Teste com o substituto: inconclusivo.** O substituto não consegue testar a identidade de centroide,
   porque o seu (2,0) deriva 3–10% em relação ao fluxo.
4. **Mensurabilidade [D, numérico; corrigida pelo verificador].**
   $\sigma(M_f)/M_f=\sigma_\delta/\delta_{\rm ord}$ vale 1,14 (A em CE), 4,42 (A em ET) e ≥ 0,43 (M = 200
   em CE). **Não é uma medida competitiva** de $M_f$; é um teste de consistência BMS. O "0,170 ms" citado
   no relatório de D3 é $|{\rm CM}/\Delta h|$; $M_f/2$ é 0,152 ms.
5. **Excêntricas.**
   - **Pares.** Com o (2,0) oscilatório e a energia de ligação excêntrica do EOB, os pares do exp12
     sobrevivem, mas só no nível do tremor do modelo ($1\times10^{-5}$–$2{,}4\times10^{-5}$). Resíduos
     menores são amostras de ruído.
   - **Duas janelas com $e_0$ e $\ell_0$ livres:** inconclusivo (melhor $3{,}6\times10^{-3}$, com
     orçamento limitado). As "direções excêntricas quase nulas" também ficaram inconclusivas: não se
     resolvem acima do erro das colunas.
   - **Dependência em $\ell_0$.** É linear em $e_0$ (primeiro harmônico $\approx0{,}04$–$0{,}05\,e_0$ no
     deslocamento) e vem dos últimos ~100 M. É qualitativamente física, porque $M_f$ oscila com a
     anomalia em RN [Nee2025]. A magnitude na memória **não** está validada: o controle PN só concorda
     em termos relativos (0,34–0,36 do valor absoluto), e não houve segundo modelo excêntrico.
     [GPA2024], com memória DC excêntrica no TEOBResumS-Dalí, deveria ser comparado.

## 8. Erro de modelo contra estrutura fina

As estruturas mais finas encontradas ficam todas abaixo do erro entre modelos:
- o $\sigma_4$ intrínseco ($10^{-4}$–$10^{-3}$);
- a dobra em $\iota\approx37°$;
- a curva de T com $\iota$ e $D$ conhecidos;
- a família de duas janelas em O0 ($10^{-6}$–$10^{-5}$);
- as direções excêntricas ($10^{-5}$).

O erro entre modelos medido aqui é:
- 1–1,4% em desl20 e até 4,8% em cm20 entre NRSur7dq4 e CCE;
- $\sigma_4$ diferindo por fator 5 entre dois substitutos;
- modos ausentes mudando desl40 de −13% a +46%;
- 5–12% no spin do nível C na parte híbrida (C18).

**Regra adotada:** só são afirmações físicas as estruturas que sobrevivem a dois modelos (a estrutura
spin − giroscópica, o posto genérico, os loci exatos, as identidades analíticas). O resto é propriedade
do modelo usado.

## 9. O que é recuperável e o que não é

| | Recuperável (com o detector certo) | Irrecuperável ou impraticável |
|---|---|---|
| Memória sozinha (memória órfã) | instante, uma amplitude ($\cos\iota$–$D$), uma escala de massa ($\sigma_{\ln M}\approx0{,}12$ em CE, $\rho=34$); $\psi$ com uma rede | razão de massas e spins (no prior); fase orbital; recuo; ~1–3 bits intrínsecos no máximo |
| Memória + onda oscilatória | ganho de 1–8% em $D$ | — |
| Memórias integradas teóricas (observador ideal com giroscópios e banda até DC) | 4 números com posto 4 (fibras de dimensão 2) | não existem fisicamente para interferômetros |
| Céu inteiro (observador ideal) | quase tudo nos parâmetros intrínsecos (posto 4 alinhado; 7 com precessão) | direções de segunda ordem ($\chi_a$ em $q=1$); estruturas abaixo do erro de modelo |
| Princípio (sem ruído) | o modo dominante a menos de uma fase constante, pela EDO dos fluxos | fase orbital absoluta; $K(\iota)$ num observador; partes que caem no horizonte (etapa 5) |

**Contribuições candidatas** (não encontradas na literatura; a confirmar por busca em texto completo):
1. O teorema de posto, com loci exatos, a identidade do limite (2,2) e o mapa da fibra global.
2. As constantes ótimas $c_L$ e $c(e_2)$ da desigualdade memória–energia, com as cotas inferiores sem
   modelo.
3. A forma fechada $c_\ell$ do limite de velocidade do núcleo.
4. A quantificação Fisher, informação mútua e região órfã da memória sozinha, em detector único.
5. Os eixos ópticos e o índice +1/2 dos zeros da memória no céu, seguindo $e_Q$.
6. A EDO exata de recuperação de fase com unicidade pelo ponto de retorno.
7. A leitura da memória de CM como atraso.

## 10. Contradições resolvidas e pendências

**Definições unificadas.**
- "Mensurável" = a forma de onda $F_+h_++F_\times h_\times$ na banda. Os postos de O e O0 (D1, D2, D6)
  são de um objeto teórico.
- As frações órfãs valem para detector único.
- $\delta_{\rm ord}=M_f/2=0{,}152$ ms no sistema A.

**Janelas contra séries.** A série resolvida no tempo já contém o que as janelas acrescentam (§2.5); a
base certa é a de funcionais numa variável adaptada (§6.6).

**Seguimentos de maior valor** (propostos pelo crítico de completude):
1. Memória órfã e Fisher numa **rede real** (ET triângulo, CE+CE+ET, $\psi$ e céu).
2. **Certificação entre modelos** (SEOBNRv5HM, IMRPhenomTHM, NRSur7dq4 com todos os modos) das
   estruturas quase nulas.
3. **Estrelas de nêutrons** com o TEOBResumS 4.4.1, que respeita $\Lambda$ (confirmado pelo crítico).
4. Validação com **RN CCE do SXS** (identidade do atraso, (2,0), modos ausentes).
5. **Posterior bayesiano** da memória órfã com emulador.
6. **Sistemas extremos** ($q$ até 15, IMBH).
7. Segundo modelo excêntrico.
8. A comparação janelas × momentos com detector real.
