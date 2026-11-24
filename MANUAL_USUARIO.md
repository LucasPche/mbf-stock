# Manual do Usuário — MBF Stock

## 1. Apresentação

O MBF Stock é um sistema web desenvolvido para facilitar o controle de estoque de peças e materiais de uma metalúrgica.

Por meio dele, é possível consultar materiais cadastrados, acompanhar quantidades disponíveis, registrar solicitações e verificar movimentações realizadas.

O sistema possui dois perfis de acesso: administrador e operador.

## 2. Como acessar o sistema

Para utilizar a versão online, basta ter um navegador atualizado, conexão com a internet e credenciais válidas. Não é necessário instalar Python no computador do usuário.

**Endereço principal:** https://mbf-stock.onrender.com/

**Ambiente de testes (quando disponível):** https://mbf-stock-teste.onrender.com/

No plano gratuito do Render, o primeiro acesso após inatividade pode demorar. O acesso local para desenvolvimento é descrito a seguir.

### Iniciando o servidor localmente (desenvolvimento)

Abra a pasta do projeto no VS Code e acesse o terminal. Instale as dependências com `python -m pip install -r requirements.txt`.

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
3. Marque a caixa de aceite dos Termos de Uso e da Política de Privacidade.
4. Clique no botão de entrar.
5. Aguarde o carregamento do painel principal.

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

Nessa área, é possível consultar contas, criar novos usuários diretamente e analisar solicitações de cadastro.

**Cadastro administrativo:** acesse **Usuários**, clique em **Limpar** para abrir o formulário de novo cadastro, informe nome, login, perfil, setor e uma senha com no mínimo 8 caracteres e clique em **Salvar usuário**. O servidor armazena um hash PBKDF2-HMAC-SHA256 com salt, e não a senha em texto puro.

**Cadastro por solicitação:** na tela de login, clique em **Solicitar cadastro**, preencha o formulário e aceite os Termos de Uso. O administrador deve acessar **Usuários > Pedidos de cadastro** e escolher **Liberar** ou **Rejeitar**.

**Edição:** na lista de usuários liberados, clique em **Editar**. A senha pode ficar em branco quando não for alterada.

**Desativação:** na lista de usuários, selecione **Desativar** e confirme. A conta perde o acesso, mas o histórico permanece preservado. A desativação não exclui dados pessoais.

O controle de permissões impede que operadores realizem operações administrativas sem autorização.

## 10. Privacidade e direitos do titular (LGPD)

O usuário autenticado pode acessar **Meus dados e LGPD**, informar detalhes opcionais e clicar em **Solicitar exclusão de dados**. A solicitação aparece na seção **Acompanhamento** com seu status e a resposta do administrador. Não é possível abrir duas solicitações pendentes simultaneamente.

O administrador também acessa **Meus dados e LGPD** para consultar as solicitações, clicar em **Analisar pedido**, indicar o status (**em análise** ou **indeferido**) e registrar a justificativa.

**Limitação importante:** o sistema registra e acompanha a solicitação, mas ainda não elimina ou anonimiza automaticamente os dados pessoais. A opção de conclusão está indisponível até que exista tratamento efetivo dos dados. A decisão deve observar a finalidade do tratamento e eventuais hipóteses legais de conservação. Esse recurso não representa, isoladamente, conformidade integral à LGPD.

## 11. Auditoria administrativa

Entre como administrador e abra **Auditoria** no menu lateral. A tela mostra os eventos persistidos com data, usuário, ação e detalhes; use **Atualizar registros** para recarregar os eventos mais recentes. Operadores não têm acesso à consulta de auditoria.

O registro persistente inclui eventos de autenticação, criação e edição administrativa de usuários e solicitações de privacidade. A auditoria ainda não representa cobertura de todas as ações possíveis do sistema. O banco PostgreSQL/Supabase é o meio de persistência; o acesso para consulta é realizado pela própria interface, com autorização administrativa.

## 12. Relatórios

O sistema disponibiliza informações de estoque e recursos de relatório para auxiliar no acompanhamento dos materiais.

Quando disponível na tela, a exportação em CSV permite obter os dados em um formato que pode ser aberto em programas de planilha.

## 13. Consulta de CEP

O MBF Stock utiliza o serviço ViaCEP para auxiliar no preenchimento de informações de endereço do fornecedor.

Ao informar um CEP válido, o navegador pode consultar os dados correspondentes e preencher os campos disponíveis.

Essa consulta auxilia o preenchimento do formulário, mas os dados obtidos do ViaCEP não são persistidos no banco de dados pela integração atual.

## 14. Como sair do sistema

Ao terminar de utilizar o MBF Stock:

1. Localize a opção **Sair**.
2. Clique para encerrar a sessão.
3. Aguarde o retorno à tela de login.

O sistema também encerra sessões após aproximadamente 30 minutos de inatividade.

## 15. Problemas comuns

### Não consigo acessar o sistema

Na versão online, confira a conexão com a internet e o endereço `https://mbf-stock.onrender.com/`; aguarde a inicialização se o serviço gratuito estiver inativo. Na execução local, verifique se `python server.py` está em execução e se `http://localhost:8000` foi digitado corretamente.

### Usuário ou senha incorretos

Confira os dados informados. Em bancos já existentes, as senhas não são alteradas automaticamente pelas variáveis configuradas no terminal.

### Não tenho permissão para realizar uma operação

Algumas funcionalidades são exclusivas do administrador. Verifique se você está utilizando o perfil correto.

### Não consigo retirar uma peça

Confira a quantidade disponível. O sistema impede retiradas que deixariam o estoque com saldo negativo.

### A sessão expirou

Caso permaneça um período sem utilizar o sistema, será necessário realizar o login novamente.

## 16. Armazenamento e cuidados com os dados

A versão online utiliza PostgreSQL no Supabase; a execução local utiliza SQLite quando `DATABASE_URL` não está definida. Os dados da versão online são mantidos no banco remoto e não no computador de quem acessa o site. O histórico de movimentações e as solicitações permanecem vinculados às contas utilizadas.

Não compartilhe senhas, tokens de sessão nem a variável `DATABASE_URL`. Após utilizar um computador compartilhado, clique em **Sair**.

## 17. Considerações finais

O MBF Stock reúne funcionalidades para organizar o cadastro de peças, acompanhar o estoque e registrar solicitações de materiais.

A utilização dos diferentes perfis permite separar as atividades administrativas das operações de consulta e solicitação.

O histórico de movimentações e os indicadores do painel auxiliam no acompanhamento das informações e no controle dos materiais cadastrados.