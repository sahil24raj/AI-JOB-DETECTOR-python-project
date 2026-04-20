/* ============================================================
   main.js — Analyzer page logic
   ============================================================ */

// ── Character counter ────────────────────────────────────────
const textarea  = document.getElementById('jobText');
const charCount = document.getElementById('charCount');

textarea.addEventListener('input', () => {
  const len = textarea.value.length;
  charCount.textContent = len.toLocaleString() + ' character' + (len !== 1 ? 's' : '');
});

// ── Analyze ──────────────────────────────────────────────────
async function analyzeJob() {
  const text = textarea.value.trim();
  if (!text) {
    showToast('⚠️ Please paste a job description first.', 'warn');
    textarea.focus();
    return;
  }
  if (text.length < 20) {
    showToast('⚠️ Description is too short — paste the full text.', 'warn');
    return;
  }

  setLoading(true);

  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_text: text })
    });

    const data = await res.json();

    if (!res.ok) {
      showToast('❌ ' + (data.error || 'Server error. Please try again.'), 'error');
      setLoading(false);
      return;
    }

    displayResults(data);

  } catch (err) {
    showToast('❌ Network error. Check your connection.', 'error');
  }

  setLoading(false);
}

// ── Display Results ──────────────────────────────────────────
function displayResults({ scam_score, result, reasons }) {
  const section  = document.getElementById('resultSection');
  const scoreEl  = document.getElementById('scoreNumber');
  const badgeEl  = document.getElementById('resultBadge');
  const descEl   = document.getElementById('scoreDescription');
  const listEl   = document.getElementById('flagsList');
  const noFlags  = document.getElementById('noFlags');
  const ringFill = document.getElementById('ringFill');

  // Show section
  section.classList.remove('hidden');
  section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Animate score number
  animateNumber(scoreEl, 0, scam_score, 900);

  // SVG ring  (circumference = 2π×50 ≈ 314)
  const circumference = 314;
  const offset = circumference - (scam_score / 100) * circumference;
  ringFill.style.strokeDashoffset = offset;

  // Colour the ring
  if (scam_score >= 60) {
    ringFill.style.stroke = '#ef4444';
  } else if (scam_score >= 30) {
    ringFill.style.stroke = '#f59e0b';
  } else {
    ringFill.style.stroke = '#22c55e';
  }

  // Badge + description
  const info = resultInfo(result);
  badgeEl.textContent = result;
  badgeEl.className   = 'result-badge ' + info.badgeClass;
  descEl.textContent  = info.description;

  // Flags list
  listEl.innerHTML = '';
  if (reasons && reasons.length > 0) {
    noFlags.classList.add('hidden');
    reasons.forEach(r => {
      const li = document.createElement('li');
      li.textContent = r;
      listEl.appendChild(li);
    });
  } else {
    noFlags.classList.remove('hidden');
  }
}

function resultInfo(result) {
  switch (result) {
    case 'High Risk':
      return {
        badgeClass: 'badge-high',
        description: '🚨 Very likely a scam. Do NOT apply or pay anything.'
      };
    case 'Medium Risk':
      return {
        badgeClass: 'badge-medium',
        description: '⚠️ Several red flags found. Research the company carefully before applying.'
      };
    default:
      return {
        badgeClass: 'badge-safe',
        description: '✅ Looks legitimate. Always verify contact details independently.'
      };
  }
}

// ── Clear ─────────────────────────────────────────────────────
function clearAll() {
  textarea.value = '';
  charCount.textContent = '0 characters';
  document.getElementById('resultSection').classList.add('hidden');
  textarea.focus();
}

// ── Helpers ───────────────────────────────────────────────────
function setLoading(on) {
  const btn     = document.getElementById('analyzeBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('btnSpinner');

  btn.disabled = on;
  if (on) {
    btnText.textContent = 'Analyzing…';
    spinner.classList.remove('hidden');
  } else {
    btnText.textContent = '🔍 Analyze Now';
    spinner.classList.add('hidden');
  }
}

function animateNumber(el, from, to, duration) {
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(from + (to - from) * easeOut(progress));
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

// ── Toast notifications ───────────────────────────────────────
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.textContent = message;

  Object.assign(toast.style, {
    position:     'fixed',
    bottom:       '1.5rem',
    right:        '1.5rem',
    background:   type === 'error' ? 'rgba(239,68,68,.95)' :
                  type === 'warn'  ? 'rgba(245,158,11,.95)' :
                                     'rgba(34,197,94,.95)',
    color:        '#fff',
    padding:      '.8rem 1.4rem',
    borderRadius: '10px',
    fontSize:     '.9rem',
    fontWeight:   '600',
    boxShadow:    '0 8px 30px rgba(0,0,0,.4)',
    zIndex:       '9999',
    animation:    'fadeUp .3s ease',
    maxWidth:     '340px'
  });

  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity .4s';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Keyboard shortcut: Ctrl+Enter to analyze ─────────────────
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    analyzeJob();
  }
});
