# Verificação adversarial da linha D5: L08 e L09 (recuperação de fase pelos fluxos; memória no *ringdown*)

**Relatório verificado:** `linhas/L08_L09_fase_e_ringdown.md`. O relatório original não foi editado.

**Scripts de verificação** (todos em `codigo/revisao/`):

| Script | Saída | Tempo |
|---|---|---|
| `ver_D5_pesos.py` | `codigo/revisao/ver_D5_pesos.txt` | ~10 s |
| `ver_D5_edo.py` | `codigo/revisao/ver_D5_edo.txt` | 42 s |
| `ver_D5_quina.py` | `codigo/revisao/ver_D5_quina.txt` | ~30 s |

**Reexecuções.**
- `exp31_varios_modos.py` rodou numa cópia em diretório temporário. A saída é **idêntica** a `resultados/exp31_varios_modos.txt`, tirando as linhas de tempo.
- O desvio de fase do exp32 foi recalculado por álgebra própria a partir de `resultados/exp24_fisher_memoria.json` e `resultados/exp32_fase_ruido.json`.

**Rótulos.** [E] estabelecido, [D] derivado aqui, [H] hipótese.

## Resumo dos vereditos

| # | Afirmação | Veredito |
|---|---|---|
| 1 | Identidade $\dot u^2=4(uP-H^2)$, $\dot\psi=H/u$ (H08.1) | confirmado |
| 2 | $t_p=\arg\max H^2/P=\arg\max\lvert h\rvert$; $\kappa=54{,}6$ (H08.3) | confirmado ($\kappa=55{,}2$ só com dados) |
| 3 | Unicidade pelo ponto de retorno (H08.4) | **parcial**: vale para soluções $C^1$ (completei o passo não linear); há soluções $C^0$ com quina que têm os mesmos $P$ e $H$; a "confirmação numérica" é um artefato |
| 4 | Instabilidade para frente $10^{1{,}59\times10^5}$; condicionamento 1 desde $t_p$ (H08.5) | amplificação confirmada (PN); condicionamento **parcial** |
| 5 | Teste (a): reconstrução exata até $t_p+60$ (H08.6) | confirmado e reforçado: os erros relatados são do esquema de trapézio |
| 6 | Pesos por par, viés $b_{22\times32}=-3{,}615$, previsto contra medido (H08.8) | confirmado de forma independente (sxs); ressalvas no fim da inspiral e em $q=4$ |
| 7 | Zero do 3j para $\ell=3$ em $L=2$ (H08.8b) | confirmado |
| 8 | $K(\iota)$: ±10° → +18% / −21,5% (H08.11) | confirmado (números); a "ambiguidade exata" precisa ser qualificada |
| 9 | Ruído: CE 56 rad desde 10 Hz, ~1 bit só nos últimos 5 ms (H08.12) | confirmado (reprodução da álgebra; Fisher linearizado) |
| 10 | L09: batimento superamortecido; oscilação visível compatível com $(2,2)\times(3,2)$ | batimento confirmado; compatibilidade **parcial** (frequência 8–14% abaixo de todos os pares $m=2$) |

## 1. Identidade (H08.1): confirmado

**Derivação refeita à mão.** Com $h=ae^{-i\psi}$:
- $\bar h\dot h=a\dot a-ia^2\dot\psi=\tfrac12\dot u-iH$;
- $|\bar h\dot h|^2=uP$;
- logo $\tfrac14\dot u^2+H^2=uP$ e $P/H=\dot\psi(1+\dot a^2/(a^2\dot\psi^2))$, que é igual a $\dot\psi/(1-\dot a^2/P)$.

O sympy do exp30 (resíduo 0) está correto.

