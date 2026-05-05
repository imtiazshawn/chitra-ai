"""Reusable UI components for ChitraAI"""
import streamlit as st

def render_header(agent_count=4):
    """Render the main header with status"""
    st.markdown(f"""
    <div class="status-bar">
        <div class="neon-title">⚡ CHITRA AI PIPELINE</div>
        <div class="system-status">
            <div><span class="status-dot"></span>STATUS: ONLINE</div>
            <div style="margin-top: 0.15rem;">AGENTS: {agent_count:02d}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_status_cards(groq_status, pexels_status, ffmpeg_ok):
    """Render API and system status cards"""
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

def render_agent_list():
    """Render the agent pipeline list"""
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

def render_log(message, is_error=False):
    """Render system log message"""
    color = "#FF0080" if is_error else "#FF6B35"
    return f"""
    <div class="system-log">
        <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
        <div class="log-content" style="color: {color};">{message}</div>
    </div>
    """

def render_final_output(video_duration, segment_count, final_output):
    """Render final output section"""
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
                            {video_duration:.1f}s • {segment_count} segments • 1080×1920
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with open(final_output, 'rb') as f:
        st.download_button(
            label="⬇ DOWNLOAD VIDEO",
            data=f,
            file_name=final_output,
            mime="video/mp4",
            use_container_width=True,
            type="primary"
        )
    
    st.video(final_output)
