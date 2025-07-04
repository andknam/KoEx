from backend.hanja_utils.tokenizer import group_komoran_tokens
from backend.hanja_utils.rule_matcher import merge_aux_grammar_chunks


def test_merge(input_tokens: list[tuple[str, str]], expected: list[str]):
    grouped = group_komoran_tokens(input_tokens)
    result = merge_aux_grammar_chunks(grouped)
    result_tokens = [token for token, _ in result]

    assert (
        result_tokens == expected
    ), f"\nExpected: {expected}\nGot:      {result_tokens}\nGrouped: {grouped}"

    print(
        f"✅ Passed: {' + '.join([t[0] for t in input_tokens])} → {' + '.join(expected)}"
    )


if __name__ == "__main__":
    print("\n=== Running grammar chunking tests ===\n")

    # 하 + 고 + 싶 + 다 → 하고싶다
    test_merge([("하", "VV"), ("고", "EC"), ("싶", "VA"), ("다", "EF")], ["하고싶다"])

    # 실천 + 하 + 고 + 싶 + 다 → 실천 + 실천하고싶다
    test_merge(
        [("실천", "NNG"), ("하", "XSV"), ("고", "EC"), ("싶", "VA"), ("다", "EF")],
        ["실천", "실천하고싶다"],
    )

    # 공부 + 하 + 려고 + 하 + 다 → 공부 + 공부하려고하다
    test_merge(
        [("공부", "NNG"), ("하", "XSV"), ("려고", "EC"), ("하", "VV"), ("다", "EF")],
        ["공부", "공부하려고하다"],
    )

    # 하 + 고 + 있 + 다 → 하고있다
    test_merge([("하", "VV"), ("고", "EC"), ("있", "VX"), ("다", "EF")], ["하고있다"])

    # 하 + 지 + 않 + 다 → 하지않다
    test_merge([("하", "VV"), ("지", "EC"), ("않", "VX"), ("다", "EF")], ["하지않다"])

    # 실천 + 하 + 지 + 않 + 다 → 실천 + 실천하지않다
    test_merge(
        [("실천", "NNG"), ("하", "XSV"), ("지", "EC"), ("않", "VX"), ("다", "EF")],
        ["실천", "실천하지않다"],
    )

    # 하 + ㄹ + 수 + 있 + 다 → 할수있다
    test_merge(
        [("하", "VV"), ("ㄹ", "ETM"), ("수", "NNG"), ("있", "VV"), ("다", "EF")],
        ["할수있다"],
    )

    print("\n✅ All tests passed.\n")
