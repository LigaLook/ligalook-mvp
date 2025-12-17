import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import random
# HIER IST DER TRICK: Wir importieren unsere eigenen Tools
import utils 

# --- KONFIGURATION ---
st.set_page_config(page_title="LigaLook", page_icon="⚽", layout="wide")
SHEET_NAME = "LigaLook Users"

# --- LOGIN SCREEN (Benutzt jetzt utils) ---
def login_system():
    st.markdown("## ⚽ LigaLook Login")
    tab1, tab2 = st.tabs(["Einloggen", "Registrieren"])

    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        pw = st.text_input("Passwort", type="password", key="login_pw")
        if st.button("Starten", type="primary"):
            # Aufruf der Funktion aus der utils Datei
            if utils.check_credentials(SHEET_NAME, email, pw):
                st.session_state["logged_in"] = True
                st.session_state["username"] = email
                st.rerun()
            else:
                st.error("Falsche Daten.")

    with tab2:
        if "reg_step" not in st.session_state:
            st.session_state["reg_step"] = 1
            
        if st.session_state["reg_step"] == 1:
            r_email = st.text_input("E-Mail für Account", key="reg_email")
            if st.button("Code senden"):
                users = utils.load_users(SHEET_NAME)
                if r_email in users:
                    st.warning("Account existiert schon.")
                else:
                    code = str(random.randint(1000, 9999))
                    st.session_state["code"] = code
                    st.session_state["target"] = r_email
                    # Mail senden über utils
                    if utils.send_verification_email(r_email, code):
                        st.session_state["reg_step"] = 2
                        st.rerun()
        
        elif st.session_state["reg_step"] == 2:
            st.info(f"Code gesendet an {st.session_state['target']}")
            code_in = st.text_input("Code eingeben", key="code_in")
            pw_in = st.text_input("Passwort wählen", type="password", key="reg_pw")
            
            if st.button("Fertigstellen"):
                if code_in == st.session_state["code"]:
                    # Speichern über utils
                    utils.save_user(SHEET_NAME, st.session_state["target"], pw_in)
                    st.success("Erstellt! Bitte einloggen.")
                    st.session_state["reg_step"] = 1
                    st.balloons()
                else:
                    st.error("Falscher Code")

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.write(f"User: {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    # --- DEIN DESIGNER ---
    st.title("⚽ LigaLook Dashboard")
    st.sidebar.header("Design")
    
    uploaded_bg = st.sidebar.file_uploader("Hintergrundbild", type=['jpg', 'png'])
    text_color = st.sidebar.color_picker("Textfarbe", "#FFFFFF")
    font_size = st.sidebar.slider("Größe", 10, 200, 60)
    
    uploaded_excel = st.file_uploader("Excel Datei", type=['xlsx'])
    
    # ... Hier kommt deine Grafik-Logik (unverändert) ...
    # Wenn du willst, können wir die Grafik-Logik später AUCH in eine grafik_utils.py packen!
    
    if uploaded_excel and uploaded_bg:
        try:
            df = pd.read_excel(uploaded_excel)
            st.data_editor(df)
            if st.button("Bilder generieren"):
                st.success("Funktion aktiv!")
        except Exception as e:
            st.error(f"Fehler: {e}")

# --- STEUERUNG ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()
