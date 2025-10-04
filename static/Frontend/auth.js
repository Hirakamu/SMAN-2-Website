// auth.js — cookie-based auth, API = localhost:5000
const API = "http://localhost:5000";
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* helpers */
async function safeJson(res) {
  const text = await res.text().catch(() => null);
  try { return text ? JSON.parse(text) : null; } catch { return text; }
}

/* network calls (send cookies) */
async function loginUser(username, password) {
  return fetch(`${API}/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
}
async function registerUser(username, password) {
  return fetch(`${API}/register`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
}
async function logoutUser() {
  return fetch(`${API}/logout`, { method: 'POST', credentials: 'include' });
}
async function fetchMe() {
  try {
    const res = await fetch(`${API}/me`, { credentials: 'include' });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

/* UI helpers */
function localUIAfterAuth(user) {
  const navLogin = document.getElementById('nav-login');
  const navRegister = document.getElementById('nav-register');
  const navLogout = document.getElementById('nav-logout');
  const navUser = document.getElementById('nav-user');

  if (navLogin) navLogin.style.display = 'none';
  if (navRegister) navRegister.style.display = 'none';
  if (navLogout) navLogout.style.display = 'inline-block';
  if (navUser) {
    navUser.style.display = 'inline-block';
    navUser.textContent = user && user.username ? user.username : 'Me';
  }
}

/* wire login form */
const loginSubmit = document.getElementById('login-submit');
if (loginSubmit) {
  loginSubmit.addEventListener('click', async () => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const msg = document.getElementById('msg');
    if (msg) { msg.style.color = ''; msg.textContent = 'Processing...'; }
    try {
      const res = await loginUser(username, password);
      const body = await safeJson(res);
      if (res.ok && body && body.status === 'ok') {
        if (msg) { msg.style.color = '#6f6'; msg.textContent = 'Login ok'; }
        localUIAfterAuth({ username });
        setTimeout(() => location.href = 'index.html', 300);
      } else {
        if (msg) { msg.style.color = '#f88'; msg.textContent = body && body.status ? `Login failed (${res.status})` : `Login failed (${res.status})`; }
      }
    } catch (e) {
      console.error(e);
      if (document.getElementById('msg')) document.getElementById('msg').textContent = 'Network error';
    }
  });
}

/* wire register form */
const registerSubmit = document.getElementById('register-submit');
if (registerSubmit) {
  registerSubmit.addEventListener('click', async () => {
    const username = document.getElementById('r-username').value.trim();
    const password = document.getElementById('r-password').value;
    const rMsg = document.getElementById('r-msg');
    if (rMsg) { rMsg.style.color = ''; rMsg.textContent = 'Processing...'; }
    try {
      const res = await registerUser(username, password);
      const body = await safeJson(res);
      if (res.status === 201) {
        if (rMsg) { rMsg.style.color = '#6f6'; rMsg.textContent = 'Account created'; }
        localUIAfterAuth({ username });
        setTimeout(() => location.href = 'index.html', 300);
      } else {
        if (rMsg) {
          const reason = body && body.reason ? ` - ${body.reason}` : '';
          rMsg.style.color = '#f88';
          rMsg.textContent = `Register failed (${res.status})${reason}`;
        }
      }
    } catch (e) {
      console.error(e);
      if (rMsg) rMsg.textContent = 'Network error';
    }
  });
}

/* nav wiring */
const navLogout = document.getElementById('nav-logout');
if (navLogout) {
  navLogout.addEventListener('click', async () => {
    await logoutUser();
    // reset UI
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navUser = document.getElementById('nav-user');
    if (navLogin) navLogin.style.display = 'inline-block';
    if (navRegister) navRegister.style.display = 'inline-block';
    if (navLogout) navLogout.style.display = 'none';
    if (navUser) { navUser.style.display = 'none'; navUser.textContent = ''; }
    location.href = 'index.html';
  });
}

/* initial session check */
(async function initAuthNav() {
  const me = await fetchMe();
  if (me) localUIAfterAuth(me);
  else {
    const navLogout = document.getElementById('nav-logout');
    const navUser = document.getElementById('nav-user');
    if (navLogout) navLogout.style.display = 'none';
    if (navUser) navUser.style.display = 'none';
  }
})();
