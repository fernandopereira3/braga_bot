# BragaBot 🤖

## Descrição

O BragaBot é um projeto educacional de automação web desenvolvido em Python usando Selenium WebDriver. O bot foi criado para automatizar o processo de login e navegação no sistema SIGAA (Sistema Integrado de Gestão de Atividades Acadêmicas) da Universidade de Brasília (UnB).

## ⚠️ Aviso Importante

**Este é um projeto com fins puramente educacionais e encontra-se em desenvolvimento (inacabado).** 

O projeto foi criado para:
- Demonstrar conceitos de automação web
- Ensinar o uso da biblioteca Selenium
- Praticar desenvolvimento em Python
- Explorar técnicas de web scraping

## Funcionalidades Atuais

- ✅ Verificação de conectividade com o site
- ✅ Configuração automática do ChromeDriver
- ✅ Login automatizado no SIGAA
- ✅ Navegação para seção de cursos
- ✅ Contagem de módulos disponíveis
- ✅ Tratamento básico de erros

## Funcionalidades Planejadas (Em Desenvolvimento)

- ⏳ Extração detalhada de informações dos cursos
- ⏳ Geração de relatórios
- ⏳ Interface gráfica
- ⏳ Configuração via arquivo de configuração
- ⏳ Logs mais detalhados

## Tecnologias Utilizadas

- **Python 3.x**
- **Selenium WebDriver** - Automação do navegador
- **ChromeDriver** - Driver para Google Chrome
- **Requests** - Verificação de conectividade HTTP

## Pré-requisitos

- Python 3.6 ou superior
- Google Chrome instalado
- ChromeDriver compatível com a versão do Chrome

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/braga_bot.git
cd braga_bot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Baixe o ChromeDriver e coloque na pasta do projeto:
   - Acesse: https://chromedriver.chromium.org/
   - Baixe a versão compatível com seu Chrome
   - Extraia o arquivo `chromedriver` na pasta raiz do projeto

## Como Usar

```bash
python app_main.py
```

**Nota:** Você precisará modificar as credenciais no código antes de executar.

## Estrutura do Projeto