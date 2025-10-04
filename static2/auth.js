// check session on load
async function checkAuth() {
  try {
    let res = await fetch("http://localhost:1234/me", { credentials: "include" });
    if (res.ok) {
      let user = await res.json();
      let authLinks = document.getElementById("auth-links");
      if (authLinks) {
        authLinks.innerHTML = `<span>Hello, ${user.username}</span> 
                               <a href="profile.html">Profil</a>`;
      }
    }
  } catch (e) { console.log("Not logged in"); }
}

// handle login
let loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.onsubmit = async (e) => {
    e.preventDefault();
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let res = await fetch("http://localhost:1234/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (res.ok) {
      alert("Logged in!");
      window.location.href = "index.html";
    } else {
      alert("Login failed");
    }
  };
}

// handle register
let registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.onsubmit = async (e) => {
    e.preventDefault();
    let username = document.getElementById("username").value;
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    let res = await fetch("http://localhost:1234/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });
    if (res.ok) {
      alert("Registered! Please login");
      window.location.href = "login.html";
    } else {
      alert("Register failed");
    }
  };
}

// handle profile
let profileDiv = document.getElementById("profile");
if (profileDiv) {
  fetch("http://localhost:1234/me", { credentials: "include" })
    .then(r => r.json())
    .then(user => {
      profileDiv.innerHTML = `<b>${user.username}</b> (Role: ${user.role})`;
    });
}

// handle article creation
let articleForm = document.getElementById("articleForm");
if (articleForm) {
  articleForm.onsubmit = async (e) => {
    e.preventDefault();
    let title = document.getElementById("title").value;
    let content = document.getElementById("content").value;
    let res = await fetch("http://localhost:1234/article", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content })
    });
    if (res.ok) {
      alert("Article published!");
      window.location.href = "index.html";
    } else {
      alert("Failed to publish");
    }
  };
}

// run on load
checkAuth();
