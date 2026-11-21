# BolKhata (बोलखाता / ಬೋಲ್‌ಖಾತಾ)
### *The Ledger You Talk To.*

> **Project Theme:** Voice AI for Bharat – Financial Record-Keeping for Informal Retail  
> **Team:** Neural Nomads  
> **Institution:** New Horizon College of Engineering  

---

## 1. Product Overview
**BolKhata** is an AI-powered, multilingual, voice-first digital ledger tailored specifically for Indian kirana shopkeepers and small informal retailers. It replaces physical paper credit notebooks (*udhaar khata*) with a conversational voice interface supporting **Kannada, Hindi, English, and colloquial code-mixed Indian dialects** (e.g., Hinglish and Kanglish).

A shopkeeper can speak naturally (e.g. *"Ramesh ka 340 udhaar, kal 200 diya tha"*), and BolKhata simultaneously parses multiple financial events, confirms them, records them with double-entry precision in the ledger, recalculates balances, and responds with natural vernacular speech.

---

## 2. Problem Statement
Informal retail (kirana stores, provision shops, vegetable stalls) forms the financial backbone of local Indian commerce. Over 90% of informal retail transactions in India happen on short-term trust credit (*udhaar*). However:
- Physical registers suffer from torn pages, math errors, and missing transaction records.
- Existing digital accounting apps require tedious manual smartphone typing, which is frustrating and impractical for shopkeepers serving continuous foot traffic with busy hands.
- Language and digital literacy barriers prevent informal merchants from adopting complex English-first SaaS dashboards.

---

## 3. Proposed Solution
BolKhata introduces a **zero-friction voice-first workflow**:
- **Push-to-Talk Simplicity**: One prominent mic tap on the dashboard.
- **Multilingual & Code-Mixed Understanding**: Natural understanding of compound Indian sentences in Kannada, Hindi, and English.
- **Compound Multi-Event Parsing**: Recognizes simultaneous credit and payment events in a single utterance.
- **Deterministic Financial Safety**: Pure decimal arithmetic; balances are calculated strictly from confirmed ledger entries, never fabricated by AI.
- **Offline-First PWA**: Allows recording transactions even when local mobile network connectivity drops.

---

## 4. Key Features

- **Push-to-Talk Voice Centerpiece**: Visual audio waveform, live speech transcription, and instant intent classification.
- **Compound Sentence Parsing**: Recognizes multiple events in a single sentence (e.g., Credit of ₹340 today + Payment of ₹200 yesterday).
- **Ambiguity Detection & Clarification**: Intercepts unclear commands (e.g., missing amounts or ambiguous credit/payment) and asks clarification questions before recording.
- **Double-Entry Style Ledger Math**: Strict Python `Decimal` arithmetic preventing floating-point rounding errors.
  $$\text{Outstanding Balance} = \sum \text{Confirmed Credits} - \sum \text{Confirmed Payments}$$
- **Full Customer Khata Management**: Customer search, balance tracking, transaction history statements, and advance credit support.
- **Audit-Preserving Corrections & Reversals**: Mistakes can be corrected or undone without deleting historical transactions, maintaining a complete tamper-proof audit trail.
- **Conversational Financial Assistant**: Instant voice answers to queries like *"Who owes me the most money?"* and *"How much did I collect today?"*
- **Polite Payment Reminders**: Auto-generates respectful payment reminders in Hindi, Kannada, and English with one-click WhatsApp sharing.
- **Offline-First Mode (PWA)**: IndexedDB client queue with idempotency keys preventing duplicates upon reconnection.

---

## 5. Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (Indian Kirana palette: Deep Forest Green `#1B4332`, Sage `#40916C`, Warm Cream `#FDFCF7`)
- **Icons**: Lucide React
- **Routing**: React Router v6
- **Data Fetching & State**: TanStack Query (React Query)
- **Offline Storage**: IndexedDB via `idb` library + Service Worker PWA

### Backend
- **Framework**: FastAPI (Python 3.11 - 3.14+)
- **Database**: SQLite (local development & instant evaluation) / PostgreSQL-compatible architecture
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT token authentication with PBKDF2-HMAC-SHA256 password hashing

