import os
import json
import subprocess
import sys

ASSETS_FOLDER = 'assets_long'
TEMP_FOLDER = 'temp_long'
OUTPUT_VIDEO = 'draft_video_long.mp4'


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
        '-i', f'color=c=black:s=1920x1080:d={duration}:r=30',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-y',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)


def assemble_video_with_complex_filter(video_map, audio_path, output_path):
    """Assemble video using FFmpeg with strict duration enforcement and seamless looping."""
    print("\nAssembling video with strict duration sync...")
    
    # Get exact audio duration using ffprobe
    cmd_probe = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(cmd_probe, capture_output=True, text=True)
    audio_duration = float(result.stdout.strip())
    print(f"  Audio duration: {audio_duration:.2f}s")
    
    inputs = []
    filter_parts = []
    total_video_duration = 0
    
    for i, segment in enumerate(video_map):
        clip_path = os.path.join(ASSETS_FOLDER, f"clip_{i+1}.mp4")
        required_duration = segment['end_time'] - segment['start_time']
        
        if not os.path.exists(clip_path):
            print(f"  Warning: {clip_path} not found, creating fallback...")
            clip_path = os.path.join(TEMP_FOLDER, f"fallback_{i+1}.mp4")
            create_fallback_clip(required_duration, clip_path)
            clip_duration = required_duration
        else:
            # Get actual clip duration
            clip_duration = get_video_duration(clip_path)
        
        total_video_duration += required_duration
        
        # If clip is shorter than required, we need seamless looping
        if clip_duration < required_duration:
            print(f"  Clip {i+1}: {clip_duration:.2f}s < {required_duration:.2f}s, enabling seamless loop")
            # Use stream_loop to ensure clip loops infinitely
            inputs.extend(['-stream_loop', '-1', '-i', clip_path])
        else:
            # Clip is long enough, no loop needed
            inputs.extend(['-i', clip_path])
        
        # Trim to exact duration, setpts to reset timestamps - 16:9 format (1920x1080)
        filter_parts.append(
            f"[{i}:v]trim=start=0:end={required_duration},setpts=PTS-STARTPTS,"
            f"fps=30,format=yuv420p,scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,setsar=1[v{i}]"
        )
    
    # Verify total video duration matches audio
    if total_video_duration < audio_duration:
        print(f"  Warning: Total video segments ({total_video_duration:.2f}s) < audio ({audio_duration:.2f}s)")
        print(f"  Gap: {audio_duration - total_video_duration:.2f}s will be filled with last clip loop")
    
    concat_inputs = ''.join([f"[v{i}]" for i in range(len(video_map))])
    filter_complex = ';'.join(filter_parts) + f";{concat_inputs}concat=n={len(video_map)}:v=1:a=0[outv]"
    
    cmd = [
        'ffmpeg',
        *inputs,
        '-i', audio_path,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', f'{len(video_map)}:a',
        '-t', str(audio_duration),   # Force exact output duration = audio duration
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-r', '30',
        '-fflags', '+genpts',
        '-async', '1',
        '-y',
        output_path
    ]
    
    print(f"  Processing {len(video_map)} clips → forcing {audio_duration:.2f}s output...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    
    # Verify output duration
    output_duration = get_video_duration(output_path)
    sync_diff = abs(output_duration - audio_duration)
    print(f"  Output: {output_duration:.2f}s | Sync diff: {sync_diff:.2f}s")
    
    if sync_diff < 0.1:
        print("  ✓ Perfect sync achieved!")
    
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
    print("=== Video Assembly with FFmpeg (16:9) ===\n")
    
    # Check FFmpeg
    if not check_ffmpeg():
        return
    
    # Get audio file
    audio_file = input("Enter the path to your audio file (MP3/WAV): ").strip()
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return
    
    # Load video map
    if not os.path.exists('video_map_long.json'):
        print("Error: video_map_long.json not found")
        return
    
    with open('video_map_long.json', 'r', encoding='utf-8') as f:
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
