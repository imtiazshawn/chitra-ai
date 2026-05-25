"""Voice Activity Detection (VAD) Utilities - Professional Speech Detection"""
import os

# Try to import torch/VAD dependencies, but make them optional
try:
    import torch
    import torchaudio
    VAD_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Warning: VAD dependencies not available: {e}")
    print("Subtitle timing will use fallback method (12% trim)")
    VAD_AVAILABLE = False
    torch = None
    torchaudio = None

# Global VAD model cache
_vad_model = None
_vad_utils = None

def load_vad_model():
    """Load Silero VAD model (cached for performance)."""
    global _vad_model, _vad_utils
    
    if not VAD_AVAILABLE:
        return None, None
    
    if _vad_model is None:
        print("Loading Silero VAD model...")
        try:
            _vad_model, _vad_utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            print("✓ VAD model loaded")
        except Exception as e:
            print(f"Warning: Failed to load VAD model: {e}")
            print("Falling back to timestamp-based detection")
            return None, None
    
    return _vad_model, _vad_utils

def get_speech_timestamps(audio_path, sampling_rate=16000):
    """Detect speech segments in audio using Silero VAD.
    
    Args:
        audio_path: Path to audio file
        sampling_rate: Target sampling rate (VAD works best at 16kHz)
    
    Returns:
        List of speech segments: [{'start': 0.5, 'end': 2.3}, ...]
    """
    if not VAD_AVAILABLE:
        return []
    
    model, utils = load_vad_model()
    
    if model is None:
        print("VAD not available, returning empty segments")
        return []
    
    try:
        # Load audio
        wav, sr = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = torch.mean(wav, dim=0, keepdim=True)
        
        # Resample to 16kHz if needed (VAD requirement)
        if sr != sampling_rate:
            resampler = torchaudio.transforms.Resample(sr, sampling_rate)
            wav = resampler(wav)
        
        # Get speech timestamps from VAD
        speech_timestamps = utils[0](
            wav.squeeze(),
            model,
            sampling_rate=sampling_rate,
            threshold=0.5,  # Speech probability threshold
            min_speech_duration_ms=250,  # Minimum speech segment (250ms)
            min_silence_duration_ms=100,  # Minimum silence to split (100ms)
            window_size_samples=512,  # Analysis window
            speech_pad_ms=30  # Padding around speech (30ms)
        )
        
        # Convert to seconds
        speech_segments = []
        for ts in speech_timestamps:
            speech_segments.append({
                'start': ts['start'] / sampling_rate,
                'end': ts['end'] / sampling_rate
            })
        
        print(f"✓ VAD detected {len(speech_segments)} speech segments")
        return speech_segments
        
    except Exception as e:
        print(f"Warning: VAD processing failed: {e}")
        return []

def trim_word_to_speech_segments(word_start, word_end, speech_segments, buffer_ms=50):
    """Trim word timestamp to only overlap with speech segments.
    
    Args:
        word_start: Word start time (seconds)
        word_end: Word end time (seconds)
        speech_segments: List of speech segments from VAD
        buffer_ms: Buffer before segment end (milliseconds)
    
    Returns:
        Tuple of (trimmed_start, trimmed_end)
    """
    buffer = buffer_ms / 1000.0  # Convert to seconds
    
    # Find which speech segment(s) this word overlaps with
    for segment in speech_segments:
        seg_start = segment['start']
        seg_end = segment['end']
        
        # Check if word overlaps with this speech segment
        if word_start < seg_end and word_end > seg_start:
            # Trim word to fit within speech segment
            trimmed_start = max(word_start, seg_start)
            trimmed_end = min(word_end, seg_end - buffer)
            
            # Ensure end is after start
            if trimmed_end > trimmed_start:
                return trimmed_start, trimmed_end
    
    # If word doesn't overlap with any speech segment, return minimal duration
    # This handles edge cases where VAD might miss very short words
    return word_start, word_start + 0.1

def apply_vad_to_word_segments(words, speech_segments):
    """Apply VAD trimming to all word segments.
    
    Args:
        words: List of word dicts with 'start' and 'end' keys
        speech_segments: List of speech segments from VAD
    
    Returns:
        List of words with trimmed timestamps
    """
    if not speech_segments:
        print("Warning: No speech segments from VAD, using original timestamps")
        return words
    
    trimmed_words = []
    skipped_count = 0
    
    for word in words:
        original_start = word['start']
        original_end = word['end']
        
        # Trim to speech segments
        trimmed_start, trimmed_end = trim_word_to_speech_segments(
            original_start, 
            original_end, 
            speech_segments
        )
        
        # Calculate how much we trimmed
        original_duration = original_end - original_start
        trimmed_duration = trimmed_end - trimmed_start
        trim_percent = ((original_duration - trimmed_duration) / original_duration * 100) if original_duration > 0 else 0
        
        # Skip words that were trimmed too much (likely in silence)
        if trimmed_duration < 0.05:  # Less than 50ms
            skipped_count += 1
            continue
        
        # Create trimmed word
        trimmed_word = word.copy()
        trimmed_word['start'] = trimmed_start
        trimmed_word['end'] = trimmed_end
        trimmed_word['vad_trimmed'] = trim_percent > 5  # Flag if significantly trimmed
        
        trimmed_words.append(trimmed_word)
    
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} words in silence/breath regions")
    
    print(f"✓ VAD trimming applied to {len(trimmed_words)} words")
    return trimmed_words
