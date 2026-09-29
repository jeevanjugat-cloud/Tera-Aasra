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
                    
                    # WHATSAPP INTEGRATION
                    wa_msg = f"ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹਿ ਜੀ।\nਸਤਿਕਾਰਯੋਗ {donor_name} ਜੀ, ਤੁਹਾਡਾ ਦਾਨ (Rs. {amount}) ਪ੍ਰਾਪਤ ਹੋਇਆ ਹੈ। ਰਸੀਦ ਨੰਬਰ: {rec_no_input}। ਤੇਰਾ ਆਸਰਾ ਵੱਲੋਂ ਧੰਨਵਾਦ।"
                    wa_url = utils.wa_link(donor_phone, wa_msg)
                    if wa_url:
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #25D366; color: white; border-radius: 8px; font-weight: bold; text-decoration: none;">💬 WhatsApp 'ਤੇ ਰਸੀਦ ਭੇਜੋ</a>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.write("#### 🕒 ਪਿਛਲੀਆਂ ਐਂਟਰੀਆਂ")
            if don_data:
                df_rec = pd.DataFrame([d for d in don_data if d.get('donation_type') == "ਪੈਸੇ (Monetary)"])
                if not df_rec.empty:
                    disp_cols = [c for c in ['id', 'date', 'name', 'phone', 'amount', 'bank_account', 'collector_name'] if c in df_rec.columns]
                    df_rec = utils.format_dates_in_df(df_rec[disp_cols], ascending=False)
                    st.dataframe(df_rec, hide_index=True, use_container_width=True)
                    utils.create_print_button(df_rec, "Recent Donations", "🖨️ ਦਾਨ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ")

    elif st.session_state.entry_mode == "📉 ਖਰਚਾ (Payment Debit)":
        if not is_mgmt:
            with st.form("expense_form", clear_on_submit=True):
                st.write("### 📉 ਖਰਚਾ ਜਾਂ ਪੇਮੈਂਟ ਦਰਜ ਕਰੋ")
                payee_name = st.text_input("ਭੁਗਤਾਨ ਕਿਸ ਨੂੰ ਕੀਤਾ / ਪ੍ਰਾਪਤ ਕਰਤਾ (Payee / Paid To Name)")
                desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Description)")
                
                # CUSTOM CATEGORY LOGIC
                cat_options = [c for c in config.EXPENSE_CATEGORIES if not c.startswith("---")] + ["➕ ਹੋਰ ਨਵਾਂ ਖਰਚਾ ਹੈੱਡ (Add New Expense Head)"]
                cat = st.selectbox("ਕੈਟਾਗਰੀ", cat_options)
                new_cat = st.text_input("ਨਵੇਂ ਖਰਚੇ ਦਾ ਹੈੱਡ ਦਰਜ ਕਰੋ (Enter New Expense Head Name)") if cat == "➕ ਹੋਰ ਨਵਾਂ ਖਰਚਾ ਹੈੱਡ (Add New Expense Head)" else ""
                
                exp_amount = st.number_input("ਰਕਮ (₹)", min_value=1.0)
                bank_acc_exp = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਕੱਟੇ?", config.BANK_ACCOUNTS)
                exp_date = st.date_input("ਖਰਚੇ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=True)
                
                submitted_exp = st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ", type="primary")
                
            if submitted_exp and desc:
                final_cat = new_cat.strip() if new_cat else cat
                f_dt = exp_date.strftime("%Y-%m-%d")
                res_ins = utils.supabase.table("expenses").insert({"description": desc, "amount": exp_amount, "date": f_dt, "category": final_cat, "bank_account": bank_acc_exp, "add_to_mirror": add_to_mirror_exp, "payee_name": payee_name}).execute()
                inserted_id = res_ins.data[0]['id'] if res_ins.data else "N/A"
                st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ!")
                
                if inserted_id != "N/A":
                    # Generate Voucher (Temporary override to include payee)
                    html_file_exp = utils.generate_html_expense_voucher(inserted_id, desc + f" (Payee: {payee_name})", exp_amount, utils.clean_date_to_display(f_dt), final_cat, bank_acc_exp)
                    with open(html_file_exp, "r", encoding="utf-8") as file: st.download_button("🖨️ ਵਾਊਚਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=html_file_exp, mime="text/html", type="primary")

            st.markdown("---")
            try:
                recents = utils.supabase.table("expenses").select("*").order("id", desc=True).limit(50).execute().data
                if recents: 
                    df_exp_disp = pd.DataFrame(recents)[['id', 'date', 'payee_name', 'description', 'amount', 'category', 'bank_account']]
                    df_exp_disp = utils.format_dates_in_df(df_exp_disp, ascending=False)
                    st.dataframe(df_exp_disp, hide_index=True, use_container_width=True)
                    utils.create_print_button(df_exp_disp, "Expense List", "🖨️ ਖਰਚਾ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", landscape=True)
            except: pass
