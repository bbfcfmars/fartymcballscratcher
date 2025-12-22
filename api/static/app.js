// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const searchForm = document.getElementById('searchForm');
const settingsForm = document.getElementById('settingsForm');
const fileInput = document.getElementById('file');
const dropZone = document.getElementById('dropZone');
const fileName = document.getElementById('fileName');
const uploadStatus = document.getElementById('uploadStatus');
const results = document.getElementById('results');
const settingsModal = document.getElementById('settingsModal');
const settingsBtn = document.getElementById('settingsBtn');
const closeSettings = document.getElementById('closeSettings');
const apiKeyWarning = document.getElementById('apiKeyWarning');
const configureKeyLink = document.getElementById('configureKeyLink');
const apiKeyStatus = document.getElementById('apiKeyStatus');

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;

        // Update tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${targetTab}Tab`).classList.add('active');
    });
});

// File input handling
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `📄 ${file.name} (${formatFileSize(file.size)})`;
        fileName.classList.add('show');
    }
});

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file) {
        fileInput.files = e.dataTransfer.files;
        fileName.textContent = `📄 ${file.name} (${formatFileSize(file.size)})`;
        fileName.classList.add('show');
    }
});

// Upload form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const file = fileInput.files[0];

    if (!file) {
        showStatus(uploadStatus, 'Please select a file', 'error');
        return;
    }

    formData.append('file', file);
    formData.append('kind', document.getElementById('kind').value);
    formData.append('title', document.getElementById('title').value);

    const film = document.getElementById('film').value;
    const author = document.getElementById('author').value;

    if (film) formData.append('film', film);
    if (author) formData.append('author', author);

    showStatus(uploadStatus, 'Uploading and processing...', 'loading');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(uploadStatus, `✅ ${data.message}`, 'success');
            uploadForm.reset();
            fileName.classList.remove('show');
        } else {
            showStatus(uploadStatus, `❌ Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, `❌ Error: ${error.message}`, 'error');
    }
});

// Search form submission
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const query = document.getElementById('query').value;
    const filterFilm = document.getElementById('filterFilm').value;
    const filterKind = document.getElementById('filterKind').value;
    const topK = parseInt(document.getElementById('topK').value);

    results.innerHTML = '<div class="status show loading">🔍 Searching...</div>';

    try {
        const requestBody = { query, top_k: topK };
        if (filterFilm) requestBody.film = filterFilm;
        if (filterKind) requestBody.kind = filterKind;

        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data.results);
        } else {
            results.innerHTML = `<div class="status show error">❌ Error: ${data.detail}</div>`;
        }
    } catch (error) {
        results.innerHTML = `<div class="status show error">❌ Error: ${error.message}</div>`;
    }
});

// Settings modal
settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('show');
    checkApiKeyStatus();
});

closeSettings.addEventListener('click', () => {
    settingsModal.classList.remove('show');
});

configureKeyLink.addEventListener('click', (e) => {
    e.preventDefault();
    settingsModal.classList.add('show');
    checkApiKeyStatus();
});

settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.classList.remove('show');
    }
});

// Settings form submission
settingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const apiKey = document.getElementById('apiKey').value;

    if (!apiKey) {
        apiKeyStatus.innerHTML = '<div class="status show error">Please enter an API key</div>';
        return;
    }

    apiKeyStatus.innerHTML = '<div class="status show loading">Saving...</div>';

    try {
        const formData = new FormData();
        formData.append('api_key', apiKey);

        const response = await fetch('/settings/api-key', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            apiKeyStatus.innerHTML = `<div class="status show success">✅ ${data.message}</div>`;
            document.getElementById('apiKey').value = '';
            setTimeout(() => {
                checkApiKeyStatus();
            }, 1500);
        } else {
            apiKeyStatus.innerHTML = `<div class="status show error">❌ ${data.detail}</div>`;
        }
    } catch (error) {
        apiKeyStatus.innerHTML = `<div class="status show error">❌ Error: ${error.message}</div>`;
    }
});

// Check API key status on load
async function checkApiKeyStatus() {
    try {
        const response = await fetch('/settings/api-key');
        const data = await response.json();

        if (data.configured) {
            apiKeyWarning.style.display = 'none';
            apiKeyStatus.innerHTML = `<div class="status show success">✅ API key configured: ${data.key_preview}</div>`;
        } else {
            apiKeyWarning.style.display = 'block';
            apiKeyStatus.innerHTML = '<div class="status show error">⚠️ No API key configured</div>';
        }
    } catch (error) {
        console.error('Error checking API key status:', error);
    }
}

// Display search results
function displayResults(resultsData) {
    if (!resultsData || resultsData.length === 0) {
        results.innerHTML = '<div class="card no-results">No results found. Try a different query or check your filters.</div>';
        return;
    }

    let html = '';

    resultsData.forEach(result => {
        const scorePercent = (result.score * 100).toFixed(1);

        html += `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">${escapeHtml(result.title)}</div>
                    <div class="result-score">${scorePercent}%</div>
                </div>
                <div class="result-meta">
                    <span class="result-badge">📁 ${result.kind}</span>
                    ${result.film ? `<span class="result-badge">🎬 ${escapeHtml(result.film)}</span>` : ''}
                    ${result.author ? `<span class="result-badge">✍️ ${escapeHtml(result.author)}</span>` : ''}
                    <span class="result-badge">Chunk ${result.chunk_index + 1}</span>
                </div>
                <div class="result-text">${escapeHtml(result.text)}</div>
            </div>
        `;
    });

    results.innerHTML = html;
}

// Utility functions
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status show ${type}`;
    element.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check API key on page load
checkApiKeyStatus();
