# AI Video Agent

A Python-based AI Video Agent that creates short-form videos (Reels/Shorts) from audio files.

## Features

- **Step 1**: Transcribe audio and generate video map with AI
- **Step 2**: Download portrait videos from Pexels based on keywords
- **Step 3**: Assemble final video with FFmpeg
- **Step 4**: Add professional captions with word-level timing

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

## Usage

### Step 1: Transcribe Audio & Generate Video Map
```bash
python src/main.py
```
This creates `video_map.json` with timestamped segments and visual keywords.

### Step 2: Download Videos from Pexels
```bash
python src/download_videos.py
```
This downloads portrait videos to `/assets` folder based on keywords.

### Step 3: Assemble Final Video
```bash
python src/assemble_video.py
```
This creates `draft_video.mp4` with trimmed clips, 9:16 aspect ratio, and synced audio.

### Step 4: Add Professional Captions
```bash
python src/add_captions.py
```
This creates `final_output.mp4` with word-level captions and logo overlay.

**Optional**: Place `logo.png` in the project root for branding overlay.

## Project Structure

```
ChitraAI/
├── venv/                 # Virtual environment
├── src/                  # Source code
│   ├── main.py          # Step 1: Transcription & mapping
│   ├── download_videos.py # Step 2: Video download
│   ├── assemble_video.py  # Step 3: Video assembly
│   └── add_captions.py    # Step 4: Caption generation
├── assets/              # Downloaded video clips
├── temp/                # Temporary processed clips
├── video_map.json       # Generated video map
├── draft_video.mp4      # Assembled video
├── final_output.mp4     # Final video with captions
├── logo.png             # Optional branding logo
├── requirements.txt     # Dependencies
├── .env                 # API keys (not in git)
├── .env.example         # Environment template
├── .gitignore          # Git ignore
└── README.md           # Documentation
```
