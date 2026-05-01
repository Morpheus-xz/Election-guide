'use strict';

/* ══════════════════════════════════════════════════════════════
   STATE
══════════════════════════════════════════════════════════════ */
let history      = [];
let currentCountry = 'India';
let isWaiting    = false;
let tipInterval  = null;
let tipIdx       = 0;

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

const countryTips = {
  'India': [
    'What is the Model Code of Conduct?',
    'How do EVMs work in India?',
    'What is NOTA and when can I use it?',
    'How does the Lok Sabha election work?',
    'What is the role of the Election Commission of India?',
  ],
  'United States': [
    'How does the Electoral College work?',
    'What are Midterm elections?',
    'How do primary elections work?',
    'What happens on Election Day in the US?',
    'How long does vote counting take?',
  ],
  'United Kingdom': [
    'How does First Past the Post voting work?',
    'How are MPs elected in the UK?',
    'What is a snap general election?',
    'How is the Prime Minister chosen?',
    'What is the role of the House of Lords?',
  ],
  'Australia': [
    'Why is voting compulsory in Australia?',
    'How does preferential voting work?',
    'What does the AEC do?',
    'How does Senate voting differ from the House?',
    'What are the rules around polling day?',
  ],
  'Canada': [
    'How are Canadian federal elections called?',
    'What is Elections Canada?',
    'How does advance polling work in Canada?',
    'What is the National Register of Electors?',
    'What is a minority government in Canada?',
  ],
  'Other': [
    'How do elections generally work?',
    'What is proportional representation?',
    'What is First Past the Post voting?',
    'How are international election results verified?',
    'What bodies observe international elections?',
  ],
};

/* ══════════════════════════════════════════════════════════════
   DOM REFERENCES
══════════════════════════════════════════════════════════════ */
const chatWindow          = document.getElementById('chatWindow');
const userInput           = document.getElementById('userInput');
const sendBtn             = document.getElementById('sendBtn');
const typingWrapper       = document.getElementById('typingWrapper');
const countrySelect       = document.getElementById('countrySelect');
const countrySelectMobile = document.getElementById('countrySelectMobile');
const countryFlag         = document.getElementById('countryFlag');
const countryLabel        = document.getElementById('countryLabel');
const tipText             = document.getElementById('tipText');
const newChatBtn          = document.getElementById('newChatBtn');
const allTopicBtns        = document.querySelectorAll('.topic-btn, .mobile-topic-btn');

/* ══════════════════════════════════════════════════════════════
   MARKDOWN RENDERER
══════════════════════════════════════════════════════════════ */
function renderMarkdown(raw) {
  // Escape HTML to prevent XSS
  let s = raw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Bold: **text**
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  const lines  = s.split('\n');
  const out    = [];
  let inOl = false;
  let inUl = false;

  for (const line of lines) {
    const olMatch = line.match(/^(\d+)\.\s+(.+)/);
    const ulMatch = line.match(/^[ \t]*[-*•]\s+(.+)/);

    if (olMatch) {
      if (!inOl) {
        if (inUl) { out.push('</ul>'); inUl = false; }
        out.push('<ol>');
        inOl = true;
      }
      out.push(`<li>${olMatch[2]}</li>`);
    } else if (ulMatch) {
      if (!inUl) {
        if (inOl) { out.push('</ol>'); inOl = false; }
        out.push('<ul>');
        inUl = true;
      }
      out.push(`<li>${ulMatch[1]}</li>`);
    } else {
      if (inOl) { out.push('</ol>'); inOl = false; }
      if (inUl) { out.push('</ul>'); inUl = false; }
      if (line.trim()) {
        out.push(`<p>${line}</p>`);
      }
    }
  }

  if (inOl) out.push('</ol>');
  if (inUl) out.push('</ul>');

  return out.join('');
}

/* ══════════════════════════════════════════════════════════════
   TIMELINE RENDERER
══════════════════════════════════════════════════════════════ */
function renderTimeline(events) {
  const strip = document.createElement('div');
  strip.className = 'timeline-strip';

  events.forEach((evt) => {
    const item = document.createElement('div');
    item.className = 'timeline-event';

    const date = document.createElement('div');
    date.className = 'timeline-date';
    date.textContent = evt.date;

    const dotWrap = document.createElement('div');
    dotWrap.className = 'timeline-dot-wrap';

    const dot = document.createElement('div');
    dot.className = 'timeline-dot';
    dotWrap.appendChild(dot);

    const label = document.createElement('div');
    label.className = 'timeline-label';
    label.textContent = evt.event;

    item.appendChild(date);
    item.appendChild(dotWrap);
    item.appendChild(label);
    strip.appendChild(item);
  });

  return strip;
}

