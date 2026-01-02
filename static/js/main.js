
// DOM Elements
const chatContainer = document.getElementById('chat-container');
const queryInput = document.getElementById('query-input');
const sendBtn = document.getElementById('send-btn');
const loading = document.getElementById('loading');

const exportBtn = document.getElementById('export-btn-panel');
const ttsBtn = document.getElementById('tts-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const settingsBtn = document.getElementById('settings-btn');
const historyModal = document.getElementById('history-modal');
const snippetsModal = document.getElementById('snippets-modal');
const settingsModal = document.getElementById('settings-modal');

const chatSidebar = document.getElementById('chat-sidebar');
const chatHistoryList = document.getElementById('chat-history-list');
const newChatBtn = document.getElementById('new-chat-btn');

// State
let currentSnippets = [];
let settings = {
    voiceVolume: 100,
    voiceRate: 0.9,
    voicePitch: 1.0,
    theme: 'dark'
};
// Authentication Guard - Redirect to login if not authenticated
(function () {
    const token = sessionStorage.getItem('access_token');
    // Only check on main pages, not on login page itself
    if (!token && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
        return;
    }
})();

// Global Variables
let currentChatId = null;
let chatHistory = [];
let currentDeleteChatId = null;
let ttsActive = false;
let currentUtterance = null;


// Auth Helper
async function authFetch(url, options = {}) {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        throw new Error("No token");
    }

    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + token;

    const response = await fetch(url, options);
    if (response.status === 401) {
        sessionStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error("Unauthorized");
    }
    return response;
}

// FUNCTION DEFINITIONS
function loadSettings() {
    const stored = sessionStorage.getItem('docuMindSettings');
    if (stored) {
        settings = { ...settings, ...JSON.parse(stored) };
        applySettings();
    }
}

function saveSettings() {
    sessionStorage.setItem('docuMindSettings', JSON.stringify(settings));
}

function applySettings() {
    document.getElementById('voice-volume').value = settings.voiceVolume;
    document.getElementById('voice-rate').value = settings.voiceRate;
    document.getElementById('voice-pitch').value = settings.voicePitch;
    document.getElementById('volume-value').textContent = settings.voiceVolume + '%';
    document.getElementById('rate-value').textContent = settings.voiceRate.toFixed(1) + 'x';
    document.getElementById('pitch-value').textContent = settings.voicePitch.toFixed(1) + 'x';

    document.body.className = 'theme-' + settings.theme;
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === settings.theme);
    });
}

