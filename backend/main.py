from fastapi import FastAPI
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_PASSWORD loaded:", os.getenv("DB_PASSWORD") is not None)

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
password_hash = PasswordHash.recommended()

class DepositRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0)

class WithdrawRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0)

class TransferRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float = Field(gt=0)

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/balance/{user_id}")
def balance(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT balance FROM users WHERE id = %s",
        (user_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return {"message": "User not found"}

    return {"balance": result[0]}
@app.post("/deposit")
def deposit(data: DepositRequest):
    connection = get_connection()
    

    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET balance = balance + %s WHERE id = %s",
        (data.amount, data.user_id)
    )
    cursor.execute(
    """
    INSERT INTO transactions (from_user_id, to_user_id, type, amount)
    VALUES (%s, %s, %s, %s)
    """,
    (
        None,
        data.user_id,
        "deposit",
        data.amount
    )
)
    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Deposit successful"}

@app.post("/withdraw")
def withdraw(data: WithdrawRequest):
    connection = get_connection()

    cursor = connection.cursor()

    # 先查询当前余额
    cursor.execute(
        "SELECT balance FROM users WHERE id = %s",
        (data.user_id,)
    )
    result = cursor.fetchone()

    # 用户不存在
    if result is None:
        cursor.close()
        connection.close()
        return {"message": "User not found"}

    balance = result[0]

    # 余额不足
    if balance < data.amount:
        cursor.close()
        connection.close()
        return {"message": "Insufficient balance"}

    # 余额足够，再扣钱
    cursor.execute(
        "UPDATE users SET balance = balance - %s WHERE id = %s",
        (data.amount, data.user_id)
    )
    cursor.execute(
    """
    INSERT INTO transactions (from_user_id, to_user_id, type, amount)
    VALUES (%s, %s, %s, %s)
    """,
    (
        data.user_id,
        None,
        "withdraw",
        data.amount
    )
)
    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Withdraw successful"}

@app.post("/transfer")
def transfer(data: TransferRequest):

    if data.from_user_id == data.to_user_id:
        return {"message": "Cannot transfer to yourself"}

    connection = get_connection()

    cursor = connection.cursor()

    try:
        # 查询并锁定转出账户
        cursor.execute(
            "SELECT balance FROM users WHERE id = %s FOR UPDATE",
            (data.from_user_id,)
        )
        sender = cursor.fetchone()

        if sender is None:
            return {"message": "Sender not found"}

        # 检查收款账户
        cursor.execute(
            "SELECT id FROM users WHERE id = %s",
            (data.to_user_id,)
        )
        receiver = cursor.fetchone()

        if receiver is None:
            return {"message": "Receiver not found"}

        # 检查余额
        if sender[0] < data.amount:
            return {"message": "Insufficient balance"}

        # 转出账户扣款
        cursor.execute(
            "UPDATE users SET balance = balance - %s WHERE id = %s",
            (data.amount, data.from_user_id)
        )

        # 收款账户入账
        cursor.execute(
            "UPDATE users SET balance = balance + %s WHERE id = %s",
            (data.amount, data.to_user_id)
        )

        # 写入交易记录
        cursor.execute(
            """
            INSERT INTO transactions
            (from_user_id, to_user_id, type, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.from_user_id,
                data.to_user_id,
                "transfer",
                data.amount
            )
        )

        connection.commit()

        return {"message": "Transfer successful"}

    except Exception:
        connection.rollback()
        return {"message": "Transfer failed"}

    finally:
        cursor.close()
        connection.close()

@app.get("/transactions/{user_id}")
def get_transactions(user_id: int):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, from_user_id, to_user_id, type, amount, created_at
        FROM transactions
        WHERE from_user_id = %s OR to_user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id, user_id)
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return {"transactions": results}

@app.post("/register")
def register(data: RegisterRequest):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = %s",
        (data.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user is not None:
        cursor.close()
        connection.close()
        return {"message": "Username already exists"}

    hashed_password = password_hash.hash(data.password)

    cursor.execute(
        """
        INSERT INTO users (username, password, balance)
        VALUES (%s, %s, %s)
        """,
        (data.username, hashed_password, 0)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Register successful"}




@app.post("/login")
def login(data: LoginRequest):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, username, password, balance FROM users WHERE username = %s",
        (data.username,)
    )

    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return {"message": "User not found"}

    if not password_hash.verify(data.password, user[2]):
        cursor.close()
        connection.close()
        return {"message": "Incorrect password"}

    cursor.close()
    connection.close()

    return {
        "message": "Login successful",
        "user_id": user[0],
        "username": user[1],
        "balance": user[3]
    }