import requests
from pprint import pprint


url = "https://api.intelligence.io.solutions/api/v1/models"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjA0M2UyYWRjLWNlMGQtNDdhMy1hY2RlLTEyMWU2MTk3MjcyZCIsImV4cCI6NDkwNzQwNDA3OX0.anZEz7MidIKi4NdLzAmvRyLzL0Ay_qVppUyTcymYrqcWWPZAjKNqgexgZiQYTEjAgh0AsvHEymAbJS4vR0eNhQ",
}

response = requests.get(url, headers=headers)
data = response.json()
pprint(data)

for i in range(len(data['data'])):
    name = data['data'][i]['id']
    print(name)