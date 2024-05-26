from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QCursor
from PyQt6.QtCore import QSize, Qt
from Cash_Inventory_and_Refill import CashInventoryUI
from Pickup import PickupUI


class NDA_Menu_Button(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_pixmap = QPixmap()
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("Menu_Button")

    def sizeHint(self):
        parent_hint = super().sizeHint()
        if not self.m_pixmap.isNull():
            return QSize(parent_hint.width() + self.m_pixmap.width(), max(parent_hint.height(), self.m_pixmap.height()))
        return parent_hint

    def setPixmap(self, pixmap):
        self.m_pixmap = pixmap
        self.update()  # Force a repaint to show the pixmap

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.m_pixmap.isNull():
            painter = QPainter(self)
            y = (self.height() - self.m_pixmap.height()) // 2
            painter.drawPixmap(10, y, self.m_pixmap)


class NDA_UI(QWidget):
    def __init__(self):
        super().__init__()
        self.CashInventoryRefillUI = None
        self.pickupUI = None  # Initialize pickupUI here
        self.setFixedSize(600, 500)  # Set fixed size for the NDA menu

        # Layout
        self.layout = QVBoxLayout()
        self.main_widget = QWidget()

        # Import Images
        self.PayPoint_logo = QLabel()
        self.PayPoint_logo.setPixmap(QPixmap('Images/PayPoint_full_logo.png'))
        self.CubeIQ_image = QLabel()
        self.CubeIQ_image.setPixmap(QPixmap('Images/up_2017_logo_en_resized_150x47.png'))

        # Cash Inventory and Refill Button
        self.cashInventoryButton = NDA_Menu_Button("Cash Inventory and Refill")
        self.cashInventoryButton.setPixmap(QPixmap('Images/double-chevron_30x31.png'))

        # Pickup
        self.PickupButton = NDA_Menu_Button("Pickup")
        self.PickupButton.setPixmap(QPixmap('Images/pickup_double-chevron_30x31.png'))

        # Exchange
        self.ExchangeButton = NDA_Menu_Button("Exchange")
        self.ExchangeButton.setPixmap(QPixmap('Images/reverse_double-chevron_30x31-removebg-preview_30x31.png'))

        # Loader Replacement
        self.Loader_Replacement_Button = NDA_Menu_Button("Loader Replacement")
        self.Loader_Replacement_Button.setPixmap(QPixmap('Images/Loader_double-chevron_30x31.png'))

        # CashBox Replacement
        self.CashBox_Replacement_Button = NDA_Menu_Button("CashBox Replacement")
        self.CashBox_Replacement_Button.setPixmap(QPixmap('Images/screen-rotation-button_30x30.png'))

        # About and Exit Button
        self.About_button = QPushButton("About")
        self.Exit_button = QPushButton("Exit")

        self.setupUI()

    def setupUI(self):
        # Set Object names
        self.About_button.setObjectName("About_button")
        self.Exit_button.setObjectName("Exit_button")
        # Set CSS of window
        style = '''
        QWidget {background: white;}
        QPushButton#Menu_Button {
            background-color: #0011fe; 
            color: white; 
            font-size: 20px; 
            font-weight: bold;
            padding: 5px;
        }
        QPushButton#Menu_Button::text {
            padding: 20px;
        }
        QPushButton#Menu_Button::icon {
            position: absolute;
            left: 10px;
        }
        QPushButton#About_button {background-color: #6c757e;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   min-width: 100px; position: relative; text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        QPushButton#Exit_button {background-color: #0c6efd;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   min-width: 100px; position: relative; text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        '''
        self.setStyleSheet(style)

        # Remove the title bar and disable closing the window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus)

        # Add logos
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.PayPoint_logo, alignment=Qt.AlignmentFlag.AlignLeft)
        logo_layout.addSpacing(50)
        logo_layout.addWidget(self.CubeIQ_image, alignment=Qt.AlignmentFlag.AlignRight)

        # Footer buttons
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.About_button, alignment=Qt.AlignmentFlag.AlignLeft)
        footer_layout.addWidget(self.Exit_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.About_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.Exit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Buttons
        self.cashInventoryButton.clicked.connect(self.showCashInventory)
        self.PickupButton.clicked.connect(self.showPickup)
        self.Exit_button.clicked.connect(self.hide)

        # Add to layout
        self.layout.addLayout(logo_layout)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.cashInventoryButton)
        self.layout.addWidget(self.PickupButton)
        self.layout.addWidget(self.ExchangeButton)
        self.layout.addWidget(self.Loader_Replacement_Button)
        self.layout.addWidget(self.CashBox_Replacement_Button)
        self.layout.addSpacing(100)
        self.layout.addLayout(footer_layout)

        self.setLayout(self.layout)

    def showCashInventory(self):
        # Create CashInventory and show it
        if not self.CashInventoryRefillUI:
            self.CashInventoryRefillUI = CashInventoryUI()
            self.CashInventoryRefillUI.backClicked.connect(self.show)
        self.hide()
        self.CashInventoryRefillUI.show()

    def showPickup(self):
        # Create one PickupUI
        if not self.pickupUI:
            self.pickupUI = PickupUI()
            self.pickupUI.backClicked.connect(self.show)  # Connect the signal to the show slot
        self.hide()  # Hide the NDA_UI when showing the PickupUI
        self.pickupUI.show()
