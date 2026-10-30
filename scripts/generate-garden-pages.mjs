import { execFileSync } from "node:child_process"
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

const rooms = [
  { key: "home", label: "首页", url: "/", icon: "home" },
  { key: "library", label: "Library", url: "/library/", icon: "book" },
  { key: "gallery", label: "Gallery", url: "/gallery/", icon: "frame" },
  { key: "studio", label: "Studio", url: "/studio/", icon: "tools" },
]

const icons = {
  home: '<path d="M4 11.5 12 5l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5h-5v5H5a1 1 0 0 1-1-1z"/>',
  book: '<path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H19v14H6.5A1.5 1.5 0 0 0 5 19.5z"/><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"/>',
  frame:
    '<rect x="4" y="5" width="16" height="14" rx="2"/><path d="m4 16 4.5-4.5 4 4 2.5-2.5L20 18"/><circle cx="15.5" cy="9.5" r="1.5"/>',
  tools:
    '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
}

function icon(name) {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`
}

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

// Last-change time per file. A fresh clone (Cloudflare build) gives every file the
// same mtime, so committed files use their last commit time; files with local,
// uncommitted changes use their mtime.
function gitTimes() {
  const times = new Map()
  const dirty = new Set()
  const git = (args) =>
    execFileSync("git", ["-c", "core.quotePath=false", ...args], {
      cwd: projectRoot,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
      stdio: ["ignore", "pipe", "ignore"],
    })

  try {
    let current = 0
    for (const line of git(["log", "--format=@@%ct", "--name-only", "--", "content", "html"]).split(
      "\n",
    )) {
      if (line.startsWith("@@")) current = Number(line.slice(2)) * 1000
      else if (line && !times.has(line)) times.set(line, current)
    }
    for (const line of git([
      "status",
      "--porcelain",
      "--untracked-files=all",
      "--",
      "content",
      "html",
    ]).split("\n")) {
      const file = line.slice(3).replace(/^"|"$/g, "")
      if (file) dirty.add(file.split(" -> ").pop())
    }
  } catch {
    // Not a git checkout: fall back to filesystem times.
  }

  return { times, dirty }
}

const history = gitTimes()

// Recorded by scripts/publish-notes.mjs at publish time; authoritative on every builder.
let publishDates = {}
try {
  publishDates = JSON.parse(await fs.readFile(path.join(projectRoot, "publish-dates.json"), "utf8"))
} catch {
  // No ledger yet: fall back to git / filesystem below.
}

async function updatedTime(file, frontmatter = {}) {
  const relative = path.relative(projectRoot, file).split(path.sep).join("/")
  const declared = Date.parse(
    frontmatter.updated || frontmatter.modified || publishDates[relative]?.modified || "",
  )
  if (!Number.isNaN(declared)) return declared

  if (!history.dirty.has(relative) && history.times.has(relative))
    return history.times.get(relative)

  return (await fs.stat(file)).mtimeMs
}

// "学习笔记/01 Areas/语文/初二课文" -> "语文 · 初二课文"
function shortFolder(folder) {
  if (!folder || folder === ".") return "未分类"
  const parts = folder
    .split(/[\\/]/)
    .filter((part) => part && !/^\d+\s*(areas?|projects?|resources?|archives?)$/i.test(part))
  if (parts.length > 1 && parts[0] === "学习笔记") parts.shift()
  return parts.slice(-2).join(" · ") || folder
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
    const folder = path.dirname(relativePath)

    notes.push({
      title: frontmatter.title || path.basename(file, ".md"),
      url: `/${slug}`,
      room: "Library",
      folder: folder === "." ? "" : folder.split(path.sep).join("/"),
      category: shortFolder(folder),
      updated: await updatedTime(file, frontmatter),
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
    let folder = path.dirname(relativePath)
    // html/<name>/index.html is one work, not a folder of works.
    if (path.basename(relativePath) === "index.html") folder = path.dirname(folder)

    pages.push({
      title: titleFromHtml(html, file),
      url: publicHtmlUrl(relativePath),
      room: "Gallery",
      folder: folder === "." ? "" : folder.split(path.sep).join("/"),
      category: folder === "." ? "作品" : shortFolder(folder),
      updated: await updatedTime(file),
      standalone: true,
    })
  }

  return pages.sort((a, b) => b.updated - a.updated)
}

async function getStudioItems() {
  const alist = {
    title: "Alist 资源库",
    kind: "文件与媒体",
    url: "https://melyi.uk/alist/",
    room: "Studio",
    category: "资源",
  }

  if (!(await pathExists(studioIndexPath))) return [alist]

  const raw = await fs.readFile(studioIndexPath, "utf8")
  const items = JSON.parse(raw)

  return [
    ...items.map((item) => ({
      title: item.title,
      kind: item.type || "Download",
      url: item.url,
      room: "Studio",
      category: "工具",
      standalone: item.standalone === true,
    })),
    alist,
  ]
}

function formatDate(ms) {
  if (!ms) return ""
  const date = new Date(ms)
  const now = new Date()
  const parts = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "numeric",
    day: "numeric",
  }).formatToParts(date)
  const get = (type) => parts.find((part) => part.type === type)?.value
  const sameYear = get("year") === String(now.getFullYear())
  return `${sameYear ? "" : `${get("year")}年`}${get("month")}月${get("day")}日`
}

function isExternal(url) {
  return /^https?:\/\//i.test(url)
}

function row(item, { showRoom = false } = {}) {
  const external = isExternal(item.url)
  // Standalone pages are not Quartz pages: let the browser load them normally.
  const attrs = item.standalone || external ? " data-router-ignore" : ""
  const target = external ? ' target="_blank" rel="noopener"' : ""
  const meta =
    item.kind || (showRoom ? `${item.room} · ${item.category}` : formatDate(item.updated))

  return `<a class="g-row" href="${escapeHtml(item.url)}" data-garden-item data-title="${escapeHtml(item.title)}" data-search="${escapeHtml(`${item.title} ${item.folder || ""} ${item.category || ""}`)}" data-room="${escapeHtml(item.room)}" data-updated="${Number(item.updated) || 0}"${attrs}${target}>
  <span class="g-row-text"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(meta)}</small></span>
  <span class="g-row-go" aria-hidden="true">${external ? "↗" : "›"}</span>
