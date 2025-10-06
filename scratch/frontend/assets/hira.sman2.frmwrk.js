async function initPage() {
  // =====================
  // Backend URL
  // =====================
  //const backendurl = "http://localhost:5000"; // development
  const backendurl = "https://api.sman2cikpus.sch.id"; // production
  // =====================
  // Header/Footer Templates
  // =====================
  const headerHTML = `
    <header>
      <h1>SMAN 2 Cikarang Pusat</h1>
      <nav>
        <ul>
          <li><a href=".">Beranda</a></li>
          <li><a href="artikel.html">Artikel</a></li>
          <li><a href="tentang.html">Tentang Sekolah</a></li>
          <li><a href="#kontak">Kontak</a></li>
        </ul>
      </nav>
    </header>
  `;
  const footerHTML = `<footer>&copy; ${new Date().getFullYear()} SMAN 2 Cikarang Pusat</footer>`;

  const headerEl = document.querySelector('header');
  const footerEl = document.querySelector('footer');
  if (headerEl) headerEl.innerHTML = headerHTML;
  if (footerEl) footerEl.innerHTML = footerHTML;

  // =====================
  // Article Loader
  // =====================
  async function articleFeatures() {
    const container = document.getElementById("article-list");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";

    try {
      const res = await fetch(`${backendurl}/rand/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const articles = await res.json(); // <-- assume backend sends JSON [{title, content, img?}, ...]
      container.innerHTML = ''; // clear loading

      articles.forEach(article => {
        const link = document.createElement('a');
        link.href = `baca.html?title=${encodeURIComponent(article.title)}`;
        link.className = 'article-card';  // apply same card styles
        link.innerHTML = `${article.img ? `<img src="${article.img}" alt="${article.title}">` : ''}<h3>${article.title}</h3><p>${article.content}</p>
`;
        container.appendChild(link);
      });

    } catch (err) {
      container.innerHTML = `<h2 style="color:red;">Failed to load articles: ${err.message}</h2>`;
      console.error(err);
    }
  }

  async function readArticle() {
    const container = document.getElementById("article-content");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";

    // get ?title=... from URL
    const params = new URLSearchParams(window.location.search);
    const title = params.get("title");
    if (!title) {
      container.innerHTML = "<h2 style='color:red;'>No article selected</h2>";
      return;
    }

    try {
      const { marked } = await import("https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js");

      const res = await fetch(`${backendurl}/baca?title=${encodeURIComponent(title)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const article = await res.json(); // {title, date, content, img}
      container.innerHTML = `
      <h1>${article.title}</h1>
      <small>${article.date}</small>
      <hr>
      ${article.img ? `<img src="${article.img}" alt="${article.title}" style="max-width:100%;">` : ""}
      <div class="content">${marked.parse(article.content)}</div>
    `;
      // note: marked.js (https://marked.js.org/) or similar needed if you want Markdown → HTML in browser

    } catch (err) {
      container.innerHTML = `<h2 style="color:red;">Failed to load article: ${err.message}</h2>`;
      console.error(err);
    }
  }

  // =====================
  // Expose globally
  // =====================
  window.articleFeatures = articleFeatures;
  window.readArticle = readArticle;
}

// Run when DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initPage().then(() => articleFeatures()));
} else {
  initPage().then(() => articleFeatures());
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initPage().then(() => readArticle()));
} else {
  initPage().then(() => readArticle());
}
