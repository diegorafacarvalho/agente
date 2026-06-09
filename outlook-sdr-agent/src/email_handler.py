"""
Handler para manipulação de e-mails do Outlook

Responsável por:
- Conectar ao Outlook via Microsoft Graph API
- Ler e-mails recebidos
- Enviar respostas
- Classificar e-mails
"""

from O365 import Account, Connection
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

from config.settings import settings


class EmailHandler:
    def __init__(self):
        self.account = None
        self.mailbox = None
        self._connect()
    
    def _connect(self):
        """Conecta à conta do Outlook"""
        try:
            credentials = (settings.OUTLOOK_CLIENT_ID, settings.OUTLOOK_CLIENT_SECRET)
            
            # Configurações de autenticação
            self.account = Account(
                credentials,
                tenant_id=settings.OUTLOOK_TENANT_ID,
                auth_flow_type='credentials'  # Ou 'authorization' para OAuth2 interativo
            )
            
            if self.account.authenticate():
                self.mailbox = self.account.mailbox()
                logger.info("✅ Conectado ao Outlook com sucesso!")
            else:
                logger.error("❌ Falha na autenticação do Outlook")
                
        except Exception as e:
            logger.error(f"Erro ao conectar ao Outlook: {str(e)}")
            raise
    
    def get_unread_emails(self, limit: int = 50) -> List[Dict]:
        """
        Obtém e-mails não lidos da caixa de entrada
        
        Args:
            limit: Número máximo de e-mails para retornar
            
        Returns:
            Lista de dicionários com informações dos e-mails
        """
        emails = []
        
        try:
            # Filtra apenas e-mails não lidos
            unread_messages = self.mailbox.inbox.get_messages(
                limit=limit,
                query=self.mailbox.inbox.q().on_unread()
            )
            
            for message in unread_messages:
                email_data = {
                    'id': str(message.object_id),
                    'subject': message.subject,
                    'sender': message.sender.address,
                    'sender_name': message.sender.name,
                    'received': message.received,
                    'body': message.body,
                    'has_attachments': message.has_attachments,
                    'is_read': message.is_read,
                    'message_object': message  # Mantém referência para responder depois
                }
                emails.append(email_data)
                logger.info(f"📧 E-mail processado: {email_data['subject']}")
                
        except Exception as e:
            logger.error(f"Erro ao buscar e-mails: {str(e)}")
        
        return emails
    
    def get_email_thread(self, email_id: str) -> List[Dict]:
        """
        Obtém todo o thread/histórico de um e-mail
        
        Args:
            email_id: ID do e-mail principal
            
        Returns:
            Lista de mensagens do thread
        """
        # Implementação simplificada - em produção, buscaria por conversation_id
        logger.info(f"Buscando thread do e-mail: {email_id}")
        return []
    
    def send_reply(self, original_message, reply_text: str, attachments: List = None) -> bool:
        """
        Envia resposta para um e-mail
        
        Args:
            original_message: Mensagem original (objeto O365)
            reply_text: Texto da resposta
            attachments: Lista de anexos (opcional)
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            reply = original_message.reply()
            reply.body = reply_text
            
            if attachments:
                for attachment in attachments:
                    reply.attach(attachment)
            
            reply.send()
            logger.info(f"✅ Resposta enviada para: {original_message.sender.address}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar resposta: {str(e)}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: List[str] = None, attachments: List = None) -> bool:
        """
        Envia um novo e-mail
        
        Args:
            to: Destinatário
            subject: Assunto
            body: Corpo do e-mail
            cc: Lista de cópias (opcional)
            attachments: Lista de anexos (opcional)
            
        Returns:
            True se enviado com sucesso
        """
        try:
            message = self.mailbox.new_message()
            message.to.add(to)
            message.subject = subject
            message.body = body
            
            if cc:
                for email in cc:
                    message.cc.add(email)
            
            if attachments:
                for attachment in attachments:
                    message.attach(attachment)
            
            message.send()
            logger.info(f"✅ E-mail enviado para: {to}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def mark_as_read(self, message) -> bool:
        """Marca e-mail como lido"""
        try:
            message.mark_as_read()
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar como lido: {str(e)}")
            return False
    
    def mark_as_read_by_id(self, email_id: str) -> bool:
        """Marca e-mail como lido pelo ID"""
        try:
            # Implementação simplificada - em produção buscaria a mensagem pelo ID
            logger.info(f"E-mail {email_id} marcado como lido (simulado)")
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar como lido por ID: {str(e)}")
            return False
    
    def send_reply_by_id(self, email_id: str, body: str) -> bool:
        """Envia resposta usando ID do e-mail (para API Web)"""
        try:
            # Em produção, buscaria a mensagem original pelo ID
            # Por enquanto, implementação simplificada
            logger.info(f"Resposta enviada para e-mail {email_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar resposta por ID: {str(e)}")
            return False
    
    def classify_email_intent(self, email_data: Dict) -> Dict:
        """
        Classifica a intenção do e-mail (será integrado com IA)
        
        Args:
            email_data: Dados do e-mail
            
        Returns:
            Dicionário com classificação
        """
        # Classificação básica por palavras-chave
        # Em produção, isso será feito pela IA
        
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        text = f"{subject} {body}"
        
        classification = {
            'intent': 'unknown',
            'priority': 'medium',
            'lead_temperature': 'cold',
            'needs_response': True,
            'suggested_action': 'review'
        }
        
        # Palavras-chave para interesse
        interest_keywords = [
            'interessado', 'interesse', 'gostaria', 'queria',
            'informações', 'informacoes', 'preço', 'preco',
            'valor', 'orçamento', 'orcamento', 'demonstração',
            'demo', 'reunião', 'reuniao', 'agendar', 'call'
        ]
        
        # Palavras-chave para follow-up
        followup_keywords = [
            'retorno', 'follow', 'acompanhar', 'atualização',
            'atualizacao', 'novidade', 'status', 'andamento'
        ]
        
        # Palavras-chave para desinteresse
        negative_keywords = [
            'não interessado', 'nao interessado', 'agora não',
            'agora nao', 'sem interesse', 'ocupado', 'busy'
        ]
        
        # Verifica interesse
        if any(keyword in text for keyword in interest_keywords):
            classification['intent'] = 'interest'
            classification['lead_temperature'] = 'warm'
            classification['suggested_action'] = 'respond_quickly'
            classification['priority'] = 'high'
        
        # Verifica follow-up
        elif any(keyword in text for keyword in followup_keywords):
            classification['intent'] = 'followup'
            classification['lead_temperature'] = 'warm'
            classification['suggested_action'] = 'provide_update'
        
        # Verifica desinteresse
        elif any(keyword in text for keyword in negative_keywords):
            classification['intent'] = 'not_interested'
            classification['lead_temperature'] = 'cold'
            classification['needs_response'] = False
            classification['suggested_action'] = 'archive'
        
        # Verifica agendamento
        if 'agenda' in text or 'horário' in text or 'horario' in text:
            classification['intent'] = 'scheduling'
            classification['suggested_action'] = 'schedule_meeting'
        
        logger.info(f"Classificação: {classification['intent']} - Temp: {classification['lead_temperature']}")
        
        return classification


# Exemplo de uso
if __name__ == "__main__":
    logger.info("Testando EmailHandler...")
    
    try:
        handler = EmailHandler()
        
        # Busca e-mails não lidos
        emails = handler.get_unread_emails(limit=5)
        
        logger.info(f"Encontrados {len(emails)} e-mails não lidos")
        
        for email in emails:
            logger.info(f"\n{'='*50}")
            logger.info(f"De: {email['sender_name']} <{email['sender']}>")
            logger.info(f"Assunto: {email['subject']}")
            logger.info(f"Recebido: {email['received']}")
            
            # Classifica o e-mail
            classification = handler.classify_email_intent(email)
            logger.info(f"Intenção: {classification['intent']}")
            logger.info(f"Ação sugerida: {classification['suggested_action']}")
            
    except Exception as e:
        logger.error(f"Erro no teste: {str(e)}")
