async function loadPage() {
  // Header HTML
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

  // Footer HTML
  const footerHTML = `
    <footer>
      <p>&copy; 2025 My Website</p>
    </footer>
  `;

  const css = `
    /* Reset */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /* Body */
    body {
      font-family: "Futura PT", sans-serif;
      background: #f5f5f5;
      color: #333;
      line-height: 1.6;
    }

    /* Header + Nav */
    header {
      background: #222;
      color: white;
      padding: 15px 20px;
    }

    header h1 {
      margin-bottom: 10px;
    }

    nav ul {
      list-style: none;
      display: flex;
      gap: 15px;
    }

    nav a {
      color: white;
      text-decoration: none;
      font-weight: bold;
    }

    nav a:hover {
      text-decoration: underline;
    }

    /* Footer */
    footer {
      text-align: center;
      padding: 15px;
      background: #222;
      color: white;
      margin-top: 30px;
    }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // Inject into the page
  document.getElementById('header').innerHTML = headerHTML;
  document.getElementById('footer').innerHTML = footerHTML;
}
loadPage();