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
from models.salesforce_features import (
    task_manager, event_manager, report_engine, approval_process,
    workflow_automation, forecast_management, document_management,
    custom_object_support, chatter_collaboration, formula_engine
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


# ==================== SALESFORCE FEATURES ====================

# ==================== API: TASK MANAGEMENT ====================

@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    """Create a new task"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    task = task_manager.create_task(
        user_id=user_id,
        subject=data.get('subject'),
        description=data.get('description', ''),
        priority=data.get('priority', 'Normal'),
        status=data.get('status', 'Not Started'),
        due_date=data.get('due_date'),
        assigned_to=data.get('assigned_to', user_id),
        related_to_type=data.get('related_to_type'),
        related_to_id=data.get('related_to_id'),
    )
    
    notify_user(
        user_id,
        NotificationType.TASK_CREATED.value,
        "Task Created",
        f"New task: {data.get('subject')}",
        icon='task_alt',
        color='blue'
    )
    
    return jsonify(task), 201


@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """Get all tasks for user"""
    user_id = request.args.get('user_id', 'user_1')
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    tasks = task_manager.get_user_tasks(user_id)
    
    if status:
        tasks = [t for t in tasks if t.get('status') == status]
    if priority:
        tasks = [t for t in tasks if t.get('priority') == priority]
    
    return jsonify({"tasks": tasks, "total": len(tasks)})


@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_get_task(task_id):
    """Get specific task"""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """Update task"""
    data = request.json
    task = task_manager.update_task(task_id, data)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route('/api/tasks/<task_id>/complete', methods=['PUT'])
def api_complete_task(task_id):
    """Mark task as complete"""
    task = task_manager.update_task(task_id, {'status': 'Completed'})
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    user_id = task.get('user_id', 'user_1')
    notify_user(
        user_id,
        NotificationType.TASK_COMPLETED.value,
        "Task Completed",
        f"Task '{task.get('subject')}' marked as complete",
        icon='check_circle',
        color='green'
    )
    
    return jsonify(task)


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete task"""
    if task_manager.delete_task(task_id):
        return jsonify({"success": True}), 204
    return jsonify({"error": "Task not found"}), 404


@app.route('/api/task-queues', methods=['POST'])
def api_create_task_queue():
    """Create task queue"""
    data = request.json
    queue = task_manager.create_task_queue(
        name=data.get('name'),
        description=data.get('description', ''),
        owner_id=data.get('owner_id', 'user_1')
    )
    return jsonify(queue), 201


@app.route('/api/task-queues', methods=['GET'])
def api_get_task_queues():
    """Get all task queues"""
    queues = task_manager.get_all_task_queues()
    return jsonify({"queues": queues, "total": len(queues)})


# ==================== API: EVENT MANAGEMENT ====================

@app.route('/api/events', methods=['POST'])
def api_create_event():
    """Create event/meeting"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    event = event_manager.create_event(
        user_id=user_id,
        title=data.get('title'),
        description=data.get('description', ''),
        event_type=data.get('event_type', 'Meeting'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        location=data.get('location', ''),
        attendees=data.get('attendees', []),
        related_to_type=data.get('related_to_type'),
        related_to_id=data.get('related_to_id'),
    )
    
    notify_user(
        user_id,
        NotificationType.EVENT_CREATED.value,
        "Event Created",
        f"New event: {data.get('title')}",
        icon='event',
        color='purple'
    )
    
    return jsonify(event), 201


@app.route('/api/events', methods=['GET'])
def api_get_events():
    """Get events"""
    user_id = request.args.get('user_id', 'user_1')
    event_type = request.args.get('type')
    
    events = event_manager.get_user_events(user_id)
    
    if event_type:
        events = [e for e in events if e.get('event_type') == event_type]
    
    return jsonify({"events": events, "total": len(events)})


@app.route('/api/events/<event_id>', methods=['GET'])
def api_get_event(event_id):
    """Get specific event"""
    event = event_manager.get_event(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event)


@app.route('/api/events/<event_id>', methods=['PUT'])
def api_update_event(event_id):
    """Update event"""
    data = request.json
    event = event_manager.update_event(event_id, data)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event)


@app.route('/api/events/<event_id>', methods=['DELETE'])
def api_delete_event(event_id):
    """Delete event"""
    if event_manager.delete_event(event_id):
        return jsonify({"success": True}), 204
    return jsonify({"error": "Event not found"}), 404


# ==================== API: REPORTS & DASHBOARDS ====================

@app.route('/api/reports', methods=['POST'])
def api_create_report():
    """Create report"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    report = report_engine.create_report(
        user_id=user_id,
        name=data.get('name'),
        report_type=data.get('report_type', 'Tabular'),
        source_object=data.get('source_object'),
        columns=data.get('columns', []),
        filters=data.get('filters', []),
        grouping=data.get('grouping', []),
        is_public=data.get('is_public', False),
    )
    
    notify_user(
        user_id,
        NotificationType.REPORT_CREATED.value,
        "Report Created",
        f"New report: {data.get('name')}",
        icon='assessment',
        color='blue'
    )
    
    return jsonify(report), 201


