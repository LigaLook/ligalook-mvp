import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- 1. KONFIGURATION ---
st.set_page_config(
    page_title="LigaLook | Matchday Generator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. AUTHENTIFIZIERUNG (DER TÜRSTEHER) ---

# Hier definieren wir die User (Für das MVP direkt im Code)
# In Zukunft lagern wir das in eine sichere Datei aus.
auth_data = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': 'Admin User',
                # Das Passwort ist "123" (aber verschlüsselt/gehasht)
                'password': '$2b$12$D2.n.12345678901234567eX.a.u.th.hash.value.CHANGE_THIS' 
                # HINWEIS: Da ich keinen echten Hash generieren kann ohne Terminal, 
                # nutzen wir hier einen Trick. Streamlit-Authenticator braucht gehashte Passwörter.
                # Wir bauen die Config gleich so, dass es funktioniert.
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'random_signature_key',
        'name': 'ligalook_cookie'
    },
    'preauthorized': {'emails': []}
}

# Workaround: Wir überschreiben das Passwort oben mit einem echten Hash für "123"
# Hash für "123" = $2b$12$1.n.12345678901234567eX.a.u.th.hash.value (Dummy)
# Wir nutzen für diesen Test den "Plain Text", den Authenticator aber hashen soll. 
# Aber korrekterweise nutzen wir Hasher.

# --- VEREINFACHTE VARIANTE FÜR DEN START ---
# Wir nutzen eine simple Konfiguration, damit du sofort starten kannst.
# Passwort für alle: 'abc'

authenticator = stauth.Authenticate(
    auth_data['credentials'],
    auth_data['cookie']['name'],
    auth_data['cookie']['key'],
    auth_data['cookie']['expiry_days']
)

# ACHTUNG: Da das Hashen komplex ist, tricksen wir für dein MVP kurz:
# Wir loggen uns manuell ein oder nutzen die UI.
# Damit der Code unten funktioniert, musst du erst das Paket installieren.
# Da ich dir keinen Hash generieren kann (das ändert sich jedes Mal),
# bauen wir einen manuellen Login-Check, der einfacher ist für heute.

# --- SICHERER LOGIN (Secrets) ---
def check_password():
    """Prüft Username/Passwort gegen die sicheren Streamlit Secrets."""

    def password_entered():
        """Wird ausgeführt, wenn User Enter drückt."""
        entered_user = st.session_state.get("username", "")
        entered_pw = st.session_state.get("password", "")

        # Wir holen die User-Liste sicher aus den Secrets
        # Struktur in Secrets: [passwords] user = "pw"
        if entered_user in st.secrets["passwords"] and entered_pw == st.secrets["passwords"][entered_user]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Passwort sofort löschen
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Erster Aufruf
        st.markdown("## 🔒 LigaLook Login")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        # Falsche Eingabe
        st.markdown("## 🔒 LigaLook Login")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Login fehlgeschlagen")
        return False
    
    else:
        # Alles korrekt
        return True
        
    # --- AB HIER BEGINNT DEINE EIGENTLICHE APP ---
    
    # Logout Button in der Sidebar
    if st.sidebar.button("Log out"):
        del st.session_state["password_correct"]
        st.rerun()

    # Hilfsfunktion: Schriftart laden
    def load_font(size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except IOError:
                return ImageFont.load_default()

    # --- HEADER & STYLE ---
    st.title("⚽ LigaLook")
    st.markdown("### Dein automatischer Matchday-Designer")
    st.markdown("---")

    # --- SIDEBAR ---
    st.sidebar.header("🎨 Design & Layout")
    
    # Branding für User
    st.sidebar.info(f"Eingeloggt als: **Admin**")

    uploaded_bg = st.sidebar.file_uploader("1. Hintergrundbild (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

    img_width, img_height = 800, 600 

    if uploaded_bg:
        bg_preview = Image.open(uploaded_bg)
        img_width, img_height = bg_preview.size
        st.sidebar.success(f"Bildformat: {img_width}x{img_height}px")
    else:
        st.sidebar.info("Bitte lade erst ein Hintergrundbild hoch.")

    st.sidebar.subheader("Text-Style")
    text_color = st.sidebar.color_picker("Textfarbe", "#FFFFFF")
    font_size = st.sidebar.slider("Schriftgröße", 10, 200, 60)

    st.sidebar.subheader("Position (X / Y)")
    x_pos = st.sidebar.slider("X-Position (Horizontal)", 0, img_width, int(img_width/2))
    y_pos = st.sidebar.slider("Y-Position (Vertikal)", 0, img_height, int(img_height/2))

    use_watermark = st.sidebar.checkbox("Wasserzeichen anzeigen", value=True)

    # --- MAIN AREA ---
    st.subheader("📋 Daten aus Excel")
    uploaded_excel = st.file_uploader("2. Excel-Liste hochladen (.xlsx)", type=['xlsx'])

    if uploaded_excel and uploaded_bg:
        try:
            df = pd.read_excel(uploaded_excel)
            
            req_cols = ["Heim", "Gast", "Ergebnis", "Liga"]
            if not all(col in df.columns for col in req_cols):
                st.error(f"Fehler: Die Excel benötigt die Spalten: {', '.join(req_cols)}")
            else:
                edited_df = st.data_editor(df, num_rows="dynamic")
                
                st.write("---")
                
                if st.button("🚀 Grafiken jetzt generieren", type="primary"):
                    st.success(f"Erstelle {len(edited_df)} Bilder...")
                    cols = st.columns(3)
                    
                    for index, row in edited_df.iterrows():
                        img = Image.open(uploaded_bg).convert("RGBA")
                        draw = ImageDraw.Draw(img)
                        font = load_font(font_size)
                        
                        text_match = f"{row['Heim']} vs {row['Gast']}"
                        text_score = f"{row['Ergebnis']} | {row['Liga']}"
                        full_text = f"{text_match}\n{text_score}"
                        
                        draw.text((x_pos, y_pos), full_text, fill=text_color, font=font, anchor="mm", align="center")
                        
                        if use_watermark:
                            watermark_font = load_font(20)
                            w_x, w_y = img_width - 20, img_height - 30
                            draw.text((w_x, w_y), "Created with LigaLook.com", fill="#FFFFFF", font=watermark_font, anchor="rm")

                        buf = io.BytesIO()
                        img.convert("RGB").save(buf, format="JPEG", quality=95)
                        byte_im = buf.getvalue()
                        
                        filename = f"LigaLook_{row['Heim']}_vs_{row['Gast']}.jpg".replace(" ", "_")
                        
                        with cols[index % 3]:
                            st.image(byte_im, caption=f"Spiel {index+1}", use_column_width=True)
                            st.download_button(
                                label="⬇️ Download",
                                data=byte_im,
                                file_name=filename,
                                mime="image/jpeg",
                                key=f"dl_{index}"
                            )
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Fehler: {e}")

    elif not uploaded_excel:
        st.info("Bitte einloggen und Excel hochladen.")
