import streamlit as st
import pandas as pd
from datetime import date
import time
import urllib.parse
import config
import utils

def show_page(is_mgmt):
    st.header("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦ ਪ੍ਰਬੰਧਨ")
    modes = ["💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)", "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)", "📉 ਖਰਚਾ (Payment Debit)", "🏦 ਬੈਂਕ ਐਂਟਰੀ (Manual Bank Entry)", "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)", "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)"]
    if st.session_state.entry_mode not in modes: st.session_state.entry_mode = modes[0]
    st.session_state.entry_mode = st.radio("ਐਂਟਰੀ ਦੀ ਕਿਸਮ ਚੁਣੋ:", modes, index=modes.index(st.session_state.entry_mode), horizontal=True)
    st.markdown("---")

    if st.session_state.entry_mode == "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)":
        if not is_mgmt:
            st.write("### 💰 ਨਵਾਂ ਦਾਨ ਦਰਜ ਕਰੋ ਅਤੇ ਰਸੀਦ ਬਣਾਓ")
            try: don_data = utils.supabase.table("donations").select("*").limit(100000).execute().data or []
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
                with col_m2: bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ?", config.BANK_ACCOUNTS); receipt_date = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                cq_no, cq_bank = "", ""
                if pay_mode == "Cheque":
                    cc1, cc2 = st.columns(2)
                    with cc1: cq_no = st.text_input("ਚੈੱਕ ਨੰਬਰ")
                    with cc2: cq_bank = st.text_input("ਬੈਂਕ ਦਾ ਨਾਮ")
                add_to_mirror = st.checkbox("✅ ਇਸ ਦਾਨ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                submitted = st.form_submit_button("ਸੇਵ ਕਰੋ ਅਤੇ ਰਸੀਦ ਤਿਆਰ ਕਰੋ", type="primary")
                
            if submitted and donor_name:
                books = utils.supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book = next((b for b in books if int(b['start_no']) <= int(rec_no_input) <= int(b['end_no'])), None)
                existing_rec = utils.supabase.table("donations").select("id").eq("id", int(rec_no_input)).execute().data
                
                if not matched_book: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਕਿਸੇ ਵੀ ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif existing_rec: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ!")
                else:
                    collector = matched_book['collector_name']
                    formatted_date = receipt_date.strftime("%Y-%m-%d")
                    utils.supabase.table("donations").insert({"id": int(rec_no_input), "name": donor_name, "phone": donor_phone, "address": donor_address, "amount": amount, "date": formatted_date, "payment_mode": pay_mode, "donation_type": "ਪੈਸੇ (Monetary)", "item_details": "", "bank_account": bank_acc, "on_account_of": on_account_of, "add_to_mirror": add_to_mirror, "collector_name": collector, "cheque_no": cq_no, "cheque_bank": cq_bank}).execute()
                    st.success(f"✅ ਰਸੀਦ #{rec_no_input} ਸੇਵ ਹੋ ਗਈ!")
                    html_file = utils.generate_html_receipt(int(rec_no_input), donor_name, donor_phone, amount, utils.clean_date_to_display(formatted_date), pay_mode, "ਪੈਸੇ (Monetary)", "", bank_acc, on_account_of, collector, donor_address, cq_no, cq_bank)
                    with open(html_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ/ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file, mime="text/html", type="primary")
            
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ")
            if don_data:
                df_rec = pd.DataFrame([d for d in don_data if d.get('donation_type') == "ਪੈਸੇ (Monetary)"])
                if not df_rec.empty:
                    disp_cols = [c for c in ['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name'] if c in df_rec.columns]
                    df_rec = utils.format_dates_in_df(df_rec[disp_cols], ascending=False)
                    df_rec.insert(0, "Select", False)
                    edited_df = st.data_editor(df_rec, column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=disp_cols, hide_index=True, use_container_width=True)
                    selected_ids = edited_df[edited_df["Select"] == True]['id'].tolist()
                    if selected_ids:
                        for sid in selected_ids:
                            row_data = next(r for r in don_data if r['id'] == sid)
                            h_file = utils.generate_html_receipt(row_data['id'], row_data.get('name',''), row_data.get('phone',''), float(row_data.get('amount',0) or 0), utils.clean_date_to_display(row_data.get('date','')), row_data.get('payment_mode','N/A'), "ਪੈਸੇ (Monetary)", "", row_data.get('bank_account','N/A'), row_data.get('on_account_of',''), row_data.get('collector_name', ''), row_data.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), row_data.get('cheque_no', ''), row_data.get('cheque_bank', ''))
                            with open(h_file, "r", encoding="utf-8") as f: st.download_button(f"🖨️ Print #{row_data['id']}", data=f.read(), file_name=h_file, mime="text/html")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)":
        if not is_mgmt:
            st.write("### 📦 ਸਮਾਨ ਦਾ ਦਾਨ ਦਰਜ ਕਰੋ")
            try: ik_data = utils.supabase.table("donations").select("*").limit(100000).execute().data or []
            except: ik_data = []
            
            unique_donors_ik = list({d['name']: d for d in ik_data if d.get('name') and str(d.get('name')).strip() != ""}.keys())
            sel_donor_ik = st.selectbox("ਪੁਰਾਣਾ ਦਾਨੀ ਲੱਭੋ", ["➕ ਨਵਾਂ ਦਾਨੀ (New Donor)"] + unique_donors_ik)
            match_ik = next((d for d in reversed(ik_data) if d.get('name') == sel_donor_ik), {}) if sel_donor_ik != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else {}
            
            with st.form("inkind_form", clear_on_submit=True):
                donor_name_ik = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ", value=sel_donor_ik if sel_donor_ik != "➕ ਨਵਾਂ ਦਾਨੀ (New Donor)" else "")
                donor_phone_ik = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Optional)", value=match_ik.get('phone', ''))
                donor_address_ik = st.text_input("ਪਤਾ", value=match_ik.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'))
                item_details_ik = st.text_input("ਰਸੀਦ 'ਤੇ ਛਾਪਣ ਲਈ ਸਮਾਨ ਦਾ ਵੇਰਵਾ")
                rec_no_ik = st.number_input("ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1)
                col_k1, col_k2 = st.columns(2)
                with col_k1: amount_ik = st.number_input("ਅੰਦਾਜ਼ਨ ਕੀਮਤ (₹)", min_value=0.0)
                with col_k2: receipt_date_ik = st.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                
                add_destination = st.radio("ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ?", ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ"], horizontal=True)
                try: stock_opts_ik = [s['item_name'] for s in utils.supabase.table("stock").select("item_name").limit(50000).execute().data] + ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                except: stock_opts_ik = ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                col_s1, col_s2 = st.columns(2)
                with col_s1: s_item_sel_ik = st.selectbox("ਮੌਜੂਦਾ ਲਿਸਟ ਵਿੱਚੋਂ ਚੁਣੋ", stock_opts_ik); s_qty_ik = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5)
                with col_s2: s_item_new_ik = st.text_input("ਜਾਂ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"); s_unit_ik = st.selectbox("ਇਕਾਈ (Unit)", config.STOCK_UNITS)
                s_type_ik = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", config.ASSET_TYPES)
                
                submitted_ik = st.form_submit_button("ਸਮਾਨ ਦੀ ਰਸੀਦ ਬਣਾਓ", type="primary")
                
            if submitted_ik and donor_name_ik and item_details_ik:
                final_item_ik = s_item_new_ik.strip() if s_item_sel_ik == "➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ" else s_item_sel_ik.strip()
                is_whole_ik = any(u in s_unit_ik for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                books_ik = utils.supabase.table("receipt_books").select("*").eq("status", "Active").execute().data or []
                matched_book_ik = next((b for b in books_ik if int(b['start_no']) <= int(rec_no_ik) <= int(b['end_no'])), None)
                
                if add_destination != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and not final_item_ik: st.error("❌ ਗਲਤੀ: ਸਮਾਨ ਦਾ ਨਾਮ ਦਿਓ!")
                elif add_destination != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and is_whole_ik and not float(s_qty_ik).is_integer(): st.error("❌ ਗਲਤੀ: ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                elif not matched_book_ik: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਜਾਰੀ ਕੀਤੀ ਕਿਤਾਬ ਵਿੱਚ ਨਹੀਂ ਹੈ!")
                elif utils.supabase.table("donations").select("id").eq("id", int(rec_no_ik)).execute().data: st.error("❌ ਗਲਤੀ: ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ!")
                else:
                    collector_ik = matched_book_ik['collector_name']
                    formatted_date_ik = receipt_date_ik.strftime("%Y-%m-%d")
                    utils.supabase.table("donations").insert({"id": int(rec_no_ik), "name": donor_name_ik, "phone": donor_phone_ik, "address": donor_address_ik, "amount": amount_ik, "date": formatted_date_ik, "payment_mode": "N/A", "donation_type": "ਸਮਾਨ (In-Kind / Ration)", "item_details": item_details_ik, "bank_account": "N/A", "on_account_of": "ਸਮਾਨ ਦਾਨ", "add_to_mirror": False, "collector_name": collector_ik}).execute()
                    
                    if add_destination == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ" and final_item_ik and s_qty_ik > 0:
                        from datetime import datetime
                        res_stock = utils.supabase.table("stock").select("*").eq("item_name", final_item_ik).execute()
                        if res_stock.data:
                            old_qty, old_val = float(res_stock.data[0].get('quantity', 0)), float(res_stock.data[0].get('estimated_value', 0))
                            utils.supabase.table("stock").update({"quantity": old_qty + s_qty_ik, "estimated_value": round(old_val + amount_ik, 2), "unit": s_unit_ik, "procurement_date": formatted_date_ik, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", final_item_ik).execute()
                        else:
                            utils.supabase.table("stock").insert({"item_name": final_item_ik, "quantity": s_qty_ik, "estimated_value": round(amount_ik, 2), "unit": s_unit_ik, "procurement_date": formatted_date_ik, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()
                        st.success("✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ ਸਟਾਕ ਜੁੜ ਗਿਆ!")
                    elif add_destination == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ" and final_item_ik:
                        utils.supabase.table("assets").insert({"name": final_item_ik, "asset_type": s_type_ik, "value": amount_ik, "quantity": s_qty_ik, "date_added": formatted_date_ik}).execute()
                        st.success("✅ ਰਸੀਦ ਬਣ ਗਈ ਅਤੇ ਪੱਕੀ ਸੰਪਤੀ ਜੁੜ ਗਈ!")
                    else: st.success(f"✅ ਰਸੀਦ #{rec_no_ik} ਤਿਆਰ ਹੈ।")
                    
                    html_file_ik = utils.generate_html_receipt(int(rec_no_ik), donor_name_ik, donor_phone_ik, amount_ik, utils.clean_date_to_display(formatted_date_ik), "N/A", "ਸਮਾਨ (In-Kind / Ration)", item_details_ik, "N/A", "ਸਮਾਨ ਦਾਨ", collector_ik, donor_address_ik)
                    with open(html_file_ik, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file_ik, mime="text/html", type="primary")
            st.markdown("---")
            if ik_data: 
                df_ik = pd.DataFrame([d for d in ik_data if d.get('donation_type') == "ਸਮਾਨ (In-Kind / Ration)"])
                if not df_ik.empty:
                    disp_cols_ik = [c for c in ['id', 'date', 'name', 'phone', 'item_details', 'amount'] if c in df_ik.columns]
                    st.dataframe(utils.format_dates_in_df(df_ik[disp_cols_ik], ascending=False), hide_index=True, use_container_width=True)
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📉 ਖਰਚਾ (Payment Debit)":
        if not is_mgmt:
            with st.form("expense_form", clear_on_submit=True):
                st.write("### 📉 ਖਰਚਾ ਜਾਂ ਪੇਮੈਂਟ ਦਰਜ ਕਰੋ")
                desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ")
                cat = st.selectbox("ਕੈਟਾਗਰੀ", [c for c in config.EXPENSE_CATEGORIES if not c.startswith("---")])
                exp_amount = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ?", config.BANK_ACCOUNTS)
                exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                add_destination_exp = st.radio("ਖਰੀਦੇ ਗਏ ਸਮਾਨ ਨੂੰ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ?", ["ਕਿਤੇ ਨਹੀਂ (Do not add)", "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ"], horizontal=True)
                
                try: stock_opts_exp = [s['item_name'] for s in utils.supabase.table("stock").select("item_name").limit(50000).execute().data] + ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                except: stock_opts_exp = ["➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"]
                
                col_es1, col_es2 = st.columns(2)
                with col_es1: s_item_sel_exp = st.selectbox("ਮੌਜੂਦਾ ਲਿਸਟ ਵਿੱਚੋਂ ਚੁਣੋ", stock_opts_exp); s_qty_exp = st.number_input("ਮਾਤਰਾ (Qty)", min_value=0.0, step=0.5)
                with col_es2: s_item_new_exp = st.text_input("ਜਾਂ ਨਵਾਂ ਨਾਮ ਲਿਖੋ"); s_unit_exp = st.selectbox("ਇਕਾਈ", config.STOCK_UNITS)
                s_type_exp = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", config.ASSET_TYPES)
                
                submitted_exp = st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ", type="primary")
                
            if submitted_exp and desc:
                from datetime import datetime
                final_item_exp = s_item_new_exp.strip() if s_item_sel_exp == "➕ ਨਵਾਂ ਨਾਮ ਲਿਖੋ" else s_item_sel_exp.strip()
                is_whole_exp = any(u in s_unit_exp for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                if add_destination_exp != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and not final_item_exp: st.error("❌ ਗਲਤੀ: ਸਮਾਨ ਦਾ ਨਾਮ ਦਿਓ!")
                elif add_destination_exp != "ਕਿਤੇ ਨਹੀਂ (Do not add)" and is_whole_exp and not float(s_qty_exp).is_integer(): st.error("❌ ਗਲਤੀ: ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                else:
                    res_ins = utils.supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": exp_date.strftime("%Y-%m-%d"), "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp}).execute()
                    inserted_id = res_ins.data[0]['id'] if res_ins.data else "N/A"
                    if add_destination_exp == "📦 ਸਟਾਕ ਵਿੱਚ ਜੋੜੋ" and final_item_exp and s_qty_exp > 0:
                        res_stock = utils.supabase.table("stock").select("*").eq("item_name", final_item_exp).execute()
                        if res_stock.data:
                            old_qty, old_val = float(res_stock.data[0].get('quantity', 0)), float(res_stock.data[0].get('estimated_value', 0))
                            utils.supabase.table("stock").update({"quantity": old_qty + s_qty_exp, "estimated_value": round(old_val + exp_amount, 2), "unit": s_unit_exp, "procurement_date": exp_date.strftime("%Y-%m-%d"), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", final_item_exp).execute()
                        else:
                            utils.supabase.table("stock").insert({"item_name": final_item_exp, "quantity": s_qty_exp, "estimated_value": round(exp_amount, 2), "unit": s_unit_exp, "procurement_date": exp_date.strftime("%Y-%m-%d"), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()
                        st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ ਸਟਾਕ ਜੁੜ ਗਿਆ!")
                    elif add_destination_exp == "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ ਜੋੜੋ" and final_item_exp and s_qty_exp > 0:
                        utils.supabase.table("assets").insert({"name": final_item_exp, "asset_type": s_type_exp, "value": exp_amount, "quantity": s_qty_exp, "date_added": str(exp_date)}).execute()
                        st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ ਅਤੇ ਸੰਪਤੀ ਜੁੜ ਗਈ!")
                    else: st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ!")

                    if inserted_id != "N/A":
                        html_file_exp = utils.generate_html_expense_voucher(inserted_id, desc, exp_amount, utils.clean_date_to_display(exp_date.strftime("%Y-%m-%d")), cat, bank_acc_exp)
                        with open(html_file_exp, "r", encoding="utf-8") as file: st.download_button("🖨️ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_exp, mime="text/html", type="primary")
            st.markdown("---")
            try:
                recents = utils.supabase.table("expenses").select("*").order("id", desc=True).limit(50).execute().data
                if recents: 
                    df_exp_disp = pd.DataFrame(recents)[['id', 'date', 'description', 'amount', 'category', 'bank_account']]
                    df_exp_disp.insert(0, "Select", False)
                    edited_exp_df = st.data_editor(utils.format_dates_in_df(df_exp_disp, ascending=False), column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=['id', 'date', 'description', 'amount', 'category', 'bank_account'], hide_index=True, use_container_width=True)
                    selected_exp_ids = edited_exp_df[edited_exp_df["Select"] == True]['id'].tolist()
                    if selected_exp_ids:
                        for sid in selected_exp_ids:
                            row_data = next(r for r in recents if r['id'] == sid)
                            h_file = utils.generate_html_expense_voucher(row_data['id'], row_data.get('description',''), float(row_data.get('amount',0)), utils.clean_date_to_display(row_data.get('date','')), row_data.get('category',''), row_data.get('bank_account',''))
                            with open(h_file, "r", encoding="utf-8") as f: st.download_button(f"🖨️ Print #{sid}", data=f.read(), file_name=h_file, mime="text/html")
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "🏦 ਬੈਂਕ ਐਂਟਰੀ (Manual Bank Entry)":
        if not is_mgmt:
            with st.form("manual_bank_form", clear_on_submit=True):
                st.write("### 🏦 ਮੈਨੂਅਲ ਬੈਂਕ ਐਂਟਰੀ")
                b_acc = st.selectbox("ਬੈਂਕ ਖਾਤਾ", config.BANK_ACCOUNTS)
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
                        utils.supabase.table("bank_ledger").insert({"txn_date": b_date.strftime("%Y-%m-%d"), "description": b_desc, "bank_name": b_acc, "debit": float(debit_val), "credit": float(credit_val), "balance": 0.0, "source": "Manual Entry"}).execute()
                        st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!")
            st.markdown("---")
            try:
                recents = utils.supabase.table("bank_ledger").select("*").eq("source", "Manual Entry").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(utils.format_dates_in_df(pd.DataFrame(recents)[['id', 'txn_date', 'bank_name', 'description', 'debit', 'credit']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)":
        if not is_mgmt:
            with st.form("party_form", clear_on_submit=True):
                st.write("### 📁 ਨਵੀਂ ਪਾਰਟੀ ਜਾਂ ਵੈਂਡਰ ਬਣਾਓ")
                p_name = st.text_input("ਪਾਰਟੀ ਦਾ ਨਾਮ")
                p_type = st.selectbox("ਖਾਤੇ ਦੀ ਕਿਸਮ", ["Sundry Creditor (ਦੇਣਦਾਰ)", "Sundry Debtor (ਪਾਉਣਦਾਰ)"])
                p_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                p_address = st.text_input("ਪਤਾ")
                p_amount = st.number_input("ਸ਼ੁਰੂਆਤੀ ਬੈਲੇਂਸ (₹)", min_value=0.0)
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and p_name:
                    utils.supabase.table("parties").insert({"name": p_name, "party_type": p_type, "phone": p_phone, "address": p_address, "opening_balance": p_amount, "created_at": str(date.today())}).execute()
                    st.success(f"✅ ਪਾਰਟੀ ਸੇਵ ਹੋ ਗਈ!")
            st.markdown("---")
            try:
                recents = utils.supabase.table("parties").select("*").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(utils.format_dates_in_df(pd.DataFrame(recents)[['id', 'name', 'party_type', 'opening_balance']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)":
        if not is_mgmt:
            with st.form("cheque_form", clear_on_submit=True):
                st.write("### 💳 ਚੈੱਕ ਜਾਰੀ ਕਰਨ ਦੀ ਐਂਟਰੀ")
                cq_no = st.text_input("ਚੈੱਕ ਨੰਬਰ")
                cq_bank = st.selectbox("ਬੈਂਕ ਖਾਤਾ", config.BANK_ACCOUNTS)
                cq_party = st.text_input("ਕਿਸ ਨੂੰ ਦਿੱਤਾ/ਲਿਆ")
                cq_amt = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                cq_date = st.date_input("ਚੈੱਕ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                cq_status = st.selectbox("ਸਟੇਟਸ", ["Pending", "Cleared", "Cancelled"])
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and cq_no:
                    utils.supabase.table("cheques").insert({"cheque_no": cq_no, "bank_name": cq_bank, "party_name": cq_party, "amount": cq_amt, "cheque_date": str(cq_date), "status": cq_status}).execute()
                    st.success("✅ ਚੈੱਕ ਸੇਵ ਹੋ ਗਿਆ!")
            st.markdown("---")
            try:
                recents = utils.supabase.table("cheques").select("*").order("id", desc=True).limit(50).execute().data
                if recents: st.dataframe(utils.format_dates_in_df(pd.DataFrame(recents)[['id', 'cheque_date', 'cheque_no', 'party_name', 'amount', 'status']], ascending=False), hide_index=True, use_container_width=True)
            except: pass
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)":
        st.write("### 🖨️ ਪੁਰਾਣੀ ਰਸੀਦ ਜਾਂ ਖਰਚਾ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ")
        rep_type = st.radio("ਕੀ ਪ੍ਰਿੰਟ ਕਰਨਾ ਹੈ?", ["ਦਾਨ ਰਸੀਦ", "ਖਰਚਾ ਵਾਊਚਰ"], horizontal=True)
        col_search1, col_search2 = st.columns(2)
        
        if rep_type == "ਦਾਨ ਰਸੀਦ":
            with col_search1:
                search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ ਭਰੋ", min_value=1, step=1)
                if st.button("🔍 ਰਸੀਦ ਲੱਭੋ", type="primary"):
                    res = utils.supabase.table("donations").select("*").eq("id", search_id).execute()
                    if res.data:
                        rec = res.data[0]
                        html_file_rep = utils.generate_html_receipt(search_id, rec.get('name',''), rec.get('phone',''), rec.get('amount',0), utils.clean_date_to_display(rec.get('date','')), rec.get('payment_mode','N/A'), rec.get('donation_type','ਪੈਸੇ (Monetary)'), rec.get('item_details',''), rec.get('bank_account','N/A'), rec.get('on_account_of',''), rec.get('collector_name', ''), rec.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), rec.get('cheque_no', ''), rec.get('cheque_bank', ''))
                        st.success("✅ ਰਸੀਦ ਮਿਲ ਗਈ ਹੈ!")
                        with open(html_file_rep, "r", encoding="utf-8") as file: st.download_button("🖨️ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file_rep, mime="text/html", type="primary")
                    else: st.error("❌ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ।")
            with col_search2:
                search_donor = st.text_input("ਦਾਨੀ ਦੇ ਨਾਮ ਨਾਲ ਖੋਜ ਕਰੋ")
                if search_donor:
                    df_don = pd.DataFrame(utils.supabase.table("donations").select("*").limit(100000).execute().data or [])
                    if not df_don.empty:
                        matches = df_don[df_don['name'].str.contains(search_donor, case=False, na=False)]
                        if not matches.empty: st.dataframe(utils.format_dates_in_df(matches[['id', 'date', 'name', 'phone', 'amount']].copy(), ascending=False), hide_index=True)
                            
        elif rep_type == "ਖਰਚਾ ਵਾਊਚਰ":
            with col_search1:
                search_id_exp = st.number_input("ਵਾਊਚਰ ਨੰਬਰ ਭਰੋ", min_value=1, step=1)
                if st.button("🔍 ਵਾਊਚਰ ਲੱਭੋ", type="primary"):
                    res = utils.supabase.table("expenses").select("*").eq("id", search_id_exp).execute()
                    if res.data:
                        rec = res.data[0]
                        html_file_rep = utils.generate_html_expense_voucher(search_id_exp, rec.get('description',''), rec.get('amount',0), utils.clean_date_to_display(rec.get('date','')), rec.get('category',''), rec.get('bank_account','N/A'))
                        st.success("✅ ਵਾਊਚਰ ਮਿਲ ਗਿਆ ਹੈ!")
                        with open(html_file_rep, "r", encoding="utf-8") as file: st.download_button("🖨️ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_rep, mime="text/html", type="primary")
                    else: st.error("❌ ਵਾਊਚਰ ਨਹੀਂ ਮਿਲਿਆ।")
            with col_search2:
                search_desc = st.text_input("ਵੇਰਵੇ ਨਾਲ ਖੋਜ ਕਰੋ")
                if search_desc:
                    df_exp_all = pd.DataFrame(utils.supabase.table("expenses").select("*").limit(100000).execute().data or [])
                    if not df_exp_all.empty:
                        matches = df_exp_all[df_exp_all['description'].str.contains(search_desc, case=False, na=False)]
                        if not matches.empty: st.dataframe(utils.format_dates_in_df(matches[['id', 'date', 'description', 'amount', 'category']].copy(), ascending=False), hide_index=True)
