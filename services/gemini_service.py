"""
GeminiCRM Pro - Gemini AI Service
Comprehensive AI integration for CRM intelligence
"""
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# Global client
_client = None

def get_client():
    """Get or initialize Gemini client"""
    global _client
    if _client is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            _client = genai.Client(api_key=api_key)
    return _client

def set_api_key(api_key):
    """Set API key and reinitialize client"""
    global _client
    os.environ['GEMINI_API_KEY'] = api_key
    _client = genai.Client(api_key=api_key)
    return True

def is_configured():
    """Check if API is configured"""
    return bool(os.environ.get('GEMINI_API_KEY'))


def _call_gemini(prompt, temperature=0.3, max_tokens=2000):
    """Make a call to Gemini API"""
    client = get_client()
    if not client:
        return {"error": "Gemini API not configured"}
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return {"success": True, "text": response.text}
    except Exception as e:
        return {"error": str(e)}


def _parse_json_response(text):
    """Extract JSON from response text"""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    return None


# ==================== AI FEATURES ====================

def score_lead(lead_data):
    """
    AI Lead Scoring
    Analyzes lead data and returns comprehensive scoring
    """
    prompt = f"""You are an expert B2B sales analyst. Analyze this lead and provide a comprehensive scoring assessment.

LEAD DATA:
- Name: {lead_data.get('name', 'Unknown')}
- Company: {lead_data.get('company', 'Unknown')}
- Title: {lead_data.get('title', 'Unknown')}
- Source: {lead_data.get('source', 'Unknown')}
- Current Status: {lead_data.get('status', 'New')}
- Estimated Deal Value: ${lead_data.get('estimated_value', 0):,}
- Email Opens: {lead_data.get('email_opens', 0)}
- Email Clicks: {lead_data.get('email_clicks', 0)}
- Website Visits: {lead_data.get('website_visits', 0)}
- Notes: {lead_data.get('notes', 'No notes')}

Analyze and provide JSON response:
{{
    "score": <0-100>,
    "grade": "<A/B/C/D/F>",
    "conversion_probability": <0-100>,
    "urgency": "<high/medium/low>",
    "strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "weaknesses": ["<weakness1>", "<weakness2>"],
    "buying_signals": ["<signal1>", "<signal2>"],
    "recommended_actions": ["<action1>", "<action2>", "<action3>"],
    "ideal_next_step": "<specific next action>",
    "estimated_close_timeline": "<e.g., 2-4 weeks>",
    "summary": "<2-3 sentence summary>"
}}

Consider: job title authority, engagement signals, company fit, deal size, and timing indicators."""

    result = _call_gemini(prompt, temperature=0.3)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "analysis": parsed}
    return {"success": True, "analysis": {"raw": result["text"]}}


def generate_email(lead_data, email_type="follow_up", tone="professional", context=""):
    """
    Smart Email Generator
    Creates personalized emails based on context
    """
    prompt = f"""You are an expert B2B sales copywriter. Write a personalized {email_type} email.

RECIPIENT INFORMATION:
- Name: {lead_data.get('name', 'the prospect')}
- Company: {lead_data.get('company', 'their company')}
- Title: {lead_data.get('title', '')}
- Current Status: {lead_data.get('status', 'New')}
- Previous Notes: {lead_data.get('notes', 'No previous notes')}
- Engagement: {lead_data.get('email_opens', 0)} email opens, {lead_data.get('website_visits', 0)} site visits

EMAIL REQUIREMENTS:
- Type: {email_type}
- Tone: {tone}
- Additional Context: {context if context else 'None provided'}

Provide JSON response:
{{
    "subject": "<compelling subject line>",
    "body": "<full email body with proper formatting, use \\n for line breaks>",
    "call_to_action": "<the main CTA>",
    "follow_up_timing": "<when to follow up>",
    "tips": ["<personalization tip>", "<improvement suggestion>"]
}}

Make it personalized, value-focused, and concise with a clear CTA."""

    result = _call_gemini(prompt, temperature=0.7)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "email": parsed}
    return {"success": True, "email": {"raw": result["text"]}}


