# 🗄️ CloudBase - Student Records on Amazon RDS

A cloud-database project: a **Flask web app + REST API** that stores data in a managed **Amazon RDS (MySQL)** database.
Add, edit, delete and search student records, and view live statistics (total, average CGPA, per department).

Without any cloud account it falls back to a local SQLite file, so you can develop and demo offline.

## Tech stack
Python · Flask · SQLAlchemy · PyMySQL · Amazon RDS (MySQL) · boto3 · HTML/JS

## Architecture
```
Browser ──► Flask app (app.py) ──SQLAlchemy──► Amazon RDS MySQL (cloud)
                 │
                 └── REST API: /api/students, /api/stats, /api/health
```

## Project structure
| Path | Purpose |
|---|---|
| `app.py` | Flask app and REST API |
| `models.py` | `Student` table (SQLAlchemy model) |
| `schema.sql` | Equivalent SQL schema and sample data |
| `templates/index.html` | Web interface |
| `scripts/create_rds.py` | Creates the RDS instance with boto3 |
| `scripts/delete_rds.py` | Deletes the instance (stop billing) |
| `.env.example` | Template for the database connection string |
| `tests/test_api.py` | Automated tests |

## Run locally (SQLite, no AWS)
```bash
python -m venv .venv
.venv\Scripts\activate           # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Connect to Amazon RDS
1. **Create the database** in the AWS Console: RDS → Create database → Standard create → **MySQL** → **Free tier** template.
   Set instance id `cloudbase-db`, master username `admin`, a strong password, class `db.t3.micro`,
   **Public access: Yes** (demo only), initial database name `cloudbase`.
   (Or run `python scripts/create_rds.py --password "..."`.)
2. **Open the port:** RDS instance → Connectivity → VPC security group → Inbound rules → add **MySQL/Aurora (3306)** from **My IP**.
3. **Copy the endpoint** (looks like `cloudbase-db.xxxx.ap-south-1.rds.amazonaws.com`).
4. Copy `.env.example` to `.env` and set `DATABASE_URL=mysql+pymysql://admin:PASSWORD@ENDPOINT:3306/cloudbase`.
5. Run `python app.py` and open `/api/health` - it should return `{"status":"ok"}`.
6. **Delete the instance when done** (RDS console, or `python scripts/delete_rds.py`) to avoid charges.

## REST API
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/students?q=` | List/search students |
| POST | `/api/students` | Add a student |
| PUT | `/api/students/<id>` | Update a student |
| DELETE | `/api/students/<id>` | Delete a student |
| GET | `/api/stats` | Totals and per-department counts |
| GET | `/api/health` | Database connectivity check |

## Security notes
Credentials live in `.env` (git-ignored), inputs are validated, queries go through SQLAlchemy (no SQL injection),
and storage encryption is enabled by the creation script. For production, keep RDS private and put the app in the same VPC.

## Tests
```bash
pytest -q
```

## Future work
Authentication, Docker + EC2/Elastic Beanstalk deployment, read replicas, automated backups/snapshots dashboard, CloudWatch monitoring.

## License
MIT
