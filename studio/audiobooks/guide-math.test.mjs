import { test } from "node:test"
import assert from "node:assert/strict"
import { splitGuideMath } from "./guide-math.js"

const formulas = text => splitGuideMath(text).filter(part => part.raw)

test("guide math supports the reported formula and all four delimiters", () => {
  assert.deepEqual(formulas("总人数为 $7.2 + 69.4 = 76.6$ 人"), [
    { text: "7.2 + 69.4 = 76.6", raw: "$7.2 + 69.4 = 76.6$", display: false },
  ])
  const parts = formulas(String.raw`$x^2$ $$\frac{1}{2}$$ \(e^{i\pi}+1=0\) \[\sqrt{-1}\]`)
  assert.deepEqual(parts.map(part => part.display), [false, true, false, true])
})

test("ordinary currency, escaped dollars and incomplete formulas remain intact", () => {
  for (const text of ["Costs $5 and $10.", "$7.2 + $69.4 = $76.6", String.raw`Price \$5 and \$10`, "An unclosed $x", "$$x"]) {
    assert.deepEqual(splitGuideMath(text), [{ text }])
  }
})

test("escaped delimiters and braces inside formulas do not end them early", () => {
  assert.equal(formulas(String.raw`\(\text{a \) b} + x\)`)[0].text, String.raw`\text{a \) b} + x`)
  assert.equal(formulas(String.raw`$\text{\$5} + x$`)[0].text, String.raw`\text{\$5} + x`)
  assert.equal(formulas("$$x\n+ y$$")[0].display, true)
})

test("text around adjacent formulas is preserved", () => {
  const text = "令 $x = 0$ 或 $x \\to \\infty$。"
  assert.equal(splitGuideMath(text).map(part => part.raw || part.text).join(""), text)
  assert.equal(formulas(text).length, 2)
})
