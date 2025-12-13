import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. KONFIGURATION ---
st.set_page_config(
    page_title="LigaLook | Matchday Generator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SICHERER LOGIN (NUR SECRETS) ---
def check_password():
    """Prüft Username/Passwort gegen die sicheren Streamlit Secrets."""

    def password_entered():
        """Wird ausgeführt, wenn User Enter drückt."""
        entered_user = st.session_state.get("username", "")
        entered_pw = st.session_state.get("password", "")

        # Wir holen die User-Liste sicher aus den Secrets
        if "passwords" in st.secrets:
            if entered_user in st.secrets["passwords"] and entered_pw == st.secrets["passwords"][entered_user]:
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Passwort sofort löschen
            else:
                st.session_state["password_correct"] = False
        else:
            st.error("Fehler: Keine Passwörter in den Secrets gefunden!")

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
        st.error("😕 Login fehlgeschlagen oder User unbekannt")
        return False
    
    else:
        # Alles korrekt
        return True

# --- 3. DIE EIGENTLICHE APP ---
if check_password():
    
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

    # HEADER
    st.title("⚽ LigaLook")
    st.markdown("### Dein automatischer Matchday-Designer")
    st.markdown("---")

    # SIDEBAR
    st.sidebar.header("🎨 Design & Layout")
    st.sidebar.success(f"Eingeloggt.") # Kleiner Hinweis

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

    # MAIN AREA
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
        st.info("Bitte Excel hochladen.")
