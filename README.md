# MBF Stock — Sistema de Controle de Estoque

## 1. Sobre o projeto

O MBF Stock é um sistema web desenvolvido para ajudar no controle de estoque de peças e materiais de uma metalúrgica.

A ideia do projeto surgiu da necessidade de organizar melhor o cadastro das peças, acompanhar as quantidades disponíveis e facilitar as solicitações de materiais.

O sistema foi desenvolvido como Projeto Final de Curso (PFC) de Sistemas de Informação, utilizando Python no servidor e HTML, CSS e JavaScript na interface.

## 2. Tecnologias utilizadas

As principais tecnologias utilizadas no desenvolvimento foram:

- **Python:** desenvolvimento do servidor e das funcionalidades do sistema.
- **HTML, CSS e JavaScript:** criação da interface e interação com o usuário.
- **SQLite:** armazenamento das informações.
- **JSON:** troca de dados entre o navegador e o servidor.
- **Git e GitHub:** controle de versões do projeto.
- **Unittest:** criação e execução dos testes automatizados.
- **Coverage.py:** verificação da cobertura dos testes.

## 3. Requisitos para execução

Para executar o sistema, é necessário ter:

- Python 3.11 ou superior.
- Um navegador atualizado.
- Acesso ao terminal ou ao VS Code.

Para verificar a cobertura dos testes, também é necessário instalar a biblioteca Coverage:

```powershell
python -m pip install coverage
```

## 4. Como executar

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

O MBF Stock utiliza SQLite para armazenar as informações das peças, usuários, solicitações e movimentações.

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

Na execução realizada em 11/11/2026, foram obtidos os seguintes resultados:

- **45 testes executados.**
- **45 testes aprovados.**
- **Nenhum erro ou falha.**

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
- `RELATORIO_REVISAO.md`: registra as correções e verificações realizadas.

## 12. Considerações finais

O desenvolvimento do MBF Stock permitiu aplicar conhecimentos adquiridos durante o curso de Sistemas de Informação, principalmente nas áreas de programação web, banco de dados, autenticação e testes de software.

Durante o projeto, foram realizadas melhorias para aumentar a segurança, corrigir problemas de validação e garantir maior controle sobre as movimentações do estoque.

Os testes automatizados e as verificações realizadas nas principais telas ajudaram a confirmar o funcionamento das funcionalidades implementadas.

O sistema reúne recursos de cadastro, consulta, solicitações e histórico de movimentações, atendendo ao objetivo de organizar e facilitar o acompanhamento dos materiais de uma metalúrgica.