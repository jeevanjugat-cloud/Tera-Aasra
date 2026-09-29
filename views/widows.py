import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import utils

def show_page(is_mgmt):
    st.header("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ ਡਾਟਾਬੇਸ")
    w_tab1, w_tab2, w_tab3 = st.tabs(["➕ ਨਵਾਂ ਕਾਰਡ ਬਣਾਓ", "📋 ਡਾਟਾਬੇਸ ਸੂਚੀ", "🛍️ ਰਾਸ਼ਨ ਵੰਡ"])
    
    with w_tab1:
        if not is_mgmt:
            with st.form("widow_form", clear_on_submit=True):
                c_w1, c_w2, c_w3 = st.columns(3)
                with c_w1: w_form_no = st.text_input("ਫਾਰਮ ਨੰ:"); w_name = st.text_input("ਨਾਮ ਬੀਬੀ: *ਜ਼ਰੂਰੀ*"); w_husband = st.text_input("ਪਤੀ ਦਾ ਨਾਮ:"); w_death_date = st.text_input("ਪਤੀ ਦੀ ਮੌਤ ਦੀ ਤਾਰੀਖ:")
                with c_w2: w_card_no = st.text_input("ਕਾਰਡ ਨੰ:"); w_age = st.text_input("ਉਮਰ / ਸਾਲ:"); w_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ: *ਜ਼ਰੂਰੀ*"); w_issued_by = st.text_input("ਜਾਰੀ ਕਰਤਾ:")
                with c_w3: w_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg']); w_card_date = st.date_input("ਸ਼ੁਰੂਆਤ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                
                w_address = st.text_area("ਪਤਾ (Address):")
                cb1, cb2 = st.columns(2)
                with cb1: w_boys = st.text_area("ਲੜਕੇ (ਉਮਰ, ਕਲਾਸ):")
                with cb2: w_girls = st.text_area("ਲੜਕੀਆਂ (ਉਮਰ, ਕਲਾਸ):")
                
                if st.form_submit_button("ਕਾਰਡ ਸੇਵ ਕਰੋ", type="primary") and w_name:
                    utils.supabase.table("widows").insert({"form_no": w_form_no, "card_no": w_card_no, "name": w_name, "age": w_age, "husband_name": w_husband, "husband_death_date": w_death_date, "phone": w_phone, "address": w_address, "boys_details": w_boys, "girls_details": w_girls, "issued_by": w_issued_by, "join_date": str(w_card_date), "photo_base64": utils.compress_image(w_photo)}).execute()
                    st.success(f"✅ '{w_name}' ਦਾ ਕਾਰਡ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ!")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    with w_tab2:
        st.write("### 📑 ਰਜਿਸਟਰਡ ਵਿਧਵਾਵਾਂ ਦੀ ਸੂਚੀ")
        try: widows_data = utils.supabase.table("widows").select("*").limit(100000).execute().data or []
        except: widows_data = []
            
        if widows_data:
            df_w = pd.DataFrame(widows_data)
            display_cols = [c for c in ['card_no', 'name', 'age', 'husband_name', 'phone', 'address', 'join_date'] if c in df_w.columns]
            st.dataframe(utils.format_dates_in_df(df_w[display_cols], ascending=False), hide_index=True, use_container_width=True)
            
            df_print_w = utils.format_dates_in_df(df_w, ascending=False).copy()
            df_print_w['ਫੋਟੋ'] = df_print_w['photo_base64'].apply(lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo') if 'photo_base64' in df_print_w.columns else 'No Photo'
            print_cols_map_w = {'card_no': 'ਕਾਰਡ ਨੰ', 'name': 'ਨਾਮ', 'age': 'ਉਮਰ', 'husband_name': 'ਪਤੀ', 'phone': 'ਫ਼ੋਨ', 'address': 'ਪਤਾ', 'ਫੋਟੋ': 'ਫੋਟੋ'}
            df_print_w = df_print_w.rename(columns={k: v for k, v in print_cols_map_w.items() if k in df_print_w.columns})
            html_table_w = df_print_w[[v for k, v in print_cols_map_w.items() if v in df_print_w.columns]].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_w = utils.generate_html_report_landscape("Widows Database", html_table_w)
            with open(report_file_w, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_w, mime="text/html", type="primary")
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    with w_tab3:
        st.write("### 🛍️ ਮਹੀਨਾਵਾਰ ਰਾਸ਼ਨ ਵੰਡ")
        try:
            widows_list = utils.supabase.table("widows").select("*").limit(100000).execute().data or []
            stock_list = utils.supabase.table("stock").select("*").gt("quantity", 0).limit(100000).execute().data or []
        except: widows_list, stock_list = [], []
            
        if not widows_list: st.warning("⚠️ ਪਹਿਲਾਂ ਵਿਧਵਾਵਾਂ ਦਾ ਪ੍ਰੋਫਾਈਲ ਦਰਜ ਕਰੋ।")
        elif not stock_list: st.warning("⚠️ ਸਟਾਕ ਖਾਲੀ ਹੈ।")
        else:
            if not is_mgmt:
                w_names = [f"ਕਾਰਡ {w.get('card_no','-')} - {w.get('name','Unknown')} ({w.get('phone','')})" for w in widows_list]
                s_dict = {s['item_name']: float(s.get('quantity', 0) or 0) for s in stock_list}
                with st.form("ration_dist_form"):
                    col1, col2 = st.columns(2)
                    with col1: selected_widow = st.selectbox("ਕਿਸ ਨੂੰ ਰਾਸ਼ਨ ਦਿੱਤਾ?", w_names); dist_date = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    with col2: selected_item = st.selectbox("ਕਿਹੜਾ ਸਮਾਨ ਦਿੱਤਾ?", list(s_dict.keys())); qty_to_give = st.number_input(f"ਮਾਤਰਾ - ਸਟਾਕ ਮੌਜੂਦ: {s_dict.get(selected_item, 0)}", min_value=0.5, step=0.5)
                    
                    if st.form_submit_button("ਰਾਸ਼ਨ ਵੰਡ ਸੇਵ ਕਰੋ", type="primary"):
                        old_qty = s_dict.get(selected_item, 0)
                        if qty_to_give > old_qty: st.error(f"❌ ਗਲਤੀ: ਸਟਾਕ ਵਿੱਚ ਸਿਰਫ਼ {old_qty} ਮਾਤਰਾ ਬਾਕੀ ਹੈ!")
                        else:
                            new_qty = max(0.0, old_qty - qty_to_give)
                            curr_stock = utils.supabase.table("stock").select("*").eq("item_name", selected_item).execute().data
                            if curr_stock:
                                curr_val = float(curr_stock[0].get('estimated_value', 0) or 0)
                                utils.supabase.table("stock").update({"quantity": new_qty, "estimated_value": round((curr_val * (new_qty / old_qty)) if old_qty > 0 else 0.0, 2), "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).eq("item_name", selected_item).execute()
                                utils.supabase.table("stock_usage").insert({"item_name": selected_item, "quantity": qty_to_give, "unit": curr_stock[0].get('unit', ''), "purpose": f"Ration to: {selected_widow}", "usage_date": str(dist_date)}).execute()
                            
                            widow_just_name = selected_widow.split(" - ")[1].split(" (")[0] if " - " in selected_widow else selected_widow
                            utils.supabase.table("ration_distribution").insert({"widow_name": widow_just_name, "item_name": selected_item, "quantity": qty_to_give, "distribution_date": str(dist_date)}).execute()
                            st.success(f"✅ {widow_just_name} ਨੂੰ {qty_to_give} {selected_item} ਦੇ ਦਿੱਤਾ ਗਿਆ ਹੈ!"); time.sleep(1.5); st.rerun()
                            
        st.markdown("---")
        st.write("#### 📑 ਪਿਛਲੀ ਰਾਸ਼ਨ ਵੰਡ ਦਾ ਰਿਕਾਰਡ")
        try: dist_data = utils.supabase.table("ration_distribution").select("*").order("id", desc=True).limit(50).execute().data or []
        except: dist_data = []
        if dist_data: st.dataframe(utils.format_dates_in_df(pd.DataFrame(dist_data)[['id', 'distribution_date', 'widow_name', 'item_name', 'quantity']], ascending=False), hide_index=True, use_container_width=True)
