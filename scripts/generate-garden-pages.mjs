import fs from "node:fs/promises"
import path from "node:path"

const projectRoot = path.resolve(import.meta.dirname, "..")
const contentDir = path.join(projectRoot, "content")
const htmlDir = path.join(projectRoot, "html")
const studioIndexPath = path.join(projectRoot, "studio", "downloads-index.json")

const generatedPages = new Set([
  "index.md",
  path.join("library", "index.md"),
  path.join("gallery", "index.md"),
  path.join("studio", "index.md"),
])

async function pathExists(filePath) {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

async function walk(dir, files = []) {
  if (!(await pathExists(dir))) return files

  const entries = await fs.readdir(dir, { withFileTypes: true })

  for (const entry of entries) {
    if (entry.name === ".DS_Store") continue
    if (entry.name === "README.md") continue

    const fullPath = path.join(dir, entry.name)

    if (entry.isDirectory()) {
      await walk(fullPath, files)
    } else if (entry.isFile()) {
      files.push(fullPath)
    }
  }

  return files
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
}

function stripFrontmatter(markdown) {
  return markdown.replace(/^---\n[\s\S]*?\n---\n?/, "")
}

function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---/)
  const data = {}
  if (!match) return data

  for (const line of match[1].split("\n")) {
    const pair = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/)
    if (!pair) continue
    data[pair[1]] = pair[2].replace(/^["']|["']$/g, "").trim()
  }

  return data
}

function firstHeading(markdown) {
  return stripFrontmatter(markdown).match(/^#\s+(.+)$/m)?.[1]?.trim()
}

function firstParagraph(markdown) {
  const body = stripFrontmatter(markdown)
  const paragraph = body
    .split(/\n{2,}/)
    .map((block) =>
      block
        .replace(/^#+\s+.*$/gm, "")
        .replace(/^---+$/gm, "")
        .replace(/^>\s?/gm, "")
        .trim(),
    )
    .find((block) => block && !block.startsWith("![["))

  return paragraph?.replace(/\s+/g, " ").slice(0, 170)
}

function titleFromHtml(html, filePath) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)
  const title = match?.[1]
    ?.replace(/\s+/g, " ")
    .replace(/&nbsp;/g, " ")
    .trim()

  return title || path.basename(filePath, path.extname(filePath))
}

function publicHtmlUrl(relativePath) {
  const normalized = relativePath.split(path.sep).join("/")

  if (normalized.endsWith("/index.html")) {
    return `/html/${normalized.replace(/\/index\.html$/, "/")}`
  }

  return `/html/${normalized}`
}

async function getNotes() {
  const files = (await walk(contentDir)).filter((file) => file.endsWith(".md"))
  const notes = []

  for (const file of files) {
    const relativePath = path.relative(contentDir, file)
    if (generatedPages.has(relativePath)) continue

    const markdown = await fs.readFile(file, "utf8")
    const frontmatter = parseFrontmatter(markdown)
    const slug = relativePath.replace(/\.md$/, "").split(path.sep).join("/")

    notes.push({
      title: frontmatter.title || path.basename(file, ".md"),
      summary: frontmatter.description || firstParagraph(markdown) || "A note from Rosemary Garden.",
      url: `/${slug}`,
      type: "Note",
      room: "Library",
      category: path.dirname(relativePath) === "." ? "未分类" : path.dirname(relativePath),
      updated: (await fs.stat(file)).mtimeMs,
    })
  }

  return notes.sort((a, b) => b.updated - a.updated)
}

async function getHtmlPages() {
  const files = (await walk(htmlDir)).filter((file) => file.toLowerCase().endsWith(".html"))
  const pages = []

  for (const file of files) {
    const html = await fs.readFile(file, "utf8")
    const relativePath = path.relative(htmlDir, file)

    pages.push({
      title: titleFromHtml(html, file),
      summary: "An interactive page or visual work from the gallery.",
      url: publicHtmlUrl(relativePath),
      type: "Gallery",
      room: "Gallery",
      category: path.dirname(relativePath) === "." ? "未分类" : path.dirname(relativePath),
      updated: (await fs.stat(file)).mtimeMs,
    })
  }

  return pages.sort((a, b) => b.updated - a.updated)
}

async function getStudioItems() {
  const alist = {
    title: "Alist Resource Library",
    type: "Resource Hub",
    summary: "Browse extended files, media, and long-term resources.",
    url: "https://melyi.uk/alist/",
    room: "Studio",
  }

  if (!(await pathExists(studioIndexPath))) return [alist]

  const raw = await fs.readFile(studioIndexPath, "utf8")
  const items = JSON.parse(raw)

  return [
    ...items.map((item) => ({
      title: item.title,
      type: item.type || "Download",
      summary: item.description || "A downloadable resource from the studio.",
      url: item.url,
      room: "Studio",
      standalone: item.standalone === true,
    })),
    alist,
  ]
}

function card(item) {
  const routerIgnore = item.standalone || /^https?:\/\//i.test(item.url) ? " data-router-ignore" : ""

  return `<a class="garden-card" href="${escapeHtml(item.url)}" data-garden-item data-title="${escapeHtml(item.title)}" data-category="${escapeHtml(item.category || item.room)}" data-updated="${Number(item.updated) || 0}"${routerIgnore}>
  <strong>${escapeHtml(item.title)}</strong>
</a>`
}

