# GenuVoice - AI Voice Agent Platform

Autonomous debt collection system with conversational AI voice agents. Built with FastAPI, ElevenLabs Conversational AI, and Supabase.

## 🏗️ Current Architecture

```
┌──────────────┐
│  Dashboard   │  https://genuvoice.com (HTML/JS/Bootstrap)
│  Web Panel   │  - Customer list, status, agent selection
└──────┬───────┘
       │
┌──────▼───────┐
│  FastAPI API │  https://genuvoice.com/api + /tools
│  AWS EC2     │  - Tool endpoints for ElevenLabs
│              │  - Dashboard API endpoints
└──────┬───────┘
       │
       ├──────────┬─────────────┐
       │          │             │
┌──────▼──┐  ┌───▼────────┐  ┌─▼──────────┐
│Supabase │  │ ElevenLabs │  │   Twilio   │
│PostgreSQL  │  Conversational  │  Telephony │
└─────────┘  │     AI     │  └────────────┘
             └────────────┘
```

## 🛠️ Tech Stack

**Infrastructure:**
- AWS EC2 t2.micro (Amazon Linux 2023)
- Docker + Docker Compose
- Nginx (reverse proxy + SSL termination)
- Let's Encrypt (SSL certificates)
- AWS Route 53 (DNS management)

**Frontend:**
- Clean "Quiet Luxury" design (Mercury/Stripe inspired)
- Bootstrap 5 + Custom CSS
- Dynamic Agent Selection

**Domain:** genuvoice.com

## 📁 Project Structure

```
voice_agent/
├── main.py                    # FastAPI app (tool endpoints + dashboard API)
├── database.py                # Supabase client initialization
├── make_call.py               # Script to initiate outbound calls (CLI)
├── list_agents.py             # Utility to list available ElevenLabs agents
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .gitignore                 # Excludes logs/, .env, etc.
│
├── static/                    # Frontend dashboard
│   ├── dashboard.html         # Main dashboard page
│   ├── landing.html           # Landing page
│   ├── css/styles.css         # Custom styles (Dark/Light themes)
│   └── js/app.js             # Dashboard logic (API calls, UI updates)
│
├── logs/                      # Application logs (auto-generated)
│
├── tools_config/              # ElevenLabs tool configurations (JSON)
│
├── jess_prompt_v2.txt         # English agent prompt (optimized)
├── jess_prompt_v2_es.txt      # Spanish agent prompt (optimized)
│
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Container orchestration
├── nginx.conf                 # Nginx configuration
│
├── AWS_DEPLOYMENT_SUMMARY.md  # AWS deployment documentation
└── OUTBOUND_CALLS_GUIDE.md    # Guide for call operations
```

## 🔑 Environment Variables (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key

# ElevenLabs
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_AGENT_ID=agent_xxx (Default Agent)
AGENT_PHONE_NUMBER_ID=phnum_xxx
```

## 🗄️ Database Schema (Supabase)

**Table:** `customers`

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Customer full name |
| phone | text | Phone number (E.164 format) |
| debt_amount | numeric | Debt amount in USD |
| due_date | date | Original due date |
| status | text | Current status (active, promised_to_pay, refused, etc.) |
| risk_level | text | Risk level (low, medium, high) |
| updated_at | timestamptz | Last update timestamp (Used for "Last Action") |

## 🔌 API Endpoints

### Tool Endpoints (for ElevenLabs)

**POST /tools/get-customer-name**
- Retrieves customer name for identity verification.

**POST /tools/get-case-details**
- Gets full debt information after identity confirmed.

**POST /tools/propose-payment-plan**
- Calculates installment plans or validates settlements.

**POST /tools/update-status**
- Updates customer status after call ends.

### Dashboard API Endpoints

**GET /api/agents**
- Returns list of available ElevenLabs agents.

**GET /api/customers**
- Returns list of all customers with status and risk metrics.

**POST /api/call**
- Initiates ElevenLabs outbound call to a specific customer using a selected agent.

**GET /dashboard** 
- Serves dashboard HTML interface.

**GET /**
- Serves landing page.

## 🤖 ElevenLabs Agents

The system supports multiple agents. The current active agents (fetched dynamically) include:
1. **Jess (Standard)**
2. **Jess Paisa (Latam)**

**Tool Configuration:**
- All tools use `dynamic_variable: "system__called_number"` for phone parameter.

## 🚀 AWS Deployment

**Instance:**
- IP: 3.219.214.103
- URL: [https://genuvoice.com](https://genuvoice.com)

**Deployment Workflow:**

```bash
# 1. Upload updated files
scp -i ~/.ssh/voice-agent-key.pem main.py ec2-user@3.219.214.103:~/voice_agent/
scp -i ~/.ssh/voice-agent-key.pem -r static ec2-user@3.219.214.103:~/voice_agent/

# 2. SSH and Rebuild
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
cd ~/voice_agent
sudo docker stop jess-voice-agent
sudo docker rm jess-voice-agent
sudo docker build -t jess-voice-agent .
sudo docker run -d --name jess-voice-agent --env-file .env -p 8000:8000 -v ~/voice_agent/logs:/app/logs jess-voice-agent
```

## 📝 Logging System

**Configured similar to Serilog (.NET):**
- Console output: INFO level
- File output: DEBUG level → `logs/app_YYYYMMDD.log`
- Errors only: ERROR level → `logs/errors_YYYYMMDD.log`
- Rotating files: 10MB max, 5 backups

## 🐛 Common Issues & Fixes

**Issue:** "Last Action" column empty.
**Fix:** The system now falls back to `updated_at` timestamps if specific call logs are missing.

**Issue:** Dropdown text invisible.
**Fix:** CSS forces black text on white background for form inputs.

---

**Project Status:** ✅ Fully operational and production-ready for PoC
**Last Updated:** December 13, 2025
