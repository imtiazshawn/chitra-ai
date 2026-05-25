"""Autonomous Engine - 100% End-to-End Pipeline"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.components import render_log, render_header, render_status_cards
from assemble_video import check_ffmpeg, get_video_duration
from workspace_manager import create_unique_project_folder, get_project_paths, cleanup_project_temp

def render_autonomous_engine():
    """Render the Autonomous Engine 100% pipeline page"""
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'cancel_requested' not in st.session_state:
        st.session_state.cancel_requested = False
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    
    groq_status = groq_key and groq_key != 'your_groq_api_key_here'
    pexels_status = pexels_key and pexels_key != 'your_pexels_api_key_here'
    ffmpeg_ok = check_ffmpeg()

    # Header
    render_header(agent_count=8)

    # Main Grid
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">// INPUT CONFIG</div>', unsafe_allow_html=True)
            
            # YouTube Channel URL Input
            st.markdown('<div class="upload-label">YOUTUBE CHANNEL URL</div>', unsafe_allow_html=True)
            channel_url = st.text_input(
                "",
                placeholder="e.g., https://youtube.com/@channelname",
                label_visibility="collapsed",
                disabled=st.session_state.processing
            )
            
            # Captions Toggle
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            add_captions = st.checkbox(
                "Add dynamic captions",
                value=True,
                help="Professional word-level highlighting captions",
                disabled=st.session_state.processing
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Info box
            st.markdown("""
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 6px;">
                <div style="color: #00FF88; font-size: 0.85rem; font-weight: bold; margin-bottom: 0.25rem;">AUTONOMOUS ENGINE</div>
                <div style="color: #CCC; font-size: 0.75rem;">
                    AI analyzes channel → Suggests topic<br>
                    Generates script → Creates voiceover<br>
                    Assembles video → Optimizes SEO<br>
                    100% hands-free content creation
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Control Buttons
            st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            if st.session_state.processing:
                st.button("⏳ PROCESSING...", use_container_width=True, disabled=True, type="primary")
            else:
                generate_btn = st.button("⚡ ANALYZE & GENERATE", use_container_width=True, type="primary")

            if st.session_state.processing:
                st.markdown('<div style="margin-top: 0.5rem;">', unsafe_allow_html=True)
                if st.button("✕ CANCEL", use_container_width=True, type="secondary"):
                    st.session_state.cancel_requested = True
                    st.session_state.processing = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

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
                        <div class="agent-name">SPY AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Analyze YouTube channel content<br/>→ Suggest unique trending topic</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">02</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SCRIPT AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate high-retention script<br/>→ Hook, tension, solution, CTA structure</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">03</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">VOICE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Synthesize professional voiceover<br/>→ ElevenLabs or Edge-TTS backup</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">04</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">INTELLIGENCE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Transcribe and analyze audio<br/>→ Generate timestamped video map</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">05</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">DOWNLOAD AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Extract visual keywords<br/>→ Download videos from Pexels</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">06</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">ASSEMBLY AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Sync clips with audio<br/>→ Render 9:16 vertical format</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">07</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">SUBTITLE AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate word-level captions<br/>→ Burn subtitles and logo</div>
                </div>
            </div>
            
            <div class="agent-item">
                <div class="agent-number">08</div>
                <div class="agent-content">
                    <div class="agent-header">
                        <div class="agent-name">METADATA AGENT</div>
                        <div class="agent-status">IDLE</div>
                    </div>
                    <div class="agent-desc">→ Generate viral titles (3 options)<br/>→ SEO descriptions and tags</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent status placeholder
            agent_status = st.empty()
            
            # Output placeholder
            output_placeholder = st.empty()
            
            # System Log
            st.markdown('<div style="margin-top: 1.15rem;">', unsafe_allow_html=True)
            log_placeholder = st.empty()
            log_placeholder.markdown(render_log("// awaiting channel URL..."), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Process Autonomous Engine Pipeline
    if 'generate_btn' in locals() and generate_btn and not st.session_state.processing:
        if not channel_url:
            log_placeholder.markdown(render_log("// ERROR: YouTube channel URL required", is_error=True), unsafe_allow_html=True)
        elif not groq_status:
            log_placeholder.markdown(render_log("// ERROR: GROQ_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        elif not pexels_status:
            log_placeholder.markdown(render_log("// ERROR: PEXELS_API_KEY not configured", is_error=True), unsafe_allow_html=True)
        else:
            st.session_state.processing = True
            st.session_state.cancel_requested = False
            
            try:
                # Create unique project folder
                project_folder, project_id = create_unique_project_folder("autonomous")
                paths = get_project_paths(project_folder)
                
                from spy_agent import analyze_channel_and_suggest_topic
                from script_agent import generate_script
                from speech_agent import generate_speech_from_script
                from main import transcribe_audio, create_video_map
                from ui.pipeline import download_video_to_project, assemble_video
                from add_captions import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo
                from metadata_agent import generate_seo_metadata
                import json
                
                # Step 1: Spy Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #FF6B35; font-weight: bold;">🕵️ AGENT 1/8: Spy Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Analyzing channel content patterns...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [1/8] Spy Agent: Analyzing channel..."), unsafe_allow_html=True)
                spy_data = analyze_channel_and_suggest_topic(channel_url)
                topic = spy_data['suggested_topic']
                
                # Step 2: Script Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown(f"""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1/8: Complete</div>
                    <div style="color: #888; font-size: 0.75rem; margin-top: 0.25rem;">Topic: {topic}</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🤖 AGENT 2/8: Script Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Generating high-retention script...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [2/8] Script Agent: Generating..."), unsafe_allow_html=True)
                script_data = generate_script(topic, add_reading_instructions=True)
                
                # Save script to project folder
                with open(paths['script'], 'w', encoding='utf-8') as f:
                    json.dump(script_data, f, indent=2, ensure_ascii=False)
                
                # Step 3: Voice Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-2/8: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🎙️ AGENT 3/8: Voice Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Synthesizing professional voiceover...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [3/8] Voice Agent: Synthesizing..."), unsafe_allow_html=True)
                audio_path = generate_speech_from_script(script_data, paths['audio'], paths['clean_script'])
                
                # Step 4: Intelligence Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-3/8: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🧠 AGENT 4/8: Intelligence Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Analyzing audio and mapping visuals...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [4/8] Intelligence Agent: Mapping..."), unsafe_allow_html=True)
                transcript = transcribe_audio(paths['audio'])
                video_map = create_video_map(transcript)
                
                # Save video map to project folder
                with open(paths['video_map'], 'w', encoding='utf-8') as f:
                    json.dump(video_map, f, indent=2, ensure_ascii=False)
                
                # Step 5: Download Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-4/8: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📥 AGENT 5/8: Download Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Fetching visual assets from Pexels...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [5/8] Download Agent: Fetching..."), unsafe_allow_html=True)
                successful = sum(1 for i, segment in enumerate(video_map, 1) if download_video_to_project(segment, i, paths['assets']))
                
                # Step 6: Assembly Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-5/8: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">🎬 AGENT 6/8: Assembly Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Compiling video with perfect sync...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [6/8] Assembly Agent: Compiling..."), unsafe_allow_html=True)
                assemble_video(video_map, paths['audio'], paths['draft_video'], paths['assets'], paths['temp'])
                
                # Step 7: Subtitle Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                final_output = paths['draft_video']
                if add_captions:
                    agent_status.markdown("""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-6/8: Complete</div>
                        <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📝 AGENT 7/8: Subtitle Agent</div>
                        <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Adding dynamic captions...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    log_placeholder.markdown(render_log("// [7/8] Subtitle Agent: Processing..."), unsafe_allow_html=True)
                    word_segments = create_word_segments(video_map, transcript, paths['audio'])
                    create_dynamic_highlight_subtitles(word_segments, video_map, paths['captions'])
                    logo_for_caption = paths['logo'] if os.path.exists(paths['logo']) else None
                    burn_subtitles_and_logo(paths['draft_video'], paths['captions'], logo_for_caption, paths['final_output'])
                    final_output = paths['final_output']
                
                # Step 8: Metadata Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                agent_status.markdown("""
                <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-7/8: Complete</div>
                    <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📊 AGENT 8/8: Metadata Agent</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Generating SEO metadata...</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// [8/8] Metadata Agent: Optimizing..."), unsafe_allow_html=True)
                metadata = generate_seo_metadata(script_data)
                
                # Save metadata to project folder
                with open(paths['metadata'], 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Final Status
                agent_status.markdown(f"""
                <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ ALL 8 AGENTS COMPLETE</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Your reel + SEO metadata is ready!</div>
                    <div style="color: #666; font-size: 0.75rem; margin-top: 0.25rem;">Project: {project_id}</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log(f"// ✓ AUTONOMOUS ENGINE COMPLETE - {project_id}"), unsafe_allow_html=True)
                
                # Cleanup
                cleanup_project_temp(project_folder)
                
                # Display output
                video_duration = get_video_duration(final_output)
                
                with output_placeholder.container():
                    st.markdown(f"""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #FF6B35; font-weight: bold; margin-bottom: 0.5rem;">GENERATED REEL</div>
                        <div style="color: #888; font-size: 0.85rem;">
                            Topic: {topic}<br>
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
                    
                    # SEO Metadata Options - Premium Accordion Layout
                    st.markdown("""
                    <div style="margin-top: 1.5rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem;">
                        <div style="color: #00FF88; font-weight: bold; margin-bottom: 0.75rem;">📊 SEO METADATA (3 OPTIONS)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, option in enumerate(metadata['options'], 1):
                        # Determine focus type for each option
                        focus_types = ['Viral Focus', 'SEO Focus', 'Curiosity/Hook Focus']
                        focus_type = focus_types[i-1] if i <= len(focus_types) else 'Balanced Focus'
                        
                        with st.expander(f"Option {i}: {focus_type}", expanded=(i==1)):
                            st.markdown(f"**Title:**")
                            st.code(option.get('title', 'N/A'), language=None)
                            
                            st.markdown(f"**Description:**")
                            st.code(option.get('description', 'N/A'), language=None)
                            
                            st.markdown(f"**Tags:**")
                            st.code(', '.join(option.get('tags', [])), language=None)
                    
                    # Success message
                    st.markdown("""
                    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px;">
                        <div style="color: #00FF88; font-weight: bold; margin-bottom: 0.5rem;">🎬 READY TO UPLOAD!</div>
                        <div style="color: #CCC; font-size: 0.85rem;">
                            Your professional reel + SEO metadata is ready for YouTube Shorts, Instagram Reels, or TikTok
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.session_state.processing = False
                
            except InterruptedError as e:
                log_placeholder.markdown(render_log(f"// CANCELLED: {str(e)}", is_error=True), unsafe_allow_html=True)
                agent_status.empty()
                st.session_state.processing = False
                st.warning("Process cancelled by user")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                log_placeholder.markdown(render_log(f"// ERROR: {str(e)}", is_error=True), unsafe_allow_html=True)
                st.error(f"Pipeline failed: {str(e)}\n\n{error_details}")
                agent_status.empty()
                st.session_state.processing = False
