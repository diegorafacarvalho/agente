"""
Web Dashboard - Interface Visual para SDR Agent
Dashboard elegante e moderno com Flask para gestão de e-mails e aprovações
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
from loguru import logger
import sys
import os

# Adiciona o path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.email_handler import EmailHandler
from src.ai_agent import SDRAgent
from src.follow_up import FollowUpManager
from src.scheduler import MeetingScheduler
from config.settings import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdr-agent-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado global da aplicação
app_state = {
    'emails_pending': [],
    'followups_pending': [],
    'stats': {
        'emails_processed': 0,
        'responses_sent': 0,
        'followups_created': 0,
        'meetings_scheduled': 0
    },
    'processing': False,
    'last_update': None
}

# Inicializa componentes
email_handler = EmailHandler()
ai_agent = SDRAgent()
followup_manager = FollowUpManager()
scheduler = MeetingScheduler()


def background_processor():
    """Processa e-mails em segundo plano"""
    while True:
        if not app_state['processing']:
            try:
                app_state['processing'] = True
                
                # Processa e-mails não lidos
                emails = email_handler.get_unread_emails(limit=20)
                
                new_emails = []
                for email in emails:
                    classification = email_handler.classify_email_intent(email)
                    
                    if classification['needs_response']:
                        analysis = ai_agent.analyze_email(email)
                        
                        if analysis.get('next_action') in ['send_email', 'respond_quickly', 'provide_update']:
                            response_text = ai_agent.generate_response(email, analysis)
                            
                            new_emails.append({
                                'id': email['id'],
                                'subject': email['subject'],
                                'sender_name': email['sender_name'],
                                'sender': email['sender'],
                                'received_at': email.get('received_at', '').strftime('%Y-%m-%d %H:%M') if email.get('received_at') else '',
                                'preview': email['body'][:200] + '...' if len(email['body']) > 200 else email['body'],
                                'classification': classification,
                                'analysis': analysis,
                                'suggested_response': response_text,
                                'status': 'pending'
                            })
                
                app_state['emails_pending'] = new_emails
                app_state['last_update'] = datetime.now().isoformat()
                
                # Notifica via WebSocket
                socketio.emit('update', {
                    'type': 'emails_updated',
                    'count': len(new_emails),
                    'timestamp': app_state['last_update']
                })
                
            except Exception as e:
                logger.error(f"Erro no processamento: {str(e)}")
            finally:
                app_state['processing'] = False
        
        time.sleep(30)  # Atualiza a cada 30 segundos


@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html', stats=app_state['stats'])


@app.route('/api/emails')
def get_emails():
    """API para obter e-mails pendentes"""
    return jsonify({
        'emails': app_state['emails_pending'],
        'count': len(app_state['emails_pending']),
        'last_update': app_state['last_update']
    })


@app.route('/api/approve/<email_id>', methods=['POST'])
def approve_email(email_id):
    """Aprova e envia e-mail"""
    try:
        email_data = next((e for e in app_state['emails_pending'] if e['id'] == email_id), None)
        
        if not email_data:
            return jsonify({'error': 'E-mail não encontrado'}), 404
        
        # Envia e-mail
        success = email_handler.send_reply_by_id(
            email_id=email_id,
            body=email_data['suggested_response']
        )
        
        if success:
            # Remove da lista de pendentes
            app_state['emails_pending'] = [e for e in app_state['emails_pending'] if e['id'] != email_id]
            app_state['stats']['responses_sent'] += 1
            
            socketio.emit('update', {
                'type': 'email_approved',
                'email_id': email_id,
                'stats': app_state['stats']
            })
            
            return jsonify({'success': True, 'message': 'E-mail enviado com sucesso!'})
        else:
            return jsonify({'error': 'Falha ao enviar e-mail'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao aprovar e-mail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reject/<email_id>', methods=['POST'])
def reject_email(email_id):
    """Rejeita e-mail (não envia)"""
    try:
        email_data = next((e for e in app_state['emails_pending'] if e['id'] == email_id), None)
        
        if not email_data:
            return jsonify({'error': 'E-mail não encontrado'}), 404
        
        # Marca como lido sem responder
        email_handler.mark_as_read_by_id(email_id)
        
        # Remove da lista de pendentes
        app_state['emails_pending'] = [e for e in app_state['emails_pending'] if e['id'] != email_id]
        
        socketio.emit('update', {
            'type': 'email_rejected',
            'email_id': email_id,
            'count': len(app_state['emails_pending'])
        })
        
        return jsonify({'success': True, 'message': 'E-mail rejeitado'})
        
    except Exception as e:
        logger.error(f"Erro ao rejeitar e-mail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/edit/<email_id>', methods=['POST'])
def edit_email(email_id):
    """Edita resposta antes de enviar"""
    try:
        data = request.json
        new_response = data.get('response', '')
        
        email_data = next((e for e in app_state['emails_pending'] if e['id'] == email_id), None)
        
        if not email_data:
            return jsonify({'error': 'E-mail não encontrado'}), 404
        
        # Atualiza resposta sugerida
        email_data['suggested_response'] = new_response
        
        return jsonify({
            'success': True,
            'message': 'Resposta atualizada',
            'response': new_response
        })
        
    except Exception as e:
        logger.error(f"Erro ao editar e-mail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/followups')
def get_followups():
    """API para obter follow-ups pendentes"""
    due_followups = followup_manager.get_due_followups()
    
    followups_list = []
    for task in due_followups:
        lead_data = {
            'name': task.lead_name,
            'email': task.lead_email,
            'last_contact': task.last_contact.isoformat() if task.last_contact else '',
            'attempt_number': task.attempt_number
        }
        
        days_since = (datetime.now() - task.last_contact).days if task.last_contact else 0
        followup_message = ai_agent.generate_followup(lead_data, days_since)
        
        followups_list.append({
            'id': task.id,
            'lead_name': task.lead_name,
            'lead_email': task.lead_email,
            'last_contact': task.last_contact.isoformat() if task.last_contact else '',
            'attempt_number': task.attempt_number,
            'priority': task.priority,
            'suggested_message': followup_message,
            'status': 'pending'
        })
    
    return jsonify({
        'followups': followups_list,
        'count': len(followups_list)
    })


@app.route('/api/stats')
def get_stats():
    """API para obter estatísticas"""
    return jsonify({
        'stats': app_state['stats'],
        'pending_emails': len(app_state['emails_pending']),
        'last_update': app_state['last_update']
    })


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Força atualização dos dados"""
    try:
        # Processa e-mails imediatamente
        emails = email_handler.get_unread_emails(limit=20)
        
        new_emails = []
        for email in emails:
            classification = email_handler.classify_email_intent(email)
            
            if classification['needs_response']:
                analysis = ai_agent.analyze_email(email)
                
                if analysis.get('next_action') in ['send_email', 'respond_quickly', 'provide_update']:
                    response_text = ai_agent.generate_response(email, analysis)
                    
                    new_emails.append({
                        'id': email['id'],
                        'subject': email['subject'],
                        'sender_name': email['sender_name'],
                        'sender': email['sender'],
                        'received_at': email.get('received_at', '').strftime('%Y-%m-%d %H:%M') if email.get('received_at') else '',
                        'preview': email['body'][:200] + '...' if len(email['body']) > 200 else email['body'],
                        'classification': classification,
                        'analysis': analysis,
                        'suggested_response': response_text,
                        'status': 'pending'
                    })
        
        app_state['emails_pending'] = new_emails
        app_state['last_update'] = datetime.now().isoformat()
        
        socketio.emit('update', {
            'type': 'refresh_complete',
            'count': len(new_emails),
            'timestamp': app_state['last_update']
        })
        
        return jsonify({
            'success': True,
            'count': len(new_emails)
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Inicia thread de processamento em segundo plano
    processor_thread = threading.Thread(target=background_processor, daemon=True)
    processor_thread.start()
    
    logger.info("🚀 Iniciando Web Dashboard...")
    logger.info("🌐 Acesse: http://localhost:5000")
    
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
