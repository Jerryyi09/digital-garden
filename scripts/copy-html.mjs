import fs from "node:fs/promises"
import path from "node:path"
import process from "node:process"
import { fileURLToPath } from "node:url"
import { slugifyPath } from "@quartz-community/utils"

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

async function copyFileWithMode(sourcePath, destinationPath) {
  await fs.mkdir(path.dirname(destinationPath), { recursive: true })
  await fs.chmod(path.dirname(destinationPath), 0o755).catch(() => {})
  await fs.copyFile(sourcePath, destinationPath)
  await fs.chmod(destinationPath, 0o644).catch(() => {})
}

export async function copyDir(source, destination) {
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
      await copyFileWithMode(sourcePath, destinationPath)
    }
  }
}

function slugifySegments(segments) {
  if (segments.length === 0) return ""
  return slugifyPath(segments.join("/"))
}

/**
 * Copy standalone HTML works from `html/` into `public/html/`.
 * Mirrors any path whose Quartz `slugifyPath` differs from its raw path so that
 * links rewritten by `@quartz-community/crawl-links` (spaces -> `-`, uppercase ->
 * lowercase) resolve cleanly alongside raw URLs, while keeping relative asset
 * filenames inside `assets/` and `images/` subdirectories intact.
 */
export async function copyHtmlDir(source, destination) {
  async function walkAndCopy(currentSource, pageRelSegments = [], assetRelSegments = null) {
    await fs.mkdir(path.join(destination, ...pageRelSegments, ...(assetRelSegments ?? [])), {
      recursive: true,
    })
    await fs
      .chmod(path.join(destination, ...pageRelSegments, ...(assetRelSegments ?? [])), 0o755)
      .catch(() => {})

    const entries = await fs.readdir(currentSource, { withFileTypes: true })
    const entryNames = new Set(entries.map((e) => e.name))

    for (const entry of entries) {
      if (entry.name === ".DS_Store") continue
      if (entry.name === "README.md") continue
      if (entry.name.endsWith(".test.mjs")) continue

      const sourcePath = path.join(currentSource, entry.name)

      if (entry.isDirectory()) {
        const nextAssetSegments =
          assetRelSegments !== null
            ? [...assetRelSegments, entry.name]
            : entry.name === "assets" || entry.name === "images"
              ? [entry.name]
              : null
        const nextPageSegments = nextAssetSegments !== null ? pageRelSegments : [...pageRelSegments, entry.name]
        await walkAndCopy(sourcePath, nextPageSegments, nextAssetSegments)
        continue
      }

      if (!entry.isFile()) continue

      const rawRelParts = [...pageRelSegments, ...(assetRelSegments ?? []), entry.name]
      const rawDest = path.join(destination, ...rawRelParts)
      await copyFileWithMode(sourcePath, rawDest)

      const slugPageRel = slugifySegments(pageRelSegments)
      const isHtmlPage = assetRelSegments === null && entry.name.toLowerCase().endsWith(".html")
      const isStandaloneHtml = isHtmlPage && entry.name.toLowerCase() !== "index.html"
      const baseName = isStandaloneHtml ? entry.name.slice(0, -5) : null
      const hasDirectoryIndex =
        isStandaloneHtml &&
        entryNames.has(baseName) &&
        (await pathExists(path.join(currentSource, baseName, "index.html")))

      if (isStandaloneHtml && !hasDirectoryIndex) {
        const rawMirrorIndex = path.join(destination, ...pageRelSegments, baseName, "index.html")
        await copyFileWithMode(sourcePath, rawMirrorIndex)
      }

      const slugFileName = isHtmlPage
        ? entry.name.toLowerCase() === "index.html"
          ? "index.html"
          : `${slugifyPath(baseName)}.html`
        : entry.name

      const slugRelParts = [
        ...(slugPageRel ? slugPageRel.split("/") : []),
        ...(assetRelSegments ?? []),
        slugFileName,
      ]
      const slugDest = path.join(destination, ...slugRelParts)

      if (slugDest !== rawDest) {
        await copyFileWithMode(sourcePath, slugDest)
      }

      if (isStandaloneHtml && !hasDirectoryIndex) {
        const slugBaseName = slugifyPath(baseName)
        const slugMirrorIndex = path.join(
          destination,
          ...(slugPageRel ? slugPageRel.split("/") : []),
          slugBaseName,
          "index.html",
        )
        const rawMirrorIndex = path.join(destination, ...pageRelSegments, baseName, "index.html")
        if (slugMirrorIndex !== rawMirrorIndex) {
          await copyFileWithMode(sourcePath, slugMirrorIndex)
        }
      }
    }
  }

  await walkAndCopy(source)
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (await pathExists(sourceDir)) {
    await copyHtmlDir(sourceDir, outputDir)
    console.log(`Copied standalone HTML from ${sourceDir} to ${outputDir}`)
  } else {
    console.log("No standalone HTML directory found; skipped.")
  }

  // Keep the PWA outside Quartz routing and scope its service worker to this app.
  const audiobooksSource = path.join(projectRoot, "studio", "audiobooks")
  if (await pathExists(audiobooksSource)) {
    await copyDir(audiobooksSource, path.join(projectRoot, "public", "studio", "audiobooks"))
  }
}
