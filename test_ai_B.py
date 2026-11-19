import pytest

from scores import load_scores


@pytest.fixture
def csv_path(tmp_path):
    def create(content):
        path = tmp_path / "scores.csv"
        path.write_bytes(content.encode("utf-8"))
        return path

    return create


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (
            "name,score\n민수,85\n",
            [("민수", 85)],
        ),
        (
            "name,score\n민수,85\n예슬,92\n지우,70\n",
            [("민수", 85), ("예슬", 92), ("지우", 70)],
        ),
        (
            'name,score\n"김,민수",85\n',
            [("김,민수", 85)],
        ),
        (
            'name,score\n"김""민수",85\n',
            [('김"민수', 85)],
        ),
        (
            "name,score\r\n민수,85\r\n예슬,92\r\n",
            [("민수", 85), ("예슬", 92)],
        ),
        (
            "name,score\n민수,85",
            [("민수", 85)],
        ),
        (
            "name,score\n",
            [],
        ),
    ],
    ids=[
        "single-record",
        "multiple-records-preserve-order",
        "quoted-comma",
        "escaped-quote",
        "windows-line-endings",
        "no-final-newline",
        "header-only",
    ],
)
def test_load_scores_valid_csv(csv_path, content, expected):
    result = load_scores(csv_path(content))

    assert isinstance(result, list)
    assert result == expected
    assert all(isinstance(record, tuple) for record in result)
    assert all(isinstance(name, str) for name, _ in result)
    assert all(type(score) is int for _, score in result)


@pytest.mark.parametrize(
    "score",
    [0, 1, 99, 100],
    ids=["minimum", "above-minimum", "below-maximum", "maximum"],
)
def test_load_scores_valid_score_boundaries(csv_path, score):
    path = csv_path(f"name,score\n예슬,{score}\n")

    assert load_scores(path) == [("예슬", score)]


@pytest.mark.parametrize(
    "score",
    [-1, 101],
    ids=["below-minimum", "above-maximum"],
)
def test_load_scores_out_of_range_score(csv_path, score):
    path = csv_path(f"name,score\n예슬,{score}\n")

    with pytest.raises(ValueError):
        load_scores(path)


@pytest.mark.parametrize(
    "score",
    ["abc", "85.5", "NaN", "inf"],
    ids=["text", "decimal", "nan", "infinity"],
)
def test_load_scores_non_integer_score(csv_path, score):
    path = csv_path(f"name,score\n예슬,{score}\n")

    with pytest.raises(ValueError):
        load_scores(path)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "예슬,90\n",
        "student,score\n예슬,90\n",
        "name,grade\n예슬,90\n",
        "score,name\n90,예슬\n",
        "name,score,extra\n예슬,90,x\n",
    ],
    ids=[
        "empty-file",
        "missing-header",
        "wrong-name-column",
        "wrong-score-column",
        "reversed-columns",
        "extra-header-column",
    ],
)
def test_load_scores_invalid_header(csv_path, content):
    with pytest.raises(ValueError):
        load_scores(csv_path(content))


@pytest.mark.parametrize(
    "row",
    [
        ",90",
        "   ,90",
        "예슬,",
        "예슬,   ",
        ",",
        "예슬",
        "예슬,90,extra",
    ],
    ids=[
        "missing-name",
        "whitespace-name",
        "missing-score",
        "whitespace-score",
        "both-values-missing",
        "too-few-columns",
        "too-many-columns",
    ],
)
def test_load_scores_invalid_record(csv_path, row):
    path = csv_path(f"name,score\n{row}\n")

    with pytest.raises(ValueError):
        load_scores(path)


@pytest.mark.parametrize(
    "content",
    [
        "name,score\n예슬,90\n예슬,90\n",
        "name,score\n예슬,90\n예슬,80\n",
    ],
    ids=["duplicate-name-same-score", "duplicate-name-different-score"],
)
def test_load_scores_duplicate_name(csv_path, content):
    with pytest.raises(ValueError):
        load_scores(csv_path(content))


def test_load_scores_unclosed_quoted_field(csv_path):
    path = csv_path('name,score\n"예슬,90\n')

    with pytest.raises(ValueError):
        load_scores(path)


@pytest.mark.parametrize("invalid_index", [0, 1, 2])
def test_load_scores_invalid_row_is_not_silently_skipped(
    csv_path, invalid_index
):
    rows = ["민수,85", "예슬,92"]
    rows.insert(invalid_index, "지우,invalid")
    path = csv_path("name,score\n" + "\n".join(rows) + "\n")

    with pytest.raises(ValueError):
        load_scores(path)


def test_load_scores_missing_file(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(path)


def test_load_scores_does_not_modify_source_file(csv_path):
    path = csv_path("name,score\n예슬,90\n")
    original = path.read_bytes()

    load_scores(path)

    assert path.read_bytes() == original