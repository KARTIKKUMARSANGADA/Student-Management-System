from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies import get_current_user, get_db, require_admin
from app.models.grade import GradeTable
from app.models.enrollment import EnrollmentTable
from app.models.course import CourseTable
from app.schemas.grade import GradeCreate
from app.utils.grade_calculator import calculate_grade

router = APIRouter(prefix="/grades", tags=["Grades"])


# ==============================
# ASSIGN GRADE (Admin Only)
# ==============================
@router.post("/", status_code=status.HTTP_201_CREATED)
def assign_grade(data: GradeCreate,db: Session = Depends(get_db),current_user=Depends(require_admin)):

    enrollment = db.query(EnrollmentTable).filter(
        EnrollmentTable.id == data.enrollment_id
    ).first()

    if not enrollment:
        raise HTTPException(404, "Enrollment not found")

    existing = db.query(GradeTable).filter(
        GradeTable.enrollment_id == data.enrollment_id
    ).first()

    if existing:
        raise HTTPException(400, "Grade already assigned")

    if data.marks_obtained > data.total_marks:
        raise HTTPException(400, "Marks cannot exceed total")

    grade_letter = calculate_grade(
        data.marks_obtained,
        data.total_marks
    )

    new_grade = GradeTable(
        enrollment_id=data.enrollment_id,
        marks_obtained=data.marks_obtained,
        total_marks=data.total_marks,
        grade_letter=grade_letter,
        remarks=data.remarks
    )

    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)

    return {
        "message": "Grade assigned successfully",
        "grade_letter": grade_letter
    }


# ==============================
# VIEW ALL GRADES (Admin Only)
# ==============================
@router.get("/")
def get_all_grades(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    return db.query(GradeTable).all()


# ==============================
# VIEW SINGLE GRADE (Admin Only)
# ==============================
@router.get("/{id}")
def get_grade(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    grade = db.query(GradeTable).filter(GradeTable.id == id).first()

    if not grade:
        raise HTTPException(404, "Grade not found")

    return grade


# ==============================
# UPDATE GRADE (Admin Only)
# ==============================
@router.put("/{id}")
def update_grade(
    id: UUID,
    grade_update: GradeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    grade = db.query(GradeTable).filter(GradeTable.id == id).first()

    if not grade:
        raise HTTPException(404, "Grade not found")

    grade.marks_obtained = grade_update.marks_obtained
    grade.total_marks = grade_update.total_marks
    grade.remarks = grade_update.remarks
    grade.grade_letter = calculate_grade(
        grade_update.marks_obtained,
        grade_update.total_marks
    )

    db.commit()
    db.refresh(grade)

    return {"message": "Grade updated successfully"}


# ==============================
# DELETE GRADE (Admin Only)
# ==============================
@router.delete("/{id}")
def delete_grade(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    grade = db.query(GradeTable).filter(GradeTable.id == id).first()

    if not grade:
        raise HTTPException(404, "Grade not found")

    db.delete(grade)
    db.commit()

    return {"message": "Grade deleted successfully"}


# ==============================
# VIEW STUDENT GRADES
# Admin → Any student
# Student → Only own
# ==============================
@router.get("/student/{student_id}")
def get_student_grades(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(403, "You can view only your grades")

    grades = db.query(GradeTable).join(EnrollmentTable).filter(
        EnrollmentTable.student_id == student_id
    ).all()

    if not grades:
        raise HTTPException(404, "No grades found")

    return grades


# ==============================
# GPA SUMMARY
# Admin → Any student
# Student → Only own
# ==============================
@router.get("/student/{student_id}/summary")
def get_student_gpa_summary(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):

    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(403, "You can view only your GPA")

    results = (
        db.query(GradeTable, CourseTable)
        .join(EnrollmentTable, GradeTable.enrollment_id == EnrollmentTable.id)
        .join(CourseTable, EnrollmentTable.course_id == CourseTable.id)
        .filter(EnrollmentTable.student_id == student_id)
        .all()
    )

    if not results:
        raise HTTPException(404, "No grades found")

    grade_points_map = {
        "A": 4.0,
        "B": 3.0,
        "C": 2.0,
        "D": 1.0,
        "F": 0.0,
    }

    total_points = 0
    total_credits = 0
    credits_earned = 0

    for grade, course in results:
        credit = course.credit_hours
        points = grade_points_map.get(grade.grade_letter, 0)

        total_points += points * credit
        total_credits += credit

        if grade.grade_letter != "F":
            credits_earned += credit

    gpa = round(total_points / total_credits, 2) if total_credits else 0

    return {
        "student_id": student_id,
        "total_courses": len(results),
        "credits_attempted": total_credits,
        "credits_earned": credits_earned,
        "gpa": gpa
    }
