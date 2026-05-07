"""Audio to Reels pipeline page"""
import streamlit as st
import os

from ui.components import (
    render_header, 
    render_status_cards, 
    render_agent_list, 
    render_log,
    render_final_output
)
from ui.pipeline import run_pipeline
from assemble_video import check_ffmpeg, get_video_duration

def render_audio_to_reels():
    """Render the Audio to Reels pipeline page"""
    
    # Check API keys and FFmpeg
    groq_key = os.getenv('GROQ_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    ffmpeg_ok = check_ffmpeg()

    groq_status = groq_key and groq_key != 'your_groq_api_key_here'
    pexels_status = pexels_key and pexels_key != 'your_pexels_api_key_here'

    # Header
    render_header()

    # Main Grid
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
            
            # Audio Upload
            st.markdown('<div class="upload-label">AUDIO SOURCE</div>', unsafe_allow_html=True)
            audio_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], key="audio", label_visibility="collapsed")
            if audio_file:
                st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem; text-align: center; margin-top: 0.5rem;">✓ {audio_file.name}</div>', unsafe_allow_html=True)
            
            # Logo Upload
            st.markdown('<div class="upload-label" style="margin-top: 1.5rem;">BRAND LOGO (OPTIONAL)</div>', unsafe_allow_html=True)
            logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo", label_visibility="collapsed")
            if logo_file:
                st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem; text-align: center; margin-top: 0.5rem;">✓ {logo_file.name}</div>', unsafe_allow_html=True)
            
            # Caption Toggle
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            add_captions = st.checkbox("Dynamic word-level captions", value=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Initiate Button
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            initiate = st.button("⚡ INITIATE PIPELINE", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// AGENT CONSOLE</div>', unsafe_allow_html=True)
            
            # Agent Pipeline
            render_agent_list()
            
            # Final output placeholder
            output_placeholder = st.empty()

            # System Log
            st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
            log_placeholder = st.empty()
            log_placeholder.markdown(render_log("// awaiting pipeline start..."), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Process Pipeline
    if initiate:
        if not audio_file:
            log_placeholder.markdown(render_log("// ERROR: No audio file uploaded", is_error=True), unsafe_allow_html=True)
        elif not groq_status:
            log_placeholder.markdown(render_log("// ERROR: GROQ_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        elif not pexels_status:
            log_placeholder.markdown(render_log("// ERROR: PEXELS_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        elif not ffmpeg_ok:
            log_placeholder.markdown(render_log("// ERROR: FFmpeg not installed", is_error=True), unsafe_allow_html=True)
        else:
            final_output, segment_count = run_pipeline(audio_file, logo_file, add_captions, log_placeholder, output_placeholder)
            
            # Show final output
            video_duration = get_video_duration(final_output)
            
            with output_placeholder.container():
                render_final_output(video_duration, segment_count, final_output)
