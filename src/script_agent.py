import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# High-retention script structure
SCRIPT_PROMPT_TEMPLATE = """You are a Senior Architect in business/tech content creation. Generate a 40-50 second high-retention video script.

Topic: {topic}

STRUCTURE (strict timing):
[0-5s] THE HOOK: Bold claim, shocking stat, or direct pain point question. No fluff.
[5-20s] THE TENSION: Agitate the problem. Why the status quo fails.
[20-40s] THE SOLUTION: The unique insight. Punchy, authoritative, cynical.
[40-50s] THE CTA: Sharp closing statement.

STYLE RULES:
- Brutally honest, slightly cynical, high-value
- NO generic AI phrases: "In the world of", "Unlock your potential", "Embark on a journey"
- Professional tech/business terminology
- Fast-paced, retention-focused
- Write like a senior engineer explaining to juniors

OUTPUT FORMAT (JSON only):
{{
  "raw_script": "The complete 40-50 second script as one paragraph",
  "video_vibe": "tech|professional|dramatic|energetic",
  "hook": "First 5 seconds text",
  "estimated_duration": 45
}}

Generate the script now. Return ONLY valid JSON."""


def generate_script(topic):
    """Generate high-retention script from topic using Groq."""
    print(f"Generating script for topic: {topic}")
    
    prompt = SCRIPT_PROMPT_TEMPLATE.format(topic=topic)
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior content strategist. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # Clean JSON
    if response_text.startswith('```json'):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith('```'):
        response_text = response_text[3:-3].strip()
    
    script_data = json.loads(response_text)
    print(f"✓ Script generated ({script_data.get('estimated_duration', 45)}s)")
    
    return script_data


def save_script(script_data, output_path="generated_script.json"):
    """Save generated script to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Script saved to {output_path}")


def main():
    topic = input("Enter your topic: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    # Generate script
    script_data = generate_script(topic)
    
    # Save to file
    save_script(script_data)
    
    print("\n" + "="*50)
    print("GENERATED SCRIPT:")
    print("="*50)
    print(f"\nVibe: {script_data.get('video_vibe', 'professional')}")
    print(f"Duration: ~{script_data.get('estimated_duration', 45)}s")
    print(f"\nHook: {script_data.get('hook', 'N/A')}")
    print(f"\nFull Script:\n{script_data.get('raw_script', 'N/A')}")
    print("\n" + "="*50)
    print("\nNext: Use this script with a TTS service to generate audio,")
    print("then run the Audio to Reels pipeline.")


if __name__ == '__main__':
    main()
