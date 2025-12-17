// Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const numStocksSlider = document.getElementById('numStocks');
const numStocksValue = document.getElementById('numStocksValue');
const timeEstimate = document.getElementById('timeEstimate');
const customSymbolsInput = document.getElementById('customSymbols');
const getRecommendationsBtn = document.getElementById('getRecommendations');
const loadingContainer = document.getElementById('loadingContainer');
const loadingText = document.getElementById('loadingText');
const progressFill = document.getElementById('progressFill');
const resultsSection = document.getElementById('resultsSection');
const resultsSummary = document.getElementById('resultsSummary');
const topCards = document.getElementById('topCards');
const tableBody = document.getElementById('tableBody');
const errorMessage = document.getElementById('errorMessage');
const apiStatus = document.getElementById('apiStatus');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkApiStatus();
    updateTimeEstimate();
    
    numStocksSlider.addEventListener('input', () => {
        numStocksValue.textContent = numStocksSlider.value;
        updateTimeEstimate();
    });
    
    getRecommendationsBtn.addEventListener('click', fetchRecommendations);
});

// Check API Status
async function checkApiStatus() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_BASE_URL}/`, { 
            signal: controller.signal,
            method: 'GET'
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            apiStatus.className = 'api-status connected';
            apiStatus.querySelector('.status-text').textContent = 'FastAPI Connected ✓';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        // Retry after a short delay
        setTimeout(checkApiStatus, 2000);
        apiStatus.className = 'api-status';
        apiStatus.querySelector('.status-text').textContent = 'Connecting to FastAPI...';
    }
}

// Update Time Estimate
function updateTimeEstimate() {
    const numStocks = parseInt(numStocksSlider.value);
    const estimatedSeconds = numStocks * 12;
    const estimatedMinutes = estimatedSeconds / 60;
    
    if (estimatedSeconds >= 60) {
        timeEstimate.textContent = `⏱️ Estimated time: ~${estimatedMinutes.toFixed(1)} minutes (${estimatedSeconds} seconds)`;
    } else {
        timeEstimate.textContent = `⏱️ Estimated time: ~${estimatedSeconds} seconds`;
    }
}

// Fetch Recommendations
async function fetchRecommendations() {
    const numStocks = parseInt(numStocksSlider.value);
    const customSymbols = customSymbolsInput.value.trim();
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';
    
    // Show loading
    loadingContainer.style.display = 'block';
    getRecommendationsBtn.disabled = true;
    
    // Calculate estimated time
    const estimatedSeconds = numStocks * 12;
    const estimatedMinutes = estimatedSeconds / 60;
    const timeMsg = estimatedSeconds >= 60 
        ? `This will take approximately ${estimatedMinutes.toFixed(1)} minutes (${estimatedSeconds} seconds)`
        : `This will take approximately ${estimatedSeconds} seconds`;
    
    loadingText.textContent = `Fetching live stock data for ${numStocks} stocks... ${timeMsg}. Please wait...`;
    
    // Simulate progress (since we can't track actual API progress)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 100 / estimatedSeconds;
        if (progress > 95) progress = 95; // Don't complete until done
        progressFill.style.width = `${progress}%`;
    }, 1000);
    
    try {
        // Build request parameters
        const params = new URLSearchParams({ limit: numStocks.toString() });
        if (customSymbols) {
            params.append('symbols', customSymbols);
        }
        
        // Calculate timeout (estimated time + 60 seconds buffer)
        const timeout = Math.max(estimatedSeconds * 1000 + 60000, 120000);
        
        // Make API request
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(`${API_BASE_URL}/recommendations?${params}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        clearInterval(progressInterval);
        let errorMsg = 'Failed to connect to FastAPI. Make sure the API server is running on http://localhost:8000';
        if (error.name === 'AbortError') {
            errorMsg = 'Request timeout. The API took too long to respond. Please try again or analyze fewer stocks.';
        } else if (error.message) {
            errorMsg = error.message;
        }
        displayError(errorMsg);
    } finally {
        loadingContainer.style.display = 'none';
        getRecommendationsBtn.disabled = false;
    }
}

// Display Results
function displayResults(data) {
    const recommendations = data.recommendations || [];
    const totalAnalyzed = data.total_analyzed || 0;
    
    if (recommendations.length === 0) {
        displayError('No positive predictions found. Try different stocks or check back later.');
        return;
    }
    
    // Update summary
    resultsSummary.textContent = `✅ Analyzed ${totalAnalyzed} stocks and found ${recommendations.length} recommendations`;
    
    // Display top 3 cards
    displayTopCards(recommendations.slice(0, 3));
    
    // Display full table
    displayTable(recommendations);
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display Top 3 Cards
function displayTopCards(topThree) {
    topCards.innerHTML = '';
    
    topThree.forEach((rec, index) => {
        const rank = index + 1;
        const card = document.createElement('div');
        card.className = `top-card rank-${rank}`;
        
        card.innerHTML = `
            <div class="top-card-rank">Rank #${rank}</div>
            <div class="top-card-symbol">${rec.symbol}</div>
            <div class="top-card-price">$${rec.predicted_price.toFixed(2)}</div>
            <div class="top-card-change">
                +${rec.predicted_change_percent.toFixed(2)}% 
                ($${rec.predicted_change.toFixed(2)})
            </div>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.9;">
                Current: $${rec.current_price.toFixed(2)}
            </div>
        `;
        
        topCards.appendChild(card);
    });
}

// Display Table
function displayTable(recommendations) {
    tableBody.innerHTML = '';
    
    recommendations.forEach((rec, index) => {
        const rank = index + 1;
        const row = document.createElement('tr');
        
        const changeClass = rec.predicted_change_percent >= 0 ? 'change-positive' : 'change-negative';
        const directionClass = rec.predicted_change_percent >= 0 ? 'direction-up' : 'direction-down';
        const directionIcon = rec.predicted_change_percent >= 0 ? '📈' : '📉';
        
        // Data drift indicator
        let driftIndicator = '';
        if (rec.data_drift) {
            const severity = rec.data_drift.severity || 'none';
            if (severity === 'high') {
                driftIndicator = '<span style="color: #ff0066;">🔴 High Drift</span>';
            } else if (severity === 'medium') {
                driftIndicator = '<span style="color: #f59e0b;">⚡ Medium Drift</span>';
            } else if (severity === 'low') {
                driftIndicator = '<span style="color: #00ff88;">⚠️ Low Drift</span>';
            } else {
                driftIndicator = '<span style="color: #00ff88;">✅ No Drift</span>';
            }
        }
        
        row.innerHTML = `
            <td>
                <span class="rank-badge rank-${rank <= 3 ? rank : ''}">${rank}</span>
            </td>
            <td><span class="symbol">${rec.symbol}</span></td>
            <td><span class="price">$${rec.current_price.toFixed(2)}</span></td>
            <td><span class="price">$${rec.predicted_price.toFixed(2)}</span></td>
            <td class="${changeClass}">
                ${rec.predicted_change >= 0 ? '+' : ''}$${rec.predicted_change.toFixed(2)}
            </td>
            <td class="${changeClass}">
                ${rec.predicted_change_percent >= 0 ? '+' : ''}${rec.predicted_change_percent.toFixed(2)}%
            </td>
            <td class="${directionClass}">
                ${directionIcon} ${rec.direction}
            </td>
            <td>${driftIndicator}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Display Error
function displayError(message) {
    errorMessage.textContent = `❌ Error: ${message}`;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

