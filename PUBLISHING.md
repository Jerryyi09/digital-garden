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

## Cloudflare Pages settings

Use these settings when connecting the GitHub repository:

```text
Production branch: v5
Build command: npm ci && npm run build
Build output directory: public
```

Recommended custom domain:

```text
notes.melyi.uk
```
