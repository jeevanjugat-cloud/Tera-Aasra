import streamlit as st
import pandas as pd
from datetime import date
import time
import config
import utils

def show_page(is_mgmt):
    st.header("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)")
    
    tab1, tab2 = st.tabs(["💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Receipts)", "💸 ਖਰਚਾ ਪਾਓ (Payments)"])
    
    with tab1:
        st.subheader("ਨਵਾਂ ਦਾਨ / ਰਸੀਦ (New Receipt)")
        
        # 1. ਭੁਗਤਾਨ ਦਾ ਤਰੀਕਾ (ਡ੍ਰੌਪਡਾਊਨ ਫਾਰਮ ਤੋਂ ਬਾਹਰ ਰੱਖਿਆ ਹੈ, ਤਾਂ ਜੋ ਸਕਰੀਨ ਆਟੋ-ਅਪਡੇਟ ਹੋ ਸਕੇ)
        pay_modes = ["ਨਕਦ (Cash)", "UPI / Online", "NEFT / RTGS", "ਚੈੱਕ (Cheque)"]
        pay_mode = st.selectbox("ਭੁਗਤਾਨ ਦਾ ਤਰੀਕਾ (Payment Mode):", pay_modes)
        
        # 2. ਆਟੋਮੈਟਿਕ ਬੈਂਕ ਸਿਲੈਕਸ਼ਨ ਲੌਜਿਕ (Auto Bank Selection)
        if pay_mode in ["UPI / Online", "NEFT / RTGS", "ਚੈੱਕ (Cheque)"]:
            default_bank = "Kotak Bank Regular"
        else:
            default_bank = "ਨਕਦ (Cash)"
            
        try: 
            b_idx = config.BANK_ACCOUNTS.index(default_bank)
        except ValueError: 
            b_idx = 0
        
        # 3. ਫਾਰਮ ਸ਼ੁਰੂ 
        with st.form("donation_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d_date = col1.date_input("ਰਸੀਦ ਦੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
            
            # ਬੈਂਕ ਖਾਤਾ ਆਪਣੇ ਆਪ ਉੱਪਰ ਵਾਲੇ ਲੌਜਿਕ ਹਿਸਾਬ ਨਾਲ ਚੁਣਿਆ ਜਾਵੇਗਾ
            b_acc = col2.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ?", config.BANK_ACCOUNTS, index=b_idx)
            
            d_name = st.text_input("ਦਾਨੀ ਦਾ ਨਾਮ (Donor Name)*")
            
            c1, c2 = st.columns(2)
            d_phone = c1.text_input("ਫੋਨ ਨੰਬਰ (Phone)")
            d_amount = c2.number_input("ਰਕਮ (Amount ₹)*", min_value=1.0, step=100.0)
            
            # 4. ਡਾਇਨਾਮਿਕ ਚੈੱਕ ਕਾਲਮ (Dynamic Cheque Columns)
            chq_no = ""
            chq_bank = ""
            if pay_mode == "ਚੈੱਕ (Cheque)":
                st.markdown("---")
                st.info("🏦 ਚੈੱਕ ਦਾ ਵੇਰਵਾ ਭਰੋ:")
                c3, c4 = st.columns(2)
                chq_no = c3.text_input("ਚੈੱਕ ਨੰਬਰ (Cheque No.)*")
                chq_bank = c4.text_input("ਚੈੱਕ ਵਾਲਾ ਬੈਂਕ (Bank Name)")
                st.markdown("---")

            d_address = st.text_input("ਪਤਾ (Address)")
            on_acc = st.text_input("ਕਿਸ ਕੰਮ ਲਈ (On Account Of / Purpose)")
            
            add_to_mirror = st.checkbox("✅ ਇਸ ਦਾਨ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=False)
            
            submitted = st.form_submit_button("ਰਸੀਦ ਸੇਵ ਕਰੋ (Save Receipt)", type="primary")
            
            if submitted:
                if not d_name or d_amount <= 0:
                    st.error("ਕਿਰਪਾ ਕਰਕੇ ਨਾਮ ਅਤੇ ਰਕਮ ਜ਼ਰੂਰ ਭਰੋ!")
                elif pay_mode == "ਚੈੱਕ (Cheque)" and not chq_no:
                    st.error("ਕਿਰਪਾ ਕਰਕੇ ਚੈੱਕ ਨੰਬਰ ਜ਼ਰੂਰ ਭਰੋ!")
                else:
                    rec_id = int(time.time() % 100000)
                    
                    utils.supabase.table("donations").insert({
                        "id": rec_id,
                        "date": str(d_date),
                        "name": d_name,
                        "phone": d_phone,
                        "address": d_address,
                        "amount": d_amount,
                        "payment_mode": pay_mode,
                        "cheque_no": chq_no,
                        "cheque_bank": chq_bank,
                        "donation_type": "ਪੈਸੇ (Monetary)",
                        "item_details": "",
                        "bank_account": b_acc,
                        "on_account_of": on_acc,
                        "collector_name": st.session_state.get('username', 'Admin'),
                        "add_to_mirror": add_to_mirror
                    }).execute()
                    
                    if add_to_mirror:
                        utils.supabase.table("bank_ledger").insert({
                            "txn_date": str(d_date),
                            "description": f"ਦਾਨ: {d_name} (Rec#{rec_id}) - {on_acc}",
                            "bank_name": b_acc,
                            "debit": 0.0,
                            "credit": d_amount,
                            "balance": 0.0,
                            "source": "App (Donation)"
                        }).execute()
                        
                    if pay_mode == "ਚੈੱਕ (Cheque)":
                        utils.supabase.table("cheques").insert({
                            "cheque_date": str(d_date),
                            "cheque_no": chq_no,
                            "bank_name": b_acc,
                            "amount": d_amount,
                            "status": "Pending",
                            "party_name": d_name
                        }).execute()
                    
                    st.success(f"✅ ਰਸੀਦ #{rec_id} ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਈ ਹੈ!")
                    time.sleep(1.5)
                    st.rerun()
                    
    with tab2:
        st.subheader("ਨਵਾਂ ਖਰਚਾ (New Expense)")
        with st.form("expense_form", clear_on_submit=True):
            e_date = st.date_input("ਮਿਤੀ (Date)", value=date.today(), format="DD/MM/YYYY")
            e_cat = st.selectbox("ਖਰਚੇ ਦੀ ਕੈਟਾਗਰੀ", [c for c in config.EXPENSE_CATEGORIES if not c.startswith("---")])
            e_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚੋਂ ਪੈਸੇ ਦਿੱਤੇ?", config.BANK_ACCOUNTS)
            
            c1, c2 = st.columns(2)
            e_payee = c1.text_input("ਪ੍ਰਾਪਤ ਕਰਤਾ (Paid To)")
            e_amount = c2.number_input("ਰਕਮ (Amount ₹)*", min_value=1.0, step=100.0)
            
            e_desc = st.text_input("ਵੇਰਵਾ (Description)*")
            
            add_to_mirror_exp = st.checkbox("✅ ਇਸ ਖਰਚੇ ਨੂੰ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਪਾਓ", value=False)
            
            if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ (Save Expense)", type="primary"):
                if not e_desc or e_amount <= 0:
                    st.error("ਕਿਰਪਾ ਕਰਕੇ ਵੇਰਵਾ ਅਤੇ ਰਕਮ ਜ਼ਰੂਰ ਭਰੋ!")
                else:
                    utils.supabase.table("expenses").insert({
                        "date": str(e_date),
                        "category": e_cat,
                        "payee_name": e_payee,
                        "amount": e_amount,
                        "description": e_desc,
                        "bank_account": e_acc,
                        "add_to_mirror": add_to_mirror_exp
                    }).execute()
                    
                    if add_to_mirror_exp:
                        utils.supabase.table("bank_ledger").insert({
                            "txn_date": str(e_date),
                            "description": f"ਖਰਚਾ: {e_desc}",
                            "bank_name": e_acc,
                            "debit": e_amount,
                            "credit": 0.0,
                            "balance": 0.0,
                            "source": "App (Expense)"
                        }).execute()
                        
                    st.success("✅ ਖਰਚਾ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ ਹੈ!")
                    time.sleep(1.5)
                    st.rerun()
