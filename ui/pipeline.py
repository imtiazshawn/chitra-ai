"""Pipeline execution logic for ChitraAI"""
import os
import time
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from workspace_manager import create_unique_project_folder, get_project_paths, cleanup_project_temp
from main import transcribe_audio, create_video_map
from download_videos import find_and_download_video
from assemble_video import get_video_duration
from add_captions import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo

def run_pipeline(audio_file, logo_file, add_captions_flag, log_placeholder, output_placeholder):
    """Execute the full video generation pipeline"""
    
    # Create unique project folder
    project_folder, project_id = create_unique_project_folder("reels_9x16")
    paths = get_project_paths(project_folder)
    
    # Save uploaded audio
    with open(paths['audio'], 'wb') as f:
        f.write(audio_file.read())
    
    # Save logo if provided
    if logo_file:
        with open(paths['logo'], 'wb') as f:
            f.write(logo_file.read())
    
    try:
        # Step 1: Transcription
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF6B35;">// [AGENT 01] Transcribing audio...</div>
        </div>
        """, unsafe_allow_html=True)
        
        transcript = transcribe_audio(paths['audio'])
        video_map = create_video_map(transcript)
        
        # Save video map
        import json
        with open(paths['video_map'], 'w', encoding='utf-8') as f:
            json.dump(video_map, f, indent=2, ensure_ascii=False)
        
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
        
        successful = sum(1 for i, segment in enumerate(video_map, 1) if download_video_to_project(segment, i, paths['assets']))
        
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
        
        assemble_video(video_map, paths['audio'], paths['draft_video'], paths['assets'], paths['temp'])
        
        log_placeholder.markdown("""
        <div class="system-log">
            <div class="log-title">// SYSTEM LOG</div>
            <div class="log-content" style="color: #FF6B35;">// [AGENT 03] ✓ Video assembled</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step 4: Add captions (if checked)
        final_output = paths['draft_video']
        
        if add_captions_flag:
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 04] Adding dynamic captions...</div>
            </div>
            """, unsafe_allow_html=True)
            
            word_segments = create_word_segments(video_map)
            create_dynamic_highlight_subtitles(word_segments, video_map, paths['captions'])
            
            final_output = paths['final_output']
            logo_for_caption = paths['logo'] if os.path.exists(paths['logo']) else None
            burn_subtitles_and_logo(paths['draft_video'], paths['captions'], logo_for_caption, final_output)
            
            log_placeholder.markdown("""
            <div class="system-log">
                <div class="log-title">// SYSTEM LOG</div>
                <div class="log-content" style="color: #FF6B35;">// [AGENT 04] ✓ Captions added</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Success
        log_placeholder.markdown(f"""
        <div class="system-log">
            <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
            <div class="log-content" style="color: #FF6B35;">// ✓ PIPELINE COMPLETE</div>
            <div class="log-content" style="color: #888; margin-top: 0.5rem;">// Project: {project_id}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Cleanup
        cleanup_project_temp(project_folder)
        
        return final_output, len(video_map)
        
    except Exception as e:
        log_placeholder.markdown(f"""
        <div class="system-log">
            <div class="log-title terminal"><span class="term-dots"><span></span><span></span><span></span></span> SYSTEM LOG</div>
            <div class="log-content" style="color: #FF0080;">// ERROR: {str(e)}</div>
        </div>
        """, unsafe_allow_html=True)
        raise

def download_video_to_project(segment, clip_number, assets_folder):
    """Download video for a segment to specific assets folder."""
    import requests
    import time
    
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    
    search_queries = segment.get('search_queries', [])
    fallback_topic = segment.get('fallback_topic', 'abstract')
    all_queries = search_queries + [fallback_topic]
    
    for query in all_queries:
        # Search Pexels
        url = 'https://api.pexels.com/videos/search'
        headers = {'Authorization': PEXELS_API_KEY}
        params = {'query': query, 'orientation': 'portrait', 'per_page': 15}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            videos = response.json().get('videos', [])
            
            for video in videos:
                video_files = video.get('video_files', [])
                portrait_files = [vf for vf in video_files if vf.get('height', 0) > vf.get('width', 0)]
                
                if portrait_files:
                    portrait_files.sort(key=lambda x: x.get('height', 0), reverse=True)
                    video_url = portrait_files[0].get('link')
                    
                    if video_url:
                        filename = f"clip_{clip_number}.mp4"
                        filepath = os.path.join(assets_folder, filename)
                        
                        vid_response = requests.get(video_url, stream=True)
                        if vid_response.status_code == 200:
                            with open(filepath, 'wb') as f:
                                for chunk in vid_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            return True
        
        time.sleep(0.5)
    
    return False

def assemble_video(video_map, audio_path, output_path, assets_folder, temp_folder):
    """Assemble video from clips in specific project folder."""
    
    # Get audio duration
    audio_duration = get_video_duration(audio_path)
    
    inputs = []
    filter_parts = []
    
    for i, segment in enumerate(video_map):
        clip_path = os.path.join(assets_folder, f"clip_{i+1}.mp4")
        required_duration = segment['end_time'] - segment['start_time']
        
        # Create fallback if clip doesn't exist
        if not os.path.exists(clip_path):
            clip_path = os.path.join(temp_folder, f"fallback_{i+1}.mp4")
            cmd = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'color=c=black:s=1080x1920:d={required_duration}:r=30',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-y', clip_path
            ]
            subprocess.run(cmd, capture_output=True)
            clip_duration = required_duration
        else:
            clip_duration = get_video_duration(clip_path)
        
        # Use stream_loop for short clips
        if clip_duration < required_duration:
            inputs.extend(['-stream_loop', '-1', '-i', clip_path])
        else:
            inputs.extend(['-i', clip_path])
        
        # Trim and scale each clip
        filter_parts.append(
            f"[{i}:v]trim=duration={required_duration},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,fps=30,format=yuv420p[v{i}]"
        )
    
    # Concatenate all clips
    concat_inputs = ''.join([f"[v{i}]" for i in range(len(video_map))])
    filter_complex = ';'.join(filter_parts) + f";{concat_inputs}concat=n={len(video_map)}:v=1:a=0[outv]"
    
    cmd = [
        'ffmpeg',
        *inputs,
        '-i', audio_path,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', f'{len(video_map)}:a',
        '-t', str(audio_duration),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-r', '30',
        '-vsync', 'cfr',
        '-y', output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Video assembly failed: {result.stderr}")
    
    return output_path
