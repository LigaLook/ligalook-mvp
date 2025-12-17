import streamlit as st
import streamlit.components.v1 as components
import utils 
import designer_code 
import legal  # <--- NEU: Deine Texte importieren

# --- KONFIGURATION ---
st.set_page_config(page_title="LigaLook Designer", page_icon="⚽", layout="wide")
SHEET_NAME = "LigaLook Users"

# --- OPTIK ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- NEU: DIE POP-UP FUNKTIONEN ---
@st.dialog("Rechtliche Hinweise")
def open_legal_modal(category):
    if category == "impressum":
        st.markdown(legal.IMPRESSUM_TEXT)
    elif category == "datenschutz":
        st.markdown(legal.DATENSCHUTZ_TEXT)

# --- LOGIN SCREEN ---
def login_system():
    st.markdown("## ⚽ LigaLook Login")
    tab1, tab2, tab3 = st.tabs(["🔒 Einloggen", "📝 Registrieren", "❓ Passwort vergessen"]) # <--- Neuer Tab

    # --- TAB 1: LOGIN ---
    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        pw = st.text_input("Passwort", type="password", key="login_pw")
        if st.button("Anmelden", type="primary"):
            if utils.check_credentials(SHEET_NAME, email, pw):
                st.session_state["logged_in"] = True
                st.session_state["username"] = email
                st.rerun()
            else:
                st.error("E-Mail oder Passwort falsch.")

    # --- TAB 2: REGISTRIEREN ---
    with tab2:
        # ... (Dein bisheriger Registrierungs-Code bleibt hier unverändert stehen) ...
        # (Um Platz zu sparen, kopiere hier einfach deinen alten Tab 2 Code rein)
        if "reg_step" not in st.session_state:
            st.session_state["reg_step"] = 1
            
        if st.session_state["reg_step"] == 1:
            r_email = st.text_input("E-Mail für Account", key="reg_email")
            if st.button("Code anfordern", key="reg_btn"):
                users = utils.load_users(SHEET_NAME)
                if r_email in users:
                    st.warning("Account existiert schon.")
                else:
                    import random
                    code = str(random.randint(1000, 9999))
                    st.session_state["code"] = code
                    st.session_state["target"] = r_email
                    if utils.send_verification_email(r_email, code):
                        st.session_state["reg_step"] = 2
                        st.rerun()
        
        elif st.session_state["reg_step"] == 2:
            st.info(f"Code gesendet an {st.session_state['target']}")
            code_in = st.text_input("Code eingeben", key="code_in")
            pw_in = st.text_input("Passwort wählen", type="password", key="reg_pw")
            
            if st.button("Account erstellen"):
                if code_in == st.session_state["code"]:
                    utils.save_user(SHEET_NAME, st.session_state["target"], pw_in)
                    st.success("Erstellt! Bitte einloggen.")
                    st.session_state["reg_step"] = 1
                    st.rerun()
                else:
                    st.error("Falscher Code")

    # --- TAB 3: PASSWORT VERGESSEN (NEU!) ---
    with tab3:
        st.write("Kein Problem. Wir senden dir einen Code, um es zurückzusetzen.")
        
        if "reset_step" not in st.session_state:
            st.session_state["reset_step"] = 1
            
        # Schritt 1: Email prüfen
        if st.session_state["reset_step"] == 1:
            reset_email = st.text_input("Deine E-Mail", key="reset_email")
            if st.button("Code senden", key="reset_btn_send"):
                users = utils.load_users(SHEET_NAME)
                if reset_email not in users:
                    st.error("Diese E-Mail kennen wir nicht.")
                else:
                    import random
                    code = str(random.randint(1000, 9999))
                    st.session_state["reset_code"] = code
                    st.session_state["reset_target"] = reset_email
                    
                    if utils.send_verification_email(reset_email, code):
                        st.session_state["reset_step"] = 2
                        st.rerun()
        
        # Schritt 2: Code & Neues PW
        elif st.session_state["reset_step"] == 2:
            st.info(f"Code an {st.session_state['reset_target']} gesendet.")
            
            r_code = st.text_input("Code aus E-Mail", key="reset_code_in")
            r_new_pw = st.text_input("Neues Passwort", type="password", key="reset_new_pw")
            
            if st.button("Passwort ändern"):
                if r_code == st.session_state["reset_code"]:
                    if utils.update_password(SHEET_NAME, st.session_state["reset_target"], r_new_pw):
                        st.success("Passwort geändert! Du kannst dich jetzt einloggen.")
                        st.session_state["reset_step"] = 1
                        st.balloons()
                    else:
                        st.error("Fehler beim Speichern.")
                else:
                    st.error("Falscher Code.")

    # --- FOOTER MIT BUTTONS (statt Links) ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 4]) # Kleine Spalten für die Buttons
    with col1:
        if st.button("Impressum"):
            open_legal_modal("impressum")
    with col2:
        if st.button("Datenschutz"):
            open_legal_modal("datenschutz")

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.write(f"User: **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        
        st.divider()
        # Buttons in der Sidebar
        if st.button("Impressum", key="sidebar_imp"):
            open_legal_modal("impressum")
        if st.button("Datenschutz", key="sidebar_dat"):
            open_legal_modal("datenschutz")
    
    # Designer laden
    components.html(designer_code.HTML_CONTENT, height=1100, scrolling=False)

# --- STEUERUNG ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()
