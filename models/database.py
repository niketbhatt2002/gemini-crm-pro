"""
GeminiCRM Pro - Data Models & In-Memory Database
In production, replace with PostgreSQL/MongoDB
"""
import uuid
from datetime import datetime, timedelta
import random

# ==================== IN-MEMORY DATABASE ====================
DB = {
    'contacts': {},
    'leads': {},
    'deals': {},
    'tasks': {},
    'activities': {},
    'emails': {},
    'notes': {},
    'tags': {},
    'users': {},
}

# ==================== MODEL CLASSES ====================

class Contact:
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.first_name = data.get('first_name', '')
        self.last_name = data.get('last_name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.company = data.get('company', '')
        self.title = data.get('title', '')
        self.industry = data.get('industry', '')
        self.website = data.get('website', '')
        self.address = data.get('address', '')
        self.city = data.get('city', '')
        self.country = data.get('country', '')
        self.linkedin = data.get('linkedin', '')
        self.twitter = data.get('twitter', '')
        self.tags = data.get('tags', [])
        self.avatar_color = data.get('avatar_color', self._random_color())
        self.owner_id = data.get('owner_id', 'user_1')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    def _random_color(self):
        colors = ['#4285f4', '#34a853', '#fbbc04', '#ea4335', '#9334e6', '#00acc1']
        return random.choice(colors)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'initials': self.initials,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'title': self.title,
            'industry': self.industry,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'linkedin': self.linkedin,
            'twitter': self.twitter,
            'tags': self.tags,
            'avatar_color': self.avatar_color,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Lead:
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.contact_id = data.get('contact_id')
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.company = data.get('company', '')
        self.title = data.get('title', '')
        self.source = data.get('source', 'Website')
        self.status = data.get('status', 'New')  # New, Contacted, Qualified, Unqualified
        self.score = data.get('score', 50)
        self.estimated_value = data.get('estimated_value', 0)
        self.notes = data.get('notes', '')
        self.tags = data.get('tags', [])
        
        # Engagement metrics
        self.email_opens = data.get('email_opens', 0)
        self.email_clicks = data.get('email_clicks', 0)
        self.website_visits = data.get('website_visits', 0)
        self.last_activity = data.get('last_activity', datetime.now().isoformat())
        
        # AI Analysis
        self.ai_score = data.get('ai_score')
        self.ai_insights = data.get('ai_insights', [])
        
        self.owner_id = data.get('owner_id', 'user_1')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][:1] + parts[-1][:1]).upper()
        return self.name[:2].upper()
    
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
            'contact_id': self.contact_id,
            'name': self.name,
            'initials': self.initials,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'title': self.title,
            'source': self.source,
            'status': self.status,
            'score': self.score,
            'score_grade': self.score_grade,
            'estimated_value': self.estimated_value,
            'notes': self.notes,
            'tags': self.tags,
            'email_opens': self.email_opens,
            'email_clicks': self.email_clicks,
            'website_visits': self.website_visits,
            'last_activity': self.last_activity,
            'ai_score': self.ai_score,
            'ai_insights': self.ai_insights,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Deal:
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name', '')
        self.contact_id = data.get('contact_id')
        self.lead_id = data.get('lead_id')
        self.company = data.get('company', '')
        self.value = data.get('value', 0)
        self.currency = data.get('currency', 'USD')
        self.stage = data.get('stage', 'lead')  # lead, qualified, proposal, negotiation, closed_won, closed_lost
        self.probability = data.get('probability', 10)
        self.expected_close_date = data.get('expected_close_date')
        self.actual_close_date = data.get('actual_close_date')
        self.description = data.get('description', '')
        self.notes = data.get('notes', '')
        self.tags = data.get('tags', [])
        self.products = data.get('products', [])
        
        # AI Predictions
        self.ai_win_probability = data.get('ai_win_probability')
        self.ai_insights = data.get('ai_insights', [])
        self.ai_next_steps = data.get('ai_next_steps', [])
        
        self.owner_id = data.get('owner_id', 'user_1')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    @property
    def weighted_value(self):
        return self.value * (self.probability / 100)
    
    @property
    def stage_color(self):
        colors = {
            'lead': '#4285f4',
            'qualified': '#34a853',
            'proposal': '#fbbc04',
            'negotiation': '#ff6d01',
            'closed_won': '#0f9d58',
            'closed_lost': '#ea4335',
        }
        return colors.get(self.stage, '#9e9e9e')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'company': self.company,
            'value': self.value,
            'currency': self.currency,
            'stage': self.stage,
            'stage_color': self.stage_color,
            'probability': self.probability,
            'weighted_value': self.weighted_value,
            'expected_close_date': self.expected_close_date,
            'actual_close_date': self.actual_close_date,
            'description': self.description,
            'notes': self.notes,
            'tags': self.tags,
            'products': self.products,
            'ai_win_probability': self.ai_win_probability,
            'ai_insights': self.ai_insights,
            'ai_next_steps': self.ai_next_steps,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Task:
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.type = data.get('type', 'Other')  # Call, Email, Meeting, Follow-up, Demo, Other
        self.priority = data.get('priority', 'Medium')  # Low, Medium, High, Urgent
        self.status = data.get('status', 'pending')  # pending, in_progress, completed, cancelled
        self.due_date = data.get('due_date')
        self.due_time = data.get('due_time')
        self.completed_at = data.get('completed_at')
        
        # Relations
        self.contact_id = data.get('contact_id')
        self.lead_id = data.get('lead_id')
        self.deal_id = data.get('deal_id')
        
        # AI Generated
        self.ai_generated = data.get('ai_generated', False)
        self.ai_reason = data.get('ai_reason', '')
        
        self.owner_id = data.get('owner_id', 'user_1')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.fromisoformat(self.due_date).date() < datetime.now().date()
        return False
    
    @property
    def priority_color(self):
        colors = {
            'Low': '#9e9e9e',
            'Medium': '#4285f4',
            'High': '#fbbc04',
            'Urgent': '#ea4335',
        }
        return colors.get(self.priority, '#9e9e9e')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'priority': self.priority,
            'priority_color': self.priority_color,
            'status': self.status,
            'due_date': self.due_date,
            'due_time': self.due_time,
            'completed_at': self.completed_at,
            'is_overdue': self.is_overdue,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'deal_id': self.deal_id,
            'ai_generated': self.ai_generated,
            'ai_reason': self.ai_reason,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Activity:
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.type = data.get('type', 'note')  # note, email, call, meeting, task_completed, deal_updated, etc.
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.contact_id = data.get('contact_id')
        self.lead_id = data.get('lead_id')
        self.deal_id = data.get('deal_id')
        self.metadata = data.get('metadata', {})
        self.owner_id = data.get('owner_id', 'user_1')
        self.created_at = data.get('created_at', datetime.now().isoformat())
    
    @property
    def icon(self):
        icons = {
            'note': 'description',
            'email': 'email',
            'call': 'phone',
            'meeting': 'event',
            'task_completed': 'check_circle',
            'deal_updated': 'trending_up',
            'lead_created': 'person_add',
            'ai_insight': 'auto_awesome',
        }
        return icons.get(self.type, 'circle')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'icon': self.icon,
            'title': self.title,
            'description': self.description,
            'contact_id': self.contact_id,
            'lead_id': self.lead_id,
            'deal_id': self.deal_id,
            'metadata': self.metadata,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
        }


