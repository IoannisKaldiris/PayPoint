import threading
import sys
from flask import Flask, request, jsonify
from Cashier_Window import CashierWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QIcon
from System_Tray_Icon import SystemTrayIcon


def create_flask_app(qt_app):
    server_app = Flask(__name__)

    @server_app.route('/payment', methods=["POST"])
    def process_payment():
        data = request.json
        amount = data.get('amount')

        if not amount:
            return jsonify({"error": "No amount provided"}), 400

        qt_app.postEvent(qt_app, ShowCashierEvent(amount))

        return jsonify({"message": "Payment processed successfully", "amount": amount}), 200

    @server_app.route('/accept_denomination', methods=["POST"])
    def manage_input_denomination():
        data = request.json
        input_amount = data.get('input_denomination')

        if not input_amount:
            return jsonify({"error": "No correct format provided"}), 400

        if not app.is_transaction_active():
            return jsonify({"error": "No active transaction. Start a payment first."}), 406

        try:
            # Convert input_amount to float and format it to two decimal places
            input_amount_float = float(input_amount)
            formatted_amount = format(input_amount_float, ".2f")

            # Post event to the QApplication instance with the formatted data
            event = Deposit_Denomination(formatted_amount)
            qt_app.postEvent(qt_app, event)

            return jsonify({"message": "Denomination accepted", "amount": formatted_amount}), 200
        except ValueError:
            # Handle the error if input_amount cannot be converted to float
            return jsonify({"error": "Invalid input, amount must be a valid number"}), 400

    return server_app


class ShowCashierEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, amount):
        super().__init__(self.EVENT_TYPE)
        self.amount = amount


class Deposit_Denomination(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, cash_in):
        super().__init__(self.EVENT_TYPE)
        self.cash_in = cash_in


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.cashier_window = None
        self.tray_icon = SystemTrayIcon(QIcon("Images/PayPoint_logo.ico"), self)

    def event(self, event):
        if event.type() == ShowCashierEvent.EVENT_TYPE:
            self.show_cashier(event.amount)
            return True
        elif event.type() == Deposit_Denomination.EVENT_TYPE:
            if self.cashier_window:
                self.cashier_window.deposit_update_labels(event.cash_in)
            return True
        return super().event(event)

    def show_cashier(self, amount):
        # Check if the window exists and is visible; if not, create or show it
        if self.cashier_window is None or not self.cashier_window.isVisible():
            self.cashier_window = CashierWindow(amount)
            self.cashier_window.start_transaction()
        else:
            # If window exists but needs to be reset for a new transaction
            self.cashier_window.reset_for_new_transaction(amount)

        self.cashier_window.show()

    def is_transaction_active(self):
        if self.cashier_window and self.cashier_window.transaction_active:
            return True
        return False

    def setup_tray_icon(self):
        self.tray_icon = SystemTrayIcon(QIcon("Images/PayPoint_logo.ico"), self)
        self.tray_icon.show()


if __name__ == "__main__":
    app = Application(sys.argv)
    app.setup_tray_icon()
    flask_app = create_flask_app(app)
    threading.Thread(target=lambda: flask_app.run(debug=True, use_reloader=False)).start()
    sys.exit(app.exec())
