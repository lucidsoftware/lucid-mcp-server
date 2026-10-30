---
name: lucid-diagram-bpmn
description: Creates an editable Lucid BPMN 2.0 process diagram from a process description or step table, using BPMN shapes and sequence, message, and association flows. Use only when the user explicitly says "BPMN" or invokes this skill. Do not use for generic workflow, process diagram, or flowchart requests without "BPMN".
---

## Goal

Turn the user's process description into an editable Lucid diagram using BPMN 2.0 notation. Strive to deliver a complete and polished diagram. Make sure text does not overlap a pool, lane, or shape border. Verify the structure and rendered layout, then provide the edit URL. Provide document JSON only when requested.

## Why this skill exists

A flowchart made from ordinary rectangles and diamonds may look like BPMN but loses the shape semantics needed for later editing, re-import, or analysis. BPMN also distinguishes sequence flow within a participant from message flow between participants; confusing those changes the process meaning.

## Inputs

- A process description, step list, transcript, or step table is required. Read the full input before modeling. If the user refers to an unavailable source document, ask for it rather than inventing a process.
- Participant boundaries, triggers, decisions, outcomes, and data may be inferred when the input supports them. State material assumptions before creating the diagram; ask only when an ambiguity would change the process meaning.
- A process name, orientation, and visual style are optional. Infer a concise name and use horizontal lanes. Follow any styling directions, supplied example, or company standard theme. If none is provided, use a reasonable, restrained color palette for the pools and lanes so participants are easy to distinguish.

---

## Hard constraint: BPMN-only shapes

Every shape on the canvas MUST use a `bpmn*` shape type, with exactly one exception: the Container Library `swimLanes` shape may be used for lane structures when the user specifically needs its branded lane headers. No other non-BPMN shape types are permitted, even when they would visually resemble a BPMN element. A generic shape would lose BPMN semantics; `swimLanes` also trades away the lane container's BPMN identity.

**Allowed shape types (the complete list):**

| BPMN element                                            | Lucid `type`         |
| ------------------------------------------------------- | -------------------- |
| Activity (task, subprocess, call activity, transaction) | `bpmnActivity`       |
| Event (start / intermediate / end, all event subtypes)  | `bpmnEvent`          |
| Gateway (exclusive, parallel, inclusive, etc.)          | `bpmnGateway`        |
| Pool with lanes                                         | `bpmnPool`           |
| Collapsed / black-box pool                              | `bpmnBlackBoxPool`   |
| Data object                                             | `bpmnDataObject`     |
| Data store                                              | `bpmnDataStore`      |
| Text annotation                                         | `bpmnTextAnnotation` |
| Group                                                   | `bpmnGroup`          |
| Choreography (rare; include only on explicit request)   | `bpmnChoreography`   |
| Conversation (rare; include only on explicit request)   | `bpmnConversation`   |

**Forbidden shape types** — do NOT emit any of these, even as a fallback:

- Standard Library: `rectangle`, `text`, `hotspot`, `image`, `stickyNote`, `lucidCard`
- Shape Library: `circle`, `diamond`, `hexagon`, `pentagon`, `octagon`, `cloud`, `cross`, `polyStar`, `singleArrow`, `doubleArrow`, `isoscelesTriangle`, `rightTriangle`
- Container Library: `rectangleContainer`, `roundedRectangleContainer`, `circleContainer`, `pillContainer`, `braceContainer`, `bracketContainer`, `diamondContainer` (`swimLanes` is the one permitted exception — see "Pool & lane structure" below)
- Flowchart Library: `process`, `decision`, `terminator`, `database`, `document`, `manualInput`, `delay`, `note`, etc. (BPMN has its own equivalents)
- UML, Lucidspark, Named, and Table libraries

If a non-BPMN need arises (e.g., a free-floating comment), use `bpmnTextAnnotation` — the BPMN 2.0 Library's dedicated annotation shape. Never substitute a Standard Library `text`, `stickyNote`, or Flowchart Library `note` shape for this, even though they'd render similarly. If grouping is needed without semantic flow impact, use `bpmnGroup`. For lane structures, `bpmnPool` is the default choice; `swimLanes` is the one permitted non-BPMN shape and may be used instead when there's a specific reason to — either way, follow the header-naming rule in "Pool & lane structure" below.

Before emitting the JSON, scan every shape and confirm `type` starts with `bpmn`, with the sole allowed exception of a `swimLanes` shape used for lane structure. If any other shape's `type` doesn't start with `bpmn`, replace it or remove it.

