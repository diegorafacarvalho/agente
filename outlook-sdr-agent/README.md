# Outlook SDR Agent - Agente de Vendas Inteligente

Agente autônomo para atuar como SDR/BDR no Outlook, realizando:
- Análise de e-mails trocados
- Respostas automáticas inteligentes
- Follow-up automático
- Agendamento de reuniões
- Qualificação de leads

## Estrutura do Projeto

```
outlook-sdr-agent/
├── src/                    # Código fonte
│   ├── email_handler.py    # Manipulação de e-mails
│   ├── ai_agent.py         # Agente de IA para respostas
│   ├── follow_up.py        # Sistema de follow-up
│   ├── scheduler.py        # Agendamento de reuniões
│   └── main.py             # Ponto de entrada
├── config/                 # Configurações
│   └── settings.py         # Configurações do sistema
├── data/                   # Dados persistentes
├── tests/                  # Testes
├── logs/                   # Logs do sistema
├── requirements.txt        # Dependências
└── README.md               # Este arquivo
```

## Funcionalidades

### 1. **Análise de E-mails**
- Lê e-mails recebidos no Outlook
- Identifica intenções do cliente
- Classifica leads (quente, morno, frio)

### 2. **Respostas Automáticas**
- Gera respostas contextualizadas usando IA
- Mantém tom profissional e persuasivo
- Personaliza baseado no histórico

### 3. **Follow-up Inteligente**
- Agenda follow-ups automáticos
- Define prioridades baseadas em engajamento
- Ajusta timing baseado em respostas

### 4. **Agendamento**
- Integra com calendário
- Sugere horários para reuniões
- Envia convites automaticamente

## Pré-requisitos

- Python 3.9+
- Conta Microsoft/Outlook com API habilitada
- Chave de API para IA (OpenAI ou similar)

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

1. Copie `config/settings.example.py` para `config/settings.py`
2. Preencha suas credenciais do Outlook
3. Configure sua chave de API de IA
4. Ajuste parâmetros de follow-up

## Uso

```bash
python src/main.py
```

## Tecnologias

- **Python** - Linguagem principal
- **Microsoft Graph API** - Integração com Outlook
- **OpenAI/LangChain** - IA para geração de respostas
- **SQLite/PostgreSQL** - Banco de dados
- **APScheduler** - Agendamento de tarefas
