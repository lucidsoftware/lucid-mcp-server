# Sequence diagrams

Use with the shared workflow in [SKILL.md](../SKILL.md).

Use `lucid_create_sequence_diagram` (PlantUML markup). Read `lucid://skills/sequence-diagram-specification` before building the diagram, as directed in Step 4 of the core skill.

Keep one scenario per diagram. Trace the request or workflow across modules or services from the code, using the components and relationships extracted in Step 3.

Apply the shared post-creation verification in Step 6: export and inspect the PNG, and confirm each connector points in the direction supported by the code. Use the script workflow there to correct verification findings. The Standard Import JSON validation and elbow-routing rules apply to JSON-built diagrams, rather than this PlantUML route.
