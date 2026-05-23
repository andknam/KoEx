## Language Analysis Overview

KoEx uses a multi-stage language analysis pipeline to convert raw Korean input into semantically meaningful components.

This powers both the standalone language analysis and integrated subtitle analysis within the YouTube player.

### Processing Flow
1. Preprocess
    - Strip all non-Hangul characters
2. Normalize spacing (띄어쓰기)
    - Send the cleaned Korean text to `gpt-4o-mini` for lightweight spacing correction
    - Preserve wording and meaning; only add natural Korean spacing
    - This helps Komoran avoid bad splits caused by glued text
        - Example: `이루고나니` → `이루고 나니`
3. Idioms (사자성어)
    - Replace detected idioms with placeholders (`＠＠{idx}` using U+FF20 full-width ＠)
4. Tokenize
    - Use KoNLPy Komoran to tokenize input with placeholders
5. Grammar Chunking
    - Merge auxiliary grammar using rules from `auxiliary_grammar_rules.yaml`
        - At each position, greedily apply the longest matching rule
        - Each rule specifies a sequence of tags (and optionally tokens) that represent a meaningful grammar chunk
        - Example (`aux_negation_adverb_past`)
            - pattern:
                - token: 안
                    - tag: MAG
                - tag: VV
                - tag: EP
                - tag: EF (use `TAG_EQUIVALENTS` map to match `EF` or `EC` here)
            - Input: `[('나', 'NP'), ('는', 'JX'), ('안', 'MAG'), ('가', 'VV'), ('았', 'EP'), ('어요', 'EC')]`
            - Output: `[('나', 'NP'), ('는', 'JX'), ('안갔어요', 'VV')]`
6. Morphological Grouping (meaning)
    - Greedily group linguistically meaningful units (typically noun/verb + ending)
        - e.g. `[("평화", "NNG"), ("롭", "XSA"), ("다", "EF")]` → `[("평화롭다", "VA")]`
7. Morphophonological Contraction (sound)
    - Contract verb stems (e.g. `하 + 였 → 했`)
8. Finalize tokens
    - Substitute idiom placeholders with idioms
    - Filter out excluded tokens (stopwords, particles, etc.)
9. Extract and tag candidate Korean words
    - Extract nouns and verbs from the final tokens
    - Return both base and derived forms if applicable (e.g. `평화` (base) vs `평화롭다` (derived))
    - Preserve the order in which words appear in the sentence
10. Final GPT integration
    - `hanja_batcher`
        - Input all base words --> returns the Hanja form of a word (if applicable), Korean gloss, Pinyin, and English gloss 
    - `korean_analyzer`
        - Input the original query --> returns the English gloss
        - Input all words (use derived only if applicable) --> returns the word, part-of-speech, English gloss, and example sentence in Korean
11. Romanization
    - Decompose Hangul syllables into initial (초성), medial (중성), and final (종성)
    - Apply phonological rules:
        - Handle `ㅎ` transformations
        - Apply consonant assimilation (e.g. 받침 + next consonant)
        - Split double final consonants
    - Handle incomplete or partial Hangul/Jamo input (e.g. `ㅋㅋㅋ`, `ㅏㅏㅏ`)
    - Output syllable-level romanization with hyphen separation (e.g. `an-nyeong-ha-se-yo`)
    - Supports Hangul, English, and unknown letters

### Output Layers

1. Romanization
2. Sentence gloss
3. Korean word information
4. Hanja annotations

### POS Tag Reference

KoEx uses KoNLPy’s Komoran wrapper. See the [KoNLPy Komoran API docs](https://konlpy.org/en/latest/api/konlpy.tag/#komoran-class) and the [KOMORAN POS table](https://docs.komoran.kr/firststep/postypes.html) for the full tag list.

The pipeline mostly cares about these tag families:

| Family | Tags | Used for |
| --- | --- | --- |
| Nouns | `NNG`, `NNP`, `NNB`, `NR` | Candidate words such as `꿈`, `곁`, names, bound nouns, numerals |
| Predicates | `VV`, `VA`, `VX`, `VCN`, `VCP` | Verbs, adjectives, auxiliaries, copulas |
| Roots / suffixes | `XR`, `XSV`, `XSA`, `XSN` | Roots like `초라`; derivations like `공부하다`, `초라하다`, `가능성` |
| Adverbs / determiners | `MAG`, `MAJ`, `MM` | Adverbs like `가장`, `너무`; determiners like `이`, `그` |
| Particles | `JKS`, `JKO`, `JKB`, `JKG`, `JX`, `JC` | Usually skipped or filtered out |
| Endings | `EP`, `EC`, `EF`, `ETM` | Verb endings used for grammar chunking |
| Other text | `SN`, `SL`, `SH` | Numbers, foreign words, Hanja |

Content extraction keeps broad semantic tags first, then removes common particles/filler words through `EXCLUDE_TOKENS`.

### Future Improvements
- Perform idiom detection using a hardcoded list to remove dependence on GPT
- Extend the grammar rules to support more patterns (non-auxiliary)
    - conjunctions (`일하고 나서`)
    - conditionals (`좋으면`)
    - supposition (`갈 것 같아`)
    - reported speech / quotatives (`공부하자고 했다`)
    - noun-modifying clauses (`보던 영화`)
    - etc.
