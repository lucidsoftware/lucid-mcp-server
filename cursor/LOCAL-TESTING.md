# Local plugin testing for marketplace submissions

This guide explains why we use a **`lucid-dev` symlink** when testing the Lucid Cursor plugin before marketplace submission. It applies to any plugin that lives in a **subfolder** of a shared monorepo (like `lucid-mcp-server/cursor/`), not only to Lucid.

---

## TL;DR

| Question | Answer |
|:---------|:-------|
| Why can't I test from `plugins/local/lucid/`? | That folder is the **marketplace repo root**. Cursor expects `plugin.json` at the install root, but ours lives in `cursor/`. |
| What is `lucid-dev`? | A **local-only symlink** pointing at the real plugin directory (`cursor/`). It is **not** committed to git. |
| Is `lucid-dev` a different Lucid backend? | **No.** It hits the same production MCP endpoint (`https://mcp.lucid.app/mcp`) as the shipped plugin. |
| Why do I see `/lucid` instead of `/lucid-dev`? | The slash command comes from the **skill name** (`lucid`), not the local install folder name. |
| Do end users need `lucid-dev`? | **No.** They install `lucid` from the marketplace via `/add-plugin lucid`. |

---

## Background: two layers in one repo

The `lucid-mcp-server` repo serves two audiences:

1. **All MCP clients** — root `README.md`, `FAQ.md`, shared docs
2. **Cursor users** — the plugin under `cursor/`

```
lucid-mcp-server/                 ← marketplace repo root
├── .cursor-plugin/
│   └── marketplace.json            ← indexes plugins in subfolders
├── README.md                       ← all-clients MCP server docs
├── FAQ.md
├── LICENSE
└── cursor/                         ← the actual Cursor plugin
    ├── .cursor-plugin/
    │   └── plugin.json             ← Cursor reads THIS file
    ├── mcp.json
    ├── skills/lucid/SKILL.md
    └── README.md
```

The root `.cursor-plugin/marketplace.json` tells the Cursor marketplace where to find the plugin:

```json
{
  "plugins": [
    {
      "name": "lucid",
      "source": "cursor"
    }
  ]
}
```

This layout is **correct for submission** — it keeps Cursor-specific files separate from shared MCP documentation. It is also why local testing needs an extra step.

---

## How Cursor loads local plugins

Cursor discovers local plugins under:

```
~/.cursor/plugins/local/<install-name>/
```

For each folder, Cursor looks for a plugin manifest at:

```
<install-name>/.cursor-plugin/plugin.json
```

If `plugin.json` is missing at that level, Cursor does **not** treat the folder as an installable plugin — even if a valid plugin exists one directory deeper.

### What goes wrong with `plugins/local/lucid/` alone

When you clone or copy the full repo to `~/.cursor/plugins/local/lucid/`, the tree looks like:

```
plugins/local/lucid/
├── .cursor-plugin/marketplace.json   ← marketplace index, NOT a plugin manifest
└── cursor/
    └── .cursor-plugin/plugin.json    ← the real plugin (one level too deep)
```

Cursor scans `plugins/local/lucid/` and finds `marketplace.json`, not `plugin.json`. The plugin under `cursor/` is never loaded.

This is the core reason testing from the repo root folder named `lucid` does not work.

---

## What the `lucid-dev` symlink solves

The symlink gives Cursor a local install path whose **root is the plugin directory**:

```
~/.cursor/plugins/local/
├── lucid/                            ← full repo copy (for editing)
└── lucid-dev → lucid/cursor/         ← local-only symlink (for loading)
```

From Cursor's perspective:

```
plugins/local/lucid-dev/
├── .cursor-plugin/plugin.json        ✓ found at install root
├── mcp.json
└── skills/lucid/SKILL.md
```

Edits made in the repo under `lucid/cursor/` are picked up immediately because `lucid-dev` points at the same files.

### Why the name `lucid-dev`?

The folder name is arbitrary. We use `lucid-dev` because:

1. **Avoids collision** with a future marketplace install named `lucid` (you can have both during development, though we recommend disabling one).
2. **Signals intent** — this install is for local development, not what we ship to users.
3. **Distinguishes logs** — MCP logs show `plugin-lucid-dev-lucid` so you can tell local testing apart from a marketplace install.

The name does **not** change user-facing branding. The plugin still displays as **Lucid**, the MCP server key is still `lucid`, and the skill slash command is still `/lucid`.

---

## Naming cheat sheet

Confusion usually comes from mixing up these layers:

| Layer | Name you see | Defined in | Committed to repo? |
|:------|:-------------|:-----------|:-------------------|
| Marketplace repo | `lucid-mcp-server` | Root folder / `marketplace.json` | Yes |
| Marketplace plugin id | `lucid` | `marketplace.json` → `"name": "lucid"` | Yes |
| Local install folder | `lucid-dev` | Symlink on your machine | **No** |
| Plugin display name | `Lucid` | `cursor/.cursor-plugin/plugin.json` | Yes |
| MCP server key | `lucid` | `cursor/mcp.json` | Yes |
| Skill / slash command | `/lucid` | `cursor/skills/lucid/SKILL.md` | Yes |
| Internal Cursor id (logs) | `plugin-lucid-dev-lucid` | Derived from install folder + MCP key | N/A |

---

## Setup (one-time per machine)

### 1. Clone or copy the repo locally

