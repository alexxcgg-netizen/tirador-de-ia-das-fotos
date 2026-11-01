# Verificação adversarial da linha D8 (L19: CM como atraso; L16: excentricidade)

Relatório verificado: `linhas/L16_L19_cm_e_excentricas.md`. Não editei esse relatório nem os scripts dele.

Scripts desta verificação (em `codigo/revisao/`):
- `ver_D8_jacobiano.py`
- `ver_D8_l19_series.py`
- `ver_D8_fisher.py`
- `ver_D8_anomalia.py`
- `ver_D8_pares_tremor.py`

Saídas (em `resultados/`): `ver_D8_jacobiano.txt`, `ver_D8_l19_series.txt`, `ver_D8_fisher.txt`,
`ver_D8_anomalia.txt` e `ver_D8_pares_tremor.txt`.

Rótulos: [E] estabelecido, [D] derivado aqui, [H] hipótese.

## Resumo

| # | Afirmação | Veredito |
|---|---|---|
| 1 | H19.1: identidade $K_\ell=-\Delta J_\ell\,\delta_\ell$ (atraso de centroide) | **confirmada** (refeita de forma independente; eq. 3.11 lida na fonte LaTeX de Nichols 2018) |
| 2 | H19.2: $\delta^\text{ord}_\ell=12M_f/[(\ell-1)\ell(\ell+1)(\ell+2)]$ | **confirmada** (direto das eqs. DeltaKlm e 4.23 de Nichols) |
| 3 | H19.3/H19.4 refutadas; H19.6: o transiente é o QNM (2,0,0) | refutações **confirmadas**; H19.6 **parcial**: vale para $u\ge16$ M, não perto do pico de $D$ |
| 4 | exp39: $\sigma_\delta$ e $\sigma(M_f)/M_f\ge0{,}37$ | $\sigma_\delta$ **confirmada**; $\sigma(M_f)/M_f$ **errada**: dividida pelo atraso total em vez do ordinário. O certo é ≥ 0,43 (A: 1,14, não 1,00) |
| 5 | H16.3: o menor valor singular cai de 5,4e−5 para 1,55e−5, logo as direções excêntricas entram no núcleo | **refutada como evidência**. A queda é garantida por entrelaçamento e não se distingue de colunas aleatórias; o erro das colunas (~1e−4) é maior que os dois valores singulares. Status correto: inconclusiva |
| 6 | H16.1: pares re-solvidos a 9,5e−7 até 2,4e−5 | **parcial**: os pares sobrevivem só ao nível do tremor, que medi entre 1,0e−5 e 2,4e−5. Resíduos menores que isso não significam nada |
| 7 | H16.4a,b: dependência em $\ell_0$ linear em $e_0$, nascida nos últimos 100 M | **confirmada** com quadratura independente (números reproduzidos a ≤2%) |
| 8 | H16.4c: o controle PN dá "quase os mesmos números" | **refutada como evidência**: só coincide a razão a uma média diferente; em valor absoluto o PN dá 0,34–0,36 do SEOBNRv5EHM |
| 9 | Originalidade (atraso; memória × anomalia) | **parcial**: não achei antecedentes; a API do arXiv recusou as buscas (limite de taxa); falta citar Grilli et al. 2024 |

---

## 1. H19.1: identidade do atraso de centroide [D, conferida]

**Fonte.** Baixei a fonte LaTeX de arXiv:1807.08767 e conferi a eq. `DeltaCalK`:
$$\Delta\mathcal K=\int_{u_1}^{u_2}(\Phi-\Phi_{(n)})\,du-u(\Phi-\Phi_{(n)})\big|_{u_1}^{u_2}.$$

