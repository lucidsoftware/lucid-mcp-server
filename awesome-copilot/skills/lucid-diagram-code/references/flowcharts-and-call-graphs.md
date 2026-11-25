# Flowcharts and call graphs

Use with the shared workflow in [SKILL.md](../SKILL.md).

## Shapes

| Element                                               | Lucid shape                                                       |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| Start or end                                          | `terminator`                                                      |
| Step or statement block                               | `process`                                                         |
| Call to another function that is documented elsewhere | `predefinedProcess` (needs `sideWidth`, e.g. 0.1)                 |
| Decision                                              | `decision`                                                        |
| Input or output                                       | `data`                                                            |
| Database read or write                                | `database`                                                        |
| Function in a call graph                              | `rectangle` (name only), grouped by file in `rectangleContainer`s |
| Continues on another page                             | `offPageLink`, with a `gotoPage` action                           |

## Flowchart style

Use for "how does X work", a named feature or pipeline, or any time the user asks for a flow. It is a flowchart whose steps come from the real code path, not from the class structure.

1. Trace one path from the entry point (route handler, exported function, event listener, CLI command) to its outcome, following calls across files. Record the file and function for each step.
2. Draw steps as `process`, branches as `decision` (label each exit with the condition from the code), external calls as `predefinedProcess`, I/O as `data`, stores as `database`, and entry and exit as `terminator`. Label steps in plain language and add the function name on a second line, e.g. `Validate order<br>OrderService.validate`.
3. When the path crosses modules or services, use `swimLanes` with one lane per module so hand-offs are visible. Never combine two modules in one lane, even when a module has a single step. Show error and early-return branches, but fold repeated handling into one shared exit.
4. Keep it to one scenario per page (about 25 shapes). Put sub-flows on their own page, linked with `offPageLink`, instead of cramming them in.
5. Do not invent steps that are implied but not in the code. Put guesses in the assumptions list and mark the connector (or the step, when the guess is about the step itself) with `?`, for example `Yes?` on a branch whose condition you inferred, or `Send reset email?` on a step whose place in the order you inferred. A guess about the order of two steps puts the `?` on the connector between them.

## Layout

Size labeled rectangles at 320 x 140 px, with labels of about 90 characters or less, and keep boxes of the same kind the same size. Lay flowcharts out from top to bottom with branches side by side. For both views, apply the shared sizing, connector, and verification guidance in Steps 5 and 6 of the core skill. Explicit user requests override the default shape count and page splitting.
