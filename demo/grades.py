GRADE_THRESHOLDS = {"A": 90, "B": 80, "C": 70, "D": 60}


def letter_grade(score):
    for grade, threshold in GRADE_THRESHOLDS.items():
        if score >= threshold:
            return grade
    return "F"


def class_average(scores):
    return sum(scores) / len(scores)


def passing_students(students):
    return [s for s in students if s["score"] >= 60]


def grade_distribution(scores):
    dist = {g: 0 for g in [*GRADE_THRESHOLDS, "F"]}
    for score in scores:
        dist[letter_grade(score)] += 1
    return dist


if __name__ == "__main__":
    scores = [95, 83, 72, 58, 91, 64, 77, 45, 88, 60]
    students = [{"name": f"Student {i+1}", "score": s} for i, s in enumerate(scores)]

    print(f"Class average: {class_average(scores):.1f}")
    print(f"Passing students: {len(passing_students(students))}/{len(students)}")
    print("\nGrade distribution:")
    for grade, count in grade_distribution(scores).items():
        print(f"  {grade}: {count}")
    print("\nIndividual grades:")
    for s in students:
        print(f"  {s['name']}: {s['score']} -> {letter_grade(s['score'])}")
