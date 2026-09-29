import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import config
import utils

def show_page(is_mgmt, is_admin):
    st.header("📦 ਸਟਾਕ ਅਤੇ ਰਸੀਦ ਕਿਤਾਬਾਂ (Stock & Books)")
    modes = ["📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)", "📤 ਸਟਾਕ ਵੰਡ (Stock Issuance)", "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"]
    if st.session_state.other_mode not in modes: st.session_state.other_mode = modes[0]
    st.session_state.other_mode = st.radio("ਸੈਕਸ਼ਨ ਚੁਣੋ:", modes, index=modes.index(st.session_state.other_mode), horizontal=True)
    st.markdown("---")

    if st.session_state.other_mode == "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)":
        st.write("### 📑 ਮੌਜੂਦਾ ਸਟਾਕ ਰਿਪੋਰਟ")
        st.info("💡 ਨਵਾਂ ਸਟਾਕ ਸਿਰਫ਼ 'ਸਮਾਨ ਦਾ ਦਾਨ' ਜਾਂ 'ਖਰਚਾ' ਵਾਲੇ ਫਾਰਮ ਰਾਹੀਂ ਹੀ ਜੋੜਿਆ ਜਾ ਸਕਦਾ ਹੈ।")
        try: stock_res = utils.supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
        except: stock_res = []
        if stock_res:
            df_stock = pd.DataFrame(stock_res)
            disp_cols = [c for c in ['item_name', 'quantity', 'unit', 'estimated_value', 'procurement_date', 'last_updated'] if c in df_stock.columns]
            df_disp = utils.format_dates_in_df(df_stock[disp_cols], ascending=False)
            st.dataframe(df_disp, hide_index=True, use_container_width=True)
            
            # Universal Print Button for Current Stock
            utils.create_print_button(df_disp, "Current Stock Inventory", "🖨️️ ਸਟਾਕ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ")
        else: st.warning("ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਸਮਾਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    elif st.session_state.other_mode == "📤 ਸਟਾਕ ਵੰਡ (Stock Issuance)":
        col1, col2 = st.columns([1, 2])
        with col1:
            if not is_mgmt:
                with st.form("stock_issue_form", clear_on_submit=True):
                    st.write("### 📤 ਸਟਾਕ ਵੰਡੋ ਜਾਂ ਵਰਤੋ")
                    try: stock_res = utils.supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
                    except: stock_res = []
                    if stock_res:
                        s_dict = {s['item_name']: float(s.get('quantity', 0) or 0) for s in stock_res}
                        s_units = {s['item_name']: s.get('unit', '') for s in stock_res}
                        s_items = list(s_dict.keys())
                        item_name = st.selectbox("ਕਿਹੜਾ ਸਮਾਨ ਵੰਡਣਾ ਹੈ?", s_items)
                        item_unit = s_units.get(item_name, '')
                        is_whole_issue = any(u in item_unit for u in ["Pcs", "Bags", "ਪੀਸ", "ਬੈਗ"])
                        qty = st.number_input(f"ਮਾਤਰਾ ({item_unit}) - ਮੌਜੂਦ: {s_dict.get(item_name, 0)}", min_value=0.5 if not is_whole_issue else 1.0, step=1.0 if is_whole_issue else 0.5)
                        purpose_input = st.text_input("ਵਰਤੋਂ ਦਾ ਕਾਰਨ / ਕਿਸਨੂੰ ਦਿੱਤਾ?")
                        proc_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                        if st.form_submit_button("ਸਟਾਕ ਜਾਰੀ ਕਰੋ", type="primary"):
                            if not purpose_input.strip(): st.error("❌ ਕਿਰਪਾ ਕਰਕੇ ਵਰਤੋਂ ਦਾ ਕਾਰਨ ਦੱਸੋ!")
                            elif is_whole_issue and not float(qty).is_integer(): st.error("❌ ਗਲਤੀ: ਮਾਤਰਾ ਪੂਰਾ ਨੰਬਰ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ!")
                            else:
                                old_qty = s_dict.get(item_name, 0)
                                if qty > old_qty: st.error(f"❌ ਗਲਤੀ: ਸਟਾਕ ਵਿੱਚ ਸਿਰਫ਼ {old_qty} ਮਾਤਰਾ ਬਾਕੀ ਹੈ!")
                                else:
                                    new_qty = old_qty - qty
                                    curr_stock = utils.supabase.table("stock").select("*").eq("item_name", item_name).execute().data
                                    old_val = float(curr_stock[0].get('estimated_value', 0) or 0) if curr_stock else 0.0
                                    new_val = (old_val * (new_qty / old_qty)) if old_qty > 0 else 0.0
                                    utils.supabase.table("stock").update({"quantity": new_qty, "estimated_value": round(new_val, 2), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", item_name).execute()
                                    utils.supabase.table("stock_usage").insert({"item_name": item_name, "quantity": qty, "unit": item_unit, "purpose": purpose_input, "usage_date": str(proc_date)}).execute()
                                    st.success(f"✅ '{item_name}' ਜਾਰੀ ਕਰ ਦਿੱਤਾ ਗਿਆ ਹੈ!"); time.sleep(1.2); st.rerun()
                    else: st.warning("ਸਟਾਕ ਖਾਲੀ ਹੈ।")
        with col2:
            st.write("### 📝 ਵਰਤੋਂ ਦਾ ਰਿਕਾਰਡ")
            try: usage_res = utils.supabase.table("stock_usage").select("*").order("id", desc=True).limit(50).execute().data or []
            except: usage_res = []
            if usage_res:
                df_usage = pd.DataFrame(usage_res)[['usage_date', 'item_name', 'quantity', 'unit', 'purpose']]
                df_disp_usg = utils.format_dates_in_df(df_usage, ascending=False)
                st.dataframe(df_disp_usg, hide_index=True, use_container_width=True)
                
                # Universal Print Button for Stock Usage
                utils.create_print_button(df_disp_usg, "Stock Usage Record", "🖨️ ਪ੍ਰਿੰਟ ਵਰਤੋਂ ਸੂਚੀ")
            else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")

    elif st.session_state.other_mode == "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)":
        if is_admin:
            with st.form("book_issue_form", clear_on_submit=True):
                st.write("### 📖 ਨਵੀਂ ਰਸੀਦ ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ")
                col_b1, col_b2 = st.columns(2)
                with col_b1: collector_input = st.text_input("ਕਲੈਕਟਰ ਦਾ ਨਾਮ"); start_ser = st.number_input("ਸ਼ੁਰੂਆਤੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=1)
                with col_b2: end_ser = st.number_input("ਆਖਰੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=100); issue_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                if st.form_submit_button("ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ (Issue)", type="primary"):
                    if collector_input and end_ser >= start_ser:
                        existing_books = utils.supabase.table("receipt_books").select("*").execute().data or []
                        overlap = any(int(start_ser) <= int(b['end_no']) and int(end_ser) >= int(b['start_no']) for b in existing_books)
                        if overlap: st.error("❌ ਗਲਤੀ: ਇਹ ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਜਾਰੀ ਕੀਤੇ ਜਾ ਚੁੱਕੇ ਹਨ!")
                        else:
                            utils.supabase.table("receipt_books").insert({"collector_name": collector_input, "start_no": int(start_ser), "end_no": int(end_ser), "issued_date": issue_date.strftime("%Y-%m-%d"), "status": "Active"}).execute()
                            st.success("✅ ਕਿਤਾਬ ਜਾਰੀ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!")
        st.write("### 📑 ਜਾਰੀ ਕੀਤੀਆਂ ਗਈਆਂ ਕਿਤਾਬਾਂ")
        try: books_all = utils.supabase.table("receipt_books").select("*").order("id", desc=True).limit(100000).execute().data or []
        except: books_all = []
        if books_all:
            df_books = pd.DataFrame(books_all)[['collector_name', 'start_no', 'end_no', 'issued_date', 'status']]
            df_disp_books = utils.format_dates_in_df(df_books, ascending=False)
            st.dataframe(df_disp_books, hide_index=True, use_container_width=True)
            
            # Universal Print Button for Books
            utils.create_print_button(df_disp_books, "Issued Receipt Books", "🖨️ ਕਿਤਾਬਾਂ ਦੀ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ")
