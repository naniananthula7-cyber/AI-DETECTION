from flask import Flask, render_template
import subprocess
import sys

app = Flask(__name__)
process = None  # Track detection process

@app.route('/')
def home():
    # Initially only show START button
    return render_template('index.html', show_stop=False)

@app.route('/start')
def start():
    global process
    if process is None or process.poll() is not None:
        # Use sys.executable to ensure the correct Python interpreter is used
        # shell=True ensures Windows handles arguments correctly
        process = subprocess.Popen(
            [sys.executable, "detection.py"],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # keep process alive in its own console
        )
        print("✅ Detection process started and will keep running until STOP is clicked.")
        return render_template('index.html', show_stop=True)
    else:
        return "⚠️ Detection is already running."

@app.route('/stop')
def stop():
    global process
    if process is not None and process.poll() is None:
        process.terminate()
        process = None
        print("🛑 Detection process stopped.")
        return render_template('index.html', show_stop=False)
    else:
        return "⚠️ No detection process running."

if __name__ == "__main__":
    app.run(debug=True)