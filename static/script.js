// Global variables
let blockchainData = {};

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    refreshData();
});

async function refreshData() {
    try {
        const response = await fetch('/api/blockchain');
        blockchainData = await response.json();

        updateStatusBar();
        displayBlockchain();
        displayPending();
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

function updateStatusBar() {
    const chainStatus = document.getElementById('chainStatus');
    const blockCount = document.getElementById('blockCount');

    chainStatus.textContent = blockchainData.is_valid ? 'Valid' : 'Invalid';
    chainStatus.classList.remove('valid', 'invalid');
    chainStatus.classList.add(blockchainData.is_valid ? 'valid' : 'invalid');

    blockCount.textContent = `${blockchainData.length} blocks`;
}

function displayBlockchain() {
    const container = document.getElementById('blockchainDisplay');
    container.innerHTML = '';

    if (!blockchainData.chain || blockchainData.chain.length === 0) {
        container.innerHTML = '<div class="data-display empty">No blocks in the blockchain</div>';
        return;
    }

    blockchainData.chain.forEach(block => {
        const blockCard = createBlockCard(block);
        container.appendChild(blockCard);
    });
}

function createBlockCard(block) {
    const card = document.createElement('div');
    card.className = 'block-card';

    card.innerHTML = `
        <div class="block-header">
            <div class="block-index">Block #${block.index}</div>
            <div class="block-timestamp">${new Date(block.timestamp * 1000).toLocaleString()}</div>
        </div>

        <div class="block-info">
            <div class="info-label">Previous Hash</div>
            <div class="info-value">${block.previous_hash}</div>
        </div>

        <div class="block-info">
            <div class="info-label">Hash</div>
            <div class="info-value">${block.hash}</div>
        </div>

        <div class="block-data">
            <div class="info-label">Data</div>
            ${createDataRows(block.data)}
        </div>

        <div class="nonce-badge">Nonce: ${block.nonce}</div>
    `;

    return card;
}

function createDataRows(data) {
    return Object.entries(data).map(([key, value]) => `
        <div class="data-row">
            <span class="data-key">${key}:</span>
            <span class="data-value">${JSON.stringify(value)}</span>
        </div>
    `).join('');
}

async function displayPending() {
    try {
        const response = await fetch('/api/pending');
        const pendingData = await response.json();

        const container = document.getElementById('pendingData');

        if (!pendingData.pending_data || Object.keys(pendingData.pending_data).length === 0) {
            container.className = 'data-display empty';
            container.textContent = 'No pending transactions';
            return;
        }

        container.className = 'data-display';
        container.innerHTML = createDataRows(pendingData.pending_data);
    } catch (error) {
        console.error('Error loading pending data:', error);
    }
}

async function validateChain() {
    try {
        const response = await fetch('/api/validate');
        const result = await response.json();

        alert(result.message);
        refreshData();
    } catch (error) {
        console.error('Error validating chain:', error);
    }
}

async function mineBlock() {
    try {
        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const result = await response.json();

        if (result.success) {
            alert('Block mined successfully!');
        } else {
            alert('Error mining block: ' + result.error);
        }

        refreshData();
    } catch (error) {
        console.error('Error mining block:', error);
    }
}

async function showAddData() {
    // This would show a modal for adding data - simplified for now
    const attributes = blockchainData.schema;
    const formHtml = Object.keys(attributes).map(attr => `
        <div class="form-group">
            <label for="${attr}">${attr}:</label>
            <input type="text" id="${attr}" name="${attr}" placeholder="Enter ${attr} value">
        </div>
    `).join('');

    document.getElementById('formFields').innerHTML = formHtml;
    document.getElementById('addDataModal').classList.add('active');
}

function hideAddData() {
    document.getElementById('addDataModal').classList.remove('active');
}

async function submitAddData() {
    const formData = {};
    const inputs = document.querySelectorAll('#addDataForm input');

    inputs.forEach(input => {
        const key = input.name;
        const value = input.value.trim();

        // Basic type inference
        if (!isNaN(value) && value.includes('.')) {
            formData[key] = parseFloat(value);
        } else if (!isNaN(value)) {
            formData[key] = parseInt(value);
        } else if (value.startsWith('"') && value.endsWith('"')) {
            formData[key] = value.slice(1, -1);
        } else {
            formData[key] = value;
        }
    });

    try {
        const response = await fetch('/api/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (result.success) {
            alert('Data added to pending transactions');
            hideAddData();
            refreshData();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error adding data:', error);
    }
}

// Handle form submission
document.getElementById('addDataForm').addEventListener('submit', function(e) {
    e.preventDefault();
    submitAddData();
});

async function executeCommand() {
    const commandInput = document.getElementById('commandInput');
    const commandOutput = document.getElementById('commandOutput');
    const command = commandInput.value.trim();

    if (!command) {
        commandOutput.textContent = 'Please enter a command';
        return;
    }

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command }),
        });

        const result = await response.json();

        if (result.success) {
            commandOutput.textContent = result.output;
            refreshData(); // Refresh to show any changes
        } else {
            commandOutput.textContent = 'Error: ' + result.error;
        }
    } catch (error) {
        console.error('Error executing command:', error);
        commandOutput.textContent = 'Error: ' + error.message;
    }
}
