"""Metadata Agent - SEO Expert for Video Optimization"""
import os
import json
from groq import Groq

def generate_seo_metadata(script_data):
    """Generate viral titles, SEO descriptions, and tags for the video."""
    print("\n=== Metadata Agent: SEO Optimization ===\n")
    
    # Initialize Groq client
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
        raise ValueError("GROQ_API_KEY not configured in .env file")
    
    client = Groq(api_key=groq_api_key)
    
    # Extract script content
    hook = script_data.get('hook', '')
    formatted_script = script_data.get('formatted_script', [])
    full_script = '\n'.join(formatted_script) if formatted_script else ''
    video_vibe = script_data.get('video_vibe', 'professional')
    
    print("Generating SEO metadata...")
    
    prompt = f"""You are a YouTube SEO expert specializing in viral short-form content.

Video Script:
{hook}
{full_script}

Video Vibe: {video_vibe}

Generate 3 different options for:

1. VIRAL TITLE (each under 60 characters, curiosity-driven, no clickbait)
2. SEO DESCRIPTION (2-3 sentences with relevant keywords and 3-5 hashtags)
3. TAGS (8-10 optimized tags for YouTube/Instagram algorithm)

Format your response EXACTLY like this:

OPTION 1:
Title: [title here]
Description: [description here with #hashtags]
Tags: tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8

OPTION 2:
Title: [title here]
Description: [description here with #hashtags]
Tags: tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8

OPTION 3:
Title: [title here]
Description: [description here with #hashtags]
Tags: tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Parse the output into structured format
        metadata_options = parse_metadata_output(raw_output)
        
        print(f"✓ Generated {len(metadata_options)} SEO options\n")
        
        return {
            'options': metadata_options,
            'video_vibe': video_vibe,
            'raw_output': raw_output
        }
        
    except Exception as e:
        print(f"Error generating metadata: {str(e)}")
        raise

def parse_metadata_output(raw_output):
    """Parse the AI output into structured metadata options."""
    options = []
    
    # Split by OPTION markers
    option_blocks = raw_output.split('OPTION ')
    
    for block in option_blocks[1:]:  # Skip first empty split
        lines = block.strip().split('\n')
        option = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Title:'):
                option['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Description:'):
                option['description'] = line.replace('Description:', '').strip()
            elif line.startswith('Tags:'):
                tags_str = line.replace('Tags:', '').strip()
                option['tags'] = [tag.strip() for tag in tags_str.split(',')]
        
        if option:
            options.append(option)
    
    return options

def save_metadata(metadata, output_file='seo_metadata.json'):
    """Save metadata to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ SEO metadata saved: {output_file}")

def main():
    """CLI interface for Metadata Agent."""
    print("=== Metadata Agent - SEO Expert ===\n")
    
    # Load script data
    if not os.path.exists('generated_script.json'):
        print("Error: generated_script.json not found")
        print("Run Script Agent first to generate a script")
        return
    
    with open('generated_script.json', 'r', encoding='utf-8') as f:
        script_data = json.load(f)
    
    try:
        metadata = generate_seo_metadata(script_data)
        save_metadata(metadata)
        
        print("\n" + "="*60)
        print("✓ SEO Metadata Generated!\n")
        
        for i, option in enumerate(metadata['options'], 1):
            print(f"OPTION {i}:")
            print(f"Title: {option.get('title', 'N/A')}")
            print(f"Description: {option.get('description', 'N/A')}")
            print(f"Tags: {', '.join(option.get('tags', []))}")
            print()
        
        print("Use these options to optimize your video for maximum reach!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == '__main__':
    main()
