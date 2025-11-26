# Jess Voice Agent - PoC Backend

Autonomous debt collection and retention system with conversational voice agent.

## 🎯 Description

**Jess** is a conversational AI agent designed to make outbound collection calls in a professional and empathetic manner. This repository contains the FastAPI backend that provides the tools Jess uses during conversations.

### Key Features

- ✅ **Privacy-First**: Does not reveal sensitive information until identity is confirmed
- ✅ **Smart Negotiation**: Calculates payment plans and validates offers
- ✅ **Automatic Recording**: Updates the status of each interaction
- ✅ **ElevenLabs Integration**: Designed to work with ElevenLabs Conversational AI

## 🏗️ Architecture

```
┌─────────────────┐
│  ElevenLabs     │ ← Handles voice and conversation
│  + Twilio       │
└────────┬────────┘
         │
         │ HTTP Calls
         ▼
┌─────────────────┐
│  FastAPI        │ ← This repository
│  (Tools API)    │
└────────┬────────┘
         │
         │ SQL Queries
         ▼
┌─────────────────┐
│  Supabase       │ ← PostgreSQL database
│  (PostgreSQL)   │
└─────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Supabase account (free tier available)
- ElevenLabs account
- Twilio account (configured in ElevenLabs)
- Ngrok (for local development)

## 🚀 Installation

### 1. Clone the repository

```bash
cd voice_agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_AGENT_ID=your-agent-id
```

### 5. Configure the database

#### Option A: Using the script (recommended)

```bash
python setup_db.py
```

This script will show you the SQL you need to run in Supabase.

#### Option B: Manual

1. Go to your project at [Supabase](https://supabase.com)
2. Navigate to "SQL Editor"
3. Run the SQL shown in `setup_db.py`

### 6. Load test data

```bash
python seed_data.py
```

This will create 3 test customers with different debt scenarios.

## 🎮 Usage

### Start the server

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`

### Verify it works

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "Jess Voice Agent API",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Expose with Ngrok (for ElevenLabs)

In another terminal:

```bash
ngrok http 8000
```

Copy the HTTPS URL that ngrok gives you (e.g., `https://abc123.ngrok.io`)

## 🔧 API Endpoints

### 1. GET /health
Verifies that the server is running.

### 2. POST /tools/get-case-details

Retrieves customer debt details.

**Request:**
```json
{
  "phone": "+15551234567"
}
```

**Response:**
```json
{
  "debt_amount": 500.00,
  "due_date": "2023-11-01",
  "risk_level": "medium",
  "days_overdue": 15
}
```

### 3. POST /tools/propose-payment-plan

Calculates payment plans or validates discount offers.

**Request (Installments):**
```json
{
  "phone": "+15551234567",
  "installments": 3
}
```

**Request (Discount):**
```json
{
  "phone": "+15551234567",
  "offer_amount": 400.00
}
```

**Response:**
```json
{
  "plan_type": "installments",
  "installment_amount": 166.67,
  "payment_dates": ["2024-01-01", "2024-02-01", "2024-03-01"],
  "total_amount": 500.00,
  "discount_applied": 0.00,
  "accepted": true,
  "message": "Payment plan of 3 installments approved"
}
```

### 4. POST /tools/update-status

Updates customer status after the call.

**Request:**
```json
{
  "phone": "+15551234567",
  "new_status": "promised_to_pay",
  "summary": "Customer agreed to 3 installments of $166.67"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status updated to 'promised_to_pay'"
}
```

## 🎙️ Configure ElevenLabs

### 1. Create the Agent

