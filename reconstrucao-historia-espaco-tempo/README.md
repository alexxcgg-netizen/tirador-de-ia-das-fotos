# Reconstrução da história do espaço-tempo por meio da memória gravitacional

Projeto de pesquisa: quanto da história de um sistema físico pode ser reconstruído a partir do
que ele deixa nas ondas gravitacionais, em especial nas memórias gravitacionais (deslocamento,
spin, centro de massa e giroscópica)?

**Estado em 31/10/2026:** etapas 1 a 5 concluídas, com código verificado e cinco experimentos
numéricos reproduzíveis. Próximo passo sugerido no fim de `06_conclusoes_e_limites.md`.

## Resultado principal

**As quatro memórias são medidas de "intensidade", não de "campo".** Na ordem em que são
calculadas, as partes que vêm da radiação dependem da história só por duas matrizes integradas
no tempo: os momentos espectrais de primeira e segunda ordem da matriz espectral cruzada dos
modos, $\int\omega\,\tilde h\tilde h^\dagger$ e $\int\omega^2\,\tilde h\tilde h^\dagger$
(Teorema 1, `03_problema_concreto.md`). Consequências:

- Qualquer filtro de fase comum a todos os modos preserva as quatro memórias no céu inteiro. Daí
  saem infinitas histórias distintas com as mesmas memórias. Exemplos construídos: um corpo que
  gira acelerando × o mesmo desacelerando (anti-*chirp*), uma explosão × duas de meia potência,
  fonte de massa × fonte com mistura de massa e corrente, sinal limpo × disperso. As quatro memórias
  coincidem em 1e-15, e as formas de onda são diferentes (sobreposição de 0,22 a 0,71). A fonte
  de dualidade é a exceção: numa só direção, só se separa pela polarização da memória em relação à oscilação.
- Na ordem cúbica a igualdade quebra pouco (1e-7 a 1e-4) e pode ser restaurada em ~1e-8 ajustando
  só a fase.
- A forma de onda completa separa essas histórias, e a memória é um subproduto dela no vácuo. O
  valor próprio da memória é outro: testa a RG não linear e mede os canais que não são ondas
  gravitacionais (neutrinos, luz, matéria ejetada).

**Limites rigorosos da reconstrução** (`06_conclusoes_e_limites.md`): nada de dentro de horizontes;
nada do que cai no horizonte (ilustrado numericamente com precisão de 1e-25); nenhuma dinâmica
esférica (Birkhoff); nenhum multipolo estático; reconstrução pela torre de memórias com ruído
amplificado por $\sim e^{a^2/4}$; e nenhum algoritmo, inclusive de IA, extrai mais informação do
que os dados têm.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `01_revisao_critica.md` | Etapa 1: a equação central, simplificações perigosas, os nove tópicos anteriores, o que é conhecido e o que é novo |
| `02_caminhos.md` | Etapa 2: abordagens independentes, verificação de originalidade, conexões entre áreas |
| `03_problema_concreto.md` | Etapa 3: Teoremas 1 e 2, fontes degeneradas, comparação de formas de onda, ordem cúbica |
| `04_brechas.md` | Etapa 4: fase, observáveis novos, multimensageiros, informação, simetrias, polarização |
| `05_experimentos.md` | Etapa 5: os cinco experimentos, números e como rodar |
| `06_conclusoes_e_limites.md` | Resposta à pergunta central, limites, previsões verificáveis, problemas em aberto |
| `referencias.md` | ~80 referências verificadas online, com correções de atribuição |
| `codigo/` | `harmonicos.py`, `memorias.py`, `fontes.py` e os experimentos `exp01`–`exp05` |
| `resultados/` | saídas de texto dos experimentos |
| `figuras/` | gráficos gerados pelos experimentos |

## Rótulos usados em todos os textos

- **[E]** estabelecido na literatura (com referência);
- **[D]** derivado ou verificado nesta pesquisa (elementar, mas não encontrado na literatura nessa forma);
- **[H]** hipótese;
- **[S]** especulação.

"Não encontrado na literatura" significa "após busca razoável em 31/10/2026" (`02_caminhos.md` §9),
não "inédito garantido".

## Como reproduzir

```bash
pip install numpy matplotlib mpmath
cd codigo
python3 exp01_verificacao.py          # confere o código contra Favata 2009, Nichols 2017 e 2018
python3 exp02_fontes_degeneradas.py   # etapa 3: cinco histórias, mesmas memórias
python3 exp03_ordem_cubica.py         # etapa 3: o que acontece na ordem cúbica (~10 min)
python3 exp04_horizonte.py            # limite: radiação que só cai no buraco negro
python3 exp05_torre_momentos.py       # limite: reconstruir a onda pela torre de memórias
```

![Cinco histórias, mesma memória](figuras/e3_formas_de_onda.png)
