# BolKhata - Comprehensive Development Plan
**The Ledger You Talk To**
*Team: Neural Nomads | Institution: New Horizon College of Engineering*
*Theme: Voice AI for Bharat – Financial Record-Keeping for Informal Retail*

---

## 1. Executive Summary & Goals
BolKhata is an AI-powered, multilingual, voice-first digital ledger tailored for Indian kirana shopkeepers and small retailers. It replaces physical udhaar khata (credit registers) with an intuitive conversational interface in Kannada, Hindi, and English (including code-mixed colloquial dialects like Hinglish and Kanglish).

Key Architectural Pillars:
1. **Financial Integrity First**: Deterministic ledger math using `Decimal` arithmetic, double-entry style ledger state derivation, atomic database operations, and immutable audit logs.
2. **Robust Multilingual Speech & NLU Pipeline**: Handles multi-event voice commands (e.g. "Ramesh ka 340 udhaar, kal 200 diya tha"), detects ambiguity, validates missing fields, and queries live financial data.
3. **Offline-First PWA**: IndexedDB storage, optimistic local updates, and idempotent background sync.
4. **Accessible Indian UI/UX**: Warm Indian aesthetic (forest green `#1B4332`, sage `#40916C`, warm cream `#FDFBF7`), high contrast, prominent voice mic centerpiece, and vernacular voice synthesis.

---

## 2. Technical Architecture

### 2.1 Backend Architecture
- **Language & Runtime**: Python 3.14+
- **Framework**: FastAPI (async REST APIs, automatic OpenAPI docs)
- **Database**: SQLite (local development / zero-config demo) with SQLAlchemy 2.0 ORM and Alembic-compatible schema designed for PostgreSQL production migration.
- **Security**: Passlib / bcrypt / argon2 password hashing, python-jose JWT authentication, shop-level row isolation via tenant filters.
- **AI / Voice Module (`backend/app/ai`)**:
  - `speech_to_text.py`: Multilingual STT interface (Bhashini / OpenAI Whisper / Web Speech fallback).
  - `language_detector.py`: Heuristics and n-gram based Indic code-mix detector (Kannada, Hindi, English).
  - `intent_classifier.py`: Classification for `ADD_CREDIT`, `RECORD_PAYMENT`, `CHECK_BALANCE`, `DAILY_SUMMARY`, `MONTHLY_SUMMARY`, `CORRECT_TRANSACTION`, `REVERSE_TRANSACTION`, `GENERAL_HELP`, etc.
  - `entity_extractor.py`: Extracts amounts, customer names, relative dates (today, yesterday, specific dates), currency, and flags ambiguity.
  - `transaction_parser.py`: Multi-event sentence splitter & composite intent parser (essential for acceptance test: "Ramesh ka 340 udhaar, kal 200 diya tha").
  - `response_generator.py`: Multilingual natural response templating in Kannada, Hindi, and English.
  - `text_to_speech.py`: TTS audio synthesis provider (Indic TTS / browser SpeechSynthesis fallback).
  - `ai_provider.py`: Unified provider abstraction layer with environment-based configuration.

### 2.2 Frontend Architecture
- **Framework**: React 18 / 19 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom Indian Kirana theme (Deep Forest Green, Warm Cream, Sage, Coral/Amber highlights)
- **Icons**: Lucide React
- **Routing**: React Router v6
- **State & Data Fetching**: TanStack Query (React Query) + Context API for Auth and Voice Session
- **Offline / PWA**: Web Service Worker, IndexedDB for local transactions, background sync queue with idempotency keys
- **Audio / Voice Component**: Push-to-Talk audio recorder with Web Audio API visualizer waveform, speech recognition fallback, live transcript editing, and confirmation modal.

### 2.3 Database Schema
- `users`: User credentials, name, mobile, preferred language, timestamps.
- `shops`: Shop metadata, owner foreign key, currency (`INR`).
- `customers`: Customer name, mobile, address, notes, shop FK, archive flag.
- `transactions`: Core ledger records (`CREDIT` or `PAYMENT`), amount (numeric/decimal), transaction date, description, input method (`VOICE`, `MANUAL`, `OFFLINE_SYNC`), status (`CONFIRMED`, `PENDING`, `REVERSED`), idempotency key, reversal pointer.
- `transaction_audit`: Full audit trail for corrections and reversals.
- `pending_sync`: Offline synchronization queue with status and deduplication tokens.
- `reminders`: Payment reminder history and drafted messages.

---

## 3. Development Phases & Milestones

### Phase 1: Environment & Project Scaffolding
- Initialize directory structures (`backend` and `frontend`).
- Set up Python virtual environment and install backend dependencies (FastAPI, Uvicorn, SQLAlchemy, Pydantic, pytest, etc.).
- Scaffold Vite React TypeScript frontend with Tailwind CSS and Lucide icons.

### Phase 2: Database Models & Financial Ledger Engine
- Define SQLAlchemy models with UUID primary keys and proper indexes.
- Implement strict decimal arithmetic ledger calculator:
  `Outstanding = Total Confirmed Credits - Total Confirmed Payments`.
- Implement idempotent transaction creation, reversal, and correction workflows.
- Seed demo data (Ramesh, Suresh, Priya, Anjali, Kumar) with isolated test states.

### Phase 3: Core REST APIs
- Auth routes: register, login, demo-login, me.
- Customer routes: CRUD, search, ledger balance calculation.
- Transaction routes: create, list, filter, correct, reverse.
- Reports routes: daily metrics, monthly trends, outstanding distribution.
- Sync routes: push offline transactions, deduplication.

### Phase 4: Voice & NLU Intelligence Pipeline
- Multi-event voice parser capable of parsing complex compound sentences:
  "Ramesh ka 340 udhaar, kal 200 diya tha" -> Event A (Credit 340 today) + Event B (Payment 200 yesterday).
- Ambiguity detection (e.g. missing amount, ambiguous customer name, unclassified transaction type).
- Natural language response generation in Hindi, Kannada, and English.
- Voice endpoints: `/api/voice/interpret`, `/api/voice/confirm`, `/api/voice/speak`.

### Phase 5: Frontend UI & Voice Experience
- Responsive Layout (Desktop sidebar + Mobile bottom nav & top bar).
- Authentic branding: Logo mark (Ledger + Mic Soundwave), Wordmark, Favicon.
- Dashboard with real-time dynamic KPIs and prominent "Talk to BolKhata" centerpiece.
- Push-to-Talk recording interface with audio visualizer, transcript editor, and dual-event confirmation modal.
- Customer management, Transaction history with filters, Reports with charts, Reminders with WhatsApp integration, Settings with language switcher.

### Phase 6: Offline-First & PWA Implementation
- IndexedDB client storage for customers and offline transactions.
- Service worker registration and offline status indicator.
- Sync manager that triggers automatic synchronization when back online.

### Phase 7: Verification & Testing
- Automated Pytest suite: financial math, multi-event voice parsing, shop isolation, reversals, and the Ramesh acceptance test.
- Frontend verification and cross-browser responsiveness testing.
- End-to-end Ramesh workflow verification: ₹340 credit + ₹200 yesterday payment => ₹140 outstanding.

### Phase 8: DevOps & Documentation
- Dockerfile for backend and frontend, `docker-compose.yml`.
- Comprehensive `README.md` with instructions for Windows PowerShell and Unix, API specs, demo credentials, and architectural diagrams.
