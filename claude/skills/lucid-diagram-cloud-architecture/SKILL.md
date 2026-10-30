---
name: lucid-diagram-cloud-architecture
description: Converts infrastructure and deployment code (Terraform/OpenTofu, CloudFormation/CDK, Pulumi, Azure Bicep/ARM, Kubernetes/Helm) into editable Lucid cloud architecture diagrams, or refines an existing diagram from such code. Use when the user supplies or points to that code and wants its cloud resources, connections, or boundaries visualized. Do not use for cloud architecture described only in prose, without code.
---

# Cloud architecture from code

## Goal

Turn repository code into an editable Lucidchart cloud architecture diagram using the Lucid MCP. Done means the diagram reflects the inspected code, uses appropriate provider shapes, and has passed structural and visual checks, with assumptions and gaps disclosed.

## Why this skill exists

Infrastructure code mixes deployment dependencies, runtime connections, and configuration that may remain unresolved. Converting every reference into an arrow produces misleading architecture, while guessing cloud icons or skipping rendered inspection produces diagrams that are incorrect or hard to read.

## Hard constraints

- **Ground the diagram in code and distinguish assumptions from facts.** Reasonable assumptions are allowed when they help explain the architecture, but append `?` to each assumed resource, connection, or boundary label and explain its basis in the key, notes, or delivery summary; otherwise readers may mistake it for verified configuration.
- **Inspect code without deploying it, and exclude secrets from diagrams and tool payloads.** Diagram creation does not require changing infrastructure or exposing credentials.
- **Look up shape IDs and scripting methods in the Lucid MCP references.** Guessed names can fail or represent the wrong service.
- **Visually inspect the exported diagram and correct layout defects before calling it verified.** Structural validation alone misses clipped labels and overlapping shapes or lines; if inspection is unavailable, disclose that limitation.

## Inputs

| Input                                             | Required? | Default or handling                                                                                                                      |
| ------------------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Repository path, relevant files, or code snippets | Yes       | Use the supplied code or current repository when clearly intended; ask if no source is identifiable.                                     |
| Service/directory and environment                 | No        | Infer a coherent scope from the code and state it. Ask if choosing among environments would materially change the diagram.               |
| Detail level                                      | No        | Default to a service-level overview; aggregate repeated resources and disclose omissions.                                                |
| Existing Lucid document URL or ID                 | For edits | Fetch and update that document. For a new-diagram request, create a Lucidchart document. Resolve the target before editing if ambiguous. |
| Cloud provider or visual preferences              | No        | Infer providers from resource definitions and use their service icons. Honor explicit preferences.                                       |
| Existing plan or sanitized inventory              | No        | Use as supplemental evidence and record its environment and provenance.                                                                  |

Ask only when missing information materially affects the result and cannot be inferred from the available input.

## Workflow

### Step 1: Read the scoped code

**Input:** Source code and scope from the inputs above. **Output:** Relevant definitions, references, and unresolved configuration for one stated scope.

Start with the requested directory, service, and environment. Inspect relevant infrastructure entry points, deployment manifests, and application configuration, following local modules and references as needed. Keep environments distinct; do not combine development and production resources into one apparent deployment. If scope is unspecified, choose a coherent overview and state its scope.

Useful inputs include:

- Terraform/OpenTofu `.tf` and `.tf.json`, module sources, variables, locals, outputs, and provider aliases.
- CloudFormation/SAM templates, AWS CDK source or existing synthesized templates, Pulumi programs, and Azure Bicep/ARM templates.
- Kubernetes manifests, Helm values/templates, Kustomize overlays, container definitions, deployment pipelines, and application clients or configuration that establish cloud service usage.

Use static inspection first. Do not run deployment code, Terraform apply, or cloud mutations to discover architecture. Existing user-supplied plans or sanitized inventories can clarify resolved values; label their environment and provenance. Source configuration describes intended architecture, not proof that resources are deployed. Exclude credentials and sensitive configuration values from diagrams and tool payloads.

### Step 2: Map code to architecture elements

**Input:** Definitions and references from Step 1. **Output:** An evidence-backed inventory of diagram nodes, boundaries, connections, and unknowns.

Build a compact working inventory of resources, connections, boundaries, and material configuration, recording source paths and relevant symbols. For each item, plan its visible representation or record why it is omitted at the chosen detail level. Preserve useful resource addresses or logical IDs in notes so labels can remain readable. Application SDK calls can establish usage but do not prove ownership, region, or network placement. Show referenced external resources as external when their definitions are unavailable.

