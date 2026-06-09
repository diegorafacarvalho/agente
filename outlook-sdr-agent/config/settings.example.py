"""
Configurações do Outlook SDR Agent

Copie este arquivo para settings.py e preencha com suas credenciais.
NUNCA commit o arquivo settings.py com credenciais reais!
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Configurações do Outlook/Microsoft
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_TENANT_ID: str = ""
    OUTLOOK_EMAIL: str = ""
    
    # Configurações de IA - MÚLTIPLAS OPÇÕES (GRÁTIS e PAGAS)
    
    # Opção 1: Google Gemini (RECOMENDADO - GRÁTIS)
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-pro"
    
    # Opção 2: OpenAI (PAGO - mas tem trial gratuito)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # Opção 3: Ollama (GRÁTIS - roda localmente)
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Configurações de Follow-up
    FOLLOWUP_INITIAL_HOURS: int = 24  # Horas para primeiro follow-up
    FOLLOWUP_SECOND_HOURS: int = 72   # Horas para segundo follow-up
    FOLLOWUP_MAX_ATTEMPTS: int = 3    # Máximo de tentativas
    
    # Configurações de Agendamento
    MEETING_DURATION_MINUTES: int = 30
    WORKING_HOURS_START: int = 9      # 9 AM
    WORKING_HOURS_END: int = 18       # 6 PM
    
    # Banco de Dados
    DATABASE_URL: str = "sqlite:///data/sdr_agent.db"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/sdr_agent.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Configuração de exemplo para ambiente de desenvolvimento
settings = Settings()

# Validação básica e mensagens informativas
if not settings.OUTLOOK_CLIENT_ID:
    print("⚠️  AVISO: OUTLOOK_CLIENT_ID não configurado!")

# Verifica qual IA está configurada
configured_ais = []
if settings.GOOGLE_API_KEY:
    configured_ais.append("✅ Google Gemini (GRÁTIS)")
if settings.OPENAI_API_KEY:
    configured_ais.append("✅ OpenAI (PAGO)")
if settings.OLLAMA_BASE_URL:
    configured_ais.append("✅ Ollama (GRÁTIS - local)")

if configured_ais:
    print("\n🤖 IAs Configuradas:")
    for ai in configured_ais:
        print(f"   {ai}")
else:
    print("\n⚠️  AVISO: Nenhuma IA configurada!")
    print("💡 DICA: Configure GOOGLE_API_KEY para usar Gemini grátis!")
    print("   Obtenha sua chave em: https://makersuite.google.com/app/apikey")
