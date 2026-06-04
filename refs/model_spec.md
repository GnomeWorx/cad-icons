# Fusion 360 Plastic Design Tools — Function Point Specification

## Document Control

| Property | Value |
|----------|-------|
| **Document ID** | FISSIONCAD-SPEC-MD |
| **Title** | Fusion 360 Plastic Design Tools — Function Point Specification |
| **Ref Prefix** | MD-xxx |
| **Total Function Points** | 96 |
| **Last Generated** | 2026-06-04 |

---

## 3.3.1 Rule Components

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 1 | MD-004 | Physical Material | Material type (ABS, Nylon, etc.) \| Affects mass/physical properties |
| 2 | MD-005 | Physical Values | Thickness, Draft Angle, Nominal Radius \| Referenced by modeling commands |
| 3 | MD-006 | Design Advice Values | Thickness range, Thickness variation, Minimum draft angle, Knife-edge threshold \| Used for manufacturability analysis |

## 4.1 Boss Tool - Fastener Integration

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 4 | MD-019 | Fastener: Library selection | Select from library of fasteners (standards-based) |
| 5 | MD-020 | Fastener: Configuration (head, drive, length, material) | Configure: Head Type, Drive, Length, Thread Angle, Diameter, Material, Surface Finish |
| 6 | MD-021 | Fastener: Component creation | Fastener added as new component to file |

## 4.2 Snap Fit Tool

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 7 | MD-025 | Snap Fit: Positioning method | Position via sketch points between two bodies |
| 8 | MD-026 | Snap Fit: Hook angle adjustment | Individual or global hook angle adjustment |
| 9 | MD-027 | Snap Fit: Hook extension/shortening | Hook extension/shortening controls |
| 10 | MD-028 | Snap Fit: Automatic clearance cut | **Automatic clearance cut** when hook intersects second body |

## 4.3 Rib/Web Tool

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 11 | MD-029 | Rib: Thickness from Plastic Rule | Thickness driven by Plastic Rule |
| 12 | MD-030 | Rib: Draft from Plastic Rule | Draft Angle applied automatically |
| 13 | MD-031 | Rib: Associative features | Associative top/bottom features created |

## 4.4 Shell Tool

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 14 | MD-032 | Shell: Thickness from Plastic Rule | Thickness automatically populates from Plastic Rule when rule is assigned |
| 15 | MD-033 | Shell: Plastic Rule prerequisite | Must assign Plastic Rule **before** using Shell for inheritance to work |

## 4.4.1 Boss Tool

_6 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 16 | MD-013 | Positioning | Requires sketch point (recommended on offset or mid-plane) |
| 17 | MD-014 | Offset Position | Distance from sketch plane |
| 18 | MD-015 | Diameter | Boss outer diameter |
| 19 | MD-016 | Fastener Diameter | Inner hole diameter for screw/insert |
| 20 | MD-017 | Direction | Boss extrusion direction |
| 21 | MD-018 | Dual Bosses | Creates bosses on both sides of sketch plane when two bodies visible |

## 4.4.2 Snap Fit Tool

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 22 | MD-022 | Parallel Hook & Groove | Hook and groove aligned with pull direction |
| 23 | MD-023 | Perpendicular Hook & Groove | Hook perpendicular to pull direction |
| 24 | MD-024 | Hook & Loop | Cantilever hook with catching loop |

## 4.4.7 Geometric Pattern Tool

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 25 | MD-040 | Size Limit / Range | Varies object sizes from smallest to largest across pattern |
| 26 | MD-041 | Border Clearance | Option to keep border clear of pattern elements |
| 27 | MD-042 | Face Selection | Pattern fills selected face(s) |
| 28 | MD-043 | Join/Cut/New Body | Boolean operation options |

## 4.5 Draft Tool

_1 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 29 | MD-034 | Draft: Value from Plastic Rule | Draft Angle value inherits from Plastic Rule |

## 4.5 Draft Tool - Prerequisites

_1 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 30 | MD-035 | Draft: Pull direction requirement for Design Advice | Pull direction must be defined for Design Advice analysis |

## 4.6 Thicken Tool

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 31 | MD-036 | Thicken: Value from Plastic Rule | Thickness value inherits from assigned Plastic Rule |
| 32 | MD-037 | Thicken: Plastic Rule prerequisite | Requires rule assignment prior to feature creation |

## 4.7 Geometric Pattern - Applications

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 33 | MD-044 | Application: Ventilation holes | Ventilation holes |
| 34 | MD-045 | Application: Grip textures | Grip textures |
| 35 | MD-046 | Application: Aesthetic patterns | Aesthetic patterns |
| 36 | MD-047 | Application: Light passages | Light passages |

## 4.7 Geometric Pattern - Shapes

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 37 | MD-038 | Geometric Pattern: Default shapes (Sphere, Cylinder, Cube) | Default shapes: Sphere, Cylinder, Cube |
| 38 | MD-039 | Geometric Pattern: Custom shape from solid body | Custom shape: Any solid body in file |

