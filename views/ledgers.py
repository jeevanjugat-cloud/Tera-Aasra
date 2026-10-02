import streamlit as st
import pandas as pd
from datetime import date
import io
import time
import itertools
import config
import utils

def exact_bank_match(db_bank, target_bank):
    db_b = str(db_bank).strip().lower()
    tgt_b = str(target_bank).strip().lower()
    if "cash" in tgt_b or "ਨਕਦ" in tgt_b:
        return "cash" in db_b or "ਨਕਦ" in db_b
    return db_b == tgt_b

def get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_cheques_safe, detailed=False):
    all_banks_dynamic = set(config.BANK_ACCOUNTS)
    if not df_don_safe.empty and 'bank_account' in df_don_safe.columns:
        all_banks_dynamic.update(df_don_safe['bank_account'].dropna().unique())
    if not df_exp_safe.empty and 'bank_account' in df_exp_safe.columns:
        all_banks_dynamic.update(df_exp_safe['bank_account'].dropna().unique())
    if not df_ledg_safe.empty and 'bank_name' in df_ledg_safe.columns:
        all_banks_dynamic.update(df_ledg_safe['bank_name'].dropna().unique())
        
    valid_banks = sorted(list({str(b).strip() for b in all_banks_dynamic if str(b).strip() not in ["", "None", "nan", "N/A"]}))
    
    bank_balances = {} if detailed else {bank: 0.0 for bank in valid_banks}
    
    if not df_don_safe.empty: df_don_safe['add_to_mirror'] = df_don_safe.get('add_to_mirror', True).fillna(True).astype(bool)
    if not df_exp_safe.empty: df_exp_safe['add_to_mirror'] = df_exp_safe.get('add_to_mirror', True).fillna(True).astype(bool)

    for bank in valid_banks:
        b_in = 0.0
        b_out = 0.0
        
        if not df_don_safe.empty:
            mask_don = df_don_safe['bank_account'].apply(lambda x: exact_bank_match(x, bank)) & (df_don_safe['donation_type'] == 'ਪੈਸੇ (Monetary)')
            is_cash = "ਨਕਦ" in bank or "cash" in bank.lower()
            if not is_cash: mask_don = mask_don & df_don_safe['add_to_mirror']
            b_in += pd.to_numeric(df_don_safe[mask_don]['amount'], errors='coerce').fillna(0.0).sum()
            
        if not df_exp_safe.empty:
            mask_exp = df_exp_safe['bank_account'].apply(lambda x: exact_bank_match(x, bank))
            is_cash = "ਨਕਦ" in bank or "cash" in bank.lower()
            if not is_cash: mask_exp = mask_exp & df_exp_safe['add_to_mirror']
            b_out += pd.to_numeric(df_exp_safe[mask_exp]['amount'], errors='coerce').fillna(0.0).sum()
            
        if not df_ledg_safe.empty:
            mask_ledg = df_ledg_safe['bank_name'].apply(lambda x: exact_bank_match(x, bank))
            b_in += pd.to_numeric(df_ledg_safe[mask_ledg]['credit'], errors='coerce').fillna(0.0).sum()
            b_out += pd.to_numeric(df_ledg_safe[mask_ledg]['debit'], errors='coerce').fillna(0.0).sum()
            
        current_bal = b_in - b_out
        
        pending_chq = 0.0
        if not df_cheques_safe.empty and 'bank_name' in df_cheques_safe.columns:
            mask_chq = df_cheques_safe['bank_name'].apply(lambda x: exact_bank_match(x, bank)) & df_cheques_safe['status'].astype(str).str.contains('Pending', case=False, na=False)
            pending_chq = pd.to_numeric(df_cheques_safe[mask_chq]['amount'], errors='coerce').fillna(0.0).sum()
            
        if detailed:
            bank_balances[bank] = {
                "ਖਾਤਾ (Bank/Cash)": bank,
                "ਅਸਲ ਬੈਲੇਂਸ (Actual)": current_bal,
                "ਕਲੀਅਰਿੰਗ (Pending Chq)": pending_chq,
                "ਨੈੱਟ ਬੈਲੇਂਸ (Net)": current_bal - pending_chq
            }
        else:
            bank_balances[bank] = current_bal - pending_chq
        
    return bank_balances

