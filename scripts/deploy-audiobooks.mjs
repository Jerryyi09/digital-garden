import { spawnSync } from "node:child_process"

const host = "hp@10.0.0.85"
const options = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-p", "2222", "-i", "/Users/jerryyi/.ssh/id_rsa"]
function run(command, args, capture = false) {
  const result = spawnSync(command, args, { stdio: capture ? "pipe" : "inherit", encoding: "utf8" })
  if (result.status !== 0) throw new Error(result.stderr || `${command} exited with ${result.status}`)
  return result.stdout?.trim()
}

// Publish only the requested Studio entry and player; do not overwrite other site content.
run("node", ["--check", "studio/audiobooks/app.js"])
run("npm", ["test"])
run("npm", ["run", "build"])
const stage = run("ssh", [...options, host, "mktemp -d /tmp/garden-audiobooks.XXXXXX"], true)
if (!/^\/tmp\/garden-audiobooks\.[a-zA-Z0-9]+$/.test(stage)) throw new Error("Unexpected staging path")
run("scp", ["-r", "-P", "2222", "-i", "/Users/jerryyi/.ssh/id_rsa",
  "public/studio/audiobooks", "public/studio/index.html", "scripts/deploy-audiobooks-remote.py", `${host}:${stage}/`])
run("ssh", [...options, host, `python3 ${stage}/deploy-audiobooks-remote.py ${stage}`])
