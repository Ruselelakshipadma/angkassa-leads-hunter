import os
import time
from datetime import datetime
from flask import Flask
import threading

# Setup Flask app
app = Flask(__name__)

# Function to perform lead checking
def get_leads():
    print("🔍 Starting to scan for new leads...")
    # Logika scrapenya ada di sini
    print("✅ Lead checking done at", datetime.now())

# Define route
@app.route('/')
def home():
    return "Lead Hunter is running!"

# Function to run the lead checking at intervals
def run_leads():
    while True:
        get_leads()
        time.sleep(1800)  # Delay 30 menit (1800 detik)

# Run the Flask app and lead checker on separate threads
if __name__ == "__main__":
    # Start the lead checking function in a separate thread
    threading.Thread(target=run_leads, daemon=True).start()

    # Start the Flask app on the port specified in Render's environment
    port = int(os.environ.get("PORT", 10000))  # default to 10000 if PORT not found
    app.run(host="0.0.0.0", port=port)  # Expose the app to external IPs (Render's server)
