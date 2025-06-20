import subprocess
import os
import sys
import glob
import json
from vtt_parser import parse_vtt_file

RAW_DIR = "youtube/raw"
PARSED_DIR = "youtube/parsed"
LANG = "ko"

def download_subtitles(video_url: str) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    command = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", LANG,
        "--skip-download",
        "-P", RAW_DIR,
        video_url
    ]

    print("Running yt-dlp...")
    subprocess.run(command, check=True)

    # Find the most recent .vtt file
    vtt_files = sorted(glob.glob(os.path.join(RAW_DIR, f"*.{LANG}.vtt")), key=os.path.getmtime)
    if not vtt_files:
        raise FileNotFoundError("No subtitle file was found after yt-dlp ran.")

    latest_vtt = vtt_files[-1]
    print(f"Found subtitle file: {latest_vtt}")
    
    return latest_vtt

def parse_and_save(vtt_path: str):
    os.makedirs(PARSED_DIR, exist_ok=True)

    parsed = parse_vtt_file(vtt_path)

    filename = os.path.basename(vtt_path).replace(".vtt", ".json")
    output_path = os.path.join(PARSED_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"Parsed output saved to: {output_path}")

def main():
    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        url = input("Paste YouTube URL: ").strip()

    vtt_path = download_subtitles(url)
    parse_and_save(vtt_path)

if __name__ == "__main__":
    main()
