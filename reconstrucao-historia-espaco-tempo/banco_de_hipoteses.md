# Banco de hipóteses

Arquivo permanente do laboratório de hipóteses do projeto. Cada hipótese tem identificador, descrição,
fundamentação, equações, experimentos, código, resultados, contraexemplos, limitações, potencial de
originalidade e próximo experimento. Hipóteses refutadas ficam registradas: o motivo da refutação é
informação.

**Status possíveis:**
- **CM** confirmada matematicamente (demonstração);
- **CN** confirmada numericamente (nos casos calculados, com o erro do modelo);
- **R** refutada;
- **I** inconclusiva;
- **NT** ainda não testada.

**Originalidade** (depois de busca bibliográfica):
- **conhecida** (está na literatura);
- **parcial** (há trabalhos próximos);
- **não encontrada** (não achei na literatura; não quer dizer inédita).

Índice rápido (detalhes abaixo):

| ID | Hipótese (curta) | Status | Originalidade |
|---|---|---|---|
| H01 | Teorema 1: as memórias só veem $B=\int\dot h\dot h^\dagger$ e $A-A^\dagger$ | CM + CN | não encontrada |
| H02 | Filtros de fase comuns geram famílias infinitas com as mesmas memórias | CM + CN | não encontrada |
| H03 | A degenerescência persiste em todas as ordens não lineares | I | não encontrada |
| H04 | Radiação que cai no horizonte é invisível no infinito | CM (teoria linear) + ilustrada | conhecida |
| H05 | A torre de memórias reconstrói a onda de forma estável | R | parcial |
| H06 | A família infinita contém pares de binárias da RG | R | não encontrada |
| H07 | Num observador há famílias exatas de binárias com as mesmas 4 memórias | CN (versão idealizada: $m=0$, deslocamento total); I (versão observável: D1) | parcial (degenerescência qualitativa conhecida) |
| H08 | Binárias excêntricas com spins imitam as memórias de uma circular | CN (no piso do modelo, inclusive $q_B=1$ e 1,2; família de dimensão 4 com $\ell_0$) | não encontrada |
| H09 | Sem spins, uma excêntrica só imita a circular com $\eta>1/4$ | CN | não encontrada |
| H10 | (versão antiga) Nenhuma excêntrica imita a circular, nem com spins | R (erro numérico) | — |
| H11 | As memórias globais (céu inteiro) são quase injetivas | CN | não encontrada |
| H12 | Em $q=1$ as memórias veem $\chi_a$ só em 2ª ordem | CM + CN (parte par $\propto d^{2}$) | corolário de simetria conhecida |
| H13 | Simetria $(\eta,D)\to(\lambda\eta,\lambda D)$ de 3 memórias na ordem PN dominante, quebrada em 1PN | CM + CN (o CM só é invariante com $M$ na parte ordinária) | corolário das escalas conhecidas |
| H14 | O recuo não é fixado pelas 4 memórias $m=0$ | CN (o argumento de simetria do 07 não vale; a conclusão vale pela família) | parcial |
| H15 | $\Omega_{\rm mem}=\dot h_{20}/(C\lvert h_{30}\rvert)$ recupera a frequência orbital, $C=40\sqrt7/21$ | CN (2–13%) | corolário de uma linha (Favata 2009b, Nichols 2017) |
| H16 | Medir as memórias em duas janelas elimina a família degenerada | R como "elimina"; CN como "deixa família aproximada" ($4\times10^{-5}$–$2\times10^{-3}$) | não encontrada |
| H17 | As memórias de um observador medem o "orçamento de cargas" ($M_f$, $E$, $J$) | R | — |
| H18 | Um interferômetro mede as quatro memórias | R (giroscópica não mensurável; CM confundido com $t_0$) | conhecida |
| H19 | A memória resolvida no tempo separa os pares degenerados | CN par a par ($\rho_{\rm mem}\approx3$–14; 29–41 para $q_B=1$); I minimizando sobre a família | não encontrada |
| H20 | O nível C (modos $m=0$ do substituto) é o padrão-ouro | R para spin e giroscópica na parte híbrida PN (erro de 5–12% na taxa) | — |
| H21 | A memória de CM é um atraso de $M_f/2$ do degrau da deformação | NT (linha L19, agente D8) | relação conhecida; uso como observável não encontrado |

As hipóteses H18–H21 vêm da revisão adversarial (`08_revisao_e_correcoes.md`); as das linhas da etapa 7 (H22 em diante) estão na seção "Etapa 7", mais abaixo.

---

## Etapas 3 a 6

