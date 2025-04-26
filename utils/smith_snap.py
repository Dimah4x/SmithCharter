# smith_chart_qt/utils/smith_snap.py
import numpy as np


# Smith chart geometry: circles defined in normalized reflection coefficient plane
def generate_smith_values():
    r_vals = np.concatenate([
        np.linspace(0.01, 0.2, 20, endpoint=False),
        np.linspace(0.2, 0.5, 15, endpoint=False),
        np.linspace(0.5, 1, 10, endpoint=False),
        np.linspace(1, 2, 10, endpoint=False),
        np.linspace(2, 5, 15, endpoint=False),
        np.linspace(5, 10, 10, endpoint=False),
        np.linspace(10, 20, 5)
    ])

    x_vals = r_vals.copy()  # same density for reactance arcs

    return r_vals, x_vals


r_values, x_values = generate_smith_values()


def snap_to_smith(x, y, tolerance=0.05):
    closest_point = (x, y)
    min_dist = float('inf')

    # Snap to resistance circles (center = (r/(1+r), 0), radius = 1/(1+r))
    for r in r_values:
        center = r / (1 + r), 0
        radius = 1 / (1 + r)
        dx, dy = x - center[0], y - center[1]
        dist_to_circle = abs(np.hypot(dx, dy) - radius)
        if dist_to_circle < min_dist and dist_to_circle < tolerance:
            theta = np.arctan2(dy, dx)
            new_x = center[0] + radius * np.cos(theta)
            new_y = center[1] + radius * np.sin(theta)
            closest_point = (new_x, new_y)
            min_dist = dist_to_circle

    # Snap to reactance arcs (center = (1, ±1/x), radius = 1/|x|)
    for xval in x_values:
        for sign in [+1, -1]:
            cx, cy = 1, sign * 1 / xval
            r = 1 / abs(xval)
            dx, dy = x - cx, y - cy
            dist_to_arc = abs(np.hypot(dx, dy) - r)
            if dist_to_arc < min_dist and dist_to_arc < tolerance:
                theta = np.arctan2(dy, dx)
                new_x = cx + r * np.cos(theta)
                new_y = cy + r * np.sin(theta)
                closest_point = (new_x, new_y)
                min_dist = dist_to_arc

    return closest_point
