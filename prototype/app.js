/* ============================================ */
/* VinFast AI Advisor — Chat Logic              */
/* Kết nối THẬT với agent.py qua Flask API      */
/* ============================================ */

// ── Config ──
const API_URL = '/api/chat';
const API_RESET = '/api/reset';

// ── State ──
let isTyping = false;
let sessionId = '';
let messageHistory = [];

// ── Screen Navigation ──
function goToChat() {
    const home = document.getElementById('screen-home');
    const chat = document.getElementById('screen-chat');

    home.classList.add('exit-left');
    home.classList.remove('active');

    setTimeout(() => {
        chat.classList.add('active');

        // Send welcome message on first open
        if (messageHistory.length === 0) {
            addBotMessageDirect(
                "Xin chào! 👋 Tôi là **VinFast AI Advisor** — trợ lý tư vấn xe điện VinFast.\n\n" +
                "Tôi có thể giúp bạn:\n" +
                "🔋 Tìm xe điện phù hợp ngân sách\n" +
                "📊 So sánh chi tiết các model\n" +
                "💰 Tính tổng chi phí sở hữu\n\n" +
                "Hãy hỏi tôi bất cứ điều gì! 😊"
            );
        }
    }, 300);
}

function goHome() {
    const home = document.getElementById('screen-home');
    const chat = document.getElementById('screen-chat');

    chat.classList.remove('active');

    setTimeout(() => {
        home.classList.remove('exit-left');
        home.classList.add('active');
    }, 300);
}

function toggleMenu() {
    if (confirm('Bạn muốn reset cuộc trò chuyện?')) {
        resetChat();
    }
}

async function resetChat() {
    // Reset server session
    if (sessionId) {
        try {
            await fetch(API_RESET, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
        } catch (e) { /* ignore */ }
    }

    // Reset UI
    sessionId = '';
    messageHistory = [];
    const container = document.getElementById('chat-messages');
    container.innerHTML = '<div class="date-divider"><span>Hôm nay</span></div>';

    // Show suggestions again
    const suggestions = document.getElementById('quick-suggestions');
    if (suggestions) suggestions.style.display = 'flex';

    // Re-send welcome
    addBotMessageDirect(
        "Xin chào! 👋 Cuộc trò chuyện đã được reset.\n\n" +
        "Bạn muốn hỏi gì về xe VinFast? 😊"
    );
}

// ── Messages ──
function getCurrentTime() {
    return new Date().toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function addMessage(content, type) {
    const container = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.className = `message ${type}`;

    const avatar = type === 'bot' ? '🚗' : '👤';
    const formattedContent = formatMessage(content);

    msg.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div>
            <div class="msg-bubble">${formattedContent}</div>
            <span class="msg-time">${getCurrentTime()}</span>
        </div>
    `;

    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;

    // === Attach click handlers to action chips (Tư vấn gợi ý) ===
    if (type === 'bot') {
        const actionChips = msg.querySelectorAll('.chat-action');
        actionChips.forEach(chip => {
            chip.style.cursor = 'pointer';
            chip.onclick = function(e) {
                e.preventDefault();
                const text = chip.textContent.trim();
                sendSuggestion(text);
            };
        });
    }

    messageHistory.push({ role: type, content: content });
}

function addBotMessageDirect(content) {
    // Hiển thị ngay — không qua API (dùng cho welcome message)
    addMessage(content, 'bot');
}

function addUserMessage(content) {
    addMessage(content, 'user');
}

// ── Typing indicator ──
function showTyping() {
    isTyping = true;
    const container = document.getElementById('chat-messages');
    const statusText = document.getElementById('status-text');

    statusText.textContent = 'Đang trả lời...';
    statusText.style.color = 'var(--blue-500)';

    const typing = document.createElement('div');
    typing.className = 'message bot';
    typing.id = 'typing-msg';
    typing.innerHTML = `
        <div class="msg-avatar">🚗</div>
        <div class="msg-bubble">
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    isTyping = false;
    const typing = document.getElementById('typing-msg');
    if (typing) typing.remove();

    const statusText = document.getElementById('status-text');
    statusText.textContent = 'Luôn sẵn sàng';
    statusText.style.color = '#22C55E';
}

// ── Send message to REAL agent.py API ──
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();

    if (!text || isTyping) return;

    input.value = '';
    addUserMessage(text);

    // Hide suggestions after first message
    const suggestions = document.getElementById('quick-suggestions');
    if (suggestions) suggestions.style.display = 'none';

    // Show typing indicator
    showTyping();

    try {
        // === GỌI API THẬT → agent.py (LangGraph + RAG + Tools) ===
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId
            })
        });

        const data = await response.json();

        // Lưu session_id cho các lần gọi tiếp (memory)
        if (data.session_id) {
            sessionId = data.session_id;
        }

        hideTyping();
        addMessage(data.reply || 'Không có phản hồi.', 'bot');

    } catch (error) {
        hideTyping();
        console.error('API Error:', error);
        addMessage(
            '⚠️ Không thể kết nối với server.\n\n' +
            'Hãy đảm bảo `python server.py` đang chạy tại http://localhost:5000',
            'bot'
        );
    }
}

