"""
GeminiCRM Pro - API Middleware & Rate Limiting
Advanced API monitoring, rate limiting, and security
"""
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import hashlib
import uuid

# ==================== RATE LIMITING ====================

class RateLimiter:
    """Rate limiting system"""
    
    def __init__(self):
        self.limits = {}  # user_id -> {timestamp -> count}
        self.config = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000
        }
    
    def check_rate_limit(self, user_id):
        """Check if user is within rate limits"""
        now = datetime.now()
        user_limits = self.limits.get(user_id, {})
        
        # Clean old entries
        cutoff_time = now - timedelta(days=1)
        self.limits[user_id] = {
            ts: count for ts, count in user_limits.items()
            if datetime.fromisoformat(ts) > cutoff_time
        }
        
        # Check minute limit
        minute_ago = (now - timedelta(minutes=1)).isoformat()
        minute_requests = len([t for t in self.limits[user_id].keys() if t > minute_ago])
        
        if minute_requests >= self.config['requests_per_minute']:
            return False, 'Rate limit exceeded (per minute)'
        
        # Check hour limit
        hour_ago = (now - timedelta(hours=1)).isoformat()
        hour_requests = len([t for t in self.limits[user_id].keys() if t > hour_ago])
        
        if hour_requests >= self.config['requests_per_hour']:
            return False, 'Rate limit exceeded (per hour)'
        
        # Check day limit
        day_ago = (now - timedelta(days=1)).isoformat()
        day_requests = len([t for t in self.limits[user_id].keys() if t > day_ago])
        
        if day_requests >= self.config['requests_per_day']:
            return False, 'Rate limit exceeded (per day)'
        
        return True, 'OK'
    
    def record_request(self, user_id):
        """Record API request"""
        if user_id not in self.limits:
            self.limits[user_id] = {}
        
        self.limits[user_id][datetime.now().isoformat()] = 1
    
    def get_usage(self, user_id):
        """Get user's API usage"""
        now = datetime.now()
        user_limits = self.limits.get(user_id, {})
        
        minute_ago = (now - timedelta(minutes=1)).isoformat()
        hour_ago = (now - timedelta(hours=1)).isoformat()
        day_ago = (now - timedelta(days=1)).isoformat()
        
        return {
            'minute': len([t for t in user_limits.keys() if t > minute_ago]),
            'hour': len([t for t in user_limits.keys() if t > hour_ago]),
            'day': len([t for t in user_limits.keys() if t > day_ago]),
            'limits': self.config
        }

# ==================== API MONITORING ====================

