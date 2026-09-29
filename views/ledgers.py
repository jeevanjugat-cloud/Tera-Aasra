import streamlit as st
import pandas as pd
from datetime import date
import io
import time
import config
import utils

def get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_cheques_safe):
    # Discover all unique dynamic banks and cash accounts
    all_banks = set(config.BANK_ACCOUNTS)
    for df, col in [(df_don_safe, 'bank_account'), (df_exp_safe, 'bank_account'), (df_ledg_safe, 'bank_name'), (df_cheques_safe, 'bank_name')]:
        if not df.empty and col in df.columns:
            all_banks.update(df[col].dropna().unique())
    
    all_banks = sorted(list(all_banks))
    bank_balances = {bank: 0.0 for bank in all_banks}
    
    if not df_ledg_safe.empty and 'balance' in df_ledg_safe.columns:
        df_ledg_safe['balance'] = pd.to_numeric(df_ledg_safe['balance'], errors='coerce').fillna(0.0)

    for bank in all_banks:
        is_cash_type = "ਨਕਦ" in bank or "cash" in bank.lower()
        if is_cash_type:
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
                if '__dt' not in df_excel.columns: df_excel['__dt'] = df_excel['txn_date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
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
            if target_bank and not (utils.is_bank_match(b_acc, target_bank) and (row['add_to_mirror'] or "ਨਕਦ" in target_bank)): continue
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']} (Rec#{row['id']})", 'Account': b_acc, 'Credit': float(row.get('amount') or 0.0), 'Debit': 0.0, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': 'App (Donation)'})
    
    if not df_exp.empty:
        df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_exp.iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank and not (utils.is_bank_match(b_acc, target_bank) and (row['add_to_mirror'] or "ਨਕਦ" in target_bank)): continue
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
    modes = ["⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ", "📝 ਦਾਨੀ ਸਟੇਟਮੈਂਟ (Donor Statement)", "📉 ਖਰਚਾ ਹੈੱਡ ਸਟੇਟਮੈਂਟ", "📊 ਮੁੱਖ ਖਰਚੇ ਵੇਰਵਾ (Major Heads)", "🏦 ਬੈਂਕ ਲੈਜ਼ਰ", "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ", "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit)"]
    if st.session_state.acc_mode not in modes: st.session_state.acc_mode = modes[0]
    st.session_state.acc_mode = st.selectbox("ਖਾਤਾ/ਰਿਪੋਰਟ ਚੁਣੋ:", modes, index=modes.index(st.session_state.acc_mode))
    st.markdown("---")

    don_data = utils.supabase.table("donations").select("*").limit(100000).execute().data or []
    exp_data = utils.supabase.table("expenses").select("*").limit(100000).execute().data or []
    ledg_data = utils.supabase.table("bank_ledger").select("*").limit(100000).execute().data or []
    chq_data = utils.supabase.table("cheques").select("*").limit(100000).execute().data or []
    df_don, df_exp, df_ledg, df_cheques = pd.DataFrame(don_data), pd.DataFrame(exp_data), pd.DataFrame(ledg_data), pd.DataFrame(chq_data)

    if st.session_state.acc_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        st.info("ਪਲੀਜ਼ P&L ਆਪਸ਼ਨ ਵਰਤੋ।")

    elif st.session_state.acc_mode == "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ":
        st.write("### 💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ")
        st.success("✅ **ਫਾਰਮੂਲਾ:** Bank Balance = (ਐਕਸਲ ਦਾ ਆਖਰੀ ਬੈਲੇਂਸ) - (ਪੈਂਡਿੰਗ ਚੈੱਕ)")
        col_d1, _ = st.columns([1, 2])
        with col_d1: as_of_date = st.date_input("ਕਿਸ ਤਾਰੀਖ ਤੱਕ ਦਾ ਬੈਲੇਂਸ ਦੇਖਣਾ ਹੈ?", value=date.today(), format="DD/MM/YYYY")
        
        df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe = df_don.copy(), df_exp.copy(), df_ledg.copy(), df_cheques.copy()
        for df, col in [(df_don_safe, 'date'), (df_exp_safe, 'date'), (df_ledg_safe, 'txn_date'), (df_chq_safe, 'cheque_date')]:
            if not df.empty:
                df['__dt'] = df[col].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
                df.drop(df[df['__dt'] > as_of_date].index, inplace=True)
                
        bank_balances = get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe)
        
        # Only show non-zero balances to keep it clean
        bals_list = [(b, val) for b, val in bank_balances.items() if val != 0.0 or b in config.BANK_ACCOUNTS]
        
        df_bals = pd.DataFrame(bals_list, columns=["ਖਾਤਾ", "ਬੈਲੇਂਸ ₹"])
        st.dataframe(df_bals.style.format({'ਬੈਲੇਂਸ ₹': '{:,.2f}'}), hide_index=True, use_container_width=True)
        utils.create_print_button(df_bals, f"Bank Balances as of {utils.clean_date_to_display(as_of_date)}", "🖨️ ਬੈਲੇਂਸ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ")

    elif st.session_state.acc_mode == "📝 ਦਾਨੀ ਸਟੇਟਮੈਂਟ (Donor Statement)":
        st.write("### 📝 ਦਾਨੀ ਸਟੇਟਮੈਂਟ (Donor Statement)")
        if not df_don.empty:
            uq_donors = sorted(list({str(d).strip() for d in df_don['name'].dropna() if str(d).strip() != ""}))
            sel_donor = st.selectbox("ਦਾਨੀ ਦਾ ਨਾਮ ਖੋਜੋ/ਚੁਣੋ:", ["All Donors"] + uq_donors)
            c1, c2 = st.columns(2)
            d1 = c1.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), format="DD/MM/YYYY")
            d2 = c2.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
            
            df_d = df_don.copy()
            df_d['__dt'] = df_d['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_d = df_d[(df_d['__dt'] >= d1) & (df_d['__dt'] <= d2)]
            if sel_donor != "All Donors": df_d = df_d[df_d['name'].astype(str).str.contains(sel_donor, case=False, na=False)]
            
            if not df_d.empty:
                df_disp = df_d[['id', 'date', 'name', 'payment_mode', 'on_account_of', 'amount']].copy()
                df_disp = utils.format_dates_in_df(df_disp, ascending=True)
                st.dataframe(df_disp, hide_index=True, use_container_width=True)
                total_don = pd.to_numeric(df_disp['amount'], errors='coerce').sum()
                st.markdown(f"**ਕੁੱਲ ਦਾਨ (Total Donated): ₹ {total_don:,.2f}**")
                utils.create_print_button(df_disp, f"Statement for {sel_donor} ({utils.clean_date_to_display(d1)} to {utils.clean_date_to_display(d2)})", "🖨️ ਪ੍ਰਿੰਟ ਸਟੇਟਮੈਂਟ (Print Statement)", landscape=True)
            else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਮਿਲਿਆ।")

    elif st.session_state.acc_mode == "📉 ਖਰਚਾ ਹੈੱਡ ਸਟੇਟਮੈਂਟ":
        st.write("### 📉 ਖਰਚਾ ਹੈੱਡ ਸਟੇਟਮੈਂਟ (Expense Statement)")
        if not df_exp.empty:
            uq_cats = sorted(list({str(c).strip() for c in df_exp['category'].dropna() if str(c).strip() != ""}))
            sel_cat = st.selectbox("ਖਰਚੇ ਦੀ ਕੈਟਾਗਰੀ ਚੁਣੋ:", ["All Expenses"] + uq_cats)
            c1, c2 = st.columns(2)
            d1 = c1.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), format="DD/MM/YYYY")
            d2 = c2.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
            
            df_e = df_exp.copy()
            df_e['__dt'] = df_e['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_e = df_e[(df_e['__dt'] >= d1) & (df_e['__dt'] <= d2)]
            if sel_cat != "All Expenses": df_e = df_e[df_e['category'].astype(str) == sel_cat]
            
            if not df_e.empty:
                df_disp = df_e[['id', 'date', 'payee_name', 'description', 'category', 'bank_account', 'amount']].copy()
                df_disp = utils.format_dates_in_df(df_disp, ascending=True)
                st.dataframe(df_disp, hide_index=True, use_container_width=True)
                total_exp = pd.to_numeric(df_disp['amount'], errors='coerce').sum()
                st.markdown(f"**ਇਸ ਮੱਦ ਦਾ ਕੁੱਲ ਖਰਚਾ: ₹ {total_exp:,.2f}**")
                utils.create_print_button(df_disp, f"Expense Statement: {sel_cat}", "🖨️ ਪ੍ਰਿੰਟ ਸਟੇਟਮੈਂਟ", landscape=True)
            else: st.info("ਕੋਈ ਖਰਚਾ ਨਹੀਂ ਮਿਲਿਆ।")

    elif st.session_state.acc_mode == "📊 ਮੁੱਖ ਖਰਚੇ ਵੇਰਵਾ (Major Heads)":
        st.write("### 📊 ਮੁੱਖ ਖਰਚੇ ਵੇਰਵਾ (Expenses under Major Heads)")
        if not df_exp.empty:
            c1, c2 = st.columns(2)
            d1 = c1.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), format="DD/MM/YYYY", key="mh_d1")
            d2 = c2.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY", key="mh_d2")
            
            df_e = df_exp.copy()
            df_e['__dt'] = df_e['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_e = df_e[(df_e['__dt'] >= d1) & (df_e['__dt'] <= d2)]
            df_e['amount'] = pd.to_numeric(df_e['amount'], errors='coerce').fillna(0)
            
            def map_major_head(cat):
                cat = str(cat).strip()
                if cat in ["ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)", "ਲੰਗਰ (Langar)"]: return "ਕੀਰਤਨ ਸਮਾਗਮ (Samagams)"
                if cat in ["ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)"]: return "ਤੇਰਾ ਆਸਰਾ (Tera Aasra / Welfare)"
                return "ਹੋਰ ਖਰਚੇ (Others)"
                
            if not df_e.empty:
                df_e['Major Head'] = df_e['category'].apply(map_major_head)
                grouped = df_e.groupby(['Major Head', 'category'])['amount'].sum().reset_index()
                grand_total = grouped['amount'].sum()
                grouped['% of Total'] = ((grouped['amount'] / grand_total) * 100).round(2).astype(str) + "%"
                
                st.dataframe(grouped, hide_index=True, use_container_width=True)
                st.markdown(f"**Grand Total: ₹ {grand_total:,.2f}**")
                utils.create_print_button(grouped, f"Major Heads Summary ({utils.clean_date_to_display(d1)} to {utils.clean_date_to_display(d2)})", "🖨️ ਪ੍ਰਿੰਟ ਖਰਚਾ ਸਮਰੀ")
            else: st.info("ਇਸ ਸਮੇਂ ਦੌਰਾਨ ਕੋਈ ਖਰਚਾ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        all_banks = set(config.BANK_ACCOUNTS)
        for df, col in [(df_don, 'bank_account'), (df_exp, 'bank_account'), (df_ledg, 'bank_name')]:
            if not df.empty and col in df.columns: all_banks.update(df[col].dropna().unique())
            
        selected_bank = st.selectbox("ਬੈਂਕ/ਖਾਤਾ ਚੁਣੋ", sorted(list(all_banks)))
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
            utils.create_print_button(df_disp, f"Bank Ledger - {selected_bank}", "🖨️ ਬੈਂਕ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", landscape=True)
        else: st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ":
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Parties")
            try: r = utils.supabase.table("parties").select("*").limit(1000).execute().data
            except: r = []
            if r: 
                dp = pd.DataFrame(r)[['name', 'party_type', 'opening_balance']]
                st.dataframe(dp, hide_index=True, use_container_width=True); utils.create_print_button(dp, "Parties", "🖨️ Print")
        with c2:
            st.subheader("Cheques")
            if not df_cheques.empty:
                dc = utils.format_dates_in_df(df_cheques[['cheque_date', 'cheque_no', 'bank_name', 'amount', 'status']], ascending=False)
                st.dataframe(dc, hide_index=True, use_container_width=True); utils.create_print_button(dc, "Cheques", "🖨️ Print")

    elif st.session_state.acc_mode == "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit)":
        if st.button("📥 CA ਐਕਸਲ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            b = io.BytesIO()
            with pd.ExcelWriter(b, engine='openpyxl') as w:
                for tbl in ["donations", "expenses", "bank_ledger", "parties", "cheques", "stock", "assets", "students", "widows", "ration_distribution", "stock_usage", "receipt_books"]:
                    try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table(tbl).select("*").limit(100000).execute().data or []), ascending=True).to_excel(w, sheet_name=tbl[:31], index=False)
                    except: pass
            st.download_button("📥 ਡਾਊਨਲੋਡ", data=b.getvalue(), file_name=f"CA_Audit_{date.today()}.xlsx", type="primary")
