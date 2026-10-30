export const MIN_SEARCH_LENGTH = 1

export function normalizedSearchQuery(value) {
  return String(value || '').trim().replace(/\s+/g, ' ')
}

export function canSearch(value) {
  const query = normalizedSearchQuery(value)
  return query.length >= MIN_SEARCH_LENGTH && query.length <= 100
}

export function searchUrl(query) {
  return `https://melyi.uk:8089/sync/v1/search?q=${encodeURIComponent(normalizedSearchQuery(query))}`
}
