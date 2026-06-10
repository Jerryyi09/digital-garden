import fs from "node:fs/promises"
import path from "node:path"

const projectRoot = path.resolve(import.meta.dirname, "..")
const contentIndexPath = path.join(projectRoot, "content", "index.md")
const htmlDir = path.join(projectRoot, "html")
const sectionStart = "<!-- standalone-html:start -->"
const sectionEnd = "<!-- standalone-html:end -->"

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
    if (entry.name === ".DS_Store") continue

    const fullPath = path.join(dir, entry.name)

    if (entry.isDirectory()) {
      await walk(fullPath, files)
    } else if (entry.isFile()) {
      files.push(fullPath)
    }
  }

  return files
}

function titleFromHtml(html, filePath) {
  const match = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)
  const title = match?.[1]
    ?.replace(/\s+/g, " ")
    .replace(/&nbsp;/g, " ")
    .trim()

  return title || path.basename(filePath, path.extname(filePath))
}

function publicUrl(relativePath) {
  const normalized = relativePath.split(path.sep).join("/")

  if (normalized.endsWith("/index.html")) {
    return `/html/${normalized.replace(/\/index\.html$/, "/")}`
  }

  return `/html/${normalized}`
}

async function getHtmlPages() {
  if (!(await pathExists(htmlDir))) return []

  const files = await walk(htmlDir)
  const htmlFiles = files.filter((file) => file.toLowerCase().endsWith(".html"))
  const pages = []

  for (const file of htmlFiles) {
    const html = await fs.readFile(file, "utf8")
    const relativePath = path.relative(htmlDir, file)
    pages.push({
      title: titleFromHtml(html, file),
      url: publicUrl(relativePath),
    })
  }

  return pages.sort((a, b) => a.title.localeCompare(b.title, "zh-CN"))
}

function replaceSection(markdown, section) {
  const pattern = new RegExp(`\\n*${sectionStart}[\\s\\S]*?${sectionEnd}\\n*`, "m")

  if (pattern.test(markdown)) {
    return markdown.replace(pattern, section ? `\n\n${section}\n` : "\n")
  }

  return section ? `${markdown.trimEnd()}\n\n${section}\n` : markdown
}

async function main() {
  if (!(await pathExists(contentIndexPath))) {
    throw new Error(`Homepage not found: ${contentIndexPath}`)
  }

  const pages = await getHtmlPages()
  const markdown = await fs.readFile(contentIndexPath, "utf8")
  const section =
    pages.length === 0
      ? ""
      : `${sectionStart}\n## 独立网页\n\n${pages
          .map((page) => `- [${page.title}](${page.url})`)
          .join("\n")}\n${sectionEnd}`

  await fs.writeFile(contentIndexPath, replaceSection(markdown, section))
  console.log(`Standalone HTML links: ${pages.length}`)
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
