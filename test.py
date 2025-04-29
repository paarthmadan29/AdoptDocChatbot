import requests

url = "http://localhost:8000/chat"
headers = {
    "Content-Type": "application/json"
}
data = {
    "query": "How do I access the Volume Browser after it's been added to my Volume?"
}

response = requests.post(url, headers=headers, json=data)

# Print the response
from pprint import pprint
pprint(response.json())
breakpoint()