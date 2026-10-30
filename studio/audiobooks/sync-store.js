export async function openSyncStore(indexedDb = indexedDB) {
  const db = await new Promise((resolve, reject) => {
    const request = indexedDb.open('garden-audiobooks-sync', 1)
    request.onupgradeneeded = () => request.result.createObjectStore('items', { keyPath: 'key' })
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
  return {
    async list(account) {
      return new Promise((resolve, reject) => {
        const request = db.transaction('items').objectStore('items').getAll()
        request.onsuccess = () => resolve(request.result.filter(row => row.account === account).map(({ key, account: owner, ...row }) => row))
        request.onerror = () => reject(request.error)
      })
    },
    async put(account, row) {
      return new Promise((resolve, reject) => {
        const transaction = db.transaction('items', 'readwrite')
        transaction.objectStore('items').put({ ...row, account, key: JSON.stringify([account, row.kind, row.id]) })
        transaction.oncomplete = () => resolve()
        transaction.onerror = () => reject(transaction.error)
        transaction.onabort = () => reject(transaction.error || new Error('Sync store transaction aborted'))
      })
    },
  }
}
