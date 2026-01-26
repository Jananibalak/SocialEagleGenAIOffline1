import streamlit as st
import requests

API_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="ShowZio", layout="wide")

with open("ui.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ---------------------------
# Routing
# ---------------------------
if "route" not in st.session_state:
    st.session_state["route"] = "home"

def go(route):
    st.session_state["route"] = route
    st.rerun()


# ---------------------------
# API Helpers
# ---------------------------
def api_get(path):
    return requests.get(API_BASE + path)

def api_post(path, payload=None, files=None):
    if files is not None:
        return requests.post(API_BASE + path, files=files)
    return requests.post(API_BASE + path, json=payload)

def api_put(path, payload=None):
    return requests.put(API_BASE + path, json=payload)

def api_delete(path):
    return requests.delete(API_BASE + path)


# Vendor APIs
def request_otp(email): return api_post("/api/vendor/request-otp", {"email": email})
def register_vendor(payload): return api_post("/api/vendor/register", payload)
def vendor_login(email, password): return api_post("/api/vendor/login", {"email": email, "password": password})

def upload_logo(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    return api_post("/api/vendor/upload-logo", files=files)

def update_profile(vendor_id, about, logo_url=None, logo_path=None):
    return api_put(f"/api/vendor/profile/{vendor_id}", {"about": about, "logo_url": logo_url, "logo_path": logo_path})

def upload_item_image(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    return api_post("/api/items/upload-image", files=files)

def add_item(payload): return api_post("/api/items", payload)
def update_item(item_id, payload): return api_put(f"/api/items/{item_id}", payload)
def delete_item(item_id): return api_delete(f"/api/items/{item_id}")


# Customer APIs
def get_vendors():
    r = api_get("/api/vendors")
    if r.status_code != 200:
        return []
    return r.json().get("vendors", [])

def get_catalog(vendor_id: int):
    r = api_get(f"/api/catalog/{vendor_id}")
    if r.status_code != 200:
        return None
    return r.json()


# ---------------------------
# Navbar (top)
# ---------------------------
# ---------------------------
# Navbar (clickable)
# ---------------------------
st.markdown(
    """
    <div class="navbar">
      <div class="navbar-inner">
        <div class="brand">
          <div class="brand-badge">S</div>
          <div>ShowZio</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# clickable nav buttons
nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 1, 1, 1.2])

with nav1:
    if st.button("About", key="nav_about"):
        go("about")

with nav2:
    if st.button("Customer", key="nav_customer"):
        go("customer")

with nav3:
    if st.button("Vendor", key="nav_vendor"):
        go("vendor")

with nav4:
    if st.button("Contact", key="nav_contact"):
        go("contact")

with nav5:
    st.markdown('<div class="doodle">', unsafe_allow_html=True)
    if st.button("🏠 Home", type="primary", key="nav_home", use_container_width=True):
        go("home")
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="page">', unsafe_allow_html=True)


# ---------------------------
# HOME
# ---------------------------
if st.session_state["route"] == "home":
    st.markdown(
        """
        <div class="hero">
          <div class="hero-grid">
            <div>
              <div class="hero-title">
                Grow your business with<br/>
                <span style="color:#22c55e;">ShowZio</span>
              </div>
              <div class="hero-sub">
                A mobile-friendly vendor catalog platform. Vendors upload items and customers
                order directly on WhatsApp.
              </div>
              <div class="cta-row">
                <span class="cta-primary">Fast Setup</span>
                <span class="cta-ghost">WhatsApp Orders</span>
              </div>
            </div>
            <div>
              <img src="https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?w=1200"
                   style="width:100%; border-radius:20px; border:1px solid #eee;" />
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown('<div class="section-title">Choose your portal</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🛍 Customer")
        st.caption("Browse vendors and view their products.")
        if st.button("Open Customer", use_container_width=True):
            go("customer")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔐 Vendor")
        st.caption("Login, register with OTP, manage items and profile.")
        if st.button("Open Vendor", use_container_width=True):
            go("vendor")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# CUSTOMER PAGE (Vendor list + search)
# ---------------------------
elif st.session_state["route"] == "customer":
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<div class="section-title">🏬 Vendors</div>', unsafe_allow_html=True)
    with col2:
        if st.button("⬅ Back"):
            go("home")

    # Search with icon style
    search_vendor = st.text_input("🔍 Search vendors", placeholder="Type vendor name...")
    vendors = get_vendors()

    if search_vendor:
        vendors = [v for v in vendors if search_vendor.lower() in v["name"].lower()]

    if not vendors:
        st.warning("No vendors found.")
        st.stop()

    cols = st.columns(4)
    for i, v in enumerate(vendors):
        with cols[i % 4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            logo = v.get("logo_url") or "https://via.placeholder.com/300?text=Vendor"
            st.image(logo, use_container_width=True)
            st.write(f"### {v['name']}")
            st.caption((v.get("about") or "")[:80])
            if st.button("View Catalog", key=f"v_{v['id']}", use_container_width=True):
                st.session_state["selected_vendor"] = v["id"]
                go("catalog")
            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# CUSTOMER: catalog view + item search
# ---------------------------
elif st.session_state["route"] == "catalog":
    vendor_id = st.session_state.get("selected_vendor")
    if not vendor_id:
        go("customer")

    data = get_catalog(vendor_id)
    if not data:
        st.error("Vendor not found")
        if st.button("Back"):
            go("customer")
        st.stop()

    vendor = data["vendor"]
    items = data["items"]

    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader(f"🏪 {vendor['name']}")
    with col2:
        if st.button("⬅ Back"):
            go("customer")

    if vendor.get("logo_url"):
        st.image(vendor["logo_url"], width=120)
    if vendor.get("about"):
        st.info(vendor["about"])

    search_item = st.text_input("🔍 Search items", placeholder="Type item name...")
    if search_item:
        items = [it for it in items if search_item.lower() in it["title"].lower()]

    st.divider()
    st.subheader("📦 Items")

    if not items:
        st.warning("No items found.")
        st.stop()

    cols = st.columns(4)
    whatsapp = vendor["whatsapp"]
    for idx, item in enumerate(items):
        with cols[idx % 4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.image(item["image_url"], use_container_width=True)
            st.write("**" + item["title"] + "**")
            st.write("₹", item["price"])
            st.caption("✅ In Stock" if item["in_stock"] else "❌ Out of Stock")
            msg = f"Hi I want to order: {item['title']} (₹{item['price']})"
            link = f"https://wa.me/{whatsapp}?text={msg.replace(' ', '%20')}"
            st.markdown(f"[📲 Order]({link})")
            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# VENDOR PORTAL (table layout + search)
# ---------------------------
elif st.session_state["route"] == "vendor":
    st.markdown('<div class="section-title">🔐 Vendor Portal</div>', unsafe_allow_html=True)

    if st.button("⬅ Back"):
        go("home")

    if "vendor_id" not in st.session_state:
        tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register (OTP)"])

        with tab1:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                r = vendor_login(email, password)
                if r.status_code != 200:
                    st.error(r.text)
                else:
                    data = r.json()
                    st.session_state["vendor_id"] = data["vendor_id"]
                    st.session_state["vendor_name"] = data["name"]
                    st.session_state["vendor_whatsapp"] = data["whatsapp"]
                    st.success("✅ Login success")
                    st.rerun()

        with tab2:
            if "otp_sent" not in st.session_state:
                st.session_state["otp_sent"] = False

            name = st.text_input("Shop Name")
            whatsapp = st.text_input("WhatsApp Number")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pw")
            about = st.text_area("About")

            colA, colB = st.columns(2)
            with colA:
                if st.button("📩 Send OTP", use_container_width=True):
                    r = request_otp(email)
                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        st.session_state["otp_sent"] = True
                        st.success("✅ OTP sent")

            otp = st.text_input("Enter OTP", max_chars=6)

            with colB:
                if st.button("✅ Register", use_container_width=True):
                    payload = {
                        "name": name,
                        "whatsapp": whatsapp,
                        "email": email,
                        "password": password,
                        "about": about,
                        "otp": otp
                    }
                    r = register_vendor(payload)
                    if r.status_code != 200:
                        st.error(r.text)
                    else:
                        st.success("✅ Registered. Please login now.")
                        st.session_state["otp_sent"] = False

        st.stop()

    vendor_id = st.session_state["vendor_id"]
    st.success(f"✅ Welcome {st.session_state['vendor_name']} | Vendor ID: {vendor_id}")

    if st.button("Logout"):
        keep_route = st.session_state["route"]
        st.session_state.clear()
        st.session_state["route"] = keep_route
        st.rerun()

    tab_items, tab_add, tab_profile = st.tabs(["📦 Items (Table)", "➕ Add Item", "🏪 Profile"])

    # Items table
    with tab_items:
        r = api_get(f"/api/catalog/{vendor_id}")
        items = []
        if r.status_code == 200:
            items = r.json()["items"]

        st.text_input("🔍 Search items", key="vendor_item_search", placeholder="Search by item title...")

        search_txt = st.session_state.get("vendor_item_search", "")
        if search_txt:
            items = [it for it in items if search_txt.lower() in it["title"].lower()]

        if not items:
            st.warning("No items found.")
        else:
            for it in items:
                c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
                with c1:
                    st.image(it["image_url"], width=70)
                with c2:
                    st.write(it["title"])
                with c3:
                    st.write(f"₹ {it['price']}")
                with c4:
                    st.write("✅" if it["in_stock"] else "❌")
                with c5:
                    if st.button("📝 Edit", key=f"edit_{it['id']}"):
                        st.session_state["edit_item_id"] = it["id"]
                        st.session_state["edit_item_data"] = it
                        st.rerun()

                st.divider()

            # edit popup section
            if "edit_item_id" in st.session_state:
                it = st.session_state["edit_item_data"]

                st.subheader("📝 Edit Item")
                new_title = st.text_input("Title", value=it["title"])
                new_price = st.number_input("Price", value=float(it["price"]), min_value=1.0, step=1.0)
                new_stock = st.checkbox("In Stock", value=it["in_stock"])

                colx, coly = st.columns(2)
                with colx:
                    if st.button("💾 Save Changes"):
                        payload = {"title": new_title, "price": new_price, "in_stock": new_stock, "image_url": it["image_url"]}
                        ur = update_item(it["id"], payload)
                        if ur.status_code == 200:
                            st.success("Updated ✅")
                            del st.session_state["edit_item_id"]
                            del st.session_state["edit_item_data"]
                            st.rerun()
                        else:
                            st.error(ur.text)

                with coly:
                    if st.button("🗑 Delete Item"):
                        dr = delete_item(it["id"])
                        if dr.status_code == 200:
                            st.success("Deleted ✅")
                            del st.session_state["edit_item_id"]
                            del st.session_state["edit_item_data"]
                            st.rerun()
                        else:
                            st.error(dr.text)

    # Add item
    with tab_add:
        title = st.text_input("Item Title", key="add_title")
        price = st.number_input("Price", min_value=1.0, step=1.0, key="add_price")
        in_stock = st.checkbox("In Stock", value=True, key="add_stock")
        uploaded = st.file_uploader("Upload Item Image", type=["png", "jpg", "jpeg", "webp"])

        if st.button("➕ Add Item", use_container_width=True):
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
            if r.status_code == 200:
                st.success("✅ Item added")
                st.rerun()
            else:
                st.error(r.text)

    # Profile
    with tab_profile:
        about = st.text_area("About")
        logo_file = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg", "webp"])

        if st.button("💾 Save Profile", use_container_width=True):
            logo_url = None
            logo_path = None

            if logo_file:
                lr = upload_logo(logo_file)
                if lr.status_code != 200:
                    st.error(lr.text)
                    st.stop()
                data = lr.json()
                logo_url = data["logo_url"]
                logo_path = data["logo_path"]

            pr = update_profile(vendor_id, about, logo_url, logo_path)
            if pr.status_code == 200:
                st.success("✅ Profile updated")
            else:
                st.error(pr.text)

elif st.session_state["route"] == "about":
    st.markdown('<div class="section-title">📖 About ShowZio</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("""
    **ShowZio** is a vendor catalog platform.
    Vendors upload items + prices, customers browse and place orders directly via WhatsApp.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state["route"] == "contact":
    st.markdown('<div class="section-title">📬 Contact</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("Email: showzio.support@gmail.com")
    st.write("WhatsApp: +91 9xxxxxxxxx")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
