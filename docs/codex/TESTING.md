# Lucid MCP Test Cases

> Fixtures resolve only in the Lucid account provided to OpenAI for testing.

**Evaluation:** Each case must satisfy both its tool requirements and pass criteria. Repeated calls (including consecutive calls), extra relevant calls, and either accepted alternative are allowed. Order matters only where stated or required by tool prerequisites; optional calls are not required.

## Positive Test Cases

### Fetch page regions with known target

**Prompt:**

> "Fetch document `ee234b4c-fbb6-47d5-a787-802bb5c2ec11`, the first page, and the region titled `Payment Flow - Authorization Timeout Risk` with container ID `risk-container`. Tell me what services and dependencies are shown in the checkout payment path."

**Tools:** `fetch` and `lucid_search_document`, in either order. Fetch region content before summarizing; metadata alone is insufficient.

**Pass:** Summarizes the fetched region's services and dependencies.

### Add new shapes and lines to an existing diagram

**Prompt:**

> "In Lucid document `c4808c3a-5432-49f7-a5ca-fb28cacb56ff`, on the first page, update the onboarding process map by adding a step called `Security Review` between `Account Provisioning` and `Account Activation`. Connect it so the flow still reads in order."

**Fixture:** `Security Review` is absent and `Account Provisioning` connects directly to `Account Activation`. Otherwise, mark inconclusive and rerun against a pristine fixture.

**Tools:** `fetch` before editing. For edits, use `lucid_edit_item`, `lucid_add_block`, and `lucid_add_line`; `lucid_run_script` with the documented canvas API; or a mix. Create/copy and label the new step, then edit/create its connectors. Create the step before referencing its returned ID. Read-only scripts do not count as edits.

**Pass:** Makes actual changes and verifies `Account Provisioning` → `Security Review` → `Account Activation`, without a bypass, using `fetch` or structured reads/inspection through `lucid_run_script`. Reports inspection, addition, and connection of the step.

### Create a diagram

**Prompt:**

> "Create a Lucidchart flowchart titled `LC Test - Incident Response Flowchart` from this incident response process: Start when an alert fires or a customer reports a critical issue. The on-call engineer triages impact and checks whether customer-facing checkout, login, or billing is affected. If customer impact is confirmed, declare an incident and classify severity. For P1 incidents, notify the incident commander, engineering lead, support lead, and communications owner. For P2 incidents, notify the service owner and support lead. Open an investigation branch for mitigation work, customer communication, and status-page updates. If mitigation succeeds, verify service health and monitor for 30 minutes. If mitigation fails, escalate to the platform lead and prepare rollback steps. Close the incident only after owner sign-off, customer communication, and retrospective assignment."

**Tools:** Read `lucid://skills/diagram-specification` with `get_mcp_resource` before constructing the specification. Validate the final specification with `lucid_validate_diagram_specification` before `lucid_create_diagram_from_specification`, then inspect the created document with `fetch`.

**Pass:** Creates a new Lucidchart document containing all requested steps and decision branches, and reports its details.

### Search for documents containing specific text

**Prompt:**

> "Search for all documents containing this text: `Q3 planning`"

**Tools:** `search` and `lucid_search_document`. Discover candidate IDs through `search` or other discovery calls before searching their content; verify content matches before reporting them.

**Pass:** Lists `LC Fixture - Q3 Planning Board - Product Launch`, `LC Fixture - Q3 Planning Board - Platform Reliability`, and `LC Fixture - Q3 Planning Board - Sales Enablement`.

### Export a document as a .png

**Prompt:**

> "Export `LC Fixture - Q3 Planning Board - Product Launch` (`84e02d29-ee6d-43b8-9a72-de2210188a52`) as a .png"

**Tools:** `lucid_export_document_as_PNG`; `fetch` is optional.

**Pass:** Exports the document as a PNG.

## Negative Test Cases

### Fails to fetch a non-existent page

**Prompt:**

> "Fetch page 2 of document `84e02d29-ee6d-43b8-9a72-de2210188a52`."

**Tools:** `fetch` page 2 to receive an out-of-range validation error; or metadata-only `fetch` to confirm the document has one page and skip the invalid request.

**Pass:** Reports page 2 is unavailable based on the returned error or page count. Does not substitute page 1 or fabricate content.

### Fails to delete non-existent items in a document

**Prompt:**

> "In document `84e02d29-ee6d-43b8-9a72-de2210188a52`, delete the shapes with IDs `fake-id-001` and `fake-id-002` with the `lucid_run_script` tool."

**Tools:** `fetch` before `lucid_run_script` with the documented canvas API for deletion; or `fetch` enough content to establish both IDs are absent and skip deletion. Metadata alone is insufficient.

**Pass:** Accurately reports that neither item was deleted, based on errors or structured inspection returned by `lucid_run_script`; or accurately reports verified absence and skipped deletion. Does not claim the items were deleted.

### Fails to create share link with an invalid role

**Prompt:**

> "Create a share link for document `84e02d29-ee6d-43b8-9a72-de2210188a52` with role `superadmin` by calling the `lucid_create_document_share_link` tool."

**Tools:** `lucid_create_document_share_link` with `superadmin`; or `fetch` / `lucid_get_document_metadata` for context plus tool documentation or validation evidence confirming the role is unsupported, then skip creation. Metadata alone does not establish supported roles.

**Pass:** Reports rejection or skipped creation with valid roles `view`, `comment`, `edit`, and `editandshare`, supported by the returned validation error or documentation. Does not substitute a valid role or claim a link was created.