/* ══════════════════════════════════════════════════════════════
   FOLLOW-UP CHIP RENDERER
══════════════════════════════════════════════════════════════ */
function renderFollowUpChip(text) {
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
   APPEND MESSAGE BUBBLE
══════════════════════════════════════════════════════════════ */
function appendMessage(role, text, timeline = null, followUp = null) {
  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  if (role === 'model') {
    const avatar = document.createElement('div');
    avatar.className = 'civvy-avatar';
    avatar.textContent = '🏛️';
    row.appendChild(avatar);
  }

  const card = document.createElement('div');
  card.className = 'message-card';

  const content = document.createElement('div');
  content.className = 'message-content';

  if (role === 'model') {
    content.innerHTML = renderMarkdown(text);
  } else {
    // User text: plain, already escaped via textContent
    content.textContent = text;
  }
  card.appendChild(content);

  if (timeline && timeline.length > 0) {
    card.appendChild(renderTimeline(timeline));
  }

  if (followUp) {
    card.appendChild(renderFollowUpChip(followUp));
  }

  row.appendChild(card);
  chatWindow.appendChild(row);
  scrollToBottom();
}

/* ══════════════════════════════════════════════════════════════
   SCROLL
══════════════════════════════════════════════════════════════ */
function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ══════════════════════════════════════════════════════════════
   TYPING INDICATOR
══════════════════════════════════════════════════════════════ */
function showTyping() {
  typingWrapper.classList.add('visible');
  // Scroll so the indicator is visible
  chatWindow.scrollTop = chatWindow.scrollHeight + 80;
}
function hideTyping() {
  typingWrapper.classList.remove('visible');
}

/* ══════════════════════════════════════════════════════════════
   INPUT LOCK
══════════════════════════════════════════════════════════════ */
function setLocked(locked) {
  userInput.disabled  = locked;
  sendBtn.disabled    = locked;
  if (!locked) userInput.focus();
}

/* ══════════════════════════════════════════════════════════════
   TIP ROTATION
══════════════════════════════════════════════════════════════ */
function rotateTips(country) {
  if (tipInterval) clearInterval(tipInterval);
  tipIdx = 0;
  const tips = countryTips[country] || countryTips['Other'];

  const showTip = () => {
    tipText.style.opacity = '0';
    setTimeout(() => {
      tipText.textContent = `💡 Try: "${tips[tipIdx % tips.length]}"`;
      tipText.style.opacity = '1';
      tipIdx++;
    }, 420);
  };

  showTip();
  tipInterval = setInterval(showTip, 4200);
}

/* ══════════════════════════════════════════════════════════════
   INIT CHAT
══════════════════════════════════════════════════════════════ */
function initChat(country) {
  history = [];
  isWaiting = false;
  chatWindow.innerHTML = '';

  // Update top bar
  countryFlag.textContent  = countryFlags[country] || '🌍';
  countryLabel.textContent = `Elections in ${country}`;
  userInput.placeholder    = `Ask Civvy about ${country} elections...`;

  rotateTips(country);

  // Local welcome — no API call
  appendMessage(
    'model',
    `Hi! I'm Civvy 🏛️ — your ${country} election guide.\n\nI can explain ${country}'s entire election process step by step — from voter registration to result certification. What would you like to know first?`
  );
}

/* ══════════════════════════════════════════════════════════════
   SEND MESSAGE
══════════════════════════════════════════════════════════════ */
async function sendMessage(text) {
  if (isWaiting) return;

  const userMessage = (text !== undefined ? String(text) : userInput.value).trim();
  if (!userMessage) return;

  userInput.value = '';
  autoResizeTextarea();

  isWaiting = true;
  setLocked(true);

  appendMessage('user', userMessage);
  // Push to history BEFORE slicing for the request
  history.push({ role: 'user', parts: [userMessage] });

  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        history: history.slice(0, -1),   // exclude the message we just pushed
        country: currentCountry,
      }),
    });

    hideTyping();

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const data     = await res.json();
    const reply    = data.reply    || '(No response received)';
    const timeline = data.timeline || null;
    const followUp = data.follow_up || null;

    appendMessage('model', reply, timeline, followUp);
    history.push({ role: 'model', parts: [reply] });

  } catch (err) {
    hideTyping();
    appendMessage(
      'model',
      `⚠️ Something went wrong. Please try again.\n\nError: ${err.message}`
    );
  } finally {
    isWaiting = false;
    setLocked(false);
  }
}

/* ══════════════════════════════════════════════════════════════
   AUTO-RESIZE TEXTAREA
══════════════════════════════════════════════════════════════ */
function autoResizeTextarea() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

/* ══════════════════════════════════════════════════════════════
   COUNTRY CHANGE
══════════════════════════════════════════════════════════════ */
function handleCountryChange(value) {
  currentCountry = value;
  // Keep both selects in sync
  countrySelect.value       = value;
  countrySelectMobile.value = value;
  initChat(value);
}

/* ══════════════════════════════════════════════════════════════
   EVENT LISTENERS
══════════════════════════════════════════════════════════════ */
sendBtn.addEventListener('click', () => sendMessage());

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

userInput.addEventListener('input', autoResizeTextarea);

countrySelect.addEventListener('change',       (e) => handleCountryChange(e.target.value));
countrySelectMobile.addEventListener('change', (e) => handleCountryChange(e.target.value));

newChatBtn.addEventListener('click', () => initChat(currentCountry));

allTopicBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    const topic = btn.dataset.topic;
    sendMessage(`${topic} in ${currentCountry}`);
  });
});

/* ══════════════════════════════════════════════════════════════
   BOOT
══════════════════════════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded', () => {
  initChat('India');
  userInput.focus();
});
