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

# --- 2. HILFSFUNKTIONEN (EMAIL & DATENBANK) ---

def send_verification_email(to_email, code):
    """Sendet den 4-stelligen Code per E-Mail."""
    try:
        # Wir holen die Zugangsdaten aus den Secrets
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]

        msg = MIMEText(f"Hallo!\n\nDein Bestätigungscode für LigaLook ist: {code}\n\nViel Erfolg!")
        msg['Subject'] = "Dein Code für LigaLook"
        msg['From'] = sender_email
        msg['To'] = to_email

        # Verbindung zum Server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Verschlüsselung starten
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Fehler beim Mail-Versand: {e}")
        return False

def load_users():
    """Lädt User aus der lokalen Datei."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_user(email, password):
    """Speichert neuen User."""
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[email] = hashed_pw
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def check_credentials(email, password):
    """Prüft Login-Daten."""
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if email in users and users[email] == hashed_pw:
        return True
    return False

# --- 3. LOGIN & REGISTRIERUNG ---

def login_system():
    st.markdown("## ⚽ LigaLook Zugang")
    
    tab1, tab2 = st.tabs(["Einloggen", "Registrieren"])

    # --- TAB 1: LOGIN ---
    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        password = st.text_input("Passwort", type="password", key="login_pw")
        
        if st.button("Anmelden", type="primary"):
            if check_credentials(email, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = email
                st.rerun()
            else:
                st.error("E-Mail oder Passwort falsch.")

    # --- TAB 2: REGISTRIERUNG ---
    with tab2:
        # Schritt 1: E-Mail eingeben
        if "reg_phase" not in st.session_state:
            st.session_state["reg_phase"] = 1

        if st.session_state["reg_phase"] == 1:
            st.write("Erstelle einen Account mit deiner E-Mail.")
            reg_email = st.text_input("Deine E-Mail Adresse", key="reg_email")
            
            if st.button("Code anfordern"):
                users = load_users()
                if reg_email in users:
                    st.warning("Diese E-Mail ist schon registriert. Bitte einloggen.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.warning("Bitte gültige E-Mail eingeben.")
                else:
                    # Code generieren
                    code = str(random.randint(1000, 9999))
                    st.session_state["verification_code"] = code
                    st.session_state["reg_email_target"] = reg_email
                    
                    with st.spinner("Sende E-Mail..."):
                        success = send_verification_email(reg_email, code)
                    
                    if success:
                        st.session_state["reg_phase"] = 2
                        st.success(f"Code wurde an {reg_email} gesendet!")
                        st.rerun()
        
        # Schritt 2: Code prüfen
        elif st.session_state["reg_phase"] == 2:
            st.info(f"Code gesendet an: {st.session_state['reg_email_target']}")
            
            entered_code = st.text_input("4-stelligen Code eingeben", key="code_input")
            new_pw = st.text_input("Neues Passwort wählen", type="password", key="new_pw")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Registrierung abschließen"):
                    if entered_code == st.session_state["verification_code"]:
                        if len(new_pw) < 4:
                            st.warning("Passwort zu kurz (min 4 Zeichen).")
                        else:
                            save_user(st.session_state["reg_email_target"], new_pw)
                            st.success("Account erstellt! Du kannst dich jetzt einloggen.")
                            # Aufräumen
                            del st.session_state["reg_phase"]
                            del st.session_state["verification_code"]
                            st.balloons()
                    else:
                        st.error("Falscher Code.")
            with col2:
                if st.button("Zurück / Email ändern"):
                    st.session_state["reg_phase"] = 1
                    st.rerun()

# --- 4. HAUPT-APP (DEIN TOOL) ---
def main_app():
    # Logout Button Sidebar
    with st.sidebar:
        st.write(f"Angemeldet: **{st.session_state['username']}**")
        if st.button("Ausloggen"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()

    # Hilfsfunktion Font
    def load_font(size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            return ImageFont.load_default()

    # HEADER
    st.title("⚽ LigaLook Dashboard")
    st.markdown("Dein automatischer Matchday-Designer")

    # SIDEBAR SETTINGS
    st.sidebar.header("🎨 Design Einstellungen")
    
    uploaded_bg = st.sidebar.file_uploader("1. Hintergrundbild (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

    # Standardwerte, falls kein Bild da ist
    img_width, img_height = 800, 600
    if uploaded_bg:
        img_temp = Image.open(uploaded_bg)
        img_width, img_height = img_temp.size
    
    st.sidebar.subheader("Text Style")
    text_color = st.sidebar.color_picker("Textfarbe", "#FFFFFF")
    font_size = st.sidebar.slider("Schriftgröße", 10, 200, 60)

    st.sidebar.subheader("Position")
    x_pos = st.sidebar.slider("X-Position", 0, img_width, int(img_width/2))
    y_pos = st.sidebar.slider("Y-Position", 0, img_height, int(img_height/2))
    
    use_watermark = st.sidebar.checkbox("Wasserzeichen anzeigen", value=True)

    # MAIN AREA
    st.subheader("📋 Daten Upload")
    uploaded_excel = st.file_uploader("2. Excel-Liste hochladen (.xlsx)", type=['xlsx'])

    if uploaded_excel and uploaded_bg:
        try:
            df = pd.read_excel(uploaded_excel)
            
            # Prüfen ob Spalten da sind
            needed = ["Heim", "Gast", "Ergebnis", "Liga"]
            if not all(col in df.columns for col in needed):
                st.error(f"Excel braucht Spalten: {needed}")
            else:
                st.data_editor(df, num_rows="dynamic")
                
                if st.button("🚀 Grafiken jetzt generieren", type="primary"):
                    st.success(f"Erstelle Bilder...")
                    cols = st.columns(3)
                    
                    for index, row in df.iterrows():
                        img = Image.open(uploaded_bg).convert("RGBA")
                        draw = ImageDraw.Draw(img)
                        font = load_font(font_size)
                        
                        # Text zusammenbauen
                        full_text = f"{row['Heim']} vs {row['Gast']}\n{row['Ergebnis']} | {row['Liga']}"
                        
                        # Zeichnen
                        draw.text((x_pos, y_pos), full_text, fill=text_color, font=font, anchor="mm", align="center")
                        
                        # Wasserzeichen
                        if use_watermark:
                            w_font = load_font(20)
                            draw.text((img_width - 20, img_height - 30), "Created with LigaLook", fill="white", font=w_font, anchor="rm")

                        # Speichern
                        buf = io.BytesIO()
                        img.convert("RGB").save(buf, format="JPEG")
                        byte_im = buf.getvalue()
                        
                        filename = f"Match_{row['Heim']}_{row['Gast']}.jpg"
                        
                        with cols[index % 3]:
                            st.image(byte_im, use_column_width=True)
                            st.download_button("Download", byte_im, filename, mime="image/jpeg", key=f"dl_{index}")
                    
                    st.balloons()
                        
        except Exception as e:
            st.error(f"Fehler: {e}")
    elif not uploaded_excel:
        st.info("Bitte Excel hochladen.")
    elif not uploaded_bg:
        st.info("Bitte Hintergrundbild hochladen.")

# --- 5. STEUERUNG (MAIN LOOP) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()
