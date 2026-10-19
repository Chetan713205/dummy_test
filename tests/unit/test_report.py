import pytest
from fastapi import HTTPException

from main import get_student_report


def test_student_report_uses_contract_fields():
    report = get_student_report(1)

    assert report.total == 265
    assert report.average == 88.33
    assert [(item.subject, item.marks) for item in report.marks] == [
        ("Mathematics", 92),
        ("Science", 85),
        ("English", 88),
    ]


def test_missing_student_report_raises():
    with pytest.raises(HTTPException) as caught:
        get_student_report(99)

    assert caught.value.status_code == 404
