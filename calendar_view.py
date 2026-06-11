import calendar
from datetime import date, datetime

from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from completion import (
    apply_calendar_pill_style,
    apply_schedule_card_style,
    display_status_label,
    populate_status_combo,
)
from database import (
    Schedule,
    auto_mark_incomplete,
    delete_schedule,
    set_completion_status,
    toggle_notification,
)
from icons import delete_icon, notify_off_icon, notify_on_icon
from time_flow import DayTimeline, TimeFlowBar


WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MAX_EVENTS_PER_CELL = 2


def schedules_for_date(schedules: list[Schedule], day: date) -> list[Schedule]:
    matched = [
        s for s in schedules
        if s.start_time.date() <= day <= s.end_time.date()
    ]
    return sorted(matched, key=lambda s: s.start_time)


class DayCell(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, day: date, parent: QWidget | None = None):
        super().__init__(parent)
        self.day = day
        self._selected = False
        self._is_today = False
        self.time_flow: TimeFlowBar | None = None
        self.setObjectName("DayCell")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(3)

        self.day_label = QLabel(str(day.day))
        self.day_label.setObjectName("DayNumber")
        layout.addWidget(self.day_label)

        self.events_layout = QVBoxLayout()
        self.events_layout.setSpacing(2)
        layout.addLayout(self.events_layout)
        layout.addStretch()

        self.time_flow = TimeFlowBar(day)
        self.time_flow.hide()
        layout.addWidget(self.time_flow)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_today(self, today: bool) -> None:
        self._is_today = today
        self.setProperty("today", today)
        if self.time_flow:
            self.time_flow.setVisible(today)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_other_month(self, other: bool) -> None:
        self.setProperty("otherMonth", other)
        self.style().unpolish(self)
        self.style().polish(self)

    def populate(self, schedules: list[Schedule]) -> None:
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for schedule in schedules[:MAX_EVENTS_PER_CELL]:
            pill = QLabel(f"{schedule.start_time.strftime('%H:%M')} {schedule.title}")
            pill.setObjectName("EventPill")
            apply_calendar_pill_style(pill, schedule)
            pill.setToolTip(
                f"{schedule.title}\n"
                f"{schedule.start_time.strftime('%H:%M')} – "
                f"{schedule.end_time.strftime('%H:%M')}\n"
                f"Status: {display_status_label(schedule)}"
            )
            font = QFont()
            font.setPointSize(9)
            pill.setFont(font)
            self.events_layout.addWidget(pill)

        if len(schedules) > MAX_EVENTS_PER_CELL:
            more = QLabel(f"+{len(schedules) - MAX_EVENTS_PER_CELL} more")
            more.setObjectName("MoreEvents")
            self.events_layout.addWidget(more)

        if self.time_flow and self._is_today:
            self.time_flow.set_schedules(schedules)

    def update_time_flow(self) -> None:
        if self.time_flow and self._is_today:
            self.time_flow.update_flow()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day)
        super().mousePressEvent(event)


