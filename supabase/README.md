# Preparação da migração Supabase (branch supabase-postgres)

## Estado
A infraestrutura Supabase foi criada, mas **o servidor Python desta branch ainda utiliza SQLite**.
Definir `DATABASE_URL` no Render, por si só, **não migra os dados nem muda o backend**.
Não considerar a migração concluída sem adaptação do código e testes.

## Etapas seguras
1. No Supabase, SQL Editor > New query: execute `supabase/schema.sql` e confira as cinco tabelas.
2. Adaptar `database_repository.py`, `server.py` e `inventory_service.py` para PostgreSQL/psycopg. Diferenças: placeholders, `AUTOINCREMENT`, `PRAGMA`, `lastrowid`, tratamento de erros e transações.
3. Inicializar contas com senhas provenientes de variáveis de ambiente, nunca SQL com senha em texto claro.
4. Criar testes de integração contra um banco PostgreSQL isolado, incluindo login, cadastro, edição, exclusão lógica, aprovação concorrente e histórico.
5. Fazer backup/migração explícita dos dados do SQLite existente se forem necessários. Não executar `init_db` em produção sem revisar a lógica de seed.
6. Após validação, configurar `DATABASE_URL` exclusivamente em Render > Environment e publicar a branch testada.
7. Reiniciar e comprovar persistência após redeploy. Atualizar README, monografia e manual para refletir o backend efetivo.

## Segurança
Nunca publicar a connection string com senha em GitHub, screenshots ou mensagens.
Se a credencial tiver sido exposta, redefina a senha do banco no Supabase e atualize o Render.
A URL deve usar TLS e os dados não devem ser acessíveis diretamente pelo navegador.
