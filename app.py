"""
GeminiCRM Pro - Main Application
AI-Powered CRM built with Google Gemini 3
"""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from config import Config
from models.database import (
    DB, get_all, get_by_id, create, update, delete, search, init_sample_data,
    Contact, Lead, Deal, Task, Activity
)
from models.user_profile import (
    notification_manager, profile_manager, activity_logger,
    init_default_user_profile, NotificationType, NotificationPriority
)
from services import gemini_service

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Initialize database with sample data on first run
try:
    if not DB.get('contacts'):
        init_sample_data()
except Exception as e:
    print(f"Warning: Could not initialize sample data: {e}")

# Initialize default user profile
try:
    if not profile_manager.get_profile('user_1'):
        init_default_user_profile('user_1')
except Exception as e:
    print(f"Warning: Could not initialize user profile: {e}")

# ==================== PAGE ROUTES ====================

@app.route('/')
def index():
    """Dashboard page"""
    return render_template('index.html', page='dashboard')

@app.route('/leads')
def leads_page():
    """Leads management page"""
    return render_template('leads.html', page='leads')

@app.route('/contacts')
def contacts_page():
    """Contacts page"""
    return render_template('contacts.html', page='contacts')

@app.route('/pipeline')
def pipeline_page():
    """Visual pipeline page"""
    return render_template('pipeline.html', page='pipeline')

@app.route('/deals')
def deals_page():
    """Deals page"""
    return render_template('deals.html', page='deals')

@app.route('/tasks')
def tasks_page():
    """Tasks page"""
    return render_template('tasks.html', page='tasks')

@app.route('/analytics')
def analytics_page():
    """Analytics dashboard"""
    return render_template('analytics.html', page='analytics')

@app.route('/profile')
def profile_page():
    """User profile page"""
    return render_template('profile.html', page='profile')


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({"error": "Bad request"}), 400


# ==================== API: CONFIGURATION ====================

@app.route('/api/config/status', methods=['GET'])
def api_config_status():
    """Check API configuration status"""
    configured = gemini_service.is_configured()
    api_key = os.environ.get('GEMINI_API_KEY', '')
    return jsonify({
        "configured": configured,
        "key_preview": f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else None
    })

@app.route('/api/config', methods=['POST'])
def api_config_set():
    """Set API key"""
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        gemini_service.set_api_key(api_key)
        return jsonify({"success": True})
    return jsonify({"error": "No API key provided"}), 400


# ==================== API: DASHBOARD ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    """Get dashboard statistics"""
    leads = get_all('leads')
    deals = get_all('deals')
    tasks = get_all('tasks')
    contacts = get_all('contacts')
    
    # Calculate stats
    total_pipeline = sum(d.get('value', 0) for d in deals)
    weighted_pipeline = sum(d.get('value', 0) * d.get('probability', 0) / 100 for d in deals)
    avg_lead_score = sum(l.get('score', 0) for l in leads) / len(leads) if leads else 0
    
    # Deals by stage
    deals_by_stage = {}
    for d in deals:
        stage = d.get('stage', 'unknown')
        if stage not in deals_by_stage:
            deals_by_stage[stage] = {'count': 0, 'value': 0}
        deals_by_stage[stage]['count'] += 1
        deals_by_stage[stage]['value'] += d.get('value', 0)
    
    # Tasks stats
    pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])
    overdue_tasks = len([t for t in tasks if t.get('is_overdue')])
    
    # Hot leads (score > 70)
    hot_leads = len([l for l in leads if l.get('score', 0) > 70])
    
    return jsonify({
        "total_contacts": len(contacts),
        "total_leads": len(leads),
        "total_deals": len(deals),
        "total_pipeline": total_pipeline,
        "weighted_pipeline": round(weighted_pipeline),
        "avg_lead_score": round(avg_lead_score, 1),
        "hot_leads": hot_leads,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "deals_by_stage": deals_by_stage,
        "pipeline_stages": Config.PIPELINE_STAGES,
    })


# ==================== API: CONTACTS ====================

@app.route('/api/contacts', methods=['GET'])
def api_contacts_list():
    """List all contacts"""
    contacts = get_all('contacts')
    query = request.args.get('q', '')
    if query:
        contacts = search('contacts', query, ['first_name', 'last_name', 'email', 'company'])
    return jsonify({"contacts": contacts})

