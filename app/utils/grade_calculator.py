

def calculate_grade(marks_obtained: int, total_marks: int) -> str:
    if total_marks <= 0:
        raise ValueError("Total marks must be greater than 0")

    percentage = (marks_obtained / total_marks) * 100

    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"