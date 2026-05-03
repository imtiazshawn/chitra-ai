import os
import json
import requests
from dotenv import load_dotenv
import time

load_dotenv()

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
ASSETS_FOLDER = 'assets'


def create_assets_folder():
    """Create assets folder if it doesn't exist."""
    if not os.path.exists(ASSETS_FOLDER):
        os.makedirs(ASSETS_FOLDER)
        print(f"✓ Created {ASSETS_FOLDER} folder")


def search_pexels_video(keyword, orientation='portrait'):
    """Search Pexels for videos with specific keyword and orientation."""
    url = 'https://api.pexels.com/videos/search'
    headers = {'Authorization': PEXELS_API_KEY}
    params = {
        'query': keyword,
        'orientation': orientation,
        'per_page': 15
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('videos', [])
    return []


def get_video_url(video):
    """Extract the best quality portrait video URL."""
    video_files = video.get('video_files', [])
    
    # Filter for portrait videos (height > width)
    portrait_files = [
        vf for vf in video_files 
        if vf.get('height', 0) > vf.get('width', 0)
    ]
    
    if not portrait_files:
        return None
    
    # Sort by quality (prefer HD)
    portrait_files.sort(key=lambda x: x.get('height', 0), reverse=True)
    return portrait_files[0].get('link')


def simplify_keyword(keyword):
    """Simplify keyword by taking first word or removing descriptors."""
    words = keyword.strip().split()
    
    if len(words) > 1:
        # Try removing last word first
        return ' '.join(words[:-1])
    
    return None


def download_video(url, filename):
    """Download video from URL and save to file."""
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        filepath = os.path.join(ASSETS_FOLDER, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False


def find_and_download_video(keyword, clip_number, max_retries=3):
    """Search and download video with retry logic."""
    original_keyword = keyword
    current_keyword = keyword
    attempt = 0
    
    while attempt < max_retries:
        print(f"  Searching Pexels for: '{current_keyword}'")
        
        videos = search_pexels_video(current_keyword)
        
        if videos:
            # Try to find a suitable video
            for video in videos:
                video_url = get_video_url(video)
                if video_url:
                    filename = f"clip_{clip_number}.mp4"
                    print(f"  Found video! Downloading {filename}...")
                    
                    if download_video(video_url, filename):
                        print(f"✓ Downloaded {filename}")
                        return True
                    else:
                        print(f"  Failed to download, trying next video...")
        
        # No suitable video found, simplify keyword
        attempt += 1
        if attempt < max_retries:
            simplified = simplify_keyword(current_keyword)
            if simplified:
                print(f"  No results. Retrying with simpler keyword...")
                current_keyword = simplified
            else:
                # Use generic fallback
                current_keyword = 'abstract'
                print(f"  No results. Trying generic keyword: '{current_keyword}'")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✗ Could not find video for '{original_keyword}' after {max_retries} attempts")
    return False


def main():
    print("=== Pexels Video Downloader ===\n")
    
    # Check API key
    if not PEXELS_API_KEY:
        print("Error: PEXELS_API_KEY not found in .env file")
        return
    
    # Load video map
    if not os.path.exists('video_map.json'):
        print("Error: video_map.json not found")
        return
    
    with open('video_map.json', 'r', encoding='utf-8') as f:
        video_map = json.load(f)
    
    print(f"Loaded video map with {len(video_map)} segments\n")
    
    # Create assets folder
    create_assets_folder()
    
    # Download videos for each segment
    successful = 0
    for i, segment in enumerate(video_map, 1):
        keyword = segment.get('visual_keyword', 'abstract')
        print(f"\n[{i}/{len(video_map)}] Downloading clip {i}...")
        print(f"  Keyword: {keyword}")
        
        if find_and_download_video(keyword, i):
            successful += 1
        
        time.sleep(1)  # Rate limiting between requests
    
    print(f"\n{'='*40}")
    print(f"✓ Process complete!")
    print(f"✓ Successfully downloaded: {successful}/{len(video_map)} clips")
    print(f"✓ Videos saved in: {ASSETS_FOLDER}/")


if __name__ == '__main__':
    main()
