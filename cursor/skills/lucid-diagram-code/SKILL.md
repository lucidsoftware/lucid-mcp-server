---
name: lucid-diagram-code
description: 'Create or update editable Lucid diagrams for general code diagramming and comprehension, using code, repos, API definitions, or system descriptions. Use when asked to show or explain interactions, trace calls, map dependencies, or visualize execution flow in Lucid, even without the word “diagram”. Use for UML class diagrams, C4 context/container/component diagrams, sequence diagrams, call graphs, flowcharts based on code, and code explanations where a visual of structure, dependencies, or execution flow would help. Load this skill before creating or updating these Lucid diagrams, even after reading Lucid MCP resources such as `lucid://skills/readme`; those resources do not replace this workflow. For requests requiring enterprise architecture or cloud architecture modeling, prefer the relevant specialized skills. Excludes generating code from diagrams and business-process diagrams with no code involved.'
user-invocable: true
metadata:
    version: 1.0
    author: 'Lucid Software'
---

# Lucid Diagram Code

## Goal

Take code (a snippet, a package, or a whole repo) and produce an editable Lucid diagram that shows its structure at the right level of detail, or take an existing Lucid diagram and bring it in line with the code it describes. "Done" means the diagram exists, passes the checks in Step 6, and the user has been told what was inferred, what was left out, and why this scope and diagram type were chosen.

Pick the diagram type and level of detail from the scope of the code, and ask the user about scope when it is unclear or not specified (Step 2). Supported views include flowcharts, UML class diagrams, C4 diagrams (context, container, component), call graphs, and sequence diagrams.

Use this skill for general code diagramming and comprehension: explaining implementation structure, dependencies, and execution flow. A feature or pipeline named in prose counts: find it in the repo (Step 1) and diagram what you find. The Lucid MCP's readme and spec resources (Step 4) are steps inside this workflow, so settle scope and diagram type before calling any creation tool.

When the requested outcome requires enterprise architecture modeling (such as business capabilities, application portfolios, or relationships across business and technology domains) or cloud architecture modeling (such as provider-specific infrastructure, deployment topology, networking, or security boundaries), defer to the relevant specialized skill when available, even if the input is code. A general code or C4 view can still include cloud services; their presence alone does not require switching skills. For a mixed request, use this skill for the implementation view and the specialized skill for its architecture view.

An explanation request can also benefit from a diagram without explicitly asking for one. Use judgment based on the user's question: a diagram can clarify branching behavior in "explain how authentication works", execution order in "walk me through the checkout flow", or relationships in "how do these services communicate?" Create a diagram when it materially helps explain the code, and connect the accompanying explanation to what it shows. A simple question that is clear in prose does not need a diagram.

The two common agent misunderstanding failures this skill prevents are misinterpreting the input as the system the agent expects (a tidy three-tier app), and misjudging the scope needed to answer the question (60 classes on one page, or one class blown up into an architecture diagram). These are errors in the agent's understanding and depiction of the code, rather than flaws in the code or architecture itself.

## Hard constraints

- **Draw only what the input supports.** Every shape and connector must trace to something in the input (a class, import, route, call, or sentence). Invented elements make the diagram look authoritative while being wrong.
- **Mark inferences.** Anything not stated in the input (a multiplicity, a database behind a repository class, a protocol) goes in the assumptions list in Step 7, and the shape or connector on the diagram that depends on it gets a `?` suffix on its label. This covers the order of two steps, which value a call passes along, and which branch a path takes, not only an uncertain arrow. If it is in the assumptions list and drawn, it has a `?` on the diagram. Readers trust a diagram more than prose, so guesses must be visible.
- **Mark source conflicts too.** Conflicting sources remain uncertain even when you choose one reading. Draw one consistent reading, mark each affected relationship with `?`, and explain which source you followed. A separate note or delivery caveat does not replace the marker on the element. Put `?` beside the uncertain claim: `Publishes invoice.requested?` for disputed behavior, `[AMQP?]` for an inferred protocol. Scope and presentation choices do not require `?`.
- **Settle scope before building.** Never start drawing until you know which slice of the code the diagram covers (Step 2). Wrong scope wastes the whole build.
- **Read the Lucid specification before building JSON.** The Standard Import format is strict, and guessing field names or shape types gets the import rejected.
- **Use verified shapes.** For Standard Import JSON, use shape types from the current Lucid specification. For native C4 shapes, follow the scripting and shape-library discovery route in the C4 reference. Do not invent type names, shape IDs, or library IDs.
- **Verify before delivering.** Run the checks in Step 6. Unchecked layout fails silently.
- **No emoji in labels.** Lucid can render emoji as black boxes.
- **Never include secrets.** If the input contains credentials, API keys, tokens, or connection strings, leave their values out of diagram labels, notes, and the final response. Name the component or credential by role ("Postgres" or "the database password"). This also applies when warning about exposed credentials: explain where the secret was found without quoting its value.
- **Read-only on the code.** This skill reads code and diffs. It never edits source files, branches, or PRs.

