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
    
    # Prepare transcript text with timestamps
    segments_text = "\n".join([
        f"[{seg['start']:.2f}s - {seg['end']:.2f}s]: {seg['text']}"
        for seg in transcript.segments
    ])
    
    prompt = f"""You are a video editor AI. Analyze this timestamped transcript and create a video map.

Transcript:
{segments_text}

Create a JSON array where each segment is 5-10 seconds long. For each segment provide:
- start_time: float (seconds)
- end_time: float (seconds)
- transcript_text: string (the spoken words in this segment)
- visual_keyword: string (1-3 words describing ideal stock footage, e.g., "city skyline", "person working", "nature landscape")
- caption_style: string (one of: "energetic", "calm", "professional", "dramatic", "playful")

Choose caption_style based on the content tone. Choose visual_keyword based on what would visually represent the content.

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
    print(f"Video map created with {len(video_map)} segments")
    return video_map


def save_video_map(video_map, output_path="video_map.json"):
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
    print(f"✓ Output: video_map.json")


if __name__ == '__main__':
    main()
