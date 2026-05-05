"""Topic to Reels pipeline page"""
import streamlit as st
import os

from ui.components import render_header, render_status_cards, render_log
from script_agent import generate_script, save_script

def render_topic_to_reels():
    """Render the Topic to Reels pipeline page"""
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    groq_status = groq_key and groq_key != 'your_groq_api_key_here'

    # Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">TOPIC TO REELS</div>
        <div class="page-subtitle">AI Script Generation → Video Synthesis</div>
    </div>
    """, unsafe_allow_html=True)

    # Status Card
    with st.container(border=True):
        st.markdown('<div class="panel-title">// SYSTEM STATUS</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            status_icon = "✓" if groq_status else "✗"
            status_color = "#00FF88" if groq_status else "#FF0080"
            st.markdown(f'<div style="color: {status_color}; font-size: 0.9rem;">{status_icon} GROQ API</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="color: #FFB800; font-size: 0.9rem;">⚠ TTS: Manual (Coming Soon)</div>', unsafe_allow_html=True)

    # Main Grid
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
            
            # Topic Input
            st.markdown('<div class="upload-label">TOPIC / IDEA</div>', unsafe_allow_html=True)
            topic = st.text_area(
                "",
                placeholder="e.g., Why microservices fail in startups",
                height=100,
                label_visibility="collapsed"
            )
            
            # Reading Instructions Checkbox
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            add_instructions = st.checkbox(
                "Add reading instructions on script",
                value=False,
                help="Include [Director Cues] for tone, pacing, and silences"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Script Style
            st.markdown('<div class="upload-label" style="margin-top: 1.5rem;">SCRIPT STYLE</div>', unsafe_allow_html=True)
            script_style = st.selectbox(
                "",
                ["Senior Architect (Default)", "Energetic Educator", "Dramatic Storyteller"],
                label_visibility="collapsed"
            )
            
            # Generate Button
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            generate_btn = st.button("⚡ GENERATE SCRIPT", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// SCRIPT OUTPUT</div>', unsafe_allow_html=True)
            
            # Output placeholder
            output_placeholder = st.empty()
            
            # System Log
            st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
            log_placeholder = st.empty()
            log_placeholder.markdown(render_log("// awaiting topic input..."), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Process Script Generation
    if generate_btn:
        if not topic:
            log_placeholder.markdown(render_log("// ERROR: Topic cannot be empty", is_error=True), unsafe_allow_html=True)
        elif not groq_status:
            log_placeholder.markdown(render_log("// ERROR: GROQ_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        else:
            try:
                # Generate script
                log_placeholder.markdown(render_log("// [SCRIPT AGENT] Generating high-retention script..."), unsafe_allow_html=True)
                
                script_data = generate_script(topic, add_instructions)
                save_script(script_data)
                
                log_placeholder.markdown(render_log("// [SCRIPT AGENT] ✓ Script generated successfully"), unsafe_allow_html=True)
                
                # Display output
                with output_placeholder.container():
                    st.markdown(f"""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #FF6B35; font-weight: bold; margin-bottom: 0.5rem;">VIBE: {script_data.get('video_vibe', 'professional').upper()}</div>
                        <div style="color: #888; font-size: 0.85rem;">Duration: ~{script_data.get('estimated_duration', 45)}s | Lines: {len(script_data.get('formatted_script', []))}</div>
                        {f'<div style="color: #00FF88; font-size: 0.85rem; margin-top: 0.25rem;">✓ Reading instructions included</div>' if add_instructions else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="upload-label">THE HOOK (0-5s)</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color: #FFF; padding: 0.75rem; background: rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 1rem;">{script_data.get("hook", "N/A")}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="upload-label">FORMATTED SCRIPT</div>', unsafe_allow_html=True)
                    
                    # Display formatted script with proper line breaks
                    formatted_lines = script_data.get('formatted_script', [])
                    script_display = "\n".join(formatted_lines)
                    
                    st.text_area("", value=script_display, height=300, label_visibility="collapsed")
                    
                    st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                    st.download_button(
                        "📥 DOWNLOAD SCRIPT JSON",
                        data=open('generated_script.json', 'rb').read(),
                        file_name='generated_script.json',
                        mime='application/json',
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(255, 184, 0, 0.1); border: 1px solid #FFB800; border-radius: 8px;">
                        <div style="color: #FFB800; font-weight: bold; margin-bottom: 0.5rem;">⚠ NEXT STEPS:</div>
                        <div style="color: #CCC; font-size: 0.85rem;">
                            1. Use a TTS service (ElevenLabs, Google TTS) to convert script to audio<br>
                            2. Upload the audio to "Audio to Reels" pipeline<br>
                            3. Generate your final video
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                log_placeholder.markdown(render_log(f"// ERROR: {str(e)}", is_error=True), unsafe_allow_html=True)
