# 🎉 Quick Start Guide - Run GeminiCRM Pro Locally

Welcome! This guide will have you viewing this amazing enterprise-grade CRM system in just **5 minutes**.

---

## 📋 Prerequisites

Make sure you have these installed on your Windows machine:

- ✅ **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- ✅ **Git** - [Download here](https://git-scm.com/download/win)
- ✅ **Visual Studio Code** (Optional but recommended)

**Verify Installation**:
```powershell
python --version
pip --version
git --version
```

---

## 🚀 Step 1: Navigate to Project Directory

```powershell
cd "c:\Users\Niket Bhatt\Documents\gemini-crm-pro"
```

---

## 📦 Step 2: Install Dependencies

Install all required Python packages:

```powershell
pip install -r requirements.txt
```

**What this installs**:
- ✅ Flask - Web framework
- ✅ Flask-CORS - API cross-origin support
- ✅ Google GenAI - Gemini API integration
- ✅ Python-dotenv - Environment configuration
- ✅ And 15+ more essential packages

**Expected output**:
```
Successfully installed flask-3.x.x flask-cors-4.x.x google-genai-1.x.x ...
```

---

## 🔑 Step 3: Configure API Keys (Optional but Recommended)

### Option A: Use without Gemini AI (Development Mode)
The app works perfectly without Gemini API key - all features are available!

### Option B: Enable Gemini AI Features (Recommended)
Get a free Gemini API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key

Create a `.env` file in the project root:

```powershell
# Windows PowerShell
@"
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
"@ | Out-File -Encoding utf8 .env
```

Or create it manually:
- Open the project folder in VS Code
- Create new file: `.env`
- Add: `GEMINI_API_KEY=your_api_key_here`
- Save

---

## ✨ Step 4: Start the Application

Run the Flask development server:

```powershell
python app.py
```

**Expected output**:
```
 * Running on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```

---

## 🌐 Step 5: Open in Your Browser

Open your web browser and go to:

```
http://localhost:5000
```

### You should see:

✅ **Dashboard** - Overview with stats
✅ **Leads** - Lead management with AI scoring
✅ **Contacts** - Full contact database
✅ **Deals** - Kanban pipeline view
✅ **Tasks** - Task management
✅ **Analytics** - Reports and insights
✅ **Profile** - User profile settings
✅ **Notifications** - Real-time alerts

---

## 🎯 What You Can Do

### 1. **Explore the Dashboard**
- View key metrics
- See activity summary
- Check recent deals

### 2. **Manage Leads**
- Add new leads
- View lead details
- Use AI scoring (if Gemini API configured)
- Track lead interactions

### 3. **Organize Contacts**
- Browse all contacts
- Add new contacts
- View interaction history
- Export contact data

### 4. **Track Deals**
- Drag deals between pipeline stages
- Add new opportunities
- Update deal amounts
- Track deal progress

### 5. **Create Tasks**
- Create new tasks
- Set priorities and due dates
- Mark tasks complete
- Assign to team members

### 6. **View Analytics**
- Sales metrics and trends
- Deal forecasting
- Team performance
- Activity reports

### 7. **Manage Profile**
- Update user settings
- Configure notifications
- Set preferences
- View profile details

---

## 📱 Features Available Offline

All core CRM features work without internet:
- ✅ Lead management
- ✅ Contact management
- ✅ Deal tracking
- ✅ Task management
- ✅ User profiles
- ✅ Notifications
- ✅ Activity logging
- ✅ Dashboard analytics

**AI Features require Gemini API key**:
- 🤖 AI Lead Scoring
- 🤖 Email generation
- 🤖 Conversation analysis

---

## 🛑 Stop the Application

Press `Ctrl+C` in the terminal:

```
Press CTRL+C to quit
```

---

## 🎨 Explore the Design

GeminiCRM Pro features:
- 🎨 **Google Material Design 3** - Professional, modern UI
- 📱 **Fully Responsive** - Works on desktop, tablet, mobile
- ⚡ **Smooth Animations** - Professional transitions
- 🎯 **Intuitive Navigation** - Sidebar + top header
- 🌙 **Professional Colors** - Google's color system

---

## 📊 Project Structure

```
gemini-crm-pro/
├── app.py                          # Main Flask application (941 lines)
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
│
├── models/
│   ├── database.py                # Data models
│   ├── user_profile.py            # User & notification system
│   └── salesforce_features.py     # Salesforce features (Tasks, Events, etc)
│
├── services/
│   └── gemini_service.py          # Gemini AI integration
│
├── routes/
│   └── __init__.py
│
├── static/
│   ├── css/
│   │   ├── style.css              # Original styles
│   │   └── material-design-3.css  # Material Design 3 (1,300+ lines)
│   └── js/
│       └── app.js                 # Frontend JavaScript
│
└── templates/
    ├── base.html                  # Base template
    ├── base-new.html              # Material Design 3 layout
    ├── index.html                 # Dashboard
    ├── leads.html                 # Lead management
    ├── contacts.html              # Contact management
    ├── deals.html                 # Deal pipeline
    ├── tasks.html                 # Task management
    ├── analytics.html             # Analytics
    ├── profile.html               # User profile
    └── notifications.html         # Notifications
```

---

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "Port 5000 is already in use"

**Solution**: Kill existing process or use different port
```powershell
# Kill existing Python processes
taskkill /F /IM python.exe

# Or run on different port
python app.py --port=5001
```

### Issue: "GEMINI_API_KEY not set"

**Solution**: Not required! The app works without it
- Development mode: All features work
- Production mode: Add API key to .env file

### Issue: CSS or JavaScript not loading

**Solution**: Clear browser cache (Ctrl+Shift+Delete) and refresh

### Issue: "ImportError" when running app.py

**Solution**: Verify Python environment
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m py_compile app.py
```

---

## 🎓 Learning the Codebase

### Key Files to Understand

**1. app.py** (941 lines)
- All 50+ API endpoints
- Route handlers
- Flask configuration
- Error handling

**2. models/salesforce_features.py** (447 lines)
- Task management system
- Event management
- Reporting engine
- Approval workflows
- And more!

**3. static/css/material-design-3.css** (1,300+ lines)
- Complete design system
- 80+ CSS variables
- 30+ component classes
- Responsive design

**4. models/user_profile.py** (429 lines)
- User management
- Notification system
- Activity logging
- Profile management

### API Endpoints (50+)

View all endpoints:
```powershell
# From project root
Find-Content -Path "app.py" -Pattern "@app.route" | Measure-Object -Line
```

Or check `API_REFERENCE_GUIDE.md` for detailed documentation.

---

## 📈 Next Steps

After exploring locally:

1. **Customize for Your Needs**
   - Modify templates in `/templates`
   - Update styles in `/static/css`
   - Add new endpoints in `app.py`

2. **Connect Real Database**
   - Update `models/database.py`
   - Configure PostgreSQL/MySQL
   - Run database migrations

3. **Add Team Users**
   - Create user accounts
   - Set up roles and permissions
   - Configure team settings

4. **Deploy to Cloud**
   - Deploy to Heroku, AWS, or Google Cloud
   - Set up production database
   - Configure Gemini API key
   - Set up monitoring

5. **Integrate with Tools**
   - Email integration
   - Slack notifications
   - Calendar sync
   - Third-party apps

---

## 🎯 Salesforce Features Included

All implemented and ready to use:

| Feature | Endpoints | Status |
|---------|-----------|--------|
| **Leads** | 4 | ✅ Active |
| **Contacts** | 4 | ✅ Active |
| **Deals** | 4 | ✅ Active |
| **Tasks** | 8 | ✅ Active |
| **Events** | 5 | ✅ Active |
| **Reports** | 5 | ✅ Active |
| **Approvals** | 4 | ✅ Active |
| **Workflows** | 4 | ✅ Active |
| **Documents** | 2 | ✅ Active |
| **Forecasting** | 2 | ✅ Active |
| **Chatter** | 5 | ✅ Active |
| **User Profiles** | 6 | ✅ Active |
| **Notifications** | 4 | ✅ Active |
| **Activities** | 3 | ✅ Active |

---

## 📞 Need Help?

Check these files for more info:
- 📖 `README.md` - Full project overview
- 📚 `README_V2.md` - Version 2 features
- 🔗 `API_REFERENCE_GUIDE.md` - All 50+ endpoints
- 🏗️ `ARCHITECTURE_GUIDE.md` - System design
- 🎨 `SALESFORCE_FEATURES_COMPLETE.md` - Feature details
- 📋 `DELIVERY_SUMMARY.md` - What's included

---

## 🎉 You're Ready!

Everything is set up and ready to go. Open `http://localhost:5000` and start exploring your amazing enterprise CRM! 

Enjoy your professional Salesforce-level CRM with Material Design 3! 🚀

---

**GeminiCRM Pro v2.0**
*An enterprise-grade CRM powered by AI*

