# Lotec — SaaS de Gestão para Assistências Técnicas

Plataforma completa multi-tenant para gestão de assistências técnicas de eletrônicos. Ordens de serviço, clientes, aparelhos, financeiro, assinaturas e portal do cliente.

**Acesse:** [https://assistencia.lourenc00.dev.br](https://assistencia.lourenc00.dev.br)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Alembic |
| Banco | PostgreSQL 16 |
| Proxy | nginx |
| Pagamentos | Mercado Pago (assinaturas recorrentes) |
| Deploy | Docker Compose, Cloudflare Tunnel |
| Backup | cron + pg_dump (diário às 3h) |

---

## Funcionalidades

### Para o dono da assistência
- Cadastro de clientes com dados de contato
- Cadastro de aparelhos (marca, modelo, IMEI, defeito)
- Ordens de serviço com numeração automática (ex: LoTec-001)
- Fluxo de status: Recebido → Em Análise → Aguardando Aprovação → Aguardando Peça → Em Reparo → Pronto → Entregue
- Registro de serviços e peças com cálculo automático de valores
- Histórico completo de cada OS
- Dashboard com métricas (OS abertas, receita, status)
- Relatórios por período com exportação CSV
- Busca global (clientes, aparelhos, OS)
- Portal público para clientes acompanharem suas OS

### Para o Super Admin (plataforma)
- Dashboard com MRR, total de empresas, assinaturas
- Gerenciamento de empresas (ativação/suspensão)
- Visualização de assinaturas, pagamentos e webhooks
- Gerenciamento de planos
- Configurações com toggles ligar/desligar:
  - Mercado Pago
  - E-mails (SMTP)
  - Fotos (S3/MinIO)
  - Portal público
  - Período de teste
  - Planos individuais

### Segurança
- Multi-tenant: isolamento total entre empresas
- JWT com refresh token
- Senhas com Argon2id + pepper
- Rate limiting (auth: 5r/s, geral: 30r/s)
- Headers de segurança (CSP, XSS, CORS)
- Webhook com validação HMAC
- Backup automático diário

---

## Planos

| Plano | Preço | Recursos |
|---|---|---|
| **Básico** | R$ 29,90/mês | Clientes, aparelhos, OS, relatórios básicos |
| **Profissional** | R$ 49,90/mês | + Fotos, exportação CSV, busca global |
| **Premium** | R$ 79,90/mês | + Portal do cliente, suporte prioritário |

Período de teste gratuito: 15 dias (configurável).
Dias de tolerância pós-cancelamento: 5 dias (configurável).

---

## Instalação

### Pré-requisitos
- Docker + Docker Compose
- Ubuntu 20.04+ (testado em 26.04)

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/lourenc00/lotec-saas.git
cd lotec-saas

# 2. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Editar com suas credenciais

# 3. Subir os serviços
docker compose up -d

# 4. Verificar se está rodando
docker compose ps
curl http://localhost:80/health
```

### Configuração do Mercado Pago

1. Acesse o painel do Mercado Pago para desenvolvedores
2. Copie o **Access Token** e **Public Key**
3. Crie 3 planos de recorrência (Básico, Profissional, Premium)
4. Copie os IDs dos planos
5. Configure o webhook com URL: `https://SEU-DOMINIO/api/webhooks/mercadopago`
6. No painel admin (`/admin/configuracoes`), preencha as credenciais

### Configuração do Cloudflare Tunnel

```yaml
# /etc/cloudflared/config.yml
ingress:
  - hostname: assistencia.seudominio.com
    service: http://localhost:7855
  - service: http_status:404
```

```bash
sudo systemctl restart cloudflared
```

---

## Comandos úteis

```bash
# Status dos serviços
docker compose ps

# Logs
docker compose logs -f backend
docker compose logs -f frontend

# Reiniciar um serviço
docker compose restart backend

# Rebuild (após alterações no código)
docker compose up -d --build backend frontend

# Backup manual
./backups/backup-db.sh

# Restore
./backups/restore-db.sh /home/luciano/lotec-saas/backups/lotec_YYYYMMDD_HHMMSS.dump.gz

# Acessar o banco
docker compose exec postgres psql -U lotec_user -d lotec_db
```

---

## Estrutura do projeto

```
lotec-saas/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/        # Endpoints da API
│   │   │   ├── api/webhooks/  # Webhooks (Mercado Pago)
│   │   │   ├── core/          # Config, auth, dependências
│   │   │   ├── models/        # Modelos SQLAlchemy
│   │   │   ├── schemas/       # Schemas Pydantic
│   │   │   ├── services/      # Lógica de negócio
│   │   │   └── integrations/  # Clientes externos (MP)
│   │   ├── alembic/           # Migrations do banco
│   │   └── Dockerfile
│   └── frontend/
│       ├── app/
│       │   ├── page.tsx           # Landing page
│       │   ├── login/             # Login
│       │   ├── cadastro/          # Registro
│       │   ├── planos/            # Planos públicos
│       │   ├── acompanhar/        # Portal do cliente
│       │   ├── dashboard/         # Painel do usuário
│       │   └── admin/             # Painel Super Admin
│       ├── lib/
│       │   ├── api.ts             # Cliente API
│       │   └── auth-context.tsx   # Contexto de autenticação
│       └── Dockerfile
├── infra/nginx/nginx.conf
├── backups/
├── docker-compose.yml
└── .env
```

---

## API

A documentação interativa da API está disponível em:
- **Swagger UI:** `https://assistencia.lourenc00.dev.br/docs` (apenas em desenvolvimento)
- **OpenAPI JSON:** `https://assistencia.lourenc00.dev.br/openapi.json`

### Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/v1/auth/register` | Criar conta |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Dados do usuário logado |
| GET | `/api/v1/dashboard/summary` | Métricas do dashboard |
| GET/POST | `/api/v1/customers` | Listar/criar clientes |
| GET/POST | `/api/v1/devices` | Listar/criar aparelhos |
| GET/POST | `/api/v1/service-orders` | Listar/criar OS |
| POST | `/api/v1/service-orders/{id}/status` | Atualizar status da OS |
| GET | `/api/v1/reports/service-orders` | Relatório de OS |
| GET | `/api/v1/portal/{token}` | Portal público (acompanhamento) |
| POST | `/api/webhooks/mercadopago` | Webhook do Mercado Pago |

---

## O que ainda falta fazer

### Prioridade Alta
- [ ] Teste end-to-end do checkout do Mercado Pago (fazer assinatura real de teste)
- [ ] Validação do webhook do Mercado Pago em produção
- [ ] Fluxo de e-mails: boas-vindas, status da OS, lembrete de pagamento
- [ ] Termos de uso e política de privacidade
- [ ] Página 404 personalizada

### Prioridade Média
- [ ] Impressão de OS (PDF)
- [ ] Upload de logo por empresa (white-label)
- [ ] Notificações in-app (mensagens dentro do sistema)
- [ ] Filtros avançados nas listagens (data, técnico, status)
- [ ] Paginação otimizada com cursor
- [ ] Testes automatizados (pytest + frontend)
- [ ] CI/CD (GitHub Actions)

### Prioridade Baixa
- [ ] App mobile (React Native ou PWA)
- [ ] Notificações push (Firebase)
- [ ] Integração com WhatsApp (envio de status)
- [ ] Estoque de peças
- [ ] Financeiro (fluxo de caixa, despesas)
- [ ] Orçamentos antes da OS
- [ ] Múltiplos técnicos por OS
- [ ] Laudo técnico (PDF)
- [ ] Dashboard com gráficos (Chart.js)
- [ ] Dark mode
- [ ] Internacionalização (i18n)
- [ ] Auditoria de ações (log de quem fez o quê)

### Infraestrutura
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Logs centralizados (Loki ou ELK)
- [ ] SSL direto (Let's Encrypt) caso não use Cloudflare
- [ ] Staging environment
- [ ] Load balancing (se precisar escalar)
- [ ] CDN para assets estáticos

---

## Usuário padrão

| Campo | Valor |
|---|---|
| Email | `admin@lotec.com` |
| Senha | `Test1234!` |
| Perfil | Super Admin |

---

## Licença

Projeto privado. Todos os direitos reservados.
