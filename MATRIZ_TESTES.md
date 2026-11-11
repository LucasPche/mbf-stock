# Matriz preliminar de testes — MBF Stock

Os resultados abaixo representam cenários efetivamente cobertos pelos testes automatizados, **não a aprovação integral de cada requisito**. A avaliação final de cada RF depende também de teste manual e evidências anexadas.

| Requisito | Evidência automatizada disponível | Situação do requisito completo |
|---|---|---|
| RF01 — Login | Login correto/incorreto; logout; sessão bloqueada | Parcialmente verificado |
| RF02 — Perfis | Operador impedido de acessar usuários e criar peças | Parcialmente verificado |
| RF03 — Peças | Cadastro, edição, ajuste e bloqueio de exclusão com histórico | Parcialmente verificado |
| RF04 — Busca e filtros | Não coberto na interface | Não verificado |
| RF05 — Solicitações | Cadastro válido e entradas inválidas | Parcialmente verificado |
| RF06 — Aprovação/rejeição | Aprovação e prevenção de dupla aprovação; rejeição ainda não testada | Parcialmente verificado |
| RF07 — Saldo e saída | Baixa de saldo; insuficiência de saldo | Parcialmente verificado |
| RF08 — Movimentações | Registro de entrada de ajuste e consulta de histórico | Parcialmente verificado |
| RF09 — Dashboard | Não coberto nos testes atuais | Não verificado |
| RF10 — CSV | Não coberto nos testes atuais | Não verificado |
| RF11 — Usuários | Bloqueio de acesso; operações administrativas ainda não completas | Parcialmente verificado |

## Evidências a anexar antes da entrega

Para cada caso de teste, registrar identificador, pré-condição, passos, resultado esperado, resultado observado, data, commit Git e captura de tela ou saída do teste. Os comandos de `coverage` verificam instruções de código, não substituem a matriz de requisitos.

## Execução complementar em 11/11/2026

- Teste de **rejeição de solicitação**: HTTP 200, pedido alterado para `rejeitado`, saldo da peça preservado — aprovado em banco temporário.
- Teste de **integridade referencial**: `PRAGMA foreign_keys = 1` e `PRAGMA foreign_key_check` sem violações no banco temporário — aprovado.
- Teste de **rota inexistente**: resposta HTTP 404 — aprovado.
- **Total:** 27 testes automatizados aprovados; cobertura de instruções de `server.py`: 65% (498 instruções, 176 não cobertas).

**Limite da evidência:** não há neste relatório capturas de interface, homologação em Windows ou aceite completo dos 11 requisitos. Não classificar RF06 ou RNF04 como integralmente aprovados apenas com os cenários acima.
