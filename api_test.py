import requests
from pprint import pprint

url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjA0M2UyYWRjLWNlMGQtNDdhMy1hY2RlLTEyMWU2MTk3MjcyZCIsImV4cCI6NDkwNzQwNDA3OX0.anZEz7MidIKi4NdLzAmvRyLzL0Ay_qVppUyTcymYrqcWWPZAjKNqgexgZiQYTEjAgh0AsvHEymAbJS4vR0eNhQ",
}

data = {
    "model": "deepseek-ai/DeepSeek-R1",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant"
        },
        {
            "role": "user",
            "content": "how are you doing"
        }
    ],
}

response = requests.post(url, headers=headers, json=data)
data = response.json()
# pprint(data)

text = data['choices'][0]['message']['content']
print(text.split('</think>\n\n')[1])