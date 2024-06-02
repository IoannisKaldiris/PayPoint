import socket


def send_socket_data(data):
    host = '127.0.0.1'  # The server's hostname or IP address
    port = 65432  # The port used by the server

    # Connect, send, receive, and close each time this function is called.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode())
        response = s.recv(1024)
        print("Received from server:", response.decode())


if __name__ == "__main__":
    valid_denominations = {0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00, 200.00,
                           500.00}

    while True:
        input_denomination = input("Enter the denomination or 'c' to close: ")

        if input_denomination.lower() == 'c':
            print("Exiting...")
            break

        try:
            denomination_float = float(input_denomination)
            if denomination_float not in valid_denominations:
                print("Invalid denomination entered. Please enter a valid Euro denomination.")
                continue
        except ValueError:
            print("Invalid input. Please enter a numerical value.")
            continue

        data = f"denomination:{denomination_float}"
        send_socket_data(data)
