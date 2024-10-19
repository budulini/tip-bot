from flask import Flask, Response

app = Flask(__name__)

# Function to stream the logs
def generate_logs():
    with open('bot.log', 'r') as f:  # Adjust the path to your log file
        while True:
            line = f.readline()
            if not line:
                break
            yield line

@app.route('/logs')
def logs():
    return Response(generate_logs(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)