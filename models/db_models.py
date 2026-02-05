"""
GeminiCRM Pro - SQLAlchemy Database Models
Real persistent database with SQLite
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import json

db = SQLAlchemy()

# ==================== HELPER FUNCTIONS ====================

def generate_uuid():
    return str(uuid.uuid4())

def get_current_time():
    return datetime.utcnow()

# ==================== USER MODELS ====================

class User(db.Model, UserMixin):
    """User account model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='sales_rep')  # admin, manager, sales_rep
    avatar_color = db.Column(db.String(20), default='#4285f4')
    phone = db.Column(db.String(50))
    title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    timezone = db.Column(db.String(50), default='UTC')
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    contacts = db.relationship('Contact', backref='owner', lazy='dynamic', foreign_keys='Contact.owner_id')
    leads = db.relationship('Lead', backref='owner', lazy='dynamic', foreign_keys='Lead.owner_id')
    accounts = db.relationship('Account', backref='owner', lazy='dynamic', foreign_keys='Account.owner_id')
    opportunities = db.relationship('Opportunity', backref='owner', lazy='dynamic', foreign_keys='Opportunity.owner_id')
    tasks = db.relationship('Task', backref='owner', lazy='dynamic', foreign_keys='Task.owner_id')
    activities = db.relationship('Activity', backref='owner', lazy='dynamic', foreign_keys='Activity.owner_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'initials': self.initials,
            'role': self.role,
            'avatar_color': self.avatar_color,
            'phone': self.phone,
            'title': self.title,
            'department': self.department,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== ACCOUNT (COMPANY) MODEL ====================

class Account(db.Model):
    """Account/Company model - central to all relationships"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False, index=True)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    annual_revenue = db.Column(db.Float, default=0)
    phone = db.Column(db.String(50))
    fax = db.Column(db.String(50))
    
    # Address
    billing_street = db.Column(db.String(255))
    billing_city = db.Column(db.String(100))
    billing_state = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(20))
    billing_country = db.Column(db.String(100))
    
    shipping_street = db.Column(db.String(255))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    shipping_country = db.Column(db.String(100))
    
    # Classification
    account_type = db.Column(db.String(50), default='prospect')  # prospect, customer, partner, competitor
    rating = db.Column(db.String(20))  # hot, warm, cold
    description = db.Column(db.Text)
    
    # Parent account for hierarchies
    parent_id = db.Column(db.String(36), db.ForeignKey('accounts.id'))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    contacts = db.relationship('Contact', backref='account', lazy='dynamic')
    opportunities = db.relationship('Opportunity', backref='account', lazy='dynamic')
    activities = db.relationship('Activity', backref='account', lazy='dynamic')
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'industry': self.industry,
            'company_size': self.company_size,
            'annual_revenue': self.annual_revenue,
            'phone': self.phone,
            'account_type': self.account_type,
            'rating': self.rating,
            'description': self.description,
            'billing_city': self.billing_city,
            'billing_country': self.billing_country,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'contacts_count': self.contacts.count(),
            'opportunities_count': self.opportunities.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== CONTACT MODEL ====================

class Contact(db.Model):
    """Contact model - individuals at accounts"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Address
    mailing_street = db.Column(db.String(255))
    mailing_city = db.Column(db.String(100))
    mailing_state = db.Column(db.String(100))
    mailing_postal_code = db.Column(db.String(20))
    mailing_country = db.Column(db.String(100))
    
    # Social & Web
    linkedin = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    
    # Status
    lead_source = db.Column(db.String(100))
    description = db.Column(db.Text)
    do_not_call = db.Column(db.Boolean, default=False)
    do_not_email = db.Column(db.Boolean, default=False)
    
    # Avatar
    avatar_color = db.Column(db.String(20), default='#4285f4')
    
    # Foreign Keys
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    last_activity_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    leads = db.relationship('Lead', backref='contact', lazy='dynamic')
    opportunities = db.relationship('Opportunity', backref='primary_contact', lazy='dynamic', foreign_keys='Opportunity.contact_id')
    activities = db.relationship('Activity', backref='contact', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'initials': self.initials,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'title': self.title,
            'department': self.department,
            'mailing_city': self.mailing_city,
            'mailing_country': self.mailing_country,
            'linkedin': self.linkedin,
            'twitter': self.twitter,
            'lead_source': self.lead_source,
            'description': self.description,
            'avatar_color': self.avatar_color,
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== LEAD MODEL ====================

class Lead(db.Model):
    """Lead model - potential customers not yet converted"""
    __tablename__ = 'leads'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    name = db.Column(db.String(255), nullable=False)  # Full name for display
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    company = db.Column(db.String(255))
    title = db.Column(db.String(100))
    website = db.Column(db.String(255))
    
    # Address
    street = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Lead info
    status = db.Column(db.String(50), default='new')  # new, contacted, qualified, unqualified, converted
    source = db.Column(db.String(100))  # website, referral, linkedin, google_ads, etc.
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    annual_revenue = db.Column(db.Float)
    estimated_value = db.Column(db.Float, default=0)
    
    # Scoring
    score = db.Column(db.Integer, default=50)
    rating = db.Column(db.String(20))  # hot, warm, cold
    
    # Engagement tracking
    email_opens = db.Column(db.Integer, default=0)
    email_clicks = db.Column(db.Integer, default=0)
    website_visits = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime)
    
    # AI Analysis
    ai_score = db.Column(db.Integer)
    ai_insights = db.Column(db.JSON, default=list)
    ai_next_action = db.Column(db.String(255))
    
    # Notes
    description = db.Column(db.Text)
    
    # Conversion info
    is_converted = db.Column(db.Boolean, default=False)
    converted_date = db.Column(db.DateTime)
    converted_account_id = db.Column(db.String(36))
    converted_contact_id = db.Column(db.String(36))
    converted_opportunity_id = db.Column(db.String(36))
    
    # Foreign Keys
    contact_id = db.Column(db.String(36), db.ForeignKey('contacts.id'))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    activities = db.relationship('Activity', backref='lead', lazy='dynamic')
    
    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.name[:2].upper() if self.name else 'NA'
    
    @property
    def score_grade(self):
        if self.score >= 80: return 'A'
        if self.score >= 60: return 'B'
        if self.score >= 40: return 'C'
        if self.score >= 20: return 'D'
        return 'F'
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'name': self.name,
            'initials': self.initials,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'title': self.title,
            'city': self.city,
            'country': self.country,
            'status': self.status,
            'source': self.source,
            'industry': self.industry,
            'estimated_value': self.estimated_value,
            'score': self.score,
            'score_grade': self.score_grade,
            'rating': self.rating,
            'email_opens': self.email_opens,
            'email_clicks': self.email_clicks,
            'website_visits': self.website_visits,
            'ai_score': self.ai_score,
            'ai_insights': self.ai_insights,
            'ai_next_action': self.ai_next_action,
            'description': self.description,
            'is_converted': self.is_converted,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== OPPORTUNITY MODEL ====================

class Opportunity(db.Model):
    """Opportunity/Deal model - sales opportunities"""
    __tablename__ = 'opportunities'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Value
    amount = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='USD')
    
    # Stage & Probability
    stage = db.Column(db.String(50), default='prospecting')
    # prospecting, qualification, needs_analysis, value_proposition, 
    # id_decision_makers, perception_analysis, proposal, negotiation, 
    # closed_won, closed_lost
    probability = db.Column(db.Integer, default=10)
    forecast_category = db.Column(db.String(50), default='pipeline')  # pipeline, best_case, commit, closed
    
    # Dates
    close_date = db.Column(db.Date)
    actual_close_date = db.Column(db.Date)
    
    # Type
    opportunity_type = db.Column(db.String(50))  # new_business, existing_business, renewal
    lead_source = db.Column(db.String(100))
    
    # Competition
    competitors = db.Column(db.JSON, default=list)
    
    # Next steps
    next_step = db.Column(db.String(255))
    
    # Loss reason (if closed_lost)
    loss_reason = db.Column(db.String(255))
    
    # AI Analysis
    ai_win_probability = db.Column(db.Integer)
    ai_insights = db.Column(db.JSON, default=list)
    ai_recommended_actions = db.Column(db.JSON, default=list)
    
    # Foreign Keys
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'))
    contact_id = db.Column(db.String(36), db.ForeignKey('contacts.id'))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    last_activity_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    line_items = db.relationship('OpportunityLineItem', backref='opportunity', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='opportunity', lazy='dynamic')
    
    @property
    def weighted_amount(self):
        return self.amount * (self.probability / 100)
    
    @property
    def stage_color(self):
        colors = {
            'prospecting': '#4285f4',
            'qualification': '#34a853',
            'needs_analysis': '#fbbc04',
            'value_proposition': '#ff6d01',
            'id_decision_makers': '#9334e6',
            'perception_analysis': '#00acc1',
            'proposal': '#e91e63',
            'negotiation': '#ff5722',
            'closed_won': '#0f9d58',
            'closed_lost': '#ea4335',
        }
        return colors.get(self.stage, '#9e9e9e')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'amount': self.amount,
            'currency': self.currency,
            'stage': self.stage,
            'stage_color': self.stage_color,
            'probability': self.probability,
            'forecast_category': self.forecast_category,
            'weighted_amount': self.weighted_amount,
            'close_date': self.close_date.isoformat() if self.close_date else None,
            'opportunity_type': self.opportunity_type,
            'lead_source': self.lead_source,
            'competitors': self.competitors,
            'next_step': self.next_step,
            'loss_reason': self.loss_reason,
            'ai_win_probability': self.ai_win_probability,
            'ai_insights': self.ai_insights,
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else None,
            'contact_id': self.contact_id,
            'contact_name': self.primary_contact.full_name if self.primary_contact else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== PRODUCT MODEL ====================

