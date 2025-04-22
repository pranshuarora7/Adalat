let allCases = []; // Store all results to use later in modal

async function searchCases() {
    const input = document.getElementById('caseInput').value.trim();
    if (!input) {
        alert("Please describe your case.");
        return;
    }

    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');

    try {
        const response = await fetch("http://localhost:5000/api/retrieve-similar-cases", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: input })
        });

        const results = await response.json();
        allCases = results; // Save for modal use

        document.getElementById('loading').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');

        const casesContainer = document.getElementById('casesContainer');
        casesContainer.innerHTML = "";

        results.forEach((c, index) => {
            const card = document.createElement('div');
            card.className = "case-card";
            card.innerHTML = `
        <h3>Case ID: ${c.id}</h3>
        <p><strong>Similarity:</strong> ${(c.similarity_score * 100).toFixed(2)}%</p>
        <p>${c.text.substring(0, 150)}...</p>
        <button onclick="openModal(${index})">Read More</button>
      `;
            casesContainer.appendChild(card);
        });

        // Dummy chart
        const won = Math.floor(Math.random() * 60) + 20; // 20% - 80%
        const lost = 100 - won;

        const ctx = document.getElementById('casesChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Won', 'Lost'],
                datasets: [{
                    label: 'Case Outcomes',
                    data: [won, lost],
                    backgroundColor: ['#4CAF50', '#F44336'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });

    } catch (error) {
        console.error(error);
        alert("Something went wrong. Please try again later.");
    }
}

function generateSummary(fullText) {
    // Simple text summarizer: pick first few sentences
    const sentences = fullText.split('. ');
    let summary = sentences.slice(0, 4).join('. ') + '.';
    if (summary.length > 500) {
        summary = summary.substring(0, 500) + '...';
    }
    return summary;
}
function openModal(index) {
    const modal = document.getElementById('caseModal');
    const modalText = document.getElementById('modalText');

    const caseData = allCases[index];

    // Inject full details + summarize button
    modalText.innerHTML = `
        <h3>Case ID: ${caseData.id}</h3>
        <p><strong>Similarity:</strong> ${(caseData.similarity_score * 100).toFixed(2)}%</p>
        <p id="fullCaseText" style="margin-top:1rem;">${caseData.text}</p>
        <button id="summarizeButton" class="expand-btn" style="margin-top:2rem;">Summarize</button>
    `;

    // Open modal
    modal.classList.add('show');

    // Now bind summarize button
    const summarizeButton = document.getElementById('summarizeButton');
    summarizeButton.addEventListener('click', function () {
        showSummary(caseData);
    });
}

function showSummary(caseData) {
    const modalText = document.getElementById('modalText');

    // Dummy values for now (you can adjust if you have real fields)
    const court = "Supreme Court";
    const date = "12-April-2024";
    const result = Math.random() > 0.5 ? "Won" : "Lost"; // Random win/loss for now
    const shortSummary = generateSummary(caseData.text);

    modalText.innerHTML = `
        <h3>Case Summary</h3>
        <p><strong>Court:</strong> ${court}</p>
        <p><strong>Date:</strong> ${date}</p>
        <p><strong>Result:</strong> ${result}</p>
        <p><strong>Summary:</strong> ${shortSummary}</p>
        <button onclick="closeModal()" class="expand-btn" style="margin-top:2rem;">Close</button>
    `;
}


function closeModal() {
    const modal = document.getElementById('caseModal');
    modal.classList.remove('show');
}

// Close modal if click outside the modal content
window.onclick = function (event) {
    const modal = document.getElementById('caseModal');
    if (event.target == modal) {
        closeModal();
    }
}
