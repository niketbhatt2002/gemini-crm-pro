"""
GeminiCRM Pro - Email Integration & Campaign Management
Email sending, templates, and campaign tracking
"""
from datetime import datetime
import uuid
from enum import Enum

# ==================== EMAIL TEMPLATES ====================

class EmailTemplate:
    """Email template model"""
    
    TEMPLATES = {
        'welcome': {
            'subject': 'Welcome to {company_name}!',
            'body': '''Hi {first_name},

Welcome to {company_name}! We're excited to have you on board.

Best regards,
{sender_name}'''
        },
        'follow_up': {
            'subject': 'Following up on {opportunity}',
            'body': '''Hi {first_name},

I wanted to follow up on our conversation about {opportunity}.

Would you be available for a quick call this week?

Best regards,
{sender_name}'''
        },
        'proposal': {
            'subject': 'Your Customized Proposal',
            'body': '''Hi {first_name},

I've prepared a customized proposal for {opportunity}.

Please find it attached. Let me know if you have any questions!

Best regards,
{sender_name}'''
        },
        'closing': {
            'subject': 'Let\'s finalize {opportunity}',
            'body': '''Hi {first_name},

I believe we're ready to move forward with {opportunity}.

Let me know your thoughts on the proposed terms.

Best regards,
{sender_name}'''
        }
    }
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name')
        self.subject = data.get('subject')
        self.body = data.get('body')
        self.category = data.get('category', 'custom')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    def render(self, context):
        """Render template with context variables"""
        subject = self.subject
        body = self.body
        
        for key, value in context.items():
            subject = subject.replace(f'{{{key}}}', str(value))
            body = body.replace(f'{{{key}}}', str(value))
        
        return {'subject': subject, 'body': body}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'category': self.category,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

# ==================== EMAIL CAMPAIGN ====================

class EmailCampaign:
    """Email campaign model"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.name = data.get('name')
        self.template_id = data.get('template_id')
        self.recipient_ids = data.get('recipient_ids', [])
        self.status = data.get('status', 'draft')  # draft, scheduled, sent, paused
        self.scheduled_at = data.get('scheduled_at')
        self.sent_at = data.get('sent_at')
        self.created_by = data.get('created_by')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
        self.stats = data.get('stats', {
            'total_sent': 0,
            'opened': 0,
            'clicked': 0,
            'bounced': 0,
            'failed': 0
        })
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_id': self.template_id,
            'recipient_count': len(self.recipient_ids),
            'status': self.status,
            'scheduled_at': self.scheduled_at,
            'sent_at': self.sent_at,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'stats': self.stats,
            'open_rate': f"{(self.stats.get('opened', 0) / max(self.stats.get('total_sent', 1), 1) * 100):.1f}%"
        }

# ==================== EMAIL MESSAGE ====================

class EmailMessage:
    """Individual email message"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.recipient_email = data.get('recipient_email')
        self.recipient_id = data.get('recipient_id')
        self.subject = data.get('subject')
        self.body = data.get('body')
        self.html_body = data.get('html_body')
        self.sender_id = data.get('sender_id')
        self.campaign_id = data.get('campaign_id')
        self.status = data.get('status', 'pending')  # pending, sent, opened, clicked, bounced, failed
        self.sent_at = data.get('sent_at')
        self.opened_at = data.get('opened_at')
        self.clicked_at = data.get('clicked_at')
        self.error = data.get('error')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_email': self.recipient_email,
            'recipient_id': self.recipient_id,
            'subject': self.subject,
            'status': self.status,
            'campaign_id': self.campaign_id,
            'sender_id': self.sender_id,
            'sent_at': self.sent_at,
            'opened_at': self.opened_at,
            'clicked_at': self.clicked_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

# ==================== EMAIL SERVICE ====================

