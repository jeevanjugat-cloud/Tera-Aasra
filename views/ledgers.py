import streamlit as st
import pandas as pd
from datetime import date
import io
import time
import config
import utils

# === EXACT FORMULA: LAST UPLOADED EXCEL BALANCE - PENDING CHEQUES ===
def get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_cheques_safe):
    bank_balances = {bank: 0.0 for bank in config.BANK_ACCOUNTS}
    
    if not df_ledg_safe.empty and 'balance' in df_ledg_safe.columns:
        df_ledg_safe['balance'] = pd.to_numeric(df_ledg_safe['balance'], errors='coerce').fillna(0.0)

    for bank in config.BANK_ACCOUNTS:
        if bank == "ਨਕਦ (Cash)":
            b_in = df_don_safe[df_don_safe['bank_account'].apply(lambda x: utils.is_bank_match(x, bank)) & (df_don_safe['donation_type'] == 'ਪੈਸੇ (Monetary)')]['amount'].sum() if not df_don_safe.empty else 0.0
            b_in += df_ledg_safe[df_ledg_safe['bank_name'].apply(lambda x: utils.is_bank_match(x, bank))]['credit'].sum() if not df_ledg_safe.empty else 0.0
            b_out = df_exp_safe[df_exp_safe['bank_account'].apply(lambda x: utils.is_bank_match(x, bank))]['amount'].sum() if not df_exp_safe.empty else 0.0
            b_out += df_ledg_safe[df_ledg_safe['bank_name'].apply(lambda x: utils.is_bank_match(x, bank))]['debit'].sum() if not df_ledg_safe.empty else 0.0
            bank_balances[bank] = b_in - b_out
            continue
            
        latest_excel_bal = 0.0
        if not df_ledg_safe.empty and 'bank_name' in df_ledg_safe.columns:
            mask_excel = df_ledg_safe['bank_name'].apply(lambda x: utils.is_bank_match(x, bank)) & (df_ledg_safe['balance'] != 0.0)
            df_excel = df_ledg_safe[mask_excel].copy()
            if not df_excel.empty:
                if '__dt' not in df_excel.columns:
                    df_excel['__dt'] = df_excel['txn_date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
                df_excel = df_excel.sort_values(by=['__dt', 'id'], ascending=True)
                latest_excel_bal = float(df_excel.iloc[-1]['balance'])
                
        pending_chq = 0.0
        if not df_cheques_safe.empty and 'bank_name' in df_cheques_safe.columns:
            mask_chq = df_cheques_safe['bank_name'].apply(lambda x: utils.is_bank_match(x, bank)) & df_cheques_safe['status'].astype(str).str.contains('Pending', case=False, na=False)
            pending_chq = pd.to_numeric(df_cheques_safe[mask_chq]['amount'], errors='coerce').fillna(0.0).sum()
            
        bank_balances[bank] = latest_excel_bal - pending_chq
        
    return bank_balances

def get_ledger_data(df_don, df_exp, df_ledg, target_bank=None):
    entries = []
    if not df_don.empty:
        df_don['add_to_mirror'] = df_don.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)'].iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank and not (utils.is_bank_match(b_acc, target_bank) and (row['add_to_mirror'] or target_bank == "ਨਕਦ (Cash)")): continue
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']} (Rec#{row['id']})", 'Account': b_acc, 'Credit': float(row.get('amount') or 0.0), 'Debit': 0.0, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': 'App (Donation)'})
    
    if not df_exp.empty:
        df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_exp.iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank and not (utils.is_bank_match(b_acc, target_bank) and (row['add_to_mirror'] or target_bank == "ਨਕਦ (Cash)")): continue
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Account': b_acc, 'Credit': 0.0, 'Debit': float(row.get('amount') or 0.0), 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': 0.0, 'Source': 'App (Expense)'})
    
    if not df_ledg.empty:
        for _, row in df_ledg.iterrows():
            b_acc = row.get('bank_name')
            if pd.isna(b_acc) or str(b_acc).strip() in ["", "None", "nan"]: b_acc = "Kotak Bank Regular"
            if target_bank and not utils.is_bank_match(b_acc, target_bank): continue
            entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Account': b_acc, 'Credit': float(row.get('credit') or 0.0), 'Debit': float(row.get('debit') or 0.0), 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': row.get('source', 'Manual Entry')})
            
    return pd.DataFrame(entries)

