from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import CourseTable
from app.dependencies import get_db, get_current_user, require_admin
from app.schemas.course import CreateCourseRequest, UpdateCourseRequest

router = APIRouter(prefix="/courses", tags=["Courses"])


# ==============================
# CREATE COURSE (Admin Only)
# ==============================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_course(
    input: CreateCourseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    course = CourseTable(
        title=input.title,
        description=input.description,
        credit_hours=input.credit_hours,
        max_students=input.max_students
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "message": "Course added successfully",
        "course_id": course.id
    }


# ==============================
# VIEW ALL COURSES (Logged-in Users)
# ==============================
@router.get("/")
def get_all_courses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(CourseTable).all()


# ==============================
# VIEW SINGLE COURSE (Logged-in Users)
# ==============================
@router.get("/{id}")
def get_course_by_id(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    course = db.query(CourseTable).filter(
        CourseTable.id == id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


# ==============================
# UPDATE COURSE (Admin Only)
# ==============================
@router.put("/{id}")
def update_course(
    id: UUID,
    data: UpdateCourseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    course = db.query(CourseTable).filter(
        CourseTable.id == id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.title = data.title
    course.description = data.description
    course.credit_hours = data.credit_hours
    course.max_students = data.max_students

    db.commit()
    db.refresh(course)

    return {"message": "Course updated successfully"}


# ==============================
# DELETE COURSE (Admin Only)
# ==============================
@router.delete("/{id}")
def delete_course(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):

    course = db.query(CourseTable).filter(
        CourseTable.id == id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}
