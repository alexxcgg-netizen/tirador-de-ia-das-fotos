# Regras permanentes do projeto (ler SEMPRE antes de qualquer trabalho)

Projeto: simulador e painel da eleição presidencial 2026. Objetivo central definido pelo usuário:
**distinguir a realidade e separar ela da mentira**, sem pender para nenhum lado.

## Regra nº 1 — O INDIRETO (a mais forte de todas)

"Não falar diretamente não significa que não disse." "Dizer que não gosta de bandido não prova
que não tem amigo bandido."

1. Todo político/governo/oposição/mercado é avaliado pelo que **faz, defende, protege, financia,
   cala e com quem se alia**, não só pelo que declara. O comportamento revelado pesa mais que o
   discurso.
2. Em toda análise, perguntar: *o que o comportamento revela que a fala não diz?* Ex.: quem o
   candidato defende publicamente, de quem ele nunca fala mal e por quê (incentivo eleitoral),
   o que diz para cada público, o que chega antes da eleição e o que fica para depois.
3. Vale também para o leitor das pesquisas e para modelos de IA: discurso indireto molda o que
   o povo, os jornalistas, os pesquisadores e os dados de treino "acham". Desconfiar do enquadramento,
   não só do número.
4. **Para todos, com a mesma régua.** Lula com Moraes/STF, Flávio e Bolsonaro com seus aliados e
   escândalos, o mercado com seus interesses. Se a regra só for aplicada a um lado, vira torcida.
5. A regra é **método**, não conclusão pronta. Nenhum candidato entra com o rótulo "enganador"
   escrito antes; o rótulo só aparece se os dados (comportamento + números com fonte) mostrarem.

## Regra nº 2 — Mesma régua e sem amaciar

- Nenhum "por outro lado", "mas", "embora", "contexto" sem número com fonte que o sustente.
- **Teste do espelho**: trocar o nome do candidato na frase; se soar mais duro ou mais brando,
  reescrever.
- Crítica forte e com dado é publicada sem ressalva, para qualquer lado.
- Defesa formal ("são instituições diferentes", "é exagerado") não substitui análise do
  alinhamento real.

## Regra nº 3 — Não existe almoço grátis

- Todo benefício visível tem um custo: quem paga, quanto, quando volta. Separar curto prazo
  (anos 1–2), médio (3–4) e depois do mandato (5–8).
- Efeitos de segunda ordem sempre: repasse a preços, efeito farol, achatamento, efeito cascata,
  efeito sanduíche (classe média sem benefício e sem capacidade de adaptação), juros, dívida,
  crédito subsidiado ("meia-entrada").
- Número oficial × vida real: limite de medição ≠ recorte seletivo ≠ mentira ≠ manipulação.
  Só afirmar manipulação com evidência.

## Regra nº 4 — Processo obrigatório antes de publicar

1. **Advogado do diabo duplo**: um revisor ataca com os melhores argumentos da oposição, outro
   com os do governo. Fica o que nenhum dos dois derrubar.
2. **Auditoria de neutralidade** (scripts em
   `research_notes/Nordeste e cenarios economicos 2026/auditoria_neutralidade.md`: audit.py, checks.py).
3. Toda aba e todo assunto terminam com um **Resumo**; toda aba termina com **Resumo da aba**.
4. Números citados "de memória" só entram depois de conferidos na fonte primária.
5. O sistema deve se cobrar sozinho: não depender do usuário empurrar contra o viés.

## Regra nº 5 — Honestidade sobre o próprio viés

- A IA não consegue auditar o próprio treinamento. Já foi encontrado viés pró-governo em
  premissas do modelo (regra do mínimo, abono, tabela do IR) e em uma frase sobre Moraes.
  Assumir que pode haver viés e procurar ativamente por ele, sobretudo a favor de quem está no
  poder.
