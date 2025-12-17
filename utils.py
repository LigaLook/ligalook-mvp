# utils.py
import streamlit as st
import hashlib
import smtplib
from email.mime.text import MIMEText
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- GOOGLE SHEETS VERBINDUNG ---
def get_db_connection(sheet_name):
    """Verbindet sich mit Google Sheets."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def load_users(sheet_name):
    """Lädt alle User."""
    try:
        sheet = get_db_connection(sheet_name)
        records = sheet.get_all_records()
        # Macht ein Dict: {email: passwort}
        return {row['email']: row['password'] for row in records if row['email']}
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return {}

def save_user(sheet_name, email, password):
    """Speichert neuen User."""
    try:
        sheet = get_db_connection(sheet_name)
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        sheet.append_row([email, hashed_pw])
        return True
    except Exception as e:
        st.error(f"Speichern fehlgeschlagen: {e}")
        return False

# --- E-MAIL FUNKTION ---
def send_verification_email(to_email, code):
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]

        msg = MIMEText(f"Dein LigaLook Code ist: {code}")
        msg['Subject'] = "Dein Login Code"
        msg['From'] = sender_email
        msg['To'] = to_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Mail-Fehler: {e}")
        return False

# --- LOGIN CHECK ---
def check_credentials(sheet_name, email, password):
    users = load_users(sheet_name)
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if email in users and str(users[email]) == hashed_pw:
        return True
    return False
