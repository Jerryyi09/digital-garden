import { UserSync } from "./user-sync.js"
import { openSyncStore } from "./sync-store.js"
import { ROOT, resolveEndpoint, isWithinRoot, trackId, mediaUrl } from "./config.js"
import { getBookSummary, getBookCover, getJacketColors, hasBookReadalong } from "./summaries.js"
import { resolvePlaybackSegment, SYNC_STATE } from "./readalong-sync.js"
import { timelinePathForSource } from "./timeline-loader.js"
import { canSearch, normalizedSearchQuery, searchUrl } from "./search-client.js"

const manifestMemoryCache = new Map()
const timelineMemoryCache = new Map()

const $ = (id) => document.getElementById(id)
const audio = $("audio")
const AUDIO = /\.(mp3|m4a|m4b)$/i
const PDF = /\.pdf$/i
const IMG = /\.(jpg|jpeg|png|webp)$/i
const PREF = "garden-listen-prefs-v2"
const AUTH = "garden-listen-auth-v1"
const JOURNAL = "garden-listen-journal-v1"

let prefs = read(localStorage, PREF, { mode: "auto", username: "", speed: 1 })
let auth = read(sessionStorage, AUTH, null) || read(localStorage, AUTH, null)
let endpoint = resolveEndpoint(prefs.mode)
let records = []
let entries = []
let folder = ROOT
let current = null
let currentBookFolder = ""
let ready = false
let pendingPosition = null
let lastSave = 0
let playRequest = 0
let browseRequest = 0
let preparedNext = null
let db = null
let directoryPassword = ""
let syncStore = null
let userSync = null
let syncAccount = ""
let syncTimer = null
let searchTimer = null
let searchRequest = 0
let searchAbort = null
let globalSearchState = { query: "", results: [], loading: false, error: "" }

// Readalong & PDF State
let readalongManifest = null
let readalongTimeline = []
let readalongParentPath = ""
let readalongDocCache = new Map()
let readalongActive = false
let readalongFollowing = true
let currentSegment = null
let currentDocPath = ""
let readalongAssetBase = ""
let currentPdfPath = ""
let currentPdfName = ""
let pdfViewerActive = false
let currentGuidePath = ""
let currentGuideTitle = ""
let guideViewerActive = false
let currentFolderGuidePath = ""

// Sleep Timer State
let sleepTimerId = null
let sleepTimerMinutes = 0
let sleepTimerTargetTime = 0
let sleepTimerMode = "none" // "time" | "track" | "none"

// Device identity
let stableDevice = read(localStorage, "garden-listen-device", "")
if (!stableDevice) {
  stableDevice = `garden-listen-${Date.now()}-${Math.random().toString(36).slice(2)}`
  write(localStorage, "garden-listen-device", stableDevice)
}

function read(storage, key, fallback) {
  try {
    return JSON.parse(storage.getItem(key)) ?? fallback
  } catch {
    return fallback
  }
}

function write(storage, key, value) {
  try {
    storage.setItem(key, JSON.stringify(value))
    return true
  } catch {
    return false
  }
}

function remove(storage, key) {
  try {
    storage.removeItem(key)
  } catch {
    /* Storage can be disabled. */
  }
}

function notice(message = "", duration = 4000) {
  const el = $("notice")
  if (!message) {
    el.hidden = true
    return
  }
  el.textContent = message
  el.hidden = false
  setTimeout(() => {
    if (el.textContent === message) el.hidden = true
  }, duration)
}

function fail(error) {
  notice(error.message || "连接失败，请检查网络或登录状态。")
}

async function fetchGlobalSearch(query) {
  if (!auth?.token || !canSearch(query)) return
  const request = ++searchRequest
  searchAbort?.abort()
  searchAbort = new AbortController()
  globalSearchState = { query, results: [], loading: true, error: "" }
  render()
  try {
    const response = await fetch(searchUrl(query), {
      headers: { Authorization: auth.token, "Client-Id": stableDevice, ...(auth.deviceKey ? { "Device-Key": auth.deviceKey } : {}) },
      cache: "no-store", credentials: "omit", signal: searchAbort.signal,
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error === "invalid_query" ? "请输入 1 至 100 个字符。" : "全库搜索暂不可用")
    if (request !== searchRequest) return
    globalSearchState = { query, results: data.results || [], loading: false, error: "" }
  } catch (error) {
    if (error.name === "AbortError" || request !== searchRequest) return
    globalSearchState = { query, results: [], loading: false, error: error.message || "全库搜索暂不可用" }
  }
  render()
}

function scheduleGlobalSearch(value) {
  clearTimeout(searchTimer)
  const query = normalizedSearchQuery(value)
  ++searchRequest
  searchAbort?.abort()
  if (!canSearch(query)) {
    globalSearchState = { query: "", results: [], loading: false, error: "" }
    render()
    return
  }
  globalSearchState = { query, results: [], loading: true, error: "" }
  render()
  searchTimer = setTimeout(() => fetchGlobalSearch(query), 250)
}
function attempt(fn) {
  return (...args) =>
    Promise.resolve()
      .then(() => fn(...args))
      .catch(fail)
}

function account() {
  return auth?.username || prefs.username || "guest"
}
function libraryRecords() {
  return records
    .filter((record) => record.account === account())
    .sort((a, b) => b.updatedAt - a.updatedAt)
}
function progress(track) {
  return records.find((record) => record.account === account() && record.id === trackId(track))
}
function durationText(seconds) {
  const s = Math.max(0, Math.floor(Number(seconds) || 0))
  const hrs = Math.floor(s / 3600)
  const mins = Math.floor((s % 3600) / 60)
  const secs = String(s % 60).padStart(2, "0")
  return hrs > 0 ? `${hrs}:${String(mins).padStart(2, "0")}:${secs}` : `${String(mins).padStart(2, "0")}:${secs}`
}

const coverSignedCache = new Map()

function resolveBookCoverPath(parentDir, bookName) {
  if (!parentDir) return ""
  const registered = getBookCover(bookName)
  if (registered) return `${parentDir}/${registered}`
  // If parentDir is a sub-volume folder (e.g. .../Great Mental Models/Volume 1),
  // check if grandParent has registered cover or cover.jpg
  const grandParent = parentDir.slice(0, parentDir.lastIndexOf("/"))
  const grandName = grandParent ? grandParent.split("/").filter(Boolean).pop() : ""
  if (grandName && getBookCover(grandName)) {
    return `${grandParent}/${getBookCover(grandName)}`
  }
  // Standard cover filename present in our library
  return `${parentDir}/cover.jpg`
}

const coverQueue = []
let activeCoverRequests = 0
const MAX_CONCURRENT_COVER_REQUESTS = 4

function enqueueCoverRequest(fn) {
  return new Promise((resolve, reject) => {
    coverQueue.push({ fn, resolve, reject })
    processCoverQueue()
  })
}

function processCoverQueue() {
  while (activeCoverRequests < MAX_CONCURRENT_COVER_REQUESTS && coverQueue.length > 0) {
    const { fn, resolve, reject } = coverQueue.shift()
    activeCoverRequests++
    fn()
      .then(resolve)
      .catch(reject)
      .finally(() => {
        activeCoverRequests--
        processCoverQueue()
      })
  }
}

async function getSignedCoverUrl(fullImgPath) {
  if (!fullImgPath) return ""
  if (coverSignedCache.has(fullImgPath)) return coverSignedCache.get(fullImgPath)
  return enqueueCoverRequest(async () => {
    if (coverSignedCache.has(fullImgPath)) return coverSignedCache.get(fullImgPath)
    try {
      const info = await api("fs/get", { path: fullImgPath, password: directoryPassword }).catch(() => null)
      if (!info) return ""
      const url = mediaUrl(endpoint, { path: fullImgPath }, info.sign)
      coverSignedCache.set(fullImgPath, url)
      return url
    } catch {
      return ""
    }
  })
}

const coverObserver = typeof IntersectionObserver !== "undefined"
  ? new IntersectionObserver((entries, observer) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const wrap = entry.target
          observer.unobserve(wrap)
          const imgPath = wrap.dataset.coverPath
          const img = wrap.querySelector(".cover-real-img")
          if (imgPath && img) {
            getSignedCoverUrl(imgPath).then((signedUrl) => {
              if (signedUrl) img.src = signedUrl
              else img.remove()
            }).catch(() => img.remove())
          }
        }
      }
    }, { rootMargin: "250px 0px" })
  : null

function createBookCoverElement(bookTitle, sizeClass = "size-row", fullImgPath = "") {
  const coverWrap = document.createElement("div")
  coverWrap.className = `wx-book-cover ${sizeClass}`

  // Spine Shadow Overlay
  const spine = document.createElement("div")
  spine.className = "cover-spine-edge"
  coverWrap.append(spine)

  // Fallback Elegant Morandi Book Jacket
  const [c1, c2] = getJacketColors(bookTitle)
  const fallback = document.createElement("div")
  fallback.className = "cover-fallback-jacket"
  fallback.style.setProperty("--jacket-color-1", c1)
  fallback.style.setProperty("--jacket-color-2", c2)

  const titleText = document.createElement("div")
  titleText.className = "fallback-title"
  titleText.textContent = bookTitle || "有声书"

  const mark = document.createElement("div")
  mark.className = "fallback-bottom-mark"
  mark.textContent = "ROSEMARY"

  fallback.append(titleText, mark)
  coverWrap.append(fallback)

  // Real Cover Image with Signed URL Fetch
  if (fullImgPath) {
    const img = document.createElement("img")
    img.className = "cover-real-img"
    img.loading = "lazy"
    img.alt = bookTitle || "封面"
    img.onerror = () => {
      img.remove() // Fallback jacket immediately becomes visible underneath
    }
    coverWrap.append(img)

    // Load with sign
    if (coverSignedCache.has(fullImgPath)) {
      img.src = coverSignedCache.get(fullImgPath)
    } else if (coverObserver) {
      coverWrap.dataset.coverPath = fullImgPath
      coverObserver.observe(coverWrap)
    } else {
      getSignedCoverUrl(fullImgPath).then((signedUrl) => {
        if (signedUrl) {
          img.src = signedUrl
        } else {
          img.remove()
        }
      }).catch(() => img.remove())
    }
  }

  return coverWrap
}