### H01 — Redução de Gram (Teorema 1)
- **Descrição.** As partes nulas das quatro memórias, no céu inteiro, são funções lineares de
  $B=\int\dot h\dot h^\dagger du$ e $A-A^\dagger$, com $A=\int h\dot h^\dagger du$. Equivalentemente,
  dependem só dos momentos espectrais $\int\omega\,\tilde h\tilde h^\dagger$ e $\int\omega^2\tilde h\tilde h^\dagger$.
- **Fundamentação.** Leis de balanço BMS [Mitman2020; Nichols2018; SO2022]; substituição da expansão em modos.
- **Experimentos.** exp01, teste T7 (erro $10^{-16}$).
- **Status.** CM + CN. **Originalidade:** não encontrada (busca de 31/10/2026).
- **Limitações.** Vale na ordem quadrática da radiação.
- **Próximo.** H03 (todas as ordens).

### H02 — Família infinita por filtros de fase
- **Descrição.** $\tilde h_j(\omega)\to e^{i\varphi(\omega)}\tilde h_j(\omega)$, igual para todos os modos,
  preserva as quatro memórias.
- **Experimentos.** exp02: cinco histórias com memórias iguais em $10^{-15}$ e sobreposição das ondas
  de 0,22 a 0,71.
- **Status.** CM + CN. **Contraexemplos:** nenhum na ordem quadrática.
- **Limitações.** Fontes com dinâmica prescrita.

### H03 — Degenerescência em todas as ordens
- **Descrição.** A família de H02 sobrevive na RG completa, ajustando a fase.
- **Experimentos.** exp03: na ordem cúbica a igualdade quebra ($10^{-7}$–$10^{-4}$) e é restaurável em
  $10^{-8}$.
- **Status.** I. **Próximo.** Demonstração pelo teorema da função implícita em espaços de Sobolev.

### H04 — Núcleo do horizonte
- **Descrição.** Há dados iniciais com radiação zero em $\mathscr I^+$ e não zero no horizonte.
- **Experimentos.** exp04 (fluxo para fora $2{,}4\times10^{-25}$). **Status.** CM [DRSR2018; Masaood2022],
  ilustrada. **Originalidade:** conhecida.

### H05 — Reconstrução estável pela torre de memórias
- **Descrição.** A torre de memórias superiores reconstrói a onda.
- **Experimentos.** exp05: o ruído é amplificado como $e^{a^2/4}$.
- **Status.** R (a reconstrução existe, mas é instável). **Próximo.** L14 (janelas como base estável).

### H06 — Pares de binárias na família infinita
- **Descrição.** A família de H02 contém pares de binárias da RG.
- **Fundamentação da refutação.** Na fase estacionária, $|\tilde h_{22}|^2=a^2\Psi''/2\pi$ amarra amplitude
  e fase (`07_binarias_reais.md` §2.1).
- **Status.** R: analítico na inspiral e numérico no céu inteiro (exp06).

### H07 — Família finita num observador
- **Descrição.** Há famílias contínuas (dimensão ≥ 2) de binárias com as mesmas quatro memórias num
  observador.
- **Experimentos.** exp07 (pares em $10^{-10}$); exp11 (exata nos níveis A e C, depois de resolver de novo).
- **Status.** CN. **Limitações.** Spins alinhados; um único sistema de referência; janela fixa (10 Hz).
- **Próximo.** L01 e L02 (posto, fibra global).

### H08 — Excêntricas com spins imitam a circular
- **Experimentos.** exp12 (SEOBNRv5EHM; $\delta\sim10^{-5}$–$5\times10^{-4}$ para $e_0\le0{,}3$).
- **Status.** CN. **Limitações.** Sem modos $m=0$ no modelo; anomalia fixa em zero. **Próximo.** L16.

### H09 — Sem spins, só com $\eta>1/4$
- **Experimentos.** exp10 corrigido e exp10b (12 partidas por $e_0$; todas no limite $\eta=1/4$).
- **Status.** CN (modelo PN newtoniano, só inspiral).

### H10 — (versão antiga) Nenhuma excêntrica imita a circular
- **Status.** R. A conclusão vinha de um objetivo não suave: a grade de tempo terminava antes da
  separatriz. Corrigido em `pn_excentrico.py`.

### H11 — Quase injetividade das memórias globais
- **Experimentos.** exp06: menor valor singular relativo 0,056 (A1) e 0,41 (A2); o par mais próximo
  difere 0,5%.
- **Status.** CN. **Contraexemplo.** $q=1$ na direção $\chi_a$ (H12).

### H12 — Cegueira de 2ª ordem em $q=1$
- **Fundamentação.** A troca de rótulos equivale a uma rotação de $\pi$; os multipolos $m=0$ são pares em
  $\chi_a$, e os modos com $m$ ímpar são ímpares em $\chi_a$.
- **Experimentos.** exp13: as memórias escalam como $d^{2,0}$ (nível A) e o $1-$match como $d^{2,0}$.
- **Status.** CM + CN. **Originalidade:** parcial (a simetria é conhecida; a consequência para a
  memória não foi encontrada).

