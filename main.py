import sys

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from database import init_db
from main_window import MainWindow
from notification_service import NotificationService
from styles import APP_STYLESHEET


def create_tray_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(66, 133, 244))
    painter.setPen(QColor(40, 90, 180))
    painter.drawRoundedRect(4, 4, 56, 56, 10, 10)
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setPointSize(28)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x0084, "S")
    painter.end()
    return QIcon(pixmap)


def main() -> int:
    init_db()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available on this system.")
        return 1

    window = MainWindow()
    tray_icon = QSystemTrayIcon(create_tray_icon(), app)
    tray_icon.setToolTip("Schedule Manager")

    menu = QMenu()
    show_action = menu.addAction("Show Schedules")
    show_action.triggered.connect(window.show)
    show_action.triggered.connect(window.raise_)
    show_action.triggered.connect(window.activateWindow)

    add_action = menu.addAction("Add Schedule")
    add_action.triggered.connect(window._add_schedule)

    menu.addSeparator()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)

    tray_icon.setContextMenu(menu)
    def on_tray_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            window.show()
            window.raise_()
            window.activateWindow()

    tray_icon.activated.connect(on_tray_activated)
    tray_icon.show()

    notifier = NotificationService(tray_icon)
    window.schedule_changed.connect(notifier.reload)
    window.notification_toggled.connect(notifier.on_notification_toggled)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