| Evidence in the input                                         | Diagram element                                                                         |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Defined cloud service/resource                                | Provider service icon with a readable label and source identifier in notes              |
| Account, subscription, project, region, or network membership | A supported boundary container with only evidenced members                              |
| Runtime call, event subscription, or service integration      | Directional connector labeled with the supported interaction                            |
| `depends_on` or provisioning-only reference                   | Optional, distinctly labeled deployment dependency; never automatically a traffic arrow |
| Security rule                                                 | Access-policy annotation when relevant; not proof of runtime traffic                    |
| Unavailable module or externally referenced resource          | Labeled component/group with unresolved internals or external ownership                 |
| Conditional or repeated resource with unknown values          | Logical resource group annotated with unknown or conditional multiplicity               |

#### Preserve configuration and containment

At the default service-level overview, show configuration that changes how the pictured architecture behaves: failure/retry thresholds, retention, replica counts, schedules, relevant ports, alarm conditions, and enabled/disabled status. Use concise visible labels or callouts; hidden notes are appropriate for source identifiers and supplementary detail, but do not substitute for these annotations. Translate compact values when helpful, such as cron into a human-readable schedule. Mark materially unresolved settings, such as an unspecified schedule timezone or storage class, without inventing a value. Avoid copying every provider property into the diagram.

Record parent–child membership separately from connections. Containment applies beyond networks: projects/resource groups, storage accounts/services, datasets/tables, and Kubernetes namespaces/workloads can all establish useful hierarchy. Use labeled frames around evidenced members when a service icon cannot contain children. Distinguish administrative, network, and resource hierarchy boundaries; a project or resource group is not a network. Keep provider-managed services outside subnets/VPCs unless the code establishes membership, and distinguish a private endpoint inside a network from the service it accesses.

Draw visible, labeled containers for evidenced administrative scopes and geographic placement, not just a region name in a heading or note. Examples include AWS accounts and regions, Azure subscriptions/resource groups and resource locations, and Google Cloud projects, regions, and zones. Preserve symbolic scope names when IDs are unresolved; label an implied provider account as “account unspecified” rather than inventing an ID. Place each resource according to its own scope, including provider aliases and resource-level location overrides. Global or multi-region resources must not inherit a single-region boundary merely from a provider default: for example, AWS IAM is account-wide, a GCP VPC is global, and a US multi-region dataset is not confined to us-central1. Where administrative membership and location do not form a simple hierarchy (such as an Azure resource group with resources in different locations), use nested location groups or explicit membership labels that preserve both meanings. Keep local build artifacts outside cloud containers. Reserve a clear title band in every frame so child frames, icons, and captions cannot cover its name.

Separate a configured integration from verification of its prerequisites. If a required permission or other prerequisite is not established in the inspected scope, visibly annotate the gap (for example, “dead-letter forwarding configured; required IAM not shown”). Do not claim it is absent from the actual deployment or invent a grant. Mark inferred behavior with `?` and explain it in the key, notes, or delivery summary; a confirmed absence from the inspected files can be stated directly.

#### Interpret Terraform without inventing resolved values

Read Terraform normally; no special Terraform parser or exhaustive resource-to-icon table is required. Pay attention to the distinctions that affect the diagram:

- Resolve provider identity, aliases, local module inputs/outputs, and references where the code supports it. Module names alone do not establish their internal architecture. Represent unavailable remote modules as labeled groups or components and disclose the missing detail.
- Use `count`, `for_each`, and conditionals to determine multiplicity only when their values are known. Otherwise show a logical resource group with unknown or conditional multiplicity rather than invented instances.
- A reference or `depends_on` establishes a provisioning dependency, not necessarily a runtime request or data flow. Derive traffic arrows from integrations, event subscriptions, routes, application calls, and equivalent evidence. If deployment dependencies are useful to the requested diagram, label them separately.
- Derive network containment from subnet, VPC/VNet, region, and account/project/subscription configuration. A security rule permits traffic; it does not prove actual traffic. Do not put provider-managed services inside a subnet merely because an application in that subnet uses them.

Record reasonable assumptions separately from confirmed definitions in the inventory. State the chosen scope, material assumptions, and unresolved details briefly before building; do not use assumptions to contradict known configuration.

### Step 3: Consult Lucid specifications and shape libraries

**Input:** Providers and element types from Step 2. **Output:** The current diagram schema and verified shape IDs or documented generic fallbacks.

Discover the connected Lucid MCP tools and follow its startup guidance, including `lucid://skills/readme` and the resources it references. Read `lucid://skills/diagram-specification` before constructing Standard Import JSON. Use the server's resource-reading capability; tool prefixes can vary by client. Treat scripting API names and calls in this skill as examples to verify: consult `lucid_get_script_catalog` for the target document, then load the relevant references with `lucid_load_script_documentation` before invoking methods through `lucid_run_script`. If a named API or method is absent, find an equivalent capability in the catalog and its documentation and use the actual documented name and arguments; do not guess a replacement.

