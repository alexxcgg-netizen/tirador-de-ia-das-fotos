# Etapa 7, parte 1 — Revisão adversarial da etapa 6

Antes de continuar, a etapa 6 (`07_binarias_reais.md`) foi revista sem aceitar nada de antemão.

**Método.** Cinco revisores independentes:
- R1: equações e conceitos;
- R2: reprodução numérica;
- R3: auditoria do código e origem das diferenças entre níveis;
- R4: excentricidade e janelas;
- R5: literatura (cerca de 30 consultas ao arXiv, Crossref e leitura de 20 PDFs).

Cada achado de R1–R4 marcado como "refutado" ou "precisa de correção" passou por um segundo verificador, que refez
as contas sem confiar no primeiro (contraprova). Os achados de R5 não tiveram contraprova. Scripts em `codigo/revisao/` (`rev_R1_*` … `rev_R5_*`,
`rev_*v_*`), saídas em `resultados/revisao/`. Todos os números abaixo vêm desses arquivos.

**Resultado geral.**
- Confirmados:
  - as leis de balanço, as leis de escala, os coeficientes 1PN e a simetria de troca;
  - $C_E=\sqrt{30}/(42\sqrt\pi)$;
  - a reprodução bit a bit dos parâmetros, matches e recuos das tabelas.
- Corrigidos ou refutados: 25 itens (C1–C25, abaixo). Alguns mudam conclusões:
  - os pares "exatos" do 07 são exatos para uma versão idealizada das memórias (só multipolos $m=0$,
    deslocamento total desde $x=0$), não para o que um observador real registra;
  - um interferômetro não mede as quatro memórias;
  - duas janelas deixam uma família aproximada, não a destroem.

A contraprova deu razão ao revisor em todos os itens, exceto nos marcados "parcial" (quatro de R1, um de
R3 e um de R4), em que corrigiu o próprio revisor; a versão final está no texto.

---

## 1. Correções

### Numéricas e de infraestrutura

| # | Afirmação no 07 | Veredito | Versão correta | Evidência |
|---|---|---|---|---|
| C1 | Piso numérico do nível A $\varepsilon_{\rm num}=10^{-10}$; pares coincidem em $10^{-10}$–$10^{-11}$ | refutado | A janela começava no primeiro ponto da grade depois de $f_{\rm low}$, e as memórias formam uma **escada** em $M$: saltos de $2{,}8\times10^{-6}$ no spin a cada amostra perdida. $\varepsilon_{\rm num}\approx3\times10^{-6}$. Com $dt=0{,}125M$ os pares coincidem em $1{,}4$–$2{,}4\times10^{-6}$. A classificação "exata" ($\delta\ll\varepsilon_{\rm mod}$) sobrevive. | rev_R2_piso_numerico |
| C2 | Par (2,+0,5) resolvido em C: "$2\times10^{-7}$, piso do nível C" | corrigido | A saída do exp11 é $1{,}4\times10^{-7}$; o "piso" correto é o da escada (C1). | rev_R2_log_exp11 |
| C3 | "A onda separa os pares a partir de SNR 1–6" | corrigido | Vale para os pares **escolhidos**. A família passa por A: membros com $\lvert q_B-1{,}2\rvert<0{,}008$ não se separam com SNR 66 ($1-\text{match}=1{,}33\,\Delta q^{1{,}95}$). A onda reduz a família a uma vizinhança de largura $\propto1/\rho$, que é a incerteza usual de estimação. | rev_R2_familia_perto |
| C4 | `deteccao.comparar` mede bem a diferença entre ondas | refutado | Há um piso artificial de $\sim2\times10^{-3}$ em $1-$match, por três causas: o início abrupto em 10 Hz, o degrau dos modos $m=0$ no fim da série e a busca no tempo na grade. Os matches da Tabela 3.3 mudam no máximo 0,004 (robustos). A linha $(\chi_s=+0{,}3,\ d=0{,}2)$ do exp13 estava errada: $1-\text{match}=2{,}2\times10^{-4}$ e $\rho_{\rm crit}=47$, não $1{,}2\times10^{-3}$ e 20. Com o tratamento correto, $\rho_{\rm crit}\,d=9{,}0$–$9{,}6$ em todos os $d$. | rev_R2_exp13_match_janela |
| C5 | exp13: memórias $\propto d^{2,0}$ no nível A e $d^{1,0}$ no C | corrigido | A parte **par** em $\chi_a$ escala como $d^{2,00}$ nos dois níveis. A parte **ímpar** (que viola a simetria) é $\propto d$ no nível C ($5{,}5\times10^{-2}d$ em desl40) e também no nível A ($\sim4\times10^{-3}d$ para $\chi_s=+0{,}3$): os modos oscilatórios do substituto também violam a simetria de troca, cerca de 10 vezes menos. O coeficiente $0{,}12\,d^2$ vale para $\chi_s=-0{,}5$; para $+0{,}3$ é $0{,}18\,d^2$. | rev_R2_exp13_expoentes |
| C6 | SNR da memória de A: 0,76 / 1,44 / 10,7 / 39 (aLIGO / A+ / ET / CE) | corrigido | O exp15 usava os modos $m=0$ completos de RN, que têm toque quase normal de 100–300 Hz que não é memória. A memória **nula** (pelo fluxo) tem SNR **0,47 / 0,89 / 8,6 / 34**. A razão memória/onda cai para $\sim7\times10^{-3}$ no aLIGO. Em ET/CE, a SNR depende ~20% de $f_{\min}$ (10 contra 20 Hz). | rev_R5_snr_memoria_qnm, rev_R2_exp15_robustez |

