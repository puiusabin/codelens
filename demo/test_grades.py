import pytest
from your_module import letter_grade, class_average, passing_students, grade_distribution

# --- Happy Path Tests ---
def test_letter_grade_A():
    assert letter_grade(95) == "A"
def test_letter_grade_B():
    assert letter_grade(83) == "B"
def test_letter_grade_C():
    assert letter_grade(72) == "C"
def test_letter_grade_D():
    assert letter_grade(64) == "D"
def test_letter_grade_F():
    assert letter_grade(58) == "F"
def test_class_average_positive():
    assert class_average([95, 83, 72]) == 83.0
def test_passing_students_all_passing():
    assert len(passing_students([{"score": 95}, {"score": 83}, {"score": 72}])) == 3

# --- Edge Case Tests ---
def test_letter_grade_below_threshold():
    with pytest.raises(ValueError):
        letter_grade(-1)