Route by the represented cloud service, not by the language that declares it:

| Evidence in code                                                              | Static MCP resource starting point                                                                           | Document Script API library ID    |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------- |
| AWS resources, including Terraform `aws_*`                                    | `lucid://shape-libraries/aws-2024/common`                                                                    | `aws2024.js`                      |
| Azure resources, including Bicep/ARM, `azurerm_*`, or Azure through `azapi`   | `lucid://shape-libraries/azure-2024/common`; also check `general` for resource icons                         | `azure2024.js`                    |
| Google Cloud resources, including `google_*` / Google beta provider resources | `lucid://shape-libraries/gcp-2021/common`                                                                    | `gcp2021.js`                      |
| Kubernetes manifests, Helm, or Kubernetes resources through other IaC         | Use document-specific discovery; absence of a static Kubernetes resource is not absence of Kubernetes shapes | `kubernetes2019.js`               |
| Oracle Cloud Infrastructure                                                   | Discover through the document Script API                                                                     | `oraclecloudinfrastructure.js`    |
| Physical network or on-premises equipment                                     | Discover through the document Script API                                                                     | `network.js`                      |
| Other providers or custom services                                            | Browse/search the document's visible built-in and custom libraries                                           | Use the exact returned library ID |

These are known library starting points, not permanent version pins. Prefer a newer available library for the **same provider/service or architecture** when discovered, verifying its shape IDs, meanings, and native dimensions. A cloud provider's managed Kubernetes icon (AKS, EKS, or GKE) is not a replacement for a Kubernetes Pod, Service, or Ingress icon and must not imply hosting absent from the code.

Terraform is an input language, not the destination shape library. For example, `aws_lambda_function` calls for an AWS Lambda icon, `azurerm_storage_account` for Azure Storage, and `google_compute_instance` for Google Compute Engine. Look up the actual shape identifiers; never derive a Lucid `className` from a Terraform resource type.

#### Search both catalog surfaces before a generic fallback

The MCP exposes two complementary discovery paths. Static `lucid://shape-libraries/...` resources are useful cloud catalogs, but their resource list is **not the complete list of Lucid libraries**. The document-specific `shapelibrary` Script API also exposes built-in and custom libraries, including Kubernetes.

1. Read the relevant static catalogs through `get_mcp_resource`. Start with `common`, then the service's category and adjacent categories before declaring an icon unavailable. AWS instance icons often require `compute`, `database`, or `application-integration`; Azure queues and blobs are in `general`, not `storage`. For GCP, check the relevant `compute`, `storage`, `networking`, or other advertised category beyond `common`.
2. For Kubernetes, other libraries without static resources, or any proposed generic fallback, call `lucid_get_script_catalog` for the target document. Load available `shapelibrary` documentation with `lucid_load_script_documentation`, then use `lucid_run_script` to call `skills.shapelibrary.shapeLibrary(...)`. Browse the known library ID and search resource names within it; follow `nextPageToken` with the same query until the relevant results are exhausted. Search/browse visible libraries if a newer version or another library may apply.
3. If a new diagram has no document ID yet, create the requested document using a supported initial specification, then discover and add or replace shapes in **that same document**. Initial generic placeholders are provisional. Complete discovery and replacement before final verification; finding exact icons after creation is a reason to refine the diagram, not to retain avoidable generic shapes. Do not create an extra document solely for discovery.
4. Record exact returned `shape.id` and `shape.libraryId`. Load `basecanvasediting` documentation before creating library shapes through `skills.basecanvasediting.createBlock`, passing those values as `shapeId` and `libraryId`. Static Standard Import `className` fields and Script API `shapeId`/`libraryId` fields are different interfaces; do not interchange them.

For example, after loading the document's `shapelibrary` reference, these read-only queries discover Kubernetes shapes and Azure storage queues:

```js
const kubernetes = await skills.shapelibrary.shapeLibrary({
    libraryId: 'kubernetes2019.js',
    pageSize: 200,
});
const azureQueues = await skills.shapelibrary.shapeLibrary({
    libraryId: 'azure2024.js',
    searchTerm: 'queue',
    pageSize: 200,
});
return {kubernetes, azureQueues};
```

Run only the queries relevant to the source. If keyword search returns nothing, browse the exact library without a search term. A listed library with empty groups or zero shapes can indicate a discovery/loading limitation, not that the product lacks those shapes. Cross-check static catalogs where available and report the specific connected-server limitation if discovery remains empty. Do not switch environments or claim that Lucid has no such shape based on an empty response. Use a labeled generic fallback only after these relevant discovery paths cannot supply a usable match, and disclose it.

