# 🔌 GeminiCRM Pro - API Integration & Extensions Guide

## Overview

Comprehensive guide for integrating third-party services and building extensions for GeminiCRM Pro.

---

## Table of Contents

1. [Third-Party Integrations](#third-party-integrations)
2. [Custom Extensions](#custom-extensions)
3. [Webhook System](#webhook-system)
4. [OAuth2 Integration](#oauth2-integration)
5. [External APIs](#external-apis)
6. [Marketplace](#marketplace)

---

## Third-Party Integrations

### Email Service Integration

#### SendGrid

```python
# integrations/sendgrid_integration.py
import sendgrid
from sendgrid.helpers.mail import Mail

class SendGridIntegration:
    def __init__(self, api_key):
        self.sg = sendgrid.SendGridAPIClient(api_key)
    
    def send_email(self, to_email, subject, html_content, from_email='noreply@gemini-crm.com'):
        """Send email via SendGrid"""
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def track_opens(self, message_id):
        """Track email opens"""
        # Implementation with SendGrid webhook
        pass
```

#### Gmail API

```python
# integrations/gmail_integration.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailIntegration:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_file):
        self.service = build('gmail', 'v1', credentials=self.get_credentials(credentials_file))
    
    def get_credentials(self, credentials_file):
        """Get Gmail API credentials"""
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
    
    def send_email(self, to_email, subject, message_text):
        """Send email via Gmail API"""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            return {'success': True, 'message_id': message['id']}
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

### Calendar Integration

#### Google Calendar

```python
# integrations/google_calendar_integration.py
from datetime import datetime, timedelta
from googleapiclient.discovery import build

class GoogleCalendarIntegration:
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def create_event(self, calendar_id='primary', event_data=None):
        """Create calendar event"""
        event = {
            'summary': event_data.get('title'),
            'description': event_data.get('description'),
            'start': {
                'dateTime': event_data.get('start_time'),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_data.get('end_time'),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in event_data.get('attendees', [])],
        }
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            return {'success': True, 'event_id': event['id']}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_events(self, calendar_id='primary', max_results=10):
        """List calendar events"""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as e:
            return []
```

### SMS Integration

#### Twilio

```python
# integrations/twilio_integration.py
from twilio.rest import Client

class TwilioIntegration:
    def __init__(self, account_sid, auth_token, phone_number):
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
    
    def send_sms(self, to_number, message):
        """Send SMS"""
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            return {'success': True, 'message_id': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_whatsapp(self, to_number, message):
        """Send WhatsApp message"""
        try:
            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.phone_number}',
                to=f'whatsapp:{to_number}'
            )
            return {'success': True, 'message_id': message.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

### Payment Integration

#### Stripe

```python
# integrations/stripe_integration.py
import stripe

class StripeIntegration:
    def __init__(self, api_key):
        stripe.api_key = api_key
    
    def create_payment(self, amount, currency='usd', customer_email=None):
        """Create payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                receipt_email=customer_email
            )
            return {'success': True, 'client_secret': intent.client_secret}
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': intent.status == 'succeeded',
                'status': intent.status,
                'amount': intent.amount / 100
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

---

## Custom Extensions

### Extension Structure

```
extensions/
├── extension_base.py
├── my_extension/
│   ├── __init__.py
│   ├── manifest.json
│   ├── extension.py
│   ├── routes.py
│   └── static/
│       ├── js/
│       └── css/
```

### Base Extension Class

```python
# extensions/extension_base.py
from abc import ABC, abstractmethod

class ExtensionBase(ABC):
    """Base class for all extensions"""
    
    def __init__(self, app):
        self.app = app
        self.config = {}
    
    @abstractmethod
    def install(self):
        """Called when extension is installed"""
        pass
    
    @abstractmethod
    def uninstall(self):
        """Called when extension is uninstalled"""
        pass
    
    @abstractmethod
    def get_routes(self):
        """Return extension routes"""
        pass
    
    def get_config(self):
        """Get extension configuration"""
        return self.config
    
    def set_config(self, config):
        """Set extension configuration"""
        self.config = config
```

### Example Extension

```python
# extensions/my_extension/extension.py
from extensions.extension_base import ExtensionBase
from flask import Blueprint

class MyExtension(ExtensionBase):
    """Example custom extension"""
    
    def install(self):
        """Install extension"""
        print("Installing MyExtension...")
        # Create tables, initialize data, etc.
        return {'success': True, 'message': 'Extension installed'}
    
    def uninstall(self):
        """Uninstall extension"""
        print("Uninstalling MyExtension...")
        # Clean up tables, remove data, etc.
        return {'success': True, 'message': 'Extension uninstalled'}
    
    def get_routes(self):
        """Return extension routes"""
        bp = Blueprint('my_extension', __name__, url_prefix='/api/extensions/my-extension')
        
        @bp.route('/health', methods=['GET'])
        def health():
            return {'status': 'ok'}
        
        @bp.route('/custom-feature', methods=['POST'])
        def custom_feature():
            # Custom logic here
            return {'result': 'success'}
        
        return bp
```

### Manifest File

```json
{
  "id": "my-extension",
  "name": "My Custom Extension",
  "version": "1.0.0",
  "description": "A custom extension for GeminiCRM Pro",
  "author": "Your Company",
  "license": "MIT",
  "permissions": [
    "read:leads",
    "write:leads",
    "read:contacts",
    "write:contacts"
  ],
  "entry_point": "extension.py",
  "icon": "icon.png",
  "settings": [
    {
      "id": "api_key",
      "type": "password",
      "label": "API Key",
      "description": "Your API key"
    }
  ]
}
```

---

## Webhook System

### Webhook Registration

```python
# integrations/webhook_manager.py
class WebhookManager:
    """Manage outgoing webhooks"""
    
    def register_webhook(self, event_type, url, secret):
        """Register webhook for event"""
        webhook = {
            'id': str(uuid.uuid4()),
            'event_type': event_type,
            'url': url,
            'secret': secret,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store in database
        return webhook
    
    def trigger_webhook(self, event_type, payload):
        """Trigger webhook for event"""
        import hmac
        import hashlib
        import requests
        
        webhooks = self.get_webhooks_for_event(event_type)
        
        for webhook in webhooks:
            # Create signature
            signature = hmac.new(
                webhook['secret'].encode(),
                str(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Send webhook
            try:
                requests.post(
                    webhook['url'],
                    json=payload,
                    headers={
                        'X-Webhook-Signature': signature,
                        'X-Webhook-Event': event_type
                    },
                    timeout=30
                )
            except Exception as e:
                print(f"Webhook delivery failed: {e}")
```

### Webhook Events

```python
# Trigger webhook when events occur
from integrations.webhook_manager import WebhookManager

webhook_manager = WebhookManager()

# When lead is created
@app.route('/api/leads', methods=['POST'])
def create_lead():
    lead = create_lead_in_db(request.json)
    webhook_manager.trigger_webhook('lead.created', lead)
    return jsonify(lead)

# When deal is won
@app.route('/api/deals/<deal_id>/win', methods=['PUT'])
def win_deal(deal_id):
    deal = update_deal_in_db(deal_id, {'stage': 'closed_won'})
    webhook_manager.trigger_webhook('deal.won', deal)
    return jsonify(deal)
```

---

## OAuth2 Integration

### OAuth2 Provider Integration

```python
# integrations/oauth2.py
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import GrantBase

class MyExtensionAuthorizationServer:
    def __init__(self, app):
        self.server = AuthorizationServer(app)
    
    def handle_authorization(self, request):
        """Handle OAuth2 authorization"""
        return self.server.create_authorization_response(request)
    
    def handle_token(self, request):
        """Handle OAuth2 token request"""
        return self.server.create_token_response(request)
```

### OAuth2 Consumer Integration

```python
# integrations/oauth2_consumer.py
from authlib.integrations.requests_client import OAuth2Session

class ExternalServiceOAuth2:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_authorization_url(self, redirect_uri):
        """Get OAuth2 authorization URL"""
        client = OAuth2Session(self.client_id, redirect_uri=redirect_uri)
        url, state = client.create_authorization_url('https://api.example.com/oauth/authorize')
        return url, state
    
    def exchange_token(self, code, redirect_uri):
        """Exchange authorization code for token"""
        client = OAuth2Session(
            self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirect_uri
        )
        token = client.fetch_token('https://api.example.com/oauth/token', code=code)
        return token
```

---

## External APIs

### REST API Client

```python
# integrations/api_client.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    """Reusable REST API client with retry logic"""
    
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self):
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get(self, endpoint, params=None, headers=None):
        """GET request"""
        try:
            response = self.session.get(
                f'{self.base_url}{endpoint}',
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}
    
    def post(self, endpoint, data=None, headers=None):
        """POST request"""
        try:
            response = self.session.post(
                f'{self.base_url}{endpoint}',
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}
```

### Example: HubSpot Integration

```python
# integrations/hubspot.py
from integrations.api_client import APIClient

class HubSpotIntegration:
    def __init__(self, api_key):
        self.client = APIClient('https://api.hubapi.com')
        self.api_key = api_key
    
    def get_headers(self):
        return {'Authorization': f'Bearer {self.api_key}'}
    
    def create_contact(self, email, first_name, last_name):
        """Create HubSpot contact"""
        return self.client.post(
            '/crm/v3/objects/contacts',
            data={
                'properties': {
                    'email': email,
                    'firstname': first_name,
                    'lastname': last_name
                }
            },
            headers=self.get_headers()
        )
    
    def sync_leads(self, leads):
        """Sync leads to HubSpot"""
        results = []
        for lead in leads:
            result = self.create_contact(
                lead['email'],
                lead['first_name'],
                lead['last_name']
            )
            results.append(result)
        return results
```

---

## Marketplace

### Extension Marketplace API

```python
# marketplace/extension_registry.py
class ExtensionRegistry:
    """Manage extension marketplace"""
    
    def __init__(self):
        self.extensions = {}
    
    def publish_extension(self, manifest, code_url):
        """Publish extension to marketplace"""
        extension = {
            'id': manifest['id'],
            'name': manifest['name'],
            'version': manifest['version'],
            'description': manifest['description'],
            'author': manifest['author'],
            'code_url': code_url,
            'published_at': datetime.utcnow().isoformat()
        }
        
        self.extensions[extension['id']] = extension
        return extension
    
    def list_extensions(self):
        """List all marketplace extensions"""
        return list(self.extensions.values())
    
    def get_extension(self, extension_id):
        """Get extension details"""
        return self.extensions.get(extension_id)
    
    def install_extension(self, extension_id, app):
        """Install extension"""
        extension = self.get_extension(extension_id)
        if not extension:
            return {'success': False, 'error': 'Extension not found'}
        
        # Download and install
        # ... implementation ...
        
        return {'success': True, 'message': f'Extension {extension_id} installed'}
```

---

## Best Practices

### Security

1. **API Keys**: Store securely in environment variables
2. **Rate Limiting**: Implement rate limits for external APIs
3. **Validation**: Validate all incoming data
4. **Encryption**: Encrypt sensitive data at rest
5. **Audit**: Log all integration activities

### Performance

1. **Caching**: Cache API responses
2. **Async**: Use async for long-running operations
3. **Batching**: Batch API requests when possible
4. **Retry Logic**: Implement exponential backoff
5. **Timeouts**: Set appropriate timeout values

### Reliability

1. **Error Handling**: Handle all error scenarios
2. **Monitoring**: Monitor integration health
3. **Fallback**: Provide fallback mechanisms
4. **Testing**: Test integrations thoroughly
5. **Documentation**: Document integration setup

---

## Example Integration Flow

```python
# Complete integration example
from flask import Flask, request, jsonify
from integrations.sendgrid_integration import SendGridIntegration
from integrations.stripe_integration import StripeIntegration

app = Flask(__name__)

# Initialize integrations
email_service = SendGridIntegration(os.environ.get('SENDGRID_API_KEY'))
payment_service = StripeIntegration(os.environ.get('STRIPE_API_KEY'))

@app.route('/api/leads', methods=['POST'])
def create_lead_with_payment():
    lead_data = request.json
    
    # Create lead
    lead = create_lead_in_db(lead_data)
    
    # Process payment
    payment = payment_service.create_payment(lead_data.get('amount'))
    
    if not payment['success']:
        return jsonify({'error': payment['error']}), 400
    
    # Send confirmation email
    email_result = email_service.send_email(
        lead_data['email'],
        'New Lead Created',
        f'<h1>Welcome {lead_data["name"]}!</h1>'
    )
    
    return jsonify({
        'lead': lead,
        'payment': payment,
        'email': email_result
    })
```

---

**Last Updated**: February 4, 2026
**Version**: 1.0
**Status**: Ready for Integration
