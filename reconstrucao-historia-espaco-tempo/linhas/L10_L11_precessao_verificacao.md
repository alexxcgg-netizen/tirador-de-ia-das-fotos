# Verificação adversarial da linha D6 (L10, L11): precessão e topologia

Relatório verificado: `linhas/L10_L11_precessao.md`. Não editei o relatório nem os scripts do agente.

Scripts novos, em `codigo/revisao/`:

| Script | O que testa | Saída |
|---|---|---|
| `ver_D6_eixos.py` | eixos ópticos e divisão dos zeros, por um caminho que não usa `sYlm` nem `eth`. O campo vem da hessiana covariante de potenciais polinomiais harmônicos: $\mathrm{Hess}_S\Phi=P\,\partial\partial F\,P-kFP$, parte sem traço; o campo B sai por rotação de 45° | `resultados/ver_D6_eixos.txt` |
| `ver_D6_modos.py` | memória $m=0$ por quadratura direta no céu (Gauss–Legendre 24×48, `lal.SpinWeightedSphericalHarmonic`, sem `memorias.py`), com e sem os modos (3,±1), (4,±1), (4,±2); valor final do (2,0) | `resultados/ver_D6_modos.txt` |
| `ver_D6_jacobiano.py` | posto 7 com outros passos; bico em $\chi_\perp=0$ no ponto alinhado; variante de modelagem `zerar_m0`; 3 pontos novos; hierarquia dos spins no plano | `resultados/ver_D6_jacobiano.txt` |
| `ver_D6_eixoQ.py` | população nova (semente 99, 10 sistemas, mais 3 extremos): $e_1$ do tensor $\ell=2$ (ajuste com `scipy.special.sph_harm_y`), $e_Q$ com três pesos, $J_\text{rad}$, $\chi_f$; zeros por um localizador próprio | `resultados/ver_D6_eixoQ.txt` |
| `ver_D6_zeros_extra.py` | os casos em que o meu localizador falhou, refeitos com o localizador do exp34 e a icosfera | `resultados/ver_D6_zeros_extra.txt` |

Rótulos: [E] estabelecido, [D] derivado, [H] hipótese.

---

## 1. Eixos ópticos do campo $\ell=2$ puro (H11.4, [D]) — confirmado, com uma ressalva de originalidade

**Derivação refeita.** Tomo $\Phi=n\cdot A\,n$, com $A$ simétrico e sem traço. Na esfera, $\mathrm{Hess}_S\Phi=2PAP-2\Phi P$. A parte sem traço se anula quando $A$, restrito ao plano tangente, é isotrópico.

O plano $n^\perp$ que contém $e_2$ e $t=-\sin\alpha\,e_1+\cos\alpha\,e_3$ é isotrópico se e só se
$$\lambda_2=\lambda_1\sin^2\alpha+\lambda_3\cos^2\alpha,$$
isto é, $\sin^2\alpha=(\lambda_2-\lambda_3)/(\lambda_1-\lambda_3)$. Os zeros ficam em $n=\cos\alpha\,e_1\pm\sin\alpha\,e_3$ e nos antípodas. A fórmula do relatório está certa.

**Numérico** (T1 em `ver_D6_eixos.txt`).
- Quatro tensores aleatórios.
- Em cada um: 4 zeros, todos de índice +1/2, soma 2,000.
- Desvio máximo em relação à fórmula: 1,2e-6°, no campo E e também no B.

**Coeficiente exato da divisão.** O relatório não dá o coeficiente. Seja $\varepsilon_2$ a norma da parte $m=\pm2$ de $\ell=2$ dividida por $|a_{20}|$, com $\pm2$ juntos. Então
$$\alpha\simeq\sqrt{2\varepsilon_2/\sqrt3}.$$
- No teste T2 com $\varepsilon=10^{-4}$: separação de 1,233°, contra $2\sqrt{2\cdot10^{-4}/\sqrt3}=1{,}232°$.
- Em AL1, com $\varepsilon=1{,}79\text{e-}3$, a fórmula dá 2,605°. Bate com os "eixos ópticos 2,60°" do relatório e com os 2,55° medidos.
- O "$\sqrt\varepsilon=2{,}43°$" do relatório é só a lei de escala, sem o coeficiente.

**Originalidade.** A fórmula é a dos eixos ópticos de um cristal biaxial: normais às seções circulares do elipsoide (Fresnel; refração cônica de Hamilton). O relatório faz bem em chamar a matemática de elementar. Convém citar a óptica cristalina explicitamente.

