import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch


class SmithChart:
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.setup_chart()

    def setup_chart(self):
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1, 1.5)
        self.ax.set_ylim(-1.25, 1.25)
        self.ax.axis('off')

        # Draw constant resistance circles
        r_values = [0, 0.2, 0.5, 1, 2, 5]
        for r in r_values:
            center = r / (1 + r)
            radius = 1 / (1 + r)
            self.ax.add_patch(Circle((center, 0), radius, fill=False, linestyle='--', color='gray'))

        # Reactance arcs
        x_values = [0.2, 0.5, 1, 2, 5]
        for x in x_values:
            self._draw_reactance_arc(x)
            self._draw_reactance_arc(-x)

    def _draw_reactance_arc(self, x):
        center_x, center_y = 1, 1 / x
        radius = 1 / abs(x)
        arc = Circle((center_x, center_y), radius=radius, fill=False, linestyle='--', color='gray')
        self.ax.add_patch(arc)

    def draw_point(self, x, y):
        self.ax.plot(x, y, 'ro')

    def draw_arrow(self, start, end):
        arrow = FancyArrowPatch(start, end, arrowstyle='->', color='blue', mutation_scale=10)
        self.ax.add_patch(arrow)

    def draw_text(self, x, y, text):
        self.ax.text(x, y, text, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

    def reset(self):
        self.setup_chart()
