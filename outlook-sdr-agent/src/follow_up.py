"""
Sistema de Follow-up Automático

Responsável por:
- Gerenciar fila de follow-ups
- Calcular timing ideal de contato
- Executar follow-ups agendados
- Acompanhar métricas de engajamento
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass, asdict
import json

from config.settings import settings


@dataclass
class FollowUpTask:
    """Task de follow-up"""
    lead_id: str
    lead_name: str
    lead_email: str
    last_contact: datetime
    next_contact: datetime
    attempt_number: int
    priority: str  # low, medium, high
    status: str  # pending, completed, skipped
    notes: str = ""


class FollowUpManager:
    def __init__(self):
        self.tasks: List[FollowUpTask] = []
        self.max_attempts = settings.FOLLOWUP_MAX_ATTEMPTS
        logger.info("✅ FollowUpManager inicializado")
    
    def create_followup(
        self,
        lead_id: str,
        lead_name: str,
        lead_email: str,
        initial_delay_hours: int = None,
        priority: str = "medium"
    ) -> FollowUpTask:
        """
        Cria uma nova task de follow-up
        
        Args:
            lead_id: ID único do lead
            lead_name: Nome do lead
            lead_email: Email do lead
            initial_delay_hours: Horas até o primeiro follow-up
            priority: Prioridade (low, medium, high)
            
        Returns:
            Task criada
        """
        hours = initial_delay_hours or settings.FOLLOWUP_INITIAL_HOURS
        next_contact = datetime.now() + timedelta(hours=hours)
        
        task = FollowUpTask(
            lead_id=lead_id,
            lead_name=lead_name,
            lead_email=lead_email,
            last_contact=datetime.now(),
            next_contact=next_contact,
            attempt_number=1,
            priority=priority,
            status="pending",
            notes=f"Follow-up inicial agendado para {next_contact}"
        )
        
        self.tasks.append(task)
        logger.info(f"📅 Follow-up criado para {lead_name} em {next_contact}")
        
        return task
    
    def schedule_next_followup(self, task: FollowUpTask, days: int = None) -> Optional[FollowUpTask]:
        """
        Agenda próximo follow-up baseado no número de tentativas
        
        Args:
            task: Task atual
            days: Dias para próximo contato (opcional)
            
        Returns:
            Nova task ou None se atingiu máximo
        """
        if task.attempt_number >= self.max_attempts:
            logger.warning(f"⚠️  Máximo de follow-ups atingido para {task.lead_name}")
            task.status = "completed"
            return None
        
        # Calcula próximo intervalo baseado na tentativa
        if days is None:
            if task.attempt_number == 1:
                days = 3
            elif task.attempt_number == 2:
                days = 7
            else:
                days = 14
        
        next_contact = datetime.now() + timedelta(days=days)
        
        new_task = FollowUpTask(
            lead_id=task.lead_id,
            lead_name=task.lead_name,
            lead_email=task.lead_email,
            last_contact=datetime.now(),
            next_contact=next_contact,
            attempt_number=task.attempt_number + 1,
            priority=task.priority,
            status="pending",
            notes=f"Follow-up #{task.attempt_number + 1} agendado para {next_contact}"
        )
        
        self.tasks.append(new_task)
        logger.info(f"📅 Próximo follow-up para {task.lead_name}: {next_contact}")
        
        return new_task
    
    def get_due_followups(self) -> List[FollowUpTask]:
        """
        Retorna follow-ups que devem ser executados agora
        
        Returns:
            Lista de tasks vencidas
        """
        now = datetime.now()
        due_tasks = [
            task for task in self.tasks
            if task.status == "pending" and task.next_contact <= now
        ]
        
        # Ordena por prioridade e data
        priority_order = {"high": 0, "medium": 1, "low": 2}
        due_tasks.sort(key=lambda t: (priority_order.get(t.priority, 1), t.next_contact))
        
        logger.info(f"📋 {len(due_tasks)} follow-ups vencidos")
        
        return due_tasks
    
    def mark_completed(self, task: FollowUpTask, notes: str = ""):
        """Marca task como completada"""
        task.status = "completed"
        if notes:
            task.notes += f"\n{notes}"
        logger.info(f"✅ Follow-up completado para {task.lead_name}")
    
    def mark_skipped(self, task: FollowUpTask, reason: str):
        """Marca task como pulada"""
        task.status = "skipped"
        task.notes += f"\nPulado: {reason}"
        logger.info(f"⏭️  Follow-up pulado para {task.lead_name}: {reason}")
    
    def get_lead_history(self, lead_id: str) -> List[FollowUpTask]:
        """
        Retorna histórico de follow-ups de um lead
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lista de tasks do lead
        """
        return [task for task in self.tasks if task.lead_id == lead_id]
    
    def calculate_optimal_timing(self, engagement_data: Dict) -> int:
        """
        Calcula timing ideal para follow-up baseado em engajamento
        
        Args:
            engagement_data: Dados de engajamento (opens, clicks, replies)
            
        Returns:
            Horas até próximo contato
        """
        base_hours = 24
        
        # Ajusta baseado em engajamento
        if engagement_data.get('replied', False):
            base_hours = 4  # Respondeu rápido
        elif engagement_data.get('clicked', False):
            base_hours = 12  # Clicou mas não respondeu
        elif engagement_data.get('opened', False):
            base_hours = 24  # Apenas abriu
        else:
            base_hours = 48  # Não engajou
        
        # Ajusta baseado em horário do dia
        current_hour = datetime.now().hour
        if current_hour < 9 or current_hour > 18:
            base_hours += 12  # Espera horário comercial
        
        # Ajusta baseado em dia da semana
        if datetime.now().weekday() >= 4:  # Sexta ou fim de semana
            base_hours += 48  # Espera segunda-feira
        
        logger.info(f"⏰ Timing ótimo calculado: {base_hours} horas")
        
        return base_hours
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de follow-up"""
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == "pending"])
        completed = len([t for t in self.tasks if t.status == "completed"])
        skipped = len([t for t in self.tasks if t.status == "skipped"])
        
        by_priority = {
            'high': len([t for t in self.tasks if t.priority == "high"]),
            'medium': len([t for t in self.tasks if t.priority == "medium"]),
            'low': len([t for t in self.tasks if t.priority == "low"])
        }
        
        return {
            'total': total,
            'pending': pending,
            'completed': completed,
            'skipped': skipped,
            'by_priority': by_priority,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }


# Exemplo de uso
if __name__ == "__main__":
    logger.info("Testando FollowUpManager...")
    
    manager = FollowUpManager()
    
    # Cria alguns follow-ups de exemplo
    task1 = manager.create_followup(
        lead_id="lead_001",
        lead_name="João Silva",
        lead_email="joao@empresa.com.br",
        priority="high"
    )
    
    task2 = manager.create_followup(
        lead_id="lead_002",
        lead_name="Maria Santos",
        lead_email="maria@empresa.com.br",
        initial_delay_hours=48,
        priority="medium"
    )
    
    # Simula tempo passando
    logger.info("\n--- Status atual ---")
    stats = manager.get_stats()
    logger.info(f"Estatísticas: {json.dumps(stats, indent=2)}")
    
    # Verifica follow-ups vencidos
    due = manager.get_due_followups()
    logger.info(f"\nFollow-ups vencidos: {len(due)}")
    
    for task in due:
        logger.info(f"  - {task.lead_name} (Tentativa {task.attempt_number})")
        # Agenda próximo
        manager.schedule_next_followup(task)
