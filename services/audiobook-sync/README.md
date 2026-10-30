# Audiobook user sync

The service validates each request against Alist `/api/me`, then stores each account's progress and bookmarks in a local SQLite database. Tokens are forwarded for authentication and are never stored. Clients keep changes in IndexedDB and use revision checks; conflicts require a choice, and bookmarks use tombstones for deletion. The same SQLite file contains a non-user-specific FTS5 metadata index for global audiobook search; the search API remains authenticated.

The NUC deployment runs the `garden-audiobook-sync` Docker container on the existing `proxy_network`. The Nginx HTTPS location in `nginx-location.conf` proxies to that container; it has no published host port. Its Python code is mounted read-only from `~/.local/lib/garden-sync/`, and the SQLite database is mounted from `~/.local/share/garden-sync/`. Keep SQLite on a local disk and protect both directories with user-only permissions. Back up using `backup.py` and SQLite's online backup API, including regular restore tests; do not copy the database file alone while WAL writes are active.

Authentication is mandatory on every request; CORS is restricted to the two configured frontends. A reverse proxy is required for TLS and access from clients. The initial host user service was retained alongside the container; it is not used by Nginx. The container setup is recorded in `compose.yaml` and must be reviewed against existing server paths and the configured network before reuse.

Deploy the service with `node services/audiobook-sync/deploy-nuc.mjs`. It creates a SQLite online-backup and copies the previous service and Nginx configuration into a dated NUC backup folder before changing anything.

After a library change, rebuild the metadata-only index on the NUC host (this reads directory names, `summaries.json`, EPUB creator metadata, and track names; it never changes book files):

```sh
python3 ~/.local/lib/garden-sync/library_index.py ~/.local/share/garden-sync/sync.sqlite3 /mnt/750/Music/有声书 /多媒体/750HD/有声书
```

Run tests with `python3 -m unittest discover -s services/audiobook-sync -v` and `node --test studio/audiobooks/user-sync.test.mjs`.
