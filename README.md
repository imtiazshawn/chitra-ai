# ChitraAI - Agentic Video Synthesis System

A Python-based AI Video Agent system with multiple pipelines for automated video creation.

## Pipelines

### Audio to Reels (Active - 40% Automation)
- **Step 1**: Transcribe audio and generate video map with AI
- **Step 2**: Download portrait videos from Pexels based on keywords
- **Step 3**: Assemble final video with FFmpeg (9:16 vertical)
- **Step 4**: Add professional captions with word-level timing and global theme consistency

### Audio to Long Video (Active - 40% Automation)
- **Step 1**: Transcribe audio and generate video map with AI
- **Step 2**: Download landscape videos from Pexels based on keywords
- **Step 3**: Assemble final video with FFmpeg (16:9 landscape)
- **Step 4**: Add professional captions with word-level timing and global theme consistency

### Topic to Script (Active - 20% Automation)
- **Step 1**: Generate high-retention script from topic using AI (Script Agent)
- Manual TTS conversion required
- Use Audio to Reels for video generation

### Topic to Speech (Active - 60% Automation)
- **Step 1**: Generate high-retention script with [Director Cues] (Script Agent)
- **Step 2**: Synthesize audio using ElevenLabs professional voices (Voice Agent)
- Use Audio to Reels for video generation

### Topic to Reels (Active - 80% Automation)
- **Step 1**: Generate high-retention script from topic using AI (Script Agent)
- **Step 2**: Synthesize professional voiceover (Voice Agent)
- **Step 3**: Transcribe and map visuals (Intelligence Agent)
- **Step 4**: Download videos from Pexels (Download Agent)
- **Step 5**: Assemble video with perfect sync (Assembly Agent)
- **Step 6**: Add professional captions (Subtitle Agent)

### Full Automation (Active - 100% Automation)
- **Step 1**: Analyze YouTube channel and suggest trending topic (Spy Agent)
- **Step 2**: Generate high-retention script (Script Agent)
- **Step 3**: Synthesize professional voiceover (Voice Agent)
- **Step 4**: Transcribe and map visuals (Intelligence Agent)
- **Step 5**: Download videos from Pexels (Download Agent)
- **Step 6**: Assemble video with perfect sync (Assembly Agent)
- **Step 7**: Add professional captions (Subtitle Agent)
- **Step 8**: Generate viral titles, SEO descriptions, and tags (Metadata Agent)

## Professional Features

- ** Landing Dashboard**: Select from multiple AI pipelines with automation levels
- ** Modular Architecture**: Clean, maintainable, professional codebase
- ** Cyberpunk UI**: Matte black with neon orange/red gradients
- ** Agent-Based**: Each step handled by specialized autonomous agents
- ** State Management**: Smart UI controls prevent accidental clicks
- ** Cancel Control**: Stop processing at any time with cleanup
- ** Seamless Looping**: Video clips loop infinitely to match audio duration
- ** Professional SEO**: Copy-paste ready metadata in text areas

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg:
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

5. Configure environment:
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

6. Get API Keys:
   - **Groq**: https://console.groq.com/ (free)
   - **Pexels**: https://www.pexels.com/api/ (free)
   - **ElevenLabs**: https://elevenlabs.io/ (10,000 chars/month free)

## Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```
Then open your browser to the URL shown (usually http://localhost:8501)

**Dashboard Features:**
- Select from multiple AI pipelines
- View automation levels ("Lazy Level")
- See pipeline status (Active/Developing)
- Smooth navigation between pipelines

**Audio to Reels Features:**
- Upload audio file
- Toggle captions on/off
- Upload logo (optional)
- Real-time progress tracking
- Download final video (9:16 vertical)
- Video preview

**Audio to Long Video Features:**
- Upload audio file
- Toggle captions on/off
- Upload logo (optional)
- Real-time progress tracking
- Download final video (16:9 landscape)
- Video preview

**Topic to Reels Features:**
- Enter topic/idea
- Complete 6-agent automation pipeline
- AI generates script → synthesizes voice → creates video
- Professional captions with word-level highlighting
- Download final reel
- Video preview

**Full Automation Features:**
- Paste YouTube channel URL
- Click "Analyze & Generate" button
- AI analyzes channel and suggests trending topic
- Complete 8-agent autonomous pipeline
- Generates script → voice → video → SEO metadata
- 3 SEO options with copy-paste text areas
- Viral titles, descriptions with hashtags, optimized tags
- Cancel button to stop processing anytime
- Download final reel
- Video preview

**Topic to Speech Features:**
- Enter topic/idea
- Agentic workflow: Script Agent → Voice Agent
- Generates script with [Director Cues]
- Automatically synthesizes audio with ElevenLabs
- Professional male voice (Adam - deep, authoritative)
- Natural, expressive tone (Stability: 0.5, Similarity: 0.75)
- Download script JSON, clean text, and audio MP3
- Audio preview in browser
- Free tier: 10,000 characters/month
- Then use Audio to Reels for video

### Command Line (Advanced)

#### Topic to Reels: Generate Script
```bash
python src/script_agent.py
```
This creates `generated_script.json` with:
- High-retention 40-50s script
- Hook, tension, solution, CTA structure
- Senior Architect writing style
- Punchy segments (5-12 words per line)
- Optional [Director Cues] for tone, pacing, silences (max 4-5 per script)
- Suggested video vibe

Then convert script to audio using TTS service and proceed with Audio to Reels pipeline.

#### Topic to Speech: Generate Script + Audio
```bash
python src/speech_agent.py
```
This creates:
- `generated_script.json` - Full script with [Director Cues]
- `clean_script.txt` - Clean script for reference
- `audio.mp3` - Professional voiceover with ElevenLabs

The Voice Agent automatically:
- Uses ElevenLabs professional voice (Adam)
- Removes [Director Cues] before synthesis
- Natural, expressive tone (Stability: 0.5, Similarity: 0.75)
- Deep, authoritative voice perfect for Senior Architect persona

**ElevenLabs Setup:**
1. Sign up at https://elevenlabs.io/
2. Get your free API key (10,000 chars/month)
3. Add to `.env` file as `ELEVENLABS_API_KEY`

Then upload audio.mp3 to Audio to Reels pipeline.

#### Step 1: Transcribe Audio & Generate Video Map

**For 9:16 Reels:**
```bash
python src/main.py
```
This creates `video_map.json` with timestamped segments and visual keywords.

**For 16:9 Long Video:**
```bash
python src/main_long.py
```
This creates `video_map_long.json` with timestamped segments and visual keywords.

#### Step 2: Download Videos from Pexels

**For 9:16 Reels:**
```bash
python src/download_videos.py
```
This downloads portrait videos to `/assets` folder based on keywords.

**For 16:9 Long Video:**
```bash
python src/download_videos_long.py
```
This downloads landscape videos to `/assets_long` folder based on keywords.

#### Step 3: Assemble Final Video

**For 9:16 Reels:**
```bash
python src/assemble_video.py
```
This creates `draft_video.mp4` with trimmed clips, 9:16 aspect ratio, and synced audio.

**For 16:9 Long Video:**
```bash
python src/assemble_video_long.py
```
This creates `draft_video_long.mp4` with trimmed clips, 16:9 aspect ratio, and synced audio.

#### Step 4: Add Professional Captions

**For 9:16 Reels:**
```bash
python src/add_captions.py
```
This creates `final_output.mp4` with:
- **56px mobile-optimized font** (75% larger than before)
- **Global theme consistency** (one color + font per video)
- **Word-level dynamic highlighting** with smooth pop animations
- **3px black outline + 1.5px shadow** for perfect visibility
- **85% opacity passive words** for clear focus
- **Vibe-based font selection** (Tech, Energetic, Professional, etc.)
- **165px safe zone margin** to avoid Reels UI overlap

**For 16:9 Long Video:**
```bash
python src/add_captions_long.py
```
This creates `final_output_long.mp4` with:
- **28px subtitle-style font** (classic subtitle appearance)
- **Static text** (no animations - clean professional look)
- **2px black outline + 1px shadow** for perfect readability
- **Bottom-aligned subtitles** (traditional subtitle positioning)
- **80px safe zone margin** for 16:9 format
- **Simple white text** (no color highlighting)

**Optional**: Place `logo.png` in the project root for branding overlay.

## Project Structure

```
ChitraAI/
├── venv/                 # Virtual environment
├── ChitraAI_Projects/   # All video projects (organized by unique ID)
│   ├── reels_9x16_20240115_143022/
│   │   ├── assets/      # Downloaded video clips
│   │   ├── temp/        # Temporary processed clips
│   │   ├── audio.mp3    # Source audio
│   │   ├── video_map.json # Video mapping
│   │   ├── captions.ass # Subtitle file
│   │   ├── draft_video.mp4 # Assembled video
│   │   ├── final_output.mp4 # Final video with captions
│   │   └── logo.png     # Optional logo
│   ├── long_16x9_20240115_144530/
│   │   ├── assets/      # Downloaded landscape clips
│   │   ├── temp/        # Temporary files
│   │   └── ...          # Same structure as above
│   └── topic_to_reels_20240115_150045/
│       ├── assets/
│       ├── generated_script.json
│       ├── clean_script.txt
│       └── ...          # Complete pipeline outputs
├── src/                  # Backend pipeline code
│   ├── workspace_manager.py # Project folder management
│   ├── spy_agent.py     # Market research & topic suggestion
│   ├── script_agent.py  # Script generation from topic
│   ├── speech_agent.py  # Topic to Speech pipeline
│   ├── metadata_agent.py # SEO optimization (titles, tags)
│   ├── main.py          # Step 1: Transcription & mapping (9:16)
│   ├── main_long.py     # Step 1: Transcription & mapping (16:9)
│   ├── download_videos.py # Step 2: Video download (9:16)
│   ├── download_videos_long.py # Step 2: Video download (16:9)
│   ├── assemble_video.py  # Step 3: Video assembly (9:16)
│   ├── assemble_video_long.py # Step 3: Video assembly (16:9)
│   ├── add_captions.py    # Step 4: Caption generation (9:16)
│   └── add_captions_long.py # Step 4: Caption generation (16:9)
├── ui/                   # Frontend UI modules
│   ├── __init__.py      # Module init
│   ├── styles.py        # Base cyberpunk CSS
│   ├── dashboard_styles.py # Dashboard-specific CSS
│   ├── components.py    # Reusable UI components
│   ├── dashboard.py     # Landing dashboard
│   ├── audio_to_reels.py # Audio to Reels page (9:16)
│   ├── audio_to_long_video.py # Audio to Long Video page (16:9)
│   ├── topic_to_script.py # Topic to Script page
│   ├── topic_to_reels.py # Topic to Reels page
│   ├── topic_to_speech.py # Topic to Speech page
│   ├── autonomous_engine.py # 100% Automation engine
│   ├── pipeline.py      # Pipeline execution logic (9:16)
│   └── pipeline_long.py # Pipeline execution logic (16:9)
├── app.py               # Main app with routing
├── requirements.txt     # Dependencies
├── .env                 # API keys (not in git)
├── .env.example         # Environment template
├── .gitignore          # Git ignore
└── README.md           # Documentation
```
