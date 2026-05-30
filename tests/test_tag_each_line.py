"""Unit tests for `_tag_each_line` rendering of multi-line tool_result
content. The helper governs how `tool-fail` / `tool-ok` blocks surface
in the orchestrator's stream verbosity — line 1 carries the full
prefix, lines 2+ carry a width-matched continuation that preserves
worker attribution but drops the event-kind token."""


def test_empty_content_returns_empty_string(pila):
    assert pila._tag_each_line("  [sid tool-fail]", "") == ""


def test_only_blank_lines_returns_empty_string(pila):
    assert pila._tag_each_line("  [sid tool-fail]", "\n\n\n") == ""


def test_single_line_renders_as_prefix_space_content(pila):
    assert pila._tag_each_line("  [sid tool-fail]", "boom") == "  [sid tool-fail] boom"


def test_multi_line_first_line_keeps_full_prefix(pila):
    out = pila._tag_each_line("  [sid tool-fail]", "line one\nline two\nline three")
    first = out.splitlines()[0]
    assert first == "  [sid tool-fail] line one"


def test_multi_line_continuation_drops_kind_and_pads_to_width(pila):
    prefix = "  [sid tool-fail]"
    out = pila._tag_each_line(prefix, "line one\nline two")
    cont_line = out.splitlines()[1]
    cont_prefix = cont_line[: len(prefix)]
    # Continuation must:
    #   1. be the same width as the original prefix (column alignment)
    #   2. retain the sid (parallel-worker attribution)
    #   3. NOT contain the kind token ("tool-fail")
    assert len(cont_prefix) == len(prefix)
    assert "sid" in cont_prefix
    assert "tool-fail" not in cont_prefix
    assert cont_prefix.startswith("  [sid")
    assert cont_prefix.endswith("]")
    assert cont_line == cont_prefix + " line two"


def test_multi_line_continuation_consistent_across_all_tail_lines(pila):
    out = pila._tag_each_line("  [sid tool-fail]", "a\nb\nc\nd")
    lines = out.splitlines()
    assert len(lines) == 4
    # Lines 2-4 must share the same continuation prefix.
    cont = lines[1][: len("  [sid tool-fail]")]
    for ln in lines[2:]:
        assert ln.startswith(cont)


def test_blank_interior_lines_are_filtered(pila):
    out = pila._tag_each_line("  [sid tool-fail]", "one\n\ntwo\n\n\nthree")
    lines = out.splitlines()
    assert lines == [
        "  [sid tool-fail] one",
        lines[1],
        lines[2],
    ]
    assert lines[1].endswith(" two")
    assert lines[2].endswith(" three")


def test_works_with_tool_ok_kind(pila):
    out = pila._tag_each_line("  [sid tool-ok]", "x\ny")
    lines = out.splitlines()
    assert lines[0] == "  [sid tool-ok] x"
    assert "tool-ok" not in lines[1][: len("  [sid tool-ok]")]
    assert "sid" in lines[1]
    assert len(lines[1][: len("  [sid tool-ok]")]) == len("  [sid tool-ok]")


def test_works_with_long_sid(pila):
    prefix = "  [feat-002-conformer tool-fail]"
    out = pila._tag_each_line(prefix, "row one\nrow two")
    lines = out.splitlines()
    assert lines[0] == prefix + " row one"
    cont = lines[1][: len(prefix)]
    assert len(cont) == len(prefix)
    assert "feat-002-conformer" in cont
    assert "tool-fail" not in cont


def test_defensive_fallback_on_unexpected_prefix_shape(pila):
    # Prefix with no brackets falls back to repeating the prefix.
    out = pila._tag_each_line("xx", "a\nb")
    assert out == "xx a\nxx b"


def test_defensive_fallback_on_prefix_without_kind_token(pila):
    # Bracketed prefix but no space inside brackets → no kind to drop;
    # falls back to repeating the prefix verbatim on every line.
    out = pila._tag_each_line("[sidonly]", "a\nb")
    assert out == "[sidonly] a\n[sidonly] b"
