import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import io
import base64
import os
import time
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- CATEGORIES & ACCOUNTS ---
# Updated Bank accounts as per CA Audit Report
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

# --- USERS & ROLES ---
USERS = {
    "admin": {"password": "Japnik@3315", "role": "admin"},
    "staff": {"password": "12345", "role": "staff"},
    "management": {"password": "view@123", "role": "management"}
}

# --- SUPABASE ਕਨੈਕਸ਼ਨ ---
SUPABASE_URL = "https://jbvtvrhzzucggqhwjzuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ (Sabha Manager Pro)", page_icon="logo.png", layout="wide")

# ==========================================
# CUSTOM CSS (UI DESIGN & PROFESSIONAL HEADER)
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
        .pro-title { font-size: 28px; font-weight: bold; color: #4A1B15; margin: 0; letter-spacing: 0.5px; }
        .pro-tagline { font-size: 17px; font-weight: bold; color: #D92B2B; margin: 4px 0; }
        .pro-sub { font-size: 13px; font-weight: bold; color: #0F4C81; margin: 0; }

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
        
        .bs-box { border: 2px solid #1E3A8A; border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: rgba(30, 58, 138, 0.05); }
        .bs-header { text-align: center; color: #1E3A8A; font-size: 22px; font-weight: bold; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px; }
        .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; }
        .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #D92B2B; border-top: 1px solid #333; padding-top: 8px; margin-top: 10px; }
        
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

# --- SESSION STATE INITIALIZATION FOR TABS AND MODES ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if 'current_tab' not in st.session_state: st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
if 'entry_mode' not in st.session_state: st.session_state.entry_mode = "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"
if 'acc_mode' not in st.session_state: st.session_state.acc_mode = "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"
if 'other_mode' not in st.session_state: st.session_state.other_mode = "📦 ਸਟਾਕ (Inventory)"
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)"

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_login_path = "logo.png"
        if os.path.exists(logo_login_path):
            st.image(logo_login_path, width=100)
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #4A1B15; margin: 0; font-size: 24px;">{NGO_NAME_PB}</h2>
                <p style="color: #D92B2B; font-weight: bold; font-size: 16px; margin: 5px 0;">{NGO_TAGLINE_PB}</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = USERS[username_input]["role"]
                    st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
                    st.rerun()
                else: st.error("ਗਲਤ ਪਾਸਵਰਡ! (Incorrect Password!)")
    st.stop()

is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"
is_staff = st.session_state.role == "staff"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    role_display = "ਐਡਮਿਨ ਮੋਡ (Admin)" if is_admin else "ਮੈਨੇਜਮੈਂਟ (View Only)" if is_mgmt else "ਕਰਮਚਾਰੀ ਮੋਡ (Staff)"
    st.success(f"✅ {role_display}")
    
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()
    
    st.markdown("---")
    st.subheader("ਮੁੱਖ ਮੀਨੂ (Main Menu)")
    
    menu_options = [
        "🏠 ਹੋਮ ਪੇਜ (Home)",
        "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", 
        "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)",
        "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)"
    ]
    if is_admin or is_staff:
        menu_options.append("⚙️ ਐਡਮਿਨ ਅਤੇ ਬਲਕ ਅੱਪਲੋਡ (Admin & Bulk Upload)")
        
    st.radio("ਚੁਣੋ (Select)", menu_options, key="current_tab", label_visibility="collapsed")

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
if st.session_state.current_tab != "🏠 ਹੋਮ ਪੇਜ (Home)":
    if st.button("🏠 ਹੋਮ ਪੇਜ 'ਤੇ ਜਾਓ (Back to Home Dashboard)", type="secondary"):
        st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
        st.rerun()
    st.markdown("---")

# ==========================================
# 0. HOME PAGE DASHBOARD (SHORTCUT BUTTONS)
# ==========================================
if st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
    st.markdown("<p style='text-align: center; font-size: 20px; font-weight: bold; color: #1E3A8A; margin-bottom: 25px;'>ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਦਿੱਤੇ ਸੈਕਸ਼ਨਾਂ ਵਿੱਚੋਂ ਕੋਈ ਇੱਕ ਚੁਣੋ ਜੀ:</p>", unsafe_allow_html=True)

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
    c5, c6, c7, c8 = st.columns(4)
    if c5.button("⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (Balance Sheet)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"
        st.rerun()
    if c6.button("🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)"
        st.rerun()
    if c7.button("📁 ਪਾਰਟੀਆਂ/ਚੈੱਕ (Creditors)", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)"
        st.rerun()
    if c8.button("📊 CA ਆਡਿਟ ਐਕਸਲ ਬੈਕਅੱਪ", use_container_width=True):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)"
        st.session_state.acc_mode = "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"
        st.rerun()

    st.markdown("### 📦 ਸਟਾਕ, ਕਿਤਾਬਾਂ ਅਤੇ ਬਲਕ ਅੱਪਲੋਡ (Management)")
    c9, c10, c11, c12 = st.columns(4)
    if c9.button("📦 ਸਟਾਕ ਭੰਡਾਰ (Stock)", use_container_width=True):
        st.session_state.current_tab = "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)"
        st.session_state.other_mode = "📦 ਸਟਾਕ (Inventory)"
        st.rerun()
    if c10.button("📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Books)", use_container_width=True):
        st.session_state.current_tab = "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)"
        st.session_state.other_mode = "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"
        st.rerun()
    if (is_admin or is_staff) and c11.button("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ", use_container_width=True):
        st.session_state.current_tab = "⚙️ ਐਡਮਿਨ ਅਤੇ ਬਲਕ ਅੱਪਲੋਡ (Admin & Bulk Upload)"
        st.session_state.admin_mode = "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)"
        st.rerun()
    if is_admin and c12.button("🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ", use_container_width=True):
        st.session_state.current_tab = "⚙️ ਐਡਮਿਨ ਅਤੇ ਬਲਕ ਅੱਪਲੋਡ (Admin & Bulk Upload)"
        st.session_state.admin_mode = "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete Manager)"
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
    st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ ਚੁਣੋ (Select Action):", modes, key="entry_mode", horizontal=True)
    selected_mode = st.session_state.entry_mode
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
                        else:
                            st.info("ℹ️ ਦਾਨੀ ਦਾ ਫ਼ੋਨ ਨੰਬਰ ਨਾ ਹੋਣ ਕਾਰਨ WhatsApp ਲਿੰਕ ਨਹੀਂ ਬਣਿਆ।")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    elif selected_mode == "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)":
        if not is_mgmt:
            with st.form("inkind_form", clear_on_submit=True):
                st.write("### 📦 ਸਮਾਨ ਦਾ ਦਾਨ ਦਰਜ ਕਰੋ")
                donor_name_ik = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)", key="ik_name")
                donor_phone_ik = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional Phone)", key="ik_phone")
                item_details_ik = st.text_input("ਸਮਾਨ ਦਾ ਵੇਰਵਾ (Item Details - e.g. 50kg Wheat)", key="ik_item")
                rec_no_ik = st.number_input("ਰਸੀਦ ਨੰਬਰ (Printed Receipt No.)", min_value=1, step=1, key="ik_rec")
                col_k1, col_k2 = st.columns(2)
                with col_k1: amount_ik = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (Estimated Value ₹ - Optional)", min_value=0.0, key="ik_amt")
                with col_k2: receipt_date_ik = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), key="ik_date")
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
                if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ (Save Expense)", type="primary") and desc:
                    supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"), "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp}).execute()
                    st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ! (Expense Saved!)")
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
                    
                    c_p1, c_p2 = st.columns([1, 2])
                    with c_p1:
                        with open(html_file_rep, "r", encoding="utf-8") as file:
                            st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print)", data=file.read(), file_name=html_file_rep, mime="text/html", key="reprint_btn", type="primary")
                    with c_p2:
                        if rec.get('phone'):
                            amt_str = f"₹{rec.get('amount',0)}/- ਦਾ ਦਾਨ" if rec.get('donation_type') == "ਪੈਸੇ (Monetary)" else f"ਦਾਨ ਵਜੋਂ '{rec.get('item_details')}'"
                            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {rec.get('name')} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ {amt_str} (ਰਸੀਦ ਨੰ: {search_id}) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਧੰਨਵਾਦ ਜੀ।"
                            url = f"https://wa.me/{rec.get('phone')}?text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Resend via WhatsApp)</a>', unsafe_allow_html=True)
                else:
                    st.error("❌ ਇਸ ਨੰਬਰ ਦੀ ਕੋਈ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ।")
        with col_search2:
            search_donor = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਨਾਲ ਖੋਜ ਕਰੋ (Search by Donor Name)")
            if search_donor:
                df_don = pd.DataFrame(supabase.table("donations").select("*").execute().data or [])
                if not df_don.empty:
                    st.dataframe(df_don[df_don['name'].str.contains(search_donor, case=False, na=False)][['id', 'name', 'phone', 'amount', 'date', 'collector_name']], use_container_width=True)

