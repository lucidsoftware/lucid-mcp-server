# Lucid MCP Test Cases
> **Note**: These test cases are associated with the Lucid account provided to Anthropic for testing. The document IDs, folder IDs, and fixture document titles referenced below only resolve when running against that account.

**Evaluation:** Each case must satisfy both its tool requirements and its pass criteria. Repeated calls, extra relevant calls, and either accepted alternative are allowed. Order matters only where stated or required by tool prerequisites; optional calls are not required. Reading `lucid://skills/readme` with `get_mcp_resource` is the server's mandatory first step, so it is expected before the first tool call of every case and is not listed in each case below.

### Fetch page regions with known target

**Prompt:**

> "Fetch document `1533cc31-6314-4ff4-bea3-cca738f7a3b1`. Tell me what conditions lead to a sale approved versus a sale not being approved." 

**Expected tool path:** `fetch`. Fetch the document content before summarizing; metadata alone is insufficient. `lucid_search_document` is optional.

**Pass criteria:** The answer summarizes the fetched region and describes the decisions that lead to an approved sale, and that bad credit leads to a sale not being approved.

### Add new shapes and lines to an existing diagram

**Prompt:**

> "In Lucid document `119c28c1-7c0e-4066-b9e6-b97ec0af9ec9`, on the first page, update the onboarding process map by adding a step called `Security Review` between `Account Provisioning` and `Account Activation`. Connect it so the flow still reads in order."

**Fixture:** `Security Review` is absent and `Account Provisioning` connects directly to `Account Activation`. Otherwise, mark inconclusive and rerun against a pristine fixture.

**Expected tool path:** `fetch` before editing, then `lucid_load_script_documentation` -> `lucid_run_script`. Edits are made with `lucid_run_script` using the canvas editing API (`createBlock`, `createLine`) documented by `lucid_load_script_documentation`. `lucid_get_script_catalog` beforehand is optional. Create the step before referencing its ID in connectors. Moving neighboring blocks to make room and deleting the old direct connector are allowed. Read-only scripts do not count as edits.

**Pass criteria:** The document is fetched and changes are made. The new step sits between `Account Provisioning` and `Account Activation` with connectors in order and no bypass, verified with `fetch` or a read-only `lucid_run_script`. The assistant reports that it inspected the document, added the new step, and connected it into the flow.

### Create a diagram

**Prompt:**

> "Create a Lucidchart flowchart titled `LC Test - Incident Response Flowchart` from this incident response process: Start when an alert fires or a customer reports a critical issue. The on-call engineer triages impact and checks whether customer-facing checkout, login, or billing is affected. If customer impact is confirmed, declare an incident and classify severity. For P1 incidents, notify the incident commander, engineering lead, support lead, and communications owner. For P2 incidents, notify the service owner and support lead. Open an investigation branch with mitigation work, customer communication, and status-page updates as three parallel steps that rejoin before the mitigation decision. If mitigation succeeds, verify service health and monitor for 30 minutes. If mitigation fails, escalate to the platform lead and prepare rollback steps, then return to the mitigation decision. Close the incident only after owner sign-off, customer communication, and retrospective assignment."

**Expected tool path:** `get_mcp_resource` for `lucid://skills/diagram-specification` -> `lucid_create_diagram_from_specification`. Read the specification before constructing it. `lucid_validate_diagram_specification` before creation, and `fetch` or `lucid_export_document_as_PNG` afterward to inspect the result, are optional.

**Pass criteria:** The assistant creates a new Lucidchart document and reports its details (title, ID, link). The diagram covers the customer-impact check, P1/P2 severity paths, the three investigation activities, the mitigation success/failure paths, and the closure conditions. Wording and layout may vary, and extra steps are fine. Process steps should connect onward rather than dead-end.

### Search for documents containing specific text

**Prompt:**

> "Search for all documents containing this text: `diagram`"

**Expected tool path:** `search`. `lucid_search_document` is optional, for verifying content matches in a candidate document.

**Pass criteria:** The assistant lists matching boards: `AWS web app structural flow`, `BPMN process flow`, `MCP Test Sequence Diagram`, `Blank diagram`, `Bad Diagram`.

### Export a document as a .png

**Prompt:**

> "Export `AWS web app structural flow` (`5da33660-89d9-4bdc-a8b9-0c1165e01b15`) as a .png"

**Expected tool path:** `lucid_export_document_as_PNG`. `fetch` and `lucid_get_document_metadata` are optional.

**Pass criteria:** The assistant exports the document as a .png file and reports where the image was produced.
