"""
GeminiCRM Pro - User Profile & Notification System
Salesforce-level user management with notifications, preferences, and activity tracking
"""
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum


# ==================== NOTIFICATION TYPES ====================

class NotificationType(Enum):
    """All notification types"""
    DEAL_UPDATED = "deal_updated"
    LEAD_SCORED = "lead_scored"
    TASK_ASSIGNED = "task_assigned"
    TASK_OVERDUE = "task_overdue"
    EMAIL_OPENED = "email_opened"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"
    MEETING_REMINDER = "meeting_reminder"
    DEAL_STAGE_CHANGE = "deal_stage_change"
    ACTIVITY_FEED = "activity_feed"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


# ==================== NOTIFICATION MODEL ====================

class Notification:
    """Individual notification"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.user_id = data.get('user_id')
        self.type = data.get('type', NotificationType.ACTIVITY_FEED.value)
        self.priority = data.get('priority', NotificationPriority.NORMAL.value)
        self.title = data.get('title', '')
        self.message = data.get('message', '')
        self.icon = data.get('icon', 'info')
        self.color = data.get('color', 'blue')
        self.data = data.get('data', {})  # Additional context (deal_id, lead_id, etc.)
        self.action_url = data.get('action_url', '')
        self.is_read = data.get('is_read', False)
        self.is_pinned = data.get('is_pinned', False)
        self.read_at = data.get('read_at', None)
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.expires_at = data.get('expires_at', (datetime.now() + timedelta(days=30)).isoformat())
    
    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'icon': self.icon,
            'color': self.color,
            'data': self.data,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'is_pinned': self.is_pinned,
            'read_at': self.read_at,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
        }


# ==================== USER PROFILE MODEL ====================

class UserProfile:
    """Extended user profile with preferences and settings"""
    
    def __init__(self, data):
        self.user_id = data.get('user_id', str(uuid.uuid4()))
        self.first_name = data.get('first_name', '')
        self.last_name = data.get('last_name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.department = data.get('department', 'Sales')
        self.title = data.get('title', 'Sales Representative')
        self.avatar_url = data.get('avatar_url', '')
        self.bio = data.get('bio', '')
        self.language = data.get('language', 'en')
        self.timezone = data.get('timezone', 'UTC')
        self.date_format = data.get('date_format', 'MM/DD/YYYY')
        self.time_format = data.get('time_format', '12h')  # 12h or 24h
        self.currency = data.get('currency', 'USD')
        self.theme = data.get('theme', 'light')  # light, dark, auto
        self.status = data.get('status', 'active')  # active, away, busy, offline
        self.last_seen = data.get('last_seen', datetime.now().isoformat())
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
        
        # Notification preferences
        self.notification_preferences = data.get('notification_preferences', {
            'email_on_deal_update': True,
            'email_on_task_assign': True,
            'email_on_mention': True,
            'email_on_activity': False,
            'push_enabled': True,
            'sms_enabled': False,
            'quiet_hours_enabled': False,
            'quiet_hours_start': '18:00',
            'quiet_hours_end': '09:00',
        })
        
        # Team info
        self.team_id = data.get('team_id', '')
        self.manager_id = data.get('manager_id', '')
        self.direct_reports = data.get('direct_reports', [])
        
        # Statistics
        self.total_deals = data.get('total_deals', 0)
        self.total_contacts = data.get('total_contacts', 0)
        self.total_leads = data.get('total_leads', 0)
        self.closed_deals = data.get('closed_deals', 0)
        self.total_revenue = data.get('total_revenue', 0)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'initials': self.initials,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'title': self.title,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'language': self.language,
            'timezone': self.timezone,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'currency': self.currency,
            'theme': self.theme,
            'status': self.status,
            'last_seen': self.last_seen,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'notification_preferences': self.notification_preferences,
            'team_id': self.team_id,
            'manager_id': self.manager_id,
            'direct_reports': self.direct_reports,
            'total_deals': self.total_deals,
            'total_contacts': self.total_contacts,
            'total_leads': self.total_leads,
            'closed_deals': self.closed_deals,
            'total_revenue': self.total_revenue,
        }


# ==================== NOTIFICATION MANAGER ====================

class NotificationManager:
    """Manage user notifications"""
    
    def __init__(self):
        self.notifications = {}  # user_id -> [notifications]
    
    def create_notification(self, user_id, notification_data):
        """Create and store a new notification"""
        notification = Notification({
            'user_id': user_id,
            **notification_data
        })
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].append(notification)
        return notification
    
    def get_notifications(self, user_id, unread_only=False, limit=20):
        """Get user's notifications"""
        if user_id not in self.notifications:
            return []
        
        notifs = self.notifications[user_id]
        
        if unread_only:
            notifs = [n for n in notifs if not n.is_read]
        
        # Remove expired notifications
        notifs = [n for n in notifs if datetime.fromisoformat(n.expires_at) > datetime.now()]
        
        # Sort by date (newest first)
        notifs = sorted(notifs, key=lambda n: n.created_at, reverse=True)
        
        return notifs[:limit]
    
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        for user_id, notifs in self.notifications.items():
            for notif in notifs:
                if notif.id == notification_id:
                    notif.mark_read()
                    return True
        return False
    
    def mark_all_read(self, user_id):
        """Mark all notifications as read for a user"""
        if user_id in self.notifications:
            for notif in self.notifications[user_id]:
                if not notif.is_read:
                    notif.mark_read()
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        for user_id, notifs in self.notifications.items():
            self.notifications[user_id] = [n for n in notifs if n.id != notification_id]
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications"""
        if user_id not in self.notifications:
            return 0
        return len([n for n in self.notifications[user_id] if not n.is_read])
    
    def pin_notification(self, notification_id):
        """Pin a notification"""
        for user_id, notifs in self.notifications.items():
            for notif in notifs:
                if notif.id == notification_id:
                    notif.is_pinned = True
                    return True
        return False
    
    def unpin_notification(self, notification_id):
        """Unpin a notification"""
        for user_id, notifs in self.notifications.items():
            for notif in notifs:
                if notif.id == notification_id:
                    notif.is_pinned = False
                    return True
        return False


# ==================== USER PROFILE MANAGER ====================

class UserProfileManager:
    """Manage user profiles"""
    
    def __init__(self):
        self.profiles = {}  # user_id -> UserProfile
    
    def create_profile(self, user_id, profile_data):
        """Create a new user profile"""
        profile = UserProfile({
            'user_id': user_id,
            **profile_data
        })
        self.profiles[user_id] = profile
        return profile
    
    def get_profile(self, user_id):
        """Get user profile"""
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id, updates):
        """Update user profile"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now().isoformat()
        return profile
    
    def update_notification_preferences(self, user_id, preferences):
        """Update notification preferences"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        profile.notification_preferences.update(preferences)
        profile.updated_at = datetime.now().isoformat()
        return profile
    
    def set_status(self, user_id, status):
        """Set user status (active, away, busy, offline)"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        profile.status = status
        profile.last_seen = datetime.now().isoformat()
        return profile
    
    def get_team_members(self, team_id):
        """Get all members of a team"""
        return [p for p in self.profiles.values() if p.team_id == team_id]
    
    def get_team_statistics(self, team_id):
        """Get aggregated statistics for a team"""
        members = self.get_team_members(team_id)
        
        return {
            'member_count': len(members),
            'total_deals': sum(m.total_deals for m in members),
            'total_contacts': sum(m.total_contacts for m in members),
            'total_leads': sum(m.total_leads for m in members),
            'closed_deals': sum(m.closed_deals for m in members),
            'total_revenue': sum(m.total_revenue for m in members),
        }


