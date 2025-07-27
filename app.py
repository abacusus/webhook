from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # <- will show index.html

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("🔔 Webhook triggered!")
    print("📦 Full data received:", data)

    task_id = data.get("task_id")
    status = data.get("status")
    result_url = data.get("result", {}).get("output")

    print(f"🆔 Task ID: {task_id}")
    print(f"📌 Status: {status}")
    if result_url:
        print(f"🖼️ Image URL: {result_url}")

    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(debug=True)
