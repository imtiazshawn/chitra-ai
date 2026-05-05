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


def find_and_download_video(segment, clip_number):
    """Search and download video with multiple query attempts."""
    # Get search queries and fallback
    search_queries = segment.get('search_queries', [])
    fallback_topic = segment.get('fallback_topic', 'abstract')
    
    # Build complete search list
    all_queries = search_queries + [fallback_topic]
    
    print(f"  Available queries: {all_queries}")
    
    for query in all_queries:
        print(f"  Searching Pexels for: '{query}'")
        
        videos = search_pexels_video(query)
        
        if videos:
            # Try to find a suitable video
            for video in videos:
                video_url = get_video_url(video)
                if video_url:
                    filename = f"clip_{clip_number}.mp4"
                    print(f"  Found video! Downloading {filename}...")
                    
                    if download_video(video_url, filename):
                        print(f"✓ Downloaded {filename} using query: '{query}'")
                        return True
                    else:
                        print(f"  Failed to download, trying next video...")
        
        print(f"  No results for '{query}', trying next query...")
        time.sleep(0.5)  # Rate limiting
    
    print(f"✗ Could not find video after trying all queries")
    return False


def download_videos_for_map(video_map):
    """Download videos for all segments in video map.
    
    Args:
        video_map: List of video segments with search queries
        
    Returns:
        Number of successfully downloaded videos
    """
    create_assets_folder()
    
    successful = 0
    for i, segment in enumerate(video_map, 1):
        if find_and_download_video(segment, i):
            successful += 1
        time.sleep(1)  # Rate limiting
    
    return successful


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
        print(f"\n[{i}/{len(video_map)}] Downloading clip {i}...")
        
        if find_and_download_video(segment, i):
            successful += 1
        
        time.sleep(1)  # Rate limiting between requests
    
    print(f"\n{'='*40}")
    print(f"✓ Process complete!")
    print(f"✓ Successfully downloaded: {successful}/{len(video_map)} clips")
    print(f"✓ Videos saved in: {ASSETS_FOLDER}/")


if __name__ == '__main__':
    main()
