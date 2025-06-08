from hanja import translate
from pycccedict import CedictParser  # or your custom hanja-pinyin-meaning dict

# Load your hanja→pinyin→meaning dict
with open("hanja_char_dict.json", encoding="utf-8") as f:
    hanja_data = json.load(f)

def decompose_korean_word(word: str) -> list:
    results = []
    for ch in word:
        hanja_char = translate(ch, 'substitution')
        if ch == hanja_char:
            results.append({"char": ch, "hanja": None, "pinyin": None, "meaning": None})
        else:
            info = hanja_data.get(hanja_char, {})
            results.append({
                "char": ch,
                "hanja": hanja_char,
                "pinyin": info.get("pinyin"),
                "meaning": info.get("meaning")
            })
    return results