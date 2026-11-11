# Arquitetura e decisões técnicas — MBF Stock

## Estado real da implementação

```text
Navegador (HTML/CSS/JavaScript)
  | HTTP/JSON, token de sessão
  v
server.py (rotas HTTP + autorização + regras de negócio)
  | SQL parametrizado
  v
SQLite (users, parts, requests, movements, signup_requests)

Navegador --HTTPS--> ViaCEP (consulta de CEP, apenas preenchimento visual)
```

**Não declarar que o projeto implementa MVC completo.** A interface é separada em arquivos estáticos, mas `server.py` ainda concentra controlador HTTP, regras de negócio e acesso a dados. Essa é uma pendência expressa do orientador e deve ser tratada por refatoração real, não somente por alteração de nomenclatura na monografia.

## Regras verificadas por testes automatizados

- Login, logout, autenticação e bloqueio de operação administrativa por operador.
- Cadastro e edição de peças; diferença de estoque registrada como movimentação.
- Solicitação e aprovação com baixa de saldo; rejeição sem baixa; prevenção de dupla análise.
- Proteção contra retirada sem saldo, IDs inválidos e JSON malformado.
- Ativação de `PRAGMA foreign_keys` e verificação de integridade no banco temporário.
- Bloqueio de acesso a arquivo privado e revogação de sessão de conta desativada.

## Banco de dados: decisão pendente

SQLite suporta transações e chaves estrangeiras, mas sua adequação depende do volume, concorrência e requisitos operacionais. O orientador solicitou reconsiderar seu uso. A decisão deve ser formalizada e, se exigida migração, executada e testada (por exemplo, para PostgreSQL) **antes** de afirmar robustez empresarial. Uma simples troca no texto não atende ao parecer.

## Segurança e implantação

As sessões ficam em memória e expiram por inatividade após 30 minutos. A aplicação usa `http.server` e não deve ser exposta à internet como está. Para implantação real são necessários servidor apropriado, TLS/HTTPS, gestão persistente de sessões, política de backups, migrações e testes de concorrência e recuperação. Não há evidência suficiente para declarar conformidade plena com a LGPD.

## Rastreabilidade

A matriz de testes `MATRIZ_TESTES.md` distingue verificações automatizadas de aceite funcional. Para a exigência de 75% dos 11 RFs, são necessários pelo menos 9 requisitos aceitos com evidência; 65% de cobertura de código não comprova isso.

## Refatoração incremental — módulo de segurança

A validação de IDs e o hash/verificação de senhas foram extraídos para `security_service.py`, um módulo sem dependência HTTP ou SQLite. O `server.py` importa esses serviços; as interfaces públicas foram preservadas para manter compatibilidade com os testes. Essa separação reduz o acoplamento, mas **não é MVC completo**: a extração das regras de negócio e repositórios de dados ainda precisa ser implementada.

## Refatoração adicional: serviço de estoque (11/11/2026)

O módulo `inventory_service.py` implementa `stock_adjustment()` (calcula entrada/saída pela diferença real) e `reserve_withdrawal()` (baixa condicional atômica de estoque). As rotas de edição de peças e aprovação de solicitações chamam essas funções, mantendo as transações e respostas HTTP sob responsabilidade de `server.py`. Isso estabelece uma separação inicial de regras de negócio e controlador, mas **não completa MVC**. A persistência ainda precisa ser extraída e a arquitetura revalidada.

Foram executados 32 testes automatizados com sucesso; a cobertura combinada de `server.py`, `security_service.py` e `inventory_service.py` foi de 65% (510 instruções, 176 não cobertas). A meta de 50% de cobertura de código foi alcançada, mas a matriz de aceite dos 11 requisitos continua uma atividade distinta.


## Restrições adicionais do banco novo

As tabelas `parts`, `requests` e `movements` passaram a ter restrições `CHECK` para impedir saldos/preços negativos e quantidades de movimentação/solicitação não positivas. A integridade referencial permanece habilitada por conexão. **As restrições não são retroativas para bancos já existentes**, exigindo migração validada.

## Auditoria não destrutiva de banco legado

Foi adicionado `auditar_banco.py`, que abre um banco existente **somente para leitura**, executa `PRAGMA foreign_key_check` e verifica a presença das restrições CHECK no esquema. O programa não modifica dados e devolve código 2 quando há migração pendente. Executar: `python auditar_banco.py caminho/do/banco.db`. O arquivo `mbf_estoque.db` da cópia analisada tem zero bytes, portanto **não constitui um banco legado válido para homologar migração**. Não substituir o banco original do aluno por este arquivo. A migração de dados legados permanece pendente e exige backup e testes com cópia de dados.

## Auditoria de conteúdo legado

Além da inspeção das restrições declaradas, `auditar_banco.py` consulta
`PRAGMA integrity_check` e contabiliza valores inválidos de estoque e preço.
A execução é somente leitura. A auditoria não corrige automaticamente
inconsistências, não migra o banco e não substitui uma homologação.

## Atualização: repositório de persistência

A abertura de conexões SQLite e a inspeção de colunas foram movidas para `database_repository.py`, que recebe o caminho do banco como argumento. O `server.py` mantém uma função `connect()` de compatibilidade para preservar rotas e testes existentes. A conexão ativa chaves estrangeiras e configura espera de até 10 segundos em caso de bloqueio do banco. Dois testes novos validam essas propriedades e a idempotência de `ensure_column`.

**Limite:** trata-se de separação inicial da camada de persistência, não de MVC completo. O SQLite continua sendo o banco em uso e a migração de bases existentes ainda exige planejamento e testes.