---

## Step 1: Parse the requirements

From the user's input, extract:

- **Participants / lanes** — who performs the work (roles, departments, systems). Each becomes a lane within a `bpmnPool`. External parties that interact only via messages are modeled as separate `bpmnBlackBoxPool`s.
- **Start trigger** — what kicks the process off (timer, incoming message, manual, etc.) → `bpmnEvent` with `eventGroup: "start"` and the appropriate `eventType`.
- **Activities** — verb phrases for work participants perform, such as "Validate order", "Charge card", or "Send confirmation" → `bpmnActivity` (default `activityType: "task"`; use `eventSubProcess` for an event-triggered subprocess, `callActivity` for a reusable subprocess, and `transaction` when its semantics are specified).
- **Decisions / branching** — "if", "or", "depending on", "in parallel", "wait for first of" → `bpmnGateway` with the matching `gatewayType`.
- **End states** — terminal outcomes → `bpmnEvent` with `eventGroup: "end"` and an `eventType` reflecting how the process ends (message, error, terminate, etc.).
- **Data** — documents, records, inputs/outputs → `bpmnDataObject`. Persistent storage → `bpmnDataStore`.
- **Communication** — identify the participant boundary first. A handoff between lanes in one pool uses sequence flow; a message between separate pools uses message flow. The verb alone does not determine the connector.

Preserve each distinct action the user states in the flow. For example, "charge the card and record the result" calls for a charge task followed by a record task; a data-store association shows where the result is kept but does not perform the recording action.

**Recognition patterns:**

| User phrase                                                    | BPMN element                                                        |
| -------------------------------------------------------------- | ------------------------------------------------------------------- |
| "starts when ...", "triggered by ...", "every Monday"          | `bpmnEvent` start (eventType: `none`, `message`, `timer`, `signal`) |
| "receive", "wait for X message"                                | `bpmnEvent` intermediate, eventType: `message`                      |
| "after 24 hours", "wait 5 minutes"                             | `bpmnEvent` intermediate, eventType: `timer`                        |
| "if ... else ...", "decide whether"                            | `bpmnGateway`, gatewayType: `exclusive`                             |
| "in parallel", "and also", "fork into"                         | `bpmnGateway`, gatewayType: `parallel`                              |
| "whichever comes first", "wait for either"                     | `bpmnGateway`, gatewayType: `eventBased` or `exclusiveEventBased`   |
| "any combination of", "one or more of"                         | `bpmnGateway`, gatewayType: `inclusive`                             |
| "ends with", "process completes when", "rejection notice sent" | `bpmnEvent` end                                                     |
| "fails with error", "throws exception"                         | `bpmnEvent` end, eventType: `error`                                 |
| "abort", "kill the process"                                    | `bpmnEvent` end, eventType: `terminate`                             |
| "the form", "the application", "purchase order"                | `bpmnDataObject`                                                    |
| "the CRM", "stored in the database", "customer record"         | `bpmnDataStore`                                                     |
| "annotation", "note that", "FYI"                               | `bpmnTextAnnotation`                                                |

State your assumptions briefly before creating the diagram. Then proceed.

---

## Step 2: Read the diagram specification

Before writing JSON, read `lucid://skills/diagram-specification` through the Lucid MCP's `get_mcp_resource` tool. Follow its BPMN shape, lane, and connector rules. For `assistedLayout` on lane containers, follow the manual-layout exception in this skill instead of the specification's general recommendation.

---

## Step 3: Design the Standard Import JSON

The examples below illustrate BPMN modeling and provide parameter context. If their syntax, parameter names, or allowed values differ from the current tool descriptions/metadata or the live diagram specification, prefer those current sources. The manual-layout exception for `assistedLayout` described above still applies.

Build a single-page document by default:

```json
{
  "version": 1,
  "pages": [
    { "id": "page1", "title": "BPMN — [Process Name]", "shapes": [...], "lines": [...] }
  ]
}
```

If the process has clearly distinct phases the user wants visualized separately, use multiple pages. Otherwise, one page is correct.

### Shape size defaults

| Element                                                     | Width × Height                              |
| ----------------------------------------------------------- | ------------------------------------------- |
| `bpmnEvent` (any group/type)                                | 60 × 60                                     |
| `bpmnGateway` (any type)                                    | 60 × 60                                     |
| `bpmnActivity` task                                         | 140 × 90                                    |
| `bpmnActivity` eventSubProcess / callActivity / transaction | 180 × 110                                   |
| `bpmnDataObject`                                            | 70 × 90                                     |
| `bpmnDataStore`                                             | 90 × 70                                     |
| `bpmnTextAnnotation`                                        | 180 × 60                                    |
| `bpmnGroup`                                                 | sized to enclose its members + 30px padding |