class CalendarWidget(QFrame):
    day_selected = pyqtSignal(object)
    time_flow_tick = pyqtSignal()
    schedules_updated = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._year = datetime.now().year
        self._month = datetime.now().month
        self._selected_day = datetime.now().date()
        self._schedules: list[Schedule] = []
        self._cells: dict[date, DayCell] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("‹")
        self.prev_btn.setObjectName("NavButton")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._prev_month)

        self.month_label = QLabel()
        self.month_label.setObjectName("CalendarMonth")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("›")
        self.next_btn.setObjectName("NavButton")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._next_month)

        today_btn = QPushButton("Today")
        today_btn.setObjectName("GhostButton")
        today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        today_btn.clicked.connect(self._go_today)

        nav.addWidget(self.prev_btn)
        nav.addWidget(self.month_label, 1)
        nav.addWidget(self.next_btn)
        nav.addWidget(today_btn)
        root.addLayout(nav)

        weekday_row = QGridLayout()
        weekday_row.setSpacing(4)
        for col, name in enumerate(WEEKDAYS):
            label = QLabel(name)
            label.setObjectName("WeekdayHeader")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_row.addWidget(label, 0, col)
        root.addLayout(weekday_row)

        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        root.addLayout(self.grid, 1)

        self._build_grid()

        self._flow_timer = QTimer(self)
        self._flow_timer.setInterval(30_000)
        self._flow_timer.timeout.connect(self._update_time_flows)
        self._flow_timer.start()

    def _update_time_flows(self) -> None:
        if auto_mark_incomplete() > 0:
            self.schedules_updated.emit()
        today = datetime.now().date()
        for day, cell in self._cells.items():
            if day == today:
                cell.update_time_flow()
        self.time_flow_tick.emit()

    def _build_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cells.clear()

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        weeks = cal.monthdatescalendar(self._year, self._month)
        today = datetime.now().date()

        for row, week in enumerate(weeks):
            for col, day in enumerate(week):
                cell = DayCell(day)
                cell.set_other_month(day.month != self._month)
                cell.set_today(day == today)
                cell.set_selected(day == self._selected_day)
                cell.clicked.connect(self._on_day_clicked)
                self._cells[day] = cell
                self.grid.addWidget(cell, row, col)

        self.month_label.setText(f"{calendar.month_name[self._month]} {self._year}")
        self._update_time_flows()

    def _on_day_clicked(self, day: date) -> None:
        self._selected_day = day
        for d, cell in self._cells.items():
            cell.set_selected(d == day)
        self.day_selected.emit(day)

    def _prev_month(self) -> None:
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self._build_grid()
        self.refresh(self._schedules)

    def _next_month(self) -> None:
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self._build_grid()
        self.refresh(self._schedules)

    def _go_today(self) -> None:
        today = datetime.now().date()
        self._year = today.year
        self._month = today.month
        self._selected_day = today
        self._build_grid()
        self.refresh(self._schedules)
        self.day_selected.emit(today)

    def selected_date(self) -> date:
        return self._selected_day

    def refresh(self, schedules: list[Schedule]) -> None:
        self._schedules = schedules
        for day, cell in self._cells.items():
            cell.populate(schedules_for_date(schedules, day))
            cell.set_selected(day == self._selected_day)


class ScheduleCard(QFrame):
    double_clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    notify_toggled = pyqtSignal(int, bool)
    completion_changed = pyqtSignal(int)

    def __init__(self, schedule: Schedule, parent: QWidget | None = None):
        super().__init__(parent)
        self.schedule = schedule
        self.setObjectName("ScheduleCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_schedule_card_style(self, schedule)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        time_text = QLabel(
            f"{schedule.start_time.strftime('%H:%M')} – "
            f"{schedule.end_time.strftime('%H:%M')}"
        )
        time_text.setObjectName("ScheduleTime")
        top.addWidget(time_text, 1)

        self.notify_btn = QPushButton()
        self.notify_btn.setObjectName("IconToggleButton")
        self.notify_btn.setProperty("schedule_id", schedule.id)
        self._update_notify_btn(schedule.notification_enabled)
        self.notify_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notify_btn.clicked.connect(self._on_notify)
        top.addWidget(self.notify_btn)

        delete_btn = QPushButton()
        delete_btn.setObjectName("IconDangerButton")
        delete_btn.setIcon(delete_icon())
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setToolTip("Delete schedule")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(
            lambda: self.delete_requested.emit(schedule.id)
        )
        top.addWidget(delete_btn)
        root.addLayout(top)

        title = QLabel(schedule.title)
        title.setObjectName("ScheduleCardTitle")
        title.setWordWrap(True)
        root.addWidget(title)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_caption = QLabel("Status:")
        status_caption.setObjectName("ScheduleCardPreview")
        self.status_combo = QComboBox()
        populate_status_combo(self.status_combo, schedule)
        self.status_combo.currentIndexChanged.connect(self._on_status_changed)
        status_row.addWidget(status_caption)
        status_row.addWidget(self.status_combo, 1)
        root.addLayout(status_row)

        if schedule.content:
            preview = QLabel(schedule.content.replace("\n", " ")[:80])
            preview.setObjectName("ScheduleCardPreview")
            preview.setWordWrap(True)
            root.addWidget(preview)

    def _update_notify_btn(self, enabled: bool) -> None:
        self.notify_btn.setIcon(notify_on_icon() if enabled else notify_off_icon())
        self.notify_btn.setIconSize(QSize(18, 18))
        self.notify_btn.setToolTip(
            "Click to turn notifications off"
            if enabled
            else "Click to turn notifications on"
        )

    def _on_notify(self) -> None:
        enabled = toggle_notification(self.schedule.id)
        if enabled is not None:
            self.schedule.notification_enabled = enabled
            self._update_notify_btn(enabled)
            self.notify_toggled.emit(self.schedule.id, enabled)

    def _on_status_changed(self) -> None:
        status = self.status_combo.currentData()
        if status and status != self.schedule.completion_status:
            if set_completion_status(self.schedule.id, status):
                self.schedule.completion_status = status
                apply_schedule_card_style(self, self.schedule)
                self.completion_changed.emit(self.schedule.id)

    def mouseDoubleClickEvent(self, event) -> None:
        self.double_clicked.emit(self.schedule.id)
        super().mouseDoubleClickEvent(event)


