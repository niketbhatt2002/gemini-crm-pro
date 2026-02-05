"""
GeminiCRM Pro - Enterprise CRM Application
AI-Powered CRM built with Google Gemini - Better than Salesforce!
"""
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from config import Config
from models.db_models import (
    db, init_db, User, Account, Contact, Lead, Opportunity, 
    Task, Activity, Notification, EmailTemplate, AuditLog, Product
)
from services import gemini_service

# ==================== APP INITIALIZATION ====================

app = Flask(__name__)
app.config.from_object(Config)

# Secret key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Database configuration - SQLite for local, PostgreSQL for production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///geminicrm.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Initialize database
init_db(app)

# ==================== LOGIN MANAGER ====================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ==================== HELPER FUNCTIONS ====================

def log_activity(action, entity_type, entity_id=None, entity_name=None, old_values=None, new_values=None):
    """Log user activity for audit trail"""
    if current_user.is_authenticated:
        log = AuditLog(
            user_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:255] if request.user_agent else None
        )
        db.session.add(log)
        db.session.commit()


def create_notification(user_id, title, message, notification_type='info', related_type=None, related_id=None, priority='normal'):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_to_type=related_type,
        related_to_id=related_id,
        priority=priority
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def api_response(data=None, error=None, status=200):
    """Standardized API response"""
    if error:
        return jsonify({'success': False, 'error': error}), status
    return jsonify({'success': True, 'data': data}), status


# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity('login', 'user', user.id, user.full_name)
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        if not all([email, password, first_name, last_name]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='sales_rep'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create welcome notification
        create_notification(
            user.id,
            'Welcome to GeminiCRM Pro!',
            'Your account has been created successfully. Start by adding your first lead or contact.',
            'welcome'
        )
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    log_activity('logout', 'user', current_user.id, current_user.full_name)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In production, send email with reset link
            flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        else:
            flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


# ==================== PAGE ROUTES ====================

@app.route('/')
def index():
    """Landing page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('index.html', page='dashboard')


@app.route('/leads')
@login_required
def leads_page():
    """Leads management page"""
    return render_template('leads.html', page='leads')


@app.route('/contacts')
@login_required
def contacts_page():
    """Contacts page"""
    return render_template('contacts.html', page='contacts')


@app.route('/accounts')
@login_required
def accounts_page():
    """Accounts/Companies page"""
    return render_template('accounts.html', page='accounts')


@app.route('/opportunities')
@login_required
def opportunities_page():
    """Opportunities/Deals page"""
    return render_template('opportunities.html', page='opportunities')


@app.route('/deals')
@login_required
def deals_page():
    """Deals page (alias for opportunities)"""
    return render_template('deals.html', page='deals')


@app.route('/pipeline')
@login_required
def pipeline_page():
    """Visual pipeline page"""
    return render_template('pipeline.html', page='pipeline')


@app.route('/tasks')
@login_required
def tasks_page():
    """Tasks page"""
    return render_template('tasks.html', page='tasks')


@app.route('/calendar')
@login_required
def calendar_page():
    """Calendar page"""
    return render_template('calendar.html', page='calendar')


@app.route('/analytics')
@login_required
def analytics_page():
    """Analytics dashboard"""
    return render_template('analytics.html', page='analytics')


@app.route('/reports')
@login_required
def reports_page():
    """Reports page"""
    return render_template('reports.html', page='reports')


@app.route('/profile')
@login_required
def profile_page():
    """User profile page"""
    return render_template('profile.html', page='profile')


@app.route('/settings')
@login_required
def settings_page():
    """Settings page"""
    return render_template('settings.html', page='settings')


@app.route('/notifications')
@login_required
def notifications_page():
    """Notifications page"""
    return render_template('notifications.html', page='notifications')


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Resource not found"}), 404
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden(error):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Access forbidden"}), 403
    return render_template('errors/403.html'), 403


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


# ==================== API: CURRENT USER ====================

@app.route('/api/user/me', methods=['GET'])
@login_required
def api_current_user():
    """Get current logged-in user info"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })


@app.route('/api/user/me', methods=['PUT'])
@login_required
def api_update_current_user():
    """Update current user profile"""
    data = request.json
    
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    if 'phone' in data:
        current_user.phone = data['phone']
    if 'title' in data:
        current_user.title = data['title']
    if 'department' in data:
        current_user.department = data['department']
    if 'timezone' in data:
        current_user.timezone = data['timezone']
    if 'avatar_color' in data:
        current_user.avatar_color = data['avatar_color']
    
    db.session.commit()
    log_activity('update', 'user', current_user.id, current_user.full_name)
    
    return jsonify({'success': True, 'user': current_user.to_dict()})


# ==================== API: DASHBOARD ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """Get dashboard statistics"""
    # Get user's data
    leads = Lead.query.filter_by(owner_id=current_user.id).all()
    opportunities = Opportunity.query.filter_by(owner_id=current_user.id).all()
    tasks = Task.query.filter_by(owner_id=current_user.id).all()
    contacts = Contact.query.filter_by(owner_id=current_user.id).all()
    
    # Calculate stats
    total_pipeline = sum(o.amount or 0 for o in opportunities if o.stage not in ['closed_won', 'closed_lost'])
    weighted_pipeline = sum((o.amount or 0) * (o.probability or 0) / 100 for o in opportunities)
    won_deals = sum(o.amount or 0 for o in opportunities if o.stage == 'closed_won')
    avg_lead_score = sum(l.score or 0 for l in leads) / len(leads) if leads else 0
    
    # Deals by stage
    deals_by_stage = {}
    for o in opportunities:
        stage = o.stage or 'unknown'
        if stage not in deals_by_stage:
            deals_by_stage[stage] = {'count': 0, 'value': 0}
        deals_by_stage[stage]['count'] += 1
        deals_by_stage[stage]['value'] += o.amount or 0
    
    # Tasks summary
    today = datetime.utcnow().date()
    overdue_tasks = len([t for t in tasks if t.due_date and t.due_date.date() < today and t.status != 'completed'])
    today_tasks = len([t for t in tasks if t.due_date and t.due_date.date() == today])
    
    return jsonify({
        'success': True,
        'stats': {
            'total_leads': len(leads),
            'total_contacts': len(contacts),
            'total_opportunities': len(opportunities),
            'total_pipeline': total_pipeline,
            'weighted_pipeline': weighted_pipeline,
            'won_deals': won_deals,
            'avg_lead_score': round(avg_lead_score, 1),
            'deals_by_stage': deals_by_stage,
            'overdue_tasks': overdue_tasks,
            'today_tasks': today_tasks,
            'open_tasks': len([t for t in tasks if t.status != 'completed'])
        }
    })


# ==================== API: LEADS ====================

@app.route('/api/leads', methods=['GET'])
@login_required
def api_get_leads():
    """Get all leads for current user"""
    leads = Lead.query.filter_by(owner_id=current_user.id).order_by(Lead.created_at.desc()).all()
    return jsonify({
        'success': True,
        'leads': [l.to_dict() for l in leads]
    })


@app.route('/api/leads', methods=['POST'])
@login_required
def api_create_lead():
    """Create a new lead"""
    data = request.json
    
    lead = Lead(
        name=data.get('name', f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        company=data.get('company'),
        title=data.get('title'),
        source=data.get('source'),
        status=data.get('status', 'new'),
        industry=data.get('industry'),
        estimated_value=data.get('estimated_value', 0),
        description=data.get('description'),
        owner_id=current_user.id
    )
    
    db.session.add(lead)
    db.session.commit()
    
    log_activity('create', 'lead', lead.id, lead.name)
    
    return jsonify({
        'success': True,
        'lead': lead.to_dict()
    }), 201


@app.route('/api/leads/<lead_id>', methods=['GET'])
@login_required
def api_get_lead(lead_id):
    """Get a single lead"""
    lead = Lead.query.get_or_404(lead_id)
    return jsonify({'success': True, 'lead': lead.to_dict()})


@app.route('/api/leads/<lead_id>', methods=['PUT'])
@login_required
def api_update_lead(lead_id):
    """Update a lead"""
    lead = Lead.query.get_or_404(lead_id)
    data = request.json
    
    old_values = lead.to_dict()
    
    for key in ['name', 'first_name', 'last_name', 'email', 'phone', 'company', 
                'title', 'source', 'status', 'industry', 'estimated_value', 
                'description', 'score', 'rating']:
        if key in data:
            setattr(lead, key, data[key])
    
    db.session.commit()
    
    log_activity('update', 'lead', lead.id, lead.name, old_values, lead.to_dict())
    
    return jsonify({'success': True, 'lead': lead.to_dict()})


@app.route('/api/leads/<lead_id>', methods=['DELETE'])
@login_required
def api_delete_lead(lead_id):
    """Delete a lead"""
    lead = Lead.query.get_or_404(lead_id)
    log_activity('delete', 'lead', lead.id, lead.name)
    
    db.session.delete(lead)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/leads/<lead_id>/convert', methods=['POST'])
@login_required
def api_convert_lead(lead_id):
    """Convert lead to contact and optionally opportunity"""
    lead = Lead.query.get_or_404(lead_id)
    data = request.json
    
    # Create Account if company exists
    account = None
    if lead.company:
        account = Account(
            name=lead.company,
            website=lead.website,
            industry=lead.industry,
            owner_id=current_user.id
        )
        db.session.add(account)
        db.session.flush()
    
    # Create Contact
    contact = Contact(
        first_name=lead.first_name or lead.name.split()[0] if lead.name else 'Unknown',
        last_name=lead.last_name or (lead.name.split()[-1] if lead.name and ' ' in lead.name else ''),
        email=lead.email,
        phone=lead.phone,
        title=lead.title,
        account_id=account.id if account else None,
        lead_source=lead.source,
        owner_id=current_user.id
    )
    db.session.add(contact)
    db.session.flush()
    
    # Create Opportunity if requested
    opportunity = None
    if data.get('create_opportunity'):
        opportunity = Opportunity(
            name=f"{lead.company or lead.name} - Opportunity",
            amount=lead.estimated_value or 0,
            stage='prospecting',
            account_id=account.id if account else None,
            contact_id=contact.id,
            lead_source=lead.source,
            owner_id=current_user.id
        )
        db.session.add(opportunity)
        db.session.flush()
    
    # Mark lead as converted
    lead.is_converted = True
    lead.converted_date = datetime.utcnow()
    lead.converted_account_id = account.id if account else None
    lead.converted_contact_id = contact.id
    lead.converted_opportunity_id = opportunity.id if opportunity else None
    
    db.session.commit()
    
    log_activity('convert', 'lead', lead.id, lead.name)
    
    return jsonify({
        'success': True,
        'account': account.to_dict() if account else None,
        'contact': contact.to_dict(),
        'opportunity': opportunity.to_dict() if opportunity else None
    })


# ==================== API: CONTACTS ====================

@app.route('/api/contacts', methods=['GET'])
@login_required
def api_get_contacts():
    """Get all contacts"""
    contacts = Contact.query.filter_by(owner_id=current_user.id).order_by(Contact.created_at.desc()).all()
    return jsonify({
        'success': True,
        'contacts': [c.to_dict() for c in contacts]
    })


@app.route('/api/contacts', methods=['POST'])
@login_required
def api_create_contact():
    """Create a new contact"""
    data = request.json
    
    contact = Contact(
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        email=data.get('email'),
        phone=data.get('phone'),
        mobile=data.get('mobile'),
        title=data.get('title'),
        department=data.get('department'),
        account_id=data.get('account_id'),
        lead_source=data.get('lead_source'),
        description=data.get('description'),
        owner_id=current_user.id
    )
    
    db.session.add(contact)
    db.session.commit()
    
    log_activity('create', 'contact', contact.id, contact.full_name)
    
    return jsonify({
        'success': True,
        'contact': contact.to_dict()
    }), 201


@app.route('/api/contacts/<contact_id>', methods=['GET'])
@login_required
def api_get_contact(contact_id):
    """Get a single contact"""
    contact = Contact.query.get_or_404(contact_id)
    return jsonify({'success': True, 'contact': contact.to_dict()})


@app.route('/api/contacts/<contact_id>', methods=['PUT'])
@login_required
def api_update_contact(contact_id):
    """Update a contact"""
    contact = Contact.query.get_or_404(contact_id)
    data = request.json
    
    old_values = contact.to_dict()
    
    for key in ['first_name', 'last_name', 'email', 'phone', 'mobile', 
                'title', 'department', 'account_id', 'description']:
        if key in data:
            setattr(contact, key, data[key])
    
    db.session.commit()
    
    log_activity('update', 'contact', contact.id, contact.full_name, old_values, contact.to_dict())
    
    return jsonify({'success': True, 'contact': contact.to_dict()})


@app.route('/api/contacts/<contact_id>', methods=['DELETE'])
@login_required
def api_delete_contact(contact_id):
    """Delete a contact"""
    contact = Contact.query.get_or_404(contact_id)
    log_activity('delete', 'contact', contact.id, contact.full_name)
    
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== API: ACCOUNTS ====================

@app.route('/api/accounts', methods=['GET'])
@login_required
def api_get_accounts():
    """Get all accounts"""
    accounts = Account.query.filter_by(owner_id=current_user.id).order_by(Account.created_at.desc()).all()
    return jsonify({
        'success': True,
        'accounts': [a.to_dict() for a in accounts]
    })


@app.route('/api/accounts', methods=['POST'])
@login_required
def api_create_account():
    """Create a new account"""
    data = request.json
    
    account = Account(
        name=data.get('name', ''),
        website=data.get('website'),
        industry=data.get('industry'),
        company_size=data.get('company_size'),
        annual_revenue=data.get('annual_revenue'),
        phone=data.get('phone'),
        account_type=data.get('account_type', 'prospect'),
        description=data.get('description'),
        owner_id=current_user.id
    )
    
    db.session.add(account)
    db.session.commit()
    
    log_activity('create', 'account', account.id, account.name)
    
    return jsonify({
        'success': True,
        'account': account.to_dict()
    }), 201


@app.route('/api/accounts/<account_id>', methods=['GET'])
@login_required
def api_get_account(account_id):
    """Get a single account"""
    account = Account.query.get_or_404(account_id)
    return jsonify({'success': True, 'account': account.to_dict()})


@app.route('/api/accounts/<account_id>', methods=['PUT'])
@login_required
def api_update_account(account_id):
    """Update an account"""
    account = Account.query.get_or_404(account_id)
    data = request.json
    
    for key in ['name', 'website', 'industry', 'company_size', 'annual_revenue', 
                'phone', 'account_type', 'description', 'rating']:
        if key in data:
            setattr(account, key, data[key])
    
    db.session.commit()
    
    return jsonify({'success': True, 'account': account.to_dict()})


@app.route('/api/accounts/<account_id>', methods=['DELETE'])
@login_required
def api_delete_account(account_id):
    """Delete an account"""
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== API: OPPORTUNITIES (DEALS) ====================

@app.route('/api/opportunities', methods=['GET'])
@login_required
def api_get_opportunities():
    """Get all opportunities"""
    opportunities = Opportunity.query.filter_by(owner_id=current_user.id).order_by(Opportunity.created_at.desc()).all()
    return jsonify({
        'success': True,
        'opportunities': [o.to_dict() for o in opportunities],
        'deals': [o.to_dict() for o in opportunities]  # Alias for compatibility
    })


@app.route('/api/deals', methods=['GET'])
@login_required
def api_get_deals():
    """Get all deals (alias for opportunities)"""
    return api_get_opportunities()


@app.route('/api/opportunities', methods=['POST'])
@login_required
def api_create_opportunity():
    """Create a new opportunity"""
    data = request.json
    
    opportunity = Opportunity(
        name=data.get('name', ''),
        description=data.get('description'),
        amount=data.get('amount', 0),
        stage=data.get('stage', 'prospecting'),
        probability=data.get('probability', 10),
        close_date=datetime.strptime(data['close_date'], '%Y-%m-%d').date() if data.get('close_date') else None,
        account_id=data.get('account_id'),
        contact_id=data.get('contact_id'),
        opportunity_type=data.get('opportunity_type'),
        lead_source=data.get('lead_source'),
        next_step=data.get('next_step'),
        owner_id=current_user.id
    )
    
    db.session.add(opportunity)
    db.session.commit()
    
    log_activity('create', 'opportunity', opportunity.id, opportunity.name)
    
    return jsonify({
        'success': True,
        'opportunity': opportunity.to_dict(),
        'deal': opportunity.to_dict()
    }), 201


@app.route('/api/deals', methods=['POST'])
@login_required
def api_create_deal():
    """Create a new deal (alias)"""
    return api_create_opportunity()


@app.route('/api/opportunities/<opp_id>', methods=['GET'])
@login_required
def api_get_opportunity(opp_id):
    """Get a single opportunity"""
    opportunity = Opportunity.query.get_or_404(opp_id)
    return jsonify({'success': True, 'opportunity': opportunity.to_dict()})


@app.route('/api/opportunities/<opp_id>', methods=['PUT'])
@login_required
def api_update_opportunity(opp_id):
    """Update an opportunity"""
    opportunity = Opportunity.query.get_or_404(opp_id)
    data = request.json
    
    old_stage = opportunity.stage
    
    for key in ['name', 'description', 'amount', 'stage', 'probability', 
                'opportunity_type', 'lead_source', 'next_step', 'loss_reason']:
        if key in data:
            setattr(opportunity, key, data[key])
    
    if data.get('close_date'):
        opportunity.close_date = datetime.strptime(data['close_date'], '%Y-%m-%d').date()
    
    # If stage changed, update probability automatically
    stage_probabilities = {
        'prospecting': 10,
        'qualification': 20,
        'needs_analysis': 30,
        'value_proposition': 40,
        'id_decision_makers': 50,
        'perception_analysis': 60,
        'proposal': 70,
        'negotiation': 80,
        'closed_won': 100,
        'closed_lost': 0
    }
    
    if 'stage' in data and data['stage'] in stage_probabilities:
        opportunity.probability = stage_probabilities[data['stage']]
    
    db.session.commit()
    
    return jsonify({'success': True, 'opportunity': opportunity.to_dict()})


@app.route('/api/deals/<deal_id>', methods=['PUT'])
@login_required
def api_update_deal(deal_id):
    """Update deal (alias)"""
    return api_update_opportunity(deal_id)


@app.route('/api/opportunities/<opp_id>', methods=['DELETE'])
@login_required
def api_delete_opportunity(opp_id):
    """Delete an opportunity"""
    opportunity = Opportunity.query.get_or_404(opp_id)
    db.session.delete(opportunity)
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/deals/<deal_id>', methods=['DELETE'])
@login_required
def api_delete_deal(deal_id):
    """Delete deal (alias)"""
    return api_delete_opportunity(deal_id)


# ==================== API: TASKS ====================

@app.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    """Get all tasks"""
    tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.due_date.asc()).all()
    return jsonify({
        'success': True,
        'tasks': [t.to_dict() for t in tasks]
    })


@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    """Create a new task"""
    data = request.json
    
    task = Task(
        subject=data.get('subject', data.get('title', '')),
        description=data.get('description'),
        status=data.get('status', 'not_started'),
        priority=data.get('priority', 'normal'),
        task_type=data.get('task_type', data.get('type')),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M:%S') if data.get('due_date') else None,
        related_to_type=data.get('related_to_type'),
        related_to_id=data.get('related_to_id'),
        owner_id=current_user.id,
        assigned_to_id=data.get('assigned_to_id', current_user.id)
    )
    
    db.session.add(task)
    db.session.commit()
    
    log_activity('create', 'task', task.id, task.subject)
    
    return jsonify({
        'success': True,
        'task': task.to_dict()
    }), 201


@app.route('/api/tasks/<task_id>', methods=['GET'])
@login_required
def api_get_task(task_id):
    """Get a single task"""
    task = Task.query.get_or_404(task_id)
    return jsonify({'success': True, 'task': task.to_dict()})


@app.route('/api/tasks/<task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    """Update a task"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    for key in ['subject', 'description', 'status', 'priority', 'task_type']:
        if key in data:
            setattr(task, key, data[key])
    
    if 'title' in data:
        task.subject = data['title']
    
    if data.get('due_date'):
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M:%S')
        except:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
    
    if data.get('status') == 'completed' and not task.completed_date:
        task.completed_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'task': task.to_dict()})


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== API: ACTIVITIES ====================

