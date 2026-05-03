# AI Video Agent

A Python-based AI Video Agent that creates short-form videos (Reels/Shorts) from audio files.

## Features

- **Step 1**: Transcribe audio and generate video map with AI
- **Step 2**: Download portrait videos from Pexels based on keywords

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

4. Configure environment:
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. Get API Keys:
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

## Project Structure

```
ChitraAI/
├── venv/                 # Virtual environment
├── src/                  # Source code
│   ├── main.py          # Step 1: Transcription & mapping
│   └── download_videos.py # Step 2: Video download
├── assets/              # Downloaded video clips
├── video_map.json       # Generated video map
├── requirements.txt     # Dependencies
├── .env                 # API keys (not in git)
├── .env.example         # Environment template
├── .gitignore          # Git ignore
└── README.md           # Documentation
```
