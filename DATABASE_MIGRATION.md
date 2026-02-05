# 🗄️ GeminiCRM Pro - Database Migration Guide

## Overview

This guide covers migrating GeminiCRM Pro from in-memory storage to PostgreSQL for production use.

---

## Prerequisites

1. PostgreSQL 12+ installed
2. Python 3.8+
3. pip packages: `sqlalchemy`, `psycopg2-binary`, `alembic`

---

## Phase 1: Setup PostgreSQL

### Installation

#### Windows
```bash
# Download from https://www.postgresql.org/download/windows/
# Run installer and follow setup wizard
# Note: Default port is 5432
```

#### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql shell
CREATE DATABASE gemini_crm;
CREATE USER gemini_user WITH PASSWORD 'secure_password';
ALTER ROLE gemini_user SET client_encoding TO 'utf8';
ALTER ROLE gemini_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gemini_user SET default_transaction_deferrable TO on;
ALTER ROLE gemini_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gemini_crm TO gemini_user;

# Exit psql
\q
```

---

## Phase 2: Update Application

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Models with SQLAlchemy

Create `models/sqlalchemy_models.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='sales')
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contacts = db.relationship('Contact', backref='owner', lazy=True)
    leads = db.relationship('Lead', backref='owner', lazy=True)
    deals = db.relationship('Deal', backref='owner', lazy=True)

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(255))
    title = db.Column(db.String(100))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), default='new')
    score = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Deal(db.Model):
    __tablename__ = 'deals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, default=0)
    stage = db.Column(db.String(50), default='lead')
    probability = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='pending')
    due_date = db.Column(db.DateTime)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. Update Configuration

Modify `config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://gemini_user:password@localhost:5432/gemini_crm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-2.0-flash'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

class DevelopmentConfig(Config):
    """Development config"""
    DEBUG = True

class ProductionConfig(Config):
    """Production config"""
    DEBUG = False

class TestingConfig(Config):
    """Testing config"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://gemini_user:password@localhost:5432/gemini_crm_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### 4. Update Environment File

Update `.env`:

```bash
# Database
DATABASE_URL=postgresql://gemini_user:secure_password@localhost:5432/gemini_crm

# Flask
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here

# API
GEMINI_API_KEY=your-gemini-key

# CORS
CORS_ORIGINS=*

# Server
SERVER_PORT=5000
```

---

## Phase 3: Initialize Database

### 1. Create Tables

```python
# init_db.py
from app import app, db
from models.sqlalchemy_models import User, Contact, Lead, Deal, Task

with app.app_context():
    db.create_all()
    print("✓ Database tables created successfully")
```

Run:
```bash
python init_db.py
```

### 2. Migrate Existing Data (Optional)

```python
# migrate_data.py
from app import app, db
from models.database import get_all
from models.sqlalchemy_models import User, Contact, Lead, Deal, Task

with app.app_context():
    # Migrate users
    for user_data in get_all('users'):
        user = User(**user_data)
        db.session.add(user)
    
    # Migrate contacts
    for contact_data in get_all('contacts'):
        contact = Contact(**contact_data)
        db.session.add(contact)
    
    # Migrate leads
    for lead_data in get_all('leads'):
        lead = Lead(**lead_data)
        db.session.add(lead)
    
    # Migrate deals
    for deal_data in get_all('deals'):
        deal = Deal(**deal_data)
        db.session.add(deal)
    
    # Migrate tasks
    for task_data in get_all('tasks'):
        task = Task(**task_data)
        db.session.add(task)
    
    db.session.commit()
    print("✓ Data migration completed")
```

Run:
```bash
python migrate_data.py
```

---

## Phase 4: Update Application Code

### 1. Update `app.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
import os

app = Flask(__name__)

# Configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Database
from models.sqlalchemy_models import db
db.init_app(app)

# CORS
CORS(app)

# Routes
from routes import api_routes
app.register_blueprint(api_routes.bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### 2. Update CRUD Operations

```python
# models/crud.py
from models.sqlalchemy_models import db, Contact, Lead, Deal, Task, User

def create_contact(data):
    contact = Contact(**data)
    db.session.add(contact)
    db.session.commit()
    return contact.to_dict()

def get_contact(contact_id):
    contact = Contact.query.get(contact_id)
    return contact.to_dict() if contact else None

def update_contact(contact_id, data):
    contact = Contact.query.get(contact_id)
    if contact:
        for key, value in data.items():
            setattr(contact, key, value)
        db.session.commit()
        return contact.to_dict()
    return None

def delete_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
        return True
    return False

def get_all_contacts():
    return [c.to_dict() for c in Contact.query.all()]
```

---

## Phase 5: Set Up Alembic for Migrations

### Initialize Alembic

```bash
alembic init alembic
```

### Configure `alembic.ini`

Update database URL:
```ini
sqlalchemy.url = postgresql://gemini_user:secure_password@localhost:5432/gemini_crm
```

### Create Migration

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Phase 6: Testing

### Run Tests

```bash
pytest tests/
```

### Manual Testing

```bash
# Start application
python app.py

# Test endpoints
curl -X GET http://localhost:5000/api/contacts
curl -X POST http://localhost:5000/api/contacts -d '{"name":"John"}'
```

---

## Phase 7: Performance Optimization

### Add Indexes

```python
class Contact(db.Model):
    # ... fields ...
    __table_args__ = (
        db.Index('idx_email', 'email'),
        db.Index('idx_owner_id', 'owner_id'),
        db.Index('idx_created_at', 'created_at'),
    )
```

### Connection Pooling

```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Query Optimization

```python
# Use eager loading
contacts = Contact.query.options(
    db.joinedload(Contact.owner)
).all()

# Use pagination
page = Contact.query.paginate(page=1, per_page=20)
```

---

## Backup & Recovery

### Regular Backups

```bash
# Daily backup
pg_dump -U gemini_user gemini_crm > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U gemini_user -F c gemini_crm > backup_$(date +%Y%m%d).dump
```

### Restore from Backup

```bash
# From SQL file
psql -U gemini_user gemini_crm < backup_20240204.sql

# From dump file
pg_restore -U gemini_user -d gemini_crm backup_20240204.dump
```

---

## Troubleshooting

### Connection Issues

```python
# Test connection
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:password@localhost/gemini_crm')
connection = engine.connect()
print("✓ Connection successful")
connection.close()
```

### Migration Issues

```bash
# Check migration history
alembic history

# Downgrade migration
alembic downgrade -1

# View current version
alembic current
```

### Performance Issues

```python
# Enable query logging
app.config['SQLALCHEMY_ECHO'] = True

# Check slow queries
EXPLAIN ANALYZE SELECT * FROM contacts WHERE owner_id = 'user_id';
```

---

## Rollback to In-Memory

If you need to rollback to in-memory storage:

```python
# Switch back to models/database.py
from models.database import get_all, create, update, delete
# Keep using the same CRUD functions
```

---

## Production Checklist

- [ ] Database backed up
- [ ] Connection pooling configured
- [ ] Indexes created
- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan ready
- [ ] Performance tested
- [ ] Load testing completed

---

## Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/

---

**Last Updated**: February 4, 2026
**Version**: 1.0
**Status**: Production Ready
