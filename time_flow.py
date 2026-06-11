from datetime import date, datetime, time, timedelta

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

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
        margin = 2
        track_h = max(4.0, h * 0.45)
        track_y = (h - track_h) / 2
        track = QRectF(margin, track_y, w - margin * 2, track_h)
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
        marker_r = max(3.0, h * 0.22)
        glow_r = marker_r + 2
        glow = QPainterPath()
        glow.addEllipse(marker_x - glow_r, marker_y - glow_r, glow_r * 2, glow_r * 2)
        painter.setBrush(QColor(108, 158, 255, 70))
        painter.drawPath(glow)

        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#4f8cff"), 1.5))
        painter.drawEllipse(
            int(marker_x - marker_r), int(marker_y - marker_r),
            int(marker_r * 2), int(marker_r * 2),
        )

        painter.end()


class SidebarTimeFlow(QWidget):
    """Horizontal time-of-day bar for the day detail sidebar."""

    def __init__(self, day: date, parent: QWidget | None = None):
        super().__init__(parent)
        self.day = day
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._bar = TimeFlowBar(day)
        self._bar.setFixedHeight(22)
        layout.addWidget(self._bar, 1)

        self._time_label = QLabel()
        self._time_label.setObjectName("SidebarTimeNow")
        self._time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._time_label)

        self.update_flow()

    def set_schedules(self, schedules: list[Schedule]) -> None:
        self._bar.set_schedules(schedules)

    def update_flow(self) -> None:
        now = datetime.now()
        self._time_label.setText(now.strftime("%H:%M"))
        self._bar.update_flow()
