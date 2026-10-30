# UML class diagrams

Use with the shared workflow in [SKILL.md](../SKILL.md).

**Stereotype text:** Always use literal Unicode guillemets (`«` and `»`) around stereotypes in Lucid labels. Double angle brackets can be interpreted as markup and lose the stereotype text during import. Always convert incoming double-angle-bracket stereotype notation to guillemets, even when the user asks to preserve the supplied notation verbatim. Preserve the stereotype words, class name, and line breaks. When exact text was requested, briefly explain that the delimiters were changed so Lucid preserves the visible stereotype. For example, use `"title": "«abstract»\nEncryptableRecord"`: the stereotype is on the first line and the class name is on the second.

## Map code to UML

| In the code                                                                                                                                                                                                       | Draw as                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Interface-like contract: Java/C#/Kotlin/TypeScript/PHP `interface`, Go `interface`, Rust `trait`, Swift `protocol`, Scala `trait` with only abstract members, Python `Protocol` or ABC with only abstract methods | `umlClass` with `«interface»`                                                                                                   |
| Abstract class (Java/C#/TypeScript/PHP `abstract class`, C++ class with pure virtual methods, Python ABC with some implementation)                                                                                | `umlClass` with `«abstract»`                                                                                                    |
| Data or value type: Scala `case class`, Kotlin `data class`, Java `record`, C# `record`, Python `@dataclass`, Rust or Go `struct`, Swift `struct`                                                                 | `umlClass` with the source-language term, such as `«record»`, `«case class»`, or `«struct»`; generic `«data»` requires a legend |
| Singleton or static holder: Scala `object`, Kotlin `object`, Ruby module used as a namespace, class with only static members                                                                                      | `umlClass` with `«object»` (or `«singleton»`); join a companion object to its class with a dashed line                          |
| Enum or sealed hierarchy of fixed named values: Scala sealed trait with case objects, fieldless Rust `enum`, Kotlin sealed hierarchy of singleton values                                                          | `umlClass` with `«enumeration»`, values in the attribute list                                                                   |
| Mixin or trait composition: Scala `with`, Ruby `include`, Python multiple inheritance, PHP `use Trait`, Rust `impl Trait for Type`                                                                                | Realization (contract-only) or inheritance (carries behavior); mark mixins with `«mixin»`                                       |
| `extends` a class, Python `class A(B)`, C++ `: public B`                                                                                                                                                          | Inheritance relationship                                                                                                        |
| `implements`, Go type whose methods satisfy an interface, Rust `impl Trait for Type`, Swift protocol conformance                                                                                                  | Realization relationship                                                                                                        |
| Field holding another type (struct field, class attribute, Python `self.x = X()`)                                                                                                                                 | Association (or composition/aggregation, see below)                                                                             |
| Constructor or method parameter, or imported and used locally (`import`, `using`, `#include`, `require`, `use`)                                                                                                   | Dependency                                                                                                                      |
| Top-level functions or modules with no class (Go, Python, JavaScript, C, Rust modules)                                                                                                                            | `umlClass` named for the module with its functions as operations                                                                |

Whether a field is composition or aggregation usually depends on lifecycle, which static code rarely shows: default to plain association and say so.

Choose stereotypes by the declaration's role rather than its language keyword. A contract exposing abstract signatures maps to `«interface»` with dashed realization arrows from implementations; a trait or mixin supplying reusable behavior maps to `«mixin»` with inheritance for that behavior. If useful, preserve the original language keyword in a note. For summarized code, abstract signatures plus "implements" indicate the contract role unless implementation is described; mark genuinely unresolved roles as assumptions.

For data and value types, prefer the source-language term when it communicates useful semantics, such as `«record»`, `«data class»`, `«case class»`, or `«struct»`. If using the generic `«data»` instead, add a visible legend explaining its mapping to the source constructs. A sealed hierarchy is an enumeration only when its alternatives represent a fixed set of named values; variants with their own fields or behavior should remain separate types and relationships.

## Shapes and relationships

| Element                                         | Lucid shape                                           | Notes                                                                                                                                                                                                                                                                                             |
| ----------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Class, interface, abstract class, enum          | `umlClass`                                            | Has three sections: `title`, `properties` (list of strings), `methods` (list of strings). Does not accept `text`. Put the stereotype on the first line of `title`, e.g. `«interface»`. Write members UML-style: `- name: String`, `+ getName(): String` (`+` public, `-` private, `#` protected). |
| Package or module boundary                      | `rectangleContainer` (or `roundedRectangleContainer`) | Set `containerTitle` to the package name. Place classes inside its bounding box with at least 80px padding.                                                                                                                                                                                       |
| Layer grouping (presentation, domain, data)     | `swimLanes`                                           | Lanes are layers. Requires `titleBar` and lane fills.                                                                                                                                                                                                                                             |
| Note or constraint                              | `note` (Flowchart Library) or `text`                  | Attach with a dotted line.                                                                                                                                                                                                                                                                        |
| Cloud service (when diagramming infrastructure) | `namedShape`                                          | `className` comes from the shape library resource.                                                                                                                                                                                                                                                |

**UML relationships.** Lines are separate objects in the page's `lines` array. A line's endpoint `style` is the decoration drawn at that end, so put the decoration on the end that touches the parent or the whole.

| Relationship                                     | Line `stroke.style` | Decoration                                       |
| ------------------------------------------------ | ------------------- | ------------------------------------------------ |
| Inheritance (extends)                            | `solid`             | `endpoint2` (on the parent): `generalization`    |
| Realization (implements)                         | `dashed`            | `endpoint2` (on the interface): `generalization` |
| Association (has a / knows a)                    | `solid`             | `endpoint2`: `openArrow`; label with role name   |
| Dependency (uses)                                | `dashed`            | `endpoint2`: `openArrow`                         |
| Aggregation (has-a, parts can outlive the whole) | `solid`             | Whole's end: `aggregation`                       |
| Composition (owns, parts die with the whole)     | `solid`             | Whole's end: `composition`                       |

Add multiplicity (`1`, `0..*`) as line `text` entries near each end (`position` 0.1 and 0.9). Give each connector a different label so no two labels read as one.

## Detail levels

Pick the default level from the number of shapes the page would hold. Explicit user requests for detail or shape count override these guidelines, including member filtering and the split above 25 shapes. For example, keep all 30 classes on one page or include private members when the user asks, while still sizing and spacing shapes for readability.

| Shapes on a page      | Detail                                                                                                                     |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Up to about 8 classes | Full members and relationships                                                                                             |
| 9 to 20               | Public members only, drop getters/setters and private helpers                                                              |
| 21 to 25              | Titles only (class names and stereotypes), relationships kept                                                              |
| More than 25          | Split. Use an overview page (packages or containers as boxes) and one detail page per area, linked with `gotoPage` actions |

Apply the detail level while writing the `umlClass` JSON, not afterwards. Unless the user requests otherwise, at 9 or more classes, drop every `-` (private) and `#` (protected) member from the shapes, even when the input lists them.

For linked overview and detail pages, use the `gotoPage` action format in Step 5 of the core skill.

## Sizing and layout

For an inheritance tree, point every child's line at the same parent position so the elbows merge into one shared trunk, which is the UML convention.

- `umlClass` height: at least `60 + 20 x (number of property lines + method lines)` px. Width: at least `7 x (longest line length) + 32` px, minimum 220. Set `propertiesHeight` to roughly `properties / (properties + methods)`.
- Lay class hierarchies out with parents on top and children below.
- Lay classes out on a grid. Size every `umlClass` first with the sizing formula above, then set each row's height to the tallest class in that row, and start the next row at `previous row y + row height + 100`. Do the same for columns using the widest class. Do not position classes from a fixed row height, because one class with many members will overlap the row below.
- Leave at least 100px between classes, so multiplicities, role labels, and elbow bends have a clear channel.
- When any line ends on the **bottom edge** of a class (inheritance or realization arrows from the shapes below it), target **160px** under that class's bottom edge, and add 20px for each extra label or multiplicity line. This leaves room for the generalization arrowhead, elbow bends, and shared trunks. Measure from the class's bottom edge (`y + h`) to the top of the shapes pointing at it. Smaller gaps are acceptable when the final PNG clearly shows separated arrowheads, bends, and readable labels without collisions.
- Do the arithmetic: for every pair of shapes on a page, confirm their bounding boxes plus the gap do not intersect. Check this in the JSON, not by eye.
- If the PNG still shows overlapping classes, use `lucid_run_script` to move or resize them to the explicit grid coordinates, following "Correcting verification findings" in Step 6 of the core skill.
- Assisted layout may resize and move classes. Fetch the final shape bounds after layout and after script corrections, then recheck the gaps and the PNG; the submitted coordinates do not establish the final spacing.

## Verification

**UML notation:** each inheritance and realization arrow points at the parent or interface, interfaces and abstract classes carry a stereotype, stereotypes preserve the roles and source semantics described above, every aggregation or composition diamond sits on the whole's end, and at 9 or more classes no private or protected member remains on any shape unless the user requested otherwise. Check final bounds against the spacing targets, and verify that arrowheads, bends, and labels remain clear in the final PNG.

- **Missing stereotype text:** check the final document text and exported PNG for the full stereotype and class name (for example, `«abstract»` above `EncryptableRecord`). If the stereotype is empty or missing, replace it with literal guillemet text and verify again.
- **Inheritance arrows backwards:** the generalization end goes on the parent. Check every one.
- **Overlapping classes:** rows placed at a fixed height while one class has many members. Size first, then grid.

## Example

**Input:** "Diagram these classes" with:

```typescript
interface PaymentGateway {
    charge(amount: Money): Receipt;
}
class StripeGateway implements PaymentGateway {
    charge(amount: Money): Receipt {
        throw new Error('todo');
    }
}
class PaypalGateway implements PaymentGateway {
    charge(amount: Money): Receipt {
        throw new Error('todo');
    }
}
class CheckoutService {
    constructor(private gateway: PaymentGateway) {}
    pay(cart: Cart): Receipt {
        throw new Error('todo');
    }
}
```

**Scope check:** four related types in one file is a "few related classes" scope, so no question is needed.

**Output:** a UML class diagram with four `umlClass` shapes. `PaymentGateway` has `"title": "«interface»\nPaymentGateway"` with `+ charge(amount: Money): Receipt`, centered on the top row, with `StripeGateway` and `PaypalGateway` side by side below it. Each has a dashed elbow realization line from its top center to the interface's bottom center, with a `generalization` end on the interface, so the two lines share one trunk. `CheckoutService` sits beside `PaymentGateway` with a solid elbow association and an `openArrow` to it, labeled `gateway`.

The `private gateway` constructor parameter becomes an association because it is stored as a field. The multiplicity is left unset and listed as an assumption. `Money`, `Receipt`, and `Cart` are not defined in the input, so they are omitted and listed under "Left out".
