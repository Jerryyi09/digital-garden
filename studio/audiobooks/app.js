import { ROOT, resolveEndpoint, isWithinRoot, trackId, mediaUrl } from "./config.js"
import { getBookSummary } from "./summaries.js"

const $ = (id) => document.getElementById(id)
const audio = $("audio")
const AUDIO = /\.(mp3|m4a|m4b)$/i
const PDF = /\.pdf$/i
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
    response = await fetch(`${endpoint}/api/${route}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      credentials: "omit",
      cache: "no-store",
      signal: AbortSignal.timeout(25000),
    })
  } catch {
    throw new Error(
      "无法连接家庭书库，请检查 NUC 是否在线及网络方式。",
    )
  }
  if (!response.ok) throw new Error(`书库请求失败（HTTP ${response.status}）`)
  const result = await response.json()
  if (result.code !== 200) {
    if (result.code === 401) {
      $("settings").showModal()
      throw new Error("请使用 AList 账号登录；登录已过期。")
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
    .map((item) => ({
      path: `${path}/${item.name}`,
      name: item.name,
      is_dir: item.is_dir === true,
      size: item.size,
      modified: item.modified,
      hasReadalong: hasReadalongInFolder && !item.is_dir,
      hasPdf: Boolean(pdfInFolder) && !item.is_dir,
      pdfName: pdfInFolder,
    }))
}

async function browse(path = folder) {
  const request = ++browseRequest
  $("list-status").textContent = "正在读取目录..."
  $("refresh").disabled = true
  try {
    const result = await list(path)
    if (request !== browseRequest) return
    entries = result
    folder = path
    $("search").value = ""
    $("search-clear").hidden = true
    render()
  } finally {
    if (request === browseRequest) $("refresh").disabled = false
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

    const cover = document.createElement("div")
    cover.className = "shelf-cover-box"
    cover.textContent = "📖"

    const title = document.createElement("div")
    title.className = "shelf-card-title"
    title.textContent = record.track.name.replace(AUDIO, "")

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
    $("banner-readalong-badge").hidden = !entries.some((i) => i.hasReadalong)
    $("banner-pdf-badge").hidden = !entries.some((i) => i.hasPdf)
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

    const info = document.createElement("div")
    info.className = "item-main-info"

    const titleRow = document.createElement("div")
    titleRow.className = "item-title-row"

    const title = document.createElement("h3")
    title.className = "item-name"
    title.textContent = item.name.replace(AUDIO, "")
    titleRow.append(title)

    if (item.hasReadalong) {
      const badge = document.createElement("span")
      badge.className = "badge-readalong"
      badge.textContent = "📖 跟读"
      titleRow.append(badge)
    } else if (item.hasPdf) {
      const badge = document.createElement("span")
      badge.className = "badge-pdf"
      badge.textContent = "📄 PDF"
      titleRow.append(badge)
    }
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

  // Set titles in Mini and Full Player
  const pathParts = track.path.slice(ROOT.length).split("/").filter(Boolean)
  const bookName = pathParts.length > 1 ? pathParts[1] : (pathParts[0] || "有声书")
  const trackName = track.name.replace(AUDIO, "")

  $("mini-title").textContent = trackName
  $("mini-subtitle").textContent = bookName
  $("player-book-title").textContent = bookName
  $("player-track-title").textContent = trackName
  $("player-track-desc").textContent = "正在加载音频..."

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
  audio.play().catch((error) => {
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
function findSegment(timeline, time) {
  if (!timeline || !timeline.length) return null
  if (time < timeline[0].start) return timeline[0]
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
  // If time falls in a gap between two sentences, stick to the sentence just finished
  if (high >= 0) return timeline[high]
  return timeline[0]
}

async function setupReadalong(track, request) {
  readalongManifest = null
  readalongTimeline = []
  currentSegment = null
  currentDocPath = ""
  $("dock-readalong").hidden = true

  try {
    const parent = track.path.slice(0, track.path.lastIndexOf("/"))
    const manifestPath = `${parent}/readalong/readalong.manifest.json`
    const manifestInfo = await api("fs/get", {
      path: manifestPath,
      password: directoryPassword,
    }).catch(() => null)
    if (!manifestInfo || request !== playRequest) return

    const manifestUrl = mediaUrl(endpoint, { path: manifestPath }, manifestInfo.sign)
    const manifest = await fetch(manifestUrl, { cache: "no-store" }).then((r) => r.json())
    if (request !== playRequest || !manifest || manifest.schemaVersion !== 1) return

    const timelinePath = `${parent}/readalong/${manifest.timeline || "timeline.json"}`
    const timelineInfo = await api("fs/get", {
      path: timelinePath,
      password: directoryPassword,
    }).catch(() => null)
    if (!timelineInfo || request !== playRequest) return

    const timelineUrl = mediaUrl(endpoint, { path: timelinePath }, timelineInfo.sign)
    const timeline = await fetch(timelineUrl, { cache: "no-store" }).then((r) => r.json())
    if (request !== playRequest || !Array.isArray(timeline)) return

    readalongManifest = manifest
    // Filter segments for this specific audio track if multi-track
    const trackFiltered = timeline.filter((s) => !s.audioSourceId || s.audioSourceId === track.name)
    readalongTimeline = trackFiltered.length ? trackFiltered : timeline
    readalongParentPath = parent
    $("dock-readalong").hidden = false

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
    let pdfItem = null
    const data = await api("fs/list", {
      path: parent,
      password: directoryPassword,
      page: 1,
      per_page: 50,
      refresh: false,
    }).catch(() => null)
    if (data?.content) {
      pdfItem = data.content.find((item) => !item.is_dir && PDF.test(item.name))
    }
    if (!pdfItem || request !== playRequest) return
    currentPdfPath = `${parent}/${pdfItem.name}`
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
  if (!readalongManifest || !readalongTimeline.length) return
  readalongActive = true
  $("readalong").hidden = false
  updatePlayButtonUI(!audio.paused)

  // Preload first segment document if not loaded yet
  if (!currentDocPath && readalongTimeline[0]) {
    currentDocPath = readalongTimeline[0].document
    loadReadalongDoc(currentDocPath).catch(() => {})
  }
  syncReadalong(true)
}

function closeReadalong() {
  readalongActive = false
  $("readalong").hidden = true
}

async function loadReadalongDoc(docRelPath) {
  const docPath = `${readalongParentPath}/readalong/${docRelPath}`
  let html = readalongDocCache.get(docPath)
  if (!html) {
    $("readalong-loading").hidden = false
    try {
      const info = await api("fs/get", { path: docPath, password: directoryPassword })
      const url = mediaUrl(endpoint, { path: docPath }, info.sign)
      html = await fetch(url).then((r) => r.text())
      readalongDocCache.set(docPath, html)
    } finally {
      $("readalong-loading").hidden = true
    }
  }

  const frame = $("readalong-frame")
  frame.srcdoc = html

  setTimeout(() => {
    try {
      const doc = frame.contentDocument
      if (!doc) return
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
    } catch {
      /* Same origin sandbox */
    }
  }, 50)
}

async function syncReadalong(forceScroll = false) {
  if (!readalongActive || !readalongTimeline.length || !current) return
  const seg = findSegment(readalongTimeline, audio.currentTime)
  if (!seg) return
  if (seg === currentSegment && !forceScroll) return
  currentSegment = seg

  if (currentDocPath !== seg.document) {
    currentDocPath = seg.document
    await loadReadalongDoc(seg.document)
  }

  const frame = $("readalong-frame")
  const doc = frame.contentDocument
  if (!doc) return

  doc.querySelectorAll(".readalong-active").forEach((el) => el.classList.remove("readalong-active"))
  const targetElem = doc.getElementById(seg.fragment)
  if (targetElem) {
    targetElem.classList.add("readalong-active")
    if (readalongFollowing || forceScroll) {
      targetElem.scrollIntoView({ block: "center", behavior: "smooth" })
    }
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

// User Interaction Listeners
$("play").onclick = () => (audio.paused ? playAudio() : audio.pause())
$("mini-play-btn").onclick = async (e) => {
  e.stopPropagation()
  if (!current || !audio.src) {
    await ensureCurrentLoaded(true)
  } else {
    audio.paused ? playAudio() : audio.pause()
  }
}
$("rewind").onclick = () => seek(audio.currentTime - 15)
$("forward").onclick = () => seek(audio.currentTime + 30)
$("btn-next").onclick = nextTrack

// Toggle Full Player / Mini Player
$("mini-content-area").onclick = async () => {
  if (!current || !audio.src) {
    await ensureCurrentLoaded(false)
  }
  $("full-player").hidden = false
}
$("mini-list-btn").onclick = (e) => {
  e.stopPropagation()
  openDrawer("chapter-drawer")
}
$("player-collapse-btn").onclick = () => {
  $("full-player").hidden = true
}

// Floating Vinyl Player in Readalong & PDF Panels (WeRead Style)
$("readalong-floating-play-btn").onclick = (e) => {
  e.stopPropagation()
  audio.paused ? playAudio() : audio.pause()
}
$("readalong-floating-player").onclick = () => {
  $("full-player").hidden = false
}

$("pdf-floating-play-btn").onclick = (e) => {
  e.stopPropagation()
  audio.paused ? playAudio() : audio.pause()
}
$("pdf-floating-player").onclick = () => {
  $("full-player").hidden = false
}

// Dock buttons in Full Player
$("dock-chapters").onclick = () => openDrawer("chapter-drawer")
$("dock-timer").onclick = () => openDrawer("timer-drawer")
$("dock-readalong").onclick = openReadalong
$("dock-pdf").onclick = openPdfViewer
$("btn-speed").onclick = () => openDrawer("speed-drawer")

// Drawer Closers
$("drawer-mask").onclick = closeAllDrawers
$("drawer-close").onclick = closeAllDrawers
$("timer-close").onclick = closeAllDrawers
$("speed-close").onclick = closeAllDrawers

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
$("readalong-close").onclick = closeReadalong
$("pdf-close").onclick = closePdfViewer
$("readalong-follow").onclick = () => {
  readalongFollowing = !readalongFollowing
  $("readalong-follow").textContent = `跟随：${readalongFollowing ? "开" : "暂停"}`
  if (readalongFollowing) {
    $("readalong-locate").hidden = true
    syncReadalong(true)
  }
}
$("readalong-locate").onclick = () => {
  readalongFollowing = true
  $("readalong-follow").textContent = "跟随：开"
  $("readalong-locate").hidden = true
  syncReadalong(true)
}
$("readalong-size").onchange = () => {
  const size = $("readalong-size").value
  const doc = $("readalong-frame").contentDocument
  if (doc?.body) doc.body.style.fontSize = `${size}px`
}

// Search
$("search").oninput = (e) => {
  $("search-clear").hidden = !e.target.value
  render()
}
$("search-clear").onclick = () => {
  $("search").value = ""
  $("search-clear").hidden = true
  render()
}
$("sort").onchange = render
$("refresh").onclick = attempt(() => browse())

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
$("settings-open").onclick = () => $("settings").showModal()
$("open-conn-btn").onclick = () => $("settings").showModal()
$("settings-close").onclick = () => $("settings").close()
$("network").onchange = () => {
  try {
    $("endpoint-note").textContent = resolveEndpoint($("network").value)
  } catch (error) {
    $("endpoint-note").textContent = error.message
  }
}

$("connection-form").onsubmit = async (event) => {
  event.preventDefault()
  $("login").disabled = true
  $("login-status").textContent = "正在登录…"
  try {
    const nextEndpoint = resolveEndpoint($("network").value)
    if (location.protocol === "https:" && !nextEndpoint.startsWith("https://"))
      throw new Error("HTTPS 页面只能连接 HTTPS 书库。")
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
        { username, password, otp_code: $("otp").value.trim() },
        "",
      )
      auth = { token: data.token, deviceKey: data.device_key, username, endpoint }
    }
    directoryPassword = $("folder-password").value
    prefs = { ...prefs, mode: $("network").value, username }
    write(localStorage, PREF, prefs)
    remove(localStorage, AUTH)
    remove(sessionStorage, AUTH)
    write($("remember").checked ? localStorage : sessionStorage, AUTH, auth)
    $("password").value = ""
    $("otp").value = ""
    await browse(ROOT)
    $("settings").close()
    notice("登录成功，书库已同步")
  } catch (error) {
    $("login-status").textContent = error.message
  } finally {
    $("login").disabled = false
  }
}

$("logout").onclick = () => {
  logout()
  $("settings").close()
}
$("logout-btn").onclick = logout

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
  for (const id of ["password", "otp", "username", "folder-password"]) $(id).value = ""
  $("mini-player").hidden = true
  $("full-player").hidden = true
  notice("已清除本机登录记录")
  render()
}

$("export-btn").onclick = () => {
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
}

$("import").onchange = attempt(async () => {
  const file = $("import").files[0]
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
  $("import").value = ""
})

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
    const bookName = journal.track.path.slice(ROOT.length).split("/").filter(Boolean)[1] || "有声书"
    $("mini-subtitle").textContent = `继续听 · ${bookName}`
    $("mini-player").hidden = false
  }

  if (auth?.token) {
    browse(ROOT)
  } else {
    // Open settings if not connected
    $("settings").showModal()
  }

  // Register Service Worker
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {})
  }
}

init()