For multiple clouds, use each provider's library and distinguish provider boundaries. Avoid substituting a similar-looking icon for a different service.

Choose by **provider + service + resource type**, not by a short display label or the first search result. Catalog labels can be ambiguous: the AWS DynamoDB table entry is labeled `Table`, and the SNS topic entry is labeled `Topic`. Their full IDs identify the service. A matching short label alone does not establish that a shape is generic or that it is the correct service-specific shape.

For each resource in the inventory, record the selected catalog ID, its category, and its intrinsic dimensions. Prefer the exact service-specific instance shape; fall back to that service's general icon only when no matching instance shape is available in the relevant category. Use a generic shape only if neither is supported, and disclose the fallback. Do not use an ERD/table widget for a DynamoDB table or an unrelated messaging topic icon for SNS merely because its label matches.

| Resource in code | AWS 2024 instance shape ID                       | Category resource                                          | Current intrinsic size |
| ---------------- | ------------------------------------------------ | ---------------------------------------------------------- | ---------------------- |
| DynamoDB table   | `ResAmazonDynamoDBTableAWS2024`                  | `lucid://shape-libraries/aws-2024/database`                | 120 × 120              |
| SNS topic        | `ResAmazonSimpleNotificationServiceTopicAWS2024` | `lucid://shape-libraries/aws-2024/application-integration` | 120 × 104              |
| SQS queue        | `ResAmazonSimpleQueueServiceQueueAWS2024`        | `lucid://shape-libraries/aws-2024/application-integration` | 120 × 74               |
| Lambda function  | `ResAWSLambdaLambdaFunctionAWS2024`              | `lucid://shape-libraries/aws-2024/compute`                 | 120 × 120              |

These are lookup examples, not a replacement for reading the connected server's catalog. Use its current IDs and dimensions if they differ.

#### Azure and Kubernetes resource matches

Azure 2024 includes specific resource icons outside its Storage category:

| Resource                                      | Shape ID                   | Static category      | Current intrinsic size |
| --------------------------------------------- | -------------------------- | -------------------- | ---------------------- |
| Storage account                               | `StorageAccountsAzure2024` | `azure-2024/storage` | 120 × 97               |
| Storage queue, such as `queueServices/queues` | `StorageQueueAzure2024`    | `azure-2024/general` | 120 × 97               |
| Block blob                                    | `BlobBlockAzure2024`       | `azure-2024/general` | 120 × 97               |
| Page blob                                     | `BlobPageAzure2024`        | `azure-2024/general` | 120 × 97               |

Read those categories under `lucid://shape-libraries/`. A storage queue is not Azure Service Bus. A `queueServices/default` parent can be a labeled structural container; distinguish it from the individual queue. A `blobServices/default` definition does not establish a block blob, page blob, or storage container. Keep that service at the evidenced level rather than choosing a more specific icon unsupported by code. Preserve disabled/conditional status independently of icon selection.

Kubernetes has a dedicated library, `kubernetes2019.js`, with these resource shapes and labeled variants:

| Kubernetes kind | Shape ID      | Labeled variant      |
| --------------- | ------------- | -------------------- |
| Ingress         | `IngKub19`    | `IngLabeledKub19`    |
| Service         | `SvcKub19`    | `SvcLabeledKub19`    |
| Pod             | `PodKub19`    | `PodLabeledKub19`    |
| Deployment      | `DeployKub19` | `DeployLabeledKub19` |
| NetworkPolicy   | `NetpolKub19` | `NetpolLabeledKub19` |
| Namespace       | `NsKub19`     | `NsLabeledKub19`     |

Confirm these IDs through document discovery, or use their verified counterparts from a newer Kubernetes library. Prefer the resource icons over plain rectangles when available. Namespace and Deployment frames can still express containment, with the matching icons identifying those groups; an icon is not automatically a container. Preserve replica counts in labels or repeated Pod icons. Select labeled/unlabeled variants for readability without treating them as AWS-style service/instance prefixes, and preserve each shape's native proportions.

Follow Lucid's instance-versus-service icon convention:

- **Specific resource instance:** Prefer a colored glyph on a transparent background. A named Lambda function such as `process_orders` or a specific DynamoDB table such as `orders` represents an instance, even though its resource type is a cloud service.
- **Service in general:** Use a white glyph on a colored background when referring to Lambda, DynamoDB, or another service generally rather than a particular resource instance.
- **Only the service icon is available:** Use the white glyph on a colored background for the instance too, preserving its specific name in the label. Check the relevant category catalog before deciding that the instance icon is unavailable; the common catalog is only a subset. Do not substitute an icon for a different resource or recolor a service icon to imitate an instance icon.

