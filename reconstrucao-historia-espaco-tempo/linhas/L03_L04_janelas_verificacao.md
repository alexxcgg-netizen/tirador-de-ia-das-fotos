# Verificação adversarial da linha D2 (L03, L04): janelas e energia de ligação

Verificador: agente adversarial da linha D2. Não editei o relatório original (`linhas/L03_L04_janelas.md`) nem os scripts
dele. Checagens próprias: `codigo/revisao/ver_D2_*.py`. Todo número abaixo vem de uma execução minha (script citado) ou de
um arquivo lido (citado).

Rótulos: [E] estabelecido, [D] derivado ou verificado aqui, [H] hipótese.

## Resumo dos veredictos

| # | Afirmação do relatório | Veredicto | Onde |
|---|---|---|---|
| 1 | Fatoração $dm/dx=-\alpha E_b'$; "o fluxo e as caudas cancelam, só a absorção no horizonte sobra"; não achada na literatura | **parcial** (a identidade vale; a frase das caudas é falsa a partir de 2,5PN; a fatoração está em Favata 2009, eqs. 3.15–3.16) | §1 |
| 2 | Coeficientes 1PN e 1,5PN de $\alpha_2$, $\alpha_4$ (iguais aos de Cunningham et al. 2025) e $H_{20}$ reproduzido | **confirmado** (refeito com amplitudes de Blanchet e Gaunt próprios) | §2 |
| 3 | $\beta_3$ em 1PN, série $S_{30}$, $J(x)$ pela primeira lei | **confirmado** na aritmética; o SO de $\beta_3$ continua **não verificável**; a igualdade de $J$ é tautológica | §3 |
| 4 | Posto das bandas PN: 2 (N), 4 (1PN), 6 (1,5PN) | **confirmado** (modelo próprio, 40 algarismos); "H03.4 refutada" é questão de contagem por tipo de memória | §4 |
| 5 | Substituto contra PN: erro cai ordem a ordem até 1,2e-5; patamar de 1e-3 com spin "da energia do substituto" (H03.7) | **parcial / em boa parte circular**: as bandas boas ficam inteiras na parte PN/EOB híbrida do substituto | §5 |
| 6 | Espectros de $K$ janelas (T0 $K=2$: $\sigma_6$=5,2e-4; O0 $K=3$: 1,1e-6); "cada janela acrescenta dois números"; a janela contínua não acrescenta direções | números **confirmados**; as duas leituras são **parciais** (contagem trivial; em O0 a janela contínua melhora $\sigma_6$ 13 vezes) | §6 |
| 7 | Família aproximada (T0 $K=2$: 1,9e-3 em $q_B=1{,}6$; O0 $K=3$: 1,0e-5) | **confirmado** com outro otimizador e duas partidas | §7 |
| 8 | Desenho ótimo: $D$ = 8,18 → 11,2–11,5; corte de $K=2$ "no pico"; ganho de ~2,2 bits em $\ln M$ | números **confirmados**; leitura **parcial** (ótimo na borda imposta; ganho depende do prior por um fator 2,4; o "ganho" em $M$ já está na forma de onda de uma janela só) | §8 |
| 9 | $\pi f\,dS/dh$ mede $\iota$ sem $M$ e $D$ (H03.9), "não encontrada na literatura" | **parcial**: é a própria primeira lei ($=-\beta/\alpha$), trivial e não mensurável com o SNR de spin | §9 |

## 1. Fatoração e o "cancelamento das caudas" (H03.1)

**A identidade vale [D].** $dm/du=\alpha\,dE/du$ define $\alpha$. Com $\dot x=F/E_b'$, sai $dm/dx=\alpha E_b'$, a menos do fator
$F_\infty/(F_\infty+F_H)$. É uma mudança de variável, e nada mais.

**Não é nova.** Favata, PRD 80, 024002 (2009) (arXiv:0812.0069) faz exatamente essa mudança de variável. Li o PDF, texto
extraído para o diretório de rascunho. A eq. (3.15) é $\int x^n\,dt=\int x^n\,dx/\dot x$, e a eq. (3.16) é
$\dot x=(-L)/(dE/dx)$. O integrando da memória fica, então, $(dU_{20}/dt)/L\times dE/dx$, isto é, $\alpha E'$. O mesmo
artigo nota que "the 1.5PN contribution to the memory also vanishes" e que "the 2.5PN term vanishes for equal-mass
binaries". Ler isso como "observável de banda" é imediato. A alegação de originalidade da seção 8 deve cair para
"reformulação de Favata 2009, eqs. 3.15–3.16".

