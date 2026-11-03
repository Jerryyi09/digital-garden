const DELIMITERS = [
  ["$$", "$$", true], ["\\[", "\\]", true],
  ["\\(", "\\)", false], ["$", "$", false],
]
const IGNORED = "script,style,pre,code,textarea,noscript,math,mjx-container,.katex,.MathJax,[data-no-math]"

// Match balanced TeX delimiters; single dollars follow currency-safe boundaries.
export function splitGuideMath(text) {
  const parts = []
  let plainStart = 0
  for (let i = 0; i < text.length; i++) {
    const delimiter = DELIMITERS.find(([left]) => text.startsWith(left, i))
    if (!delimiter) {
      if (text[i] === "\\") i++
      continue
    }
    const [left, right, display] = delimiter
    const start = i + left.length
    if (left === "$" && (!text[start] || /\s/.test(text[start]))) continue
    let braces = 0
    let end = start
    for (; end < text.length; end++) {
      if (braces <= 0 && text.startsWith(right, end)) break
      if (text[end] === "\\") end++
      else if (text[end] === "{") braces++
      else if (text[end] === "}") braces--
    }
    const invalidCurrency = left === "$" && (
      /\s/.test(text[end - 1] || " ") || /[0-9]/.test(text[end + 1] || "") ||
      text.slice(start, end).includes("\n")
    )
    if (end >= text.length || end === start || invalidCurrency) {
      i += left.length - 1
      continue
    }
    if (i > plainStart) parts.push({ text: text.slice(plainStart, i) })
    parts.push({ text: text.slice(start, end), raw: text.slice(i, end + right.length), display })
    i = end + right.length - 1
    plainStart = i + 1
  }
  if (plainStart < text.length) parts.push({ text: text.slice(plainStart) })
  return parts
}

export async function renderGuideMath(doc) {
  if (!doc?.body) return 0
  const walker = doc.createTreeWalker(doc.body, 4)
  const candidates = []
  while (walker.nextNode()) {
    const node = walker.currentNode
    if (node.parentElement?.closest(IGNORED)) continue
    const parts = splitGuideMath(node.data)
    if (parts.some(part => part.raw)) candidates.push({ node, parts })
  }
  if (!candidates.length) return 0
  const { default: katex } = await import("./vendor/katex/katex.js")
  if (!doc.querySelector("link[data-guide-math]")) {
    const css = doc.createElement("link")
    css.rel = "stylesheet"
    css.href = new URL("./vendor/katex/katex.min.css", import.meta.url).href
    css.dataset.guideMath = ""
    doc.head.append(css)
    const style = doc.createElement("style")
    style.textContent = ".katex-display { overflow-x: auto; overflow-y: hidden; padding: .2em 0; }"
    doc.head.append(style)
  }
  let rendered = 0
  for (const { node, parts } of candidates) {
    if (!node.isConnected) continue
    const fragment = doc.createDocumentFragment()
    for (const part of parts) {
      if (!part.raw) {
        fragment.append(doc.createTextNode(part.text))
        continue
      }
      const span = doc.createElement("span")
      try {
        katex.render(part.text, span, {
          displayMode: part.display, throwOnError: true, trust: false,
          strict: "ignore", maxExpand: 1000, maxSize: 20,
        })
        fragment.append(span)
        rendered++
      } catch {
        // Preserve unsupported formulas verbatim instead of breaking the guide.
        fragment.append(doc.createTextNode(part.raw))
      }
    }
    node.replaceWith(fragment)
  }
  return rendered
}
