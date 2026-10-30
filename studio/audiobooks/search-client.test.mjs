import assert from 'node:assert/strict'
import test from 'node:test'
import { canSearch, normalizedSearchQuery, searchUrl } from './search-client.js'

test('global search normalizes query and encodes the request URL', () => {
  assert.equal(normalizedSearchQuery('  George   Orwell  '), 'George Orwell')
  assert.equal(canSearch('1984'), true)
  assert.equal(canSearch(''), false)
  assert.equal(searchUrl('乔治 奥威尔'), 'https://melyi.uk:8089/sync/v1/search?q=%E4%B9%94%E6%B2%BB%20%E5%A5%A5%E5%A8%81%E5%B0%94')
})