def analyze_conversation(conversation_text, lead_data=None):
    """
    Conversation Analyzer
    Extracts insights from customer conversations
    """
    lead_context = ""
    if lead_data:
        lead_context = f"""
LEAD CONTEXT:
- Name: {lead_data.get('name', 'Unknown')}
- Company: {lead_data.get('company', 'Unknown')}
- Current Stage: {lead_data.get('status', 'Unknown')}
"""

    prompt = f"""You are an expert sales conversation analyst. Analyze this customer conversation and extract key insights.

CONVERSATION:
{conversation_text}
{lead_context}

Provide JSON response:
{{
    "sentiment": "<positive/neutral/negative>",
    "sentiment_score": <-100 to 100>,
    "key_topics": ["<topic1>", "<topic2>", "<topic3>"],
    "pain_points": ["<pain point 1>", "<pain point 2>"],
    "needs_identified": ["<need1>", "<need2>"],
    "buying_signals": ["<signal1>", "<signal2>"],
    "objections": ["<objection1>", "<objection2>"],
    "competitors_mentioned": ["<competitor1>"],
    "budget_indicators": "<any budget info>",
    "timeline_indicators": "<any timeline info>",
    "decision_makers": ["<person1>"],
    "action_items": ["<action1>", "<action2>", "<action3>"],
    "recommended_next_steps": ["<step1>", "<step2>"],
    "deal_stage_suggestion": "<suggested pipeline stage>",
    "summary": "<2-3 sentence summary>"
}}

Be thorough and identify all sales-relevant insights."""

    result = _call_gemini(prompt, temperature=0.3)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "analysis": parsed}
    return {"success": True, "analysis": {"raw": result["text"]}}


def predict_deal(deal_data, lead_data=None):
    """
    Deal Predictor
    Forecasts deal outcomes and provides recommendations
    """
    lead_context = ""
    if lead_data:
        lead_context = f"""
ASSOCIATED LEAD:
- Engagement Score: {lead_data.get('score', 50)}/100
- Email Opens: {lead_data.get('email_opens', 0)}
- Website Visits: {lead_data.get('website_visits', 0)}
- Notes: {lead_data.get('notes', 'No notes')}
"""

    prompt = f"""You are an expert sales forecasting AI. Predict the outcome of this deal.

DEAL DATA:
- Deal Name: {deal_data.get('name', 'Unknown')}
- Company: {deal_data.get('company', 'Unknown')}
- Value: ${deal_data.get('value', 0):,}
- Current Stage: {deal_data.get('stage', 'lead')}
- Current Probability: {deal_data.get('probability', 10)}%
- Expected Close: {deal_data.get('expected_close_date', 'Not set')}
- Description: {deal_data.get('description', 'No description')}
- Notes: {deal_data.get('notes', 'No notes')}
{lead_context}

Provide JSON response:
{{
    "win_probability": <0-100>,
    "confidence": "<high/medium/low>",
    "predicted_outcome": "<win/loss/stall>",
    "predicted_close_date": "<YYYY-MM-DD or 'uncertain'>",
    "predicted_final_value": <dollar amount>,
    "deal_velocity": "<fast/normal/slow>",
    "risk_factors": ["<risk1>", "<risk2>", "<risk3>"],
    "success_factors": ["<factor1>", "<factor2>"],
    "key_actions_to_win": ["<action1>", "<action2>", "<action3>"],
    "potential_blockers": ["<blocker1>", "<blocker2>"],
    "stage_recommendation": "<suggested stage>",
    "priority_score": <1-10>,
    "summary": "<2-3 sentence prediction summary>"
}}

Be realistic and data-driven."""

    result = _call_gemini(prompt, temperature=0.4)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "prediction": parsed}
    return {"success": True, "prediction": {"raw": result["text"]}}


def process_notes(notes_text, lead_data=None):
    """
    Voice/Meeting Notes Processor
    Extracts structured data from unstructured notes
    """
    lead_context = ""
    if lead_data:
        lead_context = f"""
ASSOCIATED LEAD:
- Name: {lead_data.get('name', 'Unknown')}
- Company: {lead_data.get('company', 'Unknown')}
"""

    prompt = f"""You are a sales assistant AI. Process these meeting notes and extract structured information.

NOTES:
"{notes_text}"
{lead_context}

Provide JSON response:
{{
    "summary": "<brief 1-2 sentence summary>",
    "key_points": ["<point1>", "<point2>", "<point3>"],
    "action_items": [
        {{"task": "<task>", "priority": "<high/medium/low>", "due": "<timeframe>", "assigned_to": "<who>"}}
    ],
    "follow_up_required": <true/false>,
    "follow_up_date": "<suggested date or null>",
    "sentiment": "<positive/neutral/negative>",
    "names_mentioned": ["<name1>"],
    "dates_mentioned": ["<date1>"],
    "amounts_mentioned": ["<amount1>"],
    "decisions_made": ["<decision1>"],
    "questions_to_answer": ["<question1>"],
    "update_lead_notes": "<text to add to lead notes>",
    "suggested_tasks": [
        {{"title": "<task title>", "type": "<Call/Email/Meeting>", "priority": "<priority>"}}
    ]
}}

Extract all relevant sales information."""

    result = _call_gemini(prompt, temperature=0.3)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "processed": parsed}
    return {"success": True, "processed": {"raw": result["text"]}}


