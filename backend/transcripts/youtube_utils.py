import subprocess
import os
import glob
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from backend.transcripts.vtt_parser import parse_vtt_file

RAW_DIR = "backend/transcripts/youtube/raw"
PARSED_DIR = "backend/transcripts/youtube/parsed"
LANG = "ko"


def sanitize_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_id = query.get("v", [""])[0]

    if not video_id:
        raise ValueError("No video ID found in URL")

    # Only keep `v` param, discard `list`, `index`, etc.
    new_query = urlencode({"v": video_id})
    sanitized = urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, "", new_query, "")
    )
    return sanitized


def extract_video_id(url: str) -> str:
    return parse_qs(urlparse(url).query).get("v", [""])[0]


def get_parsed_path(video_id: str) -> str:
    return os.path.join(PARSED_DIR, f"{video_id}.json")


def download_subtitles(video_url: str) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    command = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang",
        LANG,
        "--skip-download",
        "-P",
        RAW_DIR,
        video_url,
    ]
    subprocess.run(command, check=True)
    vtt_files = sorted(
        glob.glob(os.path.join(RAW_DIR, f"*.{LANG}.vtt")), key=os.path.getmtime
    )
    if not vtt_files:
        raise FileNotFoundError("No .vtt file found.")
    return vtt_files[-1]


def get_video_title(video_url: str) -> str:
    result = subprocess.run(
        ["yt-dlp", "--get-title", video_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


def save_parsed_transcript(video_id: str, data):
    os.makedirs(PARSED_DIR, exist_ok=True)
    with open(get_parsed_path(video_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_parsed_transcript(video_url: str, use_cache=False):
    video_url = sanitize_youtube_url(video_url)
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL or missing video ID.")

    parsed_path = get_parsed_path(video_id)
    if use_cache and os.path.exists(parsed_path):
        with open(parsed_path, encoding="utf-8") as f:
            return json.load(f)

    # download and parse transcript
    vtt_path = download_subtitles(video_url)
    parsed = parse_vtt_file(vtt_path)

    # add video title to chunks
    video_title = get_video_title(video_url)
    for chunk in parsed:
        chunk["videoId"] = video_id
        chunk["videoTitle"] = video_title

    save_parsed_transcript(video_id, parsed)

    return parsed


if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=R5T6Dld-DqM&list=PLKcYGHfhbZWE4yig77itX4QQyXeWgo9Do&index=2"
    parsed = get_parsed_transcript(test_url, use_cache=False)
    print(json.dumps(parsed[:3], ensure_ascii=False, indent=2))  # show first 3 chunks