In AWS 2024, `Res…AWS2024` identifies resource shapes that commonly use the instance style, while `Arch…AWS2024` identifies service/architecture shapes that commonly use the service style. For example, use `ResAWSLambdaLambdaFunctionAWS2024` for a named function and `ResAmazonDynamoDBTableAWS2024` for a named table; use `ArchAWSLambdaAWS2024` and `ArchAmazonDynamoDBAWS2024` for their services in general or as the available fallback. These are distinct shape IDs, not a color toggle. Verify the exact ID and meaning in the current catalog. Apply the same visual convention where other providers offer suitable variants, but do not assume Azure or GCP uses AWS's naming prefixes.

Use `namedShape` with the catalog's exact `id` as `className` for service icons. Use `namedContainer` for boundary shapes marked `isContainer: true`, following the specification's containment and layout rules. Do not copy these Standard Import fields into scripting calls unless the script API explicitly accepts them.

Size every icon from its catalog `defaultWidth` and `defaultHeight`, and preserve that aspect ratio. Many resource icons are not square; for example, an AWS 2024 SQS queue is 120 × 74 and an IAM role is 120 × 70. To shrink or enlarge an icon, multiply both dimensions by the same factor. For a uniform row, choose a common width or maximum dimension and derive the other dimension from each icon's own aspect ratio. For a maximum size `S`, use `scale = S / max(defaultWidth, defaultHeight)`, `width = defaultWidth * scale`, and `height = defaultHeight * scale`. For example, an SNS topic scaled to width 90 must be 78 high, and an SQS queue at width 90 must be 55.5 high. A DynamoDB table remains square because its intrinsic size is square. If dimensions are unavailable, obtain the documented default size or inspect a newly created shape at its native size before resizing; do not assume 1:1. When replacing a shape, recompute dimensions for the replacement rather than reusing the old box. Never force every icon into the same square box; the renderer stretches the glyph to fill it.

### Step 4: Build the diagram specification

**Input:** Step 2's inventory and Step 3's schema and shape IDs. **Output:** Standard Import JSON for a new diagram, or an edit plan for the fetched existing document.

For an existing document, fetch its current content before planning edits so the plan uses its actual elements and preserves unrelated work.

Place related services within evidenced boundaries, keep traffic direction consistent, and label connections with their meaning. Summarize repeated resources when an overview is more useful than individual instances; disclose aggregation and omitted detail. Use a legend or notes to distinguish assumptions, conditional resources, and deployment dependencies from confirmed runtime connections. Append `?` to labels for assumed resources, boundaries, and connections (for example, `External publisher ?` or `Reads orders ?`), and describe their basis in the key, notes, or delivery summary. A legend/key is optional; do not add one solely to explain assumptions. If a legend/key is present and the diagram includes assumptions, include `? = Assumption (not confirmed by the code)` in it.

Surround every legend/key with a visible frame containing its title and all entries, with enough padding to keep text and line samples inside the border. Use a supported frame/container or a bordered rectangle behind the legend content, following the current specification. Keep this frame separate from architecture boundaries and route diagram connectors around it.

Choose a consistent flow direction, align related services, leave clear space between shapes, and size containers and labels to fit their content. Route connectors around unrelated shapes and labels; use separate pages or groups when an overview becomes crowded. Keep source identifiers in notes rather than making labels unreadably long.

#### Make routes and annotations easy to follow

Keep the main runtime path in one consistent direction, usually left to right. Prefer orthogonal (elbow) connectors for branches, returns, and crowded areas where several connections converge, especially permission, monitoring, failure-handling, and deployment links. Straight connectors are appropriate for clear, aligned paths. Reserve separate horizontal or vertical lanes and spaced attachment points so elbows do not overlap unrelated lines or run behind icons. Preserve the evidenced arrow direction; do not reverse a relationship merely to simplify routing. Select the supported connector style from the current Lucid specification or scripting documentation rather than guessing API fields or assuming rerouting changes the style.

Give every visible annotation an unambiguous owner. Put resource configuration directly beneath its name in the same caption or a tightly grouped caption block, with consistent spacing. For example, a queue's visibility timeout belongs with the queue, and a function's runtime and timeout belong with the function. Put longer explanations in a bordered callout that names the resource or relationship it describes; place it nearby, or use a clearly distinct non-traffic leader when proximity is insufficient. Use a separate labeled notes panel for diagram-wide omissions and unknowns. Do not scatter detached property text in open canvas space or make readers infer its owner from proximity to several shapes.

