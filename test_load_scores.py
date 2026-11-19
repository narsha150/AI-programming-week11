
from pathlib import Path
import pytest
from load_scores import load_scores

BASE_DIR = Path(__file__).resolve().parent


# 정상 ①
def test_정상_파일을_읽는다():
    kept, skipped = load_scores(BASE_DIR / "scores.csv")
    assert len(kept) == 5


# 정상 ②
def test_빈_줄은_건너뛴다(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("name,score\n김하나,80\n\n김둘,90\n", encoding="utf-8")
    kept, skipped = load_scores(path)
    assert kept == [("김하나", 80), ("김둘", 90)]
    assert skipped == []


# 정상 ③
def test_이름에_쉼표가_있어도_읽는다(tmp_path):
    path = tmp_path / "comma.csv"
    path.write_text('name,score\n"김,하나",90\n', encoding="utf-8")
    kept, skipped = load_scores(path)
    assert kept == [("김,하나", 90)]
    assert skipped == []


# 예외 ①
def test_없는_파일이면_오류가_난다(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "missing.csv")


# 예외 ②
def test_헤더만_있으면_빈_결과():
    kept, skipped = load_scores(BASE_DIR / "empty.csv")
    assert kept == []
    assert skipped == []


# 경계값
@pytest.mark.parametrize("점수, 유효한가", [
    (-1, False),
    (0, True),
    (1, True),
    (99, True),
    (100, True),
    (101, False),
])
def test_점수_경계값(tmp_path, 점수, 유효한가):
    path = tmp_path / "boundary.csv"
    path.write_text(f"name,score\n학생,{점수}\n", encoding="utf-8")
    kept, skipped = load_scores(path)
    assert (len(kept) == 1) == 유효한가
    assert len(skipped) == (0 if 유효한가 else 1)

def test_이름이_비어_있는_경우(tmp_path):
    path = tmp_path / "no_name.csv"
    path.write_text("name,score\n,90\n", encoding="utf-8")
    kept, skipped = load_scores(path)
    assert kept == []
    assert len(skipped) == 1
    assert skipped[0][2] == "이름이 비어 있음"


def test_프로그램_직접_실행(capsys, monkeypatch):
    import runpy
    import sys

    monkeypatch.setattr(sys, "argv", [
        "load_scores.py", str(BASE_DIR / "scores.csv")
    ])
    runpy.run_path(str(BASE_DIR / "load_scores.py"),
                   run_name="__main__")
    captured = capsys.readouterr()
    assert "읽은 줄 : 5개" in captured.out
    assert "건너뛴 줄" in captured.out