## Inputs

| Input                                                              | Required? | Notes                                                                                                             |
| ------------------------------------------------------------------ | --------- | ----------------------------------------------------------------------------------------------------------------- |
| Code, API spec, repo path, or app description                      | Yes       | If a path is given, read the relevant files. Do not diagram a repo from its name alone.                           |
| Existing Lucid diagram (URL, ID, or description), for updates only | No        | Triggers update mode. See "Updating an existing diagram".                                                         |
| Scope (which part of the code)                                     | No        | If it is unclear, follow Step 2.                                                                                  |
| Diagram type                                                       | No        | Infer from Step 2. Ask only when the choice changes the output materially.                                        |
| Detail level                                                       | No        | Infer from the size rules in Step 5.                                                                              |
| Icon style (cloud provider or generic)                             | No        | Default generic. Use provider shapes only if the user asks or the input is clearly one provider's infrastructure. |
| Product (Lucidchart or Lucidspark)                                 | No        | Default `lucidchart`.                                                                                             |

Two modes share one workflow:

| Mode                   | Trigger                                                                                                | Difference                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Snapshot** (default) | Code, schema, repo, or description                                                                     | Diagrams the code as it is.                                                                                 |
| **Update**             | "update this diagram", "refresh the diagram", "the diagram is out of date", a Lucid link plus new code | Reads the existing diagram, finds where the code differs, and edits it. See "Updating an existing diagram". |

## Workflow

### Step 1: Survey the input

Read before you ask or draw. Skim enough to answer: how big is this, how is it divided, and what depends on what?

- For a repo or folder: read manifests and entry points first (`package.json`, `build.sbt`, `pom.xml`, `docker-compose.yml`, `main.*`, route files, `angular.json`), then list top-level packages or modules and follow imports.
- For a snippet or schema: read all of it.
- To update an existing diagram: skip this step and follow "Updating an existing diagram" instead.

Record: approximate counts (files, classes or functions, services), the **natural divisions** (packages, layers, services, bounded contexts), and the **standout relationships** (one class everything depends on, a clear inheritance tree, a request path through three services, a cycle between two packages). You need these for Step 2 and for suggestions to the user.

### Step 2: Settle scope and diagram type

Match what you surveyed against this table. The scope sets the default diagram, and the default can be overridden by what the user asked for.

| Scope of the code                                                                    | Default diagram                                                                             | Level of detail                                 |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| One function or method with branching                                                | Flowchart                                                                                   | Every decision and call                         |
| A feature, pipeline, or behavior named in prose, spanning several functions or files | Flowchart (see Step 5 reference), or UML/C4 if the user asked for structure                 | Steps, decisions, and hand-offs between modules |
| One file or a few related classes (up to about 8)                                    | UML class diagram                                                                           | Full: attributes, methods, all relationships    |
| One package or module (about 9 to 25 types)                                          | UML class diagram grouped by sub-package, or C4 Component diagram                           | Per the selected reference in Step 5            |
| Many functions calling each other in a module                                        | Call graph (functions as boxes, calls as arrows)                                            | Names only, grouped by file or module           |
| A request or workflow crossing modules or services                                   | Sequence diagram                                                                            | One scenario at a time                          |
| Several services or packages in a repo                                               | C4 Container diagram (level 2), plus one C4 Component page for the most important container | Container and technology per box                |
| Whole system, multiple repos, or a description with no code                          | C4 System Context (level 1) plus Container (level 2), on separate pages                     | Systems and people, then containers             |

