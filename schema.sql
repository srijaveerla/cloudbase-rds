-- Optional: the app creates this table automatically. Run manually if you prefer.
CREATE DATABASE IF NOT EXISTS cloudbase;
USE cloudbase;

CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(120) NOT NULL UNIQUE,
    department VARCHAR(80)  NOT NULL,
    year       INT          NOT NULL,
    cgpa       DECIMAL(3,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (name, email, department, year, cgpa) VALUES
('Asha Reddy', 'asha@example.com', 'AI/ML', 3, 8.7),
('Ravi Kumar', 'ravi@example.com', 'CSE', 2, 8.1);
