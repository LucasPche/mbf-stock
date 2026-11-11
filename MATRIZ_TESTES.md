# Matriz de Testes — MBF Stock

## 1. Objetivo

Este documento apresenta os principais requisitos funcionais do MBF Stock e os testes realizados para verificar o funcionamento do sistema.

Os testes automatizados foram desenvolvidos utilizando Python e a biblioteca `unittest`. Também foram realizadas verificações manuais das principais telas da aplicação.

A matriz permite acompanhar quais funcionalidades possuem testes e quais ainda precisam de validação complementar.

## 2. Matriz de requisitos funcionais

| Requisito | Funcionalidade | Testes e verificações realizados | Situação |
|---|---|---|---|
| RF01 | Login e autenticação | Login válido e inválido, logout e controle de sessão | Parcialmente validado |
| RF02 | Perfis de acesso | Bloqueio de operações administrativas para operadores | Parcialmente validado |
| RF03 | Cadastro de peças | Cadastro, edição, ajuste de quantidade e restrições de exclusão | Parcialmente validado |
| RF04 | Busca e filtros | Consulta visual da lista de peças; filtros ainda sem evidência específica | Pendente de validação |
| RF05 | Solicitações de materiais | Registro de solicitações válidas e tratamento de entradas inválidas | Parcialmente validado |
| RF06 | Aprovação e rejeição | Aprovação, rejeição, atualização do estado e prevenção de análise duplicada | Parcialmente validado |
| RF07 | Controle de saldo | Baixa de estoque e bloqueio de retirada sem saldo suficiente | Parcialmente validado |
| RF08 | Histórico de movimentações | Registro de entradas e saídas e consulta do histórico | Parcialmente validado |
| RF09 | Dashboard | Visualização manual dos indicadores principais | Parcialmente validado |
| RF10 | Exportação CSV | Funcionalidade ainda sem evidência de teste específica | Pendente de validação |
| RF11 | Gerenciamento de usuários | Verificação de permissões e bloqueio de acesso não autorizado | Parcialmente validado |

A situação apresentada considera as evidências disponíveis até o momento. A validação completa de cada requisito depende da execução dos cenários correspondentes e da confirmação dos resultados esperados.

## 3. Testes automatizados

Os testes verificam diferentes partes do sistema, incluindo:

- Autenticação e encerramento de sessões.
- Controle de permissões dos usuários.
- Cadastro e edição de peças.
- Registro de movimentações de estoque.
- Solicitações de materiais.
- Aprovação e rejeição de solicitações.
- Prevenção de retirada sem saldo suficiente.
- Validação de dados e identificadores.
- Integridade referencial do banco.
- Acesso a arquivos privados.
- Revogação de sessões de usuários desativados.
- Funções dos módulos de estoque, segurança e persistência.
- Auditoria do banco de dados.

### Resultado da execução

**Data:** 11/11/2026

| Indicador | Resultado |
|---|---|
| Testes executados | 45 |
| Testes aprovados | 45 |
| Falhas | 0 |
| Erros | 0 |
| Resultado geral | Aprovado na execução automatizada |

Os testes foram executados localmente no Windows, utilizando bancos temporários para as verificações automatizadas.

## 4. Verificações manuais

Além dos testes automatizados, foram realizadas verificações na interface do sistema.

| Área | Verificação observada |
|---|---|
| Login | Acesso ao sistema com credenciais válidas |
| Dashboard | Exibição de indicadores gerais do estoque |
| Estoque | Exibição das peças cadastradas e das quantidades |
| Solicitações | Consulta de solicitações registradas |
| Histórico | Visualização de entradas, saídas e informações das movimentações |
| Interface | Exibição literal de texto contendo tags HTML em um registro de teste |

Essas verificações confirmam os comportamentos observados durante a execução local, mas não substituem os testes completos de cada requisito.

## 5. Testes de integridade e segurança

Foram realizados testes para verificar situações que poderiam causar inconsistências ou permitir operações indevidas.

Entre os cenários avaliados estão:

**Controle de estoque:** o sistema impede retiradas quando a quantidade disponível é insuficiente.

**Solicitações:** uma solicitação já analisada não pode ser aprovada novamente, evitando uma segunda baixa do estoque.

**Integridade referencial:** as conexões SQLite habilitam as chaves estrangeiras, e os testes verificam sua aplicação em bancos temporários.

**Sessões:** operações protegidas exigem autenticação e permissões adequadas.

**Validação de dados:** identificadores inválidos e requisições JSON malformadas são tratados pelo servidor.

**Arquivos privados:** o servidor possui verificações para impedir acesso HTTP a arquivos que não devem ser disponibilizados publicamente.

## 6. Cobertura de código

A cobertura dos testes pode ser medida utilizando a biblioteca `coverage`.

Para executar:

```powershell
python -m coverage run --source=server,security_service,inventory_service,database_repository -m unittest discover
python -m coverage report -m
```

O relatório geral obtido anteriormente apresentou 80% de cobertura, incluindo arquivos de testes.

O percentual específico dos módulos da aplicação deve ser confirmado com o comando acima.

A cobertura de código representa a proporção de instruções executadas durante os testes. Esse resultado não equivale diretamente ao percentual de requisitos funcionais aprovados.

## 7. Validação dos requisitos

O projeto possui 11 requisitos funcionais identificados de RF01 a RF11.

Para atingir um índice de aprovação de pelo menos 75%, é necessário validar integralmente no mínimo 9 desses requisitos.

A matriz atual registra os cenários já verificados e identifica as funcionalidades que ainda precisam de testes complementares.

A aprovação dos testes automatizados representa uma evidência importante de funcionamento, mas não determina, por si só, a aprovação integral de todos os requisitos.

## 8. Considerações finais

Os testes realizados no MBF Stock contribuíram para identificar e corrigir problemas relacionados à autenticação, permissões, movimentações de estoque e integridade dos dados.

A execução automatizada mais recente apresentou 45 testes aprovados, sem falhas ou erros.

A utilização de testes automatizados, verificações manuais e uma matriz de requisitos permite acompanhar a qualidade do sistema e identificar os pontos que ainda precisam de validação.