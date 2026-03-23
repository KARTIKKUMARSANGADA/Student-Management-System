from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import CourseTable
from app.models.enrollment import EnrollmentTable
from app.models.student_profile import StudentProfileTable
from app.dependencies import get_current_user, get_db, require_admin
from app.schemas.enrollments import CreateEnrollmentRequest

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# ==============================
# ENROLL STUDENT
# Admin → enroll anyone
# Student → enroll only self
# ==============================
@router.post("/", status_code=201)
def enroll_student(
    payload: CreateEnrollmentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # If student → allow only self enrollment
    if current_user.role == "student":
        if current_user.id != payload.student_id:
            raise HTTPException(
                status_code=403,
                detail="Students can enroll only themselves"
            )

    # Check student exists
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == payload.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check course exists
    course = db.query(CourseTable).filter(
        CourseTable.id == payload.course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Prevent duplicate enrollment
    existing = db.query(EnrollmentTable).filter(
        EnrollmentTable.student_id == payload.student_id,
        EnrollmentTable.course_id == payload.course_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    # Check course capacity
    enrolled_count = db.query(EnrollmentTable).filter(
        EnrollmentTable.course_id == payload.course_id
    ).count()

    if enrolled_count >= course.max_students:
        raise HTTPException(status_code=400, detail="Course is full")

    enrollment = EnrollmentTable(
        student_id=payload.student_id,
        course_id=payload.course_id
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Enrollment successful",
        "enrollment_id": enrollment.id
    }


# ==============================
# ADMIN → View All Enrollments
# ==============================
@router.get("/")
def get_all_enrollments(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return db.query(EnrollmentTable).all()


# ==============================
# STUDENT → View Own Enrollments
# ==============================
@router.get("/me")
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Students only")

    enrollments = db.query(EnrollmentTable).filter(
        EnrollmentTable.student_id == current_user.id
    ).all()

    return enrollments


# ==============================
# ADMIN → Delete Enrollment
# ==============================
@router.delete("/{id}")
def delete_enrollment(
    id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):

    enrollment = db.query(EnrollmentTable).filter(
        EnrollmentTable.id == id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()

    return {"message": "Enrollment deleted successfully"}
