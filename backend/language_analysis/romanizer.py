import re

# -----------------------------------------------------------------------------
# This romanizer is largely inspired by Ilkyu Ju (@osori) and contains:
#   - Partial/incomplete Korean syllable handling (e.g., ㅋㅋㅋ)
#   - Special “consonant + vowel” cases
#   - Consonant assimilation rules
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# VOWEL & CONSONANT MAPPINGS
# -----------------------------------------------------------------------------
vowel = {
    # simple vowels
    "ㅏ": "a",
    "ㅓ": "eo",
    "ㅗ": "o",
    "ㅜ": "u",
    "ㅡ": "eu",
    "ㅣ": "i",
    "ㅐ": "ae",
    "ㅔ": "e",
    "ㅚ": "oe",
    "ㅟ": "wi",
    # diphthongs
    "ㅑ": "ya",
    "ㅕ": "yeo",
    "ㅛ": "yo",
    "ㅠ": "yu",
    "ㅒ": "yae",
    "ㅖ": "ye",
    "ㅘ": "wa",
    "ㅙ": "wae",
    "ㅝ": "wo",
    "ㅞ": "we",
    "ㅢ": "ui",
}

# initial-position consonants (choseong)
onset = {
    "ᄀ": "g",
    "ᄁ": "kk",
    "ᄏ": "k",
    "ᄃ": "d",
    "ᄄ": "tt",
    "ᄐ": "t",
    "ᄇ": "b",
    "ᄈ": "pp",
    "ᄑ": "p",
    "ᄌ": "j",
    "ᄍ": "jj",
    "ᄎ": "ch",
    "ᄉ": "s",
    "ᄊ": "ss",
    "ᄒ": "h",
    "ᄂ": "n",
    "ᄆ": "m",
    "ᄅ": "r",
    "ᄋ": "",
}

# final-position consonants (jongseong)
coda = {
    "ᆨ": "k",
    "ᆩ": "k",
    "ᆪ": "k",  # ㄱ
    "ᆫ": "n",
    "ᆬ": "n",
    "ᆭ": "n",  # ㄴ
    "ᆮ": "t",
    "ᆯ": "l",
    "ᆰ": "k",
    "ᆱ": "m",
    "ᆲ": "p",
    "ᆳ": "s",
    "ᆴ": "t",
    "ᆵ": "p",
    "ᆶ": "l",
    "ᆷ": "m",
    "ᆸ": "p",
    "ᆹ": "p",
    "ᆺ": "t",
    "ᆻ": "t",
    "ᆼ": "ng",
    "ᆽ": "t",
    "ᆾ": "t",
    "ᇀ": "t",
    "ᇁ": "p",
    "ᇂ": "t",
    None: "",
}

# map “high‐range” jamo to “low‐range” choseong/coda keys
unicode_onset_lower = {
    "ㄱ": "ᄀ",
    "ㄲ": "ᄁ",
    "ㅋ": "ᄏ",
    "ㄷ": "ᄃ",
    "ㄸ": "ᄄ",
    "ㅌ": "ᄐ",
    "ㅂ": "ᄇ",
    "ㅃ": "ᄈ",
    "ㅍ": "ᄑ",
    "ㅈ": "ᄌ",
    "ㅉ": "ᄍ",
    "ㅊ": "ᄎ",
    "ㅅ": "ᄉ",
    "ㅆ": "ᄊ",
    "ㅎ": "ᄒ",
    "ㄴ": "ᄂ",
    "ㅁ": "ᄆ",
    "ㄹ": "ᄅ",
    "ㅇ": "ᄋ",
}

unicode_coda_lower = {
    "ㄱ": "ᆨ",
    "ㄷ": "ᆮ",
    "ㅂ": "ᆸ",
    "ㅍ": "ᇁ",
    "ㄴ": "ᆫ",
    "ㅇ": "ᆼ",
    "ㅁ": "ᆷ",
    "ㄹ": "ᆯ",
}

