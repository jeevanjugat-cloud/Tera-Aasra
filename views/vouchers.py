import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
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
                    
                    wa_msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ ਜੀ।\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ, ਤੁਹਾਡਾ ਦਾਨ (Rs. {amount}) ਪ੍ਰਾਪਤ ਹੋਇਆ ਹੈ। ਰਸੀਦ ਨੰਬਰ: {rec_no_input}। ਤੇਰਾ ਆਸਰਾ ਵੱਲੋਂ ਧੰਨਵਾਦ।"
                    wa_url = utils.wa_link(donor_phone, wa_msg)
                    if wa_url:
                        st.markdown(f"""<a href="{wa_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #25D366; color: white; border-radius: 8px; font-weight: bold; text-decoration: none;">💬 WhatsApp 'ਤੇ ਰਸੀਦ ਭੇਜੋ</a>""", unsafe_allow_html=True)
            
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ (Recent Entries)")
            if don_data:
                df_rec = pd.DataFrame([d for d in don_data if d.get('donation_type') == "ਪੈਸੇ (Monetary)"])
                if not df_rec.empty:
                    disp_cols = [c for c in ['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name'] if c in df_rec.columns]
                    df_rec = utils.format_dates_in_df(df_rec[disp_cols], ascending=False)
                    df_rec.insert(0, "Select", False)
                    edited_df = st.data_editor(df_rec, column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=disp_cols, hide_index=True, use_container_width=True, key="editor_donations")
                    utils.create_print_button(df_rec.drop(columns=['Select']), "Recent Donations", "🖨 ਦਾਨ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ")

                    selected_ids = edited_df[edited_df["Select"] == True]['id'].tolist()
                    if selected_ids:
                        for sid in selected_ids:
                            row_data = next(r for r in don_data if r['id'] == sid)
                            hf = utils.generate_html_receipt(
                                row_data['id'], row_data.get('name',''), row_data.get('phone',''), 
                                float(row_data.get('amount',0) or 0), utils.clean_date_to_display(row_data.get('date','')), 
                                row_data.get('payment_mode','N/A'), "ਪੈਸੇ (Monetary)", "", 
                                row_data.get('bank_account','N/A'), row_data.get('on_account_of',''), 
                                row_data.get('collector_name', ''), row_data.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), 
                                row_data.get('cheque_no', ''), row_data.get('cheque_bank', '')
                            )
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                with open(hf, "r", encoding="utf-8") as f:
                                    st.download_button(f"🖨️ ਰਸੀਦ #{sid} ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=hf, mime="text/html", key=f"print_don_{sid}")
                            with c2:
                                wa_msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ ਜੀ।\nਸਤਿਕਾਰਯੋਗ {row_data.get('name','')} ਜੀ, ਤੁਹਾਡਾ ਦਾਨ (Rs. {row_data.get('amount',0)}) ਪ੍ਰਾਪਤ ਹੋਇਆ ਹੈ। ਰਸੀਦ ਨੰਬਰ: {sid}। ਤੇਰਾ ਆਸਰਾ ਵੱਲੋਂ ਧੰਨਵਾਦ।"
                                wa_url = utils.wa_link(row_data.get('phone',''), wa_msg)
                                if wa_url:
                                    st.markdown(f"""<a href="{wa_url}" target="_blank" style="display: inline-block; padding: 5px 15px; background-color: #25D366; color: white; border-radius: 5px; font-weight: bold; text-decoration: none; font-size: 14px; margin-top: 2px;">💬 WhatsApp #{sid}</a>""", unsafe_allow_html=True)

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
                donor_address_ik = st.text_input("ਪਤਾ", value=match.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'))
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
                    with open(html_file_ik, "r", encoding="utf-8") as file: st.download_button("🖨 ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file_ik, mime="text/html", type="primary")
            
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ (Recent Entries)")
            if ik_data: 
                df_ik = pd.DataFrame([d for d in ik_data if d.get('donation_type') == "ਸਮਾਨ (In-Kind / Ration)"])
                if not df_ik.empty:
                    disp_cols_ik = [c for c in ['id', 'date', 'name', 'phone', 'item_details', 'amount'] if c in df_ik.columns]
                    df_disp = utils.format_dates_in_df(df_ik[disp_cols_ik], ascending=False)
                    
                    df_disp.insert(0, "Select", False)
                    edited_ik_df = st.data_editor(df_disp, column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=disp_cols_ik, hide_index=True, use_container_width=True, key="editor_inkind")
                    utils.create_print_button(df_disp.drop(columns=['Select']), "In-Kind Donations", "🖨️ ਸਮਾਨ ਦਾਨ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ")

                    selected_ik_ids = edited_ik_df[edited_ik_df["Select"] == True]['id'].tolist()
                    if selected_ik_ids:
                        for sid in selected_ik_ids:
                            row_data = next(r for r in ik_data if r['id'] == sid)
                            hf = utils.generate_html_receipt(
                                row_data['id'], row_data.get('name',''), row_data.get('phone',''), 
                                float(row_data.get('amount',0) or 0), utils.clean_date_to_display(row_data.get('date','')), 
                                "N/A", "ਸਮਾਨ (In-Kind / Ration)", row_data.get('item_details',''), 
                                "N/A", "ਸਮਾਨ ਦਾਨ", row_data.get('collector_name',''), row_data.get('address','ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ')
                            )
                            with open(hf, "r", encoding="utf-8") as f:
                                st.download_button(f"🖨️ ਰਸੀਦ #{sid} ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=hf, mime="text/html", key=f"print_ik_{sid}")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    elif st.session_state.entry_mode == "📉 ਖਰਚਾ (Payment Debit)":
        if not is_mgmt:
            st.write("### 📉 ਖਰਚਾ ਜਾਂ ਪੇਮੈਂਟ ਦਰਜ ਕਰੋ")
            try: exp_data_list = utils.supabase.table("expenses").select("payee_name").limit(100000).execute().data or []
            except: exp_data_list = []
            
            # --- PAYEE DROPDOWN LOGIC ---
            unique_payees = sorted(list({e.get('payee_name') for e in exp_data_list if e.get('payee_name') and str(e.get('payee_name')).strip() != ""}))
            sel_payee = st.selectbox("ਪੁਰਾਣਾ ਪ੍ਰਾਪਤ ਕਰਤਾ ਲੱਭੋ (Select Payee)", ["➕ ਨਵਾਂ ਪ੍ਰਾਪਤ ਕਰਤਾ (New Payee)"] + unique_payees)
            
            with st.form("expense_form", clear_on_submit=True):
                # Auto-fill Payee Name if selected from Dropdown
                payee_name = st.text_input("ਭੁਗਤਾਨ ਕਿਸ ਨੂੰ ਕੀਤਾ / ਪ੍ਰਾਪਤ ਕਰਤਾ (Payee Name)", value=sel_payee if sel_payee != "➕ ਨਵਾਂ ਪ੍ਰਾਪਤ ਕਰਤਾ (New Payee)" else "")
                desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Description)")
                
                cat_options = [c for c in config.EXPENSE_CATEGORIES if not c.startswith("---")] + ["➕ ਹੋਰ ਨਵਾਂ ਖਰਚਾ ਹੈੱਡ (Add New Expense Head)"]
                cat = st.selectbox("ਕੈਟਾਗਰੀ", cat_options)
                new_cat = st.text_input("ਨਵੇਂ ਖਰਚੇ ਦਾ ਹੈੱਡ ਦਰਜ ਕਰੋ (Enter New Expense Head Name)") if cat == "➕ ਹੋਰ ਨਵਾਂ ਖਰਚਾ ਹੈੱਡ (Add New Expense Head)" else ""
                
                exp_amount = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ?", config.BANK_ACCOUNTS)
                exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                
                add_dest = st.radio("ਖਰੀਦਿਆ ਸਮਾਨ ਕਿੱਥੇ ਜੋੜਨਾ ਹੈ?", ["ਕਿਤੇ ਨਹੀਂ", "📦 ਸਟਾਕ ਵਿੱਚ", "🏢 ਪੱਕੀ ਸੰਪਤੀ ਵਿੱਚ"], horizontal=True)
                try: stock_opts = [s['item_name'] for s in utils.supabase.table("stock").select("item_name").limit(50000).execute().data] + ["➕ ਨਵਾਂ ਨਾਮ"]
                except: stock_opts = ["➕ ਨਵਾਂ ਨਾਮ"]
                c1, c2 = st.columns(2)
                with c1: s_sel = st.selectbox("ਸਟਾਕ ਲਿਸਟ", stock_opts); s_qty = st.number_input("ਮਾਤਰਾ", min_value=0.0, step=0.5)
                with c2: s_new = st.text_input("ਨਵਾਂ ਨਾਮ"); s_unit = st.selectbox("ਇਕਾਈ", config.STOCK_UNITS)
                s_type = st.selectbox("ਸੰਪਤੀ ਕਿਸਮ", config.ASSET_TYPES)
                
                submitted_exp = st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ", type="primary")
                
            if submitted_exp and desc:
                final_cat = new_cat.strip() if new_cat else cat
                f_dt = exp_date.strftime("%Y-%m-%d")
                res_ins = utils.supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": f_dt, "category": final_cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp, "payee_name": payee_name}).execute()
                inserted_id = res_ins.data[0]['id'] if res_ins.data else "N/A"
                st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ!")
                
                if inserted_id != "N/A":
                    html_file_exp = utils.generate_html_expense_voucher(inserted_id, desc + f" (Payee: {payee_name})", exp_amount, utils.clean_date_to_display(f_dt), final_cat, bank_acc_exp)
                    with open(html_file_exp, "r", encoding="utf-8") as file: st.download_button("🖨️ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_exp, mime="text/html", type="primary")
                    
                if add_dest == "📦 ਸਟਾਕ ਵਿੱਚ" and final_cat and s_qty > 0:
                    f_item = s_new.strip() if s_sel == "➕ ਨਵਾਂ ਨਾਮ" else s_sel.strip()
                    if f_item:
                        rs = utils.supabase.table("stock").select("*").eq("item_name", f_item).execute().data
                        if rs: utils.supabase.table("stock").update({"quantity": float(rs[0].get('quantity',0)) + s_qty, "estimated_value": round(float(rs[0].get('estimated_value',0)) + exp_amount, 2), "unit": s_unit, "procurement_date": f_dt, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", f_item).execute()
                        else: utils.supabase.table("stock").insert({"item_name": f_item, "quantity": s_qty, "estimated_value": round(exp_amount, 2), "unit": s_unit, "procurement_date": f_dt, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()

            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ (Recent Entries)")
            try:
                recents = utils.supabase.table("expenses").select("*").order("id", desc=True).limit(50).execute().data
                if recents: 
                    df_exp_disp = pd.DataFrame(recents)[['id', 'date', 'payee_name', 'description', 'amount', 'category', 'bank_account']]
                    df_exp_disp = utils.format_dates_in_df(df_exp_disp, ascending=False)
                    
                    df_exp_disp.insert(0, "Select", False)
                    edited_exp_df = st.data_editor(df_exp_disp, column_config={"Select": st.column_config.CheckboxColumn("ਚੁਣੋ", default=False)}, disabled=[c for c in df_exp_disp.columns if c != 'Select'], hide_index=True, use_container_width=True, key="editor_expenses")
                    utils.create_print_button(df_exp_disp.drop(columns=['Select']), "Expense List", "🖨️ ਖਰਚਾ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", landscape=True)

                    selected_exp_ids = edited_exp_df[edited_exp_df["Select"] == True]['id'].tolist()
                    if selected_exp_ids:
                        for sid in selected_exp_ids:
                            row_data = next(r for r in recents if r['id'] == sid)
                            desc_with_payee = str(row_data.get('description','')) + f" (Payee: {row_data.get('payee_name', '')})"
                            hf = utils.generate_html_expense_voucher(
                                row_data['id'], desc_with_payee, float(row_data.get('amount',0)), 
                                utils.clean_date_to_display(row_data.get('date','')), row_data.get('category',''), row_data.get('bank_account','')
                            )
                            with open(hf, "r", encoding="utf-8") as f:
                                st.download_button(f"🖨️ ਵਾਊਚਰ #{sid} ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=hf, mime="text/html", key=f"print_exp_{sid}")
            except: pass

    elif st.session_state.entry_mode == "🏦 ਬੈਂਕ ਐਂਟਰੀ (Manual Bank Entry)":
        if not is_mgmt:
            with st.form("man_bank", clear_on_submit=True):
                b_acc = st.selectbox("ਬੈਂਕ", config.BANK_ACCOUNTS); b_dt = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                b_desc = st.text_input("ਵੇਰਵਾ")
                c1, c2 = st.columns(2); b_type = c1.radio("ਕਿਸਮ", ["Credit", "Debit"]); b_amt = c2.number_input("ਰਕਮ (₹)", min_value=1.0)
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and b_desc:
                    d_val, c_val = (b_amt, 0.0) if "Debit" in b_type else (0.0, b_amt)
                    utils.supabase.table("bank_ledger").insert({"txn_date": b_dt.strftime("%Y-%m-%d"), "description": b_desc, "bank_name": b_acc, "debit": d_val, "credit": c_val, "balance": 0.0, "source": "Manual Entry"}).execute()
                    st.success("✅ ਐਂਟਰੀ ਸੇਵ ਹੋ ਗਈ!")
            try:
                r = utils.supabase.table("bank_ledger").select("*").eq("source", "Manual Entry").order("id", desc=True).limit(50).execute().data
                if r: st.dataframe(utils.format_dates_in_df(pd.DataFrame(r)[['id', 'txn_date', 'bank_name', 'description', 'debit', 'credit']], ascending=False), hide_index=True, use_container_width=True)
            except: pass

    elif st.session_state.entry_mode == "📁 ਪਾਰਟੀ/ਵੈਂਡਰ (Party)":
        if not is_mgmt:
            with st.form("party", clear_on_submit=True):
                p_name = st.text_input("ਪਾਰਟੀ"); p_type = st.selectbox("ਕਿਸਮ", ["Sundry Creditor (ਦੇਣਦਾਰ)", "Sundry Debtor (ਪਾਉਣਦਾਰ)"])
                p_ph = st.text_input("ਫ਼ੋਨ"); p_add = st.text_input("ਪਤਾ"); p_amt = st.number_input("ਸ਼ੁਰੂਆਤੀ ਬੈਲੇਂਸ", min_value=0.0)
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and p_name:
                    utils.supabase.table("parties").insert({"name": p_name, "party_type": p_type, "phone": p_ph, "address": p_add, "opening_balance": p_amt, "created_at": str(date.today())}).execute()
                    st.success("✅ ਸੇਵ ਹੋ ਗਈ!")
            try:
                r = utils.supabase.table("parties").select("*").order("id", desc=True).limit(50).execute().data
                if r: 
                    df = utils.format_dates_in_df(pd.DataFrame(r)[['id', 'name', 'party_type', 'opening_balance']], ascending=False)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                    utils.create_print_button(df, "Parties & Vendors", "🖨️ ਪਾਰਟੀਆਂ ਪ੍ਰਿੰਟ ਕਰੋ")
            except: pass

    elif st.session_state.entry_mode == "💳 ਚੈੱਕ ਰਿਕਾਰਡ (Cheque)":
        if not is_mgmt:
            with st.form("chq", clear_on_submit=True):
                cq = st.text_input("ਚੈੱਕ ਨੰਬਰ"); cb = st.selectbox("ਬੈਂਕ", config.BANK_ACCOUNTS); cp = st.text_input("ਕਿਸ ਨੂੰ ਦਿੱਤਾ/ਲਿਆ")
                ca = st.number_input("ਰਕਮ (₹)", min_value=1.0); cd = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                cs = st.selectbox("ਸਟੇਟਸ", ["Pending", "Cleared", "Cancelled"])
                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and cq:
                    utils.supabase.table("cheques").insert({"cheque_no": cq, "bank_name": cb, "party_name": cp, "amount": ca, "cheque_date": str(cd), "status": cs}).execute()
                    st.success("✅ ਸੇਵ ਹੋ ਗਿਆ!")
            try:
                r = utils.supabase.table("cheques").select("*").order("id", desc=True).limit(50).execute().data
                if r:
                    df = utils.format_dates_in_df(pd.DataFrame(r)[['id', 'cheque_date', 'cheque_no', 'party_name', 'amount', 'status']], ascending=False)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                    utils.create_print_button(df, "Cheque Register", "🖨️ ਚੈੱਕ ਰਜਿਸਟਰ ਪ੍ਰਿੰਟ ਕਰੋ")
            except: pass

    elif st.session_state.entry_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)":
        rt = st.radio("ਪ੍ਰਿੰਟ ਕਰੋ:", ["ਦਾਨ ਰਸੀਦ", "ਖਰਚਾ ਵਾਊਚਰ"], horizontal=True)
        c1, c2 = st.columns(2)
        if rt == "ਦਾਨ ਰਸੀਦ":
            with c1:
                sid = st.number_input("ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1)
                if st.button("🔍 ਲੱਭੋ", type="primary"):
                    res = utils.supabase.table("donations").select("*").eq("id", sid).execute().data
                    if res:
                        rec = res[0]
                        hf = utils.generate_html_receipt(sid, rec.get('name',''), rec.get('phone',''), rec.get('amount',0), utils.clean_date_to_display(rec.get('date','')), rec.get('payment_mode','N/A'), rec.get('donation_type','ਪੈਸੇ (Monetary)'), rec.get('item_details',''), rec.get('bank_account','N/A'), rec.get('on_account_of',''), rec.get('collector_name', ''), rec.get('address', 'ਸ੍ਰੀ ਅੰਮ੍ਰਿਤਸਰ ਸਾਹਿਬ'), rec.get('cheque_no', ''), rec.get('cheque_bank', ''))
                        with open(hf, "r", encoding="utf-8") as f: st.download_button("🖨️ ਡਾਊਨਲੋਡ ਕਰੋ", data=f.read(), file_name=hf, mime="text/html", type="primary")
                    else: st.error("❌ ਨਹੀਂ ਮਿਲੀ।")
        else:
            with c1:
                xid = st.number_input("ਵਾਊਚਰ ਨੰਬਰ", min_value=1, step=1)
                if st.button("🔍 ਲੱਭੋ", type="primary"):
                    res = utils.supabase.table("expenses").select("*").eq("id", xid).execute().data
                    if res:
                        rec = res[0]
                        desc_with_payee = str(rec.get('description','')) + f" (Payee: {rec.get('payee_name', '')})"
                        hf = utils.generate_html_expense_voucher(xid, desc_with_payee, rec.get('amount',0), utils.clean_date_to_display(rec.get('date','')), rec.get('category',''), rec.get('bank_account','N/A'))
                        with open(hf, "r", encoding="utf-8") as f: st.download_button("🖨️ ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=hf, mime="text/html", type="primary")
                    else: st.error("❌ ਨਹੀਂ ਮਿਲਿਆ।")
