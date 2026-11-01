# Verificação adversarial da linha D4 (L12–L15): limites, canais e momentos

Verificador independente. O relatório original (`linhas/L12_a_L15_limites_canais_momentos.md`) não foi editado, e nenhum
script dele foi re-executado de forma a regravar `resultados/`. As checagens novas estão em `codigo/revisao/ver_D4_*.py`.
Todas rodaram de `codigo/` com `OMP_NUM_THREADS=1`, num processo só, e cada uma levou menos de 2 min. Os números abaixo
foram impressos por esses scripts (indico qual) ou lidos dos arquivos de D4 (cito o arquivo).

Rótulos: [E] estabelecido, [D] derivado aqui, [H] hipótese.

## Resumo do veredito

| # | Afirmação de D4 | Veredito |
|---|---|---|
| 1 | Thorne = fórmula de modos do projeto; $\|D\Delta h\|\le 4E$, com 4 ótimo | **confirmado** |
| 2 | $c_L$ como autovalor de Gram; $c_2=\sqrt{30}/6$; tabela de $c_L$; $4-c_L\approx8{,}9/L$ | **confirmado** (implementação independente, até $L=256$) |
| 3 | $c(e_2)$ pelo dual do S-lema (1,20; 1,55; 1,80) | **confirmado**, com precisão: a exatidão vem da realizabilidade de qualquer $B\succeq0$ (é um SDP) e não precisa do S-lema; achei a lei $c(1-\varepsilon)\approx c_2+2{,}94\sqrt\varepsilon$ |
| 4 | Folga nas binárias ($r$ = 0,63–0,83 de lado; 31–65% de $c(e_2)$; 16–21% de 4) | **confirmado** pela integral de Thorne direta (3 sistemas, diferença ≤ 1e-5) |
| 5 | $\lambda_\ell(\beta)/\lambda_\ell(1)\to c_\ell\beta^\ell$, $c_\ell$ = 4/5, 4/7, 8/21, 8/33 ("forma fechada não demonstrada") | **confirmado e fechado aqui**: $c_\ell=2^{\ell-1}\ell!(\ell+2)!/(2\ell+1)!$. O valor de $\ell=8$ na tabela do exp29 está errado (0,0421 contra o exato 0,0527) |
| 6 | Cota $E_x\ge D\|\delta h\|/4$ para qualquer $\beta$ | **confirmado** (a energia inclui a de repouso) |
| 7 | L14: "janelas retêm mais informação de Fisher que momentos" (H14.2), "os momentos dependem do início, as janelas não" (H14.3) e a moral "a base boa são as janelas adaptadas" | **refutado na forma enunciada**. Momentos tomados na variável adaptada $c(t)$ (fração acumulada) retêm *mais* que as janelas de energia igual (94–97% contra 54–82% com $K=12$) e não dependem do início. O que conta é a variável adaptada ao fluxo, não a escolha entre janelas e momentos |
| 8 | L15, H15.3: "dois espectros com momentos 0, 1, 2 iguais dão memórias 1,6% diferentes", logo a redução a $(B,A)$ falha | **conclusão confirmada, exemplo inadequado**. O par de D4 não casa o análogo de $A$ ($\int S/\omega$ difere 0,7%). Com $\int S$ e $\int S/\omega$ casados, a memória difere 0,6–9,4%. Com $\int S$, $\int S/\omega$, $\langle\omega\rangle$ e $\langle\omega^2\rangle$ casados, a diferença cai para ~1e-4 |

Ressalvas menores estão no §9. A busca bibliográfica (§8) não achou $c_L$, $c(e_2)$, a cota da memória nula pela lei da
área nem a forma fechada de $c_\ell$. Isso é compatível com a declaração de D4 de não alegar originalidade.

---

## 1. Fórmula de Thorne, $|K|\le1$ e a cota $4E$ (H12.1)

**Derivação refeita [D].** Para $\bar m=(e_\theta-ie_\phi)/\sqrt2$, vale $|n'\cdot\bar m|^2=\tfrac12|n'_\perp|^2=\tfrac12(1-x^2)$,
com $x=n'\cdot N$. Logo $|K|=\tfrac12(1-x^2)/(1-x)=(1+x)/2\le1$. Como $F\ge0$, segue $|D\Delta h|\le4E$. O valor 4 só é
atingido quando $x\to1$: é um supremo, não um máximo.

