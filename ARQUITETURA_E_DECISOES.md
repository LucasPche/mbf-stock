# Arquitetura e decisões técnicas — MBF Stock

## 1. Visão geral da arquitetura

O MBF Stock é um sistema web desenvolvido com Python, HTML, CSS e JavaScript, utilizando SQLite para armazenar os dados.

A interface se comunica com o servidor por meio de requisições HTTP e respostas JSON. O servidor recebe as solicitações, verifica as permissões dos usuários e executa as operações necessárias.

A estrutura atual pode ser representada da seguinte forma:

```text
Navegador (HTML, CSS e JavaScript)
          |
          | HTTP / JSON
          v
      server.py
  Rotas e autenticação
          |
          +---- security_service.py
          |     Validação e senhas
          |
          +---- inventory_service.py
          |     Regras de estoque
          |
          +---- database_repository.py
          |     Conexões e esquema
          |
          v
       SQLite
```

O sistema também utiliza o ViaCEP para consultar informações de endereço diretamente pelo navegador.

A organização em módulos permite separar algumas responsabilidades. Entretanto, o arquivo `server.py` ainda concentra parte das regras de negócio, das rotas HTTP e do acesso aos dados. Por esse motivo, a estrutura atual apresenta uma modularização parcial, sem implementar completamente o padrão MVC.

## 2. Organização dos módulos

### server.py

É o arquivo principal da aplicação. Ele inicializa o servidor HTTP, recebe as requisições, verifica as sessões e coordena as operações realizadas pelo sistema.

### security_service.py

Contém funções relacionadas à segurança, como validação de identificadores e geração e verificação de hashes de senhas.

A separação dessas funções facilita sua reutilização e permite realizar testes sem depender diretamente do servidor HTTP.

### inventory_service.py

Contém funções utilizadas nas operações de estoque.

A função `stock_adjustment()` calcula a diferença entre a quantidade anterior e a nova quantidade de uma peça, permitindo registrar corretamente as entradas e saídas.

A função `reserve_withdrawal()` realiza uma atualização condicional do saldo, evitando retiradas que deixariam o estoque negativo.

### database_repository.py

É responsável por funções relacionadas à abertura de conexões SQLite e à manutenção do esquema do banco de dados.

As conexões habilitam as chaves estrangeiras e utilizam um tempo de espera para situações em que o banco esteja temporariamente bloqueado.

O servidor mantém algumas funções de acesso ao banco para preservar a compatibilidade com as rotas existentes.

### auditar_banco.py

Foi desenvolvido para verificar a integridade de bancos de dados existentes.

A ferramenta realiza consultas de auditoria sem modificar os registros armazenados.

## 3. Banco de dados

O sistema utiliza SQLite para armazenar informações de usuários, peças, solicitações e movimentações de estoque.

As principais tabelas são:

- `users`: informações dos usuários.
- `parts`: cadastro e quantidade das peças.
- `requests`: solicitações de materiais.
- `movements`: histórico das movimentações.
- `signup_requests`: solicitações de cadastro.

O SQLite foi utilizado por permitir a criação de um banco local integrado à aplicação, sem a necessidade de instalar um servidor de banco de dados separado.

Essa escolha facilita o desenvolvimento e a execução do projeto. Entretanto, ambientes com maior número de acessos simultâneos podem exigir uma solução de banco de dados diferente, dependendo dos requisitos de desempenho e disponibilidade.

Uma possível evolução seria utilizar PostgreSQL, mediante adaptação da camada de persistência e validação das operações existentes.

## 4. Integridade dos dados

Foram adicionadas verificações para reduzir a possibilidade de registros inconsistentes.

Entre elas estão:

- Ativação de chaves estrangeiras nas conexões.
- Restrições `CHECK` para impedir quantidades e preços negativos.
- Validação de quantidades utilizadas em solicitações e movimentações.
- Verificação de saldo antes da retirada de materiais.
- Controle de operações que alteram o estoque.

As restrições adicionadas ao esquema são aplicadas na criação das tabelas correspondentes. Bancos antigos podem precisar de uma migração para receber as mesmas restrições.

Por isso, a atualização de bancos existentes exige a preservação dos dados e a realização de testes em uma cópia antes de qualquer alteração.

## 5. Auditoria do banco de dados

O arquivo `auditar_banco.py` permite analisar um banco SQLite existente.

A ferramenta utiliza verificações como:

- `PRAGMA foreign_key_check`, para identificar problemas de integridade referencial.
- `PRAGMA integrity_check`, para verificar a integridade geral do banco.
- Inspeção das restrições `CHECK` presentes nas tabelas.
- Consulta de valores inválidos relacionados a quantidades e preços.

A auditoria funciona somente em modo de leitura e não altera os dados.

Para executar:

```powershell
python auditar_banco.py caminho/do/banco.db
```

Quando identifica condições que exigem uma migração, a ferramenta pode retornar o código de saída 2.

A auditoria auxilia na identificação de problemas, mas não realiza correções ou migrações automaticamente.

## 6. Segurança

O MBF Stock possui mecanismos de autenticação e controle de acesso para diferenciar as operações permitidas aos usuários.

Entre as medidas implementadas estão:

- Armazenamento de senhas por hash com salt.
- Controle de sessões.
- Expiração de sessão após 30 minutos de inatividade.
- Verificação de permissões administrativas.
- Validação de identificadores e dados recebidos pela API.
- Bloqueio de acesso a arquivos privados.
- Revogação de sessões de contas desativadas.

As sessões são armazenadas em memória e o servidor utiliza o módulo `http.server` do Python.

Essa estrutura atende à execução local utilizada no desenvolvimento. Uma implantação em ambiente de produção exigiria outras medidas, como HTTPS, gerenciamento persistente de sessões, backups, monitoramento e testes de concorrência.

## 7. Testes automatizados

Os testes foram desenvolvidos com a biblioteca `unittest`, utilizando bancos temporários para evitar alterações nos dados utilizados durante a execução normal do sistema.

Os testes verificam situações como:

- Login, logout e autenticação.
- Permissões de administradores e operadores.
- Cadastro e edição de peças.
- Registro de movimentações.
- Solicitação, aprovação e rejeição de materiais.
- Prevenção de retirada sem saldo suficiente.
- Validação de identificadores e dados JSON.
- Integridade referencial do banco.
- Bloqueio de arquivos privados.
- Revogação de sessões.
- Funções dos módulos de segurança, estoque e persistência.
- Auditoria do banco de dados.

Na execução realizada em 11/11/2026, foram concluídos **45 testes automatizados, todos aprovados**.

Para executar novamente:

```powershell
python -m unittest discover -v
```

Para medir a cobertura dos módulos da aplicação:

```powershell
python -m coverage run --source=server,security_service,inventory_service,database_repository -m unittest discover
python -m coverage report -m
```

A cobertura de código permite identificar quais partes da implementação foram executadas durante os testes.

A validação dos requisitos funcionais também depende da execução dos cenários previstos e das evidências registradas na matriz de testes.

## 8. Rastreabilidade dos requisitos

O arquivo `MATRIZ_TESTES.md` apresenta a relação entre os requisitos do sistema e suas respectivas verificações.

Essa organização facilita a identificação das funcionalidades testadas e das evidências disponíveis.

Considerando um conjunto de 11 requisitos funcionais, a comprovação de pelo menos 75% exige a aprovação de no mínimo 9 requisitos.

Esse percentual é diferente da cobertura de código, pois representa a quantidade de requisitos efetivamente validados.

## 9. Decisões e limitações técnicas

Durante o desenvolvimento, foram realizadas alterações para melhorar a organização do código, a segurança e a integridade dos dados.

A separação das funções em módulos específicos reduziu a concentração de algumas responsabilidades no servidor principal.

Mesmo com essas melhorias, a aplicação ainda possui limitações relacionadas à arquitetura e à implantação.

Entre os pontos que podem ser aprimorados estão a separação mais completa entre rotas, regras de negócio e persistência, a avaliação de outro banco de dados para ambientes com maior concorrência e a utilização de uma estrutura de servidor adequada à produção.

Essas melhorias representam possibilidades de evolução do projeto e devem ser consideradas de acordo com os requisitos definidos para sua utilização.

## 10. Considerações finais

A arquitetura do MBF Stock foi organizada para permitir a comunicação entre a interface web, o servidor Python e o banco de dados SQLite.

Durante o desenvolvimento, foram adicionados módulos específicos para segurança, operações de estoque e persistência, além de testes automatizados e ferramentas de auditoria.

Essas alterações contribuíram para melhorar a organização do código, a validação das operações e o controle das informações armazenadas.

O projeto reúne funcionalidades de controle de estoque e apresenta uma estrutura que pode continuar sendo aprimorada conforme as necessidades de manutenção e utilização do sistema.