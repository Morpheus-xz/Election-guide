'use strict';

/* ══════════════════════════════════════════════════════════════
   STATE
══════════════════════════════════════════════════════════════ */
let history        = [];
let currentCountry = 'India';
let currentLang    = 'English';
let isWaiting      = false;
let tipInterval    = null;
let tipIdx         = 0;

/* ══════════════════════════════════════════════════════════════
   CONSTANTS
══════════════════════════════════════════════════════════════ */
const countryFlags = {
  'India':          '🇮🇳',
  'United States':  '🇺🇸',
  'United Kingdom': '🇬🇧',
  'Australia':      '🇦🇺',
  'Canada':         '🇨🇦',
  'Other':          '🌍',
};

const countryStats = {
  'India':          [{ label: 'Lok Sabha Seats', value: '543' }, { label: 'Registered Voters', value: '96.8 Cr' }, { label: 'EVMs Since', value: '1999' }],
  'United States':  [{ label: 'Electoral Votes', value: '538' }, { label: 'To Win', value: '270' }, { label: 'Election Cycle', value: '4 yrs' }],
  'United Kingdom': [{ label: 'Commons Seats', value: '650' }, { label: 'Registered Voters', value: '47 M+' }, { label: 'Voting Age', value: '18 yrs' }],
  'Australia':      [{ label: 'House Seats', value: '151' }, { label: 'Senate Seats', value: '76' }, { label: 'Voting', value: 'Mandatory' }],
  'Canada':         [{ label: 'Commons Seats', value: '338' }, { label: 'Registered Voters', value: '27 M+' }, { label: 'Election Cycle', value: '4 yrs' }],
  'Other':          [{ label: 'Coverage', value: 'Global' }, { label: 'Focus', value: 'Principles' }, { label: 'Approach', value: 'Universal' }],
};

const countryTips = {
  'India':          ['What is the Model Code of Conduct?', 'How do EVMs work in India?', 'What is NOTA?', 'How does the Lok Sabha election work?', 'What does the Election Commission do?'],
  'United States':  ['How does the Electoral College work?', 'What are Midterm elections?', 'How do primaries work?', 'What happens on Election Day?', 'How long does vote counting take?'],
  'United Kingdom': ['How does First Past the Post work?', 'How are MPs elected?', 'What is a snap election?', 'How is the Prime Minister chosen?', 'What is the House of Lords?'],
  'Australia':      ['Why is voting compulsory in Australia?', 'How does preferential voting work?', 'What is the AEC?', 'How does Senate voting work?', 'What are polling day rules?'],
  'Canada':         ['How are Canadian elections called?', 'What is Elections Canada?', 'How does advance polling work?', 'What is the National Register of Electors?', 'What is a minority government?'],
  'Other':          ['How do elections generally work?', 'What is proportional representation?', 'What is First Past the Post?', 'How are results verified internationally?', 'What bodies observe elections?'],
};

const CIVVY_SVG = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18" aria-hidden="true">
  <rect x="2" y="9" width="20" height="12" rx="2" fill="#0D1B2A" stroke="#C9A84C" stroke-width="1.5"/>
  <path d="M2 14h20" stroke="#C9A84C" stroke-width="1.5"/>
  <path d="M8 9V7a4 4 0 0 1 8 0v2" stroke="#C9A84C" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M9 18l2.5 2.5 4-5" stroke="#C9A84C" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;

