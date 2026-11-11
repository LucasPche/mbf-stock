# Manual do usuário — MBF Stock

**Versão:** revisão de 10–11/11/2026. **Ambiente:** demonstração local acadêmica.

## 1. Pré-requisitos e inicialização

1. Instale Python 3.10 ou superior.
2. Extraia os arquivos em uma pasta local e abra um terminal nessa pasta.
3. Antes da primeira execução em banco novo, configure as variáveis `MBF_ADMIN_PASSWORD` e `MBF_OPERADOR_PASSWORD` com senhas próprias. Não compartilhe credenciais no repositório.
4. Execute `python server.py` e acesse `http://localhost:8000` no navegador.
5. Entre com a conta correspondente ao perfil. Para banco novo, os usuários iniciais são `admin` e `operador`; suas senhas são as configuradas nas variáveis de ambiente.

**Atenção:** não exponha o servidor diretamente à internet. O sistema utiliza `http.server`, sessões em memória e SQLite, e não passou por homologação de produção.

## 2. Perfis

- **Administrador:** gerencia peças, usuários, pedidos de cadastro e análise de solicitações.
- **Operador:** consulta materiais e registra solicitações de retirada. Operações administrativas são verificadas também no servidor.

## 3. Consulta e manutenção de estoque

Após autenticar, abra a área de estoque para consultar as peças. Utilize os filtros disponíveis para localizar materiais. Com perfil de administrador, preencha o formulário de cadastro e informe código, nome, categoria, localização e quantidades. Quantidade e estoque mínimo devem ser números válidos e não negativos. Para editar, selecione o registro e confirme a alteração. Uma mudança de 10 para 15 unidades gera movimentação de entrada de 5; de 15 para 12 gera saída de 3. Uma peça com histórico vinculado não pode ser excluída livremente.

## 4. Solicitações de retirada

O operador escolhe uma peça, informa uma quantidade positiva e registra a solicitação. O pedido fica pendente até análise. O administrador pode aprovar ou rejeitar. A aprovação somente reduz o saldo quando existe quantidade suficiente; a rejeição não altera o estoque. Solicitações já analisadas não devem ser processadas novamente.

## 5. Usuários, histórico e relatórios

O administrador consulta e gerencia contas e pedidos de cadastro na área correspondente. O histórico registra operações relevantes e permite verificar entradas e saídas. O painel apresenta indicadores de estoque; a interface disponibiliza exportação CSV. Os resultados de indicadores, filtros e CSV ainda requerem conferência manual de aceite antes da entrega.

## 6. ViaCEP e privacidade

A interface consulta o serviço externo ViaCEP para preencher visualmente campos de endereço do fornecedor. Na versão revisada, esse endereço não integra o modelo persistido de fornecedores no SQLite; portanto, não se deve afirmar que a consulta armazena endereço. Utilize apenas dados fictícios na demonstração. Não coloque bancos, tokens, logs ou senhas no GitHub.

## 7. Encerramento e problemas comuns

Utilize a opção de sair para encerrar a sessão. Sessões expiram após aproximadamente 30 minutos de inatividade. Se o acesso falhar, confirme o endereço local e se o servidor está em execução. Erros de permissão exigem perfil autorizado. Requisições inválidas devem retornar mensagem de erro sem alterar os dados. Para registrar evidências, anote o caso de teste, resultado observado e captura sem informações sensíveis.

## 8. Testes de verificação

Na pasta do projeto, execute:

```powershell
python -m pip install coverage
python -m unittest discover -v
python -m coverage run --source=server -m unittest discover -q
python -m coverage report
```

A suíte usa banco temporário para testes HTTP; a cobertura de instruções não substitui o aceite manual de todos os requisitos funcionais.
