# E-learning Platform Database

A Python desktop app (Tkinter GUI) backed by a PostgreSQL database for managing
students, courses, enrollments, progress and certificates.

**Team:** Jeevesh S, Dhanshitha Choudary K (SRMIST, CSE)

## Features
- Add, update and delete students and courses
- Enroll students and track module progress and scores
- Early-Warning List: flags at-risk students (Low / Medium / High)
- Certificate Verification by code

## How to run
1. Install PostgreSQL and create a database named `elearning`
2. Run `schema.sql`, then `sample_data.sql`
3. `pip install -r requirements.txt`
4. Copy `config.example.py` to `config.py` and put your PostgreSQL password in it
5. `python gui.py`


## Docs
The project slides and ER diagram are in the `docs/` folder.