Não achei a aplicação aos zeros da memória (busca na seção 8).

## 2. "Qualquer parte $m\neq0$ divide cada zero +1 em dois +1/2, com meia abertura $\sim\sqrt\varepsilon$" (H11.3) — parcialmente refutada

Contraexemplos (T2 em `ver_D6_eixos.txt`). Partindo de $Y_{20}$, somei $\varepsilon$ vezes uma perturbação normalizada, com $\varepsilon=10^{-2},10^{-3},10^{-4}$, e procurei os zeros a até 30° do polo:

| Perturbação | Zeros perto do polo | Escala da separação |
|---|---|---|
| $\ell=2,3,4$ com $m=2$ (E) | 2 de +1/2 | $\varepsilon^{0{,}50}$ ✓ |
| $\ell=2,3,4$ com $m=1$ (E e B) | 2 de +1/2 | $\varepsilon^{1{,}00}$ |
| $\ell=3$, $m=3$ (E) | **4: três de +1/2 e um de −1/2** | $\varepsilon^{1{,}00}$ |

**Explicação.** Perto do polo, na base fixa, o campo axissimétrico vale $z\approx a\zeta^2$, com $\zeta=\theta e^{i\varphi}$.
- Um $m=2$ soma uma constante: dois zeros a $|\zeta|\sim\sqrt\varepsilon$.
- Um $m=1$ soma um termo $\propto\zeta$: dois zeros a $|\zeta|\sim\varepsilon$. É a inclinação, ou rotação, do padrão.
- Um $m=3$ soma um termo $\propto\bar\zeta$: um zero de −1/2 na origem e três de +1/2 a $|\zeta|\sim\varepsilon$.

**O que fica de pé:**
- A divisão em $\sqrt{\cdot}$ vale para a parte $|m|=2$ no referencial do eixo principal.
- A parte de $m$ ímpar só divide em $O(\varepsilon)$ e pode criar zeros de −1/2.
- Em AL1 e AL2 os $m$ ímpares se anulam por simetria equatorial. Por isso os números do relatório, 2,55° contra 2,60°, continuam válidos.
- Enunciado correto de H11.3: "meia abertura $\simeq\sqrt{2\varepsilon_2/\sqrt3}$, com $\varepsilon_2$ a parte $|m|=2$; partes de $m$ ímpar dão divisão $O(\varepsilon)$ e podem gerar zeros de −1/2". Isso também sugere de onde vem o zero de −1/2 observado na memória de spin.

## 3. Poincaré–Hopf, soma 2 (H11.1) — confirmado

- **[E] Teorema.** A soma dos índices de um campo de linhas em $S^2$ é $\chi(S^2)=2$. Conjugar $h$ inverte todos os enrolamentos, então o teste de orientação pela soma −2 é legítimo.
- **Testes sintéticos independentes:** soma 2,000 em todos os casos de T1.
- **População nova (13 sistemas):** com o localizador do exp34 mais a icosfera, a soma é 2 em todos os sistemas que reexaminei (`ver_D6_zeros_extra.txt`).
- **Falha do meu localizador:** o meu localizador simples, com mínimos numa rede e Nelder–Mead, perdeu zeros próximos em S01 e S03 (soma 1,5) e na memória de spin de S03 e S05.
  - O do exp34 achou 4 zeros de deslocamento, e 6 de spin, em todos esses casos.
  - A menor distância entre zeros ali chega a 1,6–2,7°.
  - Isso confirma o que o relatório diz na seção 5.4: a contagem "68/68" depende do localizador. A soma 2 serve como detector de falha, mas não prova que nenhum par $\pm1/2$ foi perdido, porque um par perdido não altera a soma.
- **Memória de spin:** o relatório não alega universalidade aqui, mas os casos novos ampliam o quadro.
  - Na maioria dos sistemas novos, 6 zeros (cinco +1/2 e um −1/2).
  - Em X1 ($q=4$, dois spins de 0,8 no plano), 4 zeros.
  - Em X2 ($q=1$, spins de 0,8 antiparalelos no plano), **8 zeros** (seis +1/2 e dois −1/2), confirmados pelo exp34.

## 4. Os zeros seguem $e_Q$, não $J_\text{rad}$ nem $\chi_f$ (H11.5, H10.3) — confirmado, com ressalva

