import streamlit as st
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import UI modules
from ui.styles import CYBERPUNK_CSS
from ui.dashboard_styles import DASHBOARD_CSS
from ui.dashboard import render_dashboard, render_back_button
from ui.audio_to_reels import render_audio_to_reels
from ui.topic_to_reels import render_topic_to_reels
from ui.topic_to_speech import render_topic_to_speech

# Page config
st.set_page_config(
    page_title="ChitraAI - Agentic Video Synthesis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply base styles
st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)
st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

# Initialize session state for page routing
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Routing logic
if st.session_state.current_page == 'dashboard':
    # Render landing dashboard
    render_dashboard()

elif st.session_state.current_page == 'audio_to_reels':
    # Render back button
    st.markdown('<div class="back-button" onclick="window.location.reload()">', unsafe_allow_html=True)
    render_back_button()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render Audio to Reels pipeline
    render_audio_to_reels()

elif st.session_state.current_page == 'topic_to_reels':
    # Render back button
    render_back_button()
    
    # Render Topic to Reels pipeline
    render_topic_to_reels()

elif st.session_state.current_page == 'topic_to_speech':
    # Render back button
    render_back_button()
    
    # Render Topic to Speech pipeline
    render_topic_to_speech()

else:
    # Fallback to dashboard
    st.session_state.current_page = 'dashboard'
    st.rerun()
