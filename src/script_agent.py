import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Professional YouTube Shorts script structure
SCRIPT_PROMPT_TEMPLATE = """You are an 11-year veteran YouTube Shorts creator with millions of views. Generate a 40-50 second story-driven script.

Topic: {topic}

STRUCTURE:
[0-3s] PATTERN INTERRUPT HOOK: Question, controversial statement, or relatable scenario that stops scrolling
[3-15s] STORY/EXAMPLE: Concrete scenario viewers can visualize. Make it REAL, not abstract
[15-35s] THE REVEAL: Explain the insight with WHY it works. Use mini-examples or demonstrations
[35-40s] AUTHORITY (optional): Brief social proof if relevant ("FBI uses this", "Studies show...")
[40-50s] STRONG CTA: Specific action ("Try this tonight"), engagement ask ("Comment if..."), NOT generic

WRITING STYLE:
- Conversational tone like talking to a friend at a bar
- Use contractions, casual language ("You know that..." not "One must consider...")
- Story-driven with concrete examples, NOT abstract facts
- Emotional connection - make viewer FEEL something (curiosity, fear, excitement)
- Each line: 5-12 words, complete thought
- NO robotic phrases: "status quo", "embark on", "unlock potential"
- Write like a HUMAN creator, not a Wikipedia article

EXAMPLE STRUCTURE (for reference only):
"Your friend just lied to you. And you missed it."
"Here's the thing - liars need time to construct their story."
"Truth? That's instant. No thinking required."
"It's called the 3-second delay rule."
"Ask a question. Count silently. More than 3 seconds? Red flag."
"Where were you last night? Honest person: immediate answer."
"Liar: Uhh... I was... at the gym. Yeah, gym."
"FBI interrogators use this in every interview."
"Try it tonight at dinner. You'll be shocked."

OUTPUT FORMAT (JSON only):
{{
  "formatted_script": [
    "Hook sentence that stops scrolling (5-12 words).",
    "Story setup with concrete scenario (5-12 words).",
    "Build the narrative naturally (5-12 words).",
    "Reveal the insight with example (5-12 words).",
    "Specific actionable CTA (5-12 words)."
  ],
  "video_vibe": "professional|dramatic|energetic|aggressive|modern|playful|calm",
  "hook": "First sentence",
  "estimated_duration": 45
}}

Generate the script now. Return ONLY valid JSON."""

SCRIPT_PROMPT_WITH_INSTRUCTIONS = """You are an 11-year veteran YouTube Shorts creator with millions of views. Generate a 40-50 second story-driven script WITH minimal reading instructions.

Topic: {topic}

STRUCTURE:
[0-3s] PATTERN INTERRUPT HOOK: Question, controversial statement, or relatable scenario that stops scrolling
[3-15s] STORY/EXAMPLE: Concrete scenario viewers can visualize. Make it REAL, not abstract
[15-35s] THE REVEAL: Explain the insight with WHY it works. Use mini-examples or demonstrations
[35-40s] AUTHORITY (optional): Brief social proof if relevant ("FBI uses this", "Studies show...")
[40-50s] STRONG CTA: Specific action ("Try this tonight"), engagement ask ("Comment if..."), NOT generic

WRITING STYLE:
- Conversational tone like talking to a friend at a bar
- Use contractions, casual language ("You know that..." not "One must consider...")
- Story-driven with concrete examples, NOT abstract facts
- Emotional connection - make viewer FEEL something (curiosity, fear, excitement)
- Each line: 5-12 words, complete thought
- NO robotic phrases: "status quo", "embark on", "unlock potential"
- Write like a HUMAN creator, not a Wikipedia article

READING INSTRUCTIONS (CRITICAL RULES):
- Add ONLY 4-5 instructions for the ENTIRE script
- Place instructions ONLY at major section transitions (Hook, Story, Reveal, CTA)
- Do NOT add instructions for every line
- Use [Micro beat] for 0.2s pauses instead of long silences
- Format: [Hook – Intriguing & Fast], [Micro beat], [Reveal – Confident tone]
- Keep pacing FAST and CONVERSATIONAL for high-retention

EXAMPLE STRUCTURE (for reference only):
{{
  "formatted_script": [
    "[Hook – Intriguing & Fast]",
    "Your friend just lied to you. And you missed it.",
    "[Micro beat]",
    "Here's the thing - liars need time to construct their story.",
    "Truth? That's instant. No thinking required.",
    "It's called the 3-second delay rule.",
    "[Reveal – Confident tone]",
    "Ask a question. Count silently. More than 3 seconds? Red flag.",
    "Where were you last night? Honest person: immediate answer.",
    "Liar: Uhh... I was... at the gym. Yeah, gym.",
    "FBI interrogators use this in every interview.",
    "[CTA – Encouraging]",
    "Try it tonight at dinner. You'll be shocked."
  ],
  "video_vibe": "professional",
  "hook": "Your friend just lied to you. And you missed it.",
  "estimated_duration": 45
}}

OUTPUT FORMAT (JSON only):
{{
  "formatted_script": [
    "[Hook – tone description]",
    "Hook sentence (5-12 words).",
    "[Micro beat]",
    "Story sentence (5-12 words).",
    "Continue narrative (5-12 words).",
    "[Instruction only at major transition]",
    "Reveal insight (5-12 words).",
    "Specific CTA (5-12 words)."
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
