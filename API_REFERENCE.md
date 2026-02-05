# GeminiCRM Pro - API Reference

Complete API documentation for all endpoints.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently uses environment-based API key for Gemini. Production should use JWT/OAuth.

---

## Configuration Endpoints

### Check API Status
```
GET /api/config/status
```
Returns whether Gemini API is configured.

**Response:**
```json
{
  "configured": true,
  "key_preview": "sk_****...****"
}
```

### Set API Key
```
POST /api/config
Content-Type: application/json
```

**Body:**
```json
{
  "api_key": "your-gemini-api-key"
}
```

**Response:**
```json
{
  "success": true
}
```

---

## Dashboard Endpoints

### Get Dashboard Statistics
```
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total_contacts": 6,
  "total_leads": 5,
  "total_deals": 5,
  "total_pipeline": 360000,
  "weighted_pipeline": 158000,
  "avg_lead_score": 60.2,
  "hot_leads": 3,
  "pending_tasks": 5,
  "overdue_tasks": 0,
  "deals_by_stage": {
    "lead": {"count": 1, "value": 25000},
    "qualified": {"count": 1, "value": 120000},
    "proposal": {"count": 2, "value": 120000},
    "negotiation": {"count": 1, "value": 95000}
  },
  "pipeline_stages": [...]
}
```

---

## Contacts Endpoints

### List All Contacts
```
GET /api/contacts
GET /api/contacts?q=search_query
```

**Query Parameters:**
- `q` (optional): Search query

**Response:**
```json
{
  "contacts": [
    {
      "id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "initials": "JD",
      "email": "john@example.com",
      "phone": "+1-555-0000",
      "company": "Tech Corp",
      "title": "VP Engineering",
      "avatar_color": "#4285f4",
      "created_at": "2025-02-04T10:00:00",
      "updated_at": "2025-02-04T10:00:00"
    }
  ]
}
```

### Create Contact
```
POST /api/contacts
Content-Type: application/json
```

**Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-0000",
  "company": "Tech Corp",
  "title": "VP Engineering",
  "industry": "Technology",
  "city": "San Francisco",
  "country": "USA"
}
```

**Response:**
```json
{
  "success": true,
  "contact": {...}
}
```

### Get Single Contact
```
GET /api/contacts/{contact_id}
```

**Response:**
```json
{
  "contact": {...}
}
```

### Update Contact
```
PUT /api/contacts/{contact_id}
Content-Type: application/json
```

**Body:** (Any fields to update)
```json
{
  "phone": "+1-555-1111",
  "title": "Director"
}
```

**Response:**
```json
{
  "success": true,
  "contact": {...}
}
```

### Delete Contact
```
DELETE /api/contacts/{contact_id}
```

**Response:**
```json
{
  "success": true
}
```

---

## Leads Endpoints

### List All Leads
```
GET /api/leads
GET /api/leads?status=Qualified
GET /api/leads?q=search_query
```

**Query Parameters:**
- `status` (optional): Filter by status
- `q` (optional): Search query

**Response:**
```json
{
  "leads": [
    {
      "id": "uuid",
      "name": "Sarah Johnson",
      "email": "sarah@example.com",
      "company": "TechCorp",
      "title": "VP Engineering",
      "source": "Website",
      "status": "Qualified",
      "score": 85,
      "score_grade": "A",
      "estimated_value": 75000,
      "email_opens": 12,
      "website_visits": 8,
      "ai_score": 87,
      "created_at": "2025-02-04T10:00:00"
    }
  ]
}
```

### Create Lead
```
POST /api/leads
Content-Type: application/json
```

**Body:**
```json
{
  "name": "John Prospect",
  "email": "john@example.com",
  "company": "Tech Corp",
  "source": "LinkedIn",
  "status": "New",
  "score": 50,
  "estimated_value": 100000,
  "notes": "Good prospect, needs follow-up"
}
```

### Get Single Lead
```
GET /api/leads/{lead_id}
```

### Update Lead
```
PUT /api/leads/{lead_id}
Content-Type: application/json
```

### Delete Lead
```
DELETE /api/leads/{lead_id}
```

---

## Deals Endpoints

### List All Deals
```
GET /api/deals
GET /api/deals?stage=proposal
```

**Query Parameters:**
- `stage` (optional): Filter by pipeline stage

**Response:**
```json
{
  "deals": [
    {
      "id": "uuid",
      "name": "TechCorp Enterprise",
      "company": "TechCorp Industries",
      "value": 75000,
      "stage": "proposal",
      "stage_color": "#fbbc04",
      "probability": 60,
      "weighted_value": 45000,
      "expected_close_date": "2025-03-06",
      "ai_win_probability": 65,
      "created_at": "2025-02-04T10:00:00"
    }
  ],
  "stages": [...]
}
```

### Create Deal
```
POST /api/deals
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Deal Name",
  "company": "Company Name",
  "value": 100000,
  "stage": "lead",
  "probability": 10,
  "expected_close_date": "2025-03-01",
  "description": "Deal description"
}
```

### Get Single Deal
```
GET /api/deals/{deal_id}
```

### Update Deal
```
PUT /api/deals/{deal_id}
Content-Type: application/json
```

### Update Deal Stage
```
PUT /api/deals/{deal_id}/stage
Content-Type: application/json
```

**Body:**
```json
{
  "stage": "proposal"
}
```

**Note:** Probability auto-updates based on stage.

### Delete Deal
```
DELETE /api/deals/{deal_id}
```

---

## Tasks Endpoints

### List All Tasks
```
GET /api/tasks
GET /api/tasks?status=pending
```

**Query Parameters:**
- `status` (optional): Filter by status

**Response:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Follow up with Sarah",
      "type": "Call",
      "priority": "High",
      "priority_color": "#fbbc04",
      "status": "pending",
      "due_date": "2025-02-05",
      "is_overdue": false,
      "contact_id": "uuid",
      "created_at": "2025-02-04T10:00:00"
    }
  ]
}
```

