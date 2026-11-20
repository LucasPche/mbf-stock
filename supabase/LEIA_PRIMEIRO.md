# Migração experimental para Supabase PostgreSQL

**A branch migracao-supabase NÃO está pronta para deploy.** O serviço ativo Render continua usando SQLite.

## Preparação
1. Criar um projeto no Supabase e aguardar o banco ficar pronto.
2. Abrir SQL Editor e executar `supabase/schema.sql` em um projeto novo de teste.
3. Em Project Settings > Database > Connection string, obter URI PostgreSQL apropriada para o ambiente Render (preferir pooler quando necessário).
4. Guardar a URI em variável secreta `DATABASE_URL` no Render; nunca publicar senha, URI completa ou chaves no GitHub.

## Trabalho pendente antes de publicar
- Adaptar `database_repository.py`, `server.py` e `inventory_service.py` para psycopg/PostgreSQL, com transações atômicas.
- Substituir SQLite `?`, `AUTOINCREMENT`, `lastrowid`, `executescript`, `PRAGMA` e exceções específicas.
- Garantir baixa concorrente de estoque, histórico, exclusão lógica e solicitações.
- Importar dados reais apenas com backup, sem duplicar usuários/peças e com IDs/sequências reconciliados.
- Executar todos os testes em PostgreSQL e teste de persistência após reinício/redeploy.
- Atualizar monografia, manual e vídeo somente depois de confirmar o funcionamento.

**Não configure DATABASE_URL no serviço Render de produção antes da adaptação e testes.**
