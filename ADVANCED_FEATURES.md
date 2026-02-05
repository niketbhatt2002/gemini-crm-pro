# 🚀 GeminiCRM Pro - Advanced Features Guide

## Overview

This guide covers the advanced features and enhancements added to GeminiCRM Pro, taking it to the next level with enterprise-grade capabilities.

---

## 📋 Table of Contents

1. [Authentication & User Management](#authentication--user-management)
2. [Advanced Analytics](#advanced-analytics)
3. [Email Integration](#email-integration)
4. [API Monitoring & Rate Limiting](#api-monitoring--rate-limiting)
5. [Webhook System](#webhook-system)
6. [Data Import/Export](#dataimportexport)
7. [Audit Logging](#audit-logging)
8. [Role-Based Access Control](#role-based-access-control)

---

## Authentication & User Management

### Features

- **JWT-based Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: 4 predefined roles with permission levels
- **Multi-Tenant Ready**: User isolation and data segregation
- **Password Management**: Secure password hashing with SHA256
- **Session Management**: Track user sessions and login activity
- **MFA Support**: Framework for multi-factor authentication

### Roles & Permissions

```python
ROLES = {
    'admin': ['create', 'read', 'update', 'delete', 'manage_users', 'analytics'],
    'manager': ['create', 'read', 'update', 'delete', 'analytics'],
    'sales': ['create', 'read', 'update', 'analytics'],
    'viewer': ['read', 'analytics']
}
```

### Usage Example

```python
from models.auth import authenticate_user, create_user, token_required

# Create new user
user_data = {
    'email': 'john@company.com',
    'password': 'secure_password',
    'first_name': 'John',
    'last_name': 'Doe',
    'role': 'sales'
}
user, error = create_user(user_data)

# Authenticate
tokens, error = authenticate_user('john@company.com', 'secure_password')

# Protected endpoints
@app.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def list_all_users():
    users = get_all_users()
    return jsonify(users)
```

### Decorators

```python
@token_required  # Requires valid JWT token
def protected_endpoint():
    pass

@permission_required('create')  # Requires specific permission
def create_resource():
    pass

@role_required('admin')  # Requires specific role
def admin_endpoint():
    pass
```

---

## Advanced Analytics

### Features

- **Lead Metrics**: Comprehensive lead scoring and analysis
- **Deal Analytics**: Pipeline analysis, forecasting, and probability tracking
- **Sales Metrics**: Team and individual performance tracking
- **Custom Reports**: Executive summaries and detailed breakdowns
- **Sales Forecasting**: 30/90-day forecasting with confidence levels
- **Pipeline Analysis**: Stage-by-stage breakdown with metrics

### Key Classes

#### AnalyticsEngine

```python
from services.analytics_service import AnalyticsEngine

engine = AnalyticsEngine()

# Lead metrics
lead_metrics = engine.calculate_lead_metrics(leads)
# Returns: total_leads, avg_score, high_quality_leads, by_source, by_status, conversion_rate

# Deal metrics
deal_metrics = engine.calculate_deal_metrics(deals)
# Returns: total_deals, pipeline_value, win_rate, deal breakdown

# Pipeline analysis
pipeline = engine.get_pipeline_analysis(deals)
# Returns: detailed stage-by-stage breakdown

# Forecasting
forecast = engine.get_forecast(deals, period_days=30)
# Returns: forecasted revenue, confidence level
```

#### ReportGenerator

```python
from services.analytics_service import ReportGenerator

# Executive summary
summary = ReportGenerator.generate_executive_summary(contacts, leads, deals, tasks)

# Lead report
lead_report = ReportGenerator.generate_lead_report(leads)

# Sales forecast
forecast_report = ReportGenerator.generate_sales_forecast(deals, period_days=90)
```

### Usage Examples

```python
# Get comprehensive analytics
analytics = AnalyticsEngine()
metrics = {
    'leads': analytics.calculate_lead_metrics(all_leads),
    'deals': analytics.calculate_deal_metrics(all_deals),
    'pipeline': analytics.get_pipeline_analysis(all_deals),
    'forecast': analytics.get_forecast(all_deals, 30)
}

# Generate reports
report = ReportGenerator.generate_executive_summary(
    contacts, leads, deals, tasks
)

# Export data
from services.analytics_service import ExportManager
csv_data = ExportManager.export_to_csv(leads, ['id', 'name', 'score'])
json_data = ExportManager.export_to_json(leads)
```

---

## Email Integration

### Features

- **Email Templates**: Pre-built and custom templates
- **Email Campaigns**: Bulk email sending with tracking
- **Template Rendering**: Dynamic content interpolation
- **Campaign Analytics**: Open/click tracking
- **Email Status Tracking**: Delivery status monitoring
- **Template Management**: Full CRUD operations

### Email Templates

```python
from services.email_service import EmailService

service = EmailService()

# Built-in templates
templates = service.list_templates()

# Create custom template
template = service.create_template({
    'name': 'Monthly Newsletter',
    'subject': 'Your {company_name} Newsletter - {month}',
    'body': 'Hi {first_name},\n\nCheck out this month\'s updates...'
})

# Render template with context
rendered = template.render({
    'company_name': 'Acme Corp',
    'first_name': 'John',
    'month': 'February'
})
```

### Email Campaigns

```python
# Create campaign
campaign = service.create_campaign({
    'name': 'Q1 Outreach',
    'template_id': template_id,
    'recipient_ids': [lead_1, lead_2, lead_3],
    'created_by': user_id
})

# Send campaign
success, message = service.send_campaign(campaign_id)

# Track engagement
service.track_email_open(message_id)
service.track_email_click(message_id)

# Get stats
stats = service.get_campaign_stats(campaign_id)
# Returns: total_sent, opened, clicked, bounced, open_rate, click_rate
```

### Campaign Statistics

```python
{
    'total_sent': 100,
    'opened': 45,
    'clicked': 12,
    'bounced': 2,
    'failed': 1,
    'open_rate': '45.0%',
    'click_rate': '12.0%'
}
```

---

## API Monitoring & Rate Limiting

### Features

- **Rate Limiting**: Per-minute, per-hour, per-day limits
- **API Monitoring**: Request logging and performance tracking
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time analysis (avg, p95, min, max)
- **API Key Management**: Secure API key generation and management
- **Health Monitoring**: Real-time API health status

### Rate Limiting

```python
from services.api_monitoring import RateLimiter

limiter = RateLimiter()

# Check rate limit
allowed, message = limiter.check_rate_limit(user_id)

# Record request
limiter.record_request(user_id)

# Get usage stats
usage = limiter.get_usage(user_id)
# Returns: minute, hour, day usage counts and limits
```

### API Monitoring

```python
from services.api_monitoring import APIMonitor

monitor = APIMonitor()

# Log request
monitor.log_request(user_id, '/api/leads', 'GET', 200, 45.2)

# Log error
monitor.log_error(user_id, '/api/leads', 'POST', 'Validation error')

# Get stats
stats = monitor.get_endpoint_stats('/api/leads')
# Returns: avg response time, p95, min, max

# Health check
health = monitor.get_health_status()
# Returns: status, error_rate, total requests

# Top endpoints
top = monitor.get_top_endpoints(10)

# Error rates by endpoint
errors = monitor.get_error_rate_by_endpoint()
```

### API Key Management

```python
from services.api_monitoring import APIKeyManager

key_manager = APIKeyManager()

# Create API key
api_key = key_manager.create_key(user_id, 'Production Key', expires_in_days=365)

# Validate key
valid, user_id_or_error = key_manager.validate_key(api_key_string)

# Revoke key
key_manager.revoke_key(api_key_string)

# Get user keys
keys = key_manager.get_user_keys(user_id)
```

### Configuration

```python
limiter.config = {
    'requests_per_minute': 60,
    'requests_per_hour': 1000,
    'requests_per_day': 10000
}
```

---

## Webhook System

### Features

- **Event-Based Webhooks**: Trigger on specific events
- **Event Logging**: Complete webhook event history
- **Webhook Management**: Register, update, delete webhooks
- **Retry Mechanism**: Framework for retry logic
- **Secret-Based Validation**: Secure webhook validation

### Events Supported

- `lead_created` - New lead created
- `lead_updated` - Lead updated
- `deal_won` - Deal won
- `deal_lost` - Deal lost
- `contact_created` - New contact
- `task_completed` - Task marked complete
- `campaign_sent` - Email campaign sent

### Usage

```python
from services.email_service import WebhookManager

webhooks = WebhookManager()

# Register webhook
webhook = webhooks.register_webhook({
    'url': 'https://your-app.com/webhooks/deals',
    'event_type': 'deal_won',
    'secret': 'webhook_secret_123'
})

# Trigger webhook
triggered_ids = webhooks.trigger_webhook('deal_won', {
    'deal_id': deal_id,
    'deal_value': 50000,
    'probability': 95
})

# Get webhook
webhook_data = webhooks.get_webhook(webhook_id)

# List all webhooks
all_webhooks = webhooks.list_webhooks()

# Delete webhook
webhooks.delete_webhook(webhook_id)
```

---

## Data Import/Export

### Features

- **Multiple Formats**: CSV, JSON, Excel support
- **Data Validation**: Schema validation during import
- **Batch Operations**: Import/export thousands of records
- **Error Reporting**: Detailed error messages
- **Field Mapping**: Flexible field mapping

### Export

```python
from services.analytics_service import ExportManager

# Export to CSV
csv_data = ExportManager.export_to_csv(leads, ['id', 'name', 'email', 'score'])

# Export to JSON
json_data = ExportManager.export_to_json(leads)

# Export to Excel
filename = ExportManager.export_to_excel(leads, 'leads_export.xlsx')
```

### Import

```python
from services.analytics_service import ImportManager

# Import from CSV
data = ImportManager.import_from_csv(csv_file_content)

# Import from JSON
data = ImportManager.import_from_json(json_file_content)

# Validate schema
schema = {
    'email': 'email',
    'name': 'string',
    'value': 'number'
}
errors = ImportManager.validate_import_data(data, schema)

if errors:
    print("Import errors:", errors)
else:
    # Process import
    for row in data:
        create_lead(row)
```

---

## Audit Logging

### Features

- **Complete Audit Trail**: Every action logged with context
- **User Activity Tracking**: Who did what and when
- **Resource History**: Track all changes to resources
- **Compliance Ready**: Detailed logging for audits
- **Searchable Logs**: Query logs by user, resource, action

### Usage

```python
from services.api_monitoring import AuditLog

audit = AuditLog()

# Log action
audit.log_action(
    user_id='user_123',
    action='create',
    resource_type='lead',
    resource_id='lead_456',
    changes={'name': 'John Doe', 'email': 'john@example.com'},
    status='success'
)

# Get user activity
activity = audit.get_user_activity('user_123', limit=100)

# Get resource history
history = audit.get_resource_history('lead', 'lead_456')

# Get all logs
logs = audit.get_all_logs(limit=1000)
```

---

## Role-Based Access Control (RBAC)

### Role Hierarchy

```
admin (Full Access)
├── All permissions
└── Manage users

manager (Senior Access)
├── create, read, update, delete
├── analytics
└── Team management

sales (Standard Access)
├── create, read, update
└── analytics

viewer (Read-Only)
└── read, analytics
```

### Permission Matrix

| Permission | Admin | Manager | Sales | Viewer |
|-----------|-------|---------|-------|--------|
| create    | ✅    | ✅      | ✅    | ❌     |
| read      | ✅    | ✅      | ✅    | ✅     |
| update    | ✅    | ✅      | ✅    | ❌     |
| delete    | ✅    | ✅      | ❌    | ❌     |
| analytics | ✅    | ✅      | ✅    | ✅     |
| manage_users | ✅ | ❌      | ❌    | ❌     |

### Implementation

```python
# Check permission
if user.has_permission('create'):
    create_lead(lead_data)

# Decorator
@permission_required('delete')
def delete_lead(lead_id):
    # Delete lead
    pass

# Role check
if user.role == 'admin':
    manage_system()
```

---

## Integration Points

### With Existing CRM Features

1. **Authentication** integrates with:
   - Dashboard (user context)
   - Lead/Deal management (owner tracking)
   - Email campaigns (sender identification)

2. **Analytics** provides:
   - Dashboard widgets
   - Report endpoints
   - Export functionality

3. **Email Service** connects to:
   - Gemini AI (email generation)
   - Leads/Contacts (recipient data)
   - Tasks (follow-up tracking)

4. **Monitoring** tracks:
   - All API endpoints
   - User actions (audit log)
   - System health

---

## Best Practices

### Security

1. **Always validate** JWT tokens before processing
2. **Use HTTPS** in production for all API calls
3. **Rotate API keys** regularly (monthly)
4. **Enable MFA** for admin users
5. **Audit sensitive** operations

### Performance

1. **Cache** frequently accessed data
2. **Use rate limiting** to prevent abuse
3. **Index** database queries
4. **Monitor** endpoint performance
5. **Archive** old audit logs

### Data Management

1. **Backup** regularly (daily)
2. **Validate** imported data
3. **Track** data changes
4. **Purge** old logs periodically
5. **Encrypt** sensitive data

---

## Migration from Basic to Advanced

### Step 1: Authentication Setup
```python
from models.auth import init_default_users
init_default_users()  # Creates admin, manager, sales users
```

### Step 2: Enable Rate Limiting
```python
from services.api_monitoring import RateLimiter
limiter = RateLimiter()
# Apply to all routes
```

### Step 3: Add Monitoring
```python
from services.api_monitoring import APIMonitor
monitor = APIMonitor()
# Log all requests
```

### Step 4: Email Integration
```python
from services.email_service import EmailService
email_service = EmailService()
# Enable email campaigns
```

### Step 5: Analytics Enablement
```python
from services.analytics_service import AnalyticsEngine
analytics = AnalyticsEngine()
# Generate reports
```

---

## API Endpoints (To Be Added)

```
Authentication:
POST   /api/auth/register        - Register new user
POST   /api/auth/login           - Login user
POST   /api/auth/refresh         - Refresh token
POST   /api/auth/logout          - Logout user
POST   /api/auth/change-password - Change password

Users:
GET    /api/users                - List users (admin only)
GET    /api/users/{id}           - Get user details
PUT    /api/users/{id}           - Update user
DELETE /api/users/{id}           - Delete user (admin only)

Analytics:
GET    /api/analytics/dashboard  - Executive summary
GET    /api/analytics/leads      - Lead analytics
GET    /api/analytics/deals      - Deal analytics
GET    /api/analytics/forecast   - Sales forecast
GET    /api/analytics/team       - Team performance

Email:
GET    /api/email/templates      - List templates
POST   /api/email/templates      - Create template
POST   /api/email/campaigns      - Create campaign
POST   /api/email/campaigns/{id}/send - Send campaign
GET    /api/email/campaigns/{id}/stats - Campaign stats

Monitoring:
GET    /api/monitoring/health    - Health status
GET    /api/monitoring/stats     - Performance stats
GET    /api/monitoring/errors    - Error report
GET    /api/monitoring/usage     - API usage

Webhooks:
POST   /api/webhooks             - Register webhook
GET    /api/webhooks             - List webhooks
DELETE /api/webhooks/{id}        - Delete webhook

Export:
POST   /api/export/csv           - Export to CSV
POST   /api/export/json          - Export to JSON
POST   /api/export/excel         - Export to Excel

Import:
POST   /api/import/csv           - Import from CSV
POST   /api/import/json          - Import from JSON
```

---

## Future Enhancements

1. **Advanced Segmentation**: AI-powered lead segmentation
2. **Predictive Analytics**: ML-based sales forecasting
3. **Real-time Notifications**: WebSocket-based updates
4. **Mobile App**: Native iOS/Android app
5. **Advanced Search**: Full-text search and faceted navigation
6. **Custom Fields**: Dynamic custom field support
7. **Multi-Language**: I18n support
8. **Custom Workflows**: Workflow automation engine
9. **API Marketplace**: Third-party integrations
10. **Enterprise SSO**: SAML/OAuth2 support

---

## Support & Troubleshooting

For issues with advanced features:
1. Check audit logs for error details
2. Review API monitoring for performance issues
3. Validate authentication and permissions
4. Check rate limit status
5. Review webhook event logs

---

**Created**: February 4, 2026
**Version**: 2.0 (Advanced)
**Status**: Ready for Enterprise Deployment
