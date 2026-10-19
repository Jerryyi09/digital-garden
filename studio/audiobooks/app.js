import { ROOT, resolveEndpoint, isWithinRoot, trackId, mediaUrl } from "./config.js"
import { getBookSummary } from "./summaries.js"

const $ = (id) => document.getElementById(id)
const audio = $("audio")
const AUDIO = /\.(mp3|m4a|m4b)$/i
const PDF = /\.pdf$/i
const PREF = "garden-listen-prefs-v1"
const AUTH = "garden-listen-auth-v1"
const JOURNAL = "garden-listen-journal-v1"
let prefs = read(localStorage, PREF, { mode: "auto", username: "", speed: 1 })
let auth = read(sessionStorage, AUTH, null) || read(localStorage, AUTH, null)
let endpoint = resolveEndpoint()
let records = []
let entries = []
let folder = ROOT
let view = "browse"
let current = null
let ready = false
let pendingPosition = null
let lastSave = 0
let playRequest = 0
let browseRequest = 0
let preparedNext = null
let db
let directoryPassword = ""
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

function notice(message = "") {
  $("notice").textContent = message
  $("notice").hidden = !message
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
  return `${Math.floor(s / 3600) ? `${Math.floor(s / 3600)}:` : ""}${String(Math.floor(s / 60) % 60).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`
}

async function openDatabase() {
  db = await new Promise((resolve, reject) => {
    const request = indexedDB.open("garden-audiobooks", 1)
    request.onupgradeneeded = () => request.result.createObjectStore("progress", { keyPath: "key" })
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
    transaction.onerror = () => notice("收听记录写入失败，请导出记录备份。")
  }
}

function saveProgress(completed = audio.ended) {
  // Metadata loading emits timeupdate/pause too; do not overwrite a resume point with zero.
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
  // Synchronous journal survives pagehide where IndexedDB may not finish before suspension.
  if (!write(localStorage, JOURNAL, record)) notice("浏览器禁用了持久存储；请导出收听记录。")
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
      "无法连接家庭书库，请检查 NUC 是否在线及访问方式。Cloudflare 只托管界面，播放仍需连接家庭服务器。",
    )
  }
  if (!response.ok) throw new Error(`书库请求失败（HTTP ${response.status}）`)
  const result = await response.json()
  if (result.code !== 200) {
    if (result.code === 401) {
      $("settings").showModal()
      throw new Error("请使用 AList 账号登录；原登录可能已过期。")
    }
    throw new Error(result.message || `AList 错误 ${result.code}`)
  }
  return result.data
}

