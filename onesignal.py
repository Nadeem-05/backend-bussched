import requests
import json

APP_ID = '9147fe2e-8d34-4ce8-9d7e-6ebf30d3470f'
REST_API_KEY = 'NTczYjgxNDYtN2RjNi00M2I3LWEwOGMtNjc4ZDVlYjMyMDAw'

ONESIGNAL_API_URL = 'https://onesignal.com/api/v1/notifications'

message = {
    "app_id": APP_ID,
    "include_player_ids": ["ca57bb89-1bd7-4b28-8de2-2d205acfa860"],
    "contents": {"en": "Hooray your dynamic bus has been scheduled!"},
    "headings": {"en": "Dynamic Bus Scheduled"}
}

message_json = json.dumps(message)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {REST_API_KEY}'
}

response = requests.post(ONESIGNAL_API_URL, headers=headers, data=message_json)

if response.status_code == 200:
    print("Notification sent successfully!")
else:
    print("Failed to send notification. Status code:", response)
