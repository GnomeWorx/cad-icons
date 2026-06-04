# Fusion 360 3D Print Tools — Function Point Specification

## Document Control

| Property | Value |
|----------|-------|
| **Document ID** | FISSIONCAD-SPEC-MK |
| **Title** | Fusion 360 3D Print Tools — Function Point Specification |
| **Ref Prefix** | MK-xxx |
| **Total Function Points** | 127 |
| **Last Generated** | 2026-06-04 |

---

## 3.1 Manufacturing Model

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 1 | MK-004 | Manufacturing Model: Non-destructive part modifications | Part modifications optimized for 3D printing without altering source geometry |
| 2 | MK-005 | Manufacturing Model: Design iteration management | Management of design iterations across print preparation phases |

## 3.3 Preferences & Settings

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 3 | MK-009 | Preference: Default export formats | Default export formats and resolutions |
| 4 | MK-010 | Preference: Mesh refinement | Mesh refinement defaults |
| 5 | MK-011 | Preference: Update behavior for linked models | Update behavior for linked models |

## 3.3.2 Additive Setup

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 6 | MK-006 | Machine Selection | Choose from printer library or configure custom machine |
| 7 | MK-007 | Print Settings | Define layer height, extrusion width, temperature parameters |
| 8 | MK-008 | Material Selection | Specify material type and properties |

## 4.1 Manual Positioning

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 9 | MK-012 | Position: Manual translation & rotation controls | Translation and rotation controls |
| 10 | MK-013 | Position: Snap-to-platform | Snap-to-platform functionality |
| 11 | MK-014 | Position: Collision detection | Collision detection during placement |

## 4.2 Automatic Orientation

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 12 | MK-015 | Auto-Orient: Minimize build height | Minimizing build height |
| 13 | MK-016 | Auto-Orient: Reduce support requirements | Reducing support requirements |
| 14 | MK-017 | Auto-Orient: Optimize surface quality | Optimizing surface quality for critical features |
| 15 | MK-018 | Auto-Orient: Avoid overhangs | Avoiding overhangs exceeding machine capabilities |

## 4.3 Automatic Arrangement

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 16 | MK-019 | Auto-Arrange: Components | Automatically arrange multiple components on build platform |
| 17 | MK-020 | Auto-Arrange: Maximize volume | Maximize build volume utilization |
| 18 | MK-021 | Auto-Arrange: Minimum spacing | Maintain minimum part spacing requirements |
| 19 | MK-022 | Auto-Arrange: Machine constraints | Respect machine-specific build area constraints |

## 4.4.4 Positioning Features

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 20 | MK-023 | Automatic Alignment | Align parts to platform or reference geometry |
| 21 | MK-024 | Orientation Optimization | Minimize build height and supports |
| 22 | MK-025 | Collision Detection | Identify inter-part and part-platform collisions |
| 23 | MK-026 | Minimum Build Height | Optimize orientation for lowest Z-height |

## 5.5.1 Support Types

_6 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 24 | MK-027 | Volume | Solid block supports \| Large overhangs, MPBF |
| 25 | MK-028 | Bar/Rod | Linear support elements \| FFF, general purpose |
| 26 | MK-029 | Polyline | Custom path-defined supports \| Complex geometries |
| 27 | MK-030 | Lattice | Grid/network structures \| Reduced material usage |
| 28 | MK-031 | Dome | Curved support caps \| Sensitive surfaces |
| 29 | MK-032 | Contour with Polyline | Boundary-following supports \| Precise edge support |

## 5.5.2 Support Customization

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 30 | MK-033 | Support Settings | Density, pattern type, contact distance |
| 31 | MK-034 | Platform Settings | Build plate adhesion options (raft, brim, skirt) |
| 32 | MK-035 | Customization | Manual addition/removal of support regions |

## 6.3 Print Statistics

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 33 | MK-045 | Statistics: Print time | Estimated print time |
| 34 | MK-046 | Statistics: Material consumption | Material consumption (length and weight) |
| 35 | MK-047 | Statistics: Energy consumption | Energy consumption estimates |
| 36 | MK-048 | Statistics: Cost calculation | Cost calculations (when material costs configured) |

