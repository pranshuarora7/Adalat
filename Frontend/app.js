// News API Integration
async function fetchNews() {
    try {
        const response = await fetch('https://newsdata.io/api/1/latest?apikey=pub_8286657b47f7c49d0aa859bb49eded6b1c3dd&category=crime&country=in&language=en');
        const data = await response.json();
        const newsTicker = document.getElementById('newsTicker');

        newsTicker.innerHTML = '';

        const filteredNews = data.results
            .filter(article => {
                const sensitiveKeywords = ['terrorist', 'attack', 'murder', 'killed', 'dead', 'bomb', 'shoot'];
                const title = article.title.toLowerCase();
                return !sensitiveKeywords.some(keyword => title.includes(keyword));
            })
            .slice(0, 5);

        if (filteredNews.length === 0) {
            newsTicker.innerHTML = `
                <div class="news-item">
                    <i class="fas fa-newspaper"></i>
                    <span>Welcome to Adalat - Your Legal Research Assistant</span>
                </div>
                <div class="news-item">
                    <i class="fas fa-newspaper"></i>
                    <span>Stay updated with the latest legal news and updates</span>
                </div>
            `;
            return;
        }

        filteredNews.forEach(article => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item';
            newsItem.innerHTML = `
                <i class="fas fa-newspaper"></i>
                <span>${article.title}</span>
            `;
            newsTicker.appendChild(newsItem);
        });

        const newsItems = newsTicker.innerHTML;
        newsTicker.innerHTML = newsItems + newsItems;

        const totalWidth = newsTicker.scrollWidth;
        const duration = totalWidth / 200;
        newsTicker.style.animationDuration = `${duration}s`;
    } catch (error) {
        console.error('Error fetching news:', error);
        const newsTicker = document.getElementById('newsTicker');
        newsTicker.innerHTML = `
            <div class="news-item">
                <i class="fas fa-newspaper"></i>
                <span>Welcome to Adalat - Your Legal Research Assistant</span>
            </div>
            <div class="news-item">
                <i class="fas fa-newspaper"></i>
                <span>Stay updated with the latest legal news and updates</span>
            </div>
        `;
    }
}

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    themeToggle.innerHTML = `<i class="fas fa-${newTheme === 'light' ? 'moon' : 'sun'}"></i>`;
});

// Chat Functionality
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendMessage = document.getElementById('sendMessage');
const newChat = document.getElementById('newChat');

function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    if (isUser) {
        messageDiv.innerHTML = `<p>${message}</p>`;
    } else {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <i class="fas fa-robot me-2"></i>
                <span class="fw-bold">Adalat Assistant</span>
            </div>
            <p>${message}</p>
        `;
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
const BASE_URL = "http://127.0.0.1:5000"; // or your Flask server URL

async function sendPromptToLLM(apiEndpoint, caseDetails) {
    addMessage("⏳ Processing your request. Please wait...");
    try {
        const response = await fetch(BASE_URL + apiEndpoint, { // 👈 Prefix BASE_URL
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ case_details: caseDetails })
        });

        const data = await response.json();

        chatMessages.lastChild.remove(); // Remove loading message

        if (data.error) {
            addMessage(`❌ Error: ${data.error}`);
        } else {
            const key = Object.keys(data)[0]; // roadmap / arguments / analysis
            addMessage(data[key]);
        }
    } catch (error) {
        console.error("Error:", error);
        chatMessages.lastChild.remove();
        addMessage("❌ Something went wrong. Please try again.");
    }
}
// Select buttons by ID (very reliable)
const roadmapBtn = document.getElementById('roadmapBtn');
const argumentsBtn = document.getElementById('argumentsBtn');
const analysisBtn = document.getElementById('analysisBtn');


// Send message logic
sendMessage.addEventListener('click', () => {
    const message = userInput.value.trim();
    if (message) {
        addMessage(message, true);
        sendPromptToLLM("/api/create-case-roadmap", message); // Default action
        userInput.value = '';
    }
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage.click();
    }
});

newChat.addEventListener('click', () => {
    chatMessages.innerHTML = `
        <div class="message assistant-message">
            <div class="d-flex align-items-center mb-2">
                <i class="fas fa-robot me-2"></i>
                <span class="fw-bold">Adalat Assistant</span>
            </div>
            <p>👩‍⚖️ How can I assist you today with your legal case?</p>
        </div>
    `;
});

// Predefined Buttons Logic
roadmapBtn.addEventListener('click', () => {
    const caseDetails = userInput.value.trim();
    if (caseDetails) {
        addMessage(caseDetails, true);
        sendPromptToLLM("/api/create-case-roadmap", caseDetails);
        userInput.value = '';
    }
});

argumentsBtn.addEventListener('click', () => {
    const caseDetails = userInput.value.trim();
    if (caseDetails) {
        addMessage(caseDetails, true);
        sendPromptToLLM("/api/generate-arguments", caseDetails);
        userInput.value = '';
    }
});

analysisBtn.addEventListener('click', () => {
    const caseDetails = userInput.value.trim();
    if (caseDetails) {
        addMessage(caseDetails, true);
        sendPromptToLLM("/api/analyze-evidence", caseDetails);
        userInput.value = '';
    }
});



// IPC Section Finder
function searchIPC() {
    const input = document.getElementById('ipcInput').value.trim().toLowerCase();
    const result = document.getElementById('ipcResult');
    if (!input) return result.innerHTML = "❗ Please enter a section or keyword.";

    const ipcDatabase = {
        "302": "IPC Section 302 - Punishment for Murder",
        "376": "IPC Section 376 - Rape",
        "420": "IPC Section 420 - Cheating and dishonestly inducing delivery of property"
    };

    const found = Object.entries(ipcDatabase).find(([key, value]) => input.includes(key) || value.toLowerCase().includes(input));
    result.innerHTML = found ? `✅ ${found[1]}` : "❌ No IPC section found. Try another term.";
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchNews();
    setInterval(fetchNews, 30000);
});
