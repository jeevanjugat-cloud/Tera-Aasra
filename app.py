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
import math
from PIL import Image
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- GEO-FENCING (ATTENDANCE LOCATION) ---
NGO_LAT = 31.6120 
NGO_LON = 74.8677

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
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
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

# ==========================================
# 100% BULLETPROOF DATE PARSER & FORMATTER (DD MMM YYYY)
# ==========================================
def parse_date_to_obj(val):
    if pd.isna(val) or str(val).strip() in ["", "NaT", "None", "nan", "null"]:
        return None
    s = str(val).strip().split(" ")[0].split("T")[0]
    
    if len(s) >= 10 and (s[4] == '-' or s[4] == '/'):
        try:
            parts = s.replace('/', '-').split('-')
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            pass
            
    if len(s) >= 8 and ('/' in s or '-' in s):
        sep = '/' if '/' in s else '-'
        parts = s.split(sep)
        if len(parts) == 3:
            try:
                if len(parts[0]) == 4: 
                    return date(int(parts[0]), int(parts[1]), int(parts[2]))
                elif len(parts[2]) == 4: 
                    p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2])
                    if p1 > 12: return date(p3, p1, p2)
                    elif p2 > 12: return date(p3, p2, p1)
                    else: return date(p3, p2, p1)
            except Exception:
                pass
                
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if pd.notna(dt):
            return dt.date()
    except Exception:
        pass
    return None

def clean_date_to_ddmmyyyy(val):
    d = parse_date_to_obj(val)
    if d: return d.strftime("%d %b %Y") # Output: 15 Apr 2026
    return str(val) if pd.notna(val) and str(val).strip() not in ["None", "nan", ""] else ""

def format_dates_in_df(df):
    df_copy = df.copy()
    date_columns = ['date', 'txn_date', 'cheque_date', 'procurement_date', 'issued_date', 'join_date', 'distribution_date', 'usage_date', 'created_at', 'Date', 'date_added', 'DateObj']
    for col in date_columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(clean_date_to_ddmmyyyy)
    if 'last_updated' in df_copy.columns:
        def parse_dt_time(d):
            if pd.isna(d) or str(d).strip() in ["", "NaT", "None", "nan"]: return ""
            try: return pd.to_datetime(str(d).strip(), dayfirst=True).strftime('%d %b %Y %I:%M %p')
            except: return str(d)
        df_copy['last_updated'] = df_copy['last_updated'].apply(parse_dt_time)
    return df_copy

def sort_df_by_date(df, date_col='date', ascending=False):
    """Sorts DataFrame correctly using parsed date objects"""
    if df.empty or date_col not in df.columns: return df
    df_copy = df.copy()
    df_copy['_temp_sort_dt'] = df_copy[date_col].apply(parse_date_to_obj).fillna(date(1900, 1, 1))
    df_copy = df_copy.sort_values(by='_temp_sort_dt', ascending=ascending).drop(columns=['_temp_sort_dt']).reset_index(drop=True)
    return df_copy

def prepare_export_df(table_name, date_col):
    """Helper to fetch, safely sort and format data for CA Export"""
    data = supabase.table(table_name).select("*").limit(100000).execute().data or []
    df = pd.DataFrame(data)
    if not df.empty and date_col in df.columns:
        df = sort_df_by_date(df, date_col, ascending=True)
    return format_dates_in_df(df)

def is_bank_match(record_bank, target_bank):
    if pd.isna(record_bank) or str(record_bank).strip() in ["", "None", "nan", "null"]:
        rb = "kotak bank regular"
    else:
        rb = str(record_bank).strip().lower()
        
    tb = str(target_bank).strip().lower()
    if rb == tb: return True
    if "kotak" in tb and "corpus" not in tb: return ("kotak" in rb) and ("corpus" not in rb)
    if "corpus" in tb: return "corpus" in rb
    if "punjab" in tb or "sind" in tb or "psb" in tb: return ("punjab" in rb) or ("sind" in rb) or ("psb" in rb)
    if "ਨਕਦ" in tb or "cash" in tb: return ("ਨਕਦ" in rb) or ("cash" in rb)
    return False

