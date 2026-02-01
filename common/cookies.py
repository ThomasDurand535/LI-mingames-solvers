import json

try:
    with open("common/cookies.json", "r") as file:
        cookies = json.load(file)
except FileNotFoundError:
    print("cookies.json not found.")
    cookies = None
except json.JSONDecodeError:
    print("Error decoding JSON.")
    cookies = None
