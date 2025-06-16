from typing import List

def contract_korean(tokens: List[str]) -> str:
    """
    Applies basic Korean morphophonological contractions.
    For example:
    - 하 + 였 → 했
    - 하 + 았 → 했
    - 끝나 + 았 → 끝났
    - 하 + ㄹ → 할
    - 아야하겠다 / 어야하겠다 → 야겠다
    """

    if len(tokens) < 2:
        return ''.join(tokens)

    # 하 + ㄹ → 할 (e.g., 하ㄹ 수 있다)
    if tokens[0] == '하' and tokens[1] == 'ㄹ':
        tokens[0] = '할'
        del tokens[1]

    # special endings like 아야하겠다 / 어야하겠다 → 야겠다
    joined = ''.join(tokens)
    if joined.endswith("아야하겠다") or joined.endswith("어야하겠다"):
        joined = joined.replace("아야하겠다", "야겠다").replace("어야하겠다", "야겠다")
        return joined

    # Iterate through pairs to contract verb stems
    i = 0
    while i < len(tokens) - 1:
        prev, curr = tokens[i], tokens[i + 1]

        # 하 + 았/었/였 → 했
        if prev == '하' and curr in {'았', '었', '였'}:
            tokens[i] = '했'
            del tokens[i + 1]
            continue

        # 가 + 았 → 갔
        if prev.endswith('가') and curr == '았':
            tokens[i] = prev[:-1] + '갔'
            del tokens[i + 1]
            continue

        # 끝나 + 았 → 끝났
        if prev.endswith('나') and curr == '았':
            tokens[i] = prev[:-1] + '났'
            del tokens[i + 1]
            continue

        # 자 + 았 → 잤
        if prev.endswith('자') and curr == '았':
            tokens[i] = prev[:-1] + '잤'
            del tokens[i + 1]
            continue

        # 주 + 었 → 줬
        if prev.endswith('주') and curr == '었':
            tokens[i] = prev[:-1] + '줬'
            del tokens[i + 1]
            continue

        i += 1

    return ''.join(tokens)
