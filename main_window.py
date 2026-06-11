from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from calendar_view import CalendarWidget, DayDetailPanel
from database import Schedule, get_all_schedules, save_schedule
from schedule_dialog import ScheduleDialog


class MainWindow(QWidget):
    schedule_changed = pyqtSignal()
    notification_toggled = pyqtSignal(int, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Manager")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setMinimumSize(980, 520)
        self._schedules: list[Schedule] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 14)
        root.setSpacing(12)

        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 14, 16, 14)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        self.title_label = QLabel("Schedule Manager")
        self.title_label.setObjectName("AppTitle")
        self.subtitle_label = QLabel("Calendar view of your plans")
        self.subtitle_label.setObjectName("AppSubtitle")
        title_block.addWidget(self.title_label)
        title_block.addWidget(self.subtitle_label)
        header_layout.addLayout(title_block)
        header_layout.addStretch()

        self.count_label = QLabel("0 schedules")
        self.count_label.setObjectName("AppSubtitle")
        self.count_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        header_layout.addWidget(self.count_label)

        add_btn = QPushButton("+ New Schedule")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_schedule)
        header_layout.addWidget(add_btn)
        root.addWidget(header_card)

        self.stack = QStackedWidget()
        self.empty_widget = self._build_empty_state()
        self.stack.addWidget(self.empty_widget)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.calendar = CalendarWidget()
        self.calendar.day_selected.connect(self._on_day_selected)
        self.calendar.schedules_updated.connect(self.refresh)
        splitter.addWidget(self.calendar)

        self.day_panel = DayDetailPanel()
        self.day_panel.setMinimumWidth(300)
        self.day_panel.setMaximumWidth(380)
        self.day_panel.schedule_double_clicked.connect(self._edit_schedule)
        self.day_panel.schedule_changed.connect(self._on_schedule_changed)
        self.day_panel.notification_toggled.connect(self.notification_toggled.emit)
        self.calendar.time_flow_tick.connect(self.day_panel.update_time_flow)
        splitter.addWidget(self.day_panel)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([620, 320])

        content_layout.addWidget(splitter)

        hint = QLabel("Click a day to view schedules · Double-click a schedule to edit")
        hint.setObjectName("HintLabel")
        content_layout.addWidget(hint)

        self.stack.addWidget(content)
        root.addWidget(self.stack, 1)

    def _build_empty_state(self) -> QWidget:
        wrapper = QFrame()
        wrapper.setObjectName("EmptyCard")
        layout = QVBoxLayout(wrapper)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(32, 48, 32, 48)

        icon = QLabel("📅")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("No schedules yet")
        title.setObjectName("EmptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Create your first schedule to see it on the calendar")
        subtitle.setObjectName("EmptySubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        cta = QPushButton("+ Create Schedule")
        cta.setObjectName("PrimaryButton")
        cta.setCursor(Qt.CursorShape.PointingHandCursor)
        cta.clicked.connect(self._add_schedule)
        cta.setFixedWidth(180)
        cta_row = QHBoxLayout()
        cta_row.addStretch()
        cta_row.addWidget(cta)
        cta_row.addStretch()
        layout.addLayout(cta_row)
        return wrapper

    def refresh(self) -> None:
        self._schedules = get_all_schedules()
        count = len(self._schedules)
        self.count_label.setText(f"{count} schedule{'s' if count != 1 else ''}")
        self.stack.setCurrentIndex(0 if count == 0 else 1)

        if count > 0:
            self.calendar.refresh(self._schedules)
            selected = self.calendar.selected_date()
            self.day_panel.show_date(selected, self._schedules)

    def _on_day_selected(self, day) -> None:
        self.day_panel.show_date(day, self._schedules)

    def _on_schedule_changed(self) -> None:
        self.refresh()
        self.schedule_changed.emit()

    def _add_schedule(self) -> None:
        selected = self.calendar.selected_date() if self._schedules else datetime.now().date()
        start = datetime.combine(selected, datetime.now().time()).replace(
            second=0, microsecond=0
        )
        schedule = Schedule(
            id=None,
            title="",
            start_time=start,
            end_time=start + timedelta(hours=1),
            content="",
            url="",
            notification_enabled=True,
            notification_time="30 minutes ago",
            repeat_time="5 minutes",
            completion_status="not_done",
        )
        dialog = ScheduleDialog(schedule, self)
        if dialog.exec():
            save_schedule(dialog.get_schedule())
            self.refresh()
            self.schedule_changed.emit()

    def _edit_schedule(self, schedule_id: int) -> None:
        from database import get_schedule

        schedule = get_schedule(schedule_id)
        if not schedule:
            return
        dialog = ScheduleDialog(schedule, self)
        if dialog.exec():
            save_schedule(dialog.get_schedule())
            self.refresh()
            self.schedule_changed.emit()

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
