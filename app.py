import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import io
import base64
import os
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- CATEGORIES & ACCOUNTS ---
BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank", "Punjab & Sind Bank"]
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
# CUSTOM CSS (UI DESIGN & HIDING GITHUB ICON)
# ==========================================
st.markdown("""
    <style>
        /* Hide Streamlit Deploy/GitHub Menu */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display:none !important;}

        /* Sidebar Menu Font Size */
        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
        
        /* All Input Labels */
        div[data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 600 !important; }
        h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
        h3 { font-size: 20px !important; font-weight: 600 !important; }
        
        /* Metric text size */
        [data-testid="stMetricLabel"] p { font-size: 16px !important; font-weight: bold !important; }
        [data-testid="stMetricValue"] { font-size: 26px !important; }
        [data-testid="stBaseButton-primary"] { font-size: 16px !important; font-weight: bold !important; padding: 5px 20px !important; }
        
        /* Balance Sheet specific styles */
        .bs-box { border: 2px solid #1E3A8A; border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: rgba(30, 58, 138, 0.05); }
        .bs-header { text-align: center; color: #1E3A8A; font-size: 22px; font-weight: bold; border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px; }
        .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; }
        .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #D92B2B; border-top: 1px solid #333; padding-top: 8px; margin-top: 10px; }
        
        /* Custom WhatsApp Button Style */
        .whatsapp-btn {
            display: inline-block;
            padding: 8px 16px;
            background-color: #25D366;
            color: white !important;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 6px;
            font-weight: bold;
            margin-top: 5px;
            border: 1px solid #128C7E;
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; color: #333; background-color: #fff; }}
        .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #4A1B15; padding-bottom: 15px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #4A1B15; margin-bottom: 5px; }}
        .report-title {{ font-size: 18px; font-weight: bold; color: #D92B2B; margin-top: 10px; }}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; text-align: left; }}
        .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 8px; color: #000; }}
        .report-table th {{ background-color: #F8F1D1; color: #4A1B15; font-weight: bold; }}
        .bs-box {{ width: 48%; display: inline-block; vertical-align: top; border: 1px solid #333; padding: 10px; box-sizing: border-box; }}
        @media print {{ body {{ padding: 0; }} }}
    </style></head>
    <body>
        <div class="header">{img_html}<div class="title">{NGO_NAME_PB}</div><div>{NGO_ADDRESS_PB}</div><div class="report-title">{title}</div></div>
        {content_html}
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Report_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, don_type, item_details, bank_acc, on_account_of):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Logo">' if logo_base64 else ''
    amount_text = f"Rs. {amount}/-" if don_type == "ਪੈਸੇ (Monetary)" else f"ਕੀਮਤ: Rs. {amount}/-" if amount > 0 else f"{item_details}"
    amount_in_words = f"Rupees {amount} Only" if don_type == "ਪੈਸੇ (Monetary)" else f"{item_details} (In-Kind Donation)"
    display_phone = phone if phone else "________________"
    
    html_content = f"""
    <!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #fff; padding: 20px; }}
            .receipt-box {{ max-width: 850px; margin: auto; padding: 20px 30px; background-color: #F8F1D1; border-top: 25px solid #4A1B15; border-bottom: 25px solid #4A1B15; color: #333; position: relative; box-sizing: border-box; }}
            .header-flex {{ display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 5px; }}
            .logo-img {{ position: absolute; left: 0; top: 0; width: 100px; height: auto; }}
            .header-text {{ text-align: center; width: 100%; padding-left: 110px; box-sizing: border-box; }}
            .title-pa {{ font-size: 28px; font-weight: bold; color: #4A1B15; margin: 0; letter-spacing: 0.5px; }}
            .title-en {{ font-size: 18px; font-weight: bold; color: #4A1B15; margin: 5px 0 8px 0; }}
            .sub-title-pa {{ font-size: 15px; color: #D92B2B; font-weight: bold; margin: 2px 0; }}
            .sub-title-en {{ font-size: 13px; font-weight: bold; color: #0F4C81; margin: 4px 0; }}
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
            <div class="header-flex">{img_html}<div class="header-text"><p class="title-pa">ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)</p><p class="title-en">Shabad Kirtan Nam Simran Satsang (Regd.)</p><p class="sub-title-pa">ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ) ਰਾਧਾ ਕ੍ਰਿਸ਼ਨ ਕਲੋਨੀ (ਮੂਲੇ ਚੱਕ), ਨੇੜੇ ਭਗਤਾਂ ਵਾਲਾ ਦਾਣਾ ਮੰਡੀ, ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ</p><p class="sub-title-en">Regd. Office: C. B. Tower, Opp. Side Alpha One Mall, G. T. Road, Sri Amritsar Sahib - 143001</p><p class="phones">(M) 099150-07697, 78953-33290, 98157-55883</p></div></div>
            <div class="reg-row"><div>Regd. No.: ASR/26/2024-25 &nbsp;|&nbsp; PAN NO. ABKTS7853G</div><div>On Account of: <span class="field-value" style="font-size:14px;">{on_account_of}</span></div></div>
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

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=150)
        st.markdown(f"<h2 style='text-align: center;'>{NGO_NAME_PB}</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = USERS[username_input]["role"]
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
        "💸 ਦਾਨ (Donations)", 
        "📉 ਖਰਚੇ (Expenses)", 
        "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Ledger)",
        "⚖️ ਖਾਤੇ (P&L & Balance Sheet)", 
        "📦 ਸਟਾਕ (Stock)", 
        "🎓 ਵਿਦਿਆਰਥੀ (Students)",
        "📊 ਐਕਸਲ ਰਿਪੋਰਟਾਂ (Excel Reports)"
    ]
    if is_admin or is_staff:
        menu_options.append("🗑️ ਡਿਲੀਟ (Delete)")
    if is_admin:
        menu_options.append("⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Tools)")
        
    selected_tab = st.radio("ਚੁਣੋ (Select)", menu_options, label_visibility="collapsed")

colA, colB = st.columns([1, 8])
with colA:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
with colB: st.title(f"{NGO_NAME_PB}")
st.markdown("---")

# ==========================================
# 1. DONATIONS
# ==========================================
if selected_tab == "💸 ਦਾਨ (Donations)":
    st.header("ਦਾਨ ਪ੍ਰਬੰਧਨ (Donation Management)")
    
    tab_mon, tab_kind = st.tabs(["💰 ਨਕਦ / ਬੈਂਕ (Monetary)", "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind / Non-Monetary)"])
    
    with tab_mon:
        if not is_mgmt:
            st.subheader("ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ (Enter Monetary Donation)")
            with st.form("donation_form", clear_on_submit=True):
                donor_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
                donor_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number - Optional)")
                on_account_of = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of - e.g. Monthly Donation)")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
                    pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Payment Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Cheque", "NEFT/RTGS"])
                with col_m2:
                    bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ? (Select Bank)", BANK_ACCOUNTS)
                    receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ (Receipt Date)", value=date.today())
                    
                st.markdown("---")
                # DEFAULT FALSE FOR DONATION MIRROR LEDGER
                add_to_mirror = st.checkbox("✅ ਇਸ ਐਂਟਰੀ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਜੋੜੋ (Add to Bank Mirror Ledger)", value=False)
                submitted = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ (Save & Generate Receipt)", type="primary")
                
            if submitted and donor_name:
                formatted_date = receipt_date.strftime("%Y-%m-%d")
                data, _ = supabase.table("donations").insert({
                    "name": donor_name, "phone": donor_phone, "amount": amount, 
                    "date": formatted_date, "payment_mode": pay_mode, "donation_type": "ਪੈਸੇ (Monetary)", 
                    "item_details": "", "bank_account": bank_acc, "on_account_of": on_account_of, "add_to_mirror": add_to_mirror
                }).execute()
                
                receipt_id = data[1][0]['id']
                html_file = generate_html_receipt(receipt_id, donor_name, donor_phone, amount, formatted_date, pay_mode, "ਪੈਸੇ (Monetary)", "", bank_acc, on_account_of)
                st.success(f"✅ ਰਸੀਦ #{receipt_id} ਤਿਆਰ ਹੈ।")
                
                col_d1, col_d2 = st.columns([1, 3])
                with col_d1:
                    with open(html_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ (Print)", data=file.read(), file_name=html_file, mime="text/html")
                with col_d2:
                    if donor_phone:
                        msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{amount}/- ਦਾ ਦਾਨ ({pay_mode} ਰਾਹੀਂ) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                        url = f"https://wa.me/{donor_phone}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ। (View Only)")

    with tab_kind:
        if not is_mgmt:
            st.subheader("ਸਮਾਨ ਦਾ ਦਾਨ ਦਰਜ ਕਰੋ (Enter In-Kind Donation)")
            with st.form("inkind_form", clear_on_submit=True):
                donor_name_ik = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)", key="ik_name")
                donor_phone_ik = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number - Optional)", key="ik_phone")
                item_details_ik = st.text_input("ਦਾਨ ਕੀਤੇ ਸਮਾਨ ਦਾ ਵੇਰਵਾ (Item Details - e.g. 50kg Wheat)", key="ik_item")
                
                col_k1, col_k2 = st.columns(2)
                with col_k1: amount_ik = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (Estimated Value ₹ - Optional)", min_value=0.0, key="ik_amt")
                with col_k2: receipt_date_ik = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ (Receipt Date)", value=date.today(), key="ik_date")
                
                submitted_ik = st.form_submit_button("ਸਮਾਨ ਦੀ ਰਸੀਦ ਬਣਾਓ (Generate In-Kind Receipt)", type="primary")
                
            if submitted_ik and donor_name_ik and item_details_ik:
                formatted_date_ik = receipt_date_ik.strftime("%Y-%m-%d")
                data_ik, _ = supabase.table("donations").insert({
                    "name": donor_name_ik, "phone": donor_phone_ik, "amount": amount_ik, 
                    "date": formatted_date_ik, "payment_mode": "N/A", "donation_type": "ਸਮਾਨ (In-Kind / Ration)", 
                    "item_details": item_details_ik, "bank_account": "N/A", "on_account_of": "ਸਮਾਨ ਦਾਨ", "add_to_mirror": False
                }).execute()
                
                receipt_id_ik = data_ik[1][0]['id']
                html_file_ik = generate_html_receipt(receipt_id_ik, donor_name_ik, donor_phone_ik, amount_ik, formatted_date_ik, "N/A", "ਸਮਾਨ (In-Kind / Ration)", item_details_ik, "N/A", "ਸਮਾਨ ਦਾਨ")
                st.success(f"✅ ਰਸੀਦ #{receipt_id_ik} ਤਿਆਰ ਹੈ।")
                
                col_d1, col_d2 = st.columns([1, 3])
                with col_d1:
                    with open(html_file_ik, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ (Print)", data=file.read(), file_name=html_file_ik, mime="text/html", key="ik_dl")
                with col_d2:
                    if donor_phone_ik:
                        msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name_ik} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ਦਾਨ ਵਜੋਂ '{item_details_ik}' ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                        url = f"https://wa.me/{donor_phone_ik}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    st.markdown("---")
    st.subheader("🔍 ਦਾਨ ਰਿਕਾਰਡ ਖੋਜੋ (Search Donations)")
    don_search_col1, don_search_col2 = st.columns(2)
    with don_search_col1: search_donor_name = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਦੁਆਰਾ ਖੋਜ ਕਰੋ (Search by Name)")
    with don_search_col2: search_don_date = st.date_input("ਮਿਤੀ ਦੁਆਰਾ ਖੋਜ ਕਰੋ (Search by Date)", value=None)

    all_donations = supabase.table("donations").select("*").execute().data
    if all_donations:
        df_donations = pd.DataFrame(all_donations)
        if search_donor_name: df_donations = df_donations[df_donations['name'].str.contains(search_donor_name, case=False, na=False)]
        if search_don_date: df_donations = df_donations[df_donations['date'].str.startswith(search_don_date.strftime("%Y-%m-%d"))]
        st.dataframe(df_donations[['id', 'name', 'phone', 'donation_type', 'amount', 'item_details', 'date']], use_container_width=True)

    st.markdown("---")
    st.subheader("🖨️ ਪੁਰਾਣੀ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ (Reprint Old Receipt)")
    search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ ਭਰੋ (Enter Receipt No.)", min_value=1, step=1)
    if st.button("🔍 ਰਸੀਦ ਲੱਭੋ (Find Receipt)", type="primary"):
        res = supabase.table("donations").select("*").eq("id", search_id).execute()
        if res.data:
            record = res.data[0]
            html_file_rep = generate_html_receipt(search_id, record.get('name',''), record.get('phone',''), record.get('amount',0), record.get('date',''), record.get('payment_mode','N/A'), record.get('donation_type','ਪੈਸੇ (Monetary)'), record.get('item_details',''), record.get('bank_account','N/A'), record.get('on_account_of',''))
            st.success(f"✅ ਰਸੀਦ #{search_id} ਮਿਲ ਗਈ ਹੈ ({record.get('name', '')})!")
            
            col_r1, col_r2 = st.columns([1, 3])
            with col_r1:
                with open(html_file_rep, "r", encoding="utf-8") as file: st.download_button(label="🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Reprint)", data=file.read(), file_name=html_file_rep, mime="text/html", key="reprint_btn")
            with col_r2:
                if record.get('phone', ''):
                    amt_text = f"₹{record['amount']}/- ਦਾ ਦਾਨ" if record.get('donation_type') == "ਪੈਸੇ (Monetary)" else f"ਦਾਨ ਵਜੋਂ '{record.get('item_details')}'"
                    msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {record['name']} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ {amt_text} ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਧੰਨਵਾਦ ਜੀ।"
                    url = f"https://wa.me/{record['phone']}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Resend via WhatsApp)</a>', unsafe_allow_html=True)
        else: st.error("❌ ਇਸ ਨੰਬਰ ਦੀ ਕੋਈ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ।")

# ==========================================
# 2. EXPENSES
# ==========================================
elif selected_tab == "📉 ਖਰਚੇ (Expenses)":
    st.header("ਖਰਚਾ ਦਰਜ ਕਰੋ (Enter Expense)")
    if not is_mgmt:
        with st.form("expense_form", clear_on_submit=True):
            desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Expense Description)")
            cat = st.selectbox("ਕੈਟਾਗਰੀ (Category / Sub-head)", [c for c in EXPENSE_CATEGORIES if not c.startswith("---")])
            exp_amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
            bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ? (From which Bank?)", BANK_ACCOUNTS)
            exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ (Date)", value=date.today())
            st.markdown("---")
            # DEFAULT FALSE FOR EXPENSE MIRROR LEDGER
            add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਦਿਖਾਓ (Add to Bank Mirror Ledger)", value=False)
            if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ (Save Expense)", type="primary") and desc:
                supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"), "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp}).execute()
                st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ! (Expense Saved!)")
    else:
        st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    st.markdown("---")
    st.subheader("📑 ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ (Expenditure Report)")
    exp_data_all = supabase.table("expenses").select("*").execute().data or []
    if exp_data_all:
        df_exp_view = pd.DataFrame(exp_data_all)[['id', 'date', 'description', 'category', 'amount', 'bank_account']].sort_values(by='date', ascending=False)
        st.dataframe(df_exp_view, use_container_width=True)
        report_file_exp = generate_html_report("Expenditure Report (ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ)", df_exp_view.to_html(index=False, border=1, classes='report-table'))
        with open(report_file_exp, "r", encoding="utf-8") as file: st.download_button("🖨️ ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Expense Report)", data=file.read(), file_name=report_file_exp, mime="text/html")

# ==========================================
# 3. BANK LEDGER
# ==========================================
elif selected_tab == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Ledger)":
    st.header("ਮਿਰਰ ਬੈਂਕ ਖਾਤੇ (Full Mirror Ledger)")
    don_data = supabase.table("donations").select("*").execute().data or []
    exp_data = supabase.table("expenses").select("*").execute().data or []
    ledger_data = supabase.table("bank_ledger").select("*").execute().data or []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledger_data)
    
    selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ (Select Bank)", BANK_ACCOUNTS)
    col_d1, col_d2 = st.columns(2)
    with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ (Start Date)", value=date(date.today().year, date.today().month, 1))
    with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ (End Date)", value=date.today())

    ledger_entries = []
    if not df_don.empty:
        df_don['add_to_mirror'] = df_don.get('add_to_mirror', True).fillna(True).astype(bool)
        bank_dons = df_don[(df_don['bank_account'] == selected_bank) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don['add_to_mirror'] == True)]
        for _, row in bank_dons.iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']}", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'App (Donation)'})
    if not df_exp.empty:
        df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', True).fillna(True).astype(bool)
        bank_exps = df_exp[(df_exp['bank_account'] == selected_bank) & (df_exp['add_to_mirror'] == True)]
        for _, row in bank_exps.iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'App (Expense)'})
    if not df_ledg.empty:
        bank_ledg = df_ledg[df_ledg['bank_name'] == selected_bank]
        for _, row in bank_ledg.iterrows(): ledger_entries.append({'ID': row['id'], 'Date': row['txn_date'], 'Description': row['description'], 'Credit': float(row['credit']), 'Debit': float(row['debit']), 'Source': row['source']})
            
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

    st.markdown("### ⚖️ ਬੈਂਕ ਮਿਲਾਨ (Reconciliation Tally)")
    col_bal1, col_bal2, col_bal3 = st.columns(3)
    col_bal1.metric(f"ਅੱਜ ਤੱਕ ਦਾ ਕੁੱਲ ਸਿਸਟਮ ਬੈਲੇਂਸ", f"₹ {sys_bal:,.2f}")
    actual_bal = col_bal2.number_input("ਬੈਂਕ ਦਾ ਅਸਲ ਬੈਲੇਂਸ (Actual Bank Balance)", value=float(sys_bal), step=100.0)
    
    if (actual_bal - sys_bal) == 0: col_bal3.success("✅ ਖਾਤਾ ਮਿਲ ਗਿਆ (Tally Matched)")
    else: col_bal3.error(f"⚠️ ਫਰਕ (Mismatch): ₹ {(actual_bal - sys_bal):,.2f}")

    if not is_mgmt:
        st.markdown("---")
        st.subheader(f"➕ ਹੋਰ ਐਂਟਰੀਆਂ / ਮਿਲਾਨ (Entries & Reconciliation)")
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
                    st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!"); st.rerun()
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
                        st.success("✅ ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਹੋ ਗਈ!"); st.rerun()

        st.markdown("---")
        st.subheader("🖨️ ਬੈਂਕ ਐਂਟਰੀ ਤੋਂ ਰਸੀਦ ਬਣਾਓ (Convert Bank Credit to Receipt)")
        col_conv1, col_conv2 = st.columns(2)
        with col_conv1:
            ledger_id = st.number_input("ਬੈਂਕ ਲੈਜ਼ਰ ID ਭਰੋ (Bank Entry ID)", min_value=0, step=1)
            if st.button("🔍 ਬੈਂਕ ਐਂਟਰੀ ਲੱਭੋ (Find Bank Entry)", type="primary"):
                res = supabase.table("bank_ledger").select("*").eq("id", ledger_id).execute()
                if res.data and res.data[0]['credit'] > 0:
                    st.session_state['convert_ledger_id'] = ledger_id
                    st.session_state['convert_ledger_data'] = res.data[0]
                else:
                    st.error("❌ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ ਜਾਂ ਇਹ ਕ੍ਰੈਡਿਟ (Credit) ਐਂਟਰੀ ਨਹੀਂ ਹੈ।")

        if 'convert_ledger_id' in st.session_state and st.session_state['convert_ledger_id'] == ledger_id:
            ldata = st.session_state['convert_ledger_data']
            with col_conv2:
                st.success(f"**ਐਂਟਰੀ ਮਿਲ ਗਈ:**\nਮਿਤੀ: {ldata['txn_date']}\nਰਕਮ: ₹{ldata['credit']}\nਵੇਰਵਾ: {ldata['description']}")
                with st.form("convert_bank_receipt"):
                    c_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
                    c_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional Phone)")
                    c_acct = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of)")
                    submitted_conv = st.form_submit_button("ਇਸਦੀ ਰਸੀਦ ਬਣਾਓ (Generate Receipt)", type="primary")
                    
            if submitted_conv and c_name:
                data_conv, _ = supabase.table("donations").insert({
                    "name": c_name, "phone": c_phone, "amount": ldata['credit'],
                    "date": ldata['txn_date'], "payment_mode": "Bank Transfer",
                    "donation_type": "ਪੈਸੇ (Monetary)", "bank_account": ldata['bank_name'],
                    "on_account_of": c_acct, "add_to_mirror": False
                }).execute()
                
                rec_id = data_conv[1][0]['id']
                h_file = generate_html_receipt(rec_id, c_name, c_phone, ldata['credit'], ldata['txn_date'], "Bank Transfer", "ਪੈਸੇ (Monetary)", "", ldata['bank_name'], c_acct)
                st.success(f"✅ ਰਸੀਦ #{rec_id} ਤਿਆਰ ਹੈ!")
                
                col_c1, col_c2 = st.columns([1, 3])
                with col_c1:
                    with open(h_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print)", data=file.read(), file_name=h_file, mime="text/html", key=f"dl_bk_{rec_id}")
                with col_c2:
                    if c_phone:
                        msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {c_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{ldata['credit']}/- ਦਾ ਦਾਨ (Bank Transfer ਰਾਹੀਂ) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
                        url = f"https://wa.me/{c_phone}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{url}" target="_blank" class="whatsapp-btn">💬 WhatsApp \'ਤੇ ਰਸੀਦ ਭੇਜੋ (Send via WhatsApp)</a>', unsafe_allow_html=True)