def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000 
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) *ਵਾਹਿਗੁਰੂ ਜੀ! ਮੈਂ ਤੁਹਾਡੀ ਗੱਲ ਬਿਲਕੁਲ ਸਮਝ ਗਿਆ ਹਾਂ। ਤੁਸੀਂ ਚਾਹੁੰਦੇ ਹੋ ਕਿ ਤਾਰੀਖਾਂ ਨੂੰ ਲੈ ਕੇ ਕਦੇ ਵੀ ਕੋਈ ਉਲਝਣ ਨਾ ਰਹੇ ਅਤੇ ਉਹ ਸਿੱਧੀਆਂ ਪੜ੍ਹਨ ਵਾਲੇ ਫਾਰਮੈਟ ਜਿਵੇਂ **"1 April 2026"** ਜਾਂ **"15 April 2026"** ਵਿੱਚ ਲਿਖੀਆਂ ਆਉਣ। 

ਇਸਤੋਂ ਇਲਾਵਾ, ਮੈਂ **CA ਲਈ ਐਕਸਲ (Excel) ਰਿਪੋਰਟਾਂ** ਅਤੇ ਸਾਫਟਵੇਅਰ ਦੀਆਂ **ਸਾਰੀਆਂ ਸਕ੍ਰੀਨਾਂ (Every Window)** 'ਤੇ 2 ਵੱਡੇ ਬਦਲਾਅ ਕੀਤੇ ਹਨ:

1. **Date Formatting (1 April 2026):** ਹੁਣ ਡਾਟਾਬੇਸ ਵਿੱਚ ਤਾਰੀਖ ਜਿਵੇਂ ਮਰਜ਼ੀ ਸੇਵ ਹੋਵੇ (04/01/2026 ਜਾਂ 15/04/2026), ਸਾਫਟਵੇਅਰ ਉਸਨੂੰ ਆਪਣੇ-ਆਪ ਅੰਗਰੇਜ਼ੀ ਮਹੀਨੇ ਵਾਲੇ ਫਾਰਮੈਟ (ਜਿਵੇਂ **15 April 2026**) ਵਿੱਚ ਬਦਲ ਦੇਵੇਗਾ। ਇਹੀ ਫਾਰਮੈਟ CA ਐਕਸਲ ਫਾਈਲ ਵਿੱਚ ਵੀ ਜਾਵੇਗਾ ਤਾਂ ਜੋ ਐਕਸਲ ਕਦੇ ਵੀ ਤਾਰੀਖਾਂ ਨੂੰ ਉਲਟ-ਪੁਲਟ ਨਾ ਕਰੇ।
2. **Global Date Sorting (ਸਭ ਕੁਝ ਮਿਤੀ ਅਨੁਸਾਰ):** ਮੈਂ ਸਿਸਟਮ ਵਿੱਚ ਇੱਕ ਨਵਾਂ `sort_df_by_date` ਇੰਜਣ ਲਗਾ ਦਿੱਤਾ ਹੈ। ਹੁਣ ਭਾਵੇਂ ਦਾਨ ਦੀ ਲਿਸਟ ਹੋਵੇ, ਖਰਚੇ ਹੋਣ, ਬੈਂਕ ਐਂਟਰੀਆਂ, ਵਿਦਿਆਰਥੀ ਜਾਂ CA ਐਕਸਲ ਰਿਪੋਰਟ—**ਸਭ ਕੁਝ ਆਪਣੇ ਆਪ ਨਵੀਂ ਮਿਤੀ ਤੋਂ ਪੁਰਾਣੀ ਮਿਤੀ ਦੇ ਕ੍ਰਮ (Date-wise Descending Order)** ਵਿੱਚ ਲੱਗ ਕੇ ਆਵੇਗਾ।

ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ **`app.py`** ਵਿੱਚ ਪੁਰਾਣਾ ਸਾਰਾ ਕੋਡ ਮਿਟਾ ਕੇ ਹੇਠਾਂ ਦਿੱਤਾ ਇਹ ਫਾਈਨਲ ਕੋਡ ਪੇਸਟ ਕਰ ਲਵੋ ਜੀ:

```python
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
import math
from PIL import Image
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- GEO-FENCING (ATTENDANCE LOCATION) ---
NGO_LAT = 31.6120 
NGO_LON = 74.8677

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
SUPABASE_URL = "[https://jbvtvrhzzucggqhwjzuu.supabase.co](https://jbvtvrhzzucggqhwjzuu.supabase.co)"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ (Sabha Manager Pro)", page_icon="logo.png", layout="wide")

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display:none !important;}

        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
        div[data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 600 !important; }
        h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
        h3 { font-size: 20px !important; font-weight: 600 !important; }
        [data-testid="stMetricLabel"] p { font
