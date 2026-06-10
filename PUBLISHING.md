# Publishing Notes

## Daily workflow

1. Add frontmatter to any Obsidian note you want to publish:

```yaml
---
title: Example Title
date: 2026-06-10
tags:
  - Obsidian
  - Writing
publish: true
---
```

2. Sync published notes into Quartz:

```bash
npm run publish-notes
```

3. Preview locally:

```bash
npm run preview
```

4. Commit and push:

```bash
git add .
git commit -m "Publish notes"
git push
```

Cloudflare Pages will rebuild the site after GitHub receives the push.

## Change the Obsidian vault path

Default vault path:

```text
/Users/jerryyi/Library/Mobile Documents/iCloud~md~obsidian/Documents
```

For another vault:

```bash
VAULT_PATH="/absolute/path/to/vault" npm run publish-notes
```

## Cloudflare Workers settings

Cloudflare now deploys static sites through Workers Static Assets.
Connect the GitHub repository to a Worker and use these build settings:

```text
Production branch: v5
Build command: npm ci && npm run build
Deploy command: npx wrangler deploy
Root directory: /
```

Recommended custom domain:

```text
notes.melyi.uk
```

## Publish standalone HTML

Put already-generated HTML pages in the `html` folder. They are copied to
`public/html` after Quartz builds.

Examples:

```text
html/demo/index.html -> https://notes.melyi.uk/html/demo/
html/report.html -> https://notes.melyi.uk/html/report.html
```

The homepage automatically adds an "独立网页" section for every `.html` file
inside the `html` folder.

## One-command publishing

Publish Obsidian notes and standalone HTML together:

```bash
npm run publish
```

With a custom commit message:

```bash
npm run publish -- "Publish new reading notes"
```

The command syncs `publish: true` Obsidian notes, rebuilds the site, commits
changed `content` and `html` files, and pushes to GitHub. Cloudflare deploys
automatically after the push.

## Optional home-server publishing

To publish the same built site to a home server, set `HOME_SERVER_TARGET` to an
SSH destination that points at the nginx html directory:

```bash
HOME_SERVER_TARGET="user@home-server:/path/to/docker-compose/nginx/html/" npm run publish
```

Example:

```bash
HOME_SERVER_TARGET="jerry@192.168.1.10:/opt/nginx/html/" npm run publish
```

This uses `rsync -az public/ "$HOME_SERVER_TARGET"` and does not delete remote
files by default.