function showError(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function addMessage(text, sender, citedFiles = [], confidenceScore = null, sourceSnippets = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = sender === 'user' ? 'You' : 'Assistant';

    const content = document.createElement('div');
    content.className = 'message-content';
    // Use Pre-wrap for raw text for now, we will add marked later
    content.style.whiteSpace = 'pre-wrap';
    content.textContent = text;

    messageDiv.appendChild(label);
    messageDiv.appendChild(content);

    // Confidence indicator removed as per user request (redundant with text response)
    /*
    if (sender === 'assistant' && confidenceScore !== null) {
        const confDiv = document.createElement('div');
        confDiv.className = 'confidence-indicator';
        let color = confidenceScore >= 80 ? '#4CAF50' : confidenceScore >= 50 ? '#FFC107' : '#f44336';
        confDiv.innerHTML = `<div class="conf-bar" style="width: ${confidenceScore}%; background: ${color};"></div><span>${confidenceScore}%</span>`;
        content.appendChild(confDiv);
    }
    */

    if (sender === 'assistant' && sourceSnippets && sourceSnippets.length > 0) {
        const btnWrap = document.createElement('div');
        btnWrap.className = 'snippet-actions';
        // Fix spacing between buttons
        btnWrap.style.display = 'flex';
        btnWrap.style.gap = '10px';

        const speakBtn = document.createElement('button');
        speakBtn.className = 'snippet-btn speak-btn';
        speakBtn.textContent = '🔊 Read';
        speakBtn.onclick = () => {
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                // If we were just reading, we stop.
                // If the user meant "read this instead", they'd click a DIFFERENT button,
                // but simpler logic for now: Click = Toggle Global Speech.
            } else {
                speakText(text);
            }
        };

        const srcBtn = document.createElement('button');
        srcBtn.className = 'snippet-btn';
        srcBtn.textContent = 'View Sources';
        srcBtn.onclick = () => showSourceSnippets(sourceSnippets);

        btnWrap.appendChild(speakBtn);
        btnWrap.appendChild(srcBtn);
        content.appendChild(btnWrap);
    }

    if (citedFiles && citedFiles.length > 0) {
        const citedDiv = document.createElement('div');
        citedDiv.className = 'cited-files';
        const label = document.createElement('div');
        label.className = 'cited-label';
        label.textContent = 'Sources:';
        citedDiv.appendChild(label);
        citedFiles.forEach(filename => {
            const chip = document.createElement('span');
            chip.className = 'file-chip';
            chip.textContent = filename;
            chip.onclick = () => downloadFile(filename);
            citedDiv.appendChild(chip);
        });
        content.appendChild(citedDiv);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    queryInput.value = '';
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    addMessage(query, 'user');
    loading.classList.add('active');
    sendBtn.disabled = true;

    // Auto-create chat if none active
    if (!currentChatId) {
        try {
            const res = await authFetch('/api/chats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: query.substring(0, 30) })
            });
            const chat = await res.json();
            currentChatId = chat.id;
            loadChatSessions();
        } catch (e) {
            console.error("Session creation error:", e);
        }
    }

    try {
        const response = await authFetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, chat_id: currentChatId })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.answer, 'assistant', data.cited_files, data.confidence_score, data.source_snippets);
            showToast('Response received', 'success');
            // Refresh sessions to update titles if first message
            loadChatSessions();
        } else {
            showError(data.error || 'Error occurred');
        }
    } catch (error) {
        showError('Failed to connect to server');
    } finally {
        loading.classList.remove('active');
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

async function loadChatSessions() {
    if (!chatHistoryList) return;
    try {
        const response = await authFetch('/api/chats');
        const chats = await response.json();
        chatHistoryList.innerHTML = '';

        if (chats.length === 0) {
            chatHistoryList.innerHTML = '<div class="loading-history">No history yet</div>';
            return;
        }

        chats.forEach(chat => {
            const item = document.createElement('div');
            item.className = `chat-session-item ${chat.id === currentChatId ? 'active' : ''}`;

            // Title Span
            const titleSpan = document.createElement('span');
            titleSpan.className = 'chat-session-title';
            titleSpan.textContent = chat.title || 'Untitled Chat';
            titleSpan.onclick = () => loadChat(chat.id);

            // Delete Button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-chat-btn';
            deleteBtn.innerHTML = '🗑️';
            deleteBtn.title = 'Delete Chat';
            deleteBtn.onclick = (e) => {
                e.stopPropagation(); // Prevent opening the chat
                deleteChat(chat.id, chat.title);
            };

            item.appendChild(titleSpan);
            item.appendChild(deleteBtn);
            chatHistoryList.appendChild(item);
        });
    } catch (e) {
        console.error("Load sessions error:", e);
    }
}

// Promise-based Modal Confirmation
function confirmDelete() {
    return new Promise((resolve) => {
        const modal = document.getElementById('delete-confirm-modal');
        const confirmBtn = document.getElementById('confirm-delete-btn');
        const cancelBtn = document.getElementById('cancel-delete-btn');

        modal.style.display = 'block';

        const handleConfirm = () => {
            cleanup();
            resolve(true);
        };

        const handleCancel = () => {
            cleanup();
            resolve(false);
        };

        const cleanup = () => {
            modal.style.display = 'none';
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);

        // Close on outside click
        window.onclick = (event) => {
            if (event.target === modal) {
                handleCancel();
            }
        };
    });
}

async function deleteChat(chatId, title) {
    // Custom Modal Confirmation
    const confirmed = await confirmDelete();
    if (!confirmed) return;

    try {
        const response = await authFetch(`/api/chats/${chatId}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Chat deleted', 'success');

            // If deleted active chat, reset to new chat
            if (currentChatId === chatId) {
                startNewChat();
            } else {
                loadChatSessions(); // Refresh list
            }
        } else {
            showError('Failed to delete chat');
        }
    } catch (e) {
        showError('Error deleting chat');
    }
}

async function loadChat(chatId) {
    if (chatId === currentChatId) return;
    loading.classList.add('active');
    try {
        const response = await authFetch(`/api/chats/${chatId}/messages`);

        // Check if response is OK
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const messages = await response.json();

        // Validate that messages is an array
        if (!Array.isArray(messages)) {
            console.error("Invalid response format:", messages);
            throw new Error("Server returned invalid data format");
        }

        currentChatId = chatId;

        // Clear UI
        document.querySelectorAll('.message').forEach(m => m.remove());
        const welcome = document.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        // Load messages with validation
        messages.forEach((m, index) => {
            if (!m || typeof m !== 'object') {
                console.warn(`Skipping invalid message at index ${index}:`, m);
                return;
            }
            addMessage(
                m.text || '',
                m.sender || 'unknown',
                m.cited_files || [],
                m.confidence_score || null,
                m.source_snippets || []
            );
        });

        loadChatSessions(); // Update active highlight
        showToast(`Loaded ${messages.length} messages`, 'success');
    } catch (e) {
        console.error("Load chat error:", e);
        showError("Failed to load chat: " + (e.message || e));
    } finally {
        loading.classList.remove('active');
    }
}

function startNewChat() {
    currentChatId = null;
    document.querySelectorAll('.message').forEach(m => m.remove());
    if (!document.querySelector('.welcome-message')) {
        chatContainer.innerHTML = `<div class="welcome-message"><h2>Welcome</h2><p>Ask questions about your documents.</p></div>`;
    }
    loadChatSessions();
}

function showSourceSnippets(snippets) {
    const list = document.getElementById('snippets-list');
    list.innerHTML = '';
    snippets.forEach(s => {
        const div = document.createElement('div');
        div.className = 'snippet-card';
        div.innerHTML = `<h4>${s.filename}</h4><p>${s.text}</p>`;
        list.appendChild(div);
    });
    snippetsModal.style.display = 'block';
}

function downloadFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}`;
}

function speakText(text) {
    if (!('speechSynthesis' in window)) return;

    // If speaking the same text or just enabled, this allows restarting or new text
    // But the toggle logic is mainly handled by the button click now.
    // This function just "starts" speech.

    window.speechSynthesis.cancel(); // Stop any current

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = settings.voiceRate || 0.9;
    utterance.volume = (settings.voiceVolume || 100) / 100;
    utterance.pitch = settings.voicePitch || 1.0;

    utterance.onstart = () => { ttsActive = true; };
    utterance.onend = () => { ttsActive = false; };

    window.speechSynthesis.speak(utterance);
}

// Initialization and Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check Auth
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login';
        return;
    }

    loadSettings();
    loadChatSessions();

    // Admin Button
    // Admin Button
    const role = sessionStorage.getItem('role');
    if (role === 'Admin') {
        const controlPanelButtons = document.querySelector('.control-panel-buttons');
        if (controlPanelButtons) {
            const adminBtn = document.createElement('button');
            adminBtn.id = 'admin-panel-btn';
            adminBtn.className = 'control-btn';
            adminBtn.title = 'Admin Dashboard';
            // Use standard structure for control buttons
            adminBtn.innerHTML = '<span class="control-label">Admin Panel</span>';
            adminBtn.onclick = () => window.location.href = '/admin';

            // Prepend to the list or append? User said "align in properly". 
            // Usually admin stuff is important, maybe at top or bottom. 
            // Control panel has: Read Aloud, Export, Clear, Settings.
            // Let's add it at the top of the control controls.
            controlPanelButtons.insertBefore(adminBtn, controlPanelButtons.firstChild);
        }
    }

    // Upload/Delete Buttons - Check permissions and attach listeners
    setTimeout(() => {
        const permissions = JSON.parse(sessionStorage.getItem('permissions') || '[]');
        const uploadBtn = document.getElementById('upload-btn');
        const manageBtn = document.getElementById('manage-files-btn');

        // Show/hide upload buttons based on permission
        // Admin has wildcard '*', others need explicit 'files.upload'
        const role = sessionStorage.getItem('role');
        const hasPermission = role === 'Admin' || permissions.includes('*') || permissions.includes('files.upload');
        if (hasPermission) {
            if (uploadBtn) {
                uploadBtn.style.display = 'block';
                uploadBtn.addEventListener('click', openUploadModal);
            }
            if (manageBtn) {
                manageBtn.style.display = 'block';
                manageBtn.addEventListener('click', openFileManagementModal);
            }
            updateQuotaDisplay(); // Update quota on load
        } else {
            if (uploadBtn) uploadBtn.style.display = 'none';
            if (manageBtn) manageBtn.style.display = 'none';
        }
    }, 500);

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (queryInput) queryInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    // Logout Handler - Show confirmation modal
    const logoutBtn = document.getElementById('logout-btn');
    const logoutModal = document.getElementById('logout-confirm-modal');
    const confirmLogoutBtn = document.getElementById('confirm-logout-btn');
    const cancelLogoutBtn = document.getElementById('cancel-logout-btn');

    if (logoutBtn && logoutModal) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            logoutModal.style.display = 'flex';
        });

        confirmLogoutBtn.addEventListener('click', () => {
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('username');
            sessionStorage.removeItem('role');
            window.location.href = '/login';
        });

        cancelLogoutBtn.addEventListener('click', () => {
            logoutModal.style.display = 'none';
        });
    }

    if (newChatBtn) newChatBtn.addEventListener('click', startNewChat);

    // Clear Chat Button
    if (clearChatBtn) clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear this chat?')) {
            if (currentChatId) {
                authFetch(`/api/chats/${currentChatId}/messages`, { method: 'DELETE' }) // Hypothetical clear endpoint or just new chat
                    .then(() => startNewChat());
            } else {
                startNewChat();
            }
        }
    });

    // TTS Button (Read/Stop)
    if (ttsBtn) ttsBtn.addEventListener('click', () => {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            ttsActive = false;
            showToast('Stopped reading', 'info');
            return;
        }

        const messages = document.querySelectorAll('.message.assistant .message-content');
        if (messages.length > 0) {
            const lastMsg = messages[messages.length - 1];
            // Extract pure text
            let text = lastMsg.innerText;
            text = text.replace(/🔊 Read\s*View Sources/g, '').replace(/Sources:.*/g, '').trim();
            speakText(text);
        } else {
            showToast('No message to read', 'warning');
        }
    });


    // Export Button
    if (exportBtn) exportBtn.addEventListener('click', () => {
        const messages = [];
        document.querySelectorAll('.message').forEach(msg => {
            const sender = msg.classList.contains('user') ? 'User' : 'AI';
            // Clean up text content
            let text = msg.querySelector('.message-content').innerText;
            text = text.replace(/🔊 Read\s*View Sources/g, '').replace(/Sources:.*/g, '').trim();
            messages.push(`[${sender}] ${text}`);
        });

        if (messages.length === 0) {
            showToast('Nothing to export', 'warning');
            return;
        }

        const blob = new Blob([messages.join('\n\n')], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Chat exported', 'success');
    });



    if (settingsBtn) settingsBtn.addEventListener('click', () => {
        settingsModal.style.display = 'flex';
    });

    // Real-time slider value updates
    const volumeSlider = document.getElementById('voice-volume');
    const rateSlider = document.getElementById('voice-rate');
    const pitchSlider = document.getElementById('voice-pitch');

    if (volumeSlider) {
        volumeSlider.addEventListener('input', (e) => {
            document.getElementById('volume-value').textContent = e.target.value + '%';
        });
    }

    if (rateSlider) {
        rateSlider.addEventListener('input', (e) => {
            document.getElementById('rate-value').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
        });
    }

    if (pitchSlider) {
        pitchSlider.addEventListener('input', (e) => {
            document.getElementById('pitch-value').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
        });
    }

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => btn.closest('.modal').style.display = 'none');
    });

    // Open Change Password Modal from Settings
    const changePasswordSettingsBtn = document.getElementById('change-password-settings-btn');
    if (changePasswordSettingsBtn) {
        changePasswordSettingsBtn.addEventListener('click', () => {
            document.getElementById('user-change-password-modal').style.display = 'flex';
        });
    }

    // Change Password Handler (for regular users)
    const changePasswordBtn = document.getElementById('change-password-btn');
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', async () => {
            const currentPw = document.getElementById('current-password-user').value;
            const newPw = document.getElementById('new-password-user').value;
            const confirmPw = document.getElementById('confirm-password-user').value;

            // Validate
            if (!currentPw || !newPw || !confirmPw) {
                showToast('All password fields are required', 'error');
                return;
            }
            if (newPw.length < 6) {
                showToast('Password must be at least 6 characters', 'error');
                return;
            }
            if (newPw !== confirmPw) {
                showToast('New passwords do not match', 'error');
                return;
            }

            try {
                const res = await authFetch('/api/users/change-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        current_password: currentPw,
                        new_password: newPw
                    })
                });
                const data = await res.json();

                if (res.ok) {
                    showToast(data.message || 'Password updated successfully', 'success');
                    // Clear fields
                    document.getElementById('current-password-user').value = '';
                    document.getElementById('new-password-user').value = '';
                    document.getElementById('confirm-password-user').value = '';
                } else {
                    showToast(data.error || 'Failed to update password', 'error');
                }
            } catch (e) {
                showToast('Error updating password', 'error');
            }
        });
    }

    // Theme selector
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            settings.theme = theme;
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applySettings();
        });
    });

    if (document.getElementById('save-settings-btn')) {
        document.getElementById('save-settings-btn').addEventListener('click', () => {
            settings.voiceVolume = parseInt(document.getElementById('voice-volume').value);
            settings.voiceRate = parseFloat(document.getElementById('voice-rate').value);
            settings.voicePitch = parseFloat(document.getElementById('voice-pitch').value);
            saveSettings();
            settingsModal.style.display = 'none';
            showToast('Settings saved', 'success');
        });
    }
});


