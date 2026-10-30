// Queue every local mutation; never hold the lock across a network request.
export class UserSync {
  constructor({ request, list, put, onChange = () => {}, lockName = null }) {
    this.request = request
    this.list = list
    this.put = put
    this.onChange = onChange
    this.lockName = lockName
    this.running = null
    this.lock = Promise.resolve()
  }

  exclusive(fn) {
    const next = this.lock.then(() => this.lockName && globalThis.navigator?.locks
      ? globalThis.navigator.locks.request(this.lockName, fn)
      : fn())
    this.lock = next.catch(() => {})
    return next
  }

  save(kind, id, value) {
    return this.exclusive(async () => {
      const old = (await this.list()).find(row => row.kind === kind && row.id === id)
      const row = { kind, id, value, revision: old?.revision ?? 0,
        generation: (old?.generation ?? 0) + 1, dirty: true, conflict: old?.conflict ?? null }
      await this.put(row)
      this.onChange(row)
      return row
    })
  }

  seed(kind, id, value) {
    return this.exclusive(async () => {
      if ((await this.list()).some(row => row.kind === kind && row.id === id)) return false
      const row = { kind, id, value, revision: 0, generation: 1, dirty: true, conflict: null }
      await this.put(row)
      this.onChange(row)
      return true
    })
  }

  async sync() {
    if (this.running) return this.running
    this.running = this.performSync().finally(() => { this.running = null })
    return this.running
  }

  async performSync() {
    const remote = await this.request('GET')
    await this.exclusive(async () => {
      const local = await this.list()
      const index = new Map(local.map(row => [JSON.stringify([row.kind, row.id]), row]))
      for (const item of remote.items) {
        const existing = index.get(JSON.stringify([item.kind, item.id]))
        let row = null
        if (!existing) row = { kind: item.kind, id: item.id, value: item.value, revision: item.revision, generation: 0, dirty: false, conflict: null }
        else if (!existing.dirty && item.revision > existing.revision) row = { ...existing, value: item.value, revision: item.revision, conflict: null }
        else if (!existing.dirty && item.revision < existing.revision) row = { ...existing, dirty: true, conflict: item }
        else if (existing.dirty && item.revision !== existing.revision) row = { ...existing, conflict: item }
        if (row) { await this.put(row); this.onChange(row) }
      }
      const remoteKeys = new Set(remote.items.map(item => JSON.stringify([item.kind, item.id])))
      for (const existing of local) {
        if (existing.revision > 0 && !remoteKeys.has(JSON.stringify([existing.kind, existing.id]))) {
          const row = { ...existing, dirty: true, conflict: { revision: 0, value: null, missing: true } }
          await this.put(row)
          this.onChange(row)
        }
      }
    })
    const snapshots = await this.exclusive(() => this.list())
    for (const snapshot of snapshots) {
      if (!snapshot.dirty || snapshot.conflict) continue
      try {
        const result = await this.request('POST', { kind: snapshot.kind, id: snapshot.id, revision: snapshot.revision, value: snapshot.value })
        await this.exclusive(async () => {
          const current = (await this.list()).find(row => row.kind === snapshot.kind && row.id === snapshot.id)
          if (!current) return
          const row = { ...current, revision: result.revision, dirty: current.generation !== snapshot.generation }
          await this.put(row)
          this.onChange(row)
        })
      } catch (error) {
        if (error.status !== 409) throw error
        await this.exclusive(async () => {
          const current = (await this.list()).find(row => row.kind === snapshot.kind && row.id === snapshot.id)
          if (!current) return
          if (error.current && current.revision === error.current.revision) return
          const row = { ...current, conflict: error.current || { revision: 0, value: null, missing: true } }
          await this.put(row)
          this.onChange(row)
        })
      }
    }
  }

  resolve(kind, id, choice) {
    return this.exclusive(async () => {
      const current = (await this.list()).find(row => row.kind === kind && row.id === id)
      if (!current?.conflict || !['local', 'remote'].includes(choice)) throw new Error('Invalid conflict resolution')
      const conflict = current.conflict
      if (choice === 'remote' && conflict.missing) throw new Error('No remote value exists')
      const row = { ...current, revision: conflict.revision, conflict: null,
        value: choice === 'remote' ? conflict.value : current.value,
        dirty: choice === 'local', generation: current.generation + 1 }
      await this.put(row)
      this.onChange(row)
      return row
    })
  }
}
