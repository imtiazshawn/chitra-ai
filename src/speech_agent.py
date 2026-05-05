import os
import json
import re
import edge_tts
import asyncio
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from dotenv import load_dotenv
from script_agent import generate_script, save_script

load_dotenv()

# Configure ElevenLabs client
client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

# V2 Model compatible voice IDs (Free Tier)
VOICE_ID = "bIHbv24MWmeRgasZH58o"  # Will
BACKUP_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam - Deep, authoritative male voice

# Edge-TTS backup voice (high-quality, always free)
EDGE_TTS_VOICE = "en-US-ChristopherNeural"  # Deep, authoritative male


def clean_script_for_tts(formatted_script):
    """Clean script by removing [Director Cues] and adding strategic pauses.
    
    Args:
        formatted_script: List of script lines with [Director Cues]
        
    Returns:
        Cleaned script text with natural breathing pauses for TTS
    """
    cleaned_lines = []
    
    for line in formatted_script:
        # Skip lines that are only director cues
        if line.startswith('[') and line.endswith(']'):
            continue
        
        # Remove any inline [brackets] from the line using Regex
        cleaned_line = re.sub(r'\[.*?\]', '', line)
        cleaned_line = cleaned_line.strip()
        
        if cleaned_line:
            # Remove periods and exclamation marks (cause 1s pause)
            cleaned_line = re.sub(r'[.!?]', '', cleaned_line)
            cleaned_lines.append(cleaned_line)
    
    # Join with commas for natural 0.2-0.3s breathing pauses
    # This mimics how real content creators speak
    clean_text = ', '.join(cleaned_lines) + '.'
    
    return clean_text


def generate_speech_edge_tts(text, output_path="audio.mp3", voice=EDGE_TTS_VOICE):
    """Generate speech using Edge-TTS as backup (always free, high quality).
    
    Args:
        text: Clean text to convert to speech
        output_path: Path to save the audio file
        voice: Edge-TTS voice ID
    """
    print(f"  Using Edge-TTS Backup (Voice: {voice})")
    
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    
    asyncio.run(_generate())
    print(f"✓ Audio generated with Edge-TTS")


def generate_speech_elevenlabs(text, output_path="audio.mp3", voice_id=VOICE_ID):
    """Generate speech using ElevenLabs V2 models (Free Tier compatible).
    
    Args:
        text: Clean text to convert to speech
        output_path: Path to save the audio file
        voice_id: ElevenLabs voice ID to use
    """
    print(f"  Using ElevenLabs V2 (Voice: Will)")
    print(f"  Model: eleven_turbo_v2_5 (Free Tier)")
    print(f"  Settings: Stability=0.4, Similarity=0.75, Style=0.6")
    
    # Generate audio using V2 model with aggressive settings
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_turbo_v2_5",  # V2 model for Free Tier
        voice_settings=VoiceSettings(
            stability=0.4,          # More variation for energy
            similarity_boost=0.75,  # Maintain voice identity
            style=0.6,              # Aggressive style exaggeration
            use_speaker_boost=True
        )
    )
    
    # Save audio to file
    with open(output_path, 'wb') as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    
    print(f"✓ Audio generated with ElevenLabs V2")


def generate_speech_from_script(script_data, output_path="audio.mp3"):
    """Generate speech from script with no-break strategy.
    
    Args:
        script_data: Dictionary containing formatted_script array
        output_path: Path to save the audio file
        
    Returns:
        Path to generated audio file
    """
    print("Generating speech with ElevenLabs...")
    
    # Extract script lines
    formatted_script = script_data.get('formatted_script', [])
    
    if not formatted_script:
        raise ValueError("No formatted_script found in script data")
    
    print(f"  Script length: {len(formatted_script)} lines")
    
    # Clean script (remove [Director Cues] with Regex)
    clean_text = clean_script_for_tts(formatted_script)
    
    # Debug: Show what was cleaned
    print(f"  Original lines: {len(formatted_script)}")
    print(f"  Cleaned preview: {clean_text[:150]}...")
    
    print(f"  Clean text: {len(clean_text)} characters")
    print(f"  Preview: {clean_text[:100]}...")
    
    # Save clean script for reference
    with open('clean_script.txt', 'w', encoding='utf-8') as f:
        f.write(clean_text)
    print(f"✓ Clean script saved to clean_script.txt")
    
    # Check API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    has_elevenlabs = api_key and api_key != 'your_elevenlabs_api_key_here'
    
    # Try ElevenLabs first, fallback to Edge-TTS if any issue
    if has_elevenlabs:
        try:
            # Attempt ElevenLabs V2
            generate_speech_elevenlabs(clean_text, output_path)
            print(f"✓ Audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"\n⚠ ElevenLabs Error Details:")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {error_msg}")
            print(f"  Full Traceback:")
            traceback.print_exc()
            print(f"\n⚡ Switching to Backup High-Quality Voice (Edge-TTS)")
    else:
        print(f"⚠ ElevenLabs API key not configured")
        print(f"⚡ Using Backup High-Quality Voice (Edge-TTS)")
    
    # No-break fallback: Edge-TTS (always works, high quality)
    try:
        generate_speech_edge_tts(clean_text, output_path)
        print(f"✓ Audio saved to {output_path}")
        return output_path
    except Exception as e:
        raise Exception(f"All speech generation methods failed: {str(e)}")


def topic_to_speech(topic, output_audio="audio.mp3"):
    """Complete pipeline: Topic → Script → Speech.
    
    Args:
        topic: The topic/idea for the script
        output_audio: Path to save the final audio file
        
    Returns:
        Tuple of (script_data, audio_path)
    """
    print("="*60)
    print("TOPIC TO SPEECH PIPELINE")
    print("="*60)
    
    # Step A: Generate Script with Reading Instructions
    print("\n[STEP 1/2] Script Agent: Generating high-retention script...")
    script_data = generate_script(topic, add_reading_instructions=True)
    save_script(script_data)
    print(f"✓ Script generated: {len(script_data.get('formatted_script', []))} lines")
    
    # Step B: Generate Speech
    print("\n[STEP 2/2] Voice Agent: Synthesizing audio...")
    audio_path = generate_speech_from_script(script_data, output_audio)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"✓ Script: generated_script.json")
    print(f"✓ Clean Script: clean_script.txt")
    print(f"✓ Audio: {audio_path}")
    print(f"\nNext Steps:")
    print("1. Review the audio.mp3 file")
    print("2. Upload to 'Audio to Reels' pipeline")
    print("3. Generate your final video")
    
    return script_data, audio_path


def main():
    topic = input("Enter your topic: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    # Run pipeline (Gemini API key not required for script preparation)
    topic_to_speech(topic)


if __name__ == '__main__':
    main()
