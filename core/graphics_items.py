from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QGraphicsItem, QMenu,
    QGraphicsScene, QGraphicsView,
    QGraphicsSimpleTextItem, QColorDialog
)
from PyQt5.QtGui import QBrush, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QTimer, QRectF
from utils.smith_snap import snap_to_smith
import numpy as np

class MovablePoint(QGraphicsEllipseItem):
    def __init__(self, radius):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable)
        self.label = QGraphicsSimpleTextItem("")
        self.label.setParentItem(self)
        self.label.setBrush(QBrush(Qt.darkBlue))
        self.label.setZValue(1)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        color_action = menu.addAction("Change Color")
        selected = menu.exec_(event.screenPos())

        if selected == delete_action:
            self.scene().removeItem(self)
        elif selected == color_action:
            color = QColorDialog.getColor()
            if color.isValid():
                self.setBrush(QBrush(color))

class DraggableText(QGraphicsTextItem):
    def __init__(self, text):
        super().__init__(text)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFlags(
            QGraphicsTextItem.ItemIsMovable |
            QGraphicsTextItem.ItemIsSelectable |
            QGraphicsTextItem.ItemIsFocusable
        )

        self.default_font_size = 16
        self.min_font_size = 8

        font = QFont()
        font.setPointSize(self.default_font_size)
        self.setFont(font)

        self.resize_handle_size = 10
        self.resizing = False

        self.base_width = 150
        self.setTextWidth(self.base_width)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.isSelected():
            rect = self.boundingRect()
            handle_rect = QRectF(
                rect.right() - self.resize_handle_size,
                rect.bottom() - self.resize_handle_size,
                self.resize_handle_size,
                self.resize_handle_size
            )
            painter.setBrush(Qt.gray)
            painter.drawRect(handle_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = self.boundingRect()
            handle_rect = QRectF(
                rect.right() - self.resize_handle_size,
                rect.bottom() - self.resize_handle_size,
                self.resize_handle_size,
                self.resize_handle_size
            )
            if handle_rect.contains(event.pos()):
                self.resizing = True
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            # delta_x controls width
            delta_x = max(30, event.pos().x())
            delta_y = max(20, event.pos().y())

            # Update text width first
            self.setTextWidth(delta_x)

            # Scale font size based on width scaling
            scale_ratio = delta_x / self.base_width
            new_font_size = max(self.min_font_size, self.default_font_size * scale_ratio)

            font = self.font()
            font.setPointSizeF(new_font_size)
            self.setFont(font)

            self.update()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.resizing:
            self.resizing = False
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        color_action = menu.addAction("Change Color")
        selected = menu.exec_(event.screenPos())

        if selected == delete_action:
            self.scene().removeItem(self)
        elif selected == color_action:
            color = QColorDialog.getColor()
            if color.isValid():
                self.setDefaultTextColor(color)


class StretchHandle(QGraphicsEllipseItem):
    def __init__(self, parent_object, which_end):
        super().__init__(-5, -5, 10, 10)
        self.setBrush(QBrush(Qt.green))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)
        self.parent_object = parent_object
        self.which_end = which_end

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.which_end == 'center':
                from utils.smith_snap import snap_to_smith
                snap_x, snap_y = snap_to_smith(value.x(), value.y())
                snapped = QPointF(snap_x, snap_y)

                if hasattr(self.parent_object, 'move_radius_with_center'):
                    if hasattr(self.parent_object, 'radius_handle') and self.parent_object.radius_handle is not None:
                        delta = snapped - self.pos()
                        self.parent_object.move_radius_with_center(delta)

                return snapped

            elif self.which_end == 'radius':
                from utils.smith_snap import snap_to_smith
                snap_x, snap_y = snap_to_smith(value.x(), value.y())
                snapped = QPointF(snap_x, snap_y)

                if hasattr(self.parent_object, 'update_circle'):
                    self.parent_object.update_circle()

                return snapped

            elif self.which_end in ['start', 'end']:
                from utils.smith_snap import snap_to_smith
                snap_x, snap_y = snap_to_smith(value.x(), value.y())
                snapped = QPointF(snap_x, snap_y)

                if hasattr(self.parent_object, 'update_line'):
                    self.parent_object.update_line(self.which_end, snapped)

                return snapped

        return super().itemChange(change, value)


