APP_STYLESHEET = """
QWidget {
    background-color: #1a1d23;
    color: #e8eaed;
    font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1a1d23;
}

QLabel {
    background: transparent;
    background-color: transparent;
}

QLabel#AppTitle {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#AppSubtitle {
    font-size: 12px;
    color: #8b939e;
}

QLabel#SectionTitle {
    font-size: 11px;
    font-weight: 600;
    color: #6c9eff;
    letter-spacing: 0.6px;
    padding-top: 4px;
}

QLabel#HintLabel {
    font-size: 11px;
    color: #6b7280;
    padding: 6px 2px 0 2px;
}

QLabel#EmptyTitle {
    font-size: 15px;
    font-weight: 600;
    color: #c5cad3;
}

QLabel#EmptySubtitle {
    font-size: 12px;
    color: #6b7280;
}

QLabel#FormLabel {
    color: #9aa0a8;
    font-size: 12px;
    min-width: 120px;
}

QLabel#DialogTitle {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#DialogSubtitle {
    font-size: 12px;
    color: #8b939e;
}

QPushButton#PrimaryButton {
    background-color: #4f8cff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton#PrimaryButton:hover {
    background-color: #6c9eff;
}

QPushButton#PrimaryButton:pressed {
    background-color: #3d78e8;
}

QPushButton#SecondaryButton {
    background-color: #2d323c;
    color: #d1d5db;
    border: 1px solid #3a4050;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #363c48;
    border-color: #4a5162;
}

QPushButton#DangerButton {
    background-color: transparent;
    color: #f07178;
    border: 1px solid #4a3038;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 500;
    min-width: 52px;
    max-width: 68px;
}

QPushButton#DangerButton:hover {
    background-color: #3a2228;
    border-color: #f07178;
}

QPushButton#IconDangerButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4x;
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
}

QPushButton#IconDangerButton:hover {
    background-color: #3a2228;
    border-color: #4a3038;
}

QPushButton#IconToggleButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4px;
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
}

QPushButton#IconToggleButton:hover {
    background-color: #2d3340;
    border-color: #3a4050;
}

QPushButton#GhostButton {
    background-color: transparent;
    color: #9aa0a8;
    border: 1px solid #3a4050;
    border-radius: 8px;
    padding: 8px 14px;
}

QPushButton#GhostButton:hover {
    background-color: #2d323c;
    color: #e8eaed;
}

QTableWidget {
    background-color: #242830;
    alternate-background-color: #282d37;
    border: 1px solid #323844;
    border-radius: 10px;
    gridline-color: #323844;
    selection-background-color: #2f3d56;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item {
    padding: 10px 12px;
    border: none;
}

QTableWidget::item:hover {
    background-color: #2d3340;
}

QHeaderView::section {
    background-color: #1f232b;
    color: #8b939e;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #323844;
    border-right: 1px solid #2a2f38;
}

QHeaderView::section:last {
    border-right: none;
}

QLineEdit, QTextEdit, QDateTimeEdit, QComboBox {
    background-color: #2d323c;
    color: #e8eaed;
    border: 1px solid #3a4050;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #4f8cff;
}

QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus, QComboBox:focus {
    border-color: #4f8cff;
}

QLineEdit::placeholder {
    color: #5c6370;
}

QTextEdit {
    padding: 8px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b939e;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #2d323c;
    color: #e8eaed;
    border: 1px solid #3a4050;
    selection-background-color: #4f8cff;
    outline: none;
}

QDateTimeEdit::drop-down {
    border: none;
    width: 20px;
}

QScrollBar:vertical {
    background: #1a1d23;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #3a4050;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #4a5162;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #1a1d23;
    height: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #3a4050;
    border-radius: 5px;
    min-width: 24px;
}

QMenu {
    background-color: #242830;
    color: #e8eaed;
    border: 1px solid #3a4050;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 28px 8px 16px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #2f3d56;
}

QMenu::separator {
    height: 1px;
    background: #3a4050;
    margin: 4px 8px;
}

QFrame#Card {
    background-color: #242830;
    border: 1px solid #323844;
    border-radius: 12px;
}

QFrame#EmptyCard {
    background-color: #242830;
    border: 1px dashed #3a4050;
    border-radius: 12px;
}

QLabel#CalendarMonth {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#WeekdayHeader {
    font-size: 11px;
    font-weight: 600;
    color: #6b7280;
    padding: 4px 0;
}

QPushButton#NavButton {
    background-color: #2d323c;
    color: #e8eaed;
    border: 1px solid #3a4050;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 600;
    padding: 0;
}

QPushButton#NavButton:hover {
    background-color: #363c48;
    border-color: #4a5162;
}

QFrame#DayCell {
    background-color: #2a2f38;
    border: 1px solid #323844;
    border-radius: 8px;
}

QFrame#DayCell[otherMonth="true"] {
    background-color: #22262e;
    border-color: #2a2f38;
}

QFrame#DayCell[otherMonth="true"] QLabel#DayNumber {
    color: #4a5162;
}

QFrame#DayCell[today="true"] {
    border-color: #4f8cff;
}

QFrame#DayCell[selected="true"] {
    background-color: #2f3d56;
    border-color: #4f8cff;
}

QFrame#DayCell:hover {
    background-color: #323844;
    border-color: #4a5162;
}

QLabel#DayNumber {
    font-size: 13px;
    font-weight: 600;
    color: #e8eaed;
}

QFrame#DayCell[today="true"] QLabel#DayNumber {
    color: #6c9eff;
}

QLabel#EventPill {
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 9px;
}

QLabel#MoreEvents {
    font-size: 9px;
    color: #6b7280;
    padding-left: 2px;
}

QLabel#DayDetailTitle {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
}

QFrame#ScheduleCard {
    background-color: #2a2f38;
    border: 1px solid #323844;
    border-radius: 8px;
}

QFrame#ScheduleCard:hover {
    background-color: #2f3540;
    border-color: #3d78e8;
}

QLabel#ScheduleTime {
    font-size: 13px;
    font-weight: 600;
    color: #6c9eff;
}

QLabel#ScheduleTimeEnd {
    font-size: 11px;
    color: #6b7280;
}

QLabel#ScheduleCardTitle {
    font-size: 13px;
    font-weight: 600;
    color: #e8eaed;
}

QLabel#ScheduleCardPreview {
    font-size: 11px;
    color: #6b7280;
}

QScrollArea {
    background: transparent;
    border: none;
}

QSplitter::handle:horizontal {
    background-color: #323844;
    width: 2px;
    margin: 0 6px;
}

QSplitter::handle:vertical {
    background-color: #323844;
    height: 2px;
    margin: 6px 0;
}

QFrame#Sidebar {
    background-color: #1f232b;
    border: 1px solid #323844;
    border-radius: 12px;
}

QLabel#SidebarTitle {
    font-size: 11px;
    font-weight: 600;
    color: #6c9eff;
    letter-spacing: 0.6px;
}

QLabel#SidebarCount {
    font-size: 12px;
    color: #8b939e;
}

QLabel#SidebarTimeNow {
    font-size: 13px;
    font-weight: 600;
    color: #6c9eff;
    min-width: 48px;
}
"""
