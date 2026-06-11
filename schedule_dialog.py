from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from completion import populate_status_combo
from database import (
    NOTIFICATION_TIMES,
    REPEAT_TIMES,
    STATUS_NOT_DONE,
    Schedule,
)
from icons import notify_off_icon, notify_on_icon


class ScheduleDialog(QDialog):
    def __init__(self, schedule: Schedule | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.schedule = schedule
        self.is_new = schedule is None or schedule.id is None
        self.setWindowTitle("New Schedule" if self.is_new else "Edit Schedule")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if schedule:
            self._load_schedule(schedule)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("New Schedule" if self.is_new else "Edit Schedule")
        title.setObjectName("DialogTitle")
        subtitle = QLabel("Fill in the details below. All times use your local clock.")
        subtitle.setObjectName("DialogSubtitle")
        subtitle.setWordWrap(True)
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        details_card = self._section_card("DETAILS")
        details_form = details_card.findChild(QFormLayout)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Meeting with team, Doctor appointment…")
        details_form.addRow(self._label("Title"), self.title_edit)

        time_row = QHBoxLayout()
        time_row.setSpacing(10)
        self.start_edit = QDateTimeEdit()
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDisplayFormat("yyyy-MM-dd  HH:mm")
        self.start_edit.setDateTime(QDateTime.currentDateTime())
        self.end_edit = QDateTimeEdit()
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDisplayFormat("yyyy-MM-dd  HH:mm")
        self.end_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.end_edit.dateTimeChanged.connect(self._update_completion_combo)
        time_row.addWidget(self._field_block("Start", self.start_edit))
        time_row.addWidget(self._field_block("End", self.end_edit))
        details_form.addRow(self._label("Time"), time_row)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Notes, agenda, or anything you want to remember…")
        self.content_edit.setMaximumHeight(96)
        details_form.addRow(self._label("Content"), self.content_edit)

        url_row = QHBoxLayout()
        url_row.setSpacing(8)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")
        self.open_url_btn = QPushButton("Open")
        self.open_url_btn.setObjectName("GhostButton")
        self.open_url_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_url_btn.clicked.connect(self._open_url)
        url_row.addWidget(self.url_edit, 1)
        url_row.addWidget(self.open_url_btn)
        details_form.addRow(self._label("URL"), url_row)

        self.completion_combo = QComboBox()
        details_form.addRow(self._label("Completion"), self.completion_combo)
        self._update_completion_combo()
        root.addWidget(details_card)

        notify_card = self._section_card("NOTIFICATIONS")
        notify_form = notify_card.findChild(QFormLayout)

        self.notification_combo = QComboBox()
        self.notification_combo.addItem(notify_on_icon(), "On")
        self.notification_combo.addItem(notify_off_icon(), "Off")
        self.notification_combo.currentTextChanged.connect(self._toggle_notification_fields)
        notify_form.addRow(self._label("Status"), self.notification_combo)

        self.notification_time_combo = QComboBox()
        self.notification_time_combo.addItems(list(NOTIFICATION_TIMES.keys()))
        notify_form.addRow(self._label("Remind before"), self.notification_time_combo)

        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(list(REPEAT_TIMES.keys()))
        notify_form.addRow(self._label("Repeat every"), self.repeat_combo)
        root.addWidget(notify_card)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #f07178; font-size: 12px;")
        self.error_label.hide()
        root.addWidget(self.error_label)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Schedule")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._validate_and_accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        root.addLayout(buttons)

        self.title_edit.returnPressed.connect(self._validate_and_accept)

    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FormLabel")
        return label

    def _field_block(self, caption: str, widget: QWidget) -> QWidget:
        block = QWidget()
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        cap = QLabel(caption)
        cap.setObjectName("FormLabel")
        layout.addWidget(cap)
        layout.addWidget(widget)
        return block

    def _section_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        section = QLabel(title)
        section.setObjectName("SectionTitle")
        layout.addWidget(section)
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(form)
        return card

    def _toggle_notification_fields(self, status: str) -> None:
        enabled = status == "On"
        self.notification_time_combo.setEnabled(enabled)
        self.repeat_combo.setEnabled(enabled)

    def _update_completion_combo(self) -> None:
        schedule = Schedule(
            id=self.schedule.id if self.schedule else None,
            title=self.title_edit.text().strip(),
            start_time=self.start_edit.dateTime().toPyDateTime(),
            end_time=self.end_edit.dateTime().toPyDateTime(),
            content="",
            url="",
            notification_enabled=True,
            notification_time="30 minutes ago",
            repeat_time="5 minutes",
            completion_status=self.completion_combo.currentData() or STATUS_NOT_DONE,
        )
        populate_status_combo(self.completion_combo, schedule)

    def _load_schedule(self, schedule: Schedule) -> None:
        self.title_edit.setText(schedule.title)
        self.start_edit.setDateTime(
            QDateTime.fromString(
                schedule.start_time.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm"
            )
        )
        self.end_edit.setDateTime(
            QDateTime.fromString(
                schedule.end_time.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm"
            )
        )
        self.content_edit.setPlainText(schedule.content)
        self.url_edit.setText(schedule.url)
        populate_status_combo(self.completion_combo, schedule)
        self.notification_combo.setCurrentText("On" if schedule.notification_enabled else "Off")
        idx = self.notification_time_combo.findText(schedule.notification_time)
        if idx >= 0:
            self.notification_time_combo.setCurrentIndex(idx)
        idx = self.repeat_combo.findText(schedule.repeat_time)
        if idx >= 0:
            self.repeat_combo.setCurrentIndex(idx)
        self._toggle_notification_fields(self.notification_combo.currentText())

    def _open_url(self) -> None:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices

        url = self.url_edit.text().strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            QDesktopServices.openUrl(QUrl(url))

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.show()

    def _validate_and_accept(self) -> None:
        self.error_label.hide()
        if not self.title_edit.text().strip():
            self._show_error("Please enter a title for this schedule.")
            self.title_edit.setFocus()
            return
        start = self.start_edit.dateTime().toPyDateTime()
        end = self.end_edit.dateTime().toPyDateTime()
        if end <= start:
            self._show_error("End time must be after the start time.")
            self.end_edit.setFocus()
            return
        self.accept()

    def get_schedule(self) -> Schedule:
        return Schedule(
            id=self.schedule.id if self.schedule else None,
            title=self.title_edit.text().strip(),
            start_time=self.start_edit.dateTime().toPyDateTime(),
            end_time=self.end_edit.dateTime().toPyDateTime(),
            content=self.content_edit.toPlainText().strip(),
            url=self.url_edit.text().strip(),
            notification_enabled=self.notification_combo.currentText() == "On",
            notification_time=self.notification_time_combo.currentText(),
            repeat_time=self.repeat_combo.currentText(),
            completion_status=self.completion_combo.currentData() or STATUS_NOT_DONE,
        )
