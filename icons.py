from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def _make_icon(drawer, size: int = 20) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    drawer(painter, size)
    painter.end()
    icon = QIcon(pixmap)
    icon.addPixmap(pixmap, QIcon.Mode.Normal, QIcon.State.Off)
    return icon


def _draw_trash(painter: QPainter, size: int, color: QColor) -> None:
    s = size
    pen = QPen(color, 1.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    lid_y = s * 0.28
    painter.drawLine(int(s * 0.32), int(lid_y), int(s * 0.68), int(lid_y))
    painter.drawLine(int(s * 0.42), int(lid_y - 3), int(s * 0.58), int(lid_y - 3))

    body = QPainterPath()
    body.addRoundedRect(s * 0.34, lid_y + 1, s * 0.32, s * 0.46, 2, 2)
    painter.drawPath(body)

    painter.drawLine(int(s * 0.44), int(lid_y + 5), int(s * 0.44), int(s * 0.66))
    painter.drawLine(int(s * 0.50), int(lid_y + 5), int(s * 0.50), int(s * 0.66))
    painter.drawLine(int(s * 0.56), int(lid_y + 5), int(s * 0.56), int(s * 0.66))


def _draw_bell(painter: QPainter, size: int, color: QColor, muted: bool = False) -> None:
    s = size
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)

    bell = QPainterPath()
    bell.moveTo(s * 0.50, s * 0.18)
    bell.cubicTo(s * 0.68, s * 0.18, s * 0.72, s * 0.42, s * 0.72, s * 0.58)
    bell.lineTo(s * 0.78, s * 0.66)
    bell.lineTo(s * 0.22, s * 0.66)
    bell.lineTo(s * 0.28, s * 0.58)
    bell.cubicTo(s * 0.28, s * 0.42, s * 0.32, s * 0.18, s * 0.50, s * 0.18)
    painter.drawPath(bell)

    painter.drawEllipse(int(s * 0.44), int(s * 0.70), int(s * 0.12), int(s * 0.10))

    if muted:
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(int(s * 0.26), int(s * 0.26), int(s * 0.74), int(s * 0.74))


def delete_icon(size: int = 18) -> QIcon:
    return _make_icon(lambda p, s: _draw_trash(p, s, QColor("#f07178")), size)


def notify_on_icon(size: int = 18) -> QIcon:
    return _make_icon(lambda p, s: _draw_bell(p, s, QColor("#7fd99a"), muted=False), size)


def notify_off_icon(size: int = 18) -> QIcon:
    return _make_icon(lambda p, s: _draw_bell(p, s, QColor("#6b7280"), muted=True), size)
