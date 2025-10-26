import os
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

MCP_DIR = os.path.dirname(__file__)

@app.route("/.well-known/ai-plugin.json")
def serve_manifest():
    """
    Endpoint de descubrimiento MCP.
    Devuelve el manifest.json y permite a modelos LLM conocer las APIs disponibles.
    """
    return send_from_directory(MCP_DIR, "manifest.json")

@app.route("/mcp/ping")
def ping():
    return jsonify({"status": "ok", "message": "Servidor MCP activo 🚀"})

if __name__ == "__main__":
    # Se puede correr de forma separada: python app/mcp/server.py
    app.run(host="0.0.0.0", port=3333, debug=True)
