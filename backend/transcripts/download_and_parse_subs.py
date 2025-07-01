import os
from urllib.parse import urlparse, parse_qs
from backend.transcripts.youtube_utils import get_parsed_transcript, save_parsed_transcript

PARSED_DIR = "backend/transcripts/youtube/parsed"

def main():
    # if len(sys.argv) >= 2:
    #     url = sys.argv[1]
    # else:
    #     url = input("Paste YouTube URL: ").strip()

    urls = [
        "https://www.youtube.com/watch?v=PmtW_4WSWMU",
        "https://www.youtube.com/watch?v=frztAv2VZQY",
        "https://www.youtube.com/watch?v=21CeSaC8nOI",
        "https://www.youtube.com/watch?v=CDlfiP3L3H4",
        "https://www.youtube.com/watch?v=7PRXUtYxWiw",
        "https://www.youtube.com/watch?v=gAQYlPSy844",
        "https://www.youtube.com/watch?v=Jm2C3vI3Ke4",
        "https://www.youtube.com/watch?v=lTaYRLpsioU",
        "https://www.youtube.com/watch?v=ZjtMzMBQoXY",
        "https://www.youtube.com/watch?v=Tsfsa1BbPxM",
        "https://www.youtube.com/watch?v=DhF2ol__Yg0",
        "https://www.youtube.com/watch?v=Kt_TE9zgPO8",
        "https://www.youtube.com/watch?v=qQxLXILF3Is",
        "https://www.youtube.com/watch?v=eXdfme2BZA0",
        "https://www.youtube.com/watch?v=seekmxnJFZM"
    ]

    for url in urls:
        parsed = get_parsed_transcript(url)

        video_id = parse_qs(urlparse(url).query).get("v", [""])[0]
        if not video_id:
            raise ValueError("Couldn't extract video ID.")

        output_path = os.path.join(PARSED_DIR, f"{video_id}.json")
        print(f"✅ Saved parsed transcript to {output_path}")

if __name__ == "__main__":
    main()