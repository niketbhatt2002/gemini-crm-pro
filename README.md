# 🚀 GeminiCRM Pro - AI-Powered Sales Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Gemini%203-Powered-4285f4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini 3">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
</p>

<p align="center">
  <strong>🏆 Built for the Gemini 3 Hackathon ($100K Prize Pool)</strong><br>
  An AI-native CRM that puts Google's Gemini 3 at the center of every sales interaction.
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Gemini 3 Integration](#-gemini-3-integration)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Hackathon Submission](#-hackathon-submission)

---

## 🎯 Overview

**GeminiCRM Pro** is a full-featured Customer Relationship Management system that leverages Google's **Gemini 3 API** to transform how sales teams work. Unlike traditional CRMs that bolt on AI as an afterthought, GeminiCRM was built from the ground up with AI as its core intelligence layer.

### The Problem

- Traditional CRMs like Salesforce charge $75+/user/month for basic AI features
- Sales teams spend 65% of their time on non-selling activities
- Manual lead scoring is inconsistent and time-consuming
- Email personalization at scale is nearly impossible

### Our Solution

GeminiCRM uses Gemini 3 to automate and enhance every aspect of the sales process:
- **Instant AI Lead Scoring** - Analyze leads in seconds, not hours
- **Smart Email Generation** - Personalized emails with one click
- **Conversation Intelligence** - Extract insights from any customer interaction
- **Predictive Deal Analytics** - Know which deals will close before they do

---

## ✨ Features

### Core CRM Features
| Feature | Description |
|---------|-------------|
| 📇 **Contact Management** | Full contact profiles with interaction history |
| 🎯 **Lead Management** | Track and qualify leads with engagement metrics |
| 💰 **Deal Pipeline** | Visual Kanban board with drag-and-drop |
| ✅ **Task Management** | Organized by priority and due date |
| 📊 **Analytics Dashboard** | Real-time performance metrics |

### AI-Powered Features (Gemini 3)
| Feature | Description |
|---------|-------------|
| 🧠 **AI Lead Scoring** | Comprehensive scoring with strengths, weaknesses, and recommended actions |
| ✉️ **Smart Email Generator** | Contextual, personalized emails in seconds |
| 💬 **Conversation Analyzer** | Extract sentiment, buying signals, and action items |
| 🔮 **Deal Predictor** | Win probability with risk factors and success strategies |
| 🎙️ **Notes Processor** | Turn meeting notes into structured CRM updates |
| 📈 **Dashboard Insights** | AI-powered pipeline analysis and forecasting |
| 💬 **AI Chat Assistant** | General-purpose sales assistant |

---

## 🧠 Gemini 3 Integration

GeminiCRM deeply integrates **Gemini 3 Flash** (`gemini-3-flash-preview`) across **7 AI features**:

### Integration Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Frontend UI   │ ──── │   Flask API      │ ──── │   Gemini 3 API  │
│   (HTML/JS)     │      │   (Python)       │      │   (Google)      │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │                         │
         │   User Actions         │   Structured Prompts    │
         │   (score lead,         │   with CRM Context      │
         │   generate email)      │                         │
         └────────────────────────┴─────────────────────────┘
```

### How Each Feature Uses Gemini 3

1. **AI Lead Scoring** - Sends lead data (engagement metrics, company info, notes) → Receives comprehensive JSON analysis with score, strengths, weaknesses, and recommendations

2. **Smart Email Generator** - Sends lead context + email type → Receives personalized email with subject, body, and CTA

3. **Conversation Analyzer** - Sends conversation transcript → Receives sentiment analysis, buying signals, objections, and action items

4. **Deal Predictor** - Sends deal + lead data → Receives win probability, risk factors, and winning strategies

5. **Notes Processor** - Sends unstructured notes → Receives structured summary, action items, and CRM updates

6. **Dashboard Insights** - Sends pipeline summary → Receives health score, priorities, and 30-day forecast

7. **AI Chat Assistant** - General sales questions → Contextual, actionable advice

### Gemini 3 Integration Description (200 words)

> GeminiCRM leverages Gemini 3's advanced reasoning capabilities across seven deeply integrated AI features. The core integration uses `gemini-3-flash-preview` through Google's GenAI Python SDK, with each feature utilizing carefully crafted prompts that include full CRM context.
>
> **Lead Scoring** analyzes 10+ engagement signals including email opens, website visits, and company fit to produce a comprehensive score with actionable recommendations. **Smart Email Generation** uses lead history and status to craft personalized follow-ups, introductions, and proposals. **Conversation Analysis** extracts sentiment, buying signals, pain points, and objections from any customer interaction.
>
> **Deal Prediction** combines deal data with lead engagement metrics to forecast win probability and identify risk factors. **Notes Processing** transforms unstructured meeting notes into structured summaries with prioritized action items. **Dashboard Insights** aggregates all CRM data to provide pipeline health scores and 30-day revenue forecasts.
>
> All responses are structured as JSON for seamless UI integration, with temperature tuning (0.3 for analytical tasks, 0.7 for creative content) to optimize output quality. The AI Chat Assistant provides a general-purpose interface for sales questions, completing the AI-native CRM experience.

---

## 📸 Screenshots

### Dashboard with AI Insights
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### Visual Pipeline (Kanban)
![Pipeline](https://via.placeholder.com/800x400?text=Pipeline+Screenshot)

### AI Lead Scoring
![Lead Scoring](https://via.placeholder.com/800x400?text=AI+Lead+Scoring)

### Smart Email Generator
![Email Generator](https://via.placeholder.com/800x400?text=Email+Generator)

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/gemini-crm-pro.git
cd gemini-crm-pro

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key (optional - can also set in UI)
export GEMINI_API_KEY="your-api-key-here"

# 5. Run the application
python app.py

# 6. Open in browser
# http://localhost:5000
```

### First Launch

1. Navigate to `http://localhost:5000`
2. Enter your Gemini API key when prompted (or click "Skip" to explore with sample data)
3. The app comes pre-loaded with sample leads, deals, and tasks

---

## 📖 Usage Guide

### Lead Scoring
1. Go to **Leads** page
2. Click **AI Score** on any lead card
3. View comprehensive analysis with score, strengths, and recommendations

### Email Generation
1. Open a lead's detail modal
2. Click **Generate Email**
3. Copy the AI-generated email to your clipboard

### Deal Prediction
1. Go to **Deals** or **Pipeline** page
2. Click **Predict** on any deal
3. View win probability, risk factors, and action items

### Pipeline Management
1. Go to **Pipeline** page
2. Drag deals between stages
3. Probabilities automatically update based on stage

### AI Assistant
1. Click the ✨ icon in the top right or sidebar
2. Ask any sales-related question
3. Get contextual, actionable advice

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Engine** | Google Gemini 3 API (`gemini-3-flash-preview`) |
| **Backend** | Python 3.9+, Flask 3.0, Flask-CORS |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Design System** | Google Material Design 3 inspired |
| **Fonts** | Google Sans, Roboto, Material Icons |

---

## 📁 Project Structure

```
gemini-crm-pro/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── models/
│   └── database.py          # Data models & in-memory storage
│
├── services/
│   └── gemini_service.py    # Gemini AI integration (7 features)
│
├── static/
│   ├── css/
│   │   └── style.css        # Material Design 3 styles
│   └── js/
│       └── app.js           # Frontend JavaScript
│
└── templates/
    ├── base.html            # Base template with sidebar & AI chat
    ├── index.html           # Dashboard
    ├── leads.html           # Leads management
    ├── contacts.html        # Contacts
    ├── pipeline.html        # Visual Kanban pipeline
    ├── deals.html           # Deals list
    ├── tasks.html           # Task management
    └── analytics.html       # Analytics dashboard
```

---

## 📡 API Documentation

### Configuration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config/status` | GET | Check API configuration |
| `/api/config` | POST | Set Gemini API key |

### CRUD Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contacts` | GET, POST | List/Create contacts |
| `/api/leads` | GET, POST | List/Create leads |
| `/api/deals` | GET, POST | List/Create deals |
| `/api/tasks` | GET, POST | List/Create tasks |

### AI Features
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/score-lead` | POST | AI lead scoring |
| `/api/ai/generate-email` | POST | Smart email generation |
| `/api/ai/analyze-conversation` | POST | Conversation analysis |
| `/api/ai/predict-deal` | POST | Deal prediction |
| `/api/ai/process-notes` | POST | Notes processing |
| `/api/ai/dashboard-insights` | GET | Pipeline insights |
| `/api/ai/chat` | POST | AI chat assistant |

---

## 🏆 Hackathon Submission

### Judging Criteria Alignment

| Criteria | Weight | How GeminiCRM Addresses It |
|----------|--------|---------------------------|
| **Technical Execution** | 40% | 7 deeply integrated AI features, clean architecture, production-ready code |
| **Innovation** | 30% | AI-native CRM (not bolt-on), unique multi-feature integration |
| **Potential Impact** | 20% | Addresses $80B+ CRM market, democratizes AI for SMBs |
| **Presentation** | 10% | Professional UI, clear documentation, demo video |

### What Makes Us Different

1. **AI-Native Architecture** - Not AI added to existing CRM, but CRM built around AI
2. **7 Integrated AI Features** - Most hackathon projects have 1-2
3. **Production-Ready** - Full CRUD, responsive design, error handling
4. **Real Business Value** - Solves actual sales pain points

---

## 📜 License

MIT License - Built for the Gemini 3 Hackathon 2026

---

## 🙏 Acknowledgments

- Google DeepMind for Gemini 3 API
- The Gemini 3 Hackathon organizers
- Material Design team for the design system

---

<p align="center">
  Made with ❤️ for the Gemini 3 Hackathon
</p>