### Pool & lane structure

**Use `bpmnPool` by default.** It keeps the participant container in the BPMN shape library. The generic `swimLanes` container is an exception only when the user specifically needs colored lane headers: `bpmnPool` ignores `headerFill`, while `swimLanes` supports it. If that exception is needed, explain in the delivery response that its lane container is not a BPMN pool and may not preserve participant semantics in a BPMN XML workflow.

Default to horizontal (`vertical: false`) — lanes stacked as rows, flow proceeding left to right. Use vertical only if the user explicitly asks.

```json
{
    "id": "pool-main",
    "type": "bpmnPool",
    "boundingBox": {"x": 50, "y": 50, "w": 1600, "h": 600},
    "title": "Retailer",
    "vertical": false,
    "lanes": [
        {"title": "Sales", "width": 200, "laneFill": "#F1F6FB"},
        {"title": "Billing", "width": 200, "laneFill": "#F5F2FA"},
        {"title": "Warehouse", "width": 200, "laneFill": "#F1F8F3"}
    ],
    "assistedLayout": false
}
```

For an explicit branded-header request, change the container to `swimLanes`, replace `title` with `"titleBar": {"height": 50, "verticalText": true}`, and add `headerFill` to each lane. Confirm the exact fields against the live specification. `titleBar` configures the bar but has no participant-name field; do not claim that `swimLanes` preserves the pool title.

```json
{
    "id": "lanes-main",
    "type": "swimLanes",
    "boundingBox": {"x": 50, "y": 50, "w": 1600, "h": 600},
    "vertical": false,
    "titleBar": {"height": 50, "verticalText": true},
    "lanes": [
        {"title": "Sales", "width": 200, "headerFill": "#CC785C", "laneFill": "#F1F6FB"},
        {"title": "Billing", "width": 200, "headerFill": "#CC785C", "laneFill": "#F5F2FA"},
        {"title": "Warehouse", "width": 200, "headerFill": "#CC785C", "laneFill": "#F1F8F3"}
    ],
    "assistedLayout": false
}
```

**Critical lane-container rules:**

- `vertical: false` → lanes are stacked rows. Each `lane.width` is the row's HEIGHT (despite the name). Sum of lane widths must equal `boundingBox.h`.
- `vertical: true` → lanes are columns. Each `lane.width` is the column's horizontal width. Sum must equal `boundingBox.w`.
- Set `assistedLayout: false` on the `bpmnPool` or `swimLanes` container. This skill intentionally overrides the specification's general recommendation of `true` for lane containers: preserving the chosen coordinates keeps lane containment, shape proportions, connector routing, and label clearance predictable during validation and PNG inspection.
- The participant name goes in `bpmnPool.title`. `swimLanes` has no equivalent participant-name field in the current import specification.
- Lane `title` and `laneFill` are required on both container types; `swimLanes` also requires `headerFill`.
- Apply the requested or company-standard palette when available. Otherwise, use distinct, light `laneFill` colors for adjacent lanes and coordinating colors across pools, while keeping text and connectors readable. `laneFill` works on `bpmnPool`; colored lane headers require the `swimLanes` exception.
- `headerFill` is honored by `swimLanes` and ignored by `bpmnPool`; do not add it to a `bpmnPool` as a styling workaround.
- Lane objects accept only `title`, `width`, `headerFill`, and `laneFill` — nothing else.

**Header text placement:** Set lane names through each lane's `title`, and the BPMN participant name through `bpmnPool.title`. Do not layer free-floating text shapes over header strips.

**Tradeoff to state out loud when using `swimLanes`:** It is a Container Library shape rather than a BPMN pool, and the current import format does not provide a pool-title field for it. Do not promise that its lanes will survive a BPMN XML export as participants.

**Lane containment:** Every shape inside the pool must fit entirely within its target lane's interior. A `bpmnPool` has a fixed 80px header along its leading edge: exclude it from the left for `vertical: false`, or from the top for `vertical: true`. For `swimLanes`, exclude the configured `titleBar.height` instead. Leave at least 30px of padding from any lane edge. Compute each shape's bounding box against the lane's usable rectangle, not the pool's full rectangle.

