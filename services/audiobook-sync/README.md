# Audiobook user sync

The service validates each request against Alist `/api/me`, then stores each account's progress and bookmarks in a local SQLite database. Tokens are forwarded for authentication and are never stored. Clients keep changes in IndexedDB and use revision checks; conflicts require a choice, and bookmarks use tombstones for deletion.

The NUC deployment runs the `garden-audiobook-sync` Docker container on the existing `proxy_network`. The Nginx HTTPS location in `nginx-location.conf` proxies to that container; it has no published host port. Its Python code is mounted read-only from `~/.local/lib/garden-sync/`, and the SQLite database is mounted from `~/.local/share/garden-sync/`. Keep SQLite on a local disk and protect both directories with user-only permissions. Back up using `backup.py` and SQLite's online backup API, including regular restore tests; do not copy the database file alone while WAL writes are active.

Authentication is mandatory on every request; CORS is restricted to the two configured frontends. A reverse proxy is required for TLS and access from clients. The initial host user service was retained alongside the container; it is not used by Nginx. The container setup is recorded in `compose.yaml` and must be reviewed against existing server paths and the configured network before reuse.

Run tests with `python3 -m unittest discover -s services/audiobook-sync -v` and `node --test studio/audiobooks/user-sync.test.mjs`.