**População nova** (`ver_D6_eixoQ.txt`, 13 sistemas; $e_1$ = autovetor do autovalor distinto de $A$, escolhido sem supor que seja o maior). Ângulo de $e_1$ com cada eixo:

| Eixo | Mediana | Máximo |
|---|---|---|
| $e_Q$, peso $\lvert\dot h\rvert^2$ de todos os modos (como no exp34) | 1,12° | 4,55° (X1) |
| $J_\text{rad}$ | 2,62° | 15,8° |
| $\chi_f$ | 6,40° | 22,2° |
| $\hat L_i$ | 9,31° | 42,8° |
| eixo no pico | 7,85° | 15,8° |

O relatório dá 0,89/4,13 para $e_Q$, 3,25/19,1 para $J_\text{rad}$ e 6,0/30,1 para $\chi_f$. A ordem $e_Q < J_\text{rad} < \chi_f$ se repete na amostra nova. Em todos os sistemas o autovalor distinto foi o maior, então a escolha de $e_1$ no exp34 está certa.

**Ressalva.** $e_Q$ é a previsão do modelo uniaxial, $A\propto\int dE\,(3\hat z_c\hat z_c^T-1)$, e depende do peso:

| Peso | Mediana | Máximo |
|---|---|---|
| só os modos (2,±2) | 1,27° | 10,4° (X1) |
| uniforme no tempo | 5,6° | 37° |

Portanto a afirmação física é: "o eixo do tensor $\ell=2$ é o eixo coprecessante médio ponderado pelo fluxo de energia de todos os modos". Isso é quase uma identidade do modelo de emissão axissimétrica instantânea. Não é uma relação com uma grandeza conservada.

A refutação de "segue $J_\text{rad}$" é robusta: há casos de 13° a 19°.

## 5. Posto 7 de 7 do jacobiano módulo rotações (H10.4) — confirmado; o conteúdo está no espectro

Resultados de `ver_D6_jacobiano.txt`:

1. **Passos 1e-3, 1e-4 e 1e-5** (J0 e J1): os valores singulares coincidem em 3 algarismos. Exemplos: J0, $\sigma_7/|v|=4{,}43\text{e-}3$; J1, 9,96e-4 a 9,97e-4. Iguais aos do relatório.
2. **Bico em $\chi_\perp=0$ no ponto alinhado J0.** O teste do relatório (h) foi feito só em $\vec\chi_B=0$. Aqui, nas quatro direções no plano:
   - $|D_+-D_-|/|D_+|$ cai proporcional a $h$, de 9e-4 a 9e-6;
   - a segunda diferença é constante, de 0,18 a 0,26, nos três passos.

   Não há bico: o posto 7 em J0 não é artefato.
3. **Variante de modelagem `zerar_m0=True`.** $J$ muda de 1% a 11%, e o menor valor singular de 0,82 a 1,00 vezes. A direção mais fraca nas coordenadas físicas não muda: componente de $\bar\varphi$ 0,97–0,98 em J1 e 0,96 em J2.
4. **Pontos novos:**

   | Ponto | $\sigma_7/\lvert v\rvert$ | Direções > 1e-2 |
   |---|---|---|
   | N1 (quase alinhado, $\chi_\perp=0{,}02$) | 3,5e-3 | 5 |
   | N2 ($q=3{,}8$, $\lvert\chi\rvert\approx0{,}7$) | 3,6e-4 | 6 |
   | N3 ($q=1{,}1$, $\chi_\perp\approx0{,}7$) | 2,1e-3 | 5 |

   Posto 7 em todos. Em N2, $\sigma_7$ fica abaixo de 1e-3: a sétima direção é ainda mais fraca perto da borda do domínio.

**Ressalva.** Posto 7 para um mapa genérico de $\mathbb R^7$ em $\mathbb R^{88}$ é o esperado. O resultado informativo é o espectro: 5–6 direções acima de 1% e uma ou duas abaixo do erro de modelo. Continua não testado se há fibras globais (seção 6 do relatório).

## 6. Hierarquia $|\chi_{A\perp}|\gg|\chi_{B\perp}|>\Delta\varphi>\bar\varphi$ (H10.5) — parcial

Valores singulares nos 4 graus no plano (`ver_D6_jacobiano.txt`, item 4):

