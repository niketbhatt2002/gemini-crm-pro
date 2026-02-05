# User Profile & Notification System Guide

## Overview

This guide covers the new enterprise-grade user profile and notification system integrated into GeminiCRM Pro. These features bring Salesforce-level CRM capabilities to track user information, preferences, and real-time notifications.

## 🎯 Features Implemented

### 1. User Profile System
- **Complete User Information**: First name, last name, email, phone
- **Work Information**: Department, job title, team assignment, manager, direct reports
- **User Preferences**: Language, timezone, date/time formats, currency, theme
- **User Status**: Active, away, busy, offline with last seen tracking
- **Performance Statistics**: Total deals, contacts, leads, closed deals, total revenue

### 2. Notification System
- **10 Notification Types**:
  - Deal Updated
  - Lead Scored
  - Task Assigned
  - Task Overdue
  - Email Opened
  - Comment Added
  - Mention
  - Meeting Reminder
  - Deal Stage Change
  - Activity Feed

- **4 Priority Levels**: Low, Normal, High, Urgent
- **Smart Features**:
  - Read/Unread tracking
  - Pin important notifications
  - Auto-expiration (30 days default)
  - Quiet hours support
  - 8 configurable notification preferences

### 3. Activity Logging
- **Audit Trail**: Track all user actions (create, update, delete, view)
- **Change Tracking**: Store old and new values
- **User Context**: IP address and user agent capture
- **Resource History**: View all changes to specific resources

## 📍 Frontend Pages

### Profile Page (`/profile`)

#### Main Sections:
1. **Profile Card** (Left Column)
   - Avatar with user initials
   - Name, title, status badge
   - Contact information
   - Team details
   - Action buttons (change password, logout)

2. **Statistics Cards**
   - Total Deals
   - Closed Deals
   - Total Contacts
   - Total Revenue

3. **Preferences Tabs**
   - **Preferences Tab**: Language, timezone, theme, currency
   - **Notifications Tab**: 8 notification preference toggles
   - **Activity Tab**: User activity timeline

#### Key Functions:
```javascript
loadProfile()              // Load user profile data
editProfile()              // Open edit modal
saveProfileChanges()       // Save profile updates
saveSetting(key, value)    // Save individual settings
updateNotifPref(key, val)  // Update notification preference
loadActivityLog()           // Load user activity history
```

### Notifications Panel

#### Features:
- **Notification Bell Icon**: Shows unread count badge
- **Slide-Out Panel**: Right-side notification drawer
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Three Filter Views**:
  - All notifications
  - Unread only
  - Pinned notifications

#### Notification Actions:
- Mark as read/unread
- Pin/unpin important notifications
- Delete notifications
- Mark all as read
- Clear all notifications

#### Key Functions:
```javascript
toggleNotificationPanel()           // Open/close panel
loadNotifications()                 // Fetch notifications
filterNotifications(filter)         // Filter by view
markNotificationRead(id)            // Mark single read
markAllAsRead()                     // Bulk read
togglePinNotification(id)           // Pin/unpin
deleteNotification(id)              // Delete notification
showToast(message, type)            // Show toast alert
```

## 🔌 API Endpoints

### Profile Endpoints

#### GET /api/profile
Retrieve user profile information
```bash
curl http://localhost:5000/api/profile?user_id=user_1
```

**Response:**
```json
{
  "user_id": "user_1",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "department": "Sales",
  "title": "Sales Manager",
  "team_id": "team_1",
  "status": "active",
  "language": "en",
  "timezone": "America/New_York",
  "theme": "light",
  "currency": "USD",
  "total_deals": 28,
  "closed_deals": 18,
  "total_contacts": 156,
  "total_leads": 42,
  "total_revenue": 1200000,
  "notification_preferences": {
    "email_on_deal_update": true,
    "email_on_task_assign": true,
    "email_on_mention": true,
    "email_on_activity": false,
    "push_enabled": true,
    "sms_enabled": false,
    "quiet_hours_enabled": false,
    "quiet_hours_start": "18:00"
  }
}
```

#### PUT /api/profile
Update user profile
```bash
curl -X PUT http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1","first_name":"John","email":"john@newdomain.com"}'
```

#### GET /api/profile/settings
Get user settings
```bash
curl http://localhost:5000/api/profile/settings?user_id=user_1
```

#### PUT /api/profile/settings
Update user settings
```bash
curl -X PUT http://localhost:5000/api/profile/settings \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1","language":"es","timezone":"Europe/Madrid"}'
```

#### POST /api/profile/status
Update user status
```bash
curl -X POST http://localhost:5000/api/profile/status \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1","status":"away"}'
```

#### GET /api/profile/<user_id>/team
Get team information and statistics
```bash
curl http://localhost:5000/api/profile/user_1/team
```

### Notification Endpoints

#### GET /api/notifications
Fetch user notifications
```bash
# Get all notifications
curl http://localhost:5000/api/notifications?user_id=user_1

# Get only unread
curl http://localhost:5000/api/notifications?user_id=user_1&unread_only=true

# Limit results
curl http://localhost:5000/api/notifications?user_id=user_1&limit=10
```

**Response:**
```json
{
  "notifications": [
    {
      "id": "notif_123",
      "user_id": "user_1",
      "type": "deal_updated",
      "priority": "high",
      "title": "Deal Updated: Acme Corp",
      "message": "Deal value: $50,000 - Stage: Proposal",
      "icon": "🤝",
      "color": "primary",
      "is_read": false,
      "is_pinned": false,
      "created_at": "2024-02-09T10:30:00",
      "expires_at": "2024-03-11T10:30:00"
    }
  ],
  "unread_count": 5
}
```

