# Fusion 360 Sketch Tools — Function Point Specification

## Document Control

| Property | Value |
|----------|-------|
| **Document ID** | FISSIONCAD-SPEC-SK |
| **Title** | Fusion 360 Sketch Tools — Function Point Specification |
| **Ref Prefix** | SK-xxx |
| **Total Function Points** | 78 |
| **Last Generated** | 2026-06-04 |

---

## 3.3.1 Basic Geometry

_9 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 1 | SK-006 | Line | Creates straight line segments \| Start point, end point, length |
| 2 | SK-007 | Circle | Center-diameter or 2-point circle \| Center point, radius/diameter |
| 3 | SK-008 | Arc | 3-point, center-point, or tangent arc \| Start, end, radius/center |
| 4 | SK-009 | Rectangle | 2-point, 3-point, center, or centered rectangle \| Corner points, dimensions |
| 5 | SK-010 | Polygon | Regular polygon (3-64 sides) \| Center, radius, side count, rotation angle |
| 6 | SK-011 | Ellipse | Oval shape \| Center, major radius, minor radius, rotation angle |
| 7 | SK-012 | Slot | Rounded rectangle/oblong hole \| Center, length, width, rotation, type (overall or center-to-center) |
| 8 | SK-013 | Spline | Smooth curve through control points \| Array of points, closed/open option |
| 9 | SK-014 | Point | Construction reference point \| X, Y coordinates |

## 3.3.2 Text Tool

_1 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 10 | SK-015 | Text | Adds text for engraving/embossing \| Content, position, height, font, bold/italic |

## Constraint Status Colors

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 11 | SK-003 | Color: Blue = Under-defined | Blue geometry = Under-defined (missing constraints/dimensions) |
| 12 | SK-004 | Color: Black = Fully defined | Black geometry = Fully defined |

## Constraint Tools (Geometric Relationships)

_15 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 13 | SK-035 | Coincident | ● \| Forces two points to share the same location |
| 14 | SK-036 | Horizontal | ↔ \| Forces line to be exactly horizontal |
| 15 | SK-037 | Vertical | ↕ \| Forces line to be exactly vertical |
| 16 | SK-038 | Parallel | ∥ \| Forces two lines to run in same direction |
| 17 | SK-039 | Perpendicular | ⟂ \| Forces two lines to meet at 90° |
| 18 | SK-040 | Tangent | ○— \| Forces curve to touch another curve smoothly at one point |
| 19 | SK-041 | Equal | ≡ \| Forces lengths or radii to be identical |
| 20 | SK-042 | Concentric | ◎ \| Forces circles/arcs to share center point |
| 21 | SK-043 | Collinear | — \| Forces lines to lie on same infinite line |
| 22 | SK-044 | Fix | 📌 \| Locks entity position |
| 23 | SK-045 | Midpoint | ◇ \| Forces point to midpoint of line |
| 24 | SK-046 | Symmetric | ⇄ \| Forces symmetry across centerline |
| 25 | SK-047 | Curvature | () \| Maintains curvature continuity between splines (G2) |
| 26 | SK-048 | Black (=Fully constrained) |  |
| 27 | SK-049 | Blue (=Under-constrained (free to move)) |  |

## Construction & Reference Tools

_6 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 28 | SK-058 | Construction Geometry | Creates reference geometry that doesn't form profiles \| Dashed/dotted lines |
| 29 | SK-059 | Centerline | Creates axis geometry that participates in profiles \| Dot-dash lines |
| 30 | SK-060 | Project | Projects 3D edges/faces onto current sketch plane \| Projected geometry |
| 31 | SK-061 | Project Cut Edges | Projects intersection of plane with existing bodies \| Intersection curves |
| 32 | SK-062 | Construction | Purely reference—does not affect profiles |
| 33 | SK-063 | Centerline | Acts as profile boundary, used for symmetry and revolve axes |

## Dimension Best Practices

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 34 | SK-054 | Best Practice: Name dimensions meaningfully | Name dimensions descriptively (e.g., `hole_offset = 0.1 * width`) |
| 35 | SK-055 | Best Practice: Use expressions/parameters | Use expressions to create relationships between parameters |
| 36 | SK-056 | Best Practice: Fully constrain sketches | Fully constrain sketches for predictable updates |

