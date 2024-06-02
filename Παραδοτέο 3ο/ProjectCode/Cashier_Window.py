import messages
import mysql.connector
import json
from mysql.connector import Error
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainterPath, QRegion, QCursor
from settings import current_language_index


def load_config():
    """Load configuration from a JSON file."""
    with open('appsettings.json', 'r') as file:
        config = json.load(file)
    return config


def log_transaction(user_id, transaction_type, description, total_amount, total_inserted_amount, total_dispensed_amount,
                    status, port_number):
    """Log transactions to the database using configurations loaded from JSON."""
    config = load_config()  # Load the configuration from the JSON file

    try:
        # Setup MySQL connection using configurations from JSON
        connection = mysql.connector.connect(
            host=config['mysql_connection']['mysql_host'],
            user=config['mysql_connection']['mysql_user'],
            passwd="",  # Assuming password is not set, modify if it has a password.
            database=config['mysql_connection']['database_name'],
            port=config['mysql_connection']['mysql_port_number']
        )
        cursor = connection.cursor()
        sql_query = """
        INSERT INTO TransactionLog (UserId, TransactionType, Description, TotalAmount, TotalInsertedAmount, 
        DispensedAmount, Status) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_query, (user_id, transaction_type, description, total_amount, total_inserted_amount,
                                   total_dispensed_amount, status))
        connection.commit()
        print(messages.LOG_TRANSACTION_SUCCESS[current_language_index])
    except Error as e:
        print(messages.LOG_TRANSACTION_FAILED[current_language_index] + ' ' + e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def dispense_change(change_due):
    # Euro denominations available for change
    denominations = [500, 200, 100, 50, 20, 10, 5, 2, 1, 0.50, 0.20, 0.10, 0.05, 0.02, 0.01]
    change_dispensed = {}
    remaining_amount = change_due

    for denom in denominations:
        if remaining_amount >= denom:
            count = int(remaining_amount // denom)
            change_dispensed[denom] = count
            remaining_amount = round(remaining_amount - (denom * count), 2)
            if remaining_amount <= 0:
                break

    return change_dispensed


class CashierWindow(QWidget):
    def __init__(self, total_amount, mode=2):
        super().__init__()
        self.config = load_config()  # Load and store the configuration from appsettings.json
        self.total_amount = total_amount  # Total amount from the initialization of class
        self.float_total_amount = float(total_amount)  # Make this amount into float for the functions
        self.total_dispense_amount = 0.0  # Total final dispense amount for the log file
        self.current_paid = 0.0  # Track the total paid amount
        self.cash_in_amount_str = ""
        self.transaction_active = False  # Have a state where I can know if the transaction is active or not
        self.manually_finalized = False  # State to check if finalized manually

        # Labels of Cashier Window
        self.label_total_amount = QLabel(
            messages.TOTAL_AMOUNT_MSG[current_language_index] + str(format(self.float_total_amount, ".2f")) + '€', self)
        self.label_cash_in = QLabel(messages.ALREADY_PAID_MSG[current_language_index] + '0.00€', self)
        self.label_cash_out = QLabel(
            messages.BALANCE_MSG[current_language_index] + str(format(self.float_total_amount, ".2f")) + '€', self)
        self.label_collected_label = QLabel(messages.COLLECTED_MSG[current_language_index], self)
        self.label_collected_denomination = QLabel(self)
        self.label_dispensed_label = QLabel(messages.DISPENSED_MSG[current_language_index], self)
        self.label_dispensed_denomination = QLabel(self)
        self.label_info_user = QLabel(self)

        # Button of Cashier Window
        self.cancel_button = QPushButton('Cancel', self)
        self.stop_button = QPushButton('Stop', self)
        self.ok_button = QPushButton('OK', self)

        self.initUI(mode)

    def initUI(self, mode):
        self.setFixedSize(350, 650)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Make window frameless
        # self.setWindowFlags(Qt.WindowType.Tool)

        # Make Widget round on the edges
        path = QPainterPath()
        radius = 40.0
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        self.center_window()

        # Set Widget style
        self.setObjectName('Cashier_Window')
        self.setStyleSheet("""#Cashier_Window {background: #002025;}""")

        # Set Widget Labels and style
        self.setup_labels()

        # Create Widget buttons
        self.setup_buttons(mode)
        self.show()

    def setup_labels(self):
        self.label_total_amount.setMinimumWidth(200)
        self.label_total_amount.setStyleSheet('color: white; font-weight:bold; font-size: 20px')
        self.label_total_amount.move(80, 50)

        self.label_cash_in.setMinimumWidth(200)
        self.label_cash_in.setStyleSheet('color: white; font-weight:bold; font-size: 20px')
        self.label_cash_in.move(80, 150)

        self.label_cash_out.setMinimumWidth(200)
        self.label_cash_out.setStyleSheet('color: white; font-weight:bold; font-size: 20px')
        self.label_cash_out.move(80, 250)

        self.label_info_user.setStyleSheet('color: white; font-weight:bold; font-size: 20px')
        self.label_info_user.move(40, 500)
        self.update_and_center_label(self.label_info_user, 'Waiting for cash deposit...')

        self.label_collected_label.move(5, 300)
        self.label_collected_label.setStyleSheet('color: white; font-size: 15px')
        self.label_collected_label.hide()

        self.label_collected_denomination.move(5, 320)
        self.label_collected_denomination.setStyleSheet('color: white; font-size: 15px')
        self.label_collected_denomination.setMinimumSize(100, 150)  # Set a minimum size
        self.label_collected_denomination.setWordWrap(True)  # Allow word wrapping if text is too long
        self.label_collected_denomination.hide()

        self.label_dispensed_label.move(210, 300)
        self.label_dispensed_label.setStyleSheet('color: white; font-size: 15px')
        self.label_dispensed_label.hide()

        self.label_dispensed_denomination.move(210, 320)
        self.label_dispensed_denomination.setMinimumSize(100, 150)  # Set a minimum size
        self.label_dispensed_denomination.setWordWrap(True)  # Allow word wrapping if text is too long
        self.label_dispensed_denomination.setStyleSheet('color: white; font-size: 15px')
        self.label_dispensed_denomination.hide()

    def setup_buttons(self, mode):
        # Cancel Button
        self.cancel_button.setObjectName('Cancel_Button')
        self.cancel_button.setStyleSheet(
            '#Cancel_Button {align-items: center; background-color: #FF2400; border-radius: .25rem; color: #fff; font-size: 20px; font-weight: 600; min-height: 35px; width: 80px;}'
        )
        self.cancel_button.move(200, 600) if mode != 1 else self.cancel_button.move(140, 600)
        self.cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_button.clicked.connect(self.cancel_transaction)

        # OK Button
        self.ok_button.setObjectName('OK_Button')
        self.ok_button.setStyleSheet(
            '#OK_Button {align-items: center; background-color: #33CEFF; border-radius: .25rem; color: #fff; font-size: 20px; font-weight: 600; min-height: 35px; width: 80px;}'
        )
        self.ok_button.move(140, 600)
        self.ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ok_button.clicked.connect(self.finalize_transaction)
        self.ok_button.hide()

        if mode != 1:
            self.stop_button.setObjectName('Stop_Button')
            self.stop_button.setStyleSheet(
                '#Stop_Button {align-items: center; background-color: #0BDA51; border-radius: .25rem; color: #fff; font-size: 20px; font-weight: 600; min-height: 35px; width: 80px;}')
            self.stop_button.move(80, 600)
            self.stop_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.stop_button.clicked.connect(self.stop_transaction)

    def center_window(self):
        # Access the screen from the application
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def deposit_update_labels(self, cash_in):
        try:
            # Convert cash_in to float if it's not already, and handle the exception if conversion fails
            cash_in_amount = float(cash_in) if isinstance(cash_in, str) else cash_in
        except ValueError:
            print("Invalid input for cash_in, must be a convertible to float")
            return

        self.cash_in_amount_str += "1 X " + str(format(cash_in_amount, ".2f")) + "€\n"

        # Show the hidden values
        self.label_collected_label.show()
        self.label_collected_denomination.show()
        self.label_dispensed_label.show()
        self.label_dispensed_denomination.show()

        # Update the total paid amount
        self.current_paid += cash_in_amount

        # Calculate the remaining balance
        balance_amount = self.float_total_amount - self.current_paid

        # Update the labels with the new data
        self.label_cash_in.setText(
            messages.ALREADY_PAID_MSG[current_language_index] + format(self.current_paid, ".2f") + '€')
        self.label_cash_out.setText(
            messages.BALANCE_MSG[current_language_index] + str(format(balance_amount, ".2f")) + '€')
        self.label_collected_denomination.setText(self.cash_in_amount_str)

        if balance_amount <= 0:
            self.cancel_button.hide()
            self.stop_button.hide()

            # Begin the Dispense Operation, when the balance is less than 0 meaning that I need dispense to complete the transaction
            if balance_amount < 0:
                if self.float_total_amount == 8.10:  # Just to show the use case without dispense available
                    self.update_and_center_label(self.label_info_user,
                                                 messages.NO_DISPENSE_AVAILABLE[current_language_index])
                    QTimer.singleShot(5000, lambda: self.start_dispensing(cancel_operation=1))
                else:  # Normal process with dispense available

                    # Calculate change to dispense
                    change_due = -balance_amount
                    change_dispensed = dispense_change(change_due)
                    # Format the change dispensed to display in the label
                    dispensed_text = '\n'.join(f"{count}x{denom}€" for denom, count in change_dispensed.items())

                    # Calculate the total dispensed amount
                    total_dispensed_amount = sum(denom * count for denom, count in change_dispensed.items())
                    self.total_dispense_amount = total_dispensed_amount
                    self.label_dispensed_denomination.setText(dispensed_text)
                    self.update_and_center_label(self.label_info_user,
                                                 messages.CASHBACK_FOR_CHANGE_MSG[current_language_index])

                    # Log the dispense
                    description = "Dispensing change"
                    transaction_status = "Completed"
                    log_transaction(3, "Dispense", description, self.total_amount, self.current_paid, total_dispensed_amount,
                                    transaction_status, self.config['mysql_connection']['mysql_port_number'])

                    QTimer.singleShot(5000, self.start_dispensing)
            else:  # case when there is no dispense: Balance == 0
                self.update_and_center_label(self.label_info_user, messages.THANK_YOU_MSG[current_language_index])
                QTimer.singleShot(5000, self.end_transaction)  # QTimer to handle delay before closing

    def update_and_center_label(self, label, text):
        # Set the new text to the label
        label.setText(text)

        # Adjust the label width to fit the text
        label.adjustSize()

        # Calculate the new x position to center the label
        new_x_position = (self.width() - label.width()) // 2

        # Get the current y position (to keep it vertically aligned as before)
        current_y_position = label.y()

        # Move the label to the new centered position
        label.move(new_x_position, current_y_position)

    def start_transaction(self):
        self.transaction_active = True

    def cancel_transaction(self):
        self.update_and_center_label(self.label_info_user, messages.CANCELLED_PAYMENT_MSG[current_language_index])
        self.cancel_button.hide()
        self.stop_button.hide()
        QTimer.singleShot(5000, lambda: self.start_dispensing(cancel_operation=1))

    def start_dispensing(self, cancel_operation=0):
        # Check if there are denominations to dispense
        if self.cash_in_amount_str and cancel_operation == 1:
            # Move collected denominations to dispensed
            dispensed_amount = sum(
                float(val.split(' X ')[1].replace('€', '')) for val in self.cash_in_amount_str.split('\n') if val)
            self.total_dispense_amount = dispensed_amount
            description = "Transaction cancelled"
            log_transaction(3, "Cancel", description, self.total_amount, self.current_paid, dispensed_amount, "Cancelled", self.config['mysql_connection']['mysql_port_number'])
            self.label_dispensed_denomination.setText(self.cash_in_amount_str)
            self.label_collected_denomination.setText("")

        self.update_and_center_label(self.label_info_user, messages.DISPENSING_CASH_MSG[current_language_index])

        # Schedule the end of the transaction
        QTimer.singleShot(5000, self.end_transaction)

    def stop_transaction(self):
        description = "Transaction stopped"
        log_transaction(3, "Stop", description, self.total_amount, self.current_paid, 0,
                        "Stopped", self.config['mysql_connection']['mysql_port_number'])
        self.update_and_center_label(self.label_info_user, messages.STOPPING_TRANSACTION_MSG[current_language_index])
        self.cancel_button.hide()
        self.stop_button.hide()
        QTimer.singleShot(6000, self.end_transaction)

    def end_transaction(self):
        # Show thank you message
        self.update_and_center_label(self.label_info_user, messages.THANK_YOU_MSG[current_language_index])
        self.transaction_active = False
        self.ok_button.show()

        # Schedule the finalization of the transaction
        QTimer.singleShot(5000, self.finalize_transaction)

    def finalize_transaction(self):
        if not self.manually_finalized:  # Only log if not already finalized manually. In reality that had happens is that the first time the function is triggered he is getting at the if not and the next time he it is already tru
            description = "Transaction finalized"
            log_transaction(3, "Finalize", description, self.total_amount, self.current_paid,
                            self.total_dispense_amount, "Completed", self.config['mysql_connection']['mysql_port_number'])

        self.manually_finalized = True  # Set the state to True to indicate manually finalization
        self.hide()  # Optionally close the window when transaction ends

    def reset_for_new_transaction(self, amount):
        self.total_amount = amount
        self.float_total_amount = float(amount)
        self.transaction_active = True
        self.total_dispense_amount = 0.0  # Total final dispense amount for the log file
        self.current_paid = 0.0  # Track the total paid amount
        self.cash_in_amount_str = ""
        self.manually_finalized = False  # State to check if finalized manually

        self.label_total_amount.setText(
            messages.TOTAL_AMOUNT_MSG[current_language_index] + str(format(self.float_total_amount, ".2f")) + '€')
        self.label_cash_in.setText(messages.ALREADY_PAID_MSG[current_language_index] + '0.00€')
        self.label_cash_out.setText(
            messages.BALANCE_MSG[current_language_index] + str(format(self.float_total_amount, ".2f")) + '€')
        self.update_and_center_label(self.label_info_user, messages.WAITING_FOR_DEPOSIT_MSG[current_language_index])

        self.cancel_button.show()
        self.stop_button.show()

        self.label_collected_label.hide()
        self.label_collected_denomination.hide()
        self.label_dispensed_label.hide()
        self.label_dispensed_denomination.hide()
