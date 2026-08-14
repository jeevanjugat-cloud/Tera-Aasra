import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse
import io
from supabase import create_client, Client

# --- ਸਭਾ ਦੇ ਵੇਰਵੇ (NGO DETAILS) ---
NGO_NAME_PB = "ਸ਼ਬਦ ਕੀਰਤਨ ਨਾਮ ਸਿਮਰਨ ਸਤਿਸੰਗ"
NGO_ADDRESS_PB = "ਰਜਿਸਟਰਡ, ਸੀ.ਬੀ. ਟਾਵਰ, ਜੀ.ਟੀ. ਰੋਡ, ਅੰਮ੍ਰਿਤਸਰ"

# --- ਲਾਗਇਨ ਖਾਤੇ (LOGIN ACCOUNTS) ---
# ਤੁਸੀਂ ਇੱਥੇ ਪਾਸਵਰਡ ਆਪਣੀ ਮਰਜ਼ੀ ਅਨੁਸਾਰ ਬਦਲ ਸਕਦੇ ਹੋ
USERS = {
    "admin": "Japnik@3315",      # ਐਡਮਿਨ: ਸਭ ਕੁਝ ਕਰ ਸਕਦਾ ਹੈ
    "staff": "12345"      # ਸਟਾਫ: ਸਿਰਫ ਐਂਟਰੀਆਂ ਕਰ ਸਕਦਾ ਹੈ
}

# --- SUPABASE ਕਨੈਕਸ਼ਨ (ਇੱਥੇ ਆਪਣੀ ਡਿਟੇਲ ਪਾਓ) ---
SUPABASE_URL = "https://jbvtvrhzzucggqhwjzuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpidnR2cmh6enVjZ2dxaHdqenV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY2OTkyMjAsImV4cCI6MjEwMjI3NTIyMH0.ynHuvuCDD3Spa6b0P6SIUecuB6sxrIbDDCQQVfiiwTs"

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Supabase ਨਾਲ ਜੁੜਨ ਵਿੱਚ ਸਮੱਸਿਆ ਆ ਰਹੀ ਹੈ।")

