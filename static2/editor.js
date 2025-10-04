// helper: fetch with timeout
async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 5000 } = options; // default 5s
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

async function loadArticles() {
  let container = document.getElementById("articles");
  if (!container) return;
  container.innerHTML = "<p>Loading articles...</p>";
  try {
    let res = await fetchWithTimeout("http://localhost:1234/articles", {
      credentials: "include",
      timeout: 4000, // 4 seconds
    });
    if (!res.ok) throw new Error("Bad response");
    let data = await res.json();
    container.innerHTML = "";
    data.forEach(article => {
      let div = document.createElement("div");
      div.className = "article";
      div.innerHTML = `<h3>${article.title}</h3>
                       <small>${article.author} | ${article.createdAt}</small>
                       <p>${article.content}</p>`;
      container.appendChild(div);
    });
  } catch (err) {
    container.innerHTML = `<p style="color:red;">⚠️ Tidak bisa menghubungi server backend. Silakan coba lagi nanti.</p>`;
    console.error("Backend unreachable:", err);
  }
}

window.onload = loadArticles;
