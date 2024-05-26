import json


def load_settings():
    with open('appsettings.json', 'r') as file:
        json_settings = json.load(file)
    return json_settings


settings = load_settings()

# Assuming English "en-US" is at index 0, map other languages as needed
language_codes = {
    "en-US": 0  # Add other languages as necessary: "fr-FR": 1, "de-DE": 2, etc.
}

# Get the current language index from settings, default to English if not found
current_language_index = language_codes.get(settings['Language'], 0)
