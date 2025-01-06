// Generate a unique session ID
const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

// DOM Elements
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const clearButton = document.getElementById('clear-chat');
const exportButton = document.getElementById('export-chat');
const typingIndicator = document.getElementById('typing-indicator');
const featureButtons = document.querySelectorAll('.feature-btn');

// Helper Functions
function formatTimestamp(date) {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    typingIndicator.classList.add('active');
}

function hideTypingIndicator() {
    typingIndicator.classList.remove('active');
}

function addMessage(content, isUser = false, timestamp = new Date().toISOString()) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    const timestampDiv = document.createElement('div');
    timestampDiv.className = 'timestamp';
    timestampDiv.textContent = formatTimestamp(timestamp);
    
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(timestampDiv);
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

async function sendMessage(message) {
    if (!message.trim()) return;
    
    // Add user message
    addMessage(message, true);
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator and add bot response
        hideTypingIndicator();
        addMessage(data.response, false, data.timestamp);
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', false);
        console.error('Error:', error);
    }
}

// Event Listeners
sendButton.addEventListener('click', () => sendMessage(userInput.value));

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage(userInput.value);
    }
});

clearButton.addEventListener('click', async () => {
    const confirmed = confirm('Are you sure you want to clear the chat history?');
    if (confirmed) {
        await fetch('/clear_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        chatBox.innerHTML = '';
        // Restore welcome message
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <h2>👋 Welcome to your Digital Marketing Assistant!</h2>
            <p>I can help you with:</p>
            <ul>
                <li>SEO strategies and optimization</li>
                <li>Content marketing tips</li>
                <li>Social media marketing</li>
                <li>Email marketing campaigns</li>
                <li>Marketing analytics and metrics</li>
            </ul>
            <p>How can I assist you today?</p>
        `;
        chatBox.appendChild(welcomeDiv);
    }
});

exportButton.addEventListener('click', async () => {
    const response = await fetch('/get_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ session_id: sessionId })
    });
    
    const data = await response.json();
    const chatHistory = data.map(msg => 
        `${msg.role.toUpperCase()} (${new Date(msg.timestamp).toLocaleString()}): ${msg.message}`
    ).join('\n\n');
    
    const blob = new Blob([chatHistory], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat-history.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

featureButtons.forEach(button => {
    button.addEventListener('click', () => {
        const topic = button.dataset.topic;
        const questions = {
            seo: "What are the best SEO practices for 2024?",
            content: "How do I create an effective content strategy?",
            social: "Which social media platforms should I focus on?",
            email: "How can I improve my email marketing campaigns?",
            analytics: "What are the most important marketing metrics to track?"
        };
        userInput.value = questions[topic];
        userInput.focus();
    });
});

// Tooltips for buttons
const buttons = document.querySelectorAll('button[title]');
const tooltip = document.getElementById('tooltip');

buttons.forEach(button => {
    button.addEventListener('mouseenter', (e) => {
        tooltip.textContent = e.target.title;
        tooltip.style.display = 'block';
        const rect = e.target.getBoundingClientRect();
        tooltip.style.top = `${rect.bottom + 5}px`;
        tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
    });
    
    button.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
    });
});