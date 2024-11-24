from flask import Flask, request
import os
import logging
import subprocess

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        subprocess.run(["/home/janko/tip-bot/webhook/webhook-handler.sh"], check=True)
        return 'Success', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28973)
