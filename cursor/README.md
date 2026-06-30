# Lucid Cursor Plugin

Connect Cursor to the Lucid MCP for working with Lucid documents, diagrams, boards, and resources.

For general MCP server setup across all clients, see the [repository README](../README.md).

## Prerequisites

1. Your Lucid account admin must enable MCP access in the Lucid Admin Panel.
2. Connect the Lucid MCP server in Cursor at **Settings → Tools & MCP**, or install this plugin to bundle the MCP config via `mcp.json`.
3. Complete the OAuth sign-in when Cursor first connects to Lucid.

## Installation

Install from the Cursor plugin marketplace:

```bash
/add-plugin lucid
```

### Local development

This plugin lives in the `cursor/` subfolder of the repository. To load it locally while keeping the full repo layout, symlink the plugin folder:

```bash
ln -sfn "$(pwd)/cursor" ~/.cursor/plugins/local/lucid-dev
```

Then enable the plugin in Cursor or run `/add-plugin lucid-dev`.

## Skills

| Skill | Description |
|:------|:------------|
| `lucid` | Search, fetch, create, edit, export, share, and comment on Lucid documents via the Lucid MCP. |

## Example prompts

- "Find and summarize my Lucid document about onboarding."
- "Create a flowchart from this code in Lucid."
- "Export this Lucidchart page as PNG."
- "Add a comment to this Lucid document."

## License

[Apache License 2.0](../LICENSE) © Lucid Software Inc.
