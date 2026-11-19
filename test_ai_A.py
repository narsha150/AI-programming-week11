import pytest

from scores import load_scores


@pytest.fixture
def csv_path(tmp_path):
    def create(content, encoding="utf-8"):
        path = tmp_path / "scores.csv"
        path.write_bytes(content.encode(encoding))
        return path

    return create


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_load_valid_scores(csv_path, encoding):
    path = csv_path(
        "이름,점수\n임예슬,95\n김민수,80\n",
        encoding=encoding,
    )

    assert load_scores(path) == (
        [("임예슬", 95), ("김민수", 80)],
        [],
    )


def test_strip_whitespace(csv_path):
    path = csv_path("이름,점수\n  임예슬  ,  85  \n")

    assert load_scores(path) == ([("임예슬", 85)], [])


@pytest.mark.parametrize("score", [0, 1, 99, 100])
def test_valid_boundary_scores(csv_path, score):
    path = csv_path(f"이름,점수\n임예슬,{score}\n")

    assert load_scores(path) == ([("임예슬", score)], [])


@pytest.mark.parametrize("score", [-1, 101, -1000000, 1000000])
def test_out_of_range_scores(csv_path, score):
    path = csv_path(f"이름,점수\n임예슬,{score}\n")

    assert load_scores(path) == (
        [],
        [(2, f"임예슬,{score}", "점수가 0~100 밖")],
    )


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("임예슬", "열 개수가 2가 아님"),
        ("임예슬,90,추가", "열 개수가 2가 아님"),
        (",90", "이름이 비어 있음"),
        ("   ,90", "이름이 비어 있음"),
        ("임예슬,", "점수가 비어 있음"),
        ("임예슬,   ", "점수가 비어 있음"),
        ("임예슬,abc", "점수가 정수가 아님"),
        ("임예슬,85.5", "점수가 정수가 아님"),
        ("임예슬,90.0", "점수가 정수가 아님"),
        ("임예슬,1e2", "점수가 정수가 아님"),
        ("임예슬,NaN", "점수가 정수가 아님"),
        ("임예슬,1 0", "점수가 정수가 아님"),
    ],
)
def test_invalid_rows(csv_path, row, reason):
    path = csv_path(f"이름,점수\n{row}\n")

    assert load_scores(path) == ([], [(2, row, reason)])


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        (",,", "열 개수가 2가 아님"),
        (",", "이름이 비어 있음"),
        (",abc", "이름이 비어 있음"),
    ],
)
def test_validation_priority(csv_path, row, reason):
    path = csv_path(f"이름,점수\n{row}\n")

    assert load_scores(path) == ([], [(2, row, reason)])


@pytest.mark.parametrize(
    "content",
    [
        "",
        "이름,점수",
        "이름,점수\n",
        "이름,점수\n\n\n",
    ],
)
def test_empty_input_or_no_data(csv_path, content):
    assert load_scores(csv_path(content)) == ([], [])


def test_blank_lines_are_not_recorded_but_affect_line_numbers(csv_path):
    path = csv_path(
        "이름,점수\n"
        "\n"
        "임예슬,90\n"
        "\n"
        "김민수,abc\n"
        "\n"
    )

    assert load_scores(path) == (
        [("임예슬", 90)],
        [(5, "김민수,abc", "점수가 정수가 아님")],
    )


def test_whitespace_only_line_is_not_an_empty_row(csv_path):
    path = csv_path("이름,점수\n   \n")

    assert load_scores(path) == (
        [],
        [(2, "   ", "열 개수가 2가 아님")],
    )


def test_mixed_rows_preserve_order_and_original_values(csv_path):
    path = csv_path(
        "이름,점수\n"
        " 임예슬 , 90 \n"
        "김민수,abc\n"
        "\n"
        " ,50\n"
        "박지수,100\n"
        "최유진,101\n"
        "이서준,\n"
        "정하늘,70,추가\n"
        "한지민,0\n"
    )

    assert load_scores(path) == (
        [("임예슬", 90), ("박지수", 100), ("한지민", 0)],
        [
            (3, "김민수,abc", "점수가 정수가 아님"),
            (5, " ,50", "이름이 비어 있음"),
            (7, "최유진,101", "점수가 0~100 밖"),
            (8, "이서준,", "점수가 비어 있음"),
            (9, "정하늘,70,추가", "열 개수가 2가 아님"),
        ],
    )


def test_duplicate_names_are_preserved(csv_path):
    path = csv_path("이름,점수\n임예슬,90\n임예슬,80\n")

    assert load_scores(path) == ([("임예슬", 90), ("임예슬", 80)], [])


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("+90", 90), ("090", 90), ("-0", 0)],
)
def test_integer_formats_accepted_by_int(csv_path, raw, expected):
    path = csv_path(f"이름,점수\n임예슬,{raw}\n")

    assert load_scores(path) == ([("임예슬", expected)], [])


def test_quoted_csv_fields(csv_path):
    path = csv_path(
        '이름,점수\n'
        '"임,예슬","90"\n'
        '"김 ""민수""",80\n'
    )

    assert load_scores(path) == (
        [("임,예슬", 90), ('김 "민수"', 80)],
        [],
    )


def test_skipped_original_is_joined_fields_not_literal_csv(csv_path):
    path = csv_path('이름,점수\n"임,예슬",abc\n')

    assert load_scores(path) == (
        [],
        [(2, "임,예슬,abc", "점수가 정수가 아님")],
    )


def test_multiline_fields_use_record_numbers(csv_path):
    path = csv_path('이름,점수\n"임\n예슬",90\n김민수,abc\n')

    assert load_scores(path) == (
        [("임\n예슬", 90)],
        [(3, "김민수,abc", "점수가 정수가 아님")],
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_line_endings(csv_path, newline):
    path = csv_path(newline.join(["이름,점수", "임예슬,90", ""]))

    assert load_scores(path) == ([("임예슬", 90)], [])


def test_first_record_is_always_skipped(csv_path):
    path = csv_path("임예슬,90\n김민수,80\n")

    assert load_scores(path) == ([("김민수", 80)], [])


def test_string_path_is_supported(csv_path):
    path = csv_path("이름,점수\n임예슬,90\n")

    assert load_scores(str(path)) == ([("임예슬", 90)], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")


def test_permission_error_is_propagated(tmp_path, monkeypatch):
    def deny_open(*args, **kwargs):
        raise PermissionError("접근 권한 없음")

    monkeypatch.setattr("builtins.open", deny_open)

    with pytest.raises(PermissionError, match="접근 권한 없음"):
        load_scores(tmp_path / "scores.csv")


def test_invalid_utf8_raises_unicode_decode_error(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_bytes(b"name,score\n\xff,90\n")

    with pytest.raises(UnicodeDecodeError):
        load_scores(path)
