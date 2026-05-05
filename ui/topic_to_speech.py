"""Topic to Speech pipeline page"""
import streamlit as st
import os

from ui.components import render_log, render_header, render_status_cards
from speech_agent import topic_to_speech
from assemble_video import check_ffmpeg

__all__ = ['render_topic_to_speech']

def render_topic_to_speech():
    """Render the Topic to Speech pipeline page"""
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
    groq_status = groq_key and groq_key != 'your_groq_api_key_here'
    elevenlabs_status = elevenlabs_key and elevenlabs_key != 'your_elevenlabs_api_key_here'
    ffmpeg_ok = check_ffmpeg()

    # Header
    render_header(agent_count=2)

    # Status Cards
    render_status_cards(groq_status, False, ffmpeg_ok)

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
                height=120,
                label_visibility="collapsed"
            )
            
            # Info box
            st.markdown("""
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 6px;">
                <div style="color: #00FF88; font-size: 0.85rem; font-weight: bold; margin-bottom: 0.25rem;">⚡ AGENTIC WORKFLOW</div>
                <div style="color: #CCC; font-size: 0.75rem;">
                    1. Script Agent generates high-retention script<br>
                    2. Voice Agent synthesizes professional audio
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate Button
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            generate_btn = st.button("⚡ GENERATE AUDIO", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// AGENT CONSOLE</div>', unsafe_allow_html=True)
            
            # Agent status placeholder
            agent_status = st.empty()
            
            # Output placeholder
            output_placeholder = st.empty()
            
            # System Log
            st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
            log_placeholder = st.empty()
            log_placeholder.markdown(render_log("// awaiting topic input..."), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Process Pipeline
    if generate_btn:
        if not topic:
            log_placeholder.markdown(render_log("// ERROR: Topic cannot be empty", is_error=True), unsafe_allow_html=True)
        elif not groq_status:
            log_placeholder.markdown(render_log("// ERROR: GROQ_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        else:
            try:
                # Step 1: Script Generation
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #FF6B35; font-weight: bold;">🤖 SCRIPT AGENT: Generating...</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Analyzing topic and creating high-retention script</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [SCRIPT AGENT] Generating high-retention script..."), unsafe_allow_html=True)
                
                script_data, audio_path = topic_to_speech(topic)
                
                # Step 2: Voice Synthesis
                agent_status.markdown("""
                <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ SCRIPT AGENT: Complete</div>
                    <div style="color: #00FF88; font-weight: bold; margin-top: 0.5rem;">🎙️ VOICE AGENT: Processing...</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Synthesizing with ElevenLabs (Adam Voice)</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [VOICE AGENT] ✓ Professional voice generated"), unsafe_allow_html=True)
                
                # Final status
                agent_status.markdown("""
                <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ SCRIPT AGENT: Complete</div>
                    <div style="color: #00FF88; font-weight: bold; margin-top: 0.5rem;">✓ VOICE AGENT: Complete</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// ✓ PIPELINE COMPLETE"), unsafe_allow_html=True)
                
                # Display output
                with output_placeholder.container():
                    st.markdown(f"""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #FF6B35; font-weight: bold; margin-bottom: 0.5rem;">GENERATED ASSETS</div>
                        <div style="color: #888; font-size: 0.85rem;">
                            Script: {len(script_data.get('formatted_script', []))} lines | 
                            Vibe: {script_data.get('video_vibe', 'professional').upper()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            "📥 SCRIPT JSON",
                            data=open('generated_script.json', 'rb').read(),
                            file_name='generated_script.json',
                            mime='application/json',
                            use_container_width=True
                        )
                    with col2:
                        st.download_button(
                            "📥 CLEAN SCRIPT",
                            data=open('clean_script.txt', 'rb').read(),
                            file_name='clean_script.txt',
                            mime='text/plain',
                            use_container_width=True
                        )
                    with col3:
                        if os.path.exists(audio_path):
                            st.download_button(
                                "🎙️ AUDIO MP3",
                                data=open(audio_path, 'rb').read(),
                                file_name='audio.mp3',
                                mime='audio/mpeg',
                                use_container_width=True
                            )
                    
                    # Audio player
                    if os.path.exists(audio_path):
                        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                        st.audio(audio_path)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Next steps
                    st.markdown("""
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px;">
                        <div style="color: #00FF88; font-weight: bold; margin-bottom: 0.5rem;">✓ READY FOR VIDEO:</div>
                        <div style="color: #CCC; font-size: 0.85rem;">
                            Upload audio.mp3 to "Audio to Reels" pipeline to generate your final video
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                log_placeholder.markdown(render_log(f"// ERROR: {str(e)}", is_error=True), unsafe_allow_html=True)
                agent_status.empty()