# Lists to help decompose/construct Hangul
unicode_initial = [chr(cp) for cp in range(4352, 4371)]  # 19 entries
unicode_medial = [
    "ㅏ",
    "ㅐ",
    "ㅑ",
    "ㅒ",
    "ㅓ",
    "ㅔ",
    "ㅕ",
    "ㅖ",
    "ㅗ",
    "ㅘ",
    "ㅙ",
    "ㅚ",
    "ㅛ",
    "ㅜ",
    "ㅝ",
    "ㅞ",
    "ㅟ",
    "ㅠ",
    "ㅡ",
    "ㅢ",
    "ㅣ",
]

unicode_final = [None] + [chr(cp) for cp in range(0x11A8, 0x11C3)]  # 28 entries

# For decomposing double consonants (겹받침)
double_consonant_final = {
    "ㄳ": ("ㄱ", "ㅅ"),
    "ㄵ": ("ᆫ", "ㅈ"),
    "ᆭ": ("ᆫ", "ᇂ"),
    "ㄺ": ("ㄹ", "ㄱ"),
    "ㄻ": ("ㄹ", "ㅁ"),
    "ㄼ": ("ㄹ", "ㅂ"),
    "ㄽ": ("ㄹ", "ㅅ"),
    "ㄾ": ("ㄹ", "ㅌ"),
    "ㄿ": ("ㄹ", "ㅍ"),
    "ㅀ": ("ㄹ", "ᇂ"),
    "ㅄ": ("ㅂ", "ㅅ"),
    "ㅆ": ("ㅅ", "ㅅ"),
}

# Manual map: final jamo → matching initial jamo
final_to_initial_map = {
    "ᆨ": "ᄀ",  # ㄱ
    "ᆩ": "ᄁ",  # ㄲ
    "ᆪ": "ᄀ",  # ㄱㅅ → ㄱ
    "ᆫ": "ᄂ",  # ㄴ
    "ᆬ": "ᄂ",  # ㄴㅈ → ㄴ
    "ᆭ": "ᄂ",  # ㄴㅎ → ㄴ
    "ᆮ": "ᄃ",  # ㄷ
    "ᆯ": "ᄅ",  # ㄹ
    "ᆰ": "ᄀ",  # ㄹㄱ → ㄱ
    "ᆱ": "ᄆ",  # ㄹㅁ → ㅁ
    "ᆲ": "ᄇ",  # ㄹㅂ → ㅂ
    "ᆳ": "ᄉ",  # ㄹㅅ → ㅅ
    "ᆴ": "ᄐ",  # ㄹㅌ → ㅌ
    "ᆵ": "ᄑ",  # ㄹㅍ → ㅍ
    "ᆶ": "ᄒ",  # ㄹㅎ → ㅎ
    "ᆷ": "ᄆ",  # ㅁ
    "ᆸ": "ᄇ",  # ㅂ
    "ᆹ": "ᄇ",  # ㅂㅅ → ㅂ
    "ᆺ": "ᄉ",  # ㅅ
    "ᆻ": "ᄊ",  # ㅆ
    "ᆼ": "ᄋ",  # ㅇ (nasal carryover)
    "ᆽ": "ᄌ",  # ㅈ
    "ᆾ": "ᄎ",  # ㅊ
    "ᇀ": "ᄐ",  # ㅌ
    "ᇁ": "ᄑ",  # ㅍ
    "ᇂ": "ᄒ",  # ㅎ
}

# suppress ㅎ-dropping for verbs like 않다, 놓다, 좋다
VERB_STEMS_TO_PRESERVE = {"않", "놓", "좋"}

NULL_CONSONANT = "ᄋ"
HANGUL_OFFSET = 0xAC00


