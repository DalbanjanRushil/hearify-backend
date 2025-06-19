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

@app.route("/generate", methods=["POST"])
def generate_music():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        print("🎧 Prompt received:", prompt)

        # Generate detailed music prompt using GPT
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Create a detailed music generation prompt based on: {prompt}"}
            ]
        )
        music_prompt = gpt_response['choices'][0]['message']['content']
        print("🧠 GPT-generated prompt:", music_prompt)

        # Send to HuggingFace MusicGen
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )

        if response.status_code != 200:
            print("❌ HuggingFace error:", response.text)
            return jsonify({"error": "HF Error", "details": response.text}), 500

        # Save music to file
        filename = f"static/music_{int(time.time())}.wav"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(response.content)

        print("✅ Music saved:", filename)
        return jsonify({"url": f"/{filename}"})

    except Exception as e:
        print("❌ EXCEPTION:", e)
        return jsonify({"error": "Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
