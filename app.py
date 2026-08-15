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

USERS = {"admin": "Japnik@3315", "staff": "12345"}

# --- SUPABASE ਕਨੈਕਸ਼ਨ ---
SUPABASE_URL = "https://jbvtvrhzzucggqhwjzuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ (Sabha Manager Pro)", page_icon="logo.png", layout="wide")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Supabase ਨਾਲ ਜੁੜਨ ਵਿੱਚ ਸਮੱਸਿਆ ਆ ਰਹੀ ਹੈ। (Error connecting to Supabase.)")

# --- HTML REPORT GENERATOR ---
def generate_html_report(title, df):
    table_html = df.to_html(index=False, border=1, classes='report-table')
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 10px;">' if logo_base64 else ''
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pa">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; color: #333; }}
            .header {{ text-align: center; margin-bottom: 20px; border-bottom: 2px solid #4A1B15; padding-bottom: 15px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #4A1B15; margin-bottom: 5px; }}
            .report-title {{ font-size: 18px; font-weight: bold; color: #D92B2B; margin-top: 10px; }}
            .report-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; text-align: left; }}
            .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 8px; }}
            .report-table th {{ background-color: #F8F1D1; color: #4A1B15; font-weight: bold; }}
            @media print {{ body {{ padding: 0; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            {img_html}
            <div class="title">{NGO_NAME_PB}</div>
            <div>{NGO_ADDRESS_PB}</div>
            <div class="report-title">{title}</div>
            <div style="font-size: 12px; margin-top: 5px; color: #555;">Report Generated On: {datetime.now().strftime("%d-%m-%Y %H:%M")}</div>
        </div>
        {table_html}
        <script>window.onload = function() {{ window.print(); }}</script>
    </body>
    </html>
    """
    filename = f"Report_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename

# --- ਰਸੀਦ ਡਿਜ਼ਾਈਨ (RECEIPT DESIGN) ---
def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, don_type, item_details, bank_acc, on_account_of):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Logo">' if logo_base64 else ''
    amount_text = f"Rs. {amount}/-" if don_type == "ਪੈਸੇ (Monetary)" else f"{item_details}"
    amount_in_words = f"Rupees {amount} Only" if don_type == "ਪੈਸੇ (Monetary)" else item_details
    display_phone = phone if phone else "________________"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pa">
    <head>
        <meta charset="UTF-8">
        <title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #fff; padding: 20px; }}
            .receipt-box {{ max-width: 850px; margin: auto; padding: 20px 30px; background-color: #F8F1D1; border-top: 25px solid #4A1B15; border-bottom: 25px solid #4A1B15; color: #333; position: relative; box-sizing: border-box; }}
            .header-flex {{ display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 5px; }}
            .logo-img {{ position: absolute; left: 0; top: 0; width: 100px; height: auto; }}
            .header-text {{ text-align: center; width: 100%; padding-left: 110px; box-sizing: border-box; }}
            .title-pa {{ font-size: 32px; font-weight: bold; color: #4A1B15; margin: 0; letter-spacing: 1px; }}
            .title-en {{ font-size: 20px; font-weight: bold; color: #4A1B15; margin: 5px 0 10px 0; }}
            .sub-title-pa {{ font-size: 16px; color: #D92B2B; font-weight: bold; margin: 2px 0; }}
            .sub-title-en {{ font-size: 14px; font-weight: bold; color: #0F4C81; margin: 5px 0; }}
            .phones {{ font-size: 13px; font-weight: bold; color: #333; margin: 2px 0; }}
            .reg-row {{ display: flex; justify-content: space-between; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; padding: 6px 0; font-size: 14px; font-weight: bold; margin-bottom: 15px; margin-top: 10px; }}
            .main-content {{ font-size: 16px; line-height: 2.2; font-weight: bold; color: #222; }}
            .row-inline {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .field-value {{ font-family: 'Courier New', Courier, monospace; font-size: 18px; color: #0F4C81; border-bottom: 1px solid #666; padding: 0 15px; font-weight: bold; }}
            .receipt-no {{ color: #D92B2B; font-size: 22px; font-weight: bold; font-family: monospace; }}
            .footer-flex {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15px; }}
            .bank-details-box {{ font-size: 12px; font-weight: bold; line-height: 1.5; background-color: rgba(255,255,255,0.4); padding: 5px 10px; border-radius: 5px; width: 65%; }}
            .bank-details-box span {{ color: #D92B2B; }}
            .amount-box {{ font-size: 22px; font-weight: bold; color: #0F4C81; border: 2px solid #333; padding: 5px 25px; border-radius: 20px; background-color: rgba(255,255,255,0.5); display: inline-block; }}
            .sign-box {{ text-align: right; margin-top: 20px; font-size: 14px; padding-bottom: 15px; }}
            .bottom-note {{ position: absolute; bottom: 0; left: 0; right: 0; background-color: #4A1B15; color: white; text-align: center; font-size: 12px; padding: 4px 0; font-weight: bold; }}
            @media print {{ body {{ padding: 0; }} .receipt-box {{ border: 2px solid #4A1B15; box-shadow: none; }} }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="header-flex">
                {img_html}
                <div class="header-text">
                    <p class="title-pa">ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)</p>
                    <p class="title-en">Shabad Kirtan Nam Simran Satsang (Regd.)</p>
                    <p class="sub-title-pa">ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ) ਰਾਧਾ ਕ੍ਰਿਸ਼ਨ ਕਲੋਨੀ (ਮੂਲੇ ਚੱਕ), ਨੇੜੇ ਭਗਤਾਂ ਵਾਲਾ ਦਾਣਾ ਮੰਡੀ, ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ</p>
                    <p class="sub-title-en">Regd. Office: C. B. Tower, Opp. Side Alpha One Mall, G. T. Road, Sri Amritsar Sahib - 143001</p>
                    <p class="phones">(M) 099150-07697, 78953-33290, 98157-55883</p>
                </div>
            </div>
            <div class="reg-row">
                <div>Regd. No.: ASR/26/2024-25 &nbsp;|&nbsp; PAN NO. ABKTS7853G</div>
                <div>On Account of: <span class="field-value" style="font-size:16px;">{on_account_of}</span></div>
            </div>
            <div class="main-content">
                <div class="row-inline">
                    <div>ਰਸੀਦ ਨੰ. <span class="field-value receipt-no" style="padding-left: 20px;">{receipt_no:04d}</span></div>
                    <div>ਮਿਤੀ <span class="field-value">{date_str[:10]}</span></div>
                </div>
                <div style="margin-top: 10px;">ਸਤਿਕਾਰ ਯੋਗ <span class="field-value" style="display:inline-block; width: 45%;">{name}</span> ਜੀ ਪਾਸੋਂ, ਮੋ.ਨੰ: <span class="field-value">{display_phone}</span></div>
                <div style="margin-top: 10px;">ਰਕਮ ਅੱਖਰੀ <span class="field-value" style="display:inline-block; width: 65%;">{amount_in_words}</span> ਧੰਨਵਾਦ ਸਹਿਤ ਵਸੂਲ ਪਾਏ।</div>
                <div style="margin-top: 10px;">ਕੈਸ਼/ਚੈਕ/ਗੂਗਲ ਪੇ/ਯੂ ਟੀ ਆਰ ਨੰ. <span class="field-value" style="display:inline-block; width: 25%;">{payment_mode}</span> ਬੈਂਕ <span class="field-value" style="display:inline-block; width: 15%;">{bank_acc}</span> ਮਿਤੀ <span class="field-value">{date_str[:10]}</span></div>
            </div>
            <div class="footer-flex">
                <div class="bank-details-box">
                    <div style="background-color: #333; color: white; padding: 2px 10px; display: inline-block; border-radius: 5px 5px 0 0; margin-bottom: 2px;">BANK A/C DETAILS :</div><br>
                    <strong>PUNJAB & SIND BANK</strong> A/c No. <span>06181000012550</span> IFSC : <span>PSIB0000618</span><br>
                    <span style="color:#333; font-weight:normal;">Sultanwind Road, Amritsar</span><br>
                    <strong>KOTAK MAHINDRA BANK</strong> A/c No. <span>4350934312</span> IFSC : <span>KKBK0004001</span><br>
                    <span style="color:#333; font-weight:normal;">East Mohan Nagar, Amritsar</span>
                </div>
                <div style="text-align: center;">
                    <div class="amount-box">{amount_text}</div>
                    <div class="sign-box">ਪ੍ਰਾਪਤ ਕਰਤਾ</div>
                </div>
            </div>
            <div class="bottom-note">Note : If you transfer any amount direct to the account please intimate on Mob : 9915007697</div>
        </div>
        <script>window.onload = function() {{ window.print(); }}</script>
    </body>
    </html>
    """
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.is_admin = False

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=150)
        st.markdown(f"<h2 style='text-align: center;'>{NGO_NAME_PB}</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)"):
                if username_input in USERS and USERS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = (username_input == "admin")
                    st.rerun()
                else:
                    st.error("ਗਲਤ ਪਾਸਵਰਡ! (Incorrect Password!)")
    st.stop()

# --- SIDEBAR NAVIGATION (ਖੱਬੇ ਪਾਸੇ ਦਾ ਮੀਨੂ) ---
with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    st.success("✅ ਐਡਮਿਨ ਮੋਡ (Admin Mode)" if st.session_state.is_admin else "✅ ਕਰਮਚਾਰੀ ਮੋਡ (Staff Mode)")
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    st.subheader("ਮੁੱਖ ਮੀਨੂ (Main Menu)")
    
    # Navigation Options
    menu_options = [
        "💸 ਦਾਨ (Donations)", 
        "📉 ਖਰਚੇ (Expenses)", 
        "🏦 ਮਿਰਰ ਬੈਂਕ (Mirror Banks)",
        "📦 ਸਟਾਕ (Stock)", 
        "🎓 ਵਿਦਿਆਰਥੀ (Students)"
    ]
    if st.session_state.is_admin:
        menu_options.append("⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Tools)")
        
    selected_tab = st.radio("ਚੁਣੋ (Select)", menu_options, label_visibility="collapsed")

# --- MAIN CONTENT HEADER ---
colA, colB = st.columns([1, 8])
with colA:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
with colB:
    st.title(f"{NGO_NAME_PB}")

st.markdown("---")

# ==========================================
# 1. DONATIONS (ਦਾਨ)
# ==========================================
if selected_tab == "💸 ਦਾਨ (Donations)":
    st.header("ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ (Enter New Donation)")
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
        donor_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number - Optional)")
        on_account_of = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of - e.g. Monthly Donation)")
        don_type = st.radio("ਦਾਨ ਦੀ ਕਿਸਮ (Type of Donation)", ["ਪੈਸੇ (Monetary)", "ਸਮਾਨ (In-Kind / Ration)"])
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=0)
            pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Payment Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Cheque", "NEFT/RTGS"])
        with col_m2:
            item_details = st.text_input("ਜੇਕਰ ਸਮਾਨ ਹੈ ਤਾਂ ਵੇਰਵਾ ਲਿਖੋ (Item Details if In-Kind)")
            bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ? (Select Bank)", BANK_ACCOUNTS)
            
        receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ (Receipt Date)", value=date.today())
        
        st.markdown("---")
        add_to_mirror = st.checkbox("✅ ਇਸ ਐਂਟਰੀ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਜੋੜੋ (Add to Bank Mirror Ledger)", value=True, help="Uncheck if this is already uploaded via Bank Statement.")
        
        submitted = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ (Save & Generate Receipt)")
        
    if submitted and donor_name:
        formatted_date = receipt_date.strftime("%Y-%m-%d")
        data, count = supabase.table("donations").insert({
            "name": donor_name, "phone": donor_phone, "amount": amount, 
            "date": formatted_date, "payment_mode": pay_mode,
            "donation_type": don_type, "item_details": item_details, "bank_account": bank_acc,
            "on_account_of": on_account_of, "add_to_mirror": add_to_mirror
        }).execute()
        
        receipt_id = data[1][0]['id']
        html_file = generate_html_receipt(receipt_id, donor_name, donor_phone, amount, formatted_date, pay_mode, don_type, item_details, bank_acc, on_account_of)
        st.success(f"✅ ਰਸੀਦ #{receipt_id} ਤਿਆਰ ਹੈ। (Receipt Ready)")
        
        with open(html_file, "r", encoding="utf-8") as file:
            st.download_button("🖨️ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ (Print Receipt)", data=file.read(), file_name=html_file, mime="text/html")
        
        if donor_phone:
            amt_text = f"₹{amount}/- ਦਾ ਦਾਨ ({pay_mode} ਰਾਹੀਂ)" if don_type == "ਪੈਸੇ (Monetary)" else f"ਦਾਨ ਵਜੋਂ '{item_details}'"
            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ {amt_text} ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
            url = f"https://wa.me/{donor_phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f"[💬 WhatsApp ਸੁਨੇਹਾ ਭੇਜਣ ਲਈ ਇੱਥੇ ਕਲਿੱਕ ਕਰੋ (Send WhatsApp)]({url})", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 ਦਾਨ ਰਿਕਾਰਡ ਖੋਜੋ (Search Donations)")
    don_search_col1, don_search_col2 = st.columns(2)
    with don_search_col1:
        search_donor_name = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਦੁਆਰਾ ਖੋਜ ਕਰੋ (Search by Name)")
    with don_search_col2:
        search_don_date = st.date_input("ਮਿਤੀ ਦੁਆਰਾ ਖੋਜ ਕਰੋ (Search by Date)", value=None)

    all_donations = supabase.table("donations").select("*").execute().data
    if all_donations:
        df_donations = pd.DataFrame(all_donations)
        if search_donor_name:
            df_donations = df_donations[df_donations['name'].str.contains(search_donor_name, case=False, na=False)]
        if search_don_date:
            date_str = search_don_date.strftime("%Y-%m-%d")
            df_donations = df_donations[df_donations['date'].str.startswith(date_str)]
        st.dataframe(df_donations[['id', 'name', 'phone', 'amount', 'payment_mode', 'bank_account', 'date']], use_container_width=True)

    st.markdown("---")
    st.subheader("🖨️ ਪੁਰਾਣੀ ਰਸੀਦ ਪ੍ਰਿੰਟ ਕਰੋ (Reprint Old Receipt)")
    search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ ਭਰੋ (Enter Receipt No.)", min_value=1, step=1)
    if st.button("🔍 ਰਸੀਦ ਲੱਭੋ (Find Receipt)"):
        res = supabase.table("donations").select("*").eq("id", search_id).execute()
        if res.data:
            record = res.data[0]
            html_file_rep = generate_html_receipt(
                search_id, record.get('name', ''), record.get('phone', ''), record.get('amount', 0), record.get('date', ''), 
                record.get('payment_mode', 'ਨਕਦ (Cash)'), record.get('donation_type', 'ਪੈਸੇ (Monetary)'), 
                record.get('item_details', ''), record.get('bank_account', 'ਨਕਦ (Cash)'), record.get('on_account_of', '')
            )
            st.success(f"✅ ਰਸੀਦ #{search_id} ਮਿਲ ਗਈ ਹੈ ({record.get('name', '')})! (Receipt Found!)")
            with open(html_file_rep, "r", encoding="utf-8") as file:
                st.download_button(label="🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Reprint)", data=file.read(), file_name=html_file_rep, mime="text/html", key="reprint_btn")
            
            if record.get('phone', ''):
                amt_text = f"₹{record['amount']}/- ਦਾ ਦਾਨ" if record.get('donation_type') == "ਪੈਸੇ (Monetary)" else f"ਦਾਨ ਵਜੋਂ '{record.get('item_details')}'"
                msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {record['name']} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ {amt_text} ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਧੰਨਵਾਦ ਜੀ।"
                url = f"https://wa.me/{record['phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f"[💬 WhatsApp ਸੁਨੇਹਾ ਦੁਬਾਰਾ ਭੇਜਣ ਲਈ ਇੱਥੇ ਕਲਿੱਕ ਕਰੋ (Resend WhatsApp)]({url})", unsafe_allow_html=True)
        else:
            st.error("❌ ਇਸ ਨੰਬਰ ਦੀ ਕੋਈ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ। (Receipt not found.)")

# ==========================================
# 2. EXPENSES (ਖਰਚੇ)
# ==========================================
elif selected_tab == "📉 ਖਰਚੇ (Expenses)":
    st.header("ਖਰਚਾ ਦਰਜ ਕਰੋ (Enter Expense)")
    with st.form("expense_form", clear_on_submit=True):
        desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Expense Description)")
        cat = st.selectbox("ਕੈਟਾਗਰੀ (Category / Sub-head)", [c for c in EXPENSE_CATEGORIES if not c.startswith("---")])
        exp_amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1)
        bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ? (From which Bank?)", BANK_ACCOUNTS)
        exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ (Date)", value=date.today())
        
        st.markdown("---")
        add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਮਿਰਰ ਖਾਤੇ ਵਿੱਚ ਵੀ ਦਿਖਾਓ (Add to Bank Mirror Ledger)", value=True)
        
        if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ (Save Expense)") and desc:
            supabase.table("expenses").insert({
                "description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"),
                "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp
            }).execute()
            st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ! (Expense Saved Successfully!)")

    st.markdown("---")
    st.subheader("📑 ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ (Expenditure Report)")
    exp_data_all = supabase.table("expenses").select("*").execute().data or []
    if exp_data_all:
        df_exp_view = pd.DataFrame(exp_data_all)
        df_exp_view = df_exp_view[['id', 'date', 'description', 'category', 'amount', 'bank_account']].sort_values(by='date', ascending=False)
        st.dataframe(df_exp_view, use_container_width=True)
        
        report_file_exp = generate_html_report("Expenditure Report (ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ)", df_exp_view)
        with open(report_file_exp, "r", encoding="utf-8") as file:
            st.download_button("🖨️ ਖਰਚਿਆਂ ਦੀ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Expense Report)", data=file.read(), file_name=report_file_exp, mime="text/html")