# ==================== ACTIVITY LOG ====================

class ActivityLog:
    """Log user activities"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.user_id = data.get('user_id')
        self.action = data.get('action', '')  # 'create', 'update', 'delete', 'view'
        self.resource_type = data.get('resource_type', '')  # 'lead', 'deal', 'contact', etc.
        self.resource_id = data.get('resource_id', '')
        self.resource_name = data.get('resource_name', '')
        self.description = data.get('description', '')
        self.old_values = data.get('old_values', {})
        self.new_values = data.get('new_values', {})
        self.ip_address = data.get('ip_address', '')
        self.user_agent = data.get('user_agent', '')
        self.created_at = data.get('created_at', datetime.now().isoformat())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'description': self.description,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at,
        }


class ActivityLogger:
    """Manage activity logs"""
    
    def __init__(self):
        self.logs = {}  # user_id -> [logs]
    
    def log_activity(self, user_id, activity_data):
        """Log an activity"""
        log = ActivityLog({
            'user_id': user_id,
            **activity_data
        })
        
        if user_id not in self.logs:
            self.logs[user_id] = []
        
        self.logs[user_id].append(log)
        return log
    
    def get_user_activity(self, user_id, limit=50):
        """Get user's activity log"""
        if user_id not in self.logs:
            return []
        
        logs = sorted(self.logs[user_id], key=lambda l: l.created_at, reverse=True)
        return logs[:limit]
    
    def get_activity_for_resource(self, resource_type, resource_id):
        """Get all activities for a specific resource"""
        activities = []
        for logs in self.logs.values():
            activities.extend([
                l for l in logs 
                if l.resource_type == resource_type and l.resource_id == resource_id
            ])
        
        return sorted(activities, key=lambda a: a.created_at, reverse=True)


# ==================== GLOBAL MANAGERS ====================

# Initialize global managers
notification_manager = NotificationManager()
profile_manager = UserProfileManager()
activity_logger = ActivityLogger()


# ==================== INITIALIZATION ====================

def init_default_user_profile(user_id='user_1'):
    """Create default user profile"""
    profile = profile_manager.create_profile(user_id, {
        'first_name': 'John',
        'last_name': 'Sales',
        'email': 'john@geminicrm.com',
        'phone': '+1-555-0100',
        'department': 'Sales',
        'title': 'Sales Manager',
        'team_id': 'team_1',
    })
    return profile
