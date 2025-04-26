from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import QRectF, Qt, QPointF
from core.graphics_items import MovablePoint, StretchableArrowWithHandles, DraggableText, SnapCircleItem
from utils.smith_snap import generate_smith_values
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SmithChartView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setAlignment(Qt.AlignCenter)
        self._pan = False
        self._pan_start = QPointF()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        bg_path = resource_path("resources/smith_chart_bg.png")
        if os.path.exists(bg_path):
            bg = QPixmap(bg_path)
        else:
            print("Image not found, generating Smith chart with matplotlib...")
            bg = self.generate_matplotlib_smith_chart()

        self.bg_item = QGraphicsPixmapItem(bg)
        self.scene.addItem(self.bg_item)

        rect = self.bg_item.boundingRect()
        margin = 500
        expanded_rect = rect.adjusted(-margin, -margin, margin, margin)
        self.setSceneRect(expanded_rect)

        self.fitInView(self.bg_item, Qt.KeepAspectRatio)

    def generate_matplotlib_smith_chart(self):
        fig = plt.figure(figsize=(6, 6), dpi=1000)
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        ax.set_xlim(-2, 1)
        ax.set_ylim(-2, 2)
        ax.axis('off')

        r_vals, x_vals = generate_smith_values()
        for r in r_vals:
            center = r / (1 + r)
            radius = 1 / (1 + r)
            circle = plt.Circle((center, 0), radius, fill=False, linestyle='--', color='gray', linewidth=0.8)
            ax.add_artist(circle)

        for x in x_vals:
            self._draw_reactance_arc(ax, x)
            self._draw_reactance_arc(ax, -x)

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        width, height = canvas.get_width_height()
        image = QImage(canvas.buffer_rgba(), width, height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(image)

    def _draw_reactance_arc(self, ax, x):
        center_x, center_y = 1, 1 / x
        radius = 1 / abs(x)
        circle = plt.Circle((center_x, center_y), radius=radius, fill=False, linestyle='--', color='gray', linewidth=0.8)
        ax.add_artist(circle)

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     self.fitInView(self.bg_item, Qt.KeepAspectRatio)

    def add_point(self):
        point = MovablePoint(5)
        self.scene.addItem(point)
        point.setPos(200, 200)

    def add_arrow(self):
        arrow = StretchableArrowWithHandles((100, 100), (250, 250))
        arrow.add_to_scene(self.scene)

    def add_text(self):
        text = DraggableText("Label")
        self.scene.addItem(text)
        text.setPos(300, 300)

    def add_circle(self):
        circle = SnapCircleItem()
        circle.add_to_scene(self.scene)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Zoom in or out depending on wheel direction
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Get mouse position relative to the scene
        old_pos = self.mapToScene(event.pos())

        # Zoom the view
        self.scale(zoom_factor, zoom_factor)

        # Get new position relative to the scene
        new_pos = self.mapToScene(event.pos())

        # Move view so the mouse position stays in place
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)  # Show closed hand
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            # Move scrollbars
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)  # Restore cursor
        else:
            super().mouseReleaseEvent(event)