@app.route('/api/contacts', methods=['POST'])
def api_contacts_create():
    """Create contact"""
    data = request.json
    contact = create('contacts', data, Contact)
    return jsonify({"success": True, "contact": contact})

@app.route('/api/contacts/<contact_id>', methods=['GET'])
def api_contacts_get(contact_id):
    """Get single contact"""
    contact = get_by_id('contacts', contact_id)
    if contact:
        return jsonify({"contact": contact})
    return jsonify({"error": "Contact not found"}), 404

@app.route('/api/contacts/<contact_id>', methods=['PUT'])
def api_contacts_update(contact_id):
    """Update contact"""
    data = request.json
    contact = update('contacts', contact_id, data)
    if contact:
        return jsonify({"success": True, "contact": contact})
    return jsonify({"error": "Contact not found"}), 404

@app.route('/api/contacts/<contact_id>', methods=['DELETE'])
def api_contacts_delete(contact_id):
    """Delete contact"""
    if delete('contacts', contact_id):
        return jsonify({"success": True})
    return jsonify({"error": "Contact not found"}), 404


# ==================== API: LEADS ====================

@app.route('/api/leads', methods=['GET'])
def api_leads_list():
    """List all leads"""
    leads = get_all('leads')
    status = request.args.get('status')
    if status:
        leads = [l for l in leads if l.get('status') == status]
    query = request.args.get('q', '')
    if query:
        leads = search('leads', query, ['name', 'email', 'company'])
    # Sort by score descending
    leads.sort(key=lambda x: x.get('score', 0), reverse=True)
    return jsonify({"leads": leads})

@app.route('/api/leads', methods=['POST'])
def api_leads_create():
    """Create lead"""
    data = request.json
    lead = create('leads', data, Lead)
    return jsonify({"success": True, "lead": lead})

@app.route('/api/leads/<lead_id>', methods=['GET'])
def api_leads_get(lead_id):
    """Get single lead"""
    lead = get_by_id('leads', lead_id)
    if lead:
        return jsonify({"lead": lead})
    return jsonify({"error": "Lead not found"}), 404

@app.route('/api/leads/<lead_id>', methods=['PUT'])
def api_leads_update(lead_id):
    """Update lead"""
    data = request.json
    lead = update('leads', lead_id, data)
    if lead:
        return jsonify({"success": True, "lead": lead})
    return jsonify({"error": "Lead not found"}), 404

@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def api_leads_delete(lead_id):
    """Delete lead"""
    if delete('leads', lead_id):
        return jsonify({"success": True})
    return jsonify({"error": "Lead not found"}), 404


# ==================== API: DEALS ====================

@app.route('/api/deals', methods=['GET'])
def api_deals_list():
    """List all deals"""
    deals = get_all('deals')
    stage = request.args.get('stage')
    if stage:
        deals = [d for d in deals if d.get('stage') == stage]
    # Sort by value descending
    deals.sort(key=lambda x: x.get('value', 0), reverse=True)
    return jsonify({"deals": deals, "stages": Config.PIPELINE_STAGES})

@app.route('/api/deals', methods=['POST'])
def api_deals_create():
    """Create deal"""
    data = request.json
    deal = create('deals', data, Deal)
    return jsonify({"success": True, "deal": deal})

@app.route('/api/deals/<deal_id>', methods=['GET'])
def api_deals_get(deal_id):
    """Get single deal"""
    deal = get_by_id('deals', deal_id)
    if deal:
        return jsonify({"deal": deal})
    return jsonify({"error": "Deal not found"}), 404