Prefer replacing the shape's native label with the resource name and caption. If a separate caption is necessary, explicitly clear or hide the native label through the supported API first; omitting text can retain default labels such as “Queue” or “Table”. Inspect the result to ensure there is only one resource caption rather than a text box layered over the original label.

Use a modest, consistent text hierarchy: resource names and primary interactions should be prominent; configuration details and callout text can be slightly smaller while remaining readable at the normal overview scale. Do not shrink text to fit a crowded layout. Expand spacing, wrap text, or move longer explanations into named callouts. Keep the provider instance glyph convention from Step 3; improving typography does not require changing icon variants or stretching icons.

#### Plan geometry around icon labels

Icon labels can cause layout rework. Plan for them before choosing coordinates; the pixel estimates below are starting points, not fixed measurements:

- **Labels render outside the icon.** AWS 2024 icon text appears centered below the icon's bounding box, not inside it, and can be much wider than the icon. Budget about 40 px below each icon for a one-line label of roughly 20 characters, and treat the label as about 7 px per character wide, centered on the icon. Use `inspect`'s rendered `footprint` once the shape exists; it includes external labels and takes precedence over estimates. Verify label placement and wrapping in the export for every library used.
- **Keep connectors off label edges.** Do not attach a connector to the bottom of an icon whose label sits there, and do not route a line beneath a neighboring icon's label. Attach runtime connectors to the sides along the flow direction, and attach permission or deployment connectors to the top.
- **Reserve space around line text.** Treat a connector label as a text box with its own clearance, not as empty space along the route. Leave a visible gap from nearby icon footprints, resource captions, arrowheads, bends, frame titles, and other labels. About one text-line height is a useful starting clearance; increase it when wrapping makes the label taller. Center labels on open segments with balanced space on either side, and place them beside or above their own line so it does not strike through the text. If there is no clear segment, lengthen the route or move the nodes instead of squeezing the label against a shape. Check the actual rendered label bounds rather than only the icon boxes.
- **Use bands for layered relationships.** For a left-to-right flow, a useful starting layout, when these elements exist in the code, is:
    - a top band for identity and control-plane resources such as IAM roles, connected down to the tops of the resources they grant access to;
    - a middle band for the runtime data path, connected side to side;
    - a lower band for failure handling, such as dead-letter queues, and policy notes;
    - deployment artifacts, such as locally built archives or images, outside the cloud boundary and nearest the resource they deploy to.
- **Center and wrap connector labels at creation.** Prefer a label centered along a clear segment of its connector, with centered multiline text and enough separation that the line does not strike through the words. On elbow routes, use a long, unobstructed segment rather than a bend or crossing; the geometric midpoint is not useful if it falls in a crowded area. Choose each label's documented `position` and `side` in the Standard Import JSON accordingly. Keep relationship labels compact: wrap at natural phrase boundaries into two or three short lines, often around 20–30 characters per line as a starting point, rather than stretching a sentence across the whole gap. For example, use “Event source mapping” followed by “batch size 10”, or “Redrive after” followed by “3 receives”. Put longer explanations in a named callout, and keep resource properties in their resource captions. Use supported text-width or line-break controls and verify the actual wrapping in the PNG. Script APIs may provide no method to move a label along an existing line, so later fixes can require moving shapes or endpoints.
- **Investigate `text-fit` warnings in context.** A check against an icon's bounding box may not account for an external label. Confirm the actual rendered footprint and PNG before treating a finding as a false positive. Fix genuine overflow or unreadable text; do not stretch the icon to accommodate its label.

For a legend, use a supported frame/container or bordered rectangle with the title and entries placed inside its border. A `containerTitle` may render above the border, so verify its placement or use a separate title text box inside the frame. Sample lines about 80 px long and rows about 50 px apart are useful starting points; size text boxes and the enclosing frame to fit the actual content.

For example, an AWS SQS event source targeting a Lambda function maps to two verified AWS service shapes and an SQS-to-Lambda connector labeled “event source.” It does not justify adding a VPC or database.

Before creation, use `lucid_validate_diagram_specification` when available and fix structural and layout findings. Trace every node and connector back to a confirmed definition or explicit assumption in Step 2; account for omitted resources and check that every assumption label includes `?`.

### Step 5: Create or update the Lucid document

**Input:** Step 4's validated specification or edit plan. **Output:** A document ID, editable URL, and current element IDs for verification and refinement.

For a new diagram, call `create_diagram_from_specification` (commonly `lucid_create_diagram_from_specification`) using the current tool schema: a descriptive `title`, `product: "lucidchart"`, and the serialized specification in `standard_import_json`. Set `use_assisted_layout` consistently with the layout chosen in Step 4; use `false` for deliberately positioned shapes.

