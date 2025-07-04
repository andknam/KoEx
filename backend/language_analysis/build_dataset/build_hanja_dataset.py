import requests
from bs4 import BeautifulSoup
import json
import time
import re
from collections import defaultdict

### === STEP 1: Scrape Wiktionary for char-level info ===


def fetch_char_data(char):
    url = f"https://en.wiktionary.org/wiki/{char}"
    res = requests.get(url)
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    entry = {"pinyin": "", "meaning": ""}

    # Try to find a pinyin transcription, not IPA
    pinyin_el = soup.select_one("span[lang=cmn] span.tr")
    if pinyin_el:
        entry["pinyin"] = pinyin_el.get_text(strip=True)
    else:
        # fallback to IPA if pinyin isn't available
        pinyin_ipa = soup.find("span", class_="IPA")
        if pinyin_ipa:
            entry["pinyin"] = pinyin_ipa.get_text(strip=True)

    # Get English gloss
    defn_block = soup.find("span", id="Chinese")
    if defn_block:
        ul = defn_block.find_next("ol")
        if ul:
            li = ul.find("li")
            if li:
                entry["meaning"] = li.get_text(strip=True).split(". ")[-1]

    return entry if entry["pinyin"] or entry["meaning"] else None


def extract_korean_readings(soup):
    readings = set()
    for span in soup.find_all("span", attrs={"lang": re.compile(r"^ko")}):
        text = span.get_text(strip=True)
        if all("가" <= ch <= "힣" for ch in text) and 1 <= len(text) <= 2:
            readings.add(text)

    ko_pron_matches = re.findall(r"\{\{ko-pron\|([가-힣]+)", soup.prettify())
    readings.update(ko_pron_matches)
    return list(readings)


def build_char_and_reverse_dict(unique_hanja_chars):
    char_dict = {}
    reverse_dict = defaultdict(list)

    for char in sorted(set(unique_hanja_chars)):
        print(f"🔍 Fetching {char}")
        url = f"https://en.wiktionary.org/wiki/{char}"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"⚠️ Failed for {char}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        # Char-level metadata
        char_data = fetch_char_data(char)
        if char_data:
            char_dict[char] = char_data

        # Reverse Hangul lookup
        hangul_readings = extract_korean_readings(soup)
        for reading in hangul_readings:
            reverse_dict[reading].append(char)

        time.sleep(1.0)

    return char_dict, reverse_dict


### === STEP 2: Use reverse_dict to convert Korean words to Hanja ===


def lookup_hanja_for_word(word, reverse_dict):
    hanja_chars = []
    for syllable in word:
        hanjas = reverse_dict.get(syllable, [])
        if hanjas:
            hanja_chars.append(hanjas[0])  # pick first for now
        else:
            hanja_chars.append(syllable)
    return "".join(hanja_chars), hanja_chars


def enrich_korean_word_dict(korean_dict, reverse_dict, char_dict):
    enriched = {}
    for word in korean_dict:
        hanja_word, hanja_chars = lookup_hanja_for_word(word, reverse_dict)
        seen = set()
        ordered_chars = [
            c for c in hanja_chars if c in char_dict and not (c in seen or seen.add(c))
        ]

        enriched[word] = {"hanja": hanja_word, "chars": ordered_chars}
    return enriched


### === MAIN ===

if __name__ == "__main__":
    # Load input word list
    with open("korean_word_dict_test.json", encoding="utf-8") as f:
        korean_word_dict = json.load(f)

    # Step 1: Get all unique syllables and map to Hanja
    all_hangul_syllables = set()
    for word in korean_word_dict:
        for ch in word:
            if "가" <= ch <= "힣":
                all_hangul_syllables.add(ch)

    print(f"🔡 Found {len(all_hangul_syllables)} unique Hangul syllables")

    # Step 2: Build hanja char dict + reverse map
    hanja_char_dict, hangul_to_hanja = build_char_and_reverse_dict(all_hangul_syllables)

    with open("hanja_char_dict.json", "w", encoding="utf-8") as f:
        json.dump(hanja_char_dict, f, ensure_ascii=False, indent=2)
    with open("hangul_to_hanja.json", "w", encoding="utf-8") as f:
        json.dump(hangul_to_hanja, f, ensure_ascii=False, indent=2)

    # Step 3: Enrich word dict using hanja mapping
    enriched_dict = enrich_korean_word_dict(
        korean_word_dict, hangul_to_hanja, hanja_char_dict
    )

    with open("hanja_dict_enriched.json", "w", encoding="utf-8") as f:
        json.dump(enriched_dict, f, ensure_ascii=False, indent=2)

    print(
        "📁 Saved: hanja_char_dict.json, hangul_to_hanja.json, hanja_dict_enriched.json"
    )
