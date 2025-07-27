from flask import Flask, request, render_template, redirect, jsonify
import requests

app = Flask(__name__)

# Homepage with image URL form
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Route to submit image URL to Nero API
@app.route('/submit', methods=['POST'])
def submit():
    image_url = request.form.get('image_url')

    # Nero API setup
    nero_api_url = "https://api.nero.com/biz/api/task"
    api_key = "JRGKEBDP4K87Q7DBRT3FSB4B"  # Replace with your actual API key

    headers = {
        "x-neroai-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "type": "ImageUpscaler:Standard",
        "body": {
            "image": image_url
        },
        "info": {
            "webhook": "https://webhook-srz2.onrender.com/webhook"
        }
    }

    response = requests.post(nero_api_url, headers=headers, json=data)
    print("🎯 Nero Task Submitted:", response.json())

    return render_template('index.html', submitted=True, nero_response=response.json())

# Webhook to receive result from Nero
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    print("✅ Webhook Triggered!")
    print("Full Payload:", data)

    task_id = data.get("task_id")
    status = data.get("status")
    result_url = data.get("result", {}).get("output")

    print(f"🆔 Task ID: {task_id}")
    print(f"📌 Status: {status}")
    if result_url:
        print(f"🖼️ Upscaled Image URL: {result_url}")

    return jsonify({"message": "Webhook received successfully"}), 200

if __name__ == '__main__':
    app.run(deug=True)
