import sys
import requests
from PyQt6.QtWidgets import QLabel, QWidget, QMainWindow, QPushButton, QLineEdit, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QDoubleValidator, QCursor, QValidator, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set Main Window Title
        self.setWindowTitle('Software Engineer v0.1')

        # Create Image Labels to add the Images
        self.label_image_1 = QLabel(self)
        self.label_image_2 = QLabel(self)
        self.label_image_3 = QLabel(self)
        self.label_image_4 = QLabel(self)
        self.label_image_5 = QLabel(self)
        self.label_image_6 = QLabel(self)
        self.label_image_7 = QLabel(self)
        self.label_image_8 = QLabel(self)

        # Import Images
        self.CubeIQ_image = QPixmap('Images/up_2017_logo_en_resized.png')
        self.CubeIQ_icon_image = QIcon('Images/up_2017_logo_en.ico')
        self.Euro_image = QPixmap('Images/euro_sign_612x612-removebg-preview.png')
        self.setWindowIcon(self.CubeIQ_icon_image)

        # Buttons
        self.POS_button_0 = QPushButton('0', self)
        self.POS_button_1 = QPushButton('1', self)
        self.POS_button_2 = QPushButton('2', self)
        self.POS_button_3 = QPushButton('3', self)
        self.POS_button_4 = QPushButton('4', self)
        self.POS_button_5 = QPushButton('5', self)
        self.POS_button_6 = QPushButton('6', self)
        self.POS_button_7 = QPushButton('7', self)
        self.POS_button_8 = QPushButton('8', self)
        self.POS_button_9 = QPushButton('9', self)
        self.POS_button_minus = QPushButton('-', self)
        self.POS_button_comma = QPushButton('.', self)
        self.POS_button_clear = QPushButton('C', self)
        self.POS_button_arrow = QPushButton('->', self)

        self.Entry_button_clear = QPushButton('Clear', self)
        self.Entry_button_PayPod = QPushButton('Pay', self)

        # Text Labels
        self.label_0 = QLabel('Total amount to pay', self)
        self.label_1 = QLabel('Amount 1', self)
        self.label_2 = QLabel('Amount 2', self)
        self.label_3 = QLabel('Amount 3', self)
        self.label_4 = QLabel('Amount 4', self)
        self.label_5 = QLabel('Amount 5', self)
        self.label_6 = QLabel('Amount 6', self)
        self.label_7 = QLabel('Customer', self)

        # Create Text Inputs
        self.input_text_0 = QLineEdit(self)
        self.input_text_1 = QLineEdit(self)
        self.input_text_2 = QLineEdit(self)
        self.input_text_3 = QLineEdit(self)
        self.input_text_4 = QLineEdit(self)
        self.input_text_5 = QLineEdit(self)
        self.input_text_total_amount = QLineEdit(self)
        self.input_text_customer = QLineEdit(self)

        # Create Central Widget
        self.main_window = QWidget()

        # Line Edit Focused has the last widget focused before the button is pressed
        self.lineEditFocused = None
        self.app = QApplication(sys.argv)
        self.app.focusChanged.connect(self.on_focusChanged)

        self.setupUI()

    def setupUI(self):
        style = '''
        QMainWindow {background: #00171f;}
        QLabel#Text_Label {font-size: 22px;   font-weight: 600;   background-image: linear-gradient(to left, #553c9a, #b393d3);   color: orange;   background-clip: text;   -webkit-background-clip: text;}
        QPushButton#POS_button {   background-color: #0a6bff;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   min-width: 35px;   padding: 16px 20px;   position: relative;   text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        QPushButton#Entry_button{   background-color: #0a6bff;   border-radius: 4px;   border: 0;   box-shadow: rgba(1,60,136,.5) 0 -1px 3px 0 inset,rgba(0,44,97,.1) 0 3px 6px 0;   box-sizing: border-box;   color: #fff;   cursor: pointer;   display: inherit;   font-family: "Space Grotesk",-apple-system,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";   font-size: 18px;   font-weight: 700;   line-height: 24px;   margin: 0;   min-height: 50px;   min-width: 80px;   padding: 16px 20px;   position: relative;   text-align: center;   user-select: none;   -webkit-user-select: none;   touch-action: manipulation;   vertical-align: baseline;   transition: all .2s cubic-bezier(.22, .61, .36, 1); } QPushButton:hover {   background-color: #065dd8;   transform: translateY(-2px); }
        QLineEdit{{direction:rtl; font-size:32px; color: #EBEBEB; border: 0px solid black; background-color: {0}; color: #EBEBEB; border: 2px solid #ffa02f;}} QLineEdit:hover{{ border: 3px solid #FFFF00;}}
        '''

        input_style = """QLineEdit{{direction:rtl; font-size:32px; color: #EBEBEB; border: 0px solid black; background-color: {0}; color: #EBEBEB; border: 2px solid #ffa02f;}} QLineEdit:hover{{ border: 3px solid #FFFF00;}}""".format(
            '#262626')

        # Images scaling
        self.label_image_1.resize(300, 93)
        self.label_image_1.setPixmap(self.CubeIQ_image)
        self.label_image_1.move(80, 900)

        # Euro images
        self.label_image_2.setPixmap(self.Euro_image)
        self.label_image_3.setPixmap(self.Euro_image)
        self.label_image_4.setPixmap(self.Euro_image)
        self.label_image_5.setPixmap(self.Euro_image)
        self.label_image_6.setPixmap(self.Euro_image)
        self.label_image_7.setPixmap(self.Euro_image)
        self.label_image_8.setPixmap(self.Euro_image)
        self.label_image_2.move(345, 202)
        self.label_image_3.move(345, 352)
        self.label_image_4.move(345, 502)
        self.label_image_5.move(745, 202)
        self.label_image_6.move(745, 352)
        self.label_image_7.move(745, 502)
        self.label_image_8.move(552, 80)

        # When hover over button change the cursor
        self.POS_button_0.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_5.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_6.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_7.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_8.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_9.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_minus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_comma.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.POS_button_arrow.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.Entry_button_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.Entry_button_PayPod.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Move buttons to the desired location
        self.POS_button_0.move(980, 450)
        self.POS_button_1.move(850, 150)
        self.POS_button_2.move(980, 150)
        self.POS_button_3.move(1110, 150)
        self.POS_button_4.move(850, 250)
        self.POS_button_5.move(980, 250)
        self.POS_button_6.move(1110, 250)
        self.POS_button_7.move(850, 350)
        self.POS_button_8.move(980, 350)
        self.POS_button_9.move(1110, 350)
        self.POS_button_minus.move(850, 450)
        self.POS_button_comma.move(1110, 450)
        self.POS_button_clear.move(850, 550)
        self.POS_button_arrow.move(1110, 550)
        self.Entry_button_clear.move(200, 730)
        self.Entry_button_PayPod.move(430, 730)

        # Set Object Name for buttons for style
        self.POS_button_0.setObjectName('POS_button')
        self.POS_button_1.setObjectName('POS_button')
        self.POS_button_2.setObjectName('POS_button')
        self.POS_button_3.setObjectName('POS_button')
        self.POS_button_4.setObjectName('POS_button')
        self.POS_button_5.setObjectName('POS_button')
        self.POS_button_6.setObjectName('POS_button')
        self.POS_button_7.setObjectName('POS_button')
        self.POS_button_8.setObjectName('POS_button')
        self.POS_button_9.setObjectName('POS_button')
        self.POS_button_minus.setObjectName('POS_button')
        self.POS_button_comma.setObjectName('POS_button')
        self.POS_button_clear.setObjectName('POS_button')
        self.POS_button_arrow.setObjectName('POS_button')
        self.Entry_button_clear.setObjectName('Entry_button')
        self.Entry_button_PayPod.setObjectName('Entry_button')

        # Set Object name for style
        self.label_0.setObjectName('Text_Label')
        self.label_1.setObjectName('Text_Label')
        self.label_2.setObjectName('Text_Label')
        self.label_3.setObjectName('Text_Label')
        self.label_4.setObjectName('Text_Label')
        self.label_5.setObjectName('Text_Label')
        self.label_6.setObjectName('Text_Label')
        self.label_7.setObjectName('Text_Label')

        # Move Text Labels to specified position and resize them in order to fit text
        self.label_0.move(290, 30)
        self.label_1.move(130, 150)
        self.label_2.move(130, 300)
        self.label_3.move(130, 450)
        self.label_4.move(530, 150)
        self.label_5.move(530, 300)
        self.label_6.move(530, 450)
        self.label_7.move(330, 600)

        self.label_0.resize(300, 25)
        self.label_1.resize(200, 20)
        self.label_2.resize(200, 20)
        self.label_3.resize(200, 20)
        self.label_4.resize(200, 20)
        self.label_5.resize(200, 20)
        self.label_6.resize(200, 20)
        self.label_7.resize(200, 20)

        # Set Text right to left write
        self.input_text_0.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_1.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_2.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_3.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_4.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_5.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_total_amount.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input_text_customer.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Move Text Inputs to specified positions
        self.input_text_0.move(40, 200)
        self.input_text_1.move(440, 200)
        self.input_text_2.move(40, 350)
        self.input_text_3.move(440, 350)
        self.input_text_4.move(40, 500)
        self.input_text_5.move(440, 500)
        self.input_text_total_amount.move(260, 70)
        self.input_text_customer.move(180, 630)

        self.input_text_0.resize(300, 40)
        self.input_text_1.resize(300, 40)
        self.input_text_2.resize(300, 40)
        self.input_text_3.resize(300, 40)
        self.input_text_4.resize(300, 40)
        self.input_text_5.resize(300, 40)
        self.input_text_total_amount.resize(290, 50)
        self.input_text_customer.resize(400, 70)

        # Set Style
        self.input_text_0.setStyleSheet(input_style)
        self.input_text_1.setStyleSheet(input_style)
        self.input_text_2.setStyleSheet(input_style)
        self.input_text_3.setStyleSheet(input_style)
        self.input_text_4.setStyleSheet(input_style)
        self.input_text_5.setStyleSheet(input_style)
        self.input_text_total_amount.setStyleSheet(input_style)
        self.input_text_customer.setStyleSheet(input_style)
        self.setStyleSheet(style)

        # Set Validator to inputs
        only_float = QDoubleValidator(0.0, 250.0, 2)
        reg_ex = QRegularExpression(r'^[0-9]*(\.[0-9]{0,2})?$')
        float_validator_0 = QRegularExpressionValidator(reg_ex, self.input_text_0)
        float_validator_1 = QRegularExpressionValidator(reg_ex, self.input_text_1)
        float_validator_2 = QRegularExpressionValidator(reg_ex, self.input_text_2)
        float_validator_3 = QRegularExpressionValidator(reg_ex, self.input_text_3)
        float_validator_4 = QRegularExpressionValidator(reg_ex, self.input_text_4)
        float_validator_5 = QRegularExpressionValidator(reg_ex, self.input_text_5)
        float_validator_total = QRegularExpressionValidator(reg_ex, self.input_text_total_amount)

        self.input_text_0.setValidator(only_float)
        self.input_text_0.setValidator(float_validator_0)
        self.input_text_1.setValidator(only_float)
        self.input_text_1.setValidator(float_validator_1)
        self.input_text_2.setValidator(only_float)
        self.input_text_2.setValidator(float_validator_2)
        self.input_text_3.setValidator(only_float)
        self.input_text_3.setValidator(float_validator_3)
        self.input_text_4.setValidator(only_float)
        self.input_text_4.setValidator(float_validator_4)
        self.input_text_5.setValidator(only_float)
        self.input_text_5.setValidator(float_validator_5)
        self.input_text_total_amount.setValidator(only_float)
        self.input_text_total_amount.setValidator(float_validator_total)

        # When sub_amount is written then total amount is calculated
        self.input_text_0.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))
        self.input_text_1.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))
        self.input_text_2.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))
        self.input_text_3.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))
        self.input_text_4.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))
        self.input_text_5.textChanged.connect(lambda: self.calculate_total_amount(
            [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
             self.input_text_5], self.input_text_total_amount))

        # Press Clear and clear all inputs
        self.Entry_button_clear.clicked.connect(self.clear_text)
        self.POS_button_clear.clicked.connect(self.clear_text)

        # WHen Button clicked add character to the last focused user input
        self.POS_button_0.clicked.connect(lambda: self.setFocusText('0'))
        self.POS_button_1.clicked.connect(lambda: self.setFocusText('1'))
        self.POS_button_2.clicked.connect(lambda: self.setFocusText('2'))
        self.POS_button_3.clicked.connect(lambda: self.setFocusText('3'))
        self.POS_button_4.clicked.connect(lambda: self.setFocusText('4'))
        self.POS_button_5.clicked.connect(lambda: self.setFocusText('5'))
        self.POS_button_6.clicked.connect(lambda: self.setFocusText('6'))
        self.POS_button_7.clicked.connect(lambda: self.setFocusText('7'))
        self.POS_button_8.clicked.connect(lambda: self.setFocusText('8'))
        self.POS_button_9.clicked.connect(lambda: self.setFocusText('9'))
        self.POS_button_comma.clicked.connect(lambda: self.setFocusText('.'))

        self.Entry_button_PayPod.clicked.connect(self.send_POST_request)

        # self.setCentralWidget(self.main_window)

    # Calculate total amount of QLineEdit input when value changes
    def calculate_total_amount(self, sub_amount, total_amount):
        total = 0

        # self.lineEditFocused is the last entry that has been selected if it has a comma then disable comma button
        # and this event is triggered every time each QLineEdit is changing
        self.POS_button_comma.setEnabled(True)

        for entry in sub_amount:
            value = entry.text()
            if value == '':
                total += 0
            elif ',' in entry.text():
                total += float(value.replace(',', '.'))
                self.POS_button_comma.setEnabled(False)
            else:
                total += float(value)
        total_amount.setText(str(round(total, 2)))  # If round not present then a problem with computation

    # Clear text when clear button is pressed
    def clear_text(self):
        for qlineedit in [self.input_text_0, self.input_text_1, self.input_text_2, self.input_text_3, self.input_text_4,
                          self.input_text_5]:
            QLineEdit.clear(qlineedit)

    def setFocusText(self, button_value):
        if self.lineEditFocused.__class__.__name__ == 'QLineEdit':
            if self.lineEditFocused.text() == '':
                self.lineEditFocused.setText(button_value)
            else:
                self.lineEditFocused.setText(self.lineEditFocused.text() + button_value)
        else:
            pass

    def on_focusChanged(self, widget):
        if widget.__class__.__name__ == 'QLineEdit':
            self.lineEditFocused = widget
            linedit = QApplication.focusWidget()
            # print(linedit)

    def send_POST_request(self):
        amount = self.input_text_total_amount.text()  # Get the text from the QLineEdit
        data = {"amount": amount}

        url = 'http://127.0.0.1:5000/payment'  # The URL where the POST request needs to be sent

        headers = {'Content-Type': 'application/json'}  # Set the headers to indicate JSON data

        try:
            response = requests.post(url, json=data, headers=headers)  # Send POST request

            if response.ok:
                print("This is the response: ", response)
                print("Payment processed successfully")
            else:
                print("This is the response: ", response)
                print("Failed to process payment")
        except requests.exceptions.RequestException as e:
            print("An error occurred: ", e)
