---
name: lucid
description: "Use when working with Lucidchart, Lucidspark, or Lucidscale tasks: search/list documents, fetch or summarize content, create or edit diagrams, export, share, comment, or work with Lucid IDs/URLs through the Lucid MCP."
---

# Lucid
Use the currently exposed Lucid MCP tools as the source of truth.

## Workflow
1. Match the user's goal to the most specific available Lucid MCP tool.
2. Prefer stable IDs or URLs. Search/list before asking when discovery is possible.
3. Read any required `lucid://...` resource before calling a tool that requires it.
4. Fetch current document/page/item state before editing existing content.
5. Ask for one missing source artifact when creation or modification depends on unavailable input.
6. Confirm before destructive actions, bulk changes, broad permission changes, or anonymous share links.
7. Report the affected document/page/item/thread IDs, returned URLs, exported files, and key assumptions.

## Intent Routing
- For discovery, history, folders, or unknown documents, use search/list tools before asking for an ID.
- For large documents, search distinctive text first, then fetch only the relevant page or region when possible.
- For document understanding, fetch the smallest useful scope and summarize only MCP-provided content.
- For edits, fetch or search first to identify current page/item IDs and nearby context.
- For creation, use the most specific creator available. For general diagram/import tools, follow all tool prerequisites and required resources.
- For export, sharing, comments, or collaboration, prefer exact document/thread IDs and report returned files, URLs, roles, or comment IDs.

## Source Dependency Gate
- Before creating or modifying Lucid content, check whether the request depends on an unavailable source artifact such as an uploaded file, link, spreadsheet, PDF, image, selected content, prior diagram, or pasted text.
- If required source content is missing, ask one concise question for it. Do not generate a generic substitute.

## Guardrails
- Treat MCP responses as ground truth. Do not invent document contents, object IDs, resource names, supported shapes, or tool capabilities.
- Use Lucid resource libraries when tool descriptions reference them.
- Read current document state before editing existing content.
- Re-fetch or otherwise verify after meaningful edits when practical.
- Confirm first when the operation is destructive, broad, permission-related, anonymous-sharing-related, or ambiguous in scope.

## Reporting
- For read-only work, report the key result, including when nothing matched.
- For creation or edits, name what changed and include relevant document/page/item/thread IDs, returned URLs or files, and any layout, routing, or source assumptions.