**Rederivação independente.** Seja $E(u)=\Phi-\Phi_{(n)}$ e $D=E-E(u_1)$.
- Uma constante $c$ somada a $E$ contribui $c(u_2-u_1)-c(u_2-u_1)=0$. Logo $\Delta\mathcal K$ não depende do valor em $u_1$.
- Integrando por partes, $\Delta\mathcal K=-\int u\,\dot D\,du$.
- Com $D(u_2)=0$ (degraus iguais), $\int\dot D=0$. A expressão então não depende da origem de $u$ e vale
  $-\Delta J\,(\langle u\rangle_{\dot h}-\langle u\rangle_{\dot S})$.

**Termos lineares em $C$.** Conferi também que se cancelam na parte elétrica do balanço do aspecto de momento
angular. Para $C_{AB}=(2D_AD_B-\gamma_{AB}D^2)\Phi$:
- $D^CC_{CA}=D_A(D^2+2)\Phi$;
- $D_BD_AD_CC^{BC}$ e $D^2D^CC_{CA}$ valem os dois $D_AD^2f+D_Af$, com $f=(D^2+2)\Phi$.

**Ressalvas** (já presentes no relatório):
- a hipótese $D(u_2)=0$ despreza $m_\ell(u_s)\neq0$ e o recuo;
- a identidade fixa só o primeiro momento de $D$.

## 2. H19.2: atraso ordinário [E + D, conferido na fonte]

Nichols, eq. `DeltaKlm` mais eq. 4.23 (`KlmChargePhilm`):
$$\Delta\mathcal K^\text{ord}_{\ell m}=\frac{(\ell-2)!}{(\ell+2)!}\frac{64\pi}{\sqrt{\ell(\ell+1)}}\Big(-\frac{3M}{16\pi}\sqrt{\ell(\ell+1)}\Big)\Delta\Phi_{\ell m}=-12M\frac{(\ell-2)!}{(\ell+2)!}\Delta\Phi_{\ell m}=-\frac{3M}{2\mathfrak D_\ell}\Delta\Phi_{\ell m}.$$

Consequências:
- A razão entre CM e memória não depende da normalização dos potenciais. Logo
  $\delta^\text{ord}_\ell=12M/[(\ell-1)\ell(\ell+1)(\ell+2)]$, isto é, $M/2$, $M/30$, $M/140$, $M/420$.
- Isso coincide com o código (`observaveis.py`, `-1.5*Mf*dPhi/Dfrak`).
- Em Nichols, $M$ é a massa do estado estacionário, em ordem linear na memória. Usar $M_f$ é uma escolha; a
  diferença é de ordem $\Delta\Phi\,\Delta M$, e a variante já foi estimada em 0,47% (L00).

## 3. Transiente: atraso pontual (H19.3, H19.4) e QNM (H19.6)

Feito com `ver_D8_l19_series.py`, a partir de `exp38_series.npz`, nos sistemas q = 1, q = 4 e A.

**Teste pontual: reproduzido exatamente.**

| Sistema | max\|D\|/desl | $(M_f/2)\max\dot S$/desl | $\delta$ ajustado | $R^2$ |
|---|---|---|---|---|
| q = 1 | 0,177 | 0,0119 | 3,72 M | 0,275 |
| q = 4 | 0,488 | — | 15,4 M | — |
| A | 0,150 | — | 3,28 M | — |

- Melhor deslocamento: 2,50, 8,25 e 2,29 M.
- Com o intervalo $[-100,30]$ M em vez de $[-100,100]$ M: 3,5, 9,75 e 3,25 M.
- As refutações de H19.3 e H19.4 ficam de pé e não dependem do intervalo.

**QNM (2,0,0).** Variei o início do ajuste e comparei com hipóteses falsas:
- **A partir de 16 M:** reproduzido (0,976, 0,981 e 0,979 da variância). A frequência falsa do (2,2,0) dá 0,66,
  0,77 e 0,61, e uma exponencial sem oscilação 0,70, 0,64 e 0,69. O QNM é preferido, mas em q = 4 a frequência
  errada também explica 77–89% para início ≥ 16 M: a discriminação é fraca para q grande.
