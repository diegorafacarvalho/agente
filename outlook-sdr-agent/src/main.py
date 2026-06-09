"""
SDR Agent - Ponto de Entrada Principal

Orquestra todos os componentes do sistema:
- Email Handler (leitura/resposta de e-mails)
- AI Agent (análise e geração de conteúdo)
- Follow-up Manager (gestão de follow-ups)
- Meeting Scheduler (agendamento de reuniões)
"""

import sys
import time
from datetime import datetime
from loguru import logger
from typing import Dict, Optional

# Configura logs
logger.remove()
logger.add(
    "logs/sdr_agent.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
)

from src.email_handler import EmailHandler
from src.ai_agent import SDRAgent
from src.follow_up import FollowUpManager
from src.scheduler import MeetingScheduler
from config.settings import settings


class SDRAgentSystem:
    """Sistema principal do SDR Agent"""
    
    def __init__(self):
        logger.info("🚀 Inicializando SDR Agent System...")
        
        self.email_handler = EmailHandler()
        self.ai_agent = SDRAgent()
        self.followup_manager = FollowUpManager()
        self.scheduler = MeetingScheduler()
        
        # Estatísticas da sessão
        self.stats = {
            'emails_processed': 0,
            'responses_sent': 0,
            'followups_created': 0,
            'meetings_scheduled': 0,
            'errors': 0
        }
        
        logger.info("✅ Sistema inicializado com sucesso!")
    
    def process_inbox(self, limit: int = 50, auto_respond: bool = False, require_approval: bool = True) -> Dict:
        """
        Processa caixa de entrada
        
        Args:
            limit: Máximo de e-mails para processar
            auto_respond: Se deve responder automaticamente (ignorado se require_approval=True)
            require_approval: Se exige aprovação humana antes de enviar (PADRÃO: True)
            
        Returns:
            Estatísticas do processamento
        """
        logger.info("\n" + "="*60)
        logger.info("📬 Processando caixa de entrada...")
        if require_approval:
            logger.info("⚠️  MODO DE APROVAÇÃO ATIVADO (Nada será enviado sem seu OK)")
        logger.info("="*60)
        
        emails = self.email_handler.get_unread_emails(limit=limit)
        
        if not emails:
            logger.info("✨ Nenhum e-mail novo para processar!")
            return self.stats
        
        logger.info(f"📧 {len(emails)} e-mails encontrados")
        
        for email in emails:
            try:
                self._process_single_email(email, auto_respond, require_approval)
                self.stats['emails_processed'] += 1
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar e-mail: {str(e)}")
                self.stats['errors'] += 1
        
        return self.stats
    
    def _process_single_email(self, email: Dict, auto_respond: bool, require_approval: bool):
        """Processa um único e-mail"""
        logger.info(f"\n{'-'*50}")
        logger.info(f"Processando: {email['subject']}")
        logger.info(f"De: {email['sender_name']} <{email['sender']}>")
        
        # Classifica o e-mail
        classification = self.email_handler.classify_email_intent(email)
        logger.info(f"Classificação: {classification['intent']} | Temp: {classification['lead_temperature']}")
        
        # Analisa com IA
        analysis = self.ai_agent.analyze_email(email)
        
        # Decide ação baseada na análise
        action = analysis.get('next_action', 'review')
        logger.info(f"Ação recomendada: {action}")
        
        if action == 'archive' or not classification['needs_response']:
            logger.info("⏭️  E-mail arquivado (sem resposta necessária)")
            self.email_handler.mark_as_read(email['message_object'])
            return
        
        if action in ['send_email', 'respond_quickly', 'provide_update']:
            # Gera resposta
            response_text = self.ai_agent.generate_response(email, analysis)
            
            logger.info("\n💡 RESPOSTA SUGERIDA PELA IA:")
            logger.info("="*40)
            logger.info(response_text)
            logger.info("="*40)
            
            should_send = False
            
            if require_approval:
                # Pede aprovação do usuário
                user_input = input("\n🤔 Deseja enviar esta resposta? (sim/não/editar): ").strip().lower()
                
                if user_input in ['sim', 's', 'y', 'yes', 'aprovar']:
                    should_send = True
                    logger.info("✅ Resposta aprovada pelo usuário.")
                elif user_input in ['editar', 'e']:
                    logger.info("✏️  Editando resposta... (Cole o texto final abaixo)")
                    response_text = input("Nova resposta:\n")
                    should_send = True
                    logger.info("✅ Resposta editada e aprovada.")
                else:
                    logger.info("❌ Resposta rejeitada. E-mail apenas marcado como lido.")
                    self.email_handler.mark_as_read(email['message_object'])
                    return
            elif auto_respond:
                # Modo automático (apenas se require_approval=False)
                should_send = True
                logger.info("⚡ Envio automático (modo sem aprovação).")
            
            if should_send:
                # Envia resposta
                success = self.email_handler.send_reply(
                    email['message_object'],
                    response_text
                )
                
                if success:
                    self.stats['responses_sent'] += 1
                    logger.info("✅ Resposta enviada com sucesso!")
                    
                    # Agenda follow-up se necessário
                    followup_days = analysis.get('suggested_followup_days', 3)
                    if followup_days > 0:
                        self.followup_manager.create_followup(
                            lead_id=email['id'],
                            lead_name=email['sender_name'],
                            lead_email=email['sender'],
                            initial_delay_hours=followup_days * 24,
                            priority=analysis.get('lead_temperature', 'medium')
                        )
                        self.stats['followups_created'] += 1
                
                # Marca como lido
                self.email_handler.mark_as_read(email['message_object'])
        
        # Verifica interesse em reunião
        if analysis.get('meeting_interest', False) or action == 'schedule_meeting':
            logger.info("📅 Interesse em reunião detectado!")
            self._handle_meeting_request(email, analysis)
    
    def _handle_meeting_request(self, email: Dict, analysis: Dict):
        """Gerencia solicitação de reunião"""
        available_slots = self.scheduler.get_available_slots()
        
        if available_slots:
            # Envia proposta de horários
            self.scheduler.send_meeting_invite(
                email=email['sender'],
                name=email['sender_name'],
                proposed_times=[slot['start'] for slot in available_slots[:3]],
                subject=email['subject']
            )
            logger.info("📧 Proposta de reunião enviada")
    
    def process_followups(self, auto_send: bool = False, require_approval: bool = True) -> Dict:
        """
        Processa follow-ups pendentes
        
        Args:
            auto_send: Se deve enviar automaticamente (ignorado se require_approval=True)
            require_approval: Se exige aprovação humana antes de enviar (PADRÃO: True)
            
        Returns:
            Estatísticas
        """
        logger.info("\n" + "="*60)
        logger.info("📬 Processando follow-ups pendentes...")
        if require_approval:
            logger.info("⚠️  MODO DE APROVAÇÃO ATIVADO (Nada será enviado sem seu OK)")
        logger.info("="*60)
        
        due_followups = self.followup_manager.get_due_followups()
        
        if not due_followups:
            logger.info("✨ Nenhum follow-up pendente!")
            return self.stats
        
        logger.info(f"📋 {len(due_followups)} follow-ups vencidos")
        
        for task in due_followups:
            try:
                logger.info(f"\nFollow-up: {task.lead_name} (Tentativa {task.attempt_number})")
                
                # Prepara dados do lead
                lead_data = {
                    'name': task.lead_name,
                    'email': task.lead_email,
                    'last_contact': task.last_contact,
                    'attempt_number': task.attempt_number
                }
                
                # Gera mensagem de follow-up
                days_since = (datetime.now() - task.last_contact).days
                followup_message = self.ai_agent.generate_followup(lead_data, days_since)
                
                logger.info("\n💡 FOLLOW-UP SUGERIDO PELA IA:")
                logger.info("="*40)
                logger.info(followup_message)
                logger.info("="*40)
                
                should_send = False
                
                if require_approval:
                    # Pede aprovação do usuário
                    user_input = input("\n🤔 Deseja enviar este follow-up? (sim/não/editar): ").strip().lower()
                    
                    if user_input in ['sim', 's', 'y', 'yes', 'aprovar']:
                        should_send = True
                        logger.info("✅ Follow-up aprovado pelo usuário.")
                    elif user_input in ['editar', 'e']:
                        logger.info("✏️  Editando follow-up... (Cole o texto final abaixo)")
                        followup_message = input("Nova mensagem:\n")
                        should_send = True
                        logger.info("✅ Follow-up editado e aprovado.")
                    else:
                        logger.info("❌ Follow-up rejeitado. Apenas registrado como visualizado.")
                        self.followup_manager.mark_completed(task)
                        continue
                elif auto_send:
                    # Modo automático (apenas se require_approval=False)
                    should_send = True
                    logger.info("⚡ Envio automático (modo sem aprovação).")
                
                if should_send:
                    # Envia follow-up
                    success = self.email_handler.send_email(
                        to=task.lead_email,
                        subject=f"Follow-up: {task.lead_name}",
                        body=followup_message
                    )
                    
                    if success:
                        self.stats['responses_sent'] += 1
                        logger.info("✅ Follow-up enviado com sucesso!")
                        
                        # Agenda próximo follow-up
                        self.followup_manager.schedule_next_followup(task)
                        self.followup_manager.mark_completed(task)
                
            except Exception as e:
                logger.error(f"❌ Erro no follow-up: {str(e)}")
                self.stats['errors'] += 1
        
        # Estatísticas
        stats = self.followup_manager.get_stats()
        logger.info(f"\n📊 Estatísticas de Follow-up:")
        logger.info(f"   Total: {stats['total']}")
        logger.info(f"   Pendentes: {stats['pending']}")
        logger.info(f"   Completados: {stats['completed']}")
        logger.info(f"   Taxa: {stats['completion_rate']:.1f}%")
        
        return self.stats
    
    def run_continuous(self, interval_minutes: int = 15, require_approval: bool = True):
        """
        Roda o sistema continuamente
        
        Args:
            interval_minutes: Intervalo entre execuções
            require_approval: Se exige aprovação humana (PADRÃO: True - seguro)
        """
        if require_approval:
            logger.warning("⚠️  ATENÇÃO: Modo contínuo COM aprovação requer interação humana!")
            logger.warning("Use --no-approval se quiser automação total (cuidado!)")
            logger.info("")
        
        logger.info(f"🔄 Iniciando modo contínuo (intervalo: {interval_minutes}min)")
        logger.info("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                logger.info(f"\n{'='*60}")
                logger.info(f"🕐 Ciclo iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                logger.info(f"{'='*60}")
                
                # Processa e-mails
                self.process_inbox(auto_respond=not require_approval, require_approval=require_approval)
                
                # Processa follow-ups
                self.process_followups(auto_send=not require_approval, require_approval=require_approval)
                
                # Resumo da sessão
                logger.info(f"\n📊 Resumo da Sessão:")
                logger.info(f"   E-mails processados: {self.stats['emails_processed']}")
                logger.info(f"   Respostas enviadas: {self.stats['responses_sent']}")
                logger.info(f"   Follow-ups criados: {self.stats['followups_created']}")
                logger.info(f"   Erros: {self.stats['errors']}")
                
                # Aguarda próximo ciclo
                logger.info(f"\n⏳ Próximo ciclo em {interval_minutes} minutos...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("\n\n👋 Sistema encerrado pelo usuário")
            logger.info(f"\n📊 Estatísticas Finais:")
            for key, value in self.stats.items():
                logger.info(f"   {key}: {value}")


def main():
    """Função principal"""
    logger.info("="*60)
    logger.info("🤖 OUTLOOK SDR AGENT")
    logger.info("Agente Inteligente de Vendas")
    logger.info("="*60)
    
    # Verifica configurações
    if not settings.OUTLOOK_CLIENT_ID:
        logger.error("❌ OUTLOOK_CLIENT_ID não configurado!")
        logger.error("Configure suas credenciais em config/settings.py")
        return
    
    # Inicializa sistema
    system = SDRAgentSystem()
    
    # Modo de operação
    import argparse
    parser = argparse.ArgumentParser(description='SDR Agent - Automação de Vendas')
    parser.add_argument('--continuous', action='store_true', help='Rodar continuamente')
    parser.add_argument('--interval', type=int, default=15, help='Intervalo em minutos (modo contínuo)')
    parser.add_argument('--no-approval', action='store_true', help='⚠️  CUIDADO: Enviar e-mails SEM aprovação (automação total)')
    parser.add_argument('--demo', action='store_true', help='Rodar em modo demonstração')
    
    args = parser.parse_args()
    
    # Define se requer aprovação (PADRÃO: SIM, requer aprovação)
    require_approval = not args.no_approval
    
    if args.demo:
        logger.info("\n🎭 MODO DEMONSTRAÇÃO")
        logger.info("(Simulação sem enviar e-mails reais)")
        # Aqui poderia ter lógica de demo
    
    if args.continuous:
        system.run_continuous(interval_minutes=args.interval, require_approval=require_approval)
    else:
        # Execução única
        logger.info(f"\n{'✅ COM APROVAÇÃO' if require_approval else '⚠️  AUTOMAÇÃO TOTAL (sem aprovação)'}")
        system.process_inbox(auto_respond=not require_approval, require_approval=require_approval)
        system.process_followups(auto_send=not require_approval, require_approval=require_approval)
        
        logger.info("\n✅ Processamento concluído!")
        logger.info(f"E-mails: {system.stats['emails_processed']}")
        logger.info(f"Respostas: {system.stats['responses_sent']}")


if __name__ == "__main__":
    main()