class EmailService:
    """Email service with template and campaign support"""
    
    def __init__(self):
        self.templates = {}
        self.campaigns = {}
        self.messages = {}
        self._init_default_templates()
    
    def _init_default_templates(self):
        """Initialize default email templates"""
        for name, content in EmailTemplate.TEMPLATES.items():
            template = EmailTemplate({
                'name': name,
                'subject': content['subject'],
                'body': content['body'],
                'category': 'system'
            })
            self.templates[template.id] = template.to_dict()
    
    def create_template(self, data):
        """Create email template"""
        template = EmailTemplate(data)
        self.templates[template.id] = template.to_dict()
        return template.to_dict()
    
    def get_template(self, template_id):
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self):
        """List all templates"""
        return list(self.templates.values())
    
    def update_template(self, template_id, data):
        """Update template"""
        if template_id not in self.templates:
            return None
        
        template_data = self.templates[template_id]
        template_data.update(data)
        template_data['updated_at'] = datetime.now().isoformat()
        
        return template_data
    
    def delete_template(self, template_id):
        """Delete template"""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False
    
    def create_campaign(self, data):
        """Create email campaign"""
        campaign = EmailCampaign(data)
        self.campaigns[campaign.id] = campaign.to_dict()
        return campaign.to_dict()
    
    def get_campaign(self, campaign_id):
        """Get campaign by ID"""
        return self.campaigns.get(campaign_id)
    
    def list_campaigns(self):
        """List all campaigns"""
        return list(self.campaigns.values())
    
    def update_campaign(self, campaign_id, data):
        """Update campaign"""
        if campaign_id not in self.campaigns:
            return None
        
        campaign_data = self.campaigns[campaign_id]
        allowed_fields = ['name', 'status', 'scheduled_at']
        
        for field in allowed_fields:
            if field in data:
                campaign_data[field] = data[field]
        
        campaign_data['updated_at'] = datetime.now().isoformat()
        return campaign_data
    
    def send_campaign(self, campaign_id, dry_run=False):
        """Send campaign to all recipients"""
        if campaign_id not in self.campaigns:
            return False, 'Campaign not found'
        
        campaign = self.campaigns[campaign_id]
        template = self.templates.get(campaign['template_id'])
        
        if not template:
            return False, 'Template not found'
        
        messages_sent = 0
        
        for recipient_id in campaign.get('recipient_ids', []):
            if not dry_run:
                message = EmailMessage({
                    'recipient_id': recipient_id,
                    'subject': template['subject'],
                    'body': template['body'],
                    'sender_id': campaign['created_by'],
                    'campaign_id': campaign_id,
                    'status': 'sent'
                })
                self.messages[message.id] = message.to_dict()
                messages_sent += 1
            else:
                messages_sent += 1
        
        campaign['status'] = 'sent'
        campaign['sent_at'] = datetime.now().isoformat()
        campaign['stats']['total_sent'] = messages_sent
        
        return True, f'{messages_sent} emails scheduled'
    
    def get_campaign_stats(self, campaign_id):
        """Get campaign statistics"""
        if campaign_id not in self.campaigns:
            return None
        
        campaign = self.campaigns[campaign_id]
        campaign_messages = [m for m in self.messages.values() if m.get('campaign_id') == campaign_id]
        
        stats = {
            'total_sent': len(campaign_messages),
            'opened': len([m for m in campaign_messages if m.get('status') == 'opened']),
            'clicked': len([m for m in campaign_messages if m.get('status') == 'clicked']),
            'bounced': len([m for m in campaign_messages if m.get('status') == 'bounced']),
            'failed': len([m for m in campaign_messages if m.get('status') == 'failed'])
        }
        
        total = stats['total_sent']
        stats['open_rate'] = f"{(stats['opened'] / total * 100):.1f}%" if total > 0 else "0%"
        stats['click_rate'] = f"{(stats['clicked'] / total * 100):.1f}%" if total > 0 else "0%"
        
        return stats
    
    def track_email_open(self, message_id):
        """Track email open"""
        if message_id in self.messages:
            message = self.messages[message_id]
            if message['status'] == 'sent':
                message['status'] = 'opened'
                message['opened_at'] = datetime.now().isoformat()
                return True
        return False
    
    def track_email_click(self, message_id):
        """Track email click"""
        if message_id in self.messages:
            message = self.messages[message_id]
            if message['status'] in ['sent', 'opened']:
                message['status'] = 'clicked'
                message['clicked_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_message(self, message_id):
        """Get message by ID"""
        return self.messages.get(message_id)
    
    def list_campaign_messages(self, campaign_id):
        """List messages for campaign"""
        return [m for m in self.messages.values() if m.get('campaign_id') == campaign_id]

# ==================== WEBHOOK SYSTEM ====================

class Webhook:
    """Webhook model for notifications"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.url = data.get('url')
        self.event_type = data.get('event_type')  # lead_created, deal_won, etc.
        self.is_active = data.get('is_active', True)
        self.secret = data.get('secret', str(uuid.uuid4()))
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.last_triggered = data.get('last_triggered')
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'event_type': self.event_type,
            'is_active': self.is_active,
            'secret': self.secret,
            'created_at': self.created_at,
            'last_triggered': self.last_triggered
        }

class WebhookManager:
    """Manage webhooks"""
    
    def __init__(self):
        self.webhooks = {}
        self.event_log = []
    
    def register_webhook(self, data):
        """Register new webhook"""
        webhook = Webhook(data)
        self.webhooks[webhook.id] = webhook.to_dict()
        return webhook.to_dict()
    
    def trigger_webhook(self, event_type, payload):
        """Trigger webhooks for event"""
        triggered = []
        
        for webhook_id, webhook in self.webhooks.items():
            if webhook.get('event_type') == event_type and webhook.get('is_active'):
                self.event_log.append({
                    'webhook_id': webhook_id,
                    'event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'payload': payload
                })
                triggered.append(webhook_id)
                webhook['last_triggered'] = datetime.now().isoformat()
        
        return triggered
    
    def get_webhook(self, webhook_id):
        """Get webhook by ID"""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self):
        """List all webhooks"""
        return list(self.webhooks.values())
    
    def delete_webhook(self, webhook_id):
        """Delete webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False
