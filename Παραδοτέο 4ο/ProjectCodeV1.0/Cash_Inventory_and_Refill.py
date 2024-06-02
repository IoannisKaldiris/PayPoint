import json
import mysql.connector
import socket
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QGuiApplication, QCursor


def get_database_connection():
    config = load_config()
    db_config = config['mysql_connection']

    # Establish the connection using the parameters from appsettings.json
    return mysql.connector.connect(
        host=db_config["mysql_host"],
        user=db_config["mysql_user"],
        port=db_config["mysql_port_number"],
        database=db_config["database_name"]
    )


def parse_denomination(denomination):
    if '€' in denomination:
        return float(denomination.strip(' €'))
    elif '¢' in denomination:
        return float(denomination.strip(' ¢')) / 100  # Convert cents to euros
    else:
        raise ValueError(f"Invalid currency denomination: {denomination}")


def load_config():
    with open('appsettings.json', 'r') as file:
        data = json.load(file)
    data["FLevelThres"] = json.loads(data["FLevelThres"])  # Parse the FLevelThres JSON string into a dictionary
    return data


def denomination_to_index(denomination):
    # This function needs to be implemented to map denominations to their respective indices.
    # Assuming the denominations are from "1¢" to "500€" with corresponding indices 0 to 14.
    # Implement this based on your actual data.
    denominations = ["1 ¢", "2 ¢", "5 ¢", "10 ¢", "20 ¢", "50 ¢", "1 €", "2 €", "5 €", "10 €", "20 €", "50 €", "100 €",
                     "200 €",
                     "500 €"]
    return denominations.index(denomination)


def content_CashBox():
    return 0.00


def content_Loader():
    return 0.00


class ServerController(QObject):
    update_denomination_signal = pyqtSignal(str, float)


