import requests

url = "http://127.0.0.1:8000/solve"
payload = {"prompt": "how much is 1+2?"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(response.text)
print('')