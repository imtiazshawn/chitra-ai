import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# High-retention script structure with optional reading instructions
SCRIPT_PROMPT_TEMPLATE = """You are an expert content creator. Generate a 40-50 second high-retention video script for ANY topic.

Topic: {topic}

STRUCTURE (strict timing):
[0-5s] THE HOOK: Bold claim, shocking stat, or direct pain point question. No fluff.
[5-20s] THE TENSION: Agitate the problem. Why the status quo fails.
[20-40s] THE SOLUTION: The unique insight. Punchy, authoritative.
[40-50s] THE CTA: Sharp closing statement.

STYLE RULES:
- Brutally honest, high-value content
- NO generic AI phrases: "In the world of", "Unlock your potential", "Embark on a journey"
- Match the tone to the topic (professional, entertaining, educational, inspirational)
- Fast-paced, retention-focused
- Each line must be a COMPLETE THOUGHT or SENTENCE (5-12 words)
- Natural flow, coherent sentences
- Focus ONLY on the SPECIFIC topic provided

OUTPUT FORMAT (JSON only):
{{
  "formatted_script": [
    "Complete sentence about the hook (5-12 words).",
    "Another complete sentence building tension (5-12 words).",
    "The key insight that changes perspective (5-12 words).",
    "Sharp closing statement that demands action (5-12 words)."
  ],
  "video_vibe": "professional|dramatic|energetic|aggressive|modern|playful|calm",
  "hook": "First sentence",
  "estimated_duration": 45
}}

Generate the script now. Return ONLY valid JSON."""

SCRIPT_PROMPT_WITH_INSTRUCTIONS = """You are an expert content creator. Generate a 40-50 second high-retention video script WITH minimal reading instructions for ANY topic.

Topic: {topic}

STRUCTURE (strict timing):
[0-5s] THE HOOK: Bold claim, shocking stat, or direct pain point question. No fluff.
[5-20s] THE TENSION: Agitate the problem. Why the status quo fails.
[20-40s] THE SOLUTION: The unique insight. Punchy, authoritative.
[40-50s] THE CTA: Sharp closing statement.

STYLE RULES:
- Brutally honest, high-value content
- NO generic AI phrases: "In the world of", "Unlock your potential", "Embark on a journey"
- Match the tone to the topic (professional, entertaining, educational, inspirational)
- Fast-paced, retention-focused
- Each line must be a COMPLETE THOUGHT or SENTENCE (5-12 words)
- Natural flow, coherent sentences
- Focus ONLY on the SPECIFIC topic provided

READING INSTRUCTIONS (CRITICAL RULES):
- Add ONLY 4-5 instructions for the ENTIRE script
- Place instructions ONLY at major section transitions (Hook, Problem, Solution, CTA)
- Do NOT add instructions for every line
- Use [Micro beat] for 0.2s pauses instead of long silences
- Format: [Hook – Aggressive & Fast], [Micro beat], [Punchline – Serious tone]
- Keep pacing FAST and PUNCHY for high-retention

EXAMPLE STRUCTURE (DO NOT COPY CONTENT):
{{
  "formatted_script": [
    "[Hook – Aggressive & Fast]",
    "Opening statement about YOUR topic (5-12 words)",
    "[Micro beat]",
    "Build tension specific to YOUR topic (5-12 words)",
    "Continue argument with authority (5-12 words)",
    "Deliver key insight for YOUR topic (5-12 words)",
    "[Punchline – Serious tone]",
    "Solution statement (5-12 words)",
    "Sharp closing CTA (5-12 words)"
  ],
  "video_vibe": "professional|dramatic|energetic|aggressive|modern|playful|calm",
  "hook": "First sentence",
  "estimated_duration": 45
}}

OUTPUT FORMAT (JSON only):
{{
  "formatted_script": [
    "[Hook – tone description]",
    "Complete sentence (5-12 words).",
    "Another complete sentence (5-12 words).",
    "[Instruction only at major transition]",
    "Complete sentence (5-12 words)."
  ],
  "video_vibe": "professional|dramatic|energetic|aggressive|modern|playful|calm",
  "hook": "First sentence",
  "estimated_duration": 45
}}

Generate the script now. Return ONLY valid JSON."""


def generate_script(topic, add_reading_instructions=False):
    """Generate high-retention script from topic using Groq.
    
    Args:
        topic: The topic/idea for the script
        add_reading_instructions: If True, adds [Director Cues] for tone, pacing, silences
    """
    print(f"Generating script for topic: {topic}")
    if add_reading_instructions:
        print("  Mode: WITH reading instructions")
    
    prompt_template = SCRIPT_PROMPT_WITH_INSTRUCTIONS if add_reading_instructions else SCRIPT_PROMPT_TEMPLATE
    prompt = prompt_template.format(topic=topic)
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior content strategist. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1500
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # Clean JSON
    if response_text.startswith('```json'):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith('```'):
        response_text = response_text[3:-3].strip()
    
    script_data = json.loads(response_text)
    print(f"✓ Script generated ({script_data.get('estimated_duration', 45)}s)")
    print(f"✓ Lines: {len(script_data.get('formatted_script', []))}")
    
    return script_data


def save_script(script_data, output_path="generated_script.json"):
    """Save generated script to JSON file.
    
    Args:
        script_data: Script dictionary to save
        output_path: Full path where to save the script (default: root)
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Script saved to {output_path}")


def main():
    topic = input("Enter your topic: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        return
    
    # Ask for reading instructions
    add_instructions = input("Add reading instructions? (y/n): ").strip().lower() == 'y'
    
    # Generate script
    script_data = generate_script(topic, add_instructions)
    
    # Save to file
    save_script(script_data)
    
    print("\n" + "="*50)
    print("GENERATED SCRIPT:")
    print("="*50)
    print(f"\nVibe: {script_data.get('video_vibe', 'professional')}")
    print(f"Duration: ~{script_data.get('estimated_duration', 45)}s")
    print(f"Lines: {len(script_data.get('formatted_script', []))}")
    print(f"\nHook: {script_data.get('hook', 'N/A')}")
    print(f"\nFormatted Script:")
    for line in script_data.get('formatted_script', []):
        print(f"  {line}")
    print("\n" + "="*50)
    print("\nNext: Use this script with a TTS service to generate audio,")
    print("then run the Audio to Reels pipeline.")


if __name__ == '__main__':
    main()