// ===== UPLOAD & FILE MANAGEMENT FUNCTIONS =====
// Add these to main.js

// Update quota display on button
async function updateQuotaDisplay() {
    try {
        const response = await authFetch('/api/upload/quota');
        if (!response.ok) return;

        const data = await response.json();
        const uploadBtn = document.getElementById('upload-btn');

        if (!uploadBtn) return;

        if (data.limit === null) {
            // Admin - unlimited
            uploadBtn.querySelector('.control-label').textContent = 'Upload Files (Unlimited)';
            uploadBtn.disabled = false;
            uploadBtn.title = 'Upload files to incoming directory';
        } else {
            // Regular user with quota
            uploadBtn.querySelector('.control-label').textContent = `Upload Files (${data.used}/${data.limit})`;

            if (data.remaining <= 0) {
                uploadBtn.disabled = true;
                uploadBtn.style.opacity = '0.5';
                uploadBtn.style.cursor = 'not-allowed';
                uploadBtn.title = 'Upload limit reached. Delete some files to upload more.';
            } else {
                uploadBtn.disabled = false;
                uploadBtn.style.opacity = '1';
                uploadBtn.style.cursor = 'pointer';
                uploadBtn.title = `Upload files (${data.remaining} remaining)`;
            }
        }
    } catch (e) {
        console.error('Error updating quota:', e);
    }
}

