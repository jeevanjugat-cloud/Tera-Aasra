import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import urllib.parse
import io
import base64
import os
import time
import json
import math
from PIL import Image
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"
NGO_LAT, NGO_LON = 31.6120, 74.8677

BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = ["--- ਕੀਰਤਨ ਸਮਾਗਮ (Samagams) ---", "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)", "ਲੰਗਰ (Langar)", "--- ਤੇਰਾ ਆਸਰਾ (Tera Aasra) ---", "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)", "ਹੋਰ ਖਰਚੇ (Others)"]
STOCK_UNITS = ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)", "ਬੈਗ/ਬੋਰੀਆਂ (Bags)"]
ASSET_TYPES = ["ਬਿਲਡਿੰਗ (Building)", "ਫਰਨੀਚਰ (Furniture)", "ਇਲੈਕਟ੍ਰੋਨਿਕਸ (Electronics/IT)", "ਵਾਹਨ (Vehicles)", "ਮਸ਼ੀਨਰੀ (Machinery)", "ਹੋਰ (Other)"]

USERS = {
    "admin": {"password": "Japnik@3315", "role": "admin"},
    "staff": {"password": "12345", "role": "staff"},
    "management": {"password": "view@123", "role": "management"},
    "emp1": {"password": "emp1", "role": "employee"},
    "emp2": {"password": "emp2", "role": "employee"},
    "emp3": {"password": "emp3", "role": "employee"},
    "emp4": {"password": "emp4", "role": "employee"}
}
SUPABASE_URL = "https://jbvtvrhzzucggqhwjzuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        div[data-testid="stSidebar"] p {font-size: 16px !important; font-weight: 600 !important;}
        .pro-header-flex { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #F8F1D1, #fff); padding: 15px 20px; border-radius: 12px; border: 2px solid #4A1B15; margin-bottom: 20px;}
        .pro-logo { width: 85px; margin-right: 20px; }
        .pro-title { font-size: 28px; font-weight: bold; color: #4A1B15; margin: 0; }
        .pro-tagline { font-size: 17px; font-weight: bold; color: #D92B2B; margin: 4px 0; }
        .bs-box { border: 2px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
        .bs-header { text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px; }
        .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; }
        .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #E53935; border-top: 1px solid #333; padding-top: 8px; }
        .whatsapp-btn { display: inline-block; padding: 10px 20px; background-color: #25D366; color: white !important; font-size: 17px; border-radius: 8px; font-weight: bold; text-decoration: none;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# STRICT DATE PARSER (Outputs: 1 April 2026) & DB HELPERS
# ==========================================
def parse_date_to_obj(val):
    if pd.isna(val) or str(val).strip() in ["", "NaT", "None", "nan", "null"]: return None
    s = str(val).strip().split(" ")[0].split("T")[0]
    try:
        # dayfirst=False forcefully reads 04/01/2026 as April 1, 2026 and 15/04/2026 as April 15
        dt = pd.to_datetime(s, dayfirst=False, errors='coerce')
        if pd.notna(dt): return dt.date()
    except: pass
    return None

def clean_date_to_display(val):
    d = parse_date_to_obj(val)
    if d: return f"{d.day} {d.strftime('%B %Y')}" # Returns Format: 1 April 2026
    return str(val) if pd.notna(val) else ""

def format_dates_in_df(df, ascending=False):
    df_copy = df.copy()
    date_columns = ['date', 'txn_date', 'cheque_date', 'procurement_date', 'issued_date', 'join_date', 'distribution_date', 'usage_date', 'created_at', 'Date', 'date_added']
    
    sort_col = next((c for c in date_columns if c in df_copy.columns), None)
    if sort_col:
        df_copy['__sort_dt'] = df_copy[sort_col].apply(parse_date_to_obj).fillna(date(1900,1,1))
        df_copy = df_copy.sort_values(by='__sort_dt', ascending=ascending).drop(columns=['__sort_dt'])
        
    for col in date_columns:
        if col in df_copy.columns: df_copy[col] = df_copy[col].apply(clean_date_to_display)
            
    if 'last_updated' in df_copy.columns:
        def parse_dt_time(d):
            dt_obj = parse_date_to_obj(d)
            if dt_obj:
                try: return f"{dt_obj.day} {dt_obj.strftime('%B %Y')} {pd.to_datetime(str(d)).strftime('%I:%M %p')}"
                except: return f"{dt_obj.day} {dt_obj.strftime('%B %Y')}"
            return str(d)
        df_copy['last_updated'] = df_copy['last_updated'].apply(parse_dt_time)
    return df_copy

def is_bank_match(record_bank, target_bank):
    rb = "kotak bank regular" if pd.isna(record_bank) or str(record_bank).strip() in ["", "None", "nan", "null"] else str(record_bank).strip().lower()
    tb = str(target_bank).strip().lower()
    if rb == tb: return True
    if "kotak" in tb and "corpus" not in tb: return ("kotak" in rb) and ("corpus" not in rb)
    if "corpus" in tb: return "corpus" in rb
    if "punjab" in tb or "sind" in tb or "psb" in tb: return ("punjab" in rb) or ("sind" in rb) or ("psb" in rb)
    if "ਨਕਦ" in tb or "cash" in tb: return ("ਨਕਦ" in rb) or ("cash" in rb)
    return False

def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000 
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def compress_image(uploaded_file, max_size=(150, 150)):
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file)
            img.thumbnail(max_size)
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG", quality=70)
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except: return ""
    return ""

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return ""

@st.cache_resource
def init_connection(): return create_client(SUPABASE_URL, SUPABASE_KEY)
try: supabase: Client = init_connection()
except: st.error("Supabase Error.")

# ==========================================
# REPORT GENERATORS (COMBINED TO SAVE SPACE)
# ==========================================
def generate_html_report(title, content, landscape=False):
    logo_b64 = get_base64_image("logo.png")
    img = f'<img src="data:image/png;base64,{logo_b64}" style="height:80px;margin-bottom:10px;">' if logo_b64 else ''
    page_css = "@page { size: landscape; margin: 10mm; }" if landscape else ""
    overflow = "overflow-x: auto;" if landscape else "text-align: left;"
    html = f"""<!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>{title}</title>
    <style>{page_css} body {{font-family: 'Segoe UI', sans-serif; padding: 20px; color: #333; text-align: center;}}
    .header {{border-bottom: 2px solid #4A1B15; padding-bottom: 15px; margin-bottom: 20px;}}
    .title {{font-size: 24px; font-weight: bold; color: #4A1B15; margin-bottom: 2px;}}
    .tagline {{font-size: 17px; font-weight: bold; color: #D92B2B; margin-bottom: 5px;}}
    .report-table {{width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; text-align: {'center' if landscape else 'left'};}}
    .report-table th, .report-table td {{border: 1px solid #aaa; padding: 8px;}}
    .report-table th {{background-color: #F8F1D1; color: #4A1B15; font-weight: bold;}}
    .bs-box {{width: 48%; display: inline-block; vertical-align: top; border: 1px solid #333; padding: 10px; box-sizing: border-box; text-align: left;}}
    .table-img {{width: 60px; height: 60px; object-fit: cover; border-radius: 5px; border: 1px solid #ccc;}}
    @media print {{ body {{padding: 0;}} }}</style></head>
    <body><div class="header">{img}<div class="title">{NGO_NAME_PB}</div><div class="tagline">{NGO_TAGLINE_PB}</div>
    <div style="font-size: 13px;">{NGO_ADDRESS_PB}</div><h3 style="color:#0F4C81;margin-top:10px;">{title}</h3></div>
    <div style="{overflow}">{content}</div><script>window.onload=function(){{window.print();}}</script></body></html>"""
    fname = f"Report_{title.replace(' ', '_')}.html"
    with open(fname, "w", encoding="utf-8") as f: f.write(html)
    return fname

def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, don_type, item_details, bank_acc, on_account_of, collector="", address="ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ", cheque_no="", cheque_bank=""):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="position: absolute; left: 0; top: 0; width: 100px; height: auto;">' if logo_base64 else ''
    amount_text = f"Rs. {amount}/-" if don_type == "ਪੈਸੇ (Monetary)" else f"ਕੀਮਤ: Rs. {amount}/-" if amount > 0 else f"{item_details}"
    amount_in_words = f"Rupees {amount} Only" if don_type == "ਪੈਸੇ (Monetary)" else f"{item_details} (In-Kind Donation)"
    pay_display = f"Cheque (ਨੰ: {cheque_no}, ਬੈਂਕ: {cheque_bank})" if payment_mode == "Cheque" and cheque_no else payment_mode
    
    html_content = f"""<!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>Receipt #{receipt_no}</title>
        <style>body {{ font-family: 'Segoe UI', sans-serif; background-color: #fff; padding: 20px; }}
            .receipt-box {{ max-width: 850px; margin: auto; padding: 20px 30px; background-color: #F8F1D1; border-top: 25px solid #4A1B15; border-bottom: 25px solid #4A1B15; position: relative; }}
            .header-flex {{ display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 5px; }}
            .header-text {{ text-align: center; width: 100%; padding-left: 110px; }}
            .title-pa {{ font-size: 26px; font-weight: bold; color: #4A1B15; margin: 0; }}
            .sub-title-pa {{ font-size: 16px; color: #D92B2B; font-weight: bold; margin: 4px 0; }}
            .reg-row {{ display: flex; justify-content: space-between; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; padding: 5px 0; font-size: 13px; font-weight: bold; margin-bottom: 12px; margin-top: 10px; }}
            .main-content {{ font-size: 15px; line-height: 2.0; font-weight: bold; color: #222; }}
            .row-inline {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .field-value {{ font-family: monospace; font-size: 16px; color: #0F4C81; border-bottom: 1px solid #666; padding: 0 10px; font-weight: bold; }}
            .receipt-no {{ color: #D92B2B; font-size: 20px; }}
            .footer-flex {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15px; }}
            .amount-box {{ font-size: 18px; font-weight: bold; color: #0F4C81; border: 2px solid #333; padding: 5px 20px; border-radius: 15px; background-color: rgba(255,255,255,0.5); }}
            @media print {{ body {{ padding: 0; }} .receipt-box {{ border: 2px solid #4A1B15; box-shadow: none; }} }}</style></head>
    <body><div class="receipt-box"><div class="header-flex">{img_html}<div class="header-text"><p class="title-pa">{NGO_NAME_PB}</p><div class="sub-title-pa">{NGO_TAGLINE_PB}</div>
    <p style="font-size:13px; color:#0F4C81; margin: 3px 0; font-weight:bold;">Regd. Office: {NGO_ADDRESS_PB}<br>(M) 099150-07697, 78953-33290</p></div></div>
    <div class="reg-row"><div>Regd. No.: ASR/26/2024-25</div><div>ਕਲੈਕਟਰ: {collector} | On Account of: <span class="field-value">{on_account_of}</span></div></div>
    <div class="main-content"><div class="row-inline"><div>ਰਸੀਦ ਨੰ. <span class="field-value receipt-no">{receipt_no:04d}</span></div><div>ਮਿਤੀ <span class="field-value">{date_str}</span></div></div>
    <div style="margin-top: 10px;">ਸਤਿਕਾਰ ਯੋਗ <span class="field-value">{name}</span> ਜੀ ਪਾਸੋਂ, ਮੋ.ਨੰ: <span class="field-value">{phone if phone else '________'}</span></div>
    <div style="margin-top: 10px;">ਪਤਾ <span class="field-value">{address}</span></div>
    <div style="margin-top: 10px;">ਰਕਮ ਅੱਖਰੀ <span class="field-value">{amount_in_words}</span> ਧੰਨਵਾਦ ਸਹਿਤ ਵਸੂਲ ਪਾਏ।</div>
    <div style="margin-top: 10px;">ਮੋਡ <span class="field-value">{pay_display}</span> ਬੈਂਕ <span class="field-value">{bank_acc}</span> ਮਿਤੀ <span class="field-value">{date_str}</span></div></div>
    <div class="footer-flex">
    <div style="font-size:11px; font-weight:bold; background-color:rgba(255,255,255,0.4); padding:5px; border-radius:5px; width:65%;">
    <div style="background-color:#333; color:white; padding:2px 10px; display:inline-block;">BANK A/C DETAILS :</div><br>
    <strong>PUNJAB & SIND BANK</strong> A/c: <span style="color:#D92B2B;">06181000012550</span> IFSC: <span style="color:#D92B2B;">PSIB0000618</span><br>
    <strong>KOTAK MAHINDRA BANK</strong> A/c: <span style="color:#D92B2B;">4350934312</span> IFSC: <span style="color:#D92B2B;">KKBK0004001</span></div>
    <div style="text-align:center;"><div class="amount-box">{amount_text}</div><div style="margin-top:15px;font-size:14px;">ਪ੍ਰਾਪਤ ਕਰਤਾ</div></div></div>
    </div><script>window.onload = function() {{ window.print(); }}</script></body></html>"""
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_expense_voucher(voucher_no, desc, amount, date_str, cat, bank_acc):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="position: absolute; left: 0; top: 0; width: 80px; height: auto;">' if logo_base64 else ''
    html_content = f"""<!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>Expense Voucher #{voucher_no}</title>
        <style>body {{ font-family: sans-serif; padding: 20px; }} .receipt-box {{ max-width: 800px; margin: auto; padding: 20px 30px; border: 2px solid #333; position: relative; }}
        .header-flex {{ display: flex; align-items: center; justify-content: center; position: relative; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .main-content {{ font-size: 16px; line-height: 2.0; font-weight: bold; }} .field-value {{ font-family: monospace; font-size: 16px; border-bottom: 1px dashed #666; padding: 0 10px; color: #0F4C81; }}
        </style></head><body><div class="receipt-box"><div class="header-flex">{img_html}<div style="text-align:center; width:100%;"><h2 style="margin:0;">{NGO_NAME_PB}</h2><p style="margin:4px 0;">{NGO_TAGLINE_PB}</p></div></div>
        <h3 style="text-align:center;text-decoration:underline;">PAYMENT / EXPENSE VOUCHER</h3>
        <div class="main-content"><div style="display:flex; justify-content:space-between;"><div>ਵਾਊਚਰ ਨੰ: <span class="field-value" style="color:#D92B2B;">{voucher_no}</span></div><div>ਮਿਤੀ: <span class="field-value">{date_str}</span></div></div>
        <div style="margin-top:15px;">ਵੇਰਵਾ (Description): <span class="field-value">{desc}</span></div>
        <div style="margin-top:15px;">ਕੈਟਾਗਰੀ (Category): <span class="field-value">{cat}</span></div>
        <div style="margin-top:15px;">ਬੈਂਕ/ਖਾਤਾ (Paid From): <span class="field-value">{bank_acc}</span></div>
        <div style="margin-top:25px;"><div style="font-size:18px; border:2px solid #333; padding:5px 20px; display:inline-block;">ਰਕਮ (Amount): Rs. {amount}/-</div></div></div>
        <div style="display:flex; justify-content:space-between; margin-top:60px; font-weight:bold; font-size:14px;"><div style="text-align:center;">______________________<br><br>ਪ੍ਰਾਪਤ ਕਰਤਾ</div><div style="text-align:center;">______________________<br><br>ਪ੍ਰਵਾਨ ਕਰਤਾ</div></div></div>
        <script>window.onload = function() {{ window.print(); }}</script></body></html>"""
    filename = f"Expense_Voucher_{voucher_no}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

# --- LEDGER CALCULATIONS ---
def get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe):
    bank_balances = {bank: 0.0 for bank in BANK_ACCOUNTS}
    for bank in BANK_ACCOUNTS:
        b_in, b_out = 0.0, 0.0
        if not df_don_safe.empty and 'bank_account' in df_don_safe.columns:
            if bank == "ਨਕਦ (Cash)": mask_don = df_don_safe['bank_account'].apply(lambda x: is_bank_match(x, bank)) & (df_don_safe['donation_type'] == 'ਪੈਸੇ (Monetary)')
            else: mask_don = df_don_safe['bank_account'].apply(lambda x: is_bank_match(x, bank)) & (df_don_safe['donation_type'] == 'ਪੈਸੇ (Monetary)') & (df_don_safe['add_to_mirror'] == True)
            b_in += df_don_safe[mask_don]['amount'].sum()
        if not df_ledg_safe.empty and 'bank_name' in df_ledg_safe.columns:
            mask_l_cr = df_ledg_safe['bank_name'].apply(lambda x: is_bank_match(x, bank))
            b_in += df_ledg_safe[mask_l_cr]['credit'].sum()
        if not df_exp_safe.empty and 'bank_account' in df_exp_safe.columns:
            if bank == "ਨਕਦ (Cash)": mask_exp = df_exp_safe['bank_account'].apply(lambda x: is_bank_match(x, bank))
            else: mask_exp = df_exp_safe['bank_account'].apply(lambda x: is_bank_match(x, bank)) & (df_exp_safe['add_to_mirror'] == True)
            b_out += df_exp_safe[mask_exp]['amount'].sum()
        if not df_ledg_safe.empty and 'bank_name' in df_ledg_safe.columns:
            mask_l_db = df_ledg_safe['bank_name'].apply(lambda x: is_bank_match(x, bank))
            b_out += df_ledg_safe[mask_l_db]['debit'].sum()
        bank_balances[bank] = b_in - b_out
    return bank_balances

def get_ledger_data(df_don, df_exp, df_ledg, target_bank=None):
    entries = []
    if not df_don.empty:
        df_don['add_to_mirror'] = df_don.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)'].iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank:
                if target_bank == "ਨਕਦ (Cash)":
                    if not is_bank_match(b_acc, target_bank): continue
                else:
                    if not (is_bank_match(b_acc, target_bank) and row['add_to_mirror']): continue
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']} (Rec#{row['id']})", 'Account': b_acc, 'Credit': float(row.get('amount') or 0.0), 'Debit': 0.0, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': 'App (Donation)'})
    
    if not df_exp.empty:
        df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_exp.iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank:
                if target_bank == "ਨਕਦ (Cash)":
                    if not is_bank_match(b_acc, target_bank): continue
                else:
                    if not (is_bank_match(b_acc, target_bank) and row['add_to_mirror']): continue
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Account': b_acc, 'Credit': 0.0, 'Debit': float(row.get('amount') or 0.0), 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': 0.0, 'Source': 'App (Expense)'})
    
    if not df_ledg.empty:
        for _, row in df_ledg.iterrows():
            b_acc = row.get('bank_name')
            if pd.isna(b_acc) or str(b_acc).strip() in ["", "None", "nan"]: b_acc = "Kotak Bank Regular"
            if target_bank and not is_bank_match(b_acc, target_bank): continue
            entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Account': b_acc, 'Credit': float(row.get('credit') or 0.0), 'Debit': float(row.get('debit') or 0.0), 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': row.get('source', 'Manual Entry')})
    return pd.DataFrame(entries)

