# Given string
denomination_string = "500 €"

# Remove the euro sign and any other non-numeric characters except for the decimal point
cleaned_denomination = ''.join(char for char in denomination_string if char.isdigit() or char == '.')

# Convert to float
denomination_float = float(cleaned_denomination)

print(denomination_float)  # Output will be 500.0