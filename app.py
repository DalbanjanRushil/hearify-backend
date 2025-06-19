import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Load API keys from environment
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
        print("\n🎧 Prompt received:", prompt)

        # ✅ DEBUG: Confirm keys are loaded
        print("🔍 Checking API Keys:")
        print("✅ OPENAI_API_KEY loaded:", "Yes" if openai.api_key else "❌ Missing")
        print("✅ HF_API_TOKEN loaded:", "Yes" if HF_API_TOKEN else "❌ Missing")

        # ✅ STEP 1: [TEMP] Generate a fake GPT response
        # Commenting out GPT until it's confirmed working
        # Uncomment this block once HuggingFace is confirmed
        # gpt_response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{
        #         "role": "user",
        #         "content": f"Create a detailed music generation prompt based on: {prompt}"
        #     }]
        # )
        # music_prompt = gpt_response['choices'][0]['message']['content']
        
        # TEMPORARY HARD-CODED PROMPT
        music_prompt = f"A peaceful lo-fi instrumental with sounds of {prompt}"
        print("🧠 Using fallback music prompt:", music_prompt)

        # ✅ STEP 2: Call HuggingFace MusicGen
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )

        print("🎵 HuggingFace response code:", response.status_code)

        if response.status_code != 200:
            print("❌ HuggingFace Error:", response.text)
            return jsonify({"error": "HuggingFace API failed", "details": response.text}), 500

        # ✅ STEP 3: Save to static folder
        filename = f"static/music_{int(time.time())}.wav"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(response.content)

        print("✅ Music saved at:", filename)
        return jsonify({"url": f"/{filename}"})

    except Exception as e:
        print("❌ EXCEPTION:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