# ==========================================
# AUTH & ROUTING
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = st.session_state.username = None

for state_key, def_val in [('current_tab', "🏠 ਹੋਮ ਪੇਜ (Home)"), ('entry_mode', "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"), ('acc_mode', "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"), ('other_mode', "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)"), ('admin_mode', "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)")]:
    if state_key not in st.session_state: st.session_state[state_key] = def_val

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=100)
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h2 style='color:#4A1B15;'>{NGO_NAME_PB}</h2><p style='color: #E53935; font-weight: bold;'>{NGO_TAGLINE_PB}</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = USERS[username_input]["role"]
                    st.session_state.username = username_input
                    st.session_state.current_tab = "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)" if st.session_state.role == "employee" else "🏠 ਹੋਮ ਪੇਜ (Home)"
                    st.rerun()
                else: st.error("ਗਲਤ ਪਾਸਵਰਡ!")
    st.stop()

is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"
is_staff = st.session_state.role == "staff"
is_employee = st.session_state.role == "employee"

with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    role_display = {"admin": "ਐਡਮਿਨ ਮੋਡ (Admin)", "management": "ਮੈਨੇਜਮੈਂਟ (View Only)", "staff": "ਕਰਮਚਾਰੀ ਮੋਡ (Staff)", "employee": "ਸਟਾਫ ਹਾਜ਼ਰੀ ਮੋਡ (Employee)"}.get(st.session_state.role, "")
    st.success(f"✅ {role_display}")
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.role = st.session_state.username = None
        st.rerun()
    st.markdown("---")
    st.subheader("ਮੁੱਖ ਮੀਨੂ")
    menu_opts = ["⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)"] if is_employee else ["🏠 ਹੋਮ ਪੇਜ (Home)", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)", "🎓 ਵਿਦਿਆਰਥੀ (Students)", "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)", "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)"]
    if is_admin or is_staff: menu_opts.append("⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)")
    c_idx = menu_opts.index(st.session_state.current_tab) if st.session_state.current_tab in menu_opts else 0
    st.session_state.current_tab = st.radio("ਚੁਣੋ", menu_opts, index=c_idx, label_visibility="collapsed")

logo_b64 = get_base64_image("logo.png")
st.markdown(f"<div class='pro-header-flex'>{f'<img src=\"data:image/png;base64,{logo_b64}\" class=\"pro-logo\">' if logo_b64 else ''}<div class='pro-text-box'><div class='pro-title'>{NGO_NAME_PB}</div><div class='pro-tagline'>{NGO_TAGLINE_PB}</div><div class='pro-sub'>{NGO_ADDRESS_PB}</div></div></div>", unsafe_allow_html=True)
if st.session_state.current_tab != "🏠 ਹੋਮ ਪੇਜ (Home)" and not is_employee:
    if st.button("🏠 ਹੋਮ ਪੇਜ 'ਤੇ ਜਾਓ", type="secondary"): st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"; st.rerun()
    st.markdown("---")

# ==========================================
# 0. EMPLOYEE ATTENDANCE 
# ==========================================
if st.session_state.current_tab == "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)":
    st.header("⏱️ ਰੋਜ਼ਾਨਾ ਹਾਜ਼ਰੀ (Daily Attendance)")
    try: my_profile = supabase.table("staff_profiles").select("*").eq("login_id", st.session_state.get('username', '')).execute().data
    except: my_profile = []
    
    if not my_profile: st.error("⚠️ ਤੁਹਾਡੀ ਲਾਗਇਨ ID ਕਿਸੇ ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ ਨਾਲ ਨਹੀਂ ਜੁੜੀ ਹੋਈ।")
    else:
        clean_name = my_profile[0].get('name', 'Unknown')
        st.success(f"ਜੀ ਆਇਆਂ ਨੂੰ, **{clean_name}** ਜੀ!")
        att_e_tab1, att_e_tab2 = st.tabs(["⏱️ ਅੱਜ ਦੀ ਹਾਜ਼ਰੀ (Punch In/Out)", "📝 ਛੁੱਟੀ ਬੇਨਤੀ (Leave Request)"])
        with att_e_tab1:
            today_str = str(date.today())
            current_time = datetime.now().strftime("%I:%M %p")
            try: today_record = supabase.table("attendance").select("*").eq("staff_name", clean_name).eq("date", today_str).execute().data
            except: today_record = []
            
            st.write("### 📍 ਲੋਕੇਸ਼ਨ ਵੈਰੀਫਿਕੇਸ਼ਨ")
            try:
                from streamlit_geolocation import streamlit_geolocation
                loc = streamlit_geolocation()
                if loc and loc.get('latitude') and loc.get('longitude'):
                    dist = get_distance_meters(loc['latitude'], loc['longitude'], NGO_LAT, NGO_LON)
                    st.write(f"📍 ਮੌਜੂਦਾ ਦੂਰੀ: **{dist:.0f} ਮੀਟਰ**")
                    if dist <= 100:
                        st.success("✅ ਲੋਕੇਸ਼ਨ ਮੈਚ ਹੋ ਗਈ! ਹੁਣ ਤੁਸੀਂ ਹਾਜ਼ਰੀ ਲਗਾ ਸਕਦੇ ਹੋ।")
                        if not today_record:
                            if st.button("🟢 Punch IN (ਆਉਣ ਦਾ ਸਮਾਂ)", type="primary", use_container_width=True):
                                supabase.table("attendance").insert({"staff_name": clean_name, "date": today_str, "in_time": current_time, "out_time": "", "status": "Present"}).execute()
                                st.success("✅ ਹਾਜ਼ਰੀ ਲੱਗ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                        else:
                            rec = today_record[0]
                            st.success(f"✅ Punch IN Time: {rec.get('in_time', '')}")
                            if not rec.get('out_time'):
                                if st.button("🔴 Punch OUT (ਜਾਣ ਦਾ ਸਮਾਂ)", type="primary", use_container_width=True):
                                    supabase.table("attendance").update({"out_time": current_time}).eq("id", rec['id']).execute()
                                    st.success("✅ ਜਾਣ ਦਾ ਸਮਾਂ ਲੱਗ ਗਿਆ ਹੈ!"); time.sleep(1.5); st.rerun()
                            else: st.error(f"🔴 Punch OUT Time: {rec.get('out_time', '')}")
                    else: st.error(f"❌ ਤੁਸੀਂ TERA AASRA ਤੋਂ ਬਾਹਰ ਹੋ।")
            except: st.error("🚨 `pip install streamlit-geolocation` ਚਲਾਓ")
            
            st.markdown("---")
            st.write(f"#### 📅 ਪਿਛਲੀ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ")
            try:
                my_att = supabase.table("attendance").select("*").eq("staff_name", clean_name).limit(20).execute().data or []
                if my_att: st.dataframe(format_dates_in_df(pd.DataFrame(my_att)[['date', 'in_time', 'out_time', 'status']], ascending=False), hide_index=True, use_container_width=True)
            except: pass

        with att_e_tab2:
            with st.form("emp_manual_att_form", clear_on_submit=True):
                m_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                m_status = st.selectbox("ਕੀ ਲਗਾਉਣਾ ਹੈ?", ["Present", "Absent", "Half Day"])
                m_reason = st.text_input("ਕਾਰਨ (Reason)")
                if st.form_submit_button("ਬੇਨਤੀ ਭੇਜੋ", type="primary"):
                    supabase.table("attendance_requests").insert({"staff_name": clean_name, "date": str(m_date), "requested_status": m_status, "reason": m_reason, "status": "Pending"}).execute()
                    st.success("✅ ਬੇਨਤੀ ਚਲੀ ਗਈ ਹੈ!")

# ==========================================
# 0. HOME PAGE DASHBOARD
# ==========================================
elif st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
    st.markdown("<p style='text-align: center; font-size: 20px; font-weight: bold;'>ਸੈਕਸ਼ਨ ਚੁਣੋ ਜੀ:</p>", unsafe_allow_html=True)
    def render_nav_row(title, buttons_data):
        st.markdown(f"### {title}")
        cols = st.columns(len(buttons_data))
        for i, (btn_label, tab_name, mode_key, mode_val) in enumerate(buttons_data):
            if cols[i].button(btn_label, use_container_width=True, type="primary" if mode_key == "entry_mode" else "secondary"):
                st.session_state.current_tab = tab_name
                if mode_key: st.session_state[mode_key] = mode_val
                st.rerun()

    render_nav_row("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦਾਂ", [("💰 ਨਵਾਂ ਦਾਨ / ਰਸੀਦ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"), ("📦 ਸਮਾਨ ਦਾ ਦਾਨ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)"), ("📉 ਖਰਚਾ (Payment)", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "📉 ਖਰਚਾ (Payment Debit)"), ("🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)")])
    render_nav_row("🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਆਡਿਟ", [("⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"), ("📖 ਮੁੱਖ ਲੈਜ਼ਰ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)"), ("🏦 ਬੈਂਕ ਲੈਜ਼ਰ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)"), ("📁 ਪਾਰਟੀਆਂ (Parties)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)"), ("📊 CA ਐਕਸਪੋਰਟ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)")])
    render_nav_row("📦 ਸਟਾਕ, ਵਿਦਿਆਰਥੀ, ਵਿਧਵਾ ਰਾਸ਼ਨ ਅਤੇ ਪ੍ਰਬੰਧ", [("📦 ਸਟਾਕ ਭੰਡਾਰ", "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)", "other_mode", "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)"), ("🎓 ਵਿਦਿਆਰਥੀ", "🎓 ਵਿਦਿਆਰਥੀ (Students)", None, None), ("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ", "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)", None, None), ("🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ", "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)", None, None)])
    if is_admin and st.button("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ", use_container_width=True): st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"; st.session_state.admin_mode = "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)"; st.rerun()
    elif is_staff and st.button("🗑️ ਡਿਲੀਟ ਬੇਨਤੀ", use_container_width=True): st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"; st.session_state.admin_mode = "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)"; st.rerun()