class Product(db.Model):
    """Product catalog"""
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    
    # Pricing
    unit_price = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='USD')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'unit_price': self.unit_price,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class OpportunityLineItem(db.Model):
    """Products/services in an opportunity"""
    __tablename__ = 'opportunity_line_items'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    opportunity_id = db.Column(db.String(36), db.ForeignKey('opportunities.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'))
    
    # Line item details
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, default=0)
    discount_percent = db.Column(db.Float, default=0)
    
    @property
    def total_price(self):
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percent / 100)
        return subtotal - discount
    
    def to_dict(self):
        return {
            'id': self.id,
            'opportunity_id': self.opportunity_id,
            'product_id': self.product_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount_percent': self.discount_percent,
            'total_price': self.total_price,
        }


# ==================== TASK MODEL ====================

class Task(db.Model):
    """Task/To-do model"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Status & Priority
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed, waiting, deferred
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Task type
    task_type = db.Column(db.String(50))  # call, email, meeting, follow_up, demo, other
    
    # Dates
    due_date = db.Column(db.DateTime)
    reminder_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    # Related to
    related_to_type = db.Column(db.String(50))  # account, contact, lead, opportunity
    related_to_id = db.Column(db.String(36))
    
    # Foreign Keys
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    assigned_to_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return self.due_date < datetime.utcnow()
        return False
    
    @property
    def priority_color(self):
        colors = {
            'low': '#9e9e9e',
            'normal': '#4285f4',
            'high': '#ff9800',
            'urgent': '#ea4335',
        }
        return colors.get(self.priority, '#9e9e9e')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'title': self.subject,  # Alias for compatibility
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'priority_color': self.priority_color,
            'task_type': self.task_type,
            'type': self.task_type,  # Alias
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'reminder_date': self.reminder_date.isoformat() if self.reminder_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'is_overdue': self.is_overdue,
            'related_to_type': self.related_to_type,
            'related_to_id': self.related_to_id,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': self.assigned_to.full_name if self.assigned_to else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== ACTIVITY MODEL ====================

class Activity(db.Model):
    """Activity log for all interactions"""
    __tablename__ = 'activities'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Activity type
    activity_type = db.Column(db.String(50), nullable=False)
    # call, email, meeting, task_completed, note, log_a_call, 
    # send_email, create_event, stage_change, deal_created, lead_converted
    
    # Status
    status = db.Column(db.String(50))  # scheduled, completed, cancelled
    
    # Date/Time
    activity_date = db.Column(db.DateTime, default=get_current_time)
    duration_minutes = db.Column(db.Integer)
    
    # Related to (polymorphic)
    related_to_type = db.Column(db.String(50))  # account, contact, lead, opportunity
    related_to_id = db.Column(db.String(36))
    
    # Specific foreign keys for easy querying
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'))
    contact_id = db.Column(db.String(36), db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.String(36), db.ForeignKey('leads.id'))
    opportunity_id = db.Column(db.String(36), db.ForeignKey('opportunities.id'))
    
    # Owner
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'description': self.description,
            'activity_type': self.activity_type,
            'status': self.status,
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'duration_minutes': self.duration_minutes,
            'related_to_type': self.related_to_type,
            'related_to_id': self.related_to_id,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== EMAIL TEMPLATE MODEL ====================

class EmailTemplate(db.Model):
    """Reusable email templates"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body_html = db.Column(db.Text)
    body_text = db.Column(db.Text)
    category = db.Column(db.String(100))  # follow_up, introduction, proposal, thank_you
    is_active = db.Column(db.Boolean, default=True)
    
    # Usage stats
    times_used = db.Column(db.Integer, default=0)
    
    # Owner
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body_html': self.body_html,
            'body_text': self.body_text,
            'category': self.category,
            'is_active': self.is_active,
            'times_used': self.times_used,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== NOTIFICATION MODEL ====================

