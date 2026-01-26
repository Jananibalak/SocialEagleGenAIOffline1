import streamlit as st
import requests

API_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="Customer", layout="wide")

st.title("🛍 Customer Catalog")
st.caption("Browse vendors and their items")


def get_vendors():
    r = requests.get(f"{API_BASE}/api/vendors")
    if r.status_code != 200:
        st.error(r.text)
        return []
    return r.json().get("vendors", [])


def get_catalog(vendor_id: int):
    r = requests.get(f"{API_BASE}/api/catalog/{vendor_id}")
    if r.status_code != 200:
        st.error(r.text)
        return None
    return r.json()


# Route-like behavior using query params
vendor_id = st.query_params.get("vendor_id", None)

if vendor_id:
    vendor_id = int(vendor_id)
    data = get_catalog(vendor_id)

    if not data:
        st.stop()

    vendor = data["vendor"]
    items = data["items"]

    st.subheader(f"🏪 {vendor['name']}")
    if vendor.get("logo_url"):
        st.image(vendor["logo_url"], width=140)
    if vendor.get("about"):
        st.info(vendor["about"])

    whatsapp_link = f"https://wa.me/{vendor['whatsapp']}?text=Hi%20I%20want%20to%20order%20items%20from%20your%20catalog"
    st.markdown(f"✅ **Order via WhatsApp:** [{whatsapp_link}]({whatsapp_link})")

    st.divider()
    st.subheader("📦 Items")

    if not items:
        st.warning("No items added yet.")
        st.stop()

    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            st.image(item["image_url"], use_container_width=True)
            st.write("###", item["title"])
            st.write("₹", item["price"])
            st.write("✅ In Stock" if item["in_stock"] else "❌ Out of Stock")

            order_msg = f"Hi I want to order: {item['title']} (₹{item['price']})"
            item_link = f"https://wa.me/{vendor['whatsapp']}?text={order_msg.replace(' ', '%20')}"
            st.markdown(f"[📲 Order This Item]({item_link})")

    st.divider()
    if st.button("⬅️ Back to vendors"):
        st.query_params.clear()
        st.rerun()

else:
    st.subheader("🏬 Vendors")
    vendors = get_vendors()

    if not vendors:
        st.warning("No vendors available.")
        st.stop()

    cols = st.columns(3)
    for idx, v in enumerate(vendors):
        with cols[idx % 3]:
            logo = v.get("logo_url") or "https://via.placeholder.com/300?text=Vendor"
            st.image(logo, use_container_width=True)
            st.write("###", v["name"])
            st.caption(v.get("about") or "")

            if st.button("View Catalog", key=f"view_{v['id']}"):
                st.query_params["vendor_id"] = str(v["id"])
                st.rerun()