# ==========================================
# 1. VOUCHER & RECEIPT ENTRY
# ==========================================
elif st.session_state.current_tab == "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)":
    st.header("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦ ਪ੍ਰਬੰਧਨ")
    modes = ["💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)", "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)", "📉 ਖਰਚਾ (Payment Debit)", "🏦 ਬੈਂਕ ਐਂਟਰੀ (Manual Bank Entry)", "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)", "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)"]
    if st.session_state.entry_mode not in modes: st.session_state.entry_mode = modes[0]
    st.session_state.entry_mode = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ ਚੁਣੋ:", modes, index=modes.index(st.session_state.entry_mode), horizontal=True)
    st.markdown("---")

    if st.session_state.entry_mode == "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)":
        if not is_mgmt:
            st.write("### 💰 ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ")
            try: don_data = supabase.table("donations").select("*").limit(100000).execute().data or []
            except: don_data = []
            unique_donors = list({d['name']: d for d in don_data if d.get('name') and str(d.get('name')).strip() != ""}.keys())
            sel_donor = st.selectbox("ਪੁਰਾਣਾ ਦਾਨੀ ਲੱਭੋ", ["➕ ਨਵਾਂ ਦਾਨੀ (New Donor)"] + unique_donors)
            match = next((d for d in reversed(don_data) if d.get('name') == sel_donor), {}) if sel_donor != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else {}
            
            with st.form("donation_form", clear_on_submit=True):
                donor_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ", value=sel_donor if sel_donor != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else "")
                donor_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (WhatsApp ਲਈ ਜ਼ਰੂਰੀ)", value=match.get('phone', ''))
                donor_address = st.text_input("ਪਤਾ", value=match.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'))
                on_account_of = st.text_input("ਕਿਸ ਮੱਦ ਲਈ (e.g. Monthly Donation)")
                rec_no_input = st.number_input("ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1)
                col_m1, col_m2 = st.columns(2)
                with col_m1: amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0); pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Cheque", "NEFT/RTGS"])
                with col_m2: bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ?", BANK_ACCOUNTS); receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                cq_no, cq_bank = "", ""
                if pay_mode == "Cheque":
                    cc1, cc2 = st.columns(2)
                    with cc1: cq_no = st.text_input("ਚੈੱਕ ਨੰਬਰ")
                    with cc2: cq_bank = st.text_input("ਬੈਂਕ ਦਾ ਨਾਮ")
                add_to_mirror = st.checkbox("✅ ਇਸ ਦਾਨ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                submitted = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਤਿਆਰ ਕਰੋ", type="primary")
                
            if submitted and donor_name:
                books = supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book = next((b for b in books if int(b['start_no']) <= int(rec_no_input) <= int(b['end_no'])), None)
                existing_rec = supabase.table("donations").select("id").eq("id", int(rec_no_input)).execute().data
                if not matched_book: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਕਿਸੇ ਵੀ ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif existing_rec: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ!")
                else:
                    collector = matched_book['collector_name']
                    formatted_date = receipt_date.strftime("%Y-%m-%d")
                    supabase.table("donations").insert({"id": int(rec_no_input), "name": donor_name, "phone": donor_phone, "address": donor_address, "amount": amount, "date": formatted_date, "payment_mode": pay_mode, "donation_type": "ਪੈਸੇ (Monetary)", "item_details": "", "bank_account": bank_acc, "on_account_of": on_account_of, "add_to_mirror": add_to_mirror, "collector_name": collector, "cheque_no": cq_no, "cheque_bank": cq_bank}).execute()
                    st.success(f"✅ ਰਸੀਦ #{rec_no_input} ਸੇਵ ਹੋ ਗਈ!")
                    html_file = generate_html_receipt(int(rec_no_input), donor_name, donor_phone, amount, clean_date_to_display(formatted_date), pay_mode, "ਪੈਸੇ (Monetary)", "", bank_acc, on_account_of, collector, donor_address, cq_no, cq_bank)
                    with open(html_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ/ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file, mime="text/html", type="primary")
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ")
            if don_data:
                df_rec = pd.DataFrame([d for d in don_data if d.get('donation_type') == "ਪੈਸੇ (Monetary)"])
                if not df_rec.empty:
                    disp_cols = [c for c in ['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name'] if c in df_rec.columns]
                    df_rec = format_dates_in_df(df_rec[disp_cols], ascending=False)
                    df_rec.insert(0, "Select", False)
                    edited_df = st.data_editor(df_rec, column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=disp_cols, hide_index=True, use_container_width=True, key="editor_recent_monetary")
                    selected_ids = edited_df[edited_df["Select"] == True]['id'].tolist()
                    if selected_ids:
                        for sid in selected_ids:
                            row_data = next(r for r in don_data if r['id'] == sid)
                            h_file = generate_html_receipt(row_data['id'], row_data.get('name',''), row_data.get('phone',''), float(row_data.get('amount',0) or 0), clean_date_to_display(row_data.get('date','')), row_data.get('payment_mode','N/A'), "ਪੈਸੇ (Monetary)", "", row_data.get('bank_account','N/A'), row_data.get('on_account_of',''), row_data.get('collector_name', ''), row_data.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), row_data.get('cheque_no', ''), row_data.get('cheque_bank', ''))
                            with open(h_file, "r", encoding="utf-8") as f: st.download_button(f"🖨️ Print #{row_data['id']}", data=f.read(), file_name=h_file, mime="text/html", key=f"dl_mon_{sid}")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)":
        if not is_mgmt:
            st.write("### 📦 ਸਮਾਨ ਦਾ ਦਾਨ ਦਰਜ ਕਰੋ")
            try: ik_data = supabase.table("donations").select("*").limit(100000).execute().data or []
            except: ik_data = []
            unique_donors_ik = list({d['name']: d for d in ik_data if d.get('name') and str(d.get('name')).strip() != ""}.keys())
            sel_donor_ik = st.selectbox("ਪੁਰਾਣਾ ਦਾਨੀ ਲੱਭੋ", ["➕ ਨਵਾਂ ਦਾਨੀ (New Donor)"] + unique_donors_ik, key="ik_donor_sel")
            match_ik = next((d for d in reversed(ik_data) if d.get('name') == sel_donor_ik), {}) if sel_donor_ik != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else {}
            
            with st.form("inkind_form", clear_on_submit=True):
                donor_name_ik = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ", value=sel_donor_ik if sel_donor_ik != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else "", key="ik_name")
                donor_phone_ik = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional Phone)", value=match_ik.get('phone', ''), key="ik_phone")
                donor_address_ik = st.text_input("ਪਤਾ", value=match_ik.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), key="ik_addr")
                item_details_ik = st.text_input("ਰਸੀਦ 'ਤੇ ਛਾਪਣ ਲਈ ਸਮਾਨ ਦਾ ਵੇਰਵਾ", key="ik_item")
                rec_no_ik = st.number_input("ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, key="ik_rec")
                col_k1, col_k2 = st.columns(2)
                with col_k1: amount_ik = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (₹)", min_value=0.0, key="ik_amt")
                with col_k2: receipt_date_ik = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                add_destination = st.radio("ਦਾਨ ਕੀਤੇ ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ?", ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)"], horizontal=True)
                
                try: stock_opts_ik = [s['item_name'] for s in supabase.table("stock").select("item_name").limit(50000).execute().data] + ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                except: stock_opts_ik = ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                col_s1, col_s2 = st.columns(2)
                with col_s1: s_item_sel_ik = st.selectbox("ਮੌਜੂਦਾ ਲਿਸਟ ਵਿੱਚੋਂ ਚੁਣੋ", stock_opts_ik, key="s_item_sel_ik"); s_qty_ik = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5, key="s_qty_ik")
                with col_s2: s_item_new_ik = st.text_input("ਜਾਂ ਨਵਾਂ ਨਾਮ ਲਿਖੋ", key="s_item_new_ik"); s_unit_ik = st.selectbox("ਇਕਾਈ (Unit)", STOCK_UNITS, key="s_unit_ik")
                s_type_ik = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", ASSET_TYPES, key="s_type_ik")
                submitted_ik = st.form_submit_button("ਸਮਾਨ ਦੀ ਰਸੀਦ ਬਣਾਓ", type="primary")
                
            if submitted_ik and donor_name_ik and item_details_ik:
                final_item_ik = s_item_new_ik.strip() if s_item_sel_ik == "➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ" else s_item_sel_ik.strip()
                is_whole_ik = any(u in s_unit_ik for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                books_ik = supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book_ik = next((b for b in books_ik if int(b['start_no']) <= int(rec_no_ik) <= int(b['end_no'])), None)
                
                if add_destination != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and not final_item_ik: st.error("❌ ਗਲਤੀ: ਕਿਰਪਾ ਕਰਕੇ ਸਮਾਨ ਦਾ ਨਾਮ ਦਿਓ!")
                elif add_destination != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and is_whole_ik and not float(s_qty_ik).is_integer(): st.error(f"❌ ਗਲਤੀ: ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                elif not matched_book_ik: st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif supabase.table("donations").select("id").eq("id", int(rec_no_ik)).execute().data: st.error(f"❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ!")
                else:
                    collector_ik = matched_book_ik['collector_name']
                    formatted_date_ik = receipt_date_ik.strftime("%Y-%m-%d")
                    supabase.table("donations").insert({"id": int(rec_no_ik), "name": donor_name_ik, "phone": donor_phone_ik, "address": donor_address_ik, "amount": amount_ik, "date": formatted_date_ik, "payment_mode": "N/A", "donation_type": "ਸਮਾਨ (In-Kind / Ration)", "item_details": item_details_ik, "bank_account": "N/A", "on_account_of": "ਸਮਾਨ ਦਾਨ", "add_to_mirror": False, "collector_name": collector_ik}).execute()
                    
                    if add_destination == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ (Add to Stock)" and final_item_ik and s_qty_ik > 0:
                        res_stock = supabase.table("stock").select("*").eq("item_name", final_item_ik).execute()
                        if res_stock.data:
                            old_qty, old_val = float(res_stock.data[0].get('quantity', 0)), float(res_stock.data[0].get('estimated_value', 0))
                            supabase.table("stock").update({"quantity": old_qty + s_qty_ik, "estimated_value": round(old_val + amount_ik, 2), "unit": s_unit_ik, "procurement_date": formatted_date_ik, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", final_item_ik).execute()
                        else:
                            supabase.table("stock").insert({"item_name": final_item_ik, "quantity": s_qty_ik, "estimated_value": round(amount_ik, 2), "unit": s_unit_ik, "procurement_date": formatted_date_ik, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()
                        st.success(f"✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ ਸਟਾਕ ਜੁੜ ਗਿਆ!")
                    elif add_destination == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ (Add to Fixed Asset)" and final_item_ik:
                        supabase.table("assets").insert({"name": final_item_ik, "asset_type": s_type_ik, "value": amount_ik, "quantity": s_qty_ik, "date_added": formatted_date_ik}).execute()
                        st.success(f"✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ ਪੱਕੀ ਸੰਪਤੀ ਜੁੜ ਗਈ!")
                    else: st.success(f"✅ ਰਸੀਦ #{rec_no_ik} ਤਿਆਰ ਹੈ।")
                    
                    html_file_ik = generate_html_receipt(int(rec_no_ik), donor_name_ik, donor_phone_ik, amount_ik, clean_date_to_display(formatted_date_ik), "N/A", "ਸਮਾਨ (In-Kind / Ration)", item_details_ik, "N/A", "ਸਮਾਨ ਦਾਨ", collector_ik, donor_address_ik)
                    with open(html_file_ik, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file_ik, mime="text/html", key="ik_dl", type="primary")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ")
            if ik_data: 
                df_ik = pd.DataFrame([d for d in ik_data if d.get('donation_type') == "ਸਮਾਨ (In-Kind / Ration)"])
                if not df_ik.empty:
                    disp_cols_ik = [c for c in ['id', 'date', 'name', 'phone', 'item_details', 'amount'] if c in df_ik.columns]
                    st.dataframe(format_dates_in_df(df_ik[disp_cols_ik], ascending=False), hide_index=True, use_container_width=True)
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📉 ਖਰਚਾ (Payment Debit)":
        if not is_mgmt:
            with st.form("expense_form", clear_on_submit=True):
                st.write("### 📉 ਖਰਚਾ ਜਾਂ ਪੇਮੈਂਟ ਦਰਜ ਕਰੋ")
                desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ")
                cat = st.selectbox("ਕੈਟਾਗਰੀ", [c for c in EXPENSE_CATEGORIES if not c.startswith("---")])
                exp_amount = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ?", BANK_ACCOUNTS)
                exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                add_destination_exp = st.radio("ਖਰੀਦੇ ਗਏ ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ?", ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ"], horizontal=True)
                
                try: stock_opts_exp = [s['item_name'] for s in supabase.table("stock").select("item_name").limit(50000).execute().data] + ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                except: stock_opts_exp = ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                
                col_es1, col_es2 = st.columns(2)
                with col_es1: s_item_sel_exp = st.selectbox("ਮੌਜੂਦਾ ਲਿਸਟ ਵਿੱਚੋਂ ਚੁਣੋ", stock_opts_exp, key="s_item_sel_exp"); s_qty_exp = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5, key="s_qty_exp")
                with col_es2: s_item_new_exp = st.text_input("ਜਾਂ ਨਵਾਂ ਨਾਮ ਲਿਖੋ", key="s_item_new_exp"); s_unit_exp = st.selectbox("ਇਕਾਈ", STOCK_UNITS, key="s_unit_exp")
                s_type_exp = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", ASSET_TYPES, key="s_type_exp")
                submitted_exp = st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ", type="primary")
                
            if submitted_exp and desc:
                final_item_exp = s_item_new_exp.strip() if s_item_sel_exp == "➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ" else s_item_sel_exp.strip()
                is_whole_exp = any(u in s_unit_exp for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                if add_destination_exp != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and not final_item_exp: st.error("❌ ਗਲਤੀ: ਸਮਾਨ ਦਾ ਨਾਮ ਦਿਓ!")
                elif add_destination_exp != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and is_whole_exp and not float(s_qty_exp).is_integer(): st.error(f"❌ ਗਲਤੀ: ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                else:
                    res_ins = supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"), "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp}).execute()
                    inserted_id = res_ins.data[0]['id'] if res_ins.data else "N/A"
                    if add_destination_exp == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ" and final_item_exp and s_qty_exp > 0:
                        res_stock = supabase.table("stock").select("*").eq("item_name", final_item_exp).execute()
                        if res_stock.data:
                            old_qty, old_val = float(res_stock.data[0].get('quantity', 0)), float(res_stock.data[0].get('estimated_value', 0))
                            supabase.table("stock").update({"quantity": old_qty + s_qty_exp, "estimated_value": round(old_val + exp_amount, 2), "unit": s_unit_exp, "procurement_date": exp_date.strftime("%Y-%m-%d"), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", final_item_exp).execute()
                        else:
                            supabase.table("stock").insert({"item_name": final_item_exp, "quantity": s_qty_exp, "estimated_value": round(exp_amount, 2), "unit": s_unit_exp, "procurement_date": exp_date.strftime("%Y-%m-%d"), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()
                        st.success(f"✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ ਸਟਾਕ ਜੁੜ ਗਿਆ!")
                    elif add_destination_exp == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ" and final_item_exp and s_qty_exp > 0:
                        supabase.table("assets").insert({"name": final_item_exp, "asset_type": s_type_exp, "value": exp_amount, "quantity": s_qty_exp, "date_added": str(exp_date)}).execute()
                        st.success(f"✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ ਸੰਪਤੀ ਜੁੜ ਗਈ!")
                    else: st.success(f"✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ!")

                    if inserted_id != "N/A":
                        html_file_exp = generate_html_expense_voucher(inserted_id, desc, exp_amount, clean_date_to_display(exp_date.strftime("%Y-%m-%d")), cat, bank_acc_exp)
                        with open(html_file_exp, "r", encoding="utf-8") as file: st.download_button("🖨️ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_exp, mime="text/html", type="primary")

            st.markdown("---")
            try:
                recents = supabase.table("expenses").select("*").order("id", desc=True).limit(50).execute().data
                if recents: 
                    df_exp_disp = pd.DataFrame(recents)[['id', 'date', 'description', 'amount', 'category', 'bank_account']]
                    df_exp_disp.insert(0, "Select", False)
                    edited_exp_df = st.data_editor(format_dates_in_df(df_exp_disp, ascending=False), column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=['id', 'date', 'description', 'amount', 'category', 'bank_account'], hide_index=True, use_container_width=True, key="editor_recent_expenses")
                    selected_exp_ids = edited_exp_df[edited_exp_df["Select"] == True]['id'].tolist()
                    if selected_exp_ids:
                        for sid in selected_exp_ids:
                            row_data = next(r for r in recents if r['id'] == sid)
                            h_file = generate_html_expense_voucher(row_data['id'], row_data.get('description',''), float(row_data.get('amount',0)), clean_date_to_display(row_data.get('date','')), row_data.get('category',''), row_data.get('bank_account',''))
                            with open(h_file, "r", encoding="utf-8") as f: st.download_button(f"🖨️ Print #{sid}", data=f.read(), file_name=h_file, mime="text/html", key=f"dl_exp_{sid}")
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "🏦 ਬੈਂਕ ਐਂਟਰੀ (Manual Bank Entry)":
        if not is_mgmt:
            with st.form("manual_bank_form", clear_on_submit=True):
                st.write("### 🏦 ਮੈਨੂਅਲ ਬੈਂਕ ਐਂਟਰੀ")
                b_acc = st.selectbox("ਬੈਂਕ ਖਾਤਾ", BANK_ACCOUNTS)
                b_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                b_desc = st.text_input("ਵੇਰਵਾ")
                col1, col2 = st.columns(2)
                with col1: b_type = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ", ["ਖਾਤੇ ਵਿੱਚ ਆਏ (Credit)", "ਖਾਤੇ ਵਿੱਚੋਂ ਕੱਟੇ (Debit)"])
                with col2: b_amt = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary"):
                    if not b_desc: st.error("❌ ਵੇਰਵਾ ਜ਼ਰੂਰੀ ਹੈ!")
                    else:
                        debit_val = b_amt if "Debit" in b_type else 0.0
                        credit_val = b_amt if "Credit" in b_type else 0.0
                        supabase.table("bank_ledger").insert({"txn_date": b_date.strftime("%Y-%m-%d"), "description": b_desc, "bank_name": b_acc, "debit": float(debit_val), "credit": float(credit_val), "balance": 0.0, "source": "Manual Entry"}).execute()
                        st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!")
            st.markdown("---")
            try:
                recents = supabase.table("bank_ledger").select("*").eq("source", "Manual Entry").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(format_dates_in_df(pd.DataFrame(recents)[['id', 'txn_date', 'bank_name', 'description', 'debit', 'credit']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)":
        if not is_mgmt:
            with st.form("party_form", clear_on_submit=True):
                st.write("### 📁 ਨਵੀਂ ਪਾਰਟੀ ਜਾਂ ਵੈਂਡਰ ਬਣਾਓ")
                p_name = st.text_input("ਪਾਰਟੀ ਦਾ ਨਾਮ")
                p_type = st.selectbox("ਖਾਤੇ ਦੀ ਕਿਸਮ", ["Sundry Creditor (ਦੇਣਦਾਰ - ਪੈਸੇ ਦੇਣੇ ਹਨ)", "Sundry Debtor (ਪਾਉਣਦਾਰ - ਪੈਸੇ ਲੈਣੇ ਹਨ)"])
                p_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                p_address = st.text_input("ਪਤਾ")
                p_amount = st.number_input("ਸ਼ੁਰੂਆਤੀ ਬੈਲੇਂਸ (₹)", min_value=0.0)
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and p_name:
                    supabase.table("parties").insert({"name": p_name, "party_type": p_type, "phone": p_phone, "address": p_address, "opening_balance": p_amount, "created_at": str(date.today())}).execute()
                    st.success(f"✅ ਪਾਰਟੀ ਸੇਵ ਹੋ ਗਈ!")
            st.markdown("---")
            try:
                recents = supabase.table("parties").select("*").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(format_dates_in_df(pd.DataFrame(recents)[['id', 'name', 'party_type', 'opening_balance']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)":
        if not is_mgmt:
            with st.form("cheque_form", clear_on_submit=True):
                st.write("### 💳 ਚੈੱਕ ਜਾਰੀ ਕਰਨ ਦੀ ਐਂਟਰੀ")
                cq_no = st.text_input("ਚੈੱਕ ਨੰਬਰ")
                cq_bank = st.selectbox("ਬੈਂਕ ਖਾਤਾ", BANK_ACCOUNTS)
                cq_party = st.text_input("ਕਿਸ ਨੂੰ ਦਿੱਤਾ/ਲਿਆ")
                cq_amt = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                cq_date = st.date_input("ਚੈੱਕ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                cq_status = st.selectbox("ਸਟੇਟਸ", ["Pending (ਕਲੀਅਰ ਹੋਣਾ ਬਾਕੀ)", "Cleared (ਕਲੀਅਰ ਹੋ ਗਿਆ)", "Cancelled (ਰੱਦ ਕੀਤਾ)"])
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and cq_no:
                    supabase.table("cheques").insert({"cheque_no": cq_no, "bank_name": cq_bank, "party_name": cq_party, "amount": cq_amt, "cheque_date": str(cq_date), "status": cq_status}).execute()
                    st.success("✅ ਚੈੱਕ ਸੇਵ ਹੋ ਗਿਆ!")
            st.markdown("---")
            try:
                recents = supabase.table("cheques").select("*").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(format_dates_in_df(pd.DataFrame(recents)[['id', 'cheque_date', 'cheque_no', 'party_name', 'amount', 'status']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)":
        st.write("### 🖨️ ਪੁਰਾਣੀ ਰਸੀਦ ਜਾਂ ਖਰਚਾ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ")
        rep_type = st.radio("ਕੀ ਪ੍ਰਿੰਟ ਕਰਨਾ ਹੈ?", ["ਦਾਨ ਰਸੀਦ (Donation Receipt)", "ਖਰਚਾ ਵਾਊਚਰ (Expense Voucher)"], horizontal=True)
        col_search1, col_search2 = st.columns(2)
        if rep_type == "ਦਾਨ ਰਸੀਦ (Donation Receipt)":
            with col_search1:
                search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ ਭਰੋ", min_value=1, step=1)
                if st.button("🔍 ਰਸੀਦ ਲੱਭੋ", type="primary"):
                    res = supabase.table("donations").select("*").eq("id", search_id).execute()
                    if res.data:
                        rec = res.data[0]
                        html_file_rep = generate_html_receipt(search_id, rec.get('name',''), rec.get('phone',''), rec.get('amount',0), clean_date_to_display(rec.get('date','')), rec.get('payment_mode','N/A'), rec.get('donation_type','ਪੈਸੇ (Monetary)'), rec.get('item_details',''), rec.get('bank_account','N/A'), rec.get('on_account_of',''), rec.get('collector_name', ''), rec.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), rec.get('cheque_no', ''), rec.get('cheque_bank', ''))
                        st.success(f"✅ ਰਸੀਦ ਮਿਲ ਗਈ ਹੈ!")
                        with open(html_file_rep, "r", encoding="utf-8") as file: st.download_button("🖨️ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file_rep, mime="text/html", type="primary")
                    else: st.error("❌ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ।")
            with col_search2:
                search_donor = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਨਾਲ ਖੋਜ ਕਰੋ")
                if search_donor:
                    df_don = pd.DataFrame(supabase.table("donations").select("*").limit(100000).execute().data or [])
                    if not df_don.empty:
                        matches = df_don[df_don['name'].str.contains(search_donor, case=False, na=False)]
                        if not matches.empty: st.dataframe(format_dates_in_df(matches[['id', 'date', 'name', 'phone', 'amount']].copy(), ascending=False), hide_index=True)
                            
        elif rep_type == "ਖਰਚਾ ਵਾਊਚਰ (Expense Voucher)":
            with col_search1:
                search_id_exp = st.number_input("ਵਾਊਚਰ ਨੰਬਰ ਭਰੋ", min_value=1, step=1, key="sch_exp_id")
                if st.button("🔍 ਵਾਊਚਰ ਲੱਭੋ", type="primary"):
                    res = supabase.table("expenses").select("*").eq("id", search_id_exp).execute()
                    if res.data:
                        rec = res.data[0]
                        html_file_rep = generate_html_expense_voucher(search_id_exp, rec.get('description',''), rec.get('amount',0), clean_date_to_display(rec.get('date','')), rec.get('category',''), rec.get('bank_account','N/A'))
                        st.success(f"✅ ਵਾਊਚਰ ਮਿਲ ਗਿਆ ਹੈ!")
                        with open(html_file_rep, "r", encoding="utf-8") as file: st.download_button("🖨️ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_rep, mime="text/html", type="primary")
                    else: st.error("❌ ਵਾਊਚਰ ਨਹੀਂ ਮਿਲਿਆ।")
            with col_search2:
                search_desc = st.text_input("ਵੇਰਵੇ ਨਾਲ ਖੋਜ ਕਰੋ", key="sch_exp_desc")
                if search_desc:
                    df_exp_all = pd.DataFrame(supabase.table("expenses").select("*").limit(100000).execute().data or [])
                    if not df_exp_all.empty:
                        matches = df_exp_all[df_exp_all['description'].str.contains(search_desc, case=False, na=False)]
                        if not matches.empty: st.dataframe(format_dates_in_df(matches[['id', 'date', 'description', 'amount', 'category']].copy(), ascending=False), hide_index=True)

# ==========================================
# 2. LEDGERS, BANK & CA REPORTS
# ==========================================
elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)":
    st.header("🏦 ਖਾਤੇ, ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    modes = ["⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ (Cash & Bank Balances)", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)", "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)", "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"]
    if st.session_state.acc_mode not in modes: st.session_state.acc_mode = modes[0]
    st.session_state.acc_mode = st.radio("ਖਾਤਾ ਚੁਣੋ:", modes, index=modes.index(st.session_state.acc_mode), horizontal=True)
    st.markdown("---")

    don_data = supabase.table("donations").select("*").limit(100000).execute().data or []
    exp_data = supabase.table("expenses").select("*").limit(100000).execute().data or []
    try: ledg_data = supabase.table("bank_ledger").select("*").limit(100000).execute().data or []
    except: ledg_data = []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledg_data)

    if st.session_state.acc_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        assets_data = supabase.table("assets").select("*").limit(100000).execute().data or []
        liab_data = supabase.table("liabilities").select("*").limit(100000).execute().data or []
        df_assets = pd.DataFrame(assets_data) if assets_data else pd.DataFrame(columns=['name', 'value', 'asset_type'])
        df_liab = pd.DataFrame(liab_data) if liab_data else pd.DataFrame(columns=['name', 'value'])
        
        total_income = df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)']['amount'].astype(float).sum() if not df_don.empty else 0.0
        total_income += df_ledg['credit'].astype(float).sum() if not df_ledg.empty and 'credit' in df_ledg.columns else 0.0
        total_expense = df_exp['amount'].astype(float).sum() if not df_exp.empty else 0.0
        total_expense += df_ledg['debit'].astype(float).sum() if not df_ledg.empty and 'debit' in df_ledg.columns else 0.0
        surplus = total_income - total_expense
        
        asset_totals, fixed_assets_val = {}, 0.0
        if not df_assets.empty:
            df_assets['value'] = pd.to_numeric(df_assets['value'], errors='coerce').fillna(0.0)
            df_assets['asset_type'] = df_assets.get('asset_type', 'ਹੋਰ (Other)').fillna('ਹੋਰ (Other)')
            asset_totals = df_assets.groupby('asset_type')['value'].sum().to_dict()
            fixed_assets_val = df_assets['value'].sum()
            
        other_liab_val = pd.to_numeric(df_liab['value'], errors='coerce').fillna(0.0).sum() if not df_liab.empty else 0.0
        
        st.subheader("📊 Income & Expenditure Account")
        inc_exp_html = f"""<table class="report-table"><tr><th>Expenditure (ਖਰਚੇ)</th><th>Amount (₹)</th><th>Income (ਆਮਦਨ)</th><th>Amount (₹)</th></tr>
            <tr><td>Total Expenses & Payments</td><td>{total_expense:,.2f}</td><td>Total Donations & Receipts</td><td>{total_income:,.2f}</td></tr>
            <tr style="font-weight:bold; color: #D92B2B;"><td>Surplus (ਬੱਚਤ)</td><td>{surplus if surplus > 0 else 0:,.2f}</td><td>Deficit (ਘਾਟਾ)</td><td>{abs(surplus) if surplus < 0 else 0:,.2f}</td></tr>
            <tr style="background-color: #F8F1D1; font-weight:bold;"><td>Total</td><td>{max(total_income, total_expense):,.2f}</td><td>Total</td><td>{max(total_income, total_expense):,.2f}</td></tr></table>"""
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        
        bank_balances = get_bank_balances(df_don, df_exp, df_ledg)
        total_assets = fixed_assets_val + sum(bank_balances.values())
        total_liabilities = other_liab_val + surplus
        
        st.markdown("---")
        st.subheader("⚖️ Balance Sheet")
        col_liab, col_assets = st.columns(2)
        with col_liab:
            st.markdown('<div class="bs-box"><div class="bs-header">Liabilities & Funds</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Corpus/Capital Funds & Liab:</span><span>₹ {other_liab_val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Add: Surplus (ਬੱਚਤ):</span><span>₹ {surplus:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Liabilities:</span><span>₹ {total_liabilities:,.2f}</span></div></div>', unsafe_allow_html=True)
        with col_assets:
            st.markdown('<div class="bs-box"><div class="bs-header">Assets (ਸੰਪਤੀ)</div>', unsafe_allow_html=True)
            for atype, aval in asset_totals.items(): st.markdown(f'<div class="bs-row"><span>{atype}:</span><span>₹ {aval:,.2f}</span></div>', unsafe_allow_html=True)
            for b, val in bank_balances.items(): st.markdown(f'<div class="bs-row"><span>{b}:</span><span>₹ {val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Assets:</span><span>₹ {total_assets:,.2f}</span></div></div>', unsafe_allow_html=True)
            
        assets_breakdown = "".join([f"<p>{k}: {v:,.2f}</p>" for k, v in asset_totals.items()])
        full_html = f"<h3>Income & Expenditure Account</h3>{inc_exp_html}<br><h3>Balance Sheet</h3><div style='width:100%;'><div class='bs-box'><h4>Liabilities</h4><p>Funds & Liab: {other_liab_val:,.2f}</p><p>Surplus: {surplus:,.2f}</p><hr><p><b>Total: {total_liabilities:,.2f}</b></p></div><div class='bs-box'><h4>Assets</h4>{assets_breakdown}<p>Bank/Cash: {sum(bank_balances.values()):,.2f}</p><hr><p><b>Total: {total_assets:,.2f}</b></p></div></div>"
        fin_report = generate_html_report("Financial Statements", full_html)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

        if is_admin:
            st.markdown("---")
            st.subheader("⚙️ ਸੰਪਤੀ ਅਤੇ ਫੰਡ ਜੋੜੋ (Add Fixed Assets / Funds)")
            ac1, ac2 = st.columns(2)
            with ac1:
                with st.form("add_asset"):
                    a_name = st.text_input("ਸੰਪਤੀ ਦਾ ਨਾਮ")
                    a_type = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", ASSET_TYPES)
                    a_qty = st.number_input("ਮਾਤਰਾ", min_value=1.0, step=1.0)
                    a_val = st.number_input("ਕੁੱਲ ਮੁੱਲ (₹)", min_value=0.0)
                    a_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    if st.form_submit_button("ਸੰਪਤੀ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("assets").insert({"name": a_name, "asset_type": a_type, "quantity": a_qty, "value": a_val, "date_added": str(a_date)}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()
            with ac2:
                with st.form("add_liab"):
                    l_name = st.text_input("ਫੰਡ ਦਾ ਨਾਮ")
                    l_val = st.number_input("ਮੁੱਲ (₹)", min_value=0.0)
                    if st.form_submit_button("ਫੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        supabase.table("liabilities").insert({"name": l_name, "value": l_val, "date_added": str(date.today())}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()

    elif st.session_state.acc_mode == "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ (Cash & Bank Balances)":
        st.write("### 💰 ਮੌਜੂਦਾ ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ")
        bank_balances = get_bank_balances(df_don, df_exp, df_ledg)
        df_bals = pd.DataFrame(list(bank_balances.items()), columns=["ਖਾਤਾ (Account Name)", "ਮੌਜੂਦਾ ਬੈਲੇਂਸ (Current Balance ₹)"])
        total_bal = df_bals["ਮੌਜੂਦਾ ਬੈਲੇਂਸ (Current Balance ₹)"].sum()
        
        st.dataframe(df_bals.style.format({'ਮੌਜੂਦਾ ਬੈਲੇਂਸ (Current Balance ₹)': '{:,.2f}'}), hide_index=True, use_container_width=True)
        st.markdown(f"**ਕੁੱਲ ਬੈਲੇਂਸ: ₹ {total_bal:,.2f}**")
        rep_file = generate_html_report("Cash & Bank Balances", df_bals.to_html(index=False, border=1, classes='report-table') + f"<br><h4 style='text-align: right; color: #D92B2B;'>ਕੁੱਲ: Rs. {total_bal:,.2f}</h4>")
        with open(rep_file, "r", encoding="utf-8") as f: st.download_button("🖨️ ਬੈਲੇਂਸ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=rep_file, mime="text/html", type="primary")

    elif st.session_state.acc_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)":
        st.write("### 📖 ਮੁੱਖ ਲੈਜ਼ਰ / ਡੇਅ ਬੁੱਕ")
        filter_opt = st.radio("ਫਿਲਟਰ (Filter):", ["ਸਾਰੀਆਂ ਐਂਟਰੀਆਂ (All)", "ਸਿਰਫ਼ ਦਾਨ (Donations)", "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)", "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)"], horizontal=True)
        show_all_dates_md = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True, key="chk_all_md")
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all_dates_md)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all_dates_md)

        df_main = get_ledger_data(df_don, df_exp, df_ledg)
        if not df_main.empty:
            df_main['DateObj'] = df_main['Date'].apply(parse_date_to_obj).fillna(date.today())
            df_main = df_main.sort_values(by=['DateObj', 'ID'], ascending=True) 
            
            if show_all_dates_md:
                df_period = df_main.copy()
                running_bal = 0.0
            else:
                df_before = df_main[df_main['DateObj'] < start_date]
                opening_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
                df_period = df_main[(df_main['DateObj'] >= start_date) & (df_main['DateObj'] <= end_date)].copy()
                running_bal = opening_bal

            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(clean_date_to_display)
            
            if filter_opt == "ਸਿਰਫ਼ ਦਾਨ (Donations)": df_period = df_period[df_period['Source'] == 'App (Donation)']
            elif filter_opt == "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)": df_period = df_period[df_period['Source'] == 'App (Expense)']
            elif filter_opt == "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)": df_period = df_period[~df_period['Source'].str.contains('App', na=False)]
            
            df_disp = df_period[['ID', 'Date', 'Description', 'Account', 'Source', 'Credit', 'Debit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']]
            st.dataframe(df_disp.style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}), hide_index=True, use_container_width=True)
            report_file_main = generate_html_report(f"ਮੁੱਖ ਲੈਜ਼ਰ ({filter_opt})", df_disp.to_html(index=False, border=1, classes='report-table'), landscape=True)
            with open(report_file_main, "r", encoding="utf-8") as file: st.download_button("🖨️ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_main, mime="text/html", type="primary")

    elif st.session_state.acc_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ", BANK_ACCOUNTS)
        show_all_dates_bk = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True, key="chk_all_bk")
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all_dates_bk)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all_dates_bk)

        df_compiled = get_ledger_data(df_don, df_exp, df_ledg, target_bank=selected_bank)
        if not df_compiled.empty:
            df_compiled['DateObj'] = df_compiled['Date'].apply(parse_date_to_obj).fillna(date.today())
            df_compiled = df_compiled.sort_values(by=['DateObj', 'ID'], ascending=True)
            
            if show_all_dates_bk:
                df_period = df_compiled.copy()
                running_bal = 0.0
            else:
                df_before = df_compiled[df_compiled['DateObj'] < start_date]
                opening_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
                df_period = df_compiled[(df_compiled['DateObj'] >= start_date) & (df_compiled['DateObj'] <= end_date)].copy()
                running_bal = opening_bal

            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(clean_date_to_display)
            
            df_disp_bank = df_period[['ID', 'Date', 'Description', 'Source', 'Credit', 'Debit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']]
            st.dataframe(df_disp_bank.style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}), hide_index=True, use_container_width=True)
            
            st.markdown("---")
            report_file_bank = generate_html_report(f"ਬੈਂਕ ਲੈਜ਼ਰ - {selected_bank}", df_disp_bank.to_html(index=False, border=1, classes='report-table'), landscape=True)
            with open(report_file_bank, "r", encoding="utf-8") as file: st.download_button("🖨️ ਬੈਂਕ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_bank, mime="text/html", type="primary")
        else: st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)":
        st.write("### 📊 CA ਆਡਿਟ ਅਤੇ ਐਕਸਲ ਬੈਕਅੱਪ")
        st.info("ਆਪਣੇ CA ਨੂੰ ਆਡਿਟ ਲਈ ਇਹ ਪੂਰਾ ਮਲਟੀ-ਸ਼ੀਟ ਐਕਸਲ ਡਾਟਾਬੇਸ ਭੇਜੋ।")
        if st.button("📥 CA ਐਕਸਲ ਬੈਕਅੱਪ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                format_dates_in_df(pd.DataFrame(supabase.table("donations").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Donations_Receipts', index=False)
                format_dates_in_df(pd.DataFrame(supabase.table("expenses").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Expenses', index=False)
                try: format_dates_in_df(pd.DataFrame(supabase.table("bank_ledger").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Bank_Ledger', index=False)
                except: pass
                try: format_dates_in_df(pd.DataFrame(supabase.table("parties").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Creditors_Debtors', index=False)
                except: pass
                try: format_dates_in_df(pd.DataFrame(supabase.table("cheques").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Cheque_Register', index=False)
                except: pass
                format_dates_in_df(pd.DataFrame(supabase.table("stock").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Stock', index=False)
                try: format_dates_in_df(pd.DataFrame(supabase.table("assets").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Fixed_Assets', index=False)
                except: pass
                format_dates_in_df(pd.DataFrame(supabase.table("students").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Students', index=False)
                try: format_dates_in_df(pd.DataFrame(supabase.table("widows").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Widows', index=False)
                except: pass
                try: format_dates_in_df(pd.DataFrame(supabase.table("ration_distribution").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Ration', index=False)
                except: pass
                try: format_dates_in_df(pd.DataFrame(supabase.table("stock_usage").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Stock_Usage', index=False)
                except: pass
                format_dates_in_df(pd.DataFrame(supabase.table("receipt_books").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Receipt_Books', index=False)
            st.download_button("📥 ਕਲਿੱਕ ਕਰਕੇ ਡਾਊਨਲੋਡ ਕਰੋ", data=buffer.getvalue(), file_name=f"CA_Audit_Data_{datetime.now().strftime('%d-%m-%Y')}.xlsx", type="primary")

# ==========================================
# 3. STOCK & RECEIPT BOOKS
# ==========================================
elif st.session_state.current_tab == "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)":
    st.header("📦 ਸਟਾਕ ਅਤੇ ਰਸੀਦ ਕਿਤਾਬਾਂ (Stock & Books)")
    modes = ["📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)", "📤 ਸਟਾਕ ਵੰਡ (Stock Issuance)", "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"]
    if st.session_state.other_mode not in modes: st.session_state.other_mode = modes[0]
    st.session_state.other_mode = st.radio("ਸੈਕਸ਼ਨ ਚੁਣੋ:", modes, index=modes.index(st.session_state.other_mode), horizontal=True)
    st.markdown("---")

    if st.session_state.other_mode == "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)":
        st.write("### 📑 ਮੌਜੂਦਾ ਸਟਾਕ ਰਿਪੋਰਟ")
        try: stock_res = supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
        except: stock_res = []
        if stock_res:
            df_stock = pd.DataFrame(stock_res)
            disp_cols = [c for c in ['item_name', 'quantity', 'unit', 'estimated_value', 'procurement_date', 'last_updated'] if c in df_stock.columns]
            st.dataframe(format_dates_in_df(df_stock[disp_cols]), hide_index=True, use_container_width=True)
            report_file_stock = generate_html_report("Current Stock Inventory", format_dates_in_df(df_stock[disp_cols]).to_html(index=False, border=1, classes='report-table'))
            with open(report_file_stock, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸਟਾਕ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stock, mime="text/html")
        else: st.warning("ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਸਮਾਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.other_mode == "📤 ਸਟਾਕ ਵੰਡ (Stock Issuance)":
        col1, col2 = st.columns([1, 2])
        with col1:
            if not is_mgmt:
                with st.form("stock_issue_form", clear_on_submit=True):
                    st.write("### 📤 ਸਟਾਕ ਵੰਡੋ ਜਾਂ ਵਰਤੋ")
                    try: stock_res = supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
                    except: stock_res = []
                    if stock_res:
                        s_dict = {s['item_name']: float(s.get('quantity', 0) or 0) for s in stock_res}
                        s_units = {s['item_name']: s.get('unit', '') for s in stock_res}
                        s_items = list(s_dict.keys())
                        item_name = st.selectbox("ਕਿਹੜਾ ਸਮਾਨ ਵੰਡਣਾ ਹੈ?", s_items)
                        item_unit = s_units.get(item_name, '')
                        is_whole_issue = any(u in item_unit for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                        qty = st.number_input(f"ਮਾਤਰਾ ({item_unit}) - ਮੌਜੂਦ: {s_dict.get(item_name, 0)}", min_value=0.5 if not is_whole_issue else 1.0, step=1.0 if is_whole_issue else 0.5)
                        purpose_input = st.text_input("ਵਰਤੋਂ ਦਾ ਕਾਰਨ / ਕਿਸਨੂੰ ਦਿੱਤਾ?")
                        proc_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                        if st.form_submit_button("ਸਟਾਕ ਜਾਰੀ ਕਰੋ", type="primary"):
                            if not purpose_input.strip(): st.error("❌ ਕਿਰਪਾ ਕਰਕੇ ਵਰਤੋਂ ਦਾ ਕਾਰਨ ਦੱਸੋ!")
                            elif is_whole_issue and not float(qty).is_integer(): st.error(f"❌ ਗਲਤੀ: '{item_unit}' ਲਈ ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                            else:
                                old_qty = s_dict.get(item_name, 0)
                                if qty > old_qty: st.error(f"❌ ਗਲਤੀ: ਸਟਾਕ ਵਿੱਚ ਸਿਰਫ਼ {old_qty} ਮਾਤਰਾ ਬਾਕੀ ਹੈ!")
                                else:
                                    new_qty = old_qty - qty
                                    curr_stock = supabase.table("stock").select("*").eq("item_name", item_name).execute().data
                                    old_val = float(curr_stock[0].get('estimated_value', 0) or 0) if curr_stock else 0.0
                                    new_val = (old_val * (new_qty / old_qty)) if old_qty > 0 else 0.0
                                    supabase.table("stock").update({"quantity": new_qty, "estimated_value": round(new_val, 2), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", item_name).execute()
                                    supabase.table("stock_usage").insert({"item_name": item_name, "quantity": qty, "unit": item_unit, "purpose": purpose_input, "usage_date": str(proc_date)}).execute()
                                    st.success(f"✅ '{item_name}' ਜਾਰੀ ਕਰ ਦਿੱਤਾ ਗਿਆ ਹੈ!"); time.sleep(1.2); st.rerun()
                    else: st.warning("ਸਟਾਕ ਖਾਲੀ ਹੈ।")
        with col2:
            st.write("### 📝 ਵਰਤੋਂ ਦਾ ਰਿਕਾਰਡ")
            try: usage_res = supabase.table("stock_usage").select("*").order("id", desc=True).limit(50).execute().data or []
            except: usage_res = []
            if usage_res:
                df_usage = pd.DataFrame(usage_res)[['usage_date', 'item_name', 'quantity', 'unit', 'purpose']]
                st.dataframe(format_dates_in_df(df_usage, ascending=False), hide_index=True, use_container_width=True)
            else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")

    elif st.session_state.other_mode == "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)":
        if is_admin:
            with st.form("book_issue_form", clear_on_submit=True):
                st.write("### 📖 ਨਵੀਂ ਰਸੀਦ ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ")
                col_b1, col_b2 = st.columns(2)
                with col_b1: collector_input = st.text_input("ਕਲੈਕਟਰ ਦਾ ਨਾਮ"); start_ser = st.number_input("ਸ਼ੁਰੂਆਤੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=1)
                with col_b2: end_ser = st.number_input("ਆਖਰੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=100); issue_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                if st.form_submit_button("ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ (Issue)", type="primary"):
                    if collector_input and end_ser >= start_ser:
                        existing_books = supabase.table("receipt_books").select("*").execute().data or []
                        if any(int(start_ser) <= int(b['end_no']) and int(end_ser) >= int(b['start_no']) for b in existing_books): st.error("❌ ਗਲਤੀ: ਇਹ ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਜਾਰੀ ਕੀਤੇ ਜਾ ਚੁੱਕੇ ਹਨ!")
                        else:
                            supabase.table("receipt_books").insert({"collector_name": collector_input, "start_no": int(start_ser), "end_no": int(end_ser), "issued_date": issue_date.strftime("%Y-%m-%d"), "status": "Active"}).execute()
                            st.success("✅ ਕਿਤਾਬ ਜਾਰੀ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!")
        st.write("### 📑 ਜਾਰੀ ਕੀਤੀਆਂ ਗਈਆਂ ਕਿਤਾਬਾਂ")
        try: books_all = supabase.table("receipt_books").select("*").order("id", desc=True).limit(100000).execute().data or []
        except: books_all = []
        if books_all:
            df_books = pd.DataFrame(books_all)[['collector_name', 'start_no', 'end_no', 'issued_date', 'status']]
            st.dataframe(format_dates_in_df(df_books, ascending=False), hide_index=True, use_container_width=True)
            report_file_books = generate_html_report("Issued Receipt Books", format_dates_in_df(df_books).to_html(index=False, border=1, classes='report-table'))
            with open(report_file_books, "r", encoding="utf-8") as file: st.download_button("🖨️ ਕਿਤਾਬਾਂ ਦੀ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_books, mime="text/html")

# ==========================================
# 4. STUDENTS
# ==========================================
elif st.session_state.current_tab == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
    st.header("🎓 ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ")
    s_tab1, s_tab2 = st.tabs(["➕ ਨਵਾਂ ਵਿਦਿਆਰਥੀ ਦਰਜ ਕਰੋ", "📋 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ"])
    
    with s_tab1:
        if not is_mgmt:
            with st.form("student_form", clear_on_submit=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1: stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ"); stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                with col_s2: stu_course = st.selectbox("ਕਲਾਸ", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"]); join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                s_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and stu_name:
                    supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ", "photo_base64": compress_image(s_photo)}).execute()
                    st.success(f"✅ '{stu_name}' ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    with s_tab2:
        st.write("### 📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ")
        try: student_data = supabase.table("students").select("*").limit(100000).execute().data or []
        except: student_data = []
        if student_data:
            df_stu = pd.DataFrame(student_data)
            display_cols = [c for c in ['name', 'phone', 'course', 'join_date', 'pass_date'] if c in df_stu.columns]
            st.dataframe(format_dates_in_df(df_stu[display_cols], ascending=False), hide_index=True, use_container_width=True)
            
            df_print = format_dates_in_df(df_stu, ascending=False).copy()
            df_print['ਫੋਟੋ (Photo)'] = df_print['photo_base64'].apply(lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo') if 'photo_base64' in df_print.columns else 'No Photo'
            print_cols_map = {'name': 'ਨਾਮ', 'phone': 'ਫ਼ੋਨ', 'course': 'ਕਲਾਸ', 'join_date': 'ਦਾਖਲਾ ਮਿਤੀ', 'pass_date': 'ਸਟੇਟਸ', 'ਫੋਟੋ (Photo)': 'ਫੋਟੋ'}
            df_print = df_print.rename(columns={k: v for k, v in print_cols_map.items() if k in df_print.columns})
            html_table = df_print[[v for k, v in print_cols_map.items() if v in df_print.columns]].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_stu = generate_html_report_landscape("Students List", html_table)
            with open(report_file_stu, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stu, mime="text/html", type="primary")
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

# ==========================================
# 5. WIDOWS RATION
# ==========================================
elif st.session_state.current_tab == "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)":
    st.header("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ ਡਾਟਾਬੇਸ")
    w_tab1, w_tab2, w_tab3 = st.tabs(["➕ ਨਵਾਂ ਕਾਰਡ ਬਣਾਓ", "📋 ਡਾਟਾਬੇਸ ਸੂਚੀ", "🛍️ ਰਾਸ਼ਨ ਵੰਡ"])
    
    with w_tab1:
        if not is_mgmt:
            with st.form("widow_form", clear_on_submit=True):
                c_w1, c_w2, c_w3 = st.columns(3)
                with c_w1: w_form_no = st.text_input("ਫਾਰਮ ਨੰ:"); w_name = st.text_input("ਨਾਮ ਬੀਬੀ: *ਜ਼ਰੂਰੀ*"); w_husband = st.text_input("ਪਤੀ ਦਾ ਨਾਮ:"); w_death_date = st.text_input("ਪਤੀ ਦੀ ਮੌਤ ਦੀ ਤਾਰੀਖ:")
                with c_w2: w_card_no = st.text_input("ਕਾਰਡ ਨੰ:"); w_age = st.text_input("ਉਮਰ / ਸਾਲ:"); w_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ: *ਜ਼ਰੂਰੀ*"); w_issued_by = st.text_input("ਜਾਰੀ ਕਰਤਾ:")
                with c_w3: w_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg']); w_card_date = st.date_input("ਸ਼ੁਰੂਆਤ ਮਿਤੀ:", value=date.today(), format="DD/MM/YYYY")
                w_address = st.text_area("ਪਤਾ (Address):")
                cb1, cb2 = st.columns(2)
                with cb1: w_boys = st.text_area("ਲੜਕੇ (ਉਮਰ, ਕਲਾਸ):")
                with cb2: w_girls = st.text_area("ਲੜਕੀਆਂ (ਉਮਰ, ਕਲਾਸ):")
                
                if st.form_submit_button("ਕਾਰਡ ਸੇਵ ਕਰੋ", type="primary") and w_name:
                    supabase.table("widows").insert({"form_no": w_form_no, "card_no": w_card_no, "name": w_name, "age": w_age, "husband_name": w_husband, "husband_death_date": w_death_date, "phone": w_phone, "address": w_address, "boys_details": w_boys, "girls_details": w_girls, "issued_by": w_issued_by, "join_date": str(w_card_date), "photo_base64": compress_image(w_photo)}).execute()
                    st.success(f"✅ '{w_name}' ਦਾ ਕਾਰਡ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ!")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    with w_tab2:
        st.write("### 📑 ਰਜਿਸਟਰਡ ਵਿਧਵਾਵਾਂ ਦੀ ਸੂਚੀ")
        try: widows_data = supabase.table("widows").select("*").limit(100000).execute().data or []
        except: widows_data = []
        if widows_data:
            df_w = pd.DataFrame(widows_data)
            display_cols = [c for c in ['card_no', 'name', 'age', 'husband_name', 'phone', 'address', 'join_date'] if c in df_w.columns]
            st.dataframe(format_dates_in_df(df_w[display_cols], ascending=False), hide_index=True, use_container_width=True)
            
            df_print_w = format_dates_in_df(df_w, ascending=False).copy()
            df_print_w['ਫੋਟੋ'] = df_print_w['photo_base64'].apply(lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo') if 'photo_base64' in df_print_w.columns else 'No Photo'
            print_cols_map_w = {'card_no': 'ਕਾਰਡ ਨੰ', 'name': 'ਨਾਮ', 'age': 'ਉਮਰ', 'husband_name': 'ਪਤੀ', 'phone': 'ਫ਼ੋਨ', 'address': 'ਪਤਾ', 'ਫੋਟੋ': 'ਫੋਟੋ'}
            df_print_w = df_print_w.rename(columns={k: v for k, v in print_cols_map_w.items() if k in df_print_w.columns})
            html_table_w = df_print_w[[v for k, v in print_cols_map_w.items() if v in df_print_w.columns]].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_w = generate_html_report_landscape("Widows Database", html_table_w)
            with open(report_file_w, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_w, mime="text/html", type="primary")
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    with w_tab3:
        st.write("### 🛍️ ਮਹੀਨਾਵਾਰ ਰਾਸ਼ਨ ਵੰਡ")
        try: widows_list = supabase.table("widows").select("*").limit(100000).execute().data or []
        except: widows_list = []
        try: stock_list = supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
        except: stock_list = []
            
        if not widows_list: st.warning("⚠️ ਪਹਿਲਾਂ ਵਿਧਵਾਵਾਂ ਦਾ ਪ੍ਰੋਫਾਈਲ ਦਰਜ ਕਰੋ।")
        elif not stock_list: st.warning("⚠️ ਸਟਾਕ ਖਾਲੀ ਹੈ।")
        else:
            if not is_mgmt:
                w_names = [f"ਕਾਰਡ {w.get('card_no','-')} - {w.get('name','Unknown')} ({w.get('phone','')})" for w in widows_list]
                s_dict = {s['item_name']: float(s.get('quantity', 0) or 0) for s in stock_list}
                with st.form("ration_dist_form"):
                    col1, col2 = st.columns(2)
                    with col1: selected_widow = st.selectbox("ਕਿਸ ਨੂੰ ਰਾਸ਼ਨ ਦਿੱਤਾ?", w_names); dist_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    with col2: selected_item = st.selectbox("ਕਿਹੜਾ ਸਮਾਨ ਦਿੱਤਾ?", list(s_dict.keys())); qty_to_give = st.number_input(f"ਮਾਤਰਾ - ਸਟਾਕ ਮੌਜੂਦ: {s_dict.get(selected_item, 0)}", min_value=0.5, step=0.5)
                    if st.form_submit_button("ਰਾਸ਼ਨ ਵੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        old_qty = s_dict.get(selected_item, 0)
                        if qty_to_give > old_qty: st.error(f"❌ ਗਲਤੀ: ਸਟਾਕ ਵਿੱਚ ਸਿਰਫ਼ {old_qty} ਮਾਤਰਾ ਬਾਕੀ ਹੈ!")
                        else:
                            new_qty = max(0.0, old_qty - qty_to_give)
                            curr_stock = supabase.table("stock").select("*").eq("item_name", selected_item).execute().data
                            if curr_stock:
                                curr_val = float(curr_stock[0].get('estimated_value', 0) or 0)
                                supabase.table("stock").update({"quantity": new_qty, "estimated_value": round((curr_val * (new_qty / old_qty)) if old_qty > 0 else 0.0, 2), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", selected_item).execute()
                                supabase.table("stock_usage").insert({"item_name": selected_item, "quantity": qty_to_give, "unit": curr_stock[0].get('unit', ''), "purpose": f"Ration to: {selected_widow}", "usage_date": str(dist_date)}).execute()
                            widow_just_name = selected_widow.split(" - ")[1].split(" (")[0] if " - " in selected_widow else selected_widow
                            supabase.table("ration_distribution").insert({"widow_name": widow_just_name, "item_name": selected_item, "quantity": qty_to_give, "distribution_date": str(dist_date)}).execute()
                            st.success(f"✅ {widow_just_name} ਨੂੰ {qty_to_give} {selected_item} ਦੇ ਦਿੱਤਾ ਗਿਆ ਹੈ!"); time.sleep(1.5); st.rerun()
                            
        st.markdown("---")
        st.write("#### 📑 ਪਿਛਲੀ ਰਾਸ਼ਨ ਵੰਡ ਦਾ ਰਿਕਾਰਡ")
        try: dist_data = supabase.table("ration_distribution").select("*").order("id", desc=True).limit(50).execute().data or []
        except: dist_data = []
        if dist_data: st.dataframe(format_dates_in_df(pd.DataFrame(dist_data)[['id', 'distribution_date', 'widow_name', 'item_name', 'quantity']], ascending=False), hide_index=True, use_container_width=True)

# ==========================================
# 🧑‍💼 STAFF & ATTENDANCE MANAGEMENT
# ==========================================
elif st.session_state.current_tab == "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)":
    st.header("🧑‍💼 ਸਟਾਫ ਮੈਨੇਜਮੈਂਟ ਅਤੇ ਹਾਜ਼ਰੀ")
    att_tabs = st.tabs(["👤 ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Profiles)", "🛡️ ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ (Admin Approvals)", "📋 ਸਭ ਦੀ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ (Monthly Report)"])
    
    with att_tabs[0]:
        col_st1, col_st2 = st.columns([1, 2])
        with col_st1:
            if is_admin or is_mgmt:
                with st.form("staff_profile_form", clear_on_submit=True):
                    st.write("### ➕ ਨਵਾਂ ਸਟਾਫ ਦਰਜ ਕਰੋ")
                    st_name = st.text_input("ਸਟਾਫ ਦਾ ਨਾਮ *ਜ਼ਰੂਰੀ*")
                    st_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                    st_role = st.selectbox("ਡਿਊਟੀ / ਅਹੁਦਾ", ["ਮੈਨੇਜਰ", "ਅਧਿਆਪਕ", "ਕਲਰਕ", "ਸੇਵਾਦਾਰ", "ਡਰਾਈਵਰ", "ਹੋਰ"])
                    st_login = st.selectbox("ਲਾਗਇਨ ਆਈ.ਡੀ", ["ਕੋਈ ਨਹੀਂ (None)", "emp1", "emp2", "emp3", "emp4", "emp5"])
                    st_join = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    st_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg'])
                    if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and st_name:
                        supabase.table("staff_profiles").insert({"name": st_name, "phone": st_phone, "role": st_role, "join_date": str(st_join), "photo_base64": compress_image(st_photo), "login_id": st_login if "emp" in st_login else ""}).execute()
                        st.success(f"✅ '{st_name}' ਸੇਵ ਹੋ ਗਿਆ!")
            else: st.info("⚠️ ਸਿਰਫ਼ ਐਡਮਿਨ ਲਈ।")
                
        with col_st2:
            st.write("### 📋 ਸਟਾਫ ਦੀ ਸੂਚੀ")
            try: staff_data = supabase.table("staff_profiles").select("*").limit(100000).execute().data or []
            except: staff_data = []
            if staff_data: st.dataframe(format_dates_in_df(pd.DataFrame(staff_data)[['name', 'phone', 'role', 'login_id', 'join_date']], ascending=False), hide_index=True, use_container_width=True)

    with att_tabs[1]:
        st.write("### 🛡️ ਸਟਾਫ ਦੀਆਂ ਪੈਂਡਿੰਗ ਹਾਜ਼ਰੀ ਬੇਨਤੀਆਂ")
        try: att_reqs = supabase.table("attendance_requests").select("*").eq("status", "Pending").limit(100000).execute().data or []
        except: att_reqs = []
        if att_reqs:
            st.dataframe(format_dates_in_df(pd.DataFrame(att_reqs)[['id', 'staff_name', 'date', 'requested_status', 'reason', 'created_at']], ascending=False), hide_index=True, use_container_width=True)
            req_dict = {f"ID: {r.get('id','')} - {r.get('staff_name','')} ({clean_date_to_display(r.get('date',''))} : {r.get('requested_status','')})": r for r in att_reqs}
            sel_req_str = st.selectbox("ਬੇਨਤੀ ਚੁਣੋ", list(req_dict.keys()))
            if sel_req_str:
                target_r = req_dict[sel_req_str]
                col_aa, col_ar = st.columns(2)
                with col_aa:
                    if st.button("✅ ਹਾਜ਼ਰੀ ਮਨਜ਼ੂਰ ਕਰੋ", type="primary"):
                        existing = supabase.table("attendance").select("*").eq("staff_name", target_r['staff_name']).eq("date", target_r['date']).execute().data
                        if existing: supabase.table("attendance").update({"status": target_r['requested_status']}).eq("id", existing[0]['id']).execute()
                        else: supabase.table("attendance").insert({"staff_name": target_r['staff_name'], "date": target_r['date'], "in_time": "Manual", "out_time": "Manual", "status": target_r['requested_status']}).execute()
                        supabase.table("attendance_requests").update({"status": "Approved"}).eq("id", target_r['id']).execute()
                        st.success("✅ ਹਾਜ਼ਰੀ ਲੱਗ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                with col_ar:
                    if st.button("❌ ਬੇਨਤੀ ਰੱਦ ਕਰੋ"):
                        supabase.table("attendance_requests").update({"status": "Rejected"}).eq("id", target_r['id']).execute()
                        st.error("❌ ਰੱਦ ਕੀਤੀ ਗਈ!"); time.sleep(1.5); st.rerun()
        else: st.info("ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")

    with att_tabs[2]:
        st.write("### 📅 ਮਹੀਨਾਵਾਰ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ")
        col_m1, col_m2 = st.columns(2)
        with col_m1: sel_month = st.selectbox("ਮਹੀਨਾ (Month)", range(1, 13), index=date.today().month - 1)
        with col_m2: sel_year = st.selectbox("ਸਾਲ (Year)", range(2024, 2035), index=date.today().year - 2024)
        num_days = calendar.monthrange(sel_year, sel_month)[1]
        
        try:
            all_att = supabase.table("attendance").select("*").gte("date", f"{sel_year}-{sel_month:02d}-01").lte("date", f"{sel_year}-{sel_month:02d}-{num_days:02d}").limit(100000).execute().data or []
            if all_att:
                df_att = pd.DataFrame(all_att)
                df_att['date_obj'] = df_att['date'].apply(parse_date_to_obj)
                df_att = df_att.dropna(subset=['date_obj'])
                df_att['day'] = df_att['date_obj'].apply(lambda x: x.day)
                def get_status_code(s):
                    s = str(s).lower()
                    if "present" in s or "ਹਾਜ਼ਰ" in s: return "P"
                    if "absent" in s or "ਛੁੱਟੀ" in s or "ਗੈਰ" in s: return "A"
                    if "half" in s or "ਅੱਧਾ" in s: return "HD"
                    return "P"
                df_att['status_code'] = df_att['status'].apply(get_status_code)
                pivot_df = df_att.pivot_table(index='staff_name', columns='day', values='status_code', aggfunc='last').reindex(columns=list(range(1, num_days + 1))).fillna("-")
                pivot_df['Total P'] = (pivot_df[list(range(1, num_days + 1))] == 'P').sum(axis=1) + ((pivot_df[list(range(1, num_days + 1))] == 'HD').sum(axis=1) * 0.5)
                pivot_df['Total A'] = (pivot_df[list(range(1, num_days + 1))] == 'A').sum(axis=1)
                st.dataframe(pivot_df.reset_index(), hide_index=True, use_container_width=True)
            else: st.info("ਇਸ ਮਹੀਨੇ ਦਾ ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")
        except: pass

# ==========================================
# 6. ADMIN & BULK UPLOAD MANAGEMENT
# ==========================================
elif st.session_state.current_tab == "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)":
    st.header("⚙️ ਐਡਮਿਨ, ਡਿਲੀਟ ਅਤੇ ਸੋਧ (Edit) ਸਿਸਟਮ")
    modes = ["📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)", "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"] if is_admin else ["🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
    if st.session_state.admin_mode not in modes: st.session_state.admin_mode = modes[0]
    st.session_state.admin_mode = st.radio("ਐਡਮਿਨ ਟੂਲ ਚੁਣੋ:", modes, index=modes.index(st.session_state.admin_mode), horizontal=True)
    st.markdown("---")
    
    t_map = {"ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", "ਪਾਰਟੀ (Party)": "parties", "ਚੈੱਕ (Cheque)": "cheques", "ਸੰਪਤੀ (Asset)": "assets", "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", "ਸਟਾਕ ਵਰਤੋਂ (Stock Usage)": "stock_usage", "ਵਿਦਿਆਰਥੀ (Student)": "students", "ਵਿਧਵਾ (Widow)": "widows", "ਰਾਸ਼ਨ ਵੰਡ (Ration)": "ration_distribution", "ਰਸੀਦ ਕਿਤਾਬ (Receipt Book)": "receipt_books", "ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Staff)": "staff_profiles", "ਹਾਜ਼ਰੀ (Attendance)": "attendance"}

    if st.session_state.admin_mode == "📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)" and is_admin:
        st.write("### 📂 ਪੁਰਾਣਾ ਡਾਟਾ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ")
        upload_type = st.selectbox("ਡਾਟਾ ਚੁਣੋ", ["ਦਾਨ (Donations)", "ਵਿਦਿਆਰਥੀ (Students)", "ਵਿਧਵਾਵਾਂ (Widows)", "ਬੈਂਕ ਐਂਟਰੀਆਂ (Bank Ledger)"])
        default_bank_upload = st.selectbox("ਇਹ ਸਟੇਟਮੈਂਟ ਕਿਸ ਬੈਂਕ ਦੀ ਹੈ?", BANK_ACCOUNTS, index=1) if upload_type == "ਬੈਂਕ ਐਂਟਰੀਆਂ (Bank Ledger)" else "Kotak Bank Regular"
        uploaded_file = st.file_uploader("ਐਕਸਲ ਫਾਈਲ ਚੁਣੋ (.xlsx, .xls)", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            df_upload.columns = df_upload.columns.str.lower().str.replace(' ', '_').str.replace('-', '_').str.strip()
            df_upload = df_upload.astype(object).where(pd.notna(df_upload), None)
            st.dataframe(df_upload.head(10), use_container_width=True)
            
            if st.button(f"🚀 ਸਾਰਾ ਡਾਟਾ {upload_type} ਵਿੱਚ ਸੇਵ ਕਰੋ", type="primary"):
                try:
                    if upload_type == "ਦਾਨ (Donations)": allowed_cols, table_name = ['id', 'date', 'name', 'phone', 'address', 'amount', 'payment_mode', 'cheque_no', 'cheque_bank', 'donation_type', 'item_details', 'bank_account', 'on_account_of', 'collector_name', 'add_to_mirror', 'balance'], "donations"
                    elif upload_type == "ਵਿਦਿਆਰਥੀ (Students)": allowed_cols, table_name = ['name', 'phone', 'course', 'join_date', 'pass_date', 'photo_base64'], "students"
                    elif upload_type == "ਵਿਧਵਾਵਾਂ (Widows)": allowed_cols, table_name = ['form_no', 'card_no', 'name', 'age', 'husband_name', 'husband_death_date', 'phone', 'address', 'boys_details', 'girls_details', 'issued_by', 'join_date', 'photo_base64'], "widows"
                    elif upload_type == "ਬੈਂਕ ਐਂਟਰੀਆਂ (Bank Ledger)":
                        for c in ['withdrawal', 'withdrawals', 'dr']:
                            if c in df_upload.columns and 'debit' not in df_upload.columns: df_upload['debit'] = df_upload[c]
                        for c in ['deposit', 'deposits', 'cr']:
                            if c in df_upload.columns and 'credit' not in df_upload.columns: df_upload['credit'] = df_upload[c]
                        df_upload['debit'] = pd.to_numeric(df_upload.get('debit', 0), errors='coerce').fillna(0.0)
                        df_upload['credit'] = pd.to_numeric(df_upload.get('credit', 0), errors='coerce').fillna(0.0)
                        df_upload['balance'] = pd.to_numeric(df_upload.get('balance', 0), errors='coerce').fillna(0.0)
                        df_upload['source'] = df_upload.get('source', 'Bulk Excel')
                        if 'bank_name' not in df_upload.columns and 'bank' in df_upload.columns: df_upload['bank_name'] = df_upload['bank']
                        elif 'account' in df_upload.columns and 'bank_name' not in df_upload.columns: df_upload['bank_name'] = df_upload['account']
                        df_upload['bank_name'] = df_upload.get('bank_name', default_bank_upload).fillna(default_bank_upload).replace("", default_bank_upload)
                        if 'txn_date' not in df_upload.columns:
                            if 'date' in df_upload.columns: df_upload['txn_date'] = df_upload['date']
                            elif 'transaction_date' in df_upload.columns: df_upload['txn_date'] = df_upload['transaction_date']
                            elif 'value_date' in df_upload.columns: df_upload['txn_date'] = df_upload['value_date']
                        if 'txn_date' in df_upload.columns: 
                            df_upload['txn_date'] = df_upload['txn_date'].apply(lambda d: parse_date_to_obj(d).strftime('%Y-%m-%d') if parse_date_to_obj(d) else str(d))
                        allowed_cols, table_name = ['txn_date', 'description', 'bank_name', 'debit', 'credit', 'balance', 'source'], "bank_ledger"

                    for c in allowed_cols:
                        if c not in df_upload.columns: df_upload[c] = None
                    df_upload = df_upload[allowed_cols]
                    records = df_upload.to_dict(orient='records')
                    for rec in records:
                        for k, v in rec.items():
                            if isinstance(v, float) and math.isnan(v): rec[k] = None

                    # Batch insertion to avoid timeouts (500 records per API call)
                    for i in range(0, len(records), 500): supabase.table(table_name).insert(records[i:i+500]).execute()
                    st.success(f"✅ {upload_type} ਦਾ ਸਾਰਾ ਡਾਟਾ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਲੋਡ ਹੋ ਗਿਆ ਹੈ!")
                except Exception as e: st.error(f"❌ ਐਰਰ: {e}")

    elif st.session_state.admin_mode == "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚੋਂ ਡਿਲੀਟ ਕਰਨਾ ਹੈ?", list(t_map.keys()), key="del_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="del_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="del_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="del_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []

        try: raw_data = supabase.table(table_name).select("*").limit(100000).execute().data or []
        except: raw_data = []

        if raw_data:
            df_del = pd.DataFrame(raw_data)
            if search_name:
                search_cols = [c for c in ['name', 'description', 'item_name', 'party_name', 'collector_name', 'widow_name', 'staff_name', 'purpose'] if c in df_del.columns]
                if search_cols:
                    mask = df_del[search_cols[0]].astype(str).str.contains(search_name, case=False, na=False)
                    for c in search_cols[1:]: mask = mask | df_del[c].astype(str).str.contains(search_name, case=False, na=False)
                    df_del = df_del[mask]
            if filter_date and len(date_range) == 2:
                d_start, d_end = date_range
                date_cols = [c for c in ['date', 'txn_date', 'created_at', 'cheque_date', 'last_updated', 'join_date', 'distribution_date', 'issued_date', 'date_added', 'usage_date'] if c in df_del.columns]
                if date_cols:
                    df_del['__temp_date'] = df_del[date_cols[0]].apply(parse_date_to_obj)
                    df_del = df_del[(df_del['__temp_date'] >= d_start) & (df_del['__temp_date'] <= d_end)].drop(columns=['__temp_date'])
                    
            if not df_del.empty:
                st.success(f"✅ ਕੁੱਲ {len(df_del)} ਐਂਟਰੀਆਂ ਮਿਲੀਆਂ ਹਨ।")
                df_del.insert(0, "Select", False)
                edited_df = st.data_editor(format_dates_in_df(df_del, ascending=False), column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=[c for c in df_del.columns if c != "Select"], hide_index=True, use_container_width=True, key=f"editor_delete_{table_name}")
                selected_rows = edited_df[edited_df["Select"] == True]
                if not selected_rows.empty:
                    if is_admin:
                        if st.button("🛑 ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ (Delete)", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else int(float(row['id']))
                                col_name = "item_name" if table_name == "stock" else "id"
                                supabase.table(table_name).delete().eq(col_name, rec_id).execute()
                            st.success("✅ ਡਿਲੀਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਬੇਨਤੀ ਭੇਜੋ", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else str(row['id'])
                                supabase.table("deletion_requests").insert({"table_name": table_name, "record_id": str(rec_id), "details": str(row.drop('Select').to_dict()), "requested_by": "staff"}).execute()
                            st.success("✅ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")

    elif st.session_state.admin_mode == "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚ ਸੋਧ ਕਰਨੀ ਹੈ?", list(t_map.keys()), key="edit_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="edit_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="edit_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="edit_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []
            
        try: raw_data = supabase.table(table_name).select("*").limit(100000).execute().data or []
        except: raw_data = []
            
        if raw_data:
            df_edit = pd.DataFrame(raw_data)
            if search_name:
                search_cols = [c for c in ['name', 'description', 'item_name', 'party_name', 'collector_name', 'widow_name', 'staff_name', 'purpose'] if c in df_edit.columns]
                if search_cols:
                    mask = df_edit[search_cols[0]].astype(str).str.contains(search_name, case=False, na=False)
                    for c in search_cols[1:]: mask = mask | df_edit[c].astype(str).str.contains(search_name, case=False, na=False)
                    df_edit = df_edit[mask]
            if filter_date and len(date_range) == 2:
                d_start, d_end = date_range
                date_cols = [c for c in ['date', 'txn_date', 'created_at', 'cheque_date', 'last_updated', 'join_date', 'distribution_date', 'issued_date', 'date_added', 'usage_date'] if c in df_edit.columns]
                if date_cols:
                    df_edit['__temp_date'] = df_edit[date_cols[0]].apply(parse_date_to_obj)
                    df_edit = df_edit[(df_edit['__temp_date'] >= d_start) & (df_edit['__temp_date'] <= d_end)].drop(columns=['__temp_date'])
                    
            if not df_edit.empty:
                st.success("✅ ਸਿੱਧਾ ਕਲਿੱਕ ਕਰਕੇ ਬਦਲਾਅ ਕਰੋ:")
                df_edit = format_dates_in_df(df_edit, ascending=False).reset_index(drop=True).where(pd.notnull(df_edit), None)
                pk_col = 'item_name' if table_name == 'stock' else 'id'
                
                edited_df = st.data_editor(df_edit, hide_index=True, disabled=[pk_col] if pk_col in df_edit.columns else [], use_container_width=True, key=f"editor_edit_{table_name}")
                changed_rows = []
                orig_records, edited_records = df_edit.to_dict('records'), edited_df.to_dict('records')
                
                for i in range(len(orig_records)):
                    orig, ed = orig_records[i], edited_records[i]
                    changes = {}
                    for k in ed.keys():
                        if str(orig[k]) != str(ed[k]):
                            if k in ['date', 'txn_date', 'cheque_date', 'procurement_date', 'issued_date', 'join_date', 'distribution_date', 'usage_date', 'created_at', 'Date', 'date_added']:
                                obj = parse_date_to_obj(ed[k])
                                changes[k] = obj.strftime('%Y-%m-%d') if obj else str(ed[k])
                            else: changes[k] = ed[k]
                    if changes: changed_rows.append((orig['item_name'] if table_name == 'stock' else orig['id'], changes))
                        
                if changed_rows:
                    if is_admin:
                        if st.button("💾 ਬਦਲਾਅ ਸੇਵ ਕਰੋ (Save)", type="primary"):
                            for rec_id, changes in changed_rows:
                                supabase.table(table_name).update(changes).eq("item_name" if table_name == "stock" else "id", rec_id).execute()
                            st.success("✅ ਡਾਟਾਬੇਸ ਅਪਡੇਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ", type="primary"):
                            for rec_id, changes in changed_rows:
                                supabase.table("edit_requests").insert({"table_name": table_name, "record_id": str(rec_id), "changes": json.dumps(changes), "status": "Pending", "requested_by": "staff"}).execute()
                            st.success("✅ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")
