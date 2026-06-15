# Lucid MCP Server

Connect your AI tools to Lucid to intelligently search for files, create visuals, and share with your team.

The Lucid Model Context Protocol (MCP) server is a cloud-hosted bridge between your Lucid documents and AI tools such as ChatGPT, Claude, Microsoft Copilot, and Cursor. Once connected, you can use natural language to search, retrieve, edit, summarize, and create Lucid documents from inside your AI client.

- **Endpoint:** `https://mcp.lucid.app/mcp`
- **Transport:** Streamable HTTP
- **Auth:** OAuth 2.0 with Dynamic Client Registration (DCR)
- **Plans:** Free, Individual, Team, and Enterprise. Not available on [FedRAMP](https://help.lucid.co/hc/en-us/articles/8780203563284) accounts.
- **Marketplace listing:** [lucid.co/marketplace/e16391cc/lucid-mcp-server](https://lucid.co/marketplace/e16391cc/lucid-mcp-server)
- **Setup guide:** [Integrate Lucid with AI tools using the Lucid MCP server](https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server)

---

## What you can do

With the Lucid MCP server connected, you can prompt your AI tool to:

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
- **Convert visual output** from Claude into a Lucid document

### Example prompts

```
"Show me all Lucid documents that talk about the website redesign project."
```

```
"Find the 'Q4 Website Redesign Workflow' document in Lucid, and give me a summary of action items."
```

```
"Create a diagram in Lucid that maps out a user authentication flow."
```

```
"In my Lucid IT Escalation Process document, update all decision blocks to a red fill with bold white text."
```

```
"Create a shareable link with view-only permissions for my 'FY26 Q3 Product Roadmap' document in Lucid."
```

---

## Supported clients

The Lucid MCP server is compatible with any MCP client. For one-click setup, Lucid offers dedicated connectors for ChatGPT and Claude:

- [Connect Lucid to ChatGPT](https://help.lucid.co/hc/en-us/articles/47991410649492-Connect-Lucid-to-ChatGPT)
- [Connect Lucid to Claude](https://help.lucid.co/hc/en-us/articles/47850709372180-Connect-Lucid-to-Claude)

For other clients, follow the MCP-setup docs for your tool of choice and use the server URL `https://mcp.lucid.app/mcp`:

| Client | Setup docs |
|---|---|
| ChatGPT | [Developer mode](https://platform.openai.com/docs/guides/developer-mode) |
| Claude desktop | [Local MCP servers on Claude desktop](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop) |
| Claude web | [Custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp) |
| Claude Code | [Installing MCP servers](https://docs.claude.com/en/docs/claude-code/mcp#installing-mcp-servers) |
| Microsoft Copilot Studio | [Add an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent) |
| GitHub Copilot | [Extend Copilot Chat with MCP](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/extend-copilot-chat-with-mcp) |
| Cursor | [MCP context](https://cursor.com/docs/context/mcp) |
| Windsurf | [Configuring your first MCP server](https://windsurf.com/university/tutorials/configuring-first-mcp-server) |

This is not an exhaustive list — the Lucid MCP server works with any MCP-compatible client.

> AI tools you set up with the Lucid MCP server are Non-Lucid Applications (as defined in our [Terms of Service](https://lucid.co/tos)). Your use of these AI tools is subject to the agreement between you and the third-party provider.

---

## JSON config

Some clients require you to edit a JSON config file directly.

**If your client supports the HTTP transport:**

```json
"Lucid Software": {
  "type": "http",
  "url": "https://mcp.lucid.app/mcp"
}
```

**If your client does not support HTTP transport**, use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) Node.js package to forward stdio requests to the Lucid MCP server. Node.js must be installed.

```json
"Lucid Software": {
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://mcp.lucid.app/mcp"]
}
```

---

## For admins: enable or disable the MCP server

Admins on **Team** and **Enterprise** accounts can control whether users can connect to the Lucid MCP server.

1. In your Lucid account, select **Admin** from the left-side panel.
2. Click **Security** in the left-side menu.
3. Select **Feature controls**.
4. Under **MCP access**, use the toggle next to **Allow users to connect**.
5. Confirm with **Enable MCP** or **Disable MCP** in the modal.

Granting access allows users to connect from any AI client. To restrict access to specific AI tools, you'll need to disable the MCP server at the account level.

---

## Authentication & data handling

- Authentication uses **OAuth 2.0** with Dynamic Client Registration (DCR).
- The Lucid MCP server can access any Lucid document you have permission to access within your account. It cannot access documents owned by users outside your account.
- The server acts as a **pass-through** — it does not retain document content, user prompts, or queries. Your credentials are never shared outside your Lucid account.

---

## FAQ

See [FAQ.md](FAQ.md) for answers to common questions about how the server works, what it can access, how data is handled, the diagram types it can create, and how it differs from standard text-to-AI connections.

---

## Support & feedback

- **Setup help:** [Lucid Help Center article](https://help.lucid.co/hc/en-us/articles/42578801807508-Integrate-Lucid-with-AI-tools-using-the-Lucid-MCP-server)
- **Issues & feature requests:** [Open an issue](../../issues) in this repository
- **General Lucid support:** [lucid.co/support](https://lucid.co/support)

---

## License

[Apache License 2.0](LICENSE) © Lucid Software Inc.
