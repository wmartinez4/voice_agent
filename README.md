# GenuVoice - AI Voice Agent Platform

Autonomous debt collection system with conversational AI voice agents. Built with FastAPI, ElevenLabs Conversational AI, and Supabase.

## 🏗️ Current Architecture

```
┌──────────────┐
│  Dashboard   │  https://genuvoice.com (HTML/JS/Bootstrap)
│  Web Panel   │  - Customer list, status, call initiation
└──────┬───────┘
       │
┌──────▼───────┐
│  FastAPI API │  https://genuvoice.com/api + /tools
│  AWS EC2     │  - Tool endpoints for ElevenLabs
└──────┬───────┘  - Dashboard API endpoints
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

**Backend:**
- FastAPI (Python 3.9+)
- Supabase (PostgreSQL + Python client)
- Python logging (file + console output)

**Voice AI:**
- ElevenLabs Conversational AI (2 agents: English + Spanish)
- Twilio (telephony provider)

**Frontend:**
- HTML5 + Vanilla JavaScript
- Bootstrap 5 (UI framework)
- No build process required

**Infrastructure:**
- AWS EC2 t2.micro (Amazon Linux 2023)
- Docker + Docker Compose
- Nginx (reverse proxy + SSL termination)
- Let's Encrypt (SSL certificates)
- AWS Route 53 (DNS management)

**Domain:** genuvoice.com

## 📁 Project Structure

```
voice_agent/
├── main.py                    # FastAPI app (tool endpoints + dashboard API)
├── database.py                # Supabase client initialization
├── make_call.py               # Script to initiate outbound calls
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .gitignore                 # Excludes logs/, .env, etc.
│
├── static/                    # Frontend dashboard
│   ├── index.html            # Main dashboard page
│   ├── css/styles.css        # Custom styles
│   └── js/app.js             # Dashboard logic (API calls, UI updates)
│
├── logs/                      # Application logs (auto-generated)
│   ├── app_YYYYMMDD.log      # All logs (DEBUG+)
│   └── errors_YYYYMMDD.log   # Errors only (ERROR+)
│
├── tools_config/              # ElevenLabs tool configurations (JSON)
│   ├── tool_1_get_customer_name.json
│   ├── tool_2_get_case_details.json
│   ├── tool_3_propose_payment_plan.json
│   └── tool_4_update_status.json
│
├── jess_prompt_v2.txt         # English agent prompt (optimized)
├── jess_prompt_v2_es.txt      # Spanish agent prompt (optimized)
├── POC_AGENT_FLOW.txt         # Demo flow documentation
│
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Container orchestration
├── nginx.conf                 # Nginx configuration
│
└── AWS_DEPLOYMENT_SUMMARY.md  # AWS deployment documentation
```

## 🔑 Environment Variables (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key

# ElevenLabs
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_AGENT_ID=agent_xxx (current: Spanish agent)
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
| updated_at | timestamptz | Last update timestamp |

**Test Data (3 customers):**
- Willian Martinez: +573124199685, $664
- Mauricio Ordonez: +16787079207, $850
- Mauricio Cuevas: +16173653176, $1,200

## 🔌 API Endpoints

### Tool Endpoints (for ElevenLabs)

**POST /tools/get-customer-name**
- Retrieves customer name for identity verification
- Called FIRST before revealing any sensitive info
- Input: `{ "phone": "+573124199685" }`
- Output: `{ "customer_name": "Willian Martinez" }`

**POST /tools/get-case-details**
- Gets full debt information after identity confirmed
- Input: `{ "phone": "+573124199685" }`
- Output: `{ customer_name, debt_amount, due_date, risk_level, days_overdue }`

**POST /tools/propose-payment-plan**
- Calculates installment plans or validates settlements
- Input: `{ "phone": "+573...", "installments": 3 }` OR `{ "phone": "+573...", "offer_amount": 500 }`
- Output: `{ plan_type, installment_amount, payment_dates, total_amount, discount_applied, accepted, message }`

**POST /tools/update-status**
- Updates customer status after call ends
- Input: `{ "phone": "+573...", "new_status": "promised_to_pay", "summary": "..." }`
- Output: `{ "success": true, "message": "..." }`

### Dashboard API Endpoints

**GET /api/customers**
- Returns list of all customers with status
- Output: Array of CustomerListItem objects

**POST /api/call**
- Initiates ElevenLabs outbound call
- Input: `{ "phone": "+573124199685" }`
- Output: `{ "success": true, "conversation_id": "conv_xxx", "customer_name": "..." }`

**GET /** 
- Serves dashboard HTML interface

**GET /health**
- Health check endpoint

## 🤖 ElevenLabs Agents

**Agent 1 (English):**
- Agent ID: `agent_8701kaydfsgkf06ryjpg7hqd9am2`
- Prompt: `jess_prompt_v2.txt`
- Voice: Natural English female voice
- Initial greeting: "Hi! <break time="0.3s"/> This is Jess. <break time="0.3s"/> Am I speaking with the account holder?"

**Agent 2 (Spanish):**
- Agent ID: `agent_2701kb5wfzw7e1dr1xcq4zwptjxw` (CURRENT)
- Prompt: `jess_prompt_v2_es.txt`
- Voice: Natural Spanish female voice
- Initial greeting: "¡Hola! <break time="0.3s"/> Habla Jess. <break time="0.3s"/> ¿Hablo con el titular de la cuenta?"

**Tool Configuration:**
- All 4 tools use `dynamic_variable: "system__called_number"` for phone parameter
- URLs point to: `https://genuvoice.com/tools/...`

