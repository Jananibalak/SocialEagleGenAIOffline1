"""
BudgetBuddy Streamlit Frontend
A beautiful frontend that connects to the Flask REST API
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json

# Page config
st.set_page_config(
    page_title="💰 BudgetBuddy - Smart Bill Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:5000")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'bills_uploaded' not in st.session_state:
    st.session_state.bills_uploaded = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None


def create_session(api_key):
    """Create a new session with the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/session/create",
            json={"api_key": api_key},
            timeout=10
        )
        if response.status_code == 201:
            data = response.json()
            st.session_state.session_id = data['session_id']
            return True, "Session created successfully!"
        else:
            return False, f"Error: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to API. Make sure the Flask API is running!"
    except Exception as e:
        return False, f"Error: {str(e)}"


def upload_bills(files):
    """Upload bills to the API"""
    try:
        files_data = [('files', (file.name, file, file.type)) for file in files]
        data = {'session_id': st.session_state.session_id}
        
        response = requests.post(
            f"{API_BASE_URL}/api/upload",
            data=data,
            files=files_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.bills_uploaded = True
            return True, result
        else:
            return False, response.json().get('error', 'Upload failed')
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_analysis():
    """Get financial analysis from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/analysis/{st.session_state.session_id}",
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('error', 'Analysis failed')
    except Exception as e:
        return False, f"Error: {str(e)}"


def search_bills(query, top_k=5):
    """Search bills using semantic search"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            json={
                "session_id": st.session_state.session_id,
                "query": query,
                "top_k": top_k
            },
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('error', 'Search failed')
    except Exception as e:
        return False, f"Error: {str(e)}"


def chat_with_ai(message):
    """Chat with AI about bills"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={
                "session_id": st.session_state.session_id,
                "message": message
            },
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('error', 'Chat failed')
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_bills():
    """Get all processed bills"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/bills/{st.session_state.session_id}",
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('error', 'Failed to fetch bills')
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    # Header
    st.markdown('<h1 class="main-header">💰 BudgetBuddy</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your AI-powered financial advisor - Get insights on your spending! 🤗</p>', unsafe_allow_html=True)
    
    # Check API health
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ Cannot connect to the API! Make sure the Flask API is running on " + API_BASE_URL)
        st.info("💡 Start the API with: `python app.py` in the bill_analyzer_api folder")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API URL configuration
        with st.expander("🔧 API Settings", expanded=False):
            custom_url = st.text_input("API URL", value=API_BASE_URL)
            if custom_url != API_BASE_URL:
                st.session_state.api_base_url = custom_url
                st.rerun()
        
        # API Key input
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get your key from openrouter.ai"
        )
        
        # Create session button
        if api_key and not st.session_state.session_id:
            if st.button("🚀 Create Session", use_container_width=True):
                with st.spinner("Creating session..."):
                    success, message = create_session(api_key)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        # Show session status
        if st.session_state.session_id:
            st.success(f"✅ Session Active")
            st.caption(f"ID: {st.session_state.session_id[:8]}...")
            
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.bills_uploaded = False
                st.session_state.chat_history = []
                st.session_state.analysis_data = None
                st.rerun()
        
        st.markdown("---")
        
        # File upload section
        if st.session_state.session_id:
            st.header("📁 Upload Bills")
            uploaded_files = st.file_uploader(
                "Choose bill files",
                type=['pdf', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Upload PDFs or images of your bills"
            )
            
            if uploaded_files:
                st.info(f"📄 {len(uploaded_files)} file(s) selected")
                
                if st.button("🔍 Process Bills", use_container_width=True):
                    with st.spinner(f"Processing {len(uploaded_files)} bill(s)..."):
                        success, result = upload_bills(uploaded_files)
                        if success:
                            st.success(f"✅ Processed {result['processed_count']} bills!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.info("📸 For best OCR results:\n- Use good lighting\n- Keep text readable\n- Avoid shadows")
    
    # Main content
    if not st.session_state.session_id:
        # Welcome screen
        st.markdown("""
        ### 👋 Welcome to BudgetBuddy!
        
        Your AI-powered financial assistant that helps you understand and optimize your spending.
        
        #### 🚀 How to get started:
        1. **Get your API key** from [OpenRouter](https://openrouter.ai/keys)
        2. **Enter it** in the sidebar
        3. **Click "Create Session"**
        4. **Upload your bills** (PDFs or images)
        5. **Get personalized insights!** 🎉
        
        #### ✨ What you'll get:
        - 📊 Beautiful spending visualizations
        - 🤖 AI-powered financial advice
        - 💬 Chat with your financial data
        - 📈 Category-wise breakdowns
        - 💡 Personalized saving tips
        """)
        
    elif not st.session_state.bills_uploaded:
        # Waiting for bills
        st.info("👈 Upload your bills using the sidebar to get started!")
        
        st.markdown("""
        ### 📄 Supported File Types:
        - **PDF documents** - Digital or scanned bills
        - **Images** - PNG, JPG, JPEG (we'll use OCR to read them)
        
        ### 💰 What we can analyze:
        - Grocery receipts
        - Restaurant bills
        - Utility bills
        - Online shopping receipts
        - And more!
        """)
        
    else:
        # Show analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "🔥 AI Insights",
            "💬 Chat",
            "📈 Bill Details"
        ])
        
        with tab1:
            display_overview()
        
        with tab2:
            display_insights()
        
        with tab3:
            display_chat()
        
        with tab4:
            display_bills()


