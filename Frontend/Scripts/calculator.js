let totalCasesChecked = 0;
let totalWinProbability = 0;

document.getElementById("calculatorForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form from submitting normally

    const caseDetails = document.getElementById("caseDetails").value.trim();
    const courtType = document.getElementById("courtType").value;
    const evidenceStrength = document.getElementById("evidenceStrength").value;

    if (!caseDetails || !courtType || !evidenceStrength) {
        alert("Please fill in all the fields.");
        return;
    }

    // Show loading spinner
    document.getElementById("loadingSpinner").style.display = "block";
    document.getElementById("probabilityResult").innerHTML = "";
    document.getElementById("suggestions").style.display = "none";
    document.getElementById("similarCasesContainer").innerHTML = "";

    try {
        // Call API to predict win probability
        const response = await fetch("http://localhost:5000/api/predict-win-probability", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ case_details: caseDetails })
        });

        const result = await response.json();

        if (result.probability === undefined) {
            throw new Error("Invalid probability response from server.");
        }

        const probability = (result.probability * 100).toFixed(2); // Convert to percentage
        document.getElementById("probabilityResult").innerHTML = `
            <div class="alert alert-success text-center">
                <h4>Win Probability: ${probability}%</h4>
            </div>
        `;

        // Update dashboard
        totalCasesChecked++;
        totalWinProbability += parseFloat(probability);

        const avgWin = (totalWinProbability / totalCasesChecked).toFixed(2);
        document.getElementById("totalCases").innerText = totalCasesChecked;
        document.getElementById("avgWin").innerText = `${avgWin}%`;

        // Suggestion Logic (basic)
        if (probability > 70) {
            document.getElementById("suggestions").style.display = "block";
            document.getElementById("suggestions").innerText = "✅ Great chance of winning! Proceed confidently.";
        } else if (probability > 40) {
            document.getElementById("suggestions").style.display = "block";
            document.getElementById("suggestions").innerText = "⚖️ 50-50 chance. Gather stronger evidence.";
        } else {
            document.getElementById("suggestions").style.display = "block";
            document.getElementById("suggestions").innerText = "⚠️ Low chance of winning. Reconsider your approach.";
        }

        // Fetch similar cases
        await fetchSimilarCases(caseDetails);

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong. Please try again later.");
    } finally {
        document.getElementById("loadingSpinner").style.display = "none";
    }
});

async function fetchSimilarCases(caseDetails) {
    try {
        const response = await fetch("http://localhost:5000/api/retrieve-similar-cases", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: caseDetails })
        });

        const results = await response.json();

        if (!Array.isArray(results)) {
            throw new Error("Similar cases response is not an array.");
        }

        const container = document.getElementById("similarCasesContainer");
        container.innerHTML = "";

        results.forEach((caseItem) => {
            const col = document.createElement("div");
            col.className = "col-md-6 mb-3";

            const card = document.createElement("div");
            card.className = "card h-100 shadow-sm";

            const cardBody = document.createElement("div");
            cardBody.className = "card-body";

            const similarityScore = (caseItem.similarity_score * 100).toFixed(2);

            cardBody.innerHTML = `
                <h5 class="card-title">Case ID: ${caseItem.id || "N/A"}</h5>
                <p class="card-text"><strong>Similarity:</strong> ${similarityScore}%</p>
                <p class="card-text">${truncateText(caseItem.text || "", 150)}</p>
            `;

            card.appendChild(cardBody);
            col.appendChild(card);
            container.appendChild(col);
        });

    } catch (error) {
        console.error("Error fetching similar cases:", error);
    }
}

function truncateText(text, maxLength) {
    if (!text) return "No description available.";
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + "...";
}
