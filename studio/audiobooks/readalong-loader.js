// Limit retained releases and segments; oversized timelines remain usable without caching.
export class ReadalongCache {
  constructor({ maxEntries = 4, maxWeight = 50000, ttl = Infinity, weight = () => 1, now = Date.now } = {}) {
    Object.assign(this, { maxEntries, maxWeight, ttl, weight, now })
    this.entries = new Map()
    this.totalWeight = 0
  }

  get(key) {
    const entry = this.entries.get(key)
    if (!entry) return undefined
    if (this.now() >= entry.expires) {
      this.delete(key)
      return undefined
    }
    this.entries.delete(key)
    this.entries.set(key, entry)
    return entry.value
  }

  delete(key) {
    const entry = this.entries.get(key)
    if (entry) this.totalWeight -= entry.weight
    this.entries.delete(key)
  }

  set(key, value) {
    this.delete(key)
    const weight = this.weight(value)
    if (weight > this.maxWeight) return
    this.entries.set(key, { value, weight, expires: this.now() + this.ttl })
    this.totalWeight += weight
    while (this.entries.size > this.maxEntries || this.totalWeight > this.maxWeight) {
      this.delete(this.entries.keys().next().value)
    }
  }

  clear() {
    this.entries.clear()
    this.totalWeight = 0
  }
}

export function manifestDirectories(trackPath, root) {
  const result = []
  let parent = trackPath.slice(0, trackPath.lastIndexOf("/"))
  while (parent === root || parent.startsWith(`${root}/`)) {
    result.push(parent)
    if (parent === root) break
    parent = parent.slice(0, parent.lastIndexOf("/"))
  }
  return result
}

export function matchAudioSource(sources = [], track, relative) {
  const exact = sources.find(source => source.id === relative || source.alistPath === track.path)
  if (exact) return exact
  const named = sources.filter(source => source.id === track.name || source.name === track.name)
  return named.length === 1 ? named[0] : null
}

export function segmentsForTrack(timeline, sources = [], source, track, relative) {
  const exact = timeline.filter(segment => segment.audioSourceId === (source?.id || relative))
  if (exact.length) return exact
  const named = sources.filter(item => item.name === track.name || item.id === track.name)
  if (named.length <= 1) {
    const legacy = timeline.filter(segment => segment.audioSourceId === track.name)
    if (legacy.length) return legacy
  }
  return timeline.some(segment => segment.audioSourceId) ? [] : timeline
}

export async function findEpubInPages(path, fetchPage, isCurrent) {
  let count = 0
  for (let page = 1; isCurrent(); page++) {
    const data = await fetchPage(path, page)
    if (!isCurrent()) return null
    const batch = data?.content || []
    const epub = batch.find(item => !item.is_dir && /\.epub$/i.test(item.name))
    if (epub) return epub
    count += batch.length
    if (!batch.length || (data.total != null && count >= data.total)) return null
  }
  return null
}
