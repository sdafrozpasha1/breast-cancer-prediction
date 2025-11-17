// Production API URL
const API_URL = 'https://breast-cancer-prediction-z4zt.onrender.com/api';

// Initialize app - skip login and go straight to dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Hide login/register pages
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'none';
    
    // Show dashboard immediately
    document.getElementById('dashboardPage').classList.add('active');
    document.getElementById('userName').textContent = 'Guest User';
    
    // Load initial content
    loadDashboard();
});

// Page Navigation
function showPage(pageName) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    document.getElementById(`${pageName}Content`).classList.add('active');
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    if (pageName === 'educational') {
        loadEducationalResources();
    }
}

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.getAttribute('data-page');
        showPage(page);
    });
});

// Prediction Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.getAttribute('data-tab');
        
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tab}Tab`).classList.add('active');
    });
});

// Symptom-Based Prediction
document.getElementById('symptomForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch(`${API_URL}/predict/symptom-based`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayPredictionResult(result);
        } else {
            alert(result.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error connecting to server. Please try again.');
    }
});

// Technical Prediction
document.getElementById('technicalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch(`${API_URL}/predict/technical`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayPredictionResult(result);
        } else {
            alert(result.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error connecting to server. Please try again.');
    }
});

function displayPredictionResult(result) {
    const resultBox = document.getElementById('predictionResult');
    const resultContent = document.getElementById('resultContent');
    
    let html = '';
    
    if (result.type === 'symptom-based') {
        html = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #667eea; margin-bottom: 10px;">Risk Assessment</h4>
                <p style="font-size: 24px; font-weight: bold; color: ${result.risk_percentage > 60 ? '#dc3545' : result.risk_percentage > 30 ? '#ffc107' : '#28a745'};">
                    ${result.outcome}
                </p>
                <p style="font-size: 18px; margin-top: 10px;">
                    Risk Percentage: <strong>${result.risk_percentage}%</strong>
                </p>
            </div>
            <div style="padding: 15px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                <p style="color: #856404; margin: 0;">
                    <strong>Important:</strong> This is a preliminary assessment. Please consult with a healthcare professional for proper diagnosis and treatment.
                </p>
            </div>
        `;
    } else {
        html = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #667eea; margin-bottom: 10px;">Medical Analysis</h4>
                <p style="font-size: 24px; font-weight: bold; color: ${result.outcome === 'Malignant' ? '#dc3545' : '#28a745'};">
                    ${result.outcome}
                </p>
                <div style="margin-top: 15px;">
                    <p style="font-size: 16px;">
                        Malignant Probability: <strong>${result.malignant_probability}%</strong>
                    </p>
                    <p style="font-size: 16px;">
                        Benign Probability: <strong>${result.benign_probability}%</strong>
                    </p>
                </div>
            </div>
            <div style="padding: 15px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                <p style="color: #856404; margin: 0;">
                    <strong>Important:</strong> This prediction is based on medical measurements. Always consult with an oncologist for proper diagnosis.
                </p>
            </div>
        `;
    }
    
    // Add prevention recommendations
    if (result.preventions && result.preventions.length > 0) {
        html += `
            <div style="margin-top: 30px;">
                <h4 style="color: #667eea; margin-bottom: 15px;">📋 Personalized Prevention & Action Plan</h4>
                <div style="display: grid; gap: 15px;">
        `;
        
        result.preventions.forEach(prevention => {
            const priorityColor = prevention.priority === 'Urgent' ? '#dc3545' : 
                                 prevention.priority === 'High' ? '#ff6b6b' : 
                                 prevention.priority === 'Medium' ? '#ffc107' : '#28a745';
            
            html += `
                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid ${priorityColor};">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <h5 style="color: #333; margin: 0; font-size: 16px;">
                            ${prevention.category}
                        </h5>
                        <span style="background: ${priorityColor}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                            ${prevention.priority}
                        </span>
                    </div>
                    <p style="color: #555; font-weight: 600; margin: 8px 0;">
                        ${prevention.recommendation}
                    </p>
                    <p style="color: #666; font-size: 14px; margin: 0;">
                        ${prevention.details}
                    </p>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    resultContent.innerHTML = html;
    resultBox.style.display = 'block';
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

// AI Assistance
document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = document.getElementById('chatQuestion').value;
    const chatMessages = document.getElementById('chatMessages');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = question;
    chatMessages.appendChild(userMsg);
    
    document.getElementById('chatQuestion').value = '';
    
    try {
        const response = await fetch(`${API_URL}/ai-assistance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Add AI response
        const aiMsg = document.createElement('div');
        aiMsg.className = 'message ai';
        aiMsg.textContent = data.response;
        chatMessages.appendChild(aiMsg);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        alert('Error connecting to server. Please try again.');
    }
});

// Educational Resources
async function loadEducationalResources() {
    try {
        const response = await fetch(`${API_URL}/educational-resources`);
        
        const resources = await response.json();
        const resourcesList = document.getElementById('resourcesList');
        
        resourcesList.innerHTML = resources.map(resource => `
            <div class="resource-card">
                <h3>${resource.title}</h3>
                <p>${resource.description}</p>
                <span class="category">${resource.category}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading resources:', error);
    }
}

// Dashboard
function loadDashboard() {
    // Simple dashboard without history
    document.getElementById('totalPredictions').textContent = '0';
    document.getElementById('lastPrediction').textContent = 'No predictions yet';
}

// Hide logout button since no authentication
document.getElementById('logoutBtn').style.display = 'none';