/* ══════════════════════════════════════════════════════════════
   DOM REFERENCES
══════════════════════════════════════════════════════════════ */
const chatWindow          = document.getElementById('chatWindow');
const userInput           = document.getElementById('userInput');
const sendBtn             = document.getElementById('sendBtn');
const typingWrapper       = document.getElementById('typingWrapper');
const countrySelect       = document.getElementById('countrySelect');
const langSelect          = document.getElementById('langSelect');
const countrySelectMobile = document.getElementById('countrySelectMobile');
const countryFlag         = document.getElementById('countryFlag');
const countryLabel        = document.getElementById('countryLabel');
const countrySub          = document.getElementById('countrySub');
const tipText             = document.getElementById('tipText');
const newChatBtn          = document.getElementById('newChatBtn');
const statsGrid           = document.getElementById('statsGrid');
const factText            = document.getElementById('factText');
const refreshFactBtn      = document.getElementById('refreshFactBtn');
const progressBar         = document.getElementById('progressBar');
const compareModal        = document.getElementById('compareModal');
const compareClose        = document.getElementById('compareClose');
const compareSubmit       = document.getElementById('compareSubmit');
const voiceBtn            = document.getElementById('voiceBtn');
const darkModeBtn         = document.getElementById('darkModeBtn');
const darkModeBtnMobile   = document.getElementById('darkModeBtnMobile');
const quizBtn             = document.getElementById('quizBtn');
const compareBtn          = document.getElementById('compareBtn');
const glossaryBtn         = document.getElementById('glossaryBtn');
const mobileQuizBtn       = document.getElementById('mobileQuizBtn');
const mobileGlossaryBtn   = document.getElementById('mobileGlossaryBtn');
const allTopicBtns        = document.querySelectorAll('.topic-btn, .mobile-topic-btn');

/* ══════════════════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════════════════ */
function showProgress() {
  progressBar.style.width = '0%';
  progressBar.classList.add('loading');
}
function hideProgress() {
  progressBar.style.transition = 'width 0.2s ease';
  progressBar.style.width = '100%';
  setTimeout(() => {
    progressBar.classList.remove('loading');
    progressBar.style.width = '0%';
    progressBar.style.transition = '';
  }, 280);
}

/* ══════════════════════════════════════════════════════════════
   DARK MODE
══════════════════════════════════════════════════════════════ */
function setDarkMode(dark) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  const icon = dark ? '☀️' : '🌙';
  darkModeBtn.textContent        = icon;
  darkModeBtnMobile.textContent  = icon;
  localStorage.setItem('civvy-theme', dark ? 'dark' : 'light');
}
function toggleDarkMode() {
  setDarkMode(document.documentElement.getAttribute('data-theme') !== 'dark');
}
darkModeBtn.addEventListener('click',       toggleDarkMode);
darkModeBtnMobile.addEventListener('click', toggleDarkMode);

/* ══════════════════════════════════════════════════════════════
   MARKDOWN RENDERER
══════════════════════════════════════════════════════════════ */
function renderMarkdown(raw) {
  let s = raw
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  const lines = s.split('\n');
  const out = [];
  let inOl = false, inUl = false;

  for (const line of lines) {
    const ol = line.match(/^(\d+)\.\s+(.+)/);
    const ul = line.match(/^[ \t]*[-*•]\s+(.+)/);

    if (ol) {
      if (!inOl) { if (inUl) { out.push('</ul>'); inUl = false; } out.push('<ol>'); inOl = true; }
      out.push(`<li>${ol[2]}</li>`);
    } else if (ul) {
      if (!inUl) { if (inOl) { out.push('</ol>'); inOl = false; } out.push('<ul>'); inUl = true; }
      out.push(`<li>${ul[1]}</li>`);
    } else {
      if (inOl) { out.push('</ol>'); inOl = false; }
      if (inUl) { out.push('</ul>'); inUl = false; }
      if (line.trim()) out.push(`<p>${line}</p>`);
    }
  }
  if (inOl) out.push('</ol>');
  if (inUl) out.push('</ul>');
  return out.join('');
}

