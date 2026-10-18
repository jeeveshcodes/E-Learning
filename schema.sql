DROP TABLE IF EXISTS certificates, progress, enrollments, modules, courses, instructors, students CASCADE;

CREATE TABLE students (
    student_id  SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    joined_on   DATE DEFAULT CURRENT_DATE
);

CREATE TABLE instructors (
    instructor_id SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE courses (
    course_id      SERIAL PRIMARY KEY,
    title          VARCHAR(200) NOT NULL,
    description    TEXT,
    instructor_id  INT REFERENCES instructors(instructor_id) ON DELETE SET NULL,
    duration_hours INT DEFAULT 0
);

CREATE TABLE modules (
    module_id    SERIAL PRIMARY KEY,
    course_id    INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    title        VARCHAR(200) NOT NULL,
    module_order INT NOT NULL
);

CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id    INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id     INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrolled_on   DATE DEFAULT CURRENT_DATE,
    status        VARCHAR(20) DEFAULT 'active',
    UNIQUE (student_id, course_id)
);

CREATE TABLE progress (
    progress_id  SERIAL PRIMARY KEY,
    student_id   INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    module_id    INT NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    completed    BOOLEAN DEFAULT FALSE,
    score        NUMERIC(5,2),
    completed_on DATE,
    UNIQUE (student_id, module_id)
);

CREATE TABLE certificates (
    certificate_id   SERIAL PRIMARY KEY,
    student_id       INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id        INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    issued_on        DATE DEFAULT CURRENT_DATE,
    certificate_code VARCHAR(30) UNIQUE NOT NULL,
    UNIQUE (student_id, course_id)
);