| Ponto | Valores singulares | Observação |
|---|---|---|
| N2 | 2,3e-1 ($\lvert\chi_{A\perp}\rvert$) · 1,6e-2 ($\lvert\chi_{B\perp}\rvert$) · 9,0e-3 ($\Delta\varphi$) · 3,4e-4 ($\bar\varphi$, 0,996) | hierarquia confirmada |
| N3 | 4,1e-2 · 3,7e-2 · 5,4e-3 · 2,2e-3 | as duas primeiras misturam os dois módulos; não há $\lvert\chi_{A\perp}\rvert\gg\lvert\chi_{B\perp}\rvert$ |
| N1 | 7,2e-2 · 1,8e-2 · 2,4e-4 · 1,0e-4 | direção dominante (0,81; 0,58): a combinação dos módulos, não $\chi_{A\perp}$ sozinho |

Em N3 ($q\approx1$ com spins no plano comparáveis), a mais fraca é ainda $\bar\varphi$ (0,96). Em N1, os dois azimutes são fracos porque o efeito deles escala com $|\chi_\perp|=0{,}02$.

**Conclusão:**
- "$\bar\varphi$ é a direção mais fraca" vale em 6 de 7 pontos (exceção J4, já declarada no relatório).
- "$|\chi_{A\perp}|\gg|\chi_{B\perp}|$" não é universal: falha com $q\approx1$ e spins comparáveis.
- A hierarquia do relatório deve ser apresentada como dependente da configuração (dominada por $q$ e pela razão dos spins), não como ordem geral.

## 7. Achado lateral: o nível A do CCE e de `binarias` erra desl40 por faltarem (3,1), (4,1), (4,2) — confirmado em módulo, com o sinal corrigido

Quadratura direta e independente (`ver_D6_modos.txt`; mesma janela $f_{22}\ge0{,}007$, todos os $m\neq0$ com $\ell\le4$, contra o mesmo conjunto sem os seis modos):

| Sistema | $\ell=4$: (todos − sem)/sem | Relatório (S7 − S7c) | $\ell=2$ |
|---|---|---|---|
| $q=1$, $\chi=(0,0)$ | +11,2% | +11% | +0,37% |
| $q=1{,}2$, $(0{,}3;\ -0{,}2)$ | +12,0% | +12% | +0,39% |
| $q=2$, $(-0{,}5;\ 0{,}5)$ | +2,4% | +2,4% | +0,13% |
| $q=3$, $(0{,}5;\ 0{,}3)$ | +45,9% | +46% | +0,26% |
| $q=3{,}9$, $(0;\ 0)$ — caso novo | **−13,1%** | — | +0,12% |

- Os números do relatório se reproduzem por um caminho sem `memorias.py`.
- A frase da seção 4.1(b), "subestima o deslocamento $\ell=4$ em ~10% ou mais", não é geral:
  - em $q=3{,}9$ sem spin, o sinal se inverte;
  - em $q=2$, $\chi=(-0{,}5;0{,}5)$, o efeito é só 2,4%.
- Correção: "erra desl40 de −13% a +46% conforme $q$ e os spins". A conclusão prática, de que o $\ell=4$ do nível A de `binarias` tem erro de modelagem de dezenas de por cento, fica mais forte. Ela afeta outras linhas que usam desl40 (L00, L13–L15).

## 8. Modos $m=0$ do NRSur7dq4 sem memória (H10.2) — confirmado nos alinhados

O $|h_{20}(t_\text{fim})|$ inercial (igual ao coorbital nos alinhados) vale de 1,1e-5 a 5,9e-5 nos 5 sistemas. O $\max|h_{20}|$ fica entre 6,7e-3 e 2,4e-2. Não há degrau de memória: a memória esperada é 0,03–0,09, segundo o relatório.

Não verifiquei os precessantes no referencial coorbital.

## 9. Observador: "4 números de memória mensuráveis" (H10.7) — parcial

- **Posto 4.** É trivial: a matriz tem 4 linhas e 10 colunas genéricas. "Confirmada numericamente" acrescenta pouco.
- **"Mensuráveis".** Conflita com os itens 4 e 5 da revisão da etapa 6, que o relatório cita mas não aplica:
  - $\int h$ da memória não é uma grandeza bem definida (o CM do código é o $\Delta K$ de Nichols, e $\int h_+du$ diverge);
  - o CM é degenerado com $t_0$;
  - um interferômetro mede 2 números, como o próprio relatório reconhece.

  Correção: o observador tem 4 combinações de multipolos de memória, das quais 2 são mensuráveis por um detector, e mesmo essas com as degenerescências acima.
