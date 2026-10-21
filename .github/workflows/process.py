import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

video_url = os.environ.get("YOUTUBE_URL")
api_key = os.environ.get("GEMINI_API_KEY")

if not video_url:
    raise ValueError("YOUTUBE_URL environment variable is missing")

# Extract Video ID from URL
match = re.search(r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})", video_url)
if not match:
    raise ValueError("Invalid YouTube URL")
video_id = match.group(1)

# Extract Transcript
try:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join([item['text'] for item in transcript_list])
except Exception as e:
    print(f"Error fetching transcript: {e}")
    transcript_text = "Transcript directly available nahi ahe."

# Process with Gemini API
client = genai.Client(api_key=api_key)
prompt = f"""
Analyze this YouTube transcript and format it into a structured note for a Second Brain knowledge base:

1. **Core Concept & Summary**
2. **Key Takeaways & Actionable Insights**
3. **Important Code Snippets / Technical Pointers** (if applicable)
4. **Structured JSON Bit & Tags**

Transcript:
{transcript_text}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Save Note to Repository
os.makedirs("notes", exist_ok=True)
filename = f"notes/video_{video_id}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Successfully created note: {filename}")