# ==========================================
# 3. MIRROR BANKS (ਮਿਰਰ ਬੈਂਕ)
# ==========================================
elif selected_tab == "🏦 ਮਿਰਰ ਬੈਂਕ (Mirror Banks)":
    st.header("ਮਿਰਰ ਬੈਂਕ ਖਾਤੇ (Full Mirror Ledger)")
    
    don_data = supabase.table("donations").select("*").execute().data or []
    exp_data = supabase.table("expenses").select("*").execute().data or []
    ledger_data = supabase.table("bank_ledger").select("*").execute().data or []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledger_data)
    
    selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ (Select Bank)", BANK_ACCOUNTS)
    
    st.markdown("### 📅 ਮਿਤੀ ਅਨੁਸਾਰ ਸਟੇਟਮੈਂਟ (Statement Period)")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ (Start Date)", value=date(date.today().year, date.today().month, 1))
    with col_d2:
        end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ (End Date)", value=date.today())

    ledger_entries = []
    
    if not df_don.empty:
        if 'add_to_mirror' not in df_don.columns:
            df_don['add_to_mirror'] = True
        df_don['add_to_mirror'] = df_don['add_to_mirror'].fillna(True).astype(bool)
        
        bank_dons = df_don[(df_don['bank_account'] == selected_bank) & (df_don['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don['add_to_mirror'] == True)]
        for _, row in bank_dons.iterrows():
            ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ (Donation): {row['name']} (Rec No: {row['id']})", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'App (Donation)'})
            
    if not df_exp.empty:
        if 'add_to_mirror' not in df_exp.columns:
            df_exp['add_to_mirror'] = True
        df_exp['add_to_mirror'] = df_exp['add_to_mirror'].fillna(True).astype(bool)
        
        bank_exps = df_exp[(df_exp['bank_account'] == selected_bank) & (df_exp['add_to_mirror'] == True)]
        for _, row in bank_exps.iterrows():
            ledger_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ (Expense): {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'App (Expense)'})
            
    if not df_ledg.empty:
        bank_ledg = df_ledg[df_ledg['bank_name'] == selected_bank]
        for _, row in bank_ledg.iterrows():
            ledger_entries.append({'ID': row['id'], 'Date': row['txn_date'], 'Description': row['description'], 'Credit': float(row['credit']), 'Debit': float(row['debit']), 'Source': row['source']})
            
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
        
        report_title = f"Bank Statement - {selected_bank} ({start_date} to {end_date})"
        report_file_bank = generate_html_report(report_title, df_period[['Date', 'Description', 'Source', 'Credit', 'Debit', 'Running Balance']])
        with open(report_file_bank, "r", encoding="utf-8") as file:
            st.download_button("🖨️ ਸਟੇਟਮੈਂਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Statement)", data=file.read(), file_name=report_file_bank, mime="text/html")
    else:
        st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਹਾਲੇ ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਹੈ। (No entries yet)")

    st.markdown("### ⚖️ ਬੈਂਕ ਮਿਲਾਨ (Reconciliation Tally)")
    col_bal1, col_bal2, col_bal3 = st.columns(3)
    col_bal1.metric(f"ਅੱਜ ਤੱਕ ਦਾ ਕੁੱਲ ਸਿਸਟਮ ਬੈਲੇਂਸ (System Bal)", f"₹ {sys_bal:,.2f}")
    actual_bal = col_bal2.number_input("ਬੈਂਕ ਦਾ ਅਸਲ ਬੈਲੇਂਸ (Actual Bank Balance)", value=float(sys_bal), step=100.0)
    
    diff = actual_bal - sys_bal
    if diff == 0:
        col_bal3.success("✅ ਖਾਤਾ ਮਿਲ ਗਿਆ (Tally Matched)")
    else:
        col_bal3.error(f"⚠️ ਫਰਕ (Mismatch): ₹ {diff:,.2f}")

    st.markdown("---")
    st.subheader(f"➕ ਬੈਂਕ ਦੀਆਂ ਹੋਰ ਐਂਟਰੀਆਂ ਪਾਓ (Add Bank Ledger Entries)")
    
    t3_col1, t3_col2 = st.columns(2)
    with t3_col1:
        with st.form("manual_ledger"):
            st.write("ਹੱਥੀਂ ਐਂਟਰੀ ਕਰੋ (Manual Entry)")
            m_date = st.date_input("ਮਿਤੀ (Date)")
            m_desc = st.text_input("ਵੇਰਵਾ (Description - e.g. Bank Interest)")
            m_type = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ (Type)", ["ਕ੍ਰੈਡਿਟ / ਆਏ (Credit)", "ਡੈਬਿਟ / ਕੱਟੇ (Debit)"])
            m_amt = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
            if st.form_submit_button("ਐਂਟਰੀ ਸੇਵ ਕਰੋ (Save Entry)"):
                credit_val = m_amt if "Credit" in m_type else 0.0
                debit_val = m_amt if "Debit" in m_type else 0.0
                supabase.table("bank_ledger").insert({
                    "bank_name": selected_bank, "txn_date": m_date.strftime("%Y-%m-%d"),
                    "description": m_desc, "credit": credit_val, "debit": debit_val, "balance": 0, "source": "Manual"
                }).execute()
                st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ! (Entry Saved)")
                st.rerun()
                
    with t3_col2:
        st.write("ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ (Upload Statement Excel)")
        st.warning("Excel Columns: Date, Description, Credit, Debit, Balance")
        stmt_file = st.file_uploader(f"Upload {selected_bank} Statement", type=['xlsx', 'xls'], key="bank_stmt")
        if stmt_file:
            try:
                df_stmt = pd.read_excel(stmt_file)
                df_stmt.columns = df_stmt.columns.str.lower()
                if 'balance' not in df_stmt.columns:
                    st.error("ਐਕਸਲ ਫਾਈਲ ਵਿੱਚ 'Balance' ਕਾਲਮ ਨਹੀਂ ਹੈ! (Balance column missing!)")
                else:
                    if st.button("ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ (Upload Statement)"):
                        ledg_records = []
                        for _, row in df_stmt.iterrows():
                            if pd.isna(row.get('date')) or pd.isna(row.get('description')):
                                continue
                            ledg_records.append({
                                "bank_name": selected_bank, "txn_date": str(row['date'])[:10],
                                "description": str(row['description']), 
                                "credit": float(row.get('credit', 0) if pd.notna(row.get('credit')) else 0),
                                "debit": float(row.get('debit', 0) if pd.notna(row.get('debit')) else 0), 
                                "balance": float(row.get('balance', 0) if pd.notna(row.get('balance')) else 0),
                                "source": "Statement Upload"
                            })
                        if ledg_records:
                            supabase.table("bank_ledger").insert(ledg_records).execute()
                            st.success("✅ ਸਟੇਟਮੈਂਟ ਅੱਪਲੋਡ ਹੋ ਗਈ! (Statement Uploaded)")
                            st.rerun()
            except Exception as e:
                st.error(f"ਫਾਈਲ ਗਲਤ ਹੈ (File Error): {e}")

    st.markdown("---")
    st.subheader("🖨️ ਬੈਂਕ ਐਂਟਰੀ ਤੋਂ ਰਸੀਦ ਬਣਾਓ (Convert Bank Credit to Receipt)")
    st.info("ਜੇਕਰ ਕੋਈ ਪੈਸਾ ਬੈਂਕ ਸਟੇਟਮੈਂਟ ਵਿੱਚ ਆਇਆ ਹੈ ਅਤੇ ਤੁਸੀਂ ਉਸਦੀ ਰਸੀਦ ਕੱਟਣੀ ਹੈ, ਤਾਂ ਇੱਥੇ ਉਸ ਐਂਟਰੀ ਦਾ ID ਭਰੋ।")
    
    col_conv1, col_conv2 = st.columns(2)
    with col_conv1:
        ledger_id = st.number_input("ਬੈਂਕ ਲੈਜ਼ਰ ID ਭਰੋ (Bank Entry ID)", min_value=0, step=1)
        if st.button("🔍 ਬੈਂਕ ਐਂਟਰੀ ਲੱਭੋ (Find Bank Entry)"):
            res = supabase.table("bank_ledger").select("*").eq("id", ledger_id).execute()
            if res.data and res.data[0]['credit'] > 0:
                st.session_state['convert_ledger_id'] = ledger_id
                st.session_state['convert_ledger_data'] = res.data[0]
            else:
                st.error("❌ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ ਜਾਂ ਇਹ ਕ੍ਰੈਡਿਟ (Credit) ਐਂਟਰੀ ਨਹੀਂ ਹੈ।")

    if 'convert_ledger_id' in st.session_state and st.session_state['convert_ledger_id'] == ledger_id:
        ldata = st.session_state['convert_ledger_data']
        with col_conv2:
            st.success(f"**ਐਂਟਰੀ ਮਿਲ ਗਈ (Entry Found):**\nਮਿਤੀ: {ldata['txn_date']}\nਰਕਮ: ₹{ldata['credit']}\nਵੇਰਵਾ: {ldata['description']}")
            with st.form("convert_bank_receipt"):
                c_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
                c_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional Phone)")
                c_acct = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (On Account of)")
                submitted_conv = st.form_submit_button("ਇਸਦੀ ਰਸੀਦ ਬਣਾਓ (Generate Receipt)")
                
        if submitted_conv and c_name:
            data_conv, _ = supabase.table("donations").insert({
                "name": c_name, "phone": c_phone, "amount": ldata['credit'],
                "date": ldata['txn_date'], "payment_mode": "Bank Transfer",
                "donation_type": "ਪੈਸੇ (Monetary)", "bank_account": ldata['bank_name'],
                "on_account_of": c_acct, "add_to_mirror": False
            }).execute()
            
            rec_id = data_conv[1][0]['id']
            h_file = generate_html_receipt(rec_id, c_name, c_phone, ldata['credit'], ldata['txn_date'], "Bank Transfer", "ਪੈਸੇ (Monetary)", "", ldata['bank_name'], c_acct)
            st.success(f"✅ ਰਸੀਦ #{rec_id} ਤਿਆਰ ਹੈ! (Receipt Ready)")
            with open(h_file, "r", encoding="utf-8") as file:
                st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print Receipt)", data=file.read(), file_name=h_file, mime="text/html", key=f"dl_bk_{rec_id}")