function pageFrame({ title, subtitle, cssClass, body }) {
  return `---
title: ${title}
cssclasses:
  - garden-page
  - ${cssClass}
---

${body}
`
}

function nav({ isHome = false } = {}) {
  return `<nav class="garden-nav" aria-label="Garden sections">
  ${isHome ? '<a href="https://gsw.melyi.uk/" data-router-ignore>谈诗说文</a>' : '<a href="/">Home</a>'}
  <a href="/library/">Library</a>
  <a href="/gallery/">Gallery</a>
  <a href="/studio/">Studio</a>
</nav>`
}

function homePage(notes, gallery, studio) {
  const featured = [...gallery, ...notes, ...studio].slice(0, 4)
  const recent = [...gallery, ...notes].slice(0, 6)

  return pageFrame({
    title: "Rosemary Garden",
    cssClass: "garden-home",
    body: `<section class="garden-hero">
  <div class="garden-hero-copy">
    <p class="garden-eyebrow">学习 · 阅读 · 创作</p>
    <h1>Rosemary Garden</h1>
    ${nav({ isHome: true })}
  </div>
  <figure class="garden-hero-art">
    <picture>
      <img src="/static/garden/cockatiel-hero.png" alt="A dreamy editorial illustration of a cockatiel in Rosemary Garden" loading="eager" decoding="async" onerror="this.onerror=null;this.src='/static/garden/cockatiel-hero.png'" />
    </picture>
  </figure>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">探索花园</p>
    <h2>今天想从哪里开始？</h2>
  </div>
  <div class="garden-room-grid">
    ${roomCard("Library", "课程笔记与阅读发现", "/library/")}
    ${roomCard("Gallery", "作品、网页与创意实验", "/gallery/")}
    ${roomCard("Studio", "工具、资源与听书", "/studio/")}
  </div>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">最近更新</p>
    <h2>新鲜上架</h2>
  </div>
  <div class="garden-card-grid">${featured.map(card).join("\n")}</div>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">接着逛</p>
    <h2>最近浏览</h2>
  </div>
  <div class="garden-list" data-recent-list data-fallback="${escapeHtml(JSON.stringify(recent))}">${recent.map(card).join("\n")}</div>
</section>
${recentBrowserScript()}`,
  })
}

function roomCard(title, summary, url) {
  return `<a class="garden-room" href="${url}">
  <span>${title}</span>
</a>`
}

function listingPage({ title, eyebrow, intro, cssClass, items }) {
  const categories = [...new Set(items.map((item) => item.category || item.room))]
  return pageFrame({
    title,
    cssClass,
    body: `<section class="garden-listing-hero">
  <p class="garden-eyebrow">${escapeHtml(eyebrow)}</p>
  <h1>${escapeHtml(title)}</h1>
  ${nav()}
</section>

<section class="garden-section">
  <div class="garden-tools">
    <label class="garden-search"><span>搜索</span><input type="search" data-garden-search placeholder="搜索标题或目录" /></label>
    <label class="garden-sort"><span>排序</span><select data-garden-sort><option value="updated">最近更新</option><option value="title">标题 A–Z</option></select></label>
    <span class="garden-count" data-garden-count>${items.length} 项</span>
  </div>
  <div class="garden-directory" data-garden-directory>${categories.map((category) => `<section class="garden-folder" data-folder="${escapeHtml(category)}"><h2>${escapeHtml(category)}</h2><div class="garden-list">${items.filter((item) => (item.category || item.room) === category).map(card).join("\n")}</div></section>`).join("\n")}</div>
</section>
${recentBrowserScript()}`,
  })
}

function recentBrowserScript() {
  return `<script>
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
</script>`
}

function emptyState() {
  return `<div class="garden-empty">This room is waiting for its first bloom.</div>`
}

async function writePage(name, content) {
  const outputPath = path.join(contentDir, name)
  await fs.mkdir(path.dirname(outputPath), { recursive: true })
  await fs.writeFile(outputPath, content)
}

async function main() {
  const notes = await getNotes()
  const gallery = await getHtmlPages()
  const studio = await getStudioItems()

  await writePage("index.md", homePage(notes, gallery, studio))
  await writePage(
    path.join("library", "index.md"),
    listingPage({
      title: "Library",
      eyebrow: "Notes / Reading / Thinking",
      intro: "A quiet room for notes, reading trails, and gathered ideas from Obsidian.",
      cssClass: "garden-library",
      items: notes,
    }),
  )
  await writePage(
    path.join("gallery", "index.md"),
    listingPage({
      title: "Gallery",
      eyebrow: "Works / Pages / Visuals",
      intro: "A bright exhibition room for interactive pages, slides, images, and project pieces.",
      cssClass: "garden-gallery",
      items: gallery,
    }),
  )
  await writePage(
    path.join("studio", "index.md"),
    listingPage({
      title: "Studio",
      eyebrow: "Resources / Tools / Downloads",
      intro: "A working room for resource links, downloadable materials, and future creative tools.",
      cssClass: "garden-studio",
      items: studio,
    }),
  )

  console.log(`Garden pages: ${notes.length} notes, ${gallery.length} gallery items, ${studio.length} studio items`)
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
