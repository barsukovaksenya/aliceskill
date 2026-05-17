import requests


url = 'http://aliceskill-seven.vercel.app/post'

data = {
  "request": {
    "command": "нет",
    "original_utterance": "хорошо"
  },
  "session": {
    "new": False,
    "message_id": 1,
    "session_id": "test-session-123",
    "skill_id": "test-skill",
    "user_id": "test-user-1"
  },
  "version": "1.0"
}

response = requests.post(url, json=data)
print(response.json())
