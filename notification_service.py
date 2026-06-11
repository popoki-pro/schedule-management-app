from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QSystemTrayIcon

from database import NOTIFICATION_TIMES, REPEAT_TIMES, Schedule, get_all_schedules


class NotificationService(QObject):
    notify = pyqtSignal(str, str)

    def __init__(self, tray: QSystemTrayIcon):
        super().__init__()
        self._tray = tray
        self._last_fired: dict[int, datetime] = {}
        self._disabled_ids: set[int] = set()
        self._timer = QTimer(self)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(self._check_notifications)
        self.reload()
        self._timer.start()

    def reload(self) -> None:
        self._last_fired.clear()
        self._disabled_ids = {
            s.id
            for s in get_all_schedules()
            if s.id is not None and not s.notification_enabled
        }

    def on_notification_toggled(self, schedule_id: int, enabled: bool) -> None:
        if enabled:
            self._disabled_ids.discard(schedule_id)
        else:
            self._disabled_ids.add(schedule_id)
            self._last_fired.pop(schedule_id, None)

    def _is_notification_enabled(self, schedule: Schedule) -> bool:
        if schedule.id is None:
            return schedule.notification_enabled
        if schedule.id in self._disabled_ids:
            return False
        return schedule.notification_enabled

    def _check_notifications(self) -> None:
        now = datetime.now()
        for schedule in get_all_schedules():
            if schedule.id is not None and not schedule.notification_enabled:
                self._disabled_ids.add(schedule.id)
            if not self._is_notification_enabled(schedule):
                continue
            self._maybe_notify(schedule, now)

    def _maybe_notify(self, schedule: Schedule, now: datetime) -> None:
        if now >= schedule.start_time:
            return

        lead_minutes = NOTIFICATION_TIMES.get(schedule.notification_time, 30)
        first_notify_at = schedule.start_time - timedelta(minutes=lead_minutes)
        if now < first_notify_at:
            return

        repeat_minutes = REPEAT_TIMES.get(schedule.repeat_time, 5)
        last = self._last_fired.get(schedule.id)
        if last and (now - last) < timedelta(minutes=repeat_minutes):
            return

        self._last_fired[schedule.id] = now
        remaining = schedule.start_time - now
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes = remainder // 60
        if hours > 0:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{minutes}m"

        title = f"Upcoming: {schedule.title}"
        message = f"Starts in {time_str}"
        if schedule.content:
            message += f"\n{schedule.content}"

        self.notify.emit(title, message)
        self._tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)
