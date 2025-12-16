import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import json
import os
import hashlib

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="LigaLook", page_icon="⚽", layout="wide")

# Name der Datei, in der wir User speichern
DB_FILE = "users.json"

# --- 2. HILFSFUNKTIONEN (DATENBANK) ---
def load_users():
    """Lädt die User aus der JSON-Datei. Wenn keine da ist, erstellt sie eine leere."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_user(username, password):
    """Speichert einen neuen User."""
    users = load_users()
    # Wir hashen das Passwort für minimale Sicherheit (SHA256)
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[username] = hashed_pw
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def check_credentials(username, password):
    """Prüft, ob User und Passwort stimmen."""
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    if username in users and users[username] == hashed_pw:
        return True
    return False

# --- 3. LOGIN & REGISTRIERUNG SYSTEM ---
def login_screen():
    st.markdown("## ⚽ Willkommen bei LigaLook")
    
    tab1, tab2 = st.tabs(["🔒 Einloggen", "📝 Registrieren"])

    with tab1:
        st.write("Bitte melde dich an.")
        login_user = st.text_input("Benutzername", key="login_user")
        login_pw = st.text_input("Passwort", type="password", key="login_pw")
        
        if st.button("Einloggen"):
            if check_credentials(login_user, login_pw):
                st.session_state["logged_in"] = True
                st.session_state["username"] = login_user
                st.rerun()
            else:
                st.error("Falscher Benutzername oder Passwort.")

    with tab2:
        st.write("Neu hier? Erstelle einen Account.")
        new_user = st.text_input("Neuer Benutzername", key="new_user")
        new_pw = st.text_input("Neues Passwort", type="password", key="new_pw")
        
        if st.button("Kostenlos Registrieren"):
            users = load_users()
            if new_user in users:
                st.error("Dieser Benutzername ist schon vergeben.")
            elif new_user and new_pw:
                save_user(new_user, new_pw)
                st.success("Erfolgreich registriert! Du kannst dich jetzt im Tab 'Einloggen' anmelden.")
            else:
                st.warning("Bitte fülle beide Felder aus.")

# --- 4. DIE HAUPT-APP (Nur sichtbar wenn eingeloggt) ---
def main_app():
    # Logout Button in der Sidebar
    with st.sidebar:
        st.write(f"Angemeldet als: **{st.session_state['username']}**")
        if st.button("Abmelden"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.markdown("---")

    # Hilfsfunktion: Schriftart laden
    def load_font(size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except IOError:
                return ImageFont.load_default()

    # HEADER
    st.title("⚽ LigaLook Dashboard")
    st.markdown("Dein automatischer Matchday-Designer")
    st.info("Lade hier deine Excel-Liste hoch.")

    # SIDEBAR DESIGN
    st.sidebar.header("🎨 Design Einstellungen")
    uploaded_bg = st.sidebar.file_uploader("1. Hintergrundbild (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    text_color = st.sidebar.color_picker("Textfarbe", "#FFFFFF")
    font_size = st.sidebar.slider("Schriftgröße", 10, 200, 60)
    
    # Initiale Werte für Bildgröße (Fallback)
    img_width, img_height = 800, 600
    if uploaded_bg:
        img = Image.open(uploaded_bg)
        img_width, img_height = img.size
    
    x_pos = st.sidebar.slider("X-Position", 0, img_width, int(img_width/2))
    y_pos = st.sidebar.slider("Y-Position", 0, img_height, int(img_height/2))
    use_watermark = st.sidebar.checkbox("Wasserzeichen", value=True)

    # MAIN AREA
    uploaded_excel = st.file_uploader("2. Excel-Liste hochladen", type=['xlsx'])

    if uploaded_excel and uploaded_bg:
        try:
            df = pd.read_excel(uploaded_excel)
            st.data_editor(df, num_rows="dynamic")
            
            if st.button("🚀 Grafiken generieren", type="primary"):
                cols = st.columns(3)
                for index, row in df.iterrows():
                    img = Image.open(uploaded_bg).convert("RGBA")
                    draw = ImageDraw.Draw(img)
                    font = load_font(font_size)
                    
                    # Text Logik
                    full_text = f"{row.get('Heim', 'Heim')} vs {row.get('Gast', 'Gast')}\n{row.get('Ergebnis', '-:-')} | {row.get('Liga', 'Liga')}"
                    
                    draw.text((x_pos, y_pos), full_text, fill=text_color, font=font, anchor="mm", align="center")
                    
                    if use_watermark:
                        w_font = load_font(20)
                        draw.text((img_width - 20, img_height - 30), "Created with LigaLook", fill="white", font=w_font, anchor="rm")

                    # Speichern für Download
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG")
                    byte_im = buf.getvalue()
                    
                    filename = f"Match_{index}.jpg"
                    with cols[index % 3]:
                        st.image(byte_im, use_column_width=True)
                        st.download_button("Download", byte_im, filename, mime="image/jpeg", key=f"dl_{index}")
                        
        except Exception as e:
            st.error(f"Fehler beim Verarbeiten: {e}")

# --- 5. STEUERUNG (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_screen()