**External participants:** Model each external party that exchanges only messages (e.g., "Customer email service", "Bank") as its own separate `bpmnBlackBoxPool` placed above or below the main pool. Black box pools have no internal flow — only message flows connect to them.

```json
{
    "id": "pool-bank",
    "type": "bpmnBlackBoxPool",
    "boundingBox": {"x": 50, "y": 700, "w": 1600, "h": 60},
    "text": "Payment Processor"
}
```

### Events

```json
{
    "id": "ev-start",
    "type": "bpmnEvent",
    "eventGroup": "start",
    "eventType": "message",
    "boundingBox": {"x": 170, "y": 150, "w": 60, "h": 60},
    "text": "Order received"
}
```

Pick the `eventType` based on what triggers / signals the event:

- `none` — generic start/end; default if no specific trigger described
- `message` — sending or receiving a message
- `timer` — time-based trigger or delay
- `signal` — broadcast signal (one-to-many)
- `error` — error thrown / caught (end events usually)
- `escalation`, `compensation`, `cancel`, `conditional`, `link`, `multiple`, `parallelMultiple`, `terminate` — use when the user describes the matching semantics

### Activities

```json
{
    "id": "act-validate",
    "type": "bpmnActivity",
    "activityType": "task",
    "boundingBox": {"x": 240, "y": 140, "w": 140, "h": 90},
    "text": "Validate order"
}
```

`activityType` values:

- `task` — atomic unit of work (default)
- `transaction` — ACID-bracketed group of activities (double border)
- `eventSubProcess` — event-triggered sub-process
- `callActivity` — reusable / global process invoked here (bold border)

Activity labels: imperative verb phrase, short (e.g., "Validate order", "Charge credit card", "Send confirmation email"). Avoid passive voice.

### Gateways

```json
{
    "id": "gw-payment-ok",
    "type": "bpmnGateway",
    "gatewayType": "exclusive",
    "boundingBox": {"x": 500, "y": 155, "w": 60, "h": 60},
    "text": "Payment\napproved?"
}
```

`gatewayType` selection:

- `exclusive` (XOR, default) — one path taken based on conditions
- `parallel` (AND) — all outgoing paths taken
- `inclusive` (OR) — one or more outgoing paths taken based on conditions
- `eventBased` — next path chosen by which event occurs first
- `exclusiveEventBased` — variant used to start a process based on first event
- `parallelEventBased` — variant that starts a process and waits for all events
- `complex` — none of the above fit
- `none` — visually a diamond with no inner marker (rarely correct)

For a split gateway with conditions, set the gateway's `text` to a question. Label each outgoing sequence flow with the condition (`"Yes"`, `"No"`, `"amount > $1000"`, etc.).

### Data objects & data stores

```json
{"id": "data-order", "type": "bpmnDataObject", "dataType": "input",
 "boundingBox": {"x": 280, "y": 280, "w": 70, "h": 90}, "text": "Order"}

{"id": "store-crm", "type": "bpmnDataStore",
 "boundingBox": {"x": 800, "y": 280, "w": 90, "h": 70}, "text": "CRM"}
```

`dataType` for data objects: `none` (default), `collection`, `input`, `output`.

Data objects connect to activities via **associations** (dotted lines, no arrow or open arrow), never sequence flows.

### Text annotations & groups

```json
{"id": "note-1", "type": "bpmnTextAnnotation",
 "boundingBox": {"x": 600, "y": 80, "w": 180, "h": 60},
 "text": "Manual review required for orders over $10k"}

{"id": "group-1", "type": "bpmnGroup",
 "boundingBox": {"x": 230, "y": 130, "w": 360, "h": 200},
 "text": "Pre-fulfillment checks"}
```

Annotations connect to whatever they annotate via an **association** (dotted, no arrowhead). Groups are visual-only — they do not impose flow semantics.

Always use `bpmnTextAnnotation` — the BPMN 2.0 Library's dedicated shape — for any free-floating note or comment. Never use a Standard Library `text`, `stickyNote`, or Flowchart Library `note` shape, even when one would visually resemble an annotation.

---

## Connectors (lines) — BPMN flow semantics

Lines are not "shapes" in Lucid, but they carry BPMN semantics and must follow these three patterns exactly:

### Sequence flow (within a single pool)

Solid line, filled arrow at target. Use for normal flow.

```json
{
    "id": "sf-1",
    "lineType": "elbow",
    "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": "ev-start"},
    "endpoint2": {"type": "shapeEndpoint", "style": "arrow", "shapeId": "act-validate"},
    "stroke": {"color": "#000000", "width": 1, "style": "solid"}
}
```

