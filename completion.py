from datetime import datetime

from PyQt6.QtWidgets import QComboBox, QWidget

from database import (
    COMPLETION_STATUSES,
    STATUS_CALENDAR_COLORS,
    STATUS_DONE,
    STATUS_INCOMPLETE,
    STATUS_LABELS,
    STATUS_NOT_DONE,
    Schedule,
)

DEFAULT_PILL = ("#3d4f6a", "#d1d9e6")
DEFAULT_CARD_BORDER = "#323844"


def has_elapsed(schedule: Schedule, now: datetime | None = None) -> bool:
    return (now or datetime.now()) >= schedule.end_time


def available_statuses(schedule: Schedule, now: datetime | None = None) -> tuple[str, ...]:
    if has_elapsed(schedule, now):
        return (STATUS_DONE, STATUS_INCOMPLETE)
    return (STATUS_NOT_DONE, STATUS_DONE)


def display_status(schedule: Schedule, now: datetime | None = None) -> str:
    now = now or datetime.now()
    if schedule.completion_status == STATUS_DONE:
        return STATUS_DONE
    if not has_elapsed(schedule, now):
        return STATUS_NOT_DONE
    return STATUS_INCOMPLETE


def apply_calendar_pill_style(
    widget: QWidget, schedule: Schedule, now: datetime | None = None
) -> None:
    shown = display_status(schedule, now)
    if shown == STATUS_DONE:
        bg, fg = STATUS_CALENDAR_COLORS[STATUS_DONE]
    elif shown == STATUS_INCOMPLETE:
        bg, fg = STATUS_CALENDAR_COLORS[STATUS_INCOMPLETE]
    else:
        bg, fg = DEFAULT_PILL
    widget.setStyleSheet(
        f"background-color: {bg}; color: {fg}; border-radius: 4px; padding: 2px 4px;"
    )


def apply_schedule_card_style(
    card: QWidget, schedule: Schedule, now: datetime | None = None
) -> None:
    shown = display_status(schedule, now)
    border_colors = {
        STATUS_DONE: "#7fd99a",
        STATUS_INCOMPLETE: "#e2b86b",
        STATUS_NOT_DONE: DEFAULT_CARD_BORDER,
    }
    color = border_colors.get(shown, DEFAULT_CARD_BORDER)
    card.setStyleSheet(
        f"QFrame#ScheduleCard {{ border-left: 3px solid {color}; }}"
    )


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, STATUS_LABELS[STATUS_NOT_DONE])


def display_status_label(schedule: Schedule, now: datetime | None = None) -> str:
    return status_label(display_status(schedule, now))


def populate_status_combo(combo: QComboBox, schedule: Schedule, now: datetime | None = None) -> None:
    current = schedule.completion_status
    allowed = available_statuses(schedule, now)
    if current not in allowed:
        current = allowed[0]

    combo.blockSignals(True)
    combo.clear()
    for status in allowed:
        combo.addItem(STATUS_LABELS[status], status)
    idx = combo.findData(current)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    combo.blockSignals(False)