- **A partir do pico de $|D|$** (4,75 M em q = 1 e A; 8,25 M em q = 4):
  - o (2,0,0) sozinho explica só 0,83, 0,91 e 0,83;
  - com o sobretom (2,0,1), 0,95–0,99;
  - a frequência livre cai para 0,344–0,352, 15–17% abaixo do QNM.
  - O núcleo do transiente, onde está o max|D| citado no relatório, não é um único QNM fundamental.
- **Amplitude relativa do toque.** Depende do início do ajuste: em q = 1 vai de 0,225 (no pico) a 0,113 (16 M) e
  0,033 (30 M); em q = 4, de 0,61 a 0,46 e 0,11. O "0,02–1,09" do relatório só vale para o início em 16 M.

**Veredito.** H19.6 é "confirmada numericamente para $u\gtrsim16$ M". Perto do pico, os dados pedem sobretons
ou uma parte que não é QNM. A conclusão qualitativa (o transiente é o toque do aspecto de massa, não um atraso)
se mantém.

## 4. Mensurabilidade (exp39)

`ver_D8_fisher.py` refaz o produto interno de forma independente:
- FFT de $\dot s$ reamostrado por spline;
- janela de Tukey só no início, de 0,1 ou 0,5 s;
- $f_s$ de 2048 ou 4096 Hz;
- $\rho$ por $|\tilde s|=|\widetilde{\dot s}|/2\pi f$.

Reproduz, sem dependência das escolhas, $\rho_\text{nula}$ (0,470 / 0,892 / 8,64 / 34,09) e $\sigma_\delta$
(7674 / 4035 / 656 / 170 µs) para aLIGO / A+ / ET / CE. Também reproduz $\delta_\text{tot}=0{,}5303$ M = 169,8 µs.

**Erro encontrado.** O exp39 imprime $\sigma(M_f)/M_f=1/(\delta_\text{tot}/\sigma)$. O próprio relatório diz que
só a parte ordinária do atraso é proporcional a $M_f$; a parte nula é prevista pela onda oscilatória. O certo é
$\sigma(M_f)/M_f=\sigma_\delta/\delta_\text{ord}$, com $\delta_\text{ord}(\iota=50°)=0{,}4632$ M (o arquivo do
exp39 já traz a coluna "ord"):

| Caso | Valor do relatório | Valor correto |
|---|---|---|
| A, CE | 1,00 | **1,14** |
| A, ET | 3,86 | 4,42 |
| M = 120, CE | 0,53 | **0,61** |
| M = 200, CE | 0,37 | **0,43** |
| M = 200, ET 5 Hz | 1,24 | 1,44 |

Eventos iguais ao A para 3σ em CE: 9/0,875² ≈ 12, não 9.

A conclusão (H19.8 refutada) fica mais forte. O número "≥ 0,37" deve ser "≥ 0,43".

## 5. H16.3: jacobiano de duas janelas com direções excêntricas

`ver_D8_jacobiano.py` usa o `J7` salvo em `exp40_jacobiano.json`.

**Entrelaçamento [E].** Para $A=[B\,C]$ com $B$ de 7 × 5, $\sigma_7(A)\le\sigma_5(B)$. Acrescentar duas colunas
**sempre** abaixa ou mantém o menor valor singular. A queda de 5,39e−5 para 1,55e−5 não é, por si, evidência.

**Base aleatória.** Troquei $(X,Y)$ por vetores gaussianos com as mesmas normas (20 000 sorteios):
- $\sigma_\text{min}$ mediano 2,7e−5, com quantis de 10% e 90% em 5,4e−6 e 4,9e−5;
- 29% dos sorteios ficam ≤ 1,55e−5.
- O valor real é típico de colunas quaisquer.
- Ele também depende da escala escolhida para $(X,Y)$: 2,7e−6 com escala × 0,1 e 1,8e−5 com × 10.

