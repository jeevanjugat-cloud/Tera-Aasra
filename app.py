import streamlit as st
import config
import utils
import os

st.set_page_config(page_title="ਸਭਾ ਮੈਨੇਜਰ ਪ੍ਰੋ", page_icon="logo.png", layout="wide")
config.apply_custom_css()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = st.session_state.username = None

for state_key, def_val in [('current_tab', "🏠 ਹੋਮ ਪੇਜ (Home)"), ('entry_mode', "💰 ਨਕਦ/ਬੈਂਕ ਦਾਨ (Cash/Bank Receipt)"), ('acc_mode', "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)"), ('other_mode', "📑 ਮੌਜੂਦਾ ਸਟਾਕ (Current Stock)"), ('admin_mode', "🗑️ ਡਿਲੀਟ ਮੈਨੇਜਮੈਂਟ (Delete)")]:
    if state_key not in st.session_state: st.session_state[state_key] = def_val

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): st.image("logo.png", width=100)
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h2 style='color:#4A1B15;'>{config.NGO_NAME_PB}</h2><p style='color: #E53935; font-weight: bold;'>{config.NGO_TAGLINE_PB}</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in config.USERS and config.USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = config.USERS[username_input]["role"]
                    st.session_state.username = username_input
                    st.session_state.current_tab = "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)" if st.session_state.role == "employee" else "🏠 ਹੋਮ ਪੇਜ (Home)"
                    st.rerun()
                else: st.error("ਗਲਤ ਪਾਸਵਰਡ!")
    st.stop()

is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"
is_staff = st.session_state.role == "staff"
is_employee = st.session_state.role == "employee"

with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    role_display = {"admin": "ਐਡਮਿਨ ਮੋਡ (Admin)", "management": "ਮੈਨੇਜਮੈਂਟ (View Only)", "staff": "ਕਰਮਚਾਰੀ ਮੋਡ (Staff)", "employee": "ਸਟਾਫ ਹਾਜ਼ਰੀ ਮੋਡ (Employee)"}.get(st.session_state.role, "")
    st.success(f"✅ {role_display}")
    if st.button("ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.role = st.session_state.username = None
        st.rerun()
    st.markdown("---")
    st.subheader("ਮੁੱਖ ਮੀਨੂ")
    menu_opts = ["⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)"] if is_employee else ["🏠 ਹੋਮ ਪੇਜ (Home)", "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)", "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)", "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)", "🎓 ਵਿਦਿਆਰਥੀ (Students)", "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)", "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)"]
    if is_admin or is_staff: menu_opts.append("⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)")
    c_idx = menu_opts.index(st.session_state.current_tab) if st.session_state.current_tab in menu_opts else 0
    st.session_state.current_tab = st.radio("ਚੁਣੋ", menu_opts, index=c_idx, label_visibility="collapsed")

logo_b64 = utils.get_base64_image("logo.png")
st.markdown(f"<div class='pro-header-flex'>{f'<img src=\"data:image/png;base64,{logo_b64}\" class=\"pro-logo\">' if logo_b64 else ''}<div class='pro-text-box'><div class='pro-title'>{config.NGO_NAME_PB}</div><div class='pro-tagline'>{config.NGO_TAGLINE_PB}</div><div class='pro-sub'>{config.NGO_ADDRESS_PB}</div></div></div>", unsafe_allow_html=True)

if st.session_state.current_tab != "🏠 ਹੋਮ ਪੇਜ (Home)" and not is_employee:
    if st.button("🏠 ਹੋਮ ਪੇਜ 'ਤੇ ਜਾਓ", type="secondary"): st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"; st.rerun()
    st.markdown("---")

# --- SMART ROUTING SYSTEM ---
try:
    if st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
        from views import home
        home.show_page(is_admin, is_staff)
    elif st.session_state.current_tab == "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)":
        from views import attendance
        attendance.show_page(st.session_state.username)
    elif st.session_state.current_tab == "📝 ਰੋਜ਼ਾਨਾ ਐਂਟਰੀਆਂ (Voucher Entry)":
        from views import vouchers
        vouchers.show_page(is_mgmt)
    elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA Reports)":
        from views import ledgers
        ledgers.show_page(is_admin)
    elif st.session_state.current_tab == "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Receipt Books)":
        from views import stock
        stock.show_page(is_mgmt, is_admin)
    elif st.session_state.current_tab == "🎓 ਵਿਦਿਆਰਥੀ (Students)":
        from views import students
        students.show_page(is_mgmt)
    elif st.session_state.current_tab == "👵 ਵਿਧਵਾ ਰਾਸ਼ਨ (Widows Ration)":
        from views import widows
        widows.show_page(is_mgmt)
    elif st.session_state.current_tab == "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff & Attendance)":
        from views import staff
        staff.show_page(is_admin, is_mgmt)
    elif st.session_state.current_tab == "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin & Edit)":
        from views import admin
        admin.show_page(is_admin, is_staff)
except ModuleNotFoundError:
    st.info("🚧 ਇਹ ਸੈਕਸ਼ਨ ਅਜੇ ਬਣ ਰਿਹਾ ਹੈ। (Please create the corresponding file in views folder)")
