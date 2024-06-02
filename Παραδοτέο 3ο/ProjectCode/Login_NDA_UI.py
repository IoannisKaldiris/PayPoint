import json
import mysql.connector
from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon, QCursor
from PyQt6.QtCore import Qt
from mysql.connector import Error
from NDA_menu import NDA_UI


def load_config():
    """
    Load configuration data from JSON file
    :return: json object
    """
    with open('appsettings.json', 'r') as file:
        data = json.load(file)
    return data


class Login_NDA_UI(QWidget):
    def __init__(self):
        super().__init__()

        # Set Fixed Size window
        self.setFixedSize(520, 600)

        # Import Images
        self.CubeIQ_image = QPixmap('Images/up_2017_logo_en_resized.png')
        self.CubeIQ_icon_image = QIcon('Images/up_2017_logo_en.ico')
        self.Euro_image = QPixmap('Images/euro_sign_612x612-removebg-preview.png')
        self.setWindowIcon(self.CubeIQ_icon_image)

        # Set Main Window Title
        self.setWindowTitle("NDA Sign In")
        self.setWindowIcon(self.CubeIQ_icon_image)

        # Create layout
        self.layout = QVBoxLayout()

        # Add logo and title
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("Images/PayPoint_logo.png").scaledToWidth(70))
        self.title = QLabel("Sign In")

        # Username and Password fields
        self.username_label = QLabel("Username")
        self.password_label = QLabel("Password")

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()

        # Error Label
        self.error_label = QLabel("")

        # Buttons
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")

        # Logo Image
        self.UPatras_logo = QLabel()

        # NDA menu
        self.NDA_menu = NDA_UI()

        self.setupUI()

    def setupUI(self):
        # set object names
        self.back_button.setObjectName("Back_button")
        self.next_button.setObjectName("Next_button")
        self.title.setObjectName("Sign_In")
        self.username_label.setObjectName("Username_label")
        self.password_label.setObjectName("Password_label")
        self.error_label.setObjectName("Error_label")

        # Set CSS of window
        style = '''
        QWidget {background: white;}
        QPushButton#Back_button {background-color: #31363F;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   max-width: 100px; position: relative; text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        QPushButton#Next_button {background-color: #0a6bff;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   max-width: 100px; position: relative; text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        QLabel#Sign_In {font-size: 30px;}
        QLineEdit { background-color: #f0f0f0; border: 2px solid #ccc; border-radius: 8px; padding: 6px 12px; font-size: 16px; color: #333; margin-left: 20px; margin-right: 20px;}
        QLineEdit:focus { background-color: #FDFFC2; border-color: #C0D6E8}
        #Username_label, #Password_label {margin-left: 20px;}
        #Error_label {margin-left: 20px; color: red;}
        '''
        self.setStyleSheet(style)

        # Set alignment
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.UPatras_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.next_button)
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Logo Label
        self.UPatras_logo.resize(300, 93)
        self.UPatras_logo.setPixmap(self.CubeIQ_image)

        # Add widgets to layout
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.error_label)
        self.layout.addSpacing(50)
        self.layout.addLayout(button_layout)
        self.layout.addSpacing(50)
        self.layout.addWidget(self.UPatras_logo)

        self.setLayout(self.layout)

        # Connect buttons
        self.back_button.clicked.connect(self.hide)
        self.next_button.clicked.connect(self.validateCredentials)

        # Remove the title bar and disable closing the window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus)

    def create_connection(self):
        """ Create a database connection using settings from the JSON file"""
        config = load_config()
        try:
            connection = mysql.connector.connect(
                host=config["mysql_connection"]["mysql_host"],
                user=config["mysql_connection"]["mysql_user"],
                passwd="",
                database=config["mysql_connection"]["database_name"],
                port=config["mysql_connection"]["mysql_port_number"]
            )
            return connection
        except Error as e:
            self.error_label.setText(f"Connection error: {e}")
            return None

    def validateCredentials(self):
        # Handle the validation of credentials
        username = self.username_edit.text()
        password = self.password_edit.text()

        # Create a connection to the database
        connection = self.create_connection()
        if connection is None:
            return  # The error label is already updated in create_connection()

        query = """
            SELECT u.UserName, u.PasswordHash, r.RoleName
            FROM users u
            INNER JOIN userroles ur ON u.Id = ur.UserId
            INNER JOIN aspnetroles r ON ur.RoleId = r.Id
            WHERE u.UserName = %s AND u.PasswordHash = %s AND u.IsEnabled = TRUE AND r.RoleName IN ('Admin', 'NDAUser')
        """

        try:
            cursor = connection.cursor()
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                self.error_label.setText("")  # Clear error on successful login
                self.hide()
                self.NDA_menu.show()
            else:
                self.error_label.setText("Invalid credentials or insufficient permissions")
        except Error as e:
            self.error_label.setText(f"Query error: {e}")

    def closeEvent(self, event):
        self.hide()