**A frase "as caudas cancelam, só a absorção sobra" é falsa a partir de 2,5PN** (`codigo/revisao/ver_D2_alpha_indep.py`).
Tirei $\alpha_2=(dh_{20}/dx)/E_b'$ do $H_{20}$ e do $E$ de Cunningham (`resultados/exp20_pn_expressoes.json`):
- coeficiente de $x^{1/2}$: 0;
- de $x$: $71\nu/24-1051/2016$, que confere;
- de $x^{3/2}$: 0 sem spin, e $(320s+297\delta\sigma)/192=5s/3+99\delta\sigma/64$ com spin, que confere;
- de $x^{5/2}$: **$\tfrac{253\pi}{96}(4\nu-1)$**, um termo de cauda ($\pi$) que $E_b$ não tem.

Esse termo vem das caudas de modos com $m$ diferentes, (2,1), (3,3), (3,1), e não cancela na razão. É $\propto\delta^2$:
zero em $q=1$, o que explica por que as colunas 2PN e 2,5PN do `exp20_pn.txt` são idênticas em $q=1$.

Contribuição relativa do termo em $\alpha_2$:

| $q$ | $x=0{,}04$ | $x=0{,}1$ |
|---|---|---|
| 1,2 | −2,2e-5 | −2,2e-4 |
| 3 | −6,6e-4 | −6,6e-3 |
| 8 | −1,6e-3 | −1,6e-2 |

Em $q=3$, $x=0{,}1$, isso supera o patamar de ~1e-3 que o relatório atribui à energia. **Correção:** só a cauda dominante
($4\pi x^{3/2}$) cancela; a partir de 2,5PN, $\alpha$ carrega caudas.

## 2. $\alpha_2$, $\alpha_4$ em 1PN (independente)

`ver_D2_alpha_indep.py` usa as amplitudes não giratórias de Blanchet LRR até 1PN, digitadas por mim: (2,2), (2,1),
(3,3), (3,2), (3,1), (4,4), (4,2). Não usa ABFO nem o código do agente. A Gaunt é minha, pela fórmula geral de três
${}_sY_{\ell m}$, com $\overline{{}_sY_{\ell m}}=(-1)^{s+m}{}_{-s}Y_{\ell,-m}$.

| Quantidade | Obtido aqui | Esperado |
|---|---|---|
| fluxo 1PN (controle) | $-1247/336-35\nu/12$ | idem (exato) |
| $\alpha_2$ dominante | $4\sqrt{30\pi}/21=1{,}8491675$ | idem |
| $\alpha_2$, 0,5PN | 0 | 0 |
| $\alpha_2$, 1PN | $-0{,}5213294+2{,}9583333\,\nu$ | $-1051/2016+71\nu/24$ |
| $\alpha_4$ dominante | $\sqrt{10\pi}/315$ | idem |
| $\alpha_4$, 1PN | $-10{,}682156+51{,}732955\,\nu$ | $-157925/14784+9105\nu/176$ |

Conferi também à mão $(a_2+2e_2)/2=-4075/4032+67\nu/48$ (o 1PN de Favata) e $\tfrac25a_3+e_3=16s/3+419\delta\sigma/160$
(o 1,5PN de Cunningham). **Confirmado.** O SO de $\alpha_2$ fica confirmado pela razão de Cunningham (item 1).

## 3. $\beta_3$, $S_{30}(x)$ e primeira lei

- **$\beta_3$ em 1PN.** $-5017/1296+1247/336=-1450/9072=-725/4536$ e $-25/108+35/12=145/54$. A aritmética confere, e
  $\sqrt{210\pi}/70=\sqrt{3\pi/70}$ (Nichols).
- **$S_{30}$** (`ver_D2_primeira_lei.py`). Integrei $-\beta x^{-3/2}E_b'$ com os $b_2$, $b_3$ do relatório e o $E$ de
  Cunningham: $1+(7529/4536-68\nu/27)x-(415s/54+3575\delta\sigma/864)x^{3/2}$, igual ao relatório.
- **O SO de $\beta_3$** ($100s/27+1415\delta\sigma/432$) não tem conferência independente. A busca na web (abaixo) não achou
  o modo (3,0) com SO publicado, e a API do arXiv recusou as consultas ("Rate exceeded", máquina compartilhada). Fica
  **não verificável** aqui. Vem das amplitudes ABFO, cujo SO foi validado pelo $\alpha_2$ (item 2).