### Create Task
```
POST /api/tasks
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Task Title",
  "type": "Call",
  "priority": "High",
  "due_date": "2025-02-10",
  "description": "Task details",
  "contact_id": "uuid"
}
```

### Get Single Task
```
GET /api/tasks/{task_id}
```

### Update Task
```
PUT /api/tasks/{task_id}
Content-Type: application/json
```

### Complete Task
```
POST /api/tasks/{task_id}/complete
```

**Response:**
```json
{
  "success": true,
  "task": {...}
}
```

### Delete Task
```
DELETE /api/tasks/{task_id}
```

---

## Activities Endpoints

### List Activities
```
GET /api/activities
GET /api/activities?contact_id=uuid
GET /api/activities?lead_id=uuid
GET /api/activities?deal_id=uuid
```

**Query Parameters:**
- `contact_id` (optional): Filter by contact
- `lead_id` (optional): Filter by lead
- `deal_id` (optional): Filter by deal

**Response:**
```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "email",
      "icon": "email",
      "title": "Sent introduction",
      "description": "Initial contact email",
      "contact_id": "uuid",
      "created_at": "2025-02-04T10:00:00"
    }
  ]
}
```

### Create Activity
```
POST /api/activities
Content-Type: application/json
```

**Body:**
```json
{
  "type": "call",
  "title": "Discovery call",
  "description": "Discussed requirements",
  "contact_id": "uuid"
}
```

---

## AI Endpoints

### Score Lead
```
POST /api/ai/score-lead
Content-Type: application/json
```

**Body:**
```json
{
  "lead_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "score": 87,
    "grade": "A",
    "conversion_probability": 78,
    "urgency": "high",
    "strengths": ["Strong engagement", "Good fit"],
    "weaknesses": ["Budget pending"],
    "buying_signals": ["Requested demo", "Multiple visits"],
    "recommended_actions": ["Schedule demo", "Send proposal"],
    "ideal_next_step": "Send demo booking email",
    "estimated_close_timeline": "2-4 weeks",
    "summary": "High-quality prospect with strong signals"
  }
}
```

### Generate Email
```
POST /api/ai/generate-email
Content-Type: application/json
```

**Body:**
```json
{
  "lead_id": "uuid",
  "type": "follow_up",
  "tone": "professional",
  "context": "After discovery call"
}
```

**Response:**
```json
{
  "success": true,
  "email": {
    "subject": "Following up on our discussion",
    "body": "Hi [Name],\n\nThank you for...",
    "call_to_action": "Schedule next call",
    "follow_up_timing": "If no response in 3 days",
    "tips": ["Personalize further", "Add value"]
  }
}
```

### Analyze Conversation
```
POST /api/ai/analyze-conversation
Content-Type: application/json
```

