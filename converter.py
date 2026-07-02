import math
import numpy as np
from matplotlib.textpath import TextPath
import ezdxf
from ezdxf.math import Vec3
from paths import PlotPath
from gcode import *
from optimizer import optimize_paths

def transform_point(x, y, insert, rotation_deg):
    a = math.radians(rotation_deg)

    xr = x * math.cos(a) - y * math.sin(a)
    yr = x * math.sin(a) + y * math.cos(a)

    return Vec3(insert.x + xr, insert.y + yr, 0)

def make_path(points, source_type="", layer=""):
    if not points or len(points) < 2:
        return []
    return [PlotPath(points, source_type, layer)]

def line_to_paths(e):
    return [
        PlotPath(
            points=[
                e.dxf.start,
                e.dxf.end,
            ],
            source_type="LINE",
            layer=e.dxf.layer,
        )
    ]

def circle_to_paths(e, segments=80):
    center = e.dxf.center
    radius = e.dxf.radius

    points = []

    for i in range(segments + 1):
        ang = 2 * math.pi * i / segments
        x = center.x + radius * math.cos(ang)
        y = center.y + radius * math.sin(ang)
        points.append(Vec3(x, y, 0))

    return make_path(points, e)

def ellipse_to_paths(e, segments=80):
    params = np.linspace(
        e.dxf.start_param,
        e.dxf.end_param,
        segments + 1,
    )

    points = list(e.vertices(params))

    return [
        PlotPath(
            points=points,
            source_type="ELLIPSE",
            layer=e.dxf.layer,
        )
    ]

def arc_to_paths(e, segments=40):
    center = e.dxf.center
    r = e.dxf.radius

    start = math.radians(e.dxf.start_angle)
    end = math.radians(e.dxf.end_angle)

    if end < start:
        end += 2 * math.pi

    points = []

    for i in range(segments + 1):
        a = start + (end - start) * i / segments
        x = center.x + r * math.cos(a)
        y = center.y + r * math.sin(a)
        points.append(type(center)(x, y, 0))

    return make_path(points, e)

def lwpolyline_to_paths(e):
    points = []

    for p in e.get_points():
        x = p[0]
        y = p[1]
        points.append(type(e.dxf.elevation)(x, y, 0))

    if e.closed:
        points.append(points[0])

    return make_path(points, e)

def polyline_to_paths(e):
    points = []

    for vertex in e.vertices:
        points.append(vertex.dxf.location)

    if e.is_closed:
        points.append(points[0])

    return make_path(points, e)

def spline_to_paths(e, segments=100):
    points = list(e.flattening(distance=0.1, segments=segments))
    return make_path(points, e)

def text_to_paths(e):
    text = clean_dxf_text(e.dxf.text)
    insert = e.dxf.insert
    height = e.dxf.height

    if e.dxf.hasattr("text_direction"):
        d = e.dxf.text_direction
        rotation = math.degrees(math.atan2(d.y, d.x))
    else:
        rotation = e.dxf.rotation if e.dxf.hasattr("rotation") else 0

    tp = TextPath((0, 0), text, size=height)

    g = []

    for poly in tp.to_polygons():
        points = [
            transform_point(x, y, insert, rotation)
            for x, y in poly
        ]

        if len(points) > 1:
            g += make_path(points, e)

    return g

