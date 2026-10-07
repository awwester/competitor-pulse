from app.services.diffing import diff_text, normalize_text, truncate


def test_normalize_text_collapses_whitespace_and_blank_lines():
    assert normalize_text("  Pro   plan \n\n\n\t$29 / mo  ") == "Pro plan\n$29 / mo"


def test_diff_text_counts_added_and_removed_lines():
    result = diff_text("Starter\n$15\nPro", "Free\n$0\nPro")
    assert (result.lines_added, result.lines_removed) == (2, 2)


def test_diff_text_of_identical_text_is_empty():
    assert diff_text("same", "same").text == ""


def test_truncate_leaves_short_text_untouched():
    assert truncate("short", 10) == "short"


def test_truncate_marks_removed_characters():
    assert truncate("a" * 15, 10).endswith("[truncated 5 chars]")