@app.route('/api/reports', methods=['GET'])
def api_get_reports():
    """Get all reports"""
    user_id = request.args.get('user_id', 'user_1')
    reports = report_engine.get_user_reports(user_id)
    return jsonify({"reports": reports, "total": len(reports)})


@app.route('/api/reports/<report_id>/execute', methods=['POST'])
def api_execute_report(report_id):
    """Execute report and get results"""
    report = report_engine.get_report(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    
    # Simulate report execution
    results = {
        "report_id": report_id,
        "name": report.get('name'),
        "executed_at": report.get('created_at'),
        "data": [],
        "summary": {"total_records": 0}
    }
    
    return jsonify(results)


@app.route('/api/dashboards', methods=['POST'])
def api_create_dashboard():
    """Create dashboard"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    dashboard = report_engine.create_dashboard(
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description', ''),
        widgets=data.get('widgets', []),
        is_public=data.get('is_public', False),
    )
    
    return jsonify(dashboard), 201


@app.route('/api/dashboards', methods=['GET'])
def api_get_dashboards():
    """Get all dashboards"""
    user_id = request.args.get('user_id', 'user_1')
    dashboards = report_engine.get_user_dashboards(user_id)
    return jsonify({"dashboards": dashboards, "total": len(dashboards)})


# ==================== API: APPROVALS ====================

@app.route('/api/approvals', methods=['POST'])
def api_submit_approval():
    """Submit record for approval"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    approval = approval_process.submit_for_approval(
        submitter_id=user_id,
        record_type=data.get('record_type'),
        record_id=data.get('record_id'),
        process_id=data.get('process_id'),
        comments=data.get('comments', ''),
    )
    
    notify_user(
        user_id,
        NotificationType.APPROVAL_SUBMITTED.value,
        "Approval Submitted",
        f"Record submitted for approval",
        icon='check',
        color='blue'
    )
    
    return jsonify(approval), 201


@app.route('/api/approvals', methods=['GET'])
def api_get_approvals():
    """Get pending approvals"""
    user_id = request.args.get('user_id', 'user_1')
    approvals = approval_process.get_pending_approvals(user_id)
    return jsonify({"approvals": approvals, "total": len(approvals)})


@app.route('/api/approvals/<approval_id>/approve', methods=['POST'])
def api_approve_record(approval_id):
    """Approve a record"""
    data = request.json
    approver_id = data.get('approver_id', 'user_1')
    comments = data.get('comments', '')
    
    approval = approval_process.approve_record(approval_id, approver_id, comments)
    if not approval:
        return jsonify({"error": "Approval not found"}), 404
    
    notify_user(
        approver_id,
        NotificationType.APPROVAL_APPROVED.value,
        "Record Approved",
        "You approved a record",
        icon='verified',
        color='green'
    )
    
    return jsonify(approval)


@app.route('/api/approvals/<approval_id>/reject', methods=['POST'])
def api_reject_record(approval_id):
    """Reject a record"""
    data = request.json
    approver_id = data.get('approver_id', 'user_1')
    comments = data.get('comments', '')
    
    approval = approval_process.reject_record(approval_id, approver_id, comments)
    if not approval:
        return jsonify({"error": "Approval not found"}), 404
    
    notify_user(
        approver_id,
        NotificationType.APPROVAL_REJECTED.value,
        "Record Rejected",
        "You rejected a record",
        icon='clear',
        color='red'
    )
    
    return jsonify(approval)


# ==================== API: WORKFLOWS ====================

@app.route('/api/workflows', methods=['POST'])
def api_create_workflow():
    """Create workflow automation"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    workflow = workflow_automation.create_workflow(
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description', ''),
        object_type=data.get('object_type'),
        trigger=data.get('trigger'),
        criteria=data.get('criteria', []),
        actions=data.get('actions', []),
    )
    
    return jsonify(workflow), 201


@app.route('/api/workflows', methods=['GET'])
def api_get_workflows():
    """Get all workflows"""
    user_id = request.args.get('user_id', 'user_1')
    workflows = workflow_automation.get_user_workflows(user_id)
    return jsonify({"workflows": workflows, "total": len(workflows)})


@app.route('/api/workflows/<workflow_id>/activate', methods=['PUT'])
def api_activate_workflow(workflow_id):
    """Activate workflow"""
    workflow = workflow_automation.activate_workflow(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify(workflow)


@app.route('/api/workflows/<workflow_id>/deactivate', methods=['PUT'])
def api_deactivate_workflow(workflow_id):
    """Deactivate workflow"""
    workflow = workflow_automation.deactivate_workflow(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify(workflow)


# ==================== API: FORECASTING ====================

@app.route('/api/forecasts', methods=['POST'])
def api_generate_forecast():
    """Generate sales forecast"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    forecast = forecast_management.generate_forecast(
        user_id=user_id,
        period=data.get('period'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        include_scenarios=data.get('include_scenarios', False),
    )
    
    return jsonify(forecast), 201