@app.route('/api/deals/<deal_id>', methods=['PUT'])
def api_deals_update(deal_id):
    """Update deal"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    deal = update('deals', deal_id, data)
    if deal:
        # Send notification for deal update
        notify_user(
            user_id,
            NotificationType.DEAL_UPDATED.value,
            f"Deal Updated: {deal.get('name', 'Untitled')}",
            f"Deal value: ${deal.get('value', 0):,} - Stage: {deal.get('stage', 'Unknown')}",
            priority=NotificationPriority.NORMAL.value,
            icon='🤝',
            color='primary',
            data={'deal_id': deal_id, 'deal_value': deal.get('value')},
            action_url=f'/deals?id={deal_id}'
        )
        return jsonify({"success": True, "deal": deal})
    return jsonify({"error": "Deal not found"}), 404

@app.route('/api/deals/<deal_id>', methods=['DELETE'])
def api_deals_delete(deal_id):
    """Delete deal"""
    if delete('deals', deal_id):
        return jsonify({"success": True})
    return jsonify({"error": "Deal not found"}), 404

@app.route('/api/deals/<deal_id>/stage', methods=['PUT'])
def api_deals_update_stage(deal_id):
    """Update deal stage (for drag & drop)"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    new_stage = data.get('stage')
    old_stage = data.get('old_stage', 'unknown')
    
    # Update probability based on stage
    probabilities = {
        'lead': 10, 'qualified': 25, 'proposal': 50,
        'negotiation': 75, 'closed_won': 100, 'closed_lost': 0
    }
    
    updates = {'stage': new_stage}
    if new_stage in probabilities:
        updates['probability'] = probabilities[new_stage]
    
    deal = update('deals', deal_id, updates)
    if deal:
        # Send notification for deal stage change
        notify_user(
            user_id,
            NotificationType.DEAL_STAGE_CHANGE.value,
            f"Deal Stage Changed: {deal.get('name', 'Untitled')}",
            f"Moved from {old_stage.replace('_', ' ').title()} to {new_stage.replace('_', ' ').title()}",
            priority=NotificationPriority.HIGH.value,
            icon='📈',
            color='warning',
            data={'deal_id': deal_id, 'old_stage': old_stage, 'new_stage': new_stage},
            action_url=f'/deals?id={deal_id}'
        )
        return jsonify({"success": True, "deal": deal})
    return jsonify({"error": "Deal not found"}), 404


# ==================== API: TASKS ====================

@app.route('/api/tasks', methods=['GET'])
def api_tasks_list():
    """List all tasks"""
    tasks = get_all('tasks')
    status = request.args.get('status')
    if status:
        tasks = [t for t in tasks if t.get('status') == status]
    # Sort by due date
    tasks.sort(key=lambda x: (x.get('due_date') or '9999-99-99', x.get('priority', 'Low')))
    return jsonify({"tasks": tasks})

@app.route('/api/tasks', methods=['POST'])
def api_tasks_create():
    """Create task"""
    data = request.json
    task = create('tasks', data, Task)
    
    # Send notification if task is assigned to someone
    if task and data.get('assigned_to'):
        assigned_to = data.get('assigned_to')
        notify_user(
            assigned_to,
            NotificationType.TASK_ASSIGNED.value,
            f"New Task: {task.get('title', 'Untitled')}",
            f"Task assigned by {data.get('assigned_by', 'Manager')} - Due: {task.get('due_date', 'No date')}",
            priority=NotificationPriority.HIGH.value,
            icon='✓',
            color='info',
            data={'task_id': task.get('id'), 'assigned_by': data.get('assigned_by')},
            action_url=f'/tasks?id={task.get("id")}'
        )
    
    return jsonify({"success": True, "task": task})

@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_tasks_get(task_id):
    """Get single task"""
    task = get_by_id('tasks', task_id)
    if task:
        return jsonify({"task": task})
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def api_tasks_update(task_id):
    """Update task"""
    data = request.json
    task = update('tasks', task_id, data)
    if task:
        return jsonify({"success": True, "task": task})
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def api_tasks_delete(task_id):
    """Delete task"""
    if delete('tasks', task_id):
        return jsonify({"success": True})
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def api_tasks_complete(task_id):
    """Mark task as complete"""
    from datetime import datetime
    task = update('tasks', task_id, {
        'status': 'completed',
        'completed_at': datetime.now().isoformat()
    })
    if task:
        # Notify the task creator or manager
        assigned_by = task.get('assigned_by', 'user_1')
        notify_user(
            assigned_by,
            NotificationType.TASK_ASSIGNED.value,
            f"Task Completed: {task.get('title', 'Untitled')}",
            f"Task completed by {task.get('assigned_to', 'Team member')}",
            priority=NotificationPriority.NORMAL.value,
            icon='✓',
            color='success',
            data={'task_id': task_id},
            action_url=f'/tasks?id={task_id}'
        )
        return jsonify({"success": True, "task": task})
    return jsonify({"error": "Task not found"}), 404


# ==================== API: ACTIVITIES ====================

@app.route('/api/activities', methods=['GET'])
def api_activities_list():
    """List activities"""
    activities = get_all('activities')
    contact_id = request.args.get('contact_id')
    lead_id = request.args.get('lead_id')
    deal_id = request.args.get('deal_id')
    
    if contact_id:
        activities = [a for a in activities if a.get('contact_id') == contact_id]
    if lead_id:
        activities = [a for a in activities if a.get('lead_id') == lead_id]
    if deal_id:
        activities = [a for a in activities if a.get('deal_id') == deal_id]
    
    # Sort by created_at descending
    activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({"activities": activities[:50]})  # Limit to 50