# ==========================================
# 2. LEDGERS, BANK & CA REPORTS
# ==========================================
elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)":
    st.header("🏦 ਖਾਤੇ, ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    
    modes = [
        "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", 
        "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", 
        "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)", 
        "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"
    ]
    st.radio("ਖਾਤਾ ਚੁਣੋ:", modes, key="acc_mode", horizontal=True)
    selected_mode = st.session_state.acc_mode
    st.markdown("---")

    don_data = supabase.table("donations").select("*").execute().data or []
    exp_data = supabase.table("expenses").select("*").execute().data or []
    try:
        ledg_data = supabase.table("bank_ledger").select("*").execute().data or []
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
        
        fixed_assets_val = df_assets['value'].sum() if not df_assets.empty else 0.0
        bank_balances = {"ਨਕਦ (Cash)": 0.0, "Kotak Bank Regular": 0.0, "Kotak Bank Corpus Fund": 0.0, "Punjab & Sind Bank": 0.0}
        for bank in BANK_ACCOUNTS:
            b_in = df_don[(df_don['bank_account'] == bank) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don.get('add_to_mirror', False) == True)]['amount'].sum() if not df_don.empty else 0
            b_in += df_ledg[df_ledg['bank_name'] == bank]['credit'].sum() if not df_ledg.empty and 'bank_name' in df_ledg.columns and 'credit' in df_ledg.columns else 0
            b_out = df_exp[(df_exp['bank_account'] == bank) & (df_exp.get('add_to_mirror', False) == True)]['amount'].sum() if not df_exp.empty else 0
            b_out += df_ledg[df_ledg['bank_name'] == bank]['debit'].sum() if not df_ledg.empty and 'bank_name' in df_ledg.columns and 'debit' in df_ledg.columns else 0
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
            st.markdown(f'<div class="bs-row"><span>Fixed Assets (ਪੱਕੀ ਸੰਪਤੀ ਜਿਵੇਂ ਬਿਲਡਿੰਗ, ਫਰਨੀਚਰ):</span><span>₹ {fixed_assets_val:,.2f}</span></div>', unsafe_allow_html=True)
            for b, val in bank_balances.items(): st.markdown(f'<div class="bs-row"><span>{b}:</span><span>₹ {val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Assets:</span><span>₹ {total_assets:,.2f}</span></div></div>', unsafe_allow_html=True)
            
        full_html = f"<h3>Income & Expenditure Account</h3>{inc_exp_html}<br><h3>Balance Sheet</h3>"
        full_html += f"""<div style="width:100%;"><div class="bs-box"><h4>Liabilities</h4><p>Funds & Liab: {other_liab_val:,.2f}</p><p>Surplus: {surplus:,.2f}</p><hr><p><b>Total: {total_liabilities:,.2f}</b></p></div><div class="bs-box"><h4>Assets</h4><p>Fixed Assets: {fixed_assets_val:,.2f}</p><p>Bank/Cash: {sum(bank_balances.values()):,.2f}</p><hr><p><b>Total: {total_assets:,.2f}</b></p></div></div>"""
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
                    a_val = st.number_input("ਮੁੱਲ (Value ₹)", min_value=0.0)
                    if st.form_submit_button("ਸੰਪਤੀ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("assets").insert({"name": a_name, "value": a_val, "date_added": str(date.today())}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()
            with ac2:
                with st.form("add_liab"):
                    st.write("**Fund/Liability (ਫੰਡ ਜਾਂ ਉਧਾਰ ਜੋੜੋ)**")
                    l_name = st.text_input("ਫੰਡ ਦਾ ਨਾਮ (e.g. Corpus Fund, Loan)")
                    l_val = st.number_input("ਮੁੱਲ (Value ₹)", min_value=0.0)
                    if st.form_submit_button("ਫੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("liabilities").insert({"name": l_name, "value": l_val, "date_added": str(date.today())}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()

    elif selected_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ (Select Bank)", BANK_ACCOUNTS)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ (Start Date)", value=date(date.today().year, date.today().month, 1))
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ (End Date)", value=date.today())

        ledger_entries = []
        if not df_don.empty:
            df_don['add_to_mirror'] = df_don.get('add_to_mirror', False).fillna(False).astype(bool)
            for _, row in df_don[(df_don['bank_account'] == selected_bank) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don['add_to_mirror'] == True)].iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']}", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'App (Donation)'})
        if not df_exp.empty:
            df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', False).fillna(False).astype(bool)
            for _, row in df_exp[(df_exp['bank_account'] == selected_bank) & (df_exp['add_to_mirror'] == True)].iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'App (Expense)'})
        if not df_ledg.empty and 'bank_name' in df_ledg.columns:
            for _, row in df_ledg[df_ledg['bank_name'] == selected_bank].iterrows(): ledger_entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Credit': float(row.get('credit', 0)), 'Debit': float(row.get('debit', 0)), 'Source': row.get('source', 'Manual')})
                
        df_compiled = pd.DataFrame(ledger_entries)
        sys_bal = 0.0
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
            closing_bal = opening_bal + df_period['Credit'].sum() - df_period['Debit'].sum()
            sys_bal = df_compiled['Credit'].sum() - df_compiled['Debit'].sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ਓਪਨਿੰਗ ਬੈਲੇਂਸ (Opening)", f"₹ {opening_bal:,.2f}")
            m2.metric("ਕੁੱਲ ਜਮ੍ਹਾਂ (Total Credit)", f"₹ {df_period['Credit'].sum():,.2f}")
            m3.metric("ਕੁੱਲ ਖਰਚਾ (Total Debit)", f"₹ {df_period['Debit'].sum():,.2f}")
            m4.metric("ਕਲੋਜ਼ਿੰਗ ਬੈਲੇਂਸ (Closing)", f"₹ {closing_bal:,.2f}")
            st.dataframe(df_period[['ID', 'Date', 'Description', 'Source', 'Credit', 'Debit', 'Running Balance']].style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'Running Balance': '{:.2f}'}), use_container_width=True)
            
            report_file_bank = generate_html_report(f"Bank Statement - {selected_bank}", df_period[['Date', 'Description', 'Source', 'Credit', 'Debit', 'Running Balance']].to_html(index=False, border=1, classes='report-table'))
            with open(report_file_bank, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸਟੇਟਮੈਂਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_bank, mime="text/html")
        else: st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਹਾਲੇ ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਹੈ।")

        st.markdown("---")
        st.subheader("🖨️ ਬੈਂਕ ਐਂਟਰੀ ਤੋਂ ਰਸੀਦ ਬਣਾਓ ਅਤੇ WhatsApp ਭੇਜੋ")
        col_conv1, col_conv2 = st.columns(2)
        with col_conv1:
            ledger_id = st.number_input("ਬੈਂਕ ਲੈਜ਼ਰ ID ਭਰੋ (Bank Entry ID)", min_value=0, step=1)
            if st.button("🔍 ਬੈਂਕ ਐਂਟਰੀ ਲੱਭੋ (Find Bank Entry)", type="primary"):
                try:
                    res = supabase.table("bank_ledger").select("*").eq("id", ledger_id).execute()
                    if res.data and res.data[0]['credit'] > 0:
                        st.session_state['convert_ledger_id'] = ledger_id
                        st.session_state['convert_ledger_data'] = res.data[0]
                    else: st.error("❌ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ ਜਾਂ ਇਹ ਕ੍ਰੈਡਿਟ (Credit) ਐਂਟਰੀ ਨਹੀਂ ਹੈ।")
                except Exception: st.error("❌ ਬੈਂਕ ਲੈਜ਼ਰ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।")

        if 'convert_ledger_id' in st.session_state and st.session_state['convert_ledger_id'] == ledger_id:
            ldata = st.session_state['convert_ledger_data']
            with col_conv2:
                st.success(f"**ਐਂਟਰੀ:** {ldata['txn_date']} | ₹{ldata['credit']} | {ldata['description']}")
                with st.form("convert_bank_receipt"):
                    c_rec_no = st.number_input("ਰਸੀਦ ਨੰਬਰ (Printed Serial No.)", min_value=1, step=1)
                    c_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
                    c_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (WhatsApp Phone)")
                    c_acct = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of)")
                    submitted_conv = st.form_submit_button("ਇਸਦੀ ਰਸੀਦ ਬਣਾਓ (Generate Receipt)", type="primary")
                    
            if submitted_conv and c_name:
                books_c = supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                m_book = next((b for b in books_c if int(b['start_no']) <= int(c_rec_no) <= int(b['end_no'])), None)
                ex_rec = supabase.table("donations").select("*").eq("id", int(c_rec_no)).execute().data
                
                if not m_book: st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ {c_rec_no} ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif ex_rec: st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਵਰਤੀ ਜਾ ਚੁੱਕੀ ਹੈ!")
                else:
                    col_name = m_book['collector_name']
                    supabase.table("donations").insert({
                        "id": int(c_rec_no), "name": c_name, "phone": c_phone, "amount": ldata['credit'],
                        "date": ldata['txn_date'], "payment_mode": "Bank Transfer",
                        "donation_type": "ਪੈਸੇ (Monetary)", "bank_account": ldata['bank_name'],
                        "on_account_of": c_acct, "add_to_mirror": False, "collector_name": col_name
                    }).execute()
                    
                    h_file = generate_html_receipt(int(c_rec_no), c_name, c_phone, ldata['credit'], ldata['txn_date'], "Bank Transfer", "ਪੈਸੇ (Monetary)", "", ldata['bank_name'], c_acct, col_name)
                    st.success(f"✅ ਰਸੀਦ #{c_rec_no} ਤਿਆਰ ਹੈ! (ਕਲੈਕਟਰ: {col_name})")
                    
                    col_c1, col_c2 = st.columns([1, 2])
                    with col_c1:
                        with open(h_file, "r", encoding="utf-8") as file:
                            st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print)", data=file.read(), file_name=h_file, mime="text/html", key=f"dl_bk_{c_rec_no}", type="primary")
                    with col_c2:
                        if c_phone:
                            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ።\n\nਸਤਿਕਾਰਯੋਗ {c_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{ldata['credit']}/- ਦਾ ਦਾਨ (Bank Transfer ਰਾਹੀਂ, ਰਸੀਦ ਨੰ: {c_rec_no}) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                            url = f"https://wa.me/{c_phone}?text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)

        if not is_mgmt:
            st.markdown("---")
            st.subheader(f"➕ ਹੱਥੀਂ ਐਂਟਰੀ / ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ")
            t3_col1, t3_col2 = st.columns(2)
            with t3_col1:
                with st.form("manual_ledger"):
                    st.write("ਹੱਥੀਂ ਐਂਟਰੀ ਕਰੋ (Manual Entry)")
                    m_date = st.date_input("ਮਿਤੀ (Date)")
                    m_desc = st.text_input("ਵੇਰਵਾ (Description - e.g. Bank Interest)")
                    m_type = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ (Type)", ["ਕ੍ਰੈਡਿਟ / ਆਏ (Credit)", "ਡੈਬਿਟ / ਕੱਟੇ (Debit)"])
                    m_amt = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
                    if st.form_submit_button("ਐਂਟਰੀ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("bank_ledger").insert({"bank_name": selected_bank, "txn_date": m_date.strftime("%Y-%m-%d"), "description": m_desc, "credit": m_amt if "Credit" in m_type else 0.0, "debit": m_amt if "Debit" in m_type else 0.0, "source": "Manual"}).execute()
                        st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!"); time.sleep(1); st.rerun()
            with t3_col2:
                st.write("ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ (Upload Statement Excel)")
                stmt_file = st.file_uploader(f"Upload {selected_bank} Statement", type=['xlsx', 'xls'], key="bank_stmt")
                if stmt_file:
                    df_stmt = pd.read_excel(stmt_file)
                    df_stmt.columns = df_stmt.columns.str.lower()
                    if 'balance' not in df_stmt.columns: st.error("ਐਕਸਲ ਵਿੱਚ 'Balance' ਕਾਲਮ ਨਹੀਂ ਹੈ!")
                    elif st.button("ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ", type="primary"):
                        ledg_records = [{"bank_name": selected_bank, "txn_date": str(row['date'])[:10], "description": str(row['description']), "credit": float(row.get('credit',0)), "debit": float(row.get('debit',0)), "balance": float(row.get('balance',0)), "source": "Statement Upload"} for _, row in df_stmt.iterrows() if pd.notna(row.get('date')) and pd.notna(row.get('description'))]
                        if ledg_records:
                            supabase.table("bank_ledger").insert(ledg_records).execute()
                            st.success("✅ ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਹੋ ਗਈ!"); time.sleep(1); st.rerun()

    elif selected_mode == "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)":
        st.write("### 📁 ਸਾਰੀਆਂ ਪਾਰਟੀਆਂ ਦੀ ਸੂਚੀ (Creditors & Debtors)")
        try: parties_data = supabase.table("parties").select("*").execute().data or []
        except Exception: parties_data = []
        if parties_data: st.dataframe(pd.DataFrame(parties_data)[['id', 'name', 'party_type', 'phone', 'address', 'opening_balance']], use_container_width=True)
        else: st.info("ਹਾਲੇ ਕੋਈ ਪਾਰਟੀ ਦਰਜ ਨਹੀਂ ਹੈ।")
        
        st.write("### 💳 ਸਾਰੇ ਚੈੱਕਾਂ ਦਾ ਰਿਕਾਰਡ (Cheques History)")
        try: cq_data = supabase.table("cheques").select("*").execute().data or []
        except Exception: cq_data = []
        if cq_data: st.dataframe(pd.DataFrame(cq_data)[['id', 'cheque_no', 'bank_name', 'party_name', 'amount', 'cheque_date', 'status']], use_container_width=True)
        else: st.info("ਹਾਲੇ ਕੋਈ ਚੈੱਕ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

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
                pd.DataFrame(supabase.table("receipt_books").select("*").execute().data or []).to_excel(writer, sheet_name='Receipt_Books', index=False)
            st.download_button("📥 ਕਲਿੱਕ ਕਰਕੇ ਡਾਊਨਲੋਡ ਕਰੋ", data=buffer.getvalue(), file_name=f"CA_Audit_Data_{datetime.now().strftime('%d-%m-%Y')}.xlsx", type="primary")

# ==========================================
# 3. STOCK & RECEIPT BOOKS
# ==========================================
elif st.session_state.current_tab == "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)":
    st.header("📦 ਸਟਾਕ, ਵਿਦਿਆਰਥੀ ਅਤੇ ਰਸੀਦ ਕਿਤਾਬਾਂ")
    modes = ["📦 ਸਟਾਕ (Inventory)", "🎓 ਵਿਦਿਆਰਥੀ (Students)", "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"]
    st.radio("ਸੈਕਸ਼ਨ ਚੁਣੋ:", modes, key="other_mode", horizontal=True)
    selected_mode = st.session_state.other_mode
    st.markdown("---")

    if selected_mode == "📦 ਸਟਾਕ (Inventory)":
        col1, col2 = st.columns([1, 2])
        with col1:
            if not is_mgmt:
                with st.form("stock_form", clear_on_submit=True):
                    st.write("### 📦 ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ")
                    item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ (Item Name)")
                    qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=0.0, step=0.5)
                    unit = st.selectbox("ਇਕਾਈ (Unit)", ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)"])
                    stock_action = st.radio("ਐਕਸ਼ਨ (Action)", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add Stock)", "ਸਮਾਨ ਵਰਤਿਆ (Remove Stock)"])
                    if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ", type="primary") and item_name:
                        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        res = supabase.table("stock").select("*").eq("item_name", item_name).execute()
                        if res.data: supabase.table("stock").update({"quantity": res.data[0]['quantity'] + qty if "Add" in stock_action else max(0, res.data[0]['quantity'] - qty), "last_updated": current_date}).eq("item_name", item_name).execute()
                        else: supabase.table("stock").insert({"item_name": item_name, "quantity": qty if "Add" in stock_action else 0, "unit": unit, "last_updated": current_date}).execute()
                        st.success(f"✅ ਸਟਾਕ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ!")
        with col2:
            st.write("### 📑 ਮੌਜੂਦਾ ਸਟਾਕ ਰਿਪੋਰਟ")
            stock_res = supabase.table("stock").select("*").gt("quantity", 0).execute()
            if stock_res.data: st.dataframe(pd.DataFrame(stock_res.data)[['item_name', 'quantity', 'unit', 'last_updated']], use_container_width=True)

    elif selected_mode == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
        col1, col2 = st.columns([1, 2])
        with col1:
            if not is_mgmt:
                with st.form("student_form", clear_on_submit=True):
                    st.write("### 🎓 ਨਵਾਂ ਵਿਦਿਆਰਥੀ")
                    stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ")
                    stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                    stu_course = st.selectbox("ਕਲਾਸ", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"])
                    join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ", value=date.today())
                    if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ", type="primary") and stu_name:
                        supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ"}).execute()
                        st.success("✅ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
        with col2:
            st.write("### 📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ")
            student_data = supabase.table("students").select("*").execute().data or []
            if student_data: st.dataframe(pd.DataFrame(student_data)[['name', 'phone', 'course', 'join_date']], use_container_width=True)

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
        books_all = supabase.table("receipt_books").select("*").execute().data or []
        if books_all: st.dataframe(pd.DataFrame(books_all)[['collector_name', 'start_no', 'end_no', 'issued_date', 'status']], use_container_width=True)

# ==========================================
# 4. ADMIN & BULK UPLOAD MANAGEMENT
# ==========================================
elif st.session_state.current_tab == "⚙️ ਐਡਮਿਨ ਅਤੇ ਬਲਕ ਅੱਪਲੋਡ (Admin & Bulk Upload)":
    st.header("⚙️ ਐਡਮਿਨ, ਬਲਕ ਅੱਪਲੋਡ ਅਤੇ ਡਿਲੀਟ ਸਿਸਟਮ")
    modes = ["📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)", "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete Manager)"]
    st.radio("ਐਡਮਿਨ ਟੂਲ ਚੁਣੋ:", modes, key="admin_mode", horizontal=True)
    selected_mode = st.session_state.admin_mode
    st.markdown("---")

    if selected_mode == "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)":
        st.write("### 📂 ਪੁਰਾਣਾ ਡਾਟਾ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ (Upload Old Donations via Excel)")
        st.info("ਐਕਸਲ ਸ਼ੀਟ ਰਾਹੀਂ ਦਾਨ ਦਾ ਵੱਡਾ ਰਿਕਾਰਡ ਇੱਕੋ ਕਲਿੱਕ ਵਿੱਚ Supabase ਡਾਟਾਬੇਸ ਵਿੱਚ ਅੱਪਲੋਡ ਕਰੋ।")
        uploaded_file = st.file_uploader("ਦਾਨ ਦੀ ਐਕਸਲ ਫਾਈਲ ਚੁਣੋ (.xlsx, .xls)", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            df_upload.columns = df_upload.columns.str.lower()
            st.dataframe(df_upload.head(10), use_container_width=True)
            if 'add_to_mirror' not in df_upload.columns: df_upload['add_to_mirror'] = True
            if st.button("🚀 ਸਾਰਾ ਡਾਟਾ ਸੇਵ ਕਰੋ (Upload All Records)", type="primary"):
                if 'balance' in df_upload.columns: df_upload['balance'] = df_upload['balance'].fillna(0)
                df_upload['add_to_mirror'] = df_upload['add_to_mirror'].fillna(True).astype(bool)
                supabase.table("donations").insert(df_upload.to_dict(orient='records')).execute()
                st.success("✅ ਸਾਰਾ ਡਾਟਾ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਲੋਡ ਹੋ ਗਿਆ ਹੈ!")

    elif selected_mode == "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete Manager)":
        t_map = {"ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", "ਪਾਰਟੀ (Party)": "parties", "ਚੈੱਕ (Cheque)": "cheques", "ਸੰਪਤੀ (Asset)": "assets", "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", "ਵਿਦਿਆਰਥੀ (Student)": "students", "ਰਸੀਦ ਕਿਤਾਬ (Receipt Book)": "receipt_books"}
        if is_admin:
            st.subheader("🔔 ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਬੇਨਤੀਆਂ (Pending Requests from Staff)")
            reqs = supabase.table("deletion_requests").select("*").eq("status", "Pending").execute().data
            if reqs:
                st.dataframe(pd.DataFrame(reqs)[['id', 'table_name', 'record_id', 'details', 'created_at']], use_container_width=True)
                with st.form("approve_reject_form"):
                    req_id = st.number_input("ਬੇਨਤੀ ID ਭਰੋ", min_value=0, step=1)
                    action = st.radio("ਐਕਸ਼ਨ", ["✅ ਮਨਜ਼ੂਰ (Approve & Delete)", "❌ ਰੱਦ ਕਰੋ (Reject)"])
                    if st.form_submit_button("ਲਾਗੂ ਕਰੋ", type="primary") and req_id > 0:
                        target_req = next((r for r in reqs if int(r['id']) == req_id), None)
                        if target_req:
                            if "Approve" in action:
                                try:
                                    if target_req['table_name'] == "stock": supabase.table(target_req['table_name']).delete().eq("item_name", str(target_req['record_id'])).execute()
                                    else: supabase.table(target_req['table_name']).delete().eq("id", int(float(target_req['record_id']))).execute()
                                    supabase.table("deletion_requests").update({"status": "Approved"}).eq("id", req_id).execute()
                                    st.success("✅ ਐਂਟਰੀ ਡਿਲੀਟ ਹੋ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                                except Exception as e: st.error(f"Error: {e}")
                            else:
                                supabase.table("deletion_requests").update({"status": "Rejected"}).eq("id", req_id).execute()
                                st.success("❌ ਬੇਨਤੀ ਰੱਦ ਕੀਤੀ ਗਈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਇਸ ਸਮੇਂ ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")
            st.markdown("---")
            st.subheader("⚡ ਸਿੱਧਾ ਡਿਲੀਟ ਕਰੋ (Direct Admin Delete)")
            
        if is_staff: st.info("⚠️ ਸਟਾਫ ਸਿੱਧਾ ਡਿਲੀਟ ਨਹੀਂ ਕਰ ਸਕਦਾ। ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਕੋਲ ਮਨਜ਼ੂਰੀ ਲਈ ਜਾਵੇਗੀ।")
            
        del_type = st.selectbox("ਕੀ ਡਿਲੀਟ ਕਰਨਾ ਹੈ? (Select Category)", list(t_map.keys()))
        if del_type == "ਸਟਾਕ (Stock)":
            del_item = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ ਭਰੋ (Enter Item Name)")
            if st.button("🔍 ਲੱਭੋ", type="primary"):
                res = supabase.table("stock").select("*").eq("item_name", del_item).execute()
                if res.data: st.session_state['del_entry_data'] = res.data[0]; st.session_state['del_entry_id'] = del_item; st.session_state['del_entry_type'] = del_type
                else: st.error("❌ ਨਹੀਂ ਮਿਲੀ।")
        else:
            del_id = st.number_input("ਐਂਟਰੀ ਦਾ ID ਭਰੋ (Entry ID)", min_value=0, step=1)
            if st.button("🔍 ਲੱਭੋ", type="primary"):
                try:
                    res = supabase.table(t_map[del_type]).select("*").eq("id", del_id).execute()
                    if res.data: st.session_state['del_entry_data'] = res.data[0]; st.session_state['del_entry_id'] = str(del_id); st.session_state['del_entry_type'] = del_type
                    else: st.error("❌ ਨਹੀਂ ਮਿਲੀ।")
                except Exception: st.error("❌ ਟੇਬਲ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।")
                
        if 'del_entry_data' in st.session_state and st.session_state.get('del_entry_type') == del_type:
            data = st.session_state['del_entry_data']
            record_id = st.session_state['del_entry_id']
            st.info(f"ਵੇਰਵਾ: {data}")
            if is_admin:
                if st.button("🛑 ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ", type="primary"):
                    try:
                        if del_type == "ਸਟਾਕ (Stock)": supabase.table(t_map[del_type]).delete().eq("item_name", record_id).execute()
                        else: supabase.table(t_map[del_type]).delete().eq("id", int(float(record_id))).execute()
                        st.success("✅ ਡਿਲੀਟ ਹੋ ਗਿਆ!"); st.session_state.pop('del_entry_data', None); time.sleep(1.5); st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
            elif is_staff:
                if st.button("📩 ਐਡਮਿਨ ਨੂੰ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ", type="primary"):
                    supabase.table("deletion_requests").insert({"table_name": t_map[del_type], "record_id": str(record_id), "details": str(data), "requested_by": "staff"}).execute()
                    st.success("✅ ਤੁਹਾਡੀ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); st.session_state.pop('del_entry_data', None); time.sleep(1.5); st.rerun()