# ==========================================
# 4. STOCK (ਸਟਾਕ)
# ==========================================
elif selected_tab == "📦 ਸਟਾਕ (Stock)":
    st.header("ਸਟਾਕ / ਭੰਡਾਰ (Stock Management)")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("stock_form", clear_on_submit=True):
            item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ (Item Name)")
            qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=0.0, step=0.5)
            unit = st.selectbox("ਇਕਾਈ (Unit)", ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)"])
            stock_action = st.radio("ਐਕਸ਼ਨ (Action)", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add Stock)", "ਸਮਾਨ ਵਰਤਿਆ (Remove Stock)"])
            
            if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ (Update Stock)") and item_name:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                res = supabase.table("stock").select("*").eq("item_name", item_name).execute()
                if res.data:
                    old_qty = res.data[0]['quantity']
                    new_qty = old_qty + qty if "Add" in stock_action else max(0, old_qty - qty)
                    supabase.table("stock").update({"quantity": new_qty, "last_updated": current_date, "unit": unit}).eq("item_name", item_name).execute()
                else:
                    new_qty = qty if "Add" in stock_action else 0
                    supabase.table("stock").insert({"item_name": item_name, "quantity": new_qty, "unit": unit, "last_updated": current_date}).execute()
                st.success(f"✅ '{item_name}' ਦਾ ਸਟਾਕ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ! (Stock Updated)")

    with col2:
        stock_res = supabase.table("stock").select("*").gt("quantity", 0).execute()
        if stock_res.data:
            df_stock = pd.DataFrame(stock_res.data)[['item_name', 'quantity', 'unit', 'last_updated']]
            st.dataframe(df_stock, use_container_width=True)
            
            report_file_stock = generate_html_report("Current Stock Inventory (ਮੌਜੂਦਾ ਸਟਾਕ)", df_stock)
            with open(report_file_stock, "r", encoding="utf-8") as file:
                st.download_button("🖨️ ਸਟਾਕ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Stock Report)", data=file.read(), file_name=report_file_stock, mime="text/html")

