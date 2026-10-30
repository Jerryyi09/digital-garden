export const ROOT = "/多媒体/750HD/有声书"
export const EXTERNAL_ALIST = "https://melyi.uk:8089/alist"
export const LAN_ALIST = "http://10.0.0.85:8088/alist"

export function resolveEndpoint(mode = "auto", location = window.location) {
  const isHttps = location.protocol === "https:"
  const local = /^(10\.|192\.168\.|127\.|localhost$|172\.(1[6-9]|2\d|3[01])\.)/.test(location.hostname)

  if (mode === "external") return EXTERNAL_ALIST
  if (mode === "lan") {
    if (isHttps) {
      // Automatic safe fallback: on HTTPS, LAN HTTP is blocked by browsers, use secure external endpoint
      return EXTERNAL_ALIST
    }
    return LAN_ALIST
  }
  if (local && location.hostname !== "localhost" && !location.hostname.startsWith("127.")) {
    return `${location.origin}/alist`
  }
  if (location.hostname === "melyi.uk") {
    const port = location.port || "8089"
    return `${location.protocol}//${location.hostname}:${port}/alist`
  }
  return EXTERNAL_ALIST
}

export function isWithinRoot(path) {
  return typeof path === "string" && (path === ROOT || path.startsWith(`${ROOT}/`)) &&
    !path.split("/").some(part => part === "." || part === "..")
}

export function trackId(track) {
  return JSON.stringify([track.path, Number(track.size) || 0, track.modified || ""])
}

export function mediaUrl(endpoint, track, sign) {
  if (!isWithinRoot(track.path)) throw new Error("音频不在有声书目录内")
  const url = new URL(`${endpoint}/d${track.path.split("/").map(encodeURIComponent).join("/")}`)
  if (sign) url.searchParams.set("sign", sign)
  return url.href
}
