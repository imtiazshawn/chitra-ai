"""Topic to Reels - Full 80% Automation Pipeline"""
import streamlit as st
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.components import render_log, render_header, render_status_cards
from assemble_video import check_ffmpeg, get_video_duration
from workspace_manager import create_unique_project_folder, get_project_paths, cleanup_project_temp

def render_topic_to_reels():
    """Render the Topic to Reels full automation pipeline"""
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    
    groq_status = groq_key and groq_key != 'your_groq_api_key_here'
    elevenlabs_status = elevenlabs_key and elevenlabs_key != 'your_elevenlabs_api_key_here'
    pexels_status = pexels_key and pexels_key != 'your_pexels_api_key_here'
    ffmpeg_ok = check_ffmpeg()

    # Header
    render_header(agent_count=6)

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
                height=120,
                label_visibility="collapsed"
            )
            
            # Captions Toggle
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            add_captions = st.checkbox(
                "Add dynamic captions",
                value=True,
                help="Professional word-level highlighting captions"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate Button
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            generate_btn = st.button("⚡ GENERATE REEL", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// AGENT CONSOLE</div>', unsafe_allow_html=True)
            
            # Agent Pipeline Display
            agent_pipeline = st.empty()
            agent_pipeline.markdown("""
            <div class="agent-list">
            <div class="agent-item">
                <div class="agent-number">01</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SCRIPT AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate high-retention script<br/>→ Hook, tension, solution, CTA structure</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">02</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">VOICE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Synthesize professional voiceover<br/>→ ElevenLabs or Edge-TTS backup</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">03</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">INTELLIGENCE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Transcribe and analyze audio<br/>→ Generate timestamped video map</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">04</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">DOWNLOAD AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Extract visual keywords<br/>→ Download videos from Pexels</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">05</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">ASSEMBLY AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Sync clips with audio<br/>→ Render 9:16 vertical format</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">06</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SUBTITLE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate word-level captions<br/>→ Burn subtitles and logo</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent status placeholder for updates
            agent_status = st.empty()
            
            # Output placeholder
            output_placeholder = st.empty()
            
            # System Log
            st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
            log_placeholder = st.empty()
            log_placeholder.markdown(render_log("// awaiting topic input..."), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Process Full Pipeline
    if generate_btn:
        if not topic:
            log_placeholder.markdown(render_log("// ERROR: Topic cannot be empty", is_error=True), unsafe_allow_html=True)
        elif not groq_status:
            log_placeholder.markdown(render_log("// ERROR: GROQ_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        elif not pexels_status:
            log_placeholder.markdown(render_log("// ERROR: PEXELS_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        else:
            try:
                # Create unique project folder
                project_folder, project_id = create_unique_project_folder("topic_to_reels")
                paths = get_project_paths(project_folder)
                
                from script_agent import generate_script
                from speech_agent import generate_speech_from_script
                from main import transcribe_audio, create_video_map
                from ui.pipeline import download_video_to_project, preprocess_clip, assemble_video
                from add_captions import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo
                import json
                
                # Step 1: Script Generation
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #FF6B35; font-weight: bold;">🤖 AGENT 1/6: Script Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Generating high-retention script...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [1/6] Script Agent: Generating..."), unsafe_allow_html=True)
                script_data = generate_script(topic, add_reading_instructions=True)
                
                # Save script to project folder
                with open(paths['script'], 'w', encoding='utf-8') as f:
                    json.dump(script_data, f, indent=2, ensure_ascii=False)
                
                # Step 2: Voice Synthesis
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1/6: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🎙️ AGENT 2/6: Voice Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Synthesizing professional voiceover...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [2/6] Voice Agent: Synthesizing..."), unsafe_allow_html=True)
                audio_path = generate_speech_from_script(script_data, paths['audio'], paths['clean_script'])
                
                # Step 3: Intelligence Agent
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-2/6: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🧠 AGENT 3/6: Intelligence Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Analyzing audio and mapping visuals...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [3/6] Intelligence Agent: Mapping..."), unsafe_allow_html=True)
                transcript = transcribe_audio(paths['audio'])
                video_map = create_video_map(transcript)
                
                # Save video map to project folder
                with open(paths['video_map'], 'w', encoding='utf-8') as f:
                    json.dump(video_map, f, indent=2, ensure_ascii=False)
                
                # Step 4: Download Agent
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-3/6: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📥 AGENT 4/6: Download Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Fetching visual assets from Pexels...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [4/6] Download Agent: Fetching..."), unsafe_allow_html=True)
                successful = sum(1 for i, segment in enumerate(video_map, 1) if download_video_to_project(segment, i, paths['assets']))
                
                # Step 5: Assembly Agent
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-4/6: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🎬 AGENT 5/6: Assembly Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Compiling video with perfect sync...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [5/6] Assembly Agent: Compiling..."), unsafe_allow_html=True)
                assemble_video(video_map, paths['audio'], paths['draft_video'], paths['assets'], paths['temp'])
                
                # Step 6: Subtitle Agent (if enabled)
                final_output = paths['draft_video']
                if add_captions:
                    agent_status.markdown("""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-5/6: Complete</div>
                        <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📝 AGENT 6/6: Subtitle Agent</div>
                        <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Adding dynamic captions...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    log_placeholder.markdown(render_log("// [6/6] Subtitle Agent: Processing..."), unsafe_allow_html=True)
                    word_segments = create_word_segments(video_map, transcript)
                    create_dynamic_highlight_subtitles(word_segments, video_map, paths['captions'])
                    logo_for_caption = paths['logo'] if os.path.exists(paths['logo']) else None
                    burn_subtitles_and_logo(paths['draft_video'], paths['captions'], logo_for_caption, paths['final_output'])
                    final_output = paths['final_output']
                
                # Final Status
                agent_status.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ ALL AGENTS COMPLETE</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Your reel is ready!</div>
                    <div style="color: #666; font-size: 0.75rem; margin-top: 0.25rem;">Project: {project_id}</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log(f"// ✓ PIPELINE COMPLETE - {project_id}"), unsafe_allow_html=True)
                
                # Cleanup
                cleanup_project_temp(project_folder)
                
                # Display output
                video_duration = get_video_duration(final_output)
                
                with output_placeholder.container():
                    st.markdown(f"""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #FF6B35; font-weight: bold; margin-bottom: 0.5rem;">GENERATED REEL</div>
                        <div style="color: #888; font-size: 0.85rem;">
                            Vibe: {script_data.get('video_vibe', 'professional').upper()} | 
                            Duration: {video_duration:.1f}s
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Video preview
                    if os.path.exists(final_output):
                        st.video(final_output)
                    
                    # Download button
                    st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                    if os.path.exists(final_output):
                        st.download_button(
                            "📥 DOWNLOAD REEL",
                            data=open(final_output, 'rb').read(),
                            file_name=f"{project_id}.mp4",
                            mime='video/mp4',
                            use_container_width=True
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Success message
                    st.markdown("""
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px;">
                        <div style="color: #00FF88; font-weight: bold; margin-bottom: 0.5rem;">🎬 READY TO UPLOAD!</div>
                        <div style="color: #CCC; font-size: 0.85rem;">
                            Your professional reel is ready for Instagram, TikTok, or YouTube Shorts
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                log_placeholder.markdown(render_log(f"// ERROR: {str(e)}", is_error=True), unsafe_allow_html=True)
                st.error(f"Pipeline failed: {str(e)}\n\n{error_details}")
                agent_status.empty()