## 5.5.1 Design Advice (Preview)

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 39 | MD-051 | Thickness | Large variations, walls too thin, walls too thick |
| 40 | MD-052 | Undercuts | Features requiring sliders or lifters in mold |
| 41 | MD-053 | Draft | Faces with insufficient draft angle |
| 42 | MD-054 | Knife-edge | Thin, long tool features (causes premature wear) |

## Core vs. Extension: Tool Availability Summary

_9 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 43 | MD-061 | Plastic Rules | ✗ \| ✓ |
| 44 | MD-062 | Assign Plastic Rule | ✗ \| ✓ |
| 45 | MD-063 | Boss | ✗ \| ✓ |
| 46 | MD-064 | Snap Fit | ✗ \| ✓ |
| 47 | MD-065 | Rib/Web (enhanced) | ✗ \| ✓ |
| 48 | MD-066 | Geometric Pattern | ✗ \| ✓ |
| 49 | MD-067 | Design Advice | ✗ \| ✓ |
| 50 | MD-068 | Volumetric Lattice | ✗ \| ✓ (Preview) |
| 51 | MD-069 | Organic Mesh Conversion | ✗ \| ✓ |

## Design Advice - Recommendations

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 52 | MD-055 | Design Advice: Actionable recommendations | Each alert includes actionable recommendations |
| 53 | MD-056 | Design Advice: Learning links | Links to in-depth concepts for learning |
| 54 | MD-057 | Design Advice: Region ignore option | Option to ignore specific regions after addressing |

## Key Benefits Summary

_5 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 55 | MD-089 | Parametric propagation | Change material → all plastic features update automatically |
| 56 | MD-090 | Manufacturing awareness | Features designed with injection molding constraints built-in |
| 57 | MD-091 | Reduced clicks | Secondary features (draft, fillet) applied automatically |
| 58 | MD-092 | Design validation | Catch manufacturability issues before prototyping |
| 59 | MD-093 | Fastener library | Integrated screw/insert library with component generation |

## Related Extensions

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 60 | MD-094 | Product Design Extension | Plastic rules, bosses, snaps, geometric patterns, design advice |
| 61 | MD-095 | Simulation Extension | Stress analysis, snap performance, mold filling simulation |
| 62 | MD-096 | Fusion with PowerShape | Core/cavity splitting, mold-base design, electrode modeling |

## Volumetric Lattice - Parameters

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 63 | MD-058 | Lattice: Cell shape | Cell shape |
| 64 | MD-059 | Lattice: Cell size | Cell size |
| 65 | MD-060 | Lattice: Density | Density |

## Workflow

_19 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 66 | MD-007 | Workflow Step 1: Access Plastic Tab → Assign Plastic Rule |  |
| 67 | MD-008 | Workflow Step 2: Select target component |  |
| 68 | MD-009 | Workflow Step 3: Choose pre-defined rule or create custom |  |
| 69 | MD-010 | Workflow Step 4: Rule populates Parameters dialog automatically |  |
| 70 | MD-011 | Workflow Step 5: Subsequent features inherit rule values |  |
| 71 | MD-012 | Workflow Step 6: Change material → all features update automatically |  |
| 72 | MD-048 | Workflow Step 1: Select Design Advice in Plastic tab |  |
| 73 | MD-049 | Workflow Step 2: Select component and pull direction (tool movement direction after injection) |  |
| 74 | MD-050 | Workflow Step 3: Click Analyze |  |
| 75 | MD-079 | Workflow Step 1: Activate Product Design Extension |  |
| 76 | MD-080 | Workflow Step 2: Access Plastic Tab in Design Workspace |  |
| 77 | MD-081 | Workflow Step 3: Assign Plastic Rule to component(s) |  |
| 78 | MD-082 | Workflow Step 4: Create base geometry (Extrude, Revolve, etc.) |  |
| 79 | MD-083 | Workflow Step 5: Apply Shell (inherits thickness from rule) |  |
| 80 | MD-084 | Workflow Step 6: Add plastic features: |  |
| 81 | MD-085 | Workflow Step 7: Apply automatic Draft and Fillet (rule-driven) |  |
| 82 | MD-086 | Workflow Step 8: Run Design Advice analysis |  |
| 83 | MD-087 | Workflow Step 9: Iterate and refine |  |
| 84 | MD-088 | Workflow Step 10: (Optional) Run mold filling simulation with Simulation Extension |  |

## Workflow (Detail)

_9 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 85 | MD-070 | Select material (ABS, Nylon, etc.) |  |
| 86 | MD-071 | Define/confirm physical values |  |
| 87 | MD-072 | Set design advice thresholds |  |
| 88 | MD-073 | Boss (from sketch points) |  |
| 89 | MD-074 | Snap Fits (from sketch points) |  |
| 90 | MD-075 | Ribs/Webs |  |
| 91 | MD-076 | Define pull direction |  |
| 92 | MD-077 | Review thickness/undercut/draft/knife-edge alerts |  |
| 93 | MD-078 | Implement recommendations |  |

## Workspace & Access

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 94 | MD-001 | Location | Design Workspace → Plastic Tab |
| 95 | MD-002 | Prerequisite | Product Design Extension active |
| 96 | MD-003 | Best Practice | Assign Plastic Rules before creating features |

---

*End of specification — 96 function points total.*
