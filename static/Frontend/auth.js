// auth.js — shared login / register logic
const API = "http://localhost:5000"; // replace with your server (include scheme and port)
const yearEl = document.getElementById('year');
if(yearEl) yearEl.textContent = new Date().getFullYear();

/* Login page refs */
const loginForm = document.getElementById('login-form');
const username = document.getElementById('username');
const password = document.getElementById('password');
const loginSubmit = document.getElementById('login-submit');
const msg = document.getElementById('msg');

/* Register page refs */
const registerForm = document.getElementById('register-form');
const rUsername = document.getElementById('r-username');
const rPassword = document.getElementById('r-password');
const registerSubmit = document.getElementById('register-submit');
const rMsg = document.getElementById('r-msg');

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  const text = await res.text();
  // try parse JSON safely
  try { return {ok: res.ok, status: res.status, body: JSON.parse(text)}; }
  catch { return {ok: res.ok, status: res.status, body: text}; }
}

/* Attach handlers only if elements exist on page */
if(loginSubmit && username && password) {
  loginSubmit.addEventListener('click', async () => {
    msg.textContent = "Processing...";
    try {
      const {ok, status, body} = await postJson(`${API}/login`, {username: username.value, password: password.value});
      if(ok && body && body.status === "ok") {
        // store username as a simple session marker
        localStorage.setItem('user', username.value);
        msg.style.color = '#6f6';
        msg.textContent = "Login successful. Redirecting…";
        setTimeout(()=> location.href = 'index.html', 600);
      } else {
        msg.style.color = '#f88';
        msg.textContent = (body && body.status) ? `Login failed (${status})` : `Login failed (${status})`;
      }
    } catch (err) {
      console.error(err);
      msg.style.color = '#f88';
      msg.textContent = 'Network error';
    }
  });
}

if(registerSubmit && rUsername && rPassword) {
  registerSubmit.addEventListener('click', async () => {
    rMsg.textContent = "Processing...";
    try {
      const {ok, status, body} = await postJson(`${API}/register`, {username: rUsername.value, password: rPassword.value});
      if(ok && status === 201) {
        rMsg.style.color = '#6f6';
        rMsg.textContent = 'Account created. Redirecting to login…';
        setTimeout(()=> location.href = 'login.html', 600);
      } else {
        rMsg.style.color = '#f88';
        const reason = body && body.reason ? ` - ${body.reason}` : '';
        rMsg.textContent = `Register failed (${status})${reason}`;
      }
    } catch (err) {
      console.error(err);
      rMsg.style.color = '#f88';
      rMsg.textContent = 'Network error';
    }
  });
}
