# BragaBot

---

> # ⚠️ PROJETO EDUCACIONAL
> ## Este projeto foi desenvolvido exclusivamente para fins de estudo e aprendizado da biblioteca **Selenium WebDriver** com Python.
> **Não use em produção ou para fins não autorizados.**

---

Automação de cursos na plataforma EAD da CECP. O bot faz login com múltiplos usuários, detecta cursos incompletos, navega por todas as atividades, envia feedbacks e baixa os certificados automaticamente.

## Funcionalidades

- Login automático com múltiplos usuários.
- Detecção de cursos incompletos (baseado em progresso da plataforma)
- Navegação automática por todas as atividades do curso.
- Marcação de atividades como concluídas
- Preenchimento e envio automático de feedbacks
- Download de certificados em PDF com nome do curso e do usuário no arquivo

## Pré-requisitos

- Python 3.14+
- Google Chrome instalado
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes)

## Instalação

```bash
git clone https://github.com/seu-usuario/braga_bot.git
cd braga_bot
uv sync
```

## Configuração

Crie um arquivo `users.txt` na raiz do projeto com um usuário por linha no formato `cpf:senha`:

```
123.456.789-00:minhasenha
987.654.321-00:outrasenha
```

Ou configure via variáveis de ambiente (para usuário único):

```bash
SITE_USERNAME=123.456.789-00
SITE_PASSWORD=minhasenha
```

## Como Usar

```bash
uv run python app.py
```

O bot irá:
1. Verificar conectividade com o site
2. Para cada usuário: fazer login, listar cursos incompletos e completar cada um
3. Baixar os certificados gerados como `certificado_{nome_curso}_{nome_usuario}.pdf`

## Estrutura do Projeto

```
braga_bot/
├── app.py          # Ponto de entrada — login, scan de cursos e orquestração
├── app_course.py   # Lógica de navegação e conclusão de cursos
├── check.py        # Verificação de conectividade com o site
├── users.txt       # Credenciais dos usuários (não versionar)
├── pyproject.toml  # Dependências do projeto
└── requirements.txt
```

## Dependências principais

| Pacote | Uso |
|--------|-----|
| `selenium` | Automação do navegador Chrome |
| `requests` | Download de certificados via sessão HTTP |
| `python-dotenv` | Leitura de variáveis de ambiente do `.env` |