For an existing document, use the content fetched in Step 4 and refresh it if needed before mutation. Use runscript (`lucid_run_script`) to edit or refine the requested architecture, including shapes, labels, connections, and layout:

1. Call `lucid_get_script_catalog` for the target document to discover available scripting APIs.
2. Load relevant references with `lucid_load_script_documentation` to verify exact method names, arguments, and return values. If an example API or method below is unavailable, look for an equivalent in the catalog and its references.
3. Invoke the verified `skills.<name>.<method>(...)` calls through `lucid_run_script`, using current document element IDs. Do not guess scripting methods or reuse IDs from another document. If no supported equivalent exists, report that limitation.

Creation produces a new document; use scripting when the user wants to update the existing one. Return the document element IDs needed for later calls in the script result, with meaningful names so the model can retain and reuse them. If an ID is missing or no longer current, read the document through a documented scripting API to retrieve it before editing. These are IDs of elements in the document, not shape-library IDs. If a mutation's outcome is unclear, inspect the document before retrying to avoid duplicate content.

### Step 6: Verify coverage, inspect the PNG, and correct defects

**Input:** The created or updated document from Step 5 and the evidence inventory from Step 2. **Output:** A structurally checked, visually inspected diagram, or an explicit account of checks that could not be completed.

1. Reconcile the current document with the Step 2 inventory: for each material resource, relationship, boundary, and configuration fact, identify its visible representation or explicitly account for its omission. Hidden notes or the final chat response do not satisfy a required visible annotation. Check parent–child containment, required integration prerequisites, and material unknowns as well as missing or duplicate resources, incorrect shape meanings, unsupported containment, and reversed connections. Confirm that each resource and relationship matches the inventory or is visibly marked with `?` as an assumption. Confirm that each assumption is explained in the key, notes, or delivery summary. If a legend/key is present, confirm that it has a visible enclosing frame and, when assumptions are shown, a `? = Assumption` entry.
2. Follow the catalog/documentation process in Step 5 to find the target document's inspection and validation capabilities before running them. For example, if confirmed by the catalog and loaded references, use a read-only `lucid_run_script` call to return `skills.basecanvasediting.inspect(ids)` and `await skills.basecanvasediting.validateCanvas(...)`, with documented validators such as `lineTextOverlapsBlock`, `lineThroughBlock`, `blockOverlap`, and `textOverflow`. If those names are absent, use the equivalent inspection or validation methods discovered in the catalog and their documented arguments. Use the returned rendered footprints to plan related corrections together. After a mutation, await validation in that script and return its findings and changed IDs. These checks complement the PNG inspection; unavailable APIs do not justify skipping the visual check.
3. Call `lucid_export_document_as_PNG` for the target document and relevant pages, following its current parameter schema. Open and look at the returned image; a successful export alone is not visual verification.
4. Inspect the full page for hierarchy and overall readability, then inspect detailed regions at a useful scale for small text and dense connections. Keep legend text readable and consistent with the other annotations; enlarge its text boxes and frame rather than shrinking it to fit. Check for overlapping shapes, unintended overlapping line segments, lines crossing unrelated shapes or labels, clipped text, confusing crossings, and inconsistent alignment or spacing. Intentional container nesting is not a defect. Check arrow direction and readable connection labels as well. Compare each actual `className` with the service-specific ID selected in Step 3, not just the visible label. Replace provisional generic shapes when discovery found a suitable exact icon, including Kubernetes resources and Azure storage queues. Confirm that named resource instances use instance icons when available, while general service references use service icons. Check that `width / height` matches the catalog aspect ratio (allowing rounding) and that no icon looks stretched or squashed.
    - Trace each connector from source to arrowhead without relying on color alone. Replace crowded diagonal fans with elbow routes and separate lanes where that improves clarity; elbows still fail if they run through icons, captions, or other line labels. Check that connector labels are compact, centered on clear segments, and separated from bends and crossings.
    - For every configuration caption or explanatory note, identify the resource, relationship, or diagram-wide scope it belongs to from the visible diagram alone. If ownership is ambiguous, move it into the resource caption or a named, bordered callout. Check that the text hierarchy is consistent and that secondary details remain readable.
    - Check that every evidenced account/project/subscription and region scope has its intended enclosing frame, its title is visible, and its members are correct. Global resources must remain outside single-region groups. Confirm that custom captions do not coexist with leftover default shape labels and that connector labels have visible clearance from nearby resource captions.
