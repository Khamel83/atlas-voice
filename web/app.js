// Atlas Voice - Frontend JavaScript

let currentPatternId = null;
let currentPromptId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPatterns();
    setupEventListeners();
});

function setupEventListeners() {
    // Import form
    document.getElementById('import-form').addEventListener('submit', handleImport);

    // Generate form
    document.getElementById('generate-form').addEventListener('submit', handleGenerate);

    // Refresh patterns
    document.getElementById('refresh-patterns').addEventListener('click', loadPatterns);

    // Copy prompt
    document.getElementById('copy-prompt').addEventListener('click', copyPrompt);

    // Download prompt
    document.getElementById('download-prompt').addEventListener('click', downloadPrompt);

    // Privacy report
    document.getElementById('view-privacy').addEventListener('click', showPrivacyReport);
}

// Import & Analyze
async function handleImport(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const statusEl = document.getElementById('import-status');

    // Show loading
    statusEl.className = 'status info';
    statusEl.textContent = 'Uploading and analyzing...';
    statusEl.classList.remove('hidden');

    try {
        const response = await fetch('/api/import', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Import failed');
        }

        const data = await response.json();

        // Show success
        statusEl.className = 'status success';
        statusEl.innerHTML = `
            ✓ Success! Analyzed ${data.stats.total_words.toLocaleString()} words<br>
            Profile: ${data.name}
        `;

        // Reset form
        form.reset();

        // Reload patterns
        await loadPatterns();

        // Auto-select the new pattern
        selectPattern(data.pattern_id);

    } catch (error) {
        statusEl.className = 'status error';
        statusEl.textContent = '✗ Error: ' + error.message;
    }
}

// Load patterns
async function loadPatterns() {
    try {
        const response = await fetch('/api/patterns');
        const data = await response.json();

        const listEl = document.getElementById('patterns-list');

        if (data.patterns.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No voice patterns yet. Import your writing above.</p>';
            return;
        }

        listEl.innerHTML = data.patterns.map(pattern => `
            <div class="pattern-item" data-pattern-id="${pattern.id}">
                <h4>${pattern.name}</h4>
                <p>${pattern.source_description}</p>
                <div class="pattern-stats">
                    <span class="stat"><strong>${pattern.total_words.toLocaleString()}</strong> words</span>
                    <span class="stat"><strong>${pattern.total_sentences.toLocaleString()}</strong> sentences</span>
                    <span class="stat">Created ${new Date(pattern.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.pattern-item').forEach(item => {
            item.addEventListener('click', () => {
                selectPattern(item.dataset.patternId);
            });
        });

    } catch (error) {
        console.error('Failed to load patterns:', error);
    }
}

// Select a pattern
function selectPattern(patternId) {
    currentPatternId = patternId;

    // Update UI
    document.querySelectorAll('.pattern-item').forEach(item => {
        if (item.dataset.patternId === patternId) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });

    // Show generate section
    document.getElementById('selected-pattern-id').value = patternId;
    document.getElementById('generate-section').classList.remove('hidden');

    // Scroll to generate section
    document.getElementById('generate-section').scrollIntoView({ behavior: 'smooth' });
}

// Generate prompt
async function handleGenerate(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const statusEl = document.getElementById('generate-status');

    // Show loading
    statusEl.className = 'status info';
    statusEl.textContent = 'Generating your voice prompt...';
    statusEl.classList.remove('hidden');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Generation failed');
        }

        const data = await response.json();

        // Hide status
        statusEl.classList.add('hidden');

        // Show result
        currentPromptId = data.prompt_id;
        document.getElementById('prompt-text').textContent = data.prompt_text;
        document.getElementById('result-section').classList.remove('hidden');

        // Scroll to result
        document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        statusEl.className = 'status error';
        statusEl.textContent = '✗ Error: ' + error.message;
    }
}

// Copy prompt to clipboard
async function copyPrompt() {
    const promptText = document.getElementById('prompt-text').textContent;
    const statusEl = document.getElementById('copy-status');

    try {
        await navigator.clipboard.writeText(promptText);

        statusEl.className = 'status success';
        statusEl.textContent = '✓ Copied to clipboard!';
        statusEl.classList.remove('hidden');

        setTimeout(() => {
            statusEl.classList.add('hidden');
        }, 3000);

    } catch (error) {
        statusEl.className = 'status error';
        statusEl.textContent = '✗ Failed to copy';
        statusEl.classList.remove('hidden');
    }
}

// Download prompt
function downloadPrompt() {
    if (!currentPromptId) return;

    window.location.href = `/api/prompts/${currentPromptId}/download`;
}

// Show privacy report
async function showPrivacyReport() {
    try {
        const response = await fetch('/api/privacy');
        const data = await response.json();

        const message = `
PRIVACY REPORT
${'='.repeat(60)}

✓ ${data.guarantee}

Current Storage:
  - Voice patterns: ${data.stats.patterns_count}
  - Words analyzed: ${data.stats.total_words_analyzed.toLocaleString()}
  - Original content stored: ${data.stats.original_content_stored}
  - Database size: ${data.stats.database_size_kb} KB

What We Store:
${data.what_we_store.map(item => `  • ${item}`).join('\n')}

What We DON'T Store:
${data.what_we_dont_store.map(item => `  • ${item}`).join('\n')}
        `.trim();

        alert(message);

    } catch (error) {
        alert('Failed to load privacy report');
    }
}
