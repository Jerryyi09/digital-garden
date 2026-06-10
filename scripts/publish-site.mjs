import { spawnSync } from "node:child_process"
import process from "node:process"

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: false,
    ...options,
  })

  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}

function output(command, args) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    shell: false,
  })

  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }

  return result.stdout.trim()
}

function hasStagedChanges() {
  const result = spawnSync("git", ["diff", "--cached", "--quiet"], {
    stdio: "ignore",
    shell: false,
  })

  return result.status === 1
}

const message =
  process.argv.slice(2).join(" ").trim() ||
  `Publish site content ${new Date().toISOString().slice(0, 10)}`

console.log("Syncing published Obsidian notes...")
run("npm", ["run", "publish-notes"])

console.log("Building Quartz site and standalone HTML...")
run("npm", ["run", "build"])

console.log("Preparing changed content for Git...")
run("git", ["add", "content", "html"])

const status = output("git", ["status", "--short"])

if (!hasStagedChanges()) {
  console.log("No published content changes found. Nothing to push.")
  process.exit(0)
}

console.log(status)
run("git", ["commit", "-m", message])

console.log("Pushing to GitHub. Cloudflare will deploy after the push.")
run("git", ["push"])