@app.route('/api/activities', methods=['GET'])
@login_required
def api_get_activities():
    """Get recent activities"""
    limit = request.args.get('limit', 50, type=int)
    activities = Activity.query.filter_by(owner_id=current_user.id).order_by(Activity.created_at.desc()).limit(limit).all()
    return jsonify({
        'success': True,
        'activities': [a.to_dict() for a in activities]
    })


@app.route('/api/activities', methods=['POST'])
@login_required
def api_create_activity():
    """Log an activity"""
    data = request.json
    
    activity = Activity(
        subject=data.get('subject', ''),
        description=data.get('description'),
        activity_type=data.get('activity_type', 'note'),
        status=data.get('status', 'completed'),
        activity_date=datetime.utcnow(),
        duration_minutes=data.get('duration_minutes'),
        related_to_type=data.get('related_to_type'),
        related_to_id=data.get('related_to_id'),
        account_id=data.get('account_id'),
        contact_id=data.get('contact_id'),
        lead_id=data.get('lead_id'),
        opportunity_id=data.get('opportunity_id'),
        owner_id=current_user.id
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'activity': activity.to_dict()
    }), 201


# ==================== API: NOTIFICATIONS ====================

@app.route('/api/notifications', methods=['GET'])
@login_required
def api_get_notifications():
    """Get user notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    })


@app.route('/api/notifications/<notif_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notif_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notif_id)
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def api_mark_all_notifications_read():
    """Mark all notifications as read"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== API: AI FEATURES ====================

