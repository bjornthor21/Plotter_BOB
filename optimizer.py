def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def optimize_gcode(paths):
    optimized = []
    current_pos = (0, 0)

    paths = paths.copy()

    while paths:
        best_index = min(
            range(len(paths)),
            key=lambda i: distance(current_pos, paths[i].start)
        )

        path = paths.pop(best_index)
        optimized.append(path)
        current_pos = path.end

    return optimized