import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

@app.route("/")
def home():
    return "🎵 Hearify Backend is running"

@app.route("/generate", methods=["POST"])
def generate_music():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        print("🎧 Prompt received:", prompt)

        # Step 1: Generate a music description using GPT
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Create a detailed music generation prompt based on: {prompt}"}
            ]
        )
        music_prompt = gpt_response['choices'][0]['message']['content']
        print("🧠 GPT-generated prompt:", music_prompt)

        # Step 2: Call HuggingFace MusicGen
        hf_response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )

        print("🎵 HuggingFace response code:", hf_response.status_code)

        if hf_response.status_code != 200:
            print("❌ HuggingFace ERROR:", hf_response.text)
            return jsonify({"error": "HF API failed", "details": hf_response.text}), 500

        # Step 3: Save audio file
        filename = f"static/music_{int(time.time())}.wav"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(hf_response.content)

        print("✅ Music saved as:", filename)
        return jsonify({"url": f"/{filename}"})

    except Exception as e:
        print("❌ EXCEPTION:", e)
        import traceback
        traceback.print_exc()  # shows full stacktrace in logs
        return jsonify({"error": "Server Exception", "details": str(e)}), 500

# Run app on 0.0.0.0 so Render can detect it
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