@app.route('/api/ai/score-lead', methods=['POST'])
@login_required
def api_ai_score_lead():
    """AI Lead Scoring"""
    data = request.json
    
    if not gemini_service.is_configured():
        return jsonify({'error': 'AI service not configured. Please set your API key.'}), 400
    
    result = gemini_service.score_lead(data)
    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/generate-email', methods=['POST'])
@login_required
def api_ai_generate_email():
    """AI Email Generation"""
    data = request.json
    
    if not gemini_service.is_configured():
        return jsonify({'error': 'AI service not configured. Please set your API key.'}), 400
    
    result = gemini_service.generate_email(
        email_type=data.get('email_type', 'follow_up'),
        context=data.get('context', {})
    )
    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/predict-deal', methods=['POST'])
@login_required
def api_ai_predict_deal():
    """AI Deal Prediction"""
    data = request.json
    
    if not gemini_service.is_configured():
        return jsonify({'error': 'AI service not configured. Please set your API key.'}), 400
    
    result = gemini_service.predict_deal(data)
    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/suggest-actions', methods=['POST'])
@login_required
def api_ai_suggest_actions():
    """AI Action Suggestions"""
    data = request.json
    
    if not gemini_service.is_configured():
        return jsonify({'error': 'AI service not configured. Please set your API key.'}), 400
    
    result = gemini_service.suggest_next_actions(data)
    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/analyze-sentiment', methods=['POST'])
