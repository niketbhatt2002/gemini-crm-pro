"""
GeminiCRM Pro - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = 'gemini-2.0-flash'
    
    # App Settings
    APP_NAME = 'GeminiCRM'
    APP_VERSION = '1.0.0'
    
    # Pipeline Stages
    PIPELINE_STAGES = [
        {'id': 'lead', 'name': 'Lead', 'color': '#4285f4'},
        {'id': 'qualified', 'name': 'Qualified', 'color': '#34a853'},
        {'id': 'proposal', 'name': 'Proposal', 'color': '#fbbc04'},
        {'id': 'negotiation', 'name': 'Negotiation', 'color': '#ff6d01'},
        {'id': 'closed_won', 'name': 'Closed Won', 'color': '#0f9d58'},
        {'id': 'closed_lost', 'name': 'Closed Lost', 'color': '#ea4335'},
    ]
    
    # Lead Sources
    LEAD_SOURCES = [
        'Website', 'Referral', 'LinkedIn', 'Google Ads', 
        'Trade Show', 'Cold Outreach', 'Partner', 'Other'
    ]
    
    # Task Priorities
    TASK_PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
    
    # Task Types
    TASK_TYPES = ['Call', 'Email', 'Meeting', 'Follow-up', 'Demo', 'Other']