# ==================== DATABASE OPERATIONS ====================

def init_sample_data():
    """Initialize database with sample data"""
    
    # Sample Contacts
    contacts_data = [
        {
            'first_name': 'Sarah', 'last_name': 'Johnson',
            'email': 'sarah.johnson@techcorp.com', 'phone': '+1 (555) 123-4567',
            'company': 'TechCorp Industries', 'title': 'VP of Engineering',
            'industry': 'Technology', 'city': 'San Francisco', 'country': 'USA',
        },
        {
            'first_name': 'Michael', 'last_name': 'Chen',
            'email': 'm.chen@innovateai.io', 'phone': '+1 (555) 234-5678',
            'company': 'InnovateAI', 'title': 'CTO',
            'industry': 'AI/ML', 'city': 'Austin', 'country': 'USA',
        },
        {
            'first_name': 'Emily', 'last_name': 'Rodriguez',
            'email': 'emily.r@globalretail.com', 'phone': '+1 (555) 345-6789',
            'company': 'Global Retail Solutions', 'title': 'Director of Sales',
            'industry': 'Retail', 'city': 'New York', 'country': 'USA',
        },
        {
            'first_name': 'David', 'last_name': 'Park',
            'email': 'dpark@finservices.net', 'phone': '+1 (555) 456-7890',
            'company': 'Premier Financial Services', 'title': 'Operations Manager',
            'industry': 'Finance', 'city': 'Chicago', 'country': 'USA',
        },
        {
            'first_name': 'Lisa', 'last_name': 'Thompson',
            'email': 'lthompson@healthplus.org', 'phone': '+1 (555) 567-8901',
            'company': 'HealthPlus Medical', 'title': 'IT Director',
            'industry': 'Healthcare', 'city': 'Boston', 'country': 'USA',
        },
        {
            'first_name': 'James', 'last_name': 'Wilson',
            'email': 'jwilson@acmesoftware.com', 'phone': '+1 (555) 678-9012',
            'company': 'Acme Software', 'title': 'CEO',
            'industry': 'Software', 'city': 'Seattle', 'country': 'USA',
        },
    ]
    
    for data in contacts_data:
        contact = Contact(data)
        DB['contacts'][contact.id] = contact.to_dict()
    
    contact_ids = list(DB['contacts'].keys())
    
    # Sample Leads
    leads_data = [
        {
            'name': 'Sarah Johnson', 'email': 'sarah.johnson@techcorp.com',
            'company': 'TechCorp Industries', 'title': 'VP of Engineering',
            'source': 'Website', 'status': 'Qualified', 'score': 85,
            'estimated_value': 75000, 'email_opens': 12, 'website_visits': 8,
            'notes': 'Very interested in enterprise features. Has budget approval for Q1.',
            'contact_id': contact_ids[0],
        },
        {
            'name': 'Michael Chen', 'email': 'm.chen@innovateai.io',
            'company': 'InnovateAI', 'title': 'CTO',
            'source': 'LinkedIn', 'status': 'New', 'score': 62,
            'estimated_value': 120000, 'email_opens': 4, 'website_visits': 15,
            'notes': 'AI startup with Series B funding. Decision maker.',
            'contact_id': contact_ids[1],
        },
        {
            'name': 'Emily Rodriguez', 'email': 'emily.r@globalretail.com',
            'company': 'Global Retail Solutions', 'title': 'Director of Sales',
            'source': 'Trade Show', 'status': 'Contacted', 'score': 78,
            'estimated_value': 45000, 'email_opens': 9, 'website_visits': 6,
            'notes': 'Met at SaaS Summit 2025. Needs Shopify integration.',
            'contact_id': contact_ids[2],
        },
        {
            'name': 'David Park', 'email': 'dpark@finservices.net',
            'company': 'Premier Financial', 'title': 'Operations Manager',
            'source': 'Referral', 'status': 'Qualified', 'score': 91,
            'estimated_value': 95000, 'email_opens': 18, 'website_visits': 22,
            'notes': 'Referred by existing customer. Needs SOC2 compliance.',
            'contact_id': contact_ids[3],
        },
        {
            'name': 'Lisa Thompson', 'email': 'lthompson@healthplus.org',
            'company': 'HealthPlus Medical', 'title': 'IT Director',
            'source': 'Google Ads', 'status': 'New', 'score': 25,
            'estimated_value': 30000, 'email_opens': 1, 'website_visits': 2,
            'notes': 'Downloaded whitepaper. No response yet.',
            'contact_id': contact_ids[4],
        },
    ]
    
    for data in leads_data:
        lead = Lead(data)
        DB['leads'][lead.id] = lead.to_dict()
    
    lead_ids = list(DB['leads'].keys())
    
    # Sample Deals
    deals_data = [
        {
            'name': 'TechCorp Enterprise License',
            'company': 'TechCorp Industries',
            'value': 75000, 'stage': 'proposal', 'probability': 60,
            'expected_close_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[0], 'lead_id': lead_ids[0],
            'description': 'Enterprise license for 50 users',
        },
        {
            'name': 'InnovateAI Platform Deal',
            'company': 'InnovateAI',
            'value': 120000, 'stage': 'qualified', 'probability': 30,
            'expected_close_date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[1], 'lead_id': lead_ids[1],
            'description': 'Full platform implementation',
        },
        {
            'name': 'Premier Financial - Annual Contract',
            'company': 'Premier Financial Services',
            'value': 95000, 'stage': 'negotiation', 'probability': 75,
            'expected_close_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[3], 'lead_id': lead_ids[3],
            'description': 'Annual enterprise contract with SOC2',
        },
        {
            'name': 'Global Retail - Starter Package',
            'company': 'Global Retail Solutions',
            'value': 45000, 'stage': 'proposal', 'probability': 50,
            'expected_close_date': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[2], 'lead_id': lead_ids[2],
            'description': 'Starter package with Shopify integration',
        },
        {
            'name': 'Acme Software - Pilot Program',
            'company': 'Acme Software',
            'value': 25000, 'stage': 'lead', 'probability': 10,
            'expected_close_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[5],
            'description': 'Initial pilot program',
        },
    ]
    
    for data in deals_data:
        deal = Deal(data)
        DB['deals'][deal.id] = deal.to_dict()
    
    deal_ids = list(DB['deals'].keys())
    
    # Sample Tasks
    tasks_data = [
        {
            'title': 'Follow up with Sarah Johnson',
            'description': 'Send proposal document and schedule demo',
            'type': 'Call', 'priority': 'High', 'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[0], 'deal_id': deal_ids[0],
        },
        {
            'title': 'Send pricing to Michael Chen',
            'description': 'Prepare custom pricing for enterprise features',
            'type': 'Email', 'priority': 'Medium', 'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[1], 'deal_id': deal_ids[1],
        },
        {
            'title': 'Contract review with David Park',
            'description': 'Review final contract terms',
            'type': 'Meeting', 'priority': 'Urgent', 'status': 'pending',
            'due_date': datetime.now().strftime('%Y-%m-%d'),
            'contact_id': contact_ids[3], 'deal_id': deal_ids[2],
        },
        {
            'title': 'Demo for Emily Rodriguez',
            'description': 'Product demo focusing on Shopify integration',
            'type': 'Demo', 'priority': 'High', 'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[2], 'deal_id': deal_ids[3],
        },
        {
            'title': 'Re-engage Lisa Thompson',
            'description': 'Send personalized follow-up email',
            'type': 'Email', 'priority': 'Low', 'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'contact_id': contact_ids[4], 'lead_id': lead_ids[4],
        },
    ]
    
    for data in tasks_data:
        task = Task(data)
        DB['tasks'][task.id] = task.to_dict()
    
    # Sample Activities
    activities_data = [
        {
            'type': 'email', 'title': 'Sent introduction email',
            'description': 'Introduced our platform and key features',
            'contact_id': contact_ids[0],
        },
        {
            'type': 'call', 'title': 'Discovery call completed',
            'description': 'Discussed requirements and timeline',
            'contact_id': contact_ids[0], 'deal_id': deal_ids[0],
        },
        {
            'type': 'meeting', 'title': 'Product demo',
            'description': 'Full platform demonstration',
            'contact_id': contact_ids[3], 'deal_id': deal_ids[2],
        },
        {
            'type': 'note', 'title': 'Budget confirmed',
            'description': 'Customer confirmed Q1 budget allocation',
            'contact_id': contact_ids[0], 'deal_id': deal_ids[0],
        },
    ]
    
    for data in activities_data:
        activity = Activity(data)
        DB['activities'][activity.id] = activity.to_dict()
    
    return True


# ==================== CRUD OPERATIONS ====================

def get_all(collection):
    """Get all items from a collection"""
    return list(DB.get(collection, {}).values())

def get_by_id(collection, item_id):
    """Get item by ID"""
    return DB.get(collection, {}).get(item_id)

def create(collection, data, model_class):
    """Create new item"""
    item = model_class(data)
    DB[collection][item.id] = item.to_dict()
    return item.to_dict()

def update(collection, item_id, data):
    """Update existing item"""
    if item_id in DB.get(collection, {}):
        DB[collection][item_id].update(data)
        DB[collection][item_id]['updated_at'] = datetime.now().isoformat()
        return DB[collection][item_id]
    return None

def delete(collection, item_id):
    """Delete item"""
    if item_id in DB.get(collection, {}):
        del DB[collection][item_id]
        return True
    return False

def search(collection, query, fields):
    """Search items by query in specified fields"""
    results = []
    query = query.lower()
    for item in DB.get(collection, {}).values():
        for field in fields:
            if query in str(item.get(field, '')).lower():
                results.append(item)
                break
    return results


# Initialize sample data on import
init_sample_data()
