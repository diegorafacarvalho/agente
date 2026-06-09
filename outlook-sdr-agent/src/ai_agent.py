"""
Agente de IA para SDR/BDR

Responsável por:
- Analisar e-mails e contexto
- Gerar respostas inteligentes e personalizadas
- Qualificar leads
- Sugerir próximos passos

SUPORTA MÚLTIPLAS IAs GRATUITAS:
- Google Gemini (recomendado - grátis, rápido, bom)
- Ollama (grátis - roda localmente, precisa instalar)
- Hugging Face (grátis - modelos open source)
- OpenAI (pago - mas tem trial gratuito)
"""

from typing import Dict, List, Optional
from loguru import logger
import json

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_OPENAI_AVAILABLE = True
except ImportError:
    LANGCHAIN_OPENAI_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_GOOGLE_AVAILABLE = True
except ImportError:
    LANGCHAIN_GOOGLE_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from langchain.schema import HumanMessage, SystemMessage, AIMessage
from config.settings import settings


class SDRAgent:
    def __init__(self):
        self.model = None
        self.model_type = None  # 'openai', 'google', 'ollama', 'fallback'
        self._initialize_model()
        
        # Prompt do sistema para o agente SDR
        self.system_prompt = """
Você é um SDR (Sales Development Representative) experiente e profissional, 
trabalhando como assistente virtual de vendas. Seu objetivo é:

1. QUALIFICAR LEADS: Identificar prospects qualificados baseados em:
   - Necessidade real do produto/serviço
   - Autoridade de decisão
   - Orçamento disponível
   - Timing adequado (metodologia BANT)

2. ENGAJAR PROSPECTS: Criar conexões genuínas através de:
   - Respostas personalizadas e relevantes
   - Demonstração de entendimento das dores do cliente
   - Tom profissional mas amigável
   - Chamadas para ação claras

3. AGENDAR REUNIÕES: Converter conversas em reuniões qualificadas:
   - Sugerir horários de forma natural
   - Explicar o valor da reunião
   - Remover objeções sobre o tempo

4. FAZER FOLLOW-UP: Manter o engajamento com:
   - Mensagens de acompanhamento estratégicas
   - Novas informações de valor
   - Persistência sem ser invasivo

DIRETRIZES DE COMUNICAÇÃO:
- Seja conciso (e-mails curtos são mais eficazes)
- Personalize cada mensagem (evite templates genéricos)
- Foque no valor para o cliente, não nas features
- Use perguntas abertas para entender necessidades
- Mantenha tom positivo e prestativo
- Sempre inclua uma call-to-action clara

FORMATO DE RESPOSTA:
Forneça sua resposta em JSON com a seguinte estrutura:
{
    "response_text": "Texto completo da resposta em português",
    "lead_score": 0-100,
    "lead_temperature": "cold|warm|hot",
    "qualification_status": "unqualified|potential|qualified",
    "next_action": "send_email|schedule_call|send_info|followup_later|archive",
    "suggested_followup_days": 0-7,
    "key_insights": ["lista", "de", "insights", "sobre", "o", "prospect"],
    "objections_detected": ["lista", "de", "objeções"],
    "meeting_interest": true|false,
    "confidence_score": 0.0-1.0
}
"""

    def _initialize_model(self):
        """Inicializa o modelo de IA com suporte a múltiplos provedores"""
        
        # Prioridade: Google Gemini > Ollama > OpenAI > Fallback
        
        # 1. Tenta Google Gemini (GRÁTIS)
        if LANGCHAIN_GOOGLE_AVAILABLE and settings.GOOGLE_API_KEY:
            try:
                self.model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.7,
                    google_api_key=settings.GOOGLE_API_KEY
                )
                self.model_type = 'google'
                logger.info("✅ Modelo Google Gemini inicializado! (GRÁTIS)")
                return
            except Exception as e:
                logger.warning(f"Gemini falhou: {str(e)}")
        
        # 2. Tenta Ollama (GRÁTIS - local)
        if OLLAMA_AVAILABLE:
            try:
                # Verifica se Ollama está rodando
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    self.model_type = 'ollama'
                    logger.info("✅ Ollama detectado! (GRÁTIS - local)")
                    return
            except:
                pass
        
        # 3. Tenta OpenAI (PAGO)
        if LANGCHAIN_OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.model = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    temperature=0.7,
                    max_tokens=1000
                )
                self.model_type = 'openai'
                logger.info(f"✅ Modelo {settings.OPENAI_MODEL} inicializado! (PAGO)")
                return
            except Exception as e:
                logger.warning(f"OpenAI falhou: {str(e)}")
        
        # 4. Fallback sem IA
        self.model_type = 'fallback'
        logger.warning("⚠️  Nenhuma IA configurada. Usando modo fallback (regras básicas).")
        logger.info("💡 DICA: Configure GOOGLE_API_KEY para usar Gemini grátis!")
    
    def analyze_email(self, email_data: Dict, context: Dict = None) -> Dict:
        """
        Analisa um e-mail e gera insights
        
        Args:
            email_data: Dados do e-mail (assunto, corpo, remetente, etc.)
            context: Contexto adicional (histórico, empresa, etc.)
            
        Returns:
            Análise completa do e-mail
        """
        logger.info(f"🤖 Analisando e-mail: {email_data.get('subject', 'Sem assunto')}")
        
        # Prepara o prompt
        user_prompt = self._build_analysis_prompt(email_data, context)
        
        if self.model and self.model_type in ['google', 'openai']:
            try:
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = self.model.invoke(messages)
                analysis = self._parse_response(response.content)
                
                logger.info(f"Lead Score: {analysis.get('lead_score', 0)}")
                logger.info(f"Temperatura: {analysis.get('lead_temperature', 'unknown')}")
                
                return analysis
                
            except Exception as e:
                logger.error(f"Erro na análise com IA: {str(e)}")
        
        # Tenta Ollama se disponível
        elif self.model_type == 'ollama':
            try:
                full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
                response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': full_prompt}])
                analysis = self._parse_response(response['message']['content'])
                
                logger.info(f"Lead Score: {analysis.get('lead_score', 0)}")
                logger.info(f"Temperatura: {analysis.get('lead_temperature', 'unknown')}")
                
                return analysis
            except Exception as e:
                logger.error(f"Erro na análise com Ollama: {str(e)}")
        
        # Fallback sem IA
        return self._fallback_analysis(email_data)
    
    def generate_response(self, email_data: Dict, analysis: Dict) -> str:
        """
        Gera resposta para o e-mail baseado na análise
        
        Args:
            email_data: Dados do e-mail original
            analysis: Análise prévia do e-mail
            
        Returns:
            Texto da resposta
        """
        logger.info("📝 Gerando resposta...")
        
        prompt = f"""
Com base na análise abaixo, gere uma resposta profissional e persuasiva em português:

EMAIL ORIGINAL:
Assunto: {email_data.get('subject', '')}
De: {email_data.get('sender_name', 'Desconhecido')} <{email_data.get('sender', '')}>
Data: {email_data.get('received', '')}

CORPO DO EMAIL:
{email_data.get('body', '')}

ANÁLISE DO SDR:
- Lead Score: {analysis.get('lead_score', 0)}
- Temperatura: {analysis.get('lead_temperature', 'unknown')}
- Próxima ação: {analysis.get('next_action', 'review')}
- Insights: {', '.join(analysis.get('key_insights', []))}

Gere uma resposta que:
1. Agradeça o contato
2. Demonstre entendimento da necessidade
3. Ofereça valor específico
4. Inclua uma call-to-action clara
5. Seja concisa (máximo 150 palavras)

Responda APENAS com o texto do e-mail, sem explicações adicionais.
"""
        
        if self.model and self.model_type in ['google', 'openai']:
            try:
                messages = [
                    SystemMessage(content="Você é um SDR profissional escrevendo respostas por e-mail."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.model.invoke(messages)
                return response.content
                
            except Exception as e:
                logger.error(f"Erro ao gerar resposta: {str(e)}")
        
        # Tenta Ollama
        elif self.model_type == 'ollama':
            try:
                response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])
                return response['message']['content']
            except Exception as e:
                logger.error(f"Erro ao gerar resposta com Ollama: {str(e)}")
        
        # Fallback sem IA
        return self._fallback_response(email_data, analysis)
    
    def generate_followup(self, lead_data: Dict, days_since_last_contact: int) -> str:
        """
        Gera mensagem de follow-up
        
        Args:
            lead_data: Dados do lead/histórico
            days_since_last_contact: Dias desde último contato
            
        Returns:
            Texto do follow-up
        """
        logger.info(f"📬 Gerando follow-up ({days_since_last_contact} dias)")
        
        prompt = f"""
Gere uma mensagem de follow-up estratégica em português.

CONTEXTO DO LEAD:
Nome: {lead_data.get('name', 'Prospect')}
Empresa: {lead_data.get('company', 'N/A')}
Último contato: {days_since_last_contact} dias atrás
Interesse demonstrado: {lead_data.get('interest_level', 'médio')}
Última interação: {lead_data.get('last_interaction', 'N/A')}

Crie um follow-up que:
1. Seja breve e direto
2. Traga algo de valor (insight, caso de sucesso, conteúdo relevante)
3. Não pareça desesperado ou insistente
4. Tenha uma call-to-action suave
5. Justifique o motivo do contato

Responda APENAS com o texto do e-mail.
"""
        
        if self.model and self.model_type in ['google', 'openai']:
            try:
                messages = [
                    SystemMessage(content="Você é um SDR criando follow-ups estratégicos."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.model.invoke(messages)
                return response.content
                
            except Exception as e:
                logger.error(f"Erro ao gerar follow-up: {str(e)}")
        
        # Tenta Ollama
        elif self.model_type == 'ollama':
            try:
                response = ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])
                return response['message']['content']
            except Exception as e:
                logger.error(f"Erro ao gerar follow-up com Ollama: {str(e)}")
        
        return self._fallback_followup(lead_data, days_since_last_contact)
    
    def _build_analysis_prompt(self, email_data: Dict, context: Dict = None) -> str:
        """Constrói prompt para análise do e-mail"""
        prompt = f"""
Analise este e-mail recebido:

ASSUNTO: {email_data.get('subject', 'Sem assunto')}
REMETENTE: {email_data.get('sender_name', 'Desconhecido')} <{email_data.get('sender', '')}>
DATA: {email_data.get('received', 'N/A')}

CORPO DO EMAIL:
{email_data.get('body', 'Sem conteúdo')}

{'CONTEXTO ADICIONAL:' if context else ''}
{json.dumps(context, indent=2) if context else 'Nenhum contexto adicional'}

Forneça sua análise no formato JSON especificado.
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parseia a resposta da IA para JSON"""
        try:
            # Tenta extrair JSON do texto
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                logger.warning("Não foi possível extrair JSON da resposta")
                return self._fallback_analysis({})
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON: {str(e)}")
            return self._fallback_analysis({})
    
    def _fallback_analysis(self, email_data: Dict) -> Dict:
        """Análise fallback sem IA"""
        body = email_data.get('body', '').lower()
        subject = email_data.get('subject', '').lower()
        text = f"{body} {subject}"
        
        score = 50
        temperature = "warm"
        
        if any(word in text for word in ['urgente', 'preciso', 'interessado', 'reunião']):
            score = 75
            temperature = "hot"
        elif any(word in text for word in ['não interessado', 'agora não']):
            score = 25
            temperature = "cold"
        
        return {
            "response_text": "Obrigado pelo seu contato. Vamos analisar sua mensagem e retornaremos em breve.",
            "lead_score": score,
            "lead_temperature": temperature,
            "qualification_status": "potential",
            "next_action": "send_email",
            "suggested_followup_days": 3,
            "key_insights": ["Análise básica sem IA"],
            "objections_detected": [],
            "meeting_interest": False,
            "confidence_score": 0.5
        }
    
    def _fallback_response(self, email_data: Dict, analysis: Dict) -> str:
        """Resposta fallback sem IA"""
        sender_name = email_data.get('sender_name', 'Prospect')
        
        return f"""Olá {sender_name},

Obrigado pelo seu contato! 

Recebemos sua mensagem e estamos analisando sua solicitação. 
Um de nossos especialistas entrará em contato em breve para melhor atendê-lo.

Enquanto isso, fique à vontade para visitar nosso site ou responder este e-mail 
caso tenha alguma dúvida adicional.

Atenciosamente,
Equipe de Vendas
"""
    
    def _fallback_followup(self, lead_data: Dict, days: int) -> str:
        """Follow-up fallback sem IA"""
        name = lead_data.get('name', 'Prospect')
        
        return f"""Olá {name},

Espero que esteja bem!

Estou passando apenas para saber se você teve oportunidade de avaliar nossa proposta 
e se há alguma dúvida em que possa ajudar.

Fico à disposição para agendar uma rápida conversa esta semana.

Abraços,
Equipe de Vendas
"""


# Exemplo de uso
if __name__ == "__main__":
    logger.info("Testando SDRAgent...")
    
    agent = SDRAgent()
    
    # E-mail de exemplo
    test_email = {
        'subject': 'Interesse em solução de automação',
        'sender_name': 'João Silva',
        'sender': 'joao@empresa.com.br',
        'received': '2024-01-15 10:30:00',
        'body': """
Olá,

Vi sua apresentação sobre automação de vendas e fiquei muito interessado.
Estamos buscando uma solução para nosso time de 15 pessoas.

Vocês poderiam me enviar mais informações sobre preços e funcionalidades?
Também gostaria de agendar uma demonstração.

Aguardo retorno.

João Silva
Gerente Comercial - Empresa XYZ
"""
    }
    
    # Analisa o e-mail
    analysis = agent.analyze_email(test_email)
    logger.info(f"\nAnálise: {json.dumps(analysis, indent=2)}")
    
    # Gera resposta
    response = agent.generate_response(test_email, analysis)
    logger.info(f"\nResposta gerada:\n{response}")