async function list(path) {
  if (!isWithinRoot(path)) throw new Error("只能浏览 /750HD/有声书 下的目录")
  // Fetch every page; server-side page-size limits must not hide later chapters.
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
  $("list-status").textContent = "正在读取目录…"
  $("refresh").disabled = true
  try {
    const result = await list(path)
    if (request !== browseRequest) return
    entries = result
    folder = path
    view = "browse"
    $("search").value = ""
    notice()
    render()
    $("connection").textContent =
      `${endpoint.startsWith(location.origin) ? "当前站点直连" : "外网 HTTPS"} · 书库已连接`
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

function render() {
  breadcrumbs()

  // Display full book overview at the top if inside a book folder
  const currentDirName = folder.slice(ROOT.length).split("/").filter(Boolean).pop() || ""
  const currentSummary = getBookSummary(currentDirName)
  if (currentSummary && folder !== ROOT && view === "browse") {
    $("folder-summary-text").textContent = currentSummary
    $("folder-summary").hidden = false
  } else {
    $("folder-summary").hidden = true
    $("folder-summary-text").textContent = ""
  }

  $("browse-tab").setAttribute("aria-pressed", String(view === "browse"))
  $("recent-tab").setAttribute("aria-pressed", String(view === "recent"))
  $("search").placeholder = view === "recent" ? "搜索收听记录 / 文件名" : "搜索当前目录 / 文件名"
  const query = $("search").value.trim().toLocaleLowerCase()
  let items = view === "recent" ? libraryRecords().map((record) => record.track) : [...entries]
  items = items.filter((item) => item.name.toLocaleLowerCase().includes(query))
  if (view !== "recent")
    items.sort(
      (a, b) =>
        Number(b.is_dir) - Number(a.is_dir) ||
        ($("sort").value === "modified"
          ? (Date.parse(b.modified) || 0) - (Date.parse(a.modified) || 0)
          : a.name.localeCompare(b.name, "zh-CN", { numeric: true })),
    )
  $("items").replaceChildren()
  $("list-status").textContent =
    `${view === "recent" ? "最近收听" : "当前目录"} · ${items.length} 项${query ? " · 已筛选" : ""}`
  for (const item of items) {
    const record = progress(item)
    const button = document.createElement("button")

    if (item.is_dir) {
      button.className = "item dir-item"
      const title = document.createElement("strong")
      title.textContent = item.name.replace(AUDIO, "")
      if (item.hasReadalong) {
        const badge = document.createElement("span")
        badge.className = "badge-readalong"
        badge.textContent = "📖 跟读"
        title.append(badge)
      } else if (item.hasPdf) {
        const badge = document.createElement("span")
        badge.className = "badge-pdf"
        badge.textContent = "📄 PDF"
        title.append(badge)
      }

      const descText = getBookSummary(item.name)
      const desc = document.createElement("p")
      desc.className = "item-desc"
      desc.textContent = descText || "点击浏览有声书章节与资料"

      const action = document.createElement("span")
      action.className = "row-action"
      action.setAttribute("aria-hidden", "true")
      action.textContent = "↗"

      button.append(title, desc, action)
    } else {
      button.className = "item"
      const kind = document.createElement("span")
      kind.className = "kind"
      kind.textContent = `♫ ${item.name.split(".").pop().toUpperCase()}`
      const title = document.createElement("strong")
      title.textContent = item.name.replace(AUDIO, "")
      if (item.hasReadalong) {
        const badge = document.createElement("span")
        badge.className = "badge-readalong"
        badge.textContent = "📖 跟读"
        title.append(badge)
      } else if (item.hasPdf) {
        const badge = document.createElement("span")
        badge.className = "badge-pdf"
        badge.textContent = "📄 PDF"
        title.append(badge)
      }
      const meta = document.createElement("small")
      meta.textContent = record
        ? `${record.completed ? "已听完" : "听至"} ${durationText(record.position)} / ${durationText(record.duration)}`
        : `${(item.size / 1024 / 1024).toFixed(1)} MB · 开始收听`
      const action = document.createElement("span")
      action.className = "row-action"
      action.setAttribute("aria-hidden", "true")
      action.textContent = "▷"
      button.append(kind, title, meta, action)
      if (record) {
        const bar = document.createElement("progress")
        bar.max = record.duration || 1
        bar.value = record.position
        bar.setAttribute("aria-label", "收听进度")
        button.append(bar)
      }
    }

    button.onclick = attempt(() => (item.is_dir ? browse(item.path) : loadTrack(item)))
    const row = document.createElement("div")
    row.className = "item-row"
    row.setAttribute("role", "listitem")
    row.append(button)
    $("items").append(row)
  }
  if (!items.length) {
    const empty = document.createElement("p")
    empty.className = "empty"
    empty.textContent = query
      ? "没有匹配的文件名。可进入其他分类查找。"
      : view === "recent"
        ? "还没有收听记录。选一本书，开始听吧。"
        : "这里暂无音频；如果尚未连接，请先登录书库。"
    $("items").append(empty)
  }
  const latest = libraryRecords().find((record) => !record.completed)
  $("resume").hidden = !latest
  if (latest) {
    $("resume-title").textContent = latest.track.name.replace(AUDIO, "")
    $("resume-meta").textContent =
      `上次听至 ${durationText(latest.position)} / ${durationText(latest.duration)}`
    $("resume-play").onclick = attempt(() => loadTrack(latest.track))
  }
}

async function stream(track) {
  const info = await api("fs/get", { path: track.path, password: directoryPassword })
  // Use AList's signed /d endpoint; raw_url may contain private Docker/LAN addresses.
  return mediaUrl(endpoint, track, info.sign)
}

async function prepareNext(request) {
  preparedNext = null
  $("next").disabled = true
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
      $("next").disabled = false
    }
  } catch {
    /* Next-chapter discovery must not stop the current chapter. */
  }
}

async function loadTrack(track, preparedUrl) {
  if (!isWithinRoot(track.path) || !AUDIO.test(track.name))
    throw new Error("不是可播放的有声书文件")
  saveProgress()
  const request = ++playRequest
  audio.pause()
  ready = false
  pendingPosition = null
  current = null
  preparedNext = null
  $("next").disabled = true
  $("play").disabled = true
  $("player").hidden = false
  $("track-title").textContent = track.name.replace(AUDIO, "")
  $("track-folder").textContent =
    track.path.slice(ROOT.length, track.path.lastIndexOf("/")) || "有声书"
  $("player-status").textContent = "正在准备音频…"
  const url = preparedUrl || (await stream(track))
  if (request !== playRequest) return
  const saved = progress(track)
  current = track
  pendingPosition = saved && !saved.completed ? Math.max(0, saved.position - 3) : 0
  audio.src = url
  audio.playbackRate = Number(prefs.speed) || 1
  audio.load()
  $("play").disabled = false
  // Safari may reject after the API await; expose a real user-gesture play button.
  playAudio()
  prepareNext(request)
  setupReadalong(track, request)
  setupPdf(track, request)
}

