const sample = {
  feature: {
    title: "Feature article title goes here",
    meta: "By Author Name · Oct 3, 2025 · 6 min read",
    excerpt: "Short excerpt to hook the reader. This is a sample paragraph that should summarize the feature and give a reason to click through.",
    image: "https://picsum.photos/seed/feature/800/500"
  },
  posts: Array.from({length:34}).map((_,i)=>({
    title:`Article #${i+1} — short headline`,
    meta:`Author ${i+1} · ${["Oct 1","Sep 28","Sep 20"][i%3]} · ${(3+i)%10} min`,
    excerpt:"A concise excerpt to give context and invite the reader to open the article.",
    thumb:`https://picsum.photos/seed/${i+1}/600/400`
  }))
};

// DOM refs
const year = document.getElementById('year');
const featureTitle = document.getElementById('feature-title');
const featureMeta = document.getElementById('feature-meta');
const featureExcerpt = document.getElementById('feature-excerpt');
const featureImg = document.querySelector('#feature img');
const feed = document.getElementById('feed');

// ping DOM refs
const pingBtn = document.getElementById('ping-btn');
const pingUrl = document.getElementById('ping-url');
const pingStatus = document.getElementById('ping-status');

// init feature + year
year.textContent = new Date().getFullYear();
featureTitle.textContent = sample.feature.title;
featureMeta.textContent = sample.feature.meta;
featureExcerpt.textContent = sample.feature.excerpt;
featureImg.src = sample.feature.image;

// render posts
sample.posts.forEach(p=>{
  const card = document.createElement('article');
  card.className = 'card';
  card.innerHTML = `
    <img class="thumb" src="${p.thumb}" alt="">
    <div style="flex:1">
      <div class="meta">${p.meta}</div>
      <h3 class="title">${p.title}</h3>
      <p class="excerpt">${p.excerpt}</p>
    </div>
  `;
  feed.appendChild(card);
});

// article click animation
document.addEventListener('click', e=>{
  const target = e.target.closest('.card');
  if(!target) return;
  console.log('Open article (static demo). Replace with real link or API fetch.');
  target.animate([{transform:'scale(1)'},{transform:'scale(0.995)'}],{duration:120,iterations:1});
});

// auto ping on load (no manual controls)
async function runPing() {
  if (!pingStatus) return;
  pingStatus.textContent = 'Connection: Loading';
  const target = 'http://localhost:5000/ping';
  try {
    const res = await fetch(target, { method: 'GET', credentials: 'include' });
    try {
      const data = await res.json();
      pingStatus.textContent = `Connection: Reachable (${res.status}) — ${data && data.status ? data.status : 'ok'}`;
    } catch {
      pingStatus.textContent = `Connection: Reachable (${res.status}) — response blocked`;
    }
  } catch (err) {
    console.error('ping error', err);
    pingStatus.textContent = 'Connection: Failed (browser blocked or server unreachable)';
  }
}

window.addEventListener('DOMContentLoaded', runPing);
