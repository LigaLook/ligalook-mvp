import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import json
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
import random
import time

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="LigaLook", page_icon="⚽", layout="wide")

DB_FILE = "users.json"

# --- 2. HILFSFUNKTIONEN ---

def send_verification_email(to_email, code):
    """Sendet den Bestätigungscode per E-Mail."""
    try:
        # Daten aus den Secrets laden
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]

        msg = MIMEText(f"Hallo!\n\nDein Bestätigungscode für LigaLook ist: {code}\n\nViel Erfolg beim Spiel!")
        msg['Subject'] = "Dein Code für LigaLook"
        msg['From'] = sender_email
        msg['To'] = to_email

        # Senden
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Mail-Versand: {e}")
        return False

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_user(email, password):
    users = load_users()
    # Passwort verschlüsseln
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[email] = hashed_pw
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def check_credentials(email, password):
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if email in users and users[email] == hashed_pw:
        return True
    return False

# --- 3. LOGIN & REGISTRIERUNG ---

def login_system():
    st.markdown("## ⚽ LigaLook Zugang")
    
    # Tabs umschalten
    tab1, tab2 = st.tabs(["Einloggen", "Registrieren (mit E-Mail)"])

    # --- LOGIN TAB ---
    with tab1:
        st.write("Bereits registriert?")
        email = st.text_input("E-Mail", key="login_email")
        password = st.text_input("Passwort", type="password", key="login_pw")
        
        if st.button("Anmelden", type="primary"):
            if check_credentials(email, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = email
                st.rerun()
            else:
                st.error("Falsche Daten oder User nicht gefunden.")

    # --- REGISTRIERUNG TAB ---
    with tab2:
        st.write("Neu hier?")
        
        # Schritt 1: E-Mail eingeben
        if "reg_phase" not in st.session_state:
            st.session_state["reg_phase"] = 1

        if st.session_state["reg_phase"] == 1:
            reg_email = st.text_input("Deine E-Mail Adresse", key="reg_email")
            
            if st.button("Code anfordern"):
                users = load_users()
                if reg_email in users:
                    st.warning("Diese E-Mail gibt es schon. Bitte einloggen.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.warning("Ungültige E-Mail.")
                else:
                    # Code generieren
                    code = str(random.randint(1000, 9999))
                    st.session_state["verification_code"] = code
                    st.session_state["reg_email_target"] = reg_email
                    
                    with st.spinner("Sende E-Mail..."):
                        success = send_verification_email(reg_email, code)
                    
                    if success:
                        st.session_state["reg_phase"] = 2
                        st.success(f"Code an {reg_email} gesendet!")
                        st.rerun()
        
        # Schritt 2: Code eingeben
        elif st.session_state["reg_phase"] == 2:
            st.info(f"Code wurde an {st.session_state['reg_email_target']} gesendet.")
            
            entered_code = st.text_input("4-stelligen Code eingeben", key="code_input")
            new_pw = st.text_input("Neues Passwort wählen", type="password", key="new_pw")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Registrierung abschließen"):
                    if entered_code == st.session_state["verification_code"]:
                        if len(new_pw) < 4:
                            st.warning("Passwort zu kurz.")
                        else:
                            save_user(st.session_state["reg_email_target"], new_pw)
                            st.success("Account erstellt! Du kannst dich jetzt einloggen.")
                            # Reset
                            del st.session_state["reg_phase"]
                            del st.session_state["verification_code"]
                            st.balloons()
                    else:
                        st.error("Falscher Code.")
            with col2:
                if st.button("Zurück"):
                    st.session_state["reg_phase"] = 1
                    st.rerun()

# --- 4. HAUPT-APP ---
def main_app():
    with st.sidebar:
        st.write(f"User: **{st.session_state['username']}**")
        if st.button("Ausloggen"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
    
    # HIER DEIN DESIGNER CODE (gekürzt für Übersicht)
    st.title("⚽ LigaLook Dashboard")
    
    # Sidebar Settings
    st.sidebar.header("Design")
    uploaded_bg = st.sidebar.file_uploader("Hintergrundbild", type=['jpg', 'png'])
    text_color = st.sidebar.color_picker("Farbe", "#FFFFFF")
    
    uploaded_excel = st.file_uploader("Excel hochladen", type=['xlsx'])
    
    if uploaded_excel and uploaded_bg:
        try:
            df = pd.read_excel(uploaded_excel)
            st.data_editor(df)
            if st.button("🚀 Generieren"):
                st.balloons()
                st.success("Funktion aktiv! (Code gekürzt)")
        except:
            st.error("Fehler beim Laden.")

# --- 5. STEUERUNG ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()
