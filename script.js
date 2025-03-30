// Load and process the data
let correctData = [];
let biasedData = [];

// Function to load CSV data
async function loadData() {
    try {
        const response = await fetch('loan.csv');
        const csvText = await response.text();
        const result = Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true
        });
        
        correctData = result.data;
        biasedData = createBiasedData(correctData);
        
        // Create initial visualizations
        createVisualizations();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Function to create biased data
function createBiasedData(data) {
    return data.map(record => {
        const biasedRecord = { ...record };
        // Introduce bias based on gender
        if (biasedRecord.gender === 'Female') {
            // Lower credit score for females
            biasedRecord.credit_score = Math.max(500, parseInt(biasedRecord.credit_score) - 20);
            // Lower income for females
            biasedRecord.income = Math.max(20000, parseInt(biasedRecord.income) * 0.9);
        }
        return biasedRecord;
    });
}

// Function to create visualizations
function createVisualizations() {
    // Gender distribution visualization
    const genderData = {
        correct: calculateGenderDistribution(correctData),
        biased: calculateGenderDistribution(biasedData)
    };

    // Create gender distribution plot
    const genderTrace1 = {
        x: ['Male', 'Female'],
        y: [genderData.correct.male, genderData.correct.female],
        name: 'Correct Data',
        type: 'bar',
        marker: { color: '#3498db' }
    };

    const genderTrace2 = {
        x: ['Male', 'Female'],
        y: [genderData.biased.male, genderData.biased.female],
        name: 'Biased Data',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };

    const genderLayout = {
        title: 'Gender Distribution in Loan Applications',
        barmode: 'group',
        height: 400
    };

    Plotly.newPlot('correctData', [genderTrace1, genderTrace2], genderLayout);

    // Credit score distribution visualization
    const creditData = {
        correct: calculateCreditScoreDistribution(correctData),
        biased: calculateCreditScoreDistribution(biasedData)
    };

    const creditTrace1 = {
        x: Object.keys(creditData.correct),
        y: Object.values(creditData.correct),
        name: 'Correct Data',
        type: 'bar',
        marker: { color: '#3498db' }
    };

    const creditTrace2 = {
        x: Object.keys(creditData.biased),
        y: Object.values(creditData.biased),
        name: 'Biased Data',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };

    const creditLayout = {
        title: 'Credit Score Distribution',
        barmode: 'group',
        height: 400
    };

    Plotly.newPlot('biasedData', [creditTrace1, creditTrace2], creditLayout);
}

// Helper function to calculate gender distribution
function calculateGenderDistribution(data) {
    const distribution = {
        male: 0,
        female: 0
    };
    
    data.forEach(record => {
        if (record.gender === 'Male') {
            distribution.male++;
        } else {
            distribution.female++;
        }
    });
    
    return distribution;
}

// Helper function to calculate credit score distribution
function calculateCreditScoreDistribution(data) {
    const distribution = {};
    
    data.forEach(record => {
        const score = Math.floor(parseInt(record.credit_score) / 50) * 50;
        const range = `${score}-${score + 49}`;
        distribution[range] = (distribution[range] || 0) + 1;
    });
    
    return distribution;
}

// Form submission handler
document.getElementById('loanForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        occupation: document.getElementById('occupation').value,
        education_level: document.getElementById('education').value,
        marital_status: document.getElementById('maritalStatus').value,
        income: parseInt(document.getElementById('income').value),
        credit_score: parseInt(document.getElementById('creditScore').value)
    };

    // Simple loan approval logic
    const isApproved = formData.credit_score >= 650 && formData.income >= 50000;
    
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <div class="alert ${isApproved ? 'alert-success' : 'alert-danger'}">
            <h3>Loan Application Status: ${isApproved ? 'Approved' : 'Denied'}</h3>
            <p>Based on your credit score and income, your application has been ${isApproved ? 'approved' : 'denied'}.</p>
        </div>
    `;
});

// Load data when the page loads
document.addEventListener('DOMContentLoaded', loadData); 