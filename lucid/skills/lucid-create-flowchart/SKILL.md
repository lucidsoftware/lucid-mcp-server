---
name: lucid-create-flowchart
description: 'Create an editable Lucid flowchart to show the steps and decision branches of a process. Use when a flowchart is the intended diagram type.'
user-invocable: true
metadata:
    version: 1.0
    author: 'Lucid Software'
---

# Create Flowchart

Create an editable Lucid flowchart faithful to the user's source process.

## Load MCP guidance

Use `get_mcp_resource` to read `lucid://skills/readme`, then `lucid://skills/diagram-layout-flowchart` and its linked `lucid://skills/diagram-layout` resource before building. Follow those resources for flow planning, shape semantics, placement, decision labels, routing, and verification. Load current Script API documentation as directed there.

## Creation conventions

- Draw only steps, decisions, and outcomes supported by the source. State inferred steps as assumptions. If a branch's destination is unknown, end it at a terminator labeled with what is known.
- Use the Flowchart shape library. Use specialized shapes only when the process calls for them, such as data input/output, manual operations, predefined subprocesses, documents, databases, or delays.
- Show parallel work as branches that rejoin at an explicit join step; these are not decision exits and need no branch labels.
- Prefer one page. Use off-page links only when the flow is too large to read on one page or multiple pages are requested.
- Avoid emoji in labels; Lucid can render them as black boxes.
- Name the document after the process, for example, "Flowchart: Employee Onboarding".

Unless the user specifies colors, use these fills consistently:

| Meaning                   | Fill      |
| ------------------------- | --------- |
| Start / end               | `#D1E7DD` |
| Process step              | `#DCE8F7` |
| Decision                  | `#FFF3CD` |
| Exception or failure path | `#F8D7DA` |

Explain colors and non-obvious shapes with small matching samples in a container titled "Legend", clear of the flow. Use consistent font sizes and centered labels. Include labeled line samples when line styles carry meaning.

## Build and deliver

Follow the loaded MCP guidance to validate and repair the created diagram. Report unresolved issues; if document classification blocks access, stop and share the link.

Return a brief summary of the flow, assumptions or unresolved source gaps, and the edit link.
