# Audiobook user sync

The service validates each request against Alist `/api/me`, then stores each account's progress and bookmarks in a local SQLite database. Tokens are forwarded for authentication and are never stored. Clients keep changes in IndexedDB and use revision checks; conflicts require a choice, and bookmarks use tombstones for deletion.

The NUC deployment uses the user service `garden-sync.service`, a SQLite database under `~/.local/share/garden-sync/`, and an HTTPS Nginx location as shown in `nginx-location.conf`. The Docker bridge address is an environment-specific value: confirm the live `proxy_network` gateway before deploying. Keep SQLite on a local disk and protect the service directory and database with user-only permissions. Back up using SQLite's online backup API, including regular restore tests; do not copy the database file alone while WAL writes are active.

The service binds only the Docker bridge gateway. Authentication is mandatory on every request; CORS is restricted to the two configured frontends. A reverse proxy is still required for TLS and access from clients. Do not enable or expose this service until the deployment and user-isolation tests pass and the proposed NUC file changes have been approved.

Run tests with `python3 -m unittest discover -s services/audiobook-sync -v` and `node --test studio/audiobooks/user-sync.test.mjs`.
