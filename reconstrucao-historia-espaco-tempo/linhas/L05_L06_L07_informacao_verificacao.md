# Verificação adversarial da linha D3 (L05, L06, L07): informação, Fisher e memória órfã

Relatório verificado: `linhas/L05_L06_L07_informacao.md` (não editado). Scripts de verificação, todos novos:
`codigo/revisao/ver_D3_comum.py`, `ver_D3_fisher.py`, `ver_D3_orfa.py`, `ver_D3_lei_quarto.py`, `ver_D3_L06.py`.
Saídas: `resultados/ver_D3_fisher.{txt,json}`, `resultados/ver_D3_orfa.{txt,json}`, `resultados/ver_D3_lei_quarto.txt`,
`resultados/ver_D3_L06.txt`. Tudo rodou com `OMP_NUM_THREADS=1` e no máximo 2 processos (Fisher 123 s, órfã 433 s).

## Pipeline independente

O exp24 usa um módulo próprio (`exp24_comum.py`): tensores esparsos, "espectro exato do degrau mantido", derivada em
ln M pela lei de escala, produto com peso fracionário no bin de 10 Hz. Para não herdar erros dele, escrevi
`ver_D3_comum.py` com escolhas diferentes em cada etapa:
- a série vem de `observaveis.serie_memoria(tipo='nula', magnetica=True)`, o código do L00;
- o espectro sai de uma reamostragem a 4096 Hz no tempo físico (t = 0 no pico), com valor final mantido 4 s e uma rampa de cosseno de 8 s, numa FFT de 128 s;
- a derivada em ln M é uma diferença finita física: a onda é gerada de novo em $M e^{\pm h}$, com a janela sempre desde 10 Hz;
- cos ι também vai por diferença finita;
- o produto interno é uma soma de Riemann simples a partir de 10 Hz.

## V1. Fisher da memória sozinha (H05.1, H07.1): **confirmado**, com ressalva sobre os priors

Rodei duas vezes, com passos (h_lnM, h_q, h_χ) = (0,01; 0,01; 0,01) e (0,03; 0,02; 0,02) (`ver_D3_fisher.txt`):

| | relatório (exp24) | verificação (passos 1) | verificação (passos 2) |
|---|---|---|---|
| ρ+, ρ× CE | 34,087 / 3,211 | 34,089 / 3,211 | idem |
| ρ+ ET | 8,636 | 8,638 | idem |
| λ' CE (4 maiores) | 8,7e4; 1,97e3; 11,8; 0,11 | 8,705e4; 1,969e3; 11,76; 0,110 | 8,705e4; 1,969e3; 11,76; 0,111 |
| d_ef aLIGO/A+/ET/CE | 1,25/1,58/2,56/3,03 | 1,251/1,583/2,560/3,027 | idem |
| I (bits) CE; I_intr CE | 15,6; 1,70 | 15,59; 1,704 | 15,59; 1,704 |
| σ_lnM, σ_cosι, σ_t0 (CE) | 0,121; 0,235; 1,09 ms | 0,121; 0,235; 1,09 ms | idem |
| autovetores CE 2 e 3 | −0,90 cos ι −0,36 ln D…; +0,95 ln M… | −0,905 cos ι −0,357 ln D +0,15 χ1 +0,13 ln M; +0,95 ln M −0,17 ψ +0,13 cos ι | idem |

Com outro espectro, outra quadratura e outras derivadas, os números batem com os do relatório em 3 algarismos.
Isso inclui a derivada em ln M feita pela lei de escala (o T4 do relatório dava 0,3–1%; na matriz final o efeito é
menor que o arredondamento).

**Sensibilidade aos priors, que o relatório só menciona:**
- O total de bits é quase convenção. Com o prior de $t_0$ em 10 ms, 50 ms ou 1 s, I(CE) vale 13,3 / 15,6 / 19,9 bits.
- $d_{\rm ef}$ é robusto: 3,03 nos três casos.
- $I_{\rm intr}$ depende do prior de massa: com $M$ num fator 2, 3 ou 10, vale 1,18 / 1,70 / 2,69 bits em CE e 0,33 / 0,61 / 1,34 em ET.
- A conclusão qualitativa se mantém: em CE, três direções acima de 1 ($t_0$, amplitude, escala de massa).
- Os valores "1,7 bits intrínsecos" e "16% dos bits" devem ser lidos como relativos ao prior escolhido.

