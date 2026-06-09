# 🚀 GUIA RÁPIDO - Deixe o Sistema Funcional AGORA!

## ✅ Passo 1: Instalar Dependências

```bash
cd /workspace/outlook-sdr-agent
pip install -r requirements.txt
```

---

## ✅ Passo 2: Configurar IA Gratuita (Google Gemini)

### 2.1 Obtenha sua API Key GRÁTIS do Google Gemini
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 2.2 Configure o arquivo `.env`

```bash
# Copie o template
cp .env.example .env
```

Agora edite o arquivo `.env` e adicione:

```env
# === IA GRATUITA - GOOGLE GEMINI ===
GOOGLE_API_KEY=sua_chave_aqui_cole_a_chave_do_passo_anterior

# === CONFIGURAÇÕES DO OUTLOOK (Azure AD) ===
# Você precisa registrar um app no Azure Portal
OUTLOOK_CLIENT_ID=seu_client_id
OUTLOOK_CLIENT_SECRET=seu_client_secret
OUTLOOK_TENANT_ID=seu_tenant_id
```

---

## ✅ Passo 3: Configurar Outlook (Azure AD)

### 3.1 Registrar Aplicativo no Azure

1. Acesse: https://portal.azure.com
2. Vá em **Azure Active Directory** → **App registrations** → **New registration**
3. Nome: `Outlook SDR Agent`
4. Tipo de conta: **Accounts in any organizational directory and personal Microsoft accounts**
5. Redirect URI: `http://localhost` (ou deixe em branco por enquanto)
6. Clique em **Register**

### 3.2 Anotar Credenciais

Após registrar, copie:
- **Application (client) ID** → `OUTLOOK_CLIENT_ID`
- **Directory (tenant) ID** → `OUTLOOK_TENANT_ID`

### 3.3 Criar Client Secret

1. No menu do app, vá em **Certificates & secrets**
2. Clique em **New client secret**
3. Descrição: `SDR Agent Secret`
4. Expiração: 24 meses
5. Clique em **Add**
6. **IMPORTANTE:** Copie o valor do segredo AGORA (não mostra de novo!)
7. Cole no `.env` como `OUTLOOK_CLIENT_SECRET`

### 3.4 Configurar Permissões de API

1. No menu do app, vá em **API permissions**
2. Clique em **Add a permission** → **Microsoft Graph**
3. Selecione **Delegated permissions**
4. Adicione estas permissões:
   - `Mail.Read` - Ler e-mails
   - `Mail.Send` - Enviar e-mails
   - `Mail.ReadWrite` - Modificar e-mails (marcar como lido)
   - `Calendars.ReadWrite` - Agendar reuniões
5. Clique em **Grant admin consent** (se tiver permissão de admin)

---

## ✅ Passo 4: Testar o Sistema

### Modo SEGURO (com aprovação - PADRÃO) ⭐ RECOMENDADO

```bash
python src/main.py
```

Neste modo:
- ✅ A IA lê e analisa os e-mails
- ✅ A IA sugere respostas
- ❌ **NADA é enviado sem você aprovar!**
- Você vê a resposta sugerida e digita `sim`, `não` ou `editar`

### Modo Automático (SEM aprovação - CUIDADO!)

```bash
python src/main.py --no-approval
```

⚠️ **Atenção:** Este modo envia e-mails automaticamente sem sua aprovação!

### Ver Ajuda Completa

```bash
python src/main.py --help
```

---

## 📋 Resumo dos Comandos

| Comando | O que faz | Aprovação necessária? |
|---------|-----------|----------------------|
| `python src/main.py` | Processa e-mails uma vez | ✅ SIM (padrão) |
| `python src/main.py --continuous` | Roda continuamente (a cada 15min) | ✅ SIM (padrão) |
| `python src/main.py --no-approval` | Processa e-mails automaticamente | ❌ NÃO (cuidado!) |
| `python src/main.py --continuous --no-approval` | Automação total 24/7 | ❌ NÃO (use com cautela) |
| `python src/main.py --interval 30` | Roda a cada 30 minutos | ✅ SIM |

---

## 🎯 Fluxo de Uso Recomendado (COM APROVAÇÃO)

1. **Execute o sistema:**
   ```bash
   python src/main.py
   ```

2. **Para cada e-mail novo:**
   - O sistema lê e analisa o e-mail
   - A IA classifica (frio/morno/quente)
   - A IA gera uma resposta sugerida
   - **Você vê a resposta na tela**
   - Digite:
     - `sim` → Envia a resposta
     - `não` → Não envia, apenas marca como lido
     - `editar` → Você edita o texto antes de enviar

3. **Follow-ups:**
   - O sistema agenda follow-ups automaticamente
   - Quando chegar a hora, ele mostra a mensagem sugerida
   - Você aprova ou edita antes de enviar

---

## ❓ Problemas Comuns

### Erro: "GOOGLE_API_KEY não configurado"
- Verifique se copiou a chave corretamente no `.env`
- Teste a chave em: https://aistudio.google.com/app/apikey

### Erro: "OUTLOOK_CLIENT_ID não configurado"
- Complete o passo 3 (registro no Azure)
- Verifique se o `.env` está na pasta raiz do projeto

### Erro de autenticação do Outlook
- Execute o script pela primeira vez para autorizar
- Uma janela do navegador abrirá para login
- Faça login com sua conta Microsoft/Outlook

---

## 🎉 Pronto!

Agora seu sistema está funcional e **SEGURO** - nenhum e-mail será enviado sem sua aprovação!

Dúvidas? Consulte a documentação completa em `/docs/`.