# ==========================================
# 4. BALANCE SHEET & P&L
# ==========================================
elif selected_tab == "⚖️ ਖਾਤੇ (P&L & Balance Sheet)":
    st.header("⚖️ ਵਿੱਤੀ ਖਾਤੇ (Financial Statements)")
    
    don_data = supabase.table("donations").select("*").execute().data or []
    exp_data = supabase.table("expenses").select("*").execute().data or []
    ledg_data = supabase.table("bank_ledger").select("*").execute().data or []
    assets_data = supabase.table("assets").select("*").execute().data or []
    liab_data = supabase.table("liabilities").select("*").execute().data or []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledg_data)
    df_assets = pd.DataFrame(assets_data) if assets_data else pd.DataFrame(columns=['name', 'value'])
    df_liab = pd.DataFrame(liab_data) if liab_data else pd.DataFrame(columns=['name', 'value'])
    
    total_income = df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)']['amount'].sum() if not df_don.empty else 0.0
    total_income += df_ledg['credit'].sum() if not df_ledg.empty else 0.0
    total_expense = df_exp['amount'].sum() if not df_exp.empty else 0.0
    total_expense += df_ledg['debit'].sum() if not df_ledg.empty else 0.0
    
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
    bank_balances = {"ਨਕਦ (Cash)": 0.0, "Kotak Bank": 0.0, "Punjab & Sind Bank": 0.0}
    
    for bank in BANK_ACCOUNTS:
        b_in = df_don[(df_don['bank_account'] == bank) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don.get('add_to_mirror', True) == True)]['amount'].sum() if not df_don.empty else 0
        b_in += df_ledg[df_ledg['bank_name'] == bank]['credit'].sum() if not df_ledg.empty else 0
        b_out = df_exp[(df_exp['bank_account'] == bank) & (df_exp.get('add_to_mirror', True) == True)]['amount'].sum() if not df_exp.empty else 0
        b_out += df_ledg[df_ledg['bank_name'] == bank]['debit'].sum() if not df_ledg.empty else 0
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
        for b, val in bank_balances.items():
            st.markdown(f'<div class="bs-row"><span>{b}:</span><span>₹ {val:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bs-total"><span>Total Assets:</span><span>₹ {total_assets:,.2f}</span></div></div>', unsafe_allow_html=True)
    
    full_html = f"<h3>Income & Expenditure Account</h3>{inc_exp_html}<br><h3>Balance Sheet</h3>"
    full_html += f"""<div style="width:100%;">
    <div class="bs-box"><h4>Liabilities</h4><p>Funds & Liab: {other_liab_val:,.2f}</p><p>Surplus: {surplus:,.2f}</p><hr><p><b>Total: {total_liabilities:,.2f}</b></p></div>
    <div class="bs-box"><h4>Assets</h4><p>Fixed Assets: {fixed_assets_val:,.2f}</p><p>Bank/Cash: {sum(bank_balances.values()):,.2f}</p><hr><p><b>Total: {total_assets:,.2f}</b></p></div>
    </div>"""
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
                    st.success("ਸੇਵ ਹੋ ਗਿਆ!"); st.rerun()
        with ac2:
            with st.form("add_liab"):
                st.write("**Fund/Liability (ਫੰਡ ਜਾਂ ਉਧਾਰ ਜੋੜੋ)**")
                l_name = st.text_input("ਫੰਡ ਦਾ ਨਾਮ (e.g. Corpus Fund, Loan)")
                l_val = st.number_input("ਮੁੱਲ (Value ₹)", min_value=0.0)
                if st.form_submit_button("ਫੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                    supabase.table("liabilities").insert({"name": l_name, "value": l_val, "date_added": str(date.today())}).execute()
                    st.success("ਸੇਵ ਹੋ ਗਿਆ!"); st.rerun()

# ==========================================
# 5. STOCK
# ==========================================
elif selected_tab == "📦 ਸਟਾਕ (Stock)":
    st.header("ਸਟਾਕ / ਭੰਡਾਰ (Stock Management)")
    col1, col2 = st.columns([1, 2])
    with col1:
        if not is_mgmt:
            with st.form("stock_form", clear_on_submit=True):
                item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ (Item Name)")
                qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=0.0, step=0.5)
                unit = st.selectbox("ਇਕਾਈ (Unit)", ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)"])
                est_val = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (Value ₹ - Optional)", min_value=0.0)
                stock_action = st.radio("ਐਕਸ਼ਨ (Action)", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add Stock)", "ਸਮਾਨ ਵਰਤਿਆ (Remove Stock)"])
                if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ (Update Stock)", type="primary") and item_name:
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    res = supabase.table("stock").select("*").eq("item_name", item_name).execute()
                    if res.data: supabase.table("stock").update({"quantity": res.data[0]['quantity'] + qty if "Add" in stock_action else max(0, res.data[0]['quantity'] - qty), "estimated_value": res.data[0].get('estimated_value',0) + est_val if "Add" in stock_action else max(0, res.data[0].get('estimated_value',0) - est_val), "last_updated": current_date, "unit": unit}).eq("item_name", item_name).execute()
                    else: supabase.table("stock").insert({"item_name": item_name, "quantity": qty if "Add" in stock_action else 0, "estimated_value": est_val if "Add" in stock_action else 0, "unit": unit, "last_updated": current_date}).execute()
                    st.success(f"✅ ਸਟਾਕ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ!")
        else:
            st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    with col2:
        stock_res = supabase.table("stock").select("*").gt("quantity", 0).execute()
        if stock_res.data:
            df_stock = pd.DataFrame(stock_res.data)[['item_name', 'quantity', 'unit', 'estimated_value', 'last_updated']]
            st.dataframe(df_stock, use_container_width=True)
            report_file_stock = generate_html_report("Current Stock Inventory (ਮੌਜੂਦਾ ਸਟਾਕ)", df_stock.to_html(index=False, border=1, classes='report-table'))
            with open(report_file_stock, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸਟਾਕ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stock, mime="text/html")

