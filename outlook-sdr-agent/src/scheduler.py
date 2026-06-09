"""
Agendador de Reuniões

Responsável por:
- Integrar com calendário (Outlook/Google)
- Sugerir horários disponíveis
- Enviar convites de reunião
- Gerenciar confirmações
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json

try:
    from O365 import Account
    O365_AVAILABLE = True
except ImportError:
    O365_AVAILABLE = False
    logger.warning("O365 não disponível. Funcionalidade de calendário limitada.")

from config.settings import settings


class MeetingScheduler:
    def __init__(self):
        self.account = None
        self.schedule = None
        self._connect()
    
    def _connect(self):
        """Conecta ao calendário do Outlook"""
        if not O365_AVAILABLE:
            logger.warning("Calendário indisponível - O365 não instalado")
            return
        
        try:
            credentials = (settings.OUTLOOK_CLIENT_ID, settings.OUTLOOK_CLIENT_SECRET)
            
            self.account = Account(
                credentials,
                tenant_id=settings.OUTLOOK_TENANT_ID,
                auth_flow_type='credentials'
            )
            
            if self.account.authenticate():
                self.schedule = self.account.schedule()
                logger.info("✅ Conectado ao calendário do Outlook!")
            else:
                logger.error("❌ Falha na autenticação do calendário")
                
        except Exception as e:
            logger.error(f"Erro ao conectar ao calendário: {str(e)}")
    
    def get_available_slots(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        duration_minutes: int = None
    ) -> List[Dict]:
        """
        Obtém horários disponíveis na agenda
        
        Args:
            start_date: Data inicial para busca
            end_date: Data final para busca
            duration_minutes: Duração necessária da reunião
            
        Returns:
            Lista de horários disponíveis
        """
        if not self.schedule:
            return self._fallback_available_slots(start_date, end_date, duration_minutes)
        
        try:
            # Define período de busca (próximos 5 dias úteis por padrão)
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=5)
            
            duration = duration_minutes or settings.MEETING_DURATION_MINUTES
            
            # Busca eventos no período
            calendar = self.schedule.get_default_calendar()
            events = calendar.get_events(
                start=start_date,
                end=end_date,
                include_recurring=True
            )
            
            # Extrai horários ocupados
            busy_slots = []
            for event in events:
                busy_slots.append({
                    'start': event.start,
                    'end': event.end,
                    'subject': event.subject
                })
            
            # Gera horários disponíveis
            available = self._find_free_slots(
                busy_slots,
                start_date,
                end_date,
                duration
            )
            
            logger.info(f"📅 Encontrados {len(available)} horários disponíveis")
            return available
            
        except Exception as e:
            logger.error(f"Erro ao buscar horários: {str(e)}")
            return self._fallback_available_slots(start_date, end_date, duration_minutes)
    
    def _find_free_slots(
        self,
        busy_slots: List[Dict],
        start: datetime,
        end: datetime,
        duration_minutes: int
    ) -> List[Dict]:
        """Encontra slots livres entre horários ocupados"""
        available = []
        
        # Horário comercial
        work_start = settings.WORKING_HOURS_START
        work_end = settings.WORKING_HOURS_END
        
        current = start
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current < end:
            # Pula fins de semana
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            # Define início e fim do dia útil
            day_start = current.replace(hour=work_start, minute=0, second=0, microsecond=0)
            day_end = current.replace(hour=work_end, minute=0, second=0, microsecond=0)
            
            if current < day_start:
                current = day_start
            
            # Verifica se há conflito
            slot_end = current + slot_duration
            
            if slot_end > day_end:
                # Pula para próximo dia
                current = current.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                continue
            
            # Verifica conflitos com eventos existentes
            has_conflict = False
            for busy in busy_slots:
                if current < busy['end'] and slot_end > busy['start']:
                    has_conflict = True
                    break
            
            if not has_conflict:
                available.append({
                    'start': current,
                    'end': slot_end,
                    'formatted': current.strftime("%d/%m/%Y às %H:%M")
                })
            
            # Próximo slot (de 30 em 30 minutos)
            current += timedelta(minutes=30)
        
        return available[:10]  # Retorna até 10 opções
    
    def _fallback_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int
    ) -> List[Dict]:
        """Fallback quando calendário não está disponível"""
        logger.info("Usando fallback para horários disponíveis")
        
        available = []
        duration = duration_minutes or 30
        
        if not start_date:
            start_date = datetime.now()
        
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        for _ in range(10):  # 10 slots de exemplo
            if current.weekday() < 5:  # Dias úteis
                available.append({
                    'start': current,
                    'end': current + timedelta(minutes=duration),
                    'formatted': current.strftime("%d/%m/%Y às %H:%M")
                })
            current += timedelta(hours=1)
        
        return available
    
    def schedule_meeting(
        self,
        attendee_email: str,
        attendee_name: str,
        subject: str,
        start_time: datetime,
        duration_minutes: int = None,
        location: str = None,
        body: str = None
    ) -> bool:
        """
        Agenda uma reunião
        
        Args:
            attendee_email: Email do participante
            attendee_name: Nome do participante
            subject: Assunto da reunião
            start_time: Horário de início
            duration_minutes: Duração
            location: Local (opcional)
            body: Descrição (opcional)
            
        Returns:
            True se agendado com sucesso
        """
        if not self.schedule:
            logger.warning("Agendamento indisponível - calendário não conectado")
            return False
        
        try:
            duration = duration_minutes or settings.MEETING_DURATION_MINUTES
            end_time = start_time + timedelta(minutes=duration)
            
            calendar = self.schedule.get_default_calendar()
            meeting = calendar.new_event()
            
            meeting.subject = subject
            meeting.start = start_time
            meeting.end = end_time
            meeting.location = location or "Online - Link será enviado"
            meeting.body = body or f"Reunião com {attendee_name}"
            
            meeting.attendees.add(attendee_email)
            
            meeting.save()
            meeting.send_invite()
            
            logger.info(f"✅ Reunião agendada: {subject} com {attendee_name}")
            logger.info(f"   Data: {start_time.strftime('%d/%m/%Y %H:%M')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar reunião: {str(e)}")
            return False
    
    def send_meeting_invite(
        self,
        email: str,
        name: str,
        proposed_times: List[datetime],
        subject: str,
        message: str = None
    ) -> bool:
        """
        Envia proposta de horários para reunião
        
        Args:
            email: Email do destinatário
            name: Nome do destinatário
            proposed_times: Lista de horários sugeridos
            subject: Assunto
            message: Mensagem personalizada
            
        Returns:
            True se enviado com sucesso
        """
        from src.email_handler import EmailHandler
        
        handler = EmailHandler()
        
        # Formata horários
        times_formatted = "\n".join([
            f"• {t.strftime('%d/%m/%Y às %H:%M')}" 
            for t in proposed_times[:5]
        ])
        
        body = message or f"""
