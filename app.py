import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import urllib.parse
import io
import base64
import os
import time
import json
from PIL import Image
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- CATEGORIES & ACCOUNTS ---
BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = [
    "--- ਕੀਰਤਨ ਸਮਾਗਮ (Samagams) ---",
    "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", 
    "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)", "ਲੰਗਰ (Langar)",
    "--- ਤੇਰਾ ਆਸਰਾ (Tera Aasra) ---",
    "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", 
    "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", 
    "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)", "ਹੋਰ ਖਰਚੇ (Others)"
]
STOCK_UNITS = ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)", "ਬੈਗ/ਬੋਰੀਆਂ (Bags)"]
ASSET_TYPES = ["ਬਿਲਡਿੰਗ (Building)", "ਫਰਨੀਚਰ (Furniture)", "ਇਲੈਕਟ੍ਰੋਨਿਕਸ (Electronics/IT)", "ਵਾਹਨ (Vehicles)", "ਮਸ਼ੀਨਰੀ (Machinery)", "ਹੋਰ (Other)"]

# ==========================================
# CREDENTIALS (DIRECTLY IN CODE)
# ==========================================
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

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ (Sabha Manager Pro)", page_icon="logo.png", layout="wide")

# ==========================================
# CUSTOM CSS (UI DESIGN & DARK MODE FIXES)
# ==========================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display:none !important;}

        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
        div[data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 600 !important; }
        h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
        h3 { font-size: 20px !important; font-weight: 600 !important; }
        [data-testid="stMetricLabel"] p { font-size: 16px !important; font-weight: bold !important; }
        [data-testid="stMetricValue"] { font-size: 26px !important; }
        
        .pro-header-flex {
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #F8F1D1 0%, #ffffff 100%);
            padding: 15px 20px;
            border-radius: 12px;
            border: 2px solid #4A1B15;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .pro-logo { width: 85px; height: auto; margin-right: 20px; }
        .pro-text-box { text-align: center; }
        .pro-title { font-size: 28px; font-weight: bold; color: #4A1B15 !important; margin: 0; letter-spacing: 0.5px; }
        .pro-tagline { font-size: 17px; font-weight: bold; color: #D92B2B !important; margin: 4px 0; }
        .pro-sub { font-size: 13px; font-weight: bold; color: #0F4C81 !important; margin: 0; }

        div.stButton > button {
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 16px 10px !important;
            margin-bottom: 10px !important;
            border-radius: 10px !important;
            width: 100% !important;
        }
        
        div.row-widget.stRadio > div {
            background-color: #F8F1D1;
            padding: 8px 15px;
            border-radius: 10px;
            border: 1px solid #4A1B15;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        div.row-widget.stRadio p { color: #4A1B15 !important; font-weight: bold !important; }
        
        .bs-box { border: 2px solid var(--text-color); border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: transparent; }
        .bs-header { text-align: center; color: var(--text-color); font-size: 22px; font-weight: bold; border-bottom: 2px solid var(--text-color); padding-bottom: 10px; margin-bottom: 15px; }
        .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; color: var(--text-color); }
        .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #E53935; border-top: 1px solid var(--text-color); padding-top: 8px; margin-top: 10px; }
        
        .whatsapp-btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #25D366;
            color: white !important;
            text-align: center;
            text-decoration: none;
            font-size: 17px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 6px;
            border: 1.5px solid #128C7E;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        .whatsapp-btn:hover { background-color: #128C7E; }
    </style>
""", unsafe_allow_html=True)

def compress_image(uploaded_file, max_size=(150, 150)):
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file)
            img.thumbnail(max_size)
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_str
        except Exception as e:
            st.error(f"Image processing error: {e}")
            return ""
    return ""

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return ""

@st.cache_resource
def init_connection(): return create_client(SUPABASE_URL, SUPABASE_KEY)

try: supabase: Client = init_connection()
except Exception as e: st.error("Supabase Error.")

def generate_html_report(title, content_html):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 10px;">' if logo_base64 else ''
    html_content = f"""
    <!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; color: #333; background-color: #fff; text-align: center; }}
        .header {{ margin-bottom: 20px; border-bottom: 2px solid #4A1B15; padding-bottom: 15px; text-align: center; }}
        .title {{ font-size: 24px; font-weight: bold; color: #4A1B15; margin-bottom: 2px; }}
        .tagline {{ font-size: 17px; font-weight: bold; color: #D92B2B; margin-bottom: 5px; }}
        .report-title {{ font-size: 18px; font-weight: bold; color: #0F4C81; margin-top: 10px; }}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; text-align: left; }}
        .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 8px; color: #000; }}
        .report-table th {{ background-color: #F8F1D1; color: #4A1B15; font-weight: bold; }}
        .bs-box {{ width: 48%; display: inline-block; vertical-align: top; border: 1px solid #333; padding: 10px; box-sizing: border-box; text-align: left; }}
        @media print {{ body {{ padding: 0; }} }}
    </style></head>
    <body>
        <div class="header">
            {img_html}
            <div class="title">{NGO_NAME_PB}</div>
            <div class="tagline">{NGO_TAGLINE_PB}</div>
            <div style="font-size: 13px;">{NGO_ADDRESS_PB}</div>
            <div class="report-title">{title}</div>
        </div>
        <div style="text-align: left;">{content_html}</div>
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Report_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_report_landscape(title, content_html):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 10px;">' if logo_base64 else ''
    html_content = f"""
    <!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>{title}</title>
    <style>
        @page {{ size: landscape; margin: 10mm; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px; color: #333; background-color: #fff; text-align: center; }}
        .header {{ margin-bottom: 15px; border-bottom: 2px solid #4A1B15; padding-bottom: 10px; text-align: center; }}
        .title {{ font-size: 22px; font-weight: bold; color: #4A1B15; margin-bottom: 2px; }}
        .tagline {{ font-size: 15px; font-weight: bold; color: #D92B2B; margin-bottom: 5px; }}
        .report-title {{ font-size: 16px; font-weight: bold; color: #0F4C81; margin-top: 8px; }}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; text-align: center; vertical-align: middle; }}
        .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 5px; color: #000; vertical-align: middle; text-align: center; }}
        .report-table th {{ background-color: #F8F1D1; color: #4A1B15; font-weight: bold; }}
        .table-img {{ width: 60px; height: 60px; object-fit: cover; border-radius: 5px; border: 1px solid #ccc; }}
        @media print {{ body {{ padding: 0; }} }}
    </style></head>
    <body>
        <div class="header">
            {img_html}
            <div class="title">{NGO_NAME_PB}</div>
            <div class="tagline">{NGO_TAGLINE_PB}</div>
            <div style="font-size: 12px;">{NGO_ADDRESS_PB}</div>
            <div class="report-title">{title}</div>
        </div>
        <div style="overflow-x: auto;">{content_html}</div>
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Report_Landscape_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, don_type, item_details, bank_acc, on_account_of, collector=""):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Logo">' if logo_base64 else ''
    amount_text = f"Rs. {amount}/-" if don_type == "ਪੈਸੇ (Monetary)" else f"ਕੀਮਤ: Rs. {amount}/-" if amount > 0 else f"{item_details}"
    amount_in_words = f"Rupees {amount} Only" if don_type == "ਪੈਸੇ (Monetary)" else f"{item_details} (In-Kind Donation)"
    display_phone = phone if phone else "________________"
    collector_info = f"ਕਲੈਕਟਰ: {collector}" if collector else ""
    
    html_content = f"""
    <!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #fff; padding: 20px; }}
            .receipt-box {{ max-width: 850px; margin: auto; padding: 20px 30px; background-color: #F8F1D1; border-top: 25px solid #4A1B15; border-bottom: 25px solid #4A1B15; color: #333; position: relative; box-sizing: border-box; }}
            .header-flex {{ display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 5px; }}
            .logo-img {{ position: absolute; left: 0; top: 0; width: 100px; height: auto; }}
            .header-text {{ text-align: center; width: 100%; padding-left: 110px; box-sizing: border-box; }}
            .title-pa {{ font-size: 26px; font-weight: bold; color: #4A1B15; margin: 0; letter-spacing: 0.5px; }}
            .sub-title-pa {{ font-size: 16px; color: #D92B2B; font-weight: bold; margin: 4px 0; text-align: center; width: 100%; display: block; }}
            .sub-title-en {{ font-size: 13px; font-weight: bold; color: #0F4C81; margin: 3px 0; }}
            .phones {{ font-size: 13px; font-weight: bold; color: #333; margin: 2px 0; }}
            .reg-row {{ display: flex; justify-content: space-between; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; padding: 5px 0; font-size: 13px; font-weight: bold; margin-bottom: 12px; margin-top: 10px; }}
            .main-content {{ font-size: 15px; line-height: 2.0; font-weight: bold; color: #222; }}
            .row-inline {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .field-value {{ font-family: 'Courier New', Courier, monospace; font-size: 16px; color: #0F4C81; border-bottom: 1px solid #666; padding: 0 10px; font-weight: bold; }}
            .receipt-no {{ color: #D92B2B; font-size: 20px; font-weight: bold; font-family: monospace; }}
            .footer-flex {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15px; }}
            .bank-details-box {{ font-size: 11px; font-weight: bold; line-height: 1.4; background-color: rgba(255,255,255,0.4); padding: 5px 10px; border-radius: 5px; width: 65%; }}
            .bank-details-box span {{ color: #D92B2B; }}
            .amount-box {{ font-size: 18px; font-weight: bold; color: #0F4C81; border: 2px solid #333; padding: 5px 20px; border-radius: 15px; background-color: rgba(255,255,255,0.5); display: inline-block; }}
            .sign-box {{ text-align: right; margin-top: 15px; font-size: 14px; padding-bottom: 10px; }}
            .bottom-note {{ position: absolute; bottom: 0; left: 0; right: 0; background-color: #4A1B15; color: white; text-align: center; font-size: 11px; padding: 4px 0; font-weight: bold; }}
            @media print {{ body {{ padding: 0; }} .receipt-box {{ border: 2px solid #4A1B15; box-shadow: none; }} }}
        </style></head>
    <body>
        <div class="receipt-box">
            <div class="header-flex">
                {img_html}
                <div class="header-text">
                    <p class="title-pa">{NGO_NAME_PB}</p>
                    <div style="text-align: center; width: 100%;">
                        <span class="sub-title-pa">{NGO_TAGLINE_PB}</span>
                    </div>
                    <p class="sub-title-en">ਸੇਵਾ ਵਿਸਥਾਰ: ਰਾਧਾ ਕ੍ਰਿਸ਼ਨ ਕਲੋਨੀ (ਮੂਲੇ ਚੱਕ), ਨੇੜੇ ਭਗਤਾਂ ਵਾਲਾ ਦਾਣਾ ਮੰਡੀ, ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ</p>
                    <p class="sub-title-en">Regd. Office: C. B. Tower, Opp. Side Alpha One Mall, G. T. Road, Sri Amritsar Sahib - 143001</p>
                    <p class="phones">(M) 099150-07697, 78953-33290, 98157-55883</p>
                </div>
            </div>
            <div class="reg-row"><div>Regd. No.: ASR/26/2024-25 &nbsp;|&nbsp; PAN NO. ABKTS7853G</div><div>{collector_info} &nbsp;|&nbsp; On Account of: <span class="field-value" style="font-size:14px;">{on_account_of}</span></div></div>
            <div class="main-content">
                <div class="row-inline"><div>ਰਸੀਦ ਨੰ. <span class="field-value receipt-no" style="padding-left: 15px;">{receipt_no:04d}</span></div><div>ਮਿਤੀ <span class="field-value">{date_str[:10]}</span></div></div>
                <div style="margin-top: 10px;">ਸਤਿਕਾਰ ਯੋਗ <span class="field-value" style="display:inline-block; width: 45%;">{name}</span> ਜੀ ਪਾਸੋਂ, ਮੋ.ਨੰ: <span class="field-value">{display_phone}</span></div>
                <div style="margin-top: 10px;">ਰਕਮ ਅੱਖਰੀ <span class="field-value" style="display:inline-block; width: 65%;">{amount_in_words}</span> ਧੰਨਵਾਦ ਸਹਿਤ ਵਸੂਲ ਪਾਏ।</div>
                <div style="margin-top: 10px;">ਕੈਸ਼/ਚੈਕ/ਗੂਗਲ ਪੇ/ਯੂ ਟੀ ਆਰ ਨੰ. <span class="field-value" style="display:inline-block; width: 25%;">{payment_mode}</span> ਬੈਂਕ <span class="field-value" style="display:inline-block; width: 15%;">{bank_acc}</span> ਮਿਤੀ <span class="field-value">{date_str[:10]}</span></div>
            </div>
            <div class="footer-flex">
                <div class="bank-details-box"><div style="background-color: #333; color: white; padding: 2px 10px; display: inline-block; border-radius: 5px 5px 0 0; margin-bottom: 2px;">BANK A/C DETAILS :</div><br><strong>PUNJAB & SIND BANK</strong> A/c No. <span>06181000012550</span> IFSC : <span>PSIB0000618</span><br><span style="color:#333; font-weight:normal;">Sultanwind Road, Amritsar</span><br><strong>KOTAK MAHINDRA BANK</strong> A/c No. <span>4350934312</span> IFSC : <span>KKBK0004001</span><br><span style="color:#333; font-weight:normal;">East Mohan Nagar, Amritsar</span></div>
                <div style="text-align: center;"><div class="amount-box">{amount_text}</div><div class="sign-box">ਪ੍ਰਾਪਤ ਕਰਤਾ</div></div>
            </div>
            <div class="bottom-note">Note : If you transfer any amount direct to the account please intimate on Mob : 9915007697</div>
        </div>
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if 'current_tab' not in st.session_state: st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
if 'entry_mode' not in st.session_state: st.session_state.entry_mode = "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"
if 'acc_mode' not in st.session_state: st.session_state.acc_mode = "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"
if 'other_mode' not in st.session_state: st.session_state.other_mode = "📦 ਸਟਾਕ (Inventory)"
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)"

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_login_path = "logo.png"
        if os.path.exists(logo_login_path):
            st.image(logo_login_path, width=100)
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: var(--text-color); margin: 0; font-size: 26px;">{NGO_NAME_PB}</h2>
                <p style="color: #E53935; font-weight: bold; font-size: 16px; margin: 5px 0;">{NGO_TAGLINE_PB}</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = USERS[username_input]["role"]
                    st.session_state.username = username_input
                    
                    if st.session_state.role == "employee":
                        st.session_state.current_tab = "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)"
                    else:
                        st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
                    st.rerun()
                else: st.error("ਗਲਤ ਪਾਸਵਰਡ! (Incorrect Password!)")
    st.stop()

is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"
is_staff = st.session_state.role == "staff"
is_employee = st.session_state.role == "employee"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    if is_admin: role_display = "ਐਡਮਿਨ ਮੋਡ (Admin)"
    elif is_mgmt: role_display = "ਮੈਨੇਜਮੈਂਟ (View Only)"
    elif is_staff: role_display = "ਕਰਮਚਾਰੀ ਮੋਡ (Staff)"
    elif is_employee: role_display = "ਸਟਾਫ ਹਾਜ਼ਰੀ ਮੋਡ (Employee)"
    
    st.success(f"✅ {role_display}")
    
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()
    
    st.markdown("---")
    st.subheader("ਮੁੱਖ ਮੀਨੂ (Main Menu)")
    
    if is_employee:
        menu_options = ["⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)"]
    else:
        menu_options = [
            "🏠 ਹੋਮ ਪੇਜ (Home)",
            "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", 
            "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)",
            "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)",
            "🎓 ਵਿਦਿਆਰਥੀ (Students)",
            "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)",
            "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)"
        ]
        if is_admin or is_staff:
            menu_options.append("⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)")
        
    try:
        current_idx = menu_options.index(st.session_state.current_tab)
    except ValueError:
        current_idx = 0

    selected_tab = st.radio("ਚੁਣੋ (Select)", menu_options, index=current_idx, label_visibility="collapsed")
    st.session_state.current_tab = selected_tab

# --- PROFESSIONAL HEADER ON ALL PAGES ---
logo_path = "logo.png"
logo_base64 = get_base64_image(logo_path)
logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" class="pro-logo">' if logo_base64 else ''

st.markdown(f"""
    <div class="pro-header-flex">
        {logo_img_tag}
        <div class="pro-text-box">
            <div class="pro-title">{NGO_NAME_PB}</div>
            <div class="pro-tagline">{NGO_TAGLINE_PB}</div>
            <div class="pro-sub">{NGO_ADDRESS_PB}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- QUICK HOME NAVIGATION BUTTON FOR MOBILE USERS ---
if st.session_state.current_tab != "🏠 ਹੋਮ ਪੇਜ (Home)" and not is_employee:
    if st.button("🏠 ਹੋਮ ਪੇਜ 'ਤੇ ਜਾਓ (Back to Home Dashboard)", type="secondary"):
        st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
        st.rerun()
    st.markdown("---")

# ==========================================
# 0. EMPLOYEE ATTENDANCE (DEDICATED STRICT VIEW)
# ==========================================
if st.session_state.current_tab == "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)":
    st.header("⏱️ ਰੋਜ਼ਾਨਾ ਹਾਜ਼ਰੀ (Daily Attendance)")
    
    my_username = st.session_state.get('username', '')
    
    try: my_profile = supabase.table("staff_profiles").select("*").eq("login_id", my_username).execute().data
    except Exception: my_profile = []
    
    if not my_profile:
        st.error("⚠️ ਤੁਹਾਡੀ ਲਾਗਇਨ ID ਕਿਸੇ ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ ਨਾਲ ਨਹੀਂ ਜੁੜੀ ਹੋਈ।")
        st.info("ਕਿਰਪਾ ਕਰਕੇ ਐਡਮਿਨ ਨੂੰ ਕਹੋ ਕਿ ਤੁਹਾਡਾ 'ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ' ਬਣਾਉਂਦੇ ਸਮੇਂ ਤੁਹਾਡੀ **Login ID** ਸੈੱਟ ਕਰਨ।")
    else:
        clean_name = my_profile[0].get('name', 'Unknown')
        
        st.success(f"ਜੀ ਆਇਆਂ ਨੂੰ (Welcome), **{clean_name}** ਜੀ!")
        
        att_e_tab1, att_e_tab2 = st.tabs(["⏱️ ਅੱਜ ਦੀ ਹਾਜ਼ਰੀ (Punch In/Out)", "📝 ਛੁੱਟੀ/ਪੁਰਾਣੀ ਹਾਜ਼ਰੀ ਬੇਨਤੀ (Leave Request)"])
        
        with att_e_tab1:
            today_str = str(date.today())
            current_time = datetime.now().strftime("%I:%M %p")
            
            try: today_record = supabase.table("attendance").select("*").eq("staff_name", clean_name).eq("date", today_str).execute().data
            except Exception: today_record = []
            
            if not today_record:
                st.info(f"ਤੁਹਾਡੀ ਅੱਜ ਦੀ ਹਾਜ਼ਰੀ ਹਾਲੇ ਨਹੀਂ ਲੱਗੀ। (Time: {current_time})")
                if st.button("🟢 Punch IN (ਆਉਣ ਦਾ ਸਮਾਂ)", type="primary", use_container_width=True):
                    supabase.table("attendance").insert({
                        "staff_name": clean_name, "date": today_str,
                        "in_time": current_time, "out_time": "", "status": "Present"
                    }).execute()
                    st.success(f"✅ ਹਾਜ਼ਰੀ ਲੱਗ ਗਈ ਹੈ!")
                    time.sleep(1.5); st.rerun()
            else:
                rec = today_record[0]
                st.success(f"✅ Punch IN Time: {rec.get('in_time', '')}")
                if not rec.get('out_time') or rec.get('out_time') == "":
                    st.warning(f"ਤੁਹਾਡਾ ਜਾਣ ਦਾ ਸਮਾਂ ਹਾਲੇ ਨਹੀਂ ਲੱਗਿਆ। (Time: {current_time})")
                    if st.button("🔴 Punch OUT (ਜਾਣ ਦਾ ਸਮਾਂ)", type="primary", use_container_width=True):
                        supabase.table("attendance").update({"out_time": current_time}).eq("id", rec['id']).execute()
                        st.success(f"✅ ਜਾਣ ਦਾ ਸਮਾਂ ਲੱਗ ਗਿਆ ਹੈ!")
                        time.sleep(1.5); st.rerun()
                else:
                    st.error(f"🔴 Punch OUT Time: {rec.get('out_time', '')}")
                    st.info("🌟 ਅੱਜ ਦੀ ਤੁਹਾਡੀ ਡਿਊਟੀ ਪੂਰੀ ਹੋ ਗਈ ਹੈ।")

            st.markdown("---")
            st.write(f"#### 📅 ਤੁਹਾਡੀ ਪਿਛਲੀ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ (Your Past Attendance)")
            try:
                my_att = supabase.table("attendance").select("*").eq("staff_name", clean_name).order("date", desc=True).limit(10).execute().data or []
                if my_att:
                    df_my_att = pd.DataFrame(my_att)
                    display_my_att = [c for c in ['date', 'in_time', 'out_time', 'status'] if c in df_my_att.columns]
                    st.dataframe(df_my_att[display_my_att], hide_index=True, use_container_width=True)
                else:
                    st.info("ਕੋਈ ਪੁਰਾਣੀ ਹਾਜ਼ਰੀ ਨਹੀਂ ਮਿਲੀ।")
            except Exception: pass

        with att_e_tab2:
            st.write("### 📝 ਛੁੱਟੀ ਜਾਂ ਪੁਰਾਣੀ ਹਾਜ਼ਰੀ ਦੀ ਬੇਨਤੀ (Leave Request)")
            with st.form("emp_manual_att_form", clear_on_submit=True):
                st.write(f"**ਸਟਾਫ ਦਾ ਨਾਮ:** {clean_name}")
                m_date = st.date_input("ਕਿਸ ਦਿਨ ਦੀ ਬੇਨਤੀ ਹੈ? (Date)")
                m_status = st.selectbox("ਕੀ ਲਗਾਉਣਾ ਹੈ? (Status)", ["Present (ਹਾਜ਼ਰ)", "Absent (ਛੁੱਟੀ/ਗੈਰ-ਹਾਜ਼ਰ)", "Half Day (ਅੱਧਾ ਦਿਨ)"])
                m_reason = st.text_input("ਕਾਰਨ (Reason)")
                
                if st.form_submit_button("ਐਡਮਿਨ ਨੂੰ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ", type="primary"):
                    supabase.table("attendance_requests").insert({
                        "staff_name": clean_name, "date": str(m_date),
                        "requested_status": m_status, "reason": m_reason,
                        "status": "Pending"
                    }).execute()
                    st.success("✅ ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਕੋਲ ਮਨਜ਼ੂਰੀ ਲਈ ਚਲੀ ਗਈ ਹੈ!")

# ==========================================
# 0. HOME PAGE DASHBOARD (SHORTCUT BUTTONS)
# ==========================================
elif st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
    st.markdown("<p style='text-align: center; font-size: 20px; font-weight: bold; color: var(--text-color); margin-bottom: 25px;'>ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਦਿੱਤੇ ਸੈਕਸ਼ਨਾਂ ਵਿੱਚੋਂ ਕੋਈ ਇੱਕ ਚੁਣੋ ਜੀ:</p>", unsafe_allow_html=True)

    st.markdown("### 📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦਾਂ (Vouchers & Receipts)")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💰 ਨਵਾਂ ਦਾਨ / ਰਸੀਦ (Receipt)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)"
        st.session_state.entry_mode = "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"
        st.rerun()
    if c2.button("📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)"
        st.session_state.entry_mode = "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)"
        st.rerun()
    if c3.button("📉 ਖਰਚਾ (Payment)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)"
        st.session_state.entry_mode = "📉 ਖਰਚਾ (Payment Debit)"
        st.rerun()
    if c4.button("🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / WhatsApp", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)"
        st.session_state.entry_mode = "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint / Resend WhatsApp)"
        st.rerun()

    st.markdown("### 🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਆਡਿਟ (Accounts & Reports)")
    c5, c6, c7, c8, c8a = st.columns(5)
    if c5.button("⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"
        st.rerun()
    if c6.button("📖 ਮੁੱਖ ਲੈਜ਼ਰ (Daybook)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)"
        st.rerun()
    if c7.button("🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)"
        st.rerun()
    if c8.button("📁 ਪਾਰਟੀਆਂ (Parties)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)"
        st.rerun()
    if c8a.button("📊 CA ਐਕਸਪੋਰਟ", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"
        st.rerun()

    st.markdown("### 📦 ਸਟਾਕ, ਵਿਦਿਆਰਥੀ, ਵਿਧਵਾ ਰਾਸ਼ਨ ਅਤੇ ਪ੍ਰਬੰਧ (Management)")
    c9, c10, c11, c12 = st.columns(4)
    if c9.button("📦 ਸਟਾਕ ਭੰਡਾਰ (Stock)", use_container_width=True):
        st.session_state.current_tab = "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)"
        st.session_state.other_mode = "📦 ਸਟਾਕ (Inventory)"
        st.rerun()
    if c10.button("🎓 ਵਿਦਿਆਰਥੀ (Students)", use_container_width=True):
        st.session_state.current_tab = "🎓 ਵਿਦਿਆਰਥੀ (Students)"
        st.rerun()
    if c11.button("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows)", use_container_width=True):
        st.session_state.current_tab = "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)"
        st.rerun()
    if c12.button("🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff)", use_container_width=True):
        st.session_state.current_tab = "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)"
        st.rerun()
    
    if is_admin:
        if st.button("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ", use_container_width=True):
            st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"
            st.session_state.admin_mode = "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)"
            st.rerun()
    elif is_staff:
        if st.button("🗑️ ਡਿਲੀਟ ਬੇਨਤੀ", use_container_width=True):
            st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"
            st.session_state.admin_mode = "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)"
            st.rerun()

# ==========================================
# 1. SINGLE WINDOW: VOUCHER & RECEIPT ENTRY
# ==========================================
elif st.session_state.current_tab == "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)":
    st.header("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦ ਪ੍ਰਬੰਧਨ (Single Window Entry)")
    
    modes = [
        "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)", 
        "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)", 
        "📉 ਖਰਚਾ (Payment Debit)", 
        "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)", 
        "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)", 
        "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint / Resend WhatsApp)"
    ]
    if st.session_state.entry_mode not in modes: st.session_state.entry_mode = modes[0]
    selected_mode = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ ਚੁਣੋ (Select Action):", modes, index=modes.index(st.session_state.entry_mode), horizontal=True)
    st.session_state.entry_mode = selected_mode
    st.markdown("---")

    if selected_mode == "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)":
        if not is_mgmt:
            with st.form("donation_form", clear_on_submit=True):
                st.write("### 💰 ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ")
                donor_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
                donor_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number - WhatsApp ਲਈ ਜ਼ਰੂਰੀ)")
                on_account_of = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of - e.g. Monthly Donation)")
                rec_no_input = st.number_input("ਰਸੀਦ ਨੰਬਰ (Printed Receipt Serial No.)", min_value=1, step=1)
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
                    pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Payment Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Cheque", "NEFT/RTGS"])
                with col_m2:
                    bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ? (Select Bank)", BANK_ACCOUNTS)
                    receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ (Receipt Date)", value=date.today())
                    
                add_to_mirror = st.checkbox("✅ ਇਸ ਐਂਟਰੀ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਜੋੜੋ (Add to Bank Ledger)", value=False)
                submitted = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਤਿਆਰ ਕਰੋ (Save & Generate Receipt)", type="primary")
                
            if submitted and donor_name:
                books = supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book = next((b for b in books if int(b['start_no']) <= int(rec_no_input) <= int(b['end_no'])), None)
                existing_rec = supabase.table("donations").select("*").eq("id", int(rec_no_input)).execute().data
                
                if not matched_book:
                    st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ {rec_no_input} ਕਿਸੇ ਵੀ ਜਾਰੀ ਕੀਤੀ ਗਈ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif existing_rec:
                    st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ {rec_no_input} ਪਹਿਲਾਂ ਹੀ ਵਰਤੀ ਜਾ ਚੁੱਕੀ ਹੈ!")
                else:
                    collector = matched_book['collector_name']
                    formatted_date = receipt_date.strftime("%Y-%m-%d")
                    supabase.table("donations").insert({
                        "id": int(rec_no_input), "name": donor_name, "phone": donor_phone, "amount": amount, 
                        "date": formatted_date, "payment_mode": pay_mode, "donation_type": "ਪੈਸੇ (Monetary)", 
                        "item_details": "", "bank_account": bank_acc, "on_account_of": on_account_of, 
                        "add_to_mirror": add_to_mirror, "collector_name": collector
                    }).execute()
                    
                    st.success(f"✅ ਰਸੀਦ #{rec_no_input} ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਈ! (ਕਲੈਕਟਰ: {collector})")
                    html_file = generate_html_receipt(int(rec_no_input), donor_name, donor_phone, amount, formatted_date, pay_mode, "ਪੈਸੇ (Monetary)", "", bank_acc, on_account_of, collector)
                    
                    col_d1, col_d2 = st.columns([1, 2])
                    with col_d1:
                        with open(html_file, "r", encoding="utf-8") as file:
                            st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ/ਪ੍ਰਿੰਟ ਕਰੋ (Print)", data=file.read(), file_name=html_file, mime="text/html", type="primary")
                    with col_d2:
                        if donor_phone:
                            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{amount}/- ਦਾ ਦਾਨ (ਰਸੀਦ ਨੰ: {rec_no_input}, ਕਲੈਕਟਰ: {collector}) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                            url = f"https://wa.me/{donor_phone}?text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.write("#### 🕒 ਤੁਹਾਡੀਆਂ ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ (Recent Donations)")
            try:
                recents = supabase.table("donations").select("*").eq("donation_type", "ਪੈਸੇ (Monetary)").order("id", desc=True).limit(10).execute().data
                if recents: 
                    df_rec = pd.DataFrame(recents)[['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name']]
                    df_rec.insert(0, "Select", False)
                    
                    st.write("**🖨️ ਰਸੀਦ ਪ੍ਰਿੰਟ ਜਾਂ WhatsApp ਕਰਨ ਲਈ ਟਿੱਕ ਲਗਾਓ (Select to Print/WhatsApp):**")
                    
                    edited_df = st.data_editor(
                        df_rec,
                        column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)},
                        disabled=['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name'],
                        hide_index=True,
                        use_container_width=True,
                        key="editor_recent_monetary"
                    )
                    
                    selected_ids = edited_df[edited_df["Select"] == True]['id'].tolist()
                    
                    if selected_ids:
                        st.write("##### 🖨️ ਚੁਣੀਆਂ ਗਈਆਂ ਰਸੀਦਾਂ (Selected Receipts)")
                        for sid in selected_ids:
                            row_data = next(r for r in recents if r['id'] == sid)
                            h_file = generate_html_receipt(
                                row_data['id'], row_data.get('name',''), row_data.get('phone',''), 
                                float(row_data.get('amount',0) or 0), row_data.get('date',''), 
                                row_data.get('payment_mode','N/A'), "ਪੈਸੇ (Monetary)", "", 
                                row_data.get('bank_account','N/A'), row_data.get('on_account_of',''), 
                                row_data.get('collector_name', '')
                            )
                            
                            c1, c2, c3 = st.columns([2, 1, 1])
                            with c1:
                                st.markdown(f"**ਰਸੀਦ #{row_data['id']}** - {row_data.get('name','')} (₹{row_data.get('amount',0)})")
                            with c2:
                                with open(h_file, "r", encoding="utf-8") as f:
                                    st.download_button("🖨️ Print", data=f.read(), file_name=h_file, mime="text/html", key=f"dl_mon_{sid}")
                            with c3:
                                phone = str(row_data.get('phone', '')).strip()
                                if phone and phone.lower() not in ['nan', 'none', '']:
                                    msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {row_data.get('name','')} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{row_data.get('amount',0)}/- ਦਾ ਦਾਨ (ਰਸੀਦ ਨੰ: {row_data['id']}) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਧੰਨਵਾਦ ਜੀ।"
                                    url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                                    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn" style="padding: 5px 15px; font-size: 14px; margin-top: 0;">💬 WhatsApp</a>', unsafe_allow_html=True)
                                else:
                                    st.caption("ਨੰਬਰ ਨਹੀਂ ਹੈ")
                else: 
                    st.info("ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")
            except Exception as e: 
                pass

        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    elif selected_mode == "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)":
        if not is_mgmt:
            with st.form("inkind_form", clear_on_submit=True):
                st.write("### 📦 ਸਮਾਨ ਦਾ ਦਾਨ ਦਰਜ ਕਰੋ")
                donor_name_ik = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)", key="ik_name")
                donor_phone_ik = text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional Phone)", key="ik_phone")
                item_details_ik = st.text_input("ਰਸੀਦ 'ਤੇ ਛਾਪਣ ਲਈ ਸਮਾਨ ਦਾ ਵੇਰਵਾ (Receipt Item Details)", key="ik_item")
                rec_no_ik = st.number_input("ਰਸੀਦ ਨੰਬਰ (Printed Receipt No.)", min_value=1, step=1, key="ik_rec")
                
                col_k1, col_k2 = st.columns(2)
                with col_k1: amount_ik = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (Estimated Value ₹)", min_value=0.0, key="ik_amt")
                with col_k2: receipt_date_ik = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), key="ik_date")
                
                st.markdown("---")
                add_destination = st.radio("ਦਾਨ ਕੀਤੇ ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ? (Where to add this item?)", 
                                           ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)"], 
                                           horizontal=True)
                
                st.write("*(ਜੇਕਰ ਸਟਾਕ ਜਾਂ ਸੰਪਤੀ ਚੁਣਿਆ ਹੈ, ਤਾਂ ਹੇਠਾਂ ਵੇਰਵਾ ਭਰੋ)*")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1: s_item_ik = st.text_input("ਸਟਾਕ/ਸੰਪਤੀ ਦਾ ਨਾਮ", key="s_item_ik")
                with col_s2: s_qty_ik = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5, key="s_qty_ik")
                with col_s3: s_unit_ik = st.selectbox("ਇਕਾਈ (Unit)", STOCK_UNITS, key="s_unit_ik")
                with col_s4: s_type_ik = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ (Asset Type)", ASSET_TYPES, key="s_type_ik")
                
                submitted_ik = st.form_submit_button("ਸਮਾਨ ਦੀ ਰਸੀਦ ਬਣਾਓ (Generate In-Kind Receipt)", type="primary")
                
            if submitted_ik and donor_name_ik and item_details_ik:
                books_ik = supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book_ik = next((b for b in books_ik if int(b['start_no']) <= int(rec_no_ik) <= int(b['end_no'])), None)
                existing_rec_ik = supabase.table("donations").select("*").eq("id", int(rec_no_ik)).execute().data
                
                if not matched_book_ik:
                    st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ {rec_no_ik} ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif existing_rec_ik:
                    st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਵਰਤੀ ਜਾ ਚੁੱਕੀ ਹੈ!")
                else:
                    collector_ik = matched_book_ik['collector_name']
                    formatted_date_ik = receipt_date_ik.strftime("%Y-%m-%d")
                    
                    supabase.table("donations").insert({
                        "id": int(rec_no_ik), "name": donor_name_ik, "phone": donor_phone_ik, "amount": amount_ik, 
                        "date": formatted_date_ik, "payment_mode": "N/A", "donation_type": "ਸਮਾਨ (In-Kind / Ration)", 
                        "item_details": item_details_ik, "bank_account": "N/A", "on_account_of": "ਸਮਾਨ ਦਾਨ", 
                        "add_to_mirror": False, "collector_name": collector_ik
                    }).execute()
                    
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if add_destination == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)" and s_item_ik and s_qty_ik > 0:
                        res_stock = supabase.table("stock").select("*").eq("item_name", s_item_ik).execute()
                        if res_stock.data:
                            old_qty = float(res_stock.data[0].get('quantity', 0) or 0)
                            old_val = float(res_stock.data[0].get('estimated_value', 0) or 0)
                            new_qty = old_qty + s_qty_ik
                            new_val = old_val + amount_ik
                            supabase.table("stock").update({
                                "quantity": new_qty, 
                                "estimated_value": round(new_val, 2), 
                                "unit": s_unit_ik, 
                                "procurement_date": formatted_date_ik,
                                "last_updated": current_datetime
                            }).eq("item_name", s_item_ik).execute()
                        else:
                            supabase.table("stock").insert({
                                "item_name": s_item_ik, 
                                "quantity": s_qty_ik, 
                                "estimated_value": round(amount_ik, 2), 
                                "unit": s_unit_ik, 
                                "procurement_date": formatted_date_ik,
                                "last_updated": current_datetime
                            }).execute()
                        st.success(f"✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ '{s_item_ik}' ਸਟਾਕ ਵਿੱਚ ਜੁੜ ਗਿਆ!")
                        
                    elif add_destination == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)" and s_item_ik:
                        supabase.table("assets").insert({
                            "name": s_item_ik,
                            "asset_type": s_type_ik,
                            "value": amount_ik,
                            "quantity": s_qty_ik,
                            "date_added": formatted_date_ik
                        }).execute()
                        st.success(f"✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ '{s_item_ik}' ਪੱਕੀ ਸੰਪਤੀ (Fixed Assets) ਵਿੱਚ ਜੁੜ ਗਿਆ!")
                    else:
                        st.success(f"✅ ਰਸੀਦ #{rec_no_ik} ਤਿਆਰ ਹੈ। (ਕਲੈਕਟਰ: {collector_ik})")
                    
                    html_file_ik = generate_html_receipt(int(rec_no_ik), donor_name_ik, donor_phone_ik, amount_ik, formatted_date_ik, "N/A", "ਸਮਾਨ (In-Kind / Ration)", item_details_ik, "N/A", "ਸਮਾਨ ਦਾਨ", collector_ik)
                    
                    col_d1, col_d2 = st.columns([1, 2])
                    with col_d1:
                        with open(html_file_ik, "r", encoding="utf-8") as file:
                            st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print)", data=file.read(), file_name=html_file_ik, mime="text/html", key="ik_dl", type="primary")
                    with col_d2:
                        if donor_phone_ik:
                            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name_ik} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ਦਾਨ ਵਜੋਂ '{item_details_ik}' (ਰਸੀਦ ਨੰ: {rec_no_ik}) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                            url = f"https://wa.me/{donor_phone_ik}?text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ (Recent In-Kind)")
            try:
                recent_ik = supabase.table("donations").select("*").eq("donation_type", "ਸਮਾਨ (In-Kind / Ration)").order("id", desc=True).limit(10).execute().data
                if recent_ik: 
                    df_ik = pd.DataFrame(recent_ik)[['id', 'date', 'name', 'phone', 'item_details', 'amount']]
                    df_ik.insert(0, "Select", False)
                    
                    edited_ik = st.data_editor(
                        df_ik,
                        column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)},
                        disabled=['id', 'date', 'name', 'phone', 'item_details', 'amount'],
                        hide_index=True,
                        use_container_width=True,
                        key="editor_recent_inkind"
                    )
                    
                    selected_ik_ids = edited_ik[edited_ik["Select"] == True]['id'].tolist()
                    if selected_ik_ids:
                        for sid in selected_ik_ids:
                            sel_data_ik = next(r for r in recent_ik if r['id'] == sid)
                            h_file_recent_ik = generate_html_receipt(
                                sel_data_ik['id'], sel_data_ik.get('name',''), sel_data_ik.get('phone',''), 
                                float(sel_data_ik.get('amount',0) or 0), sel_data_ik.get('date',''), 
                                sel_data_ik.get('payment_mode','N/A'), "ਸਮਾਨ (In-Kind / Ration)", 
                                sel_data_ik.get('item_details',''), sel_data_ik.get('bank_account','N/A'), 
                                sel_data_ik.get('on_account_of',''), sel_data_ik.get('collector_name', '')
                            )
                            c1, c2, c3 = st.columns([2, 1, 1])
                            with c1: st.markdown(f"**ਰਸੀਦ #{sel_data_ik['id']}** - {sel_data_ik.get('name','')}")
                            with c2:
                                with open(h_file_recent_ik, "r", encoding="utf-8") as file:
                                    st.download_button("🖨️ Print", data=f.read(), file_name=h_file_recent_ik, mime="text/html", key=f"p_ik_{sel_data_ik['id']}")
            except Exception as e: pass
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif selected_mode == "📉 ਖਰਚਾ (Payment Debit)":
        if not is_mgmt:
            with st.form("expense_form", clear_on_submit=True):
                st.write("### 📉 ਖਰਚਾ ਜਾਂ ਪੇਮੈਂਟ ਦਰਜ ਕਰੋ")
                desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Expense Description)")
                cat = st.selectbox("ਕੈਟਾਗਰੀ (Category / Sub-head)", [c for c in EXPENSE_CATEGORIES if not c.startswith("---")])
                exp_amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
                bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ? (From which Bank?)", BANK_ACCOUNTS)
                exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ (Date)", value=date.today())
                add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਦਿਖਾਓ (Add to Bank Ledger)", value=False)
                
                st.markdown("---")
                add_destination_exp = st.radio("ਖਰੀਦੇ ਗਏ ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ? (Where to add this item?)", 
                                               ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)"], 
                                               horizontal=True)
                
                col_es1, col_es2, col_es3, col_es4 = st.columns(4)
                with col_es1: s_item_exp = st.text_input("ਸਟਾਕ/ਸੰਪਤੀ ਦਾ ਨਾਮ", key="s_item_exp")
                with col_es2: s_qty_exp = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5, key="s_qty_exp")
                with col_es3: s_unit_exp = st.selectbox("ਇਕਾਈ (Unit)", STOCK_UNITS, key="s_unit_exp")
                with col_es4: s_type_exp = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ (Asset Type)", ASSET_TYPES, key="s_type_exp")
                
                if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ (Save Expense)", type="primary") and desc:
                    supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"), "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp}).execute()
                    
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if add_destination_exp == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)" and s_item_exp and s_qty_exp > 0:
                        res_stock = supabase.table("stock").select("*").eq("item_name", s_item_exp).execute()
                        if res_stock.data:
                            old_qty = float(res_stock.data[0].get('quantity', 0) or 0)
                            old_val = float(res_stock.data[0].get('estimated_value', 0) or 0)
                            new_qty = old_qty + s_qty_exp
                            new_val = old_val + exp_amount
                            supabase.table("stock").update({
                                "quantity": new_qty, 
                                "estimated_value": round(new_val, 2), 
                                "unit": s_unit_exp, 
                                "procurement_date": exp_date.strftime("%Y-%m-%d"),
                                "last_updated": current_date
                            }).eq("item_name", s_item_exp).execute()
                        else:
                            supabase.table("stock").insert({
                                "item_name": s_item_exp, 
                                "quantity": s_qty_exp, 
                                "estimated_value": round(exp_amount, 2), 
                                "unit": s_unit_exp, 
                                "procurement_date": exp_date.strftime("%Y-%m-%d"),
                                "last_updated": current_date
                            }).execute()
                        st.success(f"✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ '{s_item_exp}' ਸਟਾਕ ਵਿੱਚ ਜੁੜ ਗਿਆ!")
                        
                    elif add_destination_exp == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)" and s_item_exp and s_qty_exp > 0:
                        supabase.table("assets").insert({
                            "name": s_item_exp,
                            "asset_type": s_type_exp,
                            "value": exp_amount,
                            "quantity": s_qty_exp,
                            "date_added": str(exp_date)
                        }).execute()
                        st.success(f"✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ '{s_item_exp}' ਪੱਕੀ ਸੰਪਤੀ (Fixed Asset) ਵਿੱਚ ਜੁੜ ਗਿਆ!")
                    else:
                        st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ! (Expense Saved!)")
            
            st.markdown("---")
            try:
                recents = supabase.table("expenses").select("*").order("id", desc=True).limit(5).execute().data
                if recents: st.dataframe(pd.DataFrame(recents)[['id', 'date', 'description', 'amount', 'category', 'bank_account']], hide_index=True, use_container_width=True)
            except: pass
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif selected_mode == "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)":
        if not is_mgmt:
            with st.form("party_form", clear_on_submit=True):
                st.write("### 📁 ਨਵੀਂ ਪਾਰਟੀ ਜਾਂ ਵੈਂਡਰ ਬਣਾਓ")
                p_name = st.text_input("ਪਾਰਟੀ / ਵੈਂਡਰ ਦਾ ਨਾਮ (Party Name)")
                p_type = st.selectbox("ਖਾਤੇ ਦੀ ਕਿਸਮ (Account Type)", ["Sundry Creditor (ਦੇਣਦਾਰ - ਪੈਸੇ ਦੇਣੇ ਹਨ)", "Sundry Debtor (ਪਾਉਣਦਾਰ - ਪੈਸੇ ਲੈਣੇ ਹਨ)"])
                p_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)")
                p_address = st.text_input("ਪਤਾ (Address)")
                p_amount = st.number_input("ਸ਼ੁਰੂਆਤੀ ਬੈਲੇਂਸ (Opening Balance ₹)", min_value=0.0)
                if st.form_submit_button("ਪਾਰਟੀ ਸੇਵ ਕਰੋ (Save Party)", type="primary") and p_name:
                    supabase.table("parties").insert({"name": p_name, "party_type": p_type, "phone": p_phone, "address": p_address, "opening_balance": p_amount, "created_at": str(date.today())}).execute()
                    st.success(f"✅ ਪਾਰਟੀ '{p_name}' ਸੇਵ ਹੋ ਗਈ!")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif selected_mode == "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)":
        if not is_mgmt:
            with st.form("cheque_form", clear_on_submit=True):
                st.write("### 💳 ਚੈੱਕ ਜਾਰੀ ਕਰਨ ਦੀ ਐਂਟਰੀ (Cheque Issued)")
                cq_no = st.text_input("ਚੈੱਕ ਨੰਬਰ (Cheque Number)")
                cq_bank = st.selectbox("ਬੈਂਕ ਖਾਤਾ (Bank Account)", BANK_ACCOUNTS)
                cq_party = st.text_input("ਕਿਸ ਨੂੰ ਦਿੱਤਾ/ਲਿਆ (Party Name)")
                cq_amt = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
                cq_date = st.date_input("ਚੈੱਕ ਦੀ ਮਿਤੀ (Cheque Date)", value=date.today())
                cq_status = st.selectbox("ਸਟੇਟਸ (Status)", ["Pending (ਕਲੀਅਰ ਹੋਣਾ ਬਾਕੀ)", "Cleared (ਕਲੀਅਰ ਹੋ ਗਿਆ)", "Cancelled (ਰੱਦ ਕੀਤਾ)"])
                if st.form_submit_button("ਚੈੱਕ ਸੇਵ ਕਰੋ (Save Cheque)", type="primary") and cq_no:
                    supabase.table("cheques").insert({"cheque_no": cq_no, "bank_name": cq_bank, "party_name": cq_party, "amount": cq_amt, "cheque_date": str(cq_date), "status": cq_status}).execute()
                    st.success("✅ ਚੈੱਕ ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif selected_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint / Resend WhatsApp)":
        st.write("### 🖨️ ਪੁਰਾਣੀ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ ਜਾਂ WhatsApp 'ਤੇ ਦੁਬਾਰਾ ਭੇਜੋ")
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ ਭਰੋ (Enter Receipt No.)", min_value=1, step=1)
            if st.button("🔍 ਰਸੀਦ ਲੱਭੋ (Find Receipt)", type="primary"):
                res = supabase.table("donations").select("*").eq("id", search_id).execute()
                if res.data:
                    rec = res.data[0]
                    html_file_rep = generate_html_receipt(search_id, rec.get('name',''), rec.get('phone',''), rec.get('amount',0), rec.get('date',''), rec.get('payment_mode','N/A'), rec.get('donation_type','ਪੈਸੇ (Monetary)'), rec.get('item_details',''), rec.get('bank_account','N/A'), rec.get('on_account_of',''), rec.get('collector_name', ''))
                    st.success(f"✅ ਰਸੀਦ #{search_id} ਮਿਲ ਗਈ ਹੈ ({rec.get('name', '')})!")
                    with open(html_file_rep, "r", encoding="utf-8") as file:
                        st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print)", data=file.read(), file_name=html_file_rep, mime="text/html", type="primary")
                else:
                    st.error("❌ ਇਸ ਨੰਬਰ ਦੀ ਕੋਈ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ।")
        with col_search2:
            search_donor = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਨਾਲ ਖੋਜ ਕਰੋ")
            if search_donor:
                df_don = pd.DataFrame(supabase.table("donations").select("*").execute().data or [])
                if not df_don.empty:
                    matches = df_don[df_don['name'].str.contains(search_donor, case=False, na=False)]
                    if not matches.empty:
                        df_disp = matches[['id', 'date', 'name', 'phone', 'amount']].copy()
                        st.dataframe(df_disp, hide_index=True)

# ==========================================
# 2. LEDGERS, BANK & CA REPORTS
# ==========================================
elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)":
    st.header("🏦 ਖਾਤੇ, ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    
    modes = [
        "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", 
        "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)",
        "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", 
        "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)", 
        "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"
    ]
    if st.session_state.acc_mode not in modes: st.session_state.acc_mode = modes[0]
    selected_mode = st.radio("ਖਾਤਾ ਚੁਣੋ:", modes, index=modes.index(st.session_state.acc_mode), horizontal=True)
    st.session_state.acc_mode = selected_mode
    st.markdown("---")

    don_data = supabase.table("donations").select("*").execute().data or []
    exp_data = supabase.table("expenses").select("*").execute().data or []
    try: ledg_data = supabase.table("bank_ledger").select("*").execute().data or []
    except Exception: ledg_data = []
    assets_data = supabase.table("assets").select("*").execute().data or []
    liab_data = supabase.table("liabilities").select("*").execute().data or []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledg_data)

    if selected_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        df_assets = pd.DataFrame(assets_data) if assets_data else pd.DataFrame(columns=['name', 'value'])
        df_liab = pd.DataFrame(liab_data) if liab_data else pd.DataFrame(columns=['name', 'value'])
        
        total_income = df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)']['amount'].sum() if not df_don.empty else 0.0
        total_income += df_ledg['credit'].sum() if not df_ledg.empty and 'credit' in df_ledg.columns else 0.0
        total_expense = df_exp['amount'].sum() if not df_exp.empty else 0.0
        total_expense += df_ledg['debit'].sum() if not df_ledg.empty and 'debit' in df_ledg.columns else 0.0
        surplus = total_income - total_expense
        
        # Calculate Asset Totals by Category
        if not df_assets.empty:
            if 'asset_type' not in df_assets.columns:
                df_assets['asset_type'] = 'ਹੋਰ (Other)'
            else:
                df_assets['asset_type'] = df_assets['asset_type'].fillna('ਹੋਰ (Other)')
            asset_totals = df_assets.groupby('asset_type')['value'].sum().to_dict()
            fixed_assets_val = df_assets['value'].sum()
        else:
            asset_totals = {}
            fixed_assets_val = 0.0

        st.subheader("📊 Income & Expenditure Account (ਆਮਦਨ ਅਤੇ ਖਰਚਾ)")
        inc_exp_html = f"""
        <table class="report-table">
            <tr><th>Expenditure (ਖਰਚੇ)</th><th>Amount (₹)</th><th>Income (ਆਮਦਨ)</th><th>Amount (₹)</th></tr>
            <tr><td>Total Expenses & Payments</td><td>{total_expense:,.2f}</td><td>Total Donations & Receipts</td><td>{total_income:,.2f}</td></tr>
            <tr style="font-weight:bold; color: #D92B2B;"><td>Surplus (ਬੱਚਤ)</td><td>{surplus if surplus > 0 else 0:,.2f}</td><td>Deficit (ਘਾਟਾ)</td><td>{abs(surplus) if surplus < 0 else 0:,.2f}</td></tr>
            <tr style="background-color: #F8F1D1; font-weight:bold;"><td>Total</td><td>{max(total_income, total_expense):,.2f}</td><td>Total</td><td>{max(total_income, total_expense):,.2f}</td></tr>
        </table>
        """
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        
        bank_balances = {"ਨਕਦ (Cash)": 0.0, "Kotak Bank Regular": 0.0, "Kotak Bank Corpus Fund": 0.0, "Punjab & Sind Bank": 0.0}
        for bank in BANK_ACCOUNTS:
            b_list = [bank, "Kotak Bank"] if bank == "Kotak Bank Regular" else [bank]
            b_in = df_don[(df_don['bank_account'].isin(b_list)) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don.get('add_to_mirror', False) == True)]['amount'].sum() if not df_don.empty else 0
            b_in += df_ledg[df_ledg['bank_name'].isin(b_list)]['credit'].sum() if not df_ledg.empty and 'bank_name' in df_ledg.columns and 'credit' in df_ledg.columns else 0
            b_out = df_exp[(df_exp['bank_account'].isin(b_list)) & (df_exp.get('add_to_mirror', False) == True)]['amount'].sum() if not df_exp.empty else 0
            b_out += df_ledg[df_ledg['bank_name'].isin(b_list)]['debit'].sum() if not df_ledg.empty and 'bank_name' in df_ledg.columns and 'debit' in df_ledg.columns else 0
            bank_balances[bank] = b_in - b_out
        
        total_assets = fixed_assets_val + sum(bank_balances.values())
        other_liab_val = df_liab['value'].sum() if not df_liab.empty else 0.0
        total_liabilities = other_liab_val + surplus
        
        st.markdown("---")
        st.subheader("⚖️ Balance Sheet / Statement of Affairs")
        col_liab, col_assets = st.columns(2)
        with col_liab:
            st.markdown('<div class="bs-box"><div class="bs-header">Liabilities & Funds (ਦੇਣਦਾਰੀਆਂ)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Corpus/Capital Funds & Liab:</span><span>₹ {other_liab_val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Add: Surplus (ਬੱਚਤ):</span><span>₹ {surplus:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Liabilities:</span><span>₹ {total_liabilities:,.2f}</span></div></div>', unsafe_allow_html=True)
        with col_assets:
            st.markdown('<div class="bs-box"><div class="bs-header">Assets (ਸੰਪਤੀ)</div>', unsafe_allow_html=True)
            if asset_totals:
                for atype, aval in asset_totals.items():
                    st.markdown(f'<div class="bs-row"><span>{atype}:</span><span>₹ {aval:,.2f}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bs-row"><span>Fixed Assets:</span><span>₹ 0.00</span></div>', unsafe_allow_html=True)
                
            for b, val in bank_balances.items(): st.markdown(f'<div class="bs-row"><span>{b}:</span><span>₹ {val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Assets:</span><span>₹ {total_assets:,.2f}</span></div></div>', unsafe_allow_html=True)
            
        assets_breakdown = "".join([f"<p>{k}: {v:,.2f}</p>" for k, v in asset_totals.items()]) if asset_totals else f"<p>Fixed Assets: {fixed_assets_val:,.2f}</p>"
        
        full_html = f"<h3>Income & Expenditure Account</h3>{inc_exp_html}<br><h3>Balance Sheet</h3>"
        full_html += f"""<div style="width:100%;"><div class="bs-box"><h4>Liabilities</h4><p>Funds & Liab: {other_liab_val:,.2f}</p><p>Surplus: {surplus:,.2f}</p><hr><p><b>Total: {total_liabilities:,.2f}</b></p></div><div class="bs-box"><h4>Assets</h4>{assets_breakdown}<p>Bank/Cash: {sum(bank_balances.values()):,.2f}</p><hr><p><b>Total: {total_assets:,.2f}</b></p></div></div>"""
        fin_report = generate_html_report("Financial Statements (ਖਾਤੇ)", full_html)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਫਾਈਨਾਂਸ਼ੀਅਲ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

        if is_admin:
            st.markdown("---")
            st.subheader("⚙️ ਸੰਪਤੀ ਅਤੇ ਫੰਡ ਜੋੜੋ (Add Fixed Assets / Funds - Admin Only)")
            ac1, ac2 = st.columns(2)
            with ac1:
                with st.form("add_asset"):
                    st.write("**Fixed Asset (ਪੱਕੀ ਸੰਪਤੀ ਜੋੜੋ)**")
                    a_name = st.text_input("ਸੰਪਤੀ ਦਾ ਨਾਮ (e.g. Building, Furniture)")
                    a_type = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ (Asset Type)", ASSET_TYPES)
                    a_qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=1.0, step=1.0)
                    a_val = st.number_input("ਕੁੱਲ ਮੁੱਲ (Total Value ₹)", min_value=0.0)
                    a_date = st.date_input("ਖਰੀਦ/ਪ੍ਰਾਪਤੀ ਮਿਤੀ (Procurement Date)", value=date.today())
                    if st.form_submit_button("ਸੰਪਤੀ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("assets").insert({"name": a_name, "asset_type": a_type, "quantity": a_qty, "value": a_val, "date_added": str(a_date)}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()
            with ac2:
                with st.form("add_liab"):
                    st.write("**Fund/Liability (ਫੰਡ ਜਾਂ ਉਧਾਰ ਜੋੜੋ)**")
                    l_name = st.text_input("ਫੰਡ ਦਾ ਨਾਮ (e.g. Corpus Fund, Loan)")
                    l_val = st.number_input("ਮੁੱਲ (Value ₹)", min_value=0.0)
                    if st.form_submit_button("ਫੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("liabilities").insert({"name": l_name, "value": l_val, "date_added": str(date.today())}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()
            
            st.write("### 📋 ਮੌਜੂਦਾ ਪੱਕੀ ਸੰਪਤੀ ਅਤੇ ਫੰਡ ਦੀ ਸੂਚੀ (Fixed Asset Register & Funds)")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.write("**🏢 ਪੱਕੀ ਸੰਪਤੀ (Fixed Assets)**")
                if not df_assets.empty:
                    st.dataframe(df_assets[[c for c in ['id', 'asset_type', 'name', 'quantity', 'value', 'date_added'] if c in df_assets.columns]], hide_index=True, use_container_width=True)
                else:
                    st.info("ਕੋਈ ਸੰਪਤੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")
            with col_v2:
                st.write("**💰 ਫੰਡ/ਉਧਾਰ (Liabilities & Funds)**")
                if not df_liab.empty:
                    st.dataframe(df_liab[[c for c in ['id', 'name', 'value', 'date_added'] if c in df_liab.columns]], hide_index=True, use_container_width=True)
                else:
                    st.info("ਕੋਈ ਫੰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif selected_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)":
        st.write("### 📖 ਮੁੱਖ ਲੈਜ਼ਰ / ਡੇਅ ਬੁੱਕ (Consolidated Main Daybook)")
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ (Start Date)", value=date(date.today().year, date.today().month, 1), key="md_start")
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ (End Date)", value=date.today(), key="md_end")

        main_entries = []
        if not df_don.empty:
            for _, row in df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)'].iterrows():
                main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']} (Rec#{row['id']})", 'Account': row.get('bank_account', 'N/A'), 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'Donation'})
        if not df_exp.empty:
            for _, row in df_exp.iterrows():
                main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']} ({row['category']})", 'Account': row.get('bank_account', 'N/A'), 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'Expense'})
        if not df_ledg.empty and 'bank_name' in df_ledg.columns:
            for _, row in df_ledg.iterrows():
                main_entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Account': row.get('bank_name', 'N/A'), 'Credit': float(row.get('credit', 0)), 'Debit': float(row.get('debit', 0)), 'Source': row.get('source', 'Manual')})
                
        df_main = pd.DataFrame(main_entries)
        if not df_main.empty:
            df_main['Date'] = pd.to_datetime(df_main['Date']).dt.date
            df_main = df_main.sort_values(by='Date')
            
            df_before = df_main[df_main['Date'] < start_date]
            opening_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
            
            df_period = df_main[(df_main['Date'] >= start_date) & (df_main['Date'] <= end_date)].copy()
            running_bal = opening_bal
            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['Running Balance'] = balances
            
            closing_bal = opening_bal + df_period['Credit'].sum() - df_period['Debit'].sum()
            
            disp_cols = ['ID', 'Date', 'Description', 'Account', 'Source', 'Credit', 'Debit', 'Running Balance']
            st.dataframe(df_period[disp_cols].style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'Running Balance': '{:.2f}'}), hide_index=True, use_container_width=True)
            report_file_main = generate_html_report("ਮੁੱਖ ਲੈਜ਼ਰ (Consolidated Main Daybook)", df_period[disp_cols].to_html(index=False, border=1, classes='report-table'))
            with open(report_file_main, "r", encoding="utf-8") as file: 
                st.download_button("🖨️ ਮੁੱਖ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ (Print Main Ledger)", data=file.read(), file_name=report_file_main, mime="text/html", type="primary")

    elif selected_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ (Select Bank)", BANK_ACCOUNTS)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ (Start Date)", value=date(date.today().year, date.today().month, 1))
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ (End Date)", value=date.today())

        search_banks = [selected_bank, "Kotak Bank"] if selected_bank == "Kotak Bank Regular" else [selected_bank]

        ledger_entries = []
        if not df_don.empty:
            df_don['add_to_mirror'] = df_don.get('add_to_mirror', False).fillna(False).astype(bool)
            for _, row in df_don[(df_don['bank_account'].isin(search_banks)) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don['add_to_mirror'] == True)].iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']}", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'App (Donation)'})
        if not df_exp.empty:
            df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', False).fillna(False).astype(bool)
            for _, row in df_exp[(df_exp['bank_account'].isin(search_banks)) & (df_exp['add_to_mirror'] == True)].iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'App (Expense)'})
        if not df_ledg.empty and 'bank_name' in df_ledg.columns:
            for _, row in df_ledg[df_ledg['bank_name'].isin(search_banks)].iterrows(): ledger_entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Credit': float(row.get('credit', 0)), 'Debit': float(row.get('debit', 0)), 'Source': row.get('source', 'Manual')})
                
        df_compiled = pd.DataFrame(ledger_entries)
        if not df_compiled.empty:
            df_compiled['Date'] = pd.to_datetime(df_compiled['Date']).dt.date
            df_compiled = df_compiled.sort_values(by='Date')
            df_before = df_compiled[df_compiled['Date'] < start_date]
            opening_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
            df_period = df_compiled[(df_compiled['Date'] >= start_date) & (df_compiled['Date'] <= end_date)].copy()
            running_bal = opening_bal
            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['Running Balance'] = balances
            st.dataframe(df_period[['ID', 'Date', 'Description', 'Source', 'Credit', 'Debit', 'Running Balance']].style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'Running Balance': '{:.2f}'}), hide_index=True, use_container_width=True)

    elif selected_mode == "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)":
        st.write("### 📊 CA ਆਡਿਟ ਅਤੇ ਐਕਸਲ ਬੈਕਅੱਪ")
        st.info("ਆਪਣੇ CA (Chartered Accountant) ਨੂੰ ਆਡਿਟ ਅਤੇ ਰਿਟਰਨ ਭਰਨ ਲਈ ਇਹ ਮੁਕੰਮਲ ਮਲਟੀ-ਸ਼ੀਟ ਐਕਸਲ ਫਾਈਲ ਭੇਜੋ।")
        if st.button("📥 CA ਐਕਸਲ ਬੈਕਅੱਪ ਡਾਊਨਲੋਡ ਕਰੋ (Download Excel)", type="primary"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                pd.DataFrame(supabase.table("donations").select("*").execute().data or []).to_excel(writer, sheet_name='Donations_Receipts', index=False)
                pd.DataFrame(supabase.table("expenses").select("*").execute().data or []).to_excel(writer, sheet_name='Expenses', index=False)
                try: pd.DataFrame(supabase.table("bank_ledger").select("*").execute().data or []).to_excel(writer, sheet_name='Bank_Ledger', index=False)
                except Exception: pass
                try: pd.DataFrame(supabase.table("parties").select("*").execute().data or []).to_excel(writer, sheet_name='Creditors_Debtors', index=False)
                except Exception: pass
                try: pd.DataFrame(supabase.table("cheques").select("*").execute().data or []).to_excel(writer, sheet_name='Cheque_Register', index=False)
                except Exception: pass
                pd.DataFrame(supabase.table("stock").select("*").execute().data or []).to_excel(writer, sheet_name='Stock', index=False)
                try: pd.DataFrame(supabase.table("assets").select("*").execute().data or []).to_excel(writer, sheet_name='Fixed_Assets_Register', index=False)
                except Exception: pass
                pd.DataFrame(supabase.table("students").select("*").execute().data or []).to_excel(writer, sheet_name='Students', index=False)
                try: pd.DataFrame(supabase.table("widows").select("*").execute().data or []).to_excel(writer, sheet_name='Widows_Ration', index=False)
                except Exception: pass
                try: pd.DataFrame(supabase.table("ration_distribution").select("*").execute().data or []).to_excel(writer, sheet_name='Ration_Distribution', index=False)
                except Exception: pass
                pd.DataFrame(supabase.table("receipt_books").select("*").execute().data or []).to_excel(writer, sheet_name='Receipt_Books', index=False)
            st.download_button("📥 ਕਲਿੱਕ ਕਰਕੇ ਡਾਊਨਲੋਡ ਕਰੋ", data=buffer.getvalue(), file_name=f"CA_Audit_Data_{datetime.now().strftime('%d-%m-%Y')}.xlsx", type="primary")

# ==========================================
# 3. STOCK & RECEIPT BOOKS
# ==========================================
elif st.session_state.current_tab == "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)":
    st.header("📦 ਸਟਾਕ ਅਤੇ ਰਸੀਦ ਕਿਤਾਬਾਂ (Stock & Books)")
    modes = ["📦 ਸਟਾਕ (Inventory)", "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"]
    if st.session_state.other_mode not in modes: st.session_state.other_mode = modes[0]
    selected_mode = st.radio("ਸੈਕਸ਼ਨ ਚੁਣੋ:", modes, index=modes.index(st.session_state.other_mode), horizontal=True)
    st.session_state.other_mode = selected_mode
    st.markdown("---")

    if selected_mode == "📦 ਸਟਾਕ (Inventory)":
        col1, col2 = st.columns([1, 2])
        with col1:
            if not is_mgmt:
                with st.form("stock_form", clear_on_submit=True):
                    st.write("### 📦 ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ (Update Stock)")
                    item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ (Item Name)")
                    qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=0.0, step=0.5)
                    unit = st.selectbox("ਇਕਾਈ (Unit)", STOCK_UNITS)
                    est_val = st.number_input("ਅੰਦਾਜ਼ਨ ਕੁੱਲ ਕੀਮਤ (Estimated Total Value ₹ - Optional)", min_value=0.0)
                    proc_date = st.date_input("ਖਰੀਦ/ਪ੍ਰਾਪਤੀ ਮਿਤੀ (Procurement Date)", value=date.today())
                    stock_action = st.radio("ਐਕਸ਼ਨ (Action)", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add Stock)", "ਸਮਾਨ ਵਰਤਿਆ (Remove Stock)"])
                    
                    if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ (Save Stock)", type="primary") and item_name:
                        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        res = supabase.table("stock").select("*").eq("item_name", item_name).execute()
                        if res.data:
                            old_qty = float(res.data[0].get('quantity', 0) or 0)
                            old_val = float(res.data[0].get('estimated_value', 0) or 0)
                            if "Add" in stock_action:
                                new_qty = old_qty + qty
                                new_val = old_val + est_val
                                supabase.table("stock").update({
                                    "quantity": new_qty,
                                    "estimated_value": round(new_val, 2),
                                    "unit": unit,
                                    "procurement_date": str(proc_date),
                                    "last_updated": current_date
                                }).eq("item_name", item_name).execute()
                            else:
                                new_qty = max(0.0, old_qty - qty)
                                new_val = max(0.0, old_val - est_val) if est_val > 0 else (old_val * (new_qty / old_qty) if old_qty > 0 else 0.0)
                                supabase.table("stock").update({
                                    "quantity": new_qty,
                                    "estimated_value": round(new_val, 2),
                                    "unit": unit,
                                    "last_updated": current_date
                                }).eq("item_name", item_name).execute()
                        else:
                            new_qty = qty if "Add" in stock_action else 0.0
                            new_val = est_val if "Add" in stock_action else 0.0
                            supabase.table("stock").insert({
                                "item_name": item_name,
                                "quantity": new_qty,
                                "estimated_value": round(new_val, 2),
                                "unit": unit,
                                "procurement_date": str(proc_date) if "Add" in stock_action else "",
                                "last_updated": current_date
                            }).execute()
                        st.success(f"✅ '{item_name}' ਦਾ ਸਟਾਕ ਸਫਲਤਾਪੂਰਵਕ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ!")
                        time.sleep(1.2); st.rerun()
        with col2:
            st.write("### 📑 ਮੌਜੂਦਾ ਸਟਾਕ ਰਿਪੋਰਟ (Current Stock Inventory)")
            try: stock_res = supabase.table("stock").select("*").gt("quantity", 0).execute().data or []
            except Exception: stock_res = []
            if stock_res:
                df_stock = pd.DataFrame(stock_res)
                disp_cols = [c for c in ['item_name', 'quantity', 'unit', 'estimated_value', 'procurement_date', 'last_updated'] if c in df_stock.columns]
                st.dataframe(df_stock[disp_cols], hide_index=True, use_container_width=True)
                
                report_file_stock = generate_html_report("Current Stock Inventory (ਮੌਜੂਦਾ ਸਟਾਕ)", df_stock[disp_cols].to_html(index=False, border=1, classes='report-table'))
                with open(report_file_stock, "r", encoding="utf-8") as file:
                    st.download_button("🖨️ ਸਟਾਕ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stock, mime="text/html")
            else:
                st.info("ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਸਮਾਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif selected_mode == "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)":
        if is_admin:
            with st.form("book_issue_form", clear_on_submit=True):
                st.write("### 📖 ਨਵੀਂ ਰਸੀਦ ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ")
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    collector_input = st.text_input("ਕਲੈਕਟਰ ਦਾ ਨਾਮ")
                    start_ser = st.number_input("ਸ਼ੁਰੂਆਤੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=1)
                with c_b2:
                    end_ser = st.number_input("ਆਖਰੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=100)
                    issue_date = st.date_input("ਜਾਰੀ ਕਰਨ ਦੀ ਮਿਤੀ", value=date.today())
                if st.form_submit_button("ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ (Issue Book)", type="primary"):
                    if collector_input and end_ser >= start_ser:
                        supabase.table("receipt_books").insert({"collector_name": collector_input, "start_no": int(start_ser), "end_no": int(end_ser), "issued_date": issue_date.strftime("%Y-%m-%d"), "status": "Active"}).execute()
                        st.success(f"✅ ਕਿਤਾਬ ਜਾਰੀ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!")
        st.write("### 📑 ਜਾਰੀ ਕੀਤੀਆਂ ਗਈਆਂ ਕਿਤਾਬਾਂ")
        try: books_all = supabase.table("receipt_books").select("*").execute().data or []
        except Exception: books_all = []
        if books_all:
            df_books = pd.DataFrame(books_all)[['collector_name', 'start_no', 'end_no', 'issued_date', 'status']]
            st.dataframe(df_books, hide_index=True, use_container_width=True)
            report_file_books = generate_html_report("ਜਾਰੀ ਕੀਤੀਆਂ ਰਸੀਦ ਕਿਤਾਬਾਂ (Issued Receipt Books)", df_books.to_html(index=False, border=1, classes='report-table'))
            with open(report_file_books, "r", encoding="utf-8") as file: st.download_button("🖨️ ਕਿਤਾਬਾਂ ਦੀ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_books, mime="text/html")

# ==========================================
# 4. STUDENTS (Separate Tab WITH PHOTO & LANDSCAPE)
# ==========================================
elif st.session_state.current_tab == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
    st.header("🎓 ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ (Student Records)")
    s_tab1, s_tab2 = st.tabs(["➕ ਨਵਾਂ ਵਿਦਿਆਰਥੀ ਦਰਜ ਕਰੋ (Add New)", "📋 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ (Database List)"])
    
    with s_tab1:
        if not is_mgmt:
            with st.form("student_form", clear_on_submit=True):
                st.write("### 🎓 ਨਵਾਂ ਵਿਦਿਆਰਥੀ")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ (Name)")
                    stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone)")
                with col_s2:
                    stu_course = st.selectbox("ਕਲਾਸ (Course)", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"])
                    join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ (Join Date)", value=date.today())
                
                s_photo = st.file_uploader("ਵਿਦਿਆਰਥੀ ਦੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ (Upload Photo)", type=['png', 'jpg', 'jpeg'])
                st.caption("ਫੋਟੋ ਦਾ ਸਾਈਜ਼ ਆਪਣੇ ਆਪ ਛੋਟਾ ਹੋ ਜਾਵੇਗਾ।")

                if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ (Save Record)", type="primary") and stu_name:
                    with st.spinner("ਸੇਵ ਹੋ ਰਿਹਾ ਹੈ..."):
                        try:
                            photo_str = compress_image(s_photo)
                            supabase.table("students").insert({
                                "name": stu_name, 
                                "phone": stu_phone, 
                                "course": stu_course, 
                                "join_date": join_date.strftime("%Y-%m-%d"), 
                                "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ",
                                "photo_base64": photo_str
                            }).execute()
                            st.success(f"✅ '{stu_name}' ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
                        except Exception as e:
                            st.error(f"❌ ਐਰਰ: ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ Supabase ਦੇ students ਟੇਬਲ ਵਿੱਚ 'photo_base64' ਕਾਲਮ ਬਣਾਓ। Details: {e}")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    with s_tab2:
        st.write("### 📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ (Students List)")
        try: student_data = supabase.table("students").select("*").execute().data or []
        except Exception: student_data = []
        
        if student_data:
            df_stu = pd.DataFrame(student_data)
            display_cols = [c for c in ['name', 'phone', 'course', 'join_date', 'pass_date'] if c in df_stu.columns]
            
            st.dataframe(df_stu[display_cols], hide_index=True, use_container_width=True)
            
            st.write("---")
            st.write("#### 🖼️ ਵਿਦਿਆਰਥੀ ਦਾ ਪੂਰਾ ਵੇਰਵਾ ਅਤੇ ਫੋਟੋ (View Details & Photo)")
            s_options = {f"{s.get('name','Unknown')} ({s.get('course', '')}) - {s.get('phone', '')}": s for s in student_data}
            selected_s = st.selectbox("ਵਿਦਿਆਰਥੀ ਚੁਣੋ (Select Student)", list(s_options.keys()))
            
            if selected_s:
                s_d = s_options[selected_s]
                sc1, sc2 = st.columns([3, 1])
                with sc1:
                    st.write(f"**ਨਾਮ:** {s_d.get('name', '')} | **ਕਲਾਸ:** {s_d.get('course', '')}")
                    st.write(f"**ਫ਼ੋਨ:** {s_d.get('phone', '')}")
                    st.write(f"**ਦਾਖਲਾ ਮਿਤੀ:** {s_d.get('join_date', '')} | **ਸਟੇਟਸ:** {s_d.get('pass_date', '')}")
                with sc2:
                    if s_d.get('photo_base64'):
                        st.markdown(f'<img src="data:image/jpeg;base64,{s_d["photo_base64"]}" style="width:120px; border:2px solid #4A1B15; border-radius:5px;">', unsafe_allow_html=True)
                    else:
                        st.info("ਕੋਈ ਫੋਟੋ ਨਹੀਂ ਹੈ।")
            
            df_print = df_stu.copy()
            if 'photo_base64' in df_print.columns:
                df_print['ਫੋਟੋ (Photo)'] = df_print['photo_base64'].apply(
                    lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo'
                )
            else:
                df_print['ਫੋਟੋ (Photo)'] = 'No Photo'

            print_cols_map = {
                'name': 'ਨਾਮ (Name)',
                'phone': 'ਫ਼ੋਨ (Phone)',
                'course': 'ਕਲਾਸ (Course)',
                'join_date': 'ਦਾਖਲਾ ਮਿਤੀ (Join Date)',
                'pass_date': 'ਸਟੇਟਸ (Status)',
                'ਫੋਟੋ (Photo)': 'ਫੋਟੋ (Photo)'
            }
            df_print = df_print.rename(columns={k: v for k, v in print_cols_map.items() if k in df_print.columns})
            print_cols = [v for k, v in print_cols_map.items() if v in df_print.columns]

            html_table = df_print[print_cols].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_stu = generate_html_report_landscape("ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ (Students List)", html_table)
            
            with open(report_file_stu, "r", encoding="utf-8") as file: 
                st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ (Print Landscape Report)", data=file.read(), file_name=report_file_stu, mime="text/html", type="primary")
        else:
            st.info("ਇਸ ਸਮੇਂ ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

# ==========================================
# 5. WIDOWS RATION DATABASE (New Tab WITH IMAGES & NEW FIELDS)
# ==========================================
elif st.session_state.current_tab == "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)":
    st.header("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ ਡਾਟਾਬੇਸ ਅਤੇ ਵੰਡ (Widows Ration & Distribution)")
    
    w_tab1, w_tab2, w_tab3 = st.tabs(["➕ ਨਵਾਂ ਕਾਰਡ / ਪ੍ਰੋਫਾਈਲ ਬਣਾਓ (Add New)", "📋 ਡਾਟਾਬੇਸ ਸੂਚੀ (Database List)", "🛍️ ਰਾਸ਼ਨ ਵੰਡ (Ration Distribution)"])
    
    with w_tab1:
        if not is_mgmt:
            with st.form("widow_form", clear_on_submit=True):
                st.write("### 👵 ਨਵਾਂ ਵਿਧਵਾ ਕਾਰਡ ਦਰਜ ਕਰੋ (New Widow Card Entry)")
                
                c_w1, c_w2, c_w3 = st.columns(3)
                with c_w1:
                    w_form_no = st.text_input("ਫਾਰਮ ਨੰ: (Form No.)")
                    w_name = st.text_input("ਨਾਮ ਬੀਬੀ: (Name) *ਜ਼ਰੂਰੀ*", key="w_req_name")
                    w_husband = st.text_input("ਪਤੀ ਦਾ ਨਾਮ: (Husband's Name)")
                    w_death_date = st.text_input("ਪਤੀ ਦੀ ਮੌਤ ਦੀ ਤਾਰੀਖ:")
                    
                with c_w2:
                    w_card_no = st.text_input("ਕਾਰਡ ਨੰ: (Card No.)")
                    w_age = st.text_input("ਉਮਰ / ਸਾਲ: (Age or DOB)")
                    w_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ: (Phone) *ਜ਼ਰੂਰੀ*")
                    w_issued_by = st.text_input("ਜਾਰੀ ਕਰਤਾ: (Issued By)")
                    
                with c_w3:
                    w_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ (Upload Photo)", type=['png', 'jpg', 'jpeg'])
                    st.caption("ਫੋਟੋ ਦਾ ਸਾਈਜ਼ ਆਪਣੇ ਆਪ ਛੋਟਾ ਹੋ ਜਾਵੇਗਾ।")
                    w_card_date = st.date_input("ਕਾਰਡ ਸ਼ੁਰੂਆਤ ਦੀ ਤਾਰੀਖ:", value=date.today())
                
                w_address = st.text_area("ਪਤਾ (Address):")
                
                st.write("**ਬੱਚੇ (Children Details):**")
                cb1, cb2 = st.columns(2)
                with cb1:
                    w_boys = st.text_area("ਲੜਕੇ (ਉਮਰ, ਕਲਾਸ): \nਉਦਾਹਰਣ: 14 ਸਾਲ - 8ਵੀਂ, 10 ਸਾਲ - 5ਵੀਂ")
                with cb2:
                    w_girls = st.text_area("ਲੜਕੀਆਂ (ਉਮਰ, ਕਲਾਸ): \nਉਦਾਹਰਣ: 12 ਸਾਲ - 6ਵੀਂ")
                
                if st.form_submit_button("ਕਾਰਡ ਸੇਵ ਕਰੋ (Save Card)", type="primary") and w_name:
                    with st.spinner("ਸੇਵ ਹੋ ਰਿਹਾ ਹੈ..."):
                        try:
                            photo_str = compress_image(w_photo)
                            supabase.table("widows").insert({
                                "form_no": w_form_no,
                                "card_no": w_card_no,
                                "name": w_name,
                                "age": w_age,
                                "husband_name": w_husband,
                                "husband_death_date": w_death_date,
                                "phone": w_phone,
                                "address": w_address,
                                "boys_details": w_boys,
                                "girls_details": w_girls,
                                "issued_by": w_issued_by,
                                "join_date": str(w_card_date),
                                "photo_base64": photo_str
                            }).execute()
                            st.success(f"✅ '{w_name}' ਦਾ ਕਾਰਡ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ ਹੈ!")
                        except Exception as e:
                            st.error(f"❌ ਐਰਰ: ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ Supabase ਦੇ widows ਟੇਬਲ ਵਿੱਚ ਨਵੇਂ ਕਾਲਮ ਬਣਾਓ। Details: {e}")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    with w_tab2:
        st.write("### 📑 ਰਜਿਸਟਰਡ ਵਿਧਵਾਵਾਂ ਦੀ ਸੂਚੀ")
        try: widows_data = supabase.table("widows").select("*").execute().data or []
        except Exception: widows_data = []
            
        if widows_data:
            df_w = pd.DataFrame(widows_data)
            display_cols = [c for c in ['card_no', 'name', 'age', 'husband_name', 'phone', 'address', 'join_date'] if c in df_w.columns]
            
            st.dataframe(df_w[display_cols], hide_index=True, use_container_width=True)
            
            st.write("---")
            st.write("#### 🖼️ ਪੂਰਾ ਕਾਰਡ ਅਤੇ ਫੋਟੋ ਦੇਖੋ (View Full Card with Photo)")
            w_options = {f"ਕਾਰਡ: {w.get('card_no', '')} - {w.get('name','Unknown')}": w for w in widows_data}
            selected_w = st.selectbox("ਵਿਧਵਾ ਚੁਣੋ (Select Widow)", list(w_options.keys()))
            
            if selected_w:
                w_d = w_options[selected_w]
                w_col1, w_col2 = st.columns([3, 1])
                with w_col1:
                    st.write(f"**ਫਾਰਮ ਨੰ:** {w_d.get('form_no', '')} | **ਕਾਰਡ ਨੰ:** {w_d.get('card_no', '')}")
                    st.write(f"**ਨਾਮ:** {w_d.get('name', '')} | **ਉਮਰ:** {w_d.get('age', '')}")
                    st.write(f"**ਪਤੀ ਦਾ ਨਾਮ:** {w_d.get('husband_name', '')} (ਮੌਤ: {w_d.get('husband_death_date', '')})")
                    st.write(f"**ਫ਼ੋਨ:** {w_d.get('phone', '')}")
                    st.write(f"**ਪਤਾ:** {w_d.get('address', '')}")
                    st.write(f"**ਲੜਕੇ:** {w_d.get('boys_details', '')} | **ਲੜਕੀਆਂ:** {w_d.get('girls_details', '')}")
                    st.write(f"**ਕਾਰਡ ਜਾਰੀ ਮਿਤੀ:** {w_d.get('join_date', '')} | **ਜਾਰੀ ਕਰਤਾ:** {w_d.get('issued_by', '')}")
                with w_col2:
                    if w_d.get('photo_base64'):
                        st.markdown(f'<img src="data:image/jpeg;base64,{w_d["photo_base64"]}" style="width:150px; border:2px solid #4A1B15; border-radius:5px;">', unsafe_allow_html=True)
                    else:
                        st.info("ਕੋਈ ਫੋਟੋ ਨਹੀਂ ਹੈ।")
            
            df_print_w = df_w.copy()
            if 'photo_base64' in df_print_w.columns:
                df_print_w['ਫੋਟੋ (Photo)'] = df_print_w['photo_base64'].apply(
                    lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo'
                )
            else:
                df_print_w['ਫੋਟੋ (Photo)'] = 'No Photo'

            print_cols_map_w = {
                'card_no': 'ਕਾਰਡ ਨੰ (Card)',
                'name': 'ਨਾਮ (Name)',
                'age': 'ਉਮਰ (Age)',
                'husband_name': 'ਪਤੀ ਦਾ ਨਾਮ (Husband)',
                'phone': 'ਫ਼ੋਨ (Phone)',
                'address': 'ਪਤਾ (Address)',
                'ਫੋਟੋ (Photo)': 'ਫੋਟੋ (Photo)'
            }
            df_print_w = df_print_w.rename(columns={k: v for k, v in print_cols_map_w.items() if k in df_print_w.columns})
            print_cols_w = [v for k, v in print_cols_map_w.items() if v in df_print_w.columns]

            html_table_w = df_print_w[print_cols_w].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_w = generate_html_report_landscape("ਵਿਧਵਾਵਾਂ ਦੀ ਸੂਚੀ (Widows Database)", html_table_w)
            
            with open(report_file_w, "r", encoding="utf-8") as file: 
                st.download_button("🖨️ ਵਿਧਵਾਵਾਂ ਦੀ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ (Print Landscape)", data=file.read(), file_name=report_file_w, mime="text/html", type="primary")
        else:
            st.info("ਇਸ ਸਮੇਂ ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    with w_tab3:
        st.write("### 🛍️ ਮਹੀਨਾਵਾਰ ਰਾਸ਼ਨ ਵੰਡ (Monthly Ration Distribution)")
        try:
            widows_list = supabase.table("widows").select("*").execute().data or []
            stock_list = supabase.table("stock").select("*").gt("quantity", 0).execute().data or []
        except Exception:
            widows_list, stock_list = [], []
            
        if not widows_list:
            st.warning("⚠️ ਪਹਿਲਾਂ ਵਿਧਵਾਵਾਂ ਦਾ ਪ੍ਰੋਫਾਈਲ ਦਰਜ ਕਰੋ।")
        elif not stock_list:
            st.warning("⚠️ ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਸਮਾਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਸਟਾਕ ਅੱਪਡੇਟ ਕਰੋ।")
        else:
            if not is_mgmt:
                w_names = [f"ਕਾਰਡ {w.get('card_no','-')} - {w.get('name','Unknown')} ({w.get('phone','')})" for w in widows_list]
                s_items = [s['item_name'] for s in stock_list]
                s_dict = {s['item_name']: float(s.get('quantity', 0) or 0) for s in stock_list}
                
                with st.form("ration_dist_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_widow = st.selectbox("ਕਿਸ ਨੂੰ ਰਾਸ਼ਨ ਦਿੱਤਾ? (Select Widow)", w_names)
                        dist_date = st.date_input("ਵੰਡਣ ਦੀ ਮਿਤੀ (Distribution Date)", value=date.today())
                    with col2:
                        selected_item = st.selectbox("ਕਿਹੜਾ ਸਮਾਨ ਦਿੱਤਾ? (Select Item)", s_items)
                        qty_to_give = st.number_input(f"ਮਾਤਰਾ - ਸਟਾਕ ਵਿੱਚ ਮੌਜੂਦ: {s_dict.get(selected_item, 0)}", min_value=0.5, step=0.5)
                        
                    if st.form_submit_button("ਰਾਸ਼ਨ ਵੰਡ ਸੇਵ ਕਰੋ (Save & Update Stock)", type="primary"):
                        old_qty = s_dict.get(selected_item, 0)
                        if qty_to_give > old_qty:
                            st.error(f"❌ ਗਲਤੀ: ਸਟਾਕ ਵਿੱਚ ਸਿਰਫ਼ {old_qty} ਮਾਤਰਾ ਬਾਕੀ ਹੈ!")
                        else:
                            new_qty = max(0.0, old_qty - qty_to_give)
                            curr_stock = supabase.table("stock").select("*").eq("item_name", selected_item).execute().data
                            if curr_stock:
                                curr_val = float(curr_stock[0].get('estimated_value', 0) or 0)
                                new_val = (curr_val * (new_qty / old_qty)) if old_qty > 0 else 0.0
                                supabase.table("stock").update({
                                    "quantity": new_qty, 
                                    "estimated_value": round(new_val, 2),
                                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }).eq("item_name", selected_item).execute()
                            
                            widow_just_name = selected_widow.split(" - ")[1].split(" (")[0] if " - " in selected_widow else selected_widow.split(" (")[0]
                            supabase.table("ration_distribution").insert({
                                "widow_name": widow_just_name,
                                "item_name": selected_item,
                                "quantity": qty_to_give,
                                "distribution_date": str(dist_date)
                            }).execute()
                            
                            st.success(f"✅ {widow_just_name} ਨੂੰ {qty_to_give} {selected_item} ਦੇ ਦਿੱਤਾ ਗਿਆ ਹੈ! ਸਟਾਕ ਅਪਡੇਟ ਹੋ ਗਿਆ।")
                            time.sleep(1.5); st.rerun()
                            
        st.markdown("---")
        st.write("#### 📑 ਪਿਛਲੀ ਰਾਸ਼ਨ ਵੰਡ ਦਾ ਰਿਕਾਰਡ (Recent Distributions)")
        try: dist_data = supabase.table("ration_distribution").select("*").order("distribution_date", desc=True).execute().data or []
        except Exception: dist_data = []
        if dist_data:
            df_dist = pd.DataFrame(dist_data)[['id', 'distribution_date', 'widow_name', 'item_name', 'quantity']]
            st.dataframe(df_dist, hide_index=True, use_container_width=True)
            report_file_dist = generate_html_report("ਰਾਸ਼ਨ ਵੰਡ ਰਿਕਾਰਡ (Ration Distribution)", df_dist.to_html(index=False, border=1, classes='report-table'))
            with open(report_file_dist, "r", encoding="utf-8") as file: st.download_button("🖨️ ਵੰਡ ਰਿਕਾਰਡ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_dist, mime="text/html")
        else:
            st.info("ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

# ==========================================
# 🧑‍💼 ADMIN/STAFF: STAFF & ATTENDANCE MANAGEMENT
# ==========================================
elif st.session_state.current_tab == "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)":
    st.header("🧑‍💼 ਸਟਾਫ ਮੈਨੇਜਮੈਂਟ ਅਤੇ ਹਾਜ਼ਰੀ (Staff Management)")
    
    tab_list = ["👤 ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Profiles)", "🛡️ ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ (Admin Approvals)", "📋 ਸਭ ਦੀ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ (Monthly Report)"]
    att_tabs = st.tabs(tab_list)
    
    # --- 1. STAFF PROFILES (ADMIN/MGMT ONLY) ---
    with att_tabs[0]:
        col_st1, col_st2 = st.columns([1, 2])
        with col_st1:
            if is_admin or is_mgmt:
                with st.form("staff_profile_form", clear_on_submit=True):
                    st.write("### ➕ ਨਵਾਂ ਸਟਾਫ ਦਰਜ ਕਰੋ")
                    st_name = st.text_input("ਸਟਾਫ ਦਾ ਨਾਮ (Name) *ਜ਼ਰੂਰੀ*")
                    st_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone)")
                    st_role = st.selectbox("ਡਿਊਟੀ / ਅਹੁਦਾ (Role/Duty)", ["ਮੈਨੇਜਰ", "ਅਧਿਆਪਕ", "ਕਲਰਕ", "ਸੇਵਾਦਾਰ", "ਡਰਾਈਵਰ", "ਹੋਰ"])
                    
                    st_login = st.selectbox("ਸਿਸਟਮ ਲਾਗਇਨ ਆਈ.ਡੀ (System Login ID)", ["ਕੋਈ ਨਹੀਂ (None)", "emp1", "emp2", "emp3", "emp4", "emp5"])
                    st.caption("ਜੋ ID ਇੱਥੇ ਚੁਣੋਗੇ, ਕਰਮਚਾਰੀ ਉਸੇ ID ਨਾਲ ਲਾਗਇਨ ਕਰਕੇ ਆਪਣੀ ਹਾਜ਼ਰੀ ਲਗਾ ਸਕੇਗਾ।")
                    
                    st_join = st.date_input("ਜੁਆਇਨਿੰਗ ਮਿਤੀ (Join Date)", value=date.today())
                    st_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ (Upload Photo)", type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button("ਪ੍ਰੋਫਾਈਲ ਸੇਵ ਕਰੋ (Save Staff)", type="primary") and st_name:
                        with st.spinner("ਸੇਵ ਹੋ ਰਿਹਾ ਹੈ..."):
                            try:
                                photo_str = compress_image(st_photo)
                                login_val = st_login if "emp" in st_login else ""
                                supabase.table("staff_profiles").insert({
                                    "name": st_name,
                                    "phone": st_phone,
                                    "role": st_role,
                                    "join_date": str(st_join),
                                    "photo_base64": photo_str,
                                    "login_id": login_val
                                }).execute()
                                st.success(f"✅ '{st_name}' ਦਾ ਪ੍ਰੋਫਾਈਲ ਸੇਵ ਹੋ ਗਿਆ!")
                            except Exception as e:
                                st.error(f"❌ ਐਰਰ: ਕਿਰਪਾ ਕਰਕੇ SQL Code ਚਲਾ ਕੇ 'login_id' ਵਾਲਾ ਕਾਲਮ ਬਣਾਓ। Details: {e}")
            else:
                st.info("⚠️ ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ ਸਿਰਫ਼ ਐਡਮਿਨ ਜਾਂ ਮੈਨੇਜਮੈਂਟ ਦਰਜ ਕਰ ਸਕਦੇ ਹਨ।")
                
        with col_st2:
            st.write("### 📋 ਸਟਾਫ ਦੀ ਸੂਚੀ (Staff List)")
            try: staff_data = supabase.table("staff_profiles").select("*").execute().data or []
            except Exception: staff_data = []
            
            if staff_data:
                df_staff = pd.DataFrame(staff_data)
                disp_st_cols = [c for c in ['name', 'phone', 'role', 'login_id', 'join_date'] if c in df_staff.columns]
                st.dataframe(df_staff[disp_st_cols], hide_index=True, use_container_width=True)
                
                df_print_st = df_staff.copy()
                if 'photo_base64' in df_print_st.columns:
                    df_print_st['ਫੋਟੋ (Photo)'] = df_print_st['photo_base64'].apply(
                        lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo'
                    )
                else:
                    df_print_st['ਫੋਟੋ (Photo)'] = 'No Photo'

                print_cols_map_st = {
                    'name': 'ਨਾਮ (Name)', 'phone': 'ਫ਼ੋਨ (Phone)',
                    'role': 'ਅਹੁਦਾ (Role)', 'login_id': 'ਲਾਗਇਨ (Login)',
                    'join_date': 'ਮਿਤੀ (Join Date)', 'ਫੋਟੋ (Photo)': 'ਫੋਟੋ (Photo)'
                }
                df_print_st = df_print_st.rename(columns={k: v for k, v in print_cols_map_st.items() if k in df_print_st.columns})
                print_cols_st = [v for k, v in print_cols_map_st.items() if v in df_print_st.columns]

                html_table_st = df_print_st[print_cols_st].to_html(index=False, border=1, classes='report-table', escape=False)
                report_file_st = generate_html_report_landscape("ਸਟਾਫ ਦੀ ਸੂਚੀ (Staff List)", html_table_st)
                
                with open(report_file_st, "r", encoding="utf-8") as file: 
                    st.download_button("🖨️ ਸਟਾਫ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ (Print Landscape)", data=file.read(), file_name=report_file_st, mime="text/html", type="primary")
            else:
                st.info("ਕੋਈ ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    # --- 2. ADMIN APPROVALS ---
    with att_tabs[1]:
        st.write("### 🛡️ ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਹਾਜ਼ਰੀ ਬੇਨਤੀਆਂ (Pending Leave Requests)")
        try:
            att_reqs = supabase.table("attendance_requests").select("*").eq("status", "Pending").execute().data or []
        except Exception: att_reqs = []
        
        if att_reqs:
            df_areq = pd.DataFrame(att_reqs)[['id', 'staff_name', 'date', 'requested_status', 'reason', 'created_at']]
            st.dataframe(df_areq, hide_index=True, use_container_width=True)
            
            req_choices = [f"ID: {r['id']} - {r['staff_name']} ({r['date']} : {r['requested_status']})" for r in att_reqs]
            sel_req_str = st.selectbox("ਬੇਨਤੀ ਚੁਣੋ (Select Request)", req_choices)
            r_id = int(sel_req_str.split(" ")[1])
            
            col_aa, col_ar = st.columns(2)
            with col_aa:
                if st.button("✅ ਹਾਜ਼ਰੀ ਮਨਜ਼ੂਰ ਕਰੋ (Approve)", type="primary"):
                    target_r = next((r for r in att_reqs if int(r['id']) == r_id), None)
                    if target_r:
                        existing = supabase.table("attendance").select("*").eq("staff_name", target_r['staff_name']).eq("date", target_r['date']).execute().data
                        if existing:
                            supabase.table("attendance").update({"status": target_r['requested_status']}).eq("id", existing[0]['id']).execute()
                        else:
                            supabase.table("attendance").insert({
                                "staff_name": target_r['staff_name'], "date": target_r['date'],
                                "in_time": "Manual", "out_time": "Manual", "status": target_r['requested_status']
                            }).execute()
                        
                        supabase.table("attendance_requests").update({"status": "Approved"}).eq("id", r_id).execute()
                        st.success("✅ ਹਾਜ਼ਰੀ ਲੱਗ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            with col_ar:
                if st.button("❌ ਬੇਨਤੀ ਰੱਦ ਕਰੋ (Reject)"):
                    supabase.table("attendance_requests").update({"status": "Rejected"}).eq("id", r_id).execute()
                    st.error("❌ ਬੇਨਤੀ ਰੱਦ ਕੀਤੀ ਗਈ ਹੈ।"); time.sleep(1.5); st.rerun()
        else:
            st.info("ਇਸ ਸਮੇਂ ਕੋਈ ਪੈਂਡਿੰਗ ਹਾਜ਼ਰੀ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")

    # --- 3. ALL REPORTS (MONTHLY MATRIX VIEW - FIXED) ---
    with att_tabs[2]:
        st.write("### 📅 ਮਹੀਨਾਵਾਰ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ (Monthly Attendance Report)")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_month = st.selectbox("ਮਹੀਨਾ (Month)", range(1, 13), index=date.today().month - 1)
        with col_m2:
            sel_year = st.selectbox("ਸਾਲ (Year)", range(2024, 2035), index=date.today().year - 2024)
            
        num_days = calendar.monthrange(sel_year, sel_month)[1]
        start_date_str = f"{sel_year}-{sel_month:02d}-01"
        end_date_str = f"{sel_year}-{sel_month:02d}-{num_days:02d}"
        
        try:
            all_att = supabase.table("attendance").select("*").gte("date", start_date_str).lte("date", end_date_str).execute().data or []
            
            if all_att:
                df_att = pd.DataFrame(all_att)
                df_att['date'] = pd.to_datetime(df_att['date'])
                df_att['day'] = df_att['date'].dt.day
                
                def get_status_code(status_str):
                    if not status_str: return "-"
                    s = str(status_str).lower()
                    if "present" in s or "ਹਾਜ਼ਰ" in s: return "P"
                    if "absent" in s or "ਛੁੱਟੀ" in s or "ਗੈਰ" in s: return "A"
                    if "half" in s or "ਅੱਧਾ" in s: return "HD"
                    return "P" # fallback
                    
                df_att['status_code'] = df_att['status'].apply(get_status_code)
                
                # Pivot Table
                pivot_df = df_att.pivot_table(index='staff_name', columns='day', values='status_code', aggfunc='last')
                
                # Ensure all days 1 to 31/30 are columns
                all_days = list(range(1, num_days + 1))
                pivot_df = pivot_df.reindex(columns=all_days).fillna("-")
                
                # Totals
                pivot_df['Total P'] = (pivot_df[all_days] == 'P').sum(axis=1) + ((pivot_df[all_days] == 'HD').sum(axis=1) * 0.5)
                pivot_df['Total A'] = (pivot_df[all_days] == 'A').sum(axis=1)
                
                pivot_df = pivot_df.reset_index()
                pivot_df.rename(columns={'staff_name': 'Staff Name'}, inplace=True)
                
                st.dataframe(pivot_df, hide_index=True, use_container_width=True)
                
                html_table_att = pivot_df.to_html(index=False, border=1, classes='report-table')
                report_title = f"ਮਹੀਨਾਵਾਰ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ - {sel_month}/{sel_year} (Monthly Attendance)"
                report_file_att = generate_html_report_landscape(report_title, html_table_att)
                
                with open(report_file_att, "r", encoding="utf-8") as file:
                    st.download_button("🖨️ ਮਹੀਨਾਵਾਰ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Monthly Landscape)", data=file.read(), file_name=report_file_att, mime="text/html", type="primary")
                    
            else:
                st.info("ਇਸ ਮਹੀਨੇ ਦਾ ਕੋਈ ਹਾਜ਼ਰੀ ਰਿਕਾਰਡ ਨਹੀਂ ਮਿਲਿਆ। (No records found for this month)")
        except Exception as e:
            st.error(f"Error generating report: {e}")

# ==========================================
# 6. ADMIN & BULK UPLOAD MANAGEMENT
# ==========================================
elif st.session_state.current_tab == "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)":
    st.header("⚙️ ਐਡਮਿਨ, ਡਿਲੀਟ ਅਤੇ ਸੋਧ (Edit) ਸਿਸਟਮ")
    
    if is_admin:
        modes = ["📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)", "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
    else:
        modes = ["🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
        
    if st.session_state.admin_mode not in modes: 
        st.session_state.admin_mode = modes[0]
        
    selected_mode = st.radio("ਐਡਮਿਨ ਟੂਲ ਚੁਣੋ:", modes, index=modes.index(st.session_state.admin_mode), horizontal=True)
    st.session_state.admin_mode = selected_mode
    st.markdown("---")

    t_map = {
        "ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", 
        "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", "ਪਾਰਟੀ (Party)": "parties", 
        "ਚੈੱਕ (Cheque)": "cheques", "ਸੰਪਤੀ (Asset)": "assets", 
        "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", 
        "ਵਿਦਿਆਰਥੀ (Student)": "students", "ਵਿਧਵਾ (Widow)": "widows", 
        "ਰਾਸ਼ਨ ਵੰਡ (Ration)": "ration_distribution", "ਰਸੀਦ ਕਿਤਾਬ (Receipt Book)": "receipt_books",
        "ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Staff)": "staff_profiles", "ਹਾਜ਼ਰੀ (Attendance)": "attendance"
    }

    if selected_mode == "📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)" and is_admin:
        st.write("### 📂 ਪੁਰਾਣਾ ਡਾਟਾ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ (Upload Data via Excel)")
        st.info("ਇੱਕੋ ਕਲਿੱਕ ਵਿੱਚ ਐਕਸਲ ਸ਼ੀਟ ਰਾਹੀਂ ਦਾਨੀਆਂ, ਵਿਦਿਆਰਥੀਆਂ ਜਾਂ ਵਿਧਵਾਵਾਂ ਦਾ ਵੱਡਾ ਰਿਕਾਰਡ ਅੱਪਲੋਡ ਕਰੋ।")
        
        upload_type = st.selectbox("ਡਾਟਾ ਚੁਣੋ (Select Data Type)", ["ਦਾਨ (Donations)", "ਵਿਦਿਆਰਥੀ (Students)", "ਵਿਧਵਾਵਾਂ (Widows)"])
        uploaded_file = st.file_uploader("ਐਕਸਲ ਫਾਈਲ ਚੁਣੋ (.xlsx, .xls)", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            df_upload.columns = df_upload.columns.str.lower()
            st.dataframe(df_upload.head(10), use_container_width=True)
            
            if st.button(f"🚀 ਸਾਰਾ ਡਾਟਾ {upload_type} ਵਿੱਚ ਸੇਵ ਕਰੋ (Upload All)", type="primary"):
                try:
                    if upload_type == "ਦਾਨ (Donations)":
                        if 'add_to_mirror' not in df_upload.columns: df_upload['add_to_mirror'] = True
                        if 'balance' in df_upload.columns: df_upload['balance'] = df_upload['balance'].fillna(0)
                        df_upload['add_to_mirror'] = df_upload['add_to_mirror'].fillna(True).astype(bool)
                        supabase.table("donations").insert(df_upload.to_dict(orient='records')).execute()
                    
                    elif upload_type == "ਵਿਦਿਆਰਥੀ (Students)":
                        supabase.table("students").insert(df_upload.to_dict(orient='records')).execute()
                        
                    elif upload_type == "ਵਿਧਵਾਵਾਂ (Widows)":
                        supabase.table("widows").insert(df_upload.to_dict(orient='records')).execute()
                        
                    st.success(f"✅ {upload_type} ਦਾ ਸਾਰਾ ਡਾਟਾ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਲੋਡ ਹੋ ਗਿਆ ਹੈ!")
                except Exception as e:
                    st.error(f"❌ ਐਰਰ: ਕਿਰਪਾ ਕਰਕੇ ਐਕਸਲ ਸ਼ੀਟ ਦੇ ਕਾਲਮ ਚੈੱਕ ਕਰੋ। (Details: {e})")

    elif selected_mode == "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)":
        if is_admin:
            st.subheader("🔔 ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਡਿਲੀਟ ਬੇਨਤੀਆਂ")
            try: reqs = supabase.table("deletion_requests").select("*").eq("status", "Pending").execute().data
            except Exception: reqs = []
                
            if reqs:
                st.dataframe(pd.DataFrame(reqs)[['id', 'table_name', 'record_id', 'details', 'created_at']], hide_index=True, use_container_width=True)
                
                req_choices = [f"ID: {r['id']} ({r['table_name']})" for r in reqs]
                selected_req_str = st.selectbox("ਬੇਨਤੀ ਚੁਣੋ (Select Request to Action)", req_choices, key="sel_del_req")
                req_id = int(selected_req_str.split(" ")[1])
                
                col_a, col_r = st.columns(2)
                with col_a:
                    if st.button("✅ ਡਿਲੀਟ ਮਨਜ਼ੂਰ (Approve & Delete)", type="primary"):
                        target_req = next((r for r in reqs if int(r['id']) == req_id), None)
                        if target_req:
                            try:
                                if target_req['table_name'] == "stock": supabase.table(target_req['table_name']).delete().eq("item_name", str(target_req['record_id'])).execute()
                                else: supabase.table(target_req['table_name']).delete().eq("id", int(float(target_req['record_id']))).execute()
                                supabase.table("deletion_requests").update({"status": "Approved"}).eq("id", req_id).execute()
                                st.success("✅ ਐਂਟਰੀ ਪੱਕੇ ਤੌਰ 'ਤੇ ਡਿਲੀਟ ਹੋ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                with col_r:
                    if st.button("❌ ਬੇਨਤੀ ਰੱਦ ਕਰੋ (Reject)", type="primary"):
                        supabase.table("deletion_requests").update({"status": "Rejected"}).eq("id", req_id).execute()
                        st.error("❌ ਬੇਨਤੀ ਰੱਦ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")
            st.markdown("---")
            
        st.subheader("⚡ ਡਿਲੀਟ ਕਰਨ ਲਈ ਐਂਟਰੀਆਂ ਲੱਭੋ")
        if is_staff: st.info("⚠️ ਸਟਾਫ ਸਿੱਧਾ ਡਿਲੀਟ ਨਹੀਂ ਕਰ ਸਕਦਾ। ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਕੋਲ ਮਨਜ਼ੂਰੀ ਲਈ ਜਾਵੇਗੀ।")
            
        del_type = st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚੋਂ ਡਿਲੀਟ ਕਰਨਾ ਹੈ?", list(t_map.keys()), key="del_cat")
        table_name = t_map[del_type]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="del_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="del_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="del_dt") if filter_date else []

        with st.spinner("ਡਾਟਾ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ..."):
            try: raw_data = supabase.table(table_name).select("*").execute().data or []
            except Exception as e: raw_data = []

        if raw_data:
            df_del = pd.DataFrame(raw_data)
            if search_name:
                search_cols = [c for c in ['name', 'description', 'item_name', 'party_name', 'collector_name', 'widow_name', 'staff_name'] if c in df_del.columns]
                if search_cols:
                    mask = df_del[search_cols[0]].astype(str).str.contains(search_name, case=False, na=False)
                    for c in search_cols[1:]: mask = mask | df_del[c].astype(str).str.contains(search_name, case=False, na=False)
                    df_del = df_del[mask]
                    
            if filter_date and len(date_range) == 2:
                d_start, d_end = date_range
                date_cols = [c for c in ['date', 'txn_date', 'created_at', 'cheque_date', 'last_updated', 'join_date', 'distribution_date', 'issued_date', 'date_added'] if c in df_del.columns]
                if date_cols:
                    d_col = date_cols[0]
                    df_del['__temp_date'] = pd.to_datetime(df_del[d_col], errors='coerce').dt.date
                    df_del = df_del[(df_del['__temp_date'] >= d_start) & (df_del['__temp_date'] <= d_end)]
                    df_del = df_del.drop(columns=['__temp_date'])
                    
            if not df_del.empty:
                st.success(f"✅ ਕੁੱਲ {len(df_del)} ਐਂਟਰੀਆਂ ਮਿਲੀਆਂ ਹਨ।")
                for col in df_del.columns: df_del[col] = df_del[col].fillna("").astype(str)
                df_del.insert(0, "Select", False)
                df_del = df_del.reset_index(drop=True)
                
                edited_df = st.data_editor(
                    df_del,
                    column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ (Select)", default=False)},
                    disabled=[c for c in df_del.columns if c != "Select"],
                    hide_index=True,
                    use_container_width=True,
                    key=f"editor_delete_{table_name}"
                )
                
                selected_rows = edited_df[edited_df["Select"] == True]
                
                if not selected_rows.empty:
                    st.warning(f"⚠️ ਤੁਸੀਂ {len(selected_rows)} ਐਂਟਰੀਆਂ ਚੁਣੀਆਂ ਹਨ।")
                    if is_admin:
                        if st.button("🛑 ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ (Delete Selected)", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else int(float(row['id']))
                                col_name = "item_name" if table_name == "stock" else "id"
                                supabase.table(table_name).delete().eq(col_name, rec_id).execute()
                            st.success("✅ ਡਿਲੀਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਬੇਨਤੀ ਭੇਜੋ (Request Delete)", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else str(row['id'])
                                row_dict = row.drop('Select').to_dict()
                                supabase.table("deletion_requests").insert({
                                    "table_name": table_name, 
                                    "record_id": str(rec_id), 
                                    "details": str(row_dict), 
                                    "requested_by": "staff"
                                }).execute()
                            st.success("✅ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਖੋਜ ਅਨੁਸਾਰ ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")
        else: st.info("ਟੇਬਲ ਖਾਲੀ ਹੈ।")

    elif selected_mode == "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)":
        if is_admin:
            st.subheader("🔔 ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਸੋਧ (Edit) ਬੇਨਤੀਆਂ")
            try: reqs_edit = supabase.table("edit_requests").select("*").eq("status", "Pending").execute().data
            except Exception: reqs_edit = []
            
            if reqs_edit:
                df_reqs = pd.DataFrame(reqs_edit)[['id', 'table_name', 'record_id', 'changes', 'created_at']]
                st.dataframe(df_reqs, hide_index=True, use_container_width=True)
                
                req_choices = [f"ID: {r['id']} ({r['table_name']} - Rec: {r['record_id']})" for r in reqs_edit]
                selected_req_str = st.selectbox("ਬੇਨਤੀ ਚੁਣੋ (Select Edit Request)", req_choices, key="sel_edit_req")
                req_id = int(selected_req_str.split(" ")[1])
                
                col_ea, col_er = st.columns(2)
                with col_ea:
                    if st.button("✅ ਸੋਧ ਮਨਜ਼ੂਰ ਕਰੋ (Approve & Update)", type="primary"):
                        target_req = next((r for r in reqs_edit if int(r['id']) == req_id), None)
                        if target_req:
                            try:
                                changes_dict = json.loads(target_req['changes'])
                                rec_id = target_req['record_id'] if target_req['table_name'] == "stock" else int(float(target_req['record_id']))
                                col_name = "item_name" if target_req['table_name'] == "stock" else "id"
                                
                                supabase.table(target_req['table_name']).update(changes_dict).eq(col_name, rec_id).execute()
                                supabase.table("edit_requests").update({"status": "Approved"}).eq("id", req_id).execute()
                                st.success("✅ ਐਂਟਰੀ ਸਫਲਤਾਪੂਰਵਕ ਅਪਡੇਟ ਹੋ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                with col_er:
                    if st.button("❌ ਬੇਨਤੀ ਰੱਦ ਕਰੋ (Reject)", type="primary"):
                        supabase.table("edit_requests").update({"status": "Rejected"}).eq("id", req_id).execute()
                        st.error("❌ ਬੇਨਤੀ ਰੱਦ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else:
                st.info("ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")
            st.markdown("---")
            
        st.subheader("⚡ ਸੋਧਣ ਲਈ ਐਂਟਰੀਆਂ ਲੱਭੋ ਅਤੇ ਬਦਲੋ (Edit Entries)")
        if is_staff: st.info("⚠️ ਸਟਾਫ ਸਿੱਧਾ ਅਪਡੇਟ ਨਹੀਂ ਕਰ ਸਕਦਾ। ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਕੋਲ ਮਨਜ਼ੂਰੀ ਲਈ ਜਾਵੇਗੀ।")
        
        edit_type = st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚ ਸੋਧ ਕਰਨੀ ਹੈ? (Select Category)", list(t_map.keys()), key="edit_cat")
        table_name = t_map[edit_type]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="edit_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="edit_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="edit_dt") if filter_date else []
            
        with st.spinner("ਡਾਟਾ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ..."):
            try: raw_data = supabase.table(table_name).select("*").execute().data or []
            except Exception as e: raw_data = []
            
        if raw_data:
            df_edit = pd.DataFrame(raw_data)
            if search_name:
                search_cols = [c for c in ['name', 'description', 'item_name', 'party_name', 'collector_name', 'widow_name', 'staff_name'] if c in df_edit.columns]
                if search_cols:
                    mask = df_edit[search_cols[0]].astype(str).str.contains(search_name, case=False, na=False)
                    for c in search_cols[1:]: mask = mask | df_edit[c].astype(str).str.contains(search_name, case=False, na=False)
                    df_edit = df_edit[mask]
            if filter_date and len(date_range) == 2:
                d_start, d_end = date_range
                date_cols = [c for c in ['date', 'txn_date', 'created_at', 'cheque_date', 'last_updated', 'join_date', 'distribution_date', 'issued_date', 'date_added'] if c in df_edit.columns]
                if date_cols:
                    d_col = date_cols[0]
                    df_edit['__temp_date'] = pd.to_datetime(df_edit[d_col], errors='coerce').dt.date
                    df_edit = df_edit[(df_edit['__temp_date'] >= d_start) & (df_edit['__temp_date'] <= d_end)]
                    df_edit = df_edit.drop(columns=['__temp_date'])
                    
            if not df_edit.empty:
                st.success("✅ ਹੇਠਾਂ ਦਿੱਤੇ ਟੇਬਲ ਵਿੱਚ ਸਿੱਧਾ ਕਲਿੱਕ ਕਰਕੇ ਬਦਲਾਅ ਕਰੋ (Double click a cell to edit):")
                df_edit = df_edit.reset_index(drop=True)
                df_edit = df_edit.where(pd.notnull(df_edit), None)
                
                pk_col = 'item_name' if table_name == 'stock' else 'id'
                disabled_cols = [pk_col] if pk_col in df_edit.columns else []
                
                edited_df = st.data_editor(
                    df_edit,
                    hide_index=True,
                    disabled=disabled_cols,
                    use_container_width=True,
                    key=f"editor_edit_{table_name}"
                )
                
                changed_rows = []
                orig_records = df_edit.to_dict('records')
                edited_records = edited_df.to_dict('records')
                
                for i in range(len(orig_records)):
                    orig = orig_records[i]
                    ed = edited_records[i]
                    changes = {}
                    for k in ed.keys():
                        orig_val = orig[k]
                        ed_val = ed[k]
                        if pd.isna(orig_val): orig_val = None
                        if pd.isna(ed_val): ed_val = None
                        
                        if str(orig_val) != str(ed_val):
                            if isinstance(orig_val, (int, float)) and ed_val is not None:
                                try:
                                    ed_val = float(ed_val) if '.' in str(ed_val) else int(ed_val)
                                except ValueError:
                                    pass
                            changes[k] = ed_val
                    
                    if changes:
                        record_id = orig['item_name'] if table_name == 'stock' else orig['id']
                        changed_rows.append((record_id, changes))
                        
                if changed_rows:
                    st.warning(f"⚠️ ਤੁਸੀਂ {len(changed_rows)} ਐਂਟਰੀਆਂ ਵਿੱਚ ਬਦਲਾਅ ਕੀਤੇ ਹਨ।")
                    if is_admin:
                        if st.button("💾 ਬਦਲਾਅ ਸੇਵ ਕਰੋ (Update Directly)", type="primary"):
                            for rec_id, changes in changed_rows:
                                col_name = "item_name" if table_name == "stock" else "id"
                                supabase.table(table_name).update(changes).eq(col_name, rec_id).execute()
                            st.success("✅ ਡਾਟਾਬੇਸ ਅਪਡੇਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ (Request Edit Approval)", type="primary"):
                            for rec_id, changes in changed_rows:
                                supabase.table("edit_requests").insert({
                                    "table_name": table_name,
                                    "record_id": str(rec_id),
                                    "changes": json.dumps(changes),
                                    "status": "Pending",
                                    "requested_by": "staff"
                                }).execute()
                            st.success("✅ ਬੇਨਤੀਆਂ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")