**Body:**
```json
{
  "conversation": "Full conversation transcript",
  "lead_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "sentiment": "positive",
    "sentiment_score": 75,
    "key_topics": ["Pricing", "Integration", "Timeline"],
    "pain_points": ["Current delays", "Cost concerns"],
    "needs_identified": ["Faster implementation", "ROI"],
    "buying_signals": ["Budget confirmed", "Timeline set"],
    "objections": ["Integration complexity"],
    "action_items": ["Send architecture doc", "Schedule demo"],
    "deal_stage_suggestion": "proposal",
    "summary": "Strong prospect ready for proposal stage"
  }
}
```

### Predict Deal
```
POST /api/ai/predict-deal
Content-Type: application/json
```

**Body:**
```json
{
  "deal_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "win_probability": 75,
    "confidence": "high",
    "predicted_outcome": "win",
    "predicted_close_date": "2025-03-15",
    "predicted_final_value": 75000,
    "deal_velocity": "normal",
    "risk_factors": ["Competing vendor", "Budget approval"],
    "success_factors": ["Strong champion", "Good fit"],
    "key_actions_to_win": ["Schedule executive meeting", "Send case study"],
    "potential_blockers": ["Procurement delays"],
    "stage_recommendation": "proposal",
    "priority_score": 9,
    "summary": "High-probability deal. Focus on executive alignment."
  }
}
```

### Process Notes
```
POST /api/ai/process-notes
Content-Type: application/json
```

**Body:**
```json
{
  "notes": "Meeting transcript or notes",
  "lead_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "processed": {
    "summary": "Discussed implementation timeline and budget",
    "key_points": ["3-month implementation", "$100K budget", "Team of 5"],
    "action_items": [
      {"task": "Send proposal", "priority": "high", "due": "2 days"}
    ],
    "decisions_made": ["Approved pilot", "Assigned project manager"],
    "update_lead_notes": "New action items: Send proposal, Schedule kickoff"
  }
}
```

### Get Dashboard Insights
```
GET /api/ai/dashboard-insights
```

**Response:**
```json
{
  "success": true,
  "insights": {
    "health_score": 82,
    "health_status": "good",
    "pipeline_summary": "$335K pipeline across 5 deals",
    "top_priorities": ["Close Premier deal", "Qualify InnovateAI", "Demo for Global Retail"],
    "hot_leads": ["David Park", "Sarah Johnson"],
    "at_risk_deals": [],
    "quick_wins": ["Follow up with Lisa Thompson", "Send Acme proposal"],
    "key_insights": ["Premier deal closing soon", "Strong Q1 pipeline"],
    "this_week_actions": ["Contract review", "Follow-up calls", "Demo prep"],
    "forecast_30_days": {
      "expected_closes": 1,
      "expected_revenue": 95000,
      "confidence": "high"
    }
  }
}
```

### AI Chat
```
POST /api/ai/chat
Content-Type: application/json
```

**Body:**
```json
{
  "message": "How should I approach this tough negotiation?",
  "context": {"deal_id": "uuid"}
}
```

**Response:**
```json
{
  "success": true,
  "response": "Here are some strategies for tough negotiations..."
}
```

### Suggest Tasks
```
POST /api/ai/suggest-tasks
Content-Type: application/json
```

**Body:**
```json
{
  "lead_id": "uuid",
  "deal_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "title": "Schedule demo",
      "description": "Product demo for stakeholders",
      "type": "Meeting",
      "priority": "High",
      "due_in_days": 3,
      "reason": "Lead expressed interest in seeing platform"
    }
  ]
}
```

---

## Search Endpoints

### Global Search
```
GET /api/search?q=query
```

**Query Parameters:**
- `q`: Search query (minimum 2 characters)

**Response:**
```json
{
  "results": [
    {
      "type": "contact",
      "id": "uuid",
      "title": "Sarah Johnson",
      "subtitle": "TechCorp Industries",
      "icon": "person"
    },
    {
      "type": "lead",
      "id": "uuid",
      "title": "Sarah Johnson",
      "subtitle": "TechCorp Industries",
      "icon": "trending_up"
    },
    {
      "type": "deal",
      "id": "uuid",
      "title": "TechCorp Enterprise",
      "subtitle": "$75,000",
      "icon": "handshake"
    }
  ]
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "error": "Bad request"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

### AI API Not Configured
```json
{
  "error": "Gemini API not configured"
}
```

---

## Rate Limiting
Currently not implemented. To be added in production.

## Authentication
Currently uses environment variables. Production should implement JWT/OAuth.

## CORS
Currently allows all origins. Configure in `.env` for production.

---

**API Version**: 1.0.0
**Last Updated**: February 4, 2026
