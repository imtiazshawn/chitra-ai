import os
import json
import subprocess
from collections import Counter

# ============================================================================
# GLOBAL THEME PALETTE - Professional Long Video Standard (16:9)
# ============================================================================

GLOBAL_THEME_PALETTE = {
    'energetic': {
        'color': '&H0000FFFF',  # Bright Yellow (BGR format)
        'font': 'Montserrat ExtraBold'
    },
    'calm': {
        'color': '&H00FFB6C1',  # Soft Blue
        'font': 'Inter'
    },
    'professional': {
        'color': '&H0000D4FF',  # Orange
        'font': 'Inter Black'
    },
    'dramatic': {
        'color': '&H000000FF',  # Red
        'font': 'Montserrat ExtraBold'
    },
    'playful': {
        'color': '&H00FF00FF',  # Magenta
        'font': 'Komika Axis'
    },
    'aggressive': {
        'color': '&H0000D4FF',  # Electric Orange
        'font': 'Montserrat ExtraBold'
    },
    'modern': {
        'color': '&H00FFAA00',  # Electric Blue
        'font': 'Inter Black'
    }
}

# Fallback fonts in order of preference
FONT_FALLBACK_LIST = [
    'Montserrat ExtraBold',
    'Inter Black',
    'The Bold Font',
    'Komika Axis',
    'Arial Black',
    'Impact'
]

# Professional Long Video Standards (16:9)
BASE_FONT_SIZE = 56  # Eye-catching size for desktop/TV
OUTLINE_WIDTH = 3.0  # 3px black outline for visibility
SHADOW_DEPTH = 1.5   # Subtle drop shadow
SAFE_ZONE_MARGIN = 120  # Vertical margin (safe zone for 16:9)
PASSIVE_WORD_OPACITY = 217  # 85% opacity for passive words (255 * 0.85)
ACTIVE_SCALE_BOOST = 115  # 15% size increase for active word

# ============================================================================


def format_time_ass(seconds):
    """Convert seconds to ASS subtitle format (h:mm:ss.cs)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def detect_video_vibe(video_map):
    """Detect the dominant vibe from video_map caption styles."""
    styles = [seg.get('caption_style', 'professional') for seg in video_map]
    if not styles:
        return 'professional'
    
    # Get most common style
    style_counts = Counter(styles)
    dominant_style = style_counts.most_common(1)[0][0]
    return dominant_style


def get_global_theme(video_vibe):
    """Get global theme (color + font) for entire video based on vibe."""
    theme = GLOBAL_THEME_PALETTE.get(video_vibe, GLOBAL_THEME_PALETTE['professional'])
    return theme['color'], theme['font']


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


def create_dynamic_highlight_subtitles(word_segments, video_map, output_file='captions_long.ass', audio_duration=None):
    """Create professional ASS subtitle with global theme and dynamic word-level highlighting."""
    print("Creating professional dynamic subtitle file (16:9)...")
    
    # Get audio duration from video_map if not provided
    if audio_duration is None and video_map:
        audio_duration = max(seg['end_time'] for seg in video_map)
    
    # Detect video vibe and get global theme
    video_vibe = detect_video_vibe(video_map)
    primary_highlight_color, global_font = get_global_theme(video_vibe)
    
    print(f"  Video Vibe: {video_vibe}")
    print(f"  Global Font: {global_font}")
    print(f"  Highlight Color: {primary_highlight_color}")
    if audio_duration:
        print(f"  Audio Duration: {audio_duration:.2f}s")
    
    # Convert passive opacity to ASS alpha format (inverted: 255 = transparent, 0 = opaque)
    passive_alpha = 255 - PASSIVE_WORD_OPACITY
    passive_color = f"&H{passive_alpha:02X}FFFFFF"  # White with 85% opacity
    
    # ASS file header with professional standards (16:9 resolution)
    ass_content = f"""[Script Info]