# -----------------------------------------------------------------------------
# UTILITY: Decompose a full Hangul syllable into (initial, medial, final)
# -----------------------------------------------------------------------------
class Syllable:
    def __init__(self, char: str):
        self.char = char
        if self.is_hangul(char):
            code = ord(char) - HANGUL_OFFSET
            initial_idx = code // 588
            remainder = code % 588
            medial_idx = remainder // 28
            final_idx = remainder % 28

            # Now these lookups are guaranteed to be in‐range, because
            #   0 <= initial_idx <= 18
            #   0 <= medial_idx  <= 20
            #   0 <= final_idx   <= 27
            self.initial = unicode_initial[initial_idx]
            self.medial = unicode_medial[medial_idx]
            self.final = unicode_final[final_idx]
        else:
            # not a precomposed Hangul syllable, so don’t index into those arrays
            self.initial = None
            self.medial = None
            self.final = None

    def is_hangul(self, ch: str) -> bool:
        return HANGUL_OFFSET <= ord(ch) <= 0xD7A3

    def final_to_initial(self, final_jamo: str) -> str:
        if final_jamo in final_to_initial_map:
            return final_to_initial_map[final_jamo]
        print(f"⚠️ Warning: No mapping for final_jamo={final_jamo!r}")
        return "ᄋ"  # fallback null consonant (safe default)

    def __repr__(self):
        if not self.initial:
            return self.char  # leave non‐Hangul as is
        # otherwise rebuild from (initial, medial, final)
        init_idx = unicode_initial.index(self.initial)
        med_idx = unicode_medial.index(self.medial)
        fin_idx = unicode_final.index(self.final) if self.final in unicode_final else 0
        codept = HANGUL_OFFSET + (init_idx * 588) + (med_idx * 28) + fin_idx
        return chr(codept)

    def __str__(self):
        return self.__repr__()


# -----------------------------------------------------------------------------
# APPLY RULES: Handle consonant assimilation / special “ㅎ” cases / double consonants
# -----------------------------------------------------------------------------
class RomanizeRules:
    def __init__(self, text: str):
        self._syllables = [Syllable(ch) for ch in text]
        self.pronounced = "".join(str(syl) for syl in self._apply_rules())

    def _apply_rules(self) -> list[Syllable]:
        for idx, syl in enumerate(self._syllables):
            try:
                nxt = self._syllables[idx + 1]
                if not nxt.is_hangul(nxt.char):
                    nxt = None
            except IndexError:
                nxt = None

            final = syl.final
            next_initial = nxt.initial if nxt else None
            final_exists = final not in (None, "")
            final_before_consonant = final_exists and next_initial not in (None, NULL_CONSONANT)
            final_before_vowel = final_exists and next_initial == NULL_CONSONANT

            # ㅎ-based assimilation (e.g., 놓고 → 노코) — but skip verb stems like "않", "놓", "좋"
            if final in ("ᇂ", "ᆭ", "ᆶ") and nxt:
                if syl.char in VERB_STEMS_TO_PRESERVE:
                    continue  # preserve final ㅎ and skip all assimilation

                if next_initial in ("ᄀ", "ᄃ", "ᄌ", "ᄉ"):
                    nxt.initial = {"ᄀ": "ᄏ", "ᄃ": "ᄐ", "ᄌ": "ᄎ", "ᄉ": "ᄊ"}[next_initial]
                    syl.final = None
                elif next_initial == "ᄂ":
                    syl.final = "ᆯ" if final == "ᆶ" else "ᆫ"
                elif next_initial == NULL_CONSONANT:
                    syl.final = "ᆯ" if final == "ᆶ" else "ᆫ"
            elif final == "ᇂ":
                syl.final = None

            # consonant assimilation
            if final_before_consonant and final != NULL_CONSONANT:
                if final in ["ᆩ", "ᆿ", "ᆪ", "ㄺ"]:
                    syl.final = "ᆨ"
                elif final in ["ᆺ", "ᆻ", "ᆽ", "ᆾ", "ᇀ"]:
                    syl.final = "ᆮ"
                elif final in ["ᇁ", "ㅄ", "ㄿ"]:
                    syl.final = "ᆸ"
                elif final in ["ᆲ", "ᆳ", "ᆴ"]:
                    syl.final = "ᆯ"
                elif final == "ᆬ":
                    syl.final = "ᆫ"
                elif final == "ᆱ":
                    syl.final = "ᆷ"

                if syl.final == "ᆫ" and next_initial == "ᄅ":
                    syl.final = "ᆯ"
                if syl.final == "ᆨ" and next_initial in ("ᄂ", "ᄅ"):
                    syl.final = "ᆼ"
                    if next_initial == "ᄅ":
                        nxt.initial = "ᄂ"
                if syl.final == "ᆼ" and next_initial == "ᄅ":
                    nxt.initial = "ᄂ"

            # move final to next initial if vowel
            if final_before_vowel:
                if syl.final != "ᆼ":
                    nxt.initial = nxt.final_to_initial(syl.final)
                    syl.final = None

            # split double finals
            if syl.final in double_consonant_final and nxt:
                first_final, second_final = double_consonant_final[syl.final]
                syl.final = first_final
                nxt.initial = nxt.final_to_initial(second_final)

        return self._syllables


