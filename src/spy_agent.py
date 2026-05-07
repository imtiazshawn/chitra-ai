"""Spy Agent - Market Research for YouTube Channels"""
import os
import json
import re
from groq import Groq

def extract_channel_id(url):
    """Extract channel ID or handle from YouTube URL."""
    # Handle various YouTube URL formats
    patterns = [
        r'youtube\.com/@([^/\?]+)',
        r'youtube\.com/channel/([^/\?]+)',
        r'youtube\.com/c/([^/\?]+)',
        r'youtube\.com/user/([^/\?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def analyze_channel_and_suggest_topic(channel_url):
    """Analyze YouTube channel and suggest a unique trending topic."""
    print(f"\n=== Spy Agent: Market Research ===")
    print(f"Target: {channel_url}\n")
    
    # Extract channel identifier
    channel_id = extract_channel_id(channel_url)
    if not channel_id:
        print("Warning: Could not extract channel ID from URL")
        print("Proceeding with generic analysis...\n")
    else:
        print(f"Channel ID: {channel_id}\n")
    
    # Initialize Groq client
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
        raise ValueError("GROQ_API_KEY not configured in .env file")
    
    client = Groq(api_key=groq_api_key)
    
    # Simulated recent titles (in production, use YouTube Data API)
    # For now, we'll ask the AI to suggest based on channel URL pattern
    print("Analyzing channel content patterns...")
    
    prompt = f"""You are a YouTube market research expert analyzing content trends.

Channel URL: {channel_url}

Based on this channel URL and typical content patterns in this niche, suggest ONE unique, trending topic for a 40-50 second short/reel that:
1. Hasn't been overdone in this niche
2. Has high viral potential
3. Solves a specific problem or answers a burning question
4. Is relevant to the channel's audience

Respond with ONLY the topic as a single sentence (no explanations, no quotes).

Example outputs:
- Why most developers quit coding after 2 years
- The psychology behind why people ghost you
- How billionaires think differently about time

Your topic:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=100
        )
        
        topic = response.choices[0].message.content.strip()
        
        # Clean up the topic
        topic = topic.strip('"\'')
        
        print(f"✓ Suggested Topic: {topic}\n")
        
        return {
            'channel_url': channel_url,
            'channel_id': channel_id,
            'suggested_topic': topic,
            'confidence': 'high'
        }
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

def save_spy_report(spy_data, output_file='spy_report.json'):
    """Save spy agent report to JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(spy_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Spy report saved: {output_file}")

def main():
    """CLI interface for Spy Agent."""
    print("=== Spy Agent - YouTube Market Research ===\n")
    
    channel_url = input("Enter YouTube Channel URL: ").strip()
    
    if not channel_url:
        print("Error: Channel URL is required")
        return
    
    try:
        spy_data = analyze_channel_and_suggest_topic(channel_url)
        save_spy_report(spy_data)
        
        print("\n" + "="*50)
        print("✓ Market research complete!")
        print(f"✓ Suggested Topic: {spy_data['suggested_topic']}")
        print("\nNext: Use this topic with Script Agent to generate content")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == '__main__':
    main()
