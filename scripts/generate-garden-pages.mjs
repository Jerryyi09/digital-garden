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
      title: frontmatter.title || firstHeading(markdown) || path.basename(file, ".md"),
      summary: frontmatter.description || firstParagraph(markdown) || "A note from Rosemary Garden.",
      url: `/${slug}`,
      type: "Note",
      room: "Library",
    })
  }

  return notes.sort((a, b) => a.title.localeCompare(b.title, "zh-CN"))
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
    })
  }

  return pages.sort((a, b) => a.title.localeCompare(b.title, "zh-CN"))
}

async function getStudioItems() {
  const alist = {
    title: "Alist Resource Library",
    type: "Resource Hub",
    summary: "Browse extended files, media, and long-term resources.",
    url: "https://melyi.uk:8089/alist",
    room: "Studio",
  }

  if (!(await pathExists(studioIndexPath))) return [alist]

  const raw = await fs.readFile(studioIndexPath, "utf8")
  const items = JSON.parse(raw)

  return [
    alist,
    ...items.map((item) => ({
      title: item.title,
      type: item.type || "Download",
      summary: item.description || "A downloadable resource from the studio.",
      url: item.url,
      room: "Studio",
    })),
  ]
}

function card(item) {
  return `<a class="garden-card" href="${escapeHtml(item.url)}">
  <span class="garden-card-kicker">${escapeHtml(item.room)} / ${escapeHtml(item.type)}</span>
  <strong>${escapeHtml(item.title)}</strong>
  <span>${escapeHtml(item.summary)}</span>
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

function nav() {
  return `<nav class="garden-nav" aria-label="Garden sections">
  <a href="/">Home</a>
  <a href="/library/">Library</a>
  <a href="/gallery/">Gallery</a>
  <a href="/studio/">Studio</a>
</nav>`
}

function homePage(notes, gallery, studio) {
  const featured = [...gallery, ...notes, ...studio].slice(0, 6)
  const recent = [...gallery, ...notes].slice(0, 6)

  return pageFrame({
    title: "Rosemary Garden",
    cssClass: "garden-home",
    body: `<section class="garden-hero">
  <div class="garden-hero-copy">
    <p class="garden-eyebrow">Personal Portal / Little Wings</p>
    <h1>Rosemary Garden</h1>
    <p class="garden-subtitle">A Personal Portal for Growing, Making, Learning, and Wondering</p>
    ${nav()}
  </div>
  <figure class="garden-hero-art">
    <picture>
      <img src="/static/garden/cockatiel-hero.png" alt="A dreamy editorial illustration of a cockatiel in Rosemary Garden" loading="eager" decoding="async" onerror="this.onerror=null;this.src='/static/garden/cockatiel-hero.png'" />
    </picture>
  </figure>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">Garden Rooms</p>
    <h2>Four doors for growing work</h2>
  </div>
  <div class="garden-room-grid">
    ${roomCard("Library", "Obsidian notes, reading traces, ideas, and collected thoughts.", "/library/")}
    ${roomCard("Gallery", "Interactive pages, visual works, slides, and growing projects.", "/gallery/")}
    ${roomCard("Studio", "Downloads, resource hubs, and future learning tools.", "/studio/")}
  </div>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">Featured</p>
    <h2>Selected blooms</h2>
  </div>
  <div class="garden-card-grid">${featured.map(card).join("\n")}</div>
</section>

<section class="garden-section">
  <div class="garden-section-head">
    <p class="garden-eyebrow">Recent Blooms</p>
    <h2>Newly opened paths</h2>
  </div>
  <div class="garden-card-grid compact">${recent.map(card).join("\n")}</div>
</section>`,
  })
}

function roomCard(title, summary, url) {
  return `<a class="garden-room" href="${url}">
  <span>${title}</span>
  <p>${summary}</p>
</a>`
}

function listingPage({ title, eyebrow, intro, cssClass, items }) {
  return pageFrame({
    title,
    cssClass,
    body: `<section class="garden-listing-hero">
  <p class="garden-eyebrow">${escapeHtml(eyebrow)}</p>
  <h1>${escapeHtml(title)}</h1>
  <p>${escapeHtml(intro)}</p>
  ${nav()}
</section>

<section class="garden-section">
  <div class="garden-card-grid">${items.map(card).join("\n") || emptyState()}</div>
</section>`,
  })
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
