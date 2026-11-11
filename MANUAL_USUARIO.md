# Manual do Usuário — MBF Stock

## 1. Apresentação

O MBF Stock é um sistema web desenvolvido para facilitar o controle de estoque de peças e materiais de uma metalúrgica.

Por meio dele, é possível consultar materiais cadastrados, acompanhar quantidades disponíveis, registrar solicitações e verificar movimentações realizadas.

O sistema possui dois perfis de acesso: administrador e operador.

## 2. Como acessar o sistema

Para utilizar o MBF Stock, é necessário ter Python 3.11 ou superior instalado no computador e um navegador atualizado.

### Iniciando o servidor

Abra a pasta do projeto no VS Code e acesse o terminal.

Antes da primeira execução com um banco novo, configure as senhas dos usuários iniciais:

```powershell
$env:MBF_ADMIN_PASSWORD = 'substitua-por-senha-forte-1'
$env:MBF_OPERADOR_PASSWORD = 'substitua-por-senha-forte-2'
```

Em seguida, execute:

```powershell
python server.py
```

Com o servidor funcionando, abra o navegador e acesse:

http://localhost:8000

### Realizando o login

Na tela inicial:

1. Informe seu nome de usuário.
2. Digite sua senha.
3. Clique no botão de entrar.
4. Aguarde o carregamento do painel principal.

Em um banco de dados novo, os usuários iniciais são `admin` e `operador`, com as senhas definidas no terminal.

## 3. Perfis de acesso

### Administrador

O administrador possui acesso às funções de gerenciamento do sistema, incluindo cadastro e edição de peças, gerenciamento de usuários e análise das solicitações de materiais.

### Operador

O operador pode consultar as peças cadastradas, verificar informações do estoque e registrar solicitações de retirada.

As operações disponíveis dependem das permissões de cada perfil.

## 4. Dashboard

Após realizar o login, o usuário é direcionado ao painel principal.

O dashboard apresenta informações gerais do estoque, como:

- Quantidade de peças cadastradas.
- Materiais abaixo do estoque mínimo.
- Solicitações pendentes.
- Pedidos de cadastro pendentes.

Essas informações permitem acompanhar a situação do estoque sem precisar consultar cada peça individualmente.

## 5. Consulta de estoque

Para consultar os materiais:

1. Acesse a opção **Estoque** no menu.
2. Visualize a lista de peças cadastradas.
3. Utilize a pesquisa ou os filtros disponíveis para localizar uma peça.
4. Consulte as informações apresentadas, como código, nome, categoria e quantidade disponível.

Os materiais abaixo do estoque mínimo são identificados na interface para facilitar seu acompanhamento.

## 6. Cadastro e edição de peças

O cadastro e a edição de peças são operações disponíveis para usuários com permissão administrativa.

### Cadastrar uma peça

1. Entre com uma conta de administrador.
2. Acesse a área de estoque.
3. Abra a opção de cadastro de peça.
4. Preencha os campos solicitados, como código, nome, categoria, localização e quantidades.
5. Confira os dados informados.
6. Salve o cadastro.

As quantidades e o estoque mínimo devem ser valores válidos e não negativos.

### Editar uma peça

1. Localize a peça desejada.
2. Selecione a opção de edição.
3. Altere as informações necessárias.
4. Confirme a operação.

Quando a quantidade de uma peça é alterada, o sistema registra a diferença no histórico de movimentações.

Por exemplo, se a quantidade passar de 10 para 15 unidades, será registrada uma entrada de 5 unidades. Se passar de 15 para 12, será registrada uma saída de 3 unidades.

A exclusão de peças pode ser impedida quando existem registros relacionados que precisam ser preservados.

## 7. Solicitação de materiais

O operador pode registrar solicitações de retirada de peças.

Para realizar uma solicitação:

1. Acesse a área **Solicitações**.
2. Selecione a peça desejada.
3. Informe a quantidade solicitada.
4. Confirme o envio.
5. Acompanhe o estado da solicitação.

Após o envio, a solicitação fica pendente de análise.

### Aprovação e rejeição

O administrador pode consultar as solicitações pendentes e decidir pela aprovação ou rejeição.

Quando uma solicitação é aprovada, o sistema verifica a quantidade disponível antes de realizar a baixa no estoque.

Se a solicitação for rejeitada, a quantidade da peça não será alterada.

Solicitações já analisadas não podem ser aprovadas ou rejeitadas novamente.

## 8. Histórico de movimentações

A área de histórico permite acompanhar as entradas e saídas de materiais.

Para consultar:

1. Acesse **Histórico** no menu.
2. Visualize as movimentações registradas.
3. Consulte a peça, a quantidade movimentada, a data e o usuário responsável.

O histórico ajuda a identificar alterações realizadas no estoque e acompanhar a movimentação dos materiais.

## 9. Gerenciamento de usuários

O administrador possui acesso às funcionalidades de gerenciamento de usuários.

Nessa área, é possível consultar as contas e analisar solicitações de cadastro, conforme as opções disponíveis na interface.

O controle de permissões impede que operadores realizem operações administrativas sem autorização.

## 10. Relatórios

O sistema disponibiliza informações de estoque e recursos de relatório para auxiliar no acompanhamento dos materiais.

Quando disponível na tela, a exportação em CSV permite obter os dados em um formato que pode ser aberto em programas de planilha.

## 11. Consulta de CEP

O MBF Stock utiliza o serviço ViaCEP para auxiliar no preenchimento de informações de endereço do fornecedor.

Ao informar um CEP válido, o navegador pode consultar os dados correspondentes e preencher os campos disponíveis.

Essa consulta auxilia o preenchimento do formulário, mas os dados de endereço não são armazenados no banco SQLite da versão atual.

## 12. Como sair do sistema

Ao terminar de utilizar o MBF Stock:

1. Localize a opção **Sair**.
2. Clique para encerrar a sessão.
3. Aguarde o retorno à tela de login.

O sistema também encerra sessões após aproximadamente 30 minutos de inatividade.

## 13. Problemas comuns

### Não consigo acessar o sistema

Verifique se o servidor está em execução e se o endereço `http://localhost:8000` foi digitado corretamente.

### Usuário ou senha incorretos

Confira os dados informados. Em bancos já existentes, as senhas não são alteradas automaticamente pelas variáveis configuradas no terminal.

### Não tenho permissão para realizar uma operação

Algumas funcionalidades são exclusivas do administrador. Verifique se você está utilizando o perfil correto.

### Não consigo retirar uma peça

Confira a quantidade disponível. O sistema impede retiradas que deixariam o estoque com saldo negativo.

### A sessão expirou

Caso permaneça um período sem utilizar o sistema, será necessário realizar o login novamente.

## 14. Considerações finais

O MBF Stock reúne funcionalidades para organizar o cadastro de peças, acompanhar o estoque e registrar solicitações de materiais.

A utilização dos diferentes perfis permite separar as atividades administrativas das operações de consulta e solicitação.

O histórico de movimentações e os indicadores do painel auxiliam no acompanhamento das informações e no controle dos materiais cadastrados.