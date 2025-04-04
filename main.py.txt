import time
from datetime import datetime

def get_leads():
    print("🔍 Starting to scan for new leads...")
    # nanti disini tempat logika scrapenya
    print("✅ Lead checking done at", datetime.now())

if __name__ == "__main__":
    while True:
        get_leads()
        time.sleep(1800)  # delay 30 menit (1800 detik)