### AI & Speech Pipeline (`backend/app/ai/`)
- `language_detector.py`: Heuristic & n-gram Indic code-mix detector (Kannada, Hindi, English).
- `intent_classifier.py`: Financial intent classifier (`ADD_CREDIT`, `RECORD_PAYMENT`, `CHECK_BALANCE`, `REVERSE_TRANSACTION`, `CORRECT_TRANSACTION`, etc.).
- `entity_extractor.py`: Extracts amounts, relative dates (*kal*, *aaj*, *ninne*, *ivattu*), and customer names.
- `transaction_parser.py`: Multi-event sentence clause splitter and entity binder.
- `response_generator.py`: Generates spoken and written vernacular confirmations.
- `speech_to_text.py`: Modular STT provider (Bhashini / OpenAI Whisper / Web Speech API).
- `text_to_speech.py`: Modular TTS synthesizer.

---

## 6. Project Architecture

```
bolkhata/
│
├── frontend/                     # React + TypeScript + Vite Frontend
│   ├── public/                   # Static assets, favicon, logo, manifest.json, sw.js
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, BottomNav, VoiceCenterpiece, ConfirmationModal
│   │   ├── context/              # AuthContext, LanguageContext
│   │   ├── layouts/              # AppLayout shell
│   │   ├── pages/                # Dashboard, VoiceAssistant, Customers, CustomerDetail, Transactions, Reports, Reminders, Settings, Welcome
│   │   ├── services/             # API client, token handling
│   │   ├── types/                # TypeScript interface definitions
│   │   ├── utils/                # IndexedDB offline storage
│   │   ├── App.tsx               # Main routing & React Query setup
│   │   └── main.tsx              # Application entrypoint
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── ai/                   # Voice & NLU pipeline
│   │   ├── api/                  # REST endpoints (auth, customers, transactions, voice, assistant, reports, sync)
│   │   ├── core/                 # Config, security, JWT
│   │   ├── database/             # SQLAlchemy engine & demo seed scripts
│   │   ├── models/               # Relational ORM models
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── services/             # Decimal ledger engine, customer service, report service, sync service
│   │   └── main.py               # FastAPI application initialization
│   ├── tests/                    # Pytest test suites (ledger math, voice AI, Ramesh acceptance test)
│   ├── requirements.txt
│   └── Dockerfile
│
├── scripts/                      # Startup and testing helper scripts (PowerShell & Bash)
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variable reference
├── DEVELOPMENT_PLAN.md           # Engineering plan & milestones
├── TASKS.md                      # Progress tracking checklist
└── README.md                     # Comprehensive project documentation
```

---

## 7. Setup & Installation Instructions

### Prerequisites
- **Python**: Version 3.11, 3.12, 3.13, or 3.14
- **Node.js**: Version 18, 20, 22, or 24 with npm
- **Operating System**: Windows, macOS, or Linux

---

### Step 1: Clone or Navigate to Project
```powershell
# Windows PowerShell
cd "C:\Users\MRUDHULA P\.gemini\antigravity\scratch\bolkhata"
```

```bash
# Linux / macOS
cd bolkhata
```

---

### Step 2: Backend Setup & Dependency Installation

#### Windows PowerShell:
```powershell
cd backend
python -m pip install -r requirements.txt
```

#### Linux / macOS:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 3: Frontend Setup & Dependency Installation

#### Windows PowerShell:
```powershell
cd ../frontend
npm.cmd install
```

#### Linux / macOS:
```bash
cd ../frontend
npm install
```

---

## 8. Running the Application

### Option A: Running with PowerShell Scripts (Windows)

Open two terminal windows:

**Terminal 1 (Backend API):**
```powershell
cd "C:\Users\MRUDHULA P\.gemini\antigravity\scratch\bolkhata"
.\scripts\run_backend.ps1
```
*Backend starts on `http://127.0.0.1:8000` with interactive Swagger API docs at `http://127.0.0.1:8000/docs`.*

**Terminal 2 (Frontend UI):**
```powershell
cd "C:\Users\MRUDHULA P\.gemini\antigravity\scratch\bolkhata"
.\scripts\run_frontend.ps1
```
*Frontend opens at `http://localhost:5173`.*

---

### Option B: Running with Docker Compose
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 9. Demo Credentials & Instant Mode

BolKhata includes a pre-seeded Indian kirana store demonstration environment:

- **Shop Name**: Sharma Kirana & General Store
- **Shopkeeper**: Rajesh Sharma
- **Mobile Number**: `9876543210`
- **Password**: `demo1234`
- **Pre-seeded Customers**:
  - **Ramesh**: Clean opening balance of ₹0 (Reserved for the critical acceptance test!)
  - **Suresh**: ₹850 outstanding
  - **Priya**: ₹420 outstanding
  - **Anjali**: ₹0 (settled)
  - **Kumar**: ₹1,200 outstanding