def show_page(is_admin):
    st.header("🏦 ਖਾਤੇ, ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    modes = ["⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ (Cash & Bank Balances)", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)", "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)", "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)"]
    if st.session_state.acc_mode not in modes: st.session_state.acc_mode = modes[0]
    st.session_state.acc_mode = st.radio("ਖਾਤਾ ਚੁਣੋ:", modes, index=modes.index(st.session_state.acc_mode), horizontal=True)
    st.markdown("---")

    don_data = utils.supabase.table("donations").select("*").limit(100000).execute().data or []
    exp_data = utils.supabase.table("expenses").select("*").limit(100000).execute().data or []
    try: ledg_data = utils.supabase.table("bank_ledger").select("*").limit(100000).execute().data or []
    except: ledg_data = []
    try: chq_data = utils.supabase.table("cheques").select("*").limit(100000).execute().data or []
    except: chq_data = []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledg_data)
    df_cheques = pd.DataFrame(chq_data)

    if st.session_state.acc_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        assets_data = utils.supabase.table("assets").select("*").limit(100000).execute().data or []
        liab_data = utils.supabase.table("liabilities").select("*").limit(100000).execute().data or []
        df_assets = pd.DataFrame(assets_data) if assets_data else pd.DataFrame(columns=['name', 'value', 'asset_type'])
        df_liab = pd.DataFrame(liab_data) if liab_data else pd.DataFrame(columns=['name', 'value'])
        
        total_income = df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)']['amount'].astype(float).sum() if not df_don.empty else 0.0
        total_income += df_ledg['credit'].astype(float).sum() if not df_ledg.empty and 'credit' in df_ledg.columns else 0.0
        total_expense = df_exp['amount'].astype(float).sum() if not df_exp.empty else 0.0
        total_expense += df_ledg['debit'].astype(float).sum() if not df_ledg.empty and 'debit' in df_ledg.columns else 0.0
        surplus = total_income - total_expense
        
        asset_totals, fixed_assets_val = {}, 0.0
        if not df_assets.empty:
            df_assets['value'] = pd.to_numeric(df_assets['value'], errors='coerce').fillna(0.0)
            df_assets['asset_type'] = df_assets.get('asset_type', 'ਹੋਰ (Other)').fillna('ਹੋਰ (Other)')
            asset_totals = df_assets.groupby('asset_type')['value'].sum().to_dict()
            fixed_assets_val = df_assets['value'].sum()
            
        other_liab_val = pd.to_numeric(df_liab['value'], errors='coerce').fillna(0.0).sum() if not df_liab.empty else 0.0
        
        st.subheader("📊 Income & Expenditure Account")
        inc_exp_html = f"""<table class="report-table"><tr><th>Expenditure (ਖਰਚੇ)</th><th>Amount (₹)</th><th>Income (ਆਮਦਨ)</th><th>Amount (₹)</th></tr>
            <tr><td>Total Expenses & Payments</td><td>{total_expense:,.2f}</td><td>Total Donations & Receipts</td><td>{total_income:,.2f}</td></tr>
            <tr style="font-weight:bold; color: #D92B2B;"><td>Surplus (ਬੱਚਤ)</td><td>{surplus if surplus > 0 else 0:,.2f}</td><td>Deficit (ਘਾਟਾ)</td><td>{abs(surplus) if surplus < 0 else 0:,.2f}</td></tr>
            <tr style="background-color: #F8F1D1; font-weight:bold;"><td>Total</td><td>{max(total_income, total_expense):,.2f}</td><td>Total</td><td>{max(total_income, total_expense):,.2f}</td></tr></table>"""
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        
        df_don_safe = df_don.copy()
        if not df_don_safe.empty: df_don_safe['amount'] = pd.to_numeric(df_don_safe['amount'], errors='coerce').fillna(0)
        df_exp_safe = df_exp.copy()
        if not df_exp_safe.empty: df_exp_safe['amount'] = pd.to_numeric(df_exp_safe['amount'], errors='coerce').fillna(0)
        df_ledg_safe = df_ledg.copy()
        if not df_ledg_safe.empty:
            df_ledg_safe['credit'] = pd.to_numeric(df_ledg_safe.get('credit', 0), errors='coerce').fillna(0)
            df_ledg_safe['debit'] = pd.to_numeric(df_ledg_safe.get('debit', 0), errors='coerce').fillna(0)

        bank_balances = get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_cheques)
        total_assets = fixed_assets_val + sum(bank_balances.values())
        total_liabilities = other_liab_val + surplus
        
        st.markdown("---")
        st.subheader("⚖️ Balance Sheet")
        col_liab, col_assets = st.columns(2)
        with col_liab:
            st.markdown('<div class="bs-box"><div class="bs-header">Liabilities & Funds</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Corpus/Capital Funds:</span><span>₹ {other_liab_val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-row"><span>Add: Surplus (ਬੱਚਤ):</span><span>₹ {surplus:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Liabilities:</span><span>₹ {total_liabilities:,.2f}</span></div></div>', unsafe_allow_html=True)
        with col_assets:
            st.markdown('<div class="bs-box"><div class="bs-header">Assets (ਸੰਪਤੀ)</div>', unsafe_allow_html=True)
            for atype, aval in asset_totals.items(): st.markdown(f'<div class="bs-row"><span>{atype}:</span><span>₹ {aval:,.2f}</span></div>', unsafe_allow_html=True)
            for b, val in bank_balances.items(): st.markdown(f'<div class="bs-row"><span>{b}:</span><span>₹ {val:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bs-total"><span>Total Assets:</span><span>₹ {total_assets:,.2f}</span></div></div>', unsafe_allow_html=True)
            
        assets_breakdown = "".join([f"<p>{k}: {v:,.2f}</p>" for k, v in asset_totals.items()])
        full_html = f"<h3>Income & Expenditure Account</h3>{inc_exp_html}<br><h3>Balance Sheet</h3><div style='width:100%;'><div class='bs-box'><h4>Liabilities</h4><p>Funds & Liab: {other_liab_val:,.2f}</p><p>Surplus: {surplus:,.2f}</p><hr><p><b>Total: {total_liabilities:,.2f}</b></p></div><div class='bs-box'><h4>Assets</h4>{assets_breakdown}<p>Bank/Cash: {sum(bank_balances.values()):,.2f}</p><hr><p><b>Total: {total_assets:,.2f}</b></p></div></div>"
        fin_report = utils.generate_html_report("Financial Statements", full_html)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

        if is_admin:
            st.markdown("---")
            st.subheader("⚙️ ਸੰਪਤੀ ਅਤੇ ਫੰਡ ਜੋੜੋ")
            ac1, ac2 = st.columns(2)
            with ac1:
                with st.form("add_asset"):
                    a_name = st.text_input("ਸੰਪਤੀ ਦਾ ਨਾਮ")
                    a_type = st.selectbox("ਸੰਪਤੀ ਦੀ ਕਿਸਮ", config.ASSET_TYPES)
                    a_qty = st.number_input("ਮਾਤਰਾ", min_value=1.0, step=1.0)
                    a_val = st.number_input("ਕੁੱਲ ਮੁੱਲ (₹)", min_value=0.0)
                    a_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    if st.form_submit_button("ਸੰਪਤੀ ਸੇਵ ਕਰੋ", type="primary"):
                        utils.supabase.table("assets").insert({"name": a_name, "asset_type": a_type, "quantity": a_qty, "value": a_val, "date_added": str(a_date)}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()
            with ac2:
                with st.form("add_liab"):
                    l_name = st.text_input("ਫੰਡ ਦਾ ਨਾਮ")
                    l_val = st.number_input("ਮੁੱਲ (₹)", min_value=0.0)
                    if st.form_submit_button("ਫੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        utils.supabase.table("liabilities").insert({"name": l_name, "value": l_val, "date_added": str(date.today())}).execute()
                        st.success("ਸੇਵ ਹੋ ਗਿਆ!"); time.sleep(1); st.rerun()

    elif st.session_state.acc_mode == "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ (Cash & Bank Balances)":
        st.write("### 💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ")
        st.success("✅ **ਨਵਾਂ ਫਾਰਮੂਲਾ ਲਾਗੂ ਹੈ:** Bank Balance = (ਐਕਸਲ ਦਾ ਆਖਰੀ ਬੈਲੇਂਸ) - (ਪੈਂਡਿੰਗ ਚੈੱਕ)")
        
        col_d1, _ = st.columns([1, 2])
        with col_d1:
            as_of_date = st.date_input("ਕਿਸ ਤਾਰੀਖ ਤੱਕ ਦਾ ਬੈਲੇਂਸ ਦੇਖਣਾ ਹੈ? (As of Date)", value=date.today(), format="DD/MM/YYYY")
            
        df_don_safe = df_don.copy()
        if not df_don_safe.empty: 
            df_don_safe['amount'] = pd.to_numeric(df_don_safe['amount'], errors='coerce').fillna(0)
            df_don_safe['__dt'] = df_don_safe['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_don_safe = df_don_safe[df_don_safe['__dt'] <= as_of_date]
            
        df_exp_safe = df_exp.copy()
        if not df_exp_safe.empty: 
            df_exp_safe['amount'] = pd.to_numeric(df_exp_safe['amount'], errors='coerce').fillna(0)
            df_exp_safe['__dt'] = df_exp_safe['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_exp_safe = df_exp_safe[df_exp_safe['__dt'] <= as_of_date]
            
        df_ledg_safe = df_ledg.copy()
        if not df_ledg_safe.empty:
            df_ledg_safe['credit'] = pd.to_numeric(df_ledg_safe.get('credit', 0), errors='coerce').fillna(0)
            df_ledg_safe['debit'] = pd.to_numeric(df_ledg_safe.get('debit', 0), errors='coerce').fillna(0)
            df_ledg_safe['__dt'] = df_ledg_safe['txn_date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_ledg_safe = df_ledg_safe[df_ledg_safe['__dt'] <= as_of_date]

        df_chq_safe = df_cheques.copy()
        if not df_chq_safe.empty:
            df_chq_safe['__dt'] = df_chq_safe['cheque_date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_chq_safe = df_chq_safe[df_chq_safe['__dt'] <= as_of_date]

        bank_balances = get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe)
        
        df_bals = pd.DataFrame(list(bank_balances.items()), columns=["ਖਾਤਾ (Account Name)", "ਬੈਲੇਂਸ (Balance ₹)"])
        total_bal = df_bals["ਬੈਲੇਂਸ (Balance ₹)"].sum()
        
        st.dataframe(df_bals.style.format({'ਬੈਲੇਂਸ (Balance ₹)': '{:,.2f}'}), hide_index=True, use_container_width=True)
        
        display_dt = utils.clean_date_to_display(as_of_date)
        st.markdown(f"**{display_dt} ਤੱਕ ਕੁੱਲ ਬੈਲੇਂਸ: ₹ {total_bal:,.2f}**")
        
        rep_file = utils.generate_html_report(f"Cash & Bank Balances (As of {display_dt})", df_bals.to_html(index=False, border=1, classes='report-table') + f"<br><h4 style='text-align: right; color: #D92B2B;'>ਕੁੱਲ: Rs. {total_bal:,.2f}</h4>")
        with open(rep_file, "r", encoding="utf-8") as f: st.download_button("🖨️ ਬੈਲੇਂਸ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=f.read(), file_name=rep_file, mime="text/html", type="primary")

    elif st.session_state.acc_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)":
        st.write("### 📖 ਮੁੱਖ ਲੈਜ਼ਰ / ਡੇਅ ਬੁੱਕ")
        filter_opt = st.radio("ਫਿਲਟਰ (Filter):", ["ਸਾਰੀਆਂ ਐਂਟਰੀਆਂ (All)", "ਸਿਰਫ਼ ਦਾਨ (Donations)", "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)", "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)"], horizontal=True)
        show_all = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)

        df_main = get_ledger_data(df_don, df_exp, df_ledg)
        if not df_main.empty:
            df_main['DateObj'] = df_main['Date'].apply(utils.parse_date_to_obj).fillna(date.today())
            df_main = df_main.sort_values(by=['DateObj', 'ID'], ascending=True) 
            
            if show_all: df_period, running_bal = df_main.copy(), 0.0
            else:
                df_before = df_main[df_main['DateObj'] < start_date]
                running_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
                df_period = df_main[(df_main['DateObj'] >= start_date) & (df_main['DateObj'] <= end_date)].copy()

            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(utils.clean_date_to_display)
            
            if filter_opt == "ਸਿਰਫ਼ ਦਾਨ (Donations)": df_period = df_period[df_period['Source'] == 'App (Donation)']
            elif filter_opt == "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)": df_period = df_period[df_period['Source'] == 'App (Expense)']
            elif filter_opt == "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)": df_period = df_period[~df_period['Source'].str.contains('App', na=False)]
            
            df_disp = df_period[['ID', 'Date', 'Description', 'Account', 'Source', 'Credit', 'Debit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']]
            st.dataframe(df_disp.style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}), hide_index=True, use_container_width=True)
            report_file_main = utils.generate_html_report(f"ਮੁੱਖ ਲੈਜ਼ਰ ({filter_opt})", df_disp.to_html(index=False, border=1, classes='report-table'), landscape=True)
            with open(report_file_main, "r", encoding="utf-8") as file: st.download_button("🖨️ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_main, mime="text/html", type="primary")

    elif st.session_state.acc_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        selected_bank = st.selectbox("ਬੈਂਕ ਚੁਣੋ", config.BANK_ACCOUNTS)
        show_all = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)

        df_compiled = get_ledger_data(df_don, df_exp, df_ledg, target_bank=selected_bank)
        if not df_compiled.empty:
            df_compiled['DateObj'] = df_compiled['Date'].apply(utils.parse_date_to_obj).fillna(date.today())
            df_compiled = df_compiled.sort_values(by=['DateObj', 'ID'], ascending=True)
            
            if show_all: df_period, running_bal = df_compiled.copy(), 0.0
            else:
                df_before = df_compiled[df_compiled['DateObj'] < start_date]
                running_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
                df_period = df_compiled[(df_compiled['DateObj'] >= start_date) & (df_compiled['DateObj'] <= end_date)].copy()

            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Credit'] - row['Debit'])
                balances.append(running_bal)
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(utils.clean_date_to_display)
            
            df_disp = df_period[['ID', 'Date', 'Description', 'Source', 'Credit', 'Debit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']]
            st.dataframe(df_disp.style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}), hide_index=True, use_container_width=True)
            
            st.markdown("---")
            report_file_bank = utils.generate_html_report(f"ਬੈਂਕ ਲੈਜ਼ਰ - {selected_bank}", df_disp.to_html(index=False, border=1, classes='report-table'), landscape=True)
            with open(report_file_bank, "r", encoding="utf-8") as file: st.download_button("🖨️ ਬੈਂਕ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_bank, mime="text/html", type="primary")
        else: st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)":
        st.write("### 📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ ਰਜਿਸਟਰ")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.subheader("ਪਾਰਟੀਆਂ (Parties)")
            try: p_data = utils.supabase.table("parties").select("*").limit(1000).execute().data or []
            except: p_data = []
            if p_data:
                df_p = pd.DataFrame(p_data)[['name', 'party_type', 'phone', 'opening_balance']]
                st.dataframe(df_p, hide_index=True, use_container_width=True)
            else: st.info("ਕੋਈ ਪਾਰਟੀ ਨਹੀਂ ਹੈ।")
            
        with p_col2:
            st.subheader("ਚੈੱਕ (Cheques)")
            if not df_cheques.empty:
                df_c_disp = df_cheques[['cheque_date', 'cheque_no', 'bank_name', 'party_name', 'amount', 'status']]
                st.dataframe(utils.format_dates_in_df(df_c_disp, ascending=False), hide_index=True, use_container_width=True)
            else: st.info("ਕੋਈ ਚੈੱਕ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)":
        st.write("### 📊 CA ਆਡਿਟ ਅਤੇ ਐਕਸਲ ਬੈਕਅੱਪ")
        st.info("ਆਪਣੇ CA ਨੂੰ ਆਡਿਟ ਲਈ ਇਹ ਪੂਰਾ ਮਲਟੀ-ਸ਼ੀਟ ਐਕਸਲ ਡਾਟਾਬੇਸ ਭੇਜੋ।")
        if st.button("📥 CA ਐਕਸਲ ਬੈਕਅੱਪ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("donations").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Donations_Receipts', index=False)
                utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("expenses").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Expenses', index=False)
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("bank_ledger").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Bank_Ledger', index=False)
                except: pass
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("parties").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Creditors_Debtors', index=False)
                except: pass
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("cheques").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Cheque_Register', index=False)
                except: pass
                utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("stock").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Stock', index=False)
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("assets").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Fixed_Assets', index=False)
                except: pass
                utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("students").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Students', index=False)
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("widows").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Widows', index=False)
                except: pass
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("ration_distribution").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Ration', index=False)
                except: pass
                try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("stock_usage").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Stock_Usage', index=False)
                except: pass
                utils.format_dates_in_df(pd.DataFrame(utils.supabase.table("receipt_books").select("*").limit(100000).execute().data or []), ascending=True).to_excel(writer, sheet_name='Receipt_Books', index=False)
            st.download_button("📥 ਕਲਿੱਕ ਕਰਕੇ ਡਾਊਨਲੋਡ ਕਰੋ", data=buffer.getvalue(), file_name=f"CA_Audit_Data_{date.today().strftime('%d-%m-%Y')}.xlsx", type="primary")
