import streamlit as st
import pandas as pd
from datetime import date
import json
import time
import math
import config
import utils

# Bulletproof Signature: Prevents any TypeError related to positional arguments
def show_page(is_admin=False, is_staff=False, *args, **kwargs):
    st.header("⚙️ ਐਡਮਿਨ, ਡਿਲੀਟ ਅਤੇ ਸੋਧ (Edit) ਸਿਸਟਮ")
    
    if is_admin:
        modes = ["📔 ਜਰਨਲ ਵਾਊਚਰ (JV / Manual)", "📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)", "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
    else:
        modes = ["🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
        
    if 'admin_mode' not in st.session_state or st.session_state.admin_mode not in modes: 
        st.session_state.admin_mode = modes[0]
        
    st.session_state.admin_mode = st.radio("ਐਡਮਿਨ ਟੂਲ ਚੁਣੋ:", modes, index=modes.index(st.session_state.admin_mode), horizontal=True)
    st.markdown("---")
    
    t_map = {
        "ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", 
        "ਪਾਰਟੀ (Party)": "parties", "ਚੈੱਕ (Cheque)": "cheques", "ਸੰਪਤੀ (Asset)": "assets", 
        "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", "ਸਟਾਕ ਵਰਤੋਂ (Stock Usage)": "stock_usage", 
        "ਵਿਦਿਆਰਥੀ (Student)": "students", "ਵਿਧਵਾ (Widow)": "widows", "ਰਾਸ਼ਨ ਵੰਡ (Ration)": "ration_distribution", 
        "ਰਸੀਦ ਕਿਤਾਬ (Receipt Book)": "receipt_books", "ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Staff)": "staff_profiles", "ਹਾਜ਼ਰੀ (Attendance)": "attendance"
    }

    # ================= 1. JV AND MANUAL ENTRIES =================
    if st.session_state.admin_mode == "📔 ਜਰਨਲ ਵਾਊਚਰ (JV / Manual)":
        st.write("### 📔 ਜਰਨਲ ਵਾਊਚਰ ਅਤੇ ਮੈਨੂਅਲ ਐਂਟਰੀਆਂ")
        
        try:
            # Safely fetch and format bank accounts to prevent type mismatch sorting errors
            e_data = utils.supabase.table("expenses").select("bank_account").limit(5000).execute().data or []
            d_data = utils.supabase.table("donations").select("bank_account").limit(5000).execute().data or []
            
            e_accs = {str(e.get('bank_account')).strip() for e in e_data if e.get('bank_account')}
            d_accs = {str(d.get('bank_account')).strip() for d in d_data if d.get('bank_account')}
            
            all_b = sorted(list(set(config.BANK_ACCOUNTS) | d_accs | e_accs))
        except Exception:
            all_b = config.BANK_ACCOUNTS

        jv_type = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ ਚੁਣੋ (Select Entry Type):", ["🏦 ਬੈਂਕ/ਕੈਸ਼ ਮੈਨੂਅਲ ਐਂਟਰੀ", "🔄 ਫੰਡ ਟਰਾਂਸਫਰ (Fund Transfer)", "⚠️ ਰਿਵਰਸਲ / ਐਡਜਸਟਮੈਂਟ"], horizontal=True)
        
        if jv_type == "🏦 ਬੈਂਕ/ਕੈਸ਼ ਮੈਨੂਅਲ ਐਂਟਰੀ":
            st.info("ਇਹ ਐਂਟਰੀ ਸਿੱਧਾ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਜਾਵੇਗੀ (Credit = Deposit/ਪੈਸੇ ਆਏ, Debit = Withdrawal/ਪੈਸੇ ਗਏ)।")
            with st.form("jv_bank_form", clear_on_submit=True):
                b_acc = st.selectbox("ਬੈਂਕ/ਕੈਸ਼ ਖਾਤਾ", all_b)
                b_dt = st.date_input("ਮਿਤੀ (Date)", value=date.today(), format="DD/MM/YYYY")
                b_desc = st.text_input("ਵੇਰਵਾ (Description)")
                c1, c2 = st.columns(2)
                b_type = c1.radio("ਕਿਸਮ (Type)", ["Deposit/Credit (ਪੈਸੇ ਆਏ)", "Withdrawal/Debit (ਪੈਸੇ ਗਏ)"])
                b_amt = c2.number_input("ਰਕਮ (₹)", min_value=0.01)
                if st.form_submit_button("ਐਂਟਰੀ ਸੇਵ ਕਰੋ", type="primary") and b_desc:
                    c_val, d_val = (b_amt, 0.0) if "Deposit/Credit" in b_type else (0.0, b_amt)
                    utils.supabase.table("bank_ledger").insert({"txn_date": b_dt.strftime("%Y-%m-%d"), "description": b_desc, "bank_name": b_acc, "debit": d_val, "credit": c_val, "balance": 0.0, "source": "Manual Entry"}).execute()
                    st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!")
                    
        elif jv_type == "🔄 ਫੰਡ ਟਰਾਂਸਫਰ (Fund Transfer)":
            st.info("ਇੱਕ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਢ ਕੇ ਦੂਜੇ ਖਾਤੇ ਵਿੱਚ ਪਾਉਣ ਲਈ (ਜਿਵੇਂ Cash ਤੋਂ Bank ਵਿੱਚ ਜਮ੍ਹਾਂ ਕਰਾਉਣੇ)।")
            with st.form("jv_transfer_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                from_acc = c1.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਕੱਢਣੇ ਹਨ? (From - Withdrawal/Debit)", all_b)
                to_acc = c2.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਪਾਉਣੇ ਹਨ? (To - Deposit/Credit)", all_b)
                t_amt = st.number_input("ਰਕਮ (₹)", min_value=0.01)
                t_desc = st.text_input("ਵੇਰਵਾ (Description) - e.g. Cash deposited to Bank")
                t_dt = st.date_input("ਮਿਤੀ (Date)", value=date.today(), format="DD/MM/YYYY")
                if st.form_submit_button("ਟਰਾਂਸਫਰ ਕਰੋ", type="primary") and t_desc:
                    if from_acc == to_acc: st.error("ਦੋਵੇਂ ਖਾਤੇ ਵੱਖੋ-ਵੱਖਰੇ ਹੋਣੇ ਚਾਹੀਦੇ ਹਨ!")
                    else:
                        dt_str = t_dt.strftime("%Y-%m-%d")
                        utils.supabase.table("bank_ledger").insert({"txn_date": dt_str, "description": t_desc + f" (To {to_acc})", "bank_name": from_acc, "debit": t_amt, "credit": 0.0, "balance": 0.0, "source": "Admin Transfer"}).execute()
                        utils.supabase.table("bank_ledger").insert({"txn_date": dt_str, "description": t_desc + f" (From {from_acc})", "bank_name": to_acc, "debit": 0.0, "credit": t_amt, "balance": 0.0, "source": "Admin Transfer"}).execute()
                        st.success("✅ ਫੰਡ ਟਰਾਂਸਫਰ ਹੋ ਗਿਆ!")
                        
        elif jv_type == "⚠️️ ਰਿਵਰਸਲ / ਐਡਜਸਟਮੈਂਟ":
            st.info("ਗਲਤ ਖਰਚੇ ਜਾਂ ਦਾਨ ਨੂੰ ਠੀਕ ਕਰਨ ਲਈ Reverse (ਮਾਈਨਸ / Negative) ਐਂਟਰੀ ਪਾਓ, ਤਾਂ ਜੋ ਲੈਜ਼ਰ ਸਹੀ ਰਹੇ।")
            with st.form("jv_adj_form", clear_on_submit=True):
                adj_target = st.selectbox("ਕੀ ਐਡਜਸਟ ਕਰਨਾ ਹੈ?", ["ਖਰਚਾ (Expense Adjustment)", "ਦਾਨ (Donation Adjustment)"])
                adj_desc = st.text_input("ਵੇਰਵਾ / ਨਾਮ (Description / Name)")
                
                if "ਖਰਚਾ" in adj_target:
                    cat_options = [c for c in config.EXPENSE_CATEGORIES if not c.startswith("---")]
                    adj_cat = st.selectbox("ਕੈਟਾਗਰੀ", cat_options)
                else:
                    adj_cat = st.selectbox("ਦਾਨ ਦੀ ਕਿਸਮ", ["ਪੈਸੇ (Monetary)"])
                    
                adj_amt = st.number_input("ਰਕਮ (Amount ₹) - Negative value to reverse/reduce!", value=-100.0)
                adj_bank = st.selectbox("ਬੈਂਕ/ਕੈਸ਼ ਖਾਤਾ", all_b)
                adj_dt = st.date_input("ਮਿਤੀ (Date)", value=date.today(), format="DD/MM/YYYY")
                
                if st.form_submit_button("ਐਡਜਸਟਮੈਂਟ ਸੇਵ ਕਰੋ", type="primary") and adj_desc:
                    dt_str = adj_dt.strftime("%Y-%m-%d")
                    if "ਖਰਚਾ" in adj_target:
                        utils.supabase.table("expenses").insert({"description": adj_desc + " (Reversal/Adj)", "amount": adj_amt, "date": dt_str, "category": adj_cat, "bank_account": adj_bank, "add_to_mirror": True, "payee_name": "Admin Adjustment"}).execute()
                    else:
                        utils.supabase.table("donations").insert({"id": int(time.time() % 100000), "name": adj_desc + " (Reversal/Adj)", "phone": "", "address": "", "amount": adj_amt, "date": dt_str, "payment_mode": "Adjustment", "donation_type": "ਪੈਸੇ (Monetary)", "item_details": "", "bank_account": adj_bank, "on_account_of": "Adjustment", "add_to_mirror": True, "collector_name": "Admin"}).execute()
                    st.success("✅ ਐਡਜਸਟਮੈਂਟ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!")

        st.markdown("---")
        st.write("#### 🕒 ਪਿਛਲੀਆਂ JV / ਮੈਨੂਅਲ ਐਂਟਰੀਆਂ")
        try:
            r = utils.supabase.table("bank_ledger").select("*").in_("source", ["Admin JV", "Admin Transfer", "Manual Entry"]).order("id", desc=True).limit(50).execute().data
            if r: st.dataframe(utils.format_dates_in_df(pd.DataFrame(r)[['id', 'txn_date', 'bank_name', 'description', 'debit', 'credit', 'source']], ascending=False), hide_index=True, use_container_width=True)
        except Exception: pass

    # ================= 2. BULK UPLOAD =================
    elif st.session_state.admin_mode == "📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)" and is_admin:
        st.write("### 📂 ਪੁਰਾਣਾ ਡਾਟਾ ਐਕਸਲ ਰਾਹੀਂ ਅੱਪਲੋਡ ਕਰੋ")
        upload_type = st.selectbox("ਡਾਟਾ ਚੁਣੋ", ["ਦਾਨ (Donations)", "ਵਿਦਿਆਰਥੀ (Students)", "ਵਿਧਵਾਵਾਂ (Widows)", "ਬੈਂਕ ਐਂਟਰੀਆਂ (Bank Ledger)"])
        default_bank_upload = st.selectbox("ਇਹ ਸਟੇਟਮੈਂਟ ਕਿਸ ਬੈਂਕ ਦੀ ਹੈ?", config.BANK_ACCOUNTS, index=1) if upload_type == "ਬੈਂਕ ਐਂਟਰੀਆਂ (Bank Ledger)" else "Kotak Bank Regular"
            
        uploaded_file = st.file_uploader("ਐਕਸਲ ਫਾਈਲ ਚੁਣੋ (.xlsx, .xls)", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            df_upload.columns = df_upload.columns.str.lower().str.replace(' ', '_').str.replace('-', '_').str.strip()
            df_upload = df_upload.astype(object).where(pd.notna(df_upload), None)
            st.dataframe(df_upload.head(10), use_container_width=True)
            
            if st.button(f"🚀 ਸਾਰਾ ਡਾਟਾ {upload_type} ਵਿੱਚ ਸੇਵ ਕਰੋ", type="primary"):
                try:
                    if upload_type == "ਦਾਨ (Donations)":
                        allowed_cols, table_name = ['id', 'date', 'name', 'phone', 'address', 'amount', 'payment_mode', 'cheque_no', 'cheque_bank', 'donation_type', 'item_details', 'bank_account', 'on_account_of', 'collector_name', 'add_to_mirror', 'balance'], "donations"
                    elif upload_type == "ਵਿਦਿਆਰਥੀ (Students)":
                        allowed_cols, table_name = ['name', 'phone', 'course', 'join_date', 'pass_date', 'photo_base64'], "students"
                    elif upload_type == "ਵਿਧਵਾਵਾਂ (Widows)":
                        allowed_cols, table_name = ['form_no', 'card_no', 'name', 'age', 'husband_name', 'husband_death_date', 'phone', 'address', 'boys_details', 'girls_details', 'issued_by', 'join_date', 'photo_base64'], "widows"
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
                            df_upload['txn_date'] = df_upload['txn_date'].apply(lambda d: utils.parse_date_to_obj(d).strftime('%Y-%m-%d') if utils.parse_date_to_obj(d) else str(d))
                        allowed_cols, table_name = ['txn_date', 'description', 'bank_name', 'debit', 'credit', 'balance', 'source'], "bank_ledger"

                    for c in allowed_cols:
                        if c not in df_upload.columns: df_upload[c] = None
                    df_upload = df_upload[allowed_cols]
                    records = df_upload.to_dict(orient='records')
                    for rec in records:
                        for k, v in rec.items():
                            if isinstance(v, float) and math.isnan(v): rec[k] = None

                    for i in range(0, len(records), 500): utils.supabase.table(table_name).insert(records[i:i+500]).execute()
                    st.success(f"✅ {upload_type} ਦਾ ਸਾਰਾ ਡਾਟਾ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਲੋਡ ਹੋ ਗਿਆ ਹੈ!")
                except Exception as e: st.error(f"❌ ਐਰਰ: {e}")

    # ================= 3. DELETE MANAGEMENT =================
    elif st.session_state.admin_mode == "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚੋਂ ਡਿਲੀਟ ਕਰਨਾ ਹੈ?", list(t_map.keys()), key="del_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="del_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="del_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="del_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []

        try: raw_data = utils.supabase.table(table_name).select("*").limit(100000).execute().data or []
        except Exception: raw_data = []

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
                    df_del['__temp_date'] = df_del[date_cols[0]].apply(utils.parse_date_to_obj)
                    df_del = df_del[(df_del['__temp_date'] >= d_start) & (df_del['__temp_date'] <= d_end)].drop(columns=['__temp_date'])
                    
            if not df_del.empty:
                st.success(f"✅ ਕੁੱਲ {len(df_del)} ਐਂਟਰੀਆਂ ਮਿਲੀਆਂ ਹਨ।")
                df_del.insert(0, "Select", False)
                edited_df = st.data_editor(utils.format_dates_in_df(df_del, ascending=False), column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=[c for c in df_del.columns if c != "Select"], hide_index=True, use_container_width=True, key=f"editor_delete_{table_name}")
                selected_rows = edited_df[edited_df["Select"] == True]
                if not selected_rows.empty:
                    if is_admin:
                        if st.button("🛑 ਪੱਕਾ ਡਿਲੀਟ ਕਰੋ (Delete)", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else int(float(row['id']))
                                col_name = "item_name" if table_name == "stock" else "id"
                                utils.supabase.table(table_name).delete().eq(col_name, rec_id).execute()
                            st.success("✅ ਡਿਲੀਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਬੇਨਤੀ ਭੇਜੋ", type="primary"):
                            for _, row in selected_rows.iterrows():
                                rec_id = row['item_name'] if table_name == "stock" else str(row['id'])
                                utils.supabase.table("deletion_requests").insert({"table_name": table_name, "record_id": str(rec_id), "details": str(row.drop('Select').to_dict()), "requested_by": "staff"}).execute()
                            st.success("✅ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")

    # ================= 4. EDIT MANAGEMENT =================
    elif st.session_state.admin_mode == "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚ ਸੋਧ ਕਰਨੀ ਹੈ?", list(t_map.keys()), key="edit_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="edit_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="edit_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="edit_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []
            
        try: raw_data = utils.supabase.table(table_name).select("*").limit(100000).execute().data or []
        except Exception: raw_data = []
            
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
                    df_edit['__temp_date'] = df_edit[date_cols[0]].apply(utils.parse_date_to_obj)
                    df_edit = df_edit[(df_edit['__temp_date'] >= d_start) & (df_edit['__temp_date'] <= d_end)].drop(columns=['__temp_date'])
                    
            if not df_edit.empty:
                st.success("✅ ਸਿੱਧਾ ਕਲਿੱਕ ਕਰਕੇ ਬਦਲਾਅ ਕਰੋ:")
                df_edit = utils.format_dates_in_df(df_edit, ascending=False).reset_index(drop=True).where(pd.notnull(df_edit), None)
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
                                obj = utils.parse_date_to_obj(ed[k])
                                changes[k] = obj.strftime('%Y-%m-%d') if obj else str(ed[k])
                            else: changes[k] = ed[k]
                    if changes: changed_rows.append((orig['item_name'] if table_name == 'stock' else orig['id'], changes))
                        
                if changed_rows:
                    if is_admin:
                        if st.button("💾 ਬਦਲਾਅ ਸੇਵ ਕਰੋ (Save)", type="primary"):
                            for rec_id, changes in changed_rows:
                                utils.supabase.table(table_name).update(changes).eq("item_name" if table_name == "stock" else "id", rec_id).execute()
                            st.success("✅ ਡਾਟਾਬੇਸ ਅਪਡੇਟ ਹੋ ਗਿਆ!"); time.sleep(1.5); st.rerun()
                    elif is_staff:
                        if st.button("📩 ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ ਲਈ ਭੇਜੋ", type="primary"):
                            for rec_id, changes in changed_rows:
                                utils.supabase.table("edit_requests").insert({"table_name": table_name, "record_id": str(rec_id), "changes": json.dumps(changes), "status": "Pending", "requested_by": "staff"}).execute()
                            st.success("✅ ਬੇਨਤੀ ਭੇਜ ਦਿੱਤੀ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
            else: st.info("ਕੋਈ ਐਂਟਰੀ ਨਹੀਂ ਮਿਲੀ।")
