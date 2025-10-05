async function initPage() {
  // =====================
  // CSS Injection
  // =====================
  const css = `
    /* Reset */
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f9f9f9; color:#333; line-height:1.6; }
    
    header { background:#222; color:white; padding:15px 20px; }
    header h1 { margin-bottom:10px; }
    nav ul { list-style:none; display:flex; gap:15px; }
    nav a { color:white; text-decoration:none; font-weight:bold; }
    nav a:hover { text-decoration:underline; }

    footer { text-align:center; padding:15px; background:#222; color:white; margin-top:30px; }

    /* Article card (for articleFeatures) */
    .article-card { background:#fff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08); overflow:hidden; transition: transform 0.2s, box-shadow 0.2s; }
    .article-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
    .article-card img { width:100%; height:180px; object-fit:cover; }
    .article-card h3 { font-size:1.2rem; color:#333; margin:15px 20px 10px 20px; }
    .article-card p { font-size:0.95rem; color:#555; line-height:1.5; margin:0 20px 20px 20px; }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // =====================
  // Backend URL
  // =====================
  const backendurl = "http://192.168.18.2:5000";

  // =====================
  // Header/Footer Templates
  // =====================
  const headerHTML = `
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
      const res = await fetch(`${backendurl}/post/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      container.innerHTML = "";
      data.forEach(article => {
        const div = document.createElement("div");
        div.className = "article-card";
        div.innerHTML = `
          ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}">` : ""}
          <h3><a href="./page/baca.html?title=${article.title.trim().toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9-]/g,"")}">${article.title}</a></h3>
          <p>${article.preview}</p>
        `;
        container.appendChild(div);
      });

    } catch (err) {
      container.innerHTML = `<p style="color:red;">Failed to load articles: ${err.message}</p>`;
      console.error(err);
    }
  }

  // =====================
  // Expose globally
  // =====================
  window.articleFeatures = articleFeatures;
}

// Run when DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initPage().then(() => articleFeatures()));
} else {
  initPage().then(() => articleFeatures());
}
