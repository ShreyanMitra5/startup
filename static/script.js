document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBiasResults(data.original, data.biased);
            createVisualizations(data.original.visualization_data, data.biased.visualization_data);
            addDownloadButton(data.biased.download_link);
        } else {
            alert(data.error || 'Error processing file');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing file');
    }
});

function displayBiasResults(original, biased) {
    const resultsDiv = document.getElementById('biasResults');
    let html = '<div class="bias-results">';
    
    // Original Data Analysis
    html += '<h3>Original Data Analysis</h3>';
    html += createBiasSection(original.bias_metrics, original.bias_present);
    
    // Biased Data Analysis
    html += '<h3>Biased Data Analysis</h3>';
    html += createBiasSection(biased.bias_metrics, biased.bias_present);
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

function createBiasSection(metrics, biasPresent) {
    let html = '<div class="bias-section">';
    
    // Gender Bias
    const genderDiff = Math.abs(metrics.gender_bias.male_approval_rate - metrics.gender_bias.female_approval_rate);
    html += `
        <div class="bias-metric ${biasPresent.gender_bias ? 'bias-detected' : ''}">
            <h4>Gender Bias Analysis</h4>
            <p>Male Approval Rate: ${(metrics.gender_bias.male_approval_rate * 100).toFixed(1)}%</p>
            <p>Female Approval Rate: ${(metrics.gender_bias.female_approval_rate * 100).toFixed(1)}%</p>
            <p>Difference: ${(genderDiff * 100).toFixed(1)}%</p>
            ${biasPresent.gender_bias ? '<div class="alert alert-warning">Gender bias detected!</div>' : ''}
        </div>
    `;
    
    // Income Bias
    const incomeDiff = Math.abs(metrics.income_bias.male_avg_income - metrics.income_bias.female_avg_income);
    html += `
        <div class="bias-metric ${biasPresent.income_bias ? 'bias-detected' : ''}">
            <h4>Income Bias Analysis</h4>
            <p>Male Average Income: $${metrics.income_bias.male_avg_income.toFixed(2)}</p>
            <p>Female Average Income: $${metrics.income_bias.female_avg_income.toFixed(2)}</p>
            <p>Difference: $${incomeDiff.toFixed(2)}</p>
            ${biasPresent.income_bias ? '<div class="alert alert-warning">Income bias detected!</div>' : ''}
        </div>
    `;
    
    // Credit Score Bias
    const creditDiff = Math.abs(metrics.credit_score_bias.male_avg_credit - metrics.credit_score_bias.female_avg_credit);
    html += `
        <div class="bias-metric ${biasPresent.credit_score_bias ? 'bias-detected' : ''}">
            <h4>Credit Score Bias Analysis</h4>
            <p>Male Average Credit Score: ${metrics.credit_score_bias.male_avg_credit.toFixed(1)}</p>
            <p>Female Average Credit Score: ${metrics.credit_score_bias.female_avg_credit.toFixed(1)}</p>
            <p>Difference: ${creditDiff.toFixed(1)}</p>
            ${biasPresent.credit_score_bias ? '<div class="alert alert-warning">Credit score bias detected!</div>' : ''}
        </div>
    `;
    
    html += '</div>';
    return html;
}

function createVisualizations(originalData, biasedData) {
    // Gender Distribution
    const genderTrace1 = {
        x: ['Male', 'Female'],
        y: [originalData.gender_distribution.male, originalData.gender_distribution.female],
        name: 'Original',
        type: 'bar',
        marker: { color: '#3498db' }
    };
    
    const genderTrace2 = {
        x: ['Male', 'Female'],
        y: [biasedData.gender_distribution.male, biasedData.gender_distribution.female],
        name: 'Biased',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const genderLayout = {
        title: 'Gender Distribution Comparison',
        barmode: 'group',
        height: 300
    };
    
    Plotly.newPlot('genderDistribution', [genderTrace1, genderTrace2], genderLayout);
    
    // Credit Score Distribution
    const creditTrace1 = {
        x: Object.keys(originalData.credit_score_ranges),
        y: Object.values(originalData.credit_score_ranges),
        name: 'Original',
        type: 'bar',
        marker: { color: '#3498db' }
    };
    
    const creditTrace2 = {
        x: Object.keys(biasedData.credit_score_ranges),
        y: Object.values(biasedData.credit_score_ranges),
        name: 'Biased',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const creditLayout = {
        title: 'Credit Score Distribution Comparison',
        barmode: 'group',
        height: 300
    };
    
    Plotly.newPlot('creditScoreDistribution', [creditTrace1, creditTrace2], creditLayout);
    
    // Income Distribution
    const incomeTrace1 = {
        x: Object.keys(originalData.income_ranges),
        y: Object.values(originalData.income_ranges),
        name: 'Original',
        type: 'bar',
        marker: { color: '#3498db' }
    };
    
    const incomeTrace2 = {
        x: Object.keys(biasedData.income_ranges),
        y: Object.values(biasedData.income_ranges),
        name: 'Biased',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const incomeLayout = {
        title: 'Income Distribution Comparison',
        barmode: 'group',
        height: 300
    };
    
    Plotly.newPlot('incomeDistribution', [incomeTrace1, incomeTrace2], incomeLayout);
    
    // Approval Rates
    const approvalTrace1 = {
        x: ['Male', 'Female'],
        y: [
            originalData.gender_distribution.male / (originalData.gender_distribution.male + originalData.gender_distribution.female) * 100,
            originalData.gender_distribution.female / (originalData.gender_distribution.male + originalData.gender_distribution.female) * 100
        ],
        name: 'Original',
        type: 'bar',
        marker: { color: '#3498db' }
    };
    
    const approvalTrace2 = {
        x: ['Male', 'Female'],
        y: [
            biasedData.gender_distribution.male / (biasedData.gender_distribution.male + biasedData.gender_distribution.female) * 100,
            biasedData.gender_distribution.female / (biasedData.gender_distribution.male + biasedData.gender_distribution.female) * 100
        ],
        name: 'Biased',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const approvalLayout = {
        title: 'Gender Distribution Comparison',
        yaxis: { title: 'Percentage' },
        barmode: 'group',
        height: 300
    };
    
    Plotly.newPlot('approvalRates', [approvalTrace1, approvalTrace2], approvalLayout);
}

function addDownloadButton(downloadLink) {
    const resultsDiv = document.getElementById('biasResults');
    const downloadButton = document.createElement('a');
    downloadButton.href = downloadLink;
    downloadButton.className = 'btn btn-success mt-3';
    downloadButton.innerHTML = '<i class="fas fa-download"></i> Download Biased Data';
    resultsDiv.appendChild(downloadButton);
} 