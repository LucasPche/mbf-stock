# Banco de dados PostgreSQL — Supabase

## Situação da implementação

O MBF Stock possui suporte a **SQLite local** e **PostgreSQL remoto**. O arquivo `database_repository.py` escolhe PostgreSQL quando a variável de ambiente `DATABASE_URL` está definida e utiliza o driver `psycopg`; sem ela, utiliza SQLite. O esquema PostgreSQL está em `supabase/schema.sql`.

Na demonstração publicada no Render, foram observados registros de peças no painel do Supabase e o cadastro de uma nova peça permaneceu visível após reinicialização do serviço. Isso valida o cenário manual observado, mas não substitui testes abrangentes de concorrência e recuperação de falhas.

## Configuração

1. Crie um projeto Supabase e confira o esquema em `supabase/schema.sql`.
2. Obtenha uma string de conexão PostgreSQL compatível com a rede do ambiente de execução. No Render, quando necessário, use o **Session pooler** IPv4 do Supabase, em vez do host direto IPv6.
3. Configure `DATABASE_URL` no Render em **Environment**, sem colocar a senha no GitHub.
4. Configure `MBF_ADMIN_PASSWORD` e `MBF_OPERADOR_PASSWORD` para a inicialização de usuários em um banco novo.
5. Use **Build Command** `pip install -r requirements.txt` e **Start Command** `python server.py`.
6. Verifique logs de inicialização, login, listagem e cadastro de peças. Reinicie o serviço e confira a persistência no Supabase.

## Testes e limitações

Execute `python -m unittest discover -v` localmente. Os testes unitários utilizam principalmente SQLite; a execução de 54 testes aprovados em CI não equivale a uma suíte completa de integração PostgreSQL. O script `supabase/check_connection.py` auxilia na verificação da conexão, quando executado em ambiente com credenciais autorizadas.

**Não existe migração automática de dados antigos do SQLite.** Faça backup e migração controlada quando necessário. A aplicação usa sessões em memória e o servidor Python `http.server`, de modo que a implantação é destinada à demonstração acadêmica, não a uma operação corporativa homologada.

## Segurança

Nunca publique credenciais, `DATABASE_URL`, capturas com senhas ou arquivos `.env`. A conexão usa TLS. Caso uma senha seja exposta, redefina-a no Supabase e atualize a variável no Render. O banco deve ser acessado pelo servidor, não diretamente pelo navegador.
