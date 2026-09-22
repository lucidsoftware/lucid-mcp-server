# Lucid MCP Test Cases
> **Note**: These test cases are associated with the Lucid account provided to Anthropic for testing. The document IDs, folder IDs, and fixture document titles referenced below only resolve when running against that account.

# Positive Test Cases

### Fetch page regions with known target

**Prompt:**

> "Fetch document `1533cc31-6314-4ff4-bea3-cca738f7a3b1`. Tell me what conditions lead to a sale approved versus a sale not being approved." 

**Expected tool path:** `fetch`.

**Pass criteria:** The answer summarizes the fetched region and describes the decisions that lead to an approved sale, and that bad credit leads to a sale not being approved.

### Add new shapes and lines to an existing diagram

**Prompt:**

> "In Lucid document `119c28c1-7c0e-4066-b9e6-b97ec0af9ec9`, on the first page, update the onboarding process map by adding a step called `Security Review` between `Account Provisioning` and `Account Activation`. Connect it so the flow still reads in order."

**Expected tool path:** `fetch` -> `lucid_add_block` -> `lucid_add_line`.

**Pass criteria:** The document is fetched and changes are made. The assistant reports that it inspected the document, added the new step, and connected it into the flow.

### Create a diagram

**Prompt:**

> "Create a Lucidchart flowchart titled `LC Test - Incident Response Flowchart` from this incident response process: Start when an alert fires or a customer reports a critical issue. The on-call engineer triages impact and checks whether customer-facing checkout, login, or billing is affected. If customer impact is confirmed, declare an incident and classify severity. For P1 incidents, notify the incident commander, engineering lead, support lead, and communications owner. For P2 incidents, notify the service owner and support lead. Open an investigation branch for mitigation work, customer communication, and status-page updates. If mitigation succeeds, verify service health and monitor for 30 minutes. If mitigation fails, escalate to the platform lead and prepare rollback steps. Close the incident only after owner sign-off, customer communication, and retrospective assignment."

**Expected tool path:** `get_mcp_resource` for `lucid://diagram-specification` -> `lucid_create_diagram_from_specification`.

**Pass criteria:** The assistant creates a new Lucidchart document and reports the created document details. The diagram contains the required process steps and decision branches.

### Search for documents containing specific text

**Prompt:**

> "Search for all documents containing this text: `flow`"

**Expected tool path:** `search`.

**Pass criteria:** The assistant lists matching boards: `AWS web app structural flow`, `Business process flow example`, `LC Test - Incident Response Flowchart`, `New Hire Onboarding Process`, `BPMN, process flow`.

### Export a document as a .png

**Prompt:**

> "Export `AWS web app structural flow` (`5da33660-89d9-4bdc-a8b9-0c1165e01b15`) as a .png"

**Expected tool path:** Export .png.

**Pass criteria:** The assistant exports the document as a .png file.