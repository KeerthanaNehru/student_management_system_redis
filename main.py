from fastapi import FastAPI, HTTPException
import redis
from pydantic import BaseModel

# Connect to Redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)

app = FastAPI(title="Student Management API")

# Pydantic model for Student
class Student(BaseModel):
    name: str
    age: int
    skills: list[str]

# ---------------- CREATE ----------------
@app.post("/students/{student_id}")
def create_student(student_id: str, student: Student):
    key = f"student:{student_id}"
    if r.exists(key):
        raise HTTPException(status_code=400, detail="Student already exists")

    # Store as a hash in Redis
    r.hset(key, mapping={
        "name": student.name,
        "age": str(student.age),
        "skills": ",".join(student.skills)
    })
    return {"message": f"Student {student_id} created successfully"}

# ---------------- READ ----------------
@app.get("/students/{student_id}")
def read_student(student_id: str):
    key = f"student:{student_id}"
    if not r.exists(key):
        raise HTTPException(status_code=404, detail="Student not found")

    data = r.hgetall(key)
    # Convert skills string back to list
    data["skills"] = data["skills"].split(",") if data.get("skills") else []
    return data

'''
# ---------------- READ ALL DATA ----------------
@app.get("/students")
def read_all_students():
    keys = r.keys("student:*")
    students = []

    for key in keys:
        student_data = r.hgetall(key)
        student_data["skills"] = student_data["skills"].split(",") if student_data.get("skills") else []
        student_id = key.split(":")[1]  # Extract the ID from key
        students.append({"id": student_id, **student_data})

    return students
'''

# ---------------- UPDATE ----------------
@app.put("/students/{student_id}")
def update_student(student_id: str, student: Student):
    key = f"student:{student_id}"
    if not r.exists(key):
        raise HTTPException(status_code=404, detail="Student not found")

    r.hset(key, mapping={
        "name": student.name,
        "age": str(student.age),
        "skills": ",".join(student.skills)
    })
    return {"message": f"Student {student_id} updated successfully"}

# ---------------- DELETE ----------------
@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    key = f"student:{student_id}"
    if not r.exists(key):
        raise HTTPException(status_code=404, detail="Student not found")

    r.delete(key)
    return {"message": f"Student {student_id} deleted successfully"}


