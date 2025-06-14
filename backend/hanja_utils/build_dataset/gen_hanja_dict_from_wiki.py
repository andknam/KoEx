import requests
from bs4 import BeautifulSoup
import json

def scrape_korean_words_from_wikipedia(topics):
    words = set()
    for topic in topics:
        url = f"https://ko.wikipedia.org/wiki/{topic}"
        print(f"🌐 Fetching: {url}")
        res = requests.get(url)
        if res.status_code != 200:
            print(f"⚠️ Failed to fetch {url}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        for el in soup.find_all(['li', 'td', 'p']):
            text = el.get_text(strip=True)
            for token in text.split():
                if 2 <= len(token) <= 6 and all('가' <= ch <= '힣' for ch in token):
                    words.add(token)

    final_words = list(words)
    print(f"✅ Scraped {len(final_words)} unique Korean words")
    return {word: {} for word in final_words}

if __name__ == "__main__":
    topics = [
        "한국어", "조선시대", "한복", "유교", "세종대왕", "불교", "교육", "한국_문학",
        "대한민국", "한국_전쟁", "민주화_운동", "헌법", "정치_제도", "유엔",
        "인공지능", "과학_기술", "정보통신", "반도체", "인터넷", "의학",
        "서울", "교통", "음식", "환경", "건강", "경제",
        "영화", "음악", "아이돌", "대중문화", "인터넷_문화",
        "철학", "논리학", "윤리학", "사회학", "심리학", "종교"
    ]

    korean_word_dict = scrape_korean_words_from_wikipedia(topics)

    with open("./korean_word_dict.json", "w", encoding="utf-8") as f:
        json.dump(korean_word_dict, f, ensure_ascii=False, indent=2)

    print("📁 Saved korean_word_dict.json")
