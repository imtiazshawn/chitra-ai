import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def transcribe_audio(audio_path):
    """Transcribe audio file using Groq's Whisper model."""
    print(f"Transcribing audio: {audio_path}")
    
    with open(audio_path, 'rb') as audio_file:
        transcript = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            response_format="verbose_json"
        )
    
    print("Transcription complete")
    return transcript


def create_video_map(transcript):
    """Use Groq's Llama model to create a structured video map."""
    print("Creating video map with Llama-3.3...")
    
    # Get total audio duration
    total_duration = transcript.segments[-1]['end'] if transcript.segments else 0
    
    # Prepare transcript text with timestamps
    segments_text = "\n".join([
        f"[{seg['start']:.2f}s - {seg['end']:.2f}s]: {seg['text']}"
        for seg in transcript.segments
    ])
    
    prompt = f"""You are a video editor AI. Analyze this timestamped transcript and create a video map.

Transcript (Total Duration: {total_duration:.2f} seconds):
{segments_text}

CRITICAL REQUIREMENTS:
1. Create segments that cover the ENTIRE audio from 0 to {total_duration:.2f} seconds
2. Each segment should be 5-10 seconds long
3. The LAST segment MUST end at exactly {total_duration:.2f} seconds
4. NO GAPS between segments - they must be continuous

For each segment provide:
- start_time: float (seconds) - must start where previous segment ended
- end_time: float (seconds) - must be continuous, last segment ends at {total_duration:.2f}
- transcript_text: string (the spoken words in this segment)
- search_queries: array of 3 search query variations (e.g., ["business meeting", "office work", "professional workspace"])
- fallback_topic: string (generic fallback like "abstract tech", "nature", "city life", "people")
- caption_style: string (one of: "energetic", "calm", "professional", "dramatic", "playful")

Choose search_queries based on what would visually represent the content with variations.
Choose fallback_topic as a safe generic option if specific searches fail.

Return ONLY valid JSON array, no markdown or explanation."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a video editing assistant that outputs only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    # Extract JSON from response
    response_text = response.choices[0].message.content.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith('```'):
        response_text = response_text[3:-3].strip()
    
    video_map = json.loads(response_text)
    
    # Validate and fix video map to ensure full coverage
    video_map = validate_and_fix_video_map(video_map, total_duration)
    
    print(f"Video map created with {len(video_map)} segments")
    print(f"Coverage: 0s to {video_map[-1]['end_time']:.2f}s (Audio: {total_duration:.2f}s)")
    return video_map


def validate_and_fix_video_map(video_map, total_duration):
    """Validate video map covers full duration and fix if needed."""
    if not video_map:
        return video_map
    
    # Check if last segment ends before audio ends
    last_end = video_map[-1]['end_time']
    
    if last_end < total_duration - 0.1:  # More than 0.1s gap (stricter)
        print(f"Warning: Video map ends at {last_end:.2f}s but audio is {total_duration:.2f}s")
        print(f"Extending last segment to cover full duration...")
        
        # Extend the last segment to cover remaining time
        video_map[-1]['end_time'] = total_duration
        
        # If gap is too large (>5s), add a new segment
        gap = total_duration - last_end
        if gap > 5:
            video_map.append({
                'start_time': last_end,
                'end_time': total_duration,
                'transcript_text': video_map[-1]['transcript_text'],  # Reuse last text
                'search_queries': video_map[-1]['search_queries'],
                'fallback_topic': video_map[-1]['fallback_topic'],
                'caption_style': video_map[-1]['caption_style']
            })
            print(f"Added extra segment to fill {gap:.2f}s gap")
    elif last_end > total_duration + 0.1:  # Video map is longer than audio
        print(f"Warning: Video map ends at {last_end:.2f}s but audio is only {total_duration:.2f}s")
        print(f"Trimming last segment to match audio duration...")
        video_map[-1]['end_time'] = total_duration
    
    return video_map


def save_video_map(video_map, output_path="video_map_long.json"):
    """Save video map to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(video_map, f, indent=2, ensure_ascii=False)
    print(f"Video map saved to {output_path}")


def main():
    audio_file = input("Enter the path to your MP3 file: ").strip()
    
    if not os.path.exists(audio_file):
        print(f"Error: File not found: {audio_file}")
        return
    
    # Step 1: Transcribe audio
    transcript = transcribe_audio(audio_file)
    
    # Step 2: Create video map
    video_map = create_video_map(transcript)
    
    # Step 3: Save to JSON
    save_video_map(video_map)
    
    print("\n✓ Process complete!")
    print(f"✓ Total segments: {len(video_map)}")
    print(f"✓ Output: video_map_long.json")


if __name__ == '__main__':
    main()
