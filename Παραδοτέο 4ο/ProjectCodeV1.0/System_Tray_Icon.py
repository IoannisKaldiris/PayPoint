from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QLabel, QWidgetAction
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, pyqtSignal
from Login_NDA_UI import Login_NDA_UI

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self.setToolTip('PayPoint NDA mode')

        # Create a QMenu for the tray icon
        self.menu = QMenu()

        # Adding title of QSystemTrayIcon
        self.tray_title = QLabel("<img src='Images/PDN_tray_icon.png' width='45' height='25'>\tPDN PayPoint")
        self.title_action = QWidgetAction(self.menu)

        # Adding BNR and CLS of QSystemTrayIcon
        self.BNR_label = QLabel(
            "<img src=Images/28-285541_star-icon-white-png-transparent-png-removebg-preview.png width='25' height='25'> &nbsp;BNR: READY")
        self.BNR_action = QWidgetAction(self.menu)
        self.BNR_action.setDefaultWidget(self.BNR_label)

        self.CLS_label = QLabel(
            "<img src=Images/28-285541_star-icon-white-png-transparent-png-removebg-preview.png width='25' height='25'> &nbsp; CLS: READY")
        self.CLS_action = QWidgetAction(self.menu)
        self.CLS_action.setDefaultWidget(self.CLS_label)

        # NDA mode
        self.NDA_label = ClickableLabel(
            "<img src='Images/menu-bar_resized.png' width='25' height='25' style='vertical-align: middle' > &nbsp; Admin mode")
        self.NDA_action = QWidgetAction(self.menu)
        self.NDA_action.setDefaultWidget(self.NDA_label)

        # Admin Login Widget
        self.admin_login_widget = Login_NDA_UI()

        self.setupUI()

    def setupUI(self):
        # Set object names
        self.tray_title.setObjectName("Tray_title")
        self.BNR_label.setObjectName("BNR_title")
        self.CLS_label.setObjectName("CLS_title")
        self.NDA_label.setObjectName("NDA_title")

        # Set css
        menu_style = """
            QMenu {
                background-color: #333; /* dark background */
                color: #fff; /* white text */
                border: 1px solid #555;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
            }
            QMenu::item:selected { /* when selected */
                background-color: #666;
            }
            QMenu::separator {
                height: 2px;
                background: white; /* make separator white */
                margin-left: 10px;
                margin-right: 10px;
            }
            #BNR_title, #CLS_title {
                color: white;
                font-size: 20px; 
                margin-left: 15px;
            }
            #BNR_title {
                margin-top: 5px;
                margin-bottom: 5px;
            }
            #CLS_title {
                margin-bottom: 10px;
            }
            #NDA_title:hover {
                background-color: #707070;
            }
        """
        title_label_css = """
            #Tray_title {
                color: white; /* Gold color */
                font-size: 26px; /* Larger font size */
            }
        """

        self.menu.setStyleSheet(menu_style)
        self.tray_title.setStyleSheet(title_label_css)
        self.NDA_label.setStyleSheet(
            "padding-top: 10px; padding-bottom: 10px; padding-left: 15px; color: white; font-size: 20px;")
        # Add actions to qsystem tray icon
        self.title_action.setDefaultWidget(self.tray_title)

        self.menu.addAction(self.title_action)
        self.menu.addSeparator()

        self.menu.addAction(self.BNR_action)
        self.menu.addAction(self.CLS_action)
        self.menu.addSeparator()

        self.menu.addAction(self.NDA_action)

        # NDA Label
        self.NDA_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.NDA_label.clicked.connect(self.NDA_mode)

        self.setContextMenu(self.menu)

    def NDA_mode(self):
        self.admin_login_widget.show()


class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # Signal to emit when the label is clicked

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit clicked signal when the label is pressed
