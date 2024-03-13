import requests
import json

APP_ID = '9147fe2e-8d34-4ce8-9d7e-6ebf30d3470f'
REST_API_KEY = 'NTczYjgxNDYtN2RjNi00M2I3LWEwOGMtNjc4ZDVlYjMyMDAw'

ONESIGNAL_API_URL = 'https://onesignal.com/api/v1/notifications'

message = {
    "app_id": APP_ID,
    "include_player_ids": ["ca57bb89-1bd7-4b28-8de2-2d205acfa860"],
    "contents": {"en": "Hooray your dynamic bus has been scheduled!"},
    "headings": {"en": "Dynamic Bus Scheduled"},
    "small_icon": "buss",
    "large_icon": "https://i.imgur.com/AXydRIM.png",
    "big_picture":"https://i.imgur.com/Wsf4w9f.png",
    "android_accent_color":"FFFF0000"
    
}
test = ["feed1993-441b-4af9-b4c7-39365b263ce4","dc0b5027-0c88-44d9-b945-3b567117f8d5","06d73f55-7ccb-48f9-a2fe-d34cb4f1e29c"]
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