Title: ChitraAI Professional Captions (16:9)
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{global_font},{BASE_FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{OUTLINE_WIDTH},{SHADOW_DEPTH},2,50,50,{SAFE_ZONE_MARGIN},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    last_subtitle_end = 0
    
    # Add each word segment with dynamic highlighting
    for segment in word_segments:
        words = segment['text'].split()
        start = segment['start']
        end = segment['end']
        duration = end - start
        word_duration = duration / len(words)
        
        # Create individual subtitle for each word timing
        for word_idx, word in enumerate(words):
            word_start = start + (word_idx * word_duration)
            word_end = word_start + word_duration
            
            # Track last subtitle timestamp
            if word_end > last_subtitle_end:
                last_subtitle_end = word_end
            
            # Build the text with highlighting for current word
            formatted_words = []
            for i, w in enumerate(words):
                if i == word_idx:
                    # ACTIVE WORD: Pop effect with global highlight color
                    formatted_words.append(
                        f"{{\\c{primary_highlight_color}\\fscx100\\fscy100"
                        f"\\t(0,150,\\fscx{ACTIVE_SCALE_BOOST}\\fscy{ACTIVE_SCALE_BOOST})}}"
                        f"{w.upper()}{{\\r}}"
                    )
                else:
                    # PASSIVE WORDS: White with 85% opacity
                    formatted_words.append(
                        f"{{\\c{passive_color}}}{w.upper()}{{\\r}}"
                    )
            
            text = ' '.join(formatted_words)
            start_time = format_time_ass(word_start)
            end_time = format_time_ass(word_end)
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
    
    # Verify subtitle coverage matches audio duration
    if audio_duration and last_subtitle_end < audio_duration:
        print(f"  Warning: Subtitles end at {last_subtitle_end:.2f}s but audio is {audio_duration:.2f}s")
        print(f"  Gap: {audio_duration - last_subtitle_end:.2f}s (this is normal for ending silence)")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    print(f"✓ Professional subtitle file created: {output_file}")
    print(f"  Font Size: {BASE_FONT_SIZE}px (Desktop-optimized)")
    print(f"  Outline: {OUTLINE_WIDTH}px black")
    print(f"  Shadow: {SHADOW_DEPTH}px depth")
    print(f"  Safe Zone: {SAFE_ZONE_MARGIN}px margin")
    print(f"  Last subtitle: {last_subtitle_end:.2f}s")
    return output_file


def burn_subtitles_and_logo(input_video, subtitle_file, logo_path, output_video):
    """Burn subtitles and overlay logo using FFmpeg."""
    print("\nBurning dynamic subtitles and adding logo overlay...")
    
    # Get exact duration from draft video to preserve it
    cmd_probe = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_video
    ]
    result = subprocess.run(cmd_probe, capture_output=True, text=True)
    try:
        video_duration = float(result.stdout.strip())
    except:
        video_duration = None
    
    if not os.path.exists(logo_path):
        print(f"Warning: Logo file not found: {logo_path}")
        print("Proceeding without logo overlay...")
        has_logo = False
    else:
        has_logo = True
    
    subtitle_file_escaped = subtitle_file.replace('\\', '/').replace(':', '\\:')
    
    # Base flags for strict duration enforcement
    duration_flags = ['-t', str(video_duration)] if video_duration else []
    
    if has_logo:
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
            '-fflags', '+genpts',
            '-async', '1',
            *duration_flags,
            '-y',
            output_video
        ]
    else:
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-vf', f"ass={subtitle_file_escaped},format=yuv420p",
            '-c:a', 'copy',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-fflags', '+genpts',
            '-async', '1',
            *duration_flags,
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
    print("=== Dynamic Caption Generator (16:9) ===\n")
    
    # Check for required files
    input_video = 'draft_video_long.mp4'
    if not os.path.exists(input_video):
        print(f"Error: {input_video} not found")
        return
    
    if not os.path.exists('video_map_long.json'):
        print("Error: video_map_long.json not found")
        return
    
    # Load video map
    with open('video_map_long.json', 'r', encoding='utf-8') as f:
        video_map = json.load(f)
    
    print(f"Loaded video map with {len(video_map)} segments\n")
    
    # Create word-level segments
    print("Step 1: Creating word-level segments...")
    word_segments = create_word_segments(video_map)
    print(f"✓ Created {len(word_segments)} word segments (max 3 words each)\n")
    
    # Create professional dynamic highlight subtitle file
    print("Step 2: Generating professional subtitle file with global theme...")
    subtitle_file = create_dynamic_highlight_subtitles(word_segments, video_map)
    print()
    
    # Check for logo
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        print(f"✓ Logo found: {logo_path}")
    else:
        print(f"ℹ Logo not found: {logo_path} (will proceed without logo)")
    
    # Burn subtitles and add logo
    print("\nStep 3: Burning subtitles and overlaying logo...")
    output_video = 'final_output_long.mp4'
    
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
