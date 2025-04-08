// Initialize AOS animations
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// API endpoints
const API_BASE_URL = 'http://localhost:5000/api';

// DOM elements
const caseForm = document.getElementById('caseForm');
const caseText = document.getElementById('caseText');
const winProbabilityBar = document.querySelector('.progress-bar');
const similarCasesList = document.getElementById('similarCasesList');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendMessageBtn = document.getElementById('sendMessage');
const saveChatBtn = document.getElementById('saveChat');
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-link');
const newChatButton = document.getElementById('newChat');
const savedChatsDropdown = document.getElementById('savedChatsDropdown');
const casesGrid = document.getElementById('casesGrid');
const caseCategory = document.getElementById('caseCategory');
const caseSearch = document.getElementById('caseSearch');
const calculateBtn = document.getElementById('calculateBtn');
const probabilityResult = document.getElementById('probabilityResult');

// Chat state
let currentChatId = null;
let chatHistory = [];
let currentChat = [];

// Event listeners
caseForm.addEventListener('submit', handleCaseSubmit);
sendMessageBtn.addEventListener('click', handleSendMessage);
saveChatBtn.addEventListener('click', handleSaveChat);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

// Initialize navigation
document.addEventListener('DOMContentLoaded', function() {
    // Get all navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');
    
    // Function to show a specific section
    function showSection(sectionId) {
        sections.forEach(section => {
            if (section.id === sectionId) {
                section.classList.remove('d-none');
                section.classList.add('active-section');
            } else {
                section.classList.add('d-none');
                section.classList.remove('active-section');
            }
        });
        
        // Update active state in navigation
        navLinks.forEach(link => {
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    
    // Add click event listeners to navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
            
            // Update URL without page reload
            history.pushState(null, '', `#${sectionId}`);
        });
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function() {
        const hash = window.location.hash.substring(1);
        if (hash) {
            showSection(hash);
        } else {
            showSection('chat'); // Default section
        }
    });
    
    // Show initial section based on URL hash
    const initialSection = window.location.hash.substring(1) || 'chat';
    showSection(initialSection);
    
    // Initialize chat functionality
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendMessage');
    
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function handleSendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            
            // Simulate AI response (replace with actual API call)
            setTimeout(() => {
                const responses = [
                    "I understand your question. Let me help you with that.",
                    "Based on my analysis, here's what I found...",
                    "I'll need more information to provide a complete answer.",
                    "Let me search through similar cases for you."
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                addMessage(randomResponse);
            }, 1000);
        }
    }
    
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Initialize new chat button
    document.getElementById('newChat').addEventListener('click', function() {
        chatMessages.innerHTML = '';
        addMessage("Hello! I'm your legal research assistant. How can I help you today?");
    });
    
    // Initialize cases functionality
    const casesGrid = document.getElementById('casesGrid');
    const caseCategory = document.getElementById('caseCategory');
    const caseSearch = document.getElementById('caseSearch');
    
    function loadCases() {
        // Simulated case data (replace with actual API call)
        const cases = [
            {
                title: "Contract Dispute Resolution",
                category: "Civil",
                date: "2023-01-15",
                outcome: "Settled",
                summary: "Successfully mediated a contract dispute between two corporations."
            },
            {
                title: "Criminal Defense Case",
                category: "Criminal",
                date: "2023-02-20",
                outcome: "Acquitted",
                summary: "Defended client against false accusations with strong evidence."
            }
        ];
        
        casesGrid.innerHTML = '';
        cases.forEach(caseData => {
            const caseCard = document.createElement('div');
            caseCard.className = 'case-card';
            caseCard.innerHTML = `
                <h3>${caseData.title}</h3>
                <p><strong>Category:</strong> ${caseData.category}</p>
                <p><strong>Date:</strong> ${caseData.date}</p>
                <p><strong>Outcome:</strong> ${caseData.outcome}</p>
                <p>${caseData.summary}</p>
            `;
            casesGrid.appendChild(caseCard);
        });
    }
    
    caseCategory.addEventListener('change', loadCases);
    caseSearch.addEventListener('input', loadCases);
    
    // Initialize win calculator
    const calculatorForm = document.getElementById('calculatorForm');
    const probabilityResult = document.getElementById('probabilityResult');
    
    calculatorForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const caseType = document.getElementById('caseType').value;
        const caseDetails = document.getElementById('caseDetails').value;
        
        // Simulate probability calculation (replace with actual API call)
        const probability = Math.floor(Math.random() * 100);
        probabilityResult.innerHTML = `
            <div class="alert alert-info">
                <h4>Win Probability: ${probability}%</h4>
                <p>Based on the provided information, there is a ${probability}% chance of winning this case.</p>
            </div>
        `;
    });
    
    // Initialize analytics charts
    const caseDistributionChart = new Chart(
        document.getElementById('caseDistributionChart'),
        {
            type: 'doughnut',
            data: {
                labels: ['Criminal', 'Civil', 'Corporate'],
                datasets: [{
                    data: [30, 45, 25],
                    backgroundColor: [
                        '#4a6bff',
                        '#6c5ce7',
                        '#00cec9'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        }
    );
    
    const successRateChart = new Chart(
        document.getElementById('successRateChart'),
        {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Success Rate',
                    data: [75, 82, 78, 85, 90, 88],
                    borderColor: '#4a6bff',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        }
    );
    
    // Load initial data
    loadCases();
});

// Handle case submission
async function handleCaseSubmit(e) {
    e.preventDefault();
    
    const text = caseText.value.trim();
    if (!text) {
        alert('Please enter case details');
        return;
    }

    try {
        analyzeCase(text);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze case');
    }
}

// Analyze case
async function analyzeCase(caseText) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-case`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ case_text: caseText })
        });

        if (!response.ok) throw new Error('Case analysis failed');

        const data = await response.json();
        
        // Update win probability
        const winProbability = Math.round(data.win_probability * 100);
        winProbabilityBar.style.width = `${winProbability}%`;
        winProbabilityBar.textContent = `${winProbability}%`;

        // Update similar cases
        updateSimilarCases(data.similar_cases);

        // Add initial chat message
        addMessage('assistant', `I've analyzed your case. The win probability is ${winProbability}%. Here are some similar cases for reference. How can I help you further?`);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze case');
    }
}

// Update similar cases list
function updateSimilarCases(cases) {
    similarCasesList.innerHTML = '';
    
    cases.forEach(caseData => {
        const caseElement = document.createElement('a');
        caseElement.href = '#';
        caseElement.className = 'list-group-item list-group-item-action';
        caseElement.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">Case ${caseData.id}</h6>
                <small>${Math.round(caseData.similarity_score * 100)}% match</small>
            </div>
            <p class="mb-1">${caseData.text.substring(0, 100)}...</p>
        `;
        similarCasesList.appendChild(caseElement);
    });
}

// Handle save chat
async function handleSaveChat() {
    try {
        const response = await fetch(`${API_BASE_URL}/save-chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: currentChatId,
                chat_history: chatHistory,
                title: `Chat ${new Date().toLocaleString()}`
            })
        });

        if (!response.ok) throw new Error('Chat saving failed');

        const data = await response.json();
        console.log('Chat saved successfully:', data);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save chat');
    }
}