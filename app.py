import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

@app.route("/")
def home():
    return "🎵 Hearify Backend is running!"

@app.route("/generate", methods=["POST"])
def generate_music():
    print("\n🔥 /generate endpoint HIT")

    try:
        # Get the incoming prompt from frontend
        data = request.get_json()
        prompt = data.get("prompt", "")
        print("🎧 Prompt received:", prompt)

        # Log status of API keys
        print("🔍 API Keys Status:")
        print("✅ OPENAI_API_KEY:", "Loaded" if openai.api_key else "❌ MISSING")
        print("✅ HF_API_TOKEN:", "Loaded" if HF_API_TOKEN else "❌ MISSING")

        # Step 1: Use fallback prompt (disable GPT for now)
        music_prompt = f"A chill lo-fi beat with {prompt}"
        print("🧠 Using prompt:", music_prompt)

        # Step 2: Call HuggingFace API
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )

        print("🎵 HF response code:", response.status_code)

        if response.status_code != 200:
            print("❌ HuggingFace Error:", response.text)
            return jsonify({"error": "HuggingFace API failed", "details": response.text}), 500

        # Step 3: Save music file
        filename = f"static/music_{int(time.time())}.wav"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(response.content)

        print("✅ Music saved:", filename)
        return jsonify({ "url": f"/{filename}" })

    except Exception as e:
        print("❌ EXCEPTION:", e)
        import traceback
        traceback.print_exc()
        return jsonify({ "error": "Server error", "details": str(e) }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
