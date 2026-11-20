# MBF Stock — Sistema de Controle de Estoque

## 1. Sobre o projeto

O MBF Stock é um sistema web desenvolvido para ajudar no controle de estoque de peças e materiais de uma metalúrgica.

A ideia do projeto surgiu da necessidade de organizar melhor o cadastro das peças, acompanhar as quantidades disponíveis e facilitar as solicitações de materiais.

O sistema foi desenvolvido como Projeto Final de Curso (PFC) de Sistemas de Informação, utilizando Python no servidor e HTML, CSS e JavaScript na interface.

## 2. Tecnologias utilizadas

As principais tecnologias utilizadas no desenvolvimento foram:

- **Python:** desenvolvimento do servidor e das funcionalidades do sistema.
- **HTML, CSS e JavaScript:** criação da interface e interação com o usuário.
- **SQLite:** banco local para desenvolvimento e testes.
- **PostgreSQL (Supabase):** banco persistente quando `DATABASE_URL` estiver configurada.
- **JSON:** troca de dados entre o navegador e o servidor.
- **Git e GitHub:** controle de versões do projeto.
- **Unittest:** criação e execução dos testes automatizados.
- **Coverage.py:** verificação da cobertura dos testes.

## 3. Requisitos para execução

Para executar o sistema localmente, é necessário ter:

- Python 3.11 ou superior.
- Um navegador atualizado.
- Acesso ao terminal ou ao VS Code.

Instale as dependências do projeto com `python -m pip install -r requirements.txt`.

Para verificar a cobertura dos testes, também é necessário instalar a biblioteca Coverage:

```powershell
python -m pip install coverage
```

## 4. Acesso online e execução local

**Demonstração publicada no Render:** https://mbf-stock-teste.onrender.com/

O acesso exige uma conta e senha válidas. O serviço gratuito pode demorar a responder após um período de inatividade.

### Execução local

Abra a pasta do projeto no VS Code e acesse o terminal.

No PowerShell, configure as senhas iniciais:

```powershell
$env:MBF_ADMIN_PASSWORD = 'substitua-por-senha-forte-1'
$env:MBF_OPERADOR_PASSWORD = 'substitua-por-senha-forte-2'
python server.py
```

Depois, abra o navegador e acesse:

http://localhost:8000

Em um banco de dados novo, os usuários iniciais são:

- **Administrador:** `admin`
- **Operador:** `operador`

As senhas serão aquelas configuradas no terminal. Caso o banco já tenha usuários cadastrados, as senhas existentes não serão alteradas automaticamente.

Por segurança, as senhas reais e os arquivos do banco de dados não devem ser publicados no GitHub.

## 5. Funcionalidades do sistema

### Login e controle de acesso

O sistema possui uma tela de login para identificar os usuários e controlar o acesso às funcionalidades.

Existem permissões diferentes para administradores e operadores. As sessões expiram após 30 minutos de inatividade.

### Dashboard

A tela inicial apresenta informações gerais sobre o estoque, como quantidade de peças cadastradas, materiais abaixo do estoque mínimo e solicitações pendentes.

### Estoque

Na área de estoque é possível consultar as peças cadastradas, pesquisar materiais e visualizar informações como código, nome, categoria, quantidade e localização.

Usuários com permissão administrativa também podem cadastrar, editar e excluir peças, respeitando as regras de integridade do sistema.

### Solicitações

Os operadores podem solicitar materiais disponíveis no cadastro.

As solicitações ficam registradas para análise do administrador, que pode aprová-las ou rejeitá-las.

Quando uma solicitação é aprovada e existe saldo suficiente, a quantidade solicitada é descontada do estoque.

### Histórico

O sistema registra as movimentações realizadas, permitindo consultar entradas, saídas, quantidades, datas e usuários responsáveis.

Isso facilita o acompanhamento das alterações feitas no estoque.

### Gerenciamento de usuários

O administrador possui acesso às funções de gerenciamento de usuários e às solicitações de cadastro, conforme as permissões implementadas.

## 6. Organização dos arquivos

O projeto está dividido nos seguintes arquivos e pastas:

| Arquivo | Função |
|---|---|
| `server.py` | Servidor, rotas e comunicação com a interface |
| `database_repository.py` | Conexão e operações relacionadas ao banco |
| `security_service.py` | Validação de identificadores e tratamento de senhas |
| `inventory_service.py` | Regras relacionadas às movimentações de estoque |
| `auditar_banco.py` | Verificação de integridade do banco |
| `public/` | Arquivos HTML, CSS e JavaScript |
| `test_*.py` | Testes automatizados |
| `MANUAL_USUARIO.md` | Orientações para utilizar o sistema |
| `MATRIZ_TESTES.md` | Relação entre requisitos e testes |
| `ARQUITETURA_E_DECISOES.md` | Organização técnica e decisões do projeto |

Essa divisão ajuda a separar algumas responsabilidades do sistema e facilita a manutenção do código.

## 7. Banco de dados

O MBF Stock utiliza SQLite localmente. Quando `DATABASE_URL` está configurada, a camada `database_repository.py` conecta ao PostgreSQL (Supabase) por meio do driver `psycopg`. A demonstração publicada foi verificada com registros visíveis no Supabase e persistência após reinicialização. O banco SQLite não é migrado automaticamente para o PostgreSQL.

