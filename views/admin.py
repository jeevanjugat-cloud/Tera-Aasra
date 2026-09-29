import streamlit as st
import pandas as pd
from datetime import date
import json
import time
import math
import config
import utils

def show_page(is_admin, is_staff):
    st.header("⚙️ ਐਡਮਿਨ, ਡਿਲੀਟ ਅਤੇ ਸੋਧ (Edit) ਸਿਸਟਮ")
    modes = ["📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)", "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"] if is_admin else ["🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)", "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)"]
    if st.session_state.admin_mode not in modes: st.session_state.admin_mode = modes[0]
    st.session_state.admin_mode = st.radio("ਐਡਮਿਨ ਟੂਲ ਚੁਣੋ:", modes, index=modes.index(st.session_state.admin_mode), horizontal=True)
    st.markdown("---")
    
    t_map = {"ਦਾਨ (Donation)": "donations", "ਖਰਚਾ (Expense)": "expenses", "ਬੈਂਕ ਐਂਟਰੀ (Bank Ledger)": "bank_ledger", "ਪਾਰਟੀ (Party)": "parties", "ਚੈੱਕ (Cheque)": "cheques", "ਸੰਪਤੀ (Asset)": "assets", "ਦੇਣਦਾਰੀ (Liability)": "liabilities", "ਸਟਾਕ (Stock)": "stock", "ਸਟਾਕ ਵਰਤੋਂ (Stock Usage)": "stock_usage", "ਵਿਦਿਆਰਥੀ (Student)": "students", "ਵਿਧਵਾ (Widow)": "widows", "ਰਾਸ਼ਨ ਵੰਡ (Ration)": "ration_distribution", "ਰਸੀਦ ਕਿਤਾਬ (Receipt Book)": "receipt_books", "ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ (Staff)": "staff_profiles", "ਹਾਜ਼ਰੀ (Attendance)": "attendance"}

    if st.session_state.admin_mode == "📂 ਬਲਕ ਅੱਪਲੋਡ (Bulk Upload)" and is_admin:
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

                    # Batch insertion to avoid timeouts
                    for i in range(0, len(records), 500): utils.supabase.table(table_name).insert(records[i:i+500]).execute()
                    st.success(f"✅ {upload_type} ਦਾ ਸਾਰਾ ਡਾਟਾ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਲੋਡ ਹੋ ਗਿਆ ਹੈ!")
                except Exception as e: st.error(f"❌ ਐਰਰ: {e}")

    elif st.session_state.admin_mode == "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚੋਂ ਡਿਲੀਟ ਕਰਨਾ ਹੈ?", list(t_map.keys()), key="del_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="del_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="del_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="del_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []

        try: raw_data = utils.supabase.table(table_name).select("*").limit(100000).execute().data or []
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

    elif st.session_state.admin_mode == "✏️ ਸੋਧ ਮੈਨੇਜਮੈਂਟ (Edit)":
        table_name = t_map[st.selectbox("ਕਿਸ ਟੇਬਲ ਵਿੱਚ ਸੋਧ ਕਰਨੀ ਹੈ?", list(t_map.keys()), key="edit_cat")]
        col_f1, col_f2 = st.columns(2)
        with col_f1: search_name = st.text_input("ਨਾਮ/ਵੇਰਵੇ ਨਾਲ ਲੱਭੋ", key="edit_srch")
        with col_f2: 
            filter_date = st.checkbox("ਮਿਤੀ ਨਾਲ ਲੱਭੋ", key="edit_chk_dt")
            date_range = st.date_input("ਮਿਤੀ ਚੁਣੋ", [], key="edit_dt", min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY") if filter_date else []
            
        try: raw_data = utils.supabase.table(table_name).select("*").limit(100000).execute().data or []
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
