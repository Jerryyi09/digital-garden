import { ROOT, resolveEndpoint, isWithinRoot, trackId, mediaUrl } from "./config.js"
import { getBookSummary, getBookCover, getJacketColors } from "./summaries.js"

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

// Readalong & PDF State
let readalongManifest = null
let readalongTimeline = []
let readalongParentPath = ""
let readalongDocCache = new Map()
let readalongActive = false
let readalongFollowing = true
let currentSegment = null
let currentDocPath = ""
let currentPdfPath = ""
let currentPdfName = ""
let pdfViewerActive = false

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

async function getSignedCoverUrl(fullImgPath) {
  if (!fullImgPath) return ""
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
}

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
  if (!isWithinRoot(path)) throw new Error("只能浏览 /750HD/有声书 下的目录")
  const content = []
  let hasReadalongInFolder = false
  let pdfInFolder = null
  let imageInFolder = null
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
        hasReadalong: hasReadalongInFolder && !item.is_dir,
        hasPdf: Boolean(pdfInFolder) && !item.is_dir,
        pdfName: pdfInFolder,
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

    const prog = document.createElement("div")
    prog.className = "shelf-card-progress"
    const percent = Math.min(100, Math.floor((record.position / (record.duration || 1)) * 100))
    prog.textContent = record.completed ? "已读完" : `已听 ${percent}%`

    card.append(cover, title, prog)
    card.onclick = attempt(() => loadTrack(record.track))
    shelfContainer.append(card)
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
    $("folder-summary-text").textContent = currentSummary || "暂无简介，点击章节即可播放。"

    // Render Banner Cover
    const bannerCoverWrap = document.querySelector(".banner-cover-wrap")
    if (bannerCoverWrap) {
      bannerCoverWrap.replaceChildren()
      const coverFile = getBookCover(currentDirName) || entries.find((i) => i.coverFile)?.coverFile
      const fullCoverPath = coverFile ? `${folder}/${coverFile}` : ""
      bannerCoverWrap.append(createBookCoverElement(currentDirName, "size-banner", fullCoverPath))
    }
    $("folder-summary").hidden = false
  } else {
    $("folder-summary").hidden = true
  }

  const query = $("search").value.trim().toLocaleLowerCase()
  let items = [...entries]
  if (query) {
    items = items.filter((item) => item.name.toLocaleLowerCase().includes(query))
  }

  items.sort(
    (a, b) =>
      Number(b.is_dir) - Number(a.is_dir) ||
      ($("sort").value === "modified"
        ? (Date.parse(b.modified) || 0) - (Date.parse(a.modified) || 0)
        : a.name.localeCompare(b.name, "zh-CN", { numeric: true })),
  )

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
      desc.textContent = getBookSummary(item.name) || "点击浏览有声书章节与配套讲义"
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
  $("btn-next").disabled = true
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
      $("btn-next").disabled = false
    }
  } catch {
    /* Next chapter discovery failure shouldn't stop playback */
  }
}

