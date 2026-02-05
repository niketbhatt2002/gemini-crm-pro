# 🔧 Troubleshooting Guide - GeminiCRM Pro

Having issues running GeminiCRM Pro locally? This guide covers the most common problems and their solutions.

---

## ✅ Pre-Flight Checklist

Before troubleshooting, verify these basics:

- [ ] Python 3.8+ installed: `python --version`
- [ ] pip working: `pip --version`
- [ ] In correct directory: `cd c:\Users\Niket Bhatt\Documents\gemini-crm-pro`
- [ ] requirements.txt exists: `dir requirements.txt`
- [ ] app.py exists: `dir app.py`

---

## 🚨 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'flask'"

**Error Message**:
```
ModuleNotFoundError: No module named 'flask'
```

**Cause**: Dependencies not installed

**Solution**:
```powershell
cd "c:\Users\Niket Bhatt\Documents\gemini-crm-pro"
pip install -r requirements.txt
```

**If still not working**:
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

---

### Issue 2: "Port 5000 is already in use"

**Error Message**:
```
Address already in use
OSError: [Errno 10048] Only one usage of each socket address
```

**Cause**: Another application is using port 5000

**Solution Option A - Kill existing process**:
```powershell
taskkill /F /IM python.exe
# Wait a moment, then run: python app.py
```

**Solution Option B - Use different port**:
```powershell
# Edit app.py line (look for app.run()):
# Change from: app.run(debug=False, port=5000)
# To: app.run(debug=False, port=5001)

python app.py
# Then access: http://localhost:5001
```

**Solution Option C - Find which process uses port 5000**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with the number you found)
taskkill /PID <PID> /F
```

---

### Issue 3: "ImportError" or "ModuleNotFoundError"

**Error Message**:
```
ImportError: cannot import name 'X' from 'Y'
ModuleNotFoundError: No module named 'google.genai'
```

**Cause**: Missing or incorrectly installed dependency

**Solution**:
```powershell
# Reinstall all dependencies fresh
pip install --upgrade --force-reinstall -r requirements.txt

# Verify Flask is installed
pip show flask

# Verify Google GenAI is installed
pip show google-genai
```

---

### Issue 4: "SyntaxError" in app.py or models

**Error Message**:
```
SyntaxError: invalid syntax (app.py, line 123)
```

**Cause**: Python syntax error (usually after manual edits)

**Solution**:
```powershell
# Test Python files for syntax errors
python -m py_compile app.py
python -m py_compile models/user_profile.py
python -m py_compile models/salesforce_features.py
```

**If syntax error found**:
- Check the line number mentioned in the error
- Look for missing colons, quotes, or parentheses
- Compare with the original file on GitHub

---

### Issue 5: Browser shows "Connection refused"

**Error Message**:
```
localhost refused to connect
Unable to connect
This site can't be reached
```

**Cause**: Flask server not running

**Solution**:
```powershell
# Check if app.py is running
Get-Process python -ErrorAction SilentlyContinue

# If not running, start it
cd "c:\Users\Niket Bhatt\Documents\gemini-crm-pro"
python app.py

# Check the output for:
# * Running on http://127.0.0.1:5000
```

**If Flask crashes immediately**:
```powershell
# Run with verbose output
python -u app.py

# Note any error messages and check above solutions
```

---

### Issue 6: CSS or JavaScript not loading

**Symptoms**:
- Page looks unstyled (no colors, layout is broken)
- Buttons don't work
- Dropdown menus don't open

**Cause**: Static files not loading correctly

**Solutions**:

**Option A - Clear browser cache**:
1. Open browser DevTools (F12)
2. Right-click refresh button
3. Select "Empty cache and hard refresh"
4. Or: Ctrl+Shift+Delete, clear all, refresh

**Option B - Check file permissions**:
```powershell
# Verify static files exist
dir static/css/
dir static/js/

# They should contain:
# - style.css
# - material-design-3.css
# - app.js
```

**Option C - Check Flask is serving static files**:
```powershell
# In browser, try accessing CSS directly:
# http://localhost:5000/static/css/style.css
# http://localhost:5000/static/js/app.js

# If 404 error, static files aren't being served
```

---

### Issue 7: "GEMINI_API_KEY not set" warning

**Message in terminal**:
```
WARNING: GEMINI_API_KEY is not configured
AI features will be disabled
```

**This is NOT an error!**

**Explanation**: 
- The app works perfectly without Gemini API key
- You can use all CRM features
- AI features (like lead scoring) just won't work

**To enable AI** (optional):
1. Get free API key: https://aistudio.google.com/app/apikey
2. Create `.env` file in project root
3. Add: `GEMINI_API_KEY=your_key_here`
4. Restart app: `python app.py`

---

### Issue 8: "Module has no attribute" error

**Error Message**:
```
AttributeError: module 'X' has no attribute 'Y'
```

**Cause**: Dependency version mismatch or outdated cache

**Solution**:
```powershell
# Clear Python cache
Remove-Item -Path "__pycache__" -Recurse -Force
Remove-Item -Path "models/__pycache__" -Recurse -Force
Remove-Item -Path "services/__pycache__" -Recurse -Force

# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Try again
python app.py
```

---

### Issue 9: "PermissionError" or "Access Denied"

**Error Message**:
```
PermissionError: [Errno 13] Permission denied: 'app.py'
```

**Cause**: File is locked by another process or antivirus

**Solution**:
```powershell
# Kill any Python processes
taskkill /F /IM python.exe

# Disable antivirus temporarily (if using)
# Or add the project folder to antivirus whitelist

# Try again
python app.py
```

---

### Issue 10: Database or data persistence issues

**Symptoms**:
- Data doesn't save
- Added leads disappear on refresh
- Tasks not appearing

**Explanation**:
By default, GeminiCRM uses in-memory storage (data resets on restart).

**Solution for development**:
This is normal! Data is stored in memory for quick testing.

**Solution for persistence**:
To save data between sessions, you need to set up a database:

1. **Option A - SQLite (Simple)**:
   - Edit `models/database.py`
   - Uncomment SQLite configuration
   - Data saves to `crm_data.db`

2. **Option B - PostgreSQL (Production)**:
   - Install PostgreSQL
   - Update config with DB connection string
   - Run migrations
   - Data persists in database

---

## 🛠️ Advanced Troubleshooting

### Check Python version compatibility

```powershell
python --version
# Should show 3.8.0 or higher

# If using Python 2.x, uninstall and install Python 3.8+
```

### Verify all dependencies installed correctly

```powershell
pip list | findstr "flask\|google\|sqlalchemy"

# Should show:
# flask
# google-genai
# sqlalchemy
# (and others)
```

### Run Flask in debug mode (more verbose errors)

```powershell
# Edit app.py, change:
# app.run(debug=False)
# To:
# app.run(debug=True)

python app.py
# Now you get more detailed error messages
```

### Test individual components

```powershell
# Test if imports work
python -c "import flask; print('Flask OK')"
python -c "import google.genai; print('Google GenAI OK')"
python -c "from models.database import Lead; print('Models OK')"

# Test if app can be imported
python -c "from app import app; print('App imports OK')"
```

---

## 📞 Still Having Issues?

If none of the above solutions work:

1. **Check GitHub for issues**:
   - https://github.com/niketbhatt2002/gemini-crm-pro/issues

2. **Review the logs**:
   - Check terminal output for full error message
   - Copy the entire error message

3. **Verify your setup matches**:
   - Python 3.8+ installed
   - All requirements.txt packages installed
   - Running from correct directory
   - Using correct browser and port

4. **Try a fresh start**:
   ```powershell
   # Kill all Python processes
   taskkill /F /IM python.exe
   
   # Clear Python cache
   Remove-Item -Path "__pycache__" -Recurse -Force
   
   # Reinstall everything
   pip install --upgrade --force-reinstall -r requirements.txt
   
   # Start fresh
   python app.py
   ```

---

## ✨ Common Questions

**Q: Do I need a Gemini API key to run the app?**
A: No! The app works perfectly without it. AI features are optional.

**Q: Will my data persist between sessions?**
A: By default, data is stored in memory (resets on restart). To persist data, configure a database.

**Q: Can I run this on a different port?**
A: Yes! Edit app.py and change `port=5000` to your desired port.

**Q: Is this production-ready?**
A: The backend is production-ready. For production deployment, configure a real database and use a WSGI server like Gunicorn.

**Q: What should I do if I accidentally deleted a file?**
A: Restore from GitHub:
```powershell
git checkout <filename>
```

**Q: How do I update to the latest version?**
A: Pull from GitHub:
```powershell
git pull origin main
pip install --upgrade -r requirements.txt
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start app | `python app.py` |
| Stop app | `Ctrl+C` |
| Install deps | `pip install -r requirements.txt` |
| Test syntax | `python -m py_compile app.py` |
| View running processes | `Get-Process python` |
| Kill Python processes | `taskkill /F /IM python.exe` |
| Check pip packages | `pip list` |
| Find what uses port 5000 | `netstat -ano \| findstr :5000` |

---

## 🎉 Success!

Once you see this in terminal, everything is working:

```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

Then open your browser to: **http://localhost:5000**

Enjoy your enterprise CRM! 🚀