- **$J(x)$ pela primeira lei.** A diferença para o $J$ de Blanchet até 3PN, que digitei por memória, é 0. O SO,
  $-\tfrac{35}{6}s-\tfrac52\delta\sigma$, coincide com a forma conhecida. Mas a igualdade é **tautológica**: o $E$ e o $J$
  publicados satisfazem $dE=\Omega\,dJ$ por construção. Não é teste de nada novo.

## 4. Posto das bandas PN (H03.3, H03.4)

`ver_D2_posto_pn.py` é um modelo próprio. Usa $h_{20}$ (Favata/Cunningham até 1,5PN) e $S_{30}$, com fatores angulares
$\sin^2\iota$ e $\sin^2\iota\cos\iota$, aritmética de 40 algarismos (mpmath) e derivadas centrais de passo 1e-12.
Valores singulares para A, 8 bandas de 10 a 37,5 Hz:

| Ordem | Valores singulares |
|---|---|
| N | 1,22e-1, 2,22e-2, 7e-28, … (posto **2**) |
| 1PN | 1,19e-1, 2,23e-2, 8,4e-4, 1,6e-5, 8e-44 (posto **4**) |
| 1,5PN | 1,27e-1, 2,36e-2, 1,66e-2, 1,09e-4, 4,0e-5, **5,5e-7** (posto **6**) |

O padrão se repete com 3 bandas e com $q=3$. Só com o deslocamento, o posto é 1 → 2 → 3.

**Confirmado:** cada ordem acrescenta um número por tipo de memória, logo dois com deslocamento + spin. "H03.4 refutada"
é, portanto, uma questão de contagem e não um fato físico novo. O sexto valor singular é 5e-7 a 5e-6 (o meu e o do
relatório), muito abaixo de qualquer precisão: "fixam $\chi_1$ e $\chi_2$" só vale formalmente.

## 5. Substituto contra PN (H03.7) — teste em boa parte circular

O NRHybSur3dq8_CCE é híbrido. Fonte: Yoo et al. 2023, arXiv:2306.03148, seção II, lida no HTML.
- A janela de hibridização fica a "roughly 2500−3500M before the peak".
- Antes dela, as amplitudes são PN ("non-memory terms to 3.5 PN order") e a fase é a do SEOBNRv4_opt.

`ver_D2_hibrido.py` localiza essa janela em $Mf_{22}$:
- $q=1$: 0,0055–0,0062;
- A: 0,0056–0,0063;
- $q=3$: 0,0064–0,0072.

$Mf=0{,}002$ cai em $u\approx-59000$ M, $0{,}003$ em −19600 e $0{,}006$ em −2850.

Consequências:
- **As bandas [0,002; 0,006] estão inteiras na parte PN/EOB.** O "erro 1,2e-5 em 3,5PN" compara PN com amplitudes PN e
  fase EOB. O $\alpha$ efetivo concorda a 6,5e-5 porque as amplitudes ali **são** PN. Não é um teste contra RN.
- **O patamar de ~1e-3 com spins** mede a diferença entre a $E_b$ PN e a energética do SEOBNRv4_opt (os termos de fase com
  spin do PN vão só até 2,5PN). Não é uma propriedade do substituto RN.
- **Na parte RN** ($Mf\ge0{,}006$; o relatório a chama de "fusão", mas é $u\approx-2800$ a $-250$ M, com
  $Mf_{\rm pico}\approx0{,}058$), o erro não cai ordem a ordem. Em $q=1$, deslocamento (2,0), [0,012; 0,014]: 2PN +3,8e-3,
  3PN −5,0e-3, 3,5PN −7,2e-3 (`exp20_pn.txt`). **H03.7 vale só na parte híbrida PN, onde é circular.**
- **Parte nula da CM.** O "salto em $Mf\approx0{,}006$" (`exp20_cm_dt.txt`: −1,2e-5 por 0,001 em [0,005; 0,006] e −3,05e-5
  em [0,006; 0,007]) coincide com a janela de hibridização. Isso **apoia** a [H] do relatório (artefato de hibridização).

## 6. Espectros de $K$ janelas (H03.5, H04.1)

**Reprodução** (`ver_D2_jac_outro_ponto.py`). Com passos dobrados, A dá T0 $K=2$: $\sigma_6$ = 5,20e-4 e O0 $K=3$: 1,15e-6,
iguais ao `exp21_jacobianos_K.txt`. **Confirmado** como número.

**Outro ponto** ($q=2$, $\chi=(0{,}5;0)$, mesmas janelas): T0 $K=2$ tem $\sigma_6$ = 1,02e-3; O0 $K=3$, **2,5e-7** (passos
×1 e ×2 iguais). A "terceira janela" de O0 dá um sexto número 4,6 vezes menor que em A.

