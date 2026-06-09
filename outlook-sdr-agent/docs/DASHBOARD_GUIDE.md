# 🌐 Guia do Dashboard Web - SDR Agent

## 🎉 Interface Visual Elegante e Moderna!

Agora você tem um **dashboard visual lindo** para gerenciar seus e-mails e aprovar respostas!

---

## 🚀 Como Usar o Dashboard

### 1. Instalar Dependências Web

```bash
cd /workspace/outlook-sdr-agent
pip install -r requirements.txt
```

### 2. Configurar Credenciais (se ainda não fez)

```bash
cp .env.example .env
# Edite .env com suas credenciais do Azure e Google Gemini
```

### 3. Iniciar o Dashboard

```bash
python web/app.py
```

### 4. Acessar no Navegador

Abra seu navegador e acesse:
```
http://localhost:5000
```

---

## ✨ Funcionalidades do Dashboard

### 📊 Painel de Estatísticas
- **E-mails Pendentes**: Quantidade de e-mails aguardando aprovação
- **Respostas Enviadas**: Total de e-mails já enviados
- **Follow-ups Criados**: Follow-ups agendados
- **Reuniões Agendadas**: Reuniões marcadas

### 📨 Gestão de E-mails

Para cada e-mail recebido, você vê:
- ✅ **Assunto e Remetente**
- 🏷️ **Classificação**: Hot/Warm/Cold + Intenção
- 💡 **Resposta Sugerida pela IA**
- ⚡ **Ações Rápidas**:
  - **Aprovar e Enviar** → Envia imediatamente
  - **Editar** → Modifica a resposta antes de enviar
  - **Rejeitar** → Descarta e marca como lido

### 🔄 Atualização em Tempo Real
- **Auto-refresh**: A cada 30 segundos
- **WebSocket**: Notificações instantâneas quando ações são realizadas
- **Botão Manual**: Atualize quando quiser

### ✏️ Editor de Respostas
- Clique em "Editar" para modificar a resposta sugerida
- Editor de texto completo
- Salve e aprove depois

---

## 🎨 Design Premium

O dashboard possui:
- 🌈 **Gradiente Moderno**: Roxo/azul elegante
- 🪟 **Glassmorphism**: Efeito de vidro fosco
- 📱 **Responsivo**: Funciona em desktop e mobile
- ⚡ **Animações Suaves**: Transições elegantes
- 🔔 **Notificações Toast**: Feedback visual das ações
- 🎯 **Tags Coloridas**: Identificação rápida de leads

---

## 🔐 Segurança

**Nenhum e-mail é enviado sem sua aprovação!**

- ✅ Aprovação manual obrigatória por padrão
- ✏️ Opção de editar antes de enviar
- ❌ Rejeição simples com um clique
- 🛡️ Confirmação antes de ações importantes

---

## 📱 Como Funciona o Fluxo

```
1. E-mail chega no Outlook
   ↓
2. IA analisa e gera resposta
   ↓
3. Dashboard mostra o e-mail + resposta sugerida
   ↓
4. VOCÊ decide:
   - ✅ Aprovar → Envia
   - ✏️ Editar → Modifica → Envia
   - ❌ Rejeitar → Ignora
```

---

## 🛠️ Comandos Úteis

### Iniciar Dashboard
```bash
python web/app.py
```

### Ver Logs
```bash
tail -f logs/sdr_agent.log
```

### Parar Servidor
Pressione `Ctrl+C` no terminal

---

## 🎯 Dicas de Uso

1. **Mantenha o dashboard aberto** enquanto trabalha
2. **Revise as respostas** antes de aprovar (a IA pode errar)
3. **Use o editor** para personalizar mensagens importantes
4. **Monitore as estatísticas** para acompanhar produtividade
5. **Atualize manualmente** se quiser verificar novos e-mails imediatamente

---

## 🔧 Personalização

### Mudar Porta
Edite `web/app.py` e altere:
```python
socketio.run(app, debug=True, port=5000, host='0.0.0.0')
# Mude port=5000 para outra porta
```

### Acessar de Outro Dispositivo
O servidor roda em `0.0.0.0`, então você pode acessar de qualquer dispositivo na mesma rede:
```
http://SEU_IP:5000
```

---

## 📸 Preview

O dashboard inclui:
- **Header** com logo e status online
- **Cards de estatísticas** com ícones coloridos
- **Lista de e-mails** com cards interativos
- **Tags de classificação** (Hot/Warm/Cold)
- **Botões de ação** coloridos e intuitivos
- **Modal de edição** para respostas
- **Notificações toast** no canto superior direito

---

## 🆘 Problemas Comuns

### Erro: "Port already in use"
```bash
# Mude a porta ou mate o processo usando a porta 5000
lsof -ti:5000 | xargs kill
```

### Dashboard não carrega
```bash
# Verifique se as dependências estão instaladas
pip install flask flask-socketio eventlet
```

### E-mails não aparecem
- Verifique se configurou corretamente o `.env`
- Confira se há e-mails não lidos no Outlook
- Clique em "Atualizar" para forçar refresh

---

## 🎊 Pronto!

Agora você tem uma **interface profissional e bonita** para gerenciar suas vendas!

**Acesse:** http://localhost:5000

**Lembre-se:** Nenhum e-mail será enviado sem sua aprovação! ✅
