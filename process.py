import os
import re
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

video_url = os.environ.get("YOUTUBE_URL")
api_key = os.environ.get("GEMINI_API_KEY")

if not video_url:
    raise ValueError("YOUTUBE_URL is missing")

if not api_key:
    raise ValueError("GEMINI_API_KEY secret is missing in GitHub repository settings.")

# Extract Video ID
match = re.search(r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})", video_url)
if not match:
    raise ValueError("Invalid YouTube URL")
video_id = match.group(1)

# Fetch Transcript
try:
    yt = YouTubeTranscriptApi()
    transcript_list = yt.fetch(video_id)
    transcript_text = " ".join([item['text'] for item in transcript_list])
except Exception as e:
    print(f"Error fetching transcript via fetch(): {e}")
    try:
        # Fallback for different library versions
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
    except Exception as ex:
        print(f"Fallback failed: {ex}")
        transcript_text = "Transcript directly available nahi ahe."

# Call Gemini API
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

# Save Note locally
os.makedirs("notes", exist_ok=True)
filename = f"notes/video_{video_id}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Successfully created note: {filename}")

# Git Push Back to Repository
subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"Add note for video {video_id}"])
subprocess.run(["git", "push"])