C4 levels in one line each: **Context** shows your system, its users, and the other systems it talks to. **Container** shows the separately deployable or runnable pieces (a web app, an API, a database). **Component** shows the major building blocks inside one container. **Code** is the class level, which is a UML class diagram.

**Flowchart is always an option.** For any scope, a flowchart of the control flow (what happens, in what order) is a valid alternative to a structural view, and words like "flow", "walk through", or "how X works" mean the user wants one. Include it when you ask about scope. When you guess on a structural row, build the structural diagram and offer the flowchart as a follow-up, or add it as a second page when the feature has a clear start-to-finish path.

**When scope is unclear, ask.** Ask when plausible choices of scope or diagram type would materially change the answer and the request does not resolve that choice. A broad repo request with several substantial areas, or a view that would contain more than about 25 shapes, usually needs clarification. A small, fully described system can be sufficiently bounded even if it spans several packages or services: for example, five named containers with their technologies and relationships can support a container overview without another question. If the requested view and boundaries are clear, or the supplied detail supports a straightforward default at a legible size, proceed and briefly explain the choice. The words "repo", "codebase", or "system" alone do not determine whether clarification is needed.

Ask once, and ground the options in what you read in Step 1. Use `AskUserQuestion` or a similar user prompt tool for clarification if available (otherwise a short numbered list in chat). Offer 2 to 4 concrete options, put your recommendation first and label it, and name real things from the code:

> I read the `billing/` repo (4 packages, about 60 classes). The clearest divisions are `invoicing`, `payments`, `ledger`, and `notifications`. `payments` and `invoicing` both depend on `ledger`, and `PaymentGateway` has 3 implementations. Which would you like?
>
> 1. C4 Container + Component overview of all four packages (Recommended: it is the only view that fits all 60 classes legibly)
> 2. UML class diagram of `payments` only, showing the `PaymentGateway` hierarchy
> 3. Sequence diagram of one invoice being paid, across `invoicing`, `payments`, and `ledger`
> 4. Something else

Add a second question only if the diagram type is also unclear (for example, class diagram or C4 for a mid-sized package). When clarification is needed, ask and end the turn before creating a diagram. A missing question tool or a CLI invocation does not establish that the user is unavailable; ask in chat. Once the user answers, make that scope the deliverable rather than retaining a broader overview as the main result.

**When the user delegates or the task is explicitly unattended, choose and say so.** Proceed without clarification when the user says "you pick", says they cannot answer, or the task explicitly requires unattended completion (for example, a scheduled run). An unanswered question alone does not authorize choosing. Choose the best diagram for the job using the table above and these tiebreakers:

1. Prefer the smallest scope that still answers the likely question. If the request names a class, package, or service, scope to it.
2. Prefer the divisions the code already has (existing packages, services, or modules) over ones you invent.
3. If two options are close, build the one that fits on one legible page and offer the other as a follow-up. Add a second page for the runner-up only when it is cheap.
4. Tell the user what you chose and why, up front in the delivery (Step 7, item 1). Do this whenever you picked the scope or diagram type yourself, including when you did not ask because you could not.

### Step 3: Extract components and relationships

Build a working list before drawing anything:

1. **Components:** classes, interfaces, functions, modules, services, databases, queues, external systems, users. Record where each was found (file and line, or sentence).
2. **Relationships:** extends, implements, composes, depends on, calls, reads/writes, publishes/subscribes. Record direction and any label (method name, route, protocol, event).
3. **Groupings:** packages, layers, deployment boundaries.
4. **Unknowns:** anything referenced but not defined (an imported client with no visible server), or a component whose file or package is not stated. Use the plain name from the code plus the `?` suffix required by the Hard constraints, and put the caveat in the assumptions list (optionally also use a dashed outline). Do not write caveat text such as "(file not stated)" in the label.