async function loadTrack(track, preparedUrl) {
  if (!isWithinRoot(track.path) || !AUDIO.test(track.name))
    throw new Error("不是可播放的有声书音频文件")
  saveProgress()
  const request = ++playRequest
  audio.pause()
  ready = false
  pendingPosition = null
  current = null
  preparedNext = null
  $("btn-next").disabled = true

  // Immediately clear old timeline & document to avoid scanning wrong chapters
  readalongTimeline = []
  currentSegment = null
  currentDocPath = ""
  $("dock-readalong").hidden = true
  $("dock-pdf").hidden = true

  // Set titles and artwork in Mini and Full Player
  const parentDir = track.path.slice(0, track.path.lastIndexOf("/"))
  const bookName = parentDir.split("/").filter(Boolean).pop() || "有声书"
  const trackName = track.name.replace(AUDIO, "")

  $("mini-title").textContent = trackName
  $("mini-subtitle").textContent = bookName
  $("player-book-title").textContent = bookName
  $("player-track-title").textContent = trackName
  $("player-track-desc").textContent = "正在加载音频..."

  // Update Disc Center Artwork with Book Cover
  const fullCoverPath = resolveBookCoverPath(parentDir, bookName)

  const miniThumb = $("mini-cover-thumb")
  const vinylCenter = $("vinyl-cover-art")
  const rfCenter = document.querySelector("#readalong-floating-disc .floating-center")
  const pfCenter = document.querySelector("#pdf-floating-disc .floating-center")

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

  // Load signed cover if exists
  if (fullCoverPath) {
    getSignedCoverUrl(fullCoverPath).then((signedUrl) => {
      if (signedUrl && request === playRequest) {
        const bgCss = `url("${signedUrl}") center/cover no-repeat`
        if (miniThumb) { miniThumb.style.background = bgCss; $("mini-cover-icon").hidden = true }
        if (vinylCenter) { vinylCenter.style.background = bgCss; vinylCenter.textContent = "" }
        if (rfCenter) { rfCenter.style.background = bgCss; rfCenter.textContent = "" }
        if (pfCenter) { pfCenter.style.background = bgCss; pfCenter.textContent = "" }
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
  renderDrawerTrackList()
}

async function ensureCurrentLoaded(autoPlay = true) {
  if (current && audio.src) {
    if (autoPlay && audio.paused) playAudio()
    return
  }
  const journal = read(localStorage, JOURNAL, null)
  const candidateTrack = journal?.track || libraryRecords()[0]?.track
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
    $("player-track-desc").textContent = target > 0 ? `已续播至 ${durationText(target)} (回退3秒)` : "已准备就绪"
  } catch {
    /* Stream seekable */
  }
}

function seek(seconds) {
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

  // Class-based CSS toggle ensures 100% reliable SVG icon switching
  if (playBtn) playBtn.classList.toggle("is-playing", playing)
  if (miniPlayBtn) miniPlayBtn.classList.toggle("is-playing", playing)
  if (rfBtn) rfBtn.classList.toggle("is-playing", playing)
  if (pfBtn) pfBtn.classList.toggle("is-playing", playing)

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

  const rfDisc = $("readalong-floating-disc")
  const pfDisc = $("pdf-floating-disc")
  if (playing) {
    $("mini-cover-thumb").classList.add("spinning")
    $("vinyl-disc").classList.add("spinning")
    if (rfDisc) rfDisc.classList.add("spinning")
    if (pfDisc) pfDisc.classList.add("spinning")
  } else {
    $("mini-cover-thumb").classList.remove("spinning")
    $("vinyl-disc").classList.remove("spinning")
    if (rfDisc) rfDisc.classList.remove("spinning")
    if (pfDisc) pfDisc.classList.remove("spinning")
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
  $("player-track-desc").textContent = "正在播放 · 进度自动保存"
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
    $("player-track-desc").textContent = "全书已播完"
    render()
  }
})

audio.addEventListener("error", () => {
  if (current) notice("音频加载失败，请检查网络或重新选择。")
})

document.addEventListener("visibilitychange", () => {
  if (document.hidden) saveProgress(audio.ended)
})
window.addEventListener("pagehide", () => saveProgress(audio.ended))

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
    $("timer-label").textContent = "播完关"
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
      $("timer-label").textContent = `${mins}分关`
      notice(`已开启定时关闭：${mins} 分钟后停止播放`)
    }
  }
  document.querySelectorAll(".timer-opt").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.minutes === String(minutes))
  })
}

function clearSleepTimer() {
  if (sleepTimerId) clearTimeout(sleepTimerId)
  sleepTimerId = null
  sleepTimerMode = "none"
  sleepTimerMinutes = 0
  $("timer-label").textContent = "定时"
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
  if (!timeline || !timeline.length) return null
  if (!Number.isFinite(time) || time <= timeline[0].start) return timeline[0]
  if (time >= timeline[timeline.length - 1].end) return timeline[timeline.length - 1]

  let low = 0,
    high = timeline.length - 1
  while (low <= high) {
    const mid = (low + high) >> 1
    const seg = timeline[mid]
    if (time < seg.start) high = mid - 1
    else if (time >= seg.end) low = mid + 1
    else return seg
  }
  if (high >= 0 && low < timeline.length) {
    return (time - timeline[high].end < timeline[low].start - time) ? timeline[high] : timeline[low]
  }
  return high >= 0 ? timeline[high] : timeline[0]
}

