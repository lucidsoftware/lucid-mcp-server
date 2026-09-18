# Lucid Plugin for Claude

Connect Claude to the Lucid MCP server for working with Lucid documents, diagrams, boards, and resources.

This plugin bundles the remote MCP configuration and a Lucid skill.

## Installation

For local testing or installation directly from this repository, add it as a plugin marketplace and install Lucid:

```text
/plugin marketplace add lucidsoftware/lucid-mcp-server
/plugin install lucid@lucid-mcp-server
```

If Claude Code asks you to reload plugins, run `/reload-plugins`.

After acceptance into Anthropic's public marketplace, users can instead discover **Lucid** at [claude.com/plugins](https://claude.com/plugins) or install it from the official catalog:

```text
/plugin install lucid@claude-plugins-official
```

## Authentication

The plugin connects to `https://mcp.lucid.app/mcp` over streamable HTTP. On first use, open `/mcp`, select the Lucid server, and complete the OAuth sign-in flow. No client secret is stored in this plugin.

Team and Enterprise administrators must first enable MCP access under **Admin → Security → AI controls** in Lucid. Lucid MCP is not available for FedRAMP accounts.

## Local development

Load the plugin directory directly from the repository root:

```bash
claude --plugin-dir ./claude
```

Validate the plugin manifest and component layout:

```bash
claude plugin validate ./claude --strict
```

After changing the manifest, MCP configuration, or skill layout, run `/reload-plugins` in Claude Code.

## Layout

```text
claude/
├── .claude-plugin/
│   └── plugin.json       # plugin metadata and inline MCP server config
├── skills/
│   └── lucid/
│       └── SKILL.md      # Lucid workflow guidance
└── README.md
```

Only `plugin.json` belongs inside `.claude-plugin/`. Claude Code discovers skills and other plugin components relative to the plugin root.

## Support

- [Lucid MCP setup guide](https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server)
- [Repository issues](https://github.com/lucidsoftware/lucid-mcp-server/issues)
- [Lucid support](https://lucid.co/support)
