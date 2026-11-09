# mbf-stock
Sistema web para controle de estoque da MBF – Metalúrgica Brasileira de Fixadores

## Limitações técnicas e melhorias futuras

O MBF Estoque é um protótipo acadêmico desenvolvido para demonstrar funcionalidades de gerenciamento de estoque, cadastro de peças, usuários, solicitações e histórico de movimentações.

Atualmente, o sistema utiliza Python com http.server para disponibilizar a aplicação, SQLite para armazenar os dados e sessões de autenticação mantidas em memória.

Embora essas tecnologias atendam aos objetivos de demonstração do projeto, a aplicação ainda não está preparada para utilização em ambiente de produção.

Para uma futura implantação em ambiente empresarial, recomenda-se:

- Utilizar um servidor de aplicação apropriado para produção, com HTTPS.
- Avaliar um banco de dados adequado ao acesso simultâneo de múltiplos usuários.
- Implementar sessões persistentes, com expiração e gerenciamento seguro.
- Ampliar os testes automatizados, de segurança e de desempenho.
- Estabelecer rotinas de backup, monitoramento e recuperação de dados.

Essas melhorias são propostas para versões futuras e não fazem parte do escopo atual do protótipo acadêmico.