- **"Assinatura de precessão" $|\Delta h_\times|/|\Delta h_+|$.** Não é invariante sob $\psi$: sob $\psi\to\psi+\delta$, o par gira de $2\delta$, e a razão vai de 0 a ∞. Com a memória sozinha, onde $\psi$ é desconhecido (como o relatório supõe ao contar parâmetros), essa razão não é observável. Ela só tem sentido se $\psi$ vier da onda oscilatória. Só o ângulo relativo entre $\Delta h$ e o outro par é invariante.

## 10. Não verificado

- H10.6, a parte secular pelo modelo do eixo precessante (razões 0,83–1,05).
- A concordância de ~1% com o CCE em desl20, spin30 e giro (só a parte dos modos foi refeita, item 7).
- O recuo contra o surfinBH.
- $J_\text{rad}$ contra $J_i-J_f$. Os números desse item estão em `exp33_validacao.txt` (c). O desvio absoluto chega a 2e-2 de $|J|\approx0{,}2$–$0{,}4$, cerca de 1,5–3° na direção. Isso é atribuível ao $J_i$ PN 2PN, mas mostra que $J_\text{rad}$ não foi validado melhor que alguns graus por um caminho independente.

## 11. Literatura e originalidade (busca curta, API do arXiv, 2026-11-01)

**Consultas** (`export.arxiv.org/api/query`):
- `memory AND Poincare-Hopf`: 3 resultados, nenhum de ondas gravitacionais;
- `abs:"gravitational wave memory" AND abs:zeros`: 9, nenhum sobre zeros no céu;
- `abs:memory AND abs:umbilic`: 1, irrelevante;
- `abs:"polarization singularities" AND abs:gravitational`: 1, o formalismo eth de 1997;
- `abs:"displacement memory" AND abs:precessing`: 2, arXiv:2506.08888 (citado) e **arXiv:2607.04909** (2026, análise cumulativa com o (2,0) completo; não citado no relatório, deve ser acrescentado);
- `abs:memory AND abs:precessing AND abs:Fisher`: 0;
- `abs:memory AND abs:"sky pattern"`: arXiv:1605.01273 (citado) e 2107.02208;
- `abs:"tendex" AND abs:memory`: 0.

**Conclusão.** Não encontrei trabalho sobre zeros, índices ou eixos ópticos do padrão de memória no céu, nem sobre o posto do jacobiano das memórias de precessão. A alegação "não encontrado" do relatório se sustenta, dentro dos limites de uma busca curta.

A matemática dos eixos ópticos é clássica (óptica cristalina). A divisão de um ponto +1 em dois +1/2 é a de Berry, Dennis & Lee (2004), citada.

## 12. Tabela de status revisada

| Id | Status no relatório | Status após verificação | Motivo |
|---|---|---|---|
| H10.1 | confirmada numericamente (parcial) | não reverificada; achado lateral confirmado com sinal corrigido | item 7 |
| H10.2 | confirmada numericamente | confirmada (alinhados) | item 8 |
| H10.3 | refutada | refutada (confirmado) | item 4 |
| H10.4 | confirmada numericamente | confirmada; robusta a passo, bico e variante | item 5 |
| H10.5 | confirmada em J1, J2, J5 | confirmada para "$\bar\varphi$ mais fraca" (6/7 pontos); hierarquia $\lvert\chi_{A\perp}\rvert\gg\lvert\chi_{B\perp}\rvert$ refutada como geral (N3, N1) | item 6 |
| H10.7 | confirmada numericamente | parcial: contagem certa, "mensuráveis" e "assinatura $\lvert\Delta h_\times\rvert/\lvert\Delta h_+\rvert$" não se sustentam | item 9 |
| H11.1 | confirmada matematicamente | confirmada | item 3 |
| H11.3 | confirmada numericamente | parcialmente refutada: $\sqrt\varepsilon$ só para $\lvert m\rvert=2$; $m$ ímpar dá $O(\varepsilon)$, e $m=3$ dá 4 zeros com um de −1/2 | item 2 |
| H11.4 | confirmada matematicamente | confirmada (derivação e numérico independentes); matemática clássica de óptica cristalina | item 1 |
| H11.5 | refutada (segue $e_Q$) | confirmada a refutação; $e_Q$ depende do peso (só (2,±2): máximo 10°) | item 4 |