Olá {name},

Gostaria de agendar uma reunião para conversarmos melhor.

Segue algumas opções de horário que tenho disponível:

{times_formatted}

Algum desses horários funciona para você? Se não, fique à vontade para 
sugerir outro horário que seja mais conveniente.

Aguardo seu retorno!

Atenciosamente,
Equipe de Vendas
"""
        
        success = handler.send_email(
            to=email,
            subject=f"Proposta de Reunião: {subject}",
            body=body
        )
        
        if success:
            logger.info(f"📧 Proposta de reunião enviada para {name}")
        
        return success
    
    def confirm_meeting(
        self,
        email: str,
        name: str,
        meeting_time: datetime,
        meeting_link: str = None
    ) -> bool:
        """
        Envia confirmação de reunião agendada
        
        Args:
            email: Email do participante
            name: Nome do participante
            meeting_time: Horário da reunião
            meeting_link: Link da reunião (Zoom, Teams, etc.)
            
        Returns:
            True se enviado com sucesso
        """
        from src.email_handler import EmailHandler
        
        handler = EmailHandler()
        
        link_info = ""
        if meeting_link:
            link_info = f"\nLink da reunião: {meeting_link}"
        
        body = f"""
Olá {name},

Sua reunião foi confirmada! 🎉

📅 Data: {meeting_time.strftime('%d/%m/%Y')}
⏰ Horário: {meeting_time.strftime('%H:%M')}
{link_info}

Por favor, confirme seu recebimento deste e-mail.

Caso precise remarcar, é só me avisar.

Te vejo em breve!

Abraços,
Equipe de Vendas
"""
        
        success = handler.send_email(
            to=email,
            subject=f"Reunião Confirmada - {meeting_time.strftime('%d/%m/%Y')}",
            body=body
        )
        
        if success:
            logger.info(f"✅ Confirmação enviada para {name}")
        
        return success


# Exemplo de uso
if __name__ == "__main__":
    logger.info("Testando MeetingScheduler...")
    
    scheduler = MeetingScheduler()
    
    # Busca horários disponíveis
    available = scheduler.get_available_slots()
    
    logger.info("\n--- Horários Disponíveis ---")
    for slot in available:
        logger.info(f"  {slot['formatted']}")
    
    # Exemplo de proposta de reunião
    if available:
        scheduler.send_meeting_invite(
            email="prospect@empresa.com.br",
            name="João Silva",
            proposed_times=[slot['start'] for slot in available[:3]],
            subject="Demonstração de Solução"
        )