class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # task_due, deal_update, lead_assigned, etc.
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    
    # Related to
    related_to_type = db.Column(db.String(50))
    related_to_id = db.Column(db.String(36))
    action_url = db.Column(db.String(255))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'related_to_type': self.related_to_type,
            'related_to_id': self.related_to_id,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== AUDIT LOG MODEL ====================

class AuditLog(db.Model):
    """Audit trail for all changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, view, export
    entity_type = db.Column(db.String(50), nullable=False)  # account, contact, lead, opportunity, etc.
    entity_id = db.Column(db.String(36))
    entity_name = db.Column(db.String(255))
    
    # Change details
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    
    # Context
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=get_current_time)
    
    # Relationship
    user = db.relationship('User', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ==================== INITIALIZE DATABASE ====================

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(email='admin@geminicrm.com').first()
        if not admin:
            admin = User(
                id='admin-001',
                email='admin@geminicrm.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                avatar_color='#4285f4'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample demo user
            demo = User(
                id='demo-001',
                email='demo@geminicrm.com',
                first_name='Demo',
                last_name='User',
                role='sales_rep',
                avatar_color='#34a853'
            )
            demo.set_password('demo123')
            db.session.add(demo)
            
            db.session.commit()
            print("✅ Database initialized with default users")
            print("   Admin: admin@geminicrm.com / admin123")
            print("   Demo:  demo@geminicrm.com / demo123")
            
            # Add sample data for demo
            _create_sample_data(admin.id)


def _create_sample_data(owner_id):
    """Create sample data for demo purposes"""
    from datetime import datetime, timedelta
    
    # Sample Accounts
    accounts_data = [
        {'id': 'acc-001', 'name': 'TechCorp Solutions', 'industry': 'Technology', 'website': 'https://techcorp.com', 'phone': '+1 (555) 123-4567', 'annual_revenue': 5000000, 'company_size': '201-500', 'billing_city': 'San Francisco', 'billing_state': 'CA', 'billing_country': 'USA'},
        {'id': 'acc-002', 'name': 'Global Industries Inc', 'industry': 'Manufacturing', 'website': 'https://globalind.com', 'phone': '+1 (555) 234-5678', 'annual_revenue': 15000000, 'company_size': '500+', 'billing_city': 'Chicago', 'billing_state': 'IL', 'billing_country': 'USA'},
        {'id': 'acc-003', 'name': 'StartupXYZ', 'industry': 'Technology', 'website': 'https://startupxyz.io', 'phone': '+1 (555) 345-6789', 'annual_revenue': 500000, 'company_size': '11-50', 'billing_city': 'Austin', 'billing_state': 'TX', 'billing_country': 'USA'},
        {'id': 'acc-004', 'name': 'FinanceFirst Bank', 'industry': 'Financial Services', 'website': 'https://financefirst.com', 'phone': '+1 (555) 456-7890', 'annual_revenue': 50000000, 'company_size': '500+', 'billing_city': 'New York', 'billing_state': 'NY', 'billing_country': 'USA'},
        {'id': 'acc-005', 'name': 'HealthCare Plus', 'industry': 'Healthcare', 'website': 'https://healthcareplus.com', 'phone': '+1 (555) 567-8901', 'annual_revenue': 8000000, 'company_size': '201-500', 'billing_city': 'Boston', 'billing_state': 'MA', 'billing_country': 'USA'},
    ]
    
    for acc_data in accounts_data:
        account = Account(owner_id=owner_id, **acc_data)
        db.session.add(account)
    
    # Sample Contacts
    contacts_data = [
        {'id': 'con-001', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@techcorp.com', 'phone': '+1 (555) 111-2222', 'title': 'CTO', 'department': 'Technology', 'account_id': 'acc-001'},
        {'id': 'con-002', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@globalind.com', 'phone': '+1 (555) 222-3333', 'title': 'VP of Operations', 'department': 'Operations', 'account_id': 'acc-002'},
        {'id': 'con-003', 'first_name': 'Mike', 'last_name': 'Davis', 'email': 'mike@startupxyz.io', 'phone': '+1 (555) 333-4444', 'title': 'CEO', 'department': 'Executive', 'account_id': 'acc-003'},
        {'id': 'con-004', 'first_name': 'Emily', 'last_name': 'Brown', 'email': 'emily.brown@financefirst.com', 'phone': '+1 (555) 444-5555', 'title': 'CFO', 'department': 'Finance', 'account_id': 'acc-004'},
        {'id': 'con-005', 'first_name': 'David', 'last_name': 'Wilson', 'email': 'dwilson@healthcareplus.com', 'phone': '+1 (555) 555-6666', 'title': 'Director of IT', 'department': 'Technology', 'account_id': 'acc-005'},
        {'id': 'con-006', 'first_name': 'Lisa', 'last_name': 'Anderson', 'email': 'lisa@techcorp.com', 'phone': '+1 (555) 666-7777', 'title': 'Product Manager', 'department': 'Product', 'account_id': 'acc-001'},
    ]
    
    for con_data in contacts_data:
        contact = Contact(owner_id=owner_id, **con_data)
        db.session.add(contact)
    
    # Sample Leads
    leads_data = [
        {'id': 'lead-001', 'first_name': 'Robert', 'last_name': 'Taylor', 'email': 'robert.taylor@newprospect.com', 'company': 'New Prospect Inc', 'title': 'Marketing Director', 'phone': '+1 (555) 777-8888', 'status': 'new', 'source': 'Website', 'score': 85},
        {'id': 'lead-002', 'first_name': 'Amanda', 'last_name': 'Martinez', 'email': 'amanda.m@futuretech.io', 'company': 'FutureTech', 'title': 'VP Sales', 'phone': '+1 (555) 888-9999', 'status': 'contacted', 'source': 'LinkedIn', 'score': 72},
        {'id': 'lead-003', 'first_name': 'Kevin', 'last_name': 'Lee', 'email': 'klee@innovate.co', 'company': 'Innovate Co', 'title': 'Operations Manager', 'phone': '+1 (555) 999-0000', 'status': 'qualified', 'source': 'Referral', 'score': 90},
        {'id': 'lead-004', 'first_name': 'Jennifer', 'last_name': 'White', 'email': 'jwhite@growthbiz.com', 'company': 'GrowthBiz', 'title': 'CEO', 'phone': '+1 (555) 000-1111', 'status': 'new', 'source': 'Trade Show', 'score': 65},
        {'id': 'lead-005', 'first_name': 'Chris', 'last_name': 'Garcia', 'email': 'cgarcia@enterprise.net', 'company': 'Enterprise Networks', 'title': 'IT Director', 'phone': '+1 (555) 111-3333', 'status': 'nurturing', 'source': 'Webinar', 'score': 78},
    ]
    
    for lead_data in leads_data:
        lead = Lead(owner_id=owner_id, **lead_data)
        db.session.add(lead)
    
    # Sample Opportunities (Deals)
    opps_data = [
        {'id': 'opp-001', 'name': 'TechCorp Enterprise License', 'account_id': 'acc-001', 'amount': 150000, 'stage': 'Negotiation', 'probability': 75, 'close_date': datetime.utcnow() + timedelta(days=15)},
        {'id': 'opp-002', 'name': 'Global Industries Platform Migration', 'account_id': 'acc-002', 'amount': 350000, 'stage': 'Proposal', 'probability': 50, 'close_date': datetime.utcnow() + timedelta(days=30)},
        {'id': 'opp-003', 'name': 'StartupXYZ Starter Package', 'account_id': 'acc-003', 'amount': 25000, 'stage': 'Qualification', 'probability': 30, 'close_date': datetime.utcnow() + timedelta(days=45)},
        {'id': 'opp-004', 'name': 'FinanceFirst Security Suite', 'account_id': 'acc-004', 'amount': 500000, 'stage': 'Closed Won', 'probability': 100, 'close_date': datetime.utcnow() - timedelta(days=10)},
        {'id': 'opp-005', 'name': 'HealthCare Plus Integration', 'account_id': 'acc-005', 'amount': 200000, 'stage': 'Prospecting', 'probability': 20, 'close_date': datetime.utcnow() + timedelta(days=60)},
    ]
    
    for opp_data in opps_data:
        opp = Opportunity(owner_id=owner_id, **opp_data)
        db.session.add(opp)
    
    # Sample Tasks
    tasks_data = [
        {'id': 'task-001', 'subject': 'Follow up with TechCorp on proposal', 'description': 'Schedule call to discuss enterprise license terms', 'priority': 'high', 'status': 'in_progress', 'due_date': datetime.utcnow() + timedelta(days=2), 'related_to_type': 'opportunity', 'related_to_id': 'opp-001'},
        {'id': 'task-002', 'subject': 'Send Global Industries contract', 'description': 'Prepare and send final contract documents', 'priority': 'high', 'status': 'not_started', 'due_date': datetime.utcnow() + timedelta(days=1), 'related_to_type': 'account', 'related_to_id': 'acc-002'},
        {'id': 'task-003', 'subject': 'Research StartupXYZ competitors', 'description': 'Competitive analysis for upcoming meeting', 'priority': 'normal', 'status': 'not_started', 'due_date': datetime.utcnow() + timedelta(days=5), 'related_to_type': 'account', 'related_to_id': 'acc-003'},
        {'id': 'task-004', 'subject': 'Quarterly review with HealthCare Plus', 'description': 'Prepare Q4 review presentation', 'priority': 'normal', 'status': 'not_started', 'due_date': datetime.utcnow() + timedelta(days=7), 'related_to_type': 'account', 'related_to_id': 'acc-005'},
        {'id': 'task-005', 'subject': 'Update CRM records', 'description': 'Ensure all recent activities are logged', 'priority': 'low', 'status': 'not_started', 'due_date': datetime.utcnow() + timedelta(days=3)},
    ]
    
    for task_data in tasks_data:
        task = Task(owner_id=owner_id, **task_data)
        db.session.add(task)
    
    db.session.commit()
    print("✅ Sample data created (5 accounts, 6 contacts, 5 leads, 5 opportunities, 5 tasks)")

