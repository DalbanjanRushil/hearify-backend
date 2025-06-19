import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Load environment variables (must be set in Render)
openai.api_key = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

@app.route("/")
def home():
    return "🎵 Hearify Backend is running"

@app.route("/generate", methods=["POST"])
def generate_music():
    print("\n🔥 /generate endpoint HIT")

    try:
        # Get prompt from frontend
        data = request.get_json()
        prompt = data.get("prompt", "")
        print("🎧 Prompt received:", prompt)

        # Log key status
        print("🔍 Checking API Keys:")
        print("✅ OPENAI_API_KEY:", "Yes" if openai.api_key else "❌ Missing")
        print("✅ HF_API_TOKEN:", "Yes" if HF_API_TOKEN else "❌ Missing")

        # Step 1: TEMP — Hardcoded fallback prompt instead of GPT
        music_prompt = f"A calm lo-fi beat with soft textures and {prompt}"
        print("🧠 Using fallback music prompt:", music_prompt)

        # Step 2: Send to HuggingFace MusicGen
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )

        print("🎵 HuggingFace response code:", response.status_code)

        if response.status_code != 200:
            print("❌ HuggingFace ERROR:", response.text)
            return jsonify({"error": "HuggingFace API failed", "details": response.text}), 500

        # Step 3: Save audio file in static/
        filename = f"static/music_{int(time.time())}.wav"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(response.content)

        print("✅ Music saved:", filename)
        return jsonify({ "url": f"/{filename}" })

    except Exception as e:
        print("❌ EXCEPTION occurred:", e)
        import traceback
        traceback.print_exc()
        return jsonify({ "error": "Server error", "details": str(e) }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
