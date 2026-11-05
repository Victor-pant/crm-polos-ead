# CRM Polos EAD — Projeto Integrador (Univesp)

CRM web para gestão comercial dos polos EAD de **Pirapozinho** e **Santo
Anastácio**, com cadastro de leads, histórico de interações (WhatsApp,
telefone, presencial, e-mail), dashboards comerciais e API REST para
integrações externas.

> **Escopo final:** em relação ao Plano de Ação, a integração com a API do
> WhatsApp (envio automático de mensagens) foi retirada do escopo. O sistema
> ficou focado no cadastro e acompanhamento de leads e nos dashboards, que
> já atendem às necessidades da empresa. As conversas são registradas
> manualmente no histórico de cada lead.

**Equipe:** Victor Hugo Alves Oliveira ([@Victor-pant](https://github.com/Victor-pant))
e Anderson Aparecido de Melo ([@andersonmelloap-spec](https://github.com/andersonmelloap-spec)).

Feito com Python/Flask, seguindo o Plano de Ação do PI, cobrindo todos os
requisitos obrigatórios:

| Requisito | Onde está no projeto |
|---|---|
| Framework web | Flask (`app.py`, `routes/`) |
| Banco de dados | SQLite via SQLAlchemy (`models.py`) — troque a `DATABASE_URL` para usar PostgreSQL/MySQL em produção sem mudar o código |
| Script web (JavaScript) | `static/js/main.js` (contador de caracteres, confirmação, filtros) e `static/js/dashboard.js` (gráficos via fetch + Chart.js) |
| Computação em nuvem | Deploy pronto para Render (`Procfile`) — ver seção "Deploy" |
| API | `routes/api.py` — API REST própria (leads e interações), autenticada por token |
| Acessibilidade | skip-link, `aria-label`/`aria-live`, labels em todos os campos, foco visível, HTML semântico — ver `templates/base.html` e `static/css/style.css` |
| Controle de versão | Git + GitHub (este repositório) |
| Testes | `tests/` com pytest (modelos, rotas web e API) |
| Análise de dados (opcional) | Dashboard com indicadores de conversão e gráficos por status/origem/polo |

---

## 1. Como rodar na sua máquina

Pré-requisitos: **Python 3.10+** instalado.

```bash
# 1. Entre na pasta do projeto
cd crm_unoeste

# 2. Crie e ative um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Copie o arquivo de variáveis de ambiente
copy .env.example .env      # Windows
cp .env.example .env        # Linux/Mac

# 5. Popule o banco com dados de demonstração (2 polos, 1 usuário, 7 leads)
python seed.py

# 6. Rode a aplicação
python app.py
```

Acesse **http://localhost:5000** e entre com:
- **E-mail:** `maria@unoeste-pi.com.br`
- **Senha:** `123456`

> Se quiser começar com o banco vazio (sem dados de exemplo), pule o passo
> 5 — a aplicação cria o banco automaticamente na primeira execução, mas
> você precisará criar um usuário manualmente (veja `seed.py` como
> referência de como criar um `Usuario` com `set_senha()`).

---

## 2. Estrutura do projeto

```
crm_unoeste/
├── app.py              # application factory + ponto de entrada
├── config.py           # configurações (lidas de variáveis de ambiente)
├── extensions.py       # instâncias do SQLAlchemy e Flask-Login
├── models.py           # Polo, Usuario, Lead, Interacao
├── seed.py             # popula o banco com dados de demonstração
├── routes/
│   ├── auth.py          # login/logout
│   ├── leads.py         # CRUD de leads, lista inteligente, timeline
│   ├── api.py           # API REST para integrações externas
│   └── dashboard.py     # indicadores e dados dos gráficos
├── templates/           # HTML (Jinja2 + Bootstrap 5)
├── static/
│   ├── css/style.css
│   └── js/{main.js, dashboard.js}
└── tests/               # testes automatizados (pytest)
```

---

## 3. Rodando os testes

```bash
pytest -v
```

Os testes usam um banco SQLite **em memória** (não afetam o `crm.db` real)
e cobrem: hashing de senha, regras de negócio (lead atrasado, telefone
normalizado), autenticação, criação de leads/interações e a API REST.

---

## 4. A API REST

Toda rota em `/api/*` exige o cabeçalho `X-API-Token`
com o valor definido em `API_TOKEN` no `.env`.

```bash
# Listar leads
curl -H "X-API-Token: SEU_TOKEN" http://localhost:5000/api/leads

# Criar um lead
curl -X POST -H "X-API-Token: SEU_TOKEN" -H "Content-Type: application/json" \
     -d '{"nome": "João Silva", "telefone": "18999998888", "origem": "WhatsApp"}' \
     http://localhost:5000/api/leads

# Registrar uma interação no histórico do lead
curl -X POST -H "X-API-Token: SEU_TOKEN" -H "Content-Type: application/json" \
     -d '{"mensagem": "Cliente perguntou sobre valores", "direcao": "recebida"}' \
     http://localhost:5000/api/leads/1/interacoes
```

---

## 5. Deploy em nuvem (Render — gratuito)

O repositório já traz um `render.yaml` (Blueprint):

1. Em [render.com](https://render.com), clique em **New + → Blueprint** e
   selecione este repositório.
2. Confirme. O Render cria o Web Service `crm-polos-ead` com:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app --preload --workers 2 --bind 0.0.0.0:$PORT`
   - `SECRET_KEY` e `API_TOKEN` gerados automaticamente
   - `AUTO_SEED=1`: na primeira execução, o banco vazio é populado com os
     dados fictícios de demonstração (login `maria@unoeste-pi.com.br` / `123456`).

> No plano gratuito o disco é temporário: o SQLite volta aos dados de
> demonstração a cada novo deploy/reinício, e o serviço "dorme" após 15 min
> sem acesso (o primeiro acesso depois disso leva ~1 min). Para guardar dados
> reais, crie um PostgreSQL no Render e defina `DATABASE_URL` com a
> "Internal Database URL" — nenhuma mudança de código é necessária.

---

## 6. Controle de versão (Git/GitHub)

```bash
git clone https://github.com/Victor-pant/crm-polos-ead.git
cd crm-polos-ead
```

O `.gitignore` já está configurado para não versionar o banco (`*.db`),
o `.env` com segredos, e as pastas de ambiente virtual.

**Fluxo sugerido para trabalhar com o Anderson:** cada um cria uma branch
por funcionalidade (`git checkout -b feature/dashboard`), e vocês abrem
Pull Requests no GitHub para revisar o código um do outro antes do merge
— isso também gera um bom histórico de commits para citar no relatório
final do PI.

---

## 7. Próximos passos sugeridos

- [ ] Trocar `SECRET_KEY` e `API_TOKEN` por valores fortes antes de
      colocar em produção
- [ ] Cadastrar um usuário para cada polo (hoje só existe a "Maria")
- [ ] Adicionar mais testes de acessibilidade (ex.: rodar o axe-core no
      navegador) para o relatório final
