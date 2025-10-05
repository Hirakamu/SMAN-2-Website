// endpoint

let backendurl = "http://192.168.18.2:5000"; //development
//let backendurl = "https://api.sman2cikpus.sch.id"; //production


// Public Functions
async function articleFeatures() {
    let container = document.getElementById("article-list");
    container.innerHTML = "<p>Loading...</p>";
    try {
        let res = await fetch(`${backendurl}/post/`);
        if (!res.ok) { throw new Error(`HTTP error ${res.status}`); }
        let data = await res.json();
        container.innerHTML = "";
        data.forEach(article => {
            let div = document.createElement("div");
            div.className = "article";
            div.innerHTML = `
                ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" style="max-width:100%;height:auto;">` : ""}
                <h3>
                  <a style=".article a {color: black;text-decoration: none;} .article a:hover {text-decoration: underline;}" href="./page/baca.html?title=${article.title.trim().toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}">
                    ${article.title}
                  </a>
                </h3>
                <p>${article.preview}</p>
                <br>
                <hr>
                <br>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        container.innerHTML = `<p style="color:red;">Failed to load articles: ${err.message}</p>`;
        console.error("Error loading articles:", err);
    }
}
async function loadArticle() {
    const params = new URLSearchParams(window.location.search);
    const titleSlug = params.get("title");
    if (!titleSlug) {
        document.getElementById("article-title").textContent = "Missing title parameter";
        document.getElementById("article-body").innerHTML = "";
        return;
    }

    try {
        const res = await fetch(`${backendurl}/post/baca?title=${encodeURIComponent(titleSlug)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const article = await res.json();

        document.getElementById("title").textContent = article.title + " - SMAN 2 Cikarang Pusat";
        document.getElementById("article-body").innerHTML = article.html;
    } catch (err) {
        document.getElementById("article-title").textContent = "Failed to load article";
        document.getElementById("article-body").textContent = err.message;
        console.error(err);
    }
}

// Elements
(() => {
  // Templates (modify this data if needed)
  const defaultTemplates = {
    header: `
      <header>
      <h1>SMAN 2 Cikarang Pusat</h1>
      <nav>
        <ul>
          <li><a href=".">Beranda</a></li>
          <li><a href="./page/artikel">Artikel</a></li>
          <li><a href="./page/tentang">Tentang Sekolah</a></li>
          <li><a href="#kontak">Kontak</a></li>
          <li id="credential"><a href=""></a></li>
        </ul>
      </nav>
    </header>

    `,
    footer: `
      <div class="site-footer">
        <div class="container">
          <small>&copy; {{year}} {{site}}</small>
        </div>
      </div>
    `,
    articlearea: `
      <section class="articles">
        <div class="container">
          <slot> <!-- fallback if inner HTML present --> </slot>
        </div>
      </section>
    `,
    newsarea: `
      <section class="news">
        <div class="container"><h2>Latest News</h2><div class="news-list">{{content}}</div></div>
      </section>
    `,
    loginarea: `
      <div class="login-area container">
        <form id="login-form">
          <input name="username" placeholder="username"><input name="password" type="password" placeholder="password">
          <button type="submit">Login</button>
        </form>
      </div>
    `,
    adminarea: `
      <section class="admin-area container">
        <h2>Admin</h2>
        <div class="admin-controls">{{controls}}</div>
      </section>
    `,
    readingarea: `
      <article class="reading container">
        <header><h2>{{title}}</h2></header>
        <main>{{body}}</main>
      </article>
    `,
    homearea: `
      <section class="home container">
        <h2>{{headline}}</h2>
        <p>{{lead}}</p>
      </section>
    `
  };

  // Public API holder
  const Includes = {
    templates: { ...defaultTemplates },
    setTemplate(name, tpl) { this.templates[name] = tpl; rerender(name); },
    getTemplate(name) { return this.templates[name]; },
    async renderAll() { await renderNames(Object.keys(this.templates)); },
  };
  // interpolation: {{key}} reads attribute or dataset or context
  function interpolate(tpl, el, ctx = {}) {
    return tpl.replace(/\{\{\s*([^\}\s]+)\s*\}\}/g, (_, key) => {
      if (key in ctx) return ctx[key];
      if (el.hasAttribute(key)) return el.getAttribute(key);
      if (el.dataset && (key in el.dataset)) return el.dataset[key];
      return '';
    });
  }
  async function loadExternal(url) {
    try {
      const r = await fetch(url, { cache: "no-cache" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.text();
    } catch (e) {
      console.warn('Includes: failed to fetch', url, e);
      return '';
    }
  }
  async function renderElement(name, el) {
    // Priority: data-src -> global template -> inline tpl attr -> existing innerHTML
    let tpl = '';
    if (el.dataset && el.dataset.src) {
      tpl = await loadExternal(el.dataset.src);
    } else if (Includes.templates[name]) {
      tpl = Includes.templates[name];
    } else if (el.getAttribute('tpl')) {
      tpl = el.getAttribute('tpl');
    } else {
      tpl = el.innerHTML || '';
    }

    // allow passing a JSON context via data-ctx or ctx attribute
    let ctx = {};
    const ctxAttr = el.getAttribute('ctx') || el.dataset.ctx;
    if (ctxAttr) {
      try { ctx = JSON.parse(ctxAttr); } catch (e) { /* ignore */ }
    }

    // add a few automatic fields
    ctx.year = ctx.year || new Date().getFullYear();
    ctx.site = ctx.site || document.title || '';

    const out = interpolate(tpl, el, ctx);
    // if template contains <slot> and element had content, preserve it
    if (out.includes('<slot')) {
      // keep original children as fallback (simple approach)
      const wrapper = document.createElement('div');
      wrapper.innerHTML = out;
      // replace <slot> with original innerHTML
      wrapper.querySelectorAll('slot').forEach(s => {
        s.outerHTML = el.innerHTML || '';
      });
      el.innerHTML = wrapper.innerHTML;
    } else {
      el.innerHTML = out;
    }
  }
  async function renderNames(names) {
    for (const name of names) {
      const nodes = document.querySelectorAll(name);
      for (const el of nodes) {
        await renderElement(name, el);
      }
    }
  }
  async function rerender(name) {
    if (!name) return Includes.renderAll();
    if (Array.isArray(name)) return renderNames(name);
    await renderNames([name]);
  }
  
  // expose to window
  window.Includes = Includes;

  // auto-run after DOM loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Includes.renderAll());
  } else {
    Includes.renderAll();
  }

})();