# --- HTML RECEIPT GENERATOR ---
def generate_html_receipt(receipt_no, name, amount, date, payment_mode):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pa">
    <head>
        <meta charset="UTF-8">
        <title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .receipt-box {{ max-width: 600px; margin: auto; padding: 30px; border: 2px solid #ff9933; border-radius: 10px; background-color: #ffffff; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; border-bottom: 2px solid #ff9933; padding-bottom: 10px; margin-bottom: 20px; }}
            .header h1 {{ color: #cc5200; margin: 0; font-size: 28px; }}
            .header p {{ color: #555; margin: 5px 0 0 0; font-size: 14px; }}
            .content {{ line-height: 1.8; font-size: 18px; color: #333; }}
            .row {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
            .amount-box {{ font-size: 24px; font-weight: bold; background-color: #fff0e6; padding: 10px; text-align: center; border-radius: 5px; margin: 20px 0; border: 1px dashed #ff9933; }}
            .footer {{ margin-top: 40px; display: flex; justify-content: space-between; align-items: flex-end; }}
            .sign-line {{ border-top: 1px solid #000; width: 150px; text-align: center; padding-top: 5px; font-size: 14px; }}
            @media print {{ body {{ background-color: #fff; padding: 0; }} .receipt-box {{ box-shadow: none; border: 2px solid #000; }} }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="header">
                <h1>ੴ</h1>
                <h1>{NGO_NAME_PB}</h1>
                <p>{NGO_ADDRESS_PB}</p>
                <h3 style="color:#444; margin-top:15px;">ਦਾਨ ਰਸੀਦ (DONATION RECEIPT)</h3>
            </div>
            <div class="content">
                <div class="row">
                    <span><strong>ਰਸੀਦ ਨੰਬਰ (Receipt No):</strong> {receipt_no}</span>
                    <span><strong>ਮਿਤੀ (Date):</strong> {date[:10]}</span>
                </div>
                <div style="margin-top: 20px;">
                    <p><strong>ਦਾਨੀ ਦਾ ਨਾਮ (Received with thanks from):</strong> {name}</p>
                    <p><strong>ਭੁਗਤਾਨ ਦਾ ਤਰੀਕਾ (Payment Mode):</strong> {payment_mode}</p>
                </div>
                <div class="amount-box">
                    ਰਕਮ (Amount): ₹ {amount}/-
                </div>
                <p style="text-align: center; color: #666; font-size: 14px;">
                    <em>ਸਭਾ ਨੂੰ ਮਾਲੀ ਸਹਾਇਤਾ ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।<br>Thank you for your generous support.</em>
                </p>
            </div>
            <div class="footer">
                <div></div>
                <div class="sign-line">ਪ੍ਰਵਾਨਿਤ ਦਸਤਖਤ<br>(Authorized Signatory)</div>
            </div>
        </div>
        <script>
            window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filename


# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.session_state.username = ""

# --- LOGIN SCREEN (ਲਾਗਇਨ ਸਕਰੀਨ) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🙏</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{NGO_NAME_PB}</h2>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.subheader("🔒 ਸਾਫਟਵੇਅਰ ਵਿੱਚ ਲਾਗਇਨ ਕਰੋ")
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            submit_login = st.form_submit_button("ਲਾਗਇਨ (Login)")
            
            if submit_login:
                if username_input in USERS and USERS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    if username_input == "admin":
                        st.session_state.is_admin = True
                    else:
                        st.session_state.is_admin = False
                    st.rerun()
                else:
                    st.error("❌ ਯੂਜ਼ਰਨੇਮ ਜਾਂ ਪਾਸਵਰਡ ਗਲਤ ਹੈ!")
    st.stop()  # ਇੱਥੇ ਕੋਡ ਰੁਕ ਜਾਵੇਗਾ ਜਦੋਂ ਤੱਕ ਲਾਗਇਨ ਨਹੀਂ ਹੁੰਦਾ

# ==========================================
# ਮੁੱਖ ਸਾਫਟਵੇਅਰ (ਸਿਰਫ਼ ਲਾਗਇਨ ਹੋਣ ਤੋਂ ਬਾਅਦ ਖੁੱਲ੍ਹੇਗਾ)
# ==========================================

with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ")
    if st.session_state.is_admin:
        st.success("✅ ਤੁਸੀਂ ਐਡਮਿਨ (Admin) ਵਜੋਂ ਲਾਗਇਨ ਹੋ।")
    else:
        st.info("✅ ਤੁਸੀਂ ਕਰਮਚਾਰੀ (Staff) ਵਜੋਂ ਲਾਗਇਨ ਹੋ।")
        
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

st.title(f"🙏 {NGO_NAME_PB}")
st.write(f"📍 {NGO_ADDRESS_PB}")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💸 ਦਾਨ (Donation)", 
    "📉 ਖਰਚੇ (Expenses)", 
    "📦 ਸਟਾਕ (Stock)", 
    "🎓 ਵਿਦਿਆਰਥੀ (Students)", 
    "📊 ਖਾਤਾ ਸੰਖੇਪ (Accounts)",
    "📑 ਰਿਪੋਰਟਾਂ (Reports)"
])

# TAB 1: DONATIONS
with tab1:
    st.header("ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ")
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)")
        donor_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone)")
        amount = st.number_input("ਰਕਮ / Amount (₹)", min_value=1)
        pay_mode = st.selectbox("ਭੁਗਤਾਨ ਦਾ ਤਰੀਕਾ (Payment Mode)", ["ਨਕਦ (Cash)", "ਆਨਲਾਈਨ (UPI/Bank)"])
        receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ (Receipt Date)", value=date.today())
        submit = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ")

    if submit and donor_name and amount:
        formatted_date = receipt_date.strftime("%Y-%m-%d")
        
        data, count = supabase.table("donations").insert({
            "name": donor_name, 
            "phone": donor_phone, 
            "amount": amount, 
            "date": formatted_date, 
            "payment_mode": pay_mode
        }).execute()
        
        receipt_id = data[1][0]['id']
        html_file = generate_html_receipt(receipt_id, donor_name, amount, formatted_date, pay_mode)
        st.success(f"ਦਾਨ ਸੇਵ ਹੋ ਗਿਆ! ਰਸੀਦ #{receipt_id} ਤਿਆਰ ਹੈ।")
        
        with open(html_file, "r", encoding="utf-8") as file:
            st.download_button(label="🖨️ ਪ੍ਰਿੰਟ ਕਰਨ ਲਈ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file, mime="text/html")
        
        if donor_phone:
            msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ।\n\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ,\n{NGO_NAME_PB} ਨੂੰ ₹{amount}/- ਦਾ ਦਾਨ ({pay_mode} ਰਾਹੀਂ) ਦੇਣ ਲਈ ਆਪ ਜੀ ਦਾ ਬਹੁਤ-ਬਹੁਤ ਧੰਨਵਾਦ ਜੀ।"
            url = f"https://wa.me/{donor_phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f"[💬 WhatsApp ਸੁਨੇਹਾ ਭੇਜਣ ਲਈ ਇੱਥੇ ਕਲਿੱਕ ਕਰੋ]({url})", unsafe_allow_html=True)

# TAB 2: EXPENDITURES
with tab2:
    st.header("ਖਰਚਾ ਦਰਜ ਕਰੋ")
    with st.form("expense_form", clear_on_submit=True):
        desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Description)")
        exp_amount = st.number_input("ਰਕਮ (₹)", min_value=1)
        exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ (Date)", value=date.today())
        if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ") and desc:
            formatted_exp_date = exp_date.strftime("%Y-%m-%d")
            supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": formatted_exp_date}).execute()
            st.success("ਖਰਚਾ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ!")

# TAB 3: STOCK MANAGEMENT
with tab3:
    st.header("ਸਟਾਕ / ਭੰਡਾਰ")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("stock_form", clear_on_submit=True):
            item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ")
            qty = st.number_input("ਮਾਤਰਾ", min_value=0.0, step=0.5)
            unit = st.selectbox("ਇਕਾਈ", ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)"])
            stock_action = st.radio("ਐਕਸ਼ਨ", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add)", "ਸਮਾਨ ਵਰਤਿਆ (Remove)"])
            
            if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ") and item_name:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                res = supabase.table("stock").select("*").eq("item_name", item_name).execute()
                
                if res.data:
                    old_qty = res.data[0]['quantity']
                    new_qty = old_qty + qty if "Add" in stock_action else max(0, old_qty - qty)
                    supabase.table("stock").update({"quantity": new_qty, "last_updated": current_date, "unit": unit}).eq("item_name", item_name).execute()
                else:
                    new_qty = qty if "Add" in stock_action else 0
                    supabase.table("stock").insert({"item_name": item_name, "quantity": new_qty, "unit": unit, "last_updated": current_date}).execute()
                st.success(f"'{item_name}' ਦਾ ਸਟਾਕ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ!")

    with col2:
        st.subheader("ਮੌਜੂਦਾ ਸਟਾਕ")
        stock_res = supabase.table("stock").select("*").gt("quantity", 0).execute()
        if stock_res.data:
            df = pd.DataFrame(stock_res.data)
            st.dataframe(df[['item_name', 'quantity', 'unit', 'last_updated']], use_container_width=True)

# TAB 4: STUDENTS
with tab4:
    st.header("ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ")
    with st.form("student_form", clear_on_submit=True):
        stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ")
        stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
        stu_course = st.selectbox("ਕਲਾਸ", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"])
        join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ", value=date.today())
        has_passed = st.checkbox("ਕੀ ਕੋਰਸ ਪੂਰਾ ਕਰ ਲਿਆ ਹੈ?")
        pass_date = st.date_input("ਪਾਸ ਹੋਣ ਦੀ ਮਿਤੀ", value=date.today()) if has_passed else None
        
        if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ") and stu_name:
            p_date = pass_date.strftime("%Y-%m-%d") if has_passed else "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ"
            supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": p_date}).execute()
            st.success("ਵਿਦਿਆਰਥੀ ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")

# TAB 5: ACCOUNTS OVERVIEW
with tab5:
    st.header("ਖਾਤਾ ਸੰਖੇਪ (Financial Overview)")
    
    don_res = supabase.table("donations").select("*").execute()
    exp_res = supabase.table("expenses").select("*").execute()
    
    df_don = pd.DataFrame(don_res.data) if don_res.data else pd.DataFrame(columns=['id', 'name', 'amount', 'date'])
    df_exp = pd.DataFrame(exp_res.data) if exp_res.data else pd.DataFrame(columns=['id', 'description', 'amount', 'date'])
    
    tot_don = df_don['amount'].sum() if not df_don.empty else 0
    tot_exp = df_exp['amount'].sum() if not df_exp.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ਕੁੱਲ ਆਮਦਨ (Income)", f"₹ {tot_don:,.2f}")
    c2.metric("ਕੁੱਲ ਖਰਚਾ (Expenses)", f"₹ {tot_exp:,.2f}")
    c3.metric("ਮੌਜੂਦਾ ਬਕਾਇਆ (Balance)", f"₹ {tot_don - tot_exp:,.2f}")
    
    # ADMIN ONLY: Delete Section
    if st.session_state.is_admin:
        st.error("⚠️ ਐਡਮਿਨ ਪਾਵਰ: ਗਲਤ ਐਂਟਰੀਆਂ ਡਿਲੀਟ ਕਰੋ (Admin Delete Area)")
        del_col1, del_col2 = st.columns(2)
        with del_col1:
            st.write("ਦਾਨ ਡਿਲੀਟ ਕਰੋ")
            don_id = st.number_input("ਰਸੀਦ ਨੰਬਰ (Donation ID)", min_value=0, step=1)
            if st.button("ਦਾਨ ਡਿਲੀਟ ਕਰੋ"):
                supabase.table("donations").delete().eq("id", don_id).execute()
                st.success("ਡਿਲੀਟ ਹੋ ਗਿਆ!")
                st.rerun()
        with del_col2:
            st.write("ਖਰਚਾ ਡਿਲੀਟ ਕਰੋ")
            exp_id = st.number_input("ਖਰਚਾ ID (Expense ID)", min_value=0, step=1)
            if st.button("ਖਰਚਾ ਡਿਲੀਟ ਕਰੋ"):
                supabase.table("expenses").delete().eq("id", exp_id).execute()
                st.success("ਡਿਲੀਟ ਹੋ ਗਿਆ!")
                st.rerun()

# TAB 6: REPORTS
with tab6:
    st.header("ਐਕਸਲ ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ (Download Excel)")
    if st.button("📊 ਰਿਪੋਰਟ ਤਿਆਰ ਕਰੋ (Generate Report)"):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            pd.DataFrame(supabase.table("donations").select("*").execute().data or []).to_excel(writer, sheet_name='ਦਾਨ', index=False)
            pd.DataFrame(supabase.table("expenses").select("*").execute().data or []).to_excel(writer, sheet_name='ਖਰਚੇ', index=False)
            pd.DataFrame(supabase.table("stock").select("*").execute().data or []).to_excel(writer, sheet_name='ਸਟਾਕ', index=False)
            pd.DataFrame(supabase.table("students").select("*").execute().data or []).to_excel(writer, sheet_name='ਵਿਦਿਆਰਥੀ', index=False)
        
        st.download_button("📥 ਡਾਊਨਲੋਡ ਕਰੋ (Download Excel)", data=buffer.getvalue(), file_name=f"NGO_Report_{datetime.now().strftime('%d-%m-%Y')}.xlsx")
