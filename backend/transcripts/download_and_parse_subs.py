# backend/transcripts/download_and_parse_subs.py
import sys
import os
from backend.transcripts.youtube_utils import get_parsed_transcript, save_parsed_to_json

PARSED_DIR = "backend/transcripts/youtube/parsed"

def main():
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = input("Paste YouTube URL: ").strip()

    parsed = get_parsed_transcript(url)

    from urllib.parse import urlparse, parse_qs
    video_id = parse_qs(urlparse(url).query).get("v", [""])[0]
    if not video_id:
        raise ValueError("Couldn't extract video ID.")

    output_path = os.path.join(PARSED_DIR, f"{video_id}.json")
    save_parsed_to_json(parsed, output_path)
    print(f"✅ Saved parsed transcript to {output_path}")

if __name__ == "__main__":
    main()