**Conditional sequence flow** (when the outgoing condition isn't the default):

- Keep `endpoint2.style: "arrow"` and add the condition as line text.
- From a gateway, set `endpoint1.style: "none"`. Never use the mini-diamond `bpmnConditional` marker on an outgoing gateway flow.
- Reserve `endpoint1.style: "bpmnConditional"` for conditional flows leaving activities (`bpmnActivity`).

**Default sequence flow** (the "otherwise" branch of a gateway):

- Keep `endpoint2.style: "arrow"`.
- Set `endpoint1.style: "bpmnDefault"`.

### Message flow (between pools or between a pool and a black-box pool)

Dashed line, open circle at source, open arrow at target.

```json
{
    "id": "mf-1",
    "lineType": "elbow",
    "endpoint1": {"type": "shapeEndpoint", "style": "openCircle", "shapeId": "act-charge"},
    "endpoint2": {"type": "shapeEndpoint", "style": "openArrow", "shapeId": "pool-bank"},
    "stroke": {"color": "#000000", "width": 1, "style": "dashed"},
    "text": [{"text": "Payment request", "position": 0.5, "side": "middle"}]
}
```

Message flows must cross a pool boundary. Never use a message flow within one pool, and never use a sequence flow between pools.

### Association (to/from data objects, annotations, groups)

Dotted line, no arrowhead (or open arrow only for directed data associations).

```json
{
    "id": "as-1",
    "lineType": "straight",
    "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": "act-validate"},
    "endpoint2": {"type": "shapeEndpoint", "style": "none", "shapeId": "data-order"},
    "stroke": {"color": "#707070", "width": 1, "style": "dotted"}
}
```

### Line labels

Label the outgoing sequence flows of a conditional gateway split with their conditions. Do not invent conditions for a parallel split or a converging gateway. Label other sequence flows only when the transition needs clarification. Give each message flow a short, nonempty label naming the message, and leave room for that label away from shapes and pool borders.

```json
"text": [{"text": "Yes", "position": 0.5, "side": "middle"}]
```

### Line routing

- Use `"lineType": "elbow"` for sequence and message flows — BPMN convention is rectilinear routing.
- Use `"lineType": "straight"` only for short associations to data objects/annotations.
- Check the space around message-flow labels and pool boundaries before relying on automatic elbow routing. Pin endpoints when precision is needed to keep a connector or its label clear of a shape.

---

## Layout rules

BPMN reads left to right (or top to bottom in a vertical pool). Time flows from the start event toward the end event. Check the rendered result before delivery.

**Within a lane:**

- Place the start event to the right of the lane header, with enough padding that neither the event nor its label touches the header text. Check the actual header width in the rendered PNG.
- Each successive activity / gateway sits to the right of the previous, with **at least 200px center-to-center** (60–140px element + 60–80px gap).
- Vertically center elements within their lane's usable region.

**Across lanes:**

- A handoff between lanes is shown by a sequence flow that crosses from one lane's element to another's. The receiving element's x should be slightly to the right of (or equal to) the sending element's x — never to the left, unless modeling a rework loop.

**Branches from a gateway:**

- For a 2-way exclusive split, place one branch's activities at the gateway's y position, the other branch stacked above or below with 100px vertical separation. Re-merge at a converging gateway downstream.
- For parallel splits, stack branches vertically so they're visually equivalent.

**Pool sizing:**

- Pool height = `Σ lane.width` (since `vertical: false` makes lane widths into row heights). Each lane should be at least 140px tall to fit an activity plus padding.
- Pool width = enough to fit the longest end-to-end flow. Start with 1600px; widen as needed.

---

## Step 4: Create the document

Before creating it, check that each shape is in the allow-list, each line endpoint refers to a shape on the page, every message flow has a label, and every shape inside a pool fits in its intended lane. Call `lucid_validate_diagram_specification` with the final JSON before `lucid_create_diagram_from_specification`; the create tool's own preflight is not a substitute. Fix structural and layout findings, then rerun validation. Read `skipped_checks`; a clean report does not prove elbow routing is clear.

Call `lucid_create_diagram_from_specification` with:

- `title`: `"BPMN — [Process Name]"`
- `product`: `"lucidchart"`
- `use_assisted_layout`: `false` (preserve the chosen pool and shape positions)
- `standard_import_json`: your JSON string

**Containment rule reminder:** Every shape inside the pool must have its entire bounding box within its target lane's usable rectangle (excluding the pool title bar and lane header). Shapes that clip the lane edge will not be auto-corrected.

---

## Step 5: Verify the result

- Check the flow graph: every split has the intended outgoing branches and an explicit gateway; merging gateways are allowed to have one outgoing sequence flow. Sequence flows stay inside one pool, including across its lanes. Message flows cross between distinct pools. Data objects, stores, annotations, and groups do not carry sequence flow.
- Export each page with `lucid_export_document_as_PNG` and inspect the rendered image for the requested lane colors, clipped or overlapping shapes, unreadable labels, and connectors crossing unrelated shapes. Treat a label touching a pool or lane border, another connector, or other text as an overlap. If `lucid_validate_diagram_specification` warned that text may shrink inside a shape, confirm it remains readable in the PNG; also inspect the elbow connector paths that tool could not check. If PNG export times out, retry after a short pause; do not treat the preflight report as visual verification. Correct defects in the created document with `lucid_run_script`: check the Script API catalog, load the relevant documentation, and fetch item IDs as needed. Keep required message-flow and conditional-branch labels when correcting their placement. Do not create a replacement document. After each script edit, export the document and check it again; keep correcting visible overlaps, especially labels touching pool, lane, or shape borders or other text, before delivering the link.
- Check that the rendered diagram matches the user's process, including start triggers, branch labels, end states, and participant boundaries. Do not infer a missing step solely to make the picture look complete.

---

## Step 6: Deliver results

Provide:

1. **Brief summary**: pools/lanes, the high-level flow (start → key gateways → end), and any external participants modeled as black-box pools.
2. **Assumptions called out**: anything you inferred (event types, gateway types, missing participants).
3. **Edit URL**: from the creation response.
4. **Known tradeoffs or unresolved details**: mention the `swimLanes` exception if used, and any process detail the input did not establish.

If the user asks for JSON, use the Lucid `fetch` tool with the document ID to retrieve its structured content. For a large document, fetch metadata first and then the needed pages or regions. Present the fetched content as formatted JSON; do not label the original Standard Import JSON as an export of the created document. Otherwise, offer to provide JSON if useful.

---

## Common BPMN modeling pitfalls to avoid

- **Implicit gateways**: Two outgoing sequence flows from a task implies an uncontrolled split. Always insert an explicit gateway when flow branches.
- **Crossing pool boundaries with sequence flow**: Sequence flows must stay within one pool. Any inter-pool communication is a message flow.
- **Data object as a flow element**: Data objects connect via associations, never sequence flow. They are not "in" the flow.
- **End events without an event group**: Every event must have `eventGroup` set. Omitting it loses the intended start, intermediate, or end semantics.
- **Trading away BPMN semantics for styling**: `bpmnPool` ignores `headerFill`, but remains the default. Use `swimLanes` only when branded lane headers are explicitly needed, and explain its participant-title and BPMN identity limitations.
- **Treating a lane handoff as a message**: Lanes in one pool are one participant. Continue sequence flow across the lane boundary; reserve message flow for distinct pools.
- **Text annotation via a non-BPMN shape**: Free-floating notes must use `bpmnTextAnnotation`, never `text`, `stickyNote`, or `note`.
- **Decorative shapes (rectangles, circles, diamonds) used to "look like" BPMN**: Forbidden. Use the real BPMN type so semantics survive a re-import or analysis.
- **Emoji in text**: Lucid renders emoji as black boxes — never include them in labels.

---

## Notes

- Activity labels: imperative verb + object ("Approve invoice"). Avoid gerunds ("Approving invoice") and passive constructions.
- Event labels: noun phrase describing the state ("Order received", "Payment confirmed").
- Gateway labels: a yes/no question ("Stock available?") or a decision noun ("Routing").
- Pool/lane titles: the participant or role name, not the action.
- Keep the diagram on one page unless the user asks for separate pages per phase.

## Example

Input: "Create a BPMN for a retailer: Sales receives an order, Billing checks payment, and Warehouse ships it if approved. Otherwise Sales rejects it."

Output: one `bpmnPool` titled "Retailer" with Sales, Billing, and Warehouse lanes; a start event, tasks for the stated actions, an exclusive gateway for payment approval, and separate shipped and rejected end events. The lane handoffs use sequence flow because all three roles are inside the same participant. The two gateway branches have "Approved" and "Declined" labels; no message flow is added because the input names no other participant.
