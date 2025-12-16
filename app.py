import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib
import smtplib
from email.mime.text import MIMEText
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="LigaLook", page_icon="⚽", layout="wide")

# Name deines Google Sheets (exakt so schreiben wie in Google Drive!)
SHEET_NAME = "LigaLook Users"

# --- 2. GOOGLE SHEETS VERBINDUNG ---
def get_db_connection():
    """Verbindet sich mit Google Sheets."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Wir laden die Credentials direkt aus den Secrets
    creds_dict = st.secrets["service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

def load_users():
    """Lädt alle User aus dem Sheet."""
    try:
        sheet = get_db_connection()
        records = sheet.get_all_records()
        # Wandelt Liste von Dicts in ein einfaches User-Dict um: {email: passwort}
        user_dict = {row['email']: row['password'] for row in records if row['email']}
        return user_dict
    except Exception as e:
        st.error(f"Datenbank-Fehler: {e}")
        return {}

def save_user(email, password):
    """Fügt neuen User ins Sheet ein."""
    try:
        sheet = get_db_connection()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        sheet.append_row([email, hashed_pw])
        return True
    except Exception as e:
        st.error(f"Konnte User nicht speichern: {e}")
        return False

# --- 3. MAIL & LOGIN LOGIK ---
def send_verification_email(to_email, code):
    try:
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]

        msg = MIMEText(f"Dein Code: {code}")
        msg['Subject'] = "LigaLook Code"
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

def check_credentials(email, password):
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if email in users and str(users[email]) == hashed_pw:
        return True
    return False

# --- 4. LOGIN SCREEN ---
def login_system():
    st.markdown("## ⚽ LigaLook Login")
    tab1, tab2 = st.tabs(["Einloggen", "Registrieren"])

    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        pw = st.text_input("Passwort", type="password", key="login_pw")
        if st.button("Starten", type="primary"):
            if check_credentials(email, pw):
                st.session_state["logged_in"] = True
                st.session_state["username"] = email
                st.rerun()
            else:
                st.error("Falsch.")

    with tab2:
        # Phase 1: Email
        if "reg_step" not in st.session_state:
            st.session_state["reg_step"] = 1
            
        if st.session_state["reg_step"] == 1:
            r_email = st.text_input("E-Mail für Account", key="reg_email")
            if st.button("Code senden"):
                users = load_users()
                if r_email in users:
                    st.warning("Gibt es schon.")
                else:
                    code = str(random.randint(1000, 9999))
                    st.session_state["code"] = code
                    st.session_state["target"] = r_email
                    if send_verification_email(r_email, code):
                        st.session_state["reg_step"] = 2
                        st.rerun()
        
        # Phase 2: Code
        elif st.session_state["reg_step"] == 2:
            st.info(f"Code an {st.session_state['target']} gesendet.")
            code_in = st.text_input("Code", key="code_in")
            pw_in = st.text_input("Passwort", type="password", key="reg_pw")
            
            if st.button("Anlegen"):
                if code_in == st.session_state["code"]:
                    save_user(st.session_state["target"], pw_in)
                    st.success("Account erstellt!")
                    st.session_state["reg_step"] = 1
                    st.balloons()
                else:
                    st.error("Falscher Code")

# --- 5. MAIN APP ---
def main_app():
    with st.sidebar:
        st.write(f"User: {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    # ... HIER DEIN DESIGNER CODE VOM VORHERIGEN SCHRITT EINFÜGEN ...
    st.title("⚽ LigaLook Dashboard")
    # (Den Rest kennst du ja schon, einfach hier reinkopieren)
    st.info("Datenbank verbunden: Google Sheets ✅")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()
