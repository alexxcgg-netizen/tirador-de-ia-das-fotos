# Etapa 5 — Matemática e experimentos numéricos

Todo o código está em `codigo/`, e as saídas em `resultados/` e `figuras/`. Para rodar:

```bash
pip install numpy matplotlib mpmath
cd reconstrucao-historia-espaco-tempo/codigo
python3 exp01_verificacao.py        # ~20 s
python3 exp02_fontes_degeneradas.py # ~2 min
python3 exp03_ordem_cubica.py       # ~10 min
python3 exp04_horizonte.py          # ~2 min
python3 exp05_torre_momentos.py     # ~2 s
```

Unidades: $G=c=1$, massa da fonte $M=1$, $h$ = $r$ × deformação.

## Módulos

- `harmonicos.py`: harmônicos com peso de spin (fórmula de Goldberg sem cotangentes), operadores
  $\eth,\bar\eth$ nas convenções de [Mitman2020], quadratura de Gauss–Legendre na esfera.
  Testes: ortonormalidade (erro 1e-14), conjugação (exata), autovalores de $\eth,\bar\eth$ contra
  derivadas numéricas (1e-9).
- `memorias.py`: as quatro memórias (partes nulas), calculadas de dois jeitos independentes: no tempo,
  na grade da esfera (`memorias_tempo`), e pelas matrizes de Gram (`memorias_gram`). Também calcula as
  partes não lineares instantâneas (modo de memória de spin, taxa de memória nula).
- `fontes.py`: fontes hipotéticas da Etapa 3 e os filtros de fase.

## 1. Verificação contra a literatura (`exp01_verificacao.py`)

| Teste | Resultado |
|---|---|
| T1 $h^{\rm mem}_{20}$ de binária pós-newtoniana × $(4/7)\sqrt{5\pi/6}\,\eta M(x_f-x_0)$ [Favata2009a] | razão 1,0003 |
| T2 padrão $\sin^2\theta(17+\cos^2\theta)/192\pi$ [Nichols2017] | erro 6e-4 |
| T3 memória de spin (3,0) × $\sqrt{3\pi/70}\,\eta M^2\lvert x_f^{-1/2}-x_0^{-1/2}\rvert$ [Nichols2017] | razão 1,00004; fase $\pi/2$ (magnética) |
| T4 modo de memória de spin $h_\times=(3/32\pi)\,\mathrm{Im}(\bar H_{22}\dot H_{22})\sin^2\theta\cos\theta$ [Nichols2017] | razão 1,000000, com sinal |
| T5 momento angular irradiado pelo termo $W$ × fórmula de modos | razão 1,000000 |
| T6 cálculo no tempo × matrizes de Gram | 1e-16 a 1e-15 |
| T7 $B=M_2$, $A=iM_1$, $A^\dagger=-A$ (momentos espectrais) | 1e-16 |
| T8 memória de CM (3,3), (3,1), (5,5) × [Nichols2018, eq. DeltaK35modes] | razão 1 exata |
| T9 termo de helicidade com tensores explícitos: $N_{ab}\tilde C^{ab}=-2\,\mathrm{Im}(\bar h\dot h)$ | 9e-16 |

Os resíduos de T1 e T2 (3e-4, 6e-4) vêm da inconsistência pós-newtoniana de incluir $\dot A^2$ no
fluxo (a energia irradiada sai 2,9e-4 acima de $\tfrac12\eta M\Delta x$), não do código.

## 2. Fontes distintas, mesmas memórias (`exp02_fontes_degeneradas.py`)

Descrito em `03_problema_concreto.md` §3. Resumo: as fontes B (anti-*chirp*), C (duas explosões),
D (dualidade) e E (dispersão) reproduzem as quatro memórias de A no céu inteiro com diferença
≤ 2,4e-15. As sobreposições das formas de onda com A são 0,22 / 0,71 / 1,00 (0,50 sem girar a
polarização) / 0,51.

Figuras: `figuras/e3_formas_de_onda.png`, `figuras/e3_mapas_memoria.png`, `figuras/e3_divisao.png`.

## 3. Ordem cúbica (`exp03_ordem_cubica.py`)

- O modelo inclui a memória acumulada (2,0) e (4,0) e o modo de memória de spin (3,0) dentro de $h$,
  e recalcula as quatro memórias com as mesmas fórmulas exatas. Fica de fora a parte elétrica
  instantânea que depende da dinâmica da fonte, e as caudas.
