from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import pymysql
from datetime import date

app = FastAPI()

# Конфігурація бази даних
DB_CONFIG = {
    "host": "localhost",
    "user": "api_user",
    "password": "secure_pass123",
    "database": "mydb",
    "charset": "utf8mb4"
}

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor
    )

# Pydantic моделі 

class Role(BaseModel):
    id: int
    name: str

class UserBase(BaseModel):
    email: str
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    role_id: int

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class QuizCategory(BaseModel):
    id: int
    name: str

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    category_id: int

class Quiz(QuizBase):
    id: int

class QuestionBase(BaseModel):
    quiz_id: int
    text: str
    question_type: str  # 'single_choice', 'multiple_choice', 'text'

class Question(QuestionBase):
    id: int

class OptionBase(BaseModel):
    question_id: int
    text: str

class Option(OptionBase):
    id: int

class AnswerBase(BaseModel):
    user_id: int
    quiz_id: int
    question_id: int
    option_id: Optional[int] = None  # Для вибору варіантів
    text_answer: Optional[str] = None  # Для текстових відповідей

class Answer(AnswerBase):
    id: int

# Користувачі 

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Перевірка наявності email
            cursor.execute("SELECT id FROM User WHERE email = %s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Вставка нового користувача
            cursor.execute(
                """INSERT INTO User (email, last_name, first_name, role_id) 
                VALUES (%s, %s, %s, %s)""",
                (user.email, user.last_name, user.first_name, user.role_id)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            return {**user.dict(), "id": user_id}
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM User LIMIT %s, %s", (skip, limit))
            return cursor.fetchall()
    finally:
        conn.close()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM User WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    finally:
        conn.close()

# Опитування 

@app.post("/quizzes/", response_model=Quiz)
def create_quiz(quiz: QuizBase):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO Quiz (title, description, start_date, end_date, status, category_id) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (quiz.title, quiz.description, quiz.start_date, quiz.end_date, quiz.status, quiz.category_id)
            )
            quiz_id = cursor.lastrowid
            conn.commit()
            return {**quiz.dict(), "id": quiz_id}
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/quizzes/", response_model=List[Quiz])
def read_quizzes(skip: int = 0, limit: int = 100):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Quiz LIMIT %s, %s", (skip, limit))
            return cursor.fetchall()
    finally:
        conn.close()

@app.get("/quizzes/{quiz_id}", response_model=Quiz)
def read_quiz(quiz_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Quiz WHERE id = %s", (quiz_id,))
            quiz = cursor.fetchone()
            if quiz is None:
                raise HTTPException(status_code=404, detail="Quiz not found")
            return quiz
    finally:
        conn.close()

#Питання

@app.post("/questions/", response_model=Question)
def create_question(question: QuestionBase):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Перевірка наявності опитування
            cursor.execute("SELECT id FROM Quiz WHERE id = %s", (question.quiz_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            cursor.execute(
                """INSERT INTO Question (quiz_id, text, question_type) 
                VALUES (%s, %s, %s)""",
                (question.quiz_id, question.text, question.question_type)
            )
            question_id = cursor.lastrowid
            conn.commit()
            return {**question.dict(), "id": question_id}
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/questions/{question_id}", response_model=Question)
def read_question(question_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Question WHERE id = %s", (question_id,))
            question = cursor.fetchone()
            if question is None:
                raise HTTPException(status_code=404, detail="Question not found")
            return question
    finally:
        conn.close()

#Відповіді
@app.post("/answers/", response_model=Answer)
def create_answer(answer: AnswerBase):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Перевірка наявності користувача, опитування та питання
            cursor.execute("SELECT id FROM User WHERE id = %s", (answer.user_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="User not found")
                
            cursor.execute("SELECT id FROM Quiz WHERE id = %s", (answer.quiz_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Quiz not found")
                
            cursor.execute("SELECT id FROM Question WHERE id = %s", (answer.question_id,))
            question = cursor.fetchone()
            if question is None:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Якщо питання не текстове, перевіряємо наявність варіанту
            if question['question_type'] != 'text' and answer.option_id is None:
                raise HTTPException(status_code=400, detail="Option ID is required for non-text questions")
            
            # Якщо питання текстове, перевіряємо наявність текстової відповіді
            if question['question_type'] == 'text' and answer.text_answer is None:
                raise HTTPException(status_code=400, detail="Text answer is required for text questions")
            
            cursor.execute(
                """INSERT INTO Answer (user_id, quiz_id, question_id, option_id, text_answer) 
                VALUES (%s, %s, %s, %s, %s)""",
                (answer.user_id, answer.quiz_id, answer.question_id, answer.option_id, answer.text_answer)
            )
            answer_id = cursor.lastrowid
            conn.commit()
            return {**answer.dict(), "id": answer_id}
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/answers/{answer_id}", response_model=Answer)
def read_answer(answer_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Answer WHERE id = %s", (answer_id,))
            answer = cursor.fetchone()
            if answer is None:
                raise HTTPException(status_code=404, detail="Answer not found")
            return answer
    finally:
        conn.close()

