# 🚀 QUICK START - Dashboard Web

## ⚡ Iniciando em 3 Passos

### 1️⃣ Instalar Dependências

```bash
cd /workspace/outlook-sdr-agent
pip install -r requirements.txt
```

### 2️⃣ Configurar Credenciais

Crie o arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
# Azure AD (Outlook)
OUTLOOK_CLIENT_ID=seu_client_id
OUTLOOK_CLIENT_SECRET=seu_client_secret
OUTLOOK_TENANT_ID=seu_tenant_id

# Google Gemini (IA GRÁTIS)
GOOGLE_API_KEY=sua_chave_gratis_aqui

# Ou use OpenAI (pago)
# OPENAI_API_KEY=sua_chave_openai
```

### 3️⃣ Iniciar Dashboard

```bash
python web/app.py
```

Acesse no navegador: **http://localhost:5000**

---

## 🎯 O Que Você Vai Ver

Ao abrir o dashboard:

1. **📊 Painel de Estatísticas**
   - E-mails pendentes
   - Respostas enviadas
   - Follow-ups criados
   - Reuniões agendadas

2. **📨 Lista de E-mails**
   - Cada e-mail mostra:
     - Assunto e remetente
     - Classificação (Hot/Warm/Cold)
     - Resposta sugerida pela IA
     - Botões: Aprovar, Editar, Rejeitar

3. **📋 Follow-ups**
   - Follow-ups vencidos aparecem aqui
   - Mensagens sugeridas pela IA

---

## ✅ Fluxo de Aprovação

**Nenhum e-mail é enviado sem sua aprovação!**

1. IA lê e-mail e gera resposta
2. Dashboard mostra a sugestão
3. **VOCÊ decide:**
   - ✅ **Aprovar** → Envia imediatamente
   - ✏️ **Editar** → Modifica → Envia
   - ❌ **Rejeitar** → Ignora e marca como lido

---

## 🛠️ Comandos Úteis

### Iniciar
```bash
python web/app.py
```

### Parar
Pressione `Ctrl+C` no terminal

### Ver Logs
```bash
tail -f logs/sdr_agent.log
```

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask flask-socketio eventlet
```

### Erro: "Port 5000 already in use"
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Dashboard não carrega e-mails
- Verifique se `.env` está configurado corretamente
- Confira credenciais do Azure AD
- Clique em "🔄 Atualizar" para forçar refresh

---

## 📚 Documentação Completa

- **README.md** - Visão geral do projeto
- **INSTALL.md** - Guia detalhado de instalação
- **docs/IA_GRATIS.md** - Como usar IAs gratuitas
- **docs/DASHBOARD_GUIDE.md** - Guia completo do dashboard

---

## 🎉 Pronto!

Agora você tem um **dashboard profissional** para gerenciar suas vendas!

**Acesso:** http://localhost:5000

**Lembre-se:** Todo e-mail precisa da sua aprovação antes de ser enviado! ✅