**Resolução.** As colunas circulares têm erro entre passos $h$ e $h/2$ de até 16% (coluna $M$). Em valor absoluto,
nas unidades escaladas:

| Coluna | Erro absoluto |
|---|---|
| $\iota$ | 1,4e−5 |
| $\chi_1$ | 1,6e−3 |
| $M$ | 4,1e−3 |
| $q$ | 1,2e−3 |
| $\chi_2$ | 6,9e−4 |

- O tremor medido (§6, até 2,4e−5) dividido pelo passo também dá ~1e−4 por coluna.
- Pela desigualdade de Weyl, valores singulares de 5e−5 e 1,5e−5 não são resolvidos.
- Com ruído desse tamanho nas colunas circulares, $\sigma_\text{min}$ de $B$ tem mediana 7e−4 e o de $J_7$
  5,5e−5, com 10%–90% em 1e−5 e 1,3e−4.

**O que resta de específico.** O vetor singular mais fraco tem peso 0,54 em $(X,Y)$, contra 0,025 com colunas
aleatórias. É um indício, mas sobre um jacobiano não resolvido. As colunas $(X,Y)$ também mudam 146–195% entre
$e_0=0{,}03$ e 0,06.

**O teste direto não confirma.** As quatro buscas locais param em 1,5e−4 a 6,6e−4, acima do controle circular
(2,4e−5).

**Veredito.** H16.3 deve passar de "confirmada numericamente" para **inconclusiva**. O "deslocamento de 0,64
unidades que muda os resíduos só 1e−5" vem de um $\sigma_\text{min}$ que não está resolvido.

## 6. H16.1: pares do exp12 com as correções

`ver_D8_pares_tremor.py` avalia dois pares re-solvidos:
- **No ponto re-solvido:** reproduz 9,50e−7 ($e_0=0{,}1$, $q_B=1{,}2$) e 1,55e−6 ($e_0=0{,}2$, $q_B=2$).
- **Com perturbações inobserváveis** ($M$ ou $\chi_1$ × (1 + 1e−10, 1e−8, 1e−6), ou $\ell_0=10^{-6}$): o
  resíduo salta para 1,0e−5 a 1,55e−5 no primeiro par e para 3,7e−6 a 2,4e−5 no segundo.
- O deslocamento sozinho muda ~1,1e−5 com $\Delta M/M=10^{-10}$.

Consequências:
- O piso real é 1e−5 a 2,4e−5. Os resíduos de 9,5e−7 a 5e−6 são pontos de sorte achados pelo otimizador. O
  relatório reconhece isso em II.6, mas os destaca no resumo e na tabela.
- A afirmação de que as correções mudam B **acima** do tremor vale só por um fator de 2–4 (4,1e−5 e 4,6e−5
  contra até 2,4e−5).
- Os pares sobrevivem às correções, mas só ao nível do tremor.
- No par $e_0=0{,}1$, $q_B=1{,}2$, $\chi_1$ mudou 0,034. Esse par do exp12 não estava convergido (5,5e−4), então
  não é "o mesmo par" corrigido.

## 7. H16.4a,b: dependência na anomalia

`ver_D8_anomalia.py` usa uma quadratura independente:
- derivada de 2ª ordem;
- integrais de Gaunt calculadas por Gauss-Legendre (sYlm conferido contra a forma fechada de ${}_{-2}Y_{22}$ a 1e−12);
- sem o (2,0) newtoniano;
- 16 valores de $\ell_0$, contra 12 no exp40.

| Sistema, $e_0$ | $a_1$(desl20) aqui | Relatório | $a_1(M_f)$ aqui | Relatório | Últimos 100 M / total (correlação) |
|---|---|---|---|---|---|
| A, 0,05 | 2,01e−3 | 2,0e−3 | 9,85e−5 | 9,8e−5 | 1,37 (0,94) |
| A, 0,1 | 4,17e−3 | 4,1e−3 | 2,00e−4 | 2,0e−4 | 1,34 (0,93) |
| A, 0,2 | 8,09e−3 | 8,1e−3 | 4,01e−4 | 4,0e−4 | 1,39 (0,92) |
| B, 0,2 | 9,29e−3 | 9,3e−3 | 3,36e−4 | 3,4e−4 | 1,43 (0,92) |