@app.route('/api/forecasts', methods=['GET'])
def api_get_forecasts():
    """Get forecasts"""
    user_id = request.args.get('user_id', 'user_1')
    forecasts = forecast_management.get_user_forecasts(user_id)
    return jsonify({"forecasts": forecasts, "total": len(forecasts)})


# ==================== API: DOCUMENTS ====================

@app.route('/api/documents', methods=['POST'])
def api_upload_document():
    """Upload document"""
    user_id = request.form.get('user_id', 'user_1')
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    document = document_management.upload_document(
        user_id=user_id,
        filename=file.filename,
        file_size=len(file.read()),
        file_type=file.content_type or 'application/octet-stream',
        related_to_type=request.form.get('related_to_type'),
        related_to_id=request.form.get('related_to_id'),
        description=request.form.get('description', ''),
    )
    
    return jsonify(document), 201


@app.route('/api/documents', methods=['GET'])
def api_get_documents():
    """Get documents"""
    user_id = request.args.get('user_id', 'user_1')
    related_to_type = request.args.get('related_to_type')
    related_to_id = request.args.get('related_to_id')
    
    documents = document_management.get_user_documents(user_id)
    
    if related_to_type and related_to_id:
        documents = [d for d in documents if d.get('related_to_type') == related_to_type and d.get('related_to_id') == related_to_id]
    
    return jsonify({"documents": documents, "total": len(documents)})


# ==================== API: CUSTOM OBJECTS ====================

@app.route('/api/custom-objects', methods=['POST'])
def api_create_custom_object():
    """Create custom object"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    custom_obj = custom_object_support.create_custom_object(
        user_id=user_id,
        name=data.get('name'),
        label=data.get('label'),
        description=data.get('description', ''),
    )
    
    return jsonify(custom_obj), 201


@app.route('/api/custom-objects', methods=['GET'])
def api_get_custom_objects():
    """Get custom objects"""
    user_id = request.args.get('user_id', 'user_1')
    custom_objs = custom_object_support.get_user_custom_objects(user_id)
    return jsonify({"custom_objects": custom_objs, "total": len(custom_objs)})


@app.route('/api/custom-objects/<object_id>/fields', methods=['POST'])
def api_add_custom_field(object_id):
    """Add custom field to object"""
    data = request.json
    
    field = custom_object_support.add_custom_field(
        object_id=object_id,
        field_name=data.get('field_name'),
        field_type=data.get('field_type', 'Text'),
        label=data.get('label'),
        required=data.get('required', False),
        unique=data.get('unique', False),
        help_text=data.get('help_text', ''),
    )
    
    if not field:
        return jsonify({"error": "Object not found"}), 404
    
    return jsonify(field), 201


# ==================== API: CHATTER (COLLABORATION) ====================

@app.route('/api/chatter/feed/<record_type>/<record_id>', methods=['GET'])
def api_get_feed(record_type, record_id):
    """Get feed for a record"""
    feed = chatter_collaboration.get_record_feed(record_type, record_id)
    return jsonify({"feed": feed, "total": len(feed)})


@app.route('/api/chatter/feed/<record_type>/<record_id>', methods=['POST'])
def api_post_to_feed(record_type, record_id):
    """Post to record feed"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    post = chatter_collaboration.post_to_feed(
        user_id=user_id,
        record_type=record_type,
        record_id=record_id,
        content=data.get('content'),
        attachment=data.get('attachment'),
    )
    
    notify_user(
        user_id,
        NotificationType.COMMENT_ADDED.value,
        "Posted to Feed",
        "Your post was added to the feed",
        icon='comment',
        color='blue'
    )
    
    return jsonify(post), 201


@app.route('/api/chatter/comment/<post_id>', methods=['POST'])
def api_comment_on_post(post_id):
    """Add comment to post"""
    data = request.json
    user_id = data.get('user_id', 'user_1')
    
    comment = chatter_collaboration.comment_on_post(
        user_id=user_id,
        post_id=post_id,
        content=data.get('content'),
    )
    
    if not comment:
        return jsonify({"error": "Post not found"}), 404
    
    return jsonify(comment), 201


@app.route('/api/chatter/follow/<record_type>/<record_id>', methods=['POST'])
def api_follow_record(record_type, record_id):
    """Follow a record"""
    user_id = request.json.get('user_id', 'user_1')
    
    follow = chatter_collaboration.follow_record(user_id, record_type, record_id)
    
    return jsonify(follow), 201


@app.route('/api/chatter/unfollow/<record_type>/<record_id>', methods=['POST'])
def api_unfollow_record(record_type, record_id):
    """Unfollow a record"""
    user_id = request.json.get('user_id', 'user_1')
    
    unfollow = chatter_collaboration.unfollow_record(user_id, record_type, record_id)
    
    return jsonify({"success": unfollow})




if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
