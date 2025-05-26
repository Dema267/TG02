import os
import http.client
import json
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "rottentomato.p.rapidapi.com"

conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
headers = {
    'x-rapidapi-key': RAPIDAPI_KEY,
    'x-rapidapi-host': RAPIDAPI_HOST
}

conn.request("GET", "/tv-shows/popular", headers=headers)  # попробуй разные эндпоинты из документации
res = conn.getresponse()
data = res.read()

print("HTTP статус:", res.status)
print("Ответ сервера:")
print(json.dumps(json.loads(data), indent=2, ensure_ascii=False))
