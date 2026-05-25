"""Precise Word-Level Alignment using WhisperX - Audio Analysis Method"""
import os

# Try to import WhisperX, make it optional
try:
    import whisperx
    import torch
    WHISPERX_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Warning: WhisperX not available: {e}")
    print("Subtitle timing will use fixed-duration fallback")
    WHISPERX_AVAILABLE = False
    whisperx = None
    torch = None

# Global model cache
_whisperx_model = None
_align_model = None
_align_metadata = None

def load_whisperx_models(device="cpu"):
    """Load WhisperX models for transcription and alignment."""
    global _whisperx_model, _align_model, _align_metadata
    
    if not WHISPERX_AVAILABLE:
        return None, None, None
    
    if _whisperx_model is None:
        print("Loading WhisperX models...")
        try:
            # Load Whisper model
            _whisperx_model = whisperx.load_model(
                "base",  # Use base model (faster, good accuracy)
                device=device,
                compute_type="int8"  # Faster on CPU
            )
            print("✓ WhisperX transcription model loaded")
            
            # Load alignment model
            _align_model, _align_metadata = whisperx.load_align_model(
                language_code="en",
                device=device
            )
            print("✓ WhisperX alignment model loaded")
            
        except Exception as e:
            print(f"Warning: Failed to load WhisperX models: {e}")
            return None, None, None
    
    return _whisperx_model, _align_model, _align_metadata

def get_precise_word_timestamps(audio_path, transcript_text=None):
    """Get precise word-level timestamps by analyzing audio waveform.
    
    This uses forced alignment to map each word to its exact position in the audio.
    
    Args:
        audio_path: Path to audio file
        transcript_text: Optional transcript text (if None, will transcribe)
    
    Returns:
        List of word dicts: [{'word': 'hello', 'start': 0.5, 'end': 0.8}, ...]
    """
    if not WHISPERX_AVAILABLE:
        print("WhisperX not available, returning empty list")
        return []
    
    model, align_model, align_metadata = load_whisperx_models()
    
    if model is None:
        print("WhisperX models not loaded, returning empty list")
        return []
    
    try:
        print(f"Analyzing audio waveform: {audio_path}")
        
        # Load audio
        audio = whisperx.load_audio(audio_path)
        
        # Transcribe if no transcript provided
        if transcript_text is None:
            print("  Transcribing audio...")
            result = model.transcribe(audio, batch_size=16)
            print(f"  ✓ Transcribed {len(result['segments'])} segments")
        else:
            # Use provided transcript
            result = {
                "segments": [{"text": transcript_text}],
                "language": "en"
            }
        
        # Align words to audio (THIS IS THE MAGIC)
        print("  Performing forced alignment (mapping words to audio)...")
        result = whisperx.align(
            result["segments"],
            align_model,
            align_metadata,
            audio,
            device="cpu",
            return_char_alignments=False
        )
        
        # Extract word-level timestamps
        words = []
        for segment in result["segments"]:
            if "words" in segment:
                for word_info in segment["words"]:
                    words.append({
                        'word': word_info['word'],
                        'start': word_info['start'],
                        'end': word_info['end']
                    })
        
        print(f"✓ Aligned {len(words)} words with precise timing")
        
        # Show sample
        if words:
            print(f"  Sample: '{words[0]['word']}' at {words[0]['start']:.2f}s-{words[0]['end']:.2f}s")
        
        return words
        
    except Exception as e:
        print(f"Warning: WhisperX alignment failed: {e}")
        return []

def apply_precise_alignment_to_segments(word_segments, precise_words):
    """Replace fixed-duration timing with precise WhisperX timing.
    
    Args:
        word_segments: List of 3-word chunks with fixed timing
        precise_words: List of individual words with precise timing from WhisperX
    
    Returns:
        List of word segments with precise timing
    """
    if not precise_words:
        print("No precise timing available, keeping fixed-duration timing")
        return word_segments
    
    print(f"Applying precise alignment to {len(word_segments)} segments...")
    
    # Create word lookup by text
    precise_lookup = {w['word'].strip().lower(): w for w in precise_words}
    
    aligned_segments = []
    word_index = 0
    
    for segment in word_segments:
        words_in_segment = segment['text'].split()
        
        # Find precise timing for this chunk
        chunk_words = []
        for word in words_in_segment:
            if word_index < len(precise_words):
                chunk_words.append(precise_words[word_index])
                word_index += 1
        
        if chunk_words:
            # Use precise start/end from WhisperX
            aligned_segment = segment.copy()
            aligned_segment['start'] = chunk_words[0]['start']
            aligned_segment['end'] = chunk_words[-1]['end']
            aligned_segments.append(aligned_segment)
        else:
            # Fallback to original timing
            aligned_segments.append(segment)
    
    print(f"✓ Applied precise timing to {len(aligned_segments)} segments")
    return aligned_segments
