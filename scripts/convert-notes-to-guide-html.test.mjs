import test from "node:test"
import assert from "node:assert/strict"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { buildAssetIndex, convertFile, renderToAccordionHtmlWithAssets } from "./convert-notes-to-guide-html.mjs"

test("convertFile resolves Obsidian embeds, relative images, and Mermaid diagrams", async () => {
  const root = mkdtempSync(join(tmpdir(), "garden-convert-html-test-"))
  try {
    const vaultDir = join(root, "vault")
    const attachDir = join(vaultDir, "02 Resources", "附件")
    const noteDir = join(vaultDir, "01 Areas", "计算机 AI")
    const localAssetsDir = join(noteDir, "assets")
    mkdirSync(attachDir, { recursive: true })
    mkdirSync(localAssetsDir, { recursive: true })

    writeFileSync(join(attachDir, "Pasted image 20261126162040.png"), "fake-png")
    writeFileSync(join(localAssetsDir, "diagram.svg"), "<svg></svg>")

    const mdPath = join(noteDir, "Test Note.md")
    const markdown = [
      "---",
      "publish: true",
      "---",
      "",
      "# 测试标题",
      "",
      "## 第一节",
      "",
      "嵌入图片：",
      "![[Pasted image 20261126162040.png|480]]",
      "",
      "相对路径图片：",
      "![SVG示意图](assets/diagram.svg)",
      "",
      "代码块里的示例不应被替换：",
      "```markdown",
      "![[Pasted image 20261126162040.png]]",
      "```",
      "",
      "## 第二节",
      "",
      "```mermaid",
      "graph TD",
      '  A["开始"] --> B["结束"]',
      "```",
      "",
    ].join("\n")
    writeFileSync(mdPath, markdown, "utf8")

    const outHtml = join(root, "html", "计算机 AI", "Test Note", "index.html")
    const assetIndex = buildAssetIndex([
      join(attachDir, "Pasted image 20261126162040.png"),
      join(localAssetsDir, "diagram.svg"),
    ])

    await convertFile(mdPath, outHtml, { assetIndex })

    const html = readFileSync(outHtml, "utf8")
    assert.match(html, /<img src="assets\/Pasted%20image%2020261126162040\.png"[^>]*width="480"/)
    assert.match(html, /<img src="assets\/diagram\.svg" alt="SVG示意图"/)
    assert.match(html, /<code class="language-markdown">!\[\[Pasted image 20261126162040\.png\]\]/)
    assert.match(html, /<div class="mermaid-block"><div class="mermaid">graph TD/)
    assert.match(html, /mermaid\.esm\.min\.mjs/)
    assert.match(html, /addEventListener\('toggle'/)

    assert.equal(
      existsSync(join(root, "html", "计算机 AI", "Test Note", "assets", "Pasted image 20261126162040.png")),
      true,
    )
    assert.equal(
      existsSync(join(root, "html", "计算机 AI", "Test Note", "assets", "diagram.svg")),
      true,
    )
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test("renderToAccordionHtmlWithAssets omits Mermaid script when note has no Mermaid blocks", () => {
  const { html } = renderToAccordionHtmlWithAssets("# 标题\n\n## 节\n\n纯文本", "/tmp/plain.md")
  assert.doesNotMatch(html, /mermaid\.esm\.min\.mjs/)
})