## 🚀 AWS Deployment

**Instance:**
- Type: t2.micro (AWS Free Tier)
- OS: Amazon Linux 2023
- IP: 3.219.214.103
- Region: us-east-1

**Domain:**
- Domain: genuvoice.com (AWS Route 53)
- DNS: A record → 3.219.214.103
- SSL: Let's Encrypt (auto-renewal configured)
- Expires: 2026-03-13

**Containers:**
- `jess-voice-agent`: FastAPI app (port 8000)
- `jess-nginx`: Nginx reverse proxy (ports 80, 443)

**Access:**
```bash
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
```

## 📦 Local Development

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure .env
Copy credentials from AWS EC2:
```bash
scp -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103:~/voice_agent/.env .env
```

### 3. Run Locally
```bash
# Terminal 1: FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Ngrok (if testing with ElevenLabs)
ngrok http 8000
```

### 4. Access Dashboard
```
http://localhost:8000/
```

## 🔄 Deployment Workflow

### Deploy Code Changes to AWS

```bash
# 1. Upload updated files
scp -i ~/.ssh/voice-agent-key.pem main.py ec2-user@3.219.214.103:~/voice_agent/
scp -i ~/.ssh/voice-agent-key.pem -r static ec2-user@3.219.214.103:~/voice_agent/

# 2. SSH to EC2
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103

# 3. Rebuild and restart
cd ~/voice_agent
docker stop jess-voice-agent jess-nginx
docker rm jess-voice-agent jess-nginx
docker build -t jess-voice-agent .
docker run -d --name jess-voice-agent --restart unless-stopped \
  -p 8000:8000 --env-file .env \
  -v /home/ec2-user/voice_agent/logs:/app/logs \
  -v /home/ec2-user/voice_agent/static:/app/static \
  jess-voice-agent
docker run -d --name jess-nginx --restart unless-stopped \
  -p 80:80 -p 443:443 \
  -v /home/ec2-user/voice_agent/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  --link jess-voice-agent:api \
  nginx:alpine

# 4. Verify
docker ps
docker logs --tail 20 jess-voice-agent
curl https://genuvoice.com/health
```

## 🧪 Testing

### Test Tool Endpoints
```bash
# Get customer name
curl -X POST https://genuvoice.com/tools/get-customer-name \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573124199685"}'

# Get case details
curl -X POST https://genuvoice.com/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573124199685"}'
```

