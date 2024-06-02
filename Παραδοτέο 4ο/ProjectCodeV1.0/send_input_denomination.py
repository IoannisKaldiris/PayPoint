import requests


def send_post_request(data):
    url = "http://127.0.0.1:5000/accept_denomination"  # Replace this with your specific URL
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


if __name__ == "__main__":
    # Define valid euro denominations
    valid_denominations = {0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00, 200.00,
                           500.00}

    while True:  # Keep running until the user decides to exit
        input_denomination = input("Enter the denomination or 'c' to close: ")

        if input_denomination.lower() == 'c':  # Check if the user wants to close the application
            print("Exiting...")
            break  # Exit the loop and terminate the script

        try:
            # Convert input to float and check if it's a valid denomination
            denomination_float = float(input_denomination)
            if denomination_float not in valid_denominations:
                print("Invalid denomination entered. Please enter a valid Euro denomination.")
                continue
        except ValueError:
            print("Invalid input. Please enter a numerical value.")
            continue

        data = {
            "input_denomination": denomination_float
        }

        response = send_post_request(data)
        if response:
            print("Response:", response)