- Efeito da ordem cúbica nas memórias de A: 1,2% a 2,5%.
- Quebra A × B (anti-*chirp*): 1,1e-7 (deslocamento), 3,6e-7 (spin), 1,1e-4 (CM), 1,4e-7 (giroscópica).
- **Continuação:** história $B(s)$ = A com dispersão $s\,\varphi_E$ mais correção de fase em
  100 funções; $s$ de 0,05 a 1 em 20 passos. Sem correção, a diferença cúbica chega a ~1e-4; com
  correção fica em ~1e-7 o caminho todo. O jacobiano tem posto 56–58 de 58 componentes.
- **Polimento no fim (Levenberg–Marquardt):** diferenças finais 7e-8 (deslocamento), 2,5e-8 (spin),
  3e-8 (CM), 1,4e-8 (giroscópica), contra 2,7e-5 a 1,2e-4 sem correção. A memória quadrática fica
  exata (≤ 2e-15). A sobreposição do modo 22 com A é 0,60.
- **Limitação:** convergência lenta ($\sigma_{\min}/\sigma_{\max}\approx10^{-9}$). Não cheguei à
  precisão de máquina. É evidência numérica forte de degenerescência na ordem cúbica, não prova.

Figura: `figuras/e3_ordem_cubica.png`.

## 4. Núcleo do horizonte (`exp04_horizonte.py`)

- Perturbação de paridade ímpar $\ell=2$ de Schwarzschild (equação de Regge–Wheeler),
  esquema *leapfrog* exatamente reversível, diferenças finitas de 4ª ordem, $r^*\in[-2000,2000]$.
- Construção: um pacote caindo no horizonte no fim da história, evoluído para trás no tempo. A
  segunda camada de tempo usa a relação de dispersão **discreta** do esquema, para ser uma onda
  "pura que sai" e não deixar eco numérico.
- História B (onda que entra + pulso de compensação perto do horizonte): fluxo para fora no
  observador ($r^*=800$) = **2,4e-25** (nível de arredondamento); $|\psi|$ máximo ali = 2e-13;
  fluxo para dentro do horizonte = 4,76.
- História C (a mesma onda, sem o pulso): fluxo para fora = **0,46** (parte refletida pela barreira).
- História A (nada acontece): tudo zero. **A e B são indistinguíveis em $\mathscr I^+$**, mas em B
  uma onda inteira caiu no buraco.
- Ilustra um teorema já estabelecido [DRSR2018; Masaood2022] na teoria linear. Na teoria não linear,
  a massa final difere pela energia absorvida (é preciso comparar com um buraco de massa ajustada).

Figura: `figuras/e5_horizonte.png`.

## 5. Torre de memórias e continuação analítica (`exp05_torre_momentos.py`)

- Modelo: $N(u)=e^{-u^2/2\sigma^2}\cos\omega_0u$. Os momentos $\mu_n=\int u^nN\,du$ têm forma fechada
  com polinômios de Hermite, calculados com 150 dígitos (mpmath).
- Cada momento medido com erro relativo $\varepsilon$; reconstrução de $\tilde N(\omega_0)$ pela série de Taylor.
- **Amplificação do ruído** (erro na onda / erro nas memórias), com $a=\omega_0\sigma$ (~número de ciclos):

| $a$ | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|
| amplificação | 3,7 | 78 | 1,1e4 | 1,2e7 | 9,6e10 | 5,9e15 |
| $e^{a^2/4}$ | 2,7 | 55 | 8,1e3 | 8,9e6 | 7,2e10 | 4,3e15 |

- Com $a=12$ (só ~4 ciclos dentro de ±σ), errar menos de 10% na onda exige memórias com precisão
  ~2e-17. Uma fusão binária tem dezenas de ciclos na banda.
- **Cauda $1/u^2$ da *news*:** $\mu_1$ cresce como $\ln U$ e $\mu_2$ como $U$ com o corte $U$: a
  torre nem está definida sem regularização [LS2019].

Figura: `figuras/e5_torre_momentos.png`.

## 6. O que não foi feito (próximos experimentos)

- Ordem cúbica completa com os termos elétricos instantâneos de uma fonte de verdade (formalismo
  pós-Minkowskiano) e as caudas.
- ~~Fontes autogravitantes: memórias globais de binárias com modelos de forma de onda (substitutos de
  relatividade numérica com memória [Yoo2023]) para testar a hipótese de quase injetividade~~ —
  feito na etapa 6 (exp06–exp15, descritos em `07_binarias_reais.md`)
  (`03_problema_concreto.md` §6).
- Fisher completo da memória para LIGO, ET, CE e LISA com curvas de ruído reais.
- Simulação do teste de birrefringência com a memória como referência (`04_brechas.md` §8).
