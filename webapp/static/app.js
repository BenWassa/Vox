

let currentCard = null;
let mode = 'guess-english'; // 'guess-english' or 'guess-hanzi'
const cardContainer = document.getElementById('card-container');
const hanzi = document.getElementById('hanzi');
const pinyin = document.getElementById('pinyin');
const english = document.getElementById('english');
const revealBtn = document.getElementById('reveal');
const correctBtn = document.getElementById('correct');
const incorrectBtn = document.getElementById('incorrect');
const modeLabel = document.getElementById('mode-label');

function showTab(name) {
    document.querySelectorAll('.tab').forEach(div => div.classList.add('hidden'));
    document.getElementById(name).classList.remove('hidden');
    if (name === 'vocab') loadCard();
    if (name === 'grammar') loadGrammar();
    if (name === 'dashboard') loadStats();
}

async function loadCard() {
    setLoading(true);
    try {
        const response = await fetch('/api/card');
        if (!response.ok) throw new Error('Failed to fetch card');
        const data = await response.json();
        if (!data.available) {
            pinyin.textContent = '';
            english.textContent = '';
            hanzi.textContent = 'All done!';
            revealBtn.disabled = true;
            correctBtn.disabled = true;
            incorrectBtn.disabled = true;
            modeLabel.textContent = '';
            currentCard = null;
            setLoading(false);
            return;
        }
        currentCard = data.card;
        if (mode === 'guess-english') {
            hanzi.textContent = data.card.hanzi;
            pinyin.textContent = data.card.pinyin;
            english.textContent = '?';
            modeLabel.textContent = 'Guess the English meaning';
        } else {
            hanzi.textContent = '?';
            pinyin.textContent = '';
            english.textContent = data.card.english;
            modeLabel.textContent = 'Guess the Hanzi and Pinyin';
        }
        revealBtn.disabled = false;
        correctBtn.disabled = true;
        incorrectBtn.disabled = true;
    } catch (err) {
        showError('Could not load card. Please try again.');
    }
    setLoading(false);
}

function reveal() {
    if (!currentCard) return;
    if (mode === 'guess-english') {
        english.textContent = currentCard.english;
    } else {
        hanzi.textContent = currentCard.hanzi;
        pinyin.textContent = currentCard.pinyin;
    }
    correctBtn.disabled = false;
    incorrectBtn.disabled = false;
    revealBtn.disabled = true;
}

async function mark(correct) {
    if (!currentCard) return;
    setLoading(true);
    try {
        await fetch(`/api/card/${currentCard.id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({correct})
        });
        await loadCard();
    } catch (err) {
        showError('Could not submit answer.');
    }
    setLoading(false);
}

function switchMode() {
    mode = (mode === 'guess-english') ? 'guess-hanzi' : 'guess-english';
    loadCard();
}

async function loadGrammar() {
    setLoading(true);
    try {
        const response = await fetch('/api/grammar');
        if (!response.ok) throw new Error('Failed to fetch grammar');
        const items = await response.json();
        const table = document.getElementById('grammar-table');
        table.innerHTML = '<tr><th>ID</th><th>Pattern</th><th>Status</th></tr>';
        items.forEach(pt => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${pt.id}</td><td>${pt.pattern}</td><td>
                <select onchange="updateGrammar(${pt.id}, this.value)">
                    <option value="unseen" ${pt.status=='unseen'?'selected':''}>unseen</option>
                    <option value="seen" ${pt.status=='seen'?'selected':''}>seen</option>
                    <option value="practiced" ${pt.status=='practiced'?'selected':''}>practiced</option>
                    <option value="mastered" ${pt.status=='mastered'?'selected':''}>mastered</option>
                </select></td>`;
            table.appendChild(tr);
        });
    } catch (err) {
        showError('Could not load grammar points.');
    }
    setLoading(false);
}

async function updateGrammar(id, status) {
    try {
        await fetch(`/api/grammar/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
    } catch (err) {
        showError('Could not update grammar point.');
    }
}

async function loadStats() {
    setLoading(true);
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const stats = await response.json();
        document.getElementById('stats').textContent = JSON.stringify(stats, null, 2);
    } catch (err) {
        showError('Could not load dashboard stats.');
    }
    setLoading(false);
}


// Loading indicator helpers
function setLoading(isLoading) {
    if (isLoading) {
        document.body.classList.add('loading');
    } else {
        document.body.classList.remove('loading');
    }
}

// Error feedback
function showError(msg) {
    let err = document.getElementById('error-message');
    if (!err) {
        err = document.createElement('div');
        err.id = 'error-message';
        err.style.position = 'fixed';
        err.style.top = '20px';
        err.style.left = '50%';
        err.style.transform = 'translateX(-50%)';
        err.style.background = '#ef4444';
        err.style.color = 'white';
        err.style.padding = '12px 24px';
        err.style.borderRadius = '8px';
        err.style.zIndex = '9999';
        err.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        document.body.appendChild(err);
    }
    err.textContent = msg;
    err.style.display = 'block';
    setTimeout(() => { err.style.display = 'none'; }, 3000);
}

// Client-side validation for input (future extension)
// Example: validate user input before marking correct/incorrect

showTab('vocab');
