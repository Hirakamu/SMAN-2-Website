// article.js — load article from /articles
const API = "http://YOUR_SERVER:5000"; // replace with your server
const artTitle = document.getElementById('art-title');
const artMeta = document.getElementById('art-meta');
const artContent = document.getElementById('art-content');
const notfound = document.getElementById('notfound');

function qs(param) {
  return new URLSearchParams(location.search).get(param);
}

async function loadArticles() {
  try {
    const res = await fetch(`${API}/articles`);
    if(!res.ok) throw new Error(`status ${res.status}`);
    const arr = await res.json();
    return arr;
  } catch (err) {
    console.error(err);
    return null;
  }
}

(async function init() {
  const id = qs('id');
  if(!id) {
    artTitle.textContent = "Article id missing";
    return;
  }

  const articles = await loadArticles();
  if(!articles) {
    artTitle.textContent = "Failed to load article";
    return;
  }

  const a = articles.find(x => String(x.id) === String(id));
  if(!a) {
    notfound.style.display = 'block';
    document.getElementById('article-root').style.display = 'none';
    return;
  }

  artTitle.textContent = a.title || 'Untitled';
  artMeta.textContent = `Author ID ${a.author} · Article ID ${a.id}`;
  // content may be stored as HTML or plain text. render safely:
  artContent.innerText = a.content || '';
})();
