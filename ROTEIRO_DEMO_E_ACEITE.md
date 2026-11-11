# Roteiro de demonstração e aceite — MBF Stock

**Versão de referência:** branch `entrega0911`. **Finalidade:** comprovar os requisitos perante o professor, sem confundir teste automatizado com aceite humano.

## Preparação
1. Executar `python -m unittest discover -v` e registrar o resumo, data e commit.
2. Em ambiente de demonstração com dados de teste, executar `python server.py` e abrir `http://localhost:8000`.
3. Preparar contas de administrador e operador, sem revelar senhas no vídeo.
4. Usar peças de teste ou um backup; não alterar o banco de produção da metalúrgica.

## Roteiro para vídeo (aproximadamente 5–8 minutos)
| Tempo sugerido | Requisito | Demonstração | Evidência esperada |
|---|---|---|---|
| 0:00–0:40 | RF01 | Login válido e tentativa inválida | Acesso correto; credenciais inválidas recusadas |
| 0:40–1:10 | RF02 | Entrar como operador e comparar com administrador | Ações administrativas restritas |
| 1:10–1:55 | RF03 | Cadastrar peça de teste, editar e demonstrar validação | Peça salva; campos inválidos recusados |
| 1:55–2:20 | RF04 | Buscar código e filtrar categoria | Lista filtrada |
| 2:20–3:00 | RF05 | Operador solicita quantidade com comentário | Solicitação pendente |
| 3:00–3:45 | RF06 | Administrador aprova uma solicitação e rejeita outra | Status e justificativa registrados |
| 3:45–4:20 | RF07 | Comparar saldo antes e depois; testar insuficiência | Baixa correta; saldo negativo impedido |
| 4:20–4:50 | RF08 | Abrir histórico | Movimento associado à aprovação |
| 4:50–5:20 | RF09 | Abrir dashboard | Indicadores coerentes com dados |
| 5:20–5:50 | RF10 | Exportar e abrir CSV | Arquivo com valores corretos |
| 5:50–6:40 | RF11 | Administrador editar usuário; operador tentar acesso restrito | Permissões e atualização verificadas |

## Registro de aceite
Para cada RF, registrar **data, resultado esperado, resultado observado, evidência (print/vídeo), aprovado/reprovado, responsável**. Marcar um RF como aceito somente após conferir seus critérios. A meta de 75% corresponde a **pelo menos 9 dos 11 RFs**, mas não deve ser declarada atingida sem os registros.

## Arquitetura e limitações
O backend usa `http.server` com módulos de segurança, estoque e persistência; não é um MVC estrito. SQLite é justificável para protótipo acadêmico e demonstração local, mas requer avaliação de concorrência, backup, segurança e implantação antes de uso corporativo. ViaCEP consulta dados no frontend e não garante persistência de endereço. O modelo BPMN editável está em `docs/processo_retirada.bpmn` e deve ser renderizado em editor BPMN para a monografia.

## Verificação de entrega
- [ ] GitHub Actions da versão final aprovado
- [ ] Todos os testes automatizados da branch final aprovados
- [ ] Vídeo gravado sem credenciais expostas
- [ ] Pelo menos 9 RFs aceitos com evidência e responsável
- [ ] BPMN visual exportado e incluído na monografia
- [ ] Sumário, paginação, figuras e referências da monografia revisados no Word
- [ ] README, matriz e monografia descrevem a mesma versão
- [ ] Backup de dados realizado antes de qualquer demonstração que altere registros

**Atenção:** este roteiro não é uma declaração de homologação. Ele define as provas necessárias para concluir a entrega.
