// ── Elements ──
const overlay   = document.getElementById('overlay');
const modal     = document.getElementById('modal');
const toast     = document.getElementById('toast');
const tabs      = document.querySelectorAll('.tab');
const panels    = document.querySelectorAll('.form-panel');

// ── Modal open/close ──
document.getElementById('openModal').addEventListener('click', openModal);
document.getElementById('closeModal').addEventListener('click', closeModal);

overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

function openModal() {
  overlay.classList.add('active');
}

function closeModal() {
  overlay.classList.remove('active');
  clearAllErrors();
}

// ── Toast ──
function showToast(msg) {
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 3000);
}

// ── Tab switching ──
tabs.forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

document.getElementById('goRegister').addEventListener('click', () => switchTab('register'));
document.getElementById('goLogin').addEventListener('click',    () => switchTab('login'));

function switchTab(name) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  panels.forEach(p => p.classList.toggle('active', p.id === 'panel-' + name));
  clearAllErrors();
}

// ── Validation helpers ──
function isValidEmail(val) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
}

function setError(inputId, errId, show) {
  document.getElementById(inputId).classList.toggle('error', show);
  document.getElementById(errId).classList.toggle('show', show);
}

function clearAllErrors() {
  document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
  document.querySelectorAll('.err-msg.show').forEach(el => el.classList.remove('show'));
}

// ── Login submit ──
document.getElementById('loginBtn').addEventListener('click', () => {
  const email = document.getElementById('l-email').value.trim();
  const pass  = document.getElementById('l-pass').value;
  let valid = true;

  if (!isValidEmail(email)) { setError('l-email', 'l-email-err', true); valid = false; }
  else                       { setError('l-email', 'l-email-err', false); }

  if (!pass) { setError('l-pass', 'l-pass-err', true); valid = false; }
  else       { setError('l-pass', 'l-pass-err', false); }

  if (valid) {
    closeModal();
    showToast('Signed in successfully!');
  }
});

// ── Register submit ──
document.getElementById('registerBtn').addEventListener('click', () => {
  const name    = document.getElementById('r-name').value.trim();
  const email   = document.getElementById('r-email').value.trim();
  const pass    = document.getElementById('r-pass').value;
  const confirm = document.getElementById('r-confirm').value;
  let valid = true;

  if (!name)              { setError('r-name',    'r-name-err',    true); valid = false; }
  else                    { setError('r-name',    'r-name-err',    false); }

  if (!isValidEmail(email)) { setError('r-email', 'r-email-err',  true); valid = false; }
  else                      { setError('r-email', 'r-email-err',  false); }

  if (pass.length < 8)   { setError('r-pass',    'r-pass-err',    true); valid = false; }
  else                   { setError('r-pass',    'r-pass-err',    false); }

  if (confirm !== pass)  { setError('r-confirm', 'r-confirm-err', true); valid = false; }
  else                   { setError('r-confirm', 'r-confirm-err', false); }

  if (valid) {
    closeModal();
    showToast('Account created! Welcome aboard.');
  }
});