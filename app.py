import streamlit as st
import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import existing modules
from main import transcribe_audio, create_video_map, save_video_map
from download_videos import (
    create_assets_folder, 
    find_and_download_video,
    PEXELS_API_KEY
)
from assemble_video import (
    check_ffmpeg,
    create_temp_folder,
    get_video_duration,
    cleanup_temp_files
)
from add_captions import (
    create_word_segments,
    create_dynamic_highlight_subtitles,
    burn_subtitles_and_logo
)

# Page config
st.set_page_config(
    page_title="ChitraAI - AI Video Pipeline",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check API keys and FFmpeg
groq_key = os.getenv('GROQ_API_KEY')
pexels_key = os.getenv('PEXELS_API_KEY')
ffmpeg_ok = check_ffmpeg()

groq_status = groq_key and groq_key != 'your_groq_api_key_here'
pexels_status = pexels_key and pexels_key != 'your_pexels_api_key_here'

# Custom CSS - Cyberpunk Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stApp {
        background: #0A0A0A;
    }
    
    .neon-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B35 0%, #FF0080 50%, #8B00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
        margin-bottom: 0.5rem;
    }
    
    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
    }
    .status-bar .neon-title { margin: 0; line-height: 1.1; }
    
    .system-status {
        color: #FF6B35;
        font-size: 0.9rem;
        text-align: right;
        line-height: 1.2;
    }
    
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #FF6B35;
        box-shadow: 0 0 10px #FF6B35;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-bottom: 2.5rem;
    }
    
    .status-card {
        background: rgba(255, 107, 53, 0.05);
        border: 1px solid;
        padding: 1rem;
        border-radius: 4px;
    }
    
    .status-card.connected {
        border-image: linear-gradient(135deg, #FF6B35, #FF0080) 1;
    }
    
    .status-card.disconnected {
        border: 1px solid #333;
        opacity: 0.5;
    }
    
    .card-title {
        color: #888;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    .card-status {
        color: #FF6B35;
        font-size: 1rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    .card-status.disconnected {
        color: #555;
        text-shadow: none;
    }
    
    /* Native Streamlit bordered containers for left/right panels (top level only) */
    div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #333;
        border-right: 1px solid rgba(255, 107, 53, 0.35);
        box-shadow: 1px 0 0 rgba(255, 107, 53, 0.06), 10px 0 28px rgba(255, 107, 53, 0.06);
        padding: 1.05rem 1rem 1.05rem;
    }
    div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #333;
        border-left: 1px solid rgba(255, 107, 53, 0.35);
        box-shadow: -1px 0 0 rgba(255, 107, 53, 0.06), -10px 0 28px rgba(255, 107, 53, 0.06);
        padding: 1.05rem 1rem 1.05rem;
    }
    
    .panel-title {
        color: #FF6B35;
        font-size: 0.85rem;
        margin-bottom: 1.25rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    
    .upload-label {
        color: #888;
        font-size: 0.75rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Streamlit file uploader -> designed drop zone */
    div[data-testid="column"]:first-child [data-testid="stFileUploader"] {
        margin-bottom: 1.25rem;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(255, 255, 255, 0.16) !important;
        background: rgba(0, 0, 0, 0.35) !important;
        border-radius: 6px !important;
        padding: 0 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        box-shadow: none;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(255, 107, 53, 0.65) !important;
        background: rgba(255, 107, 53, 0.05) !important;
        box-shadow: 0 0 18px rgba(255, 107, 53, 0.09);
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] > div {
        display: grid !important;
        place-items: center !important;
        min-height: 148px;
        padding: 22px 18px !important;
    }
    /* Hide Streamlit's default helper text; we provide pixel-perfect labels */
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] small,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] span,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] p,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] button {
        display: none !important;
    }
    /* Two uploaders in left panel: style their "designed" content via ::before */
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(1) [data-testid="stFileUploaderDropzone"]::before {
        content: "↑\A\A AUDIO SOURCE\A MP3 • WAV • M4A";
        white-space: pre;
        text-align: center;
        color: rgba(255, 255, 255, 0.88);
        font-size: 0.78rem;
        letter-spacing: 1px;
        line-height: 1.35;
        text-shadow: 0 0 12px rgba(255, 107, 53, 0.18);
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(1) [data-testid="stFileUploaderDropzone"]::before {
        display: block;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(1) [data-testid="stFileUploaderDropzone"] > div {
        min-height: 172px;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(2) [data-testid="stFileUploaderDropzone"]::before {
        content: "◇\A\A BRAND LOGO\A OPTIONAL • PNG • JPG";
        white-space: pre;
        text-align: center;
        color: rgba(255, 255, 255, 0.82);
        font-size: 0.78rem;
        letter-spacing: 1px;
        line-height: 1.35;
        text-shadow: 0 0 12px rgba(255, 107, 53, 0.14);
    }
    
    .toggle-container {
        padding: 1.05rem 1.1rem;
        background: rgba(255, 107, 53, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.14);
        margin: 1.1rem 0 1.25rem;
        text-align: left;
        border-radius: 6px;
        box-shadow: none;
        cursor: pointer;
    }
    .toggle-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.6rem;
    }
    .toggle-title .label {
        color: rgba(255, 255, 255, 0.86);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 1.5px;
    }
    .toggle-title .hint {
        color: rgba(255, 107, 53, 0.85);
        font-size: 0.7rem;
        letter-spacing: 1px;
        border: 1px solid rgba(255, 107, 53, 0.55);
        padding: 0.2rem 0.5rem;
    }
    .toggle-container:hover {
        border-color: rgba(255, 107, 53, 0.55);
        box-shadow: 0 0 0 1px rgba(255, 107, 53, 0.2), 0 0 22px rgba(255, 107, 53, 0.09);
    }
    /* Tighten checkbox area so it feels like a module, not a raw control */
    .toggle-container [data-testid="stCheckbox"] {
        margin-top: -0.05rem;
        display: flex;
        justify-content: flex-start;
    }
    .toggle-container [data-testid="stCheckbox"] label {
        width: auto;
        padding: 0;
        display: flex !important;
        align-items: center !important;
        gap: 0.45rem;
        line-height: 1;
        color: rgba(255, 255, 255, 0.88) !important;
        font-size: 0.84rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .toggle-container [data-testid="stCheckbox"] input {
        margin-top: 0 !important;
    }
    
    .agent-list {
        position: relative;
        padding-left: 0.25rem;
        margin-top: 0.25rem;
    }
    /* One continuous vertical connector line */
    .agent-list::before {
        content: '';
        position: absolute;
        left: 1.05rem;
        top: 0.55rem;
        bottom: 0.55rem;
        width: 2px;
        background: linear-gradient(180deg, rgba(255, 107, 53, 0.55) 0%, rgba(255, 0, 128, 0.55) 100%);
        opacity: 0.28;
        filter: drop-shadow(0 0 6px rgba(255, 107, 53, 0.25));
        border-radius: 2px;
    }

    .agent-item {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1.15rem;
        position: relative;
        align-items: center;
    }
    /* Remove per-item line segments; we use a single continuous line now */
    .agent-item::after { display: none; }
    
    .agent-number {
        color: #FF6B35;
        font-size: 1.25rem;
        font-weight: 700;
        min-width: 2rem;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
        line-height: 1.0;
        padding-top: 0.1rem;
    }
    
    .agent-content {
        flex: 1;
    }
    
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    
    .agent-name {
        color: #FFF;
        font-size: 0.98rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .agent-desc {
        color: #666;
        font-size: 0.74rem;
        line-height: 1.55;
    }
    
    .agent-status {
        color: #FF6B35;
        font-size: 0.7rem;
        padding: 0.25rem 0.75rem;
        border: 1px solid #FF6B35;
        text-shadow: 0 0 5px rgba(255, 107, 53, 0.5);
        white-space: nowrap;
        border-radius: 999px;
        letter-spacing: 1px;
    }
    
    .agent-item.final-output {
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        padding-top: 1.1rem;
        margin-top: 0.9rem;
    }
    
    .final-output-body {
        margin-top: 0.85rem;
        padding: 1rem;
        border: 1px solid rgba(255, 107, 53, 0.35);
        background: rgba(255, 107, 53, 0.06);
        border-radius: 6px;
        box-shadow: inset 0 0 0 1px rgba(255, 107, 53, 0.08);
    }
    
    .agent-status.running {
        animation: glow 1.5s infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(255, 107, 53, 0.5); }
        50% { box-shadow: 0 0 15px rgba(255, 107, 53, 0.8); }
    }
    
    .system-log {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        padding: 1.05rem 1.15rem;
        border-radius: 6px;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
    }
    
    .log-title {
        color: #FF6B35;
        font-size: 0.75rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    .log-title.terminal {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.75rem;
    }
    .term-dots {
        display: inline-flex;
        gap: 6px;
        transform: translateY(-1px);
    }
    .term-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.18);
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.12);
    }
    
    .log-content {
        color: rgba(255, 107, 53, 0.6);
        font-size: 0.8rem;
        line-height: 1.8;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.08);
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B35 0%, #FF0080 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3) !important;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 0 30px rgba(255, 107, 53, 0.6) !important;
    }
    
    .stCheckbox label {
        color: #888 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="status-bar">
    <div class="neon-title">⚡ CHITRA AI PIPELINE</div>
    <div class="system-status">
        <div><span class="status-dot"></span>STATUS: ONLINE</div>
        <div style="margin-top: 0.15rem;">AGENTS: 04</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status Cards
st.markdown(f"""
<div class="status-cards">
    <div class="status-card {'connected' if groq_status else 'disconnected'}">
        <div class="card-title">GROQ API</div>
        <div class="card-status {'connected' if groq_status else 'disconnected'}">
            {'● CONNECTED' if groq_status else '○ DISCONNECTED'}
        </div>
    </div>
    <div class="status-card {'connected' if pexels_status else 'disconnected'}">
        <div class="card-title">PEXELS</div>
        <div class="card-status {'connected' if pexels_status else 'disconnected'}">
            {'● CONNECTED' if pexels_status else '○ DISCONNECTED'}
        </div>
    </div>
    <div class="status-card {'connected' if ffmpeg_ok else 'disconnected'}">
        <div class="card-title">FFMPEG</div>
        <div class="card-status {'connected' if ffmpeg_ok else 'disconnected'}">
            {'● CONNECTED' if ffmpeg_ok else '○ DISCONNECTED'}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Grid
col_left, col_right = st.columns([1, 1.6])

with col_left:
    with st.container(border=True):
        st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
        
        # Audio Upload
        audio_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], key="audio", label_visibility="collapsed")
        if audio_file:
            st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem; text-align: center;">✓ {audio_file.name}</div>', unsafe_allow_html=True)
        
        # Caption Toggle
        st.markdown("""
        <div class="toggle-title">
            <div class="label">DYNAMIC CAPTIONS</div>
        </div>
        <div style="color: rgba(255,255,255,0.52); font-size: 0.72rem; margin-bottom: 0.55rem; letter-spacing: 0.5px;">
            Word-level highlight subtitles
        </div>
        """, unsafe_allow_html=True)
        add_captions = st.checkbox("Dynamic word-level captions", value=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Logo Upload
        logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo", label_visibility="collapsed")
        if logo_file:
            st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem; text-align: center;">✓ {logo_file.name}</div>', unsafe_allow_html=True)
        
        # Initiate Button
        st.markdown('<div style="margin-top: 1.2rem;">', unsafe_allow_html=True)
        initiate = st.button("⚡ INITIATE PIPELINE", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    with st.container(border=True):
        st.markdown('<div class="panel-title">// AGENT CONSOLE</div>', unsafe_allow_html=True)
        
        # Agent Pipeline
        agent_container = st.container()
        with agent_container:
            st.markdown("""
            <div class="agent-list">
            <div class="agent-item">
                <div class="agent-number">01</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SCRIPT AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Transcribe audio via Groq Whisper<br/>→ Generate timestamped video map with AI</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">02</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">ASSET AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Extract visual keywords from segments<br/>→ Download portrait videos from Pexels API</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">03</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">ASSEMBLY AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Trim and sync video clips to timestamps<br/>→ Render 9:16 vertical format with FFmpeg</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">04</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SUBTITLE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate word-level caption timing<br/>→ Burn subtitles and logo overlay</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Final output placeholder (becomes AGENT 05 only after completion)
        output_placeholder = st.empty()

        # System Log (inside right panel, below agent list)
        st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
        log_placeholder = st.empty()
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
            <div class="log-content">// awaiting pipeline start...</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Process Pipeline
if initiate:
    if not audio_file:
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: No audio file uploaded</div>
        </div>
        """, unsafe_allow_html=True)
    elif not groq_status:
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: GROQ_API_KEY not configured</div>
        </div>
        """, unsafe_allow_html=True)
    elif not pexels_status:
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: PEXELS_API_KEY not configured</div>
        </div>
        """, unsafe_allow_html=True)
    elif not ffmpeg_ok:
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: FFmpeg not installed</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Save uploaded audio
        audio_path = f"temp_audio_{int(time.time())}.{audio_file.name.split('.')[-1]}"
        with open(audio_path, 'wb') as f:
            f.write(audio_file.read())
        
        # Save logo if provided
        logo_path = None
        if logo_file:
            logo_path = "logo.png"
            with open(logo_path, 'wb') as f:
                f.write(logo_file.read())
        
        try:
            # Step 1: Transcription
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 01] Transcribing audio...</div>
            </div>
            """, unsafe_allow_html=True)
            
            transcript = transcribe_audio(audio_path)
            video_map = create_video_map(transcript)
            save_video_map(video_map)
            
            log_placeholder.markdown(f"""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 01] ✓ Transcribed {len(video_map)} segments</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 2: Download videos
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 02] Downloading videos from Pexels...</div>
            </div>
            """, unsafe_allow_html=True)
            
            create_assets_folder()
            successful = 0
            
            for i, segment in enumerate(video_map, 1):
                if find_and_download_video(segment, i):
                    successful += 1
            
            log_placeholder.markdown(f"""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 02] ✓ Downloaded {successful}/{len(video_map)} clips</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 3: Assemble video
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 03] Assembling video...</div>
            </div>
            """, unsafe_allow_html=True)
            
            create_temp_folder()
            
            # Prepare inputs and filter complex
            inputs = []
            filter_parts = []
            
            for i, segment in enumerate(video_map):
                clip_path = os.path.join('assets', f"clip_{i+1}.mp4")
                duration = segment['end_time'] - segment['start_time']
                
                # Check if clip exists, create fallback if not
                if not os.path.exists(clip_path):
                    clip_path = os.path.join('temp', f"fallback_{i+1}.mp4")
                    cmd = [
                        'ffmpeg', '-f', 'lavfi',
                        '-i', f'color=c=black:s=1080x1920:d={duration}:r=30',
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-y', clip_path
                    ]
                    subprocess.run(cmd, capture_output=True)
                
                inputs.extend(['-i', clip_path])
                
                filter_parts.append(
                    f"[{i}:v]trim=start=0:end={duration},setpts=PTS-STARTPTS,"
                    f"fps=30,format=yuv420p,scale=1080:1920:force_original_aspect_ratio=increase,"
                    f"crop=1080:1920,setsar=1[v{i}]"
                )
            
            concat_inputs = ''.join([f"[v{i}]" for i in range(len(video_map))])
            filter_complex = ';'.join(filter_parts) + f";{concat_inputs}concat=n={len(video_map)}:v=1:a=0[outv]"
            
            audio_duration = get_video_duration(audio_path)
            
            draft_output = 'draft_video.mp4'
            cmd = [
                'ffmpeg', *inputs, '-i', audio_path,
                '-filter_complex', filter_complex,
                '-map', '[outv]', '-map', f'{len(video_map)}:a',
                '-t', str(audio_duration),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-c:a', 'aac', '-b:a', '192k', '-r', '30',
                '-y', draft_output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception("Video assembly failed")
            
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 03] ✓ Video assembled</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 4: Add captions (if checked)
            final_output = draft_output
            
            if add_captions:
                log_placeholder.markdown("""
                <div class="system-log">
                    <div class="log-title">// SYSTEM LOG</div>
                    <div class="log-content" style="color: #FF6B35;">// [AGENT 04] Adding dynamic captions...</div>
                </div>
                """, unsafe_allow_html=True)
                
                word_segments = create_word_segments(video_map)
                subtitle_file = create_dynamic_highlight_subtitles(word_segments)
                
                final_output = 'final_output.mp4'
                logo_for_caption = logo_path if logo_path and os.path.exists(logo_path) else 'logo.png'
                burn_subtitles_and_logo(draft_output, subtitle_file, logo_for_caption, final_output)
                
                log_placeholder.markdown("""
                <div class="system-log">
                    <div class="log-title">// SYSTEM LOG</div>
                    <div class="log-content" style="color: #FF6B35;">// [AGENT 04] ✓ Captions added</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Success
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// ✓ PIPELINE COMPLETE</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show final output section
            video_duration = get_video_duration(final_output)
            
            with output_placeholder.container():
                st.markdown(f"""
                <div class="agent-list">
                    <div class="agent-item final-output">
                        <div class="agent-number">05</div>
                        <div class="agent-content">
                            <div class="agent-header">
                                <div class="agent-name">FINAL OUTPUT</div>
                                <div class="agent-status">READY</div>
                            </div>
                            <div class="agent-desc">→ Rendered Video Output</div>
                            <div class="final-output-body">
                                <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:0.75rem;">
                                    <div style="color:#FF6B35; font-size:0.95rem; font-weight:700; letter-spacing:1px;">✓ VIDEO GENERATED</div>
                                    <div style="color: rgba(255,255,255,0.5); font-size:0.72rem; letter-spacing:0.5px;">
                                        {video_duration:.1f}s • {len(video_map)} segments • 1080×1920
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Download button
                with open(final_output, 'rb') as f:
                    st.download_button(
                        label="⬇ DOWNLOAD VIDEO",
                        data=f,
                        file_name=final_output,
                        mime="video/mp4",
                        use_container_width=True,
                        type="primary"
                    )
                
                # Video preview
                st.video(final_output)
            
            # Cleanup
            cleanup_temp_files()
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
        except Exception as e:
            log_placeholder.markdown(f"""
            <div class="system-log">
                <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
                <div class="log-content" style="color: #FF0080;">// ERROR: {str(e)}</div>
            </div>
            """, unsafe_allow_html=True)
