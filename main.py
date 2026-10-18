from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Student Marks API", version="1.0.0")

# ---------- Pydantic Schemas ----------

class Subject(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)

class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    class_name: str = Field(..., alias="class")

    class Config:
        populate_by_name = True

class MarksCreate(BaseModel):
    student_id: int
    subject_id: int
    marks: float = Field(..., ge=0, le=100)

class Marks(BaseModel):
    id: int
    student_id: int
    subject_id: int
    marks: float = Field(..., ge=0, le=100)

class StudentReport(BaseModel):
    student: Student
    marks: List[dict]
    total: float
    average: float


# ---------- In-memory Data ----------

subjects_db: List[Subject] = [
    Subject(id=1, name="Mathematics"),
    Subject(id=2, name="Science"),
    Subject(id=3, name="English"),
]

students_db: List[Student] = [
    Student(id=1, name="Alice", **{"class": "10A"}),
    Student(id=2, name="Bob", **{"class": "10B"}),
    Student(id=3, name="Charlie", **{"class": "10A"}),
]

marks_db: List[Marks] = [
    Marks(id=1, student_id=1, subject_id=1, marks=92),
    Marks(id=2, student_id=1, subject_id=2, marks=85),
    Marks(id=3, student_id=1, subject_id=3, marks=88),
    Marks(id=4, student_id=2, subject_id=1, marks=74),
    Marks(id=5, student_id=2, subject_id=2, marks=69),
    Marks(id=6, student_id=3, subject_id=1, marks=95),
    Marks(id=7, student_id=3, subject_id=2, marks=91),
    Marks(id=8, student_id=3, subject_id=3, marks=79),
]


# ---------- APIs ----------

@app.get("/")
def root():
    return {"message": "Welcome to Student Marks API"}


# ---- Subjects ----
@app.get("/subjects", response_model=List[Subject])
def get_subjects():
    return subjects_db


@app.post("/subjects", response_model=Subject, status_code=201)
def create_subject(subject: Subject):
    if any(s.id == subject.id for s in subjects_db):
        raise HTTPException(status_code=400, detail="Subject ID already exists")
    subjects_db.append(subject)
    return subject


# ---- Students ----
@app.get("/students", response_model=List[Student])
def get_students():
    return students_db


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    for s in students_db:
        if s.id == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")


@app.post("/students", response_model=Student, status_code=201)
def create_student(student: Student):
    if any(s.id == student.id for s in students_db):
        raise HTTPException(status_code=400, detail="Student ID already exists")
    students_db.append(student)
    return student


# ---- Marks ----
@app.get("/marks", response_model=List[Marks])
def get_marks():
    return marks_db


@app.post("/marks", response_model=Marks, status_code=201)
def add_marks(payload: MarksCreate):
    # validate student & subject
    if not any(s.id == payload.student_id for s in students_db):
        raise HTTPException(status_code=404, detail="Student not found")
    if not any(s.id == payload.subject_id for s in subjects_db):
        raise HTTPException(status_code=404, detail="Subject not found")

    new_id = max((m.id for m in marks_db), default=0) + 1
    new_mark = Marks(id=new_id, **payload.model_dump())
    marks_db.append(new_mark)
    return new_mark


# ---- Report ----
@app.get("/students/{student_id}/report", response_model=StudentReport)
def get_student_report(student_id: int):
    student = next((s for s in students_db if s.id == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student_marks = [m for m in marks_db if m.student_id == student_id]
    if not student_marks:
        return StudentReport(student=student, marks=[], total=0, average=0)

    subject_map = {s.id: s.name for s in subjects_db}
    detailed = [
        {
            "subject": subject_map.get(m.subject_id, "Unknown"),
            "marks": m.marks,
        }
        for m in student_marks
    ]
    total = sum(m.marks for m in student_marks)
    average = round(total / len(student_marks), 2)

    return StudentReport(
        student=student,
        marks=detailed,
        total=total,
        average=average,
    )