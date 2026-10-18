from datetime import date
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


# ---------- core helper ----------

def get_connection():
    """Open a new connection to the elearning database."""
    return psycopg2.connect(**DB_CONFIG)


def run_query(sql, params=None, fetch=True):
    """Run one SQL statement.
    fetch=True  -> for SELECT: returns a list of dicts (one per row)
    fetch=False -> for INSERT / UPDATE / DELETE: returns None
    %s placeholders keep user input out of the SQL text (prevents SQL injection).
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            result = cur.fetchall() if fetch else None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------- students ----------

def get_students():
    return run_query(
        "SELECT student_id, name, email, joined_on FROM students ORDER BY student_id"
    )


def add_student(name, email):
    run_query("INSERT INTO students (name, email) VALUES (%s, %s)",
              (name, email), fetch=False)


def update_student(student_id, name, email):
    run_query("UPDATE students SET name = %s, email = %s WHERE student_id = %s",
              (name, email, student_id), fetch=False)


def delete_student(student_id):
    run_query("DELETE FROM students WHERE student_id = %s",
              (student_id,), fetch=False)


# ---------- courses ----------

def get_instructors():
    return run_query("SELECT instructor_id, name FROM instructors ORDER BY name")


def get_courses():
    return run_query("""
        SELECT c.course_id, c.title, c.description, c.duration_hours,
               i.name AS instructor
        FROM courses c
        LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
        ORDER BY c.course_id
    """)


def add_course(title, description, instructor_id, duration_hours):
    run_query("""INSERT INTO courses (title, description, instructor_id, duration_hours)
                 VALUES (%s, %s, %s, %s)""",
              (title, description, instructor_id, duration_hours), fetch=False)


def update_course(course_id, title, description, instructor_id, duration_hours):
    run_query("""UPDATE courses
                 SET title = %s, description = %s, instructor_id = %s, duration_hours = %s
                 WHERE course_id = %s""",
              (title, description, instructor_id, duration_hours, course_id), fetch=False)


def delete_course(course_id):
    run_query("DELETE FROM courses WHERE course_id = %s", (course_id,), fetch=False)


# ---------- enrollments ----------

def enroll_student(student_id, course_id):
    run_query("INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
              (student_id, course_id), fetch=False)


def get_enrollments():
    return run_query("""
        SELECT e.enrollment_id, s.name AS student, c.title AS course,
               e.enrolled_on, e.status
        FROM enrollments e
        JOIN students s ON s.student_id = e.student_id
        JOIN courses  c ON c.course_id  = e.course_id
        ORDER BY e.enrollment_id
    """)


def delete_enrollment(enrollment_id):
    run_query("DELETE FROM enrollments WHERE enrollment_id = %s",
              (enrollment_id,), fetch=False)


def set_enrollment_status(enrollment_id, status):
    run_query("UPDATE enrollments SET status = %s WHERE enrollment_id = %s",
              (status, enrollment_id), fetch=False)


# ---------- progress ----------

def get_modules(course_id):
    return run_query(
        "SELECT module_id, title, module_order FROM modules "
        "WHERE course_id = %s ORDER BY module_order", (course_id,))


def record_progress(student_id, module_id, score):
    """Mark a module completed with a score. If a row already exists, update it."""
    run_query("""
        INSERT INTO progress (student_id, module_id, completed, score, completed_on)
        VALUES (%s, %s, TRUE, %s, CURRENT_DATE)
        ON CONFLICT (student_id, module_id)
        DO UPDATE SET completed = TRUE, score = EXCLUDED.score,
                      completed_on = CURRENT_DATE
    """, (student_id, module_id, score), fetch=False)


# ---------- reports ----------

def get_course_completion():
    """Per course: how many students enrolled, how many finished every module, and the rate."""
    rows = run_query("""
        WITH totals AS (
            SELECT course_id, COUNT(*) AS total
            FROM modules
            GROUP BY course_id
        ),
        done AS (
            SELECT p.student_id, m.course_id, COUNT(*) AS done
            FROM progress p
            JOIN modules m ON m.module_id = p.module_id
            WHERE p.completed = TRUE
            GROUP BY p.student_id, m.course_id
        )
        SELECT c.course_id, c.title,
               COUNT(e.enrollment_id) AS enrolled,
               COUNT(e.enrollment_id) FILTER (
                   WHERE COALESCE(t.total, 0) > 0 AND COALESCE(d.done, 0) = t.total
               ) AS completed
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.course_id
        LEFT JOIN totals t ON t.course_id = c.course_id
        LEFT JOIN done d ON d.course_id = c.course_id AND d.student_id = e.student_id
        GROUP BY c.course_id, c.title
        ORDER BY c.course_id
    """)
    for r in rows:
        r["rate"] = round(100 * r["completed"] / r["enrolled"], 1) if r["enrolled"] else 0.0
    return rows


def get_top_scorers(course_id=None, limit=5):
    """Students ranked by average score. Pass a course_id to rank within one course."""
    return run_query("""
        SELECT s.name,
               COUNT(p.progress_id)   AS modules_done,
               ROUND(AVG(p.score), 1) AS avg_score
        FROM progress p
        JOIN students s ON s.student_id = p.student_id
        JOIN modules  m ON m.module_id  = p.module_id
        WHERE p.completed = TRUE AND p.score IS NOT NULL
          AND (%s IS NULL OR m.course_id = %s)
        GROUP BY s.student_id, s.name
        ORDER BY avg_score DESC, modules_done DESC
        LIMIT %s
    """, (course_id, course_id, limit))


# ---------- feature 1: early-warning list ----------

def classify_risk(avg_score, days_inactive):
    """Rule-based risk level. Returns (level, reason)."""
    if avg_score is None or days_inactive is None:
        return "Medium", "no modules completed yet"

    level = "Low"
    reasons = []

    if avg_score < 40:
        level = "High"
        reasons.append(f"average score {avg_score}")
    elif avg_score < 60:
        level = "Medium"
        reasons.append(f"average score {avg_score}")

    if days_inactive >= 14:
        level = "High"
        reasons.append(f"no module completed in {days_inactive} days")
    elif days_inactive >= 7:
        if level == "Low":
            level = "Medium"
        reasons.append(f"no module completed in {days_inactive} days")

    return level, ", ".join(reasons) if reasons else "on track"


def get_early_warning():
    """One row per student with a Low / Medium / High label and a reason."""
    rows = run_query("""
        SELECT s.student_id, s.name,
               COUNT(p.progress_id)            AS modules_done,
               ROUND(AVG(p.score), 1)          AS avg_score,
               (CURRENT_DATE - MAX(p.completed_on)) AS days_inactive
        FROM students s
        LEFT JOIN progress p ON p.student_id = s.student_id AND p.completed = TRUE
        GROUP BY s.student_id, s.name
        ORDER BY s.student_id
    """)
    result = []
    for r in rows:
        level, reason = classify_risk(r["avg_score"], r["days_inactive"])
        r["risk"] = level
        r["reason"] = reason
        result.append(r)
    order = {"High": 0, "Medium": 1, "Low": 2}
    result.sort(key=lambda r: order[r["risk"]])   # worst first
    return result


# ---------- feature 2: certificates ----------

def issue_certificate(student_id, course_id):
    """Issue a certificate only if every module of the course is completed.
    Returns the certificate code, or None if the course isn't finished."""
    existing = run_query(
        "SELECT certificate_code FROM certificates WHERE student_id = %s AND course_id = %s",
        (student_id, course_id))
    if existing:
        return existing[0]["certificate_code"]

    total = run_query("SELECT COUNT(*) AS n FROM modules WHERE course_id = %s",
                      (course_id,))[0]["n"]
    done = run_query("""
        SELECT COUNT(*) AS n FROM progress p
        JOIN modules m ON m.module_id = p.module_id
        WHERE p.student_id = %s AND m.course_id = %s AND p.completed = TRUE
    """, (student_id, course_id))[0]["n"]

    if total == 0 or done < total:
        return None

    code = f"CERT-{date.today().year}-{uuid.uuid4().hex[:6].upper()}"
    run_query("""INSERT INTO certificates (student_id, course_id, certificate_code)
                 VALUES (%s, %s, %s)""", (student_id, course_id, code), fetch=False)
    return code


def verify_certificate(code):
    """Returns a dict (student, course, issued_on) if the code is valid, else None."""
    rows = run_query("""
        SELECT s.name AS student, c.title AS course, ce.issued_on
        FROM certificates ce
        JOIN students s ON s.student_id = ce.student_id
        JOIN courses  c ON c.course_id  = ce.course_id
        WHERE ce.certificate_code = %s
    """, (code.strip(),))
    return rows[0] if rows else None


# ---------- quick self-test: run `python db.py` ----------

if __name__ == "__main__":
    print("Students:", len(get_students()))
    print("\nEarly-warning list:")
    for r in get_early_warning():
        print(f"  {r['name']:<16} {r['risk']:<7} {r['reason']}")
    print("\nCourse completion:")
    for r in get_course_completion():
        print(f"  {r['title']:<26} {r['enrolled']} enrolled, {r['completed']} completed, {r['rate']}%")
    print("\nTop scorers:", [(r["name"], r["avg_score"]) for r in get_top_scorers()])
    print("\nVerify CERT-2026-0001:", verify_certificate("CERT-2026-0001"))
    print("Verify FAKE-CODE:     ", verify_certificate("FAKE-CODE"))