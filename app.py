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
        margin-bottom: 2rem;
    }
    
    .system-status {
        color: #FF6B35;
        font-size: 0.9rem;
        text-align: right;
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
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: rgba(255, 107, 53, 0.05);
        border: 1px solid;
        padding: 1rem;
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
    
    .input-panel {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #222;
        padding: 1.5rem;
    }
    
    .panel-title {
        color: #FF6B35;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .upload-zone {
        border: 2px dashed #333;
        padding: 2rem 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
        background: rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    }
    
    .upload-zone:hover {
        border-color: #FF6B35;
        background: rgba(255, 107, 53, 0.05);
    }
    
    .upload-label {
        color: #666;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .toggle-container {
        padding: 1rem;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid #222;
        margin-bottom: 1.5rem;
    }
    
    .agent-console {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #222;
        padding: 1.5rem;
    }
    
    .agent-item {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .agent-item:not(:last-child)::after {
        content: '';
        position: absolute;
        left: 1.25rem;
        top: 3rem;
        width: 2px;
        height: calc(100% - 1rem);
        background: linear-gradient(180deg, #FF6B35 0%, #FF0080 100%);
        opacity: 0.3;
    }
    
    .agent-number {
        color: #FF6B35;
        font-size: 1.5rem;
        font-weight: 700;
        min-width: 2.5rem;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    .agent-content {
        flex: 1;
    }
    
    .agent-name {
        color: #FFF;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .agent-desc {
        color: #666;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .agent-status {
        display: inline-block;
        color: #FF6B35;
        font-size: 0.75rem;
        padding: 0.25rem 0.75rem;
        border: 1px solid #FF6B35;
        text-shadow: 0 0 5px rgba(255, 107, 53, 0.5);
    }
    
    .agent-status.running {
        animation: glow 1.5s infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(255, 107, 53, 0.5); }
        50% { box-shadow: 0 0 15px rgba(255, 107, 53, 0.8); }
    }
    
    .system-log {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid #222;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .log-title {
        color: #FF6B35;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .log-content {
        color: rgba(255, 107, 53, 0.4);
        font-size: 0.85rem;
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
        <div style="margin-top: 0.25rem;">AGENTS: 04</div>
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
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
    
    # Audio Upload
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">AUDIO SOURCE</div>', unsafe_allow_html=True)
    audio_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], key="audio")
    if audio_file:
        st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem;">✓ {audio_file.name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Logo Upload
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">BRAND LOGO (OPTIONAL)</div>', unsafe_allow_html=True)
    logo_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="logo")
    if logo_file:
        st.markdown(f'<div style="color: #FF6B35; font-size: 0.75rem;">✓ {logo_file.name}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Caption Toggle
    st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
    add_captions = st.checkbox("DYNAMIC WORD-LEVEL CAPTIONS", value=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initiate Button
    initiate = st.button("⚡ INITIATE PIPELINE", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="agent-console">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">// AGENT CONSOLE</div>', unsafe_allow_html=True)
    
    # Agent Pipeline
    st.markdown(f"""
    <div class="agent-item">
        <div class="agent-number">01</div>
        <div class="agent-content">
            <div class="agent-name">SCRIPT AGENT</div>
            <div class="agent-desc">→ Transcribe audio via Groq Whisper<br/>→ Generate timestamped video map with AI</div>
            <div class="agent-status">IDLE</div>
        </div>
    </div>
    
    <div class="agent-item">
        <div class="agent-number">02</div>
        <div class="agent-content">
            <div class="agent-name">ASSET AGENT</div>
            <div class="agent-desc">→ Extract visual keywords from segments<br/>→ Download portrait videos from Pexels API</div>
            <div class="agent-status">IDLE</div>
        </div>
    </div>
    
    <div class="agent-item">
        <div class="agent-number">03</div>
        <div class="agent-content">
            <div class="agent-name">ASSEMBLY AGENT</div>
            <div class="agent-desc">→ Trim and sync video clips to timestamps<br/>→ Render 9:16 vertical format with FFmpeg</div>
            <div class="agent-status">IDLE</div>
        </div>
    </div>
    
    <div class="agent-item">
        <div class="agent-number">04</div>
        <div class="agent-content">
            <div class="agent-name">SUBTITLE AGENT</div>
            <div class="agent-desc">→ Generate word-level caption timing<br/>→ Burn subtitles and logo overlay</div>
            <div class="agent-status">IDLE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# System Log
log_placeholder = st.empty()
log_placeholder.markdown("""
<div class="system-log">
    <div class="log-title">// SYSTEM LOG</div>
    <div class="log-content">// awaiting pipeline start...</div>
</div>
""", unsafe_allow_html=True)

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
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// ✓ PIPELINE COMPLETE</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Video info
            video_duration = get_video_duration(final_output)
            
            st.markdown(f"""
            <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; padding: 1.5rem; margin-top: 2rem;">
                <div style="color: #FF6B35; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem;">✓ VIDEO GENERATED</div>
                <div style="color: #888; font-size: 0.85rem;">
                    Duration: {video_duration:.1f}s | Segments: {len(video_map)} | Resolution: 1080x1920
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
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF0080;">// ERROR: {str(e)}</div>
            </div>
            """, unsafe_allow_html=True)
