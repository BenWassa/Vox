
let currentCard = null;
let mode = 'guess-english'; // 'guess-english' or 'guess-hanzi'

function showTab(name) {
    document.querySelectorAll('.tab').forEach(div => div.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    if (name === 'vocab') loadCard();
    if (name === 'grammar') loadGrammar();
    if (name === 'dashboard') loadStats();
}

function loadCard() {
    fetch('/api/card').then(r => r.json()).then(data => {
        const pinyin = document.getElementById('pinyin');
        const english = document.getElementById('english');
        const hanzi = document.getElementById('hanzi');
        const revealBtn = document.getElementById('reveal');
        const correctBtn = document.getElementById('correct');
        const incorrectBtn = document.getElementById('incorrect');
        const modeLabel = document.getElementById('mode-label');

        if (!data.available) {
            pinyin.innerText = '';
            english.innerText = '';
            hanzi.innerText = 'All done!';
            revealBtn.disabled = true;
            correctBtn.disabled = true;
            incorrectBtn.disabled = true;
            modeLabel.innerText = '';
            currentCard = null;
            return;
        }
        currentCard = data.card;
        if (mode === 'guess-english') {
            hanzi.innerText = data.card.hanzi;
            pinyin.innerText = data.card.pinyin;
            english.innerText = '?';
            modeLabel.innerText = 'Guess the English meaning';
        } else {
            hanzi.innerText = '?';
            pinyin.innerText = '';
            english.innerText = data.card.english;
            modeLabel.innerText = 'Guess the Hanzi and Pinyin';
        }
        revealBtn.disabled = false;
        correctBtn.disabled = true;
        incorrectBtn.disabled = true;
    });
}

function reveal() {
    if (!currentCard) return;
    const hanzi = document.getElementById('hanzi');
    const pinyin = document.getElementById('pinyin');
    const english = document.getElementById('english');
    if (mode === 'guess-english') {
        english.innerText = currentCard.english;
    } else {
        hanzi.innerText = currentCard.hanzi;
        pinyin.innerText = currentCard.pinyin;
    }
    document.getElementById('correct').disabled = false;
    document.getElementById('incorrect').disabled = false;
    document.getElementById('reveal').disabled = true;
}

function mark(correct) {
    if (!currentCard) return;
    fetch('/api/card/' + currentCard.id, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({correct: correct})
    }).then(() => loadCard());
}

function switchMode() {
    mode = (mode === 'guess-english') ? 'guess-hanzi' : 'guess-english';
    loadCard();
}

function loadGrammar() {
    fetch('/api/grammar').then(r => r.json()).then(items => {
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
    });
}

function updateGrammar(id, status) {
    fetch('/api/grammar/' + id, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: status})
    });
}

function loadStats() {
    fetch('/api/dashboard').then(r => r.json()).then(stats => {
        document.getElementById('stats').innerText = JSON.stringify(stats, null, 2);
    });
}

showTab('vocab');
