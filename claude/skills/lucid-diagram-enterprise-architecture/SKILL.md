---
name: lucid-diagram-enterprise-architecture
description: 'Use this skill first for explicit enterprise architecture, ArchiMate, or business/application/technology architecture views, even when the source is code; lucid-diagram-code handles other code diagrams. Create or edit in Lucid with native ArchiMate 3.2/4.0 shapes or regular flowchart notation. Cloud infrastructure requests without an enterprise architecture view are outside this skill.'
user-invocable: true
metadata:
    version: 1.0
    author: 'Lucid Software'
---

# Enterprise architecture diagram

## Scope and notation

- Use the requested ArchiMate version (3.2 or 4.0) or regular flowchart notation. If ArchiMate is requested without a version, ask; when interaction is unavailable, choose 3.2 and disclose it. If notation is unspecified, ask whether ArchiMate is needed; when interaction is unavailable, choose flowchart and disclose it.
- Keep current, conditional, and planned architecture distinct. Do not place a proposed integration in a current-state view, including in its notes or legend.
- When code is the source, model deployable systems and evidenced runtime interactions, not each import or in-process module as a system. An import, registration, or TODO does not establish a call; an unnamed caller or consumer is not an architecture participant. Put branch conditions on the relationships they govern, such as a write or publish that happens only after a successful reservation.
- Use Standard Import only to bootstrap an empty document. Build and edit all architecture content through RunScript, including regular flowcharts; Standard Import does not cover every native ArchiMate shape.

## Choose ArchiMate elements

- A team or organization is a Business Actor; a responsibility that several actors can fill is a Business Role. A named sequence of business work is a Business Process; an externally offered capability is a Service.
- A Business Object is conceptual information such as Order. A Data Object is that information structured for an application, such as rows in an `orders` table. Similar names do not prove a realization relationship between them.
- A deployable business application is an Application Component. Shared middleware such as a message broker, database management system, or operating system is technology System Software; a named hosting environment is a Node.
- Distinguish an event occurrence from its payload. Use an Application Event when the source says an event is published; add a Data Object only when message content belongs in the requested view. Do not invent a consumer.

## Keep ArchiMate version and relationships valid

- Find the requested version's native shapes through the document's `skills.shapelibrary.shapeLibrary(...)` catalog, and create them through RunScript with the returned `(libraryId, id)` pair. ArchiMate 4 uses Common Process and Service shapes across layers; apply the requested layer styling to those returned shapes. Do not use flowchart lookalikes or borrow shapes from another ArchiMate version. If the library is unavailable, say the requested diagram cannot be delivered; disclose any empty bootstrap document as empty.
- Check each ArchiMate relationship against an authoritative rule for the selected version and its exact source and target element types when that reference is available. The Lucid shape catalog and model memory are not rule checks. Without a checked reference, label relationship choices as provisional; never call one valid, allowed, or derived, or claim ArchiMate compliance. If strict compliance is required, ask for the version-specific reference before drawing those relationships.
- For Access, the source is the accessing element and the target is the passive object. Its arrowhead points toward the reader for read, toward the object for write, and both ways for read/write. If the source only says "accesses", use Access without a read/write arrowhead.
- Do not infer a technology product, deployment artifact, hosting relationship, business-to-data realization, or event delivery destination from a suggestive name alone. State material source uncertainty and any unverified relationship when delivering the view.
- Before delivering an ArchiMate view, check saved library IDs and relationship endpoints against the source; inspect rendered layer placement and Access arrowheads.
