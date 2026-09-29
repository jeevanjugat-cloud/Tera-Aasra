import streamlit as st
import pandas as pd
from datetime import date
import utils

def show_page(is_mgmt):
    st.header("🎓 ਵਿਦਿਆਰਥੀਆਂ ਦਾ ਰਿਕਾਰਡ")
    s_tab1, s_tab2 = st.tabs(["➕ ਨਵਾਂ ਵਿਦਿਆਰਥੀ ਦਰਜ ਕਰੋ", "📋 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ"])
    
    with s_tab1:
        if not is_mgmt:
            with st.form("student_form", clear_on_submit=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1: stu_name = st.text_input("ਵਿਦਿਆਰਥੀ ਦਾ ਨਾਮ"); stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ")
                with col_s2: stu_course = st.selectbox("ਕਲਾਸ", ["ਕੰਪਿਊਟਰ ਸਿੱਖਿਆ", "ਸਿਲਾਈ ਸੈਂਟਰ"]); join_date = st.date_input("ਦਾਖਲਾ ਮਿਤੀ", value=date.today(), format="DD/MM/YYYY")
                s_photo = st.file_uploader("ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ", type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("ਸੇਵ ਕਰੋ", type="primary") and stu_name:
                    utils.supabase.table("students").insert({"name": stu_name, "phone": stu_phone, "course": stu_course, "join_date": join_date.strftime("%Y-%m-%d"), "pass_date": "ਪੜ੍ਹਾਈ ਜਾਰੀ ਹੈ", "photo_base64": utils.compress_image(s_photo)}).execute()
                    st.success(f"✅ '{stu_name}' ਦਾ ਰਿਕਾਰਡ ਸੇਵ ਹੋ ਗਿਆ!")
        else: st.info("👁️ ਮੈਨੇਜਮੈਂਟ ਮੋਡ।")

    with s_tab2:
        st.write("### 📑 ਵਿਦਿਆਰਥੀਆਂ ਦੀ ਸੂਚੀ")
        try: student_data = utils.supabase.table("students").select("*").limit(100000).execute().data or []
        except: student_data = []
        
        if student_data:
            df_stu = pd.DataFrame(student_data)
            display_cols = [c for c in ['name', 'phone', 'course', 'join_date', 'pass_date'] if c in df_stu.columns]
            st.dataframe(utils.format_dates_in_df(df_stu[display_cols], ascending=False), hide_index=True, use_container_width=True)
            
            df_print = utils.format_dates_in_df(df_stu, ascending=False).copy()
            df_print['ਫੋਟੋ (Photo)'] = df_print['photo_base64'].apply(lambda x: f'<img src="data:image/jpeg;base64,{x}" class="table-img">' if x else 'No Photo') if 'photo_base64' in df_print.columns else 'No Photo'
            print_cols_map = {'name': 'ਨਾਮ', 'phone': 'ਫ਼ੋਨ', 'course': 'ਕਲਾਸ', 'join_date': 'ਦਾਖਲਾ ਮਿਤੀ', 'pass_date': 'ਸਟੇਟਸ', 'ਫੋਟੋ (Photo)': 'ਫੋਟੋ'}
            df_print = df_print.rename(columns={k: v for k, v in print_cols_map.items() if k in df_print.columns})
            html_table = df_print[[v for k, v in print_cols_map.items() if v in df_print.columns]].to_html(index=False, border=1, classes='report-table', escape=False)
            report_file_stu = utils.generate_html_report_landscape("Students List", html_table)
            with open(report_file_stu, "r", encoding="utf-8") as file: st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=report_file_stu, mime="text/html", type="primary")
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")