Durante o desenvolvimento, foram realizadas melhorias nas validações e na integridade dos dados, incluindo a ativação das chaves estrangeiras e verificações de quantidades e valores inválidos.

Também foi criada uma ferramenta de auditoria para identificar possíveis inconsistências em bancos existentes.

O SQLite atende à execução local utilizada no desenvolvimento. A avaliação de sua adequação a ambientes com maior número de acessos simultâneos ainda faz parte das decisões técnicas do projeto.

## 8. Segurança

Foram implementadas medidas para melhorar a segurança e evitar erros durante a utilização, como:

- Armazenamento de senhas utilizando hash e salt.
- Controle de acesso de acordo com o perfil do usuário.
- Expiração das sessões por inatividade.
- Validação de dados recebidos pela API.
- Tratamento de conteúdo HTML exibido na interface.
- Verificação de integridade dos registros do banco.
- Controle de retirada de materiais para evitar saldo negativo.

Essas verificações ajudam a reduzir erros e impedir operações não autorizadas.

## 9. Testes automatizados

Foram desenvolvidos testes automatizados para verificar funcionalidades importantes do sistema, incluindo autenticação, permissões, validação de dados, operações de estoque, solicitações e integridade do banco.

Para executar os testes:

```powershell
python -m unittest discover -v
```

Para verificar a cobertura do código da aplicação:

```powershell
python -m coverage run --source=server,security_service,inventory_service,database_repository -m unittest discover
python -m coverage report -m
```

Na execução de CI da branch de migração em 20/11/2026, foram obtidos:

- **54 testes executados e aprovados**, sem falhas, no ambiente de testes automatizados.
- A suíte usa SQLite local para testes unitários e não substitui testes de integração com PostgreSQL real.

O relatório geral de cobertura apresentou 80%. Para avaliar especificamente o código da aplicação, deve ser utilizado o comando com `--source`, indicado acima.

A cobertura de código é uma das formas de avaliar os testes. A comprovação dos requisitos funcionais também depende da matriz de testes e das verificações realizadas no sistema.

## 10. Integração com ViaCEP

O sistema utiliza o ViaCEP para auxiliar no preenchimento do endereço de fornecedores.

A consulta é realizada pelo navegador. Atualmente, os dados preenchidos por essa integração não são armazenados no banco de dados.

## 11. Documentação

Além deste README, o projeto possui arquivos complementares:

- `MANUAL_USUARIO.md`: explica como utilizar as principais funcionalidades.
- `MATRIZ_TESTES.md`: apresenta os testes e sua relação com os requisitos.
- `ARQUITETURA_E_DECISOES.md`: descreve a organização técnica do sistema.
- `supabase/README.md`: descreve a configuração e as verificações do PostgreSQL.
- `docs/processo_retirada.bpmn`: modelo BPMN do processo de retirada.

## 12. Considerações finais

O desenvolvimento do MBF Stock permitiu aplicar conhecimentos adquiridos durante o curso de Sistemas de Informação, principalmente nas áreas de programação web, banco de dados, autenticação e testes de software.

Durante o projeto, foram realizadas melhorias para aumentar a segurança, corrigir problemas de validação e garantir maior controle sobre as movimentações do estoque.

Os testes automatizados e as verificações realizadas nas principais telas ajudaram a confirmar o funcionamento das funcionalidades implementadas.

O sistema reúne recursos de cadastro, consulta, solicitações e histórico de movimentações, atendendo ao objetivo de organizar e facilitar o acompanhamento dos materiais de uma metalúrgica.

## Atualização de modelagem e segurança — 11/11/2026

- Modelo BPMN 2.0 de solicitação e aprovação: [docs/processo_retirada.bpmn](docs/processo_retirada.bpmn). Abrir em editor BPMN para conferir e exportar figura antes de inserir na monografia.
- Dashboard e relatório de itens críticos: escape de conteúdo dinâmico na interface.
- Exportação CSV: tratamento de conteúdo que poderia ser interpretado como fórmula por planilhas.
- Ver [ARQUITETURA_E_DECISOES.md](ARQUITETURA_E_DECISOES.md) para limitações e decisões técnicas.

**Escopo:** projeto acadêmico de demonstração. A separação em módulos não representa MVC completo. O servidor `http.server` e as sessões em memória não constituem uma solução corporativa homologada. Os testes automatizados e a matriz de aceite devem ser reproduzidos no commit final.


## Configuração PostgreSQL (Supabase) e publicação

- Instale dependências com `python -m pip install -r requirements.txt`.
- Configure `DATABASE_URL` em ambiente seguro (não salve credenciais no Git).
- Execute o esquema `supabase/schema.sql` no SQL Editor do projeto Supabase ou permita que a aplicação crie as tabelas ao iniciar.
- A aplicação seleciona PostgreSQL automaticamente se `DATABASE_URL` estiver definida; caso contrário, usa SQLite local.
- No Render, use o build `pip install -r requirements.txt` e a inicialização `python server.py`.
- A conexão, o login, o cadastro de peça e a persistência após reinicialização foram verificados na demonstração. Para novas alterações, repita os testes de regressão. Não há migração automática dos registros do SQLite antigo.
- O roteiro de validação está em `supabase/README.md`.
