# Contract Management Tool - Camunda

A comprehensive Contract Management System capable of handling the lifecycle of contracts—from submission to approval or rejection. The solution leverages **Camunda Platform 7** for process orchestration, **FastAPI** for backend logic, **React (Vite)** for a modern frontend, and **Azure SQL** for robust data persistence.

## 🚀 Features

-   **Dashboard**: Real-time overview of contract statuses (Created, Approved, Rejected).
-   **Workflow Automation**: Business processes managed by Camunda (BPMN).
-   **Contract Management**: Submit, View, Approve, and Reject contracts.
-   **Automated Listeners**: External Python workers handle database operations and notifications.
-   **Email Integration**: Notifications simulated via MailHog.

## 🏗 System Architecture

The project follows a containerized microservices architecture:

| Service | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React + Vite | User Interface for dashboard and contract forms. |
| **Backend** | FastAPI | REST API for data retrieval and initiating workflows. |
| **Workflow Engine** | Camunda 7 | Orchestrates the `Contract_Management_Process` BPMN. |
| **Database** | Azure SQL | Stores contract business data (`CreatedContracts`, etc.). |
| **System DB** | PostgreSQL | Stores Camunda internal data (users, history, etc.). |
| **Workers** | Python | External task clients for Camunda (Save to DB, Send Email). |

## 🛠 Prerequisites

-   **Docker** & **Docker Compose** installed.
-   **Azure SQL** database credentials (server, user, password, db name).

## ⚡ Quick Start

### 1. Configuration

Ensure you have a `.env` file in the `docker/` directory with your Azure SQL credentials.

```bash
# Example .env config
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=contract_db
AZURE_SQL_USER=your_user
AZURE_SQL_PASSWORD=your_password
```

### 2. Run with Docker Compose

The entire stack (Frontend, Backend, Camunda, DBs, Workers) is orchestrated via Docker Compose.

```bash
cd docker
docker compose up -d --build
```

### 3. Access Services

Once the containers are up, access the different components:

| Component | URL | Credentials (if any) |
| :--- | :--- | :--- |
| **Frontend Dashboard** | `http://localhost:5173` | N/A |
| **Backend API** | `http://localhost:8000` | N/A |
| **Camunda Cockpit** | `http://localhost:8080` | `demo` / `demo` |
| **MailHog (Email)** | `http://localhost:8025` | N/A |

### 4. Stopping the System

```bash
docker compose down
```

## 📂 Project Structure

```text
contractManagementTool-camunda/
├── backend/            # FastAPI Application (API & DB Logic)
├── frontend/           # React + Vite Application
├── bpmn/               # BPMN Process Definitions
├── docker/             # Docker Compose & Worker Scripts
│   ├── worker_store_*.py    # External Task Workers
│   ├── docker-compose.yml   # Orchestration
│   └── .env                 # Config (Secrets)
```

## 🔍 Workflow Details

The system follows the `Contract_Management_Process`:
1.  **Contract Submitted**: User submits via Frontend -> Backend starts process.
2.  **Worker Store**: Python worker saves contract to `CreatedContracts` in Azure SQL.
3.  **Approval Task**: User Task in Camunda for Manager approval.
4.  **Decision Gateway**:
    -   **Approved**: Worker saves to `ApprovedContracts`.
    -   **Rejected**: Worker saves to `RejectedContracts`.