// Open upload modal
async function openUploadModal() {
    try {
        const response = await authFetch('/api/upload/quota');
        const data = await response.json();

        const quotaDisplay = document.getElementById('upload-quota-display');
        if (data.limit === null) {
            quotaDisplay.textContent = 'You have unlimited uploads (Admin)';
            quotaDisplay.style.color = 'var(--success-color)';
        } else {
            quotaDisplay.textContent = `Files uploaded: ${data.used}/${data.limit} (${data.remaining} remaining)`;
            quotaDisplay.style.color = data.remaining > 0 ? 'var(--text-secondary)' : 'var(--danger-color)';
        }

        openModal('upload-modal');
    } catch (e) {
        showToast('Error loading quota', 'error');
    }
}

// Submit file upload
async function submitUpload() {
    const fileInput = document.getElementById('file-upload-input');
    const files = fileInput.files;

    if (files.length === 0) {
        showToast('Please select files to upload', 'error');
        return;
    }

    const uploadBtn = document.getElementById('upload-submit-btn');
    const progressDiv = document.getElementById('upload-progress');
    const progressBar = document.getElementById('upload-progress-bar');
    const statusText = document.getElementById('upload-status');

    uploadBtn.disabled = true;
    progressDiv.style.display = 'block';

    let uploaded = 0;
    let failed = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length) * 100;
        progressBar.style.width = progress + '%';
        statusText.textContent = `Uploading ${i + 1} of ${files.length}: ${file.name}`;

        // Check file size
        if (file.size > 25 * 1024 * 1024) {
            showToast(`File "${file.name}" is too large (max 25MB)`, 'error');
            failed++;
            continue;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await authFetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                uploaded++;
            } else {
                showToast(`Error uploading "${file.name}": ${data.error}`, 'error');
                failed++;
                // If quota reached, stop trying
                if (response.status === 429) break;
            }
        } catch (e) {
            showToast(`Error uploading "${file.name}"`, 'error');
            failed++;
        }
    }

    // Reset and close
    uploadBtn.disabled = false;
    progressDiv.style.display = 'none';
    progressBar.style.width = '0%';
    fileInput.value = '';

    // Show summary
    if (uploaded > 0) {
        showToast(`Successfully uploaded ${uploaded} file(s)${failed > 0 ? `, ${failed} failed` : ''}`, 'success');
    }

    // Update quota and close modal
    await updateQuotaDisplay();
    closeModal('upload-modal');
}