- Expoente em $e_0$: 1,00 (0,05–0,2).
- Subamostragem com 8 pontos: o mesmo $a_1$, sem aliasing.
- Com a janela desde −3000 M, a variação é 0,94–0,99 da total.
- **Confirmado** dentro do modelo SEOBNRv5EHM. A física da magnitude continua não validada, como o relatório diz.

## 8. H16.4c: o controle PN

O relatório compara o 1º harmônico **relativo**:
- PN: 4,5e−3, 9,3e−3 e 1,50e−2;
- SEOBNRv5EHM: 4,5e−3, 9,3e−3 e 1,56e−2.

As médias são muito diferentes (`exp40_anomalia.json`): a memória PN até a separatriz vale 2,35e−2, contra
6,65e−2 do SEOBNRv5EHM. Em valor absoluto, o 1º harmônico PN é **0,34–0,36** do SEOBNRv5EHM (1,07e−4 contra
3,01e−4 em $e_0=0{,}1$).

A coincidência relativa é de normalização. O efeito PN vem de cortar a emissão num instante secular fixo, um
artefato de borda que o próprio relatório descreve. O controle PN não sustenta a magnitude e não deve ser
apresentado como "quase os mesmos números". O apoio à natureza física fica só no qualitativo, por [Nee2025].

## 9. Literatura e originalidade

**API do arXiv.** Dez consultas, todas recusadas com "Rate exceeded": a máquina é compartilhada e esperei 35–60 s
entre tentativas. Não verifiquei por essa via.

**WebSearch.**
- "center-of-mass memory time delay ringdown mass aspect": volta Nichols 2018, Siddhant & Grant 2024 e
  arXiv:2110.15922. Nada sobre a leitura de atraso.
- "memory dependence on mean anomaly eccentric": volta arXiv:2510.08105 (já citado), Favata 2011, Islam et al.
  (arXiv:2109.00754) e **Grilli, Placidi, Albanesi, Grignani, Orselli, arXiv:2410.05386**. Este último põe a
  memória DC (Ebersold et al.) em variáveis EOB excêntricas no **TEOBResumS-Dalí** e estuda a dependência na
  excentricidade. O relatório não o cita.
  - Pelo resumo, não trata da anomalia.
  - É o "segundo modelo excêntrico" cuja falta o relatório lamenta. O ramo Dalí do TEOBResumS, com memória,
    existe na literatura.

**Na fonte de Nichols 2018.** Não há "time delay", "delay" nem "time shift" no LaTeX. A única leitura de atraso
ali é entre observadores, como o relatório diz.

**Veredito.** A ausência de antecedentes para as duas leituras é plausível, mas a busca está incompleta (sem a
API do arXiv). O relatório já não alega descoberta, o que é adequado.

## 10. Recomendações ao autor

1. Corrigir $\sigma(M_f)/M_f$ (§4): usar $\delta_\text{ord}$; o limite passa a ≥ 0,43.
2. Rebaixar H16.3 para inconclusiva (§5). Para testá-la de verdade: passos maiores com várias réplicas para
   estimar o ruído das colunas, comparação com colunas aleatórias, e buscas diretas mais longas.
3. Nas tabelas, informar o piso como ~1e−5 a 2,4e−5 e não destacar resíduos abaixo dele (§6).
4. Reescrever o controle PN em valor absoluto (§8).
5. Restringir H19.6 a $u\gtrsim16$ M e dizer que a amplitude do toque depende do início do ajuste (§3).
6. Citar arXiv:2410.05386 e considerar o TEOBResumS-Dalí como segundo modelo.