function sendSuggestion(text) {
    document.getElementById('chat-input').value = text;
    sendMessage();
}

// ── Format markdown → rich HTML ──
function formatMessage(text) {
    if (!text) return '';

    // Split into lines for block-level processing
    const lines = text.split('\n');
    let html = '';
    let inTable = false;
    let tableRows = [];
    let inList = false;
    let listType = ''; // 'ul' or 'ol'
    let listItems = [];

    function flushTable() {
        if (tableRows.length === 0) return '';
        let t = '<table class="chat-table"><thead><tr>';
        // First row = header
        const headerCells = parseTableRow(tableRows[0]);
        headerCells.forEach(cell => { t += `<th>${inlineFormat(cell)}</th>`; });
        t += '</tr></thead><tbody>';

        // Skip separator row (row with ---)
        let startIdx = 1;
        if (tableRows.length > 1 && tableRows[1].match(/^\|[\s\-:|]+\|$/)) {
            startIdx = 2;
        }

        for (let i = startIdx; i < tableRows.length; i++) {
            const cells = parseTableRow(tableRows[i]);
            t += '<tr>';
            cells.forEach(cell => { t += `<td>${inlineFormat(cell)}</td>`; });
            t += '</tr>';
        }
        t += '</tbody></table>';
        tableRows = [];
        return t;
    }

    function flushList() {
        if (listItems.length === 0) return '';
        const tag = listType;
        let l = `<${tag} class="chat-list">`;
        listItems.forEach(item => { l += `<li>${inlineFormat(item)}</li>`; });
        l += `</${tag}>`;
        listItems = [];
        inList = false;
        return l;
    }

    function parseTableRow(row) {
        return row.split('|').slice(1, -1).map(c => c.trim());
    }

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // ── Table row: | col | col |
        if (trimmed.match(/^\|.+\|$/)) {
            if (inList) html += flushList();
            inTable = true;
            tableRows.push(trimmed);
            continue;
        } else if (inTable) {
            html += flushTable();
            inTable = false;
        }

        // ── Numbered list: 1. item, 2. item
        const olMatch = trimmed.match(/^(\d+)\.\s+(.+)/);
        if (olMatch) {
            if (inList && listType !== 'ol') html += flushList();
            inList = true;
            listType = 'ol';
            listItems.push(olMatch[2]);
            continue;
        }

        // ── Bullet list: - item or • item
        const ulMatch = trimmed.match(/^[-•]\s+(.+)/);
        if (ulMatch) {
            if (inList && listType !== 'ul') html += flushList();
            inList = true;
            listType = 'ul';
            listItems.push(ulMatch[1]);
            continue;
        }

        // Flush list if we hit a non-list line
        if (inList) html += flushList();

        // ── Headers: ### Header
        if (trimmed.startsWith('### ')) {
            html += `<div class="chat-h3">${inlineFormat(trimmed.slice(4))}</div>`;
            continue;
        }
        if (trimmed.startsWith('## ')) {
            html += `<div class="chat-h2">${inlineFormat(trimmed.slice(3))}</div>`;
            continue;
        }

        // ── Horizontal rule: --- or ───
        if (trimmed.match(/^[-─═]{3,}$/)) {
            html += '<hr class="chat-hr">';
            continue;
        }

        // ── Empty line = paragraph break
        if (trimmed === '') {
            html += '<div class="chat-spacer"></div>';
            continue;
        }

        // ── Normal line
        html += `<div class="chat-line">${inlineFormat(trimmed)}</div>`;
    }

    // Flush remaining
    if (inTable) html += flushTable();
    if (inList) html += flushList();

    return html;
}

// Inline formatting: bold, action buttons, etc.
function inlineFormat(text) {
    return text
        // Bold: **text**
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Clickable actions: [Action text]
        .replace(/\[([^\]]+)\]/g, '<span class="chat-action">$1</span>')
        ;
}

// ── Initialize ──
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        const observer = new MutationObserver(() => {
            if (document.getElementById('screen-chat').classList.contains('active')) {
                setTimeout(() => chatInput.focus(), 600);
            }
        });
        observer.observe(document.getElementById('screen-chat'), {
            attributes: true,
            attributeFilter: ['class']
        });
    }
});