#### GET /api/notifications/unread-count
Get unread notification count
```bash
curl http://localhost:5000/api/notifications/unread-count?user_id=user_1
```

#### POST /api/notifications/<id>/read
Mark notification as read
```bash
curl -X POST http://localhost:5000/api/notifications/notif_123/read
```

#### POST /api/notifications/mark-all-read
Mark all notifications as read
```bash
curl -X POST http://localhost:5000/api/notifications/mark-all-read?user_id=user_1
```

#### DELETE /api/notifications/<id>
Delete a notification
```bash
curl -X DELETE http://localhost:5000/api/notifications/notif_123
```

#### POST /api/notifications/<id>/pin
Pin or unpin a notification
```bash
curl -X POST http://localhost:5000/api/notifications/notif_123/pin
```

#### GET /api/notifications/preferences
Get notification preferences
```bash
curl http://localhost:5000/api/notifications/preferences?user_id=user_1
```

#### PUT /api/notifications/preferences
Update notification preferences
```bash
curl -X PUT http://localhost:5000/api/notifications/preferences \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1","email_on_deal_update":false,"push_enabled":true}'
```

#### POST /api/notifications/test
Create a test notification (for demo/testing)
```bash
curl -X POST http://localhost:5000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1"}'
```

### Activity Endpoints

#### GET /api/activity/user/<user_id>
Get user's activity log
```bash
curl http://localhost:5000/api/activity/user/user_1?limit=20
```

**Response:**
```json
{
  "activities": [
    {
      "id": "activity_123",
      "user_id": "user_1",
      "action": "update",
      "resource_type": "deal",
      "resource_id": "deal_456",
      "resource_name": "Acme Corp Contract",
      "description": "Updated deal stage from proposal to negotiation",
      "old_values": {"stage": "proposal"},
      "new_values": {"stage": "negotiation"},
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-02-09T10:30:00"
    }
  ]
}
```

#### GET /api/activity/resource/<type>/<id>
Get activity for a specific resource
```bash
# Get all activities on a specific deal
curl http://localhost:5000/api/activity/resource/deal/deal_456
```

## 🔔 Notification Integration Points

Notifications are automatically triggered by these events:

### 1. Lead Scoring
```python
# When a lead is AI scored
POST /api/ai/score-lead
→ Triggers: LEAD_SCORED notification with score and grade
```

### 2. Task Assignment
```python
# When a task is created
POST /api/tasks
→ Triggers: TASK_ASSIGNED notification to assigned user

# When a task is completed
POST /api/tasks/<id>/complete
→ Triggers: TASK_ASSIGNED notification to task creator
```

### 3. Deal Updates
```python
# When a deal is updated
PUT /api/deals/<id>
→ Triggers: DEAL_UPDATED notification

# When a deal stage changes
PUT /api/deals/<id>/stage
→ Triggers: DEAL_STAGE_CHANGE notification
```

## 🎨 Customization

### Notification Types
Edit in `models/user_profile.py`:
```python
class NotificationType(Enum):
    DEAL_UPDATED = "deal_updated"
    LEAD_SCORED = "lead_scored"
    # Add custom types here
```

### Notification Priority
```python
class NotificationPriority(Enum):
    LOW = "low"           # 1
    NORMAL = "normal"     # 2
    HIGH = "high"         # 3
    URGENT = "urgent"     # 4
```

### Creating Custom Notifications
```python
# Use the notify_user helper function
notify_user(
    user_id="user_1",
    notification_type=NotificationType.DEAL_UPDATED.value,
    title="Custom Title",
    message="Custom message",
    priority=NotificationPriority.HIGH.value,
    icon="🎯",
    color="warning",
    data={"key": "value"},
    action_url="/deals/123"
)
```

## 🔐 Security Considerations

1. **User Context**: Always validate user_id in requests
2. **Privacy**: Notifications are user-specific
3. **Expiration**: Notifications auto-expire after 30 days
4. **Activity Logs**: Include IP address for audit trail
5. **Preferences**: Users control notification settings

## 📊 Performance

- **In-Memory Storage**: Notifications stored in memory (production should use database)
- **Auto-Refresh**: Client-side auto-refresh every 30 seconds
- **Pagination**: Limit parameter for efficient loading
- **Filtering**: Server-side filtering for unread notifications

## 🚀 Future Enhancements

1. **Real-time WebSocket**: Replace polling with WebSocket
2. **Email Notifications**: Send notifications via email
3. **Push Notifications**: Browser push notifications
4. **SMS Alerts**: Critical notifications via SMS
5. **Slack Integration**: Send notifications to Slack
6. **Notification Rules**: Custom rules for notification triggering
7. **Batch Operations**: Bulk import/export of notification preferences
8. **Analytics**: Track notification engagement and effectiveness

## 🐛 Troubleshooting

### Profile Not Loading
- Check user_id parameter
- Verify user profile exists in database
- Check browser console for JavaScript errors

### Notifications Not Appearing
- Verify notification preferences are enabled
- Check if quiet hours are active
- Clear browser cache
- Check if notification panel opened

### Missing Activity Logs
- Ensure activity_logger is initialized
- Check if resource actions trigger notifications
- Verify user_id is passed in requests

## 📝 Testing

Test the notification system:
```bash
# Create test notification
curl -X POST http://localhost:5000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_1"}'

# Get all notifications
curl http://localhost:5000/api/notifications?user_id=user_1

# Mark as read
curl -X POST http://localhost:5000/api/notifications/notif_id/read

# Delete notification
curl -X DELETE http://localhost:5000/api/notifications/notif_id
```

---

**Version**: 1.0  
**Last Updated**: February 9, 2024  
**Compatible**: GeminiCRM Pro 2.0+
