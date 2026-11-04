import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import vm from "node:vm"
import { transformSync } from "esbuild"

test("garden filtering preserves row order without moving DOM nodes on each keystroke", () => {
  const source = fs.readFileSync(new URL("./garden.inline.ts", import.meta.url), "utf8")
  const body = source.slice(source.indexOf("function setupListing()"), source.indexOf("// Note pages"))
  const row = (title: string, updated: number) => ({ dataset: { title, updated, search: title }, hidden: false })
  const rows = [row("Apple", 1), row("Banana", 2)]
  let moves = 0
  const list = { querySelectorAll: () => rows, append: (...items: typeof rows) => { moves++; rows.splice(0, rows.length, ...items) } }
  const folder = { querySelector: () => list, hidden: false, open: false }
  const directory = { querySelectorAll: () => [folder] }
  const input = { value: "", addEventListener: (_event: string, fn: () => void) => { input.update = fn }, update: () => {} }
  const buttons = ["updated", "title"].map(sort => ({ dataset: { sort }, setAttribute() {},
    addEventListener(_event: string, fn: (event: unknown) => void) { this.click = () => fn({ currentTarget: this }) }, click: () => {} }))
  const count = { textContent: "" }
  const empty = { hidden: false }
  const nodes = new Map([["[data-garden-directory]", directory], ["[data-garden-search]", input],
    ["[data-garden-count]", count], ["[data-garden-empty]", empty]] as [string, unknown][])
  const context = vm.createContext({ window: {}, document: { querySelector: (key: string) => nodes.get(key), querySelectorAll: () => buttons } })
  vm.runInContext(transformSync(body, { loader: "ts" }).code + "\nsetupListing()", context)
  assert.equal(rows[0].dataset.title, "Banana")
  assert.equal(moves, 1)
  input.value = "Apple"; input.update()
  assert.equal(count.textContent, "1 项")
  assert.equal(moves, 1)
  buttons[1].click()
  assert.equal(rows[0].dataset.title, "Apple")
  assert.equal(moves, 2)
  input.value = "missing"; input.update()
  assert.equal(empty.hidden, false)
  assert.equal(moves, 2)
  input.value = ""; input.update()
  assert.equal(count.textContent, "2 项")
})
