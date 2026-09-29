import streamlit as st
import pandas as pd
from datetime import date, datetime
import calendar
import time
import utils

def show_page(is_admin, is_mgmt):
    st.header("🧑‍💼 ਸਟਾਫ ਮੈਨੇਜਮੈਂਟ ਅਤੇ ਹਾਜ਼ਰੀ")
    att_tabs = st.tabs(["👤 ਸਟਾਫ ਪ੍ਰੋਫਾਈਲ", "🛡️ ਐਡਮਿਨ ਮਨਜ਼ੂਰੀ", "📋 ਮਹੀਨਾਵਾਰ ਰਿਪੋਰਟ"])
    
    with att_tabs[0]:
        col_st1, col_st2 = st.columns([1, 2])
        with col_st1:
            if is_admin or is_mgmt:
                with st.form("staff_profile_form", clear_on_submit=True):
                    st.write("### ➕ ਨਵਾਂ ਸਟਾਫ ਦਰਜ ਕਰੋ")
                    st_name = st.text_input("ਸਟਾਫ ਦਾ ਨਾਮ *ਜ਼ਰੂਰੀ*")
                    st_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                    st_role = st.selectbox("ਡਿਊਟੀ / ਅਹੁਦਾ", ["ਮੈਨੇਜਰ", "ਅਧਿਆਪਕ", "ਕਲਰਕ", "ਸੇਵਾਦਾਰ", "ਡਰਾਈਵਰ", "ਹੋਰ"])
                    st_login = st.selectbox("ਲਾਗਇਨ ਆਈ.ਡੀ", ["ਕੋਈ ਨਹੀਂ (None)", "emp1", "emp2", "emp3", "emp4", "emp5"])
                    st_join = st.date_input("ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                    st_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and st_name:
                        utils.supabase.table("staff_profiles").insert({"name": st_name, "phone": st_phone, "role": st_role, "join_date": str(st_join), "photo_base64": utils.compress_image(st_photo), "login_id": st_login if "emp" in st_login else ""}).execute()
                        st.success(f"✅ '{st_name}' ਸੇਵ ਹੋ ਗਿਆ!")
            else: st.info("⚠️ ਸਿਰਫ਼ ਐਡਮਿਨ ਲਈ।")
                
        with col_st2:
            st.write("### 📋 ਸਟਾਫ ਦੀ ਸੂਚੀ")
            try: staff_data = utils.supabase.table("staff_profiles").select("*").limit(100000).execute().data or []
            except: staff_data = []
            if staff_data: st.dataframe(utils.format_dates_in_df(pd.DataFrame(staff_data)[['name', 'phone', 'role', 'login_id', 'join_date']], ascending=False), hide_index=True, use_container_width=True)

    with att_tabs[1]:
        st.write("### 🛡️ ਪੈਂਡਿੰਗ ਹਾਜ਼ਰੀ ਬੇਨਤੀਆਂ")
        try: att_reqs = utils.supabase.table("attendance_requests").select("*").eq("status", "Pending").limit(100000).execute().data or []
        except: att_reqs = []
        if att_reqs:
            st.dataframe(utils.format_dates_in_df(pd.DataFrame(att_reqs)[['id', 'staff_name', 'date', 'requested_status', 'reason', 'created_at']], ascending=False), hide_index=True, use_container_width=True)
            req_dict = {f"ID: {r.get('id','')} - {r.get('staff_name','')} ({utils.clean_date_to_display(r.get('date',''))} : {r.get('requested_status','')})": r for r in att_reqs}
            sel_req_str = st.selectbox("ਬੇਨਤੀ ਚੁਣੋ", list(req_dict.keys()))
            if sel_req_str:
                target_r = req_dict[sel_req_str]
                col_aa, col_ar = st.columns(2)
                with col_aa:
                    if st.button("✅ ਹਾਜ਼ਰੀ ਮਨਜ਼ੂਰ ਕਰੋ", type="primary"):
                        existing = utils.supabase.table("attendance").select("*").eq("staff_name", target_r['staff_name']).eq("date", target_r['date']).execute().data
                        if existing: utils.supabase.table("attendance").update({"status": target_r['requested_status']}).eq("id", existing[0]['id']).execute()
                        else: utils.supabase.table("attendance").insert({"staff_name": target_r['staff_name'], "date": target_r['date'], "in_time": "Manual", "out_time": "Manual", "status": target_r['requested_status']}).execute()
                        utils.supabase.table("attendance_requests").update({"status": "Approved"}).eq("id", target_r['id']).execute()
                        st.success("✅ ਹਾਜ਼ਰੀ ਲੱਗ ਗਈ ਹੈ!"); time.sleep(1.5); st.rerun()
                with col_ar:
                    if st.button("❌ ਬੇਨਤੀ ਰੱਦ ਕਰੋ"):
                        utils.supabase.table("attendance_requests").update({"status": "Rejected"}).eq("id", target_r['id']).execute()
                        st.error("❌ ਰੱਦ ਕੀਤੀ ਗਈ!"); time.sleep(1.5); st.rerun()
        else: st.info("ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")

    with att_tabs[2]:
        st.write("### 📅 ਮਹੀਨਾਵਾਰ ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ")
        col_m1, col_m2 = st.columns(2)
        with col_m1: sel_month = st.selectbox("ਮਹੀਨਾ (Month)", range(1, 13), index=date.today().month - 1)
        with col_m2: sel_year = st.selectbox("ਸਾਲ (Year)", range(2024, 2035), index=date.today().year - 2024)
        num_days = calendar.monthrange(sel_year, sel_month)[1]
        
        try:
            all_att = utils.supabase.table("attendance").select("*").gte("date", f"{sel_year}-{sel_month:02d}-01").lte("date", f"{sel_year}-{sel_month:02d}-{num_days:02d}").limit(100000).execute().data or []
            if all_att:
                df_att = pd.DataFrame(all_att)
                df_att['date_obj'] = df_att['date'].apply(utils.parse_date_to_obj)
                df_att = df_att.dropna(subset=['date_obj'])
                df_att['day'] = df_att['date_obj'].apply(lambda x: x.day)
                
                def get_status_code(s):
                    s = str(s).lower()
                    if "present" in s or "ਹਾਜ਼ਰ" in s: return "P"
                    if "absent" in s or "ਛੁੱਟੀ" in s or "ਗੈਰ" in s: return "A"
                    if "half" in s or "ਅੱਧਾ" in s: return "HD"
                    return "P"
                    
                df_att['status_code'] = df_att['status'].apply(get_status_code)
                pivot_df = df_att.pivot_table(index='staff_name', columns='day', values='status_code', aggfunc='last').reindex(columns=list(range(1, num_days + 1))).fillna("-")
                pivot_df['Total P'] = (pivot_df[list(range(1, num_days + 1))] == 'P').sum(axis=1) + ((pivot_df[list(range(1, num_days + 1))] == 'HD').sum(axis=1) * 0.5)
                pivot_df['Total A'] = (pivot_df[list(range(1, num_days + 1))] == 'A').sum(axis=1)
                st.dataframe(pivot_df.reset_index(), hide_index=True, use_container_width=True)
            else: st.info("ਇਸ ਮਹੀਨੇ ਦਾ ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")
        except: pass