# ==========================================
# 6. STUDENTS
# ==========================================
elif selected_tab == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
    st.header("ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ (Student Records)")
    if not is_mgmt:
        with st.form("student_form", clear_on_submit=True):
            stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ (Student Name)")
            stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)")
            stu_course = st.selectbox("ਕਲਾਸ (Course)", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"])
            join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ (Join Date)", value=date.today())
            if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ", type="primary") and stu_name:
                supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ"}).execute()
                st.success("✅ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
    else:
        st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ: ਤੁਸੀਂ ਸਿਰਫ਼ ਡਾਟਾ ਦੇਖ ਸਕਦੇ ਹੋ।")

    st.markdown("---")
    st.subheader("📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ (Student List)")
    student_data = supabase.table("students").select("*").execute().data or []
    if student_data:
        df_students = pd.DataFrame(student_data)[['id', 'name', 'phone', 'course', 'join_date', 'pass_date']]
        st.dataframe(df_students, use_container_width=True)
        report_file_stu = generate_html_report("Enrolled Students", df_students.to_html(index=False, border=1, classes='report-table'))
        with open(report_file_stu, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stu, mime="text/html")

# ==========================================
# 7. EXCEL REPORTS
# ==========================================
elif selected_tab == "📊 ਐਕਸਲ ਰਿਪੋਰਟਾਂ (Excel Reports)":
    st.header("📊 ਐਕਸਲ ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ (Download All Data Backup)")
    st.info("ਸਾਰੇ ਡਾਟੇ ਦਾ ਮੁਕੰਮਲ ਬੈਕਅੱਪ ਐਕਸਲ ਫਾਈਲ ਵਿੱਚ ਡਾਊਨਲੋਡ ਕਰੋ। (Download complete backup in Excel)")
    
    if st.button("📊 ਰਿਪੋਰਟ ਤਿਆਰ ਕਰੋ (Generate Excel Report)", type="primary"):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            pd.DataFrame(supabase.table("donations").select("*").execute().data or []).to_excel(writer, sheet_name='Donations', index=False)
            pd.DataFrame(supabase.table("expenses").select("*").execute().data or []).to_excel(writer, sheet_name='Expenses', index=False)
            pd.DataFrame(supabase.table("bank_ledger").select("*").execute().data or []).to_excel(writer, sheet_name='Bank Ledger', index=False)
            pd.DataFrame(supabase.table("stock").select("*").execute().data or []).to_excel(writer, sheet_name='Stock', index=False)
            pd.DataFrame(supabase.table("students").select("*").execute().data or []).to_excel(writer, sheet_name='Students', index=False)
            pd.DataFrame(supabase.table("assets").select("*").execute().data or []).to_excel(writer, sheet_name='Fixed Assets', index=False)
            pd.DataFrame(supabase.table("liabilities").select("*").execute().data or []).to_excel(writer, sheet_name='Liabilities', index=False)
        
        st.download_button("📥 ਐਕਸਲ ਡਾਊਨਲੋਡ ਕਰੋ (Download Backup)", data=buffer.getvalue(), file_name=f"NGO_Backup_{datetime.now().strftime('%d-%m-%Y')}.xlsx", type="primary")

# ==========================================
# 8. DELETE SYSTEM (ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ)
# ==========================================
elif selected_tab == "🗑️ ਡਿਲੀਟ (Delete)":
    import time
    st.header("🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete Management)")
    t_map = {"ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", "ਸੰਪਤੀ (Asset)": "assets", "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", "ਵਿਦਿਆਰਥੀ (Student)": "students"}
    
    if is_admin:
        st.subheader("🔔 ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਬੇਨਤੀਆਂ (Pending Requests from Staff)")
        reqs = supabase.table("deletion_requests").select("*").eq("status", "Pending").execute().data
        if reqs:
            df_reqs = pd.DataFrame(reqs)[['id', 'table_name', 'record_id', 'details', 'created_at']]
            st.dataframe(df_reqs, use_container_width=True)
            
            with st.form("approve_reject_form"):
                req_id = st.number_input("ਬੇਨਤੀ ID ਭਰੋ (Enter Request ID)", min_value=0, step=1)
                action = st.radio("ਕੀ ਕਰਨਾ ਹੈ? (Action)", ["✅ ਮਨਜ਼ੂਰ ਕਰੋ ਅਤੇ ਡਿਲੀਟ ਕਰੋ (Approve & Delete)", "❌ ਰੱਦ ਕਰੋ (Reject)"])
                if st.form_submit_button("ਲਾਗੂ ਕਰੋ (Apply)", type="primary") and req_id > 0:
                    req_id_int = int(req_id)
                    target_req = next((r for r in reqs if int(r['id']) == req_id_int), None)
                    if target_req:
                        if "Approve" in action:
                            t_name = target_req['table_name']
                            r_id = target_req['record_id']
                            try:
                                if t_name == "stock": supabase.table(t_name).delete().eq("item_name", str(r_id)).execute()
                                else: supabase.table(t_name).delete().eq("id", int(float(r_id))).execute()
                                supabase.table("deletion_requests").update({"status": "Approved"}).eq("id", req_id_int).execute()
                                st.success("✅ ਐਂਟਰੀ ਸਫਲਤਾਪੂਰਵਕ ਡਿਲੀਟ ਹੋ ਗਈ ਹੈ! (Entry Deleted!)")
                                time.sleep(1.5); st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                        else:
                            try:
                                supabase.table("deletion_requests").update({"status": "Rejected"}).eq("id", req_id_int).execute()
                                st.success("❌ ਬੇਨਤੀ ਰੱਦ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ! (Request Rejected!)")
                                time.sleep(1.5); st.rerun()
                            except Exception as e: st.error(f"Error: {e}")
                    else: st.error("ਗਲਤ ਬੇਨਤੀ ID! (Invalid Request ID)")
        else: st.info("ਇਸ ਸਮੇਂ ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ। (No pending requests.)")
        st.markdown("---")
        st.subheader("⚡ ਸਿੱਧਾ ਡਿਲੀਟ ਕਰੋ (Direct Admin Delete)")
        
    if is_staff: st.info("⚠️ ਸਟਾਫ ਸਿੱਧਾ ਡਿਲੀਟ ਨਹੀਂ ਕਰ ਸਕਦਾ। ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਕੋਲ ਮਨਜ਼ੂਰੀ ਲਈ ਜਾਵੇਗੀ। (Staff can only request deletion.)")
        
    del_type = st.selectbox("ਕੀ ਡਿਲੀਟ ਕਰਨਾ ਹੈ? (Select Category)", list(t_map.keys()))
    
    if del_type == "ਸਟਾਕ (Stock)":
        del_item = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ ਭਰੋ (Enter Item Name)")
        if st.button("🔍 ਸਟਾਕ ਲੱਭੋ (Find)", type="primary"):
            res = supabase.table("stock").select("*").eq("item_name", del_item).execute()
            if res.data:
                st.session_state['del_entry_data'] = res.data[0]
                st.session_state['del_entry_id'] = del_item
                st.session_state['del_entry_type'] = del_type
            else: st.error("❌ ਨਹੀਂ ਮਿਲੀ। (Not found)")
    else:
        del_id = st.number_input("ਐਂਟਰੀ ਦਾ ID ਭਰੋ (Entry ID)", min_value=0, step=1)
        if st.button("🔍 ਐਂਟਰੀ ਲੱਭੋ (Find)", type="primary"):
            res = supabase.table(t_map[del_type]).select("*").eq("id", del_id).execute()
            if res.data:
                st.session_state['del_entry_data'] = res.data[0]
                st.session_state['del_entry_id'] = str(del_id)
                st.session_state['del_entry_type'] = del_type
            else: st.error("❌ ਨਹੀਂ ਮਿਲੀ। (Not found)")
            
    if 'del_entry_data' in st.session_state and st.session_state.get('del_entry_type') == del_type:
        data = st.session_state['del_entry_data']
        record_id = st.session_state['del_entry_id']
        st.write("### 📄 ਐਂਟਰੀ ਦਾ ਵੇਰਵਾ (Entry Details):")
        
        details_str = ""
        if del_type == "ਦਾਨ (Donation)": details_str = f"ਨਾਮ: {data.get('name')}, ਰਕਮ: ₹{data.get('amount')}, ਮਿਤੀ: {data.get('date')}"
        elif del_type == "ਖਰਚਾ (Expense)": details_str = f"ਵੇਰਵਾ: {data.get('description')}, ਰਕਮ: ₹{data.get('amount')}, ਮਿਤੀ: {data.get('date')}"
        elif del_type == "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": details_str = f"ਬੈਂਕ: {data.get('bank_name')}, ਵੇਰਵਾ: {data.get('description')}, Credit: ₹{data.get('credit')}, Debit: ₹{data.get('debit')}"
        elif del_type == "ਵਿਦਿਆਰਥੀ (Student)": details_str = f"ਨਾਮ: {data.get('name')}, ਕੋਰਸ: {data.get('course')}"
        elif del_type == "ਸਟਾਕ (Stock)": details_str = f"ਨਾਮ: {data.get('item_name')}, ਮਾਤਰਾ: {data.get('quantity')}"
        else: details_str = f"ਨਾਮ: {data.get('name')}, ਮੁੱਲ: ₹{data.get('value')}"
        
        st.info(details_str)
        
        if is_admin:
            if st.button("🛑 ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ (Confirm Direct Delete)", type="primary"):
                try:
                    if del_type == "ਸਟਾਕ (Stock)": supabase.table(t_map[del_type]).delete().eq("item_name", record_id).execute()
                    else: supabase.table(t_map[del_type]).delete().eq("id", int(float(record_id))).execute()
                    st.success("✅ ਡਿਲੀਟ ਹੋ ਗਿਆ!"); st.session_state.pop('del_entry_data', None); time.sleep(1.5); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        elif is_staff:
            if st.button("📩 ਐਡਮਿਨ ਨੂੰ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ (Send to Admin for Approval)", type="primary"):
                supabase.table("deletion_requests").insert({
                    "table_name": t_map[del_type], "record_id": str(record_id), "details": details_str, "requested_by": "staff"
                }).execute()
                st.success("✅ ਤੁਹਾਡੀ ਬੇਨਤੀ ਐਡਮਿਨ ਨੂੰ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ! (Request sent to Admin!)")
                st.session_state.pop('del_entry_data', None); time.sleep(1.5); st.rerun()

# ==========================================
# 9. ADMIN TOOLS (Bulk Uploads)
# ==========================================
elif selected_tab == "⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Tools)":
    st.header("⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Controls)")
    st.subheader("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload Donations)")
    uploaded_file = st.file_uploader("ਦਾਨ ਦਾ ਰਿਕਾਰਡ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ", type=['xlsx', 'xls'])
    if uploaded_file is not None:
        df_upload = pd.read_excel(uploaded_file)
        df_upload.columns = df_upload.columns.str.lower()
        if 'balance' not in df_upload.columns: st.error("ਐਕਸਲ ਵਿੱਚ 'Balance' ਕਾਲਮ ਨਹੀਂ ਹੈ!")
        else:
            if 'add_to_mirror' not in df_upload.columns: df_upload['add_to_mirror'] = True
            if st.button("🚀 ਸਾਰਾ ਡਾਟਾ ਸੇਵ ਕਰੋ", type="primary"):
                df_upload['balance'] = df_upload['balance'].fillna(0); df_upload['add_to_mirror'] = df_upload['add_to_mirror'].fillna(True).astype(bool)
                supabase.table("donations").insert(df_upload.to_dict(orient='records')).execute()
                st.success("✅ ਅੱਪਲੋਡ ਸਫਲ!")
