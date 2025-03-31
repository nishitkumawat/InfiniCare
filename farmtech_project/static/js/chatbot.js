/**
 * Chatbot functionality for the Reve Digital Platform
 * Supports both farming and healthcare domains
 */

document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestionButtons = document.querySelectorAll('.suggestion');
    
    // Get CSRF token from cookie
    function getCsrfToken() {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; csrftoken=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }
    
    // Add a message to the chat window
    function addMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        
        // Check if the message contains HTML (for formatted responses with lists, etc.)
        if (message.includes('<') && message.includes('>') && !isUser) {
            messageElement.innerHTML = message;
        } else {
            const messageText = document.createElement('p');
            messageText.classList.add('mb-0');
            messageText.textContent = message;
            messageElement.appendChild(messageText);
        }
        
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Send message to AI assistant
    async function sendMessage(message) {
        // Show user message
        addMessage(message, true);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ message: message }),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Show bot response
            addMessage(data.response);
        } catch (error) {
            console.error('Error:', error);
            
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Show error message
            addMessage('Sorry, I had trouble connecting. Please try again later.');
        }
    }
    
    // Submit form event
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });
    
    // Suggestion button clicks
    suggestionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.textContent;
            messageInput.value = message;
            sendMessage(message);
        });
    });
    
    // Enter key to send message
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Handle tab switching for suggestion categories
    const tabButtons = document.querySelectorAll('[data-bs-toggle="pill"]');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Deactivate all tabs
            document.querySelectorAll('[data-bs-toggle="pill"]').forEach(btn => {
                btn.classList.remove('active');
                const targetId = btn.getAttribute('data-bs-target');
                document.querySelector(targetId).classList.remove('show', 'active');
            });
            
            // Activate clicked tab
            this.classList.add('active');
            const targetId = this.getAttribute('data-bs-target');
            const targetPane = document.querySelector(targetId);
            targetPane.classList.add('show', 'active');
        });
    });
    
    // Focus input on page load
    messageInput.focus();
});
