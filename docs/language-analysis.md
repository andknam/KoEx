## Language Analysis Overview

KoEx uses a multi-stage language analysis pipeline to transform raw Korean input into semantic parts.

This powers both the standalone language analysis and integrated subtitle analysis within the YouTube player.

### Processing Flow

We transform the input into semantically meaningful parts via:

1. Preprocess
    - Strip all non-Hangul characters
2. Idioms (사자성어)
    - Input the full original query --> return all idioms 
    - Replace idioms with a placeholder (`＠＠{idx}` = Full-width @ (U+FF20))
3. Tokenize
    - Use KoNLPy Komoran to tokenize input with placeholders
4. Grammar Merging
    - Merge auxiliary grammar using rules from `auxiliary_grammar_rules.yaml`
        - At each position, greedily apply the longest matching rule
        - Each rule specifies a sequence of tags (and optionally tokens) that represent a meaningful grammar chunk
        - Example (`aux_negation_adverb_past`)
            - pattern:
                - token: 안
                    - tag: MAG
                - tag: VV
                - tag: EP
                - tag: EF
            - Input: `[('나', 'NP'), ('는', 'JX'), ('안', 'MAG'), ('가', 'VV'), ('았', 'EP'), ('어요', 'EC')]`
            - Output: `[('나', 'NP'), ('는', 'JX'), ('안갔어요', 'VV')]`
5. Morphological (meaning) Grouping
    - Greedily group linguistically meaningful units (typically noun/verb + ending)
        - i.e. `[("평화", "NNG"), ("롭", "XSA"), ("다", "EF")]` → `[("평화", "NNG"), ("평화롭다", "VA")]`
    - (If applicable), return the base and derived forms of the word
6. Morphophonological (sound) Contractions
    - Contract verb stems (i.e. `하 + 였 → 했`)
7. Finalize tokens
    - Substitute idiom placeholders with idioms
    - Filter out excluded tokens (stopwords, particles, etc.)
7. Extract and tag candidate Korean words
    - Extract nouns and verbs from the final tokens
    - If applicable, tag words as base or derived (`실천` (base) vs `실천하다` (derived))
8. Final GPT integration
    - `hanja_batcher`
        - Input all base words --> returns the Hanja form of a word (if applicable), Korean gloss, Pinyin, and English gloss 
    - `korean_analyzer`
        - Input the full original query --> returns the English gloss
        - Input all words (use derived only if applicable) --> returns the word, part-of-speech, English gloss, and example sentence in Korean
9. Romanization
    - Decompose Hangul syllables into initial, medial, and final components
    - Apply linguistic rules
        - Handle consonant assimilation / special “ㅎ” cases / double consonants
    - Handle incomplete/partial Hangul/Jamo sequences (i.e. `ㅋㅋㅋ`, `ㅏㅏㅏ`)
    - Output results hyphen-separated by character (i.e. `an-nyeong-ha-se-yo`)
        - Supports Hangul, English, and unknown letters

### Output Layers

1. Romanization
2. Sentence gloss
3. Korean word information
4. Hanja annotations

### Future Improvements
- Perform idiom detection using a hardcoded list to remove dependence on GPT
- Extend the grammar rules to support stacked auxiliaries (i.e. `공부하지 않으려고 했어요`)
- Extend the grammar rules to support more patterns (non-auxiliary)
    - conjunctions (`일하고 나서`)
    - conditionals (`좋으면`)
    - supposition (`갈 것 같아`)
    - reported speech / quotatives (`공부하자고 했다`)
    - noun-modifying clauses (`보던 영화`)
    - etc.