### Definições e teoria

| # | Afirmação no 07 | Veredito | Versão correta | Evidência |
|---|---|---|---|---|
| C7 | §1.2: os multipolos $m\neq0$ são "só termo de borda" e por isso só os $m=0$ entram | refutado | A borda **final** é física, fixada pela fusão. No observador ela muda o spin em ±1,4%, a giroscópica e o CM em ±0,5%, conforme o azimute $\phi$. O par (2,0) do exp07 difere até $3{,}1\times10^{-2}$ com todos os $m$. | rev_R1_m_nao_nulo |
| C8 | §1.3: usar o deslocamento total "não altera a lógica" | corrigido | 10% do deslocamento de A acumula antes de 10 Hz, fora da banda. No deslocamento **de janela** (o observável), os pares do exp07 diferem de $2{,}6\times10^{-3}$ a $3{,}6\times10^{-2}$. | rev_R1_janela_desl |
| C9 | Rótulo da memória de CM "$\int h_+du$" | corrigido | O código calcula o $\Delta\mathcal K$ de [Nichols2018], eq. 3.11: $\int(\Phi-\Phi^{(n)})du-[u(\Phi-\Phi^{(n)})]$. A integral bruta de $h_+$ diverge. No observador, CM ≈ $-(M_f/2)\Delta h_+$ (parte ordinária $\ell=2$, 88%) mais 11% de parte nula, o que equivale a um **atraso de $M_f/2$** do degrau da deformação em relação ao degrau previsto pelo fluxo. Além disso, `binarias.py` usa na parte ordinária o deslocamento total e na nula só a janela: de 11% ($q=1$) a 42% ($q=8$) de cm20 vem de antes da janela. | rev_R1_jacobiano, rev_R3_cm_convencoes |
| C10 | §2.2: um observador mede 4 números | corrigido | Um interferômetro mede $F_+h_++F_\times h_\times$ na banda, com $F_+$ e $F_\times$ desconhecidos. **A giroscópica não é mensurável** (é a rotação de um giroscópio, $\sim3\times10^{-41}$ rad). **O CM é degenerado com o instante de chegada** $t_0$. Da memória de spin, só 11–29% do valor DC está em 10–50 Hz, e a SNR em $h_\times$ é 8–11 vezes menor que em $h_+$. Na prática há no máximo ~2 números integrados, ou melhor, uma forma de onda de memória na banda. As incógnitas sobem para ≥ 11 (céu, $\psi$, $t_0$, $\phi$). | rev_R1_detector |
| C11 | Separar os pares só pela memória exige SNR de memória de 20 a 300 | refutado (parcial) | A memória **resolvida no tempo** separa os pares (2,0), (3,0) e (2,+0,5), par a par, com $\rho_{\rm mem}(+)\approx3$–14, e o par (1,0) com 29–41. CE separa os três primeiros e fica no limite no quarto; aLIGO não separa nenhum. Na versão de **duas janelas** o 07 era otimista: as diferenças estão no spin ($h_\times$) e na giroscópica (não mensurável), e exigem $\rho_+\sim2\times10^{2}$–$3\times10^{3}$. A ambiguidade da memória órfã (minimizando sobre a família) ficou **em aberto**. | rev_R1_detector, rev_R1v_detector |
| C12 | §2.3: a simetria $(\eta,D)\to(\lambda\eta,\lambda D)$ preserva o CM | corrigido | O CM só é preservado se a parte ordinária usar $M$. Com $M_f$ (escolha do código, termo de ordem $h^4$) ele quebra $5\times10^{-3}$ já na ordem dominante; a §3.4 do 07 contradizia a §2.3. Os resíduos LO do exp08 ($10^{-4}$) são numéricos. Como a giroscópica não é mensurável, **na ordem dominante a razão de massas é exatamente degenerada com todas as memórias mensuráveis**. | rev_R1_pn_quadratura |
| C13 | §2.2: posto 4 (suposto) | complementado (parcial) | O posto 4 foi verificado em A ($\iota=50°$; valores singulares 4,40; 1,67; 0,61; 0,116). Ele cai para 3 em $\iota=\pi/2$ (spin e giroscópica se anulam) e para 1 em $\iota=0$ (deslocamento, spin e CM $\propto\sin^2\iota$). Com $D$ e $\iota$ fixos há uma direção intrínseca quase nula (valor singular $6{,}6\times10^{-4}$, sobretudo $q$). Perto dos zeros, $\delta$ deve usar uma escala fixa. | rev_R1_jacobiano, rev_R1v_observador |
| C14 | §2.1: "igualar $\lvert\tilde h\rvert$ força $\lambda'=\lambda$" [D, analítico] | corrigido (parcial) | O argumento era heurístico. Ver a prova pelos harmônicos logo abaixo da tabela. A simetria PN não é um filtro de fase: multiplica $\lvert\tilde h\rvert^2$ por $1/\lambda$. A §3.2 testa filtros só indiretamente. | rev_R1_analitico A5, rev_R1v_analitico |
| C15 | §2.4: o recuo entra nos $m=0$ só em $O(v^2)$ (argumento de simetria) | corrigido | A lógica não vale: os $m=0$ dependem de $\lvert v\rvert$ em primeira ordem, através de $\lambda$. A conclusão "um observador não fixa o recuo" vale pela **família** (recuos de 18 a 227 km/s com as mesmas memórias). Além disso, [MW2019] eq. 101 mostra que a memória de boost é par em $V$ em todo multipolo. | R1, R5 |
| C16 | §2.6: $P$ e $Q$ resolvidos no tempo determinam $h$; $C=5{,}0397$ | corrigido | A proposição exige suporte **conexo**: dois surtos disjuntos têm $P$ e $Q$ iguais (resíduo $2\times10^{-14}$) e formas de onda diferentes. Com a simetria de reflexão, a fase global se reduz a um sinal. $C=2C_E/C_J=40\sqrt7/21=5{,}03953$, com $C_J=\sqrt{210}/(280\sqrt\pi)$. O valor 5,0397 era a calibração numérica, enviesada em $3\times10^{-5}$ pela fase acumulada por soma. | rev_R1_analitico A1, A7 |
| C17 | Duas janelas "eliminam a família"; "forma mais robusta" | corrigido | O jacobiano 8×6 tem posto 6, mas o menor valor singular é $\sim9\times10^{-4}$ (o $2{,}5\times10^{-3}$ de R1 era ruído do passo). As diferenças de deslocamento total e de CM entre janelas são $\sim10^{-3}$: só spin e giroscópica mudam (×0,69 e ×0,68 de 10 para 20 Hz). Resolvendo de novo com as 8 equações sobra uma família **aproximada**, com resíduo de $4\times10^{-5}$ a $2\times10^{-3}$ para $q_B$ de 1,1 a 3. Classificação: aproximada, não destruída. | rev_R4_janelas*, rev_R1v_observador |
| C18 | Nível C = memória completa de RN, "vale até $10^{-3}$" | refutado | Spin e giroscópica do nível C têm erro de 5–12% na taxa na parte **híbrida PN** do substituto: ali o (3,0) é PN de ordem dominante, e o nível A é mais confiável. Com a janela começando dentro da parte de RN, $\lvert A-C\rvert$ do spin em $q=8$ cai de 6,7% para 0,7%. Outros pontos: giro30 A−C = 1,45–1,52 × spin30 A−C (cancelamento entre os termos de spin e helicidade); o giro10 é robusto; os modos (3,1) e (4,2), que faltam, dão +0,5% a +1,0%; a parte ordinária do spin é ≤ $10^{-3}$. No deslocamento, o excesso de C (4,8–7,9% do incremento) está na inspiral de RN, e não na hibridização PN: o [H] do 07 §3.6 vale para o (3,0), não para o (2,0). | rev_R3_origem_AC, rev_R3_taxa_pares, rev_R3_ordinaria |
| C19 | Termo de Favata antes da janela; $M_f$ | corrigido (pequeno) | A `favata_h20` não tem termos de spin (até 0,2% do deslocamento total com $\chi=0{,}6$). Falta o termo 2PN em $M_f$ ($\le5\times10^{-5}$). | rev_R3_cm_convencoes |
| C20 | `pn_excentrico` "suave e preciso" depois da correção | corrigido (pequeno) | É suave, mas converge só em primeira ordem em $dt$: o peso da ponta, onde o fluxo é máximo, fica na separatriz. O erro, $\sim5\times10^{-4}$, quase se cancela entre A e B; as conclusões do exp10 e exp10b não mudam. | rev_R3_pn_dt, rev_R3_pn_borda |

