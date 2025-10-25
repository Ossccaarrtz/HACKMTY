import os
import requests
import base64

# ==========================
# ⚙️ Configuración ElevenLabs
# ==========================
ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
ELEVEN_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# ==========================
# 🔊 Función principal
# ==========================
def synthesize_voice(text: str) -> str:
    """Convierte texto a voz y devuelve audio base64 sin crear archivos locales."""
    if not ELEVEN_KEY:
        print("⚠️  Falta ELEVEN_API_KEY en entorno.")
        return None

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }

    try:
        response = requests.post(ELEVEN_URL, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"[ElevenLabs Error] {response.text}")
            return None

        audio_base64 = base64.b64encode(response.content).decode("utf-8")
        return audio_base64
    except Exception as e:
        print(f"[TTS Error] {e}")
        return None
