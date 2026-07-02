def pen_up():
    return "M5"

def pen_down():
    return "M3 S1000"

def path_to_gcode(path, settings):
    points = path.points

    g = [
        f"G0 X{points[0].x:.3f} Y{points[0].y:.3f}",
        pen_down(),
    ]

    for p in points[1:]:
        g.append(f"G1 X{p.x:.3f} Y{p.y:.3f} F{settings.feed}")

    g.append(pen_up())
    return g


def paths_to_gcode(paths, settings):
    gcode = [
        "G21",
        "G90",
        pen_up(),
    ]

    for path in paths:
        gcode += path_to_gcode(path, settings)

    gcode += [pen_up(), "M2"]
    return gcode