**Prova pelos harmônicos (C14).** Na fase estacionária, $\Psi_{\ell m}(f)=\tfrac m2\Psi_{22}(2f/m)+$ const.
Um filtro comum que leve binária em binária exige $\delta(f)=\tfrac m2\delta(2f/m)+c_m$ para todo $m$
presente. A solução geral é $f\,p(\ln f)$, com $p$ periódica de período $\ln(m/2)$. Com $m=2,3,4$, os
períodos $\ln2$ e $\ln1{,}5$ são incomensuráveis, e só sobra translação no tempo mais fase global. Com
só $m=2$ e 4 ($q=1$, sem spins) sobram filtros log-periódicos, e é preciso o argumento de amplitude.

### Excentricidade

| # | Afirmação no 07 | Veredito | Versão correta | Evidência |
|---|---|---|---|---|
| C21 | Piso do SEOBNRv5EHM $\sim10^{-5}$, incluindo "diferenças entre execuções" | corrigido | O modelo é **determinístico**. O piso é a falta de suavidade da saída: mudar $M$ em $10^{-12}$ já altera as memórias em $\sim5\times10^{-6}$. A origem não é a grade de saída nem a tolerância do integrador. Por componente, $2\times10^{-5}$–$10^{-4}$. | rev_R4_ruido_pares, rev_R4_tremor_dt, rev_R3_excentricas |
| C22 | Tabela 3.5: pares com $q_B=1{,}2$ e 1 em $5\times10^{-5}$–$5\times10^{-4}$ | corrigido (parcial) | Eram soluções mal convergidas: diff_step $10^{-3}$, pequeno diante do tremor, e um cache com chaves arredondadas. Ver os novos pares logo abaixo da tabela. | rev_R4v_resolver, rev_R4_resolver_l0 |
| C23 | Falta do (2,0) oscilatório no SEOBNRv5EHM "desprezível" | corrigido (parcial) | Muda desl., CM e $E$ em $\sim5\times10^{-6}$, $2\times10^{-5}$ e $5\times10^{-5}$ para $e_0=0{,}1$, 0,2 e 0,3; spin e giroscópica não mudam. Não é desprezível diante dos resíduos de $\sim7\times10^{-6}$. O $M_f$ de B usa a energia de ligação circular (erro de $5\times10^{-6}$ a $5\times10^{-5}$). | rev_R3v, rev_R3_excentricas |
| C24 | Pares com anomalia $\ell_0=0$ "exatos"; tabela de efeito de $e_0$ | complementado | Ver a seção sobre a anomalia logo abaixo da tabela. | rev_R4_anomalia* |
| C25 | Janela das excêntricas "desde 10 Hz", como o corte de um detector | corrigido | 10 Hz é a frequência de onda **média** (orbital média de 5 Hz). Na primeira órbita, a frequência instantânea vai de 6,6 a 17 Hz: a janela não equivale a um corte em frequência. $e_0=0{,}3$ está dentro do domínio do modelo (sem avisos; os avisos começam em $e_0=0{,}6$). | rev_R4_freq_inicial, rev_R4_dominio |