def display_overview():
    """Display financial overview"""
    st.subheader("📊 Financial Overview")
    
    with st.spinner("Loading analysis..."):
        success, data = get_analysis()
        
        if not success:
            st.error(f"Failed to load analysis: {data}")
            return
        
        st.session_state.analysis_data = data
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💸 Total Spent",
            f"${data['total_spent']:,.2f}",
            help="Total amount across all bills"
        )
    
    with col2:
        st.metric(
            "📄 Total Bills",
            data['total_bills'],
            help="Number of bills processed"
        )
    
    with col3:
        st.metric(
            "📊 Average Bill",
            f"${data['average_bill']:,.2f}",
            help="Average amount per bill"
        )
    
    # Category breakdown
    if data.get('category_breakdown'):
        st.markdown("### 💰 Spending by Category")
        
        col1, col2 = st.columns(2)
        
        categories = data['category_breakdown']
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title="Category Distribution",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=list(categories.keys()),
                y=list(categories.values()),
                title="Amount by Category",
                labels={'x': 'Category', 'y': 'Amount ($)'},
                color=list(categories.values()),
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)


def display_insights():
    """Display AI-generated insights"""
    st.subheader("🔥 Your Personalized Insights")
    
    if not st.session_state.analysis_data:
        with st.spinner("Loading analysis..."):
            success, data = get_analysis()
            if success:
                st.session_state.analysis_data = data
            else:
                st.error("Failed to load insights")
                return
    
    insights = st.session_state.analysis_data.get('insights', {})
    
    # Observations
    if insights.get('observations'):
        st.markdown(f'<div class="insight-box"><h3>💡 What I Noticed</h3><p>{insights["observations"]}</p></div>', unsafe_allow_html=True)
    
    # Warnings
    if insights.get('warnings'):
        st.markdown(f'<div class="warning-box"><h3>⚠️ Heads Up!</h3><p>{insights["warnings"]}</p></div>', unsafe_allow_html=True)
    
    # Recommendations
    if insights.get('recommendations'):
        st.markdown(f'<div class="success-box"><h3>✨ My Advice for You</h3><p>{insights["recommendations"]}</p></div>', unsafe_allow_html=True)


def display_chat():
    """Display chat interface"""
    st.subheader("💬 Chat with BudgetBuddy")
    st.markdown("Ask me anything about your bills! I'm here to help! 😊")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(message['user'])
        with st.chat_message("assistant"):
            st.markdown(message['assistant'])
    
    # Chat input
    if prompt := st.chat_input("Ask about your spending..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                success, response = chat_with_ai(prompt)
                
                if success:
                    ai_response = response['ai_response']
                    st.markdown(ai_response)
                    
                    # Store in chat history
                    st.session_state.chat_history.append({
                        'user': prompt,
                        'assistant': ai_response
                    })
                    
                    # Show sources if available
                    if response.get('sources'):
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(response['sources'], 1):
                                st.caption(f"**Source {i}:**")
                                st.text(source['content'])
                else:
                    st.error(f"Error: {response}")


def display_bills():
    """Display detailed bill breakdown"""
    st.subheader("📋 Bill Details")
    
    with st.spinner("Loading bills..."):
        success, data = get_all_bills()
        
        if not success:
            st.error(f"Failed to load bills: {data}")
            return
        
        bills = data.get('bills', [])
    
    if not bills:
        st.info("No bills uploaded yet!")
        return
    
    # Create DataFrame
    df_data = []
    for bill in bills:
        df_data.append({
            'Filename': bill.get('filename', 'N/A'),
            'Merchant': bill.get('merchant', 'Unknown'),
            'Amount': f"${bill.get('amount', 0):.2f}",
            'Date': bill.get('date', 'N/A'),
            'Category': bill.get('category', 'Other')
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download as CSV",
        csv,
        "bills_analysis.csv",
        "text/csv",
        key='download-csv'
    )
    
    # Bill details
    st.markdown("### 🔍 Detailed View")
    
    for i, bill in enumerate(bills, 1):
        with st.expander(f"📄 {bill.get('filename', 'Bill')} - ${bill.get('amount', 0):.2f}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Merchant:**", bill.get('merchant', 'Unknown'))
                st.write("**Amount:**", f"${bill.get('amount', 0):.2f}")
                st.write("**Date:**", bill.get('date', 'N/A'))
            
            with col2:
                st.write("**Category:**", bill.get('category', 'Other'))
                items = bill.get('items', [])
                if items:
                    st.write(f"**Items:** {len(items)}")
            
            # Show items if available
            if items:
                st.markdown("**Line Items:**")
                for item in items[:5]:  # Show first 5 items
                    st.caption(f"• {item.get('name', 'Item')}: ${item.get('price', 0):.2f}")


if __name__ == "__main__":
    main()