1. Go to [ElevenLabs Dashboard](https://elevenlabs.io)
2. Create a new Conversational AI Agent
3. Name it "Jess"

### 2. Configure the Voice

- Select a professional female voice (e.g., Rachel, Sarah)
- Adjust:
  - Stability: 0.6-0.7
  - Similarity: 0.7-0.8
  - Style: 0.3-0.4

### 3. Configure the System Prompt

Copy all content from `prompt_guide.md` (SYSTEM PROMPT section) and paste it into the agent's instructions field.

### 4. Configure the Tools

In the agent's "Tools" section, add these 3 tools:

#### Tool 1: get_case_details
- **Name:** `get_case_details`
- **Description:** "Retrieves customer debt information after identity confirmation"
- **URL:** `https://your-ngrok-url.ngrok.io/tools/get-case-details`
- **Method:** POST
- **Parameters:**
  ```json
  {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    }
  }
  ```

#### Tool 2: propose_payment_plan
- **Name:** `propose_payment_plan`
- **Description:** "Calculates payment plans or validates settlement offers"
- **URL:** `https://your-ngrok-url.ngrok.io/tools/propose-payment-plan`
- **Method:** POST
- **Parameters:**
  ```json
  {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "installments": {
      "type": "integer",
      "description": "Number of installments (optional)"
    },
    "offer_amount": {
      "type": "number",
      "description": "Settlement offer amount (optional)"
    }
  }
  ```

#### Tool 3: update_status
- **Name:** `update_status`
- **Description:** "Updates customer status after call completion"
- **URL:** `https://your-ngrok-url.ngrok.io/tools/update-status`
- **Method:** POST
- **Parameters:**
  ```json
  {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "new_status": {
      "type": "string",
      "description": "New status"
    },
    "summary": {
      "type": "string",
      "description": "Interaction summary (optional)"
    }
  }
  ```

### 5. Configure Twilio

1. In ElevenLabs, go to the Telephony section
2. Connect your Twilio account
3. Configure a phone number for outbound calls

## 🧪 Test the System

### Local Test (without real call)

```bash
# Terminal 1: Server
uvicorn main:app --reload

# Terminal 2: Tests
curl -X POST http://localhost:8000/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567"}'
```

### Test with ElevenLabs

1. Make sure ngrok is running
2. In ElevenLabs, use the "Test Call" function
3. Enter one of the test numbers: `+15551234567`
4. Jess should call and follow the complete flow

## 📊 Project Structure

```
voice_agent/
├── main.py              # FastAPI app with endpoints
├── database.py          # Supabase connection
├── setup_db.py          # DB setup script
├── seed_data.py         # Test data
├── trigger.py           # (Optional) Script to initiate calls
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Environment variables (do not commit)
├── prompt_guide.md      # Guide to configure Jess
└── README.md            # This file
```

## 🐛 Troubleshooting

### Error: "Missing required environment variables"
- Verify that your `.env` file exists and has the correct credentials
- Make sure you're in the correct directory

### Error: "Customer not found"
- Run `python seed_data.py` to create test data
- Verify that the phone number includes the country code (e.g., +1)

### ElevenLabs cannot call my endpoints
- Verify that ngrok is running
- Make sure to use the HTTPS URL from ngrok
- Check that CORS is enabled in `main.py` (already configured)

### The call connects but Jess doesn't respond
- Check the FastAPI server logs
- Verify that the System Prompt is configured correctly
- Make sure the tools are properly configured in ElevenLabs

## 📈 Next Steps (Post-PoC)

- [ ] Add authentication to endpoints
- [ ] Implement `interactions` table for complete history
- [ ] Add metrics and analytics
- [ ] Implement rate limiting
- [ ] Add unit tests
- [ ] Deploy to production (Railway, Render, AWS, etc.)
- [ ] Configure custom domain (remove ngrok)

## 🔒 Security

**IMPORTANT for Production:**

- ✅ Never commit the `.env` file
- ✅ Use environment variables in production
- ✅ Implement authentication on endpoints
- ✅ Validate and sanitize all inputs
- ✅ Use HTTPS in production
- ✅ Configure CORS appropriately (don't use `*` in production)

## 📝 License

This is a Proof of Concept (PoC) project for educational purposes.

## 🤝 Contributions

This is a PoC project. For improvements or suggestions, open an issue.

## 📞 Support

For questions about:
- **Backend/API**: Check the logs in the terminal
- **ElevenLabs**: [Official Documentation](https://elevenlabs.io/docs)
- **Supabase**: [Official Documentation](https://supabase.com/docs)

---

**Good luck with your Jess PoC! 🚀**
