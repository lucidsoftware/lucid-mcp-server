# Lucid Cursor Plugin

Connect Cursor to the Lucid MCP for working with Lucid documents, diagrams, boards, and resources.

This plugin bundles the Lucid MCP server configuration and a unified agent skill so Cursor can search, fetch, create, edit, export, share, and comment on Lucid content.

## MCP server

| | |
|:--|:--|
| **Endpoint** | `https://mcp.lucid.app/mcp` |
| **Transport** | Streamable HTTP |
| **Auth** | OAuth 2.0 with Dynamic Client Registration (DCR) |
| **Plans** | Free, Individual, Team, and Enterprise. Not available on [FedRAMP](https://help.lucid.co/hc/en-us/articles/8780203563284) accounts. |

Installing this plugin adds the Lucid MCP server via the bundled `mcp.json`. You can also connect manually in **Settings → Tools & MCP**:

```json
{
  "mcpServers": {
    "lucid": {
      "url": "https://mcp.lucid.app/mcp"
    }
  }
}
```

On first connect, complete the OAuth sign-in when Cursor prompts you. Lucid uses Dynamic Client Registration, so no fixed client ID or secret is required in the config.

## Prerequisites

1. **Admin access (Team/Enterprise):** An account admin must enable MCP in the Lucid Admin Panel:
   - Open **Admin** → **Security** → **Feature controls**
   - Under **MCP access**, enable **Allow users to connect**
   - Confirm with **Enable MCP**
2. **Authenticate:** After installing the plugin, connect the Lucid MCP server in Cursor and complete OAuth when prompted.

Setup guide: [Integrate Lucid with AI tools using the Lucid MCP server](https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server)

## Installation

Install from the Cursor plugin marketplace:

```bash
/add-plugin lucid
```

Or enable the plugin in **Settings → Plugins**.

## Skills

| Skill | Description |
|:------|:------------|
| `lucid` | Search, fetch, create, edit, export, share, and comment on Lucid documents via the Lucid MCP. |

The skill is tool-agnostic — it uses the currently exposed Lucid MCP tools as the source of truth rather than a static tool list.

## What you can do

With the Lucid MCP server connected, you can ask Cursor to:

- **Search** Lucid documents for specific content
- **Summarize** document details and action items
- **Create shareable links** with the permission level you specify
- **Share documents** with collaborators by email
- **Create diagrams** from a natural-language prompt
- **Create org charts** from a CSV file or text
- **Edit, add, or delete shapes** in an existing document
- **Generate UML sequence diagrams** from PlantUML markup
- **Export documents** as PNG
- **Fetch images** attached to shapes in a document

## Example prompts

```
Show me all Lucid documents that talk about the website redesign project.
```

```
Find the 'Q4 Website Redesign Workflow' document in Lucid, and give me a summary of action items.
```

```
Create a diagram in Lucid that maps out a user authentication flow.
```

```
In my Lucid IT Escalation Process document, update all decision blocks to a red fill with bold white text.
```

```
Create a shareable link with view-only permissions for my 'FY26 Q3 Product Roadmap' document in Lucid.
```

```
Find and summarize my Lucid document about onboarding.
```

```
Export this Lucidchart page as PNG.
```

## Authentication & data handling

- Authentication uses **OAuth 2.0** with Dynamic Client Registration (DCR).
- The Lucid MCP server can access any Lucid document you have permission to access within your account. It cannot access documents owned by users outside your account.
- The server acts as a **pass-through** — it does not retain document content, user prompts, or queries. Your credentials are never shared outside your Lucid account.

> AI tools you set up with the Lucid MCP server are Non-Lucid Applications (as defined in Lucid's [Terms of Service](https://lucid.co/tos)). Your use of these AI tools is subject to the agreement between you and the third-party provider.

## Support & feedback

- **Setup help:** [Lucid Help Center — MCP integration](https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server)
- **General Lucid support:** [lucid.co/support](https://lucid.co/support)

## License

Apache License 2.0 © Lucid Software Inc.