@login_required
def api_ai_analyze_sentiment():
    """AI Sentiment Analysis"""
    data = request.json
    text = data.get('text', '')
    
    if not gemini_service.is_configured():
        return jsonify({'error': 'AI service not configured. Please set your API key.'}), 400
    
    result = gemini_service.analyze_sentiment(text)
    return jsonify({'success': True, 'result': result})


@app.route('/api/ai/insights', methods=['GET'])
@login_required
def api_ai_insights():
    """Get AI-powered insights for dashboard"""
    if not gemini_service.is_configured():
        # Return default insights if AI not configured
        return jsonify({
            'success': True,
            'insights': [
                {
                    'type': 'tip',
                    'title': 'Configure AI',
                    'message': 'Set up your Gemini API key to unlock AI-powered insights and recommendations.',
                    'action': 'Configure Now',
                    'action_url': '#'
                }
            ]
        })
    
    # Get user's data for AI analysis
    leads = Lead.query.filter_by(owner_id=current_user.id).all()
    opportunities = Opportunity.query.filter_by(owner_id=current_user.id).all()
    tasks = Task.query.filter_by(owner_id=current_user.id).all()
    
    insights = gemini_service.generate_insights({
        'leads': [l.to_dict() for l in leads],
        'opportunities': [o.to_dict() for o in opportunities],
        'tasks': [t.to_dict() for t in tasks]
    })
    
    return jsonify({'success': True, 'insights': insights})


