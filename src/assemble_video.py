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
    return float(result.stdout.strip())


def process_clip(input_path, output_path, duration, clip_number, total_clips):
    """Trim and resize clip to 1080x1920 (9:16 aspect ratio)."""
    print(f"  [{clip_number}/{total_clips}] Processing {os.path.basename(input_path)}...")
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-t', str(duration),  # Trim to exact duration
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',  # Resize and crop
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-an',  # Remove audio from clips
        '-y',  # Overwrite output
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Warning: Error processing clip {clip_number}")
        return False
    
    return True


def create_concat_file(processed_clips):
    """Create FFmpeg concat file."""
    concat_file = os.path.join(TEMP_FOLDER, 'concat_list.txt')
    
    with open(concat_file, 'w') as f:
        for clip in processed_clips:
            # Use relative path and escape special characters
            clip_path = clip.replace('\\', '/')
            f.write(f"file '../{clip_path}'\n")
    
    return concat_file


def concatenate_videos(concat_file, output_path):
    """Concatenate all processed clips."""
    print("\n  Concatenating all clips...")
    
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        '-y',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error concatenating videos: {result.stderr}")
        return False
    
    return True


def add_audio(video_path, audio_path, output_path):
    """Add audio to video and ensure sync."""
    print("\n  Adding audio track...")
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',  # Match shortest stream (ensures sync)
        '-y',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error adding audio: {result.stderr}")
        return False
    
    return True


def cleanup_temp_files():
    """Remove temporary files."""
    if os.path.exists(TEMP_FOLDER):
        for file in os.listdir(TEMP_FOLDER):
            os.remove(os.path.join(TEMP_FOLDER, file))
        os.rmdir(TEMP_FOLDER)


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
    
    # Process each clip
    print("Step 1: Processing clips (trim & resize to 1080x1920)...\n")
    processed_clips = []
    
    for i, segment in enumerate(video_map, 1):
        clip_path = os.path.join(ASSETS_FOLDER, f"clip_{i}.mp4")
        
        if not os.path.exists(clip_path):
            print(f"  Warning: {clip_path} not found, skipping...")
            continue
        
        duration = segment['end_time'] - segment['start_time']
        output_path = os.path.join(TEMP_FOLDER, f"processed_{i}.mp4")
        
        if process_clip(clip_path, output_path, duration, i, len(video_map)):
            processed_clips.append(output_path)
    
    if not processed_clips:
        print("\nError: No clips were processed successfully")
        return
    
    print(f"\n✓ Processed {len(processed_clips)}/{len(video_map)} clips")
    
    # Concatenate clips
    print("\nStep 2: Concatenating clips...")
    concat_file = create_concat_file(processed_clips)
    temp_video = os.path.join(TEMP_FOLDER, 'concatenated.mp4')
    
    if not concatenate_videos(concat_file, temp_video):
        print("Error: Failed to concatenate videos")
        return
    
    print("✓ Clips concatenated")
    
    # Add audio
    print("\nStep 3: Adding audio and syncing...")
    if not add_audio(temp_video, audio_file, OUTPUT_VIDEO):
        print("Error: Failed to add audio")
        return
    
    print(f"✓ Audio added and synced")
    
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
        
        if abs(video_duration - audio_duration) < 0.5:
            print("✓ Perfect sync!")
    
    # Cleanup
    print("\nCleaning up temporary files...")
    cleanup_temp_files()
    print("✓ Cleanup complete")


if __name__ == '__main__':
    main()