def get_dashboard_insights(leads, deals, tasks):
    """
    Dashboard AI Insights
    Analyzes overall CRM data and provides insights
    """
    # Compile stats
    total_pipeline = sum(d.get('value', 0) for d in deals)
    weighted_pipeline = sum(d.get('value', 0) * d.get('probability', 0) / 100 for d in deals)
    avg_score = sum(l.get('score', 0) for l in leads) / len(leads) if leads else 0
    
    deals_by_stage = {}
    for d in deals:
        stage = d.get('stage', 'unknown')
        deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
    
    overdue_tasks = len([t for t in tasks if t.get('is_overdue')])
    pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])

    prompt = f"""You are a sales analytics AI. Analyze this CRM data and provide strategic insights.

CRM SUMMARY:
- Total Leads: {len(leads)}
- Total Deals: {len(deals)}
- Total Pipeline Value: ${total_pipeline:,}
- Weighted Pipeline: ${weighted_pipeline:,.0f}
- Average Lead Score: {avg_score:.1f}/100
- Deals by Stage: {json.dumps(deals_by_stage)}
- Pending Tasks: {pending_tasks}
- Overdue Tasks: {overdue_tasks}

TOP LEADS (by score):
{json.dumps([{'name': l.get('name'), 'company': l.get('company'), 'score': l.get('score'), 'value': l.get('estimated_value')} for l in sorted(leads, key=lambda x: x.get('score', 0), reverse=True)[:5]], indent=2)}

TOP DEALS (by value):
{json.dumps([{'name': d.get('name'), 'value': d.get('value'), 'stage': d.get('stage'), 'probability': d.get('probability')} for d in sorted(deals, key=lambda x: x.get('value', 0), reverse=True)[:5]], indent=2)}

Provide JSON response:
{{
    "health_score": <0-100>,
    "health_status": "<excellent/good/needs_attention/critical>",
    "pipeline_summary": "<one line summary>",
    "top_priorities": ["<priority1>", "<priority2>", "<priority3>"],
    "hot_leads": ["<lead name>"],
    "at_risk_deals": ["<deal name>"],
    "quick_wins": ["<opportunity>"],
    "key_insights": ["<insight1>", "<insight2>", "<insight3>"],
    "recommended_focus": ["<focus area 1>", "<focus area 2>"],
    "this_week_actions": ["<action1>", "<action2>", "<action3>"],
    "forecast_30_days": {{
        "expected_closes": <number>,
        "expected_revenue": <amount>,
        "confidence": "<high/medium/low>"
    }},
    "warnings": ["<warning if any>"],
    "summary": "<executive summary in 2-3 sentences>"
}}

Provide actionable, specific insights."""

    result = _call_gemini(prompt, temperature=0.4)
    if "error" in result:
        return result
    
    parsed = _parse_json_response(result["text"])
    if parsed:
        return {"success": True, "insights": parsed}
    return {"success": True, "insights": {"raw": result["text"]}}


def chat_assistant(message, context=None):
    """
    AI Chat Assistant
    General-purpose sales assistant chat
    """
    system_context = """You are GeminiCRM's AI Sales Assistant. You help sales professionals with:
- Lead qualification and scoring
- Email drafting and communication
- Deal strategy and forecasting
- Task prioritization
- Sales best practices
- CRM data analysis

Be helpful, concise, and actionable. Focus on practical sales advice."""

    context_info = ""
    if context:
        context_info = f"\n\nCURRENT CONTEXT:\n{json.dumps(context, indent=2)}"

    prompt = f"""{system_context}
{context_info}

USER MESSAGE: {message}

Provide a helpful, actionable response. If appropriate, structure your response with clear sections or bullet points."""

    result = _call_gemini(prompt, temperature=0.7, max_tokens=1500)
    if "error" in result:
        return result
    
    return {"success": True, "response": result["text"]}


def suggest_tasks(lead_data=None, deal_data=None):
    """
    AI Task Suggestions
    Suggests next actions based on context
    """
    context = ""
    if lead_data:
        context += f"""
LEAD:
- Name: {lead_data.get('name')}
- Status: {lead_data.get('status')}
- Score: {lead_data.get('score')}
- Last Activity: {lead_data.get('last_activity')}
"""
    if deal_data:
        context += f"""
DEAL:
- Name: {deal_data.get('name')}
- Stage: {deal_data.get('stage')}
- Value: ${deal_data.get('value', 0):,}
- Expected Close: {deal_data.get('expected_close_date')}
"""

    prompt = f"""You are a sales productivity AI. Suggest tasks based on this context:
{context}

Provide JSON array of suggested tasks:
[
    {{
        "title": "<task title>",
        "description": "<brief description>",
        "type": "<Call/Email/Meeting/Follow-up/Demo/Other>",
        "priority": "<Urgent/High/Medium/Low>",
        "due_in_days": <number>,
        "reason": "<why this task>"
    }}
]

Suggest 3-5 actionable tasks."""

    result = _call_gemini(prompt, temperature=0.5)
    if "error" in result:
        return result
    
    try:
        text = result["text"]
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            tasks = json.loads(text[start:end])
            return {"success": True, "suggestions": tasks}
    except:
        pass
    
    return {"success": True, "suggestions": []}