## Dimension Tools (Parametric Constraints)

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 37 | SK-050 | Distance Dimension | Linear distance between two points or line length \| Value (mm), text position |
| 38 | SK-051 | Radius Dimension | Radius of arc or fillet \| Value (mm) |
| 39 | SK-052 | Diameter Dimension | Diameter of circle \| Value (mm) |
| 40 | SK-053 | Angle Dimension | Angle between two lines \| Value (degrees) |

## Environment Notes

_1 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 41 | SK-005 | Shortcut `S` for Tool Search | Use `S` key to open shortcut menu for quick tool access |

## Grid & Snap Options

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 42 | SK-068 | Grid: Visibility toggle | Grid visibility |
| 43 | SK-069 | Grid: Snap to grid | Snap to grid |
| 44 | SK-070 | Snap: Point snapping | Snap points |

## Inspection & Display Tools

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 45 | SK-064 | Measure | Measures distances between points, edges, or surfaces |
| 46 | SK-065 | Sketch Palette | Controls grids, snaps, profile display, and geometry type |
| 47 | SK-066 | Profile Display | Shows closed profiles with blue highlighting |
| 48 | SK-067 | Points Display | Shows all sketch points to identify gaps |

## Modify Tools

_9 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 49 | SK-020 | Trim | Removes excess sketch lines up to intersection boundaries  \| Click segment to remove |
| 50 | SK-021 | Extend | Extends line to nearest boundary \| Click line near end to extend |
| 51 | SK-022 | Offset | Creates parallel copy of geometry at specified distance \| Select geometry, set distance, chain selection option |
| 52 | SK-023 | Move/Copy | Translates or rotates geometry \| Select entities, specify displacement vector/angle |
| 53 | SK-024 | Rotate | Rotates geometry about point \| Select entities, center point, angle |
| 54 | SK-025 | Scale | Resizes geometry about reference point  \| Select entities, base point, scale factor |
| 55 | SK-026 | Fillet | Rounds corners with specified radius \| Select corner/intersection, radius value |
| 56 | SK-027 | Chamfer | Bevels corners with specified distances \| Select corner, equal distance or two distances |
| 57 | SK-028 | Break | Splits geometry into segments at selected points  \| Select geometry, click split points |

## Pattern Tools

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 58 | SK-032 | Rectangular Pattern | Creates array of copies in grid formation  \| X count, Y count, X spacing, Y spacing |
| 59 | SK-033 | Circular Pattern | Creates array of copies around center point  \| Center point, instance count, total angle |
| 60 | SK-034 | Mirror | Creates mirrored copy across symmetry line  \| Geometry to mirror, mirror line |

## Shortcut Keys

_8 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 61 | SK-016 | Shortcut `C` | Circle |
| 62 | SK-017 | Shortcut `L` | Line |
| 63 | SK-018 | Shortcut `X` | Construction toggle |
| 64 | SK-019 | Shortcut `P` | Project |
| 65 | SK-029 | Shortcut `T` | Trim |
| 66 | SK-030 | Shortcut `M` | Move |
| 67 | SK-031 | Shortcut `Q` | Extrude (exits sketch) |
| 68 | SK-057 | Shortcut `D` | Dimension |

## Sketch Creation & Environment Setup

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 69 | SK-001 | Create Sketch | Creates a new 2D sketch on a selected plane or face \| Toolbar → Create Sketch or right-click → Create Sketch |
| 70 | SK-002 | Finish Sketch | Exits sketch environment and saves changes \| Toolbar → Finish Sketch |

## Workflow

_8 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 71 | SK-071 | Workflow Step 1: Create Sketch → Select Plane |  |
| 72 | SK-072 | Workflow Step 2: Create Geometry (Lines, Circles, etc.) |  |
| 73 | SK-073 | Workflow Step 3: Apply Constraints (Horizontal, Parallel, Tangent, etc.) |  |
| 74 | SK-074 | Workflow Step 4: Add Dimensions (Distance, Radius, Angle) |  |
| 75 | SK-075 | Workflow Step 5: Modify as Needed (Trim, Offset, Fillet, Pattern) |  |
| 76 | SK-076 | Workflow Step 6: Verify Geometry (Blue = Under-defined → Black = Fully defined) |  |
| 77 | SK-077 | Workflow Step 7: Finish Sketch |  |
| 78 | SK-078 | Workflow Step 8: Create 3D Feature (Extrude, Revolve, etc.) |  |

---

*End of specification — 78 function points total.*
