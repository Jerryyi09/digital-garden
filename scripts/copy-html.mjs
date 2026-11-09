import fs from "node:fs/promises"
import path from "node:path"

const projectRoot = path.resolve(import.meta.dirname, "..")
const sourceDir = path.join(projectRoot, "html")
const outputDir = path.join(projectRoot, "public", "html")

async function pathExists(filePath) {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

async function copyDir(source, destination) {
  await fs.mkdir(destination, { recursive: true })
  await fs.chmod(destination, 0o755).catch(() => {})
  const entries = await fs.readdir(source, { withFileTypes: true })

  for (const entry of entries) {
    if (entry.name === ".DS_Store") continue
    if (entry.name === "README.md") continue
    if (entry.name.endsWith(".test.mjs")) continue

    const sourcePath = path.join(source, entry.name)
    const destinationPath = path.join(destination, entry.name)

    if (entry.isDirectory()) {
      await copyDir(sourcePath, destinationPath)
    } else if (entry.isFile()) {
      await fs.copyFile(sourcePath, destinationPath)
      await fs.chmod(destinationPath, 0o644).catch(() => {})

      // For standalone *.html (excluding index.html), also generate a mirror directory with index.html
      // This ensures 100% clean-URL compatibility across Nginx, Cloudflare Pages, and SPA routers
      if (entry.name.endsWith(".html") && entry.name !== "index.html") {
        const baseName = entry.name.slice(0, -5)
        const mirrorDir = path.join(destination, baseName)
        await fs.mkdir(mirrorDir, { recursive: true })
        await fs.chmod(mirrorDir, 0o755).catch(() => {})
        const mirrorIndex = path.join(mirrorDir, "index.html")
        await fs.copyFile(sourcePath, mirrorIndex)
        await fs.chmod(mirrorIndex, 0o644).catch(() => {})
      }
    }
  }
}

if (await pathExists(sourceDir)) {
  await copyDir(sourceDir, outputDir)
  console.log(`Copied standalone HTML from ${sourceDir} to ${outputDir}`)
} else {
  console.log("No standalone HTML directory found; skipped.")
}

// Keep the PWA outside Quartz routing and scope its service worker to this app.
await copyDir(
  path.join(projectRoot, "studio", "audiobooks"),
  path.join(projectRoot, "public", "studio", "audiobooks"),
)