def get_ledger_data(df_don, df_exp, df_ledg, target_bank=None, view_mode="Mirror"):
    entries = []
    is_mirror = "Mirror" in view_mode or "ਸੰਸਥਾ" in view_mode
    
    if not df_don.empty:
        df_don['add_to_mirror'] = df_don.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_don[df_don['donation_type'] == 'ਪੈਸੇ (Monetary)'].iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank:
                is_match = exact_bank_match(b_acc, target_bank)
                is_cash = "ਨਕਦ" in target_bank or "cash" in target_bank.lower()
                if not is_match: continue
                if not is_cash and not row['add_to_mirror']: continue
            
            if is_mirror: d_val, c_val = float(row.get('amount') or 0.0), 0.0
            else: d_val, c_val = 0.0, float(row.get('amount') or 0.0)
            
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਦਾਨ: {row['name']} (Rec#{row['id']})", 'Account': b_acc, 'Debit': d_val, 'Credit': c_val, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': 'App (Donation)'})
    
    if not df_exp.empty:
        df_exp['add_to_mirror'] = df_exp.get('add_to_mirror', True).fillna(True).astype(bool)
        for _, row in df_exp.iterrows():
            b_acc = row.get('bank_account', 'N/A')
            if target_bank:
                is_match = exact_bank_match(b_acc, target_bank)
                is_cash = "ਨਕਦ" in target_bank or "cash" in target_bank.lower()
                if not is_match: continue
                if not is_cash and not row['add_to_mirror']: continue
            
            if is_mirror: d_val, c_val = 0.0, float(row.get('amount') or 0.0)
            else: d_val, c_val = float(row.get('amount') or 0.0), 0.0
            
            entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Account': b_acc, 'Debit': d_val, 'Credit': c_val, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': 0.0, 'Source': 'App (Expense)'})
    
    if not df_ledg.empty:
        for _, row in df_ledg.iterrows():
            b_acc = row.get('bank_name')
            if pd.isna(b_acc) or str(b_acc).strip() in ["", "None", "nan"]: b_acc = "Kotak Bank Regular"
            if target_bank and not exact_bank_match(b_acc, target_bank): continue
            
            if is_mirror: 
                d_val, c_val = float(row.get('credit') or 0.0), float(row.get('debit') or 0.0) 
            else: 
                d_val, c_val = float(row.get('debit') or 0.0), float(row.get('credit') or 0.0)
                
            entries.append({'ID': row.get('id', 0), 'Date': row.get('txn_date', ''), 'Description': row.get('description', ''), 'Account': b_acc, 'Debit': d_val, 'Credit': c_val, 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': float(row.get('balance') or 0.0), 'Source': row.get('source', 'Manual Entry')})
            
    return pd.DataFrame(entries)

def show_page(is_admin):
    st.header("🏦 ਖਾਤੇ, ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    
    modes = [
        "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", 
        "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ", 
        "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)", 
        "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)", 
        "📝 ਦਾਨੀ ਸਟੇਟਮੈਂਟ (Donor Statement)", 
        "📉 ਖਰਚਾ ਸਟੇਟਮੈਂਟ (Expense Statement)", 
        "📊 ਮੁੱਖ ਖਰਚੇ ਵੇਰਵਾ (Major Heads)", 
        "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ", 
        "📊 CA ਆਡਿਟ ਐਕਸਲ"
    ]
    
    if 'acc_mode' not in st.session_state or st.session_state.acc_mode not in modes: 
        st.session_state.acc_mode = "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)"
        
    st.session_state.acc_mode = st.radio("ਖਾਤਾ/ਰਿਪੋਰਟ ਚੁਣੋ:", modes, index=modes.index(st.session_state.acc_mode), horizontal=True)
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
        st.write("### ⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ ਅਤੇ P&L (Professional Statement)")
        col_d1, _ = st.columns([1, 2])
        with col_d1: 
            as_of_date = st.date_input("ਕਿਸ ਤਾਰੀਖ ਤੱਕ ਦੀ ਰਿਪੋਰਟ ਦੇਖਣੀ ਹੈ?", value=date.today(), format="DD/MM/YYYY")
            
        assets_data = utils.supabase.table("assets").select("*").limit(100000).execute().data or []
        liab_data = utils.supabase.table("liabilities").select("*").limit(100000).execute().data or []
        df_assets = pd.DataFrame(assets_data) if assets_data else pd.DataFrame(columns=['name', 'value', 'asset_type', 'date_added'])
        df_liab = pd.DataFrame(liab_data) if liab_data else pd.DataFrame(columns=['name', 'value', 'date_added'])
        
        # Data filtering
        df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe = df_don.copy(), df_exp.copy(), df_ledg.copy(), df_cheques.copy()
        
        for df, col in [(df_don_safe, 'date'), (df_exp_safe, 'date'), (df_ledg_safe, 'txn_date'), (df_chq_safe, 'cheque_date'), (df_assets, 'date_added'), (df_liab, 'date_added')]:
            if not df.empty and col in df.columns:
                df['__dt'] = df[col].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
                df.drop(df[df['__dt'] > as_of_date].index, inplace=True)

        df_don_safe['amount'] = pd.to_numeric(df_don_safe.get('amount', 0), errors='coerce').fillna(0)
        df_exp_safe['amount'] = pd.to_numeric(df_exp_safe.get('amount', 0), errors='coerce').fillna(0)
        if not df_ledg_safe.empty:
            df_ledg_safe['credit'] = pd.to_numeric(df_ledg_safe.get('credit', 0), errors='coerce').fillna(0)
            df_ledg_safe['debit'] = pd.to_numeric(df_ledg_safe.get('debit', 0), errors='coerce').fillna(0)

        # ---------------- 1. INCOME & EXPENDITURE HEADS (SUMMARIZED) ----------------
        expense_heads = {}
        if not df_exp_safe.empty:
            def map_major_head_pl(cat):
                cat = str(cat).strip()
                if cat in ["Kirtan Smagam Expenses", "ਲੰਗਰ (Langar)", "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)"]: 
                    return "ਧਾਰਮਿਕ ਸਮਾਗਮ (Religious Programs)"
                if cat in ["Other Asset Purchase", "Salary", "Miscleneous Expenses Tera Aasra", "Free Distribution Clothing", "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)"]: 
                    return "ਤੇਰਾ ਆਸਰਾ (Tera Aasra / Welfare)"
                return "ਹੋਰ ਖਰਚੇ (Others)"
            
            df_exp_safe['Major Head'] = df_exp_safe['category'].apply(map_major_head_pl)
            exp_grouped = df_exp_safe.groupby('Major Head')['amount'].sum().to_dict()
            for k, v in exp_grouped.items():
                if v > 0: expense_heads[k] = v
                
        ledger_debits = df_ledg_safe['debit'].sum() if not df_ledg_safe.empty and 'debit' in df_ledg_safe.columns else 0.0
        if ledger_debits > 0: expense_heads['Bank Charges / Manual Debits'] = ledger_debits
            
        total_expense = sum(expense_heads.values())
        
        income_heads = {}
        total_income = 0.0
        if not df_don_safe.empty:
            total_income += df_don_safe[df_don_safe['donation_type'] == 'ਪੈਸੇ (Monetary)']['amount'].sum()
        if not df_ledg_safe.empty and 'credit' in df_ledg_safe.columns:
            total_income += df_ledg_safe['credit'].sum()
            
        if total_income > 0:
            income_heads['Donations (ਕੁੱਲ ਦਾਨ)'] = total_income
            
        surplus = total_income - total_expense

        # P&L HTML Generation
        inc_items = sorted(list(income_heads.items()), key=lambda x: x[1], reverse=True)
        exp_items = sorted(list(expense_heads.items()), key=lambda x: x[1], reverse=True)
        
        inc_exp_rows = ""
        for exp, inc in itertools.zip_longest(exp_items, inc_items, fillvalue=("", 0)):
            exp_name, exp_val = exp
            inc_name, inc_val = inc
            
            exp_val_str = f"₹ {exp_val:,.2f}" if exp_name != "" else ""
            inc_val_str = f"₹ {inc_val:,.2f}" if inc_name != "" else ""
            
            inc_exp_rows += f"<tr><td style='text-align:left; border-right:none;'>{exp_name}</td><td style='text-align:right; border-left:none;'>{exp_val_str}</td><td style='text-align:left; border-right:none;'>{inc_name}</td><td style='text-align:right; border-left:none;'>{inc_val_str}</td></tr>"
            
        if surplus > 0:
            inc_exp_rows += f"<tr style='color: #0F4C81; font-weight:bold;'><td style='text-align:left; border-right:none;'>To Surplus (Excess of Income over Exp.)</td><td style='text-align:right; border-left:none;'>₹ {surplus:,.2f}</td><td style='text-align:left; border-right:none;'></td><td style='text-align:right; border-left:none;'></td></tr>"
        elif surplus < 0:
            inc_exp_rows += f"<tr style='color: #D92B2B; font-weight:bold;'><td style='text-align:left; border-right:none;'></td><td style='text-align:right; border-left:none;'></td><td style='text-align:left; border-right:none;'>By Deficit (Excess of Exp. over Income)</td><td style='text-align:right; border-left:none;'>₹ {abs(surplus):,.2f}</td></tr>"

        inc_exp_html = f'''<table class="report-table" style="width:100%; border: 1px solid #333; margin-bottom: 20px;">
            <tr style="background-color: #F8F1D1;"><th style="text-align:left; width:35%;">Expenditure (ਖਰਚੇ)</th><th style="text-align:right; width:15%;">Amount</th><th style="text-align:left; width:35%;">Donations (ਦਾਨ)</th><th style="text-align:right; width:15%;">Amount</th></tr>
            {inc_exp_rows}
            <tr style="background-color: #eee; font-weight:bold;"><td style="text-align:left; border-right:none;">Total</td><td style="text-align:right; border-left:none;">₹ {max(total_income, total_expense):,.2f}</td><td style="text-align:left; border-right:none;">Total</td><td style="text-align:right; border-left:none;">₹ {max(total_income, total_expense):,.2f}</td></tr>
            </table>'''
            
        st.subheader(f"📊 Income & Expenditure Account (As of {utils.clean_date_to_display(as_of_date)})")
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        
        # ---------------- 2. BALANCE SHEET ----------------
        asset_totals, fixed_assets_val = {}, 0.0
        if not df_assets.empty:
            df_assets['value'] = pd.to_numeric(df_assets['value'], errors='coerce').fillna(0.0)
            df_assets['asset_type'] = df_assets.get('asset_type', 'ਹੋਰ (Other)').fillna('ਹੋਰ (Other)')
            asset_totals = df_assets.groupby('asset_type')['value'].sum().to_dict()
            fixed_assets_val = df_assets['value'].sum()
            
        other_liab_val = pd.to_numeric(df_liab['value'], errors='coerce').fillna(0.0).sum() if not df_liab.empty else 0.0
        bank_balances = get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe, detailed=False)
        total_assets = fixed_assets_val + sum(bank_balances.values())
        
        auto_corpus = total_assets - (other_liab_val + surplus)
        total_liabilities = other_liab_val + surplus + auto_corpus
        
        liab_list = [
            ("<b>Capital / Corpus Fund</b>", ""),
            ("Opening Balance / Manual Funds", f"₹ {other_liab_val:,.2f}"),
            ("Auto Corpus Fund (Balancing Fig.)", f"₹ {auto_corpus:,.2f}"),
            (f"<b>{'Add: Surplus' if surplus >= 0 else 'Less: Deficit'} (During the Year)</b>", f"<b>₹ {abs(surplus):,.2f}</b>"),
            ("<b>Current Liabilities</b>", ""),
            ("Sundry Creditors / Pending Dues", "₹ 0.00")
        ]
        
        asset_list = [("<b>Fixed Assets</b>", "")]
        for k, v in asset_totals.items():
            if v > 0: asset_list.append((f" - {k}", f"₹ {v:,.2f}"))
            
        asset_list.append(("<b>Current Assets</b>", ""))
        for k, v in bank_balances.items():
            if v != 0: asset_list.append((f"Bank / Cash: {k}", f"₹ {v:,.2f}"))
            
        bs_rows = ""
        for liab, asset in itertools.zip_longest(liab_list, asset_list, fillvalue=("", "")):
            l_name, l_val = liab
            a_name, a_val = asset
            bs_rows += f"<tr><td style='text-align:left; border-right:none;'>{l_name}</td><td style='text-align:right; border-left:none;'>{l_val}</td><td style='text-align:left; border-right:none;'>{a_name}</td><td style='text-align:right; border-left:none;'>{a_val}</td></tr>"

        bs_html = f'''<table class="report-table" style="width:100%; border: 1px solid #333;">
            <tr style="background-color: #F8F1D1;"><th style="text-align:left; width:35%;">Liabilities & Funds</th><th style="text-align:right; width:15%;">Amount</th><th style="text-align:left; width:35%;">Assets & Properties</th><th style="text-align:right; width:15%;">Amount</th></tr>
            {bs_rows}
            <tr style="background-color: #eee; font-weight:bold;"><td style="text-align:left; border-right:none;">Total</td><td style="text-align:right; border-left:none;">₹ {total_liabilities:,.2f}</td><td style="text-align:left; border-right:none;">Total</td><td style="text-align:right; border-left:none;">₹ {total_assets:,.2f}</td></tr>
            </table>'''
            
        st.markdown("---")
        st.subheader(f"⚖️ Balance Sheet (As of {utils.clean_date_to_display(as_of_date)})")
        st.markdown(bs_html, unsafe_allow_html=True)
            
        full_html = f"<h2 style='text-align:center; color:#0F4C81;'>Income & Expenditure Account</h2><p style='text-align:center;'>As of {utils.clean_date_to_display(as_of_date)}</p>{inc_exp_html}<br><hr><br><h2 style='text-align:center; color:#0F4C81;'>Balance Sheet</h2><p style='text-align:center;'>As of {utils.clean_date_to_display(as_of_date)}</p>{bs_html}"
        fin_report = utils.generate_html_report(f"Financial Statements as of {utils.clean_date_to_display(as_of_date)}", full_html)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ (Print Final Statements)", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

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

    elif st.session_state.acc_mode == "💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ":
        st.write("### 💰 ਕੈਸ਼ ਅਤੇ ਬੈਂਕ ਬੈਲੇਂਸ (Detailed View)")
        col_d1, _ = st.columns([1, 2])
        with col_d1: as_of_date = st.date_input("ਕਿਸ ਤਾਰੀਖ ਤੱਕ ਦਾ ਬੈਲੇਂਸ ਦੇਖਣਾ ਹੈ?", value=date.today(), format="DD/MM/YYYY")
        
        df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe = df_don.copy(), df_exp.copy(), df_ledg.copy(), df_cheques.copy()
        for df, col in [(df_don_safe, 'date'), (df_exp_safe, 'date'), (df_ledg_safe, 'txn_date'), (df_chq_safe, 'cheque_date')]:
            if not df.empty:
                df['__dt'] = df[col].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
                df.drop(df[df['__dt'] > as_of_date].index, inplace=True)
                
        bank_balances = get_bank_balances(df_don_safe, df_exp_safe, df_ledg_safe, df_chq_safe, detailed=True)
        df_bals = pd.DataFrame(list(bank_balances.values()))
        
        st.dataframe(df_bals.style.format({
            'ਅਸਲ ਬੈਲੇਂਸ (Actual)': '{:,.2f}', 
            'ਕਲੀਅਰਿੰਗ (Pending Chq)': '{:,.2f}', 
            'ਨੈੱਟ ਬੈਲੇਂਸ (Net)': '{:,.2f}'
        }), hide_index=True, use_container_width=True)
        
        total_bal = df_bals["ਨੈੱਟ ਬੈਲੇਂਸ (Net)"].sum()
        st.markdown(f"**ਕੁੱਲ ਨੈੱਟ ਬੈਲੇਂਸ: ₹ {total_bal:,.2f}**")
        utils.create_print_button(df_bals, f"Detailed Bank Balances as of {utils.clean_date_to_display(as_of_date)}", "🖨️ ਬੈਲੇਂਸ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ")

    elif st.session_state.acc_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)":
        st.write("### 📖 ਮੁੱਖ ਲੈਜ਼ਰ / ਡੇਅ ਬੁੱਕ")
        filter_opt = st.radio("ਫਿਲਟਰ (Filter):", ["ਸਾਰੀਆਂ ਐਂਟਰੀਆਂ (All)", "ਸਿਰਫ਼ ਦਾਨ (Donations)", "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)", "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)"], horizontal=True)
        show_all = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)

        df_main = get_ledger_data(df_don, df_exp, df_ledg, target_bank=None, view_mode="Mirror")
        if not df_main.empty:
            df_main['DateObj'] = df_main['Date'].apply(utils.parse_date_to_obj).fillna(date.today())
            df_main = df_main.sort_values(by=['DateObj', 'ID'], ascending=True) 
            
            if show_all: df_period, running_bal = df_main.copy(), 0.0
            else:
                df_before = df_main[df_main['DateObj'] < start_date]
                running_bal = df_before['Debit'].sum() - df_before['Credit'].sum()
                df_period = df_main[(df_main['DateObj'] >= start_date) & (df_main['DateObj'] <= end_date)].copy()

            balances = []
            for _, row in df_period.iterrows():
                running_bal += (row['Debit'] - row['Credit'])
                balances.append(running_bal)
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(utils.clean_date_to_display)
            
            if filter_opt == "ਸਿਰਫ਼ ਦਾਨ (Donations)": df_period = df_period[df_period['Source'] == 'App (Donation)']
            elif filter_opt == "ਸਿਰਫ਼ ਖਰਚੇ (Expenses)": df_period = df_period[df_period['Source'] == 'App (Expense)']
            elif filter_opt == "ਸਿਰਫ਼ ਬੈਂਕ (Bank Ledger)": df_period = df_period[~df_period['Source'].str.contains('App', na=False)]
            
            df_disp = df_period[['ID', 'Date', 'Description', 'Account', 'Source', 'Debit', 'Credit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']].copy()
            df_disp.rename(columns={'Debit': 'Receipt/In (Dr)', 'Credit': 'Payment/Out (Cr)'}, inplace=True)
            
            st.dataframe(df_disp.style.format({'Receipt/In (Dr)': '{:.2f}', 'Payment/Out (Cr)': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}), hide_index=True, use_container_width=True)
            utils.create_print_button(df_disp, f"Main Ledger ({filter_opt})", "🖨️ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", landscape=True)
        else:
            st.info("ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.acc_mode == "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)":
        st.write("### 🏦 ਬੈਂਕ ਲੈਜ਼ਰ ਅਤੇ ਸਟੇਟਮੈਂਟ ਮਿਲਾਨ")
        
        all_banks_dynamic = set(config.BANK_ACCOUNTS)
        if not df_don.empty and 'bank_account' in df_don.columns:
            all_banks_dynamic.update(df_don['bank_account'].dropna().unique())
        if not df_exp.empty and 'bank_account' in df_exp.columns:
            all_banks_dynamic.update(df_exp['bank_account'].dropna().unique())
        if not df_ledg.empty and 'bank_name' in df_ledg.columns:
            all_banks_dynamic.update(df_ledg['bank_name'].dropna().unique())
            
        selected_bank = st.selectbox("ਬੈਂਕ ਜਾਂ ਕੈਸ਼ ਖਾਤਾ ਚੁਣੋ:", sorted(list(all_banks_dynamic)))
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **ਸਟੇਟਮੈਂਟ ਦੇਖਣ ਦਾ ਤਰੀਕਾ (View Mode):**")
        view_format = st.radio("ਦਿਖਾਉਣ ਦਾ ਤਰੀਕਾ ਚੁਣੋ:", 
            ["📖 ਸੰਸਥਾ ਦਾ ਲੈਜ਼ਰ / Mirror Cash Book (ਪੈਸੇ ਆਏ = Debit)", "🏦 ਅਸਲੀ ਬੈਂਕ ਸਟੇਟਮੈਂਟ (ਪੈਸੇ ਆਏ = Credit)"], 
            horizontal=True)
        st.markdown("---")

        show_all = st.checkbox("✅ ਸਾਰੀਆਂ ਮਿਤੀਆਂ ਦੀਆਂ ਐਂਟਰੀਆਂ ਦਿਖਾਓ", value=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1: start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)
        with col_d2: end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), format="DD/MM/YYYY", disabled=show_all)

        df_compiled = get_ledger_data(df_don, df_exp, df_ledg, target_bank=selected_bank, view_mode=view_format)
        
        if not df_compiled.empty:
            df_compiled['DateObj'] = df_compiled['Date'].apply(utils.parse_date_to_obj).fillna(date.today())
            df_compiled = df_compiled.sort_values(by=['DateObj', 'ID'], ascending=True)
            
            if show_all: df_period, running_bal = df_compiled.copy(), 0.0
            else:
                df_before = df_compiled[df_compiled['DateObj'] < start_date]
                if "ਅਸਲੀ ਬੈਂਕ ਸਟੇਟਮੈਂਟ" in view_format:
                    running_bal = df_before['Credit'].sum() - df_before['Debit'].sum()
                else:
                    running_bal = df_before['Debit'].sum() - df_before['Credit'].sum()
                    
                df_period = df_compiled[(df_compiled['DateObj'] >= start_date) & (df_compiled['DateObj'] <= end_date)].copy()

            balances = []
            for _, row in df_period.iterrows():
                if "ਅਸਲੀ ਬੈਂਕ ਸਟੇਟਮੈਂਟ" in view_format:
                    running_bal += (row['Credit'] - row['Debit'])
                else:
                    running_bal += (row['Debit'] - row['Credit'])
                balances.append(running_bal)
                
            df_period['ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)'] = balances
            df_period['Date'] = df_period['Date'].apply(utils.clean_date_to_display)
            
            df_disp = df_period[['ID', 'Date', 'Description', 'Source', 'Debit', 'Credit', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)']].copy()
            
            if "ਅਸਲੀ ਬੈਂਕ ਸਟੇਟਮੈਂਟ" in view_format:
                df_disp.rename(columns={'Debit': 'Debit / Out (Dr)', 'Credit': 'Credit / In (Cr)'}, inplace=True)
                style_dict = {'Debit / Out (Dr)': '{:.2f}', 'Credit / In (Cr)': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}
            else:
                df_disp.rename(columns={'Debit': 'Debit / In (Dr)', 'Credit': 'Credit / Out (Cr)'}, inplace=True)
                style_dict = {'Debit / In (Dr)': '{:.2f}', 'Credit / Out (Cr)': '{:.2f}', 'ਐਕਸਲ ਬੈਲੇਂਸ (Uploaded Balance)': '{:.2f}', 'ਚੱਲਦਾ ਬੈਲੇਂਸ (Running)': '{:.2f}'}
            
            st.dataframe(df_disp.style.format(style_dict), hide_index=True, use_container_width=True)
            utils.create_print_button(df_disp, f"Bank Ledger - {selected_bank}", "🖨️ ਬੈਂਕ ਲੈਜ਼ਰ ਪ੍ਰਿੰਟ ਕਰੋ", landscape=True)
        else: st.info("ਇਸ ਖਾਤੇ ਵਿੱਚ ਕੋਈ ਐਂਟਰੀ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

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

    elif st.session_state.acc_mode == "📉 ਖਰਚਾ ਸਟੇਟਮੈਂਟ (Expense Statement)":
        st.write("### 📉 ਖਰਚਾ ਸਟੇਟਮੈਂਟ (Expense Statement)")
        if not df_exp.empty:
            uq_cats = sorted(list({str(c).strip() for c in df_exp['category'].dropna() if str(c).strip() != ""}))
            uq_payees = sorted(list({str(p).strip() for p in df_exp.get('payee_name', pd.Series()).dropna() if str(p).strip() != ""}))
            
            c_cat, c_payee = st.columns(2)
            with c_cat: sel_cat = st.selectbox("ਖਰਚੇ ਦੀ ਕੈਟਾਗਰੀ ਚੁਣੋ:", ["All Categories"] + uq_cats)
            with c_payee: sel_payee = st.selectbox("ਪ੍ਰਾਪਤ ਕਰਤਾ (Payee Name) ਚੁਣੋ:", ["All Payees"] + uq_payees)
            
            c1, c2 = st.columns(2)
            d1 = c1.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date.today().replace(day=1), format="DD/MM/YYYY")
            d2 = c2.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
            
            df_e = df_exp.copy()
            df_e['__dt'] = df_e['date'].apply(utils.parse_date_to_obj).fillna(date(1900,1,1))
            df_e = df_e[(df_e['__dt'] >= d1) & (df_e['__dt'] <= d2)]
            
            if sel_cat != "All Categories": 
                df_e = df_e[df_e['category'].astype(str) == sel_cat]
            if sel_payee != "All Payees":
                df_e = df_e[df_e['payee_name'].astype(str).str.contains(sel_payee, case=False, na=False)]
            
            if not df_e.empty:
                df_disp = df_e[['id', 'date', 'payee_name', 'description', 'category', 'bank_account', 'amount']].copy()
                df_disp = utils.format_dates_in_df(df_disp, ascending=True)
                st.dataframe(df_disp, hide_index=True, use_container_width=True)
                total_exp = pd.to_numeric(df_disp['amount'], errors='coerce').sum()
                st.markdown(f"**ਕੁੱਲ ਖਰਚਾ (Total Expense): ₹ {total_exp:,.2f}**")
                utils.create_print_button(df_disp, f"Expense Statement", "🖨 ਪ੍ਰਿੰਟ ਸਟੇਟਮੈਂਟ", landscape=True)
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
                
                # 1. ਧਾਰਮਿਕ / ਕੀਰਤਨ ਸਮਾਗਮ (Religious Programs)
                if cat in ["Kirtan Smagam Expenses", "ਲੰਗਰ (Langar)", "ਛਪਾਈ (Printing)", "ਮਾਰਕੀਟਿੰਗ (Marketing)", "ਸਾਊਂਡ ਸਿਸਟਮ (Sound)", "ਭੇਟਾ - ਕੀਰਤਨੀਏ (Bheta Kirtaniya)", "ਭੇਟਾ - ਕਥਾਵਾਚਕ (Bheta Katha Vachak)"]: 
                    return "ਧਾਰਮਿਕ ਸਮਾਗਮ (Religious Programs)"
                
                # 2. ਤੇਰਾ ਆਸਰਾ / ਵੈਲਫੇਅਰ (Tera Aasra / Welfare)
                if cat in ["Other Asset Purchase", "Salary", "Miscleneous Expenses Tera Aasra", "Free Distribution Clothing", "ਰਾਸ਼ਨ ਖਰੀਦ (Purchase of Ration)", "ਅਧਿਆਪਕਾਂ ਦੀ ਤਨਖਾਹ (Payment to Teachers)", "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)"]: 
                    return "ਤੇਰਾ ਆਸਰਾ (Tera Aasra / Welfare)"
                
                # 3. ਬਾਕੀ ਸਾਰੇ ਖਰਚੇ
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

    elif st.session_state.acc_mode == "📊 CA ਆਡਿਟ ਐਕਸਲ":
        st.write("### 📊 CA ਆਡਿਟ ਅਤੇ ਐਕਸਲ ਬੈਕਅੱਪ")
        st.info("ਆਪਣੇ CA ਨੂੰ ਆਡਿਟ ਲਈ ਇਹ ਪੂਰਾ ਮਲਟੀ-ਸ਼ੀਟ ਐਕਸਲ ਡਾਟਾਬੇਸ ਭੇਜੋ।")
        if st.button("📥 CA ਐਕਸਲ ਬੈਕਅੱਪ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            b = io.BytesIO()
            with pd.ExcelWriter(b, engine='openpyxl') as w:
                for tbl in ["donations", "expenses", "bank_ledger", "parties", "cheques", "stock", "assets", "students", "widows", "ration_distribution", "stock_usage", "receipt_books"]:
                    try: utils.format_dates_in_df(pd.DataFrame(utils.supabase.table(tbl).select("*").limit(100000).execute().data or []), ascending=True).to_excel(w, sheet_name=tbl[:31], index=False)
                    except: pass
            st.download_button("📥 ਡਾਊਨਲੋਡ ਕਰੋ", data=b.getvalue(), file_name=f"CA_Audit_{date.today()}.xlsx", type="primary")