### Test Dashboard API
```bash
# List customers
curl https://genuvoice.com/api/customers

# Initiate call
curl -X POST https://genuvoice.com/api/call \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573124199685"}'
```

### Test Call Script
```bash
# From local machine
cd /Users/willianmartinez/voice_agent
source venv/bin/activate
python make_call.py +573124199685  # Calls Willian Martinez
python make_call.py +16787079207   # Calls Mauricio Ordonez
python make_call.py +16173653176   # Calls Mauricio Cuevas
```

### Access Dashboard
```
https://genuvoice.com
```

## 📝 Logging System

**Configured similar to Serilog (.NET):**
- Console output: INFO level
- File output: DEBUG level → `logs/app_YYYYMMDD.log`
- Errors only: ERROR level → `logs/errors_YYYYMMDD.log`
- Rotating files: 10MB max, 5 backups

**View logs on AWS:**
```bash
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
docker logs -f jess-voice-agent
tail -f ~/voice_agent/logs/app_*.log
```

## 🔐 SSL Certificate Renewal

Let's Encrypt certificates expire every 90 days. Renewal is configured but verify:

```bash
# Check certificate expiry
sudo certbot certificates

# Manual renewal (if needed)
docker stop jess-nginx
sudo certbot renew
docker start jess-nginx
```

## 🎯 ElevenLabs Configuration

**Current Tools URLs (update these if domain/IP changes):**
```
https://genuvoice.com/tools/get-customer-name
https://genuvoice.com/tools/get-case-details
https://genuvoice.com/tools/propose-payment-plan
https://genuvoice.com/tools/update-status
```

**Tool Parameters:**
- All tools have `phone` parameter configured as:
  - `value_type: "dynamic_variable"`
  - `dynamic_variable: "system__called_number"`
  - `required: true`

**Dynamic Variables:**
ElevenLabs automatically provides `system__called_number` during real calls. This ensures tools receive the correct phone number.

## 🌐 Dashboard Features

**Current Implementation:**
- Customer list with real-time data from Supabase
- Status badges (active, promised, refused, etc.)
- Risk level indicators (low, medium, high)
- Days overdue calculation with color coding
- One-click call initiation
- Modal feedback for call status
- Auto-refresh every 30 seconds

**Access:** https://genuvoice.com

**Security Note:** Currently no authentication. Add login system for production.

## 🔧 Key Configuration Files

**Dockerfile:**
- Base: `python:3.9-slim`
- Installs gcc, curl, Python deps
- Exposes port 8000
- Mounts logs and static directories

**docker-compose.yml:**
- `api` service: FastAPI app
- `nginx` service: Reverse proxy with SSL

**nginx.conf:**
- HTTP → HTTPS redirect
- Proxies all traffic to FastAPI (port 8000)
- SSL certificates from `/etc/letsencrypt/`

**.env (required secrets):**
```
SUPABASE_URL=
SUPABASE_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_AGENT_ID=
AGENT_PHONE_NUMBER_ID=
```

## 🚨 Important Notes

**Agent Prompts:**
- `jess_prompt_v2.txt`: Optimized English prompt (436 lines, ~50% token reduction)
- `jess_prompt_v2_es.txt`: Optimized Spanish prompt (neutral Latin Spanish)
- Both include: privacy-first approach, empathetic tone, error handling protocols

**Tool Execution Order:**
1. `get_customer_name` - ALWAYS FIRST (privacy)
2. `get_case_details` - After identity confirmed
3. `propose_payment_plan` - If customer requests
4. `update_status` - At end of EVERY call

**Error Handling Protocol:**
- Critical tools (1 & 2): End call gracefully if they fail
- Non-critical tools (3): Promise specialist follow-up
- Logging tool (4): Fail silently, don't tell customer

## 💻 AWS Management

**AWS CLI Profile:** `pocaws`