# ==========================================
# 5. STUDENTS (ਵਿਦਿਆਰਥੀ)
# ==========================================
elif selected_tab == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
    st.header("ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ (Student Records)")
    with st.form("student_form", clear_on_submit=True):
        stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ (Student Name)")
        stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)")
        stu_course = st.selectbox("ਕਲਾਸ (Course)", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ (Computer Class)", "ਸਿਲਾਈ ਸੈਂਟਰ (Tailoring Center)"])
        join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ (Join Date)", value=date.today())
        if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ (Save Record)") and stu_name:
            supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ (Ongoing)"}).execute()
            st.success("✅ ਵਿਦਿਆਰਥੀ ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ! (Student Record Saved)")

    st.markdown("---")
    st.subheader("📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ (Student List)")
    student_data = supabase.table("students").select("*").execute().data or []
    if student_data:
        df_students = pd.DataFrame(student_data)[['id', 'name', 'phone', 'course', 'join_date', 'pass_date']]
        st.dataframe(df_students, use_container_width=True)
        
        report_file_stu = generate_html_report("Enrolled Students Record (ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ)", df_students)
        with open(report_file_stu, "r", encoding="utf-8") as file:
            st.download_button("🖨️ ਵਿਦਿਆਰਥੀ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Student List)", data=file.read(), file_name=report_file_stu, mime="text/html")

# ==========================================
# 6. ADMIN TOOLS (ਐਡਮਿਨ ਟੂਲਸ)
# ==========================================
elif selected_tab == "⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Tools)":
    st.header("⚙️ ਐਡਮਿਨ ਟੂਲਸ (Admin Controls)")
    
    if not st.session_state.is_admin:
        st.error("⚠️ ਸੁਰੱਖਿਆ ਕਾਰਨਾਂ ਕਰਕੇ: ਸਿਰਫ਼ ਐਡਮਿਨ (Admin) ਹੀ ਇੱਥੇ ਬਦਲਾਅ ਕਰ ਸਕਦਾ ਹੈ। (Access Restricted to Admin Only)")
    else:
        st.subheader("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload Donations)")
        st.warning("Excel Columns: name, phone, amount, date, payment_mode, donation_type, item_details, bank_account, on_account_of, balance, add_to_mirror")
        uploaded_file = st.file_uploader("ਦਾਨ ਦਾ ਰਿਕਾਰਡ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ (Upload Excel File)", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                df_upload.columns = df_upload.columns.str.lower()
                if 'balance' not in df_upload.columns:
                    st.error("ਐਕਸਲ ਫਾਈਲ ਵਿੱਚ 'Balance' ਕਾਲਮ ਨਹੀਂ ਹੈ! ਹਰੇਕ ਐਂਟਰੀ ਲਈ ਬੈਲੇਂਸ ਹੋਣਾ ਲਾਜ਼ਮੀ ਹੈ।")
                else:
                    if 'add_to_mirror' not in df_upload.columns:
                        df_upload['add_to_mirror'] = True
                    st.write(df_upload.head())
                    if st.button("🚀 ਸਾਰਾ ਡਾਟਾ ਸੇਵ ਕਰੋ (Upload to Database)"):
                        df_upload['balance'] = df_upload['balance'].fillna(0)
                        df_upload['add_to_mirror'] = df_upload['add_to_mirror'].fillna(True).astype(bool)
                        records = df_upload.to_dict(orient='records')
                        supabase.table("donations").insert(records).execute()
                        st.success(f"✅ {len(records)} ਐਂਟਰੀਆਂ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਈਆਂ! (Entries Saved)")
            except Exception as e:
                st.error(f"ਫਾਈਲ ਵਿੱਚ ਕੋਈ ਗਲਤੀ ਹੈ (File Error): {e}")

        st.markdown("---")
        st.subheader("🗑️ ਯੂਨੀਵਰਸਲ ਡਿਲੀਟ ਸਿਸਟਮ (Universal Delete System)")
        
        del_type = st.selectbox("ਕੀ ਡਿਲੀਟ ਕਰਨਾ ਹੈ? (Select Category to Delete)", 
                                ["ਦਾਨ (Donation)", "ਖਰਚਾ (Expense)", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)", "ਸਟਾਕ (Stock)", "ਵਿਦਿਆਰਥੀ (Student)"])

        if del_type == "ਸਟਾਕ (Stock)":
            del_item = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ ਭਰੋ (Enter Item Name) - ਜਿਵੇਂ ਸਟਾਕ ਲਿਸਟ ਵਿੱਚ ਲਿਖਿਆ ਹੈ")
            if st.button("🔍 ਸਟਾਕ ਲੱਭੋ (Find Stock)"):
                if del_item:
                    res = supabase.table("stock").select("*").eq("item_name", del_item).execute()
                    if res.data:
                        st.session_state['del_stock_data'] = res.data[0]
                        st.session_state['del_stock_name'] = del_item
                    else:
                        st.error("❌ ਇਹ ਵਸਤੂ ਸਟਾਕ ਵਿੱਚ ਨਹੀਂ ਮਿਲੀ। (Item not found)")
                        st.session_state.pop('del_stock_data', None)
                else:
                    st.warning("ਕਿਰਪਾ ਕਰਕੇ ਨਾਮ ਭਰੋ। (Please enter name)")
            
            if 'del_stock_data' in st.session_state and st.session_state.get('del_stock_name') == del_item:
                data = st.session_state['del_stock_data']
                st.info(f"📦 **ਸਟਾਕ ਦਾ ਵੇਰਵਾ (Stock Details):**\n\n**ਨਾਮ (Name):** {data['item_name']}\n\n**ਮਾਤਰਾ (Qty):** {data['quantity']} {data['unit']}\n\n**ਆਖਰੀ ਅਪਡੇਟ (Last Updated):** {data['last_updated']}")
                st.warning("⚠️ ਕੀ ਤੁਸੀਂ ਸੱਚਮੁੱਚ ਇਸਨੂੰ ਹਮੇਸ਼ਾ ਲਈ ਡਿਲੀਟ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ? (Are you sure?)")
                if st.button("🛑 ਹਾਂ, ਡਿਲੀਟ ਕਰੋ (Yes, Confirm Delete)"):
                    supabase.table("stock").delete().eq("item_name", del_item).execute()
                    st.success(f"✅ ਸਟਾਕ '{del_item}' ਸਫਲਤਾਪੂਰਵਕ ਡਿਲੀਟ ਹੋ ਗਿਆ! (Deleted Successfully)")
                    st.session_state.pop('del_stock_data', None)
                    st.rerun()
        else:
            del_id = st.number_input("ਐਂਟਰੀ ਦਾ ID ਨੰਬਰ ਭਰੋ (Enter Entry ID)", min_value=0, step=1)
            table_map = {
                "ਦਾਨ (Donation)": "donations",
                "ਖਰਚਾ (Expense)": "expenses",
                "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger",
                "ਵਿਦਿਆਰਥੀ (Student)": "students"
            }
            if st.button(f"🔍 ਐਂਟਰੀ ਲੱਭੋ (Find Entry)"):
                if del_id > 0:
                    res = supabase.table(table_map[del_type]).select("*").eq("id", del_id).execute()
                    if res.data:
                        st.session_state['del_entry_data'] = res.data[0]
                        st.session_state['del_entry_id'] = del_id
                        st.session_state['del_entry_type'] = del_type
                    else:
                        st.error("❌ ਇਸ ID ਦੀ ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ। (No entry found for this ID)")
                        st.session_state.pop('del_entry_data', None)
                else:
                    st.warning("ਕਿਰਪਾ ਕਰਕੇ ਸਹੀ ID ਭਰੋ। (Please enter valid ID)")
            
            if 'del_entry_data' in st.session_state and st.session_state.get('del_entry_id') == del_id and st.session_state.get('del_entry_type') == del_type:
                data = st.session_state['del_entry_data']
                st.write("### 📄 ਐਂਟਰੀ ਦਾ ਵੇਰਵਾ (Entry Details):")
                
                if del_type == "ਦਾਨ (Donation)":
                    st.info(f"🙏 **ਦਾਨੀ ਦਾ ਨਾਮ (Donor):** {data.get('name')}\n\n**ਰਕਮ (Amount):** ₹{data.get('amount')}\n\n**ਮਿਤੀ (Date):** {data.get('date')}\n\n**ਕਿਸ ਮੱਦ ਲਈ (On Acct of):** {data.get('on_account_of')}")
                elif del_type == "ਖਰਚਾ (Expense)":
                    st.info(f"📉 **ਵੇਰਵਾ (Description):** {data.get('description')}\n\n**ਰਕਮ (Amount):** ₹{data.get('amount')}\n\n**ਕੈਟਾਗਰੀ (Category):** {data.get('category')}\n\n**ਮਿਤੀ (Date):** {data.get('date')}")
                elif del_type == "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)":
                    st.info(f"🏦 **ਬੈਂਕ (Bank):** {data.get('bank_name')}\n\n**ਵੇਰਵਾ (Description):** {data.get('description')}\n\n**Credit (ਆਏ):** ₹{data.get('credit')}\n\n**Debit (ਕੱਟੇ):** ₹{data.get('debit')}\n\n**ਮਿਤੀ (Date):** {data.get('txn_date')}")
                elif del_type == "ਵਿਦਿਆਰਥੀ (Student)":
                    st.info(f"🎓 **ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ (Student):** {data.get('name')}\n\n**ਕੋਰਸ (Course):** {data.get('course')}\n\n**ਦਾਖਲਾ ਮਿਤੀ (Join Date):** {data.get('join_date')}")
                
                st.warning("⚠️ ਕੀ ਤੁਸੀਂ ਸੱਚਮੁੱਚ ਇਸ ਐਂਟਰੀ ਨੂੰ ਹਮੇਸ਼ਾ ਲਈ ਡਿਲੀਟ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ? (Are you sure?)")
                if st.button("🛑 ਹਾਂ, ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ (Yes, Confirm Delete)"):
                    supabase.table(table_map[del_type]).delete().eq("id", del_id).execute()
                    st.success(f"✅ ID #{del_id} ਸਫਲਤਾਪੂਰਵਕ ਡਿਲੀਟ ਹੋ ਗਿਆ! (Deleted Successfully)")
                    st.session_state.pop('del_entry_data', None)
                    st.rerun()
