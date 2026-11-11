# Matriz de Testes — MBF Stock

# 1. Objetivo

Este documento apresenta os requisitos funcionais do MBF Stock, os testes automatizados e as verificações manuais realizados para avaliar o funcionamento do sistema.

Os testes automatizados foram desenvolvidos em Python, utilizando a biblioteca `unittest`. A cobertura de código foi medida com a ferramenta `coverage`.

A matriz relaciona os requisitos às evidências disponíveis, permitindo identificar os cenários aprovados e aqueles que ainda necessitam de validação complementar.

# 2. Matriz de requisitos funcionais

| Requisito | Funcionalidade | Testes e evidências | Situação |
|---|---|---|---|
| RF01 | Login e autenticação | Testes de credenciais válidas e inválidas, sessões e logout; acesso manual com contas distintas | Validado nos cenários executados |
| RF02 | Perfis de acesso | Testes automatizados de autorização; verificação manual das opções disponíveis para administrador e usuário comum | Validado nos cenários executados |
| RF03 | Cadastro de peças | Testes automatizados de cadastro, edição, ajuste de quantidade e restrições de exclusão | Parcialmente validado |
| RF04 | Busca e filtros | Busca por código MBF-002 e filtragem por categoria Aço, com quatro peças correspondentes | Validado nos cenários executados |
| RF05 | Solicitações de materiais | Criação manual da solicitação #4, quantidade de uma barra, com comentário; testes automatizados de entradas válidas e inválidas | Validado nos cenários executados |
| RF06 | Aprovação e rejeição | Aprovação manual da solicitação #4, atualização do status e registro da resposta; testes automatizados de rejeição e análise duplicada | Validado nos cenários executados |
| RF07 | Controle de saldo | Baixa da MBF-002 de 18 para 17 barras após aprovação; testes automatizados de saldo insuficiente | Validado nos cenários executados |
| RF08 | Histórico de movimentações | Registro manualmente confirmado da saída de uma barra, associada à solicitação #4; testes de movimentações | Validado nos cenários executados |
| RF09 | Dashboard | Conferência dos indicadores, distribuição por categoria e atualização de solicitações pendentes de 0 para 1 e novamente para 0 | Validado nos cenários executados |
| RF10 | Exportação CSV | Exportação e abertura em planilha dos relatórios de estoque e itens críticos; conferência de quantidades e faltas | Validado nos cenários executados |
| RF11 | Gerenciamento de usuários | Visualização de contas, edição do setor do Operador MBF e verificação das permissões na interface | Parcialmente validado |

**Critério de classificação:** a expressão "Validado nos cenários executados" indica que os testes descritos apresentaram os resultados esperados. Não significa que todos os cenários possíveis do requisito tenham sido executados.

# 3. Testes automatizados

Os testes automatizados abrangem:

- Autenticação, senhas e sessões.
- Permissões de acesso.
- Cadastro e edição de peças.
- Solicitações e decisões administrativas.
- Movimentações de estoque.
- Bloqueio de retiradas sem saldo suficiente.
- Validação de dados e identificadores.
- Integridade referencial do banco.
- Proteção de arquivos privados.
- Revogação de sessões.
- Serviços de estoque, segurança e persistência.
- Auditoria do banco de dados.

# 3.1. Resultado da execução

**Data:** 11/11/2026

| Indicador | Resultado |
|---|---|
| Testes executados | 45 |
| Testes aprovados | 45 |
| Falhas | 0 |
| Erros | 0 |
| Tempo da execução com cobertura | 17,010 segundos |
| Resultado geral | Aprovado |

Comando utilizado:

```powershell
python -m unittest discover -v
```

A execução apresentou a mensagem `OK`, sem falhas ou erros.

# 4. Verificações manuais

# 4.1. Busca e filtros

Foi realizada uma busca pelo código `MBF-002`, retornando a peça correspondente.

Também foi testado o filtro da categoria **Aço**, que apresentou quatro peças cadastradas nessa categoria.