## V2. Memória órfã (H05.7, H05.8): números **confirmados** para detector único; conclusão **parcial**, porque depende da liberdade de ψ

Repeti a minimização com código próprio (`ver_D3_orfa.py`):
- a série de B foi gerada em $M_{\rm ref}=45{,}5$ e reescalada no tempo;
- o espectro foi refeito pelo método da rampa;
- o tempo foi buscado com zero padding ×16 mais refino;
- $M$ foi buscado numa grade de 25 pontos em [0,7; 1,5]·M_A mais Brent.

Em detector único, o mínimo coincide com o exp26 em 3–4 algarismos:

| ponto | 1−match mín. (exp26) | verificação | M* exp26 / verif. |
|---|---|---|---|
| exp07 q_B=2 | 1,350e-5 | 1,351e-5 | 63,49 / 63,49 |
| exp07 q_B=4 | 8,066e-5 | 8,067e-5 | 53,92 / 53,92 |
| exp07 q_B=6 | 3,129e-4 | 3,130e-4 | 53,05 / 53,05 |
| canto (1; 0,8; 0,8) | 5,72e-6 | 5,72e-6 | 50,45 / 50,45 |
| canto (6; −0,8; −0,8) | 1,173e-3 | 1,173e-3 | 70,90 / 70,90 |
| canto (6; 0,8; 0,8) | 3,926e-4 | 3,927e-4 | 50,52 / 50,52 |
| (5; 0; 0) (novo) | — | 6,17e-4 (sai) | — / 57,8 |

Pelo `exp26_orfa_A.json`, a fração do cubo de Sobol abaixo de 4,30e-4 é 0,725 com $M$ livre e 0,631 com $M=65$,
como no relatório.

**Contraexemplo à leitura física.** A degenerescência em detector único usa a liberdade de ψ, isto é, mistura o
canal $h_\times$ (a memória de spin) de B. Fiz dois testes:
- **(a) B só com $h_+$, no mesmo M\*:** 1−match sobe para 1,29e-3 (q_B=4), 3,5e-3 (q_B=6) e 3,5e-3 (canto 6, +0,8).
- **(b) Rede ideal "+ e ×"** (dois detectores a 45°, que medem os dois canais; molde de B = amplitude × rotação 2ψ;
  $M$, ψ e o tempo livres; ρ_rede = 34,24, limiar 4,26e-4):
  - q_B=2 continua indistinguível (3,6e-5);
  - **q_B=4 sai** (8,3e-4, mínimo interior com M* = 47,0);
  - o canto (1; +0,8; +0,8) fica no limiar (4,8e-4) e (6; −0,8; −0,8) sai (4,7e-3);
  - q_B=6 e (6; +0,8; +0,8) chegam à borda da grade (M* = 45,5), com 1,9e-3 e 2,5e-3 lá: inconclusivos, porque o mínimo pode estar abaixo de 0,7 M_A.

Consequências:
- "72% do cubo" e "todos os pares do exp07 ficam dentro" valem para **um** interferômetro em L com ψ livre.
- Numa rede que mede as duas polarizações (CE terá dois sítios; ET é um triângulo, que mede as duas), parte da
  região sai, e o par q_B=4 do exp07 já se separa com ρ=34.
- O relatório não testou a região órfã em rede. O "100% em ET" usa ET como detector único, o que ET não é.
- H05.7 e H05.8 deveriam dizer "detector único".

## V3. Lei $(Mf)^{1/4}$ (H05.5): derivação **confirmada**; originalidade **enfraquecida**

