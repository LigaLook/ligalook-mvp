import streamlit as st
import streamlit.components.v1 as components
import utils 
import designer_code # <--- WICHTIG: Das ist deine neue Datei!

# --- KONFIGURATION ---
st.set_page_config(page_title="LigaLook Designer", page_icon="⚽", layout="wide")
# --- OPTIK: STREAMLIT BRANDING AUSBLENDEN ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
SHEET_NAME = "LigaLook Users"

# --- LOGIN SCREEN ---
def login_system():
    st.markdown("## ⚽ LigaLook Login")
    tab1, tab2 = st.tabs(["Einloggen", "Registrieren"])

    with tab1:
        email = st.text_input("E-Mail", key="login_email")
        pw = st.text_input("Passwort", type="password", key="login_pw")
        if st.button("Starten", type="primary"):
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
            
            if st.button("Fertigstellen"):
                if code_in == st.session_state["code"]:
                    utils.save_user(SHEET_NAME, st.session_state["target"], pw_in)
                    st.success("Erstellt! Bitte einloggen.")
                    st.session_state["reg_step"] = 1
                    st.rerun()
                else:
                    st.error("Falscher Code")

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.write(f"User: **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    # Hier laden wir den Code aus der Variable
    components.html(designer_code.HTML_CONTENT, height=1100, scrolling=False)

# --- STEUERUNG ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login_system()

st.markdown("---")
st.markdown("[Impressum](https://deine-webseite.com/impressum) | [Datenschutz](https://deine-webseite.com/datenschutz)", unsafe_allow_html=True)