A nomenclatura da categoria foi padronizada de `Acao` para `Aço`, com atualização dos registros existentes e criação prévia de backup do banco de dados.

**Resultado:** aprovado nos cenários observados.

# 4.2. Dashboard

Os indicadores foram comparados com os dados apresentados no estoque e nos relatórios.

| Indicador | Valor inicial |
|---|---:|
| Peças cadastradas | 8 |
| Peças abaixo do mínimo | 4 |
| Solicitações pendentes | 0 |
| Cadastros pendentes | 0 |

A distribuição por categoria apresentou:

| Categoria | Quantidade |
|---|---:|
| Aço | 4 |
| Consumível | 2 |
| Peça | 2 |
| **Total** | **8** |

Após o envio da solicitação #4, o indicador de solicitações pendentes passou de 0 para 1. Após a aprovação, retornou para 0.

**Resultado:** aprovado nos cenários observados.

# 4.3. Solicitações e aprovação

Foi criada a solicitação #4 para a peça MBF-002, com quantidade de uma barra e comentário de validação.

A solicitação foi registrada inicialmente com status pendente.

Após a aprovação administrativa, o sistema apresentou:

- Status aprovado.
- Resposta do administrador registrada.
- Redução das solicitações pendentes de 1 para 0.
- Baixa de uma barra no estoque.

**Resultado:** aprovado no cenário observado.

# 4.4. Controle de estoque

A peça MBF-002 apresentava 18 barras antes da aprovação.

Após a aprovação da retirada de uma barra, a quantidade disponível passou para 17 barras.

O sistema manteve a indicação de estoque baixo, considerando o mínimo cadastrado de 25 barras.

**Resultado:** aprovado no cenário observado.

# 4.5. Histórico de movimentações

O histórico apresentou o registro correspondente à aprovação da solicitação #4:

| Campo | Valor observado |
|---|---|
| Operação | SAÍDA |
| Peça | Barra redonda 1045 1 pol |
| Quantidade | 1 |
| Usuário | Administrador MBF |
| Referência | Solicitação #4 aprovada |
| Data registrada | 11/11/2026, 17:06:15 |

Também foram observados registros anteriores de entradas e saídas.

**Resultado:** aprovado no cenário observado.

# 4.6. Exportação CSV

Foram exportados dois relatórios:

**Relatório de estoque:** apresentou oito peças cadastradas, com seus respectivos dados de estoque.

**Relatório de itens críticos:** apresentou quatro itens abaixo da quantidade mínima.

As faltas observadas foram:

| Código | Quantidade | Mínimo | Falta |
|---|---:|---:|---:|
| MBF-002 | 18 | 25 | 7 |
| MBF-003 | 12 | 20 | 8 |
| MBF-005 | 9 | 10 | 1 |
| LOG-001 | 1 | 5 | 4 |

Os valores correspondem ao momento da exportação, anterior à aprovação da solicitação #4.

Os arquivos foram abertos em uma planilha para conferência dos dados.

**Resultado:** aprovado nos cenários básicos de exportação e conferência.

# 4.7. Gerenciamento de usuários

O administrador visualizou as contas cadastradas, seus perfis, setores e estados.

Foi realizada uma edição no cadastro do Operador MBF, alterando o setor de `Producao` para `Produção`.

Após salvar, o cadastro apresentou o novo setor, mantendo o perfil de usuário comum e o status ativo.

**Resultado:** edição básica aprovada. Permanecem pendentes outros cenários de gerenciamento.

# 4.8. Permissões do usuário comum

Foi realizado login com uma conta de perfil comum.

O menu apresentou as opções Dashboard, Estoque e Solicitações, sem disponibilizar os menus administrativos.

Na listagem de estoque, o usuário comum visualizou o botão Solicitar, mas não os botões Editar e Excluir.

**Resultado:** restrições da interface aprovadas nos cenários observados.

A segurança das rotas administrativas também é abordada nos testes automatizados, sendo distinta da simples ocultação de botões.

# 5. Testes de integridade e segurança

Os testes automatizados contemplam verificações de integridade e proteção da aplicação.