Translate the working list using the reference for the selected diagram type (Step 5). Where a relationship is implied but not shown, include it only if the evidence is strong, and put it in the assumptions list.

State the scope, diagram type, and assumptions briefly, then proceed.

### Step 4: Read the Lucid specification

Follow the Lucid MCP's startup instructions (read `lucid://skills/readme`). Then read the spec for the route you chose:

| Route                                     | Read first                                      |
| ----------------------------------------- | ----------------------------------------------- |
| `lucid_create_diagram_from_specification` | `lucid://skills/diagram-specification`          |
| `lucid_create_sequence_diagram`           | `lucid://skills/sequence-diagram-specification` |

For cloud provider shapes, also read the shape library resource named in the spec.

For C4 diagrams, also discover available script APIs with `lucid_get_script_catalog` and load `shapelibrary` and `basecanvasediting`. Use native C4 shapes and their separate editable text areas as described in the [C4 reference](references/c4.md). The Standard Import registry does not currently list C4-specific types.

### Step 5: Build the diagram

Read only the reference for each diagram type you will create or update. For a document with multiple diagram types, load the reference for each relevant page.

| Selected diagram type               | Reference                                                              | Guidance                                                                                    |
| ----------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| UML class diagram                   | [UML](references/uml.md)                                               | Language mappings, shapes, relationships, member detail, class spacing, and notation checks |
| C4 Context, Container, or Component | [C4](references/c4.md)                                                 | Component mappings, shapes, labels, colors, layout, and notation checks                     |
| Flowchart or call graph             | [Flowcharts and call graphs](references/flowcharts-and-call-graphs.md) | Shape vocabulary, code-path tracing, lanes, and flow layout                                 |
| Sequence diagram                    | [Sequence](references/sequence.md)                                     | PlantUML route and scenario verification                                                    |

Use verified shapes through the route in the selected reference. That reference supplies diagram-specific formatting; shared layout and verification rules follow here.

#### Detail levels and page splitting

