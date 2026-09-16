# Bank ATM System

一个基于 **Vue 3 + FastAPI + MySQL** 实现的简易银行 ATM 系统。

项目采用前后端分离架构，实现了用户注册、登录、余额查询、存款、取款、转账以及交易记录查询等核心功能，用于练习 Vue 前端交互、REST API、数据库操作以及前后端数据联调。

## ✨ Features

- 用户注册与登录
- Argon2 密码哈希存储
- 账户余额查询
- 存款与取款
- 用户间转账
- 转账余额校验
- 禁止向自己转账
- 交易记录持久化
- 按当前用户查询交易记录
- 前后端分离与 Axios API 调用
- MySQL 数据持久化
- 环境变量管理数据库配置

## 🛠 Tech Stack

### Frontend

- Vue 3
- Vite
- Axios
- HTML / CSS / JavaScript

### Backend

- Python
- FastAPI
- PyMySQL
- Pydantic
- pwdlib / Argon2

### Database

- MySQL

## 📁 Project Structure

```text
bank-atm-system/
├── backend/
│   ├── .env.example
│   └── main.py
│
├── database/
│   └── schema.sql
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd bank-atm-system
```

### 2. Create the database

在 MySQL 中执行：

```text
database/schema.sql
```

创建项目所需的数据库和数据表。

### 3. Configure backend environment variables

进入 `backend` 目录，将 `.env.example` 复制为 `.env`：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bank_atm
```

将 `DB_PASSWORD` 修改为本机 MySQL 密码。

> `.env` 包含本地数据库配置，不应提交到 Git 仓库。

### 4. Install backend dependencies

建议创建并激活 Python 虚拟环境，然后安装依赖：

```bash
python -m pip install fastapi uvicorn pymysql python-dotenv "pwdlib[argon2]"
```

启动后端：

```bash
cd backend
python -m uvicorn main:app --reload
```

FastAPI 默认运行在：

```text
http://127.0.0.1:8000
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 5. Install frontend dependencies

进入 `frontend`：

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器默认运行在：

```text
http://localhost:5173
```

## 🔄 Application Flow

```text
Vue
 ↓
Axios
 ↓
FastAPI
 ↓
PyMySQL
 ↓
MySQL
```

前端通过 Axios 调用 FastAPI 接口，FastAPI 对请求数据进行处理与校验，并通过 PyMySQL 操作 MySQL 数据库，最终将结果返回给 Vue 页面。

## 🔐 Security

- 用户密码使用 Argon2 哈希后存入数据库
- SQL 查询使用参数化方式传递数据
- 数据库密码通过 `.env` 环境变量管理
- `.env` 已加入 `.gitignore`，避免敏感配置提交至仓库
- 转账操作使用数据库事务，并在异常情况下执行 rollback

## 📷 Screenshots

项目界面截图将在后续补充。

## 📌 Project Status

ATM 核心功能已完成，目前包含完整的注册、登录、账户操作、转账和交易记录流程。

该项目主要用于实践前后端分离开发、REST API 调用、MySQL 数据操作以及基础业务逻辑设计。