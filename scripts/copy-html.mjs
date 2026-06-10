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
  const entries = await fs.readdir(source, { withFileTypes: true })

  for (const entry of entries) {
    if (entry.name === ".DS_Store") continue

    const sourcePath = path.join(source, entry.name)
    const destinationPath = path.join(destination, entry.name)

    if (entry.isDirectory()) {
      await copyDir(sourcePath, destinationPath)
    } else if (entry.isFile()) {
      await fs.copyFile(sourcePath, destinationPath)
    }
  }
}

if (await pathExists(sourceDir)) {
  await copyDir(sourceDir, outputDir)
  console.log(`Copied standalone HTML from ${sourceDir} to ${outputDir}`)
} else {
  console.log("No standalone HTML directory found; skipped.")
}
