import fs from "node:fs/promises"
import path from "node:path"

const projectRoot = path.resolve(import.meta.dirname, "..")
const pluginsDir = path.join(projectRoot, ".quartz", "plugins")
const indexPath = path.join(pluginsDir, "index.ts")

function parseExports(dtsContent) {
  const exports = []
  const exportMatches = dtsContent.matchAll(/export\s*{\s*([^}]+)\s*}/g)

  for (const match of exportMatches) {
    const names = match[1]
      .split(",")
      .map((name) => name.trim())
      .filter(Boolean)

    for (const name of names) {
      if (name.startsWith("type ")) continue
      const aliasMatch = name.match(/^(\w+)\s+as\s+(\w+)$/)
      exports.push(aliasMatch ? aliasMatch[2] : name)
    }
  }

  return exports
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

async function main() {
  await fs.mkdir(pluginsDir, { recursive: true })

  const entries = await fs.readdir(pluginsDir, { withFileTypes: true })
  const pluginNames = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name)
  const exportCounts = new Map()
  const pluginExports = new Map()

  for (const pluginName of pluginNames) {
    const dtsPath = path.join(pluginsDir, pluginName, "dist", "index.d.ts")
    if (!(await pathExists(dtsPath))) continue

    const dtsContent = await fs.readFile(dtsPath, "utf8")
    const exports = parseExports(dtsContent)
    pluginExports.set(pluginName, exports)

    for (const exportName of exports) {
      exportCounts.set(exportName, (exportCounts.get(exportName) ?? 0) + 1)
    }
  }

  const lines = [
    `import { componentRegistry } from "../../quartz/components/registry"`,
    "",
  ]

  for (const [pluginName, exports] of pluginExports) {
    const uniqueExports = exports.filter((exportName) => exportCounts.get(exportName) === 1)
    if (uniqueExports.length > 0) {
      lines.push(`export { ${uniqueExports.join(", ")} } from "./${pluginName}"`)
    }
  }

  // Head.tsx imports this symbol during the initial esbuild bundle, before plugins
  // can be installed on a fresh checkout.
  if (!exportCounts.has("CustomOgImagesEmitterName")) {
    lines.push(`export const CustomOgImagesEmitterName = "CustomOgImages"`)
  }

  lines.push("")
  lines.push(
    `export const plugins: Record<string, Record<string, (...args: unknown[]) => void>> = {}`,
  )
  lines.push("")
  lines.push(`void componentRegistry`)
  lines.push("")

  await fs.writeFile(indexPath, lines.join("\n"))
  console.log(`Regenerated plugin index: ${indexPath}`)
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