// Open file management modal
async function openFileManagementModal() {
    openModal('file-management-modal');
    await loadUserFiles();
}

// Load user's files
async function loadUserFiles() {
    try {
        const [filesResponse, quotaResponse] = await Promise.all([
            authFetch('/api/files'),
            authFetch('/api/upload/quota')
        ]);

        const filesData = await filesResponse.json();
        const quotaData = await quotaResponse.json();

        // Update quota display
        const quotaDisplay = document.getElementById('manage-quota-display');
        if (quotaData.limit === null) {
            quotaDisplay.textContent = 'Uploads: Unlimited (Admin)';
        } else {
            quotaDisplay.textContent = `Uploads: ${quotaData.used}/${quotaData.limit}`;
        }

        // Populate file table
        const tbody = document.getElementById('files-table-body');
        if (filesData.files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: var(--text-secondary);">No files uploaded yet</td></tr>';
            return;
        }

        tbody.innerHTML = filesData.files.map(file => {
            const sizeKB = (file.size / 1024).toFixed(2);
            const uploadedBy = file.uploaded_by || 'Unknown';
            return `
                <tr>
                    <td>${file.filename}</td>
                    <td><span class="file-chip">${file.domain}</span></td>
                    <td><span class="tag">${file.category}</span></td>
                    <td>${sizeKB} KB</td>
                    <td>${uploadedBy}</td>
                    <td>
                        <button class="btn-danger" style="padding: 4px 12px; font-size: 13px;" 
                            onclick="deleteUserFile('${file.path.replace(/\\/g, '\\\\')}', '${file.filename}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (e) {
        showToast('Error loading files', 'error');
        console.error(e);
    }
}

// Delete user file
async function deleteUserFile(filepath, filename) {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;

    try {
        const response = await authFetch(`/api/files/${filepath}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`File deleted successfully`, 'success');
            await loadUserFiles(); // Refresh list
            await updateQuotaDisplay(); // Update button quota
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (e) {
        showToast('Error deleting file', 'error');
    }
}

// ===== UPLOAD & FILE MANAGEMENT FUNCTIONS =====
// Add these to main.js

// Update quota display on button
async function updateQuotaDisplay() {
    try {
        const response = await authFetch('/api/upload/quota');
        if (!response.ok) return;

        const data = await response.json();
        const uploadBtn = document.getElementById('upload-btn');

        if (!uploadBtn) return;

        if (data.limit === null) {
            // Admin - unlimited
            uploadBtn.querySelector('.control-label').textContent = 'Upload Files (Unlimited)';
            uploadBtn.disabled = false;
            uploadBtn.title = 'Upload files to incoming directory';
        } else {
            // Regular user with quota
            uploadBtn.querySelector('.control-label').textContent = `Upload Files (${data.used}/${data.limit})`;

            if (data.remaining <= 0) {
                uploadBtn.disabled = true;
                uploadBtn.style.opacity = '0.5';
                uploadBtn.style.cursor = 'not-allowed';
                uploadBtn.title = 'Upload limit reached. Delete some files to upload more.';
            } else {
                uploadBtn.disabled = false;
                uploadBtn.style.opacity = '1';
                uploadBtn.style.cursor = 'pointer';
                uploadBtn.title = `Upload files (${data.remaining} remaining)`;
            }
        }
    } catch (e) {
        console.error('Error updating quota:', e);
    }
}

// Open upload modal
async function openUploadModal() {
    try {
        const response = await authFetch('/api/upload/quota');
        const data = await response.json();

        const quotaDisplay = document.getElementById('upload-quota-display');
        if (data.limit === null) {
            quotaDisplay.textContent = 'You have unlimited uploads (Admin)';
            quotaDisplay.style.color = 'var(--success-color)';
        } else {
            quotaDisplay.textContent = `Files uploaded: ${data.used}/${data.limit} (${data.remaining} remaining)`;
            quotaDisplay.style.color = data.remaining > 0 ? 'var(--text-secondary)' : 'var(--danger-color)';
        }

        openModal('upload-modal');
    } catch (e) {
        showToast('Error loading quota', 'error');
    }
}

// Submit file upload
async function submitUpload() {
    const fileInput = document.getElementById('file-upload-input');
    const files = fileInput.files;

    if (files.length === 0) {
        showToast('Please select files to upload', 'error');
        return;
    }

    const uploadBtn = document.getElementById('upload-submit-btn');
    const progressDiv = document.getElementById('upload-progress');
    const progressBar = document.getElementById('upload-progress-bar');
    const statusText = document.getElementById('upload-status');

    uploadBtn.disabled = true;
    progressDiv.style.display = 'block';

    let uploaded = 0;
    let failed = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length) * 100;
        progressBar.style.width = progress + '%';
        statusText.textContent = `Uploading ${i + 1} of ${files.length}: ${file.name}`;

        // Check file size
        if (file.size > 25 * 1024 * 1024) {
            showToast(`File "${file.name}" is too large (max 25MB)`, 'error');
            failed++;
            continue;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await authFetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                uploaded++;
            } else {
                showToast(`Error uploading "${file.name}": ${data.error}`, 'error');
                failed++;
                // If quota reached, stop trying
                if (response.status === 429) break;
            }
        } catch (e) {
            showToast(`Error uploading "${file.name}"`, 'error');
            failed++;
        }
    }

    // Reset and close
    uploadBtn.disabled = false;
    progressDiv.style.display = 'none';
    progressBar.style.width = '0%';
    fileInput.value = '';

    // Show summary
    if (uploaded > 0) {
        showToast(`Successfully uploaded ${uploaded} file(s)${failed > 0 ? `, ${failed} failed` : ''}`, 'success');
    }

    // Update quota and close modal
    await updateQuotaDisplay();
    closeModal('upload-modal');
}