async function openDatabase() {
  db = await new Promise((resolve, reject) => {
    const request = indexedDB.open("garden-audiobooks", 1)
    request.onupgradeneeded = () =>
      request.result.createObjectStore("progress", { keyPath: "key" })
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
  records = await new Promise((resolve, reject) => {
    const request = db.transaction("progress").objectStore("progress").getAll()
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function persist(record) {
  const index = records.findIndex((item) => item.key === record.key)
  if (index < 0) records.push(record)
  else records[index] = record
  if (db) {
    const transaction = db.transaction("progress", "readwrite")
    transaction.objectStore("progress").put(record)
  }
}

async function startUserSync() {
  if (!auth?.token || !syncStore) return
  const owner = account()
  syncAccount = owner
  const client = new UserSync({
    lockName: `garden-user-sync:${owner}`,
    list: () => syncStore.list(owner),
    put: row => syncStore.put(owner, row),
    request: async (method, body) => {
      if (syncAccount !== owner || !auth?.token) throw new Error("账号已切换")
      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), 12000)
      try {
        const response = await fetch("https://melyi.uk:8089/sync/v1/items", {
          method, headers: { Authorization: auth.token, "Client-Id": stableDevice, ...(auth.deviceKey ? { "Device-Key": auth.deviceKey } : {}), ...(body ? { "Content-Type": "application/json" } : {}) },
          body: body ? JSON.stringify(body) : undefined, cache: "no-store", credentials: "omit", signal: controller.signal,
        })
        const data = await response.json()
        if (!response.ok) throw Object.assign(new Error("同步服务暂不可用"), { status: response.status, current: data.current })
        return data
      } finally {
        clearTimeout(timer)
      }
    },
    onChange: row => {
      if (syncAccount !== owner) return
      if (row.kind === "progress" && !row.dirty && row.value?.track && isWithinRoot(row.value.track.path)) {
        const record = { ...row.value, account: owner, id: trackId(row.value.track), key: JSON.stringify([owner, trackId(row.value.track)]) }
        persist(record)
        const journal = read(localStorage, JOURNAL, null)
        if (!journal || journal.account !== owner || record.updatedAt > journal.updatedAt) write(localStorage, JOURNAL, record)
      }
    },
  })
  userSync = client
  try {
    for (const record of records.filter(row => row.account === owner && row.track && isWithinRoot(row.track.path)).sort((a, b) => b.updatedAt - a.updatedAt)) {
      await client.seed("progress", record.track.path, record)
    }
    await client.sync()
    if (userSync === client) { render(); await renderSyncItems() }
  } catch (error) {
    if (userSync === client) {
      await renderSyncItems()
      $("sync-status").textContent = "同步未连接，记录保存在本机"
    }
  }
}

function scheduleUserSync() {
  clearTimeout(syncTimer)
  syncTimer = setTimeout(() => {
    if (!userSync) return
    userSync.sync().then((remoteChanged) => {
      // A periodic sync commonly finds no remote changes. Rebuilding the home
      // dashboard in that case restarts its cover image loads and makes the
      // three recent cards visibly jump.
      if (remoteChanged) render()
      return renderSyncItems()
    }).catch(() => {
      $("sync-status").textContent = "同步未连接，记录保存在本机"
    })
  }, 1500)
}

async function renderSyncItems() {
  if (!syncStore || !userSync || !syncAccount) return
  const owner = syncAccount
  const rows = await syncStore.list(owner)
  if (syncAccount !== owner) return
  const conflicts = rows.filter(row => row.conflict)
  const dirty = rows.filter(row => row.dirty)
  $("sync-status").textContent = conflicts.length ? `有 ${conflicts.length} 条记录需要选择` : dirty.length ? `等待同步 ${dirty.length} 条` : "已同步"
  const container = $("sync-items")
  container.replaceChildren()
  for (const row of conflicts) {
    const group = document.createElement("div")
    const label = document.createElement("p")
    label.textContent = `同步冲突：${row.value?.track?.name || row.id}（本机 ${durationText(row.value?.position)} / 其他设备 ${durationText(row.conflict.value?.position)}）`
    group.append(label)
    const choices = row.conflict.missing ? [["local", "恢复本机"]] : [["local", "保留本机"], ["remote", "使用其他设备"]]
    for (const [choice, title] of choices) {
      const button = document.createElement("button")
      button.textContent = title
      button.addEventListener("click", attempt(async () => {
        await userSync.resolve(row.kind, row.id, choice)
        await userSync.sync()
        render()
        await renderSyncItems()
      }))
      group.append(button)
    }
    container.append(group)
  }
  const bookmarks = rows.filter(row => row.kind === "bookmark" && !row.value?.deleted)
  const heading = document.createElement("p")
  heading.textContent = `书签（${bookmarks.length}）`
  container.append(heading)
  for (const row of bookmarks) {
    if (!row.value?.track || !isWithinRoot(row.value.track.path)) continue
    const group = document.createElement("div")
    const open = document.createElement("button")
    open.textContent = `${row.value.track.name} · ${durationText(row.value.position)}`
    open.addEventListener("click", attempt(async () => {
      await loadTrack(row.value.track)
      pendingPosition = Math.max(0, row.value.position)
      restorePosition()
    }))
    const removeBookmark = document.createElement("button")
    removeBookmark.textContent = "删除"
    removeBookmark.addEventListener("click", attempt(async () => {
      await userSync.save("bookmark", row.id, { ...row.value, deleted: true })
      await renderSyncItems()
      scheduleUserSync()
    }))
    group.append(open, removeBookmark)
    container.append(group)
  }
}

function saveProgress(completed = audio.ended) {
  if (
    !current ||
    !ready ||
    pendingPosition !== null ||
    !Number.isFinite(audio.duration) ||
    audio.duration <= 0
  )
    return
  const record = {
    key: JSON.stringify([account(), trackId(current)]),
    account: account(),
    id: trackId(current),
    track: current,
    position: audio.currentTime,
    duration: audio.duration,
    completed,
    updatedAt: Date.now(),
    speed: audio.playbackRate,
  }
  persist(record)
  if (userSync && syncAccount === account()) {
    userSync.save("progress", record.track.path, record).then(scheduleUserSync).catch(() => {})
  }
  write(localStorage, JOURNAL, record)
  lastSave = Date.now()
}

async function api(route, body = {}, token = auth?.token) {
  const headers = { "Content-Type": "application/json", "Client-Id": stableDevice }
  if (token) headers.Authorization = token
  if (auth?.deviceKey) headers["Device-Key"] = auth.deviceKey
  let response
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 12000)
    response = await fetch(`${endpoint}/api/${route}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      credentials: "omit",
      cache: "no-store",
      signal: controller.signal,
    })
    clearTimeout(timer)
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error(`连接书库超时（12秒未响应），请检查家庭服务器网络。`)
    }
    throw new Error(
      `无法连接家庭书库（${endpoint}）：${err.message || "网络异常，请检查访问模式。"}`
    )
  }

  let result
  try {
    result = await response.json()
  } catch {
    throw new Error(`书库响应格式异常（HTTP ${response.status}）`)
  }

  if (result.code !== 200) {
    if (result.code === 401) {
      $("settings")?.showModal()
      throw new Error("请使用 AList 账号登录；登录已过期。")
    }
    if (result.code === 400 && String(result.message).toLowerCase().includes("password")) {
      throw new Error("AList 用户名或密码错误，请重新输入。")
    }
    throw new Error(result.message || `AList 错误 ${result.code}`)
  }
  return result.data
}

async function list(path) {
  if (!isWithinRoot(path)) throw new Error(`只能浏览 ${ROOT} 下的目录`)
  const content = []
  let hasReadalongInFolder = false
  let pdfInFolder = null
  let epubInFolder = null
  let imageInFolder = null
  let guideInFolder = null
  for (let page = 1; ; page++) {
    const data = await api("fs/list", {
      path,
      password: directoryPassword,
      page,
      per_page: 200,
      refresh: false,
    })
    const batch = data.content || []
    if (batch.some((item) => item.name === "readalong" || item.name === ".readalong")) {
      hasReadalongInFolder = true
    }
    const pdfItem = batch.find((item) => !item.is_dir && PDF.test(item.name))
    if (pdfItem && !pdfInFolder) {
      pdfInFolder = pdfItem.name
    }
    const epubItem = batch.find((item) => !item.is_dir && /\.epub$/i.test(item.name))
    if (epubItem && !epubInFolder) {
      epubInFolder = epubItem.name
    }
    const guideItem = batch.find((item) => !item.is_dir && /^guide\.html$/i.test(item.name))
    if (guideItem && !guideInFolder) {
      guideInFolder = guideItem.name
    }
    const imgItem = batch.find((item) => !item.is_dir && IMG.test(item.name) && !item.name.startsWith("._"))
    if (imgItem && !imageInFolder) {
      imageInFolder = imgItem.name
    }
    content.push(...batch)
    if (!batch.length || content.length >= (data.total ?? content.length)) break
  }
  const ignoredNames = new Set([
    "readalong",
    ".readalong",
    "work",
    "generated",
    "preview",
    "runtime-snapshot",
    "__pycache__",
  ])
  currentFolderGuidePath = guideInFolder ? `${path}/${guideInFolder}` : ""
  return content
    .filter((item) => {
      if (ignoredNames.has(item.name)) return false
      return item.is_dir || AUDIO.test(item.name)
    })
    .map((item) => {
      const coverFile = item.is_dir ? getBookCover(item.name) : imageInFolder
      return {
        path: `${path}/${item.name}`,
        name: item.name,
        is_dir: item.is_dir === true,
        size: item.size,
        modified: item.modified,
        hasReadalong: item.is_dir ? hasBookReadalong(item.name) : hasReadalongInFolder,
        hasPdf: Boolean(pdfInFolder) && !item.is_dir,
        pdfName: pdfInFolder,
        hasEpub: Boolean(epubInFolder) && !item.is_dir,
        epubName: epubInFolder,
        coverFile: coverFile || null,
      }
    })
}

async function browse(path = folder) {
  const request = ++browseRequest
  $("list-status").textContent = "正在读取目录..."
  const refreshBtn = $("refresh")
  if (refreshBtn) refreshBtn.disabled = true
  try {
    const result = await list(path)
    if (request !== browseRequest) return
    entries = result
    folder = path
    $("search").value = ""
    $("search-clear").hidden = true
    render()
  } catch (err) {
    if (request === browseRequest) {
      entries = []
      $("list-status").textContent = "未连接书库或登录已过期，请点击右上角设置登录"
      notice(err.message || "无法连接书库，请登录 AList。")
      render()
    }
  } finally {
    if (request === browseRequest) {
      const refreshBtn = $("refresh")
      if (refreshBtn) refreshBtn.disabled = false
    }
  }
}

function breadcrumbs() {
  const nav = $("breadcrumbs")
  nav.replaceChildren()
  const names = folder.slice(ROOT.length).split("/").filter(Boolean)
  let path = ROOT
  for (const name of ["全部分类", ...names]) {
    if (name !== "全部分类") path += `/${name}`
    const target = path
    const button = document.createElement("button")
    button.textContent = name === "全部分类" ? name : ` / ${name}`
    button.onclick = attempt(() => browse(target))
    nav.append(button)
  }
}

function navigateUp() {
  if (folder === ROOT || !isWithinRoot(folder)) {
    window.location.href = "/studio/"
    return
  }
  const parent = folder.slice(0, folder.lastIndexOf("/"))
  if (parent.length < ROOT.length || !isWithinRoot(parent)) {
    browse(ROOT)
  } else {
    browse(parent)
  }
}

function renderShelf() {
  const shelfContainer = $("shelf-items")
  shelfContainer.replaceChildren()
  const recs = libraryRecords()
  $("shelf-count").textContent = `${recs.length} 本正在收听`

  if (!recs.length) {
    const empty = document.createElement("div")
    empty.className = "shelf-empty-state"
    empty.textContent = "书架空空如也。前往「书库」选一本好书，开始倾听吧。"
    shelfContainer.append(empty)
    return
  }

  for (const record of recs) {
    const card = document.createElement("div")
    card.className = "shelf-card"

    const pathParts = record.track.path.slice(ROOT.length).split("/").filter(Boolean)
    const bookName = pathParts.length > 1 ? pathParts[1] : record.track.name.replace(AUDIO, "")
    const coverFile = getBookCover(bookName)
    let fullCoverPath = ""
    if (coverFile) {
      const parentDir = record.track.path.slice(0, record.track.path.lastIndexOf("/"))
      fullCoverPath = `${parentDir}/${coverFile}`
    }

    const cover = createBookCoverElement(bookName, "size-shelf", fullCoverPath)

    const title = document.createElement("div")
    title.className = "shelf-card-title"
    title.textContent = bookName
    if (hasBookReadalong(bookName)) {
      const badge = document.createElement("span")
      badge.className = "badge-readalong"
      badge.textContent = "跟读"
      title.append(" ", badge)
    }

    const prog = document.createElement("div")
    prog.className = "shelf-card-progress"
    const percent = Math.min(100, Math.floor((record.position / (record.duration || 1)) * 100))
    prog.textContent = record.completed ? "已读完" : `已听 ${percent}%`

    card.append(cover, title, prog)
    card.onclick = attempt(() => loadTrack(record.track))
    shelfContainer.append(card)
  }
}

const CATEGORY_SPINE_PALETTES = {
  "心智成长": ["#6b2d2d", "#8c3b3b", "#4a1e1e"],
  "文学作品": ["#1f3a52", "#2c4f6f", "#152737"],
  "文学理论": ["#2d4a3e", "#3d6454", "#1e322a"],
  "计算机与AI": ["#223147", "#324867", "#172231"],
  "艺术": ["#704214", "#8d531b", "#53310f"],
  "教育": ["#5a3d28", "#785237", "#412c1d"],
  "音乐": ["#4b3056", "#664275", "#36223e"],
  "英文读写": ["#2f4858", "#3f6176", "#21333e"],
  "传记": ["#6e3b3b", "#8b4d4d", "#502b2b"],
  "历史": ["#5c4033", "#7a5544", "#432f25"],
  "哲学": ["#2e4053", "#3d566e", "#1f2c3a"],
  "自然博物": ["#2e5339", "#3e6e4d", "#1f3827"],
  "政治": ["#5d2e46", "#7b3d5d", "#402030"],
  "社会文化": ["#4a4036", "#635649", "#342d26"],
  "科学技术": ["#1b4f72", "#246693", "#133852"],
  "数理化": ["#1a5276", "#226b9c", "#123a54"],
  "商业经济": ["#515a5a", "#6b7777", "#3a4040"],
}

// Memory cache for asynchronously loaded summary.txt from AList
const asyncSummaryMemoryCache = new Map()

async function loadAsyncSummary(bookPath, textElement) {
  if (asyncSummaryMemoryCache.has(bookPath)) {
    const cached = asyncSummaryMemoryCache.get(bookPath)
    if (cached && textElement) textElement.textContent = cached
    return
  }
  try {
    const sumPath = `${bookPath}/summary.txt`
    const info = await api("fs/get", { path: sumPath, password: directoryPassword }).catch(() => null)
    if (info && !info.is_dir) {
      const url = mediaUrl(endpoint, { path: sumPath }, info.sign)
      const text = await fetch(url).then(r => r.text()).catch(() => "")
      if (text && text.trim()) {
        const clean = text.trim()
        asyncSummaryMemoryCache.set(bookPath, clean)
        if (textElement) textElement.textContent = clean
      }
    }
  } catch {}
}

const CATEGORY_SHORT_NAMES = {
  "心智成长": "心智",
  "文学作品": "文学",
  "文学理论": "文论",
  "计算机与AI": "计算",
  "艺术": "艺术",
  "教育": "教育",
  "音乐": "音乐",
  "英文读写": "英文",
  "传记": "传记",
  "历史": "历史",
  "哲学": "哲学",
  "自然博物": "博物",
  "政治": "政治",
  "社会文化": "社会",
  "科学技术": "科技",
  "数理化": "数理",
  "商业经济": "经济",
}

function getCategoryShortName(fullName) {
  for (const [k, v] of Object.entries(CATEGORY_SHORT_NAMES)) {
    if (fullName.includes(k)) return v
  }
  return fullName.slice(0, 2)
}

function getCategoryPalette(name) {
  for (const [key, val] of Object.entries(CATEGORY_SPINE_PALETTES)) {
    if (name.includes(key)) return val
  }
  const hash = name.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const defaultColors = [
    ["#4a3b32", "#634f43", "#352a24"],
    ["#2c3e50", "#3a5169", "#1f2c39"],
    ["#34495e", "#445f7a", "#253443"],
    ["#4a235a", "#633079", "#351941"],
    ["#145a32", "#1b7843", "#0e3f23"],
    ["#78281f", "#9d3529", "#551d16"]
  ]
  return defaultColors[hash % defaultColors.length]
}

function renderHomeDashboard(categoryItems) {
  const container = $("items")
  container.replaceChildren()

  const dashboard = document.createElement("div")
  dashboard.className = "home-dashboard"

  // ----------------------------------------------------
  // 上栏：最近三个播放的有声书（恢复经典设计，一行 3 个并排大图标，显示进度，点击播放）
  // ----------------------------------------------------
  const recentSection = document.createElement("section")
  recentSection.className = "home-section recent-listen-section"

  const recentHeader = document.createElement("div")
  recentHeader.className = "section-title-bar"
  const recentTitle = document.createElement("h3")
  recentTitle.className = "section-title"
  recentTitle.textContent = "最近在听"
  const recentMore = document.createElement("span")
  recentMore.className = "section-more"
  recentMore.textContent = "历史记录"
  recentHeader.append(recentTitle, recentMore)
  recentSection.append(recentHeader)

  // 1. 优先从用户真实听书历史中提取
  const allRecords = libraryRecords()
  const recentCardsData = []
  const seenBooks = new Set()
  for (const rec of allRecords) {
    const pathParts = rec.track.path.slice(ROOT.length).split("/").filter(Boolean)
    const bookName = pathParts.length > 1 ? pathParts[1] : rec.track.name.replace(AUDIO, "")
    if (!seenBooks.has(bookName)) {
      seenBooks.add(bookName)
      recentCardsData.push({
        bookName,
        track: rec.track,
        position: rec.position || 0,
        duration: rec.duration || 1,
        completed: rec.completed || false
      })
      if (recentCardsData.length >= 3) break
    }
  }

  // 2. 若不足 3 本，从书库经典已上线图书中补齐满 3 本！
  if (recentCardsData.length < 3) {
    const fallbackFeatured = [
      { bookName: "思考快与慢", cat: "心智成长", trackName: "01 Chapter 1.mp3", pos: 350, dur: 1200 },
      { bookName: "1984 乔治 奥威尔", cat: "文学作品", trackName: "01 Part 1 Chapter 1.mp3", pos: 420, dur: 1500 },
      { bookName: "Why Machines Learn", cat: "计算机与AI", trackName: "Why Machines Learn꞉ The Elegant Maths Behind Modern AI - 06 - Chapter 1꞉ Desperately Seeking Patterns.m4b", pos: 180, dur: 1800 },
    ]
    for (const f of fallbackFeatured) {
      if (!seenBooks.has(f.bookName)) {
        seenBooks.add(f.bookName)
        recentCardsData.push({
          bookName: f.bookName,
          track: {
            name: f.trackName,
            path: `${ROOT}/${f.cat}/${f.bookName}/${f.trackName}`,
            is_dir: false
          },
          position: f.pos,
          duration: f.dur,
          completed: false
        })
        if (recentCardsData.length >= 3) break
      }
    }
  }

  const recentGrid = document.createElement("div")
  recentGrid.className = "recent-grid-3"

  for (const item of recentCardsData) {
    const card = document.createElement("div")
    card.className = "recent-book-card"
    card.title = `继续收听：${item.bookName}`

    const coverWrap = document.createElement("div")
    coverWrap.className = "recent-cover-wrap"

    const coverFile = getBookCover(item.bookName)
    let fullCoverPath = ""
    if (coverFile) {
      const parentDir = item.track.path.slice(0, item.track.path.lastIndexOf("/"))
      fullCoverPath = `${parentDir}/${coverFile}`
    }
    // 恢复立体大书封设计
    const coverEl = createBookCoverElement(item.bookName, "size-shelf", fullCoverPath)

    const playBadge = document.createElement("div")
    playBadge.className = "recent-play-badge"
    playBadge.innerHTML = `<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>`

    coverWrap.append(coverEl, playBadge)

    // 只留图片和播放小图标（无白框、无进度条、无文字书名）
    card.append(coverWrap)

    // 点击直接播放！
    card.onclick = attempt(() => loadTrack(item.track))
    recentGrid.append(card)
  }
  recentSection.append(recentGrid)
  dashboard.append(recentSection)

  // ----------------------------------------------------
  // 下栏：书库分类（极简轻盈胶囊，一行 3 个并排，简洁设计一屏尽览）
  // ----------------------------------------------------
  const catSection = document.createElement("section")
  catSection.className = "home-section categories-pills-section"

  const catHeader = document.createElement("div")
  catHeader.className = "home-section-header"
  catHeader.style.marginBottom = "6px"
  const catTitle = document.createElement("span")
  catTitle.style.cssText = "font-size: 13px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.05em;"
  catTitle.textContent = "分类专栏"
  catHeader.append(catTitle)
  catSection.append(catHeader)

  const catGrid = document.createElement("div")
  catGrid.className = "category-pills-grid"

  for (const catItem of categoryItems) {
    const card = document.createElement("div")
    card.className = "category-pill-card"
    card.title = `浏览分类：${catItem.name}`

    const palette = getCategoryPalette(catItem.name)
    const dot = document.createElement("span")
    dot.className = "category-pill-dot"
    dot.style.setProperty("--cat-dot-color", palette[1])

    const nameEl = document.createElement("span")
    nameEl.className = "category-pill-title"
    nameEl.textContent = catItem.name

    card.append(dot, nameEl)

    // 点击进入该分类
    card.onclick = attempt(() => browse(catItem.path))
    catGrid.append(card)
  }

  catSection.append(catGrid)
  dashboard.append(catSection)

  container.append(dashboard)
}

function renderGlobalSearch(query) {
  $("folder-summary").hidden = true
  $("breadcrumbs").parentElement.hidden = false
  $("list-status").parentElement.hidden = false
  $("breadcrumbs").replaceChildren()
  const crumb = document.createElement("span")
  crumb.textContent = "全库搜索"
  $("breadcrumbs").append(crumb)
  $("items").replaceChildren()
  const { results, loading, error } = globalSearchState
  $("list-status").textContent = loading ? `正在搜索“${query}”...` : `“${query}” · ${results.length} 条全库结果`
  if (error) {
    const message = document.createElement("div")
    message.className = "shelf-empty-state"
    message.textContent = error
    $("items").append(message)
    return
  }
  for (const result of results) {
    const row = document.createElement("div")
    row.className = "item-row global-search-row"
    row.setAttribute("role", "listitem")
    const card = document.createElement("div")
    card.className = "item-card"
    const icon = document.createElement("div")
    icon.className = result.kind === "book" ? "search-book-icon" : "track-disc-icon"
    icon.textContent = result.kind === "book" ? "📖" : "♫"
    const info = document.createElement("div")
    info.className = "item-main-info"
    const title = document.createElement("h3")
    title.className = "item-name"
    title.textContent = result.kind === "book" ? result.title : result.chapter
    const meta = document.createElement("p")
    meta.className = "item-meta-text search-result-meta"
    meta.textContent = [result.title, result.author, result.category].filter(Boolean).join(" · ")
    info.append(title, meta)
    if (result.summary) {
      const summary = document.createElement("p")
      summary.className = "item-desc-text"
      summary.textContent = result.summary
      info.append(summary)
    }
    const action = document.createElement("div")
    action.className = "item-action-icon"
    action.textContent = result.kind === "book" ? "›" : "▶"
    card.append(icon, info, action)
    card.onclick = attempt(() => result.kind === "book" ? browse(result.path) : loadTrack({ path: result.path, name: result.chapter, is_dir: false }))
    row.append(card)
    $("items").append(row)
  }
  if (!loading && !results.length) {
    const empty = document.createElement("div")
    empty.className = "shelf-empty-state"
    empty.textContent = "没有找到书名、作者或章节。"
    $("items").append(empty)
  }
}

function render() {
  breadcrumbs()

  // Display full book overview banner if inside a book folder
  const currentDirName = folder.slice(ROOT.length).split("/").filter(Boolean).pop() || ""
  const currentSummary = getBookSummary(currentDirName)
  const isBookFolder = folder !== ROOT && entries.some((item) => !item.is_dir)

  if (isBookFolder) {
    $("banner-title").textContent = currentDirName
    const sumEl = $("folder-summary-text")
    sumEl.textContent = ""
    if (currentSummary) {
      sumEl.textContent = currentSummary
    } else {
      loadAsyncSummary(folder, sumEl)
    }

    // Render Banner Cover
    const bannerCoverWrap = document.querySelector(".banner-cover-wrap")
    if (bannerCoverWrap) {
      bannerCoverWrap.replaceChildren()
      const coverFile = getBookCover(currentDirName) || entries.find((i) => i.coverFile)?.coverFile
      const fullCoverPath = coverFile ? `${folder}/${coverFile}` : ""
      bannerCoverWrap.append(createBookCoverElement(currentDirName, "size-banner", fullCoverPath))
    }
    if (currentFolderGuidePath) {
      $("folder-summary").classList.add("has-guide")
    } else {
      $("folder-summary").classList.remove("has-guide")
    }
    $("folder-summary").hidden = false
  } else {
    $("folder-summary").hidden = true
  }

  const query = $("search").value.trim().toLocaleLowerCase()
  if (query) {
    renderGlobalSearch(normalizedSearchQuery(query))
    return
  }
  let items = [...entries]

  items.sort(
    (a, b) =>
      Number(b.is_dir) - Number(a.is_dir) ||
      ($("sort").value === "modified"
        ? (Date.parse(b.modified) || 0) - (Date.parse(a.modified) || 0)
        : a.name.localeCompare(b.name, "zh-CN", { numeric: true })),
  )

  // 当处于首页且非搜索状态时，展现极简双栏仪表盘：彻底取消顶栏分类/状态栏，手机一屏尽收眼底
  if (folder === ROOT && !query) {
    $("breadcrumbs").parentElement.hidden = true
    $("list-status").parentElement.hidden = true
    const dirItems = items.filter((item) => item.is_dir)
    renderHomeDashboard(dirItems)
    return
  } else {
    $("breadcrumbs").parentElement.hidden = false
    $("list-status").parentElement.hidden = false
  }

  $("items").replaceChildren()
  $("list-status").textContent = `${folder === ROOT ? "全部有声书" : currentDirName} · ${items.length} 项${query ? " (已筛选)" : ""}`

  for (const item of items) {
    const record = progress(item)
    const row = document.createElement("div")
    row.className = "item-row"
    row.setAttribute("role", "listitem")

    const card = document.createElement("div")
    card.className = "item-card"

    // Left visual: Book cover for folder, disc icon for audio track
    if (item.is_dir) {
      let fullCoverPath = ""
      if (folder !== ROOT) {
        // Inside a category folder (e.g. 文学作品, 心智成长), each sub-item is a book folder
        // If sub-folder is a Volume (e.g. Volume 1), check parent folder's cover too
        const parentFolderName = folder.split("/").filter(Boolean).pop() || ""
        const coverFile = item.coverFile || getBookCover(item.name) || getBookCover(parentFolderName) || "cover.jpg"
        fullCoverPath = `${item.path}/${coverFile}`
      }
      const coverEl = createBookCoverElement(item.name, "size-row", fullCoverPath)

      // 在左侧图片右上角加小图标：可以跟读加跟读，不可跟读但有pdf加pdf，没有pdf或epub不加
      const hasRead = hasBookReadalong(item.name) || item.hasReadalong
      if (hasRead) {
        const badge = document.createElement("span")
        badge.className = "cover-corner-badge badge-readalong"
        badge.textContent = "跟读"
        coverEl.append(badge)
      } else if (item.hasPdf) {
        const badge = document.createElement("span")
        badge.className = "cover-corner-badge badge-pdf"
        badge.textContent = "PDF"
        coverEl.append(badge)
      }
      card.append(coverEl)
    } else {
      const disc = document.createElement("div")
      disc.className = "track-disc-icon"
      disc.textContent = "♫"
      card.append(disc)
    }

    const info = document.createElement("div")
    info.className = "item-main-info"

    const titleRow = document.createElement("div")
    titleRow.className = "item-title-row"

    const title = document.createElement("h3")
    title.className = "item-name"
    title.textContent = item.name.replace(AUDIO, "")
    titleRow.append(title)
    info.append(titleRow)

    if (item.is_dir) {
      const desc = document.createElement("p")
      desc.className = "item-desc-text"
      const staticSum = getBookSummary(item.name)
      if (staticSum) {
        desc.textContent = staticSum
      } else {
        desc.textContent = ""
        loadAsyncSummary(item.path, desc)
      }
      info.append(desc)
    } else {
      const meta = document.createElement("p")
      meta.className = "item-meta-text"
      meta.textContent = record
        ? `${record.completed ? "已听完" : "听至"} ${durationText(record.position)} / ${durationText(record.duration)}`
        : `${(item.size / 1024 / 1024).toFixed(1)} MB · 点击播放`
      info.append(meta)
    }

    const action = document.createElement("div")
    action.className = "item-action-icon"
    action.innerHTML = item.is_dir
      ? '<svg viewBox="0 0 24 24" class="icon-sm"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>'
      : '<svg viewBox="0 0 24 24" class="icon-sm"><path d="M8 5v14l11-7z"/></svg>'

    card.append(info, action)
    row.append(card)

    if (record && !item.is_dir) {
      const line = document.createElement("div")
      line.className = "item-progress-line"
      const bar = document.createElement("div")
      bar.className = "item-progress-bar"
      bar.style.width = `${Math.min(100, (record.position / (record.duration || 1)) * 100)}%`
      line.append(bar)
      row.append(line)
    }

    card.onclick = attempt(() => (item.is_dir ? browse(item.path) : loadTrack(item)))
    $("items").append(row)
  }

  if (!items.length) {
    const empty = document.createElement("div")
    empty.className = "shelf-empty-state"
    empty.textContent = query ? "没有找到符合条件的内容。" : "目录为空。"
    $("items").append(empty)
  }

  updateProfileStats()
}

function updateProfileStats() {
  const recs = libraryRecords()
  $("stat-books-count").textContent = recs.length
  $("stat-completed-count").textContent = recs.filter((r) => r.completed).length
  const totalSecs = recs.reduce((acc, r) => acc + (r.position || 0), 0)
  $("stat-hours-count").textContent = (totalSecs / 3600).toFixed(1)
  $("account-status").textContent = `账号: ${account()}`
  $("current-endpoint-display").textContent = endpoint.startsWith(location.origin) ? "内网直连" : "公网 HTTPS"
}

async function stream(track) {
  const info = await api("fs/get", { path: track.path, password: directoryPassword })
  return mediaUrl(endpoint, track, info.sign)
}

async function prepareNext(request) {
  preparedNext = null
  if ($("btn-next")) $("btn-next").disabled = true
  try {
    const parent = current.path.slice(0, current.path.lastIndexOf("/"))
    const tracks = (parent === folder ? entries : await list(parent))
      .filter((item) => !item.is_dir)
      .sort((a, b) => a.name.localeCompare(b.name, "zh-CN", { numeric: true }))
    const index = tracks.findIndex((item) => item.path === current?.path)
    const next = index >= 0 ? tracks[index + 1] : null
    if (!next) return
    const url = await stream(next)
    if (request === playRequest) {
      preparedNext = { track: next, url, preparedAt: Date.now() }
      if ($("btn-next")) $("btn-next").disabled = false
    }
  } catch {
    /* Next chapter discovery failure shouldn't stop playback */
  }
}

async function loadTrack(track, preparedUrl) {
  invalidateReadalong()
  if (!isWithinRoot(track.path) || !AUDIO.test(track.name))
    throw new Error("不是可播放的有声书音频文件")
  saveProgress()
  const request = ++playRequest
  audio.pause()
  ready = false
  pendingPosition = null
  current = null
  preparedNext = null
  if ($("btn-next")) $("btn-next").disabled = true

  // Immediately clear old timeline & document to avoid scanning wrong chapters
  readalongTimeline = []
  currentSegment = null
  currentDocPath = ""
  $("dock-readalong").hidden = true
  $("dock-pdf").hidden = true
  currentGuidePath = ""
  currentGuideTitle = ""
  const dockGuide = $("dock-guide")
  if (dockGuide) {
    dockGuide.disabled = true
    dockGuide.classList.add("disabled")
    dockGuide.title = "暂无深度导读"
  }

  // Set titles and artwork in Mini and Full Player
  const parentDir = track.path.slice(0, track.path.lastIndexOf("/"))
  const bookName = parentDir.split("/").filter(Boolean).pop() || "有声书"
  const trackName = track.name.replace(AUDIO, "")

  $("mini-title").textContent = trackName
  $("mini-subtitle").textContent = bookName
  $("player-book-title").textContent = bookName
  $("player-track-title").textContent = trackName
  const trackDesc = $("player-track-desc")
  if (trackDesc) trackDesc.textContent = "正在加载音频..."

  // Update Disc Center Artwork with Book Cover
  const fullCoverPath = resolveBookCoverPath(parentDir, bookName)

  const miniThumb = $("mini-cover-thumb")
  const vinylCenter = $("vinyl-cover-art")
  const rfCenter = document.querySelector("#readalong-floating-disc .floating-center")
  const pfCenter = document.querySelector("#pdf-floating-disc .floating-center")
  const gfCenter = document.querySelector("#guide-floating-disc .floating-center")

  // Fallback defaults: Elegant Ivory Vinyl Record Label (never pitch black!)
  const shortTitle = bookName.slice(0, 4)
  if (miniThumb) { miniThumb.style.background = "#32353a"; $("mini-cover-icon").hidden = false; $("mini-cover-icon").textContent = "♫" }
  if (vinylCenter) {
    vinylCenter.style.background = "#fbf9f4"
    vinylCenter.style.color = "#18191b"
    vinylCenter.textContent = shortTitle
  }
  if (rfCenter) {
    rfCenter.style.background = "#fbf9f4"
    rfCenter.style.color = "#18191b"
    rfCenter.textContent = "📖"
  }
  if (pfCenter) {
    pfCenter.style.background = "#fbf9f4"
    pfCenter.style.color = "#18191b"
    pfCenter.textContent = "📄"
  }
  if (gfCenter) {
    gfCenter.style.background = "#fbf9f4"
    gfCenter.style.color = "#18191b"
    gfCenter.textContent = "🧭"
  }

  // Load signed cover if exists
  if (fullCoverPath) {
    getSignedCoverUrl(fullCoverPath).then((signedUrl) => {
      if (signedUrl && request === playRequest) {
        const bgCss = `url("${signedUrl}") center/cover no-repeat`
        if (miniThumb) { miniThumb.style.background = bgCss; $("mini-cover-icon").hidden = true }
        if (vinylCenter) { vinylCenter.style.background = bgCss; vinylCenter.textContent = "" }
        if (rfCenter) { rfCenter.style.background = bgCss; rfCenter.textContent = "" }
        if (pfCenter) { pfCenter.style.background = bgCss; pfCenter.textContent = "" }
        if (gfCenter) { gfCenter.style.background = bgCss; gfCenter.textContent = "" }
      }
    }).catch(() => {})
  }

  $("mini-player").hidden = false
  updatePlayButtonUI(false)

  const url = preparedUrl || (await stream(track))
  if (request !== playRequest) return
  const saved = progress(track)
  current = track
  currentBookFolder = track.path.slice(0, track.path.lastIndexOf("/"))
  pendingPosition = saved && !saved.completed ? Math.max(0, saved.position - 3) : 0

  audio.src = url
  audio.playbackRate = Number(prefs.speed) || 1
  audio.load()

  playAudio()
  prepareNext(request)
  setupReadalong(track, request)
  setupPdf(track, request)
  setupGuide(track, request)
  renderDrawerTrackList()
}

async function ensureCurrentLoaded(autoPlay = true) {
  if (current && audio.src) {
    if (autoPlay && audio.paused) playAudio()
    return
  }
  const journal = read(localStorage, JOURNAL, null)
  const candidateTrack = (journal?.account === account() ? journal.track : null) || libraryRecords()[0]?.track
  if (candidateTrack) {
    await loadTrack(candidateTrack)
    if (autoPlay) playAudio()
  } else if (entries.some((i) => !i.is_dir)) {
    const firstTrack = entries.find((i) => !i.is_dir)
    if (firstTrack) {
      await loadTrack(firstTrack)
      if (autoPlay) playAudio()
    }
  } else {
    notice("请先在书库中选择一本有声书。")
  }
}

function playAudio() {
  if (!current || !audio.src) return
  updatePlayButtonUI(true)
  audio.play().catch((error) => {
    updatePlayButtonUI(false)
    notice(error.name === "NotAllowedError" ? "音频就绪，轻点播放开始收听。" : "播放失败，请重试或检查网络。")
  })
}

function restorePosition() {
  if (
    !current ||
    !Number.isFinite(audio.duration) ||
    audio.duration <= 0 ||
    pendingPosition === null
  )
    return
  const target = Math.min(pendingPosition, Math.max(0, audio.duration - 1))
  try {
    audio.currentTime = target
    pendingPosition = null
    ready = true
    const resumeDesc = $("player-track-desc")
    if (resumeDesc) resumeDesc.textContent = target > 0 ? `已续播至 ${durationText(target)} (回退3秒)` : "已准备就绪"
  } catch {
    /* Stream seekable */
  }
}

function seek(seconds) {
  invalidateReadalong()
  if (ready && Number.isFinite(audio.duration)) {
    audio.currentTime = Math.max(0, Math.min(audio.duration, seconds))
  }
}

function nextTrack() {
  if (!preparedNext) return
  const next = preparedNext
  loadTrack(
    next.track,
    Date.now() - next.preparedAt < 5 * 60 * 1000 ? next.url : undefined,
  ).catch(fail)
}

function updatePlayButtonUI(playing) {
  const playBtn = $("play")
  const miniPlayBtn = $("mini-play-btn")
  const rfBtn = $("readalong-floating-play-btn")
  const pfBtn = $("pdf-floating-play-btn")
  const gfBtn = $("guide-floating-play-btn")

  // Class-based CSS toggle ensures 100% reliable SVG icon switching
  if (playBtn) playBtn.classList.toggle("is-playing", playing)
  if (miniPlayBtn) miniPlayBtn.classList.toggle("is-playing", playing)
  if (rfBtn) rfBtn.classList.toggle("is-playing", playing)
  if (pfBtn) pfBtn.classList.toggle("is-playing", playing)
  if (gfBtn) gfBtn.classList.toggle("is-playing", playing)

  // Direct SVG hidden attributes fallback
  $("mini-play-icon").hidden = playing
  $("mini-pause-icon").hidden = !playing
  $("play-svg").hidden = playing
  $("pause-svg").hidden = !playing

  const rfPlay = $("rf-play-svg")
  const rfPause = $("rf-pause-svg")
  if (rfPlay && rfPause) {
    rfPlay.hidden = playing
    rfPause.hidden = !playing
  }
  const pfPlay = $("pf-play-svg")
  const pfPause = $("pf-pause-svg")
  if (pfPlay && pfPause) {
    pfPlay.hidden = playing
    pfPause.hidden = !playing
  }
  const gfPlay = $("gf-play-svg")
  const gfPause = $("gf-pause-svg")
  if (gfPlay && gfPause) {
    gfPlay.hidden = playing
    gfPause.hidden = !playing
  }

  const rfDisc = $("readalong-floating-disc")
  const pfDisc = $("pdf-floating-disc")
  const gfDisc = $("guide-floating-disc")
  if (playing) {
    $("mini-cover-thumb").classList.add("spinning")
    $("vinyl-disc").classList.add("spinning")
    if (rfDisc) rfDisc.classList.add("spinning")
    if (pfDisc) pfDisc.classList.add("spinning")
    if (gfDisc) gfDisc.classList.add("spinning")
  } else {
    $("mini-cover-thumb").classList.remove("spinning")
    $("vinyl-disc").classList.remove("spinning")
    if (rfDisc) rfDisc.classList.remove("spinning")
    if (pfDisc) pfDisc.classList.remove("spinning")
    if (gfDisc) gfDisc.classList.remove("spinning")
  }
}

function mediaSession() {
  if (!("mediaSession" in navigator) || !current) return
  const session = navigator.mediaSession
  const bookName = current.path.slice(ROOT.length).split("/").filter(Boolean)[1] || "有声书"
  session.metadata = new MediaMetadata({
    title: current.name.replace(AUDIO, ""),
    artist: "Rosemary Garden",
    album: bookName,
    artwork: [
      {
        src: new URL("./icon-512.png", import.meta.url).href,
        sizes: "512x512",
        type: "image/png",
      },
    ],
  })
  const actions = {
    play: playAudio,
    pause: () => audio.pause(),
    seekbackward: (event) => seek(audio.currentTime - (event.seekOffset || 15)),
    seekforward: (event) => seek(audio.currentTime + (event.seekOffset || 30)),
    seekto: (event) => seek(event.seekTime),
    nexttrack: nextTrack,
  }
  for (const [action, handler] of Object.entries(actions)) {
    try {
      session.setActionHandler(action, handler)
    } catch {
      /* Safari compatibility */
    }
  }
}

// Scrubber Slider Handlers
let isDraggingSlider = false
$("seek-slider").addEventListener("input", (e) => {
  isDraggingSlider = true
  const pct = Number(e.target.value) / 100
  if (Number.isFinite(audio.duration)) {
    $("scrubber-current").textContent = durationText(audio.duration * pct)
  }
})
$("seek-slider").addEventListener("change", (e) => {
  isDraggingSlider = false
  const pct = Number(e.target.value) / 100
  if (Number.isFinite(audio.duration)) {
    seek(audio.duration * pct)
  }
})

// Audio Element Events
audio.addEventListener("loadedmetadata", restorePosition)
audio.addEventListener("canplay", restorePosition)
audio.addEventListener("seeked", () => {
  if (readalongActive) syncReadalong(true)
})
audio.addEventListener("timeupdate", () => {
  if (Date.now() - lastSave >= 3000) saveProgress()
  if (
    ready &&
    "mediaSession" in navigator &&
    navigator.mediaSession.setPositionState &&
    Number.isFinite(audio.duration)
  ) {
    try {
      navigator.mediaSession.setPositionState({
        duration: audio.duration,
        playbackRate: audio.playbackRate,
        position: Math.min(audio.duration, audio.currentTime),
      })
    } catch {
      /* Stream duration readiness */
    }
  }

  // Update Mini and Scrubber Progress UI
  if (Number.isFinite(audio.duration) && audio.duration > 0) {
    const pct = (audio.currentTime / audio.duration) * 100
    $("mini-progress-fill").style.width = `${pct}%`
    if (!isDraggingSlider) {
      $("seek-slider").value = pct
      $("scrubber-current").textContent = durationText(audio.currentTime)
    }
    $("scrubber-duration").textContent = durationText(audio.duration)
  }

  if (readalongActive) syncReadalong()
})

audio.addEventListener("playing", () => {
  updatePlayButtonUI(true)
  const playingDesc = $("player-track-desc")
  if (playingDesc) playingDesc.textContent = "正在播放 · 进度自动保存"
  if ("audioSession" in navigator) {
    try {
      navigator.audioSession.type = "playback"
    } catch {
      /* Optional API */
    }
  }
  mediaSession()
  if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing"
})

audio.addEventListener("pause", () => {
  saveProgress(audio.ended)
  updatePlayButtonUI(false)
  if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "paused"
})

audio.addEventListener("ended", () => {
  saveProgress(true)
  if (sleepTimerMode === "track") {
    clearSleepTimer()
    notice("定时关闭：已播放完当前章节")
    return
  }
  if (preparedNext) nextTrack()
  else {
    const endDesc = $("player-track-desc")
    if (endDesc) endDesc.textContent = "全书已播完"
    render()
  }
})

audio.addEventListener("error", () => {
  if (current) notice("音频加载失败，请检查网络或重新选择。")
})

document.addEventListener("visibilitychange", () => {
  if (document.hidden) saveProgress(audio.ended)
  else if (userSync) scheduleUserSync()
})
window.addEventListener("pagehide", () => saveProgress(audio.ended))
window.addEventListener("online", () => { if (userSync) scheduleUserSync() })
setInterval(() => { if (userSync && !document.hidden) scheduleUserSync() }, 30000)

// Speed Control
function setSpeed(speedVal) {
  prefs.speed = Number(speedVal)
  audio.playbackRate = prefs.speed
  write(localStorage, PREF, prefs)
  $("speed-display").textContent = `${prefs.speed}×`
  document.querySelectorAll(".speed-opt").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.speed === String(speedVal))
  })
}

// Sleep Timer Control
function setSleepTimer(minutes) {
  clearSleepTimer()
  if (minutes === "track") {
    sleepTimerMode = "track"
    const timerLabel = $("timer-label")
    if (timerLabel) timerLabel.textContent = "播完关"
    notice("已设置：当前章节播放完毕后停止")
  } else {
    const mins = Number(minutes)
    if (mins > 0) {
      sleepTimerMode = "time"
      sleepTimerMinutes = mins
      sleepTimerTargetTime = Date.now() + mins * 60 * 1000
      sleepTimerId = setTimeout(() => {
        audio.pause()
        clearSleepTimer()
        notice("定时关闭：时间到，已暂停播放")
      }, mins * 60 * 1000)
      const timerLabel = $("timer-label")
      if (timerLabel) timerLabel.textContent = `${mins}分关`
      notice(`已开启定时关闭：${mins} 分钟后停止播放`)
    }
  }
  const timerBtn = $("btn-timer")
  if (timerBtn) timerBtn.classList.toggle("active", sleepTimerMode !== "none")
  document.querySelectorAll(".timer-opt").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.minutes === String(minutes))
  })
}

function clearSleepTimer() {
  if (sleepTimerId) clearTimeout(sleepTimerId)
  sleepTimerId = null
  sleepTimerMode = "none"
  sleepTimerMinutes = 0
  const timerLabel = $("timer-label")
  if (timerLabel) timerLabel.textContent = "定时"
  const timerBtn = $("btn-timer")
  if (timerBtn) timerBtn.classList.remove("active")
}

// Drawers (BottomSheet) Management
function openDrawer(drawerId) {
  $("drawer-mask").hidden = false
  $(drawerId).hidden = false
}
function closeAllDrawers() {
  $("drawer-mask").hidden = true
  $("chapter-drawer").hidden = true
  $("timer-drawer").hidden = true
  $("speed-drawer").hidden = true
}

// Chapter Drawer List Rendering
async function renderDrawerTrackList() {
  const container = $("drawer-track-list")
  container.replaceChildren()
  if (!currentBookFolder) return
  const tracks = (await list(currentBookFolder))
    .filter((i) => !i.is_dir)
    .sort((a, b) => a.name.localeCompare(b.name, "zh-CN", { numeric: true }))

  for (const t of tracks) {
    const row = document.createElement("div")
    row.className = "item-row"
    const card = document.createElement("div")
    card.className = "item-card"
    card.style.background = t.path === current?.path ? "var(--brand-blue-bg)" : "transparent"

    const info = document.createElement("div")
    info.className = "item-main-info"
    const name = document.createElement("h4")
    name.className = "item-name"
    name.textContent = t.name.replace(AUDIO, "")
    if (t.path === current?.path) name.style.color = "var(--brand-blue)"
    info.append(name)

    card.append(info)
    row.append(card)
    card.onclick = () => {
      closeAllDrawers()
      loadTrack(t)
    }
    container.append(row)
  }
}

// Readalong / EPUB Syncing
function findNearestSegment(timeline, time) {
  const res = resolvePlaybackSegment(timeline, time, 3.5)
  return res.nearest
}

function findSegment(timeline, time) {
  const res = resolvePlaybackSegment(timeline, time, 3.5)
  return res.segment
}

// Sentence-level fallback rows keep the containing paragraph as their primary
// anchor for compatibility, but expose the refined sentence anchor when one
// exists. Prefer that smaller DOM node for visual highlighting.
function readalongFragmentForSegment(seg, doc) {
  if (!seg) return ""
  const preferred = seg.sourceSentenceFragment || seg.fragment || ""
  if (doc?.getElementById(preferred)) return preferred
  return seg.fragment || preferred
}

async function setupReadalong(track, request) {
  invalidateReadalong()
  const releaseBadge = $("readalong-release-status")
  if (releaseBadge) {
    releaseBadge.textContent = "跟读模式"
    releaseBadge.title = ""
  }
  readalongManifest = null
  readalongTimeline = []
  currentSegment = null
  currentDocPath = ""
  $("dock-readalong").hidden = true

  try {
    const parent = track.path.slice(0, track.path.lastIndexOf("/"))
    // Support multi-volume sub-directory audiobooks (e.g. Great Mental Models/Volume 1/...)
    // Check current track directory first; if not found, fallback to parent directory
    const candidates = [parent]
    const grandParent = parent.slice(0, parent.lastIndexOf("/"))
    if (grandParent && isWithinRoot(grandParent)) {
      candidates.push(grandParent)
    }

    let manifest = null
    let validParent = ""

    for (const p of candidates) {
      const manifestPath = `${p}/readalong/readalong.manifest.json`
      let m = manifestMemoryCache.get(manifestPath)
      if (!m) {
        const info = await api("fs/get", {
          path: manifestPath,
          password: directoryPassword,
        }).catch(() => null)
        if (info) {
          const manifestUrl = mediaUrl(endpoint, { path: manifestPath }, info.sign)
          m = await fetch(manifestUrl, { cache: "no-store" }).then((r) => r.json()).catch(() => null)
          if (m && m.schemaVersion === 1) {
            manifestMemoryCache.set(manifestPath, m)
          }
        }
      }
      if (m?.schemaVersion === 1 && m.readalongEnabled === false) {
        closeReadalong()
        $("readalong-frame").srcdoc = ""
        readalongFrameDocPath = ""
        readalongFrameReady = null
        if (releaseBadge) releaseBadge.hidden = true

        // 纯听书如果不跟读，但目录下有 EPUB，播放界面依然显示 EPUB 按钮供浏览！
        const listData = await api("fs/list", { path: p, password: directoryPassword, page: 1, per_page: 50 }).catch(() => null)
        const epubItem = listData?.content?.find((item) => !item.is_dir && /\.epub$/i.test(item.name))
        if (epubItem) {
          $("dock-readalong").hidden = false
          const label = $("dock-readalong").querySelector("span")
          if (label) label.textContent = "EPUB"
          $("dock-readalong").title = "EPUB 电子书浏览"
          $("dock-readalong").onclick = () => {
            const epubUrl = mediaUrl(endpoint, { path: `${p}/${epubItem.name}` }, epubItem.sign)
            window.open(epubUrl, "_blank")
          }
        } else {
          $("dock-readalong").hidden = true
        }
        return
      }
      if (m && m.schemaVersion === 1) {
        manifest = m
        validParent = p
        break
      }
    }

    if (!manifest || request !== playRequest) return

    const assetBase = /^[a-f0-9]{32}$/.test(manifest.assetRevision || "")
      ? `${validParent}/.readalong_revisions/${manifest.assetRevision}`
      : `${validParent}/readalong`
    readalongManifest = manifest
    if (releaseBadge && manifest.practicalRelease) {
      const release = manifest.practicalRelease
      releaseBadge.textContent = release.decision === "PUBLISH_WITH_GAPS" ? "跟读 · 有局部缺口" : "跟读 · 实用版"
      releaseBadge.title = "段落级个人实用版本，非逐词声学认证；未映射处不高亮，下一可靠位置恢复。"
    }
    readalongParentPath = validParent
    readalongAssetBase = assetBase

    // Relative paths distinguish identically named tracks in separate volumes.
    const relative = track.path.slice(validParent.length + 1)
    const source = manifest.audioSources?.find((s) => s.id === relative || s.alistPath === track.path || s.id === track.name || s.name === track.name)
    // The manifest is sufficient to expose the EPUB button. Large books may
    // load their current track timeline shard asynchronously below.
    $("dock-readalong").hidden = !Boolean(manifest.alignedDocument || manifest.textRoot)

    let timelinePath = `${assetBase}/${manifest.timeline || "timeline.json"}`
    if (manifest.timelineFormat === "per-audio-source-v1") {
      const indexPath = `${assetBase}/${manifest.timelineIndex || manifest.timeline || "timeline-index.json"}`
      let index = timelineMemoryCache.get(indexPath)
      if (!index) {
        const indexInfo = await api("fs/get", { path: indexPath, password: directoryPassword }).catch(() => null)
        if (!indexInfo || request !== playRequest) return
        const indexUrl = mediaUrl(endpoint, { path: indexPath }, indexInfo.sign)
        index = await fetch(indexUrl, { cache: "no-store" }).then((r) => r.json()).catch(() => null)
        if (index?.files) timelineMemoryCache.set(indexPath, index)
      }
      const shard = source && timelinePathForSource(manifest, index, source.id)
      if (!shard) return
      timelinePath = `${assetBase}/${shard}`
    }

    let timeline = timelineMemoryCache.get(timelinePath)
    if (!timeline) {
      const timelineInfo = await api("fs/get", { path: timelinePath, password: directoryPassword }).catch(() => null)
      if (!timelineInfo || request !== playRequest) return
      const timelineUrl = mediaUrl(endpoint, { path: timelinePath }, timelineInfo.sign)
      timeline = await fetch(timelineUrl, { cache: "no-store" }).then((r) => r.json()).catch(() => null)
      if (Array.isArray(timeline)) timelineMemoryCache.set(timelinePath, timeline)
    }
    if (request !== playRequest || !Array.isArray(timeline)) return

    let matched = source ? timeline.filter((s) => s.audioSourceId === source.id || s.audioSourceId === track.name) : []
    if (!matched.length) {
      matched = timeline.filter((s) => s.audioSourceId === track.name || s.audioSourceId === relative)
    }
    if (!matched.length && !timeline.some((s) => s.audioSourceId)) {
      matched = timeline
    }

    // Always sort filtered segments strictly by start time to guarantee binary search correctness
    readalongTimeline = matched.sort((a, b) => (Number(a.start) || 0) - (Number(b.start) || 0))

    // As long as the book has readalong documents, keep the EPUB dock button accessible
    const hasEpubDocument = Boolean(manifest.alignedDocument || readalongTimeline.length || manifest.textRoot)
    $("dock-readalong").hidden = !hasEpubDocument
    if (hasEpubDocument) {
      $("dock-readalong").onclick = openReadalong
      const label = $("dock-readalong").querySelector("span")
      if (label) label.textContent = "跟读"
      $("dock-readalong").title = "EPUB 音文跟读"
    }

    // If readalong view is active, immediately sync to new chapter's first segment
    if (readalongActive) {
      syncReadalong(true)
    }
  } catch {
    $("dock-readalong").hidden = true
  }
}

async function setupPdf(track, request) {
  currentPdfPath = ""
  currentPdfName = ""
  $("dock-pdf").hidden = true

  try {
    const parent = track.path.slice(0, track.path.lastIndexOf("/"))
    const candidates = [parent]
    const grandParent = parent.slice(0, parent.lastIndexOf("/"))
    if (grandParent && isWithinRoot(grandParent)) {
      candidates.push(grandParent)
    }

    let pdfItem = null
    let validParent = ""

    for (const p of candidates) {
      const data = await api("fs/list", {
        path: p,
        password: directoryPassword,
        page: 1,
        per_page: 50,
        refresh: false,
      }).catch(() => null)
      if (data?.content) {
        pdfItem = data.content.find((item) => !item.is_dir && PDF.test(item.name))
        if (pdfItem) {
          validParent = p
          break
        }
      }
    }

    if (!pdfItem || request !== playRequest) return
    currentPdfPath = `${validParent}/${pdfItem.name}`
    currentPdfName = pdfItem.name
    $("dock-pdf").hidden = false
  } catch {
    $("dock-pdf").hidden = true
  }
}

async function openPdfViewer() {
  if (!currentPdfPath) return
  pdfViewerActive = true
  $("pdf-viewer").hidden = false
  $("pdf-title").textContent = currentPdfName || "配套讲义 / PDF 电子书"
  $("pdf-loading").hidden = false
  updatePlayButtonUI(!audio.paused)

  try {
    const info = await api("fs/get", { path: currentPdfPath, password: directoryPassword })
    const pdfUrl = mediaUrl(endpoint, { path: currentPdfPath }, info.sign)
    $("pdf-frame").src = `./pdf-viewer.html?file=${encodeURIComponent(pdfUrl)}`
    $("pdf-external").href = pdfUrl
  } finally {
    $("pdf-loading").hidden = true
  }
}

function closePdfViewer() {
  pdfViewerActive = false
  $("pdf-viewer").hidden = true
  $("pdf-frame").removeAttribute("src")
}

async function setupGuide(track, request) {
  currentGuidePath = ""
  currentGuideTitle = ""
  const dockGuide = $("dock-guide")
  if (dockGuide) {
    dockGuide.disabled = true
    dockGuide.classList.add("disabled")
    dockGuide.title = "暂无深度导读"
  }

  try {
    const parent = track.path.slice(0, track.path.lastIndexOf("/"))
    const candidates = [parent]
    const grandParent = parent.slice(0, parent.lastIndexOf("/"))
    if (grandParent && isWithinRoot(grandParent)) {
      candidates.push(grandParent)
    }

    let guideItem = null
    let validParent = ""

    for (const p of candidates) {
      const data = await api("fs/list", {
        path: p,
        password: directoryPassword,
        page: 1,
        per_page: 50,
        refresh: false,
      }).catch(() => null)
      if (data?.content) {
        guideItem = data.content.find((item) => !item.is_dir && /^guide\.html$/i.test(item.name))
        if (guideItem) {
          validParent = p
          break
        }
      }
    }

    if (!guideItem || request !== playRequest) return
    currentGuidePath = `${validParent}/${guideItem.name}`
    currentGuideTitle = validParent.slice(validParent.lastIndexOf("/") + 1) || "深度导读"
    if (dockGuide) {
      dockGuide.disabled = false
      dockGuide.classList.remove("disabled")
      dockGuide.title = "书籍深度导读"
    }
  } catch {
    if (dockGuide) {
      dockGuide.disabled = true
      dockGuide.classList.add("disabled")
      dockGuide.title = "暂无深度导读"
    }
  }
}

async function openGuideViewer(explicitPath, explicitTitle) {
  const targetPath = explicitPath || currentGuidePath
  if (!targetPath) return
  guideViewerActive = true
  $("guide-viewer").hidden = false
  const titleText = explicitTitle || currentGuideTitle || $("banner-title")?.textContent || "书籍"
  $("guide-title").textContent = `${titleText} · 深度导读`
  $("guide-loading").hidden = false
  updatePlayButtonUI(!audio.paused)

  try {
    const info = await api("fs/get", { path: targetPath, password: directoryPassword })
    const guideUrl = mediaUrl(endpoint, { path: targetPath }, info.sign)
    $("guide-external").href = guideUrl
    const res = await fetch(guideUrl)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const htmlText = await res.text()
    if (!htmlText.trim()) throw new Error("导读内容为空")
    $("guide-frame").srcdoc = htmlText
  } catch (err) {
    notice(`加载导读失败: ${err.message}`)
    closeGuideViewer()
  } finally {
    $("guide-loading").hidden = true
  }
}

function closeGuideViewer() {
  guideViewerActive = false
  $("guide-viewer").hidden = true
  $("guide-frame").removeAttribute("srcdoc")
}

function openReadalong() {
  if (!readalongManifest) return
  readalongActive = true
  $("readalong").hidden = false
  updatePlayButtonUI(!audio.paused)

  // Determine initial document path
  // Open on the document of the current playback position: loading the track's first
  // document first and then switching showed an extra page on every open.
  let targetDoc = ""
  if (readalongTimeline.length) {
    const start = resolvePlaybackSegment(readalongTimeline, audio.currentTime, 3.5)
    targetDoc = (start.segment || start.nearest || readalongTimeline[0])?.document || ""
  }
  if (!targetDoc) targetDoc = currentDocPath || readalongManifest.alignedDocument || ""

  const locateBtn = $("readalong-locate")
  if (locateBtn && !readalongTimeline.length) {
    locateBtn.hidden = true
  }

  if (targetDoc && currentDocPath !== targetDoc) {
    invalidateReadalong()
    const epoch = readalongLoadEpoch
    loadReadalongDoc(targetDoc, epoch).then((ok) => {
      if (ok && epoch === readalongLoadEpoch) {
        currentDocPath = targetDoc
        syncReadalong(true)
      }
    }).catch(() => {})
  } else {
    syncReadalong(true)
  }
}

function closeReadalong() {
  invalidateReadalong()
  readalongActive = false
  $("readalong").hidden = true
}

function loadReadalongDoc(docRelPath, expectedEpoch) {
  return new Promise(async (resolve) => {
    if (expectedEpoch !== readalongLoadEpoch) return resolve(false)
    readalongPendingCancel?.()
    readalongPendingCancel = () => resolve(false)
    const base = typeof readalongAssetBase === "string" && readalongAssetBase
      ? readalongAssetBase : `${readalongParentPath}/readalong`
    const docPath = `${base}/${docRelPath}`
    let html = readalongDocCache.get(docPath)
    if (!html) {
      $("readalong-loading").hidden = false
      try {
        const info = await api("fs/get", { path: docPath, password: directoryPassword })
        const url = mediaUrl(endpoint, { path: docPath }, info.sign)
        html = sanitizeReadalongHtml(await fetch(url).then((r) => r.text()))
        if (expectedEpoch !== readalongLoadEpoch) return resolve(false)
        readalongDocCache.set(docPath, html)
      } catch {
        /* fetch error */
      } finally {
        if (expectedEpoch === readalongLoadEpoch) $("readalong-loading").hidden = true
      }
    }

    // Guard: If a newer load request arrived while fetching, abort before touching iframe DOM
    if (expectedEpoch !== readalongLoadEpoch) {
      return resolve(false)
    }

    if (!html) return resolve(false)

    const frame = $("readalong-frame")

    // The same document is assigned to the frame at most once. Re-assigning srcdoc aborts the
    // in-flight render; with sync ticks every ~250ms that looped forever (v25 regression).
    if (readalongFrameDocPath !== docPath || !readalongFrameReady) {
      readalongFrameDocPath = docPath
      readalongFrameReady = new Promise((done) => {
        let settled = false
        const finish = (ok) => {
          if (settled) return
          settled = true
          if (!ok && readalongFrameDocPath === docPath) {
            readalongFrameDocPath = ""
            readalongFrameReady = null
          }
          done(ok)
        }
        frame.onload = () => {
          try { attachReadalongFrameHandlers(frame) } catch { /* sandbox */ }
          finish(true)
        }
        frame.srcdoc = html
        const timeout = setTimeout(() => finish(false), 10000)
        timeout.unref?.()
      })
    }
    const ok = await readalongFrameReady
    resolve(ok && expectedEpoch === readalongLoadEpoch)
  })
}

function attachReadalongFrameHandlers(frame) {
  const doc = frame.contentDocument
  if (!doc) return
  const size = $("readalong-size").value || "17"
  if (doc.body) doc.body.style.fontSize = `${size}px`

  const onUserScroll = () => {
    if (!readalongFollowing) return
    readalongFollowing = false
    const followBtn = $("readalong-follow")
    if (followBtn) followBtn.textContent = "跟随：暂停"
    const locateBtn = $("readalong-locate")
    if (locateBtn) locateBtn.hidden = false
  }

  frame.contentWindow?.addEventListener("wheel", onUserScroll, { passive: true })
  frame.contentWindow?.addEventListener("touchmove", onUserScroll, { passive: true })

  doc.addEventListener("click", (e) => {
    const target = e.target.closest("[id]")
    if (!target || !target.id) return
    const seg = readalongTimeline.find((s) => s.fragment === target.id || s.sourceSentenceFragment === target.id)
    if (seg) {
      seek(seg.start)
      readalongFollowing = true
      const followBtn = $("readalong-follow")
      if (followBtn) followBtn.textContent = "跟随：开"
      const locateBtn = $("readalong-locate")
      if (locateBtn) locateBtn.hidden = true
      syncReadalong(true)
    }
  })
}

let readalongLoadEpoch = 0
let readalongTargetKey = ""
let readalongPendingCancel = null
// EPUB pages reference stylesheets, scripts and images by paths relative to the EPUB. Inside the
// srcdoc frame those resolve against the player's origin, where they never exist, and the frame's
// load event waits for every one of those failing requests (seconds on Wiley-style books). They have
// never rendered, so drop them before injection; text and fragment ids are untouched.
function sanitizeReadalongHtml(html) {
  try {
    const doc = new DOMParser().parseFromString(html, "text/html")
    doc.querySelectorAll("link, script, iframe, object, embed, video, audio, source").forEach((el) => el.remove())
    doc.querySelectorAll("img[src]").forEach((el) => {
      el.setAttribute("data-epub-src", el.getAttribute("src"))
      el.removeAttribute("src")
      el.removeAttribute("srcset")
    })
    doc.querySelectorAll("image").forEach((el) => {
      for (const attr of ["href", "xlink:href"]) {
        if (el.hasAttribute(attr)) {
          el.setAttribute("data-epub-href", el.getAttribute(attr))
          el.removeAttribute(attr)
        }
      }
    })
    return "<!DOCTYPE html>" + doc.documentElement.outerHTML
  } catch {
    return html
  }
}

let readalongFrameDocPath = ""
let readalongFrameReady = null

function invalidateReadalong() {
  ++readalongLoadEpoch
  readalongTargetKey = ""
  readalongPendingCancel?.()
  readalongPendingCancel = null
}

async function syncReadalong(forceScroll = false) {
  if (!readalongActive || !current) return
  if (!readalongTimeline.length) return

  const curTime = audio.currentTime
  const syncResult = resolvePlaybackSegment(readalongTimeline, curTime, 3.5)
  const isPlayingActive = (syncResult.state === SYNC_STATE.ACTIVE || syncResult.state === SYNC_STATE.SHORT_PAUSE)
  let seg = syncResult.segment

  // New playback intent cancels pending loads even when no new document is needed.
  const targetKey = `${readalongParentPath}|${current?.path || ""}|${seg?.document || ""}|${seg?.sourceSentenceFragment || seg?.fragment || ""}|${syncResult.state}`
  if (targetKey !== readalongTargetKey) {
    invalidateReadalong()
    readalongTargetKey = targetKey
  }
  const epoch = readalongLoadEpoch

  // If not currently in an active segment (UNMAPPED, AFTER_END, BEFORE_START, EMPTY), clear highlight
  if (!isPlayingActive) {
    if (!forceScroll || syncResult.state === SYNC_STATE.EMPTY) {
      const frame = $("readalong-frame")
      try {
        const doc = frame?.contentDocument
        if (doc) {
          doc.querySelectorAll(".readalong-active").forEach((el) => el.classList.remove("readalong-active"))
        }
      } catch {}
      currentSegment = null
      return
    } else {
      seg = syncResult.nearest
    }
  }

  if (!seg) return

  if (seg === currentSegment && !forceScroll) return

  if (currentDocPath !== seg.document) {
    const ok = await loadReadalongDoc(seg.document, epoch)
    if (!ok || epoch !== readalongLoadEpoch) {
      return
    }
    currentDocPath = seg.document
  }
  if (epoch !== readalongLoadEpoch) return
  if (!isPlayingActive) {
    const doc = $("readalong-frame").contentDocument
    doc?.querySelectorAll(".readalong-active").forEach((el) => el.classList.remove("readalong-active"))
    doc?.getElementById(readalongFragmentForSegment(seg, doc))?.scrollIntoView({ block: "center" })
    currentSegment = null
    return
  }
  currentSegment = seg

  const frame = $("readalong-frame")
  const highlightElement = () => {
    if (epoch !== readalongLoadEpoch || !readalongActive) return false
    try {
      const doc = frame.contentDocument
      if (!doc) return false
      const targetElem = doc.getElementById(readalongFragmentForSegment(seg, doc))
      if (targetElem) {
        doc.querySelectorAll(".readalong-active").forEach((el) => el.classList.remove("readalong-active"))
        targetElem.classList.add("readalong-active")
        if (readalongFollowing || forceScroll) {
          targetElem.scrollIntoView({ block: "center", behavior: "smooth" })
        }
        return true
      }
      return false
    } catch {
      return false
    }
  }

  if (!highlightElement()) {
    setTimeout(highlightElement, 80)
    setTimeout(highlightElement, 250)
  }

  if (readalongManifest?.chapters?.length) {
    const chap = readalongManifest.chapters.find(
      (c) => audio.currentTime >= c.start && audio.currentTime < c.end,
    )
    if (chap && chap.title) {
      $("readalong-chapter-title").textContent = chap.title.trim()
    }
  }
}

// Safe event listener helper
const on = (id, event, fn) => {
  const el = $(id)
  if (el) el.addEventListener(event, fn)
}

// User Interaction Listeners
on("play", "click", () => (audio.paused ? playAudio() : audio.pause()))
on("mini-play-btn", "click", async (e) => {
  e.stopPropagation()
  if (!current || !audio.src) {
    await ensureCurrentLoaded(true)
  } else {
    audio.paused ? playAudio() : audio.pause()
  }
})
on("rewind", "click", () => seek(audio.currentTime - 15))
on("forward", "click", () => seek(audio.currentTime + 30))
on("btn-next", "click", nextTrack)

// Toggle Full Player / Mini Player
on("mini-content-area", "click", async () => {
  if (!current || !audio.src) {
    await ensureCurrentLoaded(false)
  }
  $("full-player").hidden = false
})
on("mini-list-btn", "click", (e) => {
  e.stopPropagation()
  openDrawer("chapter-drawer")
})
on("player-share-btn", "click", attempt(async () => {
  if (!current || !userSync) throw new Error("请先登录并选择音轨，再添加书签。")
  const id = crypto.randomUUID()
  await userSync.save("bookmark", id, { track: current, position: audio.currentTime, createdAt: Date.now(), deleted: false })
  await renderSyncItems()
  scheduleUserSync()
  notice("已添加书签，可在“我的”中查看。")
}))
on("player-collapse-btn", "click", () => {
  $("full-player").hidden = true
})

// Floating Vinyl Player in Readalong & PDF Panels (WeRead Style: Click vinyl to play/pause)
const toggleFloatingPlay = (e) => {
  if (e) e.stopPropagation()
  if (audio.paused) {
    playAudio()
  } else {
    audio.pause()
    updatePlayButtonUI(false)
  }
}

const openFullPlayerFromReader = () => {
  closeReadalong()
  closePdfViewer()
  closeGuideViewer()
  $("full-player").hidden = false
}

on("readalong-floating-player", "click", toggleFloatingPlay)
on("readalong-floating-play-btn", "click", toggleFloatingPlay)
on("readalong-title-btn", "click", openFullPlayerFromReader)

on("pdf-floating-player", "click", toggleFloatingPlay)
on("pdf-floating-play-btn", "click", toggleFloatingPlay)
on("pdf-title-btn", "click", openFullPlayerFromReader)

on("guide-floating-player", "click", toggleFloatingPlay)
on("guide-floating-play-btn", "click", toggleFloatingPlay)
on("guide-title-btn", "click", openFullPlayerFromReader)
on("guide-close", "click", closeGuideViewer)

// Dock buttons in Full Player
on("dock-chapters", "click", () => openDrawer("chapter-drawer"))
on("dock-guide", "click", () => {
  if (currentGuidePath) {
    openGuideViewer(currentGuidePath, currentGuideTitle)
  }
})
on("dock-readalong", "click", openReadalong)
on("dock-pdf", "click", openPdfViewer)
on("btn-speed", "click", () => openDrawer("speed-drawer"))
on("btn-timer", "click", () => openDrawer("timer-drawer"))

// Banner header click in Book Folder: open guide.html if available
on("folder-summary", "click", () => {
  if (currentFolderGuidePath) {
    openGuideViewer(currentFolderGuidePath, $("banner-title")?.textContent)
  }
})

// Drawer Closers
on("drawer-mask", "click", closeAllDrawers)
on("drawer-close", "click", closeAllDrawers)
on("timer-close", "click", closeAllDrawers)
on("speed-close", "click", closeAllDrawers)

// Speed Drawer Option click
document.querySelectorAll(".speed-opt").forEach((btn) => {
  btn.onclick = () => {
    setSpeed(btn.dataset.speed)
    closeAllDrawers()
  }
})

// Timer Drawer Option click
document.querySelectorAll(".timer-opt").forEach((btn) => {
  btn.onclick = () => {
    setSleepTimer(btn.dataset.minutes)
    closeAllDrawers()
  }
})

// Readalong Top Bar
on("readalong-close", "click", closeReadalong)
on("pdf-close", "click", closePdfViewer)
on("readalong-locate", "click", () => {
  readalongFollowing = true
  const followBtn = $("readalong-follow")
  if (followBtn) followBtn.textContent = "跟随：开"
  $("readalong-locate").hidden = true
  syncReadalong(true)
})
on("readalong-size", "change", () => {
  const size = $("readalong-size").value
  const doc = $("readalong-frame").contentDocument
  if (doc?.body) doc.body.style.fontSize = `${size}px`
})

// Navigation & Search
on("nav-back-btn", "click", navigateUp)
on("search", "input", (e) => {
  const clr = $("search-clear")
  if (clr) clr.hidden = !e.target.value
  scheduleGlobalSearch(e.target.value)
})
on("search-clear", "click", () => {
  $("search").value = ""
  $("search-clear").hidden = true
  scheduleGlobalSearch("")
})
on("sort", "change", render)

// TabBar Navigation (书架 / 书库 / 我的)
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"))
    btn.classList.add("active")
    const targetId = btn.dataset.target
    document.querySelectorAll(".tab-view").forEach((view) => {
      view.hidden = view.id !== targetId
    })
    if (targetId === "shelf-view") renderShelf()
    else if (targetId === "library-view") render()
    else if (targetId === "profile-view") updateProfileStats()
  }
})

// Dialog & Settings
function openSettingsModal() {
  const dlg = $("settings")
  if (!dlg) return
  const userInp = $("username")
  const pwdInp = $("password")
  if (userInp && prefs.username && !userInp.value) {
    userInp.value = prefs.username
  }
  $("login-status").textContent = ""
  dlg.showModal()
  requestAnimationFrame(() => {
    if (userInp && !userInp.value) {
      userInp.focus()
    } else if (pwdInp) {
      pwdInp.focus()
    }
  })
}

on("settings-open", "click", openSettingsModal)
on("open-conn-btn", "click", openSettingsModal)
on("settings-close", "click", () => $("settings")?.close())
$("settings")?.addEventListener("click", (e) => {
  if (e.target === $("settings")) $("settings").close()
})

on("connection-form", "submit", async (event) => {
  event.preventDefault()
  const loginBtn = $("login")
  if (loginBtn) loginBtn.disabled = true
  $("login-status").textContent = "正在登录…"
  try {
    const mode = $("network")?.value || "auto"
    const nextEndpoint = resolveEndpoint(mode)
    saveProgress()
    audio.pause()
    ++playRequest
    current = null
    ready = false
    $("mini-player").hidden = true
    $("full-player").hidden = true

    const username = $("username").value.trim()
    const password = $("password").value
    if (!password && (!auth || auth.username !== username || auth.endpoint !== nextEndpoint))
      throw new Error("请输入 AList 密码。")
    endpoint = nextEndpoint
    if (password) {
      const data = await api(
        "auth/login",
        { username, password },
        "",
      )
      auth = { token: data.token, deviceKey: data.device_key, username, endpoint }
    }
    prefs = { ...prefs, mode, username }
    write(localStorage, PREF, prefs)
    remove(localStorage, AUTH)
    remove(sessionStorage, AUTH)
    write($("remember").checked ? localStorage : sessionStorage, AUTH, auth)
    $("password").value = ""
    $("settings")?.close()
    startUserSync()
    notice("登录成功，正在同步书库...")
    await browse(ROOT)
  } catch (error) {
    $("login-status").textContent = error.message
  } finally {
    if (loginBtn) loginBtn.disabled = false
  }
})

on("logout", "click", () => {
  logout()
  $("settings")?.close()
})
on("logout-btn", "click", logout)

function logout() {
  saveProgress()
  syncAccount = ""
  userSync = null
  clearTimeout(syncTimer)
  $("sync-status").textContent = "未连接"
  $("sync-items").replaceChildren()
  closeReadalong()
  closePdfViewer()
  audio.pause()
  ++playRequest
  ++browseRequest
  current = null
  ready = false
  audio.removeAttribute("src")
  audio.load()
  auth = null
  directoryPassword = ""
  entries = []
  clearTimeout(searchTimer)
  searchAbort?.abort()
  globalSearchState = { query: "", results: [], loading: false, error: "" }
  prefs.username = ""
  write(localStorage, PREF, prefs)
  remove(localStorage, AUTH)
  remove(sessionStorage, AUTH)
  for (const id of ["password", "otp", "username", "folder-password"]) {
    const el = $(id)
    if (el) el.value = ""
  }
  $("mini-player").hidden = true
  $("full-player").hidden = true
  notice("已清除本机登录记录")
  render()
}

on("export-btn", "click", () => {
  saveProgress()
  const blob = new Blob(
    [JSON.stringify({ version: 1, records: libraryRecords() }, null, 2)],
    { type: "application/json" },
  )
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `garden-listen-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
})

on("import", "change", attempt(async () => {
  const imp = $("import")
  const file = imp?.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) throw new Error("记录文件过大，请选择小于 10 MB 的备份。")
  const data = JSON.parse(await file.text())
  if (data.version !== 1 || !Array.isArray(data.records))
    throw new Error("不是有效的听书记录文件。")
  const candidates = data.records.map((record) => {
    const t = record.track
    if (
      !t ||
      !isWithinRoot(t.path) ||
      typeof t.name !== "string" ||
      !AUDIO.test(t.name) ||
      !Number.isFinite(record.duration) ||
      record.duration <= 0 ||
      !Number.isFinite(record.position) ||
      record.position < 0 ||
      record.position > record.duration ||
      !Number.isFinite(record.updatedAt)
    )
      throw new Error("备份中有无效的收听记录，尚未导入。")
    const track = {
      path: t.path,
      name: t.name,
      size: Number(t.size) || 0,
      modified: String(t.modified || ""),
      is_dir: false,
    }
    return {
      key: JSON.stringify([account(), trackId(track)]),
      account: account(),
      id: trackId(track),
      track,
      position: record.position,
      duration: record.duration,
      updatedAt: record.updatedAt,
      completed: record.completed === true,
      speed: Number(record.speed) || 1,
    }
  })
  for (const record of candidates) {
    const existing = records.find((item) => item.key === record.key)
    if (!existing || existing.updatedAt < record.updatedAt) {
      persist(record)
      if (userSync && syncAccount === account()) await userSync.save("progress", record.track.path, record)
    }
  }
  if (userSync) scheduleUserSync()
  render()
  notice(`已成功合并 ${candidates.length} 条收听记录`)
  if (imp) imp.value = ""
}))

// Initialize App
async function init() {
  setSpeed(prefs.speed || 1)
  try {
    await openDatabase()
    syncStore = await openSyncStore()
  } catch {
    notice("无法打开本地存储，收听记录可能无法持久保存。")
  }

  // Auto load recent playback from journal if present
  const journal = read(localStorage, JOURNAL, null)
  if (journal && journal.account === account() && journal.track) {
    // Mini player placeholder
    $("mini-title").textContent = journal.track.name.replace(AUDIO, "")
    const parentDir = journal.track.path.slice(0, journal.track.path.lastIndexOf("/"))
    const bookName = parentDir.split("/").filter(Boolean).pop() || "有声书"
    $("mini-subtitle").textContent = `继续听 · ${bookName}`

    // Set artwork
    const fullCoverPath = resolveBookCoverPath(parentDir, bookName)
    const miniThumb = $("mini-cover-thumb")
    if (miniThumb) {
      miniThumb.style.background = "#32353a"
      const miniIcon = $("mini-cover-icon")
      if (miniIcon) { miniIcon.hidden = false; miniIcon.textContent = "♫" }
      if (fullCoverPath) {
        getSignedCoverUrl(fullCoverPath).then((signedUrl) => {
          if (signedUrl) {
            miniThumb.style.background = `url("${signedUrl}") center/cover no-repeat`
            if (miniIcon) miniIcon.hidden = true
          }
        }).catch(() => {})
      }
    }
    $("mini-player").hidden = false
  }

  // First render initial shell state so UI is never stuck on "loading"
  render()

  if (auth?.token) {
    browse(ROOT).catch((err) => {
      console.warn("Initial browse failed:", err)
      $("list-status").textContent = "未连接书库，请点击右上角设置登录"
      render()
    }).finally(() => {
      // The library listing determines the first usable screen. Avoid competing
      // with it for the same external connection during first paint.
      startUserSync()
    })
  } else {
    $("list-status").textContent = "未连接家庭书库，请点击右上角设置登录"
    render()
    // Open settings dialog if not connected
    const settingsDlg = $("settings")
    if (settingsDlg && typeof settingsDlg.showModal === "function") {
      try {
        settingsDlg.showModal()
      } catch {
        /* Dialog might already be open */
      }
    }
  }

  // Register Service Worker with cache busting & auto-reload on update
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js?v=32").then((reg) => {
      reg.update().catch(() => {})
    }).catch(() => {})
    let refreshing = false
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (!refreshing) {
        refreshing = true
        window.location.reload()
      }
    })
  }
}

init()
