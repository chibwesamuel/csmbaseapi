# CSMBaseAPI

**CSMBaseAPI** is a **cloud-native backend platform** for managing business data through **REST** and **GraphQL APIs**.  
It powers SaaS applications by providing secure, scalable APIs for handling **users, organizations, projects, tasks, and notifications** — with no frontend, just APIs.

---

## 🚀 Project Goal
Building the backend for a SaaS company.  
CSMBaseAPI provides the foundation to manage:

- **Users**  
- **Organizations**  
- **Projects**  
- **Tasks**  
- **Notifications**  

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.10.12) |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT, OAuth2 |
| **GraphQL** | Strawberry GraphQL |
| **Validation** | Pydantic |
| **Containerization** | Docker, Docker Compose |
| **Cloud** | AWS EC2, AWS RDS, AWS S3 |
| **Reverse Proxy** | Nginx |
| **CI/CD** | GitHub Actions |
| **Testing** | Pytest |
| **Documentation** | Swagger, OpenAPI |
| **Version Control** | Git, GitHub |

---

## 🏗 Architecture

```
               Client
          REST / GraphQL
                 │
          FastAPI Backend
       Authentication Layer
                 │
       Business Logic Layer
                 │
         SQLAlchemy ORM
                 │
            PostgreSQL
                 │
             AWS RDS
```

---

## ✨ Features

### 🔑 Authentication
- Register, Login, Refresh Token  
- Forgot Password, Email Verification  
- JWT-based secure sessions  

### 🏢 Organizations
- Create, Edit, Delete  
- Invite Members  

### 👤 Users
- CRUD operations  
- Roles & Permissions  

### 📂 Projects
- CRUD operations  
- Assign Users, Status, Deadline  

### ✅ Tasks
- CRUD operations  
- Priority, Labels, Comments, Attachments  

### 🔔 Notifications
- Email & API-based  
- Search, Pagination, Sorting, Filtering  

### 📊 Admin Dashboard API
- Statistics: User Count, Project Count, Task Count, Active Users  

---

## ⚡ Advanced Features
- Redis caching  
- Rate Limiting  
- Background Jobs with Celery  
- Structured Logging  
- Health Check Endpoint: `GET /health`  
- Metrics with Prometheus  

---

## 🐳 Docker Compose
One command to start everything:

```bash
docker compose up
```

---

## ☁️ AWS Deployment
- Deploy backend to **EC2**  
- Database hosted on **RDS**  
- File storage in **S3**  

---

## 🔄 CI/CD Pipeline
Every push triggers:

1. Run Tests  
2. Lint Code  
3. Build Docker Image  
4. Deploy to AWS  

---

## 📖 Documentation
- Interactive API docs via **Swagger** and **OpenAPI**  
- Architecture diagram included  

---

## ✅ Testing
- Unit & integration tests with **Pytest**