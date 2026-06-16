import pytest
from demo.grades import letter_grade, class_average, passing_students

# --- Happy Path Tests ---
# WHY: Verifies the `letter_grade` function returns the correct grade for a given score.
def test_letter_grade_A():
    assert letter_grade(95) == "A"
# WHY: Verifies the `letter_grade` function returns the correct grade for a given score.
def test_letter_grade_B():
    assert letter_grade(83) == "B"
# WHY: Verifies the `letter_grade` function returns the correct grade for a given score.
def test_letter_grade_C():
    assert letter_grade(72) == "C"
# WHY: Verifies the `letter_grade` function returns the correct grade for a given score.
def test_letter_grade_D():
    assert letter_grade(64) == "D"
# WHY: Verifies the `letter_grade` function returns 'F' for scores below 60.
def test_letter_grade_F():
    assert letter_grade(58) == "F"
# WHY: Verifies the `class_average` function calculates the average correctly.
def test_class_average():
    assert class_average([95, 83, 72, 58, 91, 64, 77, 45, 88, 60]) == 73.5
# WHY: Verifies the `passing_students` function correctly identifies passing students.
def test_passing_students():
    assert len(passing_students([{"name": "Student 1", "score": 95}, {"name": "Student 2", "score": 83}, {"name": "Student 3", "score": 72}, {"name": "Student 4", "score": 58}, {"name": "Student 5", "score": 91}, {"name": "Student 6", "score": 64}, {"name": "Student 7", "score": 77}, {"name": "Student 8", "score": 45}, {"name": "Student 9", "score": 88}, {"name": "Student 10", "score": 60}])) == 7



# --- Edge Case Tests ---
# WHY: Verifies the `letter_grade` function handles scores below 0 correctly.
def test_letter_grade_below_zero():
    with pytest.raises(ValueError):
        letter_grade(-5)