import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app


def client(tmp_path):
    return create_app(f"sqlite:///{tmp_path}/t.db").test_client()


S = {"name": "Asha", "email": "Asha@Example.com", "department": "AI/ML", "year": 3, "cgpa": 8.7}


def test_crud(tmp_path):
    c = client(tmp_path)
    r = c.post("/api/students", json=S)
    assert r.status_code == 201 and r.get_json()["email"] == "asha@example.com"
    sid = r.get_json()["id"]
    assert len(c.get("/api/students?q=asha").get_json()) == 1
    assert c.put(f"/api/students/{sid}", json={**S, "cgpa": 9.1}).get_json()["cgpa"] == 9.1
    assert c.get("/api/stats").get_json()["total"] == 1
    assert c.delete(f"/api/students/{sid}").status_code == 200
    assert c.get("/api/students").get_json() == []


def test_validation_and_duplicates(tmp_path):
    c = client(tmp_path)
    assert c.post("/api/students", json={**S, "cgpa": 15}).status_code == 400
    c.post("/api/students", json=S)
    assert c.post("/api/students", json=S).status_code == 409


def test_health(tmp_path):
    assert client(tmp_path).get("/api/health").get_json()["status"] == "ok"
