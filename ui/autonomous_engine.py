"""Autonomous Engine - 100% End-to-End Pipeline"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.components import render_log, render_header, render_status_cards
from assemble_video import check_ffmpeg

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

    # Status Cards
    render_status_cards(groq_status, pexels_status, ffmpeg_ok)

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
                <div style="color: #00FF88; font-size: 0.85rem; font-weight: bold; margin-bottom: 0.25rem;">🤖 AUTONOMOUS ENGINE</div>
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
                from spy_agent import analyze_channel_and_suggest_topic
                from script_agent import generate_script, save_script
                from speech_agent import generate_speech_from_script
                from main import transcribe_audio, create_video_map, save_video_map
                from download_videos import download_videos_for_map
                from assemble_video import assemble_video_with_complex_filter
                from add_captions import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo
                from metadata_agent import generate_seo_metadata
                
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
                save_script(script_data)
                
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
                audio_path = generate_speech_from_script(script_data, "audio.mp3")
                
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
                transcript = transcribe_audio(audio_path)
                video_map = create_video_map(transcript)
                save_video_map(video_map)
                
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
                download_videos_for_map(video_map)
                
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
                assemble_video_with_complex_filter(video_map, audio_path, "draft_video.mp4")
                
                # Step 7: Subtitle Agent
                if st.session_state.cancel_requested:
                    raise InterruptedError("Process cancelled by user")
                
                if add_captions:
                    agent_status.markdown("""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #00FF88; font-weight: bold;">✓ AGENT 1-6/8: Complete</div>
                        <div style="color: #FF6B35; font-weight: bold; margin-top: 0.5rem;">📝 AGENT 7/8: Subtitle Agent</div>
                        <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Adding dynamic captions...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    log_placeholder.markdown(render_log("// [7/8] Subtitle Agent: Processing..."), unsafe_allow_html=True)
                    word_segments = create_word_segments(video_map)
                    subtitle_file = create_dynamic_highlight_subtitles(word_segments, video_map)
                    burn_subtitles_and_logo("draft_video.mp4", subtitle_file, "logo.png", "final_output.mp4")
                    final_video = "final_output.mp4"
                else:
                    final_video = "draft_video.mp4"
                
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
                
                # Final Status
                agent_status.markdown("""
                <div style="background: rgba(0, 255, 136, 0.1); border: 1px solid #00FF88; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #00FF88; font-weight: bold;">✓ ALL 8 AGENTS COMPLETE</div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Your reel + SEO metadata is ready!</div>
                </div>
                """, unsafe_allow_html=True)
                
                log_placeholder.markdown(render_log("// ✓ AUTONOMOUS ENGINE COMPLETE"), unsafe_allow_html=True)
                
                # Display output
                with output_placeholder.container():
                    st.markdown(f"""
                    <div style="background: rgba(255, 107, 53, 0.1); border: 1px solid #FF6B35; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                        <div style="color: #FF6B35; font-weight: bold; margin-bottom: 0.5rem;">GENERATED REEL</div>
                        <div style="color: #888; font-size: 0.85rem;">
                            Topic: {topic}<br>
                            Vibe: {script_data.get('video_vibe', 'professional').upper()} | 
                            Duration: ~{script_data.get('estimated_duration', 45)}s
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Video preview
                    if os.path.exists(final_video):
                        st.video(final_video)
                    
                    # Download button
                    st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                    if os.path.exists(final_video):
                        st.download_button(
                            "📥 DOWNLOAD REEL",
                            data=open(final_video, 'rb').read(),
                            file_name=final_video,
                            mime='video/mp4',
                            use_container_width=True
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # SEO Metadata Options - Professional Display
                    st.markdown("""
                    <div style="margin-top: 1.5rem; margin-bottom: 0.5rem;">
                        <div style="color: #00FF88; font-weight: bold; font-size: 1.1rem;">📊 SEO METADATA OPTIONS</div>
                        <div style="color: #888; font-size: 0.85rem; margin-top: 0.25rem;">Copy and paste for maximum reach</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, option in enumerate(metadata['options'], 1):
                        st.markdown(f"""
                        <div style="margin-top: 1rem; padding: 0.5rem; background: rgba(255, 107, 53, 0.05); border-left: 3px solid #FF6B35;">
                            <div style="color: #FF6B35; font-weight: bold; font-size: 0.9rem;">OPTION {i}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**Title:**")
                        st.text_area(
                            f"Title {i}",
                            value=option.get('title', 'N/A'),
                            height=60,
                            label_visibility="collapsed",
                            key=f"title_{i}"
                        )
                        
                        st.markdown("**Description:**")
                        st.text_area(
                            f"Description {i}",
                            value=option.get('description', 'N/A'),
                            height=80,
                            label_visibility="collapsed",
                            key=f"desc_{i}"
                        )
                        
                        st.markdown("**Tags:**")
                        st.text_area(
                            f"Tags {i}",
                            value=', '.join(option.get('tags', [])),
                            height=60,
                            label_visibility="collapsed",
                            key=f"tags_{i}"
                        )
                    
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