## 6.6.1 Additive Toolpath Generation

_5 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 37 | MK-036 | Layer Settings | Layer height, first layer settings |
| 38 | MK-037 | Perimeter/Shell | Wall count, outer wall order |
| 39 | MK-038 | Infill | Pattern type, density, overlap percentage |
| 40 | MK-039 | Temperature | Nozzle temperature, bed temperature, cooling |
| 41 | MK-040 | Speed | Print speed, travel speed, first layer speed |

## 6.6.2 Toolpath Visualization

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 42 | MK-041 | Layer-by-Layer View | Visualize outcome at each individual layer |
| 43 | MK-042 | Nozzle Movement Simulation | Travel and extrusion moves visualized |
| 44 | MK-043 | Extrusion Visualization | Material deposition display |
| 45 | MK-044 | Retraction Display | Show retraction locations and lengths |

## 7.7.1 Additive Toolpath Simulation

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 46 | MK-049 | Toolpath Simulation | Visualize nozzle/tool movement throughout print |
| 47 | MK-050 | Layer Progression | Watch build grow layer by layer |
| 48 | MK-051 | Collision Detection | Identify collisions between tool and part |
| 49 | MK-052 | Extrusion Verification | Confirm material deposition matches expected |

## 7.7.2 Metal Powder Bed Fusion Simulation (Extension)

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 50 | MK-053 | Thermal Simulation | Predict heat distribution during printing |
| 51 | MK-054 | Stress Simulation | Identify potential warping and delamination |
| 52 | MK-055 | Compensation | Apply geometry compensation for predictable distortion |

## 8.5 Third-Party Slicer Export

_2 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 53 | MK-077 | Export: Direct to external slicer | Direct export to external slicer applications |
| 54 | MK-078 | Export: Save for manual slicer import | Save as STL/3MF for manual import |

## 8.8.1 G-Code Generation

_7 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 55 | MK-056 | Workflow Step 1: Click **Post Process** button in SIMULATE ADDITIVE TOOLPATH dialog |  |
| 56 | MK-057 | Workflow Step 2: NC Program dialog opens automatically |  |
| 57 | MK-058 | Workflow Step 3: Select appropriate post-processor for target machine |  |
| 58 | MK-059 | Workflow Step 4: Configure post-processor properties |  |
| 59 | MK-060 | Workflow Step 5: Generate and save G-code file |  |
| 60 | MK-061 | Settings Tab | Primary tab for additive manufacturing; select post-processor |
| 61 | MK-062 | Operations Tab | Not relevant for additive workflows |

## 8.8.2 Export File Formats

_5 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 62 | MK-063 | 3MF | 3D Manufacturing Format \| Preferred for multi-material/color, preserves color and material data |
| 63 | MK-064 | STL | Standard Tessellation Language \| Universal format, compatible with all slicers |
| 64 | MK-065 | G-Code | Machine instructions \| Direct printer execution |
| 65 | MK-066 | CLI | Common Layer Interface \| Industrial 3D printing systems |
| 66 | MK-067 | SLI | SLC/SLI format \| Sintering/lamination processes |

## 8.8.3 Export Resolution Options

_5 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 67 | MK-068 | Low | Standard built-in \| Standard built-in \| Quick exports, prototypes |
| 68 | MK-069 | Medium | Standard built-in \| Standard built-in \| General purpose |
| 69 | MK-070 | High | Standard built-in \| Standard built-in \| Detailed models |
| 70 | MK-071 | Ultra | 0.000508 mm \| 15 degrees \| Highly detailed geometry, large round objects |
| 71 | MK-072 | Custom | User-defined \| User-defined \| Special requirements |

## 8.8.4 Export Structure Options

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 72 | MK-073 | One File | All visible bodies in a single file |
| 73 | MK-074 | One File Per Body in Component | Individual files per body, maintains component grouping |
| 74 | MK-075 | One File Per Body in Occurrence | Individual files preserving position data for multi-material prints |
| 75 | MK-076 | One File Per Top Level Occurrence | Logical grouping for color/material separation |

