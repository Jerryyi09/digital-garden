import fs from "node:fs/promises"
import path from "node:path"
import process from "node:process"

const projectRoot = path.resolve(import.meta.dirname, "..")
const contentDir = path.join(projectRoot, "content")
const backupRoot = path.join(projectRoot, ".publish-backups")
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

const binaryExtensions = new Set([
  ".avif",
  ".gif",
  ".jpeg",
  ".jpg",
  ".mp3",
  ".mp4",
  ".pdf",
  ".png",
  ".svg",
  ".webp",
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

function hasPublishTrue(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---/)
  if (!match) return false
  return /^publish:\s*true\s*$/im.test(match[1])
}

function titleFromFile(filePath) {
  return path.basename(filePath, path.extname(filePath))
}

function createIndex(publishedNotes) {
  const rows = publishedNotes
    .sort((a, b) => a.title.localeCompare(b.title, "zh-CN"))
    .map((note) => `- [[${note.link}|${note.title}]]`)
    .join("\n")

  return `---\ntitle: Jerry 的数字花园\ntags:\n  - home\n---\n\n这里自动收录 Obsidian 中标记为 \`publish: true\` 的公开笔记。\n\n## 公开笔记\n\n${rows || "还没有找到带 `publish: true` 的笔记。"}\n`
}

function findObsidianEmbeds(markdown) {
  const matches = [...markdown.matchAll(/!\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]/g)]
  return matches.map((match) => match[1].trim())
}

async function buildAssetIndex(files) {
  const index = new Map()

  for (const file of files) {
    const ext = path.extname(file).toLowerCase()
    if (!binaryExtensions.has(ext)) continue
    const name = path.basename(file)
    if (!index.has(name)) index.set(name, [])
    index.get(name).push(file)
  }

  return index
}

async function backupExistingContent() {
  if (!(await pathExists(contentDir))) return

  const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
  await fs.mkdir(backupRoot, { recursive: true })
  await fs.rename(contentDir, path.join(backupRoot, `content-${timestamp}`))
}

async function main() {
  if (!(await pathExists(vaultPath))) {
    throw new Error(`Vault path does not exist: ${vaultPath}`)
  }

  const files = await walk(vaultPath)
  const markdownFiles = files.filter((file) => file.endsWith(".md"))
  const assetIndex = await buildAssetIndex(files)
  const publishedNotes = []

  await backupExistingContent()
  await fs.mkdir(contentDir, { recursive: true })

  for (const file of markdownFiles) {
    const markdown = await fs.readFile(file, "utf8")
    if (!hasPublishTrue(markdown)) continue

    const relativePath = path.relative(vaultPath, file)
    const outputPath = path.join(contentDir, relativePath)
    await fs.mkdir(path.dirname(outputPath), { recursive: true })
    await fs.writeFile(outputPath, markdown)

    const link = relativePath.replace(/\.md$/, "")
    publishedNotes.push({ title: titleFromFile(file), link })

    for (const embed of findObsidianEmbeds(markdown)) {
      const matches = assetIndex.get(path.basename(embed)) ?? []
      if (matches.length === 0) continue
      const assetOutput = path.join(contentDir, "attachments", path.basename(embed))
      await fs.mkdir(path.dirname(assetOutput), { recursive: true })
      await fs.copyFile(matches[0], assetOutput)
    }
  }

  await fs.writeFile(path.join(contentDir, "index.md"), createIndex(publishedNotes))

  console.log(`Vault: ${vaultPath}`)
  console.log(`Published notes: ${publishedNotes.length}`)
  console.log(`Content output: ${contentDir}`)
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
