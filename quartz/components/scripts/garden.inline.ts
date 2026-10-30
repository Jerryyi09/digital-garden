// Rosemary Garden: reading history, list search/sort and the mobile tab bar.
// Bundled as a global afterDOMLoaded script, so it also works after SPA navigation
// (inline <script> tags inside page content are not re-executed by the router).

const RECENT_KEY = "rosemary-garden-recent-v1"
const GARDEN_SLUGS = new Set(["index", "library/index", "gallery/index", "studio/index"])

type RecentItem = { title: string; url: string; room?: string; at: number }

function readRecent(): RecentItem[] {
  try {
    const items = JSON.parse(localStorage.getItem(RECENT_KEY) || "[]")
    return Array.isArray(items) ? items.filter((item) => item && item.url && item.title) : []
  } catch {
    return []
  }
}

function remember(item: Omit<RecentItem, "at">) {
  try {
    const url = new URL(item.url, location.href)
    url.hash = ""
    const href = url.href
    const items = readRecent().filter((entry) => entry.url !== href)
    items.unshift({ ...item, url: href, at: Date.now() })
    localStorage.setItem(RECENT_KEY, JSON.stringify(items.slice(0, 24)))
  } catch {
    // Storage may be unavailable (private mode); history is a convenience only.
  }
}

// Clicks on standalone gallery pages and external tools never reach a Quartz page,
// so record them at click time.
document.addEventListener("click", (event) => {
  const link = (event.target as Element | null)?.closest?.(
    "a[data-garden-item]",
  ) as HTMLAnchorElement | null
  if (!link?.dataset.title) return
  remember({ title: link.dataset.title, url: link.href, room: link.dataset.room })
})

function renderRecent() {
  const section = document.querySelector<HTMLElement>("[data-recent-section]")
  const list = section?.querySelector<HTMLElement>("[data-recent-list]")
  if (!section || !list) return

  const items = readRecent().slice(0, 4)
  list.replaceChildren()
  for (const item of items) {
    const link = document.createElement("a")
    link.className = "g-row"
    link.href = item.url
    if (!item.url.startsWith(location.origin) || item.url.includes("/html/")) {
      link.dataset.routerIgnore = ""
    }
    const text = document.createElement("span")
    text.className = "g-row-text"
    const title = document.createElement("strong")
    title.textContent = item.title
    const meta = document.createElement("small")
    meta.textContent = item.room || "Library"
    text.append(title, meta)
    const go = document.createElement("span")
    go.className = "g-row-go"
    go.setAttribute("aria-hidden", "true")
    go.textContent = "›"
    link.append(text, go)
    list.append(link)
  }
  section.hidden = items.length === 0
}

function setupListing() {
  const directory = document.querySelector<HTMLElement>("[data-garden-directory]")
  if (!directory) return

  const search = document.querySelector<HTMLInputElement>("[data-garden-search]")
  const buttons = [...document.querySelectorAll<HTMLButtonElement>("[data-sort]")]
  const count = document.querySelector<HTMLElement>("[data-garden-count]")
  const empty = document.querySelector<HTMLElement>("[data-garden-empty]")
  let sort = "updated"

  const update = () => {
    const query = (search?.value || "").trim().toLocaleLowerCase()
    let visible = 0
    for (const folder of directory.querySelectorAll<HTMLDetailsElement>("[data-folder]")) {
      const list = folder.querySelector<HTMLElement>(".g-list")
      if (!list) continue
      const rows = [...list.querySelectorAll<HTMLElement>("[data-garden-item]")]
      rows.sort((a, b) =>
        sort === "title"
          ? (a.dataset.title || "").localeCompare(b.dataset.title || "", "zh-CN")
          : Number(b.dataset.updated) - Number(a.dataset.updated),
      )
      let shown = 0
      for (const row of rows) {
        list.append(row)
        row.hidden = !(row.dataset.search || "").toLocaleLowerCase().includes(query)
        if (!row.hidden) shown++
      }
      folder.hidden = shown === 0
      if (query && shown) folder.open = true
      visible += shown
    }
    if (count) count.textContent = `${visible} 项`
    if (empty) empty.hidden = visible !== 0
  }

  const onSort = (event: Event) => {
    const button = event.currentTarget as HTMLButtonElement
    sort = button.dataset.sort || "updated"
    for (const other of buttons) other.setAttribute("aria-checked", String(other === button))
    update()
  }
  for (const button of buttons) {
    button.addEventListener("click", onSort)
    window.addCleanup?.(() => button.removeEventListener("click", onSort))
  }
  if (search) {
    search.addEventListener("input", update)
    window.addCleanup?.(() => search.removeEventListener("input", update))
  }
  update()
}

// Note pages get the same bottom tab bar as the garden rooms (shown on phones only).
function ensureTabbar(slug: string) {
  document.querySelectorAll(".g-tabbar--global").forEach((el) => el.remove())
  if (document.querySelector(".g-tabbar")) return
  const room = slug.startsWith("studio/") ? "studio" : "library"
  const links: [string, string, string, string][] = [
    [
      "home",
      "/",
      "首页",
      '<path d="M4 11.5 12 5l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5h-5v5H5a1 1 0 0 1-1-1z"/>',
    ],
    [
      "library",
      "/library/",
      "Library",
      '<path d="M5 5.5A1.5 1.5 0 0 1 6.5 4H19v14H6.5A1.5 1.5 0 0 0 5 19.5z"/><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"/>',
    ],
    [
      "gallery",
      "/gallery/",
      "Gallery",
      '<rect x="4" y="5" width="16" height="14" rx="2"/><path d="m4 16 4.5-4.5 4 4 2.5-2.5L20 18"/><circle cx="15.5" cy="9.5" r="1.5"/>',
    ],
    [
      "studio",
      "/studio/",
      "Studio",
      '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
    ],
  ]
  const nav = document.createElement("nav")
  nav.className = "g-tabbar g-tabbar--global"
  nav.setAttribute("aria-label", "花园导航")
  for (const [key, href, label, paths] of links) {
    const link = document.createElement("a")
    link.href = href
    if (key === room) link.setAttribute("aria-current", "page")
    link.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${paths}</svg><span>${label}</span>`
    nav.append(link)
  }
  document.body.append(nav)
}

document.addEventListener("nav", () => {
  const slug = document.body.dataset.slug || ""
  const isGarden = GARDEN_SLUGS.has(slug)
  document.documentElement.classList.toggle("is-garden", isGarden)

  if (!isGarden && !slug.startsWith("tags/") && slug !== "404") {
    const title = document.querySelector(".article-title")?.textContent?.trim() || document.title
    if (title)
      remember({
        title,
        url: location.href,
        room: slug.startsWith("studio/") ? "Studio" : "Library",
      })
  }

  ensureTabbar(slug)
  renderRecent()
  setupListing()
})