> **Instant Demo Access**: You can click **"Explore in Demo Mode"** directly on the welcome screen to bypass typing credentials.

---

## 10. Critical End-to-End Acceptance Test (The Ramesh Scenario)

To execute the critical end-to-end acceptance test defined in the specifications:

1. **Initial Condition**: Customer **Ramesh** has an opening balance of **₹0**.
2. **Shopkeeper Voice Input**:
   > *"Ramesh ka 340 udhaar, kal 200 diya tha."*
3. **Multi-Event Extraction**:
   BolKhata automatically identifies **TWO separate transactions**:
   - **Event 1**: Ramesh • Credit • ₹340 • Today
   - **Event 2**: Ramesh • Payment • ₹200 • Yesterday
4. **Confirmation Interface**:
   The user reviews and confirms both transactions.
5. **Database Execution & Ledger Math**:
   - Confirmed Credit: +₹340.00
   - Confirmed Payment: -₹200.00
   - **New Outstanding Balance**: ₹340.00 − ₹200.00 = **₹140.00**
6. **Spoken Response**:
   > *"Ramesh ka ₹140 baaki hai. ₹340 ka udhaar aur kal ₹200 ka payment record kar diya."*
7. **Verification**:
   A voice balance query (*"Ramesh ka kitna baaki hai?"*) immediately returns **₹140**.

---

## 11. Automated Testing Suite

Automated Pytest test suites verify financial calculations, shop data isolation, voice NLU parsing, ambiguity handling, and the complete Ramesh scenario:

```powershell
# Run Pytest in Windows PowerShell
cd backend
python -m pytest -v
```

### Test Coverage Highlights:
- `tests/test_ledger_math.py`:
  - `test_credit_increases_and_payment_decreases_balance`
  - `test_multiple_credits_and_payments_math`
  - `test_advance_negative_balance`
  - `test_idempotency_prevents_duplicate_transactions`
  - `test_reversal_creates_audit_and_recalculates_balance`
  - `test_correction_preserves_audit_trail`
  - `test_shop_data_isolation`
- `tests/test_ramesh_acceptance.py`:
  - `test_critical_ramesh_end_to_end_acceptance_scenario` (Full 8-step verification)
- `tests/test_voice_ai.py`:
  - `test_language_detection` (Kannada, Hindi, English, Code-mixed)
  - `test_intent_classification`
  - `test_ambiguity_detection`
  - `test_relative_date_extraction`

---

## 12. API Documentation

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### Key Endpoints:
- `POST /api/auth/register`: Register shopkeeper & store.
- `POST /api/auth/login`: Mobile + password authentication.
- `POST /api/auth/demo`: One-click evaluator login.
- `GET /api/customers`: List customers with computed live balances.
- `GET /api/customers/{id}/ledger`: Full customer ledger history.
- `POST /api/transactions`: Create confirmed financial record.
- `POST /api/transactions/{id}/correct`: Adjust transaction amount while preserving audit log.
- `POST /api/transactions/{id}/reverse`: Reverse transaction with compensating record.
- `POST /api/voice/interpret`: Extract multi-event financial entities from speech transcripts.
- `POST /api/voice/confirm`: Atomically write confirmed events to the database and generate spoken responses.
- `POST /api/assistant/query`: Natural language SQL queries for shop financials.
- `GET /api/reports/daily`: Daily credit, collections, and net change.
- `GET /api/reports/monthly`: Monthly revenue trends and top debtors.
- `POST /api/sync/push`: Synchronize offline-queued transactions idempotently.
- `POST /api/seed/reset`: Reset demo data back to clean state.

---

## 13. Security & Financial Integrity

- **Deterministic Arithmetic**: Powered by Python's standard `Decimal` class (`ROUND_HALF_UP`) ensuring zero floating-point imprecision.
- **Shop-Level Row Isolation**: All customer, transaction, and report queries enforce tenant `shop_id` scoping.
- **Idempotency Protection**: Every offline synchronization item carries a UUID operation token preventing double-posting.
- **Audit Logging**: Every transaction creation, correction, and reversal generates an immutable record in `transaction_audit`.

---

## 14. Team Information
- **Team Name**: Neural Nomads
- **Institution**: New Horizon College of Engineering
- **Project**: BolKhata – The Ledger You Talk To
