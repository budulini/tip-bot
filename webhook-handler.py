from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        os.system("/home/janko/tip-bot/webhook-handler.sh")
        return 'Success', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28973)
