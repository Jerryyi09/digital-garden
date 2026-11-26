import test from "node:test"
import assert from "node:assert/strict"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { copyHtmlDir } from "./copy-html.mjs"

test("copyHtmlDir mirrors slugified directories while keeping asset filenames intact", async () => {
  const root = mkdtempSync(join(tmpdir(), "garden-copy-html-test-"))
  try {
    const src = join(root, "html")
    const dst = join(root, "public-html")

    // Case 1: folder/index.html + flat redirect + assets with spaces/uppercase
    const workDir = join(src, "计算机 AI", "AI 工程认知")
    mkdirSync(join(workDir, "assets"), { recursive: true })
    writeFileSync(join(workDir, "index.html"), "<html><body>real page</body></html>")
    writeFileSync(join(workDir, "assets", "Pasted image 1.png"), "png-bytes")
    writeFileSync(join(src, "计算机 AI", "AI 工程认知.html"), "<html>redirect</html>")

    // Case 2: standalone *.html without counterpart index.html
    mkdirSync(join(src, "英语", "Writing"), { recursive: true })
    writeFileSync(join(src, "英语", "Writing", "My Essay.html"), "<html>essay</html>")

    await copyHtmlDir(src, dst)

    // Raw paths exist
    assert.equal(existsSync(join(dst, "计算机 AI", "AI 工程认知", "index.html")), true)
    assert.equal(
      readFileSync(join(dst, "计算机 AI", "AI 工程认知", "index.html"), "utf8"),
      "<html><body>real page</body></html>",
    )
    assert.equal(
      existsSync(join(dst, "计算机 AI", "AI 工程认知", "assets", "Pasted image 1.png")),
      true,
    )

    // Slugified paths exist (matching @quartz-community/crawl-links output)
    assert.equal(
      readFileSync(join(dst, "计算机-ai", "ai-工程认知", "index.html"), "utf8"),
      "<html><body>real page</body></html>",
    )
    assert.equal(
      existsSync(join(dst, "计算机-ai", "ai-工程认知", "assets", "Pasted image 1.png")),
      true,
    )

    // Standalone *.html mirrored to both slugified .html and slugified dir/index.html
    assert.equal(
      readFileSync(join(dst, "英语", "writing", "my-essay.html"), "utf8"),
      "<html>essay</html>",
    )
    assert.equal(
      readFileSync(join(dst, "英语", "writing", "my-essay", "index.html"), "utf8"),
      "<html>essay</html>",
    )
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})