/* ══════════════════════════════════════════════════════════════
   TIMESTAMP
══════════════════════════════════════════════════════════════ */
function nowLabel() {
  return 'Today, ' + new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

/* ══════════════════════════════════════════════════════════════
   TIMELINE RENDERER
══════════════════════════════════════════════════════════════ */
function renderTimeline(events) {
  const strip = document.createElement('div');
  strip.className = 'timeline-strip';
  events.forEach(evt => {
    const item  = document.createElement('div');
    item.className = 'timeline-event';
    const date  = document.createElement('div');
    date.className = 'timeline-date';
    date.textContent = evt.date;
    const wrap  = document.createElement('div');
    wrap.className = 'timeline-dot-wrap';
    const dot   = document.createElement('div');
    dot.className = 'timeline-dot';
    wrap.appendChild(dot);
    const label = document.createElement('div');
    label.className = 'timeline-label';
    label.textContent = evt.event;
    item.append(date, wrap, label);
    strip.appendChild(item);
  });
  return strip;
}

/* ══════════════════════════════════════════════════════════════
   FOLLOW-UP CHIP
══════════════════════════════════════════════════════════════ */
function renderFollowUp(text) {
  const wrap = document.createElement('div');
  wrap.className = 'followup-wrap';
  const btn = document.createElement('button');
  btn.className = 'followup-chip';
  btn.textContent = `💬 ${text}`;
  btn.addEventListener('click', () => sendMessage(text));
  wrap.appendChild(btn);
  return wrap;
}

/* ══════════════════════════════════════════════════════════════
   SHARE CARD (Canvas → PNG download)
══════════════════════════════════════════════════════════════ */
function createShareCard(rawText) {
  const W = 620, H = 340;
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#0D1B2A';
  ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = '#C9A84C';
  ctx.lineWidth = 4;
  ctx.strokeRect(6, 6, W - 12, H - 12);

  ctx.fillStyle = '#C9A84C';
  ctx.font = 'bold 18px Georgia, serif';
  ctx.fillText('🗳️  Civvy — Your Election Guide', 28, 46);

  ctx.strokeStyle = 'rgba(201,168,76,0.35)';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(28, 60); ctx.lineTo(W - 28, 60); ctx.stroke();

  ctx.fillStyle = '#FFFFFF';
  ctx.font = '14px sans-serif';
  const clean = rawText.replace(/\*\*/g, '').replace(/\n/g, ' ');
  const words = clean.split(' ');
  let line = '', y = 86, lines = 0;
  for (const word of words) {
    const test = line + word + ' ';
    if (ctx.measureText(test).width > W - 56 && line) {
      ctx.fillText(line.trim(), 28, y);
      line = word + ' '; y += 22; lines++;
      if (lines >= 8) { ctx.fillText('…', 28, y); break; }
    } else { line = test; }
  }
  if (lines < 8) ctx.fillText(line.trim(), 28, y);

  ctx.fillStyle = 'rgba(201,168,76,0.55)';
  ctx.font = '11px sans-serif';
  ctx.fillText('election-agent-665340845923.us-central1.run.app  •  Nonpartisan & Educational', 28, H - 20);

  return canvas;
}

/* ══════════════════════════════════════════════════════════════
   APPEND MESSAGE
══════════════════════════════════════════════════════════════ */
function appendMessage(role, text, timeline = null, followUp = null) {
  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  if (role === 'model') {
    const av = document.createElement('div');
    av.className = 'civvy-avatar';
    av.innerHTML = CIVVY_SVG;
    row.appendChild(av);
  }

  const card = document.createElement('div');
  card.className = 'message-card';

  const content = document.createElement('div');
  content.className = 'message-content';
  if (role === 'model') content.innerHTML = renderMarkdown(text);
  else                  content.textContent = text;
  card.appendChild(content);

  if (role === 'model') {
    // Share button
    const shareBtn = document.createElement('button');
    shareBtn.className = 'share-btn';
    shareBtn.title = 'Download as image';
    shareBtn.textContent = '📤';
    shareBtn.addEventListener('click', () => {
      const canvas = createShareCard(text);
      canvas.toBlob(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `civvy-${currentCountry.toLowerCase().replace(/\s/g, '-')}.png`;
        a.click();
        URL.revokeObjectURL(a.href);
      });
    });
    card.appendChild(shareBtn);
  }

  if (timeline && timeline.length) card.appendChild(renderTimeline(timeline));
  if (followUp)                    card.appendChild(renderFollowUp(followUp));

  const ts = document.createElement('div');
  ts.className = 'msg-timestamp';
  ts.textContent = nowLabel();
  card.appendChild(ts);

  row.appendChild(card);
  chatWindow.appendChild(row);
  scrollBottom();
}