@app.route('/api/activities', methods=['POST'])
def api_activities_create():
    """Create activity"""
    data = request.json
    activity = create('activities', data, Activity)
    return jsonify({"success": True, "activity": activity})


# ==================== API: AI FEATURES ====================

@app.route('/api/ai/score-lead', methods=['POST'])
def api_ai_score_lead():
    """AI Lead Scoring"""
    data = request.json
    lead_id = data.get('lead_id')
    user_id = data.get('user_id', 'user_1')
    
    if lead_id:
        lead = get_by_id('leads', lead_id)
        if not lead:
            return jsonify({"error": "Lead not found"}), 404
    else:
        lead = data.get('lead_data', {})
    
    result = gemini_service.score_lead(lead)
    
    # Update lead with AI score if successful
    if result.get('success') and lead_id:
        analysis = result.get('analysis', {})
        if 'score' in analysis:
            update('leads', lead_id, {
                'ai_score': analysis.get('score'),
                'ai_insights': analysis.get('recommended_actions', [])
            })
            
            # Create notification for lead scoring
            notify_user(
                user_id,
                NotificationType.LEAD_SCORED.value,
                f"Lead {lead.get('name', 'Unknown')} Scored",
                f"Score: {analysis.get('score')}/100 - Grade: {analysis.get('grade')}",
                priority=NotificationPriority.HIGH.value,
                icon='⭐',
                color='warning',
                data={'lead_id': lead_id, 'score': analysis.get('score')},
                action_url=f'/leads?id={lead_id}'
            )
    
    return jsonify(result)

@app.route('/api/ai/generate-email', methods=['POST'])
def api_ai_generate_email():
    """AI Email Generator"""
    data = request.json
    lead_id = data.get('lead_id')
    email_type = data.get('type', 'follow_up')
    tone = data.get('tone', 'professional')
    context = data.get('context', '')
    
    lead = get_by_id('leads', lead_id) if lead_id else {}
    result = gemini_service.generate_email(lead, email_type, tone, context)
    return jsonify(result)

@app.route('/api/ai/analyze-conversation', methods=['POST'])
def api_ai_analyze_conversation():
    """AI Conversation Analyzer"""
    data = request.json
    conversation = data.get('conversation', '')
    lead_id = data.get('lead_id')
    
    lead = get_by_id('leads', lead_id) if lead_id else None
    result = gemini_service.analyze_conversation(conversation, lead)
    return jsonify(result)