**Derivação refeita à mão.** Da taxa $\dot h=(A'/4)\tau^{-5/4}$, com $\int_0^\infty\tau^{s-1}(e^{i\omega\tau}-1)d\tau=\Gamma(s)(-i\omega)^{-s}$
e $s=-1/4$, sai $T=1+(A'/4)\Gamma(-\tfrac14)(-i\omega)^{1/4}/\Delta H$. Como $\Gamma(-1/4)<0$:
$1-|T|\simeq c\cos(\pi/8)(\omega M)^{1/4}$, com $c=|\Gamma(-\tfrac14)|(5/\eta)^{1/4}/(16x_*)$, como no relatório.

**Teste numérico exato** num modelo de brinquedo (inspiral de ordem dominante mais fusão abrupta; transformada por
gama incompleta em mpmath; `ver_D3_lei_quarto.txt`):
- a razão numérico/previsto tende a 1 (0,993 em ωM = 1e-5) e a fase de 1−T tende a −π/8;
- mesmo no brinquedo a razão cai para 0,86 em ωM = 1e-2 (perto de 10 Hz para A, ωM ≈ 0,02);
- com janela finita, a lei falha para $\omega\tau_w\lesssim10$ (razão 1,57 com τ_w = 1e4, ω = 1e-5). O "cancelamento do início da janela" só vale para $\omega\tau_w\gg1$; isso vale na banda para A, mas o relatório não o diz.

**Literatura.** Elhashash & Nichols (arXiv:2504.18635, eqs. 56–57) calculam a transformada de Fourier analítica da
memória PN da inspiral, termo a termo em ordem PN (índice n), por $U(1,(7-n)/4,z)$. Conferi pelo HTML do arXiv. A
expansão de $U$ para $z$ pequeno dá a lei $f^{1/4}$ e também as correções PN que o relatório deixa como "próximo
experimento 5". O relatório cita só Favata 2009. A expansão explícita e a leitura de identificabilidade não
aparecem no texto (busquei "3/4", "asymptotic", "small f"), mas a matemática, PN incluída, está nesse trabalho.

**A consequência "a forma depende só de $M/(\eta x_*^4)$" não vale na banda.** O próprio relatório mostra
(`exp26_analise.txt`) que $\ln[M^*/(\eta x_*^4)]$ varia 1,68 ao longo do vale, contra 0,066 de $\ln M^*$. O status
"confirmada matematicamente" só cabe à expansão assintótica, não à consequência para identificabilidade.

## V4. L06: R² ≈ 0,5 da série comprimida com ruído **confirmado**

`ver_D3_L06.txt`, mesmos 6000 exemplos, GroupKFold por binária:

| features | ln M | ln M_chirp | ln M_f |
|---|---|---|---|
| MOPED 8 com ruído (CE): HGB / RF / k-NN | 0,50 / 0,51 / 0,47 | 0,50 / 0,52 / 0,50 | 0,48 / 0,49 / 0,46 |
| só a componente de amplitude (ln D) | −0,02 a −0,07 | ~0 | ~0 |
| só a componente ln M | 0,02–0,07 | 0,11–0,15 | ~0,05 |
| componentes ln M + ln D (a razão) | 0,51–0,53 | 0,52–0,54 | 0,50–0,52 |
| SNR verdadeiro (ρ+, ρ×) sem ruído | 0,25–0,29 | 0,37–0,40 | 0,24–0,28 |

O controle com ln M embaralhado entre binárias dá −0,12. O número independe do aprendiz. A informação de massa está
na razão entre a projeção na derivada em ln M e a amplitude (forma), não na amplitude sozinha.

Ressalva que continua de pé: o MOPED usa o $t_0$ verdadeiro, e como a largura do degrau escala com $M$, isso pode
inflar o R². O autor declara essa limitação.

## V5. MOPED fora do fiducial (H07.4, "refutada a degradação"): **parcial**

O "≥ 99,2%" de `exp25_compressao.txt` é retenção dos bits totais, dominados por $t_0$ e pela amplitude. Na
informação intrínseca, a mesma tabela dá:

| binária B | ET: retenção intrínseca | CE: retenção intrínseca |
|---|---|---|
| M=100, q=3, χ=0,5 | 0,53/0,58 = 91% | 1,71/1,80 = 95% |
| M=45, q=1, χ=−0,5 | 0,23/0,24 = 96% | 0,88/0,91 = 97% |

Há degradação de 3–9% na parte que interessa, e o teste usa o mesmo $t_0$. "Refutada a degradação" é forte demais;
"degradação pequena (≤ 9% da informação intrínseca)" seria mais correto.

## V6. Atraso de CM (H07.5): **rótulo numérico errado**; conclusão inalterada

- O relatório escreve "atraso $M_f/2 = 0{,}170$ ms". Mas $M_f/2 = 0{,}9498\cdot65\cdot4{,}9255\times10^{-6}/2 = 0{,}152$ ms.
- O 0,170 ms é $|{\rm CM}/\Delta h_+| = 2{,}7929\times10^{-26}/1{,}6450\times10^{-22}$ s $= 1{,}117\,M_f/2$: o excesso de 11,7% é a parte nula (item 4 da revisão).
- O σ do atraso é a fórmula trivial $1/(2\pi f_{\rm rms}\rho)$: 0,1698 ms (CE) e 0,656 ms (ET), conferidos.
- "1σ em CE" vale para |CM/Δh| (0,170 ms: razão 1,00). Para o $M_f/2$ propriamente dito seria 0,89σ.
- Em nenhum caso há detecção. "Inconclusiva" está bem.
- Observação conceitual, não testada: o sinal usado em todo o L05 é a memória nula calculada pelo fluxo, que não contém atraso nenhum. O Fisher do "atraso" mede a sensibilidade a um parâmetro de desvio, não uma propriedade do sinal modelado.

## Outras afirmações conferidas sem refazer cálculo
- **Frações do cubo:** 72% / 63% recontadas no JSON.
- **Pares do exp07:** os M* reproduzidos (V2) diferem das massas do exp07 (65,0–83,6), como diz o relatório.
- **Prioridade:** a busca no arXiv por "orphan memory", "memory + Fisher + gravitational", "memory + MOPED",
  "memory + mutual information", "memory + Cosmic Explorer + parameter estimation" e "memory + frequency domain +
  inspiral" não achou Fisher, d_ef ou informação mútua da memória **sozinha** nem MOPED aplicado à memória.
  Achou Gasparotto 2023 (LISA, memória com a onda), Rosselló-Sastre et al. 2025 (o modo (2,0) em A#/CE/ET),
  2402.18083 (cosmologia) e Elhashash & Nichols 2025 (acima).
- **Limite da busca:** algumas consultas extras foram recusadas pela API ("Rate exceeded"). A busca é por resumos, não exaustiva.

## Tabela de status após a verificação

| Afirmação | Status do relatório | Veredito |
|---|---|---|
| H05.1/H07.1: 3 direções em CE, d_ef 3,03, λ' 11,8, σ_lnM 0,121 | confirmada numericamente | **confirmado** (pipeline independente, 3 algarismos); bits e I_intr dependem do prior (13–20 bits; 1,2–2,7 bits) |
| H05.7: pares do exp07 indistinguíveis com M livre | confirmada numericamente | **parcial**: confirmado em detector único; numa rede +/× q_B=4 sai (8,3e-4 > 4,3e-4) |
| H05.8: 72% do cubo degenerado em CE, 100% em ET | confirmada numericamente | **parcial**: números corretos para detector único com ψ livre; a degenerescência usa a mistura ψ (canal h×); não testada em rede; ET tratado como detector único |
| H05.5: lei (Mf)^{1/4}, c ∝ η^{-1/4}/x* | confirmada matematicamente | **confirmado** (derivação e teste exato no brinquedo); originalidade enfraquecida por Elhashash & Nichols 2025 (eq. 56–57, Kummer U em cada ordem PN); a consequência "só M/(η x*^4)" é refutada na banda pelo próprio exp26 |
| H06.2: MOPED com ruído em CE, R²(ln M) ≈ 0,5 | refutada em parte | **confirmado** (3 aprendizes; controle nulo −0,12; a informação está na forma, não na amplitude) |
| H07.4: MOPED retém ≥ 99,2% fora do fiducial | degradação refutada | **parcial**: só nos bits totais; intrínseca 91–97% |
| H07.5: atraso de CM M_f/2 = 0,170 ms a 1σ em CE | inconclusiva | **parcial**: M_f/2 = 0,152 ms; 0,170 ms é |CM/Δh| = 1,117 M_f/2; status mantido |