function findSegment(timeline, time) {
  if (!timeline || !timeline.length) return null
  if (!Number.isFinite(time) || time < 0) return null

  const first = timeline[0]
  const last = timeline[timeline.length - 1]

  // Time is before the first segment (lead-in silence)
  if (time < first.start) {
    return first.start - time <= 5 ? first : null
  }

  // Time is after the last segment
  if (time >= last.end) {
    return time - last.end <= 5 ? last : null
  }

  let low = 0,
    high = timeline.length - 1
  while (low <= high) {
    const mid = (low + high) >> 1
    const seg = timeline[mid]
    if (time < seg.start) high = mid - 1
    else if (time >= seg.end) low = mid + 1
    else return seg
  }
  // In a pause between two sentences, hold the sentence just completed (within 4 seconds)
  if (high >= 0) {
    if (low < timeline.length && timeline[low].start - time <= 0.4) {
      return timeline[low]
    }
    const prev = timeline[high]
    if (time - prev.end <= 4.0) {
      return prev
    }
  }
  return null
}

async function setupReadalong(track, request) {
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
    let manifestInfo = null
    let validParent = ""

    for (const p of candidates) {
      const manifestPath = `${p}/readalong/readalong.manifest.json`
      const info = await api("fs/get", {
        path: manifestPath,
        password: directoryPassword,
      }).catch(() => null)
      if (info) {
        const manifestUrl = mediaUrl(endpoint, { path: manifestPath }, info.sign)
        const m = await fetch(manifestUrl, { cache: "no-store" }).then((r) => r.json()).catch(() => null)
        if (m && m.schemaVersion === 1) {
          manifest = m
          manifestInfo = info
          validParent = p
          break
        }
      }
    }

    if (!manifest || request !== playRequest) return

    const timelinePath = `${validParent}/readalong/${manifest.timeline || "timeline.json"}`
    const timelineInfo = await api("fs/get", {
      path: timelinePath,
      password: directoryPassword,
    }).catch(() => null)
    if (!timelineInfo || request !== playRequest) return

    const timelineUrl = mediaUrl(endpoint, { path: timelinePath }, timelineInfo.sign)
    const timeline = await fetch(timelineUrl, { cache: "no-store" }).then((r) => r.json())
    if (request !== playRequest || !Array.isArray(timeline)) return

    readalongManifest = manifest
    readalongParentPath = validParent

    // Robust multi-track segment matching:
    const cleanId = (s) => (s ? String(s).toLowerCase().replace(/['"’“”\s_-]/g, "").replace(/\.[a-z0-9]+$/, "") : "")
    const targetTrackId = cleanId(track.name)

    let matched = timeline.filter((s) => s.audioSourceId === track.name)
    if (!matched.length && targetTrackId) {
      matched = timeline.filter((s) => s.audioSourceId && cleanId(s.audioSourceId) === targetTrackId)
    }
    if (!matched.length && !timeline.some((s) => s.audioSourceId)) {
      matched = timeline
    }

    // Always sort filtered segments strictly by start time to guarantee binary search correctness
    readalongTimeline = matched.sort((a, b) => (Number(a.start) || 0) - (Number(b.start) || 0))

    // As long as the book has readalong documents, keep the EPUB dock button accessible
    const hasEpubDocument = Boolean(manifest.alignedDocument || readalongTimeline.length || manifest.textRoot)
    $("dock-readalong").hidden = !hasEpubDocument

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

function openReadalong() {
  if (!readalongManifest) return
  readalongActive = true
  $("readalong").hidden = false
  updatePlayButtonUI(!audio.paused)

  // Determine initial document path
  let targetDoc = currentDocPath
  if (!targetDoc) {
    if (readalongTimeline.length && readalongTimeline[0].document) {
      targetDoc = readalongTimeline[0].document
    } else if (readalongManifest.alignedDocument) {
      targetDoc = readalongManifest.alignedDocument
    }
  }

  const badge = document.querySelector(".readalong-capsule-badge")
  const followBtn = $("readalong-follow")
  const locateBtn = $("readalong-locate")

  if (readalongTimeline.length) {
    if (badge) badge.textContent = "跟读模式"
    if (followBtn) followBtn.hidden = false
  } else {
    if (badge) badge.textContent = "阅读模式"
    if (followBtn) followBtn.hidden = true
    if (locateBtn) locateBtn.hidden = true
  }

  if (targetDoc && currentDocPath !== targetDoc) {
    currentDocPath = targetDoc
    loadReadalongDoc(targetDoc).then(() => {
      syncReadalong(true)
    }).catch(() => {})
  } else {
    syncReadalong(true)
  }
}

function closeReadalong() {
  readalongActive = false
  $("readalong").hidden = true
}

function loadReadalongDoc(docRelPath) {
  return new Promise(async (resolve) => {
    const docPath = `${readalongParentPath}/readalong/${docRelPath}`
    let html = readalongDocCache.get(docPath)
    if (!html) {
      $("readalong-loading").hidden = false
      try {
        const info = await api("fs/get", { path: docPath, password: directoryPassword })
        const url = mediaUrl(endpoint, { path: docPath }, info.sign)
        html = await fetch(url).then((r) => r.text())
        readalongDocCache.set(docPath, html)
      } catch {
        /* fetch error */
      } finally {
        $("readalong-loading").hidden = true
      }
    }

    if (!html) return resolve(false)

    const frame = $("readalong-frame")

    let loaded = false
    const onFrameLoad = () => {
      if (loaded) return
      loaded = true
      try {
        const doc = frame.contentDocument
        if (doc) {
          const size = $("readalong-size").value || "17"
          if (doc.body) doc.body.style.fontSize = `${size}px`

          const onUserScroll = () => {
            if (!readalongFollowing) return
            readalongFollowing = false
            $("readalong-follow").textContent = "跟随：暂停"
            $("readalong-locate").hidden = false
          }

          frame.contentWindow?.addEventListener("wheel", onUserScroll, { passive: true })
          frame.contentWindow?.addEventListener("touchmove", onUserScroll, { passive: true })

          doc.addEventListener("click", (e) => {
            const target = e.target.closest("[id]")
            if (!target || !target.id) return
            const seg = readalongTimeline.find((s) => s.fragment === target.id)
            if (seg) {
              seek(seg.start)
              readalongFollowing = true
              $("readalong-follow").textContent = "跟随：开"
              $("readalong-locate").hidden = true
              syncReadalong(true)
            }
          })
        }
      } catch {
        /* sandbox */
      }
      resolve(true)
    }

    frame.onload = onFrameLoad
    frame.srcdoc = html
    setTimeout(onFrameLoad, 100)
  })
}

async function syncReadalong(forceScroll = false) {
  if (!readalongActive || !current) return
  if (!readalongTimeline.length) return

  const seg = findSegment(readalongTimeline, audio.currentTime)
  if (!seg) {
    const frame = $("readalong-frame")
    try {
      frame.contentDocument?.querySelectorAll(".readalong-active").forEach((el) => el.classList.remove("readalong-active"))
    } catch {}
    currentSegment = null

    // If user dragged slider (seeked) or forced scroll, ensure we flip to the nearest chapter
    if (forceScroll) {
      const nearest = findNearestSegment(readalongTimeline, audio.currentTime)
      if (nearest && currentDocPath !== nearest.document) {
        currentDocPath = nearest.document
        await loadReadalongDoc(nearest.document)
      }
      if (nearest) {
        const doc = frame.contentDocument
        const el = doc?.getElementById(nearest.fragment)
        if (el) el.scrollIntoView({ block: "center", behavior: "smooth" })
      }
    }
    return
  }
  if (seg === currentSegment && !forceScroll) return
  currentSegment = seg

  if (currentDocPath !== seg.document) {
    currentDocPath = seg.document
    await loadReadalongDoc(seg.document)
  }

  const frame = $("readalong-frame")
  const highlightElement = () => {
    try {
      const doc = frame.contentDocument
      if (!doc) return false
      const targetElem = doc.getElementById(seg.fragment)
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
  $("full-player").hidden = false
}

on("readalong-floating-player", "click", toggleFloatingPlay)
on("readalong-floating-play-btn", "click", toggleFloatingPlay)
on("readalong-title-btn", "click", openFullPlayerFromReader)
on("readalong-open-player-btn", "click", openFullPlayerFromReader)

on("pdf-floating-player", "click", toggleFloatingPlay)
on("pdf-floating-play-btn", "click", toggleFloatingPlay)
on("pdf-title-btn", "click", openFullPlayerFromReader)
on("pdf-open-player-btn", "click", openFullPlayerFromReader)

// Dock buttons in Full Player
on("dock-chapters", "click", () => openDrawer("chapter-drawer"))
on("dock-timer", "click", () => openDrawer("timer-drawer"))
on("dock-readalong", "click", openReadalong)
on("dock-pdf", "click", openPdfViewer)
on("btn-speed", "click", () => openDrawer("speed-drawer"))

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
on("readalong-follow", "click", () => {
  readalongFollowing = !readalongFollowing
  $("readalong-follow").textContent = `跟随：${readalongFollowing ? "开" : "暂停"}`
  if (readalongFollowing) {
    $("readalong-locate").hidden = true
    syncReadalong(true)
  }
})
on("readalong-locate", "click", () => {
  readalongFollowing = true
  $("readalong-follow").textContent = "跟随：开"
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
  render()
})
on("search-clear", "click", () => {
  $("search").value = ""
  $("search-clear").hidden = true
  render()
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
  if (userInp && prefs.username) userInp.value = prefs.username
  const netSel = $("network")
  if (netSel && prefs.mode) netSel.value = prefs.mode
  $("login-status").textContent = ""
  try {
    $("endpoint-note").textContent = resolveEndpoint($("network")?.value || "auto")
  } catch {
    /* fallback */
  }
  dlg.showModal()
}

on("settings-open", "click", openSettingsModal)
on("open-conn-btn", "click", openSettingsModal)
on("settings-close", "click", () => $("settings")?.close())
on("network", "change", () => {
  try {
    $("endpoint-note").textContent = resolveEndpoint($("network").value)
  } catch (error) {
    $("endpoint-note").textContent = error.message
  }
})

on("connection-form", "submit", async (event) => {
  event.preventDefault()
  const loginBtn = $("login")
  if (loginBtn) loginBtn.disabled = true
  $("login-status").textContent = "正在登录…"
  try {
    const nextEndpoint = resolveEndpoint($("network").value)
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
    prefs = { ...prefs, mode: $("network").value, username }
    write(localStorage, PREF, prefs)
    remove(localStorage, AUTH)
    remove(sessionStorage, AUTH)
    write($("remember").checked ? localStorage : sessionStorage, AUTH, auth)
    $("password").value = ""
    $("settings")?.close()
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
    if (!existing || existing.updatedAt < record.updatedAt) persist(record)
  }
  render()
  notice(`已成功合并 ${candidates.length} 条收听记录`)
  if (imp) imp.value = ""
}))

// Initialize App
async function init() {
  setSpeed(prefs.speed || 1)
  try {
    await openDatabase()
  } catch {
    notice("无法打开本地存储，收听记录可能无法持久保存。")
  }

  // Auto load recent playback from journal if present
  const journal = read(localStorage, JOURNAL, null)
  if (journal && journal.track) {
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

  // Register Service Worker
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {})
  }
}

init()
