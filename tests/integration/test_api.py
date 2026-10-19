from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_marks_list_matches_schema():
    response = client.get("/marks")

    assert response.status_code == 200
    body = response.json()
    assert body
    assert set(body[0]) == {"id", "student_id", "subject_id", "marks"}


def test_student_serializes_class_alias():
    response = client.get("/students/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "class": "10A"}


def test_student_report_matches_contract():
    response = client.get("/students/1/report")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"student", "marks", "total", "average"}
    assert body["student"]["class"] == "10A"
    assert body["total"] == 265
    assert body["average"] == 88.33
    assert [(item["subject"], item["marks"]) for item in body["marks"]] == [
        ("Mathematics", 92),
        ("Science", 85),
        ("English", 88),
    ]


def test_subjects_list():
    response = client.get("/subjects")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "Mathematics",
        "Science",
        "English",
    ]
