---
title: Studio
cssclasses:
  - garden-page
  - garden-studio
---

<section class="garden-listing-hero">
  <p class="garden-eyebrow">Resources / Tools / Downloads</p>
  <h1>Studio</h1>
  <nav class="garden-nav" aria-label="Garden sections">
  <a href="/">Home</a>
  <a href="/library/">Library</a>
  <a href="/gallery/">Gallery</a>
  <a href="/studio/">Studio</a>
</nav>
</section>

<section class="garden-section">
  <div class="garden-tools">
    <label class="garden-search"><span>搜索</span><input type="search" data-garden-search placeholder="搜索标题或目录" /></label>
    <label class="garden-sort"><span>排序</span><select data-garden-sort><option value="updated">最近更新</option><option value="title">标题 A–Z</option></select></label>
    <span class="garden-count" data-garden-count>2 项</span>
  </div>
  <div class="garden-directory" data-garden-directory><section class="garden-folder" data-folder="Studio"><h2>Studio</h2><div class="garden-list"><a class="garden-card" href="/studio/audiobooks/" data-garden-item data-title="有声书 · 听见一本书" data-category="Studio" data-updated="0" data-router-ignore>
  <strong>有声书 · 听见一本书</strong>
</a>
<a class="garden-card" href="https://melyi.uk/alist/" data-garden-item data-title="Alist Resource Library" data-category="Studio" data-updated="0" data-router-ignore>
  <strong>Alist Resource Library</strong>
</a></div></section></div>
</section>
<script>
(() => {
  const key = "rosemary-garden-recent-v1";
  const read = () => { try { return JSON.parse(localStorage.getItem(key) || "[]") } catch { return [] } };
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[data-garden-item]");
    if (!link || !link.dataset.title || link.href.startsWith("javascript:")) return;
    const items = read().filter((item) => item.url !== link.href);
    items.unshift({ title: link.dataset.title, url: link.href, category: link.dataset.category, updated: Number(link.dataset.updated) || 0 });
    localStorage.setItem(key, JSON.stringify(items.slice(0, 24)));
  });
  const recent = document.querySelector("[data-recent-list]");
  if (recent) {
    const fallback = JSON.parse(recent.dataset.fallback || "[]");
    const items = read();
    const source = items.length ? items : fallback;
    recent.replaceChildren();
    for (const item of source.slice(0, 6)) {
      const link = document.createElement("a"); link.className = "garden-row"; link.href = item.url;
      const title = document.createElement("strong"); title.textContent = item.title;
      link.append(title); recent.append(link);
    }
  }
  const search = document.querySelector("[data-garden-search]");
  const sort = document.querySelector("[data-garden-sort]");
  if (!search || !sort) return;
  const rows = [...document.querySelectorAll("[data-garden-item]")];
  const count = document.querySelector("[data-garden-count]");
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const folder of document.querySelectorAll("[data-folder]")) {
      const list = folder.querySelector(".garden-list");
      const folderRows = [...list.querySelectorAll("[data-garden-item]")];
      folderRows.sort((a, b) => sort.value === "title" ? a.dataset.title.localeCompare(b.dataset.title, "zh-CN") : Number(b.dataset.updated) - Number(a.dataset.updated));
      for (const row of folderRows) { list.append(row); const text = (row.dataset.title + " " + folder.dataset.folder).toLocaleLowerCase(); row.hidden = !text.includes(query); if (!row.hidden) visible++; }
      folder.hidden = !folderRows.some((row) => !row.hidden);
    }
    count.textContent = visible + " 项";
  };
  search.addEventListener("input", update); sort.addEventListener("change", update); update();
})();
</script>
