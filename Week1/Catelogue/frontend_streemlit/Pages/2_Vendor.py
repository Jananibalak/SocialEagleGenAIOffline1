import streamlit as st
import requests

API_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="Vendor Portal", layout="wide")

st.title("🔐 Vendor Portal")

# ---------------------------
# Helpers
# ---------------------------
def request_otp(email):
    return requests.post(f"{API_BASE}/api/vendor/request-otp", json={"email": email})

def register_vendor(payload):
    return requests.post(f"{API_BASE}/api/vendor/register", json=payload)

def login(email, password):
    return requests.post(f"{API_BASE}/api/vendor/login", json={"email": email, "password": password})

def get_catalog(vendor_id):
    return requests.get(f"{API_BASE}/api/catalog/{vendor_id}")

def add_item(payload):
    return requests.post(f"{API_BASE}/api/items", json=payload)

def delete_item(item_id):
    return requests.delete(f"{API_BASE}/api/items/{item_id}")

def update_item(item_id, payload):
    return requests.put(f"{API_BASE}/api/items/{item_id}", json=payload)

def upload_item_image(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    return requests.post(f"{API_BASE}/api/items/upload-image", files=files)

def update_profile(vendor_id, about, logo_url):
    payload = {"about": about, "logo_url": logo_url}
    return requests.put(f"{API_BASE}/api/vendor/profile/{vendor_id}", json=payload)

# ---------------------------
# LOGIN / REGISTER
# ---------------------------
if "vendor_id" not in st.session_state:

    tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register (OTP)"])

    # ---- LOGIN TAB ----
    with tab_login:
        st.subheader("Vendor Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            r = login(email, password)
            if r.status_code != 200:
                st.error(r.text)
            else:
                data = r.json()
                st.session_state["vendor_id"] = data["vendor_id"]
                st.session_state["vendor_name"] = data["name"]
                st.session_state["vendor_whatsapp"] = data["whatsapp"]
                st.success("✅ Login success")
                st.rerun()

    # ---- REGISTER TAB ----
    with tab_register:
        st.subheader("Vendor Registration + OTP Verification")

        if "otp_sent" not in st.session_state:
            st.session_state["otp_sent"] = False

        name = st.text_input("Shop Name")
        whatsapp = st.text_input("WhatsApp Number (with country code)", placeholder="919999999999")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        about = st.text_area("About your shop", placeholder="We sell fresh groceries, juice, snacks...")
        logo_url = st.text_input("Logo URL (optional)", placeholder="We will add logo upload later")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📩 Send OTP"):
                if not email:
                    st.error("Email required")
                else:
                    r = request_otp(email)
                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        st.session_state["otp_sent"] = True
                        st.success("✅ OTP sent to email")

        otp = st.text_input("Enter OTP", max_chars=6)

        with col2:
            if st.button("✅ Register"):
                if not st.session_state["otp_sent"]:
                    st.warning("Please send OTP first.")
                elif not all([name, whatsapp, email, password, otp]):
                    st.error("Fill all required fields + OTP")
                else:
                    payload = {
                        "name": name,
                        "whatsapp": whatsapp,
                        "email": email,
                        "password": password,
                        "about": about,
                        "logo_url": logo_url,
                        "otp": otp
                    }
                    r = register_vendor(payload)
                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        st.success("✅ Registration complete! Now login.")
                        st.session_state["otp_sent"] = False

    st.stop()

# ---------------------------
# DASHBOARD (after login)
# ---------------------------
vendor_id = st.session_state["vendor_id"]
st.success(f"✅ Logged in as: {st.session_state['vendor_name']} (Vendor ID: {vendor_id})")

colA, colB, colC = st.columns([2, 2, 1])
with colA:
    st.write("📞 WhatsApp:", st.session_state["vendor_whatsapp"])
with colC:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.divider()

tab1, tab2, tab3 = st.tabs(["📦 My Items (Edit/Delete)", "➕ Add Item (Upload Image)", "🏪 Profile"])

# ---------------------------
# TAB 1: My Items
# ---------------------------
with tab1:
    st.subheader("My Items")

    r = get_catalog(vendor_id)
    if r.status_code != 200:
        st.error(r.text)
    else:
        items = r.json()["items"]

        if not items:
            st.warning("No items yet.")
        else:
            for it in items:
                st.markdown("---")

                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.image(it["image_url"], width=140)
                with col2:
                    new_title = st.text_input("Title", value=it["title"], key=f"title_{it['id']}")
                    new_price = st.number_input("Price", value=float(it["price"]), min_value=1.0, step=1.0, key=f"price_{it['id']}")
                    new_stock = st.checkbox("In Stock", value=it["in_stock"], key=f"stock_{it['id']}")

                with col3:
                    if st.button("💾 Save", key=f"save_{it['id']}"):
                        payload = {
                            "title": new_title,
                            "price": new_price,
                            "in_stock": new_stock,
                            "image_url": it["image_url"]
                        }
                        ur = update_item(it["id"], payload)
                        if ur.status_code != 200:
                            st.error(ur.text)
                        else:
                            st.success("✅ Updated")
                            st.rerun()

                    if st.button("🗑 Delete", key=f"del_{it['id']}"):
                        dr = delete_item(it["id"])
                        if dr.status_code != 200:
                            st.error(dr.text)
                        else:
                            st.success("✅ Deleted")
                            st.rerun()

# ---------------------------
# TAB 2: Add Item + Upload image
# ---------------------------
with tab2:
    st.subheader("Add New Item (Image Upload)")

    title = st.text_input("Item Title", key="add_title")
    price = st.number_input("Price", min_value=1.0, step=1.0, key="add_price")
    in_stock = st.checkbox("In Stock", value=True, key="add_stock")

    uploaded = st.file_uploader("Upload Item Image", type=["png", "jpg", "jpeg", "webp"])

    if st.button("➕ Add Item Now"):
        if not title:
            st.error("Title required")
            st.stop()

        image_url = "https://via.placeholder.com/300"
        image_path = None

        if uploaded:
            up = upload_item_image(uploaded)
            if up.status_code != 200:
                st.error(up.text)
                st.stop()
            up_data = up.json()
            image_url = up_data["image_url"]
            image_path = up_data["image_path"]

        payload = {
            "vendor_id": vendor_id,
            "title": title,
            "price": price,
            "in_stock": in_stock,
            "image_url": image_url,
            "image_path": image_path
        }

        r = add_item(payload)
        if r.status_code != 200:
            st.error(r.text)
        else:
            st.success("✅ Item added")
            st.rerun()

# ---------------------------
# TAB 3: Profile settings
# ---------------------------
with tab3:
    st.subheader("Vendor Profile")
    st.info("For now logo uses URL. Next we can also upload logo like item image.")

    about = st.text_area("About", key="about_profile")
    logo_url = st.text_input("Logo URL", key="logo_profile")

    if st.button("💾 Save Profile"):
        r = update_profile(vendor_id, about, logo_url)
        if r.status_code != 200:
            st.error(r.text)
        else:
            st.success("✅ Profile updated")