class ServerThread(QThread):
    def __init__(self, host, port, controller, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.running = True
        self.controller = controller

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()
            print("Server is listening...")
            while self.running:
                client_socket, addr = server.accept()
                print("Connected by", addr)
                with client_socket:
                    while self.running:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        print('These are the data received: ', data.decode())
                        label, value = data.decode().strip().split(':')
                        denomination_amount = float(value.strip())
                        self.controller.update_denomination_signal.emit(f"{denomination_amount} €", 1)
                        client_socket.sendall(b"Data received and processed")  # Acknowledge
                        # self.controller.update_denomination_signal.emit(denomination, float(amount))

    def stop(self):
        self.running = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.close()


class Denomination_info(QWidget):
    refresh_complete_signal = pyqtSignal()

    def __init__(self, denomination="", is_BNR=False, is_CashBox=0, is_Loader=0):
        super().__init__()
        if is_CashBox == 0 and is_Loader == 0:
            self.denomination = denomination
            self.is_BNR = is_BNR
            # Compute the index from denomination
            index = denomination_to_index(denomination)

            # Parse the threshold levels from the JSON configuration
            json_data = load_config()
            thresholds = json_data["FLevelThres"]

            # Set thresholds based on the computed index
            self.min_notes_threshold = thresholds["Min"][index]
            self.float_value_threshold = thresholds["Float"][index]
            self.max_notes_threshold = thresholds["Max"][index]
            self.full_notes_threshold = thresholds["Full"][index]

            # Labels
            if self.is_BNR:
                label_text = "Notes"
            else:
                label_text = "Coins"

            self.denomination_label = QLabel(f"{label_text}: {self.denomination}")  # Denomination Label
            self.current_value_display = QLabel(
                f"€{self.current_notes_coins() * parse_denomination(self.denomination):.2f}")  # Current value display
            self.notes_count_display = QLabel(f"{self.current_notes_coins()} {label_text.lower()}")  # Current notes
            # count
            self.status_color = QFrame()  # Status bar color indicator
            try:
                self.percentage_indicator = QLabel(
                    f"at {int(round((self.current_notes_coins() / self.full_notes_threshold), 2) * 100)} %")
            except ZeroDivisionError:
                self.percentage_indicator = QLabel("Empty 0 %")

            # Threshold labels
            self.thresholds_label = QLabel("Thresholds")
            self.full_notes_info_0 = QLabel("Full")
            self.full_notes_info_1 = QLabel(":")
            self.full_notes_info_2 = QLabel(f"{self.full_notes_threshold}")

            self.max_notes_info_0 = QLabel("Max")
            self.max_notes_info_1 = QLabel(":")
            self.max_notes_info_2 = QLabel(f"{self.max_notes_threshold}")

            self.float_notes_info_0 = QLabel("Float")
            self.float_notes_info_1 = QLabel(":")
            self.float_notes_info_2 = QLabel(f"{self.float_value_threshold}")

            self.min_notes_info_0 = QLabel("Min")
            self.min_notes_info_1 = QLabel(":")
            self.min_notes_info_2 = QLabel(f"{self.min_notes_threshold}")

            # Layout
            self.layout = QVBoxLayout()

            self.init_ui_Denominations()
        elif is_CashBox == 1:
            self.denomination = denomination
            self.is_BNR = is_BNR

            # Layout
            self.layout = QVBoxLayout()

            # Labels
            self.denomination_label = QLabel("CashBox")
            self.current_value_display = QLabel(
                f"€{content_CashBox():.2f}")  # Current value display
            self.notes_count_display = QLabel(f"{self.current_notes_coins()} notes")  # Current notes count

            self.init_ui_CashBox_Loader()
        elif is_Loader == 1:
            self.denomination = denomination
            self.is_BNR = is_BNR

            # Layout
            self.layout = QVBoxLayout()

            # Labels
            self.denomination_label = QLabel("Loader")
            self.current_value_display = QLabel(
                f"€{content_Loader():.2f}")  # Current value display
            self.notes_count_display = QLabel(f"{self.current_notes_coins()} notes")  # Current notes count
            self.init_ui_CashBox_Loader()

    def init_ui_Denominations(self):
        # Set object names
        self.denomination_label.setObjectName("Heading_Label")
        self.current_value_display.setObjectName("Display_Value")
        self.notes_count_display.setObjectName("Display_Count")
        self.percentage_indicator.setObjectName("Percentage_Count")
        self.thresholds_label.setObjectName("Threshold_Header")
        self.full_notes_info_0.setObjectName("Threshold_name")
        self.full_notes_info_1.setObjectName("Threshold")
        self.full_notes_info_2.setObjectName("Threshold")
        self.max_notes_info_0.setObjectName("Threshold_name")
        self.max_notes_info_1.setObjectName("Threshold")
        self.max_notes_info_2.setObjectName("Threshold")
        self.float_notes_info_0.setObjectName("Threshold_name")
        self.float_notes_info_1.setObjectName("Threshold")
        self.float_notes_info_2.setObjectName("Threshold")
        self.min_notes_info_0.setObjectName("Threshold_name")
        self.min_notes_info_1.setObjectName("Threshold")
        self.min_notes_info_2.setObjectName("Threshold")

        style = '''
            QLabel#Heading_Label {
                color: #4e71e4;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }
            
            QLabel#Display_Value, QLabel#Percentage_Count {
                font-weight: bold;
                font-size: 18px;
            }
            
            QLabel#Display_Count {
                font-size: 18px;
            }
            
            QLabel#Threshold_name {
                font-size: 14px;
                font-family: "Gill Sans", sans-serif;
                width: 25px;
            }
            
            QLabel#Threshold {
                font-size: 14px;
                font-family: "Gill Sans", sans-serif;
            }
        '''
        self.setStyleSheet(style)
        # Adjust the label color accordingly
        self.status_color.setStyleSheet("background-color: red; border: 2px solid grey;")

        # Set custom layout
        layout_full = QHBoxLayout()
        layout_max = QHBoxLayout()
        layout_float = QHBoxLayout()
        layout_min = QHBoxLayout()

        layout_full.addWidget(self.full_notes_info_0, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_full.addWidget(self.full_notes_info_1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_full.addWidget(self.full_notes_info_2, alignment=Qt.AlignmentFlag.AlignRight)

        layout_max.addWidget(self.max_notes_info_0, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_max.addWidget(self.max_notes_info_1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_max.addWidget(self.max_notes_info_2, alignment=Qt.AlignmentFlag.AlignRight)

        layout_float.addWidget(self.float_notes_info_0, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_float.addWidget(self.float_notes_info_1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_float.addWidget(self.float_notes_info_2, alignment=Qt.AlignmentFlag.AlignRight)

        layout_min.addWidget(self.min_notes_info_0, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_min.addWidget(self.min_notes_info_1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_min.addWidget(self.min_notes_info_2, alignment=Qt.AlignmentFlag.AlignRight)

        # Set specific dimensions for the status color
        self.status_color.setFixedSize(30, 30)

        # Update the Status Color and set the initial color based on current notes/coins
        self.update_status_color()

        # Main Layout
        self.layout.addWidget(self.denomination_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.current_value_display, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.notes_count_display, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_color, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.percentage_indicator, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.thresholds_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(layout_full)
        self.layout.addLayout(layout_max)
        self.layout.addLayout(layout_float)
        self.layout.addLayout(layout_min)

        self.setLayout(self.layout)

    def init_ui_CashBox_Loader(self):
        # Set object names
        self.denomination_label.setObjectName("Heading_Label")
        self.current_value_display.setObjectName("Display_Value")
        self.notes_count_display.setObjectName("Display_Count")

        style = '''
            QLabel#Heading_Label {
                color: #4e71e4;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
            }

            QLabel#Display_Value, QLabel#Percentage_Count {
                font-weight: bold;
                font-size: 18px;
            }

            QLabel#Display_Count {
                font-size: 18px;
            }
        '''
        self.setStyleSheet(style)

        # Main Layout
        self.layout.addWidget(self.denomination_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.current_value_display, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.notes_count_display, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

    def current_notes_coins(self):
        db = get_database_connection()
        cursor = db.cursor()

        query = "SELECT count FROM simulated_inventory WHERE denomination = %s"
        cursor.execute(query, (self.denomination,))
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result[0] if result else 0

    def add_cash(self, count):
        db = get_database_connection()
        cursor = db.cursor()
        try:
            query = "UPDATE simulated_inventory SET count = count + %s WHERE denomination = %s"
            cursor.execute(query, (count, self.denomination))
            db.commit()
        finally:
            cursor.close()
            db.close()

        self.refresh_display()

    def update_status_color(self):
        current_count = self.current_notes_coins()  # Retrieve the current count of notes/coins

        # Determine the color based on threshold conditions
        if current_count >= self.full_notes_threshold:
            color = "red"  # Full or overfull
        elif self.max_notes_threshold <= current_count < self.full_notes_threshold:
            color = "#640D6B"  # Between max and full
        elif self.float_value_threshold <= current_count < self.max_notes_threshold:
            color = "#0A6847"  # Between float and max
        elif self.min_notes_threshold <= current_count < self.float_value_threshold:
            color = "#FFC55A"  # Between min and float
        else:
            color = "red"  # Below min

        # Set the color of the status bar
        self.status_color.setStyleSheet(f"background-color: {color}; border: 2px solid grey;")

    def refresh_display(self):
        db = get_database_connection()
        cursor = db.cursor()
        try:
            query = "SELECT count FROM simulated_inventory WHERE denomination = %s"
            cursor.execute(query, (self.denomination,))
            result = cursor.fetchone()
            if result:
                new_count = result[0]
                # Update the display label based on the new count
                self.current_value_display.setText(f"€{new_count * parse_denomination(self.denomination):.2f}")
                self.notes_count_display.setText(f"{new_count} {self.denomination_label.text().split(':')[0].lower()}")
                try:
                    self.percentage_indicator.setText(
                        f"at {int(round((new_count / self.full_notes_threshold), 2) * 100)} %")
                except ZeroDivisionError:
                    self.percentage_indicator = QLabel("Empty 0 %")
        finally:
            cursor.close()
            db.close()
        self.update_status_color()
        self.refresh_complete_signal.emit()  # Emit signal after refreshing the display


class CashInventoryUI(QWidget):
    backClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Define the Tread in order to receive signals to update the CashInventory
        self.server_thread = None
        self.controller = ServerController()

        # Layout
        self.layout = QVBoxLayout()

        # Import Images
        self.PayPoint_logo = QLabel()
        self.PayPoint_logo.setPixmap(QPixmap('Images/PayPoint_full_logo.png'))
        self.CubeIQ_image = QLabel()
        self.CubeIQ_image.setPixmap(QPixmap('Images/up_2017_logo_en_resized_150x47.png'))

        # Info Label
        self.header_input_label = QLabel("Cash accepted is €0.00")

        # BNR denominations
        self.euro_500_denomination = Denomination_info(denomination='5 €', is_BNR=True)
        self.euro_1000_denomination = Denomination_info(denomination='10 €', is_BNR=True)
        self.euro_2000_denomination = Denomination_info(denomination='20 €', is_BNR=True)
        self.euro_5000_denomination = Denomination_info(denomination='50 €', is_BNR=True)
        self.euro_10000_denomination = Denomination_info(denomination='100 €', is_BNR=True)
        self.euro_20000_denomination = Denomination_info(denomination='200 €', is_BNR=True)
        self.euro_50000_denomination = Denomination_info(denomination='500 €', is_BNR=True)
        self.CashBox_label = Denomination_info(is_CashBox=True)
        self.Loader_label = Denomination_info(is_Loader=True)

        # CLS denominations
        self.cent_1_denomination = Denomination_info(denomination='1 ¢', is_BNR=False)
        self.cent_2_denomination = Denomination_info(denomination='2 ¢', is_BNR=False)
        self.cent_5_denomination = Denomination_info(denomination='5 ¢', is_BNR=False)
        self.cent_10_denomination = Denomination_info(denomination='10 ¢', is_BNR=False)
        self.cent_20_denomination = Denomination_info(denomination='20 ¢', is_BNR=False)
        self.cent_50_denomination = Denomination_info(denomination='50 ¢', is_BNR=False)
        self.cent_100_denomination = Denomination_info(denomination='1 €', is_BNR=False)
        self.cent_200_denomination = Denomination_info(denomination='2 €', is_BNR=False)

        # Buttons
        self.Exit_button = QPushButton("Exit")
        # self.Exit_button.hide()
        self.total_cash_inventory = QLabel("Total cash inventory is €0.00")
        self.Done_button = QPushButton("Done")

        self.setupUI()
        self.center()

    def setupUI(self):
        # Set object name
        self.header_input_label.setObjectName("Header_Input")
        self.Exit_button.setObjectName("Exit_Button")
        self.Done_button.setObjectName("Done_Button")
        self.total_cash_inventory.setObjectName("Total_Cash_Label")

        # Set CSS of window
        style = '''QWidget {background: white;} 
        
        QLabel#Header_Input { background: #0011fe; color: white; font-size: 22px;
        font-weight: bold; min-width: 300px; padding-top: 20px; 
        padding-bottom: 20px;
        padding-left: 200px; padding-right: 200px; align-items: center;} 
        
        QLabel#Total_Cash_Label {
            font-size: 20px;
        }
        
        QPushButton#Exit_Button {
            background-color: #0c6efd;
            max-width: 150px;
            border-radius: 4px;
            border: 0;
            box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;
            box-sizing: border-box;
            color: #fff;
            display: inherit;
            font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,
            "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
            font-size: 18px; 
            font-weight: 700;   
            line-height: 24px;   
            margin: 0;   
            min-height: 50px;
            position: relative; 
            text-align: center;   
            user-select: none;   
            -webkit-user-select: none;
            touch-action: manipulation;   
            vertical-align: baseline;
            margin-left: 250px;
        }
        
        QPushButton#Done_Button {
            background-color: #0c6efd;
            max-width: 150px;
            border-radius: 4px;
            border: 0;
            box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;
            box-sizing: border-box;
            color: #fff;
            display: inherit;
            font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,
            "Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
            font-size: 18px; 
            font-weight: 700;   
            line-height: 24px;   
            margin: 0;   
            min-height: 50px;
            position: relative; 
            text-align: center;   
            user-select: none;   
            -webkit-user-select: none;
            touch-action: manipulation;   
            vertical-align: baseline;
            margin-right: 250px;
        }'''
        self.setStyleSheet(style)

        # Header Layout | First row
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.PayPoint_logo, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.header_input_label, alignment=Qt.AlignmentFlag.AlignCenter, stretch=100)
        header_layout.addWidget(self.CubeIQ_image)

        # BNR denomination + CashBox + Loader | Second row
        BNR_layout = QHBoxLayout()
        BNR_layout.addWidget(self.euro_500_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        BNR_layout.addWidget(self.euro_1000_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        BNR_layout.addWidget(self.euro_2000_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        BNR_layout.addWidget(self.euro_5000_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        BNR_layout.addWidget(self.euro_10000_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        BNR_layout.addWidget(self.euro_50000_denomination, alignment=Qt.AlignmentFlag.AlignLeft)

        loader_cashBox_layout = QVBoxLayout()
        loader_cashBox_layout.addWidget(self.CashBox_label)
        loader_cashBox_layout.addWidget(self.Loader_label)

        BNR_layout.addLayout(loader_cashBox_layout)

        # CLS denominations | Third row
        CLS_layout = QHBoxLayout()
        CLS_layout.addWidget(self.cent_1_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_2_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_5_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_10_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_20_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_50_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_100_denomination, alignment=Qt.AlignmentFlag.AlignLeft)
        CLS_layout.addWidget(self.cent_200_denomination, alignment=Qt.AlignmentFlag.AlignLeft)

        # Footer Layout | Last row
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.Exit_button)
        footer_layout.addSpacing(50)
        footer_layout.addWidget(self.total_cash_inventory, alignment=Qt.AlignmentFlag.AlignCenter)
        footer_layout.addSpacing(50)
        footer_layout.addWidget(self.Done_button)

        self.Exit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.Done_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Add click events to done and exit buttons
        self.Exit_button.clicked.connect(self.return_to_main_menu)
        self.Done_button.clicked.connect(self.stop_server)

        # Remove the title bar and disable closing the window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus)

        # Update the value of the total cash inventory except from the content of CB and Loader
        self.update_total_cash_inventory_from_display()

        # Update the UI from the input from the socket client
        self.controller.update_denomination_signal.connect(self.update_denomination)

        # Final UI layout
        self.layout.addLayout(header_layout)
        self.layout.addLayout(BNR_layout)
        self.layout.addSpacing(10)
        self.layout.addLayout(CLS_layout)
        self.layout.addLayout(footer_layout)

        self.setLayout(self.layout)

        # Connect each Denomination_info's refresh signal to the CashInventoryUI update method
        for widget in self.findChildren(Denomination_info):
            widget.refresh_complete_signal.connect(self.update_total_cash_inventory_from_display)

    def center(self):
        # Get the geometry of the primary screen
        screen_geometry = QGuiApplication.primaryScreen().geometry()

        # Calculate the center point of the screen
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2

        # Convert x and y to integers
        x = int(x)
        y = int(y)

        # Set the window position to the center
        self.move(100, 100)

    def return_to_main_menu(self):
        self.hide()
        self.backClicked.emit()

    def update_total_cash_inventory_from_display(self):
        total_value = 0.0

        # List of all Denomination_info widgets in the UI
        denomination_widgets = [
            self.euro_500_denomination, self.euro_1000_denomination, self.euro_2000_denomination,
            self.euro_5000_denomination, self.euro_10000_denomination, self.euro_50000_denomination,
            self.cent_1_denomination, self.cent_2_denomination, self.cent_5_denomination,
            self.cent_10_denomination, self.cent_20_denomination, self.cent_50_denomination,
            self.cent_100_denomination, self.cent_200_denomination
        ]

        # Calculate total value from each widget's display
        for widget in denomination_widgets:
            # Extract the numeric value from the label text (format "€X.XX")
            value_text = widget.current_value_display.text().strip('€')
            try:
                total_value += float(value_text)
            except ValueError:
                continue  # In case the text is not a valid float, skip it

        # Update the QLabel text to reflect the total cash inventory
        self.total_cash_inventory.setText(f"Total cash inventory is €{total_value:.2f}")

    def start_server(self):
        if not self.server_thread:
            self.server_thread = ServerThread('127.0.0.1', 65432, self.controller)
            self.server_thread.start()

    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None

    def update_denomination(self, denomination, amount):
        # Standardize the incoming denomination format
        try:
            denomination_value = float(denomination.split(' ')[0])
            if denomination_value < 1:  # Assuming values less than 1 are in cents
                denomination = f"{int(denomination_value * 100)} ¢"
            else:
                # Use integer formatting for whole euros, otherwise show two decimal places
                denomination = f"{int(denomination_value)} €" if denomination_value.is_integer() else f"{denomination_value:.2f} €"
        except ValueError:
            print("Error converting denomination to float")
            return

        # Find the widget by denomination
        for widget in self.findChildren(Denomination_info):
            # Here I need to add the total cash inserted
            if widget.denomination == denomination:
                widget.add_cash(amount)

    def showEvent(self, event):
        self.start_server()

    def hideEvent(self, event):
        self.stop_server()
        super().hideEvent(event)
