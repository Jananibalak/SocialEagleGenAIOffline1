import streamlit as st
import random
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
import time
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP (Change Icon to World Map)
st.set_page_config(
    page_title="World Explorer Adventure", 
    page_icon="🌍", 
    layout="wide"
)

# 2. ARCADE-STYLE UI STYLING
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
    }
    
    /* Title Styling */
    .title-text {
        text-align:center; 
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size:50px; 
        font-weight:bold; 
        color:#ff4757; 
        text-shadow: 2px 2px #ffffff;
        margin-bottom:10px;
    }
    
    /* Question Box */
    .story-box {
        background: #ff7f50; 
        padding:20px; 
        border-radius:25px; 
        font-size:30px; 
        text-align:center; 
        color:white; 
        font-family: 'Comic Sans MS', cursive;
        font-weight:bold; 
        border: 5px solid #ffffff;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Stats Box */
    .stats-container {
        background: #ffffff; 
        padding: 15px; 
        border-radius: 20px; 
        border: 4px solid #70a1ff; 
        text-align: center; 
        font-size: 24px;
        font-weight: bold;
        color: #2f3542;
    }

    /* Map Border (The "Console") */
    .map-frame {
        border: 10px solid #2f3542;
        border-radius: 20px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 3. DATA LOADING
@st.cache_data
def load_world_data():
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    return gpd.read_file(url)

world = load_world_data()

# 4. HELPERS
def get_country_from_click(lat, lon):
    if lon > 180: lon -= 360
    if lon < -180: lon += 360
    point = Point(lon, lat)
    for _, row in world.iterrows():
        if row["geometry"].contains(point):
            return row["ADMIN"]
    return None

def generate_adventure():
    fun_countries = ["Egypt", "Brazil", "France", "Japan", "Australia", "Canada", 
                     "Italy", "Mexico", "Thailand", "India", "Norway", "China"]
    random.shuffle(fun_countries)
    return fun_countries

# 5. SESSION STATE
if "adventure_list" not in st.session_state:
    st.session_state.update({
        "adventure_list": generate_adventure(),
        "current_idx": 0,
        "score": 0,
        "lives": 3,
        "start_time": time.time(),
        "game_over": False,
        "last_click_id": None,
        "paused": False
    })

# 6. REFRESHER
if not st.session_state.paused:
    st_autorefresh(interval=500, key="timer_pulse")

# 7. TIMER LOGIC
TIME_LIMIT = 20
elapsed = time.time() - st.session_state.start_time if not st.session_state.paused else 0
percent_done = min(1.0, elapsed / TIME_LIMIT)

# 8. HEADER & STATS
st.markdown('<p class="title-text">🌍 WORLD EXPLORER ✈️</p>', unsafe_allow_html=True)

stat_col1, stat_col2, stat_col3 = st.columns([2, 2, 2])
with stat_col1:
    st.markdown(f'<div class="stats-container">❤️ LIVES: {st.session_state.lives}</div>', unsafe_allow_html=True)
with stat_col2:
    st.markdown(f'<div class="stats-container">⭐ SCORE: {st.session_state.score}</div>', unsafe_allow_html=True)
with stat_col3:
    # Color-changing progress bar (Blue to Red)
    st.progress(percent_done)
    st.markdown('<p style="text-align:center; font-weight:bold; color:#ff4757;">⏳ HURRY!</p>', unsafe_allow_html=True)

# 9. GAME OVER CHECK
if (percent_done >= 1.0 and not st.session_state.paused) or st.session_state.lives <= 0:
    st.session_state.game_over = True

if st.session_state.game_over:
    st.markdown('<div class="story-box" style="background:#ff4757;">💥 GAME OVER! 💥</div>', unsafe_allow_html=True)
    if st.button("🔄 TRY AGAIN?"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# 10. CURRENT TARGET
target_country = st.session_state.adventure_list[st.session_state.current_idx]
st.markdown(f'<div class="story-box">WHERE IS {target_country.upper()}? 🤔</div>', unsafe_allow_html=True)

# 11. THE MAP (Inside a "Console" Border)
m = folium.Map(
    location=[20, 0], zoom_start=2, 
    tiles="CartoDB positron", zoom_control=False,
    min_zoom=2, max_bounds=True,
    min_lat=-85, max_lat=85, min_lon=-180, max_lon=180
)

# Wrapping map in a div for style
st.markdown('<div class="map-frame">', unsafe_allow_html=True)
map_key = f"map_q_{st.session_state.current_idx}_{st.session_state.score}"
map_data = st_folium(m, width="100%", height=450, key=map_key)
st.markdown('</div>', unsafe_allow_html=True)

# 12. CLICK HANDLING
if map_data and map_data.get("last_clicked"):
    click_id = f"{map_data['last_clicked']['lat']}_{map_data['last_clicked']['lng']}"
    
    if click_id != st.session_state.last_click_id:
        st.session_state.last_click_id = click_id
        clicked_country = get_country_from_click(map_data['last_clicked']['lat'], map_data['last_clicked']['lng'])
        
        if clicked_country == target_country:
            st.session_state.score += 10
            st.session_state.current_idx = (st.session_state.current_idx + 1) % len(st.session_state.adventure_list)
            
            st.session_state.paused = True
            st.balloons()
            st.success(f"🌟 AMAZING! YOU FOUND {target_country.upper()}!")
            
            time.sleep(2)
            
            st.session_state.start_time = time.time()
            st.session_state.last_click_id = None
            st.session_state.paused = False
            st.rerun()
        else:
            st.session_state.lives -= 1
            st.toast(f"📍 Oops! That's {clicked_country or 'the ocean'}!", icon="😅")
            time.sleep(0.5)
            st.rerun()