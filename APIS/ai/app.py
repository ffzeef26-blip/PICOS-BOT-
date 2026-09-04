from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# --- Your multiple API keys ---
API_KEYS = [
    "465445e1-7852-4d27-89c7-23403986bb8e",
    "8ed0a2bc-d409-4342-95eb-a137d502ee65",
    "084eb8a0-f92e-448d-a405-7f0c1a5311b0",
    "26d11527-7862-478c-880e-cacda2ae0263"
]

# --- Supported models, fast first ---
MODELS = [
    "Meta-Llama-3.1-8B-Instruct",
    "MiniMax-M2.5",
    "Meta-Llama-3.3-70B-Instruct",
    "Qwen3-32B",
    "Qwen3-235B",
    "gpt-oss-120b",
    "Whisper-Large-v3",
    "Llama-4-Maverick-17B-128E-Instruct",
    "E5-Mistral-7B-Instruct",
    "DeepSeek-V3.2",
    "DeepSeek-V3.1-cb",
    "DeepSeek-V3.1-Terminus",
    "DeepSeek-V3.1",
    "DeepSeek-V3-0324",
    "DeepSeek-R1-Distill-Llama-70B",
    "DeepSeek-R1-0528",
    "ALLaM-7B-Instruct-preview"
]

SAMBA_URL = "https://api.sambanova.ai/v1/chat/completions"


def ask_sambanova(question):
    """Try all keys & models until response received"""
    for key in API_KEYS:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        for model in MODELS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": (
                        "You are TEAMX LEGACY's AI assistant. "
                        "Always start the response with \"I'm TEAMX LEGACY AI assistant.\" "
                        "Respond max 700 characters. Be concise, friendly. "
                        "Do NOT include <think> tags or long reasoning."
                    )},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.3,
                "max_tokens": 180,  # ~700 characters
                "top_p": 0.9
            }

            try:
                res = requests.post(SAMBA_URL, headers=headers, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    reply = data.get("choices",[{}])[0].get("message",{}).get("content","No response")
                    if reply.strip():
                        return reply.strip(), key, model
                else:
                    continue  # try next model/key

            except requests.exceptions.Timeout:
                continue
            except Exception:
                continue

    return "No response available from any key/model.", None, None


@app.route("/ask", methods=["GET"])
def ask():
    question = request.args.get("question", "").strip()
    if not question:
        return jsonify({"status":"error","message":"Missing question"}), 400

    reply, used_key, used_model = ask_sambanova(question)

    return jsonify({
        "status": "success",
        "question": question,
        "reply": reply,
        "used_key": used_key,
        "used_model": used_model
    })


if __name__ == "__main__":
    app.run(port=5001, debug=False)