class APIMonitor:
    """Monitor API usage and performance"""
    
    def __init__(self):
        self.request_log = []
        self.error_log = []
        self.performance_metrics = defaultdict(list)
    
    def log_request(self, user_id, endpoint, method, status_code, response_time_ms):
        """Log API request"""
        self.request_log.append({
            'user_id': user_id,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'timestamp': datetime.now().isoformat()
        })
        
        self.performance_metrics[endpoint].append(response_time_ms)
    
    def log_error(self, user_id, endpoint, method, error_message):
        """Log API error"""
        self.error_log.append({
            'user_id': user_id,
            'endpoint': endpoint,
            'method': method,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_endpoint_stats(self, endpoint):
        """Get statistics for endpoint"""
        metrics = self.performance_metrics.get(endpoint, [])
        
        if not metrics:
            return None
        
        return {
            'endpoint': endpoint,
            'total_requests': len(metrics),
            'avg_response_time_ms': round(sum(metrics) / len(metrics), 2),
            'min_response_time_ms': min(metrics),
            'max_response_time_ms': max(metrics),
            'p95_response_time_ms': sorted(metrics)[int(len(metrics) * 0.95)] if metrics else 0
        }
    
    def get_health_status(self):
        """Get API health status"""
        if not self.request_log:
            return {'status': 'unknown'}
        
        last_24h = datetime.now() - timedelta(hours=24)
        recent_requests = [r for r in self.request_log if datetime.fromisoformat(r['timestamp']) > last_24h]
        recent_errors = [e for e in self.error_log if datetime.fromisoformat(e['timestamp']) > last_24h]
        
        total = len(recent_requests)
        success = len([r for r in recent_requests if r['status_code'] < 400])
        
        error_rate = (len(recent_errors) / total * 100) if total > 0 else 0
        
        status = 'healthy' if error_rate < 5 else 'degraded' if error_rate < 10 else 'unhealthy'
        
        return {
            'status': status,
            'total_requests_24h': total,
            'error_rate_percent': round(error_rate, 2),
            'errors_24h': len(recent_errors)
        }
    
    def get_top_endpoints(self, limit=10):
        """Get top endpoints by request count"""
        endpoint_counts = defaultdict(int)
        
        for request in self.request_log:
            endpoint_counts[request['endpoint']] += 1
        
        return sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_error_rate_by_endpoint(self):
        """Get error rate for each endpoint"""
        endpoint_stats = defaultdict(lambda: {'total': 0, 'errors': 0})
        
        for request in self.request_log:
            endpoint = request['endpoint']
            endpoint_stats[endpoint]['total'] += 1
            if request['status_code'] >= 400:
                endpoint_stats[endpoint]['errors'] += 1
        
        return {
            endpoint: {
                'total': stats['total'],
                'errors': stats['errors'],
                'error_rate_percent': round((stats['errors'] / stats['total'] * 100) if stats['total'] > 0 else 0, 2)
            }
            for endpoint, stats in endpoint_stats.items()
        }

# ==================== API KEY MANAGEMENT ====================

class APIKey:
    """API Key model"""
    
    def __init__(self, data):
        self.id = data.get('id', str(uuid.uuid4()))
        self.user_id = data.get('user_id')
        self.key = data.get('key', self._generate_key())
        self.name = data.get('name', 'API Key')
        self.is_active = data.get('is_active', True)
        self.last_used = data.get('last_used')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.expires_at = data.get('expires_at')
    
    @staticmethod
    def _generate_key():
        """Generate secure API key"""
        return 'gcrm_' + hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'key_preview': f"{self.key[:8]}...{self.key[-4:]}",
            'name': self.name,
            'is_active': self.is_active,
            'last_used': self.last_used,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }

class APIKeyManager:
    """Manage API keys"""
    
    def __init__(self):
        self.keys = {}  # key -> api_key_data
        self.user_keys = defaultdict(list)  # user_id -> [key_ids]
    
    def create_key(self, user_id, name=None, expires_in_days=365):
        """Create new API key"""
        api_key = APIKey({
            'user_id': user_id,
            'name': name or f'API Key {len(self.user_keys[user_id]) + 1}',
            'expires_at': (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        })
        
        self.keys[api_key.key] = api_key.to_dict()
        self.keys[api_key.key]['full_key'] = api_key.key
        self.user_keys[user_id].append(api_key.id)
        
        return api_key
    
    def get_key(self, api_key):
        """Get key info"""
        return self.keys.get(api_key)
    
    def validate_key(self, api_key):
        """Validate API key"""
        key_data = self.keys.get(api_key)
        
        if not key_data:
            return False, 'Invalid API key'
        
        if not key_data.get('is_active'):
            return False, 'API key is disabled'
        
        if key_data.get('expires_at'):
            expires_at = datetime.fromisoformat(key_data['expires_at'])
            if datetime.now() > expires_at:
                return False, 'API key has expired'
        
        return True, key_data.get('user_id')
    
    def revoke_key(self, api_key):
        """Revoke API key"""
        if api_key in self.keys:
            self.keys[api_key]['is_active'] = False
            return True
        return False
    
    def get_user_keys(self, user_id):
        """Get all keys for user"""
        key_ids = self.user_keys.get(user_id, [])
        return [self.keys[kid] for kid in key_ids if kid in self.keys]

# ==================== AUDIT LOG ====================

class AuditLog:
    """Audit logging for compliance and security"""
    
    def __init__(self):
        self.logs = []
    
    def log_action(self, user_id, action, resource_type, resource_id, changes=None, status='success'):
        """Log user action"""
        self.logs.append({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'changes': changes,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_user_activity(self, user_id, limit=100):
        """Get user activity log"""
        return [log for log in self.logs if log['user_id'] == user_id][-limit:]
    
    def get_resource_history(self, resource_type, resource_id):
        """Get resource change history"""
        return [log for log in self.logs if log['resource_type'] == resource_type and log['resource_id'] == resource_id]
    
    def get_all_logs(self, limit=1000):
        """Get all audit logs"""
        return self.logs[-limit:]
