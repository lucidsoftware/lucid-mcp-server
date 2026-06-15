# Lucid MCP Server FAQ

## How does the Lucid MCP server work?

The Lucid MCP server is a remote service available at `https://mcp.lucid.app/mcp`. It uses the streamable HTTP transport protocol and Dynamic Client Registration (DCR) to securely manage client access. Authentication is handled via OAuth 2.0, allowing Lucid users to authorize the MCP server to integrate with their AI tools. During setup, users complete two distinct authorization steps:

- **Server authentication** — verifies and registers the Lucid MCP server as a trusted service.
- **Permission scope approval** — grants the MCP server access to user documents, data, and account operations within Lucid products.

Both authentication and scope approval are required before the Lucid MCP server can interact with a user's account or data.

## Can Enterprise admins restrict access to specific AI clients?

Granting access to the Lucid MCP server allows users to connect to any AI client. If an account needs to restrict access to specific AI tools, you will need to disable the MCP server at the account level.

## What info can the Lucid MCP server access?

The Lucid MCP server can access any Lucid document you have permissions to access within your account, including titles, content, comments, and metadata. It cannot access documents owned or created by users outside your account.

## How is my data used by the Lucid MCP server?

The Lucid MCP server acts as a pass-through and does not retain document content, user prompts, or queries. Your credentials are never shared outside your Lucid account. Usage of the Lucid MCP server is subject to the negotiated services agreement between the parties or Lucid's standard Terms of Service available at [lucid.co/tos](https://lucid.co/tos).

## What types of diagrams can the Lucid MCP server create?

The Lucid MCP server can generate any diagram type supported by Lucid, such as flowcharts, org charts, sequence diagrams, and entity relationship diagrams.

While the server can automatically build a diagram from your data (for example, turning a list of employees into an org chart), it creates a static version only. It cannot create data-linked diagrams that automatically update when your source data changes.

## How does the Lucid MCP server differ from standard text-to-AI connections?

The MCP server uses a document-processing format to translate complex diagrams and text into a structure designed for LLMs. This ensures that when you ask for a summary, the AI understands the hierarchy and relationships within your document better than standard text-to-AI connections.