**Escolha das janelas** (`ver_D2_subconjuntos.py`, os 18424 trios das 49 janelas salvas no `exp21_jacobianos_K.npz`).
Em O0 $K=3$, $\sigma_6$ fica entre 2e-11 e 3,9e-6, com mediana 2,0e-7. O trio do relatório (1,15e-6) está entre os
melhores. Em 7% dos trios, $\sigma_6$ muda mais de 10% entre $h$ e $h/2$ (zero numérico). Em T0 $K=2$, o par do relatório
(10; 37,5 Hz) é **o máximo** (5,2e-4) entre os 1176 pares, com mediana 1,5e-4. As janelas mais separadas ganham, como o
relatório diz.

**Leituras.**
- **"Cada janela acrescenta dois números" é contagem de equações.** Em T0, uma janela dá 4 equações e o modelo tem 6
  parâmetros: a segunda só pode acrescentar 2. Em O0, cada janela tem exatamente 2 equações. Um mapa genérico de posto
  máximo dá isso sempre. A evidência não distingue "dois números físicos por janela" de "posto máximo genérico". Em T
  (7 parâmetros), $K=1\to2$ acrescenta 3.
- **"A janela contínua não acrescenta direções"** é trivial com o posto já saturado. Em O0, que é o conjunto mensurável,
  $\sigma_6/\sqrt K$ cresce 13 vezes de $K=3$ para 49. O relatório diz isso na 5.4, mas o resumo e a tabela (H03.5')
  generalizam a partir de T0.

## 7. Família aproximada (H03.6)

`ver_D2_familia.py` resolve de novo com `scipy.optimize.least_squares` (método `lm`, sem limites), partindo de A e de um
ponto deslocado ($\chi=(0{,}1;0{,}1)$, $M=70$, $\iota=45^\circ$, $D=380$):

| Caso ($q_B=1{,}6$) | max $\lvert r\rvert$ (duas partidas) | Relatório | Solução |
|---|---|---|---|
| O0 $K=3$ | 1,04e-5 | 1,0e-5 | $\chi_1=+0{,}5668$, $\chi_2=-0{,}6934$, $M=66{,}298$, $\iota=49{,}94^\circ$, $D=392{,}8$ (a mesma do `exp22_familia_O0_K3.txt`) |
| T0 $K=2$ (10; 37,5 Hz) | 1,94e-3 | 1,9e-3 | — |

**Confirmado.** Ressalva: em O0 a solução tem $\chi_2=-0{,}69$, perto do limite do modelo (−0,8). Em $q_B\ge2$ o relatório já
marca o contato com a borda.

## 8. Desenho ótimo (H04.1–H04.3)

**Reprodução** (`ver_D2_desenho.py`, código próprio, sem somas acumuladas, a partir de `exp23_prep_A.npz` e `_M150.npz`):

| Fonte | $D$($K=1$) | $D$($K=2$), `diag` | $D$($K=2$), `corr` |
|---|---|---|---|
| A | 8,175 | 11,466 | 11,200 |
| $M=150$ | 9,969 | 14,827 | 13,821 |

Iguais ao `exp23_desenho.txt`. **Números confirmados.**

**Ressalvas.**
- **Ótimo na borda.** O corte ótimo de $K=2$ é o último índice permitido (44 de 44 em A; 30 de 30 em $M=150$), e $D$ ainda
  cresce ali (penúltimo: 11,09 contra 11,47). "O corte cai no pico" quer dizer que o ótimo bate na restrição
  $0{,}9\,f_{\rm pico}$ imposta pela definição em frequência. Não é um ótimo interior. A "universalidade" desse corte é
  por construção (o relatório reconhece em parte).
- **O ganho depende do prior.** Com as larguras ×0,5 e ×2, o ganho de $K=1\to2$ em A (`diag`) vai de 1,95 a 4,72 em $D$
  (`corr`: 1,82 a 4,37). "~2,2 bits" vale só para os priors escolhidos.
- **Linha de base artificial.** O modelo só estima a amplitude de cada banda. A forma de onda de memória de **uma** janela,
  resolvida no tempo, já tem a informação sobre $M$: no `exp24_fisher_memoria.txt` (linha D3, CE, detector único, $t_0$
  livre), $\sigma_{\ln M}$ a posteriori é 0,121 contra o prior de 0,317 (razão 0,38). As duas bandas daqui dão 0,36. O "ganho
  em $\ln M$" das bandas recupera, então, o que o resumo por amplitudes descarta; não é informação além da forma de onda.
- **Inconsistência menor.** "$\sigma_{\ln M}$: 0,80 → 0,28" é de $K=1$ para $K=3$. Com $K=2$ é 0,36 (`corr`).
- **A deriva $f_{\rm corte}\propto M^{-0{,}72}$** confere com os cortes: $\ln(157{,}3/49{,}2)/\ln5=0{,}72$.

## 9. Razão $\pi f\,dS/dh$ (H03.9)

Pela própria fatoração, $dS/dh=-(\beta/\alpha)\,x^{-3/2}M=-(\beta/\alpha)/\Omega$, logo $\pi f\,dS/dh=-(\beta/\alpha)\,A_s/A_d$.
É a primeira lei reescrita. Confere $b_2-a_2=0{,}3615-0{,}2731\nu$.

Ressalvas:
- **Não mensurável.** A SNR de spin da janela inteira em CE é 3,2, e as bandas da inspiral ficam abaixo de 1,5
  (`exp23_prep_A.txt`).
- **Depende das polarizações.** Exige separar + de × e conhecer $\psi$ (achado 5 da revisão).
- **Originalidade fraca.** A taxa da memória de spin é $\propto$ fluxo de $J$ (Nichols 2017), e o fluxo de $J$ é o fluxo
  de $E$ dividido por $\Omega$.

"Confirmada matematicamente" está certo, mas é trivial.

## Literatura (como conferi)

- **Favata 2009** (arXiv:0812.0069): PDF baixado pelo WebFetch e texto extraído no diretório de rascunho. Trechos citados no
  item 1 (eqs. 3.15–3.16; "1.5PN contribution … also vanishes"; "2.5PN term vanishes for equal-mass binaries").
- **Yoo et al. 2023** (arXiv:2306.03148): HTML pelo WebFetch, seção II (hibridização).
- **WebSearch** com "spin memory spin-orbit 1.5PN (3,0)", "memory binding energy tail cancel" e "memory frequency bands
  identifiability Fisher":
  - não achei o (3,0) com SO publicado;
  - achei Gasparotto et al. PRD 107, 124033 (2023), um Fisher da memória para LISA, sem desenho de bandas.
- **API do arXiv** (export.arxiv.org): devolveu "Rate exceeded" em todas as tentativas. A busca é, portanto, parcial.
- **Originalidade que resiste:** o desenho ótimo de bandas de memória e a contagem de posto ordem a ordem. Ambos são
  extensões diretas.
- **Originalidade que não resiste:** a fatoração com o cancelamento do fluxo (Favata 2009).

## Scripts e saídas desta verificação

- `codigo/revisao/ver_D2_alpha_indep.py`: $\alpha_2$, $\alpha_4$ por Blanchet+Gaunt próprio; $\alpha_2$ até 2,5PN pelo
  Cunningham (termo $\pi$).
- `codigo/revisao/ver_D2_primeira_lei.py`: $J(x)$, $S_{30}(x)$.
- `codigo/revisao/ver_D2_posto_pn.py`: posto PN com 40 algarismos.
- `codigo/revisao/ver_D2_hibrido.py`: $Mf$ contra o tempo e a janela de hibridização.
- `codigo/revisao/ver_D2_subconjuntos.py`: todos os subconjuntos de janelas do npz do exp21.
- `codigo/revisao/ver_D2_jac_outro_ponto.py`: jacobianos em $q=2$ e com passos ×2.
- `codigo/revisao/ver_D2_familia.py`: família com `scipy` LM.
- `codigo/revisao/ver_D2_desenho.py`: critério D independente, priors e só deslocamento.

## Recomendações ao autor

1. Trocar "o fluxo e as caudas cancelam; só a absorção sobra" por "o fluxo cancela; a cauda dominante (1,5PN) cancela;
   a partir de 2,5PN $\alpha$ tem caudas $\propto\delta^2$". Citar Favata 2009, eqs. 3.15–3.16, como origem da fatoração.
2. Rebaixar H03.7 para "consistência da parte híbrida PN/EOB do substituto". Refazer o teste só com $Mf\ge0{,}0065$
   (parte RN), onde o erro não decresce além de 2PN. Corrigir o rótulo "fusão" para $Mf\ge0{,}006$.
3. Reescrever H03.5 e H03.5' como "posto genérico máximo" e destacar que, em O0, $\sigma_6$ depende do ponto e das
   janelas por mais de uma ordem de grandeza.
4. No desenho, declarar o ótimo de borda e a dependência do prior, e comparar com o Fisher da forma de onda completa
   (exp24).
