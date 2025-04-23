import re
from flask import Flask, Response

app = Flask(__name__)

# Function to stream the logs
def generate_logs():
    # only show INFO, WARNING, ERROR, CRITICAL
    level_re = re.compile(r' - (INFO|WARNING|ERROR|CRITICAL) - ')
    with open('./files/bot.log', 'r') as f:  # Adjust the path to your log file
        while True:
            line = f.readline()
            if not line:
                break
            if level_re.search(line):
                yield line

@app.route('/logs')
def logs():
    return Response(generate_logs(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1701)