class DayDetailPanel(QFrame):
    schedule_double_clicked = pyqtSignal(int)
    schedule_deleted = pyqtSignal()
    schedule_changed = pyqtSignal()
    notification_toggled = pyqtSignal(int, bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._day = datetime.now().date()
        self._day_timeline: DayTimeline | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QVBoxLayout()
        header.setSpacing(4)
        self.sidebar_title = QLabel("Day Schedules")
        self.sidebar_title.setObjectName("SidebarTitle")
        self.date_label = QLabel()
        self.date_label.setObjectName("DayDetailTitle")
        self.count_label = QLabel()
        self.count_label.setObjectName("SidebarCount")
        header.addWidget(self.sidebar_title)
        header.addWidget(self.date_label)
        header.addWidget(self.count_label)
        layout.addLayout(header)

        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.timeline_container)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll, 1)

        self.empty_label = QLabel("No schedules on this day")
        self.empty_label.setObjectName("EmptySubtitle")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        layout.addWidget(self.empty_label)

    def show_date(self, day: date, schedules: list[Schedule]) -> None:
        self._day = day
        self.date_label.setText(day.strftime("%A, %B %d"))
        day_schedules = schedules_for_date(schedules, day)
        self.count_label.setText(
            f"{len(day_schedules)} schedule{'s' if len(day_schedules) != 1 else ''}"
        )

        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._day_timeline = None

        today = datetime.now().date()
        if day == today:
            self._day_timeline = DayTimeline(day)
            self._day_timeline.set_schedules(schedules_for_date(schedules, day))
            self._day_timeline.setFixedHeight(56)
            self.timeline_layout.addWidget(self._day_timeline)
            self.timeline_container.show()
        else:
            self.timeline_container.hide()

        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.empty_label.setVisible(len(day_schedules) == 0)
        self.scroll.setVisible(len(day_schedules) > 0)

        for schedule in day_schedules:
            card = ScheduleCard(schedule)
            card.double_clicked.connect(self.schedule_double_clicked.emit)
            card.delete_requested.connect(self._on_delete)
            card.notify_toggled.connect(self.notification_toggled.emit)
            card.completion_changed.connect(lambda _id: self.schedule_changed.emit())
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

    def update_time_flow(self) -> None:
        if self._day_timeline:
            self._day_timeline.update_flow()

    def _on_delete(self, schedule_id: int) -> None:
        delete_schedule(schedule_id)
        self.schedule_deleted.emit()
        self.schedule_changed.emit()
