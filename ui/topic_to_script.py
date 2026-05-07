"""Topic to Script pipeline page"""
import streamlit as st
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.components import render_log, render_header, render_status_cards
from script_agent import generate_script, save_script
from assemble_video import check_ffmpeg

def render_topic_to_script():
    """Render the Topic to Script pipeline page"""
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    groq_status = groq_key and groq_key != 'your_groq_api_key_here'
    ffmpeg_ok = check_ffmpeg()

    # Header
    render_header(agent_count=1)

    # Main Grid
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
            
            # Topic Input
            st.markdown('<div class="upload-label">TOPIC / IDEA</div>', unsafe_allow_html=True)
            topic = st.text_area(
                "",
                placeholder="e.g., Why most startups fail in first year",
                height=100,
                label_visibility="collapsed"
            )
            
            # Reading Instructions Checkbox
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            add_instructions = st.checkbox(
                "Add reading instructions",
                value=False,
                help="Include [Director Cues] for tone, pacing, and silences"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Info box
            st.markdown("""
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 6px;">
                <div style="color: #00FF88; font-size: 0.85rem; font-weight: bold; margin-bottom: 0.25rem;">SCRIPT ONLY</div>
                <div style="color: #CCC; font-size: 0.75rem;">
                    Generates high-retention 40-50s script<br>
                    Perfect for content planning<br>
                    Use with external TTS services
                </div>
            </div>
            """, unsafe_allow_html=True)
            
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
                            1. Use "Topic to Speech" for automatic voiceover<br>
                            2. Or use external TTS (ElevenLabs, Google TTS)<br>
                            3. Upload audio to "Audio to Reels" pipeline
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                log_placeholder.markdown(render_log(f"// ERROR: {str(e)}", is_error=True), unsafe_allow_html=True)
