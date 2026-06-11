from datetime import date, datetime, time, timedelta

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget

from database import Schedule


def day_fraction(now: datetime | None = None) -> float:
    now = now or datetime.now()
    elapsed = now.hour * 3600 + now.minute * 60 + now.second
    return max(0.0, min(1.0, elapsed / 86400))


def schedule_span_on_day(schedule: Schedule, day: date) -> tuple[float, float] | None:
    day_start = datetime.combine(day, time.min)
    day_end = day_start + timedelta(days=1)
    start = max(schedule.start_time, day_start)
    end = min(schedule.end_time, day_end)
    if end <= start:
        return None
    start_frac = (start - day_start).total_seconds() / 86400
    end_frac = (end - day_start).total_seconds() / 86400
    return start_frac, end_frac


class TimeFlowBar(QWidget):
    def __init__(self, day: date, parent: QWidget | None = None):
        super().__init__(parent)
        self.day = day
        self._schedules: list[Schedule] = []
        self.setFixedHeight(14)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip("Current time flow through the day")

    def set_schedules(self, schedules: list[Schedule]) -> None:
        self._schedules = schedules
        self.update()

    def update_flow(self) -> None:
        now = datetime.now()
        self.setToolTip(f"Now {now.strftime('%H:%M')} · day progress {int(day_fraction(now) * 100)}%")
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 1
        track = QRectF(margin, h * 0.35, w - margin * 2, h * 0.3)
        radius = track.height() / 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1a1f28"))
        painter.drawRoundedRect(track, radius, radius)

        for schedule in self._schedules:
            span = schedule_span_on_day(schedule, self.day)
            if not span:
                continue
            x1 = track.left() + track.width() * span[0]
            x2 = track.left() + track.width() * span[1]
            seg = QRectF(x1, track.top(), max(x2 - x1, 3), track.height())
            painter.setBrush(QColor(79, 140, 255, 90))
            painter.drawRoundedRect(seg, 2, 2)

        progress = day_fraction()
        flow_end = track.left() + track.width() * progress
        if progress > 0:
            flow_rect = QRectF(track.left(), track.top(), flow_end - track.left(), track.height())
            gradient = QLinearGradient(flow_rect.left(), 0, flow_rect.right(), 0)
            gradient.setColorAt(0.0, QColor("#3d78e8"))
            gradient.setColorAt(0.55, QColor("#6c9eff"))
            gradient.setColorAt(1.0, QColor("#a78bfa"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(flow_rect, radius, radius)

        marker_x = track.left() + track.width() * progress
        marker_y = h / 2
        glow = QPainterPath()
        glow.addEllipse(marker_x - 5, marker_y - 5, 10, 10)
        painter.setBrush(QColor(108, 158, 255, 70))
        painter.drawPath(glow)

        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#4f8cff"), 1.5))
        painter.drawEllipse(int(marker_x - 3), int(marker_y - 3), 6, 6)

        painter.end()


class DayTimeline(QWidget):
    """Vertical time flow for the day detail panel when viewing today."""

    def __init__(self, day: date, parent: QWidget | None = None):
        super().__init__(parent)
        self.day = day
        self._schedules: list[Schedule] = []
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_schedules(self, schedules: list[Schedule]) -> None:
        self._schedules = schedules
        self.update()

    def update_flow(self) -> None:
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        track_x = 18
        track_w = 4
        track = QRectF(track_x, 8, track_w, h - 16)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2a2f38"))
        painter.drawRoundedRect(track, 2, 2)

        progress = day_fraction()
        flow_h = track.height() * progress
        if flow_h > 0:
            flow_rect = QRectF(track.left(), track.top(), track.width(), flow_h)
            gradient = QLinearGradient(0, flow_rect.top(), 0, flow_rect.bottom())
            gradient.setColorAt(0.0, QColor("#3d78e8"))
            gradient.setColorAt(1.0, QColor("#a78bfa"))
            painter.setBrush(gradient)
            painter.drawRoundedRect(flow_rect, 2, 2)

        for schedule in self._schedules:
            span = schedule_span_on_day(schedule, self.day)
            if not span:
                continue
            y1 = track.top() + track.height() * span[0]
            y2 = track.top() + track.height() * span[1]
            seg = QRectF(track.right() + 6, y1, w - track.right() - 12, max(y2 - y1, 4))
            painter.setBrush(QColor(79, 140, 255, 60))
            painter.setPen(QPen(QColor("#4f8cff"), 1))
            painter.drawRoundedRect(seg, 3, 3)

        marker_y = track.top() + track.height() * progress
        painter.setPen(QPen(QColor("#6c9eff"), 2))
        painter.drawLine(int(track.right() + 2), int(marker_y), w - 8, int(marker_y))
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#4f8cff"), 1.5))
        painter.drawEllipse(int(track_x + track_w / 2 - 4), int(marker_y - 4), 8, 8)

        now = datetime.now()
        painter.setPen(QColor("#6c9eff"))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(w - 52, int(marker_y + 4), now.strftime("%H:%M"))

        painter.end()
