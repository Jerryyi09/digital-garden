import test from "node:test"
import assert from "node:assert/strict"
import { spawnSync } from "node:child_process"
import { mkdtempSync, mkdirSync, writeFileSync, chmodSync, statSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { homeServerRsyncArgs } from "./publish-transfer.mjs"

test("publish transfer makes new and existing static files readable without deleting extras", () => {
  const root = mkdtempSync(join(tmpdir(), "garden-publish-test-"))
  try {
    const source = join(root, "source")
    const target = join(root, "target")
    mkdirSync(source)
    mkdirSync(target)
    mkdirSync(join(source, "private-mode"), { mode: 0o700 })
    mkdirSync(join(target, "private-mode"), { mode: 0o700 })
    writeFileSync(join(source, "page.html"), "page")
    chmodSync(join(source, "page.html"), 0o600)
    writeFileSync(join(target, "page.html"), "old")
    chmodSync(join(target, "page.html"), 0o600)
    writeFileSync(join(target, "extra"), "preserve")
    const args = homeServerRsyncArgs(target)
    args[args.length - 2] = `${source}/`
    const result = spawnSync("rsync", args, { encoding: "utf8" })
    assert.equal(result.status, 0, result.stderr)
    assert.equal(statSync(join(target, "page.html")).mode & 0o777, 0o644)
    assert.equal(statSync(join(target, "private-mode")).mode & 0o777, 0o755)
    assert.equal(statSync(target).mode & 0o777, 0o755)
    assert.equal(statSync(join(target, "extra")).isFile(), true)
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})
