TRUNCATE certificates, progress, enrollments, modules, courses, instructors, students RESTART IDENTITY CASCADE;

INSERT INTO instructors (name, email) VALUES
('Dr. Priya Nair', 'priya.nair@example.com'),
('Prof. Arjun Rao', 'arjun.rao@example.com'),
('Ms. Lakshmi Iyer', 'lakshmi.iyer@example.com');

INSERT INTO students (name, email) VALUES
('Aarav Sharma', 'aarav@example.com'),
('Diya Patel', 'diya@example.com'),
('Karthik Raj', 'karthik@example.com'),
('Meera Krishnan', 'meera@example.com'),
('Rohan Das', 'rohan@example.com'),
('Sneha Reddy', 'sneha@example.com');

INSERT INTO courses (title, description, instructor_id, duration_hours) VALUES
('Python Fundamentals', 'Core Python programming from scratch', 1, 20),
('SQL and Databases', 'Relational databases and SQL queries', 2, 15),
('Web Development Basics', 'HTML, CSS and JavaScript essentials', 3, 18);

INSERT INTO modules (course_id, title, module_order) VALUES
(1, 'Variables and Data Types', 1),
(1, 'Control Flow', 2),
(1, 'Functions', 3),
(1, 'File Handling', 4),
(2, 'Intro to SQL', 1),
(2, 'Joins', 2),
(2, 'Normalization', 3),
(2, 'Transactions', 4),
(3, 'HTML Basics', 1),
(3, 'CSS Styling', 2),
(3, 'JavaScript Basics', 3),
(3, 'Responsive Design', 4);

INSERT INTO enrollments (student_id, course_id) VALUES
(1,1),(1,2),(2,1),(3,1),(3,3),(4,2),(4,3),(5,1),(5,2),(6,3);

INSERT INTO progress (student_id, module_id, completed, score, completed_on) VALUES
-- Aarav: finished Python, started SQL
(1,1,TRUE,88,CURRENT_DATE-12),(1,2,TRUE,92,CURRENT_DATE-10),
(1,3,TRUE,85,CURRENT_DATE-8),(1,4,TRUE,90,CURRENT_DATE-5),
(1,5,TRUE,78,CURRENT_DATE-3),(1,6,TRUE,82,CURRENT_DATE-1),
-- Diya: 3 of 4 Python modules
(2,1,TRUE,70,CURRENT_DATE-9),(2,2,TRUE,75,CURRENT_DATE-6),(2,3,TRUE,68,CURRENT_DATE-2),
-- Karthik: low scores, inactive
(3,1,TRUE,35,CURRENT_DATE-20),(3,2,TRUE,40,CURRENT_DATE-18),(3,9,TRUE,45,CURRENT_DATE-17),
-- Meera: finished SQL, 2 web modules
(4,5,TRUE,95,CURRENT_DATE-14),(4,6,TRUE,91,CURRENT_DATE-11),
(4,7,TRUE,89,CURRENT_DATE-7),(4,8,TRUE,93,CURRENT_DATE-4),
(4,9,TRUE,80,CURRENT_DATE-3),(4,10,TRUE,85,CURRENT_DATE-1),
-- Rohan: one module, then went silent
(5,1,TRUE,55,CURRENT_DATE-25),
-- Sneha: 3 of 4 web modules
(6,9,TRUE,72,CURRENT_DATE-8),(6,10,TRUE,78,CURRENT_DATE-5),(6,11,TRUE,81,CURRENT_DATE-2);

INSERT INTO certificates (student_id, course_id, certificate_code) VALUES
(1, 1, 'CERT-2026-0001'),
(4, 2, 'CERT-2026-0002');
