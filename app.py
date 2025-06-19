import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "🎵 Hearify Backend is running"

@app.route("/generate", methods=["POST"])
def generate_music():
    try:
        print("✅ /generate endpoint hit!")

        # Test audio link (public .mp3 file)
        return jsonify({
            "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        })
    except Exception as e:
        print("❌ Exception:", e)
        return jsonify({ "error": "Server error", "details": str(e) }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