# ==================== API: SEARCH ====================

@app.route('/api/search', methods=['GET'])
@login_required
def api_global_search():
    """Global search across all entities"""
    query = request.args.get('q', '').strip().lower()
    
    if len(query) < 2:
        return jsonify({'success': True, 'results': []})
    
    results = []
    
    # Search leads
    leads = Lead.query.filter(
        Lead.owner_id == current_user.id,
        (Lead.name.ilike(f'%{query}%') | Lead.email.ilike(f'%{query}%') | Lead.company.ilike(f'%{query}%'))
    ).limit(5).all()
    results.extend([{'type': 'lead', 'id': l.id, 'name': l.name, 'subtitle': l.company} for l in leads])
    
    # Search contacts
    contacts = Contact.query.filter(
        Contact.owner_id == current_user.id,
        (Contact.first_name.ilike(f'%{query}%') | Contact.last_name.ilike(f'%{query}%') | Contact.email.ilike(f'%{query}%'))
    ).limit(5).all()
    results.extend([{'type': 'contact', 'id': c.id, 'name': c.full_name, 'subtitle': c.email} for c in contacts])
    
    # Search opportunities
    opportunities = Opportunity.query.filter(
        Opportunity.owner_id == current_user.id,
        Opportunity.name.ilike(f'%{query}%')
    ).limit(5).all()
    results.extend([{'type': 'opportunity', 'id': o.id, 'name': o.name, 'subtitle': f'${o.amount:,.0f}'} for o in opportunities])
    
    # Search accounts
    accounts = Account.query.filter(
        Account.owner_id == current_user.id,
        Account.name.ilike(f'%{query}%')
    ).limit(5).all()
    results.extend([{'type': 'account', 'id': a.id, 'name': a.name, 'subtitle': a.industry} for a in accounts])
    
    return jsonify({'success': True, 'results': results})


