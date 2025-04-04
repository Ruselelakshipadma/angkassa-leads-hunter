import os
import time
import random
import threading
import instaloader
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from langdetect import detect
from bs4 import BeautifulSoup
from flask import Flask
from datetime import datetime
import re

# Setup Flask app
app = Flask(__name__)

# === STEP 1: AUTH GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Ambil kredensial JSON dari environment variable
credentials_json = os.environ.get('GOOGLE_CREDENTIALS')

# Pastikan kredensial diambil dari environment variable yang telah diset
creds = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1pO-Ww9B8ec4qTyy1N-xPprEptgPTXO5sNydK4mS7g-E")
master_sheet = sheet.worksheet("Master Cust")

try:
    new_leads_sheet = sheet.worksheet("New Leads")
except:
    new_leads_sheet = sheet.add_worksheet(title="New Leads", rows="100", cols="10")

existing_emails = set(master_sheet.col_values(4))

# === STEP 2: IG SESSION ===
L = instaloader.Instaloader()
L.load_session_from_file("session-gadingserpongproperty2023", filename="session-gadingserpongproperty2023")

hashtags = ["beantobarchocolate", "chocolatemaker", "craftchocolate"]
processed = 0
max_leads = 50

def get_leads():
    global processed
    print("🔍 Starting to scan for new leads...")
    for tag in hashtags:
        posts = instaloader.Hashtag.from_name(L.context, tag).get_posts()
        for post in posts:
            try:
                profile = post.owner_profile
                username = profile.username
                full_name = profile.full_name
                bio = profile.biography.lower()
                website = profile.external_url or ""
                last_post = post.date_utc
                email_ig = ""
                email_web = ""
                language = ""
                timezone = ""
                status = ""

                # FILTER: skip kalau kompetitor / taster / kopi
                if any(x in bio for x in ["exporter", "exportir", "produce cocoa", "coffee", "barista", "review", "tasting"]):
                    continue

                if last_post.year < 2020:
                    continue  # Skip kalau terlalu lama

                emails_bio = re.findall(r"[\w\.-]+@[\w\.-]+", bio)
                if emails_bio:
                    email_ig = emails_bio[0]

                if website:
                    try:
                        res = requests.get(website, timeout=10)
                        if res.status_code != 200:
                            continue
                        soup = BeautifulSoup(res.text, 'html.parser')
                        emails_web = re.findall(r"[\w\.-]+@[\w\.-]+", soup.get_text())
                        if emails_web:
                            email_web = emails_web[0]
                        text_content = soup.get_text().strip()
                        if text_content:
                            language = detect(text_content)

                        if any(x in website for x in ['.jp', 'japan']):
                            timezone = "Asia/Tokyo"
                        elif any(x in website for x in ['.fr', 'france']):
                            timezone = "Europe/Paris"
                        elif any(x in website for x in ['.de', 'germany']):
                            timezone = "Europe/Berlin"
                        elif any(x in website for x in ['.id', 'indonesia']):
                            timezone = "Asia/Jakarta"
                        else:
                            timezone = "Etc/GMT"
                    except:
                        pass

                email_to_check = email_web or email_ig
                if email_to_check and email_to_check in existing_emails:
                    continue

                # Kalau gak ada email tapi last post ≥ 2024, tetap ambil
                if not email_to_check and last_post.year >= 2024:
                    status = "✅ Valid (2024 active, no email)"
                elif email_to_check:
                    status = "✅ Valid"
                else:
                    continue

                # Detect ISO 639-1 code
                if not language:
                    language = "en"

                # Timezone fallback
                if not timezone:
                    timezone = "Etc/GMT"

                # SIMPAN LEADS
                new_leads_sheet.append_row([
                    username, full_name, bio, website, email_ig, email_web, language, timezone, str(last_post.date()), status
                ])

                processed += 1
                print(f"✅ Saved lead: {username} ({last_post.date()})")

                if processed >= max_leads:
                    break

                time.sleep(random.randint(60, 90))  # Delay per profil

            except Exception as e:
                print(f"❌ Error: {e}")
                continue

        if processed >= max_leads:
            break

    print("✅ DONE: Leads berhasil dikumpulkan ke sheet New Leads")

# === STEP 3: FLASK ROUTE ===
@app.route('/')
def home():
    return "Lead Hunter is running!"

@app.route('/get-leads')
def run_leads():
    # Start the leads scraping in a new thread
    threading.Thread(target=get_leads).start()
    return "Lead collection started in the background."

if __name__ == "__main__":
    app.run(debug=True)