**Teste fora do substituto.** Usei um sinal analítico sintético (`ver_D5_edo.py`, parte 1): $a\propto{\rm sech}^{1/2}(t/40)$ e $\dot\psi=0{,}30+0{,}12\tanh(t/25)$.
- `exp30_comum.edo_retorno` reconstrói $\dot\psi$ com erro máximo $1{,}26\times10^{-9}$.
- O erro escala com $dt^2$: $5{,}1\times10^{-9}$, $2{,}0\times10^{-8}$ e $8{,}1\times10^{-8}$ para dt = 0,1, 0,2 e 0,4.
- O adiabático erra $4{,}8\times10^{-3}$.

## 2. Ponto de retorno e $\kappa$ (H08.3): confirmado

**Argumento.** $u_b\le u\le u(t_p)=u_b(t_p)$, logo $\max u_b=\max u$. Qualquer ponto que atinja $\max u_b$ tem $u=\max u$. O argumento está correto [D, elementar]. Ele exige $P>0$ e um máximo interior.

**$\kappa$ só com os dados.** Usei a série de Briot–Bouquet descrita na seção 3. O ajuste local de $u_b$ dá $y^*=6{,}697\times10^{-6}$, contra $a^2\ddot a^2/P=6{,}853\times10^{-6}$ calculado com a onda verdadeira. Daí $\kappa=\sqrt{P/y^*}=55{,}2$, contra 54,6 no relatório. A diferença de ~1% vem da derivada segunda numérica e não muda nada.

## 3. Unicidade (H08.4): parcial

### 3.1 O passo não linear que faltava [D, feito aqui]

Seja $w=u-u_b\ge0$ e $s=t-t_p$. Então $\dot w=\pm2\sqrt{Pw}-\dot u_b$. Perto de $t_p$, $\dot u_b\approx\ddot u_b s$ com $\ddot u_b<0$.

Com $w=s^2y$ obtém-se uma equação de Briot–Bouquet:

$$s\,\dot y=F_\sigma(y)=2\sigma\sqrt{Py}+|\ddot u_b|-2y,\qquad \sigma=(\text{ramo})\cdot{\rm sgn}(s).$$

