"""
GeminiCRM Pro - Authentication & User Management
Implements JWT-based authentication with role-based access control
"""
import os
from datetime import datetime, timedelta
from functools import wraps
import uuid
import hashlib
import jwt
from flask import request, jsonify

# ==================== CONSTANTS ====================
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ==================== USER ROLES ====================
ROLES = {
    'admin': ['create', 'read', 'update', 'delete', 'manage_users', 'analytics'],
    'manager': ['create', 'read', 'update', 'delete', 'analytics'],
    'sales': ['create', 'read', 'update', 'analytics'],
    'viewer': ['read', 'analytics']
}

# ==================== IN-MEMORY USER STORAGE ====================
USERS_DB = {}  # user_id -> user_data
TOKENS_DB = {}  # token -> user_id
SESSIONS_DB = {}  # session_id -> session_data

# ==================== USER MODEL ====================

class User:
    """User model with authentication and permissions"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.email = data.get('email')
        self.username = data.get('username')
        self.password_hash = data.get('password_hash')
        self.first_name = data.get('first_name', '')
        self.last_name = data.get('last_name', '')
        self.role = data.get('role', 'sales')
        self.department = data.get('department', '')
        self.avatar_url = data.get('avatar_url', '')
        self.is_active = data.get('is_active', True)
        self.is_verified = data.get('is_verified', False)
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
        self.last_login = data.get('last_login', None)
        self.preferences = data.get('preferences', {})
        self.mfa_enabled = data.get('mfa_enabled', False)
        
    def to_dict(self):
        """Convert to dictionary (without sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}".strip(),
            'role': self.role,
            'department': self.department,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login': self.last_login,
            'preferences': self.preferences
        }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Verify password"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def has_permission(self, action):
        """Check if user has permission for action"""
        permissions = ROLES.get(self.role, [])
        return action in permissions
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

# ==================== JWT TOKEN MANAGEMENT ====================

def create_access_token(user_id, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES):
    """Create JWT access token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm=ALGORITHM)
    return token

def create_refresh_token(user_id):
    """Create JWT refresh token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithm=ALGORITHM)
    return token

def verify_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret-key'), algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user_from_token(token):
    """Extract user from token"""
    payload = verify_token(token)
    if not payload:
        return None
    user_id = payload.get('user_id')
    return USERS_DB.get(user_id)

# ==================== AUTHENTICATION DECORATORS ====================

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user = get_current_user_from_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = user
        return f(*args, **kwargs)
    
    return decorated

def permission_required(permission):
    """Decorator to check user permissions"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if not request.user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def role_required(role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.user.role != role and request.user.role != 'admin':
                return jsonify({'error': 'Insufficient role'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ==================== USER OPERATIONS ====================

def create_user(data):
    """Create new user"""
    if not data.get('email') or not data.get('password'):
        return None, 'Email and password required'
    
    # Check if user exists
    for user in USERS_DB.values():
        if user.get('email') == data.get('email'):
            return None, 'User already exists'
    
    user = User(data)
    user.set_password(data.get('password'))
    
    USERS_DB[user.id] = user.to_dict()
    USERS_DB[user.id]['password_hash'] = user.password_hash
    
    return user.to_dict(), None

def authenticate_user(email, password):
    """Authenticate user and return tokens"""
    # Find user by email
    user_data = None
    for uid, udata in USERS_DB.items():
        if udata.get('email') == email:
            user_data = udata
            user = User(user_data)
            break
    
    if not user_data or not user.check_password(password):
        return None, 'Invalid email or password'
    
    if not user.is_active:
        return None, 'User account is disabled'
    
    user.update_last_login()
    USERS_DB[user.id]['last_login'] = user.last_login
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }, None

def get_user_by_id(user_id):
    """Get user by ID"""
    user_data = USERS_DB.get(user_id)
    if user_data:
        return User(user_data).to_dict()
    return None

def get_all_users():
    """Get all users"""
    return [User(data).to_dict() for data in USERS_DB.values()]

def update_user(user_id, data):
    """Update user"""
    if user_id not in USERS_DB:
        return None, 'User not found'
    
    user_data = USERS_DB[user_id]
    
    # Allowed fields to update
    allowed_fields = ['first_name', 'last_name', 'department', 'avatar_url', 'preferences', 'mfa_enabled']
    
    for field in allowed_fields:
        if field in data:
            user_data[field] = data[field]
    
    user_data['updated_at'] = datetime.now().isoformat()
    USERS_DB[user_id] = user_data
    
    return User(user_data).to_dict(), None

def delete_user(user_id):
    """Delete user"""
    if user_id in USERS_DB:
        del USERS_DB[user_id]
        return True
    return False

def change_password(user_id, old_password, new_password):
    """Change user password"""
    if user_id not in USERS_DB:
        return False, 'User not found'
    
    user_data = USERS_DB[user_id]
    user = User(user_data)
    
    if not user.check_password(old_password):
        return False, 'Old password is incorrect'
    
    user.set_password(new_password)
    user_data['password_hash'] = user.password_hash
    user_data['updated_at'] = datetime.now().isoformat()
    
    USERS_DB[user_id] = user_data
    return True, 'Password changed successfully'

# ==================== INITIALIZATION ====================

def init_default_users():
    """Initialize with default admin and demo users"""
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@geminierms.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'department': 'Management'
        },
        {
            'username': 'manager',
            'email': 'manager@geminierms.com',
            'password': 'manager123',
            'first_name': 'Sales',
            'last_name': 'Manager',
            'role': 'manager',
            'department': 'Sales'
        },
        {
            'username': 'sales',
            'email': 'sales@geminierms.com',
            'password': 'sales123',
            'first_name': 'John',
            'last_name': 'Salesperson',
            'role': 'sales',
            'department': 'Sales'
        }
    ]
    
    for user_data in default_users:
        create_user(user_data)
