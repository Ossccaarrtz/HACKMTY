from flask import Flask, jsonify, request
from openai import OpenAI
from elevenlabs import ElevenLabs, save
import os, uuid

app = Flask(__name__)

# Inicializa APIs
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "Rachel")
AUDIO_DIR = os.getenv("AUDIO_DIR", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

conversation_history = []  # Memoria simple


@app.route("/")
def home():
    return jsonify({"message": "FinCortex Voice activo"}), 200


@app.route("/ask", methods=["POST"])
def ask():
    """GPT-5 + ElevenLabs TTS"""
    data = request.get_json()
    question = (data or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Falta la pregunta"}), 400

    conversation_history.append({"role": "user", "content": question})
    if len(conversation_history) > 10:
        conversation_history.pop(0)

    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": (
                "Eres FinCortex Voice, el CFO virtual con voz propia. "
                "Responde con claridad, empatía y fundamento financiero breve."
            )},
            *conversation_history
        ],
        temperature=0.7,
        max_tokens=250
    )

    answer = completion.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": answer})

    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    audio = eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=answer,
        model_id="eleven_multilingual_v2"
    )
    save(audio, audio_path)

    return jsonify({
        "text": answer,
        "confidence": 0.9,
        "audio_url": f"/audio/{audio_filename}"
    })


@app.route("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

