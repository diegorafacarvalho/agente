# 🆓 IAs Gratuitas para o Outlook SDR Agent

O sistema agora suporta **múltiplas opções de IA**, incluindo várias opções **100% GRATUITAS**!

## 🎯 Opções Disponíveis

### 1. Google Gemini ⭐ (RECOMENDADO)
**Status:** GRÁTIS | **Qualidade:** Excelente | **Facilidade:** Muito Fácil

- ✅ Totalmente gratuito (até 60 requisições por minuto)
- ✅ Modelo de ponta do Google
- ✅ Não precisa instalar nada localmente
- ✅ Ótimo para português

**Como obter sua chave:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

**Configuração:**
```bash
# No arquivo .env
GOOGLE_API_KEY=sua_chave_aqui
```

**Limites:**
- 60 requisições por minuto (grátis)
- 1.500 requisições por dia (grátis)
- Mais que suficiente para uso pessoal/pequenas empresas

---

### 2. Ollama 🦙
**Status:** GRÁTIS | **Qualidade:** Boa | **Facilidade:** Média

- ✅ Totalmente gratuito e open source
- ✅ Roda localmente no seu computador (privacidade total)
- ✅ Vários modelos disponíveis (Llama2, Mistral, etc.)
- ❌ Precisa instalar o Ollama
- ❌ Requer hardware razoável (8GB+ RAM recomendado)

**Como instalar:**
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Baixe em: https://ollama.ai/download

# Depois instale um modelo:
ollama pull llama2
```

**Configuração:**
```bash
# No arquivo .env (opcional, já vem configurado)
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

**Modelos recomendados:**
- `llama2` - Bom equilíbrio entre qualidade e velocidade
- `mistral` - Mais rápido, bom para e-mails curtos
- `codellama` - Se quiser testar código também

---

### 3. Hugging Face 🤗
**Status:** GRÁTIS | **Qualidade:** Variável | **Facilidade:** Difícil

- ✅ Modelos open source
- ✅ Totalmente gratuito
- ❌ Configuração mais complexa
- ❌ Pode ser lento dependendo do modelo

**Configuração:** (ainda em desenvolvimento)

---

### 4. OpenAI GPT 💰
**Status:** PAGO (com trial grátis) | **Qualidade:** Excelente | **Facilidade:** Fácil

- ✅ Melhor qualidade geral
- ✅ Trial gratuito de $5 dólares novos usuários
- ❌ Pago após esgotar créditos
- ❌ Requer cartão de crédito

**Como obter:**
1. Acesse: https://platform.openai.com
2. Crie uma conta
3. Gere uma API Key

**Configuração:**
```bash
# No arquivo .env
OPENAI_API_KEY=sk-...
```

---

## 🏆 Minha Recomendação

### Para a maioria dos usuários: **Google Gemini**
- É grátis
- Qualidade excelente
- Super fácil de configurar
- Não requer instalação de nada

### Para quem prioriza privacidade: **Ollama**
- Roda tudo localmente
- Seus dados não saem do seu computador
- Totalmente grátis
- Mas requer hardware decente

### Para empresas/com uso intensivo: **OpenAI**
- Melhor qualidade
- Mais estável
- Suporte empresarial
- Mas é pago

---

## 📊 Comparação Rápida

| IA | Preço | Qualidade | Facilidade | Privacidade |
|----|-------|-----------|------------|-------------|
| **Gemini** | Grátis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Ollama** | Grátis | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **OpenAI** | Pago | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Fallback** | Grátis | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 Começando Agora (Recomendado: Gemini)

### Passo 1: Obter Chave Gemini (2 minutos)
1. Acesse https://makersuite.google.com/app/apikey
2. Login Google
3. Criar API Key
4. Copiar chave

### Passo 2: Configurar .env
```bash
cd /workspace/outlook-sdr-agent
cp .env.example .env
```

Edite o `.env`:
```
GOOGLE_API_KEY=AIzaSy...sua_chave_aqui
```

### Passo 3: Instalar dependências
```bash
pip install google-generativeai langchain-google-genai
```

### Passo 4: Testar
```bash
python src/main.py --test-ai
```

Pronto! 🎉

---

## ❓ FAQ

### O Gemini é realmente grátis?
Sim! O Google oferece um tier gratuito generoso que é mais que suficiente para uso pessoal ou pequenas empresas.

### Posso trocar de IA depois?
Sim! Basta mudar as variáveis de ambiente no `.env`. O sistema detecta automaticamente qual IA usar.

### O que acontece se eu não configurar nenhuma IA?
O sistema usa um modo fallback com regras básicas. Funciona, mas as respostas são menos inteligentes.

### Quantos e-mails consigo processar por dia?
- **Gemini:** ~1.500 e-mails/dia (grátis)
- **Ollama:** Ilimitado (depende do seu hardware)
- **Fallback:** Ilimitado

### Preciso de cartão de crédito?
- **Gemini:** NÃO
- **Ollama:** NÃO
- **OpenAI:** SIM (mas tem $5 grátis de trial)

---

## 🔗 Links Úteis

- [Google Gemini API](https://makersuite.google.com/app/apikey)
- [Ollama Download](https://ollama.ai/download)
- [OpenAI Platform](https://platform.openai.com)
- [Documentação LangChain](https://python.langchain.com)

---

**Dúvidas?** Consulte o README.md principal ou abra uma issue!
