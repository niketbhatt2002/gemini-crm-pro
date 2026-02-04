/**
 * GeminiCRM Pro - Main JavaScript
 * Core application functionality
 */

// ==================== Utility Functions ====================

function formatCurrency(amount) {
    if (amount >= 1000000) {
        return '$' + (amount / 1000000).toFixed(1) + 'M';
    }
    if (amount >= 1000) {
        return '$' + (amount / 1000).toFixed(0) + 'K';
    }
    return '$' + amount.toLocaleString();
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((date - now) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays > 0 && diffDays < 7) return `In ${diffDays} days`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatStage(stage) {
    const stages = {
        lead: 'Lead',
        qualified: 'Qualified',
        proposal: 'Proposal',
        negotiation: 'Negotiation',
        closed_won: 'Won',
        closed_lost: 'Lost'
    };
    return stages[stage] || stage;
}

function getAvatarColor(name) {
    const colors = ['#4285f4', '#34a853', '#fbbc04', '#ea4335', '#9334e6', '#00acc1', '#ff6d01'];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="material-icons-round">${type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info'}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== Loading Overlay ====================

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

// ==================== Modal Functions ====================

function showApiModal() {
    document.getElementById('apiKeyModal').classList.add('active');
}

function hideApiModal() {
    document.getElementById('apiKeyModal').classList.remove('active');
}

async function saveApiKey() {
    const input = document.getElementById('apiKeyInput');
    const apiKey = input.value.trim();
    
    if (!apiKey) {
        showToast('Please enter an API key', 'error');
        return;
    }
    
    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const data = await res.json();
        
        if (data.success) {
            showToast('API key saved successfully!', 'success');
            hideApiModal();
            checkApiStatus();
        } else {
            showToast(data.error || 'Failed to save API key', 'error');
        }
    } catch (error) {
        showToast('Failed to save API key', 'error');
    }
}

// ==================== API Status ====================

async function checkApiStatus() {
    try {
        const res = await fetch('/api/config/status');
        const data = await res.json();
        
        const statusEl = document.getElementById('apiStatus');
        
        if (data.configured) {
            statusEl.classList.add('connected');
            statusEl.classList.remove('disconnected');
            statusEl.querySelector('.status-text').textContent = 'Connected';
        } else {
            statusEl.classList.add('disconnected');
            statusEl.classList.remove('connected');
            statusEl.querySelector('.status-text').textContent = 'Not Connected';
            // Show modal if not configured
            showApiModal();
        }
    } catch (error) {
        console.error('Error checking API status:', error);
    }
}

// ==================== Sidebar ====================

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// ==================== AI Chat ====================

function openAIChat() {
    document.getElementById('aiChatPanel').classList.add('active');
}

function closeAIChat() {
    document.getElementById('aiChatPanel').classList.remove('active');
}

async function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesContainer = document.getElementById('aiChatMessages');
    
    // Add user message
    messagesContainer.innerHTML += `
        <div class="ai-message user">
            <div class="ai-bubble">${escapeHtml(message)}</div>
        </div>
    `;
    
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Add loading indicator
    const loadingId = 'loading-' + Date.now();
    messagesContainer.innerHTML += `
        <div class="ai-message assistant" id="${loadingId}">
            <div class="ai-avatar">
                <span class="material-icons-round">auto_awesome</span>
            </div>
            <div class="ai-bubble">
                <div class="loading-inline"><div class="spinner small"></div></div>
            </div>
        </div>
    `;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await res.json();
        
        // Remove loading indicator
        document.getElementById(loadingId).remove();
        
        // Add assistant response
        const response = data.response || data.error || 'Sorry, I encountered an error.';
        messagesContainer.innerHTML += `
            <div class="ai-message assistant">
                <div class="ai-avatar">
                    <span class="material-icons-round">auto_awesome</span>
                </div>
                <div class="ai-bubble">${formatAIResponse(response)}</div>
            </div>
        `;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        messagesContainer.innerHTML += `
            <div class="ai-message assistant">
                <div class="ai-avatar">
                    <span class="material-icons-round">auto_awesome</span>
                </div>
                <div class="ai-bubble">Sorry, I encountered an error. Please try again.</div>
            </div>
        `;
    }
}

function formatAIResponse(text) {
    // Convert markdown-like formatting to HTML
    let html = escapeHtml(text);
    
    // Convert line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // Convert bullet points
    html = html.replace(/• /g, '• ');
    html = html.replace(/- /g, '• ');
    
    // Wrap in paragraph
    if (!html.startsWith('<p>')) {
        html = '<p>' + html + '</p>';
    }
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle enter key in AI chat
document.addEventListener('DOMContentLoaded', function() {
    const aiChatInput = document.getElementById('aiChatInput');
    if (aiChatInput) {
        aiChatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendAIMessage();
            }
        });
    }
});

// ==================== Global Search ====================

let searchTimeout;

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('active');
                return;
            }
            
            searchTimeout = setTimeout(() => performSearch(query), 300);
        });
        
        searchInput.addEventListener('blur', function() {
            setTimeout(() => searchResults.classList.remove('active'), 200);
        });
    }
});

async function performSearch(query) {
    const searchResults = document.getElementById('searchResults');
    
    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (data.results.length === 0) {
            searchResults.innerHTML = '<div class="empty-state small"><p>No results found</p></div>';
        } else {
            let html = '<div class="list">';
            data.results.forEach(result => {
                html += `
                    <div class="list-item" onclick="navigateToResult('${result.type}', '${result.id}')">
                        <span class="material-icons-outlined">${result.icon}</span>
                        <div class="list-item-content">
                            <div class="list-item-title">${result.title}</div>
                            <div class="list-item-subtitle">${result.subtitle}</div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            searchResults.innerHTML = html;
        }
        
        searchResults.classList.add('active');
    } catch (error) {
        console.error('Search error:', error);
    }
}

function navigateToResult(type, id) {
    const routes = {
        contact: `/contacts?id=${id}`,
        lead: `/leads?id=${id}`,
        deal: `/deals?id=${id}`
    };
    window.location.href = routes[type] || '/';
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
});