function findSegment(timeline, time) {
  let low = 0,
    high = timeline.length - 1
  while (low <= high) {
    const mid = (low + high) >> 1
    const seg = timeline[mid]
    if (time < seg.start) high = mid - 1
    else if (time >= seg.end) low = mid + 1
    else return seg
  }
  if (high >= 0 && time - timeline[high].end < 0.6) return timeline[high]
  if (low < timeline.length && timeline[low].start - time < 0.6) return timeline[low]
  return null
}

async function setupReadalong(track, request) {
  readalongManifest = null
  readalongTimeline = []
  currentSegment = null
  currentDocPath = ""
  $("readalong-toggle").hidden = true
  if (readalongActive) closeReadalong()

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
    const trackFiltered = timeline.filter((s) => !s.audioSourceId || s.audioSourceId === track.name)
    readalongTimeline = trackFiltered.length ? trackFiltered : timeline
    readalongParentPath = parent
    $("readalong-toggle").hidden = false
    $("readalong-toggle").textContent = "📖 边听边读"
  } catch {
    $("readalong-toggle").hidden = true
  }
}

async function setupPdf(track, request) {
  currentPdfPath = ""
  currentPdfName = ""
  $("pdf-toggle").hidden = true
  if (pdfViewerActive) closePdfViewer()

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
    $("pdf-toggle").hidden = false
    $("pdf-toggle").textContent = "📄 浏览讲义/PDF"
  } catch {
    $("pdf-toggle").hidden = true
  }
}

async function openPdfViewer() {
  if (!currentPdfPath) return
  if (readalongActive) closeReadalong()
  pdfViewerActive = true
  $("pdf-viewer").hidden = false
  $("pdf-toggle").textContent = "收起讲义/PDF"
  $("pdf-title").textContent = currentPdfName || "配套讲义 / PDF 电子书"
  $("pdf-loading").hidden = false

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
  if ($("pdf-toggle")) {
    $("pdf-toggle").textContent = "📄 浏览讲义/PDF"
  }
}

function openReadalong() {
  if (!readalongManifest || !readalongTimeline.length) return
  if (pdfViewerActive) closePdfViewer()
  readalongActive = true
  $("readalong").hidden = false
  $("readalong-toggle").textContent = "收起跟读"

  // If no document is currently loaded, preload the first document
  if (!currentDocPath && readalongTimeline[0]) {
    currentDocPath = readalongTimeline[0].document
    loadReadalongDoc(currentDocPath).catch(() => {})
  }
  syncReadalong(true)
}

function closeReadalong() {
  readalongActive = false
  $("readalong").hidden = true
  if ($("readalong-toggle")) {
    $("readalong-toggle").textContent = "📖 边听边读"
  }
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

  // Attach handlers once frame content is accessible
  setTimeout(() => {
    try {
      const doc = frame.contentDocument
      if (!doc) return
      const size = $("readalong-size").value || "16"
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
      /* Access inside same-origin frame */
    }
  }, 50)
}

