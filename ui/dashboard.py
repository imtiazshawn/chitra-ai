"""Dashboard components for ChitraAI landing page"""
import streamlit as st

PIPELINES = [
    {
        "id": "audio_to_reels",
        "name": "Audio to Reels",
        "description": "Transform audio files into engaging 9:16 vertical videos with AI-generated visuals and dynamic captions.",
        "lazy_level": 40,
        "status": "active",
        "agents": 4
    },
    {
        "id": "topic_to_script",
        "name": "Topic to Script",
        "description": "Research any topic and generate a professional video script with AI-powered content generation.",
        "lazy_level": 20,
        "status": "locked",
        "agents": 1
    },
    {
        "id": "topic_to_speech",
        "name": "Topic to Speech",
        "description": "Convert topics into natural-sounding speech with Google AI Studio's advanced TTS technology.",
        "lazy_level": 60,
        "status": "locked",
        "agents": 3
    },
    {
        "id": "topic_to_reels",
        "name": "Topic to Reels",
        "description": "Ultimate automation: From topic research to final video. Maximum laziness, maximum results.",
        "lazy_level": 100,
        "status": "locked",
        "agents": 7
    }
]

def render_dashboard_header():
    """Render the dashboard header"""
    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">⚡ CHITRA AI</div>
        <div class="dashboard-subtitle">Agentic Video Synthesis System</div>
    </div>
    """, unsafe_allow_html=True)

def render_pipeline_card(pipeline, card_key):
    """Render a single pipeline card"""
    status_class = "active" if pipeline["status"] == "active" else "locked"
    status_text = "● ACTIVE" if pipeline["status"] == "active" else "🔒 DEVELOPING"
    
    card_html = f"""
    <div class="pipeline-card {status_class}" data-pipeline="{pipeline['id']}" id="card_{card_key}">
        <div class="card-content">
            <div class="card-header">
                <div class="card-title">{pipeline['name']}</div>
                <div class="card-status {status_class}">{status_text}</div>
            </div>
            <div class="card-description">{pipeline['description']}</div>
            <div class="card-metrics">
                <div class="lazy-meter">
                    <div class="lazy-label">Automation Level</div>
                    <div class="lazy-bar">
                        <div class="lazy-fill" style="width: {pipeline['lazy_level']}%"></div>
                    </div>
                </div>
                <div class="lazy-value">{pipeline['lazy_level']}%</div>
            </div>
        </div>
    </div>
    """
    return card_html

def render_dashboard():
    """Render the complete dashboard"""
    render_dashboard_header()
    
    # Create columns for the grid
    cols = st.columns(2)
    
    for idx, pipeline in enumerate(PIPELINES):
        with cols[idx % 2]:
            # Render card HTML
            st.markdown(render_pipeline_card(pipeline, idx), unsafe_allow_html=True)
            
            # Add button below card for active pipelines
            if pipeline["status"] == "active":
                if st.button(
                    "⚡ LAUNCH PIPELINE",
                    key=f"btn_{pipeline['id']}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.current_page = pipeline["id"]
                    st.rerun()
            else:
                # Show coming soon text for locked cards
                st.markdown('<div class="coming-soon-text">→ COMING SOON</div>', unsafe_allow_html=True)

def render_back_button():
    """Render back to dashboard button"""
    if st.button("← DASHBOARD", key="back_to_dashboard"):
        st.session_state.current_page = "dashboard"
        st.rerun()