### H13 — Simetria PN da ordem dominante
- **Equações.** Na ordem dominante, toda memória é $\eta\,I(x_i,x_f)$; deslocamento, spin e CM escalam
  como $\eta/D$, e a giroscópica como $\eta/D^2$.
- **Experimentos.** exp08: quebra de 1,2–1,4% em 1PN, não restaurável com $(M,D,\iota)$.
- **Status.** CM + CN.

### H14 — O recuo não é fixado
- **Fundamentação.** Rotação de $\pi$ em torno do eixo orbital: $\vec v\to-\vec v$ com os multipolos
  $m=0$ invariantes.
- **Experimentos.** exp07: recuos de 18 a 227 km/s com as mesmas memórias.
- **Status.** CM + CN.

### H15 — $\Omega_{\rm mem}$
- **Experimentos.** exp09 e exp14: erro de 2–3% com as leis de balanço e até 13% com os modos $m=0$ do
  substituto; não separa os pares mais próximos.
- **Status.** CN, com limitações. **Próximo.** L08 (recuperação exata pelos fluxos).

### H16 — Duas janelas eliminam a família
- **Experimentos.** exp14: pares exatos em 10 Hz diferem de $2\times10^{-3}$ a $5\times10^{-2}$ com
  janela em 5 ou 20 Hz.
- **Status.** I (falta mostrar que nenhum outro B satisfaz as 8 equações). **Próximo.** L03 e L04.

### H17 — Orçamento de cargas
- **Descrição.** As quatro memórias de um observador dependeriam só de $M_f$ e de $E$ e $J$ irradiados
  na janela, e a família degenerada preservaria essas cargas.
- **Experimento.** exp16: ao longo da família do exp07, $M_f$ muda até +14%, $E$ até −14% e os
  multipolos globais até 27%. A inclinação e a distância compensam.
- **Status.** R.
- **Lição.** No observador, a degenerescência mistura parâmetros intrínsecos com $(\iota,D)$; não é
  uma degenerescência "de cargas".

---

### Revisão adversarial (etapa 7, parte 1)

As hipóteses H07–H17 foram reavaliadas pela revisão (`08_revisao_e_correcoes.md`, itens C1–C25).

**Mudanças nas hipóteses antigas:**
- **H07.** Os pares do exp07 são exatos para as memórias teóricas só com $m=0$ e deslocamento total.
  Com o deslocamento de janela e os $m\neq0$ eles diferem até 3% (C7, C8). O piso numérico real é
  $\sim3\times10^{-6}$ (C1). A família continua garantida pela contagem; a versão observável é
  resolvida de novo na linha L01 (D1).
- **H08.** Os casos $q_B=1$ e 1,2 eram soluções mal convergidas. Resolvidos de novo, ficam no piso do
  modelo, $\sim10^{-5}$ (C22). A anomalia $\ell_0$ acrescenta uma dimensão à família (C24).
- **H16.** Com as 8 equações de duas janelas sobra uma família aproximada; o jacobiano tem posto 6, mas
  o menor valor singular é $\sim9\times10^{-4}$ (C17).

**Hipóteses novas:**
- **H18 (R).** Um interferômetro não mede a giroscópica e não separa o CM do instante de chegada (C10;
  [SO2023; FS2025; SGN2026]).
- **H19.**
  - **Experimento:** `codigo/revisao/rev_R1_detector.py` e `rev_R1v_detector.py`, match normalizado
    das séries de memória $m=0$.
  - **Resultado:** os pares do exp07 se separam com $\rho_{\rm mem}(+)\approx3$–14, e o par
    $q_B=1$ com 29–41.
  - **Aberto:** ninguém minimizou sobre a família inteira, então a ambiguidade da memória órfã continua
    em aberto.
  - **Próximo:** linha L05 (D3).
- **H20 (R).** O (3,0) do substituto é PN de ordem dominante na parte híbrida. Com a janela dentro da
  parte de RN, a diferença A×C do spin em $q=8$ cai de 6,7% para 0,7% (C18).
- **H21 (NT).**
  - **Origem:** a parte ordinária da memória de CM vale $\mathcal K_{20}/J_{20}=-M_f/2$ ([Nichols2018]
    eq. 4.23, com $M_f$), o que equivale a um atraso do degrau da deformação em relação ao degrau
    previsto pelo fluxo.
  - **Hipótese:** o transiente do h20 de RN em torno do pico (exp09) é esse atraso, e a comparação
    memória observada × memória prevista pela onda mede $M_f$.
  - **Próximo:** linha L19 (D8).

## Etapa 7

(preenchido com os resultados dos agentes D1–D8; ver `09_linhas_de_investigacao.md` e `linhas/`)
