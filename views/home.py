import streamlit as st

def show_page(is_admin, is_staff):
    st.markdown("<p style='text-align: center; font-size: 20px; font-weight: bold;'>ਸੈਕਸ਼ਨ ਚੁਣੋ ਜੀ:</p>", unsafe_allow_html=True)
    
    def render_nav_row(title, buttons_data):
        st.markdown(f"### {title}")
        cols = st.columns(len(buttons_data))
        for i, (btn_label, tab_name, mode_key, mode_val) in enumerate(buttons_data):
            if cols[i].button(btn_label, use_container_width=True, type="primary" if mode_key == "entry_mode" else "secondary"):
                st.session_state.current_tab = tab_name
                if mode_key: st.session_state[mode_key] = mode_val
                st.rerun()

    render_nav_row("📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ ਅਤੇ ਰਸੀਦਾਂ", [
        ("💰 ਨਵਾਂ ਦਾਨ / ਰਸੀਦ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"), 
        ("📦 ਸਮਾਨ ਦਾ ਦਾਨ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "📦 ਸਮਾਨ ਦਾ ਦਾਨ (In-Kind Donation)"), 
        ("📉 ਖਰਚਾ (Payment)", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "📉 ਖਰਚਾ (Payment Debit)"), 
        ("🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "entry_mode", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ / ਵਾਊਚਰ (Reprint)")
    ])
    
    render_nav_row("🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਆਡਿਟ", [
        ("⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"), 
        ("📖 ਮੁੱਖ ਲੈਜ਼ਰ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Main Daybook)"), 
        ("🏦 ਬੈਂਕ ਲੈਜ਼ਰ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "🏦 ਬੈਂਕ ਲੈਜ਼ਰ (Bank Book)"), 
        ("📁 ਪਾਰਟੀਆਂ (Parties)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📁 ਪਾਰਟੀਆਂ ਅਤੇ ਚੈੱਕ (Parties & Cheques)"), 
        ("📊 CA ਐਕਸਪੋਰਟ", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "acc_mode", "📊 CA ਆਡਿਟ ਐਕਸਲ (CA Audit Export)")
    ])
    
    render_nav_row("📦 ਸਟਾਕ, ਵਿਦਿਆਰਥੀ, ਵਿਧਵਾ ਰਾਸ਼ਨ ਅਤੇ ਪ੍ਰਬੰਧ", [
        ("📦 ਸਟਾਕ ਭੰਡਾਰ", "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)", "other_mode", "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)"), 
        ("🎓 ਵਿਦਿਆਰਥੀ", "🎓 ਵਿਦਿਆਰਥੀ (Students)", None, None), 
        ("👵 ਵਿਧਵਾ ਰਾਸ਼ਨ", "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)", None, None), 
        ("🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ", "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)", None, None)
    ])
    
    if is_admin and st.button("📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ", use_container_width=True): 
        st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"
        st.session_state.admin_mode = "📂 ਬਲਕ ਐਕਸਲ ਅੱਪਲੋਡ (Bulk Upload)"
        st.rerun()
    elif is_staff and st.button("🗑️ ਡਿਲੀਟ ਬੇਨਤੀ", use_container_width=True): 
        st.session_state.current_tab = "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)"
        st.session_state.admin_mode = "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)"
        st.rerun()