**Novos pares excêntricos (C22).** Resolvidos de novo com jacobiano de passos grandes:

| $e_0$ | $q_B$ | $\delta$ | $\chi_1$ | $M$ | $\iota$ | $D$ (Mpc) |
|---|---|---|---|---|---|---|
| 0,1 | 1,2 | $6{,}8\times10^{-6}$ | 0,383 | 65,147 | 48,97° | 403,2 |
| 0,2 | 1,2 | $1{,}8\times10^{-5}$ | 0,562 | 65,933 | 46,10° | 413,4 |
| 0,2 | 1 | $7{,}8\times10^{-6}$ | 0,665 | 65,594 | 44,00° | 421,5 |

Todos ficam no piso do modelo; os matches desses novos pontos não foram recalculados. Com $e_0=0{,}3$ e
$q_B=1{,}2$ continua sem solução com $\chi_1\le0{,}8$: o melhor fica em $8{,}6\times10^{-3}$, e
$4\times10^{-3}$ com $\ell_0$ livre. O "resíduo" gravado no `exp12_pares.json` subestima $\delta$, por
causa do cache.

**Anomalia $\ell_0$ (C24).**
- Com os outros parâmetros fixos, $\ell_0$ muda as memórias em até $1{,}9\times10^{-2}$. Resolvendo de
  novo para cada $\ell_0$, a coincidência volta a $7\times10^{-7}$–$4\times10^{-6}$. A família
  excêntrica tem **dimensão 4** (posto 4 em 8 parâmetros).
