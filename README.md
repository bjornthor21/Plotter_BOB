# Plotter BOB — DXF to G-code Converter

Plotter BOB is a desktop application for converting DXF technical drawings into G-code suitable for pen plotters and similar CNC-style drawing machines.

The application acts as a lightweight **slicer for technical drawings**. It reads geometry from a DXF file, converts drawing entities into internal toolpaths, optionally optimizes the drawing order to reduce unnecessary travel, previews the resulting paths, and exports the final result as G-code.

## Features

- Import DXF drawings
- Convert DXF entities into plotter toolpaths
- Interactive toolpath preview
- Zoom and pan using PyQtGraph
- Display drawing paths and pen-up travel moves
- Nearest-neighbor path optimization to reduce travel distance
- Enable or disable:
  - Text
  - MTEXT
  - Dimensions
  - Drawing borders
  - Title blocks
- Support for DXF entities including:
  - LINE
  - CIRCLE
  - ARC
  - ELLIPSE
  - LWPOLYLINE
  - POLYLINE
  - SPLINE
  - TEXT
  - MTEXT
  - DIMENSION
  - SOLID
  - INSERT
  - ATTRIB
- Conversion of text and dimension labels into drawable vector paths
- Support for common DXF formatting symbols such as:
  - Diameter (`∅`)
  - Degree (`°`)
  - Plus/minus (`±`)
- Export generated G-code
- Save G-code using a standard file dialog
- Standalone Windows executable

## How It Works

Plotter BOB uses an intermediate toolpath representation instead of converting DXF entities directly into G-code.

```text
DXF File
    │
    ▼
DXF Entity Parsing
    │
    ▼
PlotPath Generation
    │
    ▼
Path Optimization
    │
    ├──────────────► Toolpath Preview
    │
    ▼
G-code Generation
    │
    ▼
.gcode File
