-- Створення бази даних 
CREATE DATABASE IF NOT EXISTS mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE mydb;

-- Таблиця ролей
CREATE TABLE IF NOT EXISTS Role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Таблиця користувачів (додано поле password)
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Додано для зберігання хешованих паролів
    last_name VARCHAR(100),
    first_name VARCHAR(100),
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Role(id)
);

-- Таблиця категорій опитувань
CREATE TABLE IF NOT EXISTS QuizCategory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Таблиця опитувань
CREATE TABLE IF NOT EXISTS Quiz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'draft',
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES QuizCategory(id)
);

-- Таблиця питань
CREATE TABLE IF NOT EXISTS Question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    text TEXT NOT NULL,
    question_type ENUM('single_choice', 'multiple_choice', 'text') NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id) ON DELETE CASCADE
);

-- Таблиця варіантів відповідей
CREATE TABLE IF NOT EXISTS Option (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,  -- Додано для позначення правильних відповідей
    FOREIGN KEY (question_id) REFERENCES Question(id) ON DELETE CASCADE
);

-- Таблиця відповідей користувачів
CREATE TABLE IF NOT EXISTS Answer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    question_id INT NOT NULL,
    option_id INT,  -- NULL для текстових відповідей
    text_answer TEXT,  -- NULL для питань з варіантами
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id),
    FOREIGN KEY (question_id) REFERENCES Question(id),
    FOREIGN KEY (option_id) REFERENCES Option(id)
);

-- Додаткові таблиці (якщо потрібні для вашого функціоналу)
CREATE TABLE IF NOT EXISTS QuizAssignment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (quiz_id) REFERENCES Quiz(id),
    UNIQUE KEY (user_id, quiz_id)
);

-- Початкові дані
INSERT INTO Role (id, name) VALUES
(1, 'Admin'),
(2, 'Expert'),
(3, 'User');


INSERT INTO QuizCategory (id, name) VALUES
(1, 'Education'),
(2, 'Healthcare'),
(3, 'Technology');


-- Приклад користувача (пароль: admin123 - потрібно хешувати в реальному додатку)
INSERT INTO User (id, email, password, last_name, first_name, role_id) VALUES
(1, 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin', 'System', 1),
(2, 'expert@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Expert', 'John', 2),
(3, 'user@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'User', 'Alice', 3);


INSERT INTO QuizAssignment (user_id, quiz_id) VALUES
(3, 1),  -- Alice → Python Basics
(3, 2),  -- Alice → Internet Safety
(2, 1);  -- Expert John → Python Basics

-- Приклад опитування
INSERT INTO Quiz (id, title, description, start_date, end_date, status, category_id) VALUES
(1, 'Python Basics', 'Test your knowledge of Python fundamentals', '2023-01-01', '2023-12-31', 'active', 3),
(2, 'Internet Safety', 'Quiz about online security best practices', '2023-01-01', '2023-12-31', 'active', 2);


-- Приклад питань
INSERT INTO Question (id, quiz_id, text, question_type) VALUES
(1, 1, 'What is a variable in Python?', 'single_choice'),
(2, 1, 'Select correct data types in Python:', 'multiple_choice'),
(3, 2, 'How to protect your online password?', 'text');


-- Приклад варіантів відповідей
INSERT INTO Option (id, question_id, text, is_correct) VALUES
(1, 1, 'A container for storing data values', TRUE),
(2, 1, 'A function name', FALSE),
(3, 2, 'int', TRUE),
(4, 2, 'str', TRUE),
(5, 2, 'html', FALSE);



-- Приклад відповідей користувачів
INSERT INTO Answer (id, user_id, quiz_id, question_id, option_id, text_answer) VALUES
(1, 3, 1, 1, 1, NULL),  -- Alice відповіла на 1 питання (single choice)
(2, 3, 1, 2, 3, NULL),  -- Alice вибрала "int"
(3, 3, 1, 2, 4, NULL),  -- Alice вибрала "str"
(4, 3, 2, 3, NULL, 'Use strong passwords and two-factor authentication');
