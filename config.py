import streamlit as st

# --- NGO DETAILS ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"
NGO_LAT = 31.6120 
NGO_LON = 74.8677

# --- LISTS & CATEGORIES ---
BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = [
    "--- ਕੀਰਤਨ ਸਮਾਗਮ (Samagams) ---", "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", 
    "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)", "ਲੰਗਰ (Langar)",
    "--- ਤੇਰਾ ਆਸਰਾ (Tera Aasra) ---", "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", 
    "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)", "ਹੋਰ ਖਰਚੇ (Others)"
]
STOCK_UNITS = ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)", "ਬੈਗ/ਬੋਰੀਆਂ (Bags)"]
ASSET_TYPES = ["ਬਿਲਡਿੰਗ (Building)", "ਫਰਨੀਚਰ (Furniture)", "ਇਲੈਕਟ੍ਰੋਨਿਕਸ (Electronics/IT)", "ਵਾਹਨ (Vehicles)", "ਮਸ਼ੀਨਰੀ (Machinery)", "ਹੋਰ (Other)"]

# --- CREDENTIALS ---
USERS = {
    "admin": {"password": "Japnik@3315", "role": "admin"},
    "staff": {"password": "12345", "role": "staff"},
    "management": {"password": "view@123", "role": "management"},
    "emp1": {"password": "emp1", "role": "employee"},
    "emp2": {"password": "emp2", "role": "employee"},
    "emp3": {"password": "emp3", "role": "employee"},
    "emp4": {"password": "emp4", "role": "employee"},
    "emp5": {"password": "emp5", "role": "employee"}
}
SUPABASE_URL = "https://jbvtvrhzzucggqhwjzuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

# --- CUSTOM CSS ---
def apply_custom_css():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stAppDeployButton {display:none !important;}
            [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
            div[data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 600 !important; }
            h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
            h3 { font-size: 20px !important; font-weight: 600 !important; }
            [data-testid="stMetricLabel"] p { font-size: 16px !important; font-weight: bold !important; }
            [data-testid="stMetricValue"] { font-size: 26px !important; }
            .pro-header-flex { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #F8F1D1 0%, #ffffff 100%); padding: 15px 20px; border-radius: 12px; border: 2px solid #4A1B15; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            .pro-logo { width: 85px; height: auto; margin-right: 20px; }
            .pro-title { font-size: 28px; font-weight: bold; color: #4A1B15 !important; margin: 0; letter-spacing: 0.5px; }
            .pro-tagline { font-size: 17px; font-weight: bold; color: #D92B2B !important; margin: 4px 0; }
            .pro-sub { font-size: 13px; font-weight: bold; color: #0F4C81 !important; margin: 0; }
            div.stButton > button { font-size: 18px !important; font-weight: bold !important; padding: 16px 10px !important; margin-bottom: 10px !important; border-radius: 10px !important; width: 100% !important; }
            div.row-widget.stRadio > div { background-color: #F8F1D1; padding: 8px 15px; border-radius: 10px; border: 1px solid #4A1B15; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
            div.row-widget.stRadio p { color: #4A1B15 !important; font-weight: bold !important; }
            .bs-box { border: 2px solid var(--text-color); border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: transparent; }
            .bs-header { text-align: center; color: var(--text-color); font-size: 22px; font-weight: bold; border-bottom: 2px solid var(--text-color); padding-bottom: 10px; margin-bottom: 15px; }
            .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; color: var(--text-color); }
            .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #E53935; border-top: 1px solid var(--text-color); padding-top: 8px; margin-top: 10px; }
            .whatsapp-btn { display: inline-block; padding: 10px 20px; background-color: #25D366; color: white !important; text-align: center; text-decoration: none; font-size: 17px; border-radius: 8px; font-weight: bold; margin-top: 6px; border: 1.5px solid #128C7E; box-shadow: 0 2px 5px rgba(0,0,0,0.15); }
        </style>
    """, unsafe_allow_html=True)
