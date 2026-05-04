import os
import json
import subprocess
import re


def format_time_ass(seconds):
    """Convert seconds to ASS subtitle format (h:mm:ss.cs)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def get_highlight_color(caption_style):
    """Get highlight color based on caption style."""
    color_map = {
        'energetic': '&H00FFFF00',  # Bright Yellow
        'calm': '&H00FFB6C1',       # Light Pink
        'professional': '&H0000D4FF', # Cyan
        'dramatic': '&H000000FF',   # Red
        'playful': '&H00FF00FF',    # Magenta
        'tech': '&H0000FF00'        # Neon Green
    }
    return color_map.get(caption_style, '&H0000FFFF')  # Default: Yellow


def split_into_word_chunks(text, max_words=3):
    """Split text into chunks of max_words."""
    words = text.strip().split()
    chunks = []
    
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    
    return chunks


def create_word_segments(video_map):
    """Create word-level segments with equal time distribution."""
    word_segments = []
    
    for segment in video_map:
        text = segment.get('transcript_text', '').strip()
        if not text:
            continue
        
        start_time = segment['start_time']
        end_time = segment['end_time']
        caption_style = segment.get('caption_style', 'professional')
        
        # Split into word chunks
        chunks = split_into_word_chunks(text, max_words=3)
        
        if not chunks:
            continue
        
        # Distribute time equally
        total_duration = end_time - start_time
        chunk_duration = total_duration / len(chunks)
        
        for i, chunk in enumerate(chunks):
            chunk_start = start_time + (i * chunk_duration)
            chunk_end = chunk_start + chunk_duration
            
            word_segments.append({
                'text': chunk,
                'start': chunk_start,
                'end': chunk_end,
                'style': caption_style
            })
    
    return word_segments


def create_dynamic_highlight_subtitles(word_segments, output_file='captions.ass'):
    """Create ASS subtitle with dynamic word-level highlighting."""
    print("Creating dynamic highlight subtitle file...")
    
    # ASS file header with larger base font size (increased by 15%)
    ass_content = """[Script Info]
Title: AI Video Captions - Dynamic Highlight
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Inter,32,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1,2,50,50,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Add each word segment with dynamic highlighting
    for segment in word_segments:
        words = segment['text'].split()
        start = segment['start']
        end = segment['end']
        duration = end - start
        word_duration = duration / len(words)
        
        highlight_color = get_highlight_color(segment['style'])
        
        # Create individual subtitle for each word timing
        for word_idx, word in enumerate(words):
            word_start = start + (word_idx * word_duration)
            word_end = word_start + word_duration
            
            # Build the text with highlighting for current word
            formatted_words = []
            for i, w in enumerate(words):
                if i == word_idx:
                    # Active word: larger size (120%) and highlight color with pop effect
                    formatted_words.append(
                        f"{{\\fscx120\\fscy120\\c{highlight_color}\\t(0,100,\\fscx125\\fscy125)\\t(100,200,\\fscx120\\fscy120)}}{w.upper()}{{\\r}}"
                    )
                else:
                    # Inactive words: normal size and white
                    formatted_words.append(w.upper())
            
            text = ' '.join(formatted_words)
            
            start_time = format_time_ass(word_start)
            end_time = format_time_ass(word_end)
            
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    print(f"✓ Dynamic highlight subtitle file created: {output_file}")
    return output_file


def burn_subtitles_and_logo(input_video, subtitle_file, logo_path, output_video):
    """Burn subtitles and overlay logo using FFmpeg."""
    print("\nBurning dynamic subtitles and adding logo overlay...")
    
    # Check if logo exists
    if not os.path.exists(logo_path):
        print(f"Warning: Logo file not found: {logo_path}")
        print("Proceeding without logo overlay...")
        has_logo = False
    else:
        has_logo = True
    
    # Escape paths for FFmpeg
    subtitle_file_escaped = subtitle_file.replace('\\', '/').replace(':', '\\:')
    
    if has_logo:
        # With logo overlay
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-i', logo_path,
            '-filter_complex',
            f"[0:v]ass={subtitle_file_escaped}[v];[v][1:v]overlay=W-w-30:30:format=auto,format=yuv420p[outv]",
            '-map', '[outv]',
            '-map', '0:a?',
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-shortest',  # Prevent trailing frames
            '-y',
            output_video
        ]
    else:
        # Without logo overlay
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-vf', f"ass={subtitle_file_escaped},format=yuv420p",
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-shortest',  # Prevent trailing frames
            '-y',
            output_video
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: FFmpeg failed")
        print(f"Error details: {result.stderr}")
        return False
    
    return True


def main():
    print("=== Dynamic Caption Generator ===\n")
    
    # Check for required files
    input_video = 'draft_video.mp4'
    if not os.path.exists(input_video):
        print(f"Error: {input_video} not found")
        return
    
    if not os.path.exists('video_map.json'):
        print("Error: video_map.json not found")
        return
    
    # Load video map
    with open('video_map.json', 'r', encoding='utf-8') as f:
        video_map = json.load(f)
    
    print(f"Loaded video map with {len(video_map)} segments\n")
    
    # Create word-level segments
    print("Step 1: Creating word-level segments...")
    word_segments = create_word_segments(video_map)
    print(f"✓ Created {len(word_segments)} word segments (max 3 words each)\n")
    
    # Create dynamic highlight subtitle file
    print("Step 2: Generating dynamic highlight subtitle file...")
    subtitle_file = create_dynamic_highlight_subtitles(word_segments)
    print()
    
    # Check for logo
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        print(f"✓ Logo found: {logo_path}")
    else:
        print(f"ℹ Logo not found: {logo_path} (will proceed without logo)")
    
    # Burn subtitles and add logo
    print("\nStep 3: Burning subtitles and overlaying logo...")
    output_video = 'final_output.mp4'
    
    if burn_subtitles_and_logo(input_video, subtitle_file, logo_path, output_video):
        print(f"\n{'='*40}")
        print(f"✓ Video created successfully!")
        print(f"✓ Output: {output_video}")
        print(f"✓ Captions: Dynamic word-level highlighting")
        print(f"✓ Style: Professional with pop animation")
        if os.path.exists(logo_path):
            print(f"✓ Logo: Top-right corner overlay")
        print(f"\n🎬 Your video is ready for upload!")
    else:
        print("\n✗ Failed to create final video")


if __name__ == '__main__':
    main()