**Common Commands:**
```bash
# View EC2 instances
aws ec2 describe-instances --profile pocaws

# Update security group
aws ec2 authorize-security-group-ingress \
  --group-name voice-agent-sg \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0 \
  --profile pocaws

# Check Route 53 records
aws route53 list-resource-record-sets \
  --hosted-zone-id Z08503645DZMGVPUFCZT \
  --profile pocaws
```

**EC2 Instance ID:** Check with `aws ec2 describe-instances --profile pocaws`

**Security Group:** `voice-agent-sg`

**SSH Key:** `~/.ssh/voice-agent-key.pem`

## 🔄 Making Changes

### Backend Changes
1. Edit `main.py` locally
2. Test locally with `uvicorn main:app --reload`
3. Deploy to AWS (see Deployment Workflow above)
4. Restart containers

### Frontend Changes
1. Edit files in `static/` locally
2. Test by opening `static/index.html` in browser
3. Upload to AWS: `scp -i ~/.ssh/voice-agent-key.pem -r static ec2-user@3.219.214.103:~/voice_agent/`
4. No restart needed (static files)

### ElevenLabs Prompt Changes
1. Edit `jess_prompt_v2.txt` or `jess_prompt_v2_es.txt`
2. Copy entire content
3. Paste in ElevenLabs agent configuration
4. Save and test

### Database Changes
1. Go to Supabase dashboard
2. SQL Editor
3. Run migrations
4. Update models in `main.py` if schema changed

## 📊 Monitoring

**View Real-time Logs:**
```bash
# Application logs
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
docker logs -f jess-voice-agent

# Nginx logs
docker logs -f jess-nginx

# File logs
tail -f ~/voice_agent/logs/app_*.log
```

**Check Service Health:**
```bash
curl https://genuvoice.com/health
curl https://genuvoice.com/api/customers
```

## 🐛 Common Issues

**Issue:** Containers not starting after reboot
```bash
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
docker start jess-voice-agent jess-nginx
```

**Issue:** SSL certificate expired
```bash
sudo certbot renew
docker restart jess-nginx
```

**Issue:** ElevenLabs tools failing
- Check tool URLs in ElevenLabs dashboard
- Verify `system__called_number` is configured correctly
- Check API logs: `docker logs jess-voice-agent`

**Issue:** Dashboard not loading customers
- Check browser console for JavaScript errors
- Verify API endpoint: `curl https://genuvoice.com/api/customers`
- Check CORS is enabled in `main.py`

## 💰 Current Costs

| Service | Cost |
|---------|------|
| AWS EC2 t2.micro | $0/month (free tier 12 months), then ~$8-10/month |
| genuvoice.com domain | $13/year (Route 53) + $0.50/month (hosted zone) |
| Let's Encrypt SSL | Free |
| ElevenLabs | Pay per usage (calls) |
| Twilio | Pay per usage (calls) |

**Total monthly:** $0.50 (first 12 months), then ~$8-11/month

## 🎯 Next Steps for Production

### Essential:
- [ ] Add authentication to dashboard (login system)
- [ ] Implement API key authentication for `/api/*` endpoints
- [ ] Add rate limiting
- [ ] Create `call_history` table in Supabase
- [ ] Add monitoring/alerting (AWS CloudWatch)

### Nice to Have:
- [ ] Call history view in dashboard
- [ ] Advanced filters and search
- [ ] Export to CSV/Excel
- [ ] Real-time WebSocket updates
- [ ] Analytics and reporting
- [ ] Multi-user support with roles
- [ ] Payment link generation
- [ ] SMS notifications

## 📞 Support

**Documentation:**
- AWS Deployment: `AWS_DEPLOYMENT_SUMMARY.md`
- Demo Flow: `POC_AGENT_FLOW.txt`
- Agent Prompts: `jess_prompt_v2.txt`, `jess_prompt_v2_es.txt`

**External Resources:**
- ElevenLabs: https://elevenlabs.io/docs
- Supabase: https://supabase.com/docs
- FastAPI: https://fastapi.tiangolo.com

---

**Project Status:** ✅ Fully operational and production-ready for PoC
**Last Updated:** December 13, 2025