**Normalização e sinal.** Para a binária quadrupolar de ordem dominante, D4 obtém $D\Delta h/E=\sin^2\iota(17+\cos^2\iota)/24$
(`resultados/exp28_constantes.txt` (c)). Conferi isso de forma independente contra Favata 2009 [E]:
- $h_+^{\rm mem}=\frac{\eta Mx}{48R}\sin^2\Theta(17+\cos^2\Theta)$;
- $E_{\rm rad}=\eta Mx/2$ (energia de ligação newtoniana);
- a razão dá exatamente $\sin^2(17+\cos^2)/24$, com sinal positivo.

Assim, sinal e normalização coincidem com a literatura, e não só com `memorias.py`.

**Conferência numérica independente** (`ver_D4_folga.py`). Calculei a integral de Thorne direta numa grade 400×400, sem
`memorias.py`, com $B$ de janela das binárias reais. Ela reproduz o $r$ de D4 a ≤ 1e-5 relativo:

| Sistema | $r$ (aqui) | $r$ (D4) | $e_2$ |
|---|---|---|---|
| $q=1$ | 0,77328 | 0,77327 | 0,9888 |
| $q=4$ | 0,67405 | 0,67404 | 0,8816 |
| A | 0,77689 | 0,77688 | 0,9839 |

**Status: confirmado.**

## 2. Constantes $c_L$ (H12.2)

**Implementação independente** (`ver_D4_constantes.py`). Os harmônicos com peso de spin vêm das matrizes $d$ de Wigner
pela forma de Jacobi (`scipy.special.eval_jacobi`, binomiais em log-gama). Não usei `harmonicos.py` nem `spherical`. Usei
o método 1D com Gauss–Legendre em $\theta$. O erro de normalização dos harmônicos é ≤ 1,4e-12 até $L=256$.

| $L$ | 2 | 3 | 5 | 8 | 16 | 32 | 64 | 128 | 192 | 256 |
|---|---|---|---|---|---|---|---|---|---|---|
| $c_L$ (aqui) | 0,9128709292 | 1,8516605417 | 2,5108013487 | 3,0056805851 | 3,4754160905 | 3,7304733816 | 3,8632764935 | 3,9311211961 | 3,9539625981 | 3,9654270972 |
| diferença para D4 | 2,5e-11 | 3,3e-11 | 2,6e-11 | 2,2e-11 | 1,9e-11 | 1,5e-11 | 4,2e-11 | 1,9e-11 | — | — |

**Assintótica.** $L(4-c_L)$ vale 8,816 ($L=128$), 8,839 (192) e 8,851 (256). O expoente local entre 192 e 256 é −0,9955.
A extrapolação $a+b/L+c/L^2$ dá $a=8{,}886$, e a de dois pontos dá 8,885. **"$4-c_L\approx8{,}9/L$" se confirma.** A
estimativa $a\approx8{,}88$ de D4 estava certa nos dois primeiros algarismos. Isso continua sendo resultado numérico, não
demonstração.

