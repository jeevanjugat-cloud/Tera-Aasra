# utils.py
import pandas as pd
from datetime import datetime, date
import math
import io
import base64
import os
from PIL import Image
import streamlit as st
from supabase import create_client, Client
import config

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

supabase: Client = init_connection()

# --- BULLETPROOF DATE FORMATTING ---
def parse_date_to_obj(val):
    if pd.isna(val) or str(val).strip() in ["", "NaT", "None", "nan", "null"]: return None
    s = str(val).strip().split(" ")[0].split("T")[0]
    try:
        dt = pd.to_datetime(s, dayfirst=False, errors='coerce')
        if pd.notna(dt): return dt.date()
    except: pass
    return None

def clean_date_to_display(val):
    d = parse_date_to_obj(val)
    if d: return f"{d.day} {d.strftime('%B %Y')}" 
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

# --- HELPERS ---
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

# --- REPORTS ---
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
    <body><div class="header">{img}<div class="title">{config.NGO_NAME_PB}</div><div class="tagline">{config.NGO_TAGLINE_PB}</div>
    <div style="font-size: 13px;">{config.NGO_ADDRESS_PB}</div><h3 style="color:#0F4C81;margin-top:10px;">{title}</h3></div>
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
    <body><div class="receipt-box"><div class="header-flex">{img_html}<div class="header-text"><p class="title-pa">{config.NGO_NAME_PB}</p><div class="sub-title-pa">{config.NGO_TAGLINE_PB}</div>
    <p style="font-size:13px; color:#0F4C81; margin: 3px 0; font-weight:bold;">Regd. Office: {config.NGO_ADDRESS_PB}<br>(M) 099150-07697, 78953-33290</p></div></div>
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
        </style></head><body><div class="receipt-box"><div class="header-flex">{img_html}<div style="text-align:center; width:100%;"><h2 style="margin:0;">{config.NGO_NAME_PB}</h2><p style="margin:4px 0;">{config.NGO_TAGLINE_PB}</p></div></div>
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
