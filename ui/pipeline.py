"""Pipeline execution logic for ChitraAI"""
import os
import time
import subprocess
from pathlib import Path

from main import transcribe_audio, create_video_map, save_video_map
from download_videos import create_assets_folder, find_and_download_video
from assemble_video import create_temp_folder, get_video_duration, cleanup_temp_files
from add_captions import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo

def run_pipeline(audio_file, logo_file, add_captions, log_placeholder, output_placeholder):
    """Execute the full video generation pipeline"""
    
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
        successful = sum(1 for i, segment in enumerate(video_map, 1) if find_and_download_video(segment, i))
        
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
        
        draft_output = assemble_video(video_map, audio_path)
        
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
            <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
            <div class="log-content" style="color: #FF6B35;">// ✓ PIPELINE COMPLETE</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Cleanup
        cleanup_temp_files()
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return final_output, len(video_map)
        
    except Exception as e:
        log_placeholder.markdown(f"""
        <div class="system-log">
            <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: {str(e)}</div>
        </div>
        """, unsafe_allow_html=True)
        raise

def assemble_video(video_map, audio_path):
    """Assemble video from clips"""
    create_temp_folder()
    
    inputs = []
    filter_parts = []
    
    for i, segment in enumerate(video_map):
        clip_path = os.path.join('assets', f"clip_{i+1}.mp4")
        duration = segment['end_time'] - segment['start_time']
        
        # Create fallback if clip doesn't exist
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
    
    return draft_output