**Explicação heurística do $1/L$ [D, argumento].** Um feixe de largura $\sim1/L$ a um ângulo $\theta_0$ do observador
tem dois custos:
- o fator $(1+\cos\theta_0)/2$ custa $\sim\theta_0^2/4$;
- a fase $e^{-2i\phi'}$ varia $\sim1/(L\theta_0)$ através do feixe, e isso custa $\sim1/(L\theta_0)^2$.

O ótimo fica em $\theta_0\sim L^{-1/2}$, com custo total $\sim1/L$. Isso concorda com o expoente −1.

**$c_2$ refeito à mão.** O Γ de $\ell=2$ (`exp28_c2_exato.txt`) é formado por duas cadeias:
- $-2\to0\to2$, com elementos $g_1=\sqrt6/(48\pi)$ e $g_2=\sqrt6/(24\pi)$;
- $-1\to1$, com $g_3=1/(12\pi)$.

Os autovalores de $16\pi\,\mathrm{Herm}$ são $\pm16\pi\cdot\tfrac12\sqrt{g_1^2+g_2^2}=\pm\sqrt{30}/6$ e $\pm2/3$, o que confere com o sympy.
Os autovalores pelos harmônicos de Wigner-d são os mesmos.

**Sanidade.** Testei 20 000 matrizes $B\succeq0$ aleatórias, de posto 1 a 3, com $L=6$. Nenhuma passa de $c_6$ (o máximo
foi 0,914; matrizes aleatórias ficam longe do ótimo), e o autovetor ótimo atinge $c_6$ a 1e-10.

**A redução $\sup|{\rm tr}(BX)|=16\pi\lambda_{\max}(\mathrm{Herm}X)$ está correta.** O supremo é o raio numérico de $X$.
Ele é igual a $\lambda_{\max}(\mathrm{Herm}\,e^{i\alpha}X)$ para todo $\alpha$, porque uma rotação em torno de $N$
multiplica $\Delta h(N)$ por $e^{2i\alpha}$ e preserva $\ell\le L$. D4 conferiu que a variação com $\alpha$ fica ≤ 6e-15.

**Status: confirmado (caracterização e $c_2$, analíticos; assintótica, numérica).**

## 3. Limite com energia dividida $c(e_2)$ (H12.2b)

**Primal independente do dual** (`ver_D4_constantes.py` (4)). Fiz subida alternada sobre $v=(\sqrt{e_2}\,u,\sqrt{1-e_2}\,w)$
com 60 partidas aleatórias. O primal de posto 1 coincide com o dual de D4:

| $e_2$ | dual | primal | gap |
|---|---|---|---|
| 0,99 | 1,204892 | 1,204892 | 1,3e-8 |
| 0,95 | 1,552398 | 1,552398 | 2e-14 |
| 0,90 | 1,795829 | 1,795829 | 1,1e-10 |
| 0,8386 | 2,001822 | 2,001822 | 1,1e-10 |
| 0,5 | 2,488409 | 2,488405 | 4,5e-6 |

Os valores tabelados por D4 para os sistemas ($e_2$ com mais algarismos) conferem.

**Precisão conceitual.**
- Não é preciso invocar o S-lema. Como qualquer $B\succeq0$ é realizável (surtos disjuntos), o problema *físico* já é o
  SDP $\max{\rm tr}(HB)$ com ${\rm tr}B=1$ e ${\rm tr}P_2B=e_2$. A dualidade forte vale por Slater, e o primal de posto 1
  só mostra que um único surto basta.
- **Lei nova [D, numérica].** Medi $(c-c_2)/\sqrt\varepsilon$ = 2,920, 2,939 e 2,943 para $\varepsilon$ = 1e-2, 1e-3 e
  1e-4. Logo $c(1-\varepsilon)\approx c_2+2{,}94\sqrt\varepsilon$. O crescimento com a raiz explica a frase de D4 de que
  "1% de energia fora de $\ell=2$ sobe a constante de 0,91 para 1,20": o efeito é linear na *amplitude* fora de $\ell=2$,
  pelo termo cruzado.

**Status: confirmado.**

## 4. Folga nas binárias e o teste da lei da área (H12.3, H12.4)

Conferi as razões de `resultados/exp28_folga.txt` linha a linha:
- $r/c(e_2)$ de lado: 0,314–0,645;
- $r/4$: 0,157–0,207;
- $E_{\rm jan}/E_{\rm área}$: 0,077–0,230 (0,081–0,341 com $\chi_f$);
- $|D\Delta h|/(4E_{\rm área})$ de lado: 0,0128–0,0474;
- $|D\Delta h|/(c(e_2)E^\chi_{\rm área})$: 0,029–0,220 de lado e 0,017–0,136 em 50°.

Os números do relatório estão certos, mas há um problema de redação:
- **"1,3–22% do limite"** (resumo de D4) junta dois limites diferentes, (4, só a área) e ($c(e_2)$, $\chi_f$). Cada um tem
  sua faixa: 1,3–4,7% e 2,9–22% de lado.
- **"4,5 a 77 vezes"** vem de $1/0{,}220$ e $1/0{,}0128$. O valor exato do segundo é 78. A afirmação só vale de lado; em
  inclinações menores a folga é maior.

O valor central $r$ foi reproduzido de forma independente (§1). A refutação de H12.4 (o teste da lei da área não é útil)
**se mantém**: com folga ≥ 4,5, nenhuma violação plausível da lei da área seria vista antes que o teste de consistência
com o fluxo (sensível a ~3% com SNR 34) a visse.

**Status: confirmado.**

## 5. Canais e velocidade: $\lambda_\ell(\beta)$ e a cota $E_x\ge D|\delta h|/4$ (H13.1, H13.4, H12.5)

**Forma fechada [D, demonstrada aqui].** Com $F=Y_{\ell2}$ no referencial de $N$:

$$\lambda_\ell(\beta)\propto\int_{-1}^1P_\ell^2(x)\frac{\beta^2(1-x^2)}{2(1-\beta x)}dx
=\sum_k\frac{\beta^{k+2}}2\int P_\ell^2(1-x^2)x^k\,dx .$$

Como $(1-x^2)x^k$ está no espaço gerado por $\{P_n^2\}_{n\le k+2}$ e os $P_n^2$ são ortogonais, o primeiro termo não nulo é
$k=\ell-2$. Daí:

$$\frac{\lambda_\ell(\beta)}{\lambda_\ell(1)}\to c_\ell\beta^\ell,\qquad
c_\ell=\frac{\int(1-x^2)x^{\ell-2}P_\ell^2}{\int(1+x)P_\ell^2}=\frac{2^{\ell-1}\,\ell!\,(\ell+2)!}{(2\ell+1)!}=\frac{(\ell+2)!}{2\,(2\ell+1)!!}.$$

- O sympy confere para $\ell$ = 2..10: 4/5, 4/7, 8/21, 8/33, 64/429, 64/715, 128/2431, 128/4199, 512/29393.
- A razão de recorrência é $c_{\ell+1}/c_\ell=(\ell+3)/(2\ell+3)$.
- O mpmath com 60 algarismos em $\beta=10^{-3}$ concorda até $O(\beta^2)$ (`ver_D4_canais.py` (1)).
- Os quatro valores citados por D4 estão certos, e a "forma fechada não demonstrada" agora está demonstrada.

**Erro na tabela de D4.** `resultados/exp29_canais.txt` dá, para $\ell=8$ em $\beta=0{,}01$, o valor 0,0421; o exato é
0,0527. A causa é o `quad` em precisão dupla: a integral vale ~1e-16 do integrando e fica abaixo do arredondamento e do
`epsabs`. Os valores de $\ell=6,7$ ainda estão certos. O relatório não usa $\ell=8$, então a conclusão não muda. A
entrada $\ell=8$, $\beta=0{,}01$ (e $\ell\ge8$ em $\beta$ pequeno, em geral) não é confiável.

**Cota $|K_\beta|\le|K_1|\le1$.**
- **Analítica:** $\partial_\beta[\beta^2/(1-\beta x)]=\beta(2-\beta x)/(1-\beta x)^2>0$.
- **Numérica**, numa grade de 2001×2001: $\max(|K_\beta|-(1+x)/2)=3\times10^{-15}$ e a derivada em $\beta$ é ≥ 0.
- **Confirmado**, com uma ressalva que o relatório deixa implícita: a energia $E_x$ da cota inclui a energia de repouso
  das partículas massivas. Para matéria lenta, a cota é muito fraca.

**Núcleo $\ell=0,1$ para todo $\beta$.** O argumento de equivariância está correto: não há harmônicos de peso −2 com
$\ell<2$. Não refiz a parte numérica, que dá ≤ 2e-15 por construção.

**Exemplo G × N (H13.2).** A igualdade a 1,3e-14 é **tautológica por construção**. Os neutrinos têm a mesma forma angular
das ondas mais um dipolo, então a fluência total em $\ell\ge2$ é idêntica por linearidade, e 1e-14 é só arredondamento.
O exemplo ilustra a degenerescência, mas não a testa. A afirmação continua correta.

## 6. L14: momentos × janelas (H14.1–H14.4)

**Hipótese rival testada** (`ver_D4_momentos.py`). No modelo 2 de D4 (ruído branco comum em $F$), a informação retida
depende só do espaço das linhas:
- momentos em $\tau=t/T$ geram polinômios em $t$, que não resolvem os últimos ~10 ms;
- janelas de energia igual usam o fluxo nominal para pôr os cortes na fusão.

A comparação justa usa **momentos na mesma variável adaptada**: $\mu_n=\int c(t)^nF\,dt$, com $c(t)$ a fração acumulada
nominal da memória (a mesma informação que define os cortes de energia igual).

Fração retida $\sigma_{\rm série}/\sigma_K$ para (ln A, ln M, q, χ1, χ2, t0). Reproduzi os números de D4 para "momentos em
$t$" e "janelas de energia igual" exatamente:

| $K$ | momentos em $t$ (D4) | janelas de energia igual (D4) | **momentos em $c(t)$** | momentos em $\ln(t_c-t)$ |
|---|---|---|---|---|
| 6 | 1e-5 a 1e-4 | 0,18–0,43 | 0,04–0,37 | 2e-4 a 2e-3 |
| 12 | 4e-4 a 3e-3 | 0,54–0,82 | **0,94–0,97** | 6e-4 a 4e-3 |
| 32 | 8e-4 a 6e-3 | 0,72–0,97 | **0,997–1,000** | 0,02–0,23 |
| 64 | 7e-3 a 5,5e-2 | 0,93–0,99 | **0,999–1,000** | 0,25–0,69 |

**Sensibilidade ao início** da janela (−4 s → −3 s), $n$ = 1–9:
- momentos em $t$ com origem na fusão: 21–92% (reproduz D4);
- **momentos em $c(t)$: 7e-5 a 0**;
- momentos em $1-c(t)$: 1,7–8%.

**Condicionamento.** Os monômios em $c(t)$ continuam exponencialmente mal condicionados (cond 8e7 em $K=12$). A base de
Legendre em $c$ resolve o condicionamento e preserva a informação.

**Consequências.**
- **H14.1** (condição dos monômios exponencial, das janelas polinomial): **confirmada**, mas é o fenômeno conhecido da
  matriz de Hilbert ou de Vandermonde. A alegação de "não encontrada na busca" é fraca; o resultado é de análise numérica
  clássica.
- **H14.2** ("janelas retêm mais informação que momentos"): **refutada como afirmação sobre a base**. Com $K\ge12$, os
  momentos na variável adaptada retêm mais que as janelas de energia igual. A diferença entre os números de D4 vem da
  variável (tempo contra fração de energia), e a própria D4 viu metade disso ao notar que janelas uniformes são tão ruins
  quanto momentos.
- **H14.3** ("os momentos dependem do início, as janelas não"): **refutada como afirmação geral**. Vale para momentos em
  $t$, não para momentos em $c(t)$.
- **H14.4** (ortogonalizar não resolve): vale só para a ortogonalização na variável $t$. Ortogonalizar na variável
  adaptada resolve o condicionamento e a informação.
- **Moral corrigida.** A base estável e informativa é qualquer base bem condicionada (Legendre, constantes por partes) na
  variável adaptada ao fluxo. As janelas de energia igual são um caso particular.

**Ressalva sobre o modelo 1.** O ruído $\sigma=\varepsilon|\Delta m|$ "igual por medida" depende da normalização
arbitrária de cada funcional: $\tau^n$ com $T=4{,}04$ s torna os momentos superiores ~1e-2 $\Delta m$. Os fatores de 4 a
6 ordens de grandeza do modelo 1 não são invariantes por essa escolha. O modelo 2, invariante, é o que deve ser citado.

## 7. L15: proposição geral e o caso massivo (H15.1–H15.3)

**H15.1.** A proposição é correta e elementar: pela identidade de Parseval, termos com $a+b=n$ são momentos de ordem $n$
de $\tilde\psi\tilde\psi^\dagger$. A verificação numérica a 7e-16 de D4 é, porém, **tautológica**:
- num laço com FFT periódica, qualquer filtro diagonal unitário preserva exatamente as matrizes de Gram discretas, seja
  qual for a física;
- os 7e-16 confirmam a álgebra do código (útil para detectar erros de índice, como o que D4 corrigiu), não a proposição.

**H15.2** (memória linear invariante só se $e^{i\varphi(0)}=1$): correta. Para campos reais, com filtro ímpar e contínuo,
vale sempre $\varphi(0)=0$. A "dualidade constante" é descontínua em $\omega=0$ (+0,6 e −0,6), e é por isso que viola.

**H15.3** (com quanta massivos a redução a $(B,A)$ falha). Refiz o exemplo (`ver_D4_canais.py` (3)):
- **O exemplo de D4 casa as grandezas erradas.** Os dois espectros casam $\int S$, $\langle\omega\rangle$ e
  $\langle\omega^2\rangle$, mas não $\int S/\omega$ (0,6383 contra 0,6426), que é o análogo de $A$ para um modo
  ($E\leftrightarrow\int\omega^2|\tilde\psi|^2$, $A\leftrightarrow\int\omega|\tilde\psi|^2=\int S/\omega$).
- **Com só $(B,A)$ casados**, em pares de linhas estreitas com pesos positivos, a memória/$E$ difere $5{,}9\times10^{-3}$,
  $4{,}3\times10^{-2}$ e $9{,}4\times10^{-2}$, conforme as posições. **A conclusão de D4 se confirma**, até com folga maior.
- **Com $\int S$, $\int S/\omega$, $\langle\omega\rangle$ e $\langle\omega^2\rangle$ casados** (quatro linhas, pesos
  ≥ 0), a diferença cai para 1,0e-4 a 1,2e-4. A falha da redução a momentos finitos persiste, mas é pequena para espectros
  estreitos ($T_2(\beta(\omega))$ é suave).
- **Status: confirmada numericamente, com o exemplo corrigido.** O número "1,6%" não deve ser citado como efeito de casar
  $(B,A)$.

## 8. Literatura e originalidade (conferência curta)

**API do arXiv** (`export.arxiv.org/api/query`, busca em resumos). Consultas:

| Consulta | Resultado |
|---|---|
| "gravitational wave memory" AND "upper bound" | 1 resultado (arXiv:1410.3323, PTA, sem relação) |
| "memory" AND "area theorem" AND gravitational | 0 |
| "memory" AND "radiated energy" AND inequality | 0 |
| "maximum memory" AND gravitational | 0 |
| "memory" AND "Hawking" AND "area" AND bound | 0 |
| "memory" AND "massive" AND "velocity" AND "multipole" AND gravitational | 0 |
| "higher memory"/"higher memories" | arXiv:2403.13907 (Siddhant et al., memórias superiores PN) e arXiv:2608.23739 (já citado na R5) |
| memória de supernova com neutrinos e polarização | arXiv:2408.01525 e arXiv:2109.01582 (memória de supernovas; a polarização como identificador de canal já está atribuída a CBV2024 por D4) |
| "memory" AND "ultrarelativistic" AND "jet" | arXiv:2301.12590 (memória de GRB, sem cota) |

**WebSearch** ("memory bounded by radiated energy 4E/r"): só Bousso, Halpern & Koeller (2016), com cotas por entropia, e
artigos de memória em gravidade massiva; nenhuma cota memória–energia com constante ótima.

**Conclusão.** Não encontrei $c_L$, $c(e_2)$, a cota da memória nula pela área nem $c_\ell=2^{\ell-1}\ell!(\ell+2)!/(2\ell+1)!$.
A busca em resumos não exclui que isso esteja dentro de artigos, por exemplo Segalis & Ori 2001, que já contém o núcleo
massivo. A postura de D4 ("não encontrado", sem alegar originalidade) é adequada.

Exceção: a parte de condicionamento de L14 (H14.1) é conhecimento clássico de análise numérica (matrizes de Hilbert e
Vandermonde) e não deveria aparecer como "não encontrada".

## 9. Ressalvas menores

1. Tabela de $\lambda_\ell$ em `exp29_canais.txt`: $\ell=8$, $\beta=0{,}01$ está errado (0,0421 contra 0,0527); as
   demais entradas de $\beta=0{,}01$ estão certas.
2. O resumo de D4 diz "no total, 1,3–22% do limite" misturando dois limites (ver §4).
3. A SNR das memórias lentas (exp29 c-i) é de $h_+$ ótimo, com a rampa final de `observaveis.preparar`. Ela é relativa a
   um degrau de 1 ms, e as razões (0,4% e 0,7% em 1 s) dependem pouco desse tratamento. Não refiz esse cálculo.
4. "4 é ótimo" vale para fluências nulas arbitrárias. Para ondas gravitacionais, com $\ell\le L$ finito, $c_L<4$.

## 10. Tabela de status após a verificação

| Id | Status de D4 | Status após a verificação |
|---|---|---|
| H12.1 ($\le4E$, 4 ótimo) | confirmada matematicamente | **confirmada** (refeita; normalização conferida também contra Favata 2009) |
| H12.2 ($c_L$, $c_2=\sqrt{30}/6$, $\sim8{,}9/L$) | confirmada | **confirmada** (código independente até $L=256$; $a=8{,}886$) |
| H12.2b ($c(e_2)$) | confirmada numericamente | **confirmada** (primal independente; nova lei $c\approx c_2+2{,}94\sqrt{1-e_2}$; o S-lema é desnecessário) |
| H12.3 (folga nas binárias) | confirmada numericamente | **confirmada** (integral de Thorne independente, ≤ 1e-5) |
| H12.4 (teste útil da área) | refutada | **refutação mantida** |
| H12.5 ($E_x\ge D\|\delta h\|/4$) | confirmada matematicamente | **confirmada** (a energia inclui a de repouso) |
| H13.1 (núcleo $\ell=0,1$ para todo $\beta$) | confirmada | **confirmada** (argumento) |
| H13.2 (exemplo G×N) | confirmada numericamente | **confirmada, mas tautológica por construção** |
| H13.4 ($c_\ell\beta^\ell$) | confirmada numericamente | **confirmada matematicamente** com forma fechada $c_\ell=2^{\ell-1}\ell!(\ell+2)!/(2\ell+1)!$ |
| H14.1 (condicionamento) | confirmada numericamente | **confirmada** (resultado clássico, não é novidade) |
| H14.2 (janelas > momentos) | confirmada | **refutada como enunciada**: momentos na variável adaptada $c(t)$ retêm mais que as janelas de energia igual |
| H14.3 (momentos dependem do início, janelas não) | confirmada | **refutada como enunciado geral**: vale só para momentos em $t$ |
| H14.4 (ortogonalizar não resolve) | refutada | **mantida só para a variável $t$**: em $c(t)$, Legendre resolve tudo |
| H15.1 (proposição geral) | confirmada | **confirmada** (analítica; o teste numérico é tautológico) |
| H15.2 (memória linear) | confirmada | **confirmada** |
| H15.3 (massivo: a redução a $(B,A)$ falha) | confirmada (1,6%) | **confirmada com exemplo corrigido** (0,6–9,4% com $(B,A)$ casados) |
| H15.4 (Yang–Mills) | não testada | não testada |

## Arquivos desta verificação

- `codigo/revisao/ver_D4_constantes.py`: $c_L$ por Wigner-d/Jacobi até $L=256$; $c_2$ à mão; sanidade; $c(e_2)$
  primal × dual; lei em $\sqrt\varepsilon$.
- `codigo/revisao/ver_D4_folga.py`: $r$ de três binárias pela integral de Thorne direta.
- `codigo/revisao/ver_D4_canais.py`: $c_\ell$ exato e forma fechada; a entrada errada de $\ell=8$; $|K_\beta|\le1$;
  exemplo massivo corrigido.
- `codigo/revisao/ver_D4_momentos.py`: momentos na variável adaptada contra janelas (modelo 2) e sensibilidade ao início.
