from flask import Flask, request, jsonify
import openai
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load API keys from environment
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

openai.api_key = OPENAI_API_KEY

@app.route("/generate", methods=["POST"])
def generate_music():
    data = request.get_json()
    theme = data.get("prompt", "")

    # Step 1: Expand the theme using GPT
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative music composer."},
                {"role": "user", "content": f"Write a short description for AI music based on: '{theme}'"}
            ],
            temperature=0.7,
            max_tokens=60
        )
        music_prompt = gpt_response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": "GPT failed", "details": str(e)}), 500

    # Step 2: Call HuggingFace MusicGen
    try:
        hf_response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/musicgen-small",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": music_prompt}
        )
        if hf_response.status_code != 200:
            return jsonify({"error": "MusicGen failed", "details": hf_response.text}), 500

        # HuggingFace returns binary audio — we must host it or use dummy link
        # For demo: save to a file (if running locally), or return a placeholder
        with open("musicgen_output.wav", "wb") as f:
            f.write(hf_response.content)

        # You should upload it to a public location (e.g., Cloudinary, S3)
        return jsonify({"url": "/musicgen_output.wav", "prompt": music_prompt})

    except Exception as e:
        return jsonify({"error": "HuggingFace call failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