/* ══════════════════════════════════════════════════════════════
   QUIZ
══════════════════════════════════════════════════════════════ */
function renderQuizCard(questions) {
  const container = document.createElement('div');
  container.className = 'quiz-container';

  const hdr = document.createElement('div');
  hdr.className = 'quiz-header';
  hdr.innerHTML = `<h3>📝 Election Quiz — ${currentCountry}</h3><p>${questions.length} multiple-choice questions</p>`;
  container.appendChild(hdr);

  const answers = new Array(questions.length).fill(null);

  questions.forEach((q, qi) => {
    const card = document.createElement('div');
    card.className = 'quiz-question';

    const qText = document.createElement('div');
    qText.className = 'quiz-q-text';
    qText.textContent = `${qi + 1}. ${q.question}`;
    card.appendChild(qText);

    const opts = document.createElement('div');
    opts.className = 'quiz-options';

    q.options.forEach((opt, oi) => {
      const letter = ['A', 'B', 'C', 'D'][oi];
      const btn = document.createElement('button');
      btn.className = 'quiz-option-btn';
      btn.textContent = opt;
      btn.dataset.letter = letter;
      btn.addEventListener('click', () => {
        opts.querySelectorAll('.quiz-option-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        answers[qi] = letter;
      });
      opts.appendChild(btn);
    });

    card.appendChild(opts);
    container.appendChild(card);
  });

  const submitBtn = document.createElement('button');
  submitBtn.className = 'quiz-submit-btn';
  submitBtn.textContent = '📊 Submit Answers';
  submitBtn.addEventListener('click', () => {
    if (answers.includes(null)) { alert('Please answer all questions first!'); return; }
    scoreQuiz(questions, answers, container, submitBtn);
  });
  container.appendChild(submitBtn);
  return container;
}

function scoreQuiz(questions, answers, container, submitBtn) {
  let score = 0;
  questions.forEach((q, i) => {
    if (answers[i] === q.correct) score++;
    const qDiv = container.querySelectorAll('.quiz-question')[i];
    qDiv.querySelectorAll('.quiz-option-btn').forEach(btn => {
      btn.disabled = true;
      if (btn.dataset.letter === q.correct) btn.classList.add('correct');
      else if (btn.dataset.letter === answers[i]) btn.classList.add('incorrect');
    });
    const exp = document.createElement('div');
    exp.className = 'quiz-explanation';
    exp.textContent = `💡 ${q.explanation}`;
    qDiv.appendChild(exp);
  });

  const pct = Math.round((score / questions.length) * 100);
  const emoji = pct >= 80 ? '🎉' : pct >= 60 ? '👍' : '📚';
  const msg   = pct >= 80 ? 'Excellent!' : pct >= 60 ? 'Good job!' : 'Keep learning!';

  const scoreDiv = document.createElement('div');
  scoreDiv.className = 'quiz-score';
  scoreDiv.innerHTML = `
    <div class="quiz-score-number">${score}/${questions.length}</div>
    <div class="quiz-score-msg">${emoji} ${msg} You scored ${pct}% on ${currentCountry} elections!</div>`;
  submitBtn.replaceWith(scoreDiv);
}

async function startQuiz() {
  if (isWaiting) return;
  appendMessage('model', `🎯 Generating your **${currentCountry}** election quiz… this takes a moment!`);
  showProgress(); isWaiting = true; setLocked(true);
  try {
    const res = await fetch('/quiz', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ country: currentCountry, topic: 'General Election Process' }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Inject quiz into a custom Civvy-style message
    const row = document.createElement('div');
    row.className = 'message-row model';
    const av = document.createElement('div');
    av.className = 'civvy-avatar'; av.innerHTML = CIVVY_SVG;
    row.appendChild(av);
    const card = document.createElement('div');
    card.className = 'message-card';
    card.appendChild(renderQuizCard(data.questions));
    const ts = document.createElement('div');
    ts.className = 'msg-timestamp'; ts.textContent = nowLabel();
    card.appendChild(ts);
    row.appendChild(card);
    chatWindow.appendChild(row);
    scrollBottom();
  } catch (err) {
    appendMessage('model', `⚠️ Could not load quiz: ${err.message}`);
  } finally {
    hideProgress(); isWaiting = false; setLocked(false);
  }
}

/* ══════════════════════════════════════════════════════════════
   COMPARISON
══════════════════════════════════════════════════════════════ */
function renderComparisonTable(data, c1, c2) {
  const container = document.createElement('div');
  container.className = 'comparison-container';

  const hdr = document.createElement('div');
  hdr.className = 'comparison-header';
  hdr.innerHTML = `<h3>⚖️ Election Systems Compared</h3>
    <div class="comparison-countries">
      <span>${countryFlags[c1] || '🌍'} ${c1}</span>
      <span class="vs-badge">VS</span>
      <span>${countryFlags[c2] || '🌍'} ${c2}</span>
    </div>`;
  container.appendChild(hdr);

  const table = document.createElement('table');
  table.className = 'comparison-table';
  table.innerHTML = `<thead><tr>
    <th>Aspect</th>
    <th>${countryFlags[c1] || ''} ${c1}</th>
    <th>${countryFlags[c2] || ''} ${c2}</th>
  </tr></thead>`;
  const tbody = document.createElement('tbody');
  data.aspects.forEach(a => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="aspect-name">${a.aspect}</td>
      <td class="${a.winner === 'country1' ? 'highlight' : ''}">${a.country1}</td>
      <td class="${a.winner === 'country2' ? 'highlight' : ''}">${a.country2}</td>`;
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.appendChild(table);

  if (data.summary) {
    const s = document.createElement('div');
    s.className = 'comparison-summary';
    s.textContent = data.summary;
    container.appendChild(s);
  }
  return container;
}

async function submitComparison() {
  const c1 = document.getElementById('cmp1').value;
  const c2 = document.getElementById('cmp2').value;
  if (c1 === c2) { alert('Please select two different countries.'); return; }

  closeCompareModal();
  showProgress(); isWaiting = true; setLocked(true);
  appendMessage('model', `⚖️ Comparing **${c1}** vs **${c2}** election systems… one moment!`);

  try {
    const res = await fetch('/compare', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ country1: c1, country2: c2 }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const row = document.createElement('div');
    row.className = 'message-row model';
    const av = document.createElement('div');
    av.className = 'civvy-avatar'; av.innerHTML = CIVVY_SVG;
    row.appendChild(av);
    const card = document.createElement('div');
    card.className = 'message-card';
    card.appendChild(renderComparisonTable(data, c1, c2));
    const ts = document.createElement('div');
    ts.className = 'msg-timestamp'; ts.textContent = nowLabel();
    card.appendChild(ts);
    row.appendChild(card);
    chatWindow.appendChild(row);
    scrollBottom();
  } catch (err) {
    appendMessage('model', `⚠️ Comparison failed: ${err.message}`);
  } finally {
    hideProgress(); isWaiting = false; setLocked(false);
  }
}

function openCompareModal()  { compareModal.classList.add('open'); }
function closeCompareModal() { compareModal.classList.remove('open'); }

/* ══════════════════════════════════════════════════════════════
   GLOSSARY
══════════════════════════════════════════════════════════════ */
function renderGlossary(terms) {
  const container = document.createElement('div');
  container.className = 'glossary-container';
  const hdr = document.createElement('div');
  hdr.className = 'glossary-header';
  hdr.innerHTML = `<h3>📖 Election Glossary — ${currentCountry}</h3>`;
  container.appendChild(hdr);

  const acc = document.createElement('div');
  acc.className = 'glossary-accordion';
  terms.forEach(t => {
    const item = document.createElement('div');
    item.className = 'glossary-item';
    const btn = document.createElement('button');
    btn.className = 'glossary-term-btn';
    btn.textContent = t.term;
    const content = document.createElement('div');
    content.className = 'glossary-content';
    content.innerHTML = `<p class="glossary-def">${t.definition}</p>${t.example ? `<p class="glossary-example">📌 Example: ${t.example}</p>` : ''}`;
    btn.addEventListener('click', () => {
      const open = item.classList.contains('open');
      acc.querySelectorAll('.glossary-item').forEach(i => i.classList.remove('open'));
      if (!open) item.classList.add('open');
    });
    item.append(btn, content);
    acc.appendChild(item);
  });
  container.appendChild(acc);
  return container;
}

async function fetchGlossary() {
  if (isWaiting) return;
  showProgress(); isWaiting = true; setLocked(true);
  appendMessage('model', `📖 Loading the **${currentCountry}** election glossary…`);
  try {
    const res = await fetch(`/glossary?country=${encodeURIComponent(currentCountry)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const terms = await res.json();

    const row = document.createElement('div');
    row.className = 'message-row model';
    const av = document.createElement('div');
    av.className = 'civvy-avatar'; av.innerHTML = CIVVY_SVG;
    row.appendChild(av);
    const card = document.createElement('div');
    card.className = 'message-card';
    card.appendChild(renderGlossary(terms));
    const ts = document.createElement('div');
    ts.className = 'msg-timestamp'; ts.textContent = nowLabel();
    card.appendChild(ts);
    row.appendChild(card);
    chatWindow.appendChild(row);
    scrollBottom();
  } catch (err) {
    appendMessage('model', `⚠️ Glossary failed: ${err.message}`);
  } finally {
    hideProgress(); isWaiting = false; setLocked(false);
  }
}

/* ══════════════════════════════════════════════════════════════
   DID YOU KNOW
══════════════════════════════════════════════════════════════ */
async function loadFact(country) {
  factText.textContent = '⏳ Loading a fascinating fact…';
  try {
    const res = await fetch(`/fact?country=${encodeURIComponent(country)}`);
    const data = await res.json();
    factText.textContent = data.fact || 'Could not load a fact right now.';
  } catch {
    factText.textContent = 'Could not load a fact. Try refreshing!';
  }
}

/* ══════════════════════════════════════════════════════════════
   ELECTION AT A GLANCE
══════════════════════════════════════════════════════════════ */
function updateStats(country) {
  const stats = countryStats[country] || countryStats['Other'];
  statsGrid.innerHTML = '';
  stats.forEach(s => {
    const item = document.createElement('div');
    item.className = 'stat-item';
    item.innerHTML = `<div class="stat-value">${s.value}</div><div class="stat-label">${s.label}</div>`;
    statsGrid.appendChild(item);
  });
}

/* ══════════════════════════════════════════════════════════════
   VOICE INPUT
══════════════════════════════════════════════════════════════ */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = e => {
    userInput.value = e.results[0][0].transcript;
    autoResize();
    stopVoice();
    sendMessage();
  };
  recognition.onerror = stopVoice;
  recognition.onend   = stopVoice;
} else {
  voiceBtn.classList.add('hidden');
}

function startVoice() {
  if (!recognition) return;
  recognition.lang = currentLang === 'Hindi' ? 'hi-IN' : currentLang === 'Tamil' ? 'ta-IN' :
    currentLang === 'Telugu' ? 'te-IN' : currentLang === 'Bengali' ? 'bn-IN' :
    currentLang === 'Spanish' ? 'es-ES' : currentLang === 'French' ? 'fr-FR' : 'en-US';
  recognition.start();
  voiceBtn.classList.add('recording');
  voiceBtn.title = '🎤 Listening… (click to stop)';
}
function stopVoice() {
  if (!recognition) return;
  try { recognition.stop(); } catch {}
  voiceBtn.classList.remove('recording');
  voiceBtn.title = 'Voice input';
}
voiceBtn.addEventListener('click', () => {
  voiceBtn.classList.contains('recording') ? stopVoice() : startVoice();
});

/* ══════════════════════════════════════════════════════════════
   SCROLL / LOCK / TIPS
══════════════════════════════════════════════════════════════ */
function scrollBottom() { chatWindow.scrollTop = chatWindow.scrollHeight; }

function setLocked(on) {
  userInput.disabled = on;
  sendBtn.disabled   = on;
  if (!on) userInput.focus();
}

function rotateTips(country) {
  if (tipInterval) clearInterval(tipInterval);
  tipIdx = 0;
  const tips = countryTips[country] || countryTips['Other'];
  const show = () => {
    tipText.style.opacity = '0';
    setTimeout(() => {
      tipText.textContent = `💡 Try: "${tips[tipIdx++ % tips.length]}"`;
      tipText.style.opacity = '1';
    }, 420);
  };
  show();
  tipInterval = setInterval(show, 4200);
}

/* ══════════════════════════════════════════════════════════════
   TYPING INDICATOR
══════════════════════════════════════════════════════════════ */
function showTyping() { typingWrapper.classList.add('visible'); scrollBottom(); }
function hideTyping() { typingWrapper.classList.remove('visible'); }

/* ══════════════════════════════════════════════════════════════
   INIT CHAT
══════════════════════════════════════════════════════════════ */
function initChat(country) {
  history = []; isWaiting = false;
  chatWindow.innerHTML = '';

  countryFlag.textContent    = countryFlags[country] || '🌍';
  countryLabel.textContent   = `Elections in ${country}`;
  countrySub.textContent     = `Ask me anything about ${country}'s election process`;
  userInput.placeholder      = `Ask Civvy about ${country} elections…`;

  updateStats(country);
  rotateTips(country);
  loadFact(country);

  appendMessage(
    'model',
    `Hi! I'm Civvy 🏛️ — your **${country}** election guide.\n\nI can explain ${country}'s entire election process step by step. Use the sidebar tools to take a quiz, compare countries, or browse the glossary. What would you like to know first?`
  );
}

/* ══════════════════════════════════════════════════════════════
   SEND MESSAGE
══════════════════════════════════════════════════════════════ */
async function sendMessage(text) {
  if (isWaiting) return;
  const msg = (text !== undefined ? String(text) : userInput.value).trim();
  if (!msg) return;

  userInput.value = '';
  autoResize();
  isWaiting = true;
  setLocked(true);

  appendMessage('user', msg);
  history.push({ role: 'user', parts: [msg] });

  showTyping();
  showProgress();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg,
        history: history.slice(0, -1),
        country: currentCountry,
        language: currentLang,
      }),
    });

    hideTyping();
    hideProgress();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data     = await res.json();
    const reply    = data.reply    || '(No response received)';
    const timeline = data.timeline || null;
    const followUp = data.follow_up || null;

    appendMessage('model', reply, timeline, followUp);
    history.push({ role: 'model', parts: [reply] });
  } catch (err) {
    hideTyping();
    hideProgress();
    appendMessage('model', `⚠️ Something went wrong. Please try again.\n\nError: ${err.message}`);
  } finally {
    isWaiting = false;
    setLocked(false);
  }
}