</a>`
}

function tabbar(active) {
  return `<nav class="g-tabbar" aria-label="花园导航">
  ${rooms
    .map(
      (room) =>
        `<a href="${room.url}"${room.key === active ? ' aria-current="page"' : ""}>${icon(room.icon)}<span>${room.label}</span></a>`,
    )
    .join("\n  ")}
</nav>`
}

function pageFrame({ title, description, cssClass, body }) {
  return `---
title: ${title}
description: ${description}
cssclasses:
  - garden-page
  - ${cssClass}
---

${body}
`
}

function homePage(notes, gallery) {
  const latest = [...notes, ...gallery].sort((a, b) => b.updated - a.updated).slice(0, 6)

  return pageFrame({
    title: "Rosemary Garden",
    description: "Rosemary 的学习、阅读与创作花园。",
    cssClass: "garden-home",
    body: `${tabbar("home")}

<header class="g-home-head">
  <h1>Rosemary Garden</h1>
  <a class="g-chip" href="https://gsw.melyi.uk/" data-router-ignore target="_blank" rel="noopener">谈诗说文<span aria-hidden="true">↗</span></a>
</header>

<figure class="g-hero">
  <img src="/static/garden/cockatiel-hero.png" alt="Rosemary Garden 插画：树枝上的玄凤鹦鹉与一本书" loading="eager" decoding="async" />
</figure>

<section class="g-section" data-recent-section hidden>
  <h2>继续阅读</h2>
  <div class="g-list" data-recent-list></div>
</section>

<section class="g-section">
  <div class="g-section-head"><h2>最近更新</h2><a href="/library/">全部 ›</a></div>
  <div class="g-list">${latest.map((item) => row(item, { showRoom: true })).join("\n")}</div>
</section>`,
  })
}

function listingPage({ title, description, cssClass, active, items, searchable = true }) {
  const groups = new Map()
  for (const item of items) {
    const key = item.category || item.room
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(item)
  }

  // Folder headings only help when a folder groups several items.
  const flat = groups.size < 2 || [...groups.values()].every((group) => group.length < 2)

  const tools = searchable
    ? `<div class="g-tools">
  <label class="g-search"><span class="g-visually-hidden">搜索</span><input type="search" data-garden-search placeholder="搜索标题或目录" enterkeyhint="search" autocomplete="off" /></label>
  <div class="g-segment" role="radiogroup" aria-label="排序">
    <button type="button" role="radio" aria-checked="true" data-sort="updated">最近</button>
    <button type="button" role="radio" aria-checked="false" data-sort="title">标题</button>
  </div>
</div>`
    : ""

  return pageFrame({
    title,
    description,
    cssClass,
    body: `${tabbar(active)}

<header class="g-page-head">
  <h1>${escapeHtml(title)}</h1>
  <span class="g-count" data-garden-count>${items.length} 项</span>
</header>

${tools}

<div class="g-directory" data-garden-directory>
${(flat ? [["", items]] : [...groups])
  .map(
    ([group, groupItems]) => `<details class="g-folder${flat ? " is-flat" : ""}" data-folder open>
  ${flat ? "" : `<summary><span>${escapeHtml(group)}</span><em>${groupItems.length}</em></summary>`}
  <div class="g-list">${groupItems.map((item) => row(item)).join("\n")}</div>
</details>`,
  )
  .join("\n")}
</div>
<p class="g-empty" data-garden-empty hidden>没有找到匹配的内容</p>`,
  })
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

  await writePage("index.md", homePage(notes, gallery))
  await writePage(
    path.join("library", "index.md"),
    listingPage({
      title: "Library",
      description: "课程笔记与阅读导读。",
      cssClass: "garden-library",
      active: "library",
      items: notes,
    }),
  )
  await writePage(
    path.join("gallery", "index.md"),
    listingPage({
      title: "Gallery",
      description: "互动网页与创作作品。",
      cssClass: "garden-gallery",
      active: "gallery",
      items: gallery,
    }),
  )
  await writePage(
    path.join("studio", "index.md"),
    listingPage({
      title: "Studio",
      description: "工具、资源与有声书。",
      cssClass: "garden-studio",
      active: "studio",
      items: studio,
      searchable: false,
    }),
  )

  console.log(
    `Garden pages: ${notes.length} notes, ${gallery.length} gallery items, ${studio.length} studio items`,
  )
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
