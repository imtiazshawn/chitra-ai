import streamlit as st
import os
import sys
import json
import time
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
    process_clip,
    create_concat_file,
    concatenate_videos,
    add_audio,
    cleanup_temp_files,
    get_video_duration
)
from add_captions import (
    create_word_segments,
    create_ass_subtitle,
    burn_subtitles_and_logo
)

# Page config
st.set_page_config(
    page_title="ChitraAI - AI Video Generator",
    page_icon="🎬",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-top: 0;
    }
    .stProgress > div > div > div > div {
        background-color: #FF6B6B;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎬 ChitraAI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Video Generator for Reels & Shorts</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - API Keys Check
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check API keys
    groq_key = os.getenv('GROQ_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    
    if groq_key and groq_key != 'your_groq_api_key_here':
        st.success("✓ Groq API Key")
    else:
        st.error("✗ Groq API Key Missing")
    
    if pexels_key and pexels_key != 'your_pexels_api_key_here':
        st.success("✓ Pexels API Key")
    else:
        st.error("✗ Pexels API Key Missing")
    
    # Check FFmpeg
    if check_ffmpeg():
        st.success("✓ FFmpeg Installed")
    else:
        st.error("✗ FFmpeg Not Found")
    
    st.markdown("---")
    st.markdown("### 📚 How It Works")
    st.markdown("""
    1. Upload your audio
    2. AI transcribes & maps scenes
    3. Downloads matching videos
    4. Assembles final video
    5. (Optional) Adds captions
    """)

# Main interface
st.header("📤 Upload Audio")
audio_file = st.file_uploader(
    "Choose an audio file (MP3, WAV)", 
    type=['mp3', 'wav', 'm4a'],
    help="Upload the audio for your video"
)

# Options
st.header("🎨 Options")
col1, col2 = st.columns(2)

with col1:
    add_captions = st.checkbox(
        "Add Professional Captions",
        value=True,
        help="Add word-level captions with professional styling"
    )

with col2:
    logo_file = st.file_uploader(
        "Logo (Optional)",
        type=['png', 'jpg', 'jpeg'],
        help="Add your branding logo (top-right corner)"
    )

# Generate button
st.markdown("---")

if st.button("🎬 Generate Video", type="primary", use_container_width=True):
    if not audio_file:
        st.error("⚠️ Please upload an audio file first!")
    elif not groq_key or groq_key == 'your_groq_api_key_here':
        st.error("⚠️ Please configure GROQ_API_KEY in .env file")
    elif not pexels_key or pexels_key == 'your_pexels_api_key_here':
        st.error("⚠️ Please configure PEXELS_API_KEY in .env file")
    elif not check_ffmpeg():
        st.error("⚠️ FFmpeg is not installed. Please install it first.")
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
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Transcription
            status_text.text("🎤 Step 1/4: Transcribing audio...")
            progress_bar.progress(10)
            
            transcript = transcribe_audio(audio_path)
            video_map = create_video_map(transcript)
            save_video_map(video_map)
            
            progress_bar.progress(25)
            st.success(f"✓ Transcribed {len(video_map)} segments")
            
            # Step 2: Download videos
            status_text.text("📥 Step 2/4: Downloading videos from Pexels...")
            progress_bar.progress(30)
            
            create_assets_folder()
            successful = 0
            
            for i, segment in enumerate(video_map, 1):
                keyword = segment.get('visual_keyword', 'abstract')
                if find_and_download_video(keyword, i):
                    successful += 1
                progress_bar.progress(30 + int((i / len(video_map)) * 30))
            
            st.success(f"✓ Downloaded {successful}/{len(video_map)} clips")
            
            # Step 3: Assemble video
            status_text.text("🎞️ Step 3/4: Assembling video...")
            progress_bar.progress(65)
            
            create_temp_folder()
            processed_clips = []
            
            for i, segment in enumerate(video_map, 1):
                clip_path = os.path.join('assets', f"clip_{i}.mp4")
                if os.path.exists(clip_path):
                    duration = segment['end_time'] - segment['start_time']
                    output_path = os.path.join('temp', f"processed_{i}.mp4")
                    if process_clip(clip_path, output_path, duration, i, len(video_map)):
                        processed_clips.append(output_path)
            
            concat_file = create_concat_file(processed_clips)
            temp_video = os.path.join('temp', 'concatenated.mp4')
            concatenate_videos(concat_file, temp_video)
            
            draft_output = 'draft_video.mp4'
            add_audio(temp_video, audio_path, draft_output)
            
            progress_bar.progress(80)
            st.success("✓ Video assembled")
            
            # Step 4: Add captions (if checked)
            final_output = draft_output
            
            if add_captions:
                status_text.text("✍️ Step 4/4: Adding professional captions...")
                progress_bar.progress(85)
                
                word_segments = create_word_segments(video_map)
                subtitle_file = create_ass_subtitle(word_segments)
                
                final_output = 'final_output.mp4'
                logo_for_caption = logo_path if logo_path and os.path.exists(logo_path) else 'logo.png'
                burn_subtitles_and_logo(draft_output, subtitle_file, logo_for_caption, final_output)
                
                st.success("✓ Captions added")
            else:
                status_text.text("✓ Step 4/4: Skipped (captions not requested)")
            
            progress_bar.progress(100)
            
            # Success message
            st.markdown('<div class="success-box"><h2>🎉 Video Generated Successfully!</h2></div>', unsafe_allow_html=True)
            
            # Video info
            video_duration = get_video_duration(final_output)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{video_duration:.1f}s")
            with col2:
                st.metric("Segments", len(video_map))
            with col3:
                st.metric("Resolution", "1080x1920")
            
            # Download button
            with open(final_output, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Video",
                    data=f,
                    file_name=final_output,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # Video preview
            st.video(final_output)
            
            # Cleanup
            cleanup_temp_files()
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Made with ❤️ by ChitraAI | Powered by Groq, Pexels & FFmpeg</p>",
    unsafe_allow_html=True
)
