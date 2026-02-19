from flask import Flask, render_template, redirect, url_for
import subprocess
import sys

app = Flask(__name__)
process = None  # Track detection process

@app.route('/')
def home():
    global process
    is_running = process is not None and process.poll() is None
    return render_template('index.html', show_stop=is_running)

@app.route('/start')
def start():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen(
            [sys.executable, "detection.py"],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("✅ Detection process started.")
    else:
        print("⚠️ Detection is already running.")
    return redirect(url_for('home'))

@app.route('/stop')
def stop():
    global process
    if process is not None and process.poll() is None:
        # Stop detection
        process.terminate()
        process = None
        print("🛑 Detection process stopped.")

        # Automatically run upload script after stopping
        subprocess.Popen(
            [sys.executable, "save_counts.py"],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("📤 Counts upload started automatically after stop.")
    else:
        print("⚠️ No detection process running.")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