@app.route('/api/ai/predict-deal', methods=['POST'])
def api_ai_predict_deal():
    """AI Deal Predictor"""
    data = request.json
    deal_id = data.get('deal_id')
    
    deal = get_by_id('deals', deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
    
    lead = get_by_id('leads', deal.get('lead_id')) if deal.get('lead_id') else None
    result = gemini_service.predict_deal(deal, lead)
    
    # Update deal with AI prediction
    if result.get('success'):
        prediction = result.get('prediction', {})
        update('deals', deal_id, {
            'ai_win_probability': prediction.get('win_probability'),
            'ai_insights': prediction.get('risk_factors', []),
            'ai_next_steps': prediction.get('key_actions_to_win', [])
        })
    
    return jsonify(result)

@app.route('/api/ai/process-notes', methods=['POST'])
def api_ai_process_notes():
    """AI Notes Processor"""
    data = request.json
    notes = data.get('notes', '')
    lead_id = data.get('lead_id')
    
    lead = get_by_id('leads', lead_id) if lead_id else None
    result = gemini_service.process_notes(notes, lead)
    
    # Update lead notes if requested
    if result.get('success') and lead_id:
        processed = result.get('processed', {})
        if processed.get('update_lead_notes'):
            current_lead = get_by_id('leads', lead_id)
            if current_lead:
                from datetime import datetime
                current_notes = current_lead.get('notes', '')
                new_notes = f"{current_notes}\n\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {processed['update_lead_notes']}"
                update('leads', lead_id, {'notes': new_notes.strip()})
    
    return jsonify(result)

@app.route('/api/ai/dashboard-insights', methods=['GET'])
def api_ai_dashboard_insights():
    """AI Dashboard Insights"""
    leads = get_all('leads')
    deals = get_all('deals')
    tasks = get_all('tasks')
    
    result = gemini_service.get_dashboard_insights(leads, deals, tasks)
    return jsonify(result)

@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """AI Chat Assistant"""
    data = request.json
    message = data.get('message', '')
    context = data.get('context')
    
    result = gemini_service.chat_assistant(message, context)
    return jsonify(result)

@app.route('/api/ai/suggest-tasks', methods=['POST'])
def api_ai_suggest_tasks():
    """AI Task Suggestions"""
    data = request.json
    lead_id = data.get('lead_id')
    deal_id = data.get('deal_id')
    
    lead = get_by_id('leads', lead_id) if lead_id else None
    deal = get_by_id('deals', deal_id) if deal_id else None
    
    result = gemini_service.suggest_tasks(lead, deal)
    return jsonify(result)


# ==================== API: SEARCH ====================

@app.route('/api/search', methods=['GET'])
def api_global_search():
    """Global search across all entities"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"results": []})
    
    results = []
    
    # Search contacts
    for contact in search('contacts', query, ['first_name', 'last_name', 'email', 'company']):
        results.append({
            'type': 'contact',
            'id': contact['id'],
            'title': contact['full_name'],
            'subtitle': contact.get('company', ''),
            'icon': 'person'
        })
    
    # Search leads
    for lead in search('leads', query, ['name', 'email', 'company']):
        results.append({
            'type': 'lead',
            'id': lead['id'],
            'title': lead['name'],
            'subtitle': lead.get('company', ''),
            'icon': 'trending_up'
        })
    
    # Search deals
    for deal in search('deals', query, ['name', 'company']):
        results.append({
            'type': 'deal',
            'id': deal['id'],
            'title': deal['name'],
            'subtitle': f"${deal.get('value', 0):,}",
            'icon': 'handshake'
        })
    
    return jsonify({"results": results[:20]})


# ==================== API: USER PROFILE ====================

@app.route('/api/profile', methods=['GET'])
def api_get_profile():
    """Get current user profile"""
    user_id = request.args.get('user_id', 'user_1')
    profile = profile_manager.get_profile(user_id)
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify(profile.to_dict())


@app.route('/api/profile', methods=['PUT'])
def api_update_profile():
    """Update user profile"""
    user_id = request.json.get('user_id', 'user_1')
    updates = {k: v for k, v in request.json.items() if k != 'user_id'}
    
    profile = profile_manager.update_profile(user_id, updates)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    # Log activity
    activity_logger.log_activity(user_id, {
        'action': 'update',
        'resource_type': 'profile',
        'resource_id': user_id,
        'description': f"Updated profile",
    })
    
    return jsonify(profile.to_dict())


@app.route('/api/profile/settings', methods=['GET'])
def api_get_settings():
    """Get user settings and preferences"""
    user_id = request.args.get('user_id', 'user_1')
    profile = profile_manager.get_profile(user_id)
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify({
        "language": profile.language,
        "timezone": profile.timezone,
        "date_format": profile.date_format,
        "time_format": profile.time_format,
        "currency": profile.currency,
        "theme": profile.theme,
        "notification_preferences": profile.notification_preferences,
    })


@app.route('/api/profile/settings', methods=['PUT'])
def api_update_settings():
    """Update user settings"""
    user_id = request.json.get('user_id', 'user_1')
    settings = {k: v for k, v in request.json.items() if k != 'user_id'}
    
    profile = profile_manager.update_profile(user_id, settings)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify({"success": True})


@app.route('/api/profile/status', methods=['POST'])
def api_set_status():
    """Set user status (active, away, busy, offline)"""
    user_id = request.json.get('user_id', 'user_1')
    status = request.json.get('status', 'active')
    
    profile = profile_manager.set_status(user_id, status)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify({"status": profile.status})


@app.route('/api/profile/<user_id>/team', methods=['GET'])
def api_get_team(user_id):
    """Get team members and stats"""
    profile = profile_manager.get_profile(user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    team_id = profile.team_id
    members = profile_manager.get_team_members(team_id)
    stats = profile_manager.get_team_statistics(team_id)
    
    return jsonify({
        "team_id": team_id,
        "members": [m.to_dict() for m in members],
        "statistics": stats,
    })


# ==================== API: NOTIFICATIONS ====================

@app.route('/api/notifications', methods=['GET'])
def api_get_notifications():
    """Get user notifications"""
    user_id = request.args.get('user_id', 'user_1')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 20))
    
    notifications = notification_manager.get_notifications(user_id, unread_only, limit)
    
    return jsonify({
        "notifications": [n.to_dict() for n in notifications],
        "unread_count": notification_manager.get_unread_count(user_id),
    })


@app.route('/api/notifications/unread-count', methods=['GET'])
def api_unread_count():
    """Get count of unread notifications"""
    user_id = request.args.get('user_id', 'user_1')
    count = notification_manager.get_unread_count(user_id)
    
    return jsonify({"unread_count": count})


@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
def api_mark_read(notification_id):
    """Mark notification as read"""
    success = notification_manager.mark_notification_read(notification_id)
    
    if not success:
        return jsonify({"error": "Notification not found"}), 404
    
    return jsonify({"success": True})


@app.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_read():
    """Mark all notifications as read"""
    user_id = request.json.get('user_id', 'user_1')
    notification_manager.mark_all_read(user_id)
    
    return jsonify({"success": True})


@app.route('/api/notifications/<notification_id>', methods=['DELETE'])
def api_delete_notification(notification_id):
    """Delete a notification"""
    notification_manager.delete_notification(notification_id)
    return jsonify({"success": True})


@app.route('/api/notifications/<notification_id>/pin', methods=['POST'])
def api_pin_notification(notification_id):
    """Pin a notification"""
    action = request.json.get('action', 'pin')
    
    if action == 'pin':
        success = notification_manager.pin_notification(notification_id)
    else:
        success = notification_manager.unpin_notification(notification_id)
    
    if not success:
        return jsonify({"error": "Notification not found"}), 404
    
    return jsonify({"success": True})


@app.route('/api/notifications/preferences', methods=['GET'])
def api_get_notification_prefs():
    """Get notification preferences"""
    user_id = request.args.get('user_id', 'user_1')
    profile = profile_manager.get_profile(user_id)
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify(profile.notification_preferences)


@app.route('/api/notifications/preferences', methods=['PUT'])
def api_update_notification_prefs():
    """Update notification preferences"""
    user_id = request.json.get('user_id', 'user_1')
    preferences = {k: v for k, v in request.json.items() if k != 'user_id'}
    
    profile = profile_manager.update_notification_preferences(user_id, preferences)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify(profile.notification_preferences)


# ==================== API: ACTIVITY LOG ====================

@app.route('/api/activity/user/<user_id>', methods=['GET'])
def api_get_user_activity(user_id):
    """Get user activity log"""
    limit = int(request.args.get('limit', 50))
    logs = activity_logger.get_user_activity(user_id, limit)
    
    return jsonify({
        "activities": [l.to_dict() for l in logs],
        "total": len(logs),
    })


@app.route('/api/activity/resource/<resource_type>/<resource_id>', methods=['GET'])
def api_get_resource_activity(resource_type, resource_id):
    """Get activity for a specific resource"""
    activities = activity_logger.get_activity_for_resource(resource_type, resource_id)
    
    return jsonify({
        "activities": [a.to_dict() for a in activities],
        "total": len(activities),
    })


# ==================== HELPER: CREATE NOTIFICATIONS ====================

def notify_user(user_id, notification_type, title, message, **kwargs):
    """Helper to create and send notification"""
    notification_manager.create_notification(user_id, {
        'type': notification_type,
        'title': title,
        'message': message,
        'priority': kwargs.get('priority', NotificationPriority.NORMAL.value),
        'icon': kwargs.get('icon', 'info'),
        'color': kwargs.get('color', 'blue'),
        'data': kwargs.get('data', {}),
        'action_url': kwargs.get('action_url', ''),
    })


# ==================== API: SYNTHETIC NOTIFICATIONS (For Testing) ====================

@app.route('/api/notifications/test', methods=['POST'])
def api_test_notification():
    """Create test notification (for demo/testing)"""
    user_id = request.json.get('user_id', 'user_1')
    
    # Create sample notification
    notify_user(
        user_id,
        NotificationType.DEAL_UPDATED.value,
        "Deal Updated",
        "Acme Corp deal has been moved to Negotiation stage",
        icon='trending_up',
        color='green',
        data={'deal_id': 'deal_123'},
        action_url='/deals/deal_123'
    )
    
    return jsonify({"success": True, "message": "Test notification created"})




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