## 9.2 Scripting & API

_4 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 76 | MK-082 | API: Batch export | Batch export to STL/3MF formats |
| 77 | MK-083 | API: Automated orientation/arrangement | Automated orientation and arrangement |
| 78 | MK-084 | API: Custom post-processing | Custom post-processing workflows |
| 79 | MK-085 | API: External system integration | Integration with external print management systems |

## 9.9.1 Templates for Additive Operations

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 80 | MK-079 | Orientation Templates | Predefined orientation rules |
| 81 | MK-080 | Arrangement Templates | Packing strategies |
| 82 | MK-081 | Support Templates | Support structure configurations |

## 10.10.2 Mesh Inspection & Repair

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 83 | MK-086 | Mesh Inspection | Identify non-manifold geometry, holes, inverted normals |
| 84 | MK-087 | Mesh Repair | Automatic and manual repair of common mesh issues |
| 85 | MK-088 | Conversion | Convert mesh bodies to solid bodies for editing |

## Key Shortcuts & Commands Summary

_5 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 86 | MK-123 | Additive Setup | Configure printer and material \| Manufacture → Additive |
| 87 | MK-124 | Arrange | Auto-position multiple parts \| Additive → Arrange |
| 88 | MK-125 | Generate Toolpath | Slice model for printing \| Additive → Generate |
| 89 | MK-126 | Simulate Toolpath | Preview print process \| Additive → Simulate |
| 90 | MK-127 | Post Process | Generate G-code \| Simulate dialog → Post Process |

## Workflow (Detail)

_34 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 91 | MK-089 | Create/Import CAD Model |  |
| 92 | MK-090 | Design for Additive Manufacturing (DFAM) principles |  |
| 93 | MK-091 | Lightweight part design |  |
| 94 | MK-092 | Structural simulation |  |
| 95 | MK-093 | Volumetric lattice generation |  |
| 96 | MK-094 | Create Manufacturing Model (derive workflow) |  |
| 97 | MK-095 | Additive Setup |  |
| 98 | MK-096 | Select printer/machine |  |
| 99 | MK-097 | Configure print settings |  |
| 100 | MK-098 | Select material |  |
| 101 | MK-099 | Position & Orient Parts |  |
| 102 | MK-100 | Manual positioning OR |  |
| 103 | MK-101 | Automatic orientation |  |
| 104 | MK-102 | Automatic arrangement (multi-part) |  |
| 105 | MK-103 | Generate Supports (if required) |  |
| 106 | MK-104 | Select support type |  |
| 107 | MK-105 | Configure parameters |  |
| 108 | MK-106 | Manual adjustments |  |
| 109 | MK-107 | Generate Toolpath (Slice) |  |
| 110 | MK-108 | Configure layer settings |  |
| 111 | MK-109 | Set infill/perimeter parameters |  |
| 112 | MK-110 | One-click generation |  |
| 113 | MK-111 | Simulate Toolpath |  |
| 114 | MK-112 | Layer-by-layer visualization |  |
| 115 | MK-113 | Collision detection |  |
| 116 | MK-114 | Verify toolpath |  |
| 117 | MK-115 | Post-Process |  |
| 118 | MK-116 | Select post-processor |  |
| 119 | MK-117 | Configure properties |  |
| 120 | MK-118 | Generate G-code |  |
| 121 | MK-119 | EXPORT |  |
| 122 | MK-120 | Save as STL/3MF |  |
| 123 | MK-121 | Export G-code to SD card/serial |  |
| 124 | MK-122 | Or send directly to third-party slicer |  |

## Workspace & Access

_3 function points_

| # | Ref | Name | Description |
|---|-----|------|-------------|
| 125 | MK-001 | Primary Workspace | Design → Manufacture Workspace |
| 126 | MK-002 | 3D Printing Access | Manufacture tab → Additive section |
| 127 | MK-003 | Prerequisite | None (included in base Fusion 360) |

---

*End of specification — 127 function points total.*