- O efeito vem dos últimos ~500 M antes do pico: a excentricidade residual modula a energia irradiada.
- O sinal da variação do deslocamento com $e_0$ depende de $\ell_0$: para $e_0=0{,}3$, de −1,2% a +1,1%.
  Só a redução do spin é robusta: de −5,0% a −6,9%.

---

## 2. Literatura: o que já era conhecido (R5)

**Afirmações [D] do 07 que são [E] ou corolários imediatos:**

| Seção do 07 | O que diz | Onde já está |
|---|---|---|
| §1.3 | acúmulo $\propto x^{-1/2}$ e memória de janela | [Nichols2017]; [FS2025] eq. 44 |
| §1.2 | termos $m\neq0$ de borda | [Nichols2018] eqs. 4.21–4.22 |
| §2.3 | escalas $\eta M/D$, $\eta M^2/D$, $\eta M^2/D^2$ | [Favata2009b], [Nichols2017], [FS2025] |
| §2.4 | recuo | [Favata2009c] e [MW2019] eq. 101 |
| §2.5 | cegueira a $\chi_a$ | corolário da simetria de troca: [Varma2019], [Yoo2023], [Arun2009] |
| exp13 | usar uma restrição exata da RG para medir o erro de um modelo | [ADK2020]; [DGH2025] |
| §2.1 | relação amplitude–fase na fase estacionária | [CF1994]; a conclusão sobre filtros é elementar e não foi encontrada enunciada |

**A degenerescência da memória sozinha é conhecida qualitativamente:**
- [McNeill2017]: "all orphan memory looks the same: like a step function"; o título publicado é
  "Detecting Gravitational Wave Memory without Parent Signals";
- [ET2020]: "only the overall amplitude of the signal changes";
- [TGvH2026]: degenerescência massa–distância em PTA;
- [DTLW2020].

**Linhas da etapa 7 já antecipadas:**

