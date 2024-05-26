import json
import mysql.connector
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


def load_json_settings():
    """ Load settings from the JSON file. """
    with open('appsettings.json', 'r') as file:
        return json.load(file)


def get_database_connection():
    config = load_json_settings()
    db_config = config['mysql_connection']

    # Establish the connection using the parameters from appsettings.json
    return mysql.connector.connect(
        host=db_config["mysql_host"],
        user=db_config["mysql_user"],
        port=db_config["mysql_port_number"],
        database=db_config["database_name"]
    )


def fetch_denomination_thresholds():
    """ Fetches current counts and thresholds for each denomination from the database. """
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT denomination, count, min_threshold, float_threshold, max_threshold, full_threshold "
                       "FROM simulated_inventory")
        result = {row[0]: {'count': row[1], 'min': row[2], 'float': row[3], 'max': row[4], 'full': row[5]} for row in
                  cursor.fetchall()}
        return result
    except mysql.connector.Error as e:
        print(f"Error fetching denomination data: {e}")
    finally:
        connection.close()


def dispense_change(change_due, denominations_data):
    # Create a new dictionary that maps floating point representations of denominations to their data
    cleaned_denominations = {}
    for denom, data in denominations_data.items():
        # Remove the euro sign and convert euro denominations to float, keep cents as is for comparison
        if '€' in denom:
            value = float(denom.replace('€', '').strip())
        elif '¢' in denom:
            value = float(denom.replace('¢', '').strip()) / 100  # Convert cents to euros for uniformity
        cleaned_denominations[value] = data

    denominations = sorted(cleaned_denominations.keys(), reverse=True)

    change_dispensed = {}
    remaining_amount = change_due
    print("Adjusted denominations:", cleaned_denominations)

    for denom in denominations:
        denom_data = cleaned_denominations[denom]
        print(f"Checking denomination: {denom:.2f}€")
        if remaining_amount >= denom and denom_data['count'] > 0:
            max_count = int(min(remaining_amount // denom, denom_data['count']))
            if denom_data['count'] - max_count < denom_data['min']:
                continue  # Skip this denomination if it would breach the minimum threshold
            change_dispensed[f"{denom:.2f}€"] = max_count
            remaining_amount = round(remaining_amount - (denom * max_count), 2)
            if remaining_amount <= 0:
                break

    if remaining_amount > 0:
        print("Unable to dispense the exact amount due to threshold limitations.")
        return {}
    return change_dispensed


def update_database_with_dispensed(dispensed):
    """ Updates the database with the dispensed amounts. """
    connection = get_database_connection()
    print("These are the dispensed: ", dispensed)
    try:
        cursor = connection.cursor()
        # Transform the keys of the dictionary
        transformed_dispensed = {}
        for denomination, count in dispensed.items():
            if denomination.endswith('€'):
                value = float(denomination[:-1])  # Remove the '€' and convert to float
                if value.is_integer():
                    new_key = f"{int(value)} €"  # For whole euros, use 'x €'
                else:
                    # For cents, convert to cent value and use 'xx ¢'
                    cents_value = int(round(value * 100))
                    new_key = f"{cents_value} ¢"
                transformed_dispensed[new_key] = count

        # Perform the database update using the transformed keys
        for denomination, count in transformed_dispensed.items():
            cursor.execute("UPDATE simulated_inventory SET count = count - %s WHERE denomination = %s",
                           (count, denomination))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error updating database: {e}")
    finally:
        connection.close()


class PickupUI(QWidget):
    backClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(450)
        self.settings = load_json_settings()  # Load settings from JSON
        self.demo_pickup_amount = self.settings.get('DemoPickupAmount', 10.2)  # Default to 10.2 if not found

        # Import Images
        self.CubeIQ_image = QPixmap('Images/up_2017_logo_en_resized.png')

        # Add logo and title
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("Images/PayPoint_logo.png").scaledToWidth(70))
        self.title = QLabel("Unlock Action")
        self.OTP_text = QLabel("Use received One-Time-Password")

        # Create layout
        self.layout = QVBoxLayout()

        # OTP_label
        self.OTP_label = QLabel("OTP")

        # OTP field
        self.OTP_input = QLineEdit()

        # Error Label
        self.error_label = QLabel()

        # Buttons
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")

        # Logo Image
        self.UPatras_logo = QLabel()

        # Waiting Dispense state

        # Labels
        self.PayPoint_logo = QLabel()
        self.PayPoint_logo.setPixmap(QPixmap('Images/PayPoint_full_logo.png'))
        self.UPatras_logo_resized = QLabel()
        self.UPatras_logo_resized.setPixmap(QPixmap('Images/up_2017_logo_en_resized_150x47.png'))
        self.header_label = QLabel("Pickup Cash")
        self.info_label = QLabel(f"Requested pickup cash amount €{self.demo_pickup_amount:.2f}\nClick the Start "
                                 "button to commence dispensing...")

        # Buttons
        self.exit_button = QPushButton("Exit")
        self.start_button = QPushButton("Start")

        # Dispensing State
        self.dispensing_label = QLabel(f"Dispensed cash amount €{self.demo_pickup_amount:.2f}"
                                       f"\n\n {'{: >5}'}...click the button to exit")

        # Create and configure the timer
        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # 5000 milliseconds = 5 seconds
        self.timer.setSingleShot(True)  # Ensures the timer only triggers once
        self.timer.timeout.connect(self.final_rebuild_waiting_dispense_layout)

        self.setupUI()

    def setupUI(self):
        # Set object names
        self.back_button.setObjectName("Back_button")
        self.next_button.setObjectName("Next_button")
        self.exit_button.setObjectName("Exit_button")
        self.start_button.setObjectName("Start_button")
        self.title.setObjectName("Title")
        self.OTP_text.setObjectName("OTP_Text")
        self.OTP_input.setObjectName("OTP_Input")
        self.OTP_label.setObjectName("OTP_Label")
        self.header_label.setObjectName("Pickup_Cash_Label")
        self.info_label.setObjectName("Dispensing_Info")
        self.dispensing_label.setObjectName("Dispensing_Label")

        # Set CSS of Pickup UI
        style = '''
        QWidget {
            background: white;
        }
         
        QPushButton#Back_button, #Exit_button {
            background-color: #31363F;   
            border-radius: 4px;   
            border: 0;   
            box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   
            box-sizing: border-box;   
            color: #fff;   
            cursor: pointer;   
            display: inherit;   
            font-family: "Space Grotesk",
            -apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji",
            "Segoe UI Symbol";   
            font-size: 16px;   
            font-weight: 700;   
            line-height: 24px;   
            margin: 0;   
            min-height: 40px;   
            max-width: 100px; 
            position: relative; 
            text-align: center;   
            user-select: none;   
            -webkit-user-select: none;   
            touch-action: manipulation;   
            vertical-align: baseline;   
            transition: all .2s cubic-bezier(.22, .61, .36, 1); 
        } 
        
        QPushButton:hover {   
            background-color: #065dd8;   
            transform: translateY(-2px); 
        } 
        
        QPushButton#Next_button, #Start_button {
            background-color: #0a6bff;   
            border-radius: 4px;  
            border: 0;   
            box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   
            box-sizing: border-box;   
            color: #fff;   
            cursor: pointer;   
            display: inherit;   
            font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",
            Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   
            font-size: 16px;  
            font-weight: 700;   
            line-height: 24px;   
            margin: 0;   
            min-height: 40px;   
            max-width: 100px; 
            position: relative; 
            text-align: center;   
            user-select: none;   
            -webkit-user-select: none;   
            touch-action: manipulation;   
            vertical-align: baseline;   
            transition: all .2s cubic-bezier(.22, .61, .36, 1); 
        }
         
        QPushButton:hover {   
            background-color: #065dd8;   
            transform: translateY(-2px); 
        }
        
        QLabel#Title {
            font-size: 22px;
        }
        
        QLabel#OTP_Text {
            font-size: 14px;
        }
        
        QLineEdit {
            background-color: #f0f0f0; 
            border: 2px solid #ccc; 
            border-radius: 8px; 
            padding: 6px 12px; 
            font-size: 16px; 
            color: #333; 
            margin-left: 20px; 
            margin-right: 20px;
        }
        
        #OTP_Label {
            margin-left: 20px;
        }
        
        QLineEdit:focus { 
                background-color: #FDFFC2; 
                border-color: #C0D6E8
        }
        
        #Error_label {
            margin-left: 20px; 
            color: red;
        }
        
        #Pickup_Cash_Label {
            background-color: #0011ff; 
            color: white; 
            padding: 10px; 
            font-size: 20px;
        }
        
        #Dispensing_Info, #Dispensing_Label {
            font-size: 18px
        }
        '''
        self.setStyleSheet(style)

        # Set alignment
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.UPatras_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.OTP_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.next_button)

        # Logo Label
        self.UPatras_logo.resize(300, 93)
        self.UPatras_logo.setPixmap(self.CubeIQ_image)

        # Add widgets to layout
        self.layout.addWidget(self.logo)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.title)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.OTP_text)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.OTP_label)
        self.layout.addWidget(self.OTP_input)
        self.layout.addSpacing(30)
        self.layout.addLayout(button_layout)
        self.layout.addSpacing(100)
        self.layout.addWidget(self.UPatras_logo)

        self.setLayout(self.layout)

        # Button click events
        self.back_button.clicked.connect(self.onBackClicked)
        self.next_button.clicked.connect(self.transition_to_state_waiting_dispense)

        self.exit_button.clicked.connect(self.onBackClicked)
        self.start_button.clicked.connect(self.transition_to_state_init_dispense)

        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.start_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Remove the title bar and disable closing the window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus)

    def transition_to_state_waiting_dispense(self):
        self.hide_layout_contents(self.layout)
        self.setMinimumWidth(800)

        # Ensure elements are not only hidden but also managed correctly in layouts
        # Clear and rebuild the layout with necessary widgets
        self.rebuild_waiting_dispense_layout()

    def rebuild_waiting_dispense_layout(self):
        # Layout for header
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.PayPoint_logo, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.UPatras_logo_resized, alignment=Qt.AlignmentFlag.AlignRight)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.exit_button)
        button_layout.addSpacing(150)
        button_layout.addWidget(self.start_button)

        self.layout.addLayout(header_layout)
        self.layout.addSpacing(150)
        self.layout.addWidget(self.info_label)
        self.layout.addSpacing(150)
        self.layout.addLayout(button_layout)

        self.PayPoint_logo.show()
        self.header_label.show()
        self.UPatras_logo_resized.show()
        self.info_label.show()
        self.exit_button.show()
        self.start_button.show()

    def final_rebuild_waiting_dispense_layout(self):
        self.hide_layout_contents(self.layout)
        self.setMinimumWidth(800)
        # Fetch denomination data and thresholds
        denomination_data = fetch_denomination_thresholds()

        # Calculate change
        dispensed_change = dispense_change(self.demo_pickup_amount, denomination_data)

        # Check if the change was successfully calculated
        if not dispensed_change:
            self.dispensing_label.setText("Unable to process the dispense due to insufficient denominations available.")
        else:
            # Display dispensed amount and update the database accordingly
            update_database_with_dispensed(dispensed_change)
            self.dispensing_label.setText(
                f"Dispensed cash amount €{self.demo_pickup_amount}\n\n{"": <5}...click the button to exit")

        # Layout for header
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.PayPoint_logo, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.UPatras_logo_resized, alignment=Qt.AlignmentFlag.AlignRight)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.exit_button)
        button_layout.addSpacing(150)
        button_layout.addWidget(self.start_button)

        self.layout.addLayout(header_layout)
        self.layout.addSpacing(150)
        self.layout.addWidget(self.info_label)
        self.layout.addSpacing(100)
        self.layout.addWidget(self.dispensing_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addSpacing(150)
        self.layout.addLayout(button_layout)

        self.PayPoint_logo.show()
        self.header_label.show()
        self.UPatras_logo_resized.show()
        self.info_label.show()
        self.exit_button.show()
        self.dispensing_label.show()

    def transition_to_state_init_dispense(self):
        """ Transition to the state that occurs after pressing the start button. """
        # Hide the start button as it's no longer needed in this phase
        self.start_button.hide()

        # Start the timer
        self.timer.start()

    def hide_layout_contents(self, layout):
        """Recursively hides all widgets and sub-layouts within a given layout and removes spacers."""
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().hide()  # Hide the widget
            elif item.layout():
                self.hide_layout_contents(item.layout())  # Recursively hide contents of sub-layouts
            elif item.spacerItem():
                layout.removeItem(item)  # Remove the spacer item from the layout

    def resetUI(self):
        """ Resets the UI elements to their initial states for OTP input. """
        self.hide_layout_contents(self.layout)  # Hide all current contents

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.next_button)

        # Rebuild the initial layout
        self.layout.addWidget(self.logo)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.title)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.OTP_text)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.OTP_label)
        self.layout.addWidget(self.OTP_input)
        self.layout.addSpacing(30)
        self.layout.addLayout(button_layout)
        self.layout.addSpacing(100)
        self.layout.addWidget(self.UPatras_logo)

        # Show necessary elements
        self.logo.show()
        self.title.show()
        self.OTP_text.show()
        self.OTP_label.show()
        self.OTP_input.show()
        self.back_button.show()
        self.next_button.show()
        self.UPatras_logo.show()

        # Clear any text from the OTP input field
        self.OTP_input.clear()

        # Clear any error messages
        self.error_label.setText("")

        self.setMinimumWidth(450)

    def onBackClicked(self):
        # Reset the UI to its initial state before hiding
        self.resetUI()
        self.hide()
        self.backClicked.emit()  # Emit the signal when back is clicked
