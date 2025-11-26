# Jess Voice Agent - Quick Start Guide

## 🚀 Setup in 5 Steps

### 1️⃣ Configure Credentials
```bash
cd /Users/willianmartinez/voice_agent
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 2️⃣ Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configure Database
```bash
python setup_db.py  # Shows you the SQL to run in Supabase
# Go to Supabase → SQL Editor → Run the SQL
python seed_data.py  # Load test data
```

### 4️⃣ Start Server
```bash
uvicorn main:app --reload
# Server running at http://localhost:8000
```

### 5️⃣ Expose with Ngrok
```bash
# In another terminal:
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

---

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Case Details (after confirming identity)
```bash
curl -X POST http://localhost:8000/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567"}'
```

### Propose Payment Plan (installments)
```bash
curl -X POST http://localhost:8000/tools/propose-payment-plan \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567", "installments": 3}'
```

### Propose Payment Plan (discount)
```bash
curl -X POST http://localhost:8000/tools/propose-payment-plan \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567", "offer_amount": 400}'
```

### Update Status
```bash
curl -X POST http://localhost:8000/tools/update-status \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567", "new_status": "promised_to_pay", "summary": "Customer agreed to 3 installments"}'
```

---

## 🎙️ Configure ElevenLabs

### 1. Create Agent
- Go to [ElevenLabs Dashboard](https://elevenlabs.io)
- Create new Conversational AI Agent
- Name: "Jess"

### 2. System Prompt
- Open `prompt_guide.md`
- Copy the "SYSTEM PROMPT" section
- Paste it into the agent's instructions field

### 3. Configure Tools
Add these 3 tools (use your ngrok URL):

**Tool 1: get_case_details**
- URL: `https://your-ngrok.ngrok.io/tools/get-case-details`
- Method: POST
- Parameters: `{"phone": {"type": "string"}}`

**Tool 2: propose_payment_plan**
- URL: `https://your-ngrok.ngrok.io/tools/propose-payment-plan`
- Method: POST
- Parameters: 
  ```json
  {
    "phone": {"type": "string"},
    "installments": {"type": "integer"},
    "offer_amount": {"type": "number"}
  }
  ```

**Tool 3: update_status**
- URL: `https://your-ngrok.ngrok.io/tools/update-status`
- Method: POST
- Parameters:
  ```json
  {
    "phone": {"type": "string"},
    "new_status": {"type": "string"},
    "summary": {"type": "string"}
  }
  ```

### 4. Connect Twilio
- In ElevenLabs → Telephony
- Connect your Twilio account
- Configure number for outbound calls

---

## 🧪 Test the System

### Test Phone Numbers
- `+15551234567` - María González ($500, 15 days overdue)
- `+15559876543` - Carlos Rodríguez ($1,200, 45 days overdue)
- `+15555555555` - Ana Martínez ($250, 7 days overdue)

### Local Test
```bash
# Verify everything works:
python test_setup.py
```

### Test with ElevenLabs
1. In ElevenLabs, use "Test Call"
2. Enter one of the test numbers
3. Jess should call and follow the complete flow

---

## 📁 Important Files

| File | Description |
|------|-------------|
| `main.py` | FastAPI with 3 endpoints |
| `database.py` | Supabase connection |
| `setup_db.py` | Script to create tables |
| `seed_data.py` | Test data |
| `prompt_guide.md` | Instructions for Jess |
| `README.md` | Complete documentation |
| `.env` | Credentials (create from .env.example) |

---

## 🐛 Troubleshooting

### "Missing required environment variables"
→ Verify that `.env` exists and has correct credentials

### "Customer not found"
→ Run `python seed_data.py`

### ElevenLabs cannot call endpoints
→ Verify ngrok is running and use the HTTPS URL

### Jess doesn't respond
→ Check FastAPI server logs
→ Verify System Prompt in ElevenLabs
→ Ensure tools are properly configured

---

## 📚 Complete Documentation

- **README.md** - Complete installation and usage guide
- **prompt_guide.md** - Detailed Jess configuration
- **walkthrough.md** - Implementation summary

---

## ✅ Verification Checklist

- [ ] Supabase configured and table created
- [ ] Test data loaded
- [ ] FastAPI server running
- [ ] Ngrok exposing the server
- [ ] Agent created in ElevenLabs
- [ ] System prompt configured
- [ ] 3 tools configured with correct URLs
- [ ] Twilio connected
- [ ] Test call successfully completed

---

**Ready to start! 🎉**
