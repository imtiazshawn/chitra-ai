"""Pipeline execution logic for ChitraAI (16:9 Long Video)"""
import os
import time
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from workspace_manager import create_unique_project_folder, get_project_paths, cleanup_project_temp
from main import transcribe_audio, create_video_map
from assemble_video_long import get_video_duration

def run_pipeline_long(audio_file, logo_file, add_captions_flag, log_placeholder, output_placeholder):
    """Execute the full video generation pipeline for 16:9 format"""
    
    # Create unique project folder
    project_folder, project_id = create_unique_project_folder("long_16x9")
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
        
        successful = sum(1 for i, segment in enumerate(video_map, 1) if download_video_to_project_long(segment, i, paths['assets']))
        
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
        
        assemble_video_long(video_map, paths['audio'], paths['draft_video'], paths['assets'], paths['temp'])
        
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
                <div class="log-content" style="color: #FF6B35;">// [AGENT 04] Adding captions...</div>
            </div>
            """, unsafe_allow_html=True)
            
            from add_captions_long import create_word_segments, create_dynamic_highlight_subtitles, burn_subtitles_and_logo
            
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

def download_video_to_project_long(segment, clip_number, assets_folder):
    """Download landscape video for a segment to specific assets folder."""
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    
    search_queries = segment.get('search_queries', [])
    fallback_topic = segment.get('fallback_topic', 'abstract')
    all_queries = search_queries + [fallback_topic]
    
    for query in all_queries:
        # Search Pexels for landscape videos
        url = 'https://api.pexels.com/videos/search'
        headers = {'Authorization': PEXELS_API_KEY}
        params = {'query': query, 'orientation': 'landscape', 'per_page': 15}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            videos = response.json().get('videos', [])
            
            # Filter and sort by duration (prefer longer clips 15+ seconds)
            suitable_videos = []
            for video in videos:
                video_files = video.get('video_files', [])
                landscape_files = [vf for vf in video_files if vf.get('width', 0) > vf.get('height', 0)]
                
                if landscape_files:
                    landscape_files.sort(key=lambda x: x.get('width', 0), reverse=True)
                    best_file = landscape_files[0]
                    duration = video.get('duration', 0)
                    suitable_videos.append({
                        'url': best_file.get('link'),
                        'duration': duration
                    })
            
            # Sort by duration (longest first)
            suitable_videos.sort(key=lambda x: x['duration'], reverse=True)
            
            # Try to download
            for video_info in suitable_videos:
                video_url = video_info['url']
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

def preprocess_clip_long(clip_path, required_duration, output_path):
    """Pre-process clip to exact duration by looping if needed."""
    clip_duration = get_video_duration(clip_path)
    
    if clip_duration >= required_duration:
        # Clip is long enough, just trim it
        cmd = [
            'ffmpeg', '-i', clip_path,
            '-t', str(required_duration),
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac', '-y', output_path
        ]
    else:
        # Clip is too short, loop it to exact duration
        loop_count = int(required_duration / clip_duration) + 2  # Extra loops for safety
        cmd = [
            'ffmpeg',
            '-stream_loop', str(loop_count),
            '-i', clip_path,
            '-t', str(required_duration),
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-c:a', 'aac', '-y', output_path
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def assemble_video_long(video_map, audio_path, output_path, assets_folder, temp_folder):
    """Assemble video from clips in specific project folder (16:9 format)."""
    
    # Get audio duration
    audio_duration = get_video_duration(audio_path)
    
    # Calculate total video duration from segments
    total_video_duration = sum(seg['end_time'] - seg['start_time'] for seg in video_map)
    
    print(f"Audio duration: {audio_duration:.2f}s")
    print(f"Video segments total: {total_video_duration:.2f}s")
    
    # Step 1: Pre-process all clips to exact durations
    processed_clips = []
    for i, segment in enumerate(video_map):
        clip_path = os.path.join(assets_folder, f"clip_{i+1}.mp4")
        required_duration = segment['end_time'] - segment['start_time']
        processed_path = os.path.join(temp_folder, f"processed_{i+1}.mp4")
        
        # Create fallback if clip doesn't exist
        if not os.path.exists(clip_path):
            cmd = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'color=c=black:s=1920x1080:d={required_duration}:r=30',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-y', processed_path
            ]
            subprocess.run(cmd, capture_output=True)
        else:
            # Pre-process clip to exact duration
            preprocess_clip_long(clip_path, required_duration, processed_path)
        
        processed_clips.append(processed_path)
    
    # Step 2: Simple assembly - scale, crop, and concat
    inputs = []
    filter_parts = []
    
    for i, processed_clip in enumerate(processed_clips):
        inputs.extend(['-i', processed_clip])
        
        # Simple scale and crop for 16:9 (no trim needed - already exact duration)
        filter_parts.append(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,fps=30,format=yuv420p,setsar=1[v{i}]"
        )
    
    # Concatenate all clips and trim to exact audio duration
    concat_inputs = ''.join([f"[v{i}]" for i in range(len(processed_clips))])
    filter_complex = ';'.join(filter_parts) + f";{concat_inputs}concat=n={len(processed_clips)}:v=1:a=0[concat];[concat]trim=duration={audio_duration},setpts=PTS-STARTPTS,fps=30[outv]"
    
    cmd = [
        'ffmpeg',
        *inputs,
        '-i', audio_path,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', f'{len(processed_clips)}:a',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'copy',
        '-r', '30',
        '-y', output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Video assembly failed: {result.stderr}")
    
    return output_path
