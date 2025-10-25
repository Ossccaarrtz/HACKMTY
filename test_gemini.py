import requests
import json

# URL del backend que corre en Docker
url = "http://localhost:5000/ask"

# Pregunta de prueba que se enviará como JSON
payload = {"question": "Dame un resumen financiero de México en 2024"}

# Envía el POST a Flask
response = requests.post(url, json=payload)

# Muestra el resultado legible
try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception:
    print("Error:", response.text)
