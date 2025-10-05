async function initPage() {
  // =====================
  // CSS Injection
  // =====================
  const css = `
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:"Futura PT", sans-serif; background:#f5f5f5; color:#333; line-height:1.6; }
    header { background:#222; color:white; padding:15px 20px; }
    header h1 { margin-bottom:10px; }
    nav ul { list-style:none; display:flex; gap:15px; }
    nav a { color:white; text-decoration:none; font-weight:bold; }
    nav a:hover { text-decoration:underline; }
    footer { text-align:center; padding:15px; background:#222; color:white; margin-top:30px; }
    .article a { color:black; text-decoration:none; }
    .article a:hover { text-decoration:underline; }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // =====================
  // Backend URL
  // =====================
  const backendurl = "http://192.168.18.2:5000";

  // =====================
  // Templates
  // =====================
  const templates = {
    header: `<header><h1>SMAN 2 Cikarang Pusat</h1><nav><ul><li><a href=".">Beranda</a></li><li><a href="./page/artikel">Artikel</a></li><li><a href="./page/tentang">Tentang Sekolah</a></li><li><a href="#kontak">Kontak</a></li><li id="credential"><a href=""></a></li></ul></nav></header>`,
    footer: `<footer><p>&copy; {{year}} {{site}}</p></footer>`,
    articlearea: `<section class="articles"><div class="container"><slot></slot></div></section>`,
    readingarea: `<article class="reading container"><header><h2>{{title}}</h2></header><main>{{body}}</main></article>`
  };

  function interpolate(tpl, ctx = {}) {
    return tpl.replace(/\{\{\s*([^\}\s]+)\s*\}\}/g, (_, key) => ctx[key] || '');
  }

  async function renderTemplate(el, tpl, ctx = {}) {
    ctx.year = ctx.year || new Date().getFullYear();
    ctx.site = ctx.site || document.title || '';
    let out = interpolate(tpl, ctx);

    if (out.includes('<slot')) {
      const wrapper = document.createElement('div');
      wrapper.innerHTML = out;
      wrapper.querySelectorAll('slot').forEach(s => s.outerHTML = el.innerHTML || '');
      el.innerHTML = wrapper.innerHTML;
    } else {
      el.innerHTML = out;
    }
  }

  // =====================
  // Header/Footer Render
  // =====================
  const headerEl = document.getElementById('header');
  const footerEl = document.getElementById('footer');
  if (headerEl) await renderTemplate(headerEl, templates.header);
  if (footerEl) await renderTemplate(footerEl, templates.footer);

  // =====================
  // Article Functions
  // =====================
  async function articleFeatures() {
    const container = document.getElementById("article-list");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";
    try {
      const res = await fetch(`${backendurl}/post/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      container.innerHTML = "";
      data.forEach(article => {
        const div = document.createElement("div");
        div.className = "article";
        div.innerHTML = `
          ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" style="max-width:100%;height:auto;">` : ""}
          <h3>
            <a href="./page/baca.html?title=${article.title.trim().toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9-]/g,"")}">
              ${article.title}
            </a>
          </h3>
          <p>${article.preview}</p>
          <br><hr><br>
        `;
        container.appendChild(div);
      });
    } catch (err) {
      container.innerHTML = `<p style="color:red;">Failed to load articles: ${err.message}</p>`;
      console.error(err);
    }
  }

  async function loadArticle() {
    const params = new URLSearchParams(window.location.search);
    const titleSlug = params.get("title");
    if (!titleSlug) return;

    try {
      const res = await fetch(`${backendurl}/post/baca?title=${encodeURIComponent(titleSlug)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const article = await res.json();
      const titleEl = document.getElementById("title");
      const bodyEl = document.getElementById("article-body");
      if (titleEl) titleEl.textContent = article.title + " - SMAN 2 Cikarang Pusat";
      if (bodyEl) bodyEl.innerHTML = article.html;
    } catch (err) {
      console.error(err);
    }
  }

  // Expose functions
  window.articleFeatures = articleFeatures;
  window.loadArticle = loadArticle;
}

// Run on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initPage());
} else {
  initPage();
}