class StretchableArrowWithHandles(QGraphicsLineItem):
    def __init__(self, start, end):
        super().__init__(*start, *end)
        self.setPen(QPen(Qt.blue, 2))
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsScenePositionChanges |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        self.start_handle = StretchHandle(self, 'start')
        self.end_handle = StretchHandle(self, 'end')

        self.start_handle.setPos(QPointF(*start))
        self.end_handle.setPos(QPointF(*end))

        # Initially hide handles
        self.start_handle.setVisible(False)
        self.end_handle.setVisible(False)

    def add_to_scene(self, scene):
        scene.addItem(self)
        scene.addItem(self.start_handle)
        scene.addItem(self.end_handle)

    def update_line(self, which, pos):
        if which == 'start':
            self.setLine(pos.x(), pos.y(), self.line().x2(), self.line().y2())
        elif which == 'end':
            self.setLine(self.line().x1(), self.line().y1(), pos.x(), pos.y())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            selected = bool(value)
            self.start_handle.setVisible(selected)
            self.end_handle.setVisible(selected)
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        color_action = menu.addAction("Change Color")
        selected = menu.exec_(event.screenPos())

        if selected == delete_action:
            scene = self.scene()
            scene.removeItem(self)
            scene.removeItem(self.start_handle)
            scene.removeItem(self.end_handle)
        elif selected == color_action:
            color = QColorDialog.getColor()
            if color.isValid():
                self.setPen(QPen(color, 2))


class SnapCircleItem(QGraphicsEllipseItem):
    def __init__(self):
        super().__init__()
        self.setPen(QPen(Qt.darkMagenta, 2))
        self.setBrush(QBrush(QColor(255, 255, 255, 0)))
        self.setFlags(QGraphicsItem.ItemIsSelectable)

        self.true_radius = 50
        self.unit_vector = QPointF(1, 0)

        self.center_handle = None
        self.radius_handle = None

        self.label = QGraphicsSimpleTextItem("", self)
        self.label.setBrush(QBrush(Qt.darkBlue))
        self.label.setZValue(1)

    def add_to_scene(self, scene):
        self.center_handle = StretchHandle(self, 'center')
        self.radius_handle = StretchHandle(self, 'radius')

        self.center_handle.setPos(QPointF(200, 200))
        self.radius_handle.setPos(QPointF(250, 200))

        scene.addItem(self)
        scene.addItem(self.center_handle)
        scene.addItem(self.radius_handle)

        self.update_circle()

    def move_radius_with_center(self, delta):
        if self.center_handle and self.radius_handle:
            self.radius_handle.setPos(self.radius_handle.pos() + delta)
            self.update_circle()

    def update_circle(self):
        if not (self.center_handle and self.radius_handle):
            return

        c = self.center_handle.pos()
        r = self.radius_handle.pos()

        dx = r.x() - c.x()
        dy = r.y() - c.y()
        radius = np.hypot(dx, dy)

        self.setRect(c.x() - radius, c.y() - radius, 2 * radius, 2 * radius)

        # Update label
        if abs(c.y()) < 0.1:
            r_val = c.x() / (1 - c.x()) if (1 - c.x()) != 0 else 0
            label = f"r = {r_val:.2f}" if r_val >= 0 else ""
        elif abs(c.x() - 1) < 0.1:
            x_val = 1 / abs(c.y()) if c.y() != 0 else 0
            sign = '+' if c.y() > 0 else '-'
            label = f"x = {sign}{x_val:.2f}"
        else:
            label = ""

        self.label.setText(label)
        self.label.setPos(c.x() + radius * 1.1, c.y())

    def move_center(self, new_center_pos):
        if self.center_handle and self.radius_handle:
            old_center_pos = self.center_handle.pos()
            delta = new_center_pos - old_center_pos

            self.center_handle.setPos(new_center_pos)
            new_radius_pos = self.radius_handle.pos() + delta
            self.radius_handle.setPos(new_radius_pos)

            self.update_circle()

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        color_action = menu.addAction("Change Color")
        selected = menu.exec_(event.screenPos())

        if selected == delete_action:
            scene = self.scene()
            scene.removeItem(self)
            if self.center_handle:
                scene.removeItem(self.center_handle)
            if self.radius_handle:
                scene.removeItem(self.radius_handle)
        elif selected == color_action:
            color = QColorDialog.getColor()
            if color.isValid():
                self.setPen(QPen(color, 2))
