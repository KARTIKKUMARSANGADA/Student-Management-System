from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.models import StudentProfileTable
from app.schemas.student import UpdatePhoneRequest, UpdateStudent, GetStudent

router = APIRouter(prefix="/students", tags=["Student"])


# ✅ Get All Students (Admin Only)
@router.get("/", response_model=list[GetStudent])
def get_all_students(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    students = db.query(StudentProfileTable).all()
    return students


# ✅ Update Own Phone Number (Student)
@router.put("/me")
def update_my_profile(
    payload: UpdatePhoneRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    student.phone = payload.phone
    db.commit()
    db.refresh(student)

    return {"message": "Your phone updated successfully"}


# ✅ Get My Profile
@router.get("/me/profile")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return student


# ✅ Get Student By ID (Admin Only)
@router.get("/{id}", response_model=GetStudent)
def get_student_by_id(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


# ✅ Update Student (Admin Only)
@router.put("/{id}")
def update_student_admin(
    id: UUID,
    payload: UpdateStudent,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    student.first_name = payload.first_name
    student.last_name = payload.last_name
    student.phone = payload.phone
    student.date_of_birth = payload.date_of_birth

    db.commit()
    db.refresh(student)

    return {"message": f"Student {payload.first_name} updated successfully"}


# ✅ Delete Student (Admin Only)
@router.delete("/{id}")
def delete_student(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    student = db.query(StudentProfileTable).filter(
        StudentProfileTable.user_id == id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}