async function syncReadalong(forceScroll = false) {
  if (!readalongActive || !readalongTimeline.length || !current) return
  const seg =
    findSegment(readalongTimeline, audio.currentTime) ||
    (audio.currentTime < readalongTimeline[0].start ? readalongTimeline[0] : null)
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

function playAudio() {
  if (!current || !audio.src) return
  audio.play().catch((error) => {
    $("player-status").textContent =
      error.name === "NotAllowedError"
        ? "音频已准备好，轻点「播放」开始。"
        : "播放失败，请重新选择音频刷新链接，或检查文件编码与网络。"
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
    $("player-status").textContent =
      target > 0
        ? `已恢复至 ${durationText(target)}（回退 3 秒接续）`
        : "已准备好 · 轻点播放即可收听"
  } catch {
    /* Retry when the stream becomes seekable. */
  }
}

function seek(seconds) {
  if (ready && Number.isFinite(audio.duration))
    audio.currentTime = Math.max(0, Math.min(audio.duration, seconds))
}

function nextTrack() {
  if (!preparedNext) return
  const next = preparedNext
  loadTrack(next.track, Date.now() - next.preparedAt < 5 * 60 * 1000 ? next.url : undefined).catch(
    fail,
  )
}

function mediaSession() {
  if (!("mediaSession" in navigator) || !current) return
  const session = navigator.mediaSession
  session.metadata = new MediaMetadata({
    title: current.name.replace(AUDIO, ""),
    artist: "Rosemary Garden",
    album: "花园听书",
    artwork: [
      { src: new URL("./icon-512.png", import.meta.url).href, sizes: "512x512", type: "image/png" },
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
      /* Unsupported actions vary by iOS version. */
    }
  }
}

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
      /* Some streams have not exposed a valid duration yet. */
    }
  }
  if (readalongActive) syncReadalong()
})
audio.addEventListener("playing", () => {
  $("play").textContent = "暂停"
  $("player-status").textContent = "正在收听 · 进度自动保存"
  if ("audioSession" in navigator) {
    try {
      navigator.audioSession.type = "playback"
    } catch {
      /* Optional API. */
    }
  }
  mediaSession()
  if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing"
})
audio.addEventListener("pause", () => {
  saveProgress(audio.ended)
  $("play").textContent = "播放"
  if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "paused"
})
audio.addEventListener("ended", () => {
  saveProgress(true)
  if (preparedNext) nextTrack()
  else {
    $("player-status").textContent = "本节已听完"
    render()
  }
})
audio.addEventListener("error", () => {
  if (current)
    $("player-status").textContent =
      "音频加载失败。请重新选择刷新链接；仍失败时需检查文件编码或 AList 权限。"
})
document.addEventListener("visibilitychange", () => {
  if (document.hidden) saveProgress(audio.ended)
})
window.addEventListener("pagehide", () => saveProgress(audio.ended))
$("play").onclick = () => (audio.paused ? playAudio() : audio.pause())
$("rewind").onclick = () => seek(audio.currentTime - 15)
$("forward").onclick = () => seek(audio.currentTime + 30)
$("next").onclick = nextTrack
$("speed").onchange = () => {
  prefs.speed = Number($("speed").value)
  audio.playbackRate = prefs.speed
  write(localStorage, PREF, prefs)
  saveProgress()
}
$("search").oninput = render
$("sort").onchange = render
$("browse-tab").onclick = () => {
  view = "browse"
  render()
}
$("recent-tab").onclick = () => {
  view = "recent"
  render()
}
$("refresh").onclick = attempt(() => browse())
$("settings-open").onclick = () => $("settings").showModal()
$("settings-close").onclick = () => $("settings").close()
$("readalong-toggle").onclick = () => (readalongActive ? closeReadalong() : openReadalong())
$("readalong-close").onclick = closeReadalong
$("pdf-toggle").onclick = () => (pdfViewerActive ? closePdfViewer() : openPdfViewer())
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
    $("player").hidden = true
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
    $("login-status").textContent = ""
  } catch (error) {
    $("login-status").textContent = error.message
  } finally {
    $("login").disabled = false
  }
}

$("logout").onclick = () => {
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
  $("player").hidden = true
  $("connection").textContent = "已退出登录"
  $("login-status").textContent = "已清除本机登录；收听记录保留，重新登录相同账号后可续听。"
  render()
}

$("export").onclick = () => {
  saveProgress()
  const url = URL.createObjectURL(
    new Blob([JSON.stringify({ version: 1, records: libraryRecords() }, null, 2)], {
      type: "application/json",
    }),
  )
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = `garden-listen-${new Date().toISOString().slice(0, 10)}.json`
  anchor.click()
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
  $("login-status").textContent = `已合并 ${candidates.length} 条收听记录。`
  $("import").value = ""
})

async function start() {
  try {
    await openDatabase()
  } catch {
    notice("当前浏览器无法打开进度数据库；本次仅保留临时记录，请导出备份。")
  }
  const journal = read(localStorage, JOURNAL, null)
  if (journal?.key && isWithinRoot(journal.track?.path)) {
    const existing = records.find((item) => item.key === journal.key)
    if (!existing || journal.updatedAt > existing.updatedAt) persist(journal)
  }
  try {
    endpoint = resolveEndpoint(prefs.mode)
  } catch {
    prefs.mode = "auto"
    endpoint = resolveEndpoint()
  }
  // A token is only ever sent to the endpoint at which this app obtained it.
  if (auth?.endpoint !== endpoint) auth = null
  $("network").value = prefs.mode
  $("username").value = auth?.username || prefs.username || ""
  $("remember").checked = Boolean(read(localStorage, AUTH, null))
  $("speed").value = String(prefs.speed || 1)
  $("network").onchange()
  render()
  $("connection").textContent = "等待连接家庭书库"
  if (auth) {
    try {
      await browse(ROOT)
    } catch (error) {
      fail(error)
    }
  } else {
    notice("连接家庭 AList 账号后，即可浏览 /750HD/有声书。")
    $("settings").showModal()
  }
  if ("serviceWorker" in navigator && window.isSecureContext) {
    navigator.serviceWorker
      .register("./sw.js", { scope: "./", updateViaCache: "none" })
      .catch(() => {
        notice("当前环境无法安装离线界面，在线浏览与播放仍可使用。")
      })
  }
}
start().catch(fail)