5. Correct defects with `lucid_run_script`, using the catalog/documentation process in Step 5. Move or resize shapes and containers, and reroute or separate connectors through the documented APIs. Preserve connection endpoints, icon aspect ratios, and architectural meaning while improving readability. Plan each correction against every nearby shape, icon label, and connector label rather than only the reported defect, because a single shape move can create a new collision. When editing connectors:
    - For a fixed block attachment, use the endpoint's documented `connection: {x, y}` with normalized coordinates from 0 to 1. This pins the attachment by default; use `autoLink: true` only when it may move automatically. Keep scripting endpoint fields distinct from Standard Import endpoint fields.
    - When changing a crowded straight connector to an elbow, first select the documented orthogonal connector style, then prefer `skills.basecanvasediting.rerouteLines(...)` after adjusting spacing or endpoints. Rerouting alone does not establish the desired connector style. The `lines` API provides `setRoute`, but its current guidance reserves manual routing for an explicitly requested path; load and follow that reference when applicable.
    - If no documented method moves a connector label, clear it by moving shapes or endpoints, or shorten the label text.
6. Export a fresh PNG and inspect it again after the last visual edit, including small label or legend changes. Recheck semantic coverage after edits so layout fixes do not remove required information. Repeat inspection, correction, and export as many times as needed to make the diagram accurate and readable; there is no fixed iteration limit. Prefer well-planned corrections that address related issues together, but do not stop merely to reduce the number of rounds. If a tool or API limitation prevents further progress, report the specific remaining issue and do not claim full verification. Refine the same document instead of creating replacement documents for layout revisions.

**Acceptance check before delivery:** Verify that the visible diagram covers the scoped inventory, shows the correct containment and relationship types, preserves material configuration and uncertainty, uses verified shapes with native proportions, and has a readable framed legend when present. Confirm that the inspected PNG reflects the final state. Known fixable omissions or readability defects mean refinement is still needed; acknowledging them in chat does not complete verification. If a tool limitation blocks a check or correction, state the specific unresolved issue and qualify the verification status. There is no fixed correction-round limit.

### Step 7: Deliver the verified diagram

**Input:** The document and verification result from Step 6. **Output:** A concise handoff containing:

- The editable Lucid document link and PNG preview when available.
- What the diagram covers, including source scope and environment.
- Material assumptions, aggregations, unresolved values, and omitted components.
- Verification status and any remaining visual or tool limitation.

Explain that the diagram is a snapshot of the inspected code, not live cloud discovery or automatic synchronization.

## Example

**Input:** Terraform defines an SQS queue, a Lambda function, and this event source mapping:

```hcl
resource "aws_lambda_event_source_mapping" "orders" {
  event_source_arn = aws_sqs_queue.orders.arn
  function_name    = aws_lambda_function.process_orders.arn
}
```

**Output:** AWS SQS and Lambda icons labeled `orders` and `process_orders`, joined by an SQS-to-Lambda connector labeled “event source.” Look up their exact shape IDs in the AWS catalog, preserve Terraform resource addresses in notes, and inspect the exported PNG after creation.

The integration establishes the connection; a generic `depends_on` would not. No region, subnet, or downstream database is invented from this snippet.

## Common pitfalls

- **Terraform as a shape library:** Searching for Terraform icons for cloud resources. Select the represented provider's catalog instead.
- **Every reference becomes traffic:** Drawing runtime arrows for provisioning dependencies or permitted access. Use Step 2's evidence-to-element mapping.
- **Guessed module internals:** Expanding an unavailable module into a familiar architecture. Keep its internals explicitly unresolved.
- **Export without inspection:** Treating a successful PNG response as proof of readability. View the image, correct defects with runscript, and inspect a new export.
- **Ambiguous catalog labels:** Choosing a generic `Table` or `Topic` by label alone, or rejecting a correct service-specific shape because its label is short. Verify the full catalog ID, provider, service, and resource type.
- **Static catalogs mistaken for all libraries:** Concluding Kubernetes icons do not exist because no Kubernetes resource URI is advertised. Query the document's `shapelibrary` API and `kubernetes2019.js` before a fallback.
- **Stopping at the obvious category:** Missing Azure `StorageQueueAzure2024` because only `common` and `storage` were read. Search `general` and the document library before using a generic queue.
- **Squashed icons:** Giving every icon the same square bounding box. Scale each icon proportionally from its catalog default size.
- **Connectors through icon labels:** Attaching lines to an icon's bottom edge or placing icons as if their labels fit inside their bounding boxes. Reserve space below each icon and use the band layout in Step 4.

## Limitations

Static code describes intended configuration and can leave runtime behavior, external modules, and instance counts unresolved. The diagram is only as complete as the inspected scope and available evidence.

Supported shapes and scripting APIs depend on the connected Lucid MCP and target document. If the MCP is unavailable, identify the needed connection; a local architecture inventory is partial work, not a created Lucid diagram. Report unavailable validation or preview capabilities without silently substituting another diagramming service.
