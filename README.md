# 🏥 KleckAdvice Agent

An AI-powered web platform that reads patient lab reports (including scanned PDFs), tracks user activity history, and turns complex medical data into clear, visual, and conversational health insights — built for the **Hack2Heal** hackathon.

## 🌟 What It Does

- **Secure User Access:** Features a centralized Login and Registration system to keep patient environments completely isolated.
- **Direct PDF Processing:** Users can upload lab report PDFs (including scanned pages) directly to a specialized engine for rapid multi-page processing.
- **AI-Driven Health Analysis:** A LangGraph-powered LLM agent extracts complex lab values, references normal thresholds, flags abnormal results, and generates a conversational summary alongside an aggregate risk score.
- **Dynamic Visual Analytics:** Renders interactive data visualizations (Lab Values vs. Normal Range column ranges and a Risk Gauge) powered by Highcharts.
- **Conversational Health Q&A:** Patients can type follow-up questions about their specific metrics in plain language.
- **Live User Compliance Auditing:** Keeps a personal, real-time activity ledger showing exact timestamps, actions (`REGISTER`, `LOGIN_SUCCESS`, `PDF_ANALYZE`, `ASK_QUESTION`), and metadata securely tied to individual user profiles.

## 🏗️ Architecture
+--------------------------------------------+|       Frontend (HTML/JS + Highcharts)      |+--------+--------------------------+--------+|                          |(Direct Heavy Operations)              (Auth / Audit Traffic)|                          |v                          v+--------------------+      +-----------------------+|  FastAPI (Python)  |      |   Spring Boot (Java)  |+---------+----------+      +-----------+-----------+|                             |(LangGraph Pipeline)             (Data Persistence)v                             v+--------------------+      +-----------------------+|    Groq LLM API    |      |  PostgreSQL Database  |+--------------------+      +-----------------------+

The system implements a high-performance **Decoupled Architecture**:
1. **Frontend to FastAPI:** Large, compute-heavy PDF files and AI question texts bypass the Java environment entirely to save system memory and eliminate network latency.
2. **Frontend to Spring Boot:** Lightweight governance traffic (User credentials, verification tokens, and event audit metadata) goes to the Java layer.
3. **Spring Boot to PostgreSQL:** Java Spring Boot persists structured user definitions and permanent historical compliance logs into an enterprise-grade background PostgreSQL server.

## 🛠️ Tech Stack

- **Frontend:** Single Page Application (SPA) built using HTML5, CSS3, Vanilla JavaScript, and Highcharts.
- **Identity & Compliance Gateway:** Java, Spring Boot (Spring Data JPA, Hibernate).
- **Core Intelligence Pipeline:** Python 3.10+, FastAPI, LangGraph, Groq, PyMuPDF (fitz), and `pytesseract` (OCR).
- **Relational Storage Engine:** PostgreSQL.

## 🚀 Setup & Installation

### 1. Database Provisioning
Ensure a local instance of **PostgreSQL** is running on your machine. Access your SQL terminal client and instantiate a database matching your naming configurations:
```sql
CREATE DATABASE postgres;
```

### 2. Java Governance Layer (Spring Boot)
1. Open your `src/main/resources/application.properties` file and supply your PostgreSQL database server properties:
   ```properties
   spring.datasource.url=jdbc:postgresql://localhost:5432/postgres
   spring.datasource.username=postgres
   spring.datasource.password=your_secret_password_here
   spring.jpa.hibernate.ddl-auto=update
   spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
   ```
2. Launch the Java compilation and server engine:
   ```bash
   cd spring_backend
   ./mvnw spring-boot:run
   ```
   *The authorization gateway will sit alive on `http://localhost:8080`.*

### 3. Python Analysis Pipeline (FastAPI)
1. Install your project dependencies:
   ```bash
   cd python_backend
   pip install -r requirements.txt --break-system-packages
   ```
2. Configure your external environment runtime credentials:
   ```bash
   export GROQ_API_KEY="your-groq-api-key-here"
   ```
3. Boot up your production-ready ASGI web runner:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The intelligence engine will sit alive on `http://localhost:8000`.*

### 4. Client Presentation Layer
1. Open your browser and navigate directly to your Java asset location: **`http://localhost:8080`** (or open `index.html`).
2. Register an account or log in via the secure gateway screen to automatically initialize your personalized medical analysis environment.

## 📦 System Requirements

- **Runtime Environments:** Python 3.10+ and Java JDK 17+.
- **Database Server:** PostgreSQL 16+.
- **OCR Engine Dependency:** Tesseract OCR binary must be installed locally on your system path:
  - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
  - **macOS:** `brew install tesseract`
  - **Windows PC:** Download installer binaries from the [UB-Mannheim Tesseract Repository](https://github.com/UB-Mannheim/tesseract/wiki).
- **API Access:** A functional Groq Cloud Developer API key available from [Groq Console](https://console.groq.com).

## ⚠️ Medical Disclaimer

This application delivers general educational metrics intended strictly to help users comprehend standard clinical lab ranges. It is **not a diagnostic framework** or medical device, and does not provide or replace certified professional healthcare advice. Patients must always consult an authorized medical doctor or clinical professional for accurate medical interpretation of diagnostic outcomes.

## 👥 Team
**KleckAdvice**