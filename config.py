# config.py
from supabase import create_client, Client
import streamlit as st

NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ-ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ (ਰਜਿ.)"
NGO_TAGLINE_PB = "ਸੇਵਾ ਵਿਸਥਾਰ: ਤੇਰਾ ਆਸਰਾ (ਸੇਵਾ-ਸਹਿਯੋਗ-ਭਲਾਈ)"
NGO_ADDRESS_PB = "ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

NGO_LAT, NGO_LON = 31.6120, 74.8677

BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = [
    "--- ਕੀਰਤਨ ਸਮਾਗਮ (Samagams) ---", "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", 
    "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)", "ਲੰਗਰ (Langar)",
    "--- ਤੇਰਾ ਆਸਰਾ (Tera Aasra) ---", "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", 
    "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)", "ਹੋਰ ਖਰਚੇ (Others)"
]
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

@st.cache_resource
def init_connection(): 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try: 
    supabase: Client = init_connection()
except Exception as e: 
    st.error(f"Supabase Error: {e}")