# ==================== API: REPORTS ====================

@app.route('/api/reports/pipeline', methods=['GET'])
@login_required
def api_report_pipeline():
    """Pipeline report data"""
    opportunities = Opportunity.query.filter_by(owner_id=current_user.id).all()
    
    by_stage = {}
    for opp in opportunities:
        stage = opp.stage or 'unknown'
        if stage not in by_stage:
            by_stage[stage] = {'count': 0, 'value': 0}
        by_stage[stage]['count'] += 1
        by_stage[stage]['value'] += opp.amount or 0
    
    return jsonify({
        'success': True,
        'report': {
            'by_stage': by_stage,
            'total_count': len(opportunities),
            'total_value': sum(o.amount or 0 for o in opportunities)
        }
    })


@app.route('/api/reports/leads', methods=['GET'])
@login_required
def api_report_leads():
    """Leads report data"""
    leads = Lead.query.filter_by(owner_id=current_user.id).all()
    
    by_source = {}
    by_status = {}
    
    for lead in leads:
        source = lead.source or 'unknown'
        status = lead.status or 'unknown'
        
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1
        
        if status not in by_status:
            by_status[status] = 0
        by_status[status] += 1
    
    return jsonify({
        'success': True,
        'report': {
            'by_source': by_source,
            'by_status': by_status,
            'total_count': len(leads),
            'avg_score': sum(l.score or 0 for l in leads) / len(leads) if leads else 0
        }
    })


# ==================== API: EXPORT ====================

@app.route('/api/export/<entity_type>', methods=['GET'])
@login_required
def api_export_data(entity_type):
    """Export data as JSON (can be extended for CSV/Excel)"""
    format_type = request.args.get('format', 'json')
    
    data = []
    if entity_type == 'leads':
        items = Lead.query.filter_by(owner_id=current_user.id).all()
        data = [l.to_dict() for l in items]
    elif entity_type == 'contacts':
        items = Contact.query.filter_by(owner_id=current_user.id).all()
        data = [c.to_dict() for c in items]
    elif entity_type == 'opportunities':
        items = Opportunity.query.filter_by(owner_id=current_user.id).all()
        data = [o.to_dict() for o in items]
    elif entity_type == 'accounts':
        items = Account.query.filter_by(owner_id=current_user.id).all()
        data = [a.to_dict() for a in items]
    elif entity_type == 'tasks':
        items = Task.query.filter_by(owner_id=current_user.id).all()
        data = [t.to_dict() for t in items]
    else:
        return jsonify({'error': f'Unknown entity type: {entity_type}'}), 400
    
    log_activity('export', entity_type, None, f'Exported {len(data)} {entity_type}')
    
    return jsonify({
        'success': True,
        'entity_type': entity_type,
        'count': len(data),
        'data': data
    })


# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print("\n" + "="*60)
    print("🚀 GeminiCRM Pro - Enterprise CRM")
    print("="*60)
    print(f"🌐 Running on: http://127.0.0.1:{port}")
    print(f"📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\n📋 Default Users:")
    print("   Admin: admin@geminicrm.com / admin123")
    print("   Demo:  demo@geminicrm.com / demo123")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
