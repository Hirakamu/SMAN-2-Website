let backendurl = "http://192.168.18.2:5000";
//let backendurl = "https://api.sman2cikpus.sch.id";
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