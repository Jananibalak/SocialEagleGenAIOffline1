import streamlit as st
import random
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="World Explorer Adventure", layout="wide")

# ---------------- SIMPLE KID UI ----------------
st.markdown("""
<style>
.main {background-color: #f8edff;}
.title {text-align:center;font-size:40px;font-weight:bold;color:#6a4c93;}
.story-box {background:#cdb4db;padding:20px;border-radius:15px;font-size:22px;text-align:center;color:#240046;}
.lives {text-align:center;font-size:28px;}
.timer {text-align:center;font-size:24px;color:#d00000;}
.stButton>button {border-radius:10px;padding:8px 20px;font-size:16px;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MAP DATA ----------------
@st.cache_data
def load_world():
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    return gpd.read_file(url)

world = load_world()

def get_country_from_click(lat, lon):
    point = Point(lon, lat)
    for _, row in world.iterrows():
        if row["geometry"].contains(point):
            return row["ADMIN"]
    return None

def get_country_shape(country_name):
    row = world[world["ADMIN"] == country_name]
    if not row.empty:
        return row.iloc[0]["geometry"]
    return None

# ---------------- GAME DATA ----------------
fun_countries = ["Egypt","Brazil","France","Japan","Australia",
                 "Canada","South Africa","Italy","Mexico","Thailand"]

def generate_adventure():
    return [{"text": f"✈️ Travel to {c}!", "country": c}
            for c in random.sample(fun_countries, 4)]

# ---------------- SESSION STATE ----------------
defaults = {
    "lives": 3,
    "step": 0,
    "story_steps": generate_adventure(),
    "highlight_country": None,
    "game_over": False,
    "question_start_time": time.time()
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- HEADER ----------------
st.markdown('<div class="title">🌍 World Explorer Adventure ✈️</div>', unsafe_allow_html=True)
st.markdown(f'<div class="lives">{"❤️" * st.session_state.lives}</div>', unsafe_allow_html=True)

# ---------------- AUTO REFRESH TIMER ----------------
st_autorefresh(interval=1000, key="timer_refresh")

# ---------------- TIMER ----------------
TIME_LIMIT = 10
elapsed = int(time.time() - st.session_state.question_start_time)
remaining = max(0, TIME_LIMIT - elapsed)
st.markdown(f'<div class="timer">⏳ Time Left: {remaining}s</div>', unsafe_allow_html=True)

if remaining <= 0 and not st.session_state.game_over:
    st.session_state.lives -= 1
    st.session_state.highlight_country = st.session_state.story_steps[st.session_state.step]["country"]
    st.warning("⏰ Time's up!")
    time.sleep(1)

    st.session_state.step += 1
    if st.session_state.step >= len(st.session_state.story_steps):
        st.session_state.story_steps = generate_adventure()
        st.session_state.step = 0

    st.session_state.question_start_time = time.time()
    st.rerun()

# ---------------- GAME OVER ----------------
if st.session_state.lives <= 0:
    st.session_state.game_over = True

if st.session_state.game_over:
    st.error("💀 Game Over!")
    if st.button("🔁 Replay Adventure"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()
    st.stop()

# ---------------- CURRENT QUESTION ----------------
current_step = st.session_state.story_steps[st.session_state.step]
target_country = current_step["country"]
st.markdown(f'<div class="story-box">{current_step["text"]}</div>', unsafe_allow_html=True)

# ---------------- CENTERED MAP ----------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    m = folium.Map(location=[20,0], zoom_start=2, tiles="CartoDB positron")

    if st.session_state.highlight_country:
        shape = get_country_shape(st.session_state.highlight_country)
        if shape is not None:
            folium.GeoJson(
                shape,
                style_function=lambda x: {
                    "fillColor":"#ffafcc",
                    "color":"red",
                    "weight":3,
                    "fillOpacity":0.5,
                }).add_to(m)

    map_data = st_folium(m, width=700, height=500, key=f"map_{st.session_state.step}")

# ---------------- CLICK HANDLING ----------------
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    clicked_country = get_country_from_click(lat, lon)

    if clicked_country == target_country:
        st.balloons()
        st.success("🎉 Correct!")
        time.sleep(1)
        st.session_state.highlight_country = None
    else:
        st.session_state.lives -= 1
        st.session_state.highlight_country = target_country
        st.error(f"❌ That was {clicked_country or 'the ocean'}")
        time.sleep(1)

    st.session_state.step += 1
    if st.session_state.step >= len(st.session_state.story_steps):
        st.session_state.story_steps = generate_adventure()
        st.session_state.step = 0

    st.session_state.question_start_time = time.time()
    st.rerun()