Either work directly in your git clone:

```bash
git clone git@github.com:lucidsoftware/lucid-mcp-server.git
cd lucid-mcp-server
```

Or keep a working copy under Cursor's local plugins directory (common during active development):

```bash
cp -R /path/to/lucid-mcp-server ~/.cursor/plugins/local/lucid
```

### 2. Create the symlink

Point a local install name at the **`cursor/`** plugin directory — not the repo root:

```bash
ln -sfn ~/.cursor/plugins/local/lucid/cursor ~/.cursor/plugins/local/lucid-dev
```

If you prefer to symlink straight from your git clone (no extra copy):

```bash
ln -sfn ~/path/to/lucid-mcp-server/cursor ~/.cursor/plugins/local/lucid-dev
```

### 3. Enable the plugin in Cursor

```bash
/add-plugin lucid-dev
```

Or enable it under **Settings → Plugins**.

### 4. Connect MCP (first time only)

Complete OAuth when Cursor prompts you. The bundled `mcp.json` points at production:

```json
{
  "mcpServers": {
    "lucid": {
      "url": "https://mcp.lucid.app/mcp"
    }
  }
}
```

Local testing uses the **same endpoint** end users will use after marketplace install. There is no separate "dev MCP server" in this setup.

---

## Verification checklist

Use this before opening a marketplace PR or tagging a release.

| Step | Pass criteria |
|:-----|:--------------|
| Symlink exists | `readlink ~/.cursor/plugins/local/lucid-dev` → `.../cursor` |
| Plugin loads | **Settings → Plugins** shows Lucid enabled |
| MCP connected | **Settings → Tools & MCP** shows `lucid` connected (green) |
| OAuth works | First tool call succeeds without `needsAuth` |
| Skill available | Typing `/lucid` in chat offers the Lucid skill |
| Edit loop | Change `cursor/skills/lucid/SKILL.md`, restart/reload if needed, confirm behavior updates |
| Logs | `~/Library/Application Support/Cursor/logs/.../mcp-server-plugin-lucid-dev-lucid.log` shows `Successfully connected` |

Quick functional smoke test — ask the agent to list your Lucid root folder, or invoke the `lucid_list_folder_contents` MCP tool.

---

## Alternatives (and trade-offs)

### Option A: Symlink to `cursor/` (recommended)

```
lucid-dev → .../lucid-mcp-server/cursor
```

**Pros:** Keeps marketplace repo layout intact; edits are live; matches how Cursor resolves `source: "cursor"` in `marketplace.json`.

**Cons:** Requires one local symlink per developer (not committed).

### Option B: Flatten the plugin to the install root

Move `plugin.json`, `mcp.json`, and `skills/` to `plugins/local/lucid/` directly.

**Pros:** No symlink.

**Cons:** Breaks the monorepo layout required for marketplace submission; you would maintain two different directory structures.

### Option C: Test only after marketplace publish

Install via `/add-plugin lucid` from the marketplace.

**Pros:** Exactly matches end-user experience.

**Cons:** Slow feedback loop; not suitable for pre-submission iteration.

**Recommendation:** Use Option A for day-to-day development; run Option C once before final submission to validate the published artifact.

---

## What to commit vs keep local

| Path | Commit? | Notes |
|:-----|:--------|:------|
| `cursor/.cursor-plugin/plugin.json` | Yes | Shipped plugin manifest |
| `cursor/mcp.json` | Yes | Bundled MCP config |
| `cursor/skills/` | Yes | Shipped skills |
| `.cursor-plugin/marketplace.json` | Yes | Marketplace index |
| `~/.cursor/plugins/local/lucid-dev` | **No** | Developer symlink only |
| OAuth tokens | **No** | Stored by Cursor locally after sign-in |

Add `lucid-dev` to personal setup notes or an internal runbook — not to the repo.

---

## Common questions

### "Why can't I just test from the `lucid` folder?"

You can — but you must test from **`lucid/cursor/`**, not `lucid/` itself. The repo root is a marketplace wrapper. Without the symlink (or flattening), Cursor never reaches the plugin manifest.

### "Do I need both `lucid` and `lucid-dev` enabled?"

No. Prefer **one** local install during development. Running both a marketplace `lucid` install and a local `lucid-dev` install can register duplicate MCP servers.

### "Is `lucid-dev` a staging environment?"

No. It only changes **where Cursor reads plugin files from**. The MCP endpoint remains `https://mcp.lucid.app/mcp`.

### "Will users see `lucid-dev`?"

No. Users install **`lucid`** from the marketplace. They never create a symlink.

---

## Template for future marketplace submissions

When adding another Cursor plugin to a shared repo:

1. Put the plugin in a subfolder (e.g. `cursor/`, `vscode/`, `my-plugin/`).
2. Register it in root `.cursor-plugin/marketplace.json` with `"source": "<subfolder>"`.
3. On each dev machine, symlink `~/.cursor/plugins/local/<name>-dev` → `<repo>/<subfolder>`.
4. Load with `/add-plugin <name>-dev`.
5. Ship to users as `<name>` via the marketplace — no symlink required.

---

## Related docs

- [`cursor/README.md`](./README.md) — end-user install and usage
- [Root `README.md`](../README.md) — Lucid MCP server docs for all clients
- Cursor plugin scaffolding: `/add-plugin create-plugin` (includes marketplace layout guidance)
