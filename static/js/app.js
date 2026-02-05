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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || createToastContainer();
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

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ==================== Loading Overlay ====================

function showLoading() {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// ==================== Modal Functions ====================

function showApiModal() {
    let modal = document.getElementById('apiKeyModal');
    if (!modal) {
        createApiModal();
        modal = document.getElementById('apiKeyModal');
    }
    modal.classList.add('active');
}

function hideApiModal() {
    const modal = document.getElementById('apiKeyModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function createApiModal() {
    const modal = document.createElement('div');
    modal.id = 'apiKeyModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-backdrop" onclick="hideApiModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Configure Gemini API</h3>
                <button class="close-btn" onclick="hideApiModal()">
                    <span class="material-icons-round">close</span>
                </button>
            </div>
            <div class="modal-body">
                <p>To use AI features, please enter your Google Gemini API key:</p>
                <input type="password" id="apiKeyInput" class="form-control" placeholder="Enter API key...">
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="hideApiModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveApiKey()">Save API Key</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function saveApiKey() {
    const input = document.getElementById('apiKeyInput');
    const apiKey = input.value.trim();
    
    if (!apiKey) {
        showToast('Please enter an API key', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const data = await res.json();
        hideLoading();
        
        if (data.success) {
            showToast('API key saved successfully!', 'success');
            hideApiModal();
            checkApiStatus();
        } else {
            showToast(data.error || 'Failed to save API key', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Failed to save API key', 'error');
        console.error('Error:', error);
    }
}

// ==================== API Status ====================

async function checkApiStatus() {
    try {
        const res = await fetch('/api/config/status');
        const data = await res.json();
        
        const statusEl = document.getElementById('apiStatus');
        
        if (statusEl) {
            if (data.configured) {
                statusEl.classList.add('connected');
                statusEl.classList.remove('disconnected');
                const textEl = statusEl.querySelector('.status-text');
                if (textEl) textEl.textContent = 'Connected';
            } else {
                statusEl.classList.add('disconnected');
                statusEl.classList.remove('connected');
                const textEl = statusEl.querySelector('.status-text');
                if (textEl) textEl.textContent = 'Not Connected';
                showApiModal();
            }
        }
    } catch (error) {
        console.error('Error checking API status:', error);
    }
}

// ==================== Sidebar ====================

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// ==================== AI Chat ====================

function openAIChat() {
    let panel = document.getElementById('aiChatPanel');
    if (!panel) {
        createAIChatPanel();
        panel = document.getElementById('aiChatPanel');
    }
    panel.classList.add('active');
}

function closeAIChat() {
    const panel = document.getElementById('aiChatPanel');
    if (panel) {
        panel.classList.remove('active');
    }
}

function createAIChatPanel() {
    const panel = document.createElement('div');
    panel.id = 'aiChatPanel';
    panel.className = 'ai-chat-panel';
    panel.innerHTML = `
        <div class="ai-chat-header">
            <h3>AI Assistant</h3>
            <button onclick="closeAIChat()" class="close-btn">
                <span class="material-icons-round">close</span>
            </button>
        </div>
        <div id="aiChatMessages" class="ai-chat-messages"></div>
        <div class="ai-chat-footer">
            <input type="text" id="aiChatInput" class="form-control" placeholder="Ask me anything...">
            <button onclick="sendAIMessage()" class="btn-icon">
                <span class="material-icons-round">send</span>
            </button>
        </div>
    `;
    document.body.appendChild(panel);
}

async function sendAIMessage() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesContainer = document.getElementById('aiChatMessages');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-message user';
    userMsg.innerHTML = `<div class="ai-bubble">${escapeHtml(message)}</div>`;
    messagesContainer.appendChild(userMsg);
    
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Add loading indicator
    const loadingId = 'loading-' + Date.now();
    const loadingMsg = document.createElement('div');
    loadingMsg.id = loadingId;
    loadingMsg.className = 'ai-message assistant';
    loadingMsg.innerHTML = `
        <div class="ai-avatar">
            <span class="material-icons-round">auto_awesome</span>
        </div>
        <div class="ai-bubble">
            <div class="loading-inline"><div class="spinner small"></div></div>
        </div>
    `;
    messagesContainer.appendChild(loadingMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    showLoading();
    
    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        hideLoading();
        const data = await res.json();
        
        // Remove loading indicator
        const loading = document.getElementById(loadingId);
        if (loading) loading.remove();
        
        // Add assistant response
        const response = data.response || data.error || 'Sorry, I encountered an error.';
        const assistantMsg = document.createElement('div');
        assistantMsg.className = 'ai-message assistant';
        assistantMsg.innerHTML = `
            <div class="ai-avatar">
                <span class="material-icons-round">auto_awesome</span>
            </div>
            <div class="ai-bubble">${formatAIResponse(response)}</div>
        `;
        messagesContainer.appendChild(assistantMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        hideLoading();
        const loading = document.getElementById(loadingId);
        if (loading) loading.remove();
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'ai-message assistant';
        errorMsg.innerHTML = `
            <div class="ai-avatar">
                <span class="material-icons-round">auto_awesome</span>
            </div>
            <div class="ai-bubble">Sorry, I encountered an error. Please try again.</div>
        `;
        messagesContainer.appendChild(errorMsg);
        console.error('Chat error:', error);
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

// ==================== Global Search ====================

let searchTimeout;

function initSearch() {
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchResults) {
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
}

async function performSearch(query) {
    const searchResults = document.getElementById('searchResults');
    
    if (!searchResults) return;
    
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
                            <div class="list-item-title">${escapeHtml(result.title)}</div>
                            <div class="list-item-subtitle">${escapeHtml(result.subtitle)}</div>
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
        showToast('Search failed', 'error');
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
    initSearch();
    
    // Add AI chat button if not exists
    if (!document.getElementById('aiChatPanel')) {
        const fab = document.createElement('button');
        fab.id = 'aiChatFab';
        fab.className = 'fab fab-primary';
        fab.innerHTML = '<span class="material-icons-round">auto_awesome</span>';
        fab.onclick = () => openAIChat();
        document.body.appendChild(fab);
    }
});

// Handle AI chat input enter key
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const aiChatInput = document.getElementById('aiChatInput');
        if (aiChatInput) {
            aiChatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendAIMessage();
                }
            });
        }
    }, 500);
});