Explicit user requests for detail or shape count override the defaults, including member filtering and splitting above 25 shapes. Otherwise, split diagrams with more than about 25 shapes into an overview page and one detail page per area. UML member-detail thresholds are in the [UML reference](references/uml.md#detail-levels).

For the split, give each overview box `"actions": [{"type": "gotoPage", "pageId": "<detail page id>"}]`. The `pageId` must exactly match the `id` of a page in the same import.

#### Shared sizing and layout

- Keep at least 60px clearance between shapes and at least 80px of padding inside containers. Apply any larger spacing required by the selected reference.
- Place related shapes next to each other. Long connectors between distant shapes are the usual cause of lines crossing unrelated boxes.
- Assisted layout: use `use_assisted_layout: true` for diagrams without containers. When containers hold shapes, set `use_assisted_layout: false` and `assistedLayout: true` on each container, except containers that hold other containers, which get `assistedLayout: false`.

For sequence diagrams, use the PlantUML route in the [sequence reference](references/sequence.md). For C4 diagrams, use the native-shape scripting route in the [C4 reference](references/c4.md), including its document bootstrap for a new diagram. For other JSON-built diagrams, use the following creation route.

Create the diagram with `lucid_create_diagram_from_specification`: `title` as "<System or module> <diagram type>" ("Billing Containers (C4 L2)"), `product` as `lucidchart`, and `standard_import_json` as your JSON string, after the checks in Step 6.

### Step 6: Verify

Run these checks, fix any failure, and re-check. Do not deliver on a failed check.

**Layout pass (before validating JSON-built diagrams).** Check connector routing below and apply the sizing and spacing rules in the selected diagram reference. Fix layout issues in the JSON before calling the validator.

_Connectors_

- Use `lineType: "elbow"` for every connector in class diagrams, C4 diagrams, flowcharts, and call graphs. Use `straight` only when both endpoints share a row or column, so the line is straight anyway. Do not use `curved`.
- Pin both endpoints with `position` on the sides that face each other: parent above child is child top center `{"x": 0.5, "y": 0}` to parent bottom center `{"x": 0.5, "y": 1}`; side by side is `{"x": 1, "y": 0.5}` to `{"x": 0, "y": 0.5}`. An unpinned endpoint attaches wherever Lucid picks, which produces lines running corner to corner through other shapes.
- Never pin both ends of one connector to the same side of their shapes (for example both on bottom edges). That forces a U-shaped elbow. Use facing sides, or move the shapes so the sides face each other.
- When several lines meet one side of a shape, spread them (`x` of 0.25, 0.5, 0.75) so they do not stack into one thick line.
- If an elbow line would pass through a third shape, move shapes (put connected shapes in adjacent rows or columns) rather than accept the crossing.

**Before creating (JSON-built diagrams):**

1. Call `lucid_validate_diagram_specification` with the JSON. Fix every structural finding and every layout finding (overlaps, text too long for its box, lines crossing unrelated shapes, labels on shapes). Read `skipped_checks`: elbow connectors get no geometry check, so the layout pass above and the PNG check below are what catch elbow routing problems.
2. **Traceability:** every shape and connector maps to an entry in your Step 3 list. Remove anything that does not. Then cross-check the other way: every assumption you will list in Step 7 that a shape, connector, or step order on the diagram depends on has a `?` on that element's label. Add any missing `?` before creating.
3. **Completeness:** every component in scope appears, or is named in the delivery as left out.
4. **Diagram-specific checks:** run the notation, detail, and layout checks in the selected reference. For documents with multiple diagram types, check each page against its own reference.

**After creating (all types):**

For script-built C4 diagrams, apply the same traceability, completeness, and diagram-specific checks above to the planned content. Run `basecanvasediting.validateCanvas` after mutations, checking text overflow, default text, contrast, overlaps, connected endpoints, line paths, and label collisions. Repair unintended findings and revalidate. The JSON validator only checks the bootstrap document, not content added later by scripts.

5. Export with `lucid_export_document_as_PNG` and look at it. Check for unreadable or inconsistently sized text, overlapping shapes, diagonal or corner-to-corner lines, lines passing through unrelated boxes, and mislabeled shapes. Correct findings in the existing document using the script workflow below, then export again to verify the result.
6. **Direction:** for each connector, confirm the arrow matches the code (caller to callee, dependent to dependency).
7. **Final-state assumptions:** fetch the finished document after creation and after corrections. Check that every drawn inference and unresolved source conflict still has `?` beside the affected claim, and that the delivery explains those marks. Check the actual labels, not only the submitted JSON or a separate note.

**Correcting verification findings:**

Use `lucid_run_script` to move, resize, or update shapes and connectors in the existing document when verification reveals a problem. Look up the supported operations with `lucid_get_script_catalog` and `lucid_load_script_documentation`, then fetch the document to get current item IDs before editing. Apply targeted corrections such as separating overlapping shapes, enlarging a box for its text, correcting a label, or adjusting connector endpoints. Preserve unrelated content and styling. Fetch and export the document again after corrections, and repeat the relevant checks. If the required correction is unsupported, explain the limitation and ask before creating a replacement document, disclosing any edits already applied.

### Step 7: Deliver

Give the user:

1. **Scope and diagram choice.** Explain what the diagram covers and why this type, prominently in the delivery. If you picked the scope or type yourself because the user was unavailable or said "you pick", say that plainly and name the alternatives you passed over: "Since you're unavailable, I chose a package overview because about 140 classes would not fit legibly. Alternatives: a class diagram of `payments`, or a sequence diagram of checkout." Exact paragraph order is flexible; include the reason for choosing autonomously as well as the technical reason for the choice.
2. **Summary:** counts ("12 components, 15 relationships") and the main takeaway you noticed (a cycle, a god class, a single point of dependency).
3. **Assumptions:** every inference or unresolved source conflict, one line each, naming the shapes or connectors it affects. Every drawn claim that depends on it has a matching `?`; one assumption may affect several elements. Explain scope and presentation choices separately without adding uncertainty marks to established facts.
4. **Left out:** components skipped for scope or detail level, and which page or follow-up would cover them.
5. **Edit URL** from the creation response, plus the exported PNG. List any earlier documents you superseded by recreating.
6. **Rerun note:** the diagram is a snapshot. Ask the skill to update it when the code changes.

## Updating an existing diagram

Goal: bring an existing Lucid diagram in line with the code it describes, changing only what differs. **The default is to update the existing document.** If the user asks for a new page or a new document with the new version of the code (for example "make a new version", "add a page for the updated code", "keep the old one"), that is supported: see Step E.

**Step A: Identify the diagram.**

- If the user gave a Lucid URL or document ID, use it. If the diagram was created earlier in this conversation and it is the only one, use that without asking.
- Otherwise, call the Lucid MCP `search` tool with keywords from the user's description (the feature, service, or class names, plus words like "diagram"). Narrow with `product` or `last_modified_after` when you can. Search is fuzzy and silently omits documents the MCP cannot read, so treat it as discovery only. A miss does not prove the diagram does not exist.
- **Confirm before touching anything.** Show the user the best one to three matches (title, product, edit URL) and ask which is right, using `AskUserQuestion` or a similar user prompt tool for clarification if available (otherwise ask in chat). Do this even when there is only one hit. If nothing plausible comes back, say so and ask for a link.
- **Stop after asking.** When the target was discovered through search and has not been confirmed, end the turn before proceeding to edits or creating a replacement. A unique or exact-title match is still a candidate. Resume after the user confirms; preserve any target selection already authorized in the conversation. Delegation to choose a diagram type does not confirm which existing document to modify.
- If the MCP says access is disabled for a document, retry once, then tell the user.

**Step B: Read the diagram.** Call `fetch` with `metadata_only` first to get the page count and region counts, then fetch each page (use `region_index` for large pages). Use `lucid_search_document` to jump to a specific class or label. If the content is too large, ask the user whether to fetch it region by region. Then build the same working list as Step 3 from what the diagram says:

- Components: every shape, with its label, stereotype, and members.
- Relationships: every connector, with direction, arrowheads, and label.
- Groupings, and the diagram type and level of detail it uses. Load the matching Step 5 reference before comparing or editing its elements.
- Anything marked `?` or listed in a legend or notes. Those are earlier guesses worth re-checking.

Export with `lucid_export_document_as_PNG` and look at it if layout matters, for example when you will add shapes.

**Step C: Find the code to compare against.** Use whichever the user provided:

- **New or changed code supplied** (pasted code, file paths, a branch, a PR, "my current changes"): read it with read-only commands (`git diff <base>...HEAD`, `git show`, `gh pr diff <n>`, or the environment's PR tool). Read the full post-change version of each changed file, not only the hunks, because relationships live outside the changed lines. Then check the diagram's elements against it.
- **No code supplied:** search the provided repo or the current codebase for each component named in the diagram. Look it up by the exact label (for a class, function, or service), then read its file. If a component cannot be found, it may have been renamed or deleted: check the git history (`git log -S '<name>'`) before concluding.

Skip lockfiles, generated code, vendored code, formatting-only changes, and tests unless the diagram covers them. Also look one hop beyond the diagram for new neighbors of its components (a new subclass, a new caller), but only add ones that fit the diagram's scope and detail level.

**Step D: Compare.** Build a difference list, one line per item, each with its evidence (file and line, or diagram element):

| Kind of difference | Example                                                                         |
| ------------------ | ------------------------------------------------------------------------------- |
| Added              | A new class, service, step, or call that is in scope and not in the diagram.    |
| Removed            | A shape or connector whose code no longer exists.                               |
| Renamed or moved   | `OrderService` became `OrderManager`, or moved to another package or swim lane. |
| Changed            | A new, removed, or retyped member. A changed signature, route, or protocol.     |
| Relationship       | A different parent, a new dependency, a reversed call, a changed label.         |
| Unverifiable       | An element with no counterpart that you cannot confirm is stale (see below).    |

Elements that never came from code (a title, a legend, a free-text note, shapes drawn by a person for another purpose) are not differences. Leave them alone and report them. If there are no differences, say so and stop. Do not change the document.

**Step E: Apply the changes.** Show the user the difference list first when it has more than a handful of items or any removals, and proceed once they agree. Then:

- **Default: edit in place.** Unless the user asked for a new page or document, look at the Lucid MCP's script tools (`lucid_get_script_catalog`, `lucid_load_script_documentation`, `lucid_run_script`) and check that they support the required edits before making changes where possible. Use them to add, change, or delete shapes and connectors in the existing document, so the user's layout, colors, and extra annotations survive. Fetch again before each edit to get current item IDs.
- **If the user asks for a new page:** add a page to the existing document with the updated version and leave the original page untouched, if the script tools can add pages. Otherwise, explain the limitation and ask for confirmation before making a new document.
- **If the user asks for a new document:** build the whole updated diagram as a new document using Steps 4 to 6, matching the original's style and layout where you can, and leave the original untouched. Name both documents in the delivery.
- **If in-place editing turns out to be impossible** for what you need (for example, a change that needs a different diagram type or re-layout), stop and explain the limitation. Summarize any edits already applied to the original and propose how to handle that partially updated document. Obtain the user's confirmation before creating a replacement document or making further changes to the original. If a replacement is approved and created, name both documents in the delivery.
- Follow the same rules as a new diagram for anything you add: Step 6 layout and diagram-specific checks, `?` marks on inferences, and no secrets. Keep new elements consistent with the existing style (fonts, sizes, colors, stereotype wording) rather than the defaults in this skill.
- Mark what changed only when the user asks for review highlights: give new shapes a green fill (`#CDEFD0`) and changed ones an amber fill (`#FFE9A8`), and tell the user they can reset them. Otherwise keep the existing fills. Never leave removals as invisible deletions: list them in the delivery.
- Do not delete an element when you are only unsure. Keep it, add a `?`, and list it as unverifiable.

**Step F: Verify and deliver.** Fetch the document again and confirm each item on the difference list is reflected and nothing else moved. Export the PNG and check the Step 6 visual items. Then give the user:

1. **Which diagram you updated** (title and URL), and how you identified it.
2. **What you compared against** (the code or files you read, or the searched repo).
3. **The difference list**, grouped as added, removed, renamed, changed, and unverifiable, with what you did for each.
4. **Left unchanged**: elements with no code counterpart, and anything out of the diagram's scope that you noticed.
5. **Assumptions** and the matching `?` marks, as in Step 7.
6. **Edit URL** and exported PNG, and the original document if you made a copy.

## Common pitfalls

- **Wrong scope:** diagramming everything because the request said "this repo". Settle scope in Step 2, and split large scopes across linked pages.
- **Template diagram:** drawing a generic frontend/API/database stack because that is the common shape. Draw only what Step 3 found.
- **Phantom database:** adding a database because a class is called `Repository`. Add a data store only when there is a driver, connection, schema, or compose service.
- **Unlabeled arrows:** label connectors with the route (`POST /orders`), event, method, or C4 verb phrase.
- **Paraphrased names:** label classes and components with the name used in the code (`OrderService`). Do not add caveats such as "(file not stated)" to a label.
- **Diagonal connectors:** straight or unpinned lines cutting across the page. Use pinned elbow lines (Step 6 layout pass).
- **Everything on one page:** 40 shapes at tiny font. Use the detail-level and split rules.
- **Guessing which diagram to update:** picking the closest search hit without asking. Confirm with the user unless they gave a link or the diagram was made earlier in this conversation.
- **Redrawing instead of updating:** rebuilding a diagram the user has arranged and annotated. Change only what differs and leave the rest alone.
- **Skipping the PNG check:** the validator cannot judge elbow connectors, contrast, or mislabeling. Look at the export.

## Limitations

- Static reading only: runtime behavior (dynamic dispatch, reflection, dependency-injection wiring from config, feature flags) is not visible, so such links may be missing.
- Update mode can only compare what the diagram states. Hand-added notes, colors, or shapes with no counterpart in the code are left alone and reported, not judged.
- The diagram is a snapshot of the input and does not stay in sync with the code unless the skill is rerun.

Shape types in this skill and its references were checked against `lucid://skills/diagram-specification` on 2026-10-07. If the spec changes, the spec wins.
