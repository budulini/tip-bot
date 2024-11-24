from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            # Run the host script
            result = subprocess.run(
                ["/path/to/your/host-script.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            # Log success
            app.logger.info(f"Script output: {result.stdout}")
            return 'Success', 200
        except subprocess.CalledProcessError as e:
            # Log errors
            app.logger.error(f"Script failed with error: {e.stderr}")
            return f"Error: {e.stderr}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=28973)
