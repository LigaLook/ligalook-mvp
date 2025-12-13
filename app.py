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

# Hilfsfunktion: Schriftart laden (Fallback für Server)
def load_font(size):
    try:
        # Standard Arial (Windows/Mac)
        return ImageFont.truetype("arial.ttf", size)
    except IOError:
        try:
            # Linux Standard (Streamlit Cloud)
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except IOError:
            # Notfall-Fallback
            return ImageFont.load_default()

# --- 2. HEADER & STYLE ---
st.title("⚽ LigaLook")
st.markdown("### Dein automatischer Matchday-Designer")
st.markdown("---")

# --- 3. SIDEBAR (EINSTELLUNGEN) ---
st.sidebar.header("🎨 Design & Layout")

# A. Hintergrund
uploaded_bg = st.sidebar.file_uploader("1. Hintergrundbild (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

# Standard-Werte für Bildgröße
img_width, img_height = 800, 600 

if uploaded_bg:
    bg_preview = Image.open(uploaded_bg)
    img_width, img_height = bg_preview.size
    st.sidebar.success(f"Bildformat: {img_width}x{img_height}px")
else:
    st.sidebar.info("Bitte lade erst ein Hintergrundbild hoch.")

# B. Text-Style
st.sidebar.subheader("Text-Style")
text_color = st.sidebar.color_picker("Textfarbe", "#FFFFFF")
font_size = st.sidebar.slider("Schriftgröße", 10, 200, 60)

# C. Positionierung
st.sidebar.subheader("Position (X / Y)")
x_pos = st.sidebar.slider("X-Position (Horizontal)", 0, img_width, int(img_width/2))
y_pos = st.sidebar.slider("Y-Position (Vertikal)", 0, img_height, int(img_height/2))

# D. Branding Checkbox
use_watermark = st.sidebar.checkbox("Wasserzeichen anzeigen", value=True)

# --- 4. MAIN AREA (DATEN) ---
st.subheader("📋 Daten aus Excel")
uploaded_excel = st.file_uploader("2. Excel-Liste hochladen (.xlsx)", type=['xlsx'])

if uploaded_excel and uploaded_bg:
    try:
        # Excel laden
        df = pd.read_excel(uploaded_excel)
        
        # Prüfung der Spalten
        req_cols = ["Heim", "Gast", "Ergebnis", "Liga"]
        if not all(col in df.columns for col in req_cols):
            st.error(f"Fehler: Die Excel benötigt die Spalten: {', '.join(req_cols)}")
        else:
            # Editierbare Tabelle
            edited_df = st.data_editor(df, num_rows="dynamic")
            
            st.write("---")
            
            # Button
            if st.button("🚀 Grafiken jetzt generieren", type="primary"):
                st.success(f"Erstelle {len(edited_df)} Bilder für dich...")
                
                # Grid für Vorschau
                cols = st.columns(3)
                
                for index, row in edited_df.iterrows():
                    # Bild öffnen
                    img = Image.open(uploaded_bg).convert("RGBA")
                    draw = ImageDraw.Draw(img)
                    font = load_font(font_size)
                    
                    # Text Logik
                    text_match = f"{row['Heim']} vs {row['Gast']}"
                    text_score = f"{row['Ergebnis']} | {row['Liga']}"
                    full_text = f"{text_match}\n{text_score}"
                    
                    # Text zeichnen (Zentriert am Anker)
                    draw.text((x_pos, y_pos), full_text, fill=text_color, font=font, anchor="mm", align="center")
                    
                    # Wasserzeichen (Branding)
                    if use_watermark:
                        watermark_font = load_font(20)
                        w_x, w_y = img_width - 20, img_height - 30
                        draw.text((w_x, w_y), "Created with LigaLook.com", fill="#FFFFFF", font=watermark_font, anchor="rm")

                    # Speichern im Speicher (Buffer)
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()
                    
                    # Dateiname generieren
                    filename = f"LigaLook_{row['Heim']}_vs_{row['Gast']}.jpg".replace(" ", "_")
                    
                    # Anzeigen & Download
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
    st.info("Lade eine Excel-Datei hoch, um zu starten.")
