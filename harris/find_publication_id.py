import requests

API_KEY = "your_api_key_here"

url = "https://api.beehiiv.com/v2/publications"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Publication ID:", data["data"][0]["id"])  # Assumes first publication
else:
    print("Error:", response.status_code, response.text)