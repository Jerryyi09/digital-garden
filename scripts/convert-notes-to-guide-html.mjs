import fs from "node:fs/promises"
import path from "node:path"
import process from "node:process"
import { marked } from "marked"

// Configure marked
marked.setOptions({
  gfm: true,
  breaks: false,
})

const projectRoot = path.resolve(import.meta.dirname, "..")
const htmlDir = path.join(projectRoot, "html")
const vaultPath =
  process.env.VAULT_PATH ??
  "/Users/jerryyi/Library/Mobile Documents/iCloud~md~obsidian/Documents"

const ignoredDirs = new Set([
  ".git",
  ".obsidian",
  ".trash",
  ".Trash",
  "node_modules",
  ".publish-backups",
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
  const entries = await fs.readdir(dir, { withFileTypes: true })
  for (const entry of entries) {
    if (ignoredDirs.has(entry.name)) continue
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      await walk(fullPath, files)
    } else {
      files.push(fullPath)
    }
  }
  return files
}

function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!match) return { frontmatter: {}, body: markdown }

  const raw = match[1]
  const body = markdown.slice(match[0].length).trim()
  const frontmatter = {}

  let currentKey = null
  for (const line of raw.split("\n")) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith("#")) continue

    if (trimmed.startsWith("- ") && currentKey) {
      if (!Array.isArray(frontmatter[currentKey])) {
        frontmatter[currentKey] = []
      }
      frontmatter[currentKey].push(trimmed.slice(2).trim())
      continue
    }

    const pair = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/)
    if (pair) {
      const key = pair[1]
      let value = pair[2].trim()
      currentKey = key
      if (value.startsWith("[") && value.endsWith("]")) {
        frontmatter[key] = value
          .slice(1, -1)
          .split(",")
          .map((v) => v.trim().replace(/^["']|["']$/g, ""))
      } else if (value.toLowerCase() === "true") {
        frontmatter[key] = true
      } else if (value.toLowerCase() === "false") {
        frontmatter[key] = false
      } else if (value) {
        frontmatter[key] = value.replace(/^["']|["']$/g, "")
      } else {
        frontmatter[key] = []
      }
    }
  }

  return { frontmatter, body }
}

function escapeHtml(text = "") {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
}

// Enhance markdown html output with custom classes and badges
function postProcessHtml(rawHtml) {
  let html = rawHtml

  // Wrap tables with mobile-friendly class
  html = html.replace(/<table>/g, '<table class="term-table">')

  // Badges replacement for text markers
  html = html.replace(
    /【文本依据】/g,
    '<span class="badge-evidence">【文本依据】</span>',
  )
  html = html.replace(
    /【文学背景】/g,
    '<span class="badge-context">【文学背景】</span>',
  )
  html = html.replace(
    /【延伸评论】/g,
    '<span class="badge-comment">【延伸评论】</span>',
  )

  // Style h3 headings with elegant indicator
  html = html.replace(
    /<h3>([\s\S]*?)<\/h3>/g,
    '<div class="sub-heading">$1</div>',
  )

  // Enhance blockquotes with tint style if they start with key markers
  html = html.replace(
    /<blockquote>([\s\S]*?)<\/blockquote>/g,
    (match, inner) => {
      if (inner.includes("❌ 平庸") || inner.includes("平庸改写")) {
        return `<div class="tint-bad">${inner}</div>`
      }
      if (inner.includes("✅ 原文") || inner.includes("原文胜出")) {
        return `<div class="tint-good">${inner}</div>`
      }
      if (inner.includes("🔍 文本显微镜") || inner.includes("文本显微镜")) {
        return `<div class="tint-accent">${inner}</div>`
      }
      if (inner.includes("🩺 语言听诊器") || inner.includes("语言听诊器")) {
        return `<div class="tint-warm">${inner}</div>`
      }
      return `<div class="tint-box">${inner}</div>`
    },
  )

  return html
}

// Split markdown body into structured parts and sections
function parseSections(body) {
  const lines = body.split("\n")
  let preambleLines = []
  let parts = []
  let currentPart = null
  let currentSection = null

  // Determine heading structure
  const hasH1 = lines.some((l) => /^#\s+[^#]/.test(l))
  const hasH2 = lines.some((l) => /^##\s+[^#]/.test(l))

  const isPartHeading = (l) => hasH1 && /^#\s+[^#]/.test(l)
  const isSectionHeading = (l) => {
    if (hasH2) return /^##\s+[^#]/.test(l)
    if (hasH1) return /^#\s+[^#]/.test(l)
    return false
  }

  let inSections = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (isPartHeading(line)) {
      inSections = true
      currentPart = {
        title: line.replace(/^#\s+/, "").trim(),
        sections: [],
      }
      parts.push(currentPart)
      currentSection = null
      continue
    }

    if (isSectionHeading(line)) {
      inSections = true
      const sectionTitle = line.replace(/^#{1,2}\s+/, "").trim()
      currentSection = {
        title: sectionTitle,
        contentLines: [],
      }
      if (!currentPart) {
        currentPart = { title: null, sections: [] }
        parts.push(currentPart)
      }
      currentPart.sections.push(currentSection)
      continue
    }

    if (!inSections) {
      preambleLines.push(line)
    } else if (currentSection) {
      currentSection.contentLines.push(line)
    } else if (currentPart) {
      // Content directly under a part heading before any section heading
      if (!currentPart.preambleLines) currentPart.preambleLines = []
      currentPart.preambleLines.push(line)
    }
  }

  // If no sections were detected, put everything in a single section
  if (parts.length === 0) {
    parts.push({
      title: null,
      sections: [
        {
          title: "全篇导读",
          contentLines: lines,
        },
      ],
    })
    preambleLines = []
  }

  return { preamble: preambleLines.join("\n").trim(), parts }
}

const colorThemes = [
  "color-navy",
  "color-amber",
  "color-bamboo",
  "color-purple",
  "color-rose",
  "color-cyan",
]

function renderToAccordionHtml(markdown, filePath) {
  const { frontmatter, body } = parseFrontmatter(markdown)
  const title =
    frontmatter.title || path.basename(filePath, path.extname(filePath))
  const author = frontmatter.author || ""
  const date = frontmatter.date || ""
  const category = frontmatter.category || ""
  const tags = Array.isArray(frontmatter.tags)
    ? frontmatter.tags
    : frontmatter.tags
      ? [frontmatter.tags]
      : []

  const { preamble, parts } = parseSections(body)

  // Extract hero quote if preamble starts with blockquote
  let heroQuoteHtml = ""
  let restPreambleHtml = ""
  if (preamble) {
    if (preamble.startsWith(">")) {
      const quoteMatch = preamble.match(/^((?:>.*\n?)+)/)
      if (quoteMatch) {
        const quoteText = quoteMatch[1]
          .split("\n")
          .map((l) => l.replace(/^>\s?/, ""))
          .join("\n")
        heroQuoteHtml = marked.parse(quoteText)
        const rest = preamble.slice(quoteMatch[0].length).trim()
        if (rest) restPreambleHtml = postProcessHtml(marked.parse(rest))
      } else {
        heroQuoteHtml = marked.parse(preamble)
      }
    } else {
      restPreambleHtml = postProcessHtml(marked.parse(preamble))
    }
  }

  // Count total sections for toolbar labeling
  let totalSections = 0
  for (const p of parts) totalSections += p.sections.length

  // Build section HTML
  let sectionIndex = 1
  let bodyHtml = ""

  if (restPreambleHtml) {
    bodyHtml += `<div class="hero-preamble item-block">${restPreambleHtml}</div>`
  }

  for (let pIdx = 0; pIdx < parts.length; pIdx++) {
    const part = parts[pIdx]
    if (part.title) {
      bodyHtml += `
      <div class="part-divider" id="part-${pIdx + 1}">
        <span>${escapeHtml(part.title)}</span>
      </div>`
    }
    if (part.preambleLines?.length) {
      const partPreHtml = postProcessHtml(
        marked.parse(part.preambleLines.join("\n")),
      )
      bodyHtml += `<div class="part-preamble item-block">${partPreHtml}</div>`
    }

    for (const section of part.sections) {
      const numStr = String(sectionIndex).padStart(2, "0")
      const colorClass = colorThemes[(sectionIndex - 1) % colorThemes.length]
      const secId = `sec-${numStr}`
      // Open first two sections by default for immediate preview
      const isOpen = sectionIndex <= 2 ? " open" : ""
      const secContentHtml = postProcessHtml(
        marked.parse(section.contentLines.join("\n")),
      )

      bodyHtml += `
      <details class="guide-section" id="${secId}"${isOpen}>
        <summary class="section-summary">
          <div class="sum-left">
            <span class="sec-num ${colorClass}">${numStr}</span>
            <span class="sec-title">${escapeHtml(section.title)}</span>
          </div>
          <span class="sum-icon">＋</span>
        </summary>
        <div class="section-content">
          ${secContentHtml}
        </div>
      </details>`

      sectionIndex++
    }
  }

  // Badges list
  const badges = []
  if (category) badges.push(`<span class="badge">${escapeHtml(category)}</span>`)
  for (const tag of tags) {
    badges.push(`<span class="badge badge-warm">${escapeHtml(tag)}</span>`)
  }

  // Subtitle
  const subParts = []
  if (author) subParts.push(author)
  if (date) subParts.push(date)
  if (category) subParts.push(category)
  const heroSub = subParts.length ? subParts.join(" · ") : "Rosemary Garden 精读导读"

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
  <title>${escapeHtml(title)}</title>
  <!-- KaTeX for math formulas -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
  <style>
    :root {
      --bg-page: #fbf9f4;
      --bg-card: #ffffff;
      --bg-subtle: #f4efe6;
      --bg-accent: rgba(23, 93, 126, 0.08);
      --bg-warm: rgba(192, 86, 33, 0.08);
      --bg-danger: rgba(185, 28, 28, 0.06);
      --bg-success: rgba(21, 128, 61, 0.07);
      --text-main: #1c2429;
      --text-muted: #52606d;
      --text-soft: #7b8794;
      --primary: #175d7e;
      --secondary: #c05621;
      --success: #15803d;
      --danger: #b91c1c;
      --border: rgba(28, 36, 41, 0.09);
      --radius: 10px;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg-page: #12161a;
        --bg-card: #1b2127;
        --bg-subtle: #232b33;
        --bg-accent: rgba(56, 189, 248, 0.12);
        --bg-warm: rgba(251, 146, 60, 0.12);
        --bg-danger: rgba(248, 113, 113, 0.12);
        --bg-success: rgba(74, 222, 128, 0.12);
        --text-main: #e2e8f0;
        --text-muted: #94a3b8;
        --text-soft: #64748b;
        --primary: #38bdf8;
        --secondary: #fb923c;
        --success: #4ade80;
        --danger: #f87171;
        --border: rgba(255, 255, 255, 0.09);
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
    body {
      background: var(--bg-page);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      font-size: 15.5px;
      line-height: 1.78;
      padding: 8px 8px 72px;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    @media (min-width: 640px) {
      body { padding: 20px 16px 88px; font-size: 16px; }
    }
    .container { max-width: 740px; margin: 0 auto; }
    p, li { text-align: justify; margin-bottom: 0.55em; }
    p:last-child, li:last-child { margin-bottom: 0; }

    /* 顶部 Hero 卡片 */
    .hero {
      background: var(--bg-card);
      border-radius: var(--radius);
      border-top: 3.5px solid var(--primary);
      padding: 18px 14px 16px;
      margin-bottom: 10px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .hero-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .badge {
      font-size: 11.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      background: var(--bg-accent);
      color: var(--primary);
    }
    .badge-warm { background: var(--bg-warm); color: var(--secondary); }
    .hero h1 {
      font-size: 22px;
      font-weight: 800;
      line-height: 1.35;
      margin-bottom: 4px;
      color: var(--text-main);
    }
    .hero-sub { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
    .hero-quote {
      background: var(--bg-subtle);
      border-left: 3.5px solid var(--secondary);
      padding: 10px 12px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      line-height: 1.68;
      color: var(--text-main);
    }
    .hero-quote p { margin-bottom: 0.4em; }
    .hero-quote p:last-child { margin-bottom: 0; }

    /* 置顶工具栏 */
    .toolbar {
      position: sticky;
      top: 6px;
      z-index: 30;
      display: grid;
      grid-template-columns: 1.1fr 1.2fr 1fr 0.8fr;
      gap: 5px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      padding: 6px;
      border-radius: 8px;
      margin-bottom: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .t-btn {
      background: var(--bg-subtle);
      border: none;
      color: var(--text-main);
      font-size: 12px;
      font-weight: 600;
      padding: 7px 3px;
      border-radius: 5px;
      cursor: pointer;
      white-space: nowrap;
      text-align: center;
      transition: background 0.15s, opacity 0.15s;
    }
    .t-btn:hover { opacity: 0.85; }
    .t-btn.btn-back { background: var(--bg-accent); color: var(--primary); font-weight: 700; }
    .t-btn.btn-open { background: var(--bg-subtle); color: var(--text-main); }
    .t-btn.btn-close { background: var(--bg-subtle); color: var(--text-muted); }

    /* PWA 全屏模式右下角浮动返回按钮 */
    .fab-back {
      position: fixed;
      right: 14px;
      bottom: 22px;
      z-index: 99;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 14px rgba(0,0,0,0.12);
      cursor: pointer;
      opacity: 0.9;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      transition: transform 0.18s, opacity 0.18s;
    }
    .fab-back:hover, .fab-back:active {
      transform: scale(1.08);
      opacity: 1;
      background: var(--bg-accent);
    }
    .fab-back svg { width: 20px; height: 20px; }

    /* 公式排版防溢出 */
    .katex-display {
      overflow-x: auto;
      overflow-y: hidden;
      padding: 6px 0;
      margin: 8px 0;
      -webkit-overflow-scrolling: touch;
    }

    .part-divider {
      font-size: 13px;
      font-weight: 800;
      color: var(--primary);
      letter-spacing: 0.05em;
      margin: 20px 2px 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .part-divider::after { content: ""; flex: 1; height: 1px; background: var(--border); }

    /* 手风琴栏目 */
    details.guide-section {
      background: var(--bg-card);
      border-radius: var(--radius);
      margin-bottom: 10px;
      overflow: hidden;
      border: 1px solid var(--border);
      transition: box-shadow 0.18s ease;
    }
    details.guide-section[open] {
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    summary.section-summary {
      list-style: none;
      cursor: pointer;
      padding: 13px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-weight: 700;
      font-size: 15.5px;
      user-select: none;
      background: var(--bg-card);
    }
    summary.section-summary::-webkit-details-marker { display: none; }
    .sum-left { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
    .sec-num {
      font-size: 11.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 5px;
      flex-shrink: 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .color-navy { background: var(--bg-accent); color: var(--primary); }
    .color-amber { background: var(--bg-warm); color: var(--secondary); }
    .color-bamboo { background: var(--bg-success); color: var(--success); }
    .color-purple { background: rgba(147, 51, 234, 0.1); color: #9333ea; }
    .color-rose { background: var(--bg-danger); color: var(--danger); }
    .color-cyan { background: rgba(6, 182, 212, 0.1); color: #0891b2; }

    .sec-title { font-size: 15.5px; font-weight: 700; line-height: 1.35; color: var(--text-main); }
    .sum-icon { font-size: 16px; color: var(--text-soft); transition: transform 0.2s; flex-shrink: 0; font-weight: 600; }
    details[open] > summary .sum-icon { transform: rotate(45deg); color: var(--primary); }

    .section-content {
      padding: 10px 12px 18px;
      border-top: 1px solid var(--border);
    }
    @media (min-width: 640px) {
      .section-content { padding: 14px 18px 22px; }
    }

    /* 内部小标题与区块 */
    .sub-heading {
      font-size: 14.5px;
      font-weight: 800;
      color: var(--primary);
      margin: 14px 0 6px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .sub-heading::before { content: "▍"; color: var(--secondary); font-size: 12px; }

    .item-block {
      padding: 10px 0;
      border-bottom: 1px dashed var(--border);
    }
    .item-block:last-child { border-bottom: none; }

    /* 纯色块 */
    .tint-box, .tint-accent, .tint-warm, .tint-good, .tint-bad {
      padding: 9px 12px;
      border-radius: 6px;
      margin: 9px 0;
      font-size: 14px;
      line-height: 1.72;
    }
    .tint-box { background: var(--bg-subtle); }
    .tint-accent { background: var(--bg-accent); border-left: 3px solid var(--primary); border-radius: 0 6px 6px 0; }
    .tint-warm { background: var(--bg-warm); border-left: 3px solid var(--secondary); border-radius: 0 6px 6px 0; }
    .tint-good { background: var(--bg-success); border-left: 3px solid var(--success); border-radius: 0 6px 6px 0; }
    .tint-bad { background: var(--bg-danger); border-left: 3px solid var(--danger); border-radius: 0 6px 6px 0; }

    /* 标签 */
    .badge-evidence, .badge-context, .badge-comment {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 0 5px;
      border-radius: 3px;
      margin-right: 3px;
    }
    .badge-evidence { background: var(--bg-accent); color: var(--primary); }
    .badge-context { background: var(--bg-warm); color: var(--secondary); }
    .badge-comment { background: var(--bg-subtle); color: var(--text-muted); }

    /* 表格移动端自适应 */
    table.term-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      margin: 10px 0;
      table-layout: fixed;
    }
    table.term-table th, table.term-table td {
      border: 1px solid var(--border);
      padding: 8px 6px;
      text-align: left;
      vertical-align: top;
      line-height: 1.55;
      word-break: break-word;
    }
    table.term-table th {
      background: var(--bg-subtle);
      font-weight: 700;
      color: var(--primary);
    }

    ul, ol { padding-left: 19px; margin: 6px 0 10px; }
    li { font-size: 14.8px; margin-bottom: 5px; }
    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      background: var(--bg-subtle);
      padding: 1.5px 5px;
      border-radius: 4px;
      color: var(--primary);
    }
    pre {
      background: var(--bg-subtle);
      padding: 10px 12px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 10px 0;
      border: 1px solid var(--border);
    }
    pre code { background: none; padding: 0; color: var(--text-main); }

    footer {
      text-align: center;
      padding: 28px 0 10px;
      font-size: 12px;
      color: var(--text-soft);
    }
    footer a { color: var(--primary); text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <!-- 顶部总览 Hero -->
    <header class="hero">
      ${badges.length ? `<div class="hero-badges">${badges.join("")}</div>` : ""}
      <h1>${escapeHtml(title)}</h1>
      <div class="hero-sub">${escapeHtml(heroSub)}</div>
      ${heroQuoteHtml ? `<div class="hero-quote">${heroQuoteHtml}</div>` : ""}
    </header>

    <!-- 置顶工具栏 -->
    <nav class="toolbar">
      <button class="t-btn btn-back" onclick="navigateBack()">← 作品廊</button>
      <button class="t-btn btn-open" onclick="toggleAllSections(true)">📖 全部展开 (${totalSections})</button>
      <button class="t-btn btn-close" onclick="toggleAllSections(false)">📁 全部收起</button>
      <button class="t-btn" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">⬆ 顶部</button>
    </nav>

    <!-- 手风琴内容区块 -->
    <main>
      ${bodyHtml}
    </main>

    <!-- PWA / 移动端悬浮快捷返回按钮 -->
    <button class="fab-back" onclick="navigateBack()" aria-label="返回作品廊" title="返回作品廊">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
    </button>

    <footer>
      <p>Rosemary Garden · <a href="/gallery/">返回作品廊</a> · <a href="/library/">返回图书馆</a></p>
    </footer>
  </div>

  <script>
    function toggleAllSections(openState) {
      document.querySelectorAll('.guide-section').forEach(d => d.open = openState);
    }

    function navigateBack() {
      if (window.history.length > 1 && document.referrer && !document.referrer.includes(location.pathname)) {
        window.history.back();
      } else {
        window.location.href = '/gallery/';
      }
    }

    // Initialize KaTeX formulas
    document.addEventListener("DOMContentLoaded", function() {
      if (typeof renderMathInElement === "function") {
        renderMathInElement(document.body, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false},
            {left: "\\(", right: "\\)", display: false},
            {left: "\\[", right: "\\]", display: true}
          ],
          throwOnError: false
        });
      }
    });
  </script>
</body>
</html>`
}

async function convertFile(sourceFile, outputHtmlFile) {
  const markdown = await fs.readFile(sourceFile, "utf8")
  const html = renderToAccordionHtml(markdown, sourceFile)
  await fs.mkdir(path.dirname(outputHtmlFile), { recursive: true })
  await fs.writeFile(outputHtmlFile, html, "utf8")
}

async function main() {
  const specificFile = process.argv[2]
  if (specificFile) {
    const fullPath = path.resolve(specificFile)
    const outName = path.basename(fullPath, ".md") + ".html"
    const outPath = path.join(htmlDir, "notes", outName)
    await convertFile(fullPath, outPath)
    console.log(`Converted: ${fullPath} -> ${outPath}`)
    return
  }

  if (!(await pathExists(vaultPath))) {
    console.log(`Vault path does not exist: ${vaultPath}. Skipping conversion (assumed pre-built or remote CI environment).`)
    return
  }

  console.log(`Scanning vault: ${vaultPath}...`)
  const files = await walk(vaultPath)
  const markdownFiles = files.filter((f) => f.endsWith(".md"))

  let convertedCount = 0

  for (const file of markdownFiles) {
    const text = await fs.readFile(file, "utf8")
    const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/)
    if (!match) continue
    if (!/^(?:publish|published):\s*["']?true["']?/im.test(match[1])) continue

    const relative = path.relative(vaultPath, file)
    // Map to html/ path, preserving folder structure (e.g. html/01 Areas/语文/...)
    // or simplified e.g. html/语文/初一课文/《驿路梨花》.html
    const dirParts = path.dirname(relative).split(path.sep)
    // Filter out numbered categories like "01 Areas", "00 Projects" to keep clean URLs
    const cleanDirParts = dirParts.filter(
      (p) => !/^\d+\s*(areas?|projects?|resources?|archives?)$/i.test(p) && p !== "学习笔记",
    )
    const baseName = path.basename(file, ".md")
    // If the last directory part equals the baseName, avoid duplicating directory (e.g. 数学/初中代数核心思维体系/初中代数核心思维体系.html -> 数学/初中代数核心思维体系/)
    if (cleanDirParts.length > 0 && cleanDirParts[cleanDirParts.length - 1] === baseName) {
      cleanDirParts.pop()
    }
    const workDir = path.join(htmlDir, ...cleanDirParts, baseName)
    const indexPath = path.join(workDir, "index.html")
    const flatPath = path.join(htmlDir, ...cleanDirParts, `${baseName}.html`)

    await convertFile(file, indexPath)
    // Also provide a flat alias so direct .html URLs redirect smoothly
    const redirectHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=./${encodeURIComponent(baseName)}/"><script>location.replace('./${encodeURIComponent(baseName)}/');</script></head><body></body></html>`
    await fs.writeFile(flatPath, redirectHtml, "utf8")

    const outputRel = path.join(...cleanDirParts, baseName, "index.html")
    console.log(`[HTML] ${relative} -> html/${outputRel}`)
    convertedCount++
  }

  console.log(`Successfully converted ${convertedCount} published notes to accordion HTML.`)
}

main().catch((err) => {
  console.error("Error converting notes:", err)
  process.exit(1)
})