def clean_dxf_text(text: str) -> str:
    """Convert common DXF formatting codes to plain Unicode."""

    replacements = {
        "%%c": "⌀",        # Diameter symbol
        "%%C": "⌀",
        "%%d": "°",        # Degree
        "%%D": "°",
        "%%p": "±",        # Plus/minus
        "%%P": "±",
        "\\P": "\n",       # New paragraph
        "\\~": " ",        # Non-breaking space
        "\\U+2205": "∅",   # Diameter (Unicode)
        "\\U+2300": "⌀",   # Diameter symbol
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

def apply_mtext_alignment(polys, attachment_point):
    xs = [x for poly in polys for x, y in poly]
    ys = [y for poly in polys for x, y in poly]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    if attachment_point in [2, 5, 8]:  # center X
        shift_x = -(min_x + max_x) / 2
    elif attachment_point in [3, 6, 9]:  # right
        shift_x = -max_x
    else:  # left
        shift_x = -min_x

    if attachment_point in [1, 2, 3]:  # top
        shift_y = -max_y
    elif attachment_point in [4, 5, 6]:  # middle
        #shift_y = -(min_y + max_y) / 2
        pass
    else:  # bottom
        shift_y = -min_y

    return [[(x + shift_x, y + shift_y) for x, y in poly] for poly in polys]

def mtext_to_paths(e):
    text = clean_dxf_text(e.plain_text())
    #text = e.plain_text()
    insert = e.dxf.insert
    height = e.dxf.char_height
    rotation = e.dxf.rotation if e.dxf.hasattr("rotation") else 0
    attachment = e.dxf.attachment_point if e.dxf.hasattr("attachment_point") else 1

    line_spacing = height * 1.4 * e.dxf.get("line_spacing_factor", 1.0)

    all_polys = []

    for line_index, line in enumerate(text.splitlines()):
        local_y = -line_index * line_spacing
        tp = TextPath((0, local_y), line, size=height)
        line_polys = tp.to_polygons()

        xs = [x for poly in line_polys for x, y in poly]
        if xs:
            min_x, max_x = min(xs), max(xs)

            if attachment in [2, 5, 8]:      # center
                shift_x = -(min_x + max_x) / 2
            elif attachment in [3, 6, 9]:    # right
                shift_x = -max_x
            else:                            # left
                shift_x = -min_x

            line_polys = [
                [(x + shift_x, y) for x, y in poly]
                for poly in line_polys
            ]

        all_polys.extend(line_polys)

    if not all_polys:
        return []

    ys = [y for poly in all_polys for x, y in poly]
    min_y, max_y = min(ys), max(ys)

    if attachment in [1, 2, 3]:      # top
        shift_y = -max_y
    elif attachment in [4, 5, 6]:    # middle
        shift_y = -(min_y + max_y) / 2
    else:                            # bottom
        shift_y = -min_y

    all_polys = [
        [(x, y + shift_y) for x, y in poly]
        for poly in all_polys
    ]

    g = []
    for poly in all_polys:
        points = [transform_point(x, y, insert, rotation) for x, y in poly]
        if len(points) > 1:
            g += make_path(points, e)

    return g

def solid_to_paths(e):
    points = []
    
    for name in ["vtx0", "vtx1", "vtx2", "vtx3"]:
        if e.dxf.hasattr(name):
            points.append(e.dxf.get(name))

    if len(points) >= 3:
        points.append(points[0])
        return make_path(points, e)

    return []

def align_dimension_text(polys):
    if not polys:
        return polys

    xs = [x for poly in polys for x, y in poly]
    ys = [y for poly in polys for x, y in poly]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # attachment_point 1 = top-left
    shift_x = -min_x
    shift_y = -max_y

    return [
        [(x + shift_x, y + shift_y) for x, y in poly]
        for poly in polys
    ]

def dimension_mtext_to_paths(e):
    raw = e.text
    text = e.plain_text()

    # Inventor/AIGDT diameter symbol issue:
    # raw has \fAIGDT ... \ln, but plain_text() turns it into "n"
    if "\\fAIGDT" in raw and "\\ln" in raw and text.startswith("n"):
        text = "∅" + text[1:]

    text = clean_dxf_text(text)
    height = e.dxf.char_height
    DIM_TEXT_Y_OFFSET = -0.10 * height
    insert = Vec3(e.dxf.insert.x, e.dxf.insert.y + DIM_TEXT_Y_OFFSET, 0)

    if e.dxf.hasattr("text_direction"):
        d = e.dxf.text_direction
        rotation = math.degrees(math.atan2(d.y, d.x))
    else:
        rotation = e.dxf.rotation if e.dxf.hasattr("rotation") else 0


    tp = TextPath((0, 0), text, size=height)
    polys = tp.to_polygons()
    polys = align_dimension_text(polys)

    g = []
    for poly in polys:
        points = [transform_point(x, y, insert, rotation) for x, y in poly]
        if len(points) > 1:
            g += make_path(points, e)

    return g

def attrib_to_paths(e):
    text = clean_dxf_text(e.dxf.text)

    if not text.strip():
        return []

    insert = e.dxf.insert
    height = e.dxf.height
    rotation = e.dxf.rotation if e.dxf.hasattr("rotation") else 0

    tp = TextPath((0, 0), text, size=height)

    g = []
    for poly in tp.to_polygons():
        points = [transform_point(x, y, insert, rotation) for x, y in poly]
        if len(points) > 1:
            g += make_path(points, e)

    return g

def entity_to_paths(e, settings):
    match e.dxftype():
        case "LINE":
            return line_to_paths(e)

        case "CIRCLE":
            return circle_to_paths(e)

        case "ELLIPSE":
            return ellipse_to_paths(e)

        case "ARC":
            return arc_to_paths(e)

        case "LWPOLYLINE":
            return lwpolyline_to_paths(e)

        case "POLYLINE":
            return polyline_to_paths(e)

        case "SPLINE":
            return spline_to_paths(e)

        case "TEXT":
            if not settings.draw_text:
                return []
            return text_to_paths(e)

        case "MTEXT":
            if not settings.draw_mtext:
                return []
            return mtext_to_paths(e)

        case "DIMENSION":
            if not settings.draw_dimensions:
                return []

            paths = []
            for ve in e.virtual_entities():
                if ve.dxftype() == "MTEXT":
                    paths += dimension_mtext_to_paths(ve)
                else:
                    paths += entity_to_paths(ve, settings)
            return paths

        case "SOLID":
            return solid_to_paths(e)

        case "INSERT":
            name = e.dxf.name

            if "Border" in name and not settings.draw_border:
                return []

            if "Title Blocks" in name and not settings.draw_title_block:
                return []

            paths = []

            try:
                for ve in e.virtual_entities():
                    paths += entity_to_paths(ve, settings)

                for attrib in e.attribs:
                    paths += attrib_to_paths(attrib)

            except Exception as err:
                print(f"Could not render INSERT '{name}': {err}")

            return paths

        case "ATTRIB":
            if not settings.draw_text:
                return []
            return attrib_to_paths(e)

        case "ATTDEF":
            if not settings.draw_text:
                return []
            return text_to_paths(e)

        case "POINT":
            return []

        case _:
            print(f"Unknown entity type: {e.dxftype()}")
            return []
        
def convert_dxf(input_file, output_file, settings):
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()

    paths = []

    for e in msp:
        paths += entity_to_paths(e, settings)

    if settings.optimize_paths:
        paths = optimize_paths(paths)

    gcode = paths_to_gcode(paths, settings)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(gcode))

    return gcode, paths