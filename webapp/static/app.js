let currentCard = null;

function showTab(name) {
    document.querySelectorAll('.tab').forEach(div => div.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    if (name === 'vocab') loadCard();
    if (name === 'grammar') loadGrammar();
    if (name === 'dashboard') loadStats();
}

function loadCard() {
    fetch('/api/card').then(r => r.json()).then(data => {
        if (!data.available) {
            document.getElementById('pinyin').innerText = 'All done!';
            document.getElementById('english').innerText = '';
            document.getElementById('hanzi').innerText = '';
            document.getElementById('reveal').disabled = true;
            document.getElementById('correct').disabled = true;
            document.getElementById('incorrect').disabled = true;
            currentCard = null;
            return;
        }
        currentCard = data.card;
        document.getElementById('pinyin').innerText = data.card.pinyin;
        document.getElementById('english').innerText = data.card.english;
        document.getElementById('hanzi').innerText = '?';
        document.getElementById('reveal').disabled = false;
        document.getElementById('correct').disabled = true;
        document.getElementById('incorrect').disabled = true;
    });
}

function reveal() {
    if (!currentCard) return;
    document.getElementById('hanzi').innerText = currentCard.hanzi;
    document.getElementById('correct').disabled = false;
    document.getElementById('incorrect').disabled = false;
    document.getElementById('reveal').disabled = true;
}

function mark(correct) {
    fetch('/api/card/' + currentCard.id, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({correct: correct})
    }).then(() => loadCard());
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