# -----------------------------------------------------------------------------
# MAIN ROMANIZER CLASS
# -----------------------------------------------------------------------------
class Romanizer:
    """
    Converts Korean text (with partial/incomplete syllables, jamo, etc.) into a
    hyphenated, romanized string. English segments are kept intact (no hyphens).
    """

    _RE_HANGUL_SYLLABLE = re.compile(r"[가-힣]")
    _RE_JAMO = re.compile(r"[ㄱ-ㅣ]")
    _RE_ENGLISH = re.compile(r"[A-Za-z]")

    # Punctuation/space boundaries where we should NOT insert a hyphen:
    _NO_HYPHEN = {" ", ";", ":", ",", "-", "--", "."}

    def __init__(self, text: str):
        self.text = text

    def romanize(self) -> str:
        # Step 1: Apply pronunciation rules, then iterate each character
        pronounced = RomanizeRules(self.text).pronounced
        parts: list[str] = []

        for ch in pronounced:
            # Full Hangul syllable
            if Romanizer._RE_HANGUL_SYLLABLE.match(ch):
                syl = Syllable(ch)
                try:
                    o = onset[syl.initial]
                    v = vowel[syl.medial]
                    c = coda[syl.final]
                    parts.append(o + v + c)
                except KeyError:
                    parts.append("#")

            # Isolated Jamo (ㄱ, ㅏ, etc.)
            elif Romanizer._RE_JAMO.match(ch):
                if ch in unicode_onset_lower:
                    parts.append(onset[unicode_onset_lower[ch]])
                elif ch in vowel:
                    parts.append(vowel[ch])
                elif ch in unicode_coda_lower:
                    parts.append(coda[unicode_coda_lower[ch]])
                else:
                    parts.append("#")

            # English letter: accumulate consecutive letters
            elif Romanizer._RE_ENGLISH.match(ch):
                if (
                    parts
                    and parts[-1].isalpha()
                    and Romanizer._RE_ENGLISH.match(parts[-1][0])
                ):
                    parts[-1] += ch
                else:
                    parts.append(ch)

            # Anything else: punctuation, numbers, space, etc.
            else:
                parts.append(ch)

        # Step 2: Hyphenate between “parts” unless separated by NO_HYPHEN characters
        result: list[str] = []
        for idx, segment in enumerate(parts):
            result.append(segment)
            if idx < len(parts) - 1:
                nxt = parts[idx + 1]
                if segment in Romanizer._NO_HYPHEN or nxt in Romanizer._NO_HYPHEN:
                    continue
                result.append("-")

        return "".join(result)


def romanize(text: str) -> str:
    return Romanizer(text).romanize()


# -----------------------------------------------------------------------------
# If you want to quickly test a few examples, uncomment the following:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # tests = [
    #     "안녕하세요.",
    #     "저는 대학생 입니다 ㅋㅋㅋ ㅏㅏㅏ.",
    #     "종로, 그렇지, 입학, 행복하다, 곧할거야",
    #     "This doesn’t contain any Korean #@12345?!"
    # ]
    tests = ["작심삼일로 끝나지 않도록"]
    for txt in tests:
        print(f"{txt!r}  →  {Romanizer(txt).romanize()}")
