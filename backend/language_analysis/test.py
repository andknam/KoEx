from backend.language_analysis.linguistic_processing.grouping import group_komoran_tokens
from backend.language_analysis.linguistic_processing.rule_matcher import merge_aux_grammar_chunks


def test_merge(input_tokens: list[tuple[str, str]], expected: list[str]):
    merged = merge_aux_grammar_chunks(input_tokens)
    grouped = group_komoran_tokens(merged)
    result_tokens = [token for token, _ in grouped]

    assert (
        result_tokens == expected
    ), f"\nExpected: {expected}\nGot:      {result_tokens}\nGrouped: {grouped}"

    print(
        f"✅ Passed: {' + '.join([t[0] for t in input_tokens])} → {' + '.join(expected)}"
    )


if __name__ == "__main__":
    print("\n=== Running grammar chunking tests ===\n")

    # Simple aux tests
    test_merge([("하", "VV"), ("고", "EC"), ("싶", "VA"), ("다", "EF")], ["하고싶다"])
    test_merge([("하", "VV"), ("고", "EC"), ("있", "VX"), ("다", "EF")], ["하고있다"])
    test_merge([("하", "VV"), ("지", "EC"), ("않", "VX"), ("다", "EF")], ["하지않다"])
    test_merge([("하", "VV"), ("ㄹ", "ETM"), ("수", "NNG"), ("있", "VV"), ("다", "EF")], ["할수있다"])

    # Compound derivation + aux
    test_merge(
        [("실천", "NNG"), ("하", "XSV"), ("고", "EC"), ("싶", "VA"), ("다", "EF")],
        ["실천", "실천하고싶다"],
    )
    test_merge(
        [("실천", "NNG"), ("하", "XSV"), ("지", "EC"), ("않", "VX"), ("다", "EF")],
        ['실천', '실천하지', '않다'],
    )

    # Try-to-do (noun stem)
    test_merge(
        [("공부", "NNG"), ("하", "XSV"), ("려고", "EC"), ("하", "VV"), ("다", "EF")],
        ['공부', '공부하려고', '하다'],
    )

    # Negation obligation (가지 말았어야 했어요)
    test_merge(
        [("가지", "NNB"), ("말", "VX"), ("았", "EP"), ("어야", "EC"), ("했어요", "VV")],
        ['가지', '말았어야', '했어요'],
    )

    # Potential negation (않을수도있어요)
    test_merge(
        [("가지", "NNB"), ("않", "VX"), ("을", "ETM"), ("수", "NNB"), ("도", "JX"), ("있", "VV"), ("어요", "EC")],
        ["가지", "않을수도있어요"],
    )

    # Progressive + want past (하고 싶어했어요)
    test_merge(
        [("하", "VV"), ("고", "EC"), ("싶", "VA"), ("어", "EC"), ("했어요", "VV")],
        ['하고싶어', '했어요'],
    )

    # Future intent negation (하지 않겠어요)
    test_merge(
        [("하", "VV"), ("지", "EC"), ("않", "VX"), ("겠", "EP"), ("어요", "EF")],
        ["하지않겠어요"],
    )

    # Try-to-do (no noun base) 하려고 했어요
    test_merge(
        [("하", "VV"), ("려고", "EC"), ("했어요", "VV")],
        ['하려고했어요'],
    )

    # Fully nested: 공부하지 않으려고 했어요
    test_merge(
        [
            ("공부", "NNG"),
            ("하", "XSV"),
            ("지", "EC"),
            ("않", "VX"),
            ("으려고", "EC"),
            ("했어요", "VV"),
        ],
        ['공부', '공부하지', '않으려고했어요'],
    )

    print("\n✅ All tests passed.\n")