// Open file management modal
async function openFileManagementModal() {
    openModal('file-management-modal');
    await loadUserFiles();
}

// Load user's files
async function loadUserFiles() {
    try {
        const [filesResponse, quotaResponse] = await Promise.all([
            authFetch('/api/files'),
            authFetch('/api/upload/quota')
        ]);

        const filesData = await filesResponse.json();
        const quotaData = await quotaResponse.json();

        // Update quota display
        const quotaDisplay = document.getElementById('manage-quota-display');
        if (quotaData.limit === null) {
            quotaDisplay.textContent = 'Uploads: Unlimited (Admin)';
        } else {
            quotaDisplay.textContent = `Uploads: ${quotaData.used}/${quotaData.limit}`;
        }

        // Populate file table
        const tbody = document.getElementById('files-table-body');
        if (filesData.files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: var(--text-secondary);">No files uploaded yet</td></tr>';
            return;
        }

        tbody.innerHTML = filesData.files.map(file => {
            const sizeKB = (file.size / 1024).toFixed(2);
            const uploadedBy = file.uploaded_by || 'Unknown';
            return `
                <tr>
                    <td>${file.filename}</td>
                    <td><span class="file-chip">${file.domain}</span></td>
                    <td><span class="tag">${file.category}</span></td>
                    <td>${sizeKB} KB</td>
                    <td>${uploadedBy}</td>
                    <td>
                        <button class="btn-danger" style="padding: 4px 12px; font-size: 13px;" 
                            onclick="deleteUserFile('${file.path.replace(/\\/g, '\\\\')}', '${file.filename}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (e) {
        showToast('Error loading files', 'error');
        console.error(e);
    }
}

// Delete user file
async function deleteUserFile(filepath, filename) {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;

    try {
        const response = await authFetch(`/api/files/${filepath}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`File deleted successfully`, 'success');
            await loadUserFiles(); // Refresh list
            await updateQuotaDisplay(); // Update button quota
        } else {
            showToast(`Error: ${data.error}`, 'error');
        }
    } catch (e) {
        showToast('Error deleting file', 'error');
    }
}

// Initialize upload/delete on page load
document.addEventListener('DOMContentLoaded', () => {
    // Wait for auth to complete
    setTimeout(() => {
        const permissions = JSON.parse(sessionStorage.getItem('permissions') || '[]');

        // Show/hide upload buttons based on permission
        // Admin has wildcard '*', others need explicit 'files.upload'
        const role = sessionStorage.getItem('role');
        const hasPermission = role === 'Admin' || permissions.includes('*') || permissions.includes('files.upload');
        if (hasPermission) {
            document.getElementById('upload-btn').style.display = 'block';
            document.getElementById('manage-files-btn').style.display = 'block';
            updateQuotaDisplay(); // Update quota on load
        } else {
            document.getElementById('upload-btn').style.display = 'none';
            document.getElementById('manage-files-btn').style.display = 'none';
        }

        // Attach event listeners
        document.getElementById('upload-btn')?.addEventListener('click', openUploadModal);
        document.getElementById('manage-files-btn')?.addEventListener('click', openFileManagementModal);
    }, 500);
});
// Modal helper functions - add to main.js

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}