/* ══════════════════════════════════════════════════════════════
   AUTO-RESIZE TEXTAREA
══════════════════════════════════════════════════════════════ */
function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

/* ══════════════════════════════════════════════════════════════
   COUNTRY / LANGUAGE CHANGE
══════════════════════════════════════════════════════════════ */
function handleCountryChange(value) {
  currentCountry = value;
  countrySelect.value       = value;
  countrySelectMobile.value = value;
  sessionStorage.setItem('civvy-country', value);
  initChat(value);
}

function handleLangChange(value) {
  currentLang = value;
  langSelect.value = value;
  sessionStorage.setItem('civvy-lang', value);
}

/* ══════════════════════════════════════════════════════════════
   EVENT LISTENERS
══════════════════════════════════════════════════════════════ */
sendBtn.addEventListener('click', () => sendMessage());
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
userInput.addEventListener('input', autoResize);

countrySelect.addEventListener('change',       e => handleCountryChange(e.target.value));
countrySelectMobile.addEventListener('change', e => handleCountryChange(e.target.value));
langSelect.addEventListener('change',          e => handleLangChange(e.target.value));

newChatBtn.addEventListener('click', () => initChat(currentCountry));

allTopicBtns.forEach(btn => {
  if (btn.dataset.topic) {
    btn.addEventListener('click', () => sendMessage(`${btn.dataset.topic} in ${currentCountry}`));
  }
});

quizBtn.addEventListener('click',       startQuiz);
mobileQuizBtn.addEventListener('click', startQuiz);
glossaryBtn.addEventListener('click',       fetchGlossary);
mobileGlossaryBtn.addEventListener('click', fetchGlossary);

compareBtn.addEventListener('click',    openCompareModal);
compareClose.addEventListener('click',  closeCompareModal);
compareSubmit.addEventListener('click', submitComparison);
compareModal.addEventListener('click',  e => { if (e.target === compareModal) closeCompareModal(); });

refreshFactBtn.addEventListener('click', () => loadFact(currentCountry));

/* ══════════════════════════════════════════════════════════════
   BOOT
══════════════════════════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded', () => {
  // Restore preferences
  const savedTheme   = localStorage.getItem('civvy-theme');
  const savedCountry = sessionStorage.getItem('civvy-country') || 'India';
  const savedLang    = sessionStorage.getItem('civvy-lang')    || 'English';

  if (savedTheme === 'dark') setDarkMode(true);

  currentLang = savedLang;
  langSelect.value = savedLang;

  handleCountryChange(savedCountry);
  userInput.focus();
});