**Solução verdadeira** (ramo + antes do pico e ramo − depois): $\sigma=-1$ dos dois lados.
- $F_{-1}$ é decrescente e tem uma raiz positiva única $y^*$.
- $F'_{-1}(y^*)=-2-\sqrt{P/y^*}<0$.
- Logo os desvios crescem como $|s|^{F'}$ quando $s\to0$. Só $y^*$ chega ao ponto, e em $w$ o expoente é $-\sqrt{P/y^*}=-\kappa$.
- Da relação $F(y^*)=0$ vem $y^*=a^2\ddot a^2/P$, exatamente o $\kappa$ linearizado do relatório.

**Ramo tangente** ($\sigma=+1$): a raiz é $y_+$, com $\sqrt{y_+}>\sqrt P$, e $F'_{+1}(y_+)=\sqrt{P/y_+}-2<0$. Esse ramo também é único.

Conclusão:
- A proposição do relatório (única solução $C^1$ com $u\to0$ em $\pm\infty$) está **correta**.
- O passo que o autor deixou em aberto fecha sem surpresa.
- O integrador próprio (Radau na variável $w$, partindo dessa série, `edo_propria`) reproduz a solução verdadeira: $1{,}3\times10^{-10}$ em $[-3000,-200]$ e $1{,}6\times10^{-8}$ em $[30,60]$ M.

### 3.2 A hipótese $C^1$ é essencial: contraexemplos $C^0$ (`ver_D5_quina.py`)

**Construção.** A curva é a solução verdadeira até $t_p$, segue o ramo + tangente de $t_p$ até $t_k$ e o ramo − depois de $t_k$. Integrei com Radau (rtol $10^{-12}$). Reconstruí $h=\sqrt u\,e^{-i\int H/u}$ (fase por antiderivada de spline) e recalculei $P$ e $H$ por diferenças finitas de 8ª ordem, a mais de 2,5 M das quinas.

| $t_k$ | máx $u/u_{\rm ver}$ | $\lvert\Delta$fase$\rvert$ em $t_p+30$ | máx $\lvert P_{\rm rec}/P-1\rvert$ | máx $\lvert H_{\rm rec}/H-1\rvert$ | $u/u_{\rm ver}$ em $t_p+60$ | sobreposição até $t_p+30$ |
|---|---|---|---|---|---|---|
| 1 M | 1,169 | 0,043 rad | $1{,}9\times10^{-6}$ | $1{,}0\times10^{-6}$ | 1,00000 | 0,99991 |
| 3 M | 2,479 | 0,683 rad | $6{,}7\times10^{-5}$ | $3{,}8\times10^{-5}$ | 1,00000 | 0,98211 |
| 6 M | 7,744 | 2,971 rad | $1{,}5\times10^{-5}$ | $7{,}1\times10^{-6}$ | 1,00000 | 0,82965 |
| 10 M | 25,84 | 9,210 rad | $8{,}9\times10^{-6}$ | $4{,}3\times10^{-6}$ | 1,00000 | 0,63776 |
| referência (sem quina) | 1,000 | 0,000 | $1{,}9\times10^{-6}$ | $1{,}0\times10^{-6}$ | 1,00000 | 1,00000 |

Essas curvas têm os mesmos $P$ e $H$ (até o piso numérico de $2\times10^{-6}$) e $u\to u_{\rm ver}\to0$ depois do pico. A fase pós-pico difere em até 9 rad.

O que as distingue é só a quina:
- $\dot a$ troca de sinal num instante;
- $\dot h$ é refletido, com $|\dot h|$ contínuo;
- o salto de $\dot u$ é de 0,27–0,75 $u$/M nas quinas do trapézio (`ver_D5_edo.txt`, parte 2).

Para ondas físicas (suaves) a hipótese $C^1$ é razoável, e a proposição sobrevive. Mas:
- A frase do resumo, "só a solução verdadeira atravessa o pico; as outras fogem ou morrem", é **falsa sem $C^1$**. Ela vale só para soluções que não trocam de ramo fora de $t_p$.
- Famílias que escapam antes do pico (desvio de $10^{-9}$ em $t=-30$ ou $-100$ M, depois quina) **não** voltam a zero dentro da janela ($u/u_{\rm ver}(t_p+60)\sim10^3$–$10^6$). Ali o critério "$u\to0$ no futuro" funciona.

### 3.3 A "confirmação numérica" da unicidade é um artefato

Na tabela de contração do relatório (§4.2), um erro de 10% em $u(t_p)$ cai a $4\times10^{-5}$ em 1 M. Ao reproduzi-la (`ver_D5_edo.txt`, parte 3), encontrei três coisas:

1. **Os números não dependem de δ.** Os desvios são idênticos, algarismo por algarismo, para $\delta=+10^{-3}$, $+10^{-4}$, $-10^{-3}$ e $-10^{-1}$. Por exemplo, $+4{,}5\times10^{-6}$ em $t_p-1$ e $+2{,}4\times10^{-5}$ em $t_p+1$. Isso inclui valores iniciais **abaixo** da fronteira, que são fisicamente impossíveis. O primeiro passo cai na fronteira $u=H^2/P$ (corte, "clip") e apaga o valor inicial.
2. **O integrador continua a partir daí.** A solução resultante é, na verdade, uma solução com quina em $t_p\pm0{,}25$ (seção 3.2), e não uma "solução que converge". O relatório interpretou como bom condicionamento o que é um exemplo de não unicidade $C^0$, com efeito pequeno quando a quina está a menos de 1 M do pico.
3. **O decaimento medido é do esquema, não da EDO.** O trapézio implícito é A-estável mas não L-estável. Com $L=2P/|\dot u|$, o fator por passo é $(1-L\,dt/2)/(1+L\,dt/2)$:

   | $t$ (M) | $L\,dt$ | Fator do trapézio | Exato $e^{-L\,dt}$ |
   |---|---|---|---|
   | −10000 | 6,2 | −0,51 | $2\times10^{-3}$ |
   | −1 | 15,4 | −0,77 | $2\times10^{-7}$ |
   | −0,5 | 33,4 | −0,89 | $3\times10^{-15}$ |

   A contração verdadeira entre $|s|=0{,}25$ e $|s|=1$ M seria $4^{-55}\approx10^{-33}$. O piso de $10^{-5}$–$10^{-6}$ é numérico.

**Status sugerido para H08.4:** confirmada matematicamente para soluções $C^1$, agora com o passo não linear completo. A afirmação "confirmada numericamente" deve sair. O enunciado deve explicitar que existem soluções $C^0$ com os mesmos $P$ e $H$.

## 4. Instabilidade para frente e condicionamento (H08.5)

**Amplificação: confirmado.** Na ordem dominante PN:
- $\varepsilon^{1/2}=(32/5)\eta x^{5/2}$;
- a taxa é $2P/\dot u\simeq(5/16)/(\eta x)$;
- $\int2P/\dot u\,dt=(5/1024)/(\eta^2x_i^5)$.

Com $\eta=0{,}2479$ e $x_i=0{,}0466$ (10 Hz), isso dá $\log_{10}=1{,}571\times10^5$, contra $1{,}59\times10^5$ no relatório. A taxa em $x=0{,}0942$ ($t\approx-1000$ M) dá 13,38/M, contra 13,26. É uma checagem analítica independente.

**Condicionamento 1,00: parcial.** O fator ~1 entre $\delta(P/H)$ e $\delta\dot\psi$ é verdadeiro, mas por um motivo que o relatório não diz. Com ruído suave de $10^{-3}$, **20,8%** dos passos da inspiral caem na fronteira, onde a EDO devolve o próprio estimador adiabático (clip 13662 no relatório). No fim da inspiral a EDO fica **pior** que o adiabático: rms $1{,}88\times10^{-3}$ contra $1{,}35\times10^{-3}$.

A EDO só ganha quando o erro relativo de $P/H$ fica abaixo de $\varepsilon$:

| Ruído | Passos na fronteira | rms no fim da inspiral (EDO) | rms (adiabático) |
|---|---|---|---|
| $10^{-3}$ | 20,8% (inspiral) | $1{,}88\times10^{-3}$ | $1{,}35\times10^{-3}$ |
| $10^{-5}$ | 0 | $9{,}5\times10^{-6}$ | $7{,}5\times10^{-4}$ |
| $10^{-7}$ | 0 | $3{,}3\times10^{-7}$ | $7{,}4\times10^{-4}$ |

Isso é coerente com H08.7 refutada: com fluxos de memória (erros de 1,5–8%) ou com ruído de detector, a EDO exata não acrescenta nada.

## 5. Teste (a) (H08.6): confirmado e reforçado

**Integrador independente** (Radau em $w$, com partida de Briot–Bouquet usando só os dados), no sistema A:

| Intervalo | Integrador próprio | `edo_retorno` |
|---|---|---|
| $[-3000,-200]$ | $1{,}3\times10^{-10}$ | $3{,}5\times10^{-10}$ |
| $[-200,-0{,}1]$ | $1{,}2\times10^{-9}$ | $4{,}3\times10^{-6}$ |
| $[0{,}1;30]$ | $6{,}4\times10^{-9}$ | $5{,}9\times10^{-6}$ |
| $[30,60]$ | $1{,}6\times10^{-8}$ | $1{,}4\times10^{-5}$ |

Os limites do relatório ($\le2{,}6\times10^{-5}$ até $t_p+60$) são do esquema de trapézio perto do ponto de retorno, não um limite intrínseco. Com dt = 0,5 (subamostragem), os erros do `edo_retorno` sobem para $1{,}4\times10^{-9}$, $8{,}5\times10^{-6}$, $2{,}4\times10^{-5}$ e $5{,}6\times10^{-5}$: ordem 2 na inspiral e ~1–2 perto do pico. A conclusão (reconstrução exata com $P$ e $H$ de um modo só) fica mais forte.

## 6. Pesos angulares e viés (H08.8): confirmado de forma independente, com ressalvas

**Implementação independente.** Usei `sxs.waveforms.memory.J_E` e `J_J` (Mitman et al., eqs. 17b e 17d), não a `taxas_m0` do projeto. Os sinais são circulares sintéticos com $\Omega=0{,}05$ (`ver_D5_pesos.txt`):
- Só o (2,2): taxa de $h_{20}$ por $P$ = 0,073576 = $C_E$; ${\rm Im}\,h_{30}$ por $H$ = 0,029200 = $C_J$; $g^E_{4,22}=0{,}000708$.
- Na escala do relatório, os pesos coincidem em 6 algarismos:
  - par 21: $g^E_2=-0{,}036788$, $g^J_3=-0{,}058399$;
  - par 44: $-0{,}037457$ e $-0{,}061939$;
  - par 43: $-0{,}009364$ e $+0{,}030969$;
  - 22×32: $+0{,}217641$ e $+0{,}191941$ (iguais para duas fases relativas, 0 e 0,7);
  - 33 e 32: $g^E_2=0$.
- $b_p$ reproduzidos: +0,8750, +1,1667, −0,7778, +2,2061, −1,8773 e **−3,6154**.

**Reexecução do exp31.** A saída é idêntica. Viés medido contra previsto na inspiral: −1,47/−1,52% (A), −2,06/−2,18% ($q=4$), −3,33/−3,54% ($q=1$, $\chi=0{,}6$) e −2,11/−2,21% ($q=2$).

**Ressalvas** (estão no arquivo do autor, mas não no resumo):
- **No fim da inspiral** a soma linear superestima o viés em 10–17%: −4,90 contra −4,45% (A), −4,76 contra −4,20% ($q=4$), −8,92 contra −7,64% ($q=1$, $\chi=0{,}6$) e −4,60 contra −4,16% ($q=2$). O "previsto a 3–6%" vale só na inspiral.
- **Em $q=4$**, o par 22×32 sozinho prevê −4,46% contra −2,06% medido; o resto é cancelado por outros pares. "Sobretudo $(2,2)\times(3,2)$" vale para massas quase iguais, não em geral.

## 7. Zero do 3j (H08.8b): confirmado

- O sympy dá $\begin{pmatrix}3&3&2\\2&-2&0\end{pmatrix}=0$. Para $\ell=2$, 4 e 5 os valores são não nulos: $\sqrt{70}/35$, $-4\sqrt{385}/1155$ e $\sqrt{4290}/715$.
- Como a linha de spin anula o fator para **todo** $m$, os modos 33, 32 e 31 não entram em $E_2$. O sxs confirma: $g^E_2=0$ para 33 e 32.
- Os pares cruzados $\ell\ne\ell'$ entram (33×43 e 22×32).

É uma regra de seleção elementar [D]. Não encontrei a frase explícita na literatura (Favata, ApJL 696 L159, só dá os $U_{L0}$ em termos de $I_{22}$), mas ela deve estar implícita nas fórmulas de memória por soma de modos. Não é um achado.

## 8. $K(\iota)$ (H08.11): confirmado nos números, qualificado no enunciado

Usei a fórmula do relatório com `harmonicos.sYlm` e o $g^E_4$ do sxs. Relativo a $K(50°)=-0{,}66445$:

| $\iota$ | 40° | 45° | 55° | 60° |
|---|---|---|---|---|
| $K/K(50°)-1$ | +0,1800 | +0,0946 | −0,1033 | −0,2148 |

São os números do relatório. Além disso, $K(90°)\approx10^{-16}$, porque $Y_{30}(\pi/2)=0$, como no item 9 da revisão.

**Qualificação.** A ambiguidade é exata no sentido de que os dados $(\lambda P,\mu H)$ são realizáveis por **algum** modo único: a EDO tem solução pelo ponto de retorno, com $u_b$ escalado e o mesmo argmax. A relação $\dot\psi'=(\lambda/\mu)\dot\psi$ é só aproximada, com correção $O(\varepsilon)$: a mudança $w=(\lambda/\mu^2)u'$ leva a $\dot w=(\lambda/\mu)\,2\sqrt{wP-H^2}$, que não é a EDO original. O próprio relatório mostra 0,3–0,4% depois do pico. Conviria escrever "ambiguidade exata de realizabilidade; a escala de $\Omega$ vale a $O(\varepsilon)$".

## 9. Fase com ruído (H08.12): confirmado (reprodução)

Recalculei $\sigma=\sqrt{g^{\rm T}(G+\Sigma_p^{-1})^{-1}g}$ com os gradientes de `exp32_fase_ruido.json` e o Fisher do D3:

| Detector | Desde 10 Hz | 20 Hz | 100 Hz | 5 ms antes do pico | 2 ms antes |
|---|---|---|---|---|---|
| CE, detector único | 56,3 rad | 19,0 | 1,17 | 0,755 | 0,345 |
| ET | 80 rad | — | — | 0,915 | — |

Os números são os do relatório. Em CE, ln M sozinho daria 39,9 rad, e a correlação ln M–$t_0$ é −0,53.

**Conferências.**
- A convenção de $t_0$ ($e^{-2\pi i f t_0}$, sinal $s(t-t_0)$) é a mesma do gradiente usado, $\partial_{t_0}=-(\dot\psi_b-\dot\psi_a)/M_s$.
- Os bits estão corretos: $\sigma=0{,}76$ dá 1,0 bit e $\sigma=0{,}34$ dá 2,1 bits.
- A conta "≈0,7 ciclo de 81,6" confere: 4,62 rad = 0,74 ciclo; 512,8 rad = 81,6 ciclos.

**Limite.** O Fisher é linearizado. Em ET ($\rho=8{,}6$) e na polarização × ($\rho_\times=3{,}2$ em CE) ele não é confiável, como o próprio autor reconhece. A conclusão qualitativa (a memória sozinha quase não prevê fase) é robusta, porque o erro é dominado por $\sigma_{\ln M}\cdot|t_a\dot\psi_a|$.

## 10. L09: parcial

**Confirmados.**
- QNMs com o pacote `qnm` (A: $M_f=0{,}94971$, $\chi_f=0{,}71404$): 220 = 0,5675−0,0845i; 221 = 0,5559−0,2553i; 320 = 0,8056−0,0881i; 200 = 0,4160−0,0886i. São idênticos aos do exp32.
- Batimento 220–221: $Q_b=0{,}0116/0{,}3398=0{,}034$. Superamortecido, confirmado.

**"Oscilação visível compatível com $(2,2)\times(3,2)$" (0,238/M): parcial.**
- O *pencil* dá 0,2175 (ordem 3) e 0,2051 (ordem 5) em A, e 0,2203 e 0,2176 em $q=1$. Fica 8–14% abaixo de 220×320 (0,2380).
- Fica abaixo de todos os outros pares $m=2$: 220×321 = 0,2297 e 221×320 = 0,2496.
- Uma "mistura de 220×320 e 221×320", como o relatório escreve, não produz frequência menor que as duas.
- O único par perto de 0,2175 é 330×430 (0,2198/M). Mas em $q=1$ sem spin os modos de $m$ ímpar são nulos por simetria, e ali o polo é 0,2203: logo também não é ele.
- O amortecimento medido, 0,2227, também não bate com 220×320 (0,1725).

Leitura mais honesta: há uma oscilação de ~0,21–0,22/M ainda não identificada. Provavelmente é conteúdo de fusão não QNM na janela $[10,60]$ M, já que o próprio autor nota a instabilidade do *pencil*.

**H09.3** (toque do (2,0,0) no resíduo RN − nula): os números conferem com o arquivo. A frequência fica a ≤1% (A e $q=1$), mas o amortecimento fica 15–28% abaixo. Concordo com "confirmada na frequência, inconclusiva no amortecimento".

## 11. Literatura e originalidade

**Como conferi.**
- A API do arXiv respondeu "Rate exceeded" em três tentativas (máquina compartilhada), e não houve resultado dela.
- Três buscas na web:
  - reconstrução de fase a partir de memória de deslocamento e de spin e de fluxos;
  - razão das taxas de memória e frequência orbital;
  - Favata 2009, termos de $|h_{33}|^2$ em $h_{20}$.
- Leitura (WebFetch) de arXiv:0902.3660 (Favata, ApJL 2009). Ela só dá $U_{20}$ e $U_{40}$ em termos de $I_{22}$, sem os pares $\ell=3$.

**Resultado.** Nenhum trabalho reconstrói o modo oscilatório a partir de $P$ e $H$ resolvidos no tempo, nem trata o ponto de retorno ou a ambiguidade $K(\iota)$. Isso é coerente com o relatório. Os resultados mais próximos são:
- Mitman et al., arXiv:2007.11562 (memórias de deslocamento e de spin em NR);
- Nichols, arXiv:1702.03300;
- Gasparotto et al., arXiv:2301.13228 (memória para parâmetros em LISA);
- arXiv:2403.13907 (memórias superiores, PN).

A busca é curta e incompleta. O autor não alega descoberta, e a matemática (problema radial, Briot–Bouquet, regra de seleção) é clássica.

## 12. Recomendações ao autor

1. **H08.4:** reescrever como "única entre as soluções $C^1$". Incluir o passo não linear da seção 3.1 e os contraexemplos $C^0$ da seção 3.2. Retirar a tabela de contração como evidência: ela mede o corte e o trapézio, não a EDO.
2. **Integrador:** trocar o trapézio por um esquema L-estável (Radau, BDF) ou pela série de Briot–Bouquet perto de $t_p$. Os erros pós-pico caem de $10^{-5}$ para $10^{-8}$.
3. **H08.5:** dizer que o "condicionamento 1" vem em parte do corte na fronteira (20,8% dos passos da inspiral com ruído de $10^{-3}$). A EDO só supera o adiabático com erros relativos de $P/H$ menores que $\varepsilon$ (~$10^{-4}$–$10^{-3}$).
4. **H08.8:** restringir o "previsto a 3–6%" à inspiral (10–17% no fim) e o "sobretudo 22×32" às massas quase iguais.
5. **L09:** trocar "compatível com $(2,2)\times(3,2)$, mistura de 220×320 e 221×320" por "não identificada (8–14% abaixo de todos os pares $m=2$)".

## Tabela de status após a verificação

| Id | Status no relatório | Status após a verificação |
|---|---|---|
| H08.1 | confirmada matematicamente | confirmada matematicamente (derivação refeita; sinal sintético $1{,}3\times10^{-9}$) |
| H08.3 | confirmada matematicamente e numericamente | confirmada ($\kappa=55{,}2$ só com dados, contra 54,6) |
| H08.4 | confirmada (linearizado) e numericamente | confirmada matematicamente **só para $C^1$** (passo não linear feito); "numericamente" é artefato; existem soluções $C^0$ com os mesmos $P$ e $H$ e fase até 9,2 rad diferente |
| H08.5 | confirmada numericamente | amplificação confirmada (PN $1{,}571\times10^5$); condicionamento parcial |
| H08.6 | confirmada numericamente | confirmada, com erro real ≤ $1{,}6\times10^{-8}$ (Radau) |
| H08.8 | confirmada numericamente | confirmada (pesos e $b_p$ exatos via sxs); ressalvas no fim da inspiral e em $q=4$ |
| H08.8b | confirmada matematicamente | confirmada |
| H08.11 | confirmada numericamente | confirmada (+0,1800 e −0,2148); escala a $O(\varepsilon)$ |
| H08.12 | confirmada numericamente (Fisher) | reproduzida (56,3 rad; 0,755 rad em 5 ms); limite de Fisher |
| H09.2 | refutada | refutada (superamortecido); a atribuição da oscilação a 22×32 fica inconclusiva |
| H09.3 | confirmada na frequência | concordo |
