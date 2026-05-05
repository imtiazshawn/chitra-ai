import os
import json
import subprocess
import sys

ASSETS_FOLDER = 'assets'
TEMP_FOLDER = 'temp'
OUTPUT_VIDEO = 'draft_video.mp4'


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg is not installed or not in PATH")
        print("Download from: https://ffmpeg.org/download.html")
        return False


def create_temp_folder():
    """Create temp folder for processed clips."""
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
        print(f"✓ Created {TEMP_FOLDER} folder")


def get_video_duration(video_path):
    """Get video duration using FFprobe."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0.0


def create_fallback_clip(duration, output_path):
    """Create a black fallback clip with specified duration."""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=black:s=1080x1920:d={duration}:r=30',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-y',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)


def assemble_video_with_complex_filter(video_map, audio_path, output_path):
    """Assemble video using FFmpeg with infinite looping for perfect sync."""
    print("\nAssembling video with infinite loop sync...")
    
    # Get exact audio duration using ffprobe
    cmd_probe = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(cmd_probe, capture_output=True, text=True)
    audio_duration = float(result.stdout.strip())
    print(f"  Audio duration: {audio_duration:.2f}s")
    
    # Prepare inputs with stream_loop for infinite looping
    inputs = []
    filter_parts = []
    
    for i, segment in enumerate(video_map):
        clip_path = os.path.join(ASSETS_FOLDER, f"clip_{i+1}.mp4")
        duration = segment['end_time'] - segment['start_time']
        
        # Check if clip exists, create fallback if not
        if not os.path.exists(clip_path):
            print(f"  Warning: {clip_path} not found, creating fallback...")
            clip_path = os.path.join(TEMP_FOLDER, f"fallback_{i+1}.mp4")
            create_fallback_clip(duration, clip_path)
        
        # Add stream_loop -1 for infinite looping BEFORE -i
        inputs.extend(['-stream_loop', '-1', '-i', clip_path])
        
        # Build filter with consistent 30fps and proper format
        filter_parts.append(
            f"[{i}:v]trim=start=0:end={duration},setpts=PTS-STARTPTS,"
            f"fps=30,format=yuv420p,scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1[v{i}]"
        )
    
    # Concatenate all processed clips
    concat_inputs = ''.join([f"[v{i}]" for i in range(len(video_map))])
    filter_complex = ';'.join(filter_parts) + f";{concat_inputs}concat=n={len(video_map)}:v=1:a=0[outv]"
    
    # Build FFmpeg command with proper sync flags
    cmd = [
        'ffmpeg',
        *inputs,
        '-i', audio_path,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', f'{len(video_map)}:a',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-r', '30',              # Force consistent 30fps
        '-fflags', '+genpts',    # Generate presentation timestamps
        '-async', '1',           # Force audio-video sync
        '-shortest',             # End when shortest stream (audio) ends
        '-y',
        output_path
    ]
    
    print(f"  Processing {len(video_map)} clips with infinite loop...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    
    return True


def cleanup_temp_files():
    """Remove temporary files."""
    if os.path.exists(TEMP_FOLDER):
        for file in os.listdir(TEMP_FOLDER):
            try:
                os.remove(os.path.join(TEMP_FOLDER, file))
            except:
                pass
        try:
            os.rmdir(TEMP_FOLDER)
        except:
            pass


def main():
    print("=== Video Assembly with FFmpeg ===\n")
    
    # Check FFmpeg
    if not check_ffmpeg():
        return
    
    # Get audio file
    audio_file = input("Enter the path to your audio file (MP3/WAV): ").strip()
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return
    
    # Load video map
    if not os.path.exists('video_map.json'):
        print("Error: video_map.json not found")
        return
    
    with open('video_map.json', 'r', encoding='utf-8') as f:
        video_map = json.load(f)
    
    print(f"Loaded video map with {len(video_map)} segments\n")
    
    # Create temp folder
    create_temp_folder()
    
    # Check which clips exist
    existing_clips = 0
    for i in range(1, len(video_map) + 1):
        clip_path = os.path.join(ASSETS_FOLDER, f"clip_{i}.mp4")
        if os.path.exists(clip_path):
            existing_clips += 1
    
    print(f"Found {existing_clips}/{len(video_map)} clips in assets folder")
    if existing_clips < len(video_map):
        print(f"Missing clips will be replaced with black fallback clips\n")
    
    # Assemble video with complex filter
    print("Assembling video with perfect sync...")
    
    if not assemble_video_with_complex_filter(video_map, audio_file, OUTPUT_VIDEO):
        print("Error: Failed to assemble video")
        return
    
    # Verify output
    if os.path.exists(OUTPUT_VIDEO):
        video_duration = get_video_duration(OUTPUT_VIDEO)
        audio_duration = get_video_duration(audio_file)
        
        print(f"\n{'='*40}")
        print(f"✓ Video created successfully!")
        print(f"✓ Output: {OUTPUT_VIDEO}")
        print(f"✓ Video duration: {video_duration:.2f}s")
        print(f"✓ Audio duration: {audio_duration:.2f}s")
        print(f"✓ Sync difference: {abs(video_duration - audio_duration):.2f}s")
        
        if abs(video_duration - audio_duration) < 0.1:
            print("✓ Perfect sync!")
    
    # Cleanup
    print("\nCleaning up temporary files...")
    cleanup_temp_files()
    print("✓ Cleanup complete")


if __name__ == '__main__':
    main()