| Linha | Trabalhos anteriores | Situação |
|---|---|---|
| L09 (memória no *ringdown*, frequências-diferença) | [EN2025b] eq. 3.29; [Shi2026]; [Bourg2026] | publicada |
| L13 (núcleo $\ell<2$) | [MW2019] eq. 100 | conhecido |
| L12 | [MW2019] eqs. 103–105 limitam a memória **ordinária** de boost pela lei da área | parcial: a memória nula fica em aberto |
| L17 (raios de estrelas de nêutrons pela memória) | [Kennefick1994]; [LTE2024] | conhecida |
| L03, ordem dominante | [Favata2009b], nota 4 | conhecida |
| L10, existência da memória $m\neq0$ | [Talbot2018]; [RH2025] | conhecida |

**Mensurabilidade:**
- spin e CM só dariam evidência numa população, com dois CE e cerca de 1 ano [SGN2026];
- a giroscópica é inobservável na prática [SO2023; FS2025];
- o GWTC-3 não detecta memória [Cheung2024], e seriam precisos ~2000 eventos.

**Lacunas que parecem abertas** (não encontradas):
- análise explícita de identificabilidade (posto, fibras) do mapa parâmetros → memórias;
- memórias em várias janelas e "espectroscopia de energia de ligação" além da ordem dominante;
- Fisher, Cramér-Rao e informação mútua quantitativos da memória sozinha resolvida no tempo;
- desigualdade para a memória **nula** pela energia irradiada e pela lei da área;
- recuperação de fase a partir dos modos de memória (elementar);
- identificabilidade dos spins no plano pelos multipolos $m\neq0$;
- estabilidade dos momentos contra as janelas;
- MOPED, subespaços ativos e informação mútua aplicados à memória;
- a memória de CM como observável de $M_f$ (a relação é conhecida, o uso não).

---

## 3. O que muda nas conclusões da etapa 6

| Conclusão do 07 | Depois da revisão |
|---|---|
| A família infinita (filtros de fase) não contém binárias da RG | **Mantida**, com prova melhor (harmônicos $m=2,3,4$ na fase estacionária). Exceção: $q=1$ sem spins, onde sobram filtros log-periódicos e vale o argumento de amplitude. |
| Num observador há famílias exatas de binárias com as mesmas 4 memórias | **Mantida para as 4 memórias teóricas na versão do 07** (multipolos $m=0$, deslocamento total). Com o deslocamento de janela e os $m\neq0$, os pares do exp07 deixam de coincidir (até 3%). A contagem garante que as famílias continuam existindo, mas é preciso resolvê-las de novo (etapa 7, D1). |
| A família é robusta aos níveis A, B e C | **Mantida**, com a ressalva de que o nível C não é o padrão-ouro para spin e giroscópica na parte PN. |
| Pares excêntricos idênticos | **Mantida e ampliada**: exatos no piso do modelo também para $q_B=1$ e 1,2 com $e_0\le0{,}2$; $\ell_0$ é mais uma dimensão da família (total 4). |
| As ondas completas separam os pares (SNR 1–6) | **Corrigida**: vale para pares escolhidos; a família passa por A, e a onda reduz a ambiguidade à incerteza usual de estimação de parâmetros ($\Delta q\approx0{,}008$ com SNR 66). |
| Duas janelas quebram a família | **Rebaixada** a "deixam uma família aproximada" ($4\times10^{-5}$–$2\times10^{-3}$). |
| Separar pela memória exige SNR de memória de 20 a 300 | **Refutada nos dois sentidos**: a memória resolvida no tempo separa os pares do exp07 com 3–14 (29–41 para $q_B=1$); duas janelas exigiriam $10^2$–$10^3$. |
| Um observador mede 4 memórias | **Refutada como afirmação operacional**: a giroscópica não é mensurável por interferômetros e o CM se confunde com $t_0$. A pergunta científica passa a ser o conteúdo de informação da **forma de onda da memória na banda** (etapa 7, D3). |

**Observação metodológica.** Três defeitos numéricos (a escada de discretização, o piso artificial do
match e um otimizador travado diante do tremor do modelo) produziam números falsamente precisos ou
falsamente positivos. A etapa 7 usa um módulo novo, `codigo/observaveis.py`, com janela de início
exato, memórias suaves nos parâmetros, CM consistente, multipolos $m\neq0$, séries de memória nula e
match corrigido. Ele foi testado e verificado antes das linhas de pesquisa (`linhas/L00_*`).
