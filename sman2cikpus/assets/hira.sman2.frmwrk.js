async function initPage() {

  const backendurl = "http://192.168.18.2:5000"; const frontendurl = "http://192.168.18.2:5500/sman2cikpus" //development
  // const backendurl = "https://api.sman2cikpus.sch.id"; const frontendurl = "https://sman2cikpus.sch.id" //production
  
  // edit in hira.sman2.style.css
  document.head.appendChild(Object.assign(document.createElement("style"), {textContent: await fetch(`${frontendurl}/assets/hira.sman2.style.css`).then(r => r.text())}));
  
  // elements template
  if (document.querySelector('header')) document.querySelector('header').innerHTML =/*html*/`
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
  if (document.querySelector('footer')) document.querySelector('footer').innerHTML = /*html*/`
    <footer>
      <h5 style='color: red;'>UNRELEASED, DEVELOPMENT MODULE</h5>
      <h3>
        SMAN 2 Cikarang Pusat. Moving For Bright Future
        <br>
        <a href="https://github.com/hirakamu">@Hirakamu</a>
      </h3>
    </footer>
  `;

  // functions
  async function articleFeatures() {
    const container = document.getElementById("article-list");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";
    try {
      const res = await fetch(`${backendurl}/rand/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const articles = await res.json();
      container.innerHTML = '';
      articles.forEach(article => {
        const link = document.createElement('a');
        link.href = `baca.html?title=${encodeURIComponent(article.title)}`;
        link.className = 'article-card';
        link.innerHTML = `${article.img ? `<img src="${article.img}" alt="${article.title}">` : ''}<h3>${article.title}</h3><p>${article.content}</p>`;
        container.appendChild(link);
      });
    } catch (err) {
      container.innerHTML = `<h2 style="color:red;">Failed to fetch articles. Please Wait.</h2>`;
      console.error(err);
    }
  }
  async function readArticle() {
    const container = document.getElementById("article-content");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";
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
      const article = await res.json();
      container.innerHTML = `
      <h1>${article.title}</h1>
      <small>${article.date}</small>
      <hr>
      ${article.img ? `<img src="${article.img}" alt="${article.title}" style="max-width:100%;">` : ""}
      <div class="content">${marked.parse(article.content)}</div>
    `;

    } catch (err) {
      container.innerHTML = `<h2 style="color:red;">Failed to load article: ${err.message}</h2>`;
      console.error(err);
    }
  }

  window.articleFeatures = articleFeatures;
  window.readArticle = readArticle;
}

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
