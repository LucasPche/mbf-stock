# Relatório de validação — Entrega final MBF Stock

**Data:** 20/11/2026  
**Repositório:** https://github.com/LucasPche/mbf-stock  
**Branch de entrega:** `entregafinal`

## Evidências automatizadas

- **54 testes unitários executados e aprovados**, conforme logs do GitHub Actions.
- **Cobertura total de 65%** nos módulos `server.py`, `security_service.py`, `inventory_service.py` e `database_repository.py`, medida pelo Coverage.py.
- **Meta acadêmica de cobertura:** mínimo de 50%; **atendida**.
- Workflow de testes: https://github.com/LucasPche/mbf-stock/actions/runs/44836084017
- Workflow de validação técnica: https://github.com/LucasPche/mbf-stock/actions/runs/44836084057
- Execução com percentual explícito nos logs: https://github.com/LucasPche/mbf-stock/actions/runs/44836015988

## Configuração e persistência

A aplicação seleciona SQLite local quando `DATABASE_URL` não está definida e PostgreSQL/Supabase quando está configurada. Na demonstração do Render, foi verificado manualmente que uma peça cadastrada continuava disponível após a reinicialização do serviço.

**Demonstração validada:** https://mbf-stock-teste.onrender.com/

## Escopo da validação

A cobertura de 65% é a medida de execução dos testes automatizados sobre os módulos indicados; não significa que 65% dos requisitos funcionais tenham sido homologados. Os testes de CI utilizam SQLite e não equivalem a uma bateria completa de integração com PostgreSQL. O sistema utiliza sessões em memória e servidor `http.server`, adequado ao contexto acadêmico demonstrativo, não homologado para operação corporativa.

## Documentação complementar

- [Manual do Usuário](MANUAL_USUARIO.md)
- [Matriz de Testes](MATRIZ_TESTES.md)
- [Arquitetura e Decisões Técnicas](ARQUITETURA_E_DECISOES.md)
- [Configuração PostgreSQL/Supabase](supabase/README.md)

Os slides, vídeo demonstrativo, resumo expandido e a monografia com manual anexado como apêndice são entregáveis acadêmicos separados e não são comprovados por este relatório.
