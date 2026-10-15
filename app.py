"""CloudBase - student records app backed by a cloud database (Amazon RDS MySQL)."""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Student, db

load_dotenv()


def create_app(database_url=None):
    app = Flask(__name__)
    url = database_url or os.environ.get("DATABASE_URL") or "sqlite:///cloudbase_local.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = url
    # pool_pre_ping reconnects if RDS dropped an idle connection
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 280}
    db.init_app(app)
    with app.app_context():
        db.create_all()

    def validate(d):
        for f in ("name", "email", "department", "year", "cgpa"):
            if d.get(f) in (None, ""):
                return f"{f} is required"
        try:
            if not 0 <= float(d["cgpa"]) <= 10:
                return "cgpa must be between 0 and 10"
            if not 1 <= int(d["year"]) <= 6:
                return "year must be between 1 and 6"
        except (TypeError, ValueError):
            return "year and cgpa must be numbers"
        return None

    @app.get("/")
    def index():
        kind = "MySQL (RDS)" if url.startswith("mysql") else url.split(":")[0]
        return render_template("index.html", db_kind=kind)

    @app.get("/api/health")
    def health():
        db.session.execute(db.text("SELECT 1"))
        return jsonify(status="ok", database=url.split(":")[0])

    @app.get("/api/students")
    def list_students():
        q = request.args.get("q", "").strip()
        query = Student.query
        if q:
            like = f"%{q}%"
            query = query.filter(Student.name.ilike(like) | Student.department.ilike(like)
                                 | Student.email.ilike(like))
        return jsonify([s.to_dict() for s in query.order_by(Student.id.desc()).all()])

    @app.post("/api/students")
    def add_student():
        d = request.get_json() or {}
        err = validate(d)
        if err:
            return jsonify(error=err), 400
        s = Student(name=d["name"].strip(), email=d["email"].strip().lower(),
                    department=d["department"].strip(), year=int(d["year"]), cgpa=float(d["cgpa"]))
        db.session.add(s)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error="A student with this email already exists"), 409
        return jsonify(s.to_dict()), 201

    @app.put("/api/students/<int:sid>")
    def update_student(sid):
        s = db.get_or_404(Student, sid)
        d = request.get_json() or {}
        err = validate(d)
        if err:
            return jsonify(error=err), 400
        s.name, s.department = d["name"].strip(), d["department"].strip()
        s.email, s.year, s.cgpa = d["email"].strip().lower(), int(d["year"]), float(d["cgpa"])
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error="A student with this email already exists"), 409
        return jsonify(s.to_dict())

    @app.delete("/api/students/<int:sid>")
    def delete_student(sid):
        db.session.delete(db.get_or_404(Student, sid))
        db.session.commit()
        return jsonify(ok=True)

    @app.get("/api/stats")
    def stats():
        total = db.session.query(func.count(Student.id)).scalar()
        avg = db.session.query(func.avg(Student.cgpa)).scalar()
        by_dept = db.session.query(Student.department, func.count(Student.id)) \
            .group_by(Student.department).all()
        return jsonify(total=total, avg_cgpa=round(avg, 2) if avg else 0,
                       by_department={d: c for d, c in by_dept})

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