**Controle de saldo:** prevenção de retiradas quando não existe quantidade suficiente.

**Solicitações:** prevenção de nova aprovação de solicitações já analisadas.

**Integridade referencial:** verificação da aplicação de restrições de chaves estrangeiras em bancos temporários.

**Sessões e permissões:** exigência de autenticação e autorização nas operações protegidas.

**Validação de entradas:** tratamento de identificadores inválidos e dados malformados.

**Arquivos privados:** verificações para impedir o acesso HTTP indevido a arquivos internos.

**Tratamento de HTML:** a tabela de estoque apresentou literalmente as tags HTML inseridas em um registro de teste. Esse resultado não comprova, isoladamente, a proteção de todas as áreas da interface.

# 5.1. Pontos de segurança para revisão

Recomenda-se revisar a inserção de dados dinâmicos no Dashboard, nos relatórios e nas demais áreas que utilizem construção de HTML.

Também é recomendada a execução de testes adicionais para exportação CSV, incluindo tratamento de caracteres especiais e entradas que possam ser interpretadas como fórmulas por programas de planilha.

Essas verificações complementares não estão classificadas como concluídas.

# 6. Cobertura de código

A cobertura foi medida em 11/11/2026, considerando somente os módulos da aplicação.

Comandos utilizados:

```powershell
python -m coverage run --source=server,security_service,inventory_service,database_repository,auditar_banco -m unittest discover
python -m coverage report -m
```

# 6.1. Resultado por módulo

| Arquivo | Instruções | Não cobertas | Cobertura |
|---|---:|---:|---:|
| `auditar_banco.py` | 39 | 9 | 77% |
| `database_repository.py` | 11 | 0 | 100% |
| `inventory_service.py` | 10 | 0 | 100% |
| `security_service.py` | 19 | 1 | 95% |
| `server.py` | 477 | 173 | 64% |
| **Total** | **556** | **183** | **67%** |

A execução com cobertura apresentou 45 testes aprovados.

A cobertura total da aplicação foi de **67%***, superando a meta de referência de 50%.

Esse percentual não deve ser confundido com a porcentagem de requisitos funcionais integralmente validados.

# 7. Validação dos requisitos funcionais

O projeto possui 11 requisitos funcionais, identificados de RF01 a RF11.

Para alcançar um índice mínimo de 75% de requisitos integralmente aprovados, é necessário comprovar a aprovação de pelo menos nove requisitos.

A presente matriz demonstra resultados positivos em testes automatizados e verificações manuais, mas utiliza a classificação "Validado nos cenários executados" quando não há comprovação de todos os critérios de aceitação.

Assim, o índice de aprovação integral dos requisitos ainda depende da formalização desses critérios e da confirmação dos cenários faltantes.

A quantidade de testes automatizados aprovados e a cobertura de código são indicadores complementares de qualidade, mas não substituem a avaliação individual dos requisitos.

# 8. Pendências e recomendações

Antes da entrega definitiva, recomenda-se:

1. Complementar os testes de cadastro, edição e exclusão de peças.
2. Validar os cenários restantes de gerenciamento de usuários.
3. Revisar o tratamento de HTML em todas as áreas da interface.
4. Complementar os testes de segurança dos arquivos CSV.
5. Formalizar os critérios de aceitação de cada requisito funcional.
6. Registrar as evidências finais e atualizar os resultados quando houver novas alterações no sistema.

# 9. Considerações finais

Os testes realizados demonstraram resultados positivos nas principais operações do MBF Stock, incluindo autenticação, permissões, solicitações, aprovação, movimentações de estoque, histórico, Dashboard e exportação de relatórios.

Na execução de 11/11/2026, os 45 testes automatizados foram aprovados, sem falhas ou erros, e a cobertura do código da aplicação alcançou 67%.

As verificações manuais complementaram os resultados automatizados, demonstrando o comportamento do sistema em situações reais de utilização.

A matriz permite acompanhar a evolução da validação e identificar os cenários que ainda necessitam de confirmação antes da conclusão definitiva do projeto.