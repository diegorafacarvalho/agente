# Guia de Instalação e Configuração

Siga este guia passo a passo para configurar seu Outlook SDR Agent.

## 📋 Pré-requisitos

1. **Python 3.9 ou superior**
   ```bash
   python --version
   ```

2. **Conta Microsoft/Outlook** com permissões administrativas

3. **Azure AD App Registration** (veja abaixo)

4. **Chave de API OpenAI** (ou outro provedor de IA)

---

## 🔧 Passo 1: Configurar Azure AD (Microsoft)

### 1.1 Registrar Aplicação no Azure Portal

1. Acesse [portal.azure.com](https://portal.azure.com)
2. Vá em **Azure Active Directory** > **App registrations**
3. Clique em **New registration**
4. Preencha:
   - **Name**: `Outlook SDR Agent`
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Deixe em branco (usamos auth flow de credentials)

5. Anote as seguintes informações:
   - **Application (client) ID** → `OUTLOOK_CLIENT_ID`
   - **Directory (tenant) ID** → `OUTLOOK_TENANT_ID`

### 1.2 Criar Client Secret

1. Na sua aplicação, vá em **Certificates & secrets**
2. Clique em **New client secret**
3. Adicione uma descrição e escolha expiração
4. **Copie o valor do secret imediatamente** → `OUTLOOK_CLIENT_SECRET`
   ⚠️ Você não poderá vê-lo novamente depois!

### 1.3 Configurar Permissões da API

1. Vá em **API permissions**
2. Clique em **Add a permission** > **Microsoft Graph**
3. Selecione **Application permissions**
4. Adicione:
   - `Mail.Read` - Ler e-mails
   - `Mail.ReadWrite` - Ler e escrever e-mails
   - `Mail.Send` - Enviar e-mails
   - `Calendars.ReadWrite` - Gerenciar calendário
   - `User.Read` - Ler perfil do usuário

5. Clique em **Grant admin consent** (necessário admin)

---

## 🐍 Passo 2: Instalar Dependências

```bash
# Navegue até o diretório do projeto
cd outlook-sdr-agent

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Microsoft Outlook / Azure AD
OUTLOOK_CLIENT_ID=seu-client-id-aqui
OUTLOOK_CLIENT_SECRET=seu-client-secret-aqui
OUTLOOK_TENANT_ID=seu-tenant-id-aqui
OUTLOOK_EMAIL=seu.email@empresa.com.br

# OpenAI
OPENAI_API_KEY=sk-sua-chave-openai-aqui
OPENAI_MODEL=gpt-4

# Configurações opcionais
FOLLOWUP_INITIAL_HOURS=24
FOLLOWUP_MAX_ATTEMPTS=3
DATABASE_URL=sqlite:///data/sdr_agent.db
LOG_LEVEL=INFO
```

---

## 🧪 Passo 4: Testar a Instalação

### Teste básico (sem conexão real):

```bash
# Execute em modo de verificação
python src/main.py --help
```

### Teste com conexão Outlook (após configurar tudo):

```bash
# Execução única
python src/main.py

# Modo contínuo (verifica a cada 15 minutos)
python src/main.py --continuous --interval 15

# Modo sem resposta automática (apenas leitura)
python src/main.py --no-auto-respond
```

---

## 🚀 Passo 5: Usando o Sistema

### Comandos Disponíveis

```bash
# Ver ajuda
python src/main.py --help

# Executar uma vez (processa e-mails e follow-ups)
python src/main.py

# Modo contínuo (roda indefinidamente)
python src/main.py --continuous --interval 30

# Apenas processar e-mails (sem responder)
python src/main.py --no-auto-respond

# Modo demonstração
python src/main.py --demo
```

### Fluxo de Funcionamento

1. **Leitura de E-mails**: O sistema lê e-mails não lidos da caixa de entrada
2. **Classificação**: Cada e-mail é classificado por intenção e temperatura do lead
3. **Análise com IA**: A IA analisa o contexto e sugere ações
4. **Resposta Automática**: Respostas são geradas e enviadas (se habilitado)
5. **Follow-up**: Follow-ups são agendados automaticamente
6. **Agendamento**: Propostas de reunião são enviadas quando há interesse

---

## 📊 Monitoramento

### Logs

Os logs são salvos em:
- `logs/sdr_agent.log` - Arquivo de log completo
- Console - Logs em tempo real durante execução

### Verificando Status

Durante a execução, você verá:
- ✅ E-mails processados
- ✅ Respostas enviadas
- ✅ Follow-ups criados
- ❌ Erros (se houver)

---

## 🔒 Segurança

### Boas Práticas

1. **Nunca commit** o arquivo `.env` com credenciais reais
2. Use **segredos do Azure** com expiração definida
3. Rotacione credenciais periodicamente
4. Restrinja permissões ao mínimo necessário
5. Monitore logs de acesso no Azure Portal

### Arquivos Sensíveis

Estes arquivos estão no `.gitignore`:
- `.env` - Credenciais
- `config/settings.py` - Configurações locais
- `logs/*.log` - Logs podem conter dados sensíveis
- `data/*.db` - Banco de dados local

---

## 🛠️ Troubleshooting

### Erro: "Authentication failed"

✅ Verifique:
- Client ID, Secret e Tenant ID estão corretos
- Permissões foram concedidas no Azure
- Admin consent foi aprovado

### Erro: "OPENAI_API_KEY not configured"

✅ Verifique:
- Chave da API está correta no `.env`
- Conta OpenAI tem créditos disponíveis

### Erro: "Module not found"

✅ Execute:
```bash
pip install -r requirements.txt --upgrade
```

### E-mails não estão sendo lidos

✅ Verifique:
- Permissão `Mail.Read` está configurada
- E-mails realmente estão na caixa de entrada (não em outras pastas)
- Não há filtros ou regras movendo e-mails

---

## 📞 Suporte

Para issues específicos do projeto, consulte:
- Documentação da [Microsoft Graph API](https://docs.microsoft.com/graph/)
- Documentação do [LangChain](https://python.langchain.com/)
- Documentação da [O365 Library](https://github.com/O365/python-o365)

---

## 🎯 Próximos Passos

Após instalação bem-sucedida:

1. **Configure templates** personalizados para sua empresa
2. **Ajuste prompts** da IA para seu tom de voz
3. **Defina regras** específicas de qualificação de leads
4. **Integre com CRM** (em desenvolvimento)
5. **Configure webhooks** para tempo real (futuro)

Boas vendas! 🚀
