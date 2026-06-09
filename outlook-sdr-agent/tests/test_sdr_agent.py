"""
Testes unitários do SDR Agent

Execute com: pytest tests/ -v
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


class TestEmailClassification:
    """Testes para classificação de e-mails"""
    
    def test_classify_interest_keywords(self):
        """Testa detecção de palavras-chave de interesse"""
        from src.email_handler import EmailHandler
        
        # Mock para evitar conexão real
        with patch('src.email_handler.EmailHandler._connect'):
            handler = EmailHandler()
        
        email_data = {
            'subject': 'Interesse em solução',
            'body': 'Gostaria de mais informações sobre preços e agendar uma demonstração',
            'sender': 'test@example.com'
        }
        
        classification = handler.classify_email_intent(email_data)
        
        assert classification['intent'] == 'interest'
        assert classification['lead_temperature'] == 'warm'
        assert classification['suggested_action'] == 'respond_quickly'
    
    def test_classify_not_interested(self):
        """Testa detecção de desinteresse"""
        from src.email_handler import EmailHandler
        
        with patch('src.email_handler.EmailHandler._connect'):
            handler = EmailHandler()
        
        email_data = {
            'subject': 'Re: Proposta',
            'body': 'Obrigado, mas não estamos interessados no momento.',
            'sender': 'test@example.com'
        }
        
        classification = handler.classify_email_intent(email_data)
        
        assert classification['intent'] == 'not_interested'
        assert classification['needs_response'] == False
    
    def test_classify_scheduling(self):
        """Testa detecção de solicitação de agendamento"""
        from src.email_handler import EmailHandler
        
        with patch('src.email_handler.EmailHandler._connect'):
            handler = EmailHandler()
        
        email_data = {
            'subject': 'Agendar reunião',
            'body': 'Podemos marcar um horário para conversar? Qual seu horário disponível?',
            'sender': 'test@example.com'
        }
        
        classification = handler.classify_email_intent(email_data)
        
        assert classification['intent'] == 'scheduling'
        assert classification['suggested_action'] == 'schedule_meeting'


class TestFollowUpManager:
    """Testes para gerenciamento de follow-up"""
    
    def test_create_followup(self):
        """Testa criação de task de follow-up"""
        from src.follow_up import FollowUpManager
        
        manager = FollowUpManager()
        
        task = manager.create_followup(
            lead_id="test_001",
            lead_name="João Silva",
            lead_email="joao@test.com",
            priority="high"
        )
        
        assert task.lead_id == "test_001"
        assert task.lead_name == "João Silva"
        assert task.attempt_number == 1
        assert task.status == "pending"
        assert task.priority == "high"
    
    def test_schedule_next_followup(self):
        """Testa agendamento de próximo follow-up"""
        from src.follow_up import FollowUpManager, FollowUpTask
        
        manager = FollowUpManager()
        
        # Cria task inicial
        task = FollowUpTask(
            lead_id="test_001",
            lead_name="João Silva",
            lead_email="joao@test.com",
            last_contact=datetime.now(),
            next_contact=datetime.now(),
            attempt_number=1,
            priority="medium",
            status="pending"
        )
        
        # Agenda próximo
        new_task = manager.schedule_next_followup(task)
        
        assert new_task is not None
        assert new_task.attempt_number == 2
        assert new_task.lead_id == task.lead_id
    
    def test_max_attempts_reached(self):
        """Testa limite máximo de tentativas"""
        from src.follow_up import FollowUpManager, FollowUpTask
        
        manager = FollowUpManager()
        manager.max_attempts = 3
        
        # Cria task na tentativa 3
        task = FollowUpTask(
            lead_id="test_001",
            lead_name="João Silva",
            lead_email="joao@test.com",
            last_contact=datetime.now(),
            next_contact=datetime.now(),
            attempt_number=3,
            priority="medium",
            status="pending"
        )
        
        # Tenta agendar próximo (deve retornar None)
        new_task = manager.schedule_next_followup(task)
        
        assert new_task is None
        assert task.status == "completed"
    
    def test_get_stats(self):
        """Testa estatísticas de follow-up"""
        from src.follow_up import FollowUpManager
        
        manager = FollowUpManager()
        
        # Cria algumas tasks
        manager.create_followup("1", "Lead 1", "l1@test.com", priority="high")
        manager.create_followup("2", "Lead 2", "l2@test.com", priority="medium")
        manager.create_followup("3", "Lead 3", "l3@test.com", priority="low")
        
        stats = manager.get_stats()
        
        assert stats['total'] == 3
        assert stats['pending'] == 3
        assert stats['by_priority']['high'] == 1
        assert stats['by_priority']['medium'] == 1
        assert stats['by_priority']['low'] == 1


class TestSDRAgent:
    """Testes para agente de IA"""
    
    def test_fallback_analysis_hot_lead(self):
        """Testa análise fallback para lead quente"""
        from src.ai_agent import SDRAgent
        
        agent = SDRAgent()
        
        email_data = {
            'subject': 'URGENTE: Preciso de solução agora',
            'body': 'Estou muito interessado, quero agendar reunião urgente',
            'sender': 'hot@test.com'
        }
        
        analysis = agent._fallback_analysis(email_data)
        
        assert analysis['lead_score'] == 75
        assert analysis['lead_temperature'] == 'hot'
    
    def test_fallback_analysis_cold_lead(self):
        """Testa análise fallback para lead frio"""
        from src.ai_agent import SDRAgent
        
        agent = SDRAgent()
        
        email_data = {
            'subject': 'Re: Proposta',
            'body': 'Não estou interessado agora, obrigado.',
            'sender': 'cold@test.com'
        }
        
        analysis = agent._fallback_analysis(email_data)
        
        assert analysis['lead_score'] == 25
        assert analysis['lead_temperature'] == 'cold'
    
    def test_fallback_response_generation(self):
        """Testa geração de resposta fallback"""
        from src.ai_agent import SDRAgent
        
        agent = SDRAgent()
        
        email_data = {
            'sender_name': 'Maria Santos',
            'subject': 'Contato',
            'body': 'Olá'
        }
        
        analysis = {'next_action': 'send_email'}
        
        response = agent._fallback_response(email_data, analysis)
        
        assert 'Maria Santos' in response
        assert 'Obrigado' in response
        assert len(response) > 50


class TestMeetingScheduler:
    """Testes para agendador de reuniões"""
    
    def test_fallback_available_slots(self):
        """Testa geração de horários disponíveis (fallback)"""
        from src.scheduler import MeetingScheduler
        
        # Mock para evitar conexão real
        with patch('src.scheduler.MeetingScheduler._connect'):
            scheduler = MeetingScheduler()
        
        start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        slots = scheduler._fallback_available_slots(start, end, 30)
        
        assert len(slots) > 0
        assert all('start' in slot for slot in slots)
        assert all('formatted' in slot for slot in slots)
    
    def test_find_free_slots_no_conflicts(self):
        """Testa busca de slots sem conflitos"""
        from src.scheduler import MeetingScheduler
        
        with patch('src.scheduler.MeetingScheduler._connect'):
            scheduler = MeetingScheduler()
        
        start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=2)
        
        # Sem eventos ocupados
        free_slots = scheduler._find_free_slots([], start, end, 30)
        
        assert len(free_slots) > 0


# Teste de integração mockado
class TestIntegration:
    """Testes de integração mockados"""
    
    @patch('src.email_handler.EmailHandler')
    @patch('src.ai_agent.SDRAgent')
    @patch('src.follow_up.FollowUpManager')
    @patch('src.scheduler.MeetingScheduler')
    def test_system_initialization(self, mock_scheduler, mock_followup, mock_agent, mock_handler):
        """Testa inicialização do sistema"""
        from src.main import SDRAgentSystem
        
        # Configura mocks
        mock_handler.return_value = Mock()
        mock_agent.return_value = Mock()
        mock_followup.return_value = Mock()
        mock_scheduler.return_value = Mock()
        
        system = SDRAgentSystem()
        
        assert system.email_handler is not None
        assert system.ai_agent is not None
        assert system.followup_manager is not None
        assert system.scheduler is not None
        assert system.stats['emails_processed'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
